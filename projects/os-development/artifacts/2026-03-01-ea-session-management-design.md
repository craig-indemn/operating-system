---
ask: "Design the EA and session management architecture for the operating system — tmux-based Claude Code sessions, event-driven state tracking, switchboard EA, unified interface for all project work"
created: 2026-03-01
workstream: os-development
session: 2026-03-01-a
sources:
  - type: local-artifact
    ref: "projects/os-development/artifacts/2026-03-01-claude-code-internals.md"
    name: "Claude Code Internals research"
  - type: web
    ref: "https://code.claude.com/docs/en/hooks"
    name: "Claude Code Hooks Documentation"
  - type: web
    ref: "https://code.claude.com/docs/en/headless"
    name: "Claude Code Agent SDK Documentation"
  - type: web
    ref: "https://code.claude.com/docs/en/remote-control"
    name: "Claude Code Remote Control Documentation"
  - type: local-artifact
    ref: "projects/os-development/artifacts/2026-02-19-dispatch-system-design.md"
    name: "Dispatch System Design (prior art)"
---

# Design: EA & Session Management Architecture

**Date:** 2026-03-01
**Status:** Approved — ready for implementation planning

## Problem

The operating system is the brain behind all work — it has skills, projects, and connections to every tool. But today, each Claude Code session is isolated. There's no way to:
- See what sessions are running across projects
- Switch between sessions without manually finding tmux panes
- Have an intelligent assistant manage session lifecycle (create, monitor, clean up)
- Get a unified view of what's happening across all active work

The current workflow is: manually start Claude Code, manually remember which terminal is which, manually do cleanup when done. Context about active work lives in Craig's head, not in the system.

## Vision

An **Executive Assistant (EA)** that serves as the switchboard for all work. The EA manages Claude Code sessions running in tmux, each scoped to a project in the OS repo. The EA creates sessions, monitors their state, facilitates switching between them, and handles lifecycle ceremonies. You talk to individual sessions directly for project work; you talk to the EA for orchestration.

The system builds on Claude Code's existing infrastructure — session transcripts, hooks, tasks, Agent Teams — rather than replacing it. A thin integration layer connects what already exists.

---

## Architecture

### Four Components

```
You (human)
  |
  |--- directly attach to any tmux session
  |
  v
EA (Claude Code session with EA skill loaded)
  |
  |--- reads session state files
  |--- calls session CLI
  |--- sends commands via tmux send-keys
  |
  v
Session CLI (`session` command)
  |
  |--- creates/destroys tmux sessions
  |--- launches Claude Code with correct flags
  |--- writes initial state files
  |
  v
Session State Files (sessions/{uuid}.json)
  ^
  |--- hooks from each Claude Code session write events
  |
Individual Claude Code Sessions (each in own tmux pane + OS worktree)
  |
  |--- some may internally use Agent Teams (teammates within scope)
```

**Session state files** — `sessions/{uuid}.json`, one per active session. Written by the CLI at creation, updated by hooks during the session's life. Read by the EA and CLI.

**Session CLI** — A Python script at `systems/session-manager/cli.py`. Wraps tmux + Claude Code CLI. Creates, lists, attaches, closes sessions. Both the EA and you use this directly.

**Hooks** — Installed globally in `~/.claude/settings.json`. Every Claude Code session fires events that update its state file. Lightweight — just update status and append events.

**EA skill** — The intelligence layer at `.claude/skills/ea/SKILL.md`. Reads session state, calls the CLI, understands projects and context.

### Key Principles

1. **OS repo is home base.** Every session starts in an OS worktree. External repos (bot-service, platform-v2, etc.) are added via `--add-dir`. Sessions always inherit OS skills, CLAUDE.md, and conventions.

2. **File-per-session eliminates contention.** Multiple sessions writing hooks, multiple EAs reading state — no conflicts because each session only writes its own file.

3. **tmux send-keys is the write mechanism.** Universal — works whether you're the EA, a script, or a human. No special IPC needed.

