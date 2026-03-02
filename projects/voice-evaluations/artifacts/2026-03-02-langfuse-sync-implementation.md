---
ask: "Implement Langfuse trace sync + fix transcript evaluation join for end-to-end voice data pipeline"
created: 2026-03-02
workstream: voice-evaluations
session: 2026-03-02-b
sources:
  - type: github
    description: "Code changes across indemn-observability (8 files) and evaluations (1 file)"
  - type: mongodb
    description: "Dev MongoDB tiledesk.traces and tiledesk.requests for join verification"
  - type: langfuse
    description: "Dev Langfuse project cmht0gwcr001oad07czzyujje — 180 traces, 16 in date range"
---

# Langfuse Sync Implementation & Initial Test Results

## What Was Built

### Observatory (indemn-observability, branch: demo-gic)

**3 commits** (all local, unpushed):
- `c249af9` feat: Langfuse trace sync task + API endpoint
- `e035deb` fix: Langfuse API compatibility — Z suffix + limit=100

**Files changed:**
1. `connectors/langfuse.py` — Added `transform_observation_to_run()` (static, converts Langfuse obs → Langsmith-compatible run schema), `aiter_all_traces()` (async generator, all traces in date range), `_iso_with_z()` helper
2. `connectors/mongodb.py` — Added `get_request_id_by_call_sid()` (two-hop join), `get_request_id_by_phone_and_time()` (fallback join by phone + time window)
3. `writers/mongodb.py` — Added `get_latest_langfuse_sync_time()`, compound index `(extra.metadata.source, _synced_at)`
4. `tasks.py` — Added `run_sync_langfuse_traces_task()` — core sync function
5. `ingestion/__init__.py` — Export new task
6. `api/models/base.py` — Added `SyncLangfuseTracesRequest`, updated `JobResponse.job_type` Literal
7. `api/models/__init__.py` — Re-exported new model
8. `api/routers/admin.py` — Added `POST /api/admin/sync-langfuse-traces` endpoint

### Evaluations (evaluations, branch: main)

**1 commit** (local, unpushed):
- `9f8b7da` fix: rewrite Langfuse tool call fetch with two-hop join via CallSid

**File changed:**
- `transcript_evaluation.py` — Rewrote `_fetch_langfuse_tool_calls()`: MongoDB request lookup → CallSid → Langfuse filter JSON, phone+room_name fallback, fetches both GENERATION and TOOL observations

## Bugs Found & Fixed During Testing

1. **Langfuse requires Z suffix on ISO timestamps** — `datetime.isoformat()` on naive datetimes produces `2026-02-01T00:00:00` which Langfuse rejects with 400. Fixed with `_iso_with_z()` helper.
2. **Langfuse observations endpoint caps at limit=100** — Our code passed `limit=200`, got 400. Fixed to `limit=100`.

## Initial Test Results (Dev Environment)

### Setup
- Dev Langfuse project: `cmht0gwcr001oad07czzyujje` (180 total traces)
- Dev MongoDB: `dev-indemn.pj4xyep.mongodb.net/tiledesk` (742 voice requests)
- All services started via `local-dev.sh start --env=dev`
- Auth: copilot-server JWT (support@indemn.ai), strip "JWT " prefix for Observatory Bearer auth

### Sync Results
```
Job 2947a104: completed in ~30 seconds
Traces in date range (Feb 1 - Mar 3): 16 of 180 total
Observations synced: 620 runs
Join resolution: 11/16 traces matched (69%), 5 unmatched
Distinct request_ids: 8 (all 8 verified in requests collection)
```

### DISCREPANCIES TO INVESTIGATE

**1. 11 matched traces → only 8 distinct request_ids**
- 11 traces matched but only 8 unique request_ids. This means 3 traces matched to the SAME request_id as another trace. The phone+time fallback join may be matching multiple Langfuse traces to the same MongoDB request (e.g., if a caller called back within the 5-minute window, or if there are duplicate/retry traces in Langfuse for the same call).
- **Action needed**: Query to see which request_ids have multiple Langfuse traces pointing at them, and whether that's correct.

**2. 5 unmatched traces (31%)**
- These 5 traces had phone numbers extracted from `lk.room_name` but no matching request found in dev MongoDB within the 5-minute window.
- Possible causes: (a) the call exists in prod MongoDB but not dev, (b) the `createdAt` timestamp in requests differs by more than 5 minutes from the Langfuse trace timestamp, (c) the phone regex didn't extract correctly, (d) the `attributes.From` field format doesn't match.
- **Action needed**: Log the specific phone numbers and timestamps for the 5 unmatched traces, then manually check MongoDB.

**3. Run type distribution seems off**
- 620 runs: 569 chain + 51 llm + 0 tool
- Expected from plan: ~10 GENERATION + ~5 TOOL + ~10 AGENT + ~75 SPAN per trace
- The 0 tool count is suspicious — TOOL observations should map to run_type="tool"
- **Action needed**: Check if TOOL observations exist in dev Langfuse, or if that observation type is only in prod.

**4. No TOOL observations found**
- The transform maps GENERATION→"llm", TOOL→"tool", else→"chain". Getting 0 tools means either (a) dev Langfuse has no TOOL-type observations, or (b) the observation type field name is different.
- **Action needed**: Fetch raw observations for one trace and check the actual `type` values.

## Environment Configuration

### Langfuse Two-Project Setup
| Project | Project ID | Creds Location | Traces |
|---------|-----------|----------------|--------|
| Prod (indemn) | `cmht0a7ll001qad07jn0ko84c` | OS `.env` | 1,142 |
| Dev (dev indemn) | `cmht0gwcr001oad07czzyujje` | `.env.dev` | 180 |

**Critical**: Prod Langfuse traces match PROD MongoDB only. Dev Langfuse traces match DEV MongoDB only. Using mismatched creds/DB will yield 0 joins.

### Env Var Notes
- Added `LANGFUSE_HOST="https://hipaa.cloud.langfuse.com"` to `.env.dev` (was missing — only had `LANGFUSE_BASE_URL`)
- Observatory reads `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`
- Evaluations reads `langfuse_host`, `langfuse_public_key`, `langfuse_secret_key` (from settings)

### Auth for Local Testing
Observatory admin endpoints require `is_indemn_employee=True`. Get token via:
```python
# Get JWT from copilot-server
resp = requests.post("http://localhost:3000/auth/signin",
    json={"email": "support@indemn.ai", "password": "nzrjW3tZ9K3YiwtMWzBm"})
token = resp.json()["token"].replace("JWT ", "")  # Strip prefix!
# Use as: Authorization: Bearer {token}
```

## Remaining Test Steps (From Plan)

- [ ] **Investigate discrepancies** (above — must do before proceeding)
- [ ] Step 4: Run ingestion (`POST /api/admin/ingest`) for voice conversations
- [ ] Step 5: Verify Observatory UI (localhost:5175) — voice channel badge, trace panel
- [ ] Step 6: Trigger transcript evaluation from Observatory
- [ ] Step 7: Verify in Copilot Dashboard (localhost:4500) — Transcript type badge

## Services Running
All started via `local-dev.sh start --env=dev`:
- Observatory: 8004 + UI: 5175
- Bot-service: 8001
- Evaluations: 8002 + UI: 5174
- Copilot-server: 3000
- Copilot-dashboard: 4500
