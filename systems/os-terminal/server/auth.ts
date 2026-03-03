import type { Request, Response, NextFunction } from 'express';
import type { WebSocket } from 'ws';
import { timingSafeEqual, randomBytes } from 'node:crypto';

export function tokensMatch(provided: string, expected: string): boolean {
  const a = Buffer.from(provided);
  const b = Buffer.from(expected);
  if (a.length !== b.length) {
    // Compare against expected-length random bytes so timing is constant
    // regardless of provided token length (prevents length inference)
    timingSafeEqual(b, randomBytes(b.length));
    return false;
  }
  return timingSafeEqual(a, b);
}

/**
 * Express middleware: validates Authorization: Bearer <token> on protected routes.
 * When OS_TERMINAL_TOKEN is not set, auth is disabled (passes through).
 */
export function authMiddleware(req: Request, res: Response, next: NextFunction): void {
  const expected = process.env.OS_TERMINAL_TOKEN;
  if (!expected) {
    next();
    return;
  }

  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  const token = authHeader.slice(7);
  if (!tokensMatch(token, expected)) {
    res.status(403).json({ error: 'Invalid token' });
    return;
  }

  next();
}

/**
 * WebSocket auth gate — waits for {"type":"auth","token":"..."} as first message.
 * Returns true if authenticated, false if rejected (ws already closed with 4401).
 * When OS_TERMINAL_TOKEN is not set, resolves immediately (no auth needed).
 */
export function authenticateWs(ws: WebSocket): Promise<boolean> {
  const expected = process.env.OS_TERMINAL_TOKEN;
  if (!expected) return Promise.resolve(true);

  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      cleanup();
      ws.close(4401, 'Auth timeout');
      resolve(false);
    }, 5000);

    const onMessage = (raw: Buffer | string) => {
      cleanup();
      try {
        const msg = JSON.parse(raw.toString());
        if (msg.type === 'auth' && typeof msg.token === 'string' && tokensMatch(msg.token, expected)) {
          resolve(true);
          return;
        }
      } catch {
        // invalid JSON
      }
      ws.close(4401, 'Auth failed');
      resolve(false);
    };

    const onClose = () => {
      cleanup();
      resolve(false);
    };

    function cleanup() {
      clearTimeout(timeout);
      ws.removeListener('message', onMessage);
      ws.removeListener('close', onClose);
    }

    ws.on('message', onMessage);
    ws.on('close', onClose);
  });
}
