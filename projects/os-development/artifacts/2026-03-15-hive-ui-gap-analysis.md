---
ask: "Audit the Hive UI implementation against the visual design doc and main design doc — identify all gaps"
created: 2026-03-15
workstream: os-development
session: 2026-03-15-b
sources:
  - type: design
    description: "Visual design doc — 2026-03-15-hive-ui-visual-design.md"
  - type: design
    description: "Main design doc — 2026-03-08-hive-design.md (UI sections)"
  - type: session
    description: "Browser E2E testing revealed issues"
---

# Hive UI Gap Analysis — Design vs. Implementation

## Critical Gaps

### 1. Sessions Not Visible
**Design:** "Two data sources: sessions/*.json (real-time) + Hive API (knowledge). The UI merges both into one unified Wall."
**Actual:** Sessions don't appear. The session state watcher uses `OS_ROOT/sessions/` as its directory. When running from a worktree, `OS_ROOT` points to the worktree which has no `sessions/` dir. Session state files live at `/Users/home/Repositories/operating-system/sessions/`.
**Fix:** The sessions dir path should always resolve to the main repo's `sessions/` directory, not relative to OS_ROOT. Or: `getSessionsDir()` should look at the actual repo root (not worktree). The `useSessions()` hook works — it connects to `/ws/state` which watches that directory. The issue is purely the directory path.

### 2. Wall is a Sidebar, Not a Surrounding Surface
**Design:** "The Wall surrounds the Focus Area. The Focus Area is always centered. The Wall is the peripheral awareness layer." The visual design shows the Wall as a left column at 240-400px.
**Actual:** Implementation matches the layout spec (left column), but it feels like a sidebar because:
- Tiles are in a single vertical column with no width variation
- No multi-column layout even when Wall is 400px wide
- No masonry/variable-height tiles
- It doesn't feel like a "living breathing" surface — it's a list

**Fix:** The Wall needs:
- CSS Grid with `auto-fill` columns when Wall width permits (2 columns at 400px, 1 at 240px)
- Variable tile heights based on content/priority (active tiles get more height)
- The "breathing" needs to be visible — tiles should animate/resize when Wall width changes

### 3. No Masonry / Multi-Column Tile Layout
**Design:** "Masonry-style variable-height tiles" with column counts: 2 columns at 400px, 1-2 at 300px, 3-4 in overview.
**Actual:** `flex-direction: column` with `gap: 4px`. Always one column. No grid.
**Fix:** Replace the flex column with CSS grid:
```css
display: grid;
grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
gap: 4px;
```
In overview mode: `grid-template-columns: repeat(auto-fill, minmax(250px, 1fr))` for 3-4 columns.

### 4. No Tile Height Variation (Not "Breathing")
**Design:** Progressive disclosure tiers based on tile height:
- Compressed (48-60px): done/backlog, or Wall in compressed mode
- Standard (80-100px): default for most tiles
- Expanded (120-160px): active/high-priority tiles
- Featured (180px+): overview mode or wide Wall

The HiveTile component has a ResizeObserver to detect its height and show/hide content accordingly. But nothing SETS different heights — all tiles get the same auto height from their content.

**Actual:** All tiles are the same height (~55px) because they only show badge + title.
**Fix:** Tiles need explicit height allocation based on:
- Status: active tiles get `minHeight: 120px` (expanded), backlog/done get `48px` (compressed)
- Priority: critical/high get more height
- Wall width: wider Wall = taller tiles (featured tier)
- The height should be set on the wrapper div in Wall.tsx, and HiveTile's ResizeObserver will automatically show more content as the height increases.

### 5. Session Tiles Missing Session-Specific Data
**Design:** "Session tiles: type 'session', show status/context%/model, session-specific colors. Click session tile → opens terminal in Focus Area."
**Actual:** `sessionToTile()` creates a HiveRecord but the HiveTile component doesn't know how to render session-specific info (context %, model, session status with the existing status colors like blue/green/amber/red).
**Fix:** HiveTile needs a session rendering mode that shows context%, model badge, and uses session status colors instead of Hive status visuals.

### 6. Wall Tile Ordering Not Reflecting Design
**Design:** "All types mixed on one surface. Tiles are NOT grouped by type or system. Organization is by relevance and status, not by category."
**Actual:** `sortWallRecords()` sorts by priority→status→recency, which is correct. But the tiles appear in a flat list that doesn't visually communicate priority grouping. No visual separators, no priority section headers, no size differentiation.
**Fix:** Priority should be communicated through tile height (critical=featured, high=expanded, medium=standard, low/none=compressed). This makes the Wall self-organizing visually.

## Minor Gaps

### 7. Right-Click Context Menu
**Design:** "shadcn dropdown: zinc-900 bg, zinc-800 border, zinc-100 text"
**Actual:** ActionMenu component exists and is wired up via `onContextMenu`. However, browser testing showed it may not fire correctly (Playwright couldn't trigger it). Needs real browser verification.
**Fix:** Verify `e.preventDefault()` in HiveTile's `onContextMenu` handler stops the browser's native menu. May need to also handle long-press on mobile.

### 8. Unused Components Still in Codebase
**Files to remove:** `TerminalGrid.tsx` and `SessionPanel.tsx` are fully replaced by `FocusArea.tsx` and `Wall.tsx`. They're still imported nowhere but exist in the directory.

### 9. Overview Mode Tile Reflow
**Design:** "Tiles reflow to 3-4 columns at expanded/featured sizes"
**Actual:** Overview mode just makes the Wall full-width. Tiles stay in a single column. Should reflow to multi-column grid.
**Fix:** Wall.tsx should detect `compressed` prop (inverted — overview = not compressed) and switch to multi-column CSS grid.

### 10. Done Tiles Visible But Faded
**Design:** "Done items don't disappear — they fade (lower brightness) but remain on the Wall. Completed work is context for what's next AND source material for future work."
**Actual:** Status-based opacity works for domain/search filtering, but done tiles aren't visually differentiated from active tiles in the default view. The HiveTile has `getStatusVisuals()` which maps done→bg-base/15% accent/text-muted, but this is subtle.
**Fix:** The tile height allocation should also make done tiles compressed (48px) so they recede visually while still being present.

## Data Flow Issue

### 11. Session State Directory
**Root cause of sessions not showing:** `getSessionsDir()` in `server/state.ts` returns `join(getOsRoot(), 'sessions')`. When `OS_ROOT` is a worktree path, there are no session state files there.
**Fix options:**
a. Always use the main repo path for sessions (hardcode or derive from git)
b. Symlink `sessions/` in worktrees to the main repo
c. Make `OS_ROOT` point to the actual repo root, not the worktree
d. Add a separate `SESSIONS_DIR` env var

Option (c) is cleanest — the server should always know where the real OS root is, even when running from a worktree. The hive CLI and vault are in the worktree, but sessions are shared infrastructure.

## Summary: Priority Fix Order

1. **Session visibility** — fix the sessions dir path so active tmux sessions appear as tiles
2. **Multi-column masonry layout** — CSS grid in Wall.tsx with column count responsive to width
3. **Variable tile heights** — allocate height based on status/priority/Wall-width
4. **Overview reflow** — multi-column grid in overview mode
5. **Session tile rendering** — show context%, model, session status colors
6. **Breathing animation** — smooth transitions when Wall width changes
7. **Remove unused components** — TerminalGrid.tsx, SessionPanel.tsx
8. **Right-click menu** — verify in real browser, fix if needed
