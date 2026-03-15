// Hive record types shared between hooks and components

export interface HiveRecord {
  record_id: string;
  type: string;          // entity type or 'knowledge'
  title?: string;        // knowledge records
  name?: string;         // entity records
  tags?: string[];
  domains?: string[];
  status?: string;
  priority?: string;
  system?: string;       // synced record source system
  ref?: string;          // external artifact pointer
  refs_out?: Record<string, string[]>;
  content?: string;      // knowledge body (truncated)
  created_at?: string;
  updated_at?: string;
  // Workflow-specific
  objective?: string;
  current_context?: string;
  // Meeting-specific
  date?: string;
  // Extra fields
  [key: string]: unknown;
}

export function getRecordLabel(record: HiveRecord): string {
  return record.title || record.name || record.record_id;
}

export function getRecordType(record: HiveRecord): string {
  // For knowledge records, return the primary tag for color lookup
  if (record.type === 'knowledge' && record.tags?.length) {
    return record.tags[0]!;
  }
  return record.type;
}

export function getConnectionCount(record: HiveRecord): number {
  if (!record.refs_out) return 0;
  return Object.values(record.refs_out).reduce((sum, refs) => sum + refs.length, 0);
}
