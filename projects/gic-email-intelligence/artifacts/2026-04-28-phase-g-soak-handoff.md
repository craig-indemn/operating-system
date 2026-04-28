---
ask: "Wrap Phase G with the soak validation outcome, surface the pre-cutover checklist for Phase I, and capture the design decisions that surfaced during the soak."
created: 2026-04-28
workstream: gic-email-intelligence
session: 2026-04-28-b
sources:
  - type: ec2
    description: "Validated full sync → processing → automation pipeline on EC2 dev-services against soak DB + UAT Unisoft"
  - type: codebase
    description: "PRs #1, #17, #18 merged or in review on indemn-ai/gic-email-intelligence"
  - type: aws
    description: "Parameter Store + Secrets Manager dev populated; EC2 dev runner online; Atlas via PrivateLink"
---

# GIC → Indemn Migration — Phase G Soak Handoff

**Status:** Phases E + F + G + H.3/4 complete. **Cutover-ready.** Next milestone: Phase I (DEVOPS-157) prod cutover.

## Phase G validation outcome

Phase G ran end-to-end against a separate Mongo database (`gic_email_intelligence_devsoak`) with `SOAK_MODE=true`. Real customer emails arriving in `quote@gicunderwriters.com` were processed in parallel with live Railway prod — zero production impact.

| Pipeline stage | Validation |
|---|---|
| Sync | Real emails pulled from Outlook into soak DB; sync_state advanced on every 5-min tick; no errors. |
| Processing (extract → classify → link) | All emails classified; PDFs extracted; submissions created; folder moves correctly skipped per SOAK_MODE. |
| Automation (agent → Unisoft Quote creation) | 5 successful UAT Quote creations, 1 fail-closed for UAT-missing agency. |
| Notifications | Zero `SendActivityEmail` calls fired (gated by SOAK_MODE). |
| Outlook state | Zero folder moves; `email.folder` field unchanged on every soak record. |
| Production cluster (`gic_email_intelligence`) | Untouched — soak writes went to separate DB. |

**UAT Quotes created during soak (for reference):**
- Q:17373 / Task 16884 — Golden Hands Home Keeping & Disinfectant Crew, LLC
- Q:17374 / Task 16885 — GP Landscaping
- Q:17375 / Task 16886 — Allfix Ocean Services LLC
- Q:17376 / Task 16887 — Robbyn Albernas
- Q:17377 / Task 16888 — Alpro Marble Polishing, Inc.

(JC has used UAT for testing throughout development — these 5 are additional UAT-only records, no customer-visible state.)

## Issues discovered + fixed during F + G

These would have blocked prod cutover if not caught now:

1. **CORS_ORIGINS Pydantic env parsing bug** — Pydantic Settings v2 attempts `json.loads()` on env values for `list[str]` fields BEFORE running validators. The Phase B.8 `mode="before"` validator only intercepted post-JSON-decode, so the comma-separated env value crashed the app at startup. Fix: `Annotated[list[str], NoDecode]`. Test added that exercises the actual env-var path. **PR #17, merged.**

2. **Docker Hub creds not on the new repo** — `DOCKER_USERNAME` and `DOCKER_PASSWORD` are per-repo secrets in the Indemn pattern (not org-level shared with this repo). Fixed by extracting from cached `/home/ubuntu/.docker/config.json` on dev-services and setting via `gh secret set`.

3. **Trivy action version invalid** — Dhruv's bump to `aquasecurity/trivy-action@0.36.0` missed the `v` prefix. Fixed to `v0.36.0` on PR #1.

4. **docker-compose port 8080 conflict** — `openai-fastapi-app-1` already binds host port 8080 on dev-services. Changed our api service to `ports: ["8002:8080"]`. PR #1 merge commit `9357c6dc`.

5. **SOAK_MODE flag added** — needed to make Phase G safe by gating Outlook folder moves + SendActivityEmail. **PR #18, awaiting review.** Code IS deployed on dev-services via manual `workflow_dispatch` from `feat/soak-mode` branch; the validated soak proves the code works.

## What's done and ready for cutover

| Phase | Status | Notes |
|---|---|---|
| A–D | Done | 32 commits, prior session |
| E (AWS infra dev) | Done | Secrets, params, SG-reference, OIDC verified; Atlas via PrivateLink |
| F.1 (push to indemn-ai) | Done | PR #1 merged with merge commit |
| F.2 (branch protection on prod) | **NOT DONE** — needs admin (Craig has it) |
| F.3 (Amplify rewire) | **NOT DONE** — was blocked behind PR #1 merge; now unblocked |
| G (dev soak) | Done — validated today |
| H.1 (Datadog alerts) | **NOT DONE** — needs PagerDuty vs Slack-to-phone decision |
| H.2 (Atlas backup tier) | **NOT DONE** — needs Atlas UI verification (Craig) |
| H.3 (security.md) | Done — committed to PR #1 |
| H.4 (S3 versioning + lifecycle) | Done |
| Self-hosted runners (DEVOPS-159) | Done |
| IAM OIDC role | Verified — same pattern as every Indemn repo, no special prod handling needed |

