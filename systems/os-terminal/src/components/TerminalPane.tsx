import { useEffect, useImperativeHandle, forwardRef } from 'react';
import { useTerminal } from '../hooks/useTerminal';
import '@xterm/xterm/css/xterm.css';

export interface TerminalPaneHandle {
  fit: () => void;
  focus: () => void;
}

interface TerminalPaneProps {
  sessionName: string;
  status: string;
  contextPct: number;
  isMaximized: boolean;
  isFocused: boolean;
  onMaximize: () => void;
  onMinimize: () => void;
  onRestore: () => void;
  onFocus: () => void;
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

export const TerminalPane = forwardRef<TerminalPaneHandle, TerminalPaneProps>(
  ({ sessionName, status, contextPct, isMaximized, isFocused, onMaximize, onMinimize, onRestore, onFocus }, ref) => {
    const { containerRef, fit, focus } = useTerminal({ sessionName });

    useImperativeHandle(ref, () => ({ fit, focus }), [fit, focus]);

    // Refit when maximized/restored
    useEffect(() => {
      const timer = setTimeout(fit, 50);
      return () => clearTimeout(timer);
    }, [isMaximized, fit]);

    const statusColor = STATUS_COLORS[status] || '#9ca3af';

    return (
      <div
        className={`terminal-pane ${isFocused ? 'focused' : ''}`}
        onClick={onFocus}
        style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
      >
        <div className="terminal-header" onDoubleClick={isMaximized ? onRestore : onMaximize}>
          <div className="terminal-header-left">
            <span className="status-dot" style={{ backgroundColor: statusColor }} />
            <span className="session-name">{sessionName}</span>
            <span className="context-pct">{contextPct}%</span>
          </div>
          <div className="terminal-header-right">
            <button className="pane-btn" onClick={(e) => { e.stopPropagation(); onMinimize(); }} title="Minimize">_</button>
            <button className="pane-btn" onClick={(e) => { e.stopPropagation(); isMaximized ? onRestore() : onMaximize(); }} title={isMaximized ? 'Restore' : 'Maximize'}>
              {isMaximized ? '\u274F' : '\u25A1'}
            </button>
          </div>
        </div>
        <div
          ref={containerRef}
          className="terminal-container"
          style={{ flex: 1, overflow: 'hidden' }}
        />
      </div>
    );
  }
);

TerminalPane.displayName = 'TerminalPane';
