# OS Terminal Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Bloomberg-style terminal grid UI that connects to existing tmux-managed Claude Code sessions, accessible from any device via browser.

**Architecture:** Single Node.js server (Express + ws) serves a React frontend and relays WebSocket connections to tmux sessions via node-pty. Session state comes from existing `sessions/*.json` files written by the session management system's hooks. A file watcher pushes state changes to connected clients in real time. A single `server.on('upgrade')` dispatcher routes WebSocket connections to either the terminal relay or the state watcher.

**Tech Stack:** React 18, TypeScript, Vite, xterm.js v5, react-grid-layout, node-pty, Express, ws, PWA

---

## Project Location

`systems/os-terminal/` — consistent with the OS convention that systems are operational infrastructure. The terminal UI is a system that serves the OS, like session-manager and dispatch.

## Key Identifiers

**`session_id` (UUID) is the primary identifier** throughout the system — REST API, React component keys, layout items. Session `name` is for display only. This is because multiple state files can share the same name (e.g., old ended sessions alongside active ones).

## Prerequisites

- **Node.js 18.11+** required (`fs/promises.watch()` async iterable support). Current LTS (Node.js 20) recommended. Check with `node --version`.
- tmux 3.1+ installed (needed for `window-size latest` option). Current: tmux 3.6a.
- Xcode Command Line Tools installed (needed for node-pty native compilation).
- `OS_ROOT` environment variable set in `.env` (already present).
- `~/.tmux.conf` must include `set -g window-size latest` and `set -g default-terminal "tmux-256color"`.

---

## Task 1: Add `--non-interactive` Flag to Session CLI

**Why:** The REST API calls `session close` via `execFile`, which has no stdin. The current `close` command calls `input("Interrupt? [y/N]")` when a session stays active past the 30s timeout, which hangs in a non-TTY context.

**Files:**
- Modify: `systems/session-manager/cli.py:290-303`

**Step 1: Add `--non-interactive` argument to the close subcommand**

In `cli.py`, find the close subparser definition (variable `p_close`, around line 439) and add:

```python
p_close.add_argument("--non-interactive", action="store_true",
                     help="Skip interactive prompts (for API use)")
```

**Step 2: Update `cmd_close` to respect the flag**

Replace the interactive prompt block (lines 298-303):

```python
# Before (interactive):
#     response = input("Interrupt? [y/N] ").strip().lower()
#     if response != "y":
#         print("Aborted.")
#         return

# After:
if args.non_interactive:
    print("Session still active after 30s (non-interactive mode). Proceeding with cleanup.")
else:
    response = input("Interrupt? [y/N] ").strip().lower()
    if response != "y":
        print("Aborted.")
        return
```

**Step 3: Test the flag**

Run: `source .env && session close nonexistent-session --non-interactive`
Expected: Exits with error message about session not found (no hang, no prompt).

**Step 4: Commit**

```bash
git add systems/session-manager/cli.py
git commit -m "feat(session-manager): add --non-interactive flag to close command for API use"
```

---

## Task 2: Project Scaffolding

**Files:**
- Create: `systems/os-terminal/package.json`
- Create: `systems/os-terminal/tsconfig.json`
- Create: `systems/os-terminal/tsconfig.node.json`
- Create: `systems/os-terminal/vite.config.ts`
- Create: `systems/os-terminal/index.html`
- Create: `systems/os-terminal/.gitignore`
- Create: `systems/os-terminal/src/main.tsx`
- Create: `systems/os-terminal/src/App.tsx`
- Create: `systems/os-terminal/src/App.css`

**Step 1: Create package.json with all dependencies**

```json
{
  "name": "os-terminal",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "concurrently \"npm run dev:server\" \"npm run dev:client\"",
    "dev:client": "vite",
    "dev:server": "tsx watch server/index.ts",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "start": "node dist/server/index.js"
  },
  "dependencies": {
    "@xterm/xterm": "^5.5.0",
    "@xterm/addon-fit": "^0.10.0",
    "@xterm/addon-webgl": "^0.18.0",
    "@xterm/addon-web-links": "^0.11.0",
    "express": "^4.21.0",
    "node-pty": "^1.0.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-grid-layout": "^1.4.4",
    "react-resizable": "^3.0.5",
    "ws": "^8.18.0"
  },
  "devDependencies": {
    "@types/express": "^5.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@types/react-grid-layout": "^1.3.5",
    "@types/ws": "^8.5.0",
    "@vitejs/plugin-react": "^4.3.0",
    "concurrently": "^9.1.0",
    "tsx": "^4.19.0",
    "typescript": "^5.6.0",
    "vite": "^6.0.0"
  }
}
```

Note: `concurrently` is in `devDependencies` (dev tool only). `react-resizable` is a direct dependency (required for CSS import, transitive via react-grid-layout).

**Step 2: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  },
  "include": ["src"]
}
```

**Step 3: Create tsconfig.node.json for server code**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "noEmit": true,
    "strict": true,
    "skipLibCheck": true
  },
  "include": ["server", "vite.config.ts"]
}
```

**Step 4: Create vite.config.ts**

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3100,
    proxy: {
      '/api': 'http://localhost:3101',
      '/ws/': {
        target: 'ws://localhost:3101',
        ws: true,
      },
    },
  },
});
```

Note: Proxy key is `/ws/` (with trailing slash) to avoid matching unrelated paths like `/ws-other`.

**Step 5: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#1a1a2e" />
    <title>OS Terminal</title>
    <link rel="manifest" href="/manifest.json" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Step 6: Create src/main.tsx**

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './App.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

**Step 7: Create src/App.tsx (placeholder)**

```tsx
export default function App() {
  return <div className="app">OS Terminal</div>;
}
```

**Step 8: Create src/App.css (base styles)**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #root {
  height: 100%;
  width: 100%;
  overflow: hidden;
  background: #1a1a2e;
  color: #e0e0e0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
}

.app {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}
```

**Step 9: Create .gitignore**

```
node_modules/
dist/
.vite/
```

**Step 10: Install dependencies and verify build**

Run: `cd systems/os-terminal && npm install`
Expected: Clean install with no errors. node-pty compiles natively.

Run: `cd systems/os-terminal && npx vite build`
Expected: Build succeeds.

**Step 11: Commit**

```bash
git add systems/os-terminal/
git commit -m "feat(os-terminal): scaffold project — Vite + React + TypeScript"
```

---

## Task 3: Backend — Shared State Module, REST API, and Server Skeleton

**Files:**
- Create: `systems/os-terminal/server/types.ts`
- Create: `systems/os-terminal/server/state.ts`
- Create: `systems/os-terminal/server/routes/sessions.ts`
- Create: `systems/os-terminal/server/index.ts`

