---
ask: "How do bulk operations work in the kernel — the pattern, execution, events, failure handling, and how scheduled and ad-hoc operations unify under one mechanism?"
created: 2026-04-10
workstream: product-vision
session: 2026-04-10-b
sources:
  - type: conversation
    description: "Craig and Claude working through bulk operations design — the first design session in the post-retrace sequence (session 6)"
  - type: artifact
    description: "2026-04-10-gic-retrace-full-kernel.md (surfaced coalescing as a concern)"
  - type: artifact
    description: "2026-04-10-eventguard-retrace.md (351 venue deployments forced bulk operations as a design item)"
  - type: artifact
    description: "2026-04-10-crm-retrace.md (overdue sweep + health monitoring as recurring bulk workloads)"
  - type: artifact
    description: "2026-04-10-post-trace-synthesis.md (identified bulk operations as item 7)"
  - type: artifact
    description: "2026-04-10-realtime-architecture-design.md (watch coalescing mechanism this builds on)"
---

# Bulk Operations Pattern

## Context

Item 7 from the post-trace synthesis. Three workloads forced the issue:

- **GIC hourly stale check** — find 50+ stale submissions, update them, coalesce the resulting events into one ops queue item
- **EventGuard 351 venue deployments** — one-shot CSV import, progress visibility, idempotent on resume, doesn't spam the onboarder queue
- **CRM daily overdue sweep** — bulk-update action items, per-owner scoped coalescing (each owner sees their batch, ops sees the aggregate)
- **Future**: data migrations and reprocessing — 10K+ entity ops, progress tracking, resumability

Common shape across all of them: **iterate a source, apply a deterministic operation per item, in batches, with progress and resumability.**

## Decision: Pattern, Not Primitive

Bulk operations are a **kernel-provided pattern**, composed from existing primitives:

- Message (the queue entry for visibility)
- Temporal workflow (the generic `bulk_execute` engine)
- MongoDB transactions (per-batch atomicity)
- Watch coalescing (rendering collapse at the queue layer)
- Selective emission (events preserved: one save = one event)
- OTEL traces + changes collection (audit)

**No 7th structural primitive. No new bootstrap entity.** The six-primitive count (Entity, Message, Actor, Role, Organization, Integration) is stable. The six-bootstrap-entity count (Org, Actor, Role, Integration, Attention, Runtime) is stable.

The spec of a bulk operation (entity type, operation, source, batch size) does NOT persist as an entity. Its execution history lives in Temporal workflow state during execution, and its effects live in the changes collection permanently (queryable by `bulk_operation_id = temporal_workflow_id`).

**Trade-off accepted**: the operation spec itself (what was requested, by whom, with what source) decays with Temporal retention (~weeks). The entity changes it produced are permanent via the changes collection. For scheduled ops, the spec is in the associate's skill (persisted data). For ad-hoc ops, the changes collection shows every entity touched. This is sufficient for MVP. If long-term spec history becomes load-bearing for compliance, a `BulkOperation` entity can be added later — the upgrade is additive and non-breaking.

## The Mechanism

### Generic `bulk_execute` Temporal workflow

One workflow definition in kernel code handles all bulk operations. Parameters:

- `entity_type`
- `operation`: one of create, update, transition, method, delete
- `source`: CSV file, query filter, explicit list, or stdin
- `batch_size`
- `idempotency_key`: hash of the operation spec
- `failure_mode`: skip (default) or abort

### Entry points (three, one mechanism)

1. **Auto-generated CLI per entity**: `indemn <entity> bulk-*` commands. Thin wrapper that constructs the spec, creates a queue message for visibility, directly invokes the `bulk_execute` Temporal workflow, returns the workflow ID. Same pattern as real-time direct invocation from the realtime-architecture session.
2. **Scheduled associate**: associate with cron trigger whose skill invokes a bulk CLI command. Kernel makes no distinction — the skill is the bulk op source.
3. **Direct invocation**: any actor (human, associate, CLI script) can invoke a bulk op via CLI.

### Event emission

- **Per-entity events**: "one save = one event" is preserved. 351 entity writes produce 351 events.
- Each event carries `context.bulk_operation_id = <temporal_workflow_id>`.
- Watches with `coalesce: {strategy: by_bulk_operation_id, window: Xm, summary_template: "..."}` collapse them at queue rendering time.
- Scoped watches (`scope: field_path` or `scope: active_context`) resolve per event at emit time. Coalescing is applied per-target-actor, so each stakeholder sees their own coalesced batch.

