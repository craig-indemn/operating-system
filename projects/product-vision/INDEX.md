# Product Vision

Indemn is building the operating system for insurance. Not a better CRM, not a nicer chatbot. The OS that any insurance business runs on — modeled, automated, and powered by AI associates. EventGuard proved AI can run an insurance business end-to-end. The OS makes it repeatable for anyone.

## Status

**Session 2026-04-13 (session 6, day 3) — Simplification pass complete. All post-trace synthesis items resolved. Systematic gap analysis surfaced 6 remaining design categories beyond kernel architecture. Next: design sessions for Infrastructure & Deployment, Development Workflow, Dependencies & Resilience, Operations, Transition & Coexistence, Domain Modeling Process — then write the specification document, derive the build sequence, engage stakeholders, and build.**

**Session 2026-04-11 (session 6, day 2 cont.) — Authentication design complete (item 10 from post-trace synthesis). One new bootstrap entity: Session (count now 7). Five auth method types. Platform admin model refined for "Indemn builds most things for the customer."**

**Session 2026-04-11 (session 6, day 2) — Base UI as real-time operational surface complete (items 8 and 9 from post-trace synthesis, resolved together). Pipeline Dashboard + Queue Health collapse into the base UI itself — derived from system definition, not a separate feature. Assistant-at-the-forefront is the primary UI decision.**

**Session 2026-04-10 (session 6) — Design phase continuing. Bulk operations pattern complete (item 7 from post-trace synthesis).**

**Session 2026-04-10 — Kernel validated against three real workloads. First design session complete. Remaining design work is finite and scoped. Path to spec is a checklist of known items.**

**Prior: Session 2026-04-08/09 — Kernel architecture substantially resolved. Needs consolidation into single spec, then build.**

### What Was Accomplished

**Phase 1: Context Curation — COMPLETE** (Session 2026-03-24/25)
- 62+ documents read. Source index. 5 context documents.

**Phase 2: Vision Synthesis — COMPLETE** (Sessions 2026-03-24/25 + 2026-03-30)
- Core framing: The Operating System for Insurance
- Domain model v2: 44 aggregate roots, DDD-classified
- Four Outcomes / Four Engines as product layer
- Three tiers: out of box / configured / developer (PaaS)
- Associate architecture: deep agents with skills + CLI
- Why insurance why now, automation spectrum, intelligence flywheel
- Platform tiers, buying experience, operational model

**Phase 3: Design — COMPLETE** (Sessions 2026-03-30 + 2026-04-02 + 2026-04-07 + 2026-04-08/09)
- Kernel primitives: Entity, Message, Actor, Role, Organization
- Wiring mechanism: WATCHES on roles (actor-centric routing) — THE core question resolved
- Actor spectrum: deterministic ↔ reasoning, harness-agnostic, same framework
- Kernel capabilities = entity methods (unified), activated via CLI, parameterized by per-org config
- Skills: always markdown, stored in MongoDB, entity skills (auto-generated) + associate skills (behavioral)
- One condition language: JSON, shared by watches and rules, one evaluator
- Everything is data: entity definitions, skills, rules, configs in MongoDB. OS codebase = platform. Database = application.
- Temporal for associate execution (durable workflows). MongoDB for the universal queue (humans + associates).
- OTEL baked in: correlation_id = trace_id, everything in one trace
- Unified queue: associates are employees, same queue as humans, interchangeable
- Entry points (channels, webhooks, API, polling) create entities → kernel takes over
- Triggers: message (watch match), schedule (creates queue items), direct invocation (real-time)
- Assignment: domain concern, not kernel primitive. Context-based filtering.
- Schema migration: first-class capability with batching, dry-run, aliases, rollback
- Three rounds of architecture ironing: 19 inconsistencies found and resolved
- Three rounds of independent reviews: security, platform engineering, DevOps — 14 findings, all addressed
- Data architecture: MongoDB (config + data), S3 (files), Temporal Cloud (execution), OTEL (observability)
- Security: OrgScopedCollection, AWS Secrets Manager, skill content hashing, sandbox spec, tamper-evident audit

**Phase 4: Implementation Planning — NEEDS REVISION**
- Original plan (Phases 0-5) is stale — architecture changed significantly
- Build order still: hand-build first, extract framework
- But specifics need revision based on new architecture (Temporal, everything-is-data, etc.)

**Phase 5: Priorities, Roles, Time, Execution — NEEDS REVISION**
- Same principles apply but implementation details changed

### What's Next
1. **Consolidate into single kernel specification** — one document capturing the final architecture, clear enough to build from
2. **Retrace GIC end-to-end with final architecture** — validate all decisions hold under real usage
3. **Simplification pass** — remove anything that doesn't earn its complexity
4. **Revised build order** — what gets built first, acceptance criteria, validation approach
5. **Start building** — first entity by hand, prove the full stack works

**Not Yet Done:**
- Resolve the wiring/connection mechanism (core design question — blocks everything)
- Trace real scenarios end-to-end through every component (solidify mental model)
- Craig's pressure test with GIC case study context
- Finalize roles and time allocations
- Final roadmap synthesis
- Vision document consolidation (28+ artifacts → one narrative)
- Stakeholder engagement strategy
- The deliverable format
- Champion strategy (how Craig rolls this out to the company)

### The Path to Roadmap

Per Craig: vision → design → implementation → priorities → roles → time allocations → execution → **roadmap** (last)

1. **Context Curation** — DONE.
2. **Vision Synthesis** — DONE. 10+ artifacts capturing OS framing, industry context, product model, associate architecture, operational model.
3. **Design** — SUBSTANTIALLY DONE. 5-layer architecture, core primitives (Entity + Message), hardened via adversarial review, uniform Entity class, simplified real-time.
4. **Implementation Planning** — DRAFTED. Phases 0-5, hand-build first approach.
5. **Priorities, Roles, Time, Execution** — INITIAL PASS. Needs deeper work on roles and finalization.
6. **End-to-end scenario tracing** — NOT DONE. Craig wants to trace real scenarios through every component to solidify mental model. Has a parallel project as pressure test.
7. **Phased Roadmap** — NOT DONE. The final synthesis.
8. **Stakeholder Engagement + Champion Strategy** — NOT DONE. How Craig rolls this out to the company.
9. **The Deliverable** — NOT DONE. Vision + roadmap in presentable form.

### Critical Framing Decisions (from brainstorming)

