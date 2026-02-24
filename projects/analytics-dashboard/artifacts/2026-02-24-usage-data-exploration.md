---
ask: "What does the tiledesk MongoDB data look like for org/agent usage over the last 6 months, and how does the Observatory currently work?"
created: 2026-02-24
workstream: analytics-dashboard
session: 2026-02-24-a
sources:
  - type: mongodb
    description: "Queried requests, organizations, faq_kbs, daily_snapshots, observatory_conversations collections in tiledesk database"
  - type: github
    description: "Explored indemn-observability repo — architecture, ETL, overview page, data models"
---

# Usage Data Exploration & Observatory Architecture

## Observatory Architecture

- **Frontend**: React 19 + TypeScript, Vite (port 5173), Tailwind, shadcn/ui, Recharts
- **Backend**: Python FastAPI + async Motor (MongoDB), Uvicorn (port 8000)
- **Overview page**: `frontend/src/components/overview/OverviewView.tsx` — 6 hero KPIs, category tabs, outcome/trend/volume charts
- **Data flow**: MongoDB raw → ETL (ingest/classify/aggregate) → `daily_snapshots` → `/api/aggregations/snapshots` → `useSnapshots()` hook
- **Key insight**: Current overview is single-scope (platform OR one customer OR one agent). No multi-org comparison or monthly breakdown table exists.

## Platform Usage Data (Sep 2025 - Feb 2026)

| Month | Conversations | Active Orgs | Top Org |
|-------|-------------|------------|---------|
| Sep 2025 | 5,601 | 16 | GIC (1,833) |
| Oct 2025 | 12,694 | 17 | EventGuard (6,672) |
| Nov 2025 | 5,028 | 18 | GIC (1,935) |
| Dec 2025 | 4,716 | 18 | GIC (2,052) |
| Jan 2026 | 7,423 | 25 | GIC (2,663) |
| Feb 2026* | 4,948 | 19 | GIC (2,049) |

*partial through Feb 24

## Top Organizations (6-month totals)

1. **GIC Underwriters**: ~13,165 — consistently highest
2. **EventGuard**: ~12,299 — massive Oct spike (6,672), otherwise 750-1,700
3. **Indemn** (internal): ~7,828
4. **Family First**: ~1,172
5. **Bonzah**: ~1,069
6. **Open Enrolment**: ~1,035
7. **Distinguished**: ~758

## Growing Customers

- **Rankin Insurance**: 0 → 0 → 0 → 2 → 176 → 243 (new, growing fast)
- **Loro**: 15 → 1 → 3 → 37 → 177 → 89 (significant ramp)
- **Union General**: 19 → 28 → 15 → 10 → 25 → 142 (Feb spike)
- **Tillman Insurance**: new Dec → 4 → 64 → 57

## Top Bots by Volume

| Bot | Org | 6-mo Total |
|-----|-----|-----------|
| GIC Underwriters Inc | GIC | ~8,226 |
| EventGuard main | EventGuard | ~11,949 |
| Indemn primary | Indemn | ~7,288 |
| Family First bot | Family First | ~902 |
| Gabby Original | Bonzah | ~963 |

## Data Coverage Gap

- `daily_snapshots`: Jan 5, 2026+ only (553 docs in tiledesk)
- `observatory_conversations`: Jan 5, 2026+ only (9,058 docs)
- `requests`: Full history available (142,849 total docs)
- **Implication**: For Sep-Dec 2025, we can only get conversation counts, bot participation, and depth from raw requests. No outcomes, sentiment, or performance metrics.

## Key Collections for This Feature

1. **requests** — conversation-level: createdAt, hasBot, participantsBots, id_organization, depth, status, channel
2. **organizations** — org names, active status
3. **faq_kbs** — bot names, org mapping, type, channels
4. **daily_snapshots** — pre-aggregated KPIs (Jan 2026+ only)

## Observatory API Patterns

- All queries respect scope hierarchy: platform → customer → agent
- Endpoints: `/api/aggregations/snapshots`, `/api/aggregations/distributions`, `/api/structure/*`
- Admin endpoints for ETL: `/api/admin/ingest`, `/api/admin/aggregate`
- Auth via scope context (platform-level = Indemn employees only)
