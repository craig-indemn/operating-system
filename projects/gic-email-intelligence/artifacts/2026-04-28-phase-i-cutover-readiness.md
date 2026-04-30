---
ask: "Snapshot the cutover-readiness state — what's done, what's left, the runbook Craig executes on cutover day, and clean rollback procedure. Single document handed off for the cutover window."
created: 2026-04-28
workstream: gic-email-intelligence
session: 2026-04-28-c
sources:
  - type: aws
    description: "Prod Secrets Manager + Parameter Store populated under indemn/prod/gic-email-intelligence/*"
  - type: vercel
    description: "Outlook add-in rebuilt + deployed against canonical api.gic.indemn.ai/api"
  - type: amplify
    description: "App d244t76u9ej8m0 rewired to indemn-ai/gic-email-intelligence; main branch build verified"
  - type: github
    description: "indemn-ai/gic-email-intelligence — main + prod branches both protected; PR #18 awaiting review"
---

# Phase I — Cutover-Readiness State

> **🔄 SUPERSEDED 2026-04-29 — cutover executed.**
> This document is the **pre-cutover snapshot + runbook**. For the post-cutover state, lessons learned, and current carryover items, read **[`2026-04-29-cutover-execution-handoff.md`](2026-04-29-cutover-execution-handoff.md)** instead. That artifact is the current source of truth for the GIC migration.
>
> Production is now live on EC2 prod-services as of 2026-04-29 ~22:50 UTC. Phase J (7-day soak) in progress. Kept here for historical reference of the original plan.

**TL;DR:** Pre-cutover prep complete except for **PR #18 review/merge**. Once that lands, the cutover window is fireable.

## Pre-cutover checklist

| # | Item | Status | Owner |
|---|------|--------|-------|
| 1 | PR #18 (SOAK_MODE flag) reviewed + merged | ⏳ Awaiting review | Dolly / Dhruv / Rudra |
| 2 | F.2 — `prod` branch protection on indemn-ai/gic-email-intelligence | ✅ Done — branch at `b1fc9d77`, protected via org "Prod PR" ruleset | — |
| 3 | F.3 — Amplify rewire to indemn-ai (dev branch) | ✅ Done — main branch build job 106 succeeded against new repo | — |
| 4 | I.1b — Outlook add-in rebuild | ✅ Done — `gic-addin.vercel.app` now serves bundle pointing at `https://api.gic.indemn.ai/api` (canonical) | — |
| 5 | I.2 — Prod Secrets Manager + Parameter Store | ✅ Done — 5 secrets + 24 params under `indemn/prod/gic-email-intelligence/*`, with PrivateLink mongodb-uri, prod proxy port 5001, prod task action IDs (70/3), all `pause-*=true` initial | — |

## Decisions still owed (Craig)

These don't block cutover technically but should be made before the window:

1. **Datadog routing (H.1).** PagerDuty or Slack-to-phone? Operational visibility during cutover. Skipping is valid — alerts can be added post-cutover, but the cutover window itself runs blind to anything except direct log inspection.
2. **Atlas backup tier verification (H.2).** Atlas UI check on `dev-indemn` cluster: confirm continuous backup with ≥30-day retention. If not, upgrade tier before cutover (Atlas UI; can be done same-day).
3. **Customer comms (T-24h).** Email to JC + Maribel announcing the window. Template in implementation plan section I.1 of `2026-04-27-migration-implementation-plan.md`. Send 24h before window.

## Cutover window — runbook summary

Reference: full per-step detail in `2026-04-27-migration-implementation-plan.md` Phase I.1–I.12.

**Window:** ~90-min hard-stop. Target a low-traffic window (early Tuesday or Wednesday morning before agents start sending). 24-h watchful soak after.

**Roles per design:**
- Cutover lead: Craig
- Backup lead: Dhruv (must have AWS, Atlas, Railway, Amplify, Vercel access; brief 24h prior with this doc + implementation plan)
- Customer comms: Craig (T-24h, T+0 start, T+0 done)

**Order of operations during the window:**

1. **T-24h:** Customer comms email + verify Atlas backup tier (H.2) + lower Route 53 TTL on `api.gic.indemn.ai` to 60s
2. **T-0 step 0:** Customer comms ("starting now")
3. **Atlas snapshot** of `gic_email_intelligence` (rollback floor; record snapshot ID in cutover Slack thread)
4. **Pause Railway prod** all 3 services: `railway variables set PAUSE_SYNC=true PAUSE_PROCESSING=true PAUSE_AUTOMATION=true --environment production --service {sync|processing|automation}` — wait 360s for any in-flight tick to drain
5. **Push prod branch:** `git push indemn migration/indemn-infra:prod` — triggers `build-prod.yml` workflow → builds + deploys to prod-services EC2 with all `pause-*=true` initial
6. **Trigger Amplify prod rebuild:**
   - `aws amplify update-branch --app-id d244t76u9ej8m0 --branch-name prod --environment-variables VITE_API_BASE=https://api.gic.indemn.ai`
   - `aws amplify start-job --app-id d244t76u9ej8m0 --branch-name prod --job-type RELEASE`
