---
ask: "Phase 1 domain model for the customer system — comprehensive entity definitions designed from scratch"
created: 2026-04-14
workstream: customer-system
session: 2026-04-14-a
sources:
  - type: conversation
    description: "Craig and Claude designing the domain model from scratch, informed by all source material"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-14-system-capabilities.md"
    name: "System capabilities — what the system needs to do"
  - type: local
    ref: "projects/product-vision/artifacts/2026-04-13-white-paper.md"
    name: "OS White Paper — kernel primitives and mechanisms"
---

# Phase 1: Domain Model

**Craig Certo — April 14, 2026**

The customer system is the first domain built on the Indemn Operating System. This document defines the Phase 1 entities — the source of truth that answers **"What's the story with [customer]?"** for anyone on the team.

## Design Principles

- **Entities are cheap.** The OS auto-generates CLI, API, UI, and audit trail from entity definitions. A richer model means more capability, not more burden.
- **AI populates everything.** Data is extracted from meetings, emails, Slack, integrations — not manually entered. Design for AI extraction, not human data entry.
- **Enums over free text.** AI classifies more reliably into defined categories.
- **If it passes the entity criteria, make it an entity.** Identity, lifecycle, independence, CLI test, watchable, multiplicity — if it qualifies, don't cram it into a field on something else.
- **The kernel handles connective tissue.** Activity logging (changes collection), notifications (watches), audit trail, role-based access — these are kernel mechanisms, not domain entities.

## Entity Map

Phase 1 has 14 entities across 5 groups:

```
ROOT
  Company ──── Contact (many)
    │
    ├── Deal (many) ──── Conference (source)
    │
    ├── Associate Deployment (many) ──── Associate Type (catalog)
    │
    ├── Outcome (many) ──── Outcome Type (reference)
    │
    ├── Meeting (many) ──┬── Decision (many)
    │                    ├── Commitment (many)
    │                    └── Signal (many)
    │
    └── Task (many, also linked to Deal, Meeting)

REFERENCE
  Associate Type
  Outcome Type
  Stage
```

---

## Entity Definitions

### 1. Company

The root entity. Any business Indemn has a relationship with — prospect, lead, pilot, customer. One entity, one lifecycle.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | Company name |
| type | enum | Broker, MGA_MGU, Carrier, InsurTech, Other |
| cohort | enum | Core_Platform, Graduating, AI_Investments, Prospect |
| tier | enum | Enterprise, Core |
| icp_fit | enum | Strong, Medium, Low |
| source | enum | Conference, Inbound, Referral, Outbound, Existing |
| source_detail | string | Specific conference, referrer name, etc. |
| owner | actor_ref | Account lead |
| standin | actor_ref | Backup account lead |
| website | string | |
| domain | string | |
| linkedin_url | string | |
| industry | string | |
| hq_location | string | |
| employee_count | integer | |
| annual_revenue | decimal | |
| founded_year | integer | |
| ams_system | string | What AMS they use |
| technologies | list[string] | Software and platforms they run |
| specialties | list[string] | Lines of business, focus areas |
| drive_folder_url | string | Transitional — link to existing Google Drive folder |
| notes | text | |

**State Machine:**

```
prospect → pilot → customer → expanding → churned
                             → paused
```

`prospect`: Any company we're in conversation with but haven't started work for. Covers all sales stages — the specific sales stage lives on Deal.

`pilot`: We've started work. Resources are committed. (Kyle's Pipeline Source of Truth: "prospects enter customer tracking at pilot start.")

`customer`: Live in production. Paying or in active engagement.

`expanding`: Active and growing — additional deals, new associates, deeper engagement.

`churned`: Relationship ended.

`paused`: Relationship on hold — not dead, but not active. Replaces "parked" from Kyle's docs.

**Relationships:** Has many Contacts, Deals, Associate Deployments, Outcomes, Meetings, Tasks, Signals, Commitments, Decisions.

---

### 2. Contact

A person at a company. The "who do we talk to" piece.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company |
| name | string | Full name |
| title | string | Job title |
| email | string | |
| phone | string | |
| role | enum | Decision_Maker, Executive_Sponsor, Technical, Day_to_Day, Champion, Influencer, End_User |
| is_primary | boolean | Primary contact for this company |
| how_met | enum | Conference, LinkedIn, Email_Intro, Referral, Discovery_Call, Inbound, Cold_Outreach |
| linkedin_url | string | |
| notes | text | |

