# Union General — Intake Manager

Bug triage, reproduction, and fixes for the Union General (UG) Portal / Intake Manager — the comparative rater product Ben Bailey and team use to submit surplus-lines business across multiple carriers. Distinct from Johnson Insurance (GIC) work.

## Status
**Session 1 (2026-04-17):** Project opened, three UG repos mapped, code analysis complete, **data verified end-to-end** against production logs (via SSM read-only) and MongoDB quote documents. WHAT/WHY/HOW established for Bugs #1 and #3. Bug #2 still needs specific repro input from Rem.

**Screenshot's source submission identified**: Xol Lounge (thread `AQQkADA...xV8=`), a Bakersfield CA bar with $240K GL exposure, class code 16940. Log shows `generated=3, errors=0`. MongoDB state for all three quotes (ACIC / Scottsdale / Northfield) matches the screenshot exactly.

**Bug #3 (fee-calc) — data-confirmed:**
- ACIC stored `[tax "Taxes" $120.00, fee "Fees" $207.20]` — aggregated flat, not broken down. `raw_response.tax_breakdown` is null. The $207.20 is likely ACIC's own policy/admin fee + stamping fee; injected broker/inspection were dropped on round-trip.
- Scottsdale (NATIONWIDE_CL) stored `[fee "Broker Fee" $200, fee "Inspection Fee" $200]` — Nationwide's API echoed them back from what we sent.
- Northfield stored `[]` (empty). `raw_response.input_params.taxes_and_fees` contains the injected $200/$200 but they were never transmitted to the carrier or extracted back — Northfield's code path is end-to-end fee-blind.
- **Root cause:** no unified fee/tax pipeline. Three carrier providers each own isolated logic; no post-processing step.
- **Fix recommendation:** Option B — centralized `taxes_and_fees_resolver` in `QuoteGenerationService.generate_quote`. Possibly Option C alongside (state surplus-lines tax table for carriers whose API doesn't return them).

**Bug #1 (older subs still fail) — 4 distinct failure patterns identified in logs:**
- **Pattern A**: Invalid class code persists through regenerates — e.g., class code `9711` rejected by ACIC, no-match at Nationwide, `VALIDATIONFAILED` at Northfield, all for the same submission. Regenerating without fixing upstream data reproduces the same error. Investigation target: `class_code_matcher.py`, extraction pipeline.
- **Pattern B**: Carriers legitimately decline out-of-appetite classes — not a bug, expected behavior.
- **Pattern C**: Python `NoneType has no len()` crash in Nationwide CL agent code — real bug. Target: `providers/nationwide/cl/graph.py` or `tools.py`.
- **Pattern D**: Travelers API returns wrong state for some zips — warning only, handled gracefully.
- **Root cause:** mix of upstream data quality (A) and one concrete Python bug (C). Need specific failing submission IDs from Ben/Rem to map each older sub to a pattern.

**Bug #2 (false-positive validations) — not yet investigated.** Need specific form + field + submission from Ben.

See [data-verification-findings](artifacts/2026-04-17-data-verification-findings.md) for full data-backed analysis.

**Non-bug findings flagged:**
- Intake-manager frontend container unhealthy for 3 days (9,107 failing healthchecks since ~2026-04-14) — users still working, so healthcheck likely misconfigured but needs follow-up.
- DataDog trace ingestion broken on copilot-prod host.
- Intake-manager prod `.env` still hand-maintained (same drift risk as the Nationwide URL regression).

**Active bug report** (see [ben-bailey-bug-report](artifacts/2026-04-17-ben-bailey-bug-report.md) and screenshot):
1. **Older submissions still fail** — not yet investigated; needs submission IDs from Ben to pull logs from copilot-prod (no CloudWatch log groups for intake-manager — logs live in docker containers on EC2, SSM-accessible read-only).
2. **False-positive validation violations** — not yet investigated; likely in `app/services/validation/json_rule_validator.py` and/or `parameter_violation_mapper_service.py`. Needs a specific repro case from Ben.
3. **Fee calculation inconsistent across carriers** — **root cause identified** (see above). Ready for data verification + fix planning.

Rem confirmed: Dhruv was primary dev, handed off context to Rudra. Ben tagged the issues high priority; Craig offered to dig in.

**Next session:**
1. **Monitor the #dev-squad thread** — watch for Rudra's PR #118 review, Rem's answer on Bug #3 policy questions + design-doc pointers, any Bug #2 repro from Ben.
2. **Pattern A upstream trace (Bug #1)** — not blocked on Ben/Rem. Pull the specific failing submission from logs (`AQQkADA...EOW6JgWwEgCg7bI4JvL_iw=`, Fri 2026-04-17 16:20) from MongoDB and trace where the class code 9711 came from: extraction output? class-code matcher? original input? Investigate `app/services/class_code_matcher.py`, `app/services/quote/parameter_extractor.py`, `app/services/extraction/`.
3. **Pattern C verification** — once PR #118 merges + deploys, watch for absence of the NoneType error in prod logs. Ask Rem if Ben could try re-running the submission(s) that previously crashed on Nationwide CL.
4. **Bug #3 fix planning** — wait for Rem's response on source-of-truth for state taxes and existing design docs. Once received, pick between Option A (narrow per-carrier patches), Option B (centralized resolver), or B+C (add state tax table).
5. **Frontend container healthcheck** — low-priority non-blocker; investigate whether Next.js mode mismatch vs. healthcheck expectation.
6. **Reproduction environment** — test `./start-dev.sh` locally with staging-pointed config; this unblocks any local development we'd want to do.
7. **Beads init** — still open.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| intake-manager | GitHub repo | [indemn-ai/intake-manager](https://github.com/indemn-ai/intake-manager) — Python, default branch `main` |
| ug-apis | GitHub repo | [indemn-ai/ug-apis](https://github.com/indemn-ai/ug-apis) — Python, default `main` |
| ug-service | GitHub repo | [indemn-ai/ug-service](https://github.com/indemn-ai/ug-service) — JavaScript, default `main` |
| **PR #118 — Pattern C NoneType fix** | GitHub PR | [indemn-ai/intake-manager#118](https://github.com/indemn-ai/intake-manager/pull/118) — 3-line fix, awaiting Rudra review |
| **#dev-squad handoff thread** | Slack | [permalink](https://indemn.slack.com/archives/C08AM1YQF9U/p1776450222923819) — 2026-04-17 findings message to Rem + Rudra |
| Ben Bailey (UG) | Slack user | U08KVL9D0HG (workspace TFJBK4B7A) — reporter |
| Rem (George Remmer) | Slack user | U03DP1H58B1 — customer-success point of contact |
| Rudra (Rudraraj Thakar) | Slack user | U0881BF4EMN — current intake-manager dev (inherited from Dhruv) |
| Dhruv | Slack / GitHub | prior primary dev, currently OOO — original builder of fee/tax logic |
| #dev-squad | Slack channel | C08AM1YQF9U (14 members, shared team channel) |
| Prod deploy host | EC2 | copilot-prod (`i-0df529ca541a38f3d`, 54.226.32.134), `/opt/Intake-manager/` |
| Related devops context | OS project | [projects/devops/INDEX.md](../devops/INDEX.md) — Nationwide fix details (2026-04-17 session) |
| Bug report screenshot | Local artifact | `artifacts/2026-04-17-ben-bailey-screenshot.png` |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-04-17 | [ben-bailey-bug-report](artifacts/2026-04-17-ben-bailey-bug-report.md) | Capture Ben Bailey's 3-issue bug report forwarded by Rem, with screenshot evidence and structured framing |
| 2026-04-17 | [repo-mapping](artifacts/2026-04-17-repo-mapping.md) | Map the three UG-adjacent repos (intake-manager, ug-apis, ug-service) and identify which owns the rater, fee calc, validation, carrier integrations |
| 2026-04-17 | [bug3-fee-calc-analysis](artifacts/2026-04-17-bug3-fee-calc-analysis.md) | Root-cause analysis of Bug #3 (fee-calc inconsistency) — side-by-side code read across three carrier provider paths, architectural gap identified, fix options |
| 2026-04-17 | [data-verification-findings](artifacts/2026-04-17-data-verification-findings.md) | Data-verified WHAT/WHY/HOW for all three bugs using production logs (via SSM read-only) and MongoDB quote documents. Identifies Xol Lounge as the screenshot's source submission, confirms Bug #3 fully with stored data, uncovers 4 distinct failure patterns for Bug #1 including a Python NoneType crash in Nationwide CL agent |
| 2026-04-17 | [dev-squad-message-draft](artifacts/2026-04-17-dev-squad-message-draft.md) | Draft iterations (V1–V5) of the findings message to Rem + Rudra, preserved for reference on tone + framing choices |
| 2026-04-17 | [dev-squad-message-sent](artifacts/2026-04-17-dev-squad-message-sent.md) | Final posted message to #dev-squad with pending-items tracker — what's awaiting response from whom |

## Decisions
- 2026-04-17: Project scoped to Union General / intake-manager, separate from GIC work. Name `union-general-intake-manager` keeps it specific (UG may have other products later).
- 2026-04-17: Treat this as a systematic bug-fix project — reproduction capability is prerequisite to fixes, not an afterthought. No "guess and patch" on production.
- 2026-04-17: Intake-manager prod deploys via hand-maintained `/opt/Intake-manager/.env` on copilot-prod — `aws-env-loader.sh` exists in repo but isn't wired into deploy. This is a latent source of config drift and was how the Nationwide URL regression got introduced. Migrate env management to SM as follow-up work (tracked in devops project).
- 2026-04-17: Scottsdale (SIC) is Nationwide's surplus-lines E&S subsidiary — the rater labels it "Scottsdale" in the UI but the request routes through `providers/nationwide/cl/` and the Nationwide Insurance API wrapper in `ug-apis`. No dedicated SIC provider exists or is needed.
- 2026-04-17: Bug #3 root cause is architectural, not a one-line bug. Three provider code paths (ACIC, Nationwide CL, Northfield) each own their own tax/fee handling; Northfield's is entirely missing. The fix requires either per-carrier patching (Option A) or a centralized post-processing step (Option B). Deferring decision to Craig after MongoDB data verification.
- 2026-04-17: `intake-manager` does not have CloudWatch log groups — all logs live in Docker containers on copilot-prod EC2 and require SSM Session Manager (read-only) to inspect. No Lambda or ECS path exists for this service.

## Open Questions
- ~~Which of the three repos owns the fee-calculation logic?~~ **Answered:** `intake-manager/app/services/quote/` (see repo-mapping artifact).
- ~~Is the fee-calc divergence a data problem or a code problem?~~ **Answered:** Code problem — each of three carrier providers owns its own tax/fee path with no unifying step; Northfield handles nothing at all (see bug3-fee-calc-analysis artifact).
- Can intake-manager run locally, or is staging the only reproducible environment? Does `./start-dev.sh` cover it? (Needs testing — FastAPI:8000 + Next:3000 per the README.)
- For Bug #1 (older subs failing) — do we have submission IDs/logs from Ben? Still open; ask Rem next session.
- For Bug #2 (validation false-positives) — which form, which fields, which carrier, which state? Still open; ask Rem next session.
- **Is ACIC's $120 tax + $207.20 fees correct for the state in question?** Need risk state + state surplus-lines tax rate to verify. This determines whether ACIC's response is source of truth or whether the app should own a state tax table.
- **Does Nationwide CL actually return state surplus-lines taxes in its API response?** Screenshot suggests no — but code is willing to extract them if present. Need to inspect a raw Nationwide CL response from MongoDB.
- **Does Northfield's API return any tax/fee elements at all?** Can't tell from code alone (parser ignores them). Must inspect raw response.
- **Are broker/inspection fees always flat $200 per carrier, or does it vary by state/agency/product?** Currently treated as flat per-provider in `_FALLBACK_PROVIDER_FEES`.
- Beads is empty everywhere in the OS — init in main repo and wire up, or skip task tracking and use this INDEX.md + the bug-report artifact as the source of truth?