The REST API reads session state files from `$OS_ROOT/sessions/*.json`. It uses `session_id` as the primary identifier. Mutations go through the session CLI.

**Step 1: Create server/types.ts**

```typescript
export interface SessionEvent {
  type: string;
  at: string;
  summary?: string;
}

export interface SessionState {
  version: number;
  session_id: string;
  name: string;
  project: string | null;
  worktree_path: string;
  tmux_session: string;
  status: string;
  additional_dirs: string[];
  permissions: { mode: string };
  model: string;
  created_at: string;
  last_activity: string;
  context_remaining_pct: number;
  git_branch: string;
  events: SessionEvent[];
}
```

**Step 2: Create server/state.ts — shared session state reader**

This module is imported by both the REST API and the file watcher. Single source of truth for reading session state.

```typescript
import { readdir, readFile } from 'fs/promises';
import { join } from 'path';
import type { SessionState } from './types.js';

export function getOsRoot(): string {
  const root = process.env.OS_ROOT;
  if (!root) {
    throw new Error('OS_ROOT environment variable is not set. Set it in .env or export it before starting the server.');
  }
  return root;
}

export function getSessionsDir(): string {
  return join(getOsRoot(), 'sessions');
}

export function getSessionCli(): string {
  return join(getOsRoot(), 'systems/session-manager/cli.py');
}

export async function readAllSessions(): Promise<SessionState[]> {
  const dir = getSessionsDir();
  let files: string[];
  try {
    files = await readdir(dir);
  } catch {
    return [];
  }

  const sessions: SessionState[] = [];
  for (const file of files) {
    if (!file.endsWith('.json')) continue;
    try {
      const content = await readFile(join(dir, file), 'utf-8');
      sessions.push(JSON.parse(content));
    } catch {
      // Skip corrupt or partially-written files
    }
  }
  return sessions;
}

/**
 * Find a session by session_id. Returns the first match.
 */
export function findById(sessions: SessionState[], id: string): SessionState | undefined {
  return sessions.find(s => s.session_id === id);
}

/**
 * Find a session by name. Prefers active sessions over ended ones.
 * Returns undefined if no match.
 */
export function findByName(sessions: SessionState[], name: string): SessionState | undefined {
  const matches = sessions.filter(s => s.name === name);
  if (matches.length === 0) return undefined;
  // Prefer non-ended sessions
  const active = matches.find(s => !['ended', 'ended_dirty'].includes(s.status));
  return active || matches[0];
}
```

**Step 3: Create server/routes/sessions.ts**

```typescript
import { Router } from 'express';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { readAllSessions, findById, findByName, getSessionCli } from '../state.js';

const exec = promisify(execFile);
const router = Router();

// GET /api/sessions — list all sessions
router.get('/', async (_req, res) => {
  const sessions = await readAllSessions();
  res.json(sessions);
});

// GET /api/sessions/by-name/:name — lookup by name (prefers active)
router.get('/by-name/:name', async (req, res) => {
  const sessions = await readAllSessions();
  const session = findByName(sessions, req.params.name);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }
  res.json(session);
});

// GET /api/sessions/:id — lookup by session_id
router.get('/:id', async (req, res) => {
  const sessions = await readAllSessions();
  const session = findById(sessions, req.params.id);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }
  res.json(session);
});

// POST /api/sessions — create a new session
router.post('/', async (req, res) => {
  const { name, addDirs, model, permissions } = req.body;
  if (!name) {
    res.status(400).json({ error: 'name is required' });
    return;
  }

  const args = ['create', name];
  if (model) args.push('--model', model);
  if (permissions) args.push('--permissions', permissions);
  if (addDirs && Array.isArray(addDirs)) {
    for (const dir of addDirs) {
      args.push('--add-dir', dir);
    }
  }

  try {
    await exec('python3', [getSessionCli(), ...args], {
      env: { ...process.env },
      timeout: 30_000,
    });
    // Read back the created session
    const sessions = await readAllSessions();
    const session = findByName(sessions, name);
    res.status(201).json(session || { name, status: 'creating' });
  } catch (err: any) {
    res.status(500).json({ error: err.stderr || err.message });
  }
});

// DELETE /api/sessions/:id — close a session by session_id
// Resolves session_id to name for the CLI. Uses --non-interactive flag.
// Use ?force=true to destroy instead of close.
router.delete('/:id', async (req, res) => {
  const sessions = await readAllSessions();
  const session = findById(sessions, req.params.id);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }

  const { force } = req.query;
  const command = force === 'true' ? 'destroy' : 'close';
  const args = [getSessionCli(), command, session.name];
  if (command === 'close') {
    args.push('--non-interactive');
  }

  try {
    await exec('python3', args, {
      env: { ...process.env },
      timeout: 180_000, // close flow sends 3 cleanup commands, each waits up to 60s
    });
    res.json({ status: 'closed' });
  } catch (err: any) {
    res.status(500).json({ error: err.stderr || err.message });
  }
});

export default router;
```

**Step 4: Create server/index.ts — Express + single WebSocket upgrade dispatcher**

This is the server skeleton. WebSocket handlers (terminal relay and state watcher) will be added in Tasks 4 and 5. The upgrade dispatcher is set up now so both handlers register correctly from the start.

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import sessionsRouter from './routes/sessions.js';

const app = express();
const server = createServer(app);

app.use(express.json());
app.use('/api/sessions', sessionsRouter);

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok' });
});

// Error-handling middleware — catch unhandled async errors from routes
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// --- WebSocket setup ---
// Two WebSocketServer instances, both noServer: true.
// A single upgrade handler dispatches based on URL path.
export const terminalWss = new WebSocketServer({ noServer: true });
export const stateWss = new WebSocketServer({ noServer: true });

server.on('upgrade', (request, socket, head) => {
  const url = new URL(request.url || '', `http://${request.headers.host}`);

  if (url.pathname.startsWith('/ws/terminal/')) {
    terminalWss.handleUpgrade(request, socket, head, (ws) => {
      terminalWss.emit('connection', ws, request);
    });
  } else if (url.pathname === '/ws/state') {
    stateWss.handleUpgrade(request, socket, head, (ws) => {
      stateWss.emit('connection', ws, request);
    });
  } else {
    socket.destroy();
  }
});

const PORT = parseInt(process.env.PORT || '3101', 10);
server.listen(PORT, () => {
  console.log(`OS Terminal server running on port ${PORT}`);
});

export { server };
```

**Step 5: Test the REST API**

Run: `cd systems/os-terminal && source ../../.env && npx tsx server/index.ts &`

Run: `curl http://localhost:3101/api/health`
Expected: `{"status":"ok"}`

