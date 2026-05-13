---
description: Force a fresh plan review cycle. Clears existing approvals and re-runs Auditor + Warden + Critic on the current plan.
trigger_keywords:
  - relay plan review
  - re-review plan
  - unlock plan
---

# /relay:plan-review

When the user invokes this command:

1. Read `.relay/state.json`. Verify a plan exists.

2. Clear existing approvals:
   - Set `approvals.auditor`, `approvals.warden`, `approvals.critic` to `null`
   - Set `plan_checksum` and `security_design_checksum` to `null`
   - Set `phase` to `plan_review`

3. Inform the user: "Plan unlocked. Re-running Auditor, Warden, and Critic. This will loop until all three approve."

4. Begin the Phase 3 → Phase 4 workflow as defined in CLAUDE.md.

Use this when:
- The user manually edited plan.md and wants it re-reviewed
- A build-phase issue suggests the plan itself was wrong
- The user wants to add scope and needs the plan revised
