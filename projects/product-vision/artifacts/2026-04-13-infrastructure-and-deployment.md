---
ask: "How is the OS deployed — what services exist, where do they run, how do they communicate, how do they scale, and what are the production requirements?"
created: 2026-04-13
workstream: product-vision
session: 2026-04-13-b
sources:
  - type: conversation
    description: "Craig and Claude designing infrastructure and deployment — first of six gap sessions before spec writing"
  - type: research
    description: "Railway documentation research — networking, WebSocket limits, pricing, cron, health checks, secrets, regions, logging, connection limits"
  - type: artifact
    description: "2026-04-09-consolidated-architecture.md (the kernel architecture this infrastructure supports)"
  - type: artifact
    description: "2026-04-10-realtime-architecture-design.md (Runtime, harness pattern, real-time channels)"
  - type: artifact
    description: "2026-04-11-authentication-design.md (Session, auth middleware — runs in the API server)"
  - type: artifact
    description: "2026-04-13-session-6-checkpoint.md (established this as gap session #1)"
---

# Infrastructure and Deployment

## Context

First of six gap sessions identified in the session 6 checkpoint. The kernel architecture is complete (sessions 3-6, 50+ artifacts). What's missing: the deployment shape — what services exist, where they run, how they communicate, how they scale, and what production requires.

This artifact answers: if an engineer has the kernel specification, what does the DEPLOYMENT look like?

## Principles

- **Simplicity for MVP.** Minimal moving parts. Don't pre-build for scale.
- **The OS is a modular monolith.** One codebase, clear internal boundaries. One Docker image for the kernel with multiple entry points.
- **Railway for MVP.** Craig uses it for existing Indemn services. Familiar, simple, managed. Not pre-committing to ECS — Railway may be sufficient long-term.
- **The API is the universal gateway.** The CLI, base UI, harnesses, and Tier 3 developers all access the system through the API. No direct MongoDB access for anything except the kernel processes themselves.
- **Real-time from day one.** Voice and chat harnesses deploy alongside the kernel from the start.

## Service Architecture

### Five services, one kernel image

Three kernel processes share one Docker image (`indemn-kernel`) with different entry points. Two additional service types run from their own images.

#### The kernel image (`indemn-kernel`)

Contains the full kernel codebase: entity framework, API server, queue processor, Temporal worker, CLI, all dependencies. Built once, deployed as three containers with different entry points.

| Process | Entry point | Role | Internet-facing? | Connects to |
|---|---|---|---|---|
| **API Server** | `python -m indemn.api` | FastAPI — REST API, WebSocket for real-time UI updates, webhook endpoints, auth endpoints | **Yes** (public domain) | MongoDB Atlas (direct), AWS Secrets Manager, Temporal Cloud |
| **Queue Processor** | `python -m indemn.queue_processor` | Lightweight sweep: catches undispatched Temporal workflows, runs escalation sweeps, creates cron-triggered queue items | **No** (internal only) | MongoDB Atlas (direct), Temporal Cloud |
| **Temporal Worker** | `python -m indemn.temporal_worker` | Executes associate workflows (generic claim→process→complete) and kernel workflows (bulk ops, deployments, platform upgrades) | **No** (internal only) | MongoDB Atlas (direct), AWS Secrets Manager, Temporal Cloud |

#### The UI image (`indemn-ui`)

