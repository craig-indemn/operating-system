# OS Development

Development of the operating system itself — the skills, systems, and infrastructure that make Indemn's connected intelligence layer work. Covers the dispatch system, systems framework, skill improvements, and meta-level architecture of the OS.

## Status
**Session 2026-02-19-c**: Fixed all dispatch engine bugs and achieved full end-to-end success — 2/2 tasks passed autonomously. Three bugs fixed: (1) `contextlib.aclosing()` for anyio cancel scope cleanup between sequential `query()` calls, (2) monkey-patch for SDK `rate_limit_event` crash ([Issue #583](https://github.com/anthropics/claude-agent-sdk-python/issues/583)), (3) `bd children` only returns open tasks — switched to `bd list --parent --all`. Also added verification retry loop and proper max-retry enforcement. SDK updated to v0.1.39. Total test cost: ~$0.28 for 2 tasks (implement + verify each).

**Test results (epic `os-development-26e`):**
- Task 1 "Create hello.txt" — PASSED, verified, committed ($0.16)
- Task 2 "Create goodbye.txt" — PASSED, verified with backstop check, committed ($0.06)
- Dependencies respected, learnings accumulated, git history clean

**What's working:**
- Full ralph loop: read epic → pick ready task → implement → verify → close bead → git commit → next task
- SDK subscription auth
- Fresh context per task with full OS framework (`setting_sources=["user", "project"]`)
- Separate verification sessions with text-based JSON parsing
- Dependency-aware task ordering
- Retry logic (3 impl retries, 3 verify retries per task)

**Next session should:**
1. Run a real dispatch against an actual service repo (not just test files)
2. Determine which OS skills to symlink to `~/.claude/skills/` for global access
3. Consider whether to clean up test beads or keep them as examples

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

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-19 | [dispatch-system-design](artifacts/2026-02-19-dispatch-system-design.md) | Full architecture for dispatch system, OS primitives, SDK findings, ralph loop design |
| 2026-02-19 | [dispatch-system-implementation](artifacts/2026-02-19-dispatch-system-implementation.md) | Build the dispatch engine, skills, beads skill, and systems framework |
| 2026-02-19 | [dispatch-engine-fixes](artifacts/2026-02-19-dispatch-engine-fixes.md) | Fix engine bugs (anyio, rate_limit_event, bd children), configure agent sessions, end-to-end test passing |

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

## Open Questions
- Which OS skills should be symlinked to `~/.claude/skills/` for global access in dispatched sessions?
- When SDK Issue #583 is fixed, remove the monkey-patch from engine.py
