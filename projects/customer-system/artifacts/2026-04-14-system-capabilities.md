---
ask: "Comprehensive list of what the customer system needs to do — derived from all source documents and stakeholder conversations"
created: 2026-04-14
workstream: customer-system
session: 2026-04-14-a
sources:
  - type: google-doc
    description: "Kyle's 28-file Customer Success Context Package"
  - type: google-sheets
    description: "Kyle's CRM InsurTechNY sheet"
  - type: meeting-transcript
    description: "All meeting transcripts from April 1-13, 2026"
  - type: conversation
    description: "Craig's notes and brain dump"
---

# Customer System: What Should It Do?

Everything the system needs to enable, extracted from every source document and stakeholder conversation. This is not a solution design — it's the complete inventory of capabilities that should inform the domain model and phasing.

Organized by functional area. Each capability is attributed to its source.

---

## 1. Customer Record & Source of Truth

The system is the single place anyone goes to understand a customer.

| # | Capability | Source |
|---|-----------|--------|
| 1.1 | Look up any customer and see a complete picture: owner, stage, health, what's been built, what's in progress, last contact, next step | Kyle (Customer OS doc), all stakeholders |
| 1.2 | Track every customer from first contact (prospect/lead) through active customer through churned — one entity, one lifecycle | Kyle (Pipeline Source of Truth), Craig |
| 1.3 | Assign an account owner and a standin per customer | Ganesh (Apr 6), Kyle+Cam (Apr 1) |
| 1.4 | Track which associates have been deployed for each customer and their status | Kyle (Branch template), Craig's notes |
| 1.5 | Track which outcomes are being delivered per customer | Kyle (Branch template), Four Outcomes framework |
| 1.6 | Track the customer's tier/cohort (Core Platform, Graduating, AI Investments) | Kyle (Portfolio Overview) |
| 1.7 | Store the customer's AMS system, integrations, and technology stack | Kyle (Prisma schema — amsSystem, amsNotes) |
| 1.8 | Link to the customer's Google Drive folder | Kyle (Prisma schema — googleDriveFolderId) |
| 1.9 | Track days since last contact with staleness alerts | Kyle (CRM sheet, Pipeline spec), George (Apr 8) |
| 1.10 | Track customer-side contacts: name, title, email, role, primary flag | Kyle (CRM sheet — Contacts tab) |
| 1.11 | Store enrichment data: employee count, annual revenue, industry, HQ, founded year, technologies, specialties | Kyle (Prisma schema, CRM Company Profiles tab) |
| 1.12 | Classify customer type: Broker, MGA/MGU, Carrier, InsurTech, Other | Kyle (Prisma schema, CRM sheet) |
| 1.13 | Classify ICP fit: Strong, Medium, Low | Kyle (CRM Company Profiles tab) |
| 1.14 | Track how we met / lead source per customer | Kyle (CRM sheet — How Met column) |
| 1.15 | Track customer-side key contacts with their roles in the engagement | Kyle (Team Allocation doc) |
| 1.16 | Distinguish Enterprise customers (need new development) from Core (personalize existing) | Kyle+Cam (Apr 1 decisions) |
| 1.17 | Remove or park dead-weight accounts | Kyle+Cam (Apr 1 decisions) |

---

## 2. Pipeline & Deal Tracking

Track business opportunities from first contact through close.

| # | Capability | Source |
|---|-----------|--------|
| 2.1 | Track deals through stages: CONTACT → DISCOVERY → DEMO → PROPOSAL → NEGOTIATION → VERBAL → SIGNED | Kyle (CRM Stages tab) |
| 2.2 | Auto-calculate probability from stage (5% → 15% → 25% → 40% → 60% → 80% → 100%) — no manual overrides | Kyle (Pipeline Source of Truth), Kyle+Cam (Apr 1) |
| 2.3 | Score deals on multiple dimensions (company fit, relationship, eagerness, use case, milestone) — 1-5 scale each | Kyle (Prisma schema) |
| 2.4 | Calculate composite score and weighted pipeline value | Kyle (CRM Stages tab formula, Prisma schema) |
| 2.5 | Classify deal warmth: Cold, Cool, Warm, Hot, On Fire | Kyle (Prisma schema) |
| 2.6 | Map each deal to a primary outcome (Revenue, Efficiency, Retention, Control) | Kyle (Prisma schema) |
| 2.7 | Track key dates: first contact, proposal sent, closed, contract signed | Kyle (Prisma schema) |
| 2.8 | Detect stale deals based on stage-specific thresholds (14 days for CONTACT, 5 days for VERBAL) | Kyle (CRM Stages tab — Stale After) |
| 2.9 | Track expected ARR per deal | Kyle (CRM sheet, Prisma schema) |
| 2.10 | Track competitive intelligence per deal | Kyle (Pipeline Source of Truth) |
| 2.11 | Support multiple concurrent deals per company (initial, expansion, upsell) | Kyle (Pipeline Source of Truth — Opportunities tab) |
| 2.12 | Track revenue potential and estimated engineering hours per opportunity | Kyle (Pipeline Source of Truth — Opportunities tab) |
| 2.13 | When a deal is WON/pilot starts, flow naturally into customer delivery tracking | Kyle (Pipeline Source of Truth — "prospects enter customer tracking at pilot start") |

