# GIC Agent Improvements

Systematic improvement of the GIC Underwriters AI associate ("Fred") — identify opportunities, implement changes, evaluate impact, and monitor ongoing performance.

## Status
**Phase 4 (Production Deployment) IN PROGRESS. Linear tickets created (AI-333 + 6 sub-issues). Customer report PDF generated — needs minor fixes + user feedback. Report delivery blocks all production changes.**

**Evaluation IDs:**
- Test bot (dev): `6787a63d2ea6350012955ed9`
- Rubric: `3bd8cc49-7eef-4110-95ac-01fdc4419cc5` (5 rules, v2 — calibrated Rule 03)
- Test set: `0977c5bc-2987-40fa-95bb-31f14781a7c1` (9 scenarios + 8 single-turn = 17 items, **v3** — criteria aligned to opportunities)
- **Old baseline (v2 criteria): `081e50a2-425f-40c8-a01f-5e43985a7f34`** — 13/15 passed (criteria too lenient)
- **V3 baseline: `4ee5b3af-f0b1-43f8-9883-303da9e3927a`** — 7/17 passed (41.2%), 10 opportunity-aligned items FAIL, 7 regression guards PASS, rubric 85/85 (100%)
- Eval model: `openai:gpt-4.1` | Eval DB: dev/tiledesk (not evaluations)

**Official baseline (observatory, 3,701 real conversations):**
- Autonomous resolution rate: **8%** (300/3,701)
- Total failure rate: **44%** (missed_handoff + partial + timeout + abandoned + out_of_hours)
- Policy API failure rate: **15%** (486/3,198 API calls)
- Missed handoffs: **618** (17% of real conversations)
- Bad product inquiry outcomes: **437** (51% of 860 product inquiries)
- After-hours wasted conversations: **69** (avg 11 turns before user finds out)
- Frustrated users: **288** (7.8%)

