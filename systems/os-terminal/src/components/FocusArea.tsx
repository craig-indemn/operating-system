import { useRef, useMemo, useCallback, useEffect, useState } from 'react';
import { TerminalPane, TerminalPaneHandle } from './TerminalPane';
import { BrowserPane } from './BrowserPane';
import { TabBar } from './TabBar';
import type { SessionInfo } from '../hooks/useSessions';

const GAP = 4;
const MIN_COL_WIDTH = 500; // slightly smaller than the old 600px to give Wall more room

export interface BrowserPanel {
  id: string;
  url: string;
  title: string;
}

interface FocusAreaProps {
  sessions: SessionInfo[];
  browserPanels: BrowserPanel[];
  maximized: string | null;
  focused: string | null;
  minimized: Set<string>;
  isMobile: boolean;
  onMaximize: (id: string) => void;
  onMinimize: (id: string) => void;
  onRestore: () => void;
  onFocus: (id: string) => void;
  onCloseSession: (id: string) => void;
  onCloseBrowser: (id: string) => void;
}

type PanelItem =
  | { kind: 'terminal'; session: SessionInfo }
  | { kind: 'browser'; panel: BrowserPanel };

function getPanelId(item: PanelItem): string {
  return item.kind === 'terminal' ? item.session.session_id : item.panel.id;
}

const FOCUS_ORDER_KEY = 'hive-focus-order';

