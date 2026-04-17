# Notes: 2026-04-14-impl-spec-phase-2-3-consolidated.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-2-3-consolidated.md
**Read:** 2026-04-16 (full file — 2015 lines; read sections 1-760 in full covering Phase 2 Temporal/worker/workflows/activities; section headers via grep; Phase 3 integration sections 1355-2015 spot-read)
**Category:** spec

## Key Claims

- Phase 2 = Associate Execution. Phase 3 = Integration Framework.
- "Phase 2 adds durable associate execution via Temporal. Phase 3 adds external system connectivity via the Integration kernel entity and adapters."
- **Explicitly deferred**: Base UI (Phase 4), Full authentication (Phase 4), Real-time channels, **harness pattern**, Attention activation, Runtime deployment (Phase 5), Saga-style cross-batch rollback (post-MVP), bulk_apply DSL (post-MVP).
- Generic `ProcessMessageWorkflow` — one workflow for ALL associate message processing. "The skill is the source of truth for orchestration. Temporal wraps the generic claim → process → complete cycle for durability."
- `HumanReviewWorkflow` for human-in-the-loop decisions via Temporal signals.
- `BulkExecuteWorkflow` — generic bulk operation workflow. `bulk_operation_id = temporal_workflow_id`.
- Scheduled task execution: Phase 2 MVP uses application-level cron in queue processor; future upgrade to Temporal Schedules.
- Direct invocation endpoint at `/api/associates/{associate_id}/invoke` for real-time channels and testing.
- Phase 3 adapter base class (outbound: fetch, send, charge; inbound: validate_webhook, parse_webhook; auth: auth_initiate, auth_callback, refresh_token).
- Adapter registry keyed by `provider:version`.
- Credential resolution order: actor personal → owner's personal (for owner-bound associates) → org-level with role-based access.
- Outlook and Stripe adapters as reference implementations.

## Architectural Decisions

### Phase 2 (CRITICAL — Source of Finding 0)

- **`kernel/temporal/worker.py` is the kernel Temporal Worker entry point** (`python -m kernel.temporal.worker`). Per its docstring: "Executes associate workflows and kernel workflows."
- **Worker registers** 3 workflows (ProcessMessageWorkflow, HumanReviewWorkflow, BulkExecuteWorkflow) and 6 activities (claim_message, load_entity_context, **process_with_associate**, complete_message, fail_message, process_bulk_batch).
- Worker config: max_concurrent_activities=20, max_concurrent_workflow_tasks=10, graceful_shutdown_timeout=30, OTEL TracingInterceptor.
- **`process_with_associate` IS THE AGENT EXECUTION LOOP placed inside the kernel Temporal Worker as an activity.** It:
  - Loads associate config (Actor.get)
  - Sets auth context (current_org_id, current_actor_id, current_correlation_id, current_depth)
  - Loads + verifies skills (Skill.find_one, verify_content_hash)
  - Dispatches to `_execute_deterministic`, `_execute_reasoning`, or `_execute_hybrid` based on associate.mode
- **`_execute_reasoning` implements the LLM tool-use loop INSIDE THE KERNEL**:
  - `import anthropic` at line 557
  - `client = anthropic.AsyncAnthropic()` at line 563
  - `client.messages.create(model=model, tools=[{execute_command tool}], ...)` at line 590
  - Iterates up to 20 times, feeding tool results back to LLM
  - "For Phase 2 MVP: use Anthropic API directly. Future: pluggable LLM provider per associate.llm_config"
- **`_execute_deterministic` parses markdown skill line-by-line** and executes CLI commands via HTTP.
- **`_execute_hybrid`**: try deterministic first; if any step returns `needs_reasoning`, fall back to `_execute_reasoning`.
- **`_execute_command_via_api`**: the agent executes "CLI commands" by making HTTP POST to the kernel's API. Parses `indemn email classify EMAIL-001 --auto` → POST to `/api/emails/EMAIL-001/classify`. **This is the agent-to-kernel interface within the same monolith.**
- Context propagation via headers: `X-Correlation-ID`, `X-Cascade-Depth`. API middleware reads headers and sets contextvars.
- **Optimistic dispatch**: API fires-and-forgets Temporal workflow start after save_tracked() commits.
- **Sweep backstop**: Queue processor checks every few seconds for undispatched associate-eligible messages.
- **Direct invocation endpoint** `/api/associates/{associate_id}/invoke` creates queue entry AND starts workflow immediately.

