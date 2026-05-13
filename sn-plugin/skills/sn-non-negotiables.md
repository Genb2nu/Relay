# SimplifyNext Non-Negotiables

## Purpose

These are the absolute standards that every SimplifyNext Power Platform delivery
must meet. No exceptions. If a component does not meet these standards, it is
not done.

Any agent that produces output violating a non-negotiable must be re-invoked
to fix it before phase advancement.

---

## Solution Standards

### SN-NN-001: Named Solution Required
Every project must have its own named, unmanaged solution in development.
No components may be added to the Default Solution.

**Violation:** Components created outside a named solution.
**Fix:** Move all components into the project solution before QA.

### SN-NN-002: Managed in Test and Production
Solutions must be exported as managed and imported as managed to all
non-development environments.

**Violation:** Unmanaged solution imported to test or prod.
**Fix:** Re-export as managed and re-import.

### SN-NN-003: Publisher Prefix Consistency
Every custom component must use the project's publisher prefix from
`.sn/state.json.publisher_prefix`. No component may use a different prefix
or no prefix.

**Violation:** Column named `new_status` instead of `ops_status`.
**Fix:** Rename the column; update all references.

---

## Security Standards

### SN-NN-004: No UI-Only Security
Security must never rely solely on hiding UI elements. Every data restriction
must be enforced at the Dataverse layer (security roles, FLS, or record ownership).

**Violation:** A sensitive column is hidden in a form but not covered by FLS.
**Fix:** Add FLS profile for the column and assign to appropriate roles.

### SN-NN-005: FLS for All PII and Financial Data
Any column containing PII (names, emails, phone numbers, addresses, government IDs)
or financial data (amounts, account numbers, salaries) must have an FLS profile.

**Violation:** `ops_salary` column has no FLS profile.
**Fix:** Create FLS profile, assign the column, assign profile to authorised roles only.

### SN-NN-006: Least Privilege Roles
Security roles must grant the minimum privilege required.
No non-admin role may have organization-level Write or Delete.
No non-admin role may have "All" access to any table.

**Violation:** OpsUser role has Delete: Organization on ops_request.
**Fix:** Change Delete to None or Basic (user-owned records only).

### SN-NN-007: No Self-Approval
Any workflow that includes an approval step must prevent the record creator
from approving their own record.

**Violation:** Approval flow does not check if approver is the same as creator.
**Fix:** Add self-approval check in flow; set outcome to "Rejected - Self Approval" if matched.

---

## Flow Standards

### SN-NN-008: Error Handling in Every Flow
Every Power Automate flow must have a Try-Catch pattern.
No flow may allow unhandled errors to silently fail.

**Violation:** Flow has no Scope actions and no error branch.
**Fix:** Wrap all logic in a Try scope; add Catch scope with error notification.

### SN-NN-009: Connection References (No Personal Connections)
All flows must use connection references. No flow may be hard-coded to a
personal connection that would break if the developer leaves.

**Violation:** Flow uses a personal Dataverse connection.
**Fix:** Create a connection reference; update the flow to use it.

### SN-NN-010: Flows Inside Solution
Every flow must be inside the project solution.
Flows created outside the solution will not be included in exports.

**Violation:** Flow exists in My Flows but not in the solution.
**Fix:** Add the flow to the solution.

---

## Canvas App Standards

### SN-NN-011: App Checker Zero Errors
Every Canvas App must pass App Checker with 0 errors across all 5 categories
(Formulas, Runtime, Accessibility, Performance, Data source) before sign-off.

**Violation:** App has 3 accessibility errors.
**Fix:** Fix each error; re-run App Checker; verify 0 errors.

### SN-NN-012: Solution-Aware Canvas App
Canvas Apps must be created inside the solution (not as personal apps).
They must be solution-aware to be included in exports.

**Violation:** Canvas App was created from Make.PowerApps.com home without
selecting the solution first.
**Fix:** The app cannot be moved. A new app must be created inside the solution.

### SN-NN-013: No Hardcoded Connections
Canvas Apps must use named data sources connected to the project solution's
Dataverse tables. No hardcoded connection strings or direct SQL.

---

## MDA Standards

### SN-NN-014: MDA Must Be Published
Every Model-Driven App must be published before it is considered complete.
An unpublished MDA will not reflect schema or sitemap changes.

**Violation:** Sitemap updated but `PublishAllXml` not called.
**Fix:** Call `PublishAllXml`.

### SN-NN-015: All Tables Must Have a Main Form
Every table that appears in the MDA sitemap must have at least one published
Main form. Quick Create forms are optional. Card forms are optional.

**Violation:** ops_request is in the sitemap but has no Main form.
**Fix:** Create and publish a Main form for ops_request.

---

## Deployment Standards

### SN-NN-016: Version Before Every Deploy
The solution version must be incremented before every deployment.
Format: `major.minor.patch.build`

**Violation:** Deploying version 1.0.0.0 for the third time.
**Fix:** Increment to 1.0.0.3 before deploying.

### SN-NN-017: Deployment Checklist Completed
Every deployment requires the pre-deployment checklist from
`templates/deployment-checklist.md` to be completed and acknowledged
by the developer before proceeding.

**Violation:** Deployment triggered without checklist confirmation.
**Fix:** Print checklist, obtain confirmation, then deploy.

---

## Documentation Standards

### SN-NN-018: Plan Must Cover All User Stories
Every user story in `docs/requirements.md` must be traceable to at least
one component in `docs/plan.md`.

**Violation:** US-4 ("Viewer can export report") has no corresponding component.
**Fix:** Add the report component to the plan, or explicitly descope US-4 with user approval.

### SN-NN-019: Security Design Must Cover All Tables
Every custom table must appear in `docs/security-design.md` with a privilege
matrix showing Create/Read/Write/Delete/Append/AppendTo for every role.

**Violation:** ops_audit_log table missing from security-design.md.
**Fix:** Add ops_audit_log to the security matrix.