4. **The EA is not special.** It's a session like any other. When it hits context limits, a new EA session reads the same state files and picks up where the last one left off. The intelligence comes from state on disk, not context in memory.

5. **Don't reinvent what Claude Code already has.** Session transcripts, context tracking, task lists, Agent Teams messaging — all exist. We hook into them, not rebuild them.

6. **Scalable by design.** Multiple EAs can manage different project portfolios simultaneously. No shared mutable state between EAs — each reads the same state files and claims sessions via `managed_by`.

---

## Session State File

Path: `sessions/{session-uuid}.json` in the OS repo root.

```json
{
  "session_id": "3168d79f-c3ca-4cfe-9a66-38086d9cd49a",
  "name": "voice-evaluations",
  "project": "voice-evaluations",
  "worktree": ".claude/worktrees/voice-evaluations",
  "tmux_session": "os-voice-evaluations",
  "status": "idle",
  "repo_cwd": "/Users/home/Repositories/operating-system",
  "additional_dirs": [
    "/Users/home/Repositories/bot-service"
  ],
  "permissions": {
    "mode": "bypassPermissions",
    "allowed_tools": [],
    "custom_rules": []
  },
  "model": "opus",
  "created_at": "2026-03-01T10:00:00Z",
  "last_activity": "2026-03-01T10:45:00Z",
  "context_remaining_pct": 42,
  "git_branch": "os-voice-evaluations",
  "managed_by": null,
  "events": [
    {"type": "started", "at": "2026-03-01T10:00:00Z"},
    {"type": "task_completed", "summary": "Transcript eval verified", "at": "2026-03-01T10:30:00Z"},
    {"type": "idle", "at": "2026-03-01T10:45:00Z"}
  ]
}
```

### Fields

| Field | Description |
|-------|-------------|
| `session_id` | Claude Code session UUID |
| `name` | Human-readable name (used for tmux, display) |
| `project` | OS project name (maps to `projects/<name>/`) |
| `worktree` | Path to the OS worktree this session runs in |
| `tmux_session` | tmux session name for attach/send-keys |
| `status` | Derived from latest event: `active`, `idle`, `blocked`, `context_low`, `ended` |
| `repo_cwd` | Always the OS repo (worktree path) |
| `additional_dirs` | External repos accessible via `--add-dir` |
| `permissions` | Session permission configuration |
| `model` | Claude model in use |
| `created_at` | When session was created |
| `last_activity` | Timestamp of last activity |
| `context_remaining_pct` | Context window remaining (updated by statusline hook) |
| `git_branch` | Current git branch in the worktree |
| `managed_by` | EA identifier if claimed, null if unclaimed |
| `events` | Append-only event log (capped, older events roll to history.jsonl if needed) |

### Event Types

| Event | Trigger |
|-------|---------|
| `started` | Session created and Claude Code launched |
| `active` | User or EA sent a message |
| `idle` | Claude finished responding, waiting for input |
| `task_completed` | A task was marked complete |
| `blocked` | Session needs decision or external input |
| `context_low` | Context remaining dropped below 10% |
| `ended` | Session terminated |

---

## Session CLI

Script: `systems/session-manager/cli.py`
Alias: `session` (configured in `.env` or shell profile)

### Commands

| Command | Description |
|---------|-------------|
| `session create <project> [flags]` | Create worktree, start tmux session, launch Claude Code, write state file |
| `session list` | List all active sessions: name, status, last activity, context %, project |
| `session attach <name>` | Attach terminal to tmux pane (direct interaction with Claude Code) |
| `session send <name> "message"` | Send message via tmux send-keys without attaching |
| `session status <name>` | Show detailed session state from state file |
| `session close <name>` | Send cleanup commands, wait for exit, mark as ended |
| `session destroy <name>` | Force-kill tmux session, clean up worktree, mark as ended |

