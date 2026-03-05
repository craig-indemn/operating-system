import { execFileSync } from 'child_process';

export const TMUX_PREFIX = 'os-';

/** Resolve tmux binary path — node-pty's posix_spawnp may not find it on PATH */
export function findTmux(): string {
  const candidates = ['/opt/homebrew/bin/tmux', '/usr/local/bin/tmux', '/usr/bin/tmux'];
  for (const candidate of candidates) {
    try {
      execFileSync(candidate, ['-V'], { timeout: 2000 });
      return candidate;
    } catch { /* try next */ }
  }
  return 'tmux'; // Fallback to PATH lookup
}

export const TMUX_BIN = findTmux();

/** Validate session name: only alphanumeric, hyphens, underscores, max 128 chars */
export function isValidSessionName(name: string): boolean {
  return name.length > 0 && name.length <= 128 && /^[a-zA-Z0-9_-]+$/.test(name);
}
