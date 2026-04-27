---
ask: "Capture the Phase E execution session outcomes — what shipped, what was discovered, what's blocked, and exactly what the next session needs to know to resume cleanly at Phase F."
created: 2026-04-27
workstream: gic-email-intelligence
session: 2026-04-27-c
sources:
  - type: codebase
    description: "1 new commit on /Users/home/Repositories/gic-email-intelligence-migration:migration/indemn-infra (daf216e — env-loader patch)"
  - type: aws
    description: "Secrets Manager + Parameter Store dev-side population, Unisoft proxy SG ingress add, IAM read-only verification, dev-services SSM-driven verification"
  - type: linear
    description: "DEVOPS-151 → In Progress, DEVOPS-153 → Done, DEVOPS-159 created + assigned to Dhruv"
---

# GIC → Indemn Migration — Phase E Execution Handoff

**Status:** Phase E (DEVOPS-153) **Done** — 5 of 6 sub-steps executed in this session (E.1–E.5), E.6 handed off to Dhruv via DEVOPS-159 due to repo-admin permission gap. Branch `migration/indemn-infra` in worktree `/Users/home/Repositories/gic-email-intelligence-migration` is now **33 commits ahead of `origin/main`** (was 32; added `daf216e` env-loader patch). Working tree clean. 113 unit tests pass (1 pre-existing failure carried forward, predates session).

**Next session starts at:** Phase F (DEVOPS-154) — push to `indemn-ai/gic-email-intelligence`. **F is partially blocked** on DEVOPS-159: F.1 (push) we can do (we have push permission), F.2 (branch protection) needs admin we don't have. F.3 (Amplify rewire) requires the push to be live first.

## What shipped this session

### Phase E.1 — Secrets Manager (dev): 6 secrets live

After redundancy cleanup against `shared/*`, the final dev layout under `indemn/dev/gic-email-intelligence/*` is:

| Secret | Source | Notes |
|---|---|---|
| `mongodb-uri` | Railway dev `MONGODB_URI` (modified — see E.3) | DIFFERENT from `shared/mongodb-uri` (different DB user) |
| `graph-credentials` | Railway dev (4 fields → JSON bundle) | tenant_id, client_id, client_secret, user_email |
| `google-cloud-sa-json` | Railway dev `GOOGLE_SA_JSON` | DIFFERENT from `shared/google-cloud-sa` (different GCP project) |
| `anthropic-api-key` | Railway dev `ANTHROPIC_API_KEY` | DIFFERENT from `shared/anthropic-api-key` (different account) |
| `tiledesk-db-uri` | Railway dev `TILEDESK_DB_URI` | GIC-only — no shared equivalent |
| `unisoft-api-key` | Railway dev `UNISOFT_API_KEY` | flat, NOT JSON bundle — Railway has no username/password/broker_id values |

