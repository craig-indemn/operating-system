# Design: OS Terminal — Visual Interface to the Indemn Operating System

**Date:** 2026-03-02
**Status:** Approved — ready for implementation planning

## Problem

The operating system has a robust session management backend — CLI, hooks, state files, worktree isolation. But the only interface is the terminal. There's no way to:
- See all running sessions at once from any device
- Switch between sessions without manually attaching to tmux panes
- Access sessions remotely (phone, iPad, another machine)
- Layer voice interaction on top of sessions

The vision is a Bloomberg terminal for Claude Code sessions — a grid of live terminals you can rearrange, focus, and talk to from anywhere.

## Vision

A thin web layer on top of tmux sessions. The session management system is the backend; this is the frontend. A single UI that shows all sessions, lets you interact with any of them, and works on desktop, tablet, and phone. Voice is a first-class interaction mode layered on top — not the first build, but baked into the architecture from day one.

The EA session is the control plane. It creates, closes, monitors, and orchestrates sessions. The UI reads the same state files the EA produces. Whether a session is created by the EA, the CLI, or a button in the UI — they all write to the same state files, and the UI reflects the change immediately.

---

## System Architecture

### Three Layers

| Layer | What It Does | Runs Where |
|-------|-------------|------------|
| **UI** | React app — grid of xterm.js terminals, session management | Browser, PWA, iOS (Capacitor) |
| **Backend** | WebSocket relay to tmux, REST API for session state, voice service integration | Same machine as tmux (local Mac today, remote server later) |
| **Voice** | STT/TTS processing, routes transcribed text to sessions | Local Mac, GPU server, or cloud — independent deployment |

### What Already Exists (unchanged)

- Session management CLI (`session create/list/close/...`)
- Session state files (`sessions/*.json`)
- Hooks that update state in real time
- tmux sessions running Claude Code
- EA session with `/sessions` skill for orchestration

### Data Flow

```
Browser / Desktop / iOS App
        |
   Voice stream (WebRTC/WebSocket) ─── Voice Service (STT ↔ TTS)
        |                                      |
   WebSocket (terminal I/O)              Transcribed text
        |                                      |
   Node.js Backend ◄──────────────────────────┘
   ├── REST API (reads sessions/*.json)
   ├── Terminal relay (node-pty → tmux attach)
   └── File watcher (pushes state changes to clients)
        |
   tmux sessions (Claude Code)
        |
   Session state files (sessions/*.json)
        ^
        |── updated by hooks from each Claude Code session
        |── updated by session CLI (create, close, destroy)
        |── read by EA, UI, and CLI
```

### Single Source of Truth

The state files are the single source of truth. The UI never writes state files directly — it goes through the CLI. All mutation paths converge:

| Action Source | Path |
|--------------|------|
| EA creates session | `session create` → writes state file → file watcher → UI updates |
| User clicks "New Session" in UI | REST API → `session create` → writes state file → file watcher → UI updates |
| User types `session create` in terminal | CLI → writes state file → file watcher → UI updates |

No sync problems because there's only one source of truth.

### The EA in the Grid

The EA is a session like any other. It shows up as a pane in the terminal grid. You can see what it's doing, talk to it, maximize it. From the UI's perspective, it's just another terminal pane — the difference is the EA has the `/sessions` skill loaded and understands orchestration.

---

## UI Architecture

### Grid System

React with `react-grid-layout` — a draggable, resizable grid where each cell is a terminal pane. Layouts persist across page reloads (saved to localStorage or the backend).

### Terminal Panes

Each pane is an xterm.js instance connected via WebSocket to a tmux session. The pane has a thin header bar showing:
- Session name
- Status indicator (active/idle/context low)
- Minimize/maximize buttons
- Context % remaining

### Dynamic Behavior

- When a new session is created (detected via state file watcher), a new pane appears in the grid automatically
- When a session ends, its pane grays out or closes (configurable)
- Minimize collapses a pane to just its header bar in the grid
- Maximize expands a pane to fill the entire viewport — one click to go back to grid view
- Double-click a pane header to maximize/restore (like a desktop OS)

### Responsive Layout

- **Desktop:** full grid, multiple panes visible simultaneously
- **Tablet:** 2-column grid or single-column with larger panes
- **Phone:** single pane view with a session drawer/sidebar to switch between sessions

### Session Management Panel

A sidebar or top bar that shows all sessions (mirrors `session list`). From here you can:
- Create a new session
- Attach to an existing session (opens its pane)
- Close/destroy a session
- See at a glance: name, status, context %, last activity

### Keyboard Shortcuts

- `Cmd+1-9` to focus a specific pane
- `Cmd+N` to create a new session
- `Cmd+W` to close/minimize the focused pane
- `Escape` to return from maximized to grid view

---

## Backend Architecture

### Single Node.js Server

Three responsibilities:

**1. REST API — session state**
```
GET  /api/sessions          → reads sessions/*.json, returns all sessions
GET  /api/sessions/:name    → single session detail
POST /api/sessions          → calls `session create` CLI
DELETE /api/sessions/:name  → calls `session close` CLI
```

Thin wrapper around the session CLI and state files. No database — just reads JSON files from disk and calls the CLI for mutations.

**2. WebSocket — terminal I/O**
```
WS /terminal/:name → spawns `tmux attach-session -t os-<name>`
```

Each WebSocket connection spawns a tmux attach process via `node-pty` (pseudo-terminal). Keystrokes from the browser flow in, terminal output flows back. Multiple clients can connect to the same session simultaneously — they all see the same tmux output (native tmux behavior).

**3. WebSocket — live state updates**