### Phase 3 (Integration Framework)

- Adapter base class `Adapter(ABC)` in `kernel/integration/adapter.py` — abstract methods for fetch/send/charge/validate_webhook/parse_webhook/auth_initiate/auth_callback/refresh_token.
- Adapter registry `ADAPTER_REGISTRY` in `kernel/integration/registry.py`, keyed by `provider:version`.
- Credential resolver `resolve_integration()` in `kernel/integration/resolver.py`.
- Credential management with OAuth token refresh in `kernel/integration/credentials.py`.
- Adapter dispatch in `kernel/integration/dispatch.py` with auto-refresh on AdapterAuthError.
- Webhook endpoint in `kernel/api/webhook.py` — `/webhook/{provider}/{integration_id}` — looks up Integration, invokes adapter's validate_webhook + parse_webhook.
- Outlook adapter (email) and Stripe adapter (payments) as reference implementations in `kernel/integration/adapters/`.

## Layer/Location Specified

**CRITICAL — This is the Finding 0 source in the spec:**

The Phase 2 spec places agent execution INSIDE THE KERNEL at these specific locations:

| Location | Content |
|---|---|
| `kernel/temporal/worker.py` | Worker process definition (entry: `python -m kernel.temporal.worker`). Runs in the kernel Docker image as the `indemn-temporal-worker` Railway service. |
| `kernel/temporal/workflows.py` | `ProcessMessageWorkflow`, `HumanReviewWorkflow`, `BulkExecuteWorkflow` — durable workflow definitions. |
| `kernel/temporal/activities.py` | **`process_with_associate`** — the agent loop. Includes `_execute_deterministic`, `_execute_reasoning` (with Anthropic LLM tool-use loop), `_execute_hybrid`. Imports `anthropic` library. |

**Per the trust boundary stated in Phase 0-1 CLAUDE.md**: "kernel processes (API, QP, TW) have direct MongoDB." The Temporal Worker is a kernel process with full DB credentials. **This means agent execution runs INSIDE the trust boundary, with DB credentials, with `import anthropic`.**

**Per the design (2026-04-10-realtime-architecture-design.md)**: agent execution should run in harness images outside the kernel, with only CLI authentication, bridging a specific framework (deepagents/LangChain) and transport (LiveKit/WebSocket/Temporal) to the kernel via `execute_command` style CLI subprocess calls. The harness for async would be `indemn/runtime-async-deepagents:1.2.0` — a separate image.

**The Phase 2 spec does NOT implement the harness pattern.** It embeds agent execution as kernel-side Temporal activities. This is where Finding 0 was introduced into the design → spec pipeline.

### Phase 3 layer claims

- Adapters live in `kernel/integration/adapters/` — kernel code, consistent with the design (adapters are kernel code per 2026-04-10-integration-as-primitive.md).
- Adapter registry, resolver, credentials, dispatch all in `kernel/integration/` — kernel code.
- Webhook endpoint at `kernel/api/webhook.py` — part of the kernel API Server.
- No architectural-layer deviation in Phase 3.

## Dependencies Declared

- `temporalio` (workflows + activities)
- `temporalio.contrib.opentelemetry` (TracingInterceptor)
- **`anthropic`** (LLM client imported directly in `_execute_reasoning`)
- `httpx` (for CLI-command-via-API within activity)
- `croniter` (for scheduled task cron checking)
- Temporal Cloud (production)
- MongoDB (message queue + log, ChangeRecord, entities)

## Code Locations Specified

