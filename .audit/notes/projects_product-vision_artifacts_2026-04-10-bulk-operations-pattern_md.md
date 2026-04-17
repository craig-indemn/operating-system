# Notes: 2026-04-10-bulk-operations-pattern.md

**File:** projects/product-vision/artifacts/2026-04-10-bulk-operations-pattern.md
**Read:** 2026-04-16 (full file — 296 lines)
**Category:** design-source

## Key Claims

- Bulk operations are a **kernel-provided pattern**, not a primitive. Composed from existing primitives (Message, Temporal workflow, MongoDB transactions, watch coalescing, selective emission, OTEL, changes collection).
- **No 7th structural primitive. No new bootstrap entity.** Six-primitive count stays stable.
- **Generic `bulk_execute` Temporal workflow** in kernel code handles ALL bulk operations.
- Parameters: entity_type, operation (create/update/transition/method/delete), source (CSV/query/list/stdin), batch_size, idempotency_key, failure_mode (skip/abort).
- Three entry points, one mechanism: auto-generated CLI per entity, scheduled associate skill invocation, direct invocation.
- **`bulk_operation_id = temporal_workflow_id`** — coupling accepted for simplicity.
- Per-entity events preserved: "one save = one event" — 351 writes produce 351 events, each with `context.bulk_operation_id`.
- CLI verb taxonomy (5 verbs) enforces selective emission:
  - `bulk-create` (creation events)
  - `bulk-transition` (state change events)
  - `bulk-method` (method invocation events, for cascading business ops)
  - `bulk-update` (silent raw field updates — migrations/backfills)
  - `bulk-delete` (deletion events, gated with dry-run)
- Per-batch MongoDB transaction. MongoDB limits: ~1000 ops/txn, ~60s timeout, 16MB documents. Batch size tuned to stay under.
- **No cross-batch rollback for MVP.** Dry-run is the safety net. Saga compensation deferred.
- Default failure mode = skip-and-continue with error list. `--failure-mode=abort` is opt-in.
- Workflow terminal states: `completed`, `completed_with_errors`, `failed`.
- Multi-entity-per-row uses skill code (Option α); `bulk_apply` DSL deferred.
- The bulk operation spec itself does NOT persist as an entity. Execution state lives in Temporal (weeks retention), effects live permanently in changes collection (queryable by `bulk_operation_id`). Scheduled ops have spec in skill.
- `indemn bulk status / list / cancel / retry` queries Temporal directly.

## Architectural Decisions

- **No new primitive, no new entity.** The pattern is composed from existing kernel machinery.
- **Generic workflow in kernel code**: one `bulk_execute` Temporal workflow that parameterizes across all bulk operations.
- **Idempotency at entity level**: state machines, `external_ref`, method author responsibility. Not enforced by kernel for bulk-method in MVP.
- **Rule of thumb**: if a change should cascade, make it a method (@exposed) and use `bulk-method`. `bulk-update` is explicitly silent.
- **Error classification**: StateMachineError / ValidationError / PermissionDenied / EntityNotFound = permanent (skip); VersionConflict = transient (retry once, then permanent); Network / MongoDB / lock timeout = transient (propagate, Temporal retries whole activity).
- **Default = skip**; `abort` is explicit opt-in for operations where partial completion is worse than total failure.
- **Scope resolution happens per-event at emit time.** Coalescing applied per-target-actor, so each stakeholder sees their own coalesced batch.
- **Unified mechanism for scheduled + ad-hoc**: kernel makes no distinction. Scheduled associates invoke bulk CLI; ad-hoc invocation invokes bulk CLI. Both flow through the same `bulk_execute` workflow.
- **CLI auto-generates** the bulk-* verbs per entity (no manual registration).

## Layer/Location Specified

