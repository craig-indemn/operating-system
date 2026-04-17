# Notes: 2026-04-09-architecture-ironing-round-2.md

**File:** projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-2.md
**Read:** 2026-04-16 (full file — 165 lines)
**Category:** design-source

## Key Claims

5 resolutions:
- **#1 Kernel capabilities + entity methods = ONE thing.** "Kernel capabilities ARE entity methods." Activating a capability adds a method to the entity class. Same interface as custom `@exposed` methods from CLI/API/skill/associate perspective.
- **#2 Watch + rule conditions = ONE language.** One evaluator, JSON syntax, shared operators (`equals`, `contains`, `matches`, `gt`, `lt`, `in`, `all`, `any`, `not`). Watches and rules are separate concepts (watches belong to roles for routing; rules belong to entity methods for behavior), but share the evaluator.
- **#3 Messages carry REFERENCES, not copies.** Entities are source of truth. Messages: `entity_type`, `entity_id`, `event_type`, `target_role`, `correlation_id`, `created_at`, `summary`. Actors load fresh entity data when processing. One MongoDB read per message. Same reference in Temporal workflow input.
- **#4 Entity skills vs. associate skills — NOT a problem.** Both are markdown files loaded into agent context. Different creation (auto-generated vs. hand-authored) and purpose (what commands exist vs. how to process). Same format, same loading mechanism.
- **#5 Audit + message log + OTEL traces — three systems, three purposes, one trace_id.**
  - Changes collection: field-level mutations, compliance (years retention), indexed by entity_id.
  - Message log: completed work items, operations (months-years), indexed by role/date/entity_type.
  - OTEL traces: full execution path, developer debugging (days-weeks), indexed by trace_id.
  - **OTEL is the connective tissue.** `correlation_id = trace_id`. `indemn trace entity EMAIL-001` queries all three and presents unified timeline.

## Architectural Decisions

- **Unified capability/method concept**: user-facing abstraction is "entity methods"; kernel provides a library of reusable methods that can be activated on any entity type.
- **Shared condition evaluator** across watches + rules. Single implementation, single trace format.
- **Entity is source of truth, messages are references** (not snapshots). Small perf cost (load entity per message), big consistency benefit (no stale copies).
- **Three data stores each optimized for their query pattern** — no redundancy despite capturing similar events.

## Layer/Location Specified

- **Kernel capability library** = kernel code, Python modules providing reusable methods.
- **Condition evaluator** = kernel (`kernel/watch/evaluator.py`, shared with rule engine).
- **Message schema** = minimal references in `kernel/message/schema.py`.
- **Changes collection** = MongoDB, append-only, hash chain.
- **Message log** = MongoDB collection, separate from message_queue.
- **OTEL spans** = emitted from kernel at entity save, watch eval, rule eval, message creation, Temporal workflow, LLM calls.

**Finding 0 relevance**: Not directly. This round of ironing is about unifying concepts (capability/method, conditions, references vs copies, audit/log/trace). Worker location still unaddressed.

## Dependencies Declared

- Capability library (kernel)
- Condition evaluator (kernel)
- OTEL SDK + exporter (Grafana Tempo, Jaeger, etc.)
- MongoDB (changes collection, message_log)
- correlation_id = OTEL trace_id format

## Code Locations Specified

- `kernel/capability/registry.py`
- `kernel/watch/evaluator.py` (shared with rule engine)
- `kernel/rule/engine.py` (uses evaluator)
- `kernel/message/schema.py` (minimal reference schema)
- `kernel/changes/collection.py` + `hash_chain.py`
- `kernel/observability/tracing.py` (OTEL)

## Cross-References

- 2026-04-09-architecture-ironing.md (round 1)
- 2026-04-09-architecture-ironing-round-3.md (round 3 — event granularity + @exposed emission boundary)
- 2026-04-09-entity-capabilities-and-skill-model.md (capability model details)
- Phase 0-1 consolidated spec (implements these unifications)

## Open Questions or Ambiguities

- **Capability activation lifecycle** (enable/disable, multiple versions) — deferred.
- **Context depth for message references** — resolved in round 1 (configurable per watch, default shallow).

**Supersedence note**: All 5 resolutions SURVIVE into final architecture.
