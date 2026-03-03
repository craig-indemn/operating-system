import { Router, Request, Response, NextFunction } from 'express';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { readAllSessions, findById, findByName, getSessionCli } from '../state.js';
import { isValidSessionName } from '../tmux.js';

const exec = promisify(execFile);
const router = Router();

const ALLOWED_MODELS = ['opus', 'sonnet', 'haiku'] as const;
const ALLOWED_PERMISSIONS = ['default', 'acceptEdits', 'bypassPermissions'] as const;

/** Wrap async route handlers so Express 4 catches rejections */
const asyncHandler = (fn: (req: Request, res: Response) => Promise<void>) =>
  (req: Request, res: Response, next: NextFunction) => fn(req, res).catch(next);

// GET /api/sessions — list all sessions
router.get('/', asyncHandler(async (_req, res) => {
  const sessions = await readAllSessions();
  res.json(sessions);
}));

// GET /api/sessions/by-name/:name — lookup by name (prefers active)
router.get('/by-name/:name', asyncHandler(async (req, res) => {
  const sessions = await readAllSessions();
  const session = findByName(sessions, req.params.name);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }
  res.json(session);
}));

// GET /api/sessions/:id — lookup by session_id
router.get('/:id', asyncHandler(async (req, res) => {
  const sessions = await readAllSessions();
  const session = findById(sessions, req.params.id);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }
  res.json(session);
}));

// POST /api/sessions — create a new session
router.post('/', asyncHandler(async (req, res) => {
  const { name, addDirs, model, permissions } = req.body;
  if (!name || typeof name !== 'string') {
    res.status(400).json({ error: 'name is required' });
    return;
  }
  if (!isValidSessionName(name)) {
    res.status(400).json({ error: 'Invalid session name (alphanumeric, hyphens, underscores, max 128 chars)' });
    return;
  }
  if (model && !ALLOWED_MODELS.includes(model)) {
    res.status(400).json({ error: `Invalid model. Allowed: ${ALLOWED_MODELS.join(', ')}` });
    return;
  }
  if (permissions && !ALLOWED_PERMISSIONS.includes(permissions)) {
    res.status(400).json({ error: `Invalid permissions. Allowed: ${ALLOWED_PERMISSIONS.join(', ')}` });
    return;
  }
  if (addDirs !== undefined) {
    if (!Array.isArray(addDirs) || !addDirs.every((d: unknown) => typeof d === 'string' && d.startsWith('/'))) {
      res.status(400).json({ error: 'addDirs must be an array of absolute paths' });
      return;
    }
  }

  const args = ['create', name];
  if (model) args.push('--model', model);
  if (permissions) args.push('--permissions', permissions);
  if (addDirs && Array.isArray(addDirs)) {
    for (const dir of addDirs) {
      args.push('--add-dir', dir);
    }
  }

  try {
    await exec('python3', [getSessionCli(), ...args], {
      env: { ...process.env },
      timeout: 30_000,
    });
    // Read back the created session
    const sessions = await readAllSessions();
    const session = findByName(sessions, name);
    res.status(201).json(session || { name, status: 'creating' });
  } catch (err: unknown) {
    const error = err as { stderr?: string; message?: string };
    res.status(500).json({ error: error.stderr || error.message });
  }
}));

// DELETE /api/sessions/:id — close a session by session_id
// Resolves session_id to name for the CLI. Uses --non-interactive flag.
// Use ?force=true to destroy instead of close.
router.delete('/:id', asyncHandler(async (req, res) => {
  const sessions = await readAllSessions();
  const session = findById(sessions, req.params.id);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }

  // Defense in depth — validate session name before passing to execFile
  if (!isValidSessionName(session.name)) {
    res.status(400).json({ error: 'Session has invalid name' });
    return;
  }

  const { force } = req.query;
  const command = force === 'true' ? 'destroy' : 'close';
  const args = [getSessionCli(), command, session.name];
  if (command === 'close') {
    args.push('--non-interactive');
  }

  try {
    await exec('python3', args, {
      env: { ...process.env },
      timeout: 180_000, // close flow sends 3 cleanup commands, each waits up to 60s
    });
    res.json({ status: 'closed' });
  } catch (err: unknown) {
    const error = err as { stderr?: string; message?: string };
    res.status(500).json({ error: error.stderr || error.message });
  }
}));

export default router;
