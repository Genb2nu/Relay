---
name: canvas-mcp-prompt-patterns
description: |
  Library of Canvas Authoring MCP prompt patterns — what works, what doesn't,
  and lessons learned from real projects. Stylist references this when writing
  MCP prompt sections in design-system.md. Grows after each project.
trigger_keywords:
  - mcp prompt
  - generate-canvas-app
  - canvas prompt
  - prompt pattern
  - canvas generation
allowed_tools:
  - Read
---

# Canvas MCP Prompt Patterns

This skill is a living library of prompt patterns for the Canvas Authoring MCP
(/generate-canvas-app and /edit-canvas-app). Stylist references this when writing
MCP prompts in design-system.md to avoid known bad patterns.

---

## Prompt Structure (proven effective)

A good /generate-canvas-app prompt follows this structure:

```
1. App purpose (1 sentence)
2. Screen name and purpose
3. Layout zones with EXACT positions (X, Y, Width, Height)
4. Controls per zone with:
   - Control type (MUST say "modern" explicitly)
   - Visual properties (Fill, Color, Font, Size, BorderRadius — use RGBA values)
   - Data binding (Items, Default, Value — use actual table/column names)
5. Navigation connections between screens
```

---

## Known Good Patterns

### Pattern: Explicit RGBA in prompt
```
Header rectangle at 0,0 size 1366x56 with Fill=RGBA(37,99,235,1)
```
**Result:** MCP applies the exact colour. No ambiguity.

### Pattern: Modern control specification
```
Add a modern Button control named btnSubmit at X=500, Y=600, Width=200, Height=44
with Fill=RGBA(37,99,235,1), Color=RGBA(255,255,255,1), BorderRadius=8
```
**Result:** Creates modern variant with correct styling.

### Pattern: Gallery with row template
```
Modern Gallery control named galRequests at X=0, Y=132, Width=400, Height=636
Items: Filter(<prefix>_leaverequests, <prefix>_requestorid = User().Email)
Row height: 64
Row template contains:
  - Label for Title at relative X=16, Y=8, showing ThisItem.<prefix>_title
  - Label for Date at relative X=16, Y=36, showing Text(ThisItem.createdon, "dd MMM yyyy")
  - Status badge at relative X=300, Y=16
```
**Result:** Gallery with properly structured rows.

---

## Known Bad Patterns (AVOID)

### Bad: Vague colour instruction
```
Make the header blue
```
**Result:** MCP uses an arbitrary blue, often RGBA(0,0,255,1) or default black.
**Fix:** Always specify exact RGBA values.

### Bad: No control type specified
```
Add a button for submit
```
**Result:** MCP may use classic Button control.
**Fix:** Always say "modern Button control".

### Bad: No dimensions
```
Put a gallery on the left side
```
**Result:** Gallery may overflow screen or be tiny.
**Fix:** Always specify X, Y, Width, Height.

### Bad: Relative positioning without anchors
```
Place the form below the header
```
**Result:** Unpredictable Y position.
**Fix:** Use exact coordinates: "Form at X=100, Y=120, Width=600, Height=500"

---

## /edit-canvas-app Patterns

### Pattern: Logic wiring (preserves visual properties)
```
For the button named btnSubmit:
- Set OnSelect to: Patch(<prefix>_leaverequests, Defaults(<prefix>_leaverequests), {<fields>}); Navigate(ScreenSuccess)
DO NOT MODIFY: X, Y, Width, Height, Fill, Color, Font, Size, FontWeight,
RadiusTopLeft, RadiusTopRight, RadiusBottomLeft, RadiusBottomRight,
BorderColor, BorderThickness, PaddingTop, PaddingBottom, PaddingLeft, PaddingRight
```
**Result:** Only logic properties change; visual layout preserved.

### Pattern: Data binding for gallery
```
Set the Items property of galRequests to:
SortByColumns(Filter(<prefix>_leaverequests, <prefix>_requestorid = User().Email), "createdon", SortOrder.Descending)
DO NOT MODIFY visual properties of the gallery or its template controls.
```

---

## Lessons Learned

| Lesson | Source | Impact |
|---|---|---|
| MCP defaults to classic controls if not told "modern" | LRS pilot | All controls wrong variant |
| MCP ignores colours when prompt says "professional" without RGBA | LRS pilot | Black/default fills |
| Gallery Items must use full table logical name with prefix | LRS pilot | Data source errors |
| /edit-canvas-app can overwrite visual properties if not constrained | Design discussion | Layout destroyed |

---

## Adding to This Library

After each project, append new entries:
1. What prompt text was used
2. What MCP actually produced
3. Quality rating (Good / Acceptable / Bad)
4. Lesson learned

Format:
```markdown
### Pattern: <short name>
**Prompt:** `<exact text sent to MCP>`
**Result:** <what happened>
**Rating:** Good | Acceptable | Bad
**Lesson:** <what to do differently>
```
