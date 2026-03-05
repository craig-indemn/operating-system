# OS Development

Development of the operating system itself — the skills, systems, and infrastructure that make Indemn's connected intelligence layer work. Covers the dispatch system, systems framework, skill improvements, and meta-level architecture of the OS.

## Status
**Session 2026-03-04-a (in progress)**: Gas Town / Wasteland / Dolt research complete. Decision: use Gas Town alongside OS for multi-agent code work, keep OS for intelligence and tools. Dolt as potential state backend. Documented OS Terminal server startup in SYSTEM.md, CLAUDE.md, and sessions skill.

**Session 2026-03-03-c**: Responsive mobile/tablet layout implemented. Single-pane mode with tab bar on ≤1024px. Craig verified on iPad.

**Session 2026-03-03-b**: V2 Remote Access fully shipped. Auth, reconnection, heartbeat, production build, Tailscale Serve.

**Session 2026-03-03-a**: UI polish. CSS auto-grid, VS Code theme, scrollbar fix, resize smear fix.

**Previous**: 2026-03-02-d browser-tested V1. 2026-03-02-c built V1. 2026-03-02-b designed it.

**Onboarding branch** — is 40+ commits behind main. DO NOT rebase while parallel sessions active.

**Next session should:**
1. Install Gas Town and Dolt — set up first rig against an Indemn service repo
2. Evaluate Dolt as OS state backend (replace `sessions/*.json`)
3. Consider Obsidian for project artifacts visualization
4. V3 voice layer or V4 augmentation (overlays, context panels)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Agent SDK docs | Web | https://platform.claude.com/docs/en/agent-sdk/overview |
| Agent SDK Python ref | Web | https://platform.claude.com/docs/en/agent-sdk/python |
| Agent SDK Skills | Web | https://platform.claude.com/docs/en/agent-sdk/skills |
| Ralph (reference impl) | GitHub | https://github.com/snarktank/ralph |
| Gas Town | GitHub | https://github.com/steveyegge/gastown |
| Beads | GitHub | https://github.com/steveyegge/beads |
| Dolt | GitHub | https://github.com/dolthub/dolt |
| Gas Town blog | Medium | https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04 |
| Wasteland blog | Medium | https://steve-yegge.medium.com/welcome-to-the-wasteland-a-thousand-gas-towns-a5eb9bc8dc1f |
| Gas Town Emergency Manual | Medium | https://steve-yegge.medium.com/gas-town-emergency-user-manual-cf0e4556d74b |
| Gas Town Discord | Web | https://gastownhall.ai |
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
| 2026-03-02 | [os-terminal-design](artifacts/2026-03-02-os-terminal-design.md) | Bloomberg-style terminal grid UI — React + xterm.js, WebSocket relay to tmux, voice sidecar architecture, Capacitor for iOS |
| 2026-03-02 | [os-terminal-v1-implementation](artifacts/2026-03-02-os-terminal-v1-implementation.md) | V1 build complete — all files, integration test results, issues fixed, 10-point browser test checklist for next session |
| 2026-03-02 | [os-terminal-v1-browser-testing](artifacts/2026-03-02-os-terminal-v1-browser-testing.md) | V1 browser testing — 14-point checklist results, bugs found/fixed, remaining known issues |
| 2026-03-04 | [gastown-research](artifacts/2026-03-04-gastown-research.md) | Gas Town, Wasteland, Dolt research — architecture comparison, integration vision, action items |
| 2026-03-04 | [gastown-integration-design](artifacts/2026-03-04-gastown-integration-design.md) | Design: Gas Town as dispatch engine, session types, Dolt backend, Obsidian, phased implementation |

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
- 2026-03-02: OS Terminal is the visual interface — Bloomberg-style grid of live terminals
- 2026-03-02: React + xterm.js for the frontend (react-grid-layout replaced with CSS auto-grid in 2026-03-03)
- 2026-03-02: Capacitor for iOS App Store distribution (same React codebase)
- 2026-03-02: Single Node.js backend — REST API + WebSocket terminal relay + file watcher
- 2026-03-02: UI never writes state files directly — all mutations go through session CLI
- 2026-03-02: EA is a regular session in the grid — not special-cased by the UI
- 2026-03-02: Voice is an independent sidecar service, layered on top of the terminal UI
- 2026-03-02: V1 is local only; remote access, auth, and iOS in V2
- 2026-03-02: node-pty 1.2.0-beta.11 required for Node.js 25 — stable 1.1.0 has posix_spawnp failure
- 2026-03-02: tmux binary path resolved explicitly (/opt/homebrew/bin/tmux) — node-pty spawn doesn't inherit full shell PATH
- 2026-03-02: session_id (UUID) is the primary identifier everywhere — React keys, layout items, API params. Name is display-only.
- 2026-03-02: Single server.on('upgrade') dispatcher routes WebSocket connections — prevents dual-handler race condition
- 2026-03-02: Layout entries must exist synchronously (useMemo) before render — useEffect races with react-grid-layout's onLayoutChange
- 2026-03-02: Buttons inside react-grid-layout drag handles need onMouseDown stopPropagation to receive clicks
- 2026-03-02: Session close from UI uses destroy (force=true) for immediate teardown — graceful close hangs on interactive prompts
- 2026-03-03: CSS auto-grid with 400px min column width replaces react-grid-layout — simpler, auto-sizes, drag-to-swap only
- 2026-03-03: useCSSTransforms=false required for sharp xterm.js text on Retina — CSS transforms cause canvas blur
- 2026-03-03: xterm.js scrollback=0 since tmux handles scrollback — eliminates scrollbar
- 2026-03-03: Backend cross-references session state files with tmux liveness — stale ended sessions show as active if tmux is alive
- 2026-03-03: Deduplicate sessions by tmux_session name, keeping most recent state file
- 2026-03-03: Single-pane mode on ≤1024px — one terminal + bottom tab bar, same view for iPad and phone
- 2026-03-03: Min column width 600px (was 400px) — fewer columns but more readable
- 2026-03-03: Grid row spanning — terminals in columns without last-row items stretch to fill full height
- 2026-03-03: Session panel overlay breakpoint widened from 768px to 1024px to match single-pane breakpoint
- 2026-03-04: Use Gas Town alongside OS — GT for multi-agent code execution, OS for intelligence/tools/workflows
- 2026-03-04: Dolt is the best candidate for OS state backend — queryable, versioned, concurrent-safe, federable
- 2026-03-04: Gas Town rig = one piece of the OS. OS sessions can start/manage rigs.
- 2026-03-04: Obsidian as potential visual layer over project artifacts (point vault at `projects/`)

## Open Questions
- Which OS skills should be symlinked to `~/.claude/skills/` for global access in dispatched sessions?
- When SDK Issue #583 is fixed, remove the monkey-patch from engine.py
- 1Password: `op run` vs `op read` for secret injection? Split `.env` into urls + secrets?
- Should onboarding branch be maintained separately, or just point new engineers at main?
