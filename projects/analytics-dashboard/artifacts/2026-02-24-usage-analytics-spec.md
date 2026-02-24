---
ask: "What is the full implementation spec for the Observatory usage analytics feature?"
created: 2026-02-24
workstream: analytics-dashboard
session: 2026-02-24-b
sources:
  - type: mongodb
    description: "Verified billing filter against stripe_meters, explored requests collection schema, indexes, and participantsBots field structure"
  - type: github
    description: "Explored indemn-observability repo — overview page, scope system, API routers, data access layer, types, TabBar, CategoryTabs, dependencies, main.py"
  - type: linear
    description: "COP-326 — In Progress, Cycle 73, assigned Craig"
---

# Usage Analytics Spec — Indemn Observatory

## Overview

Add a Usage section to the Observatory overview page showing billable conversation counts broken out by organization and agent over a configurable date range. This is the first thing users see when they open Observatory. Data is sourced directly from the tiledesk `requests` collection using the billing-aligned filter, independent of the daily_snapshots / LangSmith pipeline.

## Linear

COP-326 — In Progress, Cycle 73, assigned Craig.

---

## 1. UI Placement

### Architecture Context

The Observatory frontend has two levels of navigation:

1. **Top-level TabBar** (`components/layout/TabBar.tsx`): Route-based pages using `react-router-dom` — Overview (`/`), Flow (`/flow`), Outcomes (`/outcomes`), Compare (`/compare`), Conversations (`/conversations`).

2. **CategoryTabs** within OverviewView (`components/overview/CategoryTabs.tsx`): KPI metric category tabs — Volume, Outcomes, Experience, Operations, Performance, Content. These switch which KPI metrics and charts are displayed. The `MetricCategory` type is `"volume" | "outcomes" | "experience" | "operations" | "performance" | "content"`.

### Placement Decision

Add `"usage"` as a new `MetricCategory` in `CategoryTabs.tsx`, positioned **first** (before Volume). It is the **default selected category** when the overview page loads — change the `useState` default from `"outcomes"` to `"usage"`.

**Why CategoryTab, not a new route:** The usage table shares the same scope and date range controls as the existing overview page. Adding a new top-level route would duplicate those controls. Usage is a category of overview data alongside volume, outcomes, etc.

**What changes:**
- `CategoryTabs.tsx`: Add `"usage"` to `MetricCategory` union type and `categories` array as first entry. Update `TabsList` grid class from `grid-cols-6` to `grid-cols-7` (or switch to `flex` layout) to accommodate the 7th tab.
- `OverviewView.tsx`: Change default category state to `"usage"`, add conditional rendering for the usage section when `category === "usage"`. The usage section should render **before** the early-return loading check on `useSnapshots()` since it is independent of snapshot data — otherwise the usage table would be blocked by the snapshots loading state.

### Layout When Usage Category Is Selected

