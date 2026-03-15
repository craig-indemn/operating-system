# OS Development

Development of the operating system itself — the skills, systems, and infrastructure that make Indemn's connected intelligence layer work. Covers the dispatch system, systems framework, skill improvements, and meta-level architecture of the OS.

## Status
**Session 2026-03-15-a (complete)**: Completed all three tasks from the 2026-03-14-b handoff. (1) **Rewrote the design doc** — 816 insertions, 492 deletions across 10 outdated sections: Principle 1, Architecture Overview, Data Model, Registry, Storage Architecture, Context Assembly, Hive CLI, Session Initialization, Open Decisions, Implementation Phases. All now reflect the two-layer architecture, unified CLI, and context assembly agent model. (2) **Designed content system Hive integration** — cs.py stays as source of truth, workflow entity maps to idea level, integration lives in cs.py, full transition map (idea created through published), context assembly playbook searches entire Hive for topic + codebase + pipeline state + brand voice, context note includes system instructions to route session into content pipeline. (3) **Designed code development system Hive integration** — composes existing OS tools with Hive workflow entity as glue (no separate state store), systematic checkpointing via skills at decision points + session close, full lifecycle (design → review → plan → execute → code-review → test → deploy), context assembly playbook preserves full reasoning trail across 20+ sessions to solve "losing the plot" problem. **Design is now complete. Next: create the implementation plan.**

**Session 2026-03-14-b (complete)**: Deep dive on context assembly and data architecture. Major shifts: (1) Context assembly is an LLM agent using Hive CLI as toolkit, not a fixed algorithm. (2) Two-layer data model — entities in MongoDB only (no YAML files), knowledge as git-tracked markdown files differentiated by tags (not separate type schemas). (3) Workflow entities stored in Hive but lifecycle owned by systems (content, code dev, etc.). (4) 14-command unified CLI surface with transparent entity/knowledge routing. (5) Reconciled session initialization — dedicated context assembly session writes comprehensive context note, working session starts hydrated. (6) System-specific context playbooks — each system's skill defines what context to gather. Resolved all open gaps: context window budgeting (not a problem), entity aliasing (LLM handles it), cross-type queries (LLM + CLI), mobile (deferred). **Full artifact at `artifacts/2026-03-14-hive-context-assembly-redesign.md`.**

**Session 2026-03-14-a (complete)**: Major Hive architecture evolution — replaced "everything is a note" with **typed record system** (YAML-defined types, entity schemas, typed relationships). Added self-improvement via `hive feedback` command, code dev system integration framework, bidirectional external system sync framework (moved from Phase 6 to Phase 3), user-driven Wall arrangement. Stress-tested: git scalability (synced records gitignored), Obsidian dropped (Hive UI replaces), concurrent access noted, quick capture flow (always note first, reclassify async).

**Session 2026-03-09-a (complete)**: Continued Hive design — full UI design (Wall + Focus Area layout, tile system, visual encoding, fluid sizing, session initialization flow), flywheel mechanics (emergent from linked notes, not coded pipelines), content system integration framework, generic system integration contract. Design doc updated with 5 new major sections and 17 new decisions.

**Session 2026-03-08-a (complete)**: Designed The Hive — the awareness and connective tissue layer for the operating system. Extended brainstorming session covering vision, data model, ontology, storage architecture, context assembly, and system integration model. Full design document produced. This is a major architectural addition to the OS.

**Previous**: 2026-03-05-a shell sessions. 2026-03-04-a Gas Town/Dolt. 2026-03-03-c responsive mobile. 2026-03-03-b remote access. 2026-03-03-a UI polish. 2026-03-02-d browser-tested V1. 2026-03-02-c built V1. 2026-03-02-b designed it.

**Onboarding branch** — is 40+ commits behind main. DO NOT rebase while parallel sessions active.

