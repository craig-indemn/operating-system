---
ask: "Separate the Python backend from the React frontend in copilot-dashboard-react into a new percy-service repo"
created: 2026-02-19
workstream: platform-development
session: 2026-02-19-d
sources:
  - type: github
    description: "indemn-ai/percy-service repo (empty, created 2026-02-19)"
  - type: github
    description: "indemn-ai/copilot-dashboard-react repo structure, Dockerfile, CI/CD workflows"
  - type: local
    description: "Project artifacts from sessions a-c covering architecture, deployment, and federation"
---

# Design: Backend/Frontend Separation — percy-service

## Problem

`copilot-dashboard-react` is a monorepo containing both the Python FastAPI backend (`indemn_platform/`) and the React frontend (`ui/`). They're deployed as a single Docker container with nginx + uvicorn + supervisord.

The team wants to:
- Add more React components to the frontend repo for the copilot dashboard
- Deploy backend and frontend independently
- Follow the existing convention of one service = one repo = one container

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend repo | `copilot-dashboard-react` | Keeps React UI, federation, docs. Grows as the React component library for the dashboard. |
| Backend repo | `percy-service` | Gets the entire Python backend. Clean, self-contained service. |
| Jarvis → Percy rename | Repo name only | Code stays "Jarvis" internally. Full rename is a separate task — bundling it doubles risk for no architectural benefit. |
| Containers | Two separate containers, two docker-compose files | Matches team convention. Each repo is self-contained. |
| Routing | Frontend nginx proxies `/api/` + `/ws` to percy-service | Same URL structure as today. Zero changes to Angular config or React code. Invisible to users. |
| Network | Existing shared Docker network on EC2 | Both compose files reference it as external. Docker DNS resolves service names. |
| Git history | Clean break | Fresh repo for percy-service. History lives in copilot-dashboard-react forever. Avoids git filter-branch complexity. |
| CI/CD | Two independent workflows, new GitHub runners | Each repo builds and deploys its own container. Independent deploy cycles. |
| Migration order | Deploy backend first → verify → flip frontend → verify | Rollback is trivial: redeploy the last known good combined image. |

## What Moves Where

### percy-service (new repo)

```
percy-service/
├── indemn_platform/           # Entire Python backend
│   ├── api/                   # FastAPI route handlers (includes main.py entry point)
│   ├── models/                # Pydantic schemas
│   ├── repositories/          # MongoDB data access
│   ├── graph_factory/         # Config → LangGraph compilation
│   ├── components/            # LangGraph node implementations
│   ├── connectors/            # External integrations + eval connector
│   ├── simulation/            # Evaluation harness
│   ├── jarvis/                # Jarvis AI builder (rename deferred)
│   └── scoring.py             # Score computation
├── tests/                     # Full test suite (api/, e2e/, integration/, unit/, fixtures/, scenarios/)
├── tasks/                     # Jarvis task documentation (jarvis_baseline_execution.md)
├── scripts/
│   ├── seed_components.py     # Seed component definitions to MongoDB
│   └── seed_jarvis_templates.py  # Seed Jarvis templates + eval prompts
├── skills/
│   └── evaluations/           # Jarvis workflow skills
├── pyproject.toml             # Python dependencies (uv)
├── uv.lock
├── .dockerignore              # Exclude tests/, docs/, .venv/, *.md
├── Dockerfile                 # Python-only: uvicorn, no nginx
├── docker-compose.yml         # Shared external network
└── .github/workflows/
    ├── build.yml              # Dev: build + deploy on push to main
    └── build-prod.yml         # Prod: build + deploy on push to prod branch
```

**Note:** The FastAPI entry point is `indemn_platform/api/main.py` (not `indemn_platform/main.py`). The uvicorn command must reference `indemn_platform.api.main:app`.

### copilot-dashboard-react (keeps)

```
copilot-dashboard-react/
├── ui/                        # All React code
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── components/        # UI components (evaluation, chat, builder, report, graph)
│   │   ├── federation/        # Module Federation exports (5 components)
│   │   ├── api/hooks/         # React Query hooks
│   │   └── lib/               # Utilities (scoring.ts, PDF generation)
│   ├── scripts/
│   │   └── build-federation.js  # Three-phase federation build
│   ├── vite.config.ts         # Dev server config
│   └── vite.federation.config.ts  # Federation build config
├── skills/
│   └── react-angular-federation/  # Federation integration docs
├── nginx.conf                 # Updated: proxy to percy-service:8000 (at repo root, not nginx/)
├── docs/plans/                # 90+ historical design docs (stay here)
├── package.json               # npm dependencies (UI)
├── Dockerfile                 # Simplified: Node build + nginx only, CMD: nginx -g 'daemon off;'
├── docker-compose.yml         # Shared external network
└── .github/workflows/
    ├── build.yml              # Dev: build + deploy on push to main
    └── build-prod.yml         # Prod: build + deploy on push to prod branch
```

