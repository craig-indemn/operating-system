# Notes: /Users/home/Repositories/indemn-os/kernel/integration/dispatch.py

**File:** /Users/home/Repositories/indemn-os/kernel/integration/dispatch.py
**Read:** 2026-04-16 (full file — 84 lines)
**Category:** code

## Key Claims

- Module docstring: "Adapter dispatch — resolve, instantiate, auto-refresh. get_adapter() is the primary entry point for all adapter usage. Handles credential resolution, caching, and OAuth token refresh. execute_with_retry() wraps adapter methods with auth error retry."
- `get_adapter(system_type, actor_id, org_id, require_org_only)` — resolves integration, fetches credentials, instantiates adapter, handles proactive token refresh.
- `execute_with_retry(adapter, method_name, *args, **kwargs)` — wraps method calls with retry on AdapterAuthError (refresh + retry), AdapterRateLimitError (wait retry_after + retry), AdapterTimeoutError (immediate retry).

## Architectural Decisions

- Integration resolution → credential fetch → adapter instantiation → optional token refresh = single `get_adapter` call.
- Adapter's `_secret_ref` attribute stored on instance for retry logic reference.
- Token refresh is transparent: `adapter.needs_token_refresh()` check triggers refresh before returning adapter.
- `execute_with_retry` handles three error classes: auth (refresh + retry), rate-limit (backoff + retry), timeout (immediate retry).
- No retry on `AdapterValidationError` or `AdapterNotFoundError` (permanent errors).

## Layer/Location Specified

- Kernel code: `kernel/integration/dispatch.py`.
- Correct layer per design (Integration primitive + adapters as kernel code).
- Entry point for all adapter usage — ensures consistent auth handling across callers.

**No architectural-layer deviation.**

## Dependencies Declared

- `kernel.integration.adapter.Adapter`, `AdapterAuthError`, `AdapterRateLimitError`, `AdapterTimeoutError`
- `kernel.integration.credentials.fetch_credentials`, `store_credentials`
- `kernel.integration.registry.get_adapter_class`
- `kernel.integration.resolver.resolve_integration`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/integration/dispatch.py`
- Called by: any kernel code needing an adapter (webhook endpoint, entity method invocations, etc.)

## Cross-References

- Design: 2026-04-10-integration-as-primitive.md (credential resolution, rotation)
- Phase 3 spec §3.5 (Adapter Dispatch with Auto-Refresh)
- `kernel/integration/adapter.py` — base class + error hierarchy
- `kernel/integration/registry.py` — adapter class lookup
- `kernel/integration/resolver.py` — integration resolution
- `kernel/integration/credentials.py` — credential fetch/store

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Setting `adapter._secret_ref` as an instance attribute is slightly hacky — could be a constructor param.
- `execute_with_retry` is a function, not a decorator. Callers wrap method invocations explicitly.
- Only retries once — no exponential backoff or multiple attempts. Consistent with "fail fast" semantics for integrations.
- Token refresh on `get_adapter` is "check proactively" (via `needs_token_refresh()`); `execute_with_retry` also handles reactive refresh on AdapterAuthError. Both paths exist.

Dispatch is correctly placed in the kernel and follows the design pattern.
