---
ask: "What is the core framing for Indemn's platform vision?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-25-a
sources:
  - type: conversation
    description: "Craig's articulation of the vision during session 2026-03-25, building on 2026-03-24/25 brainstorming"
---

# The Operating System for Insurance

## The Core Idea

Indemn is building the operating system for insurance. Not a tool. Not a platform you plug into your stack. The operating system that the entire insurance business runs on.

Like an actual OS: you don't build a new one for every customer. The OS already understands the domain. You configure it, install the applications you need, connect it to external systems, and the business runs.

## The Analogy (Precise, Not Metaphor)

- **Hardware** = Carriers (binding authority), regulations, the physical insurance industry. The underlying reality.
- **Operating System** = Indemn's system. Domain model, entities, APIs, CLI. The infrastructure layer that models the entire insurance business.
- **Applications** = Associates, configured workflows, customer-facing products. The things that run on the OS to deliver outcomes.
- **Users** = Insurance businesses, agents, consumers. The people who interact with the applications.

You don't rebuild the OS for each customer. Applications run on the OS. The OS abstracts away the complexity of the insurance domain. Developers can build new applications on it. It gets better with every deployment.

## The System Is in the Middle

The Indemn system is the hub. Everything else connects to it.

**Inputs** — any channel, any source:
- Web chat agents (consumers, agents)
- Voice agents (phone systems)
- Email automations (inbound/outbound)
- Text/SMS automations
- Form submissions (web, PDF, ACORD)
- Data from external systems (AMS, carrier portals, CRM)
- API integrations
- Web operators (automating legacy system interactions)

**The OS processes everything** — submissions, quotes, policies, claims, payments, documents, communications, compliance. Every entity in the insurance business is modeled, has a state machine, has an API, has a CLI command.

**Outputs** — any destination, any format:
- Policy documents, certificates, disclosures
- Payments to carriers, commissions to agents
- Communications across all channels
- Data to external systems (AMS sync, carrier reporting, bordereaux)
- Regulatory filings
- Analytics and reporting
- Websites, landing pages, embedded widgets

Whether a business runs entirely on Indemn or keeps their legacy systems and connects them — either way, the Indemn OS is the engine processing everything. We're the electricity that powers the insurance business.

## Why Implementation Is Trivially Fast

If the OS is built right — the domain model covers everything, the CLI is comprehensive, the APIs are complete — then setting up a new customer is configuration, not construction.

A Claude Code agent reads an implementation plan. Runs CLI commands in parallel:
- `indemn org create "Acme Insurance"`
- `indemn product configure --carrier hartford --lob gl --template commercial-gl`
- `indemn associate deploy --type intake --config acme-intake.yaml`
- `indemn channel connect --type email --provider outlook --org acme`
- `indemn integration connect --type ams --provider applied-epic --org acme`

The hard work was building the operating system. Using it is configuration. Seconds, hours, days — not weeks or months. The same way installing an app on your phone takes seconds because the OS already handles everything underneath.

This is what "scales infinitely" actually means in practice. Not "we hire more engineers." An AI agent executes an implementation plan using the CLI. Parallel sub-tasks. An hour.

## Carriers as Conduit

Carriers have binding authority — the legal right to write insurance. Their products exist but are trapped in legacy systems, distributed through outdated channels, processed through manual workflows.

Indemn takes their products and makes them digital-native. The product is reborn on the OS:
- It can be sold through any channel (web, voice, email, embedded)
- It can be processed entirely by AI (quoting, binding, issuance)
- It can be managed end-to-end (servicing, renewals, claims)
- It reaches customers the carrier could never reach on their own

The carrier wins: their product gets a new life, new distribution, new scale. Indemn wins: the OS powers it all. This is the EventGuard model at scale — JM's product, reborn as a digital-native insurance experience on the Indemn OS.

## Three Access Tiers (Growth Model)

1. **Out of the box** — Customer buys from the website. Preconfigured product. Live immediately. Self-service. This is the product-led growth play.

2. **Configured** — Indemn (or an AI agent) configures the customer's business on the OS. Connects their systems, sets up their workflows, deploys their associates. This is the middle market machine.

3. **Developer CLI** — Tech-savvy insurance people use the CLI to build their own products on the infrastructure. They create their own associates, define their own workflows, build entirely new insurance products. This is the AWS play — developers building on the OS. This is when the platform becomes the industry standard.

## What This Really Is

This isn't AI-first insurance. It's deeper than that.

It's the deep agent capabilities to build insurance products at scale that are entirely digital. We're digitizing the insurance world. Every insurance product, every workflow, every business process — modeled, automated, and run on a single operating system.

We can automate parts of a business. We can automate full lines of business. We can digitize an entire company. The possibilities are defined only by the completeness of the OS and the insurance domain it models.

Any solution, if it's related to insurance, can be developed on the OS and implemented through the OS. EventGuard proved it's possible. The OS makes it repeatable for anything.

## The Four Outcomes (What Customers Buy)

Every insurance distribution leader wants one of four outcomes:

1. **Revenue Growth** — New capacity, new channels, new products
2. **Operational Efficiency** — Automate the drudgery
3. **Client Retention** — Protect and grow the book
4. **Strategic Control** — Visibility and governance

These are the applications that run on the OS. The Four Engines (Revenue, Efficiency, Retention, Control) are the product groupings. The 48 associates are the configured agents that deliver them. All powered by the same OS underneath.

The business story (Kyle, Cam) and the technology story (Craig) are the same story told from two sides. The Four Outcomes are why customers buy. The OS is how it all works. Together, that's the Series A pitch.

## EventGuard: The Proof

EventGuard is the proof that this concept works. Built as an MGA lab experiment — one product, one carrier, hand-built from scratch. AI runs the entire insurance program: quoting, binding, payments, compliance, distribution across 351 venues. 2,934 policies. $766K in premium. Acquired for $2.78M.

EventGuard proved that AI can run an end-to-end insurance business. The OS is what lets us do that for anyone, for any type of insurance, without starting from scratch.

Every bespoke solution we've built since — GIC's email intelligence, INSURICA's renewal monitoring, Union General's submission processing — is R&D. Each one taught us what the OS must handle. The patterns we discovered are baked into the design. The domain model, the entity system, the workflow engine — all informed by real implementations for real customers.

Now we're building the OS itself. When it's ready, every new customer is configuration. Every new product is an application. Every new capability makes the OS smarter for everyone.

## The Convergence

Kyle's document: "Customer Operating System." Craig's personal project: an operating system for his own work. The company vision: the operating system for insurance.

It all converges on the same concept at different scales. The OS for one person (Craig's). The OS for one company's customer intelligence (Kyle's). The OS for the entire insurance industry (the vision).
