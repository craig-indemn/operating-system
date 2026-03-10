# DevOps

Infrastructure, secrets management, deployment automation, and container orchestration for Indemn's microservices platform.

## Status
Ninth session (2026-03-11): **PS parameter service URLs VERIFIED and FIXED. Loader .env gap FIXED.** Checked docker-compose files — all use Docker bridge + `shared-datadog` external network. Compared PS params against actual prod `.env` values. Fixed 9 wrong URLs (public domains for copilot/proxy/sync/evaluations, private IPs for host-mapped services). Fixed QUOTE_PRICE_DETAILS_API alias bug. Found critical loader gap: switching `env_file: .env` → `.env.aws` would lose ~70 static config vars per service. Fixed ALL 13 loader scripts to copy `.env` as base then append SM/PS overrides (last-value-wins). Fixed Firebase naming bugs in copilot-server + copilot-dashboard loaders. All pushed.

**Next session:** 1) Wait for Dhruv's reviews on 19 PRs. 2) Resolve copilot-dashboard deploy PR #989 merge conflict. 3) Create deploy PRs for evaluations + copilot-dashboard-react after their feature PRs merge. 4) Test a service deployment end-to-end on dev EC2 to verify .env.aws generation.

Previous: Eighth (2026-03-10b) all AWS infra deployed, PRs organized, release doc created. Seventh (2026-03-10) release doc, prod EC2s mapped. Sixth (2026-03-06) all 12 SM PRs open. Fifth–First: see below.

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
| 2026-03-10 | [production-release](artifacts/2026-03-10-production-release.md) | Full production release doc — all repos, PRs, env vars, infrastructure, deployment order |
| 2026-03-10 | [session-handoff](artifacts/2026-03-10-session-handoff.md) | Session handoff with exact next steps and remaining open items |
| 2026-03-11 | [release-notion](artifacts/2026-03-11-release-notion.md) | Notion-format release doc with all PRs, deploy paths, and status per repo |
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
- 2026-03-06: email-channel-service uses env vars at runtime (not file-based credentials). `GOOGLE_AUTH_CREDEINTIALS` (typo preserved) is a JSON blob env var, not a file
- 2026-03-06: All 12 services get identical shared secrets block, with per-service PARAM_MAP customization
- 2026-03-06: Coupled pairs (tiledesk, middleware-service) have identical loader scripts in both repos — idempotent
- 2026-03-06: SM secrets for new service-specific credentials created with PLACEHOLDER values — must be populated from EC2 before merging PRs
- 2026-03-06: Deploy jobs use EC2 instance profile for AWS auth — do NOT add OIDC permissions blocks or configure-aws-credentials to deploy jobs
- 2026-03-06: Preserve existing docker-compose vs docker compose syntax per-service (don't standardize)
- 2026-03-06: Preserve existing sudo patterns per-service (some use sudo on pull but not up)
- 2026-03-06: ~~PS service URLs are correct as `localhost`~~ SUPERSEDED by 2026-03-11 findings
- 2026-03-11: Prod PS service URLs use a MIX of public domains and private IPs (verified from actual prod .env files):
  - Public domains for copilot-server (`https://copilot.indemn.ai`), middleware (`https://proxy.indemn.ai`), sync (`https://copilotsync.indemn.ai`), evaluations (`https://evaluations.indemn.ai/api/v1`)
  - Private IPs for host-mapped services on prod-services EC2 (bot-service, conversation, kb, voice, payment, operations_api at `172.31.22.7:<port>`)
  - `SERVER_BASE_URL` is a relative path (`/api/`), not an absolute URL
- 2026-03-11: copilot-server port 3000 is `expose:` only in docker-compose (not `ports:`), so NOT reachable via host IP — must use `https://copilot.indemn.ai` or container name `copilot-server:3000` on shared-datadog network
- 2026-03-11: All Docker services use bridge networking with `shared-datadog` external network — no `network_mode: host` anywhere
- 2026-03-11: QUOTE_PRICE_DETAILS_API alias in copilot-server loader was broken — derived from API_URL port replacement (`:3000`→`:9090`) which fails with domain URLs. Fixed to use CONVERSATION_URL directly (pushed to PR #796)
- 2026-03-11: Loader scripts must copy `.env` as base before appending SM/PS overrides — switching `env_file: .env` → `.env.aws` without this loses ~70 static config vars per service (feature flags, static paths, Docker container names, etc.). Last-value-wins ensures SM/PS values override .env values for managed vars.
- 2026-03-11: Firebase env var names in copilot-server/dashboard loaders were wrong — `FIREBASE_APIKEY` instead of `FIREBASE_API_KEY`, `FIREBASE_AUTHDOMAIN` instead of `FIREBASE_AUTH_DOMAIN`, etc. Fixed in both loaders to match what the application code expects.
- 2026-03-11: Prod service URL pattern — services with public domains (copilot.indemn.ai, proxy.indemn.ai, copilotsync.indemn.ai, evaluations.indemn.ai, bot.indemn.ai) use domain names. Services without public domains use private IPs with host-mapped ports. copilot-server port 3000 is `expose:` only (no host port mapping) — MUST use domain.
- 2026-03-06: SM secret values populated directly on EC2 using `populate-sm-secrets.sh` — secrets never leave the box
- 2026-03-06: Temporary `secrets-write-temp` IAM policy added then removed for EC2 to write to SM (role normally read-only)
- 2026-03-06: Voice service uses `GOOGLE_PROJECT_ID`/`GOOGLE_CLIENT_EMAIL`/`GOOGLE_PRIVATE_KEY` (no `_CLOUD_` prefix)
- 2026-03-06: Middleware uses `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`S3_BUCKET_NAME`/`PRIVATE_S3_BUCKET_NAME` for S3
- 2026-03-06: Firebase uses `FIREBASE_SERVICE_ACCOUNT_JSON` (not `FIREBASE_SERVICE_ACCOUNT`)

## What's Deployed
### AWS — Dev
- **IAM Role:** `indemn-dev-services` — attached to dev EC2, reads `dev/*` only, explicit prod deny
- **IAM Role:** `github-actions-deploy` — OIDC federation for indemn-ai GitHub org, dev only
- **OIDC Provider:** `token.actions.githubusercontent.com` — scoped to indemn-ai repos
- **Secrets Manager:** 35 secrets under `dev/` (24 shared, 11 service-specific). 15/17 populated from EC2; 2 remain PLACEHOLDER (google-oauth, groq-api-key — not configured in dev)
- **Parameter Store:** ~90 parameters under `/dev/` (shared + per-service config). Service URLs all `localhost` (single EC2).

### AWS — Prod
- **IAM Role:** `indemn-prod-services` — attached to both prod EC2s, reads `indemn/prod/*` only, explicit dev deny
- **Secrets Manager:** 34 secrets under `indemn/prod/` (24 shared + 8 service-specific + langfuse + livekit). All populated from EC2s via scripts.
- **Parameter Store:** 114 parameters under `/indemn/prod/`. Service URLs verified against prod .env files (2026-03-11): public domains for copilot/proxy/sync/evaluations, private IPs for host-mapped services on prod-services.
- **AWS CLI v2:** Installed on both prod EC2s

### Dev EC2 (i-0fde0af9d216e9182)
- **AWS CLI v2** installed at `/usr/local/bin/aws`
- **Observatory** running via docker-compose with `env_file: .env.aws` (secrets from SM/PS)
- **GitHub Actions self-hosted runner** at `/home/ubuntu/actions-runner-observatory/`

### Prod EC2s
- **prod-services** (`i-00ef8e2bfa651aaa8`, 98.88.11.14 / 172.31.22.7): bot-service, middleware, conversation, kb, payment, operations_api, email-channel, voice-service, copilot-sync, evaluations, percy, copilot-dashboard-react
- **copilot-prod** (`i-0df529ca541a38f3d`, 54.226.32.134 / 172.31.37.32): copilot-server, copilot-dashboard, observatory
- **voice-livekit** (`i-01e65d5494fd64b05`, 3.236.53.208): voice-livekit (NOT part of SM migration)

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
| 8 | payment-service | [#56](https://github.com/indemn-ai/payment-service/pull/56) | Open |
| 9 | copilot-sync-service | [#116](https://github.com/indemn-ai/copilot-sync-service/pull/116) | Open — docker-scan FAILED (node-tar CVE) |
| 10 | operations_api | [#92](https://github.com/indemn-ai/operations_api/pull/92) | Open — docker-scan FAILED (tar-fs CVE) |
| 11 | voice-service | [#38](https://github.com/indemn-ai/voice-service/pull/38) | Open |
| 12 | email-channel-service | [#35](https://github.com/indemn-ai/email-channel-service/pull/35) | Open |

## Next Steps
1. ~~Test deployment: push `aws-secrets-management` branch, verify container pulls secrets on dev EC2~~ ✓ Done
2. ~~Migrate all services to SM~~ ✓ All 12 PRs open on GitHub
3. ~~Get push access for 5 blocked repos~~ ✓ Dhruv granted access, all pushed
4. ~~Source real secret values from EC2 and update SM PLACEHOLDERs~~ ✓ 15/17 populated (google-oauth + groq-api-key don't exist in dev)
5. ~~Update service URLs in PS from `localhost` to actual EC2 addresses~~ ✓ Verified and fixed (2026-03-11) — 9 params corrected, 8 confirmed
6. ~~Set up prod secrets~~ ✓ 34 SM secrets + 114 PS params created (2026-03-10)
7. ~~Verify PS parameter service URLs against actual prod .env~~ ✓ Done (2026-03-11)
8. ~~Fix loader .env gap~~ ✓ All 13 loaders now copy .env as base (2026-03-11)
9. ~~Fix Firebase naming + QUOTE_PRICE_DETAILS_API bugs~~ ✓ Done (2026-03-11)
10. Get Dhruv's review approval on all 12 PRs (all set to "In Review" in Linear)
11. Resolve copilot-dashboard deploy PR #989 merge conflict (prod has `intake-manager-changes` hotfix)
12. Create deploy PRs for evaluations + copilot-dashboard-react after their feature PRs merge
13. Fix docker-scan failures on 3 repos if required check: copilot-sync-service, middleware-socket-service, operations_api
14. Merge PRs one by one, verify each deploy (see merge order and deployment order in release doc)
15. Write DEVOPS-94 proposal for team 1Password approach

## SM Secrets Status
15/17 secrets populated from EC2 `.env` files using `scripts/populate-sm-secrets.sh`.

**Populated (15):** stripe-keys (2 keys), firebase-credentials (7 keys), sendgrid-api-key, twilio-credentials, bland-api-key, airtable-api-key, google-cloud-sa (3 keys), service-tokens (2 keys), copilot-api-credentials (2 keys), middleware/aws-s3-credentials (4 keys), operations-api/carrier-credentials (13 keys), copilot-server/chat21-credentials, copilot-server/admin-credentials (2 keys), operations-api/mixpanel-token, email-channel/google-auth-credentials (1 key)

**Still PLACEHOLDER (2):**
| Secret Path | Reason |
|-------------|--------|
| `shared/google-oauth` | No Google OAuth configured in dev (vars don't exist in tiledesk .env) |
| `shared/groq-api-key` | Not used in dev bot-service |

**Partial keys (expected):** stripe-keys has 2/4 (no webhook secrets in dev), firebase-credentials has 7/10 (no database_url, messaging_sender_id, app_id in .env), service-tokens has 2/3 (no apps_access_token — only APPS_ACCESS_TOKEN_SECRET which is in admin-credentials)

**Env var name discoveries from EC2:**
- Voice service uses `GOOGLE_PROJECT_ID`, `GOOGLE_CLIENT_EMAIL`, `GOOGLE_PRIVATE_KEY` (no `_CLOUD_` prefix)
- Middleware uses `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`, `PRIVATE_S3_BUCKET_NAME`
- Firebase uses `FIREBASE_SERVICE_ACCOUNT_JSON` (not `FIREBASE_SERVICE_ACCOUNT`)

## Coupled Pairs (Must Merge Together)
1. **copilot-dashboard + copilot-server** → deploy to `/opt/tiledesk/` — share docker-compose.yml and .env
2. **middleware-socket-service + copilot-sync-service** → deploy to `/opt/middleware-service/` — share docker-compose.yml and .env

## Merge Order (Phase 5)
1. evaluations (standalone, simplest)
2. bot-service (standalone, core)
3. payment-service (standalone)
4. kb-service (standalone, deploys to /opt/openai-fastapi)
5. conversation-service (standalone, deploys to /opt/utility-service)
6. copilot-dashboard + copilot-server (BOTH together — /opt/tiledesk)
7. middleware-socket-service + copilot-sync-service (BOTH together — /opt/middleware-service)
8. operations_api (standalone)
9. voice-service (standalone)
10. email-channel-service (standalone)

## Linear Sub-Issues (DEVOPS-95 through DEVOPS-107)
All set to "In Review" with PR links in comments. Dhruv added as reviewer.

| Linear | Service | PR | Status |
|--------|---------|-----|--------|
| DEVOPS-95 | bot-service | #247 | In Review |
| DEVOPS-96 | conversation-service | #131 | In Review |
| DEVOPS-97 | copilot-dashboard | #987 | In Review |
| DEVOPS-98 | copilot-server | #796 | In Review |
| DEVOPS-99 | copilot-sync-service | #116 | In Review — docker-scan FAILED |
| DEVOPS-100 | evaluations | #8 | In Review |
| DEVOPS-101 | kb-service | #138 | In Review |
| DEVOPS-102 | middleware-socket-service | #338 | In Review — docker-scan FAILED |
| DEVOPS-103 | payment-service | #56 | In Review |
| DEVOPS-104 | voice-service | #38 | In Review |
| DEVOPS-105 | operations_api | #92 | In Review — docker-scan FAILED |
| DEVOPS-106 | email-channel-service | #35 | In Review |
| DEVOPS-107 | Path rename | — | Done |

## Docker-Scan Failures (Pre-existing, Not From Our Changes)
3 repos fail Trivy security scan on PR due to `node-tar` CVEs in dependencies:
- **copilot-sync-service**: `tar` 7.5.2 needs bump to ≥7.5.10 (CVE-2026-23950, -24842, -26960, -29786)
- **middleware-socket-service**: `tar` already at 7.5.10 but CVEs in base Docker image
- **operations_api**: Uses `tar-fs`/`tar-stream` (different packages), same CVE family

Scan workflow: `.github/workflows/docker-image-scanner.yml` — runs on `pull_request` to `main`, uses `aquasecurity/trivy-action@0.24.0`, fails on HIGH/CRITICAL with `exit-code: "1"`.

Whether these block merge depends on branch protection rules (couldn't read — 404 on protection API, likely need admin). All repos also require review approval regardless.

## Scripts (in OS repo)
- `scripts/aws-env-loader-template.sh` — template for service loader scripts
- `scripts/populate-sm-secrets.sh` — run on EC2 to populate SM from `.env` files (dry-run by default)
- `scripts/find-env-var-names.sh` — diagnostic: prints env var names (not values) from EC2 `.env` files

## Open Questions
- Should Docker Hub credentials move to AWS (ECR) or stay in GitHub secrets for now?
- When to tackle prod secrets setup?
- GROQ_API_KEY: is it actually used in production bot-service? (.env.example has it commented out)
- Are docker-scan failures required checks that block merge? Need admin to confirm.
