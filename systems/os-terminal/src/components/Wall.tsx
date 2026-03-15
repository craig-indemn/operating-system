import { useState, useMemo, useCallback } from 'react';
import { HiveTile } from './HiveTile';
import { QuickCapture } from './QuickCapture';
import { SearchTile } from './SearchTile';
import type { HiveRecord } from '../types/hive';
import type { SessionInfo } from '../hooks/useSessions';
import { sortWallRecords, loadWallOrder, saveWallOrder, reorderWall, getHighlightReel } from '../utils/wallOrder';
import { BG, TEXT, TYPE_COLORS } from '../utils/colors';

interface WallProps {
  records: HiveRecord[];
  sessions: SessionInfo[];
  activeDomain: string | null;
  searchQuery: string;
  searchResults: HiveRecord[] | null;
  compressed: boolean; // true when Focus has 2+ panels
  overview: boolean;   // true when Wall is full-screen overview
  onTileClick: (record: HiveRecord) => void;
  onTileContextMenu: (record: HiveRecord, e: React.MouseEvent) => void;
  onSessionClick: (sessionId: string) => void;
  onQuickCapture: (text: string) => void;
  onSearch: (query: string) => void;
  onClearSearch: () => void;
}

/** Convert active sessions to HiveRecord-like objects for unified Wall display */
function sessionToTile(session: SessionInfo): HiveRecord {
  return {
    record_id: `session:${session.session_id}`,
    type: 'session',
    name: session.name,
    // Preserve actual session status for tile rendering
    status: 'active',
    // Sessions are always top priority — they're the most immediate active work
    priority: 'critical',
    domains: session.project ? [session.project] : undefined,
    updated_at: session.last_activity,
    created_at: session.created_at,
    // Stash session data for rendering and click handler
    _sessionId: session.session_id,
    _sessionStatus: session.status, // original session status for color
    _contextPct: session.context_remaining_pct,
    _sessionType: session.type,
    _model: session.model,
  };
}

/**
 * Check if a record has content worth showing beyond badge+title.
 * Only tiles with rich content get expanded/featured heights.
 */
function hasRichContent(record: HiveRecord): boolean {
  if (record.type === 'session') return true; // always has context% + model
  if (record.type === 'workflow' && record.current_context) return true;
  if (record.type === 'workflow' && record.objective) return true;
  if (record.content) return true;
  if (record.tags && record.tags.length > 0) return true;
  if (record.refs_out && Object.keys(record.refs_out).length > 0) return true;
  return false;
}

/**
 * Compute tile height based on record status, priority, content, and mode.
 * Only allocate expanded/featured heights for tiles with content to display.
 *
 * Design tiers:
 *   Compressed (48-60px): done/backlog, or compressed Wall
 *   Standard (70-85px): default — badge + title + timestamp
 *   Expanded (120-140px): active/high-priority WITH content
 *   Featured (160-180px): overview mode, rich tiles only
 */
function getTileHeight(record: HiveRecord, overview: boolean, compressed: boolean): number {
  if (compressed) return 52;

  const status = record.status || '';
  const priority = record.priority || '';
  const isSession = record.type === 'session';
  const isHighPriority = priority === 'critical' || priority === 'high';
  const hasContent = hasRichContent(record);

  // Done/archived/backlog always compressed
  if (status === 'done' || status === 'archived') return 48;
  if (status === 'backlog') return 52;

  if (overview) {
    if (isSession) return 140;
    if (isHighPriority && hasContent) return 180;
    if (hasContent) return 120;
    return 85;
  }

  // Normal Wall
  if (isSession) return 120;
  if (isHighPriority && hasContent) return 140;
  if (status === 'active' && hasContent) return 120;
  if (hasContent) return 85;
  return 70;
}

