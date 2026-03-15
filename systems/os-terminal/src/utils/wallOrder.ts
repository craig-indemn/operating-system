// Wall ordering: priority → status → recency
// User can drag-to-reorder within priority buckets (persisted to localStorage)

import type { HiveRecord } from '../types/hive';

const PRIORITY_ORDER: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
};

const STATUS_ORDER: Record<string, number> = {
  active: 0,
  'in-review': 1,
  ideating: 2,
  backlog: 3,
  done: 4,
  archived: 5,
};

const WALL_ORDER_KEY = 'hive-wall-order';

export function loadWallOrder(): string[] {
  try {
    const saved = localStorage.getItem(WALL_ORDER_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

export function saveWallOrder(order: string[]): void {
  localStorage.setItem(WALL_ORDER_KEY, JSON.stringify(order));
}

function getPriorityScore(record: HiveRecord): number {
  // Sessions always sort above everything else — they're active work
  if (record.type === 'session') return -1;
  return PRIORITY_ORDER[record.priority ?? ''] ?? 2; // default to medium
}

function getStatusScore(record: HiveRecord): number {
  return STATUS_ORDER[record.status ?? ''] ?? 2; // default to ideating
}

function getRecencyScore(record: HiveRecord): number {
  const ts = record.updated_at || record.created_at || '';
  return ts ? new Date(ts).getTime() : 0;
}

/**
 * Sort records for Wall display.
 * Primary: priority (critical first)
 * Secondary: status (active first)
 * Tertiary: recency (newest first)
 *
 * User-dragged order overrides within the same priority bucket.
 */
export function sortWallRecords(
  records: HiveRecord[],
  manualOrder: string[],
): HiveRecord[] {
  // If manual order exists, use it as a hint within priority groups
  const manualIndex = new Map(manualOrder.map((id, i) => [id, i]));

  return [...records].sort((a, b) => {
    // Priority first
    const pa = getPriorityScore(a);
    const pb = getPriorityScore(b);
    if (pa !== pb) return pa - pb;

    // Within same priority: check manual order
    const ma = manualIndex.get(a.record_id);
    const mb = manualIndex.get(b.record_id);
    if (ma !== undefined && mb !== undefined) {
      return ma - mb;
    }

    // Status second
    const sa = getStatusScore(a);
    const sb = getStatusScore(b);
    if (sa !== sb) return sa - sb;

    // Recency third (newest first)
    return getRecencyScore(b) - getRecencyScore(a);
  });
}

/**
 * Filter records for the compressed Wall view (when Focus has many panels).
 * Shows only active/attention items — not the full inventory.
 */
export function getHighlightReel(records: HiveRecord[]): HiveRecord[] {
  return records.filter(r => {
    const status = r.status ?? '';
    // Show active, in-review, critical/high priority regardless of status
    if (status === 'active' || status === 'in-review') return true;
    if (r.priority === 'critical' || r.priority === 'high') return true;
    // Show recently updated (within 24h) even if backlog/ideating
    const updated = r.updated_at || r.created_at;
    if (updated) {
      const age = Date.now() - new Date(updated).getTime();
      if (age < 24 * 60 * 60 * 1000) return true;
    }
    return false;
  });
}

/**
 * Reorder: swap two records within the manual order array.
 * Returns new order array.
 */
export function reorderWall(
  currentOrder: string[],
  allRecordIds: string[],
  sourceId: string,
  targetId: string,
): string[] {
  // Ensure all IDs are in the order array
  const order = [...currentOrder];
  for (const id of allRecordIds) {
    if (!order.includes(id)) order.push(id);
  }

  const srcIdx = order.indexOf(sourceId);
  const tgtIdx = order.indexOf(targetId);
  if (srcIdx >= 0 && tgtIdx >= 0) {
    // Swap positions
    [order[srcIdx], order[tgtIdx]] = [order[tgtIdx]!, order[srcIdx]!];
  }

  return order;
}
