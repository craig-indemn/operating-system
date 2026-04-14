---
ask: "Consolidated vision document for the customer system — problem, capabilities, phased trajectory"
created: 2026-04-14
workstream: customer-system
session: 2026-04-14-a
sources:
  - type: google-doc
    description: "Kyle's 28-file Customer Success Context Package"
  - type: google-sheets
    description: "Kyle's CRM InsurTechNY sheet"
  - type: meeting-transcript
    description: "Craig/Kyle (Apr 6, Apr 9), Craig/Cam (Apr 9), Craig/George (Apr 8), Craig/Peter (Apr 9), Craig/Ganesh (Apr 6)"
  - type: meeting-transcript
    description: "Kyle+Cam Customer Review (Apr 1), CDD status meetings, Weekly Platform Sync"
  - type: conversation
    description: "Craig's notes and synthesis"
---

# Customer System: Vision & Trajectory

**Craig Certo — April 14, 2026**

This document synthesizes input from Kyle, Cam, George, Peter, and Ganesh across 10+ meetings and 28+ working documents from March-April 2026. It captures the problems we're solving, what the system needs to do (comprehensively), and how we get there in phases.

The customer system is the first domain built on the Indemn Operating System. It becomes the source of truth for everything the company does — customers, prospects, delivery, meetings, team workload. Phase 1 is the foundation. Everything else builds on it.

---

## The Problem

If anyone needs to understand a customer, they ask Kyle. That doesn't scale — and Kyle can't plug in for the next three months.

The data exists, but it's scattered across six or more disconnected systems: Pipeline API (Vercel), Airtable, Google Sheets, Google Drive (43 customer subfolders), Meeting Intelligence DB (22K+ extractions from 3,130 meetings), and Slack. No single system is authoritative. Nobody maintains all of them. When Johnson Insurance went 10+ days without a response, nobody noticed until Kyle checked.

Beyond the source of truth problem, the company has no defined delivery process (18 customers, each approached differently), no visibility into who's working on what (Peter finds out customers went live after the fact), and no way to quantify the value being delivered (ROI models exist for one customer — Branch).

These aren't separate problems. They're facets of one problem: the company doesn't have a system that models its own operations.

**What everyone said:**

- **Kyle**: "We need better visibility and predictability in customer delivery, along with documenting the baseline process for onboarding new customers." Wants an immutable ledger, updated daily, interactable by AI and humans.
- **Cam**: Team efforts are a "net vector sum of zero." Alignment is a force multiplier we don't have. Revenue Agents as a strategic differentiator — vendors that contribute to the top line are indispensable.
- **George**: Usage data access is the #1 ask — "would reduce pre-meeting review from 20 minutes to 5, nearly doubling the number of customers I could manage."
- **Peter**: "Primary problem is mitigating miscommunications — people send emails and make calls to customers without informing the team."
- **Ganesh**: Account general + standin model to prevent gatekeeping. Churn detection via engagement monitoring. Built a prototype UI already.

---

## What the System Needs to Do

Organized by phase. Phase 1 capabilities are the foundation — the source of truth that makes everything else possible. Later phases build on that data.

### Phase 1: Source of Truth

The system answers one question: **"What's the story with [customer]?"** Anyone on the team can ask it and get a complete, current answer without asking Kyle.

**Customer & Prospect Record**
- Look up any company (prospect or customer) and see: who owns it, what stage it's in, what's been built, what's in progress, last contact, next step
- Track every company from first contact through active customer through churned — one entity, one lifecycle (prospects and customers are the same thing at different stages)
- Assign account owner and standin per company
- Track customer type (Broker, MGA, Carrier, InsurTech), ICP fit, cohort (Core, Graduating, AI Investments)
- Track how we met / lead source
- Distinguish Enterprise (needs new development) from Core (personalize existing)
- Store enrichment data: employee count, revenue, industry, HQ, specialties
- Link to Google Drive folder, AMS system, integration notes

**People**
- Track contacts per company: name, title, email, role, primary flag
- Track Indemn team assignments per company: account lead, standin, engineering lead, executive sponsor

**Pipeline & Deals**
- Track deals through stages with auto-calculated probability — no manual overrides
- Support multiple concurrent deals per company (initial engagement, expansion, upsell)
- Track expected ARR, scoring, warmth classification
- Detect stale deals based on stage-specific thresholds
- Map each deal to a primary outcome (Revenue, Efficiency, Retention, Control)
- Conference leads enter as companies with deals — same system, same lifecycle

**What's Deployed**
- Track which associates are live per customer, their status, and what channel they're on
- Link deployments to the associate catalog (what type, what outcome it serves)

**Data Ingestion (Phase 1)**
- Import existing customer data from Pipeline API and Google Sheets
- Import conference leads from Kyle's CRM sheet
- Import contacts and enrichment from existing sources
- Establish the baseline that everyone works from

### Phase 2: Delivery Tracking

Once we know who our customers are, we track what we're building for them.

**Implementation Lifecycle**
- Track implementations through stages: kickoff → configuration → testing → soft launch → live → optimization
- Track implementation health: on track, at risk, blocked
- Record every stage transition immutably (the OS changes collection handles this)
- Track launch benchmarks: target vs actual days to launch

