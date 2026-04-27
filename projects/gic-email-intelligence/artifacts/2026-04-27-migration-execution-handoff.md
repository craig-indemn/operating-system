---
ask: "Capture every irreplaceable piece of context from the migration execution session so the next session can resume Phase E with zero information loss."
created: 2026-04-27
workstream: gic-email-intelligence
session: 2026-04-27-b
sources:
  - type: codebase
    description: "31 commits on /Users/home/Repositories/gic-email-intelligence-migration:migration/indemn-infra"
  - type: aws
    description: "SSM inspection of dev-services, ALB inventory, EIP verification, SG audit"
  - type: subagent-driven-development
    description: "12 implementer + spec + quality review cycles for Phase B; 2 batched dispatches for C and D"
---

# GIC → Indemn Migration — Execution Handoff (End of Phase D)

**Status:** Phases A, B, C, D complete. Branch `migration/indemn-infra` in worktree `/Users/home/Repositories/gic-email-intelligence-migration` is **31 commits ahead of `origin/main`**, working tree clean, 113 unit tests passing.

**Next session resumes at Phase E** (AWS Secrets Manager + Parameter Store + Atlas allowlist + Unisoft SG). Every step in Phase E is **[NEEDS USER APPROVAL]** per the production-safety rule.

## Linear tracking (created end of session 2026-04-27)

Migration is now tracked under **DEVOPS-151** (parent) with 7 sub-issues — one per phase. Use the `/linear` skill to update status as work progresses.

| Linear ID | Phase | State | Notes |
|---|---|---|---|
| DEVOPS-151 | Parent | Backlog | Move to **In Progress** when Phase E begins |
| DEVOPS-152 | Phase A–D (32 commits) | **Done** | Already complete; do not modify |
| DEVOPS-153 | Phase E (AWS infra) | Backlog | Has E.5 OIDC blocker noted in description |
| DEVOPS-154 | Phase F (push + Amplify rewire) | Backlog | |
| DEVOPS-155 | Phase G (dev deploy + 24h soak) | Backlog | |
| DEVOPS-156 | Phase H (ops readiness, parallel with G) | Backlog | |
| DEVOPS-157 | Phase I (prod cutover, 90-min window) | Backlog | Priority 1 |
| DEVOPS-158 | Phase J (7-day soak + tear-down) | Backlog | |

**Status update protocol for the next session:**
- When starting a phase: update its sub-issue Backlog → In Progress (`linearis --api-token "$LINEAR_API_KEY" issues update DEVOPS-XXX --status "In Progress"`)
- When a phase completes: → Done. Add a comment with commit SHAs / outcome via `linearis comments create DEVOPS-XXX --body "..."`
- Update parent DEVOPS-151 → In Progress when Phase E starts; → Done when Phase J completes
- For Phase E specifically, comment on each E.1–E.6 sub-step as it's approved + executed
- All `linearis` commands need `--api-token "$LINEAR_API_KEY"` flag (the env var is set in `~/.zshrc`-sourced `.env` but the CLI doesn't pick it up automatically; the proxy `linearis-proxy.sh` is broken because it tries 1Password and the credential isn't in the expected vault)

**Linear skill is globally available.** The next session can invoke `/linear` (skill in user-invocable list) without setup.

## Read-first files for the next session

1. **This file** — execution state, ground-truthed facts, tracked follow-ups
2. `projects/gic-email-intelligence/artifacts/2026-04-27-migration-to-indemn-infrastructure-design.md` — strategic design (4 review rounds)
3. `projects/gic-email-intelligence/artifacts/2026-04-27-migration-implementation-plan.md` — bite-sized task plan (2 review rounds)
4. `projects/gic-email-intelligence/INDEX.md` — workstream resume narrative

The implementation plan's **Phase E** section is the next session's task list verbatim. This handoff doc adds the execution-time facts the plan didn't have.

## The 31 commits (chronological)

