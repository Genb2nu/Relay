---
name: power-platform-alm
description: |
  ALM pipeline patterns for Power Platform. Covers solution export/import,
  Azure DevOps integration, Git integration, environment promotion strategy,
  and PAC CLI workflows. Reference for Drafter when planning deployment and
  for Courier when executing it.
trigger_keywords:
  - ALM
  - deployment
  - solution export
  - pipeline
  - azure devops
  - environment promotion
  - pac solution
allowed_tools:
  - Read
  - WebSearch
---

# Power Platform ALM Patterns

> **Publisher prefix**: All examples use `<prefix>_` as a placeholder.
> Read the actual prefix from `.relay/state.json` before creating any component.

## Environment Strategy

### Standard Three-Tier

```
DEV (unmanaged) → TEST (managed) → PROD (managed)
```

- **DEV**: Unmanaged solution. Active development happens here. All makers have System Customiser or equivalent.
- **TEST**: Managed import. UAT and integration testing. Restricted maker access.
- **PROD**: Managed import. End users only. No maker access except for emergency fixes.

### Environment Variables

Every value that changes between environments MUST be an Environment Variable:

- API endpoints / URLs
- Email addresses (notification recipients)
- Tenant/app IDs
- Feature flags
- Connection reference targets

**Never hardcode** these in flows, plugins, or web resources.

## Solution Structure

### Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Publisher prefix | 3-5 lowercase chars, no underscores | `relay` |
| Solution unique name | PascalCase, no spaces | `TrainingRequestApproval` |
| Solution display name | Human-readable | `Training Request Approval` |

### Component Organisation

For solutions with many components (100+), consider segmenting:

- **Core solution**: Tables, security roles, option sets
- **App solution**: Model-driven / canvas apps, sitemap
- **Flow solution**: Cloud flows, connection references
- **Custom code solution**: Plugins, PCF controls, web resources

Segment only when the component count makes a single solution unwieldy. For small projects, one solution is fine.

## PAC CLI Workflow

### Authentication

```bash
# Create an auth profile for each environment
pac auth create --name DEV --environment https://dev-env.crm.dynamics.com
pac auth create --name TEST --environment https://test-env.crm.dynamics.com
pac auth create --name PROD --environment https://prod-env.crm.dynamics.com

# Switch between environments
pac auth select --name DEV
```

### Export

```bash
# Export unmanaged (for source control)
pac solution export --path ./export --name TrainingRequestApproval --overwrite

# Export managed (for deployment to TEST/PROD)
pac solution export --path ./export --name TrainingRequestApproval --managed --overwrite

# Unpack for git-friendly source control
pac solution unpack --zipfile ./export/TrainingRequestApproval.zip --folder ./src/solution --processCanvasApps
```

### Import

```bash
# Select target environment
pac auth select --name TEST

# Import managed solution
pac solution import --path ./export/TrainingRequestApproval_managed.zip --activate-plugins --force-overwrite

# Check import status
pac solution list
```

## Git Integration

### Recommended .gitignore

```
# Packed solution zips (regenerated from source)
*.zip

# Environment-specific settings
.env
.env.*

# Auth profiles
.pac/

# Build artifacts
bin/
obj/
node_modules/

# Relay session state
.relay/
```

### Branch Strategy

```
main ─────────────────────────── production-ready
  └── develop ────────────────── integration branch
       ├── feature/TRA-001 ──── per-feature branches
       └── feature/TRA-002
```

### Commit Conventions

```
feat(schema): add TrainingRequest table with approval columns
fix(flow): handle null manager in approval flow
security(roles): restrict Employee role to User-scope read on ApprovalRecord
docs(plan): update deployment section after Auditor feedback
```

## Azure DevOps Pipeline (template)

```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'windows-latest'

steps:
  - task: PowerPlatformToolInstaller@2
    displayName: 'Install Power Platform CLI'

  - task: PowerPlatformPackSolution@2
    displayName: 'Pack solution'
    inputs:
      SolutionSourceFolder: '$(Build.SourcesDirectory)/src/solution'
      SolutionOutputFile: '$(Build.ArtifactStagingDirectory)/solution.zip'
      SolutionType: 'Managed'

  - task: PowerPlatformImportSolution@2
    displayName: 'Import to TEST'
    inputs:
      authenticationType: 'PowerPlatformSPN'
      PowerPlatformSPN: 'TEST-ServiceConnection'
      SolutionInputFile: '$(Build.ArtifactStagingDirectory)/solution.zip'
      ActivatePlugins: true

  - task: PublishBuildArtifacts@1
    displayName: 'Publish artifact'
    inputs:
      PathtoPublish: '$(Build.ArtifactStagingDirectory)'
      ArtifactName: 'solution'
```

## Troubleshooting

### Common export errors

- **"Solution not found"**: Check `pac auth list` — are you authenticated to the right environment?
- **"Missing dependencies"**: The solution references components from another solution. Add those as dependencies or merge.
- **"Active layer conflicts"**: Someone customised a managed component directly. Remove active customisations before export.

### Common import errors

- **"Component already exists"**: Another solution owns this component. Check solution layering.
- **"Missing dependency"**: Import prerequisite solutions first.
- **"Plugin step registration failed"**: Assembly version mismatch. Re-build and re-export.

---

## Power Automate Flow Automation via Solution Import

Flows can be fully automated by generating JSON definitions and importing them via solution.

