---
description: Start a new Relay project. Scaffolds the project folder structure and begins discovery with Scout.
trigger_keywords:
  - relay start
  - new project
  - start relay
  - begin project
---

# /relay:start

## Step 0a — Prerequisite Check (FIRST — before anything else)

Before creating any files or asking any questions, resolve the Relay plugin root once:

```powershell
$relayRoot = (Get-Location).Path

if (-not (Test-Path (Join-Path $relayRoot "scripts\relay-prerequisite-check.py"))) {
    $relayScript = Get-ChildItem -Path (Join-Path $env:USERPROFILE ".copilot") -Recurse -Filter relay-prerequisite-check.py -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($relayScript) {
        $relayRoot = Split-Path $relayScript.DirectoryName -Parent
    }
}

if (-not (Test-Path (Join-Path $relayRoot "scripts\relay-prerequisite-check.py"))) {
    throw "Could not locate the Relay plugin root. Ensure Relay is available locally before running /relay:start."
}
```

Before creating any files or asking any questions, run the prerequisite check:

```powershell
$env:PYTHONUTF8 = "1"
python (Join-Path $relayRoot "scripts\relay-prerequisite-check.py")
```

**If the gate returns exit code 1 (critical failures):**
- Show the user the full output
- Do NOT proceed to scaffolding
- Offer to run with `--fix` to attempt auto-remediation:
  ```powershell
  python (Join-Path $relayRoot "scripts\relay-prerequisite-check.py") --fix
  ```
- After fixes, re-run the check. Only proceed when gate returns exit 0.

**If the gate returns exit code 0 (all critical checks pass):**
- Show the summary to the user (especially any non-critical warnings)
- Proceed to Step 0b

## Step 0b — Initialise project files

After prerequisites pass, run these commands:

```powershell
# Create .relay/ folder
New-Item -ItemType Directory -Force -Path .relay | Out-Null
New-Item -ItemType Directory -Force -Path docs | Out-Null
New-Item -ItemType Directory -Force -Path src | Out-Null

# Initialise state.json
$state = @{
    project_name = ""
    publisher_prefix = ""
    environment_url = ""
    solution_name = ""
    phase = "discovery"
    mode = "greenfield"
    plan_checksum = $null
    security_design_checksum = $null
    approvals = @{}
    components = @{
        app_modules = @{}
        security_roles = @{}
        fls_profiles = @{}
        connection_references = @{}
    }
} | ConvertTo-Json -Depth 5
Set-Content -Path ".relay/state.json" -Value $state

# Copy the canonical plan-index scaffold from the Relay plugin root
$planIndexSource = Join-Path $relayRoot "schemas\plan-index.schema.json"
if (-not (Test-Path $planIndexSource)) {
  throw "Canonical plan-index scaffold not found at $planIndexSource"
}
Copy-Item -Path $planIndexSource -Destination ".relay/plan-index.json" -Force

# Initialise execution log
Set-Content -Path ".relay/execution-log.jsonl" -Value ""

Write-Host "Project files initialised"
```

Verify the files were created before proceeding:
```powershell
ls .relay/
# Should show: state.json, plan-index.json, execution-log.jsonl
```

Validate the Phase 0 scaffold before invoking Scout:
```powershell
python (Join-Path $relayRoot "scripts\relay-gate-check.py") --phase 0
```

Log the initialisation:
```python
import json, datetime
entry = {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "agent": "conductor", "event": "project_initialised", "phase": "0"}
with open(".relay/execution-log.jsonl", "a") as f: f.write(json.dumps(entry) + "\n")
```

Only AFTER files are created — invoke Scout for discovery.

When the user invokes this command:

1. Check if `.relay/state.json` already exists in the current directory.
  - If yes AND `context_loaded` is `true`: proceed normally — merge the existing state with the Phase 0 scaffold above. Read `.relay/context-summary.md` and pass it to Scout.
   - If yes AND `phase` is any other value: refuse: "This folder already has an active Relay project at phase '<phase>'. Run `/relay:status` to see where you are, or delete `.relay/state.json` to start fresh."

2. Use the Phase 0 scaffold above as the canonical state shape and keep `phase` within this set only:
  `discovery`, `planning`, `review`, `adversarial`, `build`, `verify`, `complete`.

3. Ask the user for a one-paragraph project brief. Explain:
   "Give me a one-paragraph brief describing what you want to build. Include: who will use it (personas), what they need to do, and any security-sensitive data. I'll hand this to Scout for discovery."

4. Once the user provides the brief, invoke Scout with the brief text.
