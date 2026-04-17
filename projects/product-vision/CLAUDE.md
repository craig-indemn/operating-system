# Product Vision — The Indemn OS

This project contains the complete design, specifications, audit trail, and implementation status of the Indemn Operating System for Insurance.

**Read this file first in any session touching the OS.**

## CRITICAL: Session Bootstrap Protocol

Every session MUST read these files before doing any work:

1. **This file** (`CLAUDE.md`) — orientation + artifact index
2. **`INDEX.md`** § Status + § Decisions (2026-04-17 entries) — what happened, what's decided
3. **`artifacts/2026-04-16-vision-map.md`** — the authoritative design synthesis (23 sections, 104 files distilled). **This replaces reading individual design artifacts.**
4. **`artifacts/2026-04-17-session-summary.md`** — deployed infrastructure, credentials, bootstrap data

**DO NOT** re-read source design artifacts unless the vision map is ambiguous on a specific point blocking work. The synthesis artifacts exist so you don't have to.

## If Something Breaks

1. `indemn trace entity <EntityType> <id>` — what happened to this entity
2. `indemn trace cascade <correlation_id>` — full execution tree
3. `railway logs --service <service>` — container logs
4. Check Grafana Cloud traces — OTEL spans across all services
5. Read the relevant code: `kernel/` for kernel issues, `harnesses/` for harness issues, `indemn_os/` for CLI issues
6. **Fix and verify** — don't just deploy, confirm the fix works against the live system

## Design Integrity Rules

- **Vision IS the MVP.** Never simplify, collapse, or defer designed features without explicit approval from Craig.
- **Implement EXACTLY what the design specifies.** Every flag, parameter, and behavior. If the design says `--depth 2 --include-related`, the code has `--depth 2 --include-related`.
- **Verify against the live system.** Don't just commit — confirm it works E2E.
- **When Craig asserts something was designed**, search until you find it in the artifacts. His cross-session memory is authoritative.

## What the OS Is

An object-oriented insurance system where every insurance concept has schema + state machine + API + CLI. AI agents are a CHANNEL into the platform, not a separate system. Define an entity and it auto-generates its API, CLI, documentation (skills), permissions, and UI — the self-evidence property.

**Six primitives**: Entity, Message, Actor, Role, Organization, Integration.
**Seven kernel entities**: Organization, Actor, Role, Integration, Attention, Runtime, Session.

## Source of Truth — Artifact Index

### Foundational Design
| Artifact | What it is |
|---|---|
| `artifacts/2026-04-13-white-paper.md` | The canonical vision document — readable by anyone |
| `artifacts/context/craigs-vision.md` | Craig's underlying thesis — AI-first, agents building agents |

### Architecture (read the vision map, not the individual sources)
| Artifact | What it is |
|---|---|
| `artifacts/2026-04-16-vision-map.md` | **AUTHORITATIVE** — 23-section synthesis of 104 design files. Use this instead of reading individual design artifacts. |
| `artifacts/2026-04-16-alignment-audit.md` | Final discrepancy report — 9 items, all resolved 2026-04-17 |

### Implementation Specifications
| Artifact | What it is |
|---|---|
| `artifacts/2026-04-14-impl-spec-phase-0-1-consolidated.md` | **AUTHORITATIVE** Phase 0+1 spec (kernel framework) |
| `artifacts/2026-04-14-impl-spec-phase-2-3-consolidated.md` | **AUTHORITATIVE** Phase 2+3 spec (associate execution + integrations) |
| `artifacts/2026-04-14-impl-spec-phase-4-5-consolidated.md` | **AUTHORITATIVE** Phase 4+5 spec (base UI + real-time) |
| `artifacts/2026-04-14-impl-spec-phase-6-7-consolidated.md` | Phase 6+7 spec (CRM + GIC) — Phase 6 superseded by Craig's updated CRM design |

### Harness Pattern (Finding 0 resolution)
| Artifact | What it is |
|---|---|
| `artifacts/2026-04-16-harness-implementation-plan.md` | Governing plan + 7 gates |
| `artifacts/2026-04-16-async-harness-draft.md` | Gate 2 implementation draft (revised) |
| `artifacts/2026-04-17-chat-harness-scope.md` | Chat harness scope — 47 design claims, architectural decisions |

### Session Artifacts (2026-04-17)
| Artifact | What it is |
|---|---|
| `artifacts/2026-04-17-operational-surface-audit.md` | Gap report: 15 subsystems verified, deployment fixes, remaining gaps |
| `artifacts/2026-04-17-remaining-implementation-scope.md` | Every remaining gap scoped with design references |
| `artifacts/2026-04-17-session-summary.md` | Complete session record — what was built, deployed, verified |

