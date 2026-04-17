# Notes: /Users/home/Repositories/indemn-os/Dockerfile

**File:** /Users/home/Repositories/indemn-os/Dockerfile
**Read:** 2026-04-16 (full file — 18 lines)
**Category:** infrastructure

## Key Claims

- Base image: `python:3.12-slim`.
- Installs `uv` (Python package manager).
- Copies `pyproject.toml` and `uv.lock`, runs `uv sync --frozen --no-dev`.
- Copies application code: `kernel/`, `kernel_entities/`, `seed/`.
- Default CMD: `uv run python -m kernel.api.app` — overridable per Railway service.

## Architectural Decisions

- **Single image for all kernel processes.** Different Railway services override CMD to run:
  - API Server: `python -m kernel.api.app`
  - Queue Processor: `python -m kernel.queue_processor`
  - Temporal Worker: `python -m kernel.temporal.worker`
- Matches Phase 0-1 spec §0.3 Dockerfile and §0.9 Deployment.
- No `harnesses/` directory copied — Dockerfile doesn't include harness code.

## Layer/Location Specified

- **This is the KERNEL image** per white paper § Service Architecture: "Three kernel processes share one image with different entry points."
- The image contains `kernel/`, `kernel_entities/`, `seed/`. No harness code.
- Per design: Harness images are SEPARATE — `indemn/runtime-voice-deepagents:1.2.0`, `indemn/runtime-chat-deepagents:1.2.0`, `indemn/runtime-async-deepagents:1.2.0`.

**Current state matches the design for the kernel image.** The design requires additional harness Dockerfiles — currently NONE EXIST:
- No `harnesses/voice-deepagents/Dockerfile`
- No `harnesses/chat-deepagents/Dockerfile`
- No `harnesses/async-deepagents/Dockerfile`

**Pass 2 finding for Finding 0:**
- **No harness Dockerfiles in the repo.** Confirmed by `find /Users/home/Repositories/indemn-os -type d -name "harness*"` earlier — returns empty.
- Per the Phase 4-5 spec, the voice harness example at `harnesses/voice-deepagents/main.py` was spec'd but not implemented as a deployable artifact (confirmed by comprehensive audit).

## Dependencies Declared

- Python 3.12
- uv (from `ghcr.io/astral-sh/uv:latest`)
- pyproject.toml dependencies (Beanie, FastAPI, Temporalio, **anthropic**, etc.)

## Code Locations Specified

- Kernel code copied into `/app/kernel/`
- Kernel entities copied into `/app/kernel_entities/`
- Seed data copied into `/app/seed/`
- No harness code copied (no `harnesses/` in repo)

## Cross-References

- Phase 0-1 spec §0.3 Dockerfile
- Phase 0-1 spec §0.9 Deployment (Railway services)
- White paper § Service Architecture
- Design: 2026-04-10-realtime-architecture-design.md Part 4 (three harness images specified)

## Open Questions or Ambiguities

**Finding 0 confirmation at the infrastructure layer:**
- **The kernel image is correctly built**, but:
- **No harness images exist.** Per design, there should be three additional images: `indemn/runtime-voice-deepagents`, `indemn/runtime-chat-deepagents`, `indemn/runtime-async-deepagents`. None are present in the repo.
- Because no harness images exist, Finding 0's structural gap is present at every layer — design (harness pattern), code (in-kernel agent execution), and infrastructure (no harness Docker images).

**Fix direction:**
- Create `harnesses/async-deepagents/Dockerfile` + Python harness script.
- Create `harnesses/chat-deepagents/Dockerfile` + Python harness script.
- Create `harnesses/voice-deepagents/Dockerfile` + Python harness script (spec'd but not implemented).
- Each harness image includes: harness script, `indemn` CLI pre-installed, framework (deepagents), transport (LiveKit/WebSocket/Temporal).
- Configure Railway services for each harness image with appropriate environment variables (RUNTIME_ID, INDEMN_SERVICE_TOKEN, INDEMN_API_URL).

**Secondary observations:**
- Single-image multi-entry-point is fine for the kernel (3 kernel processes share code).
- No health check in Dockerfile — Railway likely provides health checks via HTTP endpoints configured elsewhere.
- `--no-dev` correctly excludes dev dependencies.
- uv.lock frozen sync ensures reproducible builds.

Dockerfile is correctly configured for the kernel, but missing the harness counterparts required by the design.
