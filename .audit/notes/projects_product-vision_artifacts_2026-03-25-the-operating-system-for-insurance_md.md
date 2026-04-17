# Notes: 2026-03-25-the-operating-system-for-insurance.md

**File:** projects/product-vision/artifacts/2026-03-25-the-operating-system-for-insurance.md
**Read:** 2026-04-16 (full file — 128 lines)
**Category:** design-source (vision framing)

## Key Claims

- Core idea: Indemn is building the operating system for insurance. Not a tool. Not a platform. An OS.
- OS analogy (precise): Hardware = Carriers; OS = Indemn; Applications = Associates; Users = Businesses/agents/consumers.
- "You don't rebuild the OS for each customer. Applications run on the OS."
- Indemn is in the middle — inputs (any channel) → OS processes → outputs (any destination).
- "Whether a business runs entirely on Indemn or keeps their legacy systems and connects them — either way, the Indemn OS is the engine processing everything."
- Implementation is trivially fast: Claude Code agent reads plan, runs CLI commands in parallel.
- Three Access Tiers: Out of the box / Configured / Developer CLI (matches tier-operations doc).
- Four Outcomes framework: Revenue Growth, Operational Efficiency, Client Retention, Strategic Control.
- EventGuard is the proof that AI can run end-to-end insurance program; OS makes it repeatable.

## Architectural Decisions

- **OS is the hub** — everything connects to it via the CLI and APIs.
- **Every entity has state machine + API + CLI command** — later resolved as auto-generation from entity definitions.
- **CLI as universal installer** — Tier 3 deployment model. CLI commands like `indemn org create`, `indemn product configure`, `indemn associate deploy`, `indemn channel connect`, `indemn integration connect`.
- **"Configuration, not construction"** — new customer = data configuration, not code writing. Later formalized in "everything is data" data architecture.

## Layer/Location Specified

- No code paths or process topology. Vision-level framing.
- Implicit: OS is ONE deployment; customers run ON it (not self-hosted). Later formalized as PaaS.

## Dependencies Declared

- EventGuard (proof of concept)
- Carrier products (for distribution)
- Existing Indemn customer implementations (GIC, INSURICA, Union General as R&D)

## Code Locations Specified

- None. Vision framing artifact.

## Cross-References

- context/craigs-vision.md (thesis foundation)
- 2026-03-24-associate-domain-mapping.md (48 associates)
- Cam's Four Outcomes Product Matrix
- EventGuard, GIC, INSURICA, Union General (R&D for OS)
- Later: all subsequent design artifacts + the white paper

## Open Questions or Ambiguities

- How to make implementation "trivially fast" technically — resolved via CLI auto-generation from entity definitions.
- How carriers/distribution work on the OS — resolved via entity modeling (Carrier, DistributionPartner primitives).

**Vision framing document. No Finding 0-class deviations. Establishes the "applications run on the OS" mental model that informs later kernel vs. harness separation.**