**State Machine:** None. Contacts are active by default. If someone leaves the company, a new Contact is created at their new company; the old record remains as history.

---

### 3. Deal

A specific business opportunity with a company. The sales stages live here, not on Company.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company |
| name | string | What the deal is ("Initial engagement", "Voice expansion", "Email intelligence pilot") |
| primary_contact | entity_ref | Relationship to Contact — who we're working with on their side |
| owner | actor_ref | Who on our team owns this deal |
| stage | enum | See state machine |
| expected_arr | decimal | Expected annual recurring revenue |
| primary_outcome | enum | Revenue_Growth, Operational_Efficiency, Client_Retention, Strategic_Control |
| source | enum | Conference, Inbound, Referral, Outbound |
| source_conference | entity_ref | Relationship to Conference, if source is conference |
| company_fit_score | integer | 1-5 |
| relationship_score | integer | 1-5 |
| eagerness_score | integer | 1-5 |
| use_case_score | integer | 1-5 |
| milestone_score | integer | 1-5 |
| composite_score | computed | Average of the five scores |
| warmth | enum | Cold, Cool, Warm, Hot, On_Fire |
| probability | computed | Auto-calculated from stage |
| weighted_value | computed | expected_arr × probability × (composite_score / 5) |
| stale_threshold_days | computed | Derived from stage (14 for contact, 5 for verbal) |
| days_since_activity | computed | Days since last entity change or related Task/Meeting |
| is_stale | computed | days_since_activity > stale_threshold_days |
| follow_up_date | date | When the next follow-up should happen |
| competitive_notes | text | What we know about competition on this deal |
| lost_reason | text | If lost, why |
| notes | text | |

**State Machine:**

```
contact → discovery → demo → proposal → negotiation → verbal → signed → lost
                                                                       → parked
```

Probability auto-calculated: contact=5%, discovery=15%, demo=25%, proposal=40%, negotiation=60%, verbal=80%, signed=100%.

When a Deal transitions to `signed`, a watch triggers the Company to evaluate its own state — if the Company is `prospect`, it transitions to `pilot` or `customer`.

**Relationships:** Belongs to Company. Has many Tasks. May reference a Conference as source. Links to Associate Deployments that result from this deal.

---

### 4. Conference

A specific event Indemn attends. Manages preparation, lead tracking, and ROI.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | "InsurTechNY Spring 2026" |
| location | string | City, venue |
| date_start | date | |
| date_end | date | |
| owner | actor_ref | Who's coordinating Indemn's presence |
| cost | decimal | Total cost of attendance (booth, travel, etc.) |
| attendee_list_ref | string | Reference to attendee data source |
| attendee_count | integer | Total attendees at the conference |
| leads_collected | computed | Count of Deals with source_conference = this conference |
| contacts_collected | computed | Count of Contacts with how_met referencing this conference |
| revenue_generated | computed | Sum of signed Deal ARR where source_conference = this conference |
| roi | computed | revenue_generated / cost |
| notes | text | |

**State Machine:**

```
planning → pre_event → active → follow_up → complete
```

`planning`: Researching attendees, preparing materials, setting up demos.

`pre_event`: Outreach to attendees, scheduling meetings.

`active`: Conference is happening. Collecting contacts, having conversations.

`follow_up`: Conference is over. Working through leads, scheduling demos, sending materials.

`complete`: All leads processed. ROI calculated.

**Relationships:** Referenced by Deals (as source). Referenced by Contacts (how_met context).

---

### 5. Associate Deployment

A specific associate deployed (or planned) for a specific customer.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company |
| deal | entity_ref | Relationship to Deal this deployment came from |
| associate_type | entity_ref | Relationship to Associate Type (catalog entry) |
| name | string | Specific instance name ("GIC Email Intelligence", "Branch Front Desk") |
| outcome | entity_ref | Relationship to Outcome this deployment contributes to |
| channels | list[enum] | Voice, Chat, Email, Copilot |
| tier | enum | Tier_1, Tier_2, Tier_3 (quick win, real value, expansion) |
| owner | actor_ref | Who's building/maintaining this |
| integration_requirements | list[string] | What external systems need to be connected |
| escalation_paths | text | How and when this associate escalates to a human |
| success_metrics | text | How we measure whether this deployment is working |
| notes | text | |

