# DevOps

Infrastructure, secrets management, deployment automation, and container orchestration for Indemn's microservices platform.

## Status
Thirteenth session (2026-04-27): **Saved-items continuation + CLI shipping + form-extractor renderer style alignment.** See [2026-04-27 saved-items-cli-shipping](artifacts/2026-04-27-saved-items-cli-shipping.md) for the full rollup. Highlights: (1) `@indemn/cli@1.4.0` published — banner-on-every-command shipped (AI-368, closes the Celine-in-Insurica near-miss class of bug). (2) `@indemn/cli@1.5.0` PR #13 awaiting Rudra/Jonathan re-review — `functions create`/`update` now write the full `configurationSchema` (AI-369). End-to-end verified on a real dev bot: bearer-token + api-key both round-trip through real httpbin requests. Self-review found 2 real bugs (snake_case auth values + broken `functions test`) — both fixed. (3) form-extractor PR #17 (renderer service migration) re-skinned to Inter font + Tailwind blue/slate matching Copilot Dashboard's `IndemnPreset`; pushed to existing branch, replied to Dolly for re-review. (4) Booked 15-min calendar event Tue 2026-04-28 8:30 AM ET with Rem + Rudra + Dhruv for JM manager-agent test process sync. (5) Saved-for-Later queue: archived 5 items (Rudra joshu env, Dolly form-extractor runner, Rem rollup, Dolly list-orgs, banner ask, Dolly form-extractor UI). Queue now at 3 active items (Jonathan Observatory bug = next session's primary; AI-369 in flight; Craig's own follow-up to Dhruv handled side-channel).

**Next session — primary**: triage **Jonathan's Observatory bug** for Insurica's Reception agent (saved-item parent thread `1777060307.862239`). Symptoms: Volume tab shows "No data", Flow tab shows "No flow data", other tabs show 0 conversations despite overview having data. Likely a data-scope mismatch (bot_id vs project_id, or filter excluding the agent type). Repo at `indemn-ai/Indemn-observatory`, deployed to copilot-prod (`i-0df529ca541a38f3d`). See [observability-env-inventory](artifacts/2026-03-03-observability-env-inventory.md) for env reference. Detailed pickup checklist in the 2026-04-27 artifact.

**Next session — secondary (passively unblocking)**: when AI-369 PR #13 approves → `git push origin main:prod` on indemn-cli → publish 1.5.0 → archive saved item + Slack reply. When form-extractor PR #17 re-approves → coordinate merge.

**Cleanup**: jarvis-cli-mcp project INDEX still says version 1.1.1; should be updated to reflect 1.4.0 published + 1.5.0 in flight.

---

Twelfth session (2026-04-20 → 2026-04-24): **Multi-day dev-squad unblock sweep while Dhruv remains OOO.** 8 threads handled end-to-end — see [multi-day-dev-squad-unblock](artifacts/2026-04-24-multi-day-dev-squad-unblock.md) for the full rollup. Highlights: (1) voice-service dev Cartesia version drift corrected — dev PS bumped `2024-06-10` → `2025-04-16` to match prod, PR #59 closed as defensive-code-not-needed. (2) middleware-socket-service PR #383 merged to prod (Family First COP-489 cherry-pick). (3) voice-livekit + dev-services docker image prune (77 GB + 42 GB reclaimed). (4) web-operators PR #33 opened (main → prod, build-dev.yml is fully commented out per Dhruv's original choice). (5) operations_api Joshu sync (Rudra's PR #119) unblocked via 14 new AWS entries (2 SM + 12 PS), loader PR #120 merged, cron running every 5 min with `JOSHU_MAX_RECORD_ATTEMPTS=1` and `JOSHU_SYNC_ENABLED=true`. (6) form-extractor CI/CD is fundamentally broken (4 stacked problems inherited from fork import on 2026-03-06); minimum-fix PR #27 opened, full fix tracked in DEVOPS-147. (7) `AIRTABLE_BASE_ID` briefly got the wrong value (Rudra's DM had `appizFSmK52Cfa0YE` but 11 routes depend on the existing `apptIDyxMfOqiThg5`) — reverted after Rudra flagged, zero damage in 16-hour window.

