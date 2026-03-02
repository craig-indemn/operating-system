import { Router } from 'express';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { readAllSessions, findById, findByName, getSessionCli } from '../state.js';

const exec = promisify(execFile);
const router = Router();

// GET /api/sessions — list all sessions
router.get('/', async (_req, res) => {
  const sessions = await readAllSessions();
  res.json(sessions);
});

// GET /api/sessions/by-name/:name — lookup by name (prefers active)
router.get('/by-name/:name', async (req, res) => {
  const sessions = await readAllSessions();
  const session = findByName(sessions, req.params.name);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }
  res.json(session);
});

// GET /api/sessions/:id — lookup by session_id
router.get('/:id', async (req, res) => {
  const sessions = await readAllSessions();
  const session = findById(sessions, req.params.id);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }
  res.json(session);
});

// POST /api/sessions — create a new session
router.post('/', async (req, res) => {
  const { name, addDirs, model, permissions } = req.body;
  if (!name) {
    res.status(400).json({ error: 'name is required' });
    return;
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
});

// DELETE /api/sessions/:id — close a session by session_id
// Resolves session_id to name for the CLI. Uses --non-interactive flag.
// Use ?force=true to destroy instead of close.
router.delete('/:id', async (req, res) => {
  const sessions = await readAllSessions();
  const session = findById(sessions, req.params.id);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
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
});

export default router;
