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
  'Status (<Main Table>)'.Approved,  RGBA(16, 185, 129, 0.15),
  'Status (<Main Table>)'.Rejected,  RGBA(239, 68, 68, 0.15),
  'Status (<Main Table>)'.Escalated, RGBA(139, 92, 246, 0.15),
  'Status (<Main Table>)'.Cancelled, RGBA(148, 163, 184, 0.15),
    RGBA(245, 158, 11, 0.15)  // Pending (default)
)

// Badge text colour
Switch(
    ThisItem.Status,
  'Status (<Main Table>)'.Approved,  RGBA(16, 185, 129, 1),
  'Status (<Main Table>)'.Rejected,  RGBA(239, 68, 68, 1),
  'Status (<Main Table>)'.Escalated, RGBA(139, 92, 246, 1),
  'Status (<Main Table>)'.Cancelled, RGBA(148, 163, 184, 1),
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

## Wireframe HTML Patterns

Use these patterns ONLY for `docs/wireframes.html` during Stylist Mode C.
This is a planning artifact for human review, not a production web UI.

### Base CSS Pattern (inline only)
```html
<style>
  :root {
    --bg: #f8fafc;
    --surface: #ffffff;
    --border: #e2e8f0;
    --text: #0f172a;
    --muted: #64748b;
    --nav: #1d4ed8;
    --pending: #f59e0b;
    --active: #10b981;
    --signed: #065f46;
    --rejected: #ef4444;
    --escalated: #8b5cf6;
  }

  body { margin: 0; padding: 24px; background: var(--bg); color: var(--text); font-family: Segoe UI, Arial, sans-serif; }
  .screen { margin: 0 0 32px; border: 1px solid var(--border); border-radius: 16px; background: var(--surface); overflow: hidden; }
  .screen-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: #eff6ff; border-bottom: 1px solid var(--border); }
  .screen-body { display: grid; grid-template-columns: 88px 1fr; min-height: 480px; }
  .pill-nav { padding: 16px 10px; background: #f1f5f9; border-right: 1px solid var(--border); }
  .pill { margin: 0 0 10px; padding: 10px 12px; border-radius: 999px; background: #dbeafe; color: #1e3a8a; font-size: 12px; text-align: center; }
  .content { padding: 20px; }
  .zone { margin: 0 0 16px; padding: 16px; border: 1px dashed #cbd5e1; border-radius: 12px; background: #fff; }
  .annotation { display: inline-block; margin: 0 8px 8px 0; padding: 4px 10px; border-radius: 999px; background: #e2e8f0; color: #334155; font-size: 12px; font-weight: 600; }
  .flow-arrow { margin: 12px 0; color: var(--muted); font-size: 13px; }
  .gallery-row, .table-row { display: grid; grid-template-columns: 1.4fr 1fr 120px; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); }
  .field-list { display: grid; grid-template-columns: repeat(2, minmax(180px, 1fr)); gap: 12px; }
  .field { padding: 10px 12px; border: 1px solid var(--border); border-radius: 10px; background: #f8fafc; color: var(--muted); font-size: 13px; }
  .badge { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
  .badge.pending { background: rgba(245, 158, 11, 0.15); color: var(--pending); }
  .badge.active { background: rgba(16, 185, 129, 0.15); color: var(--active); }
  .badge.signed { background: rgba(6, 95, 70, 0.12); color: var(--signed); }
  .badge.rejected { background: rgba(239, 68, 68, 0.15); color: var(--rejected); }
  .badge.escalated { background: rgba(139, 92, 246, 0.15); color: var(--escalated); }
</style>
```

### Pill Navigation Screen Pattern
```html
<section class="screen">
  <div class="screen-header">
    <div>
      <strong>scrDashboard</strong>
      <div>Persona: Employee</div>
    </div>
    <div>
      <span class="annotation">Visible to: Employee</span>
      <span class="annotation">Primary flow: Submit request</span>
    </div>
  </div>
  <div class="screen-body">
    <aside class="pill-nav">
      <div class="pill">Home</div>
      <div class="pill">Requests</div>
      <div class="pill">Balance</div>
    </aside>
    <main class="content">
      <div class="zone">Header bar / summary cards</div>
      <div class="zone">Gallery placeholder</div>
      <div class="flow-arrow">Flow: scrDashboard -> scrRequestForm -> scrConfirmation</div>
    </main>
  </div>
</section>
```

### Status Badge Pattern
Use requirement-aligned status colour labels in the wireframes. Default mapping:

```html
<span class="badge pending">Pending</span>
<span class="badge active">Active</span>
<span class="badge signed">Signed</span>
<span class="badge rejected">Rejected</span>
<span class="badge escalated">Escalated</span>
```

### Gallery Row Placeholder Pattern
```html
<div class="zone">
  <div class="gallery-row">
    <strong>Request-001</strong>
    <span>Start Date / Summary</span>
    <span class="badge pending">Pending</span>
  </div>
  <div class="gallery-row">
    <strong>Request-002</strong>
    <span>Start Date / Summary</span>
    <span class="badge active">Active</span>
  </div>
</div>
```

### Form Field Layout Pattern
```html
<div class="zone">
  <div class="field-list">
    <div class="field">Request Type</div>
    <div class="field">Start Date</div>
    <div class="field">End Date</div>
    <div class="field">Manager</div>
    <div class="field">Notes (multiline)</div>
    <div class="field">Attachment area</div>
  </div>
</div>
```

### MDA Table View Pattern
```html
<section class="screen">
  <div class="screen-header">
    <div>
      <strong>MDA: Approval Workspace</strong>
      <div>Persona: Manager</div>
    </div>
    <span class="annotation">Visible to: Manager, Admin</span>
  </div>
  <div class="content">
    <div class="zone">View selector / command bar placeholder</div>
    <div class="zone">
      <div class="table-row"><strong>ID</strong><strong>Status</strong><strong>Owner</strong></div>
      <div class="table-row"><span>Record-001</span><span class="badge pending">Pending</span><span>User A</span></div>
      <div class="table-row"><span>Record-002</span><span class="badge signed">Signed</span><span>User B</span></div>
    </div>
    <div class="zone">
      <strong>Form fields</strong>
      <div class="field-list">
        <div class="field">Status</div>
        <div class="field">Decision</div>
        <div class="field">Comments</div>
        <div class="field">Audit history subgrid</div>
      </div>
    </div>
  </div>
</section>
```

### Screen Annotation Label Style
- Use compact pill annotations for persona visibility, sensitive areas, and approval-only actions
- Place annotations near the relevant zone, not in a separate legend only
- Prefer labels like `Visible to: Manager`, `Sensitive data`, `Approval action`, `Read-only for Employee`
- Keep annotation text short and explicit so Auditor and Warden can review without guessing intent

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
