# Voice Analytics

Generate voice and web chat analytics reports for customers — Rankin Insurance (voice agent retrospective) and Distinguished (Cyber Agent web chat metrics). Includes fixing Observatory ingestion pipeline bugs and running data hydration locally against production.

## Status
**Session 2026-03-09-a** (IN PROGRESS): Slack requirements gathered, data explored, Observatory ingestion bug found and fixed, pipeline run for both orgs. Both Rankin (203 convos) and Distinguished (86 convos) are hydrated in the Observatory. Reports not yet generated.

**Next**: Review Observatory in browser, generate Distinguished Cyber report (EOD deadline), generate Rankin 2-week voice report, commit bug fix.

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

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-09 | [session-handoff](artifacts/2026-03-09-session-handoff.md) | Full session context: Slack requirements, data discovery, bug fix, pipeline execution, what's left to do |

## Decisions
- 2026-03-09: Rankin voice report uses existing `generate-voice-report.jsx` — same format as Feb 5 report, extended to 2-week date range
- 2026-03-09: Distinguished Cyber Agent has only 1 non-test conversation March 5-9 — need to confirm with Ganesh/Peter before generating report
- 2026-03-09: Observatory `get_all_bot_ids` bug fixed locally (id_project → id_organization) — not committed yet
- 2026-03-09: Run Observatory locally pointed at prod for data ingestion — prod Observatory is down until Wednesday
- 2026-03-09: Use `reuse_classifications=true` for ingestion to avoid re-classifying already-processed conversations

## Open Questions
- Should Distinguished report include test conversations from March 4? Or expand date range beyond March 5-9?
- Should Distinguished report include Internal User Assistant data (6 real convos) or just Cyber Agent?
- What format does Jonathan want for the two-report split (customer-facing vs internal voice benchmark)?
- When will Observatory prod deploy (PR #28) happen? Craig said mid-week.
