---
ask: "What is Craig's full vision for the Indemn platform — the insurance lab, the factory, the roadmap, the team, the story?"
created: 2026-03-25
updated: 2026-03-25
workstream: product-vision
session: 2026-03-24-a
version: 2
sources:
  - type: conversation
    description: "Extended brainstorming sessions between Craig and Claude, 2026-03-24/25"
  - type: synthesis
    description: "Drawing on 62+ documents read from Slack, Google Drive, OS projects, codebases, and meeting notes"
---

# The Vision: Building the Factory

## The One-Liner

We proved AI can run an insurance business. Now we're building the factory that lets us do it for anyone.

## EventGuard: The Proof

A 110-year-old carrier gave us a product. We built everything — quoting, binding, payments, compliance, distribution across 351 venues. AI sells the insurance. 2,934 policies. $766K in premium. They acquired it for $2.78M because it worked.

EventGuard proved that AI can run an end-to-end insurance business. Not assist. Not augment. Run. From the moment a customer visits a venue's website to the moment they hold a policy — AI handles every step.

We built it as an MGA lab experiment. One product, one carrier, one team, hand-built from scratch. It was so good it became a standalone business worth acquiring.

That's the proof of concept. Now the question: what if we could do that for any insurance company, for any type of insurance, without starting from scratch each time?

## The Factory

EventGuard was the first product built in the lab. The platform is the factory that makes it repeatable.

Today, every customer gets a bespoke solution. GIC gets custom email intelligence. INSURICA gets custom renewal monitoring. Union General gets custom submission processing. Each one works. Each one required dedicated engineering. Each one taught us something about what insurance businesses actually need.

Those implementations are our R&D. Every bespoke solution we've built is research into what the platform must handle. The patterns repeat: submissions need to be processed, quotes need to be generated, policies need to be managed, documents need to be produced, communications need to happen across channels. Different customers, same underlying operations.

The factory is the system that models those underlying operations once and lets us configure them for anyone. Not a better CRM. Not a nicer chatbot. An engine that models any insurance business as a system of entities, workflows, and AI agents — and lets that business run autonomously.

This is the technology dimension that completes the Series A story. Kyle and Cam articulate what we deliver — four outcomes, revenue engines, 48 associates across three customer types. The factory is HOW we deliver all of it at scale. Without it, we're a services company that builds custom solutions. With it, we're a platform company that configures them.

That's the difference between a $50M outcome and a billion-dollar one.

## The Four Outcomes

Every insurance distribution leader is trying to achieve one of four outcomes. This is Cam's framework, and it's exactly right — it's the customer-facing truth of what we sell:

1. **Revenue Growth** — Unlock capacity to capture missed revenue. 24/7 quoting, binding, eligibility triage, lead capture.
2. **Operational Efficiency** — Liberate staff from administrative drudgery. Automated intake, email triage, document processing, knowledge search.
3. **Client Retention** — Protect the book and maximize lifetime value. Renewal monitoring, cross-sell identification, proactive outreach, lapse prevention.
4. **Strategic Control** — Visibility, agility, and governance. Analytics, audit trails, workflow configuration, distribution management.

These aren't four separate product lines. They're four reasons a customer calls us. And every one of them is delivered through the same factory.

## The Four Engines

The outcomes map to engines — the product-level groupings that organize how we deliver:

- **Revenue Engine** — 24/7 quoting/binding, eligibility triage, agent portal support, embedded distribution. Best for MGAs drowning in submissions and program admins scaling distribution.
- **Efficiency Engine** — Service automation, underwriting guardrails, internal knowledge search, email intelligence. Best for retail agencies with high service volume and MGAs with inbox chaos.
- **Retention Engine** — Silent churn defender, cross-sell identification, lapse prevention, renewal remarketing. Best for agencies protecting their book.
- **Control Engine** — Strategy Studio, distribution analytics, audit trails, workflow configuration. Best for ops leaders needing visibility.

All four engines share a single brain — one knowledge base trained on a customer's products, guidelines, and workflows. Train once, deploy across use cases.

The engines are the product packaging. The factory is what powers them all.

## Associates: Where the Engine Meets the Customer

The 48 associates in Cam's pricing matrix — across Agencies, Carriers, and Distribution — are not 48 different products. They are 48 configurations of the same underlying system.

Each associate is an AI agent equipped with skills that define how to interact with the platform via CLI and API. One associate has a role. One associate has multiple skills. The skills tell it how to read submissions, run extraction, trigger validation, draft responses, generate quotes, issue certificates.

