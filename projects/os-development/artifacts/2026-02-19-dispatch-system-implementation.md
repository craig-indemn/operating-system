---
ask: "Build the dispatch system — the ralph loop engine, dispatch skill, beads skill, and systems framework — so the OS can autonomously execute implementation plans across repos"
created: 2026-02-19
workstream: os-development
session: 2026-02-19-b
sources:
  - type: web
    description: "Claude Agent SDK docs — query(), ClaudeAgentOptions, setting_sources, structured output, hooks, permissions"
  - type: web
    description: "Claude Code CLI headless docs — claude -p flags, skills in headless mode, CLAUDE.md hierarchy"
  - type: web
    description: "Agent SDK GitHub issues — rate_limit_event parsing, subscription auth (Issue #559)"
  - type: web
    description: "Ralph Wiggum loop pattern — autonomous iteration, stop hooks, backstop criteria"
---

# Dispatch System Implementation

## What Was Built

### Systems Framework (new OS primitive)

Systems are now a first-class concept alongside Skills and Projects. Documented in:
- `CLAUDE.md` — Systems section with table of systems, explanation of what they are
- `.claude/rules/conventions.md` — System conventions (SYSTEM.md format, directory structure, three primitives)

**Three primitives:** Skills (capabilities), Projects (memory), Systems (processes)

### Dispatch System (`systems/dispatch/`)

**`SYSTEM.md`** — System definition. What dispatch does, capabilities, state management, dependencies, integration points.

**`engine.py`** (~350 lines) — The ralph loop engine. Python, using `query()` from `claude-agent-sdk`.

How the engine works:
1. Takes a beads epic ID as input
2. Reads epic via `bd show <epic-id> --json` — gets target repo, backstop acceptance criteria
3. Lists children via `bd children <epic-id> --json` — gets all tasks
4. **Loop:**
   - Find next ready child (open status, deps satisfied)
   - Mark in_progress via `bd update --status in_progress`
   - Build context string: epic description, task details, learnings from previous tasks
   - Call `query()` with full OS framework:
     - `setting_sources=["user", "project"]` — loads skills + CLAUDE.md
     - `permission_mode="acceptEdits"` — autonomous execution
     - `allowed_tools` — full Claude Code toolset including Skill
     - `system_prompt` — preset claude_code with appended task context
   - Catch `MessageParseError` for `rate_limit_event` (known SDK issue)
   - Run **separate verification session** — read-only tools, `json_schema` output for pass/fail
   - If pass: `bd close`, git commit in target repo, append to learnings
   - If fail: retry with failure context (up to 2 retries), append to learnings
5. Write summary when complete

Key design decisions in the engine:
- Beads interaction via `bd` CLI commands (CLI-first, not SQLite direct)
- `CLAUDECODE` env var unset to bypass nested session detection
- Learnings are append-only — grow across tasks, injected as context
- Verification uses `output_format` with `json_schema` for structured pass/fail

### Dispatch Skill (`.claude/skills/dispatch/SKILL.md`)

Interface for invoking dispatch from interactive OS sessions.

Commands:
- `/dispatch <epic-id>` — Execute all children of an epic through the ralph loop
- `/dispatch status <epic-id>` — Check progress via `bd children`
- `/dispatch create` — Interactively create an epic + child tasks from conversation context

### Beads Skill (`.claude/skills/beads/SKILL.md`)

Comprehensive beads task tracking skill covering:
- Core: create, ready, update, close, show, search
- Epics: create with `--repo`, `--acceptance`, `--parent` for dispatch containers
- Dependencies: add, remove, tree, cycles
- Bulk create from markdown files
- Visualization: `bd graph`, `bd list --pretty`
- Quality: `bd lint` to verify acceptance criteria
- Advanced: defer, estimates, external refs, molecules, gates, swarms
- Dispatch integration section — exact flow from conversation to `/dispatch`

### CLAUDE.md Updates

- Added `/dispatch` to System Skills table
- Added `/beads` to Tool Skills table
- Added Systems section with dispatch listed
- Updated project skill to reference beads skill

## SDK Auth Finding

The Agent SDK authenticates with the Claude Code subscription. Tested and confirmed:
- SDK connects and runs sessions using subscription auth
- `rate_limit_event` message parsing error occurs (SDK v0.1.38 doesn't recognize this message type)
- Auth works — the error is a parsing issue, not auth. Engine catches and handles it.
- `claude -p` CLI works as alternative but lacks skills loading
- Decision: use SDK for full framework support, catch parse errors

## Flow: Conversation to Dispatch

```
1. Work on a project in the OS (conversation, research, decisions)
2. "Let's break this into tasks for dispatch"
3. Create epic: bd create "Title" --type epic --repo /path --acceptance "backstop"
4. Create children: bd create "Task" --parent <epic-id> --acceptance "criteria"
5. Verify: bd lint, bd children <epic-id> --pretty
6. /dispatch <epic-id> → engine grinds through tasks
7. Review results, save artifact, update project
```

## Files Created/Modified

| File | Action |
|------|--------|
| `systems/dispatch/SYSTEM.md` | Created |
| `systems/dispatch/engine.py` | Created |
| `.claude/skills/dispatch/SKILL.md` | Created |
| `.claude/skills/beads/SKILL.md` | Created |
| `CLAUDE.md` | Modified — Systems section, dispatch + beads in skill tables |
| `.claude/rules/conventions.md` | Modified — Systems conventions |
| `.claude/skills/project/SKILL.md` | Modified — beads reference |

## Not Yet Tested

The dispatch engine needs end-to-end testing from a terminal (outside Claude Code):
```bash
cd projects/os-development
bd create "Test dispatch" --type epic --repo /tmp/test-repo --acceptance "hello.txt exists"
bd create "Create hello.txt" --parent <epic-id> --acceptance "File contains hello world"
env -u CLAUDECODE /Users/home/Repositories/.venv/bin/python3 systems/dispatch/engine.py <epic-id> --beads-dir projects/os-development
```
