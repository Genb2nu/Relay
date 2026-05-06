---
description: |
  Inspect an existing Power Platform solution. Maps all components, runs
  security and quality analysis, and produces a comprehensive audit report.
  Strictly read-only during inspection. Fix phase is opt-in after the report
  is reviewed by the user.
trigger_keywords:
  - relay inspect
  - inspect solution
  - inspect existing
  - analyse and fix
  - audit and fix
---

# /relay:inspect

## Overview

Inspect is a two-phase operation:

1. **Inspect Phase (Phases 1–6)** — strictly read-only. Discovers, analyses, and reports.
2. **Fix Phase (Phases 7–9)** — opt-in only, started only after user reviews and approves.

**During Phases 1–6: no CREATE, UPDATE, or DELETE operations to any Dataverse table, flow, app,
web resource, or Power Pages component. If any agent attempts a write, Conductor MUST stop it.**

---

## Phase 1 — Intake

### Step 1a: Auth Selection

Before anything else, discover and confirm the correct account and environment.

```powershell
pac auth list
pac org who
```

Present all authenticated profiles clearly:

```
Authenticated profiles:
[1] * john@contoso.com    → Contoso Dev    https://contoso-dev.crm.dynamics.com
[2]   test@contoso.com    → Contoso Dev    (test account — may lack admin roles)
[3]   john@fabrikam.com   → Fabrikam Prod  https://fabrikam.crm.dynamics.com

Currently active: [1] john@contoso.com → Contoso Dev
```

**If ONE profile:**
"You are authenticated as `<account>` → `<env name>`. Is this the correct environment? [Yes / No]"
- If No: "Please run `pac auth select --index <n>` to switch, then re-run `/relay:inspect`." Stop.
- If Yes: proceed.

**If MULTIPLE profiles:**
"Multiple accounts are authenticated. Which one should Relay use for this inspection? Enter the index.
Note: the account needs **System Administrator** or **System Customizer** role to read all solution components."
- Run: `pac auth select --index <n>`
- Confirm: `pac org who` — display the new active profile

### Step 1b: Solution Selection

```powershell
pac solution list
```

Show the list of solutions. If the user passed a solution name as an argument, confirm it matches.
Otherwise ask: "Which solution do you want to inspect? Enter the unique name."

### Step 1c: inspect-context/ Folder

Check if `inspect-context/` exists in the current working directory.

**If it does NOT exist — create it and present to user:**
```
✅ Created: inspect-context/
   Path: <full path to inspect-context/>

Drop any relevant documents here before I begin analysis:
  • Module design docs, business requirements, user stories
  • Architecture notes, existing test plans, process flows
  • Any file that explains what this solution is meant to do
  Formats accepted: .md .txt .docx .pdf .xlsx .csv .png .jpg

Do you have documents to add?
[Yes — I'm dropping files now]  [Skip — proceed without context]
```