**Note:** `dashboard-config.json` is NOT in this repo — it lives in the Angular `copilot-dashboard` repo. The `CLAUDE.md` and `.claude/` directory need to be updated for both repos to reflect the new structure.

## Container Architecture

### percy-service container

```
percy-service container
  Port mapping: 8003:8000
  └── uvicorn --workers 1 (port 8000)
      └── FastAPI app (indemn_platform.api.main:app)

  Healthcheck: curl -f http://localhost:8000/api/v1/health || exit 1

  Environment (directly referenced in code):
    MONGO_URL, MONGO_DB_NAME                          # Primary DB (indemn_platform)
    V1_MONGODB_URI, V1_MONGODB_DB                     # V1 tiledesk DB (read-only, for V1 agent configs)
    OPENAI_API_KEY                                    # Used in kb_retrieval.py
    ANTHROPIC_API_KEY                                 # Implicit: read by langchain-anthropic (ChatAnthropic)
    EVALUATION_SERVICE_URL=http://evaluations:8080    # Eval connector (defaults to localhost:8002 in code)
    PINECONE_API_KEY                                  # KB retrieval (index name hardcoded as "indemn")
    COHERE_API_KEY                                    # Cohere reranking
    AUTH_ENABLED, JWT_SECRET                          # JWT auth enforcement
    CO_PILOT_URL                                      # Human handoff connector

  Environment (implicit, read by libraries):
    LANGSMITH_API_KEY, LANGSMITH_PROJECT_NAME         # LangSmith tracing (read by langchain)
    LANGCHAIN_TRACING_V2                              # Enable/disable tracing
```

No nginx, no supervisord. Just uvicorn serving the API and WebSocket.

**Critical: `--workers 1` is required.** The backend uses in-memory state: `MemorySaver` for checkpointing, plus persistent asyncio background tasks (`simulation_job_runner()` and `jarvis_job_runner()`) started at boot. Multiple workers would duplicate these background tasks and break shared state. The current config runs `--workers 2` which is a latent bug; percy-service should fix this.

**Note:** `PLATFORM_URL`, `BOT_SERVICE_URL`, `REDIS_URL`, `PINECONE_ENVIRONMENT`, and `PINECONE_INDEX_NAME` from the old `.env` are NOT referenced in the Python code and can be dropped.

### copilot-dashboard-react container

```
copilot-dashboard-react container
  Port mapping: 8006:8080
  └── nginx (port 8080)
      ├── /            → static files (dist-federation/)
      ├── /api/        → proxy to percy-service:8000
      ├── /ws           → proxy to percy-service:8000 (WebSocket upgrade)
      └── /eval-api/   → proxy to evaluations:8080

  Healthcheck: curl -f http://localhost:8080/ || exit 1
  CMD: nginx -g 'daemon off;'
  Build arg: VITE_FEDERATION_BASE_URL
```

No Python, no uvicorn, no supervisord. Just nginx serving static files and proxying API requests. Must preserve non-root user setup (`appuser`) and nginx permission directories from the current Dockerfile.

**Healthcheck change:** The current combined container checks `/api/v1/health` (which hits the backend). After separation, the frontend healthcheck is changed to `/` (nginx serving static files). This means the frontend container will report "healthy" even if the backend is down. This is intentional — the frontend's job is to serve files and proxy, not to guarantee backend availability. Backend health is monitored via percy-service's own healthcheck. Operators should monitor both containers independently.

### nginx.conf changes

The critical change — use Docker DNS resolver and variable-based proxy to handle startup ordering:

```nginx
resolver 127.0.0.11 valid=30s;  # Docker internal DNS (matches existing eval-api pattern)

location /api/ {
    set $percy percy-service;
    proxy_pass http://$percy:8000;
    # ... existing proxy headers unchanged
}

location /ws {
    set $percy percy-service;
    proxy_pass http://$percy:8000;
    # ... existing WebSocket headers unchanged
}
```

