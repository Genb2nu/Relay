# /sn-status — Show Project Status

## Purpose

Display the current phase, gate status, and what the next action is.

## Usage

```
/sn-status
/sn-status --verbose
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--verbose` | No | Include component list and issue details |

## Process

### Step 1 — Read State
Read `.sn/state.json`. If missing, report:
```
No active project found. Run /sn-start to begin.
```

### Step 2 — Compute Gate Status
Check each phase gate based on state.json fields:

| Phase | Gate Condition |
|---|---|
| Discovery | `docs/requirements.md` exists |
| Planning | `docs/plan.md` + `docs/security-design.md` exist |
| Review | `auditor_approved = true` |
| Build | `forge_complete = true` (or all Forge flags) |
| QA | `sentinel_approved = true` |
| Deploy | `deployed_at` is set |

### Step 3 — Format Output

**Standard output:**
```
=== SimplifyNext Project Status ===

Project:     {project name}
Prefix:      {publisher_prefix}
Environment: {environment}
Phase:       {phase} ({emoji})

Gate Status:
  ✅ Discovery    — requirements.md exists
  ✅ Planning     — plan.md + security-design.md exist
  ⏳ Review       — auditor running (1 issue pending)
  ⬜ Build        — not started
  ⬜ QA           — not started
  ⬜ Deploy       — not started

Next action: Run /sn-plan-review to re-invoke Auditor after Blueprint fixes.

Open issues:
  - [Auditor] User story US-3 has no corresponding component
```

**Phase emojis:**
- `discovery` → 🔍
- `planning` → 📝
- `review` → 🔎
- `build` → 🔨
- `qa` → 🧪
- `complete` → ✅

### Step 4 — Verbose Mode
When `--verbose` is passed, also show:

```
Components Planned:
  Tables:  ops_request, ops_approval (2)
  Roles:   OpsManager, OpsApprover, OpsViewer (3)
  Flows:   OpsApprovalFlow, OpsReminderFlow (2)
  Apps:    Canvas App (1), MDA (1)

Components Built:
  Tables:  ops_request ✅, ops_approval ✅ (2/2)
  Roles:   OpsManager ✅, OpsApprover ⏳, OpsViewer ⬜ (1/3)
  ...

Last 5 execution log events:
  2026-05-13T10:00:00Z  conductor    phase_transition  → planning
  2026-05-13T10:05:00Z  blueprint    completed         plan.md written
  2026-05-13T10:10:00Z  auditor      started           reviewing plan
  2026-05-13T10:12:00Z  auditor      issue_found       US-3 has no component
  2026-05-13T10:12:01Z  auditor      completed         approved=false
```

## Error States

| Condition | Message |
|---|---|
| `.sn/state.json` missing | "No project found. Run /sn-start." |
| `docs/` missing | "docs/ folder missing — run /sn-start to reinitialise." |
| Corrupt JSON | "state.json is corrupt. Check `.sn/state.json` manually." |
