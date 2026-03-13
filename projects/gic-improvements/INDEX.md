# GIC Agent Improvements

Systematic improvement of the GIC Underwriters AI associate ("Fred") — identify opportunities, implement changes, evaluate impact, and monitor ongoing performance.

## Status
**DEPLOYING TO PRODUCTION. All dev work complete. Craig deploying changes via copilot-dashboard UI. Kyle approved shipping — waiting on Ryan's perspective on messaging and JC approval on first message specifically.**

**What's deploying:**
1. System prompt rewrite (all enhancements) — Craig doing via UI
2. First message update — **BLOCKED: needs JC approval** per Kyle
3. KB retrieval — add faqs-retriever tool + fix namespace/KB config on prod
4. Policy tool output — expiration dates and structured display
5. Policy number normalization — PR to operations_api (code change)

**Best eval result (v6 test set, run 5): 15/19 (78.9%)** — handoff diligence PASS, CSR summary PASS, explicit handoff PASS, failed handoff PASS. Up from 7/17 (41.2%) baseline.

**Evaluation IDs:**
- Test bot (dev): `6787a63d2ea6350012955ed9`
- Rubric: `3bd8cc49-7eef-4110-95ac-01fdc4419cc5` (5 rules, v2)
- Test set: `0977c5bc-2987-40fa-95bb-31f14781a7c1` (19 items, **v6**)
- **Best eval: `2dff7636-296d-4da1-9b5a-145ee610c4b1`** — 15/19 (78.9%)
- Eval model: `openai:gpt-4.1` | Eval DB: dev/tiledesk

**Official baseline (observatory, 3,701 real conversations):**
- Autonomous resolution rate: **8%** (300/3,701)
- Total failure rate: **44%**
- Policy API failure rate: **15%** (486/3,198 API calls)
- Missed handoffs: **618** (17%)
- Bad product inquiry outcomes: **437** (51% of 860 product inquiries)
- After-hours wasted conversations: **69** (avg 11 turns)
- Frustrated users: **288** (7.8%)

**Linear tickets (AI-333 parent + 8 sub-issues):**
- AI-334: Reframe report as enhancement summary — **DONE**
- AI-335: Policy number normalization — code PR needed
- AI-336: KB retrieval fix — config change on prod
- AI-337: System prompt + opener — deploying now
- AI-338: Policy tool output — config change on prod
- AI-339: 4-week monitoring — starts after deploy
- AI-340: Handoff diligence — included in prompt, deploying now
- AI-341: CSR conversation summary — included in prompt, deploying now

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
| Enhancement report PDF | File | ~/Repositories/indemn-observability/reports/GIC_Agent_Enhancement_Report_March_13__2026.pdf |
| Report data | File | ~/Repositories/indemn-observability/data/gic-improvement-report.json |
| Report renderer | File | ~/Repositories/indemn-observability/scripts/generate-gic-improvement-report.jsx |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-12 | [ryan-gic-ux-observations](artifacts/ryan-gic-ux-observations.pdf) | Ryan's full UX analysis with 17 observations and 14 screenshots |
| 2026-03-12 | [agent-research](artifacts/2026-03-12-agent-research.md) | Deep research: agent config, backend architecture, policy API, knowledge bases, quantified baselines for all 13 improvement opportunities |
| 2026-03-12 | [opportunity-prioritization](artifacts/2026-03-12-opportunity-prioritization.md) | Prioritization of opportunities using observatory data and actual conversation analysis — 7 active, 5 parked, 2 bundled |
| 2026-03-12 | [evaluation-criteria](artifacts/2026-03-12-evaluation-criteria.md) | Evaluation rubric rules, test case designs, observatory baselines, and projected impact per opportunity |
| 2026-03-12 | [baseline-evaluation-results](artifacts/2026-03-12-baseline-evaluation-results.md) | Baseline eval: 13/15 passed, all rubric rules 100%, 2 handoff workflow failures — full analysis with conversations |
| 2026-03-12 | [v3-baseline-evaluation-results](artifacts/2026-03-12-v3-baseline-evaluation-results.md) | V3 baseline: 7/17 passed (41.2%), 10/10 opportunity items FAIL as expected, perfect calibration |
| 2026-03-12 | [policy-number-analysis](artifacts/2026-03-12-policy-number-analysis.md) | Analysis of 192 real policy lookups — 13 carrier formats, 2 normalization rules fix 100% of addressable failures (63% of total) |
| 2026-03-12 | [retrieval-investigation](artifacts/2026-03-12-retrieval-investigation.md) | KB retrieval root cause: wrong Pinecone namespace + wrong KB ID filter. Prod bot has no faqs-retriever tool at all. |
| 2026-03-12 | [post-implementation-evaluation-results](artifacts/2026-03-12-post-implementation-evaluation-results.md) | Post-implementation eval: 12/17 (70.6%) vs baseline 7/17 (41.2%). 5 items flipped, 0 regressions. |
| 2026-03-13 | [revised-deployment-plan](artifacts/2026-03-13-revised-deployment-plan.md) | Revised plan based on Kyle's feedback — ship together, track individually, reframe report, add handoff diligence + CSR summary |

## Decisions
- 2026-03-12: Project created to track GIC agent improvement work per Kyle's directive
- 2026-03-12: Prioritization complete — 7 active opportunities selected based on observatory data
- 2026-03-12: Parked slot-filling (#1), tone (#2), constraint surfacing (#8), "thank you" closure (#9), boolean bug (#12)
- 2026-03-12: KB retrieval root cause — wrong Pinecone namespace + KB ID. Prod bot has NO faqs-retriever tool.
- 2026-03-12: Post-implementation eval: 12/17 (70.6%) vs baseline 7/17 (41.2%). Zero regressions.
- 2026-03-13: Kyle directive — ship fixes now, don't wait for GIC approval. Reframe report as enhancement summary.
- 2026-03-13: Contact collection (#13) deprioritized per Kyle — portal already has broker context via API.
- 2026-03-13: New features added: handoff diligence (AI-340) + CSR conversation summary (AI-341).
- 2026-03-13: Root cause found — bot-service `return_tools()` drops LLM text when a tool call is in the same response. Summary must be in a separate text-only turn before handoff triggers.
- 2026-03-13: Two-turn handoff approach: agent posts summary + asks "Shall I connect you now?" (text only) → user confirms → handoff triggers. Eval confirmed 15/19 (78.9%).
- 2026-03-13: Report reframed — stripped internal gaps (KB disconnected, quote collection, silent handoffs). Enhancement-focused. PDF generated.
- 2026-03-13: Kyle: first message needs JC approval before changing. Hold on first_message update.
- 2026-03-13: Kyle: wants Ryan's perspective on shipping and messaging around changes.

## Open Questions
- JC approval on first message — Kyle says JC is particular about the greeting
- Ryan's perspective on shipping and messaging around changes
- Policy number normalization — PR to operations_api still needs to be created and deployed
- Production KB deployment — faqs-retriever tool + namespace fix + KB mapping + top_k need to be applied via UI or MongoDB
- Pinecone deduplication: ~5x duplicate vectors — clean up, or leave and compensate with higher top_k?
