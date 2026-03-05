import type { SessionInfo } from '../hooks/useSessions';

interface SessionPanelProps {
  sessions: SessionInfo[];
  onCreateSession: () => void;
  onSelectSession: (sessionId: string) => void;
  isOpen: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  started: '#60a5fa',
  active: '#4ade80',
  idle: '#fbbf24',
  context_low: '#f87171',
  ended: '#6b7280',
  ended_dirty: '#ef4444',
  stale: '#6b7280',
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function SessionPanel({ sessions, onCreateSession, onSelectSession, isOpen }: SessionPanelProps) {
  const activeSessions = sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status));
  const endedSessions = sessions.filter(s => ['ended', 'ended_dirty'].includes(s.status));

  return (
    <div className={`session-panel ${isOpen ? 'open' : 'closed'}`}>
      <div className="panel-header">
        <h2>Sessions</h2>
        <button className="create-btn" onClick={onCreateSession}>+</button>
      </div>

      <div className="panel-section">
        <h3>Active ({activeSessions.length})</h3>
        {activeSessions.map(s => (
          <div key={s.session_id} className="session-card" onClick={() => onSelectSession(s.session_id)}>
            <div className="session-card-header">
              <span className="status-dot" style={{ backgroundColor: STATUS_COLORS[s.status] || '#9ca3af' }} />
              <span className="session-card-name">{s.name}</span>
            </div>
            <div className="session-card-meta">
              <span>{s.status}</span>
              <span>ctx {s.context_remaining_pct}%</span>
              <span>{timeAgo(s.last_activity)}</span>
            </div>
          </div>
        ))}
      </div>

      {endedSessions.length > 0 && (
        <div className="panel-section">
          <h3>Ended ({endedSessions.length})</h3>
          {endedSessions.slice(0, 5).map(s => (
            <div key={s.session_id} className="session-card ended">
              <div className="session-card-header">
                <span className="status-dot" style={{ backgroundColor: STATUS_COLORS[s.status] || '#9ca3af' }} />
                <span className="session-card-name">{s.name}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
