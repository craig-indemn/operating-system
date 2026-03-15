---
ask: "Define the visual design system for the Hive UI — color, typography, tile anatomy, layout, interactions, responsive behavior"
created: 2026-03-15
workstream: os-development
session: 2026-03-15-a
sources:
  - type: session
    description: "Brainstorming session — shadcn-inspired direction, mosaic tiles, zinc palette, progressive disclosure"
  - type: design
    description: "Hive design doc — tile visual encoding, Wall+Focus layout, fluid sizing"
---

# Hive UI Visual Design

## Design Direction

shadcn/ui aesthetic adapted for a mosaic workspace. Clean, professional, modern, functional — advanced tool vibe. Information-dense without clutter. Zinc dark mode, saturated type badges on neutral surfaces, domain-colored accent bars.

## Color System (Zinc-Based)

| Token | Value | Hex | Usage |
|-------|-------|-----|-------|
| `bg-base` | zinc-950 | `#09090b` | Page background, done tiles recede to this |
| `bg-surface` | zinc-900 | `#18181b` | Standard tile background, panels |
| `bg-lifted` | zinc-850 | `#1f1f23` | Active tile background — stands forward |
| `bg-sunken` | zinc-925 | `#131316` | Backlog tile background — recedes |
| `border` | zinc-800 | `#27272a` | Panel borders, top bar, menus |
| `text-primary` | zinc-100 | `#f4f4f5` | Tile titles, primary content |
| `text-secondary` | zinc-400 | `#a1a1aa` | Metadata, timestamps, descriptions |
| `text-muted` | zinc-500 | `#71717a` | Faded labels, done tile text |

## Typography

- **Inter** — titles, body, UI labels. Weights: 400 (body), 500 (labels), 600 (titles)
- **Geist Mono** — record IDs, timestamps, tags, status badges. Weight: 400
- Base sizes: 13px tile content, 12px metadata, 11px compressed tiles, 10px tag pills

## Domain Accent Colors (3px Left Bar)

| Domain | Color | Hex |
|--------|-------|-----|
| Indemn | Lilac | `#a78bfa` |
| Career Catalyst | Blue | `#3b82f6` |
| Personal | Honey/Amber | `#d97706` |

Accent bar brightness tracks status: 100% active, 70% normal, 40% backlog, 15% done.

## Type Badge Colors (Saturated, Small Pills)

Badge: colored background at 15% opacity, text in full saturated color. Geist Mono, 11px, uppercase.

**Core entities:**
| Type | Color | Hex |
|------|-------|-----|
| `person` | Violet | `#8b5cf6` |
| `company` | Indigo | `#6366f1` |
| `project` | Steel | `#94a3b8` |
| `product` | Cyan | `#06b6d4` |
| `workflow` | Sky | `#0ea5e9` |
| `meeting` | Pink | `#ec4899` |
| `brand` | Rose | `#f43f5e` |
| `platform` | Slate | `#64748b` |
| `channel` | Teal | `#14b8a6` |

**Synced entities:**
| Type | Color | Hex |
|------|-------|-----|
| `linear_issue` | Purple | `#a855f7` |
| `calendar_event` | Fuchsia | `#d946ef` |
| `github_pr` | Green | `#22c55e` |
| `slack_message` | Emerald | `#10b981` |

**Knowledge tags:**
| Tag | Color | Hex |
|-----|-------|-----|
| `decision` | Amber | `#f59e0b` |
| `design` | Orange | `#f97316` |
| `research` | Lime | `#84cc16` |
| `note` | Zinc | `#a1a1aa` |
| `session_summary` | Sky | `#38bdf8` |
| `feedback` | Yellow | `#eab308` |

## Tile Anatomy

No visible border. 3px accent bar on left edge (domain color). Background step communicates status.

### Status → Background

