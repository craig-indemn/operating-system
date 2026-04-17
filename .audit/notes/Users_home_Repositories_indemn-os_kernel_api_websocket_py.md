# Notes: /Users/home/Repositories/indemn-os/kernel/api/websocket.py

**File:** /Users/home/Repositories/indemn-os/kernel/api/websocket.py
**Read:** 2026-04-16 (full file — 181 lines)
**Category:** code

## Key Claims

- Module docstring: "WebSocket handler — real-time entity updates via MongoDB Change Streams. [G-34]. Each WebSocket connection watches the database-level change stream, filtered by org_id. Clients send subscribe/unsubscribe messages to control which entity types and entities they receive updates for."
- `websocket_handler(websocket)` — endpoint handler. Auth via query param `token`.
- Module-level connection tracker: `_connections: dict[str, dict] = {}`.
- On connection: verify JWT, accept WebSocket, start background `_watch_changes` task.
- Handles incoming messages: `ping` → `pong`, `subscribe` → add filter, `unsubscribe` → remove filter.
- `_watch_changes` pipeline: `[{"$match": {"fullDocument.org_id": org_id}}]`, database-level `db.watch(pipeline, full_document="updateLookup")`.
- For each change, iterates active subscriptions, sends matching changes as `{"type": "entity_change", ...}` JSON.
- Helper functions: `_matches_filter`, `_collection_to_entity_type`, `_serialize_for_ws`.

## Architectural Decisions

- One MongoDB Change Stream per WebSocket connection, filtered by org_id.
- Subscriptions are client-side: the browser sends subscribe messages; the server filters the change stream accordingly.
- Authentication via query param (not header) — necessary for browser WebSocket API which can't set Authorization header directly.
- Cleanup: cancel watcher task on disconnect; remove connection from `_connections`.
- Subscription filter supports entity_type, entity_id, collection.

## Layer/Location Specified

- Kernel code: `kernel/api/websocket.py`.
- Runs in kernel API server process.
- Direct MongoDB access (uses `get_database()` which is inside trust boundary).
- Per design (2026-04-11-base-ui-operational-surface.md): "Real-time updates via MongoDB Change Streams filtered by current view query and pagination." WebSocket handler in kernel is correct.
- Per white paper § Service Architecture: "API Server... WebSocket for real-time UI updates." Correct placement.

**No architectural-layer deviation for this file.**

Note: This is the WebSocket for UI real-time updates, distinct from any chat-harness WebSocket that might be needed for the assistant (which the design implies but the current code doesn't implement).

## Dependencies Declared

- `fastapi.WebSocket`, `WebSocketDisconnect`
- `asyncio`
- `orjson`
- `uuid.uuid4`
- `kernel.auth.jwt.verify_access_token`
- `kernel.db.get_database`
- `kernel.db.ENTITY_REGISTRY` (for collection→entity mapping)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/api/websocket.py`
- Mounted in: `kernel/api/app.py` as a WebSocket route
- Paired with Phase 4-5 UI: `ui/src/api/websocket.ts` (client connection manager)

## Cross-References

- Design: 2026-04-11-base-ui-operational-surface.md §"Real-Time Update Filtering"
- Phase 4-5 spec §4.6 (Real-Time Updates via WebSocket)
- White paper § Production Requirements (WebSocket keepalive)
- `kernel/auth/jwt.py` — token verification

## Open Questions or Ambiguities

**No Pass 2 layer deviation for the UI WebSocket.**

**Secondary observations:**
- **WebSocket keepalive**: white paper says "the real-time UI channel, the chat harness — must send ping frames every 30-45 seconds." This WebSocket handler handles `ping` messages from the client but doesn't proactively send pings to keep the connection alive. May rely on client-side pings to prevent proxy timeouts.
- Database-level `db.watch()` rather than per-collection watches — single stream, filtered client-side via subscription. Efficient for many subscribed collections.
- Filter-aware per the spec requirement: subscriptions specify entity_type/entity_id/collection filters.
- Auth via query param: not ideal for security (URL logs can leak tokens) but required for browser WebSocket API compatibility. Standard tradeoff.
- `_serialize_for_ws` handles ObjectIds and datetimes for JSON transmission.

This file implements the UI real-time mechanism correctly. It's unrelated to Finding 0 — which concerns where agent execution lives, not how UI receives updates.

**Note on chat-harness WebSocket**: the design's chat-harness pattern would have a SEPARATE WebSocket endpoint served by the chat-deepagents harness image (not by the kernel API server). That WebSocket would carry the assistant conversation. Currently, the assistant is a kernel API endpoint (`kernel/api/assistant.py`), not a WebSocket, so no parallel chat-harness WebSocket exists. This is the broader Finding 0 — not this file's concern.