**Next session should:**
1. **Create the implementation plan** — the design is complete. All sections of the design doc are current. Content system and code development system integrations are fully designed. Build the phased implementation plan with tasks, dependencies, and acceptance criteria.

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
| 2026-03-08 | [hive-design](artifacts/2026-03-08-hive-design.md) | The Hive — unified awareness/knowledge/work system. Data model, ontology, context assembly, system integration, 6-phase implementation plan |
| 2026-03-14 | [hive-context-assembly-redesign](artifacts/2026-03-14-hive-context-assembly-redesign.md) | Context assembly deep dive — LLM agent model, two-layer data architecture (entities in MongoDB / knowledge as files), workflow entity pattern, vault restructuring |

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
- 2026-03-05: OS Terminal supports shell sessions — plain tmux terminals alongside Claude sessions, created/deleted without session CLI
- 2026-03-08: The Hive is the awareness and connective tissue layer — it doesn't replace systems, it connects them
- 2026-03-08: ~~Everything is a note~~ SUPERSEDED by typed record system (2026-03-14)
- 2026-03-08: ~~Flat vault structure~~ SUPERSEDED by typed directories (2026-03-14)
- 2026-03-08: Awareness records: any typed record with system: and ref: fields points to external artifacts
- 2026-03-08: Local MongoDB, not Atlas — personal/cross-domain data stays private and local
- 2026-03-08: Local embedding model (Ollama), swappable via abstraction layer
- 2026-03-08: Controlled vocabulary via `ontology.yaml` — prevents tag fragmentation, evolves deliberately
- 2026-03-08: Context assembly produces session initialization instructions — knowledge + skills + reads + reminders, tailored by objective
- 2026-03-08: System CLIs handle their own Hive updates — each system manages its domain logic, Hive CLI is the low-level building block
- 2026-03-08: Skills must document Hive integration convention — new skills follow it, existing skills evolve incrementally
- 2026-03-08: Files are source of truth (native records), MongoDB is derived index — Git-trackable. Synced records use external system as source of truth.
- 2026-03-08: Graph expansion favors breadth — can't explore what you don't know about
- 2026-03-08: Migration is gradual — projects/ coexists with hive/, nothing breaks
- 2026-03-08: Hive UI lives in OS Terminal (Bloomberg-style) — kanban, graph, timeline views alongside sessions
- 2026-03-08: Hive notes for skills/systems enable self-aware context assembly — the system recommends relevant tools per session
- 2026-03-09: The Hive is the home screen — replaces OS Terminal as the front door, terminals are one view within it
- 2026-03-09: Wall + Focus Area layout — Wall surrounds Focus, breathes with activity level, toggle to full Overview
- 2026-03-09: Tiles are the only UI elements — no chrome, no buttons, no menus. The data is the UI.
- 2026-03-09: Fluid tile sizing — continuous scaling based on available space, not fixed breakpoints
- 2026-03-09: Rectangular tiles for MVP — honeycomb deferred (CSS grid is rectangle-native, hex is significantly harder)
- 2026-03-09: Visual encoding — color=type, accent/border=domain, brightness=status for glanceable scanning
- 2026-03-09: Two data sources — active sessions from sessions/*.json (real-time), everything else from Hive API
- 2026-03-09: UI reads from Hive only — all system data syncs into Hive backend, UI doesn't call external APIs
- 2026-03-09: Session initialization — ask objective FIRST, then retrieve context parameterized by topic+objective+system
- 2026-03-09: Flywheel is emergent from linked notes — no hard-coded pipelines between systems
- 2026-03-09: "Create linked note" is a first-class UI interaction — primary mechanism for thought accumulation
- 2026-03-09: Generic system integration framework — every system follows same contract for Hive awareness records
- 2026-03-09: Content system creates awareness records at each pipeline stage (idea→extraction→draft→publish)
- 2026-03-09: Don't hard-code system-specific logic in Hive UI — tiles are generic, any system plugs in automatically
- 2026-03-09: Completed sessions get Hive awareness records at session close — active state stays in sessions/*.json
- 2026-03-14: Everything is a typed record — YAML-defined types with schemas, replaces "everything is a note"
- 2026-03-14: Type system is configuration-driven — add YAML to .registry/types/, CLI auto-discovers, no code changes
- 2026-03-14: Entities are YAML, knowledge is Markdown — structured data vs rich text, clear separation
- 2026-03-14: Typed references replace generic wiki-links for entity relationships
- 2026-03-14: Typed directories replace flat vault — each type has a directory
- 2026-03-14: Wall arrangement is user-driven — priority → status → recency → drag-to-reorder. Not LLM at render time.
- 2026-03-14: `hive feedback` for self-improvement — feedback as notes, retrieval snapshots in Phase 2+
- 2026-03-14: Bidirectional sync framework for external systems — inbound pull/push/scheduled, outbound direct tile actions + session-based
- 2026-03-14: Synced records git-ignored in .synced/ directories — external system is source of truth
- 2026-03-14: Obsidian compatibility dropped — Hive UI replaces the need
- 2026-03-14: Quick capture always creates note first, reclassifies async — capture speed > classification accuracy
- 2026-03-14: Code development system is separate design effort — Hive defines generic contract only
- 2026-03-15: Content system: cs.py stays as source of truth for content lifecycle, Hive adds cross-system context
- 2026-03-15: Content system: Hive workflow entity maps to idea level (not piece level) — one workflow per idea, pieces are awareness records
- 2026-03-15: Content system: Hive integration lives in cs.py itself — system CLI owns its Hive updates, graceful degradation if Hive unavailable
- 2026-03-15: Content system: every pipeline transition creates a Hive knowledge record (including each draft version and feedback round — not too noisy, context assembly handles relevance)
- 2026-03-15: Content system: context assembly playbook searches entire Hive for topic (the source material), not just content pipeline state
- 2026-03-15: Code dev system: composes existing OS tools, Hive workflow entity is the glue — no separate state store
- 2026-03-15: Code dev system: checkpoints at decision points during sessions + session summary at close (both levels)
- 2026-03-15: Code dev system: skills that drive the work own the checkpointing — brainstorming skill creates decisions, debugging skill creates root cause analyses, etc.
- 2026-03-15: Code dev system: context note includes full design decisions with rationale (not compressed summaries) — this is what prevents "losing the plot" across 20+ sessions

## Open Questions
- Which OS skills should be symlinked to `~/.claude/skills/` for global access in dispatched sessions?
- When SDK Issue #583 is fixed, remove the monkey-patch from engine.py
- 1Password: `op run` vs `op read` for secret injection? Split `.env` into urls + secrets?
- Should onboarding branch be maintained separately, or just point new engineers at main?
- Hive: Note creation mechanics — explicit CLI calls vs hooks vs hybrid?
- Hive: Sync trigger — on CLI operations, Git hooks, file watcher, or manual?
- Hive: Linear bidirectional sync — conflict resolution, trigger mechanism?
- Hive: Session lifecycle — RESOLVED: first message via tmux send-keys, session asks objective, then retrieves context
- Hive: Which Ollama embedding model? nomic-embed-text vs mxbai-embed-large?
- Hive: Context assembly LLM — session assembles from raw notes, or separate LLM call in CLI?
- Hive: Beads coexistence — mirror as awareness records? Replace with Linear?
- Hive: Graph quality — archival conventions, stale note detection, noise prevention?
- Hive UI: Mobile experience — important but not yet designed
- Hive UI: Self-improvement mechanisms — RESOLVED: `hive feedback` command, feedback as notes
- Hive UI: Detailed note creation walkthroughs — real scenario end-to-end flows needed (through typed system)
- Hive: Code development system integration — RESOLVED: separate system design, Hive provides generic contract
- **CRITICAL: Hive context assembly redesign for typed records** — entity anchor identification, relationship traversal, objective-aware filtering, context window budgeting, entity aliasing/fuzzy matching
- Hive: Concurrent access — multiple sessions creating records simultaneously, need atomic writes
- Hive: MongoDB auto-start — should `hive` commands auto-start MongoDB if not running?
