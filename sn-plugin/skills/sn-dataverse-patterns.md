# SimplifyNext Dataverse Patterns

## Purpose

Standard Dataverse API patterns used by Forge-Vault when building schema,
security roles, and FLS profiles. All operations use the Dataverse REST API.

---

## API Base URL

All API calls use:
```
{environment_url}/api/data/v9.2/
```

Read environment URL from `.sn/state.json.environment`.

## Required Headers

Every metadata API call must include:
```
Authorization: Bearer {token}
Content-Type: application/json
OData-MaxVersion: 4.0
OData-Version: 4.0
MSCRM.SolutionUniqueName: {solution_name}
```

The `MSCRM.SolutionUniqueName` header ensures all components are automatically
added to the correct solution.

---

## Create Table

```http
POST /api/data/v9.2/EntityDefinitions
Content-Type: application/json

{
  "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
  "SchemaName": "{Prefix}_{TableName}",
  "DisplayName": {
    "LocalizedLabels": [{ "Label": "{Display Name}", "LanguageCode": 1033 }]
  },
  "DisplayCollectionName": {
    "LocalizedLabels": [{ "Label": "{Display Name Plural}", "LanguageCode": 1033 }]
  },
  "Description": {
    "LocalizedLabels": [{ "Label": "{Description}", "LanguageCode": 1033 }]
  },
  "OwnershipType": "UserOwned",
  "HasActivities": false,
  "HasNotes": false,
  "IsActivity": false,
  "PrimaryNameAttribute": "{prefix}_{primarycolumn}",
  "Attributes": [
    {
      "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
      "IsPrimaryName": true,
      "SchemaName": "{Prefix}_{PrimaryColumn}",
      "LogicalName": "{prefix}_{primarycolumn}",
      "DisplayName": {
        "LocalizedLabels": [{ "Label": "{Primary Column Name}", "LanguageCode": 1033 }]
      },
      "RequiredLevel": { "Value": "ApplicationRequired" },
      "MaxLength": 200
    }
  ]
}
```

## Add Column to Table

```http
POST /api/data/v9.2/EntityDefinitions(LogicalName='{prefix}_{table}')/Attributes
Content-Type: application/json

{
  "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
  "SchemaName": "{Prefix}_{ColumnName}",
  "LogicalName": "{prefix}_{columnname}",
  "DisplayName": {
    "LocalizedLabels": [{ "Label": "{Column Display Name}", "LanguageCode": 1033 }]
  },
  "RequiredLevel": { "Value": "None" },
  "MaxLength": 500
}
```

Column types and their `@odata.type`:
- Text: `Microsoft.Dynamics.CRM.StringAttributeMetadata`
- Integer: `Microsoft.Dynamics.CRM.IntegerAttributeMetadata`
- Decimal: `Microsoft.Dynamics.CRM.DecimalAttributeMetadata`
- DateTime: `Microsoft.Dynamics.CRM.DateTimeAttributeMetadata`
- Choice: `Microsoft.Dynamics.CRM.PicklistAttributeMetadata`
- Yes/No: `Microsoft.Dynamics.CRM.BooleanAttributeMetadata`
- Lookup: `Microsoft.Dynamics.CRM.LookupAttributeMetadata`
- Multi-line text: `Microsoft.Dynamics.CRM.MemoAttributeMetadata`

---

## Create Security Role

```http
POST /api/data/v9.2/roles
Content-Type: application/json

{
  "name": "{RoleName}",
  "businessunitid@odata.bind": "/businessunits({buId})"
}
```

Fetch root Business Unit ID:
```http
GET /api/data/v9.2/businessunits?$filter=parentbusinessunitid eq null&$select=businessunitid
```

## Assign Privilege to Role

```http
POST /api/data/v9.2/roles({roleId})/Microsoft.Dynamics.CRM.AddPrivilegesRole
Content-Type: application/json

{
  "Privileges": [
    {
      "Depth": "Global",
      "Name": "prv{Operation}{EntityName}"
    }
  ]
}
```

Privilege names follow the pattern: `prv{Create|Read|Write|Delete|Append|AppendTo|Assign|Share}{EntitySchemaName}`

Example: `prvReadOps_Request`, `prvCreateOps_Request`

Depth values: `"Basic"` (user), `"Local"` (BU), `"Deep"` (Parent BU), `"Global"` (Org)

---

## Create FLS Profile

```http
POST /api/data/v9.2/fieldsecurityprofiles
Content-Type: application/json

{
  "name": "{prefix}_{ProfileName}",
  "description": "{Description}"
}
```

## Assign Column to FLS Profile

```http
POST /api/data/v9.2/fieldpermissions
Content-Type: application/json

{
  "fieldsecurityprofileid@odata.bind": "/fieldsecurityprofiles({profileId})",
  "entityname": "{prefix}_{table}",
  "attributelogicalname": "{prefix}_{column}",
  "canread": "1",
  "canupdate": "1",
  "cancreate": "1"
}
```

Values: `"0"` = No, `"1"` = Yes, `"2"` = Allowed (but can be overridden)

## Assign FLS Profile to Role

```http
POST /api/data/v9.2/fieldsecurityprofiles({profileId})/fieldsecurityprofile_roles/$ref
Content-Type: application/json

{
  "@odata.id": "{baseUrl}/api/data/v9.2/roles({roleId})"
}
```

---

## Create Environment Variable

```http
POST /api/data/v9.2/environmentvariabledefinitions
Content-Type: application/json

{
  "schemaname": "{prefix}_{VariableName}",
  "displayname": "{Display Name}",
  "type": 100000000,
  "defaultvalue": "{default value}",
  "description": "{Description}"
}
```

Type codes: String=100000000, Number=100000001, Boolean=100000002, JSON=100000003, DataSource=100000004, Secret=100000005

## Verify Table Exists

```http
GET /api/data/v9.2/EntityDefinitions?$filter=LogicalName eq '{prefix}_{table}'&$select=LogicalName,MetadataId
```

Returns empty array if not found. Check `value.length > 0`.

---

## Publish Customisations

After all schema changes, publish:
```http
POST /api/data/v9.2/PublishAllXml
```

Or publish specific components:
```http
POST /api/data/v9.2/PublishXml
Content-Type: application/json

{
  "ParameterXml": "<importexportxml><entities><entity>{prefix}_{table}</entity></entities></importexportxml>"
}
```