Under the hood, a "Renewal Associate" is:
- A scheduled trigger → reading Policy and Customer entities
- Running a Compare capability against renewal pricing data
- Identifying premium increases above threshold
- Generating a communication (remarket recommendation) via Email channel
- Surfacing results in the platform UX for human review

A "Quote & Bind Associate" for embedded distribution is:
- A web widget trigger → collecting applicant information into a Submission
- Running eligibility against Carrier appetite rules
- Generating a Quote via a rating integration
- Executing a Bind → creating a Policy and triggering Payment
- Issuing a Certificate and sending confirmation via Email

Different associates, different outcomes, same engine underneath. The associate mapping research confirmed: 7 core entities + 6 core capabilities cover 84% of the entire pricing matrix. Get those 13 things right and you can configure the vast majority of what we sell.

The three target groups — Agencies, Carriers, Distribution/MGAs — are configurations of the same platform, not separate architectures. This is what Kyle's three-tier model (middle market + enterprise + product partnerships) needs to work: one platform serving all three through configuration.

## The Engine: What We're Actually Building

### An Object-Oriented Insurance System

At its core, we are modeling the businesses in our space as entities and integrating AI into the entire system.

Every entity that exists in an insurance business — submissions, policies, quotes, carriers, agents, coverages, claims, premiums, commissions — is modeled as a first-class object with:
- A schema (what fields it has)
- A state machine (how it transitions through its lifecycle)
- An API (full CRUD operations)
- A CLI (agent-accessible, human-accessible)

The system is organized into sub-domains that mirror how insurance actually works:
- **Core Insurance** — Products, coverages, LOBs, class codes, rating, appetite, underwriting guidelines
- **Risk & Parties** — Insureds, agents, agencies, carriers, distribution partners
- **Submission & Quoting** — Applications, submissions, quotes, underwriting decisions
- **Policy Lifecycle** — Binders, policies, endorsements, renewals, cancellations, certificates
- **Claims** — Claims, claimants, reserves, loss history
- **Financial** — Premiums, payments, invoices, commissions, trust accounting
- **Authority & Compliance** — Delegated authority, licensing, surplus lines, regulatory filings
- **Distribution & Delivery** — Programs, product configurations, deployments, partner management

The system should be so foundational, so primitive, so atomic that there is no situation in any customer's insurance business that can't be handled within our system. If it exists in insurance, there is a way to model it and operate on it through the platform.

The domain model is the engine. 44 aggregate roots across 9 sub-domains, classified using domain-driven design. Built incrementally — Phase 1 covers the ~25 things needed for current associate capabilities, Phase 2 adds financial and distribution for middle market, Phase 3 adds authority, compliance, and claims for carrier-grade operations.

### CLI-First, Agent-First

Everything goes through the CLI. Stand up a customer: CLI. Deploy associates: CLI. Configure products: CLI. Run evaluations: CLI. Generate documents: CLI. Deploy a website with embedded agents: CLI.

If it can be done through the CLI, an agent can do it. If an agent can do it, it scales infinitely. That's how you get from "5 companies in the lab" to "500 companies on the platform."

This is already proven at small scale. The Indemn CLI can create agents, run evaluations, modify agents based on evaluation results. The OS demonstrates at the individual level what the platform will do at the company level: make any operation accessible to AI agents through well-documented, composable interfaces.

The end state: agents building agents. Agents migrating data. Agents configuring workflows. With a few CLI commands, you set up an end-to-end insurance business. Deploy agents, deploy websites, migrate data, configure products.

### The Experience Layer

Ryan's wireframes are the vision for what humans see:
- **Pipeline / Submission Queue** — What the user sees on login. All active work.
- **Customer Workspace / Risk Record** — The working session for one customer or one risk.
- **Line Workstream** — LOB-specific application, quoting, binding.
- **Carrier Workstream** — The thread with a specific carrier.

The key insight from the wireframe analysis: the wholesaler view is a CONFIGURATION of the same platform as the retail agency view. Submission Queue is a reconfigured Pipeline. Risk Record is a reconfigured Customer Workspace. Same components, different arrangement. One platform, any customer type.

### Delivery Channels as First-Class

The platform doesn't just process data. It delivers products.

EventGuard has its own website with an embedded AI agent. Every wedding venue has its own page with a venue-specific agent. This is a delivery mechanism: the system generates and deploys customer-facing experiences.

Product pages, landing pages, embedded widgets, Outlook add-ins, voice agents on phone systems — these are all delivery channels that the platform manages. Stand up a new distribution channel for a partner: configure the product, configure the associate, deploy the surface. CLI.

## The Insurance Lab

