# Platform Development

End-to-end development of the Indemn agent platform — spanning indemn-platform-v2 (V2 agent builder + Jarvis), the evaluation harness, copilot-dashboard (Angular config UI), and supporting services. Covers debugging, feature development, and refinement of the full stack from agent configuration through evaluation and deployment.

## Status
**Session 2026-02-23-b**: Deep root cause analysis of the rubric_creator behavior. Traced the full data flow from seed script → DB → deep_agent component → subagent spawning → bot_context call → LLM. **Key correction:** the rubric_creator IS following its prompt — the problem is systemic. The Wedding Bot's system prompt has 10+ workflow-specific directives all using CRITICAL/MUST/MANDATORY language, and the prompt's universal applicability filter is guidance-level (soft), not structural (hard). The bot's system prompt IS stored in bot_configurations (5,153 chars, correcting session-a's finding). The bot_context endpoint returns deduplicated tools (21, not 46). This is a design gap, not a prompt defiance issue. Full root cause artifact created.

**Next session should**:
1. **Fix the rubric_creator prompt** — hard cap (3-6 rules), concrete self-check with 3-message test, negative examples from this failure, explicit "ignore tool descriptions" guidance. See artifact section 5.1.
2. **Consider architectural fix** — fixed rubric template (Option D in artifact section 5.2) flips the paradigm from "generate everything" to "start with standard, customize minimally"
3. **Fix the test_set_creator prompt** — add "single-turn = brand new conversation with NO context" guidance, increase max_turns guidance for deep workflows
4. Rewrite this evaluation's rubric + test set manually (or re-run after prompt fixes)
5. Re-run evaluation with corrected materials
6. Still open: CI/CD runners, prod deployment, bead `nlw`, credential rotation

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-platform-v2 | GitHub repo + local | indemn-ai/copilot-dashboard-react (org), craig-indemn/indemn-platform-v2 (personal) |
| percy-service | GitHub repo + local | indemn-ai/percy-service, `/Users/home/Repositories/percy-service` |
| evaluations | GitHub repo + local | indemn-ai/evaluations, `/Users/home/Repositories/evaluations` |
| copilot-dashboard | GitHub repo + local | indemn-ai/copilot-dashboard, `/Users/home/Repositories/copilot-dashboard` |
| bot-service | GitHub repo + local | indemn-ai/bot-service, `/Users/home/Repositories/bot-service` |
| copilot-server | GitHub repo + local | indemn-ai/copilot-server, `/Users/home/Repositories/copilot-server` |
| Dev EC2 | AWS | devcopilot.indemn.ai, devplatform.indemn.ai, devevaluations.indemn.ai |
| Design docs | Local | `/Users/home/Repositories/indemn-platform-v2/docs/plans/` (80+ docs) |
| Eval V2 Spec | Local | `docs/plans/2026-02-06-evaluation-framework-v2-spec.md` |
| Master Roadmap | Local | `docs/plans/MASTER-ROADMAP.md` |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-19 | [initial-context](artifacts/2026-02-19-initial-context.md) | Comprehensive context doc for LLM sessions covering all services, architecture, evaluation framework, federation, deployment, and current state |
| 2026-02-19 | [css-leakage-investigation](artifacts/2026-02-19-css-leakage-investigation.md) | Root cause analysis of CSS leakage from federation — dual injection via plugin + Shadow DOM, fix is patching remoteEntry.js |
| 2026-02-19 | [session-b-fixes](artifacts/2026-02-19-session-b-fixes.md) | Session summary — CSS fix deployed to dev, Loading... fix PR #958, local-dev and agent-browser skills created |
| 2026-02-19 | [session-c-evals-fix](artifacts/2026-02-19-session-c-evals-fix.md) | Evaluations fix — EVALUATION_SERVICE_URL missing, Jarvis avatar fix, proxy.indemn.ai outage resolution |
| 2026-02-19 | [backend-separation-design](artifacts/2026-02-19-backend-separation-design.md) | Design for separating Python backend into percy-service repo, keeping React frontend in copilot-dashboard-react |
| 2026-02-19 | [session-d-separation-planning](artifacts/2026-02-19-session-d-separation-planning.md) | Session summary — designed separation, 3 review rounds, beads epic p0l with 15 tasks |
| 2026-02-20 | [session-e-separation-execution](artifacts/2026-02-20-session-e-separation-execution.md) | Executed full separation — percy-service live, frontend-only container deployed, runners set up |
| 2026-02-23 | [eventguard-evaluation-audit](artifacts/2026-02-23-eventguard-evaluation-audit.md) | Comprehensive audit of EventGuard baseline evaluation — rubric has 18 rules (should be 5-8), test set has context-dependent single-turn tests, Jarvis prompts match code but subagent isn't following them |
| 2026-02-23 | [rubric-root-cause-analysis](artifacts/2026-02-23-rubric-root-cause-analysis.md) | Deep root cause analysis — rubric_creator IS following its prompt, the issue is systemic: V1 bot prompts mix universal/workflow directives with equal language, and the filter is guidance not structure. Full data flow trace, corrected findings, solution options. |

