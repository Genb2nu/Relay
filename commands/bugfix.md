---
description: |
  Fix a specific bug in an existing Power Platform solution. Critic diagnoses
  the root cause first, Drafter writes a minimal fix plan, Forge touches only
  what the fix requires. Designed to be surgical — no unintended side effects.
trigger_keywords:
  - relay bugfix
  - fix bug
  - bug fix
  - something is broken
  - not working
  - error in solution
---

# /relay:bugfix

When the user invokes this command:

1. Check that `docs/existing-solution.md` exists. If not:
   - Tell the user: "Run `/relay:analyse` first so I understand the existing
     solution before diagnosing the bug."
   - Stop.

2. Ask the user to describe the bug:
   "Describe the bug:
   - What behaviour is happening?
   - What behaviour was expected?
   - When did it start? (after a deployment? always been there?)
   - Which component is involved? (flow name, table, app screen, etc.)
   - Any error messages?"

3. Update `.relay/state.json`:
   ```json
   {
     "mode": "bugfix",
     "phase": "diagnosis",
     "bug_description": "<user description>"
   }
   ```

4. Run the **bugfix workflow** — Critic diagnoses FIRST:

   **Phase: Diagnosis (Critic)**
   Critic reads `docs/existing-solution.md` and the bug description.
   Critic's job here is root cause analysis, not plan review:
   - What is most likely causing this behaviour?
   - Walk through the execution path: trigger → logic → outcome
   - Check the footgun checklist for known failure modes matching this symptom
   - Produce `docs/bug-diagnosis.md`:

   ```markdown
   # Bug Diagnosis — <bug description>

   ## Symptom
   <What the user reported>

   ## Probable root cause
   <Most likely cause with reasoning>

   ## Execution path analysis
   1. <Step 1 in the execution path>
   2. <Step 2 — where it likely fails>
   3. ...

   ## Alternative causes to rule out
   - <Alternative 1> — rule out by: <how to verify>
   - <Alternative 2> — rule out by: <how to verify>

   ## Recommended fix approach
   <High-level fix direction — NOT the implementation>

   ## Components involved
   | Component | Role in bug |
   |---|---|
   | | |

   ## Components NOT involved (do not touch)
   | Component | Why not involved |
   |---|---|
   | | |
   ```

   **Phase: Fix Planning (Drafter)**
   Drafter reads `docs/bug-diagnosis.md` and produces `docs/fix-plan.md`:
   - The minimal change required to fix the root cause
   - Explicit scope: ONLY what the fix touches
   - Explicit non-scope: everything else
   - Expected outcome after the fix

   **Phase: Review (Warden only — lightweight)**
   Warden checks the fix doesn't introduce a security gap.
   Auditor is skipped — fixes are minimal and don't warrant full plan review.

   **Phase: Fix (Forge specialist or Vault as needed)**
   Forge specialist/Vault implement ONLY what `docs/fix-plan.md` specifies.
   Any temptation to "improve things while we're in here" is rejected.

   **Phase: Verify (Sentinel)**
   Sentinel verifies:
   - The bug is fixed (the reported symptom no longer occurs)
   - Regression: related components still behave correctly

5. On completion, tell the user:
   - What was changed
   - How to verify the fix in the environment
   - Whether a solution export is needed