With the factory built, we become a lab where insurance gets reinvented.

Imagine a cohort. Five insurance companies join the Indemn lab. Each represents a different type of business — but all run on the same platform:

**The Carrier** — like what we did with JM/EventGuard, but configured on the platform instead of hand-built. A carrier wants to launch a new specialty product. We model their product, configure associates to sell it, deploy it on partner websites. End-to-end: customer asks questions → gets a quote → binds → pays → receives policy. What took us months of custom engineering with EventGuard becomes weeks of configuration.

**The MGA/Wholesaler** — like what we're building for GIC, but on the platform. Their inbox gets 100+ emails a day. We model their business — carriers, agents, appetite rules, LOBs. Configure the Intake Associate. Emails arrive, get classified, extracted, validated, routed. Quotes come back, get compared, get sent to the retail agent. What we learned building GIC's bespoke email intelligence becomes a configurable workflow.

**The Retail Agency** — like what we deliver for INSURICA, but on the platform. Their phones ring constantly — billing questions, COI requests, policy changes. We configure the Front Desk Associate, the Renewal Associate, the Cross-Sell Associate. What we learned from INSURICA's renewal workflows and service patterns becomes reusable capability.

**The Program Administrator** — standing up new distribution channels. Instead of building a portal from scratch, they configure a product on the platform, define the underwriting rules, deploy associates on partner websites. What we learned from Union General's specialty underwriting becomes a template.

**The Wholesale Broker** — transforming email-driven operations. Two internal teams sharing inbox chaos become an organized submission pipeline with cross-team visibility. What we learned from GIC's two-stream workflow becomes a configurable pattern.

Each company gets onboarded. Their business is modeled. Associates are configured. Channels are connected. Within weeks, they have a fully operational digital insurance business running on Indemn.

Every bespoke solution we've built — EventGuard, GIC email, INSURICA renewals, Union General intake, the product showcases — is R&D that informed this design. The patterns we discovered are baked into the platform. The factory produces what the lab invented.

## What We've Learned (R&D That Informs the Platform)

### EventGuard — End-to-End Proof of Concept
The reference implementation. Proved that AI can run a complete insurance program: quoting, binding, payments, compliance, distribution. 351 venue websites, 2,934 policies, $766K premium. Teaches us: what does the full policy lifecycle look like on a platform? What does embedded distribution require? How do payments, compliance, and revenue sharing work?

### GIC Email Intelligence — The Intelligence Layer
3,214 emails classified, 2,754 submissions linked. Built the pattern for email → classification → extraction → situation assessment → draft generation. Teaches us: how does unstructured input become structured domain data? How do two internal teams (CS/servicing + placement/underwriting) share a workflow?

### Intake Manager (Dhruv) — The Platform Kernel
The most mature domain model in the company. Submission processing, extraction, validation, quoting. Reduced underwriter processing from 30 min to 3-4 min. ~50-70% of the platform foundation already exists here. Teaches us: how do submissions flow through configurable workflows? How does extraction work against variable forms?

### INSURICA — Retention at Scale
3.7x expansion in 5 months. Renewal monitoring, CSR automation, multi-channel service. Teaches us: what does the Retention Engine actually need? How do renewal workflows and cross-sell identification work?

### Product Showcases — Capability Demonstrations
7 pages on blog.indemn.ai demonstrating workflows: Document Retrieval, Quote & Bind, Conversational Intake, Email Intelligence, Intake Manager, Cross-Sell, CLI tools. Created for conferences and sales conversations. Each demonstrates a real capability that needs to be refined and aligned with the platform vision. They show what's possible — the platform makes it repeatable.

### The Starting Materials
- **Intake Manager** — the kernel. Evolves into the platform core.
- **GIC Email Intelligence** — the intelligence layer pattern.
- **Mint** — document generation engine. ACORD 25, premium disclosures. Reusable CLI.
- **Evaluation Framework** — rubrics, test sets, automated quality. How associates get tested and improved.
- **The CLI** — agent creation, evaluation, exports. The control plane prototype.
- **The OS** — session management, dispatch, skills architecture. The meta-layer that orchestrates everything.

### What We're NOT Doing
- Not migrating the current system into the new platform
- Not replacing copilot-dashboard
- Not disrupting current customer delivery
- Building something new alongside what exists
- Current implementations are R&D that informs the platform design
- When the new platform is ready, new customers go on it; existing customers migrate over time

## The Team

