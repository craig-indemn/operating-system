# Platform Development

End-to-end development of the Indemn agent platform — spanning indemn-platform-v2 (V2 agent builder + Jarvis), the evaluation harness, copilot-dashboard (Angular config UI), and supporting services. Covers debugging, feature development, and refinement of the full stack from agent configuration through evaluation and deployment.

## Status
**Session 2026-02-24-a** (IN PROGRESS): Deep-diving into Dhruv's evaluations feedback (COP-325 — 10 issues + 3 from Dolly + 3 strategic asks from Slack). Building comprehensive spec for each item before implementing. Issues 1-6 fully written up (Issue 4 folded into Issue 3). Issues 7-14 + strategic asks S1-S3 still need spec files. Key finding: federated component colors must match the copilot-dashboard Angular host (`$brand-primary: #1E40AF`, blue/slate palette), NOT the React app's own design system. All context preserved in `artifacts/2026-02-24-evaluations-feedback/CONTEXT.md` — READ THIS FILE to resume.

**Previous session (2026-02-23-d)**: Baseline generation feature declared production-ready. Ran 3 evaluations against Wedding Bot. Run 3 results: 15/15 completed, 10 passed, 5 failed, criteria 98%, rubric 91%.

**What's done:**
- Jarvis skills architecture: 9 commits on percy-service main, deployed to dev EC2
- Skills framework: FilesystemBackend + SkillsMiddleware + 3 SKILL.md files
- 3 successful evaluation runs validating quality improvements across iterations
- Rubric: 6 universal rules including no_harmful_content (up from 5)
- Test set: 15 items, 98% criteria pass rate, no criteria/rubric overlap
- Stale resources cleaned up (only 1 rubric + 1 test set per run remain)
- Production readiness checklist created with full deployment plan

