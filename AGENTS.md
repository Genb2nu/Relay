# Relay — Development Conventions

This document covers conventions for contributing to Relay. Read this before editing agents, skills, commands, hooks, or scripts.

---

## Repository structure

```
relay/
├── agents/              # Specialist agent personas (.agent.md)
├── commands/            # Slash commands (.md)
├── hooks/               # PreToolUse enforcement
│   ├── hooks.json
│   └── scripts/
│       ├── pre-tool-use.sh         # Write/Edit restrictions
│       ├── phase-gate-hook.sh      # Bash command gate enforcement
│       └── session-start.sh
├── schemas/             # plan-index.schema.json
├── scripts/             # Python automation
│   ├── relay-gate-check.py
│   ├── relay-consistency-check.py
│   ├── relay-drift-check.py
│   └── relay-score.py
├── skills/              # Embedded knowledge bases (SKILL.md per folder)
├── templates/           # Document templates
├── docs-internal/       # Internal guides (adversarial-pilot-guide.md)
├── lib/                 # Shared bash utilities
├── CLAUDE.md            # Conductor master instructions
├── AGENTS.md            # This file
└── README.md
```

---

## Agent conventions (.agent.md)

Every agent file follows this structure:

```markdown
---
name: <codename>
description: |
  One paragraph. What this agent does, when it's invoked, what it produces.
model: opus | sonnet
tools:
  - Read
  - Write   # only if the agent writes files
  - Edit    # only if the agent edits files
  - Bash    # only if the agent runs commands
  - WebSearch
---

# <Codename> — <Role>

<Persona statement: "You are a senior X. You do Y.">

## Rules
<Numbered rules specific to this agent>

## Output Contract
<What the agent MUST write to plan-index.json after completing its work>

## Execution Logging
<What events the agent logs to execution-log.jsonl>

## Handoff
<Structured return to Conductor — 3-5 lines>
```

**Model assignment:**
- Opus: Conductor, Drafter, Auditor, Warden, Critic (judgment-heavy)
- Sonnet: Scout, Stylist, Analyst, Vault, Forge, Sentinel (execution-heavy)

**Write restrictions are enforced by hooks:**

| Agent | Can write to |
|---|---|
| Scout | `docs/requirements.md`, `.relay/state.json`, `.relay/plan-index.json` |
| Drafter | `docs/plan.md`, `docs/security-design.md`, `docs/plan-scores.md`, `.relay/plan-index.json` |
| Auditor | Nothing (read-only) |
| Warden | `docs/security-design.md`, `docs/security-test-report.md` |
| Critic | `docs/critic-report.md`, `.relay/plan-index.json` |
| Stylist | `docs/design-system.md`, `docs/design-review.md`, `docs/wireframes.html`, `.relay/plan-index.json` |
| Analyst | `docs/existing-solution.md` |
| Vault | `src/dataverse/`, `scripts/*.ps1`, `src/solution/`, `.relay/state.json`, `.relay/plan-index.json`, `.relay/execution-log.jsonl` |
| Forge | `src/plugins/`, `src/webresources/`, `src/pcf/`, `scripts/` |
| Forge-Canvas | `src/canvas-apps/`, `docs/canvas-app-instructions.md`, `.relay/plan-index.json`, `.relay/execution-log.jsonl` |
| Forge-MDA | `src/mda/`, `scripts/apply-mda-sitemap.ps1`, `.relay/plan-index.json`, `.relay/execution-log.jsonl` |
| Forge-Flow | `docs/flow-build-guide.md`, `.relay/plan-index.json`, `.relay/execution-log.jsonl` |
| Forge-Pages | `src/pages/`, `.relay/plan-index.json`, `.relay/execution-log.jsonl` |
| Sentinel | `docs/test-report.md`, `docs/drift-report.md` |

---

## Blocked handoff rule

When an agent cannot complete because of an environment, platform, or access blocker, the handoff must preserve the exact recovery sequence already attempted.

At minimum, include:
- the blocker state that remains true
- the concrete steps already tried, in order
- what changed vs what did not change after each step
- the next recommended action and whether it is inside or outside Relay's repo scope

Do not return a generic "blocked" summary that loses prior recovery evidence. The next agent should be able to continue from the preserved attempt history without re-running the same blind retries.

---

## Skill conventions (SKILL.md)

Every skill folder contains a `SKILL.md` file:

```markdown
---
name: <skill-name>
description: |
  What this skill covers, when agents should reference it, trigger keywords.
trigger_keywords:
  - keyword1
  - keyword2
allowed_tools:
  - Read
---

# <Skill Title>

<Content>
```