```
┌─────────────────────────────────────────────────────┐
│  [Date Range Selector]          [Scope Selector]    │  ← existing controls
├─────────────────────────────────────────────────────┤
│  [Hero KPI Tiles]                                   │  ← existing (always visible)
├─────────────────────────────────────────────────────┤
│  Usage | Volume | Outcomes | Experience | ...       │  ← CategoryTabs (Usage first)
├─────────────────────────────────────────────────────┤
│                                                     │
│  Showing: Sep 1, 2025 — Feb 24, 2026               │  ← explicit date range label
│                                                     │
│  ┌───────────────┬─────┬─────┬─────┬───────┐       │
│  │ Organization  │ Sep │ Oct │ ... │ Total │       │  ← usage table
│  ├───────────────┼─────┼─────┼─────┼───────┤       │
│  │ GIC Underwrit │1478 │1761 │ ... │ 9102  │       │
│  │  ▸ GIC Bot    │ 765 │ 421 │ ... │ 4175  │       │  ← expanded agent sub-row
│  │ EventGuard    │ 964 │3796 │ ... │ 8280  │       │
│  │ ...           │     │     │     │       │       │
│  └───────────────┴─────┴─────┴─────┴───────┘       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Date Range Label

A text label displayed prominently above the table showing the exact range being queried. Format: `Showing: {start_date} — {end_date}` (e.g., "Showing: Sep 1, 2025 — Feb 24, 2026"). This updates whenever the global date range selector changes.

---

## 2. Scope Integration

The Usage section fully participates in the existing Observatory scope system (`ScopeContext` via `useScope()` hook). The scope provides `scopeParams` (`scope_level`, `customer_id`, `agent_id`) and `dateParams` (`date_from`, `date_to`) which are passed to the API.

### Platform Level (Indemn)

- **Default date range**: Last 6 months (see Section 3 for implementation)
- **Table shows**: All non-test organizations, sorted by total descending
- **Row type**: Organization
- **Drill-down**: Click a row to expand inline — agent sub-rows appear indented below the org
- **Expanded agent rows**: Fetched on demand (lazy load), sorted by total descending within the org
- **Authorization**: Platform scope requires Indemn employee access (enforced by `ValidatedScope`)

### Organization Level

- **Default date range**: Last 30 days (current default)
- **Table shows**: All agents for that organization, sorted by total descending
- **Row type**: Agent
- **Drill-down**: None — agents are the leaf level when scoped to an org

### Agent Level

- **Default date range**: Last 30 days (current default)
- **Table shows**: Single row for that agent
- **Row type**: Agent
- **Drill-down**: None

### Key Principle

The same data shape is used at every scope level. The table always renders rows with period columns and a total. The only difference is what the rows represent (orgs or agents) and whether inline expansion is available.

---

## 3. Date Range & Bucketing

### Global Date Range Selector

The Usage section uses the **existing global date range selector** (`DateRangePicker` at `components/ui/date-range-picker.tsx`). The picker currently has preset buttons for 7, 14, 30, and 90 days. It uses a raw Calendar component with no programmatic max range — users can already select any range via the calendar.

**Changes needed:**
- Add a **"Last 6 months"** preset button (183 days) to the `presets` array in `DateRangePicker`
- The Usage section should select this preset by default at platform scope

### Scope-Dependent Date Defaults

When the Usage category is selected, the component itself manages the date range default based on scope:
- Platform scope → select "Last 6 months" (183 days) on initial load
- Organization scope → use current 30-day default
- Agent scope → use current 30-day default

**Implementation note:** The `ScopeProvider` (`hooks/useScope.tsx`) does not currently change `dateRange` when scope changes — it initializes once to 30 days. Rather than modifying the ScopeProvider (which would affect all categories), the `UsageSection` component should call `setDateRange()` from `useScope()` when it mounts at platform scope, setting it to 6 months. This is a local concern of the usage feature, not a global scope behavior change.

The user can always override the default by selecting a different range.

### Adaptive Bucketing

Column granularity adapts to the size of the selected date range:

| Condition | Granularity | Column Header Format | Example |
|-----------|-------------|---------------------|---------|
| Range > 31 days | Monthly | "MMM YYYY" | "Sep 2025", "Oct 2025" |
| Range 8–31 days | Weekly | "MMM D–D" | "Feb 3–9", "Feb 10–16" |
| Range ≤ 7 days | Daily | "MMM D" | "Feb 18", "Feb 19" |

### Bucketing Rules

- **Monthly**: Bucket by calendar month. A period that starts or ends mid-month includes only conversations within the selected range — the column still shows the month name (e.g., "Sep 2025") but contains the partial count.
- **Weekly**: Weeks start on Monday. The first and last bucket may be partial weeks. Header shows the actual days included (e.g., "Feb 22–24" for a partial final week).
- **Daily**: One column per day in the range.

### Timezone

All bucketing uses **UTC** (MongoDB's `$dateToString` default, no `timezone` parameter). This is deliberate — Stripe billing uses UTC boundaries, so UTC bucketing aligns with billing data. A small number of conversations near month boundaries may appear in a different month than a user's local timezone would suggest. This is acceptable for a billing-aligned view.

### Weekly Bucketing Edge Case

ISO week years can differ from calendar years at year boundaries (e.g., Dec 29, 2025 is ISO week 1 of 2026). If the date range spans late December / early January, the `YYYY-WNN` bucket key uses `$isoWeekYear` which may differ from the calendar year. Column headers should use the ISO week year, not the calendar year, to avoid confusion.

### Total Column

Always present as the rightmost column. Sum of all bucket values for that row.

---

## 4. Data Source & Filtering

### Collection

`requests` in the `tiledesk` database on MongoDB Atlas (production cluster). The existing `MongoDBDataStore` already connects to the `tiledesk` database (configured in `config.py` line 16: `database: str = "tiledesk"`), so no new connection is needed.

### Billing-Aligned Filter

Every query applies this filter to match Stripe billing numbers:

```javascript
{
  status: 1000,                // closed conversations only
  isTestMode: { $ne: true },   // exclude test mode
  depth: { $gt: 2 }            // more than 2 messages (substantive conversations)
}
```

Verified 2026-02-24 against `stripe_meters` collection — matches within 1–2% (timing differences at month boundaries).

### Test Organization Exclusion

These organizations are always excluded from results:

| Organization | ID | Reason |
|--------------|----|--------|
| Indemn | `65e18047b26fd2526e096cd0` | Internal |
| Demos | `66c0920c358d3f001351c22c` | Demo showcase |
| Voice Demos | `66d196e9cc5cd70013e46565` | Voice prototypes |
| test-dolly-prod | `65e18830a0616000137bb854` | Test account |
| InsuranceTrak | `65e60f70683d12001386515a` | Legacy test |

EventGuard is **not** a test org — it is a real customer (Jewelers Mutual product).

These IDs should be defined as a constant (e.g., `EXCLUDED_ORG_IDS`) in a config or constants module, not hardcoded in the aggregation pipeline.

### Unattributed Conversations (~22%)

Approximately 22% of billable requests have an empty `participantsBots` array (human-only conversations where no bot participated). These conversations:
- **Are counted in org-level totals** (they match the billing filter)
- **Cannot be attributed to a specific agent** (no bot ID to group by)

**Handling:** When showing agent-level breakdowns (drill-down or org scope), include an **"Unattributed"** row at the bottom that captures conversations with empty `participantsBots`. This ensures the agent-level totals sum to the org-level total, maintaining data trust.

### Independence from LangSmith Pipeline

This feature queries `requests` directly. It does **not** use `daily_snapshots`, `observatory_conversations`, or LangSmith tracing data. Numbers will differ from the KPI tiles (which use the snapshots pipeline). This is intentional — the usage table shows billing-aligned conversation counts, the KPIs show observability metrics.

---

## 5. API Design

### Endpoint

```
GET /api/aggregations/usage
```

### Authentication & Authorization

The endpoint uses the existing `ValidatedScope` dependency (`dependencies.py`), which handles:
- Scope parameter validation (`scope_level` must be "platform", "customer", or "agent")
- Platform scope restricted to Indemn employees
- External users forced to customer scope for their org(s)
- Customer/agent ID validation against user's accessible orgs

```python
@router.get("/usage")
async def get_usage(
    scope: ValidatedScope = Depends(get_validated_scope),
    date_from: Optional[date] = Query(None, description="Start date (inclusive)"),
    date_to: Optional[date] = Query(None, description="End date (inclusive)"),
    data_store: DataStore = Depends(get_data_store),
):
```

### Query Parameters

Uses the same parameter pattern as all existing endpoints:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scope_level` | string | No (default: "platform") | `"platform"`, `"customer"`, or `"agent"` |
| `customer_id` | string | No | Organization ID. Required for customer scope. |
| `agent_id` | string | No | Agent (faq_kb) ID. Required for agent scope. |
| `date_from` | ISO date (YYYY-MM-DD) | No | Start of date range (inclusive) |
| `date_to` | ISO date (YYYY-MM-DD) | No | End of date range (inclusive) |

