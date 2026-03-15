import { Router, Request, Response, NextFunction } from 'express';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';
import { access, constants } from 'fs/promises';
import { getOsRoot } from '../state.js';

const exec = promisify(execFile);
const router = Router();

/** Wrap async route handlers so Express 4 catches rejections */
const asyncHandler = (fn: (req: Request, res: Response) => Promise<void>) =>
  (req: Request, res: Response, next: NextFunction) => fn(req, res).catch(next);

function getHiveCli(): string {
  // The hive CLI lives at systems/hive/cli.py relative to OS_ROOT
  return join(getOsRoot(), 'systems/hive/cli.py');
}

function getHivePython(): string {
  // Use the venv python that has hive dependencies
  return '/Users/home/Repositories/.venv/bin/python3';
}

/** Cache for CLI existence check — avoid stat on every request */
let cliExistsChecked = false;
let cliExists = false;

async function ensureCliExists(): Promise<void> {
  if (cliExistsChecked) {
    if (!cliExists) {
      throw new CliNotFoundError();
    }
    return;
  }
  try {
    await access(getHiveCli(), constants.R_OK);
    cliExists = true;
  } catch {
    cliExists = false;
    throw new CliNotFoundError();
  } finally {
    cliExistsChecked = true;
  }
}

class CliNotFoundError extends Error {
  constructor() {
    super('Hive CLI not found');
    this.name = 'CliNotFoundError';
  }
}

/**
 * Run a hive CLI command and parse JSON output.
 * The hive CLI auto-detects non-TTY and outputs JSON when piped.
 */
async function runHive(args: string[], timeout = 15_000): Promise<unknown> {
  await ensureCliExists();

  try {
    const { stdout } = await exec(getHivePython(), [getHiveCli(), ...args], {
      env: { ...process.env },
      timeout,
    });

    const trimmed = stdout.trim();
    if (!trimmed) {
      return {};
    }

    try {
      return JSON.parse(trimmed);
    } catch {
      // CLI produced non-JSON output — return as message
      return { message: trimmed };
    }
  } catch (err: unknown) {
    const error = err as { code?: string; stderr?: string; message?: string; killed?: boolean };

    if (error.killed) {
      const timeoutErr = new Error('Hive CLI timed out') as Error & { statusCode: number };
      timeoutErr.statusCode = 504;
      throw timeoutErr;
    }

    // Try to parse stderr for a structured error message
    const stderr = error.stderr?.trim() || '';
    const message = stderr || error.message || 'Hive CLI error';

    const cliErr = new Error(message) as Error & { statusCode: number };
    cliErr.statusCode = 500;
    throw cliErr;
  }
}

/**
 * Collect defined query params into CLI flag arrays.
 * Skips undefined/empty values. Handles both --flag value and --flag patterns.
 */
function queryToFlags(
  query: Record<string, unknown>,
  mapping: Record<string, string>,
): string[] {
  const flags: string[] = [];
  for (const [param, flag] of Object.entries(mapping)) {
    const value = query[param];
    if (value !== undefined && value !== '' && value !== null) {
      flags.push(flag, String(value));
    }
  }
  return flags;
}

// ---------------------------------------------------------------------------
// GET /records — List records by type/tag, or recent activity if none specified
// ---------------------------------------------------------------------------
router.get('/records', asyncHandler(async (req, res) => {
  const { type, tag, recent } = req.query;

  // If no type or tag specified, return recent activity feed
  if (!type && !tag) {
    const args = ['recent'];
    if (recent && typeof recent === 'string') args.push(recent);
    const flags = queryToFlags(
      req.query as Record<string, unknown>,
      { domain: '--domains', limit: '--limit' },
    );
    args.push('--format', 'json', ...flags);
    const data = await runHive(args);
    res.json(data);
    return;
  }

  // hive list <type-or-tag>
  const typeOrTag = (type || tag) as string;
  const args = ['list', typeOrTag];
  const flags = queryToFlags(
    req.query as Record<string, unknown>,
    {
      status: '--status',
      domain: '--domain',
      recent: '--recent',
      limit: '--limit',
      refsTo: '--refs-to',
    },
  );
  args.push('--format', 'json', ...flags);

  const data = await runHive(args);
  res.json(data);
}));

// ---------------------------------------------------------------------------
// GET /search — Semantic + keyword search
// ---------------------------------------------------------------------------
router.get('/search', asyncHandler(async (req, res) => {
  const { q, knowledgeOnly, entitiesOnly } = req.query;

  if (!q || typeof q !== 'string') {
    res.status(400).json({ error: 'Query parameter "q" is required' });
    return;
  }

  const args = ['search', q];
  const flags = queryToFlags(
    req.query as Record<string, unknown>,
    {
      tags: '--tags',
      domains: '--domains',
      types: '--types',
      recent: '--recent',
      limit: '--limit',
    },
  );

  if (knowledgeOnly === 'true') flags.push('--knowledge-only');
  if (entitiesOnly === 'true') flags.push('--entities-only');

  args.push('--format', 'json', ...flags);

  // Search can be slow due to embedding lookups
  const data = await runHive(args, 30_000);
  res.json(data);
}));

// ---------------------------------------------------------------------------
// GET /recent — Recent activity feed
// ---------------------------------------------------------------------------
router.get('/recent', asyncHandler(async (req, res) => {
  const { duration } = req.query;

  const args = ['recent'];
  if (duration && typeof duration === 'string') args.push(duration);

  const flags = queryToFlags(
    req.query as Record<string, unknown>,
    {
      types: '--types',
      domains: '--domains',
      limit: '--limit',
    },
  );
  args.push('--format', 'json', ...flags);

  const data = await runHive(args);
  res.json(data);
}));