Run: `curl http://localhost:3101/api/sessions`
Expected: JSON array of session state objects.

Kill the server after testing.

**Step 6: Commit**

```bash
git add systems/os-terminal/server/
git commit -m "feat(os-terminal): backend skeleton — shared state module, REST API, single WebSocket upgrade dispatcher"
```

---

## Task 4: Backend — WebSocket Terminal Relay

**Files:**
- Create: `systems/os-terminal/server/terminal.ts`
- Modify: `systems/os-terminal/server/index.ts` (add import + init call)

Each WebSocket connection to `/ws/terminal/:name` spawns a `tmux attach-session` process via node-pty and pipes I/O bidirectionally. Handles PTY lifecycle carefully to avoid double-kill errors.

**Step 1: Create server/terminal.ts**

```typescript
import type { WebSocketServer, WebSocket } from 'ws';
import type { IncomingMessage } from 'http';
import { execFileSync } from 'child_process';
import * as pty from 'node-pty';

interface TerminalMessage {
  type: 'input' | 'resize';
  data?: string;
  cols?: number;
  rows?: number;
}

const TMUX_PREFIX = 'os-';

function tmuxSessionExists(name: string): boolean {
  try {
    execFileSync('tmux', ['has-session', '-t', name], { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}

export function initTerminalHandler(wss: WebSocketServer): void {
  wss.on('connection', (ws: WebSocket, request: IncomingMessage) => {
    const url = new URL(request.url || '', `http://${request.headers.host}`);
    const sessionName = decodeURIComponent(url.pathname.replace('/ws/terminal/', ''));
    const tmuxSession = `${TMUX_PREFIX}${sessionName}`;

    console.log(`Terminal connected: ${tmuxSession}`);

    // Validate tmux session exists before spawning PTY
    if (!tmuxSessionExists(tmuxSession)) {
      console.error(`tmux session ${tmuxSession} does not exist`);
      ws.close(1011, `tmux session not found: ${tmuxSession}`);
      return;
    }

    let ptyProcess: pty.IPty;
    try {
      ptyProcess = pty.spawn('tmux', ['attach-session', '-t', tmuxSession], {
        name: 'xterm-256color',
        cols: 80,
        rows: 30,
        cwd: process.env.HOME || '/tmp',
        env: { ...process.env, TERM: 'xterm-256color' },
      });
    } catch (err) {
      console.error(`Failed to attach to tmux session ${tmuxSession}:`, err);
      ws.close(1011, `Failed to attach to tmux session: ${tmuxSession}`);
      return;
    }

    // Track PTY lifecycle to prevent double-kill
    let ptyExited = false;

    // PTY output -> WebSocket
    ptyProcess.onData((data: string) => {
      if (ws.readyState === ws.OPEN) {
        ws.send(data);
      }
    });

    // PTY exit -> close WebSocket
    ptyProcess.onExit(({ exitCode }) => {
      ptyExited = true;
      console.log(`PTY exited for ${tmuxSession} (code ${exitCode})`);
      if (ws.readyState === ws.OPEN) {
        ws.close(1000, 'PTY process exited');
      }
    });

    // WebSocket messages -> PTY
    ws.on('message', (raw: Buffer) => {
      if (ptyExited) return;
      try {
        const msg: TerminalMessage = JSON.parse(raw.toString());
        if (msg.type === 'input' && msg.data) {
          ptyProcess.write(msg.data);
        } else if (msg.type === 'resize' && msg.cols && msg.rows) {
          ptyProcess.resize(msg.cols, msg.rows);
        }
      } catch {
        // If not valid JSON, treat as raw input
        ptyProcess.write(raw.toString());
      }
    });

    // WebSocket close -> kill PTY (if still alive)
    ws.on('close', () => {
      console.log(`Terminal disconnected: ${tmuxSession}`);
      if (!ptyExited) {
        try { ptyProcess.kill(); } catch { /* already dead */ }
      }
    });

    ws.on('error', (err) => {
      console.error(`WebSocket error for ${tmuxSession}:`, err);
      if (!ptyExited) {
        try { ptyProcess.kill(); } catch { /* already dead */ }
      }
    });
  });
}
```

**Step 2: Wire into server/index.ts**

Add to the imports and after `stateWss` declaration:

```typescript
import { initTerminalHandler } from './terminal.js';
// ... after export const terminalWss = ...
initTerminalHandler(terminalWss);
```

**Step 3: Test with a real tmux session**

Prerequisites: Have at least one managed session running.

Run: `cd systems/os-terminal && source ../../.env && npx tsx server/index.ts &`

Test with wscat:
```bash
npx wscat -c ws://localhost:3101/ws/terminal/os-development
```
Expected: Terminal output from the tmux session appears. Typing sends input.

Kill the server after testing.

**Step 4: Commit**

```bash
git add systems/os-terminal/server/terminal.ts systems/os-terminal/server/index.ts
git commit -m "feat(os-terminal): WebSocket terminal relay — node-pty pipes tmux I/O with PTY lifecycle guard"
```

---

## Task 5: Backend — State File Watcher

**Files:**
- Create: `systems/os-terminal/server/watcher.ts`
- Modify: `systems/os-terminal/server/index.ts` (add import + init call)

Watches `sessions/*.json` for changes and broadcasts updated session state to all connected clients. Uses trailing-edge debounce to coalesce rapid file events.

**Step 1: Create server/watcher.ts**

```typescript
import { watch, mkdir } from 'fs/promises';
import type { WebSocketServer, WebSocket } from 'ws';
import { readAllSessions, getSessionsDir } from './state.js';

export function initStateHandler(wss: WebSocketServer): void {
  const clients = new Set<WebSocket>();

  wss.on('connection', (ws: WebSocket) => {
    clients.add(ws);
    ws.on('close', () => clients.delete(ws));
    ws.on('error', () => clients.delete(ws));

    // Send initial state on connect
    readAllSessions().then(sessions => {
      if (ws.readyState === ws.OPEN) {
        ws.send(JSON.stringify({ type: 'sessions', data: sessions }));
      }
    });
  });

  // Watch sessions directory for changes
  startWatching(getSessionsDir(), clients);
}

async function broadcastSessions(clients: Set<WebSocket>): Promise<void> {
  const sessions = await readAllSessions();
  const message = JSON.stringify({ type: 'sessions', data: sessions });
  for (const client of clients) {
    if (client.readyState === client.OPEN) {
      client.send(message);
    }
  }
}

async function startWatching(dir: string, clients: Set<WebSocket>): Promise<void> {
  // Ensure sessions directory exists (first run or clean environment)
  await mkdir(dir, { recursive: true });

  // Trailing-edge debounce: reset timer on each event, fire once after events stop
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;

  try {
    const watcher = watch(dir, { recursive: false });
    for await (const event of watcher) {
      if (!event.filename?.endsWith('.json')) continue;

      // Reset debounce timer on each event
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        broadcastSessions(clients);
      }, 150); // 150ms trailing edge — atomic writes generate 4-5 events in ~50ms
    }
  } catch (err) {
    console.error('State watcher error:', err);
    // Retry after 5 seconds
    setTimeout(() => startWatching(dir, clients), 5000);
  }
}
```

**Step 2: Wire into server/index.ts**

Add to the imports and after `stateWss` declaration:

```typescript
import { initStateHandler } from './watcher.js';
// ... after export const stateWss = ...
initStateHandler(stateWss);
```

**Step 3: The final server/index.ts should look like this:**

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import sessionsRouter from './routes/sessions.js';
import { initTerminalHandler } from './terminal.js';
import { initStateHandler } from './watcher.js';

const app = express();
const server = createServer(app);

app.use(express.json());
app.use('/api/sessions', sessionsRouter);

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok' });
});

// Error-handling middleware
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// --- WebSocket setup ---
// Two WebSocketServer instances, both noServer: true.
// A single upgrade handler dispatches based on URL path.
const terminalWss = new WebSocketServer({ noServer: true });
const stateWss = new WebSocketServer({ noServer: true });

initTerminalHandler(terminalWss);
initStateHandler(stateWss);

server.on('upgrade', (request, socket, head) => {
  const url = new URL(request.url || '', `http://${request.headers.host}`);

  if (url.pathname.startsWith('/ws/terminal/')) {
    terminalWss.handleUpgrade(request, socket, head, (ws) => {
      terminalWss.emit('connection', ws, request);
    });
  } else if (url.pathname === '/ws/state') {
    stateWss.handleUpgrade(request, socket, head, (ws) => {
      stateWss.emit('connection', ws, request);
    });
  } else {
    socket.destroy();
  }
});

const PORT = parseInt(process.env.PORT || '3101', 10);
server.listen(PORT, () => {
  console.log(`OS Terminal server running on port ${PORT}`);
});
```

**Step 4: Commit**

```bash
git add systems/os-terminal/server/
git commit -m "feat(os-terminal): state file watcher — trailing-edge debounce, broadcasts to all clients"
```

---

## Task 6: Frontend — Terminal Component

**Files:**
- Create: `systems/os-terminal/src/components/TerminalPane.tsx`
- Create: `systems/os-terminal/src/hooks/useTerminal.ts`

The core terminal component: xterm.js instance connected to a tmux session via WebSocket. Uses `useState` for connection state (reactive). Component should be keyed by `session_id` in the parent so React forces remount when the session changes.

**Step 1: Create src/hooks/useTerminal.ts**

```typescript
import { useEffect, useRef, useCallback, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebglAddon } from '@xterm/addon-webgl';
import { WebLinksAddon } from '@xterm/addon-web-links';

interface UseTerminalOptions {
  sessionName: string;
  fontSize?: number;
}

interface UseTerminalReturn {
  containerRef: React.RefObject<HTMLDivElement | null>;
  fit: () => void;
  focus: () => void;
  isConnected: boolean;
}

export function useTerminal({ sessionName, fontSize = 14 }: UseTerminalOptions): UseTerminalReturn {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const termRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const fit = useCallback(() => {
    fitAddonRef.current?.fit();
  }, []);

  const focus = useCallback(() => {
    termRef.current?.focus();
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || termRef.current) return;

    const term = new Terminal({
      cursorBlink: true,
      fontSize,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#1a1a2e',
        foreground: '#e0e0e0',
        cursor: '#e0e0e0',
        selectionBackground: '#3a3a5e',
      },
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.loadAddon(new WebLinksAddon());

    term.open(container);

    try {
      term.loadAddon(new WebglAddon());
    } catch {
      // WebGL unavailable — DOM renderer is fine
    }

    fitAddon.fit();
    termRef.current = term;
    fitAddonRef.current = fitAddon;

    // WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/terminal/${encodeURIComponent(sessionName)}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
    };

    ws.onmessage = (event) => {
      term.write(event.data);
    };

    ws.onclose = () => {
      setIsConnected(false);
      term.write('\r\n\x1b[31m[Disconnected]\x1b[0m\r\n');
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    // User input -> WebSocket
    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'input', data }));
      }
    });

    // Resize -> WebSocket
    term.onResize(({ cols, rows }) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'resize', cols, rows }));
      }
    });

    // Cleanup
    return () => {
      ws.close();
      term.dispose();
      termRef.current = null;
      fitAddonRef.current = null;
      wsRef.current = null;
      setIsConnected(false);
    };
  }, [sessionName, fontSize]);

  return { containerRef, fit, focus, isConnected };
}
```

**Step 2: Create src/components/TerminalPane.tsx**

```tsx
import { useEffect, useImperativeHandle, forwardRef } from 'react';
import { useTerminal } from '../hooks/useTerminal';
import '@xterm/xterm/css/xterm.css';

export interface TerminalPaneHandle {
  fit: () => void;
  focus: () => void;
}

interface TerminalPaneProps {
  sessionName: string;
  status: string;
  contextPct: number;
  isMaximized: boolean;
  isFocused: boolean;
  onMaximize: () => void;
  onMinimize: () => void;
  onRestore: () => void;
  onFocus: () => void;
}

const STATUS_COLORS: Record<string, string> = {
  started: '#60a5fa',
  active: '#4ade80',
  idle: '#fbbf24',
  context_low: '#f87171',
  ended: '#6b7280',
  ended_dirty: '#ef4444',
  stale: '#6b7280',
};

export const TerminalPane = forwardRef<TerminalPaneHandle, TerminalPaneProps>(
  ({ sessionName, status, contextPct, isMaximized, isFocused, onMaximize, onMinimize, onRestore, onFocus }, ref) => {
    const { containerRef, fit, focus } = useTerminal({ sessionName });

    useImperativeHandle(ref, () => ({ fit, focus }), [fit, focus]);

    // Refit when maximized/restored
    useEffect(() => {
      const timer = setTimeout(fit, 50);
      return () => clearTimeout(timer);
    }, [isMaximized, fit]);

    const statusColor = STATUS_COLORS[status] || '#9ca3af';

    return (
      <div
        className={`terminal-pane ${isFocused ? 'focused' : ''}`}
        onClick={onFocus}
        style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
      >
        <div className="terminal-header" onDoubleClick={isMaximized ? onRestore : onMaximize}>
          <div className="terminal-header-left">
            <span className="status-dot" style={{ backgroundColor: statusColor }} />
            <span className="session-name">{sessionName}</span>
            <span className="context-pct">{contextPct}%</span>
          </div>
          <div className="terminal-header-right">
            <button className="pane-btn" onClick={(e) => { e.stopPropagation(); onMinimize(); }} title="Minimize">_</button>
            <button className="pane-btn" onClick={(e) => { e.stopPropagation(); isMaximized ? onRestore() : onMaximize(); }} title={isMaximized ? 'Restore' : 'Maximize'}>
              {isMaximized ? '\u274F' : '\u25A1'}
            </button>
          </div>
        </div>
        <div
          ref={containerRef}
          className="terminal-container"
          style={{ flex: 1, overflow: 'hidden' }}
        />
      </div>
    );
  }
);

TerminalPane.displayName = 'TerminalPane';
```

**Step 3: Add terminal pane styles to App.css**

```css
/* Terminal pane chrome */
.terminal-pane {
  border: 1px solid #2a2a4a;
  border-radius: 4px;
  overflow: hidden;
  background: #1a1a2e;
}

