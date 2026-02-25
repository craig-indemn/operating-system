# O'Connor Evaluations

Running and refining AI agent evaluations for O'Connor Insurance Associates using the Jarvis skills-based framework (v2). Covers baseline generation, result analysis, bug fixes in the evaluation pipeline, and iterative improvement of rubrics and test sets across all 4 O'Connor agents.

## Status
**Session 2026-02-25-b** (IN PROGRESS): Deep analysis of Internal Operations Associate eval results. Fixed connector validation, handoff echo bug in eval harness, test set criteria, and rubric evaluator prompt. Built `/eval-analysis` skill. Three eval runs completed with progressive improvements (8/13 → 9/13 → 10/13). Fourth run in progress with tool trace stripping for rubric evaluators.

**Results progression (Internal Operations Associate):**
- Run 1 (`74ed9dd0`, test set v1): **8/13 passed** — 2 false failures (bad criteria), 2 handoff echo bugs, 1 KB retrieval
- Run 2 (`92a9df66`, test set v2): **9/13 passed** — fixed criteria for items 5, 8, 11
- Run 3 (`139afa11`, test set v3): **10/13 passed** — fixed evaluator prompt for handoff + tool traces
- Run 4 (in progress, test set v3): testing tool trace stripping from rubric evaluators

**Remaining 3 failures in run 3:**
1. Off-Topic Request (Taxes) — criteria too strict ("clearly communicates its role"), agent declined correctly but didn't state job title
2. Confused User — rubric evaluator still seeing public URLs from inline tool traces (fix: strip tool traces from rubric evaluator outputs)
3. Live Handoff (HR) — handoff echo still showing in transcript, rubric flags incoherence (fix: strip tool traces + handoff artifacts)

**Code changes this session (uncommitted in respective repos):**
- `evaluations/src/indemn_evals/engine/multi_turn_simulated.py` — echo fix: check `has_tool_calls` before using `model_output.content`
- `evaluations/src/indemn_evals/engine/single_turn.py` — same echo fix
- `evaluations/src/indemn_evals/api/routes/evaluations.py` — evaluator prompt: handoff behavior in eval mode, tool trace = internal processing
- `evaluations/src/indemn_evals/evaluators/builders.py` — `_strip_tool_traces()` + `_clean_outputs_for_rubric()`: strip tool execution traces from rubric evaluator outputs
- `percy-service/indemn_platform/connectors/implementations/platform_api/evaluations.py` — pre-flight validation for RubricsConnector, QuestionSetsConnector, TestSetsConnector

**OS changes this session:**
- Created `/eval-analysis` skill at `.claude/skills/eval-analysis/SKILL.md` with `references/data-shapes.md`
- Added `/eval-analysis` to CLAUDE.md Workflow Skills table

## External Resources
| Resource | Type | Link |
|----------|------|------|
| percy-service | GitHub repo + local | indemn-ai/percy-service, `/Users/home/Repositories/percy-service` |
| evaluations | GitHub repo + local | indemn-ai/evaluations (branch: main), `/Users/home/Repositories/evaluations` |
| copilot-dashboard | GitHub repo + local | indemn-ai/copilot-dashboard, `/Users/home/Repositories/copilot-dashboard` |
| indemn-platform-v2 | GitHub repo + local (UI only) | `/Users/home/Repositories/indemn-platform-v2` |
| bot-service | GitHub repo + local | `/Users/home/Repositories/bot-service` |
| copilot-server | GitHub repo + local | `/Users/home/Repositories/copilot-server` |
| O'Connor Org (prod) | MongoDB | org_id: `696b1e23ec2b21075fce4c76` |
| O'Connor Org (prod, duplicate) | MongoDB | org_id: `6983ddb7803dd0ae14767eba` (0 bots) |
| LangSmith | Eval traces | https://smith.langchain.com/o/eb08d154-04ac-4397-af57-6bc89a71e751 |
| Platform Development project | OS project | `projects/platform-development/` (parent project with full eval framework context) |

## O'Connor Agents (Prod)
| Bot ID | Name | Eval Status |
|--------|------|-------------|
| 696b1e35ec2b21075fce4cc2 | O'Connor External Engagement Associate | Rubric + 15-item test set ready (`e9934f60`, `2eaf824e`). Not yet run. |
| 696fb30cec2b21075fd315b7 | Sandy, for O'Connor (Billing, Personal) | No rubric or test set — needs Jarvis generation |
| 696fc955ec2b21075fd37426 | O'Connor Internal Operations Associate | **10/13 passed** (rubric: `ff45b89d`, test set: `c3da2631` v3, latest run: `139afa11`). Run 4 in progress. |
| 697bca8eec2b21075feff641 | Coral, for O'Connor (Billing, Commercial Lines) | No rubric or test set — needs Jarvis generation |

