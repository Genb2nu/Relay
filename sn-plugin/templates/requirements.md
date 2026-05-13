# Requirements — {Project Name}

**Project:** {Project Name}
**Solution:** {solution_name}
**Publisher Prefix:** {publisher_prefix}
**Date:** {date}
**Status:** Draft / Approved

---

## 1. Project Overview

{One paragraph describing the business problem this solution solves and the
expected outcome.}

---

## 2. Personas

| Persona | Description | Key Responsibilities |
|---|---|---|
| {PersonaName} | {Role in the organisation} | {What they do in this solution} |
| {PersonaName} | {Role in the organisation} | {What they do in this solution} |

### Persona Access Summary

| Persona | Can Create | Can Read (own) | Can Read (all) | Can Approve | Can Admin |
|---|---|---|---|---|---|
| {Persona 1} | ✅ | ✅ | ❌ | ❌ | ❌ |
| {Persona 2} | ❌ | ✅ | ✅ | ✅ | ❌ |
| {Persona 3} | ❌ | ✅ | ✅ | ❌ | ✅ |

---

## 3. User Stories

### {Persona 1}

- As a **{Persona 1}**, I want to **{action}** so that **{outcome}**.
- As a **{Persona 1}**, I want to **{action}** so that **{outcome}**.
- As a **{Persona 1}**, I want to **{action}** so that **{outcome}**.

### {Persona 2}

- As a **{Persona 2}**, I want to **{action}** so that **{outcome}**.
- As a **{Persona 2}**, I want to **{action}** so that **{outcome}**.
- As a **{Persona 2}**, I want to **{action}** so that **{outcome}**.

---

## 4. Data Entities

| Display Name | Logical Name | Primary Column | Key Columns | Relationships |
|---|---|---|---|---|
| {Entity Name} | `{prefix}_{entityname}` | `{prefix}_{primarycol}` | {col1}, {col2} | {related entity} |

### Entity Details

#### {Entity Display Name} (`{prefix}_{entityname}`)

| Column | Logical Name | Type | Required | Notes |
|---|---|---|---|---|
| {Column Name} | `{prefix}_{colname}` | Text / Integer / Choice / DateTime / Lookup | Yes/No | {notes} |

---

## 5. Business Rules

| Rule | Description | Enforcement Level |
|---|---|---|
| {Rule name} | {Description of the rule} | Flow / Dataverse BR / Role |

---

## 6. Integrations

| System | Direction | Method | Purpose |
|---|---|---|---|
| {External System} | Inbound / Outbound | HTTP / Connector / Dataverse | {What it does} |

*If no integrations: "None required for this project."*

---

## 7. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | {e.g. "Gallery loads in under 3 seconds with 500 records"} |
| Availability | {e.g. "Must be available during business hours 8am–6pm AEST"} |
| Data Retention | {e.g. "Records archived after 12 months"} |
| Accessibility | {e.g. "App Checker score 0 errors, WCAG 2.1 AA"} |
| Mobile | {e.g. "Canvas App must work on iOS Safari and Chrome Android"} |

---

## 8. Out of Scope

The following items were discussed but are explicitly **not** included in this project:

- {Descoped item 1}
- {Descoped item 2}

---

## 9. Open Questions

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | {Question} | {Business / Dev} | Open / Resolved |

---

## Approval

- [ ] Requirements reviewed by client/stakeholder
- [ ] Requirements approved to proceed to planning
- [ ] Approved by: {Name}, {Date}
