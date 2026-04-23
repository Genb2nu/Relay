---
name: power-platform-footgun-checklist
description: |
  Critic's structured checklist of known Power Platform footguns, anti-patterns,
  and common oversights. Critic walks this list before any free-form review.
  Each item is marked PASS / FAIL / N/A with a one-line justification.
trigger_keywords:
  - footgun
  - checklist
  - critic review
  - adversarial check
allowed_tools:
  - Read
---

# Power Platform Footgun Checklist

Critic: walk every item below. For each, mark PASS / FAIL / N/A and write a
one-line justification. If any item is FAIL, proceed to free-form adversarial
review after completing the full checklist.

## Schema & Data Model

### 1. Plugin execution order
- **What to check**: If multiple plugins register on the same table/message/stage, is the execution order explicitly defined?
- **Why it matters**: Undefined order means unpredictable behaviour. Plugin A may depend on Plugin B's output, but run first.
- **Mark N/A if**: No plugins in the solution.

### 2. Circular references in schema
- **What to check**: Do any table relationships create a cycle? (A → B → C → A)
- **Why it matters**: Circular cascade can cause infinite loops on delete/assign.

### 3. Cascade delete safety
- **What to check**: Are any 1:N relationships set to Cascade All for delete? Would deleting a parent wipe out critical child records?
- **Why it matters**: Accidental cascade delete of thousands of records is unrecoverable without backup.

### 4. Column limits per table
- **What to check**: Does any table approach the 1,024 column limit? Are computed/rollup columns counted?
- **Why it matters**: Hitting the limit mid-project blocks new features.

### 5. Data volume and delegation
- **What to check**: For canvas apps, are there non-delegable functions (e.g. `CountRows`, `Search`, `SortByColumns` on large tables)?
- **Why it matters**: Non-delegable queries only process the first 500/2000 records. Results are silently incomplete.

## Flows & Automation

### 6. Flow concurrency limits
- **What to check**: Do any flows need sequential processing? Is the concurrency degree set correctly?
- **Why it matters**: Default concurrency allows parallel runs. If the flow creates/updates records, parallel runs cause race conditions and duplicates.

### 7. Flow error handling
- **What to check**: Does every flow have error handling (Scope with Configure run after → failed/timed out)?
- **Why it matters**: A flow that fails silently is worse than no flow. Data ends up in an inconsistent state with no alert.

### 8. Flow throttling
- **What to check**: Could any trigger fire at high volume? (e.g. bulk data import triggering "When a row is added" 10,000 times)
- **Why it matters**: Dataverse throttles at ~6,000 requests/5 minutes. Mass-trigger scenarios queue and delay, or fail entirely.

### 9. Business rule vs plugin conflict
- **What to check**: Are there Business Rules and plugins registered on the same table/event that could conflict?
- **Why it matters**: Business Rules execute client-side (on forms) AND server-side. A plugin on the same message may see different data depending on execution order.

### 10. Async vs sync plugin choice
- **What to check**: Are plugins registered as synchronous when they should be async, or vice versa?
- **Why it matters**: Sync plugins block the user's save operation. Long-running logic in sync = timeout errors for users.

## Solution & Deployment

### 11. Solution layering conflicts
- **What to check**: Does this solution modify components owned by another solution? Are there active-layer customisations?
- **Why it matters**: Importing a managed solution over active-layer changes can silently lose customisations.

### 12. Connection reference identity
- **What to check**: Does any connection reference use the maker's identity instead of invoking user?
- **Why it matters**: Privilege escalation. See `power-platform-security-patterns` Trap 6.

### 13. Environment variables for env-specific values
- **What to check**: Are URLs, email addresses, tenant IDs, or other environment-specific values hardcoded instead of using Environment Variables?
- **Why it matters**: Hardcoded values break on import to a different environment.

### 14. Managed vs unmanaged strategy
- **What to check**: Is the deployment plan clear about which environments get managed vs unmanaged?
- **Why it matters**: Unmanaged in production = ungovernable. Can't cleanly remove or version.

## Security Cross-Check

### 15. Quick-view FLS coverage
- **What to check**: If a column has FLS, is it also restricted on every quick-view form that displays it?
- **Why it matters**: FLS on the main form means nothing if the column is exposed on a quick-view embedded in another entity's form.

### 16. Requirements fully covered by plan
- **What to check**: Cross-reference every user story in requirements.md against plan.md. Is anything missing?
- **Why it matters**: Drafter may have dropped a requirement without noticing.

### 17. Security design matches requirements trust boundaries
- **What to check**: Do the security roles and FLS in security-design.md actually enforce the trust boundaries specified in requirements.md?
- **Why it matters**: Security design can drift from requirements if Warden focused on technical feasibility over requirement coverage.

## Licensing & Limits

### 18. Licensing implications
- **What to check**: Does the solution require premium connectors? Additional Dataverse capacity? Per-app vs per-user licensing?
- **Why it matters**: Licensing costs can make a technically sound solution economically infeasible.

---

## How to Use This Checklist

1. Read `docs/plan.md`, `docs/security-design.md`, and `docs/requirements.md`
2. For each numbered item above, determine PASS / FAIL / N/A
3. Write results into `docs/critic-report.md` using the critic report template
4. If ANY item is FAIL, proceed to Mode 2 (free-form adversarial review)
5. If ALL items are PASS or N/A, approve immediately

### 19. /genpage used for standard MDA configuration
- **What to check**: If Forge used /genpage to configure MDA sitemap, forms, or views
- **Why it matters**: /genpage builds custom React/TypeScript coded pages only. Using it for standard configuration fails silently or produces wrong output. Standard MDA config uses Dataverse API to patch sitemap/form XML.
- **Mark N/A if**: No model-driven app in the solution, or /genpage was only used for actual custom coded pages.

### 20. Duplicate app modules or components
- **What to check**: Does state.json track all created component GUIDs? Did Forge check state.json before creating any app module, connection reference, or other named component?
- **Why it matters**: Without state coordination, Forge creates duplicate app modules when it can't find the one Vault created (naming mismatch). Leads to "two Leave Request Admin apps" problem.
- **Mark N/A if**: No app modules or shared components in the solution.

### 21. FLS profile assignment automated
- **What to check**: Were FLS profile assignments automated via Dataverse API, or incorrectly declared "manual"?
- **Why it matters**: FLS assignment IS automatable via `systemuserprofiles` and `teamprofiles` endpoints. Leaving it manual wastes user time unnecessarily.
- **Mark N/A if**: No FLS profiles in the solution.

### 22. Security role assignment to users automated
- **What to check**: Were security role assignments automated via `pac admin assign-user`, or incorrectly declared "manual"?
- **Why it matters**: PAC CLI can assign roles to known users. Only skip automation if users aren't known at build time.
- **Mark N/A if**: User list not known at build time (acceptable reason to leave manual with documented instructions).

### 23. Flow import automation attempted
- **What to check**: Were Power Automate flows generated as JSON and imported via solution, or incorrectly skipped as "not automatable"?
- **Why it matters**: Flows ARE automatable via solution import. Only connection linking and flow activation are genuinely manual.
- **Mark N/A if**: No flows in the solution.