7. **DNS flip on `api.gic.indemn.ai`:** Route 53 → ALB DNS for `dev-gic-email-intelligence` ALB on prod-services (or whichever ingress pattern is wired — see ingress investigation note below)
8. **Unpause EC2 prod crons one at a time** (5-min soak between each):
   - sync-cron first (lowest risk)
   - processing-cron next
   - automation-cron last (writes to Unisoft prod)
9. **Verify end-to-end** with a real customer email or controlled test:
   - `processing_status: complete` within 5 min of arrival
   - `automation_status: complete` with populated `unisoft_quote_id` within 30 min
   - Quote in Unisoft prod with attachments + activity + notification email delivered to agent
   - Datadog clean (if H.1 wired)
10. **Remove Railway IPs from allowlists** (Atlas + Unisoft proxy SG `162.220.234.15/32`)
11. **T+0 done customer comms** ("Migration complete. Flag anything that looks off.")

**Hard-stop at 90 min.** If verification step 9 hasn't passed by 90 min, abort + roll back rather than push through.

## Open ingress investigation (before cutover or at step 7)

The Phase G work proved the EC2 dev container stack runs cleanly, but the **ingress pattern from `api.gic.indemn.ai` → EC2 prod container port 8002** isn't fully wired yet. Two paths:

- **(a)** Add a server block to host nginx on prod-services routing `api.gic.indemn.ai` → `localhost:8002` (matches the dev-services pattern; ~5 min)
- **(b)** Create an ALB `dev-gic-email-intelligence` (or `prod-gic-email-intelligence`) with target group → `i-00ef8e2bfa651aaa8:8002`, listener with ACM cert, Route 53 alias to ALB DNS

Pattern (a) matches what bot-service / observability use on these EC2 instances per the F.1 inspection. **Recommend (a)** — less infrastructure to manage, matches existing convention.

**Required step before cutover:** SSM into prod-services, confirm host nginx is running and check existing config patterns (similar to dev-services nginx with `/etc/nginx/sites-enabled/{default,webapp}`). Add a server block for `api.gic.indemn.ai → localhost:8002` and reload nginx. Validates ingress before customers hit it.

## Rollback procedure (if step 9 fails or 90-min hard-stop hit)

In order:
1. **Pause EC2 prod first** (set `pause-*=true` in Param Store, recreate containers OR just stop them via `docker compose stop`) — this prevents the "both stacks alive" Atlas connection-pool overlap
2. **Flip Route 53 back** to Railway public domain — change batch JSON pre-staged at `/tmp/api-gic-rollback.json` per implementation plan I.8
3. **Re-enable Railway crons:** `railway variables set PAUSE_SYNC=false PAUSE_PROCESSING=false PAUSE_AUTOMATION=false --environment production --service ...`
4. Investigate without time pressure

