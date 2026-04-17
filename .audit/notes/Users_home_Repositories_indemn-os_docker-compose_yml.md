# Notes: /Users/home/Repositories/indemn-os/docker-compose.yml

**File:** /Users/home/Repositories/indemn-os/docker-compose.yml
**Read:** 2026-04-16 (full file — 36 lines)
**Category:** infrastructure

## Key Claims

- Three services:
  - **`indemn-api`**: builds from Dockerfile, runs `uvicorn kernel.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload`. Exposes port 8000. Has env for MongoDB, AWS, JWT, Temporal, API URL.
  - **`indemn-queue-processor`**: builds from Dockerfile, runs `python -m kernel.queue_processor`. Depends on indemn-api.
  - **`temporal-dev`**: uses `temporalio/auto-setup:latest` image. Exposes 7233 (Temporal) and 8233 (Temporal UI).
- Volumes: `.:/app` for live reload during dev.
- Dev-only JWT key: `JWT_SIGNING_KEY=dev-signing-key-not-for-production`.

## Architectural Decisions

- Local dev uses three services: API, Queue Processor, Temporal dev.
- **The Temporal Worker is NOT in docker-compose.yml** — this is a notable absence.
- Volume mount enables hot reload.
- Remote infrastructure: MongoDB Atlas, AWS Secrets Manager (env vars expected).

## Layer/Location Specified

- Two kernel processes run in local dev: API Server, Queue Processor.
- Temporal dev server runs locally.
- **The Temporal Worker (`kernel/temporal/worker.py`) is missing from docker-compose.yml.**

**Pass 2 observation**: The docker-compose only starts 2 of 3 kernel processes. In production (Railway), all three kernel processes run per Phase 0-1 spec §0.9. For local dev, the Temporal Worker isn't started by default — likely intentional (the developer starts it manually when testing associate execution).

**Finding 0 at infrastructure layer**: Confirmed — no harness services in docker-compose.yml either. The design requires harness images running alongside the kernel processes. The local dev setup doesn't include:
- `indemn-temporal-worker` (the kernel worker — currently absent)
- Harness services (voice-deepagents, chat-deepagents, async-deepagents — don't exist)

## Dependencies Declared

- Docker / docker-compose
- `python:3.12-slim` base (from Dockerfile)
- `temporalio/auto-setup:latest` for local Temporal server
- MongoDB Atlas (remote, via env)
- AWS Secrets Manager (remote, via env)

## Code Locations Specified

- Services share the same image (`build: .` which uses the Dockerfile).
- No harness services = no harness images.

## Cross-References

- Phase 0-1 spec §0.4 docker-compose.yml (expected configuration)
- `Dockerfile` — image definition
- `kernel/api/app.py` — API entry point
- `kernel/queue_processor.py` — queue processor entry point
- `kernel/temporal/worker.py` — Temporal worker entry point (NOT in compose)

## Open Questions or Ambiguities

**Pass 2 findings:**

1. **Temporal Worker missing from local dev.** Developers testing associate execution need to manually run `python -m kernel.temporal.worker`. Could be added to docker-compose for convenience.

2. **No harness services.** Per Finding 0, harnesses should exist as separate services. Once harnesses are built, they should be added to docker-compose.yml for local dev:
   ```yaml
   indemn-async-deepagents:
     build: ./harnesses/async-deepagents
     environment:
       - INDEMN_API_URL=http://indemn-api:8000
       - INDEMN_SERVICE_TOKEN=...
       - RUNTIME_ID=...
   ```
   Similarly for chat and voice harnesses.

**Secondary observations:**
- `JWT_SIGNING_KEY=dev-signing-key-not-for-production` is correct for local dev.
- No health checks defined — relies on `depends_on` for startup order (not for readiness).
- `--reload` flag on uvicorn enables hot reload during development.
- No volume for UI (dev server runs separately).
- Atlas dev cluster referenced by env var — no local MongoDB container.

docker-compose matches the Phase 0-1 spec. The gaps (no Temporal Worker service, no harness services) reflect the broader Finding 0 architectural incompleteness, not a local dev config bug per se.
