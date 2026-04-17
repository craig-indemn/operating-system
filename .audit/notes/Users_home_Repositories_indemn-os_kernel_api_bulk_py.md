# Notes: /Users/home/Repositories/indemn-os/kernel/api/bulk.py

**File:** /Users/home/Repositories/indemn-os/kernel/api/bulk.py
**Read:** 2026-04-16 (full file — 97 lines)
**Category:** code

## Key Claims

- Module docstring: "Bulk operations API — start BulkExecuteWorkflow via Temporal. Entity-specific bulk endpoints are auto-registered. This provides bulk monitoring commands (status, list, cancel)."
- `bulk_router` at `/api/bulk` prefix.
- Endpoints:
  - `POST /api/bulk/start` — starts `BulkExecuteWorkflow` with spec
  - `GET /api/bulk/` — lists bulk workflows (filtered by status)
  - `GET /api/bulk/{workflow_id}` — gets status of a specific workflow
  - `POST /api/bulk/{workflow_id}/cancel` — cancels a workflow at next batch boundary
- All endpoints use Temporal client (`get_temporal_client`) for direct Temporal API interaction.
- Workflow IDs generated as `bulk-{uuid4().hex[:12]}`.

## Architectural Decisions

- Bulk monitoring queries Temporal directly (not MongoDB) — consistent with design ("execution state lives in Temporal").
- `list_workflows` uses Temporal's workflow query syntax: `"WorkflowType = 'BulkExecuteWorkflow'"`.
- Cancel is graceful (cancels at next batch boundary per design).
- Auth required on all endpoints.
- Workflow dispatched to `task_queue="indemn-kernel"` — consistent with current kernel worker.

## Layer/Location Specified

- Kernel code: `kernel/api/bulk.py`.
- Bulk ops are a kernel-provided pattern per design — runs in kernel Temporal worker.
- This file is the API surface for bulk operations; the actual workflow + activity is in `kernel/temporal/workflows.py::BulkExecuteWorkflow` + `kernel/temporal/activities.py::process_bulk_batch`.

**No layer deviation.** Bulk operations are correctly kernel-side per the bulk-operations-pattern design.

## Dependencies Declared

- `fastapi` — APIRouter, Depends, HTTPException
- `uuid.uuid4`
- `kernel.auth.middleware.get_current_actor`
- `kernel.temporal.client.get_temporal_client`
- `kernel.temporal.workflows.BulkExecuteWorkflow`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/api/bulk.py`
- Mounted in `kernel/api/app.py` via `bulk_router`
- Per-entity bulk start also exists in `kernel/api/registration.py::_register_bulk_route` (auto-generated per entity)
- CLI bulk commands in `kernel/cli/bulk_commands.py` + `kernel/cli/bulk_monitor.py`

## Cross-References

- Design: 2026-04-10-bulk-operations-pattern.md
- Phase 2-3 spec §2.10 Bulk Operations
- `kernel/temporal/workflows.py::BulkExecuteWorkflow`
- `kernel/temporal/activities.py::process_bulk_batch`
- `kernel/cli/bulk_commands.py`, `bulk_monitor.py`

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Auth only checks for authenticated actor — doesn't check per-entity permissions at this layer. Per-entity bulk start endpoint (in registration.py) does check permissions. This endpoint is more generic.
- No permission check on cancel — any authenticated actor can cancel any bulk. Possible security concern (should be limited to ops or the initiating actor).
- Error handling is minimal; catches generic Exception on describe.
- `list_workflows` iteration could be paginated — returns all results currently.

This file is correctly placed and implements the bulk monitoring design. Permission model for cancel may be a minor improvement opportunity but not a layer issue.
