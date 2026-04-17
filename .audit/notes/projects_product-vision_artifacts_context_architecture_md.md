# Notes: context/architecture.md

**File:** projects/product-vision/artifacts/context/architecture.md
**Read:** 2026-04-16 (full file — 225 lines)
**Category:** stakeholder-context

## Key Claims

- **Ryan's insurance domain taxonomy (4 levels + cross-cutting)**:
  - L1 Outcomes (Revenue, Efficiency, Retention, Control)
  - L2 Journeys (P&C lifecycle stages)
  - L3 Workflows (bounded sequences within journeys)
  - L4 Capabilities (atomic, reusable, composable)
  - Cross-cutting: Channels (Voice/Chat/Email/Web/SMS) + Actors (Policyholder/Agent/Broker/Carrier)
- **Ryan's architecture layers**: L1 Runtime infra → L2 Integration → L3 Insurance Domain (the moat) → L4 Application.
- **Key connection**: Taxonomy capabilities = Architecture Layer 3b (the hinge). Workflows = Layer 3c.
- **Craig's unified architecture model** — 5 core concepts bridging domain taxonomy and engineering:
  1. Domain Objects (the nouns, source of truth)
  2. Capabilities (the verbs, atomic/reusable)
  3. Workflow Templates (composed sequences, parameterized by config)
  4. **Channels — "AI agents are a CHANNEL into the insurance platform, not a separate system."**
  5. Customer Configuration (what makes each customer different, not code)
- **Technology Systems Map (18 systems across 4 layers)** — system health avg 2.3/5.0. L1 runtime, L2 integration, L3 insurance domain (the moat), L4 platform application.
- **Engineering priorities**: two expansion patterns observed — Web Chat → Voice (Distinguished, GIC, Branch), Conversation → Integration Depth (UG, INSURICA, Johnson).
- **Ryan's wireframes**: 4-screen retail agency + 2 new screens for wholesaler. Wholesaler = configuration of same platform, not a separate product.
- **What exists in code**: Intake Manager (most mature — Submission/Quote/Parameter/Workflow/FormSchema/ThreadEvent), GIC Email Intelligence (Email/Submission/SituationAssessment/Draft/Extraction/Carrier/Agent), bot-service/copilot, platform-v2, EventGuard.
- **Critical gap**: Intake Manager and GIC Email Intelligence model Submission differently — unifying is first engineering task.
- **What does NOT exist in code**: Policy, Coverage, Product, Premium, Commission, Claim, Endorsement, Certificate, Binder, Insured/Risk, DelegatedAuthority, License, Payment, Invoice, Reserve, Rating — "essentially the entire post-bind world and the financial layer."
- **Domain model research**: 22 entities → 70 entities across 9 sub-domains after pressure-testing from 5 angles.

## Architectural Decisions

- **AI agents are a CHANNEL, not a separate system** — foundational.
- **Object-oriented system modeling insurance business**.
- **CLI-first everything**: CLI stands up customer, deploys associates, configures products, runs evaluations.
- **Three tiers of platform usage**: Managed service / Self-service workflows / Build on the platform.
- **5 universal findings**:
  1. Separate platform from domain
  2. Policy lifecycle is backbone
  3. Configuration ≠ transactions
  4. "Customer" is wrong — real entities are Insured, RetailAgent, Agency, Carrier, DistributionPartner
  5. Financial layer is severely underdeveloped.
- **Not a migration — a new platform built alongside the current system.**

## Layer/Location Specified

- **Ryan's layered architecture** — conceptual, not code-level:
  - L1 Runtime infra (LLM/Voice/Channels/VectorDB) → kernel + external services
  - L2 Integration (Carrier APIs, AMS, Web operators, Payments) → `kernel/integration/` + adapters
  - L3 Insurance Domain (knowledge + capabilities + workflows) → per-org config + skills + entity definitions
  - L4 Application (Admin, HITL, Analytics, Templates) → base UI
- **Current system**: bot-service + copilot-server + platform-v2 + voice-service + conversation-service — separate repos.
- **New OS (platform)**: one repo (`indemn-os`) — modular monolith.

**Finding 0 relevance**: "AI agents are a CHANNEL into the insurance platform, not a separate system." This architectural framing requires agents to be CLIENTS of the platform, accessing it through the platform's surface — which is exactly the harness pattern. Agents embedded in the kernel violate this "agents are clients" principle.

## Dependencies Declared

- Current codebases (bot-service, copilot, platform-v2, voice-service, conversation-service)
- Intake Manager (most mature domain model — 4-5 sprints of Dhruv's work)
- GIC Email Intelligence (Craig's model)
- MongoDB (per-repo databases)
- Railway (current deployments)
- Ryan's taxonomy document
- Kyle's Technology Systems Map (18 systems)

## Code Locations Specified

- Intake Manager: Dhruv's work; ~7 entities (Submission, Quote, Parameter, Workflow, FormSchema, ThreadEvent, SubmissionState)
- GIC Email Intelligence: Craig's work; ~6 entities (Email, Submission, SituationAssessment, Draft, Extraction, Carrier, Agent)
- Bot-service/Copilot: Conversations, agent configs, knowledge bases, organizations
- Platform V2: Agents, Templates, TestSets, Rubrics, Evaluations
- EventGuard: Quote records, Stripe, landing pages
- **New OS**: `indemn-os` repo (this project)

## Cross-References

- Ryan's wireframes (GIC Email Intelligence repo)
- Kyle's Indemn Technology Systems Map (Google Doc)
- Engineering Priorities Landscape document
- Domain model research (5-angle pressure test)
- Intake Manager codebase
- GIC Email Intelligence codebase
- Later feeds: white paper, realtime-architecture-design, all design artifacts

## Open Questions or Ambiguities

- **Status of Intake Manager vs GIC Submission unification** — open at time of writing, addressed by the new OS's generic entity framework.
- **22 entities → 70 entities**: domain model research flagged as DRAFT, needs review for redundancies. Status at time of writing: "should be validated with Ryan and Dhruv during stakeholder engagement."
- **Three tiers of platform usage** — MVP doesn't ship all three; Tier 2 is primary per gap sessions.

**Supersedence note**:
- "AI agents are a CHANNEL" thesis SURVIVES.
- "5 core concepts" map to later primitives: Domain Objects → Entity, Capabilities → entity methods, Workflow Templates → Skills, Channels → entry points, Customer Configuration → rules + lookups.
- 70-entity domain catalog NOT directly in kernel (kernel has 7 kernel entities; domain entities are per-org data).
- "Not a migration — new platform alongside current" SURVIVES.
- Post-bind / financial gap (policy/commission/claim/payment) — still not in kernel; to be implemented as per-org domain entities when customers need them.
