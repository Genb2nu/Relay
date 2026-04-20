# Security Design — <project name>

> Owned by Warden. Initial draft by Drafter, revised by Warden during plan review.
> Do not edit manually after lock.

## Personas and Trust Boundaries

| Persona | Dataverse Security Role | Trust Level | What They Can See | What They Must NOT See |
|---|---|---|---|---|
| | | | | |

## Table Ownership Model

| Table | Ownership Type | Rationale |
|---|---|---|
| | User / Organisation | |

> **Reminder**: Organisation-owned tables cannot use row-level security via BU
> hierarchy. Only use Organisation ownership when ALL users should have equal
> access to all rows, or when access is controlled purely by security role
> privilege scope.

## Security Roles

### Role: <role name>

**Assigned to persona(s)**: 

| Table | Create | Read | Write | Delete | Append | Append To | Assign | Share |
|---|---|---|---|---|---|---|---|---|
| | User | User | User | None | User | User | None | None |
| | | | | | | | | |

Scope values: None / User / BU / Parent BU / Org

### Role: <next role...>

## Field-Level Security (FLS)

| Table | Column | FLS Profile | Can Read | Can Update | Can Create |
|---|---|---|---|---|---|
| | | <profile name> | Yes/No per role | Yes/No per role | Yes/No per role |

> **Verification checklist** (Warden must confirm all four):
> - [ ] FLS configured on the table column definition
> - [ ] FLS profile assigned to the correct security roles
> - [ ] FLS restricts the column on ALL forms (main, quick-create, quick-view)
> - [ ] FLS restricts the column via Web API (test with API call, not just form)

## UI-vs-Actual-Security Audit

For every UI-based restriction in the plan, confirm it is backed by real security:

| UI Restriction | Mechanism | Is This Real Security? | Backing Security Control |
|---|---|---|---|
| Field hidden on form | JS `setVisible(false)` | ❌ NO | FLS profile required |
| Field hidden on form | Business Rule | ❌ NO | FLS profile required |
| Table not in sitemap | Sitemap config | ❌ NO | Security role privilege required |
| View filtered | View filter | ❌ NO | Security role scope required |
| Canvas app Filter() | Client-side filter | ❌ NO | Dataverse security role required |
| | | | |

## Connection Reference Security

| Connection Reference | Connector | Identity Used | Risk Level | Mitigation |
|---|---|---|---|---|
| | | Maker / Invoking User | High / Low | |

> **Rule**: Any connection reference using the maker's identity where the maker
> has higher privileges than the invoking user is a privilege escalation risk.
> Default to invoking-user identity unless there is a documented exception.

## Teams and Business Units

| Team/BU | Purpose | Members | Access Granted |
|---|---|---|---|
| | | | |

## Hierarchy Security

- **Hierarchy type**: None / Manager / Positional
- **Depth**: 
- **Edge cases addressed**:
  - User with no manager: 
  - Circular hierarchy: 
  - Cross-BU manager: 

## DLP Impact Assessment

| Connector Used | DLP Group (Business / Non-Business / Blocked) | Conflict? | Resolution |
|---|---|---|---|
| | | | |

## Sharing Configuration

| Table | Default Sharing | Cascade Share | Auto-Share via Connection | Risk |
|---|---|---|---|---|
| | | | | |
