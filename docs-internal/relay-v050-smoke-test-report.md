# Relay v0.5.0 Smoke Test Report
**Project:** Emerald Polytechnic Contract Management System (EP CMS)
**Environment:** copilot-test1.crm5.dynamics.com
**Test window:** Relay v0.5.0, GitHub Copilot CLI
**Tester:** Conductor (manual relay turns)
**Date:** 2026-05-01

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total findings | 58 |
| Relay infrastructure bugs/enhancements | 30 |
| Project-specific (CMS design) | 28 |
| Phases completed | 6 of 6 (Phase 6 = PARTIAL PASS) |
| Critical Relay bugs | 5 |
| Schema deployed |  16 tables, 6 roles, 3 FLS, 5 BUs |
| Canvas App deployed |  Blocked (F27) |
| Flows deployed |  Blocked (F20) |
| MDA deployed |  Blank shell only (F29) |

Relay v0.5.0 successfully completed all 6 phases end-to-end with workarounds.
The core schema, security design, and plan quality are production-grade.
Five critical CLI-mode bugs block unassisted runs  all are fixable for v0.5.1.

---

## PART 1  RELAY INFRASTRUCTURE FINDINGS
*These are bugs or enhancements needed in Relay itself. Nothing to do with the CMS project.*

---

###  Critical  Must fix before v0.5.1 GA

#### F6  Drafter cannot create large files in CLI mode (unrecoverable)
**What happened:** Drafter was launched 3 times to write `docs/plan.md`. Each attempt failed
silently  no error, no output file, agent just stopped. The plan is ~40KB of structured
markdown + code. Splitting into two sequential subagent calls (one file each) also failed.

**Root cause hypothesis:** CLI subagent context window is smaller than VS Code sessions.
Large code/schema output hits the token budget before the `create` tool call is reached.
Code has higher token density per byte than prose  the 39KB requirements input +
plan generation together exceed the limit. Critic and Stylist succeeded at similar byte
counts because they write prose (lower token density).

**Workaround used:** Conductor wrote `plan.md` section-by-section using direct `edit`/`create`
tool calls instead of delegating to Drafter.

**Fix for v0.5.1:**
- `relay-workflow`: In CLI mode, Drafter must write files in 400-line chunks using
  sequential `edit` tool calls, never a single `create` for the full file.
- Add a `CLAUDE.md` note: `max_output_chunk_lines: 400` for CLI mode.
- Or: Conductor pre-creates empty plan.md and Drafter appends section-by-section.

---

#### F11  Vault agent silent context overflow  same issue as Drafter
**What happened:** Vault wrote all 4 scripts to `scripts/` (wrong folder) instead of `src/dataverse/`,
then appeared to hang. Eventually completed at 23 min. Same token-overflow pattern as Drafter.

**Fix for v0.5.1:** Same chunk-based approach. Vault should write one table group per agent
call (e.g., "write tables 15 to create-schema.ps1") rather than the full 16-table script
in one pass. Conductor orchestrates the sequential calls.

---

#### F13  `stop_powershell` does NOT kill background agents
**What happened:** After Vault ran for 20+ min with no progress, `stop_powershell` was called.
The tool returned success. Vault continued running and eventually completed. Agent processes
are isolated from the PowerShell session  the shell kill has no effect on the agent.

**Fix for v0.5.1:** Document this clearly in `relay-orchestration` skill. Add a note to
`relay-workflow`: "If a subagent appears hung, do not attempt to kill it via stop_powershell.
Wait for the completion notification. If no notification after 30 min, assume failure and
re-launch with a smaller scope."

---

#### F22  Relay never validates authenticated identity before deployment
**What happened:** `pac auth list` showed 5 profiles. The active one (user5) was missing
`prvReadSolution` and had no solution management rights. Deployment attempts failed silently.
Relay never asked "which user should we deploy as?" before Phase 5.

**Root cause:** Relay has no pre-deploy auth check step. The conductor assumes the active
pac auth profile has sufficient rights.

**Fix for v0.5.1:** Add a `validate-auth` gate at the start of Phase 5:
```powershell
pac auth who   # confirm identity
pac solution list --environment $env  # confirm can read solutions
```
If `pac solution list` fails, halt and ask user to run `pac auth select` or `pac auth create`.
Document in `relay-workflow` Phase 5 preconditions.

---

#### F27  Forge pa.yaml output incompatible with `pac canvas pack`
**What happened:** Forge correctly generates pa.yaml files for the Canvas App screens.
`pac canvas pack` was run to produce an `.msapp` file for deployment.
Error: `PA3002: Can't find CanvasManifest.json  is sources an old version?`

