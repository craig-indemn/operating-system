---
ask: "Generate voice analytics reports for Rankin (voice) and Distinguished Cyber (web chat), and fix Observatory ingestion pipeline bugs discovered during the process"
created: 2026-03-09
workstream: voice-analytics
session: 2026-03-09-a
sources:
  - type: slack
    description: "Searched #customer-implementation, #dev-squad for Rankin and Distinguished requirements from Jonathan and Ganesh"
  - type: mongodb
    description: "Queried prod tiledesk DB for org IDs, bot IDs, conversation counts, channels, date ranges"
  - type: langfuse
    description: "Verified Langfuse API is live, checked trace structure and metadata fields"
  - type: github
    description: "Checked indemn-observability repo branches, remotes, prod vs main divergence"
  - type: observatory-api
    description: "Ran full ingestion pipeline locally: sync-traces, ingest, aggregate for both orgs"
---

# Voice Analytics Session Handoff — 2026-03-09

## What Was Requested (from Slack)

### 1. Rankin Voice Report (from Jonathan in #customer-implementation)
- **Request**: 2-week voice retrospective report for Rankin Insurance
- **Reporter**: Jonathan (U07U9TCVBS8)
- **Additional context**: Jonathan and Rem discussed splitting reporting into two artifacts:
  1. **Customer-facing** (product-led growth oriented)
  2. **Internal** (voice technical benchmark tracing)
- **Craig's response**: Will run ad hoc locally, asked for feedback on format changes
- **Deadline**: Not hard, but Jonathan checking in today

### 2. Distinguished Cyber Report (from Ganesh in #dev-squad)
- **Request**: Curated report for Distinguished's Cyber Agent — their sync meeting is tomorrow morning (March 10)
- **Reporter**: Ganesh (U040W167JP6)
- **Deadline**: EOD March 9
- **Requested metrics**:
  1. Number of conversations with at least one user utterance
  2. Feedback from conversations
  3. Requests to talk to a human
  4. Avg conversation depth (total utterances), steps (user utterances), and time
  5. Bonus: Sankey view of conversations
- **Time period**: March 5-9 (Thursday to Monday)
- **Context**: Craig said Observatory is ready for them but prod deploy blocked until Wednesday. Offered to create ad-hoc report that can later become a downloadable report in the Observatory.

## Data Discovery

