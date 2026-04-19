# Customer System

The first real system built on the Indemn Operating System. A customer delivery/success system that becomes the source of truth for customer information — who our customers are, what we've built for them, what state things are in, and what needs attention.

## Status

**Session 2026-04-19 — Customer system live. Tier 1 + Tier 2 UI gaps resolved. 9 of 20 gaps fixed.**

### What's Done
- All 14 entity definitions created and deployed (3 reference + 11 domain)
- 14 entity skills auto-generated (self-evidence property verified)
- 13 team members created as human actors + team_member role granted to all
- Reference data seeded: 7 stages, 4 outcome types
- Bulk data imported: 24 associate types, 2 conferences, 87 companies, 92 contacts
- 3 kernel bugs found and fixed (CLI trailing slash, Decimal serialization insert + update paths)
- Comprehensive browser evaluation: 10 working, 20 gaps documented with priority tiers
- **Tier 1 gaps resolved (3/3):**
  - G-1: Assistant wired and working — OS Assistant actor with 23 skills, dynamic discovery, full chat flow verified
  - G-2: ObjectIds resolve to human names in list views and detail sidebar
  - G-3: Navigation cleaned — domain entities, system entities grouped; infrastructure hidden
- **Tier 2 gaps resolved (6/6):**
  - G-4: Search box + state filter dropdown on list views
  - G-5: Pagination (50/page, Previous/Next controls)
  - G-6: Enum fields render as dropdowns (enum_values check before type switch)
  - G-8: Transition buttons removed from list rows (detail only)
  - G-10: Transition confirmation dialog with entity name
  - G-11: Changes timeline fixed (was querying wrong endpoint, now uses trace API)
  - G-12: Entity pickers show resolved names, dropdown on focus, clear button
  - G-14: State color coding for all domain states (customer, prospect, churned, etc.)
- State transitions verified E2E (Company: customer → expanding → customer)
- Comprehensive browser evaluation of UI: 10 things working, 20 gaps documented with priority tiers

### What's Next
1. **Tune assistant** — CLI command syntax in skills, context awareness from current view
2. **Phase F: Watches + Automation** — design with Craig
3. **Resolve Tier 3 UI gaps (11 items)** — date pickers, column selection, URL navigation, bulk actions, observability dashboards, real-time updates, etc.
4. **Fix bulk-create pipeline** — org_id propagation + type coercion in Temporal
5. **Test new entity creation via UI** — verify "+ New Company" form works with enum dropdowns and entity pickers

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
