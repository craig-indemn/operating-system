---
ask: "Production release document for March 2026 — Craig's work across all repos, PRs, env vars, and deployment steps"
created: 2026-03-10
workstream: devops
session: 2026-03-10-a
sources:
  - type: github
    description: "Commit history and PR state across all indemn-ai repos"
  - type: linear
    description: "Issue status for DEVOPS-42 (SM migration), COP-359 (voice eval), and related"
  - type: aws
    description: "Secrets Manager and Parameter Store inventory for dev and prod"
---

# Production Release — March 2026

## Release Overview

Craig's work spanning 16 repos. Three major initiatives:

1. **AWS Secrets Manager migration** — all 12 services migrated from `.env` to SM/PS (feature branches, PRs open)
2. **Voice evaluation system** — transcript + simulation evaluation across evaluations, voice-livekit, observatory, indemn-platform-v2
3. **Platform features** — evaluations UI federation, Jarvis skills architecture, auth fixes, observatory reporting

---

## Pre-Deployment: AWS Secrets Manager & Parameter Store

Before any service can deploy with SM migration, the prod SM/PS infrastructure must exist.

**Current state:**
- **Dev**: 27 SM secrets + 105 PS parameters — fully populated
- **Prod**: 1 SM secret (`mongodb-uri`) + 0 PS parameters

### Shared Secrets — Classification

**Same value in dev and prod (copy from dev):**

| SM Secret | Keys | Notes |
|---|---|---|
| `shared/anthropic-api-key` | _(plain)_ | Account-level |
| `shared/openai-api-key` | _(plain)_ | Account-level |
| `shared/google-api-key` | _(plain)_ | Account-level |
| `shared/cohere-api-key` | _(plain)_ | Account-level |
| `shared/groq-api-key` | _(plain)_ | Account-level |
| `shared/langsmith-api-key` | _(plain)_ | Account-level |
| `shared/sendgrid-api-key` | _(plain)_ | Account-level |
| `shared/airtable-api-key` | _(plain)_ | Account-level PAT |
| `shared/bland-api-key` | _(plain)_ | Account-level |
| `shared/voice-api-keys` | elevenlabs, deepgram, cartesia | Account-level |
| `shared/twilio-credentials` | account_sid, auth_token | Same Twilio account |
| `shared/google-cloud-sa` | project_id, client_email, private_key | Same GCP project |
| `shared/auth-secrets` | global_secret, jwt_secret, session_secret | Same auth secrets |
| `shared/copilot-api-credentials` | username, password | Internal API auth |
| `shared/service-tokens` | system_user_token, conversation_service_token | Internal tokens |
| `shared/support-email` | username, password | Same email |
| `shared/vapid-keys` | public_key, private_key | Same keypair |
| `shared/pinecone-api-key` | _(plain)_ | Same account; index via PS |

**Same infrastructure, copy from dev:**

| SM Secret | Keys | Confirmed |
|---|---|---|
| `shared/redis-credentials` | host, port, username, password, url | Same Redis Cloud instance for dev and prod |
| `shared/rabbitmq-url` | _(plain)_ | Same Amazon MQ broker for dev and prod |

**Different instances, need prod values:**

| SM Secret | Keys | Details |
|---|---|---|
| `shared/livekit-credentials` | api_key, api_secret, url | Two different instances on same GPU cluster — need prod api_key, api_secret, url |
| `shared/langfuse-keys` | public_key, secret_key | Dev project: `dev-indemn`, Prod project: `indemn` — need prod project keys |

**Unknown — need to verify (pull from prod EC2 `.env`):**

| SM Secret | Keys | Action |
|---|---|---|
| `shared/stripe-keys` | secret_key, publishable_key, webhook_secret, connect_webhook_secret | Pull from prod EC2 — webhook secrets may differ |
| `shared/firebase-credentials` | project_id, api_key, auth_domain, etc. | Pull from prod EC2 — DEVOPS-17 tracks separate projects |
| `shared/google-oauth` | client_id, client_secret, callback_url | Pull from prod EC2 — callback_url differs per domain |
| `shared/slack-webhook-url` | _(plain)_ | Pull from prod EC2 — may be same or different channel |

**Environment-specific (need prod values):**

| SM Secret | Keys | Source |
|---|---|---|
| `shared/mongodb-uri` | _(plain)_ | **Already populated** — prod cluster |

### Service-Specific Secrets (need prod equivalents)

| Dev Secret | Keys | Notes |
|---|---|---|
| `services/copilot-server/admin-credentials` | super_password, admin_password | Pull from prod EC2 |
| `services/copilot-server/chat21-credentials` | admin_token, jwt_secret | Pull from prod EC2 |
| `services/middleware/aws-s3-credentials` | access_key_id, secret_access_key, bucket_name | **bucket_name may differ** |
| `services/operations-api/carrier-credentials` | markel_*, cmf_*, gic_*, bonzah_*, insurica_* | **May be sandbox vs prod endpoints** |
| `services/operations-api/mixpanel-token` | _(plain)_ | Pull from prod EC2 |
| `services/email-channel/google-auth-credentials` | _(JSON blob)_ | Pull from prod EC2 |
| `services/observability/demo-credentials` | _(observatory)_ | May not need in prod |
| `services/observability/internal-api-key` | _(plain)_ | Pull from prod EC2 |