```
ae81ddc test(models): align with 8-stage lifecycle redesign (e723a50)
f79ff05 feat(loop): add SIGTERM-aware run_loop helper for cron containers
9221041 refactor(loop): tighten docstring on env reload + drop unused pytest import
a9d84fa feat(sync): support --loop --interval for long-running container mode
19f3e59 refactor(sync): rename _sync_tick parameter to cfg + sync doc references to new CLI form
c013251 feat(automate): support --loop --interval for long-running container mode
79b3a25 refactor(automate): move pause check into _automate_tick + forward flags via partial
e0e0cfb feat(process): support --loop --interval for long-running container mode
587ade7 docs(harness): explain batch gate on _process_tick pause check
73ab9da feat(config): add PAUSE_SYNC and enforce in sync tick
e8f74b1 docs(sync): drop now-stale 'Phase B.5 adds' tense from _sync_tick docstring
caa7323 feat(api): add /healthz process-alive endpoint for Docker healthcheck
6aacb0c test(healthz): rename test to be honest about what it verifies
364b6ca refactor(submissions): extract _find_duplicate_by_name helper for in-process callers
2db728c feat(automation): add stale-claim recovery with fail-closed duplicate check
c4f2745 refactor(recovery): wrap Mongo writes + tighten test contract + bucket failed_recovery_review in stats
53f58f1 feat(api): env-var-ize CORS_ORIGINS with whitespace stripping and startup log
ca9d960 feat(config): env-var-ize GRAPH_USER_EMAIL and parameterize skill prompts
9b5f707 feat(config): env-var-ize task group IDs and PUBLIC_BASE_URL
ea0a338 feat(config): require UNISOFT_PROXY_URL env var (remove hardcoded fallbacks)
9cf9755 chore: delete dead code (addin-test, data exploration corpus, design HTMLs, deprecated skill)
c43bc88 chore(scripts): delete one-off historical migration/seed scripts
64cd38b chore(docker): strip entrypoint.sh Mongo primary detection (Atlas SRV makes it unreachable)
8a57e41 feat(docker): add docker-compose.yml with 4 services (api, sync, processing, automation)
cd2a259 feat(deploy): add aws-env-loader.sh with GIC-specific PARAM_MAP entries
c026758 ci: add build.yml for dev branch (build + push + deploy to dev-services)
85c14b0 ci: add build-prod.yml for prod branch (deploy to prod-services)
14b82b6 ci: add Trivy image vulnerability scanning workflow
e777bc0 chore(repo): add dependabot config and CODEOWNERS
36a15de fix(docker): use agent.harness module path for processing-cron
182f3c0 docs: add README and operational runbook
```

Phase A: `ae81ddc`. Phase B: `f79ff05` → `ea0a338` (19 commits). Phase C: `9cf9755` → `64cd38b` (3). Phase D: `8a57e41` → `182f3c0` (8 — one extra for the `automate process` → `outlook-agent process` correction).

## Ground-truthed AWS facts (verified this session via SSM/AWS CLI)

**Indemn AWS account:** `780354157690`

**EC2 EIPs (attached, persist across stop/start):**
- dev-services `i-0fde0af9d216e9182` → EIP `44.196.55.84` (alloc `eipalloc-052cb05ad7610770a`)
- prod-services `i-00ef8e2bfa651aaa8` → EIP `98.88.11.14` (alloc `eipalloc-033cd7692f750f1ae`)
- indemn-windows-server (Unisoft proxy) `i-0dc2563c9bc92aa0e` → EIP `54.83.28.79`, private IP `172.31.23.146`

**Indemn ingress pattern: ALB-per-service-per-env** (NOT shared ALB with hostname routing). Example template: `dev-bot-service` ALB has HTTPS:443 listener, HTTP target group port 80 → `i-0fde0af9d216e9182:8001`. Route 53 CNAME `bot.indemn.ai` → ALB DNS. Verified by inspecting `aws elbv2 describe-load-balancers` and the listener/target-group config.

**Implication for GIC:** Phase E (or Phase F deployment) must create:
- `dev-gic-email-intelligence` ALB → target group → `i-0fde0af9d216e9182:8080`
- `prod-gic-email-intelligence` ALB → target group → `i-00ef8e2bfa651aaa8:8080`
- HTTPS listener with ACM cert for `*.gic.indemn.ai` (or specific subdomain)
- Route 53: `api-dev.gic.indemn.ai` → dev ALB; `api.gic.indemn.ai` → prod ALB
- `docker-compose.yml` uses `ports: ["8080:8080"]` (already in place)

**Nginx on dev-services exists but is NOT the API ingress.** Only serves a static-site config for `abc.indemn.ai`. Don't try to route GIC traffic through it.

