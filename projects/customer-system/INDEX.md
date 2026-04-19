# Customer System

The first real system built on the Indemn Operating System. A customer delivery/success system that becomes the source of truth for customer information — who our customers are, what we've built for them, what state things are in, and what needs attention.

## Status

**Session 2026-04-19 — Customer system live on the OS. UI evaluation complete. 20 gaps identified.**

### What's Done
- All 14 entity definitions created and deployed (3 reference + 11 domain)
- 14 entity skills auto-generated (self-evidence property verified)
- 13 team members created as human actors + team_member role granted to all
- Reference data seeded: 7 stages, 4 outcome types
- Bulk data imported: 24 associate types, 2 conferences, 87 companies, 92 contacts
- 3 kernel bugs found and fixed (CLI trailing slash, Decimal serialization insert + update paths)
- State transitions verified E2E (Company: customer → expanding → customer)
- Comprehensive browser evaluation of UI: 10 things working, 20 gaps documented with priority tiers

### What's Next
1. **Resolve 20 UI gaps** — Tier 1 (assistant, ObjectId display, nav filtering) then Tier 2 (search, enums, relationship pickers, transition confirmation, changes rendering, pagination)
2. **Phase F: Watches + Automation** — design with Craig after UI gaps are resolved
3. **Fix bulk-create pipeline** — org_id propagation + type coercion in Temporal

### Key Numbers
| Entity | Count |
|--------|-------|
| Companies | 87 |
| Contacts | 92 |
| Associate Types | 24 |
| Conferences | 2 |
| Stages | 7 |
| Outcome Types | 4 |
| Human Actors | 14 |
| Roles | 4 |
| Entity Definitions | 14 (customer) + 3 (test) |
| Auto-Generated Skills | 24 |

## External Resources

| Resource | Type | Link |
|----------|------|------|
| OS API | Railway | https://indemn-api-production.up.railway.app |
| OS UI | Railway | https://indemn-ui-production.up.railway.app |
| Chat Runtime | Railway | wss://indemn-runtime-chat-production.up.railway.app/ws/chat |
| indemn-os repo | GitHub | craig-indemn/indemn-os (main branch) |
| OS repo | GitHub | os-roadmap branch |

## Artifacts

| Date | Artifact | Ask |
|------|----------|-----|
| 2026-04-14 | [problem-statement](artifacts/2026-04-14-problem-statement.md) | 7 concepts with evidence, success criteria, risks |
| 2026-04-14 | [domain-model-thinking](artifacts/2026-04-14-domain-model-thinking.md) | Entity criteria, kernel vs domain boundary |
| 2026-04-14 | [phase-1-domain-model](artifacts/2026-04-14-phase-1-domain-model.md) | 14 entities with fields, state machines, relationships |
| 2026-04-19 | [known-issues](artifacts/2026-04-19-known-issues.md) | Kernel bugs (3 fixed, 5 open) + data quality notes |
| 2026-04-19 | [ui-evaluation](artifacts/2026-04-19-ui-evaluation.md) | Comprehensive browser evaluation — 10 working, 20 gaps with priority tiers |

## Decisions

- 2026-04-14: Company entity covers full lifecycle from prospect through churned
- 2026-04-14: Deal deferred to Phase 2 — Company carries stage and ARR directly
- 2026-04-14: AI populates everything — system designed for extraction, not manual entry
- 2026-04-14: One role for now (team_member, full access)
- 2026-04-19: Bulk import done via individual creates (bypassed Temporal bulk-create due to org_id propagation bug)
- 2026-04-19: how_met enum values mapped from 20+ conference-specific values to 7 canonical values during import
- 2026-04-19: UI evaluation confirms self-evidence property works but usability needs 20 gaps resolved before team can use daily

## Open Questions

- How meeting transcripts flow from Google Drive into the system (integration adapter design)
- How Slack notifications work (integration adapter design)
- Watch configurations per role (deferred until automation design — Phase F)
- When Deal entity becomes necessary (forcing function: company with multiple concurrent opportunities)
- How to configure the default assistant associate for each org
