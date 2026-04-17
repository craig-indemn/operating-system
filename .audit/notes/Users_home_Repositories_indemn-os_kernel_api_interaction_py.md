# Notes: /Users/home/Repositories/indemn-os/kernel/api/interaction.py

**File:** /Users/home/Repositories/indemn-os/kernel/api/interaction.py
**Read:** 2026-04-16 (full file — 115 lines)
**Category:** code

## Key Claims

- Module docstring: "Interaction endpoints — handoff, transfer, and observation. [G-49, G-51]. Transfer: move an Interaction between actors/roles. Observe: start observing an Interaction without handling it."
- Two endpoints:
  - `POST /api/interactions/{interaction_id}/transfer` — change handling_actor_id or handling_role_id
  - `POST /api/interactions/{interaction_id}/observe` — open observing Attention
- Transfer logic:
  1. Close old handler's Attention (status → closed)
  2. Update Interaction.handling_actor_id or handling_role_id
  3. Re-target pending messages (update target_actor_id for pending messages context.interaction_id)
- Observe logic: creates Attention with purpose="observing", 1 hour TTL.
- Uses `interaction_cls.get_scoped(interaction_id)` — scoped query.
- Uses `save_tracked` with method metadata.

## Architectural Decisions

- Handoff is a field update on Interaction (`handling_actor_id` / `handling_role_id`) per design.
- Attention opens and closes as part of handoff — ties into the unified Attention mechanism.
- Re-targeting pending messages ensures queue items follow the new handler.
- Observe is a first-class state (per design) — Attention with purpose="observing", not a separate mechanism.
- Auth via `get_current_actor` — requires valid session.
- Does not validate role permissions to transfer (assumes middleware + entity layer handle it).

## Layer/Location Specified

- Kernel code: `kernel/api/interaction.py`.
- Handoff mechanics live in the kernel — correct per design.
- Per design (2026-04-10-realtime-architecture-design.md Part 6 Handoff): "Handoff between actors on a live interaction is a field update. The interaction entity has a handling actor. Transfer changes the handler. The runtime notices and switches modes."

**The endpoints match the design** — kernel updates the Interaction entity + Attention records. The Runtime (harness) is expected to watch the Interaction entity via Change Stream and react by switching modes. The kernel doesn't push to the Runtime — the Runtime pulls via Change Stream.

**No architectural-layer deviation for this file.**

## Dependencies Declared

- `fastapi` — APIRouter, Depends, HTTPException, Query
- `bson.ObjectId`
- `datetime`, `timedelta`, `timezone`
- `kernel.auth.middleware.get_current_actor`
- `kernel.db.ENTITY_REGISTRY`
- `kernel_entities.attention.Attention`
- `kernel.message.schema.Message` (for re-targeting pending messages)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/api/interaction.py`
- Mounted in: `kernel/api/app.py` via `interaction_router`

## Cross-References

- Design: 2026-04-10-realtime-architecture-design.md Part 6 (Handoff)
- Design: Part 7 (Voice Clients as Integrations)
- Phase 4-5 spec §5.6 (Handoff)
- `kernel_entities/attention.py` — Attention entity with purpose=observing
- `kernel_entities/runtime.py` — Runtime entity (not directly referenced, but handoff implies Runtime watches for changes)

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Handoff requires an Interaction entity definition; per the comprehensive audit, Interaction as a domain entity is not defined in the seed data (Phase 6/7 defines it, but Phase 6 hasn't run).
- Re-targeting pending messages via direct `update_many` bypasses save_tracked — this is a raw update without audit. For the handoff use case this may be acceptable (the audit is on the Interaction entity's save_tracked), but technically any message update should go through a consistent path.
- Role-based transfer (`to_role`) doesn't assign a specific actor — someone in that role must claim. The Runtime handling the conversation is expected to bridge turns to the queue targeting the role.
- Observe creates a 1-hour TTL Attention — UI should heartbeat to extend. If user just observes and leaves, Attention auto-expires.

**Dependency on harness existence**: The design says "The Runtime hosting the Interaction subscribes (via its harness's Change Stream) to updates on the Interaction entity. When handling_actor_id or handling_role_id changes, the Runtime's session logic switches." This requires a harness to exist and run. Per Finding 0, no harnesses exist yet. So this handoff endpoint works at the entity level (updates handler, closes/opens Attention) but the actual mode switch in a running harness can't happen — there are no running harnesses.

This file is correctly specified and implemented; it's waiting for harnesses to exist to be fully functional end-to-end.
