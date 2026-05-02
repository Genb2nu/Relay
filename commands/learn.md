---
description: |
  Extracts patterns from a completed project's execution log and proposes
  additions to Relay skill files. Learns from what worked and what failed
  so the squad improves with every project. Run after Phase 7 (complete).
trigger_keywords:
  - relay learn
  - extract patterns
  - update skills
  - feedback loop
---

# /relay:learn

When the user invokes this command, extract patterns from the completed project and propose skill additions.

## Step 1 — Check preconditions

```powershell
$state = Get-Content ".relay/state.json" | ConvertFrom-Json
if ($state.phase -ne "complete") {
    Write-Host "/relay:learn only runs after a project finishes."
    Write-Host "Current phase: $($state.phase)"
    exit
}
```

If the project phase is not "complete", inform the user and stop.

## Step 2 — Read sources (with fallback)

**Primary source:** Read `.relay/execution-log.jsonl`
Look for events with these types:
- `pattern_discovered`
- `issue_found`
- `component_created`
- `approval_given`

**Fallback (if log is empty or has no structured pattern events):**
Read these files and extract patterns manually:
- `docs/plan.md` — new patterns in schema design, flow architecture, security
- `docs/critic-report.md` — issues found = potential footgun additions
- `docs/security-design.md` — security patterns identified
- `docs/test-report.md` — test findings and edge cases

## Step 3 — Extract and deduplicate patterns

Pattern types and their target skills:

| Pattern type | Target skill file |
|---|---|
| Power Fx patterns | `skills/power-fx-patterns/SKILL.md` |
| Flow/ALM patterns | `skills/power-platform-alm/SKILL.md` |
| Security patterns | `skills/power-platform-security-patterns/SKILL.md` |
| New footgun items | `skills/power-platform-footgun-checklist/SKILL.md` |
| Canvas App patterns | `skills/canvas-app-design-patterns/SKILL.md` |

**Before proposing any pattern:**
1. Read the target skill file
2. Check if the pattern already exists (same concept, even if different wording)
3. Skip if already documented — do not propose duplicates

## Step 4 — Present proposals to user (one at a time)

Format each proposal like this:

```
/relay:learn found N new patterns from this project:

[1] <Pattern type>
    <Concise pattern description or code snippet>
    Suggested addition to: <target skill file path>
    Context: <Why this pattern is useful — one line>
    Add? yes / no / edit

[2] ...
```

Wait for user response on each proposal before proceeding.
Accept responses: "yes", "no", "skip", or "edit [new text]".

## Step 5 — Apply approved patterns

For each "yes" — append the pattern to the relevant skill file under an appropriate section heading.
For each "edit [text]" — use the user's edited version instead.
For "no" or "skip" — skip silently.

**Never add:**
- Project-specific values (table names with specific prefixes, GUIDs, org URLs)
- Patterns that are environment-specific (specific tenant IDs, user emails)
- Patterns that already exist in the skill

**Always generalise:** Replace specific prefixes with `<prefix>_`, specific table names with `<table_logical_name>`, specific URLs with `<org-url>`.

## Step 6 — Write learn-report.md

After all proposals are processed, write `docs/learn-report.md`:

```markdown
# Learn Report

**Project:** [name from state.json]
**Date:** [today's date]
**Patterns found:** N
**Patterns added:** X
**Patterns skipped:** Y
**Skills updated:**
- [list of skill files that were modified]

## Patterns Added

[For each added pattern: one-line summary + target skill]

## Patterns Skipped

[For each skipped pattern: one-line summary + reason (duplicate / rejected / environment-specific)]
```
