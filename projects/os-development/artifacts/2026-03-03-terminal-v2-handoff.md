---
ask: "Handoff prompt for OS Terminal V2 remote access implementation after context compaction"
created: 2026-03-03
workstream: os-development
session: 2026-03-03-b
sources:
  - type: code
    description: "OS Terminal V2 implementation in systems/os-terminal/"
---

# OS Terminal V2 — Remote Access Handoff

## What Was Done

Implemented the full V2 remote access plan for OS Terminal (systems/os-terminal/). The plan is at `docs/plans/2026-03-02-os-terminal-design.md`. All 4 phases are code-complete:

1. **Phase 1: Production Build** — Removed unused react-grid-layout deps, fixed start script to use tsx, added static file serving with SPA catch-all, explicit vite build.outDir
2. **Phase 2: Authentication** — Bearer token auth (OS_TERMINAL_TOKEN env var), WebSocket first-message auth gate, timing-safe comparison, rate limiting, login screen, auth status discovery, logout
3. **Phase 3: Connection Resilience** — Terminal WebSocket reconnection with exponential backoff (1s-10s), visibilitychange/online listeners, press-any-key reconnect, reconnection overlay, server heartbeat (30s native ping/pong), connection state indicators
4. **Phase 4: Tailscale Prep** — PWA meta tags for iOS, generated placeholder icons, manifest.json colors fixed

## New Files Created
- `server/auth.ts` — Auth middleware, WS auth gate, tokensMatch
- `server/heartbeat.ts` — Native ping/pong keepalive
- `server/tmux.ts` — Shared findTmux, TMUX_BIN, isValidSessionName
- `src/hooks/useAuth.ts` — 4-state auth machine, LoginResult type
- `src/utils/auth.ts` — Token storage, authFetch wrapper
- `src/components/LoginScreen.tsx` — Login + error screens
- `public/icon-192.png`, `public/icon-512.png` — PWA placeholder icons

## Modified Files
- `server/index.ts` — Static serving, auth endpoints, WS auth gate in upgrade handler, heartbeat, graceful shutdown, rate limiter with eviction
- `server/terminal.ts` — Uses shared tmux.ts, session name validation, async-safe ping/pong, cleanEnv, positive resize bounds
- `server/state.ts` — Uses shared tmux.ts, async getLiveTmuxSessions (no longer blocks event loop)
- `server/watcher.ts` — Exponential backoff on retry (max 10 retries)
- `server/routes/sessions.ts` — asyncHandler wrapper for Express 4 error catching
- `src/App.tsx` — Split into App (auth gate) + AuthenticatedApp (all hooks/state)
- `src/hooks/useTerminal.ts` — Full reconnection rewrite, deferred resize to first server message
- `src/hooks/useSessions.ts` — Auth message on connect, 4401 handling, intentionalCloseRef
- `src/components/TerminalPane.tsx` — Connection state dot override, reconnection overlay
- `src/components/TerminalGrid.tsx` — Removed dead getColCount/ternary
- `src/App.css` — Login screen, overlay, pulse animation, logout btn, merged terminal-container
- `package.json` — Removed react-grid-layout/react-resizable, tsx to deps, start script
- `vite.config.ts` — Explicit build.outDir
- `index.html` — PWA meta tags, theme-color fix
- `public/manifest.json` — Colors updated to #1e1e1e

## What Still Needs Fixing

From the second round of code review, these issues were identified but NOT yet fixed (only the session name length limit was started):

### Server Issues (from review round 2)
1. **POST /api/sessions no input validation** — `name` not validated with `isValidSessionName()`, `model`/`permissions` not allowlisted, `addDirs` not validated. Fix in `server/routes/sessions.ts`.
2. **DELETE route should validate session.name** — Defense in depth before passing to execFile. Fix in `server/routes/sessions.ts`.
3. **Rate limiter key uses spoofable Tailscale-User-Login header** — Should use only `req.ip`. Fix in `server/index.ts` line 37.
4. **PTY output backpressure** — `ws.send(data)` in terminal.ts has no bufferedAmount check. Can OOM on `cat /dev/urandom`. Fix: check `ws.bufferedAmount`, pause/resume PTY.
5. **No maxPayload on WebSocket servers** — Add `maxPayload: 64 * 1024` to both WSS constructors in `server/index.ts`.
6. **Watcher unhandled promise rejections** — `readAllSessions().then(...)` on line 14 of watcher.ts needs `.catch()`. Also `broadcastSessions(clients)` in setTimeout on line 52 needs `.catch()`.
7. **Graceful shutdown incomplete** — Should terminate all WS clients, force exit after timeout. Current version just closes servers.
8. **tmuxSessionExists still uses sync execFileSync** — Should be async like state.ts's getLiveTmuxSessions. Fix in `server/terminal.ts`.
9. **Session name in WS close reason leaks internal state** — Use generic messages instead of `tmux session not found: os-xxx`.
10. **Static files lack cache headers** — Add `maxAge: '1y', immutable: true` to express.static for hashed assets.

### Frontend Issues (from review round 2)
11. **intentionalCloseRef not reset on effect re-run** — In useTerminal.ts, cleanup sets it to true but if the effect re-runs (StrictMode, dep change), it stays true. Must reset at top of effect like useSessions does.
12. **useSessions redundant ws.close() in onerror** — `ws.onerror` calls `ws.close()` which is usually redundant (browser fires onclose after onerror). Can cause double-close.
13. **TerminalGrid state setter during render** — Line 125 calls `onRestore()` during render when maximized session is gone. Should use useEffect.
14. **TerminalGrid paneRefs never pruned** — Stale entries accumulate as sessions end.

## What To Do Next

1. **Fix all remaining review issues** listed above (14 items)
2. **Run end-to-end testing** per the verification checklist in the plan:
   - Local dev (no token) — works without login
   - Local with token — login screen, enter token, full access
   - Production build — `npm run build && source ../../.env && npm start`
   - Auth rejection — wrong token → 403, WS without auth → 4401
   - Reconnection — disconnect WiFi → overlay → reconnect → resumes
   - Tab sleep — switch tabs → return → reconnects
   - Heartbeat — idle 2min → connection stays
   - Press any key — during backoff → immediate reconnect
   - Token rotation — change token, restart → old fails → login screen
   - Concurrent tabs — both work
   - Server restart — clients recover
3. **Update project INDEX.md** with session status
4. **Commit all changes**

## Key Architecture Decisions
- Auth disabled when OS_TERMINAL_TOKEN not set (local dev friction-free)
- WS auth is first-message based (not URL param) to avoid token in logs
- Terminal xterm instance created once, only WebSocket reconnects (no flash)
- Resize deferred to first server message (guarantees handler is registered)
- App split into App + AuthenticatedApp to fix Rules of Hooks
- Server heartbeat uses native RFC 6455 ping/pong; client uses app-level ping/pong for tab-resume detection

## Build/Test Commands
```bash
cd systems/os-terminal
npx tsc --noEmit           # Type check
npm run build              # Vite production build
npm run dev                # Dev mode (Vite + tsx watch)
source ../../.env && npm start  # Production mode
```

TypeScript compiles clean. Vite build succeeds. No runtime testing done yet.
