---
ask: "Insurica's Reception agent — Volume / Flow / Outcomes / Reports tabs all show 'No data' but Usage tab works. Jonathan reported in #dev-squad."
created: 2026-04-27
workstream: observatory
session: 2026-04-27-a
sources:
  - type: slack
    description: "Jonathan's bug report in #dev-squad parent thread 1777060307.862239"
  - type: mongodb
    description: "Diagnosis queries against tiledesk.requests, tiledesk.observatory_conversations, tiledesk.daily_snapshots, tiledesk.processing_runs"
  - type: aws
    description: "EC2 i-0df529ca541a38f3d (copilot-prod), Lambda observatory-ingestion-pipeline, Step Functions observatory-ingestion-pipeline, Secrets Manager indemn/prod/shared/google-cloud-sa"
  - type: github
    description: "indemn-ai/Indemn-observatory PRs #19 (historical), #72 + #73 (today)"
  - type: linear
    description: "DEVOPS-148 + 4 children, COP-507 + 2 children"
---

# Observatory Voice Ingestion Fix + Vertex Gemini Swap

## TL;DR

Two distinct bugs surfaced via Jonathan's screenshot, both fixed today:

1. **Voice ingestion never deployed to prod.** PR #19 (March 6) added Langfuse trace sync for voice agents — the source code change landed, dev infra was updated, but the prod Lambda + Step Functions state machine never got promoted. Voice agents accumulated ~120 traces of activity since 2026-03-09 with zero observatory_conversations written.
2. **Anthropic API credit balance hit zero in April.** Classifier silently caught the credit-exhausted exception and wrote default fallback values (`outcome_group=unknown`, `sentiment=neutral`, `intent=informational`) for ~950 chat conversations, polluting the Volume / Outcomes data quality.

Both were customer-impacting (Insurica + every other voice agent customer; April chat data quality system-wide). Both fully resolved end-to-end today.

## Diagnosis path

Worth preserving because we went down two wrong paths first:

1. **First wrong path: queried the `observatory` MongoDB database.** It existed, had stale data from late December 2025. Concluded "ingestion is dead since Dec." Wrong — that was a legacy DB. Live data is in `tiledesk.observatory_conversations`. The deployed observatory-api connects to the `tiledesk` DB; the `observatory` DB is leftover from a prior architecture.

2. **Second wrong path: chased the `processing.classification_version` field as a discriminator for fallback records.** The field gets stamped at obs-doc-build time from current LLM_PROVIDER config — not from the actual classifier that produced THIS record's classification values. So after switching to Gemini, the field on April records said `google:gemini-2.5-flash` even though the values were old Anthropic fallbacks. The reliable discriminator is the all-default value pattern itself, not the version stamp.

3. **Right path:** trace the actual data flow. Voice ingestion: `Langfuse → traces collection (joined to tiledesk.requests by request_id) → observatory_conversations`. Gap: `traces` collection had no langfuse-source records after 2026-03-09. Ran the Step Functions describe — prod state machine had no Langfuse branch at all. Lambda last modified 2026-01-30 — pre-voice-ingestion code. The "prod was never updated" hypothesis fit all the data.

## What was deployed today

### 1. Lambda update (DEVOPS-149)
- Pushed current source of `lambda/ingestion_pipeline/lambda_function.py` (which is actually the action-dispatcher code from `step_handler.py`, renamed at zip time per the deploy convention)
- Lambda `observatory-ingestion-pipeline` LastModified: 2026-04-27 18:48:59 UTC
- Action-dispatcher now handles `start_sync_langfuse_traces` alongside `start_sync_traces`
- Backup of pre-deploy zip: `/tmp/lambda_backup/observatory-ingestion-pipeline.prod.20260427.zip` on dev machine

### 2. Step Functions state machine update (DEVOPS-150)
- Replaced prod `observatory-ingestion-pipeline` definition with the dev definition
- Adds the parallel `SyncAllTracesWithDates` / `SyncAllTracesNoDates` blocks containing both `StartSyncTraces*` (Langsmith chat) and `StartSyncLangfuseTraces*` (Langfuse voice) branches
- Backup: `/tmp/sfn_backup/observatory-ingestion-pipeline.prod.20260427.json`
- Smoke-test execution `smoketest-2026-04-15-185043` succeeded end-to-end

