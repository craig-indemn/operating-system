# Notes: 2026-04-02-core-primitives-architecture.md

**File:** projects/product-vision/artifacts/2026-04-02-core-primitives-architecture.md
**Read:** 2026-04-16 (full file — 521 lines)
**Category:** design-source (CORE — first primitives definition)

## Key Claims

- **Four primitives (at this stage)**: Entity, Message, Actor, Role. Everything composes from these.
- "The simplest possible foundation that composes into everything the OS needs to do."
- Entity: uniform class with all capabilities; activation is configuration-driven. "No mixins, no type hierarchy." SUPERSEDES the Layer 1 mixin approach.
- Message: the "nervous system." Notifications/tasks/HITL/triggers/events/channel-input/workflow-steps are all unified as Messages.
- Actor: human or associate, has a role and a queue.
- Role: permissions + routing + UI generation + CLI scoping + skill scoping + context scoping.
- **Selective emission decided**: only state transitions + @exposed methods + create/delete emit messages. Not every field change.
- **Workflows emerge** from entity state machines + messages + routing. No workflow orchestration engine.
- Every human actor can have a personal associate (same role, same queue) — foreshadows the default assistant.
- Real-time uses SAME associate pattern as async. "This was over-engineering" (re: separate Interaction Host). Same mechanism; differ only in trigger + I/O duration.

## Architectural Decisions

**Foundation hardening from adversarial review (2026-04-07):**
1. **Version field on every entity** — optimistic concurrency (prevents silent overwrite).
2. **Transactional entity+message atomicity** — same MongoDB transaction. "Cost: 5-15% write latency. Benefit: eliminates silent message loss." This is the #1 architectural invariant (later expressed as save_tracked()).
3. **Message infrastructure: MongoDB only (MVP)** — messages collection, findOneAndUpdate for atomic claim, polling (5-second adaptive). No separate broker. Scale path: Change Streams → Redis Pub/Sub → RabbitMQ (additive).
4. **Message schema** — includes correlation_id, causation_id, depth (cascade tracking), status, claimed_by, visibility_timeout, attempt_count, max_attempts, priority, due_by, context, changes. "Traceability from day one — impossible to retrofit."
5. **Visibility timeout** — 5 min for associates, 24 hours for humans. Stuck message recovery.
6. **Cascade depth tracking + circuit breaker** — default max 10 depth.
7. **Idempotent message processing** — handlers must be idempotent; ProcessedLog pattern.
8. **Routing rules as separate entity** — configurable per org via CLI, NOT hardcoded on entity classes.
9. **Selective message emission** — state transitions / @exposed / create/delete only.
10. **MessageBus abstraction (Protocol)** — MongoDB impl now, swappable later.

Also decided:
- **Context pre-loading** on messages (attached entity graph, configurable depth).
- **Personal AI assistant per human actor** — same role permissions, same queue.
- **UI auto-generated from role** — role defines what entities + queue; UI follows.
- **Build entities by hand first, extract framework.** Inverts the original plan.

**Real-time unification (this is notable):**
- "Real-time and async use the same associate pattern."
- Non-blocking entity saves during voice calls (`asyncio.create_task`).
- Interaction entity (normal entity) tracks conversation.
- Channel adapters provide I/O; associate doesn't know which channel.
- Rejected: separate Interaction Host, Message suppression during interactions, Entity Sync Worker, Redis Streams coordination, "system of engagement" vs "system of record."

## Layer/Location Specified

- **One implementation for async and real-time** — same associate pattern.
- **MongoDB as source of truth for messages** — unified queue.
- **Polling + findOneAndUpdate for claim** — MVP. Change Streams added as wake-up signal later.
- Non-blocking saves during voice (call-site concern, not architectural).
- MessageBus as Protocol interface (kernel) with MongoDB implementation.
- Routing rules as entity (data in DB, CLI-managed).

**Not yet specified:** kernel/harness boundary (comes in 2026-04-10-realtime-architecture-design.md), trust boundary (comes in 2026-04-13-infrastructure-and-deployment.md + later).

This artifact IS the source of:
- The "unified queue" concept
- Messages as THE primitive (unifying notifications/tasks/events/triggers/workflow-steps)
- Selective emission discipline
- Transactional atomicity invariant
- Correlation/causation/depth traceability
- Visibility timeout + idempotency
- MessageBus Protocol

## Dependencies Declared

- MongoDB (messages + entities + transactions + Change Streams later)
- Pydantic + Beanie
- Claude Code skill pattern
- deep agent pattern

## Code Locations Specified

- **"Mixins-based approach is superseded"** — one Entity class with uniform capabilities.
- `Entity.save()` with version guard — critical code pattern.
- `async def save_with_messages(entity)` — the transaction pattern (later becomes save_tracked()).
- `class Message(Document)` — schema.
- `Message.get_motor_collection().find_one_and_update(...)` — atomic claim.
- Routing rules cached in memory per org (60-second TTL) — later becomes watch cache.

## Cross-References

- Supersedes: 2026-03-30-design-layer-1-entity-framework.md (mixin-based approach)
- Informed by: adversarial review findings (2026-04-07 challenges — 5 reviewers)
- Foreshadows:
  - 2026-04-08-primitives-resolved.md (6 primitives final)
  - 2026-04-09-data-architecture-everything-is-data.md
  - 2026-04-10-realtime-architecture-design.md (harness pattern — BUT this artifact claims "real-time uses same associate pattern as async" which was later refined to "harness pattern per kind+framework")
  - White paper message architecture

## Open Questions or Ambiguities

Listed in artifact:
1. Interaction Host detailed design — RESOLVED in 2026-04-10-realtime-architecture-design.md as harness pattern
2. Routing rule code extension — eventually watches not code
3. Hot/cold message collection split — resolved as message_queue + message_log
4. Admin CLI for observability — implemented per Phase 1-5 specs
5. Testing patterns — resolved in spec

**IMPORTANT — this artifact's claim that "real-time and async use the same associate pattern" was refined, not contradicted, by 2026-04-10-realtime-architecture-design.md:**
- SAME pattern: CLI-based, skill-driven, deep-agent-based.
- DIFFERENT deployment: separate harness image per (kind, framework) combo.
- So the pattern stays the same; the DEPLOYABLE topology differs.

**Finding 0 connection:**
- This artifact emphasizes "same associate pattern for async and real-time" — the implementation respects this (both currently run in-kernel). But the 2026-04-10 artifact refines this to "same pattern, separate harness images outside kernel."
- The Phase 2-3 spec interpreted "same pattern" as "run in one place (kernel)" — missing the 2026-04-10 refinement.

**No new Finding 0-class deviation introduced here. This artifact's message architecture matches what's built; the real-time unification claim was later refined to harness-per-framework, not contradicted.**
