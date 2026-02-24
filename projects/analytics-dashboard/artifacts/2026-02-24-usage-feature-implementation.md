---
ask: "Implement the usage analytics feature end-to-end — backend, frontend, MongoDB index"
created: 2026-02-24
workstream: analytics-dashboard
session: 2026-02-24-c
sources:
  - type: mongodb
    description: "Created idx_billing_usage compound index on production tiledesk.requests; verified 3 scope-level aggregation pipelines return correct data"
  - type: github
    description: "Implemented across 14 files in indemn-observability repo — 6 new, 8 modified"
  - type: linear
    description: "COP-326 — implementation complete, needs data validation"
---

# Usage Feature Implementation — Session Summary

## What Was Built

Full implementation of the Usage Analytics feature across backend and frontend of indemn-observability.

### Backend (Python/FastAPI)

| File | What |
|------|------|
| `src/observatory/api/models/usage.py` | Pydantic models: `UsageRange`, `UsageRow`, `UsageResponse` |
| `src/observatory/api/routers/usage.py` | FastAPI router: `GET /api/aggregations/usage` with ValidatedScope auth |
| `src/observatory/api/data_access.py` | +350 lines: abstract method, JSONFileDataStore stub, MongoDBDataStore with 3 aggregation pipelines |
| `src/observatory/api/main.py` | Router registration |
| `src/observatory/api/models/__init__.py` | Model re-exports |
| `src/observatory/api/routers/__init__.py` | Module export |

### Frontend (React/TypeScript)

| File | What |
|------|------|
| `frontend/src/types/api.ts` | `UsageResponse`, `UsageRow` interfaces |
| `frontend/src/lib/api.ts` | `getUsage()` API client method |
| `frontend/src/hooks/useUsage.ts` | `useUsage()` + `useUsageExpansion()` TanStack Query hooks |
| `frontend/src/components/overview/UsageTableRow.tsx` | Row component — number formatting, zero-dashes, Unattributed styling |
| `frontend/src/components/overview/UsageTable.tsx` | Table with expand/collapse, lazy agent loading, bucket header formatting |
| `frontend/src/components/overview/UsageSection.tsx` | Wrapper — date label, loading/error states, 6-month default at platform scope |
| `frontend/src/components/overview/CategoryTabs.tsx` | Added "usage" as first MetricCategory, grid-cols-7 |
| `frontend/src/components/overview/OverviewView.tsx` | Default to "usage" tab, render UsageSection independent of snapshot loading |
| `frontend/src/components/ui/date-range-picker.tsx` | Added "Last 6 months" (183 days) preset |

### MongoDB

- Created `idx_billing_usage` compound index on production `tiledesk.requests`: `{status: 1, isTestMode: 1, createdAt: 1, id_organization: 1, depth: 1}`

## What Was Verified

### API Endpoint Testing (all 3 scopes)

- **Platform scope** (`/api/aggregations/usage?scope_level=platform&date_from=2025-09-01&date_to=2026-02-24`): 15 orgs returned, GIC Underwriters at 9,115, EventGuard at 8,283. Test orgs excluded. Monthly bucketing.
- **Customer scope** (`scope_level=customer&customer_id=65eb3f19e5e6de0013fda310`): Agent breakdown for GIC — Unattributed (4,925), GIC Underwriters Inc bot (4,178), plus 3 smaller agents. Totals match org-level.
- **Agent scope** (`scope_level=agent&agent_id=66026a302af0870013103b1e`): Single row for GIC bot, 4,178 total.
- **Weekly granularity** (Feb 1–24 range): Correct ISO week bucketing (W05–W09).

### Build Verification

- Python syntax: All new files parse OK
- TypeScript: `tsc --noEmit` passes
- Vite build: Succeeds (4,239 modules)

### UI Verification (screenshot)

The feature renders correctly:
- Usage is the default/first tab on Overview
- Table shows all orgs sorted by total desc
- Expand/collapse works — clicking GIC shows agent sub-rows
- Unattributed row renders in italic
- Numbers formatted with commas, zeros show dashes
- Monthly column headers formatted ("Sep 2025", etc.)

## Bug Fixed During Implementation

**`$toObjectId` failure on `__unattributed__` sentinel value.** The `$lookup` pipeline in the customer scope aggregation used `$toObjectId` to convert participantsBots strings to ObjectIds for matching against `faq_kbs._id`. But `__unattributed__` (the sentinel for conversations without bots) would cause `$toObjectId` to throw. Fixed by using `$convert` with `onError: null` — gracefully returns null for non-ObjectId strings, which won't match any `faq_kbs._id`.

## Known Issues for Next Session

### 1. Data Numbers Don't Match Research Artifact

The screenshot shows GIC at **9,510** but the research artifact expected **~9,102**. This is because:
- The 6-month default computes 183 days back from today (Feb 24), landing on **Aug 25** — not Sep 1
- The partial August column adds ~395 conversations to GIC's total
- All other orgs similarly inflated by the Aug partial

**Root cause**: The "Last 6 months" preset uses 183 days, which doesn't align to month boundaries. The research artifact used Sep 1–Feb 24 (clean month start).

**Options to consider next session:**
- a) Change the default to compute from the 1st of (current month - 6) — clean month boundary
- b) Keep 183 days but accept the partial month (it's correct data, just includes a few extra days)
- c) Add a "Last 6 full months" preset that snaps to month boundaries

### 2. Unattributed Row is #1 for GIC

Unattributed conversations (5,136) outnumber the main GIC bot (4,361). This is the ~54% unattributed rate for GIC — higher than the platform average of 22%. This is real data, not a bug, but may confuse Kyle. Consider:
- Moving Unattributed to the bottom of the expansion (after named agents)
- Adding a tooltip explaining what "Unattributed" means
- Investigating why GIC has such high unattributed rate (possible widget config issue?)

### 3. Org-Level Totals Include Partial Data

The org-level total (9,510) is the sum of ALL conversations in the date range. The agent drill-down sums to the same (5,136 + 4,361 + 9 + 3 + 1 = 9,510). This is correct and consistent, but the partial August may confuse users expecting round month boundaries.

### 4. No Git Commit Yet

All changes are uncommitted in the indemn-observability repo. Need to commit before any other work happens there.

### 5. Frontend .env.local Created

Created `frontend/.env.local` with `VITE_API_BASE=http://localhost:8004` for local testing. This is gitignored and only affects local dev.

## Local Dev Notes

- Backend started with: `cd indemn-observability && source .env && source venv/bin/activate && uvicorn src.observatory.api.main:app --reload --port 8004`
- Frontend started with: `cd indemn-observability/frontend && npm run dev -- --port 5175`
- The `local-dev.sh start analytics --env=prod` fails MongoDB validation but the services work fine when started directly
- Auth must be enabled for proper testing; auth-disabled mode used only for curl verification
