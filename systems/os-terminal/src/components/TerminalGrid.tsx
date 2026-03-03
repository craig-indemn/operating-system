import { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import { Responsive, WidthProvider, Layout, Layouts } from 'react-grid-layout';
import { TerminalPane, TerminalPaneHandle } from './TerminalPane';
import type { SessionInfo } from '../hooks/useSessions';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGrid = WidthProvider(Responsive);
const LAYOUT_STORAGE_KEY = 'os-terminal-layouts';
const MIN_W = 3;
const MIN_H = 3;
const DEFAULT_H = 4;

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

function loadSavedLayouts(): Layouts | null {
  try {
    const saved = localStorage.getItem(LAYOUT_STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

function computeDefaultWidth(totalSessions: number): number {
  const sessionsPerRow = Math.min(totalSessions, 3) || 1;
  return Math.floor(12 / sessionsPerRow);
}

export function TerminalGrid({
  sessions, maximized, focused, minimized,
  onMaximize, onMinimize, onRestore, onFocus, onCloseSession,
}: TerminalGridProps) {
  const paneRefs = useRef<Record<string, TerminalPaneHandle | null>>({});

  // Filter to active sessions (not ended/ended_dirty)
  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  // Base layouts from localStorage (user's saved arrangement)
  const [savedLayouts, setSavedLayouts] = useState<Layouts>(() => {
    return loadSavedLayouts() || { lg: [], md: [], sm: [] };
  });

  const visibleSessions = useMemo(
    () => activeSessions.filter(s => !minimized.has(s.session_id)),
    [activeSessions, minimized],
  );

  // Ensure all visible sessions have layout entries BEFORE render.
  // This runs synchronously so react-grid-layout never sees children
  // without matching layout items (which would create w:1 h:1 defaults).
  const effectiveLayouts = useMemo(() => {
    const lg = savedLayouts.lg || [];
    const layoutMap = new Map(lg.map(l => [l.i, l]));

    // Check which visible sessions need layout entries
    const missing = visibleSessions.filter(s => {
      const entry = layoutMap.get(s.session_id);
      // Missing or has degenerate size (auto-generated default)
      return !entry || entry.w < MIN_W || entry.h < MIN_H;
    });

    if (missing.length === 0) {
      // All visible sessions have good layout entries
      return savedLayouts;
    }

    // Compute default width based on total visible count
    const defaultW = computeDefaultWidth(visibleSessions.length);
    const maxY = lg.length > 0 ? Math.max(...lg.map(l => l.y + l.h)) : 0;

    const newLg = [...lg];
    missing.forEach((s, i) => {
      const entry: Layout = {
        i: s.session_id,
        x: (i % 3) * defaultW,
        y: maxY + Math.floor(i / 3) * DEFAULT_H,
        w: defaultW,
        h: DEFAULT_H,
        minW: MIN_W,
        minH: MIN_H,
      };
      // Replace degenerate entry or add new one
      const existingIdx = newLg.findIndex(l => l.i === s.session_id);
      if (existingIdx >= 0) {
        newLg[existingIdx] = entry;
      } else {
        newLg.push(entry);
      }
    });

    return {
      lg: newLg,
      md: newLg,
      sm: newLg.map(l => ({ ...l, x: 0, w: 12 })),
    };
  }, [savedLayouts, visibleSessions]);

  // Debounced localStorage persistence — avoid writing on every drag frame
  const saveTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const handleLayoutChange = useCallback((_current: Layout[], allLayouts: Layouts) => {
    // Enforce minimum sizes — reject react-grid-layout auto-generated defaults
    const sanitized: Layouts = {};
    for (const [bp, items] of Object.entries(allLayouts)) {
      sanitized[bp] = (items as Layout[]).map(l => ({
        ...l,
        w: Math.max(l.w, MIN_W),
        h: Math.max(l.h, MIN_H),
        minW: MIN_W,
        minH: MIN_H,
      }));
    }
    setSavedLayouts(sanitized);
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(sanitized));
    }, 300);
    // NOTE: Do NOT refit terminals here — this fires on every drag/resize frame
    // and causes text duplication. Refit only on drag/resize stop events.
  }, []);

  const refitAll = useCallback(() => {
    setTimeout(() => {
      Object.values(paneRefs.current).forEach(ref => ref?.fit());
    }, 50);
  }, []);

  const handleDragStop = useCallback(() => refitAll(), [refitAll]);
  const handleResizeStop = useCallback(() => refitAll(), [refitAll]);

  // Refit all terminals when browser window resizes.
  // WidthProvider updates the grid layout, but xterm.js canvases need
  // an explicit refit to match the new container dimensions.
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

  // Maximized view: single pane fills the viewport
  if (maximized) {
    const session = activeSessions.find(s => s.session_id === maximized);
    if (!session) {
      onRestore();
      return null;
    }
    return (
      <div style={{ height: '100%', padding: 4 }}>
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
    <ResponsiveGrid
      className="terminal-grid"
      layouts={effectiveLayouts}
      breakpoints={{ lg: 1200, md: 996, sm: 768 }}
      cols={{ lg: 12, md: 12, sm: 12 }}
      rowHeight={80}
      draggableHandle=".terminal-header"
      useCSSTransforms={false}
      onDragStop={handleDragStop}
      onResizeStop={handleResizeStop}
      onLayoutChange={handleLayoutChange}
      compactType="vertical"
      margin={[4, 4] as [number, number]}
    >
      {visibleSessions.map(session => (
        <div key={session.session_id}>
          <TerminalPane
            key={session.session_id}
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
    </ResponsiveGrid>
  );
}
