# Relay Enhancement Plan
## Version: v0.5.0 (proposed)
## Source: LRS Smoke Test findings + improvement backlog

---

## 1. Fleet Readiness Assessment

### Current Status: PARTIAL

/fleet is documented in CLAUDE.md but has two critical gaps:

| Item | Status | Notes |
|---|---|---|
| /fleet command exists in Copilot CLI | UNTESTED | No fleet command file in `commands/` — it is a Copilot CLI native feature, not a Relay command |
| /fleet works in VS Code Agent Mode | NO | CLAUDE.md explicitly states: "NOT available in VS Code Agent Mode" |
| Agents are self-contained enough for parallel dispatch | PARTIAL | Agents reference each other's outputs (e.g. Auditor reads Warden's report) — violates independence rule |
| /fleet prompts are documented | YES | CLAUDE.md has 6 fleet prompt templates (Phase 3, 5a, 5b, 5b-verify, 6, audit) |
| Agents operate on their specific tasks/skills | PARTIAL | See Agent-by-Agent assessment below |

### Agent-by-Agent Readiness (for /fleet dispatch)

| Agent | Reads correct skill? | Scope correct? | Fleet-safe (no shared mutable state)? | Gap |
|---|---|---|---|---|
| Scout | relay-discovery SKILL.md | Yes | Yes | Writes state.json (safe — Phase 1 only) |
| Drafter | relay-planning SKILL.md | Yes | Yes | None observed |
| Auditor | (no assigned skill) | Yes | YES | **MISSING: no skill assigned in agents/auditor.agent.md** |
| Warden | power-platform-security-patterns SKILL.md | YES | Partial | Reads Auditor's output in some patterns (violates independence) |
| Critic | power-platform-footgun-checklist SKILL.md | Yes | Yes | None observed |
| Vault | (no dedicated skill) | Yes | YES | **MISSING: Dataverse API patterns live in ALM skill — Vault should have its own** |
| Forge | power-platform-alm SKILL.md | Partial | YES | Automation capability map embedded in persona (should be a skill) |
| Sentinel | relay-verification SKILL.md | Yes | YES | Missing: no pre-check for test user privilege levels |
| Stylist | canvas-app-design-reading SKILL.md | Yes | Yes | None observed |
| Analyst | (no assigned skill) | Yes | YES | **MISSING: no skill assigned** |

**Summary**: /fleet works in Copilot CLI if you use the prompt templates in CLAUDE.md exactly. In VS Code it is sequential. The bigger issue is 3 agents (Auditor, Analyst, Vault) have no dedicated skill to pull from — they're working from persona knowledge alone.

---

## 2. Enhancement Plan — Grouped by Investment Level

---

### TIER 1: Fix broken things (do these first — they cost every project)

These are defects that will repro on EVERY future project regardless of domain.

#### E-01: Warden script template — PS 5.x safety
**From**: IMP-01, IMP-02, IMP-03, IMP-04
**Target file**: `agents/warden.agent.md`
**Change**: Add a PowerShell Script Generation Rules section (IMP-01 already started this). Extend it to cover:
- Mandatory `Make-Headers` function with `If-Match: *` for PATCH/DELETE
- `Assert-ExceptionContains` pattern reading `$_.ErrorDetails.Message` first
- Full PS 5.x forbidden operators list
- Template function stubs embedded directly in warden.agent.md

**Effort**: S — text edits to one agent file + skills
**Priority**: CRITICAL — broke every test run on first execution

---

#### E-02: Vault — register-plugins.ps1 template must be complete
**From**: IMP-05, IMP-07, IMP-09 (F-06 through F-11)
**Target file**: `agents/vault.agent.md` + new skill `skills/dataverse-plugin-deployment-cycle/SKILL.md`
**Change**:
- Pre-images: always POST `sdkmessageprocessingstepimages` regardless of step existence
- Always set `filteringattributes` on Update steps
- After any pre-image registration: PATCH step statecode=1 → wait 2s → PATCH statecode=0
- Template must: POST assembly → POST plugintypes → POST steps → POST pre-images → cache flush
- Bind both `sdkmessageid@odata.bind` AND `sdkmessagefilterid@odata.bind` on step creation
- Always send `Prefer: return=representation` or follow up with GET to get created step ID

