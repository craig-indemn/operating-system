# Customer System

The first real system built on the Indemn Operating System. A customer delivery/success system that becomes the source of truth for customer information — who our customers are, what we've built for them, what state things are in, and what needs attention. More broadly: the company's operating system. Everything Indemn does should be in this system.

Kyle is pressing for this. It doubles as the proving ground for the OS domain modeling process.

## Status

**Session 2026-04-14 (session 1) — Problem statement complete. Domain model in progress.**

Context gathering complete — read Kyle's 28-file context package, CRM InsurTechNY sheet, 10+ meeting transcripts (Kyle, Cam, George, Peter, Ganesh), Craig's notes, and CTO thinking worktree. Problem statement artifact written with 7 concepts. Domain model thinking started — established entity criteria for the OS, identified 10 domain entities + 3 reference entities, clarified what the kernel handles vs. what needs modeling.

### What's Done
- All source materials gathered and inventoried (28 Kyle docs, CRM sheet, 10+ transcripts, Ganesh's repo link)
- Problem statement with 7 concepts, evidence, success criteria, risks
- Entity criteria framework for OS domain modeling (7 tests)
- Entity candidate list: Company, Contact, Deal, Implementation, Task, Playbook, Associate Deployment, Outcome, Meeting, Conference + reference entities (Associate Type, Outcome Type, Stage)
- Clarified kernel vs. domain boundary (activity log = changes collection, ownership = roles, notifications = watches)

### What's Next
1. **Refine entity attributes and relationships** — for each entity, define fields, state machines, and how they connect. Driven by "what are we trying to do" (source of truth, delivery tracking, pipeline, value/ROI)
2. **Resolve open design questions** — Company lifecycle vs. Deal stages vs. Implementation stages; Meeting as entity with Integration sync; Conference → Company lead flow; Playbook → Implementation relationship; Usage data sourcing
3. **Share problem statement with Kyle and Cam** for alignment (CTO framework Phase 5)
4. **Formalize the entity criteria and domain modeling process** as a reusable OS skill

## External Resources

| Resource | Type | Link |
|----------|------|------|
| Indemn CRM InsurTechNY | Google Sheet | `1B3QnzfS8IEM7cMN3ar9gSFRw8K8_viFmH-dEajQ9tQg` |
| Customer Success Context Package | Google Drive Folder | `12qo6eicpSvKNuJyafUs9qn1kdJY0OkC7` |
| Customer OS — Where We Are | Google Doc | `1dAtib-y9d5I-O9WzW8PON2ofxVKEkzhI7cXwZyk9Kxk` |
| Branch as Template | Google Doc | `1yYLRgfk1TbSNraNW9aoJ0yp6j7lCdcf8h2l8xwRSFdA` |
| Pipeline Source of Truth Spec | Google Doc | `14L6goa_P-j3bT0-YeD8qVviFHJv4nJ4wIWFGJE0tyGI` |
| Pipeline Schema (Prisma) | Google Doc | `1Fim6_FYmmPdx4Ww_df1TvCIWh48oA8e6pNbRofFGFbI` |
| Ganesh's Implementation Playbook | GitHub | `ganesh-iyer/implementation-playbook` (live: implementation-playbook.vercel.app) |
| CTO Operating Framework | Local | cto-thinking worktree: projects/cto-operating-framework/ |
| Product Vision (OS spec) | Local | projects/product-vision/ |

## Artifacts

| Date | Artifact | Ask |
|------|----------|-----|
| 2026-04-14 | [context/craigs-brain-dump](artifacts/context/2026-04-14-craigs-brain-dump.md) | Record Craig's raw notes from conversations with Kyle, George, Ganesh |
| 2026-04-14 | [context/source-inventory](artifacts/context/2026-04-14-source-inventory.md) | Complete inventory of all source materials — docs, sheets, transcripts, repos |
| 2026-04-14 | [problem-statement](artifacts/2026-04-14-problem-statement.md) | Comprehensive problem statement — 7 concepts with evidence, success criteria, risks, and phasing |
| 2026-04-14 | [domain-model-thinking](artifacts/2026-04-14-domain-model-thinking.md) | Entity criteria framework, kernel vs domain boundary, design principles |
| 2026-04-14 | [system-capabilities](artifacts/2026-04-14-system-capabilities.md) | Comprehensive capabilities list — 17 areas, ~130 capabilities, attributed to sources |
| 2026-04-14 | [vision-and-trajectory](artifacts/2026-04-14-vision-and-trajectory.md) | Full vision document for Kyle — problem, capabilities by phase, trajectory, what he gets first |
| 2026-04-14 | [phase-1-domain-model](artifacts/2026-04-14-phase-1-domain-model.md) | Phase 1 spec — 14 entities with fields, state machines, relationships, designed from scratch |

## Decisions

- 2026-04-14: This is the first implementation on the Operating System — it will prove and refine the OS domain modeling process
- 2026-04-14: Follows the CTO Operating Framework (problem-first, from Ryan coaching) — currently in Phase 1-3 (problem identification, concept decomposition, individual feedback collection)
- 2026-04-14: Phase 1 deliverable is an artifact Kyle can iterate on — problem statements, required capabilities, domain model thinking
- 2026-04-14: Company entity covers the full lifecycle from prospect/lead through customer through churned — one entity, not separate Prospect and Customer entities. Kyle's Pipeline Source of Truth spec confirms: one system for pipeline AND customers
- 2026-04-14: Playbook is an entity, not a Skill — it's interactive data you add to and refine. Skills are systematic procedures. Playbooks may generate skills for associates.
- 2026-04-14: Associate Type is a full entity (not just a reference lookup) because it's edited over time as the product evolves
- 2026-04-14: The kernel handles activity logging (changes collection), ownership (roles), notifications (watches), and audit (changes collection) — these are NOT modeled as domain entities
- 2026-04-14: Established a 7-test entity criteria framework for OS domain modeling: Identity, Lifecycle, Independence, Not Kernel Mechanism, CLI Test, Watchable, Multiplicity. This should become part of the OS domain modeling skill.

## Open Questions

- Company lifecycle vs. Deal stages vs. Implementation stages — one state machine or three?
- Meeting as entity with Integration sync from existing Meeting Intelligence DB, or separate?
- Conference → Company lead flow — how do leads transition from conference context to main pipeline?
- Playbook → Implementation — copy steps as tasks, or reference and track against?
- Usage data on Associate Deployment — sourced via Integration with Observatory?
- ROI/Value granularity on Outcome — per outcome type per company, or per associate deployment?
- How to formalize the domain modeling process as a reusable OS skill
