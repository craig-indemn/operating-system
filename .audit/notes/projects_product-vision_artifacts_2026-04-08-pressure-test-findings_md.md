# Notes: 2026-04-08-pressure-test-findings.md

**File:** projects/product-vision/artifacts/2026-04-08-pressure-test-findings.md
**Read:** 2026-04-16 (full file — 268 lines)
**Category:** design-source

## Key Claims

- **Three independent reviewers (platform architect, DX engineer, distributed systems engineer) validated the 4 primitives** (Entity, Message, Actor, Role).
- **"Watches as wiring mechanism is a genuine insight."** Actor-centric > system-centric routing.
- **Actor spectrum works** — deterministic, reasoning, hybrid — same framework, same I/O.
- **Watch evaluation scales** — sub-millisecond matching even at 1M+ entity saves/hour; bottleneck is message write throughput, not watch matching. Single Atlas M30 handles 2K–5K transactions/sec.
- **Hardening requirements address failure modes** — transactions, visibility timeouts, correlation IDs, cascade depth, idempotency.
- **Kernel-vs-domain separation is correct** — same primitives work for insurance email, sales, CRM, content management.

### Must-address findings (6 found; ALL incorporated into later designs):

1. **Voice channels need direct invocation.** 2.5–5s queue latency is unacceptable for voice; direct-invoke the associate while creating Interaction + message in parallel for audit. Latency breakdown: 1.1–7.3s message path → 0.9–2.3s direct invocation.
2. **Audit trail missing** (regulatory requirement). Added `changes` collection: entity_id, entity_type, field_name, old_value, new_value, actor_id, reason, timestamp. Same transaction as entity save.
3. **Watch conditions must be entity-local only.** Cross-entity lookups blow up save-txn latency. Either denormalize (computed fields) or filter after claim.
4. **Split message storage from day 1**: `message_queue` (active, stays tiny) + `message_log` (completed, grows). Move on completion (txn).
5. **OTEL observability baked in** — every entity save, message, watch eval, actor invocation, CLI command is an OTEL span. correlation_id IS trace_id (or linked).
6. **Pre-transition business validation** — state machines validate transition graph; Pydantic validates types; business invariants (missing required fields) need pre-transition hooks on entities.

### Define-during-implementation findings (4):

7. **Deterministic skill format** — three options (YAML / Python functions / formalized markdown with CHECK/RUN blocks). Later resolved as **markdown with backtick-delimited commands and "If"/"When" conditions** (Phase 2-3 spec `_parse_skill_steps`).
8. **Testing + debugging CLI** — `indemn trace entity`, `indemn trace cascade`, `indemn queue show`, `indemn simulate`, `indemn associate test --dry-run`, etc. Day-one requirement.
9. **Declarative system definition (YAML + CLI)** — `indemn system apply/diff/export` against system YAML manifests. Later realized as **org clone/diff/deploy** (2026-04-09-data-architecture-everything-is-data.md).
10. **Bulk operations** — day-1 requirement. Initial proposal: batch insert + `batch_id` on messages + coalescing window. Later refined into the **bulk-operations-pattern** (2026-04-10) with `bulk_execute` workflow.

### Bank-for-later findings (4):

11. **Assignment lifecycle** — richer states (pending/active/reassigned/completed/escalated), approval, round-robin, escalation chains. MVP = simple assignment. Race-condition fix (verify assignment at claim time) recommended NOW.
12. **Partial multi-entity failures ("phantom messages")** — if an actor changes A+B but crashes before C, messages from A+B are in the system and downstream processes them. MVP: order failure-prone ops first. Future: saga compensation or batch-save.
13. **Provider versioning for adapters** — Outlook Graph had 3 breaking changes in 18 months. Adapter registry needs `provider:version` key. Integration stores version used.
14. **Governor limits on watches** — misconfigured watches → message avalanches. Estimate volume, require explicit confirmation above threshold.

### Scale thresholds:
- Entity saves/hour: <100K comfortable, 100K–1M watch, >1M needs action.
- Messages/hour: <500K comfortable, 500K–2M watch, >2M needs action.
- Atlas tier: M30 → M60 → M80+ or sharding.

