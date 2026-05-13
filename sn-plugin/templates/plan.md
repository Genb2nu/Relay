# Technical Plan — {Project Name}

**Project:** {Project Name}
**Solution:** {solution_name}
**Publisher Prefix:** {publisher_prefix}
**Environment:** {environment_url}
**Date:** {date}
**Status:** Draft / Locked

> ⚠️ When locked, this file may not be edited without running `/sn-plan-review --unlock`.

---

## 1. Solution Overview

**Solution Name:** `{prefix}_{SolutionName}`
**Publisher:** {Publisher Display Name} (`{prefix}`)
**Version:** 1.0.0.0

### Component Summary

| Type | Count |
|---|---|
| Tables | {n} |
| Security Roles | {n} |
| FLS Profiles | {n} |
| Canvas Apps | {n} |
| Model-Driven Apps | {n} |
| Power Automate Flows | {n} |
| Environment Variables | {n} |
| Connection References | {n} |

---

## 2. Dataverse Tables

### `{prefix}_{entity1}` — {Entity 1 Display Name}

**Plural Name:** {Entity 1 Display Name Plural}
**Ownership:** User/Team
**Has Activities:** No
**Has Notes:** No

| Column | Logical Name | Type | Required | FLS | Notes |
|---|---|---|---|---|---|
| {Primary Col} | `{prefix}_{primarycol}` | Text (200) | Yes | No | Primary name column |
| {Column 2} | `{prefix}_{col2}` | Choice | No | No | Values: {opt1}, {opt2} |
| {Column 3} | `{prefix}_{col3}` | DateTime | No | No | |
| {Column 4} | `{prefix}_{col4}` | Lookup → `{prefix}_{entity2}` | No | No | |
| {Column 5} | `{prefix}_{col5}` | Text (500) | No | **Yes** | Sensitive field |

**Choice Values for `{prefix}_{col2}`:**
- 0: Not set
- 1: {Option 1}
- 2: {Option 2}
- 3: {Option 3}

---

## 3. Security Roles

| Role Name | Logical Name | Description |
|---|---|---|
| {Prefix}Manager | `{prefix}Manager` | Full access for managers |
| {Prefix}User | `{prefix}User` | Standard user access |
| {Prefix}Viewer | `{prefix}Viewer` | Read-only access |

### Privilege Matrix

| Table | Manager (CRWDAA) | User (CRWDAA) | Viewer (CRWDAA) |
|---|---|---|---|
| `{prefix}_{entity1}` | Org/Org/Org/Org/Org/Org | BU/User/User/None/BU/BU | None/User/None/None/User/None |

Legend: C=Create, R=Read, W=Write, D=Delete, A=Append, A=AppendTo
Depth: Org=Organisation, BU=Business Unit, User=Own records, None=No access

---

## 4. Field-Level Security Profiles

### `{prefix}_{ProfileName}`

**Assigned to Roles:** {Prefix}Manager, {Prefix}User

| Column | Table | Can Read | Can Update | Can Create |
|---|---|---|---|---|
| `{prefix}_{col5}` | `{prefix}_{entity1}` | Yes | Yes | Yes |

---

## 5. Environment Variables

| Schema Name | Display Name | Type | Default Value | Purpose |
|---|---|---|---|---|
| `{prefix}_{VarName}` | {Display Name} | String/Integer/Boolean | `{default}` | {Purpose} |

---

## 6. Connection References

| Schema Name | Connector | Purpose |
|---|---|---|
| `{prefix}_DataverseConnection` | Microsoft Dataverse | Read/write to Dataverse tables |
| `{prefix}_OutlookConnection` | Office 365 Outlook | Send email notifications |

---

## 7. Canvas App

**App Name:** {App Display Name}
**Unique Name:** `{prefix}_{AppName}`
**Type:** Canvas App (solution-scoped)

### Screens

| Screen | Persona | Purpose | Data Source |
|---|---|---|---|
| `HomeScreen` | All | Navigation hub | None |
| `{Entity}ListScreen` | {Persona} | View and filter records | `{prefix}_{entity1}` |
| `{Entity}DetailScreen` | {Persona} | View and edit a record | `{prefix}_{entity1}` |
| `ApprovalQueueScreen` | {Approver Persona} | Review pending approvals | `{prefix}_{entity1}` |

### Screen Details

#### HomeScreen
- Navigation tiles for each persona's primary function
- Shows count of pending items (if any) for the current user
- Global variable initialised: `varCurrentUser = User()`

#### {Entity}ListScreen
- Gallery filtered to `statuscode <> 3` (exclude cancelled)
- Search bar using `StartsWith(Title, txtSearch.Text)`
- "New {Entity}" button → navigates to `{Entity}DetailScreen` with `IsNew = true`

---

## 8. Model-Driven App

**App Name:** {MDA Display Name}
**Unique Name:** `{prefix}_{MDAName}`

### Sitemap

```
{Area Name}
  ├── {Group Name}
  │   ├── {Entity 1} (list)
  │   └── {Entity 2} (list)
  └── Administration
      └── Settings
```

### Forms

| Entity | Form Name | Type | Sections |
|---|---|---|---|
| `{prefix}_{entity1}` | Main Form | Main | General, Details, Approval |
| `{prefix}_{entity1}` | Quick Create | Quick Create | Title, Status |

---

## 9. Power Automate Flows

### {Prefix}ApprovalFlow

**Trigger:** When a row is added/modified — `{prefix}_{entity1}` where `statuscode = 1`
**Type:** Automated cloud flow
**Connection References:** `{prefix}_DataverseConnection`, `{prefix}_OutlookConnection`

**Actions:**
1. Get approver details from `{prefix}_{entity1}.{prefix}_approver`
2. Self-approval check: if `createdby = approver` → reject automatically
3. Start approval (Approvals connector)
4. On Approved: PATCH record `statuscode = 2`, send confirmation email
5. On Rejected: PATCH record `statuscode = 3`, send rejection email

**Error Handling:** Try/Catch scope. On catch: email `{prefix}_AdminEmail` with error details.

---

## 10. Deployment Targets

| Environment | URL | Type |
|---|---|---|
| Development | {dev url} | Unmanaged |
| Test | {test url} | Managed |
| Production | {prod url} | Managed |

---

## 11. Decisions Log

| # | Decision | Rationale | Date |
|---|---|---|---|
| 1 | {Decision} | {Why this was chosen over alternatives} | {date} |

---

## Checksums (populated on lock)

- `plan.md`: {sha256}
- `security-design.md`: {sha256}
- Locked by: Auditor
- Locked at: {timestamp}
