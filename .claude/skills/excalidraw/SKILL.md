---
name: excalidraw
description: Create Excalidraw diagrams programmatically — write .excalidraw JSON files and render to SVG/PNG. Use when the user asks for flowcharts, architecture diagrams, sequence diagrams, or any technical visual that needs precise, reproducible output (not AI-generated images).
---

# Excalidraw Diagrams

Create precise, reproducible diagrams by writing `.excalidraw` JSON files and rendering them to SVG or PNG. Flowcharts, architecture diagrams, sequence diagrams, and technical visuals.

## Status Check

```bash
ls lib/excalidraw-renderer/node_modules/@excalidraw/utils/dist/excalidraw-utils.min.js 2>/dev/null && echo "OK" || echo "NOT SET UP — run: cd lib/excalidraw-renderer && npm install"
```

## Setup

### Required: Excalidraw renderer (one-time)
```bash
cd lib/excalidraw-renderer && npm install
```
Uses `excalidraw-to-svg` + `@excalidraw/utils@0.1.2` + jsdom + canvas. ~2s render time per diagram.

**Note:** If `canvas` fails to install (Node version mismatch), install it manually via `brew install pkg-config cairo pango libpng jpeg giflib librsvg` then retry `npm install`.

### Optional: librsvg (PNG conversion from SVG)
```bash
brew install librsvg
```

## Rendering Pipeline

### 1. Write the .excalidraw JSON file

Use the Write tool to create a `.excalidraw` file. See Quick Reference below and `references/element-reference.md` for full spec.

### 2. Render to SVG

```bash
cd lib/excalidraw-renderer && node render.js /absolute/path/to/diagram.excalidraw /absolute/path/to/output/
```
Produces `/absolute/path/to/output/diagram.svg`. **Must run from `lib/excalidraw-renderer/` directory** so node_modules are found.

Stderr will show jsdom warnings about SVG image loading — these are harmless. The script exits 0 on success and prints the output path.

### 3. Optional: Convert to PNG

```bash
rsvg-convert -w 1200 -o output.png output/diagram.svg
```
Adjust `-w` for desired pixel width. Height scales proportionally.

### How Rendering Works

The renderer uses `excalidraw-to-svg` (jsdom-based) for shapes/arrows, then post-processes the SVG to inject bound text that the jsdom renderer misses. All text, shapes, arrows, and colors render correctly. The `.excalidraw` file can also be opened in excalidraw.com for pixel-perfect export.

## Quick Reference: Building Diagrams

