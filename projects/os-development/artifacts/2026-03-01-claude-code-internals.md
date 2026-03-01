---
ask: "Document how Claude Code works on our local system — sessions, hooks, state, Agent Teams, SDK — as foundation for building the EA session management layer"
created: 2026-03-01
workstream: os-development
session: 2026-03-01-a
sources:
  - type: local-filesystem
    description: "Full exploration of ~/.claude/ directory structure, settings, sessions, hooks, plugins"
  - type: web
    ref: "https://code.claude.com/docs/en/hooks"
    name: "Claude Code Hooks Documentation"
  - type: web
    ref: "https://code.claude.com/docs/en/cli-reference"
    name: "Claude Code CLI Reference"
  - type: web
    ref: "https://code.claude.com/docs/en/sub-agents"
    name: "Claude Code Sub-Agents Documentation"
  - type: web
    ref: "https://code.claude.com/docs/en/headless"
    name: "Claude Code Headless / Agent SDK Documentation"
  - type: web
    ref: "https://code.claude.com/docs/en/settings"
    name: "Claude Code Settings Documentation"
  - type: web
    ref: "https://code.claude.com/docs/en/sessions"
    name: "Claude Code Sessions Documentation"
  - type: web
    ref: "https://code.claude.com/docs/en/remote-control"
    name: "Claude Code Remote Control Documentation"
---

# Claude Code Internals: How It Works on Our System

Reference documentation for building the EA session management layer. Everything here is verified against our local system (v2.1.63) and Anthropic's official docs.

---

## 1. Filesystem Layout

All state lives under `~/.claude/` (user-level) and `<project>/.claude/` (project-level). No SQLite databases — everything is flat files (JSON, JSONL, Markdown, plain text). Total size on our system: ~1.3 GB.

### Critical Paths

| Path | Purpose | Size |
|------|---------|------|
| `~/.claude/projects/{sanitized-path}/{session-uuid}.jsonl` | Session transcripts | 810 MB total |
| `~/.claude/settings.json` | User permissions, hooks, plugins, status line | 8.8 KB |
| `~/.claude/history.jsonl` | Global append-only log of every user message | 1.9 MB (6,349 entries) |
| `~/.claude/tasks/{session-uuid}/` | Structured task lists with dependencies | Per-session |
| `~/.claude/todos/{session-uuid}-agent-{id}.json` | Task tracking per agent | Per-session |
| `~/.claude/file-history/{session-uuid}/` | Versioned backups of edited files | 23 MB total |
| `~/.claude/plans/{creative-name}.md` | Execution plans | Per-session |
| `~/.claude/debug/{session-uuid}.txt` | Debug logs | 525 MB total |
| `~/.claude/stats-cache.json` | Usage stats: daily activity, token counts, session counts | 10 KB |
| `~/.claude/agents/` | Subagent definitions (GSD plugin installs 11) | Per-agent |
| `~/.claude/skills/` | User-level skills (11 symlinks on our system) | Symlinks |
| `~/.claude/plugins/` | Plugin installs, marketplaces, cache | 12 MB |
| `~/.claude/ide/{port}.lock` | IDE integration: PID, WebSocket auth token | Per-IDE |
| `~/.claude/teams/{team-name}/config.json` | Agent Teams configuration | Per-team |
| `~/.claude/shell-snapshots/` | Shell env captures at session start | 448 KB |

### Project Path Sanitization

Session directories use sanitized project paths: `/` replaced with `-`, leading `/` removed.
- `/Users/home/Repositories/operating-system` → `-Users-home-Repositories-operating-system`
- Worktrees get their own: `-Users-home-Repositories-repo--worktrees-branch-name`

---

## 2. Session Storage Format

### Transcript Structure (JSONL)

Each line is a standalone JSON object. Common fields on every message:

```json
{
  "parentUuid": "uuid-of-parent-message",
  "isSidechain": false,
  "userType": "external",
  "cwd": "/path/to/project",
  "sessionId": "session-uuid",
  "version": "2.1.63",
  "gitBranch": "main",
  "type": "user|assistant|progress|custom-title|file-history-snapshot",
  "uuid": "unique-message-id",
  "timestamp": "ISO-8601"
}
```

### Message Types

| Type | Content |
|------|---------|
| `user` | User messages with `role: "user"` and `content` |
| `assistant` | Claude responses with tool calls, text |
| `progress` | Hook execution progress (SessionStart hooks firing) |
| `custom-title` | Session rename events |
| `file-history-snapshot` | Snapshots of files being tracked for undo |

