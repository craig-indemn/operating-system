import { useEffect, useRef } from 'react';
import type { HiveRecord } from '../types/hive';
import { BG, TEXT } from '../utils/colors';

interface ActionMenuProps {
  record: HiveRecord;
  x: number;
  y: number;
  onClose: () => void;
  onAction: (action: string, record: HiveRecord) => void;
}

const menuStyle: React.CSSProperties = {
  position: 'fixed',
  zIndex: 1000,
  background: BG.surface,
  border: `1px solid ${BG.border}`,
  borderRadius: 6,
  minWidth: 160,
  overflow: 'hidden',
  boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
  fontFamily: "'Inter', sans-serif",
};

const itemStyle: React.CSSProperties = {
  display: 'block',
  width: '100%',
  background: 'none',
  border: 'none',
  color: TEXT.primary,
  fontSize: 13,
  padding: '8px 12px',
  textAlign: 'left',
  cursor: 'pointer',
  fontFamily: 'inherit',
};

export function ActionMenu({ record, x, y, onClose, onAction }: ActionMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    const keyHandler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('mousedown', handler);
    document.addEventListener('keydown', keyHandler);
    return () => {
      document.removeEventListener('mousedown', handler);
      document.removeEventListener('keydown', keyHandler);
    };
  }, [onClose]);

  // Adjust position to keep menu on screen
  const adjustedX = Math.min(x, window.innerWidth - 180);
  const adjustedY = Math.min(y, window.innerHeight - 250);

  const isSynced = !!record.system;

  return (
    <div ref={menuRef} style={{ ...menuStyle, left: adjustedX, top: adjustedY }}>
      <button
        style={itemStyle}
        onClick={() => onAction('open_session', record)}
        onMouseOver={e => (e.currentTarget.style.background = BG.lifted)}
        onMouseOut={e => (e.currentTarget.style.background = 'none')}
      >
        Open in new session
      </button>
      <button
        style={itemStyle}
        onClick={() => onAction('mark_done', record)}
        onMouseOver={e => (e.currentTarget.style.background = BG.lifted)}
        onMouseOut={e => (e.currentTarget.style.background = 'none')}
      >
        Mark done
      </button>
      <button
        style={itemStyle}
        onClick={() => onAction('change_priority', record)}
        onMouseOver={e => (e.currentTarget.style.background = BG.lifted)}
        onMouseOut={e => (e.currentTarget.style.background = 'none')}
      >
        Change priority
      </button>
      <button
        style={itemStyle}
        onClick={() => onAction('archive', record)}
        onMouseOver={e => (e.currentTarget.style.background = BG.lifted)}
        onMouseOut={e => (e.currentTarget.style.background = 'none')}
      >
        Archive
      </button>
      <button
        style={itemStyle}
        onClick={() => onAction('create_linked', record)}
        onMouseOver={e => (e.currentTarget.style.background = BG.lifted)}
        onMouseOut={e => (e.currentTarget.style.background = 'none')}
      >
        Create linked note
      </button>
      {isSynced && (
        <button
          style={itemStyle}
          onClick={() => onAction('open_external', record)}
          onMouseOver={e => (e.currentTarget.style.background = BG.lifted)}
          onMouseOut={e => (e.currentTarget.style.background = 'none')}
        >
          Open in {record.system}
        </button>
      )}
    </div>
  );
}
