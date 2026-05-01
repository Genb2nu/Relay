---
name: canvas-app-screen-layout
description: |
  Six standard screen layout archetypes for Canvas Apps with exact zone
  dimensions, responsive formulas, and ASCII zone diagrams. Stylist references
  this when assigning layouts to screens. Forge references this when
  positioning controls.
trigger_keywords:
  - screen layout
  - canvas layout
  - zone dimensions
  - layout archetype
  - screen pattern
  - master detail
  - dashboard layout
  - pill nav
allowed_tools:
  - Read
---

# Canvas App Screen Layout Archetypes

Use these archetypes when designing Canvas App screen layouts. Each defines named zones
with exact pixel positions. Stylist selects the archetype per screen; Forge positions
controls within the zones.

---

## 1. Dashboard

**Best for:** KPI monitoring, overview screens, executive summaries
**Orientation:** Landscape (1366 x 768 minimum)

```
┌─────────────────────────────────────────────────────────────┐
│ Header Bar (0, 0) — 1366 x 56                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                          │
│  │ KPI │ │ KPI │ │ KPI │ │ KPI │  ← KPI Row (16,72) 1334w │
│  │ Card│ │ Card│ │ Card│ │ Card│    Height: 120            │
│  └─────┘ └─────┘ └─────┘ └─────┘                          │
│                                                             │
│  ┌──────────────────────┐ ┌──────────────────────┐         │
│  │                      │ │                      │         │
│  │   Chart / Grid       │ │   Chart / Grid       │         │
│  │   Left Panel         │ │   Right Panel        │         │
│  │   (16,208) 653x544   │ │   (685,208) 665x544  │         │
│  │                      │ │                      │         │
│  └──────────────────────┘ └──────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**Zone dimensions:**
| Zone | X | Y | Width | Height | Formula |
|---|---|---|---|---|---|
| Header | 0 | 0 | App.Width | 56 | — |
| KPI Row | 16 | 72 | App.Width - 32 | 120 | Per card: (App.Width - 32 - 48) / 4 |
| Left Panel | 16 | 208 | (App.Width - 48) / 2 | App.Height - 224 | — |
| Right Panel | (App.Width/2) + 8 | 208 | (App.Width - 48) / 2 | App.Height - 224 | — |

---

## 2. Master-Detail

**Best for:** Record browsing, case management, list + form views
**Orientation:** Landscape (1366 x 768 minimum)

```
┌─────────────────────────────────────────────────────────────┐
│ Header Bar (0, 0) — 1366 x 56                               │
├───────────────┬─────────────────────────────────────────────┤
│               │                                             │
│  List Panel   │   Detail Panel                              │
│  (0, 56)      │   (400, 56)                                 │
│  400 x 712    │   966 x 712                                 │
│               │                                             │
│  ┌─────────┐  │   ┌─────────────────────────────────────┐   │
│  │ Search  │  │   │ Record Header                       │   │
│  ├─────────┤  │   ├─────────────────────────────────────┤   │
│  │ Gallery │  │   │                                     │   │
│  │ (rows)  │  │   │  Form Fields / Tabs                 │   │
│  │         │  │   │                                     │   │
│  │         │  │   │                                     │   │
│  └─────────┘  │   └─────────────────────────────────────┘   │
└───────────────┴─────────────────────────────────────────────┘
```

**Zone dimensions:**
| Zone | X | Y | Width | Height | Formula |
|---|---|---|---|---|---|
| Header | 0 | 0 | App.Width | 56 | — |
| List Panel | 0 | 56 | 400 | App.Height - 56 | — |
| Search Box | 16 | 72 | 368 | 44 | — |
| Gallery | 0 | 132 | 400 | App.Height - 132 | — |
| Detail Panel | 400 | 56 | App.Width - 400 | App.Height - 56 | — |

---

## 3. Form-Focused

**Best for:** Data entry, submissions, wizard steps
**Orientation:** Either (works landscape or portrait)

```
┌─────────────────────────────────────────────────────────────┐
│ Header Bar (0, 0) — 1366 x 56                               │
├─────────────────────────────────────────────────────────────┤
│ Progress / Steps (0, 56) — 1366 x 48 (optional)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│         ┌─────────────────────────────┐                     │
│         │                             │                     │
│         │  Form Card                  │                     │
│         │  Center-aligned             │                     │
│         │  (App.Width-600)/2, 120     │                     │
│         │  600 x varies              │                     │
│         │                             │                     │
│         │  [Fields...]                │                     │
│         │                             │                     │
│         │  ┌──────┐  ┌──────┐        │                     │
│         │  │Cancel│  │Submit│        │                     │
│         │  └──────┘  └──────┘        │                     │
│         └─────────────────────────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Zone dimensions:**
| Zone | X | Y | Width | Height | Formula |
|---|---|---|---|---|---|
| Header | 0 | 0 | App.Width | 56 | — |
| Steps | 0 | 56 | App.Width | 48 | Optional |
| Form Card | (App.Width - 600) / 2 | 120 | 600 | dynamic | Center-aligned |
| Button Row | Form.X + Form.Width - 260 | Form.Y + Form.Height + 16 | 260 | 44 | Right-aligned in card |

---

## 4. Mobile-First

**Best for:** Field workers, quick approvals, phone-optimized
**Orientation:** Portrait (640 x 1136)