### File Skeleton

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude",
  "elements": [],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 },
  "files": {}
}
```

### Element Essentials

Every element needs these base properties:

```json
{
  "id": "unique-id",
  "type": "rectangle",
  "x": 100, "y": 100,
  "width": 180, "height": 70,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "seed": 100,
  "version": 1,
  "versionNonce": 100,
  "isDeleted": false,
  "groupIds": [],
  "frameId": null,
  "roundness": { "type": 3 },
  "boundElements": [],
  "updated": 1700000000000,
  "link": null,
  "locked": false
}
```

### Shape Types

| Type | Extra Properties | Notes |
|------|-----------------|-------|
| `rectangle` | — | `roundness: {"type": 3}` for rounded corners |
| `ellipse` | — | `roundness: null` always |
| `diamond` | — | `roundness: {"type": 2}` for soft corners |

### Text Inside Shapes

**Container shape** — add text to `boundElements`:
```json
"boundElements": [{ "id": "text-id", "type": "text" }]
```

**Text element** — reference the container, set position to 0:
```json
{
  "type": "text",
  "containerId": "shape-id",
  "x": 0, "y": 0, "width": 0, "height": 0,
  "text": "Label",
  "fontSize": 20,
  "fontFamily": 6,
  "textAlign": "center",
  "verticalAlign": "middle",
  "lineHeight": 1.25,
  "autoResize": true,
  "baseline": 0
}
```

When text has `containerId`, set x/y/width/height all to 0 — Excalidraw auto-positions it.

### Arrows with Bindings

```json
{
  "type": "arrow",
  "x": 180, "y": 35,
  "width": 100, "height": 0,
  "points": [[0, 0], [100, 0]],
  "startBinding": { "elementId": "source-id", "focus": 0, "gap": 4, "fixedPoint": [1, 0.5] },
  "endBinding": { "elementId": "target-id", "focus": 0, "gap": 4, "fixedPoint": [0, 0.5] },
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "roundness": { "type": 2 }
}
```

**Both shapes must list the arrow in their `boundElements`:**
```json
"boundElements": [{ "id": "arrow-id", "type": "arrow" }]
```

### fixedPoint Quick Reference

```
[0.5, 0]  = top center       [0.5, 1]  = bottom center
[0, 0.5]  = left center      [1, 0.5]  = right center
```

### Points Array

Relative to arrow's x,y. First point always `[0, 0]`.
- Right: `[[0,0], [100, 0]]`
- Down: `[[0,0], [0, 80]]`
- L-bend: `[[0,0], [0, 50], [100, 50]]`

`width` and `height` must match the bounding box of the points.

## Layout Grid

| Element | Standard Size |
|---------|--------------|
| Rectangle | 180 × 70 px |
| Diamond | 200 × 140 px |
| Ellipse | 140 × 60 px |
| Horizontal gap | 100 px |
| Vertical gap | 60 px |
| Column pitch | 280 px (180 + 100) |
| Row pitch | 130 px (70 + 60) |

**Top-down flow:** Stack vertically at same x. Arrows: `[[0,0], [0, 60]]`
**Left-right flow:** Place horizontally at same y. Arrows: `[[0,0], [100, 0]]`

## Fonts

| Value | Font | Default For |
|-------|------|-------------|
| 6 | Nunito | Professional (default) |
| 5 | Excalifont | Hand-drawn style |
| 3 | Cascadia | Code/monospace |

## Style Presets

**Professional (default):** `roughness: 0, fontFamily: 6, fillStyle: "solid", roundness: {"type": 3}`

**Hand-drawn:** `roughness: 1, fontFamily: 5, fillStyle: "hachure", roundness: null`

**Technical:** `roughness: 0, fontFamily: 3, strokeWidth: 1, roundness: null`

## Color Palette

### Backgrounds (fills)
| Color | Hex | Use |
|-------|-----|-----|
| Light blue | `#a5d8ff` | Primary boxes |
| Light green | `#b2f2bb` | Success, start |
| Light yellow | `#ffec99` | Decisions, warnings |
| Light red | `#ffc9c9` | Errors, end |
| Light purple | `#d0bfff` | Special, tertiary |
| Light orange | `#ffd8a8` | Secondary |
| Gray | `#e9ecef` | Disabled, background |
| Transparent | `"transparent"` | No fill |

### Strokes
| Color | Hex | Use |
|-------|-----|-----|
| Black | `#1e1e1e` | Default |
| Blue | `#1971c2` | Primary |
| Green | `#2f9e44` | Success |
| Red | `#e03131` | Error |
| Orange | `#e8590c` | Warning |
| Purple | `#7048e8` | Special |
| Gray | `#868e96` | De-emphasized |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing bidirectional binding | Both the arrow AND the shape must reference each other |
| Text positioned manually inside a container | Set x/y/width/height to 0 when `containerId` is set |
| Arrow width/height doesn't match points | width = max(x points) - min(x points), same for height |
| Points not starting at [0,0] | First point must always be [0, 0] |
| Missing `seed` or `versionNonce` | Use any positive integer — required but value doesn't matter |
| Forgetting `roundness` on shapes | `{"type": 3}` for rectangles, `{"type": 2}` for diamonds, `null` for ellipses |
| Using fontFamily 1 (Virgil) | Use 5 (Excalifont) or 6 (Nunito) instead |
| Arrow appears disconnected | Check all 4 cross-references: arrow start/end binding + both shapes' boundElements |

## Diagram Templates

For complete, copy-paste-ready templates see `references/diagram-patterns.md`:
- **Flowchart** — Start → Process → Decision → branches
- **Architecture** — Layered tiers with connections
- **Sequence** — Actors, lifelines, message arrows
- **Simple connected boxes** — Minimal 3-box template

## Editing After Generation

Generated `.excalidraw` files can be opened in:
- [excalidraw.com](https://excalidraw.com) — drag and drop the file
- VS Code with the Excalidraw extension
- Any tool that reads the Excalidraw JSON format
