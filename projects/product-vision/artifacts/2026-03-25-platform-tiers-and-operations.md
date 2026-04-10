---
ask: "How does the OS work as a business — buying experience, three tiers, Tier 3 as development model, and operational transition?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-25-a
sources:
  - type: conversation
    description: "Craig and Claude working through the vision, 2026-03-25"
  - type: google-sheet
    ref: "1LhHA_PIz9zu8UvatUSIzeWBUvnjgvzAfFbfIfN6Gd9s"
    name: "Four Outcomes Product Matrix — pricing reference"
  - type: google-doc
    ref: "1PuAXuJCagVEHTBGdPwBwtbf155PzHXWtjArVz0EPOpk"
    name: "Package Options — Independent Agency"
---

# Platform Tiers and Operational Model

## The Buying Experience (indemn.ai)

The second version of the website is being built now. The flow:
1. Start from the outcome — "What are you looking to achieve?"
2. Identify who you are — Agency, Carrier, MGA, Distribution
3. Browse the catalog of associates that deliver that outcome
4. Purchase — self-service, no demo booking required for standard products
5. Configure — connect to your existing systems
6. Live

This is Cam and Kyle's product design, and it maps directly to the OS. The Four Outcomes are the entry point. The associate catalog is the product. The OS is what powers delivery.

## Three Tiers

### Tier 1 — Out of the Box
**Buy from the website. Live immediately. Minimal Indemn involvement.**

- Customer selects outcome and associate(s) from the catalog
- Pricing per Cam's matrix (monthly subscription + implementation fee where needed)
- Configuration is mostly self-service — connect email, phone, set business rules
- Some light configuration help from Indemn
- Maps to Kyle's middle market machine: AEs land, FDEs configure (minimal), CS expands

**Who it serves:** Mid-market retail agencies, smaller MGAs, agencies wanting to digitize specific workflows. $15K-$40K ARR.

**What the OS enables:** Every out-of-box product is pre-configured on the OS. The customer isn't building anything — they're activating existing applications. Like installing an app on your phone.

### Tier 2 — Configured With Help
**Indemn (or AI agents) configure the customer's business on the OS. FDEs handle integration.**

- More complex needs — multiple associates, deep system integration, custom workflows
- Forward-deployed engineers help with: web operators for legacy systems, AMS connections, carrier API hookups, custom workflow configuration
- Implementation fee covers custom integration work
- Maps to Kyle's enterprise tier: custom architecture, direct attention

**Who it serves:** Larger MGAs, carriers launching products, enterprises with complex operations. $40K-$250K+ ARR.

**What the OS enables:** The same primitives as Tier 1, but configured more deeply. FDEs use the CLI and APIs to set up complex configurations. Integration work connects the OS to external systems.

### Tier 3 — Platform / Developer
**Sign up on the website. Get CLI and API access. Build your own insurance products.**

- No demo booking required — self-service signup
- Full CLI access, API documentation, developer portal
- Build your own agents, define your own workflows, create entirely new insurance products
- What you build deploys and runs ON the Indemn platform (PaaS model)
- Pricing: API/usage-based (Craig's domain — needs further design)
- Maps to Kyle's product partnerships tier: build on the platform

**Who it serves:** Tech-savvy insurance companies, insurtechs, developers in the insurance space. Variable ARR based on usage.

**What the OS enables:** The full power of the OS exposed as primitives. Same tools Indemn uses internally to build everything.

## Tier 3 Is the Development Model

This is the key insight: **Indemn uses Tier 3 to build everything.**

Every associate in the catalog, every workflow, every product configuration — all built using the same CLI and API that Tier 3 customers get access to. The development workflow:

1. **Build the OS** — domain model, entities, APIs, CLI (the infrastructure)
2. **Use the OS via Tier 3 tooling** — CLI/API to build associates, workflows, products
3. **Package for Tier 1** — pre-configured, buy on the website
4. **Package for Tier 2** — configurable with FDE assistance
5. **Offer Tier 3 access** — customers get the same tools

Indemn is the first and most demanding customer of the platform. The proof that Tier 3 works is that Indemn built the entire product catalog using it.

### The Claude Code Analogy
Think about it like Claude Code:
- Claude Code gives you primitives to build anything
- The product you build is yours
- The underlying harness and primitives power it

The Indemn OS is similar, but with a hosting dimension:
- The OS gives you primitives to build insurance products
- What you build deploys and runs ON the Indemn platform
- Indemn hosts, runs, and maintains the infrastructure
- It's a PaaS — Platform as a Service for insurance

### What Tier 3 Means for the Product
- **Developer portal** on indemn.ai with documentation, API reference, CLI download
- **Self-service signup** — no sales conversation needed
- **Usage-based pricing** — per API call, per entity, per agent deployed (needs design)
- **Build anything insurance-related** — agents, workflows, integrations, products
- **Deploy to the platform** — Indemn runs it, monitors it, scales it

This is where the OS-as-infrastructure play becomes real. And it's the piece that could change the company's trajectory from "insurance AI vendor" to "insurance infrastructure provider."

## Operational Transition

### Current State
- 15 people serving 18 bespoke customers
- Every customer has custom engineering
- Team is capacity-constrained

### Who Builds the OS
- **Craig** — Primary architect and builder, working with AI (Claude Code, the OS dispatch system)
- One architect with AI assistance building the foundation
- This is itself a proof point: AI-powered development on well-designed primitives scales beyond traditional engineering

### Who Keeps the Lights On
- **Dhruv** — Maintains production systems, current customer operations
- **Rudra** — Integration maintenance, carrier APIs
- **Rest of the team** — Current customer support, sales, operations
- The whole team keeps current customers running while Craig builds the OS

### The Transition
- OS, once developed, should be largely self-sustaining
- May need to hire a few people or reallocate team members for OS maintenance
- Current customers stay on current systems — no disruption
- New customers go on the OS
- Existing customers migrate over time (not a priority)
- Team gradually transitions from bespoke work to OS work

### What the Roadmap Needs to Account For
1. **Implementation work** — What's actually required to build each phase of the OS
2. **Rollout** — How the OS gets deployed and made available (website, developer portal, etc.)
3. **Maintenance** — Ongoing operational cost of running the OS at scale
4. **New customer onboarding** — The process for each tier (self-service → configured → developer)
5. **Current customer management** — How existing relationships are maintained during transition
6. **Hiring** — What additional people are needed and when
7. **Team restructuring** — How roles evolve as the company shifts from services to platform

### Future Team Structure (tentative)
- **OS Core Team** — Builds and maintains the domain model, APIs, CLI (Craig → eventually more engineers)
- **Applications Team** — Builds associates, workflows, integrations on the OS (uses Tier 3 tooling)
- **Deployment/FDE Team** — Configures customers, handles integration (Tier 2 work)
- **Current Operations** — Maintains existing customer systems during transition
- **Sales/GTM** — Sells from the catalog, manages customer relationships

The $10M from Series A funds: OS completion, team expansion, first wave of OS customers, and the transition from services to platform.
