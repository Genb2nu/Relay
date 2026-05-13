# sn-plugin — SimplifyNext Power Platform Copilot

A GitHub Copilot CLI plugin that gives developers an AI squad to build
Power Platform solutions following SimplifyNext's exact delivery standards.

---

## What Is This?

`sn-plugin` is a set of instructions, agent definitions, commands, skills,
and hooks that configure GitHub Copilot (or Claude Code) to behave as a
structured Power Platform delivery squad.

When you use this plugin, you get:
- **Scout** — gathers your requirements
- **Blueprint** — writes the technical plan
- **Auditor** — reviews the plan against your requirements
- **Forge** — builds Dataverse schema, Canvas Apps, MDAs, and flows via API
- **Sentinel** — verifies everything matches the plan

---

## Quick Start

### 1. Copy plugin to your project

```bash
# In your project root
cp -r sn-plugin/. .
```

Or clone directly:

```bash
git clone https://github.com/simplify-next/sn-plugin.git
```

### 2. Start a new project

```
/sn-start
```

This will ask you for:
- Project name
- Publisher prefix (e.g. `ops`, `hr`, `exp`)
- Publisher display name
- Environment URL

### 3. Follow the workflow

```
/sn-start        → Scout gathers requirements
/sn-plan-review  → Auditor reviews Blueprint's plan
/sn-build        → Forge builds everything
/sn-qa           → Sentinel verifies
/sn-deploy       → Export and deploy
```

---

## Commands

| Command | Purpose |
|---|---|
| `/sn-start` | Initialise project and gather requirements |
| `/sn-status` | Show current phase and gate status |
| `/sn-update-components` | Re-run a specific Forge specialist |
| `/sn-list-components` | List all planned components and build status |
| `/sn-plan-review` | Trigger Auditor review cycle |
| `/sn-build` | Start or resume the build phase |
| `/sn-qa` | Run full QA gate (drift + tests + security) |
| `/sn-patch-components` | Apply a targeted patch to a specific component |
| `/sn-deploy` | Export and deploy the solution |
| `/sn-agent` | Invoke a specific agent directly |
| `/sn-config` | Show or update project configuration |

---

## Directory Structure

```
.
├── .github/
│   └── copilot-instructions.md   ← Copilot identity and routing rules
├── agents/
│   ├── scout.agent.md            ← Requirements gathering
│   ├── blueprint.agent.md        ← Technical planning
│   ├── auditor.agent.md          ← Plan review
│   ├── forge.agent.md            ← Build (Dataverse, Canvas, MDA, Flow)
│   └── sentinel.agent.md         ← QA and verification
├── commands/                     ← Slash command definitions
├── hooks/                        ← Pre/post tool hooks
├── skills/                       ← Domain knowledge
├── templates/                    ← Document templates
├── lib/                          ← Shared shell utilities
├── AGENTS.md                     ← Agent reference
└── README.md                     ← This file
```

---

## Skills

The `skills/` folder contains SimplifyNext's codified knowledge:

| Skill | Contents |
|---|---|
| `sn-component-library.md` | Standard component patterns and naming |
| `sn-flow-patterns.md` | Power Automate templates and error handling |
| `sn-canvas-patterns.md` | Canvas App screen patterns and Power Fx |
| `sn-dataverse-patterns.md` | Dataverse REST API patterns |
| `sn-mda-patterns.md` | Model-Driven App API patterns |
| `sn-qa-standards.md` | Definition of done and test templates |
| `sn-non-negotiables.md` | Absolute standards — no exceptions |

---

## State Management

All project state lives in `.sn/state.json`:

```json
{
  "project": "Ops Management Portal",
  "publisher_prefix": "ops",
  "solution_name": "ops_OpsManagement",
  "environment": "https://contoso.crm5.dynamics.com",
  "phase": "build",
  "auditor_approved": true,
  "plan_locked": true,
  "components": {
    "tables": { "ops_request": "<guid>" },
    "security_roles": { "OpsManager": "<guid>" }
  }
}
```

An execution log is maintained at `.sn/execution-log.jsonl`.

---

## Prerequisites

- **PAC CLI** (Power Platform CLI): `dotnet tool install --global Microsoft.PowerPlatform.PowerApps.CLI`
- **Python 3.x** (for gate scripts)
- **GitHub Copilot CLI** or **Claude Code** with agent support
- **Power Platform environment** with System Customizer or System Administrator access

---

## Non-Negotiables

Every solution built with sn-plugin must meet SimplifyNext's 19 non-negotiable
standards. Key ones:

1. Named solution — no Default Solution
2. Managed in test/prod
3. Publisher prefix consistency throughout
4. No UI-only security (FLS required for sensitive columns)
5. Try-Catch error handling in every flow
6. Connection references (no personal connections)
7. Canvas App Checker 0 errors before sign-off
8. MDA published before QA
9. Version incremented before every deployment

Full list: `skills/sn-non-negotiables.md`

---

## Contributing

This plugin is maintained by SimplifyNext. Raise issues or PRs against the
main repository.

For internal use: follow the same workflow this plugin enforces — plan,
review, build, verify.

---

## Licence

Internal — SimplifyNext use only. Do not distribute outside the organisation.
