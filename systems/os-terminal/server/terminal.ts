import type { WebSocketServer, WebSocket } from 'ws';
import type { IncomingMessage } from 'http';
import { execFile } from 'child_process';
import { promisify } from 'util';
import * as pty from 'node-pty';
import { TMUX_BIN, TMUX_PREFIX, isValidSessionName } from './tmux.js';

const exec = promisify(execFile);

interface TerminalMessage {
  type: 'input' | 'resize' | 'ping';
  data?: string;
  cols?: number;
  rows?: number;
}

async function tmuxSessionExists(name: string): Promise<boolean> {
  try {
    await exec(TMUX_BIN, ['has-session', '-t', name], { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}

const BACKPRESSURE_THRESHOLD = 128 * 1024; // 128KB

/** Filter undefined values from process.env for node-pty */
function cleanEnv(extra: Record<string, string>): Record<string, string> {
  const env: Record<string, string> = {};
  for (const [k, v] of Object.entries(process.env)) {
    if (v !== undefined) env[k] = v;
  }
  return { ...env, ...extra };
}

export function initTerminalHandler(wss: WebSocketServer): void {
  wss.on('connection', async (ws: WebSocket, request: IncomingMessage) => {
    const url = new URL(request.url || '', `http://${request.headers.host}`);
    const sessionName = decodeURIComponent(url.pathname.replace('/ws/terminal/', ''));

    // Validate session name before using it in any command
    if (!isValidSessionName(sessionName)) {
      ws.close(1008, 'Invalid session name');
      return;
    }

    const tmuxSession = `${TMUX_PREFIX}${sessionName}`;

    console.log(`Terminal connected: ${tmuxSession}`);

    // Validate tmux session exists before spawning PTY
    if (!(await tmuxSessionExists(tmuxSession))) {
      console.error(`tmux session ${tmuxSession} does not exist`);
      ws.close(1011, 'Session not found');
      return;
    }

    let ptyProcess: pty.IPty;
    try {
      ptyProcess = pty.spawn(TMUX_BIN, ['attach-session', '-t', tmuxSession], {
        name: 'xterm-256color',
        cols: 80,
        rows: 30,
        cwd: process.env.HOME || '/tmp',
        env: cleanEnv({ TERM: 'xterm-256color' }),
      });
    } catch (err) {
      console.error(`Failed to attach to tmux session ${tmuxSession}:`, err);
      ws.close(1011, 'Failed to attach to session');
      return;
    }

    // Track PTY lifecycle to prevent double-kill
    let ptyExited = false;
    let backpressurePaused = false;

    // PTY output -> WebSocket (with backpressure to prevent OOM on fast output)
    ptyProcess.onData((data: string) => {
      if (ws.readyState === ws.OPEN) {
        if (!backpressurePaused && ws.bufferedAmount > BACKPRESSURE_THRESHOLD) {
          backpressurePaused = true;
          ptyProcess.pause();
          const check = setInterval(() => {
            if (ws.readyState !== ws.OPEN || ws.bufferedAmount <= BACKPRESSURE_THRESHOLD) {
              clearInterval(check);
              backpressurePaused = false;
              if (!ptyExited) ptyProcess.resume();
            }
          }, 50);
        }
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
    // Note: auth is handled in the upgrade handler (server/index.ts), not here.
    // tmux attach-session must NOT use -d flag — concurrent attach during reconnect
    // is benign, tmux handles it natively. -d would create a detach race.
    ws.on('message', (raw: Buffer) => {
      try {
        const msg: TerminalMessage = JSON.parse(raw.toString());
        // Application-level ping/pong — used by the client's visibilitychange handler
        // to verify the connection is alive after tab resume. This is separate from
        // the native RFC 6455 ping/pong in heartbeat.ts (which keeps NAT alive).
        if (msg.type === 'ping') {
          if (ws.readyState === ws.OPEN) {
            ws.send(JSON.stringify({ type: 'pong' }));
          }
          return;
        }
        if (ptyExited) return;
        if (msg.type === 'input' && msg.data) {
          ptyProcess.write(msg.data);
        } else if (msg.type === 'resize' && msg.cols && msg.cols > 0 && msg.rows && msg.rows > 0) {
          ptyProcess.resize(msg.cols, msg.rows);
        }
      } catch {
        // If not valid JSON, treat as raw input
        if (!ptyExited) ptyProcess.write(raw.toString());
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