**State Machine:**

```
planned → building → testing → live → paused → retired
```

**Relationships:** Belongs to Company. Belongs to Deal. References Associate Type. References Outcome. Has many Tasks.

---

### 6. Outcome

A per-customer mapping to one of the Four Outcomes. Tracks which deployments contribute and what value is being generated.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company |
| outcome_type | entity_ref | Relationship to Outcome Type |
| associate_deployments | list[entity_ref] | Which deployments contribute to this outcome |
| notes | text | Qualitative observations about value being delivered |

**State Machine:** None. Outcomes evolve over time. The changes collection tracks how the data changes. Value/ROI calculation fields are added in a later phase when the underlying data (disposition maps, performance metrics, unit economics) exists to support them.

**Relationships:** Belongs to Company. References Outcome Type. Links to Associate Deployments.

---

### 7. Meeting

A meeting with a customer or prospect. The event itself — intelligence extracted from it becomes separate entities.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company |
| contacts | list[entity_ref] | Which Contacts were present |
| team_members | list[actor_ref] | Which Indemn Actors were present |
| title | string | Meeting title |
| date | datetime | When the meeting occurred |
| duration_minutes | integer | How long the meeting lasted |
| source | enum | Gemini, Granola, Google_Meet, Zoom, Phone, In_Person |
| transcript_ref | string | Reference to transcript source (Drive doc ID, etc.) |
| recording_ref | string | Reference to recording (Drive file ID, etc.) |
| summary | text | AI-generated meeting summary |
| notes | text | |

**State Machine:**

```
recorded → processed → intelligence_extracted
```

`recorded`: Meeting happened, we have a reference to the transcript/recording.

`processed`: AI has generated a summary.

`intelligence_extracted`: AI has extracted Decisions, Action Items (→ Tasks), Commitments, and Signals as separate entities.

**Relationships:** Belongs to Company. References Contacts and Actors. Has many Decisions, Commitments, Signals. Generates Tasks (action items).

---

### 8. Task

A unit of work that needs to be done. Unifies deal next-steps, meeting action items, implementation tasks (Phase 2), and manual tasks into one entity.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company (always present for context) |
| title | string | What needs to be done |
| description | text | Details |
| assignee | actor_ref | Who is responsible |
| owner_type | enum | Internal, Customer (is this our task or theirs?) |
| due_date | date | When it's due |
| priority | enum | Low, Medium, High, Critical |
| category | enum | Technical, Training, Testing, Compliance, Sales, Relationship, Administrative |
| source | enum | Meeting, Deal, Implementation, Playbook, Manual |
| source_meeting | entity_ref | If from a meeting, which one |
| source_deal | entity_ref | If from a deal, which one |
| source_implementation | entity_ref | If from an implementation (Phase 2), which one |
| effort | enum | Small, Medium, Large |
| notes | text | |

**State Machine:**

```
open → in_progress → completed → cancelled
                   → blocked → in_progress
```

`blocked`: Something is preventing progress. Watchable — blocked tasks should surface to managers.

**Relationships:** Belongs to Company. May reference Meeting, Deal, or Implementation as source. Assigned to an Actor.

**Why this is one entity, not separate Action Item / Deal Task / Implementation Task:** They all have identity, lifecycle, assignee, due date, priority. The only difference is source. A unified Task entity lets you query "what are all the open tasks for GIC?" regardless of whether they came from a meeting, a deal, or an implementation. One entity, one queue.

---

### 9. Commitment

A promise made by Indemn to a customer, or by a customer to Indemn. Extracted from meetings, tracked for accountability.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company |
| meeting | entity_ref | Which meeting this was extracted from |
| description | text | What was promised |
| made_by | string | Who made the promise (person name — could be Indemn team or customer) |
| made_by_side | enum | Indemn, Customer |
| made_to | string | Who it was made to |
| due_date | date | When it should be fulfilled (may be vague — "by end of month") |
| due_date_precision | enum | Exact, Approximate, Unspecified |
| notes | text | |

**State Machine:**

```
open → fulfilled → missed → dismissed
```

`missed`: The due date passed without fulfillment. Watchable — missed commitments should alert the account owner.

