# Product Vision

Indemn becomes an insurance lab — the system that lets AI run insurance companies. Not a better CRM, not a nicer chatbot. A platform where any insurance company can be digitized, modeled, and operated through AI associates. EventGuard proved it's possible. The platform makes it repeatable.

## Status

**Session 2026-03-24/25-a CLOSED. Ready to resume in new session.**

### What Was Accomplished

**Phase 1: Context Curation — COMPLETE**
- Read 62+ documents from Slack, Google Drive, OS projects, codebases, and meeting notes
- Source index created cataloging every document
- 5 living context documents created (business, product, architecture, strategy, Craig's vision)

**Phase 2: Vision Synthesis — IN PROGRESS (60% complete)**
- Core thesis articulated and confirmed: one platform, any customer type, configure don't build
- "Insurance lab" framing established — cohort model, digitize entire businesses
- Domain model researched from 5 angles (retail, MGA, carrier, embedded, codebase)
- Domain model v2 completed: 44 aggregate roots + 18 children + 9 value objects + 5 reference tables
- DDD classification applied to all entities (identity, lifecycle, independence, CLI tests)
- Associate-to-entity mapping: 7 entities + 6 capabilities = 84% of pricing matrix
- Full vision document drafted (artifacts/vision/2026-03-25-the-vision.md)
- People dimension discussed — team mapping, engagement sequence planned

**Not Yet Done:**
- Phase 2 remaining: domain model review pass (redundancies between sub-domains), relationship mapping between entities
- Phase 3: Gap analysis (current state vs. domain model — what exists, what's missing, what changes)
- Phase 4: Phased roadmap (sequence of work, each phase delivers standalone value)
- Phase 5: Stakeholder engagement strategy (detailed per-person plans)
- Phase 6: The deliverable (format TBD — presentations, working sessions, demos)

### The Meta-Plan (7 stages)

1. **Context Curation** — DONE. Gathered everything.
2. **Vision Synthesis** — IN PROGRESS. Thesis confirmed. Domain model v2 done. Vision document drafted.
3. **Domain Model Refinement** — NEXT. Review pass, then validate with Ryan (domain reality) and Dhruv (implementation reality).
4. **Gap Analysis** — Map current code/customers/implementations against the domain model.
5. **Phased Roadmap** — Sequence the work. Each phase delivers value. Pre-Series A timeline.
6. **Stakeholder Strategy** — Per-person engagement. Ryan → Dhruv → George → Kyle + Cam.
7. **The Deliverable** — The CTO pitch in whatever form captivates.

### Critical Framing Decisions (from brainstorming)

- **This is NOT a migration.** The current system stays. The new platform is built alongside it. Intake Manager is the kernel. Current customer work is R&D that informs the platform.
- **This is NOT replacing copilot-dashboard.** The portal (Ryan's wireframes) is a new thing on the new platform.
- **The roadmap is pre-Series A.** The vision must be DONE before funding. When $10M arrives, we scale — we don't figure things out.
- **The vision is bigger than entities.** It's website, marketing, demos, customer delivery, testing, the team, timing. The domain model is the engine, not the car.
- **Associates are not 48 products.** They're 48 configurations of one platform. Each is an AI agent with skills that operate on domain objects via CLI/API.
- **Three tiers of platform usage emerge:** (1) Managed service (Indemn runs it), (2) Self-service (customer configures), (3) Build on platform (customer builds their own products). Maps to Kyle's three-tier model.
- **The insurance lab cohort:** Get 5 companies, digitize them on the platform, prove it works at scale. This is the Series A proof.

### How to Resume

1. Read this INDEX.md
2. Read `artifacts/vision/2026-03-25-the-vision.md` — the full vision document
3. Read `artifacts/2026-03-25-domain-model-v2.md` — the refined domain model
4. Read the 5 context documents in `artifacts/context/` for detailed source material
5. Pick up at Stage 3 (Domain Model Refinement) or Stage 4 (Gap Analysis) depending on where Craig wants to go
6. The vision document needs another pass — Craig said it's "closer" but not yet captivating enough. The insurance lab framing is right but needs to be more visceral.

### People Mapping (from discussion, sensitive)

- **Craig** — Architect. Owns vision, domain model, roadmap, OS. Builds Phase 1. Orchestrates everything.
- **Dhruv** — Most sophisticated engineer. Built Intake Manager (the kernel). Maintains production. Working on new website with Cam. **His buy-in is the most critical.** Must see his work as foundation, not replaced.
- **Ryan** — Domain expert. Taxonomy creator. Wireframe designer. Validates domain model against insurance reality. Not an engineer — product architecture.
- **George** — EventGuard operations. Pressure-tests platform against end-to-end insurance. Knows what "running real insurance" requires.
- **Jonathan** — Voice system. Channel layer.
- **Peter** — Boots on ground. Agent deployment, landing pages, customer setup.
- **Rudra** — Integrations (carrier APIs, AMS, web operators). Bus factor risk (solo on integrations).
- **Ganesh** — Best role: organizing Linear. Sees himself as PM. Gatekeeper tendency. Not in the critical path for the vision.
- **Kyle** — CEO. Product packaging, deal closing, fundraising. Wants speed. Three-tier model (middle market + enterprise + product). "Ship it" mentality.
- **Cam** — COO. GTM, enterprise relationships. Views IP as "organizational discipline." Website as discipline. Has 52 marketing sheets sales team isn't using. Wants direction and regular alignment.
- **Drew** — Website development.

### Engagement Sequence

1. **Ryan first** — Domain model validation. Low risk, high value. He's already thinking this way.
2. **Dhruv second** — Show how unified model extends his Intake Manager. His code = the foundation.
3. **George third** — EventGuard pressure test. Can the platform model what EventGuard does?
4. **Kyle + Cam together** — With domain validation and engineering alignment in hand. The pitch: "Here's the architecture that makes your three-tier model possible."

## External Resources

| Resource | Type | Link |
|----------|------|------|
| Four Outcomes Product Matrix | Google Sheet | `1LhHA_PIz9zu8UvatUSIzeWBUvnjgvzAfFbfIfN6Gd9s` |
| Customer Operating System doc | Google Doc | `1dAtib-y9d5I-O9WzW8PON2ofxVKEkzhI7cXwZyk9Kxk` |
| The Proposal doc | Google Doc | `1FhDMx8XodWWhVcU0RDTew_jJIhWbtMP_ViDi9ltkqD4` |
| Revenue Activation doc | Google Doc | `1wyvx4JLJfpDKnZvyW1ZjVDyYxwTNvXm19DIRdJn3P_w` |
| Revenue Engines doc | Google Doc | `1dQMvFcrFx_n_W0GGsq4bPl3EPpyAADjQ3W3W3GLhOfQ` |
| Technology Systems Map | Google Doc | `1_rtTKbAl8Tvhq_ZKPoobH09hK63COaI9iAVBxXw2jJc` |
| Unified Prioritization Framework | Google Sheet | `1RlqxhKbi9hKCcV4bK_jjOQEZ9iAXl3EtDhDmkcb77R0` |
| Engineering Priorities doc | Google Doc | `1OMud6HWGrsAnKEesx7cWXBFLeLu07bm82RXMcyixArA` |
| Package Options — Independent Agency | Google Doc | `1PuAXuJCagVEHTBGdPwBwtbf155PzHXWtjArVz0EPOpk` |
| Cam Bridge — Context Layer Design | Google Doc | `1TjyiXxHvTmgZQC84SqlgKjytISa3Kc2gHcg8Kz_1NKg` |
| Framework VP — Pipeline Package | Google Doc | `1PnXQWhI9ivqWKW0k3hnArOsUR8ESK_udHK_SPgDuvFA` |
| Ryan's Consolidated Doc | Google Doc | `1UrVxenQDx6EwzE4yvvocVwWeI4JXM77Dk3UURLxTQpE` |
| Ryan's Taxonomy v2.1 | Google Doc | `1eVtIQYERk0M4sCk920WwMuqDD9r8EMlExlcZ2CzzkEA` |
| Ryan's Architecture Realignment | Google Doc | `1XCTLCQMq_G8uCxaUqFYOk08XZxMwhmEmcYq_mWBdgWI` |
| Craig/Cam 1:1 Notes (Mar 23) | Google Doc | `1ZwWTHHr6yqhGTY7kKGMP7vy9tdhimUUGN6oqQDB_PrI` |
| Craig/Kyle Sync (Mar 19) | Google Doc | `1K53-v5dyODfg-GLvvIIv5ok2mAHxLcifOvMoGadZ-4E` |
| Intake Manager walkthrough (Mar 19) | Google Doc | `1zHjNB81XHP1W0Qs7oPi3AvnWkgyax8jLsPl8y0aMVBE` |
| Craig/Ryan EventGuard arch (Mar 11) | Google Doc | `1n9SQYgBbsWH-jkAsvhpIGOlC0VnmL1pTApKUJH2rj_A` |
| Series A source docs | Local | projects/series-a/source-docs/ |
| Platform Architecture project | Local | projects/platform-architecture/ (worktree: platform-architecture-brainstorming) |
| GIC Email Intelligence project | Local | projects/gic-email-intelligence/ (worktree: outlook) |
| GIC Improvements project | Local | projects/gic-improvements/ |
| Content System project | Local | projects/content-system/ |
| Ryan's wireframes (HTML/PDF) | Local | /Users/home/Repositories/gic-email-intelligence/artifacts/ |

## Artifacts

| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-24 | [source-index](artifacts/2026-03-24-source-index.md) | Complete index of all 62+ source materials gathered |
| 2026-03-24 | [associate-domain-mapping](artifacts/2026-03-24-associate-domain-mapping.md) | Map every associate to domain objects, capabilities, channels, and read/write patterns |
| 2026-03-25 | [domain-model-research](artifacts/2026-03-25-domain-model-research.md) | Validated domain model v1 — 70 entities across 9 sub-domains, tested from 5 angles |
| 2026-03-25 | [domain-model-v2](artifacts/2026-03-25-domain-model-v2.md) | Refined domain model — DDD-classified: 44 roots + 18 children + 9 value objects + 5 ref tables |
| 2026-03-25 | [the-vision](artifacts/vision/2026-03-25-the-vision.md) | The full vision document — insurance lab, architecture, roadmap, team, story |
| 2026-03-25 | [context/business](artifacts/context/business.md) | Business context — revenue, customers, team, pipeline, funding, dynamics |
| 2026-03-25 | [context/product](artifacts/context/product.md) | Product context — associates, outcomes, pricing matrix, packaging, showcases |
| 2026-03-25 | [context/architecture](artifacts/context/architecture.md) | Architecture context — domain taxonomy, engineering model, what's built, domain model research |
| 2026-03-25 | [context/strategy](artifacts/context/strategy.md) | Strategy context — priorities, political dynamics, stakeholder considerations |
| 2026-03-25 | [context/craigs-vision](artifacts/context/craigs-vision.md) | Craig's vision — the underlying system, AI-first design, agents building agents |
| 2026-03-25 | [session-notes](artifacts/2026-03-25-session-notes.md) | Unreduced session context — vibes, energy, corrections, things between the lines |

## Decisions
- 2026-03-24: Project created to house the unified CTO-level platform vision and Series A roadmap
- 2026-03-24: Phase 1 is context curation — gather everything, compress nothing, preserve full truth
- 2026-03-24: Four spheres identified: Associate Model, Pricing Matrix, Insurance Domain Architecture, Engineering Architecture
- 2026-03-25: The vision is "insurance lab" — not a better CRM, not a nicer chatbot. A system that lets AI run insurance companies.
- 2026-03-25: Associates are configurations of the same underlying agent system, not separate products. 48 configs of one platform.
- 2026-03-25: The new platform is built alongside the current system, not as a migration. Intake Manager is the kernel.
- 2026-03-25: Domain model v1 validated from 5 angles. v2 produced via DDD classification: 44 aggregate roots, 18 children, 9 value objects, 5 reference tables. DRAFT — needs stakeholder validation.
- 2026-03-25: 7 core entities + 6 capabilities cover 84% of the pricing matrix. Start there.
- 2026-03-25: Three customer types are configurations of the same platform. Confirmed by all validators.
- 2026-03-25: Platform concepts (Workflow, Template, KnowledgeBase, Skill) separated from domain entities.
- 2026-03-25: CLI-first everything. If CLI can do it, an agent can do it. If an agent can do it, it scales infinitely.
- 2026-03-25: Vision must be READY before Series A. When funding arrives, scale — don't figure things out.
- 2026-03-25: Stakeholder engagement: Ryan → Dhruv → George → Kyle + Cam.
- 2026-03-25: Craig's role: Architect. Owns vision, domain model, roadmap, OS.
- 2026-03-25: Dhruv's buy-in is most critical. His Intake Manager is the kernel.
- 2026-03-25: DDD entity classification framework: Identity + Lifecycle + Independence + Multiple References + Independent Change + CLI Test. Four categories: Aggregate Root, Aggregate Child, Value Object, Reference Table.
- 2026-03-25: Party model (ACORD pattern) — all person/org types share Contact/Party base with role extensions.
- 2026-03-25: PolicyTransaction absorbs Endorsement/Renewal/Cancellation as types.
- 2026-03-25: Three-layer communication: Email (raw channel) → Interaction (abstract conversation) → Correspondence (business-purpose tracked).
- 2026-03-25: Domain model phased: Phase 1 (~25 things for current associates), Phase 2 (+16 for middle market), Phase 3 (+22 for carrier-grade).

## Open Questions
- Domain model: needs cross-sub-domain relationship mapping (how do entities in different sub-domains reference each other?)
- Domain model: needs final review pass for redundancies between sub-domains before stakeholder presentation
- Gap analysis: what code exists vs. what the domain model requires — the concrete engineering delta
- Roadmap: phase sequencing needs to be reworked. Not a migration. Building something new alongside current system. Each phase delivers standalone value.
- The vision document needs another energy pass — Craig said "closer" but not captivating enough yet
- Series A timeline — how aggressive does the roadmap need to be?
- Which customer becomes the first end-to-end proof on the new platform?
- How does the conference (InsurTech NY) factor into timing?
- Insurance lab cohort — when does this become real vs. aspirational?
- Google Drive docs not yet read: ~30 documents from the 55-doc inventory remain unread (see source-index.md for list)
- Cam's 52 marketing sheets in #fractional-cmo Slack channel — should be reviewed for product context
