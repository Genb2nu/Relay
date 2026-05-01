# Relay Improvement Backlog
## Captured from LRS Smoke Test (Sessions 2025-07 through 2026-07)

This document captures all learnings, gaps, and improvement candidates identified during the
Leave Request System (LRS) real-world pilot run. Items are grouped by agent/area.

---

## Warden / Security Script Generation

**IMP-01: No non-ASCII characters in generated PowerShell scripts**
- Root cause: Generated scripts used emoji (✅ ❌) and em-dashes (—) in Write-Host
- Effect: PS 5.x cp1252 consoles parse-fail; script exits immediately
- Fix: Warden must generate PS 5.x safe output — ASCII only, [PASS]/[FAIL]/[SKIP] tags
- Priority: HIGH — every generated test script was broken on first run

**IMP-02: PowerShell 5.x compatibility constraints must be documented in SKILL.md**
- PS 5.x bans: `?.` null-conditional, ternary (`? :`), `&&`/`||` operators, `&` in mid-string concatenation
- Fix: Add explicit PS 5.x constraint checklist to power-platform-alm SKILL.md
- Priority: HIGH

**IMP-03: security-tests.ps1 must use If-Match: * header on all PATCH/DELETE requests**
- Root cause: PATCH without If-Match returns 412 Precondition Failed, not 403, on CRM entities
- Effect: Tests counted 412 as "unexpected block" rather than success/fail
- Fix: `Make-Headers` in generated test scripts must include `If-Match: *` by default for mutation ops
- Priority: HIGH

**IMP-04: Assert-ExceptionContains must check ErrorDetails.Message, not just stream body**
- Root cause: In PowerShell `Invoke-RestMethod`, the error body is in `$_.ErrorDetails.Message`, not the stream
- Effect: All plugin-thrown messages were "blank" — tests couldn't match error text
- Fix: Template must check ErrorDetails.Message first, stream second, Exception.Message last
- Priority: HIGH

---

## Vault / Schema Provisioning

**IMP-05: register-plugins.ps1 must register pre-images even when step already exists**
- Root cause: Script skipped pre-image registration when step was found (treated as already done)
- Effect: Pre-images missing → plugin threw KeyNotFoundException at runtime
- Fix: Always call sdkmessageprocessingstepimages POST regardless of step existence check
- Priority: HIGH — caused plugin failure in every run

**IMP-06: Plugin step filtering attributes must be set explicitly**
- Root cause: Vault did not set `filteringattributes` on Update steps
- Effect: Plugin fired on ALL updates, not just status changes — performance degradation
- Fix: Always set `filteringattributes: "lrs_status"` (or relevant columns) in sdkmessageprocessingstep PATCH
- Priority: MEDIUM

**IMP-07: After registering pre-images, plugin steps must be deactivated + reactivated**
- Root cause: Dataverse sandbox caches plugin registration; new pre-images not visible until cache flushes
- Fix: After any pre-image registration, immediately PATCH step statecode=1 then statecode=0
- Priority: HIGH — required every time pre-images are added/changed

**IMP-08: Vault must assign role privileges immediately, not leave roles as empty shells**
- Root cause: Three security roles created with no privileges assigned — separate fix script required
- Effect: All role-based access tests meaningless until privileges assigned
- Fix: Role creation script must call AddPrivilegesRole inline, not as a separate manual step
- Priority: HIGH

**IMP-09: Role privilege depth matters — AddPrivilegesRole does not downgrade existing Global privs**
- Root cause: If a role was previously given Global depth, calling AddPrivilegesRole with Basic does not downgrade
- Fix: Use RemovePrivilegeRole first, then AddPrivilegesRole to set correct depth
- Priority: MEDIUM

**IMP-10: Security role assignment API — correct disassociate URL format**
- Root cause: Multiple incorrect formats tried for `DELETE /systemuserroles_association`
- Correct format: `DELETE /systemusers({userId})/systemuserroles_association({roleId})/$ref`
- Note: `$ref` at END of path, not as query param
- Priority: MEDIUM (reference data)

**IMP-11: OData URL construction — never split with & in mid-string PS5 concatenation**
- Root cause: `"$base/entity?$filter=...&$select=..."` with backtick-escaped `$` fails if string concatenated with `&` in a command
- Fix: Assign OData URL to variable first, then pass variable to Invoke-RestMethod
- Priority: MEDIUM

---

## Sentinel / Test Environment Validation

**IMP-12: Sentinel must verify test users do NOT have SysAdmin or SysCustomizer before Phase 6**
- Root cause: user5 + user1 had System Administrator + System Customizer roles → bypassed ALL Dataverse security
- Effect: All "BLOCKED" tests returned 200 (bypassed); tests masked as PASS via 401 when tokens expired
- Fix: Add Phase 6 pre-check: `RetrieveUserPrivileges` → fail if any test user has `prvAllTables` or `prvReadAuditData` at Global
- Priority: CRITICAL

**IMP-13: TestBalanceRecordId in seed data must be owned by a DIFFERENT user than TOKEN_EMPLOYEE**
- Root cause: T-BAL-02 tested employee reading "another's balance" but record was owned by the employee
- Effect: Test always passed (own-record read) even without proper row isolation
- Fix: Seed data script must assign each test record to the correct owner explicitly. Balance record for T-BAL-02 must be owned by user2 (manager), not user5 (employee)
- Priority: HIGH