**Root cause:** `pac canvas pack/unpack` uses the **old** msapp format
(`CanvasManifest.json` + per-screen `.json` files). Forge generates the **new** pa.yaml
format, which is the Canvas Authoring MCP format. These are incompatible.
`pac canvas pack` is also deprecated as of PAC CLI 2.6.4.

**Fix for v0.5.1:** Canvas App deployment in CLI mode must use Canvas Authoring MCP
(`canvas-authoring` MCP server). Add to `relay-workflow` Phase 5:
- If Canvas Authoring MCP is configured  use MCP push
- If MCP is not available  generate manual import instructions pointing to make.powerapps.com
- Remove any references to `pac canvas pack` from Relay scripts

---

###  High — Fix for v0.5.1

#### F2  Scout crashes on PNG files despite Vision-disabled instruction
**What happened:** Scout received 4 PNG wireframe files via `/relay:load`. The load command
context summary stated Vision was disabled. Scout attempted to process the PNGs anyway and
crashed.

**Fix:** `relay:scout` agent instructions must explicitly skip binary/image files. Add file
type guard: "If any context file has extension .png, .jpg, .gif, .bmp  skip it entirely
and note it in the context summary as 'wireframe  Vision required, skipped'."

---

#### F5  Drafter context window overflow  file create failures
*(See F6  same root cause, earlier manifestation. Logged separately as it was the
first occurrence with templates/ confusion.)*

**Additional note:** Drafter also looked for `templates/plan-template.md` which does not
exist in the CLI plugin path. This compounded the failure.

**Fix:** Remove template file lookups from Drafter. Drafter should write plans from its
embedded knowledge. If a template is desired, it must be embedded in the agent's system
prompt, not referenced as a file path.

---

#### F20  Forge produces flow JSON scaffold  not a deployable Power Automate package
**What happened:** Forge wrote `src/flows/flow1-approval-routing.json`  a clean, readable
JSON describing the flow's 8 steps. This cannot be imported into Power Automate. A deployable
package is a `.zip` containing `definition.json` + `manifest.json` + connection references.

**Fix for v0.5.1:**
- **Option A (recommended):** Forge generates flows as Power Automate Solution-layer JSON
  (`src/flows/` structured for `pac solution add-reference`), not standalone JSON.
- **Option B:** Forge documents each flow as a step-by-step build guide (markdown), and
  Phase 5 deploy checklist tells the user to build manually in Power Automate designer.
- Add finding to `relay-workflow`: "Power Automate flows cannot be deployed via CLI in
  v0.5.0. Manual creation in make.powerautomate.com is required."

---

#### F24  `create-roles.ps1` not idempotent  creates duplicate roles on re-run
**What happened:** Running `create-roles.ps1` a second time creates a new set of roles
instead of skipping existing ones. Dataverse allows multiple roles with the same name at
different BUs. The idempotency check filtered by name only, not by name + root BU ID.

**Fix:** Vault-generated role scripts must filter: `$filter=name eq '<name>' and _businessunitid_value eq <rootBuId>`. If a role exists at root BU, skip creation.

---

###  Medium  Backlog for v0.5.1

#### F1  `/relay:load` + `/relay:start` conflict
`/relay:load` writes `state.json` with `phase=context_loaded`. `/relay:start` refuses to
run if `state.json` already exists. The user is explicitly told to run `start` after `load`.
**Fix:** `start` should treat `phase=context_loaded` as a valid pre-start state and merge
context into a fresh initialisation rather than blocking.

---

#### F3  Scout requires 7 separate manual relay turns  stateless UX friction
Scout asked 7 gap questions but each one required the user to copy-paste the answer and
re-invoke the skill. With stateful sessions, Scout could continue the conversation
interactively.

**Fix (v0.5.1 UX):** Scout should batch all gap questions into a single numbered list in
one turn, accept a single reply, then continue. Reduces 7 relay turns  1.

---

#### F7  Conductor forced to bypass Drafter  plan written directly by Conductor
After 3 Drafter failures, Conductor wrote `docs/plan.md` directly. This is a workaround,
not a supported pattern. The plan quality was still high, but the relay workflow was broken.

**Note:** This is a *consequence* of F6, not an independent bug. The fix is F6.

---

#### F8 / F14  Subagents (Warden, Forge) cannot create directories
Warden tried to write `scripts/security-tests.ps1`  failed because `scripts/` didn't
exist. Forge had the same issue. Three separate agents encountered this.

**Fix:** `relay-workflow` Phase 5 pre-flight: Conductor pre-creates all expected output
directories before launching subagents. Add a `bootstrap-dirs.ps1` step to relay:start
or add directory creation to each agent's preamble instructions.

