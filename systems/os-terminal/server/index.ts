import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { WebSocketServer } from 'ws';
import sessionsRouter from './routes/sessions.js';
import hiveRouter from './routes/hive.js';
import { initTerminalHandler } from './terminal.js';
import { initStateHandler } from './watcher.js';
import { initHiveHandler } from './hive-watcher.js';
import { authMiddleware, authenticateWs, tokensMatch } from './auth.js';
import { startHeartbeat } from './heartbeat.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const server = createServer(app);

app.use(express.json());

// --- Auth endpoints (public) ---
app.get('/api/auth/status', (_req, res) => {
  res.json({ authRequired: !!process.env.OS_TERMINAL_TOKEN });
});

// Rate-limited token validation (sliding window, evicted every 5 min)
const rateLimitMap = new Map<string, number[]>();
setInterval(() => {
  const now = Date.now();
  for (const [key, timestamps] of rateLimitMap) {
    if (timestamps.every(t => now - t >= 60_000)) {
      rateLimitMap.delete(key);
    }
  }
}, 300_000).unref();
app.post('/api/auth/validate', (req, res) => {
  const key = req.ip || 'unknown';
  const now = Date.now();
  const window = rateLimitMap.get(key)?.filter(t => now - t < 60_000) || [];
  if (window.length >= 5) {
    res.status(429).json({ error: 'Too many attempts. Try again in a minute.' });
    return;
  }
  window.push(now);
  rateLimitMap.set(key, window);

  const { token } = req.body;
  const expected = process.env.OS_TERMINAL_TOKEN;
  if (!expected) {
    res.json({ valid: true });
    return;
  }
  if (!token || typeof token !== 'string') {
    res.json({ valid: false });
    return;
  }

  res.json({ valid: tokensMatch(token, expected) });
});

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok' });
});

// Auth middleware for protected API routes
app.use('/api/sessions', authMiddleware, sessionsRouter);
app.use('/api/hive', authMiddleware, hiveRouter);

// Error-handling middleware — catch unhandled async errors from routes
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// --- Static file serving (production build) ---
const distPath = join(__dirname, '..', 'dist');
const indexPath = join(distPath, 'index.html');

if (existsSync(indexPath)) {
  // Hashed assets (in /assets/) get long-lived cache. index.html must NOT be cached
  // immutably — it contains references to hashed asset filenames that change on deploy.
  app.use(express.static(distPath, {
    maxAge: '1y',
    immutable: true,
    index: false, // Don't serve index.html via static — SPA catch-all handles it with no-cache
  }));
  // 404 for unknown API routes (before SPA catch-all)
  app.use('/api', (_req, res) => {
    res.status(404).json({ error: 'Not found' });
  });
  // SPA catch-all — serve index.html for client-side routing
  app.get('*', (_req, res) => {
    res.sendFile(indexPath);
  });
}

// --- WebSocket setup ---
// Two WebSocketServer instances, both noServer: true.
// A single upgrade handler dispatches based on URL path.
const terminalWss = new WebSocketServer({ noServer: true, maxPayload: 64 * 1024 });
const stateWss = new WebSocketServer({ noServer: true, maxPayload: 64 * 1024 });
const hiveWss = new WebSocketServer({ noServer: true, maxPayload: 256 * 1024 });

initTerminalHandler(terminalWss);
initStateHandler(stateWss);
initHiveHandler(hiveWss);
startHeartbeat(terminalWss);
startHeartbeat(stateWss);
startHeartbeat(hiveWss);

server.on('upgrade', (request, socket, head) => {
  const url = new URL(request.url || '', `http://${request.headers.host}`);

  if (url.pathname.startsWith('/ws/terminal/')) {
    terminalWss.handleUpgrade(request, socket, head, async (ws) => {
      const authed = await authenticateWs(ws);
      if (!authed) return;
      terminalWss.emit('connection', ws, request);
    });
  } else if (url.pathname === '/ws/state') {
    stateWss.handleUpgrade(request, socket, head, async (ws) => {
      const authed = await authenticateWs(ws);
      if (!authed) return;
      stateWss.emit('connection', ws, request);
    });
  } else if (url.pathname === '/ws/hive') {
    hiveWss.handleUpgrade(request, socket, head, async (ws) => {
      const authed = await authenticateWs(ws);
      if (!authed) return;
      hiveWss.emit('connection', ws, request);
    });
  } else {
    socket.destroy();
  }
});

const PORT = parseInt(process.env.PORT || '3101', 10);
server.listen(PORT, () => {
  console.log(`Hive server running on port ${PORT}`);
});

// Graceful shutdown — terminate all clients, force exit after 5s
function shutdown() {
  console.log('Shutting down...');
  for (const ws of terminalWss.clients) ws.terminate();
  for (const ws of stateWss.clients) ws.terminate();
  for (const ws of hiveWss.clients) ws.terminate();
  terminalWss.close();
  stateWss.close();
  hiveWss.close();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
  setTimeout(() => {
    console.error('Forced exit after timeout');
    process.exit(1);
  }, 5000).unref();
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

export { server };
