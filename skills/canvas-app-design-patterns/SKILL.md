---
name: canvas-app-design-patterns
description: |
  Visual design patterns and Power Fx colour/layout conventions for Canvas Apps.
  Covers Fluent-aligned colour tokens, accessible contrast ratios, standard
  control sizing, gallery patterns, status badge patterns, and navigation
  patterns — all expressed as Power Fx values ready for Stylist to use.
  Reference whenever designing or reviewing Canvas App UI.
trigger_keywords:
  - canvas design
  - canvas app colour
  - canvas app layout
  - power apps design
  - colour scheme
  - design system
  - gallery pattern
  - status badge
  - fluent design
allowed_tools:
  - Read
---

# Canvas App Design Patterns

## Colour Foundations

### Fluent / Microsoft 365 Aligned
Best for internal enterprise apps used alongside Teams, SharePoint, Outlook.

```
Primary:          RGBA(16, 110, 190, 1)    # Fluent blue
Primary Light:    RGBA(199, 224, 244, 1)
Primary Dark:     RGBA(0, 69, 120, 1)
Background:       RGBA(243, 242, 241, 1)   # Fluent off-white
Surface:          RGBA(255, 255, 255, 1)
Text Primary:     RGBA(32, 31, 30, 1)      # Fluent near-black
Text Secondary:   RGBA(96, 94, 92, 1)
```

### Clean Professional (neutral, works anywhere)
```
Primary:          RGBA(37, 99, 235, 1)     # Blue-600
Primary Light:    RGBA(219, 234, 254, 1)   # Blue-100
Background:       RGBA(248, 250, 252, 1)   # Slate-50
Surface:          RGBA(255, 255, 255, 1)
Text Primary:     RGBA(15, 23, 42, 1)      # Slate-900
Text Secondary:   RGBA(71, 85, 105, 1)     # Slate-500
Text Muted:       RGBA(148, 163, 184, 1)   # Slate-400
Border:           RGBA(226, 232, 240, 1)   # Slate-200
```

### Dark Operational (for dashboards, operations centres)
```
Primary:          RGBA(99, 102, 241, 1)    # Indigo
Background:       RGBA(15, 23, 42, 1)      # Near-black
Surface:          RGBA(30, 41, 59, 1)      # Dark card
Text Primary:     RGBA(248, 250, 252, 1)   # Near-white
Text Secondary:   RGBA(148, 163, 184, 1)
Border:           RGBA(51, 65, 85, 1)
```

---

## Status Colour Conventions

Always use consistent status colours across the whole app. Map to the solution's
choice column values:

```
Pending / In Progress:  RGBA(245, 158, 11, 1)   # Amber
Approved / Complete:    RGBA(16, 185, 129, 1)   # Emerald
Rejected / Error:       RGBA(239, 68, 68, 1)    # Red
Escalated / Warning:    RGBA(139, 92, 246, 1)   # Purple
Cancelled / Inactive:   RGBA(148, 163, 184, 1)  # Grey
```

**Accessible background tints for badges** (use at ~15% opacity for pill fills):
```
Pending bg:   RGBA(245, 158, 11, 0.15)
Approved bg:  RGBA(16, 185, 129, 0.15)
Rejected bg:  RGBA(239, 68, 68, 0.15)
```

---

## Accessibility — Contrast Ratios

Canvas Apps must meet WCAG AA (4.5:1 for normal text, 3:1 for large text).

| Background | Text | Ratio | Result |
|---|---|---|---|
| RGBA(255,255,255,1) | RGBA(15,23,42,1) | 19.4:1 | ✅ AAA |
| RGBA(37,99,235,1) | RGBA(255,255,255,1) | 5.9:1 | ✅ AA |
| RGBA(245,158,11,1) | RGBA(255,255,255,1) | 2.3:1 | ❌ FAIL |
| RGBA(245,158,11,1) | RGBA(15,23,42,1) | 8.4:1 | ✅ AA |
| RGBA(16,185,129,1) | RGBA(255,255,255,1) | 3.2:1 | ✅ AA (large text) |

**Rule**: Never put white text on yellow/amber or light green backgrounds.
Use dark text on those colours instead.

---

## Control Sizing Standards

