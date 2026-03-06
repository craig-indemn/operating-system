# Observatory

Indemn Observability platform — analytics and monitoring for voice and chat agents. Fixing authorization issues and improving the platform.

## Status
**2026-03-06**: All work merged into `main`. Waiting on 3 PRs to merge, then prod re-deploys and this project closes. Dependabot alerts (COP-357) are NOT on this repo — Observatory is not in Craig's COP-357 assignment.

**PRs to merge (in order):**
1. PR #27 — Agent dropdown org scoping fix → `main` (approved, needs merger)
2. Voice eval feature PR → `main`
3. PR #28 — `main` → `prod` (ships everything, merge last)

**After prod deploys:** Verify observatory is back up, auth is working, then mark COP-364 Done and close this project.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo | indemn-ai/Indemn-observatory |
| Dev deployment | URL | https://devobservatory.indemn.ai |
| Auth fix PR | GitHub PR | indemn-ai/Indemn-observatory/pull/18 (merged) |
| Agent dropdown fix | GitHub PR | indemn-ai/Indemn-observatory/pull/27 |
| Main → Prod deploy | GitHub PR | indemn-ai/Indemn-observatory/pull/28 |

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

## Open Questions
- (none remaining — Dependabot alerts tracked separately under COP-357, not on Observatory repo)
