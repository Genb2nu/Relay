# Relay — The Power Platform AI Squad

A plugin-native SDLC orchestration system for Microsoft Power Platform. Ten specialist AI agents collaborate through an enforced workflow with machine-validated quality gates, execution logging, drift detection, and runtime security testing.

Works on **Claude Code**, **GitHub Copilot CLI**, and **Copilot in VS Code**.

> **v0.3.1** — Structured contracts · Hook-enforced phase gates · Consistency validation · Column-level drift detection · Adversarial pilot guide

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
| Developer | **Forge** | Canvas Apps, MDA, Power Automate flows, code apps |
| Tester | **Sentinel** | Functional verification + drift detection (plan vs actual build) |

**Workflow:** discover → plan → review → critique → build → verify → ship

Every phase transition is gate-validated. The plan locks with SHA256 checksums after three independent reviewers approve. Security is tested at runtime, not just reviewed on paper.

---

## Prerequisites

- **Claude Code CLI** or **GitHub Copilot CLI** or **Copilot in VS Code**
- Node.js 22+
- Power Platform CLI (`pac`)
- Azure CLI (`az`)
- Python 3.8+ (for gate validation, drift detection, and scoring scripts)

### Required: Microsoft Power Platform Skills

```bash
/plugin marketplace add microsoft/power-platform-skills
/plugin install canvas-apps@power-platform-skills
/plugin install model-apps@power-platform-skills
/plugin install power-pages@power-platform-skills
/plugin install code-apps@power-platform-skills
```

| Plugin | Forge uses it for |
|---|---|
| `canvas-apps` | `/configure-canvas-mcp`, `/generate-canvas-app`, `/edit-canvas-app` |
| `model-apps` | `/genpage` — custom React pages in Model-Driven Apps |
| `power-pages` | `/create-site` — Power Pages portals |
| `code-apps` | `/create-code-app`, `/add-dataverse`, `/add-office365`, `/deploy` |

> **No Superpowers needed.** All orchestration, discovery, planning, verification, and debugging skills are embedded in Relay.

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

### Gate enforcement (hard stops, not suggestions)

`scripts/relay-gate-check.py` validates phase gates before agents are invoked.  
`hooks/scripts/phase-gate-hook.sh` intercepts Bash tool calls — build commands are blocked by exit code 2 if the plan isn't locked, regardless of LLM instructions.

`scripts/relay-consistency-check.py` cross-validates plan-index.json claims against actual doc content — catching agents that write optimistic values without backing them in the plan.

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
| `hooks/scripts/phase-gate-hook.sh` | Intercepts Bash tool calls to enforce gate conditions |

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

---

## Project Structure

```
relay/
├── agents/              # 10 specialist agent personas
├── commands/            # 13 slash commands
├── hooks/               # PreToolUse enforcement (Write/Edit + Bash)
├── schemas/             # plan-index.schema.json
├── scripts/             # Gate validation, drift detection, scoring (Python)
├── skills/              # 12 embedded knowledge bases
├── templates/           # 7 document templates
├── docs-internal/       # adversarial-pilot-guide.md
├── lib/                 # Shared bash utilities
├── CLAUDE.md            # Conductor master instructions
└── README.md
```

---

## Roadmap

### v0.3.2 (next release)
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

### v0.4 (parallel execution)
- **Claude Code**: Full parallel Phase 3/5/6 using the `Task` tool — true isolated subagents with independent context windows, file access, and tool permissions. Each agent runs simultaneously, not sequentially.
- **Copilot CLI**: Full `/fleet` integration — structured prompts for every parallel phase, dependency-aware DAG scheduling, `@agent-name` syntax for Relay specialists.
- **VS Code**: Sequential-with-inline-verification as the fallback (already designed in v0.3.2).
- **Cross-project memory**: `/relay:learn` command reads completed project execution logs and promotes repeated patterns into skill files automatically.
- **Web dashboard**: Reads `.relay/execution-log.jsonl` and `plan-index.json` and renders project status visually — for stakeholders and team leads who don't want to read JSON.

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