export function Wall({
  records, sessions, activeDomain, searchQuery, searchResults,
  compressed, overview, onTileClick, onTileContextMenu, onSessionClick,
  onQuickCapture, onSearch, onClearSearch,
}: WallProps) {
  const [manualOrder, setManualOrder] = useState<string[]>(loadWallOrder);
  const [dragSource, setDragSource] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<string | null>(null);

  // Merge sessions into tile list
  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  // Create session tiles and merge with Hive records
  const allRecords = useMemo(() => {
    const sessionTiles = activeSessions.map(sessionToTile);
    // Dedup: don't show Hive records for active sessions
    const sessionNames = new Set(activeSessions.map(s => s.name));
    const filteredRecords = records.filter(r => {
      // Skip if this is a session entity that matches an active session
      if (r.type === 'workflow' && sessionNames.has(r.name ?? '')) return false;
      return true;
    });
    return [...sessionTiles, ...filteredRecords];
  }, [records, activeSessions]);

  // Apply domain filter (fade, not hide)
  const domainFilteredIds = useMemo(() => {
    if (!activeDomain) return null;
    return new Set(
      allRecords
        .filter(r => r.domains?.includes(activeDomain))
        .map(r => r.record_id),
    );
  }, [allRecords, activeDomain]);

  // Apply search filter
  const searchFilteredIds = useMemo(() => {
    if (!searchResults) return null;
    return new Set(searchResults.map(r => r.record_id));
  }, [searchResults]);

  // Sort and optionally filter for highlight reel
  const sortedRecords = useMemo(() => {
    let recs = sortWallRecords(allRecords, manualOrder);
    if (compressed) {
      recs = getHighlightReel(recs);
    }
    return recs;
  }, [allRecords, manualOrder, compressed]);

  // Drag-to-reorder
  const handleDragStart = useCallback((id: string) => setDragSource(id), []);
  const handleDragEnter = useCallback((id: string) => setDragOver(id), []);
  const handleDragEnd = useCallback(() => {
    if (dragSource && dragOver && dragSource !== dragOver) {
      const allIds = sortedRecords.map(r => r.record_id);
      const newOrder = reorderWall(manualOrder, allIds, dragSource, dragOver);
      setManualOrder(newOrder);
      saveWallOrder(newOrder);
    }
    setDragSource(null);
    setDragOver(null);
  }, [dragSource, dragOver, sortedRecords, manualOrder]);

  const handleTileClick = useCallback((record: HiveRecord) => {
    // Session tiles route to session handler
    if (record.record_id.startsWith('session:')) {
      const sessionId = record._sessionId as string;
      onSessionClick(sessionId);
      return;
    }
    onTileClick(record);
  }, [onTileClick, onSessionClick]);

  // Grid column config based on mode
  // Overview: 3-4 columns (250px min), Normal: 1-2 columns (160px min)
  const gridColumns = overview
    ? 'repeat(auto-fill, minmax(250px, 1fr))'
    : 'repeat(auto-fill, minmax(160px, 1fr))';

  return (
    <div style={{
      height: '100%',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      background: BG.base,
    }}>
      {/* Fixed tiles: Quick Capture + Search */}
      <div style={{ padding: '8px 8px 0', flexShrink: 0 }}>
        <QuickCapture onCapture={onQuickCapture} />
        <SearchTile
          query={searchQuery}
          onSearch={onSearch}
          onClear={onClearSearch}
        />
      </div>

      {/* Scrollable tile area — CSS grid masonry */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        overflowX: 'hidden',
        padding: 8,
        display: 'grid',
        gridTemplateColumns: gridColumns,
        gap: 4,
        alignContent: 'start',
        alignItems: 'start',
        scrollbarWidth: 'thin',
        scrollbarColor: `${BG.border} transparent`,
      }}>
        {sortedRecords.map(record => {
          const isDomainFaded = domainFilteredIds && !domainFilteredIds.has(record.record_id);
          const isSearchFaded = searchFilteredIds && !searchFilteredIds.has(record.record_id);

          let opacity = 1;
          if (isSearchFaded) opacity = 0.1;
          else if (isDomainFaded) opacity = 0.2;

          const tileHeight = getTileHeight(record, overview, compressed);

          return (
            <div
              key={record.record_id}
              draggable
              onDragStart={() => handleDragStart(record.record_id)}
              onDragEnter={() => handleDragEnter(record.record_id)}
              onDragOver={e => e.preventDefault()}
              onDragEnd={handleDragEnd}
              style={{
                height: tileHeight,
                opacity: dragSource === record.record_id ? 0.5 : opacity,
                outline: dragOver === record.record_id && dragSource !== record.record_id
                  ? `2px solid ${TYPE_COLORS[record.type] || '#a78bfa'}` : 'none',
                borderRadius: 6,
                transition: 'opacity 150ms ease, min-height 300ms ease-out',
              }}
            >
              <HiveTile
                record={record}
                onClick={handleTileClick}
                onContextMenu={onTileContextMenu}
              />
            </div>
          );
        })}

        {sortedRecords.length === 0 && (
          <div style={{
            color: TEXT.muted,
            fontSize: 13,
            fontFamily: "'Inter', sans-serif",
            textAlign: 'center',
            padding: '32px 16px',
            gridColumn: '1 / -1',
          }}>
            No records yet
          </div>
        )}
      </div>
    </div>
  );
}
