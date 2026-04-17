# Notes: /Users/home/Repositories/indemn-os/kernel/integration/adapter.py

**File:** /Users/home/Repositories/indemn-os/kernel/integration/adapter.py
**Read:** 2026-04-16 (full file — 90 lines)
**Category:** code

## Key Claims

- Defines `AdapterError` hierarchy: `AdapterError`, `AdapterAuthError`, `AdapterRateLimitError`, `AdapterTimeoutError`, `AdapterNotFoundError`, `AdapterValidationError`.
- Defines `Adapter` base ABC class.
- Adapter takes `config: dict` and `credentials: dict` in constructor.
- Methods defined on the base class (raising NotImplementedError by default):
  - Outbound: `fetch`, `send`, `charge`
  - Inbound: `validate_webhook`, `parse_webhook`
  - Auth: `auth_initiate`, `auth_callback`, `refresh_token`
  - Helper: `needs_token_refresh` (returns False by default)

## Architectural Decisions

- Adapters live in the kernel (`kernel/integration/adapter.py`).
- Inherit from `ABC`.
- Methods are optional — subclasses override what they support.
- Error hierarchy enables retry classification (auth → refresh; rate → backoff; timeout → retry; not_found/validation → permanent).
- `parse_webhook` docstring says returns `{entity_type, lookup_by, lookup_value, operation, params}` — a standardized inbound webhook parse format.

## Layer/Location Specified

- Adapters are kernel code, per design (2026-04-10-integration-as-primitive.md line 71: "Python in the OS codebase (platform code)").
- `kernel/integration/adapter.py` — the correct location.
- Matches Phase 3 spec §3.1.

**Design says** (from 2026-04-10-integration-as-primitive.md):
- "Adapter (implementation) — The kernel code that executes provider-specific operations"
- "Python in the OS codebase (platform code)"

**Implementation matches design.** No architectural-layer deviation.

**Only open question per design**: Tier 3 contribution path for custom adapters — "Whether there's a managed-extension mechanism (custom adapter loaded at runtime) is an open design question. Deferred until we have a real Tier 3 use case."

## Dependencies Declared

- `abc.ABC`
- `decimal.Decimal`
- `typing.Optional`

(Light dependencies — this is just the base class.)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/integration/adapter.py`
- Provider implementations live in `kernel/integration/adapters/` (subdirectory)

## Cross-References

- Design: 2026-04-10-integration-as-primitive.md (THE source design for this file)
- Phase 3 spec §3.1 (adapter base class)
- `kernel/integration/registry.py` — registers adapter classes
- `kernel/integration/adapters/outlook.py`, `stripe_adapter.py` — concrete implementations
- `kernel/integration/dispatch.py` — dispatches to adapter methods
- `kernel/integration/resolver.py` — resolves which Integration to use

## Open Questions or Ambiguities

**No Pass 2 layer deviation for this file.** The adapter base class is correctly placed in the kernel per the design.

**Secondary observations:**
- The class is `ABC` but uses `raise NotImplementedError` rather than `@abstractmethod`. This is intentional — methods are optional, not required.
- Error hierarchy is well-designed for retry classification.
- Constructor signature (`config`, `credentials`) makes adapters stateless between invocations — consistent with how `kernel/integration/dispatch.py` instantiates them per-call.

**Note on the design's open question** (from 2026-04-10-integration-as-primitive.md): Tier 3 developers who need a new provider adapter have "the obvious answer" of contributing a kernel PR. Whether there's a managed-extension mechanism (loading external adapters at runtime without kernel deploy) is explicitly deferred. Current implementation only supports kernel-bundled adapters. This is correct per design.
