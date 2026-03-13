# Observatory

Indemn Observability platform — analytics and monitoring for voice and chat agents. Fixing authorization issues and improving the platform.

## Status
**2026-03-13**: Report Hub deployed to dev. Fixed CI/CD pipeline (IAM permissions for Secrets Manager + SSM Parameter Store), env loader pagination bug (only 10 of 114 params loaded), S3 upload permissions. Built `channel_filter` feature so agent dropdowns dynamically filter by channel (e.g. voice-daily only shows voice agents).

**Pending:**
- PR #46 — `channel_filter` + trailing slash fix + dropdown scroll + empty state → needs merge
- After merge: run dev MongoDB updates (channel_filter on voice-daily, fix org_ids)
- After dev verified: deploy to prod, run prod MongoDB updates, run migration script on prod
- COP-392 (Report Hub) can move to Done after prod deploy

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo | indemn-ai/Indemn-observatory |
| Dev deployment | URL | https://devobservatory.indemn.ai |
| Auth fix PR | GitHub PR | indemn-ai/Indemn-observatory/pull/18 (merged) |
| Agent dropdown fix | GitHub PR | indemn-ai/Indemn-observatory/pull/27 |
| Main → Prod deploy | GitHub PR | indemn-ai/Indemn-observatory/pull/28 |
| Channel filter PR | GitHub PR | indemn-ai/Indemn-observatory/pull/46 |
| Report Hub Linear issue | Linear | COP-392 |
| Implementation plan | File | docs/plans/2026-03-13-channel-filter-report-types.md |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|

## Decisions
- 2026-03-03: Fix metadata org leak at backend level (MongoDB $match filter) + frontend fallback removal
- 2026-03-03: Keep current auth model — @indemn.ai employees get full access, external users scoped to their orgs
- 2026-03-03: Suppress PyJWT InsecureKeyLengthWarning (shared secret with copilot-server, can't change unilaterally)
- 2026-03-03: Cherry-pick only security commits to main, not all demo-gic work
- 2026-03-06: All demo-gic work merged into main (PR #24 by Dhruv) — cherry-pick approach no longer needed
- 2026-03-06: Agent dropdown in Header wasn't filtering by selected org — fixed in PR #27
- 2026-03-06: main → prod merge is clean (no file-level conflicts, prod only has merge commit SHAs ahead)
- 2026-03-13: EC2-SSM-Role was missing SecretsManager + SSM read + S3 write permissions — added all three
- 2026-03-13: aws-env-loader.sh had pagination bug — GetParametersByPath only returned first 10 of 114 params
- 2026-03-13: Add `channel_filter` field to report types for dynamic agent dropdown filtering (voice-daily uses "voice")
- 2026-03-13: voice-daily should be available to any org (org_ids: null) — channel_filter handles scoping
- 2026-03-13: Distinguished Programs org ID differs per env — dev: 676be5a7ab56400012077e7d, prod: 679b191315e8c30013abdcb0

## Open Questions
- Voice-daily card shows for all orgs at platform scope, even webchat-only orgs (empty state shown, not a blocker)
