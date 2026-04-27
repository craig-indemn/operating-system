---
ask: "How do we migrate gic-email-intelligence from Railway + Craig's personal GitHub to Indemn's standard EC2/Secrets-Manager/Amplify stack without breaking live production?"
created: 2026-04-27
workstream: gic-email-intelligence
session: 2026-04-27-a
sources:
  - type: codebase
    description: "Full map of /Users/home/Repositories/gic-email-intelligence — services, Dockerfile, entrypoint, CLI, deepagent, proxy"
  - type: codebase
    description: "Indemn microservice patterns: bot-service, indemn-observability, intake-manager, web-operators"
  - type: ec2
    description: "AWS account 780354157690 — 7 instances inventoried; dev-services i-0fde0af9d216e9182, prod-services i-00ef8e2bfa651aaa8, indemn-windows-server i-0dc2563c9bc92aa0e"
  - type: railway
    description: "Project 4011d186-1821-49f5-a11b-961113e6f78d — api/sync/agent/automation services across dev + prod environments"
  - type: github
    description: "Target repo indemn-ai/gic-email-intelligence created 2026-04-27 by Dhruv, empty"
  - type: brainstorming
    description: "9-question brainstorm session 2026-04-27 with Craig — strategic decisions captured"
---

# GIC → Indemn Infrastructure Migration — Design

## Goal

Move `gic-email-intelligence` from its current Railway + personal-GitHub footprint onto Indemn's standard infrastructure (indemn-ai GitHub org, dev-services / prod-services EC2 with Docker Compose, AWS Secrets Manager, Amplify), establishing a CI/CD pipeline and cleaning up tech debt along the way. Production is live and must keep delivering through the migration.

## Non-Goals

- **Multi-tenancy / generalization** of the codebase. The repo stays GIC-specific; future customers are a separate workstream.
- **Database migration** to a different Atlas cluster. All data stays on `dev-indemn.mifra5.mongodb.net` for Phase 1; the cluster relocation is Phase 2.
- **Outlook add-in migration** off Vercel. The add-in stays on `gic-addin.vercel.app` through cutover; Amplify move is a follow-up.
- **Structural refactors** (skill-prompt registry, deepagents fork, multi-tenancy, LangSmith fix). Cleanup is dead-code-and-conformance only.
- **Switching LLM provider posture.** Gemini Vertex remains the canonical runtime default; Anthropic remains the hot-spare. Both stay supported.

## Decisions Summary

| # | Decision |
|---|---|
| 1 | Clean rebuild during migration; dev-side soak before prod cutover |
| 2 | Co-locate on `dev-services` (i-0fde0af9d216e9182) + `prod-services` (i-00ef8e2bfa651aaa8) EC2 |
| 3 | Long-running containers with internal scheduling (APScheduler / asyncio loops) — no systemd timers, no cron containers |
| 4 | Repo: `indemn-ai/gic-email-intelligence` (already created, empty) |
| 5 | Compute migrates now; Atlas cluster relocation is Phase 2 |
| 6 | Soft cutover: EC2 prod up alongside paused Railway prod; Railway destroyed within the week |
| 7 | Cleanup scope B (recommended): dead code purge + Indemn-pattern conformance + CI/CD + secrets — no refactors |
| 8 | Outlook add-in stays on Vercel through migration |
| 9 | Gemini Vertex as documented runtime default; Anthropic as hot-spare; both secrets provisioned |

## Target Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │  GitHub: indemn-ai/gic-email-intelligence   │
                    │  Branches: main (dev), prod                 │
                    │  Actions: build.yml, build-prod.yml         │
                    └────────────────┬────────────────────────────┘
                                     │
                                     │ docker buildx → push
                                     ▼
                    ┌─────────────────────────────────────────────┐
                    │  Docker Hub: indemneng/gic-email-intelligence│
                    │  Tags: main, prod, {branch}-{run_number}    │
                    └────────┬────────────────────────────────────┘
                             │ pull
            ┌────────────────┼────────────────┐
            ▼                                 ▼
  ┌─────────────────────┐         ┌─────────────────────┐
  │  EC2 dev-services   │         │  EC2 prod-services  │
  │  i-0fde0af9d216e9182│         │  i-00ef8e2bfa651aaa8│
  │  Self-hosted runner │         │  Self-hosted runner │
  │                     │         │                     │
  │ /opt/gic-email-intelligence/ │ /opt/gic-email-intelligence/│
  │   docker-compose.yml         │   docker-compose.yml        │
  │   .env.aws                   │   .env.aws                  │
  │                     │         │                     │
  │  Containers:        │         │  Containers:        │
  │   • api (8080)      │         │   • api (8080)      │
  │   • sync-cron       │         │   • sync-cron       │
  │   • processing-cron │         │   • processing-cron │
  │   • automation-cron │         │   • automation-cron │
  └──────────┬──────────┘         └──────────┬──────────┘
             │                               │
             │  reads/writes                 │  reads/writes
             ▼                               ▼
  ┌─────────────────────────────────────────────────────┐
  │  MongoDB Atlas — dev-indemn.mifra5.mongodb.net      │
  │  DB: gic_email_intelligence (Phase 1)               │
  │  Allowlist: dev-services EIP, prod-services EIP     │
  └─────────────────────────────────────────────────────┘
             │                               │
             │  outbound HTTPS               │  outbound HTTPS
             ▼                               ▼
  ┌──────────────────────┐    ┌─────────────────────────────┐
  │  Microsoft Graph API │    │  Unisoft proxy on EC2       │
  │  (quote@gic...)      │    │  indemn-windows-server      │
  │  S3 indemn-gic-att.. │    │  i-0dc2563c9bc92aa0e         │
  │  Vertex AI / Anthrop │    │  UAT :5000  Prod :5001      │
  │  Form extractor      │    │  SG sg-04cc0ee7a09c15ffb    │
  └──────────────────────┘    └─────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │  AWS Amplify (account 780354157690)                 │
  │  App d244t76u9ej8m0 — gic-email-intelligence        │
  │  Source: indemn-ai/gic-email-intelligence (rewire)  │
  │  Branches: main → dev, prod → gic.indemn.ai         │
  └─────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │  Vercel (status quo, unchanged this phase)          │
  │  gic-addin.vercel.app — Outlook add-in              │
  └─────────────────────────────────────────────────────┘
