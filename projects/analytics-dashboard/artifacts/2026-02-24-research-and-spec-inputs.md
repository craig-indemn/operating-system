---
ask: "What data, architecture, and design inputs do we need to spec the Observatory usage analytics feature?"
created: 2026-02-24
workstream: analytics-dashboard
session: 2026-02-24-a
sources:
  - type: mongodb
    description: "Queried requests, stripe_meters, organizations, faq_kbs, daily_snapshots, observatory_conversations in tiledesk database"
  - type: github
    description: "Explored indemn-observability repo — architecture, overview page, ETL, API, types"
  - type: linear
    description: "Created COP-326 — assigned to Craig, In Progress, Cycle 73"
---

# Research & Spec Inputs for Observatory Usage Analytics

## 1. The Billing-Aligned Usage Filter

To get conversation counts that match Stripe billing, apply this filter to the `requests` collection:

```javascript
{
  status: 1000,              // closed conversations only
  isTestMode: { $ne: true }, // exclude test mode
  depth: { $gt: 2 }          // more than 2 messages
}
```

- Verified 2026-02-24 against `stripe_meters` collection — matches within 1-2% (timing differences at month boundaries)
- `stripe_meters` has two meter types: `chat_conv_count` and `voice_duration_minutes`
- This filter is now documented in the MongoDB skill at `references/query-patterns.md`

### Test/Internal Orgs to Exclude

| Org | ID | Reason |
|-----|-----|--------|
| Indemn | `65e18047b26fd2526e096cd0` | Internal |
| Demos | `66c0920c358d3f001351c22c` | Demo showcase (50+ bots) |
| Voice Demos | `66d196e9cc5cd70013e46565` | Voice prototypes |
| test-dolly-prod | `66fc8ab493b5a40013596cd7` | Test account |
| InsuranceTrak | `65e60f70683d12001386515a` | Legacy test |

EventGuard is NOT a test org — it's a real customer (Jewelers Mutual product).

## 2. Verified Usage Data (Sep 2025 - Feb 2026)

### Organizations — Billable Usage

| Organization | Sep | Oct | Nov | Dec | Jan | Feb* | Total |
|---|---|---|---|---|---|---|---|
| GIC Underwriters | 1,478 | 1,761 | 1,290 | 1,375 | 1,835 | 1,363 | 9,102 |
| EventGuard | 964 | 3,796 | 648 | 651 | 1,315 | 906 | 8,280 |
| Open Enrolment | — | 313 | 213 | 109 | 216 | 9 | 860 |
| Bonzah | 84 | 85 | 81 | 71 | 126 | 47 | 494 |
| Insurica | 92 | 113 | 8 | 5 | 5 | — | 223 |
| Family First | — | — | 41 | 18 | 135 | — | 194 |
| Distinguished | 11 | 141 | 14 | 7 | 13 | 5 | 191 |
| Rankin Insurance | — | — | — | — | 45 | 132 | 177 |
| Loro | — | — | — | 11 | 67 | 59 | 137 |
| Especialty | 7 | 9 | 13 | 4 | 7 | 5 | 45 |
| Tillman Insurance | — | — | — | — | 6 | 22 | 28 |
| Union General | 3 | 7 | 2 | 3 | 3 | 9 | 27 |
| O'Connor Insurance | — | — | — | — | 18 | 3 | 21 |

*Feb partial through 2/24

### Agents — Billable Usage (Top 15)