**Effort**: M — needs new SKILL.md + vault persona update
**Priority**: HIGH — plugin tests failed every run until manually patched

---

#### E-03: Vault — role privileges must be assigned inline, not deferred
**From**: IMP-08, IMP-09
**Target file**: `agents/vault.agent.md`
**Change**: After creating each security role, immediately call `AddPrivilegesRole` with the privilege matrix from `security-design.md`. If downgrading is needed: `RemovePrivilegeRole` first, then `AddPrivilegesRole`. Do NOT leave roles as shells.

**Effort**: S — text edit to vault.agent.md
**Priority**: HIGH — security roles with no privileges make all security tests meaningless

---

#### E-04: Sentinel — pre-Phase 6 environment validation
**From**: IMP-12, IMP-13, IMP-14, IMP-15
**Target file**: `agents/sentinel.agent.md`
**Change**: Add a Phase 6 Pre-Check section that runs BEFORE any test:
1. Call `RetrieveUserPrivileges` on each test user → fail if any has `prvAllTables` at Global (= SysAdmin)
2. Verify each test fixture record is owned by the CORRECT user (employee record owned by employee userId, etc.)
3. Detect if environment is flat single-BU → warn which tests will be architecture-blocked
4. Document which test IDs require multi-BU or Access Teams (add `[ARCH-REQUIRED]` tag in script)

**Effort**: M — sentinel persona update + security-tests template update
**Priority**: CRITICAL — SysAdmin bypass invalidated 3 sessions of testing

---

#### E-05: Forge script parse validation before saving
**From**: runtime-assessment-report §5 (F-01)
**Target file**: `agents/forge.agent.md`
**Change**: After writing ANY PowerShell script, validate it with:
```powershell
$null = [System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$null, [ref]$errors)
if ($errors.Count -gt 0) { Write-Error "Parse errors found — do not commit" }
```
This check must run before Forge returns to Conductor. If parse errors found, fix inline before handoff.

**Effort**: S — text edit to forge.agent.md
**Priority**: HIGH — stray `'@` terminated one full session

---

### TIER 2: Add missing infrastructure (these unlock full automation)

#### E-06: New skill — `dataverse-plugin-deployment-cycle`
**From**: IMP-24
**Target**: NEW `skills/dataverse-plugin-deployment-cycle/SKILL.md`
**Content**:
- Full deployment cycle diagram: compile → upload DLL → POST types → POST steps → POST pre-images → cache flush → verify via plugintracelogs
- Exact Web API calls with correct fields (no `ishidden` in PATCH body — IMP-19)
- Plugin trace log endpoint: `plugintracelogs` (plural) — NOT `plugintracelog`
- Strong-name key generation pattern (RSACryptoServiceProvider 1024 → ExportCspBlob)
- Cache flush: statecode=1 → 2s wait → statecode=0 on each step
- Pre-image registration with `messagepropertyname=Target`
- Error code reference: 0x8004416c = unsigned assembly, 0x80040200 = missing sdkmessageid bind, 0x80040203 = missing messagepropertyname

**Effort**: M — write new SKILL.md (~150 lines)
**Priority**: HIGH — Vault and Forge both need this

---

#### E-07: New skill — `dataverse-privilege-depth-patterns`
**From**: IMP-23, IMP-25
**Target**: NEW `skills/dataverse-privilege-depth-patterns/SKILL.md`
**Content**:
- Privilege depth cheat sheet (User/BU/Parent BU/Org) vs ownership type table
- Critical: "Basic (User) depth in flat single-BU = effectively Org scope for list queries"
- AddPrivilegesRole vs RemovePrivilegeRole vs ReplacePrivilegesRole (which does what)
- RetrieveUserPrivileges action — how to call, what to look for
- Access Teams vs Owner Teams — when each is appropriate
- Multi-BU environment checklist: when does a project REQUIRE child BUs?
- OData disassociate URL format: `DELETE /systemusers(id)/systemuserroles_association(roleId)/$ref`

**Effort**: M — write new SKILL.md (~120 lines)
**Priority**: HIGH — multiple agents wasted sessions on privilege trial-and-error

---

