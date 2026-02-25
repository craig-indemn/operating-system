# Excalidraw Element Reference

Complete specification for building `.excalidraw` JSON files programmatically.

## File Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude",
  "elements": [],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  },
  "files": {}
}
```

- `elements` — array of shape/text/arrow objects (see below)
- `appState` — canvas settings (background color, grid)
- `files` — embedded images (base64), keyed by fileId. Rarely needed.

## Base Properties (All Elements)

Every element shares these fields:

```json
{
  "id": "unique-string-id",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 80,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "seed": 1234567890,
  "version": 1,
  "versionNonce": 1234567890,
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

### Key Property Details

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique identifier. Use descriptive IDs like `"box-start"`, `"arrow-1"`. |
| `x`, `y` | number | Top-left corner position in canvas coordinates. |
| `width`, `height` | number | Dimensions. For text, these are calculated from content. |
| `angle` | number | Rotation in radians. 0 = no rotation. |
| `strokeColor` | string | Border/outline color. Hex format `"#1e1e1e"`. |
| `backgroundColor` | string | Fill color. Use `"transparent"` for no fill. |
| `fillStyle` | string | `"solid"`, `"hachure"`, `"cross-hatch"`, `"dots"` |
| `strokeWidth` | number | Line thickness: 1 (thin), 2 (normal), 4 (bold) |
| `strokeStyle` | string | `"solid"`, `"dashed"`, `"dotted"` |
| `roughness` | number | 0 = clean, 1 = hand-drawn, 2 = very rough |
| `opacity` | number | 0–100 |
| `seed` | number | Random seed for roughness rendering. Use any positive integer. |
| `roundness` | object/null | `{"type": 3}` for rounded corners, `null` for sharp |
| `boundElements` | array | Cross-references to arrows/text bound to this element |
| `groupIds` | array | Group membership. Elements sharing a groupId move together. |

### Generating IDs and Seeds

Use descriptive string IDs for readability:
- Shapes: `"box-start"`, `"box-process"`, `"diamond-decision"`
- Arrows: `"arrow-start-to-process"`, `"arrow-yes"`, `"arrow-no"`
- Text: `"text-start"`, `"label-yes"`, `"label-no"`

Seeds can be any positive integer. Use incrementing values: `100`, `200`, `300`, etc.

## Shape Elements

### Rectangle

```json
{
  "type": "rectangle",
  "x": 100, "y": 100,
  "width": 200, "height": 80,
  "roundness": { "type": 3 }
}
```

### Ellipse

```json
{
  "type": "ellipse",
  "x": 100, "y": 100,
  "width": 120, "height": 120,
  "roundness": null
}
```

`roundness` is always `null` for ellipses (they're already round).

### Diamond

```json
{
  "type": "diamond",
  "x": 100, "y": 100,
  "width": 160, "height": 120,
  "roundness": { "type": 2 }
}
```

Diamonds render as rotated squares. The bounding box is `width × height`. Use `roundness: {"type": 2}` for slightly softened corners.

## Text Elements

```json
{
  "type": "text",
  "x": 130, "y": 125,
  "width": 140, "height": 30,
  "text": "Process Step",
  "fontSize": 20,
  "fontFamily": 6,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": "box-process",
  "lineHeight": 1.25,
  "autoResize": true,
  "baseline": 0
}
```

### Font Families

| Value | Font | Use |
|-------|------|-----|
| 5 | Excalifont (hand-drawn) | Matches hand-drawn aesthetic |
| 6 | Nunito | Clean, professional — **default** |
| 3 | Cascadia (monospace) | Code, technical labels |
| 1 | Virgil (legacy hand-drawn) | Avoid — use 5 instead |

### Text Sizing

Approximate width/height based on content:
- **Width**: ~10px per character at fontSize 20 (varies by font)
- **Height**: `fontSize * lineHeight * numberOfLines`
- For single-line labels: `height = fontSize * 1.25` (25 for fontSize 20)
- When in doubt, overestimate width slightly — Excalidraw auto-adjusts

### Text in Containers (Bound Text)

To put text inside a shape, use `containerId` on the text and `boundElements` on the shape:

**Shape (the container):**
```json
{
  "id": "box-1",
  "type": "rectangle",
  "boundElements": [
    { "id": "text-box-1", "type": "text" }
  ]
}
```

**Text (inside the container):**
```json
{
  "id": "text-box-1",
  "type": "text",
  "containerId": "box-1",
  "textAlign": "center",
  "verticalAlign": "middle",
  "x": 0, "y": 0,
  "width": 0, "height": 0
}
```

**Important:** When text has a `containerId`, set its `x`, `y`, `width`, `height` all to `0`. Excalidraw auto-positions the text within the container. The `textAlign` and `verticalAlign` control placement within the container.

## Arrow and Line Elements

### Basic Arrow

```json
{
  "type": "arrow",
  "x": 300, "y": 140,
  "width": 0, "height": 100,
  "points": [[0, 0], [0, 100]],
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "startBinding": {
    "elementId": "box-start",
    "focus": 0,
    "gap": 4,
    "fixedPoint": [0.5, 1]
  },
  "endBinding": {
    "elementId": "box-end",
    "focus": 0,
    "gap": 4,
    "fixedPoint": [0.5, 0]
  },
  "roundness": { "type": 2 }
}
```

### Points Array

Points are **relative to the arrow's x,y position**. First point is always `[0, 0]`.

```
Straight down:    [[0, 0], [0, 100]]
Straight right:   [[0, 0], [200, 0]]
L-shaped:         [[0, 0], [0, 50], [200, 50]]
Z-shaped:         [[0, 0], [0, 50], [200, 50], [200, 100]]
```

**Width and height must match the points bounding box:**
- `width` = max(all point x values) - min(all point x values)
- `height` = max(all point y values) - min(all point y values)

### Arrowhead Types

| Value | Renders |
|-------|---------|
| `"arrow"` | Standard triangle head ▶ |
| `"dot"` | Filled circle ● |
| `"bar"` | Perpendicular bar ⊢ |
| `"triangle"` | Large filled triangle |
| `null` | No arrowhead (plain line end) |

Use `"arrow"` for `endArrowhead` by default. Set `startArrowhead: null` unless bidirectional.

### Line (No Arrowheads)

```json
{
  "type": "line",
  "points": [[0, 0], [200, 0]],
  "startArrowhead": null,
  "endArrowhead": null
}
```

## Binding Protocol (Critical)

Bindings connect arrows to shapes. They require **bidirectional cross-references**.

### Arrow Side (startBinding / endBinding)

```json
{
  "elementId": "target-shape-id",
  "focus": 0,
  "gap": 4,
  "fixedPoint": [0.5, 1]
}
```

| Field | Description |
|-------|-------------|
| `elementId` | ID of the shape this end connects to |
| `focus` | -1 to 1. 0 = centered on edge. Negative = left/up, Positive = right/down |
| `gap` | Pixel gap between arrowhead and shape edge. Use 4. |
| `fixedPoint` | `[xRatio, yRatio]` on the target shape. See below. |

### fixedPoint Values

The `fixedPoint` is a normalized `[x, y]` coordinate on the target shape:

```
[0.5, 0]   = top center
[0.5, 1]   = bottom center
[0, 0.5]   = left center
[1, 0.5]   = right center
[0, 0]     = top-left corner
[1, 1]     = bottom-right corner
```

### Shape Side (boundElements)

The target shape must list the arrow in its `boundElements`:

```json
{
  "id": "box-1",
  "type": "rectangle",
  "boundElements": [
    { "id": "arrow-1", "type": "arrow" },
    { "id": "text-box-1", "type": "text" }
  ]
}
```

### Complete Binding Example

Box A → Arrow → Box B:

```json
[
  {
    "id": "box-a",
    "type": "rectangle",
    "x": 100, "y": 100, "width": 200, "height": 80,
    "boundElements": [
      { "id": "text-a", "type": "text" },
      { "id": "arrow-a-to-b", "type": "arrow" }
    ]
  },
  {
    "id": "text-a",
    "type": "text",
    "text": "Box A",
    "containerId": "box-a",
    "x": 0, "y": 0, "width": 0, "height": 0,
    "textAlign": "center", "verticalAlign": "middle"
  },
  {
    "id": "arrow-a-to-b",
    "type": "arrow",
    "x": 200, "y": 180,
    "width": 0, "height": 80,
    "points": [[0, 0], [0, 80]],
    "startBinding": {
      "elementId": "box-a",
      "focus": 0, "gap": 4,
      "fixedPoint": [0.5, 1]
    },
    "endBinding": {
      "elementId": "box-b",
      "focus": 0, "gap": 4,
      "fixedPoint": [0.5, 0]
    },
    "startArrowhead": null,
    "endArrowhead": "arrow"
  },
  {
    "id": "box-b",
    "type": "rectangle",
    "x": 100, "y": 260, "width": 200, "height": 80,
    "boundElements": [
      { "id": "text-b", "type": "text" },
      { "id": "arrow-a-to-b", "type": "arrow" }
    ]
  },
  {
    "id": "text-b",
    "type": "text",
    "text": "Box B",
    "containerId": "box-b",
    "x": 0, "y": 0, "width": 0, "height": 0,
    "textAlign": "center", "verticalAlign": "middle"
  }
]
```

### Binding Checklist

1. Arrow's `startBinding.elementId` references the source shape
2. Arrow's `endBinding.elementId` references the target shape
3. Source shape's `boundElements` includes `{"id": "arrow-id", "type": "arrow"}`
4. Target shape's `boundElements` includes `{"id": "arrow-id", "type": "arrow"}`
5. Arrow's `x,y` is at the starting point (typically bottom-center of source shape)
6. Arrow's `points` array goes from `[0,0]` to the relative offset of the end point
7. Arrow's `width` and `height` match the points bounding box

**If any cross-reference is missing, the binding won't work.** Arrows will appear disconnected.

## Groups

Group elements by giving them the same group ID:

```json
{
  "id": "box-1",
  "groupIds": ["group-header"]
},
{
  "id": "text-1",
  "groupIds": ["group-header"]
}
```

Grouped elements move and select together. Nested groups use multiple IDs: `["inner-group", "outer-group"]`.

## Z-Order

Elements render in array order — first element is at the back, last is on top. Place shapes before their text labels, and arrows after the shapes they connect.

Recommended order:
1. Background shapes (containers, frames)
2. Foreground shapes (boxes, diamonds, ellipses)
3. Text labels (bound text auto-positioned by containers)
4. Arrows and lines (on top so they're always visible)

## Color Palette

### Professional Presets

| Name | Hex | Use |
|------|-----|-----|
| Dark text | `#1e1e1e` | Default stroke, text |
| White | `#ffffff` | Backgrounds |
| Light blue | `#a5d8ff` | Primary boxes, highlights |
| Light green | `#b2f2bb` | Success, start nodes |
| Light yellow | `#ffec99` | Warnings, decisions |
| Light red | `#ffc9c9` | Errors, end nodes |
| Light purple | `#d0bfff` | Special, tertiary |
| Light orange | `#ffd8a8` | Secondary, accents |
| Gray | `#e9ecef` | Disabled, background boxes |
| Transparent | `"transparent"` | No fill |

### Stroke Colors

| Name | Hex | Use |
|------|-----|-----|
| Black | `#1e1e1e` | Default |
| Blue | `#1971c2` | Primary emphasis |
| Green | `#2f9e44` | Success |
| Red | `#e03131` | Error, danger |
| Orange | `#e8590c` | Warning |
| Purple | `#7048e8` | Special |
| Gray | `#868e96` | Secondary, de-emphasized |

## Style Presets

### Professional (Default)
```json
{
  "roughness": 0,
  "fontFamily": 6,
  "strokeWidth": 2,
  "fillStyle": "solid",
  "roundness": { "type": 3 }
}
```

### Hand-Drawn
```json
{
  "roughness": 1,
  "fontFamily": 5,
  "strokeWidth": 2,
  "fillStyle": "hachure",
  "roundness": null
}
```

### Technical
```json
{
  "roughness": 0,
  "fontFamily": 3,
  "strokeWidth": 1,
  "fillStyle": "solid",
  "roundness": null
}
```
