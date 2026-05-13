# /sn-start — Start a New Project

## Purpose

Bootstrap a new SimplifyNext Power Platform project. Captures configuration,
initialises state, and invokes Scout to gather requirements.

## Usage

```
/sn-start
/sn-start --project "Expense Tracker" --prefix "exp"
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--project` | No | Project display name (prompted if omitted) |
| `--prefix` | No | Publisher prefix 2-8 chars (prompted if omitted) |
| `--env` | No | Environment URL (prompted if omitted) |

## Process

### Step 1 — Check for Existing State
Read `.sn/state.json` if it exists. If `phase` is set and not `discovery`,
warn: "A project is already in progress (phase: {phase}). Run /sn-status to
see current state. Use /sn-start --force to reset."

### Step 2 — Gather Configuration
If arguments not provided, ask the user:

```
1. What is the project name?
   (This becomes the solution display name)

2. What publisher prefix should I use? (2-8 lowercase letters)
   Examples: exp, hr, ops, fin, con
   Tip: Use 2-3 letters from the project or client name.

3. What is your environment URL?
   Format: https://<org>.crm.dynamics.com

4. What is the publisher display name?
   (e.g. "SimplifyNext Solutions", "Contoso Internal")
```

### Step 3 — Initialise State
Create `.sn/` directory if it doesn't exist.
Write `.sn/state.json`:

```json
{
  "project": "<project name>",
  "publisher_prefix": "<prefix>",
  "publisher_name": "<display name>",
  "solution_name": "<prefix>_<ProjectName>",
  "environment": "<org-url>",
  "phase": "discovery",
  "created_at": "<ISO timestamp>",
  "components": {}
}
```

Initialise `.sn/execution-log.jsonl` with first entry:
```json
{"timestamp": "...", "agent": "conductor", "event": "project_started", "phase": "discovery"}
```

### Step 4 — Load Context (if available)
Check for `context/` folder or `.sn/context-summary.md`.
If found, load into Scout's briefing.

### Step 5 — Invoke Scout
Brief Scout with:
- The project name and any context documents
- Instructions to write `docs/requirements.md`
- The publisher prefix from state.json

### Step 6 — Report
After Scout completes, show the user:
```
Project initialised: {project name}
Publisher prefix: {prefix}
Environment: {env url}
Requirements written to: docs/requirements.md

Next: Review requirements, then run /sn-status or approve to continue.
```

## Files Created

- `.sn/state.json`
- `.sn/execution-log.jsonl`
- `docs/requirements.md` (by Scout)

## Error Handling

- Invalid prefix (not 2-8 lowercase letters): re-prompt with validation message
- Invalid environment URL (not matching `https://*.dynamics.com`): warn but allow
- Missing `docs/` directory: create it automatically