**Next session should**:
1. Set up Docker containers for percy-service and evaluations on prod EC2
2. Install self-hosted GitHub Actions runners (prod tags) for both repos
3. Configure prod `.env` files (prod MongoDB Atlas, prod bot-service URL, LangSmith project)
4. Seed `jarvis_evaluation_v2` template on prod MongoDB
5. Push percy-service and evaluations to `prod` branch
6. Create copilot-dashboard PR from `main` to `prod` for team approval
7. Smoke test baseline generation against a prod bot

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
| 2026-02-23 | [jarvis-skills-architecture](artifacts/2026-02-23-jarvis-skills-architecture.md) | Jarvis skills architecture — replaced subagents with SKILL.md files, directive allocation workflow, end-to-end validation against Wedding Bot (9/14 passed, rubric 5 rules, criteria 88%, rubric rules 94%) |
| 2026-02-23 | [prod-readiness-checklist](artifacts/2026-02-23-prod-readiness-checklist.md) | Production readiness checklist for Jarvis baseline generation — Docker setup, runners, env vars, template seeding, deploy order, smoke test |
| 2026-02-24 | [evaluations-feedback/CONTEXT.md](artifacts/2026-02-24-evaluations-feedback/CONTEXT.md) | COP-325 deep dive master context — methodology, architecture, all 17 issues, progress tracker, dev access, next steps |
| 2026-02-24 | [evaluations-feedback/issue-01](artifacts/2026-02-24-evaluations-feedback/issue-01-matrix-question-and-tool-log.md) | Issue 1: Raw dict in matrix + tool log causing false R05 failures — root caused with live data |
| 2026-02-24 | [evaluations-feedback/issue-02](artifacts/2026-02-24-evaluations-feedback/issue-02-date-rendering.md) | Issue 2: Date column wrapping — needs whitespace-nowrap |
| 2026-02-24 | [evaluations-feedback/issue-03](artifacts/2026-02-24-evaluations-feedback/issue-03-purple-theme.md) | Issue 3+4: Purple theme + card background — 4 violations across 6 files, grounded in Angular host colors |
| 2026-02-24 | [evaluations-feedback/issue-05](artifacts/2026-02-24-evaluations-feedback/issue-05-remove-metadata.md) | Issue 5: Remove Run ID + Agent ID from run detail — internal IDs not for end users |
| 2026-02-24 | [evaluations-feedback/issue-06](artifacts/2026-02-24-evaluations-feedback/issue-06-matrix-not-showing.md) | Issue 6: Matrix not showing — V2 defaults to cards view, not data issue. Default to matrix when rubric present |

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
- 2026-02-23: Jarvis skills architecture replaces subagent approach. Single agent with SKILL.md files (eval-orchestration, rubric-creation, test-set-creation) loaded via deepagents FilesystemBackend. Directive allocation workflow classifies directives before creating rubric/test set.
- 2026-02-23: V2 rubric should have exactly 3-6 universal rules. The directive allocation 3-message test (greeting, off-topic, utility) is the hard structural gate, not soft guidance.
- 2026-02-23: Headless Jarvis must NOT poll run status. Report IDs and stop. The job runner handles completion tracking.
- 2026-02-23: Local evaluations repo was on `feat/ff_evaluation` branch (stale). Deployed version is from `main`. Always use `main` branch.
- 2026-02-23: Baseline generation feature is production-ready. Generates quality rubrics (6 rules) and test sets (15 items) consistently across 3 runs.
- 2026-02-23: Bot echo on handoff failure is a real bot-service bug, not a UI or eval harness issue. Confirmed via raw conversation transcript in MongoDB.
- 2026-02-23: Single-turn items having extra scenario fields (max_turns, persona, initial_message) is cosmetically wrong but functionally harmless — engine dispatches by `type` field and only reads `message` for single-turn.
- 2026-02-23: percy-service and evaluations deploy to prod via pushing to `prod` branch (no PR needed). copilot-dashboard requires PR from `main` to `prod` with team approval.
- 2026-02-23: Evaluations container uses `MONGODB_URI` and `MONGODB_DATABASE` env vars (not `MONGO_URL`/`MONGO_DB_NAME` like percy-service).
- 2026-02-24: Federated React component colors must match the copilot-dashboard Angular host palette (`$brand-primary: #1E40AF`, `tw-bg-white`, `tw-text-slate-800`, Tailwind blue family), NOT the React app's own `index.css` design system (`--color-iris: #4752a3`).
- 2026-02-24: Scenario vs single_turn type badges use different blue shades (blue-500 vs blue-800) to maintain differentiation within the Angular palette.
- 2026-02-24: Issue 4 (card background `#f8f9fc`) folded into Issue 3 — same root cause (federated components not matching Angular host).
- 2026-02-24: V1/V2 data format mismatch hypothesis was wrong — backend populates BOTH `scores` (V1 keys) and `rubric_scores`/`criteria_scores` (V2 arrays) on the same result. `buildMatrixData()` works fine with V2 results.

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
- ~~The evaluations service on dev has a `/api/v1/bots/{bot_id}/context` endpoint that doesn't exist in the local evaluations repo. Is the deployed code ahead of the local repo? Or is there a different service handling this?~~ → ANSWERED: Local repo was on stale `feat/ff_evaluation` branch. Deployed is from `main` which has all the V2 endpoints. Updated local to `main`.
- ~~Should the rubric architecture shift from "generate from scratch" to "fixed template + minimal customization" (Option D in root cause artifact)?~~ → RESOLVED: Skills architecture with directive allocation workflow is the solution. V2 rubric (5 universal rules) validated with end-to-end eval.
- `LengthFinishReasonError` on long scenario evaluations — one rubric evaluator hit OpenAI's 32K token limit. Non-blocking but worth investigating whether max_tokens needs to be raised or the evaluator prompt needs trimming.
- **Eval harness needs session init payload support** — Scenarios start as fresh conversations with no pre-existing state. Real bot conversations get initial parameters (event_date, venue, etc.) injected via session start payloads. Without this, scenarios testing modification of session-initialized data produce meaningless results (bot tries to validate as new input instead of recognizing a modification request). Need to add `session_init_payload` (or similar) to the scenario inputs format and wire it through the multi-turn engine. This is a coverage gap that limits what the harness can test — all session-dependent behaviors are currently blind spots.
- **Date validation API returning incorrect results** — The `validate_date` tool returns "date is in the past" for future dates (June 2025, July 2025). Exposed during the Non-Contact Data Modification scenario. Likely a test environment issue or a bug in the validation endpoint.
- **Bot catastrophic degradation on handoff failure** — When the `human_handoff_slack_notification` tool fails (`invalid_token`), the bot echoes the user's first message verbatim instead of gracefully handling the error. This is a bot-service behavior bug.
