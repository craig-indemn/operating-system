# Notes: context/business.md

**File:** projects/product-vision/artifacts/context/business.md
**Read:** 2026-04-16 (full file — 166 lines)
**Category:** stakeholder-context

## Key Claims

- **Company**: Indemn. AI associates for insurance — voice, chat, email. $1.1M ARR, 18 customers, 15-person team.
- **Growth**: 3.8x MRR in 9 months. $320K SaaS + $780K JM Earnout/RevShare + $96K usage-based = $1.2M+ before expansions.
- **Series A**: raising $10M. Framework Venture Partners (lead candidate, Olivia Tiessen). Primary Venture Partners (secondary). Pipeline: 24 deals, $2.39M est ARR. "Capacity-constrained, not demand-constrained."
- **Kyle's three-tier model**:
  - Middle Market ($30K-$150K) — "Build the army." Volume play. INSURICA, Union General, GIC.
  - Enterprise — "Us, strategically." JM model. 3-5 max.
  - Product + Partnerships — "Immediate value at scale." Umbrella first. 101 Weston channel.
- **Kyle's $10M plan**: middle market sales/impl + deepen JM + activate 1-2 product programs + scale channel.
- **Kyle's $25M vision**: 3-5 carrier partnerships, 50+ customers, 2-3 embedded specialty programs.
- **The moat question**: "Revenue engines = the moat" but articulation called "uninspired" by leadership. Current best: "We're the only AI that can actually sell an insurance policy." **Craig's thesis for the moat**: insurance-native domain model + agent-accessible platform + compounding intelligence across every deployment. **Every deployment enriches the model.**
- **Kyle's intellectual framework**: "Insurance's primary constraint has always been ACCESS. Generative AI removes the access constraint entirely."
- **SaaS MRR growth** (6 customers): $7K/mo Jul 2025 → $26.7K/mo Mar 2026.
- **EventGuard**: $766K+ premium processed. 2,934 policies. 351 venues. 32.1% conversion rate.
- **Customer portfolio (Prioritization Framework scores)**:
  - INVEST HEAVILY: JM/EventGuard 95, INSURICA 94, GIC Underwriters 94.
  - EXECUTE: Branch 71, Rankin 71, Tillman 71, Union General 65.
  - STRATEGIC BET: BrightFire/Reno 81.
- **Critical product path**: Portal AI → BrightFire/Reno → Agency Network → Gastown (AI Agent Factory, Q3 2026).
- **Gastown = "the factory that builds them"** — needs Portal + Renewal + Voice proven first.
- **Team (15 people)** enumerated with roles + responsibilities.
- **Customer OS problem (from Kyle's Mar 23 doc)**: 67% of WON customers "Never" contacted. 6/18 no owner. Physicians Mutual ($500K) untouched since April 2025. Process problem, not tools problem.
- **Leadership dynamics**: Craig/Cam/Kyle/Ryan alignment issues. Cam proposes biweekly alignment meetings. Kyle's "shifting sands" problem (priorities change without warning).

## Architectural Decisions

Non-architectural — business + strategy. Key implications for the OS:
- **OS must serve all three tiers** (middle market, enterprise, product partnerships).
- **OS must be the "factory that builds them"** (Gastown).
- **Platform IS the moat** — compounding across deployments.
- **GIC + INSURICA + JM (top 3 customers) prove 80% of product thesis** → the OS must handle all three shapes of workload (B2B pipeline, renewals, embedded consumer).
- **Agent-accessible platform** — deep implications for the harness pattern (per Finding 0).

## Layer/Location Specified

- No specific layer/location claims. Business/strategy context.
- Implicit: the OS is the NEW platform Craig is building. Current codebases continue serving current customers.

**Finding 0 relevance**: The strategic context pressures toward shipping. The OS must serve revenue-generating customers. Finding 0 (agent execution in wrong layer) blocks Phase 6 (dog-fooding Indemn CRM) and Phase 7 (GIC migration — first external customer). Fixing it is essential to the Q3 2026 Gastown milestone.

## Dependencies Declared

- Current customer revenue streams (SaaS MRR, EventGuard, JM earnout)
- Series A prospective investors (Framework, Primary)
- Team allocation (15 people)
- Existing codebases + infrastructure (bot-service, copilot, etc.)

## Code Locations Specified

- None directly. Business context only.
- Current codebase organizations referenced: bot-service, voice-livekit, EventGuard, Union General intake, INSURICA, GIC, BrightFire integrations.

## Cross-References

- Kyle's Google Docs: Revenue Activation, The Proposal, Revenue Engines, Customer OS, Framework VP Pipeline.
- Ian's Four Outcomes Product Matrix.
- Cam's Four Outcomes framework.
- Pipeline dashboard (status currently broken per known issues).
- Meeting intelligence DB.

## Open Questions or Ambiguities

- **Moat articulation** — still "uninspired" per leadership acknowledgment. Craig's domain-model thesis is the default.
- **Customer OS adoption** — 67% of WON customers "Never" contacted. Process + discipline issue.
- **Selling manager gap** — nobody day-to-day manages sales team (Ian/Rocky/Marlon).
- **Website** — discipline, not project. Drew building new site.

**Supersedence note**:
- All business context is CURRENT at April 16, 2026. Subject to change weekly.
- Customer priorities (INSURICA/GIC/JM) are the targets for OS Phase 7 rollout.
- Gastown vision (AI Agent Factory, Q3 2026) is the end-state OS must enable.
- The OS's success = unlocking Gastown = Craig's technical priority.
