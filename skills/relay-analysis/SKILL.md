---
name: relay-analysis
description: |
  Analyst's knowledge base. How to map existing Power Platform solutions,
  document component inventories, identify gaps vs plan, and produce
  docs/existing-solution.md for audit/change workflows.
trigger_keywords:
  - existing solution
  - solution analysis
  - component inventory
  - analyse
  - audit existing
  - change impact
allowed_tools:
  - Read
---

# Relay Analysis — Analyst Knowledge Base

## When Analyst Runs

Analyst is invoked for:
- `/relay:analyse` — map an existing solution from scratch
- `/relay:audit` — analyse before the audit squad reviews
- `/relay:change` — map existing state before planning a change

## Component Inventory Process

### Step 1: Solution metadata
```powershell
# List solution components
$uri = "$orgUrl/api/data/v9.2/solutions?`$filter=uniquename eq '<SolutionName>'&`$expand=solution_solutioncomponent(`$select=componenttype,objectid)"
$solution = (Invoke-RestMethod -Uri $uri -Headers $headers).value[0]
```

### Step 2: Tables and columns
```powershell
# Get all custom tables in the solution
$uri = "$orgUrl/api/data/v9.2/EntityDefinitions?`$filter=IsCustomEntity eq true&`$select=LogicalName,DisplayName,OwnershipType,Description"
$tables = (Invoke-RestMethod -Uri $uri -Headers $headers).value
```

For each table, get columns:
```powershell
$uri = "$orgUrl/api/data/v9.2/EntityDefinitions(LogicalName='<table>')/Attributes?`$filter=IsCustomAttribute eq true&`$select=LogicalName,AttributeType,RequiredLevel,DisplayName"
```

### Step 3: Flows
```powershell
# Cloud flows in solution (category=5)
$uri = "$orgUrl/api/data/v9.2/workflows?`$filter=solutionid eq '<solutionid>' and category eq 5&`$select=name,statecode,primaryentity,description"
```

### Step 4: Apps
```powershell
# Canvas apps
$uri = "$orgUrl/api/data/v9.2/canvasapps?`$select=displayname,name,status"

# Model-driven apps
$uri = "$orgUrl/api/data/v9.2/appmodules?`$select=name,uniquename,url"
```

### Step 5: Security roles
```powershell
# Custom roles (not system-managed)
$uri = "$orgUrl/api/data/v9.2/roles?`$filter=ismanaged eq false and iscustomizable/Value eq true&`$select=name,roleid"
```

### Step 6: Plugins
```powershell
$uri = "$orgUrl/api/data/v9.2/pluginassemblies?`$filter=ismanaged eq false&`$select=name,version"
$uri = "$orgUrl/api/data/v9.2/sdkmessageprocessingsteps?`$filter=ismanaged eq false&`$select=name,stage,mode,filteringattributes"
```

---

## Output: docs/existing-solution.md

```markdown
# Existing Solution Analysis — <SolutionName>

## Summary
- Solution: <name> (<managed/unmanaged>)
- Publisher: <prefix> / <display name>
- Tables: <N>
- Flows: <N> (active: <N>, inactive: <N>)
- Apps: <N> canvas, <N> model-driven
- Plugins: <N> assemblies, <N> steps
- Security roles: <N>
- FLS profiles: <N>

## Tables

| Table | Display Name | Ownership | Columns | Relationships |
|---|---|---|---|---|
| <prefix>_<name> | <display> | User/Org | <N> custom | <N> 1:N, <N> N:N |

### <prefix>_<tablename> — Column Detail
| Column | Type | Required | Notes |
|---|---|---|---|
| <prefix>_name | String(200) | Yes | Primary name |
| <prefix>_status | Choice | Yes | Values: 0=Pending, 1=Approved, 2=Rejected |

## Flows

| Flow | Trigger | Status | Connected to |
|---|---|---|---|
| <name> | When row modified (<table>) | Active | Dataverse, Outlook |

## Apps

| App | Type | Entities | Notes |
|---|---|---|---|
| <name> | Canvas / MDA | <entities used> | <notes> |

## Security

| Role | Tables | Key privileges | Notes |
|---|---|---|---|
| <name> | <tables with access> | Read(BU), Write(User) | <notes> |

## Gaps & Observations

| # | Category | Finding | Severity |
|---|---|---|---|
| 1 | Security | No FLS on <column> despite being marked sensitive | HIGH |
| 2 | Design | Duplicate tables: <table1> and <table2> serve same purpose | MEDIUM |
```

---

## Gap Categories

| Category | What to look for |
|---|---|
| **Security** | Missing FLS, over-privileged roles, UI-only security, maker-identity connections |
| **Design** | Duplicate entities, unclear naming, mixed conventions, orphaned components |
| **Technical debt** | Disabled flows, unused columns, abandoned plugins, test data in prod |
| **Missing** | Components referenced but not present, broken relationships |
| **Compliance** | DLP violations, unlicensed connector usage, data residency issues |

---

## Change Impact Analysis

When running for `/relay:change`, also produce:

```markdown
## Change Impact Assessment

### Components affected by proposed change
| Component | Current state | Proposed change | Risk |
|---|---|---|---|
| <table> | 5 columns | Add 2 columns | LOW — additive |
| <flow> | Triggers on create | Add update trigger | MEDIUM — test existing |

### Components NOT affected (regression check scope)
| Component | Why unaffected | Verify anyway? |
|---|---|---|
| <other table> | No relationship to changed entity | No |
| <other flow> | Different trigger entity | Yes — shares connection ref |
```