```

Egress: dev-services and prod-services connect outbound via their attached EIPs. Both EIPs are added to (a) Atlas Network Access on the `dev-indemn` project and (b) the Unisoft proxy SG `sg-04cc0ee7a09c15ffb` on ports 5000/5001. Railway's `162.220.234.15` is removed from both after cutover.

## Phase 1.0: Pre-Cutover Code Work (Required Before Infra Cutover)

These code changes are load-bearing for the cutover safety story and must ship in the initial commit to `indemn-ai/gic-email-intelligence` before any infra is migrated. Surfaced by parallel design review on 2026-04-27.

1. **`--loop --interval N` flags on the cron commands with SIGTERM handling.** The current CLI commands (`sync run`, `automate run`, `automate process` / `agent process`) are one-tick and `sys.exit()`-based. The "long-running container with internal scheduling" decision (Q3 in the brainstorm) cannot ship without converting these to opt-in loop mode. The wrapper must trap SIGTERM so `docker stop` can drain a tick gracefully — without it, a SIGTERM mid-`SetQuote` could leave Mongo state inconsistent with Unisoft state:
   ```python
   _shutdown = False
   def _sigterm(_signum, _frame):
       global _shutdown
       _shutdown = True
   signal.signal(signal.SIGTERM, _sigterm)
   signal.signal(signal.SIGINT, _sigterm)

   def run_loop(interval: int, single_tick: Callable):
       while not _shutdown:
           settings = Settings()  # reload env each tick — picks up PAUSE_* changes without restart
           try:
               single_tick(settings)
           except Exception:
               logger.exception("tick failed")
           # interruptible sleep
           for _ in range(interval):
               if _shutdown:
                   break
               time.sleep(1)
   ```
   The flag stays opt-in so local CLI invocation and one-shot batch runs still work as before. The settings-per-tick reload is what makes pause flags fast (<1s response on next tick boundary instead of waiting up to 300s for the loop to wake up); the interruptible sleep is what lets `docker stop` drain a paused container in seconds rather than minutes.

2. **`PAUSE_SYNC` env var + enforcement in sync loop.** Currently only `PAUSE_PROCESSING` (checked at `harness.py:445`) and `PAUSE_AUTOMATION` (checked at `automate.py:52`) exist. `PAUSE_SYNC` is referenced in the cutover runbook but doesn't exist in code. Add `pause_sync: bool = False` to `config.py`, check it at the top of the sync command. Without this, we cannot safely pause Railway sync during the EC2 dev soak — both syncs would clobber each other's `sync_state.last_sync_at` token, causing duplicate or missed emails.

3. **Stale-claim recovery for `automation_status: processing` (with idempotency caveat).** The codebase has stale-claim recovery for `processing_status` (5-minute timeout, see `process_new_email.py:27-38`), but `automation_status` has no equivalent. If an automation cron crashes mid-tick — or if the container is killed during cutover — the email is orphaned forever (`{automation_status: processing}` doesn't match the `next` query that looks for unset/null). Add a parallel recovery function: emails with `automation_status=processing` and `automation_started_at` older than the timeout are reset to null. Wire it in at the top of each automation tick.

   **Idempotency caveat — important.** The automation agent's writes to Unisoft are NOT idempotent (`SetQuote` with `Action=Insert` creates a new Quote each call). If a crash happens *after* a Quote is created in Unisoft but *before* `gic emails complete` writes the `unisoft_quote_id` back to Mongo, naive recovery would re-run the agent and create a duplicate Quote. Two mitigations, both required:
   - **Conservative timeout: 60 minutes** (not 30) so the recovery only fires on truly-stuck claims, not slow-but-progressing ticks.
   - **Pre-recovery duplicate check.** Before resetting `automation_status` to null, the recovery function should call the underlying Python equivalent of `gic submissions check-duplicate --name "..."` (the existing CLI lives at `cli/commands/submissions.py:575`; expose its inner helper for in-process use). If a recent submission already has a `unisoft_quote_id` for the same name, log a `WARN: stale claim with possible Unisoft side-effect for email_id=...` and **leave it as `failed_recovery_review`** (a new automation_status state) rather than resetting to null. This forces human review for the ambiguous case rather than risking a duplicate. If Unisoft / Mongo is unreachable when recovery fires, fail-closed: skip recovery for this tick, retry next tick — never reset on the basis of an inconclusive duplicate check.

   Add Datadog alerting on `automation_status=failed_recovery_review` count > 0 so on-call sees orphans needing reconciliation.

4. **Healthcheck split: `/healthz` (process-alive) vs `/api/health` (DB-rich).** The current `/api/health` makes 3+ Mongo queries with 3-second timeouts (`api/routes/health.py`). During cutover or any Mongo blip, Docker's healthcheck would fail and restart the container — an own-goal during the cutover window. Add a no-op `/healthz` returning 200 unconditionally; point the Docker healthcheck at it. Keep `/api/health` for monitoring/Datadog. Three coordinated changes: (a) add the route handler, (b) extend the rate-limit exemption in `api/main.py:76` to include `/healthz`, (c) update `docker-compose.yml` healthcheck to `curl -f http://localhost:8080/healthz`. All three must ship together or healthchecks misbehave.

5. **Env-var-ize `GRAPH_USER_EMAIL` AND parameterize the skill prompts.** Currently hardcoded as `"quote@gicunderwriters.com"` in `config.py:13` and referenced in 7+ places: `harness.py:151,156` (internal-sender detection), `agent.py:76` (agent system prompt), `unisoft_client.py:147`, `cli.py:305`, `stats.py:346`, **and inside the skill markdown files themselves** (`agent/skills/email_classifier.md:3` and `:107`). Step 1: make `graph_user_email` a required env var, no default. Step 2: replace hardcoded references in Python code with `settings.graph_user_email`. Step 3: convert the `.md` skill files to use `{graph_user_email}` placeholders, and add a `.format(graph_user_email=...)` step in `_load_skill()` (`automation/agent.py:60`) at load time. Without step 3, the LLM prompt still hardcodes the customer email regardless of the config — defeating the purpose.

6. **CORS env-var parsing via Pydantic validator + startup log.** When converting hardcoded CORS origins to `CORS_ORIGINS` env var, add a Pydantic validator that splits on commas and strips whitespace per origin (a leading space silently breaks origin matching, since CORS comparison is exact-string):
   ```python
   class Settings(BaseSettings):
       cors_origins: list[str] = ["http://localhost:5173"]

       @field_validator("cors_origins", mode="before")
       @classmethod
       def parse_cors(cls, v):
           if isinstance(v, str):
               return [s.strip() for s in v.split(",") if s.strip()]
           return v
   ```
   Add `logger.info(f"CORS allow_origins: {settings.cors_origins}")` at app startup so the parsed list is visible in logs — cheap insurance against silent regressions from a stray comma or trailing space.

7. **Add Settings fields for new env vars used in PARAM_MAP.** In addition to `PAUSE_SYNC` (item 2) and `CORS_ORIGINS` (item 6), `config.py` is missing fields for `UNISOFT_TASK_GROUP_ID_NEWBIZ`, `UNISOFT_TASK_GROUP_ID_WC`, and `PUBLIC_BASE_URL`. Today the LOB→GroupId routing happens inside the deepagent skill prompt (hardcoded `GroupId 3` for prod NEW BIZ, `4` for prod WC). Move those to env-driven settings so the prompt is parameterized — same `{name}.format(...)` pattern as item 5. `PUBLIC_BASE_URL` is for any code that builds outbound links (e.g., notification emails referencing the GIC dashboard); audit `core/` and `automation/` for hardcoded `gic.indemn.ai` references and replace.

