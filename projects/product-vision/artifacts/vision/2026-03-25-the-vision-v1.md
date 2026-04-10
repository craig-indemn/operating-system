---
ask: "What is Craig's full vision for the Indemn platform — the insurance lab, the architecture, the roadmap, the team, the story?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-24-a
sources:
  - type: conversation
    description: "Extended brainstorming session between Craig and Claude, 2026-03-24/25"
  - type: synthesis
    description: "Drawing on 62+ documents read from Slack, Google Drive, OS projects, codebases, and meeting notes"
---

# The Vision: Indemn as Insurance Lab

## The One-Liner

Indemn becomes the lab where insurance gets reinvented. Bring us your business, and AI will run it.

## What This Actually Means

We're not building a better CRM. We're not building a nicer chatbot. We're not even building a platform in the typical SaaS sense. We're building the system that lets AI run insurance companies.

EventGuard proved this is possible. A 110-year-old carrier gave us a product. We built everything — quoting, binding, payments, compliance, distribution across 351 venues. AI sells the insurance. 2,934 policies. $766K in premium. They acquired it for $2.78M because it worked.

The problem: we did it once, and it took building everything from scratch.

The vision: build the underlying system so we can do EventGuard for ANYONE. Not in months of custom engineering — in weeks of configuration.

## The Insurance Lab Model

Imagine a cohort. Five insurance companies join the Indemn lab.

- A carrier wants to launch a new specialty product — engagement ring insurance, pet insurance, gig worker coverage. We model their product on the platform. Configure associates to sell it. Deploy it on partner websites. End-to-end: customer asks questions → gets a quote → binds → pays → receives policy. All AI. All autonomous.

- An MGA wants to automate their entire submission pipeline. Their inbox gets 100+ emails a day. We model their business on the platform — their carriers, their agents, their appetite rules, their LOBs. Configure the Intake Associate. Emails arrive, get classified, extracted, validated, routed to the right carrier. Quotes come back, get compared, get sent to the retail agent. What took 30 minutes per submission now takes 3.

- A retail agency wants to digitize their front office. Their phones ring constantly — billing questions, COI requests, policy changes. We configure the Front Desk Associate, the Renewal Associate, the Cross-Sell Associate. Calls get answered, questions get resolved, renewals get monitored, coverage gaps get identified. The producers focus on selling instead of processing.

- A program administrator wants to stand up a new distribution channel. Instead of building a portal from scratch, they configure a product on the Indemn platform, define the underwriting rules, and deploy associates on partner websites. Agents or consumers interact through voice, chat, email, or web. Binding happens in real-time.

- A wholesale broker wants to transform their email-driven operation. Their two internal teams — CS/servicing and placement/underwriting — both work from the same inbox chaos. We model their two-stream workflow, configure associates for triage, extraction, drafting, and quoting. The inbox becomes an organized submission pipeline with cross-team visibility.

Each company gets onboarded. Their business is modeled. Associates are configured. Channels are connected. Within weeks, they have a fully operational digital insurance business running on Indemn.

That's the vision. We're literally revolutionizing how insurance operates.

## Why This Works (The Architecture)

### The Foundation: An Object-Oriented Insurance System

At its core, all we are doing is modeling the businesses in our space as entities and models, and integrating AI into the entire system.

Every entity that exists in an insurance business — submissions, policies, quotes, carriers, agents, coverages, claims, premiums, commissions — is modeled as a first-class object with:
- A schema (what fields it has)
- A state machine (how it transitions through its lifecycle)
- An API (full CRUD operations)
- A CLI (agent-accessible, human-accessible)

The domain model is organized into sub-domains:
- **Core Insurance** — Products, coverages, LOBs, class codes, rating, appetite, underwriting guidelines
- **Risk & Parties** — Insureds, agents, agencies, carriers, distribution partners
- **Submission & Quoting** — Applications, submissions, quotes, underwriting decisions
- **Policy Lifecycle** — Binders, policies, endorsements, renewals, cancellations, certificates
- **Claims** — Claims, claimants, reserves, loss history
- **Financial** — Premiums, payments, invoices, commissions, trust accounting
- **Authority & Compliance** — Delegated authority, licensing, surplus lines, regulatory filings
- **Distribution & Delivery** — Programs, product configurations, deployments, partner management

The system should be so foundational, so primitive, so atomic that there is no situation in any customer's insurance business that can't be handled within our system. If it exists in insurance, there is a way to model it and operate on it through the platform.

### Associates as Processing Nodes

The associates from Cam's pricing matrix (48 across Agencies, Carriers, Distribution) are not 48 different products. They are 48 configurations of the same underlying agent system.

