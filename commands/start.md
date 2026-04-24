---
description: Start a new Relay project. Scaffolds the project folder structure and begins discovery with Scout.
trigger_keywords:
  - relay start
  - new project
  - start relay
  - begin project
---

# /relay:start

## Step 0 — Initialise project files (FIRST — before anything else)

Before invoking Scout or asking any questions, run these commands:

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

# Copy plan-index schema as starting plan-index.json
# Read from plugin root if available, otherwise create minimal version
$planIndex = @{
    version = "1.0"
    project = @{ name = ""; solution = ""; publisher_prefix = ""; environment = "" }
    phase_gates = @{
        phase1_discovery = @{ passed = $false; validated_at = $null; persona_count = 0; user_story_count = 0; entity_count = 0 }
        phase2_planning = @{ passed = $false; validated_at = $null; plan_md_exists = $false; security_design_md_exists = $false; all_entities_have_columns = $false; all_flows_have_error_handling = $false; decision_needed_count = 0 }
        phase3_review = @{ passed = $false; auditor_approved = $false; warden_approved = $false; auditor_issues_found = 0; auditor_issues_resolved = 0; warden_issues_found = 0; warden_issues_resolved = 0 }
        phase4_adversarial = @{ passed = $false; critic_approved = $false; checklist_items_total = 0; checklist_items_passed = 0; blocking_issues_found = 0; blocking_issues_resolved = 0; plan_locked = $false; plan_checksum = $null; security_design_checksum = $null }
        phase5_build = @{ passed = $false; vault_complete = $false; stylist_complete = $false; forge_complete = $false; components_built = @(); components_partial = @(); components_blocked = @() }
        phase6_verify = @{ passed = $false; sentinel_approved = $false; warden_approved = $false; security_tests_passed = 0; security_tests_failed = 0; drift_detected = $false; drift_items = @() }
    }
    components = @{ tables = @(); flows = @(); canvas_apps = @(); model_driven_apps = @(); plugins = @(); security_roles = @(); fls_profiles = @(); connection_references = @(); environment_variables = @() }
    scores = @{ plan_completeness = $null; security_coverage = $null; testability = $null; overall = $null; scored_at = $null }
    approved_by = @()
    decisions = @()
} | ConvertTo-Json -Depth 10
Set-Content -Path ".relay/plan-index.json" -Value $planIndex

# Initialise execution log
Set-Content -Path ".relay/execution-log.jsonl" -Value ""

Write-Host "Project files initialised"
```

Verify the files were created before proceeding:
```powershell
ls .relay/
# Should show: state.json, plan-index.json, execution-log.jsonl
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
   - If yes, refuse: "This folder already has an active Relay project at phase '<phase>'. Run `/relay:status` to see where you are, or delete `.relay/state.json` to start fresh."

2. Create the project folder structure:
   ```
   docs/
   src/
   .relay/
   ```

3. Write `.relay/state.json` with initial state:
   ```json
   {
     "project_name": "",
     "phase": "discovery",
     "last_updated": "<ISO timestamp>",
     "artifacts": {
       "requirements": null,
       "plan": null,
       "security_design": null,
       "critic_report": null,
       "test_report": null,
       "security_test_report": null
     },
     "approvals": {},
     "plan_checksum": null,
     "security_design_checksum": null,
     "config": {
       "enforcement_mode": "advisory"
     }
   }
   ```

4. Ask the user for a one-paragraph project brief. Explain:
   "Give me a one-paragraph brief describing what you want to build. Include: who will use it (personas), what they need to do, and any security-sensitive data. I'll hand this to Scout for discovery."

5. Once the user provides the brief, invoke Scout with the brief text.
