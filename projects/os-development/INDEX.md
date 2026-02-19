# OS Development

Development of the operating system itself — the skills, systems, and infrastructure that make Indemn's connected intelligence layer work. Covers the dispatch system, systems framework, skill improvements, and meta-level architecture of the OS.

## Status
**Session 2026-02-19**: Deep design session on OS architecture. Established the three-primitive model (Skills, Projects, Systems). Designed the dispatch system — a ralph loop that executes specs by running autonomous Claude Code sessions in target repos with managed context. Researched Claude Agent SDK, CLI orchestration, Ralph Wiggum pattern, multi-repo context loading. Installed `claude-agent-sdk` (v0.1.38). Hit nested session detection when testing SDK auth — needs manual test outside Claude Code.

**Full design artifact:** `docs/plans/2026-02-19-dispatch-system-design.md` (~400 lines, comprehensive)

**Next session should:**
1. Read `docs/plans/2026-02-19-dispatch-system-design.md` for full context
2. Test SDK auth from terminal: `env -u CLAUDECODE python3 /tmp/test_sdk.py`
3. Create `systems/dispatch/` directory with SYSTEM.md
4. Build the dispatch engine (Python ralph loop)
5. Build the dispatch skill (`.claude/skills/dispatch/SKILL.md`)

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

## Decisions
- 2026-02-19: OS has three primitives: Skills (capabilities), Projects (memory), Systems (processes)
- 2026-02-19: Dispatch is a skill + system within the OS, not a separate tool
- 2026-02-19: Ralph Wiggum loop pattern — fresh context per task, file-based state, iterate until done
- 2026-02-19: Verification always runs in a SEPARATE session from implementation
- 2026-02-19: Agent SDK is preferred mechanism; `claude -p` is fallback if SDK auth fails
- 2026-02-19: Content system stays separate for now; moving into systems/ is future work
- 2026-02-19: GSD is out of scope — building custom dispatch that fits OS patterns
- 2026-02-19: The spec format defines the work; dispatch just grinds through it (not hard-coded phases)

## Open Questions
- Does SDK auth work with Claude subscription? (test: `env -u CLAUDECODE python3 test_sdk.py`)
- Spec format: YAML vs JSON vs Markdown?
- Which OS skills should be symlinked to `~/.claude/skills/` for global access in dispatched sessions?
- How should the engine handle tasks that exceed max iterations? Skip? Abort? Ask?
- Should we build a `/spec` skill for creating well-defined specs during project work?
