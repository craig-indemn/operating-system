# OS Evaluations

Running evaluations on prod agents via the Copilot Dashboard with local services pointed at production infrastructure. Includes Jarvis improvements for evaluation workflow reliability.

## Status
Session 2026-03-04-a. Services running locally on prod (bot-service:8001, evaluations:8002, platform-v2:8003, copilot-server:3000, copilot-dashboard:4500, federation:5173). An evaluation run is currently in progress (run_id: 950d3466-9e8, agent: 68f7e0ae8d5cbe00140d).

### What was done this session:
- Started all services pointed at **prod** MongoDB/Redis/RabbitMQ using `local-dev-aws.sh start <group> --env=prod`
- Fixed React component errors in Copilot Dashboard by replacing Vite dev server with **federation build** on :5173 (`npm run build:federation && npx serve dist-federation -l 5173 --cors -n`)
- Fixed Jarvis using wrong template: prod `jarvis-default` agent was still on `jarvis_evaluation_v1` (subagents). Deleted agent, restarted platform-v2 to recreate from `jarvis_evaluation_v2` (skills-based, no subagents). Template ObjectIds: v1=`69776f4c43d5b0d6ec4cbb3f`, v2=`69a06d3d3237b08ea557027a`
- Fixed `data` field schema bug in evaluation connectors: removed `default=None` from `data` field in `RubricsInput`, `QuestionSetsInput`, `TestSetsInput` so Pydantic puts `data` in `required` array. Previously LLM omitted `data` on create calls because schema said optional. Change in `percy-service/indemn_platform/connectors/implementations/platform_api/evaluations.py` — **not yet committed or pushed**
- Investigated prod bot-service outage: `bot.indemn.ai` was down (ALB target unhealthy, timeout on :8001). Instance `i-00ef8e2bfa651aaa8` (prod-services). Container `bot-service-app-1` had high CPU (~90% container-level). RabbitMQ reconnect storms in logs. Recovered on its own. No container-level historical metrics available (Datadog agent not reachable on host).

### Next steps:
- Evaluation run in progress — check results when complete
- **Commit and push** the percy-service schema fix
- Run more evaluations on prod agents (user mentioned "slightly more involved" next eval)
- Consider adding Datadog agent to prod-services instance for container metrics

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

## External Resources
| Resource | Type | Link |
|----------|------|------|
| percy-service | GitHub | indemn-ai/percy-service (main) |
| Prod bot-service | AWS ALB | prod-bot-service (instance i-00ef8e2bfa651aaa8) |
| Prod MongoDB | Atlas | prod-indemn.3h3ab.mongodb.net |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|

## Decisions
- 2026-03-04: Switched Jarvis from v1 (subagents) to v2 (skills-based) template in prod
- 2026-03-04: Fixed connector schema by removing `default=None` from `data` field — minimal fix over full connector split refactor
- 2026-03-04: platform-v2 startup code doesn't migrate existing agents to new templates — it only creates if missing. Must delete agent to force recreation.

## Open Questions
- Should startup code in main.py update existing agents when template version changes? (Currently just reuses old agent)
- Prod bot-service resource issues — needs investigation into container limits and Datadog agent setup
- percy-service schema fix needs to be committed and pushed to remote