Each associate is an AI agent equipped with skills — similar to Claude Code skills — that define how to interact with the domain model via CLI/API. One associate has a role. One associate has multiple skills. The skills tell it how to read submissions, run extraction, trigger validation, draft responses, generate quotes, issue certificates.

Under the hood, a "Renewal Associate" is:
- A scheduled trigger → reading Policy and Customer domain objects
- Running a Compare capability against renewal pricing data
- Identifying premium increases above threshold
- Generating a communication (remarket recommendation) via Email channel
- Surfacing results in the platform UX for human review

The associate mapping research confirmed: 7 core domain objects + 6 core capabilities cover 84% of the entire pricing matrix. Get those 13 things right and you can configure the vast majority of what we sell.

### The Experience Layer

Ryan's wireframes are the vision for what humans see:
- **Pipeline / Submission Queue** — What the user sees on login. All active work.
- **Customer Workspace / Risk Record** — The working session for one customer or one risk.
- **Line Workstream** — LOB-specific application, quoting, binding.
- **Carrier Workstream** — The thread with a specific carrier.

The key insight from the wireframe analysis: the wholesaler view is a CONFIGURATION of the same platform as the retail agency view. Submission Queue is a reconfigured Pipeline. Risk Record is a reconfigured Customer Workspace. Same components, different arrangement. One platform, any customer type.

### CLI-First, Agent-First

Everything goes through the CLI. Stand up a customer: CLI. Deploy associates: CLI. Configure products: CLI. Run evaluations: CLI. Generate documents: CLI. Deploy a website with embedded agents: CLI.

If it can be done through the CLI, an agent can do it. If an agent can do it, it scales infinitely. That's how you get from "5 companies in the lab" to "500 companies on the platform."

