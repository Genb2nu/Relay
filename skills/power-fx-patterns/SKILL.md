---
name: power-fx-patterns
description: |
  Proven Power Fx patterns for Canvas Apps on Dataverse. Covers current-user
  filtering, lookup column comparisons, delegation-safe queries, balance
  calculations, navigation, and common anti-patterns. Grows with every project
  — add learnings here so they're never re-discovered. Reference whenever
  writing or reviewing Power Fx formulas.
trigger_keywords:
  - power fx
  - powerfx
  - canvas formula
  - filter formula
  - current user
  - delegation
  - lookup column
  - patch formula
  - gallery items
allowed_tools:
  - Read
---

# Power Fx Patterns

> **Publisher prefix**: All examples below use `<prefix>_` as a placeholder.
> Replace with the actual prefix from `.relay/state.json` (e.g. `cr`, `swo`, `con`).
> Forge reads the prefix from state.json — never hardcode `cr_` in generated code.

## Current User — Filtering Dataverse Lookups

### Problem
`Employee.Id = varCurrentUserId` ❌ — fails at runtime. DataEntity (Dataverse
lookup) does not expose `.Id` in Power Fx. `varCurrentUserId` from
`Office365Users.MyProfileV2().id` returns an AAD Object ID (GUID string), which
doesn't match how Dataverse stores the lookup.

### Solution
Use the Primary Email to match the current user against a systemuser lookup:

```powerfx
// Filter a gallery to show only the current user's records
Filter(
    'Leave Requests',
    Employee.'Primary Email' = User().Email
)
```

```powerfx
// Alternative: use Owner field if the table is user-owned
Filter(
    'Leave Requests',
    Owner.User = User()
)
```

```powerfx
// LookUp the current user's systemuser record for use in Patch
Set(
    varCurrentUser,
    LookUp(Users, 'Primary Email' = User().Email)
)
```

**Why**: `User().Email` returns the authenticated user's UPN which matches
`systemuser.internalemailaddress`. This is the idiomatic Power Fx pattern.

---

## Delegation — Safe Filtering

### Delegable operations on Dataverse (safe for large tables)
```powerfx
// Equality on indexed columns — delegable ✅
Filter('Leave Requests', Status = 'Status (Leave Requests)'.Pending)

// StartsWith on text columns — delegable ✅
Filter('Leave Requests', StartsWith(RequestID, "LR-"))

// Lookup relationship filter — delegable ✅
Filter('Leave Requests', Employee.'Primary Email' = User().Email)

// Multiple conditions — delegable ✅
Filter(
    'Leave Requests',
    Employee.'Primary Email' = User().Email &&
    Status = 'Status (Leave Requests)'.Pending
)
```

### Non-delegable operations (only process first 500/2000 records) ⚠️
```powerfx
// Search() — non-delegable
Search('<Table>', TextInput.Text, "<prefix>_name")  // ⚠️

// EndsWith() — non-delegable
Filter('Leave Requests', EndsWith(RequestID, "2026"))  // ⚠️

// Len(), Mid(), Left() on filter — non-delegable  // ⚠️

// CountRows() on a table — non-delegable
CountRows(Filter('Leave Requests', ...))  // ⚠️ Use CountIf() instead
```

### Safe pattern for search on large tables
```powerfx
// Use StartsWith instead of Search where possible
Filter(
    'Leave Requests',
    StartsWith(RequestID, SearchInput.Text) ||
    Employee.'Primary Email' = User().Email
)
```

---

## Patch — Creating and Updating Records

### Create a new record
```powerfx
Patch(
    'Leave Requests',
    Defaults('Leave Requests'),
    {
        'Leave Type': ddLeaveType.Selected,
        Employee: varCurrentUser,
        'Start Date': dpStartDate.SelectedDate,
        'End Date': dpEndDate.SelectedDate,
        'Number of Days': nDays,
        Status: 'Status (Leave Requests)'.Pending,
        'Submitted On': Now()
    }
);
Notify("Leave request submitted successfully", NotificationType.Success);
Navigate(scrMyRequests)
```

