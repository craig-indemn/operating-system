# OS Evaluations

Running evaluations on prod agents via the Copilot Dashboard with local services pointed at production infrastructure. Includes Jarvis improvements for evaluation workflow reliability.

## Status
Session 2026-03-05-a (continued from 2026-03-04-a). Services running locally on prod. Family First evaluation run completed: **21/52 passed (40%)** — run_id `625f7a2f-2f11-44be-b639-f91e6098d95c`. Results not yet analyzed.

### What was done across sessions:

**Session 2026-03-04-a:**
- Started all services pointed at **prod** MongoDB/Redis/RabbitMQ using `local-dev-aws.sh start <group> --env=prod`
- Fixed React component errors in Copilot Dashboard by replacing Vite dev server with **federation build** on :5173
- Fixed Jarvis using wrong template: deleted `jarvis-default` agent, restarted platform-v2 to recreate from `jarvis_evaluation_v2` (skills-based, no subagents). Template ObjectIds: v1=`69776f4c43d5b0d6ec4cbb3f`, v2=`69a06d3d3237b08ea557027a`
- Fixed `data` field schema bug in evaluation connectors: removed `default=None` from `data` field in `RubricsInput`, `QuestionSetsInput`, `TestSetsInput` — **not yet committed/pushed to percy-service**
- Investigated prod bot-service outage: high CPU, RabbitMQ reconnect storms, recovered on its own
- First eval run completed on agent `68f7e0ae8d5cbe00140d` (11/14 passed)

**Session 2026-03-05-a:**
- Exported first eval run conversation traces as markdown + PDF for teammate review
- Created `markdown-pdf` skill (`npx md-to-pdf`) and updated `eval-analysis` skill with export workflow
- Pre-processed colleague's large evaluation input (52 criteria + rubric rules) for Family First agent (`6834acd94ae4060013f3e747`):
  - Pulled 40/41 conversation transcripts from prod MongoDB (#22 missing)
  - Split colleague's rubric into 6 universal rules + workflow-specific criteria moved to test items
  - Created consolidated doc mapping colleague's terminology to our framework
- Created rubric via API: `ea4f1174-d8ae-4b77-bb4a-aed6f61b61f9` (6 rules)
- Created test set via API: `e67e074f-ed19-4d8f-9edf-f6c828d63071` (52 items: 39 single-turn, 13 scenarios)
- Triggered Family First evaluation — **completed: 21/52 passed (40%)**

### Next steps:
- **Analyze Family First eval results** — run `/eval-analysis 625f7a2f-2f11-44be-b639-f91e6098d95c` to classify failures
- **Commit and push** the percy-service schema fix (still uncommitted)
- Share results with colleague — export traces + PDF
- Iterate on test set/rubric based on analysis findings

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

## Open Questions
- Should startup code in main.py update existing agents when template version changes? (Currently just reuses old agent)
- Prod bot-service resource issues — needs investigation into container limits and Datadog agent setup
- percy-service schema fix needs to be committed and pushed to remote
- Family First 40% pass rate — need failure analysis to determine agent issues vs eval issues
- Conversation #22 missing from prod MongoDB — may need to investigate or remove from test set