### `session create` Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--add-dir <path>` | none | Additional repos to make accessible (repeatable) |
| `--model <model>` | opus | Claude model |
| `--permissions <mode>` | bypassPermissions | Permission mode |
| `--no-worktree` | false | Run in OS repo directly (no worktree isolation) |

### Create Flow

1. Create git worktree: `git worktree add .claude/worktrees/<project> -b os-<project>`
2. Write initial state file: `sessions/{uuid}.json` with all metadata
3. Create tmux session: `tmux new-session -d -s os-<project>`
4. Inside tmux, launch: `claude --worktree --dangerously-skip-permissions --add-dir <dirs> --model <model>`
5. Session is live — hooks take over state updates

### Close Flow

1. Send cleanup via `tmux send-keys`: commit changes, push, update INDEX.md
2. Send `/exit` to Claude Code
3. Wait for tmux session to end (or timeout and force-kill)
4. Clean up worktree if session made no uncommitted changes
5. Update state file: `status: "ended"`

---

## Hooks

Installed globally in `~/.claude/settings.json`. A single hook script handles all events — `systems/session-manager/hooks/update-state.py`. It receives event JSON on stdin, finds the session's state file, and updates it.

### Hook Configuration

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/home/Repositories/operating-system/systems/session-manager/hooks/update-state.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/home/Repositories/operating-system/systems/session-manager/hooks/update-state.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/home/Repositories/operating-system/systems/session-manager/hooks/update-state.py"
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/home/Repositories/operating-system/systems/session-manager/hooks/update-state.py"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/home/Repositories/operating-system/systems/session-manager/hooks/update-state.py"
          }
        ]
      }
    ]
  }
}
```

### Hook Script Logic

The script (`update-state.py`) does:

1. Read JSON from stdin — extract `session_id`, `hook_event_name`, `cwd`, `transcript_path`
2. Look for `sessions/{session_id}.json` in the OS repo
3. If not found, skip (session wasn't created by our CLI — don't interfere with ad-hoc Claude Code sessions)
4. Update based on event:
   - `SessionStart` → set `status: "active"`, update `last_activity`
   - `Stop` → set `status: "idle"`, update `last_activity`
   - `UserPromptSubmit` → set `status: "active"`, update `last_activity`
   - `TaskCompleted` → append `task_completed` event
   - `SessionEnd` → set `status: "ended"`
5. Write updated JSON back to the state file

### Context Tracking

Piggybacks on the existing **StatusLine hook** which already receives context window data on every render. We add a few lines to the statusline script to:
1. Write `context_remaining_pct` to the session's state file
2. If context drops below 10%, append a `context_low` event

This avoids adding another hook — the statusline already runs continuously.

---

## EA Skill

Path: `.claude/skills/ea/SKILL.md`

### Role

The EA is the management plane of the operating system. It reads session state, calls the session CLI, and understands projects. It orchestrates but does not do project work itself.

### Startup Behavior

On activation:
1. Run `session list` to see all active sessions
2. Read `projects/*/INDEX.md` status sections for projects without active sessions
3. Present a conversational briefing:

```
Here's where things stand:

ACTIVE SESSIONS
- voice-evaluations — idle for 20min, context 42% remaining
- platform-dev — active, working on scoring UI, context 78%

NO ACTIVE SESSION
- engineering-blog — last session ended yesterday, INDEX says draft needs review
- ringcentral — research complete, waiting on customer

NEEDS ATTENTION
- voice-evaluations session is idle — want to attach or close it up?

What would you like to work on?
```

### Capabilities

| Action | How |
|--------|-----|
| Create session | `session create <project> [flags]` |
| Show status | `session list` + read state files |
| Switch you to a session | Tell you the tmux attach command, or run `session attach` |
| Send command to session | `session send <name> "message"` |
| Close session | Send cleanup commands, then `session close <name>` |
| Modify session permissions | Update state file + send config commands to session |
| Add directory to session | Send appropriate commands via `session send` |
| Read session transcript | Read the JSONL file directly from `~/.claude/projects/` |

### What the EA Does NOT Do

- Project work (that's the session's job)
- Make decisions without your approval
- Automatically close or create sessions (manual triggers only, for now)
- Replace project-level skills (each session has its own skills)

### EA Continuity

The EA is a session like any other. When it hits context limits:
1. A new Claude Code session loads the EA skill
2. It reads `sessions/*.json` and `projects/*/INDEX.md`
3. It has the full picture immediately — no handoff ceremony needed
4. The previous EA session can be closed normally

The EA's intelligence comes from state on disk, not from accumulated context.

---

## Agent Teams Integration

The EA does NOT use Agent Teams internally. Agent Teams is a tool available to individual sessions.

### Relationship

```
EA (manages sessions)
  |
  v