| Agent | Org | Sep | Oct | Nov | Dec | Jan | Feb* | Total |
|---|---|---|---|---|---|---|---|---|
| Wedding SAAS AI Agent | EventGuard | 934 | 3,761 | 619 | 638 | 1,280 | 894 | 8,126 |
| GIC Underwriters Inc | GIC | 765 | 421 | 641 | 762 | 935 | 651 | 4,175 |
| Gabby Renter | Bonzah | 78 | 81 | 79 | 70 | 119 | 45 | 472 |
| Riley (Front Door) | Open Enrolment | — | 152 | 69 | 67 | 40 | 9 | 337 |
| Riley (Front Door) DEV | Open Enrolment | — | — | 54 | 17 | 176 | — | 247 |
| Riley (Transfer In) | Open Enrolment | — | 161 | 49 | 1 | — | — | 211 |
| Go-live Candidate | Family First | — | — | 40 | — | 135 | — | 175 |
| Ronnie2 | Rankin | — | — | — | — | 30 | 115 | 145 |
| FAQ Bot | Loro | — | — | — | 11 | 67 | 59 | 137 |
| Riley (Front Door) | Insurica | 46 | 71 | — | — | — | — | 117 |
| Internal AI Agent v2 | Distinguished | — | 113 | — | — | — | — | 113 |
| Riley (Transfer In) | Insurica | 44 | 39 | — | — | — | — | 83 |
| Internal User Asst | Distinguished | 11 | 28 | 14 | 4 | 11 | 1 | 69 |
| eSpecialty AI CSR | Especialty | 7 | 9 | 10 | 4 | 7 | 5 | 42 |
| EventGuard Affinity | EventGuard | 6 | 9 | 10 | 3 | 4 | — | 32 |

## 3. Observatory Architecture (Key Facts for Spec)

### Stack
- **Frontend**: React 19, TypeScript, Vite (port 5173), Tailwind, shadcn/ui, Recharts
- **Backend**: Python FastAPI, async Motor (MongoDB), Uvicorn (port 8000)
- **Database**: MongoDB Atlas — `tiledesk` (source) + `observatory` (analytics)

### Overview Page Structure
- File: `frontend/src/components/overview/OverviewView.tsx`
- 6 hero KPI tiles with period-over-period deltas
- Category tabs: outcomes, volume, experience, operations, performance, content
- Charts: OutcomeChart, TrendChart, VolumeCharts (all Recharts)
- Data hook: `useSnapshots()` → `/api/aggregations/snapshots`

### Scope System
- Three levels: platform → customer → agent
- Controlled by ScopeContext provider
- Date range selector at top of page drives all queries
- All API endpoints accept scope + date range parameters

### Data Flow
```
MongoDB (tiledesk) → ETL (admin endpoints) → observatory collections → API endpoints → React hooks → UI
```

### Key API Endpoints
- `GET /api/aggregations/snapshots` — daily KPIs by scope + date range
- `GET /api/aggregations/distributions` — value distributions for charts
- `GET /api/structure/platform` — all orgs with agent/tool/KB counts
- `GET /api/structure/customer/{id}` — agents for one org
- `POST /api/admin/ingest` — process conversations
- `POST /api/admin/aggregate` — compute snapshots

### Data Coverage Gap
- `daily_snapshots` and `observatory_conversations`: Jan 5, 2026+ only
- `requests` collection: full history (142K+ docs)
- For Sep-Dec 2025, only raw request data available (no outcomes, sentiment, performance)

## 4. Open Design Questions for Spec Session

1. **Date range interaction** — The overview page has a date range selector at the top. The usage table should be driven by this. How should months be bucketed? Does the selected range determine which months appear as columns? What happens for partial months?

2. **Where in the UI** — New section on the existing overview page? A new tab? A separate "Usage" view?

3. **Data source strategy** — New API endpoint querying `requests` directly with the billing filter? Or extend the daily_snapshots pipeline? Pre-compute monthly aggregates as a new collection?

4. **Agent drill-down** — Click an org row to expand and see per-agent breakdown? Or separate table?

5. **Metrics beyond conversations** — Just conversation count? Or also unique users, avg depth, avg duration?

6. **Scope interaction** — At platform level, show all orgs. When scoped to a customer, show their agents. When scoped to an agent, show... monthly trend only?

## 5. GIC Discrepancy Explained

GIC org total (13,177 raw) vs GIC bot (8,233 raw):
- 4,923 conversations had `hasBot: false` (human-only, no bot participated)
- After billing filter (status=1000, depth>2, isTestMode!=true): 9,102 org-level
- After billing filter, bot-only: 4,175 (GIC Underwriters Inc bot)
- The gap between 9,102 and 4,175 = ~4,927 human-handled conversations that are still billable
