---
name: relay-discovery
description: |
  Socratic discovery for Power Platform projects. Used by Scout to turn a
  one-paragraph brief into a fully validated requirements document. Asks
  questions one at a time, proposes approaches, validates design sections
  before writing. Adapted from Superpowers brainstorming skill — no external
  dependency required.
trigger_keywords:
  - discovery
  - requirements
  - what to build
  - brief
  - gather requirements
  - scout
allowed_tools:
  - Read
  - Write
---

# Relay Discovery — Requirements Gathering

Adapted from Superpowers brainstorming skill for Power Platform project discovery.
Scout uses this skill to turn a brief into a validated requirements document.

## Core Principle

Never start writing requirements until you understand the full picture.
A half-understood brief produces a half-correct solution.
One wrong assumption at this stage costs 10x to fix in Phase 5.

## Anti-Pattern: "The Brief Is Clear Enough"

Every project needs discovery — even ones that seem obvious.
"Build a request-management app" could mean:
- Canvas App only, or Canvas + Model-Driven
- Simple approval or multi-level escalation
- Employee self-service or HR-managed
- Dataverse or SharePoint backend

The design can be short for simple projects, but you MUST validate before writing requirements.

## Discovery Process (Scout follows this exactly)

### Step 1 — Read existing context first

Before asking a single question:
- Check if `context/` folder exists and read all files in it
- Check if `.relay/context-summary.md` exists (from `/relay:load`)
- Read any uploaded wireframes, BRDs, task lists
- What do you already know? What gaps remain?

### Step 2 — Ask questions ONE AT A TIME

Never ask more than one question per message. If a topic needs more exploration,
come back to it after the user answers.

**Prefer multiple choice over open-ended:**
```
❌ "Who will use this system?"
✅ "Who are the primary users? A) Only employees submitting requests,
    B) Employees + managers who approve, C) Employees + managers + HR admins,
    D) Something else"
```

**Question order for Power Platform projects:**
1. Personas — who uses it and what do they do?
2. Core workflow — what is the main process end-to-end?
3. Data — what entities does this track?
4. Security — what data should each persona NOT see?
5. Integration — SharePoint? Teams? Outlook? External systems?
6. Existing solutions — is there anything already built we need to work with?
7. Out-of-scope — what should this NOT do?

**Stop asking when you can answer all of these:**
- Who are all the personas and their access boundaries?
- What is the complete workflow from start to finish?
- What data needs to be stored?
- What should each persona NOT be able to see or do?

### Step 3 — Propose 2-3 approaches before committing

Once you understand the requirements, propose options:

```
I see two main approaches for this:

Option A: Canvas App + Dataverse
- Employee submits via Canvas App, manager approves via Model-Driven App
- Full control over UI, offline capable
- More build effort

Option B: Model-Driven App only
- Standard Dynamics-style forms for all users
- Faster to build, less custom UI
- Less polished employee experience

I recommend Option A because [reason].
Which direction fits better?
```

### Step 4 — Present design in sections, validate each one

Don't dump the full requirements at once. Present section by section:

```
Section 1 — Personas and access boundaries
[present, ask "does this look right?"]

Section 2 — Core workflow and user stories
[present, ask "anything missing?"]

Section 3 — Data model (entity names and purpose — no columns)
[present, ask "are all entities covered?"]

Section 4 — Out of scope and open questions
[present, ask "any gaps?"]
```

Only proceed to writing the requirements document after all sections are approved.

## Scope Check — Multi-Subsystem Projects

Before detailed questions, assess scope. If the brief describes multiple
independent subsystems (e.g. "HR platform with leave, expenses, performance,
and training"), flag it immediately:

"This sounds like 4 separate projects. Each should have its own requirements →
plan → build cycle. Which one should we start with?"

Don't spend questions refining a project that should be decomposed first.

## Column Definitions — NOT Scout's Job

Scout captures entity NAMES and PURPOSE only.
Scout does NOT define:
- Column names or data types
- Relationships between tables
- Choice set values
- Required vs optional fields

That is Drafter's job. If you find yourself writing column lists, stop.

## What Goes in requirements.md

After approval, write `docs/requirements.md`:

```markdown
# Requirements — <Project Name>

## Personas
### <Name>
- Description
- Key actions
- Access boundaries (what they CANNOT see/do)

## User Stories
### <Persona>
- As a <persona>, I want to <action> so that <value>
[minimum 5 per persona]

## Entities (names and purpose only)
- <EntityName>: <what it represents, one sentence>

## Apps
- <Canvas App name>: <personas and purpose>
- <Model-Driven App name>: <personas and purpose>

## Integrations
- <System>: <what data flows where>

## Out of Scope
- <item>

## Open Questions
- <question that needs a decision before or during planning>
```

## Handoff to Drafter

After writing requirements.md, tell Conductor:
```
Requirements complete. Personas: <N>. User stories: <N>. Entities: <N>. Open questions: <N>.
Ready for Phase 2 — Planning (Drafter).
```
