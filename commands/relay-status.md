---
description: Show current phase, active agent, blockers, and next step for this Relay project.
trigger_keywords:
  - relay status
  - project status
  - where are we
---

# /relay:status

When the user invokes this command:

1. Read `.relay/state.json`. If it doesn't exist, say: "No Relay project found in this folder. Run `/relay:start` to begin."

2. Print a clear summary:

   ```
   Project: <project_name>
   Phase: <phase> (<human-readable description>)
   Last updated: <timestamp>

   Artifacts:
   ✓ requirements.md  (or ✗ not yet created)
   ✓ plan.md          (or ✗ not yet created)  [LOCKED / unlocked]
   ✓ security-design.md (or ✗)                [LOCKED / unlocked]
   ...

   Approvals:
   Auditor: ✓ approved / ✗ pending / ⟳ reviewing
   Warden: ✓ approved / ✗ pending / ⟳ reviewing
   Critic: ✓ approved / ✗ pending / ⟳ reviewing
   Sentinel: ✓ passed / ✗ pending / ⟳ testing
   Warden (verification): ✓ passed / ✗ pending / ⟳ testing

   Next step: <what needs to happen next>
   ```

3. Phase descriptions:
   - `init` → "Project initialised, waiting for brief"
   - `discovery` → "Scout is gathering requirements"
   - `planning` → "Drafter is writing the technical plan"
   - `plan_review` → "Auditor + Warden are reviewing the plan"
   - `adversarial_pass` → "Critic is red-teaming the approved plan"
   - `building` → "Vault + Forge specialists are building the solution"
   - `verification` → "Sentinel + Warden are verifying the build"
   - `complete` → "Project complete"
