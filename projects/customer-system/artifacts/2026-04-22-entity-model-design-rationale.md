---
ask: "Capture the thinking, tradeoffs, and vision behind the entity model — why each entity exists, how they connect, how it fits the OS"
created: 2026-04-22
workstream: customer-system
session: 2026-04-22-roadmap
sources:
  - type: conversation
    description: "Craig + Claude brainstorming session, April 21-22 2026 — full reasoning captured"
---

# Entity Model Design Rationale

This document captures WHY the entity model is designed the way it is — the thinking, the tradeoffs, the rejected alternatives, and how everything connects to the Indemn OS vision. Read this to understand the system. Read the brainstorm checkpoint for field-level specs.

---

## The Problem We're Solving

Indemn has 18 customers and a growing pipeline. If anyone needs to understand a customer — what we've built for them, what we're building next, what state things are in, who's on point — they have to ask Kyle. That doesn't scale, and Kyle can't plug in for three months.

The data exists but it's scattered: Pipeline API, Airtable, Google Sheets, Google Drive (43 customer subfolders), Meeting Intelligence DB, Slack. Nothing is connected, nothing is current, nothing is authoritative.

Seven people on the team articulated seven facets of this problem (see problem-statement.md). The system we're building addresses all seven by making the OS the single source of truth for everything Indemn does with and for its customers.

---

## The Core Insight: Entities Make the System

The most important principle from this brainstorm: **the entities ARE the system.** Not a database that the system reads from. Not a CRM that people update. The entities, their relationships, their state machines, and the OS primitives that connect them (watches, associates, integrations) — that IS the customer system.

When you look at a Company in the OS, you don't see a record with 50 fields. You see a hub surrounded by:
- Operations — what they do
- Opportunities — where the gaps are
- Contacts — who we talk to
- Interactions — every touchpoint, internal and external
- Documents — every file exchanged
- Emails — every message
- Meetings — every conversation
- Deals — business opportunities
- Proposals — what we plan to deliver
- Associates — what's deployed and running

That constellation IS the comprehensive customer profile. The Company entity itself stays lean. The depth comes from the relationships. This is how the team actually thinks about customers — not as a row in a spreadsheet, but as a web of relationships, interactions, and deliverables.

Craig's principle: "For any object in our system that can stand alone, has specific structural characteristics that are important or need to be filled out or extracted systematically, it can be its own entity." Entities are cheap in the OS — they auto-generate CLI, API, UI, and skills. The cost of a new entity is near zero. The cost of cramming data into the wrong entity is confusion.

---

## The Flow: Why This Order Matters

```
Raw Data (Email, Meeting)
    → Interaction (unified timeline)
        → Company Understanding (Operations, Opportunities)
            → Proposal + Phases (what we'll deliver)
                → Delivery (Associates, Tasks)
                    → back into Interactions
```

This isn't just a data pipeline. It models how Indemn actually works with customers:

1. **We communicate** — emails, meetings, calls, Slack, in-person. Every communication is raw data that enters the system.

2. **We build a timeline** — those raw communications become Interactions. The Interaction is the abstracted touchpoint: "On April 8, Kyle and Christopher discussed the renewal wedge. Duration: 45 minutes. Key outcome: pivot from original proposal to renewal-focused approach."

3. **We understand the business** — through interactions, we learn about the customer's Operations (what they do, volumes, staffing, current automation) and identify Opportunities (gaps where our products can help).

4. **We propose a plan** — the Proposal is the culmination. It's built FROM the entities: the Opportunities we identified, the AssociateTypes that solve them, the phased approach. The proposal document Cam sends is a RENDERING of these entities.

5. **We deliver** — when a Proposal is accepted, Phases activate. Associates get deployed. Tasks get created. Commitments are tracked.

6. **We keep communicating** — delivery generates more Interactions (internal work, customer check-ins, status updates). These feed back into the system. The loop continues.

The system is a loop, not a line. Every layer feeds every other layer. An internal Slack thread about Alliance blocking on BT Core integration is an Interaction → it might generate a Task → that Task is linked to a Phase → the Phase's progress is tracked → the next customer meeting references the progress.

---

## Why Each Entity Exists

### Email — Raw Data, Not Just an Input

Email could have been just an input to create Interactions. We made it its own entity because:

1. **Email serves purposes beyond Interactions.** Kyle said "pull the proposal we sent, the date we sent it." That's a query on Email, not Interaction. `indemn email list --company "Alliance" --subject "proposal"` is a real thing people want to do.

2. **Email has specific structural characteristics.** Message ID, thread ID, HTML body, CC/BCC, attachments. These are structural properties that matter — you need the full email to recreate communication history.