#### E-08: Update `power-platform-security-patterns` with flat-BU section
**From**: IMP-14, IMP-25
**Target**: `skills/power-platform-security-patterns/SKILL.md`
**Change**: Add new section "Business Unit Topology and Row Isolation" covering:
- Single BU = no row-level isolation via privilege scope
- When to require multi-BU (any requirement: "user X cannot see user Y's records")
- Warden must flag any plan that relies on User-scope isolation in a flat-BU environment as CRITICAL
- Add to Warden's Phase 3 checklist: "Is the BU topology documented in security-design.md?"

**Effort**: S — add ~40 lines to existing SKILL.md
**Priority**: HIGH

---

#### E-09: Add missing skills for Auditor and Analyst
**From**: Agent assessment above
**Target**: NEW `skills/relay-auditing/SKILL.md` + NEW `skills/relay-analysis/SKILL.md`
- `relay-auditing`: What Auditor checks (20-point completeness checklist from LRS run), how to write issues with severity, how to write the approval decision
- `relay-analysis`: What Analyst maps when examining existing solutions, how to document component inventory, how to flag gaps vs plan

**Effort**: M each
**Priority**: MEDIUM — agents work without skills but produce better output with them

---

#### E-10: Vault — dedicated dataverse schema SKILL.md
**From**: runtime-assessment-report V-02 through V-08
**Target**: NEW `skills/dataverse-schema-api/SKILL.md`
**Content**:
- GlobalOptionSetDefinitions: use key access, not `$filter` — `GlobalOptionSetDefinitions(Name='lrs_status')`
- RelationshipDefinitions: same — key access by SchemaName
- Inline vs bound option set creation (bound only — never inline for global choices)
- Relationship POST body: do NOT include response-only fields (`ReferencedAttribute`, `ReferencingAttribute`)
- PublishAllXml retry loop pattern (race condition = retry with backoff)
- Calculated column limitation: Power Fx formula columns cannot be created via Web API — mark as manual

**Effort**: M
**Priority**: HIGH — V-02 through V-06 repro on every new project

---

### TIER 3: Orchestration and gates

#### E-11: Auto-flip approval flags in plan-index.json
**From**: runtime-assessment-report P3-01, V-09, V6-03
**Target**: Each agent persona (Auditor, Warden, Critic, Vault, Sentinel)
**Change**: Each agent's Output Contract section must specify the EXACT `plan-index.json` write it performs on completion, including the key path and value. Example for Auditor:
```json
{ "phase_gates.phase3_review.auditor_approved": true,
  "phase_gates.phase3_review.validated_at": "<ISO timestamp>",
  "phase_gates.phase3_review.auditor_issues_found": <count> }
```
This is already in CLAUDE.md's "Structured Contracts" section but not enforced in the individual agent files. The agent files need the specific write contract, not just the general principle.

**Effort**: S per agent (5 agents × S = M total)
**Priority**: HIGH — every gate requires manual Conductor intervention currently

---

#### E-12: Phase 5 gate must verify content not just booleans
**From**: runtime-assessment-report G5-01
**Target**: `scripts/relay-gate-check.py`
**Change**: Phase 5 gate should check:
- `src/plugins/` contains at least one `.dll` (not just `.cs`)
- `src/flows/` contains at least one `.json` with `triggers` key (Dataverse-shaped, not ARM)
- `scripts/` contains `register-plugins.ps1` AND `seed-test-data.ps1` AND `get-test-tokens.ps1`
- If Canvas App in plan: `.relay/state.json.canvas_app_bootstrapped == true` must be set

**Effort**: M — Python script changes
**Priority**: HIGH

---

#### E-13: Conductor must block phase advance when gate fails
**From**: runtime-assessment-report C-08
**Target**: `CLAUDE.md` + `skills/relay-orchestration/SKILL.md`
**Change**: Add explicit instruction: Conductor MUST NOT update `state.json.phase` to the next phase until `relay-gate-check.py --phase N` exits 0. If the gate fails, Conductor routes back to the responsible agent for fixes. Add a "Gate Failed — what to do" section to the orchestration skill.

**Effort**: S — text change
**Priority**: MEDIUM

---

