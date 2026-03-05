import { useState, useMemo, useCallback } from 'react';
import { useSessions } from './hooks/useSessions';
import { useAuth } from './hooks/useAuth';
import { useResponsive } from './hooks/useResponsive';
import { TerminalGrid } from './components/TerminalGrid';
import { SessionPanel } from './components/SessionPanel';
import { LoginScreen, ErrorScreen } from './components/LoginScreen';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { authFetch } from './utils/auth';

export default function App() {
  const { status, authRequired, login, logout, retry } = useAuth();

  if (status === 'loading') return null;
  if (status === 'error') return <ErrorScreen onRetry={retry} />;
  if (status === 'unauthenticated') return <LoginScreen onLogin={login} />;
  return <AuthenticatedApp onLogout={logout} authRequired={authRequired} />;
}

function AuthenticatedApp({ onLogout, authRequired }: { onLogout: () => void; authRequired: boolean }) {
  const sessions = useSessions();
  const { isMobile } = useResponsive();
  const [panelOpen, setPanelOpen] = useState(false);
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
    authFetch(`/api/sessions/${id}?force=true`, { method: 'DELETE' })
      .then(r => { if (!r.ok) return r.json().then(e => console.error('Close failed:', e)); })
      .catch(err => console.error('Close error:', err));
  }, []);
  const handleCreateSession = useCallback(() => {
    const name = prompt('Session name:');
    if (!name?.trim()) return;
    authFetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name.trim() }),
    }).catch(() => {/* watcher will pick up the new session */});
  }, []);
  const handleSelectSession = useCallback((id: string) => {
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
      if (activeSessions[index]) {
        const id = activeSessions[index]!.session_id;
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
      if (focused && !isMobile) {
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
        {authRequired && (
          <button className="logout-btn" onClick={onLogout} title="Disconnect">Logout</button>
        )}
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
            maximized={isMobile ? null : maximized}
            focused={focused}
            minimized={minimized}
            isMobile={isMobile}
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
