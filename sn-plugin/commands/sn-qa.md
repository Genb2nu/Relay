# /sn-qa — Run QA Verification

## Purpose

Run the full Phase 6 QA gate: drift detection, functional test verification,
and security spot-checks. Invokes Sentinel for functional tests.

## Usage

```
/sn-qa
/sn-qa --only drift
/sn-qa --only security
/sn-qa --only functional
/sn-qa --report
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--only` | No | Run only one check type: `drift`, `security`, `functional` |
| `--report` | No | Save QA report to `docs/qa-report.md` |
| `--fix` | No | Attempt auto-fix for drift issues (routes to Forge) |

## Pre-conditions

- Build must be complete (`state.json.build_completed_at` is set)
- Auth must be valid: `pac auth who`

If build not complete: "Run /sn-build first."

## QA Steps

### Step 1 — Drift Detection

Compare every component in `docs/plan.md` against live Dataverse:

**Tables:**
```
For each table in plan:
  GET /api/data/v9.2/EntityDefinitions?$filter=LogicalName eq '{table}'
  If 404 → DRIFT: missing table
  Else: compare column list
    For each column in plan:
      GET /api/data/v9.2/EntityDefinitions({id})/Attributes?$filter=LogicalName eq '{col}'
      If 404 → DRIFT: missing column
```

**Flows:**
```
For each flow in plan:
  GET /api/data/v9.2/workflows?$filter=name eq '{flow}' and category eq 5
  If empty → DRIFT: missing flow
  If statecode ne 1 → DRIFT: flow inactive
```

**App Modules:**
```
GET /api/data/v9.2/appmodules?$filter=uniquename eq '{uniquename}'
If empty → DRIFT: missing app
```

### Step 2 — Functional Test Cases

Sentinel reads `docs/requirements.md` and derives test cases from user stories.
For each user story, Sentinel defines:
- Test case ID
- Pre-conditions
- Steps
- Expected result

Sentinel then maps each test to a verifiable API check or UI action.

Report format:
```
TEST RESULTS:
  TC-001: Manager can create request ............. ✅ PASS
  TC-002: Approver sees pending requests ......... ✅ PASS
  TC-003: Viewer cannot delete records ........... ✅ PASS
  TC-004: Self-approval is blocked .............. ✅ PASS
  TC-005: Email sent on approval ................ ⚠️  SKIP (manual test required)
  TC-006: Escalation after 48h .................. ✅ PASS
```

### Step 3 — Security Spot-Checks

Sentinel reads `docs/security-design.md` and runs:

1. **Role boundary check:**
   For each non-admin role, verify they cannot access tables marked as restricted
   for that role in security-design.md

2. **FLS check:**
   For each sensitive column with FLS, verify:
   - FLS profile exists
   - Profile is assigned to the correct roles
   - Unassigned roles cannot see the column

3. **Self-approval check (if applicable):**
   If plan includes approval workflows, verify the workflow trigger conditions
   prevent the same user who created a record from approving it

### Step 4 — Compile Report

```
=== QA Report — {project name} ===
Date: {timestamp}

DRIFT CHECK
  Status: ✅ No drift detected (14/14 components match plan)

FUNCTIONAL TESTS
  Status: ✅ 5 passed, 0 failed, 1 skipped
  Skipped: TC-005 (email test requires mailbox configuration — test manually)

SECURITY CHECKS
  Status: ✅ All role boundaries verified
           ✅ FLS profiles active on 3 sensitive columns
           ✅ Self-approval blocked

OVERALL: ✅ QA GATE PASSED

Next: Run /sn-deploy to export and deploy the solution.
```

### Step 5 — Gate Decision

**Pass:** Update `state.json`:
- `sentinel_approved = true`
- `state.json.phase = "qa"`
- `qa_completed_at = <timestamp>`

**Fail:** Report specific failures. Offer:
```
QA found {N} issues. Options:
  a) Auto-fix drift issues: /sn-qa --fix
  b) Re-run specific component: /sn-update-components --type {type}
  c) View details: /sn-qa --report
```

When `--fix` is passed, route drift items to the appropriate Forge specialist,
then re-run Sentinel verification.

## Report File (--report)

Saves `docs/qa-report.md` with full test results, drift details, and
security check outcomes. Useful for handoff documentation.