## Local Dev Startup (Prod)
```bash
# Full federation stack on prod — run from /Users/home/Repositories
/opt/homebrew/bin/bash ./local-dev.sh start platform --env=prod
/opt/homebrew/bin/bash ./local-dev.sh start copilot-server --env=prod
/opt/homebrew/bin/bash ./local-dev.sh start copilot-dashboard --env=prod

# Platform-v2 needs manual restart with correct env:
lsof -ti :8003 | xargs kill -9 2>/dev/null
cd percy-service && set -a && source ../.env.prod && set +a && \
  export SKILLS_ROOT="/Users/home/Repositories/percy-service/skills" && \
  export MONGO_DB_NAME="indemn_platform" && \
  uv run uvicorn indemn_platform.api.main:app --port 8003 --reload > ../.logs/platform-v2.log 2>&1 &

# Evaluations needs main branch + correct env:
cd evaluations && git checkout main
# Note: evaluations/.env has MONGODB_DATABASE=tiledesk (correct — all data in tiledesk)

# Federation bundle (instead of Vite dev server):
lsof -ti :5173 | xargs kill -9 2>/dev/null
cd indemn-platform-v2/ui && npm run build:federation && npx serve dist-federation -l 5173 --cors -n &

# Login: support@indemn.ai / nzrjW3tZ9K3YiwtMWzBm
# Dashboard: http://localhost:4500
```

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|

## Decisions
- 2026-02-25: All evaluation data (rubrics, test sets, runs, results) lives in `tiledesk` database, not a separate `evaluations` database. The evaluations/.env has `MONGODB_DATABASE=tiledesk`.
- 2026-02-25: Jarvis uses `jarvis_evaluation_v2` template (skills-based, Sonnet 4.6, no subagents). Template ID is the default in percy-service code.
- 2026-02-25: Platform-v2 (percy-service) needs `MONGO_DB_NAME=indemn_platform` override when started locally on prod, because `.env.prod` sets it to `tiledesk`.
- 2026-02-25: `SKILLS_ROOT` env var must be set to `/Users/home/Repositories/percy-service/skills` for local dev. Code change in `deep_agent.py` prioritizes env var over template config.
- 2026-02-25: `local-dev.sh` updated: platform-v2 backend directory changed from `indemn-platform-v2` to `percy-service`, MongoDB validation grep fixed.
- 2026-02-25: Connector validation added to all three CRUD connectors (rubrics, question_sets, test_sets) — prescriptive error messages so Jarvis can self-correct on retry.
- 2026-02-25: Eval harness echo fix — when LLM generates tool_calls, `model_output.content` is "thinking" (echo), not the agent response. Use `bot_message` instead. Fix in both `multi_turn_simulated.py` and `single_turn.py`. Note: fix is deployed but doesn't fully resolve because bot-service streaming.py returns echo as `bot_message` too (uses `messages[0].content` instead of graph state `bot_message`). Real fix needs bot-service change.
- 2026-02-25: Rubric evaluators should NOT see tool execution traces. Tool traces are internal agent processing, not user-facing output. Implemented via `_strip_tool_traces()` in builders.py.
- 2026-02-25: Criteria evaluators SHOULD see tool traces — they need evidence of tool usage (e.g., "Agent retrieves from KB").
- 2026-02-25: Handoff tool always fails in eval mode (no human agents available). Evaluator prompt updated to not penalize conversation artifacts after handoff trigger.
- 2026-02-25: Test set criteria updated 3x: v1→v2 (items 5, 8, 11 corrected), v2→v3 (telecommuting HR redirect made conditional).

## What's Next
1. Check results of run 4 — did tool trace stripping fix the remaining rubric false positives?
2. Fix Off-Topic Request (Taxes) criterion — "clearly communicates its role" too strict
3. Address the bot-service echo bug properly — streaming.py should use graph state `bot_message` not `messages[0].content`
4. Run evaluation for External Engagement Associate (rubric + 15-item test set ready)
5. Generate rubrics + test sets for Sandy and Coral via Jarvis
6. Commit all code changes across evaluations and percy-service repos

## Open Questions
- The O'Connor org exists twice in prod (696b1e23... and 6983ddb7...). Second one has 0 bots. Is this intentional?
- Are there specific evaluation criteria or focus areas the O'Connor team cares about most?
- Should `should_use_tools` / `should_not_use_tools` fields on TestItem be wired into evaluation logic, or remain metadata-only?
