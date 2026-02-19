# Dispatch

Autonomous execution engine for implementation plans. Takes a beads epic (parent task with child tasks), runs each child task in a fresh Claude Code session via the Agent SDK, verifies results in a separate session, and loops until all tasks pass or nothing remains to try.

## Capabilities

- Execute beads epics as implementation plans against any target repo
- Fresh context window per task — no token carryover, managed context injection
- Independent verification — separate Claude Code session judges each task against acceptance criteria
- Append-only learnings — knowledge accumulates across tasks without polluting context
- Git commits after each passing task — clear history of what was built
- Full OS framework in dispatched sessions — skills, CLAUDE.md, conventions all loaded via `setting_sources`

## Skills

| Skill | Purpose |
|-------|---------|
| `/dispatch` | Entry point — takes an epic bead ID, runs the loop, reports results |

## State

- **Beads** — task status lives in the project's beads (epic + children). The engine reads and updates beads via `bd` CLI.
- **Learnings** — append-only file written during execution, carries context between tasks. Stored in `systems/dispatch/active/learnings.md` during a run.
- **Git history** — code accumulates in the target repo across tasks.

## Dependencies

- `claude-agent-sdk` (Python) — installed in `/Users/home/Repositories/.venv/`
- `bd` (beads CLI) — task tracking
- Claude Code subscription — authenticates SDK sessions
- Python 3.12+ — engine runtime

## Integration Points

- **Reads from:** beads epics (task definitions), project INDEX.md (context, decisions)
- **Produces:** code changes + git commits in target repos, bead status updates
- **Reports to:** project artifacts (via `/project save` after dispatch completes)
