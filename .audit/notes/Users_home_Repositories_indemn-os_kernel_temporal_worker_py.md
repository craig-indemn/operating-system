# Notes: /Users/home/Repositories/indemn-os/kernel/temporal/worker.py

**File:** /Users/home/Repositories/indemn-os/kernel/temporal/worker.py
**Read:** 2026-04-16 (full file — 82 lines)
**Category:** code

## Key Claims

- Module docstring: "Temporal worker — entry point for associate and kernel workflows. Runs: `python -m kernel.temporal.worker`. Processes associate workflows (ProcessMessage, HumanReview) and kernel workflows (BulkExecute) with OTEL tracing."
- Single Worker registered on task queue `"indemn-kernel"`.
- Registers 3 workflows: `ProcessMessageWorkflow`, `HumanReviewWorkflow`, `BulkExecuteWorkflow`.
- Registers 8 activities: `claim_message`, `load_entity_context`, **`process_with_associate`**, `process_human_decision`, `complete_message`, `fail_message`, `process_bulk_batch`, `preview_bulk_operation`.
- Uses OTEL TracingInterceptor.
- Worker config: `max_concurrent_activities=20`, `max_concurrent_workflow_tasks=10`, `graceful_shutdown_timeout=30`.

## Architectural Decisions

- **Single task queue for everything: `"indemn-kernel"`.**
- All workflows and activities live on this one queue.
- The worker is the `indemn-temporal-worker` Railway service — a kernel process with direct MongoDB access.
- OTEL tracing on every workflow + activity.
- Lifecycle: setup_logging → init_tracing → init_database → connect Temporal client → start worker.

## Layer/Location Specified

**This file is the kernel Temporal Worker entry point.**

- Runs as `python -m kernel.temporal.worker`.
- Deployed as the `indemn-temporal-worker` Railway service per Phase 0-1 spec.
- Inside the trust boundary — has direct MongoDB credentials.
- Registers `process_with_associate` as an activity — tying the kernel worker to agent execution.

**Per design (2026-04-10-realtime-architecture-design.md):**
- The kernel should have a Temporal Worker for kernel workflows (like BulkExecuteWorkflow, HumanReviewWorkflow, platform deployments).
- Agent execution should NOT be here — it should be in a separate async-deepagents harness image with its own Temporal worker, subscribing to a Runtime-specific task queue.

**The design distinction:**
- Kernel Temporal Worker: task queue `"indemn-kernel"` (or similar). Runs bulk operations, human review, deployment sagas, scheduled task creation.
- Async-deepagents harness's Temporal Worker: task queue `"runtime-{runtime_id}"` (e.g., `"runtime-async-default"`). Runs agent-execution activities (`process_with_associate`, skill interpretation, LLM tool-use loop).

**Current implementation conflates these:** everything runs on `"indemn-kernel"` in the kernel worker.

## Dependencies Declared

- `temporalio.contrib.opentelemetry.TracingInterceptor`
- `temporalio.worker.Worker`
- `kernel.db.init_database` (direct MongoDB init — confirms trust boundary is inside kernel)
- `kernel.observability.logging.setup_logging`
- `kernel.observability.tracing.init_tracing`
- `kernel.temporal.client.get_temporal_client`
- All activities from `kernel.temporal.activities`
- All workflows from `kernel.temporal.workflows`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/temporal/worker.py`
- Entry point: `python -m kernel.temporal.worker`
- Railway service name: `indemn-temporal-worker` (per Phase 0-1 spec)

## Cross-References

- Phase 2-3 spec §2.1 (Temporal Connection and Worker Setup)
- `kernel/temporal/activities.py` — the activities this worker runs
- `kernel/temporal/workflows.py` — the workflows this worker runs
- `kernel/temporal/client.py` — client factory
- Dockerfile + docker-compose.yml — deployment configuration

## Open Questions or Ambiguities

**Pass 2 findings:**

- **The worker registers `process_with_associate` as an activity.** Per design, agent execution should be in a separate harness image, not in the kernel worker.
- **Fix direction**: Split this worker into two:
  1. Kernel worker (this file): registers `claim_message`, `load_entity_context`, `complete_message`, `fail_message`, `process_human_decision`, `process_bulk_batch`, `preview_bulk_operation`. Keep `HumanReviewWorkflow` and `BulkExecuteWorkflow`. Remove `ProcessMessageWorkflow` and `process_with_associate`.
  2. Async-deepagents harness worker (new, in `harnesses/async-deepagents/`): registers `ProcessMessageWorkflow` + agent execution activities. Subscribes to a Runtime-specific task queue.
- The split requires:
  - A task queue naming convention (e.g., `"runtime-{runtime_id}"`)
  - The queue processor's dispatch to write to the appropriate task queue based on the associate's Runtime
  - The harness image to read its Runtime ID from env and subscribe to its task queue

**Secondary observations:**
- `graceful_shutdown_timeout=30` is reasonable.
- `max_concurrent_activities=20` and `max_concurrent_workflow_tasks=10` are deliberate caps to prevent MongoDB overload.
- OTEL tracing is correctly wired.

This file is concise and the architectural issue is clear: it registers too much. The kernel worker should be lighter and a harness worker should handle agent execution.
