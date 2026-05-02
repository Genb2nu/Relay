---
name: relay-planning
description: |
  Structured plan writing for Power Platform projects. Used by Drafter to
  turn approved requirements into a locked implementation plan with exact
  component specifications, build order, and security design. Adapted from
  Superpowers writing-plans — no external dependency required.
trigger_keywords:
  - write plan
  - implementation plan
  - plan.md
  - drafter
  - technical planning
allowed_tools:
  - Read
  - Write
---

# Relay Planning — Implementation Plan Writing

Adapted from Superpowers writing-plans skill for Power Platform projects.
Drafter uses this skill to produce plan.md and security-design.md.

## Core Principle

The plan is the contract. Every component that gets built must be in the plan.
Every decision in the plan must be traceable to the requirements.
Once locked, the plan cannot change without going back through Auditor + Warden + Critic.

## File Structure First

Before writing a single task, map out every file and component that will exist:

```
docs/
├── requirements.md    ← already exists (Scout wrote it)
├── plan.md            ← Drafter writes this
└── security-design.md ← Drafter writes this

src/
├── webresources/      ← JS web resources (if any)
├── plugins/           ← C# plugins (if any)
├── flows/             ← Flow JSON definitions
├── canvas-apps/       ← .pa.yaml source files
└── solution/          ← PAC CLI solution files

scripts/
└── *.ps1              ← Vault automation scripts
```

Map what goes in each. This is where decomposition gets locked in.

## Plan Structure

`docs/plan.md` must contain ALL of the following sections:

### 1. Solution Overview
- Solution name, publisher prefix, environment
- Components list (tables, apps, flows, plugins, security roles)
- Build order and phase breakdown

### 2. Dataverse Schema (full specification — Drafter owns this)

For every entity:
```markdown
### <prefix>_<main_entity> — <Main Entity Display Name>  *(example — use your actual table name and prefix)*
| Column | Logical Name | Type | Required | Notes |
|---|---|---|---|---|
| Request ID | <prefix>_name | Autonumber | Yes | Primary name |
| Requestor | <prefix>_requestor | Lookup → systemuser | Yes | |
| Status | <prefix>_status | Choice → <prefix>_status | Yes | Global choice |
```

Include:
- All columns with logical names, data types, required flags
- Relationships (1:N, N:N)
- Global choices / option sets with values
- Auto-number formats

### 3. Security Design (reference security-design.md)

For each security role:
- Table privileges with exact scope (User / BU / Org)
- FLS columns that need protection
- Connection reference identity (maker vs invoking user)

### 4. Apps

For Canvas App:
- Screen list with purpose and data source per screen
- Key controls and Power Fx formulas for non-trivial logic
- Navigation structure

For Model-Driven App:
- App module name
- Sitemap structure (areas, groups, subareas)
- Forms with sections and fields per section
- Views with filter criteria
- Dashboards

### 5. Power Automate Flows

For each flow — full specification:
- Trigger: table, message, filter columns
- Concurrency: sequential (degree=1) or parallel
- Step-by-step logic: all conditions, branches, and actions
- Error handling: Scope + Configure run after (failed, timed out)
- Connection references used
- Balance update logic (if applicable)

### 6. Server-Side Logic

For each plugin:
- Assembly name and namespace
- Registered step: table, message, stage (Pre/Post), mode (Sync/Async)
- Pre-image attributes (if Pre-Operation)
- Logic: what it validates and what it blocks
- Error message format

### 7. Build Order

Explicit dependency-ordered list:
1. Publisher + solution
2. Global choices
3. Tables + columns (leaf tables first, then tables with lookups)
4. Relationships
5. Security roles + FLS profiles
6. Plugin registration
7. Flows
8. App module + sitemap
9. Canvas App
10. Seed data

### 8. DECISION NEEDED Items

Every open question from requirements.md that affects the build must be listed:
```
DECISION NEEDED: Escalation timer — how many days before a pending 
request escalates to Super Admin? (Suggest: 3 days)
```

Drafter may suggest a default but must NOT decide for the user.

## Bite-Sized Tasks

Break the plan into tasks that are:
- 2-10 minutes each to execute
- Have clear completion criteria
- Specify exact file paths and component names
- Include verification steps

Bad task: "Create the security roles"
Good task: "Create <ProjectName> Employee role with User-level CRUD on <prefix>_<maintable>, User-level Read on <prefix>_<lookuptable>, Org-level Read on systemuser. Verify: pac admin list-role shows role with correct name"

## security-design.md

Write separately from plan.md. Contains:

```markdown
# Security Design — <Project Name>

## Threat Model
- Self-approval risk: [mitigation]
- Privilege escalation via API: [mitigation]
- UI-only security traps: [what was rejected and why]

## Security Roles
| Role | Table | Create | Read | Write | Delete | Scope |
|---|---|---|---|---|---|---|

## FLS Coverage
| Column | Why sensitive | Profile: Read-only | Profile: Full access |
|---|---|---|---|

## Connection References
| Reference | Connector | Identity | Why this identity |
|---|---|---|---|

## DLP Considerations
[if applicable]

## Security Checklist
- [ ] No UI-only security (JS hide, sitemap removal, Business Rule hide)
- [ ] FLS on all sensitive columns
- [ ] Plugin prevents self-approval
- [ ] Service account minimum privilege
- [ ] Connection reference identity reviewed
```

## Handoff

After writing both documents, tell Conductor:
```
Plan complete.
plan.md: <N> lines — covers schema, <N> tables, <N> flows, <N> apps
security-design.md: <N> lines — covers roles, FLS, threat model
DECISION NEEDED items: <N>
Ready for Phase 3 — Auditor + Warden review.
```
