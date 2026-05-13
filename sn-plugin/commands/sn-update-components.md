# /sn-update-components — Re-run a Component Build

## Purpose

Re-run Forge for a specific component type or named component without
re-running the full build. Used when a specific component failed or needs
to be rebuilt after a plan change.

## Usage

```
/sn-update-components --type tables
/sn-update-components --type flow --name "OpsApprovalFlow"
/sn-update-components --type canvas
/sn-update-components --type roles
/sn-update-components --type fls
/sn-update-components --type envvars
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--type` | Yes | Component type: `tables`, `roles`, `fls`, `envvars`, `canvas`, `mda`, `flow`, `all` |
| `--name` | No | Specific component name within that type |
| `--verify` | No | Run Sentinel verification after update (default: true) |

## Supported Types

| Type | Forge Specialist | What It Rebuilds |
|---|---|---|
| `tables` | forge-vault | Dataverse tables and columns |
| `roles` | forge-vault | Security roles |
| `fls` | forge-vault | Field-Level Security profiles |
| `envvars` | forge-vault | Environment variables |
| `canvas` | forge-canvas | Canvas App screens |
| `mda` | forge-mda | Model-Driven App sitemap/forms |
| `flow` | forge-flow | Power Automate flows |
| `all` | all specialists | Full rebuild (equivalent to /sn-build) |

## Process

### Step 1 — Validate Pre-conditions
Read `.sn/state.json`. Check:
- Plan is locked (`auditor_approved = true`)
- Auth is valid: `pac auth who`

If plan not locked: "Plan must be approved before rebuilding components. Run /sn-plan-review."

### Step 2 — Check Component GUIDs
Read `state.json.components`. If the component already has a GUID:
- **Do NOT create a new one**
- Perform an UPDATE (PATCH) on the existing component
- Log: "Updating existing {component} ({guid})"

If no GUID found:
- Perform a CREATE
- Store the new GUID in `state.json.components`

### Step 3 — Invoke Forge Specialist
Pass to the appropriate Forge specialist:
- The specific component(s) to rebuild
- The existing GUID map from state.json
- Instruction to patch, not create, if GUID exists

### Step 4 — Inline Verification (unless --verify=false)
After Forge completes, invoke Sentinel for the affected component type only.
Sentinel verifies the updated component matches the plan specification.

### Step 5 — Report
```
Updated: ops_request (table)
  Columns added: ops_priority, ops_escalation_date
  Columns modified: ops_status (choice updated)
  GUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Sentinel verification: ✅ passed

Run /sn-status to see overall build state.
```

## Error Handling

| Error | Action |
|---|---|
| Component not in plan | "ops_xyz is not in docs/plan.md. Check plan or use /sn-patch-components." |
| Auth failure | "Run pac auth select first." |
| API 403 | "Permission denied. Verify your user has System Customizer or System Administrator role." |
| Sentinel fails after update | Report specific failures; ask user to approve re-attempt or skip. |