- **Craig** — Architect. Owns the vision, the domain model, the roadmap, the OS that executes it. Builds the foundation. Orchestrates everything.
- **Dhruv** — Platform core engineer. His Intake Manager becomes the kernel. Maintains current production in parallel. His buy-in is the most critical — his work IS the foundation.
- **Ryan** — Domain expert and UX architect. Validates the domain model against insurance reality. Designs the experience layer. Ensures everything maps to how insurance actually works.
- **George** — EventGuard expert. Pressure-tests the platform against end-to-end insurance. Knows what "running real insurance" requires.
- **Jonathan** — Voice. Channel layer.
- **Peter** — Builds and deploys. First to stand up customers on the new platform.
- **Rudra** — Integrations. Carrier APIs, AMS, web operators. Connective tissue. Bus factor risk (solo on integrations).
- **Ganesh** — Linear organization. Process tracking.
- **Kyle** — CEO. Product vision alignment. Fundraising. Engineering activation. Three-tier model.
- **Cam** — COO. GTM. Website discipline. Four Outcomes framework. Conference demos. Sales direction.
- **Drew** — Website. The front door.

## The Story

Kyle has been looking for the moat sentence. Cam called every attempt "uninspired." Kyle's Constraint Removal piece gets close: "Insurance's primary constraint has always been ACCESS. Generative AI removes the access constraint entirely."

The moat isn't a sentence. The moat is the factory.

**The only insurance-native domain model with AI agents that can transact, not just talk.**

Every deployment enriches the model. Every carrier integration becomes reusable. Every workflow template works for the next customer. Every capability gets smarter. And because the system is AI-accessible, agents can configure new deployments, run evaluations, and improve themselves.

Kyle wants the "Wikipedia of insurance + AI." Wikipedia didn't make encyclopedias cheaper — it made the concept of "someone has to write and publish this" disappear. The Indemn platform doesn't make insurance operations more efficient — it makes "someone has to build and configure this" disappear. An agent does it. On a domain model that already understands insurance.

EventGuard proved it's possible. The factory makes it repeatable.

**"We built the lab. We proved AI can run insurance. Now we're building the factory. Bring us your business."**

## What This Makes Possible

If we build this:

- **The middle market machine works.** AEs land customers, FDEs configure the platform (not code custom solutions), CS expands. Kyle's Tier 1. Powered by the Efficiency and Revenue Engines.

- **Enterprise engagements go deeper.** JM, Nationwide — we become their insurance infrastructure. Kyle's Tier 2. The factory produces custom programs through configuration.

- **Product-led growth becomes real.** Customers self-serve on preconfigured workflows. Eventually, build on our platform themselves. Umbrella insurance, embedded products, new specialty programs — all configurable. Kyle's Tier 3. The Control Engine gives them the tools.

- **The moat compounds.** Every deployment makes the domain model richer. Every integration becomes reusable. Every customer's data makes the AI smarter. Competitors have to build all of this from scratch.

- **The team scales.** Instead of 15 engineers doing bespoke work for 18 customers, you have a platform team maintaining the core and a deployment team configuring for hundreds.

- **The Series A story completes.** Kyle and Cam tell investors what we deliver — four outcomes, revenue engines, proven with EventGuard and 18 customers. Craig adds the technology dimension: here's the factory that makes it scale infinitely. "Here's the platform. Here's EventGuard running on it. Here's how $10M scales this to 50 customers and 5 carrier partnerships."

This is how a 15-person company becomes a billion-dollar company. Not by hiring 500 engineers. By building the system that lets AI do the work.

## The Roadmap (Pre-Series A)

All of this needs to be READY before Series A. When funding arrives, we scale — we don't figure things out.

*Detailed phased roadmap to be developed — will cover design, implementation, priorities, roles, time allocations, and execution. Each phase delivers standalone value toward the complete factory.*

## How We Get Buy-In

Not a document dump. A multi-stage engagement:

1. **Ryan first** — Walk through the domain model. His taxonomy + our engineering model. He validates, he contributes, he sees his work as the foundation. Low risk, high value.

2. **Dhruv second** — Show how the unified model extends his Intake Manager. His code is the kernel. His architecture decisions are honored. He sees his work becoming the platform core, not getting replaced.

3. **George third** — Pressure test with EventGuard. Can this platform model what EventGuard does? If yes, the factory can produce anything. If gaps, we fix them.

4. **Kyle and Cam together** — With domain validation and engineering alignment already in hand. The pitch: "Your business story is exactly right. Here's the technology that makes it 100x bigger. Here's the factory that makes your three-tier model possible. Here's how the $10M builds the machine."

Each conversation builds on the previous. By the time it reaches the group, everyone has already contributed and sees their work in it.

Make it impossible to say no.
