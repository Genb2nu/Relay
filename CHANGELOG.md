# Changelog

All notable changes to Relay are documented here.

---

## [0.7.0] — 2026-05-XX

### Workflow
- Phase 2b wireframes are reinforced as a mandatory planning substep before Phase 3 review
- Phase 2 now carries an explicit `build_ready_for_vault` contract so ambiguous schema plans are blocked before review/lock
- Phase 5 workflow now explicitly continues from Vault + Stylist into all applicable Forge specialists
- Phase 5 completion contract now tracks specialist completion flags and solution component linkage

### Build Reliability
- Vault guidance now requires `MSCRM.SolutionUniqueName` on Dataverse metadata calls so created components are linked to the custom solution
- Vault guidance now requires canonical `src/dataverse/` fallback scripts and Conductor persistence/run fallback when direct execution is unavailable
- Vault script path resolution now correctly walks from `src/dataverse/` back to the workspace root before reading `.relay/state.json`
- Dataverse schema guidance now documents the working Web API payload patterns surfaced by smoke testing
- Vault guidance now requires Web API table creation to use `PrimaryNameAttribute` plus `Attributes[]` instead of the unsupported nested `PrimaryAttribute` payload
- Vault guidance now preserves publisher-prefixed schema names (for example `a2a_Request`) instead of collapsing them into invalid `a2aRequest` forms
- Vault guidance now omits unsupported `DefaultValue` from integer column creation payloads
- Vault guidance now explicitly requires solution-component count verification and no longer leaves stale unbound AddPrivilegesRole / RemovePrivilegeRole route examples
- Vault guidance now avoids generating a second parental relationship when optional session lookups coexist with an existing request parent
- Vault hook permissions now allow `src/dataverse/` artifacts and Relay build state updates
- Forge plugin handoff now requires strong-name signing and no longer recommends bare `pac plugin push` for first-time registration on PAC builds that require `--pluginId`
- Forge-MDA now treats `scripts/apply-mda-sitemap.ps1` as a real deployer contract and no longer allows undeployable placeholder form DSL to count as completed MDA output
- Forge-MDA now requires theme deployment/verification when `src/mda/theme.json` is emitted and records view-default fidelity as part of completed MDA output

### Agent Coordination
- Scout, Drafter, Critic, and Stylist write permissions/state contracts were aligned with the artifacts they are required to produce
- Blocked handoffs now explicitly preserve the recovery sequence, failed attempts, and exact next-step evidence instead of dropping context
- Forge-Canvas now treats Checklist A and the coauthoring/app bootstrap prompt as a hard first step
- Critic can update adversarial gate state in `.relay/plan-index.json`
- Forge-Canvas checklist now requires solution-scoped app creation, first save, maker-account confirmation, popup dismissal, and stable Data pane setup before MCP attachment
- Stylist wireframe guidance now asks for presentation-friendly HTML previews and review-mode explicitly treats label wrap/clipping/repeated control sizing as MAJOR findings
- Sentinel Phase 6 guidance now requires per-surface maker login verification and Power Pages / Power Automate browser preflight before final verification proceeds
- Copilot CLI `/fleet` prompts in CLAUDE.md now dispatch the specialist Forge agents instead of stale generic Forge prompts for Canvas, MDA, and flow work

### Skills
- Added `relay-recovery-playbook` with proven recovery sequences for Power Pages provisioning failures, missing Power Pages triggers, and MDA deployment reapply loops
- `playwright-testing` now includes maker-surface preflight guidance and a reusable transient-blocker clearing pattern

### Validation
- `tests/test-hooks.sh` now covers Scout state writes, Drafter plan-index writes, Critic plan-index writes, and Vault dataverse artifact writes
- `tests/test-gates.py` now covers the Phase 2 build-readiness gate alongside the existing Phase 1/5 checks
- Phase 1 gate now requires `docs/requirements.md`, not just discovery counts in `.relay/plan-index.json`
- Phase 2 consistency validation now checks for Vault build-readiness markers such as ownership, primary name attributes, choice strategy, autonumber formats, runbook coverage, and flow concurrency
- Phase 5 gate now requires actual Canvas App and Model-Driven App source artifacts before specialist completion flags can pass