**Note:** These match the existing Observatory API conventions exactly — `scope_level` (not `scope_type`), separate `customer_id` and `agent_id` (not a combined `scope_id`), and `date_from`/`date_to` (not `start_date`/`end_date`).

### Response Shape

```json
{
  "range": {
    "start": "2025-09-01",
    "end": "2026-02-24",
    "granularity": "monthly"
  },
  "buckets": ["2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02"],
  "metrics": ["conversations"],
  "rows": [
    {
      "id": "65eb3f19e5e6de0013fda310",
      "name": "GIC Underwriters",
      "type": "organization",
      "buckets": {
        "2025-09": { "conversations": 1478 },
        "2025-10": { "conversations": 1761 },
        "2025-11": { "conversations": 1290 },
        "2025-12": { "conversations": 1375 },
        "2026-01": { "conversations": 1835 },
        "2026-02": { "conversations": 1363 }
      },
      "totals": { "conversations": 9102 }
    }
  ]
}
```

### Response Shape — Design Notes

- **`metrics` array**: Declares which metrics are present. Today: `["conversations"]`. Extensible to `["conversations", "unique_users", "avg_depth"]` in the future without structural changes.
- **`buckets` on each row**: Object keyed by period string, with named metric values inside. Adding a metric means adding a key — no breaking change.
- **`totals`**: Same shape as individual bucket objects. Sum across all buckets for that row.
- **`type` field**: `"organization"` or `"agent"` — tells the frontend what the row represents and whether expansion is available.
- **`rows`**: Sorted by total conversations descending. Rows with zero total across all buckets are omitted.