**If it already exists:** list its contents and ask:
"I found these files in inspect-context/: <list>. Use them? Or add more before proceeding?
[Use existing files]  [I'm adding more now]  [Skip — ignore folder]"

Wait for user response.

**Reading documents (if provided):**
- Markdown / text / .txt → full content
- PDF / Word (.docx) → extract text content
- Excel / CSV → structure and key data summary
- Images (.png .jpg) → describe what you see (wireframes, diagrams, screenshots)

Distil all document content into `docs/project-context.md`:

```markdown
# Project Context — <Solution Name>

## Source
- Context mode: provided | inferred
- Documents loaded: <list of filenames>

## Purpose
<2-3 sentences: what this solution does>

## Intended Users / Personas
- <persona 1>: <what they do>
- <persona 2>: <what they do>

## Key Entities / Data
<list of main tables/entities mentioned>

## Key Processes
<list of business processes or workflows mentioned>

## Known Constraints / Sensitive Data
<security requirements, compliance notes, sensitive columns mentioned>

## Gaps (not covered by documents)
<what a complete spec would include that isn't in the provided docs>
```

**If user skips:** write `docs/project-context.md` with `context_mode: inferred`.
All downstream agents will flag more conservatively and note when findings are inferred.

### Step 1d: Initialise State

Create `.relay/` and `docs/` folders if they don't exist.

Write `.relay/state.json`:
```json
{
  "mode": "inspect",
  "phase": "intake",
  "solution_name": "<confirmed unique name>",
  "environment_url": "<confirmed org URL>",
  "pac_auth_account": "<confirmed account email>",
  "pac_auth_index": <confirmed index number>,
  "context_loaded": <true | false>,
  "snapshot_taken": false
}
```

Log to `.relay/execution-log.jsonl`:
```python
import json, datetime
entry = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "agent": "conductor",
    "event": "inspect_started",
    "solution": "<solution_name>",
    "account": "<pac_auth_account>",
    "environment_url": "<environment_url>"
}
```

---

## Phase 2 — Analysis

Update `state.json` `phase` → `"analysis"`. Invoke **Analyst**.

Tell Analyst:
- Solution name to discover
- Reference `docs/project-context.md` for context-enriched observations
- Produce `docs/existing-solution.md`

Wait for Analyst to complete.

---

## Phase 3 — Security Audit

Update `state.json` `phase` → `"security"`. Invoke **Warden**.

Warden reads `state.json`, detects `mode: inspect`, runs Mode C.
Warden writes security findings to `docs/audit-report.md` (security section).

Wait for Warden to complete.

---

## Phase 4 — Quality Review

Update `state.json` `phase` → `"review"`. Invoke **Critic**.

Critic detects `docs/existing-solution.md` exists and `docs/plan.md` does NOT exist → runs No-Plan Mode.
Critic writes checklist and anti-pattern findings to `docs/audit-report.md`.

Wait for Critic to complete.

---

## Phase 5 — Probing

Update `state.json` `phase` → `"probing"`. Invoke **Sentinel**.

Sentinel reads `state.json`, detects `mode: inspect`, runs Lite Mode (GET-only probes).
Sentinel writes `docs/test-probe-report.md` and feeds findings to `docs/audit-report.md`.

Wait for Sentinel to complete.

---

## Phase 6 — Report Synthesis

Update `state.json` `phase` → `"report"`.

Consolidate all findings from Phases 3–5 into final `docs/audit-report.md`:

```markdown
# Inspection Report — <Solution Name>
Generated: <date> | Environment: <org URL> | Account: <account>
Context: provided | inferred

## Executive Summary
<3–4 sentences: purpose, overall health, top concern>

## Health Score: [A / B / C / D]
A = production-ready, minor notes only
B = production-ready, improvements recommended
C = significant issues requiring attention before next release
D = critical issues requiring immediate action

## Risk Summary
| Severity    | Count |
|---|---|
| 🔴 Critical | <N>   |
| 🟡 Major    | <N>   |
| 🔵 Minor    | <N>   |
| ✅ Pass     | <N>   |

---

## What Is Working Well
<Genuine positives — good security practices, clean schema, active flows, etc.>

---

## Critical Findings (fix before production)

### [CRIT-001] <Issue title>
- **Category**: Security | Technical | Functional | ALM | Performance
- **Finding**: <what is wrong>
- **Evidence**: <specific component — table name, flow name, column name>
- **Risk**: <what happens if not fixed>
- **Remediation**: <exact steps>
- **Fix agent**: Vault | forge-flow | forge-canvas | forge-mda | forge-pages
- **Effort**: S (< 1 hr) | M (1–4 hr) | L (> 4 hr)

---

## Major Findings

### [MAJ-001] ...

---

## Minor Findings / Recommendations

### [MIN-001] ...

---

## Security Findings
<from Warden Mode C>

## Quality & Design Findings
<from Critic No-Plan Mode — checklist results + anti-patterns>

## Sentinel Probe Results
<from Sentinel Lite — probe table>

---

## Remediation Roadmap

| Priority | ID | Title | Agent | Effort | Risk if deferred |
|---|---|---|---|---|---|
| 1 | CRIT-001 | <title> | Vault | M | Data leak |
| 2 | CRIT-002 | <title> | forge-flow | S | Silent data loss |
...

---

## Appendix

### Full Component Inventory
<from docs/existing-solution.md — tables, flows, apps, roles, plugins>

### Solution Checker Raw Output
<from pac solution check — parsed by Analyst>
```

Present summary to user in terminal:

```
✅ Inspection complete — <Solution Name>

Health Score: [A/B/C/D]
🔴 Critical: <N>  🟡 Major: <N>  🔵 Minor: <N>  ✅ Pass: <N>

Top risks:
1. <risk 1>
2. <risk 2>
3. <risk 3>

Full report → docs/audit-report.md
Probe report → docs/test-probe-report.md

Would you like to address any of these findings?
[Yes — start fix phase]  [No — report only]
```

If user selects **No — report only**: done. `state.json` phase → `"complete"`.

---

## ─── HARD BOUNDARY — PHASES 1–6 WERE STRICTLY READ-ONLY ───
## ─── FIX PHASE STARTS ONLY ON EXPLICIT USER CONSENT ─────────

---

## Phase 7 — Snapshot

Update `state.json` `phase` → `"snapshot"`. Invoke **Mender** in snapshot mode.

Mender captures before-state for every component that will be touched:

**Level 1 — Solution snapshot (nuclear rollback):**
```powershell
New-Item -ItemType Directory -Force -Path "docs/snapshots" | Out-Null
pac solution export --name <SolutionName> `
    --path "docs/snapshots/solution-backup-$(Get-Date -Format 'yyyyMMdd-HHmm').zip" `
    --managed false --overwrite
```

**Level 2 — Per-component snapshots (surgical rollback):**
- Canvas apps: `pac canvas download --app-id <id>` → `docs/snapshots/canvas/<AppName>-<ts>.msapp`
- Canvas App Checker state: MCP `get_appchecker_errors` → `docs/snapshots/canvas/appchecker-before.json`
- Flows: Dataverse `GET /workflows(<id>)` → `docs/snapshots/flows/<FlowName>.json`
- Web resources: Dataverse `GET /webresourceset(<id>)?$select=content,name` → `docs/snapshots/mda/<name>`
- Power Pages: `pac pages download` → `docs/snapshots/pages/`
- Security roles: `pac solution export` scoped → `docs/snapshots/security/roles-before.zip`

Over-capture is intentional. Canvas snapshots include the entire screen's YAML — not just the
broken control — because formulas cross-reference each other.

After all snapshots captured: `state.json` `snapshot_taken` → `true`.

---

## Phase 8 — Fix Loop

Update `state.json` `phase` → `"fixing"`. Invoke **Mender** in fix mode.

Mender presents each finding and routes approved fixes to the right specialist.

---

## Phase 9 — Fix Verification

Update `state.json` `phase` → `"verifying"`. Invoke **Mender** in verify mode.

Mender re-runs Sentinel Lite probes and compile checks.

**Regression gate:** Any Sentinel Lite probe that PASSED in Phase 5 and now FAILS = STOP.
Conductor presents rollback options before proceeding.

Output: `docs/fix-verification-report.md`

On successful verification: `state.json` `phase` → `"complete"`.
