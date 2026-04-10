---
ask: "Checkpoint of all vision thinking from session 2 — what's been established, what's still open?"
created: 2026-03-30
workstream: product-vision
session: 2026-03-30-a
sources:
  - type: conversation
    description: "Craig and Claude session 2, 2026-03-30 — continuing vision development"
---

# Vision Session 2 — Checkpoint

## What Changed Since Session 1

The core framing shifted from "Insurance Lab" / "Factory" to **"The Operating System for Insurance."** This isn't just a rebranding — it's a fundamentally different concept. A factory builds things and ships them out. An operating system is what everything runs ON. The insurance business lives in the system.

## Key Concepts Established This Session

### The OS for Insurance
- Not a tool, not a platform you plug into your stack — the operating system that the entire insurance business runs on
- Precise analogy: Hardware (carriers, regulations) → OS (Indemn's system) → Applications (associates, workflows) → Users (businesses, agents, consumers)
- You don't rebuild the OS for each customer. Applications run on the OS. The OS abstracts the complexity.
- The system is in the middle — any input (web, voice, email, text, forms, API, external systems) → OS processes everything → any output (documents, payments, communications, data sync, analytics)
- We're the electricity that powers the insurance business

### Why Insurance, Why Now
- $5T+ market on fragmented legacy systems — different AMS, PAS, rating engines, CRM, email, fax
- Aging workforce, rising customer expectations, compounding regulatory complexity
- Existing vendors (Vertafore, Applied, Duck Creek, Guidewire) are point solutions bolting AI onto legacy
- Nobody is building the OS from scratch because you can't get there incrementally — you have to start from the domain model up
- Indemn's structural advantage: started with AI running insurance (EventGuard), not legacy software adding AI
- The window is open NOW — AI agent capabilities have crossed the threshold, the industry pain is acute, nobody else has started from the right place

### The Intelligence Flywheel
- Every customer on the OS generates data that makes the OS smarter for everyone
- Submission patterns, quoting outcomes, policy lifecycle events, communication patterns all improve the system
- More customers → more data → better outcomes → more customers
- The first OS to reach critical mass of data wins permanently
- One dimension of the moat (alongside domain model, CLI, agent architecture, integrations)
- Series A urgency: capture the data advantage before anyone else builds an OS

### Distribution Chain Collapse
- Today: carrier creates product → files → distributes to agencies → agents sell manually → paper apps → manual underwriting → quote in weeks → policy issued days later
- On the OS: product modeled → instantly distributable → AI agents sell 24/7 → digital application → automated processing → quote in minutes → binding in real-time
- What collapses is TIME, not people
- Kyle's constraint removal thesis made concrete: access was the constraint, the OS removes it

### Automation Spectrum
- Not everything is the same level of automation
- **Fully automated**: Some things can be completely automated (like EventGuard — end-to-end, no human touch). Indemn should power these capabilities.
- **Human-in-the-loop**: Most workflows — AI prepares everything, human decides at critical points. 30 min of processing → 3 min of review.
- **Human-directed**: Complex judgment, relationships, strategy — OS provides better tools but the work is human expertise
- Insurance IS people-centric. Agents exist for good reasons — risk management, guidance, trust. The process around those people doesn't need to be convoluted and manual.
- The OS elevates the workforce, doesn't replace it. Removes 80% administrative drudgery, humans focus on the 20% that's actual expertise.
- There's a role for everyone in this new world. That role may change.

### Four Outcomes / Four Engines Connected to the OS
- Cam's Four Outcomes (Revenue Growth, Operational Efficiency, Client Retention, Strategic Control) are the customer-facing entry point — why they buy
- Four Engines (Revenue, Efficiency, Retention, Control) are the product groupings — how we deliver
- All four engines share a single brain — one knowledge base, train once, deploy everywhere
- The engines are the product packaging. The OS is what powers them all.
- The business story (Kyle, Cam) and the technology story (Craig) are the same story from two sides

### The Vision Completes the Series A Story
- Kyle and Cam have strong Series A materials — Four Outcomes, revenue engines, customer stories, constraint removal thesis
- They tell what Indemn DELIVERS but not the HOW that makes it infinitely scalable
- Craig's technology dimension is the missing piece: the OS that makes everything scale
- Without the OS: Indemn is a services company building custom solutions
- With the OS: Indemn is a platform company that configures them
- That's the difference between a $50M outcome and a billion-dollar one
- Craig pitches Kyle and Cam → they incorporate the technology story into Series A materials → investors get the complete picture

### Three Tiers (Emerged as Product Model, Not Artificial Separation)

**Tier 1 — Out of the Box:**
- indemn.ai → outcome → who are you → associate catalog → purchase → configure → live
- Self-service, no demo needed for standard products
- Pricing per Cam's matrix

**Tier 2 — Configured with Help:**
- Same OS, but customer needs integrations that don't exist yet
- FDEs help with: web operators for legacy portals, AMS connections, carrier API hookups
- Implementation fee for custom integration work

**Tier 3 — Developer / Platform:**
- Sign up on website, get CLI and API access, build your own insurance products
- Self-service signup, no booking needed
- PaaS model: build on the platform, deploy to the platform, Indemn runs it
- Usage/API-based pricing (needs design)

**Key insight:** The distinction between tiers isn't the OS — the OS handles everyone the same way. The distinction is whether the customer's setup requires integrations that already exist or new ones that need to be built. Over time, as the integration library grows, more customers become Tier 1.

### Tier 3 Is the Development Model
- Indemn uses Tier 3 to build EVERYTHING — every associate, every workflow, every product
- Indemn is the first and most demanding customer of the platform
- The proof that Tier 3 works: Indemn built the entire catalog using it
- Claude Code analogy: same primitives, but with hosting — build here, deploy here, we run it
- Jarvis (agent that builds agents) is already a prototype of Tier 3

### Associate Architecture
- Associates ARE deep agents — LangChain-based, with skills (like Claude Code skills), observable via LangFuse
- Evolution from current V2 agents: same harness, but now with the full OS domain model to operate on
- Today: agents have conversations. On the OS: associates execute insurance workflows using skills that call CLI/API on real domain objects
- Skills work exactly like Claude Code skills — documents that describe how to use CLI commands for specific tasks
- Evaluation framework extends: same rubrics/test sets mechanism, but with insurance-specific workflow evaluations (not just conversation quality — did the workflow produce the right outcome?)
- Architecture will be redesigned/modernized from current V2, but the principles carry forward

### Customer Onboarding = Configuration + Integration
- Configuration: create org, select carriers (from existing), select LOBs/products, set workflow rules, choose associates, deploy — should be self-service or wizard-guided
- Integration: connect email, phone, AMS, carrier portals — if standard integration exists, plug and play; if new integration needed, engineering work
- No "modeling" of carriers — carriers are entities that get populated on a need-to-know basis with a reusable framework
- Data population is itself a CLI/skill operation: `indemn carrier populate --name "Hartford" --source naic,ambest`
- Early customers help build the data layer. Mature customers find everything already there. That's the network effect.

### Operational Reality
- Craig is primarily building the OS, with AI (Claude Code, the OS dispatch system, 10+ parallel sessions)
- One architect with AI can build the foundation in 1-2 weeks — this is the whole point of the OS Craig built
- Rest of team (Dhruv, Rudra, others) keeps current customers running
- OS should be largely self-sustaining once developed
- By Series A close (~3 months), the OS is built, lab is running, testing on new customers
- This is a commitment, not an aspiration

### EventGuard's Role (Clarified)
- EventGuard is proof that the CONCEPT works — AI can run an end-to-end insurance business
- It was built as an MGA lab experiment, hand-built from scratch
- It does NOT currently map through the OS entities — it's a bespoke solution
- The OS is what lets us do EventGuard for anyone without starting from scratch
- All existing customer implementations (GIC, INSURICA, Union General) are R&D that informed the platform design
- The bespoke solutions don't fit cleanly into the new system, but the intuition is: any insurance solution can be built and run on the OS

## Late Session Additions (After Initial Checkpoint)

### CRM/AMS as Core OS Capability
- The OS IS a modern CRM and AMS — the domain model (Contact/Party, Organization, Policy, Submission, etc.) provides both CRM and AMS capabilities natively
- Kyle wants the team to use a CRM — the answer is dog-fooding the OS itself. Indemn is the first customer.
- The OS can replace a customer's AMS entirely, or integrate with their existing AMS as a bridge
- No open source AMS exists — this is a market opportunity. Indemn is building the first AI-native insurance management system.

### Build vs. Buy Decision
- Researched open source frameworks: Twenty CRM, ERPNext/Frappe, Odoo, SuiteCRM, NocoBase
- Decision: **build from scratch**. The insurance domain is too specialized for generic CRM frameworks. The CLI-first requirement demands full control. The value of frameworks is primarily UI (which Craig doesn't need) and generic entities (which are trivial to build).
- The valuable PATTERN from frameworks (define entity → auto-generate everything) should be built as the OS generator
- Use existing libraries and managed services for infrastructure (Amplify, Pinecone, Stripe, Twilio)
- Stay on **MongoDB** (not Postgres) — team already uses it everywhere, document model fits insurance's inherent field variability across product types

### Entity Generator as OS Kernel
- The generator is the most important thing to build — it's the kernel of the OS
- Input: declarative entity definition (schema, state machine, relationships, permissions)
- Output: database schema, REST API, CLI commands, auto-generated skill document, webhook events, permissions model
- Skills are auto-generated and serve THREE audiences: AI associates (interface), Tier 3 developers (documentation), Indemn engineers (reference)
- This is the Claude Code skill pattern applied to the entire platform
- Building the generator first is how you build 44 entities in 1-2 weeks

### Product Configuration vs. Custom Entities
- Users don't create new entities — the OS provides the complete domain model (44 entities)
- What varies between carriers/customers is CONFIGURATION, not entity structure
- Example: WC submission vs. GL submission = same Submission entity with different form schema, validation rules, and carrier-specific fields
- Product entity defines the template (form schema, validation rules, workflow rules). Submission/Quote/Policy entities have core fields + flexible data section populated per product configuration.
- Tier 3 custom entity creation is possible but the exception, not the norm. Like Salesforce custom objects — available but most needs are met by configuring standard entities.

### SMS as Channel
- Twilio (already used for voice) handles SMS
- SMS is just another channel type the OS routes through — same pattern as voice, email, web chat

## Artifacts Produced This Session

| Artifact | What It Captures |
|----------|-----------------|
| `vision/2026-03-25-the-vision.md` (v2) | Restructured vision doc — factory framing (stale — needs OS framing in final consolidation) |
| `vision/2026-03-25-the-vision-v1.md` | Original vision doc preserved |
| `2026-03-25-the-operating-system-for-insurance.md` | Core OS framing — system in the middle, trivial implementation, carriers as conduit, three tiers, convergence |
| `2026-03-25-why-insurance-why-now.md` | Industry context, intelligence flywheel, distribution chain collapse, automation spectrum, people-centric |
| `2026-03-25-platform-tiers-and-operations.md` | Three tiers detailed, Tier 3 as development model, buying experience, operational transition, team structure |
| `2026-03-25-associate-architecture.md` | How associates work technically — deep agents, skills, evaluations, connection to current systems |
| `2026-03-30-entity-system-and-generator.md` | Entity generator, build vs buy, skills as docs, CRM/AMS implications, product configuration |

## What's Still Open

### Vision — Substantially Complete, May Surface More During Design
- The core vision is established across 7 artifacts
- Design phase will likely surface additional vision-level questions that feed back
- Final vision document consolidation happens AFTER design thinking is complete

### Unresolved Vision Questions (Lower Priority)
- Tier 3 pricing model — API/usage-based, needs brainstorming
- How the new website (being built now by Dhruv and Drew) aligns with the OS vision
- Product showcases — need to be refined and aligned with the OS vision
- How current customers eventually transition to the OS (low priority but needs a stance)
- Competitive positioning beyond "legacy vendors can't get there"
- Revenue projections with the OS model vs. current model

### Next Phase: Design
Per Craig: vision → **design** → implementation → priorities → roles → time allocations → execution → roadmap

Vision is substantially complete. Moving to design — the actual architecture, technical decisions, and how the pieces get built. Design will likely surface additional vision refinements.

## How to Resume

1. Read this checkpoint FIRST — it's the comprehensive summary of all session 2 thinking
2. Read the 7 artifacts listed above for detailed thinking on each topic
3. Read the session 1 artifacts for foundation context:
   - `artifacts/2026-03-25-domain-model-v2.md` — 44 entities, DDD-classified
   - `artifacts/context/` — 5 context docs (business, product, architecture, strategy, Craig's vision)
   - `artifacts/2026-03-24-associate-domain-mapping.md` — 48 associates mapped to entities
   - `artifacts/2026-03-25-session-notes.md` — unreduced vibes from session 1
4. Pick up at **design phase** — architecture decisions, technical implementation, how to build the generator and entity system
5. Or if Craig has additional vision thoughts, address those first
