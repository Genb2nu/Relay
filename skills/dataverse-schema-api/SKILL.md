---
name: dataverse-schema-api
description: |
  Dataverse Web API patterns for schema operations: creating tables, columns,
  relationships, option sets, and alternate keys via the Metadata API.
  Covers EntityDefinitions, AttributeDefinitions, and RelationshipDefinitions
  endpoints with exact request bodies and common error codes.
trigger_keywords:
  - create table
  - create column
  - EntityDefinitions
  - AttributeDefinitions
  - Dataverse schema
  - create relationship
  - option set
  - alternate key
allowed_tools:
  - Read
---

# Dataverse Schema API Patterns

Web API patterns for creating and modifying Dataverse schema (metadata).
Vault and Forge reference this when building tables, columns, and relationships.

---

## Base Headers for All Schema Operations

```powershell
$headers = @{
    Authorization    = "Bearer $token"
    "Content-Type"   = "application/json"
    "OData-Version"  = "4.0"
    "Prefer"         = "return=representation"
    "MSCRM.SolutionName" = "<SolutionLogicalName>"  # Adds to solution automatically
}
```

**CRITICAL:** Always include `MSCRM.SolutionName` header — this ensures the component
is added to your solution. Without it, the component goes to the Default Solution.

---

## Create Table (Entity)

```powershell
$tableBody = @{
    "@odata.type"      = "Microsoft.Dynamics.CRM.EntityMetadata"
    SchemaName         = "<Prefix>_<TableName>"
    DisplayName        = @{
        "@odata.type"  = "Microsoft.Dynamics.CRM.Label"
        LocalizedLabels = @(@{
            "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"
            Label         = "<Display Name>"
            LanguageCode  = 1033
        })
    }
    DisplayCollectionName = @{
        "@odata.type"  = "Microsoft.Dynamics.CRM.Label"
        LocalizedLabels = @(@{
            "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"
            Label         = "<Plural Display Name>"
            LanguageCode  = 1033
        })
    }
    Description        = @{
        "@odata.type"  = "Microsoft.Dynamics.CRM.Label"
        LocalizedLabels = @(@{
            "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"
            Label         = "<Description>"
            LanguageCode  = 1033
        })
    }
    OwnershipType      = "UserOwned"   # or "OrganizationOwned"
    HasNotes           = $true
    HasActivities      = $false
    IsActivity         = $false
    PrimaryNameAttribute = "<prefix>_name"
    Attributes         = @(
        @{
            "@odata.type"  = "Microsoft.Dynamics.CRM.StringAttributeMetadata"
            SchemaName     = "<Prefix>_Name"
            RequiredLevel  = @{ Value = "ApplicationRequired" }
            MaxLength      = 200
            DisplayName    = @{
                "@odata.type"  = "Microsoft.Dynamics.CRM.Label"
                LocalizedLabels = @(@{
                    "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"
                    Label         = "Name"
                    LanguageCode  = 1033
                })
            }
            IsPrimaryName  = $true
        }
    )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method POST -Uri "$orgUrl/api/data/v9.2/EntityDefinitions" `
    -Headers $headers -Body $tableBody -ContentType "application/json"
```

---

## Create Columns (Attributes)

### String Column
```powershell
$body = @{
    "@odata.type"  = "Microsoft.Dynamics.CRM.StringAttributeMetadata"
    SchemaName     = "<Prefix>_<ColumnName>"
    RequiredLevel  = @{ Value = "None" }  # None, Recommended, ApplicationRequired
    MaxLength      = 200
    FormatName     = @{ Value = "Text" }  # Text, Email, Url, Phone, TextArea
    DisplayName    = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "<Display>"; LanguageCode = 1033 }) }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/EntityDefinitions(LogicalName='<prefix>_<table>')/Attributes" `
    -Headers $headers -Body $body -ContentType "application/json"
