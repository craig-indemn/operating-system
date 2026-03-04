# DevOps

Infrastructure, secrets management, deployment automation, and container orchestration for Indemn's microservices platform.

## Status
Second session (2026-03-04): Secrets proxy implementation ~90% complete. Wrapper scripts, guard hook, skill updates, and 1Password integration all built. 1Password service account created and tokens stored in `cli-secrets` vault. **Needs: end-to-end testing of each wrapper script in a fresh session where OP_SERVICE_ACCOUNT_TOKEN is loaded via .env, then update the 1Password skill docs for onboarding.**

Previous: First session (2026-03-03). Secrets management POC for indemn-observability built. AWS CLI configured, 18 secrets + 37 parameters in dev, IAM roles + GitHub OIDC deployed.

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

## What's Deployed in AWS
- **IAM Role:** `indemn-dev-services` — attached to dev EC2, reads `dev/*` only, explicit prod deny
- **IAM Role:** `github-actions-deploy` — OIDC federation for indemn-ai GitHub org, dev only
- **OIDC Provider:** `token.actions.githubusercontent.com` — scoped to indemn-ai repos
- **Secrets Manager:** 18 secrets under `dev/` (16 shared, 2 observability-specific)
- **Parameter Store:** 37 parameters under `/dev/` (shared + observability-specific)

## Next Steps
1. **End-to-end test wrapper scripts** in a fresh session (OP_SERVICE_ACCOUNT_TOKEN will load from .env via SessionStart hook). Test: psql-connect.sh, mongosh-connect.sh, linearis-proxy.sh, curl-airtable.sh, curl-langfuse.sh
2. **Update 1Password skill** — rewrite for service account auth (not desktop app integration), document onboarding flow for new team members
3. **Fix guard hook** — it currently blocks `source .env` which is needed for loading OP_SERVICE_ACCOUNT_TOKEN. Either: (a) the SessionStart hook handles it via CLAUDE_ENV_FILE, or (b) whitelist sourcing .env specifically for non-secret config
4. Test deployment: push `aws-secrets-management` branch, verify container pulls secrets on dev EC2
5. Migrate additional services using the AWS skill's Service Migration Playbook
6. Set up prod secrets (separate session, with care)

## Open Questions
- Service URLs in Parameter Store are currently `localhost` — need to update to actual EC2 service addresses for deployed environments
- Should Docker Hub credentials move to AWS (ECR) or stay in GitHub secrets for now?
- When to tackle prod secrets setup?