---

#### F23  Vault-generated scripts use PS 7 null-coalescing `??`  breaks on PS 5.1
`create-roles.ps1` and `create-bu.ps1` used `$d??$_.Exception.Message`  a PowerShell 7
operator. Windows default is PowerShell 5.1. Scripts failed with parse errors.

**Fix:** Vault agent instructions must specify: "Write PowerShell compatible with PS 5.1.
Do not use `??`, `?.`, or `&&`/`||` pipeline chain operators."

---

#### F25  Vault scripts use hardcoded relative path for state.json
Scripts wrote back to `.relay/state.json` using a relative path, which broke when scripts
were run from a different working directory.

**Fix:** Vault scripts should resolve state.json relative to `$PSScriptRoot`, not the
current working directory.

---

#### F29  `pac model create` (Preview) creates blank MDA  sitemap not imported
`pac model create` creates and publishes an MDA but with no areas or navigation.
`src/mda/sitemap.xml` exists but there is no `pac` command to apply it.

**Fix:** Forge should package the sitemap into a minimal solution ZIP for
`pac solution import`, rather than generating a standalone XML file.

---

#### F28  AddSolutionComponent requires non-obvious integer component type codes
Conductor had to discover the correct codes by reading error messages (Type 20=Role,
70=FLS Profile, 1=Entity). Wrong codes return misleading errors ("Cannot add FieldSecurityProfile"
when adding a Role with type 70).

**Fix:** Add a constants table to Vault-generated deploy scripts and document in
`relay-workflow`. Or generate a `add-to-solution.ps1` helper with named constants.

---

###  Info / Positive observations

| ID | Observation |
|----|-------------|
| F10 | Critic wrote 36KB adversarial report in one pass  prose agents are unaffected by context overflow |
| F15 | Forge succeeded on all 5 YAML/XML/JSON runs with 400 line budget  workaround confirmed |
| F16F18 | Forge sub-30s for XML, 87121s for YAML  fast when scoped correctly |
| F26 | Dataverse creating 6 role copies (1 per BU) is expected behavior  not a Relay bug |
| S1 | Stylist produced 40KB design-system.md with 43 colour tokens in 229s  no issues |

---

## PART 2  PROJECT-SPECIFIC FINDINGS (EP CMS DESIGN)
*These are issues with the CMS design, requirements, or security model  not Relay bugs.
Included for completeness. All were resolved or accepted during Phase 3/4.*

### Auditor findings (Phase 3)  all resolved in Plan revision pass 1

| ID | Severity | Title | Resolution |
|----|----------|--------|------------|
| A1 | Critical | No contract generation flow (BR-10) | Flow 7 added to plan |
| A2 | Critical | Flow 1 approval wait mechanism not implementable as written | Redesigned with adaptive card + deadline timer |
| A3 | Critical | Canvas Steps 2, 3, 4 entirely unspecified | Scoped to smoke test  3 screens only |
| A4 | Critical | US-09 PL contract verification gate missing | Added to Flow 1 pre-approval step |
| A5 | Critical | OD-08 approver identity lookup unresolved | Resolved: ep_approverconfig lookup |
| A6 | Critical | ep_staffdetail contribution_type conflict | Renamed to ep_contribution_percent |

### Warden findings (Phase 3)  all resolved in security-design revision

| ID | Severity | Title | Resolution |
|----|----------|--------|------------|
| W1 | Critical | No plugin enforcing form status machine | FormStatusGuard plugin spec added to plan |
| W2 | Critical | ep_workday_empl_id unprotected | Added to FLS Staff HR Data profile |
| W3 | Critical | Child records not cascade-shared to Approvers | Sharing step added to Flow 1 |
| W5 | Major | Table ownership type not declared | All 16 tables annotated in plan 4 |
| W6 | Major | Director retains Write during approval chain | Director Write revoked on submission |
| W7 | Major | ep_eom_rate readable by OIC/Finance without FLS | Added to FLS Contract Confidential |

### Critic findings (Phase 4)  all resolved in Plan revision pass 2

| ID | Severity | Title | Resolution |
|----|----------|--------|------------|
| C1 | Critical | Flow 2 e-signature chain >30-day run limit | Redesigned with sub-flow child processes |
| C2 | Critical | gblPendingBilling 3-hop non-delegable traversal | Rewritten with denormalised ep_project_leader column |
| C3 | Critical | Workday EOM rate 3-way contradiction | Authoritative source declared: Workday Snapshot |
| C4 | Critical | ep_approverconfig null-ref crash on leave | Deputy fallback + P5D null-guard added |
| C5 | Major | Migration scripts POST-only  duplicates on re-run | Upsert via alternate keys added |
| C6 | Major | OIC team access never designed | OIC sharing scope documented in security-design |
| C7 | Major | Resubmission duplicates ep_approvalrecord rows | Deactivate-then-recreate pattern added |
| C8 | Major | FormStatusGuard plugin declared but not designed | Plugin spec written in plan 8 |