### Atomicity

- **Per-batch transaction** only. MongoDB limits: ~1000 operations per transaction, ~60s timeout, 16MB document limit. Batch size is tuned to stay comfortably under these limits.
- Cross-batch failure puts the operation in partial state. Temporal replay handles recovery — the workflow's batch activity is idempotent at the operation level (via state machine, external_ref, or author-enforced idempotency).
- **No cross-batch rollback for MVP.** Dry-run is the safety net for destructive ops. Saga compensation is deferred until a specific operation forces the need.

### Progress and visibility

- `indemn bulk status <workflow_id>` queries Temporal workflow state directly.
- `indemn bulk list [--status pending|running|completed|failed]` lists active and recent workflows.
- `indemn bulk cancel <workflow_id>` — graceful stop at the next batch boundary.
- `indemn bulk retry <workflow_id>` — re-runs a failed op from the idempotency checkpoint.

## Clarification: CLI Verb Taxonomy

A key discipline fell out of the CRM retrace: **selective emission must be preserved through bulk operations**. Raw field updates don't emit events. State transitions and @exposed method invocations do. Bulk CLI verbs map to this distinction:

| CLI | For | Emits events? |
|---|---|---|
| `<entity> bulk-create` | New entity creation | Yes (creation events) |
| `<entity> bulk-transition` | State machine transitions | Yes (state_changed events) |
| `<entity> bulk-method <name>` | @exposed business operations | Yes (method_invoked events) |
| `<entity> bulk-update` | Raw field updates (migrations, backfills) | **No** — silent |
| `<entity> bulk-delete` | Deletion (gated, dry-run required) | Yes (deletion events) |

**The principle**: if a field change should cascade through watches, wrap it in an @exposed method and use `bulk-method`. If it's a data migration or backfill that should be silent (no notifications, no derived work triggered), use `bulk-update`.

This discipline is enforced at the CLI level. A developer writing a bulk operation is forced to choose the right verb, which makes the semantic explicit.

### Example: CRM overdue sweep (the motivating case for this clarification)

**Wrong**: `indemn action-item bulk-update --filter '...' --set is_overdue=true`. Raw field update, no events, ops doesn't get notified, sweep is invisible.

**Right**: Add `mark_overdue()` as an @exposed method on ActionItem. Then: `indemn action-item bulk-method --method mark-overdue --filter '...'`. Method invocation emits events. Ops and account_owner watches fire. Coalescing produces per-target-actor summaries.

**Rule of thumb**: if it should cascade, make it a method.

## Scheduled + Ad-hoc Unification

GIC's hourly stale check and EventGuard's one-shot venue import use **the same mechanism**:

**GIC (scheduled)**:
1. Cron fires → message in queue for `stale_checker` role
2. Queue Processor starts Temporal workflow for the Stale Checker associate
3. Associate skill: `indemn submission bulk-transition --filter '{...}' --to stale --batch-size 50`
4. CLI creates a bulk_op message + directly invokes `bulk_execute` workflow
5. Workflow runs the iteration, emits 47 events with shared bulk_operation_id
6. Watches coalesce per target actor

**EventGuard (ad-hoc)**:
1. Admin runs: `indemn deployment bulk-create --from-csv venues.csv --batch-size 50` (single-entity case)
2. CLI creates a bulk_op message + directly invokes `bulk_execute` workflow
3. Workflow runs the iteration, emits events
4. Onboarder role sees a coalesced completion summary

The kernel makes no distinction between "scheduled bulk ops" and "ad-hoc bulk ops." Both are invocations of the same `bulk_execute` workflow with different triggers.

## Multi-Entity-Per-Row: Option α

EventGuard's venue import creates three entities per row (Venue, VenueAgreement, Deployment) with references between them. Two options were considered:

- **Option α**: Keep `bulk-*` CLI single-entity. Multi-entity cases are handled by skill code — an associate iterates the source and creates multiple entities per row, wrapped in per-row transactions.
- **Option β**: Add a `bulk_apply` DSL with per-row multi-entity operation specs, field mappings, and entity references.

**Decision: Option α.** Reasons:

1. **Simplicity earned**: `bulk-*` CLI stays narrow and intuitive. Complex cases escape to skill code where the full actor model is available.
2. **Multi-entity bulk is rare**: EventGuard's venue import is a one-shot setup. Data migrations are rare. Common bulk cases (stale sweeps, overdue checks, health scoring) are single-entity.
3. **Natural expansion path**: if we find ourselves writing the same multi-entity skill three times, that's the forcing function to promote `bulk_apply` with a DSL. Until then, skill code is the right tool.

