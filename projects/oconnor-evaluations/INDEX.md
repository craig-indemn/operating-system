# O'Connor Evaluations

Running and refining AI agent evaluations for O'Connor Insurance Associates using the Jarvis skills-based framework (v2). Covers baseline generation, result analysis, bug fixes in the evaluation pipeline, and iterative improvement of rubrics and test sets across all 4 O'Connor agents.

## Status
**Session 2026-02-25-a** (IN PROGRESS): Set up full local stack on prod (copilot-dashboard, copilot-server, platform-v2/percy-service, evaluations, bot-service, federation bundle). Seeded Jarvis templates + components to prod MongoDB. Fixed multiple configuration issues. First evaluation job completed for 2 of 4 agents.

**Results so far:**
- O'Connor Internal Operations Associate: Eval completed — **8/13 passed** (61.5%), rubric + 13-item test set created
- O'Connor External Engagement Associate: Rubric created, but test set creation failed (422 — Jarvis omitted `data` field). Only 1 test item. Needs re-trigger.
- Sandy (Billing, Personal) and Coral (Billing, Commercial) — not yet evaluated

**Bugs found this session:**
1. `local-dev.sh` MongoDB validation grep pattern wrong (fixed)
2. `local-dev.sh` platform-v2 directory pointed to `indemn-platform-v2` instead of `percy-service` (fixed)
3. `deep_agent.py` skills_root resolution — `/app/skills` (Docker path) takes priority over local path (fixed — SKILLS_ROOT env var now checked first)
4. Platform-v2 using `MONGO_DB_NAME=tiledesk` for its own DB instead of `indemn_platform` (fixed — override env var at startup)
5. Evaluations repo on stale `feat/ff_evaluation` branch — V2 endpoints missing (fixed — switched to `main`)
6. Env vars not exported when manually starting services (fixed — use `set -a` before sourcing `.env.prod`)
7. Intermittent 422 on test-set creation — Jarvis (Sonnet 4.6) sometimes omits `data` field in tool call (known LLM non-determinism, not a code bug)

**What's next:**
1. Re-trigger evaluation for O'Connor External Engagement Associate (bot 1 that failed)
2. Run evaluations for Sandy and Coral
3. Analyze the 8/13 results for Internal Operations Associate — which 5 failed and why?
4. Iterate on rubrics and test sets based on results
5. Fix the 422 intermittent issue if possible (strengthen connector validation or add retry)

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
| 696b1e35ec2b21075fce4cc2 | O'Connor External Engagement Associate | Rubric created, test set failed (1 item). Needs re-run. |
| 696fb30cec2b21075fd315b7 | Sandy, for O'Connor (Billing, Personal) | Not evaluated |
| 696fc955ec2b21075fd37426 | O'Connor Internal Operations Associate | **8/13 passed** (rubric: ff45b89d, test set: c3da2631, run: 74ed9dd0) |
| 697bca8eec2b21075feff641 | Coral, for O'Connor (Billing, Commercial Lines) | Not evaluated |

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

## Open Questions
- Why does Jarvis intermittently omit the `data` field on test-set creation? Can we add connector-level validation to return a clear error and retry?
- Should we add a retry mechanism in the Jarvis job runner for recoverable 422 errors?
- The O'Connor org exists twice in prod (696b1e23... and 6983ddb7...). Second one has 0 bots. Is this intentional?
- Are there specific evaluation criteria or focus areas the O'Connor team cares about most?
