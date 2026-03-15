import { BG, TEXT } from '../utils/colors';

interface BrowserPaneProps {
  url: string;
  title: string;
  panelId: string;
  isFocused: boolean;
  isMaximized: boolean;
  onFocus: () => void;
  onMaximize: () => void;
  onMinimize: () => void;
  onRestore: () => void;
  onClose: () => void;
}

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '4px 8px',
  background: BG.surface,
  height: 28,
  minHeight: 28,
  userSelect: 'none',
};

const btnStyle: React.CSSProperties = {
  background: 'none',
  border: `1px solid ${BG.border}`,
  color: TEXT.secondary,
  cursor: 'pointer',
  padding: '0 6px',
  borderRadius: 2,
  fontSize: 12,
  lineHeight: '18px',
};

export function BrowserPane({
  url, title, panelId: _panelId, isFocused, isMaximized,
  onFocus, onMaximize, onMinimize, onRestore, onClose,
}: BrowserPaneProps) {
  return (
    <div
      onClick={onFocus}
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        borderRadius: 4,
        overflow: 'hidden',
        border: isFocused ? `1px solid ${BG.border}` : '1px solid transparent',
        background: BG.base,
      }}
    >
      <div style={headerStyle} onDoubleClick={isMaximized ? onRestore : onMaximize}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12 }}>
          <span style={{ color: '#60a5fa', fontSize: 10 }}>◉</span>
          <span style={{ fontWeight: 600, color: TEXT.primary, fontSize: 13 }}>{title}</span>
          <span style={{ color: TEXT.muted, fontSize: 11, fontFamily: "'Geist Mono', monospace" }}>
            {new URL(url).hostname}
          </span>
        </div>
        <div style={{ display: 'flex', gap: 4 }} onMouseDown={e => e.stopPropagation()}>
          <button style={btnStyle} onClick={e => { e.stopPropagation(); onMinimize(); }} title="Minimize">_</button>
          <button style={btnStyle} onClick={e => { e.stopPropagation(); isMaximized ? onRestore() : onMaximize(); }} title={isMaximized ? 'Restore' : 'Maximize'}>
            {isMaximized ? '❏' : '□'}
          </button>
          <button
            style={{ ...btnStyle }}
            onClick={e => { e.stopPropagation(); onClose(); }}
            title="Close"
            onMouseOver={e => { (e.target as HTMLButtonElement).style.background = '#4a2020'; (e.target as HTMLButtonElement).style.color = '#f87171'; }}
            onMouseOut={e => { (e.target as HTMLButtonElement).style.background = 'none'; (e.target as HTMLButtonElement).style.color = TEXT.secondary; }}
          >×</button>
        </div>
      </div>
      <iframe
        src={url}
        style={{
          flex: 1,
          border: 'none',
          background: '#ffffff',
          width: '100%',
        }}
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-downloads"
        title={title}
      />
    </div>
  );
}
