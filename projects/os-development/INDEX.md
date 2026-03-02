# OS Development

Development of the operating system itself — the skills, systems, and infrastructure that make Indemn's connected intelligence layer work. Covers the dispatch system, systems framework, skill improvements, and meta-level architecture of the OS.

## Status
**Session 2026-03-02-a**: Implemented the EA & Session Management system. All four components built and tested (31/31 tests passing):

1. **`lib/os_state.py`** — Shared utilities: atomic JSON writes, state file lookup by session_id/name/cwd, event management with 50-event cap. Stdlib only.
2. **Hook scripts** — `update-state.py` (5 events: SessionStart, Stop, UserPromptSubmit, TaskCompleted, SessionEnd) and `update-context.py` (statusline wrapper with GSD passthrough, context % tracking, context_low at <10%). Installed globally in `~/.claude/settings.json`.
3. **Session CLI** (`systems/session-manager/cli.py`) — 7 commands: create, list, attach, send, status, close, destroy. Manages tmux + git worktrees + Claude Code processes. Aliased as `session` in `.env`.
4. **EA skill** (`.claude/skills/ea/SKILL.md`) — Reads session state, presents briefings, orchestrates lifecycle via CLI.

**Previous session (2026-03-01-a)**: Designed the EA & Session Management architecture.

**Onboarding branch** — is 40+ commits behind main. Needs rebasing but DO NOT rebase while parallel sessions are active on main.

**Next session should:**
1. Integration test the full session lifecycle (create → hooks fire → send → close)
2. Verify `--session-id` flag is honored by Claude Code (needed for hook-to-state mapping)
3. Build `/1password` skill and evaluate `op` CLI for secrets management
4. Consider task layer unification (beads + Claude Code tasks + Linear)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Agent SDK docs | Web | https://platform.claude.com/docs/en/agent-sdk/overview |
| Agent SDK Python ref | Web | https://platform.claude.com/docs/en/agent-sdk/python |
| Agent SDK Skills | Web | https://platform.claude.com/docs/en/agent-sdk/skills |
| Ralph (reference impl) | GitHub | https://github.com/snarktank/ralph |
| SDK Max billing issue | GitHub | https://github.com/anthropics/claude-agent-sdk-python/issues/559 |
| SDK rate_limit_event bug | GitHub | https://github.com/anthropics/claude-agent-sdk-python/issues/583 |
| Claude Code headless docs | Web | https://code.claude.com/docs/en/headless |
| Design doc | Local | projects/os-development/artifacts/2026-02-19-dispatch-system-design.md |
| Kai's onboarding DM | Slack | DM channel D0A36TW1YSK (Craig ↔ Kai) |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-19 | [dispatch-system-design](artifacts/2026-02-19-dispatch-system-design.md) | Full architecture for dispatch system, OS primitives, SDK findings, ralph loop design |
| 2026-02-19 | [dispatch-system-implementation](artifacts/2026-02-19-dispatch-system-implementation.md) | Build the dispatch engine, skills, beads skill, and systems framework |
| 2026-02-19 | [dispatch-engine-fixes](artifacts/2026-02-19-dispatch-engine-fixes.md) | Fix engine bugs (anyio, rate_limit_event, bd children), configure agent sessions, end-to-end test passing |
| 2026-02-23 | [onboarding-instructions](artifacts/2026-02-23-onboarding-instructions.md) | Instructions for a new developer to get set up with the operating system and local dev environment |
| 2026-03-01 | [claude-code-internals](artifacts/2026-03-01-claude-code-internals.md) | How Claude Code works on our system — sessions, hooks, state, Agent Teams, SDK. Foundation for EA integration. |
| 2026-03-01 | [ea-session-management-design](artifacts/2026-03-01-ea-session-management-design.md) | Full architecture for EA & session management — tmux sessions, event-driven state, switchboard EA, voice/task future layers |

## Decisions
- 2026-02-19: OS has three primitives: Skills (capabilities), Projects (memory), Systems (processes)
- 2026-02-19: Dispatch is a skill + system within the OS, not a separate tool
- 2026-02-19: Ralph Wiggum loop pattern — fresh context per task, file-based state, iterate until done
- 2026-02-19: Verification always runs in a SEPARATE session from implementation
- 2026-02-19: Agent SDK is THE mechanism (not fallback). Anthropic confirmed it works with subscription.
- 2026-02-19: Content system stays separate for now; moving into systems/ is future work
- 2026-02-19: GSD is out of scope — building custom dispatch that fits OS patterns
- 2026-02-19: Beads epics are the dispatch containers — no custom YAML spec format
- 2026-02-19: Minimal spec, engine decides SDK configuration
- 2026-02-19: Use `--notes "target_repo: /path"` on epics (not `--repo`, which routes to different beads DB)
- 2026-02-19: Systems documented in CLAUDE.md + conventions.md, no `/system` skill needed yet
- 2026-02-19: `contextlib.aclosing()` required for SDK `query()` async generators — prevents anyio cancel scope leaks
- 2026-02-19: Monkey-patch `parse_message` for SDK `rate_limit_event` crash (Issue #583) — return None, filter in consumer
- 2026-02-19: Use `bd list --parent --all` not `bd children` — the latter excludes closed tasks, breaking dependency resolution
- 2026-02-19: Verification uses text-based JSON parsing (not `output_format`) — `rate_limit_event` kills stream before `ResultMessage`
- 2026-02-19: Tasks that exhaust max retries are skipped, engine continues with remaining tasks
- 2026-02-19: Dispatched sessions use `bypassPermissions` — fully autonomous, no prompts
- 2026-02-19: Dispatched sessions use Opus model for maximum capability
- 2026-02-19: Verification sessions can write/edit (not read-only) — enables auto-fixes
- 2026-02-19: No `max_turns` or `max_budget_usd` limits — subscription covers it, `MAX_RETRIES_PER_TASK=3` is the circuit breaker
- 2026-02-19: Cost display in engine output is informational only (subscription, not per-session billing)
- 2026-02-24: Slack tokens read from macOS Keychain first, env vars as fallback — no plaintext tokens needed on macOS
- 2026-02-24: Skills should be platform-aware — detect OS and adjust (e.g., keychain on macOS, env vars on Linux, Python path detection)
- 2026-02-24: Adopt 1Password CLI (`op`) for secrets management — endorsed by Craig, next session priority
- 2026-03-01: EA is a switchboard — manages session lifecycle, not a proxy for project work
- 2026-03-01: All sessions start in OS repo worktrees; external repos added via `--add-dir`
- 2026-03-01: File-per-session state model — eliminates contention, scales to multiple EAs
- 2026-03-01: tmux send-keys is the universal write mechanism into sessions
- 2026-03-01: EA is above Agent Teams — manages sessions that may themselves use Agent Teams
- 2026-03-01: EA is not immortal — reads state from disk, any session with EA skill becomes the EA
- 2026-03-01: Manual triggers only for now — automation is a future layer
- 2026-03-01: Voice interface and unified task layer are future work (noted in design doc)

## Open Questions
- Which OS skills should be symlinked to `~/.claude/skills/` for global access in dispatched sessions?
- When SDK Issue #583 is fixed, remove the monkey-patch from engine.py
- 1Password: `op run` vs `op read` for secret injection? Split `.env` into urls + secrets?
- Should onboarding branch be maintained separately, or just point new engineers at main?
