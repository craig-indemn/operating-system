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
**Status:** Approved (revised after design review) — ready for implementation planning

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

**Session CLI** — A Python script at `systems/session-manager/cli.py`. Wraps tmux + Claude Code CLI. Creates, lists, attaches, closes sessions. Both the EA and you use this directly. Uses shared utilities from `lib/`.

**Hooks** — Installed globally in `~/.claude/settings.json`. Every Claude Code session fires events that update its state file. Lightweight — just update status and append events. Target execution time: under 100ms per hook invocation.

**EA skill** — The intelligence layer at `.claude/skills/ea/SKILL.md`. Reads session state, calls the CLI, understands projects and context.

### Key Principles

1. **OS repo is home base.** Every session starts in an OS worktree. External repos (bot-service, platform-v2, etc.) are added via `--add-dir`. Sessions always inherit OS skills, CLAUDE.md, and conventions.

2. **File-per-session eliminates contention.** Multiple sessions writing hooks, multiple EAs reading state — no conflicts because each session only writes its own file. Atomic writes (temp file + rename) prevent corruption within a single session's file.

3. **tmux send-keys is the write mechanism.** Universal — works whether you're the EA, a script, or a human. No special IPC needed.

4. **The EA is not special.** It's a session like any other. When it hits context limits, a new EA session reads the same state files and picks up where the last one left off. The intelligence comes from state on disk, not context in memory.

5. **Don't reinvent what Claude Code already has.** Session transcripts, context tracking, task lists, Agent Teams messaging — all exist. We hook into them, not rebuild them.

6. **Scalable by design.** Multiple EAs can manage different project portfolios simultaneously. No shared mutable state between EAs — each reads the same state files independently.

---

## Session State File

Path: `sessions/{session-uuid}.json` in the OS repo root.

