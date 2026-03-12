# Observatory

Indemn Observability platform — analytics, monitoring, and reporting for voice and chat agents.

## Status
**2026-03-12**: Report Hub feature designed and reviewed (3 rounds, 20 issues found and fixed). Design doc approved at `docs/plans/2026-03-12-observatory-report-hub-design.md`. Ready for implementation.

**Previous session (2026-03-12)**: Fixed flow query performance (522MB → 15.7MB via MongoDB projections), fixed funnel cohort auth (FunnelCohortPanel.tsx using raw fetch without JWT), consolidated CI (eliminated demo-gic branch, main→dev deploy restored), deployed fixes to dev and prod, synced fork and org repos.

**Next**: Implement Report Hub — Phase 1 (CLI reports: voice daily/retrospective for Rankin, distinguished programs). See design doc for full plan.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo (org) | indemn-ai/Indemn-observatory |
| indemn-observability | GitHub repo (fork) | craig-indemn/indemn-observability |
| Dev deployment | URL | https://devobservatory.indemn.ai |
| Prod deployment | URL | https://prodobservatory.indemn.ai |
| Report Hub design | Design doc | docs/plans/2026-03-12-observatory-report-hub-design.md |

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

## Open Questions
- (none)