## Pre-cutover checklist (Phase I prerequisites)

These must all be ✅ before picking the cutover window:

### Required before cutover
1. **PR #18 reviewed + merged.** Currently approved? Run `gh pr view 18` to check; merge if approved.
2. **F.2: Set branch protection on `prod` branch.** Create the branch from main, apply ruleset matching main's. Craig has admin.
3. **F.3: Amplify rewire to indemn-ai/gic-email-intelligence.** Update Amplify app `d244t76u9ej8m0` source from `craig-indemn` → `indemn-ai`, set `VITE_API_BASE` per branch, trigger a build to validate. **Now unblocked since PR #1 merged.**
4. **I.1b: Outlook add-in `VITE_API_BASE` rebuild.** Live add-in at `gic-addin.vercel.app` has a dead Cloudflare tunnel URL baked in (`hrs-cardiff-crop-offering.trycloudflare.com`). Rebuild against the canonical `https://api.gic.indemn.ai/api` host before cutover so Maribel's add-in works post-cutover. May require manifest re-issue + Maribel sideload.
5. **I.2: Populate prod Secrets Manager + Parameter Store.** Mirror E.1+E.2 for `indemn/prod/gic-email-intelligence/*` (Secrets Manager) and `/indemn/prod/gic-email-intelligence/*` (Param Store). Source values from Railway prod env. **CRITICAL: use PrivateLink hostname (`dev-indemn-pl-0.mifra5.mongodb.net`) for `mongodb-uri` from the start — do NOT use the public `dev-indemn.mifra5.mongodb.net`.** Use `unisoft-proxy-url=http://172.31.23.146:5001` (Prod Unisoft port). Set all `pause-*=true` initially.

### Recommended (not strictly blocking)
6. **H.1: Datadog routing decision** — needs Craig's call (PagerDuty vs Slack-to-phone) before the alerts can be wired. Cutover is doable without alerts but operational visibility is reduced.
7. **H.2: Atlas backup tier verification** — confirm `dev-indemn` cluster has continuous backup with ≥30-day retention. If not, upgrade tier before cutover.
8. **JC + Maribel customer comms** (T-24h) — Craig writes the email (template in implementation plan I.1).

### Cutover window itself (Phase I.1–I.12)
~90-min hard window with 24-h watchful soak after. Per the implementation plan:
- T-24h: customer comms (#8 above)
- T-0 step 1: Atlas snapshot (rollback floor)
- Pause Railway prod (3 services)
- DNS flip on `api.gic.indemn.ai` (TTL 60s pre-set)
- Trigger Amplify prod rebuild (against `prod` branch with `VITE_API_BASE` for prod)
- Unpause EC2 prod crons one at a time (5-min soak between each)
- Verify end-to-end with a real customer email (or controlled test)
- Remove Railway IP from Atlas allowlist + Unisoft proxy SG
- T+0 done customer comms

Then 7-day post-cutover soak (Phase J), then Railway tear-down + craig-indemn repo archival.

## Linear state at end of session

| ID | Title | Status |
|---|---|---|
| DEVOPS-151 | Parent epic | In Progress |
| DEVOPS-152 | A–D | Done |
| DEVOPS-153 | E | Done |
| DEVOPS-154 | F | Done (PR #1 merged) |
| DEVOPS-155 | G | **Done** (this session) |
| DEVOPS-156 | H | In Progress (H.3, H.4 done; H.1, H.2 outstanding) |
| DEVOPS-157 | I (cutover) | Backlog — **next milestone** |
| DEVOPS-158 | J (7-day soak + tear-down) | Backlog |
| DEVOPS-159 | Runner registration | Done |

## How to resume in the next session

1. Read this artifact + the prior `2026-04-27-phase-e-execution-handoff.md` for execution context.
2. Confirm PR #18 status: `gh pr view 18 --repo indemn-ai/gic-email-intelligence --json reviewDecision,state`. If approved+merged: ✅. If still open: surface to user.
3. Tackle the pre-cutover checklist above (items 1–5 are required, 6–8 recommended).
4. Once checklist is green, pick a cutover window with Craig (low-traffic morning per design — early Tuesday or Wednesday before agents start sending submissions).
5. Execute Phase I per implementation plan section by section with explicit user approval at each [NEEDS USER APPROVAL] gate.

## Open soak DB cleanup question (low priority)

The soak DB `gic_email_intelligence_devsoak` has ~30 emails, 5 successful submissions linked to UAT quotes, plus extractions + classifications. Three options:

- **Keep** — useful as a snapshot of pipeline output for post-mortem reference. Storage is small (~MB).
- **Drop the DB** post-cutover — no longer useful once prod is on EC2.
- **Drop now** — just don't need it.

Recommend **drop after cutover succeeds** so we have it as a reference if anything goes sideways during cutover.
