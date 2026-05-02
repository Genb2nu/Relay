---
name: power-platform-security-patterns
description: |
  Warden's knowledge base. Covers the Dataverse security model, common
  UI-vs-actual-security traps, FLS verification procedures, connection reference
  risks, and security role design patterns. Reference this skill whenever
  reviewing or designing Power Platform security.
trigger_keywords:
  - security role
  - field level security
  - FLS
  - trust boundary
  - data access
  - privilege escalation
  - row level security
allowed_tools:
  - Read
  - WebSearch
---

# Power Platform Security Patterns

## The Dataverse Security Model (cheat sheet)

### Layers (evaluated top to bottom — MOST RESTRICTIVE wins)

1. **Environment-level** — DLP policies, tenant isolation
2. **Security role** — table-level CRUD + scope (User/BU/Parent BU/Org)
3. **Column security (FLS)** — field-level read/update/create per profile
4. **Hierarchy security** — manager or position-based access to subordinates
5. **Record sharing** — explicit share of individual records to users/teams
6. **Team membership** — owner teams, access teams, AAD group teams

### Table Ownership Types

| Type | Row-level security? | BU hierarchy? | Use when |
|---|---|---|---|
| **User-owned** | Yes — owner determines BU scope | Yes | Each record belongs to a specific user; different users see different rows |
| **Organisation-owned** | No — all users with table privilege see all rows | No | Reference data, config, lookup tables where everyone sees everything |

**Common mistake**: choosing Organisation-owned "because it's simpler" and then
trying to restrict access via views or canvas Filter(). This is NOT security.

### Security Role Scope Levels

| Scope | Meaning | When to use |
|---|---|---|
| **User** | Only own records | Default. Most restrictive. |
| **Business Unit** | Own records + records owned by anyone in same BU | When teams in the same BU share workload |
| **Parent: Child BU** | Own BU + all child BUs | For managers/supervisors who oversee multiple BUs |
| **Organisation** | All records regardless of BU | Admin roles only. Never for regular users. |

## UI-vs-Actual-Security Traps

These are the most dangerous patterns in Power Platform. Each looks like security
but provides ZERO protection at the data layer.

### Trap 1: JavaScript `setVisible(false)`

- **What it does**: Hides a field on a model-driven app form
- **What it does NOT do**: Prevent access via Web API, FetchXML, Advanced Find, Power Automate, canvas apps, or any other data access channel
- **The fix**: Field-Level Security (FLS) profile on the column
- **How to verify**: Call `GET /api/data/v9.2/<table>(<id>)?$select=<column>` as the restricted user. If the column value is returned, it's not secure.

### Trap 2: Business Rule show/hide

- **What it does**: Conditionally shows/hides a field on the form via a no-code Business Rule
- **What it does NOT do**: Same as Trap 1 — form-only, no data-layer enforcement
- **The fix**: FLS profile if the intent is to restrict access, not just declutter the UI

### Trap 3: Sitemap navigation removal

- **What it does**: Removes a table from the app's navigation menu
- **What it does NOT do**: Prevent the user from accessing that table via:
  - Advanced Find
  - Direct URL (`/main.aspx?etn=<table>&pagetype=entitylist`)
  - Web API
  - Power Automate
  - Related entity lookups on other forms
- **The fix**: Remove the Read privilege on that table from the user's security role

### Trap 4: View filter as access control

- **What it does**: Filters records in a system view (e.g. "My Active Records")
- **What it does NOT do**: Prevent the user from creating a personal view with no filter, using Advanced Find, or querying the Web API without the filter
- **The fix**: Security role scope at User or BU level

### Trap 5: Canvas app `Filter()` / `Search()`

- **What it does**: Client-side filtering in Power Fx
- **What it does NOT do**: The underlying Dataverse connection returns ALL records the user has Read privilege on. The Filter() runs in the app, not at the data source.
- **The fix**: Use Dataverse security roles to restrict which records the user can read. Canvas app filtering is for UX, not security.
- **Nuance**: If using SQL or SharePoint as the data source, the same principle applies — Filter() is client-side.

### Trap 6: Connection reference with maker identity

- **What it does**: A Power Automate flow uses the maker's (creator's) connection to Dataverse or other services
- **Risk**: If the maker has System Administrator privileges, every user who triggers that flow effectively runs it with sysadmin access
- **The fix**: Use "invoking user" connection type, or create a dedicated service account with minimum-necessary privileges
- **How to verify**: Open the flow → Settings → check the connection identity for each connector