File watcher on `sessions/*.json` using `fs.watch`. When any state file changes (hooks fire, session created/closed), push the updated state to all connected clients. This is how panes appear automatically when sessions are created — no polling.

### Server Structure

```
os-terminal/
├── server/
│   ├── index.ts              # Express + WebSocket server
│   ├── routes/sessions.ts    # REST API
│   ├── terminal.ts           # WebSocket ↔ node-pty ↔ tmux
│   └── watcher.ts            # File watcher for state updates
├── src/                      # React app
│   ├── App.tsx
│   ├── components/
│   │   ├── Grid.tsx          # react-grid-layout wrapper
│   │   ├── TerminalPane.tsx  # xterm.js + pane chrome
│   │   └── SessionPanel.tsx  # sidebar/session list
│   └── hooks/
│       ├── useSession.ts     # WebSocket state subscription
│       └── useTerminal.ts    # Terminal WebSocket connection
├── package.json
└── capacitor.config.ts       # iOS/PWA config
```

### Deployment

**Today:** `node server/index.ts` runs on your Mac alongside tmux. Connect via `localhost`. For remote access later, put it behind Tailscale or an SSH tunnel — same server, just network-accessible.

---

## Voice Layer Architecture

**Not built in V1. Architected for from day one.**

The voice service is a sidecar — it connects to the same backend but adds audio I/O.

### How It Works

```
Microphone (phone/AirPods/desktop)
       |
  Audio stream (WebRTC or WebSocket)
       |
  Voice Service
  ├── STT: audio → text (Whisper, Deepgram, or similar)
  ├── Intent routing: "switch to platform-dev" → UI command
  │                   "run the tests" → text to active session
  ├── TTS: Claude's response → audio (ElevenLabs, or local model)
       |
  Audio back to device
```

### Three Types of Voice Input

| Input | What Happens |
|-------|-------------|
| UI command — "switch to voice-evals" | UI switches focused pane, no text sent to tmux |
| EA command — "create a new session for platform work" | Routed to the EA session as text input |
| Session input — "run the tests" | Transcribed text sent to the currently focused session via WebSocket |

### Intent Routing

The voice service needs to distinguish between commands to the UI (navigation), commands to the EA (orchestration), and input to the active session (work).

- **Keyword-based** for initial implementation: "hey OS" prefix for UI/EA commands, everything else goes to the active session
- **LLM-classified** later: a small fast model classifies intent before routing

### Deployment Options

- On your Mac: local Whisper for STT, fast and private
- On a server: if you want lower latency or better models
- Hybrid: STT local, TTS cloud (or vice versa)

The voice service is fully independent of the terminal UI — it connects to the same backend WebSocket. You can run the UI without voice, or add voice later without changing the UI.

---

## Implementation Priorities

### V1 — The Terminal Grid (build now)

- Node.js backend: REST API for sessions, WebSocket relay to tmux via node-pty
- React frontend: `react-grid-layout` + xterm.js
- File watcher for live state updates
- Responsive layout (desktop grid, mobile single-pane)
- PWA manifest (installable from browser)
- Runs on localhost, connects to local tmux
- Keyboard shortcuts for pane navigation

### V2 — Remote Access & iOS

- Capacitor wrapper for App Store distribution
- Authentication layer (token-based, since it's now network-accessible)
- Tailscale or tunnel setup for accessing the backend remotely
- Connection resilience (reconnect on network drop, session state preserved)

### V3 — Voice Layer

- Voice service sidecar (STT/TTS)
- Intent routing (UI commands vs EA commands vs session input)
- Audio streaming via WebRTC
- Wake word or push-to-talk modes

### V4 — Augmentation

- Overlay UI on top of terminal panes (status, buttons, actions)
- Session-aware context panels (show project INDEX.md alongside terminal)
- EA dashboard view (unified status across all sessions, not just terminal output)

---

## Key Decisions

- 2026-03-02: Bloomberg terminal is the UX model — grid of live terminals, rearrangeable, minimize/maximize
- 2026-03-02: React + xterm.js + react-grid-layout for the frontend
- 2026-03-02: Capacitor for iOS App Store distribution (same React codebase)
- 2026-03-02: Single Node.js backend — REST API, WebSocket terminal relay, file watcher
- 2026-03-02: UI never writes state files directly — all mutations go through the session CLI
- 2026-03-02: EA is a session in the grid like any other — the UI doesn't special-case it
- 2026-03-02: Voice is a sidecar service, independent of the terminal UI, layered on top
- 2026-03-02: Voice intent routing: keyword-based first, LLM-classified later
- 2026-03-02: V1 is local only (localhost). Remote access and auth added in V2.
- 2026-03-02: State files remain the single source of truth — UI, EA, and CLI all converge on them

## Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Node.js | Backend server | Installed |
| React | Frontend framework | Standard, install via create-react-app or Vite |
| xterm.js | Terminal emulator in browser | npm package |
| react-grid-layout | Draggable/resizable grid | npm package |
| node-pty | Pseudo-terminal for tmux attach | npm package (native module) |
| ws | WebSocket server | npm package |
| Capacitor | iOS/PWA wrapper | npm package (V2) |
| tmux | Terminal multiplexer | Installed |
| Session management system | State files, CLI, hooks | Built (just completed) |

## References

- [EA & Session Management Design](../projects/os-development/artifacts/2026-03-01-ea-session-management-design.md)
- [xterm.js](https://xtermjs.org/)
- [react-grid-layout](https://github.com/react-grid-layout/react-grid-layout)
- [node-pty](https://github.com/microsoft/node-pty)
- [Capacitor](https://capacitorjs.com/)
