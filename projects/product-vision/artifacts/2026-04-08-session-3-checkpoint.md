---
ask: "Comprehensive checkpoint of session 3 — what's decided, what's unresolved, and what the next session needs to tackle"
created: 2026-04-08
workstream: product-vision
session: 2026-04-07/08
sources:
  - type: conversation
    description: "Craig and Claude sessions 3, 2026-04-02 through 2026-04-08"
---

# Session 3 Checkpoint

## What This Session Accomplished

### Design Work (Layers 1-5)
- Layer 1: Entity framework — Beanie + Pydantic + MongoDB, Python classes, services, events
- Layer 2: API (FastAPI) + CLI (Typer) + Skills auto-generated, @exposed decorator
- Layer 3: Associate system — deep agents with skills + CLI sandbox, workflow entity, LangSmith evals
- Layer 4: Integrations — entity operations own external connectivity, adapter pattern
- Layer 5: Experience — UI on entity queries, role-based views, auto-generated admin

### Core Primitives
- Two implementation primitives: Entity + Message
- Four conceptual primitives: Entity + Message + Actor + Role
- Messaging: MongoDB-based, transactional with entity saves
- Entity changes generate messages, messages route to actors, actors process and change entities

### Adversarial Review
- 5 independent agents challenged the architecture from: insurance practitioner, distributed systems, developer experience, real-time systems, MVP buildability perspectives
- Core primitives VALIDATED by all 5
- Implementation HARDENED with 10 requirements

### Key Decisions Made
- Uniform Entity class — no mixins, configuration-driven activation
- MongoDB-only messaging for MVP — findOneAndUpdate for atomic claiming
- Same associate pattern for async and real-time — channels are just I/O
- Associates + skills = the rules engine (no separate rules engine)
- Build order: hand-build 3-5 entities first, extract framework, parallelize
- Adapters are actors in the messaging system (entity changes auto-sync via messages)
- Pydantic, Beanie, FastAPI, Typer, RabbitMQ (later), LangSmith for evals
- GIC email-to-AMS as case study for pressure testing

### Implementation Plan Drafted
- Phase 0 (dev framework) → Phase 1 (core) → Phase 2 (entities) → Phase 3 (associates+integrations) → Phase 4 (Indemn on OS) → Phase 5 (first customer)
- Internal CRM/CS as first use case

## What's DECIDED (Do Not Re-Litigate)

These decisions were made through extensive discussion and should be treated as settled:

1. **Entity + Message as the two implementation primitives** — everything composes from these
2. **Uniform Entity class** — one class, all capabilities, configuration-driven activation. No mixins.
3. **Python + Beanie + Pydantic + MongoDB** — the stack
4. **FastAPI for API, Typer for CLI** — auto-registered from entity classes
5. **Skills auto-generated from entity classes** — serve associates, developers, engineers
6. **@exposed decorator** — marks methods for API/CLI exposure
7. **Associates are LangChain deep agents** — same harness as Claude Code, skills + CLI sandbox
8. **Same associate pattern for async and real-time** — channels are just I/O, no separate architecture
9. **Entity methods are deterministic** — LLM reasoning goes through associates, not entity methods
10. **Associates + skills = the rules engine** — per-org business logic lives in skills, not a rules engine
11. **Adapters are actors** — integration adapters receive messages about entity changes and sync to external systems
12. **Build from scratch on MongoDB** — no open source CRM/ERP framework
13. **Build order: hand-build first** — 3-5 entities manually, extract framework, then parallelize
14. **Indemn dog-foods the OS** — internal CRM/CS as first use case
15. **Entity operations own external connectivity** — adapter pattern, no artificial system categories

### Hardening Requirements (Non-Negotiable for Foundation)
1. Version field on every entity (optimistic concurrency)
2. Transactional entity+message saves (MongoDB transactions)
3. Correlation ID + causation ID + depth on every message
4. Visibility timeout on claimed messages (stuck recovery)
5. Cascade depth tracking + circuit breaker
6. Idempotent message processing utilities
7. Selective emission (state transitions + @exposed methods only, not every field change)
8. MessageBus abstraction (interface for swappable backend)
9. Routing/wiring as configurable entity (per org, via CLI)
10. Cached evaluation of routing/wiring (in-memory, 60s TTL)

## What's UNRESOLVED (The Next Session Must Tackle)

### THE Core Question: How Does the System Wire Entity Changes to Consequences?

When an entity changes, other things need to happen: associates need to process, external systems need to sync, humans need to see updates, deterministic logic needs to run. HOW this wiring works is the core unsolved design question.

We explored several approaches:

**Approach 1: Routing Rules as separate entities (RoutingRule)**
- Per org, configurable via CLI, conditions + target role + optional action
- Evaluated when entities save
- Problems: concept felt unintuitive to Craig. Separate from the actors they target. Could become a mess with many rules.

**Approach 2: Implicit wiring from configuration**
- Integration connected → auto-syncs its entity types
- Associate has triggers → auto-activates on matching events
- Role defined → humans see their entities
- Problems: creates TWO systems — implicit for simple, explicit (rules) for complex. Craig rejected this.

**Approach 3: Connections (graph of connected things)**
- Building a system = drawing a graph of connections
- Email → Associate, Submission → AMS, Submission(needs_review) → Underwriter
- Same mechanism for all cases
- Problems: still fuzzy on implementation. Might just be routing rules renamed. Craig felt we were losing sight of the overall vision.

