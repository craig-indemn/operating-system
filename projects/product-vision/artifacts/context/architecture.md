---
ask: "What is the architecture — domain taxonomy, engineering model, what's built, what's the vision?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-24-a
sources:
  - type: local
    description: "Platform Architecture project artifacts — unified-architecture-model.md, slack-context-and-customer-intel.md"
  - type: local
    description: "Ryan's wireframes — 6 HTML/PDF files in gic-email-intelligence/artifacts/"
  - type: google-doc
    ref: "1_rtTKbAl8Tvhq_ZKPoobH09hK63COaI9iAVBxXw2jJc"
    name: "Indemn Technology Systems Map"
  - type: google-doc
    ref: "1OMud6HWGrsAnKEesx7cWXBFLeLu07bm82RXMcyixArA"
    name: "Engineering Priorities -- Landscape Analysis"
  - type: analysis
    description: "Domain model validation — 5 agents (retail, MGA, carrier, embedded, codebase)"
  - type: codebase
    description: "Intake Manager, GIC Email Intelligence, bot-service, copilot-server, platform-v2 models"
---

# Architecture Context

## Ryan's Insurance Domain Taxonomy

Four levels + two cross-cutting facets:
- **Level 1: Outcomes** — Revenue, Efficiency, Retention, Control (maps to Cam's four outcomes)
- **Level 2: Journeys** — P&C lifecycle stages (Prospect & Intake → Submission → Quote → Bind & Issue → Servicing → Renewal → Claims)
- **Level 3: Workflows** — Bounded sequences within journeys (Process HO submission, Renewal w/ remarket trigger, Medicare med matching)
- **Level 4: Capabilities** — Atomic, reusable, composable (Extract entity data from email, Check carrier appetite rules, Drug formulary lookup)
- **Cross-cutting: Channels** (Voice, Chat, Email, Web, SMS) and **Actors** (Policyholder, Agent, Broker, Carrier)

Ryan's architecture layers (right side of his diagram):
- **Layer 4: Application** — Admin, HITL, Analytics, Templates
- **Layer 3: Insurance Domain** — "the moat" (3a: Knowledge corpus, 3b: Callable capabilities, 3c: Automated workflows)
- **Layer 2: Integration** — Carrier APIs, AMS, Web operators, Payments
- **Layer 1: Runtime infra** — LLM engine, Voice, Channels, Vector DB

Key connection: **Taxonomy capabilities = Architecture Layer 3b (the hinge).** Taxonomy workflows = Architecture Layer 3c.

Product bundles = compositions drawn from both frames. Each SKU selects journeys + workflows + capabilities + channels + integrations.

## Craig's Unified Architecture Model (from platform-architecture project, March 17)

Five core concepts bridging domain taxonomy and engineering:

1. **Domain Objects** — The nouns. Source of truth. Each has schema, state machine, API. (Submission, Quote, Policy, Certificate, Email, Message + actors: PolicyHolder, Agent, Broker, Carrier)

2. **Capabilities** — The verbs. Ryan's Layer 3b. Atomic, reusable functions that operate on domain objects. (Extract, Validate, Generate, Classify, Quote, Search, Route, Notify, Transform)

3. **Workflow Templates** — Composed sequences of capabilities. Ryan's Layer 3c. Shared patterns parameterized by customer-specific business rules. (Submission Intake, Quote Processing, Document Generation, Email Triage, Policy Servicing)

4. **Channels** — How things enter and exit the system. **Key insight: AI agents are a CHANNEL into the insurance platform, not a separate system.** (AI Chat, AI Voice, Mail/Gmail/Outlook, Customer Phone Systems, Web Portal, Webhooks/API)

5. **Customer Configuration** — What makes one customer different from another. Not code — config. (Extraction schemas, validation rules, workflow matching, document templates, rate tables, provider config, business hours)

## Craig's Platform Vision (the full thesis)

Indemn becomes an insurance lab. The platform is an object-oriented system that models the entire insurance business. Every entity has a schema, state machine, and API. All accessible via CLI. All interactable by AI agents.

**Three layers:**
- **The Domain Model** — Insurance entities modeled with schemas, state machines, APIs, CLI access
- **The Associates** — AI agents equipped with skills that operate on the domain model via CLI/API. Configured, not coded.
- **The Experience Layer** — Ryan's wireframes come alive. Portal configurable per customer type.

**CLI-first everything.** Stand up a customer: CLI. Deploy associates: CLI. Configure products: CLI. Run evaluations: CLI. If it can be done through CLI, an agent can do it. If an agent can do it, it scales infinitely.

**The lab model:** Take any insurance company, model their business on the platform, configure associates, connect channels — they're running on Indemn in weeks. "EventGuard without starting EventGuard."

**AI-first design:** The system is designed so agents can interact with and build on it. Agents building agents. Agents migrating data. Agents configuring workflows. The OS (Craig's personal operating system with CLI skills) is the precursor and prototype.

**The unlock:** Three tiers of platform usage:
1. **Managed service** — Indemn deploys and runs associates (current model)
2. **Self-service workflows** — Preconfigured workflows, customize via config (middle market machine)
3. **Build on the platform** — Use domain model + CLI + API to build your own insurance products (AWS-for-insurance play)

## The Technology Systems Map (18 systems across 4 layers)

From Kyle's Mar 23 document. System health average: 2.3/5.0.

### L1 — Runtime Infrastructure (competitor parity sufficient):
- #1 Conversational AI Engine (bot-service) — 3/5, $311K, 14+ customers
- #2 Voice System (voice-livekit) — 4/5, $0-60K, 8 customers
- #4 Knowledge Base — 1/5, 3 customers asking
- #5 Real-Time Comms & Email — 1/5, 6 customers pulling, BIGGEST GAP (nobody owns it)
- #16 Compliance & Security — 5/5, SOC2

### L2 — Integration Connective Tissue:
- #9 Carrier & AMS Integrations — 2/5, $87K, 7 customers, Rudra solo = bus factor
- #15 Web Operators — 2/5, 5 customers, becoming real product line
- #17 Payments & Billing — 1/5, JM only

### L3 — Insurance Domain Layer ("The moat. Accumulates competitive value with each deployment."):
- #7 EventGuard / Embedded Insurance — 3/5, $745K ceiling
- #8 Insurance Skills Library — 2/5, $197K, underleveraged
- #14 Human-in-the-Loop — 2/5, 5 customers, compliance architecture

### L4 — Platform Application Layer:
- #3 Platform Dashboard — 3/5, copilot-dashboard
- #10 Templates & Onboarding — 3/5, Ryan coming onboard
- #11 Landing Pages & Distribution — 3/5, NO OWNER
- #12 Evaluation & Testing — 4/5, quality infrastructure
- #13 Analytics & Observatory — 3/5, demand from customers

### Operational:
- #18 Agent Maturity Pipeline — 1/5, internal only

Key cross-cutting concept: **Associate = Configured in L4, powered by L3 domain skills, connected via L2, running on L1. The workforce concept lives across the entire stack.**

## Engineering Priorities Landscape (March 2026)

Two expansion patterns observed:
1. **Web Chat → Voice** (expansion lever): Distinguished, GIC, Branch all went this path
2. **Conversation → Integration Depth** (retention lever): UG needs comparative rater, INSURICA needs Salesforce, Johnson needs Applied Epic

Invest quadrant (high value, needs work): Integrations (#9), Insurance Skills (#8), Comms & Email (#5), EventGuard (#7), AI Engine (#1)
Protect quadrant (high value, healthy): Voice (#2), Compliance (#16), Evaluation (#12)
Level Up (moderate value, easy wins): Dashboard (#3), Web Operators (#15), HITL (#14), Templates (#10), Analytics (#13)
Question (unclear value): KB (#4), Payments (#17), Agent Maturity (#18), Landing Pages (#11)

## Ryan's Wireframes (read in full)

### Retail Agency Wireframes v2 (4 screens):
- **L1 Pipeline** — Customer-first list. Columns: customer/account, lines, overall status, last activity, action needed. Ops role widens scope. Unassigned intake bar at bottom.
- **L2 Customer Workspace** — Four-panel layout: customer profile (shared across lines), comms stream (all channels, LOB-tagged), coverage opportunity cards (one per LOB, gateway to L3), placement status summary (per-carrier, per-line)
- **L3 Line Workstream (GL)** — Application tab (AI-extracted fields, inline validation, section nav), Quote tab (carrier status cards, comparison table, accept actions)
- **L4 Carrier Workstream Detail** — Reverse-chronological carrier thread. AI draft reply with review/send. Status timeline. Aging indicator.

### GIC Wholesaler Wireframes (screen delta + 2 new):
- **Screen delta table** — Maps retail → wholesaler. Most carry over or light reconfig. Two genuinely new screens.
- **Submission Queue** (new) — Risk/submission-first (not customer-first). Columns: risk/insured, retail agent, line, UW stage, action needed. CS team activity flag. Unread email bar.
- **Risk Record** (new) — Central workspace for one submission. Same 4-panel layout but: left = submission data (not profile), right = stage progress + UW decision prompt (not coverage cards). Multi-channel thread accretes email, voice, CS chat. Cross-team visibility flag.

Key insight from wireframes: **wholesaler is a configuration of the same platform, not a separate product.** Submission Queue is a reconfigured Pipeline. Risk Record is a reconfigured Customer Workspace.

### Wholesaler Interaction Flow:
Two parallel streams (CS/servicing + placement/underwriting) sharing a retail agent population. Converge at the Risk Record. 10-step flow from contact through bind. Voice agent triage is new surface area (not in original three-scenario diagrams).

### Retail IA:
Screen hierarchy L1→L2→L3→L4 with component classification: Universal (same for all), Configurable (operator sets parameters), Custom (requires Indemn engineering). Data residency: Shared (customer level), Local (single workstream), Ingested (arrives via channel).

### Component Inventory:
34 components organized across levels.

## What Exists in Code Today

### Intake Manager (most mature domain model):
- **Submission** — 7-stage processing (received → completed), SubmissionStatus, AutomationStatus
- **SubmissionState** — Accumulated parameters with email thread history
- **Quote** — Versioned per-provider, 7-status lifecycle, taxes/fees, comparison
- **Parameter** — Flattened individual fields with audit trails, validation tracking
- **Workflow** — Config-driven: matching rules, extraction config, validation config, quote provider config
- **FormSchema** — Dynamic form definitions (tabs → sections → fields)
- **ThreadEvent** — Event sourcing (email_received, document_upload, parameter_update, etc.)
- Built over 4-5 sprints by Dhruv. Reduced underwriter processing from 30 min to 3-4 min. 10-15 submissions/day for Union General.

### GIC Email Intelligence (Craig's model):
- **Email** — Outlook Graph metadata, processing status, classification
- **Submission** — 8-stage lifecycle with ball_holder tracking (queue/gic/agent/carrier/done)
- **SituationAssessment** — AI contextual analysis with next-action recommendation
- **Draft** — Suggested email replies with type, confidence, review status
- **Extraction** — Structured data from attachments
- **Carrier** — USLI, Hiscox, Granada/GIC with binding authority, submission methods
- **Agent** — Retail agent/agency with codes, LOBs, submission stats
- 3,214 emails classified, 2,754 submissions linked, 304 extractions, 122 drafts

### Critical gap between the two:
Intake Manager and GIC Email Intelligence model Submission differently — different lifecycles, different fields, different databases. Unifying these is the first concrete engineering task for the new platform.

### Bot-service / Copilot:
- Conversations (requests), agent configs (faq_kbs, bot_configurations), knowledge bases, CSR feedback, RLHF suggestions
- Organization, Project, User, Channel, Distribution (widget deployments), Lead, Template

### Platform V2:
- Agents, Templates, TestSets, Rubrics, Evaluations, JarvisJobs

### EventGuard / Conversation Service:
- Quote records (simple), Stripe payment integration (201 hard-coded links), 351 venue landing pages

### What does NOT exist in code:
Policy, Coverage, Product, Premium (standalone), Commission, Claim, Endorsement, Certificate, Binder, Insured/Risk, DelegatedAuthority, License, Payment, Invoice, Reserve, Rating — essentially the entire post-bind world and the financial layer.

## Domain Model Research (validated model)

Original 22-entity proposal pressure-tested from 5 angles (retail agency, MGA/wholesaler, carrier, embedded insurance, codebase). Found to cover ~30-40% of what's needed.

### 9 Sub-Domains (~70 entities total):

**1. Core Insurance:** Product, LineOfBusiness, Coverage, PolicyForm, ClassCode, Territory, RateTable, RatingFactor, Appetite, UnderwritingGuideline

**2. Risk & Parties:** Insured, Risk/InsuredAsset, Contact/Party, RetailAgent, Agency, Carrier, DistributionPartner, Underwriter

**3. Submission & Quoting:** Application, Submission, SubmissionLine, SubmissionRequirement, FormSchema, Quote, QuoteOption, Subjectivity, RatingTransaction, UnderwritingDecision, SituationAssessment

**4. Policy Lifecycle:** Binder, Policy, PolicyTerm, PolicyTransaction, Endorsement, Renewal, Cancellation, Certificate, CertificateHolder

**5. Claims:** Claim, Claimant, Incident, ClaimTransaction, Reserve, LossHistory, SubrogationRecovery

**6. Financial:** Premium, Payment, Invoice, PaymentPlan, UnearnedPremiumReserve, CommissionSchedule, CommissionTransaction, CommissionSplit, RevenueShareAgreement, PremiumTrustAccount, Bordereaux

**7. Authority & Compliance:** DelegatedAuthority, AuthorityLimit, Referral, License, ProducerAppointment, SurplusLinesTransaction, RegulatoryFiling, ComplianceRequirement

**8. Distribution & Delivery:** Program, ProductConfiguration, Deployment, Panel/Market, CarrierAgreement, Embed/DistributionSurface

**9. Platform Layer (separate from domain):** Associate, Skill, BotConfiguration, Workflow, Rule, Template, KnowledgeBase, Channel, Organization, Project, Task, Interaction, Correspondence, Document, Email, Draft, ParameterAudit

### 5 Universal Findings:
1. Separate platform from domain
2. Policy lifecycle is the backbone
3. Configuration ≠ transactions
4. "Customer" is wrong — real entities are Insured, RetailAgent, Agency, Carrier, DistributionPartner
5. Financial layer is severely underdeveloped

### Status: DRAFT — needs review pass for redundancies, over-engineering, clean boundaries. Should be validated with Ryan (insurance reality) and Dhruv (implementation reality) during stakeholder engagement.

## What We're Building (Craig's framing)

**Not a migration. A new platform built alongside the current system.**

Current system (bot-service, copilot, etc.) keeps serving current customers. The new platform starts from Intake Manager as the kernel and grows into the full vision. Current customer implementations are R&D that informs the platform design.

The bridge: GIC's email patterns → email channel. INSURICA's renewal workflow → workflow template. EventGuard's end-to-end flow → reference implementation. Silent Sports' doc gen → capability module.

Architecture is designed once, built incrementally. Each sub-domain has its own schemas, APIs, CLI commands. New sub-domains plug in without restructuring.
