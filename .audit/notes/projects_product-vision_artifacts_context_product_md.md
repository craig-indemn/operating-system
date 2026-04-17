# Notes: context/product.md

**File:** projects/product-vision/artifacts/context/product.md
**Read:** 2026-04-16 (full file — 186 lines)
**Category:** stakeholder-context

## Key Claims

- **Four Outcomes Framework (Cam's)**:
  1. Revenue Growth — unlock capacity to capture missed revenue (lead with this)
  2. Operational Efficiency — liberate staff from admin drudgery
  3. Client Retention — protect the book + maximize LTV
  4. Strategic Control — visibility, agility, governance
- **Language rules**: "Associate" not "chatbot". "Engine" not "tool". "Revenue Capacity" not "cost savings". "Partner" not "vendor".
- **Four Engines map to outcomes**:
  - Revenue Engine (priority) — 24/7 quoting/binding, eligibility triage, agent portal
  - Efficiency Engine — service automation, underwriting guardrails, knowledge search
  - Retention Engine — silent churn defender, cross-sell, lapse prevention
  - Control Engine — no-code (Strategy Studio), distribution analytics, audit trails
- **All four engines share ONE brain** — train once, deploy across use cases.
- **Pricing Matrix (48 Associates)** across 3 target groups:
  - Agencies (14), Carriers (14), Distribution/MGAs (20), In Development (8).
  - All 48 marked "Live" (sellable even if engineering isn't fully built).
- **~25 unique associate names** across the matrix.
- **Associate-to-domain mapping** (from research):
  - 7 domain objects in 51%+ of associates: Policy 84%, Customer/Insured 69%, Coverage 67%, Carrier 65%, Document 64%, Agent 60%, LOB 51%.
  - 6 capabilities most reused: Generate 78%, Validate 44%, Search 40%, Route 40%, Classify 40%, Extract 38%.
  - **7 entities + 6 capabilities = 84% of the pricing matrix.**
  - 7 natural groups: Intake/Triage, Knowledge/Answer, Outreach/Retention, Quoting/Binding, Email Processing, Configuration, Compliance.
- **Three target groups (Agencies, Carriers, Distribution) are configurations of SAME platform**, not separate architectures.
- **Customer Segments**:
  - P1: Mid-Market MGAs & Program Admins — "the sweet spot." $40K-$100K ARR, 2-4 mo cycle. Revenue Engine primary.
  - P2: Mid-Market Retail Agencies — $15K-$40K ARR, 1-2 mo cycle. Efficiency Engine primary. Constraint: no custom builds under $50M revenue.
  - P3: Insurance Carriers — $100K-$250K+ ARR, 6-18 mo cycle. Efficiency + Revenue.
  - P4: Strategic Partners (AMS, PAS, Insurtechs) — embed as Engagement Layer.
- **Agency packaging**: Starter $2K/mo → Growth $3.5K/mo → Professional $5.5K/mo → Enterprise $8K+/mo. $0 upfront. 90-day trial. Month-to-month.
- **7 product showcases live** on blog.indemn.ai (Document Retrieval, Quote & Bind, Conversational Intake, Email Intelligence, Intake Manager, Cross-Sell, CLI & MCP Server).
- **Craig's key insight**: "Associates are not 48 different products. They are 48 configurations of the same underlying agent system. Each associate is a configured composition of capabilities operating on domain objects through channels."

## Architectural Decisions

- **Platform is ONE system, configured per customer/persona**. Agencies/Carriers/Distribution are configurations, not separate architectures.
- **All engines share ONE brain** (knowledge base) → kernel's skill + capability model.
- **Associates = configured compositions** → per-org configuration in rules + lookups + skills.
- **7 domain objects + 6 capabilities = 84% of pricing matrix** → if kernel supports these 7 + 6, most of the product matrix is buildable.
- **Workflow templates** = composed capability sequences = skills that orchestrate CLI invocations.

## Layer/Location Specified

- No specific layer/location claims. Product strategy.
- Implicit: the OS kernel's entity framework + capability library + skill model must support the 7 canonical domain objects and 6 reused capabilities.

**Finding 0 relevance**: Reinforces that associates are CONFIGURED on the platform, not embedded in it. "48 configurations of the same underlying agent system" → the agent system runs outside the kernel's configuration space; it runs in harnesses that CONSUME configuration and execute against the platform. This aligns with the harness pattern. Current implementation (agent in kernel) violates this "associates are configured, not coded" principle.

## Dependencies Declared

- Four Outcomes framework (Cam)
- Pricing Matrix (Ian's Google Sheet)
- Landing pages / showcases (blog.indemn.ai)
- Package tiers (Starter/Growth/Pro/Enterprise)
- AMS integrations + carrier APIs (future adapters)

## Code Locations Specified

- Product showcases at `blog.indemn.ai/{page-slug}` — 7 live pages.
- Associate configurations — to be stored in MongoDB per-org (per the data architecture).
- Skills — markdown in MongoDB per-org.

## Cross-References

- Four Outcomes Product Matrix Google Sheet (Ian, Cam)
- Series A source docs (associate-suite, four-outcomes-framework, customer-segments, four-outcomes-product-strategy)
- Package Options Google Doc
- 2026-03-24-associate-domain-mapping.md (the research)
- white paper Section 4 (Tier definitions align with customer segments P1-P3)

## Open Questions or Ambiguities

- **Associate names canonicalization** — ~25 unique names across the matrix, but configurations vary per target group.
- **"In Development" items (8)** — some overlap with existing associate names, some net-new. Roadmap items.
- **Packaging tiers vs. pricing matrix line items** — the packaging tiers map loosely to associate bundles; exact per-tier associate set TBD.

**Supersedence note**:
- Product strategy is CURRENT. The OS kernel must support the 7 domain objects + 6 capabilities as per-org configurable entities/methods.
- "Associates are configurations, not products" SURVIVES as architectural principle.
- The OS's success = supporting the 48-associate matrix via 7 domain objects + 6 capabilities + per-org config.
