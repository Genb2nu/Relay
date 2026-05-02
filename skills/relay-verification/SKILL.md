---
name: relay-verification
description: |
  Verification patterns for Sentinel — checking that what was built matches
  what was planned. Never declare completion without verification. Cross-checks
  built components against plan.md spec item by item. Adapted from Superpowers
  verification-before-completion — no external dependency required.
trigger_keywords:
  - verify
  - sentinel
  - testing
  - verification
  - check build
  - functional testing
allowed_tools:
  - Read
  - Bash
  - Write
---

# Relay Verification — Sentinel Patterns

Adapted from Superpowers verification-before-completion for Power Platform build verification.

## Core Principle

Never declare a build complete without verifying it.
"It should work" is not verification. Evidence is verification.

A plan approved by Auditor + Warden + Critic represents a commitment.
Sentinel's job is to confirm that commitment was honoured — not to judge
whether the plan was good.

## Anti-Pattern: Declaration Without Evidence

```
❌ Wrong: "The Canvas App was built with 4 screens as planned. ✅"
✅ Right: "Ran get_data_source_schema — confirmed <prefix>_<maintable> connected.
          Ran compile_canvas — Validation passed, 5 files compile clean.
          Synced to Power Apps Studio — scrHome, scrNewRequest, 
          scrMyRecords, scrSummary all visible in tree view. ✅"
```

## Verification Checklist (Sentinel runs this for every build)

### Schema Verification
```bash
# Verify tables exist with correct column counts
pac dataverse table list --environment <url> --solution <name>

# Verify specific columns
pac dataverse column list --environment <url> --table <prefix>_<tablename>
```

Cross-check against plan.md schema section:
- [ ] All tables exist with correct display names
- [ ] All columns exist with correct data types
- [ ] All required flags match plan
- [ ] Lookup columns reference correct target tables
- [ ] Global choices exist with correct values
- [ ] Auto-number format matches plan

### Security Role Verification
```bash
pac admin list-role --environment <url>
```
- [ ] All roles listed in plan exist
- [ ] Role names match exactly (not "similar")

### Plugin Verification
```bash
pac solution check --path ./solution.zip
# or via Dataverse MCP: query pluginassemblies
```
- [ ] Assembly registered with correct name
- [ ] Step registered with correct table, message, stage, mode
- [ ] Pre-image attributes match plan

### Flow Verification
```bash
pac flow list --environment <url>
```
- [ ] All flows exist
- [ ] Flows exist in correct solution
- [ ] Note: flows will be OFF (expected — user turns them on)

### App Verification
- [ ] Canvas App exists with correct name
- [ ] All screens exist (verified via compile_canvas or Power Apps Studio)
- [ ] Power Fx formulas compile without errors
- [ ] Model-Driven App exists with correct app module name
- [ ] Sitemap has correct areas and subareas
- [ ] Forms have correct tabs and sections

### Environment Variable Verification
```bash
pac env list-variables --environment <url>
```
- [ ] All environment variables exist
- [ ] Default values are set correctly

### Seed Data Verification
- [ ] Check record count in each seeded table
- [ ] Spot-check 2-3 records for data quality

## Plan Cross-Reference Method

Read plan.md section by section. For each specified component:

```
Plan says: "<prefix>_<main_entity> — 12 columns including <prefix>_requestdate (DateTime)"
Evidence:  pac dataverse column list output shows <prefix>_requestdate, type DateTimeAttributeMetadata
Result:    ✅ PASS
```

Never verify by memory. Always verify by evidence.

## Partial Build Handling

If Forge specialist/Vault marked components as PARTIAL or BLOCKED:
- Document what was not built and the stated reason
- Verify the stated reason is accurate (not a workaround)
- Note it in the verification report — don't fail the build for genuinely
  un-automatable items (business rules, OAuth connection linking)

## Verification Report

Write `docs/test-report.md`:

```markdown
# Verification Report — <Project Name>
Verified: <date> | Environment: <org url>

## Schema
| Component | Planned | Verified | Status |
|---|---|---|---|
| <prefix>_<main_entity> | 12 columns | 12 columns confirmed | ✅ PASS |
| <prefix>_<related_entity> | 6 columns | 6 columns confirmed | ✅ PASS |

## Security
| Component | Status | Evidence |
|---|---|---|
| Employee role | ✅ PASS | pac admin list-role output |

## Plugins
| Assembly | Status | Evidence |
|---|---|---|
| <PluginAssemblyName> | ✅ PASS | Dataverse MCP pluginassemblies query |

## Apps
| App | Screens/Views | Compile | Status |
|---|---|---|---|
| <CanvasAppName> | 4/4 screens | ✅ clean | ✅ PASS |

## Not Verified (acceptable reasons)
| Item | Reason |
|---|---|
| Flows turned ON | User action required — Microsoft policy |
| Connection references linked | OAuth login required |
| Business rules | No API — user creates in maker portal |

## Overall Result
✅ PASS — all automatable components verified
```

## Handoff

```
Verification: PASS / FAIL
Components verified: <N>
Failures: <N> (list each)
Acceptable non-verified items: <N> (all genuinely manual)
```