```json
{
  "version": 1,
  "session_id": "3168d79f-c3ca-4cfe-9a66-38086d9cd49a",
  "name": "voice-evaluations",
  "project": "voice-evaluations",
  "worktree_path": "/Users/home/Repositories/operating-system/.claude/worktrees/voice-evaluations",
  "tmux_session": "os-voice-evaluations",
  "status": "idle",
  "additional_dirs": [
    "/Users/home/Repositories/bot-service"
  ],
  "permissions": {
    "mode": "bypassPermissions"
  },
  "model": "opus",
  "created_at": "2026-03-01T10:00:00Z",
  "last_activity": "2026-03-01T10:45:00Z",
  "context_remaining_pct": 42,
  "git_branch": "os-voice-evaluations",
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
| `version` | Schema version (currently `1`). Allows future migrations. |
| `session_id` | Claude Code session UUID |
| `name` | Human-readable name (used for tmux, display, lookups) |
| `project` | OS project name (maps to `projects/<name>/`). Null if no project. |
| `worktree_path` | Absolute path to the OS worktree this session runs in |
| `tmux_session` | tmux session name for attach/send-keys |
| `status` | Derived from latest event: `active`, `idle`, `blocked`, `context_low`, `ended`, `ended_dirty` |
| `additional_dirs` | External repos accessible via `--add-dir` |
| `permissions` | Session permission configuration |
| `model` | Claude model in use |
| `created_at` | When session was created |
| `last_activity` | Timestamp of last activity |
| `context_remaining_pct` | Context window remaining (updated by context-tracking hook) |
| `git_branch` | Current git branch in the worktree |
| `events` | Append-only event log, capped at last 50 entries |

### Event Types

| Event | Trigger |
|-------|---------|
| `started` | Session created and Claude Code launched |
| `active` | User or EA sent a message |
| `idle` | Claude finished responding, waiting for input |
| `task_completed` | A Claude Code built-in task was marked complete (see Hooks section for limitations) |
| `blocked` | Session needs decision or external input |
| `context_low` | Context remaining dropped below 10% |
| `ended` | Session terminated cleanly (cleanup completed) |
| `ended_dirty` | Session terminated but cleanup failed or was skipped |

### Events Cap

The `events` array is capped at 50 entries. When a new event would exceed the cap, the oldest events are dropped. The full event history is not preserved — `status` and `last_activity` are the authoritative fields for current state. If full history is needed for analysis, Claude Code's own session transcript (JSONL) is the source of truth.

### Name-to-UUID Lookup

State files use UUID as filename (hooks receive UUID natively). The CLI finds sessions by name by scanning `sessions/*.json` — this is O(n) but n is always small (typically <20 active sessions). If this becomes a bottleneck, add an index file.

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

The CLI manages worktrees and tmux directly — it does NOT use `claude --worktree` or `claude --tmux`, because we need control over worktree placement, tmux session naming, and state file creation timing.

1. Generate a UUID for the session
2. Create git worktree: `git worktree add .claude/worktrees/<name> -b os-<name>` from OS repo root
3. Write initial state file: `sessions/{uuid}.json` with all metadata, status `"started"`
4. Create tmux session: `tmux new-session -d -s os-<name> -c <worktree-path>`
5. Inside tmux, launch Claude Code: `tmux send-keys -t os-<name> 'claude --session-id <uuid> --dangerously-skip-permissions --add-dir <dirs> --model <model>' Enter`
6. Session is live — hooks take over state updates

**Implementation note — `--session-id` verification required:** The design assumes that passing `--session-id <uuid>` causes Claude Code to use that UUID everywhere (session transcripts, hook input `session_id` field). This must be verified during implementation. If Claude Code ignores or overrides the provided UUID, the hook-to-state-file mapping breaks and an alternative approach is needed (e.g., the hook looks up the state file by matching `cwd` to `worktree_path` instead of by `session_id`).

**Why not `claude --worktree --tmux`?** That flag tells Claude Code to create its own worktree and tmux session. We need to create both ourselves because: (a) the state file must exist before hooks fire, (b) we need predictable tmux session names for `session attach` and `session send`, and (c) we pass `--session-id` so the hook script can find the state file by UUID.

**`--add-dir` sourcing:** When a project's INDEX.md lists external repos under External Resources with type "GitHub repo", the EA or CLI can read those to determine which `--add-dir` flags to pass. This is convention-based, not enforced — the user can always override with explicit flags.

### Close Flow

The close flow is defensive — it verifies each step before proceeding.

1. **Check session state.** Read the state file. If `active`, wait up to 30s for it to become `idle`. If still active, ask the user whether to interrupt or wait.
2. **Send cleanup commands individually via tmux send-keys:**
   - `session send <name> "Commit all changes with a descriptive message"`
   - Wait for idle (poll state file, timeout 60s)
   - `session send <name> "Push the current branch"`
   - Wait for idle
   - `session send <name> "Update the project INDEX.md with current status"`
   - Wait for idle
3. **Verify cleanup.** Check git status in the worktree (no uncommitted changes, branch is pushed).
4. **Exit Claude Code.** `tmux send-keys -t os-<name> '/exit' Enter`
5. **Wait for tmux session to end** (timeout 30s, then force-kill).
6. **Clean up worktree:**
   - If worktree has no uncommitted changes and no unpushed commits: `git worktree remove <path>`
   - If worktree has uncommitted or unpushed work: leave it, log a warning
7. **Update state file:**
   - If cleanup verified: `status: "ended"`
   - If cleanup failed or worktree retained: `status: "ended_dirty"` with reason in the final event

### Destroy Flow (Force Kill)

For when a session is unresponsive or you just want it gone:

1. `tmux kill-session -t os-<name>`
2. Update state file: `status: "ended_dirty"`, event: `{"type": "ended_dirty", "reason": "force_destroyed"}`
3. Do NOT auto-remove worktree — the user should inspect it first

---

## Hooks

Installed globally in `~/.claude/settings.json`. A single hook script handles all events — `systems/session-manager/hooks/update-state.py`. It receives event JSON on stdin, finds the session's state file, and updates it.

**Execution time target:** Under 100ms per invocation. Hooks run synchronously and block the session, so they must be fast. The script does a single file read, JSON update, and atomic write — nothing else.

**Coexistence with existing hooks:** These hooks are added alongside existing hooks (`bd prime` for SessionStart/PreCompact, GSD update check for SessionStart). Array settings merge across scopes, so both fire. The session manager hook should be fast enough that the user never notices it.

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
2. Determine OS repo root from `OS_ROOT` env var (set in `.env`, defaults to `/Users/home/Repositories/operating-system`). Scan `$OS_ROOT/sessions/*.json` for a file where `session_id` matches. Fallback: if no match by `session_id`, try matching by `cwd` against `worktree_path` (handles the case where `--session-id` is not honored).
3. If not found, exit silently (session wasn't created by our CLI — don't interfere with ad-hoc Claude Code sessions)
4. Update based on event:
   - `SessionStart` → set `status: "active"`, update `last_activity`
   - `Stop` → set `status: "idle"`, update `last_activity`
   - `UserPromptSubmit` → set `status: "active"`, update `last_activity`
   - `TaskCompleted` → append `task_completed` event, update `last_activity`
   - `SessionEnd` → set `status: "ended"` (unless already `ended_dirty`)
5. Append the event to the `events` array. If array exceeds 50 entries, drop the oldest.
6. **Atomic write:** Write to `sessions/{uuid}.json.tmp`, then `os.rename()` to `sessions/{uuid}.json`. This prevents corruption if two hooks fire in rapid succession — the last write wins, but the file is never half-written.

### TaskCompleted Hook Limitation

The `TaskCompleted` hook fires when Claude Code's **built-in task system** (`TaskUpdate` tool) marks a task as completed. It does NOT fire when external task tools are used (e.g., `bd close` for beads). This means:

- Sessions using Claude Code's built-in tasks: task events are tracked automatically
- Sessions using beads: task events are not tracked via this hook

This is acceptable for V1. If beads task tracking becomes important, a `PostToolUse` hook matching `Bash` could parse commands for `bd close` patterns, but this adds complexity. For now, `idle` and `active` status tracking (which IS reliable) provides sufficient visibility.

### Context Tracking

A dedicated context-tracking hook, separate from the existing GSD statusline script. We do NOT modify the GSD statusline — it belongs to a third-party plugin.

**Mechanism:** A custom statusline script (`update-context.py`) replaces the direct GSD statusline reference. It wraps the GSD script as a subprocess — calling `node /Users/home/.claude/hooks/gsd-statusline.js` internally — and adds context tracking on top. The statusline hook receives `context_window.remaining_percentage` on every render. Our script reads this, updates the state file's `context_remaining_pct`, and if it drops below 10%, appends a `context_low` event, then passes through the GSD statusline output.

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 /Users/home/Repositories/operating-system/systems/session-manager/hooks/update-context.py"
  }
}
```

The `update-context.py` script:
1. Reads JSON from stdin
2. Forwards stdin to GSD's `gsd-statusline.js` as a subprocess, captures its output
3. Extracts `context_window.remaining_percentage` from the input JSON
4. Updates the session's state file with `context_remaining_pct` (if a state file exists for this session)
5. If context drops below 10%, appends a `context_low` event
6. Outputs the GSD statusline result (or its own minimal status line if GSD is not installed)

**If future Claude Code versions support an array format for `statusLine`**, this wrapper can be simplified to two independent commands. Until then, the wrapper approach ensures both GSD and context tracking work.

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

### Permission Management

Default permission mode is `bypassPermissions` (dangerously skip permissions). This is appropriate for most sessions because Craig works in his own environment.

For sessions that touch production data or shared infrastructure, use `acceptEdits` instead:
```
session create production-debug --permissions acceptEdits --add-dir /path/to/prod-service
```

The EA should recommend `acceptEdits` when it detects a session targets a production-connected repo. This is advisory — the user decides.

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

## Dispatch System Boundary

The dispatch system (at `systems/dispatch/engine.py`) and the session manager serve different purposes:

| | EA Sessions (interactive) | Dispatch Sessions (headless) |
|---|---|---|
| **Created by** | Session CLI (`session create`) | Dispatch engine (`engine.py`) |
| **Runs in** | tmux pane, interactive | SDK `query()`, headless |
| **Lifecycle** | Long-lived, human-driven | Short-lived, task-driven |
| **State tracked in** | `sessions/{uuid}.json` | Dispatch engine's own state (beads epics) |
| **Visible to EA** | Yes | No (dispatch results flow through project artifacts) |

**Dispatch sessions do NOT get state files in `sessions/`.** They are invisible to the EA. The dispatch system is a separate tool that the EA can invoke (via the `/dispatch` skill), but once invoked, dispatch manages its own sessions internally.

Results from dispatch flow back into the OS through normal channels: project artifacts, beads task updates, git commits. The EA sees the outcomes, not the process.

If a future need arises to monitor dispatch sessions from the EA, a `"type": "dispatch"` field can be added to state files and the dispatch engine updated to write them. But for now, these are separate systems.

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
├── sessions/                          # Session state files (NEW, gitignored)
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
│           ├── update-state.py        # Hook script for state updates
│           └── update-context.py      # StatusLine hook for context tracking
│
├── lib/                               # Shared utilities (NEW)
│   └── os_state.py                    # Atomic JSON writes, state file reading/parsing
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

### Shared Library: `lib/os_state.py`

Both the session CLI and hooks need common operations:
- Atomic JSON file writes (temp file + `os.rename()`)
- Session state file reading/parsing
- Finding a state file by session ID or name
- Timestamp formatting

These live in `lib/os_state.py` to avoid duplication between `systems/session-manager/cli.py`, `hooks/update-state.py`, and `hooks/update-context.py`. The dispatch engine (`systems/dispatch/engine.py`) can also use these utilities if needed.

**Constraint: Hook scripts must use Python stdlib only.** Hooks fire for every Claude Code session on the machine, using whatever `python3` is on PATH. They cannot depend on packages installed in a venv. The `lib/os_state.py` module must also be stdlib-only (json, os, tempfile, pathlib, etc.). The session CLI (`cli.py`) can use venv packages since it's invoked explicitly.

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
EA: "Checking session state... it's idle, proceeding with cleanup."
    [sends commit command, waits for idle]
    [sends push command, waits for idle]
    [sends INDEX update command, waits for idle]
    [verifies git status is clean]
EA: "Changes committed and pushed. INDEX updated. Session closed. Worktree cleaned up."
```

### Close flow with issues

```
You: "Close up platform-dev"
EA: "Session is currently active — Claude is mid-response. Want me to wait for it
     to finish, or interrupt?"
You: "Wait"
EA: "Session went idle. Starting cleanup..."
    [sends commit, push, INDEX update — each verified]
EA: "Cleanup done but there are 2 unpushed commits on the worktree.
     Session marked as ended_dirty. Worktree preserved at
     .claude/worktrees/platform-dev — you may want to inspect it."
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
- 2026-03-01: CLI creates worktrees and tmux sessions manually (not `claude --worktree --tmux`) for naming control and state file timing
- 2026-03-01: Hooks update state files; CLI creates them — CLI writes metadata, hooks maintain runtime state
- 2026-03-01: Atomic writes (temp + rename) for all state file updates — prevents corruption from concurrent hooks
- 2026-03-01: Dedicated context-tracking hook separate from GSD statusline — don't modify third-party plugins
- 2026-03-01: EA is not immortal — it's a session like any other, reads state from disk on startup
- 2026-03-01: Manual triggers only for now — no auto-create, auto-close, or auto-compact
- 2026-03-01: Session CLI is usable directly by the human, not only through the EA
- 2026-03-01: Default permission mode is `bypassPermissions`; use `acceptEdits` for production-touching sessions
- 2026-03-01: Agent Teams messaging patterns should be adopted for inter-session communication (future)
- 2026-03-01: Voice, task unification, and Linear integration are future layers — designed separately
- 2026-03-01: Dispatch sessions are invisible to the EA — separate system, results flow through artifacts
- 2026-03-01: TaskCompleted hook only fires for Claude Code built-in tasks, not beads — acceptable for V1
- 2026-03-01: Events capped at 50 per session — full history lives in Claude Code transcripts
- 2026-03-01: Close flow is defensive — checks idle state, sends commands individually, verifies each step, marks `ended_dirty` on failure
- 2026-03-01: Shared `lib/os_state.py` for atomic writes, state parsing — used by CLI, hooks, and potentially dispatch
- 2026-03-01: Hook scripts must be stdlib-only — they run with system python3, not venv
- 2026-03-01: `sessions/` directory is gitignored — runtime state, not project knowledge
- 2026-03-01: Hook scripts use `OS_ROOT` env var for OS repo path — avoids hardcoding, set in `.env`
- 2026-03-01: StatusLine wrapper approach (subprocess to GSD) is the primary mechanism, not an array format
- 2026-03-01: `--session-id` flag behavior needs verification — fallback lookup by cwd-to-worktree_path matching

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| tmux | Installed | Standard on macOS via Homebrew |
| Claude Code CLI | v2.1.63 | Installed at `~/.local/bin/claude` |
| Python 3.12 | Installed | At `/Users/home/Repositories/.venv/bin/python3` |
| OS repo projects/ | Exists | Project structure already in use |
| Claude Code hooks | Available | 17 events, command type works for our needs |
| Git worktrees | Available | Native git feature, no extra tooling |

## References

- [Claude Code Internals (research artifact)](artifacts/2026-03-01-claude-code-internals.md)
- [Dispatch System Design (prior art)](artifacts/2026-02-19-dispatch-system-design.md)
- [Claude Code Hooks Docs](https://code.claude.com/docs/en/hooks)
- [Claude Code Agent SDK Docs](https://code.claude.com/docs/en/headless)
- [Claude Code Remote Control Docs](https://code.claude.com/docs/en/remote-control)
- [Claude Code Sessions Docs](https://code.claude.com/docs/en/sessions)
