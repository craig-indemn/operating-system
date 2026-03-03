import type { WebSocketServer, WebSocket } from 'ws';

const PING_INTERVAL = 30_000; // 30s — keeps connections alive through cellular NATs

/**
 * Starts ping/pong heartbeat on a WebSocketServer using native ws ping/pong
 * frames (RFC 6455 opcodes). Browsers auto-respond to ping with pong — no
 * client code needed. Clients that don't respond are terminated on the next
 * ping cycle (~30-60s effective timeout).
 */
export function startHeartbeat(wss: WebSocketServer): void {
  const interval = setInterval(() => {
    for (const ws of wss.clients) {
      if ((ws as any).__isAlive === false) {
        ws.terminate();
        continue;
      }
      (ws as any).__isAlive = false;
      ws.ping();
    }
  }, PING_INTERVAL);

  wss.on('connection', (ws: WebSocket) => {
    (ws as any).__isAlive = true;
    ws.on('pong', () => {
      (ws as any).__isAlive = true;
    });
  });

  wss.on('close', () => {
    clearInterval(interval);
  });
}
