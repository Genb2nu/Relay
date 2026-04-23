---
name: relay-orchestration
description: |
  Conductor orchestration patterns for dispatching and coordinating Relay
  specialist agents. Covers how to dispatch subagents with precise context,
  handle their responses, manage phase transitions, and maintain state.
  Adapted from Superpowers subagent-driven-development — no external
  dependency required.
trigger_keywords:
  - conductor
  - orchestration
  - dispatch agent
  - subagent
  - phase transition
  - invoke specialist
allowed_tools:
  - Read
  - Write
  - Bash
---

# Relay Orchestration — Conductor Patterns

Adapted from Superpowers subagent-driven-development for Power Platform multi-agent workflows.

## Core Principle

Conductor coordinates — it does not implement.
Each specialist (Scout, Drafter, Auditor, Warden, Critic, Vault, Forge, Sentinel)
has a defined scope. Conductor's job is to:
1. Read the state
2. Dispatch the right agent with the right context
3. Review the output
4. Update the state
5. Decide what comes next

## Why Fresh Context Per Agent

Each agent receives only the context it needs — not Conductor's full history.
This prevents context pollution, keeps agents focused, and produces better output.

```
❌ Wrong: "Here's everything that has happened so far... now do Scout's job"
✅ Right: "You are Scout. Read requirements-template.md and docs/requirements.md
          if it exists. Here is the user's brief: <brief>. Begin discovery."
```

## Agent Dispatch Pattern

When Conductor dispatches a specialist:

1. **State check** — read `.relay/state.json` to confirm current phase
2. **Context assembly** — gather only what that agent needs:
   - Its persona file (`agents/<n>.agent.md`)
   - Relevant docs (requirements.md for Drafter, plan.md for Auditor, etc.)
   - Current environment state (org URL, solution name)
3. **Dispatch** — invoke with precise instructions
4. **Review output** — did the agent produce the expected artifact?
5. **State update** — write new phase/status to state.json
6. **Gate check** — is the quality gate satisfied before proceeding?

## Copilot VS Code Fallback

When subagents cannot write files directly (Copilot VS Code limitation):
Conductor runs each agent's logic sequentially using that agent's persona
and rules, producing the output itself. Output quality is identical.
This is expected behaviour — not an error.

## Phase Transition Rules

```
Phase 0 — Scaffold     → always runs, no gate
Phase 1 — Discovery    → gate: requirements.md exists and covers personas + workflow
Phase 2 — Planning     → gate: plan.md + security-design.md exist
Phase 3 — Review       → gate: Auditor AND Warden both approve (loop until both pass)
Phase 4 — Adversarial  → gate: Critic 18/18 checklist pass
                         ↓ PLAN LOCKED (SHA256 checksums computed)
Phase 5 — Build        → gate: Vault completes schema, Stylist completes design-system.md
                         then Forge builds apps, flows, assignments
Phase 6 — Verify       → gate: Sentinel AND Warden both pass (loop until both pass)
Phase 7 — Ship         → summary to user + export command
```

## Quality Gate Enforcement

Never advance a phase until the gate is satisfied.

### Phase 3 gate (Auditor + Warden)
```
If Auditor finds issues:
  → Drafter addresses each issue
  → Auditor re-reviews (same session or new dispatch)
  → Loop until Auditor gives explicit approval

If Warden finds issues:
  → Drafter addresses each security gap
  → Warden re-reviews
  → Loop until Warden gives explicit approval

Both must approve before Phase 4.
```

### Phase 6 gate (Sentinel + Warden)
Same loop — both must pass before wrap-up.

## State.json Schema

Conductor reads and writes this after every phase:

```json
{
  "project": "Leave Request System",
  "solution": "LeaveRequestSystem",
  "environment": "https://org76e4780e.crm5.dynamics.com",
  "mode": "greenfield",
  "phase": "build",
  "plan_locked": true,
  "plan_checksum": "sha256:104406...",
  "security_design_checksum": "sha256:1446E1...",
  "context_loaded": false,
  "components": {
    "app_modules": { "leave_request_admin": "<guid>" },
    "security_roles": { "employee": "<guid>", "manager": "<guid>" },
    "fls_profiles": { "status_protection": "<guid>" }
  },
  "decisions": [
    "Approval flow: Employee → Manager → Super Admin escalation after 3 days",
    "No sensitive data — standard security roles sufficient",
    "Two apps: Canvas (employees) + MDA (managers/admins)"
  ]
}
```

## Handling Agent Responses

Agents return structured handoff text. Conductor reads:
- What was completed
- What was NOT completed (with reasons)
- Required user actions remaining
- Any BLOCKED or ESCALATION flags

```
DONE: Proceed normally to next phase
DONE_WITH_CONCERNS: Read concerns before proceeding — address if blocking
NEEDS_CONTEXT: Provide missing info and re-dispatch
BLOCKED: Assess: more context? Better model? Plan wrong? Escalate to user.
```

## Parallel Dispatch

Some phases run agents in parallel (Phase 3: Auditor+Warden, Phase 5: Vault+Stylist, Phase 6: Sentinel+Warden).

In Copilot VS Code (no true parallelism): run sequentially in the same session.
In Claude Code (true Task tool): dispatch simultaneously, wait for both.

Either way — both must complete and pass before the phase gate clears.
