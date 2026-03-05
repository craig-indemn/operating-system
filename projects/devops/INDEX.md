# DevOps

Infrastructure, secrets management, deployment automation, and container orchestration for Indemn's microservices platform.

## Status
Fourth session (2026-03-04): Observatory **deployed to dev EC2 with AWS Secrets Manager**. Host-side `aws-env-loader.sh` writes `.env.aws` during GitHub Actions deploy, docker-compose reads it via `env_file`. Container has no AWS dependency. PRs #20–#23 merged to `demo-gic`. AWS CLI v2 installed on dev EC2. `build.yml` updated with same deploy pattern. PR #24 (`demo-gic` → `main`) open to converge branches. DEVOPS-42 commented. Throwaway branches cleaned up.

**Next session:** Create Linear sub-issues under DEVOPS-42 for each service that needs SM migration. Then migrate services one by one using the AWS skill's Service Migration Playbook. PR #24 (`demo-gic` → `main`) still open to merge.

Previous sessions: Third (2026-03-04) secrets proxy complete — wrapper scripts, guard hook, 1Password SA, merged os-devops to main. Second (2026-03-04) built wrapper scripts, guard hook, 1Password service account. First (2026-03-03) AWS secrets management POC — 18 secrets + 37 params, IAM roles + OIDC.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| indemn-observability | GitHub repo | indemn-ai/Indemn-observatory (PRs #20–#23 merged to demo-gic, PR #24 demo-gic→main) |
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
- 2026-03-04: Host-side env loading over container entrypoint — Docker bridge networking can't reach IMDS at hop limit 1, and keeping AWS CLI out of the image saves ~150MB
- 2026-03-04: AWS CLI v2 installed on dev EC2 as infrastructure prerequisite for host-side loading
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

## What's Deployed
### AWS
- **IAM Role:** `indemn-dev-services` — attached to dev EC2, reads `dev/*` only, explicit prod deny
- **IAM Role:** `github-actions-deploy` — OIDC federation for indemn-ai GitHub org, dev only
- **OIDC Provider:** `token.actions.githubusercontent.com` — scoped to indemn-ai repos
- **Secrets Manager:** 18 secrets under `dev/` (16 shared, 2 observability-specific)
- **Parameter Store:** 37 parameters under `/dev/` (shared + observability-specific)

### Dev EC2 (i-0fde0af9d216e9182)
- **AWS CLI v2** installed at `/usr/local/bin/aws`
- **Observatory** running via docker-compose with `env_file: .env.aws` (secrets from SM/PS)
- **GitHub Actions self-hosted runner** at `/home/ubuntu/actions-runner-observatory/`

## Next Steps
1. ~~Test deployment: push `aws-secrets-management` branch, verify container pulls secrets on dev EC2~~ ✓ Done
2. Merge `demo-gic` → `main` on indemn-observability to converge branches
3. Migrate additional services using the AWS skill's Service Migration Playbook
4. Write DEVOPS-94 proposal for team 1Password approach
5. Set up prod secrets (separate session, with care)
6. Clean up old service account tokens in 1Password (`indemn-cli` and `local-cli` SA auth tokens can be removed)

## Open Questions
- Service URLs in Parameter Store are currently `localhost` — need to update to actual EC2 service addresses for deployed environments
- Should Docker Hub credentials move to AWS (ECR) or stay in GitHub secrets for now?
- When to tackle prod secrets setup?
