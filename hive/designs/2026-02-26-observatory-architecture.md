---
title: What is the Indemn Observatory and how is it built?
tags:
- design
- architecture
domains:
- indemn
refs:
  project: gic-observatory
status: active
created: '2026-02-26'
---

# What is the Indemn Observatory and how is it built?

# Indemn Observatory Architecture

## Overview

The Indemn Observatory is an analytics platform for AI chatbot conversations in insurance. Its core innovation is **outcome-driven precursor analysis** — it discovers which factors statistically predict specific outcomes using lift factors:

```
lift = P(Factor | Outcome) / P(Factor | all conversations)
```

Factors with lift > 1.5 are precursors. Example: "Conversations with negative sentiment are 3.2x more likely to end in missed_handoff."

**Production URL**: https://indemn-observability.vercel.app
**Local repo**: `/Users/home/Repositories/indemn-observability/`

## Three Integrated Experiences

| Experience | Question | Use |
|------------|----------|-----|
| **Structure** | What exists? | Org/agent/tool/KB architecture diagram |
| **Behavior** | What happens? | Flows, patterns, distributions |
| **Investigation** | Why specifically? | Individual conversation traces |

## Scope Hierarchy

```
Platform (Indemn)
  └── Customer (Organization — e.g., GIC)
      └── Agent (channel: webchat | voice | email)
```

All analytics respect the current scope. Customers see only their own data.

## Technology Stack

### Frontend
- **React 19** + TypeScript + Vite
- **@react-pdf/renderer v4.3.2** — PDF generation in browser
- **TanStack Query** — Data fetching
- **Recharts** — Visualization (Sankey, charts)
- **shadcn/ui** — Components
- **Tailwind CSS** — Styling
- Dev server: port 5175

### Backend
- **Python 3.10+** with **FastAPI**
- **Motor** — Async MongoDB driver
- **Pydantic v2** — Validation
- **LangChain** ecosystem for LLM classification (Claude Haiku)
- Port 8004

### Database
- **MongoDB Atlas** — `tiledesk` database (11.4 GB)
- Source collections: `organizations`, `bot_configurations`, `requests`, `messages`, etc.
- Observatory collections: `observatory_conversations`, `daily_snapshots`, `precursor_lifts`, `flow_paths`, etc.

## Data Flow

```
requests (source)  ──→  Ingestion Pipeline  ──→  observatory_conversations
LangSmith traces   ──→  (classify + derive)  ──→  daily_snapshots
                                              ──→  precursor_lifts
                                              ──→  flow_paths
```

### Ingestion Pipeline (3 steps)

1. **Sync Traces**: `POST /api/admin/sync-traces` — Fetches from LangSmith → `traces` collection
2. **Ingest Conversations**: `POST /api/admin/ingest` — Reads `requests`, joins traces, runs LLM classification → `observatory_conversations`
3. **Compute Aggregations**: `POST /api/admin/aggregate` — Computes daily snapshots, distributions, precursors, flows

## Key Backend Files

| File | Purpose |
|------|---------|
| `src/observatory/api/main.py` | FastAPI app entry |
| `src/observatory/api/data_access.py` | DataStore abstraction (JSON dev / MongoDB prod) |
| `src/observatory/api/routers/aggregations.py` | Snapshots, distributions, precursors, CSR metrics |
| `src/observatory/api/routers/conversations.py` | Paginated list + trace details |
| `src/observatory/pipeline.py` | Main ingestion logic |
| `src/observatory/aggregations.py` | Aggregation engine (snapshots, distributions, precursors, flows) |
| `src/observatory/classify.py` | LLM classification (Claude Haiku) |
| `src/observatory/derivations.py` | Outcome/stage derivation |
| `src/observatory/ingestion/connectors/mongodb.py` | MongoDB source connector |

## Key Frontend Files

| File | Purpose |
|------|---------|
| `frontend/src/App.tsx` | Main router |
| `frontend/src/components/report/` | All PDF report components (25+ files) |
| `frontend/src/components/overview/ReportButton.tsx` | Export/Download dropdown menu |
| `frontend/src/hooks/useReportData.ts` | Monthly Insights data aggregation |
| `frontend/src/hooks/useCustomerReportData.ts` | Customer Analytics data aggregation |
| `frontend/src/lib/generateReport.tsx` | PDF generation utility |
| `frontend/src/components/report/styles.ts` | Brand colors, typography, layouts |

## Export/Download Button

The ReportButton dropdown offers:
1. **Export Data (CSV)** — Flattened snapshot metrics
2. **Export Data (JSON)** — Raw snapshot structure
3. **Monthly Report (PDF)** — 5-7 page insights report
4. **Customer Analytics (PDF)** — Operational report (handoff, CSR, tools) ← **THIS is the one GIC uses**

## API Routers

| Router | Key Endpoints |
|--------|--------------|
| `aggregations.py` | `/api/aggregations/snapshots`, `/distributions`, `/precursors`, `/csr-metrics` |
| `conversations.py` | `/api/conversations`, `/api/conversations/{id}` |
| `flows.py` | `/api/aggregations/flows`, `/flows/cohort` |
| `metadata.py` | `/api/metadata`, `/api/metadata/quality` |
| `structure.py` | `/api/structure/platform`, `/customer/{id}`, `/agent/{id}` |
| `admin.py` | `/api/admin/ingest`, `/aggregate`, `/jobs` |

## Outcome Classification

| Outcome | Group | Description |
|---------|-------|-------------|
| `resolved_autonomous` | success | Resolved by AI alone |
| `resolved_with_handoff` | success | Resolved after human handoff |
| `partial_then_left` | partial | Partially addressed, user left |
| `unresolved_abandoned` | failure | User abandoned |
| `unresolved_timeout` | failure | Timed out |
| `missed_handoff` | failure | Handoff requested but not completed |

## Environment Variables

```bash
MONGODB_URI=mongodb+srv://...       # Atlas connection
LANGSMITH_API_KEY=lsv2_pt_...       # Trace syncing
ANTHROPIC_API_KEY=sk-ant-...        # Claude classification
AUTH_ENABLED=true|demo|false
JWT_SECRET=...
```

## Running Locally

```bash
# Backend
source venv/bin/activate
uvicorn src.observatory.api.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev  # port 5173
```
