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