### Design Sessions (chronological, synthesized in vision map)
| Session | Key artifacts |
|---|---|
| Session 2 (2026-03-30) | Entity framework, OS framing |
| Session 3 (2026-04-02) | Core primitives (Entity, Message, Actor, Role) |
| Session 4 (2026-04-07-09) | Pressure testing, unified queue, Temporal, OTEL, security |
| Session 5 (2026-04-10) | Real-time architecture, harness pattern, Runtime, Attention, Integration as primitive |
| Session 6 (2026-04-10-13) | Bulk ops, base UI, authentication, simplification pass, gap sessions |

## Current Implementation State

### Deployed Infrastructure (Railway)
| Service | URL | Status |
|---|---|---|
| indemn-api | https://indemn-api-production.up.railway.app | Running |
| indemn-queue-processor | (internal) | Running |
| indemn-temporal-worker | (internal) | Running |
| indemn-runtime-async | Temporal queue `runtime-{id}` | Running |
| indemn-runtime-chat | wss://indemn-runtime-chat-production.up.railway.app/ws/chat | Running |
| indemn-ui | https://indemn-ui-production.up.railway.app | Running |

External: MongoDB Atlas (`dev-indemn.mifra5.mongodb.net`), Temporal Cloud (`indemn-dev.hxc6t`), Grafana Cloud (OTEL traces), GCP Vertex AI (Gemini 2.0 Flash)

### What's Built and Verified
- All 15 kernel subsystems implemented with real logic (not stubs)
- All 9 audit discrepancies resolved
- G2.3 executed: kernel is LLM-agnostic (`grep -r "import anthropic" kernel/` returns nothing)
- Async harness: E2E verified (entity created → watch fired → Temporal → harness → LLM → entity updated)
- Chat harness: E2E verified (WebSocket → Interaction + Attention → agent responds)
- Trace commands: `indemn trace entity` + `indemn trace cascade` working
- OTEL traces flowing to Grafana Cloud
- Skill auto-generation wired to entity definition creation
- Entity GET with `--depth` and `--include-related` working
- UI deployed and serving

### What's NOT Built Yet
- Voice harness (Gates 5-6) — deferred to future session
- `indemn-os` package NOT published to any registry
- CLAUDE.md NOT in the indemn-os repo (Phase 0 deliverable)
- No operating methodology skills for Claude Code
- No kernel entity skills generated (7 kernel entities are Python classes, not EntityDefinitions)
- Conversation persistence (LangGraph checkpointer) stubbed in chat harness
- Grafana dashboards not configured

## The 8-Step Domain Modeling Process

How to build anything on the OS. Per remaining-gap-sessions § 5:

1. **Understand the business** — narrative, workflows, people, systems, pain
2. **Identify entities** — nouns in the business, fields, lifecycle, relationships
3. **Identify roles and actors** — who participates, permissions, watches
4. **Define rules and configuration** — per-org business logic, lookups, capability activation
5. **Write skills** — associate behavioral instructions in markdown
6. **Set up integrations** — external system connections, adapters, credentials
7. **Test in staging** — staging org, realistic data, validate end-to-end
8. **Deploy and tune** — production, monitor, add rules for patterns LLM keeps handling

## Key Invariants

- `grep -r "import anthropic" kernel/` → nothing (kernel LLM-agnostic)
- `grep -r "from kernel" harnesses/` → nothing (trust boundary intact)
- All entity saves go through `save_tracked()` (one transaction: entity + changes + watches)
- Harnesses authenticate via service token, use CLI subprocess for all OS operations
- Skills serve associates, developers, and engineers simultaneously (self-evidence)
- Selective emission: only creation + transitions + @exposed methods emit messages

## Decisions Log

All decisions are in `INDEX.md § Decisions` with date + rationale. Key 2026-04-17 decisions:
- Harness owns message completion via `indemn queue complete/fail`
- HITL dropped for async, kept for chat/voice
- Three-layer LLM config merge (Runtime + Associate + Deployment)
- Skill hash verification in CLI (harness trusts CLI surface)
- Vision IS the MVP — no collapsing, no deferring
- Streaming wire format: typed JSON over WebSocket
- Conversation persistence: LangGraph checkpointer in MongoDB

## Credentials

All in AWS Secrets Manager under `indemn/dev/shared/`:
- `mongodb-uri`, `temporal-cloud`, `jwt-signing-key`, `grafana-otlp`
- `google-cloud-sa`, `google-api-key`, `anthropic-api-key`
- `runtime-async-service-token`, `runtime-chat-service-token`

## How to Resume Work

1. Read this CLAUDE.md
2. Read `INDEX.md` § Status + recent Decisions
3. For specific subsystem work: read the relevant consolidated spec
4. For architectural questions: read the vision map
5. Do NOT re-read source design artifacts unless the vision map is ambiguous on a specific point
