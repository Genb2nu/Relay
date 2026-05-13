# /sn-patch-components — Patch an Existing Component

## Purpose

Apply a targeted change to a specific component that is already built. Unlike
`/sn-update-components` (which re-runs a full Forge specialist pass), this
command patches a single named component with a specific change — for example,
adding a column, updating a choice set, or modifying a flow step.

## Usage

```
/sn-patch-components --component ops_request --add-column ops_priority
/sn-patch-components --component OpsApprovalFlow --update-step "Send email"
/sn-patch-components --component OpsPortal --update-screen RequestDetailScreen
/sn-patch-components --component OpsManager --add-privilege Read:ops_notification
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--component` | Yes | Logical name of the component to patch |
| `--add-column` | No | Add a new column to a table |
| `--remove-column` | No | Mark a column as deprecated (cannot delete if data exists) |
| `--update-step` | No | Modify a specific flow step |
| `--update-screen` | No | Update a Canvas App screen |
| `--add-privilege` | No | Add a privilege to a security role |
| `--remove-privilege` | No | Remove a privilege from a security role |
| `--description` | No | Describe the change in plain text (AI will interpret) |

## Process

### Step 1 — Identify Component
Read `.sn/state.json.components` to find the GUID for the named component.

If not found:
```
Component ops_xyz not found in state.json.
If it was built manually, run /sn-list-components --type tables to check.
If it's not built yet, run /sn-build.
```

### Step 2 — Validate Change
Check `docs/plan.md` to determine if the patch is:
- **In-scope** — the column/screen/step exists in the plan but wasn't built yet
- **Out-of-scope** — the change goes beyond the locked plan

If out-of-scope:
```
⚠️  This patch goes beyond the locked plan.

Change requested: add column ops_urgency_flag to ops_request
Not found in: docs/plan.md

Options:
  a) Add this to the plan and re-lock: run /sn-plan-review --unlock, then Blueprint
  b) Apply as an ad-hoc patch (untracked): --force flag required
  c) Cancel
```

### Step 3 — Apply Patch

**Add column to table:**
```
POST /api/data/v9.2/EntityDefinitions({tableId})/Attributes
{column definition per sn-dataverse-patterns.md}
```

**Update flow step:**
```
GET  /api/data/v9.2/workflows({flowId})        # fetch flow definition
PATCH flow JSON to update the specified step
PUT  /api/data/v9.2/workflows({flowId})        # write updated definition
POST /api/data/v9.2/workflows({flowId})/Activate  # reactivate
```

**Update Canvas App screen:**
```
Route to forge-canvas with specific screen name and change instructions.
forge-canvas generates updated YAML → applies via Canvas Authoring MCP.
```

**Add privilege to role:**
```
GET  /api/data/v9.2/roles({roleId})
POST /api/data/v9.2/roleprivileges (add the specific privilege)
```

### Step 4 — Verify Patch
After applying, Sentinel verifies:
- The specific attribute/step/screen/privilege now exists
- No adjacent components were broken by the change (regression check)

### Step 5 — Report
```
✅ Patch applied: ops_request → added column ops_priority (Choice)

Details:
  Table GUID:   xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  Column added: ops_priority (Choice: Low, Medium, High, Critical)
  Solution:     OpsManagement ✅ (component linked)

Sentinel verification: ✅ passed
  - Column exists in Dataverse
  - No regression on adjacent forms (ops_request Main Form updated)
  - FLS: column is public (no FLS required per plan)
```

## Safety Rules

1. Never delete a column that has data — mark deprecated in description only
2. Never modify `plan.md` or `security-design.md` without `/sn-plan-review`
3. Always link new components to the solution (set `MSCRM.SolutionUniqueName`)
4. Log every patch to `.sn/execution-log.jsonl`

## Execution Log Entry

```json
{
  "timestamp": "...",
  "agent": "forge-vault",
  "event": "component_patched",
  "phase": "build",
  "component": "ops_request",
  "change": "add_column:ops_priority",
  "guid": "..."
}
```
