# /sn-build — Start or Resume Build

## Purpose

Start or resume Phase 5 build. Invokes Forge specialists in the correct order
with inline Sentinel verification after each component group.

## Usage

```
/sn-build
/sn-build --from flow
/sn-build --skip canvas
/sn-build --dry-run
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--from` | No | Resume from a specific specialist: `vault`, `canvas`, `mda`, `flow` |
| `--skip` | No | Skip a specialist (use with caution) |
| `--dry-run` | No | Show build plan without executing |
| `--force` | No | Re-run even if component shows as already built |

## Pre-flight Checks (MANDATORY)

Before invoking any Forge specialist:

1. **Validate plan lock:**
   `state.json.auditor_approved = true` and `plan_locked = true`
   If not: "Plan must be approved first. Run /sn-plan-review."

2. **Validate auth:**
   ```powershell
   pac auth who
   pac solution list --environment $env
   ```
   If `pac solution list` fails: HALT. "Run pac auth select or pac auth create."

3. **Create output directories:**
   ```powershell
   $dirs = @("docs","scripts","src/flows","src/canvas-apps","src/mda","src/webresources",".sn")
   foreach ($d in $dirs) { if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force } }
   ```

4. **Read state.json** and confirm phase is `review` or `build`.

## Build Order

```
Step 1: forge-vault    → schema, roles, FLS, env vars
         ↓ Sentinel inline verification
         (fix loop if failures before proceeding)

Step 2: forge-canvas   → Canvas App (if plan includes)
         ↓ Print Checklist A, wait for Canvas App URL
         ↓ Sentinel: App Checker 0 errors

Step 3: forge-mda      → Model-Driven App (if plan includes)
         ↓ Sentinel: sitemap, forms, published

Step 4: forge-flow     → Power Automate flows (if plan includes)
         ↓ Sentinel: all flows active (statecode=1)

Step 5: Phase 5 COMPLETE
         → Update state.json phase to "build"
         → Run /sn-qa for full Phase 6 verification
```

## Dry-Run Output

When `--dry-run`:
```
Build Plan — {project name}

Step 1: forge-vault
  CREATE  ops_request (table, 8 columns)
  CREATE  ops_approval_log (table, 5 columns)
  CREATE  OpsManager (security role)
  CREATE  OpsApprover (security role)
  CREATE  OpsSensitiveFields (FLS profile)
  CREATE  ops_ApprovalTimeout (env var, Integer)

Step 2: forge-canvas (Canvas App in plan)
  BUILD   OpsPortal — 6 screens
    - HomeScreen
    - RequestListScreen
    - RequestDetailScreen
    - ApprovalQueueScreen
    - SettingsScreen
    - AdminScreen

Step 3: forge-mda (MDA in plan)
  BUILD   Ops Management App
    - Sitemap: Requests, Approvals, Admin
    - Forms: Main form (ops_request), Quick View (ops_approval_log)

Step 4: forge-flow (Flows in plan)
  BUILD   OpsApprovalFlow (triggered: when request created)
  BUILD   OpsReminderFlow (triggered: scheduled, daily)

Total estimated API calls: 47
Run without --dry-run to execute.
```

## Inline Verification Fix Loop

After each Forge step, Sentinel verifies. If failures:
1. Sentinel reports specific failures
2. Forge re-attempts the failed components only
3. Sentinel re-verifies
4. Maximum 3 fix attempts per component
5. After 3 failures: halt and report to user

## Phase Transition

On successful completion of all Forge steps and Sentinel inline verifications:
- Update `state.json.phase` to `"build"`
- Update `state.json.build_completed_at` to current timestamp
- Log: `{"event": "build_complete", "agent": "conductor", "phase": "build"}`
- Report:
  ```
  ✅ Build complete!
  
  All components built and verified.
  Run /sn-qa to run final verification gate.
  ```