The estimated effort for items 1–7 is roughly two days, parallelizable with the rest of the cleanup.

## Phase 1: Lift, Clean, and Shift

### 1.1 Repo bootstrap

Mechanic: push the cleaned-up code to `indemn-ai/gic-email-intelligence` as a new initial commit (single squashed commit). The personal repo (`craig-indemn/gic-email-intelligence`) becomes a frozen archive — readonly, retained for history, but no longer the source of truth. Branch protection on `main` and `prod` requires PR + green CI.

### 1.2 Cleanup scope (in the initial commit)

**Delete:**
- `addin-test/` — superseded test rig
- `data/` (the exploration corpus — emails.jsonl, vision results, batches). These are reproducible from MongoDB and S3; don't carry 2GB of PDFs into the org repo
- Root `*.html` workflow diagrams (`indemn-*-workflow.html`) — design artifacts, not code
- `*.deprecated` files (`agent/skills/stage_detector.md.deprecated`)
- One-off migration scripts in `/scripts/` that aren't load-bearing — keep only the actively-used helpers, document them, delete the rest

**Env-var-ize (no more hardcoded values):**
- `UNISOFT_PROXY_URL` — currently has `54.83.28.79:5001` as a fallback in `cli/commands/emails.py:272` and `unisoft-proxy/client/cli.py:46`. Make required, no default.
- CORS origins — currently hardcoded list in `api/main.py:54-61`. Convert to `CORS_ORIGINS` env var (comma-separated). Add startup log line. Strip whitespace.
- `GRAPH_USER_EMAIL` — currently hardcoded as `"quote@gicunderwriters.com"` in `config.py:13`. Make required, no default.
- `gic.indemn.ai` references in code — env-driven via `PUBLIC_BASE_URL`.

**Strip dead code:**
- `entrypoint.sh` Mongo-primary detection (lines 13–56) — Atlas SRV makes this unreachable. Replace with a one-line `exec "$@"`.
- `automation/agent.py` LocalShellBackend monkey-patch stays for now (out of scope per cleanup B), but add a comment marking it as a known fragile point with a TODO link to the follow-up.

**Pattern conformance (mirror bot-service):**
- Dockerfile is already multi-stage and non-root — keep, just verify ulimits/healthcheck align.
- Add `docker-compose.yml` Datadog labels per service.
- Add ulimits `nofile: {soft: 65536, hard: 65536}`.
- Add json-file logging caps (`max-size: 50m, max-file: 5, mode: non-blocking`).
- Confirm `/api/health` returns within healthcheck timeout (3s); otherwise add `/healthz` with no DB dependency.

**Add:**
- `README.md` covering local dev, Docker run, env vars, secret references.
- `docs/runbook.md` covering deploy procedure, common ops (pause/unpause crons), incident response.
- `.github/workflows/build.yml` and `build-prod.yml`.
- `.github/dependabot.yml`.
- `CODEOWNERS` (Craig, Dhruv).

### 1.3 CI/CD pipeline

Mirrors bot-service / indemn-observability exactly.

**`.github/workflows/build.yml`** (triggered on push to `main`):

1. Build job (ubuntu-latest):
   - Checkout
   - Slack notification (start)
   - Docker Buildx
   - Login to Docker Hub (`secrets.DOCKER_USERNAME`, `secrets.DOCKER_PASSWORD`)
   - Build + push `indemneng/gic-email-intelligence:main` and `indemneng/gic-email-intelligence:main-${{ github.run_number }}`
   - GHA cache (`cache-from: type=gha, cache-to: type=gha,mode=max`)
   - Slack notification (failure only)
2. Deploy job (`runs-on: [self-hosted, linux, x64, dev]`, `needs: build`):
   - Checkout
   - Docker Hub login
   - `AWS_ENV=dev AWS_SERVICE=gic-email-intelligence bash scripts/aws-env-loader.sh .env.aws`
   - `cp docker-compose.yml /opt/gic-email-intelligence/`
   - `cp .env.aws /opt/gic-email-intelligence/`
   - `cd /opt/gic-email-intelligence && docker compose pull && docker compose up -d`
   - Slack notification (failure)

**`build-prod.yml`** is identical with `prod` branch, prod runner labels, and `AWS_ENV=prod`.

The `aws-env-loader.sh` script lives in the GIC repo (copied from existing service repos). It pulls everything under `indemn/{env}/gic-email-intelligence/*` and `indemn/{env}/shared/*` into a `.env.aws` file at deploy time.

GitHub OIDC role `github-actions-deploy` already exists in the AWS account; attach a policy granting read on `indemn/dev/gic-email-intelligence/*` and `indemn/prod/gic-email-intelligence/*`.

### 1.4 AWS Secrets Manager + Parameter Store layout

**Secrets Manager (`indemn/{env}/gic-email-intelligence/*`):**

| Path | Contents |
|------|----------|
| `mongodb-uri` | full SRV connection string (matches existing Railway value through Phase 1) |
| `graph-credentials` | JSON: `{tenant_id, client_id, client_secret, user_email}` |
| `anthropic-api-key` | hot-spare LLM key |
| `google-cloud-sa-json` | full service-account JSON for Vertex AI (project `prod-gemini-470505`) |
| `unisoft-api-key` | proxy auth token (currently `84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de`) |
| `s3-credentials` | JSON if not using IAM role; preferred is IAM role on EC2, in which case this slot is unused |
| `jwt-secret` | shared with copilot-server |
| `tiledesk-db-uri` | for org-membership lookup |
| `api-token` | shared secret for service-to-service / add-in |
| `langsmith-api-key` | tracing (currently broken; future-fix) |

**Parameter Store (`/indemn/{env}/gic-email-intelligence/*`):**

Path convention matches existing services: shared params live at `/indemn/{env}/{param-name}` (e.g., `mongodb-db`, `llm-provider`); GIC-specific params live at `/indemn/{env}/gic-email-intelligence/{param-name}`. The `aws-env-loader.sh` script (copied from bot-service / observability) recursively pulls everything under `/indemn/{env}/` and maps each param-name → env-var-name via a hardcoded `PARAM_MAP`. **The shared map already covers `llm-provider`, `llm-model`, etc. but does NOT cover GIC-specific entries.** Required step: extend `PARAM_MAP` in the GIC repo's copy of `aws-env-loader.sh` with the entries below. **Items marked NEW require both a `Settings` field added to `config.py` (in Phase 1.0) AND the PARAM_MAP entry; existing entries only need PARAM_MAP.**

