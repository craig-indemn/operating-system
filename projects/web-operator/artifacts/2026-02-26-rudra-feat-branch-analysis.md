---
ask: "What has Rudra built on the feat-web-operator-improvement branch?"
created: 2026-02-26
workstream: web-operator
session: 2026-02-26-a
sources:
  - type: github
    description: "git diff/log analysis of indemn/feat-web-operator-improvement vs main (5 commits, 56 files, ~11,600 lines)"
  - type: github
    ref: "github.com/indemn-ai/web-operators"
    name: "feat-web-operator-improvement branch"
---

# Rudra's feat-web-operator-improvement Branch

Analysis of Rudra's work on the `indemn/feat-web-operator-improvement` branch. 5 commits, 56 files changed, ~11,600 lines added. This transforms the web-operator from a local CLI tool into a **production API service** with professional middleware, testing, and deployment infrastructure.

All commits co-authored with Cursor.

## What Changed — Architecture Overview

The codebase went from "run an agent locally via CLI" to a three-layer production system:

```
API Layer (FastAPI)          → accepts runs, queues them, tracks state
  ↓
Framework Layer (middleware) → caches, masks context, detects stalls
  ↓
Scripts Layer (automation)   → deterministic browser actions for Applied Epic
```

---

## 1. API Layer (`src/api/`)

A FastAPI server that manages web operator execution as a service.

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /runs` | Submit | Start a new agent run (FOP or CAP flow). Returns 202 started or 202 queued. |
| `GET /runs/{run_id}/status` | Poll | Run status: queued/running/completed/failed, elapsed time, outcome. |
| `GET /runs` | List | Active run, queue contents, recent runs (last 20). |
| `GET /health` | Probe | Liveness: status, SQLite state, active run, queue depth, uptime. |

### Key Design Decisions

- **One agent at a time.** Applied Epic can only handle one browser session, so the API serializes execution. Additional submissions go into a queue.
- **Conflation queue.** If a CAP run is already queued and another CAP request comes in, the new one replaces the old one. Only the latest matters.
- **Idempotency-Key header.** Safe retry semantics — replay the same request and get the same response.
- **SQLite for state** (`aiosqlite`). Four tables: runs, queue, idempotency_keys, session_logs. Lightweight, no external DB dependency.
- **MongoDB for artifacts.** On shutdown, syncs run results and per-activity extracted data to MongoDB (`johnson_runs` and `johnson_artifacts` collections). Historical analysis and cross-run comparison.
- **SNS notifications.** Best-effort failure alerts via AWS SNS (optional, skipped if not configured).
- **API key auth.** `X-Api-Key` header required on all endpoints except `/health`.

### Recovery

On startup, the API marks any orphaned runs (status='running' from a previous crash) as failed, then drains the queue to restart processing.

---

## 2. Framework Layer (`src/framework/`)

### SmartCacheMiddleware — Prompt Caching Optimization

Places Anthropic cache breakpoints at two stable positions:
1. **System message** — static after first turn (~8K tokens)
2. **Watermark** — the last masked tool output ("[output omitted]")

The watermark is monotonic (prefix only grows), so cache hit rate approaches 100%. This is a meaningful cost optimization given how many LLM turns a single run takes.

### WebOperatorMiddleware — Three Concerns in One Pass

**Observation masking.** Sliding window of last N full tool outputs (default 3). Older outputs get replaced with "[output omitted]". Keeps context window bounded at ~5K tokens for observations. Monotonic watermark prevents un-masking.

**Working memory injection.** Reads `working_memory.md` from disk and injects it into the system message every turn. Includes progress summary from the todo list with step status (pending/in_progress/completed).

**Progress-aware stall detection.** Detects stuck loops using:
- DOM change snapshots (elements, interactive items, refs)
- Success/failure markers in tool output
- Consecutive stall counter (only counts turns with zero progress)
- Alignment check: after N stalls, runs a cheap Haiku call to assess whether the agent is still goal-aligned
- Escalation: GiveUpAction enum escalates from retry → skip step → abort run
- Hard limit: 500 total turns caps any run

### epic_tools.py — 12 Structured Tools

Each tool wraps a script from `src/scripts/`, called as direct Python imports (no subprocess overhead). Tools wait for Epic page load before proceeding, and optionally save output JSON to the run directory as activity-prefixed files.

| Tool | What It Does |
|------|-------------|
| `epic_login` | Login flow with credentials from env vars |
| `epic_wait_for_load` | Page load polling |
| `epic_open_activity` | Search + open an activity |
| `epic_download_attachment` | Download PDF from activity |
| `epic_extract_coverages` | Extract policy coverage data |
| `epic_extract_vehicles` | Extract vehicle data |
| `epic_extract_drivers` | Extract driver data |
| `epic_extract_addl_interests` | Extract additional interests |
| `epic_open_policy` | Open a policy (with date normalization and smart matching) |
| `epic_update_activity` | Update activity fields (owner, date, notes) |
| `epic_not_issue_endorsement` | Mark endorsement as Not Issued |
| `epic_file_exit` | Exit activity (handles "No Leave In Process" popup) |

### executor.py — Enhanced Error Handling

- Streams agent events in real-time, logs each tool call to trajectory
- Transient error retry with exponential backoff (3 retries, 30s base)
- Context overflow detection ("prompt is too long" / "context_length_exceeded")
- On overflow, diagnoses which tool outputs were largest
- On failure, suggests resume command with step number

### runner.py — Run Tracking & Metrics

Each run gets a timestamped directory:
```
runs/run-YYYY-MM-DDTHH-MM-SS/
  checkpoints.db       — LangGraph SQLite
  screenshots/         — agent-browser captures
  working_memory.md    — agent state
  path_used.md         — copy of path document
  outcome.json         — final result
  trajectory.jsonl     — per-step log
  token_usage.jsonl    — per-turn token snapshots
  activity_*_*.json    — per-activity extracted data
  downloads/           — downloaded PDFs
