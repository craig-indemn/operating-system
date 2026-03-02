import { readdir, readFile } from 'fs/promises';
import { join } from 'path';
import type { SessionState } from './types.js';

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

  const sessions: SessionState[] = [];
  for (const file of files) {
    if (!file.endsWith('.json')) continue;
    try {
      const content = await readFile(join(dir, file), 'utf-8');
      sessions.push(JSON.parse(content));
    } catch {
      // Skip corrupt or partially-written files
    }
  }
  return sessions;
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