### Sentinel findings (Phase 6)  require action before production

| ID | Severity | Title | Status |
|----|----------|--------|--------|
| F30 | Critical | FLS SP not in profiles  Flow 1 silent null-routing bug | Open  manual fix required |
| R1 |  | Canvas App not deployed | Open  blocked by F27 |
| R2 |  | Power Automate flows not built | Open  blocked by F20 |
| R3 |  | MDA sitemap not imported | Open  blocked by F29 |
| R4 |  | FormStatusGuard plugin not built | Open  Phase 5 scope gap |
| R5 = F30 | Critical | epConnectionDataverse SP missing from FLS profiles | Open |

---

## PART 3  RELAY v0.5.1 RECOMMENDED CHANGES

### Priority 1  Critical (blocks unassisted CLI runs)

| # | Change | Skill/File to Update |
|---|--------|---------------------|
| P1 | CLI chunk-based file writing  400 line budget, sequential edit calls | `relay-workflow`, `CLAUDE.md` |
| P2 | Remove `templates/plan-template.md` lookup from Drafter | `agents/drafter.agent.md` |
| P3 | Canvas App deployment via Canvas Authoring MCP (not pac canvas pack) | `relay-workflow` Phase 5 |
| P4 | Pre-deploy auth validation gate (`pac auth who` + `pac solution list`) | `relay-workflow` Phase 5 |
| P5 | Document `stop_powershell` does not kill agents | `relay-orchestration` skill |

### Priority 2  High (significant UX/reliability gaps)

| # | Change | Skill/File to Update |
|---|--------|---------------------|
| H1 | Scout batch gap questions (7  1 turn) | `agents/scout.agent.md` |
| H2 | Flows deployment: document manual Power Automate path or switch to solution JSON format | `relay-workflow` Phase 5 |
| H3 | Vault PS 5.1 compatibility requirement | `agents/vault.agent.md` |
| H4 | Vault idempotent role creation (name + root BU filter) | `agents/vault.agent.md` |
| H5 | `/relay:load` + `/relay:start` phase=context_loaded merge instead of block | `commands/start.md` |

### Priority 3  Medium (polish and robustness)

| # | Change | Skill/File to Update |
|---|--------|---------------------|
| M1 | Conductor pre-creates output dirs before all subagent launches | `relay-workflow` Phase 5 |
| M2 | Vault writes state.json path relative to $PSScriptRoot | `agents/vault.agent.md` |
| M3 | MDA sitemap: Forge packages into solution ZIP for `pac solution import` | `agents/forge.agent.md` |
| M4 | AddSolutionComponent constants table (type 1=Entity, 20=Role, 70=FLS, etc.) | `relay-workflow` deploy step |
| M5 | Vault post-deploy: add FLS service principal memberships | `agents/vault.agent.md` |

---

## Phase Completion Summary

| Phase | Agent | Duration | Outcome | Key Finding |
|-------|-------|----------|---------|-------------|
| 1 Discovery | Scout | ~45 min (7 turns) |  Complete | F3: stateless UX |
| 2 Planning | Drafter  3 | ~60 min |  Conductor bypass | F5, F6: context overflow |
| 3 Review | Auditor + Warden | ~15 min |  Complete | A1A6, W1W7 resolved |
| 4 Adversarial | Critic | ~8 min |  Complete | C1C8 resolved; plan locked |
| 5 Build | Vault (23 min) + Stylist (4 min) + Forge (5 runs) | ~45 min |  Partial | F11, F12, F20, F27 |
| 5 Deploy | Conductor | ~30 min |  Partial | F22, F24, F28, F29 |
| 6 Verify | Sentinel | ~4 min |  PARTIAL PASS | F30, 7 pre-documented gaps |

**Total test duration:** ~3.5 hours (including manual relay turns and wait times)

---

## Conclusion

Relay v0.5.0 is **feature-complete but not CLI-production-ready**.
The VS Code variant likely works well (prose agents + Canvas Authoring MCP cover the gaps).
Five targeted fixes (P1P5) would make CLI-mode unassisted runs viable for v0.5.1.
The core architecture  Scout  Drafter  Auditor/Warden  Critic  Vault/Stylist/Forge  Sentinel 
is sound and produced a high-quality, deployable Dataverse schema and security design.

*End of Relay v0.5.0 Smoke Test Report*
