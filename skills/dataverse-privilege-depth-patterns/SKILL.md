---
name: dataverse-privilege-depth-patterns
description: |
  Privilege depth semantics in Dataverse: User/BU/Parent-Child BU/Org depths,
  flat-BU limitations, AddPrivilegesRole vs ReplacePrivilegesRole, Access Teams
  vs Owner Teams, and RetrieveUserPrivileges diagnostic API. Essential for
  Warden, Vault, and Sentinel when designing and testing security.
trigger_keywords:
  - privilege depth
  - security role privileges
  - AddPrivilegesRole
  - RemovePrivilegeRole
  - flat BU
  - single business unit
  - access team
  - row-level security
  - RetrieveUserPrivileges
allowed_tools:
  - Read
---

# Dataverse Privilege Depth Patterns

Understanding privilege depths is critical for Power Platform security. Getting this
wrong causes either over-permissive access or hard API errors.

---

## Privilege Depth Levels

| Depth | Name | Integer | Scope |
|---|---|---|---|
| Basic | User | 1 | Records owned by the user only |
| Local | Business Unit | 2 | Records owned by anyone in the same BU |
| Deep | Parent-Child BU | 3 | Records in user's BU + all child BUs |
| Global | Organization | 4 | All records regardless of ownership |

---

## CRITICAL: Flat Single-BU Limitation

In environments with only ONE Business Unit (no child BUs):

**Basic (User) depth does NOT provide row-level isolation for list queries.**

Why: When all users are in the same BU, "Local" and "Basic" privilege depths both
allow reading all records in that BU. The distinction between "my records" and
"BU records" only manifests when there are multiple BUs.

**What this means:**
- `prvReadAccount` at Basic depth in a flat BU = user can read ALL account records
- This is by design — Dataverse privilege depth controls BU boundaries, not individual record visibility
- Row-level isolation in flat-BU requires one of:
  1. Access Teams (per-record sharing)
  2. Custom ownership + view filters (not true security — API still returns all)
  3. Creating child Business Units

**When to recommend multi-BU:**
- Requirements say "users should only see their own records" for custom tables
- More than 2 distinct access levels exist (not just admin/user)
- Department-level data segregation is required

**When flat-BU is acceptable:**
- All users can see all records (transparency model)
- Security is only about write/delete restrictions, not read restrictions
- Read restriction is cosmetic only (filtered views, not security boundary)

---

## Table Ownership and Valid Depths

| Ownership Type | Valid Depths | Notes |
|---|---|---|
| UserOwned | Basic, Local, Deep, Global | Full depth range |
| OrganizationOwned | Global ONLY | Basic/Local causes error 0x8004140b |

**Always check ownership before assigning privileges:**
```powershell
$ownership = (Invoke-RestMethod `
    -Uri "$orgUrl/api/data/v9.2/EntityDefinitions(LogicalName='<table>')?`$select=OwnershipType" `
    -Headers $headers).OwnershipType
# Returns: "UserOwned" or "OrganizationOwned"
```

---

## AddPrivilegesRole API

Adds privileges to an existing security role.

```powershell
$body = @{
    RoleId = "<role-guid>"
    Privileges = @(
        @{ PrivilegeId = "<priv-guid>"; Depth = "Basic" }   # or Local, Deep, Global
        @{ PrivilegeId = "<priv-guid>"; Depth = "Local" }
    )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/roles(<role-guid>)/Microsoft.Dynamics.CRM.AddPrivilegesRole" `
    -Headers $headers -Body $body -ContentType "application/json"