- **`bulk_execute` Temporal workflow = kernel code.** Line 55: "One workflow definition in kernel code handles all bulk operations."
- **Auto-generated CLI per entity**: "thin wrapper that constructs the spec, creates a queue message for visibility, directly invokes the `bulk_execute` Temporal workflow."
- The CLI wrapper lives in the CLI surface (kernel-side, auto-generated from entity definitions).
- **The `bulk_execute` workflow runs in the Temporal Worker.** Per the white paper's service architecture: "Temporal Worker. Executes associate workflows — the generic claim-process-complete cycle, bulk operations, platform deployments."
- The artifact DOES differentiate bulk operations from associate execution in phrasing — bulk ops are a generic kernel workflow, not an agent loop. This makes them legitimately kernel-side work: the `bulk_execute` workflow iterates entities and calls their methods, without any LLM reasoning. It's pure deterministic orchestration.
- Associate skills that invoke bulk CLI commands: the skill runs in a harness (per realtime-architecture-design), the skill makes a CLI call, the CLI invokes the kernel's `bulk_execute` workflow. Clean separation.
- **`bulk_op_requested` message**: created in the queue for visibility, ms before Temporal workflow claims it.

## Dependencies Declared

- Temporal (durable workflow engine — for `bulk_execute`)
- MongoDB transactions (per-batch atomicity)
- MongoDB limits awareness (~1000 ops/txn, ~60s timeout, 16MB doc)
- Existing watch mechanism (coalescing)
- OTEL tracing (correlation_id = workflow_id)
- changes collection (audit trail, queryable by bulk_operation_id)
- CSV reader, query iterator, stdin stream (deferred implementation details)

## Code Locations Specified

- **`bulk_execute` Temporal workflow** — kernel code (Temporal Worker execution context)
- **CLI verb wrappers** — auto-generated per entity as part of the CLI surface
- **`bulk_op_requested` message type** — part of the message schema
- **Queue processor** — acts on schedule-triggered messages to start workflows for scheduled associates

No specific file paths prescribed.

## Cross-References

- 2026-04-10-gic-retrace-full-kernel.md (coalescing surfaced)
- 2026-04-10-eventguard-retrace.md (351 venue deployments forced the issue)
- 2026-04-10-crm-retrace.md (overdue sweep + health monitoring)
- 2026-04-10-post-trace-synthesis.md (identified as item 7)
- 2026-04-10-realtime-architecture-design.md (watch coalescing mechanism this builds on)

## Open Questions or Ambiguities

From the artifact itself:
- **Whether `bulk_op_requested` queue message is useful in practice** or adds noise. Alternative: skip-the-queue (write directly to Temporal). Deferred to spec phase.
- Exact auto-generated CLI argument shapes, source abstractions, dry-run semantics, progress streaming format, cancellation semantics, per-batch retry policy, rate limiting for bulk ops touching external Integrations — all deferred to spec phase.
- Future: `bulk_apply` DSL for multi-entity-per-row, saga compensation for cross-batch rollback, `BulkOperation` entity for long-term spec history, cumulative state aggregation across batches. Added when forcing functions appear.

**Pass 2 observations:**
- **No architectural-layer deviation expected for bulk operations.** The design explicitly places `bulk_execute` in kernel code, running in the Temporal Worker. This is legitimate kernel territory — deterministic workflow orchestration with no agent reasoning.
- **The CLI verbs (bulk-create / bulk-transition / bulk-method / bulk-update / bulk-delete) should be checkable in the implementation.** Per comprehensive audit: "5 CLI verbs (create, transition, method, update, delete) — IMPLEMENTED" and "Selective emission discipline (bulk-update is silent) — IMPLEMENTED".
- **Potential subtle check**: does `bulk_execute` workflow live in the kernel Temporal Worker, SEPARATELY from any agent-execution activity? Per the design, yes — it's a generic workflow, not tangled with agent execution. If the current code conflates them (`process_with_associate` inside same worker as `bulk_execute`), that's fine topologically — both legitimately run in kernel-side Temporal Worker. But if the kernel-side Temporal Worker ALSO runs agent loops (per Finding 0), that's the problem — those loops should be in harness images subscribing to separate task queues, per the async-deepagents harness model.