```

Tracks input/output tokens, cache read/creation, per-step attribution, path hash for integrity checking.

---

## 3. Scripts Layer (`src/scripts/`)

11 deterministic browser automation scripts for Applied Epic operations. Each uses `_browser_helpers.py` for shared patterns:

- `wait_for_epic_load()` — three-phase wait: progress bar gone → network idle → DOM stable
- `run_eval()` / `eval_json()` / `eval_text()` — JavaScript execution via agent-browser
- Network monitoring via injected XHR/fetch counters

**These scripts are Applied Epic-specific.** They encode the DOM structure, navigation patterns, and data extraction logic for this particular insurance management system. When we build the reusable framework, the scripts layer is what gets generalized — the API and framework layers are already largely domain-agnostic.

---

## 4. Path Evolution (v1 → v6)

Rudra iterated through 6 versions of the CAP renewal path:

- **v1-v3**: Manual step-by-step instructions with verbose guardrails and warnings about SPA navigation gotchas
- **v4-v6**: Refactored to use the structured tools (epic_login, extract_activities, etc.) — the agent calls tools instead of manually navigating

v6 is the current version. It includes a new conditional step (3h2) for marking endorsements as "Not Issued" when no discrepancies are found.

The default flow registry maps: FOP → path_v0, CAP → path_v3 (configurable via env var).

---

## 5. Docker & Deployment

**Dockerfile**: Python 3.11-slim, installs poppler (PDF rendering), Node.js 20, agent-browser (npm), uv for Python deps. Runs uvicorn on port 8000.

**docker-compose.yml**: Single service with .env file, volume mounts for runs/, data/, and paths/. Health check on /health every 30s.

Production-ready but currently configured for single-instance deployment.

---

## 6. Testing

Comprehensive pytest suite:

| Test File | Coverage |
|-----------|----------|
| `test_api_routes.py` | Endpoint behavior (health, auth, create/list runs, idempotency) |
| `test_api_models.py` | Pydantic model validation |
| `test_queue.py` | SessionManager conflation behavior |
| `test_state.py` | SQLite state ops (runs, queue, idempotency, recovery) |
| `test_mongo.py` | MongoDB sync (if configured) |
| `test_notifications.py` | SNS integration |
| `test_middleware.py` | WebOperatorMiddleware (observation masking, stall detection) |
| `test_tools.py` | Tool execution |
| `test_config.py` | Config loading |

---

## Dependencies Added

```
fastapi, uvicorn[standard]   — API server
aiosqlite                    — async SQLite
boto3                        — SNS notifications
pymongo[srv]                 — MongoDB sync
```

Dev: `pytest`, `pytest-asyncio`

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `EPIC_URL`, `EPIC_ENTERPRISE_ID`, `EPIC_USERCODE`, `EPIC_PASSWORD` | Applied Epic login |
| `API_KEYS` | Comma-separated API keys for auth |
| `STATE_DB_PATH` | SQLite path (default: data/state.db) |
| `MONGO_URL` | MongoDB connection (optional) |
| `SNS_TOPIC_ARN` | SNS topic for failure alerts (optional) |
| `AWS_REGION` | AWS region (default: us-east-1) |
| `FLOW_REGISTRY` | JSON override for flow type → path mapping (optional) |

---

## Assessment

**What's solid:**
- The API + queue + state design is well-thought-out for the single-session constraint
- SmartCacheMiddleware is a smart cost optimization
- Stall detection with alignment checks is sophisticated — better than static timeouts
- Token tracking and run metrics will be valuable for optimization
- Docker setup means this can deploy anywhere

**What's Epic-specific (future generalization targets):**
- All 11 scripts in `src/scripts/` — hardcoded for Applied Epic DOM
- epic_tools.py — tool definitions tied to Epic operations
- Path documents — specific to ECM CAP/FOP workflows
- Login flow — Epic-specific authentication

**What's already generalizable:**
- API layer (endpoints, queue, state, auth)
- SmartCacheMiddleware and observation masking
- Stall detection and alignment checks
- Run tracking and metrics
- Docker deployment pattern
- Executor with retry and overflow handling