**Note:** The proxy location is `/api/` (not `/api/v1`). The backend exposes both `/api/v1/...` routes and a bare `/health` endpoint. Using the broader `/api/` location matches the current nginx config.

Using a variable forces nginx to re-resolve DNS on each request, preventing cached failures if percy-service starts after the frontend container.

**What to change in nginx.conf:**
- Remove `upstream backend { server 127.0.0.1:8000; }` block
- Add `resolver 127.0.0.11 valid=30s;` inside the `server` block
- Update `/api/` and `/ws` locations to use variable-based proxy to `percy-service:8000`

**What to preserve exactly as-is:**
- `pid /tmp/nginx.pid;` (required for non-root user)
- `proxy_read_timeout 120s` for API, `proxy_read_timeout 3600s` + `proxy_send_timeout 3600s` for WebSocket
- All proxy headers (`Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`)
- WebSocket upgrade headers (`Upgrade`, `Connection "upgrade"`, `proxy_http_version 1.1`)
- `Access-Control-Allow-Origin *` headers on static file locations (needed for federation)
- `gzip` configuration, `sendfile`, `tcp_nopush`, `keepalive_timeout` settings
- The `/eval-api/` proxy block (already uses variable-based proxy — no changes needed)

### Docker Compose files

Both compose files use pre-built GHCR images (not local builds), matching the existing convention. The `IMAGE_TAG` variable allows pinning to specific builds.

**percy-service/docker-compose.yml:**
```yaml
services:
  percy-service:
    image: ghcr.io/indemn-ai/percy-service:${IMAGE_TAG:-main}
    container_name: percy-service
    ports:
      - "8003:8000"
    env_file: .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      start_period: 15s
      retries: 3
    networks:
      - shared-datadog

networks:
  shared-datadog:
    external: true
```

**copilot-dashboard-react/docker-compose.yml:**
```yaml
services:
  app:
    image: ghcr.io/indemn-ai/copilot-dashboard-react:${IMAGE_TAG:-main}
    container_name: copilot-dashboard-react
    ports:
      - "8006:8080"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/"]
      interval: 30s
      timeout: 10s
      start_period: 10s
      retries: 3
    networks:
      - shared-datadog

networks:
  shared-datadog:
    external: true
```

## CI/CD Workflows

### percy-service workflows

Both repos need **two** workflows: dev (triggers on `main`) and prod (triggers on `prod` branch). Workflows follow the existing pattern: separate build job (on `ubuntu-latest` with GitHub Actions for Docker) and deploy job (on self-hosted runner directly on EC2).

**percy-service/.github/workflows/build.yml (dev):**
```yaml
name: Build and Deploy (Dev)
on:
  push:
    branches: [main]
  workflow_dispatch:          # Enable manual re-runs from GitHub UI

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ghcr.io/indemn-ai/percy-service:main
            ghcr.io/indemn-ai/percy-service:main-${{ github.run_number }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: [self-hosted, linux, x64, dev]
    permissions:
      contents: read
      packages: read
    steps:
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Deploy
        run: |
          cd /opt/percy-service
          sudo docker compose pull percy-service
          sudo docker compose up -d --no-deps percy-service
```

**percy-service/.github/workflows/build-prod.yml (prod):**
- Same structure but triggers on `prod` branch, plus `workflow_dispatch`
- Tags image as `latest` and `${github.run_number}` (not `main` and `main-${run_number}`)
- Deploys on runner: `[self-hosted, linux, x64, prod]`
- Same `permissions` blocks and GHCR login step in deploy job

### copilot-dashboard-react workflows (updated)

Same structure as today but:
- Dockerfile no longer has a Python build stage
- Build arg `VITE_FEDERATION_BASE_URL` still required
- Deploy target unchanged (`/opt/copilot-dashboard-react`)
- Both `build.yml` (dev) and `build-prod.yml` (prod) updated to match simplified build

## Migration Strategy

### Phase 1 — Stand up percy-service (zero risk)

The old combined container keeps running. percy-service starts alongside it.

