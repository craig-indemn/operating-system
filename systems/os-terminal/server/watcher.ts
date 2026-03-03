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
    }).catch(err => {
      console.error('Failed to send initial sessions:', err);
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

const MAX_WATCHER_RETRIES = 10;

async function startWatching(dir: string, clients: Set<WebSocket>, retryCount = 0): Promise<void> {
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
        broadcastSessions(clients).catch(err => {
          console.error('Failed to broadcast sessions:', err);
        });
      }, 150); // 150ms trailing edge — atomic writes generate 4-5 events in ~50ms
    }
  } catch (err) {
    console.error('State watcher error:', err);
    if (retryCount >= MAX_WATCHER_RETRIES) {
      console.error(`State watcher gave up after ${MAX_WATCHER_RETRIES} retries`);
      return;
    }
    // Exponential backoff: 5s, 10s, 20s, 40s, ...
    const delay = 5000 * Math.pow(2, retryCount);
    setTimeout(() => startWatching(dir, clients, retryCount + 1), delay);
  }
}
