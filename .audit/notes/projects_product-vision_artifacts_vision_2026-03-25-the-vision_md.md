# Notes: vision/2026-03-25-the-vision.md

**File:** projects/product-vision/artifacts/vision/2026-03-25-the-vision.md
**Read:** 2026-04-16 (full file — 268 lines)
**Category:** stakeholder-context (vision v2 — THE CANONICAL VISION)

## Key Claims

Vision v2 (March 25, same day as v1): "Building the Factory"

- **One-liner**: "We proved AI can run an insurance business. Now we're building the factory that lets us do it for anyone."
- **EventGuard = The Proof**: single product + carrier + team, hand-built. Became standalone business ($2.78M acquisition).
- **The Factory**: "The factory is the system that models those underlying operations once and lets us configure them for anyone."
- **Technology dimension completes Series A story**: Kyle + Cam articulate WHAT (four outcomes, revenue engines, 48 associates); the factory is HOW at scale. "Without it, we're a services company that builds custom solutions. With it, we're a platform company that configures them."
- **Four Outcomes**: Revenue Growth / Operational Efficiency / Client Retention / Strategic Control (Cam's framework).
- **Four Engines** map to outcomes (Revenue, Efficiency, Retention, Control).
- **All engines share ONE brain** — one knowledge base per customer.
- **Associates = 48 configurations of same underlying system.** 7 entities + 6 capabilities = 84% of pricing matrix.
- **Three target groups (Agencies, Carriers, Distribution) = configurations of same platform**, not separate architectures.
- **Object-Oriented Insurance System**: 9 sub-domains, schema/state-machine/API/CLI per entity, "so foundational that any situation can be modeled." 44 aggregate roots across 9 sub-domains.
- **Build incrementally**: Phase 1 ~25 things for current associates, Phase 2 financial + distribution for middle market, Phase 3 authority + compliance + claims for carrier-grade.
- **CLI-first, Agent-first** (same as v1).
- **Experience Layer**: Ryan's wireframes (Pipeline/Submission Queue, Customer Workspace/Risk Record, Line Workstream, Carrier Workstream). **"The wholesaler view is a CONFIGURATION of the same platform as the retail agency view."**
- **Delivery Channels as First-Class**: embedded AI on websites, venue pages, Outlook add-ins, voice on phones.
- **The Insurance Lab**: cohort of 5 companies (carrier/MGA/retail/program admin/wholesale broker). All configured on same platform.
- **R&D that informs the platform**: EventGuard (end-to-end), GIC Email (intelligence), Intake Manager (kernel), INSURICA (retention at scale), product showcases (capability demonstrations).
- **Starting materials** listed: Intake Manager + GIC + Mint + Evaluation Framework + CLI + OS.
- **What NOT doing**: migrate current system, replace copilot-dashboard, disrupt current delivery. Build alongside.
- **Team roles** (11 people).
- **Story**: "The only insurance-native domain model with AI agents that can transact, not just talk." Moat = the factory. "Wikipedia of insurance + AI."
- **Closing line**: "We built the lab. We proved AI can run insurance. Now we're building the factory. Bring us your business."

## Architectural Decisions

- **Factory metaphor for platform**: models operations once, configures per customer.
- **Configuration, not custom code**: 48 associates = configurations.
- **ONE platform for three target groups** (Agencies/Carriers/Distribution).
- **Incremental build**: 3-phase domain model (initial 25 entities → financial + distribution → authority + compliance + claims).

## Layer/Location Specified

- **9 sub-domains** (domain layer):
  - Core Insurance, Risk & Parties, Submission & Quoting, Policy Lifecycle, Claims, Financial, Authority & Compliance, Distribution & Delivery, Platform Layer
- **Experience Layer** = Ryan's wireframes.
- **Delivery Channels** = separate deployables (websites, landing pages, widgets, voice on phone systems).
- **Platform Layer** (sub-domain 9) = Associate, Skill, BotConfiguration, Workflow, Rule, Template, KnowledgeBase, Channel, Organization, Project, Task, Interaction, Correspondence, Document, Email, Draft, ParameterAudit.

**Finding 0 relevance**:
- "**Bring us your business, and AI will RUN it**." Run = transact, not just talk. Requires agents with tools. Finding 0b (assistant no tools) contradicts this.
- "**Delivery channels as first-class** (embedded AI on websites, venue pages)" — requires chat + voice harnesses. Finding 0 blocks this.
- "**Associates = 48 configurations of the same underlying system**" — requires a harness pattern where one system + config = many associates. Current code has agent loop embedded in kernel, not configuration-driven.

## Dependencies Declared

- Existing codebases (Intake Manager, GIC, Mint, Evaluation Framework, CLI, OS, product showcases)
- JM/EventGuard proof
- Cam's Four Outcomes + 48-associate matrix
- Ryan's wireframes + taxonomy
- Current customer implementations as R&D

## Code Locations Specified

- None (vision statement).
- Implicit paths for starting materials (Intake Manager in Dhruv's work, GIC Email in Craig's work, etc.)

## Cross-References

- Vision v1 (predecessor — lab framing vs. factory framing)
- white-paper (descendant — synthesizes vision + architecture + spec)
- All architecture artifacts (implement this vision)
- Four Outcomes Product Matrix
- Ryan's wireframes

## Open Questions or Ambiguities

- **How the factory actually works at the code level** — deferred to architecture sessions (3-6) and specs (4/14).
- **Roadmap phase details** — "*Detailed phased roadmap to be developed*" — done in white paper + consolidated specs.
- **Moat articulation** — still evolving.

**Supersedence note**:
- Vision v2 is the CANONICAL vision. V1 is earlier, similar content.
- Vision SURVIVES through all subsequent design — the white paper is the formalization.
- **Key claims load-bearing for Finding 0**: "AI can transact, not just talk"; "Delivery channels as first-class"; "Associates = configurations of same system"; "Object-oriented insurance system." All require the harness pattern as implemented per session 5 realtime-architecture-design. Kernel-embedded agent execution contradicts.
