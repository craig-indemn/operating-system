# Analytics Dashboard

Add a usage analytics overview to the Indemn Observatory — organization and agent usage metrics broken out by month for the last 6 months, sourced from the tiledesk MongoDB database. Provides Kyle with visibility into platform adoption and activity trends.

## Status
**Feature complete and deployed to prod.** Session 2026-02-24-e closed out the project.

- PR #13 (`demo-gic` → `main`) merged
- PR #14 (`main` → `prod`) merged — prod CI deploying
- All 12 beads tasks closed
- Linear COP-326 moved to "Ready for Testing"
- Dev EC2 verified working (containers healthy, API returns correct data)

**Awaiting**: Kyle's review on prod once deployment completes.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Indemn Observatory | GitHub repo | indemn-ai/Indemn-observatory |
| Tiledesk DB | MongoDB Atlas | tiledesk database |
| Linear Task | Linear | COP-326 (Ready for Testing, Cycle 73, assigned Craig) |
| Observatory CLAUDE.md | Docs | indemn-observability/CLAUDE.md (503 lines, implementation guide) |
| Overview Page | Code | indemn-observability/frontend/src/components/overview/OverviewView.tsx |
| API Endpoints | Code | indemn-observability/src/observatory/api/routers/usage.py |
| Types | Code | indemn-observability/frontend/src/types/api.ts |
| PR #13 | GitHub | indemn-ai/Indemn-observatory/pull/13 (demo-gic → main) |
| PR #14 | GitHub | indemn-ai/Indemn-observatory/pull/14 (main → prod) |
| Dev EC2 | Infrastructure | ssh -i ptrkdy.pem ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com |
| PEM Key | File | /Users/home/Repositories/ptrkdy.pem |

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
- 2026-02-24: API uses ValidatedScope dependency for auth — platform scope restricted to Indemn employees, external users forced to customer scope
- 2026-02-24: **Use `attributes.bot_id` for agent attribution** — NOT `participantsBots`. Tiledesk clears participantsBots on human handoff, but attributes.bot_id persists. Eliminates the false "Unattributed" category. Every billable conversation has attributes.bot_id (verified: 16,015 with both fields agree, 4,973 only in attributes, zero mismatches).
- 2026-02-24: GIC "Unattributed" was actually human handoff conversations — Maria Gonzalez (2,181), Coralia Nunez (1,808), etc. joined bot conversations. Bot started every conversation.
- 2026-02-24: Data is web chat only (all channel=chat21). Voice conversations use a different system, not in tiledesk.requests.
- 2026-02-24: Date range presets use `days - 1` offset for inclusive counting ("Last 7 days" = 7 days inclusive → daily bucketing).
- 2026-02-24: Platform default snaps to month boundaries: 1st of (current month - 6) through end of previous month.
- 2026-02-24: Weekly bucket headers show "Feb 17 – 23" format instead of ISO week "W08".
- 2026-02-24: Table has title "Conversation Volume" and subtitle describing scope: "Billable web chat conversations by organization... Excludes test mode and internal orgs."
- 2026-02-24: CI/CD flow: `demo-gic` → `main` (PR) → `prod` (PR). `demo-gic` deploys to dev via `build-demo.yml`, `prod` deploys on push via `build-prod.yml`.
- 2026-02-24: Dev MongoDB is NOT over quota — connection works fine. The dev database simply has different org IDs than prod. Demo auth hardcodes a prod org ID (`GIC_ORG_ID`), which caused empty results on dev.
- 2026-02-24: Excluded org IDs are prod-specific — dev database has different ObjectIds for test orgs, so they show in dev (expected, not a bug).

## Open Questions
- Family First has 41 Feb conversations all flagged `isTestMode: true` — is their widget misconfigured?
