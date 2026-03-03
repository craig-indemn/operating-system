---
ask: "Browser-test OS Terminal V1 against 14-point integration checklist"
created: 2026-03-02
workstream: os-development
session: 2026-03-02-d
sources:
  - type: local
    description: "Browser testing via agent-browser CLI against localhost:3100"
  - type: local
    description: "Implementation plan checklist at docs/plans/2026-03-02-os-terminal-implementation.md (Task 12)"
---

# OS Terminal V1 Browser Testing

## 14-Point Integration Checklist Results

| # | Test | Result | Notes |
|---|------|--------|-------|
| 1 | Page loads | **Pass** | Session panel + grid render, dark theme, top bar with active count |
| 2 | Terminal I/O | **Pass** | Input flows through WebSocket to tmux, output renders in xterm.js |
| 3 | Correct routing | **Pass** | Session name in header maps to correct tmux session |
| 4 | Drag pane header | **Pass** | Grid rearranges, no overlap (manual test by user) |
| 5 | Resize pane edge | **Pass** | Terminal refits to new dimensions (manual test by user) |
| 6 | Double-click header | **Partial** | Doesn't fire via drag handle — maximize button works as alternative |
| 7 | Escape from maximized | **Pass** | Returns to grid view |
| 8 | Minimize button | **Pass** | Pane disappears from grid |
| 9 | Cmd+1 focus | **Pass** | Focuses first pane, also restores if minimized |
| 10 | Cmd+B panel toggle | **Pass** | Toggles session panel visibility |
| 11 | Create session externally | **Pass** | New pane auto-appears in grid (manual test by user) |
| 12 | Close session externally | **Pass** | Pane updates status (manual test by user) |
| 13 | Reload page | **Pass** | Layout restored from localStorage, terminals reconnect |
| 14 | Multiple browser tabs | **Pass** | Both tabs show same session output (manual test by user) |

## Bugs Found and Fixed

### 1. Layout race condition (Critical)

**Symptom**: Terminal panes rendered as tiny ~80px boxes instead of filling the grid.

**Root cause**: Sessions arrive via WebSocket after initial render. The `useEffect` that adds layout entries for new sessions races with react-grid-layout's `onLayoutChange` callback. Flow: (1) child appears without layout entry → (2) react-grid-layout auto-creates `w:1, h:1` default → (3) `onLayoutChange` saves defaults to state and localStorage → (4) `useEffect` checks if session exists in layout, finds it (at w:1), skips.

**Fix**: Replaced racy `useEffect` with synchronous `useMemo` (`effectiveLayouts`) that ensures all visible sessions have layout entries with correct sizes *before* render. Added minimum size enforcement (`MIN_W=3, MIN_H=3`) in `handleLayoutChange` to reject degenerate defaults.

### 2. Pane buttons not clickable (Important)

**Symptom**: Minimize (\_), maximize (□), and close (×) buttons did nothing when clicked.

**Root cause**: react-grid-layout's drag handler captures `mousedown` events on the `.terminal-header` (configured as `draggableHandle`). Child button elements inside the header never receive click events because the drag handler intercepts the mousedown.

**Fix**: Added `onMouseDown={(e) => e.stopPropagation()}` on the `.terminal-header-right` container wrapping the buttons. This prevents react-grid-layout from capturing mousedown on buttons while still allowing header drags.

### 3. No way to restore minimized panes (Important)

**Symptom**: Once a pane was minimized, the only way to get it back was to reload the page.

**Fix**: Added `onSelectSession` callback to `SessionPanel`. Clicking an active session card restores it (removes from minimized set), clears maximize state, and focuses. `Cmd+1-9` shortcuts also restore minimized panes.

## Features Added During Testing

- **Create session (+) button**: Prompts for session name, POSTs to `/api/sessions`
- **Close session (×) button**: Confirmation dialog, then DELETE `/api/sessions/:id?force=true`
- **Session card click**: Restores minimized panes, focuses the session

## Known Remaining Issues

- **Double-click header to maximize**: Doesn't fire due to drag handle interference. Maximize button works as alternative. Could be fixed with a manual double-click detector but low priority.
- **Minimize→restore transient sizing**: After restoring a minimized pane, it temporarily renders at a smaller size until page reload. Root cause: react-grid-layout's WidthProvider doesn't re-measure when items reappear.

## Commits This Session

| Hash | Description |
|------|-------------|
| `4ea59c7` | fix: layout race condition, session card restore, minimum sizes |
| `d1815b3` | fix: pane buttons, create/close session, drag handle fix |
