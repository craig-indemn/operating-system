import { useState, useEffect, useRef } from 'react';
import { getStoredToken, clearStoredToken } from '../utils/auth';

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
  const intentionalCloseRef = useRef(false);

  useEffect(() => {
    intentionalCloseRef.current = false;

    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/state`);
      wsRef.current = ws;

      ws.onopen = () => {
        // Send auth message first if token exists
        const token = getStoredToken();
        if (token) {
          ws.send(JSON.stringify({ type: 'auth', token }));
        }
      };

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

      ws.onclose = (event) => {
        if (event.code === 4401) {
          clearStoredToken();
          window.location.reload();
          return;
        }
        // Don't reconnect if cleanup already ran
        if (intentionalCloseRef.current) return;
        // Reconnect after 3 seconds
        reconnectTimer.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        // Browser fires onclose after onerror — no need to call ws.close()
      };
    }

    connect();

    return () => {
      intentionalCloseRef.current = true;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []);

  return sessions;
}
