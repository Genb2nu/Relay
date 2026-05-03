---
name: relay-workflow
description: |
  Master workflow skill for Relay. Defines the end-to-end lifecycle for Power
  Platform projects: discovery → planning → review → adversarial pass → build →
  verification → deploy. Automatically triggered when Conductor starts a project.
trigger_keywords:
  - relay
  - start project
  - new power platform project
  - begin relay
allowed_tools:
  - Read
  - Write
  - Bash
  - WebSearch
  - Task
---

# Relay Workflow

## Overview

Relay is an AI squad for Power Platform development. Specialist subagents
collaborate through a structured workflow with quality gates at every handoff.

## Phases

### Phase 1 — Discovery
- **Agent**: Scout
- **Input**: User's project brief
- **Output**: `docs/requirements.md`
- **Gate**: User approves requirements

### Phase 2 — Planning
- **Agent**: Drafter
- **Input**: Approved `docs/requirements.md`
- **Output**: `docs/plan.md`, `docs/security-design.md`
- **Gate**: User acknowledges plan is ready for review

### Phase 3 — Plan Review
- **Agents**: Auditor + Warden (can run in sequence)
- **Input**: `docs/plan.md`, `docs/security-design.md`
- **Output**: Structured review feedback
- **Gate**: Both return `{status: "approved"}`
- **Loop**: If either finds issues → Drafter revises → re-review

### Phase 4 — Adversarial Pass
- **Agent**: Critic
- **Input**: `docs/plan.md`, `docs/security-design.md`, `docs/requirements.md`
- **Output**: `docs/critic-report.md`
- **Gate**: Critic returns `{status: "approved"}`
- **Mode**: Checklist first. Free-form only if checklist finds FAIL items.
- **Loop**: If issues → Drafter/Warden revise → re-run all three reviewers
- **LOCK**: After all three approve, checksum plan.md and security-design.md

### Phase 5 — Build
- **Agents**: Vault (schema) + Stylist (design) + Forge specialists (apps/flows/code)
  - forge-canvas → Canvas App screens
  - forge-mda → Model-Driven App sitemap + forms
  - forge-flow → Flow build guides (temporary — automation planned v0.6.x)
  - forge-pages → Power Pages portals
  - forge → Plugins, code apps, web resources, env vars
- **Input**: Locked `docs/plan.md`, `docs/security-design.md`
- **Output**: Dataverse schema, apps, flows, code in `src/`
- **Warden on-call**: Available for security questions during build

### Phase 6 — Verification
- **Agents**: Sentinel (functional) + Warden (security)
- **Input**: Built solution + locked plan + locked security design
- **Output**: `docs/test-report.md`, `docs/security-test-report.md`
- **Gate**: Both return passed status
- **Loop**: If issues → Forge specialist/Vault fix → re-verify
- **On-demand**: Critic can be invoked if material issues suggest plan was wrong

### Phase 7 — Deploy
- **Agent**: Conductor (or Courier if available)
- **Input**: Verified solution
- **Output**: Exported managed solution, deployment summary

### Phase 8 — Wrap
- **Agent**: Conductor
- **Output**: Summary to user with: what was built, security posture, open items

## State Management

All state is stored in `.relay/state.json`, never in conversation memory.
Conductor reads this file at session start and updates it at every phase transition.

## Token Discipline

1. Subagents return 3–5 line summaries, not transcripts
2. Pass file paths to subagents, not file contents
3. Critic is checklist-first (cheap) then adversarial (expensive, only if needed)
4. Plan phase and build phase should ideally run in separate sessions
5. Use `/compact` between phases if context grows large

---

## Dataverse MCP — Tools Available to Vault, Warden, Analyst

When Dataverse MCP is connected, these tools are available:

| Tool | Used by | Purpose |
|---|---|---|
| list_tables | Vault, Analyst | Discover existing tables in the environment |
| describe_table | Vault, Analyst | Get schema of a specific table |
| create_record | Vault, Forge | Insert rows (seed data, test data) |
| read_query | Vault, Warden, Analyst, Sentinel | Query records with SELECT |
| update_record | Vault, Forge | Update existing rows |
| delete_record | Vault | Delete rows (cleanup, test data) |
| Create Table | Vault | Create new Dataverse table |
| Update Table | Vault | Modify table schema/metadata |
| search | Analyst | Full-text search across Dataverse |
| fetch | Analyst, Sentinel | Retrieve specific record by ID |

### Connection URL pattern
```
https://<org-name>.crm5.dynamics.com/api/mcp
```
Org URL found at: make.powerapps.com → Settings gear → Session details → Instance URL

### Enabling in Power Platform Admin Center
1. PPAC → Environments → select env → Settings → Product → Features
2. Enable: "Allow MCP clients to interact with Dataverse MCP server"
3. Advanced Settings → enable "Microsoft GitHub Copilot" client