### Bucket Key Formats

| Granularity | Bucket Key Format | Example |
|-------------|-------------------|---------|
| Monthly | `YYYY-MM` | `"2025-09"` |
| Weekly | `YYYY-WNN` | `"2026-W08"` |
| Daily | `YYYY-MM-DD` | `"2026-02-18"` |

### Granularity Determination

The backend computes granularity from the date range:

```python
days = (end_date - start_date).days + 1
if days <= 7:
    granularity = "daily"
elif days <= 31:
    granularity = "weekly"
else:
    granularity = "monthly"
```

### Drill-Down (Agent Expansion)

When the user expands an org row at platform scope, the frontend makes a **second call** using the same endpoint with customer scope:

```
GET /api/aggregations/usage?scope_level=customer&customer_id=<org_id>&date_from=2025-09-01&date_to=2026-02-24
```

This returns agent-level rows for that org (including an "Unattributed" row for conversations without a bot). The frontend inserts them as indented sub-rows below the org row.

This lazy-load approach keeps the initial platform query fast — it only groups by org. Agent-level detail is fetched on demand.

### Error Responses

Follow existing Observatory patterns (FastAPI HTTPException):

| Status | Condition |
|--------|-----------|
| 400 | Invalid `scope_level`, `date_from > date_to`, malformed date |
| 401 | Missing or invalid auth token |
| 403 | External user requesting platform scope, or accessing unauthorized org |
| 500 | MongoDB query timeout or connection failure |

---

## 6. MongoDB Aggregation

### Python Type Note

All aggregation pipelines below are shown in JavaScript (mongosh) syntax for readability. In the Python Motor implementation:
- Use `bson.ObjectId("...")` instead of `ObjectId("...")`
- Use `datetime` objects instead of `ISODate("...")`
- Motor's `aggregate()` returns an async cursor

### Platform Scope — Organization-Level Query

```javascript
db.getCollection("requests").aggregate([
  // Stage 1: Match billing-eligible conversations in date range
  { $match: {
    status: 1000,
    isTestMode: { $ne: true },
    depth: { $gt: 2 },
    id_organization: { $nin: [
      ObjectId("65e18047b26fd2526e096cd0"),  // Indemn
      ObjectId("66c0920c358d3f001351c22c"),  // Demos
      ObjectId("66d196e9cc5cd70013e46565"),  // Voice Demos
      ObjectId("65e18830a0616000137bb854"),  // test-dolly-prod
      ObjectId("65e60f70683d12001386515a")   // InsuranceTrak
    ]},
    createdAt: {
      $gte: ISODate("2025-09-01T00:00:00Z"),
      $lt: ISODate("2026-02-25T00:00:00Z")
    }
  }},

  // Stage 2: Group by org + time bucket
  { $group: {
    _id: {
      org: "$id_organization",
      bucket: {
        // Monthly: truncate to month
        $dateToString: { format: "%Y-%m", date: "$createdAt" }
        // Weekly: use $isoWeek + $isoWeekYear (see Date Truncation section)
        // Daily: use %Y-%m-%d format
      }
    },
    count: { $sum: 1 }
  }},

  // Stage 3: Pivot buckets into per-org objects
  { $group: {
    _id: "$_id.org",
    buckets: {
      $push: { k: "$_id.bucket", v: "$count" }
    },
    total: { $sum: "$count" }
  }},

  // Stage 4: Sort by total descending
  { $sort: { total: -1 } },

  // Stage 5: Resolve org names
  { $lookup: {
    from: "organizations",
    localField: "_id",
    foreignField: "_id",
    as: "org"
  }},
  { $unwind: "$org" },
  { $project: {
    _id: 1,
    name: "$org.name",
    buckets: 1,
    total: 1
  }}
])
```

### Customer Scope — Agent-Level Query