**Unisoft proxy SG `sg-04cc0ee7a09c15ffb` current state (verified earlier):**
- Allows ports 5000+5001 from these CIDRs:
  - `162.220.234.15/32` (Railway — REMOVE during cutover)
  - `73.87.128.242/32` (office)
  - `96.244.115.146/32` (office)
- **NO VPC CIDR rule, NO SG-reference rule.** EC2-to-proxy traffic from dev-services / prod-services is NOT permitted today.
- Phase E.4 MUST add an SG-reference rule from each of dev-services and prod-services SGs to ports 5000+5001 — this is the canonical AWS-best-practice fix.
- Phase I.11 removes Railway IP after cutover.

**Amplify app for the UI:**
- App ID `d244t76u9ej8m0`, name `gic-email-intelligence`, account `780354157690` (Indemn)
- Currently sourced from `craig-indemn/gic-email-intelligence` (must rewire in Phase F.3 to `indemn-ai/gic-email-intelligence`)
- Custom domain `gic.indemn.ai` already wired
- Branches: `main` → dev, `prod` → prod

## State of the world right now

**Working directories:**
- Migration worktree: `/Users/home/Repositories/gic-email-intelligence-migration` (branch `migration/indemn-infra`)
- Personal repo (other session): `/Users/home/Repositories/gic-email-intelligence` (branch `main`, last commit `a42bbe1`) — **another Claude session is monitoring/bug-fixing here**; do not collide
- Operating-system worktree: `/Users/home/Repositories/operating-system/.claude/worktrees/unisoft` (this session)

**Remotes on the migration worktree:**
- `origin` → `https://github.com/craig-indemn/gic-email-intelligence.git` (personal)
- `indemn` → `https://github.com/indemn-ai/gic-email-intelligence.git` (target — empty repo created by Dhruv 2026-04-27)

**Production state (Railway, untouched by this session):**
- `gic-email-intelligence` Railway project (`4011d186-1821-49f5-a11b-961113e6f78d`) running prod env normally
- API + sync + processing + automation crons running with last commit `a42bbe1` from the personal repo

**Test state on migration branch:**
- 113 unit tests passing
- 1 pre-existing failure: `test_skill_tool_map_has_all_skills` references the deprecated `stage-detector` skill from before the 2026-03-24 8-stage redesign. **NOT a regression.** Has been failing on `main` of the personal repo for ~5 weeks. Predates this session's work entirely. Not blocking.
- Mongo-dependent integration tests in `test_api.py` (8 failures) and `test_e2e_pipeline.py` (2 errors) skipped due to no local Atlas. Will pass in CI when env is configured.

## Tracked follow-ups (NOT blockers; address before relevant gates)

These came out of the subagent code reviews. Each is real but explicitly out of scope for the task that surfaced it.

### Must-fix before Phase F (push to indemn-ai)
- *(none — Phase F is mechanical push; no code changes needed)*

### Must-fix before Phase I (prod cutover)
1. **UI integration for `failed_recovery_review` state.** Frontend doesn't recognize this new automation_status value. Files to update:
   - `ui/src/api/types.ts:99` — add `'failed_recovery_review'` to the `automation_status` union
   - `ui/src/pages/SubmissionQueue.tsx:42,284-291` — `getRequiresAttention()` filter, `not_linked` / `new_application` buckets
   - `ui/src/components/ProcessingTimeline.tsx:92,99` — render the new state
   The cutover gate at design-doc line 2082 says "failed_recovery_review count must be 0" — operators need a UI surface to *see* the count.
2. **Verify dev/prod Parameter Store `cors-origins` contains all 7 previously-hardcoded URLs** before deploy: `gic.indemn.ai`, `dev.gic.indemn.ai`, the two Amplify branch URLs, `gic-addin.vercel.app`, `localhost:5173`, `localhost:3000`.
3. **Verify Datadog routing** (PagerDuty vs Slack-to-phone) before alerting is wired. The plan flagged this as a [NEEDS USER APPROVAL] decision in H.1.