**Recovery floor:** Atlas snapshot from step 3 of cutover. Restore procedure documented in `docs/security.md` (committed via PR #1).

## After cutover (Phase J — 7-day soak)

- Daily monitoring of: `automation_status: failed` count, `failed_recovery_review` count (must be 0), Atlas connection-pool utilization, container restart count
- Once 7 clean days: destroy Railway services (`railway service delete api,sync,processing,automation` for both dev + prod environments), archive `craig-indemn/gic-email-intelligence` repo
- Final cleanup: drop the `gic_email_intelligence_devsoak` Mongo database (used in Phase G for parallel-test soak)

## Linear state at end of session

| ID | Status | Notes |
|---|---|---|
| DEVOPS-151 | In Progress | Parent epic |
| DEVOPS-152 | Done | A–D |
| DEVOPS-153 | Done | E |
| DEVOPS-154 | Done | F (PR #1 merged) |
| DEVOPS-155 | Done | G (validated 5 UAT Quote creations) |
| DEVOPS-156 | In Progress | H.3 + H.4 done; H.1 + H.2 outstanding (decisions owed) |
| DEVOPS-157 | Backlog → ready to move to **In Progress** when cutover starts | I — pre-prep complete, awaits PR #18 + cutover window |
| DEVOPS-158 | Backlog | J — post-cutover soak + tear-down |
| DEVOPS-159 | Done | Runner registration |

## Files / artifacts to reference on cutover day

In OS repo (`projects/gic-email-intelligence/artifacts/`):
- `2026-04-27-migration-implementation-plan.md` — per-step runbook detail (Phase I.1–I.12)
- `2026-04-27-migration-to-indemn-infrastructure-design.md` — strategic context + risk table
- `2026-04-28-phase-g-soak-handoff.md` — Phase G validation outcome + issues fixed
- This file — cutover-readiness snapshot

In migration repo:
- `docs/runbook.md` — operational playbooks (failed-automation triage, single-email re-process, etc.)
- `docs/security.md` — encryption + backup posture (Atlas snapshot recovery procedure)
- `scripts/aws-env-loader.sh` — pulls Secrets Manager + Parameter Store at deploy time

## Quick reference: prod resource map

| Resource | Identifier |
|---|---|
| Indemn AWS account | 780354157690 |
| prod-services EC2 | i-00ef8e2bfa651aaa8 (private 172.31.22.7, EIP 98.88.11.14) |
| dev-services EC2 (pre-paused dev) | i-0fde0af9d216e9182 (private 172.31.43.40, EIP 44.196.55.84) |
| Atlas project | dev-indemn (prod data lives here through Phase 2) |
| Atlas connection (PrivateLink) | dev-indemn-pl-0.mifra5.mongodb.net |
| Atlas VPC endpoint | vpce-06c18b903fea23e06 (private IP 172.31.32.102) |
| Unisoft proxy EC2 | i-0dc2563c9bc92aa0e (private 172.31.23.146, EIP 54.83.28.79) |
| Unisoft proxy SG | sg-04cc0ee7a09c15ffb (allows shared SG sg-d4163da4 on 5000+5001) |
| dev/prod-services shared SG | sg-d4163da4 |
| Amplify app | d244t76u9ej8m0 (now → indemn-ai/gic-email-intelligence) |
| Outlook add-in | gic-addin.vercel.app (Vercel project: dist) |
| GitHub repo | indemn-ai/gic-email-intelligence |
| Self-hosted runner (prod) | ip-172-31-22-7-gic, labels [self-hosted, linux, x64, prod] |
| Self-hosted runner (dev) | ip-172-31-43-40-gic, labels [self-hosted, linux, x64, dev] |
| github-actions OIDC role | arn:aws:iam::780354157690:role/github-actions-deploy |

## End-of-session metrics

- This session: ~6h continuous work
- Phases completed: F.1, F.2, F.3, G (full soak), H.3, H.4, I.1b, I.2
- AWS state changes: 5 prod secrets created, 24 prod params created, 1 Amplify rewire, 1 Amplify build verified
- PRs: #1 merged (Phase F), #17 merged (CORS fix), #18 awaiting review (SOAK_MODE)
- Live service changes: gic-addin.vercel.app deployment replaced (was broken; now points at canonical API)
- Production impact during this entire session: zero customer-visible changes

## Recent pings (next session: monitor these)

- **Slack #dev-squad thread** — replied in Dhruv's existing thread (originally about source code location for SOC 2) with the migration update + PR #18 review ask, broadcast to channel. Sent at ts `1777410154.434829` (channel `C08AM1YQF9U`). Watching for reviewer pickup. If no reply from any of Dolly / Dhruv / Rudra by mid-day next session, can re-prompt Craig (the human) on whether to escalate.

## How to resume in the next session

1. **Read this artifact first**, then `2026-04-28-phase-g-soak-handoff.md` for the soak validation context.
2. Check PR #18 status: `gh pr view 18 --repo indemn-ai/gic-email-intelligence --json reviewDecision,state`. If approved + merged → ready to plan cutover window. If still open → re-engage reviewer pickup.
3. Confirm the AWS state is intact (read-only):
   ```bash
   aws secretsmanager list-secrets --filters Key=name,Values=indemn/prod/gic-email-intelligence --query 'SecretList[].Name' --output text | tr '\t' '\n' | sort
   aws ssm get-parameters-by-path --path /indemn/prod/gic-email-intelligence --recursive --query 'Parameters[].Name' --output text | tr '\t' '\n' | sort | wc -l
   # Expect: 5 secrets, 24 params
   ```
4. Confirm runners still online: `gh api repos/indemn-ai/gic-email-intelligence/actions/runners --jq '.runners[] | {name, status}'` — both should be `online`
5. Surface remaining decisions to Craig: Datadog routing (H.1), Atlas backup tier (H.2), customer comms timing
6. Once decisions are made + PR #18 merged, pick the cutover window (low-traffic morning) and execute Phase I.1–I.12 per implementation plan.

## Soak DB cleanup (reminder)

The `gic_email_intelligence_devsoak` Mongo database still has the Phase G validation data (~30 emails, 5 successful submissions linked to UAT quotes 17373-17377). Recommend keeping until cutover succeeds, then dropping during Phase J cleanup.
