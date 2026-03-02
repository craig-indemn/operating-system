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

// Resolve tmux binary path — node-pty's posix_spawnp may not find it on PATH
function findTmux(): string {
  const candidates = ['/opt/homebrew/bin/tmux', '/usr/local/bin/tmux', '/usr/bin/tmux'];
  for (const candidate of candidates) {
    try {
      execFileSync(candidate, ['-V'], { timeout: 2000 });
      return candidate;
    } catch { /* try next */ }
  }
  return 'tmux'; // Fallback to PATH lookup
}

const TMUX_BIN = findTmux();

function tmuxSessionExists(name: string): boolean {
  try {
    execFileSync(TMUX_BIN, ['has-session', '-t', name], { timeout: 5000 });
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
      ptyProcess = pty.spawn(TMUX_BIN, ['attach-session', '-t', tmuxSession], {
        name: 'xterm-256color',
        cols: 80,
        rows: 30,
        cwd: process.env.HOME || '/tmp',
        env: { ...process.env, TERM: 'xterm-256color' } as Record<string, string>,
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
