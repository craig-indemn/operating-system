# Notes: context/strategy.md

**File:** projects/product-vision/artifacts/context/strategy.md
**Read:** 2026-04-16 (full file — 177 lines)
**Category:** stakeholder-context

## Key Claims

Non-architectural. Stakeholder priorities + political dynamics.

- **Cam's priorities**: organizational discipline as moat; "website as a discipline"; product map (core offerings vs. new builds); sales team utilization (52 marketing sheets exist, aren't used — accessibility problem); direction; conference demos; "round three the first time" (context layer).
- **Cam's context layer**: 7-phase plan — Claude Project for Cam → Pipeline Dashboard onboarding → Meetings API to prod → Slack Bot MVP → Meeting Intelligence Pipeline → Proactive Intelligence → Individual Claude Code setups. Success metric: "Cam stops asking Kyle for routine customer context (2 weeks)."
- **Kyle's priorities**: revenue engines as moat; joint venture model ("EventGuard without having to start EventGuard"); omni-channel workflow automation (Series A pitch); self-service account creation; speed ("ship it"); three tiers.
- **Kyle's framework**: insurance constraint = ACCESS; gen AI removes it. Looking for "Wikipedia of insurance + AI."
- **Ryan's value**: insurance domain taxonomy, wireframes, organizational clarity voice. Concerned about "building useful things in isolation."
- **Dhruv's critical position**: built Intake Manager (50-70% of platform foundation). His buy-in is most important. Platform must honor his architecture decisions.
- **Craig's political strategy**: multi-stage engagement (Ryan → Dhruv → George → Kyle/Cam). "Make it impossible to say no." Delivery process is itself a design problem.
- **The broader vision (Craig's Insurance Lab)**: "Bring us your business, and AI will run it." 5 insurance companies in cohort — each proves a facet (carrier new product, MGA automation, retail agency digitization, program admin distribution, wholesale broker email ops).
- **What needs to be true before Series A**:
  1. Domain model designed and core entities built
  2. At least one associate working on new platform across two customer types
  3. Portal (Ryan's wireframes) alive on new platform
  4. End-to-end proof (one scenario running entirely on new platform)
  5. The story is proven, not promised
- **Timing conflicts**: team doing custom work, no roadmap distinguishing new builds from core, Cam's "lack of discipline," conference demos + website imminent, Series A active.

## Architectural Decisions

Non-architectural. Strategic implications:
- **Platform must coexist with current customer delivery** — additive, not disruptive.
- **Current implementations inform platform design.**
- **Dog-food Indemn CRM first (Phase 6)** before first external customer (Phase 7).
- **Ryan → Dhruv → George → Kyle/Cam** engagement sequence.

## Layer/Location Specified

- No specific layer/location claims. Strategic + political context.

**Finding 0 relevance**: The Series A urgency + "make it impossible to say no" pressure pushes toward shipping quickly. Finding 0 (agent execution in wrong layer) is a structural issue that blocks Phase 6/7 — but fixing it properly (3 harness images) is significant work that delays shipping. Tradeoff between architectural correctness and timing pressure is a governance consideration, not purely technical.

## Dependencies Declared

- Series A prospective investors (Framework, Primary)
- Key customer relationships (JM/EventGuard, INSURICA, GIC)
- Team alignment (Kyle, Cam, Craig, Dhruv, Ryan)

## Code Locations Specified

- None.

## Cross-References

- Revenue Engines Google Doc (Kyle + Cam alignment)
- Cam Bridge Context Layer Design Doc
- Constraint Removal AI Thought Piece
- Craig/Cam 1:1 + Craig/Kyle Sync meeting notes
- Ryan's wireframes + taxonomy document
- Dhruv's Intake Manager codebase

## Open Questions or Ambiguities

- **Moat sentence** — still "uninspired" per leadership.
- **Selling manager gap** — nobody manages sales team day-to-day.
- **Cam's 7-phase plan** — not tracked as kernel OS work; separate pipeline dashboard project.

**Supersedence note**: Strategy context SURVIVES as directional context. Success criteria for OS (domain model + one associate + portal + E2E proof) are the Phase 6/7 completion criteria.
