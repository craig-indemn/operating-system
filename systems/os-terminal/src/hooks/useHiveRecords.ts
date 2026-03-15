import { useState, useEffect, useRef, useCallback } from 'react';
import { getStoredToken, clearStoredToken } from '../utils/auth';
import type { HiveRecord } from '../types/hive';

export function useHiveRecords() {
  const [records, setRecords] = useState<HiveRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();
  const intentionalCloseRef = useRef(false);

  useEffect(() => {
    intentionalCloseRef.current = false;

    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/hive`);
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
          if (msg.type === 'hive_update') {
            setRecords(msg.data.records as HiveRecord[]);
            setLoading(false);
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

  // Force a re-fetch by sending a refresh message to the server
  const refresh = useCallback(() => {
    const ws = wsRef.current;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'refresh' }));
    }
  }, []);

  return { records, loading, refresh };
}
