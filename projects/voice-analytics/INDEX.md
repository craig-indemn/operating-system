# Voice Analytics

Generate voice and web chat analytics reports for customers — Rankin Insurance (voice agent retrospective) and Distinguished (Cyber Agent web chat metrics). Includes fixing Observatory ingestion pipeline bugs and running data hydration locally against production.

## Status
**Session 2026-03-09-b** (COMPLETE): Both customer reports delivered. All code committed, PRs open.

**Completed across sessions a + b:**
- Rankin 2-week voice retrospective PDF (51 calls, Feb 24 – Mar 9): `indemn-observability/reports/Rankin_Insurance_Group_Voice_Retrospective_2026-02-24_to_2026-03-09.pdf`
- Distinguished Internal Agent report PDF (5 conversations, Mar 5-6): `indemn-observability/reports/Distinguished_Programs_Internal_Agent_2026-03-05_to_2026-03-06.pdf`
- New CLI script: `indemn-observability/scripts/generate-distinguished-report.jsx`
- Voice report generator updated: dynamic titles, date display on call detail pages, brand-only pie chart palette
- Observatory bug fix committed: `mongodb.py` `get_all_bot_ids` — `id_project` → `id_organization` (COP-391)
- Pie chart palette fixed to use only brand colors (iris, lilac, eggplant, olive + tints) — no yellow/lime per Jonathan's feedback
- Sent Slack message to Ganesh re: no Cyber Agent data Mar 5-9 (no reply as of Mar 11)
- Linear issues created: COP-391 (bug fix, Ready for Testing), COP-392 (downloadable reports feature, In Progress)
- PRs open on indemn-ai/Indemn-observatory: #29 (→main), #30 (→demo-gic)

**Next:**
1. Merge PRs #29 and #30 once reviewed
2. Follow up with Ganesh on Cyber Agent data — does the 1-conversation finding match expectations?
3. Jonathan's two-report split (customer-facing vs internal voice benchmark) — needs design conversation
4. COP-392: Make CLI reports downloadable from Observatory UI

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo + local | indemn-ai/Indemn-observatory, `/Users/home/Repositories/indemn-observability/` |
| Observatory (local) | Running service | http://localhost:5175 (frontend), http://localhost:8004 (API) |
| Rankin org | MongoDB | org `6953c708922e070f5efb57a7`, project `6953c726922e070f5efb57c3` |
| Distinguished org | MongoDB | org `679b191315e8c30013abdcb0`, project `679b193615e8c30013abdcd2` |
| Langfuse | HIPAA instance | `hipaa.cloud.langfuse.com` via `curl-langfuse.sh` |
| Previous Rankin PDF | File | `indemn-observability/reports/Rankin_Insurance_Group_Voice_Daily_2026-02-05.pdf` |
| Voice report generator | Script | `indemn-observability/scripts/generate-voice-report.jsx` |
| Distinguished report generator | Script | `indemn-observability/scripts/generate-distinguished-report.jsx` |
| PR #29 (→main) | GitHub PR | https://github.com/indemn-ai/Indemn-observatory/pull/29 |
| PR #30 (→demo-gic) | GitHub PR | https://github.com/indemn-ai/Indemn-observatory/pull/30 |
| COP-391 | Linear | Bug: get_all_bot_ids org filter (Ready for Testing) |
| COP-392 | Linear | Downloadable per-customer reports (In Progress) |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-09 | [session-handoff](artifacts/2026-03-09-session-handoff.md) | Full session context: Slack requirements, data discovery, bug fix, pipeline execution, what's left to do |

## Decisions
- 2026-03-09: Rankin voice report uses existing `generate-voice-report.jsx` — same format as Feb 5 report, extended to 2-week date range
- 2026-03-09: Distinguished Cyber Agent has only 1 non-test conversation March 5-9 — confirmed with Ganesh via Slack, awaiting reply
- 2026-03-09: Distinguished report covers Internal User Assistant (5 convos Mar 5-6), not Cyber Agent (insufficient data)
- 2026-03-09: Observatory `get_all_bot_ids` bug fix committed and PR'd (COP-391)
- 2026-03-09: Run Observatory locally pointed at prod for data ingestion — prod Observatory is down until Wednesday
- 2026-03-09: Use `reuse_classifications=true` for ingestion to avoid re-classifying already-processed conversations
- 2026-03-09: Each customer gets their own report version — not reusing GIC's CustomerReportDocument
- 2026-03-09: Pie chart palette uses only brand colors (iris, lilac, eggplant, olive + tints) — no yellow/lime, no off-brand colors

## Open Questions
- What format does Jonathan want for the two-report split (customer-facing vs internal voice benchmark)?
- Does Ganesh confirm the Cyber Agent had essentially no real conversations Mar 5-9?
