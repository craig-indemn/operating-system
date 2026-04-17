# Notes: 2026-04-02-design-layer-4-integrations.md

**File:** projects/product-vision/artifacts/2026-04-02-design-layer-4-integrations.md
**Read:** 2026-04-16 (full file — 386 lines)
**Category:** design-source (Layer 4 early — integration architecture)

## Key Claims

- **Core principle**: Entity operations own external connectivity. No separate "integration layer" organized by external system type.
- Integration entity + adapter pattern = bridge between "what entity needs to do" and "how external system works."
- Entity defines @exposed operations (e.g., `submit_to_carrier`, `sync_to_ams`, `refresh_appetite`, `deliver`, `enrich`, `fetch_new`, `charge`).
- CLI exposes these naturally: `indemn submission submit-to-carrier SUB-001`, etc.
- Integration entity has: name, system_type, provider, config, status, state machine, optional web_operator_id.
- Adapter pattern: abstract interface per system type (CarrierAdapter, EmailAdapter, etc.). Providers implement.
- Adapter registry maps provider names → adapter classes.
- Hybrid integrations (API + web operator) handled internally by adapter.
- Web operators = deep agent associates with browser sandbox — same harness as all associates.
- Channel adapters (email, voice, SMS, web chat) follow same pattern but flow differs (inbound vs outbound).

## Architectural Decisions

- **Integration as entity** (status state machine, CLI-configurable). Later elevated to primitive in 2026-04-10-integration-as-primitive.md.
- **Adapter pattern** = abstract per system type, implemented per provider. Unchanged in final architecture.
- **ADAPTER_REGISTRY** — provider name → adapter class. Later keyed by `provider:version` (2026-04-10).
- **Web operators reuse associate harness** — browser automation added to sandbox. Same deep-agent architecture.
- **Wrap existing implementations as adapters** — no rebuild, standard interface on current code.
- **Mapping functions per provider** — code translation between external format and OS entity fields. Written once per provider.
- **Entity ops don't know the method** — API vs web operator vs email vs file, adapter handles it.

## Layer/Location Specified

- Adapter classes live in code (kernel) — "Python code, written once per provider."
- Integration entity in DB.
- Adapter registry in code.
- Web operator skills as markdown (per carrier portal).

"What's Configurable vs. What's Code" table (line 362-372):
- Which integrations a customer has → CLI config (customer/FDE/associate)
- Credentials + settings → CLI config (encrypted)
- Adapter implementations → Python code (Indemn engineering)
- Mapping functions → Python code
- Web operator skills → SKILL.md files
- New provider support → Adapter code + registration

**Correctly placed**: adapters as kernel code. Matches later 2026-04-10-integration-as-primitive.md and current implementation.

## Dependencies Declared

- Beanie/MongoDB, Pydantic
- Existing Indemn: middleware-socket-service (web chat), voice-service/voice-livekit (voice), GIC email intelligence, Stripe (EventGuard).
- Web operator libraries (Playwright or similar).

## Code Locations Specified

- Adapters in kernel code. Later: `kernel/integration/adapters/{provider}.py`.
- Adapter registry: later `kernel/integration/registry.py`.
- `get_adapter()` resolution function: later `kernel/integration/dispatch.py` + `kernel/integration/resolver.py`.
- Entity @exposed methods stay on entities.

## Cross-References

- 2026-04-10-integration-as-primitive.md (elevates Integration to primitive #6; this artifact's patterns RETAINED).
- 2026-03-30-design-layer-3-associate-system.md (web operators share associate harness).
- Later: Phase 3 consolidated spec implements this exactly.

## Open Questions or Ambiguities

- Credential storage — at this stage "config" dict; later explicitly moved to AWS Secrets Manager via `secret_ref`.
- Credential resolution priority — later explicitly defined (actor → owner → org).
- Webhook inbound dispatch — not detailed here; later formalized in Phase 3 spec.

**No Finding 0-class deviation.** This artifact's adapter pattern is the foundation of what's implemented. The evolution (Integration → primitive #6 with ownership model, `secret_ref`, provider_version) is consistent refinement, not contradiction. Implementation matches.

**Web operator treatment**: "deep agent associates with browser sandbox — same harness as all associates" — this reinforces that when harnesses are eventually built (Finding 0 fix), web operators share the same harness pattern. Current code has no web operators, no harnesses — consistent with Finding 0.
