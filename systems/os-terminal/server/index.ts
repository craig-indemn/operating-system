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
