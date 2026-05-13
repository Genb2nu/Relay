# /sn-deploy — Export and Deploy Solution

## Purpose

Export the solution from the development environment and deploy it to target
environments (test, production). Uses PAC CLI for all operations.

## Usage

```
/sn-deploy --env test
/sn-deploy --env prod
/sn-deploy --export-only
/sn-deploy --env test --managed
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--env` | Yes (unless --export-only) | Target environment name or URL |
| `--managed` | No | Deploy as managed solution (default: true for test/prod) |
| `--export-only` | No | Export to file but do not import |
| `--version` | No | Set solution version (e.g. `1.0.0.5`) |
| `--checklist` | No | Print deployment checklist without deploying |

## Pre-conditions

- `state.json.sentinel_approved = true` (QA gate passed)
- If not: "QA gate has not passed. Run /sn-qa first."
- Auth must be valid for both source and target environments

## Process

### Step 1 — Print Deployment Checklist (mandatory)

Always show this checklist before deploying:

```
=== Pre-Deployment Checklist ===

Development environment:
  [ ] QA gate passed (sentinel_approved = true)
  [ ] All flows are active in dev
  [ ] Canvas App passes App Checker at 0 errors
  [ ] MDA is published
  [ ] No unmanaged layers from Default Solution

Target environment ({env}):
  [ ] Publisher exists with matching prefix: {publisher_prefix}
  [ ] Connection references created for target env connections
  [ ] Environment variables have target values configured
  [ ] System Administrator / System Customizer access confirmed
  [ ] Backup of current managed solution taken (if upgrading)

Confirm all items before proceeding. (yes/no)
```

If `--checklist` flag: print and exit without deploying.

### Step 2 — Export Solution

```powershell
# Set solution version if provided
if ($version) {
  pac solution version --solutionName $solutionName --patchVersion $version
}

# Export unmanaged (always export unmanaged first for source control)
pac solution export `
  --name $solutionName `
  --path "dist/{solutionName}_unmanaged.zip" `
  --managed false `
  --environment $devEnv

# Export managed (for deployment)
pac solution export `
  --name $solutionName `
  --path "dist/{solutionName}_managed.zip" `
  --managed true `
  --environment $devEnv
```

If `--export-only`: stop here and report paths to exported files.

### Step 3 — Import to Target

```powershell
pac solution import `
  --path "dist/{solutionName}_managed.zip" `
  --environment $targetEnv `
  --async `
  --force-overwrite
```

Monitor import progress:
```powershell
do {
  Start-Sleep -Seconds 10
  $status = pac solution import-status --environment $targetEnv
} while ($status -match "Processing")
```

### Step 4 — Post-Import Configuration

After import, prompt user for:

```
Post-import steps required on {env}:

  1. Wire connection references:
     Each flow that uses connections needs the target env connection linked.
     
     Connection references to wire:
     - ops_DataverseConnection → [select Dataverse connection in {env}]
     - ops_OutlookConnection   → [select Outlook connection in {env}]
  
  2. Set environment variable values:
     - ops_ApprovalTimeout: current value = 48 (update if different for {env})
     - ops_EscalationEmail: set to the target environment contact
  
  3. Activate flows:
     Flows import as disabled. After wiring connections, activate each:
     - OpsApprovalFlow
     - OpsReminderFlow
  
  Run /sn-status to check deployment state after completing these steps.
```

### Step 5 — Record Deployment

Update `.sn/state.json`:
```json
{
  "deployments": [
    {
      "env": "{env}",
      "env_url": "{target url}",
      "deployed_at": "{timestamp}",
      "version": "{solution version}",
      "type": "managed"
    }
  ]
}
```

Log to `.sn/execution-log.jsonl`:
```json
{
  "timestamp": "...",
  "agent": "conductor",
  "event": "deployed",
  "phase": "complete",
  "target_env": "{env}",
  "version": "{version}"
}
```

### Step 6 — Final Report
```
✅ Deployment complete

Solution:  {solutionName} v{version}
Target:    {env} ({target url})
Type:      Managed
File:      dist/{solutionName}_managed.zip
Deployed:  {timestamp}

Manual steps remaining:
  ⚠️  Wire 2 connection references
  ⚠️  Set 2 environment variable values
  ⚠️  Activate 2 flows

Full deployment checklist: templates/deployment-checklist.md
```

## Rollback

If import fails or the deployment needs to be reversed:

```powershell
# Delete managed solution from target environment
pac solution delete --name $solutionName --environment $targetEnv
```

Warn user: "Deleting a managed solution removes all data in custom tables.
Only proceed if this is intentional."
