# Notes: 2026-04-13-simplification-pass.md

**File:** projects/product-vision/artifacts/2026-04-13-simplification-pass.md
**Read:** 2026-04-16 (full file — 197 lines)
**Category:** design-source

## Key Claims

- Review of the complete architecture after sessions 5-6 — asking "does this earn its complexity?" for every concept.
- Kernel = six primitives: Entity, Message, Actor, Role, Organization, Integration.
- Seven kernel entities (renamed from "bootstrap entities"): Organization, Actor, Role, Integration, Attention, Runtime, Session.
- **Two simplifications accepted:**
  1. **Watch coalescing removed from kernel → UI rendering concern.** Kernel still emits per-entity events; UI groups for display by correlation_id.
  2. **Rule evaluation traces → metadata in the changes collection.** No separate evaluation trace collection.
- **One simplification rejected**: keeping Runtime as a kernel entity ("the most important part, the center of everything" per Craig).
- **Two features deferred from MVP:**
  1. WebAuthn / passkeys (TOTP sufficient)
  2. Per-operation MFA re-verification (`requires_fresh_mfa` — session-level is sufficient)
- **Kept in MVP** (pushed back on proposed deferrals):
  - Schema migration (full: rename, type-change, batching, aliases, rollback)
  - All 5 Attention purposes (real_time_session, observing, review, editing, claim_in_progress)
  - Content visibility scoping (full_shared / metadata_shared / owner_only on Integration)
  - Rule groups with lifecycle (draft → active → archived)
- Already correctly deferred (no change): Platform admin work-type tagging + configurable notifications, Throughput + dwell-time aggregations, Assistant inline entity rendering, Tier 3 self-service (billing, plans, sub-users).
- "The architecture is proportional." Every concept serves one of the six primitives. No concept exists for theoretical reasons.
- Layered spec presentation proposed: Layer 0 (6 concepts) → Layer 1 (kernel: watches, rules, skills, queue, Temporal) → Layer 2 (operational surface: Attention, Runtime, Session, auth, base UI) → Layer 3 (patterns: bulk, harness, scoped watches, content visibility, schema migration) → Layer 4 (infrastructure: OTEL, OrgScopedCollection, changes collection, queue/log split, Secrets Manager).

## Architectural Decisions

- **Watch coalescing is a UI concern, NOT a kernel mechanism.** Kernel removes:
  - `coalesce` field on watch definitions
  - `batch_id` field on message schema
  - Time-window grouping logic in emission path
- **Kernel preserves:**
  - One save = one event
  - Per-entity messages in the queue (associates still process individually)
  - Scoped watches (still write `target_actor_id`)
  - Correlation_id-based grouping is possible client-side
- **Rule evaluation detail stored in change record metadata**: rules_checked, matched, vetoed, needs_reasoning as fields on the change record. Debuggability preserved.
- **Runtime stays** — kernel dispatches work to Runtimes, monitors health, routes real-time events through them. Dependency is real.
- "Bootstrap entity" renamed to "kernel entity" (self-evident terminology).
- Schema migration is first-class MVP. "We're building a real system. Entities will evolve through real usage within weeks."
- Content visibility scoping is MVP. "We are starting with CRM use case." Personal integrations need privacy from day one.
- Rule groups with lifecycle are MVP. "Without groups, 50 rules become unmanageable."

## Layer/Location Specified

- **Coalescing**: explicitly moved OUT of the kernel. Now UI-only.
- **Rule evaluation trace**: explicitly removed as a separate concept — now metadata on the existing changes collection.
- **No other architectural-layer movements.** Runtime, Attention, Session, harness pattern, integration adapters, auth middleware — all stay where prior design artifacts placed them.
- Layered spec presentation:
  - Layer 0 (6 primitives)
  - Layer 1 (kernel — watches, rules+lookups, skills, queue, Temporal)
  - Layer 2 (operational surface — Attention, Runtime, Session, auth, Base UI)
  - Layer 3 (patterns — bulk ops, **harness pattern** (thin CLI-based per-framework), scoped watches, content visibility, schema migration)
  - Layer 4 (infrastructure — OTEL, OrgScopedCollection, changes, queue/log, Secrets Manager)
- **Note Layer 3 explicitly includes "Harness pattern (thin CLI-based per-framework)"** — confirming harnesses are architectural and at the patterns level, NOT subsumed into Layer 1 kernel.

## Dependencies Declared

- None new. This artifact is a review; it doesn't add dependencies.

## Code Locations Specified

- Kernel code (the platform) — no change. 
- Watch coalescing code: explicitly says kernel emission path SHOULD NOT have grouping logic. This should be verifiable in implementation.
- Rule evaluation: should be recorded on change records, not separate collection. This should be verifiable in implementation.

## Cross-References

- All prior session 5-6 artifacts (referenced as "the complete architecture being reviewed")
- 2026-04-10-realtime-architecture-design.md (scoped watches, coalescing mechanism removed here, harness pattern retained)
- 2026-04-11-authentication-design.md (WebAuthn and requires_fresh_mfa deferred here)
- 2026-04-11-base-ui-operational-surface.md (UI coalescing = where coalescing now lives)
- 2026-04-10-integration-as-primitive.md (content visibility scoping on Integration kept)

## Open Questions or Ambiguities

- **What "UI-only coalescing" looks like concretely** is not fully specified. "UI groups them for display by correlation_id. One rendered row: '47 submissions became stale' with drill-down." The implementation detail is deferred.
- **Change record metadata for rule evaluation** — schema not fully specified. Example JSON provided; exact field names not locked.

**Pass 2 observations:**
- **Watch coalescing MUST NOT be in the kernel implementation.** Per the simplification, the kernel emission path should NOT have a `coalesce` field, a `batch_id`, or time-window grouping logic. If current code has any of these, it's a post-simplification regression. Per comprehensive audit's section 3a: "Watch coalescing — simplified out per `2026-04-13-simplification-pass.md`. Verify the simplification was actually applied (UI-only coalescing, no kernel mechanism)." This is a Pass 2 check point.
- **Rule evaluation context** should be in changes collection records, not a separate trace collection. Verifiable in implementation.
- **Harness pattern is confirmed as Layer 3 architectural concept** — this simplification pass did NOT deprecate it. The harness pattern survived the review.
- **No changes to Integration adapter location, skill execution location, auth middleware location, or base UI auto-generation.** Post-simplification design matches the individual artifacts (realtime-architecture, integration-as-primitive, auth design, base UI operational surface).

This artifact confirms that Finding 0's concern (harness pattern required) is NOT something simplified away. The harness pattern is explicitly preserved in Layer 3 of the simplified architecture.
