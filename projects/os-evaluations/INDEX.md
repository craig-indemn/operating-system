# OS Evaluations

Running evaluations on prod agents via the Copilot Dashboard with local services pointed at production infrastructure. Includes Jarvis improvements for evaluation workflow reliability.

## Status
Session 2026-03-17-a. Added ACIC UW Guide test scenarios to Union General agents and ran full evaluations against production.

### What was done across sessions:

**Session 2026-03-17-a:**
- Switched indemn CLI to Union General org (`67e57ba379a7c700139e3a12`); discovered CLI doesn't work in production — used evaluations REST API directly (`https://evaluations.indemn.ai/api/v1/`)
- Identified 3 Union General agents: acic uw (`686333d252e924001306e994`), super agent (`69a892039515d60623907783`), nf/sic uw (`698cb861596eb483e4ce4de0`)
- Added 1 new scenario to each test set for NF/SIC UW and Super Agent testing retrieval from the new `ACIC UW guides` FILE KB (`69b8578ba89eea32b494c5fe`)
- Ran full evaluations — **Super Agent: 14/16 (88%)**, **NF/SIC UW: 7/17 (41%)**. Both new ACIC UW Guide scenarios passed 4/4 criteria.
- Investigated recurring null-output bug on NF/SIC UW multi-turn scenarios — root cause: unhandled `httpx` exceptions in `_invoke_bot_sync()` across all 3 eval engines
- Fixed: wrapped HTTP calls with try/except in `multi_turn_simulated.py`, `multi_turn_replay.py`, `single_turn.py` — returns structured `[ERROR: ...]` message instead of silent null
- PR pushed: https://github.com/craig-indemn/evaluations/pull/3 (`fix/handle-bot-service-errors`)
- Concurrency 1 run eliminated most null outputs (1 remaining: "No-Match Handling" — likely bot-service itself timing out on no-match KB queries)

**Session 2026-03-05-a:**
- Exported first eval run conversation traces as markdown + PDF for teammate review
- Created `markdown-pdf` skill (`npx md-to-pdf`) and updated `eval-analysis` skill with export workflow
- Pre-processed colleague's large evaluation input (52 criteria + rubric rules) for Family First agent (`6834acd94ae4060013f3e747`)
- Created rubric via API: `ea4f1174-d8ae-4b77-bb4a-aed6f61b61f9` (6 rules)
- Created test set via API: `e67e074f-ed19-4d8f-9edf-f6c828d63071` (52 items: 39 single-turn, 13 scenarios)
- Triggered Family First evaluation — **completed: 21/52 passed (40%)**

**Session 2026-03-04-a:**
- Started all services pointed at **prod** MongoDB/Redis/RabbitMQ using `local-dev-aws.sh start <group> --env=prod`
- Fixed React component errors in Copilot Dashboard by replacing Vite dev server with **federation build** on :5173
- Fixed Jarvis using wrong template: deleted `jarvis-default` agent, restarted platform-v2 to recreate from `jarvis_evaluation_v2` (skills-based, no subagents)
- Fixed `data` field schema bug in evaluation connectors — **not yet committed/pushed to percy-service**
- First eval run completed on agent `68f7e0ae8d5cbe00140d` (11/14 passed)

### Next steps:
- **Merge PR #3** (`fix/handle-bot-service-errors`) and deploy to production evaluations service
- **Investigate "No-Match Handling" persistent null** — bot-service may hang on no-match KB queries; check bot-service logs/timeouts
- **Analyze Family First eval results** — run `/eval-analysis 625f7a2f-2f11-44be-b639-f91e6098d95c` to classify failures
- **Commit and push** the percy-service schema fix (still uncommitted)
- **NF/SIC UW at 41%** — many failures are real agent issues (scope boundary, legal advice, vague query handling); may need prompt tuning

## Currently Running Services (prod)
| Service | Port | How Started |
|---------|------|-------------|
| bot-service | 8001 | `local-dev-aws.sh start platform --env=prod` |
| evaluations | 8002 | (same group) |
| platform-v2 | 8003 | (same group) |
| platform-v2-ui (federation) | 5173 | `npx serve dist-federation -l 5173 --cors -n` |
| copilot-server | 3000 | `local-dev-aws.sh start copilot-server --env=prod` |
| copilot-dashboard | 4500 | `local-dev-aws.sh start copilot-dashboard --env=prod` |