```javascript
db.getCollection("requests").aggregate([
  // Stage 1: Match billing-eligible conversations for this org
  { $match: {
    status: 1000,
    isTestMode: { $ne: true },
    depth: { $gt: 2 },
    id_organization: ObjectId("<org_id>"),
    createdAt: { $gte: startDate, $lt: endDate }
  }},

  // Stage 2: Unwind participantsBots (required — it's an array of strings)
  // Requests with empty participantsBots are preserved with null via preserveNullAndEmptyArrays
  { $unwind: {
    path: "$participantsBots",
    preserveNullAndEmptyArrays: true
  }},

  // Stage 3: Group by bot + time bucket
  { $group: {
    _id: {
      agent: { $ifNull: ["$participantsBots", "__unattributed__"] },
      bucket: { $dateToString: { format: "%Y-%m", date: "$createdAt" } }
    },
    count: { $sum: 1 }
  }},

  // Stage 4: Pivot buckets per agent
  { $group: {
    _id: "$_id.agent",
    buckets: { $push: { k: "$_id.bucket", v: "$count" } },
    total: { $sum: "$count" }
  }},

  // Stage 5: Sort by total descending
  { $sort: { total: -1 } },

  // Stage 6: Resolve agent names from faq_kbs
  // NOTE: participantsBots values are strings, but faq_kbs._id is ObjectId.
  // Must convert with $toObjectId for the lookup to work.
  { $lookup: {
    from: "faq_kbs",
    let: { botId: "$_id" },
    pipeline: [
      { $match: {
        $expr: {
          $and: [
            { $ne: ["$$botId", "__unattributed__"] },
            { $eq: ["$_id", { $toObjectId: "$$botId" }] }
          ]
        }
      }}
    ],
    as: "bot"
  }},

  // Stage 7: Project final shape
  { $project: {
    _id: 1,
    name: {
      $cond: [
        { $eq: ["$_id", "__unattributed__"] },
        "Unattributed",
        { $ifNull: [{ $arrayElemAt: ["$bot.name", 0] }, "Unknown Agent"] }
      ]
    },
    buckets: 1,
    total: 1
  }}
])
```

**Key details:**
- `participantsBots` contains **strings** (e.g., `"64e3533faa90820013cd9624"`), not ObjectIds. The `$lookup` must use `$toObjectId` to convert before matching against `faq_kbs._id`.
- `$unwind` with `preserveNullAndEmptyArrays: true` keeps requests with empty `participantsBots` (they become `null`, mapped to `"__unattributed__"`).
- No requests currently have multiple bots (verified: 0 with `participantsBots.1`), so `$unwind` won't cause double-counting. But using `$unwind` is correct regardless — it handles the array-to-scalar conversion needed for grouping.

### Agent Scope — Single Agent Query

```javascript
db.getCollection("requests").aggregate([
  // Stage 1: Match by specific bot ID in participantsBots array
  { $match: {
    status: 1000,
    isTestMode: { $ne: true },
    depth: { $gt: 2 },
    participantsBots: "<agent_faq_kb_id>",  // string match against array
    createdAt: { $gte: startDate, $lt: endDate }
  }},

  // Stage 2: Group by time bucket only (single agent, no entity grouping)
  { $group: {
    _id: { $dateToString: { format: "%Y-%m", date: "$createdAt" } },
    count: { $sum: 1 }
  }},

  // Stage 3: Collect all buckets
  { $group: {
    _id: null,
    buckets: { $push: { k: "$_id", v: "$count" } },
    total: { $sum: "$count" }
  }}
])
```

The agent name is resolved separately via a single `faq_kbs.findOne({_id: ObjectId("<agent_id>")})` lookup, not in the aggregation pipeline.

### Date Truncation by Granularity

```javascript
// Monthly
{ $dateToString: { format: "%Y-%m", date: "$createdAt" } }

// Weekly (ISO week)
{ $concat: [
  { $toString: { $isoWeekYear: "$createdAt" } },
  "-W",
  { $cond: [
    { $lt: [{ $isoWeek: "$createdAt" }, 10] },
    { $concat: ["0", { $toString: { $isoWeek: "$createdAt" } }] },
    { $toString: { $isoWeek: "$createdAt" } }
  ]}
]}

// Daily
{ $dateToString: { format: "%Y-%m-%d", date: "$createdAt" } }
```

