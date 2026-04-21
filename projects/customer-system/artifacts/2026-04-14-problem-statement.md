---
ask: "Distill all stakeholder input into a comprehensive problem statement for the customer system"
created: 2026-04-14
workstream: customer-system
session: 2026-04-14-a
sources:
  - type: google-doc
    description: "Kyle's Customer Success Context Package (28 files) shared April 10"
  - type: google-doc
    ref: "1dAtib-y9d5I-O9WzW8PON2ofxVKEkzhI7cXwZyk9Kxk"
    name: "Customer Operating System — Where We Are and Where We Need to Go"
  - type: google-sheets
    ref: "1B3QnzfS8IEM7cMN3ar9gSFRw8K8_viFmH-dEajQ9tQg"
    name: "Indemn CRM — InsurtechNY Lead List V1"
  - type: google-doc
    ref: "1yYLRgfk1TbSNraNW9aoJ0yp6j7lCdcf8h2l8xwRSFdA"
    name: "Customer Delivery System — Branch as Template"
  - type: meeting-transcript
    description: "Craig/Kyle Customer Source of Truth (Apr 6), Customer Success group (Apr 6 — Craig+Ganesh), Customer Success System (Apr 9 — Craig+Cam), Craig/Kyle Sync (Apr 9), George/Craig sync (Apr 8), Peter/Craig (Apr 9)"
  - type: meeting-transcript
    description: "Kyle+Cam Customer Review Takeaways (Apr 1), Customer Status CDD (Apr 6, Apr 13), Weekly Platform Sync (Apr 1)"
  - type: conversation
    description: "Craig's notes from conversations with Kyle, George, Ganesh"
  - type: local
    description: "CTO Operating Framework (cto-thinking worktree) — platform problems and criteria"
---

# Customer System: Problem Statement

**Craig Certo — April 14, 2026**

This document captures the problems Indemn faces in managing customers, delivering work, and operating as a company. It synthesizes input from Kyle, Cam, George, Peter, Ganesh, and Craig's own observations across 10+ meetings and multiple working documents from March-April 2026.

The purpose is alignment. Before building anything, we need agreement that these are the right problems, organized the right way. This follows the CTO Operating Framework: problems first, concepts second, solutions later.

---

## The Core Problem

If anyone at Indemn needs to understand a customer — what we've built for them, what we're building next, what state things are in, who's on point, what conversations have happened — they have to ask Kyle. Kyle is the single point of failure for customer knowledge. He has said he cannot plug in for the next three months due to investor and fundraising demands. Without him, the team has no reliable way to answer basic questions about any customer.

This is not a tooling problem. Tools exist — Pipeline API, Airtable, Google Sheets, Google Drive (43 customer subfolders), Meeting Intelligence DB, Slack. The problem is that nothing is connected, nothing is current, and nothing is authoritative. The data is scattered across six or more systems, each with a partial view, each maintained by a different person (or not maintained at all).

What follows are seven specific problem areas, each with evidence from the team, success criteria, and the risk of not addressing it.

---

## Concept 1: No Single Source of Truth for Customers

### The Problem

There is no single place anyone can look up a customer and get a complete, current picture. Customer data exists in fragments across disconnected systems, and no one system is authoritative.

### Evidence

