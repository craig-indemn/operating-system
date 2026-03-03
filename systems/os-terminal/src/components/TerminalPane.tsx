import { useEffect, useImperativeHandle, forwardRef } from 'react';
import { useTerminal } from '../hooks/useTerminal';
import type { ConnectionState } from '../hooks/useTerminal';
import '@xterm/xterm/css/xterm.css';

export interface TerminalPaneHandle {
  fit: () => void;
  focus: () => void;
}

interface TerminalPaneProps {
  sessionName: string;
  sessionId: string;
  status: string;
  contextPct: number;
  isMaximized: boolean;
  isFocused: boolean;
  onMaximize: () => void;
  onMinimize: () => void;
  onRestore: () => void;
  onFocus: () => void;
  onClose: () => void;
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

const CONNECTION_COLORS: Record<ConnectionState, string> = {
  connected: '', // use session status color
  reconnecting: '#fbbf24',
  disconnected: '#ef4444',
};

export const TerminalPane = forwardRef<TerminalPaneHandle, TerminalPaneProps>(
  ({ sessionName, sessionId: _sessionId, status, contextPct, isMaximized, isFocused, onMaximize, onMinimize, onRestore, onFocus, onClose }, ref) => {
    const { containerRef, fit, focus, connectionState } = useTerminal({ sessionName });

    useImperativeHandle(ref, () => ({ fit, focus }), [fit, focus]);

    // Refit when maximized/restored
    useEffect(() => {
      const timer = setTimeout(fit, 50);
      return () => clearTimeout(timer);
    }, [isMaximized, fit]);

    // Status dot: override color when disconnected/reconnecting
    const dotColor = CONNECTION_COLORS[connectionState] || STATUS_COLORS[status] || '#9ca3af';
    const dotClass = `status-dot${connectionState === 'reconnecting' ? ' reconnecting' : ''}`;

    return (
      <div
        className={`terminal-pane ${isFocused ? 'focused' : ''}`}
        onClick={onFocus}
        style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
      >
        <div className="terminal-header" onDoubleClick={isMaximized ? onRestore : onMaximize}>
          <div className="terminal-header-left">
            <span className={dotClass} style={{ backgroundColor: dotColor }} />
            <span className="session-name">{sessionName}</span>
            <span className="context-pct">{contextPct}%</span>
          </div>
          <div className="terminal-header-right" onMouseDown={(e) => e.stopPropagation()}>
            <button className="pane-btn" onClick={(e) => { e.stopPropagation(); onMinimize(); }} title="Minimize">_</button>
            <button className="pane-btn" onClick={(e) => { e.stopPropagation(); isMaximized ? onRestore() : onMaximize(); }} title={isMaximized ? 'Restore' : 'Maximize'}>
              {isMaximized ? '\u274F' : '\u25A1'}
            </button>
            <button className="pane-btn close-btn" onClick={(e) => { e.stopPropagation(); onClose(); }} title="Close session">
              {'\u00D7'}
            </button>
          </div>
        </div>
        <div
          ref={containerRef as React.RefObject<HTMLDivElement>}
          className="terminal-container"
          style={{ flex: 1, overflow: 'hidden' }}
        >
          {connectionState !== 'connected' && (
            <div className="reconnect-overlay">
              <span>{connectionState === 'reconnecting' ? 'Reconnecting...' : 'Disconnected'}</span>
              {connectionState === 'reconnecting' && (
                <span className="reconnect-hint">[Press any key to reconnect now]</span>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }
);

TerminalPane.displayName = 'TerminalPane';