### Release
- Release metadata bumped to 0.7.0

---

## [0.6.4] — 2026-05-XX

### Reliability
- `.gitattributes` enforces LF for shell, Python, markdown, and JSON files
- Shell scripts are normalized for Git Bash / Windows compatibility
- Scout reads `.relay/context-summary.md` before asking users to restate the brief
- `/relay:start` supports resume, reset, and cancel when `.relay/state.json` already exists
- Scout explicitly treats `docs/requirements.md` as an authorized Relay discovery artifact
- Conductor writes `docs/requirements.md` from Scout output when needed and logs the fallback in `.relay/execution-log.jsonl`

### Validation
- `tests/test-hooks.sh` now covers Scout writing `docs/requirements.md`

### Release
- Release metadata bumped to 0.6.4

---

## [0.6.3] — 2026-05-XX

### Planning
- Stylist Mode C added: HTML wireframe generation as a Phase 2 planning substep
- Phase 2 now requires wireframe approval before Phase 3 review can begin

### Review
- Auditor and Warden now explicitly review docs/wireframes.html alongside the plan and security design
- Consistency validation now checks wireframes_complete against actual wireframe file existence

### Release
- Release metadata bumped to 0.6.3

---

## [0.6.2] — 2026-05-XX

### Docs
- Generic plugin guidance now uses neutral placeholders for app names, entity names, roles, prefixes, and environment examples
- Agent, skill, and command examples were normalized to avoid project-specific naming residue in reusable plugin content

### Release
- Release metadata bumped to 0.6.2

---

## [0.6.1] — 2026-05-XX

### Critical Fixes
- pre-tool-use.sh: added forge-canvas, forge-mda, forge-flow, and forge-pages with scoped artifact writes plus `.relay/plan-index.json` and `.relay/execution-log.jsonl`
- Phase 5 state contract migrated from `forge_complete` to specialist completion fields across the scaffold, template, and gate validator
- Phase 5 component inventory now includes `power_pages`
- drafter.agent.md now writes `power_pages` into the plan manifest so Phase 5 can require `power_pages_complete`

### Validation
- tests/test-hooks.sh: added specialist hook cases for forge-canvas, forge-mda, forge-flow, and forge-pages
- Python status output now uses ASCII markers across gate, drift, consistency, score, and prerequisite scripts for Windows-safe console output

### Docs
- README automation table now marks Power Automate flow output as a temporary build-guide path
- AGENTS.md specialist write permissions now match the enforced hook behavior
- Release metadata bumped to 0.6.1

---

## [0.6.0] — 2026-05-XX

### Architecture
- Forge split into four specialists: forge-canvas, forge-mda, forge-flow, forge-pages
- CLAUDE.md Phase 5 updated with specialist dispatch
- All squad/build documentation updated to reflect split
- Note: forge-flow produces build guides (temporary) — automated flow import planned for v0.6.x

### Features
- /relay:learn: extracts patterns from completed project logs and proposes skill additions
- /relay:doctor: fully executable implementation with --fix flag

### Developer Experience
- CHANGELOG.md added

---

## [0.5.2] — 2026-05-02

### Security
- pre-tool-use.sh: deny-by-default when CLAUDE_AGENT unset or unknown
- pre-tool-use.sh: Stylist and Analyst explicit enforcement cases added
- pre-tool-use.sh: write checks use normalized full paths, not basenames
- relay-drift-check.py: command injection fixed (shell=False, list args)
- phase-gate-hook.sh: expanded to pac solution import, activation scripts