```

### Integer Column
```powershell
$body = @{
    "@odata.type" = "Microsoft.Dynamics.CRM.IntegerAttributeMetadata"
    SchemaName    = "<Prefix>_<ColumnName>"
    RequiredLevel = @{ Value = "None" }
    MinValue      = 0
    MaxValue      = 2147483647
    Format        = "None"  # None, Duration, TimeZone, Language, Locale
    DisplayName   = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "<Display>"; LanguageCode = 1033 }) }
}
```

### Decimal Column
```powershell
$body = @{
    "@odata.type" = "Microsoft.Dynamics.CRM.DecimalAttributeMetadata"
    SchemaName    = "<Prefix>_<ColumnName>"
    RequiredLevel = @{ Value = "None" }
    MinValue      = 0
    MaxValue      = 1000000
    Precision     = 2
    DisplayName   = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "<Display>"; LanguageCode = 1033 }) }
}
```

### DateTime Column
```powershell
$body = @{
    "@odata.type" = "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata"
    SchemaName    = "<Prefix>_<ColumnName>"
    RequiredLevel = @{ Value = "None" }
    Format        = "DateOnly"  # DateOnly, DateAndTime
    DateTimeBehavior = @{ Value = "UserLocal" }  # UserLocal, DateOnly, TimeZoneIndependent
    DisplayName   = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "<Display>"; LanguageCode = 1033 }) }
}
```

### Choice (OptionSet) Column — Local
```powershell
$body = @{
    "@odata.type" = "Microsoft.Dynamics.CRM.PicklistAttributeMetadata"
    SchemaName    = "<Prefix>_<ColumnName>"
    RequiredLevel = @{ Value = "None" }
    OptionSet     = @{
        "@odata.type" = "Microsoft.Dynamics.CRM.OptionSetMetadata"
        IsGlobal      = $false
        OptionSetType = "Picklist"
        Options       = @(
            @{ Value = 0; Label = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "Pending"; LanguageCode = 1033 }) } }
            @{ Value = 1; Label = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "Approved"; LanguageCode = 1033 }) } }
            @{ Value = 2; Label = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "Rejected"; LanguageCode = 1033 }) } }
        )
    }
    DisplayName   = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "<Display>"; LanguageCode = 1033 }) }
}
```

### Lookup Column (via Relationship)
Lookup columns are created by creating a relationship — see Relationships section below.

---

## Create Relationships

### One-to-Many (Lookup)
```powershell
$body = @{
    "@odata.type"       = "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata"
    SchemaName          = "<prefix>_<parent>_<child>"
    ReferencedEntity    = "<prefix>_<parenttable>"      # Parent (1 side)
    ReferencingEntity   = "<prefix>_<childtable>"       # Child (N side)
    CascadeConfiguration = @{
        Assign   = "NoCascade"
        Delete   = "RemoveLink"   # RemoveLink, Restrict, Cascade
        Merge    = "NoCascade"
        Reparent = "NoCascade"
        Share    = "NoCascade"
        Unshare  = "NoCascade"
    }
    Lookup = @{
        SchemaName    = "<Prefix>_<ParentTable>Id"
        RequiredLevel = @{ Value = "None" }
        DisplayName   = @{ "@odata.type" = "Microsoft.Dynamics.CRM.Label"; LocalizedLabels = @(@{ "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"; Label = "<Parent Display Name>"; LanguageCode = 1033 }) }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/RelationshipDefinitions" `
    -Headers $headers -Body $body -ContentType "application/json"
```

### Many-to-Many
```powershell
$body = @{
    "@odata.type"         = "Microsoft.Dynamics.CRM.ManyToManyRelationshipMetadata"
    SchemaName            = "<prefix>_<table1>_<table2>"
    Entity1LogicalName    = "<prefix>_<table1>"
    Entity2LogicalName    = "<prefix>_<table2>"
    IntersectEntityName   = "<prefix>_<table1>_<table2>"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST `
    -Uri "$orgUrl/api/data/v9.2/RelationshipDefinitions" `
    -Headers $headers -Body $body -ContentType "application/json"
```

---

## Check If Entity/Column Exists (before creating)

```powershell
# Check table exists
$uri = "$orgUrl/api/data/v9.2/EntityDefinitions(LogicalName='<prefix>_<table>')?`$select=LogicalName"
try {
    $exists = Invoke-RestMethod -Uri $uri -Headers $headers
    Write-Host "[SKIP] Table already exists"
} catch {
    Write-Host "[CREATE] Table does not exist — creating"
}

# Check column exists
$uri = "$orgUrl/api/data/v9.2/EntityDefinitions(LogicalName='<prefix>_<table>')/Attributes(LogicalName='<prefix>_<column>')?`$select=LogicalName"
try {
    $exists = Invoke-RestMethod -Uri $uri -Headers $headers
    Write-Host "[SKIP] Column already exists"
} catch {
    Write-Host "[CREATE] Column does not exist — creating"
}
```

---

## Publish Customizations

After creating tables/columns, publish to make them available:

```powershell
# Publish specific entity
$body = @{
    ParameterXml = "<importexportxml><entities><entity><prefix>_<table></entity></entities></importexportxml>"
} | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri "$orgUrl/api/data/v9.2/PublishXml" `
    -Headers $headers -Body $body -ContentType "application/json"

# Publish ALL customizations (slower but safe)
Invoke-RestMethod -Method POST -Uri "$orgUrl/api/data/v9.2/PublishAllXml" -Headers $headers
```

---

## Common Error Codes

| Code | Meaning | Fix |
|---|---|---|
| 0x80048100 | Entity already exists | Check before creating |
| 0x80044154 | Attribute already exists | Check before creating |
| 0x80072013 | Violates database constraint (duplicate) | Use idempotent check pattern |
| 0x80040203 | Required property missing | Check all @odata.type annotations |
| 0x8004431A | Invalid SchemaName format | Must start with prefix_, no spaces |
