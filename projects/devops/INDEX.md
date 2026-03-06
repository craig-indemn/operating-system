# DevOps

Infrastructure, secrets management, deployment automation, and container orchestration for Indemn's microservices platform.

## Status
Fifth session (2026-03-06): **All 12 services migrated to AWS Secrets Manager** — PRs created for every service. 7 PRs pushed and open on GitHub. 5 repos blocked by missing write access (`craig-indemn` needs push permission on: payment-service, copilot-sync-service, operations_api, voice-service, email-channel-service). All have commits ready locally on `feat/aws-secrets-manager` branches. Created 17 new SM secrets (with PLACEHOLDER values — need EC2 sourcing) and ~50 new PS parameters. Template loader script at `scripts/aws-env-loader-template.sh`. Phase 0 investigation confirmed email-channel-service uses env vars (not file-based credentials).

**Next session:** 1) Get push access for 5 blocked repos and push remaining PRs. 2) Source real secret values from EC2 `.env` files and update SM PLACEHOLDERs. 3) Merge PRs one by one, verify each deploy. 4) Update service URLs in PS from `localhost` to actual EC2 addresses.

Previous sessions: Fourth (2026-03-04) observatory deployed to dev EC2 with SM. Third (2026-03-04) secrets proxy complete. Second (2026-03-04) wrapper scripts, guard hook, 1Password SA. First (2026-03-03) AWS SM POC — 18 secrets + 37 params, IAM roles + OIDC.

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
- **Secrets Manager:** 35 secrets under `dev/` (24 shared, 11 service-specific). 17 new secrets have PLACEHOLDER values pending EC2 sourcing.
- **Parameter Store:** ~90 parameters under `/dev/` (shared + per-service config)

### Dev EC2 (i-0fde0af9d216e9182)
- **AWS CLI v2** installed at `/usr/local/bin/aws`
- **Observatory** running via docker-compose with `env_file: .env.aws` (secrets from SM/PS)
- **GitHub Actions self-hosted runner** at `/home/ubuntu/actions-runner-observatory/`

## PRs — SM Migration (DEVOPS-42)
| # | Service | PR | Status |
|---|---------|-----|--------|
| 1 | evaluations | [#8](https://github.com/indemn-ai/evaluations/pull/8) | Open |
| 2 | bot-service | [#247](https://github.com/indemn-ai/bot-service/pull/247) | Open |
| 3 | kb-service | [#138](https://github.com/indemn-ai/kb-service/pull/138) | Open |
| 4 | conversation-service | [#131](https://github.com/indemn-ai/conversation-service/pull/131) | Open |
| 5 | middleware-socket-service | [#338](https://github.com/indemn-ai/middleware-socket-service/pull/338) | Open |
| 6 | copilot-server | [#796](https://github.com/indemn-ai/copilot-server/pull/796) | Open |
| 7 | copilot-dashboard | [#987](https://github.com/indemn-ai/copilot-dashboard/pull/987) | Open |
| 8 | payment-service | local commit | Blocked — no push access |
| 9 | copilot-sync-service | local commit | Blocked — no push access |
| 10 | operations_api | local commit | Blocked — no push access |
| 11 | voice-service | local commit | Blocked — no push access |
| 12 | email-channel-service | local commit | Blocked — no push access |

## Next Steps
1. ~~Test deployment: push `aws-secrets-management` branch, verify container pulls secrets on dev EC2~~ ✓ Done
2. ~~Migrate all services to SM~~ ✓ PRs created (7 pushed, 5 blocked on access)
3. Get push access for 5 blocked repos (payment-service, copilot-sync-service, operations_api, voice-service, email-channel-service)
4. Source real secret values from EC2 and update SM PLACEHOLDERs
5. Update service URLs in PS from `localhost` to actual EC2 addresses
6. Merge PRs one by one, verify each deploy (see plan Phase 5 merge order)
7. Merge `demo-gic` → `main` on indemn-observability
8. Write DEVOPS-94 proposal for team 1Password approach
9. Set up prod secrets (separate session, with care)

## Decisions
- 2026-03-06: email-channel-service uses env vars at runtime (not file-based credentials). `GOOGLE_AUTH_CREDEINTIALS` (typo preserved) is a JSON blob env var, not a file.
- 2026-03-06: All 12 services get identical shared secrets block, with per-service PARAM_MAP customization
- 2026-03-06: Coupled pairs (tiledesk, middleware-service) have identical loader scripts in both repos — idempotent
- 2026-03-06: SM secrets for new service-specific credentials created with PLACEHOLDER values — must be populated from EC2 before merging PRs

## Open Questions
- Service URLs in Parameter Store are currently `localhost` — need to update to actual EC2 service addresses for deployed environments
- Should Docker Hub credentials move to AWS (ECR) or stay in GitHub secrets for now?
- When to tackle prod secrets setup?
- 5 repos need push access for `craig-indemn` — who is the org admin to grant this?
- GROQ_API_KEY: is it actually used in production bot-service? (.env.example has it commented out)