---

## 3. Implementation & Delivery Tracking

Track what we're building for each customer and how it's going.

| # | Capability | Source |
|---|-----------|--------|
| 3.1 | Track implementation lifecycle: KICKOFF → CONFIGURATION → TESTING → SOFT_LAUNCH → LIVE → OPTIMIZATION → ADVOCATE | Kyle (Prisma schema) |
| 3.2 | Track implementation health: On Track, At Risk, Blocked | Kyle (Prisma schema) |
| 3.3 | Track which channels are deployed: voice, chat, email | Kyle (Prisma schema) |
| 3.4 | Track implementation lead and team members | Kyle (Prisma schema), George (Apr 8) |
| 3.5 | Track milestones per implementation with due dates and completion status | Kyle (Prisma schema) |
| 3.6 | Track tasks per implementation: title, owner, due date, status, priority, category (technical/training/testing/compliance) | Kyle (Prisma schema) |
| 3.7 | Track task source: manual, from meeting, from playbook | Kyle (Prisma schema — sourceMeetingId) |
| 3.8 | Track launch benchmarks: target days to launch vs actual | Kyle (Prisma schema) |
| 3.9 | Record every stage transition immutably: from, to, when, who, days in previous stage | Kyle (Prisma schema — ImplementationStageHistory) |
| 3.10 | Know when something goes live — automatic awareness, not relying on someone to announce it | Peter (Apr 9) |
| 3.11 | Filter tasks by "my tasks" vs "all tasks" | Peter (Apr 9) |
| 3.12 | See all executed tasks, who is responsible, how far along delivery is | Peter (Apr 9), George (Apr 8) |
| 3.13 | Track voice-specific configuration: use cases, phone numbers, agent persona, call counts | Kyle (Prisma schema — VoiceImplementation) |
| 3.14 | Visual progress indicator showing how close we are to delivery milestones | George (Craig's notes) |
| 3.15 | Time-to-completion information for things being built | George (Craig's notes) |

---

## 4. Playbooks & Delivery Templates

Standardized processes for how we deliver.

| # | Capability | Source |
|---|-----------|--------|
| 4.1 | Maintain playbooks per associate type: standard checklist, required inputs, integration requirements, success metrics, typical timeline, escalation paths | Kyle (Branch template) |
| 4.2 | Auto-generate tasks from playbook when starting an implementation (with dayOffset timing) | Kyle (Prisma schema — PlaybookTask) |
| 4.3 | Tier the delivery: Tier 1 (quick wins), Tier 2 (real value), Tier 3 (expansion) | Kyle (Branch template) |
| 4.4 | Track checklist completion per associate deployment | Kyle (Branch template) |
| 4.5 | Define resolution rate targets per deployment | Kyle (Branch template — "20% to 50% over 3 months") |
| 4.6 | Playbooks are living documents — editable, refinable over time from experience | Craig (session discussion) |
| 4.7 | Standardize checklists per associate type while allowing customer-specific details to vary | Kyle (Branch template) |

---

## 5. Customer Discovery & Disposition Mapping

Understanding a customer's operation before configuring the solution.

| # | Capability | Source |
|---|-----------|--------|
| 5.1 | Build a disposition map per customer: category, channel, annual volume, current automation state | Kyle (Branch template Step 1) |
| 5.2 | Capture disposition data from discovery calls, transcripts, recordings, shared reporting | Kyle (Branch template), Craig's notes from Kyle |
| 5.3 | Map each category to an associate type and an outcome | Kyle (Branch template Step 2) |
| 5.4 | Identify capability gaps where no associate type exists for a customer need | Kyle (Branch template Step 2) |
| 5.5 | Store a research document per customer encapsulating discovery findings | Craig's notes from Kyle |
| 5.6 | Store system diagram of the customer's current operations | Craig's notes from Kyle |
| 5.7 | Store detailed integration specification per customer | Craig's notes from Kyle |
| 5.8 | Understand what integrations the customer has with external systems | Craig's notes from Kyle |

---

## 6. Value, ROI & Unit Economics

Quantify what we're delivering and what the expansion potential is.

| # | Capability | Source |
|---|-----------|--------|
| 6.1 | Create a per-customer ROI model across Four Outcomes with dollar values | Kyle (Branch template Step 4) |
| 6.2 | Track measurable metrics per outcome: premium from leads, agent hours freed, policies retained, consistency scores | Kyle (Branch template) |
| 6.3 | Track net margin per customer: ARR, monthly revenue, cost per month, hours per month, margin | Kyle (Pipeline Source of Truth — Unit Economics tab), Kyle+Cam (Apr 1) |
| 6.4 | Track current value delivered vs potential value and projected timeline | Craig's notes from Kyle |
| 6.5 | Store proof points from existing customers for use in expansion/sales conversations | Kyle (Branch template) |
| 6.6 | Track customer expansion pattern: Land ($2K/mo) → Expand ($5K/mo) → Scale ($8K+/mo) | Kyle (Four Outcomes Product Map) |
| 6.7 | Calculate customer ROI vs pricing — demonstrate room to increase pricing | George (Apr 8) |
| 6.8 | Use ROI framing for investor messaging | George (Apr 8) |
| 6.9 | Track expansion opportunities per active customer | Kyle (Pipeline Source of Truth — Customer Operations tab) |

---

## 7. Health Monitoring & Alerts

Spot problems before they become crises.

| # | Capability | Source |
|---|-----------|--------|
| 7.1 | Calculate weighted health score per customer | Kyle (Health Monitor doc) |
| 7.2 | Apply cohort multipliers: Core=2x on commitment fulfillment, Graduating=2x on implementation progress | Kyle (Health Monitor doc) |
| 7.3 | Generate alert categories: FIRE (critical), WARM (needs attention), OPP (expansion opportunity) | Kyle (Health Monitor doc) |
| 7.4 | Verify "last contact" dates against Slack messages (Slack is ground truth) | Kyle (Health Monitor doc) |
| 7.5 | Detect stale customers/deals based on configurable thresholds | Kyle (CRM Stages tab, Prisma schema — isStale, staleDays) |
| 7.6 | Detect churn risk through engagement monitoring and platform usage | Ganesh (Apr 6) |
| 7.7 | Trigger-based management: automated triggers that spur humans into right activity at right time | Kyle+Cam (Apr 1 takeaways) |
| 7.8 | Send reminders for overdue follow-ups and due dates via Slack | George (Craig's notes), Craig's notes from Kyle |

---

## 8. Team Capacity & Workload

See who's doing what and whether we can take on more.

| # | Capability | Source |
|---|-----------|--------|
| 8.1 | Track hours per person per customer per activity type (Build, Maintain, Relationship, Sales) | Kyle (Pipeline Source of Truth — Team Capacity tab) |
| 8.2 | Classify delivery model per engagement: Deep, Batch, Platform, Long-term | Kyle (Team Allocation doc) |
| 8.3 | Per-person status view: tasks assigned, meeting hours, emails per week, customers managed | George (Apr 8), Craig's notes |
| 8.4 | See who is over-allocated and where bottlenecks are forming | George (Apr 8) |
| 8.5 | Model staffing ratios for growth: customer-to-engineer, customer-to-account-manager | Kyle (Capacity Model doc) |
| 8.6 | Project headcount needs as customer count grows from 18 to 100 | Kyle (Capacity Model doc) |
| 8.7 | Track how long people have been customers and completed tasks vs action items | George (Craig's notes) |

---

## 9. Communication & Awareness

Make alignment a side effect of doing work, not a separate discipline.

| # | Capability | Source |
|---|-----------|--------|
| 9.1 | When an entity changes (deployment goes live, task completes, deal moves stages), the right people know automatically | Peter (Apr 9), Cam (Apr 9), OS kernel (watches) |
| 9.2 | See all conversations with a customer in one place — not relying on people to CC support | Peter (Apr 9) |
| 9.3 | Visibility into sales conversations so implementation can plan | Peter (Apr 9) |
| 9.4 | When an engineer deploys something, the team knows without anyone having to announce it | Peter (Apr 9) |
| 9.5 | System makes communication happen naturally from actions taken within it | George (Apr 8), Peter (Apr 9) |
| 9.6 | Weekly summaries of customer status, things in motion, things people need awareness of | George (Craig's notes), Ganesh (Apr 6) |
| 9.7 | Outbound product management: release notes, bespoke customer notes | Ganesh (Apr 6) |
| 9.8 | Leadership reports generated from system data, sent to implementation channels first for review before leadership | CDD meeting (Apr 6) |

---

## 10. Meeting Intelligence

Connect meeting data to customer records.

| # | Capability | Source |
|---|-----------|--------|
| 10.1 | See the meetings we've had with each customer, with transcripts and extracted intelligence | Kyle (Meeting Intelligence doc), George (Craig's notes) |
| 10.2 | Extract decisions, quotes, signals, objections, action items, commitments, learnings from meetings | Kyle (Meeting Intelligence doc) |
| 10.3 | Use signals for health scoring: positive vs negative per customer per week | Kyle (Meeting Intelligence doc) |
| 10.4 | Track commitment fulfillment — promises extracted from meetings, tracked for accountability | Kyle (Immutable Ledger doc), Meetings API |
| 10.5 | Full-text search across all meetings for any topic | Meetings API |
| 10.6 | Link tasks to the meeting they came from | Kyle (Prisma schema — sourceMeetingId) |
| 10.7 | Pull last 7 days of meeting data to align with weekly customer call cadence | Ganesh (Apr 6 — George's suggestion) |
| 10.8 | Pick out due dates, action items, and follow-ups from meeting transcripts | Craig's notes from George |

---

## 11. Conference, Pipeline & Outreach

Track leads from events and outreach through conversion.

| # | Capability | Source |
|---|-----------|--------|
| 11.1 | Track conferences as events: name, date, cost, attendees, outcomes | Kyle (CRM InsurTechNY sheet), George (Apr 8) |
| 11.2 | Before a conference: identify attendees, their titles/roles, ICP fit | George (Apr 8), Kyle (InsurTechNY attendees sheet) |
| 11.3 | Track leads from a conference with: category (Cat 1/2A/2B/2C), owner, stage, follow-up date | Kyle (CRM Companies tab) |
| 11.4 | Track contacts collected per conference with how-met channel | Kyle (CRM Contacts tab) |
| 11.5 | Log all activity related to conference follow-up with date, action, actor, source | Kyle (CRM Ledger tab) |
| 11.6 | Track outreach: blogs, videos, live demos sent to prospects | George (Craig's notes) |
| 11.7 | Route conference contacts: C-level to Kyle/Cam, others to sales team | George (Apr 8) |
| 11.8 | Auto-sequence outreach and follow-up reminders with staleness detection | George (Apr 8) |
| 11.9 | Calculate conference ROI: cost vs revenue generated from leads acquired | Kyle (Apr 14 Slack — "Cam has the cost... we'll connect ongoing revenue expectations") |
| 11.10 | Spin up sub-sheets/views for conferences that feed into the main pipeline | Kyle (Apr 14 Slack) |
| 11.11 | Extend data model to complete prospect list with defined source of truth and update process | Kyle (Apr 14 Slack) |
| 11.12 | Connect to Apollo for contact enrichment | George (Apr 8) |
| 11.13 | Sales outbound cold outreach system | George (Craig's notes) |

---

## 12. Associate Catalog & Deployment

Track what we offer and what's deployed where.

| # | Capability | Source |
|---|-----------|--------|
| 12.1 | Maintain catalog of 24 associates organized by Engine/Outcome | Kyle (Four Outcomes Product Map) |
| 12.2 | Track maturity per associate type: Proven, Ready, In Dev | Kyle (Four Outcomes Product Map) |
| 12.3 | Track deployment mode per associate: Voice, Chat, Copilot | Kyle (Four Outcomes Product Map) |
| 12.4 | Store proof points per proven associate with customer and metrics | Kyle (Four Outcomes Product Map) |
| 12.5 | Per associate type: standard delivery checklist, required inputs, integrations, success metrics, timeline, escalation paths | Kyle (Branch template) |
| 12.6 | Analyze current customers against our associate model — what's deployed, what could be | Ganesh (Craig's notes) |
| 12.7 | Identify cross-sell/upsell based on gap between deployed and available associates | Kyle (Branch template Step 2), Ganesh |

---

## 13. Evaluations & Quality

Measure the quality of what we're deploying.

| # | Capability | Source |
|---|-----------|--------|
| 13.1 | Five judge categories for associate evaluation: Accuracy, Tone, Process, Insurance Domain, Common Errors | Kyle (Evaluation Framework doc) |
| 13.2 | Deterministic checks first, LLM judges for ambiguous cases | Kyle (Evaluation Framework doc) |
| 13.3 | Sample interactions for evaluation (10-20% non-critical, 100% critical) | Kyle (Evaluation Framework doc) |
| 13.4 | Go-live confidence metric per associate deployment | Kyle (Evaluation Framework doc) |
| 13.5 | Track quality improvements over time per associate | Kyle (Evaluation Framework doc) |
| 13.6 | Maintain trailing list of known error categories | Kyle (Evaluation Framework doc) |
| 13.7 | Connect to Observatory for usage and performance data per deployed associate | George (Apr 8), Ganesh (Apr 6) |

---

## 14. Data Ingestion & Integration

Connect existing data sources into the system.

| # | Capability | Source |
|---|-----------|--------|
| 14.1 | Import from existing Pipeline API (Vercel) — implementations, customer profiles, deals, commitments | Kyle (API Endpoints doc) |
| 14.2 | Import from Meeting Intelligence DB — 22K+ extractions, 3,130 meetings | Kyle (Meeting Intelligence doc) |
| 14.3 | Import from Slack — last contact verification, conversation history | Kyle (Health Monitor doc), Ganesh (Apr 6) |
| 14.4 | Import from Linear — task tracking, engineering work | Ganesh (Apr 6), Craig's notes |
| 14.5 | Import from Google Drive — customer folders, documents | Kyle (Prisma schema) |
| 14.6 | Import from Apollo — contact enrichment, company data | George (Apr 8) |
| 14.7 | Import from Stripe — payment data, revenue tracking | George (Craig's notes) |
| 14.8 | Import from Observatory — usage metrics, performance data per associate | George (Apr 8), Ganesh (Apr 6) |
| 14.9 | Import from Airtable — existing customer tracking data | George (Apr 8) |
| 14.10 | Import from Gmail — email history with contacts | Kyle (API Endpoints doc — Gmail API) |
| 14.11 | System supports both human and AI as actors making changes (Kyle's CRM already uses "Claude" as an actor in the Ledger) | Kyle (CRM Ledger tab) |

---

## 15. Immutable Ledger & Audit

Record everything. Reconstruct anything.

| # | Capability | Source |
|---|-----------|--------|
| 15.1 | Log every field change: date, entity, field, old value, new value, changed by, source | Kyle (Immutable Ledger doc) |
| 15.2 | Support both human and automated changes in the same log | Kyle (Immutable Ledger doc) |
| 15.3 | Track automated changes with reviewed/reverted flags | Kyle (Immutable Ledger doc — AutoAction pattern) |
| 15.4 | Log entity-matching decisions with confidence scores and correction loops | Kyle (Immutable Ledger doc — DataAssociation pattern) |
| 15.5 | Take weekly snapshots of goal progress | Kyle (Immutable Ledger doc — GoalSnapshot pattern) |
| 15.6 | Reconstruct full timeline of any customer's journey | Kyle (Prisma schema — ImplementationStageHistory) |
| 15.7 | Make the ledger interactable by both AI systems and humans | Kyle (context package — START HERE doc) |

---

## 16. Reports, Demos & Case Studies

Generate outputs from the system data.

| # | Capability | Source |
|---|-----------|--------|
| 16.1 | Generate weekly status reports for leadership | Ganesh (Apr 6), George (Craig's notes) |
| 16.2 | Generate case studies from customer delivery data and outcomes | Ganesh (Apr 6), George (Apr 8) |
| 16.3 | Generate analytical and usage reports per customer | George (Craig's notes) |
| 16.4 | Have demos in the system that the team can use in sales conversations | George (Craig's notes), Ganesh |
| 16.5 | Generate customer ROI reports showing value delivered vs investment | Kyle (Branch template Step 4) |
| 16.6 | Customer-facing evaluation reports showing agent quality | Kyle (Evaluation Framework doc) |

---

## 17. Roles, Access & Security

Different people need different views.

| # | Capability | Source |
|---|-----------|--------|
| 17.1 | Tiers of access — managers see everything, operators see their customers | George (Apr 8), Craig's notes |
| 17.2 | Account lead + standin per customer with clear ownership | Ganesh (Apr 6) |
| 17.3 | Don't expose full customer list during demos — clean, collapsible interface | George (Apr 8) |
| 17.4 | Strict guidelines for using the system during customer calls | George (Apr 8) |
| 17.5 | Roles: Account General, Account Lead, Standin, Engineering Lead, Executive Sponsor | Ganesh (Apr 6), Kyle (Team Allocation doc) |
