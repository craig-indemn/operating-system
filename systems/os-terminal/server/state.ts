import { readdir, readFile } from 'fs/promises';
import { join } from 'path';
import { execFileSync } from 'child_process';
import type { SessionState } from './types.js';

// Resolve tmux binary path
function findTmux(): string {
  const candidates = ['/opt/homebrew/bin/tmux', '/usr/local/bin/tmux', '/usr/bin/tmux'];
  for (const candidate of candidates) {
    try {
      execFileSync(candidate, ['-V'], { timeout: 2000 });
      return candidate;
    } catch { /* try next */ }
  }
  return 'tmux';
}

const TMUX_BIN = findTmux();

/** Get set of currently live tmux session names */
function getLiveTmuxSessions(): Set<string> {
  try {
    const output = execFileSync(TMUX_BIN, ['list-sessions', '-F', '#{session_name}'], {
      timeout: 5000,
      encoding: 'utf-8',
    });
    return new Set(output.trim().split('\n').filter(Boolean));
  } catch {
    return new Set();
  }
}

export function getOsRoot(): string {
  const root = process.env.OS_ROOT;
  if (!root) {
    throw new Error('OS_ROOT environment variable is not set. Set it in .env or export it before starting the server.');
  }
  return root;
}

export function getSessionsDir(): string {
  return join(getOsRoot(), 'sessions');
}

export function getSessionCli(): string {
  return join(getOsRoot(), 'systems/session-manager/cli.py');
}

export async function readAllSessions(): Promise<SessionState[]> {
  const dir = getSessionsDir();
  let files: string[];
  try {
    files = await readdir(dir);
  } catch {
    return [];
  }

  const liveTmux = getLiveTmuxSessions();

  const allSessions: SessionState[] = [];
  for (const file of files) {
    if (!file.endsWith('.json')) continue;
    try {
      const content = await readFile(join(dir, file), 'utf-8');
      const session: SessionState = JSON.parse(content);

      // Cross-reference with tmux: if state says ended but tmux is alive,
      // the session is still running (state file went stale)
      if (['ended', 'ended_dirty', 'stale'].includes(session.status)) {
        if (liveTmux.has(session.tmux_session)) {
          session.status = 'active';
        }
      }

      allSessions.push(session);
    } catch {
      // Skip corrupt or partially-written files
    }
  }

  // Deduplicate: keep only the most recent state file per tmux session.
  // Multiple state files for the same tmux session happen when sessions
  // are recreated without cleaning up old state files.
  const byTmux = new Map<string, SessionState>();
  for (const s of allSessions) {
    const existing = byTmux.get(s.tmux_session);
    if (!existing || new Date(s.last_activity) > new Date(existing.last_activity)) {
      byTmux.set(s.tmux_session, s);
    }
  }
  return Array.from(byTmux.values());
}

/**
 * Find a session by session_id. Returns the first match.
 */
export function findById(sessions: SessionState[], id: string): SessionState | undefined {
  return sessions.find(s => s.session_id === id);
}

/**
 * Find a session by name. Prefers active sessions over ended ones.
 * Returns undefined if no match.
 */
export function findByName(sessions: SessionState[], name: string): SessionState | undefined {
  const matches = sessions.filter(s => s.name === name);
  if (matches.length === 0) return undefined;
  // Prefer non-ended sessions
  const active = matches.find(s => !['ended', 'ended_dirty'].includes(s.status));
  return active || matches[0];
}
