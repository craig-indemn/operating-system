import { useMemo, useRef, useState, useEffect, useCallback } from 'react';
import type { HiveRecord } from '../types/hive';
import { getRecordLabel, getConnectionCount } from '../types/hive';
import { getTypeColor, getDomainColor, getStatusVisuals, hexToRgba, timeAgo, SESSION_STATUS_COLORS, BG, TEXT } from '../utils/colors';

// --- Disclosure tiers based on rendered height ---
const TIER_COMPRESSED = 0;
const TIER_STANDARD = 1;
const TIER_EXPANDED = 2;
const TIER_FEATURED = 3;

const THRESHOLD_STANDARD = 65;
const THRESHOLD_EXPANDED = 105;
const THRESHOLD_FEATURED = 165;

function getTier(height: number): number {
  if (height < THRESHOLD_STANDARD) return TIER_COMPRESSED;
  if (height < THRESHOLD_EXPANDED) return TIER_STANDARD;
  if (height < THRESHOLD_FEATURED) return TIER_EXPANDED;
  return TIER_FEATURED;
}

// --- Context line extraction ---
function getContextLine(record: HiveRecord): string {
  // Session tiles: show context % and model
  if (record.type === 'session') {
    const pct = record._contextPct as number | undefined;
    const model = record._model as string | undefined;
    const parts: string[] = [];
    if (pct !== undefined) parts.push(`Context: ${pct}%`);
    if (model) parts.push(model);
    return parts.join(' · ');
  }
  if (record.type === 'workflow' && record.current_context) {
    return truncate(record.current_context, 60);
  }
  if (record.type === 'meeting') {
    if (record.date) return record.date;
    if (record.content) return truncate(record.content, 60);
    return '';
  }
  if (record.content) {
    return truncate(record.content, 60);
  }
  return '';
}

// --- Description extraction ---
function getDescription(record: HiveRecord): string {
  if (record.type === 'workflow' && record.objective) {
    return truncate(record.objective, 120);
  }
  if (record.content) {
    return truncate(record.content, 120);
  }
  return '';
}

function truncate(text: string, maxLen: number): string {
  const cleaned = text.replace(/\n/g, ' ').trim();
  if (cleaned.length <= maxLen) return cleaned;
  return cleaned.slice(0, maxLen).trimEnd() + '\u2026';
}

// --- Display type for badge ---
function getDisplayType(record: HiveRecord): string {
  if (record.type === 'session') {
    const sessionType = record._sessionType as string | undefined;
    return sessionType === 'shell' ? 'SHELL' : 'SESSION';
  }
  if (record.type === 'knowledge' && record.tags?.length) {
    return record.tags[0]!.toUpperCase();
  }
  return record.type.toUpperCase();
}

// --- Hover background ---
function getHoverBg(statusBg: string): string {
  switch (statusBg) {
    case BG.base:    return BG.sunken;
    case BG.sunken:  return BG.surface;
    case BG.surface: return BG.lifted;
    case BG.lifted:  return '#27272a'; // zinc-800
    default:         return statusBg;
  }
}

// --- Session accent color based on session status ---
function getSessionAccentColor(record: HiveRecord): string {
  const sessionStatus = record._sessionStatus as string | undefined;
  if (sessionStatus && SESSION_STATUS_COLORS[sessionStatus]) {
    return SESSION_STATUS_COLORS[sessionStatus]!;
  }
  return SESSION_STATUS_COLORS.active!;
}

