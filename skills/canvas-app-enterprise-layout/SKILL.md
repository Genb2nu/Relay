---
name: canvas-app-enterprise-layout
description: |
  Reference pattern for enterprise Canvas Apps with vertical pill navigation.
  Three-zone layout: pill nav left, search bar top, tiles + table in body.
  Component-based with HtmlText containers. Use as a reference ONLY when the
  project or user-provided screenshot matches this pattern — not as a default.
  Stylist decides whether to use this pattern after reading the project context
  or analyzing the user's reference screenshot.
trigger_keywords:
  - pill navigation
  - vertical nav
  - left navigation
  - request management layout
  - approval portal layout
  - enterprise three zone
allowed_tools:
  - Read
---

# Enterprise Pill Nav Layout — Reference Pattern

**This is a named reference pattern, not a default template.**

Stylist uses this when:
- The user provides a screenshot matching this pattern (pill nav left, search top, content body)
- The project context strongly suggests an internal enterprise tool and no screenshot is provided
- The user explicitly asks for this layout style

If a screenshot is provided, always use `canvas-app-design-reading` skill to read it
first — this reference fills in structural detail for the pill nav pattern.

---

## Layout Zones

```
┌────────────────────────────────────────────────────┐
│  [●]  [────────── Search / Filter Bar ──────────] [👤] │
│  [●]                                               │
│  [●]  [ Tile ] [ Tile ] [ Tile ] [ Tile ]          │
│  [●]                                               │
│  [●]  ┌─────────────────────────────────────┐      │
│  [●]  │ Col 1 │ Col 2 │ Col 3 │ Col 4     │      │
│       │───────────────────────────────────  │      │
│       │ row   │ row   │ row   │ row        │      │
│       └─────────────────────────────────────┘      │
└────────────────────────────────────────────────────┘
```

**Zone 1 — Pill nav** (left, fixed, ~70px wide)
**Zone 2 — Search bar** (top right of nav, ~80px tall, pill shape)
**Zone 3 — Content** (tiles row + data table)

---

## HtmlText Container Specs

All visual containers use HtmlText with inline CSS. CSS dimensions must match Canvas control dimensions minus margin×2.

**Pill nav container**: `border-radius:25px; width:30px; height:310px` (for 50px×350px control)
**Card/tile**: `border-radius:15px; height:260px` (for 280px tall control)
**Search bar**: `border-radius:30px` (wide pill)
**Standard shadow**: `box-shadow:0 3px 10px 5px rgba(0,0,0,0.12)`
**Card shadow**: `box-shadow:0 5px 8px 5px rgba(0,0,0,0.12)`

Colours are NOT defined here — taken from `design-system.md`.

---

## Component Structure

```
Screen
  ├── MENU              (pill nav — full 5 icons, or compact 2 icons)
  ├── SEARCH_BAR        (wide pill — dropdown + search input + reset)
  ├── TILE_ROW          (N metric cards side by side)
  ├── DATA_TABLE        (gallery with column header labels above)
  └── POPUP             (modal overlay — hidden by default)
```

## Nav Component
- Pill background via HtmlText
- Icons overlaid as separate controls (HtmlText can't receive clicks)
- Active state: `If(gblScreen="Home", FullOpacity, HalfOpacity)` on each icon
- Compact variant: fewer icons, shorter pill, shown conditionally by role

## Search Bar
- HtmlText pill background (primary colour)
- Dropdown (view selector) + TextInput (search) + Icon (reset) overlaid
- Reset: `Reset(drpView); Reset(txtSearch); Set(varSearchText, "")`

## Tile Cards
- HtmlText card background per tile
- Labels for number (large, bold, white) and name (small, white) overlaid
- Widths: `(ContentArea.Width - gaps) / tileCount` — not hardcoded pixels

## Data Table
- Vertical gallery, column headers as separate Labels above
- Gallery template: Height=52px, separator visible
- Items: `Filter(Switch(drpView.Selected.Value, ...), search condition)`
- Status badges: coloured pills using semantic colours from design-system.md

## Popup
- Full-screen Rectangle overlay (RGBA(0,0,0,0.4))
- White card centred, border-radius:15px
- Must be last in Z-order to render on top

---

## Standard Improvements

Always add these — they were absent in the reference but should be standard:

1. Empty gallery state — message + icon when no rows
2. Loading indicator — spinner while data loads
3. Status badges — coloured pills not plain text
4. Active nav indicator — current screen icon distinguished
5. Responsive tile widths — Parent.Width calculations not hardcoded pixels
6. Row hover state — light tint on gallery template
7. Search result count — "N results" label
8. Error state — IfError on data source
