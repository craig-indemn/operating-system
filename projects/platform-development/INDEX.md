# Platform Development

End-to-end development of the Indemn agent platform — spanning indemn-platform-v2 (V2 agent builder + Jarvis), the evaluation harness, copilot-dashboard (Angular config UI), and supporting services. Covers debugging, feature development, and refinement of the full stack from agent configuration through evaluation and deployment.

## Status
**Session 2026-02-19-a**: Project created and bootstrapped. Wrote comprehensive initial context artifact (~900 lines) from deep exploration of all 5 repos — read CLAUDE.md files, git histories, 80+ design docs, source code of federation wrappers, bot-details integration, routing, config services, evaluation framework spec, and deployment infrastructure. All services are deployed to dev EC2 but user reports significant issues to resolve and architecture choices to make.

**Next session should**:
1. Get the user to describe the specific dev deployment issues and architecture decisions
2. Triage and prioritize — create beads for each issue
3. Start working through the highest-priority items
4. Read the initial context artifact first: `artifacts/2026-02-19-initial-context.md`

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

## Decisions
- 2026-02-19: Project scope is full platform — evals, federation, V2 builder, Jarvis, deployment — all active areas equally.
- 2026-02-19: Evaluations repo `feat/ff_evaluation` branch is NOT active — use `main` branch only.

## Open Questions
- What are the specific significant issues on dev deployment?
- What architecture choices need to be made?
- What is the priority order for issues vs. new features?