### 3. Vertex Gemini swap (COP-507/508)
- `/opt/observatory/.env.aws` on copilot-prod EC2: added `LLM_PROVIDER=google`, `LLM_MODEL=gemini-2.5-flash`, `GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_APPLICATION_CREDENTIALS=/etc/gcp-sa.json`, `GOOGLE_CLOUD_PROJECT=prod-gemini-470505`, `GOOGLE_CLOUD_LOCATION=us-central1`. Backup: `.env.aws.bak-vertex-20260427-172725`.
- `/opt/observatory/docker-compose.yml`: added `volumes: - ./secrets/gcp-sa.json:/etc/gcp-sa.json:ro` to the observatory-api service. Backup: `docker-compose.yml.bak-vertex-20260427-172725`.
- `/opt/observatory/secrets/gcp-sa.json`: provisioned from AWS Secrets Manager `indemn/prod/shared/google-cloud-sa` (SA `indemn-gemini-service-account@prod-gemini-470505.iam.gserviceaccount.com`, project `prod-gemini-470505`)
- No application code change — `model_utils.py`'s `google` provider branch already handled Vertex when `GOOGLE_GENAI_USE_VERTEXAI=true` is set
- Source PR: indemn-ai/Indemn-observatory#72 (Rudra + Dhruv requested)

### 4. Backfills

**Voice trace sync (COP-505)** — `force=true` against the langfuse-sync admin endpoint, 4 windows:
- 2026-03-10 → 2026-03-31: 0 traces (Langfuse genuinely empty — voice-livekit instrumentation gap, upstream issue)
- 2026-04-01 → 2026-04-14: 1,389 runs synced
- 2026-04-15: 332 runs (smoke-test window)
- 2026-04-16 → 2026-04-27: 11,056 runs synced
- Total: 12,777 voice runs added to `tiledesk.traces` collection

**Voice ingest** — `/api/admin/ingest 2026-03-10 → 2026-04-27` with `reuse_classifications=true`. Result: **120 voice obs convos written** across 12 distinct agents (Ronnie2 46, Renewals Demo VOICE 29, Petra 15, Riley Front Door 11, Renewals Voice 7, Celine FNOL 4, plus 6 others).

**April chat fallback re-classification (COP-509)** — sample test on 2026-04-09 confirmed 7/10 fallback records changed when re-classified by Gemini (3/10 stayed default = legitimately ambiguous). Then:
- Deleted 943 April records matching the all-default fallback signature (out of 950, minus 10 used in sample)
- Re-ingested 2026-04-01 → 2026-04-13 (2,155/2,241 processed) and 2026-04-14 → 2026-04-27 (2,412/2,632 processed)
- All-default count dropped from 950 → 334 (the 334 are records Gemini also classified as ambiguous; legitimate)
- 616 April records went from "unknown fallback" to real outcomes: 1,019 success, 987 failure, 103 partial, 42 pending, 995 truly unknown, 1,421 excluded

### 5. Source code cleanup (PR #73)
- Deleted legacy `lambda_function.py` (single-pass, unused)
- Renamed `step_handler.py` → `lambda_function.py` (matches deploy convention)
- Eliminates the file-collision foot-gun that caused a wasted deploy attempt today

## Operational issues observed (not yet resolved)

- **Container restart mid-ingest, twice.** RestartCount went from 0 → 2 over today's heavy ingest runs. ExitCode=0 (graceful), no OOM (148 MiB / 4 GiB usage), no kernel OOM kill, no docker events for the restart in the window. Origin unidentified. Smaller ingest windows (~14 days) completed cleanly; full 49-day window got interrupted both times. Worth investigating but didn't affect outcome — `reuse_classifications=true` made resumption cheap.
- **The 419 Jan–Mar Anthropic+all-default records** are pre-credit-failure; haven't decided whether to backfill those. Spot test would tell us if they're fallbacks or legit.

## Linear

- DEVOPS-148 (parent, voice ingestion) → Acceptance with 4 children all in Acceptance
- COP-507 (parent, Anthropic→Gemini) → Acceptance with 2 children in Acceptance, 1 (COP-509 April backfill) in Acceptance
- COP-506 (rate limiter) — Queued, intentionally deferred (current 0.8 RPS is fine for what we've done)

## Slack thread

Posted reply in `#dev-squad` thread `1777060307.862239` at 2026-04-27 21:16 UTC: confirmed fix to Jonathan and asked him to verify.