## FLS Verification Procedure

For every column that requires FLS:

1. ✅ **Table definition**: Column has "Enable column security" = Yes
2. ✅ **FLS profile created**: Profile exists with correct read/update/create permissions per role
3. ✅ **Profile assigned**: FLS profile is assigned to the correct security roles/users
4. ✅ **Main form**: Column is restricted on the main form (if present)
5. ✅ **Quick-create form**: Column is restricted on quick-create (if present)
6. ✅ **Quick-view form**: Column is restricted on any quick-view that displays it
7. ✅ **Web API**: `GET` request for the column by a restricted user returns no value (not just hidden — actually omitted from the response)
8. ✅ **Advanced Find**: Column does not appear in Advanced Find columns for restricted users
9. ✅ **Power BI**: If a Power BI report connects directly to Dataverse, FLS is respected (but only with Dataverse connector, not SQL endpoint)

## Security Role Design Patterns

### Pattern: Persona-Based Roles

Create one custom security role per persona identified in requirements. Never reuse a single role for personas with different trust levels.

```
Role: Employee
  - <MainTable>: Create(User), Read(User), Write(User), Delete(None)
  - <ReferenceTable>: Read(Org), no create/write/delete
  - <ApprovalTable>: Read(User), no create/write/delete

Role: Manager
  - <MainTable>: Read(BU), Write(BU) — can see/edit records from their BU
  - <ApprovalTable>: Create(User), Read(BU), Write(User)

Role: L&D Admin
  - <MainTable>: Read(Org), Write(Org)
  - <ApprovalTable>: Read(Org), Write(Org)
  - <ReferenceTable>: Create(Org), Read(Org), Write(Org), Delete(Org)
```

### Pattern: Minimum Privilege Start

Start every role with zero privileges. Add only what the persona needs. Never copy from an existing role and remove — you'll miss something.

### Pattern: Test User Matrix

For every persona, create a test user assigned ONLY that role. Use these test users during verification (Phase 6) to prove the security boundaries hold.

---

## Flat Single-BU Limitation (CRITICAL for security design)

### The Problem

In environments with only ONE Business Unit (the default "root" BU, no children):

- **Basic (User) depth** and **Local (BU) depth** provide IDENTICAL access for READ operations
- All users are in the same BU, so "BU scope" = "all records"
- This means "User scope Read" does NOT restrict a user to only their own records in list queries
- The user CAN still see all records via API, Advanced Find, and views

### When This Matters

| Requirement | Flat-BU works? | Multi-BU required? |
|---|---|---|
| Users see all records, restricted write/delete | Yes | No |
| Users see ONLY their own records | **NO** | Yes (or Access Teams) |
| Managers see their team's records only | **NO** | Yes (hierarchy security + child BUs) |
| Admin sees everything, users see subset | **NO** for row-level | Yes |

### Solutions for Row-Level Isolation

1. **Create child Business Units** (recommended):
   - One BU per department or team
   - Assign users to their BU
   - Basic depth now means "only records owned by me"
   - Local depth means "only records in my BU"

2. **Access Teams** (per-record sharing):
   - Create an Access Team Template on the entity
   - Add specific users to each record's access team
   - Users only see records where they're team members
   - More flexible but more complex to manage

3. **Owner filtering in views** (NOT security — UX only):
   - Filter views to `ownerid eq currentuser`
   - Does NOT prevent Web API or Advanced Find access
   - Acceptable only when the data is not sensitive

### Warden's Decision Framework

When reviewing security-design.md, check:
1. Does the plan assume row-level READ isolation?
2. Is the environment flat single-BU?
3. If both → flag as CRITICAL: "Row isolation requires child BUs or Access Teams"

### Test Implications (for Sentinel)

Tests that verify "user cannot see another user's records" will FAIL in flat-BU
environments. Tag these as `[ARCH-REQUIRED]` — they require multi-BU topology:

- T-SEC-01 type tests (employee cannot read other employee's records)
- T-BAL type tests (employee cannot read another's balance)
- Any test that expects an empty result set from a filtered-by-ownership query

These failures are ENVIRONMENT limitations, not code defects. The security design
is correct; the environment topology doesn't support the enforcement model.