**Lessons captured for future sessions**:
- Hand-maintained `.env.aws` is a trap when the service also runs `aws-env-loader.sh`. Check before hand-editing.
- "Just use what they gave" is a dangerous default when teammates DM env var blocks without checking existing code consumers.
- Disk-full on dev EC2s is recurring (`dev-services` + `voice-livekit`). Need auto-prune or size-up.

**Next session:** 1) Merge PR #118 (Pattern C fix on intake-manager) if still open. 2) Merge PR #27 (form-extractor deploy-job removal) if still open. 3) Merge PR #33 (web-operators main → prod). 4) Form-extractor full fix under DEVOPS-147 when prioritized.

---

Eleventh session (2026-04-17): **Dev-squad firefighting — 4 concurrent incidents while Dhruv is OOO.** (1) voice-service dev Cartesia empty — restart cleared poisoned cache, then deeper dig found real bug: `cartesiaService.js` line 659 does `cartesiaResponse.data` but Cartesia's `/voices` returns a plain JSON array at API version `2024-06-10`. Reproduced locally with dev creds. One-line fix opened as voice-service PR #59 (reviewer Dolly). (2) conversation-service prod error alerts routing to #whitepaper-requests — `indemn/prod/shared/slack-webhook-url` got repurposed to whitepaper webhook on 2026-03-23 while 6 services still read it as errors webhook. Created dedicated `indemn/prod/services/operations-api/whitepaper-webhook-url`, opened operations_api PR #118 (reviewer Rudra), restored shared secret to prod-errors webhook from AWSPREVIOUS, redeployed conversation-service. Running on cached env preserves whitepaper routing until PR #118 deploys. (3) intake-manager Ben comparative rater broken — `NATIONWIDE_ENVIRONMENT=prod` but `NATIONWIDE_API_BASE_URL=https://api-stage.nationwide.com` (prod-issued token rejected by stage API, 57 auth failures since 2026-04-15). Someone flipped env var on 2026-04-14 without updating URL. Rudra confirmed Nationwide should stay on stage; edited `/opt/Intake-manager/.env` on copilot-prod with backup, recreated backend container, 0 new failures. (4) Dependabot PRs (3) blocked because org ruleset 13442013 requires approval from write-access reviewer but Craig/Dolly are read-only; Dhruv was the de facto SPOF. Drafted step-by-step admin-bypass instructions for Kyle (org owner) + longer-term `pr-approvers` team prompt for his Claude Code.

**Next session:** 1) Monitor PR #59 + #118 for merge/deploy. After #118 deploys, confirm whitepaper posts still land in #whitepaper-requests (operations_api switches from cached shared-secret webhook to dedicated secret). 2) Confirm Kyle admin-bypassed the 3 Dependabot PRs + created `pr-approvers` team. 3) Follow up on voice-service latent issues (Cartesia `limit` ignored, `accent` filter is a no-op at this API version). 4) Consider aligning `indemn/dev/shared/slack-webhook-url` (same overloaded-secret footgun likely present in dev). 5) intake-manager hand-maintained `.env` on copilot-prod is a source-of-drift — migrate to AWS-managed via aws-env-loader (repo has incomplete script, not wired into deploy). 6) SM-migration queue from prior sessions still open: 12 PRs awaiting Dhruv review.

Tenth session (2026-03-11b): **Release day support.** Dhruv says SM changes NOT going in this release — wants to test on dev first. Resolved evaluations PR #9 merge conflict (voice-simulation + transcript-evaluation both added new eval types to same enums/routing — kept both, 108 tests pass). Fixed copilot-dashboard-react federation issue: prod was loading `devplatform.indemn.ai` because prod EC2 was running `:main` (dev) Docker image instead of `:latest` (prod). Root cause: docker-compose defaulted to `:main` tag. Fixed by pulling `:latest` image and updating docker-compose default to `:latest`. Also triggered fresh prod build workflow (had cache contamination from shared GHA cache scope between dev/prod — `no-cache: true` and separate `scope=prod` fix prepared in build-prod.yml but NOT pushed yet).