### Nice-to-have (post-cutover follow-up)
4. `run_loop` `threading.Event` refactor (B.1 review M-1) — replaces global `_shutdown` flag + 1-sec-granular sleep with sub-second `Event.wait(timeout)`, plus signal-handler save/restore for test isolation.
5. Pydantic v2 `class Config` → `ConfigDict` migration (deprecation warning surfaces on every test run, pre-existing).
6. Narrow `recovery.py:_check_existing_quote` `except Exception` to `except (PyMongoError, RuntimeError)` so programming errors surface as test failures instead of bumping the `errors` counter.
7. Surface `automation_recovery_note` field in the API/UI for human reconciliation (currently mongo-only metadata).
8. Consolidate `outlook-agent` commands into `gic` entry point (or document the dual-CLI rationale clearly). The plan's `automate process` typo was a symptom.
9. Move `process_command` + `_process_tick` from `harness.py` to `cli/commands/process.py` to match `sync.py`/`automate.py` shape.
10. Rename `health.py:router` → `health_router` for symmetry with `liveness_router` (B.6 review M-2).

### Operational consequences of B.10/B.11 to remember
- `gic --help` and `outlook-agent --help` now fail at `Settings()` validation when env vars are missing (because `graph_user_email`, `unisoft_task_group_id_*`, `unisoft_proxy_url` are required-no-default).
- Local dev workflow: developers must have a `.env` file. `tests/conftest.py` sets defaults at import time so the test suite still works.
- Production: AWS Secrets Manager + Parameter Store provide all required values via `aws-env-loader.sh`.
- Document this in `docs/runbook.md` if not already covered (Phase D.7).

## Decision rationale beyond commit messages

These judgment calls were made during execution and are worth preserving:

- **B.3 cleanup commit `79b3a25` front-loaded B.5's automation work.** Code reviewer identified that the wrapper-level pause check only fires at startup, defeating PAUSE_AUTOMATION in loop mode. Moved pause check into `_automate_tick` + added `functools.partial` flag forwarding. B.5's scope therefore reduced to sync-only.
- **B.4 preserved the `if batch and ...` gate on the pause check** in `_process_tick`. Original behavior: single-email diagnostic runs (`--email <id>` without `--batch`) bypass the pause flag intentionally so an operator can inspect a specific email while production is paused. Comment added at `harness.py:450` to make the intent obvious.
- **B.5 was small** because B.3 cleanup absorbed automation's pause work; only sync needed updating. 3 tests, 6 LOC of code change.
- **B.6 created a separate `liveness_router`** (no prefix) instead of including `health.router` twice with different prefixes — FastAPI can't include the same router with two prefixes for two routes.
- **B.7 ID extraction split into TWO helpers** (`_find_duplicate_matches` for the CLI's 5-match output, `_find_duplicate_by_name` for the recovery's top-1) instead of one. Spec called for one but the CLI's display-formatting required the list form too. Cleanest preservation of CLI behavior.
- **B.7 cleanup commit `c4f2745` extended scope to stats.py** (`auto_failed = failed + failed_recovery_review`, journey pipeline `$in: [failed, failed_recovery_review]`). Without this the new state would silently disappear from dashboards. UI updates explicitly deferred (broader scope).
- **B.9 expanded scope significantly** beyond the plan's 7-file list: 12 files updated. Justifications: (a) plan listed wrong loader (`automation/agent.py` instead of `agent/harness.py:load_skill` which actually loads `email_classifier.md`); (b) `unisoft-proxy/client/cli.py:305` had same antipattern (grep extension); (c) `create-quote-id.md` also had inbox references; (d) `situation_assessor.md` needed brace escaping for `.format()` compatibility (~67 patterns total). Spec reviewer confirmed all expansions justified by the plan's "grep all occurrences and audit all .md files" instruction.
- **C.2 deleted entire `scripts/` directory** (10 files, including 5 ambiguous ones). Rationale: "when in doubt, delete; git history preserves them" per the plan. None were referenced by `pyproject.toml` / `docker-compose.yml` / `Dockerfile` / `entrypoint.sh` / docs (other than a historical implementation plan referencing `seed_outlook.py` — kept the doc, deleted the script).
- **D.1 caught a bug in the design's compose template** (`automate process` doesn't exist as a `gic` subcommand — it's `outlook-agent process` in `agent/harness.py`). Fixed in commit `36a15de`. Without this, `processing-cron` container would crash-loop on `Error: No such command 'process'`.
- **D.3/D.4 modernized GitHub Actions versions** vs bot-service's deprecated `docker/build-push-action@v1`. Used `actions/checkout@v4`, `docker/setup-buildx-action@v3`, `docker/login-action@v3`, `docker/build-push-action@v5` with explicit context, GHA buildx caching, multi-tag push. Functionally equivalent on supported versions. Bot-service should follow eventually.
- **`scripts/aws-env-loader.sh` extended with Secrets Manager paths** (`gic-email-intelligence/graph-credentials`, `gic-email-intelligence/unisoft-credentials`) not in the design's PARAM_MAP — necessary because Graph + Unisoft creds are secrets, not config.
- **CODEOWNERS uses only `@craig-indemn`** (not `@dhruv-indemn`) per the design's "if unsure" fallback.

