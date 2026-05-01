---
name: relay-parallel-agents
description: |
  Patterns for dispatching Relay agents in parallel. Covers Phase 3
  (Auditor + Warden), Phase 5 (Vault + Stylist), and Phase 6
  (Sentinel + Warden). Both agents must complete and pass before the
  phase gate clears. Adapted from Superpowers dispatching-parallel-agents
  — no external dependency required.
trigger_keywords:
  - parallel agents
  - parallel review
  - dispatch parallel
  - auditor warden
  - sentinel warden
  - vault stylist
allowed_tools:
  - Read
  - Write
---

# Relay Parallel Agents

Adapted from Superpowers dispatching-parallel-agents for Power Platform review workflows.

## When Relay Uses Parallel Agents

| Phase | Agents | Both must pass |
|---|---|---|
| Phase 3 — Review | Auditor + Warden | Yes — both must approve plan |
| Phase 5 — Build | Vault + Stylist | Yes — both outputs needed before Forge |
| Phase 6 — Verify | Sentinel + Warden | Yes — both must pass before ship |

## Core Principle

Parallel agents are independent specialists reviewing or building the same
artefacts from different perspectives. They must never see each other's output
before forming their own judgment — this preserves independence.

```
❌ Wrong: "Auditor found 3 issues. Now Warden, review the plan knowing this."
✅ Right: Dispatch Warden with only plan.md + security-design.md, not Auditor's report.
```

## Phase 3 — Auditor + Warden Parallel Review

Both receive the same input: `docs/plan.md` + `docs/security-design.md`

**Dispatch Auditor with:**
- plan.md (full content)
- requirements.md (for cross-checking completeness)
- Auditor persona rules

**Dispatch Warden with:**
- plan.md (full content)
- security-design.md (full content)
- Warden persona rules
- skills/power-platform-security-patterns/SKILL.md

**After both complete:**
1. Collect all issues from both reports
2. Drafter addresses ALL issues from BOTH agents
3. Re-dispatch both for re-review
4. Loop until BOTH give explicit approval
5. Only then proceed to Phase 4

**Do NOT proceed if:**
- Only one agent approved
- Either agent gave conditional approval without re-review
- Issues were "noted" but not fixed

## Phase 5 — Vault + Stylist Parallel Build

These are parallel BUILD tasks, not reviews. Both produce outputs Forge needs.

**Vault produces:**
- Dataverse schema (tables, columns, relationships, choices)
- Security roles + FLS profiles
- Environment variables
- Seed data
- Updates state.json with component GUIDs

**Stylist produces:**
- docs/design-system.md (colours, typography, spacing, component patterns)

**Forge waits for both** before starting Canvas App build.
Forge reads design-system.md to inform /generate-canvas-app prompt.
Forge reads state.json to find Vault's component GUIDs before creating anything.

**If Stylist is unavailable:** Forge proceeds with default design tokens but
flags Canvas App as needing visual review.

## Phase 6 — Sentinel + Warden Parallel Verify

Both verify the completed build from different angles.

**Dispatch Sentinel with:**
- docs/plan.md (the approved spec)
- List of all components built (from Forge/Vault handoffs)
- Verification persona rules

Sentinel checks: does what was built match what was planned?

**Dispatch Warden with:**
- docs/security-design.md (the approved security spec)
- List of all components built
- Warden persona rules

Warden checks: are the security controls actually in place in the built solution?

**After both complete:**
- If both pass → proceed to Phase 7 (wrap-up + export)
- If either fails → Forge/Vault fix the specific failures → re-verify
- Loop until both pass

## Context Isolation

Each agent receives a precisely crafted context — only what it needs:

```
Auditor context:
  - plan.md (the document being reviewed)
  - requirements.md (to check completeness)
  - auditor persona rules

Warden context:
  - plan.md (for architecture)
  - security-design.md (the document being reviewed)
  - security-patterns skill
  - warden persona rules

Neither agent sees the other's output before completing their own review.
```

## Copilot VS Code — Sequential Fallback

Copilot VS Code doesn't support true parallel subagents or `/fleet`.
Run Phase 3 as: Auditor first, then Warden, both in same session.
Conductor still collects both outputs before proceeding.
Do NOT let Warden see Auditor's output before completing its own review.

**Important:** `/fleet` is exclusive to Copilot CLI. In VS Code Agent Mode,
Conductor runs all agents sequentially with identical output quality. Do not
attempt to use `/fleet` syntax in VS Code — it will be ignored. The sequential
approach is functionally equivalent; only parallelism (speed) differs.