**Active opportunities (by implementation group):**
- **Group A — System Prompt + Opener:** opener rewrite (#3), expectations gap (#14), after-hours detection (#7), direct request phrasing (#4)
- **Group B — Operations API Code:** policy number parsing (#5), expiration date in output (#10 bundle)
- **Group C — Knowledge Base:** WC class codes (#6), portal URLs (#11 bundle)
- **Group D — Handoff Fallback:** missed handoff fallback behavior (#13)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Ryan's UX Observation Report | Google Doc | [GIC UX Observations](https://docs.google.com/document/d/1oiVuIhvTYHTkHuyfeluFNibE-AR3UeOx_3c0uRhyvLQ/edit?usp=sharing) |
| Kyle's assignment message | Slack | mpdm-kwgeoghan--ryan--craig (ts=1773236602.449279) |
| GIC bot config | MongoDB | tiledesk.bot_configurations (bot_id: `66026a302af0870013103b1e`) |
| Policy API route | Code | operations_api/src/routes/gic-policy-details.ts |
| Policy API service | Code | operations_api/src/services/customers/gic_policy_details.ts |
| Tool execution | Code | bot-service/app/services/tools/agent_tools.py |
| Observatory data | MongoDB | tiledesk.observatory_conversations (scope.customer_id: `65eb3f19e5e6de0013fda310`) |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-12 | [ryan-gic-ux-observations](artifacts/ryan-gic-ux-observations.pdf) | Ryan's full UX analysis with 17 observations and 14 screenshots |
| 2026-03-12 | [agent-research](artifacts/2026-03-12-agent-research.md) | Deep research: agent config, backend architecture, policy API, knowledge bases, quantified baselines for all 13 improvement opportunities |
| 2026-03-12 | [opportunity-prioritization](artifacts/2026-03-12-opportunity-prioritization.md) | Prioritization of opportunities using observatory data and actual conversation analysis — 7 active, 5 parked, 2 bundled |
| 2026-03-12 | [evaluation-criteria](artifacts/2026-03-12-evaluation-criteria.md) | Evaluation rubric rules, test case designs, observatory baselines, and projected impact per opportunity |
| 2026-03-12 | [baseline-evaluation-results](artifacts/2026-03-12-baseline-evaluation-results.md) | Baseline eval: 13/15 passed, all rubric rules 100%, 2 handoff workflow failures — full analysis with conversations |
| 2026-03-12 | [v3-baseline-evaluation-results](artifacts/2026-03-12-v3-baseline-evaluation-results.md) | V3 baseline: 7/17 passed (41.2%), 10/10 opportunity items FAIL as expected, perfect calibration — full conversations and failure analysis |
| 2026-03-12 | [policy-number-analysis](artifacts/2026-03-12-policy-number-analysis.md) | Analysis of 192 real policy lookups — 13 carrier formats, 2 normalization rules fix 100% of addressable failures (63% of total) |
| 2026-03-12 | [retrieval-investigation](artifacts/2026-03-12-retrieval-investigation.md) | KB retrieval root cause: wrong Pinecone namespace + wrong KB ID filter. Fixed. Prod bot has no faqs-retriever tool at all. |
| 2026-03-12 | [post-implementation-evaluation-results](artifacts/2026-03-12-post-implementation-evaluation-results.md) | Post-implementation eval: 12/17 (70.6%) vs baseline 7/17 (41.2%). 5 items flipped, 0 regressions. Full conversation traces and failure analysis. |

## Decisions
- 2026-03-12: Project created to track GIC agent improvement work per Kyle's directive
- 2026-03-12: Added Craig's item — policy number parsing improvements in operations_api
- 2026-03-12: Prioritization complete — 7 active opportunities selected based on observatory data and conversation transcript analysis
- 2026-03-12: Parked slot-filling (#1, infrastructure), tone (#2, cosmetic), constraint surfacing (#8, not the real problem), "thank you" closure (#9, no data support), boolean bug (#12, front-end)
- 2026-03-12: Original research baseline numbers (from ad-hoc message queries) replaced with official observatory data
- 2026-03-12: Discovered new opportunity #14 (bot expectations gap) from reading actual product inquiry transcripts — bot collects 20+ turns of info without telling users it can't generate quotes
- 2026-03-12: Eval environment audit — fixed 5 critical differences (KB namespace, AgencyCode, identify_next_step, test data, evaluator model)
- 2026-03-12: Rule 03 (persona maintenance) rewritten from subjective "contextually appropriate" to explicit trigger conditions — v1 had 93% false-failure rate
- 2026-03-12: Eval service uses dev/tiledesk DB (not dev/evaluations) — caused by `.env` in evaluations/ repo overriding `MONGODB_DATABASE`
- 2026-03-12: Eval model switched from Anthropic (rate limited) to `openai:gpt-4.1`
- 2026-03-12: Test set v3 — tightened criteria to FAIL on pre-improvement behavior, added after-hours and opener test items
- 2026-03-12: V3 baseline run confirmed — 10/10 opportunity items FAIL, 7/7 regression guards PASS, 0 evaluation problems. Ready for Phase 2.
- 2026-03-12: Phase 2 Groups A/B/D implemented on test bot. System prompt fully rewritten (not patched) — consolidated redundant sections, resolved conflicts with new directives.
- 2026-03-12: Policy normalization based on 192 real lookups — 2 data-driven rules (Granada suffix strip, USLI/MV space insertion) fix 100% of addressable failures.
- 2026-03-12: KB content investigation: class codes (140 entries), portal URLs (72 entries), email routing (20+ entries) ALL exist and are trained in Pinecone. #6 and #11 are retrieval quality problems, not content gaps.
- 2026-03-12: Fabricated URLs/emails removed from prompt — never insert unverified business data into agent configs.
- 2026-03-12: KB retrieval root cause found — two config mismatches: (1) bot namespace pointed to prod org `65eb3f19e5e6de0013fda310` which doesn't exist in Pinecone; vectors are in dev org namespace `6613cbc6658ad379b7d516c9`. (2) bot KB mapping pointed to original KB `6787a670...`; vectors tagged with `6852bf20...`. Both fixed.
- 2026-03-12: Production bot has NO faqs-retriever tool — KB access never existed in production. Deploying requires adding tool + correct config.
- 2026-03-12: Pinecone has ~5x vector duplication from same data trained across multiple KBs. top_k increased to 25 to compensate.
- 2026-03-12: Verified emails from KB data added to system prompt: csr@gicunderwriters.com (handoff fallback), quote@gicunderwriters.com (quote protocol).
- 2026-03-12: Business hours confirmed from KB: 8:30 AM - 5:00 PM.
- 2026-03-12: Post-implementation eval: 12/17 (70.6%) vs baseline 7/17 (41.2%). 5 items flipped FAIL→PASS (#4, #6×2, #14×2). Rubric 85/85 — zero regressions.
- 2026-03-12: Remaining 5 failures classified: 2 eval limitations (handoff harness stops), 1 test design (greeting/first_message), 1 real agent issue (handoff explanation), 1 expected (policy parsing not deployed).
- 2026-03-12: Test criteria updated to v4 — handoff tests now evaluate pre-handoff behavior (contact collection, fallback communication) since eval harness can't test post-handoff recovery.

## Open Questions
- Evaluation criteria: what specific metrics and thresholds per opportunity for before/after comparison?
- KB content: what specific WC class code data and appetite information needs to be added? (59 codes exist, but common codes like 8810 are missing)
- Policy number formats: what are all valid GIC policy number formats across carriers? (needed for format validation)
- Handoff fallback: what timeout period before offering alternatives? What alternatives to offer?
- After-hours: exact business hours for GIC? (confirmed 8:30AM-5:00PM from KB, Mon-Fri assumed)
- Production KB deployment: how to set up faqs-retriever tool on prod bot and ensure correct Pinecone namespace/KB config?
- Pinecone deduplication: ~5x duplicate vectors — clean up, or leave and compensate with higher top_k?
