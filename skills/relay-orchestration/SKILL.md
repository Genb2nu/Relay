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
Each specialist (Scout, Drafter, Auditor, Warden, Critic, Vault, Forge specialists, Sentinel)
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

The same fallback applies in Phase 5 when a specialist can describe the build
artifacts but cannot execute them directly in the current interface: Conductor
persists the returned artifacts and runs the generated commands/scripts.

## Phase Transition Rules

```
Phase 0 — Scaffold     → always runs, no gate
Phase 1 — Discovery    → gate: requirements.md exists and covers personas + workflow
Phase 2 — Planning     → gate: plan.md + security-design.md exist and the plan is build-ready for Vault
Phase 3 — Review       → gate: Auditor AND Warden both approve (loop until both pass)
Phase 4 — Adversarial  → gate: Critic 18/18 checklist pass
                         ↓ PLAN LOCKED (SHA256 checksums computed)
Phase 5 — Build        → gate: Vault completes schema, Stylist completes design-system.md
                         then Forge specialists build apps, flows, assignments:
                           forge-canvas → Canvas App screens
                           forge-mda    → Model-Driven App sitemap + forms
                           forge-flow   → Flow build guides
                           forge-pages  → Power Pages portals
                           forge        → Plugins, code apps, web resources, env vars
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
  "project": "<Your Project Name>",
  "solution": "<YourSolutionName>",
  "environment": "https://<your-org>.crm.dynamics.com",
  "mode": "greenfield",
  "phase": "build",
  "plan_locked": true,
  "plan_checksum": "sha256:104406...",
  "security_design_checksum": "sha256:1446E1...",
  "context_loaded": false,
  "components": {
    "app_modules": { "admin_app": "<guid>" },
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

---

## Gate Failed — What To Do

When `python scripts/relay-gate-check.py --phase N` exits 1:

**Conductor MUST NOT:**
- Update `state.json.phase` to the next phase
- Skip the gate and invoke the next phase's agents
- Tell the user "we'll fix it later"

**Conductor MUST:**
1. Read the gate error output (printed to stdout)
2. Identify which agent is responsible for each error
3. Route the specific error(s) back to that agent
4. After the agent fixes → re-run the gate
5. Repeat until exit 0

**Error routing table:**
| Gate error contains | Route to |
|---|---|
| "Auditor has not approved" | Auditor (re-review) |
| "Warden has not approved" | Warden (re-review) |
| "Critic has not approved" | Critic (re-review) |
| "Vault has not completed" | Vault (fix schema) |
| "Forge has not completed" | Forge specialist (fix build) |
| "Sentinel verification not passed" | Sentinel → identify failure → route to Forge specialist |
| "security tests failed" | Forge specialist/Vault fix → Warden re-test |
| "drift detected" | Forge specialist (fix missing components) |
| "inconsistent with docs" | Drafter (update plan or fix plan-index) |
| "build-ready for Vault" | Drafter (fill missing build-contract details) |
| "DECISION NEEDED" | Ask user |
| "Required script missing" | Forge (generate the script) |
| "no .dll found" | Forge (compile plugin) |
| "ARM-shaped" | forge-flow (regenerate in Dataverse format) |
| "canvas_app_bootstrapped" | Print Canvas bootstrap checklist to user |

**Maximum retries:** If the same gate error persists after 3 fix attempts,
escalate to the user with full context. Do not loop indefinitely.

---

## Hung Subagent Protocol

**`stop_powershell` does NOT kill subagents.** Subagent processes are isolated from
the PowerShell terminal session. Calling `stop_powershell` returns success but the
agent continues running (or remains stuck).

**When a subagent appears hung (no progress for 10+ minutes):**

1. **Do NOT** attempt to kill it via `stop_powershell` or any shell command
2. **Wait** for the completion notification — CLI agents have no visible progress bar
   but may still be working (especially token-heavy schema/code generation)
3. **If no notification after 30 minutes**, assume failure and re-launch with smaller scope:
   - Drafter: "Write only sections 1-6 of plan.md" → then "Write sections 7-12"
   - Vault: "Write tables 1-8 to create-schema-part1.ps1" → then "Write tables 9-16"
   - Forge specialists: Split by component type — one specialist per app/flow/script
4. **Log the timeout** in execution-log.jsonl as `event: "agent_timeout"`
5. **If a Phase 5 specialist returned exact scripts/artifacts but could not persist or execute them, Conductor should persist and run them before declaring the phase blocked**

**Root cause:** Large file output + high token-density code = context window exhaustion.
The agent reaches its output limit before the `create` tool call completes. The 400-line
chunk rule (Hard Rule #9) prevents this for new runs.
