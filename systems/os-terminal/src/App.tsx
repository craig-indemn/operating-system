import { useState, useMemo, useCallback } from 'react';
import { useSessions } from './hooks/useSessions';
import { TerminalGrid } from './components/TerminalGrid';
import { SessionPanel } from './components/SessionPanel';

export default function App() {
  const sessions = useSessions();
  const [panelOpen, setPanelOpen] = useState(true);
  const [maximized, setMaximized] = useState<string | null>(null);
  const [focused, setFocused] = useState<string | null>(null);
  const [minimized, setMinimized] = useState<Set<string>>(new Set());

  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  const handleMaximize = useCallback((id: string) => setMaximized(id), []);
  const handleMinimize = useCallback((id: string) => {
    setMinimized(prev => new Set(prev).add(id));
  }, []);
  const handleRestore = useCallback(() => setMaximized(null), []);
  const handleFocus = useCallback((id: string) => setFocused(id), []);

  return (
    <div className="app">
      <div className="top-bar">
        <button className="toggle-panel" onClick={() => setPanelOpen(!panelOpen)}>
          {panelOpen ? '\u25C0' : '\u25B6'}
        </button>
        <span className="app-title">OS Terminal</span>
        <span className="session-count">{activeSessions.length} active</span>
      </div>
      <div className="main-content">
        {panelOpen && (
          <SessionPanel
            sessions={sessions}
            onCreateSession={() => {/* TODO: create session modal */}}
          />
        )}
        <div className="grid-area">
          <TerminalGrid
            sessions={sessions}
            maximized={maximized}
            focused={focused}
            minimized={minimized}
            onMaximize={handleMaximize}
            onMinimize={handleMinimize}
            onRestore={handleRestore}
            onFocus={handleFocus}
          />
        </div>
      </div>
    </div>
  );
}