.terminal-pane.focused {
  border-color: #4a4a8a;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  background: #16162a;
  cursor: grab;
  user-select: none;
  height: 28px;
  min-height: 28px;
}

.terminal-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.terminal-header-right {
  display: flex;
  gap: 4px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.session-name {
  font-weight: 600;
  color: #c0c0e0;
}

.context-pct {
  color: #8888aa;
  font-size: 11px;
}

.pane-btn {
  background: none;
  border: 1px solid #3a3a5e;
  color: #8888aa;
  cursor: pointer;
  padding: 0 6px;
  border-radius: 2px;
  font-size: 12px;
  line-height: 18px;
}

.pane-btn:hover {
  background: #2a2a4e;
  color: #e0e0e0;
}

.terminal-container {
  background: #1a1a2e;
}
```

**Step 4: Commit**

```bash
git add systems/os-terminal/src/
git commit -m "feat(os-terminal): terminal pane component — xterm.js + WebSocket with reactive connection state"
```

---

## Task 7: Frontend — Grid Layout with Layout Persistence

**Files:**
- Create: `systems/os-terminal/src/components/TerminalGrid.tsx`
- Create: `systems/os-terminal/src/hooks/useSessions.ts`
- Modify: `systems/os-terminal/src/App.tsx`

The grid layout uses react-grid-layout. **`session_id` is used for all keys and layout item IDs.** Layouts are persisted to localStorage.

**Step 1: Create src/hooks/useSessions.ts**

```typescript
import { useState, useEffect, useRef } from 'react';

export interface SessionInfo {
  session_id: string;
  name: string;
  project: string | null;
  status: string;
  context_remaining_pct: number;
  model: string;
  tmux_session: string;
  last_activity: string;
  created_at: string;
}

export function useSessions(): SessionInfo[] {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/state`);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'sessions') {
            setSessions(msg.data);
          }
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onclose = () => {
        // Reconnect after 3 seconds
        reconnectTimer.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []);

  return sessions;
}
```

**Step 2: Create src/components/TerminalGrid.tsx**

```tsx
import { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import { Responsive, WidthProvider, Layout, Layouts } from 'react-grid-layout';
import { TerminalPane, TerminalPaneHandle } from './TerminalPane';
import type { SessionInfo } from '../hooks/useSessions';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGrid = WidthProvider(Responsive);
const LAYOUT_STORAGE_KEY = 'os-terminal-layouts';

interface TerminalGridProps {
  sessions: SessionInfo[];
  maximized: string | null;
  focused: string | null;
  minimized: Set<string>;
  onMaximize: (id: string) => void;
  onMinimize: (id: string) => void;
  onRestore: () => void;
  onFocus: (id: string) => void;
}

function loadSavedLayouts(): Layouts | null {
  try {
    const saved = localStorage.getItem(LAYOUT_STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

function generateDefaultLayouts(sessions: SessionInfo[]): Layouts {
  const cols = 12;
  const sessionsPerRow = Math.min(sessions.length, 3) || 1;
  const colWidth = Math.floor(cols / sessionsPerRow);

  const lg: Layout[] = sessions.map((s, i) => ({
    i: s.session_id,
    x: (i % sessionsPerRow) * colWidth,
    y: Math.floor(i / sessionsPerRow) * 4,
    w: colWidth,
    h: 4,
    minW: 2,
    minH: 2,
  }));

  return { lg, md: lg, sm: lg.map(l => ({ ...l, x: 0, w: 12 })) };
}

export function TerminalGrid({
  sessions, maximized, focused, minimized,
  onMaximize, onMinimize, onRestore, onFocus,
}: TerminalGridProps) {
  const paneRefs = useRef<Record<string, TerminalPaneHandle | null>>({});

  // Filter to active sessions (not ended/ended_dirty)
  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  // Build layouts: use saved if available, else generate defaults
  const [layouts, setLayouts] = useState<Layouts>(() => {
    return loadSavedLayouts() || generateDefaultLayouts(activeSessions);
  });

  // When new sessions appear that aren't in the layout, add them.
  // Uses functional updater to read current layout without depending on it,
  // avoiding a render loop from layouts.lg in the dependency array.
  useEffect(() => {
    setLayouts(prev => {
      const currentIds = new Set(prev.lg?.map(l => l.i) || []);
      const newSessions = activeSessions.filter(s => !currentIds.has(s.session_id));
      if (newSessions.length === 0) return prev; // no change, no re-render

      const maxY = Math.max(0, ...(prev.lg || []).map(l => l.y + l.h));
      const newItems: Layout[] = newSessions.map((s, i) => ({
        i: s.session_id,
        x: (i % 3) * 4,
        y: maxY,
        w: 4,
        h: 4,
        minW: 2,
        minH: 2,
      }));
      const lg = [...(prev.lg || []), ...newItems];
      return { lg, md: lg, sm: lg.map(l => ({ ...l, x: 0, w: 12 })) };
    });
  }, [activeSessions]); // No layouts.lg dependency — functional updater reads it

  // Debounced localStorage persistence — avoid writing on every drag frame
  const saveTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const handleLayoutChange = useCallback((_current: Layout[], allLayouts: Layouts) => {
    setLayouts(allLayouts);
    // Debounce localStorage writes — onLayoutChange fires on every drag frame
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(allLayouts));
    }, 300);
    // Refit all terminals after layout change
    setTimeout(() => {
      Object.values(paneRefs.current).forEach(ref => ref?.fit());
    }, 50);
  }, []);

  const handleResizeStop = useCallback(() => {
    // Refit all terminals after any resize
    setTimeout(() => {
      Object.values(paneRefs.current).forEach(ref => ref?.fit());
    }, 50);
  }, []);

  // Maximized view: single pane fills the viewport
  if (maximized) {
    const session = activeSessions.find(s => s.session_id === maximized);
    if (!session) {
      onRestore();
      return null;
    }
    return (
      <div style={{ height: '100%', padding: 4 }}>
        <TerminalPane
          key={session.session_id}
          ref={(el) => { paneRefs.current[session.session_id] = el; }}
          sessionName={session.name}
          status={session.status}
          contextPct={session.context_remaining_pct}
          isMaximized={true}
          isFocused={true}
          onMaximize={() => {}}
          onMinimize={() => { onRestore(); onMinimize(session.session_id); }}
          onRestore={onRestore}
          onFocus={() => onFocus(session.session_id)}
        />
      </div>
    );
  }

  const visibleSessions = activeSessions.filter(s => !minimized.has(s.session_id));

  return (
    <ResponsiveGrid
      className="terminal-grid"
      layouts={layouts}
      breakpoints={{ lg: 1200, md: 996, sm: 768 }}
      cols={{ lg: 12, md: 12, sm: 12 }}
      rowHeight={80}
      draggableHandle=".terminal-header"
      onResizeStop={handleResizeStop}
      onLayoutChange={handleLayoutChange}
      compactType="vertical"
      margin={[4, 4]}
    >
      {visibleSessions.map(session => (
        <div key={session.session_id}>
          <TerminalPane
            key={session.session_id}
            ref={(el) => { paneRefs.current[session.session_id] = el; }}
            sessionName={session.name}
            status={session.status}
            contextPct={session.context_remaining_pct}
            isMaximized={false}
            isFocused={focused === session.session_id}
            onMaximize={() => onMaximize(session.session_id)}
            onMinimize={() => onMinimize(session.session_id)}
            onRestore={() => {}}
            onFocus={() => { onFocus(session.session_id); paneRefs.current[session.session_id]?.focus(); }}
          />
        </div>
      ))}
    </ResponsiveGrid>
  );
}
```

**Step 3: Update src/App.tsx — lift grid state for keyboard shortcuts**

Note: This imports `SessionPanel` which is created in Task 8. If executing tasks sequentially with type-checking between commits, either create Task 8's `SessionPanel.tsx` as a stub first, or skip the type check until Task 8 is done.

```tsx
import { useState, useMemo, useCallback } from 'react';
import { useSessions } from './hooks/useSessions';
import { TerminalGrid } from './components/TerminalGrid';
import { SessionPanel } from './components/SessionPanel';

export default function App() {
  const sessions = useSessions();
  const [panelOpen, setPanelOpen] = useState(true);
  const [maximized, setMaximized] = useState<string | null>(null);
  const [focused, setFocused] = useState<string | null>(null);
  const [minimized, setMinimized] = useState<Set<string>>(new Set());

  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  const handleMaximize = useCallback((id: string) => setMaximized(id), []);
  const handleMinimize = useCallback((id: string) => {
    setMinimized(prev => new Set(prev).add(id));
  }, []);
  const handleRestore = useCallback(() => setMaximized(null), []);
  const handleFocus = useCallback((id: string) => setFocused(id), []);

  return (
    <div className="app">
      <div className="top-bar">
        <button className="toggle-panel" onClick={() => setPanelOpen(!panelOpen)}>
          {panelOpen ? '\u25C0' : '\u25B6'}
        </button>
        <span className="app-title">OS Terminal</span>
        <span className="session-count">{activeSessions.length} active</span>
      </div>
      <div className="main-content">
        {panelOpen && (
          <SessionPanel
            sessions={sessions}
            onCreateSession={() => {/* TODO: create session modal */}}
          />
        )}
        <div className="grid-area">
          <TerminalGrid
            sessions={sessions}
            maximized={maximized}
            focused={focused}
            minimized={minimized}
            onMaximize={handleMaximize}
            onMinimize={handleMinimize}
            onRestore={handleRestore}
            onFocus={handleFocus}
          />
        </div>
      </div>
    </div>
  );
}
```

**Step 4: Add grid styles to App.css**

```css
/* Top bar */
.top-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 12px;
  background: #12122a;
  border-bottom: 1px solid #2a2a4a;
  height: 32px;
  min-height: 32px;
}

.toggle-panel {
  background: none;
  border: none;
  color: #8888aa;
  cursor: pointer;
  font-size: 14px;
  padding: 2px 6px;
}

.toggle-panel:hover {
  color: #e0e0e0;
}

.app-title {
  font-size: 13px;
  font-weight: 700;
  color: #6a6aaa;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.session-count {
  font-size: 12px;
  color: #6b7280;
  margin-left: auto;
}

/* Main content layout */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.grid-area {
  flex: 1;
  overflow: auto;
}

/* Grid overrides */
.terminal-grid {
  height: 100%;
}

.react-grid-item {
  transition: none !important;
}

.react-grid-item > .react-resizable-handle {
  background: none;
  border-right: 2px solid #3a3a5e;
  border-bottom: 2px solid #3a3a5e;
}
```

**Step 5: Commit**

```bash
git add systems/os-terminal/src/
git commit -m "feat(os-terminal): terminal grid with layout persistence — session_id keys, localStorage save/restore"
```

---

## Task 8: Frontend — Session Panel

**Files:**
- Create: `systems/os-terminal/src/components/SessionPanel.tsx`
- Modify: `systems/os-terminal/src/App.css`

A sidebar showing all sessions with status, context %, and controls.

**Step 1: Create src/components/SessionPanel.tsx**

```tsx
import type { SessionInfo } from '../hooks/useSessions';

interface SessionPanelProps {
  sessions: SessionInfo[];
  onCreateSession: () => void;
}

const STATUS_COLORS: Record<string, string> = {
  started: '#60a5fa',
  active: '#4ade80',
  idle: '#fbbf24',
  context_low: '#f87171',
  ended: '#6b7280',
  ended_dirty: '#ef4444',
  stale: '#6b7280',
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function SessionPanel({ sessions, onCreateSession }: SessionPanelProps) {
  const activeSessions = sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status));
  const endedSessions = sessions.filter(s => ['ended', 'ended_dirty'].includes(s.status));

  return (
    <div className="session-panel">
      <div className="panel-header">
        <h2>Sessions</h2>
        <button className="create-btn" onClick={onCreateSession}>+</button>
      </div>

      <div className="panel-section">
        <h3>Active ({activeSessions.length})</h3>
        {activeSessions.map(s => (
          <div key={s.session_id} className="session-card">
            <div className="session-card-header">
              <span className="status-dot" style={{ backgroundColor: STATUS_COLORS[s.status] || '#9ca3af' }} />
              <span className="session-card-name">{s.name}</span>
            </div>
            <div className="session-card-meta">
              <span>{s.status}</span>
              <span>ctx {s.context_remaining_pct}%</span>
              <span>{timeAgo(s.last_activity)}</span>
            </div>
          </div>
        ))}
      </div>

      {endedSessions.length > 0 && (
        <div className="panel-section">
          <h3>Ended ({endedSessions.length})</h3>
          {endedSessions.slice(0, 5).map(s => (
            <div key={s.session_id} className="session-card ended">
              <div className="session-card-header">
                <span className="status-dot" style={{ backgroundColor: STATUS_COLORS[s.status] || '#9ca3af' }} />
                <span className="session-card-name">{s.name}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

**Step 2: Add panel styles to App.css**

```css
/* Session panel */
.session-panel {
  width: 220px;
  min-width: 220px;
  background: #12122a;
  border-right: 1px solid #2a2a4a;
  overflow-y: auto;
  padding: 8px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 4px 8px;
}

.panel-header h2 {
  font-size: 14px;
  font-weight: 600;
  color: #c0c0e0;
}

.create-btn {
  background: #2a2a4e;
  border: 1px solid #3a3a5e;
  color: #8888aa;
  cursor: pointer;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.create-btn:hover {
  background: #3a3a5e;
  color: #e0e0e0;
}

.panel-section h3 {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #6b7280;
  padding: 8px 4px 4px;
}

.session-card {
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 2px;
}

.session-card:hover {
  background: #1a1a3e;
}

.session-card.ended {
  opacity: 0.5;
}

.session-card-header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.session-card-name {
  font-size: 13px;
  font-weight: 500;
  color: #c0c0e0;
}

.session-card-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #6b7280;
  padding-left: 14px;
  margin-top: 2px;
}
```

**Step 3: Commit**

```bash
git add systems/os-terminal/src/
git commit -m "feat(os-terminal): session panel sidebar — status colors, context %, time ago, session_id keys"
```

---

## Task 9: Keyboard Shortcuts

**Files:**
- Create: `systems/os-terminal/src/hooks/useKeyboardShortcuts.ts`
- Modify: `systems/os-terminal/src/App.tsx`

Uses `useRef` for the actions object to avoid stale closure issues when the actions object is recreated on render.

**Step 1: Create src/hooks/useKeyboardShortcuts.ts**

```typescript
import { useEffect, useRef } from 'react';

interface ShortcutActions {
  focusPane: (index: number) => void;
  createSession: () => void;
  closePane: () => void;
  escapeMaximize: () => void;
  togglePanel: () => void;
}

export function useKeyboardShortcuts(actions: ShortcutActions): void {
  // Use ref to avoid stale closures — actions object may change every render
  const actionsRef = useRef(actions);
  actionsRef.current = actions;

  useEffect(() => {
    function handler(e: KeyboardEvent) {
      // Don't capture shortcuts when typing in an input/textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;

      const meta = e.metaKey || e.ctrlKey;

      // Cmd+1-9: focus pane by index
      if (meta && e.key >= '1' && e.key <= '9') {
        e.preventDefault();
        actionsRef.current.focusPane(parseInt(e.key) - 1);
        return;
      }

      // Cmd+N: create session
      if (meta && e.key === 'n') {
        e.preventDefault();
        actionsRef.current.createSession();
        return;
      }

      // Cmd+W: close/minimize focused pane
      if (meta && e.key === 'w') {
        e.preventDefault();
        actionsRef.current.closePane();
        return;
      }

      // Escape: restore from maximized
      if (e.key === 'Escape') {
        actionsRef.current.escapeMaximize();
        return;
      }

      // Cmd+B: toggle panel
      if (meta && e.key === 'b') {
        e.preventDefault();
        actionsRef.current.togglePanel();
        return;
      }
    }

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []); // Empty deps — actionsRef keeps it fresh
}
```

**Step 2: Wire into App.tsx**

Add to the App component after the state declarations:

```typescript
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

// Inside App():
useKeyboardShortcuts({
  focusPane: (index: number) => {
    const active = sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status));
    if (active[index]) {
      setFocused(active[index].session_id);
    }
  },
  createSession: () => {/* TODO: create session modal */},
  closePane: () => {
    if (focused) {
      setMinimized(prev => new Set(prev).add(focused));
    }
  },
  escapeMaximize: () => setMaximized(null),
  togglePanel: () => setPanelOpen(prev => !prev),
});
```

**Step 3: Commit**

```bash
git add systems/os-terminal/src/
git commit -m "feat(os-terminal): keyboard shortcuts — Cmd+1-9, Cmd+N, Cmd+W, Escape, Cmd+B with ref-based actions"
```

---

## Task 10: Responsive Mobile Layout

**Files:**
- Modify: `systems/os-terminal/src/App.css`
- Modify: `systems/os-terminal/src/App.tsx`

On screens < 768px, collapse to a single-pane view with a slide-out drawer for switching sessions.

**Step 1: Add CSS media queries to App.css**

```css
@media (max-width: 768px) {
  .session-panel {
    position: fixed;
    left: 0;
    top: 32px;
    bottom: 0;
    z-index: 100;
    width: 260px;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.5);
  }

  .session-panel.mobile-open {
    transform: translateX(0);
  }

  .grid-area {
    position: relative;
    width: 100%;
  }

  .top-bar {
    padding: 4px 8px;
  }
}
```

**Step 2: Add mobile-open class toggle in App.tsx**

On mobile, toggle the `mobile-open` class on the session panel based on `panelOpen` state. The `SessionPanel` div gets `className={`session-panel ${panelOpen ? 'mobile-open' : ''}`}` on mobile. Use a `useMediaQuery` check or just apply the class unconditionally (CSS media query controls visibility).

**Step 3: Commit**

```bash
git add systems/os-terminal/src/
git commit -m "feat(os-terminal): responsive mobile layout — slide-out drawer for session switching"
```

---

## Task 11: PWA Manifest and tmux Configuration

**Files:**
- Create: `systems/os-terminal/public/manifest.json`
- Create: `systems/os-terminal/tmux.conf`

**Step 1: Create public/manifest.json**

```json
{
  "name": "OS Terminal",
  "short_name": "OS Terminal",
  "description": "Bloomberg-style terminal grid for Claude Code sessions",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a2e",
  "theme_color": "#1a1a2e",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

Note: No service worker in V1. The manifest enables "Add to Home Screen" on mobile browsers. Offline capability is not needed (always connected to backend).

**Step 2: Create tmux.conf — recommended settings**

```bash
# Required for OS Terminal multi-client web access
# Add these to ~/.tmux.conf (requires tmux 3.1+)

set -g default-terminal "tmux-256color"
set -g window-size latest          # Use most recent client's size (not smallest)
set -g mouse on                    # Enable mouse in web terminal
```

**Step 3: Commit**

```bash
git add systems/os-terminal/public/ systems/os-terminal/tmux.conf
git commit -m "feat(os-terminal): PWA manifest and recommended tmux configuration"
```

---

## Task 12: Integration Test — Full Stack

**Steps:**

1. Ensure `~/.tmux.conf` includes `set -g window-size latest`
2. Ensure at least one managed session is running (check `source .env && session list`)
3. Start the full stack: `cd systems/os-terminal && source ../../.env && npm run dev`
4. Open `http://localhost:3100` in browser

**Verify each feature:**

| # | Test | Expected |
|---|------|----------|
| 1 | Page loads | Session panel on left shows all active sessions. Grid shows terminal panes. |
| 2 | Terminal I/O | Type in a pane — input appears in the tmux session. Claude output appears in the pane. |
| 3 | Correct routing | Each pane connects to the correct tmux session (verify by session name in header). |
| 4 | Drag pane header | Grid layout rearranges. Other panes don't overlap. |
| 5 | Resize pane edge | Terminal refits to new dimensions. No truncated output. |
| 6 | Double-click header | Pane maximizes to fill viewport. |
| 7 | Escape from maximized | Returns to grid view. |
| 8 | Minimize button | Pane disappears from grid. |
| 9 | Cmd+1 | Focuses first pane. |
| 10 | Cmd+B | Toggles session panel. |
| 11 | Create session externally | Run `session create test-terminal` in another terminal. New pane auto-appears. |
| 12 | Close session externally | Run `session destroy test-terminal`. Pane updates status. |
| 13 | Reload page | Layout is restored from localStorage. Terminals reconnect. |
| 14 | Multiple browser tabs | Both tabs show the same session output (tmux native multi-client). |

**Step 1: Fix any issues discovered during testing**

**Step 2: Final commit**

```bash
git add -A
git commit -m "feat(os-terminal): V1 complete — Bloomberg-style terminal grid with live session state"
```

---

## Task Summary

| Task | What | Key Files |
|------|------|-----------|
| 1 | Add `--non-interactive` to session CLI | `systems/session-manager/cli.py` |
| 2 | Project scaffolding | `systems/os-terminal/package.json`, configs |
| 3 | Backend: shared state, REST API, server skeleton | `server/state.ts`, `server/routes/sessions.ts`, `server/index.ts` |
| 4 | Backend: WebSocket terminal relay | `server/terminal.ts` |
| 5 | Backend: state file watcher | `server/watcher.ts` |
| 6 | Frontend: terminal component | `src/components/TerminalPane.tsx`, `src/hooks/useTerminal.ts` |
| 7 | Frontend: grid layout + persistence | `src/components/TerminalGrid.tsx`, `src/hooks/useSessions.ts` |
| 8 | Frontend: session panel | `src/components/SessionPanel.tsx` |
| 9 | Keyboard shortcuts | `src/hooks/useKeyboardShortcuts.ts` |
| 10 | Responsive mobile layout | CSS media queries |
| 11 | PWA manifest + tmux config | `public/manifest.json`, `tmux.conf` |
| 12 | Integration test | Manual verification, 14-point checklist |

**Total: 12 tasks**

---

## Key Technical Notes for the Implementer

### WebSocket upgrade routing
The server uses a **single** `server.on('upgrade')` handler in `index.ts` that dispatches to the correct `WebSocketServer` based on URL path. `terminal.ts` and `watcher.ts` export `init*Handler(wss)` functions that register `wss.on('connection')` — they never touch the HTTP server directly. This avoids the dual-handler bug where multiple upgrade handlers race on the same socket.

### session_id is the primary identifier
All React component keys, layout item IDs, and state tracking (maximized, focused, minimized sets) use `session_id` (UUID). Session `name` is display-only. This prevents bugs from duplicate names across active and ended sessions.

### xterm.js v5 package names
All packages use the `@xterm/*` scope. The old `xterm` package is deprecated.

### WebGL context limit
Browsers limit WebGL contexts to 8-16 per page. The `try/catch` around `WebglAddon` loading handles this — terminals beyond the limit fall back to the DOM renderer.

### tmux window-size
`set -g window-size latest` in `~/.tmux.conf` is **required**. Without it, tmux constrains all clients to the smallest terminal size.

### node-pty native compilation
Requires Xcode Command Line Tools on macOS (`xcode-select --install`).

### OS_ROOT environment variable
**Must be set** before starting the server. The server throws immediately if it's not set — no silent fallback to a hardcoded path.

### React StrictMode double-mount
The `useTerminal` hook guards against this with `if (termRef.current) return`. Additionally, keying `TerminalPane` by `session_id` ensures React forces a full unmount/remount cycle when the session changes.

### Close command non-interactive mode
The REST API DELETE endpoint passes `--non-interactive` to the session CLI close command. This prevents the process from hanging on the `input()` prompt when a session stays active past the timeout. The non-interactive mode proceeds with cleanup regardless.

### Layout persistence
Grid layouts are saved to `localStorage` under the key `os-terminal-layouts` with a debounced write (300ms) to avoid writing on every drag frame. When new sessions appear that aren't in the saved layout, they're added at the bottom of the grid using a functional state updater (no `layouts.lg` in the dependency array to avoid render loops). Ended sessions are not removed from the saved layout (they just won't render).

### Terminal relay validation
Before spawning a PTY process, `terminal.ts` checks that the tmux session exists via `tmux has-session -t <name>`. If the session doesn't exist, the WebSocket is closed with an error message immediately — no orphaned PTY process.

### Sessions directory auto-creation
The state file watcher calls `mkdir(dir, { recursive: true })` before starting the `fs.watch` loop. This prevents ENOENT errors on first run or clean environments.

### Node.js version requirement
Node.js 18.11+ is required for `fs/promises.watch()` async iterable support. Node.js 20 LTS is recommended.

### Express error middleware
An error-handling middleware catches unhandled async errors from route handlers and returns a clean 500 JSON response instead of leaking stack traces.

### Task ordering note
Task 7 (App.tsx) imports `SessionPanel` which is created in Task 8. If type-checking between commits, create a stub `SessionPanel.tsx` first, or defer type-checking until Task 8 is complete.