#### E-14: Seed data and token scripts must be Phase 4/5 outputs, not Phase 6 prerequisites
**From**: runtime-assessment-report V6-01, IMP-21
**Target**: `agents/forge.agent.md` + `CLAUDE.md` Phase 4 section
**Change**:
- Critic (Phase 4): When producing `security-tests.ps1`, MUST also produce a `scripts/seed-test-data.ps1` template with correct ownership assignments per persona (not just create records — assign ownership explicitly)
- Forge (Phase 5): MUST produce `scripts/get-test-tokens.ps1` and `scripts/reset-test-records.ps1`. The reset script MUST deactivate plugin steps before resetting Rejected→Pending records, then reactivate.
- Sentinel (Phase 6): Expects these scripts to exist; runs `seed-test-data.ps1` first if fixtures file is absent

**Effort**: M — changes to Critic + Forge + Sentinel personas
**Priority**: HIGH — Phase 6 was completely blocked without these

---

### TIER 4: Quality of life and documentation

#### E-15: Forge — emit correct Dataverse-shaped flow JSON
**From**: runtime-assessment-report C-11
**Target**: `agents/forge.agent.md`
**Change**: Explicitly state that flow JSON must be Dataverse-shaped (clientData format), not Logic Apps ARM format. Cross-reference `skills/power-platform-alm/SKILL.md` activation pattern. Add the `clientdata` PATCH endpoint and pattern inline in the automation capability map. Forge must never produce ARM-shaped flow JSON.

**Effort**: S
**Priority**: HIGH

---

#### E-16: Phase 0 prerequisite check — detect missing MCPs before Phase 5
**From**: runtime-assessment-report 8.8 (HIGH priority)
**Target**: `scripts/relay-prerequisite-check.py` (already exists) + `CLAUDE.md` Phase 5 section
**Change**: Add MCP detection to the existing prerequisite script's Phase 5 pre-check:
- If Canvas App is in plan AND Canvas Authoring MCP not detected → WARN (canvas will not deploy automatically)
- If flows in plan AND no `pac solution` available → WARN (flows must be ARM-shaped fallback)
- Conductor should show this warning BEFORE invoking Forge, not after

**Effort**: S — add ~30 lines to existing prerequisite script
**Priority**: HIGH — discovered this AFTER Forge ran, not before

---

#### E-17: README + install.js — Windows compatibility
**From**: runtime-assessment-report C-01, C-05
**Target**: `scripts/install.js` + `README.md`
**Change**:
- `install.js`: Replace `which` with cross-platform `command -v` / `Get-Command` detection
- Python scripts: Force UTF-8 at top of each script (`sys.stdout.reconfigure(encoding='utf-8')`)
- README: Add Windows setup section with `$env:PYTHONUTF8 = "1"` and Azure CLI path

**Effort**: S
**Priority**: MEDIUM

---

#### E-18: /fleet is VS Code-unavailable — make this visible in commands
**From**: CLAUDE.md already states this, but no VS Code warning exists
**Target**: `skills/relay-parallel-agents/SKILL.md`
**Change**: Add a prominent section at the top:
```
## VS Code vs Copilot CLI
/fleet = Copilot CLI ONLY. In VS Code Agent Mode, Conductor runs agents sequentially.
Sequential output quality is IDENTICAL to fleet output quality.
The difference is only parallelism (speed), not quality.
```
This prevents users from asking "why isn't /fleet working" when in VS Code.

**Effort**: XS — 10 lines added to skill
**Priority**: LOW

---

### TIER 5: Stylist v2 — Canvas + MDA Design Pipeline (Model 5+4)

#### E-19: Stylist v2 — Designer + MCP Prompt Author + YAML Reviewer
**From**: LRS smoke test Canvas App design quality issues
**Decision**: Model 5+4 combined — Stylist writes the MCP prompt (Model 5) AND reviews the output YAML (Model 4). Stylist never accesses MCP directly. No tool grants change.

