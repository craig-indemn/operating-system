import { useEffect, useRef, useCallback, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebglAddon } from '@xterm/addon-webgl';
import { WebLinksAddon } from '@xterm/addon-web-links';
import { ClipboardAddon } from '@xterm/addon-clipboard';
import type { IClipboardProvider, ClipboardSelectionType } from '@xterm/addon-clipboard';
import { getStoredToken, clearStoredToken } from '../utils/auth';

/**
 * Custom clipboard provider that buffers OSC 52 content.
 *
 * Problem: tmux sends OSC 52 with no selection type (empty string), but the
 * default BrowserClipboardProvider only writes for type 'c'. Also,
 * navigator.clipboard.writeText requires a user gesture, but OSC 52 arrives
 * via WebSocket — not a user gesture.
 *
 * Solution: buffer the latest clipboard content from OSC 52. When the user
 * presses Cmd/Ctrl+C (a real user gesture), write the buffer to clipboard.
 */
class BufferedClipboardProvider implements IClipboardProvider {
  public pendingText: string = '';

  readText(_selection: ClipboardSelectionType): string {
    return this.pendingText;
  }

  writeText(_selection: ClipboardSelectionType, text: string): void {
    // Accept ANY selection type (including empty string from tmux).
    // Don't write to navigator.clipboard here — no user gesture.
    // Just buffer it for the next Cmd+C.
    this.pendingText = text;
  }
}

export type ConnectionState = 'connected' | 'reconnecting' | 'disconnected';

interface UseTerminalOptions {
  sessionName: string;
  fontSize?: number;
}

interface UseTerminalReturn {
  containerRef: React.RefObject<HTMLDivElement | null>;
  fit: () => void;
  focus: () => void;
  connectionState: ConnectionState;
}

const MAX_BACKOFF = 10_000; // 10s cap (local Tailscale relay)

