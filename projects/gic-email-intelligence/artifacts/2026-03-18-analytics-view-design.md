---
ask: "What analytics should we show to help GIC understand their inbox — volume, types, agents, response times?"
created: 2026-03-18
workstream: gic-email-intelligence
session: 2026-03-18-a
sources:
  - type: conversation
    description: "Craig's vision for inbox analytics — understanding the data in real-time, not just historically"
  - type: database
    description: "3,214 emails classified with type, LOB, agent, carrier, timestamps"
---

# Analytics View — Understanding the GIC Inbox

## Context

Craig: "This automation flow is just one of many automations we're going to build for them using the Inbox as the input. We need a way of truly understanding their data, not just historically speaking, but relatively real-time, and being able to present that information in a way that actually helps them."

The data already exists — 3,214 classified emails with type, LOB, named insured, agent, carrier, reference numbers, timestamps. We just need to present it.

## What GIC Needs to Understand

### Volume & Trends
- How many emails/submissions per day/week/month?
- Is volume increasing or decreasing?
- What days are busiest?
- Are there seasonal patterns by LOB?

### Composition
- What types of emails are coming in? (80% USLI quotes, 6% pending, 4% decline, etc.)
- What LOBs are most active? (GL dominates, then Commercial Package, Professional Liability)
- Which carriers are most active? (USLI vs Hiscox vs others)

### Agents & Agencies
- Which retail agents/agencies send the most submissions?
- Which agents have the most pending/stale items?
- Agent response times (how fast do they reply to info requests?)

### Operational Health
- Average time from submission to quote
- How many submissions are stale (no activity 5+ days)?
- What % of submissions need info requests vs go straight through?
- Automation rate — what % is the system handling vs needing human input?

## Data We Already Have

From 3,214 classified emails:

| Data Point | Source | Example |
|---|---|---|
| Email volume by date | `received_at` | 17 emails/day average |
| Email type distribution | `classification.email_type` | 80.7% USLI Quote, 6.7% Pending, etc. |
| LOB distribution | `classification.line_of_business` | GL 519, Commercial Package 205, etc. |
| Agent/agency | `classification.named_insured`, `from_name` | Diana Ponce, Maria Bergolla |
| Carrier | Email type + sender | USLI, Hiscox, Swyfft |
| Reference numbers | `classification.reference_numbers` | MGL026F9DR4, 139617 |
| Timestamps | `received_at` | For time-based analysis |

From 10 submissions (would be more after batch):

| Data Point | Source |
|---|---|
| Stage distribution | `stage` field |
| Draft status | `draft_status` |
| Stale submissions | `last_activity_at` vs now |
| Email count per submission | `email_count` |

## UI Design

### Option A: Analytics Tab
A separate tab/view alongside the board. Toggle between "Inbox" (the action queue board) and "Analytics" (the dashboard).

### Option B: Analytics Section Above Board
Stats cards above the action queues — always visible. Click to expand into full analytics view.

### Option C: Analytics Sidebar
Collapsible sidebar on the right showing key metrics. Board takes the rest of the space.

### Recommended: Option A with summary in the dashboard bar

The dashboard bar (already built) shows queue counts. Add a few more summary numbers and an "Analytics" link/tab that opens a full analytics view.

**Dashboard bar (enhanced):**
```
[Search...]    8 Ready · 0 Review · 2 Monitoring  |  Today: 3 new  |  [Analytics →]
```

**Analytics view (separate page/tab):**
- Email volume chart (bar chart, emails per day/week)
- Email type breakdown (donut chart)
- LOB distribution (horizontal bar chart)
- Top agents/agencies (table)
- Response time metrics (average time to first response)
- Automation rate (% auto-drafted)

### Implementation

Backend: New `/api/analytics` endpoint that aggregates email data:
```python
@router.get("/analytics")
async def get_analytics(days: int = 30):
    # Email volume by day
    # Type distribution
    # LOB distribution
    # Top agents
    # Response times
```

Frontend: Use a charting library (recharts is lightweight, works well with React). Create an Analytics page with chart components.

## Not Now, But Later
- Predictive analytics (what's likely to come in tomorrow)
- Agent scoring (which agents are reliable, which are slow)
- Carrier comparison (which carriers quote faster, decline more)
- Cost analysis (premium volume by LOB/agent)