Session A (standalone Claude Code)
Session B (team lead with 2 teammates via Agent Teams)
Session C (standalone Claude Code)
```

The EA can observe Agent Teams activity within a session by:
- Reading subagent transcripts at `~/.claude/projects/{path}/{session}/subagents/`
- Reading the team task list at `~/.claude/tasks/{team-name}/`

### Messaging Consistency

Future consideration: if we build inter-session messaging beyond tmux send-keys, we should use the same file-based patterns as Agent Teams (task lists, mailbox directories) rather than inventing a new protocol. This ensures:
- Sessions that use Agent Teams internally have consistent messaging
- The EA can read both intra-team and inter-session communications
- If Claude Code evolves Agent Teams, we evolve with it

---

## Directory Structure

```
operating-system/
├── sessions/                          # Session state files (NEW)
│   ├── {uuid}.json                    # One per active/recent session
│   └── archive/                       # Ended sessions (moved here by cleanup)
│
├── systems/
│   ├── dispatch/                      # Existing dispatch engine
│   │   ├── SYSTEM.md
│   │   └── engine.py
│   └── session-manager/               # Session management system (NEW)
│       ├── SYSTEM.md
│       ├── cli.py                     # The `session` command
│       └── hooks/
│           └── update-state.py        # Hook script for state updates
│
├── .claude/skills/
│   ├── ea/                            # EA skill (NEW, replaces content-system EA)
│   │   └── SKILL.md
│   └── ... (existing skills)
│
├── projects/                          # Existing project structure
│   ├── voice-evaluations/
│   ├── os-development/
│   └── ...
│
└── ... (existing files)
```

---

## Interaction Examples

### Starting a work session

```
You: "Let's work on voice evaluations"
EA: "No active session for voice-evaluations. Creating one..."
    [runs: session create voice-evaluations --add-dir /Users/home/Repositories/bot-service]
EA: "Session is up in tmux pane os-voice-evaluations, context at 100%.
     Last session ended 2 days ago. INDEX says transcript eval was verified,
     bug fixes committed. Want me to attach you?"
You: "Yeah"
    [runs: session attach voice-evaluations]
    -- you're now talking directly to the voice-evaluations Claude Code session --
```

### Checking in from the EA

```
You: "What's happening across my sessions?"
EA: "Three sessions active:
     - voice-evaluations: idle 15min, context 38% — might want to compact or close soon
     - platform-dev: active, last tool use was editing scoring-table.tsx
     - engineering-blog: idle 2hr, context 91% — just started, lots of room

     voice-evaluations is getting low on context. Want me to tell it to compact,
     or close it up?"
```

### Closing a session

```
You: "Close up voice-evals"
EA: "Sending cleanup commands..."
    [sends via tmux: update INDEX.md, commit, push]