## Codebase facts learned that aren't in commits

- `harness.py` is a mixed module — pipeline orchestrator helpers (`process_email`, `_enrich_submission_from_extractions`) AND the Typer CLI for `outlook-agent`. Tech debt; design didn't reorganize.
- Two CLI entry points in `pyproject.toml`: `gic` (→ `cli/main.py:app`) and `outlook-agent` (→ `agent/harness.py:app`). `outlook-inbox` is a back-compat alias for `gic`.
- The `next_email` query in `cli/commands/emails.py:160-167` uses `{"$or": [{"$exists": False}, {"$eq": None}]}` — a string value like `"failed_recovery_review"` matches NEITHER branch. Verified safe from re-claim.
- `_count_pending_emails` in `automate.py` uses the same `$or` pattern; flagged emails also excluded from pending counts.
- Both skill loaders (`automation/agent.py:_load_skill` AND `agent/harness.py:load_skill`) exist and serve different sets of skills. Both updated in B.9 to do `.format()` substitution.
- `tests/conftest.py` sets these env vars at import time so `Settings()` instantiation in tests doesn't fail with `ValidationError` on the now-required fields:
  - `GRAPH_USER_EMAIL=quote@gicunderwriters.com`
  - `UNISOFT_TASK_GROUP_ID_NEWBIZ=2`
  - `UNISOFT_TASK_GROUP_ID_WC=4`
  - `UNISOFT_PROXY_URL=http://test-proxy:5000`
- The `automation_recovery_note` field added to email docs in B.7 has no consumer (yet). Pure metadata for human reconciliation.

## Session pattern that worked well

- **Subagent-driven-development** (skill `superpowers:subagent-driven-development`) for every Phase B task: implementer → spec reviewer → code quality reviewer.
- **Combined spec+quality review** for small/contained changes (B.5, B.6, B.8) — saved one dispatch per task.
- **Full two-stage review** for complex tasks (B.7 with idempotency, B.9 with multi-file scope expansion).
- **Batch dispatches** for Phase C (3 mechanical cleanup tasks) and Phase D (7 file-creation tasks). Sub-agents reported back with multi-task summaries; one dispatch each phase.
- **Direct fix-and-commit** for trivial cleanup (3-line docstring updates) instead of subagent dispatch.

## Phase E task list (next session starts here)

Verbatim from the implementation plan, with execution-ready notes:

### E.1: Populate AWS Secrets Manager (dev) [NEEDS USER APPROVAL]
- Pull each secret from current Railway dev env (`railway variables --environment development --service api` etc.) — use `upsert_secret` helper from the plan (idempotent: `describe-secret` || `put-secret-value` else `create-secret`)
- Path: `indemn/dev/gic-email-intelligence/*` — **NO leading slash** (Secrets Manager convention)
- Entries: `mongodb-uri`, `graph-credentials` (JSON), `anthropic-api-key`, `google-cloud-sa-json`, `unisoft-api-key`, `jwt-secret`, `tiledesk-db-uri`, `api-token`, `langsmith-api-key`

### E.2: Populate Parameter Store (dev) [NEEDS USER APPROVAL]
- Path: `/indemn/dev/gic-email-intelligence/*` — **WITH leading slash** (Parameter Store convention; verified differs from Secrets Manager)
- Always pass `--overwrite` for retry safety
- Entries listed in plan's PARAM_MAP table; the `aws-env-loader.sh` script committed in `cd2a259` knows the full set

