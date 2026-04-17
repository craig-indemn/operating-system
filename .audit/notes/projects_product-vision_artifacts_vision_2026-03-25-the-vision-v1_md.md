# Notes: vision/2026-03-25-the-vision-v1.md

**File:** projects/product-vision/artifacts/vision/2026-03-25-the-vision-v1.md
**Read:** 2026-04-16 (full file — 219 lines)
**Category:** stakeholder-context (vision v1, superseded by v2)

## Key Claims

Vision v1 (March 25): "Indemn as Insurance Lab. Bring us your business, and AI will run it."

- **EventGuard as proof**: 110-year-old carrier, end-to-end AI-run insurance. 2,934 policies. $766K premium. Acquired for $2.78M.
- **The vision**: build the underlying system so EventGuard is repeatable in WEEKS, not months.
- **Insurance Lab Model**: cohort of 5 insurance companies (carrier, MGA, retail agency, program admin, wholesale broker). Each gets their business modeled on the platform. Associates configured. Channels connected. Running in weeks.
- **Architecture = Object-Oriented Insurance System**:
  - Every entity has schema + state machine + API + CLI.
  - 9 sub-domains: Core Insurance, Risk & Parties, Submission & Quoting, Policy Lifecycle, Claims, Financial, Authority & Compliance, Distribution & Delivery, Platform Layer.
  - "So foundational, so primitive, so atomic that there is no situation in any customer's insurance business that can't be handled within our system."
- **Associates as Processing Nodes**: Cam's 48 associates = 48 configurations of same system.
- **Experience Layer** = Ryan's wireframes come alive. Configurable per customer type.
- **CLI-first, Agent-first** everything.
- **Delivery channels as first-class** (websites, landing pages, widgets, Outlook add-ins, voice on phone systems).
- **Roadmap pre-Series A**: 5 phases — Foundation → First Associate → Portal → Lab Proof → Pitch.
- **Team (11 people listed with roles)**.
- **Story**: "The only insurance-native domain model with AI agents that can transact, not just talk."
- **How to get buy-in**: multi-stage engagement (Ryan → Dhruv → George → Kyle/Cam).

## Architectural Decisions

Vision-level, not architecture. But establishes the principles:
- **CLI-first, Agent-first**.
- **Object-oriented insurance system.**
- **Associates = configured compositions.**
- **Platform is the moat.**

## Layer/Location Specified

No specific code locations. Vision statement.

- **9 sub-domains** listed (later: 70 entities across the sub-domains per domain-model-research).
- **Implicit**: platform and domain layer separation (later formalized as kernel vs. domain).

**Finding 0 relevance**: "The only insurance-native domain model with AI agents that can TRANSACT, not just talk." Transacting requires tools. The kernel's current assistant (no tools) cannot transact. Finding 0b blocks this thesis.

## Dependencies Declared

- Existing codebases: Intake Manager, GIC Email Intelligence, Mint, Evaluation Framework, CLI, OS, Product Showcases.

## Code Locations Specified

- None (vision statement).

## Cross-References

- `2026-03-25-the-vision.md` (v2, the successor — factory framing vs. lab framing)
- Ryan's wireframes
- Intake Manager (Dhruv's code)
- GIC Email Intelligence (Craig's code)
- EventGuard
- Cam's 48-associate pricing matrix

## Open Questions or Ambiguities

- **v1 vs v2 difference**: v1 is "Insurance Lab" framing; v2 is "Factory" framing. Both survive into the white paper. V2 is the later superseding artifact.

**Supersedence note**: Vision v1 is SUPERSEDED by v2 (same day, refined framing). The architectural implications are the same — platform + associates + domain entities + CLI-first. V2 adds "factory" metaphor and EventGuard-as-proof emphasis.