### Flow JSON Structure (simplified)
```json
{
  "name": "Leave Request — Approval Notification",
  "properties": {
    "definition": {
      "triggers": {
        "When_a_row_is_added": {
          "type": "OpenApiConnectionWebhook",
          "inputs": {
            "host": { "connectionName": "shared_commondataserviceforapps" },
            "parameters": {
              "subscriptionRequest/message": 1,
              "subscriptionRequest/entityname": "<table_logical_name>"
            }
          }
        }
      },
      "actions": {
        "Get_Employee": { ... },
        "Get_Manager": { ... },
        "Send_email": { ... }
      },
      "contentVersion": "1.0.0.0",
      "$schema": "..."
    },
    "connectionReferences": {
      "shared_commondataserviceforapps": {
        "connectionName": "<prefix>_DataverseConnection",
        "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
      }
    }
  }
}
```

### Import Pattern
```powershell
# Pack flow into solution
pac solution export --name <YourSolutionName> --path ./solution.zip
# Add flow JSON and connection references to solution XML
# Reimport
pac solution import --path ./solution-with-flows.zip --force-overwrite --publish-changes --activate-plugins
```

### Post-import manual steps (document exactly, don't skip)
1. Power Automate → Solutions → `<solution>` → Connection References → connect each
2. Cloud Flows → select each flow → Turn on

## FLS Assignment via API

```powershell
# Assign FLS profile to security role team (preferred pattern)
$orgUrl = "https://<org>.crm5.dynamics.com"
$token = (az account get-access-token --resource $orgUrl | ConvertFrom-Json).accessToken
$h = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

# Create a team for each security role, assign FLS profile to team
# Then assign users to teams (easier to manage than direct user FLS assignment)
```

## Security Role Assignment via PAC CLI

```bash
# Assign role to user
pac admin assign-user \
  --user "user@domain.com" \
  --role "Leave Request Employee" \
  --environment "https://org.crm5.dynamics.com"

# List users to verify
pac admin list-app-user --environment "https://org.crm5.dynamics.com"
```

---

## Connection Reuse Pattern — Check Before Creating

### For Code Apps
Always run /list-connections FIRST to check for existing connections:
```
/list-connections
```
This returns all connections in the environment with their IDs and connector types.
If a matching connector exists → use its ID with /add-dataverse, /add-sharepoint etc.
If not → user creates it once in Power Apps → Forge uses it immediately after.

### For Solution Connection References (Flows)
Use the deployment settings file to auto-populate existing connection IDs:

```powershell
# Step 1 — Generate settings file (has empty ConnectionId slots)
pac solution create-settings --solution-zip ./<YourSolutionName>.zip --settings-file ./deploy-settings.json

# Step 2 — Query existing connection references in the environment
$orgUrl = "https://<your-org>.crm.dynamics.com"
$token = (az account get-access-token --resource $orgUrl | ConvertFrom-Json).accessToken
$h = @{ Authorization = "Bearer $token"; "OData-Version" = "4.0" }
$refs = Invoke-RestMethod -Uri "$orgUrl/api/data/v9.2/connectionreferences?`$select=connectionreferencelogicalname,connectionid,connectorid" -Headers $h

# Step 3 — Match and populate settings.json
# For each ConnectionReference in deploy-settings.json:
#   Find matching connectorid in $refs
#   If found → set ConnectionId to the existing value
#   If not found → leave blank (user links manually)

# Step 4 — Import with pre-populated settings
pac solution import --path ./<YourSolutionName>.zip --settings-file ./deploy-settings.json --force-overwrite --publish-changes
```

### Connection ID via Power Apps URL
If PAC CLI isn't available, get connection IDs from the URL:
- make.powerapps.com → Data → Connections → click connection
- URL format: `...connections/<connectionId>/details`
- Extract the connectionId from the URL

### When NO existing connection exists
Tell the user exactly what to create (not just "create a connection"):
> "I need a Dataverse connection in this environment. Please go to:
> make.powerapps.com → Data → Connections → + New connection → search 'Dataverse' → Create
> Once created, I'll pick it up automatically via /list-connections."

---

## Flow Activation via Dataverse clientdata PATCH

**Critical finding from pilot**: Solution flows cannot be activated via the regular
Power Automate Flow API. They must be activated via Dataverse API by PATCHing
the `clientdata` column on the `workflows` table.

### Why the regular Flow API fails for solution flows
Solution flows go through XRM which has its own connection reference resolution.
The regular Flow API expects `connectionName` but XRM resolves `connectionReferenceName`.
The PATCH must transform the clientdata structure to use connector names as keys.

### Required clientdata transformation
```
GET clientdata structure (from Dataverse):
  connectionReferences:
    <prefix>_DataverseConnection:    ← connection reference logical name as key
      connectionReferenceName: <prefix>_DataverseConnection
      api.name: shared_commondataserviceforapps

PATCH clientdata structure (what XRM expects):
  connectionReferences:
    shared_commondataserviceforapps:  ← connector name as key
      connectionReferenceLogicalName: <prefix>_DataverseConnection
      api.name: shared_commondataserviceforapps
      connection: { connectionReferenceLogicalName: <prefix>_DataverseConnection }
  
  In each trigger/action host block:
    - REMOVE: connectionReferenceName
    - SET: connectionName = connector name (e.g., shared_commondataserviceforapps)
```

### State values
- statecode=0, statuscode=1 = Draft (inactive, just imported)
- statecode=1, statuscode=2 = Active (running)

### Connection reuse pattern
Before creating new connections, search existing ones:
```powershell
$conns = Invoke-RestMethod -Uri "$orgUrl/api/data/v9.2/connections?`$select=name,connectionid,connectorid" -Headers $h
$dvConn = $conns.value | Where-Object { $_.connectorid -like "*commondataservice*" } | Select-Object -First 1
$olConn = $conns.value | Where-Object { $_.connectorid -like "*office365*" } | Select-Object -First 1
```
If found → wire automatically into clientdata connection references.
If not found → user creates once in Power Apps → Forge queries and wires on next run.