### E.3: Atlas allowlist (dev EIPs) [NEEDS USER APPROVAL]
- Add `44.196.55.84/32` and `98.88.11.14/32` to `dev-indemn` Atlas project's Network Access list
- Verify connectivity from dev-services via SSM + mongosh ping

### E.4: Unisoft proxy SG SG-reference rules [NEEDS USER APPROVAL]
- Find dev-services and prod-services SG IDs first: `aws ec2 describe-instances --instance-ids i-0fde0af9d216e9182 i-00ef8e2bfa651aaa8 --query '...SecurityGroups[0].GroupId'`
- Add to `sg-04cc0ee7a09c15ffb`: ingress on ports 5000+5001 with `--source-group <dev-sg>` and `--source-group <prod-sg>`
- Verify connectivity: SSM into dev-services, `curl -v http://172.31.23.146:5001/api/health`

### E.5: GitHub OIDC role permissions
- Find role: `aws iam list-roles --query "Roles[?contains(RoleName,'github-actions')].RoleName"`
- Verify it can read `indemn/dev/gic-email-intelligence/*` and `indemn/prod/gic-email-intelligence/*` (may already be covered by wildcard)

### E.6: Self-hosted runners online
- `gh api repos/indemn-ai/gic-email-intelligence/actions/runners` — confirm runners with `dev` and `prod` labels are online and idle
- Smoke-test by queuing a no-op build to dev runner; <2 min completion

## After Phase E

**Phase F (push + branch protection + Amplify rewire)** — also user-approval territory but small.

**Phase G (dev EC2 deployment + 24h soak)** — once F is done, deploy to dev-services with all `pause-*=true`, then carefully unpause sync → processing → automation against UAT Unisoft.

**Then Phase H (operational readiness — Datadog alerts, S3 versioning, etc.) parallel with G.**

**Then Phase I (prod cutover, 90-min hard window, full runbook execution).**

## How to resume in the next session

1. Read this file + the design doc + the implementation plan (in that order — this file gives execution context, design gives strategic context, plan gives task structure).
2. `cd /Users/home/Repositories/gic-email-intelligence-migration && git status && git log --oneline -5` to confirm branch state.
3. Run `uv run pytest tests/ --ignore=tests/test_api.py --ignore=tests/test_e2e_pipeline.py -q --tb=no` — expect 113 passed, 1 failed (pre-existing skill-map test).
4. Decide Phase E vs Phase F first move. Plan default is E first (set up AWS infra in dev), then F (push to indemn-ai), then G (deploy + soak).
5. For each Phase E step, ask the user explicit approval before executing the AWS state change.

## End-to-End Verification Results (3 parallel reviews)

Three subagent reviews ran at the end of this session to ground-truth the 32-commit branch end-to-end (the 31 above + commit `78da16f` that fixed the Dockerfile comment).

### Phase B verification (Subagent 1) — **PASS** on all 7 design items

All Phase 1.0 items delivered and integrated:
1. SIGTERM-aware loop with settings reload ✓
2. PAUSE_SYNC config + sync-tick enforcement ✓
3. Stale-claim recovery with 60-min timeout, fail-closed duplicate check, `failed_recovery_review` state ✓ (with stats.py bucket integration via `auto_failed = failed + failed_recovery_review`)
4. `/healthz` split (separate `liveness_router` at root, `/api/health` rich on `/api` prefix) ✓
5. `GRAPH_USER_EMAIL` env-var-ized + skill prompt placeholders work via `.format()` in both loaders ✓
6. `CORS_ORIGINS` env-driven with Pydantic validator + startup log ✓
7. Task group IDs + `PUBLIC_BASE_URL` env-driven, skill prompt has `{unisoft_task_group_id_*}` placeholders ✓

22 Phase B-specific tests pass (loop, sync-loop, automate-loop, process-loop, pause-sync, healthz, automation-recovery, cors-config, skill-loading). No regressions from the five `_*_tick` refactors verified by side-by-side `git show` comparison. Pause-flag flow traced end-to-end: env var → Parameter Store → loader → `.env.aws` → `Settings()` per tick → check fires <1s on next tick boundary.

### Phase C+D verification (Subagent 2) — **10/11 PASS**, 1 defect found and fixed

