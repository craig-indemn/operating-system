---
ask: "Design the visual interface for the operating system — Bloomberg-style terminal grid, remote access from any device, voice layer architecture, thin web layer on top of session management system"
created: 2026-03-02
workstream: os-development
session: 2026-03-02-b
sources:
  - type: local-artifact
    ref: "projects/os-development/artifacts/2026-03-01-ea-session-management-design.md"
    name: "EA & Session Management Design (the backend this builds on)"
  - type: local-doc
    ref: "docs/Indemn AI-First Operating System — Project Plan.md"
    name: "Kyle's original project plan"
---

# OS Terminal Design

Full design document at: `docs/plans/2026-03-02-os-terminal-design.md`

## Summary

Bloomberg-style grid of live Claude Code terminal sessions, accessible from any device. Thin React + xterm.js web layer on top of the existing session management system. State files are the single source of truth — the UI reads them, mutations go through the session CLI.

## Architecture

- **UI:** React + xterm.js + react-grid-layout. PWA + Capacitor for iOS.
- **Backend:** Single Node.js server — REST API for session state, WebSocket relay to tmux via node-pty, file watcher for live updates.
- **Voice (future):** Sidecar service — STT/TTS with intent routing. Three input types: UI commands, EA commands, session input.

## Implementation Phases

1. **V1 — Terminal Grid:** Backend + React frontend + grid layout + live state. Local only.
2. **V2 — Remote Access & iOS:** Capacitor, auth, Tailscale/tunnel, reconnection.
3. **V3 — Voice Layer:** STT/TTS sidecar, intent routing, WebRTC audio.
4. **V4 — Augmentation:** Overlays, context panels, EA dashboard.

## Key Decisions

- Bloomberg terminal UX model
- React + xterm.js + react-grid-layout
- Capacitor for iOS App Store
- UI never writes state files directly — all mutations via session CLI
- EA is a regular session in the grid
- Voice is an independent sidecar, layered on top
- State files remain single source of truth