// ---------------------------------------------------------------------------
// GET /registry/types — List entity types
// ---------------------------------------------------------------------------
router.get('/registry/types', asyncHandler(async (_req, res) => {
  const data = await runHive(['types', 'list', '--format', 'json']);
  res.json(data);
}));

// ---------------------------------------------------------------------------
// GET /registry/tags — List tags
// ---------------------------------------------------------------------------
router.get('/registry/tags', asyncHandler(async (_req, res) => {
  const data = await runHive(['tags', 'list', '--format', 'json']);
  res.json(data);
}));

// ---------------------------------------------------------------------------
// GET /status — System overview
// ---------------------------------------------------------------------------
router.get('/status', asyncHandler(async (_req, res) => {
  const data = await runHive(['status', '--format', 'json']);
  res.json(data);
}));

// ---------------------------------------------------------------------------
// GET /records/:id/refs — Get references for a record
// ---------------------------------------------------------------------------
router.get('/records/:id/refs', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const args = ['refs', id];

  const flags = queryToFlags(
    req.query as Record<string, unknown>,
    {
      direction: '--direction',
      depth: '--depth',
      types: '--types',
      tags: '--tags',
      recent: '--recent',
    },
  );
  args.push('--format', 'json', ...flags);

  const data = await runHive(args);
  res.json(data);
}));

// ---------------------------------------------------------------------------
// GET /records/:id — Get single record by ID
// ---------------------------------------------------------------------------
router.get('/records/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;

  const data = await runHive(['get', id, '--format', 'json']);

  // If the CLI returns an error-like object, treat as 404
  if (data && typeof data === 'object' && 'error' in (data as Record<string, unknown>)) {
    res.status(404).json(data);
    return;
  }

  res.json(data);
}));

// ---------------------------------------------------------------------------
// POST /records — Create a record
// ---------------------------------------------------------------------------
router.post('/records', asyncHandler(async (req, res) => {
  const { type, title, domains, tags, refs, status, ...extraFields } = req.body;

  if (!type || typeof type !== 'string') {
    res.status(400).json({ error: '"type" is required' });
    return;
  }
  if (!title || typeof title !== 'string') {
    res.status(400).json({ error: '"title" is required' });
    return;
  }

  const args = ['create', type, title];

  if (domains) {
    if (Array.isArray(domains)) {
      args.push('--domains', domains.join(','));
    } else if (typeof domains === 'string') {
      args.push('--domains', domains);
    }
  }

  if (tags) {
    if (Array.isArray(tags)) {
      args.push('--tags', tags.join(','));
    } else if (typeof tags === 'string') {
      args.push('--tags', tags);
    }
  }

  if (refs && typeof refs === 'object' && !Array.isArray(refs)) {
    // Convert { project: "hive", people: ["craig"] } to "project:hive,people:craig"
    const refParts: string[] = [];
    for (const [key, value] of Object.entries(refs)) {
      if (Array.isArray(value)) {
        for (const v of value) {
          refParts.push(`${key}:${v}`);
        }
      } else {
        refParts.push(`${key}:${value}`);
      }
    }
    if (refParts.length > 0) {
      args.push('--refs', refParts.join(','));
    }
  }

  if (status && typeof status === 'string') {
    args.push('--status', status);
  }

  // Pass extra fields as --field value flags
  for (const [field, value] of Object.entries(extraFields)) {
    if (value !== undefined && value !== null) {
      args.push(`--${field}`, String(value));
    }
  }

  args.push('--format', 'json');

  const data = await runHive(args);
  res.status(201).json(data);
}));

// ---------------------------------------------------------------------------
// PATCH /records/:id — Update a record
// ---------------------------------------------------------------------------
router.patch('/records/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { status, addTags, addRefs, ...fields } = req.body;

  const args = ['update', id];

  if (status && typeof status === 'string') {
    args.push('--status', status);
  }

  if (addTags) {
    if (Array.isArray(addTags)) {
      args.push('--add-tags', addTags.join(','));
    } else if (typeof addTags === 'string') {
      args.push('--add-tags', addTags);
    }
  }

  if (addRefs && typeof addRefs === 'object' && !Array.isArray(addRefs)) {
    const refParts: string[] = [];
    for (const [key, value] of Object.entries(addRefs)) {
      if (Array.isArray(value)) {
        for (const v of value) {
          refParts.push(`${key}:${v}`);
        }
      } else {
        refParts.push(`${key}:${value}`);
      }
    }
    if (refParts.length > 0) {
      args.push('--add-refs', refParts.join(','));
    }
  }

  // Pass remaining fields as --field value flags
  for (const [field, value] of Object.entries(fields)) {
    if (value !== undefined && value !== null) {
      args.push(`--${field}`, String(value));
    }
  }

  args.push('--format', 'json');

  const data = await runHive(args);
  res.json(data);
}));

// ---------------------------------------------------------------------------
// Error-handling middleware specific to hive routes
// ---------------------------------------------------------------------------
router.use((err: Error & { statusCode?: number }, _req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof CliNotFoundError) {
    res.status(503).json({ error: 'Hive CLI is not available' });
    return;
  }

  const status = err.statusCode || 500;
  res.status(status).json({ error: err.message || 'Hive API error' });
});

export default router;