This is already proven at small scale. The Indemn CLI can create agents, run evaluations, modify agents based on evaluation results. The OS (Craig's personal operating system with CLI skills) demonstrates at the individual level what the platform will do at the company level: make any operation accessible to AI agents through well-documented, composable interfaces.

The end state: agents building agents. Agents migrating data. Agents configuring workflows. With the click of a button — or a few CLI commands — you set up an end-to-end insurance business. Deploy agents, deploy websites, migrate data, configure products.

### Delivery Channels as First-Class

The platform doesn't just process data. It delivers products.

EventGuard has its own website with an embedded AI agent. Every wedding venue has its own page with a venue-specific agent. This is a delivery mechanism: the system generates and deploys customer-facing experiences.

Product showcase pages, landing pages, embedded widgets, Outlook add-ins, voice agents on phone systems — these are all delivery channels that the platform manages. Stand up a new distribution channel for a partner: configure the product, configure the associate, deploy the embed. CLI.

## What Exists Today

### The Current System (serving customers now):
- Bot-service, voice-service, copilot-server, copilot-dashboard, conversation-service
- Custom implementations per customer (GIC gets one thing, INSURICA gets another)
- Good enough to deliver value, not designed to scale to 50+ customers
- 18 technology systems at 2.3/5.0 average health

### The Starting Materials for the New Platform:
- **Intake Manager** (Dhruv) — The kernel. Submission processing, extraction, validation, quoting. Most mature domain model. Reduced processing from 30 min to 3-4 min. ~50-70% of the insurance domain layer.
- **GIC Email Intelligence** (Craig) — Email classification, extraction, situation assessment, draft generation. 3,214 emails processed. The intelligence layer pattern.
- **Mint** (Craig) — Document generation engine. ACORD 25, premium disclosures. Reusable CLI.
- **EventGuard** — End-to-end embedded insurance. The reference implementation for the full platform vision.
- **Evaluation Framework** — Rubrics, test sets, automated quality measurement. How associates get tested and improved.
- **The CLI** — Agent creation, evaluation, exports. The control plane prototype.
- **The OS** — Session management, dispatch, skills architecture. The meta-layer that orchestrates everything.
- **Product Showcases** — 7 pages on blog.indemn.ai demonstrating real workflows. The closest thing to the actual customer deliverable.

### What We're NOT Doing:
- Not migrating the current system into the new platform
- Not replacing copilot-dashboard
- Not disrupting current customer delivery
- Building something new alongside what exists
- Current implementations inform the platform design
- When the new platform is ready, new customers go on it; existing customers migrate over time

## The Roadmap (Pre-Series A)

All of this needs to be DONE before Series A. When funding arrives, we scale — we don't figure things out.

### Phase 1: The Foundation
Design the domain model. Build core entities with APIs and CLI. The Intake Manager evolves into the platform kernel. This is the engineering bedrock.

### Phase 2: The First Associate
Take one associate — probably the Intake Associate — and make it work on the new platform, configured for two different customer types. Prove that the same platform serves different customers through configuration, not code.

### Phase 3: The Portal
Ryan's wireframes come alive on the new platform. Submission Queue, Risk Record. One portal, configurable per customer type.

### Phase 4: The Lab Proof
End-to-end proof. Take a real scenario and run it entirely on the new platform. Quoting, binding, documents, payments, the whole thing. If this works, the vision is proven.

### Phase 5: The Pitch
Series A with proof, not promises. "Here's the platform. Here's it running real insurance. Here's how $10M scales this to 50 customers and 5 carrier partnerships."

## The Team

- **Craig** — Architect. Owns the vision, the domain model, the roadmap, the OS that executes it. Builds Phase 1. Orchestrates everything.
- **Dhruv** — Platform core engineer. His Intake Manager becomes the kernel. Maintains current production in parallel. His buy-in is the most critical.
- **Ryan** — Domain expert and UX architect. Validates the domain model. Designs the portal. Ensures everything maps to how insurance actually works.
- **George** — EventGuard expert. Pressure-tests the platform against end-to-end insurance (Phase 4).
- **Jonathan** — Voice. Channel layer.
- **Peter** — Builds and deploys. First to stand up customers on the new platform.
- **Rudra** — Integrations. Carrier APIs, AMS, web operators. Connective tissue.
- **Ganesh** — Linear organization. Process tracking.
- **Kyle** — Product vision alignment. Fundraising. Engineering activation.
- **Cam** — GTM. Website discipline. Conference demos. Sales direction.
- **Drew** — Website. The front door.

## The Story

Kyle has been looking for the moat sentence. Cam called every attempt "uninspired." Kyle's Constraint Removal piece gets close: "Insurance's primary constraint has always been ACCESS."

The platform IS the moat. Not "5 years of learnings." Not "insurance expertise." The moat is:

**The only insurance-native domain model with AI agents that can transact, not just talk.**

Every deployment enriches the model. Every carrier integration becomes reusable. Every workflow template works for the next customer. Every capability gets smarter. And because the system is AI-accessible, agents can configure new deployments, run evaluations, and improve themselves.

Kyle wants the "Wikipedia of insurance + AI." Wikipedia didn't make encyclopedias cheaper — it made the concept of "someone has to write and publish this" disappear. The Indemn platform doesn't make insurance operations more efficient — it makes "someone has to build and configure this" disappear. An agent does it. On a domain model that already understands insurance.

**"We built a lab where insurance gets reinvented. Bring us your business, and AI will run it."**

## How We Get Buy-In

Not a document dump. A multi-stage engagement:

1. **Ryan first** — Walk through the domain model. His taxonomy + our engineering model. He validates, he contributes, he sees his work as the foundation. Low risk, high value.

2. **Dhruv second** — Show how the unified model extends his Intake Manager. His code is the kernel. His architecture decisions are honored. He sees his work becoming the platform core, not getting replaced.

3. **George third** — Pressure test with EventGuard. Can this platform model what EventGuard does? If yes, the vision is concrete. If gaps, we fix them.

4. **Kyle and Cam together** — With domain validation and engineering alignment already in hand. The pitch: "Here's the architecture that makes your three-tier model possible. Here's how the $10M builds the machine."

Each conversation builds on the previous. By the time it reaches the group, everyone has already contributed and sees their work in it.

Make it impossible to say no.

## What This Makes Possible

If we build this:

- **The middle market machine works.** AEs land customers, FDEs configure the platform (not code custom solutions), CS expands. Kyle's Tier 1.

- **Enterprise engagements go deeper.** JM, Nationwide — we become their insurance infrastructure. Kyle's Tier 2.

- **Product-led growth becomes real.** Customers self-serve on preconfigured workflows. Eventually, build on our platform themselves. Umbrella insurance, embedded products, new specialty programs — all configurable. Kyle's Tier 3.

- **The moat compounds.** Every deployment makes the domain model richer. Every integration becomes reusable. Every customer's data makes the AI smarter. Competitors have to build all of this from scratch.

- **The team scales.** Instead of 15 engineers doing bespoke work for 18 customers, you have a platform team maintaining the core and a deployment team configuring for hundreds.

- **The Series A story writes itself.** "Here's the platform running real insurance. Here are 5 companies on it. Give us $10M and we'll put 50 on it."

This is how a 15-person company becomes a billion-dollar company. Not by hiring 500 engineers. By building the system that lets AI do the work.
