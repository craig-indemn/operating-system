import { watch, mkdir } from 'fs/promises';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';
import type { WebSocketServer, WebSocket } from 'ws';
import { getOsRoot } from './state.js';

const exec = promisify(execFile);

const HIVE_PYTHON = '/Users/home/Repositories/.venv/bin/python3';

function getHiveCli(): string {
  return join(getOsRoot(), 'systems/hive/cli.py');
}

function getHiveVaultDir(): string {
  return join(getOsRoot(), 'hive');
}

/** Knowledge directories within the hive vault to watch for file changes */
const KNOWLEDGE_DIRS = ['notes', 'decisions', 'designs', 'research', 'sessions'];

const MAX_WATCHER_RETRIES = 10;
const POLL_INTERVAL_MS = 30_000;
const FILE_DEBOUNCE_MS = 500;
const CLI_TIMEOUT_MS = 15_000;

/**
 * Fetch recent records from the Hive CLI.
 * Returns parsed JSON array, or empty array on failure.
 */
async function fetchAllRecords(): Promise<unknown[]> {
  try {
    const { stdout } = await exec(
      HIVE_PYTHON,
      [getHiveCli(), 'recent', '30d', '--limit', '200', '--format', 'json'],
      { timeout: CLI_TIMEOUT_MS },
    );
    const parsed = JSON.parse(stdout);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    console.error('Hive CLI fetchAllRecords failed:', err);
    return [];
  }
}

/**
 * Fetch records from the last hour for change detection during polling.
 */
async function fetchRecentRecords(): Promise<unknown[]> {
  try {
    const { stdout } = await exec(
      HIVE_PYTHON,
      [getHiveCli(), 'recent', '1h', '--format', 'json'],
      { timeout: CLI_TIMEOUT_MS },
    );
    const parsed = JSON.parse(stdout);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    console.error('Hive CLI fetchRecentRecords failed:', err);
    return [];
  }
}

function broadcast(clients: Set<WebSocket>, records: unknown[]): void {
  const message = JSON.stringify({ type: 'hive_update', data: { records } });
  for (const client of clients) {
    if (client.readyState === client.OPEN) {
      client.send(message);
    }
  }
}

/**
 * Start watching a single knowledge directory for .md file changes.
 * Calls onChange when a markdown file is created, modified, or deleted.
 */
async function watchKnowledgeDir(
  dir: string,
  onChange: () => void,
  retryCount = 0,
): Promise<void> {
  // Ensure directory exists (first run or clean environment)
  await mkdir(dir, { recursive: true });

  try {
    const watcher = watch(dir, { recursive: false });
    for await (const event of watcher) {
      if (!event.filename?.endsWith('.md')) continue;
      onChange();
    }
  } catch (err) {
    console.error(`Hive watcher error for ${dir}:`, err);
    if (retryCount >= MAX_WATCHER_RETRIES) {
      console.error(`Hive watcher gave up on ${dir} after ${MAX_WATCHER_RETRIES} retries`);
      return;
    }
    // Exponential backoff: 5s, 10s, 20s, 40s, ...
    const delay = 5000 * Math.pow(2, retryCount);
    setTimeout(() => watchKnowledgeDir(dir, onChange, retryCount + 1), delay);
  }
}

export function initHiveHandler(wss: WebSocketServer): void {
  const clients = new Set<WebSocket>();

  // Track last poll fingerprint for change detection
  let lastPollFingerprint = '';

  wss.on('connection', (ws: WebSocket) => {
    clients.add(ws);
    ws.on('close', () => clients.delete(ws));
    ws.on('error', () => clients.delete(ws));

    // Listen for refresh requests from clients
    ws.on('message', (raw) => {
      try {
        const msg = JSON.parse(String(raw));
        if (msg.type === 'refresh') {
          fetchAllRecords()
            .then((records) => {
              if (ws.readyState === ws.OPEN) {
                ws.send(JSON.stringify({ type: 'hive_update', data: { records } }));
              }
            })
            .catch((err) => {
              console.error('Failed to handle hive refresh request:', err);
            });
        }
      } catch {
        // Ignore malformed messages (e.g. auth messages handled elsewhere)
      }
    });

    // Send initial state on connect
    fetchAllRecords()
      .then((records) => {
        if (ws.readyState === ws.OPEN) {
          ws.send(JSON.stringify({ type: 'hive_update', data: { records } }));
        }
      })
      .catch((err) => {
        console.error('Failed to send initial hive records:', err);
      });
  });

  // --- File watcher: knowledge directory changes ---

  // Trailing-edge debounce: accumulate file events, broadcast once after they settle
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;

  function onFileChange(): void {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      fetchAllRecords()
        .then((records) => broadcast(clients, records))
        .catch((err) => {
          console.error('Failed to broadcast hive records after file change:', err);
        });
    }, FILE_DEBOUNCE_MS);
  }

  const vaultDir = getHiveVaultDir();
  for (const subdir of KNOWLEDGE_DIRS) {
    const fullPath = join(vaultDir, subdir);
    watchKnowledgeDir(fullPath, onFileChange).catch((err) => {
      console.error(`Failed to start hive watcher for ${fullPath}:`, err);
    });
  }

  // --- Periodic poll: MongoDB entity changes ---

  function computeFingerprint(records: unknown[]): string {
    // Simple fingerprint: record count + latest updated_at timestamp
    let latestUpdated = '';
    for (const rec of records) {
      const r = rec as Record<string, unknown>;
      const updated = (r.updated_at as string) || '';
      if (updated > latestUpdated) {
        latestUpdated = updated;
      }
    }
    return `${records.length}:${latestUpdated}`;
  }

  const pollInterval = setInterval(() => {
    fetchRecentRecords()
      .then((recentRecords) => {
        const fingerprint = computeFingerprint(recentRecords);
        if (fingerprint !== lastPollFingerprint) {
          lastPollFingerprint = fingerprint;
          // Something changed — fetch the full record set and broadcast
          return fetchAllRecords().then((records) => broadcast(clients, records));
        }
      })
      .catch((err) => {
        console.error('Hive poll error:', err);
      });
  }, POLL_INTERVAL_MS);

  // Don't let the poll interval prevent process exit
  pollInterval.unref();
}
