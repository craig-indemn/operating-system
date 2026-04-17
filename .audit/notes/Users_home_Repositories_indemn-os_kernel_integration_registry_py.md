# Notes: /Users/home/Repositories/indemn-os/kernel/integration/registry.py

**File:** /Users/home/Repositories/indemn-os/kernel/integration/registry.py
**Read:** 2026-04-16 (full file — 21 lines)
**Category:** code

## Key Claims

- Module docstring: "Adapter registry — maps provider:version to adapter class."
- Module-level dict: `ADAPTER_REGISTRY: dict[str, type[Adapter]] = {}`.
- `register_adapter(provider, version, adapter_cls)` — adds to registry with key `{provider}:{version}`.
- `get_adapter_class(provider, version)` — looks up, raises `AdapterNotFoundError`.

## Architectural Decisions

- Registry is a module-level dict — simple in-process singleton.
- Keyed by `{provider}:{version}` format — enables per-org adapter version upgrades.
- Registration happens via `register_adapter` call — typically at module import time from concrete adapter modules.
- Lookup raises `AdapterNotFoundError` (a concrete exception) rather than returning None — forces callers to handle.

## Layer/Location Specified

- Kernel code in `kernel/integration/registry.py`.
- In-process registry (no external state).
- Per design (2026-04-10-integration-as-primitive.md): "Adapter registry keyed by version: `ADAPTER_REGISTRY["outlook_v2"] = OutlookV2Adapter`." Implementation matches design exactly (uses `provider:version` format).

**No layer deviation.**

## Dependencies Declared

- `kernel.integration.adapter.Adapter` (base class, for typing)
- `kernel.integration.adapter.AdapterNotFoundError` (raised on lookup miss)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/integration/registry.py`
- Registered adapters live in `kernel/integration/adapters/`

## Cross-References

- Design: 2026-04-10-integration-as-primitive.md (adapter versioning + registry)
- Phase 3 spec §3.2 (adapter registry)
- `kernel/integration/adapter.py` — base class
- `kernel/integration/adapters/*.py` — call `register_adapter(...)` at module import
- `kernel/integration/dispatch.py` — uses `get_adapter_class(...)` to dispatch calls

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The design allows for plugin-loadable adapters in the future (explicitly deferred). Current registry is static (registered at import time).
- Tier 3 custom adapter path is not implemented (deferred per design).
- No validation that `adapter_cls` actually inherits `Adapter` — type hint is advisory only.

The registry is minimal and correctly placed. No architectural concerns.