`dismissed`: Explicitly acknowledged as no longer relevant (circumstances changed, customer rescinded, etc.).

**Relationships:** Belongs to Company. References Meeting. May generate a Task for tracking the work needed to fulfill it.

**Why this is separate from Task:** A commitment is a PROMISE — it's about accountability and trust. A task is WORK — it's about execution. Commitment "we'll have the renewal engine ready by Q2" might generate multiple tasks. The commitment tracks whether the promise was kept; the tasks track the work to keep it.

---

### 10. Signal

A health, expansion, or risk indicator extracted from a meeting or other source. Used for health scoring and early warning.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company |
| meeting | entity_ref | Which meeting this was extracted from (if meeting-sourced) |
| type | enum | Health_Positive, Health_Negative, Expansion, Churn_Risk, Blocker, Champion_Identified, Budget_Concern, Competitor_Mentioned, Escalation, Satisfaction |
| description | text | What was observed |
| source | enum | Meeting, Email, Slack, Usage_Data, Manual |
| severity | enum | Low, Medium, High |
| attributed_to | string | Who exhibited or stated this signal (person name) |
| notes | text | |

**State Machine:** None. Signals are point-in-time observations. They don't transition. They accumulate and are aggregated for health scoring.

**Relationships:** Belongs to Company. May reference Meeting.

**Why this is an entity:** Signals are queryable across meetings and time periods. "Show me all churn risk signals for GIC in the last 30 days." "How many expansion signals does INSURICA have?" Health scoring aggregates signals. You can't do this if signals are buried as text in Meeting notes.

---

### 11. Decision

A decision made in a meeting or conversation that affects the customer relationship or Indemn's approach.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| company | entity_ref | Relationship to Company (null if company-wide/internal decision) |
| meeting | entity_ref | Which meeting this was extracted from |
| description | text | What was decided |
| decided_by | string | Who made or announced the decision |
| participants | list[string] | Who was part of the decision |
| rationale | text | Why this decision was made (if captured) |
| impact | enum | Customer_Scope, Pricing, Technical, Timeline, Staffing, Strategy, Process |
| supersedes | entity_ref | If this decision replaces a previous one, link to it |
| notes | text | |

**State Machine:** None. Decisions are recorded facts. They may be superseded by later decisions (the `supersedes` field handles this).

**Relationships:** May belong to Company (or be company-agnostic). References Meeting. May reference a superseded Decision.

**Why this is an entity:** "Distinguished ARR is $12K, not $250K" is a decision that changes how you think about the customer. "GIC lead is Craig+Kyle, not Jonathan" changes staffing. These need to be findable: "what decisions have we made about GIC?" The changes collection records WHAT changed; Decision records WHY and by whom.

---

### 12. Associate Type (Reference Entity)

The catalog of associates Indemn offers. Updated as the product evolves.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | "Front Desk Associate", "Quote Associate", etc. |
| engine | enum | Revenue, Efficiency, Retention, Control |
| maturity | enum | Proven, Ready, In_Dev |
| deployment_modes | list[enum] | Voice, Chat, Copilot |
| description | text | What this associate does |
| proof_points | text | Evidence from existing deployments |
| standard_checklist | text | Default delivery checklist for deploying this type |
| required_inputs | text | What we need from the customer to deploy |
| integration_requirements | list[string] | External systems typically needed |
| typical_timeline | string | How long deployment typically takes |
| escalation_paths | text | Standard escalation patterns |
| success_metrics | text | How we measure success for this type |
| notes | text | |

**State Machine:** None for Phase 1. Maturity (Proven/Ready/In_Dev) is a field, not a state machine — it doesn't enforce transitions.

**Relationships:** Referenced by Associate Deployments.

---

### 13. Outcome Type (Reference Entity)

The Four Outcomes framework. Small, stable, but referenced everywhere.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | Revenue Growth, Operational Efficiency, Client Retention, Strategic Control |
| engine | string | Revenue Engine, Efficiency Engine, Retention Engine, Control Engine |
| description | text | What this outcome means for the customer |
| key_metrics | list[string] | How this outcome is measured |
| proof_points | text | Cross-customer evidence |
| language_guidance | text | How to talk about this outcome (from Language Rules doc) |

**State Machine:** None. These are the four pillars. They don't change.

**Relationships:** Referenced by Outcomes.

---

### 14. Stage (Reference Entity)