- **This is NOT a migration.** The current system stays. The new platform is built alongside it. Intake Manager is the kernel. Current customer work is R&D that informs the platform.
- **This is NOT replacing copilot-dashboard.** The portal (Ryan's wireframes) is a new thing on the new platform.
- **The roadmap is pre-Series A.** The vision must be DONE before funding. When $10M arrives, we scale — we don't figure things out.
- **The vision is bigger than entities.** It's website, marketing, demos, customer delivery, testing, the team, timing. The domain model is the engine, not the car.
- **Associates are not 48 products.** They're 48 configurations of one platform. Each is an AI agent with skills that operate on domain objects via CLI/API.
- **Three tiers of platform usage emerge:** (1) Managed service (Indemn runs it), (2) Self-service (customer configures), (3) Build on platform (customer builds their own products). Maps to Kyle's three-tier model.
- **The insurance lab cohort:** Get 5 companies, digitize them on the platform, prove it works at scale. This is the Series A proof.

### How to Resume

**CRITICAL: Read every file. No shortcuts. Craig explicitly said "I want the new session to read all the files otherwise we are going to not have the full context. I know it's a lot, but I think it's important."**

1. Read `artifacts/2026-04-10-session-5-checkpoint.md` LAST, not first. It's a companion for orientation AFTER you've read the artifacts, not a substitute for reading them.
2. Read files in the order listed in the session 5 checkpoint's "How to Resume" section (52 files total). This order flows from foundation (sessions 1-4) to session 5 (today) to the checkpoint.
3. For files that error on token limit (like some of the adversarial review files from 2026-04-07), use Read with offset/limit parameters or Grep to chunk through them. Do NOT move on without the full content.
4. After reading everything, ask Craig what to tackle next from the open items in the session 5 checkpoint:
   - Bulk operations pattern (item 7)
   - Pipeline dashboard + queue health (items 8, 9)
   - Authentication (item 10)
   - Documentation sweep (items 4, 5, 6, 12)
   - Simplification pass (after all design sessions)
   - Spec writing (final step)
5. Don't re-litigate decisions from prior sessions. The "What's DECIDED" section of the session 5 checkpoint is authoritative.
6. Craig's key guidance: "I don't think the system is complicated for us to implement, as long as we're clear about what we're building, why, and how it should be used, and we document everything." And: "A lot of this can be simplified" — but the simplification pass is scheduled for after all design sessions complete.

### Previous resume notes (for historical context)

Prior to session 5, resume instructions pointed to the session 4 checkpoint. That's still valid reading material but it's no longer the most recent checkpoint. Session 5 checkpoint supersedes it as the entry point.

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
| 2026-03-25 | [the-vision-v1](artifacts/vision/2026-03-25-the-vision-v1.md) | Original vision document — insurance lab framing |
| 2026-03-25 | [the-vision](artifacts/vision/2026-03-25-the-vision.md) | Vision doc v2 — factory framing (stale — needs OS framing in final consolidation) |
| 2026-03-25 | [os-for-insurance](artifacts/2026-03-25-the-operating-system-for-insurance.md) | Core OS framing — system in the middle, carriers as conduit, three tiers, convergence |
| 2026-03-25 | [why-insurance-why-now](artifacts/2026-03-25-why-insurance-why-now.md) | Industry context, intelligence flywheel, distribution chain collapse, automation spectrum |
| 2026-03-25 | [platform-tiers-and-operations](artifacts/2026-03-25-platform-tiers-and-operations.md) | Three tiers, Tier 3 as dev model, buying experience, operational transition |
| 2026-03-25 | [associate-architecture](artifacts/2026-03-25-associate-architecture.md) | Deep agents, skills, evaluations, connection to current agent systems |
| 2026-03-30 | [entity-system-and-generator](artifacts/2026-03-30-entity-system-and-generator.md) | Entity generator, build vs buy, skills as docs, CRM/AMS, product configuration |
| 2026-03-30 | [session-2-checkpoint](artifacts/2026-03-30-vision-session-2-checkpoint.md) | Comprehensive checkpoint of all session 2 thinking |
| 2026-03-25 | [context/business](artifacts/context/business.md) | Business context — revenue, customers, team, pipeline, funding, dynamics |
| 2026-03-25 | [context/product](artifacts/context/product.md) | Product context — associates, outcomes, pricing matrix, packaging, showcases |
| 2026-03-25 | [context/architecture](artifacts/context/architecture.md) | Architecture context — domain taxonomy, engineering model, what's built, domain model research |
| 2026-03-25 | [context/strategy](artifacts/context/strategy.md) | Strategy context — priorities, political dynamics, stakeholder considerations |
| 2026-03-25 | [context/craigs-vision](artifacts/context/craigs-vision.md) | Craig's vision — the underlying system, AI-first design, agents building agents |
| 2026-03-25 | [session-notes](artifacts/2026-03-25-session-notes.md) | Unreduced session context — vibes, energy, corrections, things between the lines |
| 2026-04-02 | [core-primitives-architecture](artifacts/2026-04-02-core-primitives-architecture.md) | Four primitives (Entity, Message, Actor, Role) — the simplest foundation that composes into everything |
| 2026-04-02 | [design-layer-4-integrations](artifacts/2026-04-02-design-layer-4-integrations.md) | Integration adapters, channel connections, external system mapping |
| 2026-04-02 | [design-layer-5-experience](artifacts/2026-04-02-design-layer-5-experience.md) | Experience layer — UI auto-generation, role-based views, queue dashboard |
| 2026-04-02 | [implementation-plan](artifacts/2026-04-02-implementation-plan.md) | Implementation phases, parallel session strategy, timeline estimates |
| 2026-04-03 | [message-actor-architecture-research](artifacts/2026-04-03-message-actor-architecture-research.md) | Actor model, event-driven patterns, messaging infrastructure, work queues — research for the four-primitive design |
| 2026-04-02 | [design-layer-1-entity-framework](artifacts/2026-03-30-design-layer-1-entity-framework.md) | Entity framework + Layer 2 API/CLI — Beanie, Pydantic, FastAPI, Typer, auto-registration, @exposed |
| 2026-03-30 | [design-layer-3-associate-system](artifacts/2026-03-30-design-layer-3-associate-system.md) | Associate system — deep agents, skills, workflows, evaluations, sandbox execution |
| 2026-04-07 | [challenge-insurance-practitioner](artifacts/2026-04-07-challenge-insurance-practitioner.md) | Adversarial review: missing entities, broken workflows, oversimplified state machines, rules engine need |
| 2026-04-07 | [challenge-distributed-systems](artifacts/2026-04-07-challenge-distributed-systems.md) | Adversarial review: transaction boundaries, polling, cascades, concurrency, exactly-once delivery |
| 2026-04-07 | [challenge-developer-experience](artifacts/2026-04-07-challenge-developer-experience.md) | Adversarial review: concept count, routing rules undefined, observability missing, onboarding curve |
| 2026-04-07 | [challenge-realtime-systems](artifacts/2026-04-07-challenge-realtime-systems.md) | Adversarial review: two-mode problem, voice latency, Interaction Host pattern, concurrent entity access |
| 2026-04-07 | [challenge-mvp-buildability](artifacts/2026-04-07-challenge-mvp-buildability.md) | Adversarial review: timeline reality check, over/under-engineering, build by hand first then framework |
| 2026-04-08 | [session-3-checkpoint](artifacts/2026-04-08-session-3-checkpoint.md) | Session 3 comprehensive checkpoint — what's decided, what's unresolved, how to resume |
| 2026-04-08 | [actor-spectrum-and-primitives](artifacts/2026-04-08-actor-spectrum-and-primitives.md) | Actor spectrum insight — deterministic/reasoning as interpreter choice, entity polymorphism |
| 2026-04-08 | [primitives-resolved](artifacts/2026-04-08-primitives-resolved.md) | Watches as wiring, actor definition, entity/actor boundary, scheduled tasks resolved |
| 2026-04-08 | [entry-points-and-triggers](artifacts/2026-04-08-entry-points-and-triggers.md) | How external events enter the OS. Three trigger types. Channels are entry points. |
| 2026-04-08 | [kernel-vs-domain](artifacts/2026-04-08-kernel-vs-domain.md) | Kernel primitives vs. domain entities. Assignment not a primitive. Actor references via context. |
| 2026-04-08 | [pressure-test-findings](artifacts/2026-04-08-pressure-test-findings.md) | First review round (platform, DX, distributed systems) — 8 key findings |
| 2026-04-08 | [actor-references-and-targeting](artifacts/2026-04-08-actor-references-and-targeting.md) | Messages target roles, context enables filtering. Entities are source of truth. |
| 2026-04-09 | [entity-capabilities-and-skill-model](artifacts/2026-04-09-entity-capabilities-and-skill-model.md) | Kernel capabilities + per-org config + markdown skills. The "auto" pattern. |
| 2026-04-09 | [capabilities-model-review-findings](artifacts/2026-04-09-capabilities-model-review-findings.md) | Second review round — multi-entity atomicity, rule composition, evaluation traces |
| 2026-04-09 | [temporal-integration-architecture](artifacts/2026-04-09-temporal-integration-architecture.md) | Temporal integration — what it replaces, GIC on Temporal, OTEL unification |
| 2026-04-09 | [unified-queue-temporal-execution](artifacts/2026-04-09-unified-queue-temporal-execution.md) | THE key: one queue for everyone. Associates are employees. Gradual rollout. |
| 2026-04-09 | [data-architecture-everything-is-data](artifacts/2026-04-09-data-architecture-everything-is-data.md) | Entity defs, skills, rules as DB data. Built-in version control. Environments as orgs. |
| 2026-04-09 | [architecture-ironing](artifacts/2026-04-09-architecture-ironing.md) | Round 1: 7 issues resolved (skill/workflow, entity creation, outbox, schedules, etc.) |
| 2026-04-09 | [architecture-ironing-round-2](artifacts/2026-04-09-architecture-ironing-round-2.md) | Round 2: 5 issues resolved (capabilities+methods, conditions, message data, etc.) |
| 2026-04-09 | [architecture-ironing-round-3](artifacts/2026-04-09-architecture-ironing-round-3.md) | Round 3: 7 issues resolved (events, emission, claiming, bootstrap, schema, versioning) |
| 2026-04-09 | [data-architecture-review-findings](artifacts/2026-04-09-data-architecture-review-findings.md) | Third review round (platform eng, DevOps, security) — 14 findings with priority matrix |
| 2026-04-09 | [data-architecture-solutions](artifacts/2026-04-09-data-architecture-solutions.md) | All 14 findings addressed — solutions maintain simplicity, no new infrastructure |
| 2026-04-09 | [session-4-checkpoint](artifacts/2026-04-09-session-4-checkpoint.md) | Session 4 comprehensive checkpoint — full journey, all decisions, how to resume |
| 2026-04-09 | [consolidated-architecture](artifacts/2026-04-09-consolidated-architecture.md) | THE CURRENT ARCHITECTURE in one document — all primitives, all decisions, how it works |
| 2026-04-10 | [integration-as-primitive](artifacts/2026-04-10-integration-as-primitive.md) | Integration elevated from entity to the 6th kernel bootstrap primitive. Adapters are its implementation. Owner field enables org-level and actor-level credentials. Resolves user credential management, adapter versioning, and the integration-vs-adapter framing ambiguity. |
| 2026-04-10 | [gic-retrace-full-kernel](artifacts/2026-04-10-gic-retrace-full-kernel.md) | End-to-end GIC email intelligence pipeline traced through the updated 6-primitive kernel. Validates Integration, unified queue, watches, multi-entity atomicity, --auto pattern. Kernel holds up. Six follow-up concerns identified: coalescing, pipeline dashboards, ephemeral locks, multi-LOB drafts, queue health tooling, computed field activation scope. |
| 2026-04-10 | [base-ui-and-auth-design](artifacts/2026-04-10-base-ui-and-auth-design.md) | Auto-generated base UI (1:1 CLI mapping, role-scoped, admin-first), how it addresses the retrace concerns, two kernel additions (watch coalescing, ephemeral entity locks), authentication sketch (methods-on-Actor, identity providers as Integrations, SSO+password coexistence, role-grant as meta-permission). Resolves the associate-role asymmetry with two ergonomic creation paths (named shared roles vs inline roles on associate creation). |
| 2026-04-10 | [eventguard-retrace](artifacts/2026-04-10-eventguard-retrace.md) | End-to-end EventGuard consumer-facing flow traced through the kernel (venue onboarding → widget → chat → quote → Stripe payment → policy → certificate → delivery, across 351 venues). Fully autonomous, real-time, multi-integration. Kernel holds. Surfaces one real architectural gap (mid-conversation event delivery to running real-time actors via actor-context watch scoping + Temporal signals), plus inbound webhook dispatch clarification and bulk operations pattern design. |
| 2026-04-10 | [post-trace-synthesis](artifacts/2026-04-10-post-trace-synthesis.md) | Distills what GIC + EventGuard retraces collectively validated (kernel holds across very different workloads) and what design work remains. Ten items categorized: architectural (watch coalescing, ephemeral locks, actor-context signals, bulk operations), documentation (inbound webhooks, internal vs external entities, computed field scope), supporting infrastructure (pipeline dashboard, queue health), separate session (auth). Status table shows six of ten need real design before spec. Proposes sequence: CRM trace → design sessions → simplification → spec. |
| 2026-04-10 | [crm-retrace](artifacts/2026-04-10-crm-retrace.md) | Third pressure test — Indemn's own internal CRM (generic B2B intelligence, heavy actor-level integrations, dog-fooding). Validates kernel is genuinely domain-agnostic (zero insurance concepts). Surfaces one new architectural addition (associates with `owner_actor_id` for delegated credential access to the human owner's personal integrations) and one privacy design (content visibility scoping for personal-integration-derived entities). All design items from prior traces are used here too — confirming they're real kernel requirements, not single-trace quirks. Kernel deemed ready to encapsulate. |
| 2026-04-10 | [realtime-architecture-design](artifacts/2026-04-10-realtime-architecture-design.md) | First design-session artifact. Resolves the biggest architectural gap from the retraces: how real-time actors receive mid-conversation events, how scoped events reach specific actors (not everyone in a role), where associates run, how handoff between actors/roles works. Introduces two bootstrap entities (Attention, Runtime), scoped watches (field_path + active_context), watch coalescing, the thin CLI-based harness pattern, three-layer customer-facing flexibility (Deployment+Associate+Runtime), and voice clients as Integrations. Unifies ephemeral entity locks and real-time active contexts into Attention. One new CLI command: `indemn events stream`. Six structural primitives unchanged. |
| 2026-04-10 | [session-5-checkpoint](artifacts/2026-04-10-session-5-checkpoint.md) | Comprehensive checkpoint of session 5 — the full journey (12 phases), all decisions locked in, all open items, artifacts produced, and explicit resume instructions for the next session (read ALL 52 files in the specified order, no shortcuts). Captures session 5 decisions, corrections Craig caught (file re-reads, fabricated actions, hardcoded model in harness, CLI vs API conflation), and guidance from Craig across the session. |
| 2026-04-10 | [bulk-operations-pattern](artifacts/2026-04-10-bulk-operations-pattern.md) | Bulk operations as a kernel-provided pattern (not a primitive, not a new bootstrap entity). Generic `bulk_execute` Temporal workflow. CLI verb taxonomy (bulk-create/transition/method/update/delete) enforcing selective emission discipline. Scheduled and ad-hoc unified. Multi-entity-per-row deferred to skill code (Option α). Failure handling: skip-and-continue default with `--failure-mode=abort` opt-in. Permanent vs transient error classification. Idempotency at entity level. Full GIC stale-check trace validates the pattern. Resolves item 7 from the post-trace synthesis. |
| 2026-04-11 | [base-ui-operational-surface](artifacts/2026-04-11-base-ui-operational-surface.md) | Base UI as a real-time operational surface derived from the system definition — not a dashboard app, not a separate layer. Pipeline Dashboard + Queue Health (items 8, 9) collapse into this single surface. Design principles: UI derives from system, tables > charts, interactive tables as primary surface, forms auto-generated, **assistant at the forefront** via slim top-bar input (not right-panel, not Cmd-K modal), real-time via Change Streams filtered by current view, nothing new in kernel. Rendering contract maps primitives to UI elements (entity list views, detail views, queue view, role overview, bootstrap observability, pipeline metrics, cascade viewer). Kernel aggregation capabilities: state-distribution, throughput, dwell-time, queue-depth, cascade-lineage. Default associate per human actor with same permissions — context-aware via implicit UI payload, persistent conversation, inline entity renderings, real-time subscriptions. Complexity ladder: click → pattern → instruct → command, same system across four surfaces. Active alerting deferred. Resolves items 8 and 9 from the post-trace synthesis. |
| 2026-04-11 | [authentication-design](artifacts/2026-04-11-authentication-design.md) | Authentication designed end-to-end. One new bootstrap entity: **Session** (universal across user_interactive / associate_service / tier3_api / cli_automation types). Bootstrap count now 7. Hybrid JWT + Session model: short-lived access tokens (stateless verification, 15min), long-lived opaque refresh tokens stored hashed in Secrets Manager. Platform-wide JWT signing key. **Five auth method types** (reduced from 7 by merging api_key+service_token into unified `token`, deferring WebAuthn): password, totp, sso, token, magic_link. MFA policy: Role-level `mfa_required` with Actor `mfa_exempt` override and Org `default_mfa_required`. Fresh MFA re-verification via `@exposed(requires_fresh_mfa=N)`. **Platform admin cross-org model refined for "Indemn builds most things for customer"** — `_platform` system org, PlatformCollection accessor, 4h default duration (24h max), auto-renewable on activity, work-type tagging (build/debug/incident/routine), per-customer notification config, strict scope limits (no secrets, no impersonation), audit in target org's changes collection. Claims refresh (not full revocation) on role change. Default assistant inherits user session. Owner-bound scheduled associates use own service tokens. Argon2id password hashes in MongoDB, raw secrets in Secrets Manager. Recovery flows: password reset via magic_link, MFA via backup codes or admin reset, emergency access via platform admin. No back doors. Pre-auth rate limiting. Revocation cache with Change Stream invalidation + startup bootstrap. Ten forcing functions all pressure-tested. Resolves item 10 from the post-trace synthesis. |
| 2026-04-13 | [documentation-sweep](artifacts/2026-04-13-documentation-sweep.md) | Five documentation clarifications from the post-trace synthesis, all resolved in one artifact. Item 4: inbound webhook dispatch via Integration adapters — kernel-provided endpoint at `/webhook/{provider}/{integration_id}`, adapter interface extended with validate_webhook/parse_webhook. Item 5: internal Actors (authenticate, have roles, participate) vs external counterparty entities (domain data, no auth). Item 6: computed field mappings belong on method activation config, not as Lookups — Lookups are for shared cross-entity reference data. Item 11: `owner_actor_id` on Associate formalized with consent/revocation/transfer lifecycle and two auth patterns (default assistant inherits user session, scheduled associates use own tokens). Item 12: content visibility scoping via `content_visibility` field on Integration (full_shared / metadata_shared / owner_only), default actor-owned=metadata_shared, S3 path-based access control. Resolves items 4, 5, 6, 11, 12 from the post-trace synthesis. |
| 2026-04-13 | [simplification-pass](artifacts/2026-04-13-simplification-pass.md) | Architecture reviewed with fresh eyes. Two architectural simplifications accepted: watch coalescing removed from kernel (→ UI rendering concern), rule evaluation traces moved to changes collection metadata. Runtime stays as kernel entity. "Bootstrap entity" renamed to "kernel entity." Two features confirmed deferred (WebAuthn, per-operation MFA re-verification). Craig pushed back on over-aggressive scope reductions: schema migration, all 5 Attention purposes, content visibility, and rule groups with lifecycle all kept in MVP. Architecture is proportional — every concept serves one of the six primitives. |
| 2026-04-13 | [session-6-checkpoint](artifacts/2026-04-13-session-6-checkpoint.md) | Comprehensive checkpoint. Kernel architecture complete. Systematic gap analysis surfaced 6 remaining design categories beyond the kernel (infrastructure, dev workflow, dependencies, operations, transition, domain modeling). Deliverable structure decided: one document with layered depth (white paper = sections 1-2, specification = sections 3-9, build plan = section 10). Order: design remaining gaps → write the spec → derive build sequence → stakeholder engagement → build. |

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
- 2026-03-30: Core framing evolved from "insurance lab"/"factory" to **"The Operating System for Insurance."** The system everything runs on, not a tool in the stack.
- 2026-03-30: EventGuard is proof the CONCEPT works (AI can run insurance). The OS makes it repeatable. Existing implementations (GIC, INSURICA, etc.) are R&D that informed the design.
- 2026-03-30: Four Outcomes / Four Engines are the product layer connecting customer needs to the OS. The business story (Kyle/Cam) and technology story (Craig) are the same story from two sides.
- 2026-03-30: Insurance is people-centric. The OS elevates the workforce, doesn't replace it. Full automation spectrum from EventGuard-style autonomy to human-directed with OS tooling.
- 2026-03-30: Three tiers: out of box (website) / configured (FDEs) / developer (CLI+API, PaaS). Tier distinction is integration maturity, not OS capability. Tier 3 IS the development model — Indemn uses it to build everything.
- 2026-03-30: Associates are LangChain deep agents with skills (Claude Code pattern) operating on domain objects via CLI/API. Evolution of V2 agent architecture.
- 2026-03-30: Build from scratch on MongoDB. No open source AMS exists. Insurance domain too specialized for generic CRM frameworks. The entity generator IS the framework — purpose-built, CLI-native.
- 2026-03-30: Entity generator is the OS kernel. Declarative entity definitions → auto-generate API, CLI, skill (docs), events, permissions. Skills serve associates, developers, and engineers simultaneously.
- 2026-03-30: Product configuration, not custom entities. Same Submission entity, different form schemas per product. Entity structure is fixed; product-specific data goes in flexible fields.
- 2026-03-30: The OS IS a CRM and AMS. Indemn dog-foods it. No separate CRM needed — Kyle's CRM request is answered by the OS itself.
- 2026-03-30: Craig builds the OS with AI (10+ parallel Claude Code sessions). Foundation buildable in 1-2 weeks. OS operational before Series A close (~3 months).
- 2026-03-30: Data populated on need-to-know basis with reusable CLI/skill framework. Carrier data built up through customer onboarding + industry sources. Intelligence flywheel applies to data, not just models.