3. **Email attachments feed Documents.** When an email has attachments, processing creates Document entities. The Email is the provenance record.

4. **Source of truth for content.** The email body IS the communication. The Interaction summary is a distillation. Both exist in the system for different purposes.

**Tradeoff considered:** Collapsing Email into Interaction (just store email content as Interaction fields). Rejected because Email has Gmail-specific structure (thread_id, message_id, CC/BCC) that doesn't apply to other Interaction types, and Email is useful independently.

### Document — Raw Artifact, Not Business Meaning

Document is a file or artifact. It intentionally does NOT carry business classification. A Document doesn't know it's "a proposal" or "an agreement" — that meaning comes from other entities that link to it.

**Why this separation matters:**

Craig created a 30-page analysis document for Alliance. That document is a Document entity linked to Alliance. But the key findings from that analysis are Opportunity entities, Operation entities, and other structured data. The Document is the narrative context. The entities are the actionable data.

When a Proposal entity has `source_document` → Document, the Document is the rendered output (the PDF Cam sends). The Proposal entity has the structured data (version, status, who it's for). The Document has the file.

**Tradeoff considered:** Adding `type` enum to Document (proposal, agreement, analysis, etc.). Rejected because the type is redundant — it's derivable from which entity links to it, and it creates a maintenance burden (every new entity type means updating the enum).

**Tradeoff considered:** Having Document carry creator info as "direction" (to_customer, from_customer, internal). Rejected as over-engineered — `creator_employee` vs `creator_contact` tells you which side created it.

### Interaction — The Connective Tissue

Interaction is the most novel entity in this model. It doesn't exist in most CRM systems. Here's why it's essential:

**It's the unified timeline.** Every touchpoint with or about a customer is an Interaction. Email thread, meeting, phone call, Slack thread, in-person conversation, conference encounter. One timeline, regardless of channel.

**It covers internal work, not just customer-facing.** Craig's key requirement: "It should work for our internal communications when we're delivering something for a customer." If Jonathan and Craig spend 2 hours in a meeting about Alliance's implementation, that's an Interaction linked to Alliance. This gives you total effort tracking, blocker visibility, and accountability.

**It's the hub for intelligence extraction.** When an Interaction is processed, it may produce Tasks, Commitments, Decisions, and Signals. All four intelligence entities link back to Interaction. The Interaction is where intelligence comes FROM.

**Why sources point TO Interaction (not the reverse):** Email has `interaction` → Interaction. Meeting has `interaction` → Interaction. This was a deliberate design choice. The alternative (Interaction having `source_email`, `source_meeting`, `source_slack`, `source_phone`...) creates a growing list of source fields that must be updated every time we add a new raw data type. With sources pointing to Interaction, adding a Slack raw data entity later just means adding `interaction` to the Slack entity. Interaction itself never changes.

**Slack compatibility:** Interaction operates at thread level. A Slack thread about Alliance = one Interaction. Customer-specific channels (#alliance, #gic-delivery) are easy sources. Tagged messages in general channels work too. Individual ambient mentions are too noisy and don't qualify.

**The summary field:** Craig challenged whether a summary is sufficient. The answer: the summary is a one-liner for timeline view. It IS the source of truth for "what was this touchpoint about" as a distillation. The raw content lives on Email/Meeting. The extracted substance lives in Task/Commitment/Decision/Signal entities. The summary serves the timeline — nothing more.

### Operation — What They Do

Operation models a specific business process a customer runs. "Alliance handles renewals via outbound phone calls, 4,000/year, 3 staff, manual."

**Why it's separate from Company:** Company is who they are. Operation is what they do. A company has many operations. Each operation has its own volume, staffing, channel, and automation level. These are queryable: "which customers have manual renewal processes?" → immediate prospect identification.

**Why it's separate from Opportunity:** Operation is a neutral fact about the customer's business. Opportunity is OUR assessment of where there's a gap. One Operation can have zero Opportunities (they're doing fine) or multiple (several gaps in the same process).

**Why fields are strings, not enums:** Craig called the initial enum categories "super naive." Department names and channel types vary wildly across customers. Alliance organizes by functional area. GIC organizes by channel. A carrier organizes by line of business. Rigid enums would force customers into our categories. Strings let the data teach us what the natural categories are. We'll tighten into enums when patterns emerge from real data.

### Opportunity — The Bridge

Opportunity is the bridge between "what they do" (Operations) and "what we can deliver" (Proposal Phases). It's where customer understanding meets product capability.

**The state machine tells the full story:** `identified → validated → proposed → addressed → resolved`. An Opportunity is identified through discovery, validated with the customer (they agree it's a problem), included in a Proposal Phase, actively being addressed through delivery, and resolved when the associate is live and working.

**Source tracking:** Every Opportunity links to where it was discovered — an Interaction (conversation where the pain came up) or a Document (analysis that revealed it). This is provenance. When someone asks "how do we know Alliance needs renewal automation?" the system shows you: "Discovered in the April 8 meeting with Christopher (Interaction #X), documented in Craig's Alliance analysis (Document #Y)."

**No estimated_value field:** Craig correctly identified this as premature. Value estimation will be calculated from other data (Operation volumes, pricing models), not stored as a standalone number. Adding it now would create a field that's either empty or hand-waved.

### Proposal — The Culmination

The Proposal is the most important entity for the business. It's what all discovery work leads to. It's what turns a prospect into a customer.

**Why the Proposal entity IS the source of truth, not the document:** This is a fundamental design decision. In the old world, Cam writes a Google Doc proposal and that document IS the proposal. In the OS, the Proposal entity and its Phases contain the structured data — what we're delivering, at what cost, in what phases, with what associates. The Google Doc is a RENDERING. An extremely intelligent LLM reads the entities and generates the proposal narrative. This means:
- Proposals are queryable across customers
- Proposal versioning is structural (v1, v2) not "Alliance Proposal v2 FINAL (2).docx"
- Phase changes are trackable through the OS changes collection
- Everything in the proposal is connected to the entities that inform it

**Why Proposal has no commercial summary fields:** Total investment and payment structure were removed. Why? Because they're computed from the Phase entities. Phase 1: $0 pilot. Phase 2: $2,500/mo. Phase 3: $5-10K/mo 12-month commitment. The Proposal's commercial picture IS its Phases. Storing a summary would be duplicate data that gets stale.

**Tradeoff considered:** Having "loose" Phases on Deals for pre-proposal planning (like FoxQuilt where no proposal exists yet). Rejected — every Deal gets a Proposal in `drafting` status. The Proposal is where phases live, period. This ensures one consistent container for "what's the plan for this customer."

### Phase — The Substance

Phase is where the real detail lives. But — and this was the biggest design evolution in the brainstorm — **Phase has no text blob fields.**

Craig's principle: "If we don't have an entity for it, it probably shouldn't be here." Every field that was previously text maps to an existing entity:

| Originally a text field | Now an entity relationship |
|------------------------|---------------------------|
| `customer_commitment` | Commitment entities with `phase` → Phase |
| `indemn_deliverables` | Task entities with `phase` → Phase |
| `success_metrics` | Lives on Opportunity (the gap being closed) |
| `entry_criteria` | Derivable from Task completion + Commitment fulfillment |
| `go_no_go_signal` | Derivable from entity states |

This means Phase is just: identity (name, number) + commercial terms (investment, period, commitment, pilot flag) + status. All substance comes from the entities around it.

**Investment terms are structured, not text:** Instead of `payment_structure: "month-to-month"`, we have `investment` (decimal), `investment_period` (enum), `commitment_months` (int), `is_pilot` (bool). Every commercial term is queryable.

### Associate — The Real Thing

Associate (renamed from AssociateDeployment) is the actual running bot for a customer. AssociateType is the template. This naming clarifies the distinction: you talk about "the Alliance Renewal Associate" (a specific instance) vs "the Renewal Associate type" (the template).

**Connection to production data:** Associate links to the real MongoDB data — `org_id`, `bot_id`, and `url`. This means the OS knows exactly which running bot in production corresponds to which Associate entity. When you check Associate status, you're looking at something real.

### CustomerSystem and BusinessRelationship — Understanding the Ecosystem

These entities capture the customer's ecosystem:

**CustomerSystem** answers "what tools do they use?" and directly ties to OS Integrations. If Alliance uses Applied Epic and we have an Epic adapter, the CustomerSystem entity links to the Integration entity. When scoping a Proposal, the team sees: "they use Epic (we have an adapter), Dialpad (no adapter — phone AI blocked)." This is immediately actionable.

**BusinessRelationship** answers "who do they work with?" and connects companies. If Alliance works with Everett Cash Mutual (a carrier), and ECM later becomes a prospect, we already know the relationship. Warm intro paths become visible in the data.

---

## How This Fits the OS Vision

### Self-Evidence

Define an entity and it auto-generates its API, CLI, documentation (skill), permissions, and UI. This means:

- `indemn email list --company "Alliance"` works the moment Email is defined
- The UI shows Email list and detail views automatically
- The CLI docs explain Email fields and commands
- No custom development per entity

Every new entity in this model gets the full OS treatment for free. 22 entities = 22 sets of CRUD endpoints, CLI commands, UI views, and auto-generated skills.

### Watches and Wiring

The OS watch system makes entities reactive. When entity state changes, watches fire and things happen:

- Email transitions to `classified` → watch fires → associate extracts intelligence, creates Interaction
- Opportunity transitions to `proposed` → watch fires → team notified that a gap is being addressed
- Phase transitions to `in_progress` → watch fires → Tasks and Commitments activate, Associate deployment begins
- Commitment transitions to `missed` → watch fires → account owner alerted

The entity model we designed is specifically structured to ENABLE these automations. State machines exist where state changes are meaningful and should trigger actions. Entities without state machines (Document, Operation, Signal) are facts that don't drive workflows.

### Associates Processing Data

The OS associates (AI agents) are what make raw data into intelligence. The processing pipeline:

1. **Email ingestion associate:** Gmail adapter pulls emails → creates Email entities → classifies them (links to Company, Contact) → creates Document entities from attachments → creates Interaction records
2. **Meeting processing associate:** Meeting entity with transcript → extracts Tasks, Decisions, Commitments, Signals → creates Interaction → links intelligence to Company
3. **Proposal generation associate (future):** Reads Company profile, Operations, Opportunities, AssociateTypes → generates Proposal with Phases → renders proposal Document

The entity model defines the INPUTS and OUTPUTS for these associates. The associates are the processing layer. The entities are the data layer. The watches are the wiring layer.

### The "Rocky Problem" and Multiple Input Paths

Kyle identified a critical adoption challenge: Rocky (sales rep) won't use Apollo because it's too complex. Interactions don't hit the source of truth.

The entity model solves this by accepting data from multiple paths:
- Gmail adapter → Email entities → Interactions (automatic)
- Google Meet adapter → Meeting entities → Interactions (automatic)
- Slack → Interactions (channel-based, automatic)
- Manual CLI note → Interaction (one command)
- Voice note → Interaction (future, "speak to update an account")

All paths create the same Interaction entities. The source of truth stays consistent regardless of HOW data enters. This is Craig's design: "multiple input paths, all auto-hydrated to the same data layer."

---

## Key Tradeoffs and Decisions

### 1. "No phases without a proposal"

**Decision:** Phases always belong to a Proposal. No standalone phases on Deals.

**Why:** Phases are the delivery plan. The delivery plan is communicated through a Proposal. Even internal planning (before the customer sees anything) happens in a Proposal in `drafting` status. This ensures one consistent container.

**Alternative considered:** Phases on Deals for pre-proposal planning. Rejected because it creates two places phases can live, and it's unclear when they migrate from Deal to Proposal.

### 2. "The proposal entity IS the source of truth"

**Decision:** The Proposal entity and its related entities (Phases, Opportunities, Commitments, Tasks) are the source of truth. The document is a rendering.

**Why:** This inverts the traditional model where the document IS the proposal. In the OS, entities are queryable, versionable, watchable. Documents are not. By making entities the source of truth, proposals become part of the system — not a file sitting in Drive that someone has to remember to update.

**Implication:** Proposal document generation becomes an LLM task. The LLM reads the entities and writes the narrative. This means the narrative is always consistent with the structured data.

### 3. "Sources point to Interaction, not the reverse"

**Decision:** Email has `interaction` → Interaction. Meeting has `interaction` → Interaction. Interaction has no source fields.

**Why:** Scales without touching Interaction when new source types are added. Follows OS relationship pattern.

**Alternative considered:** Interaction with `source_email`, `source_meeting` fields. Rejected because it creates a growing list of source fields.

### 4. "No fluff fields"

**Decision:** Every field is structured data, an entity relationship, or specific source-of-truth content. No keyword summaries. No text describing things that are other entities.

**Why:** Fluff fields are never maintained, never queried, and degrade trust in the data. If a summary describes data that lives on another entity, it gets stale. If it's structured data pretending to be text, it can't be queried.

**Example:** Phase originally had `customer_commitment` (text), `indemn_deliverables` (text), `success_metrics` (text), `entry_criteria` (text), `go_no_go_signal` (text). All five were replaced by entity relationships: Commitment, Task, Opportunity, and derivable state.

### 5. "Interaction covers internal AND external"

**Decision:** Interaction scope includes both customer-facing (external) and team-internal (internal) touchpoints.

**Why:** Understanding total effort, cost, and accountability per customer requires tracking internal work. If Craig and Jonathan spend 2 hours in a meeting about Alliance, that's time invested in Alliance. Blockers surface. Over-allocation becomes visible.

**Alternative considered:** Only external interactions, with internal work tracked elsewhere. Rejected because it fragments the customer timeline and makes effort tracking impossible.

### 6. "Operation and Opportunity are separate"

**Decision:** Operation = neutral fact about what they do. Opportunity = our assessment of where there's a gap.

**Why:** Operations exist whether we see opportunities or not. A customer's renewal process is a fact about their business. Whether we think we can improve it is our assessment. Separating them means we can model a customer's entire operation before identifying where we fit. This supports the systematic discovery Craig described: understand first, then map.

---

## The Alliance Test

Every design decision should pass the Alliance test: does it work for Alliance Insurance, the first target customer?

**Alliance in the OS:**
- **Company:** Alliance Insurance, 10K policies, Broker, uses BT Core + Applied Epic
- **Contacts:** Christopher Cook (CEO, signs), Brian Leftwich (operating lead), + 5-6 others from Feb meeting
- **Deal:** ALLIANCE-2026, proposal stage
- **Emails:** All email threads between Indemn and Alliance contacts (from Kyle's Gmail)
- **Meetings:** Discovery calls (Jan-Feb), Christopher call Apr 8 (renewal wedge conversation)
- **Documents:** Alliance proposal (Feb 11), Craig's 30-page analysis, Alliance's shared policy data
- **Interactions:** Timeline of every touchpoint — first contact Jan 2026 → discovery → data shared → proposal sent → silence → reconnect at NC event → April 8 call → proposal update pending
- **Operations:** Renewal outreach (phone, 4K/year, manual), customer service, new business intake
- **Opportunities:** "80% of outbound calls unanswered" (linked to Renewal Associate), "static email templates" (linked to efficiency)
- **Proposal v1:** Feb 11, Crawl-Walk-Run, sent to Christopher, currently `superseded`
- **Proposal v2:** In `drafting`, renewal-focused pivot based on April 8 call
- **Phase 1 (v2):** Renewal Associate, ~$2,500/mo, month-to-month
- **Commitments:** "Ship updated proposal by Apr 25" (Indemn, linked to Phase)
- **Tasks:** "Update proposal with renewal wedge data", "Get BT Core API credentials"
- **Decisions:** "Pivot from original proposal to renewal-focused approach" (Apr 8)
- **Signals:** health_positive ("Christopher proactively reconnected at NC event"), expansion ("interested in multi-channel beyond phone")
- **CustomerSystem:** BT Core (data provider, linked to Integration), Applied Epic (AMS), Dialpad (phone — no adapter, blocks phone AI)
- **BusinessRelationship:** Works with Everett Cash Mutual (carrier), various others
- **Associates:** None deployed yet (but some built — ready to demo)

Every entity has real data. Every relationship is meaningful. The full picture of Alliance is visible from one Company hub, drillable in any direction.

This is what Kyle asked for: "a source of truth updated daily, interactable by AI systems and humans."

This is what Cam wants: "a system that completely controls the process — on an automated basis or by a tickle, it reaches out and says hey, you haven't talked to so-and-so in a week."

This is what George needs: "reduce pre-meeting review from 20 minutes to 5."

The entities make the system. The OS makes the entities cheap. The associates make the data flow. The watches make it reactive. One model, all seven problems addressed.

---

## The Automation Pipeline: Associates and Watches

The entity model alone is a database. What makes it a SYSTEM is the wiring — associates that process data and watches that trigger them. This is the OS in action.

### The Principle: Humans for Judgment, Associates for Processing

Not everything should be automated. The design distinguishes three tiers:

**Fully automated (associates + watches):** Email classification, Interaction synthesis, Document creation from attachments, intelligence extraction. These are mechanical — an email arrives, it gets classified, it becomes part of the timeline, intelligence gets extracted. No human judgment needed for the happy path.

**CLI-assisted (Craig + Claude Code):** Entity definitions, Operations, Opportunities, Proposals + Phases, watch configuration. These require business understanding — "Alliance's renewal operation handles 4,000 policies/year" is a fact that comes from human analysis, not automated extraction. Craig populates these via CLI.

**Human-in-the-loop (review):** Validate associate classifications, review extracted intelligence, approve Proposals before sending. The associates do the work; humans verify the quality.

### Four Associates, Four Watches

The minimum viable automation pipeline for Alliance:

**Email Classifier** — triggered when an Email entity is created. Reads sender, recipients, subject, and body. Matches to a Company by contact email domains and existing Contact records. Links the Email to Company and Contacts. Transitions to `classified`. This is a hybrid associate: deterministic matching by email domain first, LLM reasoning for ambiguous cases.

**Interaction Synthesizer** — triggered when an Email transitions to `classified` or a Meeting is created. Groups emails by thread_id into a single Interaction. Creates an Interaction record with participants, date, type, scope (external/internal), and summary. Creates Document entities from email attachments. For Meetings, creates an Interaction and links it. This is primarily deterministic (thread grouping, participant extraction) with LLM for summary generation.

**Intelligence Extractor** — triggered when an Interaction is created. Reads the raw content (email body from linked Emails, transcript from linked Meeting). Extracts Tasks (action items), Decisions (choices made), Commitments (promises), and Signals (health/risk indicators). Each becomes its own entity linked to the Interaction. This is primarily LLM-based — extraction requires understanding context and intent.

**Proposal Writer** (Wave 5, manual invocation) — reads Company profile, Operations, Opportunities, Phases, AssociateTypes. Generates a proposal document narrative in the style of Cam's existing proposals (outcome-anchored, phased, customer-specific pain + quantified impact). The output is a Document entity linked as the Proposal's source_document. This is fully LLM-based with the entity data as structured input.

### Watch Flow

```
Email created
    → [Email Classifier] → links Company + Contacts
        → Email transitions to 'classified'
            → [Interaction Synthesizer] → creates Interaction + Documents
                → Interaction created
                    → [Intelligence Extractor] → creates Tasks, Decisions, Signals, Commitments

Meeting created
    → [Interaction Synthesizer] → creates Interaction
        → Interaction created
            → [Intelligence Extractor] → creates Tasks, Decisions, Signals, Commitments
```

Each step is atomic. Each produces entities that trigger the next step. If any step fails, the previous entities still exist — the pipeline is resilient. The changes collection records every mutation. Traces show the full cascade.

### Why This Order Matters

The pipeline flows from raw data to intelligence:

1. **Raw data in** (Email/Meeting created) — adapter work
2. **Classification** (Email Classifier) — link to the right Company
3. **Timeline creation** (Interaction Synthesizer) — unified touchpoint
4. **Intelligence extraction** (Intelligence Extractor) — actionable items

Each layer depends on the previous. You can't extract intelligence without an Interaction. You can't create an Interaction without a classified Email. The watches enforce this ordering automatically.

### What This Means for Alliance

When we turn on the Gmail adapter for Kyle's account:
1. Alliance emails flow in → Email entities created automatically
2. Email Classifier matches them to Alliance (by Christopher Cook's email, Brian Leftwich's email, etc.)
3. Interaction Synthesizer groups them into thread-level Interactions → Alliance timeline materializes
4. Intelligence Extractor pulls out action items, decisions, commitments from each exchange
5. Craig reviews the output → adds Operations and Opportunities from his analysis
6. Craig creates Proposal v2 → Proposal Writer generates the document

The manual work is steps 5-6. Everything else is the OS doing its job.

---

## Associate Skills

### Email Classifier

**Purpose:** Classify newly ingested Email entities — determine Company, link participants, assess relevance.

**Design decisions:**

- **Trust the LLM.** The skill describes the job, not the commands. The entity skills (Email, Company, Contact, Employee) are auto-loaded and document every CLI command available. The associate is smart enough to use them correctly.
- **Contacts ARE auto-created.** Emails are a natural discovery point for new people at companies we work with. If we get an email from an unknown person at a known Company, create the Contact. This is how the system grows its knowledge base organically.
- **Companies are NEVER auto-created.** Adding a Company is a business decision (is this a prospect? a vendor? a partner?). That requires human judgment. If the classifier can't match to an existing Company, it transitions to `needs_review`.
- **Thread context is a first-class signal.** Previous emails in the same thread (queried by thread_id) often make classification obvious. If an earlier email was already classified to Alliance, the next reply in the thread is almost certainly Alliance too.
- **Three outcomes, not two.** The state machine has `classified` (confident), `needs_review` (uncertain), and `irrelevant` (not business-related). This prevents both bad data (wrong classification) and noise (newsletters creating junk Interactions).
- **Internal emails classified as Indemn.** If all participants are Employees and no customer is referenced, the Company is Indemn. This is valid — it's real work, just not customer-specific.

**Skill:**

```markdown
# Email Classifier

You classify newly ingested Email entities. Determine which Company
the email relates to, link participants to known Contacts and
Employees, and transition to the appropriate state.

You have access to all entity skills (Email, Company, Contact,
Employee). Use them to search, create, and update entities as needed.

## Trigger
Watch: Email entity created (state: received)

## Objective

For each new email, determine:
1. Which Company does this relate to?
2. Who are the participants? (match to Employees and Contacts)
3. Is this email relevant to our business?

## Classification

**classified** — you confidently identified the Company and
participants. External participants matched or created as Contacts.
Indemn participants matched to Employees.

**needs_review** — you can't confidently determine the Company.
Update with your best guess if you have one, but let a human verify.

**irrelevant** — newsletters, automated tool notifications, spam,
vendor solicitations, personal emails with no business relevance.

## How to Determine Company

Use every signal available:
- External participant emails and domains
- Known Contacts and their Company relationships
- Email subject and body content
- Previous emails in the same thread (query by thread_id — if
  earlier emails are already classified, that's a strong signal)

If all participants are Indemn Employees and no customer is
referenced, classify the company as Indemn.

## Contacts

If you encounter an external email address that doesn't match an
existing Contact but you've identified the Company, create the
Contact. Emails are a natural discovery point for new people at
companies we work with.

## Rules

- Never create Companies. If a Company doesn't exist, transition
  to needs_review.
- When in doubt about Company, needs_review. Don't guess.
- Pull the full thread context before deciding. Earlier emails in
  the thread often make the classification obvious.
```

### Intelligence Extractor

**Purpose:** Extract actionable intelligence from Interactions — Tasks, Decisions, Commitments, Signals. The processing layer that turns raw communication into structured, queryable knowledge.

**Design decisions:**

- **Conservative extraction.** Only extract what's clearly present. Don't infer Tasks that weren't stated. Don't manufacture Signals from neutral content. Bad intelligence is worse than no intelligence — it erodes trust in the system.
- **Duplicate detection.** Before creating, check if a similar Task or Commitment already exists. Overlapping email threads (same thread, new message) could produce duplicate extraction. The associate checks first.
- **Not every Interaction produces intelligence.** A simple scheduling email or one-line reply might produce nothing. That's fine — the associate transitions to `processed` regardless.
- **Four entity types, clear separation.** Tasks = action items (someone needs to do something). Decisions = choices made (direction changed). Commitments = promises (accountability). Signals = health/risk/expansion indicators (patterns to watch). Each serves a different downstream purpose.

**Skill:**

```markdown
# Intelligence Extractor

You extract actionable intelligence from Interactions. When an
Interaction is created, you read the raw content and create
structured entities: Tasks, Decisions, Commitments, and Signals.

You have access to all entity skills (Interaction, Email, Meeting,
Task, Decision, Commitment, Signal, Company, Contact, Employee).
Use them to read source content and create intelligence entities.

## Trigger
Watch: Interaction created

## Process

Read the Interaction and its linked raw data:
- For email Interactions: read the linked Email bodies (full thread)
- For meeting Interactions: read the linked Meeting transcript and
  notes

From the content, extract any of the following that are present.
Not every Interaction produces intelligence — a simple scheduling
email might produce nothing. That's fine.

### Tasks
Action items — something someone needs to do.
- "We need to update the proposal" → Task
- "Send the API credentials by Friday" → Task
- Set assignee if it's clear who owns it
- Set due_date if one is mentioned
- Set priority based on urgency signals in the content
- Link to the Interaction and the Company

### Decisions
Choices that affect direction — something was decided.
- "We're pivoting to the renewal wedge approach" → Decision
- "Phone AI is on hold until Dialpad stabilizes" → Decision
- Capture who decided and why if stated
- Link to the Interaction and the Company

### Commitments
Promises made by either side — accountability.
- "We'll have the proposal ready by April 25" → Commitment (Indemn)
- "Christopher will review when he's back from Austin" → Commitment
  (Customer)
- Set made_by, made_by_side, made_to
- Set due_date if mentioned
- Link to the Interaction and the Company

### Signals
Health, risk, or expansion indicators — patterns to notice.
- "Christopher proactively reconnected at the conference" →
  health_positive
- "They mentioned evaluating a competitor" → competitor
- "Interested in expanding to voice channel" → expansion
- Set type, severity, attributed_to
- Link to the Interaction and the Company

## Rules

- Only extract what's clearly present. Don't infer Tasks that
  weren't stated. Don't manufacture Signals from neutral content.
- Duplicate detection: before creating, check if a similar Task or
  Commitment already exists for this Company. Don't create
  duplicates from overlapping email threads.
- Transition the Interaction to processed when done.
- If the Interaction content is thin (simple scheduling, one-line
  reply), it's fine to extract nothing and still transition to
  processed.
```

### Interaction Synthesizer

**Purpose:** Create Interaction entities from classified Emails and new Meetings. Unify raw data into the customer timeline. Create Document entities from email attachments.

**Design decisions:**

- **One thread = one Interaction.** Multiple emails in a Gmail thread map to a single Interaction. The Interaction represents the exchange, not individual messages. When a new email arrives in an existing thread, the Interaction is updated (summary rewritten to cover full arc), not duplicated.
- **Scope derived from participants.** If ANY participant is a Contact (external person), the Interaction is `external`. If ALL participants are Employees, it's `internal`. Simple, deterministic, correct.
- **Attachments become Documents immediately.** Email attachments are a primary way files enter the system. The Synthesizer creates Document entities and links them to the Company. This is how Alliance's shared policy data and our sent proposals get into the Document layer automatically.
- **Summary covers the full exchange.** For a 5-email thread, the summary distills the whole conversation arc — not just the latest message. When someone scans the Alliance timeline, they see "Discussed renewal wedge approach; Christopher confirmed interest, asked for updated proposal by Apr 25" — not "RE: RE: RE: Following up."
- **Meetings create Interactions directly.** No thread grouping needed. One Meeting = one Interaction. The Meeting's existing summary (from Gemini or manual) is used if available.

**Skill:**

```markdown
# Interaction Synthesizer

You create Interaction entities from classified Emails and new
Meetings. You unify raw data into the customer timeline.

You have access to all entity skills (Interaction, Email, Meeting,
Document, Contact, Employee). Use them to search, create, and update
entities as needed.

## Triggers
- Watch: Email transitioned to classified
- Watch: Meeting created

## For Emails

### Check for existing Interaction
Query Interactions linked to other Emails with the same thread_id.
If an Interaction already exists for this thread, link this Email
to it and update the summary if the new email adds meaningful
context.

### Create new Interaction
If no Interaction exists for this thread, create one:
- company: from the Email's company
- deal: from the Email's deal (if set)
- type: email
- scope: external if any participant is a Contact, internal if all
  are Employees
- date: date of the earliest email in the thread
- duration: not applicable for email
- participants_contacts: Contacts from sender/recipients/cc/bcc
- participants_employees: Employees from sender/recipients/cc/bcc
- summary: distill what the email exchange is about — not a
  repetition of the body, but the meaningful substance of the
  exchange

Link the Email to this Interaction.

### Attachments
If the Email has attachments, create a Document entity for each:
- company: from the Email's company
- name: attachment filename
- source: email_attachment
- source_email: link to this Email
- creator: whoever sent the email (creator_employee or
  creator_contact depending on sender)
- mime_type, file_size: from attachment metadata
- content: if text-based, store the text content

## For Meetings

Create an Interaction:
- company: from the Meeting's company
- type: meeting
- scope: external if any participant is a Contact, internal if all
  are Employees
- date: Meeting date
- duration: Meeting duration
- participants_contacts and participants_employees: from Meeting
  participant data
- summary: use the Meeting's existing summary if available, or
  generate one from the transcript

Link the Meeting to this Interaction.

## Rules

- One email thread = one Interaction. Always check for existing
  Interactions before creating a new one.
- The summary is the source of truth for "what was this exchange
  about." Write it as if someone is scanning a timeline and needs
  to understand in one sentence what happened.
- When updating an existing Interaction's summary because a new
  email arrived in the thread, preserve the full arc of the
  conversation — don't just describe the latest message.
```

---

## Critical Learning: The Execute Tool Pattern

**Discovery (2026-04-23):** Associate skills MUST include explicit instructions for using the `execute` tool with `indemn` CLI commands. Without this, the agent doesn't know HOW to interact with the OS.

**The problem:** The original v1 skills said "use entity skills to search, create, and update entities" but never mentioned the `execute` tool or showed CLI command patterns. The deepagents framework provides `execute` (shell command execution via LocalShellBackend) as a tool, but the agent has no innate knowledge of the `indemn` CLI. It tried to use `task` subagents and `read_file` instead — which can't access the OS API.

**The fix:** Each skill now has a "How to Execute" section:
```
Use the `execute` tool to run `indemn` CLI commands. Examples:
execute("indemn email get <id>")
execute("indemn company list")
```

**The principle:** Skills must be self-contained. The `execute` tool is the bridge between the agent and the OS. Every associate skill that needs to interact with entities must teach the agent this pattern.

---

## Implementation Status (2026-04-23)

| Wave | Status | What |
|------|--------|------|
| 1: Entity Definitions | COMPLETE | 26 entities live. 9 new, 1 renamed, 5 updated, 3 removed. |
| 2: Wiring | COMPLETE | 3 skills (v2), 3 roles with watches, 3 associate actors on async runtime. |
| 3: Gmail Adapter | COMPLETE | `fetch_emails()` on Google Workspace adapter. Deployed. Pipeline E2E proven. |
| 4: Human Enrichment | NOT STARTED | Craig populates Operations, Opportunities, CustomerSystem via CLI. |
| 5: Proposal Generation | NOT STARTED | Create Proposal + Phases for Alliance. Associate generates document. |

### Infrastructure Fixes During Implementation
- Queue processor `WorkflowAlreadyStartedError` (temporalio SDK removed the class, replaced with RPCError)
- Runtime service token regenerated (stored on Platform Admin actor + AWS + Railway)
- "Interaction" renamed to "Touchpoint" (naming conflict with kernel entity)
- Entity `status` fields with `is_state_field: true` were missing on 6 new entities
