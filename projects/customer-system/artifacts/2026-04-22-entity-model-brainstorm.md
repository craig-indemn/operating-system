---
ask: "Brainstorm the next evolution of the customer system entity model — Email, Interaction, Operation, Opportunity, Proposal, Phase, Document, Associate rename"
created: 2026-04-22
workstream: customer-system
session: 2026-04-22-roadmap
sources:
  - type: conversation
    description: "Craig + Claude brainstorming session, April 21-22 2026"
  - type: local
    ref: "projects/customer-system/artifacts/context/kyle-exec/"
    description: "Kyle's EXEC folder — PLAYBOOK-v2, data dictionaries, 6 leads, MAP"
  - type: google-drive
    ref: "1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph"
    description: "Cam's proposal folder — Alliance, Branch, Johnson, GIC, Charley, Physicians Mutual, SaaS Agreement"
  - type: local
    ref: "projects/customer-system/artifacts/context/2026-04-21-kyle-craig-call-transcript.txt"
    description: "Kyle/Craig call April 21 — prospect strategy, deal priorities, using Kyle as guinea pig"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-14-system-capabilities.md"
    description: "17 functional areas, ~130 capabilities from all stakeholders"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-14-problem-statement.md"
    description: "7 concepts with evidence"
---

# Entity Model Brainstorm — Checkpoint 2 (Field-Level)

**Status: COMPLETE — all entities designed field-by-field. Ready for implementation planning.**

---

## The Goal

End-to-end understanding of every customer: every interaction, every piece of data shared, every minute of work done, anything delivered for them. Organized in an intuitive way that works within the OS (associates, watches, wiring). Systematically replicable for every customer. The team uses this every day and it becomes essential.

**First target: Alliance Insurance.** Mine the data, build the comprehensive picture, make it replicable.

---

## The Flow

```
Email, Meeting (raw data sources)
    ↓ [associates classify, extract, link]
Interaction (unified timeline — external + internal)
    ↓ [informs]
Company profile + Operations + Opportunities
    ↓ [maps to our products]
Proposal + Phases (what we'll deliver)
    ↓ [accepted → delivery begins]
Associates deployed, Tasks created, delivery tracked
    ↓ [internal interactions during delivery]
Back into the Interaction timeline
```

Everything feeds everything else. The system is a loop.

The Proposal is the **culmination** of the pre-customer journey. Everything before it (discovery, interactions, data gathering, analysis) systematically feeds into it. The OS makes that pipeline visible and structured. Information gathering leads to and informs the proposal. The proposal is the "deliverable" to the prospect before they become a customer.

---

## Design Principles

1. **Entities ARE the context layer.** Having raw information in entities is the whole point. No harm in rich entities — entities are cheap, the OS auto-generates everything.

2. **No fluff fields.** Every field is either structured data (dates, amounts, enums, booleans), a relationship to another entity, or specific content that IS the source of truth for that data. No narrative summaries duplicating information that lives elsewhere. No keyword fields.

3. **Summaries only where the entity IS the source of truth.** Meeting summary on Meeting is fine — Meeting is the source of truth for that summary. Random `customer_context` text on Proposal is not — that data lives on Company.

4. **Any standalone object with specific structural characteristics should be its own entity.** Apply the 7 entity criteria. If it passes, make it an entity.

5. **Documents for narrative, entities for structured facts.** Both live in the system. The entities are actionable and queryable. The documents are the full context.

6. **Model how we actually do things.** The system should match the team's mental model.

7. **Gaps are visible.** Empty fields = gaps we need to fill. The system shows us what we don't know.

8. **If you can't point to an entity for it, it probably shouldn't be a field.** Text fields describing things that ARE other entities are fluff. The proposal is generated FROM entities — the entities are the structured data, the document is the rendered output.

---

## Entity Definitions — Final Field-Level Design

### Email

Raw Gmail messages. Source of truth for email content — should be able to recreate the email entirely.