function loadOrder(): string[] {
  try {
    const saved = localStorage.getItem(FOCUS_ORDER_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

export function FocusArea({
  sessions, browserPanels, maximized, focused, minimized, isMobile,
  onMaximize, onMinimize, onRestore, onFocus, onCloseSession, onCloseBrowser,
}: FocusAreaProps) {
  const paneRefs = useRef<Record<string, TerminalPaneHandle | null>>({});
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [dragSource, setDragSource] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<string | null>(null);
  const [numCols, setNumCols] = useState(2);
  const [order, setOrder] = useState<string[]>(loadOrder);

  const activeSessions = useMemo(
    () => sessions.filter(s => !['ended', 'ended_dirty'].includes(s.status)),
    [sessions],
  );

  // Merge terminal + browser panels into unified list
  const allPanels: PanelItem[] = useMemo(() => {
    const items: PanelItem[] = [
      ...activeSessions.filter(s => !minimized.has(s.session_id)).map(s => ({ kind: 'terminal' as const, session: s })),
      ...browserPanels.filter(p => !minimized.has(p.id)).map(p => ({ kind: 'browser' as const, panel: p })),
    ];
    return items;
  }, [activeSessions, browserPanels, minimized]);

  // Apply saved order
  const orderedPanels = useMemo(() => {
    const ids = new Set(allPanels.map(getPanelId));
    const ordered: PanelItem[] = [];
    for (const id of order) {
      const panel = allPanels.find(p => getPanelId(p) === id);
      if (panel) ordered.push(panel);
    }
    for (const p of allPanels) {
      if (!order.includes(getPanelId(p))) ordered.push(p);
    }
    return ordered.filter(p => ids.has(getPanelId(p)));
  }, [allPanels, order]);

  const updateOrder = useCallback((newOrder: string[]) => {
    setOrder(newOrder);
    localStorage.setItem(FOCUS_ORDER_KEY, JSON.stringify(newOrder));
  }, []);

  const handleDragStart = useCallback((id: string) => setDragSource(id), []);
  const handleDragEnter = useCallback((id: string) => setDragOver(id), []);
  const handleDragEnd = useCallback(() => {
    if (dragSource && dragOver && dragSource !== dragOver) {
      const ids = orderedPanels.map(getPanelId);
      const srcIdx = ids.indexOf(dragSource);
      const dstIdx = ids.indexOf(dragOver);
      if (srcIdx >= 0 && dstIdx >= 0) {
        const newIds = [...ids];
        [newIds[srcIdx], newIds[dstIdx]] = [newIds[dstIdx]!, newIds[srcIdx]!];
        updateOrder(newIds);
      }
    }
    setDragSource(null);
    setDragOver(null);
  }, [dragSource, dragOver, orderedPanels, updateOrder]);

  const refitAll = useCallback(() => {
    setTimeout(() => {
      Object.values(paneRefs.current).forEach(ref => ref?.fit());
    }, 50);
  }, []);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    const onResize = () => { clearTimeout(timer); timer = setTimeout(refitAll, 150); };
    window.addEventListener('resize', onResize);
    return () => { clearTimeout(timer); window.removeEventListener('resize', onResize); };
  }, [refitAll]);

  useEffect(() => { refitAll(); }, [orderedPanels.length, refitAll]);

  // If maximized panel disappears, restore
  const maximizedPanel = maximized ? allPanels.find(p => getPanelId(p) === maximized) : null;
  useEffect(() => {
    if (maximized && !maximizedPanel) onRestore();
  }, [maximized, maximizedPanel, onRestore]);

  // Prune stale refs
  useEffect(() => {
    const activeIds = new Set(allPanels.map(getPanelId));
    for (const id of Object.keys(paneRefs.current)) {
      if (!activeIds.has(id)) delete paneRefs.current[id];
    }
  }, [allPanels]);

  // Track column count
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new ResizeObserver(entries => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        setNumCols(Math.max(1, Math.floor((width + GAP) / (MIN_COL_WIDTH + GAP))));
      }
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  // Mobile: auto-focus first session
  useEffect(() => {
    if (isMobile && !focused && activeSessions.length > 0) {
      onFocus(activeSessions[0]!.session_id);
    }
  }, [isMobile, focused, activeSessions, onFocus]);

  // No panels — show empty state
  if (orderedPanels.length === 0 && !maximized) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#71717a', fontSize: 13, fontFamily: "'Inter', sans-serif" }}>
        Click a tile to start a session
      </div>
    );
  }

  // Mobile single-pane
  if (isMobile) {
    const activePanel = allPanels.find(p => getPanelId(p) === focused)
      ?? allPanels[0] ?? null;
    if (!activePanel) return null;

    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, padding: GAP, minHeight: 0 }}>
          {activePanel.kind === 'terminal' ? (
            <TerminalPane
              key={activePanel.session.session_id}
              ref={el => { paneRefs.current[activePanel.session.session_id] = el; }}
              sessionName={activePanel.session.name}
              sessionId={activePanel.session.session_id}
              status={activePanel.session.status}
              contextPct={activePanel.session.context_remaining_pct}
              type={activePanel.session.type}
              isMaximized={false}
              isFocused={true}
              onMaximize={() => {}}
              onMinimize={() => {}}
              onRestore={() => {}}
              onFocus={() => onFocus(activePanel.session.session_id)}
              onClose={() => onCloseSession(activePanel.session.session_id)}
            />
          ) : (
            <BrowserPane
              key={activePanel.panel.id}
              url={activePanel.panel.url}
              title={activePanel.panel.title}
              panelId={activePanel.panel.id}
              isFocused={true}
              isMaximized={false}
              onFocus={() => onFocus(activePanel.panel.id)}
              onMaximize={() => {}}
              onMinimize={() => {}}
              onRestore={() => {}}
              onClose={() => onCloseBrowser(activePanel.panel.id)}
            />
          )}
        </div>
        <TabBar
          sessions={activeSessions}
          activeSessionId={focused || ''}
          onSelect={onFocus}
        />
      </div>
    );
  }

  // Maximized view
  if (maximized && maximizedPanel) {
    const id = getPanelId(maximizedPanel);
    return (
      <div style={{ height: '100%', padding: GAP }}>
        {maximizedPanel.kind === 'terminal' ? (
          <TerminalPane
            key={id}
            ref={el => { paneRefs.current[id] = el; }}
            sessionName={maximizedPanel.session.name}
            sessionId={maximizedPanel.session.session_id}
            status={maximizedPanel.session.status}
            contextPct={maximizedPanel.session.context_remaining_pct}
            type={maximizedPanel.session.type}
            isMaximized={true}
            isFocused={true}
            onMaximize={() => {}}
            onMinimize={() => { onRestore(); onMinimize(id); }}
            onRestore={onRestore}
            onFocus={() => onFocus(id)}
            onClose={() => { onRestore(); onCloseSession(id); }}
          />
        ) : (
          <BrowserPane
            key={id}
            url={maximizedPanel.panel.url}
            title={maximizedPanel.panel.title}
            panelId={id}
            isFocused={true}
            isMaximized={true}
            onFocus={() => onFocus(id)}
            onMaximize={() => {}}
            onMinimize={() => { onRestore(); onMinimize(id); }}
            onRestore={onRestore}
            onClose={() => { onRestore(); onCloseBrowser(id); }}
          />
        )}
      </div>
    );
  }

  // Grid view — equal-sized auto-grid
  return (
    <div
      ref={containerRef}
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(auto-fit, minmax(${MIN_COL_WIDTH}px, 1fr))`,
        gridAutoRows: '1fr',
        gap: GAP,
        height: '100%',
        padding: GAP,
      }}
    >
      {orderedPanels.map((panel, index) => {
        const id = getPanelId(panel);
        const totalRows = Math.ceil(orderedPanels.length / numCols);
        const lastRowCount = orderedPanels.length % numCols || numCols;
        const col = index % numCols;
        const row = Math.floor(index / numCols);
        const itemsInCol = Math.floor(orderedPanels.length / numCols) + (col < lastRowCount ? 1 : 0);
        const isLastInCol = row === itemsInCol - 1;
        const span = isLastInCol && totalRows > 1 ? totalRows - row : 1;

        return (
          <div
            key={id}
            style={{
              minHeight: 0,
              gridRow: span > 1 ? `span ${span}` : undefined,
              opacity: dragSource === id ? 0.5 : 1,
              outline: dragOver === id && dragSource !== id ? '2px solid #a78bfa' : 'none',
              borderRadius: 4,
            }}
            draggable
            onDragStart={() => handleDragStart(id)}
            onDragEnter={() => handleDragEnter(id)}
            onDragOver={e => e.preventDefault()}
            onDragEnd={handleDragEnd}
          >
            {panel.kind === 'terminal' ? (
              <TerminalPane
                ref={el => { paneRefs.current[id] = el; }}
                sessionName={panel.session.name}
                sessionId={panel.session.session_id}
                status={panel.session.status}
                contextPct={panel.session.context_remaining_pct}
                type={panel.session.type}
                isMaximized={false}
                isFocused={focused === id}
                onMaximize={() => onMaximize(id)}
                onMinimize={() => onMinimize(id)}
                onRestore={() => {}}
                onFocus={() => { onFocus(id); paneRefs.current[id]?.focus(); }}
                onClose={() => onCloseSession(id)}
              />
            ) : (
              <BrowserPane
                url={panel.panel.url}
                title={panel.panel.title}
                panelId={id}
                isFocused={focused === id}
                isMaximized={false}
                onFocus={() => onFocus(id)}
                onMaximize={() => onMaximize(id)}
                onMinimize={() => onMinimize(id)}
                onRestore={() => {}}
                onClose={() => onCloseBrowser(id)}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
