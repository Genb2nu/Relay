# /sn-config — Show or Update Project Configuration

## Purpose

View and update project configuration stored in `.sn/state.json`. Use to
change the environment URL, update publisher details, or reset specific flags.

## Usage

```
/sn-config
/sn-config --show
/sn-config --set environment https://neworg.crm5.dynamics.com
/sn-config --set publisher_prefix ops
/sn-config --reset auditor_approved
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--show` | No | Display current configuration (default when no args) |
| `--set <key> <value>` | No | Update a configuration value |
| `--reset <key>` | No | Reset a flag to its default value |
| `--export` | No | Export state.json to stdout as pretty JSON |

## Editable Fields

| Field | Type | Description |
|---|---|---|
| `environment` | URL | Target environment URL |
| `publisher_prefix` | String | Publisher prefix (2-8 lowercase letters) |
| `publisher_name` | String | Publisher display name |
| `project` | String | Project display name |
| `solution_name` | String | Solution logical name |

## Resettable Flags

| Flag | What it resets |
|---|---|
| `auditor_approved` | Clears plan approval (also clears plan_locked) |
| `sentinel_approved` | Clears QA gate approval |
| `plan_locked` | Unlocks the plan (clears checksums) |
| `build_completed_at` | Resets build completion marker |

## Process

### Show (default)

```
/sn-config
/sn-config --show
```

Output:
```
=== SimplifyNext Project Configuration ===

Project:          Ops Management Portal
Publisher Prefix: ops
Publisher Name:   Operations Internal
Solution Name:    ops_OpsManagement
Environment:      https://contoso.crm5.dynamics.com

Phase:            build
Plan Locked:      ✅ yes
Auditor Approved: ✅ yes
Sentinel Approved: ⬜ not yet

Config file: .sn/state.json
```

### Set a Value

```
/sn-config --set environment https://neworg.crm5.dynamics.com
```

Validation:
- `publisher_prefix`: must match `^[a-z]{2,8}$`
- `environment`: must start with `https://` and contain `.dynamics.com`
- `solution_name`: must match `^[a-zA-Z][a-zA-Z0-9_]{0,63}$`

On success:
```
✅ Updated: environment → https://neworg.crm5.dynamics.com
Previous value: https://contoso.crm5.dynamics.com

Note: Changing the environment URL does not re-run any builds.
Run /sn-build or /sn-update-components to apply changes to the new environment.
```

### Reset a Flag

```
/sn-config --reset auditor_approved
```

Warning for destructive resets:
```
⚠️  Resetting auditor_approved will:
  - Set auditor_approved = false
  - Set plan_locked = false
  - Clear plan checksums

This means the plan must be re-reviewed before Forge can build.
Continue? (yes/no)
```

On confirm:
```
✅ Reset: auditor_approved = false
          plan_locked = false
          plan_checksum cleared

Run /sn-plan-review to re-run the review cycle.
```

### Export

```
/sn-config --export
```

Outputs the full `.sn/state.json` as formatted JSON. Useful for debugging
or copying state to a new environment.

## Safety Rules

1. Never allow changing `publisher_prefix` after build has started without
   a warning that all component names will be inconsistent.
2. Never allow resetting `sentinel_approved` silently — always warn.
3. Log all config changes to `.sn/execution-log.jsonl`:
   ```json
   {"event": "config_updated", "agent": "conductor", "field": "environment", "new_value": "..."}
   ```

## Prefix Change Warning

If the user tries to change `publisher_prefix` after components have been built:

```
⚠️  Changing the publisher prefix after components are built will cause
a naming mismatch between your plan and the existing Dataverse components.

Current prefix: con
Built components: con_request (table), con_approval_log (table), ConManager (role)

If you change the prefix to "ops":
  - Plan will expect: ops_request, ops_approval_log
  - Existing components are still: con_request, con_approval_log
  - This WILL break drift detection and Sentinel verification

To change the prefix cleanly:
  1. Export the solution
  2. Change publisher in PPAC
  3. Re-import
  4. Update plan.md and security-design.md
  5. Re-run /sn-plan-review

Are you sure you want to change the prefix? (yes/no)
```
