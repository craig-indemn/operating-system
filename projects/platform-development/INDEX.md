# Platform Development

End-to-end development of the Indemn agent platform — spanning indemn-platform-v2 (V2 agent builder + Jarvis), the evaluation harness, copilot-dashboard (Angular config UI), and supporting services. Covers debugging, feature development, and refinement of the full stack from agent configuration through evaluation and deployment.

## Status
**Session 2026-02-19-b**: Triaged 4 issues from Dolly's dev testing feedback. Fixed CSS style leakage (patched `build-federation.js` Phase 3 to prevent global CSS injection — deployed and verified on dev). Fixed persistent "Loading..." indicator (Jarvis chat wrapper `isLoading` stuck true when hidden — PR #958 pending review). Created `/local-dev` and `/agent-browser` skills. Remaining: `wem` (P0 — evaluations/Jarvis failing) and `5q2` (P2 — architecture discussion).

**Next session should**:
1. Read initial context: `artifacts/2026-02-19-initial-context.md`
2. Shake out evaluations framework and Jarvis in the dev UI (bead `wem`)
3. Verify PR #958 merged and Loading... fix deployed
4. Address architecture discussion (bead `5q2`) when ready

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

## Decisions
- 2026-02-19: Project scope is full platform — evals, federation, V2 builder, Jarvis, deployment — all active areas equally.
- 2026-02-19: Evaluations repo `feat/ff_evaluation` branch is NOT active — use `main` branch only.
- 2026-02-19: CSS leakage fix approach — post-process remoteEntry.js in build script rather than forking the vite-plugin-federation plugin.
- 2026-02-19: Loading... fix approach — gate template on `visible` input rather than changing default `isLoading` value.
- 2026-02-19: copilot-dashboard has branch protection — changes go through PRs.

## Open Questions
- What is the full scope of evaluations/Jarvis failures on dev? (bead `wem`)
- What architecture choices need to be made? (bead `5q2`)
- Is the CI/CD runner for copilot-dashboard-react fixable, or should we set up a new one?
