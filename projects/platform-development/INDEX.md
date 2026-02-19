# Platform Development

End-to-end development of the Indemn agent platform — spanning indemn-platform-v2 (V2 agent builder + Jarvis), the evaluation harness, copilot-dashboard (Angular config UI), and supporting services. Covers debugging, feature development, and refinement of the full stack from agent configuration through evaluation and deployment.

## Status
**Session 2026-02-19-c**: Fixed evaluations/Jarvis failure on dev (`wem` — P0 closed). Root cause: `EVALUATION_SERVICE_URL` missing from platform-v2 container `.env` on dev EC2 — connector defaulted to `localhost:8002` which fails inside Docker. Fixed by adding env var and restarting. Also fixed Jarvis avatar icons not loading (`z7a` — closed) by adding `VITE_FEDERATION_BASE_URL` build arg to Dockerfile + CI/CD workflows (commit `6cc1893`). Resolved unrelated `proxy.indemn.ai` outage caused by accidental security group rule deletion. New bead `nlw` (P1) for Jarvis duplicating rubric/test set creation after subagents complete.

**Next session should**:
1. Read initial context: `artifacts/2026-02-19-initial-context.md`
2. Verify PR #958 merged and Loading... fix deployed on dev
3. Fix Jarvis headless baseline duplicate creation (bead `nlw`) — likely prompt issue in `seed_jarvis_templates.py`
4. Address architecture discussion (bead `5q2`) when ready
5. Investigate stuck evaluation run from Feb 9 (status "running", 0/40 completed) — may need manual cleanup
6. Align env var naming: code reads `EVALUATION_SERVICE_URL`, dev had `INDEMN_EVALUATION_SERVICE_URL`

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-platform-v2 | GitHub repo + local | indemn-ai/copilot-dashboard-react (org), craig-indemn/indemn-platform-v2 (personal) |
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

## Decisions
- 2026-02-19: Project scope is full platform — evals, federation, V2 builder, Jarvis, deployment — all active areas equally.
- 2026-02-19: Evaluations repo `feat/ff_evaluation` branch is NOT active — use `main` branch only.
- 2026-02-19: CSS leakage fix approach — post-process remoteEntry.js in build script rather than forking the vite-plugin-federation plugin.
- 2026-02-19: Loading... fix approach — gate template on `visible` input rather than changing default `isLoading` value.
- 2026-02-19: copilot-dashboard has branch protection — changes go through PRs.
- 2026-02-19: Federation asset URLs require `VITE_FEDERATION_BASE_URL` as build arg — absolute URLs needed for cross-origin federation.
- 2026-02-19: Platform-v2 Docker container needs `EVALUATION_SERVICE_URL=http://evaluations:8080` in `.env` for backend connector calls (nginx proxy only handles browser requests).

## Open Questions
- What architecture choices need to be made? (bead `5q2`)
- Is the CI/CD runner for copilot-dashboard-react fixable, or should we set up a new one?
- Should `INDEMN_EVALUATION_SERVICE_URL` in dev `.env` be renamed to `EVALUATION_SERVICE_URL` to match the code? Or should the code support both?
- Stuck evaluation run from Feb 9 (0/40 completed) — clean up or leave?