**IMP-14: Dataverse flat-BU environments cannot enforce row-level isolation via privilege depth alone**
- Root cause: In single Business Unit environments, "Basic" depth privilege does not restrict list queries — all users see all records
- Effect: T-SEC-01a/b/c, T-ESC-01, T-BAL-02 cannot pass without child BUs, Access Teams, or ownership-specific filters
- Fix: Sentinel must document which tests require multi-BU or Access Team configuration. Plan must specify BU topology if row isolation is a requirement.
- Priority: CRITICAL (architecture)

**IMP-15: Dataverse privilege enforcement for custom table Create/Write may be bypassed in developer orgs**
- Root cause: In this test environment, employees could POST/PATCH custom tables (lrs_escalation, lrs_leavebalance) even without Create/Write privileges
- Effect: T-ESC-02, T-BAL-01, T-LT-01 cannot pass in developer org with permissive mode
- Fix: Sentinel should test against production-mode environments or document this as environment limitation
- Priority: HIGH

---

## Forge / Plugin Development

**IMP-16: Dataverse plugin trace log endpoint is `plugintracelogs` (plural)**
- Root cause: `plugintracelog` (singular) returns 0x80060888 "resource not found"
- Fix: Update diagnose scripts to use `plugintracelogs` entity set name
- Priority: LOW (operational knowledge)

**IMP-17: Plugin self-approval check must be guarded against null requestorid**
- Root cause: If `lrs_requestorid` is null in pre-image, plugin skips self-approval check silently
- Effect: Employee can set status=Approved without being blocked
- Fix: Plugin must explicitly block status=2/3 unless caller has HR Admin role, independent of requestorid lookup
- Priority: HIGH — add IsUserInRole(HR Admin) guard before the self-approval QueryExpression

**IMP-18: Plugin must not swallow InvalidPluginExecutionException in catch block**
- Root cause: `catch (Exception ex)` re-throws `InvalidPluginExecutionException` correctly via `throw` but the outer catch-all silently continues
- Effect: In edge cases, legitimate plugin blocks may be swallowed
- Fix: Pattern: catch (InvalidPluginExecutionException) { throw; } catch (Exception ex) { trace + return; } — always re-throw IPEE
- Priority: MEDIUM

**IMP-19: `pluginassembly` PATCH body must not include `ishidden` as an array**
- Root cause: Sending `{"content":"...","ishidden":false}` causes OData parser error `PrimitiveValue node found where StartArray expected`
- Fix: Only send `{"content":"base64..."}` when updating assembly content
- Priority: MEDIUM

---

## Conductor / Orchestration

**IMP-20: After any `/compact`, Conductor must re-read state.json AND plan-index.json before continuing**
- Root cause: Post-compact context lost agent persona states, which roles had been granted, etc.
- Fix: This is already documented in CLAUDE.md Post-/compact Re-read section — reinforce with explicit checklist
- Priority: MEDIUM

**IMP-21: Test record reset must deactivate StatusValidator plugin before resetting rejected records**
- Root cause: StatusValidator enforces BR-05 (Rejected→Pending blocked) — makes reset FAIL
- Fix: reset-test-records.ps1 must deactivate plugin step → reset → reactivate
- Priority: HIGH (operational)

**IMP-22: Security test suite must not run twice in a single powershell.exe invocation**
- Root cause: The test script apparently runs twice (first stale-token run + fresh-token run in same invocation)
- Effect: Two separate PASS/FAIL summaries shown; final score is the second run, but first run pollutes state (records consumed by first run)
- Fix: Investigate if this is a test script SETUP block running as a separate pass — check for duplicate invocation in security-tests.ps1 or wrapper script
- Priority: HIGH

---

## Skills Needed

**IMP-23: New skill needed: `dataverse-privilege-depth-patterns`**
- Content: privilege depth semantics in single vs multi-BU; AddPrivilegesRole vs ReplacePrivilegesRole; RemovePrivilegeRole; RetrieveUserPrivileges API; team-based access patterns; Access Teams vs owner teams
- Why: Multiple agents burned time on privilege depth trial-and-error

**IMP-24: New skill needed: `dataverse-plugin-deployment-cycle`**
- Content: compile → upload DLL (pluginassemblies PATCH) → deactivate step → reactivate step → test → read plugintracelogs; cache flush protocol
- Why: Every plugin fix required the same 5-step pattern with no documented guide

**IMP-25: `power-platform-security-patterns` SKILL.md needs privilege depth section**
- Add: flat-BU limitation note; Basic depth ≠ row isolation in single BU; when to recommend Access Teams
- Priority: HIGH

---

## Prioritization Summary

| Priority | Count | Key Items |
|---|---|---|
| CRITICAL | 2 | IMP-12 (SysAdmin test users), IMP-14 (flat-BU isolation) |
| HIGH | 12 | IMP-01,02,03,04,05,07,08,13,15,17,21,22 |
| MEDIUM | 8 | IMP-06,09,10,11,18,19,20,23 |
| LOW | 3 | IMP-16,24,25 |

---

*Last updated: 2026-07-28 — LRS smoke test final session*
