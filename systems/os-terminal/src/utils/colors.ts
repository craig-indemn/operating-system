// Hive Visual Design System — Color Maps
// Source: projects/os-development/artifacts/2026-03-15-hive-ui-visual-design.md

// --- Background Palette (Zinc-based) ---
export const BG = {
  base: '#09090b',     // zinc-950 — page bg, done tiles recede
  surface: '#18181b',  // zinc-900 — standard tile bg, panels
  lifted: '#1f1f23',   // zinc-850 — active tile bg
  sunken: '#131316',   // zinc-925 — backlog tile bg
  border: '#27272a',   // zinc-800 — borders, menus
} as const;

export const TEXT = {
  primary: '#f4f4f5',   // zinc-100
  secondary: '#a1a1aa', // zinc-400
  muted: '#71717a',     // zinc-500
} as const;

// --- Type → Color Map ---
// Each type gets a saturated color for its badge pill.
// Badge rendering: 15% opacity bg, full saturated text, Geist Mono 11px uppercase.
export const TYPE_COLORS: Record<string, string> = {
  // Core entities
  person: '#8b5cf6',        // Violet
  company: '#6366f1',       // Indigo
  project: '#94a3b8',       // Steel
  product: '#06b6d4',       // Cyan
  workflow: '#0ea5e9',      // Sky
  meeting: '#ec4899',       // Pink
  brand: '#f43f5e',         // Rose
  platform: '#64748b',      // Slate
  channel: '#14b8a6',       // Teal
  // Synced entities
  linear_issue: '#a855f7',  // Purple
  calendar_event: '#d946ef',// Fuchsia
  github_pr: '#22c55e',     // Green
  slack_message: '#10b981', // Emerald
  // Knowledge tags (first tag determines color)
  decision: '#f59e0b',      // Amber
  design: '#f97316',        // Orange
  research: '#84cc16',      // Lime
  note: '#a1a1aa',          // Zinc
  session_summary: '#38bdf8',// Sky
  feedback: '#eab308',      // Yellow
  context_assembly: '#38bdf8',// Sky
  // Sessions (custom)
  session: '#60a5fa',       // Blue
};

// --- Domain → Accent Color Map ---
// 3px left bar on tiles. Brightness tracks status.
export const DOMAIN_COLORS: Record<string, string> = {
  indemn: '#a78bfa',          // Lilac
  'career-catalyst': '#3b82f6',// Blue
  personal: '#d97706',        // Honey/Amber
};

// Default accent for unknown domains
export const DEFAULT_DOMAIN_COLOR = '#525252'; // zinc-600

// --- Session Status → Color Map ---
// Session tiles use these for their accent bar instead of domain colors.
export const SESSION_STATUS_COLORS: Record<string, string> = {
  started: '#3b82f6',      // Blue — fresh session, waiting
  active: '#22c55e',       // Green — recently used, working
  idle: '#f59e0b',         // Amber — not used recently
  context_low: '#ef4444',  // Red — running out of context window
};

// --- Status → Visual Mapping ---
export interface StatusVisuals {
  bg: string;
  accentOpacity: number;
  textColor: string;
}

export const STATUS_VISUALS: Record<string, StatusVisuals> = {
  active: { bg: BG.lifted, accentOpacity: 1.0, textColor: TEXT.primary },
  ideating: { bg: BG.surface, accentOpacity: 0.7, textColor: TEXT.primary },
  'in-review': { bg: BG.surface, accentOpacity: 0.7, textColor: TEXT.primary },
  backlog: { bg: BG.sunken, accentOpacity: 0.4, textColor: TEXT.secondary },
  done: { bg: BG.base, accentOpacity: 0.15, textColor: TEXT.muted },
  archived: { bg: BG.base, accentOpacity: 0.1, textColor: TEXT.muted },
};

// Default for unknown statuses
const DEFAULT_VISUALS: StatusVisuals = {
  bg: BG.surface,
  accentOpacity: 0.7,
  textColor: TEXT.primary,
};

export function getStatusVisuals(status: string): StatusVisuals {
  return STATUS_VISUALS[status] ?? DEFAULT_VISUALS;
}

// --- Helpers ---

export function getTypeColor(type: string, tags?: string[]): string {
  // For knowledge records, use the first tag's color
  if (type === 'knowledge' && tags?.length) {
    for (const tag of tags) {
      const color = TYPE_COLORS[tag];
      if (color) return color;
    }
  }
  return TYPE_COLORS[type] ?? TYPE_COLORS.note!;
}

export function getDomainColor(domains?: string[]): string {
  if (!domains?.length) return DEFAULT_DOMAIN_COLOR;
  const first = domains[0]!;
  return DOMAIN_COLORS[first] ?? DEFAULT_DOMAIN_COLOR;
}

/** Convert hex color to rgba with given opacity */
export function hexToRgba(hex: string, opacity: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

/** Format relative time from ISO string */
export function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return `${Math.floor(days / 30)}mo ago`;
}
