import { useState, useMemo, useCallback } from 'react';
import { useSessions } from './hooks/useSessions';
import { useAuth } from './hooks/useAuth';
import { useResponsive } from './hooks/useResponsive';
import { useHiveRecords } from './hooks/useHiveRecords';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { Wall } from './components/Wall';
import { FocusArea, BrowserPanel } from './components/FocusArea';
import { ActionMenu } from './components/ActionMenu';
import { LoginScreen, ErrorScreen } from './components/LoginScreen';
import { authFetch } from './utils/auth';
import { BG, TEXT, DOMAIN_COLORS } from './utils/colors';
import type { HiveRecord } from './types/hive';

export default function App() {
  const { status, authRequired, login, logout, retry } = useAuth();

  if (status === 'loading') return null;
  if (status === 'error') return <ErrorScreen onRetry={retry} />;
  if (status === 'unauthenticated') return <LoginScreen onLogin={login} />;
  return <AuthenticatedApp onLogout={logout} authRequired={authRequired} />;
}

// Domain filter pills
const DOMAINS = [
  { key: null, label: 'All' },
  { key: 'indemn', label: 'Indemn' },
  { key: 'career-catalyst', label: 'Career Catalyst' },
  { key: 'personal', label: 'Personal' },
] as const;

function AuthenticatedApp({ onLogout, authRequired }: { onLogout: () => void; authRequired: boolean }) {
  const sessions = useSessions();
  const { records, refresh: refreshHive } = useHiveRecords();
  const { isMobile, isTablet } = useResponsive();

  // Focus Area state
  const [maximized, setMaximized] = useState<string | null>(null);
  const [focused, setFocused] = useState<string | null>(null);
  const [minimized, setMinimized] = useState<Set<string>>(new Set());
  const [browserPanels, setBrowserPanels] = useState<BrowserPanel[]>([]);

  // Wall state
  const [activeDomain, setActiveDomain] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<HiveRecord[] | null>(null);
  const [overview, setOverview] = useState(false);
  const [wallOpen, setWallOpen] = useState(true); // For tablet slide-out
  const [mobileView, setMobileView] = useState<'wall' | 'focus'>('wall'); // For mobile toggle

  // Action menu state
  const [actionMenu, setActionMenu] = useState<{ record: HiveRecord; x: number; y: number } | null>(null);

  // Objective prompt state (for session spawning from tiles)
  const [objectivePrompt, setObjectivePrompt] = useState<{ record: HiveRecord } | null>(null);

  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  const focusPanelCount = useMemo(() => {
    const terminalCount = activeSessions.filter(s => !minimized.has(s.session_id)).length;
    const browserCount = browserPanels.filter(p => !minimized.has(p.id)).length;
    return terminalCount + browserCount;
  }, [activeSessions, browserPanels, minimized]);

  // Wall is compressed when Focus has 2+ panels
  const wallCompressed = focusPanelCount >= 2;

  // --- Session handlers ---
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

  const handleCloseBrowser = useCallback((id: string) => {
    setBrowserPanels(prev => prev.filter(p => p.id !== id));
    setMinimized(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const handleCreateSession = useCallback((type: 'claude' | 'shell' = 'claude', name?: string) => {
    const sessionName = name || prompt(type === 'shell' ? 'Terminal name:' : 'Session name:');
    if (!sessionName?.trim()) return;
    authFetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: sessionName.trim(), type }),
    }).catch(() => {/* watcher will pick up */});
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
    if (overview) setOverview(false);
  }, [overview]);

  // --- Hive / Wall handlers ---
  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query);
    try {
      const res = await authFetch(`/api/hive/search?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResults(Array.isArray(data) ? data : data.records || []);
      }
    } catch {
      // Search failed — leave results as is
    }
  }, []);

  const handleClearSearch = useCallback(() => {
    setSearchQuery('');
    setSearchResults(null);
  }, []);

  const handleQuickCapture = useCallback(async (text: string) => {
    try {
      await authFetch('/api/hive/records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'note', title: text }),
      });
      refreshHive();
    } catch (err) {
      console.error('Quick capture failed:', err);
    }
  }, [refreshHive]);

  const handleTileClick = useCallback((record: HiveRecord) => {
    // Open objective prompt for session spawning
    setObjectivePrompt({ record });
  }, []);

  const handleTileContextMenu = useCallback((record: HiveRecord, e: React.MouseEvent) => {
    e.preventDefault();
    setActionMenu({ record, x: e.clientX, y: e.clientY });
  }, []);

  const handleTileAction = useCallback(async (action: string, record: HiveRecord) => {
    setActionMenu(null);

    switch (action) {
      case 'mark_done':
        try {
          await authFetch(`/api/hive/records/${record.record_id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'done' }),
          });
          refreshHive();
        } catch (err) {
          console.error('Mark done failed:', err);
        }
        break;

      case 'archive':
        try {
          await authFetch(`/api/hive/records/${record.record_id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'archived' }),
          });
          refreshHive();
        } catch (err) {
          console.error('Archive failed:', err);
        }
        break;

      case 'change_priority': {
        const priority = prompt('Priority (critical, high, medium, low):');
        if (!priority) break;
        try {
          await authFetch(`/api/hive/records/${record.record_id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ priority }),
          });
          refreshHive();
        } catch (err) {
          console.error('Change priority failed:', err);
        }
        break;
      }

      case 'open_session':
        setObjectivePrompt({ record });
        break;

      case 'create_linked': {
        const title = prompt('Linked note title:');
        if (!title?.trim()) break;
        try {
          const refs: Record<string, string> = {};
          refs[record.type === 'knowledge' ? 'knowledge' : record.type] = record.record_id;
          await authFetch('/api/hive/records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              type: 'note',
              title: title.trim(),
              domains: record.domains,
              refs,
            }),
          });
          refreshHive();
        } catch (err) {
          console.error('Create linked note failed:', err);
        }
        break;
      }

      case 'open_external':
        if (record.ref) {
          window.open(record.ref, '_blank');
        }
        break;
    }
  }, [refreshHive]);

  // --- Session spawning from tile click ---
  const handleObjectiveSubmit = useCallback(async (_objective: string) => {
    if (!objectivePrompt) return;
    const record = objectivePrompt.record;
    setObjectivePrompt(null);

    const sessionName = (record.name || record.title || record.record_id)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 40);

    // Create session — context assembly would be spawned by the session manager
    handleCreateSession('claude', sessionName);
  }, [objectivePrompt, handleCreateSession]);

  // --- Keyboard shortcuts ---
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
    createSession: () => handleCreateSession('claude'),
    closePane: () => {
      if (focused && !isMobile) {
        setMinimized(prev => new Set(prev).add(focused));
      }
    },
    escapeMaximize: () => {
      if (objectivePrompt) {
        setObjectivePrompt(null);
      } else {
        setMaximized(null);
      }
    },
    togglePanel: () => setOverview(prev => !prev),
    toggleOverview: () => setOverview(prev => !prev),
  });

  // Compute Wall width based on responsive state and focus panels
  const wallWidth = overview ? '100%'
    : isMobile ? '100%'
    : isTablet ? (wallOpen ? 300 : 0)
    : focusPanelCount === 0 ? 400
    : focusPanelCount === 1 ? 300
    : 240;

  const wallElement = (
    <Wall
      records={records}
      sessions={sessions}
      activeDomain={activeDomain}
      searchQuery={searchQuery}
      searchResults={searchResults}
      compressed={wallCompressed && !overview}
      overview={overview}
      onTileClick={handleTileClick}
      onTileContextMenu={handleTileContextMenu}
      onSessionClick={(id) => {
        handleSelectSession(id);
        if (isMobile) setMobileView('focus');
        if (isTablet) setWallOpen(false);
      }}
      onQuickCapture={handleQuickCapture}
      onSearch={handleSearch}
      onClearSearch={handleClearSearch}
    />
  );

  const focusElement = (
    <FocusArea
      sessions={sessions}
      browserPanels={browserPanels}
      maximized={isMobile ? null : maximized}
      focused={focused}
      minimized={minimized}
      isMobile={isMobile}
      onMaximize={handleMaximize}
      onMinimize={handleMinimize}
      onRestore={handleRestore}
      onFocus={handleFocus}
      onCloseSession={handleCloseSession}
      onCloseBrowser={handleCloseBrowser}
    />
  );

  return (
    <div style={{
      height: '100%',
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: BG.base,
      fontFamily: "'Inter', sans-serif",
      color: TEXT.primary,
    }}>
      {/* Top Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: isMobile ? 6 : 12,
        padding: '0 12px',
        height: isMobile ? 44 : 32,
        minHeight: isMobile ? 44 : 32,
        borderBottom: `1px solid ${BG.border}`,
        background: BG.base,
      }}>
        {/* Left: Wall toggle (tablet/mobile) + HIVE branding */}
        {(isTablet || isMobile) && (
          <button
            onClick={() => isMobile ? setMobileView(prev => prev === 'wall' ? 'focus' : 'wall') : setWallOpen(prev => !prev)}
            style={{
              background: 'none',
              border: 'none',
              color: TEXT.muted,
              cursor: 'pointer',
              fontSize: 16,
              padding: '2px 6px',
              minWidth: isMobile ? 44 : undefined,
              minHeight: isMobile ? 44 : undefined,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >{isMobile ? (mobileView === 'wall' ? '⊟' : '⊞') : (wallOpen ? '◀' : '▶')}</button>
        )}
        <span style={{
          fontSize: 13,
          fontWeight: 700,
          color: TEXT.muted,
          textTransform: 'uppercase',
          letterSpacing: 2,
          fontFamily: "'Inter', sans-serif",
        }}>HIVE</span>

        {/* Center: Domain filter pills (hidden on mobile) */}
        {!isMobile && (
          <div style={{ display: 'flex', gap: 4, marginLeft: 16 }}>
            {DOMAINS.map(d => {
              const isActive = activeDomain === d.key;
              const accentColor = d.key ? DOMAIN_COLORS[d.key] || TEXT.muted : TEXT.muted;
              return (
                <button
                  key={d.key ?? 'all'}
                  onClick={() => setActiveDomain(isActive ? null : d.key)}
                  style={{
                    background: isActive ? accentColor : BG.border,
                    color: isActive ? '#ffffff' : TEXT.secondary,
                    border: 'none',
                    borderRadius: 4,
                    padding: '2px 10px',
                    fontSize: 11,
                    fontWeight: 500,
                    cursor: 'pointer',
                    fontFamily: "'Inter', sans-serif",
                    transition: 'background 150ms ease',
                  }}
                >
                  {d.label}
                </button>
              );
            })}
          </div>
        )}

        {/* Right: session count + controls */}
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 12, color: TEXT.muted, fontFamily: "'Geist Mono', monospace" }}>
            {activeSessions.length} session{activeSessions.length !== 1 ? 's' : ''}
          </span>
          {!isMobile && (
            <button
              onClick={() => setOverview(prev => !prev)}
              title="Overview (Ctrl+Shift+O)"
              style={{
                background: overview ? BG.lifted : 'none',
                border: `1px solid ${overview ? TEXT.muted : BG.border}`,
                color: overview ? TEXT.primary : TEXT.muted,
                cursor: 'pointer',
                borderRadius: 4,
                padding: '2px 8px',
                fontSize: 11,
                fontFamily: "'Geist Mono', monospace",
              }}
            >⊞</button>
          )}
          <button
            onClick={() => handleCreateSession('claude')}
            title="New Claude Session (⌘N)"
            style={{
              background: 'none',
              border: `1px solid ${BG.border}`,
              color: TEXT.muted,
              cursor: 'pointer',
              borderRadius: 4,
              padding: '2px 8px',
              fontSize: 12,
              minHeight: isMobile ? 36 : undefined,
            }}
          >+</button>
          {authRequired && (
            <button
              onClick={onLogout}
              title="Disconnect"
              style={{
                background: 'none',
                border: 'none',
                color: TEXT.muted,
                cursor: 'pointer',
                fontSize: 11,
                padding: '2px 4px',
              }}
            >Logout</button>
          )}
        </div>
      </div>

      {/* Main content */}
      {isMobile ? (
        /* Mobile: Full-screen toggle between Wall and Focus views */
        <div style={{ flex: 1, overflow: 'hidden' }}>
          {mobileView === 'wall' ? wallElement : focusElement}
        </div>
      ) : isTablet ? (
        /* Tablet: Wall is slide-out overlay, Focus takes full width */
        <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
          {/* Slide-out Wall overlay */}
          <div style={{
            position: 'absolute',
            left: 0,
            top: 0,
            bottom: 0,
            width: 300,
            zIndex: 100,
            transform: wallOpen ? 'translateX(0)' : 'translateX(-100%)',
            transition: 'transform 200ms ease',
            boxShadow: wallOpen ? '4px 0 20px rgba(0,0,0,0.5)' : 'none',
            borderRight: `1px solid ${BG.border}`,
            background: BG.base,
          }}>
            {wallElement}
          </div>
          {/* Backdrop */}
          {wallOpen && (
            <div
              style={{
                position: 'absolute', inset: 0, zIndex: 99,
                background: 'rgba(0,0,0,0.3)',
              }}
              onClick={() => setWallOpen(false)}
            />
          )}
          {/* Focus takes full width */}
          <div style={{ height: '100%', overflow: 'hidden' }}>
            {focusElement}
          </div>
        </div>
      ) : (
        /* Desktop: Wall + Focus side by side */
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Wall */}
          <div style={{
            width: wallWidth,
            minWidth: overview ? undefined : 240,
            maxWidth: overview ? undefined : (focusPanelCount === 0 ? 400 : undefined),
            transition: 'width 300ms ease-out',
            borderRight: overview ? 'none' : `1px solid ${BG.border}`,
            flexShrink: 0,
            overflow: 'hidden',
          }}>
            {wallElement}
          </div>
          {/* Focus Area — hidden in overview mode */}
          {!overview && (
            <div style={{ flex: 1, overflow: 'hidden' }}>
              {focusElement}
            </div>
          )}
        </div>
      )}

      {/* Action Menu */}
      {actionMenu && (
        <ActionMenu
          record={actionMenu.record}
          x={actionMenu.x}
          y={actionMenu.y}
          onClose={() => setActionMenu(null)}
          onAction={handleTileAction}
        />
      )}

      {/* Objective Prompt Modal */}
      {objectivePrompt && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 900,
        }}
        onClick={() => setObjectivePrompt(null)}
        >
          <div
            style={{
              background: BG.surface,
              border: `1px solid ${BG.border}`,
              borderRadius: 6,
              padding: 24,
              width: 400,
              maxWidth: '90vw',
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4, color: TEXT.primary }}>
              {objectivePrompt.record.title || objectivePrompt.record.name || objectivePrompt.record.record_id}
            </div>
            <div style={{ fontSize: 12, color: TEXT.muted, marginBottom: 16 }}>
              What are you trying to accomplish?
            </div>
            <input
              autoFocus
              type="text"
              placeholder="Describe your objective..."
              onKeyDown={e => {
                if (e.key === 'Enter') {
                  handleObjectiveSubmit((e.target as HTMLInputElement).value);
                }
                if (e.key === 'Escape') setObjectivePrompt(null);
              }}
              style={{
                width: '100%',
                background: BG.base,
                border: `1px solid ${BG.border}`,
                borderRadius: 4,
                color: TEXT.primary,
                fontSize: 13,
                padding: '10px 12px',
                outline: 'none',
                fontFamily: "'Inter', sans-serif",
                boxSizing: 'border-box',
              }}
            />
            <div style={{ fontSize: 11, color: TEXT.muted, marginTop: 8 }}>
              Press Enter to start session · Escape to cancel
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