| Field | Type | Description |
|-------|------|-------------|
| message_id | str | Gmail unique ID |
| thread_id | str | Gmail thread grouping |
| company | → Company | Which customer this relates to |
| sender | str | Email address of sender |
| sender_contact | → Contact (optional) | If sender is a known contact |
| sender_employee | → Employee (optional) | If sender is Indemn team |
| recipients | list str | TO addresses |
| cc | list str | CC addresses |
| bcc | list str | BCC addresses |
| date | datetime | When sent/received |
| subject | str | Subject line |
| body | str | Full content — HTML or plain text |
| has_attachments | bool | Whether attachments exist |
| interaction | → Interaction (optional) | Which interaction this email is part of |

**State machine:** `received → classified → processed`

**Attachments:** When processed, attachments automatically become Document entities linked to the Company.

---

### Document

Any file or artifact exchanged or created. Pointers to Google Drive files, email attachments, analysis documents, customer-shared data.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer this relates to |
| name | str | Filename or title |
| creator_employee | → Employee (optional) | If Indemn team created it |
| creator_contact | → Contact (optional) | If customer created/shared it |
| created_date | datetime | When created or shared |
| source | enum | google_drive, email_attachment, manual_upload |
| source_email | → Email (optional) | If this came from an attachment |
| drive_file_id | str (optional) | Google Drive file ID |
| drive_url | str (optional) | Direct link to Drive |
| content | str (optional) | Raw text content, if text-based |
| mime_type | str | PDF, DOCX, CSV, image, etc. |
| file_size | int (optional) | Bytes |

**No state machine.** Documents are point-in-time artifacts.

**Relationship to Proposal:** A Proposal has `source_document` — the rendered file shared with customer. The Proposal entity IS the source of truth; the Document is the rendered output.

---

### Meeting (exists — add field)

Already exists with transcripts, participants, notes. One addition:

| Field | Type | Description |
|-------|------|-------------|
| interaction | → Interaction (optional) | Which interaction this meeting is part of |

All other existing fields remain unchanged.

---

### Interaction

Unified timeline of every touchpoint — external (with customer) AND internal (work done for customer). The connective tissue of the entire system.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer this is about/for |
| deal | → Deal (optional) | If related to a specific deal |
| type | enum | email, meeting, call, slack, in_person, conference |
| scope | enum | external (with customer), internal (about/for customer) |
| date | datetime | When it occurred |
| duration | int (optional) | Minutes, for meetings/calls |
| participants_contacts | list → Contact | Customer-side people involved |
| participants_employees | list → Employee | Our people involved |
| summary | str | Source of truth for what happened in this touchpoint |

**State machine:** `logged → processed`