- 67% of WON customers showed "Never" for last contact date. 6 of 18 had no assigned owner. (Kyle, "Customer OS — Where We Are")
- Johnson Insurance went 10+ days without a response to an email. Physicians Mutual ($500K pipeline) was untouched since April 2025. (Kyle, same document)
- Data lives in at least 6 places: Pipeline API (Vercel), Airtable, Google Sheets (ARR, Prioritization, Product Matrix), Google Drive (43 folders), Meeting Intelligence DB (22K+ extractions), Slack. None are connected. (Kyle's context package)
- "Disorganized use of Kanban boards and AirTable." (George, Apr 8)
- "Information scattered across Slack, Linear, Google Docs — need centralization." (Ganesh, Apr 6)
- Kyle wants an immutable ledger updated daily — "even a spreadsheet would be a perfect starting point." (Kyle, Apr 9)

### Success Criteria

Any team member can look up any customer and within 60 seconds understand: who owns the account, what stage they're in, what's been built, what's in progress, when we last contacted them, and what the next step is. No asking Kyle. No digging through Slack.

### Risk If Not Addressed

Kyle's three-month absence from day-to-day operations creates an immediate knowledge vacuum. Customer relationships degrade silently. Expansion opportunities go unnoticed. The team cannot scale beyond what fits in one person's memory.

---

## Concept 2: No Defined Delivery Process

### The Problem

There is no repeatable, documented process for how Indemn delivers to a customer — from signing through go-live through expansion. Each customer engagement is invented from scratch.

### Evidence

- "The current process is undefined and needs formalizing to efficiently grow to 30 or 50 customers." (Kyle, Apr 6)
- Kyle's Branch template defines a 4-step framework (Intake → Map → Playbook → Value), but it exists only for Branch. No other customer has been baselined this way. (Branch as Template doc)
- "Intake documentation is the biggest currently missing element — should include links to calls, transcripts, recordings, data summaries, proposal with summarized line items, due dates." (George, Apr 8)
- "No formal structure and written documents for procedures — team relies only on memory." (Peter, Apr 9)
- Ganesh was tasked with an implementation playbook because "documentation becomes stale and hard to find." He built a UI prototype to address this. (Ganesh, Apr 6)
- Kyle+Cam decided to "go through current customers pragmatically, build 'what should we do next' per customer, then systematize." (Apr 1 takeaways)

### Success Criteria

For every customer, we can answer four questions: (1) What does their operation look like? (2) Which associates and outcomes apply? (3) What's the delivery plan, in what order? (4) What's the ROI framing for expansion? Each question has a defined process, a standard deliverable, and a known level of effort.

### Risk If Not Addressed

The scale target is 18 to 100 customers in 9 months (~10 new per month). Without a defined process, each new customer requires the same discovery effort as the first. The capacity model breaks. Quality is inconsistent. New hires have no playbook to follow.

---

## Concept 3: Communication and Alignment Failures

### The Problem

Work falls through cracks because people don't know what others are doing. Sales, customer success, and engineering are disconnected. Communication about customers happens informally and inconsistently, leading to duplicated effort, missed follow-ups, and conflicting information reaching customers.

### Evidence

- Team efforts are a "net vector sum of zero" — alignment would be a "force multiplier." (Cam, Apr 9)
- The outcome matrix wasn't being distributed even though Cam assumed it was. (Cam, Apr 9)
- "Primary problem is mitigating miscommunications — people send emails and make calls to customers without informing the team or CCing support." (Peter, Apr 9)
- No conversation log showing everything discussed with a customer. Relying on people to CC support has been inconsistent. (Peter, Apr 9)
- Lack of visibility into sales conversations means implementation can't plan. (Peter, Apr 9)
- "We cannot have a corporate attitude that we don't talk to our customers" — but dev side requested exactly that (communicate via email only). (Cam, Apr 9)
- "Not everyone is currently aligned on the company's direction." (Cam, Apr 9, as a direct warning to Craig)

### Success Criteria

Communication about customers happens as a side effect of doing work in the system — not as a separate discipline that depends on individual diligence. When an engineer deploys something, the team knows. When sales has a conversation, it's captured. When a customer goes live, everyone is aware. The system makes alignment automatic.

### Risk If Not Addressed

Cam stated this clearly: without structural alignment, adding people makes the problem worse, not better. The Director of CS hire (highest priority per Kyle+Cam) will fail if there's no system for them to operate within. Customer trust erodes when they get conflicting information from different team members.

---

## Concept 4: No Visibility into Delivery Status or Customer Health

### The Problem

Leaders and operators cannot see the status of customer delivery or the health of customer relationships without manually asking people. There is no dashboard, no automated tracking, no way to spot problems before they become crises.

### Evidence

- Usage data access is George's #1 ask — "would reduce pre-meeting review from 20 minutes to 5, allowing scaling of customer onboarding. Could nearly double number of customers I could personally manage." (George, Apr 8)
- George wants a managerial view: per-person status, task duration, meeting hours per week, revenue per customer. (George, Apr 8)
- Customer Health Monitor exists in concept but daysSinceContact shows 0/None — needs first live run validation. (Kyle's context package)
- "I want to see all executed tasks, who is responsible, how far along delivery is." (Peter, Apr 9)
- Kyle+Cam want trigger-based management — automated triggers that spur humans into the right activity at the right time. (Apr 1 takeaways)
- Ganesh wants an analytical pipeline to detect churn sooner via engagement monitoring. (Ganesh, Apr 6)
- "Customers have gone live without notifying the team." (Peter, Apr 9)

### Success Criteria

At any moment, a manager can see: which customers are healthy, which are at risk, what's behind schedule, who is over-allocated, and where the bottlenecks are. This data refreshes automatically from the systems where work actually happens. Problems surface before they become customer-facing incidents.

### Risk If Not Addressed

George's framing is the sharpest: the bottleneck isn't team size, it's information retrieval cost. Every minute spent hunting for status is a minute not spent on customers. At 50+ customers, manual status gathering is physically impossible. Churn signals go undetected until it's too late.

---

## Concept 5: No Value/ROI Framework in Practice

### The Problem

Indemn can describe its outcomes conceptually (Revenue Growth, Operational Efficiency, Client Retention, Strategic Control) but cannot quantify the value it's delivering to any specific customer. ROI models exist in theory but are not populated or tracked.

### Evidence

- Kyle's Branch template has specific ROI numbers (Revenue Growth $69-115K/yr, Operational Efficiency $25-34K/yr, Client Retention $66-161K/yr) but this exists for one customer only. (Branch as Template doc)
- "Map current customer deliveries to the associates they are subscribed to, which helps identify what to scale quickly." (Kyle, Apr 6)
- ROI framing useful for investor messaging — "demonstrates room to increase pricing." (George, Apr 8)
- Kyle+Cam decided to track net margin per customer — "start now, estimate where you can't measure, build data over time." (Apr 1 takeaways)
- Kyle's CRM sheet: Expected ARR and Composite Score columns exist structurally but are completely empty across all 40 leads. (CRM sheet analysis)
- Kyle wants the system to include a "value" component that quantifies each customer's ROI for implementing different tiers of the plan. (Craig's notes from Kyle conversation)

### Success Criteria

For every customer, we can state: what they're paying, what value we're delivering (quantified), what the expansion potential is (quantified), and what the gap is between current and potential value. This data is maintained alongside delivery tracking, not in a separate exercise. ROI framing is available for every sales and expansion conversation.

### Risk If Not Addressed

Without quantified value, expansion is driven by relationship, not data. Pricing decisions have no foundation — Kyle+Cam noted Distinguished Programs was listed at $250K when the actual ARR is $12K. The Series A story requires proof points that the platform delivers measurable ROI. Investors will ask.

---

## Concept 6: Roles and Ownership Are Undefined

### The Problem

Who owns what for each customer is ad hoc. There is no consistent model for account leadership, no clear escalation paths, and no capacity planning tied to actual workload.

### Evidence

- 6 of 18 customers had no assigned owner. (Kyle, "Customer OS — Where We Are")
- Over-allocation: sometimes 3+ Indemn people on weekly customer calls. (Ganesh, Apr 6)
- Ganesh proposed account general + standin model to prevent one person from gatekeeping the success strategy. (Ganesh, Apr 6)
- Kyle+Cam decided on a specialist team model (Jonathan=voice, George=implementation) with an account manager layer — Director of CS as connective tissue. (Apr 1 takeaways)
- Kyle's team allocation doc defines 4 delivery models (Deep, Batch, Platform, Long-term) with per-customer assignments, but these aren't tracked in any system. (Team Allocation doc)
- George wants two-tier access: managers see person-by-person status including meeting hours, tasks, and revenue. (George, Apr 8)
- "Kyle requested more frequent huddles. Will be constrained next 3 months — needs Craig to step up leading team resource direction." (Kyle, Apr 9)

### Success Criteria

Every customer has a named account lead and a named standin. Every team member can see their own workload and their colleagues' workloads. Capacity is tracked — hours per person per customer per week. The system makes it obvious when someone is over-allocated or when a customer has no active attention.

### Risk If Not Addressed

The Director of CS hire — identified as the single highest priority hire — has no system to operate within. Without defined ownership, accountability is impossible. Over-allocation continues to burn out the most engaged people (George managing too many accounts, Kyle doing demos for low-revenue customers).

---

## Concept 7: No System for Pipeline, Outreach, and Conference Follow-Through

### The Problem

When Indemn attends a conference or runs outreach, there is no system to track leads through follow-up, qualification, and conversion. Conference preparation, attendee research, outreach sequences, and post-event follow-through are all manual and disconnected from the customer delivery system.

### Evidence

- Kyle created the InsurTechNY CRM sheet the day of sharing it — a 5-table spreadsheet built from scratch for one conference. (CRM sheet, shared Apr 14)
- The CRM sheet's scoring model (Composite Score, Weighted Value) is structurally defined but entirely unpopulated. (CRM sheet analysis)
- George identified conference prep as a major capability gap: identify attendees, filter by ICP, route C-level to Kyle/Cam, auto-sequence others, track follow-up. (George, Apr 8)
- George wants to "hook up to Apollo" for contact enrichment but noted Apollo's data architecture is poor. (George, Apr 8)
- George wants outbound cold outreach integrated — "even if slightly less efficient, scale of labor hours makes it effective." (George, Apr 8)
- Kyle Apr 14 Slack: "We'd spin up sub-sheets for conferences and other things, and step 2 or 3 is to extend data model to our complete prospect list with a defined source of truth."
- The InsurTechNY attendee list (1,047 people) exists as a separate sheet with no connection to the CRM. (Google Drive)
- Kyle's Pipeline Source of Truth spec calls for one spreadsheet covering both pipeline AND customers — prospects enter customer tracking at pilot start. (Pipeline Source of Truth doc)

### Success Criteria

Before a conference, the team can see who's attending, what their ICP fit is, and what outreach has already happened. During and after, leads are tracked through a defined funnel with automatic follow-up reminders and staleness detection. Leads that convert flow naturally into the customer delivery system — no re-entry, no separate tools. The pipeline and customer systems are one continuum, not two separate worlds.

### Risk If Not Addressed

Conference ROI is unmeasurable. InsurTechNY cost real money (Cam has the numbers) and Ian collected 48 contacts and booked 12 meetings — but without a system, follow-through depends entirely on individual discipline. Leads go cold. The investment is wasted. Kyle's stated goal of connecting conference ROI to ongoing revenue expectations is impossible without connected tracking.

---

## What This Leads To

These seven problems point to one system — a unified source of truth for customers, delivery, pipeline, and operations that the entire team works from. Not a dashboard on top of existing tools. Not another spreadsheet. The system itself, modeled as entities with lifecycles, roles with ownership, and data that flows between them automatically.

This is the first domain built on the Indemn Operating System. The domain modeling process (Understand → Entities → Roles → Rules → Skills → Integrations → Test → Deploy) applies directly. The result is: the OS generates the UI, the CLI, and the API from entity definitions. Everyone on the team logs in and uses it as the source of truth. AI associates automate processes on top of that foundation.

But the system doesn't start with automation. It starts with modeling the data and ingesting what exists to establish a baseline. Phase 1 is the source of truth. Everything else builds on that.

### Phasing (High Level)

**Phase 1: Source of Truth** — Model the core entities (Customer, Associate, Outcome, Playbook, etc.), ingest existing data from current systems, establish the baseline that everyone works from. Kyle can look at customers, see status, see ownership. This is the immutable ledger.

**Phase 2: Delivery Process** — Define and track the delivery lifecycle per customer. Playbooks, checklists, milestones. The Branch 4-step framework generalized and tracked in the system. George can prep for meetings in 5 minutes. Peter knows when something goes live.

**Phase 3: Communication and Visibility** — Automated awareness from system actions. Slack notifications, status dashboards, health monitoring, trigger-based alerts. Cam's "alignment as a side effect." George's usage data integration.

**Phase 4: Pipeline and Outreach** — Conference tracking, lead qualification, outreach sequences, conversion into customer records. Kyle's CRM sheet becomes a view on the system, not a separate spreadsheet.

**Phase 5: Value and Intelligence** — ROI tracking per customer, expansion identification, capacity planning, churn detection. The analytical layer that compounds over time.

---

## Next Steps

1. **Alignment** — Share this document with Kyle and Cam. Confirm the problems are right. Confirm the phasing priority.
2. **Domain Model** — Model the entities, lifecycles, and relationships for Phase 1 (source of truth). This is the OS domain modeling process applied.
3. **Data Ingestion Plan** — Map existing data to the domain model. Define what gets imported first.
4. **Build** — Implement on the OS. The UI and CLI are auto-generated from entity definitions.
