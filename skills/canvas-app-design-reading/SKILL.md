---
name: canvas-app-design-reading
description: |
  How to analyze a screenshot or wireframe and extract a Canvas App design
  system from it. Used by Stylist when the user provides a reference image.
  Produces a project-specific design-system.md that captures layout, structure,
  component patterns, and visual style — without assuming any fixed template.
trigger_keywords:
  - screenshot
  - wireframe
  - reference design
  - looks like
  - similar to
  - design reference
  - analyze design
  - build like this
  - use this design
  - match this style
allowed_tools:
  - Read
  - Write
---

# Canvas App Design Reading

When the user provides a screenshot, wireframe, or reference image of a design
they want to follow, Stylist reads it using this skill and produces a
project-specific design-system.md. Do NOT assume a fixed template — every
design reference is different and must be read fresh.

---

## Step 1 — Identify the layout zones

Look at the overall structure first. What are the major zones?

**Common layout patterns (read which one applies — don't assume):**

```
Pattern A: Left nav + content
[Nav] [──────────────────────]
[Nav] [  Header/Filter bar   ]
[Nav] [  Content body        ]
[Nav] [  (tiles + table)     ]

Pattern B: Top nav + content
[────────── Top Navigation ──]
[  Sidebar? ] [  Content     ]
[           ] [  (body)      ]

Pattern C: Tab navigation
[  Tab 1 | Tab 2 | Tab 3    ]
[  Content for selected tab  ]

Pattern D: Dashboard grid
[──────── Header/KPIs ───────]
[  Chart  ] [ Chart ] [Chart ]
[  Table  ──────────────────]

Pattern E: Mobile (phone format)
[  Header                    ]
[  Content scrollable        ]
[  Bottom tab bar            ]

Pattern F: Split view
[  List/sidebar  ] [ Detail  ]
```

Name the pattern you see. If it doesn't match any of the above, describe it
in your own words in the design-system.md.

---

## Step 2 — Read the navigation

What navigation does the design use?

**Questions to answer:**
- Where is it positioned? (left, top, bottom, floating)
- What shape? (pill, rectangle, flat bar, tabs)
- How many items?
- Are there labels under icons, or icons only?
- Is there a visible active/selected state?
- Is there a role-conditional variant (compact vs full)?

**Extract what you can see:**
- Approximate dimensions (is it wide or narrow? tall or short?)
- Visual style: rounded corners? shadow? border?
- Icon colour and background colour (just describe — Stylist picks the colour)

---

## Step 3 — Read the header / top bar

**Questions to answer:**
- Is there a search input? What shape (pill, rectangle)?
- Is there a filter dropdown?
- Is there a reset/refresh action?
- Is there page title text?
- Does the header span full width or sit next to the nav?
- What is the approximate height of the header zone?

---

## Step 4 — Read the content body

**Questions to answer:**
- Are there summary metric tiles/cards? How many? What size relative to each other?
- Is there a data table/gallery? What columns are visible?
- Is there a detail panel or split view?
- Are there status indicators (badges, coloured chips)?
- What is the approximate proportion of tiles vs table?

---

## Step 5 — Identify component patterns

From the screenshot, identify visual components that are reusable:

```
For each distinct reusable section, note:
  - Name (what it is: navigation, search bar, metric card, data row, modal)
  - Shape (pill, rectangle, card, overlay)
  - Shadow (flat = no shadow, subtle = light shadow, elevated = strong shadow)
  - Corner radius (sharp = 0, soft = ~8px, rounded = ~15px, pill = ~25px+)
  - What controls sit inside it
```

---

## Step 6 — Note the visual style

Without deciding colours:

| Attribute | Describe what you see |
|---|---|
| Overall feel | Clean/minimal? Dense/data-rich? Bold/colorful? Corporate/flat? |
| Surfaces | White? Light grey? Dark? |
| Shadows | None? Subtle? Prominent? |
| Corner radius | Sharp? Soft? Rounded? Pill? |
| Typography weight | Light? Regular? Bold headers? |
| Spacing | Tight? Standard? Generous? |
| Dominant shape | Rectangles? Rounded rects? Pills? Mixed? |

---

## Step 7 — Write design-system.md

After reading the screenshot, produce `docs/design-system.md` with these sections:

```markdown
# Design System — <Project Name>

## Design Reading Source
Reference: <screenshot filename or "user-provided screenshot">
Layout pattern identified: <Pattern A/B/C/D/E/F or description>

## Layout Structure
<Describe the zones in plain language>
<Include an ASCII diagram if the layout is complex>

## Navigation
- Position: <left/top/bottom>
- Shape: <pill/rectangle/tab bar/etc.>
- Items: <N icons/tabs>
- Dimensions (approximate): <W×H>
- Active state: <visible/not visible/description>

## Header / Filter Bar
- Type: <search bar / title bar / tab bar / none>
- Shape: <pill/rectangle/flat>
- Contents: <dropdown, text input, icons>
- Span: <full width / partial>

## Content Body
- Top row: <tiles? how many? relative sizing?>
- Main area: <table/gallery/cards/chart/mixed>
- Detail: <split view/modal/inline/none>

## Component Shapes
| Component | Shape | Shadow | Radius | Notes |
|---|---|---|---|---|
| Navigation | pill | subtle | 25px+ | icons overlaid on HtmlText |
| Cards | rounded rect | subtle | 15px | HtmlText background |
| Search bar | wide pill | subtle | 30px | primary colour |
| Table rows | flat | none | 0 | gallery template |

## Visual Style
- Feel: <description>
- Surfaces: <white/light/dark>
- Shadow style: <flat/subtle/elevated>
- Typography: <light/regular/bold headers>
- Spacing: <tight/standard/generous>
- Dominant shapes: <description>

## Colour Palette
[Stylist selects colours based on project brief and brand — not from screenshot]
- Primary: <to be decided>
- Background: <to be decided>
- Surface/card: <to be decided>
- Status colours: <to be decided — use standard approved/pending/rejected semantic colours>

## Component Design Tokens
[Specific RGBA values and control properties filled in by Stylist based on selected palette]

## Improvements Over Reference
[List anything the reference design is missing that should be added as standard practice]
- Empty states
- Loading indicators
- Status badges (if plain text in reference)
- Active navigation indicator (if missing)
- Hover states
- Error states
```

---

## What to do when NO screenshot is provided

If the user does not provide a screenshot or wireframe:

1. Check `context/` folder for any image files
2. Ask: "Do you have a reference design or wireframe? If yes, share it and I'll match that style. If not, I'll design based on the project context and personas."
3. If no reference → make design decisions based on:
   - The project type (approval workflow → clean enterprise; consumer app → warmer, more visual)
   - The personas (office workers → professional; field workers → high contrast, large touch targets)
   - Any brand colours mentioned in the brief
   - The `canvas-app-design-patterns` skill for standard component patterns

---

## HtmlText for visual containers

When the reference design shows rounded cards, pills, or shadows — use HtmlText:

```html
<div style='
  margin: 10px;
  width: Wpx;           /* must = Canvas control Width - 20 */
  height: Hpx;          /* must = Canvas control Height - 20 */
  background-color: [colour from design-system.md];
  box-shadow: 0 Ypx Bpx Spx rgba(0,0,0,0.12);
  border-radius: Rpx
'></div>
```

Shadow values by style:
- Flat (no shadow): omit box-shadow
- Subtle: `0 2px 6px 2px rgba(0,0,0,0.08)`
- Standard: `0 3px 10px 5px rgba(0,0,0,0.12)`
- Elevated: `0 5px 15px 5px rgba(0,0,0,0.20)`

Corner radius by shape:
- Sharp: 0px
- Soft: 6-8px
- Rounded: 12-16px
- Pill: 24px+ (use half the shorter dimension for a true pill)

Interactive controls (buttons, icons) must be overlaid on HtmlText — not inside
the HTML — because HtmlText cannot receive click events.