```python
# GIC-specific entries to add to PARAM_MAP
'pipeline-stages': 'PIPELINE_STAGES',                       # existing in Settings
'pause-processing': 'PAUSE_PROCESSING',                     # existing
'pause-automation': 'PAUSE_AUTOMATION',                     # existing
'pause-sync': 'PAUSE_SYNC',                                 # NEW (Phase 1.0 item 2)
'unisoft-proxy-url': 'UNISOFT_PROXY_URL',                   # existing
'unisoft-activity-action-id': 'UNISOFT_ACTIVITY_ACTION_ID', # existing
'unisoft-task-action-id': 'UNISOFT_TASK_ACTION_ID',         # existing
'unisoft-task-group-id-newbiz': 'UNISOFT_TASK_GROUP_ID_NEWBIZ',  # NEW (Phase 1.0)
'unisoft-task-group-id-wc': 'UNISOFT_TASK_GROUP_ID_WC',     # NEW (Phase 1.0)
's3-bucket': 'S3_BUCKET',                                   # existing
'cors-origins': 'CORS_ORIGINS',                             # NEW (Phase 1.0 item 6)
'public-base-url': 'PUBLIC_BASE_URL',                       # NEW (Phase 1.0)
'gic-org-id': 'GIC_ORG_ID',                                 # existing
'graph-user-email': 'GRAPH_USER_EMAIL',                     # existing (default removed in Phase 1.0 item 5)
'google-cloud-project': 'GOOGLE_CLOUD_PROJECT',             # existing
'google-cloud-location': 'GOOGLE_CLOUD_LOCATION',           # existing
'llm-model-fast': 'LLM_MODEL_FAST',                         # existing
```

GIC-specific params:

| Path | Value (dev / prod) |
|------|--------------------|
| `llm-provider` | `google_vertexai` (default) |
| `llm-model` | `gemini-2.5-pro` |
| `llm-model-fast` | `gemini-2.5-flash` |
| `pipeline-stages` | `extract,classify,link` |
| `pause-processing` | `false` |
| `pause-automation` | `false` |
| `unisoft-proxy-url` | `http://172.31.23.146:5000` (UAT, dev) / `http://172.31.23.146:5001` (Prod) — use the proxy's *private* IP since dev/prod-services and indemn-windows-server are in the same VPC |
| `unisoft-activity-action-id` | `6` (UAT) / `6` (Prod) |
| `unisoft-task-action-id` | `40` (UAT) / `70` (Prod) |
| `unisoft-task-group-id-newbiz` | `2` (UAT) / `3` (Prod) |
| `unisoft-task-group-id-wc` | `4` (UAT — same group) / `4` (Prod) |
| `s3-bucket` | `indemn-gic-attachments` |
| `aws-region` | `us-east-1` |
| `cors-origins` | `https://gic.indemn.ai,https://dev.gic.indemn.ai,https://gic-addin.vercel.app,https://main.d244t76u9ej8m0.amplifyapp.com` |
| `public-base-url` | `https://api-dev.gic.indemn.ai` (dev) / `https://api.gic.indemn.ai` (prod) — only set if/when we route the API through a custom domain |
| `gic-org-id` | `65eb3f19e5e6de0013fda310` |
| `graph-user-email` | `quote@gicunderwriters.com` |
| `google-cloud-project` | `prod-gemini-470505` |
| `google-cloud-location` | `us-central1` |

**Note on Unisoft proxy URL:** switching from public `54.83.28.79` to private `172.31.23.146` removes a hop through the internet, removes the security-group public-IP-allowlist requirement (in-VPC traffic is governed by SG rules between EC2s, not public IPs), and is the only correct choice for in-VPC service-to-service traffic. Existing SG rule on `sg-04cc0ee7a09c15ffb` already allows the VPC CIDR for ports 5000/5001 — verify; otherwise add.

### 1.5 Docker Compose service definitions

Single `docker-compose.yml` in the repo root, deployed verbatim to `/opt/gic-email-intelligence/` on both dev-services and prod-services.

```yaml
version: "3.3"

x-logging: &default-logging
  driver: json-file
  options: { max-size: "50m", max-file: "5", mode: "non-blocking" }

x-common: &common
  image: indemneng/gic-email-intelligence:${IMAGE_TAG:-main}
  restart: always
  logging: *default-logging
  ulimits:
    nofile: { soft: 65536, hard: 65536 }
  env_file: [.env.aws]
  networks: [gic-email, shared-datadog]
  stop_grace_period: 60s   # let SIGTERM-aware loop drain the current tick before SIGKILL

services:
  api:
    <<: *common
    container_name: gic-email-api
    command: uvicorn gic_email_intel.api.main:app --host 0.0.0.0 --port 8080
    expose: ["8080"]
    cpus: "1.0"
    mem_limit: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    labels:
      com.datadoghq.ad.logs: '[{"source":"python","service":"gic-email-api","log_processing_rules":[{"type":"multi_line","name":"python_traceback","pattern":"^[A-Za-z]"}]}]'

  sync-cron:
    <<: *common
    container_name: gic-email-sync
    command: python -m gic_email_intel.cli.main sync run --loop --interval 300
    cpus: "0.5"
    mem_limit: 512M
    labels:
      com.datadoghq.ad.logs: '[{"source":"python","service":"gic-email-sync"}]'

  processing-cron:
    <<: *common
    container_name: gic-email-processing
    command: python -m gic_email_intel.cli.main automate process --loop --interval 300 --workers 3
    cpus: "1.0"
    mem_limit: 2G
    labels:
      com.datadoghq.ad.logs: '[{"source":"python","service":"gic-email-processing"}]'

  automation-cron:
    <<: *common
    container_name: gic-email-automation
    command: python -m gic_email_intel.cli.main automate run --loop --interval 900 --max 50
    cpus: "1.0"
    mem_limit: 2G
    labels:
      com.datadoghq.ad.logs: '[{"source":"python","service":"gic-email-automation"}]'

networks:
  gic-email:
    driver: bridge
  shared-datadog:
    external: true
```

The `--loop --interval N` flags are the cleanup-pass change to the CLI commands. Each command keeps its existing single-tick body and wraps it in a loop with sleep:

```python
# pseudocode added to sync, automate process, automate run
def run_loop(interval: int, single_tick: Callable):
    while True:
        try:
            single_tick()
        except Exception:
            logger.exception("tick failed")
        time.sleep(interval)
```

This is what we agreed on for cron orchestration: one persistent process per service, internal scheduling, healthcheck-observable. The `--loop` flag is opt-in so local development and one-shot CLI invocation still work as before.

API exposure: behind the existing internal ALB / Caddy / nginx that other services on dev-services and prod-services already use for ingress. Hostnames `api.gic.indemn.ai` and `api-dev.gic.indemn.ai` (Route 53 → ALB → EC2:8080). Confirm during implementation whether the existing ALB on those EC2s is wired up similarly to bot-service, or whether we add a new listener rule.

### 1.6 Network / egress plumbing & allowlist updates

**EIPs (verified 2026-04-27):**
- dev-services `i-0fde0af9d216e9182` → EIP `44.196.55.84` (alloc `eipalloc-052cb05ad7610770a`)
- prod-services `i-00ef8e2bfa651aaa8` → EIP `98.88.11.14` (alloc `eipalloc-033cd7692f750f1ae`)
- Both stable; safe to use as outbound allowlist source.