**Scope:** External = with customer. Internal = about/for customer (Craig meeting with Jonathan about Alliance's implementation is an Interaction linked to Alliance).

**Raw data links TO Interaction:** Email has `interaction` field. Meeting has `interaction` field. The Interaction doesn't have source fields — sources point to it. This scales naturally as we add raw data entities (Slack, etc.).

**Slack compatibility:** Interaction operates at thread level, not individual message level. Customer-specific channels and tagged messages are sources. Individual ambient mentions are too noisy.

**Intelligence extraction:** When an Interaction is processed, it may produce Task, Commitment, Decision, and/or Signal entities — all of which link back to the Interaction.

---

### Operation

A business process a customer runs. The "what they do" layer. From Kyle's Branch template: the Disposition Map.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| name | str | Descriptive: "Renewal outreach", "Email inbox triage" |
| department | str | How they organize it: "Service", "Renewals", "Sales" |
| channel | str | Primary channel: phone, email, web, portal, mixed |
| annual_volume | int (optional) | How many per year |
| staff_count | int (optional) | How many people work on this |
| automation_level | enum | manual, partial, automated |
| tools | list str | What systems they use for this operation |

**No state machine.** Operations are facts about the business. They get updated as we learn more.

**Note:** Field values (department, channel) are intentionally strings rather than rigid enums. Real data from customers will teach us the natural categories. Tighten into enums when patterns emerge.

**Future:** LineOfBusiness will be its own entity that Operations link to.

---

### CustomerSystem

A system/tool a customer uses. Ties to our Integration entities — when we deploy, we know what we're connecting to.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| name | str | "Applied Epic", "Dialpad", "BT Core", "Salesforce" |
| type | str | AMS, CRM, Phone, Email, Billing, Data Provider |
| integration | → Integration (optional) | Links to our OS integration if we have an adapter |

**No state machine.**

---

### BusinessRelationship

Company-to-company relationships. Who a customer works with — carriers, agencies, vendors, partners.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Our customer |
| related_company | → Company (optional) | If the related company is in our system |
| related_name | str | Name if not in our system ("Everett Cash Mutual") |
| type | str | carrier, agency, MGA, vendor, partner, reinsurer |

**No state machine.**

---

### Opportunity

An identified gap in a customer's operations, mapped to our products. The bridge between "what they do" and "what we can deliver."

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| operation | → Operation | Which business process has this gap |
| name | str | "Unanswered renewal calls", "Manual email triage" |
| mapped_associate | → AssociateType (optional) | What we'd deploy to solve it |
| mapped_outcome | → OutcomeType (optional) | Which Four Outcome it serves |
| source_interaction | → Interaction (optional) | Discovered through a conversation |
| source_document | → Document (optional) | Discovered through analysis/document review |
| phase | → Phase (optional) | Which proposal phase addresses this opportunity |

**State machine:** `identified → validated → proposed → addressed → resolved`

**Flow:** Identified through discovery → validated with customer → included in a Proposal Phase (`proposed`) → Phase is in progress (`addressed`) → associate is live and working (`resolved`).

---

### Proposal

Source of truth for what we're delivering to a customer. The culmination of discovery. The document shared with the customer is a rendering of this entity and its related entities (Phases, Opportunities, Commitments, Tasks).

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| deal | → Deal | Which deal this proposal is for |
| version | int | Proposal version (1, 2, 3...) |
| source_document | → Document (optional) | The rendered file shared with customer |
| prepared_for | → Contact | Primary recipient |
| prepared_by | → Employee | Who prepared it |
| date_prepared | date | When prepared |
| date_sent | date (optional) | When sent to customer |

**State machine:** `drafting → internal_review → sent → under_review → accepted → rejected → superseded`

**No commercial terms on Proposal itself.** Total investment and payment structure are the culmination of the Phase entities. No duplicate data.

**Proposal versioning:** When v2 is created, v1 transitions to `superseded`.

**Design decision:** The Proposal entity IS the source of truth. The document (source_document) is a rendering. An LLM generates the proposal document by reading the Proposal, its Phases, linked Opportunities, Commitments, Tasks, and AssociateTypes.

---

### Phase

Per-proposal phased delivery plan. Each proposal has 2-5 phases. The substance of what we deliver.

| Field | Type | Description |
|-------|------|-------------|
| proposal | → Proposal | Which proposal this phase belongs to |
| phase_number | int | Order (1, 2, 3) |
| name | str | "CRAWL — Revenue Growth" |
| timeline | str | "Weeks 1-4", "Months 2-3" |
| outcome | → OutcomeType | Which Four Outcome this phase delivers |
| associates | list → AssociateType | What we deploy in this phase |
| investment | decimal | Dollar amount per period |
| investment_period | enum | monthly, quarterly, annually, one_time |
| commitment_months | int (optional) | Contract commitment length |
| is_pilot | bool | Whether this is a waived/free pilot phase |

**State machine:** `not_started → in_progress → complete → skipped`

**No text blob fields.** Everything that was previously text (customer_commitment, indemn_deliverables, success_metrics, entry_criteria) is handled by related entities:
- **Customer commitments** → Commitment entities with `phase` field
- **Indemn deliverables/work** → Task entities with `phase` field
- **Success metrics** → Live on Opportunity entities (the gap being closed)
- **Entry criteria / go-no-go** → Derivable from entity states (Task completion + Commitment fulfillment)

**Design decision:** No phases without a proposal. Phases always belong to a Proposal.

---

### Associate (renamed from AssociateDeployment)

An actual deployed associate for a customer. The real thing running in production. AssociateType is the template; Associate is the instance.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| associate_type | → AssociateType | Which template it's built from |
| name | str | "Alliance Renewal Associate", "GIC Email Classifier" |
| phase | → Phase (optional) | Which proposal phase deployed it |
| deal | → Deal (optional) | Which deal it relates to |
| owner | → Employee | Who built/maintains it |
| channels | list str | voice, chat, email, copilot |
| org_id | str | Tiledesk/platform organization ID |
| bot_id | str | Bot configuration ID in MongoDB |
| url | str | Unique URL for this associate |

**State machine:** `planned → building → testing → live → paused → retired`

---

### Task (exists — updated fields)

A unit of work. Updated to connect to new entities.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| title | str | What needs to be done |
| description | str | Details |
| assignee | → Employee | Who's responsible |
| due_date | date (optional) | When it's due |
| priority | enum | low, medium, high, critical |
| phase | → Phase (optional) | If part of a proposal phase |
| interaction | → Interaction (optional) | If came from a conversation |
| deal | → Deal (optional) | If related to a deal |

**State machine:** `open → in_progress → completed → cancelled → blocked`

**Removed from original design:** `owner_type` (derivable), `category` (naive enum), `source` (derivable from relationships), `effort` (vague), `source_meeting`/`source_deal`/`source_implementation` (replaced by `interaction`, `deal`, `phase`), `notes` (description is sufficient).

---

### Commitment (exists — updated fields)

A promise made by Indemn to a customer, or by a customer to Indemn. Tracked for accountability.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| made_by | str | Who made the promise (name) |
| made_by_side | enum | indemn, customer |
| made_to | str | Who it was made to |
| due_date | date (optional) | When it should be fulfilled |
| phase | → Phase (optional) | If a proposal-phase commitment |
| interaction | → Interaction (optional) | If extracted from a conversation |
| description | str | What was promised |

**State machine:** `open → fulfilled → missed → dismissed`

**Removed from original design:** `due_date_precision` (over-engineering), `meeting` (replaced by `interaction`), `notes` (description is sufficient).

---

### Decision (exists — updated fields)

A decision that affects the customer relationship or Indemn's approach. The "why" behind changes.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| interaction | → Interaction (optional) | Where this decision was made |
| description | str | What was decided |
| decided_by | str | Who made/announced it |
| rationale | str (optional) | Why, if captured |
| supersedes | → Decision (optional) | If this replaces a previous decision |

**No state machine.** Decisions are recorded facts. They can be superseded by later decisions.

---

### Signal (exists — updated fields)

Health, expansion, or risk indicators. Point-in-time observations that accumulate for health scoring.

| Field | Type | Description |
|-------|------|-------------|
| company | → Company | Which customer |
| interaction | → Interaction (optional) | Where this signal was observed |
| type | enum | health_positive, health_negative, expansion, churn_risk, blocker, champion, budget_concern, competitor, satisfaction |
| description | str | What was observed |
| severity | enum | low, medium, high |
| attributed_to | str | Who exhibited this signal |

**No state machine.** Signals are point-in-time observations.

---

## Existing Entities (unchanged)

| Entity | Records | Notes |
|--------|---------|-------|
| **Company** | 88 | Hub entity. May get richer profile fields over time. Understanding comes from related entities, not bloated fields. |
| **Contact** | 92 | People at companies. No changes. |
| **Deal** | 6 | Business opportunities through sales funnel. No changes. |
| **Employee** | 15 | Indemn team members linked to Actors. No changes. |
| **AssociateType** | 24 | The 24-item catalog/templates. No changes. |
| **Conference** | 2 | Events and lead source. No changes. |
| **Stage** | 7 | Pipeline stages reference data. No changes. |
| **OutcomeType** | 4 | Four Outcomes framework. No changes. |

**Removed:** SuccessPhase (replaced by Phase on Proposal).

---

## Entity Relationship Map

```
Company (hub)
├── Contact (many)
├── Deal (many)
│   └── Proposal (many — versioned)
│       └── Phase (many — the delivery plan)
│           ├── ← Task (many — Indemn work items)
│           ├── ← Commitment (many — customer commitments)
│           ├── ← Opportunity (many — gaps this phase addresses)
│           └── → AssociateType (many — what we deploy)
├── Operation (many — what they do)
│   └── ← Opportunity (many — gaps identified)
├── CustomerSystem (many — what tools they use)
├── BusinessRelationship (many — who they work with)
├── Associate (many — actual deployed instances)
├── Interaction (many — unified timeline)
│   ├── ← Email (many — raw email data)
│   ├── ← Meeting (many — raw meeting data)
│   ├── ← Task (many — extracted action items)
│   ├── ← Commitment (many — extracted promises)
│   ├── ← Decision (many — extracted decisions)
│   └── ← Signal (many — extracted indicators)
├── Document (many — files and artifacts)
├── Email (many — raw Gmail messages)
└── Meeting (many — raw meeting data)
```

---

## What Cam's Proposals Taught Us

Read 6 proposals + SaaS Agreement from Cam's Drive folder. Key patterns:

1. **Every proposal anchors on outcomes, not products.** "Revenue Capacity" and "Resolution Rate" — not "we'll give you 3 chatbots."
2. **Always phased: Crawl-Walk-Run.** Phase 1 is free/cheap pilot. Phase 2 is real value. Phase 3 is expansion.
3. **Customer-specific pain + quantified impact.** Alliance: 100+ missed calls/week = $260K at risk.
4. **Associates bundled as Engines.** Customers buy Engines/Outcomes, not individual associates.
5. **Implementation roles defined.** What Indemn does vs what the customer provides.
6. **Standard SaaS Agreement embedded.** HITL, IP split, 98.9% uptime SLA, 60-day termination.

---

## What Kyle's Call (Apr 21) Taught Us

1. **Start with Alliance** — first deep-dive target.
2. **Use Kyle as guinea pig** — mine his email, Drive, calendar.
3. **Get to source of truth first** — messy and complete beats clean and sparse.
4. **Historical data informs the playbook** — process what we've done, then define what we should do.
5. **Multiple input paths** — email, meetings, Drive, Slack, manual. All auto-hydrated. (The "Rocky problem.")
6. **Export to spreadsheet** — needed for adoption.
7. **Ledger of daily changes** — "I'd rather have 20 things with 5 wrong."

---

## Implementation Plan — Alliance First

### Who Does What

| Actor | Responsibility |
|-------|---------------|
| **Associates (automated)** | Email classification, Interaction synthesis, Document creation from attachments, intelligence extraction (Tasks, Decisions, Signals, Commitments) |
| **Craig + Claude Code (CLI)** | Entity definitions, Operations, Opportunities, Proposals + Phases, associate/watch configuration, review of associate outputs |
| **Human-in-the-loop** | Validate classifications, review extracted intelligence, approve Proposals before sending |

### Associates

| Associate | Trigger | Input | Output |
|-----------|---------|-------|--------|
| **Email Classifier** | Watch: Email created | Email entity | Links Company + Contacts, transitions to `classified` |
| **Interaction Synthesizer** | Watch: Email → `classified`, Meeting created | Email or Meeting | Creates Interaction, creates Documents from attachments, transitions Email to `processed` |
| **Intelligence Extractor** | Watch: Interaction created | Interaction (reads linked Email/Meeting content) | Creates Tasks, Decisions, Commitments, Signals; transitions Interaction to `processed` |
| **Proposal Writer** (Wave 5) | Manual invocation | Company + Operations + Opportunities + Phases + AssociateTypes | Generates proposal Document |

### Watches

| Watch | Entity | Event | Fires |
|-------|--------|-------|-------|
| Email arrived | Email | created | Email Classifier |
| Email classified | Email | transitioned to `classified` | Interaction Synthesizer |
| Meeting arrived | Meeting | created | Interaction Synthesizer |
| Interaction logged | Interaction | created | Intelligence Extractor |

### Waves

**Wave 1: Entity Definitions** — create all entities via CLI. Pure structure, no data yet.

**Wave 2: Wiring** — create roles, associates (with skills), and watches. The system becomes reactive.

**Wave 3: Gmail Adapter + Ingestion** — extend Google Workspace integration for Gmail API. Pull Kyle's Alliance emails. Watches fire automatically: emails classify → interactions synthesize → intelligence extracts.

**Wave 4: Human Enrichment** — Craig via CLI populates what requires judgment: Operations (from 30-page analysis), Opportunities (mapping problems to products), CustomerSystem, BusinessRelationship. Reviews and corrects associate outputs.

**Wave 5: Proposal Generation** — create Proposal v2 + Phases for Alliance. Link Opportunities, Commitments, Tasks to Phases. Proposal Writer associate generates the document for Christopher.

### The Alliance Deliverable

Everything leads to: **a generated proposal for Alliance based on structured entity data.** Christopher Cook returns from Austin. We have an updated proposal (v2, renewal wedge pivot) that was built from every interaction, every piece of data shared, every opportunity identified — all living in the OS as connected entities. The proposal document is a rendering of this truth.
