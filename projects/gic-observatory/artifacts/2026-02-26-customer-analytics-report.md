---
ask: "How does the current Customer Analytics PDF report work and what does it contain?"
created: 2026-02-26
workstream: gic-observatory
session: 2026-02-26-a
sources:
  - type: codebase
    description: "CustomerReportDocument.tsx, useCustomerReportData.ts, ReportCSRBreakdownPage.tsx, ReportHandoffPage.tsx, ReportToolAnalysisPage.tsx, generateReport.tsx"
  - type: codebase
    ref: "/Users/home/Repositories/indemn-observability/frontend/src/components/report/"
    name: "Report component directory"
---

# Customer Analytics Report — Current State

The Customer Analytics Report is the PDF that GIC Underwriters download from the Observatory. It's an operational-focused report covering handoff performance, CSR activity, and tool analysis.

## How It's Generated

### Frontend (Production — Browser Download)

1. User clicks "Customer Analytics (PDF)" in the Export dropdown (`ReportButton.tsx`)
2. `useCustomerReportData()` hook fetches data from API
3. `generateReport()` utility creates PDF using `@react-pdf/renderer`
4. Browser downloads: `Indemn_Customer_Analytics_{OrgName}_{Month}_{Year}.pdf`

**Key files:**
- `frontend/src/components/overview/ReportButton.tsx` — Export menu trigger
- `frontend/src/hooks/useCustomerReportData.ts` — Data aggregation hook
- `frontend/src/lib/generateReport.tsx` — PDF generation (`pdf()` from @react-pdf/renderer)
- `frontend/src/components/report/CustomerReportDocument.tsx` — Report wrapper

### CLI (Ad-hoc Reports)

Two-file pattern in `scripts/`:
1. **Extraction script** (Python): Queries MongoDB, outputs JSON to `data/`
2. **Renderer script** (Node.js/JSX): Reads JSON, generates PDF to `reports/`

```bash
python scripts/extract-{name}.py --org gic --date-from 2026-02-01 --date-to 2026-02-28
NODE_PATH=frontend/node_modules node scripts/generate-{name}.jsx data/{name}.json
```

See `/report-generate` and `/report-library` skills for full workflow.

## Report Pages

### Page 1: Cover
- Indemn logo, report title, organization name, date range
- **Highlights box**: Total conversations, handoff requests (count + %), active CSRs, policy check success rate
- Conversations with < 3 messages are excluded (noise filter); excluded count shown

### Page 2: Handoff Performance (`ReportHandoffPage.tsx`)
- Total handoff requests
- Median CSR join time (seconds from handoff request to CSR joining)
- Missed handoff percentage
- Completed handoff percentage
- **Root cause analysis**: Why handoffs were missed (out of hours, no CSR available, etc.)
- **Join time comparison**: By engagement type (direct vs. after bot)

### Page 3: CSR Breakdown (`ReportCSRBreakdownPage.tsx`)
Per-CSR table with columns:
| Column | Description |
|--------|-------------|
| CSR Name | From `senderFullname` in messages |
| Chat Count | Number of conversations handled |
| Median Join Time | Seconds from handoff request to CSR joining |
| Median Response Time | Seconds between user message and CSR reply |
| Resolved Handoff % | Percentage of conversations CSR resolved |
| Median Message Count | Median messages CSR sent per conversation |

**This is the page GIC wants to augment with time-of-day distribution.**

### Page 4: Tool Analysis (`ReportToolAnalysisPage.tsx`)
- Tool success/failure/error rates (e.g., policy check tool)
- Outcome correlation by tool result
- System tag `missing_backend_data` distinguishes policy-not-found vs API error

## Data Sources

### API Endpoint: `/api/aggregations/csr-metrics`

**Response shape:**
```typescript
interface CSRMetricsResponse {
  csr_metrics: CSRMetric[];
  total_handoff_requests: number;
  total_missed_handoffs: number;
  total_out_of_hours_handoffs: number;
  median_join_time_seconds: number | null;
  handoff_root_causes: HandoffRootCauses | null;
  join_time_by_engagement: JoinTimeByEngagement | null;
}

interface CSRMetric {
  csr_name: string;
  chat_count: number;
  median_join_time_seconds: number | null;
  median_message_response_time_seconds: number | null;
  resolved_handoff_pct: number;
  median_message_count: number | null;
}
```

### Data Hook: `useCustomerReportData()`

Fetches:
- Conversations from `/api/conversations` (with scope filter)
- CSR metrics from `/api/aggregations/csr-metrics`
- Snapshots from `/api/aggregations/snapshots`

Filters:
- Organization scope (GIC)
- Date range
- Excludes conversations with < 3 messages

## What GIC Wants Added

**Request**: Time-of-day distribution showing:
1. When chats/interactions happen throughout the day
2. When individual CSRs are responding to questions
3. 20-minute interval buckets across 24 hours (72 buckets total)
4. A graph showing which CSRs were active in each period and how many chats they handled

**What this means technically:**
- Query `messages` collection for CSR response timestamps
- Bucket by 20-minute intervals: 00:00-00:19, 00:20-00:39, 00:40-00:59, 01:00-01:19, ...
- Group by CSR name
- Display as a visualization (heatmap, stacked bars, or line chart)
- Add as new page(s) in the Customer Analytics PDF

## Existing Hourly Data

The system already computes `by_hour` (0-23) in daily snapshots for conversation start times. This is a coarser granularity (hourly) and only tracks conversation starts, not individual CSR message responses. The new feature needs:
- 20-minute granularity (not hourly)
- CSR message timestamps (not conversation start times)
- Per-CSR breakdown (not aggregate)

## Brand System Reference

| Element | Value |
|---------|-------|
| Primary color | IRIS `#4752a3` |
| Secondary | LILAC `#a67cb7` |
| Dark | EGGPLANT `#1e2553` |
| Accent | LIME `#e0da67` |
| Font | Barlow (400, 500, 600, 700) |
| Page size | A4, 40pt padding |
| Card background | `#f4f3f8` |
| Logo | `frontend/src/assets/brand/Indemn_PrimaryLogo_Iris.png` |

Styles defined in `frontend/src/components/report/styles.ts`.