```

**CRITICAL LIMITATION:** `AddPrivilegesRole` does NOT downgrade existing privileges.
If a role already has `prvReadAccount` at Global depth, calling AddPrivilegesRole with
Basic depth does NOTHING — the Global depth remains.

---

## RemovePrivilegeRole API

Removes a specific privilege from a role entirely.

```powershell
$body = @{
    RoleId = "<role-guid>"
    PrivilegeId = "<priv-guid>"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/roles(<role-guid>)/Microsoft.Dynamics.CRM.RemovePrivilegeRole" `
    -Headers $headers -Body $body -ContentType "application/json"
```

**Pattern for downgrading privilege depth:**
```powershell
# 1. Remove the existing privilege (any depth)
Invoke-RestMethod -Method POST -Uri "$orgUrl/api/data/v9.2/roles($roleId)/Microsoft.Dynamics.CRM.RemovePrivilegeRole" `
  -Headers $headers -Body (@{ RoleId = $roleId; PrivilegeId = $privId } | ConvertTo-Json) -ContentType "application/json"

# 2. Re-add at the desired lower depth
Invoke-RestMethod -Method POST -Uri "$orgUrl/api/data/v9.2/roles($roleId)/Microsoft.Dynamics.CRM.AddPrivilegesRole" `
  -Headers $headers -Body (@{ RoleId = $roleId; Privileges = @(@{ PrivilegeId = $privId; Depth = "Basic" }) } | ConvertTo-Json -Depth 5) -ContentType "application/json"
```

---

## ReplacePrivilegesRole API

Replaces ALL privileges on a role at once. Use with caution — this removes anything
not in the new list.

```powershell
$body = @{
    RoleId = "<role-guid>"
    Privileges = @(
        @{ PrivilegeId = "<priv1>"; Depth = "Basic" }
        @{ PrivilegeId = "<priv2>"; Depth = "Local" }
        # Every privilege must be listed — anything not here is REMOVED
    )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/ReplacePrivilegesRole" `
    -Headers $headers -Body $body -ContentType "application/json"
```

---

## RetrieveUserPrivileges (Diagnostic)

Use to verify what a specific user can actually do:

```powershell
$uri = "$orgUrl/api/data/v9.2/systemusers(<user-guid>)/Microsoft.Dynamics.CRM.RetrieveUserPrivileges"
$privs = (Invoke-RestMethod -Uri $uri -Headers $headers).value

# Check for dangerous privileges
$sysAdmin = $privs | Where-Object { $_.PrivilegeName -eq "prvReadEntity" -and $_.Depth -eq 4 }
if ($sysAdmin) {
    Write-Host "[DANGER] User has system-level privileges — likely System Administrator"
}
```

**Use in Sentinel pre-Phase 6 check:**
If any test user returns `prvAllTables` or 400+ privileges at Global depth → they have
System Administrator. All security tests are invalid.

---

## Security Role Disassociation (Remove role from user)

```powershell
# Correct URL format — $ref at END of path
$uri = "$orgUrl/api/data/v9.2/systemusers($userId)/systemuserroles_association($roleId)/`$ref"
Invoke-RestMethod -Method DELETE -Uri $uri -Headers $headers
```

**Common mistakes:**
- ❌ `DELETE /systemuserroles($id)` — wrong entity
- ❌ `DELETE /systemusers($id)/systemuserroles_association?$id=roles($roleId)` — wrong syntax
- ✅ `DELETE /systemusers($userId)/systemuserroles_association($roleId)/$ref` — correct

---

## Access Teams vs Owner Teams

| Feature | Owner Teams | Access Teams |
|---|---|---|
| Created by | Admin (static) | System (per-record, dynamic) |
| Security role | Has its own roles | Inherits from access team template |
| Record ownership | Can own records | Cannot own records |
| Sharing | N/A | Shares specific record with team members |
| Best for | Department-level access | Per-record collaboration |

**When to use Access Teams:**
- Row-level sharing in flat-BU environments
- "Assigned to" or "collaborators" pattern
- Record-level visibility without BU restructuring

**Setup:**
1. Create Access Team Template on the entity
2. Add users to the team via `teamtemplate` + `AddMembersTeam`
3. Users automatically get access to the specific record

---

## Privilege Name Convention

Dataverse privileges follow this pattern:
- `prvRead<EntitySchemaName>` — Read
- `prvCreate<EntitySchemaName>` — Create
- `prvWrite<EntitySchemaName>` — Write (Update)
- `prvDelete<EntitySchemaName>` — Delete
- `prvAppend<EntitySchemaName>` — Append (associate child)
- `prvAppendTo<EntitySchemaName>` — AppendTo (be associated as child)
- `prvAssign<EntitySchemaName>` — Assign (change owner)
- `prvShare<EntitySchemaName>` — Share

For custom tables: `prvRead<prefix>_<tablename>` (uses schema name, not logical name).

**Getting privilege IDs:**
```powershell
$uri = "$orgUrl/api/data/v9.2/privileges?`$filter=contains(name,'<prefix>_<table>')&`$select=privilegeid,name"
$privs = (Invoke-RestMethod -Uri $uri -Headers $headers).value
```
