# Notes: 2026-04-03-message-actor-architecture-research.md

**File:** projects/product-vision/artifacts/2026-04-03-message-actor-architecture-research.md
**Read:** 2026-04-16 (full file — 529 lines)
**Category:** design-source (message architecture research)

## Key Claims

- Research on actor model, event-driven architecture, message infrastructure for Python+MongoDB+FastAPI.
- Actor frameworks surveyed: Erlang/OTP, Akka, Orleans, Proto.Actor.
- **Key insight: You don't need an actor framework.** Actors are external (humans, associates). The "actor runtime" is queue + routing system.
- Orleans virtual actor pattern = associates spin up on message arrival.
- Message granularity: emit on state transitions, @exposed methods, create/delete. NOT every field change.
- **Transactional Outbox Pattern**: entity save + outbox write in same MongoDB transaction.
- MongoDB Change Streams insufficient as primary message mechanism — lose business intent.
- **Recommended: Hybrid RabbitMQ (event bus / routing) + MongoDB (per-actor work queues).**
- Later SUPERSEDED: 2026-04-02-core-primitives-architecture.md (same timeframe) and 2026-04-09 artifacts moved to MongoDB-only messages, dropping RabbitMQ.
- Per-actor work queue as MongoDB collection with priority, aging, escalation, claim/complete.
- Context enrichment: Pattern C — enriched events with role-based context rules (resolve related entities at routing time).

## Architectural Decisions

- **Outbox pattern** for entity save + message creation — RETAINED as principle (becomes save_tracked()).
- **Selective emission** (state transitions + @exposed + create/delete only) — RETAINED.
- **Correlation IDs** for cascade tracing — RETAINED.
- **Cascade depth limit** (default 10) — RETAINED.
- **Idempotent processing** — RETAINED (visibility timeout + max attempts).
- **Work queue as MongoDB collection** — RETAINED (message_queue + message_log in final).
- **findOneAndUpdate for atomic claim** — RETAINED.
- **RabbitMQ as event bus (hybrid)** — LATER REJECTED in favor of MongoDB-only per 2026-04-02-core-primitives-architecture.md + subsequent artifacts.
- **Context enrichment per role** — RETAINED as "scoped watches with field_path/active_context" (2026-04-10).

## Layer/Location Specified

- Outbox + publisher + work queue all in kernel code.
- No kernel/harness boundary yet (pre-Session 5).
- MongoDB collection names: outbox, work_queue — later became message_queue + message_log.

## Dependencies Declared

- MongoDB (Motor + Beanie)
- RabbitMQ / Amazon MQ (later removed from architecture)
- Redis Streams (evaluated, not chosen)
- NATS JetStream (evaluated, not chosen)
- MongoDB Change Streams (evaluated, used as secondary)

## Code Locations Specified

- WorkQueueItem as Beanie Document.
- find_one_and_update pattern for atomic claim.
- Escalation sweep as periodic job.
- Router reads Role routing rules + writes to per-actor work queue with enriched context.

Later became:
- `kernel/message/schema.py` (Message + MessageLog)
- `kernel/message/bus.py` + `mongodb_bus.py` (Protocol + impl)
- `kernel/message/emit.py` (watch evaluation + message creation)
- `kernel/watch/cache.py`, `evaluator.py`, `scope.py`

## Cross-References

- 2026-04-02-core-primitives-architecture.md (contemporaneous, integrates these findings)
- Later artifacts replace RabbitMQ with MongoDB-only messaging.
- Orleans virtual actor pattern → later harness pattern (one harness image serves many associates, spins up on demand).

## Open Questions or Ambiguities

- RabbitMQ vs MongoDB-only for messaging → resolved: MongoDB-only. "One database, one transaction boundary. Entity+message atomicity is trivial with MongoDB transactions. No dual-write problem."
- Hybrid pattern (RabbitMQ routing + MongoDB work queue) was later dropped in favor of single-queue simplicity.

**No Finding 0-class deviation introduced here.** The message architecture principles (outbox, selective emission, correlation, cascade limit, idempotency, atomic claim) are all retained in the final architecture. The RabbitMQ-as-event-bus recommendation was later rejected in favor of MongoDB-only messaging. Implementation matches.

This artifact informs the Phase 1 save_tracked() and message queue design.
