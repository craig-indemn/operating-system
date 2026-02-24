# OS Development

Development of the operating system itself — the skills, systems, and infrastructure that make Indemn's connected intelligence layer work. Covers the dispatch system, systems framework, skill improvements, and meta-level architecture of the OS.

## Status
**Session 2026-02-24-a**: Addressed all 6 onboarding issues from Kai's first use of the system. Committed and pushed to main.

**Fixes applied:**
1. **Slack token extraction** — `slack_client.py` now reads from macOS Keychain first (where `agent-slack` stores tokens), env vars as fallback for Linux. No Slack tokens needed in `.env` on macOS.
2. **Linear env var mismatch** — skill now says `LINEAR_API_TOKEN` directly, removed confusing `LINEAR_API_KEY` bridge.
3. **MongoDB IP whitelisting** — added as explicit Phase 4b blocker in onboarding skill. Added to onboarding instructions artifact prereqs.
4. **Google Workspace credentials.json** — skill now references 1Password (Engineering vault → "Google Workspace OAuth — gog CLI"). Craig needs to upload `craig_secret.json` there.
5. **Python PEP 668** — Slack SDK install uses 3-tier fallback: `pip3` → `--break-system-packages` → `uv pip install --system`.
6. **`.env` special chars** — added quoting guidance to `.env.template`. Main offender (Slack cookie) no longer in `.env`.

**Platform awareness** — Slack skill now auto-detects which Python has `slack_sdk` (`SLACK_PY` pattern), documents macOS vs Linux token storage paths. `slack_client.py` uses `platform.system()` to gate keychain access.

**Onboarding branch** — is 40+ commits behind main. Needs rebasing but DO NOT rebase while parallel sessions are active on main. Do it in a quiet moment.

**Next session should:**
1. Build a `/1password` skill and evaluate 1Password CLI (`op`) for secrets management — Craig endorsed this direction
2. Consider `op run` for injecting secrets at runtime instead of plaintext `.env` files
3. Evaluate splitting `.env` into `.env.urls` (safe to commit) and secrets in 1Password
4. Upload `craig_secret.json` to 1Password Engineering vault (manual action for Craig)
5. Update onboarding branch when no parallel sessions are running

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

## Open Questions
- Which OS skills should be symlinked to `~/.claude/skills/` for global access in dispatched sessions?
- When SDK Issue #583 is fixed, remove the monkey-patch from engine.py
- 1Password: `op run` vs `op read` for secret injection? Split `.env` into urls + secrets?
- Should onboarding branch be maintained separately, or just point new engineers at main?