| Control | Height | Font size | Notes |
|---|---|---|---|
| Primary button | 44 | 14 Bold | Touch-friendly minimum |
| Secondary button | 44 | 14 | Same height for visual alignment |
| Text input | 44 | 14 | Matches button height |
| Dropdown | 44 | 14 | |
| Date picker | 44 | 14 | |
| Gallery row | 64 | 14 body | Enough for 2 lines of text |
| Card | Variable | — | Minimum height 80 |
| Header bar | 56 | 18 Bold | |
| Tab bar (bottom) | 64 | 11 | |
| Icon (in button) | 20×20 | — | |
| Icon (standalone) | 24×24 | — | |

---

## Component Patterns

### Card
Standard card for dashboard items, list items, and form sections:
```
Fill:           ColorSurface (white)
BorderThickness: 1
BorderColor:    ColorBorder
Radius:         12
PaddingLeft:    16
PaddingRight:   16
PaddingTop:     16
PaddingBottom:  16
DropShadow:     Soft (use Canvas App shadow property if available)
```

### Gallery Row (vertical list)
```
TemplateFill:       ColorSurface
OnSelect Fill:      ColorPrimaryLight
Height:             64
PaddingLeft:        16
PaddingRight:       16
Separator visible:  true
Separator color:    ColorBorder
```

### Status Badge (pill label)
```
BorderRadius:   20
PaddingLeft:    12
PaddingRight:   12
PaddingTop:     4
PaddingBottom:  4
Font size:      11
Font weight:    Bold
Fill:           <status background tint>
Color:          <status full colour>
```

Power Fx formula for dynamic status badge colour:
```powerfx
// Badge fill colour
Switch(
    ThisItem.Status,
    'Status (Leave Requests)'.Approved,  RGBA(16, 185, 129, 0.15),
    'Status (Leave Requests)'.Rejected,  RGBA(239, 68, 68, 0.15),
    'Status (Leave Requests)'.Escalated, RGBA(139, 92, 246, 0.15),
    'Status (Leave Requests)'.Cancelled, RGBA(148, 163, 184, 0.15),
    RGBA(245, 158, 11, 0.15)  // Pending (default)
)

// Badge text colour
Switch(
    ThisItem.Status,
    'Status (Leave Requests)'.Approved,  RGBA(16, 185, 129, 1),
    'Status (Leave Requests)'.Rejected,  RGBA(239, 68, 68, 1),
    'Status (Leave Requests)'.Escalated, RGBA(139, 92, 246, 1),
    'Status (Leave Requests)'.Cancelled, RGBA(148, 163, 184, 1),
    RGBA(245, 158, 11, 1)  // Pending (default)
)
```

### Header Bar
```
Fill:           ColorPrimary
Height:         56
Y:              0
Width:          Parent.Width
Title label:
    Font size:  18
    Bold:       true
    Color:      RGBA(255, 255, 255, 1)
    X:          16
Back button (if applicable):
    Icon:       Icon.ChevronLeft
    Color:      RGBA(255, 255, 255, 1)
```

### Empty State (when a gallery has no results)
```
// Show when gallery is empty
Visible: CountRows(galMain.AllItems) = 0
Icon:    Icon.Information  (or contextual icon)
Text:    "No requests found"
Colour:  ColorTextMuted
Centered horizontally and vertically in the gallery area
```

---

## Navigation Patterns

### Top header + screen navigation (recommended for tablet)
- Persistent header bar with app title and back button
- Navigate between screens using `Navigate()` or `Back()`
- No bottom nav bar needed

### Bottom tab bar (recommended for phone/mobile)
- Fixed 64px bar at bottom of screen
- 4-5 icons with labels
- Active tab: ColorPrimary icon
- Inactive tab: ColorTextMuted icon

### Breadcrumb for deep navigation
```powerfx
// Simple breadcrumb label
"Home > My Requests > " & galRequests.Selected.RequestID
```

---

## Layout Principles

1. **Consistent margins**: 16px left/right margin on all content
2. **Vertical rhythm**: 8px or 16px gaps between sections — never arbitrary
3. **Touch targets**: All interactive controls minimum 44×44px
4. **Loading states**: Show a spinner or "Loading..." label while data loads
   (`IsBlank(galMain.AllItems)` check)
5. **Empty states**: Always show a helpful empty state message, never a blank gallery
6. **Error states**: Use `Notify()` for transient errors, visible error labels for form validation
7. **Scroll**: Use vertical scrollable galleries or scrollable containers — avoid
   content that overflows the screen without a scroll mechanism