---

## 7. MongoDB Index

### Existing Indexes

The `requests` collection has 36 existing indexes. The most relevant to this query:
- `hasBot_1_status_1_createdAt_1` — partially covers the billing filter (has `status` + `createdAt`) but doesn't include `isTestMode`, `depth`, or `id_organization`
- `id_project_1_status_1_updatedAt_-1` — has `status` but uses `updatedAt` not `createdAt`

None of these efficiently support the full billing filter with date range and org grouping.

### New Compound Index

```javascript
db.getCollection("requests").createIndex(
  {
    status: 1,
    isTestMode: 1,
    createdAt: 1,
    id_organization: 1,
    depth: 1
  },
  { name: "idx_billing_usage" }
)
```

**Field order rationale:**
- `status: 1000` — equality match, narrows to closed conversations
- `isTestMode` — equality match (`{$ne: true}`)
- `createdAt` — range scan within the date window (index range scan works after equality prefixes)
- `id_organization` — used for `$nin` exclusion and `$group` (covered by index for grouping)
- `depth` — inequality filter (`{$gt: 2}`), placed last since it's a range condition

Note: `status` has limited cardinality (few distinct values), but as an equality match prefix it still narrows the index scan before the `createdAt` range. An alternative leading with `createdAt` would work for narrow date ranges but perform worse for 6-month scans across all statuses.

**Note**: This index should be created on the production Atlas cluster. Coordinate with DevOps or apply via `mongosh` with write permissions.

---

## 8. Backend Implementation

### File Locations

| File | Purpose |
|------|---------|
| `src/observatory/api/routers/usage.py` | New router — `GET /api/aggregations/usage` endpoint |
| `src/observatory/api/routers/__init__.py` | Add `from . import usage` to re-exports |
| `src/observatory/api/main.py` | Add `app.include_router(usage.router)` to router registration |
| `src/observatory/api/data_access.py` | Add abstract `get_usage_data()` method to `DataStore`, implement in `MongoDBDataStore` and stub in `JSONFileDataStore` |
| `src/observatory/api/models/usage.py` | Pydantic models for response |

### Router Pattern

Follow the exact pattern from `aggregations.py`:

```python
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date

from ..data_access import DataStore, get_data_store
from ..dependencies import ValidatedScope, get_validated_scope

router = APIRouter(prefix="/api/aggregations", tags=["aggregations"])

@router.get("/usage")
async def get_usage(
    scope: ValidatedScope = Depends(get_validated_scope),
    date_from: Optional[date] = Query(None, description="Start date (inclusive)"),
    date_to: Optional[date] = Query(None, description="End date (inclusive)"),
    data_store: DataStore = Depends(get_data_store),
):
    """
    Get billable usage metrics broken out by organization or agent.

    Returns conversation counts bucketed by time period (monthly/weekly/daily)
    based on the billing-aligned filter (status=1000, isTestMode!=true, depth>2).

    **Authorization:**
    - Platform scope: Indemn employees only
    - Customer/Agent scope: Must have access to the organization
    """
    return await data_store.get_usage_data(
        scope_level=scope.scope_level,
        customer_id=scope.customer_id,
        agent_id=scope.agent_id,
        date_from=date_from,
        date_to=date_to,
    )
```

### DataStore Changes

**Abstract method** (add to `DataStore` base class):

```python
@abstractmethod
def get_usage_data(
    self,
    scope_level: str,
    customer_id: Optional[str],
    agent_id: Optional[str],
    date_from: Optional[date],
    date_to: Optional[date],
) -> dict:
    """Get billable usage metrics bucketed by time period."""
    pass
```

Note: The abstract base uses `def` (not `async def`), matching the existing convention in `DataStore`. The `MongoDBDataStore` overrides with `async def` — this is the established pattern in the codebase.

**MongoDBDataStore implementation:** Override with `async def get_usage_data(...)`. Build the aggregation pipelines from Section 6, using the existing `self.db` connection (which already connects to `tiledesk` database).

**JSONFileDataStore stub** (for local dev without MongoDB):

```python
def get_usage_data(self, scope_level="platform", customer_id=None, agent_id=None, date_from=None, date_to=None) -> dict:
    return {
        "range": {"start": "", "end": "", "granularity": "monthly"},
        "buckets": [],
        "metrics": ["conversations"],
        "rows": [],
    }
```

