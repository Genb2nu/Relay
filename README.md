# Relay — The Power Platform AI Squad

A plugin-native SDLC orchestration system for Microsoft Power Platform. Ten specialist AI agents collaborate through an enforced workflow with machine-validated quality gates, execution logging, drift detection, and runtime security testing.

Works on **Claude Code**, **GitHub Copilot CLI**, and **Copilot in VS Code**.

> **v0.6.0** — Forge specialist split · /relay:learn · /relay:doctor full implementation · CHANGELOG.md

---

## What It Does

You describe what you want to build. Relay runs a squad of specialists through a structured, enforced pipeline — from discovery to verified deployment.

| Agent | Codename | Role |
|---|---|---|
| Business Analyst | **Scout** | Socratic discovery — one question at a time |
| Technical Planner | **Drafter** | Full plan with schema, flows, apps, security design |
| Plan Reviewer | **Auditor** | Completeness review — loops with Drafter until approved |
| Security Architect | **Warden** | Security review + runtime API security tests post-build |
| Adversarial Reviewer | **Critic** | 23-item footgun checklist + red-team pass before lock |
| UI Designer | **Stylist** | Canvas App design system — RGBA tokens, typography, spacing |
| Solution Mapper | **Analyst** | Maps existing solutions before change requests or audits |
| Dataverse Engineer | **Vault** | Tables, columns, security roles, FLS profiles, plugins |
| Canvas App Developer | **Forge-Canvas** | Canvas App screens via Canvas Authoring MCP |
| MDA Developer | **Forge-MDA** | Model-Driven App sitemap, forms, views |
| Flow Developer | **Forge-Flow** | Power Automate flow build guides |
| Power Pages Developer | **Forge-Pages** | Power Pages portals via /create-site |
| Developer | **Forge** | Plugins, code apps, web resources, env vars |
| Tester | **Sentinel** | Functional verification + drift detection (plan vs actual build) |

**Workflow:** discovery → planning → review → adversarial → build → verify → complete

Every phase transition is gate-validated. The plan locks with SHA256 checksums after three independent reviewers approve. Security is tested at runtime, not just reviewed on paper.

---

## Prerequisites

- **Claude Code CLI** or **GitHub Copilot CLI** or **Copilot in VS Code**
- Node.js 22+
- Power Platform CLI (`pac`)
- Azure CLI (`az`)
- Python 3.8+ (for gate validation, drift detection, and scoring scripts)
- `bash` (required by hooks; on Windows use Git Bash or WSL)
- `jq` (required by hooks; on Windows: `winget install jqlang.jq`)
- PowerShell 7+ / `pwsh` (required by Relay scripts)

### Required: Microsoft Power Platform Skills

```bash
/plugin marketplace add microsoft/power-platform-skills
/plugin install canvas-apps@power-platform-skills
/plugin install model-apps@power-platform-skills
/plugin install power-pages@power-platform-skills
/plugin install code-apps-preview@power-platform-skills
```

| Plugin | Used by |
|---|---|
| `canvas-apps` | forge-canvas: `/configure-canvas-mcp`, `/generate-canvas-app`, `/edit-canvas-app` |
| `model-apps` | forge-mda: `/genpage` — custom React pages in Model-Driven Apps |
| `power-pages` | forge-pages: `/create-site` — Power Pages portals |
| `code-apps-preview` | forge: `/create-code-app`, `/add-dataverse`, `/add-office365`, `/deploy` |

> **No Superpowers needed.** All orchestration, discovery, planning, verification, and debugging skills are embedded in Relay.

> **Prerequisite check:** Run `python scripts/relay-prerequisite-check.py` before starting a project. This validates all CLI tools, including `bash`, `jq`, and `pwsh`, plus auth, MCP servers, plugins, and skills. Use `--fix` to attempt auto-remediation of missing components.

### Required: Dataverse MCP

**Option A — Microsoft cloud (recommended, no install)**

1. Power Platform Admin Center → Environment → Settings → Product → Features → enable **Allow MCP clients to interact with Dataverse MCP server**
2. Advanced Settings → enable **Microsoft GitHub Copilot** client
3. VS Code: `Ctrl+Shift+P` → `MCP: Add Server` → `HTTP or Server Sent Events`
4. Enter: `https://<your-org>.crm.dynamics.com/api/mcp`
   *(Find org URL: make.powerapps.com → Settings gear → Session details → Instance URL)*

