# Notes: /Users/home/Repositories/indemn-os/kernel/temporal/workflows.py

**File:** /Users/home/Repositories/indemn-os/kernel/temporal/workflows.py
**Read:** 2026-04-16 (full file — 255 lines)
**Category:** code

## Key Claims

- Module docstring: "Temporal workflows — durable execution wrappers. ProcessMessageWorkflow: generic claim → process → complete for all associates. HumanReviewWorkflow: waits for human decision via Temporal signals. BulkExecuteWorkflow: batched entity operations with progress tracking."
- Defines three `@workflow.defn` workflow classes.
- Imports activities from `kernel.temporal.activities` using `workflow.unsafe.imports_passed_through()`.
- `ProcessMessageWorkflow.run(message_id, associate_id)` — the durable 3-step cycle: claim → load context → process → complete.
- `HumanReviewWorkflow.run(message_id, escalation_hours=48)` — claims message, waits for `submit_decision` signal or times out.
- `BulkExecuteWorkflow.run(spec_dict)` — iterates batches via `process_bulk_batch` activity.
- Data classes: `BulkOperationSpec`, `BulkResult`.
- Uses `workflow.patched("v2-enhanced-error-handling")` for backward-compatible versioning.

## Architectural Decisions

- **All three workflow types live in the kernel Temporal Worker.** They execute the activities defined in `kernel/temporal/activities.py`.
- **`ProcessMessageWorkflow` calls `process_with_associate`** — the activity that contains the agent execution loop (Finding 0 code).
- Workflow durability: if worker crashes mid-workflow, Temporal replays from the last checkpoint (activity result).
- Timeout defaults: claim=30s, load_context=30s, process=10min with 2min heartbeat_timeout, complete=30s.
- Retry policies: 2-3 attempts with backoff; non-retryable for PermanentProcessingError, SkillTamperError, PermissionError.
- `HumanReviewWorkflow` uses Temporal signals — UI posts to endpoint → endpoint sends signal → workflow resumes.
- `BulkExecuteWorkflow` uses deliberate coupling: `bulk_operation_id = temporal_workflow_id`.

## Layer/Location Specified

- This file: `kernel/temporal/workflows.py` — kernel code, runs in the kernel Temporal Worker process.
- Workflows are registered by `kernel/temporal/worker.py` in `task_queue="indemn-kernel"`.

**Layer issue**:
- **`ProcessMessageWorkflow` orchestrates `process_with_associate`** which contains the agent loop. Per design, the agent execution should be in a harness, with the harness subscribing to a Temporal task queue named after the Runtime (not `"indemn-kernel"`).
- If the harness pattern were implemented per design, the `ProcessMessageWorkflow` (or an equivalent) would:
  - Run in the harness's Temporal worker (not the kernel's)
  - Or the kernel's worker writes to a Runtime-specific task queue; the harness claims it
  - The harness calls the agent loop, not the kernel

**However, `HumanReviewWorkflow` and `BulkExecuteWorkflow` are legitimately kernel-side:**
- `HumanReviewWorkflow` doesn't involve agent execution — just signals and activity calls for `process_human_decision`. Correct placement.
- `BulkExecuteWorkflow` is a generic kernel pattern (bulk ops pattern artifact). Correct placement.

So the layer issue is specifically `ProcessMessageWorkflow` + `process_with_associate` activity, not the other workflows in this file.

## Dependencies Declared

- `temporalio.workflow` — `@workflow.defn`, `@workflow.run`, `@workflow.signal`, `workflow.wait_condition`, `workflow.execute_activity`, `workflow.patched`, `workflow.unsafe.imports_passed_through`, `workflow.logger`
- `temporalio.common.RetryPolicy`
- `asyncio.TimeoutError` (via `asyncio`)
- Kernel activities: `claim_message`, `complete_message`, `fail_message`, `load_entity_context`, `preview_bulk_operation`, `process_bulk_batch`, `process_human_decision`, **`process_with_associate`**

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/temporal/workflows.py`
- Registered by: `kernel/temporal/worker.py`
- Calls activities from: `kernel/temporal/activities.py`
- Called by:
  - `kernel/message/dispatch.py` (optimistic dispatch after save_tracked)
  - `kernel/queue_processor.py` (sweep backstop)
  - `kernel/api/direct_invoke.py` (direct invocation endpoint)
  - `kernel/api/bulk.py` (bulk operation endpoint)

## Cross-References

- Phase 2-3 consolidated spec §2.2 (ProcessMessageWorkflow), §2.3 (HumanReviewWorkflow), §2.10 (BulkExecuteWorkflow)
- `kernel/temporal/activities.py` — activity implementations
- Design: 2026-04-10-realtime-architecture-design.md Part 4 — should be in harness, not kernel
- Design: 2026-04-10-bulk-operations-pattern.md — BulkExecuteWorkflow in kernel is correct

## Open Questions or Ambiguities

**Pass 2 findings:**

- **`ProcessMessageWorkflow` shouldn't exist in the kernel's Temporal worker** — at least the part that calls `process_with_associate`. Options for fix:
  1. Move `ProcessMessageWorkflow` to `harnesses/async-deepagents/`; kernel's workflows.py only keeps `HumanReviewWorkflow` and `BulkExecuteWorkflow`.
  2. Keep `ProcessMessageWorkflow` in the kernel but replace `process_with_associate` with a task-queue-routing activity that dispatches to a Runtime-specific queue.
  3. Split: the kernel's `ProcessMessageWorkflow` handles "process human review" and "process bulk"; a harness's `ProcessMessageWorkflow` handles "process associate work."
- **`HumanReviewWorkflow` and `BulkExecuteWorkflow` are correctly placed.** They should remain in the kernel.

**Secondary observations:**
- `workflow.patched("v2-enhanced-error-handling")` is called — G-77 versioning. Looks correct.
- Non-retryable errors (PermanentProcessingError, SkillTamperError, PermissionError) correctly configured.
- Human review timeout defaults to 48 hours — matches design.
- Bulk abort mode raises `BulkAbortError` which is non-retryable.
- Sentinel ObjectId `"000000000000000000000000"` used for human review claim — slightly hacky but fine.

This file itself is not the primary Finding 0 location (that's activities.py), but it's a direct caller of the problematic activity.
