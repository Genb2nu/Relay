---
name: relay-debugging
description: |
  Systematic root cause diagnosis for Power Platform bugs. Used by Critic
  in /relay:bugfix mode to diagnose before Drafter fixes. Traces the full
  execution path, identifies root cause, eliminates alternative causes.
  Adapted from Superpowers systematic-debugging — no external dependency required.
trigger_keywords:
  - debug
  - bug
  - not working
  - error
  - broken
  - something wrong
  - diagnosing
  - root cause
  - critic diagnosis
allowed_tools:
  - Read
  - Bash
  - Write
---

# Relay Debugging — Systematic Root Cause Analysis

Adapted from Superpowers systematic-debugging for Power Platform.
Critic uses this in /relay:bugfix mode before Drafter writes a fix plan.

## Core Principle

Never propose a fix without understanding the root cause.
A fix aimed at the symptom creates a new bug.
A fix aimed at the root cause solves the problem permanently.

## Anti-Pattern: Fix Before Diagnosis

```
❌ Wrong: "The flow isn't sending emails. Let me add a retry action."
✅ Right: "The flow isn't sending emails.
          Step 1: Check if flow runs (run history).
          Step 2: If it runs but email fails — check connection reference identity.
          Step 3: If identity is correct — check DLP policy on Outlook connector.
          Root cause: DLP policy blocks Outlook in this environment.
          Fix: Add Outlook to the allowed business connectors list."
```

## The Execution Path Trace

For any Power Platform bug, trace the FULL execution path from trigger to symptom:

### Flow bugs
```
1. What triggers the flow? (row added, modified, manual, scheduled)
2. Does the trigger fire? (check run history in Power Automate)
3. If trigger fires: which step fails? (check run history error details)
4. At the failing step:
   - What connector is being used?
   - What connection reference is it using?
   - What identity does that connection run as?
   - Is there a DLP policy that could block it?
   - Is the data coming into this step correct?
5. What is the exact error message?
```

### Plugin bugs
```
1. What operation triggers the plugin? (Create/Update/Delete on which table)
2. At which stage? (Pre-Operation = before DB write, Post-Operation = after)
3. Is the plugin registered correctly? (check pluginassemblies + sdkmessageprocessingsteps)
4. Is it throwing an exception? (check system jobs or plugin trace log)
5. If blocking an operation — is the error message reaching the user?
6. Pre-image: were the required pre-image attributes registered?
```

### Canvas App bugs
```
1. Which screen is affected?
2. Which control is misbehaving?
3. What is the control's formula? (check .pa.yaml or Power Apps Studio)
4. Is it a delegation issue? (check for yellow warning triangles)
5. Is it a data type mismatch? (lookup vs text, choice vs number)
6. Is the formula referencing a column name that doesn't match the logical name?
7. Is the current user filter correct? (Employee.'Primary Email' = User().Email)
```

### Security / access bugs
```
1. Which user is affected?
2. What is the exact error? ("You don't have permission" or "No records found")
3. What security roles does this user have?
4. What is the privilege scope of the relevant role? (User / BU / Org)
5. Is there an FLS profile that might be blocking the column?
6. Is this a UI-security-trap? (record exists but hidden via JS/Business Rule)
7. Is the Business Unit hierarchy correct?
```

### MDA / Canvas App data not showing
```
1. Does the data exist in Dataverse? (query directly via Dataverse MCP)
2. If yes — is the view filter too restrictive?
3. Is the user's security role scoped correctly for their BU?
4. Is there a Personal View overriding the System View?
5. For Canvas App: is the Filter() formula delegable on this column?
```

## Footgun Pattern Matching

Check the footgun checklist before concluding root cause.
Many Power Platform bugs are well-known anti-patterns:

| Symptom | Likely footgun |
|---|---|
| Flow runs but email fails | Connection reference using maker identity |
| Flow creates race condition | Missing sequential concurrency |
| Status can't be changed via API | Missing FLS override profile |
| Canvas filter shows no results | Non-delegable filter on large table |
| Self-approval not blocked | Plugin not registered as Pre-Operation Sync |
| Flow triggers on own changes | Missing infinite loop prevention condition |
| Form field changes don't save | Business Rule conflict with code |
| Plugin runs but no effect | Wrong execution stage (Post instead of Pre) |
| Balance goes negative | Missing concurrency control on balance update flow |

## Elimination Protocol

After identifying the probable root cause, eliminate alternatives:

```
Root cause hypothesis: DLP policy blocks Outlook connector

Alternative causes to eliminate:
A) Connection reference not linked → Check: connection reference shows a connection ✅ eliminated
B) User has no Outlook license → Check: user can send email manually ✅ eliminated  
C) Flow uses wrong connection reference → Check: flow definition shows cr_OutlookConnection ✅ eliminated

Conclusion: DLP policy is the only remaining explanation.
```

## Bug Diagnosis Document

Write `docs/bug-diagnosis.md`:

```markdown
# Bug Diagnosis — <description>

## Symptom
<What the user reported, verbatim>

## Execution path analysis
1. Trigger: <what should trigger the behaviour>
2. Step 2: <next step>
3. Failure point: <where it goes wrong and why>

## Root cause
<One clear statement of the actual problem>

## Evidence
<What was checked and what it showed>

## Alternatives eliminated
| Alternative | How eliminated |
|---|---|
| | |

## Recommended fix approach
<Direction for Drafter — NOT the implementation>

## Components involved (touch these)
| Component | Role in bug |
|---|---|

## Components NOT involved (do not touch)
| Component | Why safe to leave |
|---|---|

## Expected outcome after fix
<How to verify the fix worked>
```

## Minimal Fix Principle

Once root cause is confirmed, the fix must be:
- As small as possible
- Targeted at the root cause only
- Not an opportunity to "improve while we're in here"

If the fix reveals a related issue — document it separately. Don't fix two things at once.
