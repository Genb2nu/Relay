# SimplifyNext QA Standards

## Purpose

Sentinel must follow these QA standards for all SimplifyNext projects.
These define what "done" means for every component type.

---

## Definition of Done

### Dataverse Schema
- [ ] Table exists in Dataverse (`GET EntityDefinitions` returns it)
- [ ] All planned columns exist on the table
- [ ] All choice columns have at least 2 options + "Not set" (value 0)
- [ ] Primary column has `RequiredLevel = ApplicationRequired`
- [ ] Table is inside the project solution

### Security Roles
- [ ] Role exists (`GET roles` returns it)
- [ ] Role has correct privileges per security-design.md
- [ ] Role is inside the project solution
- [ ] Role can be assigned to users (not corrupted)

### FLS Profiles
- [ ] Profile exists (`GET fieldsecurityprofiles`)
- [ ] Profile has all planned columns with correct read/write permissions
- [ ] Profile is assigned to the correct security roles
- [ ] Unassigned roles CANNOT read or write the sensitive columns

### Canvas App
- [ ] App exists in the solution
- [ ] App Checker: 0 errors in all 5 categories
- [ ] All planned screens exist
- [ ] Navigation works between all screens
- [ ] Data loads correctly from Dataverse tables
- [ ] Error states are handled gracefully

### Model-Driven App
- [ ] App module exists and is published
- [ ] Sitemap matches the planned structure
- [ ] All planned tables have at least one Main form published
- [ ] All planned views exist and return records
- [ ] App is accessible by the correct security roles

### Power Automate Flows
- [ ] Flow exists in the solution
- [ ] Flow is active (`statecode = 1, statuscode = 2`)
- [ ] Connection references are wired to live connections
- [ ] Flow has a Try-Catch error handling pattern
- [ ] Flow has been triggered at least once in testing (where testable)

### Environment Variables
- [ ] Variable exists (`GET environmentvariabledefinitions`)
- [ ] Variable has a value set (`GET environmentvariablevalues`)
- [ ] Variable is inside the project solution

---

## Test Case Template

For every user story in `docs/requirements.md`, Sentinel must write a test case:

```markdown
## TC-{number}: {User Story Title}

**User Story:** As a {persona}, I want to {action} so that {outcome}.

**Pre-conditions:**
- User is logged in as {persona}
- {Any required data state}

**Steps:**
1. {Step 1}
2. {Step 2}
...

**Expected Result:**
- {What should happen}

**Verification Method:**
- API: `GET /api/data/v9.2/{endpoint}?$filter=...`
- UI: Navigate to {screen}, observe {element}

**Status:** PASS / FAIL / SKIP

**Failure Detail:** (if FAIL)
{What actually happened}
```

---

## Security Test Checklist

Run for every project before QA gate sign-off:

### Role Boundary Tests
- [ ] Log in as a low-privilege persona (e.g., Viewer) and attempt to create a record → should be blocked
- [ ] Log in as a low-privilege persona and attempt to delete a record → should be blocked
- [ ] Log in as a low-privilege persona and attempt to access a restricted screen → screen should be hidden or show access denied

### FLS Tests
- [ ] As an unauthorised user, navigate to a record with a sensitive column → column should be blank/hidden
- [ ] As an authorised user, navigate to the same record → column should show the value

### Self-Approval Test (if approval flow exists)
- [ ] Create a record as User A → User A should not appear as a valid approver
- [ ] If User A attempts to approve their own record via the URL directly → flow should block and reject

### Data Leakage Test
- [ ] Use the Dataverse REST API as a low-privilege user → verify only own records are returned
- [ ] Attempt to query a restricted table → should return 0 results or 403

---

## Drift Detection Algorithm

```python
def check_drift(plan, dataverse_client):
    issues = []
    
    for table in plan['tables']:
        result = dataverse_client.get_entity(table['logical_name'])
        if not result:
            issues.append(f"MISSING TABLE: {table['logical_name']}")
            continue
        
        live_columns = dataverse_client.get_columns(table['logical_name'])
        for col in table['columns']:
            if col['logical_name'] not in live_columns:
                issues.append(f"MISSING COLUMN: {col['logical_name']} on {table['logical_name']}")
    
    for role in plan['security_roles']:
        if not dataverse_client.role_exists(role['name']):
            issues.append(f"MISSING ROLE: {role['name']}")
    
    for flow in plan['flows']:
        flow_data = dataverse_client.get_flow(flow['name'])
        if not flow_data:
            issues.append(f"MISSING FLOW: {flow['name']}")
        elif flow_data['statecode'] != 1:
            issues.append(f"INACTIVE FLOW: {flow['name']} (statecode={flow_data['statecode']})")
    
    return issues
```

---

## QA Report Format

```markdown
# QA Report — {project name}
Date: {timestamp}
Auditor: Sentinel

## Summary
| Category | Status | Details |
|---|---|---|
| Drift Detection | ✅ PASS | 14/14 components match plan |
| Functional Tests | ✅ PASS | 8/8 passed, 0 failed, 1 skipped |
| Security Tests | ✅ PASS | All role boundaries verified |

## Drift Details
No drift detected.

## Test Results
| ID | Story | Status |
|---|---|---|
| TC-001 | Manager creates request | ✅ PASS |
| TC-002 | Approver sees queue | ✅ PASS |
...

## Security Test Results
| Test | Result |
|---|---|
| Role boundary: Viewer cannot create | ✅ PASS |
| FLS: sensitive column hidden | ✅ PASS |
| Self-approval blocked | ✅ PASS |

## Open Items
- TC-005: Email notification (skipped — requires mailbox)

## Sign-off
Sentinel: APPROVED
```
