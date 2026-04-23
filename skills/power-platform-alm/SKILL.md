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
              "subscriptionRequest/entityname": "cr_leaverequest"
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
        "connectionName": "cr_DataverseConnection",
        "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
      }
    }
  }
}
```

### Import Pattern
```powershell
# Pack flow into solution
pac solution export --name LeaveRequestSystem --path ./solution.zip
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
