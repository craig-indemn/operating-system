# Notes: 2026-03-25-why-insurance-why-now.md

**File:** projects/product-vision/artifacts/2026-03-25-why-insurance-why-now.md
**Read:** 2026-04-16 (full file — 149 lines)
**Category:** design-source (business rationale, not architecture)

## Key Claims

- Market framing: $5T global insurance market on fragmented legacy (AMS/PAS/rating/etc.).
- Existing insurtech (Vertafore, Applied, Duck Creek, Guidewire) = point solutions with AI bolted on.
- Indemn's structural advantage: started AI-native with EventGuard, domain model is AI-designed from day one.
- Intelligence flywheel: more customers → more data → better outcomes → more customers.
- **Moat is the data**, not just code.
- Automation spectrum: Fully Automated (EventGuard) / Human-in-the-Loop (intake, renewals, claims, drafts) / Human-Directed (complex commercial, enterprise accounts, regulatory).
- "Insurance is people-centric" — OS upgrades workforce, doesn't replace.

## Architectural Decisions

- **AI-native from day one** — "Every entity has a CLI. Every operation is agent-accessible."
- **Not AI as feature on legacy systems** — AI as foundation, insurance modeled around it.
- **Automation spectrum supported structurally** — platform must support fully-automated, HITL, and human-directed flows.

## Layer/Location Specified

- No code paths or process placement.
- Platform-level business framing only.

## Dependencies Declared

- None (business document).

## Code Locations Specified

- None.

## Cross-References

- Competitive landscape (Vertafore, Applied Systems, Duck Creek, Guidewire)
- Kyle's constraint-removal thesis
- EventGuard (proof of concept)

## Open Questions or Ambiguities

- None architecturally.

**Business rationale document. No Finding 0-class concerns. Establishes the "every entity has CLI, every operation is agent-accessible" principle that later becomes the auto-generation design.**
