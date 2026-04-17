# Notes: 2026-04-10-post-trace-synthesis.md

**File:** projects/product-vision/artifacts/2026-04-10-post-trace-synthesis.md
**Read:** 2026-04-16 (full file — 198 lines)
**Category:** design-source

## Key Claims

- Synthesis after GIC and EventGuard retraces (B2B email pipeline + consumer real-time).
- **Six primitives handle both workloads** — no new primitive surfaced, no primitive felt forced or superfluous. Primitives are stable.
- Kernel is not secretly shaped for one workload type.
- Integration as primitive #6 earned its elevation (validated by both retraces).
- Watches handle all orchestration — no explicit workflow orchestration code.
- `--auto` pattern scales to both deterministic-heavy (GIC) and reasoning-heavy (EventGuard) workloads.
- Unified queue works for mixed human/associate AND fully autonomous operation.
- Selective emission prevents watch storms.
- Multi-entity atomicity holds via single-transaction actor turns.
- One actor can serve a high-volume deployment (EventGuard's Quote Assistant serves all 351 venues).
- Ten items surfaced for follow-up:
  1. Watch coalescing (→ later simplified to UI-only)
  2. Ephemeral entity locks (→ later unified into Attention)
  3. Actor-context watches + signal delivery (the biggest gap) → resolved in realtime-architecture-design
  4. Inbound webhook dispatch (documentation update to Integration)
  5. Internal vs external entities (documentation)
  6. Computed field mapping scope (documentation)
  7. Bulk operations pattern → resolved in bulk-operations-pattern
  8. Pipeline dashboard layer → resolved in base-ui-operational-surface (as part of the base UI)
  9. Queue health tooling → resolved in base-ui-operational-surface (as part of the base UI)
  10. Authentication → resolved in 2026-04-11-authentication-design.md

## Architectural Decisions

- No new primitive or new kernel entity required by the two retraces.
- The three identified "architectural gaps" (coalescing, ephemeral locks, actor-context watch scoping) are ALL additive — none require changing existing watch behavior.
- All three slot into the existing primitive model without introducing new primitives.
- Categorization:
  - Must-design before spec (architectural): items 1, 2, 3, 7
  - Design before spec (supporting infrastructure): items 4, 8, 9
  - Separate session (own scope): item 10 (auth)
  - Just documentation: items 5, 6

## Layer/Location Specified

This is a synthesis document; it doesn't itself introduce layer/location claims. It points to where the follow-up design work should happen.

Layer-relevant framings in this artifact:
- **Bulk operations pattern** described as: transaction batching strategy, event emission for bulk ops, integration with watch coalescing (later removed), progress reporting, idempotency, rollback, CLI ergonomics. All kernel-side concerns. Later formalized in bulk-operations-pattern as `bulk_execute` Temporal workflow in kernel code.
- **Actor-context watches + signal delivery** described as: "the kernel checks if the entity is in the context of a currently-running actor and routes the event as a Temporal signal to that actor's workflow instead of writing to the queue. The running workflow handles the signal by sending a proactive message on the open channel." This was REFINED in the realtime-architecture-design to use `indemn events stream` Change Streams (not Temporal signals) and Attention for context tracking.
- **Inbound webhook dispatch** described as: "Kernel webhook endpoint at `/webhook/{provider}/{integration_id}`" — kernel-side endpoint that dispatches to Integration adapter methods.
- **Pipeline dashboard layer** described as: "auto-generated reporting layer in the base UI. Sources: entity state machine distributions, message log throughput, Temporal execution stats, Integration health." Kernel provides the data sources; UI does the rendering. Later formalized in base-ui-operational-surface.

## Dependencies Declared

- None new. References existing dependencies (MongoDB, Temporal, OTEL, etc.).

## Code Locations Specified

- Kernel webhook endpoint: `/webhook/{provider}/{integration_id}` — kernel-side
- Integration adapter inbound methods: (validate_webhook, parse_webhook) — kernel code alongside outbound adapter methods
- Pipeline dashboard: base UI (auto-generated, NOT per-org custom)
- Queue health CLI commands: kernel CLI surface
- Base UI rendering contract: to be designed — maps entity definitions to default dashboards

## Cross-References

- 2026-04-10-gic-retrace-full-kernel.md
- 2026-04-10-eventguard-retrace.md
- 2026-04-10-crm-retrace.md (recommended third trace — later executed)
- 2026-04-10-integration-as-primitive.md
- 2026-04-10-base-ui-and-auth-design.md
- All the items listed point forward to later design artifacts

## Open Questions or Ambiguities

This artifact catalogs ten open items. Most are resolved by subsequent artifacts:
- Items 1, 2, 3 → 2026-04-10-realtime-architecture-design.md
- Item 4 → referenced as open in realtime-architecture-design Part 10 "deferred items", never fully formalized as a separate artifact; the pattern is stated: adapter inbound methods + kernel webhook endpoint
- Items 5, 6 → documentation clarification (absorbed into white paper / consolidated specs)
- Item 7 → 2026-04-10-bulk-operations-pattern.md
- Items 8, 9 → 2026-04-11-base-ui-operational-surface.md
- Item 10 → 2026-04-11-authentication-design.md
- Item 1 was later simplified out of kernel entirely per 2026-04-13-simplification-pass.md
- Item 2 was later unified with Attention per 2026-04-10-realtime-architecture-design.md

**Pass 2 observations:**
- This artifact is a ROUTING document — it points to where architectural decisions should be made. It surfaces issues without resolving them.
- The follow-up artifacts (realtime-architecture, bulk-operations, base-ui-operational-surface, authentication, simplification) ARE the authoritative sources for Pass 2.
- **Inbound webhook dispatch** is the one item that was NOT given its own design artifact. It remained at the level of "update the Integration artifact" which appears to not have happened as a standalone update. The Integration primitive artifact (2026-04-10-integration-as-primitive.md) mentions inbound webhooks briefly ("Integrations support both outbound and inbound connectivity"), and the realtime-architecture-design Part 10 lists "Inbound webhook dispatch documentation" as open. This may be a missing-formalization issue — implementation details for webhooks need verification against existing kernel adapter dispatch patterns.
- **No Finding 0-class deviations expected from this artifact.** It's a checkpoint/routing document, not an architectural-layer statement.