## Decisions
- 2026-02-19: Project scope is full platform — evals, federation, V2 builder, Jarvis, deployment — all active areas equally.
- 2026-02-19: Evaluations repo `feat/ff_evaluation` branch is NOT active — use `main` branch only.
- 2026-02-19: CSS leakage fix approach — post-process remoteEntry.js in build script rather than forking the vite-plugin-federation plugin.
- 2026-02-19: Loading... fix approach — gate template on `visible` input rather than changing default `isLoading` value.
- 2026-02-19: copilot-dashboard has branch protection — changes go through PRs.
- 2026-02-19: Federation asset URLs require `VITE_FEDERATION_BASE_URL` as build arg — absolute URLs needed for cross-origin federation.
- 2026-02-19: Platform-v2 Docker container needs `EVALUATION_SERVICE_URL=http://evaluations:8080` in `.env` for backend connector calls (nginx proxy only handles browser requests).
- 2026-02-19: Backend/frontend separation — percy-service gets Python backend, copilot-dashboard-react keeps React frontend. Two containers, nginx proxies to percy-service. Design doc reviewed 3x.
- 2026-02-19: Jarvis → Percy rename is repo-name only. Code stays "Jarvis" internally.
- 2026-02-19: uvicorn must run with --workers 1 (background tasks + in-memory state). Current --workers 2 is a latent bug.
- 2026-02-20: nginx:alpine needs explicit `mkdir -p` for `/var/lib/nginx` and `/var/cache/nginx` before `chown` — these dirs don't exist by default.
- 2026-02-20: percy-service dev port is 8013 (not 8003) because old combined container still uses 8003. Switch after old container is retired.
- 2026-02-20: Self-hosted runners are per-repo at `~/actions-runner-<service>/` on EC2, installed as systemd services.
- 2026-02-23: V1 evaluation data lives in tiledesk DB (not the separate evaluations DB). Query via percy-service container on dev EC2.
- 2026-02-23: Rubric should be 3-5 universal rules only (no hallucination, professional tone, stays in scope, parameter validation, no harmful content). Workflow-specific rules belong in scenario criteria.
- 2026-02-23: Single-turn tests must NOT assume mid-conversation context. If it needs prior workflow steps, it must be a multi-turn scenario.
- 2026-02-23: EventGuard bot workflow has 12+ steps — scenarios testing late-stage behavior need 12-18 max_turns.
- 2026-02-23: Local machine cannot reach dev MongoDB Atlas directly (IP whitelist). Must SSH to EC2 and query via percy-service container (`sudo docker exec percy-service python3 -c "..."`).
- 2026-02-23: Rubric_creator subagent prompt IS faithfully passed (verified full chain: seed script → DB → DeepAgentComponent → deepagents library → LLM). No truncation or modification.
- 2026-02-23: Wedding Bot system prompt IS stored in bot_configurations.ai_config.system_prompt (5,153 chars). Previous session's finding that it wasn't found was incorrect.
- 2026-02-23: bot_context endpoint (http://evaluations:8080/api/v1/bots/{id}/context) returns deduplicated tools (21, not raw 46). Endpoint exists on dev but NOT in local evaluations repo.
- 2026-02-23: The rubric over-generation is a systemic design issue, not prompt defiance. V1 bot system prompts conflate universal and workflow directives with equal language strength. The rubric_creator's universal applicability filter is guidance-level and fails against dense workflow prompts.

## Open Questions
- ~~What architecture choices need to be made? (bead `5q2`)~~ → Superseded by separation epic `p0l`
- ~~Is the CI/CD runner for copilot-dashboard-react fixable, or should we set up a new one?~~ → percy-service dev runner set up. copilot-dashboard-react dev runner still needed.
- ~~`deepagents>=0.2` — is this a private package?~~ → CI build passed, so it resolves. Not a private package.
- Should `INDEMN_EVALUATION_SERVICE_URL` in dev `.env` be renamed to `EVALUATION_SERVICE_URL` to match the code? Or should the code support both?
- Stuck evaluation run from Feb 9 (0/40 completed) — clean up or leave?
- ~~`test_env` file in copilot-dashboard-react contains real API keys committed to git~~ → File removed. Credentials should still be rotated since they were in git history.
- ~~Why does the rubric_creator subagent ignore the 5-8 rule limit and universal applicability guidance?~~ → ANSWERED: Subagent IS following the prompt. The issue is systemic — V1 bot system prompts mix universal/workflow directives with equal language, and the filter is guidance-level not structural. See rubric-root-cause-analysis artifact.
- ~~Wedding Bot has 46 tools (duplicates of ~23 unique). Why are tools duplicated?~~ → PARTIALLY ANSWERED: The bot_context endpoint returns 21 deduplicated tools. The raw DB has 46 but the evaluation framework handles dedup. Duplication in DB may be a copilot-dashboard UI issue.
- Flow init scenarios need venue initial payload flags — does the evaluation framework support injecting initial context/payload into test runs?
- Slack `human_handoff_slack_notification` returns `invalid_token` on dev — token needs refresh/configuration.
- The evaluations service on dev has a `/api/v1/bots/{bot_id}/context` endpoint that doesn't exist in the local evaluations repo. Is the deployed code ahead of the local repo? Or is there a different service handling this?
- Should the rubric architecture shift from "generate from scratch" to "fixed template + minimal customization" (Option D in root cause artifact)?