React static app served via lightweight static server (nginx or Railway's built-in static site hosting). Connects to the API server only — no direct database access. CDN-cacheable for scale.

#### Harness images (per Runtime kind+framework)

Separate Docker images, one per kind+framework combination. Deployed as separate Railway services.

| Image | Runtime kind | Framework | Transport |
|---|---|---|---|
| `indemn/runtime-voice-deepagents` | realtime_voice | deepagents | LiveKit Agents |
| `indemn/runtime-chat-deepagents` | realtime_chat | deepagents | WebSocket server |

Harnesses connect to the **API server via HTTP** (internal Railway network), not to MongoDB directly. They use the `indemn` CLI pre-installed in the image, operating in API mode for all entity operations.

Additional harness images added as new Runtime kind+framework combinations are needed. Each is a thin deployable (~60 lines of glue code per the realtime-architecture session) that bridges a specific agent framework + transport to the OS via the CLI.

## The Trust Boundary

A clean split between what has direct database access and what doesn't.

**Inside the trust boundary (direct MongoDB access):**
- API Server
- Queue Processor
- Temporal Worker

These three are the kernel. They share the same codebase, the same Docker image, and the same trust level. They all have MongoDB connection strings and AWS Secrets Manager access via Railway environment variables.

**Outside the trust boundary (API access only):**
- Base UI (connects to API via HTTP/WebSocket)
- Harnesses (connect to API via internal HTTP, use CLI in subprocess)
- CLI (remote users, FDEs, Tier 3 developers — connects to API via HTTP)
- Tier 3 applications (connect to API via HTTP)

Permissions are enforced by the auth middleware on every API request. The trust boundary means only three processes need MongoDB credentials. Everything else authenticates to the API with tokens (Session-based auth from the authentication design).

## CLI: Uniform API Mode

The CLI always operates as an HTTP client to the API server. No direct MongoDB mode. One behavior regardless of context.

- **Local development**: CLI connects to `http://localhost:8000` (local API server running via uvicorn)
- **Production**: CLI connects to `https://api.os.indemn.ai`
- **Harnesses**: CLI connects to `http://indemn-api.railway.internal:8000` (Railway private network)
- **Configuration**: `INDEMN_API_URL` environment variable. Set once per context.

This means the API server must be running for any CLI operation. For local dev, `uvicorn indemn.api:app --reload` runs alongside development. For production, the API server is always deployed. For bootstrap, the API server auto-detects an empty database on first start and provides bootstrap endpoints.

**Implications**:
- One authentication path for everything (API auth middleware)
- One permission enforcement path
- CLI, UI, harnesses, Tier 3 — all identical in how they access the system
- No "works locally but breaks in prod" from mode differences

## Dispatch Pattern: Optimistic + Sweep

When an entity saves and watches fire, the resulting messages are written to message_queue in the same MongoDB transaction. The question: how do Temporal workflows get started for associate-eligible messages?

**Not inside the MongoDB transaction.** Starting a Temporal workflow is an HTTP call to Temporal Cloud. Coupling it to the entity save transaction would make saves depend on Temporal availability.

**The pattern:**

1. **Optimistic dispatch**: after the MongoDB transaction commits, the API server fire-and-forgets a Temporal workflow start for each associate-eligible message. If Temporal is available (normal case), the associate starts processing within seconds.
2. **Sweep backstop**: the Queue Processor polls message_queue every few seconds for messages in `pending` status that haven't been claimed within a threshold. For any it finds, it dispatches a Temporal workflow. This catches the cases where the optimistic dispatch failed (Temporal blip, API server crashed between commit and dispatch, network issue).

Net effect: immediate dispatch in the happy path, automatic recovery in the failure path. Queue Processor is a lightweight sweep, not the primary dispatch mechanism.

The Queue Processor runs as a **persistent service with an internal polling loop**, not a Railway cron job. Railway's cron has 5-minute minimum granularity and timing variance — our sweep needs to run every few seconds.

## Railway Deployment

### Service configuration

| Service | Railway type | Public domain? | Replicas (MVP) | Replicas (10 customers) |
|---|---|---|---|---|
| `indemn-api` | Web service, port 8000 | **Yes** (`api.os.indemn.ai`) | 1 | 2 |
| `indemn-queue-processor` | Worker service | **No** | 1 | 1 |
| `indemn-temporal-worker` | Worker service | **No** | 1 | 2 |
| `indemn-ui` | Static site | **Yes** (`app.os.indemn.ai`) | 1 | 1 (CDN later) |
| `indemn-runtime-voice` | Web service | **Yes** (LiveKit needs public) | 0-1 | 1 |
| `indemn-runtime-chat` | Web service | **Yes** (WebSocket endpoint) | 0-1 | 1 |
| `indemn-runtime-async` | Worker service | **No** | 1 | 2 |

Internal services (Queue Processor, Temporal Worker) are never assigned public domains — Railway's private networking makes them accessible only via `service-name.railway.internal` within the same project.

### Private networking

All services in the same Railway project share a **WireGuard-encrypted private network**. Internal communication uses `service-name.railway.internal:PORT`. Cross-environment isolation: production and staging cannot communicate over private network.

The harnesses reach the API server at `http://indemn-api.railway.internal:8000`. The Queue Processor reaches Temporal at Temporal Cloud's public endpoint (authenticated via API key). The Temporal Worker connects to Temporal Cloud similarly.

### Shared variables

Railway shared variables (Project Settings → Shared Variables) define secrets once and share across services:

| Variable | Used by | Source |
|---|---|---|
| `MONGODB_URI` | API, Queue Processor, Temporal Worker | Atlas connection string |
| `AWS_ACCESS_KEY_ID` | API, Temporal Worker | IAM user for Secrets Manager + S3 |
| `AWS_SECRET_ACCESS_KEY` | API, Temporal Worker | IAM user |
| `AWS_REGION` | API, Temporal Worker | `us-east-1` |
| `TEMPORAL_ADDRESS` | API, Queue Processor, Temporal Worker | Temporal Cloud endpoint |
| `TEMPORAL_NAMESPACE` | API, Queue Processor, Temporal Worker | Temporal Cloud namespace |
| `TEMPORAL_API_KEY` | API, Queue Processor, Temporal Worker | Temporal Cloud API key |
| `JWT_SIGNING_KEY` | API | Platform-wide JWT signing key |
| `INDEMN_API_URL` | Harnesses | `http://indemn-api.railway.internal:8000` |
| `OTEL_EXPORTER_ENDPOINT` | All | Grafana Cloud OTLP endpoint |

Real secrets (per-org credentials, integration tokens) are fetched from AWS Secrets Manager at runtime by the kernel processes. Railway variables hold only the AWS credentials needed to access Secrets Manager.

### Regions

**US East for everything.** Railway, MongoDB Atlas, and Temporal Cloud all have strong US East presence. Co-located services get single-digit millisecond latency to each other and to the databases. Cross-region latency (60-80ms) would compound across every entity operation.

### SSL/TLS

Railway auto-provisions Let's Encrypt certificates for custom domains. Auto-renewed. HTTPS enforced (HTTP auto-upgrades). Zero configuration required.

## Production Requirements (from Railway review)

### 1. WebSocket keepalive — CRITICAL

Railway's proxy drops idle WebSocket connections after 60 seconds. Both the chat harness and the API server's real-time UI channel use WebSocket.

**Requirement**: all WebSocket handlers must send server-side ping frames every 30-45 seconds. The base UI WebSocket client and the chat harness client must handle pong responses. Without this, every conversation and every real-time UI connection dies silently after one minute of quiet.

Implementation: one-line configuration in the WebSocket server setup. Must be in every harness and the API server's WebSocket handler from day one.

### 2. External health monitoring — HIGH

Railway uses health checks during deployment (zero-downtime switchover) but does NOT monitor service health after deploy. If the Queue Processor or Temporal Worker crashes after going live, Railway won't restart it.

**Requirement**: external uptime monitoring from day one.

| Service | Monitor how |
|---|---|
| API Server | Grafana Cloud HTTP check on `https://api.os.indemn.ai/health` (public endpoint) |
| Queue Processor | Writes a heartbeat record to a `_health` collection in MongoDB every 30 seconds. Grafana queries it and alerts if stale > 2 minutes. |
| Temporal Worker | Same heartbeat pattern. Additionally, Temporal Cloud dashboard shows worker health natively. |
| Harnesses | HTTP health check on their public endpoints (if applicable) or heartbeat to MongoDB. |

### 3. MongoDB connection pool sizing — HIGH

Each MongoClient creates a connection pool. Default is 100 connections. Multiple services × multiple replicas can exhaust Atlas M10's 1,500 connection limit.

**Requirement**: explicit `maxPoolSize` in every service's MongoDB connection configuration.

| Service | maxPoolSize | Rationale |
|---|---|---|
| API Server | 50 per replica | Highest query volume, but async (Motor) — connections are shared across requests |
| Queue Processor | 10 | Low query volume (periodic sweeps) |
| Temporal Worker | 30 per replica | Moderate query volume (entity loads + saves per workflow activity) |
| Harnesses | 0 (no direct connection) | Use API, not MongoDB |

With 2 API replicas + 1 QP + 2 TW replicas: 100 + 10 + 60 = 170 connections. Well within M10 limits. Room to grow to 5-6 replicas before needing to revisit.

Also: Railway periodically cycles proxy instances, which drops connections. PyMongo's driver handles reconnection, but explicit connection health checks in the application startup ensure clean recovery.

### 4. Log management — HIGH

Railway log retention: 30 days on Pro plan. Rate limit: 500 lines/second/replica. Logs dropped beyond this.

**Requirement**: ship structured logs to Grafana Cloud via OTEL SDK. Railway's built-in logs serve as the quick debug console (recent, searchable). Grafana Cloud is the production audit trail (longer retention, alerting, correlation with traces).

Reduce log verbosity in production. Implement sampling for high-volume paths (entity saves, watch evaluations). Full verbosity in dev/staging.

### 5. Cloudflare in front of production API — MEDIUM

Railway has L3/L4 DDoS protection but no configurable application-layer WAF. For the production API domain:

**Requirement before first external customer**: Cloudflare (free tier minimum, Pro for WAF rules) in front of `api.os.indemn.ai`. Handles bot protection, DDoS absorption, rate limiting, and geo-blocking. Point Cloudflare's origin to Railway's public domain.

Not needed for dev/staging.

## Local Development

Craig (and future developers) run the OS locally for fast iteration.

```bash
# Terminal 1: API server with hot reload
INDEMN_API_URL=http://localhost:8000 \
MONGODB_URI=$ATLAS_DEV_URI \
uvicorn indemn.api:app --reload --port 8000

# Terminal 2: Queue processor (optional for dev — can trigger Temporal manually)
python -m indemn.queue_processor

# Terminal 3: Temporal dev server (local, no Temporal Cloud needed for dev)
temporal server start-dev --port 7233

# Terminal 4: Temporal worker
python -m indemn.temporal_worker

# Terminal 5: Base UI dev server
cd ui && npm run dev  # Vite, port 5173

# Terminal 6 (if testing voice/chat): harness
cd harnesses/voice-deepagents && python harness.py
```

MongoDB connects to Atlas dev cluster (already exists, separate from prod). No local MongoDB needed. Temporal dev server runs locally for free (no Cloud dependency during development).

The CLI works against the local API server:
```bash
export INDEMN_API_URL=http://localhost:8000
indemn entity list  # talks to local API
```

Entity type changes: modify the definition in the dev database, restart uvicorn (hot reload handles Python code changes; entity definition changes in DB need a manual restart or a `--watch-db` mode that could be built).

For parallel Claude Code sessions: git worktrees (Craig's existing OS session manager pattern). Each session works in its own worktree, merges to the main branch.

## Deployment Strategy

### Standard deploy (code changes)

1. Push to `main` → Railway auto-builds new Docker image → rolling deployment.
2. Railway starts new instance, runs health check (`/health` returns 200).
3. Old instance drains connections, new instance starts accepting.
4. Zero downtime.

### Entity type deploy (new entity types, modified definitions)

1. New entity definition written to MongoDB via CLI or API.
2. Trigger rolling restart: `railway redeploy --service indemn-api` (or automatic via CI).
3. New instances load new definitions from DB on startup (Beanie reinitialization).
4. CLI picks up new definitions automatically (ephemeral — each invocation queries the API).
5. Zero downtime (rolling restart means old instances serve during transition).

### Kernel upgrade (framework changes)

1. `indemn platform upgrade --dry-run` — previews configuration migrations.
2. `indemn platform upgrade` — applies migrations to entity definitions, capability schemas.
3. Push new kernel code → rolling deployment.
4. New instances run with updated kernel code + migrated configurations.
5. Capability schema versioning (from session 4) ensures stored configs are compatible.

## Scaling Strategy

Scaling is manual on Railway (set replica count). Triggers are monitored metrics.

| Service | Scale trigger | How |
|---|---|---|
| API Server | Response latency p95 > 500ms, or CPU > 70% | Add replicas (Railway: increase replica count) |
| Temporal Worker | Temporal task queue depth growing, or workflow completion latency increasing | Add replicas |
| Queue Processor | Message backlog growing (pending items increasing over time) | Unlikely bottleneck — single instance handles high throughput. If needed: leader election for HA. |
| Harnesses | Active session count approaching Runtime capacity | Add replicas per Runtime entity config |
| MongoDB | Connection count approaching limit, or query latency increasing | Upgrade Atlas tier (M10 → M30 → M60). Proactive: monitor via Atlas dashboard. |

For MVP: start with minimum replicas (1 each). Add replicas reactively as metrics indicate. Railway makes this a slider change.

## Cost Projections

| Scale | Atlas | Temporal | Railway compute | S3 | OTEL (Grafana) | Cloudflare | Total |
|---|---|---|---|---|---|---|---|
| **MVP** (dev + testing) | $60 (M10 × 2) | $100 | $30-50 (4-5 services) | $5 | $0 (free tier) | $0 | **~$200/month** |
| **First customer** (GIC) | $60 | $100 | $60-80 (+ replicas) | $10 | $0 | $0-20 | **~$250/month** |
| **5 customers** | $120 (M30 + M10) | $150 | $100-150 | $15 | $0 | $20 | **~$420/month** |
| **20 customers** | $300 (M30 × 2) | $300 | $200-300 | $30 | $50 | $20 | **~$920/month** |
| **50 customers** | $600 (M60 + M30) | $500 | $400-600 | $50 | $100 | $20 | **~$1,700/month** |

LLM cost (Anthropic Claude API for associate processing) is separate and per-customer. The `--auto` pattern keeps it proportional to edge-case complexity, not total volume. Estimate $1-10/day/org for typical workloads, less for orgs with well-tuned rules.

Egress cost on Railway: $0.05/GB. LLM API responses flow through Railway network. At moderate volume (1000 LLM calls/day × ~2KB response), egress is ~$0.10/month. Not material until very high scale.

## What's Decided

1. **Five services, one kernel image**: API Server, Queue Processor, Temporal Worker (all from `indemn-kernel` image), Base UI (`indemn-ui`), Harnesses (per Runtime kind+framework).
2. **Trust boundary**: kernel processes have direct MongoDB access. Everything else accesses the system via the API.
3. **CLI is always API mode**: uniform behavior, no direct MongoDB mode. `INDEMN_API_URL` configures the target.
4. **Optimistic dispatch + sweep**: API server dispatches Temporal workflows after entity save commits (fire-and-forget). Queue Processor sweeps for undispatched items as a reliability backstop.
5. **Railway for deployment**: US East region, co-located with Atlas and Temporal Cloud.
6. **Private networking**: internal services (Queue Processor, Temporal Worker) are not internet-facing. Railway WireGuard network for internal communication.
7. **Shared variables**: Railway shared variables for cross-service config (MongoDB URI, AWS creds, Temporal config, JWT key).
8. **WebSocket keepalive**: all WebSocket handlers send ping frames every 30-45 seconds (Railway proxy requirement).
9. **External health monitoring**: Grafana Cloud HTTP checks for API server. MongoDB heartbeat records for internal services.
10. **MongoDB connection pool sizing**: explicit `maxPoolSize` per service type (API: 50, QP: 10, TW: 30).
11. **Log shipping**: structured logs to Grafana Cloud via OTEL. Railway logs as quick debug console only.
12. **Cloudflare before first external customer**: WAF and DDoS protection for the production API domain.
13. **Zero-downtime deployment**: Railway rolling deploys. Entity type changes trigger rolling restart with Beanie reinitialization.
14. **Local dev**: uvicorn + temporal dev server + vite. Atlas dev cluster for MongoDB. CLI connects to local API.
15. **Scaling is manual on Railway**: replica count adjusted based on monitored metrics (latency, CPU, queue depth).

## What's Deferred

- **ECS migration**: Railway may be sufficient long-term. ECS is a potential future option, not a guaranteed migration target. The Docker images and service architecture are platform-agnostic — moving to ECS would change deployment config, not architecture.
- **Auto-scaling**: Railway doesn't support load-based auto-scaling. Manual replica management for now. If needed: move to a platform with auto-scaling, or build a simple auto-scaler that monitors metrics and adjusts Railway replica count via API.
- **Multi-region deployment**: single region (US East) for all services. Multi-region for latency or DR is a future concern when customer geography demands it.
- **Redis**: not in the stack. If needed later (for pub/sub fan-out, caching, rate-limit counters), it's additive. The architecture doesn't depend on it.
- **Service mesh / API gateway**: Railway's built-in networking is sufficient. No Envoy, Istio, or Kong needed.

## Relationship to Other Design Sessions

- **Real-time Implementation** (next session): will detail how harnesses actually connect to LiveKit, how WebSocket sessions are managed, how the voice pipeline flows. Depends on the deployment shape established here (harnesses as separate Railway services, API access via internal network, WebSocket keepalive requirement).
- **Development Workflow** (subsequent): will detail testing strategy, CI/CD pipeline specifics, parallel session conventions. Depends on the local dev setup and deployment strategy established here.
- **Dependencies & Resilience** (subsequent): will detail what happens when Atlas, Temporal, or the LLM provider goes down. The service architecture and dispatch pattern established here (optimistic + sweep, stateless workers) provide the resilience foundation.
- **Operations** (subsequent): will detail monitoring dashboards, debugging workflows, customer onboarding process. The health monitoring and logging strategy established here is the infrastructure foundation.