**Atlas allowlist (`dev-indemn` project Network Access):**
- ADD: `44.196.55.84/32` (dev-services), `98.88.11.14/32` (prod-services)
- REMOVE (after cutover, only): Railway static IP `162.220.234.15`

**Unisoft proxy SG `sg-04cc0ee7a09c15ffb` (verified 2026-04-27):**

Current state: ports 5000 and 5001 each allow `162.220.234.15/32` (Railway), `73.87.128.242/32` (office), `96.244.115.146/32` (office). **No VPC CIDR rule, no SG-reference rule. In-VPC traffic from dev-services/prod-services is NOT permitted today.**

The cleanest fix is an SG-reference rule:
- ADD ingress on ports 5000/5001 with source = security group of dev-services
- ADD ingress on ports 5000/5001 with source = security group of prod-services

This is AWS best practice (no IP plumbing to maintain, automatically follows the source instances) and means the proxy permits any current/future container on those instances without further work.

The fallback (slightly less clean) is a VPC CIDR rule:
- ADD ingress on ports 5000/5001 with source = `172.31.0.0/16`

Either fix unblocks the design's choice to use the proxy's *private* IP `172.31.23.146` from EC2. Public-IP-based allowlist (adding the two EIPs) also works but defeats the point of staying in-VPC.

REMOVE (after cutover, only): `162.220.234.15/32` from both port rules. Office IPs stay.

**Datadog network:** `shared-datadog` Docker network is `external: true` — must already exist on the host. Confirm during dev-side bring-up via `docker network ls`.

### 1.7 Amplify rewire

Existing Amplify app `d244t76u9ej8m0` (account 780354157690, name `gic-email-intelligence`). Currently sourced from `craig-indemn/gic-email-intelligence`.

Steps:
1. Disconnect existing GitHub source
2. Reconnect to `indemn-ai/gic-email-intelligence`
3. Re-verify branch → environment mappings: `main` → `main.d244t76u9ej8m0.amplifyapp.com` (dev), `prod` → `gic.indemn.ai` (prod)
4. Update environment variables per branch:
   - `VITE_API_BASE` → dev/prod API URL on EC2
5. Trigger build of both branches once code is in the new repo

`amplify.yml` in the repo is already correct.

## Operational Readiness Beyond Cutover

These are the ongoing-operations concerns the cutover doesn't address by itself but that need to be in place either before or shortly after cutover for the system to be safely operable.

### Datadog alerts (must wire before cutover)

| Alert | Threshold | Page who | Severity |
|---|---|---|---|
| API container down (healthcheck failing) | 2 consecutive failures | Craig | P1 |
| Sync cron stalled | No new emails synced in >30 min during business hours | Craig | P2 |
| Processing backlog growing | `processing_status=pending` count > 50 for >15 min | Craig | P2 |
| Automation success rate drop | <80% over a rolling hour | Craig | P2 |
| Unisoft proxy unreachable | Connection refused / 5xx for >5 min | Craig | P1 |
| Stale-claim recovery firing | `automation_status=failed_recovery_review` count > 0 | Craig | P1 (manual reconciliation) |
| MongoDB connection failures | >5/min | Craig | P1 |
| Atlas connection-pool utilization | >75% | Craig | P2 (capacity warning) |

These are alert *rules*, not just dashboard panels. Wire them in Datadog with PagerDuty (or Slack-to-phone) routing.

### Datadog dashboards (should ship within first week post-cutover)

One dashboard for GIC with: cron tick rate per service, processing latency (email-to-complete), automation success/fail rate, Unisoft API latency p50/p95/p99, email throughput by hour, container resource utilization. JC gets a read-only link.

### Backup, recovery, RTO/RPO

- **Atlas backup tier:** confirm `dev-indemn` cluster is on a tier with point-in-time recovery (M10+). If not, upgrade *before* cutover. Document retention window (30 days minimum).
- **S3 versioning:** confirm `indemn-gic-attachments` has versioning enabled. If not, enable.
- **Pre-cutover snapshot:** on-demand Atlas snapshot taken at T-0 (runbook step 13). Snapshot ID + timestamp recorded in the cutover Slack thread.
- **RTO target:** 4 hours from total-loss to operational on a fresh EC2 (image pulled from Docker Hub, `.env.aws` re-materialized from Secrets Manager, services up, DNS unchanged because EIPs persist).
- **RPO target:** 1 hour (Atlas continuous backup) for Mongo data; near-zero for S3 attachments (versioned, durable).

**Snapshot recovery procedure (runbook entry):**

1. In Atlas UI: Backups → Restore Wizard → select snapshot by ID/timestamp. Choose "Download" for inspection or "Restore to a new cluster" for a clean restore destination. Do NOT restore in place over the live cluster.
2. Restore time estimate: 30–60 min for a small (`gic_email_intelligence` is < 5GB total) database.
3. Validation: counts match expected (`emails`, `submissions`, `extractions`, `unisoft_agents`) within ±5% of pre-snapshot, and a sample of the most recent 10 emails by `received_at` exists in the restore.
4. Cutover: pause all crons (`PAUSE_*=true` everywhere), update `MONGODB_URI` in Secrets Manager to point at the restored cluster, redeploy services, unpause.
5. Snapshot retention: Atlas continuous backup with 30-day retention (verify tier supports this; upgrade pre-cutover if needed).

### Encryption posture (document existing, no new work expected)

- In transit: HTTPS everywhere (Atlas, Graph API, Unisoft proxy via Caddy/nginx eventually, Vertex AI, Anthropic, S3).
- At rest: Atlas encrypts disk volumes by default. S3 bucket should have default SSE-S3 or SSE-KMS — verify pre-cutover and enable if not.
- Document this posture in `docs/security.md` so audits can find it.

### Data retention & deletion procedure

- **Default retention:** indefinite for now (the dataset is small and operationally useful for backfill / debugging).
- **Deletion procedure:** if GIC requests deletion of a record, the playbook is: identify all docs in `emails`, `submissions`, `extractions`, `assessments`, `drafts` keyed to the named insured; delete the corresponding S3 attachments under `s3://indemn-gic-attachments/...`; record the deletion in a new `data_deletions` Mongo collection (created lazily on first write) with timestamp + requester + scope. Codify as `gic admin delete-record --insured-name "..."` CLI command (post-cutover follow-up — does not exist today).

### Unisoft proxy SPOF — explicit risk acceptance

The Unisoft proxy on `i-0dc2563c9bc92aa0e` (single Windows EC2, t3.small, no HA) is a hard single point of failure. If it's down, automation halts. **Risk accepted** because:
- Restart time is minutes (Windows service restart via SSM)
- The instance type is reliable (t3 family, attached EIP)
- The proxy is stateless — restart loses no data
- Mongo holds the email queue; emails just stack up until proxy is back, then drain

**Contingency if down >1 hour:** notify JC, pause automation explicitly via `PAUSE_AUTOMATION=true`, manually process the highest-priority emails through the Unisoft web UI until proxy is restored, then unpause. Document this in `docs/runbook.md` as the "Unisoft proxy down" playbook.

