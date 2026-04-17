# Notes: 2026-03-25-domain-model-v2.md

**File:** projects/product-vision/artifacts/2026-03-25-domain-model-v2.md
**Read:** 2026-04-16 (full file — 479 lines; DDD classification of 70 proposed entities)
**Category:** design-source (early — domain modeling)

## Key Claims

- 70 proposed items classified via DDD: 44 Aggregate Roots + 18 Children + 9 Value Objects + 5 Reference Tables; 7 dropped.
- Aggregate roots get schema, state machine, API, CLI. Children accessed via parent. Value objects embedded. Reference tables read-only.
- 8 key architectural decisions:
  1. Party Model (base Contact/Party + role extensions)
  2. PolicyTransaction absorbs all policy changes (endorsements/renewals/cancellations as types)
  3. Configuration ≠ transactions pattern
  4. Three-layer communication: Email/Interaction/Correspondence
  5. Workflow Definition/Execution split
  6. Domain events immutable (RatingTransaction, UnderwritingDecision, SituationAssessment)
  7. FormSchema placement (Product or Platform)
  8. Underwriter is user role, not domain entity

## Architectural Decisions

- Every aggregate root → own schema, state machine, API, CLI. This becomes the "entity auto-generation" concept in later designs.
- Configuration vs transaction pattern — pervasive decision.
- ParameterAudit dropped as domain entity; acknowledged as "cross-cutting audit infrastructure (event store), not domain entity." This foreshadows the changes collection + OTEL in the final architecture.
- 3-phase build mapping (Foundation → Middle Market → Carrier Grade).
- Phase 1: ~25 total things (entities + children + reference tables).

## Layer/Location Specified

- **Platform layer vs Insurance domain separation** — same split as earlier domain-model-research.
- Platform entities: Associate, Skill, Workflow, Template, KnowledgeBase, Organization, Task, Document, Interaction, BotConfiguration.
- Insurance entities: Product, Insured, RetailAgent, Agency, Carrier, DistributionPartner, Submission, Quote, Policy, Coverage, Claim, etc.
- No process/image/layer placement claims yet.

Superseded by later:
- 2026-04-08-primitives-resolved.md — distills down to 6 primitives
- 2026-04-09-data-architecture-everything-is-data.md — makes domain = data
- White paper — final state

## Dependencies Declared

- DDD (Domain-Driven Design) methodology
- ACORD standards (party model)
- ISO/NAIC (Line of Business, Class Code standards)

## Code Locations Specified

- None. Domain modeling artifact.

## Cross-References

- Successor: 2026-03-30-entity-system-and-generator.md (how to generate this)
- 2026-04-08-primitives-resolved.md (final 6 primitives)
- 2026-04-09-data-architecture-everything-is-data.md (this becomes data, not code)
- Draft status per file — pending validation with Ryan (domain) and Dhruv (technical).

## Open Questions or Ambiguities

- FormSchema location (Core Insurance or Platform) — later resolved: it's an entity definition field spec.
- DTC model (EventGuard) Application entity — later resolved via Interaction/Application pattern.
- "Can this be built?" — later resolved via entity framework (dynamic class generation from definitions).

**Exploratory domain modeling. No Finding 0-class deviation claims here — this is entity classification, not layer placement.**
