# Customer System

The first real system built on the Indemn Operating System. A customer delivery/success system that becomes the source of truth for customer information — who our customers are, what we've built for them, what state things are in, and what needs attention. More broadly: the company's operating system. Everything Indemn does should be in this system.

Kyle is pressing for this. It doubles as the proving ground for the OS domain modeling process.

## Status

**Session 2026-04-21 (session 2) — Kyle's deals live, UI overhauled, P0 complete, P1 detail view shipped.**

Read Kyle's EXEC folder (PLAYBOOK-v2, data dictionaries, 6 leads, MAP) and Cam's Proposals folder (6 customer proposals). Deal entity extended with 5 new fields, SuccessPhase entity created, Kyle's 6 close-now deals populated with real data. P0 items resolved: trace API bug, deep links, Kyle login, global activity feed. P1 detail view: read mode with inline editing + side panel from list view.

**Previous: Session 2026-04-14/15 (session 1)** — Design and data prep. Full context gathered, problem statement, domain model, data CSVs prepared.

### What's Done
- All source materials gathered and inventoried (28 Kyle docs, CRM sheet, 10+ transcripts, Ganesh's repo)
- Problem statement: 7 concepts with evidence, success criteria, risks
- System capabilities: 17 functional areas, ~130 specific capabilities attributed to sources
- Vision & trajectory document: phased roadmap, shared with Kyle and Cam
- Phase 1 domain model: 14 entities (11 domain + 3 reference), fields, state machines, relationships
- Entity criteria framework for OS domain modeling (7 tests)
- Design decisions: Deal deferred to Phase 2, Company carries pipeline stage directly, Playbook is an entity not a Skill, one role (team_member) for now
- Data prep: 87 companies, 92 contacts, 24 associate types, 2 conferences — merged, deduplicated, validated CSVs ready for bulk import
- Setup scripts: 5 scripts (bootstrap, actors, roles, entity definitions, seed/import) ready to run when kernel is up
- White paper Origin section revised and shared as branded PDF
- Automations scoped (meeting intelligence, staleness monitor, meeting prep) but deferred until data is live

### What's Next
1. **Build the OS kernel** (parallel session) — entity framework, CLI, API, watches, auth
2. **Run setup scripts** — stand up the customer system on the OS
3. **Validate the source of truth** — team starts using it, data quality improves
4. **Design and build automations** — meeting intelligence extraction, staleness monitoring, Slack notifications
5. **Formalize the domain modeling process** as a reusable OS skill (document what we learned)

## External Resources

| Resource | Type | Link |
|----------|------|------|
| Shared folder (Kyle + Cam) | Google Drive | `1KKH8juzCqVyRQ36h72nnB9Djdjy8m_j1` |
| White Paper PDF | Google Drive | `1Cr_F_K3a_I_iul7HgJqXv1IY8KieyS40` |
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
| 2026-04-14 | [problem-statement](artifacts/2026-04-14-problem-statement.md) | Comprehensive problem statement — 7 concepts with evidence, success criteria, risks |
| 2026-04-14 | [domain-model-thinking](artifacts/2026-04-14-domain-model-thinking.md) | Entity criteria framework, kernel vs domain boundary, design principles |
| 2026-04-14 | [system-capabilities](artifacts/2026-04-14-system-capabilities.md) | Comprehensive capabilities list — 17 areas, ~130 capabilities, attributed to sources |
| 2026-04-14 | [vision-and-trajectory](artifacts/2026-04-14-vision-and-trajectory.md) | Full vision document for Kyle — problem, capabilities by phase, trajectory |
| 2026-04-14 | [phase-1-domain-model](artifacts/2026-04-14-phase-1-domain-model.md) | Phase 1 spec — 14 entities with fields, state machines, relationships |

## Data

| File | Records | Purpose |
|------|---------|---------|
| data/import/companies-merged.csv | 87 | Companies — merged from Pipeline API, CRM sheet, Portfolio Overview, Customer Profiles, Team Allocation |
| data/import/contacts-merged.csv | 92 | Contacts — merged from CRM sheet, Pipeline API, Customer Profiles |
| data/import/conferences.csv | 2 | InsurTechNY Spring 2026 + ALER26 Spring 2026 |
| data/import/associate-types.csv | 24 | Four Outcomes Product Map catalog |
| data/import/implementations-existing.csv | 20 | Phase 2 data from Pipeline API |
| data/setup/01-bootstrap.sh | — | Create org and first admin |
| data/setup/02-actors.sh | 13 | Create team members |
| data/setup/03-roles.sh | 1 | Create team_member role, grant to all |
| data/setup/04-entities.sh | 14 | Define all entity types with fields and state machines |
| data/setup/05-seed.sh | — | Seed reference data and bulk import CSVs |

## Decisions

- 2026-04-14: This is the first implementation on the Operating System — proves and refines the OS domain modeling process
- 2026-04-14: Follows the CTO Operating Framework (problem-first, from Ryan coaching) — Phase 1-3 complete (problem identification, concept decomposition, individual feedback)
- 2026-04-14: Company entity covers the full lifecycle from prospect through churned — one entity, one continuum. Kyle's Pipeline Source of Truth spec confirms: one system for pipeline AND customers
- 2026-04-14: Deal entity deferred to Phase 2 — Company carries stage and ARR directly. Deal added when a company has multiple concurrent opportunities (near-zero effort to add later on the OS)
- 2026-04-14: Playbook is an entity, not a Skill — interactive data you add to and refine. Skills are systematic procedures. Playbooks may generate skills.
- 2026-04-14: Associate Type is a full entity (not just a reference lookup) — edited over time as the product evolves
- 2026-04-14: The kernel handles activity logging (changes collection), ownership (roles), notifications (watches), and audit — NOT modeled as domain entities
- 2026-04-14: Established 7-test entity criteria: Identity, Lifecycle, Independence, Not Kernel Mechanism, CLI Test, Watchable, Multiplicity
- 2026-04-14: AI populates everything — system designed for extraction, not manual entry. Enums over free text.
- 2026-04-14: Meeting intelligence (Decisions, Commitments, Signals, Tasks) are separate entities, not fields on Meeting — independently queryable and watchable
- 2026-04-14: Task is unified across all sources (meetings, implementations, manual) — one entity, one queue
- 2026-04-14: One role for now (team_member, full access). Role differentiation comes with automations.
- 2026-04-15: Automations deferred until data is live — meeting intelligence extraction, staleness monitoring, and meeting prep are scoped but not built yet
- 2026-04-15: Source of truth first, automations second. Get the data in, team starts using it, then layer on intelligence.

## Open Questions

- How to formalize the domain modeling process as a reusable OS skill (document what we learned in this session)
- When Deal entity becomes necessary (forcing function: company with multiple concurrent opportunities)
- Specific watch configurations per role (deferred until automations phase)
- How meeting transcripts flow from Google Drive into the system (integration adapter design)
- How Slack notifications work (integration adapter design)
- How to handle the Pipeline API data going forward — sunset it or keep as parallel system during transition
