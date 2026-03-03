import { useRef, useMemo, useCallback, useEffect, useState } from 'react';
import { TerminalPane, TerminalPaneHandle } from './TerminalPane';
import type { SessionInfo } from '../hooks/useSessions';

const MIN_COL_WIDTH = 400; // px — minimum width per column
const GAP = 4; // px between panes
const STORAGE_KEY = 'os-terminal-order';

interface TerminalGridProps {
  sessions: SessionInfo[];
  maximized: string | null;
  focused: string | null;
  minimized: Set<string>;
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
  sessions, maximized, focused, minimized,
  onMaximize, onMinimize, onRestore, onFocus, onCloseSession,
}: TerminalGridProps) {
  const paneRefs = useRef<Record<string, TerminalPaneHandle | null>>({});
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [dragSource, setDragSource] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<string | null>(null);

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

  // Maximized view
  if (maximized) {
    const session = activeSessions.find(s => s.session_id === maximized);
    if (!session) {
      onRestore();
      return null;
    }
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

  const count = orderedSessions.length;

  return (
    <div
      ref={containerRef}
      className="terminal-auto-grid"
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(auto-fill, minmax(${MIN_COL_WIDTH}px, 1fr))`,
        gridAutoRows: count <= getColCount() ? '1fr' : '1fr',
        gap: `${GAP}px`,
        height: '100%',
        padding: `${GAP}px`,
      }}
    >
      {orderedSessions.map(session => (
        <div
          key={session.session_id}
          style={{
            minHeight: 0,
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
      ))}
    </div>
  );
}

/** Helper to estimate column count (used for row height logic) */
function getColCount(): number {
  if (typeof window === 'undefined') return 3;
  return Math.max(1, Math.floor(window.innerWidth / MIN_COL_WIDTH));
}