### Update an existing record
```powerfx
Patch(
    'Leave Requests',
    galRequests.Selected,
    {
        Status: 'Status (Leave Requests)'.Cancelled,
        'Employee Comments': txtComments.Text
    }
);
Refresh('Leave Requests')
```

### Patch with error handling
```powerfx
If(
    IsError(
        Patch(
            'Leave Requests',
            Defaults('Leave Requests'),
            {Status: 'Status (Leave Requests)'.Pending}
        )
    ),
    Notify("Failed to submit request. Please try again.", NotificationType.Error),
    Notify("Request submitted!", NotificationType.Success);
    Navigate(scrHome)
)
```

---

## Choice Columns — Option Sets

### Referencing a choice value in a filter
```powerfx
// Use the fully qualified choice reference
Filter('Leave Requests', Status = 'Status (Leave Requests)'.Pending)

// Do NOT use the integer value directly — it breaks with label changes
Filter('Leave Requests', Status = 1)  // ❌ fragile
```

### Displaying a choice label
```powerfx
// In a gallery or label
Text(ThisItem.Status)

// For conditional formatting
If(
    ThisItem.Status = 'Status (Leave Requests)'.Approved,
    RGBA(16, 185, 129, 1),  // green
    If(
        ThisItem.Status = 'Status (Leave Requests)'.Rejected,
        RGBA(239, 68, 68, 1),  // red
        RGBA(245, 158, 11, 1)  // amber (pending/other)
    )
)
```

---

## Balance Calculation Pattern

### Pattern for leave balance display
```powerfx
// Remaining days — always recalculate, never store as static
// <prefix>_remaining = <prefix>_entitled - <prefix>_used - <prefix>_pending

// In a gallery showing leave types and balances
With(
    {
        balance: LookUp(
            'Leave Balances',
            Employee.'Primary Email' = User().Email &&
            'Leave Type'.<prefix>_name = ThisItem.<prefix>_name &&
            Year = Year(Today())
        )
    },
    balance.Remaining & " / " & balance.Entitled & " days"
)
```

---

## Navigation

### Navigate between screens with context
```powerfx
// Pass selected record to a detail screen
Navigate(
    scrRequestDetail,
    ScreenTransition.Cover,
    {selectedRequest: galRequests.Selected}
);
```

### Back navigation
```powerfx
Back()
// or
Navigate(scrHome, ScreenTransition.UnCover)
```

---

## Date Calculations

### Calculate working days between dates
```powerfx
// Simple calendar days (not working days)
DateDiff(dpStartDate.SelectedDate, dpEndDate.SelectedDate, TimeUnit.Days) + 1

// Validate date range
If(
    dpEndDate.SelectedDate < dpStartDate.SelectedDate,
    Notify("End date must be after start date", NotificationType.Error),
    Set(varDays, DateDiff(dpStartDate.SelectedDate, dpEndDate.SelectedDate, TimeUnit.Days) + 1)
)
```

---

## Common Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| `Employee.Id = varUserId` | DataEntity has no .Id in Power Fx | Use `Employee.'Primary Email' = User().Email` |
| `Search()` on large tables | Non-delegable — only searches first 2000 rows | Use `Filter()` with `StartsWith()` |
| `CountRows(table)` | Non-delegable | Use `CountIf(table, condition)` |
| Hardcoded choice integers | Breaks if option set changes | Use fully qualified choice references |
| `Collect()` in OnStart for large tables | Slow, memory-heavy | Use direct `Filter()` references |
| `UpdateContext()` vs `Set()` | UpdateContext is screen-local | Use `Set()` for cross-screen variables |
| No error handling in Patch | Silent failures confuse users | Always wrap Patch in `IsError()` check |