- 2026-04-02: Core primitives: two implementation primitives (Entity + Message), four conceptual (+ Actor + Role). Everything composes from these.
- 2026-04-02: Messages unify: notifications, tasks, triggers, HITL, workflow steps, channel input, events. All are messages routed to actors.
- 2026-04-02: Every actor (human or associate) has a queue. The queue IS their view of the system.
- 2026-04-02: Roles define access AND routing. One concept, two functions.
- 2026-04-02: Context management: entity graph resolved and attached to messages. Associates get rich pre-loaded context.
- 2026-04-02: Workflows emerge from entity state changes + message routing. Explicit workflow definitions for complex conditional/parallel/compliance cases.
- 2026-04-02: Personal AI assistant per role — an associate configured with the same permissions as the human.
- 2026-04-07: Adversarial review by 5 independent agents: insurance practitioner, distributed systems, developer experience, real-time systems, MVP buildability. Core primitives validated. Implementation hardened.
- 2026-04-07: 10 hardening requirements for the base Entity: version field, transactional saves, correlation IDs, visibility timeouts, cascade depth, idempotent handlers, selective emission, MessageBus abstraction, cached routing evaluation, routing rules as entities.
- 2026-04-07: Messaging infrastructure: MongoDB-only for MVP. Messages in `messages` collection. `findOneAndUpdate` for atomic claiming. Polling for consumption. RabbitMQ added later if needed (additive, not replacing).
- 2026-04-07: Routing rules are RoutingRule entities — per-org, configurable via CLI, cached in memory. NOT hardcoded on entity classes. Code extension point for complex logic.
- 2026-04-07: Selective emission: only state transitions + @exposed methods + creation/deletion generate messages. Not every field change.
- 2026-04-07: **Uniform Entity class — no mixins.** One class with all capabilities. Configuration determines what's active (state machine defined? routing rules exist? form schema referenced?). Zero overhead for inactive capabilities.
- 2026-04-07: **Real-time simplified — same associate pattern for async and real-time.** Channels are just I/O. No separate Interaction Host architecture. Non-blocking entity writes during voice (asyncio.create_task). Deep agent framework handles conversation state.
- 2026-04-07: **Rules engine resolved — associates + skills ARE the rules engine.** Per-state, per-carrier, per-LOB logic encoded in skills. Entity methods handle deterministic calculations. No separate rules engine needed.
- 2026-04-07: **Build order: hand-build 3-5 entities first, extract framework, parallelize the rest.** Framework emerges from usage, not theory.
- 2026-04-07: Entities are uniform infrastructure. Associates are the customization layer. Configuration (routing rules, product schemas, skills) determines per-org behavior. Code changes for new CAPABILITIES, not new CUSTOMERS. Scales to 1000 companies.
- 2026-04-07: For 1000 companies: uniform entity approach is better than mixins. Per-org behavior via configuration and associate skills. No code deployments for customer variation.

