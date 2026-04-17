# Notes: /Users/home/Repositories/indemn-os/kernel/api/registration.py

**File:** /Users/home/Repositories/indemn-os/kernel/api/registration.py
**Read:** 2026-04-16 (full file — 293 lines)
**Category:** code

## Key Claims

- Module docstring: "Auto-register API routes from entity definitions. Every entity type gets CRUD + transition + @exposed methods + capability routes. This is the self-evidence property: define an entity, its API exists."
- `register_entity_routes(app, entity_name, entity_cls)` — registers all routes for an entity type.
- Routes registered per entity:
  - `GET /api/{entities}/` — list
  - `GET /api/{entities}/{entity_id}` — get
  - `POST /api/{entities}/` — create
  - `PUT /api/{entities}/{entity_id}` — update (rejects state field changes)
  - `POST /api/{entities}/{entity_id}/transition` — state transition
  - `POST /api/{entities}/{entity_id}/{method_name}` — @exposed methods
  - `POST /api/{entities}/{entity_id}/{cap_name}?auto=true` — capability methods
  - `POST /api/{entities}/{entity_id}/evaluate-rules` — generic rule evaluation
  - `POST /api/{entities}/{entity_id}/integration/{method_name}` — adapter dispatch
  - `POST /api/{entities}/bulk` — starts BulkExecuteWorkflow
- `_fire_dispatch` — fire-and-forget optimistic_dispatch after save_tracked.
- `_coerce_objectid_fields` — converts string ObjectIds from JSON to bson.ObjectId.

## Architectural Decisions

- **Self-evidence property**: define an entity, its API routes appear automatically via `register_entity_routes`.
- All routes require authentication (Depends on `get_current_actor`) and permission check (`check_permission`).
- All reads use `find_scoped`/`get_scoped` — org scoping automatically applied.
- Create/update/transition all go through `save_tracked` (the atomic transaction).
- Capability routes take `?auto=true` query param — matches `--auto` CLI pattern.
- State field changes rejected on PUT; must use /transition endpoint (state machine bypass protection per comprehensive audit).
- Bulk endpoint starts Temporal workflow with `task_queue="indemn-kernel"`.
- Integration dispatch endpoint accepts system_type + params, calls adapter method.

## Layer/Location Specified

- Kernel code: `kernel/api/registration.py`.
- Runs in kernel API server.
- Uses `find_scoped`, `get_scoped`, `save_tracked` — all through OrgScopedCollection + save_tracked in kernel.
- Bulk endpoint dispatches to kernel's Temporal "indemn-kernel" queue — consistent with current (Finding 0) architecture. After Finding 0 fix, bulk would still go to kernel queue; only agent execution would move to harness queues.

**No layer deviation for this file.** It's correctly kernel-side (auto-generated API routes for entities).

Observation: The bulk endpoint dispatches to `task_queue="indemn-kernel"` — this is the same queue where `process_with_associate` lives today. Post-Finding-0-fix, bulk workflows stay on "indemn-kernel", agent workflows move to Runtime-specific queues.

## Dependencies Declared

- `asyncio`
- `fastapi` — APIRouter, Depends, HTTPException, Query
- `bson.ObjectId`
- `kernel.api.serialize.to_dict`
- `kernel.auth.middleware.check_permission`, `get_current_actor`
- `kernel.context.current_org_id`
- `kernel.capability.registry.get_capability` (lazy import)
- `kernel.message.dispatch.optimistic_dispatch` (lazy import)
- `kernel.temporal.client.get_temporal_client` (lazy import)
- `kernel.temporal.workflows.BulkExecuteWorkflow` (lazy import)
- `kernel.integration.dispatch.get_adapter`, `execute_with_retry` (lazy import)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/api/registration.py`
- Called by: `kernel/api/app.py` during app startup (iterates ENTITY_REGISTRY, calls `register_entity_routes` per entity)

## Cross-References

- Design: 2026-04-13-white-paper.md § Entity (self-evidence property)
- Phase 1 spec §1.21 Auto-Generated API
- `kernel/api/serialize.py` — to_dict helper
- `kernel/entity/exposed.py` — @exposed decorator
- `kernel/capability/registry.py` — capability lookup
- `kernel/integration/dispatch.py` — adapter dispatch

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The auto-generation pattern is central to the "self-evidence" design — define entity → all routes exist.
- State machine bypass protection via PUT rejection is explicit per comprehensive audit.
- Optimistic dispatch is fired after save_tracked — correct per design's "optimistic dispatch + sweep backstop" pattern.
- Integration route accepts system_type from request body — minor API ergonomics concern but works.
- Per-entity bulk endpoint matches the auto-generated CLI verb pattern.

This file is correctly placed kernel-side and implements the self-evidence design.
