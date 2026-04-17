# Notes: 2026-04-09-unified-queue-temporal-execution.md

**File:** projects/product-vision/artifacts/2026-04-09-unified-queue-temporal-execution.md
**Read:** 2026-04-16 (full file — 243 lines)
**Category:** design-source

## Key Claims

- **"The queue is ALWAYS MongoDB. For everyone."** Temporal is the execution engine associates use to PROCESS items from the shared queue. NOT the queue backend.
- **"Associates are employees"**: humans and associates share the same queue, same claim mechanism (`findOneAndUpdate`), same entity assignments, same role/permissions/observability. Only difference: execution mode.
- **Per-associate execution flow**:
  - Entity save → outbox (same MongoDB txn) → outbox poller reads → evaluates watches → writes to MongoDB `message_queue` ALWAYS → if role has associate actors, ALSO starts Temporal workflow.
  - Workflow's FIRST activity is **claim the message from the queue**.
  - If already claimed (human beat it), workflow exits gracefully.
  - Subsequent activities: load context, execute skill (CLI `--auto` + LLM if needed), save entity changes, mark message complete.
- **Gradual rollout model** (GIC example):
  - Week 1: Humans only on role → messages enter queue → humans claim.
  - Week 2: Add associate to role → workflows start, associate claims first (most of the time).
  - Week 3: Remove humans from role → associate handles all.
  - Week 4: Escalation (associate marks `needs_review`) → new message to underwriter queue.
  - **"At no point does the infrastructure change. The only thing that changes is who has which role."**
- **Temporal is down? Nothing lost.** Queue accumulates; humans process; backlog resumes when Temporal recovers.
- **"Optimization"** (noted at end): move watch evaluation INTO entity save transaction ("microseconds") so outbox record already contains the dispatch decision. Eliminates the "evaluate differently on retry" issue. **This is the proto-optimistic-dispatch pattern that becomes the Phase 2-3 MVP mechanism.**

## Architectural Decisions

- **Queue and execution are SEPARATE concerns.** MongoDB is queue infrastructure; Temporal is durable-execution infrastructure for associates. They coordinate via the claim primitive.
- **One message_queue schema for all actors.** Fields: org_id, entity_type, entity_id, event, target_role, status, claimed_by, claimed_at, visibility_timeout, priority, context (enriched entity data), correlation_id, causation_id, depth, created_at. (This schema broadly matches what ended up in `kernel/message/schema.py`.)
- **Humans interact via UI + CLI against MongoDB** directly. Associates interact via Temporal workflows.
- **Watch evaluation lives in the outbox poller** (or optimistically in the save path per the closing note).
- **Temporal Cloud is the execution host** ($100/mo).

## Layer/Location Specified

- **Queue = MongoDB `message_queue` collection** — kernel-level infrastructure.
- **Queue history = MongoDB `message_log`** — kernel-level.
- **Watch evaluation = outbox poller (regular Python)** — kernel-level process. (Later: moved into the save-tracked path per Phase 2-3 spec.)
- **Entity storage = MongoDB via Beanie** — kernel-level.
- **Associate execution = Temporal workflows** — in this artifact, workflows are run by "Temporal workers" with UNSPECIFIED location. Could be kernel or harness. This file does NOT pick a side.
- **Human interaction = UI + CLI against MongoDB**.
- **Scheduled tasks (simple) = OS scheduler/cron; (multi-step) = Temporal Schedules.**
- **Audit trail = MongoDB `changes` collection, same transaction as entity save.**
- **Observability = OTEL (entity + Temporal + LLM)**.

**Relevance to Finding 0**:
- This artifact establishes the SHAPE of the Phase 2-3 spec's claim-and-process pattern.
- It does NOT specify whether Temporal workers are in-kernel or external.
- One day later, 2026-04-10-realtime-architecture-design.md places workers in harness images outside the kernel.
- Phase 2-3 spec implemented workers as kernel processes → Finding 0 entry point.

## Dependencies Declared

- MongoDB + Beanie + Pydantic (queue + entities + message_log + changes + outbox)
- Temporal Cloud (Essentials)
- Temporal Python SDK
- OTEL + Temporal OTEL Interceptor
- UI + CLI clients (for humans)

## Code Locations Specified

- No explicit absolute paths. Concepts:
  - `ProcessMessageWorkflow` (generic associate workflow)
  - `Activity 1-N` pattern (Claim → Load → Execute → Save → Complete)
- Implementation of `ProcessMessageWorkflow` ended up in `kernel/temporal/workflows.py::ProcessMessageWorkflow` with activities in `kernel/temporal/activities.py`. That implementation faithfully follows the pattern here — **but the design left worker location open; spec chose kernel**.

## Cross-References

- 2026-04-09-temporal-integration-architecture.md (previous — this artifact supersedes "queue = Temporal task queue" with "queue = MongoDB + Temporal is execution only")
- 2026-04-10-realtime-architecture-design.md (one day later — places Temporal workers in harness images outside kernel)
- Phase 2-3 consolidated spec §2.4 (implements the activity pattern; choice of worker location = kernel → Finding 0)
- Phase 2-3 spec's `save_tracked` + optimistic dispatch = implementation of the closing-note "Optimization"

## Open Questions or Ambiguities

- **Workflows per role vs. per pipeline** — resolved as generic `ProcessMessageWorkflow`.
- **Multi-org task queue sharing** — not discussed. (Phase 2-3 spec uses single `"indemn-kernel"` queue for everything, not per-Runtime as realtime-architecture-design later specifies.)
- **Worker deployment location** — DELIBERATELY OPEN in this artifact. This openness is what lets the Phase 2-3 spec interpret it as "kernel process" without contradicting this design doc. But the realtime-architecture-design (next day) closes the open question as "harness image outside kernel."

**Supersedence note for vision map**:
- "Queue = MongoDB, execution = Temporal" — SURVIVES, core invariant.
- "Associates are employees" — SURVIVES.
- "Outbox poller pattern" — superseded by optimistic dispatch + sweep backstop.
- "Worker location" — DELIBERATELY OPEN here; CLOSED by realtime-architecture-design as "harness image outside kernel." Specs that say "kernel process" contradict the later closure.
- The "Optimization" closing note → becomes the Phase 2-3 MVP mechanism.