## Architectural Decisions

- **Four primitives are locked** (Entity, Message, Actor, Role). Concept count is right (6 to start + 4 more for depth).
- **Direct invocation is a first-class trigger type** (not just a backdoor for real-time — the documented pattern).
- **Message storage is two collections from day 1** — split is architectural, not a later optimization.
- **OTEL is not a feature — it IS the observability layer.** Every span, every primitive touch.
- **Skills CAN be deterministic/reasoning/hybrid** but the FORMAT is open at this point.
- **Testing + debugging CLI is a day-one deliverable** — not an after-thought.
- **Provider versioning of adapters is REQUIRED for MVP** — external APIs break.

## Layer/Location Specified

- **Message split** = kernel-level (two MongoDB collections: message_queue + message_log). NOT in the entity framework layer. Kernel invariant.
- **Changes collection** = kernel-level MongoDB. Same txn as entity save. Kernel invariant.
- **OTEL instrumentation** = kernel-wide: entity, watch, Temporal, LLM, CLI — all emit spans.
- **Direct invocation** = API endpoint in kernel (`POST /api/associates/{id}/invoke` per later Phase 2-3 spec).
- **Adapter registry versioned** = `provider:version` keying; adapter code in kernel.
- **Deterministic skill interpreter** — left open. This artifact doesn't place it. Later artifacts (realtime-architecture-design) place it in the harness.
- **LLM call location** — left open. Later placed in the harness.
- **Testing CLI** — `indemn trace`, `indemn simulate`, `indemn associate test` — all CLI commands. CLI subprocess into kernel.

**Finding 0 relevance**: The reviewers did NOT find Finding 0 — they validated the primitives as sound but didn't push on "where agent execution runs." The harness pattern hadn't been formalized yet (April 10). The reviewers saw "Temporal workers" but deferred deployment topology.

## Dependencies Declared

- MongoDB (two-collection split)
- Temporal (`max_concurrent_activities`, retry)
- OpenTelemetry (+ Jaeger / Tempo / Datadog exporters)
- Atlas (M30+)
- `indemn` CLI (debugging + testing commands)

## Code Locations Specified

- Conceptual:
  - `message_queue` vs. `message_log` collections
  - `changes` collection
  - `indemn trace`, `indemn simulate`, `indemn queue show`, `indemn associate test --dry-run`
  - Direct-invocation endpoint
  - OTEL spans at every primitive
- Implementation mapping:
  - Pass 2 confirmed message split exists in `kernel/message/*`.
  - `changes` exists in `kernel/changes/collection.py`.
  - OTEL: some instrumentation exists (Phase 2-3 spec mentions TracingInterceptor).
  - Direct-invocation: `kernel/api/direct_invoke.py` per Phase 2-3 spec.

## Cross-References

- 2026-04-08-actor-spectrum-and-primitives.md (origin)
- 2026-04-08-primitives-resolved.md (resolution of primitives)
- 2026-04-08-kernel-vs-domain.md (same day, adds Organization + Assignment)
- 2026-04-08-entry-points-and-triggers.md (Tier A — to be read)
- 2026-04-10-bulk-operations-pattern.md (resolved Finding 10)
- 2026-04-10-realtime-architecture-design.md (resolved Finding 1 — direct invocation via harness)
- 2026-04-11-authentication-design.md (advanced assignment thinking)
- 2026-04-13-simplification-pass.md (DROPPED message coalescing from Finding 10)

## Open Questions or Ambiguities

**Resolved in later artifacts** — already addressed per this note. Nothing architecturally open.

**Finding 11 (Assignment lifecycle)** still somewhat open at MVP scope: "simple assignment" is sufficient; richer lifecycle = later. Need to verify in Pass 4 whether assignment-at-claim-time race-condition check was implemented.

**Supersedence note**:
- Finding 10 bulk ops initial proposal (batch_id + coalescing window) is SUPERSEDED by 2026-04-10-bulk-operations-pattern.md (bulk as a kernel pattern/workflow) + 2026-04-13-simplification-pass.md (coalescing removed entirely from kernel, UI-only).
- All other findings survive.
