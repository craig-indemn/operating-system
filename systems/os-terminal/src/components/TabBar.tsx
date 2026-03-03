import type { SessionInfo } from '../hooks/useSessions';

const STATUS_COLORS: Record<string, string> = {
  started: '#60a5fa',
  active: '#4ade80',
  idle: '#fbbf24',
  context_low: '#f87171',
  ended: '#6b7280',
  ended_dirty: '#ef4444',
  stale: '#6b7280',
};

interface TabBarProps {
  sessions: SessionInfo[];
  activeSessionId: string;
  onSelect: (sessionId: string) => void;
}

export function TabBar({ sessions, activeSessionId, onSelect }: TabBarProps) {
  return (
    <div className="tab-bar">
      {sessions.map(session => (
        <button
          key={session.session_id}
          className={`tab-item${session.session_id === activeSessionId ? ' active' : ''}`}
          onClick={() => onSelect(session.session_id)}
        >
          <span
            className="status-dot"
            style={{ backgroundColor: STATUS_COLORS[session.status] || '#9ca3af' }}
          />
          <span className="tab-item-name">{session.name}</span>
        </button>
      ))}
    </div>
  );
}
