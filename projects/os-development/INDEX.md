# OS Development

Development of the operating system itself — the skills, systems, and infrastructure that make Indemn's connected intelligence layer work. Covers the dispatch system, systems framework, skill improvements, and meta-level architecture of the OS.

## Status
**Session 2026-02-19-b**: Built the dispatch system. Created systems framework (CLAUDE.md, conventions.md), dispatch engine (`systems/dispatch/engine.py`), dispatch skill, and comprehensive beads skill. SDK auth confirmed working with subscription. First end-to-end test partially succeeded — implementation session ran, created `hello.txt` in target repo ($0.19 cost), but crashed on second sequential `query()` call due to anyio cancel scope bug in the SDK. Switched engine to use `claude -p` subprocess calls as workaround, but user correctly objected to sync approach. Engine needs to stay async with SDK — just needs proper cleanup between `query()` calls.

**Key discovery:** `bd create --repo` routes to a different beads database (multi-repo feature), NOT a metadata field. Use `--notes "target_repo: /path"` instead. Engine updated accordingly.

**What was built:**
- `systems/dispatch/SYSTEM.md` — system definition
- `systems/dispatch/engine.py` — ralph loop engine (needs async fix for sequential query() calls)
- `.claude/skills/dispatch/SKILL.md` — dispatch skill interface
- `.claude/skills/beads/SKILL.md` — comprehensive beads skill (all bd commands)
- `CLAUDE.md` — Systems section added, /dispatch and /beads in skill tables
- `.claude/rules/conventions.md` — System conventions added
- Test epic `os-development-26e` with 2 children exists in beads

**Next session should:**
1. Read this INDEX.md + `artifacts/2026-02-19-dispatch-system-implementation.md`
2. Fix the async bug in engine.py — sequential `query()` calls crash due to anyio cancel scope cleanup. Need to properly exhaust/close the async generator before starting the next query.
3. Re-run test with epic `os-development-26e` (reset hello.txt in `/tmp/test-dispatch-repo` first)
4. Once working: clean up test beads, update artifact with results

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Agent SDK docs | Web | https://platform.claude.com/docs/en/agent-sdk/overview |
| Agent SDK Python ref | Web | https://platform.claude.com/docs/en/agent-sdk/python |
| Agent SDK Skills | Web | https://platform.claude.com/docs/en/agent-sdk/skills |
| Ralph (reference impl) | GitHub | https://github.com/snarktank/ralph |
| SDK Max billing issue | GitHub | https://github.com/anthropics/claude-agent-sdk-python/issues/559 |
| Claude Code headless docs | Web | https://code.claude.com/docs/en/headless |
| Design doc | Local | projects/os-development/artifacts/2026-02-19-dispatch-system-design.md |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-19 | [dispatch-system-design](artifacts/2026-02-19-dispatch-system-design.md) | Full architecture for dispatch system, OS primitives, SDK findings, ralph loop design |
| 2026-02-19 | [dispatch-system-implementation](artifacts/2026-02-19-dispatch-system-implementation.md) | Build the dispatch engine, skills, beads skill, and systems framework |

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

## Open Questions
- How to fix sequential `query()` calls in the SDK (anyio cancel scope cleanup bug)?
- Which OS skills should be symlinked to `~/.claude/skills/` for global access in dispatched sessions?
- How should the engine handle tasks that exceed max iterations? Skip? Abort? Ask?