### Subagent Transcripts

Stored at `~/.claude/projects/{path}/{session-uuid}/subagents/agent-{short-id}.jsonl`. Same format but with `"isSidechain": true`, `"agentId"`, and `"slug"` (creative name).

### Session CLI Commands

| Command | Purpose |
|---------|---------|
| `claude` | New interactive session |
| `claude -c` | Continue most recent in current directory |
| `claude -r "<session>" "query"` | Resume by ID or name |
| `claude --session-id "UUID"` | Use specific session ID |
| `claude --fork-session` | Fork when resuming (new ID, keep history) |
| `claude --from-pr 123` | Resume sessions linked to a PR |
| `/resume [session]` | Interactive: resume or show picker |
| `/rename [name]` | Rename current session |
| `/fork [name]` | Fork current conversation |

---

## 3. Hooks System

### 17 Available Hook Events

| Event | Fires When | Can Block? | Input Matcher |
|-------|-----------|------------|---------------|
| `SessionStart` | Session begins or resumes | No | `startup`, `resume`, `clear`, `compact` |
| `SessionEnd` | Session terminates | No | `clear`, `logout`, `prompt_input_exit`, `other` |
| `UserPromptSubmit` | User submits prompt, before processing | Yes | — |
| `PreToolUse` | Before tool call executes | Yes | Tool name |
| `PostToolUse` | After tool call succeeds | No | Tool name |
| `PostToolUseFailure` | After tool call fails | No | Tool name |
| `PermissionRequest` | Permission dialog appears | Yes | Tool name |
| `Notification` | Claude sends notification | No | `permission_prompt`, `idle_prompt`, `auth_success` |
| `Stop` | Claude finishes responding | Yes | — |
| `SubagentStart` | Subagent spawned | No | Agent type |
| `SubagentStop` | Subagent finishes | Yes | Agent type |
| `TeammateIdle` | Agent team teammate about to go idle | Yes | — |
| `TaskCompleted` | Task being marked complete | Yes | — |
| `ConfigChange` | Config file changes during session | Yes | Setting scope |
| `WorktreeCreate` | Worktree being created | Yes | — |
| `WorktreeRemove` | Worktree being removed | No | — |
| `PreCompact` | Before context compaction | No | `manual`, `auto` |

### Hook Types

| Type | Description | Available On |
|------|-------------|-------------|
| `command` | Shell command, receives JSON on stdin | All events |
| `http` | POST to URL with JSON body | Blocking events only |
| `prompt` | Single-turn LLM evaluation (Haiku default) | Blocking events only |
| `agent` | Multi-turn subagent with tool access (up to 50 turns) | Blocking events only |

### Standard Hook Input (JSON on stdin)

Every hook receives:

| Field | Description |
|-------|-------------|
| `session_id` | Current session identifier |
| `transcript_path` | Path to conversation JSONL |
| `cwd` | Current working directory |
| `permission_mode` | `default`, `plan`, `acceptEdits`, `dontAsk`, `bypassPermissions` |
| `hook_event_name` | Name of the event |

### Hook Output (JSON on stdout)

| Field | Default | Description |
|-------|---------|-------------|
| `continue` | `true` | If `false`, stops Claude entirely |
| `stopReason` | — | Message shown when `continue` is `false` |
| `suppressOutput` | `false` | Hides stdout from verbose output |
| `systemMessage` | — | Warning message shown to user |

### Decision Control (event-specific)

- **PreToolUse**: `hookSpecificOutput.permissionDecision` = `allow|deny|ask`
- **PermissionRequest**: `hookSpecificOutput.decision.behavior` = `allow|deny`
- **Stop/SubagentStop/PostToolUse/UserPromptSubmit**: `decision: "block"`, `reason`

### Hook Configuration Locations

| Location | Scope |
|----------|-------|
| `~/.claude/settings.json` | All projects (user) |
| `.claude/settings.json` | Single project (shared) |
| `.claude/settings.local.json` | Single project (local) |
| Managed policy settings | Organization-wide |
| Plugin `hooks/hooks.json` | When plugin enabled |
| Skill/agent YAML frontmatter | While component active |

### Environment Variables in Hooks

- `$CLAUDE_PROJECT_DIR` — project root directory
- `$CLAUDE_ENV_FILE` — (SessionStart only) file for persisting env vars
- `$CLAUDE_CODE_REMOTE` — `"true"` in remote/web environments

### Our Active Hooks

