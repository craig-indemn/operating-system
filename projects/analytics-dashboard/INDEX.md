# Analytics Dashboard

Add a usage analytics overview to the Indemn Observatory — organization and agent usage metrics broken out by month for the last 6 months, sourced from the tiledesk MongoDB database. Provides Kyle with visibility into platform adoption and activity trends.

## Status
Session 2026-02-24-a complete — research phase done, ready for spec. Verified billing-aligned usage filter (`status: 1000, isTestMode != true, depth > 2`) matches Stripe numbers. Pulled clean org and agent usage tables. Explored Observatory architecture (React 19 + FastAPI + Recharts). Created COP-326 in Linear. Updated MongoDB skill with billing filter patterns.

**Next session**: Spec the feature — UI placement, date range interaction, API design, agent drill-down. The overview page has a date range selector that drives all queries — the usage table should be dynamic based on that range, bucketing by month.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Indemn Observatory | GitHub repo | indemn-ai/indemn-observability |
| Tiledesk DB | MongoDB Atlas | tiledesk database |
| Linear Task | Linear | COP-326 (In Progress, Cycle 73, assigned Craig) |
| Observatory CLAUDE.md | Docs | indemn-observability/CLAUDE.md (503 lines, implementation guide) |
| Overview Page | Code | indemn-observability/frontend/src/components/overview/OverviewView.tsx |
| API Endpoints | Code | indemn-observability/src/observatory/api/routers/aggregations.py |
| Types | Code | indemn-observability/frontend/src/types/api.ts |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-24 | [usage-data-exploration](artifacts/2026-02-24-usage-data-exploration.md) | What does the tiledesk data look like for org/agent usage, and how does the Observatory work? |
| 2026-02-24 | [research-and-spec-inputs](artifacts/2026-02-24-research-and-spec-inputs.md) | Verified billing filter, clean usage tables, architecture summary, and open design questions for spec |

## Decisions
- 2026-02-24: Billing-aligned filter is `status: 1000, isTestMode: {$ne: true}, depth: {$gt: 2}` — verified against stripe_meters within 1-2%
- 2026-02-24: Exclude test orgs: Indemn, Demos, Voice Demos, test-dolly-prod, InsuranceTrak. EventGuard is a real customer (keep).
- 2026-02-24: Usage table should be dynamic, driven by the date range selector at top of overview page
- 2026-02-24: Filter documented in MongoDB skill `references/query-patterns.md` for reuse

## Open Questions
- How should the date range selector drive month columns? (bucket by month within selected range)
- Where in the UI — new section on overview, new tab, or separate view?
- Data source — new API endpoint on raw `requests`, or extend daily_snapshots pipeline?
- Agent drill-down UX — expandable org rows vs separate table?
- Metrics beyond conversation count — unique users, avg depth, avg duration?
- Scope interaction — what shows at platform vs customer vs agent level?
