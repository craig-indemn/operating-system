# Notes: 2026-04-08-entry-points-and-triggers.md

**File:** projects/product-vision/artifacts/2026-04-08-entry-points-and-triggers.md
**Read:** 2026-04-16 (full file — 129 lines)
**Category:** design-source

## Key Claims

- **Two distinct concepts**:
  1. How external events enter the OS (**entry points** — infrastructure)
  2. How actors are triggered (**triggers** — actor model)
- **6 entry point types**:
  - Channel (web chat, voice, SMS) → creates Interaction entity, channel stays open as I/O
  - Webhook → creates/updates entity
  - API call → creates/updates entity
  - Polling → creates entity
  - CLI command → creates/updates entity
  - Form submission → creates entity
- **3 actor trigger types**:
  - **Message** (a watch on the actor's role matches an entity change) — the primary model
  - **Schedule** (cron expression fires)
  - **Direct invocation** (CLI/API call explicit) — used for testing + real-time
- **Channels are entry points, NOT trigger types.** Voice/chat create an Interaction entity; the actor is then triggered by a watch matching Interaction:created.
- **Every external case collapses into the same pattern**: entity created/changed → watches match → actors process.
- **Scheduled tasks are associates with schedule triggers.** Managed via CLI: `indemn associate create --trigger "schedule:*/1 * * * *"`.

## Architectural Decisions

- **Actor model is CLEAN**: actors don't know about WebSockets/SIP/Twilio. They know entities + CLI. Channel infrastructure creates entities and provides I/O. Actors read/write entities. Channel translates.
- **One uniform path for all external events**: entry point → entity change → watch → message → actor (or schedule → actor).
- **Direct invocation is a first-class trigger**, not a backdoor. Used for real-time (voice/chat) to avoid queue polling latency, and for testing/debugging.
- **Schedule trigger** creates queue item (per round 1 architecture ironing) so all work is visible in queue. Actor's watch does NOT need a schedule entry; the kernel scheduler directly creates queue items for scheduled associates.

## Layer/Location Specified

- **Channel infrastructure (voice/chat/SMS)** = separate from actor framework. Per later artifacts, this infrastructure lives in the harness image (the harness hosts the transport + the agent framework).
- **Webhook handler** = kernel API endpoint (`/webhook/{provider}/{integration_id}` per Phase 2-3).
- **Polling** = scheduled associate calling adapter (e.g., `indemn email fetch-new`).
- **CLI** = API mode (per infrastructure artifact).
- **Schedule** = OS scheduler creates queue items targeting scheduled associate's role; Temporal workflow claims.

**Finding 0 relevance**:
- "Channels create Interaction entity; actor is triggered by watch on Interaction:created" — CONFIRMS the harness pattern. The channel + transport + agent framework live together in the harness image; the kernel only sees the Interaction entity.
- "Actors don't know about WebSockets/SIP/Twilio" — strong argument for the transport-bundled-with-Runtime design. Current code has WebSocket in kernel (`kernel/api/websocket.py` for UI real-time, plus assistant endpoint), but the assistant as currently built has no transport-agnostic behavior either.

## Dependencies Declared

- Channel infrastructure (LiveKit/WebSocket/Twilio) — per-provider
- Webhook endpoint (kernel)
- Adapter registry (for webhook validation + parsing)
- OS scheduler (for cron trigger dispatch)

## Code Locations Specified

- Conceptual:
  - 6 entry points and the entities each creates.
  - 3 trigger types and how each activates an actor.
- Later implemented:
  - Channels → harness images (voice, chat, sms)
  - Webhook → `kernel/api/webhook.py`
  - Polling → scheduled associate in the async harness
  - CLI → `kernel/cli/` + auto-registration
  - Schedule → `kernel/queue_processor.py::check_scheduled_associates`

## Cross-References

- 2026-04-08-primitives-resolved.md (confirms 3 trigger types)
- 2026-04-08-kernel-vs-domain.md (establishes kernel primitives)
- 2026-04-10-integration-as-primitive.md (formalizes Integration including webhook dispatch)
- 2026-04-10-realtime-architecture-design.md (confirms channel = harness transport)
- 2026-04-13-documentation-sweep.md item 4 (inbound webhook dispatch)

## Open Questions or Ambiguities

- **Channel activation**: artifact says "Interaction entity created → watch matches → actor triggered." This is partially superseded: real-time channels also use **direct invocation in parallel** (per round 1 ironing — queue entry + direct invoke simultaneously) to avoid polling latency.
- **Scheduled work location**: unspecified here. Per realtime-architecture-design, async scheduled associates live in the async-deepagents harness. Current code has them as kernel Temporal activities → Finding 0.

**Supersedence note**:
- 6 entry points + 3 trigger types SURVIVE as the canonical set.
- "Channels are entry points, not trigger types" SURVIVES.
- Real-time latency concern resolved via direct invocation parallel path.
- Schedule trigger as synthetic queue item SURVIVES (per round-1 ironing).