**Trade-off with α**: EventGuard's 351 venues takes 10-30 seconds wall time (per-row transactions) instead of ~1 second (batch transactions). For one-shot setup commands, acceptable.

## Failure Handling: Skip-and-Continue (Default)

When a batch encounters a failure mid-iteration, the default is **skip-and-continue with error tracking**.

### Default: `skip` mode

Within a batch transaction:

```
for each entity in batch:
    try:
        load, operate, save  # save emits event within txn
    except PermanentError:
        record {entity_id, error_type, message}
        continue
    except TransientError:
        raise  # propagates; Temporal retries the whole activity
commit transaction with successful writes + their events
```

### Error classification

| Error | Class | Handling |
|---|---|---|
| StateMachineError (invalid transition, already in target state) | Permanent | Skip, record |
| ValidationError (invalid field values) | Permanent | Skip, record |
| PermissionDenied | Permanent | Skip, record |
| EntityNotFound (concurrent delete) | Permanent | Skip, record |
| VersionConflict (first attempt) | Transient (retry once) | Retry; if fails again, treat permanent |
| Network / MongoDB internal errors | Transient | Propagate → Temporal retries |
| Lock timeout | Transient | Propagate → Temporal retries |

### Workflow terminal states

- `completed` — all succeeded
- `completed_with_errors` — forward progress made, some skipped (still a successful run)
- `failed` — catastrophic (couldn't start, or abort-mode and any failure)

### Opt-in: `--failure-mode=abort`

For operations where partial completion is worse than total failure (multi-entity imports where rows depend on each other, admin operations that must fully commit or not at all), the CLI takes `--failure-mode=abort`. Any permanent error aborts the batch via transaction rollback, the workflow ends in `failed`, nothing committed. The caller investigates and fixes before retrying.

**Default is `skip`. `abort` is explicit opt-in.**

### Observability

`indemn bulk status <workflow_id>` surfaces the full failure detail:

```
Bulk op BULK-abc123
Status: completed_with_errors
Source: filter (status=pending, last_activity_at<7d, followup_count>=2)
Operation: bulk-transition → stale
Processed: 47 / 47
Succeeded: 43
Skipped: 4
  SUB-042: StateMachineError — already in 'closed' state
  SUB-089: ValidationError — missing primary_owner_id
  SUB-104: VersionConflict — concurrent modification, retry exhausted
  SUB-127: EntityNotFound — deleted during processing
Duration: 1.2s
```

## Idempotency Coupling

Skip-and-continue only works because bulk operations expect idempotency at the entity level:

- **bulk-transition**: state machine is naturally idempotent. An entity already in the target state is either a no-op or a permanent error that gets skipped — same practical outcome.
- **bulk-create**: `external_ref` on source rows prevents duplicates on replay. First row with `external_ref=X` creates; subsequent rows with the same ref are skipped (permanent "already exists" error).
- **bulk-method**: the @exposed method's author is responsible for idempotency. Documented requirement. Not enforced by the kernel in MVP.
- **bulk-update**: silent by definition. Idempotency by field assignment (setting X=true is idempotent regardless of current state).
- **bulk-delete**: naturally idempotent (entity already deleted → skip).

## Worked Example: GIC Hourly Stale Check

Full trace through the pattern:

1. **T+0**: cron fires. Kernel creates a message in message_queue targeting `stale_checker` role, event_type=`schedule_fired`.
2. **Queue Processor** sees the message. Role has an associate attached. Starts Temporal workflow for the Stale Checker associate.
3. **Associate workflow** claims the message, loads the skill. Skill: "Run `indemn submission bulk-transition --filter '{"status": "pending", "last_activity_at": "older_than:7d", "followup_count": "gte:2"}' --to stale --batch-size 50`."
4. **CLI command** parses the filter, constructs the bulk op spec, hashes for idempotency_key, creates a `bulk_op_requested` message in the queue (for visibility), directly invokes `bulk_execute` Temporal workflow. Returns the workflow ID.
5. **`bulk_execute` workflow**:
   - Claims the bulk_op_requested message (direct invocation).
   - Resolves source: queries MongoDB with filter, gets 47 submission IDs.
   - Processes batch 1 (all 47 fit): begin transaction. For each, load entity, call `transition_to("stale")`, save. State machine enforces. Each save emits one event (`state_changed[to=stale]`) with `context.bulk_operation_id = <workflow_id>`. All 47 entity writes + 47 event writes commit atomically.
   - Updates Temporal state (processed=47, succeeded=47, failed=0). Completes.
6. **Watches evaluate** per emitted event:
   - **Ops role watch** matches all 47 → coalesce by bulk_operation_id → **1 queue item for ops**: "47 submissions became stale."
   - **Account_owner role watch** resolves scope per event (reads `submission.primary_owner_id` from the already-loaded entity), distributes 47 events across ~12 owners, coalesces per-target-actor → **12 queue items**, each owner sees "N of your submissions became stale."
7. **Audit**: changes collection has 47 entries with bulk_operation_id. OTEL trace under correlation_id=workflow_id.

**Result**: nobody is spammed. Ops has aggregate visibility. Each owner has a personalized batch. All deterministic operations completed in one transaction. Full audit in changes + OTEL.

## What's Decided

1. Bulk operations are a kernel-provided pattern, not a primitive and not a new bootstrap entity
2. Generic `bulk_execute` Temporal workflow (kernel code) handles all bulk operations
3. `bulk_operation_id = temporal_workflow_id` (coupling accepted for simplicity)
4. Entry points: auto-generated CLI per entity, scheduled associate skill invocations, direct invocations — all same mechanism
5. CLI verb taxonomy: bulk-create / bulk-transition / bulk-method / bulk-update / bulk-delete
6. Raw field updates that should cascade must go through @exposed methods + bulk-method
7. Per-batch MongoDB transaction for atomicity; per-entity event emission; selective emission preserved
8. Coalescing via existing watch mechanism (`coalesce: {strategy: by_bulk_operation_id, ...}`)
9. Multi-entity-per-row cases use skill code (Option α); `bulk_apply` DSL deferred
10. Failure handling default: skip-and-continue with error list; `--failure-mode=abort` opt-in
11. Error classification: permanent (skip) vs transient (Temporal retries)
12. Workflow terminal states: completed / completed_with_errors / failed
13. Idempotency: entity-level, via state machine / external_ref / method author
14. No cross-batch rollback for MVP; dry-run is the safety net; saga compensation deferred

## What's Deferred to Spec Phase

Implementation details that don't block the pattern:

- Exact auto-generated CLI argument shapes per operation verb
- Source abstractions: CSV reader implementation, query iterator semantics, stdin streaming, explicit list format
- Dry-run semantics: what it outputs, what it validates, how it presents preview
- Progress streaming format: `indemn bulk status --follow` as long-running subprocess
- Cancellation semantics details: exact checkpoint of graceful stop, state preservation during cancel
- Per-batch retry policy: Temporal retry settings (max attempts, backoff)
- Rate limiting for bulk ops that touch external Integrations (don't DDoS the carrier API)

## What's Deferred to Future Design

- **`bulk_apply` DSL with per-row multi-entity operations** — add when a real use case requires it beyond one-shot skill code
- **Saga compensation for cross-batch rollback** — add when a specific operation type demands strict all-or-nothing across batches
- **Kernel-provided `BulkOperation` entity** — add when long-term spec history becomes load-bearing for compliance or operations
- **Cumulative state aggregation across bulk batches** — e.g., "when 100 items have failed this op, stop" — not needed for known workloads

## Relationship to Other Primitives

| Primitive | How Bulk Ops Use It |
|---|---|
| Entity | The operand. Bulk ops operate on entities via their auto-generated methods. |
| Message | The queue entry for visibility. `bulk_op_requested` messages flow through the standard queue. |
| Actor | Bulk ops are initiated by actors (human CLI, scheduled associate, ad-hoc associate). The `bulk_execute` workflow runs under the initiating actor's identity. |
| Role | Scheduled bulk ops use associate roles. The CLI enforces role permissions on the entities operated on. |
| Organization | Org scoping is automatic — bulk ops only touch entities in the initiating actor's org. |
| Integration | Bulk ops don't directly use Integration, but bulk methods that invoke entity methods that call Integrations will use them per-entity. |

## Open Question (Not Blocking, Spec-Phase Decision)

The `bulk_op_requested` message is created for queue visibility. It sits in the queue for milliseconds before the Temporal workflow claims it. Is the queue visibility useful in practice, or does it add noise?

Alternative: bulk_execute workflow writes its status directly to Temporal without a pre-claim message. The queue query for "active bulk ops" reads directly from Temporal.

Both options work. The queue-visible approach is consistent with the "one queue for everything" principle. The skip-the-queue approach is simpler. Defer to spec phase — not blocking.
