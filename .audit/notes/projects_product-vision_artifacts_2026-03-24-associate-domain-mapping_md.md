# Notes: 2026-03-24-associate-domain-mapping.md

**File:** projects/product-vision/artifacts/2026-03-24-associate-domain-mapping.md
**Read:** 2026-04-16 (full file — ~970 lines; catalog of 48 associates + structural analysis)
**Category:** design-source (earliest — session 1)

## Key Claims

- Complete mapping of 48 associates from Cam's Four Outcomes Product Matrix to domain objects, capabilities, channels.
- Identifies Tier 1/2/3 domain objects by frequency across associates.
- Identifies Tier 1/2/3 capabilities by frequency.
- Seven structural findings:
  1. Policy-Coverage-Carrier triangle is the irreducible core.
  2. Document is polymorphic (needs type system, not flat table).
  3. Knowledge layer is cross-cutting (shared corpus, multiple consumers).
  4. Two workflow patterns: reactive (classify → search → generate → route) vs proactive (monitor → trigger → generate → log).
  5. AuditLog is infrastructure, not optional — "every consequential action must be logged."
  6. Associates cluster by capability profile (intake/triage, knowledge/answer, outreach/retention, quoting/binding, email processing, configuration, compliance).
  7. Three target groups (Agencies, Carriers, Distribution) are configurations of same platform, not separate architectures.

## Architectural Decisions

- **Domain model must support Tier 1 objects**: Policy, Customer, Coverage, Carrier, Document, Agent, LOB. These are universal (>50% of associates).
- **Tier 2 (must-model)**: Task, Rule, AuditLog, Submission, KnowledgeBase, Quote, Message, Conversation.
- **Capabilities** treated as first-class (Generate, Search, Validate, Route, Classify, Extract, Score, Notify, Draft, Recommend, Monitor, Quote, Triage, Schedule, Transform, Verify, Aggregate, Bind, Enforce, Enrich).
- **Platform is one system, three configurations** — Agencies/Carriers/Distribution share domain objects + capabilities; differences are in primacy, channel, and rules.
- **Workflow engine must support both reactive and proactive patterns** — event-driven triggers + request-response.
- **AuditLog is automatic infrastructure**, not per-associate implementation.
- **Knowledge layer is segmentable by audience** (internal, agents, consumers).

## Layer/Location Specified

- **This artifact is early-session domain mapping.** It does NOT specify kernel/harness/code paths.
- Key constraint it establishes: the platform must model ~20 domain objects generically; each associate is a composition of domain reads/writes + capabilities.
- The seven structural findings inform later artifacts — especially:
  - "AuditLog is infrastructure" → kernel-provided changes collection (appears in white paper).
  - "Two workflow patterns" → watches (reactive) + scheduled triggers (proactive).
  - "Knowledge layer is cross-cutting" → skills + KnowledgeBase as entity.
  - "Three target groups are configurations" → "environments are orgs" (data architecture).

Not specified: how these domain objects are stored, where the capabilities live, what process hosts them. Those resolutions come later (primitives-resolved, entity-framework, etc.).

## Dependencies Declared

- Cam's Four Outcomes Product Matrix (Google Sheet)
- Associate Suite docs
- Craig's Vision doc (context/craigs-vision.md)

## Code Locations Specified

None. Earliest-session artifact — no code paths prescribed.

## Cross-References

- `context/craigs-vision.md` — source for "the underlying system" thesis
- Will be referenced by later domain-model-research and domain-model-v2 artifacts
- Informs entity-framework design (Layer 1) and associate-system design (Layer 3)

## Open Questions or Ambiguities

- Where do domain objects live (DB schema? code structure)?  — resolved in entity-framework (later)
- Where do capabilities live (kernel? domain?) — resolved as "kernel capabilities" in 2026-04-09-entity-capabilities-and-skill-model.md
- How do the 48 associates map to runtime images/processes — resolved in realtime-architecture-design (2026-04-10)
- How is the no-code configuration (Strategy Studio) implemented — deferred per later artifacts

**No Finding 0-class deviation concerns from this artifact.** It's domain catalog, not architectural-layer placement.