**Option B — Local proxy**

```bash
dotnet tool install --global Microsoft.PowerPlatform.Dataverse.MCP
```
See [Dataverse MCP labs](https://github.com/microsoft/Dataverse-MCP) for full setup.

> Dataverse MCP tools are charged via Copilot Credits from Dec 15, 2025. Dynamics 365 Premium and M365 Copilot USL licences are exempt.

---

## Installation

### Claude Code
```
/plugin marketplace add Genb2nu/Relay
/plugin install relay@relay-marketplace
```

### GitHub Copilot CLI
```bash
copilot plugin marketplace add Genb2nu/Relay
copilot plugin install relay@relay-marketplace
```

### Copilot in VS Code
1. Enable `chat.plugins.enabled` in VS Code settings
2. `Ctrl+Shift+P` → `Chat: Install Plugin From Source` → `https://github.com/Genb2nu/Relay`

Or add to `settings.json`:
```json
"chat.plugins.marketplaces": ["https://github.com/Genb2nu/Relay"]
```

### Local development
```bash
git clone https://github.com/Genb2nu/Relay.git && cd Relay
claude --plugin-dir /path/to/Relay      # Claude Code
copilot --plugin-dir /path/to/Relay     # Copilot CLI
```

Run `tests/test-hooks.sh` to verify hook enforcement.

### After installing
```
/relay:doctor
```
Verifies all prerequisites: PAC CLI, Azure CLI, Python, Node.js, Git, Bash, jq, PowerShell 7+, Power Platform Skills plugins, Dataverse MCP, and shows your active PAC auth profile. Fix any ❌ items before starting a project.

---

## Quick Start

```
/relay:start
```

Provide a brief:

> Build a Leave Request Approval System. Employees submit requests via Canvas App. Managers approve via Model-Driven App. Super Admins have full oversight. Employees must only see their own requests. Unanswered requests escalate after 3 days.

Watch the squad work.

### With existing documents (BRDs, wireframes, task lists)
```
/relay:load     # reads context/ folder first
/relay:start    # Scout asks only about gaps
```

---

## Commands

| Command | Description |
|---|---|
| `/relay:doctor` | Pre-flight check — validates tools, plugins, MCP, auth profiles |
| `/relay:start` | Scaffold a new project and begin discovery |
| `/relay:load` | Load project documents before discovery |
| `/relay:status` | Show phase, gate status, scores, blockers — from real execution logs |
| `/relay:plan-review` | Unlock and re-run all three reviewers |
| `/relay:security-audit` | Run Warden security verification on the current build |
| `/relay:audit` | Full audit of an existing solution |
| `/relay:analyse` | Map an existing solution before making changes |
| `/relay:change` | Add a feature (scoped change with explicit touch/no-touch declarations) |
| `/relay:bugfix` | Fix a bug surgically — Critic diagnoses first |
| `/relay:visualise` | Generate Mermaid diagrams + optional stakeholder PowerPoint |
| `/relay:deploy` | Export managed solution for deployment |
| `/relay:config` | View or edit enforcement mode and model overrides |
| `/relay:agent <n>` | Talk directly to any specialist |

---

## How It Works

### Copilot VS Code (sequential — current default)

```
YOU ──► Conductor
          │
       Scout ──────────► docs/requirements.md
          │
       Drafter ─────────► docs/plan.md + docs/security-design.md
          │               .relay/plan-index.json (machine contract)
          │               docs/plan-scores.md (quality scores)
          │
       Auditor ─┐        parallel review → loop until BOTH approve
       Warden  ─┘
          │
       Critic ───────────► 23-item footgun checklist + adversarial pass
          │
       ▼ PLAN LOCKED (SHA256 + hook enforcement) ▼
          │
       Vault  ─┐          schema + design system (parallel)
       Stylist ─┘
          │
       Forge (Canvas App) ──► Canvas Authoring MCP
       Forge (MDA)        ──► Dataverse API sitemap XML
       Forge (Flows)      ──► PAC CLI import + clientdata PATCH activation
          │
       Sentinel ─┐         drift detection + security API tests (parallel)
       Warden   ─┘
          │
       Conductor ────────► summary to YOU + export command
```

> In Copilot VS Code, parallel steps run sequentially within one session. Output quality is identical — only speed differs.

---

### Copilot CLI with /fleet (true parallel — faster)

`/fleet` is a Copilot CLI command that enables Copilot to simultaneously dispatch multiple subagents in parallel, each with its own context window. Relay uses `/fleet` at every phase where agents are independent:

```
Phase 3 — Plan Review
/fleet
  @auditor.agent  ──► reviews plan.md for completeness
  @warden.agent   ──► reviews plan.md + security-design.md for security gaps
  (both run simultaneously, both must approve before Phase 4)

Phase 5a — Schema + Design (no dependency between them)
/fleet
  @vault.agent    ──► builds Dataverse schema, roles, FLS, env vars
  @stylist.agent  ──► builds docs/design-system.md

Phase 5b — Apps + Flows (all read schema, write to different targets)
/fleet
  @forge.agent    ──► Canvas App via Canvas Authoring MCP
  @forge.agent    ──► MDA sitemap XML via Dataverse API
  @forge.agent    ──► 6 flows JSON + pac solution import + activation

Phase 5b — Inline verification (immediately after each build stream)
/fleet
  @sentinel.agent ──► Canvas App: App Checker all 5 categories
  @sentinel.agent ──► MDA: sitemap, forms, views, publish status
  @sentinel.agent ──► Flows: imported, active, connection refs linked

Phase 6 — Final Verification
/fleet
  @sentinel.agent ──► functional verification + drift detection
  @warden.agent   ──► execute security-tests.ps1 (FLS, role boundaries, self-approval)
```

> **Important:** Subagents do not inherit the orchestrator's chat history — the `/fleet` prompt must be self-contained. This is why Relay's locked `plan.md`, `state.json`, and skill files matter — subagents read those files for context instead of relying on conversation history.

> **Cost note:** Each `/fleet` subagent consumes its own premium requests. Use `/fleet` when parallelism provides real time savings. For single-component builds, regular sequential mode is simpler and cheaper.

> **Availability:** `/fleet` is exclusive to Copilot CLI. It is not available in VS Code Agent Mode.

---

### /relay:audit — parallel after analysis

```
Analyst ────────────► docs/existing-solution.md (must complete first)
          │
/fleet
  @auditor.agent  ──► completeness + best practices
  @warden.agent   ──► security gaps + FLS + role design
  @critic.agent   ──► 23-item footgun checklist
          │
       Combined audit-report.md
```

---

### Parallel mode (Copilot CLI /fleet — faster)

`/fleet` dispatches multiple subagents simultaneously. Relay uses it at every independent phase:

```
Phase 3:  /fleet @auditor.agent + @warden.agent  (parallel review)
Phase 5a: /fleet @vault.agent + @stylist.agent    (schema + design)
Phase 5b: /fleet @forge.agent ×3                  (Canvas + MDA + Flows)
Phase 6:  /fleet @sentinel.agent + @warden.agent  (verify + security test)
```

> /fleet is Copilot CLI only. Subagents don't inherit chat history — they read plan.md and state.json for context. Each subagent consumes its own premium requests.

---

### Gate enforcement (hard stops, not suggestions)

`scripts/relay-gate-check.py` validates phase gates before agents are invoked.  
`hooks/scripts/phase-gate-hook.sh` intercepts Bash tool calls — build commands are blocked by exit code 2 if the plan isn't locked, regardless of LLM instructions.

`scripts/relay-consistency-check.py` cross-validates plan-index.json claims against actual doc content — catching agents that write optimistic values without backing them in the plan.

---

### E2E Testing with Playwright (Phase 6)

Sentinel generates and runs Playwright TypeScript tests using Microsoft's official `power-platform-playwright-toolkit`:

- **Canvas Apps**: iframe-scoped locators (`data-control-name`), 60s gallery timeouts
- **Model-Driven Apps**: `GridComponent` + `FormComponent` from the toolkit
- **AI-assisted**: Playwright MCP inspects live DOM to discover control names automatically
- **Auth**: one-time interactive sign-in, storage state reused across all tests
- **CI/CD ready**: runs headlessly in GitHub Actions / Azure Pipelines

---

## System Integrity

| Component | What it does |
|---|---|
| `.relay/plan-index.json` | Machine-readable contract — phase gate status, component inventory, quality scores |
| `.relay/execution-log.jsonl` | Structured log of every agent action — powers `/relay:status` |
| `scripts/relay-gate-check.py` | Validates gate conditions before phase advancement |
| `scripts/relay-consistency-check.py` | Cross-validates plan-index claims against plan.md |
| `scripts/relay-drift-check.py` | Compares plan-index components against actual Dataverse (table existence + column counts) |
| `scripts/relay-score.py` | Scores plan completeness (40%) + security (40%) + testability (20%) |
| `scripts/security-tests.ps1` | Generated by Warden — real API tests post-build |
| `tests/*.test.ts` | Generated by Sentinel — Playwright E2E for Canvas + MDA |
| `hooks/scripts/phase-gate-hook.sh` | Intercepts Bash tool calls to enforce gate conditions |
| Playwright tests | Generated by Sentinel — Canvas App + MDA E2E tests via power-platform-playwright-toolkit |
| Playwright MCP | AI inspects live app DOM to discover control names for test generation |

---

## Automation Capability

| Component | Status |
|---|---|
| Dataverse tables, columns, relationships | ✅ Automated |
| Security roles + FLS profiles | ✅ Automated |
| Plugins (registration + steps) | ✅ Automated |
| Environment variables | ✅ Automated |
| MDA sitemap + form XML | ✅ Automated via Dataverse API |
| Canvas App screens + formulas | ✅ Automated via Canvas Authoring MCP |
| Code app connectors (Dataverse, Outlook, SharePoint…) | ✅ Automated via code-apps plugin |
| Power Automate flows (build + activate) | ✅ Automated via Dataverse clientdata PATCH |
| Connection reference wiring | ✅ Automated — reuses existing connections |
| Security role → user assignment | ✅ `pac admin assign-user` |
| Canvas App first-time data source OAuth | ⚠️ User adds once in Power Apps Studio |
| Business rules | ❌ No public API — rule designer only |
| New OAuth connection (never existed) | ❌ Browser OAuth required (reused after) |

---

## Security First

- **Warden** reviews every plan before code is written — and executes API tests after build
- **UI-only security traps** are checked: JS `setVisible` ≠ security, Business Rule hide ≠ security, sitemap removal ≠ security
- **FLS verified on all surfaces** — form, quick-view, Web API, Advanced Find
- **Self-approval** enforced via synchronous pre-operation plugin, not just workflow
- **Connection reference identity** audited for privilege escalation
- **Security roles follow minimum-privilege** — zero-start, add only what's needed

---

## Model Strategy

| Opus | Sonnet |
|---|---|
| Conductor, Drafter, Auditor, Warden, Critic | Scout, Stylist, Analyst, Vault, Forge, Sentinel |

Configurable via `/relay:config`.

---

## Embedded Skills

No Superpowers required. All skills are embedded:

| Skill | Purpose |
|---|---|
| `relay-discovery` | Socratic requirements gathering |
| `relay-planning` | Full schema + plan structure |
| `relay-orchestration` | Phase dispatch, state management, gates |
| `relay-parallel-agents` | Phase 3/5/6 parallel coordination |
| `relay-verification` | Evidence-based build verification |
| `relay-debugging` | Root cause analysis (bugfix mode) |
| `power-platform-security-patterns` | FLS, role design, connection reference identity |
| `power-platform-footgun-checklist` | 23-item checklist (concurrency, env vars, cascade delete…) |
| `power-platform-alm` | Flow import, FLS assignment, connection reuse patterns |
| `power-fx-patterns` | Delegation, current-user filter, Patch patterns |
| `canvas-app-design-patterns` | RGBA tokens, WCAG ratios, gallery/badge patterns |
| `canvas-app-design-reading` | Analyze any screenshot and extract layout patterns |
| `canvas-app-enterprise-layout` | Named reference: pill nav left, search top, table body |
| `canvas-app-screen-layout` | 6 layout archetypes with zone diagrams + responsive formulas |
| `canvas-mcp-prompt-patterns` | Prompt library: known-good/bad patterns, /edit patterns |
| `dataverse-plugin-deployment-cycle` | 7-step plugin deploy: compile → upload → verify |
| `dataverse-privilege-depth-patterns` | Flat-BU handling, AddPrivilegesRole/RemovePrivilegeRole APIs |
| `dataverse-schema-api` | Table/column creation patterns, relationships, existence checks |
| `playwright-testing` | Playwright E2E for Canvas + MDA with Page Object Model |
| `relay-auditing` | 20-point completeness checklist for plan review |
| `relay-analysis` | Component inventory patterns for existing solutions |

---

## Project Structure

```
relay/
├── agents/              # 10 specialist agent personas
├── commands/            # 13 slash commands
├── hooks/               # PreToolUse enforcement (Write/Edit + Bash phase gates)
├── schemas/             # plan-index.schema.json
├── scripts/             # Gate validation, drift detection, scoring (Python)
├── skills/              # 21 embedded knowledge bases
├── templates/           # 7 document templates
├── docs-internal/       # adversarial-pilot-guide.md
├── lib/                 # Shared bash utilities
├── CLAUDE.md            # Conductor master instructions
└── README.md
```

---

## Roadmap

### v0.3.2
Fixes from the Training Request pilot:
- Publisher prefix captured in Scout's first question — never defaults to `cr_`
- `plan-index.json` created in `commands/start.md` as first action — can't be skipped
- `state.json` phase updated by agents at each transition
- Footgun #24 — Org-owned table privilege depth (Global only)
- Vault checks table ownership before assigning privilege depth
- Vault checks env var exists before creating (prevents duplicate error)
- Forge sets `AccessibleLabel` on all Canvas App YAML controls
- Sentinel verifies all 5 App Checker categories before Phase 6 sign-off
- After `/compact`, Conductor re-reads ALM skill before invoking Forge
- Forge flags MDA/flows as PARTIAL if not automated — Conductor retries
- CLAUDE.md explicit rule: MDA sitemap + flows are always automated
- `/fleet` prompts added to CLAUDE.md for Phase 3, 5a, 5b, 6
- `/relay:audit`, `/relay:change`, `/relay:visualise` updated with `/fleet`
- Phase 5b inline verification — Sentinel verifies each component immediately

### v0.4.0
- Playwright E2E testing via `power-platform-playwright-toolkit` + Playwright MCP
- `/fleet` parallel execution for Copilot CLI (Phase 3, 5a, 5b, 6, audit, change, visualise)
- Sentinel generates TypeScript tests from requirements, Page Objects from plan
- Phase 5 inline verification (Sentinel verifies each component immediately)
- Canvas App design reading skill + enterprise layout as named reference pattern
- All v0.3.2 pilot fixes included

### v0.5.2 (current)
- **Deny-by-default write hook** — `CLAUDE_AGENT` must be explicit and known before writes are allowed
- **Full-path enforcement** — hook restrictions now compare canonical workspace paths, not basenames
- **Stylist + Analyst enforcement** — both agents now have explicit write restrictions in `pre-tool-use.sh`
- **Expanded Bash phase gate** — `pac solution import`, `pac plugin push`, `dotnet build`, `activate-flows.ps1`, and all `pac solution export` variants are gated
- **Phase 0 schema validation** — `state.json` is validated against `schemas/state.schema.json` before discovery starts
- **Hook regression harness** — `tests/test-hooks.sh` verifies deny-by-default and phase-gate behavior
- **Prerequisite alignment** — docs and prerequisite checks now cover `bash`, `jq`, and `pwsh`

### v0.5.1
- **CLI context overflow fix** — Hard Rule #9: 400-line chunk limit for all agents
- **Template independence** — Drafter, Sentinel, Warden embed output structures (no template file lookups)
- **Flow build guide** — Forge produces markdown build guide instead of JSON (solution-layer JSON deferred to v0.5.2)
- **Canvas MCP-only** — `pac canvas pack` explicitly forbidden; Canvas Authoring MCP is the only deployment path
- **Vault PS 5.1 strict** — Forbidden operator list + parser validation for all generated scripts
- **Vault idempotent roles** — Existence check filters by name + root BU (prevents duplicates)
- **Vault FLS SP membership** — Connection reference service principals auto-added to FLS profiles
- **Vault $PSScriptRoot** — All scripts resolve state.json relative to script location
- **Scout batch questions** — CLI mode batches gap questions instead of interactive one-at-a-time
- **Phase 5 pre-flight** — Auth validation + directory pre-creation before any build agent
- **Hung subagent protocol** — 30-min timeout + re-launch pattern in orchestration skill
- **load+start merge** — `/relay:start` accepts `context_loaded=true` from `/relay:load` while keeping `phase=discovery`
- **MDA sitemap pattern** — Solution export→modify→reimport documented with script generation
- **AddSolutionComponent constants** — ComponentType code table added to ALM skill
- **`/relay:doctor`** — Pre-flight environment check: tools, plugins, MCP, auth profiles

### v0.5.0
- **Stylist v2** — Mode A (Design) + Mode B (Review); merged design-system.md template with 10 sections including MCP prompts and screen layouts
- **Canvas pipeline 3a-3i** — 9-step coordinated build between Stylist and Forge
- **Warden PS 5.1 template** — Mandatory test functions, OData URL variable rule, no PS 7+ syntax
- **Vault plugin deployment** — Full 7-step cycle with pre-images, cache flush, verify
- **Vault privilege depth** — AddPrivilegesRole/RemovePrivilegeRole API patterns, flat-BU handling
- **Sentinel pre-check** — SysAdmin detection, fixture ownership validation, flat-BU detection
- **Forge parse validation** — `[System.Management.Automation.Language.Parser]::ParseFile()` mandatory after every .ps1
- **Forge test scripts** — seed-test-data.ps1, get-test-tokens.ps1, reset-test-records.ps1 as Phase 5 outputs
- **Forge flow JSON format** — Dataverse clientData format enforced (not ARM template)
- **Gate content checks** — Phase 5 gate validates plugin DLL, flow JSON format, essential scripts
- **Gate blocking rule** — Hard Rule #8: gate failures block advancement, route to responsible agent
- **5 new skills** — plugin-deploy-cycle, privilege-depth, schema-api, screen-layout, mcp-prompt-patterns
- **3 updated skills** — security-patterns (flat-BU), orchestration (gate routing), parallel-agents (VS Code caveat)
- **Output contracts** — All agents write structured fields to plan-index.json
- **Windows compatibility** — install.js uses `where` on Windows (not `which`)
- **MCP detection** — install.js checks for Dataverse MCP global tool

### Future
- Claude Code `Task` tool parallelism (true isolated subagents)
- `/relay:learn` — cross-project pattern extraction from execution logs
- Web dashboard for execution-log.jsonl + plan-index.json visualization
- Playwright test agents (autonomous test execution + self-healing)
- Playwright test agents — long-running AI processes that execute and fix tests autonomously

---

## Before Going to Production

Run the adversarial pilot from `docs-internal/adversarial-pilot-guide.md`. Nine test cases:

1. Try to skip Auditor — does gate block build commands?
2. Write optimistic value to plan-index without backing it in plan.md — does consistency check catch it?
3. Plan 99 columns, build 15 — does drift detection flag the mismatch?
4. Inject wrong role scope — do Warden security tests fail?
5. Run same brief twice — are outputs structurally consistent?

**Target: 7/9 PASS before deploying to a real client project.**

---

## ⚠️ Project Files vs Plugin Files

Relay is a **plugin** — not a project workspace.

- **Project files** → your project folder: `.relay/`, `docs/`, `src/`, `scripts/`
- **Plugin files** → the Relay install: `agents/`, `commands/`, `skills/`

Plugin files should never contain real org URLs, solution names, GUIDs, or user emails. If you notice project-specific content in plugin agent files, report it as a bug.

---

## Contributing

See [AGENTS.md](AGENTS.md) for conventions on writing agents, skills, commands, hooks, and scripts.

## License

MIT