### Parameter Store (~105 params)

Most PS parameters are config values that differ between envs:
- **Service URLs**: All change from dev EC2 to prod EC2 addresses
- **Environment identifiers**: `dev` → `prod`
- **DD config**: dd-env, dd-service per service
- **Bot templates**: `bot-prompt-dev` → `bot-prompt-prod`
- **LangChain project**: `DEV` → `PROD`
- **Same across envs**: db names (tiledesk, openai), timeouts, ports, LLM defaults

### Prod Population Plan

1. Create `indemn-prod-services` IAM role (read access to `indemn/prod/*`)
2. Attach instance profile to prod EC2 (`i-00ef8e2bfa651aaa8`)
3. Copy shared secrets from dev → prod (for account-level keys)
4. Pull env-specific values from prod EC2 `.env` files (same process as dev)
5. Create all `/indemn/prod/*` PS parameters
6. Reference script: `scripts/populate-sm-secrets.sh` (create prod variant)

---

## Per-Repository Release Details

---

### 1. `Indemn-observatory` (indemn-observability) — HIGHEST PRIORITY

Observatory is **DOWN in prod** due to auth leak.

- **PR Links**:
  - [PR #27](https://github.com/indemn-ai/Indemn-observatory/pull/27): Auth — scope agent dropdown to selected org _(feature branch → main)_
  - [PR #28](https://github.com/indemn-ai/Indemn-observatory/pull/28): Deploy main → prod _(deploy PR, mergeable)_
  - PR #29: bot_ids org filter + voice/Distinguished report scripts _(feature branch → main)_
- **Craig's Work on main (18 commits)**:
  - Auth fix: scope `/api/metadata` to user's organizations (security — **leaked all org data**)
  - Auth: suppress PyJWT InsecureKeyLengthWarning
  - Voice evaluation: Langfuse sync to AWS pipeline, channel detection, evaluate UI
  - AWS Secrets Manager integration (4 PRs: initial, env loader fix, PATH discovery, workspace write)
  - SM/PS path rename to `indemn/` convention
  - CSR Time-of-Day activity page
  - Bug fixes: date objects, pagination, ingestion timeout, evaluate agent_id
  - Pie chart brand palette fixes
  - `get_all_bot_ids` org filter + voice/Distinguished report scripts
- **Craig's Work on feature branches**:
  - `fix/agent-dropdown-org-scoping` (PR #27): 3 commits — org dropdown scoping, PyJWT warning, metadata scoping
- **Unpushed local commits (5)**: pie chart fixes, bot_ids filter, demo-gic merge — **must push before deploy**
- **Environment Variables (SM/PS)**:
  - SM: mongodb-uri, langfuse-keys, auth-secrets
  - SM service-specific: observability/demo-credentials, observability/internal-api-key
  - PS service-specific: auth-enabled, cors-origins, dd-env/service/version, dd-logs-injection, dd-trace-enabled, mongodb-requests-collection
  - PS shared: environment, mongodb-db, copilot-server-url, copilot-api-url
- **Pre-Deployment Actions**:
  1. Populate prod SM/PS for observatory
  2. Push 5 unpushed local commits to `indemn/main`
  3. Merge PR #27 into main
  4. Merge PR #29 into main
  5. Update PR #28 with latest main
  6. Merge PR #28 (main → prod)
- **Post-Deployment Actions**: Verify observatory is back up, auth scoping works, Langfuse sync runs
- **Deployment Status**: NOT STARTED

---

### 2. `evaluations`

- **PR Links**:
  - [PR #7](https://github.com/indemn-ai/evaluations/pull/7): Transcript-based voice evaluation _(feature branch → main)_
  - [PR #8](https://github.com/indemn-ai/evaluations/pull/8): AWS Secrets Manager migration _(feature branch → main)_
  - [PR #9](https://github.com/indemn-ai/evaluations/pull/9): Voice simulation evaluation engine _(feature branch → main)_
  - **New PR needed**: main → prod
- **Craig's Work on main (20 commits)**:
  - COP-325 fixes: scope-filtered rules, tool log prompt, null criterion scores, tool execution log truncation, simulated user anchoring, evaluator model switch
  - Infrastructure: Docker/nginx/CI config for EC2 deployment, GHCR switch
  - Evaluation features: flat scoring aggregates, tool trace, agent context, sync endpoint, TestSet model, structured per-criterion JSON
  - Handoff detection, attribution indicators, echo fix (commit `346be29` — **diverged from remote main, needs reconciliation**)
  - Tests: 66 unit tests for V2 eval framework
  - Docs: bot-service payload contract
- **Craig's Work on feature branches**:
  - `feat/voice-simulation` (PR #9, 6 commits): voice simulation evaluation engine, tests, Deepgram SDK fix, LiveKit transcription refactor, voice metrics
  - `feat/voice-transcript-evaluation` (PR #7, 4 commits): transcript-based evaluation, Langfuse tool call fetch, fixes
  - `feat/aws-secrets-manager` (PR #8, 1 commit): SM migration
  - `feat/ff_evaluation` (2 commits, no PR): bot-service retry logic, score placeholder fix
- **Environment Variables (SM/PS)**:
  - SM shared (17): full shared block (mongodb-uri, redis, rabbitmq, all API keys, etc.)
  - PS shared: environment, mongodb-db, langchain-tracing-v2, langchain-project, langfuse-host, llm-provider/model/temperature/max-tokens, bot-service-url, evaluation-service-url
  - PS service-specific: langsmith-project, mongodb-database
- **Pre-Deployment Actions**:
  1. Populate prod SM/PS
  2. Reconcile local main divergence (different merge commits for PR #1)
  3. Push unpushed commit `346be29` (handoff detection)
  4. Merge PRs #7, #8, #9 into main
  5. Create main → prod PR
- **Post-Deployment Actions**: Verify eval service starts, voice eval endpoints respond
- **Deployment Status**: NOT STARTED

---

### 3. `copilot-dashboard`

- **PR Links**:
  - [PR #987](https://github.com/indemn-ai/copilot-dashboard/pull/987): AWS Secrets Manager migration _(feature branch → main)_
  - **New PR needed**: main → prod
- **Craig's Work on main (20 commits)**:
  - Evaluations Angular integration: wrapper, nav, routes, org-level evaluations, React component federation
  - Federation fixes: platform API routing, base URL, CSS injection, config service migration, error states
  - Agent lifecycle badge + ownership transfer
  - Jarvis chat loading indicator fix
  - CI: docker/build-push-action v1 → v6
- **Craig's Work on feature branches**:
  - `feat/aws-secrets-manager` (PR #987, 1 commit): SM migration
  - `fix/cop-325-jarvis-fob-purple` (1 commit): replace Lilac gradient with blue on Jarvis FOB
- **Environment Variables (SM/PS)**: Same as copilot-server (shared docker-compose), plus:
  - PS service-specific: chat-engine, upload-engine, push-engine, log-level, evaluation-service-url, middleware-service-url
- **Pre-Deployment Actions**:
  1. Populate prod SM/PS
  2. Merge PR #987 into main
  3. Reconcile: prod has `intake-manager-changes` hotfix not on main
  4. Create main → prod PR
- **Post-Deployment Actions**: Verify dashboard loads, evaluations tab works
- **Deployment Status**: NOT STARTED

---

### 4. `indemn-platform-v2` (copilot-dashboard-react)

- **PR Links**:
  - [PR #2](https://github.com/indemn-ai/copilot-dashboard-react/pull/2): Transcript type badge + filter UI _(feature branch → main)_
  - [PR #3](https://github.com/indemn-ai/copilot-dashboard-react/pull/3): Voice simulation type UI _(feature branch → main)_
- **Craig's Work on main (20 commits)**:
  - COP-325 UI fixes: rubric dropdown "None" option, metadata removal, theme color (purple→blue), test set display, scoring fallback, date wrapping, input parsing
  - Frontend separation from backend: Dockerfile, nginx, non-root nginx
  - Federation fixes: base URL for asset URLs, CSS injection prevention, CORS headers, platform API routing
  - Evaluation UI: 422 error surfacing, update guidance for Jarvis
  - Docs: README, CLAUDE.md updates
- **Craig's Work on feature branches**:
  - `feat/voice-simulation-type` (PR #3, 5 commits): voice_simulation type in eval UI, TestSetsList breakdown, filter chips
  - Transcript type (PR #2): transcript type support in evaluation UI
- **Environment Variables**: No SM migration — frontend app, env vars are build-time only
- **Pre-Deployment Actions**:
  1. Merge PR #2 into main
  2. Merge PR #3 into main
- **Post-Deployment Actions**: Verify build succeeds, eval UI shows voice types
- **Deployment Status**: NOT STARTED

---

### 5. `percy-service`

- **PR Links**:
  - **New PR needed**: main → prod (1 commit difference: `899ba7f`)
- **Craig's Work on main (13 commits)**:
  - Jarvis skills architecture: replace subagents with modular SKILL.md files
  - Evaluation connector validation and template fixes
  - Test-set-creation skill strengthening
  - Evaluation skill quality audit
  - Headless Jarvis polling fix
  - Data field descriptions, API payload format fixes
  - Docs: README, CLAUDE.md, initial scaffold
- **Environment Variables**: Percy manages its own env (not part of SM migration)
- **Pre-Deployment Actions**:
  1. Create main → prod PR
- **Post-Deployment Actions**: Verify percy-service starts, Jarvis skills load
- **Deployment Status**: NOT STARTED

---

### 6. `voice-livekit`

- **PR Links**:
  - [PR #83](https://github.com/indemn-ai/voice-livekit/pull/83): Eval mode for voice simulation _(feature branch → main)_
  - **New PR needed**: main → prod (29 commits on main not on prod)
- **Craig's Work on main (2 commits)**:
  - Langfuse trace metadata: add bot_id, CallSid, room_name to OTLP spans
  - Code review fixes for trace metadata
- **Craig's Work on feature branches**:
  - `feat/eval-mode` (PR #83, 2 commits): eval mode branch in entrypoint for voice simulation, uv.lock fix
- **Environment Variables**: voice-livekit uses `.env` files on GPU cluster, NOT SM/PS. Prod env at `/opt/voice-livekit/.env`, dev at `/opt/dev/voice-livekit/.env`. Deployment = update `.env` + pull code + restart.
  - Has its own: LANGFUSE keys, LIVEKIT creds, all LLM API keys, S3 creds, Redis, RabbitMQ, MongoDB
- **Pre-Deployment Actions**:
  1. Merge PR #83 into main
  2. Create main → prod PR
  3. Deploy to GPU cluster: pull code into `/opt/voice-livekit/`, update `.env` if needed (Langfuse keys may change for voice eval traces)
- **Post-Deployment Actions**: Verify voice agent starts, traces have new metadata fields
- **Deployment Status**: NOT STARTED

---

### 7. `bot-service`

- **PR Links**:
  - [PR #240](https://github.com/indemn-ai/bot-service/pull/240): Sanitize LLM parameters _(feature branch → main)_
  - [PR #247](https://github.com/indemn-ai/bot-service/pull/247): AWS Secrets Manager migration _(feature branch → main)_
  - [PR #248](https://github.com/indemn-ai/bot-service/pull/248): Langgraph dependency fixes _(feature branch → main)_
  - **New PR needed**: main → prod
- **Craig's Work (all on feature branches, nothing merged to main)**:
  - `feat/v2-integration` (6 commits): V2 routing in llm_graph, GraphFactory init, platform DB connection, agent detection, integration tests — **no PR yet**
  - `fix/sanitize-llm-parameters` (PR #240, 1 commit): sanitize params before init_chat_model — affects 59 prod bot configs
  - `feat/aws-secrets-manager` (PR #247, 1 commit): SM migration
  - `fix/dependabot-langgraph-upgrades` (PR #248, 1 commit): langgraph security fixes
  - `feat/eval-harness-integration` (1 commit): regression test integration — **no PR yet**
- **Environment Variables (SM/PS)**:
  - SM shared (17): full shared block + groq-api-key
  - PS shared (20+): environment, mongodb-db, all service URLs, LLM config, langchain/langfuse config, DD config, rabbitmq config
  - PS service-specific (6): service-name, dd-service/env/version, mongo-chat-history-db, testcase-max-concurrency, pinecone-text-key, langchain-endpoint, bot-api-base-url
- **Pre-Deployment Actions**:
  1. Populate prod SM/PS
  2. Merge PRs #240, #247, #248 into main (`feat/v2-integration` and `feat/eval-harness-integration` deferred — not in this release)
  3. Reconcile: prod has `package-import` fix not on main
  4. Create main → prod PR
- **Post-Deployment Actions**: Verify bot-service starts, LLM calls work
- **Deployment Status**: NOT STARTED

---

### 8. `copilot-server`

- **PR Links**:
  - [PR #796](https://github.com/indemn-ai/copilot-server/pull/796): AWS Secrets Manager migration _(feature branch → main)_
  - [PR #773](https://github.com/indemn-ai/copilot-server/pull/773): DEV → PROD _(deploy PR, open since Feb 24)_
- **Craig's Work on main (1 commit)**:
  - Agent lifecycle and ownership management
- **Craig's Work on feature branches**:
  - `feat/aws-secrets-manager` (PR #796, 1 commit): SM migration
- **Environment Variables (SM/PS)**:
  - SM shared (17) + SM additional shared (8): stripe-keys, firebase-credentials, sendgrid-api-key, google-oauth, airtable-api-key, service-tokens, copilot-api-credentials
  - SM service-specific (2): copilot-server/chat21-credentials, copilot-server/admin-credentials
  - PS shared (15+): environment, mongodb-db, all service URLs, sign-options-issuer, indemn-domain, api-url, server-base-url, node-env
  - PS service-specific (14): port, dd-service/env/version, jwt-expiration, admin-email, email-enabled/port, chat21 config, resthook/cache/queue enabled
- **Pre-Deployment Actions**:
  1. Populate prod SM/PS (including chat21-credentials, admin-credentials)
  2. Merge PR #796 into main
  3. Reconcile: prod has `org-availability-endpoint` hotfix not on main
  4. Merge PR #773 (main → prod)
- **Post-Deployment Actions**: Verify copilot-server starts, Firebase auth works
- **Deployment Status**: NOT STARTED

---

### 9. `voice-service`

- **PR Links**:
  - [PR #38](https://github.com/indemn-ai/voice-service/pull/38): AWS Secrets Manager migration _(feature branch → main)_
  - [PR #30](https://github.com/indemn-ai/voice-service/pull/30): DEV → PROD _(deploy PR, open since Feb 9)_
- **Craig's Work on feature branches**:
  - `feat/aws-secrets-manager` (PR #38, 1 commit): SM migration
- **Environment Variables (SM/PS)**:
  - SM shared (17) + twilio-credentials, google-cloud-sa
  - PS shared: environment, mongodb-db, node-env, dd-agent-host/port
  - PS service-specific: port, cartesia-api-version, cartesia-base-url
- **Pre-Deployment Actions**:
  1. Populate prod SM/PS
  2. Merge PR #38 into main
  3. Update and merge PR #30 (main → prod)
- **Post-Deployment Actions**: Verify voice-service starts, Twilio connects
- **Deployment Status**: NOT STARTED

---

### 10. `conversation-service`

- **PR Links**:
  - [PR #131](https://github.com/indemn-ai/conversation-service/pull/131): AWS Secrets Manager migration _(feature branch → main)_
  - **New PR needed**: main → prod
- **Craig's Work on feature branches**:
  - `feat/aws-secrets-manager` (PR #131, 1 commit): SM migration
  - `feat/pre-payment-validation` (2 commits): remove hardcoded validation rules — **deferred, not in this release**
- **Environment Variables (SM/PS)**:
  - SM shared (17) + airtable-api-key, service-tokens
  - PS shared: environment, mongodb-db, mongodb-openai-db, pinecone-environment, service URLs, rabbitmq config, default-system-user-id
  - PS service-specific: dd-service/env/version, mongo-collection-name, master-db-name, master-collection-name
- **Pre-Deployment Actions**:
  1. Populate prod SM/PS
  2. Merge PR #131 into main
  3. Create main → prod PR
- **Post-Deployment Actions**: Verify conversation-service starts, RabbitMQ connects
- **Deployment Status**: NOT STARTED

---

### 11-16. SM Migration Only Repos

These repos have **only** the AWS Secrets Manager migration commit from Craig.

#### 11. `middleware-socket-service`
- **PR**: [#338](https://github.com/indemn-ai/middleware-socket-service/pull/338) (SM migration → main)
- **New PR needed**: main → prod
- **SM/PS**: shared (17) + twilio-credentials, bland-api-key, service-tokens, copilot-api-credentials + services/middleware/aws-s3-credentials
- **PS service-specific**: port, dd-service/env, region-name + shared service URLs

#### 12. `kb-service`
- **PR**: [#138](https://github.com/indemn-ai/kb-service/pull/138) (SM migration → main)
- **New PR needed**: main → prod
- **SM/PS**: shared (17) + copilot-api-credentials (username/password)
- **PS service-specific**: dd-service/env/version, default-system-user-id + shared config

#### 13. `copilot-sync-service`
- **PR**: [#116](https://github.com/indemn-ai/copilot-sync-service/pull/116) (SM migration → main)
- **New PR needed**: main → prod
- **SM/PS**: same as middleware (shared docker-compose)
- **PS service-specific**: dd-service/env, port, rabbitmq-queue-name

#### 14. `payment-service`
- **PR**: [#56](https://github.com/indemn-ai/payment-service/pull/56) (SM migration → main)
- **New PR needed**: main → prod
- **SM/PS**: shared (17) + stripe-keys (4 keys incl. webhook secrets)
- **PS service-specific**: port, dd-service/env

#### 15. `operations_api`
- **PR**: [#92](https://github.com/indemn-ai/operations_api/pull/92) (SM migration → main)
- **New PR needed**: main → prod
- **SM/PS**: minimal shared (mongodb-uri, airtable-api-key, copilot-api-credentials) + services/operations-api/carrier-credentials, mixpanel-token
- **PS service-specific**: port, dd-service/env/version, node-env

#### 16. `email-channel-service`
- **PR**: [#35](https://github.com/indemn-ai/email-channel-service/pull/35) (SM migration → main)
- **New PR needed**: main → prod
- **SM/PS**: minimal shared (mongodb-uri, rabbitmq-url) + services/email-channel/google-auth-credentials
- **PS service-specific**: scheduler-time-interval-minutes

---

## Pre-Deployment Checklist: AWS Infrastructure & Secrets

### Phase 1: AWS Infrastructure (Craig — from local machine)

- [x] **1.1** ~~Create IAM role `indemn-prod-services`~~ — Done (2026-03-10). Policy: `prod-secrets-and-parameters-readonly`, mirrors dev role with dev↔prod swapped.
- [x] **1.2** ~~Create instance profile for `indemn-prod-services`~~ — Done
- [x] **1.3** ~~Attach instance profile to **prod-services** EC2~~ — Done (`i-00ef8e2bfa651aaa8`)
- [x] **1.4** ~~Attach instance profile to **copilot-prod** EC2~~ — Done (`i-0df529ca541a38f3d`)
- [x] **1.5** ~~Determine if voice-livekit needs SM access~~ — **No**. voice-livekit uses its own `.env` files.
- [x] **1.6** ~~Verify AWS CLI v2 is installed on both prod EC2s~~ — Done (installed on copilot-prod, already present on prod-services)
- [x] **1.7** ~~Add temporary write policy, then remove~~ — Done (added for population, removed after)

### Phase 2: Create Prod SM Secrets (Craig — from local machine via `aws` CLI)

**Copy from dev (account-level, identical values):** — ALL DONE (2026-03-10)
- [x] **2.1–2.20** All 20 shared secrets copied from dev to prod

**Already exists:**
- [x] **2.21** `indemn/prod/shared/mongodb-uri` ← already populated

**Need prod-specific values (Craig to provide):**
- [x] **2.22** ~~`indemn/prod/shared/livekit-credentials`~~ — Done (pulled from voice-livekit EC2)
- [x] **2.23** ~~`indemn/prod/shared/langfuse-keys`~~ — Done (Craig provided prod project keys)

**Pull from prod EC2 `.env` files:** — ALL DONE (2026-03-10, via populate scripts run on EC2)
- [x] **2.24** `indemn/prod/shared/stripe-keys` — Created from copilot-prod + connect_webhook_secret patched from prod-services
- [x] **2.25** `indemn/prod/shared/firebase-credentials` — Created from copilot-prod
- [x] **2.26** `indemn/prod/shared/google-oauth` — **SKIPPED** (not configured in prod, no GOOGLE_CLIENT_ID in tiledesk .env)
- [x] **2.27** `indemn/prod/shared/slack-webhook-url` — Created from bot-service .env on prod-services
- [x] **2.28** `indemn/prod/shared/sendgrid-api-key` — Updated with prod value from copilot-prod
- [x] **2.29** `indemn/prod/services/copilot-server/admin-credentials` — Created from copilot-prod
- [x] **2.30** `indemn/prod/services/copilot-server/chat21-credentials` — Created from copilot-prod
- [x] **2.31** `indemn/prod/services/observability/internal-api-key` — Created from copilot-prod
- [x] **2.32** `indemn/prod/services/observability/demo-credentials` — Created from copilot-prod
- [x] **2.33** `indemn/prod/services/middleware/aws-s3-credentials` — Created from prod-services
- [x] **2.34** `indemn/prod/services/operations-api/carrier-credentials` — Created from prod-services
- [x] **2.35** `indemn/prod/services/operations-api/mixpanel-token` — Created from prod-services
- [x] **2.36** `indemn/prod/services/email-channel/google-auth-credentials` — Created from prod-services

### Phase 3: Create Prod PS Parameters — DONE (2026-03-10)

114 parameters created under `/indemn/prod/`. Key changes from dev:
- `dd-env`, `environment`, `env` → `prod`
- `bot-engine-prompt-template` → `bot-prompt-prod`, `bot-engine-voice-prompt-template` → `prod-voice-prompt`
- `langchain-project` → `PROD-INDEMN`
- Service URLs — CORRECTED 2026-03-11 (verified against actual prod .env files):
  - `api-url` = `https://copilot.indemn.ai` (public domain, copilot-server port 3000 is `expose:` only)
  - `server-base-url` = `/api/` (relative path)
  - `copilot-server-url` = `https://copilot.indemn.ai`
  - `copilot-api-url` = `https://copilot.indemn.ai`
  - `middleware-url` = `https://proxy.indemn.ai`
  - `middleware-service-url` = `https://proxy.indemn.ai`
  - `sync-service-url` = `https://copilotsync.indemn.ai`
  - `copilot-sync-url` = `https://copilotsync.indemn.ai`
  - `evaluation-service-url` = `https://evaluations.indemn.ai/api/v1`
  - Private IPs for host-mapped services on prod-services: bot-service `:8001`, conversation `:9090`, kb `:8080`, voice `:9192`, payment `:4444`, operations `:4080`, langserver `:8001` — all at `172.31.22.7`
- DB names, LLM config, timeouts, ports — same as dev

### Phase 4: Verification — DONE (2026-03-10)

- [x] **4.1** 34 SM secrets under `indemn/prod/` (24 shared + 8 service-specific + langfuse + livekit)
- [x] **4.2** All service-specific SM secrets verified
- [x] **4.3** 114 PS parameters under `/indemn/prod/`
- [x] **4.4** Both prod EC2s verified: SM read + PS read working via instance profile

### Production Infrastructure Topology

| Instance | Name | IP | Type | Services | IAM Profile |
|---|---|---|---|---|---|
| `i-00ef8e2bfa651aaa8` | **prod-services** | 98.88.11.14 | t3.xlarge | bot-service, middleware, conversation, kb, payment, operations_api, email-channel, voice-service, copilot-sync, evaluations, percy-service, copilot-dashboard-react | **None** (needs `indemn-prod-services`) |
| `i-0df529ca541a38f3d` | **copilot-prod** | 54.226.32.134 | t3.xlarge | copilot-server, copilot-dashboard, observatory, intake-manager, form-extractor | **None** (needs `indemn-prod-services`) |
| `i-01e65d5494fd64b05` | **voice-livekit** | 3.236.53.208 | g4dn.xlarge | voice-livekit (dev at `/opt/dev/`, prod at `/opt/voice-livekit/`) | **None** (no SM — uses `.env` files) |

**Dev reference:** `i-0fde0af9d216e9182` (dev-services, 44.196.55.84) — has `indemn-dev-services` IAM profile

### Prod EC2 `.env` File Map (verified)

**prod-services** (98.88.11.14):
| Path | Service(s) |
|---|---|
| `/opt/bot-service/.env` | bot-service |
| `/opt/middleware/.env` | middleware-socket-service, copilot-sync-service |
| `/opt/utility-service/.env` | conversation-service |
| `/opt/openai-fastapi/.env` | kb-service |
| `/opt/payment-service/.env` | payment-service |
| `/opt/voice-service/.env` | voice-service |
| `/opt/operations_api/.env` | operations_api |
| `/opt/email-channel-service/.env` | email-channel-service |
| `/opt/evaluations/.env` | evaluations |
| `/opt/percy-service/.env` | percy-service |
| `/opt/copilot-dashboard-react/.env` | indemn-platform-v2 (React frontend) |
| `/opt/.env` | shared base (MongoDB, API keys, LangSmith) |

**copilot-prod** (54.226.32.134):
| Path | Service(s) |
|---|---|
| `/opt/tiledesk/.env` | copilot-server, copilot-dashboard |
| `/opt/Indemn-observatory/.env` | observatory |
| `/opt/Intake-manager/.env` | intake-manager |
| `/opt/form-extractor/.env` | form-extractor |

**voice-livekit** (3.236.53.208):
| Path | Service(s) |
|---|---|
| `/opt/voice-livekit/.env` | voice-livekit (prod) |
| `/opt/dev/voice-livekit/.env` | voice-livekit (dev) |

### Phase 5: Pull Secrets from Prod EC2s — DONE (2026-03-10)

Secrets pulled from all 3 EC2s using populate scripts that ran ON the EC2 (secrets never left the box). AWS CLI v2 installed on both copilot-prod and prod-services. Temporary write policy added and removed.

---

## All PRs — Complete Reference

### PRs into main (feature branches → main)

| # | Repo | PR | Description | Status |
|---|------|----|-------------|--------|
| 1 | evaluations | [#7](https://github.com/indemn-ai/evaluations/pull/7) | Voice transcript evaluation | Open — awaiting review |
| 2 | evaluations | [#8](https://github.com/indemn-ai/evaluations/pull/8) | AWS Secrets Manager migration | Open — awaiting review |
| 3 | evaluations | [#9](https://github.com/indemn-ai/evaluations/pull/9) | Voice simulation evaluation engine | Open — awaiting review |
| 4 | evaluations | [#10](https://github.com/indemn-ai/evaluations/pull/10) | Handoff detection, attribution, echo fix | Open — awaiting review |
| 5 | copilot-dashboard-react | [#2](https://github.com/indemn-ai/copilot-dashboard-react/pull/2) | Transcript type UI | Open — awaiting review |
| 6 | copilot-dashboard-react | [#3](https://github.com/indemn-ai/copilot-dashboard-react/pull/3) | Voice simulation type UI | Open — awaiting review |
| 7 | bot-service | [#247](https://github.com/indemn-ai/bot-service/pull/247) | AWS Secrets Manager migration | Open — awaiting review |
| 8 | bot-service | [#248](https://github.com/indemn-ai/bot-service/pull/248) | Langgraph dependency security fixes | Open — awaiting review |
| 9 | Indemn-observatory | [#27](https://github.com/indemn-ai/Indemn-observatory/pull/27) | Auth: scope agent dropdown to org | **Merged** |
| 10 | Indemn-observatory | [#29](https://github.com/indemn-ai/Indemn-observatory/pull/29) | bot_ids org filter + reports | Open — awaiting review |
| 11 | copilot-server | [#796](https://github.com/indemn-ai/copilot-server/pull/796) | AWS Secrets Manager migration | Open — awaiting review |
| 12 | copilot-dashboard | [#987](https://github.com/indemn-ai/copilot-dashboard/pull/987) | AWS Secrets Manager migration | Open — awaiting review |
| 13 | voice-service | [#38](https://github.com/indemn-ai/voice-service/pull/38) | AWS Secrets Manager migration | Open — awaiting review |
| 14 | conversation-service | [#131](https://github.com/indemn-ai/conversation-service/pull/131) | AWS Secrets Manager migration | Open — awaiting review |
| 15 | middleware-socket-service | [#338](https://github.com/indemn-ai/middleware-socket-service/pull/338) | AWS Secrets Manager migration | Open — awaiting review |
| 16 | kb-service | [#138](https://github.com/indemn-ai/kb-service/pull/138) | AWS Secrets Manager migration | Open — awaiting review |
| 17 | copilot-sync-service | [#116](https://github.com/indemn-ai/copilot-sync-service/pull/116) | AWS Secrets Manager migration | Open — awaiting review |
| 18 | payment-service | [#56](https://github.com/indemn-ai/payment-service/pull/56) | AWS Secrets Manager migration | Open — awaiting review |
| 19 | operations_api | [#92](https://github.com/indemn-ai/operations_api/pull/92) | AWS Secrets Manager migration | Open — awaiting review |
| 20 | email-channel-service | [#35](https://github.com/indemn-ai/email-channel-service/pull/35) | AWS Secrets Manager migration | Open — awaiting review |
| 21 | voice-livekit | [#83](https://github.com/indemn-ai/voice-livekit/pull/83) | Eval mode for voice simulation | **Merged** |

**Deferred (not in this release):**
- bot-service [#240](https://github.com/indemn-ai/bot-service/pull/240): Sanitize LLM parameters
- bot-service `feat/v2-integration`: V2 routing (no PR)
- bot-service `feat/eval-harness-integration`: Regression tests (no PR)
- conversation-service `feat/pre-payment-validation`: Remove hardcoded validation (no PR)

**Reviewer:** dhruvrajkotia assigned on all open PRs.

### Deploy PRs (main → prod)

| # | Repo | PR | EC2 | Deploy Path | Status |
|---|------|----|-----|-------------|--------|
| 1 | Indemn-observatory | [#28](https://github.com/indemn-ai/Indemn-observatory/pull/28) | copilot-prod | `/opt/Indemn-observatory/` | Open (pre-existing) |
| 2 | copilot-server | [#773](https://github.com/indemn-ai/copilot-server/pull/773) | copilot-prod | `/opt/tiledesk/` | Open (pre-existing) |
| 3 | copilot-dashboard | [#989](https://github.com/indemn-ai/copilot-dashboard/pull/989) | copilot-prod | `/opt/tiledesk/` | Open (new) |
| 4 | bot-service | [#249](https://github.com/indemn-ai/bot-service/pull/249) | prod-services | `/opt/bot-service/` | Open (new) |
| 5 | voice-service | [#30](https://github.com/indemn-ai/voice-service/pull/30) | prod-services | `/opt/voice-service/` | Open (pre-existing) |
| 6 | conversation-service | [#132](https://github.com/indemn-ai/conversation-service/pull/132) | prod-services | `/opt/utility-service/` | Open (new) |
| 7 | middleware-socket-service | [#339](https://github.com/indemn-ai/middleware-socket-service/pull/339) | prod-services | `/opt/middleware/` | Open (new) |
| 8 | kb-service | [#139](https://github.com/indemn-ai/kb-service/pull/139) | prod-services | `/opt/openai-fastapi/` | Open (new) |
| 9 | copilot-sync-service | [#117](https://github.com/indemn-ai/copilot-sync-service/pull/117) | prod-services | `/opt/middleware/` | Open (new) |
| 10 | payment-service | [#57](https://github.com/indemn-ai/payment-service/pull/57) | prod-services | `/opt/payment-service/` | Open (new) |
| 11 | operations_api | [#93](https://github.com/indemn-ai/operations_api/pull/93) | prod-services | `/opt/operations_api/` | Open (new) |
| 12 | email-channel-service | [#36](https://github.com/indemn-ai/email-channel-service/pull/36) | prod-services | `/opt/email-channel-service/` | Open (new) |
| 13 | voice-livekit | [#84](https://github.com/indemn-ai/voice-livekit/pull/84) | voice-livekit GPU | `/opt/voice-livekit/` | Open (new) |
| 14 | percy-service | [#5](https://github.com/indemn-ai/percy-service/pull/5) | prod-services | `/opt/percy-service/` | Open (new) |

**Pending deploy PRs** (can't create until feature PRs merge to main — main = prod currently):
- evaluations — need deploy PR after #7, #8, #9, #10 merge
- copilot-dashboard-react — need deploy PR after #2, #3 merge

### Coupled Deploys (must merge together)
- **copilot-dashboard + copilot-server** → both deploy to `/opt/tiledesk/` on copilot-prod — share docker-compose.yml
- **middleware-socket-service + copilot-sync-service** → both deploy to `/opt/middleware/` on prod-services — share docker-compose.yml

## Deployment Order (Recommended)

### Phase 0: AWS Infrastructure — DONE
- [x] IAM role `indemn-prod-services` created
- [x] Instance profiles attached to prod-services + copilot-prod EC2s
- [x] 34 SM secrets populated
- [x] 114 PS parameters created (9 URL params corrected 2026-03-11)
- [x] AWS CLI v2 installed on both prod EC2s
- [x] PS service URLs verified against actual prod .env files (2026-03-11)
- [x] Loader scripts fixed: .env base-copy + Firebase naming + QUOTE_PRICE alias (2026-03-11, all 13 repos pushed)

### Phase 1: copilot-prod EC2 (54.226.32.134) — observatory is DOWN
1. **Indemn-observatory** — CRITICAL, service is down in prod → merge deploy PR [#28](https://github.com/indemn-ai/Indemn-observatory/pull/28)
2. **copilot-server + copilot-dashboard** — coupled deploy → merge [#773](https://github.com/indemn-ai/copilot-server/pull/773) + [#989](https://github.com/indemn-ai/copilot-dashboard/pull/989) together

### Phase 2: prod-services EC2 (98.88.11.14) — core services
3. **bot-service** → merge [#249](https://github.com/indemn-ai/bot-service/pull/249) (`/opt/bot-service/`)
4. **middleware-socket-service + copilot-sync-service** — coupled → merge [#339](https://github.com/indemn-ai/middleware-socket-service/pull/339) + [#117](https://github.com/indemn-ai/copilot-sync-service/pull/117) (`/opt/middleware/`)
5. **conversation-service** → merge [#132](https://github.com/indemn-ai/conversation-service/pull/132) (`/opt/utility-service/`)
6. **kb-service** → merge [#139](https://github.com/indemn-ai/kb-service/pull/139) (`/opt/openai-fastapi/`)
7. **voice-service** → merge [#30](https://github.com/indemn-ai/voice-service/pull/30) (`/opt/voice-service/`)
8. **payment-service** → merge [#57](https://github.com/indemn-ai/payment-service/pull/57) (`/opt/payment-service/`)
9. **operations_api** → merge [#93](https://github.com/indemn-ai/operations_api/pull/93) (`/opt/operations_api/`)
10. **email-channel-service** → merge [#36](https://github.com/indemn-ai/email-channel-service/pull/36) (`/opt/email-channel-service/`)

### Phase 3: voice-livekit GPU (3.236.53.208)
11. **voice-livekit** → merge [#84](https://github.com/indemn-ai/voice-livekit/pull/84), pull code on GPU cluster

### Phase 4: Standalone services
12. **evaluations** → create + merge deploy PR after feature PRs merge (`/opt/evaluations/`)
13. **percy-service** → merge [#5](https://github.com/indemn-ai/percy-service/pull/5) (`/opt/percy-service/`)
14. **copilot-dashboard-react** → create + merge deploy PR after feature PRs merge (`/opt/copilot-dashboard-react/`)