1. Clone percy-service repo locally
2. Copy backend code from copilot-dashboard-react:
   - `indemn_platform/` → `percy-service/indemn_platform/`
   - `tests/` → `percy-service/tests/` (includes `conftest.py` files in subdirs)
   - `pyproject.toml`, `uv.lock` → `percy-service/`
   - `scripts/seed_components.py`, `scripts/seed_jarvis_templates.py` → `percy-service/scripts/`
   - `skills/evaluations/` → `percy-service/skills/evaluations/`
   - `tasks/` → `percy-service/tasks/` (Jarvis task documentation)
   - Do NOT copy: `test_env` (contains credentials — should be rotated), `.planning/`, `AGENTS.md`, root `package.json` (Playwright — see note below)
3. Create percy-service `.dockerignore` (use current `.dockerignore` as template, adapt for backend-only: exclude `tests/`, `docs/`, `.venv/`, `*.md`, `skills/`, `.beads`, `.claude`, `.planning`)
4. Create percy-service `Dockerfile`:
   - Python-only, uvicorn running `indemn_platform.api.main:app`
   - Must use `--workers 1` (background tasks + in-memory state)
   - Preserve non-root user pattern from current Dockerfile
   - Only `curl` needed for apt packages (no nginx, no supervisor)
5. Create percy-service `docker-compose.yml` (GHCR image, shared network, healthcheck)
6. Create percy-service `.github/workflows/build.yml` + `build-prod.yml` (use GitHub Actions for Docker with layer caching, self-hosted runners for deploy)
7. Add `python-dotenv` as explicit dependency in `pyproject.toml` `[dependencies]` (not dev — seed scripts need it too). Verify `deepagents>=0.2` resolves correctly (critical Jarvis dependency, may be a private package).
8. Push to `indemn-ai/percy-service` main branch
9. On EC2: `mkdir /opt/percy-service`, create `.env` with all backend env vars (see environment list in Container Architecture section — includes `V1_MONGODB_URI`, `AUTH_ENABLED`, `JWT_SECRET`, etc.)
10. On EC2: `cd /opt/percy-service && docker compose pull && docker compose up -d`
11. Verify: `curl http://localhost:8003/api/v1/health` returns expected response

**E2E tests note:** The root `package.json` contains Playwright dependencies for E2E browser tests. These tests exercise the full stack and may need to live in a separate test repo or remain in the frontend repo with the backend URL configured. Decision deferred — not a blocker for the separation.

### Phase 2 — Flip the frontend (the switchover)

12. In `copilot-dashboard-react`, create a branch:
    - Remove: `indemn_platform/`, `tests/`, `pyproject.toml`, `uv.lock`, backend seed scripts, `skills/evaluations/`
    - Remove: `supervisord.conf` (no longer managing two processes)
    - Remove: `test_env` file (contains credentials, should not be in any repo)
    - Simplify `Dockerfile`: remove Python build stage, keep Node build + nginx. CMD changes from `supervisord` to `nginx -g 'daemon off;'`. Preserve non-root `appuser` setup and nginx permission directories. Keep the stub `styles.ts` generation step (Dockerfile workaround for two-pass federation build).
    - Update `nginx.conf` (at repo root): proxy `/api/` and `/ws` to `percy-service:8000` with Docker DNS resolver
    - Update `docker-compose.yml`: use GHCR image with `IMAGE_TAG` variable, add healthcheck
    - Update `CLAUDE.md` and `.claude/` to reflect frontend-only structure
13. Test locally if possible (docker compose with both services on shared network)
14. Merge to main, build and deploy
15. Verify: `devplatform.indemn.ai` works end-to-end — agent list, agent detail, Jarvis chat (WebSocket), evaluations

### Phase 3 — Cleanup

16. Set up GitHub Actions runners for both repos
17. Verify CI/CD auto-deploys on push to main
18. Update Angular `copilot-dashboard` config: `platformWsUrl` must point to percy-service for Jarvis WebSocket in federated mode
19. Update any documentation referencing the old monorepo structure
20. Update `local-dev.sh` in operating-system if it manages platform-v2 startup
21. Create `CLAUDE.md` for percy-service repo (write from scratch for backend-only context, not copied from monorepo)
22. Clean up: remove `test_env` from copilot-dashboard-react if still present, remove `.planning/` directory from frontend repo

### Rollback

If Phase 2 breaks anything:
- Redeploy the last known good combined image: `docker compose pull app && docker compose up -d --no-deps app` in `/opt/copilot-dashboard-react`
- percy-service sitting idle causes no harm
- Investigate, fix, retry

## Risks and Gotchas