The HA story (proxy on a second instance with health-check-driven failover) is a valid post-cutover follow-up, scoped separately.

### Image vulnerability scanning

CI pipeline (in `build.yml`) should add a Trivy scan step against the built image *before* push to Docker Hub. Fail the build on CRITICAL vulnerabilities; warn on HIGH. Mirror what the Indemn org does for `bot-service`'s `docker-image-scanning.yml` — copy that workflow.

### Day-2 ongoing-ops runbook (must ship as `docs/runbook.md`)

A separate document with the most common operational scenarios. At minimum, these playbooks:
- "Automation_status: failed" triage — how to inspect, classify (agency missing / extraction failure / Unisoft API error), reset, and re-process
- "Re-process a single email" — `gic emails reset --id ...` then let the cron pick it up
- "Skill prompt change" — edit `.md`, run tests, push to `main`, CI deploys
- "Add a new LOB → Unisoft GroupId mapping" — config change in Parameter Store + redeploy
- "LLM provider failover" — flip `LLM_PROVIDER` in Parameter Store, redeploy (no code change)
- "Unisoft proxy down" — see Unisoft SPOF section
- "Atlas connection-pool exhausted" — scale tier, restart consumer that's leaking
- "Stale-claim recovery flagged an email" — manual reconciliation procedure for `automation_status: failed_recovery_review`:
  1. List the affected emails: `mongosh ... --eval 'db.emails.find({automation_status:"failed_recovery_review"}, {_id:1, "subject":1, "named_insured":1, "automation_started_at":1}).pretty()'`
  2. For each, search Mongo for a recent Quote matching the named insured: `gic submissions check-duplicate --name "..." --compact` (matches against existing submissions with `unisoft_quote_id`).
  3. If a duplicate is found from the orphaned attempt: write that quote_id back via `gic emails complete <EMAIL_ID> --quote-id N --notes "manual reconciliation 2026-XX-XX"` (note: `email_id` is positional, not `--id`). Sets `automation_status: complete`.
  4. If no duplicate exists (the crash happened before SetQuote): `gic emails reset <EMAIL_ID>` (positional, no flag). Default behavior resets `automation_status` to null; email goes back to the queue and the next automation tick picks it up.
  5. Document each manual reconciliation in a new `manual_reconciliations` Mongo collection (created lazily on first write — `db.manual_reconciliations.insertOne({...})`); fields: `email_id`, `reconciled_at`, `reconciled_by`, `outcome` (`linked_existing` / `requeued` / `closed_no_action`), `notes`.
- Datadog alert on `failed_recovery_review` count > 0 ensures these never sit unreviewed.

## Cutover Runbook

### Roles and pre-flight

- **Cutover lead:** Craig
- **Backup lead:** Dhruv (must be on call during the cutover window with the same access — Indemn AWS, Atlas, Railway, the GIC Vercel/Amplify accounts; brief him with the runbook + Slack thread before T-1)
- **Customer comms owner:** Craig (one email to JC + Maribel at T-24h, one at T+0 start, one at T+0 done)
- **Maximum cutover window:** 90 minutes from "Pause Railway prod" to "EC2 prod fully unpaused + verified." If the window blows past 90 minutes without verified end-to-end success, **abort and roll back** rather than push through. Better to do a second clean attempt than leave the system half-migrated under time pressure.
- **Go/no-go gate:** all pre-cutover steps 1–11 must be green and signed off (in the Slack thread) before the cutover window starts. Any pre-cutover failure (Atlas connection-pool over budget, EC2 dev soak shows a regression, add-in rebuild needed but not done) postpones cutover.

### Pre-cutover (T-7 to T-1 days)

1. Initial commit lands in `indemn-ai/gic-email-intelligence` — cleanup pass + Phase 1.0 code work (`--loop`, `PAUSE_SYNC`, stale-claim recovery, `/healthz`, env-var-ization) + CI/CD scaffold + docker-compose.
2. AWS Secrets Manager + Parameter Store populated for both dev and prod. **Audit and screenshot all current Railway prod env vars side-by-side with the new Secrets Manager layout** to catch any value that's been mutated in Railway's UI but never made it back to documentation.
3. EIPs `44.196.55.84` and `98.88.11.14` added to Atlas allowlist on `dev-indemn` project. SG-reference rule added to `sg-04cc0ee7a09c15ffb` (ports 5000/5001) for dev-services and prod-services SGs. Verify connectivity from each EC2: `curl -v http://172.31.23.146:5001/api/health` should succeed before proceeding.
4. Verify Atlas connection-limit headroom — at peak overlap (Railway prod + EC2 prod both connected), check we're below the cluster connection cap. M-tier permitting.
5. GitHub Actions self-hosted runners verified on dev-services and prod-services with `dev` / `prod` labels — both online and idle: `gh api repos/indemn-ai/gic-email-intelligence/actions/runners --jq '.runners[] | select(.status=="online") | {name, labels: [.labels[].name], busy}'`. Smoke-test by queueing a no-op build to the dev runner; confirm it completes in <2 min. OIDC role policy confirmed to read `indemn/{env}/gic-email-intelligence/*`.
6. First successful build → push → deploy to dev-services. EC2 dev stack comes up with `PAUSE_PROCESSING=true`, `PAUSE_AUTOMATION=true`, `PAUSE_SYNC=true` initially. API runs live; crons fire-and-exit.
7. Pause Railway dev sync first (`PAUSE_SYNC=true` on Railway dev). Wait at least one full sync interval (5 min) for any in-flight Railway tick to drain. Then unpause sync on dev EC2. Verify token advance:
   ```
   mongosh ... --eval 'db.sync_state.findOne({_id:"outlook_sync"})'
   # Expected: last_sync_at advances on every tick; no two consecutive identical values
   db.emails.aggregate([{$match:{received_at:{$gte:ISODate("...")}}},{$group:{_id:"$graph_message_id",n:{$sum:1}}},{$match:{n:{$gt:1}}}])
   # Expected: empty result (no duplicate graph_message_id within window)
   ```
   Soak 24h. Pass criterion: token advanced ≥ 250 times, zero duplicate graph_message_ids.
8. Unpause processing on dev EC2. Verify processing produces same outputs as Railway dev did, and that `PAUSE_PROCESSING` honors actually fire on Railway. Check:
   ```
   db.emails.aggregate([{$match:{processing_status:{$in:["complete","failed"]}}},{$group:{_id:"$processing_status",n:{$sum:1}}}])
   # Expected: pre/post-cutover ratios match within ±5%
   ```
   Pass criterion: backlog (`processing_status: pending`) trends to zero, no stuck `processing_status: processing` past 5 min.