Skills are reference material, not instructions. They should be:
- Specific to Power Platform (not generic coding advice)
- Based on proven patterns (pilot-validated where possible)
- Growing — add learnings after every new project

---

## Command conventions (.md)

Commands are invoked by the user via `/relay:<name>`. Each file:

```markdown
---
description: |
  One paragraph. What this command does, when to use it.
trigger_keywords:
  - phrase1
  - phrase2
---

# /relay:<name>

When the user invokes this command:
<Step-by-step instructions for Conductor>
```

Commands should:
- Describe exact steps for Conductor to follow
- Reference which agents to invoke
- Specify what to output to the user

---

## Hook conventions

`hooks/hooks.json` registers two hook types:

- **Write/Edit PreToolUse** (`pre-tool-use.sh`) — enforces plan lock and agent write restrictions
- **Bash PreToolUse** (`phase-gate-hook.sh`) — enforces phase gate conditions on PAC CLI and verification commands

When adding new enforcement rules:
- Plan lock and agent restrictions → `pre-tool-use.sh`
- Phase advancement gates → `phase-gate-hook.sh`

Hooks exit with:
- `0` = allow
- `2` = block (Claude Code treats exit 2 as rejection)

---

## Script conventions

Python scripts in `scripts/` follow these conventions:

- Exit `0` = success/pass
- Exit `1` = failure/blocked
- Always append to `.relay/execution-log.jsonl` after running
- Always update `.relay/plan-index.json` with results
- Accept `--env` or `--phase` arguments where applicable
- Print clear human-readable output — Conductor shows this to the user

---

## plan-index.json

The schema is defined in `schemas/plan-index.schema.json`. When adding new tracked fields:

1. Update the schema first
2. Update the relevant agent's output contract section
3. Update `relay-gate-check.py` if the new field is gate-relevant
4. Update `relay-consistency-check.py` if the new field can be cross-validated against docs

---

## What NOT to put in plugin files

Plugin files (agents, skills, commands, CLAUDE.md, README.md) must never contain:

- Real environment URLs (`https://<your-org>.crm5.dynamics.com`)
- Real solution names (`<SpecificSolutionName>`)
- Real component GUIDs
- Real user emails or tenant IDs
- Hardcoded table names from specific projects (`<prefix>_<entity>`)

Use generic placeholders: `<your-org>`, `<SolutionName>`, `<table_logical_name>`, `<guid>`.

Project-specific content belongs in the project's `.relay/` and `docs/` folders, not in the plugin.

---

## Version history

| Version | Key changes |
|---|---|
| v0.1 | Initial 8 agents, 7 commands, 4 skills, hook enforcement |
| v0.2.0 | Stylist + Analyst agents; load/audit/visualise/analyse/change/bugfix commands; Power Fx + design skills; command renaming |
| v0.2.1 | Automation-first Forge; state coordination; 23-item footgun checklist |
| v0.2.2 | 6 embedded workflow skills; removed Superpowers dependency |
| v0.2.3 | All 4 Power Platform skills required; connection reuse pattern |
| v0.2.4+0.2.5 | Project content cleaned; flow activation automated via clientdata PATCH |
| v0.3.0 | plan-index.json contracts; gate validation; execution log; drift detection; Warden runtime tests; plan scoring |
| v0.3.1 | Hook-enforced phase gates; consistency check; column-level drift; adversarial pilot guide |
| v0.3.2 | Publisher prefix in Scout; plan-index.json in start.md; Vault ownership checks; Forge proactive checklists; Sentinel App Checker; post-compact ALM re-read; footgun #24+#25 |
| v0.4.0 | Playwright E2E testing; /fleet parallel execution prompts; Phase 5 inline verification; Sentinel test derivation from requirements; Canvas App design reading skill |
| v0.5.0 | Stylist v2; Canvas pipeline 3a-3i; 5 new skills; PS 5.1 enforcement; Gate content checks; Output contracts |
| v0.5.1 | CLI context overflow fix; template independence; flow build guide; Canvas MCP-only; Vault PS 5.1 strict compat; idempotent roles; FLS SP membership; AddSolutionComponent constants |
| v0.5.2 | Deny-by-default hooks; full-path enforcement; Stylist/Analyst hook cases; drift-check subprocess hardening; expanded phase-gate coverage; state schema validation; regression harness |
| v0.6.0 | Forge split into 4 specialists (forge-canvas, forge-mda, forge-flow, forge-pages); /relay:learn command; /relay:doctor full implementation; CHANGELOG.md |
| v0.6.1 | Specialist hook permissions; Phase 5 specialist completion state; expanded hook tests; flow automation note corrected |