**Architecture (Phase 5 canvas pipeline):**
```
Step 3a: Stylist writes design-system.md
         → Merged document: tokens + screen layouts + MCP prompt sections + MDA specs
         → Includes Mermaid layout diagrams for user validation
Step 3b: User confirms layout (Conductor shows Mermaid diagrams)
Step 3c: Forge calls /generate-canvas-app with Stylist's prompt sections
Step 3d: Forge calls /edit-canvas-app for data bindings (DO NOT MODIFY visual props)
Step 3e: Forge calls /edit-canvas-app for navigation logic
Step 3f: Forge calls /edit-canvas-app for validation + error handling
Step 3g: Forge writes plan-index.json: "canvas_edits_complete": true
Step 3h: Stylist reads src/canvas-apps/*.pa.yaml → writes docs/design-review.md
Step 3i: Forge applies critical+major fixes from design-review.md
```

**Target files and changes:**

**`agents/stylist.agent.md` — Major rewrite:**

*Design Mode (before Forge):*
- Merged design-system.md: one file contains BOTH tokens and MCP prompt sections (Solution #1: no contradiction possible)
- App Configuration section: dimensions, orientation, modern controls ON
- Screen Inventory: list all screens from plan with purpose
- Per-screen structured MCP prompt sections using three-layer assembly (Solution #7):
  - Layer 1: Layout template from `canvas-app-screen-layout` skill (zones + dimensions)
  - Layer 2: Design tokens from the same document (colors, fonts, spacing)
  - Layer 3: Plan content (table names, columns, status values, persona views)
- Mermaid layout diagrams per screen for user preview (Solution #2)
- MDA Design section: theme colors (4 tokens), sitemap structure, form tab/section/field layout
- Mandatory modern control variant table: `Button (modern)`, `Gallery (modern)`, `TextInput (modern)` — never classic

*Review Mode (after Forge):*
- Reads `src/canvas-apps/*.pa.yaml` — it is readable text, no MCP needed
- Structural pass: count screens, count controls, verify modern vs classic control types (Solution #3)
- Token pass: search for each RGBA value across entire YAML — property-agnostic (Solution #3)
- Overflow check: `X + Width > App.Width` or `Y + Height > App.Height` on each control
- Severity-tagged findings: CRITICAL / MAJOR / MINOR (Solution #4)
- Sanity check: "Did I find >0 controls with color values? If 0, YAML format may have changed" (Solution #3)
- Output: `docs/design-review.md` with per-screen pass/fail + specific fix instructions
- One review pass only — no infinite loops. Forge fixes critical+major. Minor items go to user. (Solution #4)

*MDA Design (design-system.md sections):*
- Theme: NavBar, Primary, Accent, Header colors — must match Canvas App palette
- Sitemap: Area/Group/Subarea structure with entity names and default views
- Form layout: tab names, section names (with column count), field placement order per section
- Header fields specification
- No review loop for MDA — platform controls rendering, structure either matches spec or doesn't

**`agents/forge.agent.md` — Targeted updates:**
- Canvas MCP prompt extraction: "Read design-system.md MCP prompt sections. Substitute token names with actual RGBA values. Pass to /generate-canvas-app verbatim."
- DO NOT MODIFY visual properties rule (Solution #5):
  ```
  When calling /edit-canvas-app for logic wiring, include this constraint:
  "DO NOT MODIFY: X, Y, Width, Height, Fill, Color, Font, Size, FontWeight,
   RadiusTopLeft, RadiusTopRight, RadiusBottomLeft, RadiusBottomRight,
   BorderColor, BorderThickness, PaddingTop/Bottom/Left/Right.
   ONLY modify: Items, OnSelect, Text (formulas), Value, Default,
   Visible, DisplayMode, Navigate(), Tooltip, Reset, IfError"
  ```
- Canvas edit completion signal: write `plan-index.json.phase5_build.canvas_edits_complete = true` after ALL edit passes, BEFORE Stylist review (Solution #6)
- MDA: "Read design-system.md MDA section for sitemap structure and form tab/section/field layout before building sitemap XML or form XML"

**`skills/canvas-app-screen-layout/SKILL.md` — NEW:**
- 6 layout archetypes with exact zone dimensions:

| Pattern | Nav position | Best for | Dimensions |
|---|---|---|---|
| Dashboard | Top header only | KPI monitoring, overview | Landscape 1366+ |
| Master-detail | Left list panel (400px) + right detail | Record browsing, case management | Landscape 1366+ |
| Form-focused | Top header + wizard steps | Data entry, submissions | Either |
| Mobile-first | Bottom tab bar (60px) | Field workers, quick approvals | Portrait phone |
| Pill nav enterprise | Left pill (70px) | Internal admin tools | Landscape 1366+ |
| Tab navigation | Top tab strip (48px) | Multi-section categorized apps | Either |

- Each pattern includes: ASCII zone diagram, zone dimensions, responsive formula patterns (`Parent.Width - NavWidth - Padding`)
- Standard improvements checklist (empty gallery state, loading indicator, status badges, error states)

**`skills/canvas-app-design-patterns/SKILL.md` — Update:**
- Add Modern control variant table (which modern control replaces which classic)
- Add Canvas theme JSON structure (Fluent token → RGBA mapping)

**`skills/canvas-app-enterprise-layout/SKILL.md` — Update:**
- Add exact pixel dimensions for each zone
- Add responsive width formulas

**`skills/canvas-mcp-prompt-patterns/SKILL.md` — NEW (grows over time):**
- Initially empty "prompt library" — populated after each real project
- Structure: input prompt → what MCP produced → quality rating → lessons learned
- Stylist references this when writing new prompts to avoid known bad patterns

**`CLAUDE.md` Phase 5 section — Update:**
- Replace current Phase 5 canvas step with the 3a-3i pipeline above
- Add: Conductor gates Step 3h on `canvas_edits_complete == true`
- Add: After Stylist Review, Forge fixes critical+major only. Conductor shows minor items to user.
- Add: Forge reads design-system.md MDA section before building sitemap/forms

**Effort**: L — Stylist agent rewrite + 2 new skills + updates to Forge, CLAUDE.md, and 2 existing skills
**Priority**: HIGH — Canvas App design quality was the most visible user-facing defect

**Risks and mitigations (all addressed in the design):**
| Risk | Mitigation | Solution # |
|---|---|---|
| Token contradiction between sections | Single merged document — one source of truth | 1 |
| MCP prompt quality unpredictable | Mermaid preview + structured prompt template + prompt library skill | 2, 7 |
| YAML schema changes across MCP versions | Property-agnostic token search + sanity check | 3 |
| Infinite review→fix loop | Severity triage + one-pass cap | 4 |
| Forge overwrites visual properties | Explicit DO NOT MODIFY list in edit prompts | 5 |
| Review timing wrong | Gate on canvas_edits_complete flag | 6 |
| Prompt is single point of failure | Three-layer assembly from template + tokens + plan | 7 |

---

#### E-20: README — updated workflow, Phase 5 pipeline, Stylist v2 role
**From**: All design discussions
**Target**: `README.md`
**Change**:
- Update agent roster table: Stylist description → "Canvas App UI Designer + Design Reviewer. Produces design-system.md (tokens + MCP prompts + MDA specs) and reviews Canvas App .pa.yaml output."
- Update Phase 5 workflow diagram: show the 3a-3i canvas pipeline
- Add "Design Quality" section explaining Model 5+4: Stylist designs → Forge builds → Stylist reviews → Forge fixes
- Update Stylist's write restrictions in the agent table: `docs/design-system.md`, `docs/design-review.md`
- Add MDA design section: explain Stylist provides theme + sitemap + form layout specs
- Update the "What Relay automates" table: add Canvas App design quality row
- Update version history: v0.5.0 entry

**Effort**: M — README is the public face
**Priority**: HIGH — users need to understand the new flow

---

## 3. Prioritised Delivery Sequence

### Sprint 1 — Broken things first (2-3 sessions)
| ID | What | Files touched |
|---|---|---|
| E-01 | Warden PS 5.x template | agents/warden.agent.md |
| E-02 | Vault register-plugins template | agents/vault.agent.md + new skill |
| E-03 | Vault role privileges inline | agents/vault.agent.md |
| E-04 | Sentinel pre-Phase 6 check | agents/sentinel.agent.md |
| E-05 | Forge parse validation | agents/forge.agent.md |

### Sprint 2 — Stylist v2 + knowledge gaps (2-3 sessions)
| ID | What | Files touched |
|---|---|---|
| E-19 | **Stylist v2: design + MCP prompt + YAML review + MDA** | agents/stylist.agent.md (rewrite), agents/forge.agent.md, CLAUDE.md, skills/canvas-app-screen-layout/SKILL.md (NEW), skills/canvas-mcp-prompt-patterns/SKILL.md (NEW), skills/canvas-app-design-patterns/SKILL.md, skills/canvas-app-enterprise-layout/SKILL.md |
| E-06 | New skill: plugin deployment cycle | skills/dataverse-plugin-deployment-cycle/SKILL.md |
| E-07 | New skill: privilege depth patterns | skills/dataverse-privilege-depth-patterns/SKILL.md |
| E-08 | Update security-patterns skill | skills/power-platform-security-patterns/SKILL.md |
| E-10 | New skill: dataverse schema API | skills/dataverse-schema-api/SKILL.md |

### Sprint 3 — Orchestration correctness (1-2 sessions)
| ID | What | Files touched |
|---|---|---|
| E-11 | Auto-flip approval flags | 5 agent files |
| E-12 | Phase 5 gate content check | scripts/relay-gate-check.py |
| E-13 | Block phase advance on gate fail | CLAUDE.md + relay-orchestration SKILL |
| E-14 | Seed/token scripts in Phase 4/5 | agents/critic.agent.md + forge.agent.md + sentinel.agent.md |

### Sprint 4 — Polish + documentation (1 session)
| ID | What | Files touched |
|---|---|---|
| E-09 | New skills: Auditor + Analyst | 2 new SKILL.md files |
| E-15 | Forge: Dataverse-shaped flow JSON | agents/forge.agent.md |
| E-16 | Phase 0 MCP detection | scripts/relay-prerequisite-check.py |
| E-17 | Windows compatibility | scripts/install.js + README.md |
| E-18 | /fleet VS Code caveat | skills/relay-parallel-agents/SKILL.md |
| E-20 | **README: workflow, Phase 5 pipeline, Stylist v2** | README.md |

---

## 4. Metrics to track v0.5.0 success

After implementing v0.5.0, re-run the LRS smoke test with the same environment. Targets:

| Metric | v0.4.0 actual | v0.5.0 target |
|---|---|---|
| Security test score (raw) | 15/25 | 19/25 (architecture-limited) |
| Phase 6 first-run failures from PS script errors | 17/25 | 0/25 |
| Manual interventions between Phase 5 start and Phase 6 complete | ~40 | <5 |
| Sessions to complete smoke test end-to-end | 6+ sessions | 2 sessions |
| Agents that produce complete, deployable artifacts first try | 1/5 (Vault partial) | 4/5 |
| Canvas App design quality — first-pass controls outside canvas | Many | 0 (spec defines dimensions) |
| Canvas App design quality — wrong colors on first pass | Most controls | <10% of controls (token substitution) |
| Canvas App uses modern controls | No (classic default) | Yes (mandated in design-system.md) |
| MDA theme matches Canvas App palette | No (platform default) | Yes (Stylist specifies both) |
| Design review loop iterations | N/A | 1 (capped by design) |

---

## 5. /fleet Deep Dive — What Works and What Doesn't

### What /fleet actually is
`/fleet` is a Copilot CLI native feature that dispatches multiple subagents in parallel within a single CLI session. It is NOT a Relay invention — Relay just provides the prompt templates for each phase.

### In VS Code Agent Mode (current session environment)
- /fleet is NOT available
- Conductor runs agents sequentially using the same persona rules
- Output quality is identical — only speed differs
- No action needed; this is expected behavior per CLAUDE.md

### In Copilot CLI (the correct environment for /fleet)
Testing /fleet requires:
1. Copilot CLI installed and logged in
2. All 4 Power Platform MCP servers attached
3. A project with `.relay/state.json` in the cwd
4. The 6 fleet prompt templates from CLAUDE.md

**Known gap**: Subagents in /fleet do NOT inherit chat history — every fleet prompt must be self-contained with file paths. The current fleet prompt templates in CLAUDE.md do reference files correctly. However:
- Phase 5b fleet dispatches 3 Forge agents for Canvas/MDA/Flows — but Forge agents may still conflict on `plan-index.json` writes (no locking)
- Phase 6 fleet dispatches Sentinel + Warden simultaneously — both write to `plan-index.json.phase6_verify` but to different keys, so no conflict

**Recommended E-18 addition**: Add file-write coordination note to `skills/relay-parallel-agents/SKILL.md` — parallel agents must write to distinct keys in plan-index.json.

---

## 6. Complete File Change Manifest

Every file touched by v0.5.0, grouped by type:

### Agent files (6)
| File | Enhancements | Sprint |
|---|---|---|
| `agents/warden.agent.md` | E-01 (PS 5.x rules), E-11 (approval flags) | 1, 3 |
| `agents/vault.agent.md` | E-02 (plugin template), E-03 (role privileges), E-11 | 1, 3 |
| `agents/sentinel.agent.md` | E-04 (pre-Phase 6 check), E-11, E-14 | 1, 3 |
| `agents/forge.agent.md` | E-05 (parse validation), E-14, E-15 (flow JSON), E-19 (DO NOT MODIFY rule + MDA read) | 1, 3, 4, 2 |
| `agents/stylist.agent.md` | **E-19 (v2 rewrite: Design + MCP prompt + YAML review + MDA)** | 2 |
| `agents/critic.agent.md` | E-14 (seed data template) | 3 |

### Skills — NEW (6)
| File | Enhancement | Sprint |
|---|---|---|
| `skills/dataverse-plugin-deployment-cycle/SKILL.md` | E-06 | 2 |
| `skills/dataverse-privilege-depth-patterns/SKILL.md` | E-07 | 2 |
| `skills/dataverse-schema-api/SKILL.md` | E-10 | 2 |
| `skills/relay-auditing/SKILL.md` | E-09 | 4 |
| `skills/relay-analysis/SKILL.md` | E-09 | 4 |
| `skills/canvas-app-screen-layout/SKILL.md` | E-19 (6 layout archetypes) | 2 |
| `skills/canvas-mcp-prompt-patterns/SKILL.md` | E-19 (prompt library — grows over time) | 2 |

### Skills — UPDATED (3)
| File | Enhancement | Sprint |
|---|---|---|
| `skills/power-platform-security-patterns/SKILL.md` | E-08 (flat-BU section) | 2 |
| `skills/canvas-app-design-patterns/SKILL.md` | E-19 (modern controls table + theme JSON) | 2 |
| `skills/canvas-app-enterprise-layout/SKILL.md` | E-19 (exact pixel dimensions + responsive formulas) | 2 |
| `skills/relay-parallel-agents/SKILL.md` | E-18 (/fleet VS Code caveat) | 4 |

### Orchestration files (2)
| File | Enhancement | Sprint |
|---|---|---|
| `CLAUDE.md` | E-13 (gate blocking), E-19 (Phase 5 canvas pipeline 3a-3i) | 2, 3 |
| `skills/relay-orchestration/SKILL.md` | E-13 (gate failed section) | 3 |

### Scripts (2)
| File | Enhancement | Sprint |
|---|---|---|
| `scripts/relay-gate-check.py` | E-12 (content check, not just booleans) | 3 |
| `scripts/relay-prerequisite-check.py` | E-16 (MCP detection) | 4 |

### Public-facing (2)
| File | Enhancement | Sprint |
|---|---|---|
| `README.md` | E-17 (Windows compat), **E-20 (workflow + Phase 5 pipeline + Stylist v2 + MDA design)** | 4 |
| `scripts/install.js` | E-17 (cross-platform detection) | 4 |

### Version history update
| File | Change | Sprint |
|---|---|---|
| `AGENTS.md` | Add v0.5.0 entry: "Stylist v2 (design + review); 7 new skills; Warden PS 5.x rules; Sentinel pre-check; Phase 5 canvas pipeline" | 4 |

**Total: 20 enhancements across 20 files (6 agent, 7 new skills, 4 updated skills, 2 orchestration, 2 scripts, 2 public-facing, 1 version history)**

---

*Plan version: 2.0 — 2026-05-01*
*Based on: relay-improvement-backlog.md (25 items) + runtime-assessment-report.md (Sections 1-13)*
*Design model: Model 5+4 combined (Stylist writes MCP prompt + reviews YAML)*
*Decisions locked: Canvas pipeline 3a-3i, MDA in design-system.md, one-pass review cap, DO NOT MODIFY visual props rule*
