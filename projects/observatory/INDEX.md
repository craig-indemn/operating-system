# Observatory

Indemn Observability platform — analytics and monitoring for voice and chat agents. Fixing authorization issues and improving the platform.

## Status
**2026-04-27 EOD**: Major hot-fix day. Voice ingestion was silently broken in prod since 2026-03-09 — PR #19 (voice ingestion code) merged to `main` in early March but the lambda + Step Functions update never made it from dev to prod. Jonathan reported the user-facing symptom (Insurica voice agents showing empty Volume/Flow/Outcomes tabs). Fixed end-to-end today: prod lambda + state machine deployed, full backfill complete, classifier moved to Gemini Vertex (Anthropic credit balance had hit zero, polluting April data with default fallback values). All voice agents now render correctly. Reply posted in Jonathan's thread (`#dev-squad` parent ts `1777060307.862239`).

**Pickup tomorrow morning:**
1. Verify the 01:00 UTC scheduled SFN run on 2026-04-28 fired both `sync_traces` AND `sync_langfuse_traces` branches successfully — `aws stepfunctions list-executions --state-machine-arn arn:aws:states:us-east-1:780354157690:stateMachine:observatory-ingestion-pipeline --max-items 5` then describe the most recent
2. Confirm new langfuse trace records appeared in `tiledesk.processing_runs` (filter `job_type=sync-langfuse-traces`, sort by `started_at` desc)
3. Check PRs #72 + #73 for review activity from Rudra / Dhruv. If approved + merged, move COP-505/507/508 + DEVOPS-148/149/150 from Acceptance → Done
4. If Jonathan replied in the Slack thread, address whatever he flags
5. Optional: spot-test 5 Jan–Mar Anthropic+all-default records (the 419 from earlier diagnosis) to decide whether to run a similar backfill — current call: probably leave alone since they pre-date the credit failure

**2026-03-06**: All work merged into `main`. Waiting on 3 PRs to merge, then prod re-deploys and this project closes. Dependabot alerts (COP-357) are NOT on this repo — Observatory is not in Craig's COP-357 assignment.

**Open: PRs awaiting review (Rudra + Dhruv):**
- indemn-ai/Indemn-observatory#72 — Vertex env config (brings prod hot-fix into source)
- indemn-ai/Indemn-observatory#73 — Lambda filename normalization (prevents future deploy confusion)

**Earlier PRs to merge (from 2026-03-06):**
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
| 2026-04-27 | [Voice ingestion fix + Vertex Gemini swap](artifacts/2026-04-27-voice-ingestion-and-vertex-swap.md) | Insurica voice agent showed no data in Volume/Flow/Outcomes tabs (Jonathan, #dev-squad) |

## Decisions
- 2026-03-03: Fix metadata org leak at backend level (MongoDB $match filter) + frontend fallback removal
- 2026-03-03: Keep current auth model — @indemn.ai employees get full access, external users scoped to their orgs
- 2026-03-03: Suppress PyJWT InsecureKeyLengthWarning (shared secret with copilot-server, can't change unilaterally)
- 2026-03-03: Cherry-pick only security commits to main, not all demo-gic work
- 2026-03-06: All demo-gic work merged into main (PR #24 by Dhruv) — cherry-pick approach no longer needed
- 2026-03-06: Agent dropdown in Header wasn't filtering by selected org — fixed in PR #27
- 2026-03-06: main → prod merge is clean (no file-level conflicts, prod only has merge commit SHAs ahead)
- 2026-04-27: Switched classification LLM from Anthropic Claude Haiku to Gemini 2.5 Flash on Vertex AI. Reason: Anthropic API key credit balance ran out in April; classifier was silently writing default values. Vertex via service account (mirrors gic-email-intelligence pattern) — no application code change, env config + SA file mount only.
- 2026-04-27: Standardized lambda deploy convention — source `step_handler.py` (action dispatcher used by Step Functions) renamed to `lambda_function.py`; legacy single-pass `lambda_function.py` deleted (PR #73). Eliminates the file-collision foot-gun that caused a botched first deploy attempt today.
- 2026-04-27: Backfill convention — for date-range re-classification, delete obs convos matching the bad signature, then run `/api/admin/ingest` with `reuse_classifications=true`. Cache lookup goes against the same collection, so deleted records get fresh LLM classifications while untouched ones skip.

## Open Questions
- (none remaining — Dependabot alerts tracked separately under COP-357, not on Observatory repo)
