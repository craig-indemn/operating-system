import { useState, useCallback, useRef } from 'react';
import { TEXT } from '../utils/colors';

interface QuickCaptureProps {
  onCapture: (text: string) => void;
}

export function QuickCapture({ onCapture }: QuickCaptureProps) {
  const [value, setValue] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback(() => {
    const text = value.trim();
    if (!text || submitting) return;
    setSubmitting(true);
    onCapture(text);
    setValue('');
    setSubmitting(false);
    inputRef.current?.blur();
  }, [value, submitting, onCapture]);

  return (
    <div style={{
      border: `1px dashed #3f3f46`,
      borderRadius: 6,
      padding: '6px 10px',
      marginBottom: 4,
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      background: 'transparent',
    }}>
      <span style={{ color: TEXT.muted, fontSize: 12, flexShrink: 0 }}>+</span>
      <input
        ref={inputRef}
        type="text"
        placeholder="Capture a thought..."
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter') handleSubmit(); }}
        disabled={submitting}
        style={{
          flex: 1,
          background: 'transparent',
          border: 'none',
          outline: 'none',
          color: TEXT.primary,
          fontSize: 12,
          fontFamily: "'Inter', sans-serif",
          padding: 0,
        }}
      />
    </div>
  );
}
