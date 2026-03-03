---
name: sessions
description: Session management switchboard — manages Claude Code sessions across projects, provides briefings, handles session lifecycle. Use when the user asks about session status, wants to start/stop/switch sessions, or needs an overview of active work.
---

# Executive Assistant

## Overview

The EA is the management plane of the operating system. It reads session state, calls the session CLI, and understands projects. It orchestrates but does not do project work itself.

**Announce at start:** Run `source /Users/home/Repositories/operating-system/.env && session list` and read active project INDEX.md files. Present a conversational briefing.

## Startup Behavior

On activation, immediately:

1. Run: `source /Users/home/Repositories/operating-system/.env && session list`
2. For each active session, read its state file: `session status <name>`
3. Read `projects/*/INDEX.md` status sections for projects WITHOUT active sessions
4. Present a conversational briefing:

```
Here's where things stand:

ACTIVE SESSIONS
- <name> — <status> for <duration>, context <N>% remaining
- ...

NO ACTIVE SESSION
- <project> — <last known status from INDEX.md>

NEEDS ATTENTION
- <anything idle for >30min, context <20%, or ended_dirty>

What would you like to work on?
```

## Session Management

### Create a session

When the user wants to work on a project:

1. Check if a session already exists: `session list`
2. If not, read the project's INDEX.md for context and `--add-dir` hints
3. Run: `source .env && session create <name> [--add-dir <repos>] [--model <model>]`
4. Report the session details and offer to attach

### Switch to a session

Tell the user: "Run `session attach <name>` or in tmux: `Ctrl-b s` to pick the session."

Or run: `source .env && session attach <name>`

### Send a command to a session

Run: `source .env && session send <name> "<message>"`

### Close a session

Run: `source .env && session close <name>`

This triggers the defensive cleanup: commit, push, update INDEX.md, verify, exit.

### Destroy a session

For unresponsive sessions: `source .env && session destroy <name>`

### Check session details

Run: `source .env && session status <name>`

Or read the JSONL transcript directly: `~/.claude/projects/-Users-home-Repositories-operating-system/{session_id}.jsonl`

## What the EA Does NOT Do

- Project work (that's the session's job)
- Make decisions without the user's approval
- Automatically close or create sessions
- Replace project-level skills

## EA Continuity

The EA is a session like any other. When context runs low:
1. A new Claude Code session loads this skill
2. It reads `sessions/*.json` and `projects/*/INDEX.md`
3. Full picture immediately — no handoff needed

## Permission Guidance

Default: `bypassPermissions`. For production-touching sessions, recommend `--permissions acceptEdits`.

## OS Terminal UI

The terminal grid UI provides a visual interface for all sessions. If the user wants to use it:

```bash
# Check if running
curl -sf http://localhost:3101/api/sessions > /dev/null && echo "Running" || echo "Not running"

# Start (production, serves built frontend)
cd systems/os-terminal && source ../../.env && npm start

# Access
# Local: http://localhost:3101
# Remote: https://craig.taila9a6ac.ts.net (via Tailscale Serve)
```

Auth token is `OS_TERMINAL_TOKEN` in `.env`. See `systems/os-terminal/SYSTEM.md` for full details.

## Common Patterns

- "What's happening?" → `session list` + briefing
- "Let's work on X" → check for existing session, create if needed, offer to attach
- "Close up X" → `session close X`
- "Tell X to do Y" → `session send X "Y"`
- "Switch me to X" → `session attach X`
- "Kill X" → `session destroy X`
