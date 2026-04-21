# Customer System

The first real system built on the Indemn Operating System. A customer delivery/success system that becomes the source of truth for customer information — who our customers are, what we've built for them, what state things are in, and what needs attention. More broadly: the company's operating system. Everything Indemn does should be in this system.

Kyle is pressing for this. It doubles as the proving ground for the OS domain modeling process.

## Status

**Session 2026-04-21 (roadmap session) — Meeting ingestion pipeline built E2E. Employee entity seeded. Actors cleaned up.**

Google Meet API adapter captures everything: conference records, structured transcripts (speaker+timestamp, 30-day expiry), Gemini smart notes, recordings, Calendar attendees. 20 meetings ingested for April 20-21. 15 employees seeded from Google Admin SDK + Slack + Actor linkage. 11 junk actors deleted, 3 fixed, 3 created. `indemn meeting fetch-new` works end-to-end. `fetch_new` kernel capability is a new generic pattern (collection-level, creates entities from external systems).

**Session 2026-04-21 (customer-system session) — P0 + P1 complete. System ready for team.**

Read Kyle's EXEC folder (PLAYBOOK-v2, data dictionaries, 6 leads, MAP) and Cam's Proposals folder (6 customer proposals). Deal entity extended, SuccessPhase entity created, 6 deals populated. P0: trace bug, deep links, Kyle login, activity feed. P1: detail view with inline editing + side panel, custom domains (os.indemn.ai + api.os.indemn.ai), CLI published (v0.1.0 on GitHub), repo setup with README + getting-started + white paper + domain-modeling skill + `indemn init` with Session Startup protocol.

**Previous: Session 2026-04-20** — UI polished (15 improvements), assistant refactored to split pane with streaming + entity rendering. CI fully green.

**Previous: Session 2026-04-14/15 (session 1)** — Design and data prep. Full context gathered, problem statement, domain model, data CSVs prepared.

### What's Done
- All source materials gathered and inventoried (28 Kyle docs, CRM sheet, 10+ transcripts, Ganesh's repo)
- Problem statement: 7 concepts with evidence, success criteria, risks
- System capabilities: 17 functional areas, ~130 specific capabilities attributed to sources
- Vision & trajectory document: phased roadmap, shared with Kyle and Cam
- Phase 1 domain model: 14 entities (11 domain + 3 reference), fields, state machines, relationships
- Entity criteria framework for OS domain modeling (7 tests)
- Data prep: 87 companies, 92 contacts, 24 associate types, 2 conferences — imported and live
- 14 human actors with team_member role
- UI: auto-generated views, search/filter/sort/pagination, state transitions, changes timeline, assistant split pane, activity feed, inline editing, detail panel
- **Meeting ingestion pipeline**: Google Meet API → Meeting entities with transcripts, notes, participants, recordings
- **Employee entity**: 15 team members seeded with Google IDs, Slack IDs, Actor linkage
- **Deal entity**: 6 active deals for Kyle's prospects (FoxQuilt, Alliance, Amynta, Rankin, Tillman, O'Connor)
- **SuccessPhase entity**: created, ready for per-deal phase data
- **Custom domains**: os.indemn.ai (UI), api.os.indemn.ai (API)
- **CLI v0.1.0 published**: install script + GitHub release
- **`fetch_new` kernel capability**: generic collection-level pattern for entity ingestion from external systems
- **Google Workspace Integration**: domain-wide delegation, Meet API + Calendar API + Admin SDK + Drive API

### What's Next
1. **Fix Kyle actor** — re-set password on correct actor ID (cleanup deleted the old one)
2. **Employee resolution in meetings** — match participants to Employees + Contacts, populate team_members/contacts fields
3. **Meeting classification** — customer vs internal, link to Companies
4. **Extraction associate** — process meetings into Tasks, Decisions, Signals, Commitments
5. **Full 30-day meeting backfill** — currently only April 20-21 ingested
6. **Kyle's prospect dashboard** — Deals + Tasks + assignees + due dates
7. **SuccessPhase data** — populate when phase info comes from Kyle syncs
8. **Staleness detection** — watches not configured yet
9. **UI: `[object Object]` fix** — participants list field renders as `[object Object]` in table

### Key Numbers
| Entity | Count |
|--------|-------|
| Companies | 88 (87 + Amynta) |
| Contacts | 92 |
| Deals | 6 |
| Meetings | 20 (April 20-21) |
| Employees | 15 |
| Human Actors | 15 (cleaned up) |
| Associate Types | 24 |
| Conferences | 2 |
| Stages | 7 |
| Outcome Types | 4 |
| Entity Definitions | ~20 (domain + reference + new) |

## External Resources

