# Design: Observatory Report Hub

**Date:** 2026-03-12
**Status:** Approved

## Problem

Indemn generates PDF reports for customers (voice reports for Rankin, internal agent reports for Distinguished Programs, customer analytics for GIC, etc.) on an ad-hoc basis using CLI scripts and client-side rendering. There's no unified place for customers or internal team to browse, generate, or download reports. Reports are generated manually and delivered via email or Slack.

## Solution

A Report Hub in the observatory — a new "Reports" tab where:
- Customers log in and see report types available for their org
- Anyone can generate a new report by selecting type, agent, and date range
- Previously generated reports are cataloged and downloadable
- Internal users see all report types and all generated reports across orgs
- New report types are registered via an admin API, integrated into the `/report-generate` skill

## Design Principles

- Use existing infrastructure: MongoDB for metadata, existing extraction scripts and JSX renderers
- Server-side generation so all report types (including voice with full transcripts) work from the browser
- Extractors are synchronous Python functions wrapped in `asyncio.to_thread()` — preserves CLI compatibility without rewriting to async
- JSX renderers run via Node subprocess (no rewrite needed)
- PDFs stored in S3, metadata in MongoDB
- Per-org report type configuration — not every customer sees every report type
- Auth uses `get_current_user` with custom org access checks (not `ValidatedScope`, which is query-param based and doesn't fit the report access pattern)

---

## Data Model

Two new collections in the `tiledesk` database.

### `report_types` — Registry of available report types

```json
{
  "slug": "voice-daily",
  "name": "Voice Daily Report",
  "description": "Daily voice call summary with per-call transcripts and quality metrics",
  "scope": "agent",
  "parameters": {
    "date_from": { "type": "date", "required": true },
    "date_to": { "type": "date", "required": true }
  },
  "extractor": "voice_data",
  "renderer": "generate-voice-report.jsx",
  "org_ids": ["6953c726922e070f5efb57c3"],
  "enabled": true,
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

**Fields:**
- `slug` — unique identifier, used in API calls and URLs
- `scope` — `"agent"` (requires agent selection) or `"customer"` (org-level only)
- `parameters` — defines what the user must provide to generate (date range is standard; extensible for future params)
- `extractor` — Python module path relative to `src/observatory/extractors/` (e.g., `voice_data` for `src/observatory/extractors/voice_data.py`)
- `renderer` — path relative to `scripts/`, the JSX file that produces the PDF
- `org_ids` — array of org IDs that can access this report type. `null` means available to all orgs
- `enabled` — soft delete flag

### `reports` — Catalog of generated reports

```json
{
  "report_type": "voice-daily",
  "org_id": "6953c726922e070f5efb57c3",
  "org_name": "Rankin Insurance Group",
  "agent_id": "67dd2002eccaed00135911d4",
  "agent_name": "Ronnie2",
  "date_from": "ISODate",
  "date_to": "ISODate",
  "s3_key": "reports/6953c726.../voice-daily/67dd2002.../2026-03-01_2026-03-10.pdf",
  "s3_bucket": "indemn-observatory-reports",
  "file_size_bytes": 207000,
  "generated_by": "craig@indemn.ai",
  "created_at": "ISODate"
}
```

**S3 key pattern:** `reports/{org_id}/{report_type_slug}/{agent_id}/{date_from}_{date_to}.pdf`
- `agent_id` is `_none` for org-level (customer-scoped) reports
- Agent ID is included to prevent collisions when the same report type is generated for different agents on the same date range

**Deduplication:** Regenerating the same report (same type + org + agent + date range) replaces the existing entry. The generate endpoint upserts the `reports` catalog entry on the compound key `(report_type, org_id, agent_id, date_from, date_to)` and overwrites the S3 object. Only the latest version exists.

### Indexes

```
report_types:
  - { slug: 1 } unique
  - { org_ids: 1, enabled: 1 }

reports:
  - { org_id: 1, created_at: -1 }
  - { org_id: 1, report_type: 1, agent_id: 1, created_at: -1 }
  - { report_type: 1, org_id: 1, agent_id: 1, date_from: 1, date_to: 1 } unique  # dedup key
```

---

## Backend API

New router: `src/observatory/api/routers/reports.py`

### Auth Pattern

Report endpoints use `get_current_user` (from `auth.py`) instead of `ValidatedScope`. `ValidatedScope` is designed for query-param-based scope filtering on pre-computed aggregation data — it doesn't fit the report access pattern where we need to check `org_ids` array membership on report types and `org_id` on individual reports.

Access control logic:
- **Internal users** (`user.is_indemn_employee` or equivalent): can access all report types and all reports
- **Customer users**: can access report types where `org_ids` contains any of their `user.organization_ids` (or `org_ids` is null), and can access reports where `org_id` matches one of their orgs
- **Admin endpoints** (`POST/PATCH/DELETE /api/reports/types`): require `require_indemn_employee` dependency (same pattern as existing admin router)

### Report Type Endpoints (Admin)

**`POST /api/reports/types`** — Register a new report type
- Auth: `require_indemn_employee`
- Body: `{ slug, name, description, scope, parameters, extractor, renderer, org_ids }`
- Validates: no duplicate slug, extractor file exists, renderer file exists
- Returns: created report type document

**`PATCH /api/reports/types/{slug}`** — Update a report type
- Auth: `require_indemn_employee`
- Updatable: name, description, org_ids, enabled, parameters
- Use case: add a new org to an existing report type, disable a report type

**`DELETE /api/reports/types/{slug}`** — Disable a report type
- Auth: `require_indemn_employee`
- Soft delete: sets `enabled: false`
- Does not remove previously generated reports

### Report Endpoints (All Users)

**`GET /api/reports/types`** — List available report types for current scope
- Auth: `get_current_user`
- Internal users: return all enabled types
- Customer users: filter where `org_ids` contains any of the user's org IDs, or `org_ids` is null
- Returns: array of report type documents

**`GET /api/reports`** — List previously generated reports
- Auth: `get_current_user`
- Internal users: return all reports (filterable by org_id query param)
- Customer users: filter where `org_id` matches one of their orgs
- Additional query params: `report_type`, `agent_id`, `date_from`, `date_to`
- Sorted: `created_at` descending
- Paginated: `skip`, `limit` (default 20)
- Returns: array of report documents (without download URL — use the download endpoint)

**`POST /api/reports/generate`** — Generate a new report
- Auth: `get_current_user`
- Body: `{ report_type, org_id, agent_id, date_from, date_to }`
- Validates: report type exists, user has access to the specified org, required parameters provided
- Synchronous: blocks until PDF is generated and uploaded
- Flow:
  1. Look up report type from registry
  2. Verify user can access the specified `org_id`
  3. Run the extractor function via `asyncio.to_thread()`
  4. Write extracted JSON to temp file
  5. Subprocess: `node scripts/{renderer} /tmp/extract.json --output /tmp/report.pdf`
  6. Upload PDF to S3
  7. Upsert `reports` catalog entry (dedup on type + org + agent + dates)
  8. Return report metadata + pre-signed download URL

**`GET /api/reports/{report_id}/download`** — Get download URL for a report
- Auth: `get_current_user`
- Looks up report by `_id`, verifies user has access to the report's `org_id`
- Generates a pre-signed S3 URL (15 min expiry)
- Returns: `{ url: "https://..." }`

### Error Responses

All endpoints return consistent error shapes:

```json
{
  "detail": "Report type 'voice-daily' not found",
  "error_code": "REPORT_TYPE_NOT_FOUND"
}
```

| Scenario | Status | Error Code |
|----------|--------|------------|
| Report type not found | 404 | `REPORT_TYPE_NOT_FOUND` |
| Report not found | 404 | `REPORT_NOT_FOUND` |
| Org access denied | 403 | `ORG_ACCESS_DENIED` |
| Missing required parameter | 422 | (FastAPI default validation) |
| Extractor failed | 500 | `EXTRACTION_FAILED` |
| Renderer failed | 500 | `RENDERING_FAILED` |
| S3 upload failed | 500 | `UPLOAD_FAILED` |

---

## Server-side Generation Flow

```
POST /api/reports/generate
  │
  ├── 1. Validate request
  │     └── Look up report_type, verify user org access, validate params
  │
  ├── 2. Extract data (Python, sync via asyncio.to_thread)
  │     └── extractor = get_extractor(report_type.extractor)
  │         data = await asyncio.to_thread(extractor, config.mongodb.uri, org_id, agent_id, date_from, date_to)
  │
  ├── 3. Render PDF (Node subprocess via asyncio.create_subprocess_exec)
  │     ├── Write data to /tmp/extract-{uuid}.json
  │     └── node scripts/{renderer} /tmp/extract-{uuid}.json --output /tmp/report-{uuid}.pdf
  │
  ├── 4. Upload to S3
  │     └── boto3 put_object to indemn-observatory-reports bucket
  │
  ├── 5. Catalog
  │     └── Upsert into reports collection (dedup on type + org + agent + dates)
  │
  ├── 6. Cleanup
  │     └── Delete temp JSON and PDF files (in finally block)
  │
  └── 7. Respond
        └── Return report metadata + pre-signed download URL
```

### Extractor Package

Extractors live at `src/observatory/extractors/` — inside the main Python package so they're importable from the API routers via standard Python imports. They are **not** in `scripts/` (which is not a Python package and is not on `sys.path`).

Extractors stay **synchronous** (using `pymongo`) because: (a) the CLI scripts already work this way, (b) the API calls them via `asyncio.to_thread()` which runs sync code in a thread pool without blocking the event loop, (c) no need to rewrite every MongoDB query to async Motor.

```python
# src/observatory/extractors/__init__.py
from .registry import get_extractor  # dynamic lookup by slug

# src/observatory/extractors/registry.py
from importlib import import_module

def get_extractor(slug: str):
    """Dynamically import an extractor module by slug.
    e.g., slug='voice_data' → observatory.extractors.voice_data.extract()"""
    module = import_module(f".{slug}", package="src.observatory.extractors")
    return module.extract

# src/observatory/extractors/voice_data.py

def extract(mongodb_uri: str, org_id: str, agent_id: str | None,
            date_from: datetime, date_to: datetime) -> dict:
    """Extract voice call data. Synchronous — uses pymongo directly.
    Called from API via asyncio.to_thread(), or directly from CLI."""
    client = MongoClient(mongodb_uri)
    db = client["tiledesk"]
    try:
        # 1. Resolve org_id → project IDs
        #    The `requests` collection uses `id_project` (Tiledesk project ID),
        #    not `org_id` directly. An org can have multiple projects.
        project_ids = [
            str(p["_id"]) for p in
            db["projects"].find({"id_organization": org_id}, {"_id": 1})
        ]

        # 2. Build query with date range and optional agent filter
        query = {
            "id_project": {"$in": project_ids},
            "createdAt": {"$gte": date_from, "$lt": date_to},
            "attributes.channel": "VOICE",
        }
        if agent_id:
            query["agents.id_bot"] = agent_id

        # 3. Query and shape data for the renderer
        # ... (adapted from existing extract-voice-data.py logic)

        return data
    finally:
        client.close()
```

**Key design decisions:**

1. **Location:** `src/observatory/extractors/` not `scripts/extractors/`. This is a proper Python package, importable from `src.observatory.api.routers.reports` without `sys.path` hacks. The `scripts/` directory stays as-is for standalone CLI usage.

2. **Dynamic registry:** The `report_types` collection stores an `extractor` slug (e.g., `"voice_data"`). The `get_extractor()` function uses `importlib` to load the module dynamically, so adding a new extractor doesn't require changing the router code.

3. **Org → Project ID resolution:** The `requests` collection uses `id_project` (Tiledesk project ID), not `org_id`. Extractors must resolve `org_id` → project IDs by querying the `projects` collection where `id_organization` matches. This is a lookup, not a 1:1 mapping — an org can have multiple projects.

4. **Date range support:** The existing `extract_voice_data` CLI function takes a single `date` and computes `next_day = date + timedelta(days=1)`. The new `extract()` interface takes `date_from`/`date_to` directly for proper range support. The query logic is adapted, not wrapped.

5. **Agent filtering:** The existing CLI function has no `agent_id` parameter. The new interface adds it as optional — when provided, the query includes `agents.id_bot` to filter to a specific agent/bot.

**CLI wrappers preserved:** The existing `scripts/extract-voice-data.py` stays as a CLI tool. It can be updated to import from `src.observatory.extractors.voice_data` (with `PYTHONPATH=.`) or kept as a standalone copy. Either way, the hub uses the `src/observatory/extractors/` package.

The API router calls extractors like:
```python
# src/observatory/api/routers/reports.py
# Uses relative imports consistent with existing router convention
from ...extractors import get_extractor

extractor = get_extractor(report_type.extractor)  # e.g., "voice_data"
data = await asyncio.to_thread(
    extractor, config.mongodb.uri, org_id, agent_id, date_from, date_to
)
```

### JSX Renderers

No changes needed. Renderers stay as standalone Node scripts. They read JSON from a file and produce a PDF. The Node subprocess is called via `asyncio.create_subprocess_exec` to avoid blocking the event loop:

```python
import asyncio, json, tempfile, uuid

# Write extracted data to temp file
tmp_json = f"/tmp/extract-{uuid.uuid4()}.json"
tmp_pdf = f"/tmp/report-{uuid.uuid4()}.pdf"
try:
    with open(tmp_json, "w") as f:
        json.dump(data, f, default=str)

    proc = await asyncio.create_subprocess_exec(
        "node", f"scripts/{report_type.renderer}", tmp_json,
        "--output", tmp_pdf,
        env={**os.environ, "NODE_PATH": "/app/scripts/node_modules"},
        cwd="/app",  # match Docker WORKDIR so __dirname-relative paths resolve
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise ReportRenderError(f"Renderer failed: {stderr.decode()}")

    # Upload tmp_pdf to S3...
finally:
    for f in (tmp_json, tmp_pdf):
        if os.path.exists(f):
            os.unlink(f)
```

### AWS / S3

The observatory doesn't currently use S3 or boto3. This adds:

**Python dependencies:** `boto3` and `pymongo` added to `requirements.txt`. (`pymongo` is currently only a transitive dependency via `motor` — adding it explicitly prevents breakage if `motor` is ever removed.)

**Configuration:** New `S3Config` dataclass in `src/observatory/config.py`:
```python
@dataclass
class S3Config:
    bucket_name: str    # env: S3_REPORT_BUCKET (default: "indemn-observatory-reports")
    region: str         # env: AWS_REGION (default: "us-east-1")
    presign_expiry: int # env: S3_PRESIGN_EXPIRY (default: 900, i.e. 15 min)
```

**Credentials:** boto3 uses its default credential chain — picks up `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` from the environment, which are already set by `aws-env-loader.sh` at deploy time.

**`.env.example` update:** Add `S3_REPORT_BUCKET`, `AWS_REGION` entries (per project policy: "when adding env variables, update `.env.example` in the same PR").

---

## Frontend

### New Tab: Reports

Add "Reports" to the tab bar in `TabBar.tsx` (6th tab, after Conversations).

New route in `App.tsx`: add `/reports` → `<ReportsView />` inside the `MainContent` component's `<Routes>` block, alongside the existing analytics routes (`/flow`, `/outcomes`, `/compare`, `/conversations`). This ensures it follows the existing pattern — visible in analytics mode, hidden when `isStructureMode` is active.

### ReportsView Layout

**Top section — Generate Report cards**

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  Voice Daily Report  │  │  Customer Analytics  │  │  Monthly Insights   │
│                      │  │                      │  │                     │
│  Daily voice call    │  │  CSR handoff and     │  │  Monthly volume,    │
│  summary with per-   │  │  tool performance    │  │  intents, outcomes  │
│  call transcripts    │  │  breakdown           │  │  overview           │
│                      │  │                      │  │                     │
│  [Agent-level]       │  │  [Customer-level]    │  │  [Customer-level]   │
│                      │  │                      │  │                     │
│  [ Generate ]        │  │  [ Generate ]        │  │  [ Generate ]       │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

Clicking "Generate" expands a parameter panel below the card:
- Date range picker (date_from, date_to)
- Agent selector dropdown (if scope is "agent") — populated from structure API
- "Generate Report" button with loading state

**Bottom section — Generated Reports table**

| Report Type | Agent | Date Range | Generated By | Generated On | Download |
|------------|-------|------------|-------------|-------------|----------|
| Voice Daily | Ronnie2 | Mar 1-10, 2026 | craig@indemn.ai | Mar 12, 2026 | [Download] |
| Voice Daily | Ronnie2 | Feb 24 - Mar 9 | craig@indemn.ai | Mar 9, 2026 | [Download] |

- Filterable by report type and agent
- Sorted newest first
- Paginated
- Download button calls `/api/reports/{id}/download` and opens the pre-signed URL

### Frontend Files

New files:
- `frontend/src/pages/ReportsView.tsx` — main page component
- `frontend/src/components/reports/ReportTypeCard.tsx` — card with generate panel
- `frontend/src/components/reports/GeneratePanel.tsx` — parameter inputs + generate button
- `frontend/src/components/reports/ReportsTable.tsx` — generated reports list
- `frontend/src/hooks/useReportTypes.ts` — fetch available report types
- `frontend/src/hooks/useReports.ts` — fetch generated reports list
- `frontend/src/hooks/useGenerateReport.ts` — mutation hook for generation

Modified files:
- `frontend/src/components/layout/TabBar.tsx` — add Reports tab
- `frontend/src/App.tsx` — add /reports route
- `frontend/src/lib/api.ts` — add report API methods

### Scope Behavior

The Reports tab is visible inside `MainContent` alongside the other analytics tabs (Overview, Flow, Outcomes, Compare, Conversations). It follows the existing pattern: hidden when Structure mode is active, visible in analytics mode.

The Reports tab respects the user's identity for access control:
- **Customer logged in** → sees report types where their `org_id` is in `org_ids` (or `org_ids` is null). Sees only their generated reports.
- **Internal user, platform scope** → sees all report types and all generated reports. Can filter by org.
- **Internal user, customer scope** → sees report types for that customer (same as customer view, plus any internal-only types).

Auth is handled via `get_current_user` on the backend (not `ValidatedScope`). The frontend passes the user's token; the backend determines access based on the user's org memberships.

---

## Migration Plan

### Phase 1: CLI Reports Into the Hub

These already have Python extraction logic and JSX renderers. The extraction logic needs to be adapted (not just wrapped) — see notes below.

**Reports to migrate:**

| Report Type | Extractor | Renderer | Target Orgs |
|------------|-----------|----------|-------------|
| Voice Daily / Retrospective | `extract-voice-data.py` → `src/observatory/extractors/voice_data.py` | `generate-voice-report.jsx` | Rankin |
| Distinguished Programs Internal | New: `src/observatory/extractors/distinguished_internal.py` | `generate-distinguished-report.jsx` | Distinguished Programs |

**Extractor adaptation notes (voice_data):**
The existing `scripts/extract-voice-data.py` function differs from the new `extract()` interface in three ways that require new query logic, not just a wrapper:
1. **Date range:** Current function takes a single `date` and computes `next_day = date + timedelta(days=1)`. New interface takes `date_from`/`date_to` directly.
2. **Agent filtering:** Current function has no `agent_id` parameter. New interface adds optional agent filtering via `agents.id_bot` in the query.
3. **Org → Project resolution:** Current function takes `id_project` directly. New interface takes `org_id` and must resolve to project IDs by querying the `projects` collection where `id_organization` matches. An org can have multiple projects.

The core extraction logic (conversation processing, call reason classification, transcript formatting) stays the same — only the query setup changes.

**Steps:**
1. Create `src/observatory/extractors/` package with `__init__.py` and `registry.py`
2. Write `src/observatory/extractors/voice_data.py` — adapt extraction logic from `scripts/extract-voice-data.py` with date range, agent filtering, and org→project resolution
3. Write `src/observatory/extractors/distinguished_internal.py`
4. Create `scripts/package.json` with renderer Node dependencies (`@react-pdf/renderer`, `react`)
5. Create S3 bucket `indemn-observatory-reports`
6. Add `boto3` to Python `requirements.txt`
7. Add `S3Config` to `src/observatory/config.py`
8. Build reports router with all 7 endpoints (4 user + 3 admin)
9. Update Dockerfile: install Node.js, install renderer deps, copy font/logo assets
10. Build frontend Reports tab (TabBar, route, ReportsView, components, hooks, API methods)
11. Register report types in MongoDB via admin API
12. Upload existing PDFs from `/reports/` directory to S3, create catalog entries via admin API or migration script
13. Test: log in as Rankin → see Voice Daily → generate for a date range → download

### Phase 2: Client-side Reports Into the Hub

These currently render in-browser via React PDF. Each needs a Python extractor (porting the data fetching from React hooks) and a JSX renderer (porting the React PDF components to standalone scripts).

**Reports to migrate:**

| Report Type | Extract From | Render From | Target Orgs |
|------------|-------------|-------------|-------------|
| Monthly Customer Insights | `useReportData` hook → `src/observatory/extractors/monthly_insights.py` | `ReportDocument.tsx` → `generate-monthly-report.jsx` | All |
| Customer Analytics | `useCustomerReportData` hook → `src/observatory/extractors/customer_analytics.py` | `CustomerReportDocument.tsx` → `generate-customer-analytics.jsx` | All |
| Onboarding Guide | New extractor → `src/observatory/extractors/onboarding_guide.py` | `OnboardingGuideDocument.tsx` → `generate-onboarding-guide.jsx` | Per-org |

**Steps:**
1. For each report type: write Python extractor, create JSX renderer from existing components
2. Register in `report_types` collection
3. Verify each works through the hub (generate + download)
4. Remove `ReportButton.tsx` dropdown and associated hooks once all reports are migrated

---

## Skill Integration

The `/report-generate` skill workflow gains a final registration step:

1. **Build** — skill creates `src/observatory/extractors/{name}.py` and `scripts/generate-{name}.jsx`
2. **Test** — skill runs extraction + rendering locally to verify
3. **Register** — skill calls `POST /api/reports/types` with auth to register the new report type
4. **Done** — report is immediately available in the hub

The admin API endpoint requires platform-level auth. The skill runs in sessions with internal user credentials, so this works naturally.

The `/report-library` skill stays as-is — it provides brand system reference, component patterns, and templates for building new reports.

---

## S3 Configuration

**Bucket:** `indemn-observatory-reports`
**Region:** Same as existing AWS resources (us-east-1)
**Key pattern:** `reports/{org_id}/{report_type_slug}/{agent_id}/{date_from}_{date_to}.pdf`
- `agent_id` is `_none` for org-level reports

**Access:**
- Backend uses boto3 with credentials from `aws-env-loader.sh` (already runs at deploy time)
- Pre-signed URLs for downloads (configurable expiry, default 15 min)
- No public access to the bucket

**Lifecycle (future):** Consider S3 lifecycle rules to archive old reports to Glacier after N months.

---

## Deployment Considerations

### Node.js in the Backend Docker Image

The backend Dockerfile currently builds from `python:3.12-slim` — no Node.js runtime. The frontend is a separate container (`node:20-alpine` → nginx). These are composed via `docker-compose.yml`.

**Solution:** Install Node.js in the backend Docker image. Add to `Dockerfile`:

```dockerfile
# Install Node.js for report PDF rendering
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
```

Then install the renderer's Node dependencies in the image:

```dockerfile
# Install Node dependencies for report renderers
# WORKDIR is /app, so scripts/ is at /app/scripts/
COPY scripts/package.json scripts/package-lock.json ./scripts/
RUN cd scripts && npm ci --production

# Copy font files so renderers can find them via __dirname-relative paths
# Renderers resolve fonts via: path.join(__dirname, '..', 'frontend', 'public', 'fonts')
COPY frontend/public/fonts/ ./frontend/public/fonts/
COPY frontend/src/assets/brand/ ./frontend/src/assets/brand/
```

This requires creating a `scripts/package.json` with the renderer dependencies (at minimum: `@react-pdf/renderer`, `react`). The `NODE_PATH` env var in the subprocess call points to `/app/scripts/node_modules`.

**Path consistency:** The Dockerfile WORKDIR is `/app`. All paths in the subprocess call use `/app/` as the base. The renderers resolve font and logo paths relative to `__dirname` (e.g., `path.join(__dirname, '..', 'frontend', 'public', 'fonts')`) which resolves to `/app/frontend/public/fonts/` — the Dockerfile copies these files to match.

**Image size impact:** ~150MB for Node.js runtime + dependencies. Acceptable for a self-hosted deploy.

**Alternative considered:** Sidecar Node container or multi-stage build. Rejected as over-engineering for the current scale.

### Other Deployment Notes

- **boto3 dependency:** Add to `requirements.txt`. AWS credentials flow via `aws-env-loader.sh` (already runs at container startup).
- **S3 bucket creation:** One-time setup via AWS CLI or console. Add to deploy checklist.
- **Temp file cleanup:** Generation writes to `/tmp/` with UUID-based filenames. Cleanup happens in a `finally` block — both the JSON and PDF temp files are deleted after S3 upload (or on error).
- **Renderer fonts:** The JSX renderers register Barlow font files from absolute paths. These font files (TTF) must be included in the Docker image. Copy from `frontend/public/fonts/` during build.
- **Timeout:** Generation is synchronous. Ensure nginx proxy timeout (if applicable) is set to at least 120 seconds for the `/api/reports/generate` endpoint. Frontend `fetch` should use a matching timeout with a loading indicator.
- **`.env.example`:** Update with new env vars: `S3_REPORT_BUCKET`, `AWS_REGION`, `S3_PRESIGN_EXPIRY`.

---

## Review Issues Addressed

Issues identified during two rounds of design review and their resolutions:

### Round 1

| # | Issue | Severity | Resolution |
|---|-------|----------|------------|
| 1 | Extractors use sync pymongo; API uses async Motor — incompatible `db` parameter | Blocking | Extractors stay synchronous, take `mongodb_uri` string, create own pymongo connection. API calls via `asyncio.to_thread()`. |
| 2 | No Node.js in backend Docker image (`python:3.12-slim`) | Blocking | Install Node.js 20.x in backend Dockerfile. Create `scripts/package.json` for renderer deps. |
| 3 | No boto3 or S3 config in codebase | Blocking | Add boto3 to requirements.txt. Add `S3Config` dataclass to config.py with env vars. |
| 4 | `ValidatedScope` reads query params; generate endpoint uses POST body | Important | Use `get_current_user` with custom org access checks instead of `ValidatedScope`. |
| 5 | Report types need `org_ids` array membership filter, not scope hierarchy | Important | Use `get_current_user` and build MongoDB filter directly on `org_ids` field. |
| 6 | S3 key missing `agent_id` — collisions for same date range across agents | Important | Include `agent_id` (or `_none`) in S3 key pattern. Add agent_id to dedup index. |
| 7 | Regeneration creates duplicate catalog entries | Important | Upsert on compound key (type + org + agent + dates). Only latest version exists. |
| 8 | Reports tab visibility in Structure mode | Important | Follows existing pattern — hidden in Structure mode, visible in analytics mode. |
| 9 | No error response schema | Suggestion | Added error response table with status codes and error codes. |
| 10 | Missing `.env.example` update | Suggestion | Documented in deployment notes. |
| 11 | Temp file cleanup not specified | Suggestion | Added `finally` block cleanup in generation flow code example. |
| 12 | No timeout consideration | Suggestion | Added nginx proxy timeout and frontend fetch timeout guidance. |

### Round 2

| # | Issue | Severity | Resolution |
|---|-------|----------|------------|
| 13 | `scripts/extractors/` not importable from API — `scripts/` is not a Python package and not on `sys.path` | Blocking | Moved extractors to `src/observatory/extractors/` — proper Python package, importable via standard imports. Dynamic registry via `importlib` for slug-based lookup. |
| 14 | Extractor function signature doesn't match existing CLI script — single date vs range, no agent_id, uses `id_project` not `org_id` | Blocking | Documented as adaptation, not wrapper. New `extract()` interface has date range + agent filtering + org→project resolution. Core extraction logic reused, query setup rewritten. |
| 15 | NODE_PATH uses `/opt/observatory/` but Dockerfile WORKDIR is `/app` | Important | All paths normalized to `/app/` base. `NODE_PATH=/app/scripts/node_modules`, `cwd=/app` in subprocess. Dockerfile copies fonts/logos to match `__dirname`-relative paths. |
| 16 | Design references `config.mongodb_uri` but actual path is `config.mongodb.uri` | Important | Fixed to `config.mongodb.uri` in all code examples. |
| 17 | `requests` collection uses `id_project` (Tiledesk project ID), not `org_id` — extractors must resolve org→project IDs | Important | Extractors query `projects` collection for `id_organization` match to get project IDs, then filter `requests` by `id_project: {$in: project_ids}`. Documented in extractor code example. |

### Round 3

| # | Issue | Severity | Resolution |
|---|-------|----------|------------|
| 18 | Design uses `from src.observatory.extractors` but codebase uses relative imports exclusively | Important | Router uses `from ...extractors import get_extractor` (relative). Registry uses `import_module(".{slug}", package="src.observatory.extractors")`. |
| 19 | Extractor example queries `"channel"` but actual field is `"attributes.channel"` — would return zero results | Important | Fixed to `"attributes.channel": "VOICE"` matching the existing script's query pattern. |
| 20 | `pymongo` not explicitly in `requirements.txt` — only transitive via `motor` | Important | Added `pymongo` as an explicit dependency alongside `boto3`. |

---

## What's NOT in Scope

- Scheduled / automated report generation (cron-style)
- Email delivery of reports
- Report versioning or history (regenerating replaces for the same params)
- Admin UI for managing report types (API-only for now)
- Async generation / job queue (synchronous is fine to start)
- Report sharing links (pre-signed URLs are ephemeral by design)