9. Unpause automation on dev EC2 (against UAT Unisoft). Trigger a known-good test email; verify Quote/Task/Activity creation end-to-end. Pass criterion: at least 3 emails complete with `automation_status: complete` and a populated `unisoft_quote_id` within 30 min of arrival, and the corresponding Quotes are visible in UAT Unisoft with attachments + activity + email notification.
10. Amplify dev branch pointed at `indemn-ai/gic-email-intelligence` and rebuilt with `VITE_API_BASE` set to the dev EC2 API. UI smoke-tested: log in, see board, click into a recent submission, confirm AMS data renders, confirm WebSocket reconnects.
11. **Verify Outlook add-in's `VITE_API_BASE` (Vercel build env) targets the canonical hostname (`api.gic.indemn.ai`), not a Railway-specific domain.** If not, rebuild the add-in on Vercel against the canonical host *before* prod cutover (manifest re-issue may be required, coordinate with Maribel). If yes, no rebuild is needed since the host name doesn't change — only what it resolves to.
12. **Customer comms (T-24h):** Email to JC + Maribel: cutover window, expected zero downtime, what to look for, Craig's phone for issues. Confirm receipt before proceeding.
13. **Pre-cutover snapshot:** trigger an Atlas on-demand backup snapshot of the `gic_email_intelligence` database. Note the snapshot ID in the runbook log. This is the rollback floor for any data-corruption scenario.

### Cutover window (T-0)

Target: a low-traffic window (early morning before agents start sending submissions). Estimated 30–60 minutes hands-on, hard-stop at 90 minutes (see roles section). 24–48h watchful soak after.

**Step 0 — Customer comms.** Single line to JC + Maribel: "Migration starting now. Expected duration ~1 hour, no downtime. Will follow up when complete." Post in the joint Slack thread.

1. **Pause Railway prod**:
   - Set `PAUSE_PROCESSING=true` and `PAUSE_AUTOMATION=true` on Railway prod processing + automation services
   - Set `PAUSE_SYNC=true` on Railway prod sync (add this env var if missing — likely needs a tiny code change in sync loop to honor it)
   - Verify Railway crons fire and exit immediately (logs)
2. **Promote prod EC2 stack**:
   - Push to `prod` branch → CI/CD runs build-prod.yml → image deploys to prod-services
   - Containers start with all crons paused (initial deploy default)
   - Verify health: `curl https://api.gic.indemn.ai/api/health`, `docker compose ps`
3. **Cutover DNS for the API**:
   - Update Route 53 `api.gic.indemn.ai` from Railway public domain (`api-production-e399.up.railway.app`) to ALB on prod-services (or whichever ingress pattern fits the existing setup)
   - TTL set to 60s ahead of time so propagation is fast
4. **Cutover Amplify prod branch**:
   - Already pointed at `indemn-ai/gic-email-intelligence` from pre-cutover
   - Manually trigger a build to ensure latest code, including new `VITE_API_BASE`
5. **Unpause EC2 prod crons** (one at a time, with 5-minute soak between each):
   - sync-cron first (lowest risk — only writes to Mongo)
   - processing-cron next (writes derived data, no external side effects)
   - automation-cron last (writes to Unisoft prod — full external side effect)
