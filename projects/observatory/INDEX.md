# Observatory

Indemn Observability platform — analytics and monitoring for voice and chat agents. Fixing authorization issues and improving the platform.

## Status
Security fix complete. `/api/metadata` org-scoping fix deployed to dev (demo-gic). PR #18 open to merge into main, then main→prod. Observatory was taken down in prod, pending re-deploy after PR merge.

**Next steps:**
- Merge PR #18 into main (branch protection requires PR)
- Create PR from main into prod
- Re-deploy prod and verify

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo | indemn-ai/Indemn-observatory |
| Dev deployment | URL | https://devobservatory.indemn.ai |
| Auth fix PR | GitHub PR | indemn-ai/Indemn-observatory/pull/18 |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|

## Decisions
- 2026-03-03: Fix metadata org leak at backend level (MongoDB $match filter) + frontend fallback removal
- 2026-03-03: Keep current auth model — @indemn.ai employees get full access, external users scoped to their orgs
- 2026-03-03: Suppress PyJWT InsecureKeyLengthWarning (shared secret with copilot-server, can't change unilaterally)
- 2026-03-03: Cherry-pick only security commits to main, not all demo-gic work

## Open Questions
- When to bring all demo-gic work (voice eval, Langfuse, CSR reports) into main/prod?
- Dependabot flagged 8 vulnerabilities on default branch — need to triage