**SessionStart**: Runs `bd prime` (beads) + GSD update check
**PreCompact**: Runs `bd prime`
**StatusLine**: Node script that receives model/session/context JSON, renders colored progress bar

---

## 4. Agent SDK (Python)

### Package: `claude-agent-sdk` (v0.1.38 installed, was `claude-code-sdk`)

### Two Interfaces

**`query()` — Stateless, creates new session each call:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="...",
    options=ClaudeAgentOptions(
        cwd="/path/to/repo",
        add_dirs=["/path/to/other"],
        tools=["Bash", "Read", "Edit"],
        allowed_tools=["Bash", "Read", "Edit"],
        setting_sources=["user", "project"],
        permission_mode="bypassPermissions",
        system_prompt={"type": "preset", "preset": "claude_code", "append": "..."},
        model="claude-opus-4-6",
        max_turns=40,
        max_budget_usd=10.0,
        output_format={"type": "json_schema", "schema": {...}},
        resume="session-id",
        fork_session=True,
    )
):
    ...
```

**`ClaudeSDKClient` — Persistent connection, supports interaction:**
```python
client = ClaudeSDKClient()
await client.connect(prompt="...")
# Or: await client.query(prompt="...", session_id="...")

# Receive messages
async for message in client.receive_messages():
    ...

# Interactive methods
await client.interrupt()
await client.set_permission_mode(mode)
await client.set_model(model)
await client.rewind_files(user_message_id)
mcp_status = await client.get_mcp_status()
server_info = await client.get_server_info()
await client.disconnect()
```

### Session ID Capture

```python
async for message in query(prompt="...", options=options):
    if hasattr(message, "subtype") and message.subtype == "init":
        session_id = message.session_id
```

### Authentication Options

| Method | Env Var |
|--------|---------|
| API Key | `ANTHROPIC_API_KEY` |
| OAuth Token | `CLAUDE_CODE_OAUTH_TOKEN` |
| AWS Bedrock | `CLAUDE_CODE_USE_BEDROCK=1` |
| Google Vertex | `CLAUDE_CODE_USE_VERTEX=1` |
| Subscription | Default (no env var needed) |

### SDK Hooks (Programmatic)

Hooks can be Python callbacks (not just shell commands) when using the SDK:
```python
options=ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[callback])]},
    can_use_tool=custom_permission_handler,
)
```

---

## 5. Agent Teams (Experimental)

**Enable**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

### Architecture

- **Lead session** + **teammates** + **shared task list** + **mailbox**
- Config: `~/.claude/teams/{team-name}/config.json`
- Task list: `~/.claude/tasks/{team-name}/`
- Communication: Direct messaging between teammates, broadcasts

### Display Modes

| Mode | Behavior |
|------|----------|
| `in-process` | Default, teammates run in same process |
| `tmux` | Each teammate gets its own tmux pane |
| `auto` | Auto-detect (tmux if available) |

Set via `--teammate-mode tmux` CLI flag or `teammateMode` setting.

### Relevant Hooks

| Hook | Purpose |
|------|---------|
| `TeammateIdle` | Fires when a teammate is about to go idle — quality gate |
| `TaskCompleted` | Fires when a task is marked complete — completion criteria |

### Key Properties

- Teammates can self-claim tasks from the shared list
- Teammates can be required to plan before implementing
- Teammates cannot spawn other subagents (max depth = 1)
- Each teammate gets its own transcript at `~/.claude/projects/{path}/{session}/subagents/`

### Integration Opportunity

The OS EA doesn't need to replicate Agent Teams. It should:
1. Use the same messaging/task patterns where possible
2. Be able to spin up sessions that USE Agent Teams internally
3. Manage the lifecycle AROUND sessions (create, monitor, clean up)

---

## 6. Remote Control

### How It Works

- `claude remote-control` or `/remote-control` from existing session
- Local process makes outbound HTTPS only — never opens inbound ports
- Registers with Anthropic API and polls for work
- Messages routed over TLS via streaming connection
- Short-lived, scoped credentials

### Limitations

- One remote session per Claude Code instance
- Terminal must stay open
- ~10 minute timeout on extended network outage
- Max plan required (Pro coming soon)

### Programmatic Access

No direct API for remote control management. It's designed for human interaction via claude.ai/code or mobile app.

---

## 7. CLI Flags Reference (Session-Relevant)

| Flag | Description |
|------|-------------|
| `--add-dir` | Additional working directories |
| `--agent` | Specify agent for session |
| `--agents` | Define subagents via JSON |
| `--allowedTools` | Tools that execute without permission |
| `--continue`, `-c` | Resume most recent conversation |
| `--dangerously-skip-permissions` | Skip all permission prompts |
| `--fork-session` | Create new session ID when resuming |
| `--model` | Set model (`sonnet`, `opus`, or full name) |
| `--output-format` | Output: `text`, `json`, `stream-json` |
| `--permission-mode` | Start in specified mode |
| `--print`, `-p` | Non-interactive mode |
| `--remote` | Create new web session on claude.ai |
| `--resume`, `-r` | Resume specific session |
| `--session-id` | Use specific UUID for session |
| `--setting-sources` | Which settings to load: `user`, `project`, `local` |
| `--teammate-mode` | Agent team display: `auto`, `in-process`, `tmux` |
| `--teleport` | Resume web session locally |
| `--verbose` | Full turn-by-turn output |
| `--worktree`, `-w` | Start in isolated git worktree |

---

## 8. Settings Hierarchy

Precedence (highest first):

1. **Managed** — `/Library/Application Support/ClaudeCode/` (org-wide)
2. **CLI arguments** — flags override everything
3. **Local** — `.claude/settings.local.json` (personal, not committed)
4. **Project** — `.claude/settings.json` (committed, shared)
5. **User** — `~/.claude/settings.json` (personal, all projects)

Array settings **merge** across scopes rather than replace.

### Key Settings

| Setting | Type | Description |
|---------|------|-------------|
| `model` | string | Default model |
| `permissions.allow` | string[] | Always-allow tool rules |
| `permissions.defaultMode` | string | Default permission mode |
| `cleanupPeriodDays` | number | Session cleanup (default 30) |
| `hooks` | object | Hook configurations |
| `env` | object | Environment variables |
| `teammateMode` | string | `auto`, `in-process`, `tmux` |
| `statusLine` | object | Custom status line command |

---

## 9. Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAUDECODE` | Set when inside a Claude Code session. Blocks nested sessions. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable agent teams (`1`) |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | Enable OTEL telemetry |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Compaction trigger percentage |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | Load CLAUDE.md from `--add-dir` |
| `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY` | Auto-exit delay (ms) |
| `CLAUDE_CODE_TASK_LIST_ID` | Named task list directory |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | Disable background tasks |