### Implementation Notes

- Test org exclusion IDs should be a constant: `EXCLUDED_ORG_IDS` list of `bson.ObjectId` values, defined in a constants file or at the top of the data access method.
- Granularity computation (days → daily/weekly/monthly) should be a utility function, testable independently.
- The `MongoDBDataStore` already has `self.db` pointing to the `tiledesk` database. No new connection needed — `self.db.requests` accesses the requests collection directly.

---

## 9. Frontend Implementation

### File Locations

| File | Purpose |
|------|---------|
| `frontend/src/components/overview/UsageSection.tsx` | Usage category content — date label, table, expand state |
| `frontend/src/components/overview/UsageTable.tsx` | Table component — headers, rows, expand/collapse |
| `frontend/src/components/overview/UsageTableRow.tsx` | Single row — org or agent, click to expand |
| `frontend/src/hooks/useUsage.ts` | Data fetching hook — TanStack Query, reads from useScope() |
| `frontend/src/types/api.ts` | Add `UsageResponse`, `UsageRow` types |
| `frontend/src/lib/api.ts` | Add `getUsage()` method to API client |
| `frontend/src/components/overview/OverviewView.tsx` | Modify — add usage category, change default to "usage" |
| `frontend/src/components/overview/CategoryTabs.tsx` | Modify — add "usage" to MetricCategory type and categories array |
| `frontend/src/components/ui/date-range-picker.tsx` | Modify — add "Last 6 months" preset |

**Note:** Components go in `components/overview/` (not a `tabs/` subdirectory — no such convention exists in the codebase).

### Component Hierarchy

```
OverviewView
├── DateRangePicker (existing)
├── ScopeSelector (existing)
├── KPIGrid (existing — always visible)
├── CategoryTabs (modified — "usage" added as first)
└── (when category === "usage"):
    └── UsageSection
        ├── DateRangeLabel ("Showing: Sep 1, 2025 — Feb 24, 2026")
        └── UsageTable
            ├── UsageTableRow (org) — clickable to expand
            │   ├── UsageTableRow (agent sub-row)
            │   ├── UsageTableRow (agent sub-row)
            │   └── UsageTableRow ("Unattributed" sub-row)
            ├── UsageTableRow (org)
            └── ...
```

### useUsage Hook

Follows the exact pattern of `useSnapshots()` — uses TanStack Query `useQuery`, reads params from `useScope()` context:

```typescript
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useScope } from "@/hooks/useScope";

export function useUsage() {
  const { scopeParams, dateParams } = useScope();
  return useQuery({
    queryKey: ["usage", scopeParams, dateParams],
    queryFn: () => api.getUsage(scopeParams, dateParams),
  });
}
```

Returns TanStack Query's `UseQueryResult` with `{ data, isLoading, error, isFetching }` — not a custom return type.

For drill-down (fetching agents for a specific org), use a separate hook or parameterized call:

```typescript
export function useUsageExpansion(customerId: string | null) {
  const { dateParams } = useScope();
  return useQuery({
    queryKey: ["usage", "expansion", customerId, dateParams],
    queryFn: () => api.getUsage(
      { scope_level: "customer", customer_id: customerId, agent_id: null },
      dateParams
    ),
    enabled: !!customerId,  // only fetch when a customerId is provided
  });
}
```

### API Client Addition

Add to the `api` object in `frontend/src/lib/api.ts`, following the exact pattern of `getSnapshots`:

```typescript
getUsage: (scope: ScopeParams, dates: DateParams): Promise<UsageResponse> => {
  const params = buildParams({ ...scope, ...dates });
  return fetchJSON(`${API_BASE}/api/aggregations/usage?${params}`);
},
```

This uses the existing `buildParams` helper (handles null filtering and URLSearchParams construction) and `fetchJSON` (handles auth headers, 401 redirect to login, 403 scope enforcement). `ScopeParams` and `DateParams` are already defined locally in `api.ts` — no new imports needed.

### Expand/Collapse Behavior

- `UsageTable` maintains a `Set<string>` of expanded org IDs in React state.
- When an org row is clicked, if not expanded: add to set, `useUsageExpansion` fetches agent data. If already expanded: remove from set, collapse.
- Agent sub-rows render indented (padding-left) below the parent org row.
- Loading state: show a subtle spinner or skeleton rows while agent data loads.

