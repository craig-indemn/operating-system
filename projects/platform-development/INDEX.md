# Platform Development

End-to-end development of the Indemn agent platform — spanning indemn-platform-v2 (V2 agent builder + Jarvis), the evaluation harness, copilot-dashboard (Angular config UI), and supporting services. Covers debugging, feature development, and refinement of the full stack from agent configuration through evaluation and deployment.

## Status
**Session 2026-02-19-d**: Designed and validated the backend/frontend separation plan. Created epic `p0l` with 15 tasks across 3 phases. Design reviewed 3 times against the actual codebase — all corrections applied. Percy-service repo exists on GitHub (empty, ready for code). Architecture bead `5q2` superseded by this epic.

**Next session should**:
1. Read the design doc: `artifacts/2026-02-19-backend-separation-design.md`
2. Read initial context: `artifacts/2026-02-19-initial-context.md`
3. Run `bd ready` to see what's unblocked
4. Start executing epic `p0l` — first task is `p0l.1` (scaffold percy-service repo with backend code)
5. Background tasks still open: bead `nlw` (P1, Jarvis duplicate creation), stuck eval run from Feb 9

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-platform-v2 | GitHub repo + local | indemn-ai/copilot-dashboard-react (org), craig-indemn/indemn-platform-v2 (personal) |
| percy-service | GitHub repo | indemn-ai/percy-service (empty, awaiting backend code) |
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

## Open Questions
- ~~What architecture choices need to be made? (bead `5q2`)~~ → Superseded by separation epic `p0l`
- Is the CI/CD runner for copilot-dashboard-react fixable, or should we set up a new one? Craig now has access to set up runners.
- Should `INDEMN_EVALUATION_SERVICE_URL` in dev `.env` be renamed to `EVALUATION_SERVICE_URL` to match the code? Or should the code support both?
- Stuck evaluation run from Feb 9 (0/40 completed) — clean up or leave?
- `deepagents>=0.2` — is this a private package? Needs to resolve in percy-service's `uv sync`.
- `test_env` file in copilot-dashboard-react contains real API keys committed to git — credentials should be rotated.
