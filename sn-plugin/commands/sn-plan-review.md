# /sn-plan-review — Trigger Plan Review Cycle

## Purpose

Force a plan review cycle: invokes Auditor to re-review `docs/plan.md`.
Use when Blueprint has made revisions and Auditor needs to re-run.
Also use to unlock a locked plan for revision.

## Usage

```
/sn-plan-review
/sn-plan-review --unlock
/sn-plan-review --agent auditor
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--unlock` | No | Remove plan lock and checksums to allow Blueprint to revise |
| `--agent` | No | Run only a specific reviewer: `auditor` |

## Process

### Step 1 — Read State
Read `.sn/state.json`. Check current phase.

If `auditor_approved = true` and `--unlock` not passed:
```
Plan is already approved. To make changes, run:
  /sn-plan-review --unlock

Warning: Unlocking will clear the approval and require a full review cycle.
```

### Step 2 — Unlock (if --unlock flag)
Ask for confirmation:
```
⚠️  Unlocking the plan will:
- Clear auditor_approved status
- Allow Blueprint to revise docs/plan.md
- Require a full Auditor review before build can continue

Are you sure? (yes/no)
```

If confirmed:
- Set `state.json.auditor_approved = false`
- Set `state.json.plan_locked = false`
- Clear `state.json.plan_checksum` and `state.json.security_design_checksum`
- Log: `{"event": "plan_unlocked", "agent": "conductor"}`
- Report: "Plan unlocked. Invoke Blueprint to make revisions, then run /sn-plan-review again."

### Step 3 — Invoke Auditor
Pass to Auditor:
- `docs/plan.md`
- `docs/requirements.md`
- `docs/security-design.md`
- List of previously failed issues (from `state.json.auditor_issues`) to check first

### Step 4 — Process Auditor Result

**If Auditor approves:**
- Set `state.json.auditor_approved = true`
- Set `state.json.auditor_issues = []`
- Log: `{"event": "plan_approved", "agent": "auditor"}`
- Compute SHA256 checksums of `plan.md` and `security-design.md`
- Write checksums to state.json
- Set `state.json.plan_locked = true`
- Report:
  ```
  ✅ Plan approved by Auditor
  
  Plan locked. Checksums recorded.
  Ready to build. Run /sn-build to start Phase 5.
  ```

**If Auditor finds issues:**
- Set `state.json.auditor_approved = false`
- Set `state.json.auditor_issues = [<list>]`
- Log: `{"event": "plan_review_failed", "agent": "auditor", "issue_count": N}`
- Report issues to user with routing suggestion:
  ```
  ❌ Auditor found 2 issues:
  
  1. User story US-3 has no corresponding component
     → Route to Blueprint to add the missing component
  
  2. Table ops_request missing column ops_priority
     → Route to Blueprint to add the column
  
  Options:
  a) Blueprint will fix these → ask Blueprint to revise plan.md, then run /sn-plan-review
  b) Accept and override → not recommended; ask user explicitly
  ```

## Revision Cycle Limit

Track revision count in state.json as `review_cycle_count`.
After 3 failed cycles:
```
⚠️  3 revision cycles completed without full approval.
Remaining issues:
  - [list]
  
Escalating to user: Should we override these issues or continue revising?
```

## Files Modified

- `.sn/state.json` — approval flags, checksums, lock status
- `.sn/execution-log.jsonl` — review events
