# Notes: 2026-04-09-temporal-integration-architecture.md

**File:** projects/product-vision/artifacts/2026-04-09-temporal-integration-architecture.md
**Read:** 2026-04-16 (full file — 232 lines)
**Category:** design-source

## Key Claims

- **Temporal replaces** hand-rolled durable-execution primitives: message_queue polling, `findOneAndUpdate` claiming, visibility timeouts, DLQ + retry, crash recovery, multi-entity atomicity, cron, correlation tracking.
- **What stays**: entity framework (Beanie/Pydantic/Mongo), entity CLI/API (FastAPI/Typer), kernel capabilities (`--auto`), skills (markdown), roles+watches, OTEL.
- **Outbox pattern for entity → Temporal bridge**: Entity save + outbox insert in the SAME MongoDB transaction. Outbox poller reads records, evaluates watches, signals Temporal. At-least-once delivery.
- **Per-actor workflow model (question left open)**: "One workflow per actor vs. one workflow per pipeline — per-actor preserves the 'system churning' model." Per-actor was the leaning direction.
- **Human-in-the-loop via Temporal signals**: Workflow waits for signal; human queue = Temporal query; signal arrives → workflow resumes.
- **Scheduled tasks via Temporal Schedules** (later refined — MVP uses application cron, post-MVP migrates to Temporal Schedules per Phase 2-3 spec).
- **Unified observability via OTEL** — Temporal's TracingInterceptor creates spans that join with entity/LLM spans into one trace.
- **Temporal Cloud cost**: $100/month Essentials (1M actions included). Cost scales proportionally with scale.

## Architectural Decisions

- **Multi-entity atomicity via saga pattern**: workflow wraps multiple activities; if worker crashes, Temporal replays and skips completed activities. "No orphaned state."
- **Workflow versioning** handled by Temporal's built-in mechanism — in-flight workflows continue on old workers; new workflows route to new workers.
- **Rules are configuration data** — next workflow execution picks up new rules; in-flight workflows continue with evaluated results stored in Temporal event history.
- **Workflows per Temporal queue** — not explicitly specified here; left implicit.
- **CLI for Temporal ops**: `indemn schedule create --workflow ... --cron ...`

## Layer/Location Specified

- **Outbox poller = regular Python process** (explicitly noted as "not in Temporal"). Kernel code, lives alongside other kernel runtime processes.
- **Watch evaluation = outbox poller** (in this artifact). Simple + cached + fast.
- **Temporal activities = where actor work runs**. This artifact DOES NOT place the LLM / skill interpreter anywhere specifically — says "Activity: LLM call with skill" as if the LLM call itself IS an activity run by the Temporal worker. This is the PROTO-design of Finding 0 at the architecture level (not yet decided either way).
- **"Temporal workers"** are mentioned but deployment location is NOT specified. Could be kernel-side; could be external (the harness pattern formalizes external one day later).
- **No trust-boundary discussion** in this artifact.

**Relevance to Finding 0**: This artifact is **pre-harness-pattern**. It treats activities as "things a Temporal worker runs" without naming whether workers are kernel images or separate images. One day later (2026-04-10-realtime-architecture-design.md), the harness pattern makes workers external. The Phase 2-3 spec chose the pre-harness interpretation and kept it inside the kernel — that's Finding 0.

**This artifact is PARTIALLY SUPERSEDED**:
- Outbox pattern → evolves to **optimistic dispatch + sweep backstop** per Phase 2-3 spec (simpler, same guarantees).
- Temporal worker location → formalized as "harness image outside kernel" per 2026-04-10-realtime-architecture-design.md.
- Everything else survives.

## Dependencies Declared

- Temporal Cloud (Essentials tier)
- Temporal Python SDK
- Temporal OTEL TracingInterceptor
- MongoDB (entity storage + outbox + message_queue + message_log)
- OTEL backend
- Beanie, Pydantic, FastAPI, Typer (carryover)

## Code Locations Specified

- No absolute paths at this stage. Concept-level.
- Mentioned: `EmailSyncWorkflow`, `ExtractPDFsWorkflow`, `ClassifyEmailWorkflow`, `LinkEmailWorkflow`, `AssessSubmissionWorkflow`, `HumanReviewWorkflow`, `StaleCheckWorkflow`, `WeeklySummaryWorkflow` — example workflows.

## Cross-References

- 2026-04-09-unified-queue-temporal-execution.md (IMMEDIATELY SUPERSEDES this artifact on queue mechanism: queue is ALWAYS MongoDB; Temporal is execution engine, not queue backend)
- 2026-04-10-realtime-architecture-design.md (IMMEDIATELY SUPERSEDES this on worker location: async Temporal worker = harness image, not kernel module)
- Phase 2-3 consolidated spec §2.4 — implemented something between these three (Temporal in kernel, single `indemn-kernel` task queue, no harness) → Finding 0

## Open Questions or Ambiguities

Listed in the artifact itself:
1. One workflow per actor vs per pipeline — **resolved later as per-message workflow** (ProcessMessageWorkflow generic).
2. Human queue as Temporal query — practical at scale? **Resolved**: queue stays in MongoDB (unified-queue design supersedes).
3. Outbox poller vs. MongoDB Change Streams — **resolved in favor of optimistic dispatch + sweep** per Phase 2-3 spec.
4. Simple operations — is Temporal overhead justified? **Resolved**: yes for durability; MVP scheduled tasks use app-level cron.
5. Temporal as single point of failure — **accepted risk**; entity saves + human actors continue if Temporal down.

**Supersedence note for vision map**:
- "Temporal replaces hand-rolled durable execution" — SURVIVES.
- "Outbox for entity → Temporal bridge" — REPLACED by optimistic dispatch + sweep.
- "Workers are kernel processes" — SUPERSEDED; workers are harness images one day later.
- "Scheduled tasks via Temporal Schedules" — deferred post-MVP; Phase 2 spec uses app-cron.
