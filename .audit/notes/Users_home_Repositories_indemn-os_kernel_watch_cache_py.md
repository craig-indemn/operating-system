# Notes: /Users/home/Repositories/indemn-os/kernel/watch/cache.py

**File:** /Users/home/Repositories/indemn-os/kernel/watch/cache.py
**Read:** 2026-04-16 (full file — 60 lines)
**Category:** code

## Key Claims

- In-memory watch cache keyed by `(org_id, entity_type)` → list of `{watch, role_name}`.
- 60-second TTL with immediate invalidation on Role entity save.
- Functions:
  - `load_watch_cache()` — iterate all Role entities, populate cache.
  - `get_cached_watches(org_id, entity_type)` — returns cached entries; schedules async reload if TTL expired.
  - `invalidate_watch_cache()` — triggers immediate reload (called on Role save).

## Architectural Decisions

- Per-instance in-memory cache (no shared cache).
- TTL refresh is async — returns stale cache while reload runs in background.
- Immediate invalidation on Role save (called from save_tracked hooks).
- Module-level state `_cache`, `_cache_loaded_at`.
- Cross-instance consistency handled by TTL + save-triggered invalidation. Future: Change Stream on roles collection.

## Layer/Location Specified

- Kernel code: `kernel/watch/cache.py`.
- Runs in whichever kernel process loads it (API Server for watch evaluation during save_tracked).
- Per design: watch evaluation is kernel-side; cache improves performance.

**No layer deviation.**

**Important check for simplification pass (2026-04-13-simplification-pass.md):** The simplification pass removed watch **coalescing** from the kernel — but the cache is a different mechanism (speed of watch lookup, not event grouping). The cache stays in the kernel per design.

This file does NOT contain coalescing logic — which is correct per the simplification pass. Coalescing was moved to UI-only rendering by correlation_id.

## Dependencies Declared

- `time`
- `kernel_entities.role.Role` (lazy import inside `load_watch_cache`)
- `asyncio` (for async reload scheduling)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/watch/cache.py`
- Called by: `kernel/message/emit.py` (during watch evaluation for entity saves)
- Invalidated by: Role save hook (via `invalidate_watch_cache`)
- Loaded at startup: `kernel/api/app.py` startup event

## Cross-References

- Design: 2026-04-10-realtime-architecture-design.md (watch mechanism)
- 2026-04-13-simplification-pass.md (coalescing moved out — this file does NOT have coalescing, correct)
- Phase 1 spec §1.14 Watch Cache
- `kernel/watch/evaluator.py` — condition evaluation
- `kernel/message/emit.py` — uses cached watches

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- **NO COALESCING LOGIC** in this file — correctly simplified out per 2026-04-13-simplification-pass.md.
- Per-instance cache is acceptable for MVP; cross-instance drift is bounded by 60s TTL + explicit invalidation.
- Async reload on TTL expiry returns stale data during the reload — acceptable for watch evaluation.
- Future enhancement: Change Stream on roles collection (mentioned in docstring) would give faster cross-instance invalidation.

This file correctly implements the simplified watch cache per design. No architectural concerns.
