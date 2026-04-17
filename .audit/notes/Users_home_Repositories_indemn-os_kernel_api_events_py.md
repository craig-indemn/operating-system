# Notes: /Users/home/Repositories/indemn-os/kernel/api/events.py

**File:** /Users/home/Repositories/indemn-os/kernel/api/events.py
**Read:** 2026-04-16 (full file — 92 lines)
**Category:** code

## Key Claims

- Module docstring: "Events stream — Server-Sent Events backed by MongoDB Change Stream. [G-47]. Provides filtered NDJSON event streams for harnesses and consumers. The events stream watches the message_queue collection and delivers matching events as newline-delimited JSON."
- `stream_events(actor, interaction, entity_type, current_actor)` — GET endpoint at `/api/_stream/events`.
- Query params filter the stream: `actor`, `interaction`, `entity_type`.
- Builds MongoDB Change Stream pipeline on `message_queue` collection, filtered by `org_id` + optional filters.
- For each change, yields newline-delimited JSON (ndjson) with id, entity_type, entity_id, event_type, target_role, correlation_id, event_metadata.
- Interaction filter uses helper `_is_related_to_interaction` that checks context, entity_id, and event_metadata for matching interaction_id.

## Architectural Decisions

- Implements the `indemn events stream` backend per design (2026-04-10-realtime-architecture-design.md).
- Server-Sent Events / ndjson format — suitable for long-running subprocess consumption by harnesses.
- Scope filter: `target_actor_id == actor OR target_actor_id IS NULL` — delivers both scoped-to-this-actor messages AND unscoped messages that match the role.
- Interaction filter checks multiple places where interaction_id might live (context, entity_id, event_metadata) — defensive.
- Media type `application/x-ndjson` — streaming JSON lines.
- Auth via middleware (`get_current_actor`) — requires bearer token.

## Layer/Location Specified

- Kernel code: `kernel/api/events.py`.
- Runs in kernel API server process.
- Direct database access to `message_queue` Change Stream.
- Per design: the `indemn events stream` CLI is a long-running subprocess that consumes this endpoint. The harness runs `indemn events stream` via subprocess and reads stdout.

**Per design placement:**
- Server: kernel API (this file) — CORRECT
- Client: harness process via CLI subprocess — the harness image should be the consumer

**Currently:**
- The server exists (this file). ✓
- The CLI command to consume it likely exists at `kernel/cli/events_commands.py`.
- Harnesses that would consume the stream DON'T EXIST (per Finding 0).
- The kernel-side agent execution in `kernel/temporal/activities.py` does NOT use this events stream. The design says harnesses should consume it; the current in-kernel agent doesn't need to because it runs in the same process as the watch evaluation.

**No layer deviation for this file itself.** It correctly provides the server side of the events stream pattern. The gap is that no harnesses exist to consume it.

## Dependencies Declared

- `fastapi.APIRouter`, `Depends`, `Query`
- `fastapi.responses.StreamingResponse`
- `bson.ObjectId`
- `orjson` (imported locally in generator)
- `kernel.auth.middleware.get_current_actor`
- `kernel.db.get_database`
- MongoDB Change Streams on `message_queue` collection

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/api/events.py`
- Router: `events_router`, mounted at `/api/_stream` prefix
- CLI client: `kernel/cli/events_commands.py` (implements `indemn events stream ...`)

## Cross-References

- Design: 2026-04-10-realtime-architecture-design.md Part 8 (`indemn events stream` as the one new CLI primitive)
- Phase 4-5 spec §5.4 (events stream endpoint + CLI)
- Harness pattern usage: `subprocess.Popen(["indemn", "events", "stream", "--actor", associate_id, ...], stdout=PIPE)`

## Open Questions or Ambiguities

**No Pass 2 layer deviation for this file.**

**Secondary observations:**
- Auth uses the current_actor's org_id to filter — one actor can only see events for their own org. Good.
- Actor filter uses `$or` to include both scoped-to-actor messages AND unscoped messages — correct for the harness use case (a harness may receive both kinds).
- Interaction filter is defensive (checks 3 places) — addresses the inconsistency in where interaction_id is stored.
- The NDJSON format means consumers get one event per line — easy to parse with `for line in stream.stdout` in a harness.
- **The endpoint exists but no harness consumes it.** When harnesses are built per Finding 0's fix, this endpoint is ready to serve them.

This is a correctly-placed kernel API endpoint. The architectural fix is to add harness consumers.