---

## 10. What Already Exists on Our System

| Component | Count | Notes |
|-----------|-------|-------|
| Sessions (OS project) | ~115 | Full JSONL transcripts |
| Sessions (all projects) | 20 project dirs | 810 MB total |
| Active hooks | 3 | SessionStart (bd prime + GSD), PreCompact (bd prime) |
| User-level skills | 11 | Symlinks to content-system and observability |
| Project-level skills | 25 | In operating-system/.claude/skills/ |
| Plugins | 5 | superpowers, commit-commands, frontend-design, linear, linear-cli |
| Agents | 13 | GSD subagents |
| History entries | 6,349 | Global message log |
| Debug logs | 345 files | 525 MB |

---

## 11. Integration Points for EA Session Management

### What we get for free (already exists):

1. **Session creation**: `claude` CLI with flags for model, permissions, worktree, tools
2. **Session resume**: `claude -r <session-id>` or `claude -c`
3. **Session naming**: `/rename` command
4. **Session transcripts**: JSONL files readable by any tool
5. **State tracking via hooks**: SessionStart, SessionEnd, Stop, TaskCompleted all fire with session_id
6. **Context window status**: StatusLine hook already receives this data
7. **Agent Teams tmux mode**: `--teammate-mode tmux` renders sessions in tmux panes
8. **SDK persistent client**: `ClaudeSDKClient` for programmatic interaction
9. **Worktree isolation**: `--worktree` flag for project isolation
10. **Task tracking**: Built-in task system with dependencies, per-session

### What we need to build:

1. **Session registry** — Maps session IDs to projects, tracks lifecycle state
2. **Hook scripts** — Write events to a shared state file/directory the EA can read
3. **CLI wrapper** — Thin layer that creates sessions with OS conventions (right repo, right context, right hooks)
4. **EA skill** — Intelligence layer that uses the registry + CLI to orchestrate

### What we should NOT build:

1. Session transcript storage (Claude Code has it)
2. Context tracking (StatusLine hook has it)
3. Activity detection (hooks provide this)
4. Inter-session messaging (Agent Teams has it, or we use the same patterns)
5. File versioning/undo (file-history handles it)
