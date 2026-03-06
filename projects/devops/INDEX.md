# DevOps

Infrastructure, secrets management, deployment automation, and container orchestration for Indemn's microservices platform.

## Status
**2026-03-06**: COP-357 Dependabot vulnerability remediation **complete** — all PRs created/approved, awaiting merge. 5 repos addressed: a2p-compliance-showcase-demo (3 PRs approved), engineering-blog (4 PRs approved), percy-service (4 PRs approved incl. langgraph-checkpoint 3→4), bot-service (PR #248 created, needs review), fragments (PR #5 created, 30 alerts fixed via overrides, needs review). COP-357 moved to In Review.

Previous: Third session (2026-03-04). Secrets proxy complete and tested. Second session (2026-03-04). Built wrapper scripts, guard hook, 1Password service account. First session (2026-03-03). AWS secrets management POC.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo | craig-indemn/indemn-observability (branch: aws-secrets-management) |
| AWS Console | Cloud provider | https://console.aws.amazon.com |
| Dev EC2 | Infrastructure | i-0fde0af9d216e9182 (dev-services, t3.xlarge, us-east-1a) |
| Prod EC2 | Infrastructure | i-00ef8e2bfa651aaa8 (prod-services, t3.xlarge, us-east-1b) |
| Platform env files | Config source | /Users/home/Repositories/.env.dev, .env.prod |
| DEVOPS-42 | Linear issue | Migrate secrets from .env to AWS Secrets Manager [E-3] — In Progress, assigned Craig |
| DEVOPS-43 | Linear issue | Define credential rotation policy [E-4] — Queued (next after 42) |
| DEVOPS-94 | Linear issue | 1Password policy / credential boundary [O-5] — Queued, assigned Craig |
| COP-357 | Linear issue | Dependabot vulnerability alerts — fragments, engineering-blog, percy-service, bot-service, a2p-compliance-showcase-demo — In Review |
| bot-service PR #248 | GitHub PR | indemn-ai/bot-service/pull/248 — langgraph upgrade, needs review |
| fragments PR #5 | GitHub PR | indemn-ai/fragments/pull/5 — 30 alerts fixed via overrides, needs review |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-03 | [observability-env-inventory](artifacts/2026-03-03-observability-env-inventory.md) | What env vars does indemn-observability use, and which are secrets vs config? |
| 2026-03-03 | [devops-architecture-context](artifacts/2026-03-03-devops-architecture-context.md) | Capture the planning discussion decisions for secrets, ECS, and deployment architecture |

## Decisions
- 2026-03-04: Personal tokens stored in 1Password via service account (OP_SERVICE_ACCOUNT_TOKEN in .env), vault name `cli-secrets`
- 2026-03-04: Service account on Craig's personal 1Password (Indemn team 1Password lacks admin for SA creation)
- 2026-03-04: Each team member will have their own service account token — .env has one token that unlocks all their personal secrets
- 2026-03-04: Vault name `cli-secrets` is generic (not Indemn-specific) — designed for reuse across contexts
- 2026-03-04: Guard hook uses exit codes (exit 0 = allow, exit 2 = block) — the JSON output format caused "hook error" warnings
- 2026-03-04: SessionStart hook `load-env.sh` sources .env into CLAUDE_ENV_FILE (replaces inline echo command)
- 2026-03-04: linearis uses LINEAR_API_KEY env var, not LINEAR_API_TOKEN
- 2026-03-04: Guard hook (PreToolUse) blocks .env reads, secret var echoing, bare printenv — lives at `.claude/hooks/secrets-guard.sh`
- 2026-03-04: Wrapper scripts in `scripts/secrets-proxy/` on PATH via SessionStart hook
- 2026-03-03: Dual approach — AWS Secrets Manager for credentials, Parameter Store for non-sensitive config
- 2026-03-03: Secrets injected by infrastructure, not fetched by application code (env vars, not SDK calls)
- 2026-03-03: Hierarchical path convention: Secrets Manager `{env}/shared/{name}` (no leading slash), Parameter Store `/{env}/shared/{name}` (leading slash)
- 2026-03-03: GitHub Actions OIDC federation for AWS auth (no long-lived keys in GitHub)
- 2026-03-03: Single AWS account (780354157690), us-east-1 region
- 2026-03-03: Shared secrets across services (most credentials are common), per-env config in Parameter Store
- 2026-03-03: Forward-compatible design for future ECS migration
- 2026-03-03: AWS CLI skill created in OS to document patterns — includes Service Migration Playbook
- 2026-03-03: Dev/prod share nearly all credentials except MongoDB URI and Pinecone API key
- 2026-03-03: IAM roles use explicit Deny on prod resources for dev roles (belt + suspenders)
- 2026-03-03: Do NOT touch prod without explicit user confirmation
- 2026-03-06: Dependabot remediation (COP-357): Craig assigned fragments, engineering-blog, percy-service, bot-service, a2p-compliance-showcase-demo
- 2026-03-06: langgraph-checkpoint 3→4 major bump verified safe — MemorySaver() zero-arg usage unchanged, 762 tests pass on percy-service
- 2026-03-06: bot-service langgraph upgrade requires atomic bump of all 4 packages (langgraph, checkpoint, prebuilt, sdk) — sdk 0.2→0.3 required by langgraph 1.0.10
- 2026-03-06: fragments has dual lockfile ecosystems (pnpm-lock.yaml + 004-lovable-angular-components/package-lock.json) — each needs separate overrides mechanism
- 2026-03-06: Craig can self-approve Dependabot-authored PRs (org ruleset requires 1 review, but author is dependabot[bot])
- 2026-03-06: Craig-authored PRs (bot-service, fragments) need teammate review due to org ruleset

## What's Deployed in AWS
- **IAM Role:** `indemn-dev-services` — attached to dev EC2, reads `dev/*` only, explicit prod deny
- **IAM Role:** `github-actions-deploy` — OIDC federation for indemn-ai GitHub org, dev only
- **OIDC Provider:** `token.actions.githubusercontent.com` — scoped to indemn-ai repos
- **Secrets Manager:** 18 secrets under `dev/` (16 shared, 2 observability-specific)
- **Parameter Store:** 37 parameters under `/dev/` (shared + observability-specific)

## Next Steps
1. **COP-357**: Get Dhruv to merge the 11 approved Dependabot PRs + review/merge bot-service #248 and fragments #5. Then verify alerts close and move COP-357 to Done.
2. **Alert auto-close**: langgraph CVE-2026-28277 has `first_patched_version: null` — may need manual API dismissal after merge (`gh api -X PATCH repos/indemn-ai/{repo}/dependabot/alerts/{n} -f state=dismissed -f dismissed_reason=fix_started`)
3. Test deployment: push `aws-secrets-management` branch, verify container pulls secrets on dev EC2
4. Migrate additional services using the AWS skill's Service Migration Playbook
5. Set up prod secrets (separate session, with care)
6. Clean up old service account tokens in 1Password (`indemn-cli` and `local-cli` SA auth tokens can be removed)

## Open Questions
- Service URLs in Parameter Store are currently `localhost` — need to update to actual EC2 service addresses for deployed environments
- Should Docker Hub credentials move to AWS (ECR) or stay in GitHub secrets for now?
- When to tackle prod secrets setup?
- fragments has pre-existing build failures in 3 workspaces (000-promptkit-webchat, 002-copilot-tabs, index) — TypeScript errors, not dep-related. Should these be flagged?
- percy-service has 1 pre-existing test failure (test_list_agents_returns_summaries) — should be investigated
