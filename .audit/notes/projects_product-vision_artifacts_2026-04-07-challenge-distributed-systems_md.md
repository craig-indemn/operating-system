# Notes: 2026-04-07-challenge-distributed-systems.md

**File:** projects/product-vision/artifacts/2026-04-07-challenge-distributed-systems.md
**Read:** 2026-04-16 (JSON transcript — 2 lines; embedded prompt + agent response)
**Category:** design-pressure-test

## Key Claims

- Pressure test by "senior distributed systems engineer" persona. Focus: MongoDB + Beanie + Pydantic + FastAPI + message queue at scale.
- **Entity-message transaction boundary** is the #1 dangerous flaw — without it, OOM/deploy/crash between save and message creation loses messages.
- **Fix = Outbox Pattern via MongoDB transactions**: entity save + message creation in one `session.start_transaction()`. Atlas supports multi-doc txns. ~5-15% write latency cost.
- **Polling vs push**: at 50 actors × 5s polling = 10 qps, trivial. At 500 actors = 100 qps, fine. At 5K actors = connection limit + lots of empty polls. **Recommended: Change Streams** for sub-second latency + no polling load.
- **Cascade depth tracking** (depth field, root_message_id, parent_message_id) with hard stop at depth 10. Depth-exceeded messages → `circuit_broken` status + alert.
- **Duplicate suppression** via hash(entity_id, entity_version, event_type, actor_id) with time window.
- **Rate-limited fan-out**: single entity change → >10 messages → create one "fan-out" message dispatched by dedicated fan-out actor in batches.
- **Multi-tenancy thresholds**: M10 <100K docs/org fine; M30 handles 1M docs/org; M60+ or sharding above 10M/org. Index size must fit RAM.
- **Visibility timeout + `attempt_count` + `max_attempts`** for stuck messages. Claim query includes `OR (status=processing AND visibility_timeout<NOW)`.
- **Idempotent message handlers** required (because visibility timeout means duplicate processing can happen).
- **Routing rule caching** with 60s TTL. In-memory per API instance. 200 rules × 1K saves/hour = negligible if cached.

## Architectural Decisions

- **10 priority-ordered recommendations** (1-6 for initial implementation, 7-10 deferred):
  1. Transactional entity+message writes
  2. Visibility timeout
  3. Cascade depth + circuit breaker
  4. Idempotent handlers
  5. Correlation/causation IDs + depth
  6. Optimistic concurrency (version field)
  7. Routing rule caching
  8. Hot/cold message split
  9. MessageBus abstraction interface
  10. Change streams (replace polling)
- **Hot/cold message split**: `message_queue` (pending + processing) and `message_archive` (completed + failed). Move on completion (txn).
- **MessageBus abstraction interface** for swappable backend (MongoDB → RabbitMQ later).
- **Start with polling, migrate to Change Streams** when needed.
- **Don't shard MongoDB** for MVP (insurance volumes don't justify it; design data model with org_id prefix for future sharding).

## Layer/Location Specified

- Entity save + message emission: one MongoDB transaction on replica set.
- Outbox pattern (alternative): `_outbox` array on entity document.
- Messages: **two collections** (hot + cold). Hot is indexed for fast claim; cold is indexed for audit.
- Visibility timeout: fields on message (status, claimed_by, claimed_at, visibility_timeout, attempt_count, max_attempts).
- Cascade depth: fields on message (depth, root_message_id, parent_message_id).
- Routing rule cache: in-memory per API instance.
- MessageBus interface: abstraction layer for message publish/consume.

**Finding 0 relevance**: This pressure test did NOT address worker location (in-kernel vs. harness). It focused on message-system reliability + observability. Its recommendations survived into the kernel as implemented — the Finding 0 layer-placement issue is orthogonal to these patterns (they'd work in either architecture).

## Dependencies Declared

- MongoDB Atlas (replica set)
- MongoDB Change Streams
- Beanie ODM + Pydantic
- Potential RabbitMQ later (for message bus)
- Jaeger/Grafana Tempo/Datadog (OTEL export)

## Code Locations Specified

No paths — conceptual. Key patterns:
- `save_with_messages()` function wrapping save + emit in one transaction
- `Message` schema with the required fields
- `ProcessedLog` for idempotency tracking
- `MessageBus` Protocol

## Cross-References

- Feeds into: core-primitives-architecture (10 hardening requirements), primitives-resolved, pressure-test-findings synthesis, consolidated-architecture, all subsequent design artifacts

## Open Questions or Ambiguities

- **Outbox pattern vs. direct message_queue write in transaction**: Craig later chose DIRECT write (no separate outbox, per round-1 architecture ironing). Equivalent reliability, one fewer collection.
- **Cascade depth hard-stop value**: 10 mentioned here, confirmed in later artifacts.
- **Optimistic concurrency** (version field): mentioned here, confirmed in core-primitives-architecture hardening requirements.

**Supersedence note**:
- All 10 recommendations survive. Several were modified in implementation:
  - #1 Transactional writes → implemented as `save_tracked()` (confirmed in spec; later regressed in shakeout; later fixed per comprehensive audit).
  - #2 Visibility timeout → implemented.
  - #3 Cascade depth → implemented with max depth 10.
  - #4 Idempotent handlers → required by design; implementation discipline.
  - #5 Correlation/causation IDs → implemented.
  - #6 Optimistic concurrency → implemented via version field + conditional updates.
  - #8 Hot/cold split → implemented (message_queue + message_log).
  - #9 MessageBus abstraction → partial (kernel writes directly; Bus interface for potential broker migration).
  - #10 Change Streams → implemented for UI real-time; polling replaced in events stream.
