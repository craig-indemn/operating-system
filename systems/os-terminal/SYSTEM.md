# OS Terminal

Bloomberg-style terminal grid UI for monitoring and interacting with Claude Code sessions. React + xterm.js frontend, Node.js backend with WebSocket relay to tmux sessions.

## Quick Start

```bash
# Build and start (production)
cd systems/os-terminal
npm run build
source ../../.env && npm start

# Development (hot reload)
cd systems/os-terminal
source ../../.env && npm run dev
```

**Access:** `http://localhost:3101` (production) or `http://localhost:3100` (dev)
**Remote:** `https://craig.taila9a6ac.ts.net` via Tailscale Serve

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OS_ROOT` | Yes | — | Path to OS repo root (e.g., `/Users/home/Repositories/operating-system`) |
| `OS_TERMINAL_TOKEN` | No | — | Bearer token for auth. When set, login is required. When unset, no-auth mode. |
| `PORT` | No | `3101` | Server listen port |

All variables should be in the repo root `.env` file (sourced automatically).

## Prerequisites

- Node.js 18.11+ (for `fs/promises.watch()`)
- tmux 3.1+ (for `window-size latest`)
- `~/.tmux.conf` must include:
  ```
  set -g default-terminal "tmux-256color"
  set -g window-size latest
  set -g mouse on
  ```
- Reference tmux.conf: `systems/os-terminal/tmux.conf`

## Architecture

- **Frontend:** React + xterm.js, Vite-built SPA served from `dist/`
- **Backend:** Express + ws, single Node.js process
- **WebSocket routes:** `/ws/terminal/:name` (PTY relay), `/ws/state` (live session updates)
- **State source:** Session state files in `sessions/*.json` (written by session-manager hooks)
- **Terminal relay:** node-pty spawns `tmux attach -t <name>`, pipes I/O over WebSocket

## Capabilities

- Live terminal grid with CSS auto-grid layout (600px min column width)
- Single-pane mode on mobile/tablet (≤1024px) with bottom tab bar
- Drag-to-swap terminal positions (persisted in localStorage)
- Session panel with create dropdown (Claude Session or plain Terminal)
- Plain shell terminals alongside Claude sessions (SSH, commands, etc.)
- Token-based auth for remote access
- WebSocket reconnection with heartbeat keepalive
- Responsive touch-friendly targets (44px) on mobile

## Skills

None — the terminal UI is accessed directly via browser. The `/sessions` skill manages the sessions that appear in the terminal grid.

## State

- **No persistent state of its own** — reads session state from `sessions/*.json`
- **Layout order** — persisted in browser localStorage
- **Auth tokens** — in-memory on server, browser sessionStorage on client

## Dependencies

- Session manager — provides session state files and tmux sessions
- tmux — terminal multiplexer (sessions must exist as tmux sessions)
- Node.js + npm — runtime and package manager

## Integration Points

- **Reads from:** `sessions/*.json` state files, tmux session list
- **Writes to:** nothing — UI mutations go through the `session` CLI
- **Serves:** browser clients (local or remote via Tailscale)
