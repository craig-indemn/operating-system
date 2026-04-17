# Notes: 2026-03-25-platform-tiers-and-operations.md

**File:** projects/product-vision/artifacts/2026-03-25-platform-tiers-and-operations.md
**Read:** 2026-04-16 (full file — 149 lines)
**Category:** design-source (business/operational model, not code architecture)

## Key Claims

- Three tiers of customer engagement:
  - **Tier 1 (Out of the Box)**: Self-service, buy from website, pre-configured associates, $15K-$40K ARR (mid-market agencies, smaller MGAs)
  - **Tier 2 (Configured)**: FDEs configure customer's business on OS, custom integration work, $40K-$250K+ ARR (larger MGAs, carriers, enterprises)
  - **Tier 3 (Platform/Developer)**: Self-service signup, CLI + API access, build your own insurance products, usage-based pricing (tech-savvy insurers, insurtechs)
- **Tier 3 IS the development model** — Indemn uses Tier 3 tooling to build everything. "The proof that Tier 3 works is that Indemn built the entire product catalog using it."
- Claude Code analogy: OS provides primitives; customers build products; OS hosts and runs. PaaS for insurance.
- Current state: 15 people, 18 bespoke customers, capacity-constrained.
- Craig is primary architect/builder with AI assistance (Claude Code, OS dispatch system).
- Operational transition plan: OS built by Craig+AI; current team maintains legacy; new customers on OS; existing migrate over time.

## Architectural Decisions

- **Tier 3 is the primary development model** — internal Indemn devs + FDEs use the same CLI as external Tier 3 customers. This means the CLI must be complete and self-sufficient.
- **Self-service Tier 3 signup** — sign up on website, get CLI + API access, no sales call. Later formalized in auth design (2026-04-11) Tier 3 signup flow.
- **PaaS model** — Indemn hosts everything customers build; no "on-prem" deployment.
- **Usage-based Tier 3 pricing** (deferred design per artifact).
- Future team structure: OS Core, Applications, Deployment/FDE, Current Operations, Sales/GTM.

## Layer/Location Specified

- No code-layer or process-layer claims.
- Business/operational claims only.
- Tier 3 signup self-service → later becomes the auth-design Tier 3 signup flow.
- "What you build deploys and runs ON the Indemn platform" → implies hosted customer deployments. Later resolved: customer organizations run on the shared platform (multi-tenancy via Organization primitive + org-scoping).

## Dependencies Declared

- Cam's Four Outcomes Product Matrix
- Kyle/Cam Package Options
- Claude Code (analogy reference)

## Code Locations Specified

- None. Business/operational artifact.

## Cross-References

- Succeeded by: 2026-04-11-authentication-design.md (§ Tier 3 Self-Service Signup implements this)
- context/craigs-vision.md (vision thesis)
- context/business.md (business model)

## Open Questions or Ambiguities

- Tier 3 pricing model (per API call / per entity / per agent) — deferred
- Team restructuring pace — deferred
- Hiring plan — deferred

**Business/operational artifact. No Finding 0-class deviations. The Tier 3 CLI-based development model is consistent with later CLI-first architectural decisions.**