- 2026-04-08: **Wiring question RESOLVED — WATCHES on roles.** Actor-centric routing: "what does this role care about?" One mechanism for sequential pipelines, conditional routing, fan-out, threshold-based triggers. Configurable per org via CLI.
- 2026-04-08: **Actor spectrum — deterministic/reasoning is an interpreter choice.** The OS doesn't care how the actor decides what CLI commands to run. Same queue, same claiming, same entity changes. Associates are employees.
- 2026-04-08: **Entity polymorphism for integrations.** Outlook email IS an email entity. Integration layer collapsed into entity framework. One primitive, not two.
- 2026-04-08: **Kernel vs. domain separation.** Kernel primitives (Entity, Message, Actor, Role, Org) are the OS. Domain entities (Submission, Email, etc.) are built ON the kernel. Kernel starts bare — no insurance assumptions baked in.
- 2026-04-08: **Assignment is NOT a kernel primitive.** Messages target roles, context enables filtering. Entities can have actor reference fields. The skill decides when to assign.
- 2026-04-08: **One condition language (JSON).** Shared by watches and rules. One evaluator. No CLI shorthand — JSON everywhere.
- 2026-04-08: **Entry points → entities → kernel.** Channels (voice, chat), webhooks, API calls, polling, CLI — all create entities. Kernel takes over from there.
- 2026-04-08: **Three trigger types.** Message (watch match), schedule (creates queue items), direct invocation (real-time channels).
- 2026-04-09: **Kernel capabilities = entity methods (unified).** Reusable methods activated on entities via CLI, parameterized by per-org config (rules, lookups, thresholds). Skills orchestrate. LLM is fallback.
- 2026-04-09: **Everything is data.** Entity definitions, skills, rules, configs stored in MongoDB. OS codebase (git) is the platform. Database is the application. Environments are orgs.
- 2026-04-09: **Temporal for associate execution.** Durable workflows, crash recovery, retries. NOT for human queues. Human queues stay in MongoDB.
- 2026-04-09: **Unified queue.** MongoDB message_queue is the universal work queue. Humans and associates see the same items. Associates claim via Temporal workflow. Humans claim via UI. Same queue, same visibility, interchangeable actors.
- 2026-04-09: **OTEL baked in.** correlation_id = trace_id. Entity changes, rule evaluations, LLM calls, Temporal workflows — all spans in one trace.
- 2026-04-09: **Audit trail — changes collection.** Every mutation recorded. Append-only + hash chain for tamper evidence. Three systems (changes, message_log, OTEL) linked by trace_id.
- 2026-04-09: **Schema migration is first-class.** `indemn entity migrate` with batching, dry-run, aliases during migration window, progress, audit, rollback.
- 2026-04-09: **Rolling restart on entity type changes.** Beanie for everything, definitions from DB. CLI is ephemeral (always fresh).
- 2026-04-09: **Security: OrgScopedCollection** wrapper for defense-in-depth org isolation. AWS Secrets Manager for per-org credentials. Skill content hashing. Sandbox spec for Daytona.
- 2026-04-09: **Infrastructure:** MongoDB Atlas ($60), Temporal Cloud ($100), Railway ($30-50), S3 ($5), Grafana Cloud (free). ~$200/month MVP.