| Status | Tile Background | Accent Intensity | Text |
|--------|----------------|-----------------|------|
| Active | `bg-lifted` (#1f1f23) | 100% | `text-primary` |
| Normal/To-do | `bg-surface` (#18181b) | 70% | `text-primary` |
| Backlog | `bg-sunken` (#131316) | 40% | `text-secondary` |
| Done | `bg-base` (#09090b) | 15% | `text-muted` |

### Progressive Disclosure (4 Tiers)

**Compressed (48-60px)** — done/backlog, or Wall in compressed mode
- Type badge + title (1 line, truncated)

**Standard (80-100px)** — default for most tiles
- Type badge, title, domain accent bar, timestamp ("2h ago")

**Expanded (120-160px)** — active/high-priority tiles
- Above + context line (~60 chars), tags as pills, connection count (diamond + number)

**Featured (180px+)** — overview mode or wide Wall
- Above + description excerpt, related record badges (AI-123, PR #456)

### Visual Elements

- **Accent bar**: 3px wide, left edge, full tile height, radius on left corners
- **Type badge**: top-left pill, 15% opacity background, saturated text
- **Title**: Inter 600, 13px, `text-primary`, max 2 lines with ellipsis
- **Timestamp**: Geist Mono, 11px, `text-muted`, top-right, relative
- **Context line**: Inter 400, 12px, `text-secondary`
- **Tags**: Geist Mono pills, 10px, `zinc-800` bg, `text-secondary` text
- **Connection count**: Geist Mono, 11px, `text-muted`, diamond icon + count, bottom-right
- **Synced indicator**: small system icon next to type badge, `text-muted`

### Tile Dimensions

- Gap: 4px (dense mosaic)
- Padding: 10px 12px (standard), 6px 8px (compressed)
- Border-radius: 6px
- Accent bar border-radius: 6px on top-left and bottom-left corners

## Layout

### Structure

```
┌─────────────────────────────────────────────────┐
│  Top Bar (32px)                                 │
├──────────┬──────────────────────────────────────┤
│          │                                      │
│   Wall   │         Focus Area                   │
│  (tiles) │    (terminal + browser panels)       │
│          │                                      │
│  240-    │      equal-sized auto-grid            │
│  400px   │                                      │
│          │                                      │
├──────────┴──────────────────────────────────────┤
```

### Wall Width (Responsive to Focus)

| Focus Panels | Wall Width | Tile Columns | Dominant Tier |
|-------------|------------|-------------|---------------|
| 0 | 400px | 2 | Expanded/Featured |
| 1 | 300px | 1-2 | Standard/Expanded |
| 2+ | 240px | 1 | Compressed/Standard |
| Overview mode | Full screen | 3-4 | Expanded/Featured |

### Top Bar (32px)

- Left: "HIVE" — Inter 700, `text-muted`, uppercase, letter-spacing 2px
- Center: domain filter pills (All, Indemn, Career Catalyst, Personal). Active = accent color bg + white text. Inactive = `zinc-800` bg + `text-secondary`
- Right: search icon, overview toggle (Ctrl+Shift+O), session count

### Wall

- Vertical scroll, no horizontal
- Masonry-style variable-height tiles
- Fixed tiles at top: Quick Capture, Search (dashed `zinc-700` border, visually distinct)
- Tiles ordered: priority → status → recency, with drag-to-reorder within priority buckets

### Focus Area

- Auto-grid, equal-sized panels (same as current OS Terminal)
- Panel chrome: `zinc-900` header, session name, status dot, minimize/maximize/close
- Focused panel: subtle `zinc-700` top border highlight
- Panel types: terminal (xterm.js) and browser (sandboxed iframe)

## Interactions

### Tile Hover

- Background shifts one step lighter (e.g., `zinc-900` → `zinc-850`)
- Transition: `150ms ease`
- No scale, no shadow — stays flat

### Tile Click

- Session tile → opens terminal panel in Focus Area
- Other record → objective prompt modal (shadcn dialog: `zinc-900` bg, `zinc-800` border, 6px radius) → context assembly → working session

### Right-Click / Action Menu

- shadcn dropdown: `zinc-900` bg, `zinc-800` border, `zinc-100` text
- Actions: Mark done, Change priority, Archive, Open in new session
- Synced records: additional "Open in [system]" action

### Quick Capture

- Fixed at top of Wall, always visible
- Dashed `zinc-700` border, "Capture a thought..." placeholder
- Click → text input, Enter → creates note tile

### Search

- Fixed below quick capture, same dashed-border treatment
- "Search the Hive..." placeholder
- Results filter Wall in real-time: non-matching tiles fade to 10% opacity (preserves spatial memory)

### Domain Filter

- Non-matching tiles fade to 20% opacity (not hidden — spatial memory preserved)

### Overview Toggle (Ctrl+Shift+O)

- Wall animates to full width: `300ms ease-out`
- Focus panels slide off-screen right (keep running)
- Tiles reflow to 3-4 columns at expanded/featured sizes
- Toggle back: reverse animation

## Responsive

### Ultra-wide (>1920px)
Wall 400px, 2-column masonry, featured tiles span full width

### Desktop (1024-1920px)
Wall 240-360px responsive, 1-2 columns, standard layout

### Tablet (768-1024px)
Wall becomes slide-out overlay (300px, swipe or hamburger). Focus takes full width.

### Mobile (<768px)
Full-screen toggle: Wall view (single column scroll) | Focus view (single panel + tab bar). Bottom tab bar for switching. Floating quick capture button (48px circle, lilac accent, bottom-right). All interactive elements minimum 44px tap target.
