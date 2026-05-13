# SimplifyNext Canvas App Patterns

## Purpose

Standard Canvas App patterns that Forge-Canvas must follow for all SimplifyNext
projects. All Canvas Apps must pass App Checker at 0 errors before sign-off.

---

## App Structure Standards

### Screen Naming

Every screen name must:
- Use PascalCase
- End with `Screen`
- Be descriptive of purpose

Examples: `HomeScreen`, `RequestListScreen`, `RequestDetailScreen`, `ApprovalQueueScreen`

### Required Screens (every app)

| Screen | Purpose | Personas |
|---|---|---|
| `HomeScreen` | Navigation hub | All personas |
| `{Entity}ListScreen` | Gallery of records | Main user personas |
| `{Entity}DetailScreen` | Record detail + edit | Create/edit personas |
| `ErrorScreen` | Error display | All (internal navigation) |

### Navigation Pattern

Use `App.OnStart` to:
1. Set global variables (user, role, theme colours)
2. Preload critical data collections
3. Navigate to `HomeScreen`

Use `Navigate()` for all screen transitions — never use `Back()` in production
screens (unreliable on mobile).

---

## Power Fx Standards

### Data Loading

Always use `ClearCollect()` with `Filter()` rather than loading entire tables:

```powershell
# Good
ClearCollect(
  colRequests,
  Filter(
    '{prefix}_requests',
    '{prefix}_assignedto' = varCurrentUser.Email,
    statuscode = 1
  )
);

# Bad — loads entire table
ClearCollect(colRequests, '{prefix}_requests');
```

### Error Handling

Every `Patch()` call must check for errors:

```powershell
If(
  IsError(
    Patch(
      '{prefix}_requests',
      Defaults('{prefix}_requests'),
      { '{prefix}_title': txtTitle.Text }
    )
  ),
  Notify("Error saving request. Please try again.", NotificationType.Error),
  Notify("Request saved successfully.", NotificationType.Success);
  Navigate(RequestListScreen)
)
```

### Delegation Warning Prevention

Always use delegable filter conditions:
- Use `Filter()` with indexed columns
- Never use `Search()` on large datasets (>2000 rows without explicit delegation)
- Use `StartsWith()` instead of `in` for text search

---

## UI Component Standards

### Gallery Pattern

All galleries must:
- Set `Items` to a local collection (preloaded in `OnStart` or screen's `OnVisible`)
- Include empty state message: `If(IsEmpty(colRequests), Visible = true)`
- Use `TemplateSize` based on content, not fixed pixels

### Form Pattern

All forms must use `EditForm` or `DisplayForm` connected to a Dataverse table.
Never build forms with individual input controls manually — use the Form control.

```
EditForm (FormRequest)
  DataSource: '{prefix}_requests'
  OnSuccess: Notify("Saved"); Navigate(RequestListScreen)
  OnFailure: Notify("Error: " & FormRequest.Error.Message)
```

### Delegation-Safe Search

```powershell
// Search that delegates to Dataverse
Filter(
  '{prefix}_requests',
  StartsWith('{prefix}_title', txtSearch.Text) &&
  statuscode <> 3  // exclude cancelled
)
```

---

## Accessibility Requirements

Every app must:
- Set `AccessibleLabel` on every interactive control
- Set `TabIndex` logically (0 for skip, positive for order)
- Ensure minimum contrast ratio 4.5:1 for text
- Test with Screen Reader (App Checker accessibility score: 0 errors)

---

## App Checker — Zero Errors Policy

Before sign-off, run App Checker and verify 0 errors in all categories:

| Category | Common Issues |
|---|---|
| Formulas | Delegation warnings, deprecated functions |
| Runtime | Missing data source, invalid field references |
| Accessibility | Missing labels, low contrast |
| Performance | Unnecessary `LoadData`, large images |
| Data source | Incorrect table/column names |

If any category shows errors, Forge-Canvas must fix them before Sentinel
can approve the Canvas App.

---

## Offline-Capable Pattern (if required by plan)

For apps that need offline support:
1. Use `LoadData()` / `SaveData()` for local caching
2. Test with network disabled in browser DevTools
3. Include a sync button that calls `ClearCollect()` from Dataverse
4. Show sync status in the app header