export function useTerminal({ sessionName, fontSize = 13 }: UseTerminalOptions): UseTerminalReturn {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const termRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(1000);
  const backoffTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const intentionalCloseRef = useRef(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');

  const fit = useCallback(() => {
    fitAddonRef.current?.fit();
  }, []);

  const focus = useCallback(() => {
    termRef.current?.focus();
  }, []);

  useEffect(() => {
    intentionalCloseRef.current = false;

    const container = containerRef.current;
    if (!container || termRef.current) return;

    // Create terminal once — never recreated on reconnect
    const term = new Terminal({
      cursorBlink: true,
      fontSize,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      letterSpacing: 0,
      scrollback: 0,
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#d4d4d4',
        selectionBackground: '#264f78',
        selectionForeground: '#ffffff',
      },
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.loadAddon(new WebLinksAddon());
    const clipboardProvider = new BufferedClipboardProvider();
    term.loadAddon(new ClipboardAddon(undefined, clipboardProvider));

    term.open(container);

    try {
      term.loadAddon(new WebglAddon());
    } catch {
      // WebGL unavailable — DOM renderer is fine
    }

    fitAddon.fit();
    termRef.current = term;
    fitAddonRef.current = fitAddon;

    // --- Clipboard: Cmd/Ctrl+C writes buffered tmux selection to clipboard ---
    // Flow: user selects in tmux → tmux sends OSC 52 → ClipboardAddon stores
    // in BufferedClipboardProvider → user presses Cmd+C (user gesture) → we
    // write the buffer to the system clipboard.
    container.addEventListener('keydown', (e: KeyboardEvent) => {
      const meta = e.metaKey || e.ctrlKey;
      if (meta && e.key === 'c' && clipboardProvider.pendingText) {
        e.preventDefault();
        e.stopPropagation();
        navigator.clipboard.writeText(clipboardProvider.pendingText).catch((err) => {
          console.error('Clipboard write failed:', err);
        });
      }
    });

    // --- Touch detection ---
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    // Context menu: suppress on desktop (prevents double-menu on right-click).
    // On touch devices, allow long-press so iOS/Android paste menu appears.
    if (!isTouchDevice) {
      container.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    // --- Touch scroll → tmux mouse wheel events ---
    // tmux with 'set -g mouse on' processes mouse wheel events for scrollback.
    // Desktop: mouse wheel → xterm.js mouse reporting → escape sequences → tmux.
    // Mobile: touch swipes don't generate wheel events. We intercept touch gestures
    // and synthesize SGR-encoded mouse wheel escape sequences (button 64=up, 65=down).
    if (isTouchDevice) {
      let lastTouchY: number | null = null;
      let touchOriginY: number | null = null;
      let scrollAccumulator = 0;
      let isScrollGesture = false;
      const SCROLL_DEAD_ZONE = 10;   // px before treating as scroll (not tap/long-press)
      const PX_PER_LINE = 20;        // px of touch movement per scroll line

      container.addEventListener('touchstart', (e: TouchEvent) => {
        if (e.touches.length === 1) {
          touchOriginY = e.touches[0]!.clientY;
          lastTouchY = touchOriginY;
          isScrollGesture = false;
          scrollAccumulator = 0;
        }
      }, { passive: true });

      container.addEventListener('touchmove', (e: TouchEvent) => {
        if (lastTouchY === null || touchOriginY === null || e.touches.length !== 1) return;

        const currentY = e.touches[0]!.clientY;

        // Enter scroll mode once finger moves past dead zone
        if (!isScrollGesture) {
          if (Math.abs(currentY - touchOriginY) > SCROLL_DEAD_ZONE) {
            isScrollGesture = true;
          } else {
            return; // Still in dead zone — could be tap or long-press
          }
        }

        e.preventDefault(); // Stop iOS page bounce/rubber-banding

        const deltaY = lastTouchY - currentY; // positive = finger up = scroll up (older content)
        lastTouchY = currentY;
        scrollAccumulator += deltaY;

        // Emit one mouse wheel event per PX_PER_LINE pixels of movement
        const ws = wsRef.current;
        if (ws?.readyState === WebSocket.OPEN) {
          while (Math.abs(scrollAccumulator) >= PX_PER_LINE) {
            // SGR mouse encoding: \x1b[<button;col;rowM
            const button = scrollAccumulator > 0 ? 64 : 65;
            ws.send(JSON.stringify({ type: 'input', data: `\x1b[<${button};1;1M` }));
            scrollAccumulator -= scrollAccumulator > 0 ? PX_PER_LINE : -PX_PER_LINE;
          }
        }
      }, { passive: false });

      container.addEventListener('touchend', () => {
        lastTouchY = null;
        touchOriginY = null;
        isScrollGesture = false;
        scrollAccumulator = 0;
      }, { passive: true });
    }

    // --- Mobile paste support ---
    // Intercept paste events when our terminal has focus. This catches:
    // - iOS long-press → Paste menu
    // - iOS 3-finger paste gesture
    // - Voice-to-text apps (Wispr Flow) that paste via clipboard
    // We send clipboard text directly to the WebSocket to bypass xterm.js
    // composition issues on iOS (which can drop all but the first character).
    let mobilePasteHandler: ((e: ClipboardEvent) => void) | null = null;
    if (isTouchDevice) {
      mobilePasteHandler = (e: ClipboardEvent) => {
        // Only handle if our terminal container (or a child like xterm's textarea) is focused
        if (!container.contains(document.activeElement)) return;
        const text = e.clipboardData?.getData('text/plain');
        if (!text) return;
        e.preventDefault(); // Prevent xterm.js from also handling (avoids double-paste)
        const ws = wsRef.current;
        if (ws?.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'input', data: text }));
        }
      };
      document.addEventListener('paste', mobilePasteHandler);
    }

    // --- Idempotent connect function ---
    function connect() {
      // Clear pending backoff
      if (backoffTimerRef.current) {
        clearTimeout(backoffTimerRef.current);
        backoffTimerRef.current = null;
      }
      if (pingTimerRef.current) {
        clearTimeout(pingTimerRef.current);
        pingTimerRef.current = null;
      }

      // Null out old ws onclose to prevent recursive reconnect
      const oldWs = wsRef.current;
      if (oldWs) {
        oldWs.onclose = null;
        oldWs.onerror = null;
        oldWs.onmessage = null;
        if (oldWs.readyState === WebSocket.OPEN || oldWs.readyState === WebSocket.CONNECTING) {
          oldWs.close();
        }
      }

      setConnectionState('reconnecting');

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/terminal/${encodeURIComponent(sessionName)}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        // Send auth message. Resize is deferred until the first server
        // message arrives — this guarantees the server's terminal handler
        // is registered before we send non-auth messages.
        const token = getStoredToken();
        if (token) {
          ws.send(JSON.stringify({ type: 'auth', token }));
        }
      };

      let connected = false;
      ws.onmessage = (event) => {
        // First server message = connection fully established
        if (!connected) {
          connected = true;
          setConnectionState('connected');
          backoffRef.current = 1000; // reset backoff on success
          // Send initial resize now that the terminal handler is listening
          ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
        }
        // Handle pong responses — cancel ping timeout when received
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'pong') {
            if (pingTimerRef.current) {
              clearTimeout(pingTimerRef.current);
              pingTimerRef.current = null;
            }
            return;
          }
        } catch {
          // Not JSON — it's terminal data
        }
        term.write(event.data);
      };

      ws.onclose = (event) => {
        // Auth failure — don't reconnect, force re-login
        if (event.code === 4401) {
          clearStoredToken();
          setConnectionState('disconnected');
          window.location.reload();
          return;
        }

        // Intentional close (cleanup) — don't reconnect
        if (intentionalCloseRef.current) {
          setConnectionState('disconnected');
          return;
        }

        // Normal close by server (code 1000, e.g. PTY exited) — don't reconnect
        if (event.code === 1000) {
          setConnectionState('disconnected');
          return;
        }

        // Unexpected disconnect — reconnect with backoff
        setConnectionState('reconnecting');
        const delay = backoffRef.current;
        backoffRef.current = Math.min(backoffRef.current * 2, MAX_BACKOFF);
        backoffTimerRef.current = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        // onclose will fire after onerror
      };
    }

    // User input -> WebSocket
    const inputDisposable = term.onData((data) => {
      const ws = wsRef.current;
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'input', data }));
      } else if (backoffTimerRef.current) {
        // Press any key to reconnect immediately during backoff
        clearTimeout(backoffTimerRef.current);
        backoffTimerRef.current = null;
        connect();
        // Keypress consumed — not forwarded (acceptable tradeoff)
      }
    });

    // Resize -> WebSocket
    const resizeDisposable = term.onResize(({ cols, rows }) => {
      const ws = wsRef.current;
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'resize', cols, rows }));
      }
    });

    // visibilitychange — critical for mobile tab resume
    function handleVisibilityChange() {
      if (document.visibilityState !== 'visible') return;
      const ws = wsRef.current;

      // Already reconnecting — skip
      if (backoffTimerRef.current) return;

      if (!ws || ws.readyState !== WebSocket.OPEN) {
        connect();
        return;
      }

      // WebSocket claims OPEN — verify with ping
      try {
        ws.send(JSON.stringify({ type: 'ping' }));
      } catch {
        connect();
        return;
      }
      pingTimerRef.current = setTimeout(() => {
        // No pong received in 3s — connection is dead
        if (wsRef.current === ws) {
          ws.close();
          connect();
        }
      }, 3000);
    }

    // online event — immediate reconnect when network restored
    function handleOnline() {
      const ws = wsRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        backoffRef.current = 1000; // reset backoff
        connect();
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('online', handleOnline);

    // Initial connect
    connect();

    // Cleanup
    return () => {
      intentionalCloseRef.current = true;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('online', handleOnline);
      if (mobilePasteHandler) {
        document.removeEventListener('paste', mobilePasteHandler);
      }
      if (backoffTimerRef.current) clearTimeout(backoffTimerRef.current);
      if (pingTimerRef.current) clearTimeout(pingTimerRef.current);
      inputDisposable.dispose();
      resizeDisposable.dispose();
      wsRef.current?.close();
      term.dispose();
      termRef.current = null;
      fitAddonRef.current = null;
      wsRef.current = null;
    };
  }, [sessionName, fontSize]);

  return { containerRef, fit, focus, connectionState };
}
