# Analytics Dashboard

Add a usage analytics overview to the Indemn Observatory — organization and agent usage metrics broken out by month for the last 6 months, sourced from the tiledesk MongoDB database. Provides Kyle with visibility into platform adoption and activity trends.

## Status
Session 2026-02-24-c complete — **full implementation done**, all 12 tasks built and verified. Backend endpoint works at all 3 scope levels, frontend renders with expand/collapse, numbers match billing data. **Not yet committed** in indemn-observability repo.

**Blocker for next session**: Data presentation needs tuning before showing Kyle:
1. **Date range**: 183-day default lands on Aug 25, creating a partial August column. Should snap to month boundaries (e.g., Sep 1 – Feb 28).
2. **Unattributed sort order**: Unattributed row sorts first for GIC (54% unattributed) — should sort last within expansion.
3. **Needs Kyle review**: Numbers are real billing data, but the partial month + Unattributed prominence may confuse without context.

**Next session**: Fix date default (snap to month boundary), move Unattributed to bottom of expansion, commit code, get Kyle's feedback on the table.

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
| 2026-02-24 | [usage-analytics-spec](artifacts/2026-02-24-usage-analytics-spec.md) | Full implementation spec — UI, scope, bucketing, API, MongoDB, frontend components, implementation order |
| 2026-02-24 | [usage-feature-implementation](artifacts/2026-02-24-usage-feature-implementation.md) | Implementation session summary — 14 files, 3 scope levels verified, known issues for next session |

## Decisions
- 2026-02-24: Billing-aligned filter is `status: 1000, isTestMode: {$ne: true}, depth: {$gt: 2}` — verified against stripe_meters within 1-2%
- 2026-02-24: Exclude test orgs: Indemn, Demos, Voice Demos, test-dolly-prod, InsuranceTrak. EventGuard is a real customer (keep).
- 2026-02-24: Usage table should be dynamic, driven by the date range selector at top of overview page
- 2026-02-24: Filter documented in MongoDB skill `references/query-patterns.md` for reuse
- 2026-02-24: Usage tab is first tab on overview page, default selected — Kyle sees it immediately
- 2026-02-24: Adaptive bucketing — >31 days monthly, 8-31 days weekly, ≤7 days daily
- 2026-02-24: Use global date range selector (extend max to 6 months). Platform defaults to 6 months, org/agent defaults to 30 days.
- 2026-02-24: Drill-down is inline accordion expansion (click org → agent sub-rows appear). Lazy-loaded via second API call.
- 2026-02-24: API response shape is extensible — `metrics` array + named metric keys in bucket objects, ready for additional metrics later
- 2026-02-24: New endpoint `GET /api/aggregations/usage` queries `requests` directly (not daily_snapshots). Independent from LangSmith pipeline.
- 2026-02-24: New compound index `idx_billing_usage` on `{status, isTestMode, createdAt, id_organization, depth}`
- 2026-02-24: Conversation count only for now — shape supports adding unique_users, avg_depth etc. later
- 2026-02-24: test-dolly-prod correct ObjectId is `65e18830a0616000137bb854` (not `66fc8ab493b5a40013596cd7` from initial research)
- 2026-02-24: Usage is a CategoryTab (MetricCategory), not a top-level route. OverviewView has CategoryTabs (Volume/Outcomes/etc.) — Usage added as first category.
- 2026-02-24: ~22% of billable requests have empty participantsBots — show "Unattributed" row in agent drill-down to maintain total consistency
- 2026-02-24: participantsBots values are strings, faq_kbs._id is ObjectId — must use $toObjectId in $lookup pipeline
- 2026-02-24: API uses ValidatedScope dependency for auth — platform scope restricted to Indemn employees, external users forced to customer scope

## Open Questions
- Should "Last 6 months" snap to the 1st of (current month - 6), or keep the rolling 183-day window?
- Why does GIC have ~54% unattributed conversations vs ~22% platform average? Widget config issue or expected behavior?
- Should Unattributed row always sort last in agent expansion, or stay sorted by total?