All cleanup deletions confirmed gone with no broken references. docker-compose validates. PARAM_MAP has all 17 GIC entries. Workflows use modern action versions (checkout@v4, build-push@v5 — improvement over bot-service's @v1). Trivy + dependabot + CODEOWNERS + README + 233-line runbook all present and accurate.

**Defect found:** Dockerfile comment line 60 referenced the now-incorrect `gic_email_intel.cli.main automate process` path (the actual command is `gic_email_intel.agent.harness process`). docker-compose.yml was already correct (commit `36a15de` fixed it during D.1) but the Dockerfile comment wasn't updated. **Fixed in commit `78da16f`** during this verification pass.

Net repo stats: +2197 / -10901, dominated by Phase C deletions. Phase D additions are small.

### Phase E readiness check (Subagent 3) — **4 READY, 2 NEEDS WORK**

**Ready** (Phase E can proceed for these):
- **E.1 Secrets Manager (dev):** No conflicting secrets exist, safe to create fresh
- **E.2 Parameter Store (dev):** `--overwrite` flag in plan handles retry safety
- **E.3 Atlas allowlist:** EIPs `44.196.55.84` and `98.88.11.14` confirmed still attached
- **E.6 Self-hosted runners:** repo `indemn-ai/gic-email-intelligence` confirmed empty + ready

**Needs work — must address before E executes:**

- **E.4 Unisoft proxy SG:** Verified `sg-04cc0ee7a09c15ffb` still has only the 3 public-IP rules (Railway + 2 office). **NEW FINDING: dev-services and prod-services share SG `sg-d4163da4` (name `ptrkdy`).** One SG-reference rule from `sg-d4163da4` to ports 5000+5001 covers both EC2 instances. Plan called for two rules (one per SG) but they collapse to one given shared SG.
- **E.5 GitHub OIDC role: NEW BLOCKER FOUND.** Existing role `github-actions-deploy` has inline policy `deploy-dev-only` that explicitly **denies** `indemn/prod/*`. The prod-branch deploy job will fail because it can't read prod secrets. **Phase E.5 must either (a) create a second OIDC role scoped to prod, or (b) extend `deploy-dev-only` to allow `indemn/prod/gic-email-intelligence/*` reads.** This is a blocker the plan didn't anticipate.

**Verify-during-E (not blocking now):**
- **E.6 Runner verification** — CLI auth doesn't have GitHub org admin scope, can't query org-level runners. Org admin (Dhruv?) must confirm runners exist with correct labels before Phase G deploy attempts the workflow.

**Other findings worth carrying into Phase E:**

- Resource headroom on dev-services: 9.7 GB free, ample for the 4 new GIC containers (~5.5 GB needed). No constraint.
- `shared-datadog` external Docker network confirmed present on dev-services. Phase G compose will mount it cleanly.
- 22+ existing containers running on dev-services (bot-service, observability, etc.). Adding 4 more is safe.
- Railway prod has `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` set as env vars. **Do NOT copy these to Secrets Manager.** Replace with EC2 IAM role at deploy time. Document in runbook for future devs.
- Phase E.1 must audit env vars from ALL 4 Railway prod services (api, sync, processing, automation), not just api. Some Unisoft env vars may live only on the automation service.

## Updates to tracked follow-ups (post-review)

- ~~**Dockerfile comment defect**~~ — fixed in `78da16f` during review.
- **NEW (must-fix before Phase E):** GitHub OIDC role policy update for prod access — see E.5 finding above.
- **NEW (must-document in Phase E.1 runbook step):** Railway's `AWS_ACCESS_KEY_ID/SECRET` env vars are NOT to be replicated to Secrets Manager — replace with EC2 IAM role.
- **Phase E.4 simplification:** dev-services + prod-services share `sg-d4163da4`, so one SG-reference rule (not two) suffices.

## Final session metrics

- Wall-clock: ~4 hours of execution after design + plan reviews
- 31 commits, 7 implementer subagent dispatches (B.1-B.4, B.7, B.9, batched C+D), 8 review subagent dispatches
- ~10,500 LOC removed (mostly `data/` exploration corpus + dead scripts)
- Net new code: ~800 LOC (recovery, loop helper, healthz, env-vars, docker-compose, workflows, runbook)
- 1 pre-existing test failure carried forward (skill_tool_map; predates session by 5 weeks)
- Zero production touches (everything stayed on the migration branch in an isolated worktree)
