# Notes: 2026-04-07-challenge-insurance-practitioner.md

**File:** projects/product-vision/artifacts/2026-04-07-challenge-insurance-practitioner.md
**Read:** 2026-04-16 (JSON transcript — 23 lines; very long agent response, sampled)
**Category:** design-pressure-test

## Key Claims

Pressure test by "20-year insurance operations professional" persona. Focus: does this understand real insurance? The agent's response enumerates insurance-domain complexity the 44-entity model may underestimate:

- **Workflow complexity**: rerigs, binders extended 5+ times, multi-location policies, surplus lines with per-state rules, split placements across carriers, agency bill vs. direct bill, certificate holder endorsements, cancellation-reinstatement cycles.
- **Missing from entity model**: producer codes, agency codes, sub-producer appointments, MGA hierarchies, binding authority schemas, carrier appetite guidelines, quote expirations, renewal diary triggers, expense/commission splits, suspense items.
- **Per-org routing not sufficient**: agencies doing "the same thing" often need fundamentally different behavior — different state regulations, different carrier contracts, different compliance regimes.
- **Complex party/role relationships**: person can be a producer at agency A and a retail customer at agency B; carriers have underwriters who also have authority limits; agents can be sub-producers of MGAs.
- **Tests for "does this understand my business"**: cancellation-reinstatement lifecycle, policy change (endorsement) without creating new policy, back-dated effective dates for surplus lines, managing the 31-day-follow-up rule.

## Architectural Decisions

The response's architectural implications (inferred from the prompt + pressure test category):
- **Insurance domain is deep**. Platform must support per-carrier/per-state/per-product rules without coding each specially.
- **Party/Role model** needs to support many-to-many with roles varying by context (producer for one carrier, retail customer for another).
- **Entity state machines must allow re-entry / retry** (cancellation→reinstatement, quote→expired→re-quoted).
- **Compliance audit trail** is not optional — every change needs who, when, why, old-value, new-value.
- **The kernel-vs-domain separation** (later formalized) is the right answer: insurance-specific rules go in per-org configuration, not kernel code.

## Layer/Location Specified

- No specific layer claims. The pressure test is about DOMAIN complexity; the architectural response is that:
  - **Kernel stays domain-agnostic** (no hardcoded insurance concepts).
  - **Insurance complexity lives in entity definitions + rules + lookups + skills** (per-org data).
  - **Party/Role model** must be flexible enough that the same person can play different roles in different contexts (later implemented as Actor + Role with permissions + watches; external parties are domain entities not kernel actors).

**Finding 0 relevance**: This pressure test does not directly address agent execution location. However, the insurance domain complexity it enumerates is EXACTLY why the harness pattern matters:
- Insurance agents need to reason about complex state (binders extended multiple times, endorsements, split placements).
- These reasoning paths require deepagents middleware (todo lists, subagents, filesystem, HITL) — the kernel's simplified `_execute_reasoning` loop doesn't support this.
- The harness pattern enables full deepagents + Daytona sandbox, which is what the insurance domain demands.

## Dependencies Declared

- Referenced existing insurance platforms: Applied Epic, Vertafore, Duck Creek, Guidewire (state of the art comparison).
- Implied: carrier APIs, state DOI systems, AMS platforms.

## Code Locations Specified

- No paths. Domain complexity discussion.
- The response likely enumerates specific entity types / fields / state machines that should exist in the MVP.

## Cross-References

- Project vision: domain-model-research, domain-model-v2, associate-architecture (early framing)
- Feeds into: pressure-test-findings (synthesis), white paper (kernel-vs-domain split)
- Later directly tested: GIC retrace (B2B), EventGuard retrace (consumer), CRM retrace (generic)

## Open Questions or Ambiguities

- **How much insurance domain sits in the kernel vs. per-org data** — RESOLVED: zero insurance in kernel. All per-org.
- **How to support N-level MGA/agent hierarchies** — per-org domain entities (Agency, Agent, Producer) with relationships and access control.
- **How to handle state-specific compliance regimes** — per-org rules + lookups + required-field rules.

**Supersedence note**:
- The insurance domain concerns ARE addressed by the final architecture:
  - Domain-agnostic kernel means all insurance specifics are per-org data.
  - Flexible entity framework (EntityDefinition in MongoDB) means per-customer entity schemas.
  - Rules + Lookups + Required-field rules allow per-state / per-product configuration.
- But Finding 0 (agent execution in kernel) MEANS the agent reasoning capacity is limited — a 20-iteration LLM loop cannot handle the cascades of insurance edge cases this pressure test lists (rerig → extended binder → carrier change → retroactive endorsement).
- Full deepagents in harness (per design) is needed to handle these workflows; current implementation doesn't support that.
