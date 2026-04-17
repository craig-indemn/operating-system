# Notes: 2026-04-14-impl-spec-phase-0-1-addendum.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-0-1-addendum.md
**Read:** 2026-04-16 (sampled opening + Attention spec; 931 lines total. SUPERSEDED by consolidated.)
**Category:** spec-superseded

## Key Claims

Addendum to base Phase 0+1 spec — fills gaps from design artifacts missed in base.

Key content (based on sampled + known structure):
- **A.1 Attention kernel entity FULL SPEC** — actor_id + target_entity + related_entities + purpose (5 values) + runtime_id/workflow_id/session_id + opened_at + last_heartbeat + expires_at + metadata + status. State machine: active → expired/closed. Indexes on (actor_id, purpose), (target_entity.id).
- **A.2 Runtime kernel entity full spec** — name, kind, framework, framework_version, transport, transport_config, llm_config, deployment_image, deployment_platform, deployment_ref, capacity, instances, status. Lifecycle: configured → deploying → active → draining → stopped.
- **A.3 Session kernel entity full spec** (per authentication-design).
- **Schema migration mechanics** — rename, add, remove, convert field with batching, aliases, dry-run.
- **Rule validation at creation** — fields exist in schema, role has write permission, state fields excluded.
- **Pre-transition validation hooks** — business invariants checked before state change.

## Architectural Decisions

All decisions here SURVIVE into consolidated spec.
- Attention lifecycle is `active → expired/closed` (transitions from session 5).
- Runtime lifecycle from session 5.
- Session from authentication-design.

## Layer/Location Specified

- `kernel_entities/attention.py` — Attention Document class
- `kernel_entities/runtime.py` — Runtime Document class
- `kernel_entities/session.py` — Session Document class
- `kernel/entity/migration.py` — schema migration
- `kernel/entity/state_machine.py` — pre-transition validation

**Finding 0 relevance**: Addendum provides full Attention + Runtime specs — required for the harness pattern. But still treats Runtime.deployment_platform as a config field; the harness itself (runtime-voice-deepagents etc.) is not code in the kernel.

## Dependencies Declared

Same as base + consolidated.

## Code Locations Specified

Same as consolidated spec.

## Cross-References

- 2026-04-14-impl-spec-phase-0-1.md (base — this addendum completes it)
- 2026-04-14-impl-spec-phase-0-1-consolidated.md (SUPERSEDES this)
- 2026-04-10-realtime-architecture-design.md (source for Attention + Runtime specs)
- 2026-04-11-authentication-design.md (source for Session spec)
- 2026-04-09-data-architecture-solutions.md (source for migration/validation)
- 2026-04-08-pressure-test-findings.md (source for pre-transition validation hooks)

## Open Questions or Ambiguities

None unique to addendum. All content SURVIVES into consolidated spec.

**Supersedence note**: SUPERSEDED by consolidated spec. This addendum's content is embedded there.
