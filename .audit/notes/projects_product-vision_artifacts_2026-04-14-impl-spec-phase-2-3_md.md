# Notes: 2026-04-14-impl-spec-phase-2-3.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-2-3.md
**Read:** 2026-04-16 (sampled opening + workflow definition; 961 lines total. SUPERSEDED by consolidated.)
**Category:** spec-superseded

## Key Claims

Base Phase 2+3 implementation spec. **SUPERSEDED** by 2026-04-14-impl-spec-phase-2-3-consolidated.md (integrates base + gap resolutions).

Key content:
- **Phase 2** = Associate Execution: Temporal client + generic `ProcessMessageWorkflow` + `process_with_associate` activity + deterministic + reasoning + hybrid execution modes + `--auto` pattern.
- **Phase 3** = Integration Framework: adapter base class + ADAPTER_REGISTRY + credential resolution + dispatch with auto-refresh + webhook endpoint + Outlook + Stripe reference adapters.
- **Generic ProcessMessageWorkflow**: claim → load context → process → complete. "Skill is source of truth for orchestration — workflow is durability wrapper."

## Architectural Decisions

- **Temporal integration patterns** (from session 4 designs).
- **Generic single workflow** for all associate processing.
- **Kernel capabilities via `--auto` pattern** (per session 4).
- **Adapter pattern with `provider:version` registry** (from session 5 integration-as-primitive).
- **Webhook endpoint** at `/webhook/{provider}/{integration_id}` (from documentation-sweep item 4).

## Layer/Location Specified

- **`kernel/temporal/client.py`** — Temporal client factory.
- **`kernel/temporal/workflows.py`** — ProcessMessageWorkflow, HumanReviewWorkflow, BulkExecuteWorkflow.
- **`kernel/temporal/activities.py`** — `process_with_associate` + `_execute_deterministic` + `_execute_reasoning` + `_execute_hybrid` — **AGENT EXECUTION IN KERNEL** (Finding 0 source in spec).
- **`kernel/integration/adapter.py`** + `registry.py` + `resolver.py` + `credentials.py` + `dispatch.py`.
- **`kernel/integration/adapters/outlook.py`** + `stripe_adapter.py`.
- **`kernel/api/webhook.py`**.

**Finding 0 relevance**:
- **THIS IS WHERE FINDING 0 ENTERS THE SPEC.** `process_with_associate` is placed as a kernel Temporal activity.
- `_execute_reasoning` contains the LLM loop (20 iterations), importing `anthropic` directly.
- Task queue is `indemn-kernel` (single queue, not per-Runtime as realtime-architecture-design specifies).
- No mention of async-deepagents harness; agent execution is assumed to run in kernel Temporal worker.
- **The consolidated version of this spec inherits the same Finding 0.**

## Dependencies Declared

- Temporal SDK + TracingInterceptor
- `anthropic` (imported in `_execute_reasoning`)
- httpx (for CLI-command-via-API in activity)
- MongoDB (for entity/message/skill/integration storage)
- AWS Secrets Manager (for credentials)

## Code Locations Specified

Same as consolidated spec. Main locations:
- `kernel/temporal/{client,workflows,activities,worker}.py`
- `kernel/integration/{adapter,registry,resolver,credentials,dispatch,rotation}.py`
- `kernel/integration/adapters/{outlook,stripe_adapter}.py`
- `kernel/api/{webhook,direct_invoke,bulk,bootstrap}.py`
- `kernel/queue_processor.py` (additions: `dispatch_associate_workflows`, `check_scheduled_associates`)

## Cross-References

- 2026-04-13-white-paper.md
- 2026-04-09-temporal-integration-architecture.md (source)
- 2026-04-09-unified-queue-temporal-execution.md (source)
- 2026-04-10-integration-as-primitive.md (source)
- 2026-04-09-entity-capabilities-and-skill-model.md (source — `--auto` pattern, skill model)
- 2026-04-10-bulk-operations-pattern.md (source — bulk workflows)
- 2026-04-14-impl-spec-phase-0-1.md (foundation, this builds on)
- 2026-04-14-impl-spec-phase-2-3-consolidated.md (SUPERSEDES this)
- 2026-04-14-impl-spec-gaps.md (22 gaps identified)

## Open Questions or Ambiguities

- All 22 gaps from gap analysis SURVIVE resolution in consolidated spec.
- **Finding 0 deviation (agent execution in kernel) is NOT flagged as a gap** — it's baked into both this spec and the consolidated spec.

**Supersedence note**: SUPERSEDED by consolidated. The Finding 0 deviation EXISTS IN BOTH.
