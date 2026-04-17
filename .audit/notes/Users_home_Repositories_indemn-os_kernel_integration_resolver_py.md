# Notes: /Users/home/Repositories/indemn-os/kernel/integration/resolver.py

**File:** /Users/home/Repositories/indemn-os/kernel/integration/resolver.py
**Read:** 2026-04-16 (full file — 74 lines)
**Category:** code

## Key Claims

- Module docstring: "Credential resolution — priority chain: actor → owner → org. Resolves which Integration entity to use for a given system_type."
- `resolve_integration(system_type, actor_id, org_id, require_org_only)` — three-step resolution:
  1. Actor's own personal integration (skipped if `require_org_only=True`)
  2. Owner's personal integration (for owner-bound associates via `actor.owner_actor_id`)
  3. Org-level with role-based access (`access.roles` matches actor's role names)
- Raises `AdapterNotFoundError` with helpful message if no match.
- `org_id` and `actor_id` default to `current_org_id.get()` and `current_actor_id.get()` from contextvars.

## Architectural Decisions

- **Priority chain matches the design** (2026-04-10-integration-as-primitive.md): actor → org.
- **Step 2 (owner's personal)** supports owner-bound associates from the CRM retrace (e.g., Craig's Gmail sync associate uses Craig's Gmail integration).
- Queries MongoDB directly via Beanie (`Integration.find_one`, `Actor.get`, `Role.find`) — inside trust boundary.
- `require_org_only=True` skips personal integrations (for operations that must use org credentials like carrier payment).
- Matches the access.roles check for org-level integrations — role names in the Integration's access.roles list must intersect the actor's role names.

## Layer/Location Specified

- Kernel code: `kernel/integration/resolver.py`.
- Matches design: resolver logic lives in kernel.
- No layer deviation.

## Dependencies Declared

- `bson.ObjectId`
- `kernel.context.current_actor_id`, `current_org_id`
- `kernel.integration.adapter.AdapterNotFoundError`
- `kernel_entities.actor.Actor`
- `kernel_entities.integration.Integration`
- `kernel_entities.role.Role`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/integration/resolver.py`
- Called by: `kernel/integration/dispatch.py::get_adapter` (primary caller)

## Cross-References

- Design: 2026-04-10-integration-as-primitive.md §"Credential Resolution" (priority chain)
- Phase 3 spec §3.3 (Credential Resolution)
- 2026-04-13-documentation-sweep.md — `owner_actor_id` documentation
- `kernel_entities/integration.py` — Integration entity schema
- `kernel_entities/actor.py` — Actor's `owner_actor_id` field

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The comprehensive audit verified "Credential resolution (actor→owner→org) IMPLEMENTED".
- Owner-bound resolution (step 2) is what enables scheduled associates bound to humans (CRM use case).
- No fallback to contextvars if `actor_id` parameter is None but `current_actor_id.get()` is also None — would raise `ObjectId(None)` error. Minor robustness concern, not architectural.
- Error message gives the CLI command to create an integration — useful UX.

Resolver is well-placed and matches design expectations.
