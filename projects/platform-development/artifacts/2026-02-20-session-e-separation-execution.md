---
ask: "Execute the backend/frontend separation — epic p0l"
created: 2026-02-20
workstream: platform-development
session: 2026-02-20-e
sources:
  - type: github
    description: "indemn-ai/percy-service — scaffolded, pushed, CI running"
  - type: github
    description: "indemn-ai/copilot-dashboard-react — stripped backend, updated Dockerfile/nginx/compose"
  - type: local
    description: "EC2 dev deployment — both containers running on shared-datadog network"
---

# Session E: Backend/Frontend Separation Execution

## What Happened

Executed the full backend/frontend separation designed in session D. All 15 tasks in epic `p0l` completed across 3 phases.

### Phase 1 — Stand up percy-service (p0l.1-6)
- Cloned empty `indemn-ai/percy-service` repo
- Scaffolded with backend code from `copilot-dashboard-react`: `indemn_platform/`, `tests/`, `scripts/`, `skills/evaluations/`, `tasks/`, `pyproject.toml`, `uv.lock`
- Added `python-dotenv>=1.0` as explicit dependency, verified `deepagents>=0.2` present
- Created two-stage Dockerfile (python:3.12-slim builder + runtime, `--workers 1`, non-root appuser)
- Created docker-compose.yml (GHCR image, port 8003:8000, shared-datadog network)
- Created CI/CD workflows: `build.yml` (dev/main) and `build-prod.yml` (prod branch)
- Pushed to GitHub — CI build triggered and passed
- Deployed to dev EC2 on port 8013 (8003 occupied by old combined container)
- Health check confirmed: `curl localhost:8013/api/v1/health` → `status: ok`

### Phase 2 — Flip the frontend (p0l.7-11)
- Created `feat/frontend-only` branch on `copilot-dashboard-react`
- Stripped all backend code: `indemn_platform/`, `tests/`, `pyproject.toml`, `uv.lock`, `supervisord.conf`, `test_env`, seed scripts, `skills/evaluations/`, `tasks/`
- Simplified Dockerfile: removed Python build stage, switched to `nginx:alpine`, CMD from supervisord to nginx
- Updated nginx.conf: removed `upstream backend` block, added Docker DNS resolver (`127.0.0.11`), variable-based proxy to `percy-service:8000` for `/api/` and `/ws`
- Updated docker-compose.yml: GHCR image, removed env_file, healthcheck on `/` instead of `/api/v1/health`
- Merged to main and pushed to org repo
- Deployed to dev EC2

### Build Issues Fixed
1. **`/var/lib/nginx` missing** — `nginx:alpine` doesn't create it. Fix: `mkdir -p` before `chown`
2. **`/var/cache/nginx` permission denied** — nginx needs cache dir for request buffering. Fix: add to `mkdir -p` and `chown`
3. **Container not on shared network** — old container reused instead of recreated. Fix: `docker compose up -d --force-recreate`
4. **EC2 docker-compose.yml stale** — had old healthcheck hitting `/api/v1/health`. Fix: updated to `/`

### Phase 3 — Cleanup (p0l.12-15)
- **WebSocket URL (p0l.13)**: No changes needed. Production `wss://platform.indemn.ai/ws` routes through frontend nginx → percy-service. Local dev `ws://localhost:8003/ws` correct via Docker port mapping.
- **CLAUDE.md files (p0l.14)**: Created percy-service CLAUDE.md from scratch. Updated frontend CLAUDE.md with 12+ edits removing backend references.
- **Cleanup (p0l.15)**: Removed `AGENTS.md`, `.planning/` from frontend repo. `test_env` already gone.
- **Runners (p0l.12)**: Set up percy-service dev runner on EC2 (`~/actions-runner-percy-service`). Prod runners documented for later setup.

## Production Deployment Steps (Remaining)

1. Set up prod runners on prod EC2 for both repos (labels: `self-hosted,linux,x64,prod`)
2. Set up dev runner for copilot-dashboard-react on dev EC2
3. Create `/opt/percy-service` on prod EC2 with `.env` and `docker-compose.yml`
4. Update `/opt/copilot-dashboard-react` on prod EC2 with new compose and Dockerfile
5. Push to `prod` branch on both repos to trigger prod CI/CD
6. Verify production: `platform.indemn.ai` end-to-end

## Key Commits

| Repo | Commit | Description |
|------|--------|-------------|
| percy-service | `f00305b` | Initial scaffold with backend code |
| percy-service | `d838b30` | CLAUDE.md for backend context |
| copilot-dashboard-react | `2e28cca` | Frontend-only separation |
| copilot-dashboard-react | `13c0341` | Fix: mkdir /var/lib/nginx |
| copilot-dashboard-react | `e058181` | Fix: /var/cache/nginx permissions |
| copilot-dashboard-react | `a1ce5bc` | Cleanup + CLAUDE.md update |

## Architecture After Separation

```
devplatform.indemn.ai (ALB)
  → copilot-dashboard-react container (nginx:alpine, port 8006:8080)
      ├── /           → static files (React UI)
      ├── /api/       → proxy to percy-service:8000 (Docker DNS)
      ├── /ws         → proxy to percy-service:8000 (WebSocket)
      └── /eval-api/  → proxy to evaluations:8080

percy-service container (python:3.12-slim, port 8013:8000)
  └── uvicorn --workers 1
      └── FastAPI (indemn_platform.api.main:app)

Both on shared-datadog Docker network.
```
