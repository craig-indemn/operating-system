# Notes: 2026-04-07-challenge-realtime-systems.md

**File:** projects/product-vision/artifacts/2026-04-07-challenge-realtime-systems.md
**Read:** 2026-04-16 (JSON transcript — 2 lines; substantive content is the embedded prompt + agent response)
**Category:** design-pressure-test

## Key Claims

- Pressure test by "real-time systems engineer" persona. Focus: chat/voice/WebSocket/live collaboration/notifications latency & concurrency.
- **Two-mode problem (async queue + direct invocation)**: conflict scenario is routine, not edge-case. Voice associate + queue associate mutating same entity simultaneously produces silent data corruption.
- **Optimistic concurrency control (version fields + conditional writes)** is NOT OPTIONAL — without it, concurrent writes will produce silent divergence.
- **Voice latency budget** is well-studied: <300ms natural, 300-600ms tolerable, 600-1000ms awkward, >1000ms broken. LLM call alone is 800-2000ms.
- **WebSocket fan-out architecture**: MongoDB Change Streams + Redis Pub/Sub + subscription registry. One Change Stream per collection, application-level router, per-connection outbound buffer.
- **Introduced the "Interaction Host" pattern** (precursor to the harness pattern): stateful process per session, owns conversation history + entity cache + LLM thread + channel I/O. Never blocks on MongoDB for response path.
- **Entity Sync Worker** (async batch writer) applies entity operations from Interaction Hosts.
- **Voice-specific requirements**: pre-warmed agent context, speculative entity pre-fetching, async entity writes with call-end reconciliation, lighter LLM path for simple cases.

## Architectural Decisions

- **Two-mode split is architecturally dangerous** — need unified model where real-time IS queue-backed (direct invocation claims the queue entry, same as any actor).
- **Recommends NOT putting LLM in entity write path** — entity changes don't trigger synchronous LLM as side effect. Enqueue instead.
- **State machine transitions must be atomic** (conditional update filter on status + version).
- **Saga pattern for multi-entity operations** (MongoDB 4.0+ transactions or compensating transactions).
- **Actor-entity affinity during interactions** (soft-lock priority on entities the associate is actively using).

## Layer/Location Specified

- **Real-time layer = separate concern** that integrates with but doesn't depend on entity system for hot path.
- **Interaction Host**: stateful process per session. Owns conversation state in memory. "Never blocks on MongoDB for response path."
- **Entity Sync Worker**: background batch writer, single writer for entity changes from live interactions.
- **Bus**: Redis Streams (durable, ordered) + Redis Pub/Sub (fan-out to WebSocket servers).
- **WebSocket servers**: separate processes from API servers. Stateless except connection registry.
- **Voice service**: retains existing LiveKit architecture. Interaction Host integrates with it.

**Finding 0 relevance**: The Interaction Host pattern is the conceptual precursor to the harness pattern (2026-04-10-realtime-architecture-design). This pressure test articulated that real-time agent work belongs OUTSIDE the entity system's hot path, in a dedicated stateful component — which is exactly what the harness does. Spec + code deviated from this precursor principle.

## Dependencies Declared

- MongoDB Change Streams + transactions
- Redis (Streams for durability, Pub/Sub for fan-out)
- Node.js or Python async (stateful Interaction Host)
- LiveKit/WebRTC (voice)
- Anthropic LLM provider

## Code Locations Specified

No specific paths — conceptual design. Introduced:
- `Interaction Host` — per-session stateful process
- `Entity Sync Worker` — async batch writer
- `Subscription Registry` — in-memory for WebSocket fan-out

## Cross-References

- Project vision documents (pre-April 7)
- Feeds into: 2026-04-08-primitives-resolved.md, 2026-04-08-pressure-test-findings.md (synthesis), 2026-04-10-realtime-architecture-design.md (harness pattern), core-primitives-architecture (hardening requirements)

## Open Questions or Ambiguities

- At time of writing (April 7), the harness pattern wasn't yet formalized. The Interaction Host was the placeholder concept.
- Actor-entity affinity mechanism: surfaced as concept, resolved as **Attention** entity in 2026-04-10-realtime-architecture-design.md.

**Supersedence note**: All recommendations in this pressure test SURVIVE. The Interaction Host concept evolved into the harness pattern. Finding 0 is the architectural-layer deviation between this pressure test's guidance and the current implementation.