| Risk | Mitigation |
|------|------------|
| **nginx DNS resolution** — nginx caches upstream hostname at startup. If percy-service isn't up, 502s persist even after it starts. | Use `resolver 127.0.0.11` + variable-based `proxy_pass` to force re-resolution. |
| **WebSocket over Docker DNS** — WebSocket upgrade may behave differently over Docker networking vs localhost. | Test Jarvis chat specifically after switchover. Same nginx upgrade headers apply. |
| **Scoring drift** — `scoring.py` and `scoring.ts` now in separate repos. | Team awareness. Changes to scoring require PRs to both repos. |
| **Seed scripts** — moved to percy-service, need `MONGO_URL` to run. | Run from inside percy-service container or with correct env vars on EC2. |
| **CI/CD runner broken since Feb 11** — neither repo can auto-deploy. | Set up new runners (Craig now has access). Can do manual deploys during migration. |
| **Startup ordering** — frontend may start before backend is ready. | The DNS resolver fix handles this. nginx returns 502 briefly, then resolves once percy-service is up. Standard Docker behavior. |
| **Non-root user permissions** — simplified frontend Dockerfile must preserve `appuser` and nginx permission directories. | Copy the user creation and `chown` lines from the current Dockerfile into the new one. |
| **Angular WebSocket URL** — `dashboard-config.json` in copilot-dashboard passes `platformWsUrl` to federated Jarvis chat. | Must update to point to percy-service after separation. Address in Phase 3 cleanup. |
| **`python-dotenv` transitive dependency** — used explicitly but not listed in `pyproject.toml`. | Add as explicit dependency in percy-service to avoid breakage if upstream removes it. |
| **Production workflow** — both repos need `build-prod.yml` (triggers on `prod` branch), not just `build.yml`. | Include both workflows from day one. |
| **Background tasks with multiple workers** — `simulation_job_runner()` and `jarvis_job_runner()` are asyncio tasks started at boot. Multiple uvicorn workers duplicate them. | percy-service must use `--workers 1`. Current `--workers 2` in the monorepo is a latent bug. |
| **V1 MongoDB connection** — backend connects to TWO MongoDB databases: `indemn_platform` (primary) and tiledesk V1 (via `V1_MONGODB_URI`). | percy-service `.env` must include both connection strings. Missing `V1_MONGODB_URI` breaks Jarvis runner and V1 agent features. |
| **`test_env` file with credentials** — committed to the monorepo, contains real API keys and connection strings. | Do NOT copy to percy-service. Remove from copilot-dashboard-react during cleanup. |
| **Stub `styles.ts` generation** — Dockerfile has a workaround that generates a stub file before federation build. | Frontend Dockerfile must preserve this step or the build will fail. |
| **CORS origins** — backend CORS list includes `localhost` and `copilot` domains but not `devplatform.indemn.ai` or `platform.indemn.ai`. | Not a problem: all browser traffic goes through nginx proxy (same-origin). CORS only matters if Angular makes direct calls to percy-service bypassing nginx. Current design keeps all traffic proxied. |
| **Env var loading** — `settings.py` calls `load_dotenv(project_root / ".env")` but `.env` is never COPYed into the Docker image. | Works correctly: docker-compose `env_file` injects vars into the process environment. `load_dotenv` silently does nothing in Docker (file doesn't exist), and `os.environ.get()` picks up the compose-injected vars. Don't remove `env_file` from docker-compose. |
| **`deepagents>=0.2`** — critical Jarvis dependency, may be a private/custom package. | Verify it resolves from `uv sync` in the new repo. If it's a private index, the percy-service Dockerfile needs the same index configuration. |

## API Coupling (for reference)

The frontend communicates with the backend via two Axios clients:
- `apiClient` — base URL from `platformApiUrl` (Angular config or prop)
- `EvaluationApiClient` — base URL from `evaluationServiceUrl` (Angular config or prop)

These URLs are already configurable, not hardcoded. No frontend code changes required for the separation. The nginx proxy makes it transparent.

The only "shared" code is the scoring logic:
- Frontend: `ui/src/lib/scoring.ts`
- Backend: `indemn_platform/scoring.py`

These must stay in sync manually. No shared package or code generation exists today.

## Reference: percy-service Dockerfile

Based on line-by-line review of the current Dockerfile, this is the target structure:

```dockerfile
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app

COPY --from=builder /app /app

RUN groupadd --gid 10001 appgroup \
    && useradd --uid 10001 --gid appgroup --shell /bin/bash appuser

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "indemn_platform.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```