- 2026-04-10: **Integration elevated to the 6th kernel primitive** (bootstrap entity). The primitive set is now: Entity, Message, Actor, Role, Organization, Integration. Integration owns the external-world connection — provider, credentials, ownership (org or actor), lifecycle, status. Adapters are its implementation (kernel code). This isn't new mechanism — it's formal recognition of what the architecture already depended on.
- 2026-04-10: **Integration has an owner field** (`org_id` or `actor_id`). Resolves user credential management — actor-level integrations handle personal credentials (Gmail, Slack); org-level integrations handle shared credentials (Outlook, carrier APIs). Credential resolution checks actor-level first, then falls back to org-level via role permissions.
- 2026-04-10: **Credentials never live in MongoDB.** Integration stores `secret_ref` into AWS Secrets Manager. Rotation, audit, and access logging are first-class CLI operations on the Integration primitive.
- 2026-04-10: **Adapter versioning is formal.** Integration has `provider_version`. Adapter registry keyed by version. `indemn integration upgrade` migrates an Integration to a new adapter version with dry-run and validation. Resolves the external-API-change problem (Outlook Graph v1 → v2).
- 2026-04-10: **Rules have exactly two actions:** `set-fields` and `force-reasoning`. The `--veto` flag is sugar for "priority: high + action: force-reasoning." Previous proposal of five actions (including fabricated `map-lookup`, `transition`, `call-capability`) retracted — those were invented, not in the architecture.
- 2026-04-10: **Lookups stay separate from rules** (per 2026-04-09-capabilities-model-review-findings #3). Lookups are mapping tables, not conditional logic. Bulk-importable from CSV, maintained by non-technical users. Rules reference lookups when they need to map a value.
- 2026-04-10: **Domain entities are ALWAYS data.** No per-org Python files. Custom logic beyond existing kernel capabilities means contributing a new capability to the platform (kernel code). Kernel entities (Org, Actor, Role, Message, Changes, Integration) remain Python classes in git. Clean split: kernel in git, domain as data.
- 2026-04-10: **Deterministic associates collapsed into hybrid.** No separate deterministic harness. A hybrid associate whose kernel capabilities never return `needs_reasoning` is effectively deterministic. If compliance requires guaranteed LLM-free execution, a mode flag raises on `needs_reasoning` instead of falling back. One actor concept, one execution path.
- 2026-04-10: **Generic Temporal workflow confirmed** over per-step workflows. The skill is the source of truth for orchestration. Temporal wraps the generic claim → process → complete cycle for durability. Per-step workflows only for true long-running sagas with specialized per-step compensation (rare).

- 2026-04-10: **GIC retraced end-to-end against the updated kernel** — 6 primitives, Integration elevated, Temporal, unified queue, watches, --auto pattern, everything-is-data. Kernel holds up without changes. Six follow-up concerns surfaced, all usability/tooling (not architectural): coalescing for bulk events, pipeline dashboards, ephemeral entity locks, multi-LOB drafts (domain skill), queue health tooling, computed-field activation scope.
- 2026-04-10: **Base UI is auto-generated** from the primitives, 1:1 with CLI, role-scoped, admin-first. Same philosophy as the CLI: read entity definitions + role permissions + watches + activated methods, render accordingly. No bespoke per-org UI. Views: Queue, Entity Explorer, Entity Detail, Actor/Associate Management, Integration Management, Rules/Lookups, Skills, Roles/Watches, Trace/Audit, System Dashboards.
- 2026-04-10: **Two small kernel additions required for base UI**: (1) watch-level coalescing via optional `coalesce` config producing `batch_id` on messages; (2) ephemeral entity locks for surfacing "user is actively reviewing this" without blocking claims. Both additive, neither changes existing primitives.
- 2026-04-10: **Identity providers are Integrations** (reuse primitive #6). SSO support for enterprise customers configured as Integration entities with `system_type: identity_provider`. Login flow: IdP auth via adapter → validated token → actor lookup → OS session JWT. Password-based auth is a kernel-native method. SSO and password can coexist per org.
- 2026-04-10: **Authentication methods are a list on Actor.** Multiple methods per actor supported (password + MFA, SSO + password fallback, etc.). Credentials never stored inline — always reference AWS Secrets Manager. Covers humans, associates (service tokens), and Tier 3 developers (API keys) uniformly.
- 2026-04-10: **Role-grant authority is a meta-permission (`can_grant`) on named shared roles.** Admin can grant anything; team_lead can grant subset; individual roles like underwriter have no grant authority. Inline associate roles have `can_grant: null` — there's nothing to grant.
- 2026-04-10: **Role creation has two ergonomic paths** (one primitive):
  - **Path 1 (named shared)**: `indemn role create underwriter ...` — for organizational job functions humans hold (and possibly shared associates). Reusable, grantable per `can_grant`.
  - **Path 2 (inline on associate)**: `indemn actor create --type associate --permissions ... --watches ... --skill ...` — kernel implicitly creates a singleton role bound to this associate. Not listed as a named role. `can_grant: null`.
  - Resolves the asymmetry of giving each associate its own named role (awkward, singleton, not an org job title). Role stays as one primitive; ergonomics split by use case.
- 2026-04-10: **Authentication needs a focused design session.** Architecture sketch in place (methods on Actor, IdP as Integration, role-grant, lifecycle states provisioned→active→suspended→deprovisioned, bootstrap flow). Full design of MFA policy, Tier 3 self-service signup, session management specifics, platform-admin cross-org scope deferred to dedicated session.

- 2026-04-10: **EventGuard retraced end-to-end against the updated kernel** (consumer-facing real-time chat, Stripe payment with outbound charge + inbound webhook, fully autonomous flow, 351 venue deployments, policy issuance, PDF certificate generation, email/SMS delivery). Kernel holds. Validates: Integration supports both outbound and inbound, watches handle multi-actor choreography (payment→policy→certificate→delivery), real-time channel activation via direct invocation, fully autonomous flow has zero HITL, one associate serves all 351 venues via per-Deployment branding config, selective emission prevents conversation-turn watch storms.
- 2026-04-10: **One real architectural gap from EventGuard: mid-conversation event delivery to running real-time actors.** Watches generate queue messages but a running real-time associate holding an open WebSocket needs sub-second delivery of events related to its current Interaction (e.g., Stripe webhook completes → Policy issued → notify the live conversation). Proposed resolution: watches support an `actor_context` scope qualifier; kernel bridges matching watches to Temporal signals for the running actor workflow. Additive to existing watch → queue path. Needs its own focused design before implementation.
- 2026-04-10: **Integration primitive extends to inbound, not just outbound.** Webhooks arrive at `/webhook/{provider}/{integration_id}`, dispatched via Integration's adapter for validation and parsing into entity operations. Adapter interface has both outbound methods (charge, fetch, send) and inbound methods (validate_webhook, parse_webhook, auth_initiate). Documentation update needed on the integration artifact — not a new primitive.
- 2026-04-10: **Bulk operations pattern needs explicit design.** EventGuard's 351 venue deployments force the issue. Needs: batch sizing, transaction boundaries, event emission strategy, coalescing integration, progress reporting, idempotency, rollback on partial failure. Previously flagged as deferred; EventGuard is the forcing function.
- 2026-04-10: **Internal Actors vs. external entities clarified.** Actors (humans, associates, tier3 developers) authenticate and have roles. External counterparties (Customers buying insurance, retail Agents, partner Carriers) are entities without auth. Both are valid; they live in different parts of the primitive model. To document in the spec.
- 2026-04-10: **Cross-trace comparison (GIC + EventGuard)**: GIC is B2B/email/heavy-HITL/batch-burst/~7 associates. EventGuard is consumer/real-time/zero-HITL/continuous/~5 associates + high-volume deployment. Same 6 primitives serve both without modification. Validates the kernel is not secretly shaped for one workload type. A CRM retrace is the recommended third test to remove insurance-specific assumptions entirely.

- 2026-04-10: **CRM retraced against the updated kernel (third pressure test)** — Indemn's own internal CRM, generic B2B intelligence, 15 team members with 60 actor-level integrations, meeting intelligence, follow-up tracking, health monitoring, personal email/slack/calendar sync. Kernel holds. Zero insurance concepts required anywhere. Domain-agnostic claim validated cleanly.
- 2026-04-10: **New architectural addition from CRM: associates with `owner_actor_id`.** When an associate is bound to a human owner, its credential resolution checks the owner's personal integrations in addition to the associate's own. Enables personal sync associates (Craig's Gmail Sync uses Craig's Gmail integration) and delegated-action patterns. Small addition (one field + resolver check + audit + consent). Update to the Integration primitive's credential resolution model.
- 2026-04-10: **Content visibility scoping for personal-integration-derived entities.** When an Interaction is created from a personal Integration (e.g., Craig's Gmail sync produces an Interaction), metadata should be shared with the team by default but full content (body, attachments) should be owner-scoped (stored in actor-scoped S3 path). Configurable per Integration. Not a kernel addition — a privacy policy the kernel supports via owner fields.
- 2026-04-10: **Three traces is enough.** GIC (B2B insurance), EventGuard (consumer insurance), CRM (generic B2B intelligence) cover enough of the workload landscape. Every kernel design item from prior traces is exercised in CRM too — confirming they're real requirements, not single-trace quirks. Kernel deemed stable and ready to encapsulate. Next: design sessions on the open items (now 11 total), documentation updates, simplification pass, spec writing.

- 2026-04-10: **Default chat assistant baked into the base UI.** Every human actor opening the OS UI has a default associate they can chat with — bound to them via `owner_actor_id`, scoped to their roles and permissions. The assistant acts through the same CLI any other associate uses; the UI chat is just a surface. Natural extension of the "personal AI assistant per role" idea from core primitives. No new mechanism — it's a pre-configured associate automatically provisioned for every human actor. To be formalized in the base UI spec.

- 2026-04-10: **Attention elevated to a bootstrap entity.** Unifies previously separate concepts: UI soft-locks and real-time active session contexts. An Attention record is "this actor is currently attending to this entity, with this purpose, until this time." Six purposes: real_time_session, observing, review, editing, claim_in_progress. Heartbeat-maintained with TTL expiration; heartbeat updates bypass audit logging to avoid noise. Enables presence awareness, zombie session detection, capacity management, and scoped event routing.
- 2026-04-10: **Scoped watches resolved via emit-time target_actor_id.** Two scope resolution types: `field_path` (traverses an entity relationship to resolve to an actor_id — used for ownership-style scoping in CRM) and `active_context` (looks up matching Attention records — used for real-time event delivery in EventGuard). Kernel writes `target_actor_id` on the message at emission; claim queries filter by it. No runtime scope evaluation at query time. Sub-millisecond emit-time overhead.
- 2026-04-10: **Watch coalescing** for bulk-emission scenarios. Watches can declare a `coalesce` strategy (e.g., by_correlation_id with a time window) to group events from the same source into a single batched queue item. Applied after scope resolution, so coalescing is per-target-actor.
- 2026-04-10: **Runtime elevated to a bootstrap entity.** Deployable host for associate execution. Fields include kind (realtime_chat/voice/sms, async_worker), framework (deepagents, langchain, custom) + version, transport config, LLM defaults, deployment image, capacity, instance tracking. One Runtime hosts MANY Associates; Associate has `runtime_id`. Lifecycle: configured → deploying → active → draining → stopped. Makes deployment first-class, CLI-manageable, framework swappable.
- 2026-04-10: **Harness pattern: thin CLI-based glue code per kind+framework combo.** The harness is a deployable image (e.g., `indemn/runtime-voice-deepagents:1.2.0`) containing the framework, the transport library, and a small script that bridges to the OS via subprocess CLI calls. The CLI is the universal interface; no separate Python SDK. Harnesses are generic — they serve any Associate of matching kind by loading Associate config at session start. Full access to framework features (all of LiveKit, all of deepagents, sandboxes, etc.).
- 2026-04-10: **One new CLI infrastructure command: `indemn events stream`.** Streaming subcommand backed by MongoDB Change Streams. Outputs scoped events as JSON lines on stdout for a given actor/interaction. Used by harnesses to receive mid-conversation events. All other CLI operations in this design are auto-generated from entity definitions.
- 2026-04-10: **Handoff via `indemn interaction transfer --to/--to-role`.** The Interaction entity has `handling_actor_id` and `handling_role_id` fields. Transfer updates them; Runtime watches the Interaction via Change Stream, notices the change, switches between "run associate in-process" mode and "bridge to human via queue" mode. Observation is a first-class state (Attention with purpose=observing) — a human can watch an Interaction in real time before deciding to take over. Transfer to a role is also supported: any actor with the role can claim and becomes the de-facto handler.
- 2026-04-10: **Human voice clients as Integrations.** When a human takes over a live voice call, their UI uses a `voice_client` Integration (actor-owned) to join the LiveKit room (or equivalent). Same Integration primitive, same credential storage, same CLI management. No new concept — human voice participation reuses primitive #6.
- 2026-04-10: **Three-layer customer-facing flexibility.** Transport behavior (Deployment entity — per-venue branding, widget appearance, voice greeting), conversation style (Associate skill), execution environment (Runtime — framework, LLM, capacity). Merge order for per-session overrides: Runtime defaults → Associate override → Deployment override. Already supported by existing entities; documented as the flexibility model.

- 2026-04-10: **CLI and API are parallel auto-generated surfaces, not one or the other.** Correcting prior sloppy terminology where "CLI" was used to mean "universal interface." Both the CLI (Typer-based, for humans/agents/scripts via subprocess) and the API (FastAPI-based, for UIs and programmatic clients via HTTP/JSON) are auto-generated from entity definitions. Both respect the same entity permissions, auth model, and self-evident property. The **base UI uses the API**, not the CLI. Harnesses use the CLI via subprocess for convenience (small deployable scripts). Agents use whichever fits their execution model (deepagents uses CLI via `execute()` in sandbox; a custom agent could hit the API directly). `indemn events stream` is a CLI-specific command because it needs subprocess streaming semantics; the API equivalent is a WebSocket or SSE endpoint. The "universal interface" is the entity framework's auto-generated surface, which manifests as both CLI and API simultaneously.

- 2026-04-10 (session 6): **Bulk operations are a kernel-provided pattern, not a primitive and not a new bootstrap entity.** Six structural primitives remain Entity/Message/Actor/Role/Organization/Integration. Six bootstrap entities remain Org/Actor/Role/Integration/Attention/Runtime. Bulk ops compose from existing primitives: Message (queue visibility), Temporal workflow (generic `bulk_execute` engine), MongoDB transactions (per-batch atomicity), watch coalescing (rendering layer), selective emission (event preservation), OTEL + changes collection (audit).
- 2026-04-10 (session 6): **`bulk_operation_id = temporal_workflow_id`.** Coupling accepted for simplicity. Alternative (decoupled UUID) rejected as premature complexity. The operation spec beyond Temporal retention is not persisted — the entity changes themselves are fully queryable via changes collection, and for scheduled ops the spec lives in the associate's skill (persisted data). Kernel-provided `BulkOperation` entity is additive and can be added later if compliance demands.
- 2026-04-10 (session 6): **CLI verb taxonomy enforces selective emission discipline:** `bulk-create` / `bulk-transition` / `bulk-method` / `bulk-update` / `bulk-delete`. Raw field updates that should cascade through watches must go through @exposed methods and `bulk-method`. `bulk-update` is silent (no events) — reserved for data migrations and backfills. Rule of thumb: **if it should cascade, make it a method.**
- 2026-04-10 (session 6): **Scheduled and ad-hoc bulk operations use the same mechanism.** Scheduled associate skill invokes a bulk CLI command; ad-hoc CLI invocation does the same. The kernel makes no distinction. Both flow through the `bulk_execute` Temporal workflow with different triggers.
- 2026-04-10 (session 6): **Multi-entity-per-row bulk operations handled by skill code (Option α), not a DSL.** `bulk-*` CLI stays single-entity. Complex cases (EventGuard's Venue + VenueAgreement + Deployment per row) use associate skill code with per-row transactions. `bulk_apply` DSL deferred until a repeated use case forces it. Trade-off: per-row transactions instead of batched transactions for multi-entity cases (10-30s vs ~1s wall time for EventGuard's 351 venues). Acceptable for one-shot operations.
- 2026-04-10 (session 6): **Failure handling default is skip-and-continue with error list.** Permanent errors (StateMachineError, ValidationError, PermissionDenied, EntityNotFound, exhausted VersionConflict) are skipped and recorded. Transient errors (network, lock timeout, first-attempt VersionConflict) propagate and trigger Temporal retry of the whole batch activity. Workflow terminal states: `completed`, `completed_with_errors`, `failed`. Opt-in `--failure-mode=abort` for operations requiring strict all-or-nothing semantics (multi-entity imports with dependencies, admin operations).
- 2026-04-10 (session 6): **No cross-batch rollback for MVP.** Dry-run is the safety net for destructive operations. Saga compensation deferred until a specific operation type demands strict cross-batch rollback. Idempotency at entity level (state machine natural, `external_ref` for create, author-enforced for methods) enables safe Temporal replay on partial failure.
- 2026-04-10 (session 6): **Item 7 (bulk operations) from the post-trace synthesis is resolved.** Open items remaining: 8 (pipeline dashboard), 9 (queue health), 10 (authentication, own session), 4/5/6/11/12 (documentation sweep), plus simplification pass and spec writing.

- 2026-04-11 (session 6, day 2): **Pipeline Dashboard and Queue Health collapse into the base UI itself.** They are not two separate features — they are different views of one operational surface. The base UI is a projection of the system definition, not a dashboard application on top of it. Items 8 and 9 resolved together.
- 2026-04-11 (session 6, day 2): **The base UI derives from primitives.** Entities + roles + watches + permissions + integrations define what the UI shows. Adding an entity type means the UI reflects it immediately — its fields, state machine, @exposed methods, and activated kernel capabilities. No bespoke per-org dashboards for MVP. No per-entity UI code, ever.
- 2026-04-11 (session 6, day 2): **Visualization preference: tables > charts > prose, unless data is inherently graphical.** Interactive tables are the primary data surface. Charts reserved for continuous time-series where trajectory matters (rare — a table with counts and deltas usually serves better). No decoration for its own sake. Simpler is better.
- 2026-04-11 (session 6, day 2): **Forms for create/update, auto-generated from entity definitions.** Field types map to form controls. State machine visualized as "current state + available transition buttons," not a diagram.
- 2026-04-11 (session 6, day 2): **Assistant at the forefront: slim always-visible input at the top of every view.** Primary position, keyboard-focused, not a right-side panel or Cmd-K modal or floating widget. Expands to overlay conversation panel on engagement (~400-500px right-side panel, non-blocking, streaming responses, inline entity renderings using the same table/form components the rest of the UI uses). Persistent conversation thread per user. Implicit context awareness from UI-built payload per turn. Reuses default associate bound via `owner_actor_id` from session 5.
- 2026-04-11 (session 6, day 2): **Real-time by default via MongoDB Change Streams filtered by current view query and pagination.** Subscription is filter-aware and pagination-aware to avoid flooding. List views, detail views, queue views, bootstrap entity views all subscribe live. The UI is a live window into the churning system, not a series of periodic snapshots.
- 2026-04-11 (session 6, day 2): **The assistant panel is a running harness instance subscribing via `indemn events stream`** — same real-time event mechanism from the session 5 realtime-architecture design. When the user is discussing SUB-042 and SUB-042 changes mid-conversation, the assistant knows immediately. Enables "let me know when X happens" patterns without polling.
- 2026-04-11 (session 6, day 2): **Kernel aggregation capabilities for UI widgets:** `state-distribution` (count per state), `throughput` (counts over time windows with baseline comparison), `dwell-time` (avg/p50/p95 per state), `queue-depth` (pending messages per role), `cascade-lineage` (message tree by correlation_id). All read-only, callable from CLI/API/UI identically. Same pattern as auto-classify/fuzzy-search/stale-check — reusable methods activated per entity type via CLI.
- 2026-04-11 (session 6, day 2): **Bootstrap entities (Org, Actor, Role, Integration, Attention, Runtime) get the same auto-generation as domain entities.** Ops users see them as normal tables with row actions (pause, drain, cancel, rotate, close, transfer). No special treatment beyond inclusion in default navigation.
- 2026-04-11 (session 6, day 2): **Active alerting deferred.** Base UI visibility is sufficient for MVP. Human ops watches the dashboard. Active alerts added later when forcing functions and known thresholds justify the design — likely as watches on kernel entities (Runtime, Integration, message_queue depth) with actions that invoke notification Integrations.
- 2026-04-11 (session 6, day 2): **Complexity ladder: click → pattern-match → instruct → command.** Four surfaces (buttons, tables, assistant, CLI) same system, no privileged interface. Users don't strictly need to understand every widget — they can ask the assistant. Widgets exist for visibility and fast click-to-action, not exhaustive coverage.
- 2026-04-11 (session 6, day 2): **No new kernel entities for UI in MVP.** No `DashboardConfig`, `AlertConfig`, or `Widget` entity. Auto-generation covers the known workloads. Future customization is additive — added only when forcing functions appear. Craig flagged he foresees configurable widgets eventually but not at MVP.
- 2026-04-11 (session 6, day 2): **Items 8 and 9 from the post-trace synthesis resolved together.** Open items remaining: 10 (authentication, own session), 4/5/6/11/12 (documentation sweep), plus simplification pass and spec writing. Item 10 is the largest remaining architectural gap.

- 2026-04-11 (session 6, day 2 cont.): **Authentication designed end-to-end.** One new bootstrap entity: Session. Bootstrap entity count moves from 6 to 7: Org, Actor, Role, Integration, Attention, Runtime, **Session**. Six structural primitives unchanged.
- 2026-04-11 (session 6, day 2 cont.): **Session is universal across all auth types.** `type` field distinguishes user_interactive / associate_service / tier3_api / cli_automation. One validation path, one revocation mechanism, one audit trail. Write cost low because Session is created per token issuance, not per invocation.
- 2026-04-11 (session 6, day 2 cont.): **Hybrid JWT + Session model.** Short-lived access tokens (15 min default, stateless verification, platform-wide JWT signing key, `jti` in revocation list). Long-lived opaque refresh tokens (user_interactive only, stored hashed in Secrets Manager, rotated on refresh with 30s overlap window). Long-lived tokens for associate/tier3/cli: hash lookup against Session, no refresh.
- 2026-04-11 (session 6, day 2 cont.): **Five authentication method types** (reduced from initial 7): `password`, `totp`, `sso`, `token`, `magic_link`. Merged api_key + service_token into unified `token` type with `usage` field (associate_service / tier3_api_key / cli_automation). Deferred WebAuthn to post-MVP.
- 2026-04-11 (session 6, day 2 cont.): **MFA policy placement: Role-level `mfa_required` with Actor `mfa_exempt` override and Organization `default_mfa_required`.** Resolution order: actor exempt > role required > org default. Matches operational language.
- 2026-04-11 (session 6, day 2 cont.): **Fresh MFA re-verification via `@exposed(requires_fresh_mfa=N)` decorator parameter.** Small extension to existing `@exposed` mechanism for per-operation sensitivity. Auth middleware checks session.mfa_verified_at > now - N.
- 2026-04-11 (session 6, day 2 cont.): **Platform admin cross-org model refined for Craig's signal "we will be building most things for the customer."** The `_platform` system org holds Indemn staff. PlatformCollection accessor bypasses OrgScopedCollection for cross-org operations. Sessions: 4h default duration, 24h max, auto-renewable on activity with 30min idle timeout. Work-type tagging: `build | debug | incident | routine`. Per-customer notification config (notify_on_start | notify_on_every_request | daily_summary | silent). Strict scope limits (no secrets, no credential modification except audited rotation, no user impersonation). Session identity stays Indemn actor. Audit in target org's changes collection with full provenance (acting actor, home org, session ID, work type, reason).
- 2026-04-11 (session 6, day 2 cont.): **Claims refresh on role change, not full revocation.** Role revocation marks sessions `claims_stale = true`; next request auto-refreshes with new claims (no re-authentication). Role granting picks up on next natural refresh (within 15min). Full session revocation only on actor suspension or deprovisioning. User experience: permissions change reflects on next click, no login screen interruption.
- 2026-04-11 (session 6, day 2 cont.): **Default assistant in base UI inherits user's session.** The default associate (owner_actor_id = user) authenticates via the user's session JWT, not a separate service token. Audit attributed as "user X via default associate performed Y." Distinct from owner-bound scheduled associates which use own service tokens + credential resolution through the owner's Integrations.
- 2026-04-11 (session 6, day 2 cont.): **Credential storage**: Argon2id password hashes in MongoDB (non-reversible, defense-in-depth via OrgScopedCollection). Raw secrets (TOTP seeds, refresh tokens, backup codes, API key pre-hashes) in AWS Secrets Manager. Consistent with session 4 security decisions.
- 2026-04-11 (session 6, day 2 cont.): **Recovery flows**: password reset via email magic_link (revokes all sessions), MFA recovery via backup codes (pre-generated at enrollment, hashed in Secrets Manager) or admin reset (requires `can_grant` on target's role), emergency access via platform admin intervention. **No back doors, no security questions, no SMS.**
- 2026-04-11 (session 6, day 2 cont.): **Pre-auth rate limiting in kernel auth middleware.** Counts failed attempts keyed by (ip_address, email_hash), Change Stream sync for cross-instance coordination. Per-org configurable thresholds (default: 5/10min → 30min lockout). Audit every failure + lockout trigger.
- 2026-04-11 (session 6, day 2 cont.): **Revocation cache**: in-memory per API instance, invalidated via Change Stream on Session `status_changed[to=revoked]`, bootstrapped on instance startup from the last 15 minutes of revoked sessions. TTL eviction at 15 minutes (matches max access token lifetime).
- 2026-04-11 (session 6, day 2 cont.): **Auth events in changes collection** with specific event types (`auth.login_attempt`, `auth.session_created`, `auth.session_refreshed`, `auth.session_revoked`, `auth.mfa_enrolled`, `auth.mfa_challenged`, `auth.mfa_reset`, `auth.password_changed`, `auth.method_added`, `auth.method_removed`, `auth.role_granted`, `auth.role_revoked`, `auth.lifecycle_transitioned`, `auth.platform_admin_access`, `auth.brute_force_lockout`). Same tamper-evident hash chain as entity mutations. Surfaced via base UI "Auth Events" view and `indemn audit auth` CLI.
- 2026-04-11 (session 6, day 2 cont.): **Tier 3 self-service signup MVP scope**: org + first admin + password + email verification + first API key. NOT in MVP: billing, plans, email domain verification, sub-user invitation, OAuth app management.
- 2026-04-11 (session 6, day 2 cont.): **First-org bootstrap via stdout magic_link token.** `indemn platform init --first-admin email@indemn.ai` prints one-time token to stdout (no email Integration exists yet). First admin uses it to complete setup. After configuring platform email delivery, subsequent invitations use email.
- 2026-04-11 (session 6, day 2 cont.): **Item 10 (authentication) from the post-trace synthesis is resolved.** Open items remaining: 4/5/6/11/12 (documentation sweep), simplification pass, spec writing. All architectural gaps closed.

- 2026-04-13 (session 6, day 3): **Documentation sweep complete — items 4, 5, 6, 11, 12 from the post-trace synthesis resolved.** Inbound webhook dispatch formalized (kernel endpoint + adapter interface extension). Internal Actors vs external counterparty entities distinction made explicit. Computed field mapping scope clarified (method activation config vs Lookups). `owner_actor_id` on associates formalized with consent/revocation/transfer lifecycle. Content visibility scoping via `content_visibility` field on Integration (full_shared / metadata_shared / owner_only, default actor-owned=metadata_shared).
- 2026-04-13 (session 6, day 3): **All post-trace synthesis items resolved (4, 5, 6, 7, 8, 9, 10, 11, 12).** Remaining: simplification pass, spec writing, stakeholder engagement. The architecture is complete.

- 2026-04-13 (session 6, day 3): **Simplification pass complete.** Two architectural simplifications accepted: (1) watch coalescing removed from kernel → UI rendering concern (group by correlation_id at display time, no coalesce field on watches, no batch_id on messages), (2) rule evaluation traces → metadata in changes collection entries (no separate evaluation trace collection). Runtime stays as kernel entity per Craig. "Bootstrap entity" renamed to "kernel entity" for clarity. WebAuthn and per-operation MFA re-verification confirmed deferred. Schema migration, all 5 Attention purposes, content visibility scoping, and rule groups with lifecycle all kept in MVP per Craig's pushback.
- 2026-04-13 (session 6, day 3): **Systematic gap analysis identified 6 design categories beyond kernel architecture that need design sessions before the specification can be written:** (1) Infrastructure & Deployment, (2) Development Workflow, (3) Dependencies & Resilience, (4) Operations, (5) Transition & Coexistence, (6) Domain Modeling Process. Compliance and economics can proceed in parallel with building.
- 2026-04-13 (session 6, day 3): **The deliverable is one document with layered depth**, not separate documents. Sections 1-2 are the white paper (vision + architecture, readable by anyone). Sections 3-9 are the specification (authentication, infrastructure, dev workflow, operations, domain modeling, transition, dependencies — buildable by engineers). Section 10 is the build sequence (derived from everything above, written last). One source of truth. No drift between documents.
- 2026-04-13 (session 6, day 3): **The order going forward:** design the 6 remaining gaps (same session style: principles, forcing functions, design, pressure test, artifact) → write the specification document (consolidate all artifacts into the single layered document) → derive the build sequence (section 10, flows from sections 1-9) → stakeholder engagement (Ryan → Dhruv → George → Kyle/Cam) → build (first use case: CRM dog-fooding and/or GIC).

## Open Questions
- **Single kernel specification document** — 40+ artifacts need consolidation into one actionable spec
- **GIC end-to-end retrace** — initial trace was before Temporal, unified queue, everything-is-data. Needs fresh trace with final architecture.
- **Simplification pass** — Craig: "a lot of this can be simplified." The theoretical discussions may have over-specified.
- **Build order** — what specifically gets built first, in what order, with what acceptance criteria
- **Testing/debugging CLI** — commands sketched but not fully specified
- **Declarative system definition** — YAML manifests for `indemn system apply` not finalized
- **Bulk operations** — `indemn entity import` concept raised but not designed
- **Rule composition details** — AND/OR/NOT, lookups vs. rules, veto rules, rule groups — conceptually decided, not specified
- **Operational surface** — the full set of CLI commands the OS exposes
- Tier 3 pricing model — API/usage-based, needs brainstorming
- How the new website (Dhruv + Drew building v2) aligns with the OS vision
- Product showcases — need to be refined and aligned with the OS vision
- How current customers eventually transition to the OS (low priority)
- Revenue projections with OS model vs. current model
- Final vision document consolidation — 40+ artifacts need to become one narrative
- Roles and time allocations — need deeper work with Craig
- Champion strategy — how Craig presents and rolls out the vision to the company
- Stakeholder engagement (Ryan → Dhruv → George → Kyle/Cam) — designed but not started
