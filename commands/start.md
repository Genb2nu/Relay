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
- Proceed to Step 0c

## Step 0c — Auth Selection

Before scaffolding any files, confirm the correct PAC CLI account and environment.

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
Ask: "You are authenticated as `<account>` → `<env name>`. Is this the correct environment for this project? [Yes / No]"
- If **No**: "Please run `pac auth select --index <n>` to switch, then re-run `/relay:start`." Stop here.
- If **Yes**: proceed.

**If MULTIPLE profiles:**
Ask: "Multiple accounts are authenticated. Which one should Relay use for this project? Enter the index number.
Note: the account needs **System Administrator** or **System Customizer** role — test-only accounts will fail during schema deployment."
- Run: `pac auth select --index <n>`
- Confirm: run `pac org who` again and display the new active profile

After confirmation, store the confirmed values — they will be written to `state.json` in Step 0b:
- `environment_url` → the confirmed org URL
- `pac_auth_account` → the confirmed account email

Log to `.relay/execution-log.jsonl` (create the file if needed):
```python
import json, datetime
entry = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "agent": "conductor",
    "event": "auth_confirmed",
    "account": "<confirmed_account>",
    "org_url": "<confirmed_org_url>"
}
# append to .relay/execution-log.jsonl (create .relay/ dir first if needed)
```

Then proceed to Step 0b.

## Step 0b — Initialise project files

After prerequisites pass, if you are creating a fresh scaffold (new project or user chose Reset), run these commands:

```powershell
# Create .relay/ folder
New-Item -ItemType Directory -Force -Path .relay | Out-Null
New-Item -ItemType Directory -Force -Path docs | Out-Null
New-Item -ItemType Directory -Force -Path src | Out-Null

# Initialise state.json from the canonical Relay state schema
$stateSchemaPath = Join-Path $relayRoot "schemas\state.schema.json"
if (-not (Test-Path $stateSchemaPath)) {
  throw "Canonical state schema not found at $stateSchemaPath"
}

$stateSchema = Get-Content -Path $stateSchemaPath -Raw | ConvertFrom-Json -Depth 20

function New-RelayStateValue {
  param([object]$Schema)

  if ($Schema.PSObject.Properties.Name -contains "enum") {
    return $Schema.enum[0]
  }

  $types = @()
  if ($Schema.PSObject.Properties.Name -contains "type") {
    if ($Schema.type -is [System.Array]) {
      $types = @($Schema.type)
    } else {
      $types = @($Schema.type)
    }
  }

  if ($types -contains "null") {
    return $null
  }

  if ($types -contains "object") {
    $value = [ordered]@{}
    if ($Schema.PSObject.Properties.Name -contains "properties") {
      foreach ($property in $Schema.properties.PSObject.Properties) {
        $value[$property.Name] = New-RelayStateValue -Schema $property.Value
      }
    }
    return $value
  }

  if ($types -contains "array") {
    return @()
  }

  if ($types -contains "boolean") {
    return $false
  }

  return ""
}

$state = New-RelayStateValue -Schema $stateSchema | ConvertTo-Json -Depth 10
Set-Content -Path ".relay/state.json" -Value $state

# Immediately write the confirmed auth values from Step 0c
$stateObj = Get-Content ".relay/state.json" | ConvertFrom-Json
$stateObj.environment_url = "<org_url confirmed in Step 0c>"
$stateObj.pac_auth_account = "<account confirmed in Step 0c>"
$stateObj | ConvertTo-Json -Depth 10 | Set-Content ".relay/state.json"

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
  - If no: run Step 0c, then Step 0b once, then continue.
  - If yes: read `.relay/state.json` and show the user the current `project_name`, `solution_name`, `phase`, and `context_loaded` state.
  - Offer exactly three choices before making any changes:
    - `Resume`: keep the existing `.relay/` files and do NOT run Step 0b again.
      - If `phase` is `discovery` and `.relay/context-summary.md` exists or `context_loaded` is `true`, read `.relay/context-summary.md` and use it as Scout's starting brief.
      - Otherwise continue the active Relay project from its current phase instead of starting a new one.
    - `Reset`: archive the existing `.relay/` folder to `.relay.backup-<timestamp>`, then run Step 0b to create a fresh scaffold.
    - `Cancel`: stop with no file changes.
  - Never delete or overwrite an existing `.relay/` state unless the user explicitly chooses `Reset`.

2. Use the schema-backed Phase 0 scaffold above as the canonical state shape and keep `phase` within this set only:
  `discovery`, `planning`, `review`, `adversarial`, `build`, `verify`, `complete`.

3. Determine Scout's starting input.
   - If `.relay/context-summary.md` exists or `context_loaded` is `true`, do NOT ask the user to restate the project brief. Read the summary first and pass it to Scout. Only ask the user for a short addendum if they want to add new goals or constraints since `/relay:load`.
   - Otherwise ask the user for a one-paragraph project brief. Explain:
     "Give me a one-paragraph brief describing what you want to build. Include: who will use it (personas), what they need to do, and any security-sensitive data. I'll hand this to Scout for discovery."

4. Invoke Scout with either:
   - the `.relay/context-summary.md` contents plus any user addendum, or
   - the one-paragraph brief from Step 3.
   - Explicitly tell Scout that the user is authorizing it to update `.relay/state.json` and create `docs/requirements.md` as required Relay discovery artifacts.

5. After Scout returns, verify `docs/requirements.md` exists.
   - If Scout returned full requirements content in the response but `docs/requirements.md` is missing, write that markdown to `docs/requirements.md` yourself.
   - When you use this fallback, append a JSONL event to `.relay/execution-log.jsonl` with `agent: "conductor"`, `event: "requirements_fallback_written"`, and a UTC timestamp so the recovery is traceable.
   - Apply any explicit `.relay/state.json` updates Scout returned (at minimum `publisher_prefix` and `environment_url`) if Scout described them but did not persist them.
   - Do not treat discovery as complete until `docs/requirements.md` exists.