Defines the deal pipeline stages with probability and staleness thresholds.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | Contact, Discovery, Demo, Proposal, Negotiation, Verbal, Signed |
| probability | decimal | 0.05, 0.15, 0.25, 0.40, 0.60, 0.80, 1.00 |
| stale_after_days | integer | 14, 14, 10, 10, 7, 5, N/A |
| definition | text | What this stage means |
| order | integer | Sequence position |

**State Machine:** None. This is a lookup table.

**Relationships:** Referenced by Deals.

---

## Summary

| # | Entity | Type | State Machine | Key Purpose |
|---|--------|------|---------------|-------------|
| 1 | Company | Domain | prospect → pilot → customer → expanding → churned/paused | The root — who they are, relationship status |
| 2 | Contact | Domain | None | People at companies |
| 3 | Deal | Domain | contact → discovery → demo → proposal → negotiation → verbal → signed/lost/parked | Business opportunities, pipeline tracking |
| 4 | Conference | Domain | planning → pre_event → active → follow_up → complete | Events, lead source, ROI |
| 5 | Associate Deployment | Domain | planned → building → testing → live → paused → retired | What's deployed per customer |
| 6 | Outcome | Domain | None | Value mapping per customer |
| 7 | Meeting | Domain | recorded → processed → intelligence_extracted | Customer meetings with intelligence extraction |
| 8 | Task | Domain | open → in_progress → completed/cancelled, blocked | All work items from any source |
| 9 | Commitment | Domain | open → fulfilled → missed → dismissed | Promises tracked for accountability |
| 10 | Signal | Domain | None | Health/expansion/risk indicators |
| 11 | Decision | Domain | None | Recorded decisions with rationale |
| 12 | Associate Type | Reference | None | Product catalog |
| 13 | Outcome Type | Reference | None | Four Outcomes framework |
| 14 | Stage | Reference | None | Deal pipeline stages |

**11 domain entities + 3 reference entities = 14 total.**

The OS kernel provides: activity logging (changes collection), notifications (watches on roles), audit trail, role-based access, CLI/API/UI auto-generation. None of these need to be modeled as domain entities.

---

## Key Relationships

```
Company (1) ──── (many) Contact
Company (1) ──── (many) Deal
Company (1) ──── (many) Associate Deployment
Company (1) ──── (many) Outcome
Company (1) ──── (many) Meeting
Company (1) ──── (many) Task
Company (1) ──── (many) Commitment
Company (1) ──── (many) Signal
Company (1) ──── (many) Decision

Deal (many) ──── (1) Conference [source]
Deal (1) ──── (many) Task
Deal (1) ──── (1) Contact [primary_contact]

Associate Deployment (many) ──── (1) Associate Type
Associate Deployment (many) ──── (1) Outcome

Meeting (1) ──── (many) Decision
Meeting (1) ──── (many) Commitment
Meeting (1) ──── (many) Signal
Meeting (1) ──── (many) Task [action items]

Commitment ──── may generate Task
Decision ──── may supersede Decision

Task ──── source: Meeting | Deal | Implementation | Playbook | Manual
```

## What the Team Gets on Day One

Once these entities are defined on the OS:

- **Kyle** can `indemn company list --stage customer` and see all active customers. Can `indemn company get GIC` and see the full picture. Can `indemn deal list --is-stale true` and see what needs attention. Can `indemn commitment list --status missed` and see what promises we've broken.

- **George** can `indemn task list --assignee george --status open` before a customer call and know exactly what's on his plate. Can `indemn meeting list --company "Union General" --limit 5` and see recent meeting history. Can `indemn signal list --company "JM" --type expansion` and see growth opportunities.

- **Peter** knows when something goes live because a watch on Associate Deployment state=`live` notifies the team. Can `indemn task list --status blocked` and see what's stuck.

- **Cam** can `indemn company list --cohort Core_Platform` and see the portfolio. Can `indemn signal list --type churn_risk` and see red flags across all customers.

- **Ganesh** can see delivery status per customer through the auto-generated UI. The base UI renders entity lists, detail views, and state machines without any custom UI code.

The UI, CLI, and API all exist the moment the entities are defined. AI populates the data from existing sources (Pipeline API, Google Sheets, meeting transcripts, Slack). The changes collection records every update. Watches notify the right people when things change.
