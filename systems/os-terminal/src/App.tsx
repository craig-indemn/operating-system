import { useState, useMemo, useCallback } from 'react';
import { useSessions } from './hooks/useSessions';
import { TerminalGrid } from './components/TerminalGrid';
import { SessionPanel } from './components/SessionPanel';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

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
  const handleCloseSession = useCallback((id: string) => {
    if (!confirm('Close this session?')) return;
    fetch(`/api/sessions/${id}?force=true`, { method: 'DELETE' })
      .then(r => { if (!r.ok) return r.json().then(e => console.error('Close failed:', e)); })
      .catch(err => console.error('Close error:', err));
  }, []);
  const handleCreateSession = useCallback(() => {
    const name = prompt('Session name:');
    if (!name?.trim()) return;
    fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name.trim() }),
    }).catch(() => {/* watcher will pick up the new session */});
  }, []);
  const handleSelectSession = useCallback((id: string) => {
    // Restore if minimized, clear maximize, and focus
    setMinimized(prev => {
      if (!prev.has(id)) return prev;
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
    setMaximized(null);
    setFocused(id);
  }, []);

  useKeyboardShortcuts({
    focusPane: (index: number) => {
      const active = sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status));
      if (active[index]) {
        const id = active[index]!.session_id;
        setMinimized(prev => {
          if (!prev.has(id)) return prev;
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
        setFocused(id);
      }
    },
    createSession: handleCreateSession,
    closePane: () => {
      if (focused) {
        setMinimized(prev => new Set(prev).add(focused));
      }
    },
    escapeMaximize: () => setMaximized(null),
    togglePanel: () => setPanelOpen(prev => !prev),
  });

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
        <SessionPanel
          sessions={sessions}
          onCreateSession={handleCreateSession}
          onSelectSession={handleSelectSession}
          isOpen={panelOpen}
        />
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
            onCloseSession={handleCloseSession}
          />
        </div>
      </div>
    </div>
  );
}