### Date Range Picker Changes

Add to the `presets` array in `date-range-picker.tsx`:

```typescript
const presets = [
  { label: "Last 7 days", days: 7 },
  { label: "Last 14 days", days: 14 },
  { label: "Last 30 days", days: 30 },
  { label: "Last 90 days", days: 90 },
  { label: "Last 6 months", days: 183 },  // NEW
];
```

### Styling

- Use existing shadcn/ui table components and Tailwind classes for consistency.
- Org rows: normal weight, clickable (cursor pointer, hover state) when at platform scope.
- Agent sub-rows: indented with `pl-8`, slightly muted text or different background to visually distinguish from org rows.
- "Unattributed" row: italic or muted style to differentiate from named agents.
- Total column: bold or semi-bold to stand out.
- Numbers: right-aligned, formatted with commas (e.g., "1,478").
- Zero values: show "—" instead of "0" for cleaner readability.

---

## 10. TypeScript Types

Add to `frontend/src/types/api.ts`:

```typescript
// Response from GET /api/aggregations/usage
export interface UsageResponse {
  range: {
    start: string;        // "2025-09-01"
    end: string;          // "2026-02-24"
    granularity: "monthly" | "weekly" | "daily";
  };
  buckets: string[];      // ["2025-09", "2025-10", ...]
  metrics: string[];      // ["conversations"]
  rows: UsageRow[];
}

export interface UsageRow {
  id: string;             // org or agent ID (or "__unattributed__")
  name: string;           // display name (or "Unattributed")
  type: "organization" | "agent";
  buckets: Record<string, Record<string, number>>;
  // e.g., { "2025-09": { "conversations": 1478 } }
  totals: Record<string, number>;
  // e.g., { "conversations": 9102 }
}
```

---

## 11. Edge Cases

| Scenario | Behavior |
|----------|----------|
| Org has zero billable conversations in range | Omit from results (no empty rows) |
| Agent has conversations but org is in test exclusion list | Agent is excluded (filtering is at org level in query) |
| Date range spans less than 7 days | Switch to daily columns |
| Date range is exactly 1 day | Single daily column + total (same value) |
| New org with no history | Only appears if it has billable conversations in the selected range |
| Org row expanded but agent call fails | Show error state in the expansion area, org row stays expanded |
| Very wide table (many monthly columns) | Horizontal scroll on the table container |
| Conversations with no bot (empty participantsBots) | Counted in org totals; shown as "Unattributed" row in agent drill-down |
| Agent scope for a bot with zero conversations | Single row with all zeros (or empty state message) |
| External user tries platform scope | `ValidatedScope` returns 403; forced to customer scope for their org |
| `date_from` after `date_to` | Backend returns 400 error |

---

## 12. Implementation Order

Suggested sequence for building this feature:

1. **MongoDB index** — Create `idx_billing_usage` on production cluster
2. **Backend models** — Pydantic response models in `models/usage.py`
3. **Backend data access** — Add abstract `get_usage_data()` to `DataStore`, implement in `MongoDBDataStore`, stub in `JSONFileDataStore`
4. **Backend router** — `GET /api/aggregations/usage` in `routers/usage.py`, register in both `routers/__init__.py` and `main.py`
5. **Backend testing** — Verify endpoint returns correct data against known billing numbers from research artifact
6. **Frontend types** — Add `UsageResponse` and `UsageRow` to `types/api.ts`
7. **Frontend API client** — Add `getUsage()` to `lib/api.ts`
8. **Frontend hook** — `useUsage.ts` and `useUsageExpansion` using TanStack Query + useScope()
9. **Frontend components** — `UsageTableRow` → `UsageTable` → `UsageSection` (bottom-up)
10. **Overview integration** — Add "usage" to `CategoryTabs`, render `UsageSection` in `OverviewView`, set default category to "usage"
11. **Date range preset** — Add "Last 6 months" preset to `DateRangePicker`, add scope-dependent default logic in `UsageSection`
12. **Polish** — Number formatting, zero-value display, loading states, error handling, Unattributed row styling

---

## 13. Dependencies & Build

No new npm packages or Python dependencies are required. The feature uses:
- **Frontend**: React, TanStack Query, shadcn/ui, Tailwind — all already installed
- **Backend**: FastAPI, Motor, Pydantic, bson — all already installed

No Vite config, build config, or CI/CD changes needed.
