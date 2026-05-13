# /sn-agent — Invoke a Specific Agent Directly

## Purpose

Directly invoke a specific SimplifyNext squad agent, bypassing the normal
phase-gating workflow. Use for targeted tasks, re-runs, or agent testing.

## Usage

```
/sn-agent scout
/sn-agent blueprint --revise "Add audit trail table"
/sn-agent auditor
/sn-agent forge --specialist vault
/sn-agent forge --specialist canvas --screen RequestDetailScreen
/sn-agent sentinel --check drift
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `agent` | Yes | Agent name: `scout`, `blueprint`, `auditor`, `forge`, `sentinel` |
| `--revise` | No | Instruction for Blueprint to revise a specific section |
| `--specialist` | No | Forge specialist: `vault`, `canvas`, `mda`, `flow` |
| `--screen` | No | Specific Canvas App screen for forge-canvas |
| `--check` | No | Specific Sentinel check: `drift`, `functional`, `security` |
| `--brief` | No | Custom brief/instruction to pass to the agent |

## Agents

### Scout

```
/sn-agent scout
```

Re-invokes Scout to re-gather requirements. Use when:
- Scope has changed significantly
- New stakeholders have been identified
- Business requirements need re-validation

Scout reads existing `docs/requirements.md` as a baseline and asks only
about gaps or changes. Writes to `docs/requirements.md`.

### Blueprint

```
/sn-agent blueprint
/sn-agent blueprint --revise "Add approval audit table and flow"
```

Re-invokes Blueprint. If `--revise` is provided, Blueprint updates only the
specified sections of `docs/plan.md` and `docs/security-design.md`.

Note: If the plan is locked, Blueprint cannot write until the plan is unlocked
via `/sn-plan-review --unlock`.

### Auditor

```
/sn-agent auditor
```

Re-invokes Auditor to review the current state of `docs/plan.md`. Auditor
runs its full 20-item checklist and updates `state.json` with the result.

### Forge

```
/sn-agent forge --specialist vault
/sn-agent forge --specialist canvas
/sn-agent forge --specialist mda
/sn-agent forge --specialist flow
/sn-agent forge --specialist canvas --screen RequestDetailScreen
```

Invokes a specific Forge specialist. Each specialist reads the locked plan
and builds or re-builds the relevant components.

When `--screen` is specified, forge-canvas rebuilds only that screen.

All Forge invocations:
- Read `state.json.components` for existing GUIDs (patch, don't duplicate)
- Read the locked plan (will refuse if plan not locked)
- Run Sentinel inline verification after completion

### Sentinel

```
/sn-agent sentinel
/sn-agent sentinel --check drift
/sn-agent sentinel --check functional
/sn-agent sentinel --check security
```

Invokes Sentinel for a specific check or all checks.

## Context Passing

All agents receive:
- `.sn/state.json` — current state
- Their specific skill files
- The `--brief` text if provided

Agents do NOT receive the full conversation history — they read only from files.
Always ensure relevant information is written to `docs/` before invoking agents.

## Output

Each agent reports its result, then Conductor summarises:

```
Agent: blueprint
Task: Revise plan — add approval audit table

Result: ✅ Completed

Changes made:
  - docs/plan.md: Added ops_approval_audit table (6 columns)
  - docs/plan.md: Added AuditApprovalFlow to flows section
  - docs/security-design.md: Added FLS entry for ops_audit_result column

⚠️  Plan was modified — review lock has been cleared.
Run /sn-plan-review to re-lock before building.
```

## Safety Notes

- Direct agent invocation bypasses phase gates — use deliberately
- If you bypass Auditor approval and go straight to Forge, do so at your own risk
- Any Blueprint revision clears the plan lock automatically
- Forge invocations always verify GUIDs to prevent duplicates
