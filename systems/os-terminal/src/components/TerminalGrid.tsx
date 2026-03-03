import { useRef, useMemo, useCallback, useEffect, useState } from 'react';
import { TerminalPane, TerminalPaneHandle } from './TerminalPane';
import { TabBar } from './TabBar';
import type { SessionInfo } from '../hooks/useSessions';

const MIN_COL_WIDTH = 600; // px — minimum width per column
const GAP = 4; // px between panes
const STORAGE_KEY = 'os-terminal-order';

interface TerminalGridProps {
  sessions: SessionInfo[];
  maximized: string | null;
  focused: string | null;
  minimized: Set<string>;
  isMobile: boolean;
  onMaximize: (id: string) => void;
  onMinimize: (id: string) => void;
  onRestore: () => void;
  onFocus: (id: string) => void;
  onCloseSession: (id: string) => void;
}

function loadOrder(): string[] {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

export function TerminalGrid({
  sessions, maximized, focused, minimized, isMobile,
  onMaximize, onMinimize, onRestore, onFocus, onCloseSession,
}: TerminalGridProps) {
  const paneRefs = useRef<Record<string, TerminalPaneHandle | null>>({});
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [dragSource, setDragSource] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<string | null>(null);
  const [numCols, setNumCols] = useState(3);

  // Persisted session order (array of session_ids)
  const [order, setOrder] = useState<string[]>(loadOrder);

  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  const visibleSessions = useMemo(
    () => activeSessions.filter(s => !minimized.has(s.session_id)),
    [activeSessions, minimized],
  );

  // Apply saved order, appending any new sessions at the end
  const orderedSessions = useMemo(() => {
    const ids = new Set(visibleSessions.map(s => s.session_id));
    const ordered: SessionInfo[] = [];
    for (const id of order) {
      const session = visibleSessions.find(s => s.session_id === id);
      if (session) ordered.push(session);
    }
    for (const s of visibleSessions) {
      if (!order.includes(s.session_id)) ordered.push(s);
    }
    return ordered.filter(s => ids.has(s.session_id));
  }, [visibleSessions, order]);

  // Save order to localStorage
  const updateOrder = useCallback((newOrder: string[]) => {
    setOrder(newOrder);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newOrder));
  }, []);

  // Drag-to-swap handlers
  const handleDragStart = useCallback((id: string) => {
    setDragSource(id);
  }, []);

  const handleDragEnter = useCallback((id: string) => {
    setDragOver(id);
  }, []);

  const handleDragEnd = useCallback(() => {
    if (dragSource && dragOver && dragSource !== dragOver) {
      const ids = orderedSessions.map(s => s.session_id);
      const srcIdx = ids.indexOf(dragSource);
      const dstIdx = ids.indexOf(dragOver);
      if (srcIdx >= 0 && dstIdx >= 0) {
        const newIds = [...ids];
        [newIds[srcIdx], newIds[dstIdx]] = [newIds[dstIdx]!, newIds[srcIdx]!];
        updateOrder(newIds);
      }
    }
    setDragSource(null);
    setDragOver(null);
  }, [dragSource, dragOver, orderedSessions, updateOrder]);

  const refitAll = useCallback(() => {
    setTimeout(() => {
      Object.values(paneRefs.current).forEach(ref => ref?.fit());
    }, 50);
  }, []);

  // Refit on window resize
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    const onResize = () => {
      clearTimeout(timer);
      timer = setTimeout(refitAll, 150);
    };
    window.addEventListener('resize', onResize);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', onResize);
    };
  }, [refitAll]);

  // Refit when session count changes
  useEffect(() => {
    refitAll();
  }, [orderedSessions.length, refitAll]);

  // If the maximized session disappears, restore (via useEffect to avoid state setter during render)
  const maximizedSession = maximized ? activeSessions.find(s => s.session_id === maximized) : null;
  useEffect(() => {
    if (maximized && !maximizedSession) {
      onRestore();
    }
  }, [maximized, maximizedSession, onRestore]);

  // Prune stale paneRefs entries when sessions change
  useEffect(() => {
    const activeIds = new Set(activeSessions.map(s => s.session_id));
    for (const id of Object.keys(paneRefs.current)) {
      if (!activeIds.has(id)) {
        delete paneRefs.current[id];
      }
    }
  }, [activeSessions]);

  // Track column count via ResizeObserver for row spanning
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new ResizeObserver(entries => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        const cols = Math.max(1, Math.floor((width + GAP) / (MIN_COL_WIDTH + GAP)));
        setNumCols(cols);
      }
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  // Auto-focus initialization for mobile: sync focused state when null
  useEffect(() => {
    if (isMobile && !focused && activeSessions.length > 0) {
      onFocus(activeSessions[0]!.session_id);
    }
  }, [isMobile, focused, activeSessions, onFocus]);

  // Mobile single-pane mode
  if (isMobile) {
    const activeSession = activeSessions.find(s => s.session_id === focused)
      ?? activeSessions[0]
      ?? null;

    if (!activeSession) {
      return (
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#858585', fontSize: 14 }}>
          No active sessions
        </div>
      );
    }

    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, padding: GAP, minHeight: 0 }}>
          <TerminalPane
            key={activeSession.session_id}
            ref={(el) => { paneRefs.current[activeSession.session_id] = el; }}
            sessionName={activeSession.name}
            sessionId={activeSession.session_id}
            status={activeSession.status}
            contextPct={activeSession.context_remaining_pct}
            isMaximized={false}
            isFocused={true}
            onMaximize={() => {}}
            onMinimize={() => {}}
            onRestore={() => {}}
            onFocus={() => onFocus(activeSession.session_id)}
            onClose={() => onCloseSession(activeSession.session_id)}
          />
        </div>
        <TabBar
          sessions={activeSessions}
          activeSessionId={activeSession.session_id}
          onSelect={onFocus}
        />
      </div>
    );
  }

  // Maximized view
  if (maximized) {
    if (!maximizedSession) {
      return null; // useEffect above will call onRestore
    }
    const session = maximizedSession;
    return (
      <div style={{ height: '100%', padding: GAP }}>
        <TerminalPane
          key={session.session_id}
          ref={(el) => { paneRefs.current[session.session_id] = el; }}
          sessionName={session.name}
          sessionId={session.session_id}
          status={session.status}
          contextPct={session.context_remaining_pct}
          isMaximized={true}
          isFocused={true}
          onMaximize={() => {}}
          onMinimize={() => { onRestore(); onMinimize(session.session_id); }}
          onRestore={onRestore}
          onFocus={() => onFocus(session.session_id)}
          onClose={() => { onRestore(); onCloseSession(session.session_id); }}
        />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="terminal-auto-grid"
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(auto-fit, minmax(${MIN_COL_WIDTH}px, 1fr))`,
        gridAutoRows: '1fr',
        gap: `${GAP}px`,
        height: '100%',
        padding: `${GAP}px`,
      }}
    >
      {orderedSessions.map((session, index) => {
        // Calculate row spanning: items in columns without last-row entries fill remaining rows
        const totalRows = Math.ceil(orderedSessions.length / numCols);
        const lastRowCount = orderedSessions.length % numCols || numCols;
        const col = index % numCols;
        const row = Math.floor(index / numCols);
        const itemsInCol = Math.floor(orderedSessions.length / numCols) + (col < lastRowCount ? 1 : 0);
        const isLastInCol = row === itemsInCol - 1;
        const span = isLastInCol && totalRows > 1 ? totalRows - row : 1;

        return (
        <div
          key={session.session_id}
          style={{
            minHeight: 0,
            gridRow: span > 1 ? `span ${span}` : undefined,
            opacity: dragSource === session.session_id ? 0.5 : 1,
            outline: dragOver === session.session_id && dragSource !== session.session_id
              ? '2px solid #007acc' : 'none',
            borderRadius: 4,
          }}
          draggable
          onDragStart={() => handleDragStart(session.session_id)}
          onDragEnter={() => handleDragEnter(session.session_id)}
          onDragOver={(e) => e.preventDefault()}
          onDragEnd={handleDragEnd}
        >
          <TerminalPane
            ref={(el) => { paneRefs.current[session.session_id] = el; }}
            sessionName={session.name}
            sessionId={session.session_id}
            status={session.status}
            contextPct={session.context_remaining_pct}
            isMaximized={false}
            isFocused={focused === session.session_id}
            onMaximize={() => onMaximize(session.session_id)}
            onMinimize={() => onMinimize(session.session_id)}
            onRestore={() => {}}
            onFocus={() => { onFocus(session.session_id); paneRefs.current[session.session_id]?.focus(); }}
            onClose={() => onCloseSession(session.session_id)}
          />
        </div>
        );
      })}
    </div>
  );
}