// --- Styles ---
const styles = {
  tile: (bg: string, isCompressed: boolean): React.CSSProperties => ({
    position: 'relative',
    overflow: 'hidden',
    borderRadius: 6,
    padding: isCompressed ? '6px 8px 6px 15px' : '10px 12px 10px 15px',
    backgroundColor: bg,
    cursor: 'pointer',
    transition: 'background-color 150ms ease',
    height: '100%',
    boxSizing: 'border-box',
    display: 'flex',
    flexDirection: 'column',
    minHeight: 0,
  }),

  accentBar: (color: string, opacity: number): React.CSSProperties => ({
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: 3,
    borderRadius: '6px 0 0 6px',
    backgroundColor: color,
    opacity,
  }),

  content: {
    display: 'flex',
    flexDirection: 'column' as const,
    flex: 1,
    minHeight: 0,
    overflow: 'hidden',
    gap: 2,
  },

  header: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    flexShrink: 0,
    minWidth: 0,
  },

  typeBadge: (bgColor: string, textColor: string): React.CSSProperties => ({
    display: 'inline-flex',
    alignItems: 'center',
    padding: '1px 5px',
    borderRadius: 3,
    backgroundColor: bgColor,
    color: textColor,
    fontFamily: "'Geist Mono', monospace",
    fontSize: 11,
    fontWeight: 400,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    lineHeight: '16px',
    whiteSpace: 'nowrap',
    flexShrink: 0,
  }),

  syncedIndicator: {
    fontFamily: "'Geist Mono', monospace",
    fontSize: 11,
    color: TEXT.muted,
    flexShrink: 0,
    lineHeight: '16px',
  } as React.CSSProperties,

  timestamp: {
    fontFamily: "'Geist Mono', monospace",
    fontSize: 11,
    color: TEXT.muted,
    marginLeft: 'auto',
    flexShrink: 0,
    whiteSpace: 'nowrap',
    lineHeight: '16px',
  } as React.CSSProperties,

  title: (textColor: string, isCompressed: boolean): React.CSSProperties => ({
    fontFamily: "'Inter', sans-serif",
    fontWeight: 600,
    fontSize: 13,
    lineHeight: '18px',
    color: textColor,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    WebkitLineClamp: isCompressed ? 1 : 2,
    WebkitBoxOrient: 'vertical',
    flexShrink: 0,
    margin: 0,
  }),

  contextLine: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 400,
    fontSize: 12,
    lineHeight: '16px',
    color: TEXT.secondary,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    flexShrink: 0,
  } as React.CSSProperties,

  tagsContainer: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: 4,
    flexShrink: 0,
    marginTop: 2,
  },

  tagPill: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '1px 6px',
    borderRadius: 3,
    backgroundColor: '#27272a', // zinc-800
    color: TEXT.secondary,
    fontFamily: "'Geist Mono', monospace",
    fontSize: 10,
    fontWeight: 400,
    lineHeight: '14px',
    whiteSpace: 'nowrap',
  } as React.CSSProperties,

  connections: {
    fontFamily: "'Geist Mono', monospace",
    fontSize: 11,
    color: TEXT.muted,
    marginTop: 'auto',
    textAlign: 'right',
    flexShrink: 0,
    lineHeight: '16px',
    paddingTop: 2,
  } as React.CSSProperties,

  description: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 400,
    fontSize: 12,
    lineHeight: '16px',
    color: TEXT.secondary,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    WebkitLineClamp: 3,
    WebkitBoxOrient: 'vertical',
    flexShrink: 1,
    minHeight: 0,
    marginTop: 2,
  } as React.CSSProperties,

  // Session-specific: context bar
  contextBar: (_pct: number, color: string): React.CSSProperties => ({
    height: 3,
    borderRadius: 2,
    backgroundColor: hexToRgba(color, 0.2),
    marginTop: 4,
    flexShrink: 0,
    position: 'relative',
    overflow: 'hidden',
  }),

  contextBarFill: (pct: number, color: string): React.CSSProperties => ({
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: `${pct}%`,
    backgroundColor: color,
    borderRadius: 2,
    transition: 'width 300ms ease',
  }),
} as const;

// --- Component ---

interface HiveTileProps {
  record: HiveRecord;
  onClick?: (record: HiveRecord) => void;
  onContextMenu?: (record: HiveRecord, e: React.MouseEvent) => void;
  className?: string;
}

