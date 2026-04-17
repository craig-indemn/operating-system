# Notes: 2026-03-25-session-notes.md

**File:** projects/product-vision/artifacts/2026-03-25-session-notes.md
**Read:** 2026-04-16 (full file — 110 lines)
**Category:** design-source (session emotional/political context, not architectural)

## Key Claims

- Meta-document capturing session context not in formal artifacts.
- Records Craig's correction: "the vision is not just fucking entities" — the domain model is the engine, not the car.
- Insurance lab concept emerged: cohort of 5 insurance companies digitized on platform.
- Not a migration — something new built in parallel. "We're building something sort of on the side here."
- CLI as universal control plane — used by internal devs AND customers.
- Delivery channels (websites, embedded widgets, venue-specific pages) are first-class — part of Distribution & Delivery sub-domain.
- Stakeholder political context: Ganesh, Dhruv (linchpin), Cam's concerns, Kyle's priorities.

## Architectural Decisions

- **CLI is universal control plane** — Craig: "With the click of a button, theoretically, or a few buttons, you could set up an end-to-end insurance business. All through the CLI, we as a team and the customers themselves could use our CLI and automate everything."
- **Not a migration** — new platform, built alongside existing; existing customers migrate over time or stay.
- **OS as engine that builds OS** — "the engine actually implementing the work from beginning to end."

## Layer/Location Specified

- None. Session notes document intent and context, not code placement.

## Dependencies Declared

- None (meta-document).

## Code Locations Specified

- None.

## Cross-References

- All subsequent artifacts build on this session.

## Open Questions or Ambiguities

- Associate mechanics refinement deferred ("still work to refine the associates and how those play into everything else")
- Stakeholder political strategy

**No architectural-layer claims. No Finding 0-class concerns.**