**Tasks & Work**
- Track tasks per implementation: title, owner, due date, status, priority, category
- Filter by "my tasks" vs "all tasks"
- Link tasks to meetings they came from
- Know when things go live — automatic awareness via OS watches

**Playbooks**
- Maintain playbooks per associate type: checklist, required inputs, integrations, success metrics, timeline, escalation paths
- Generate tasks from playbook when starting an implementation
- Tier the delivery: Tier 1 (quick wins), Tier 2 (real value), Tier 3 (expansion)
- Playbooks evolve over time from delivery experience

### Phase 3: Visibility & Intelligence

With the foundation and delivery tracked, add the intelligence layer.

**Health Monitoring**
- Calculate weighted health scores with cohort multipliers
- Generate alerts: critical, needs attention, expansion opportunity
- Verify last contact dates against Slack (Slack is ground truth)
- Trigger-based management: automated nudges when thresholds are breached
- Detect churn risk through engagement monitoring

**Meeting Intelligence**
- Connect meetings to customer records
- Surface decisions, action items, commitments, signals from meeting transcripts
- Use signals for health scoring (positive vs negative per week)
- Track commitment fulfillment — promises made vs delivered

**Team Capacity**
- Track hours per person per customer per activity type
- See who is over-allocated and where bottlenecks form
- Model staffing ratios for growth from 18 to 100 customers

**Communication & Awareness**
- OS watches handle this: when entities change, the right people are notified
- Weekly summaries generated from system data
- Visibility into all customer interactions in one place

### Phase 4: Pipeline, Conference & Outreach

Extend the system to cover the full prospect lifecycle.

**Conference Management**
- Track conferences: planning, attendees, cost, outreach, follow-up, ROI
- Before events: filter attendee lists by ICP, prep research
- During/after: track leads through follow-up sequences with staleness detection
- Calculate conference ROI: cost vs revenue from leads acquired

**Outreach & Sequences**
- Auto-sequence follow-up reminders
- Route contacts by seniority (C-level to Kyle/Cam, others to sales)
- Connect to Apollo for enrichment

**Pipeline Extension**
- Complete prospect list as source of truth with defined update process
- Competitive intelligence per deal
- Sales conversation visibility feeding into delivery planning

### Phase 5: Value, ROI & Scaling

The mature system that quantifies everything.

**Value & ROI Tracking**
- Per-customer ROI model across Four Outcomes with dollar values
- Track current value delivered vs potential, with timeline
- Net margin per customer: ARR, cost, hours, margin
- Proof points from existing customers for expansion/investor conversations
- Customer expansion tracking: Land → Expand → Scale

**Customer Discovery**
- Disposition mapping: category, channel, volume, automation state per customer
- Map categories to associate types and outcomes
- Identify capability gaps

**Evaluations & Quality**
- Associate evaluation framework (Accuracy, Tone, Process, Domain, Common Errors judges)
- Go-live confidence metrics per deployment
- Quality tracking over time

**Reports & Case Studies**
- Generate case studies from delivery data and outcomes
- Analytical reports per customer
- Investor-ready proof points

**Demos**
- In-system demos for sales conversations

---

## How This Gets Built

The customer system is the first domain on the Indemn Operating System. The OS provides the kernel — entity framework, state machines, CLI/API auto-generation, watches, roles, the changes collection, integrations. We model the business data on top of it.

What the OS gives us for free:
- **Activity log**: every entity change is recorded automatically (who, what, when, from, to)
- **Notifications**: watches on roles deliver messages when entities change — Peter's "know when something goes live" is a watch configuration, not a feature
- **Audit trail**: tamper-evident, append-only, queryable
- **CLI and API**: auto-generated from entity definitions — the moment we define a Company entity, the CLI commands and API endpoints exist
- **Base UI**: auto-generated from entity definitions — the team gets a working interface without building one
- **Role-based access**: George's "managers see everything, operators see their customers" is a role configuration

What we model as domain data:
- Company, Contact, Deal, Implementation, Task, Playbook, Associate Deployment, Outcome, Meeting, Conference
- Their fields, lifecycles, and relationships
- Per-organization rules and configuration

**The sequence:**
1. Define the Phase 1 entities on the OS (Company, Contact, Deal, Associate Deployment + reference entities)
2. Ingest existing data to establish the baseline
3. The team starts using it as the source of truth
4. Add delivery tracking entities (Implementation, Task, Playbook)
5. Add intelligence integrations (Meeting Intelligence, Observatory, Slack)
6. Add pipeline and conference tracking
7. Add value/ROI layer as data accumulates

Each phase produces something usable. Nothing is built speculatively.

---

## What Kyle Gets First

Phase 1 delivers:
- A place to look up any customer or prospect and see the complete picture
- Conference leads (InsurTechNY) tracked in the same system as existing customers
- Account ownership visible for every company
- Deal pipeline with stages, probability, and staleness detection
- Associate deployments tracked per customer
- The changes collection recording every update (the immutable ledger Kyle wants)
- A CLI that anyone can use to query and update customer data
- A UI auto-generated from the entity definitions

This is the "source of truth updated daily, interactable by AI systems and humans" that Kyle described. It starts simple and grows.
