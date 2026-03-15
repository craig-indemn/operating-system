import { useState, useCallback, useRef, useEffect } from 'react';
import { TEXT } from '../utils/colors';

interface SearchTileProps {
  query: string;
  onSearch: (query: string) => void;
  onClear: () => void;
}

export function SearchTile({ query, onSearch, onClear }: SearchTileProps) {
  const [value, setValue] = useState(query);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync external query changes
  useEffect(() => {
    setValue(query);
  }, [query]);

  const handleChange = useCallback((text: string) => {
    setValue(text);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!text.trim()) {
      onClear();
      return;
    }
    debounceRef.current = setTimeout(() => {
      onSearch(text.trim());
    }, 300);
  }, [onSearch, onClear]);

  const handleClear = useCallback(() => {
    setValue('');
    onClear();
    inputRef.current?.focus();
  }, [onClear]);

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
      <span style={{ color: TEXT.muted, fontSize: 12, flexShrink: 0 }}>⌕</span>
      <input
        ref={inputRef}
        type="text"
        placeholder="Search the Hive..."
        value={value}
        onChange={e => handleChange(e.target.value)}
        onKeyDown={e => {
          if (e.key === 'Escape') {
            handleClear();
            inputRef.current?.blur();
          }
        }}
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
      {value && (
        <button
          onClick={handleClear}
          style={{
            background: 'none',
            border: 'none',
            color: TEXT.muted,
            cursor: 'pointer',
            fontSize: 12,
            padding: '0 2px',
            lineHeight: 1,
          }}
        >×</button>
      )}
    </div>
  );
}
