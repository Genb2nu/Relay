# SimplifyNext Component Library

## Purpose

Reusable component patterns that all Forge specialists must use when building
Power Platform components. These are SimplifyNext-approved patterns — do not
deviate without explicit user approval.

---

## Dataverse Table Standards

### Standard Columns (every table must have these)

Every custom table created by SimplifyNext projects must include:

| Column | Logical Name | Type | Notes |
|---|---|---|---|
| Status Reason | `statuscode` | Status Reason | Use custom labels, not default |
| Owner | `ownerid` | Owner | Use for team ownership where applicable |
| Created By | `createdby` | Lookup | System managed |
| Modified On | `modifiedon` | DateTime | System managed |
| Description | `{prefix}_description` | Multi-line Text | Always add |

### Choice Column Pattern

All choice (option set) columns must:
- Use global option sets when the same choices appear on multiple tables
- Include a "Not Set" or "Unknown" default option with value 0
- Use sentence case for option labels (not ALL CAPS, not Title Case Every Word)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
  "LogicalName": "{prefix}_{columnname}",
  "SchemaName": "{Prefix}_{ColumnName}",
  "DisplayName": { "LocalizedLabels": [{ "Label": "{Display Name}", "LanguageCode": 1033 }] },
  "OptionSet": {
    "OptionSetType": "Picklist",
    "Options": [
      { "Value": 0, "Label": { "LocalizedLabels": [{ "Label": "Not set", "LanguageCode": 1033 }] } },
      { "Value": 1, "Label": { "LocalizedLabels": [{ "Label": "Draft", "LanguageCode": 1033 }] } },
      { "Value": 2, "Label": { "LocalizedLabels": [{ "Label": "Submitted", "LanguageCode": 1033 }] } }
    ]
  }
}
```

### Lookup Column Pattern

All lookup columns must:
- Reference the target table's primary key
- Include a descriptive display name (not "Lookup")
- Be added to FLS if the referenced record is sensitive

---

## Security Role Pattern

### Role Privilege Levels

Use these standard privilege depth levels:

| Level | Value | Use Case |
|---|---|---|
| None | 0 | Explicitly deny |
| User | 1 | Own records only |
| Business Unit | 2 | BU records |
| Parent BU | 3 | BU + child BUs |
| Organization | 4 | All records |

### Minimum Role Template

Every project must create at least:
1. **{Prefix}Manager** — full CRUD on all project tables, org-level read
2. **{Prefix}User** — create + read own records, read reference data
3. **{Prefix}Viewer** — read-only on approved tables

Never grant delete privilege to non-admin roles unless explicitly required.
Never grant org-level write to non-admin roles.

---

## FLS Profile Pattern

### When to Create FLS

Create an FLS profile whenever:
- A column contains PII (names, emails, phone numbers, addresses)
- A column contains financial data (amounts, account numbers)
- A column contains approval decisions or scores
- A column is referenced in security-design.md as sensitive

### FLS Assignment Pattern

For each sensitive column:
1. Create one FLS profile per access level needed
2. Assign the FLS profile to the security role(s) that need access
3. Test that unassigned roles cannot see the column value

---

## Environment Variable Standards

All environment variables must:
- Use the publisher prefix: `{prefix}_{VariableName}`
- Have a default value set (even if just a placeholder)
- Be documented with type and purpose in `docs/plan.md`
- Be linked to the solution (not outside)

Types allowed: String, Integer, Boolean, JSON, DataSource, Secret

---

## Connection Reference Standards

All flows must use connection references — never direct connections:
- Name format: `{prefix}_{ServiceName}Connection`
- Example: `ops_DataverseConnection`, `ops_OutlookConnection`
- Create one connection reference per connector type per solution
- Document in `docs/plan.md` under "Connection References"

---

## Solution Standards

Every project must:
- Use a named solution (never Default Solution)
- Have a publisher with the project prefix
- Use unmanaged solution in dev, managed in test/prod
- Include ALL custom components in the solution
- Version solution before each deployment: `major.minor.patch.build`

Naming: `{prefix}_{SolutionDisplayName}` → e.g. `ops_OpsManagement`