export function HiveTile({ record, onClick, onContextMenu, className }: HiveTileProps) {
  const tileRef = useRef<HTMLDivElement>(null);
  const [tier, setTier] = useState<number>(TIER_STANDARD);
  const [hovered, setHovered] = useState(false);

  // Observe tile height for progressive disclosure
  useEffect(() => {
    const el = tileRef.current;
    if (!el) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const height = entry.contentRect.height;
        setTier(getTier(height));
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Derived visual properties
  const isSession = record.type === 'session';
  const label = useMemo(() => getRecordLabel(record), [record]);
  const displayType = useMemo(() => getDisplayType(record), [record]);
  const typeColor = useMemo(
    () => isSession ? getSessionAccentColor(record) : getTypeColor(record.type, record.tags),
    [record, isSession],
  );
  const domainColor = useMemo(
    () => getDomainColor(record.domains),
    [record.domains],
  );
  const statusVisuals = useMemo(
    () => getStatusVisuals(record.status || ''),
    [record.status],
  );
  const connectionCount = useMemo(
    () => getConnectionCount(record),
    [record],
  );
  const contextLine = useMemo(() => getContextLine(record), [record]);
  const description = useMemo(() => getDescription(record), [record]);

  // Session-specific derived values
  const sessionAccentColor = useMemo(
    () => isSession ? getSessionAccentColor(record) : null,
    [record, isSession],
  );
  const contextPct = isSession ? (record._contextPct as number | undefined) : undefined;

  const isCompressed = tier === TIER_COMPRESSED;

  const currentBg = hovered ? getHoverBg(statusVisuals.bg) : statusVisuals.bg;

  // Session tiles use session status color for accent bar
  const accentColor = sessionAccentColor || domainColor;
  const accentOpacity = isSession ? 1.0 : statusVisuals.accentOpacity;

  const handleClick = useCallback(() => {
    onClick?.(record);
  }, [onClick, record]);

  const handleContextMenu = useCallback((e: React.MouseEvent) => {
    if (onContextMenu) {
      e.preventDefault();
      onContextMenu(record, e);
    }
  }, [onContextMenu, record]);

  return (
    <div
      ref={tileRef}
      className={className}
      style={styles.tile(currentBg, isCompressed)}
      onClick={handleClick}
      onContextMenu={handleContextMenu}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
    >
      {/* Accent bar — session status color or domain color */}
      <div style={styles.accentBar(accentColor, accentOpacity)} />

      {/* Tile content */}
      <div style={styles.content}>
        {/* Header: type badge + synced indicator + model badge (sessions) + timestamp */}
        <div style={styles.header}>
          <span style={styles.typeBadge(hexToRgba(typeColor, 0.15), typeColor)}>
            {displayType}
          </span>
          {/* Session: model badge */}
          {isSession && typeof record._model === 'string' && tier >= TIER_STANDARD && (
            <span style={styles.typeBadge(hexToRgba('#525252', 0.3), TEXT.secondary)}>
              {record._model.replace('claude-', '').split('-')[0]!.toUpperCase()}
            </span>
          )}
          {record.system && (
            <span style={styles.syncedIndicator} title={`Synced from ${record.system}`}>
              &#x27F3;
            </span>
          )}
          {tier >= TIER_STANDARD && (
            <span style={styles.timestamp}>
              {timeAgo(record.updated_at || record.created_at || '')}
            </span>
          )}
        </div>

        {/* Title */}
        <div style={styles.title(statusVisuals.textColor, isCompressed)}>
          {label}
        </div>

        {/* Context line (expanded+) */}
        {tier >= TIER_EXPANDED && contextLine && (
          <div style={styles.contextLine}>{contextLine}</div>
        )}

        {/* Session: context bar (expanded+) */}
        {isSession && contextPct !== undefined && tier >= TIER_EXPANDED && sessionAccentColor && (
          <div style={styles.contextBar(contextPct, sessionAccentColor)}>
            <div style={styles.contextBarFill(contextPct, sessionAccentColor)} />
          </div>
        )}

        {/* Tags (expanded+) */}
        {tier >= TIER_EXPANDED && record.tags && record.tags.length > 0 && (
          <div style={styles.tagsContainer}>
            {record.tags.slice(0, 4).map((tag) => (
              <span key={tag} style={styles.tagPill}>{tag}</span>
            ))}
          </div>
        )}

        {/* Description (featured) */}
        {tier >= TIER_FEATURED && description && (
          <div style={styles.description}>{description}</div>
        )}

        {/* Connection count (expanded+) */}
        {tier >= TIER_EXPANDED && connectionCount > 0 && (
          <span style={styles.connections}>
            &#x25C6; {connectionCount}
          </span>
        )}
      </div>
    </div>
  );
}