**Approach 4: Unified subscriptions on actors**
- Every actor has subscriptions (what entity changes it cares about)
- Same concept on associates, integrations, and humans
- Problems: explored briefly, not fully developed.

### WHY This Is Hard

The wiring mechanism needs to handle ALL of these with ONE concept:
- Associate triggers (email arrives → associate processes)
- External sync (submission changes → AMS updates)
- Human notifications (submission needs review → underwriter sees it)
- Deterministic pre-processing (USLI in subject → set type without LLM)
- Cross-entity triggers (quote accepted → binding process starts)
- Conditional logic (premium > $50K → also notify senior underwriter)

Each approach we tried handles SOME of these naturally but forces others into an awkward pattern.

### Craig's Requirements for the Solution
- Must be intuitive — not just technically sound
- Same mechanism for simple and complex cases (not "implicit + explicit")
- Visible — you can see the entire system behavior at a glance
- Configurable via CLI — an agent or FDE can set up and modify
- Must align with the overall vision of simple primitives that compose infinitely
- Must scale from simple (5 rules) to complex (50+ rules) without becoming opaque

### Other Unresolved Items
- Detailed roles and time allocations
- Final roadmap synthesis
- Vision document consolidation (20+ artifacts → one narrative)
- Stakeholder engagement strategy
- Champion strategy (how Craig presents to the company)
- End-to-end scenario tracing (deferred until wiring question is resolved)

## All Artifacts (28 total)

### Vision (Sessions 1-2)
| Artifact | What |
|----------|------|
| source-index | 62+ source materials |
| associate-domain-mapping | 48 associates mapped to entities |
| domain-model-research | 70 entities validated from 5 angles |
| domain-model-v2 | 44 aggregate roots, DDD-classified |
| the-vision-v1 | Original vision — insurance lab |
| the-vision (v2) | Factory framing (stale — needs OS framing) |
| os-for-insurance | Core OS framing |
| why-insurance-why-now | Industry context, flywheel, automation spectrum |
| platform-tiers-and-operations | Three tiers, Tier 3 as dev model, operations |
| associate-architecture | Deep agents, skills, evaluations |
| entity-system-and-generator | Entity generator, build vs buy, CRM/AMS |
| session-2-checkpoint | Session 2 comprehensive summary |
| 5 context docs | business, product, architecture, strategy, Craig's vision |
| session-notes | Unreduced vibes from session 1 |

### Design (Session 3)
| Artifact | What |
|----------|------|
| core-primitives-architecture | THE source of truth — Entity + Message, hardened, uniform |
| design-layer-1-entity-framework | Entity + API/CLI — Beanie, Pydantic, FastAPI, Typer |
| design-layer-3-associate-system | Associates, skills, workflows, evaluations |
| design-layer-4-integrations | Adapter pattern, entity ops own connectivity |
| design-layer-5-experience | UI, role-based views, admin UI |
| implementation-plan | Phases 0-5, parallel sessions, timeline |

### Research (Session 3)
| Artifact | What |
|----------|------|
| message-actor-architecture-research | Actor model, event-driven patterns, infrastructure |

### Adversarial Reviews (Session 3)
| Artifact | What |
|----------|------|
| challenge-insurance-practitioner | Missing entities, broken workflows, state machines |
| challenge-distributed-systems | Transaction boundaries, polling, cascades, concurrency |
| challenge-developer-experience | Concept count, routing undefined, observability |
| challenge-realtime-systems | Two-mode problem, voice latency, concurrency |
| challenge-mvp-buildability | Timeline, over/under-engineering, what to ship |

### Checkpoints
| Artifact | What |
|----------|------|
| session-2-checkpoint | End of vision + start of design |
| session-3-checkpoint | THIS FILE — end of design, approaching roadmap |

## How to Resume (Next Session)

### Context Loading (in this order)
1. Read this checkpoint FIRST — it has the complete state
2. Read `artifacts/2026-04-02-core-primitives-architecture.md` — the source of truth for architecture decisions
3. If needed for the wiring question: read `artifacts/2026-04-07-challenge-distributed-systems.md` for the messaging infrastructure research, and `artifacts/2026-04-07-challenge-insurance-practitioner.md` for what real workflows need

### The Task
The next session should resolve THE core question: **how does the system wire entity changes to consequences?**

Approach this with fresh eyes. Don't start from "routing rules" or "connections" — start from the vision and first principles:
- The OS is simple primitives that compose infinitely
- Entity + Message are the two implementation primitives
- When entities change, the right things must happen (associates process, systems sync, humans see, deterministic logic runs)
- ONE mechanism for all cases, intuitive at any complexity level
- Configurable per org via CLI
- Visible at a glance

### What Craig Has Said That Matters
- "I want this to be foundational. I want a really clear mental model on how everything works and why."
- "It should be intuitive and self-evident."
- "High complexity or low complexity should use the same system."
- "The routing rules concept is not necessarily intuitive to me on how they work and why we need them."
- "We are losing sight of the overall vision."
- "I need fresh eyes on this."

### Craig's Parallel Work
- GIC email intelligence + Unisoft AMS automation — active case study (worktree: os-unisoft, project: gic-email-intelligence). Comprehensive exploration results in the session context.
- Hive blueprint system — related workflow orchestration pattern (projects/os-development/artifacts/2026-03-24-blueprint-*.md)
- These inform the design but the OS solution may differ from both