Previous: Ninth (2026-03-11) PS URLs verified/fixed, loader .env gap fixed, Firebase naming fixed, QUOTE_PRICE_DETAILS_API fixed. Eighth (2026-03-10b) all AWS infra deployed, PRs organized, release doc created. Seventh–First: see below.

Previous sessions: Seventh (2026-03-10) release doc, prod EC2s mapped. Sixth (2026-03-06) all 12 SM PRs open. Fifth–First: infrastructure and secrets proxy work. Fourth (2026-03-04) observatory deployed to dev EC2 with SM. Third (2026-03-04) secrets proxy complete. Second (2026-03-04) wrapper scripts, guard hook, 1Password SA. First (2026-03-03) AWS SM POC — 18 secrets + 37 params, IAM roles + OIDC.

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
| 2026-04-27 | [saved-items-cli-shipping](artifacts/2026-04-27-saved-items-cli-shipping.md) | Continue saved-item triage: ship banner (AI-368 → @indemn/cli@1.4.0), open functions configurationSchema PR (AI-369 / PR #13), push form-extractor renderer style fix to PR #17, book manager-agent sync. Captures full state for handoff. |
| 2026-04-24 | [multi-day-dev-squad-unblock](artifacts/2026-04-24-multi-day-dev-squad-unblock.md) | 5-day rollup of all engineering asks from Dolly + Rudra handled between 2026-04-20 and 2026-04-24: Cartesia version, middleware PR #383, voice-livekit + dev-services disk cleanup, web-operators PR #33, operations_api Joshu sync AWS seed + PRs #120/#121, form-extractor CI/CD diagnosis + DEVOPS-147 |
| 2026-04-23 | [slack-saved-triage](artifacts/2026-04-23-slack-saved-triage.md) | Enumerate Craig's Slack Saved-for-Later queue (10 items) with owner, context, and suggested action per item |
| 2026-04-17 | [dev-squad-incident-response](artifacts/2026-04-17-dev-squad-incident-response.md) | Handle 4 concurrent incidents (voice-service Cartesia, conversation-service slack webhook routing, intake-manager Nationwide URL mismatch, Dependabot PR merge access) |
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
- 2026-03-11: SM changes NOT going in this prod release — Dhruv wants to test on dev first
- 2026-03-11: copilot-dashboard-react prod EC2 must use `:latest` Docker image tag (prod build), NOT `:main` (dev build). The Vite federation build bakes the base URL into remoteEntry.js chunk URLs at build time.
- 2026-03-11: copilot-dashboard-react docker-compose on prod-services default changed from `:main` to `:latest`
- 2026-03-11: GHA Docker build cache scope should be separated between dev (`scope=dev`) and prod (`scope=prod`) to prevent cross-contamination — fix prepared but NOT pushed yet
- 2026-03-11: evaluations PR #9 (voice-simulation) conflict resolved — both VOICE_SIMULATION and TRANSCRIPT eval types kept, 108 tests pass
- 2026-03-06: SM secret values populated directly on EC2 using `populate-sm-secrets.sh` — secrets never leave the box
- 2026-03-06: Temporary `secrets-write-temp` IAM policy added then removed for EC2 to write to SM (role normally read-only)
- 2026-03-06: Voice service uses `GOOGLE_PROJECT_ID`/`GOOGLE_CLIENT_EMAIL`/`GOOGLE_PRIVATE_KEY` (no `_CLOUD_` prefix)
- 2026-03-06: Middleware uses `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`S3_BUCKET_NAME`/`PRIVATE_S3_BUCKET_NAME` for S3
- 2026-03-06: Firebase uses `FIREBASE_SERVICE_ACCOUNT_JSON` (not `FIREBASE_SERVICE_ACCOUNT`)
- 2026-04-17: Shared-secret overloading is an anti-pattern — `indemn/prod/shared/slack-webhook-url` was simultaneously the whitepaper webhook (for operations_api) and the error webhook (for 6 other services). Flipping value to serve one consumer broke the others. Fix: service-scoped secrets for distinct intents, even if the value happens to be shared today
- 2026-04-17: AWS Secrets Manager AWSPREVIOUS version is a reliable rollback point — used to recover the real prod-errors webhook value after someone flipped the shared secret 3 weeks earlier
- 2026-04-17: `docker restart` does NOT re-read `env_file` in docker-compose (env is baked at container CREATE time, not START). Must `docker compose up -d --force-recreate` or redeploy via CI to pick up new SM/PS values. Applies anywhere aws-env-loader.sh writes `.env.aws` that compose reads via `env_file:`.
- 2026-04-17: Nationwide integration config is split across two variables that must agree: `NATIONWIDE_ENVIRONMENT=prod` picks prod identity endpoint in `config.py`; `NATIONWIDE_API_BASE_URL` must be set to the matching prod API URL. Mismatched values yield 400 "Authorization token failed" on API calls while the token-exchange itself succeeds. Rudra confirmed Nationwide should stay on stage; only Nationwide — other carrier integrations run in prod
- 2026-04-17: Intake-manager (UG Portal) prod deploy uses a hand-maintained `/opt/Intake-manager/.env` on copilot-prod EC2 — the `aws-env-loader.sh` in the repo exists but isn't invoked by the deploy workflow. This is how the Nationwide regression was introduced and is a latent source-of-drift
- 2026-04-17: Org ruleset 13442013 ("PR for default branch required") requires 1 approving review from reviewer with write access. Org members with `pull`-only permission (Craig, Dolly) can approve but their approvals don't satisfy the rule — made Dhruv a single point of failure for Dependabot PRs while he's OOO. Fix: create `pr-approvers` team with `push` permission containing trusted approvers (drafted as prompt for Kyle's Claude Code)
- 2026-04-17: GitHub org owners (admins) can bypass ruleset "required approving reviews" via a "Merge without waiting for requirements to be met" checkbox in the PR UI — doesn't require editing the ruleset. Useful for one-off unblocks (e.g., Kyle handling Dependabot PRs while Dhruv is OOO)
- 2026-04-17: Kyle Geoghan = `kwgeoghan` on GitHub, `UFK4DNNHG` on Slack. Ganesh Iyer = `U040W167JP6` on Slack. Do not conflate.
- 2026-04-27: indemn-cli publish workflow = push `main` → `prod` branch (not tag-based). NPM_TOKEN secret already configured. Workflow at `.github/workflows/publish.yml`. Prior 1.3.1 publish was manual; 1.4.0 first to use the workflow path.
- 2026-04-27: copilot-server `createBotTool` (services/botToolsService.js:160-196) does NOT call `convertPayloadToExecutionSchema` — only `updateBotTool` does (line 277-284). Dashboard works around this by always cloning master function templates. CLI uses an internal 2-step (POST skeleton → PUT config) to bridge the gap. Tail ticket worth filing for server-side symmetry.
- 2026-04-27: REST API `authorization.type` values must be kebab-case on the wire (`api-key`, `basic-auth`, `bearer-token`, `no-auth`). Server's `validateRestApiPayload` only checks the field is truthy, so wrong-format values silently pass validation but `generateHeaders` switch falls through and emits no Authorization header. Dashboard at `copilot-dashboard/src/app/services/ai-functions-helper.service.ts` confirms kebab-case.
- 2026-04-27: Copilot Dashboard's PrimeNG theme = "IndemnPreset" (custom Aura preset at `copilot-dashboard/src/app/primeng-theme.config.ts`): primary = Tailwind blue scale, surface/text = Tailwind slate scale, light mode by default. Index.html line 60 imports Inter from Google Fonts. This — not the marketing brand (Barlow + iris/eggplant/lilac) — is "the platform" Dolly references in design feedback.

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