6. **Verify a real cycle end-to-end** — defined success criterion:
   - At least one inbound `agent_submission` email arrives within the cutover window (or use a controlled test email if traffic is quiet — coordinate with JC's office)
   - That email reaches `processing_status: complete` within 5 minutes of arrival (Mongo: `db.emails.findOne({graph_message_id:"..."}, {processing_status:1, processing_completed_at:1})`)
   - That email reaches `automation_status: complete` with a populated `unisoft_quote_id` within 30 minutes of arrival
   - In Unisoft prod UI: Quote exists with the right LOB and agency, attachments are present, an "Application Acknowledgement" activity is logged, and the recipient agent confirms receipt of the notification email
   - Datadog dashboard: container healthy, no error spike on the new EC2 services in the past 30 min
   If any of these fail and the 90-minute window is approaching, abort and roll back rather than push through.
7. **Update Atlas allowlist + Unisoft SG**:
   - Remove Railway `162.220.234.15` (only after step 6 passes)
8. **Customer comms (T+0 done).** Single line to JC + Maribel: "Migration complete. System running on new infrastructure. Please flag anything that looks off."

### Post-cutover (T+1 to T+7 days)

- 24h watchful soak with Craig + monitoring session active on Railway logs (still up but paused) and EC2 logs simultaneously.
- If anything goes wrong, in this order:
  1. **Pause EC2 API + crons first** — let in-flight requests drain (≤10s)
  2. Flip Route 53 back to Railway public domain (TTL is 60s)
  3. Re-enable Railway crons (un-pause all)
  4. Investigate without time pressure
  Pausing EC2 first prevents the rollback window from being a "both stacks are alive and competing for the connection pool" period — Atlas connection limits become a real concern otherwise.
- Once 7-day soak is clean: destroy Railway services (`railway down -s api`, etc.). Project itself can stay around for a beat as a record; ultimately archive.

### Tear-down

1. Railway services destroyed (api, sync, agent, automation, both dev + prod environments).
2. Railway project archived.
3. craig-indemn/gic-email-intelligence repo set to read-only / archived. Add a README pointing at the new home.
4. Atlas allowlist Railway IP removed.
5. Unisoft proxy SG Railway IP removed.

## Phase 2 Sketch: Database Migration

(Not in scope for this design; sketched here for continuity.)

1. Create new `prod-indemn` Atlas cluster (or use existing if present) with `gic_email_intelligence` database.
2. Set up Atlas Live Migration from `dev-indemn` → `prod-indemn` for the `gic_email_intelligence` database only.
3. Soak read replication for several days. Verify counts match.
4. Coordinate brief read-only window: pause all crons, switch `MONGODB_URI` env in Secrets Manager, redeploy, unpause.
5. Rename memory: `project_gic_infrastructure.md` updated to reflect new posture.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Double-processing during cutover overlap** | Atomic Mongo claim semantics in `gic emails next`. Pause Railway crons before unpausing EC2 crons. Verify the claim lock works as expected before going live (low-risk test in dev). |
| **Sync token desync** between Railway and EC2 | Only one of the two should run sync at a time. Railway sync is paused before EC2 sync starts. The `sync_state` doc tracks the last-since token; both writers would conflict. |
| **EIP / public-IP confusion** | Verify dev-services and prod-services have EIPs attached, not ephemeral public IPs that change on instance stop/start. Document the egress IPs in the runbook. |
| **Unisoft proxy SG misconfiguration** | Test connectivity from each EC2 to `172.31.23.146:5000` and `:5001` *before* cutover. `curl -v http://172.31.23.146:5001/api/health` from the EC2. |
| **Amplify rebuild fails on rewire** | Test rewire on dev branch first. Custom domain `gic.indemn.ai` keeps pointing at the same Amplify app — DNS doesn't change. |
| **CORS regression** | Switching to env-driven CORS introduces a new failure mode (forgotten origin). Cover with a startup-time log line of the origin list, plus a smoke test that hits the API from the UI in dev. |
| **Healthcheck against `/api/health`** that depends on Mongo/Unisoft | If these dependencies are down, healthcheck fails and Docker restarts the container. Add a `/healthz` that's purely process-alive (no DB call) for healthchecks; keep `/api/health` for monitoring. |
| **Self-hosted runner not present / not labeled** | Verify `dev` and `prod` labels on the runners on dev-services / prod-services before pushing the first build. |
| **`shared-datadog` external network missing** | Existing services on the host already use it; confirm before bringing up. |
| **LLM provider auth mismatch** | Provision both Anthropic and Vertex secrets ahead of cutover; verify both work via a CLI smoke test (`gic test llm --provider anthropic` and `--provider google_vertexai`) on dev EC2. |
| **Outlook add-in `VITE_API_BASE` baked at build** | If the add-in's Vercel env is set to a Railway-specific hostname, it'll 502 once Railway is destroyed. Mitigation: pre-cutover step 11 verifies (and rebuilds if needed) that the add-in points at the canonical `api.gic.indemn.ai` host. |
| **Sync state non-atomic** | `sync_state.last_sync_at` is read-then-write, not atomic. Two sync processes can clobber the token and cause duplicate or missed emails. **CRITICAL:** Always pause Railway sync first, wait one full sync interval (300s) for any in-flight tick to drain, *then* unpause EC2 sync. Reverse order = silent email duplication. No exceptions. |
| **Orphaned `automation_status: processing`** | Without recovery, a crashed automation cron leaves emails permanently un-processable (the `next` query filters for unset/null `automation_status`, so `processing` is never re-claimed). Mitigation: stale-claim recovery added in Phase 1.0 (item 3 in pre-cutover code work). |
| **Atlas connection-pool exhaustion during overlap** | Railway prod + EC2 prod both connected ≈ 2x base connection count. Mitigation: verify cluster tier supports the peak count pre-cutover. On rollback, pause EC2 *first* so the overlap window stays brief. |
| **Unisoft proxy SG missing VPC rule** | Verified 2026-04-27: `sg-04cc0ee7a09c15ffb` only allows specific public IPs, no VPC CIDR or SG-reference rule. EC2-to-proxy traffic will fail without an SG update. Mitigation: pre-cutover step 3 adds SG-reference rule from dev-services / prod-services SGs to ports 5000/5001. |
| **SIGTERM mid-tick corrupts state** | A `docker stop` mid-`SetQuote` could leave Unisoft with a Quote but Mongo with `automation_status=processing`. Mitigation: SIGTERM handler in loop wrapper finishes the current tick before exit (Phase 1.0 item 1). For ticks that exceed Docker's stop-grace-period (default 10s, increase to 60s in compose), the stale-claim recovery + duplicate-check is the second line of defense. |
| **Stale-recovery creates duplicate Quote** | If automation crashes after `SetQuote` but before `gic emails complete`, naive recovery would re-run and create a duplicate Quote in Unisoft. Mitigation: Phase 1.0 item 3 — pre-recovery duplicate check; ambiguous cases route to `failed_recovery_review` for human review, not auto-reset. |
| **Skill prompt out of sync with env** | Env-var-izing `GRAPH_USER_EMAIL` in code while leaving `quote@gicunderwriters.com` hardcoded in `email_classifier.md` would cause the LLM to assert the wrong inbox. Mitigation: Phase 1.0 item 5 includes both the code change AND the `.md` placeholder substitution at skill load time. |
| **CORS regression from stray whitespace in env** | `https://gic.indemn.ai, https://dev.gic.indemn.ai` (with the leading space) silently fails CORS matching. Mitigation: Phase 1.0 item 6 — Pydantic validator strips whitespace; startup log echoes the parsed list. |
| **Hidden state in Railway env vars** | A Railway env value mutated via the dashboard but never reflected back to documentation could be lost on cutover. Mitigation: screenshot full Railway prod env-var panel during pre-cutover audit; diff against the Secrets Manager layout. |
| **Production data on dev Atlas** continues being awkward | Acceptable risk for Phase 1; documented as Phase 2's main objective. |

## Out of Scope (post-cutover follow-ups)

These are documented to make sure they aren't dropped, not to be done now:

1. **Atlas relocation (Phase 2)** — own design pass, own cutover.
2. **Outlook add-in to Amplify** under `addin.gic.indemn.ai` — coordinate manifest re-sideload with Maribel.
3. **Skill prompt registry** — pull `.md` skill files into a versioned, traceable prompt management layer (LangSmith Prompts? Custom?).
4. **Deepagents `LocalShellBackend` stdin patch** — upstream PR or fork to remove the monkey-patch in `automation/agent.py`.
5. **LangSmith tracing fix** — zero traces appearing currently; env vars set, callback built. Carry-forward.
6. **Multi-tenancy refactor** — only when a second customer is real.
7. **Repo rename to `email-intelligence`** — only as part of (6).
8. **Production Atlas cluster posture review** — IAM roles, backup retention, alerting, audit logs.
9. **Datadog APM (ddtrace)** for the GIC services — bot-service has it; we don't yet.
10. **Dependency / image vulnerability scanning** beyond Dependabot — Trivy / Snyk for container images.
11. **Private container registry (ECR) as fallback for Docker Hub.** Phase 1 uses Docker Hub; if rate-limits or outages become a real issue at GIC volume, evaluate ECR. Not urgent.
12. **Unisoft proxy HA** — second instance with health-check failover, removing the single-point-of-failure risk that's been explicitly accepted for Phase 1.

## Open Items to Confirm During Implementation

**Resolved by 2026-04-27 review:**
- ~~EIPs attached to dev-services / prod-services?~~ Yes — `44.196.55.84` and `98.88.11.14`, both with allocation IDs.
- ~~Unisoft proxy SG already allows VPC traffic?~~ No — only specific public IPs today. Pre-cutover step 3 adds an SG-reference rule.
- ~~Atomic claim semantics in `gic emails next`?~~ Yes, verified — `find_one_and_update` with status filter, server-side atomic.
- ~~`PAUSE_PROCESSING` actually enforced?~~ Yes, verified at `harness.py:445-446`.

**Still open, to confirm during implementation:**
- Does the existing internal ALB / Caddy / nginx on dev-services + prod-services have a listener pattern we plug into, or do we add a new listener rule? Confirm by SSM-execing onto the host: `docker ps`, `ps aux | grep -i caddy\|nginx`. The two most likely shapes are (a) a host-level reverse proxy that maps hostnames to container ports, (b) ECR/ALB. Adapt the docker-compose `expose` vs `ports` accordingly.
- Does GitHub OIDC role `github-actions-deploy` need a policy update to include `indemn/{env}/gic-email-intelligence/*` permissions? Almost certainly yes; existing roles scope to existing services. Cheap fix.
- Is the current Atlas tier connection-pool large enough for the dev + prod overlap during cutover? Confirm by checking the cluster's connection metric vs the tier's `connectionLimit` before pausing Railway.
- Does the Outlook add-in's `VITE_API_BASE` (set as a Vercel build env) currently target `api.gic.indemn.ai` or a Railway-specific URL? Pre-cutover step 11 verifies; rebuild only if Railway-specific.