Deleted as redundant (shared/* values matched exactly via SHA256):
- `indemn/dev/gic-email-intelligence/jwt-secret` → loader uses `shared/auth-secrets.jwt_secret`
- `indemn/dev/gic-email-intelligence/langsmith-api-key` → loader uses `shared/langsmith-api-key`

Skipped per code analysis:
- `api-token` (design slot) — JWT_SECRET handles all prod auth; the api_token fallback path is never exercised. `API_TOKEN` was genuinely absent from Railway prod (verified via `jq has("API_TOKEN")` → false). System works because `api/main.py:30-31` warns only if BOTH JWT_SECRET and API_TOKEN are missing.
- `LLM_API_KEY` (Railway dev value) — dead config. `agent/llm.py:24-44` shows `api_key` is only used for `provider == "anthropic"` or `"openai"`. With `LLM_PROVIDER=google_vertexai`, Vertex auth is exclusively via `ensure_google_credentials()` reading `GOOGLE_SA_JSON`. The Railway value is set but ignored.

### Phase E.2 — Parameter Store (dev): 22 entries live

Path: `/indemn/dev/gic-email-intelligence/*` (with leading slash — Parameter Store convention).

| Param | Value | Notes |
|---|---|---|
| `llm-provider` | `google_vertexai` | overrides shared which is `anthropic` |
| `llm-model` | `gemini-2.5-pro` | |
| `llm-model-fast` | `gemini-2.5-flash` | new in Phase 1.0 |
| `pipeline-stages` | `extract,classify,link` | from Railway dev |
| `pause-sync` | `true` | INITIAL state — Phase G.2 unpauses one at a time |
| `pause-processing` | `true` | INITIAL state |
| `pause-automation` | `true` | INITIAL state |
| `unisoft-proxy-url` | `http://172.31.23.146:5000` | dev = UAT proxy port (private IP) |
| `unisoft-activity-action-id` | `6` | UAT |
| `unisoft-task-action-id` | `40` | UAT custom |
| `unisoft-task-group-id-newbiz` | `2` | UAT |
| `unisoft-task-group-id-wc` | `4` | UAT |
| `s3-bucket` | `indemn-gic-attachments` | |
| `aws-region` | `us-east-1` | |
| `cors-origins` | 7-URL list (gic.indemn.ai, dev.gic.indemn.ai, gic-addin.vercel.app, main.d244t76u9ej8m0.amplifyapp.com, localhost:5173, localhost:3000) | **VERIFY before Phase G deploy** against original `api/main.py:54-61` hardcoded list |
| `public-base-url` | `https://api-dev.gic.indemn.ai` | |
| `gic-org-id` | `65eb3f19e5e6de0013fda310` | |
| `graph-user-email` | `quote@gicunderwriters.com` | |
| `google-cloud-project` | `prod-gemini-470505` | Vertex project |
| `google-cloud-location` | `us-central1` | |
| `langchain-project` | `gic-email-processing` | from Railway dev (preserves trace continuity) |
| `langchain-tracing-v2` | `true` | from Railway dev |

### Phase E.2 also: env-loader patch (commit `daf216e`)

Discovered during loader smoke-test that the original `scripts/aws-env-loader.sh` from Phase D.2:
1. Used recursive `/indemn/{env}/` query — picked up unrelated services' params (e.g. `services/observability/cors-origins`)
2. Hard-coded `shared/*` paths for mongodb-uri and anthropic-api-key — but GIC has DIFFERENT values for those
3. Didn't load google-cloud-sa-json or tiledesk-db-uri at all
4. Expected `unisoft-credentials` JSON bundle — but Railway only has flat api_key

**Patch (`daf216e`):**
- `get_secret()` adds `|| true` — missing secrets log WARN instead of aborting under `set -e`
- Adds GIC override entries: `mongodb-uri`, `anthropic-api-key`, `google-cloud-sa-json`, `tiledesk-db-uri`, `unisoft-api-key` (flat) — applied after shared/* so GIC values win
- Parameter Store: replaced single recursive `/indemn/{env}/` query with two scoped queries (`/indemn/{env}/shared/` then `/indemn/{env}/{service}/`), concatenated so service-specific applies last per env_file last-value-wins

Verified end-to-end: `AWS_ENV=dev AWS_SERVICE=gic-email-intelligence bash scripts/aws-env-loader.sh /tmp/check.env` → exit 0, 90 vars written, GIC values winning on every overlap (LLM_PROVIDER=google_vertexai, GIC CORS list, etc.).

### Phase E.3 — Atlas allowlist: NOT added (PrivateLink swap instead)

**Pivotal discovery.** The original plan was to add public CIDRs `44.196.55.84/32` (dev-services EIP) and `98.88.11.14/32` (prod-services EIP) to the dev-indemn Atlas allowlist. While verifying connectivity, found that:

- `shared/mongodb-uri` host: `dev-indemn-pl-0.mifra5.mongodb.net` (PrivateLink endpoint)
- `gic-email-intelligence/mongodb-uri` (my E.1) host: `dev-indemn.mifra5.mongodb.net` (public endpoint)

dev-services already reaches Atlas via VPC PrivateLink endpoint `vpce-06c18b903fea23e06` (private IP 172.31.32.102, allows VPC CIDR 172.31.0.0/16 inbound on ports 1024-1026 + 27017). **The right fix was to switch GIC's URI to use the PrivateLink hostname**, not add public IPs to the allowlist.

**Executed:** updated `indemn/dev/gic-email-intelligence/mongodb-uri`, substituted host only (`dev-indemn` → `dev-indemn-pl-0`). Verified from dev-services via SSM `docker run mongo:6 mongosh ... --eval 'db.runCommand({ping:1})'` → `{ok: 1, ...}`.

**Implications for downstream:**
- Phase I.3 (prod Atlas allowlist) is similarly unnecessary — prod-services is in same VPC, same SG-allowed CIDR
- Phase I.2 (prod Secrets Manager population) MUST use PrivateLink hostname from the start
- Phase 2 (Atlas relocation to prod-indemn) — verify whether that cluster has its own PrivateLink endpoint before cutover

### Phase E.4 — Unisoft proxy SG: 1 SG-reference rule (covers both EC2s)

Verified handoff finding: dev-services (`172.31.43.40`) and prod-services (`172.31.22.7`) both attached to shared SG `sg-d4163da4`. Implementation plan called for 2 SG-reference rules (one per source SG); reality collapses to 1 since they share an SG.

**Pre-flight (read-only):**
- Confirmed sg-04cc0ee7a09c15ffb had only 3 public CIDRs per port (Railway 162.220.234.15, office 73.87.128.242, office 96.244.115.146), zero SG-references
- TCP from dev-services to 172.31.23.146:5000/5001 → BLOCK pre-change
- TCP from dev-services to 54.83.28.79:5000/5001 (public) → BLOCK (dev-services EIP not in public allowlist; only Railway + offices)

**Executed:**
- `aws ec2 authorize-security-group-ingress --group-id sg-04cc0ee7a09c15ffb --protocol tcp --port 5000 --source-group sg-d4163da4` → `sgr-0317a1e6a5f792415`
- Same for port 5001 → `sgr-0470a153b7c95a647`
- Existing 3 public-IP rules preserved (Railway + 2 office continue working through cutover; Railway 162.220.234.15 removed in Phase I.11)

**Post-change verification:** TCP from dev-services to 172.31.23.146:5000/5001 → **OPEN**.

### Phase E.5 — IAM OIDC role: dev unblocked, prod blocker confirmed

Role: `arn:aws:iam::780354157690:role/github-actions-deploy`

**Trust policy:** GitHub OIDC, sub claim `repo:indemn-ai/*:*` (wildcard) — covers `indemn-ai/gic-email-intelligence` once we push in Phase F.

**Inline policy `deploy-dev-only` (single inline policy; zero attached managed policies):**
- ✅ Allow on `indemn/dev/*` for SecretsManager + SSM Parameter Store — covers gic-email-intelligence + shared
- ✅ Allow ECR auth + push/pull on all repos in account
- ⚠️ **Explicit Deny on `indemn/prod/*`** for both SecretsManager and SSM. IAM explicit-Deny wins over Allow → **blocks Phase I prod deploy** as currently structured.

**Three options for Phase I (decide before I.4 — prod branch push):**
1. **Separate role** `github-actions-deploy-prod` with `indemn/prod/*` allow + trust scoped to prod branch only of specific repos. **Recommended** — preserves dev-only safety for other repos.
2. **Carve out the Deny** — modify `Resource` array on `DenyProdExplicitly` to exclude `indemn/prod/gic-email-intelligence/*`. Loses symmetric guarantee for that path.
3. **Remove the Deny entirely + tighten Allow scoping.** Biggest refactor, weakest safety story.

### Phase E.6 — Runner registration handed off to Dhruv (DEVOPS-159)

**Discovered:** the Indemn org's self-hosted runner pattern is **per-repo**, not org-level. dev-services has 14+ separate `actions-runner-<service>/` directories on the host, each a distinct daemon registered to one specific GitHub repo (verified via `.runner` config file: `gitHubUrl: https://github.com/indemn-ai/<service>`). Standard runner version: 2.334.0. Labels: `[self-hosted, linux, x64, dev]` on dev-services, `[..., prod]` on prod-services.

**Verified pattern across 7+ Indemn repos** (bot-service, evaluations, observatory, indemn-platform-v2, conversation-service, copilot-server, middleware-socket-service, email-channel-service): all use `runs-on: [self-hosted, linux, x64, {dev|prod}]`. Same label, but each repo has its own dedicated runner daemon on each EC2.

For `indemn-ai/gic-email-intelligence`, two new runners need to be registered:
- dev-services: directory `/home/ubuntu/actions-runner-gic-email-intelligence/`, name `ip-172-31-43-40-gic`, labels `self-hosted,linux,x64,dev`
- prod-services: directory `/home/ubuntu/actions-runner-gic-email-intelligence/`, name `ip-172-31-22-7-gic`, labels `self-hosted,linux,x64,prod`

**Why handed off:** registering a runner requires `POST /repos/{owner}/{repo}/actions/runners/registration-token`, which requires repo `admin` permission. `craig-indemn` has only `push/pull/triage` on `indemn-ai/gic-email-intelligence` (Dhruv created the empty repo and is sole admin). **DEVOPS-159 created and assigned to Dhruv** with full SSM-driven instructions, expected labels, version, and verification commands.

Same admin gap also blocks Phase F.2 (branch protection) — surfaced as a "while you're at it" side ask in DEVOPS-159: grant `craig-indemn` admin on the repo.

## Linear state at end of session

| ID | Title | Status | Notes |
|---|---|---|---|
| DEVOPS-151 | GIC Email Intelligence — migrate to Indemn infra | **In Progress** | Parent epic |
| DEVOPS-152 | Phase A–D (32 commits) | Done | Prior session |
| DEVOPS-153 | Phase E (AWS infra) | **Done** | This session |
| DEVOPS-154 | Phase F (push + branch protection + Amplify rewire) | Backlog | F.2 needs admin (see DEVOPS-159 side ask) |
| DEVOPS-155 | Phase G (dev deploy + 24h soak) | Backlog | Blocked on DEVOPS-159 runners |
| DEVOPS-156 | Phase H (ops readiness, parallel with G) | Backlog | |
| DEVOPS-157 | Phase I (prod cutover, 90-min window) | Backlog | Blocked on DEVOPS-159 runners + IAM Deny carve-out (3 options on file in DEVOPS-153 comments) |
| DEVOPS-158 | Phase J (7-day soak + tear-down) | Backlog | |
| DEVOPS-159 | **Self-hosted runner registration** | Backlog | **Assigned to Dhruv** — full instructions in description |

## AWS state changes (auditable summary)

| Change | Resource | Effect |
|---|---|---|
| Created (E.1) | 8 secrets in `indemn/dev/gic-email-intelligence/*` | populated from Railway dev values |
| Deleted (E.2 cleanup) | 2 redundant secrets (`langsmith-api-key`, `jwt-secret`) | shared/* has matching values |
| Updated (E.3) | `indemn/dev/gic-email-intelligence/mongodb-uri` | host swap to PrivateLink endpoint |
| Created (E.2) | 22 params at `/indemn/dev/gic-email-intelligence/*` | non-secret config |
| Created (E.4) | `sgr-0317a1e6a5f792415` ingress on sg-04cc0ee7a09c15ffb tcp/5000 from sg-d4163da4 | allows dev+prod-services into Unisoft proxy 5000 |
| Created (E.4) | `sgr-0470a153b7c95a647` ingress on sg-04cc0ee7a09c15ffb tcp/5001 from sg-d4163da4 | allows dev+prod-services into Unisoft proxy 5001 |
| Read-only inspections | IAM (E.5), VPC endpoints, Atlas TCP probes (E.3 verify), runner host inspection (E.6) | no state change |

**Zero touches to:** MongoDB data, Railway services, prod EC2 (only dev-services received SSM-exec read-only commands), production secrets paths (`indemn/prod/*`), DNS, Amplify.

## Doc updates needed (deferred — surface for next session)

These are real corrections to the migration design + plan that came out of execution. None block work; they keep docs honest.

| File | Section | Change |
|---|---|---|
| `2026-04-27-migration-implementation-plan.md` | E.3 / I.3 | Replace "add EIPs to Atlas allowlist" with "swap mongodb-uri host to PrivateLink (`dev-indemn-pl-0.mifra5.mongodb.net`)" |
| `2026-04-27-migration-implementation-plan.md` | E.4 | Note dev-services + prod-services share `sg-d4163da4` — single SG-reference rule per port covers both |
| `2026-04-27-migration-implementation-plan.md` | E.6 | Per-repo runner pattern (not org-level); two runners need separate registrations on each EC2; admin token required |
| `2026-04-27-migration-to-indemn-infrastructure-design.md` | 1.6 (Network plumbing) | Describe PrivateLink as canonical Atlas access path (via `vpce-06c18b903fea23e06`) — update from "EIPs added to Atlas allowlist" |
| `2026-04-27-migration-to-indemn-infrastructure-design.md` | Risks table | Close "EIP / public-IP confusion" risk — not relevant under PrivateLink |
| `2026-04-27-migration-to-indemn-infrastructure-design.md` | 1.4 (Secrets layout) | Note that several design slots (`api-token`, `LLM_API_KEY`) aren't actually needed; document the cleanup-vs-shared decision |
| `2026-04-27-migration-implementation-plan.md` | Phase I.5 prereq | Add IAM OIDC role prod blocker — three resolution options on file in DEVOPS-153 comments |

## Tracked follow-ups (carried + new)

### Must-fix before Phase G (dev deploy)
1. **DEVOPS-159 (runners) must complete first.** Without runners online for `indemn-ai/gic-email-intelligence`, build.yml's deploy job queues forever.
2. **CORS_ORIGINS pre-deploy verification.** The 7-URL list in Parameter Store was assembled from the handoff doc's must-fix list. Verify against the original `api/main.py:54-61` hardcoded list before unpausing in G.2.

### Must-fix before Phase F.2
3. **Repo admin access** — Dhruv either grants `craig-indemn` admin on `indemn-ai/gic-email-intelligence` (cleanest), OR Dhruv himself executes F.2 (sets branch protection on `main` and `prod`). Surfaced in DEVOPS-159 as a side ask.

### Must-fix before Phase I (prod cutover)
4. **IAM OIDC role prod allow.** `github-actions-deploy` role's `DenyProdExplicitly` blocks reading `indemn/prod/gic-email-intelligence/*`. Pick one of the 3 options on file (DEVOPS-153 comments) before I.4.
5. **UI integration for `failed_recovery_review` state** (carried from prior session): `ui/src/api/types.ts:99`, `SubmissionQueue.tsx:42,284-291`, `ProcessingTimeline.tsx:92,99`. Cutover gate at design-doc line 2082 says "failed_recovery_review count must be 0" — operators need a UI surface to see the count.
6. **Datadog routing decision** (Phase H.1) — PagerDuty vs Slack-to-phone. Block H.1 until decided.

### Nice-to-have (post-cutover)
7. JWT_SECRET rotation. Current dev value is 14 chars (verified in E.1 sanity check). Should be ≥32 chars before EC2 dev becomes the canonical environment.
8. Carry-forward items from prior session (auth fixes B.1 review M-1, Pydantic v2 ConfigDict migration, narrow except clauses in recovery.py, surface `automation_recovery_note` in UI/API, consolidate dual `outlook-agent`/`gic` CLIs, harness.py reorganization, health.py router rename).

## How to resume in the next session

1. **Read this file first**, then `2026-04-27-migration-execution-handoff.md` (Phases A–D context, still current). Strategic context in `2026-04-27-migration-to-indemn-infrastructure-design.md` and task structure in `2026-04-27-migration-implementation-plan.md` — both are now slightly outdated re: E.3 / E.4 / E.6 (see "Doc updates needed" above).
2. Confirm worktree state:
   ```bash
   cd /Users/home/Repositories/gic-email-intelligence-migration && git status && git log --oneline -3
   # Expect: clean, branch tip daf216e, 33 commits ahead of origin/main
   ```
3. Run unit tests: `uv run pytest tests/ --ignore=tests/test_api.py --ignore=tests/test_e2e_pipeline.py -q --tb=no` → 113 passed, 1 pre-existing failure
4. Check Linear DEVOPS-159 status:
   - If still Backlog/In Progress: stay on Phase F.1 (push). Don't try F.2 yet (needs admin).
   - If Done: full Phase F + G unblocked. Proceed to F.1.
5. **Phase F.1 (push) is doable now without DEVOPS-159** — we have `push` permission on the empty repo. The only thing this kicks off is the GitHub Actions workflow waiting for runners. F.1 push, then wait for runners, then F.3 (Amplify rewire — also doable independently of admin), then F.2 last.
6. Update any out-of-date design / plan docs per the "Doc updates needed" table above before starting F. Quick wins for clarity.

## Session metrics

- Wall-clock: ~3 hours of execution
- 1 commit (loader patch `daf216e`)
- 8 AWS state changes (6 secret create, 2 secret delete, 1 secret update, 22 param create — plus 2 SG ingress rules)
- Zero production touches
- 1 Linear sub-issue created + 4 comments + 1 status change
- Major design corrections discovered in flight: Atlas via PrivateLink (not public allowlist), per-repo runners (not org-level), shared/* vs GIC-specific values for select infrastructure secrets
