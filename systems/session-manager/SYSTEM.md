# Session Manager

Manages Claude Code sessions running in tmux, each scoped to a project in the OS repo. Creates worktrees for isolation, tracks session state via hooks, and provides a CLI for lifecycle management.

## Capabilities

- Create new Claude Code sessions in tmux with git worktree isolation
- List all active sessions with status, context usage, and project info
- Attach to sessions for direct interaction
- Send commands to sessions via tmux send-keys
- Close sessions with defensive cleanup (commit, push, update INDEX.md)
- Force-destroy unresponsive sessions

## Skills

| Skill | Purpose |
|-------|---------|
| `/sessions` | Intelligence layer — uses session CLI for orchestration |

## State

- **Session state files** — `sessions/{uuid}.json`, one per active session. Written by CLI at creation, updated by hooks during session life.
- **Hooks** — `update-state.py` (event tracking) and `update-context.py` (context window tracking) fire globally for all Claude Code sessions.

## Dependencies

- tmux — session multiplexer
- Claude Code CLI — `~/.local/bin/claude`
- Python 3.12+ (stdlib only for hooks, venv OK for CLI)
- Git — worktree management
- `lib/os_state.py` — shared utilities

## Integration Points

- **Reads from:** session state files, project INDEX.md
- **Produces:** tmux sessions running Claude Code, session state files
- **Reports to:** EA skill reads state files for briefings