### Rankin Insurance Group
- **Org ID**: `6953c708922e070f5efb57a7`
- **Project ID**: `6953c726922e070f5efb57c3`
- **Voice bots**: Ronnie (`696a321bec2b21075fcb8b2f`), Ronnie2 (`697259edec2b21075fda6439`), Ronnie3 DEV (`69821c06803dd0ae1471c557`)
- **Web bots**: James Sales Agent (`6953c726922e070f5efb57f1`), Bernadette, Curtis, Jamie
- **Voice data**: 54 calls in last 2 weeks in MongoDB `requests` (with `attributes.CallSid`)
- **Total voice all time**: 245 calls
- **Channel**: All channel=`chat21` (even voice — tiledesk doesn't distinguish)
- **Voice identification**: Presence of `attributes.CallSid` field
- **Langfuse traces**: Live, 2,779 traces synced (all orgs, Feb 24 - Mar 9)
- **Observatory data after ingestion**: 203 conversations (48 voice Ronnie2, 2 webchat James)

### Distinguished
- **Org ID**: `679b191315e8c30013abdcb0` (active org — the second org `69458775d212860013e5630c` is inactive/empty)
- **Project ID**: `679b193615e8c30013abdcd2`
- **Cyber Agent bot ID**: `68f7e0ae8d5cbe00140d62f0`
- **Internal User Assistant bot ID**: `679b193615e8c30013abdcdf`
- **Melody (voice) bot ID**: `69989523c603efb2b0c4df50` (zero conversations — not deployed)
- **March 4-9 conversations**: 14 total (7 Cyber test on Mar 4, 1 Cyber real on Mar 5, 6 Internal real on Mar 5-6)
- **All-time non-test Cyber Agent**: 43 conversations
- **Observatory data after ingestion**: 86 conversations total (Cyber + Internal)

### Key Data Finding
The Distinguished Cyber Agent has **only 1 non-test conversation** in the March 5-9 window. The 7 conversations on March 4 are all `isTestMode: true` (testing before go-live). Craig needs to ping Ganesh/Peter to confirm this is expected and decide whether to include test data or expand the date range.

## Previous Rankin Voice Report

**Found at**: `/Users/home/Repositories/indemn-observability/reports/Rankin_Insurance_Group_Voice_Daily_2026-02-05.pdf`
- **Generator script**: `indemn-observability/scripts/generate-voice-report.jsx` (622 lines, React-PDF)
- **Data JSON**: `indemn-observability/data/voice-report-2026-02-05.json`
- **Data structure**: customerName, botName, reportDate, summary (totalCalls, uniqueCallers, handoffRate, etc.), callsByHour, sentimentDistribution, callReasons, qualitySummary (avgResponseTime, avgTranscriptionConfidence, interruptions, LLM TTFT, TTS TTFB), calls[] (per-call: callSid, time, callerNumber, durationSeconds, messageCount, sentiment, summary, fullTranscript, quality metrics, actionItems)
- **Run command**: `cd /Users/home/Repositories/indemn-observability && NODE_PATH=frontend/node_modules node scripts/generate-voice-report.jsx data/voice-report-2026-02-05.json`
- **Data extraction script**: `scripts/extract-voice-data.py` — extracts voice call data from MongoDB for reports

## Observatory Ingestion Pipeline — What Was Done

### Bug Found and Fixed
**File**: `src/observatory/ingestion/connectors/mongodb.py` line 232
**Bug**: `get_all_bot_ids()` function used `query["id_project"] = organization_id` — passing an org ID to query a project ID field. These are different IDs in tiledesk.
**Fix**: Changed to `query["id_organization"] = ObjectId(organization_id)`
**Why never caught in prod**: The Lambda pipeline (`lambda/ingestion_pipeline/lambda_function.py`) never passes `organization_id` — it runs date-range-only syncs across ALL orgs. The bug only triggers when scoping to a specific org.
**Status**: Fixed locally on `main` branch of `/Users/home/Repositories/indemn-observability/`. NOT committed or pushed yet.

### Pipeline Execution (all completed successfully)

| Step | Rankin | Distinguished |
|------|--------|---------------|
| Sync LangSmith traces | N/A (voice) | 559 traces synced |
| Sync Langfuse traces | 2,779 traces synced (all orgs) | N/A (web) |
| Ingest (reuse_classifications=true) | 56/57 processed | 14/14 processed |
| Aggregate | 203 snapshots | 86 snapshots |

### How to Run the Pipeline
```bash
# Get auth token
TOKEN_RAW=$(curl -s -X POST http://localhost:8004/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"support@indemn.ai","password":"nzrjW3tZ9K3YiwtMWzBm"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")

# 1. Sync traces (LangSmith for web, Langfuse for voice)
curl -s -X POST http://localhost:8004/api/admin/sync-traces \
  -H "Authorization: $TOKEN_RAW" -H "Content-Type: application/json" \
  -d '{"organization_id": "ORG_ID", "date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD"}'

curl -s -X POST http://localhost:8004/api/admin/sync-langfuse-traces \
  -H "Authorization: $TOKEN_RAW" -H "Content-Type: application/json" \
  -d '{"date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD"}'

# 2. Ingest
curl -s -X POST http://localhost:8004/api/admin/ingest \
  -H "Authorization: $TOKEN_RAW" -H "Content-Type: application/json" \
  -d '{"organization_id": "ORG_ID", "date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD", "reuse_classifications": true}'

# 3. Aggregate
curl -s -X POST http://localhost:8004/api/admin/aggregate \
  -H "Authorization: $TOKEN_RAW" -H "Content-Type: application/json" \
  -d '{"organization_id": "ORG_ID"}'

# Monitor jobs
curl -s http://localhost:8004/api/admin/jobs -H "Authorization: $TOKEN_RAW"
```

## Observatory State

- **Backend**: Running on port 8004 (may need restart: `cd /Users/home/Repositories/indemn-observability && source venv/bin/activate && PYTHONPATH=. uvicorn src.observatory.api.main:app --reload --port 8004`)
- **Frontend**: Running on port 5175
- **Pointing at**: Production MongoDB (`prod-indemn.3h3ab.mongodb.net/tiledesk`)
- **Auth**: `AUTH_ENABLED=true`, login via `support@indemn.ai` / copilot auth proxy
- **Branch**: `main` (matches `indemn/main`, ahead of `indemn/prod`)
- **Prod deploy**: Blocked until Wednesday (PR #28 main→prod). Observatory was taken down in prod due to a bug.

## What Still Needs to Be Done

### Immediate (EOD deadline for Distinguished)
1. **Review Observatory in browser** — Craig needs to look at http://localhost:5175 for both Distinguished and Rankin, verify data makes sense
2. **Distinguished Cyber report** — Generate Ganesh's requested metrics for March 5-9. Only 1 real Cyber Agent conversation exists. Options:
   - Ping Ganesh/Peter to confirm this is expected
   - Include test conversations from March 4
   - Expand date range
   - Include Internal User Assistant data (6 real convos)
   - Screenshot/export from Observatory UI
3. **Rankin voice report** — Generate 2-week retrospective using the existing `generate-voice-report.jsx`. Need to:
   - Extract voice data for Ronnie2 agent, Feb 24 - Mar 9
   - Can use `scripts/extract-voice-data.py` or build JSON from MongoDB + Langfuse
   - Run the PDF generator
   - Consider Jonathan's two-report split (customer vs internal)

### Follow-up
4. **Commit the `get_all_bot_ids` bug fix** in indemn-observability and include in next prod deploy
5. **Set up voice data ingestion in production** — the Langfuse sync works but wasn't running in prod because Observatory was down
6. **Add Distinguished Cyber report as downloadable in Observatory** — per Craig's Slack message

## Related Projects
- `projects/voice-evaluations/` — voice evaluation framework, Langfuse integration design
- `projects/observatory/` — Observatory auth fixes, PR tracking
- `projects/gic-observatory/` — GIC-specific Observatory features, PDF report generation patterns
- `projects/analytics-dashboard/` — Usage analytics overview feature

## Key Files
| File | Purpose |
|------|---------|
| `indemn-observability/scripts/generate-voice-report.jsx` | React-PDF voice report generator (622 lines) |
| `indemn-observability/scripts/extract-voice-data.py` | MongoDB voice data extraction script |
| `indemn-observability/data/voice-report-2026-02-05.json` | Previous Rankin report data (reference format) |
| `indemn-observability/reports/Rankin_Insurance_Group_Voice_Daily_2026-02-05.pdf` | Previous Rankin PDF |
| `indemn-observability/src/observatory/ingestion/connectors/mongodb.py` | Bug fix location (line 232) |
| `indemn-observability/lambda/ingestion_pipeline/lambda_function.py` | Prod Lambda (no org_id scoping) |
| `.claude/skills/langfuse/SKILL.md` | Langfuse API patterns |
| `.claude/skills/report-library/SKILL.md` | PDF report brand system |
| `.claude/skills/report-generate/SKILL.md` | PDF report workflow |