```
┌─────────────────────────┐
│ Header (0,0) 640x56     │
├─────────────────────────┤
│                         │
│  Content Area           │
│  (0, 56)                │
│  640 x 1020             │
│                         │
│  ┌───────────────────┐  │
│  │ Card              │  │
│  └───────────────────┘  │
│  ┌───────────────────┐  │
│  │ Card              │  │
│  └───────────────────┘  │
│                         │
├─────────────────────────┤
│ Tab Bar (0,1076) 640x60 │
│  [🏠] [📋] [👤] [⚙️]    │
└─────────────────────────┘
```

**Zone dimensions:**
| Zone | X | Y | Width | Height | Formula |
|---|---|---|---|---|---|
| Header | 0 | 0 | App.Width | 56 | — |
| Content | 0 | 56 | App.Width | App.Height - 116 | Between header and tab bar |
| Tab Bar | 0 | App.Height - 60 | App.Width | 60 | Anchored to bottom |
| Tab Button | index * (App.Width / tabCount) | App.Height - 60 | App.Width / tabCount | 60 | Even distribution |

---

## 5. Pill Nav Enterprise

**Best for:** Internal admin tools, multi-section apps with heavy content
**Orientation:** Landscape (1366 x 768 minimum)

```
┌─────────────────────────────────────────────────────────────┐
│ Header Bar (0, 0) — 1366 x 56                               │
├──────┬──────────────────────────────────────────────────────┤
│      │ Search + Actions (86, 56) — 1280 x 48               │
│ Pill ├──────────────────────────────────────────────────────┤
│ Nav  │                                                      │
│      │  Content Area (86, 104)                              │
│  70  │  1264 x 648                                          │
│  x   │                                                      │
│ 712  │  ┌───────┐ ┌───────┐ ┌───────┐                      │
│      │  │ Tile  │ │ Tile  │ │ Tile  │  ← Summary tiles     │
│[icon]│  └───────┘ └───────┘ └───────┘                      │
│[icon]│                                                      │
│[icon]│  ┌─────────────────────────────────────────────┐     │
│[icon]│  │ Data Table / Gallery                        │     │
│[icon]│  │                                             │     │
│      │  └─────────────────────────────────────────────┘     │
└──────┴──────────────────────────────────────────────────────┘
```

**Zone dimensions:**
| Zone | X | Y | Width | Height | Formula |
|---|---|---|---|---|---|
| Header | 0 | 0 | App.Width | 56 | — |
| Pill Nav | 0 | 56 | 70 | App.Height - 56 | Fixed left |
| Pill Icon | 8 | 56 + (index * 70) | 54 | 54 | Per icon |
| Search Bar | 86 | 56 | App.Width - 102 | 48 | — |
| Content | 86 | 104 | App.Width - 102 | App.Height - 120 | — |
| Summary Tiles | 86 | 120 | (App.Width - 134) / 3 | 100 | 3 tiles, 16px gap |
| Data Table | 86 | 236 | App.Width - 102 | App.Height - 252 | Below tiles |

---

## 6. Tab Navigation

**Best for:** Multi-section categorized apps, settings screens
**Orientation:** Either

```
┌─────────────────────────────────────────────────────────────┐
│ Header Bar (0, 0) — 1366 x 56                               │
├─────────────────────────────────────────────────────────────┤
│ Tab Strip (0, 56) — 1366 x 48                               │
│  [Tab A]  [Tab B]  [Tab C]  [Tab D]                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tab Content Area (16, 120)                                 │
│  1334 x 632                                                 │
│                                                             │
│  (content varies per tab)                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Zone dimensions:**
| Zone | X | Y | Width | Height | Formula |
|---|---|---|---|---|---|
| Header | 0 | 0 | App.Width | 56 | — |
| Tab Strip | 0 | 56 | App.Width | 48 | — |
| Tab Button | index * tabWidth | 56 | App.Width / tabCount | 48 | Even |
| Active Indicator | tab.X | 100 | tab.Width | 4 | Underline bar |
| Content | 16 | 120 | App.Width - 32 | App.Height - 136 | — |

---

## Responsive Width Formulas

Use these formulas when controls need to adapt to different app widths:

```
// Full width with margin
Width: App.Width - (2 * SpaceXL)

// Half width (two-column layout)
Width: (App.Width - (3 * SpaceMD)) / 2

// Third width (three-column)
Width: (App.Width - (4 * SpaceMD)) / 3

// Gallery row full width
Width: Parent.Width

// Centered card
X: (App.Width - CardWidth) / 2

// Right-aligned button
X: Parent.Width - ButtonWidth - SpaceMD
```

---

## Standard Improvements Checklist

Every screen should include these UX patterns (remind Forge if missing):

| Pattern | When | Control |
|---|---|---|
| Empty gallery state | Gallery items count = 0 | Label: "No records found" centered in gallery |
| Loading indicator | While data is loading | Spinner or "Loading..." label with Visible=IsLoading |
| Status badge | Any record with status field | Pill-shaped label with status colour |
| Error banner | After failed submit/save | Red banner at top with error message |
| Confirmation | After destructive action | Dialog or overlay: "Are you sure?" |
| Disabled state | When form is incomplete | Submit button DisplayMode=If(formValid, Edit, Disabled) |
