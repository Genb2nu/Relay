---
description: |
  Add a feature or make a scoped change to an existing Power Platform solution.
  Requires /relay:analyse to have run first. Produces a change-plan that
  explicitly scopes what is touched and what is not — preventing unintended
  side effects on working components.
trigger_keywords:
  - relay change
  - add feature
  - modify solution
  - change request
  - new feature on existing
---

# /relay:change

When the user invokes this command:

1. Check that `docs/existing-solution.md` exists. If not:
   - Tell the user: "Run `/relay:analyse` first so I understand the existing
     solution before planning a change."
   - Stop.

2. Ask the user to describe the change:
   "Describe the change or feature you want to add. Be specific about:
   - What new behaviour is needed
   - Which existing components it touches (if known)
   - Any constraints (must not break X, must work with Y)"

3. Update `.relay/state.json`:
   ```json
   {
     "mode": "change",
     "phase": "discovery",
     "change_description": "<user description>"
   }
   ```

4. Run the **scoped change workflow**:

   **Phase: Discovery (Scout)**
   Scout reads `docs/existing-solution.md` + `context/` (if loaded) + the
   change description. Scout asks ONLY about gaps specific to the change —
   not about things already documented in existing-solution.md.

   **Phase: Change Planning (Drafter)**
   Drafter produces `docs/change-plan.md` (NOT plan.md). This document MUST:
   - Specify exactly what is being added or modified
   - For every component it touches, declare the existing state and the new state
   - Explicitly list what is NOT touched and why
   - Include a regression risk assessment: "Changing X may affect Y — here's why it won't"

   ```markdown
   # Change Plan — <change description>
   Base solution: <solution name> | Date: <date>

   ## Change scope
   <One paragraph description of exactly what this change does>

   ## Components being modified
   | Component | Current state | New state | Risk |
   |---|---|---|---|
   | cr_leaverequest | 15 columns | +1 column: cr_category | Low |
   | Approval flow | 3 steps | +1 condition for cr_category | Medium |

   ## Components explicitly NOT touched
   | Component | Reason not touched |
   |---|---|
   | Canvas App scrHome | No UI change required |
   | cr_leavebalance table | Balance logic unchanged |
   | Employee security role | Permissions unchanged |

   ## New components being added
   | Component | Type | Purpose |
   |---|---|---|
   | | | |

   ## Regression risk assessment
   - Changing <X>: could affect <Y> because <reason>. Mitigation: <how Forge avoids it>

   ## Rollback plan
   <How to undo this change if it breaks something>
   ```

   **Phase: Review (Auditor + Warden)**
   Same as normal plan review but focused only on the change-plan scope.
   Auditor checks the change doesn't break existing components.
   Warden checks the change doesn't introduce security gaps.

   **Phase: Adversarial (Critic)**
   Critic reviews the change-plan specifically for:
   - Unintended side effects on NOT-touched components
   - Missing regression test coverage
   - Flow trigger conflicts (does the change cause a flow to fire unexpectedly?)

   **Phase: Build (Vault + Forge)**
   Vault and Forge operate ONLY within the change-plan scope.
   Any deviation from the scope is flagged to Conductor before proceeding.

   **Phase: Verification (Sentinel + Warden)**
   Sentinel tests:
   - The new/modified functionality works as specified
   - Regression: everything in the "NOT touched" list still works

5. On completion, remind the user to test in the existing environment before
   exporting the updated managed solution.
