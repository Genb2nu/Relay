# Relay — The Power Platform AI Squad

An AI squad for Power Platform development. Eight specialist subagents collaborate through a structured workflow with quality gates at every handoff.

Works on **Claude Code** and **GitHub Copilot CLI**.

## What It Does

You describe what you want to build. Relay runs a squad of specialists:

| Agent | Codename | Job |
|---|---|---|
| Business Analyst | **Scout** | Gathers requirements through Socratic discovery |
| Technical Planner | **Drafter** | Writes complete implementation plans with full code |
| Plan Reviewer | **Auditor** | Reviews plan for completeness and technical soundness |
| Security Architect | **Warden** | Reviews security design, tests access boundaries |
| Adversarial Reviewer | **Critic** | Red-teams the approved plan before build starts |
| UI Designer | **Stylist** | Produces the design system (colours, typography, spacing) for Canvas Apps |
| Solution Mapper | **Analyst** | Maps existing deployed solutions for change requests and audits |
| Dataverse Engineer | **Vault** | Creates tables, columns, relationships, security roles |
| Developer | **Forge** | Builds apps, flows, and custom code |
| Tester | **Sentinel** | Verifies build against the approved plan |

The workflow: **discover → plan → review → critique → build → verify → ship**. Every handoff has a quality gate. The plan locks after three reviewers approve. Security is tested, not assumed.

## Prerequisites

- **Claude Code CLI** or **GitHub Copilot CLI**
- Node.js 22+
- Power Platform CLI (`pac`)
- Azure CLI (`az`)
- `jq`

### Recommended companion plugins

```bash
# Superpowers — workflow backbone
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

# Microsoft Power Platform skills — domain knowledge
/plugin marketplace add microsoft/power-platform-skills
/plugin install power-pages@power-platform-skills
/plugin install model-apps@power-platform-skills
/plugin install canvas-apps@power-platform-skills
/plugin install code-apps@power-platform-skills
```

Also complete the [Dataverse MCP labs](https://github.com/microsoft/Dataverse-MCP) to enable Vault and Warden's Dataverse access.

## Installation

Relay works on **Claude Code**, **GitHub Copilot CLI**, and **Copilot in VS Code** from the same repo — no duplicated files, no extra steps per tool.

### Claude Code

```
/plugin marketplace add Genb2nu/Relay
/plugin install relay@relay-marketplace
```

### GitHub Copilot CLI

```bash
copilot plugin install Genb2nu/Relay
```

### Copilot in VS Code (Preview)

1. Enable `chat.plugins.enabled` in VS Code settings
2. Open Command Palette → `Chat: Install Plugin From Source`
3. Enter `https://github.com/Genb2nu/Relay`

Or add as a persistent marketplace in `settings.json`:
```json
"chat.plugins.marketplaces": ["Genb2nu/Relay"]
```
Then search `@agentPlugins` in the Extensions view.

### Local development (single session, no install)

```bash
git clone https://github.com/Genb2nu/Relay.git
cd Relay

# Claude Code — test without installing
claude --plugin-dir /path/to/Relay

# Copilot CLI — test without installing
copilot --plugin-dir /path/to/Relay
```

## Quick Start

```
/relay:start
```

Then provide a brief:

> Build a Training Request Approval System on Dataverse. Three personas:
> Employee, Manager, L&D Admin. Employees submit training requests; managers
> approve or reject. Employees must only see their own requests.

Watch the squad work.

## Commands

| Command | Description |
|---|---|
| `/relay:start` | Scaffold a new project and begin discovery |
| `/relay:status` | Show current phase, blockers, and next step |
| `/relay:plan-review` | Unlock and re-run all three reviewers |
| `/relay:security-audit` | Run Warden verification on the current build |
| `/relay:deploy` | Export managed solution for deployment |
| `/relay:config` | View or edit enforcement mode and model overrides |
| `/relay:agent <name>` | Talk directly to any specialist |

## How It Works

```
YOU ──► Conductor
          │
       Scout ────────► requirements.md
          │
       Drafter ──────► plan.md + security-design.md
          │
       Auditor + Warden (parallel review, loop until approved)
          │
       Critic (checklist → adversarial if needed)
          │
       ▼ PLAN LOCKED ▼
          │
       Vault + Forge (parallel build)
          │
       Sentinel + Warden (parallel verification, loop until passed)
          │
       Conductor ──► summary to YOU
```

**Three rules:**
1. Plan locks after Auditor, Warden, AND Critic approve
2. Locked files can't be edited (hook-enforced)
3. Both functional AND security verification must pass before sign-off

## Security First

Relay treats security as a first-class concern, not an afterthought:

- **Warden** reviews every plan for security gaps before a line of code is written
- **UI-vs-actual-security traps** are explicitly checked (JS `setVisible` ≠ security, Business Rule hide ≠ security, sitemap removal ≠ security)
- **FLS is verified on all surfaces** — form, quick-view, Web API, Advanced Find
- **Connection reference identity** is audited for privilege escalation
- **Security roles follow minimum-privilege** — start from zero, add only what's needed

## Model Strategy

Opus for judgment, Sonnet for execution:

| Opus | Sonnet |
|---|---|
| Conductor, Drafter, Auditor, Warden, Critic | Scout, Vault, Forge, Sentinel |

Configurable via `/relay:config`.

## Project Structure

```
relay/
├── .claude-plugin/          # Plugin manifests
├── .github/                 # Copilot CLI instructions
├── agents/                  # 8 subagent personas
├── commands/                # Slash commands
├── hooks/                   # PreToolUse enforcement
├── skills/                  # Knowledge bases
│   ├── relay-workflow/
│   ├── power-platform-security-patterns/
│   ├── power-platform-footgun-checklist/
│   └── power-platform-alm/
├── templates/               # Document templates
├── lib/                     # Shared bash utilities
├── scripts/                 # Installer
├── CLAUDE.md                # Conductor instructions (Claude Code)
├── AGENTS.md                # Development guidelines
└── README.md
```

## Contributing

See [AGENTS.md](AGENTS.md) for conventions on writing agents, skills, commands, and hooks.

## License

MIT
