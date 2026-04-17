# Notes: 2026-04-13-infrastructure-and-deployment.md

**File:** projects/product-vision/artifacts/2026-04-13-infrastructure-and-deployment.md
**Read:** 2026-04-16 (full file — 347 lines)
**Category:** design-source (gap session #1)

## Key Claims

- **Five services**:
  - Three from `indemn-kernel` image: **API Server** (public, port 8000), **Queue Processor** (internal), **Temporal Worker** (internal). All from ONE Docker image with different entry points.
  - `indemn-ui` image: React static app.
  - **Harness images**: `indemn/runtime-voice-deepagents` and `indemn/runtime-chat-deepagents`. Internal Railway services; connect to API via `indemn-api.railway.internal:8000` using `indemn` CLI.
- **Trust boundary (EXPLICITLY SPECIFIED)**:
  - **Inside** (direct MongoDB access): API Server, Queue Processor, Temporal Worker.
  - **Outside** (API access only): Base UI, Harnesses, CLI, Tier 3 applications.
- **CLI is ALWAYS API mode.** No direct MongoDB. `INDEMN_API_URL` configures target. "One behavior regardless of context."
- **Dispatch = optimistic + sweep**:
  - Entity save commits → API server fire-and-forgets Temporal workflow start.
  - Queue Processor polls every few seconds for pending messages that weren't claimed; dispatches for any found.
- **Queue Processor is persistent service with internal polling loop**, NOT a Railway cron job (cron is 5-min granularity).
- **Railway US East** for everything (Atlas + Temporal Cloud co-located).
- **Railway shared variables** hold cross-service config + AWS creds for Secrets Manager access.
- **WebSocket keepalive = MANDATORY** (Railway proxy drops idle connections at 60s). Ping every 30-45s.
- **External health monitoring**: Grafana Cloud HTTP check on API; MongoDB heartbeat records for QP + TW.
- **MongoDB connection pool sizing**: API 50/replica, QP 10, TW 30/replica.
- **Cloudflare before first external customer** (WAF + DDoS on production API domain).
- **Cost projections**: MVP ~$200/mo → first customer ~$250 → 5 customers ~$420 → 50 customers ~$1,700.

## Architectural Decisions

- **Modular monolith**: one codebase, multiple entry points, one Docker image for kernel. Clear internal boundaries.
- **Trust boundary is enforced by deployment** (only kernel processes have MongoDB credentials via Railway env vars).
- **CLI unification eliminates "works locally but breaks in prod" bugs**: no direct-DB mode anywhere.
- **Optimistic dispatch simplifies the happy path** (no Temporal in the save txn; just HTTP fire-and-forget after commit).
- **Sweep backstop handles failure cases** without coupling entity save to Temporal availability.
- **Real-time harnesses from day one** (not deferred).

## Layer/Location Specified

- **API Server (kernel/api/)** = kernel image, public-facing. Railway service `indemn-api`.
- **Queue Processor (kernel/queue_processor.py)** = kernel image, internal. Railway service `indemn-queue-processor`.
- **Temporal Worker (kernel/temporal/worker.py)** = kernel image, internal. Railway service `indemn-temporal-worker`.
- **Base UI** = separate image `indemn-ui`. Railway service.
- **`indemn-runtime-voice`** = harness image, public (LiveKit needs public). Railway service.
- **`indemn-runtime-chat`** = harness image, public (WebSocket endpoint). Railway service.
- **MongoDB Atlas** = US East; separate dev/prod clusters.
- **AWS Secrets Manager** = US East; fetched at runtime by kernel processes.
- **Temporal Cloud** = US East namespace.
- **Grafana Cloud** = OTEL backend + health monitoring.
- **Cloudflare** = in front of production API before first external customer.

**Finding 0 relevance — CRITICAL INFRASTRUCTURE-LEVEL DRIFT**:

- **This artifact's service table lists ONLY TWO harness images**: `indemn-runtime-voice` and `indemn-runtime-chat`.
- **The April 10 realtime-architecture-design artifact specifies THREE harness images** including `indemn/runtime-async-deepagents` (async + deepagents + Temporal worker).
- **In this artifact, the kernel's Temporal Worker is described as**: "Executes associate workflows (generic claim→process→complete) and kernel workflows (bulk ops, deployments, platform upgrades)."
- **This is the drift**: associate workflows (async) placed INSIDE the kernel Temporal Worker, not in a separate async-deepagents harness image. This contradicts the April 10 design.
- **This infrastructure artifact IS WHERE FINDING 0 LIKELY ENTERED THE SPEC** (one day before Phase 2-3 consolidated spec was written). The Phase 2-3 spec §2.4 took this infrastructure-level decision and implemented it: `process_with_associate` as kernel Temporal activity.

**Supersedence question**: does April 13 infrastructure supersede April 10 realtime-architecture-design on the worker-location question? **Per user's "later artifacts may override earlier uncertain decisions" rule, the later artifact would override the earlier — BUT:**
- The April 13 infrastructure artifact doesn't cite the April 10 harness-pattern design or explicitly say "we're walking this back."
- The April 13 white paper (same day) DOES re-affirm the harness pattern including all 3 images per Pass 2 notes.
- The April 13 simplification-pass explicitly LISTS the harness pattern as Layer 3 that survived simplification.
- This strongly suggests the April 13 infrastructure artifact has a DRAFTING OMISSION (async-deepagents harness not listed in the service table) rather than a deliberate reversal.

**The right interpretation for the vision map**:
- The authoritative design is: 3 harness images (voice, chat, async), all outside the kernel trust boundary.
- Kernel Temporal Worker SHOULD handle ONLY kernel workflows (bulk ops, deployments, platform upgrades, HumanReviewWorkflow, BulkExecuteWorkflow).
- Associate execution SHOULD NOT be in the kernel Temporal Worker. It belongs in `runtime-async-deepagents` harness image subscribing to a per-Runtime task queue.
- The infrastructure artifact's omission of async-deepagents is a source of the Finding 0 spec drift.

## Dependencies Declared

- Railway (deployment)
- MongoDB Atlas (M10 MVP)
- Temporal Cloud (Essentials $100/mo)
- AWS Secrets Manager
- AWS S3
- Grafana Cloud (OTEL + health checks)
- Cloudflare (pre-customer)
- LiveKit (voice transport, for harness)
- WebSocket (chat transport, for harness)

## Code Locations Specified

- `indemn-kernel` Docker image contains:
  - `kernel/api/` (API Server)
  - `kernel/queue_processor.py` (Queue Processor)
  - `kernel/temporal/worker.py` (Temporal Worker)
  - `kernel/` entity framework, auth, watch, rule, capability, message, integration, skill, etc.
  - CLI (pre-installed in image for harness usage)
- `indemn-ui` Docker image contains:
  - React static app (built via Vite)
- `indemn/runtime-voice-deepagents` image contains:
  - LiveKit Agents SDK
  - deepagents
  - Harness glue script
  - `indemn` CLI
- `indemn/runtime-chat-deepagents` image contains:
  - WebSocket server
  - deepagents
  - Harness glue script
  - `indemn` CLI
- **MISSING from this artifact**: `indemn/runtime-async-deepagents` image (per April 10 design, should contain: Temporal worker subscribing to a per-Runtime task queue, deepagents, harness glue, `indemn` CLI).

## Cross-References

- 2026-04-09-consolidated-architecture.md (the kernel architecture this supports)
- 2026-04-10-realtime-architecture-design.md (harness pattern; specifies 3 images including async)
- 2026-04-11-authentication-design.md (Session + auth middleware in API server)
- 2026-04-13-session-6-checkpoint.md (established this as gap session #1)
- 2026-04-13-white-paper.md (same day, reaffirms harness pattern)
- 2026-04-13-simplification-pass.md (same day, harness pattern survives simplification)
- Phase 0-1 consolidated spec (implements kernel image with API/QP/TW services)
- Phase 2-3 consolidated spec §2.4 (implements `process_with_associate` as kernel Temporal activity → Finding 0 code location)

## Open Questions or Ambiguities

Listed as "What's Deferred":
- ECS migration: Railway may be sufficient long-term.
- Auto-scaling: manual replica management for now.
- Multi-region deployment: single region (US East).
- Redis: not in stack; additive if needed.
- Service mesh / API gateway: Railway networking sufficient.

**The CRITICAL ambiguity this artifact introduces**:
- Is there a third harness image for async? The artifact implies "additional harness images added as new Runtime kind+framework combinations are needed" but doesn't list async-deepagents. The realtime-architecture-design explicitly requires it.
- **Pass 2 already confirmed Finding 0 at spec + code + infra levels. This infrastructure document is where the drift crept in at the infra-design level.**

**Supersedence note for vision map**:
- **5 services (or 6 with async-deepagents included)** — reconcile with realtime-architecture-design: authoritative is 6 services.
- **Trust boundary specification** — SURVIVES (exactly matches white paper).
- **CLI unification (always API mode)** — SURVIVES.
- **Optimistic + sweep dispatch** — SURVIVES. Implemented in Phase 2-3 spec.
- **Railway + US East + Atlas + Temporal Cloud** — SURVIVES.
- **WebSocket keepalive** — SURVIVES (requirement for harnesses + UI).
- **Cloudflare before external customers** — SURVIVES as operational requirement.
- **The async-deepagents harness must be present** per realtime-architecture-design; the omission here is an artifact drafting error, not a supersedence.

**Vision-map implication**: The final authoritative infrastructure design has 6 services, 4 images (`indemn-kernel`, `indemn-ui`, `indemn/runtime-voice-deepagents`, `indemn/runtime-chat-deepagents`, `indemn/runtime-async-deepagents`). Kernel Temporal Worker handles ONLY kernel workflows (Bulk, Deploy, HumanReview). Async associates run in the runtime-async image.