## Key Commands
```bash
# Start services on prod
cd /Users/home/Repositories && local-dev-aws.sh start platform --env=prod
local-dev-aws.sh start copilot-server --env=prod
local-dev-aws.sh start copilot-dashboard --env=prod

# Federation build (required for React components in Angular dashboard)
lsof -ti :5173 | xargs kill -9 2>/dev/null
cd /Users/home/Repositories/indemn-platform-v2/ui && npm run build:federation && npx serve dist-federation -l 5173 --cors -n &

# Login: support@indemn.ai / nzrjW3tZ9K3YiwtMWzBm
# Dashboard: http://localhost:4500
```

## Key IDs
| What | ID |
|------|-----|
| Union General org | `67e57ba379a7c700139e3a12` |
| UG: acic uw agent | `686333d252e924001306e994` |
| UG: super agent | `69a892039515d60623907783` |
| UG: nf/sic uw agent | `698cb861596eb483e4ce4de0` |
| UG: nf/sic uw test set | `6f494864-4b29-46be-a3fa-5481ae38abea` (v2) |
| UG: nf/sic uw rubric | `253a525b-5c1a-462a-8ea1-a21049956432` |
| UG: super agent test set | `c87636de-46a1-442c-8585-1ba88319d50a` (v2) |
| UG: super agent rubric | `46091da9-e804-4780-ab0c-24f418183256` |
| UG: ACIC UW guides KB | `69b8578ba89eea32b494c5fe` (FILE) |
| UG: nf/sic uw best run | `04824e4e-2397-4284-b3a9-9f99c977cb8c` (concurrency 1) |
| UG: super agent best run | `9ea3e76d-a082-46d9-b8cd-3d636b4c6f37` |
| Family First bot | `6834acd94ae4060013f3e747` |
| Family First rubric | `ea4f1174-d8ae-4b77-bb4a-aed6f61b61f9` |
| Family First test set | `e67e074f-ed19-4d8f-9edf-f6c828d63071` |
| Family First eval run | `625f7a2f-2f11-44be-b639-f91e6098d95c` |
| First eval agent (Distinguished) | `68f7e0ae8d5cbe00140d` |
| First eval run | `950d3466-9e8` |

## External Resources
| Resource | Type | Link |
|----------|------|------|
| percy-service | GitHub | indemn-ai/percy-service (main) |
| Prod bot-service | AWS ALB | prod-bot-service (instance i-00ef8e2bfa651aaa8) |
| Prod MongoDB | Atlas | prod-indemn.3h3ab.mongodb.net |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-04 | [eval-conversation-traces](artifacts/2026-03-04-eval-conversation-traces.md) | Pull conversation traces from first eval run for teammate review |
| 2026-03-04 | [family-first-eval-consolidated](artifacts/2026-03-04-family-first-eval-consolidated.md) | Consolidate colleague's evaluation criteria into rubric + test set format |
| 2026-03-04 | [family-first-conversations.json](artifacts/family-first-conversations.json) | Prod conversation transcripts for 40/41 Family First test criteria |

## Decisions
- 2026-03-04: Switched Jarvis from v1 (subagents) to v2 (skills-based) template in prod
- 2026-03-04: Fixed connector schema by removing `default=None` from `data` field — minimal fix over full connector split refactor
- 2026-03-04: platform-v2 startup code doesn't migrate existing agents to new templates — it only creates if missing. Must delete agent to force recreation.
- 2026-03-05: Colleague's rubric split into 6 universal rules (rubric) + workflow-specific rules (moved to test item criteria). Rubric hard cap of 3-6 rules enforced.
- 2026-03-05: Created `markdown-pdf` skill for simple markdown→PDF conversion. Branded reports use `report-library` skill instead.
- 2026-03-17: indemn CLI doesn't work in production yet — use evaluations REST API directly for prod evals
- 2026-03-17: Use `POST /api/v1/evaluations` (V2 endpoint) not `POST /api/v1/runs` (legacy) — V2 auto-creates datasets from test sets
- 2026-03-17: NF/SIC UW agent needs concurrency 1 for reliable multi-turn evals due to bot-service latency on dual-KB retrieval

## Open Questions
- Should startup code in main.py update existing agents when template version changes? (Currently just reuses old agent)
- Prod bot-service resource issues — needs investigation into container limits and Datadog agent setup
- percy-service schema fix needs to be committed and pushed to remote
- Family First 40% pass rate — need failure analysis to determine agent issues vs eval issues
- Conversation #22 missing from prod MongoDB — may need to investigate or remove from test set
- "No-Match Handling" scenario for NF/SIC UW consistently returns null even at concurrency 1 — is bot-service hanging on no-match KB queries?
- NF/SIC UW at 41% — are failures agent prompt issues or eval criteria too strict?