### Consistency
- marketplace.json synced to 0.5.2
- CLAUDE.md /fleet deduplicated to one canonical block
- relay-start.md reduced to pointer — start.md is canonical
- schemas/state.schema.json: new state.json schema
- relay-gate-check.py Phase 0 validates state.json against schema
- Phase names standardised: discovery, planning, review, adversarial, build, verify, complete

### Code Quality
- All 5 Python scripts: safe JSON loading, atomic file writes, meaningful error exits
- relay-prerequisite-check.py: bash/jq/pwsh added, unreachable exit 2 removed
- tests/test-hooks.sh: 5 regression test cases
- README.md + doctor.md: bash/jq/pwsh documented as prerequisites

---

## [0.5.1] — 2026-05-01

### CLI Fixes (from smoke test)
- 400-line chunk budget rule for Drafter, Vault, Forge
- Drafter: removed template file lookup
- Canvas App: Canvas Authoring MCP only — pac canvas pack deprecated
- Phase 5 pre-deploy auth validation gate
- stop_powershell does not kill agents — documented
- Scout batches all gap questions in one turn
- Flows: markdown build guide (Option B)
- Vault: PS 5.1 strict compatibility
- Vault: idempotent role creation (name + root BU filter)
- /relay:start: accepts phase=context_loaded from /relay:load
- Output directories pre-created before subagent launches
- MDA sitemap packaged into solution ZIP
- AddSolutionComponent type constants table
- Vault: FLS service principal membership

---

## [0.5.0] — 2026-04-24

### Enhancements (20 items from codebase review)
- Warden PS 5.1 security test template
- Vault 7-step plugin deploy cycle
- Vault inline privilege depth assignment
- Sentinel Phase 6 pre-check (SysAdmin detection, flat-BU)
- Forge mandatory PS parse validation
- Stylist v2: Mode A + Mode B pipeline
- 5 new skills added
- security-patterns flat-BU section
- Output contracts for all agents
- Gate content checks
- Hard Rule #8 in CLAUDE.md
- Forge test infrastructure scripts
- Forge flow JSON Dataverse clientData format
- relay-auditing + relay-analysis skills
- MCP detection in install.js
- Windows where vs which compatibility

---

## [0.4.0] — 2026-04-25

- Playwright E2E testing via power-platform-playwright-toolkit
- Sentinel generates TypeScript tests from user stories
- /fleet prompts for Copilot CLI (all phases)
- Phase 5 inline component verification
- Forge Checklist G+H for Playwright auth

---

## [0.3.2] — 2026-04-24

- Scout: publisher prefix captured as first question
- plan-index.json created as first action in start.md
- state.json phase updated by agents
- Vault ownership check before privilege depth
- Vault env var existence check
- Forge PowerShell ${VarName}: pattern
- Forge proactive checklists A-F
- /relay:load Vision disabled warning
- Footgun #25 multi-flow aggregate race
- Checklist A data sources warning
- Forge AccessibleLabel on YAML controls
- Sentinel all 5 App Checker categories
- Phase 5 component-by-component verification

---

## [0.3.1] — 2026-04-24

- Hook-enforced phase gates (Bash PreToolUse)
- Consistency check: plan-index.json vs docs
- Column-level drift detection
- Adversarial pilot guide (9 test cases)

---

## [0.3.0] — 2026-04-23

- plan-index.json structured contracts
- relay-gate-check.py phase gate validation
- execution-log.jsonl structured logging
- relay-drift-check.py drift detection
- Warden runtime security tests
- relay-score.py plan quality scoring

---

## [0.2.x] — 2026-04-23

- v0.2.0: Stylist + Analyst, 6 commands, Power Fx + design skills
- v0.2.1: Automation-first Forge, 23-item footgun checklist
- v0.2.2: 6 embedded workflow skills, removed Superpowers
- v0.2.3: All 4 Power Platform skills, connection reuse
- v0.2.4+0.2.5: Flow activation automated, project content cleaned

---

## [0.1] — Initial release

- 8 specialist agents, 7 slash commands, 4 embedded skills
- Phase gate enforcement via hooks
