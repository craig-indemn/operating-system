# Observatory

Indemn Observability platform — analytics, monitoring, and reporting for voice and chat agents.

## Status
**2026-03-12**: Report Hub Phase 1 merged (PR #37). Phase 2 in PR #38 — CI passing, E2E tested with security hardening, ready to merge.

Phase 1 (merged via PR #37): backend extractors (voice_data, distinguished_internal), 7-endpoint API router, frontend Reports tab with generate/download/scope filtering, agent_ids filtering, Dockerfile with Node.js 22.x, migration script.

Phase 2 (PR #38, 4 commits, CI green): 3 new report types (customer-insights, customer-analytics, onboarding-guide), CI fix (npm removed from runtime image), old client-side PDF code removed (4,340 lines), security hardening from code review (extractor/renderer validation, error sanitization, agent-org validation, S3 bucket fix, date parity fix).

**Known bug**: Download from the Reports tab in the browser was not working correctly during local testing. Needs E2E shakeout via agent-browser. See artifact: `2026-03-12-report-hub-shakeout-plan.md`

**Next**:
1. Merge PR #38 (CI passing, all fixes committed)
2. E2E shakeout via agent-browser — generate + download each report type, test org/agent filtering, test error cases
3. Fix any bugs found during shakeout
4. Deploy to dev — verify via https://devobservatory.indemn.ai/reports
5. Register report types in prod MongoDB when ready for production

**Previous sessions (2026-03-12)**: Designed Report Hub (3 rounds of review, 20 issues resolved). Fixed flow query performance, funnel cohort auth, CI consolidation. Built Phase 1 + Phase 2 report types. Security review found and fixed 6 security issues + 3 data parity issues.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo (org) | indemn-ai/Indemn-observatory |
| indemn-observability | GitHub repo (fork) | craig-indemn/indemn-observability |
| Dev deployment | URL | https://devobservatory.indemn.ai |
| Prod deployment | URL | https://prodobservatory.indemn.ai |
| Report Hub design | Design doc | docs/plans/2026-03-12-observatory-report-hub-design.md |
| Report Hub Phase 1 PR | GitHub PR (merged) | https://github.com/indemn-ai/Indemn-observatory/pull/37 |
| Report Hub Phase 2 PR | GitHub PR | https://github.com/indemn-ai/Indemn-observatory/pull/38 |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-12 | [observatory-report-hub-design](../../docs/plans/2026-03-12-observatory-report-hub-design.md) | How to build a customer-facing report hub in the observatory with per-org configuration and server-side PDF generation |
| 2026-03-12 | [report-hub-shakeout-plan](artifacts/2026-03-12-report-hub-shakeout-plan.md) | E2E shakeout plan for Report Hub — test every user flow via agent-browser, fix download bug |

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

- 2026-03-12: Phase 2 extractors query `observatory_conversations` collection in `tiledesk` database (same DB as voice extractor)
- 2026-03-12: Phase 2 report types use scope `customer` (not `agent`) with `org_ids: null` (available to all orgs)
- 2026-03-12: Node.js upgraded to 22.x LTS in Dockerfile; npm updated to latest for security
- 2026-03-12: Frontend package.json/package-lock.json excluded from Docker image via .dockerignore
- 2026-03-12: Redundant font/brand COPY commands removed from Dockerfile (already included via `COPY . .`)

- 2026-03-12: CI fix — remove npm from runtime Docker image after `npm ci`, eliminating all 10 CVEs in npm's bundled tar/glob/minimatch. `.trivyignore` added as fallback.
- 2026-03-12: Old client-side PDF generation removed — ReportButton.tsx retains CSV/JSON export only, 24 React PDF components + generateReport.tsx + useReportData/useCustomerReportData hooks deleted, @react-pdf/renderer removed from frontend deps
- 2026-03-12: Phase 2 report types registered in dev MongoDB via migration script with dev env credentials
- 2026-03-12: Security review — extractor slug validated `^[a-z][a-z0-9_]*$`, renderer filename validated `^[a-zA-Z0-9_-]+\.jsx$`, error messages sanitized, agent-org ownership verified via projects collection, S3 presigned URLs use config bucket not doc-stored bucket
- 2026-03-12: Data parity — date boundary fix (strftime not isoformat for timezone-aware datetimes), null intents skipped not counted as "unknown", flow path defaults use empty string matching old frontend
- 2026-03-12: Analytics report renderer has intentional visual differences from old: corrected title/footer from "Insights" to "Analytics", deep links removed (not applicable for server-side PDFs), page header numbers removed (footer has dynamic Page X of Y), summary narrative uses plain text not inline bold/color

## Open Questions
- Prod migration: Phase 2 report types need to be registered in prod MongoDB separately (different org IDs)
- The `observatory_conversations` collection data availability varies by org — some orgs may not have enough data for meaningful reports
- Download bug: clicking download in the browser was not working during local testing — needs investigation during shakeout
