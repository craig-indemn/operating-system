# Meetings Intelligence Data Dictionary

> Domain-focused reference for the Indemn meetings intelligence system.
> Covers what the data **means**, how it flows, and how to query it effectively.
> Last updated: 2026-02-11

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Flow Pipeline](#data-flow-pipeline)
3. [Meeting Sources & Types](#meeting-sources--types)
4. [Extraction Types — The Core Intelligence](#extraction-types--the-core-intelligence)
5. [Signal Types — Business Intelligence](#signal-types--business-intelligence)
6. [Quotes — Voice of the Customer](#quotes--voice-of-the-customer)
7. [Deal Pipeline — CRM Data Model](#deal-pipeline--crm-data-model)
8. [Company & Contact Model](#company--contact-model)
9. [Implementation Tracking](#implementation-tracking)
10. [Investor Relations](#investor-relations)
11. [Email & Outreach System](#email--outreach-system)
12. [Slack Intelligence](#slack-intelligence)
13. [Data Quality & Matching](#data-quality--matching)
14. [System Health & Background Jobs](#system-health--background-jobs)
15. [Common Query Patterns](#common-query-patterns)
16. [JOIN Reference](#join-reference)
17. [Tips for Effective Querying](#tips-for-effective-querying)

---

## System Overview

This database powers Indemn's **meetings intelligence system** — an AI-powered platform that:

1. **Ingests meetings** from Apollo (call recordings), Granola (meeting notes), and Gemini
2. **Extracts intelligence** using LLM-based extraction strategies (decisions, learnings, problems, objections)
3. **Generates business signals** (health indicators, expansion opportunities, champion identification, churn risk)
4. **Captures notable quotes** for case studies, pitches, and testimonials
5. **Tracks a sales pipeline** of insurance industry prospects and customers
6. **Manages outreach** via email sequences and AI-generated drafts
7. **Monitors Slack channels** for customer signals
8. **Tracks investor relations** for fundraising

The core entity chain is: **Company -> Deal -> Meeting -> MeetingUtterance / MeetingExtraction / Signal / Quote**

**Scale** (as of 2026-02-11):
- 1,059 companies | 5,961 contacts | 1,089 deals
- 3,141 meetings | 183,697 utterances | 5,185 participants
- 14,612 meeting extractions | 3,240 signals | 3,681 quotes | 1,469 action items

---

## Data Flow Pipeline

```
┌─────────────────────────────────────────────────┐
│          MEETING INGESTION                       │
│  Apollo (2,704) | Granola (426) | Gemini (11)   │
│                                                  │
│  Meeting → MeetingParticipant (who was there)    │
│          → MeetingUtterance (what was said)       │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│          EXTRACTION PIPELINE                     │
│                                                  │
│  ExtractionStrategy (prompt template + schema)   │
│         │                                        │
│         ▼                                        │
│  ExtractionRun (execution record, tokens, ms)    │
│         │                                        │
│         ▼                                        │
│  MeetingExtraction (structured intelligence)     │
│    ├─ decisions  (5,691)                         │
│    ├─ learnings  (4,691)                         │
│    ├─ problems   (2,622)                         │
│    └─ objections (1,608)                         │
│                                                  │
│  Signal (business signals: 3,240)                │
│  Quote  (notable quotes: 3,681)                  │
│  ActionItem (action items: 1,469)                │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│          CRM / DEAL PIPELINE                     │
│                                                  │
│  Company → Deal → AIScoringResult                │
│                 → Activity (timeline events)      │
│                 → StaleAlert (staleness warnings) │
│                 → AutoAction (automated flags)    │
│                 → Email / DraftEmail / Outreach   │
└─────────────────────────────────────────────────┘
```

### Extraction Strategy Selection

The system selects an extraction strategy based on the meeting's `meetingType`:

| meetingType | Strategy Used | Runs |
|-------------|--------------|------|
| `customer` | Customer Meeting Extraction v1 (v2) | 210 |
| `internal` | Internal Meeting Extraction v1 | 156 |
| `investor` | Investor Meeting Extraction v1 | 4 |
| `vendor` | Vendor/Partner Meeting Extraction v1 | 4 |

Average extraction: ~7,309 tokens, ~14.7 seconds per run.

---

## Meeting Sources & Types

### Sources (Meeting.source)

| Source | Count | Description |
|--------|-------|-------------|
| `apollo` | 2,704 | Apollo.io call recordings — the primary meeting source. IDs prefixed with `apollo-`. |
| `granola` | 426 | Granola meeting notes tool — UUIDs as IDs. |
| `gemini` | 11 | Google Gemini recordings — IDs prefixed with `gemini-`. |

### Meeting Types (Meeting.meetingType)

| meetingType | Count | Description |
|------------|-------|-------------|
| `internal` | 1,642 | General internal meetings |
| `internal_sync` | 599 | Internal sync/standup meetings |
| `internal_1on1` | 359 | 1-on-1 meetings |
| `internal_dev` | 191 | Dev team meetings |
| `customer` | 141 | Customer meetings (existing clients) |
| `prospect` | 116 | Sales prospect meetings |
| `implementation` | 45 | Implementation/onboarding meetings |
| `hiring` | 18 | Hiring/recruitment meetings |
| `investor` | 9 | Investor meetings |
| NULL | 21 | Unclassified (mostly from Granola) |

### Meeting Categories (Meeting.category)

Categories are similar to `meetingType` but reflect a separate classification system. Key additions:
- `partner` (85): Partnership-related meetings
- `past` (3): Historical/archived meetings

### Meeting Visibility (Meeting.visibility)

| Value | Count | Description |
|-------|-------|-------------|
| `private` | 3,079 | Visible only to the meeting owner |
| `team` | 62 | Visible to the whole team |

---

## Extraction Types — The Core Intelligence

The `MeetingExtraction` table holds the primary AI-extracted intelligence. Each row is a single extracted insight.

### Extraction Type: `decision` (5,691 rows)

**What it means**: A decision made during the meeting — strategic choices, commitments, process changes.

**Categories**:
| Category | Count | What It Represents |
|----------|-------|--------------------|
| `strategic` | 1,931 | High-level business decisions (pricing, partnerships, product direction) |
| `commitment` | 1,183 | Specific commitments made (deliverables, timelines, promises) |
| `process` | 895 | Process and workflow decisions |
| `technical` | 428 | Technical architecture or implementation decisions |
| `product` | 325 | Product feature or roadmap decisions |
| NULL | 924 | Uncategorized decisions |

**Real examples**:
- "Re-added escrow provision to SaaS agreement" (strategic)
- "Subscription fees beyond year 3 set at 4% of DWP with specific annual amounts" (strategic)
- "Rate card for additional services set at three tiers: $100, $150, $175/hour" (strategic)

**Additional fields for decisions**: `reversible` (boolean, 2,521 populated) — whether the decision can be undone.

---

### Extraction Type: `learning` (4,691 rows)

**What it means**: Insights and learnings from the meeting — things discovered about customers, products, markets, or sales approaches.

**Categories**:
| Category | Count | What It Represents |
|----------|-------|--------------------|
| `sales` | 2,628 | Sales insights (what resonates, customer reactions, competitive intel) |
| `product` | 1,303 | Product insights (feature requests, usage patterns, gaps) |
| `implementation` | 591 | Implementation insights (what works, common challenges) |
| `support` | 142 | Support/service insights |
| `process` | 12 | Process improvements discovered |

**Confidence field** (only used for learnings):
| Confidence | Count | Meaning |
|-----------|-------|---------|
| `insight` | 2,483 | General observation or finding |
| `worked` | 1,721 | Something that was proven to work |
| `didnt_work` | 487 | Something that was proven NOT to work |

**Real examples**:
- "RV insurance customer has $20M annual revenue and multiple specialty niches" (sales, insight)
- "Customer has sophisticated web forms but manual processes behind them" (product, insight)
- "Operating system analogy helps customers understand platform vs point solution difference" (sales, worked)

---

### Extraction Type: `objection` (1,608 rows)

**What it means**: Objections raised during meetings — concerns, pushback, or resistance from prospects/customers.

**Categories**:
| Category | Count | What It Represents |
|----------|-------|--------------------|
| `technical` | 501 | Technical concerns (integration, capabilities, architecture) |
| `process` | 470 | Process concerns (workflow changes, adoption, training) |
| `timing` | 190 | Timing concerns (not the right time, competing priorities) |
| `trust` | 181 | Trust concerns (reliability, vendor risk, AI skepticism) |
| `price` | 155 | Pricing objections |
| `competition` | 69 | Competitive comparisons/preferences |
| `resource` | 22 | Resource constraints |

**Additional fields for objections**: `responseWorked` (boolean, 35 populated) — whether the response to the objection was effective.

**Real examples**:
- "CSRs may fear AI will replace them rather than assist them" (trust)
- "Agents find it faster to collect medication info themselves rather than transfer to AI" (process)
- "Mitchell poorly communicated salary expectations and waited until deal end to negotiate" (process)

---

### Extraction Type: `problem` (2,622 rows)

**What it means**: Problems or issues identified during meetings — bugs, bottlenecks, organizational challenges.

**Categories**:
| Category | Count | What It Represents |
|----------|-------|--------------------|
| `process` | 1,123 | Process breakdowns, workflow issues, organizational problems |
| `technical` | 805 | Technical bugs, integration failures, system issues |
| `communication` | 279 | Communication gaps, misalignment, unclear expectations |
| `resource` | 268 | Resource shortages, understaffing, budget constraints |
| `integration` | 85 | Integration-specific problems |

**Real examples**:
- "Lost PM 4-5 months ago and position not backfilled" (resource)
- "QuickBooks bank feeds disconnected since June 18" (technical)
- "Revenue is still too low compared to burn rate" (resource)

---

### Additional MeetingExtraction Fields

These fields are populated for a subset of extractions:

| Field | Populated Count | Used For |
|-------|----------------|----------|
| `context` | 2,548 | Additional context around the extraction |
| `extractedDate` | 2,610 | When the extracted event occurred |
| `participants` | 2,521 | JSON of participants involved |
| `rationale` | 795 | Reasoning behind the extraction |
| `personName` | 0 | (Unused — person attribution) |
| `severity` | 0 | (Unused — severity rating) |

---

## Signal Types — Business Intelligence

Signals are higher-level business intelligence extracted from meetings. While `MeetingExtraction` captures what was said/decided, `Signal` interprets what it means for the business relationship.

### Signal Types (Signal.signalType)

| Signal Type | Count | Meaning | Typical Sentiment |
|------------|-------|---------|-------------------|
| `health` | 1,229 | Account health indicator — positive or negative signs about the relationship | Mostly positive |
| `expansion` | 1,085 | Expansion opportunity — signs the customer might buy more or expand usage | Positive |
| `champion` | 685 | Champion identification — someone internally advocating for the product | Positive |
| `churn_risk` | 151 | Churn risk — warning signs the customer might leave | Negative |
| `blocker` | 88 | Blocker — something actively preventing progress | Negative |
| `insight` | 2 | General insight (rare) | Varies |

### Signal Sentiment (Signal.sentiment)

| Sentiment | Count | Description |
|-----------|-------|-------------|
| `positive` | 2,877 | 88.8% — positive indicators |
| `negative` | 274 | 8.5% — warning indicators |
| `neutral` | 89 | 2.7% — informational |

**Real examples**:
- **health/positive**: "First agreement (APA) largely accepted with minimal red lines"
- **health/positive**: "Customer proactively monitoring reception agent performance and providing ongoing feedback"
- **churn_risk/negative**: "Mitchell waited until last minute to negotiate and poorly communicated expectations"
- **champion/positive**: "Champion identified: Jeff Arnold"

---

## Quotes — Voice of the Customer

Quotes capture notable statements from meeting participants for reuse in sales, marketing, and internal purposes.

### Quote Sentiment (Quote.sentiment)

| Sentiment | Count | Description |
|-----------|-------|-------------|
| `positive` | 2,152 | 58.5% — endorsements, enthusiasm, praise |
| `neutral` | 1,114 | 30.3% — factual statements, observations |
| `negative` | 415 | 11.3% — complaints, concerns, criticism |

### Quote Usability (Quote.usableFor)

| usableFor | Count | Description |
|-----------|-------|-------------|
| `internal` | 1,804 | Internal use only — competitive intel, team learning |
| `case_study` | 950 | Suitable for case study inclusion |
| `pitch` | 688 | Useful in sales pitches and demos |
| `testimonial` | 229 | Direct testimonial material |
| `product` | 5 | Product development insights |
| `insight` | 3 | General insights |
| `thought_leadership` | 1 | Thought leadership content |
| `competitive` | 1 | Competitive positioning |

**Real examples**:
- **positive/case_study**: Customer describing specific value received from Indemn's product
- **negative/internal**: Internal discussion about operational gaps
- **positive/testimonial**: Direct endorsement from a customer champion

---

## Deal Pipeline — CRM Data Model

### Deal Stages (DealStatus enum)

The pipeline follows a linear progression with configurable staleness thresholds:

| Stage | Count | Stale After | Description |
|-------|-------|-------------|-------------|
| `CONTACT` | 817 | 14 days | Initial engagement |
| `DISCOVERY` | 201 | 7 days | Qualification and needs analysis |
| `DEMO` | 6 | 5 days | Founder demo to confirm fit |
| `PROPOSAL` | 0 | 3 days | Proposal review |
| `NEGOTIATION` | 10 | 2 days | Contract finalization |
| `WON` | 18 | N/A | Closed won |
| `LOST` | 37 | N/A | Closed lost |

Most deals (75%) are in CONTACT stage, indicating a large top-of-funnel.

### Deal Segments (Deal.segment)

| Segment | Count |
|---------|-------|
| `Enterprise` | 109 |
| `Mid-Market` | 90 |
| `SMB` | 86 |

### Opportunity Buckets (Deal.opportunityBucket)

| Bucket | Count | Description |
|--------|-------|-------------|
| `Broker Resources` | 123 | Tools/resources for brokers |
| `Agent Network` | 95 | Agent network solutions |
| `Digital Products` | 60 | Digital product offerings |

### GTM Segments (Deal.gtmSegment — GtmSegment enum)

| Segment | Count |
|---------|-------|
| `DIGITAL_PRODUCT` | 71 |
| `BROKER_RESOURCES` | 21 |
| `AGENT_NETWORK` | 3 |

### Top Use Cases (Deal.useCase)

| Use Case | Count |
|----------|-------|
| Quote-to-bind | 39 |
| Submission intake | 16 |
| Customer service | 15 |
| Quote-to-bind automation | 11 |
| Submission Triage | 5 |
| Policy administration and customer service | 4 |
| Claims management automation | 4 |

### Deal Scoring

Each deal can have an `AIScoringResult` with:
- **compositeScore**: 1.4 to 3.9 (out of 5), average 2.12
- **suggestedARR**: $24,000 to $70,000, average $34,424
- **confidence**: Mostly `low` (997 of 1,001)
- **status**: `approved` (708), `pending` (292), `rejected` (1)

The deal itself also has component scores: `companyFitScore`, `eagernessScore`, `milestoneScore`, `relationshipScore`, `useCaseScore`.

---

## Company & Contact Model

### Company Types (CompanyType enum)

| Type | Count | Description |
|------|-------|-------------|
| `OTHER` | 468 | General/uncategorized |
| `BROKER` | 252 | Insurance brokers |
| `MGA_MGU` | 243 | Managing General Agents/Underwriters |
| `CARRIER` | 96 | Insurance carriers |

### Top Industries (Company.industry)

Overwhelmingly insurance-focused:
- `insurance` (385) — 84% of companies with industry data
- `financial services` (27)
- `information technology & services` (24)

### Health Tracking

88 companies have health data:
- `healthColor`: `green` (75), `yellow` (12), `red` (1)
- `healthScore`: 0-100 numeric score

### Data Enrichment Sources

Companies are enriched from:
- **Apollo.io**: 633 companies have `apolloId`; contacts have `apolloId` (5,828)
- **Airtable**: Legacy IDs present on companies, investor firms, and investor contacts
- **Domain matching**: 567 companies have `domain` for email-to-company matching

---

## Implementation Tracking

Implementations represent post-sale customer onboarding. 19 active implementations.

### Implementation Stages (ImplementationStage enum)

Full lifecycle from kickoff through advocacy:
`KICKOFF` -> `SCOPING` -> `CONFIGURATION` -> `TESTING` -> `LAUNCH` -> `ONBOARDING` -> `ACTIVE` -> `LIVE` -> `EXPAND` -> `RENEW` -> `ADVOCATE`

Current distribution: `ACTIVE` (4), `LIVE` (4), `SCOPING` (4), `TESTING` (3), `CONFIGURATION` (2), `KICKOFF` (2).

### Agent Types

Each implementation tracks which agent types are being deployed:
- `hasVoiceAgent` — Voice AI agent
- `hasChatAgent` — Chat AI agent
- `hasEmailAgent` — Email AI agent

### Voice Implementation

6 implementations have `VoiceImplementation` records with use cases like:
- `{intake, quotes}` — Intake and quoting
- `{intake, service}` — Intake and customer service
- `{billing, service}` — Billing and service

### Milestones

228 milestones across implementations (71 completed). Milestones are organized by `ImplementationStage` — each stage has standard milestones.

---

## Investor Relations

A separate CRM subsystem for tracking investor firms during fundraising.

### Investor Types

| Type | Count |
|------|-------|
| `VC` | 166 |
| `ANGEL` | 32 |
| `CVC` | 14 |

### Investor Tiers

| Tier | Count | Meaning |
|------|-------|---------|
| `A` | 49 | Highest priority |
| `B` | 37 | High priority |
| `C` | 41 | Medium priority |
| `D` | 85 | Lower priority |

### Investor Status Pipeline

From research through investment/decline:
`RESEARCH` (37) -> `TARGET` (21) -> `COLD` (18) -> `WARM_INTRO` (4) -> `CONTACTED` (25) -> `INITIAL_MEETING` (15) -> `FOLLOW_UP` (4) -> `DEEP_DIVE` (1) -> `INTEREST` (10) -> `STRONG_INTEREST` (2) -> `INVESTED` (36) -> `DECLINED` (25) -> `PASSED` (6) -> `DORMANT` (8)

### Scoring

Investor firms have a `compositeScore` (up to 200 for invested firms), with component scores: `fitScore`, `relationshipScore`, `urgencyScore`.

---

## Email & Outreach System

### Email Tracking

425 tracked emails, all outbound from `kyle@indemn.ai`. Date range: Oct 2025 to Feb 2026.

Features:
- **Thread tracking**: Emails grouped by `threadId`
- **Open tracking**: `trackingId`, `wasOpened`, `openCount`, `firstOpenedAt`
- **Response tracking**: `needsResponse`, `responseReceived`

### Outreach Sequences

Three predefined sequences:

**Re-engagement** (default):
1. Day 0: Initial Outreach (new thread)
2. Day 3: Follow-up 1 (reply)
3. Day 7: Follow-up 2 (reply)
4. Day 14: Break-up Email (reply)

**Post-Demo**:
1. Day 0: Demo Follow-up
2. Day 3: Check-in
3. Day 7: Decision Check

**Post-Proposal**:
1. Day 0: Proposal Sent
2. Day 3: Proposal Check-in
3. Day 7: Decision Push

### Draft Email Generation

The system generates AI draft emails using context from:
- Prior email threads (`priorEmails` JSONB)
- Meeting intelligence (`meetings` JSONB)
- Deal notes (`dealNotes`)

Drafts have a priority (`high`/`medium`/`low`) and status (`pending`/`skipped`/`sent`).

### Voice Profile

A single `VoiceProfile` record captures the user's email writing style (greeting patterns, closing patterns, CTA patterns, formality score) for use in AI-generated emails.

---

## Slack Intelligence

### Monitored Channels

28 Slack channels monitored, categorized as:
- `product` (10): Product-related channels (e.g., `product-development-feedback`, `copilot-dev`)
- `customer` (7): Customer-specific channels (e.g., `indemn-gic_underwriters`, `eventguard`)
- `operations` (6): Operations channels
- `alerts` (5): Alert channels (e.g., `saas-onboarding-alerts`)

Scan frequency: every 4 hours.

### Slack Extractions

Intelligence extracted from Slack messages:
- `signalType`: `win` (3), `request` (3), `blocker` (1)
- All `extractionType`: `customer`
- Includes match data (`matchConfidence`, `matchMethod`) for company attribution

### Team Updates

80 team updates extracted from Slack:
- `updateType`: `cdd` (57) — Customer delivery digest; `status` (23) — Status updates
- Structured into `updates` (JSONB) and `todos` (JSONB) fields
- All sourced from Slack

---

## Data Quality & Matching

### Company Deduplication

The system identifies potential duplicate companies:
- `DuplicateGroup`: 65 groups (42 merged, 23 pending)
- `DuplicateGroupMember`: 146 records
- Match scores range 0.85-1.0 (avg 0.956)

### Name Matching

`LearnedMatch`: 71 cached company name matches (all `company_name` type). Maps informal names to canonical companies. Examples:
- "alchemy" -> "Alchemy Insurance Solutions"
- "bonza" -> "Bonzah"
- "distinguished" -> "Distinguished Programs"

`CompanyAlias`: 10 formal alternative names mapped to companies.

### Record Staging

`StagedRecord` / `MatchLog`: Incoming records (currently only calls) are staged, matched to companies via AI, then processed. 4 records total.

---

## System Health & Background Jobs

Five background jobs tracked in `SystemHealth`:

| Job | Description | Last Run |
|-----|-------------|----------|
| `slack_scan` | Scans 26 Slack channels for signals | 2026-02-01 |
| `daily_close` | End-of-day pipeline snapshot | 2026-02-11 |
| `daily_sync` | Full daily sync (emails, deals, signals, company matching) | 2026-02-11 |
| `daily_intelligence` | Generates daily intelligence report, posts to Slack | 2026-02-11 |
| `morning_brief` | Morning leadership briefing with pipeline summary | 2026-02-11 |

All currently in `success` status. `daily_sync` takes ~113 seconds and processes emails sent/received, close signals, stage changes, and company matching.

---

## Common Query Patterns

### 1. Find all intelligence for a specific company

```sql
-- Get all extractions, signals, quotes, and action items for a company
WITH company_meetings AS (
  SELECT m.id, m.title, m.date
  FROM "Meeting" m
  WHERE m."companyId" = '<company_id>'
)
SELECT 'extraction' as type, me."extractionType", me.category, me.text, cm.date
FROM "MeetingExtraction" me
JOIN company_meetings cm ON me."meetingId" = cm.id

UNION ALL

SELECT 'signal', s."signalType", s.sentiment, s.text, cm.date
FROM "Signal" s
JOIN company_meetings cm ON s."meetingId" = cm.id

UNION ALL

SELECT 'quote', q."usableFor", q.sentiment, q.text, cm.date
FROM "Quote" q
JOIN company_meetings cm ON q."meetingId" = cm.id

ORDER BY date DESC;
```

### 2. Pipeline health dashboard

```sql
SELECT
  d.status::text,
  count(*) as deals,
  sum(d."expectedARR") as total_arr,
  avg(d."compositeScore") as avg_score,
  count(CASE WHEN d."isStale" THEN 1 END) as stale_deals
FROM "Deal" d
WHERE d.status NOT IN ('WON', 'LOST')
GROUP BY d.status
ORDER BY d.status;
```

### 3. Top objections across customer meetings

```sql
SELECT me.category, count(*) as cnt, me.text
FROM "MeetingExtraction" me
JOIN "Meeting" m ON me."meetingId" = m.id
WHERE me."extractionType" = 'objection'
  AND m."meetingType" IN ('customer', 'prospect')
GROUP BY me.category, me.text
ORDER BY cnt DESC
LIMIT 20;
```

### 4. Recent signals for active deals

```sql
SELECT
  co.name as company,
  d.status::text as deal_status,
  s."signalType",
  s.sentiment,
  s.text,
  s."meetingDate"
FROM "Signal" s
JOIN "Company" co ON s."companyId" = co.id
JOIN "Deal" d ON d."companyId" = co.id
WHERE d.status NOT IN ('WON', 'LOST', 'CLOSED')
ORDER BY s."meetingDate" DESC NULLS LAST
LIMIT 50;
```

### 5. Testimonial-worthy quotes

```sql
SELECT
  q.text,
  q."speakerName",
  co.name as company,
  m.date
FROM "Quote" q
JOIN "Meeting" m ON q."meetingId" = m.id
LEFT JOIN "Company" co ON q."companyId" = co.id
WHERE q.sentiment = 'positive'
  AND q."usableFor" IN ('testimonial', 'case_study')
ORDER BY m.date DESC;
```

### 6. Sales learnings that worked

```sql
SELECT me.text, me.category, m.title, m.date
FROM "MeetingExtraction" me
JOIN "Meeting" m ON me."meetingId" = m.id
WHERE me."extractionType" = 'learning'
  AND me.confidence = 'worked'
ORDER BY m.date DESC
LIMIT 30;
```

### 7. Implementation status overview

```sql
SELECT
  i."customerName",
  i.stage::text,
  i."healthStatus"::text,
  i."hasVoiceAgent",
  i."hasChatAgent",
  count(im.id) as total_milestones,
  count(CASE WHEN im."isCompleted" THEN 1 END) as completed_milestones
FROM "Implementation" i
LEFT JOIN "ImplementationMilestone" im ON im."implementationId" = i.id
GROUP BY i.id, i."customerName", i.stage, i."healthStatus", i."hasVoiceAgent", i."hasChatAgent"
ORDER BY i.stage;
```

### 8. Meeting transcript with speakers

```sql
SELECT
  mu."speakerName",
  mu.text,
  mu."startMs" / 1000.0 as seconds_in
FROM "MeetingUtterance" mu
WHERE mu."meetingId" = '<meeting_id>'
ORDER BY mu."startMs";
```

### 9. Company engagement timeline

```sql
SELECT
  a.type,
  a.description,
  a."occurredAt",
  co.name as company
FROM "Activity" a
JOIN "Company" co ON a."companyId" = co.id
WHERE a."companyId" = '<company_id>'
ORDER BY a."occurredAt" DESC;
```

### 10. Deals needing attention (stale + unresolved blockers)

```sql
SELECT
  co.name as company,
  d.status::text,
  d."staleDays",
  d."expectedARR",
  sa.reason as stale_reason,
  sa."suggestedAction"
FROM "Deal" d
JOIN "Company" co ON d."companyId" = co.id
LEFT JOIN "StaleAlert" sa ON sa."dealId" = d.id AND NOT sa."isResolved"
WHERE d."isStale" = true
  AND d.status NOT IN ('WON', 'LOST', 'CLOSED')
ORDER BY d."staleDays" DESC;
```

---

## JOIN Reference

### Core Relationships (what to JOIN on)

| From | To | JOIN ON | Relationship |
|------|-----|---------|-------------|
| Meeting | Company | `Meeting."companyId" = Company.id` | Many-to-one |
| MeetingUtterance | Meeting | `MeetingUtterance."meetingId" = Meeting.id` | Many-to-one |
| MeetingParticipant | Meeting | `MeetingParticipant."meetingId" = Meeting.id` | Many-to-one |
| MeetingExtraction | Meeting | `MeetingExtraction."meetingId" = Meeting.id` | Many-to-one |
| Signal | Meeting | `Signal."meetingId" = Meeting.id` | Many-to-one |
| Signal | Company | `Signal."companyId" = Company.id` | Many-to-one |
| Quote | Meeting | `Quote."meetingId" = Meeting.id` | Many-to-one |
| Quote | Company | `Quote."companyId" = Company.id` | Many-to-one |
| ActionItem | Meeting | `ActionItem."meetingId" = Meeting.id` | Many-to-one |
| ExtractionRun | Meeting | `ExtractionRun."meetingId" = Meeting.id` | Many-to-one |
| ExtractionRun | ExtractionStrategy | `ExtractionRun."strategyId" = ExtractionStrategy.id` | Many-to-one |
| Deal | Company | `Deal."companyId" = Company.id` | Many-to-one |
| Deal | User | `Deal."ownerId" = User.id` | Many-to-one |
| Contact | Company | `Contact."companyId" = Company.id` | Many-to-one |
| Email | Company | `Email."companyId" = Company.id` | Many-to-one |
| Email | Contact | `Email."contactId" = Contact.id` | Many-to-one |
| Email | Deal | `Email."dealId" = Deal.id` | Many-to-one |
| AIScoringResult | Deal | `AIScoringResult."dealId" = Deal.id` | Many-to-one |
| Activity | Company | `Activity."companyId" = Company.id` | Many-to-one |
| Activity | Deal | `Activity."dealId" = Deal.id` | Many-to-one |
| Implementation | Company | `Implementation."companyId" = Company.id` | One-to-one |
| ImplementationMilestone | Implementation | `ImplementationMilestone."implementationId" = Implementation.id` | Many-to-one |
| ImplementationTask | Implementation | `ImplementationTask."implementationId" = Implementation.id` | Many-to-one |
| InvestorContact | InvestorFirm | `InvestorContact."firmId" = InvestorFirm.id` | Many-to-one |
| InvestorInteraction | InvestorFirm | `InvestorInteraction."firmId" = InvestorFirm.id` | Many-to-one |
| SlackExtraction | SlackChannel | `SlackExtraction."channelId" = SlackChannel.id` | Many-to-one |
| TeamUpdate | Company | `TeamUpdate."companyId" = Company.id` | Many-to-one |
| DuplicateGroupMember | DuplicateGroup | `DuplicateGroupMember."groupId" = DuplicateGroup.id` | Many-to-one |

### Indirect Relationships

To connect extractions back to companies when `MeetingExtraction.companyId` is NULL (which is almost always):
```sql
-- Go through Meeting to get the company
SELECT me.*, co.name
FROM "MeetingExtraction" me
JOIN "Meeting" m ON me."meetingId" = m.id
JOIN "Company" co ON m."companyId" = co.id;
```

To connect signals to deals:
```sql
-- Signals don't have dealId directly; go through Company
SELECT s.*, d.id as "dealId", d.status
FROM "Signal" s
JOIN "Company" co ON s."companyId" = co.id
JOIN "Deal" d ON d."companyId" = co.id;
```

---

## Tips for Effective Querying

### 1. Table names are PascalCase and must be quoted
All table and column names are PascalCase. You **must** double-quote them:
```sql
-- Correct
SELECT * FROM "MeetingExtraction" WHERE "extractionType" = 'decision';

-- Wrong (will fail)
SELECT * FROM MeetingExtraction WHERE extractionType = 'decision';
```

### 2. Enum values must be cast
When filtering on enum columns, use the enum type or cast:
```sql
-- These both work
SELECT * FROM "Deal" WHERE status = 'WON';
SELECT * FROM "Deal" WHERE status = 'WON'::"DealStatus";
```

### 3. MeetingExtraction is the richest table
With 14,612 rows across 4 extraction types, this is where most of the AI-generated intelligence lives. Always filter by `extractionType` first.

### 4. Signals connect through Company, not directly to Deal
`Signal` has `companyId` and `meetingId` but NOT `dealId`. To find signals for a deal, join through `Company`:
```sql
Signal.companyId -> Company.id <- Deal.companyId
```

### 5. MeetingExtraction.companyId is almost always NULL
Only 4 of 14,612 rows have `companyId` set. Always join through `Meeting.companyId` instead.

### 6. Meeting.source determines ID format
- Apollo meetings: ID starts with `apollo-`
- Gemini meetings: ID starts with `gemini-`
- Granola meetings: UUID format

### 7. Date fields to watch
- `Meeting.date` — The actual meeting date (use for time-based analysis)
- `Meeting.createdAt` — When the record was imported (data freshness)
- `Quote.meetingDate` / `Signal.meetingDate` — Denormalized from the meeting (convenient for queries)

### 8. Use category + extractionType for precise filtering
```sql
-- All pricing objections
WHERE "extractionType" = 'objection' AND category = 'price'

-- Sales learnings that worked
WHERE "extractionType" = 'learning' AND category = 'sales' AND confidence = 'worked'

-- Strategic decisions in customer meetings
WHERE "extractionType" = 'decision' AND category = 'strategic'
```

### 9. The `confidence` column means different things
- On `MeetingExtraction`: Only for `learning` type — `insight`/`worked`/`didnt_work`
- On `AIScoringResult`: Scoring confidence — `low`/`medium`
- On `AutoAction`: Action confidence — `medium`/`high`
- On `LearnedMatch`/`MatchLog`/`DataAssociation`: Numeric 0-1 match confidence

### 10. Large tables to be careful with
- `MeetingUtterance`: 183,697 rows — always filter by `meetingId`
- `MeetingExtraction`: 14,612 rows — filter by `extractionType`
- `Contact`: 5,961 rows — mostly from Apollo enrichment
- `MeetingParticipant`: 5,185 rows — filter by `meetingId`
