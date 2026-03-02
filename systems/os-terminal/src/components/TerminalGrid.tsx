import { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import { Responsive, WidthProvider, Layout, Layouts } from 'react-grid-layout';
import { TerminalPane, TerminalPaneHandle } from './TerminalPane';
import type { SessionInfo } from '../hooks/useSessions';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGrid = WidthProvider(Responsive);
const LAYOUT_STORAGE_KEY = 'os-terminal-layouts';

interface TerminalGridProps {
  sessions: SessionInfo[];
  maximized: string | null;
  focused: string | null;
  minimized: Set<string>;
  onMaximize: (id: string) => void;
  onMinimize: (id: string) => void;
  onRestore: () => void;
  onFocus: (id: string) => void;
}

function loadSavedLayouts(): Layouts | null {
  try {
    const saved = localStorage.getItem(LAYOUT_STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

function generateDefaultLayouts(sessions: SessionInfo[]): Layouts {
  const cols = 12;
  const sessionsPerRow = Math.min(sessions.length, 3) || 1;
  const colWidth = Math.floor(cols / sessionsPerRow);

  const lg: Layout[] = sessions.map((s, i) => ({
    i: s.session_id,
    x: (i % sessionsPerRow) * colWidth,
    y: Math.floor(i / sessionsPerRow) * 4,
    w: colWidth,
    h: 4,
    minW: 2,
    minH: 2,
  }));

  return { lg, md: lg, sm: lg.map(l => ({ ...l, x: 0, w: 12 })) };
}

export function TerminalGrid({
  sessions, maximized, focused, minimized,
  onMaximize, onMinimize, onRestore, onFocus,
}: TerminalGridProps) {
  const paneRefs = useRef<Record<string, TerminalPaneHandle | null>>({});

  // Filter to active sessions (not ended/ended_dirty)
  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  // Build layouts: use saved if available, else generate defaults
  const [layouts, setLayouts] = useState<Layouts>(() => {
    return loadSavedLayouts() || generateDefaultLayouts(activeSessions);
  });

  // When new sessions appear that aren't in the layout, add them.
  // Uses functional updater to read current layout without depending on it,
  // avoiding a render loop from layouts.lg in the dependency array.
  useEffect(() => {
    setLayouts(prev => {
      const currentIds = new Set(prev.lg?.map(l => l.i) || []);
      const newSessions = activeSessions.filter(s => !currentIds.has(s.session_id));
      if (newSessions.length === 0) return prev; // no change, no re-render

      const maxY = Math.max(0, ...(prev.lg || []).map(l => l.y + l.h));
      const newItems: Layout[] = newSessions.map((s, i) => ({
        i: s.session_id,
        x: (i % 3) * 4,
        y: maxY,
        w: 4,
        h: 4,
        minW: 2,
        minH: 2,
      }));
      const lg = [...(prev.lg || []), ...newItems];
      return { lg, md: lg, sm: lg.map(l => ({ ...l, x: 0, w: 12 })) };
    });
  }, [activeSessions]); // No layouts.lg dependency — functional updater reads it

  // Debounced localStorage persistence — avoid writing on every drag frame
  const saveTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const handleLayoutChange = useCallback((_current: Layout[], allLayouts: Layouts) => {
    setLayouts(allLayouts);
    // Debounce localStorage writes — onLayoutChange fires on every drag frame
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(allLayouts));
    }, 300);
    // Refit all terminals after layout change
    setTimeout(() => {
      Object.values(paneRefs.current).forEach(ref => ref?.fit());
    }, 50);
  }, []);

  const handleResizeStop = useCallback(() => {
    // Refit all terminals after any resize
    setTimeout(() => {
      Object.values(paneRefs.current).forEach(ref => ref?.fit());
    }, 50);
  }, []);

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
          status={session.status}
          contextPct={session.context_remaining_pct}
          isMaximized={true}
          isFocused={true}
          onMaximize={() => {}}
          onMinimize={() => { onRestore(); onMinimize(session.session_id); }}
          onRestore={onRestore}
          onFocus={() => onFocus(session.session_id)}
        />
      </div>
    );
  }

  const visibleSessions = activeSessions.filter(s => !minimized.has(s.session_id));

  return (
    <ResponsiveGrid
      className="terminal-grid"
      layouts={layouts}
      breakpoints={{ lg: 1200, md: 996, sm: 768 }}
      cols={{ lg: 12, md: 12, sm: 12 }}
      rowHeight={80}
      draggableHandle=".terminal-header"
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
            status={session.status}
            contextPct={session.context_remaining_pct}
            isMaximized={false}
            isFocused={focused === session.session_id}
            onMaximize={() => onMaximize(session.session_id)}
            onMinimize={() => onMinimize(session.session_id)}
            onRestore={() => {}}
            onFocus={() => { onFocus(session.session_id); paneRefs.current[session.session_id]?.focus(); }}
          />
        </div>
      ))}
    </ResponsiveGrid>
  );
}
