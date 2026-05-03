---
description: |
  Show current project status using real execution data from plan-index.json
  and execution-log.jsonl. Not a guess — actual system state.
trigger_keywords:
  - relay status
  - what phase
  - where are we
  - what's done
  - project status
---

# /relay:status

When the user invokes this command, read `.relay/plan-index.json` and
`.relay/execution-log.jsonl` to report actual system state.

## Step 1 — Read both files

```bash
cat .relay/plan-index.json
tail -50 .relay/execution-log.jsonl
```

## Step 2 — Report structured status

Output in this format:

```
## Relay Project Status
Project: <name> | Solution: <solution> | Environment: <env>

## Phase Progress
✅ Phase 1 — Discovery     (completed <timestamp>)
✅ Phase 2 — Planning      (completed <timestamp> | score: <overall>/100)
✅ Phase 3 — Review        (Auditor ✅ Warden ✅ | issues: <N> found, <N> resolved)
✅ Phase 4 — Adversarial   (Critic ✅ | checklist: <N>/<N> | LOCKED ✅)
🔵 Phase 5 — Build         (in progress)
   Vault: ✅ | Stylist: ✅ | Forge specialists: 🔵
   Built: <N> tables, <N> flows, <N> apps
   Partial: <list>
   Blocked: <list>
○ Phase 6 — Verify         (not started)
○ Phase 7 — Ship           (not started)

## Quality Scores
Completeness: <N>/100 | Security: <N>/100 | Testability: <N>/100 | Overall: <N>/100

## Components
Tables: <N> | Flows: <N> | Apps: <N> | Plugins: <N> | Security Roles: <N>

## Recent Activity (last 10 events)
<timestamp> [<agent>] <event>
...

## Next Step
<specific action needed to advance — from plan-index gate failures>
```

## If plan-index.json doesn't exist

Tell the user:
"No active Relay project found. Run `/relay:start` to begin a new project
or `/relay:load` to load existing project documents."

## Blockers

If any gate has failed, show the specific failures:
```
⚠️ BLOCKED: Phase 3 cannot advance
  ✗ Auditor has not approved (2 issues unresolved)
  ✗ Warden: self-approval risk not yet fixed in plan
```
