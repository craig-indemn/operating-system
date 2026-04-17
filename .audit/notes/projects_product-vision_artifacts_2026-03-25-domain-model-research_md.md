# Notes: 2026-03-25-domain-model-research.md

**File:** projects/product-vision/artifacts/2026-03-25-domain-model-research.md
**Read:** 2026-04-16 (full file — 111 lines)
**Category:** design-source (early)

## Key Claims

- Starting point: 22 proposed entities. 5 parallel validators expanded to ~70 entities across 9 sub-domains.
- 5 universal validator findings:
  1. **Separate platform from domain** — Workflow/Template/Skill/KnowledgeBase are platform infrastructure; insurance-recognizable domain is separate.
  2. Policy lifecycle is the backbone (Application → Submission → Quote → Binder → Policy → Endorsement → Renewal → Cancellation).
  3. Configuration ≠ transactions (CommissionSchedule vs CommissionTransaction).
  4. "Customer" is wrong abstraction — real: Insured, RetailAgent, Agency, Carrier, DistributionPartner.
  5. Financial layer severely underdeveloped.
- 9 sub-domains: Core Insurance, Risk & Parties, Submission & Quoting, Policy Lifecycle, Claims, Financial, Authority & Compliance, Distribution & Delivery, Platform Layer.
- Top 7 domain objects (51%+ associate frequency): Policy, Customer/Insured, Coverage, Carrier, Document, Agent, LOB.
- Top 6 capabilities: Generate, Validate, Search, Route, Classify, Extract.
- 3-phase build: MVP (simplified core) → middle-market (financial) → carrier-grade (authority/compliance/claims).
- Hardest problem: unifying IM + GIC Submission models.

## Architectural Decisions

- **Platform vs Domain separation** — this is where the "everything is data" decision originates. Platform layer (Associate, Skill, Workflow, Rule, Template, KnowledgeBase, Channel, Organization, Task, Interaction, Correspondence, Document, Email, Draft, ParameterAudit) vs. insurance-specific entities.
- Phasing: don't need all 70 entities on day one.
- **Incremental expansion through sub-domains** — each adds its own schemas/APIs/CLI without restructuring.
- **Platform Layer is infrastructure**, separate from domain (recognizable to insurance people).

## Layer/Location Specified

- "Platform layer" (Associate, Skill, Workflow, Rule, Template, KnowledgeBase, Channel, Organization, Project, Task, Interaction, Correspondence, Document, Email, Draft, ParameterAudit) — these are what would later become the kernel (+ kernel entities + domain entities).
- "Domain layer" — insurance entities — would be defined per-org via CLI.
- No process/image placement claims yet.

Later resolved: 
- Platform layer → kernel + kernel entities (six primitives resolved in 2026-04-08-primitives-resolved.md)
- Domain layer → entity definitions as data in MongoDB (2026-04-09-data-architecture-everything-is-data.md)

## Dependencies Declared

- Intake Manager, GIC Email Intelligence, bot-service, copilot-server, platform-v2, conversation-service (existing codebases for reference)

## Code Locations Specified

- References existing code entities (Submission in IM + GIC, Quote, Carrier, Agent, Email, Draft, SituationAssessment, FormSchema, Workflow in IM, Organization/Distribution/BotConfiguration/KnowledgeBase/Interaction/Lead in copilot-server).
- No new code paths prescribed.

## Cross-References

- Successor: 2026-03-25-domain-model-v2.md (refined model)
- 2026-03-24-associate-domain-mapping.md (same frequency analysis)
- Later: 2026-04-08-primitives-resolved.md (distills to 6 primitives)
- Later: 2026-04-09-data-architecture-everything-is-data.md (makes domain = data)

## Open Questions or Ambiguities

- Exact final primitive count — resolved to 6 (2026-04-08)
- How to unify IM + GIC Submission models — resolved: both become domain entity definitions stored as data per-org.
- What counts as "platform" vs "domain" — resolved: domain is per-org data; platform is kernel code + kernel entities.

**Early exploratory artifact. No Finding 0-class deviations introduced here — this is domain analysis, not layer placement.**
