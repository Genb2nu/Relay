# /sn-list-components — List All Planned Components

## Purpose

Show every component planned in `docs/plan.md`, their build status, and
the GUIDs of any already-created components.

## Usage

```
/sn-list-components
/sn-list-components --type tables
/sn-list-components --status missing
/sn-list-components --json
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--type` | No | Filter by type: `tables`, `roles`, `fls`, `envvars`, `canvas`, `mda`, `flow` |
| `--status` | No | Filter by status: `built`, `missing`, `partial` |
| `--json` | No | Output raw JSON instead of formatted table |

## Process

### Step 1 — Read Inputs
Read `docs/plan.md` and `.sn/state.json`.

### Step 2 — Cross-Reference
For each component in the plan, check if a GUID exists in `state.json.components`.

Status rules:
- `built` — GUID exists AND Sentinel last verified it ✅
- `missing` — no GUID in state.json
- `partial` — GUID exists but Sentinel flagged issues OR some sub-components missing
- `unknown` — no Sentinel run on record

### Step 3 — Format Output

**Default (no flags):**
```
=== Components for: {project name} ===

TABLES (3 planned, 2 built, 1 missing)
  ✅ ops_request         guid: xxxxxxxx-...
  ✅ ops_approval_log    guid: yyyyyyyy-...
  ❌ ops_notification    not yet built

SECURITY ROLES (3 planned, 3 built)
  ✅ OpsManager          guid: aaaaaaaa-...
  ✅ OpsApprover         guid: bbbbbbbb-...
  ✅ OpsViewer           guid: cccccccc-...

FLS PROFILES (2 planned, 2 built)
  ✅ OpsSensitiveFields  guid: dddddddd-...
  ✅ OpsApproverView     guid: eeeeeeee-...

ENVIRONMENT VARIABLES (2 planned, 1 built)
  ✅ ops_ApprovalTimeout  type: Integer, value: 48
  ❌ ops_EscalationEmail  type: String, not yet built

FLOWS (2 planned, 0 built)
  ❌ OpsApprovalFlow
  ❌ OpsReminderFlow

CANVAS APP (1 planned)
  ⏳ OpsPortal           building (5 of 8 screens complete)

MDA (1 planned)
  ❌ Ops Management App  not yet built

Total: 14 planned, 8 built, 5 missing, 1 partial
```

**JSON output:**
```json
{
  "tables": [
    { "logical_name": "ops_request", "status": "built", "guid": "..." },
    { "logical_name": "ops_notification", "status": "missing", "guid": null }
  ],
  ...
}
```

## Status Icons

| Icon | Meaning |
|---|---|
| ✅ | Built and Sentinel-verified |
| ❌ | Not yet built |
| ⏳ | Build in progress or partial |
| ⚠️ | Built but has Sentinel issues |

## Tips

- Use `--status missing` to see exactly what Forge still needs to build
- Use `--type tables` before running `/sn-update-components --type tables`
- Use `--json` to pipe output to other tools or save as a build report
