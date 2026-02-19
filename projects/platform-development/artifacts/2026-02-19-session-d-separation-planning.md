---
ask: "Plan the backend/frontend separation of copilot-dashboard-react into percy-service"
created: 2026-02-19
workstream: platform-development
session: 2026-02-19-d
sources:
  - type: github
    description: "indemn-ai/percy-service repo (empty), indemn-ai/copilot-dashboard-react structure"
  - type: local
    description: "Three rounds of design review against actual codebase at /Users/home/Repositories/indemn-platform-v2"
---

# Session D: Backend/Frontend Separation Planning

## What Happened

Designed and validated the plan to separate the Python FastAPI backend from the React frontend in `copilot-dashboard-react` into a new `percy-service` repo.

### Key Decisions
- **percy-service** gets the entire Python backend (`indemn_platform/`, tests, seed scripts, skills)
- **copilot-dashboard-react** keeps React UI, federation, docs, nginx
- Two separate containers, two docker-compose files, existing shared Docker network
- Frontend nginx proxies `/api/` + `/ws` to percy-service via Docker DNS
- Jarvis → Percy rename is repo-name only (code stays "Jarvis")
- Clean git history break (no history migration)
- Migration: deploy backend first → verify → flip frontend → verify

### Design Reviews (3 rounds)
The design was reviewed three times against the actual codebase. Key corrections:

**Round 1:** Fixed entry point (`indemn_platform.api.main:app` not `main.py`), nginx.conf path (repo root not `nginx/`), port (8080 not 80), proxy location (`/api/` not `/api/v1`), removed phantom `dashboard-config.json`, added tests/ directory, production workflow, correct env vars.

**Round 2:** Fixed CI/CD (GitHub Actions not raw docker build, self-hosted runners not SSH, GHCR images not local builds), added `--workers 1` requirement (background tasks + in-memory state), found missing env vars (`V1_MONGODB_URI`, `AUTH_ENABLED`, `JWT_SECRET`, `CO_PILOT_URL`), removed unused env vars (`REDIS_URL`, `PINECONE_ENVIRONMENT`).

**Round 3:** Added `permissions` blocks and GHCR login to deploy jobs, `workflow_dispatch` trigger, run-number tags, `start_period` for healthchecks, nginx.conf preservation checklist, CORS clarification, `deepagents>=0.2` verification note, reference Dockerfile.

### Beads Epic Created
Epic `p0l` with 15 tasks across 3 phases. Dependency chain is fully wired. Old architecture discussion bead `5q2` superseded.

## Outputs
- Design doc: `artifacts/2026-02-19-backend-separation-design.md` (reviewed 3x, implementation-ready)
- Beads epic: `platform-development-p0l` (15 tasks, dependency chain set)
- First task ready: `p0l.1` — Scaffold percy-service repo with backend code
