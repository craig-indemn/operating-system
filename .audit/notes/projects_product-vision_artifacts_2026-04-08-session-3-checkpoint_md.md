# Notes: 2026-04-08-session-3-checkpoint.md

**File:** projects/product-vision/artifacts/2026-04-08-session-3-checkpoint.md
**Read:** 2026-04-16 (full file — 216 lines)
**Category:** session-checkpoint

## Key Claims

- **End of session 3** (2026-04-02 to 2026-04-08): design work (Layers 1-5), core primitives, adversarial reviews, implementation plan draft.
- **What was decided**: 2 implementation primitives (Entity + Message), 4 conceptual primitives (Entity + Message + Actor + Role), uniform Entity class, Python/Beanie/Pydantic/MongoDB, FastAPI + Typer, skills auto-generated, @exposed decorator, LangChain deep agents, same pattern async+real-time, adapters are actors, hand-build first, Indemn dog-foods.
- **10 hardening requirements** (non-negotiable): version field, transactional entity+message saves, correlation+causation+depth IDs, visibility timeout, cascade depth + circuit breaker, idempotent processing utilities, selective emission, MessageBus abstraction, routing as entity, cached evaluation (60s TTL).
- **THE unresolved question** at end of session 3: "How does the system wire entity changes to consequences?" 4 approaches tried (routing rules / implicit wiring / connections / unified subscriptions) — none clicked.
- **Resolved in session 4**: watches on roles.
- 28 artifacts produced through session 3.

## Architectural Decisions

- **2 implementation primitives**: Entity + Message. Everything composes.
- **4 conceptual primitives**: Entity + Message + Actor + Role (pre-Integration, pre-Organization as primitive).
- **Uniform Entity class** — no mixins.
- **Same associate pattern for async and real-time** — channels are I/O.
- **Entity methods are deterministic** — LLM reasoning via associates.
- **Adapters are actors** — receive messages about entity changes, sync to external.
- **MessageBus abstraction** for swappable backend (RabbitMQ later).

## Layer/Location Specified

- **5-layer architecture** at this stage:
  - L1 Entity framework (kernel)
  - L2 API + CLI + Skills (kernel, auto-generated from entities)
  - L3 Associate system (LangChain deep agents with CLI sandbox, workflow entity, LangSmith evals) — **worker/harness location not yet specified**
  - L4 Integrations (entity ops own external connectivity, adapters)
  - L5 Experience (UI on entity queries, role-based, auto-generated admin)
- **Implementation plan drafted**: Phase 0 (dev framework) → Phase 1 (core) → Phase 2 (entities) → Phase 3 (associates + integrations) → Phase 4 (Indemn on OS) → Phase 5 (first customer). Later evolved to 8 phases.

**Finding 0 relevance**:
- L3 Associate system described as "deep agents with skills + CLI sandbox" but deployment location was NOT specified.
- Hardening requirement #10 mentions "cached evaluation of routing/wiring (in-memory, 60s TTL)" — this is for watch cache, not agent execution.
- The session ended with the wiring question unresolved; subsequent session 4 answered it but agent execution location remained deferred until session 5 (realtime-architecture-design).

## Dependencies Declared

- Python + Beanie + Pydantic + MongoDB (stack)
- FastAPI (API) + Typer (CLI)
- LangChain deep agents (associate harness)
- MongoDB-only messaging for MVP; RabbitMQ later
- LangSmith (evaluations)
- findOneAndUpdate (atomic claiming)

## Code Locations Specified

- Conceptual (no paths). The 5 layers described.
- Hardening requirements enumerate 10 kernel fields/mechanisms.

## Cross-References

- `2026-04-02-core-primitives-architecture.md` — source of truth for architecture decisions at that time
- Session 1-2 artifacts (vision, research, domain model)
- `2026-04-07` adversarial review artifacts (challenge-* files)
- Session 4 checkpoint (resolves wiring question)
- Session 5 checkpoint (adds Integration primitive, Attention, Runtime, harness pattern)

## Open Questions or Ambiguities

At end of session 3, all open:
- Wiring question (resolved in session 4 as watches on roles)
- Testing/debugging CLI
- Declarative system definition
- Bulk operations
- Rule composition details
- Build order + acceptance criteria
- Stakeholder engagement

**Supersedence note**:
- 2 implementation primitives → evolved to 6 structural primitives (session 4 + 5).
- 10 hardening requirements SURVIVE.
- 4 conceptual primitives → evolved to 6 (add Organization + Integration).
- Implementation plan phases → evolved to 8.