EA: "Changes committed and pushed. Session closed. Worktree cleaned up."
```

### EA sending a command to a session

```
You: "Tell the platform-dev session to run the tests"
EA: [runs: session send platform-dev "Run the test suite for the scoring component"]
EA: "Message sent. I'll let you know when it goes idle."
```

---

## Future Work

### Task Layer (not designed yet)

Work tracking is currently fragmented: beads per-project, Claude Code tasks per-session, Linear for engineering work. A unified task layer should:
- Give the EA a single view of "what needs doing" across all sources
- Allow tasks to be created in conversation and tracked across sessions
- Integrate with Linear for engineering work without duplicating it
- Potentially align with Claude Code's built-in task system for consistency

### Voice Interface (not designed yet)

The ultimate interface: talk to the EA through voice and audio. Enables:
- Going for a run and managing work via headphones
- Voice-driven session switching ("switch me to platform work")
- EA reading briefings aloud
- Dictating commands and messages to sessions

Architecture sketch:
- Speech-to-text layer (Whisper or cloud STT)
- EA processes intent
- Text-to-speech layer for EA responses (ElevenLabs or similar)
- Mobile app or AirPods-style always-on interface
- The EA's session management capabilities don't change — voice is just a new input/output surface

### Linear Integration (not designed yet)

Linear tracks engineering work at the company level. The OS tracks work at the execution level. Integration should:
- Let the EA see Linear issues relevant to active projects
- Update Linear status when sessions complete related work
- Not duplicate — Linear is the source of truth for what to build, the OS is the source of truth for how it's being built

### Automation (not designed yet, manual-first)

Future automation possibilities once manual workflows are proven:
- Auto-create sessions when the EA detects unstarted work
- Auto-close idle sessions after configurable timeout
- Auto-compact sessions when context drops below threshold
- Auto-notify via Slack when sessions need attention
- Scheduled EA briefings (morning standup, end-of-day summary)

---

## Decisions Made

- 2026-03-01: EA is a switchboard, not a proxy — you talk to sessions directly for project work
- 2026-03-01: All sessions start in OS repo worktrees; external repos added via `--add-dir`
- 2026-03-01: File-per-session state model — eliminates write contention, scales to multiple EAs
- 2026-03-01: tmux send-keys is the universal write mechanism into sessions
- 2026-03-01: EA is not an Agent Teams lead — it's a layer above that manages sessions which may themselves use Agent Teams
- 2026-03-01: Hooks update state files; CLI creates them — CLI writes metadata, hooks maintain runtime state
- 2026-03-01: Context tracking piggybacks on existing StatusLine hook
- 2026-03-01: EA is not immortal — it's a session like any other, reads state from disk on startup
- 2026-03-01: Manual triggers only for now — no auto-create, auto-close, or auto-compact
- 2026-03-01: Session CLI is usable directly by the human, not only through the EA
- 2026-03-01: Default permission mode is `bypassPermissions` (dangerously skip permissions)
- 2026-03-01: Agent Teams messaging patterns should be adopted for inter-session communication (future)
- 2026-03-01: `managed_by` field enables multiple EAs managing different project portfolios
- 2026-03-01: Voice, task unification, and Linear integration are future layers — designed separately

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| tmux | Installed | Standard on macOS via Homebrew |
| Claude Code CLI | v2.1.63 | Installed at `~/.local/bin/claude` |
| Python 3.12 | Installed | At `/Users/home/Repositories/.venv/bin/python3` |
| OS repo projects/ | Exists | Project structure already in use |
| Claude Code hooks | Available | 17 events, command type works for our needs |
| StatusLine hook | Active | Already receives context window data |
| Git worktrees | Available | `--worktree` flag supported |

## References

- [Claude Code Internals (research artifact)](artifacts/2026-03-01-claude-code-internals.md)
- [Dispatch System Design (prior art)](artifacts/2026-02-19-dispatch-system-design.md)
- [Claude Code Hooks Docs](https://code.claude.com/docs/en/hooks)
- [Claude Code Agent SDK Docs](https://code.claude.com/docs/en/headless)
- [Claude Code Remote Control Docs](https://code.claude.com/docs/en/remote-control)
- [Claude Code Sessions Docs](https://code.claude.com/docs/en/sessions)