Phase 2 code:
- `kernel/temporal/client.py` — Temporal client factory
- `kernel/temporal/worker.py` — Worker process, registers workflows + activities
- `kernel/temporal/workflows.py` — ProcessMessageWorkflow, HumanReviewWorkflow, BulkExecuteWorkflow
- `kernel/temporal/activities.py` — claim_message, load_entity_context, **process_with_associate**, complete_message, fail_message, process_bulk_batch, process_human_decision, preview_bulk_operation
- `kernel/message/dispatch.py` — optimistic_dispatch
- `kernel/queue_processor.py` — additions: dispatch_associate_workflows, check_scheduled_associates
- `kernel/api/direct_invoke.py` — direct invocation endpoint

Phase 3 code:
- `kernel/integration/adapter.py` — Adapter base class + error hierarchy
- `kernel/integration/registry.py` — ADAPTER_REGISTRY
- `kernel/integration/resolver.py` — resolve_integration
- `kernel/integration/credentials.py` — credential management
- `kernel/integration/dispatch.py` — adapter dispatch with auto-refresh
- `kernel/api/webhook.py` — webhook endpoint
- `kernel/integration/adapters/outlook.py` — Outlook email adapter
- `kernel/integration/adapters/stripe_adapter.py` — Stripe payment adapter

## Cross-References

- 2026-04-13-white-paper.md
- 2026-04-14-impl-spec-gaps.md
- 2026-04-14-impl-spec-phase-0-1-consolidated.md
- 2026-04-09-temporal-integration-architecture.md
- 2026-04-09-unified-queue-temporal-execution.md
- 2026-04-10-integration-as-primitive.md
- 2026-04-10-bulk-operations-pattern.md
- 2026-04-13-documentation-sweep.md

## Open Questions or Ambiguities

**The big one — Pass 2 Finding 0 source:**

The Phase 2-3 spec embeds agent execution in the kernel Temporal Worker. The design (2026-04-10-realtime-architecture-design.md) says agent execution should be in harness images outside the kernel. The spec does NOT explain why it deviates from the design. It also does not acknowledge the deviation.

**Why the deviation likely happened (my inference):**
1. Phase 5 (harness pattern, Real-Time) comes AFTER Phase 2 (Associate Execution) in the build sequence.
2. Phase 2 needs agent execution to work, but harnesses aren't available until Phase 5.
3. The spec solved this by placing agent execution inside the kernel's existing Temporal Worker — a kernel process that's already available in Phase 2.
4. **The spec should have either:**
   - Reordered phases (Phase 5 harness pattern before Phase 2 associate execution), OR
   - Explicitly created the async-deepagents harness image in Phase 2 as an additional deployable (leveraging the harness pattern ahead of the full real-time formalization), OR
   - At minimum, flagged this as a temporary placement with a migration plan to move agent execution to a harness image in Phase 5.

None of these happened. The spec placed agent execution in kernel/temporal/activities.py with no migration plan. The build implemented the spec faithfully. Pass 1 audit checked field-level correctness and missed the layer issue. Finding 0 emerged only when Craig asked "why isn't the assistant using the harness pattern?"

**Secondary observations:**
- **`_execute_reasoning` uses `anthropic` library directly.** Per the design, the kernel should be LLM-agnostic — the harness picks the framework. This embedding of `anthropic` in the kernel is a direct violation of the LLM-agnostic design principle.
- **Sandbox execution (Daytona per design layer 3)** is entirely absent. The agent runs inside the kernel Temporal activity with full DB access, not inside a sandbox.
- **Skill integrity check** (`verify_content_hash`) is correctly placed per design (line 409 of this spec) — it IS a kernel function, but is invoked inside the kernel-side agent execution. If agent execution moves to a harness, the integrity check should happen when skills are loaded by the harness from the kernel.
- **Scheduled associate execution** uses application-level cron in queue processor for MVP (Option A), not Temporal Schedules. Per design this is acceptable (both designs mentioned this path).
- **Direct invocation** endpoint exists. Per design this supports real-time channels (Phase 5) as well as testing.
- **Phase 3 (Integrations)** is consistent with design — no layer deviations.

**Pass 2 conclusion for this spec**: Phase 2 is where Finding 0 entered the spec. Phase 3 (Integrations) is clean.
