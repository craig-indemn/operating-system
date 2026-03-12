# Observatory

Indemn Observability platform — analytics, monitoring, and reporting for voice and chat agents.

## Status
**2026-03-12**: Report Hub Phase 1 complete. PR #37 open with 3 commits (implementation, scope filtering + agent_ids, Dockerfile fix). Awaiting CI scan pass after Dockerfile chown path fix.

Phase 1 delivered: backend extractors (voice_data, distinguished_internal), 7-endpoint API router, frontend Reports tab with generate/download/scope filtering, agent_ids filtering on report types, Dockerfile with Node.js 20.x, migration script. S3 bucket created, migration run on dev. E2E tested.

**Next**: Merge PR #37, deploy to dev. Then Phase 2 — migrate client-side React PDF reports (Monthly Insights, Customer Analytics, Onboarding Guide) into the hub.

**Previous sessions (2026-03-12)**: Designed Report Hub (3 rounds of review, 20 issues resolved). Fixed flow query performance, funnel cohort auth, CI consolidation.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo (org) | indemn-ai/Indemn-observatory |
| indemn-observability | GitHub repo (fork) | craig-indemn/indemn-observability |
| Dev deployment | URL | https://devobservatory.indemn.ai |
| Prod deployment | URL | https://prodobservatory.indemn.ai |
| Report Hub design | Design doc | docs/plans/2026-03-12-observatory-report-hub-design.md |
| Report Hub PR | GitHub PR | https://github.com/indemn-ai/Indemn-observatory/pull/37 |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-12 | [observatory-report-hub-design](../../docs/plans/2026-03-12-observatory-report-hub-design.md) | How to build a customer-facing report hub in the observatory with per-org configuration and server-side PDF generation |

## Decisions
- 2026-03-03: Fix metadata org leak at backend level (MongoDB $match filter) + frontend fallback removal
- 2026-03-03: Keep current auth model — @indemn.ai employees get full access, external users scoped to their orgs
- 2026-03-03: Suppress PyJWT InsecureKeyLengthWarning (shared secret with copilot-server, can't change unilaterally)
- 2026-03-06: All demo-gic work merged into main — cherry-pick approach no longer needed
- 2026-03-06: Agent dropdown in Header wasn't filtering by selected org — fixed in PR #27
- 2026-03-12: Flow query performance fix — add MongoDB projections to get_funnel_data and get_funnel_cohort (97% data reduction)
- 2026-03-12: Funnel cohort auth fix — FunnelCohortPanel.tsx switched from raw fetch to api.getPathCohort()
- 2026-03-12: CI consolidated — deleted build-demo.yml, re-enabled build.yml for main→dev, added OIDC AWS credentials
- 2026-03-12: Report Hub design — S3 for PDFs, MongoDB for catalog, server-side generation via Python extractors + Node JSX renderers
- 2026-03-12: Report auth uses get_current_user (not ValidatedScope) with custom org access checks
- 2026-03-12: Extractors live at src/observatory/extractors/ (proper Python package, not scripts/)
- 2026-03-12: Report dedup via upsert on compound key (type + org + agent + dates), replaces on regeneration
- 2026-03-12: Node.js installed in backend Docker image for JSX renderer subprocess
- 2026-03-12: Scope filtering fix — ReportsView uses useScope() to filter report type cards by org_ids and pass org_id/agent_id to useReports() hook
- 2026-03-12: Push feature branches directly to org repo (indemn remote) — fork name mismatch prevents cross-repo PRs via gh
- 2026-03-12: Added agent_ids field to report types — restricts agent dropdown to applicable agents only (same pattern as org_ids for orgs)
- 2026-03-12: Dev report types use dev org IDs (Dev-Dhruv for voice-daily, EventGuard for distinguished-internal) — prod uses different IDs
- 2026-03-12: Dockerfile chown fix — after `cd scripts`, path must be `node_modules` not `scripts/node_modules`

## Open Questions
- Phase 2: which client-side reports to migrate first? Monthly Insights is used most broadly (all orgs)