| Resource | Type | Link |
|----------|------|------|
| OS API | Railway | https://api.os.indemn.ai |
| OS UI | Railway | https://os.indemn.ai |
| Chat Runtime | Railway | wss://indemn-runtime-chat-production.up.railway.app/ws/chat |
| indemn-os repo | GitHub | craig-indemn/indemn-os (main branch) |
| OS repo | GitHub | os-roadmap branch |
| Kyle's EXEC docs | Local | artifacts/context/kyle-exec/ |
| Cam's Proposals | Google Drive | Folder `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph` |
| Shared folder (Kyle + Cam) | Google Drive | `1KKH8juzCqVyRQ36h72nnB9Djdjy8m_j1` |
| White Paper PDF | Google Drive | `1Cr_F_K3a_I_iul7HgJqXv1IY8KieyS40` |
| Indemn CRM InsurTechNY | Google Sheet | `1B3QnzfS8IEM7cMN3ar9gSFRw8K8_viFmH-dEajQ9tQg` |

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
| 2026-04-19 | [known-issues](artifacts/2026-04-19-known-issues.md) | Kernel bugs (3 fixed, 5 open) + data quality notes |
| 2026-04-19 | [ui-evaluation](artifacts/2026-04-19-ui-evaluation.md) | Comprehensive browser evaluation — 10 working, 20 gaps with priority tiers |
| 2026-04-19 | [demo-readiness](artifacts/2026-04-19-demo-readiness.md) | CEO demo assessment — recommended flow, verified features, 14 known limitations for post-demo |
| 2026-04-20 | [session-handoff](artifacts/2026-04-20-session-handoff.md) | Full handoff — reading protocol, pre-flight, architecture, what works, what needs work |
| 2026-04-20 | [ui-and-assistant-session](artifacts/2026-04-20-ui-and-assistant-session.md) | UI polish (15 improvements) + assistant UX refactor (split pane, streaming, entity rendering) |
| 2026-04-20 | [meeting-ingestion-plan](artifacts/2026-04-20-meeting-ingestion-plan.md) | Meeting ingestion + prospect delivery plan — entity refinement, Google adapter research |
| 2026-04-21 | [meeting-ingestion-checkpoint](artifacts/2026-04-21-meeting-ingestion-checkpoint.md) | Mid-session checkpoint — all knowledge, decisions, open questions about meeting ingestion |
| 2026-04-21 | [meeting-ingestion-session](artifacts/2026-04-21-meeting-ingestion-session.md) | Full session record — adapter rewrites, entity work, data quality audit |
| 2026-04-21 | [session-handoff (customer-system)](artifacts/2026-04-21-session-handoff.md) | Parallel session handoff — Deal entity, SuccessPhase, UI work, domains, CLI |
| 2026-04-21 | [context/kyle-exec/](artifacts/context/kyle-exec/) | Kyle's EXEC documents — playbook, data dictionaries, prospect list, MAP |

## Decisions

- 2026-04-14: This is the first implementation on the Operating System — proves and refines the OS domain modeling process
- 2026-04-14: Company entity covers the full lifecycle from prospect through churned
- 2026-04-14: AI populates everything — system designed for extraction, not manual entry
- 2026-04-14: One role for now (team_member, full access)
- 2026-04-14: Meeting intelligence (Decisions, Commitments, Signals, Tasks) are separate entities, not fields on Meeting
- 2026-04-14: Task is unified across all sources (meetings, implementations, manual) — one entity, one queue
- 2026-04-20: Assistant is a resizable split pane, not an overlay — peer to entity views
- 2026-04-20: UI deploys require manual `railway up` — not auto-deploy from git push
- 2026-04-21: Google Workspace adapter uses Meet REST API as primary discovery (not Drive filename search)
- 2026-04-21: `fetch_new` is a collection-level kernel capability — generic pattern for any entity type
- 2026-04-21: Meeting entity is agnostic to Google — adapter maps Meet/Calendar/Drive data to Meeting fields
- 2026-04-21: One associate for full meeting pipeline — fetch + extract (not split into two)
- 2026-04-21: Employee entity is domain data (customer success system), linked to Actor (OS primitive) via actor_id
- 2026-04-21: Participants field stores structured data (name, user_id, email, join/leave, attended/invited)
- 2026-04-21: Calendar attendees merged with Meet participants — shows both who was invited and who joined
- 2026-04-21: Company matching and meeting classification are post-processing (associate job, not adapter)
- 2026-04-21: Deal entity extended with deal_id, next_step, next_step_owner, use_case, proposal_candidate
- 2026-04-21: SuccessPhase entity — per-deal phased progression with entry criteria and go/no-go signals

## Open Questions

- When to do full 30-day meeting backfill (Meet API conference records expire after 30 days)
- How Granola meeting data integrates (some meetings use Granola instead of Google's native transcription)
- How to handle meetings where nobody enabled recording/transcription (process issue)
- SuccessPhase data — what phases look like for each deal type
- Staleness detection thresholds — what's "stale" for each entity type
- UI rendering of nested dict lists (participants field shows `[object Object]`)
