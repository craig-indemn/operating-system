---
ask: "Handle multiple live dev-squad requests: voice-service dev restart, conversation-service prod slack webhook routing wrong, intake-manager comparative rater broken for Ben, Dependabot PRs blocked because Dhruv is OOO"
created: 2026-04-17
workstream: devops
session: 2026-04-17-a
sources:
  - type: slack
    description: "DMs with Dolly (voice-service), Rudra (conversation-service + intake-manager), dev-squad channel thread about Dependabot PRs"
  - type: aws
    description: "SSM Run Command on dev-services and prod-services EC2s; Secrets Manager read/write on indemn/prod/shared/*, create on indemn/prod/services/operations-api/whitepaper-webhook-url"
  - type: github
    description: "Ruleset 13442013 inspection; repos: voice-service, operations_api, intake-manager, conversation-service; PRs opened: operations_api #118, voice-service #59"
  - type: mongodb
    description: "(none — strictly infrastructure + code work today)"
---

# Dev-Squad Incident Response — 2026-04-17

Four separate incidents handled in one session. Summary of root causes, fixes, and open follow-ups.

## 1. voice-service dev: Cartesia returning empty data

**Reported by:** Dolly (DM) — "data from cartesia api, in dev voice-service the data returned is 0"

**Initial fix:** Restarted `voice-service` on dev-services EC2. Temporarily resolved because Redis's poisoned cache entry for `/voices/settings/cartesia?service=tts` expired on restart; the endpoint repopulated with real data (TTL ~1h).

**Actual root cause (after deeper dig):** Bug in `services/cartesiaService.js` — Cartesia's `/voices` endpoint (at `Cartesia-Version: 2024-06-10`) returns a plain JSON array, not `{ data: [...] }`. The code at line 659 did `cartesiaResponse.data || []`, which is always `[]` on an array (`.data` is undefined on arrays). Every cache-miss fetch silently returned zero voices.

**Why unfiltered queries looked healthy:** Redis had stale cached payloads for `/voices?limit=20` from before the bug manifested (or from a code path that returned the wrapped shape). Cache-miss queries (any new filter combo: accent, gender, pagination) hit the broken parse → empty → then Dolly's earlier "skip cache for empty data response" branch prevented re-caching, making the failure permanent for new keys.

**Verification:** Reproduced locally with dev's Cartesia creds via a 30-line Node.js script mirroring the exact axios call. Current code → `rawDataCount: 0`. Fix applied → `rawDataCount: 371` with valid records. Bug is universal, not dev-specific.

**PR:** https://github.com/indemn-ai/voice-service/pull/59 — one-line fix: `Array.isArray(cartesiaResponse) ? cartesiaResponse : (cartesiaResponse.data || [])`. Reviewer: dolly45.

**Latent issues noted in PR description (not fixed here):**
- Cartesia ignores `limit` at this API version (returns all 371 records regardless)
- Cartesia has no `accent` field on voice records, so the `accent` filter param is a no-op — UI lies if it advertises accent filtering
- Post-filter logic only covers `language` and `gender`, not `accent`

## 2. conversation-service prod: error alerts posting to #whitepaper-requests

**Reported by:** Rudra (DM, 03:13 ET) — "We need to change SLACK_WEBHOOK_URL / ERROR_SLACK_WEBHOOK_URL on conversation-service to the prod errors slack webhook"

**Verification:** Queried prod `utility-service-app-1` container env + cross-referenced Slack channel histories:
- Webhook `B09GPQTBZ5H` → posts to **#whitepaper-requests** (confirmed via recent messages in channel)
- Webhook `B05A5E51VKK` → posts to **#prod-errors** (confirmed same way)
- Prod conversation-service had both `SLACK_WEBHOOK_URL` and `ERROR_SLACK_WEBHOOK_URL` loading from `indemn/prod/shared/slack-webhook-url` — value was `B09GPQTBZ5H` (whitepaper)

**Root cause timeline:**
- 2026-03-20 (Dhruv, commit `4646a94`): rewrote conversation-service's `aws-env-loader.sh` to load `ERROR_SLACK_WEBHOOK_URL` from `shared/slack-webhook-url`
- 2026-03-23 04:33 ET (whoever): value of `indemn/prod/shared/slack-webhook-url` flipped from `B05A5E51VKK` (prod-errors) → `B09GPQTBZ5H` (whitepaper-requests), likely to support operations_api whitepaper flow
- 2026-04-08 through 2026-04-12: conversation-service redeployed in prod, picked up the new loader + new secret value. 57 error alerts routed to #whitepaper-requests instead of #prod-errors from 2026-04-12 onward

The shared secret was overloaded: operations_api used it as the whitepaper post webhook, while conversation-service + 5 other services used it as the error webhook. Flipping the value broke one consumer to serve the other.

**Fix (4 steps, 3 completed):**
1. ✅ Created new secret `indemn/prod/services/operations-api/whitepaper-webhook-url` with `B09GPQTBZ5H` value (for operations_api's dedicated whitepaper use)
2. ✅ Opened PR `indemn-ai/operations_api#118` to read `WHITEPAPER_WEBHOOK_URL` from the dedicated secret. Reviewer: Rudra9214. Pending merge + deploy.
3. ✅ Restored `indemn/prod/shared/slack-webhook-url` to `B05A5E51VKK` (rolled back from AWSPREVIOUS, which Secrets Manager preserves)
4. ✅ Redeployed conversation-service via workflow_dispatch on `prod` branch → `utility-service-app-1` now shows both webhook env vars pointing at `B05A5E51VKK`. operations_api still running on cached env (pre-restore) so whitepaper posts keep routing correctly until PR #118 deploys.

**Verification:** Post-deploy, zero "Authorization token failed" or misrouted error alerts in logs. Runtime verification waits on next organic conversation-service error or Ben retrying a comparative rater quote.

## 3. intake-manager (UG Portal) prod: Ben's comparative rater returning nothing

**Reported by:** Rudra (indirectly, via George Remmer's DM to Craig asking about Ben's screenshot of the rater failing) — "make env only gave me 4 vars, and Ben's comparative rater for UG is broken"

**Initial misdirection:** Found typo `NATIONWaIDE_CONSUMER_SECRET` in `/opt/Intake-manager/.env` on copilot-prod. Proposed fixing, then Craig pushed back correctly: the typo isn't used (code reads `consumer_secret` via `NATIONWIDE_` env_prefix from pydantic_settings, so the typo'd key never resolves) and the real issue hadn't been verified.

**Actual root cause (after pulling logs):** 57 "Authorization token failed" errors from 2026-04-15 onward on `validate_cl_address` calls. Token exchange succeeded (client got a Bearer token from Nationwide's identity endpoint) but the downstream API call got rejected with `{ "message": "Authorization token failed." }`. URL mismatch:
- `NATIONWIDE_ENVIRONMENT=prod` → `config.py` uses `api.identity.nationwide.com` (prod identity)
- `NATIONWIDE_API_BASE_URL=https://api-stage.nationwide.com` → actual API calls to stage
- Prod-issued token sent to stage API → rejected

**Regression date:** `.env` last modified 2026-04-14 13:39 UTC. `.env.save` backup (from 2026-03-06) has `NATIONWIDE_ENVIRONMENT=stage` — someone flipped to `prod` on 2026-04-14 without updating the API base URL.

**Intent confirmation:** Rudra confirmed in DM: "only Nationwide should be pointing to stage, others are still on prod."

**Fix (executed with Craig's explicit approval):**
1. Backed up `/opt/Intake-manager/.env` to `.env.bak-2026-04-17`
2. `sed -i 's/^NATIONWIDE_ENVIRONMENT=prod$/NATIONWIDE_ENVIRONMENT=stage/'`
3. `docker compose up -d --force-recreate backend` → now running with `NATIONWIDE_ENVIRONMENT=stage` matching the stage API URL
4. Zero new auth failures in logs since restart (vs 57 in prior 96h)

**Also discovered (not fixed):** intake-manager's prod deploy doesn't use `aws-env-loader.sh` — it uses a hand-maintained `/opt/Intake-manager/.env` file on the host (that's how the regression got introduced). The repo has `scripts/aws-env-loader.sh` but it's incomplete (loads ~17 vars vs ~40 app vars actually needed). Migration to AWS-managed env is a separate follow-up.

## 4. Dependabot PRs blocked — org-level ruleset requires approval from reviewer with write access

**Reported by:** Rudra posted 3 Dependabot PRs (llm-evaluate #36, ug-apis #10, wedding-ai-agent #13) requesting review. Craig approved all three but all remained `mergeStateStatus: BLOCKED` / `reviewDecision: REVIEW_REQUIRED`. Kyle (Ganesh actually — see below) pushed to expedite because SLA breach Friday.

**Root cause:** Org ruleset `13442013` requires 1 approving review from a reviewer with write access. Craig + Dolly are both org members with `pull` (read-only) access on these repos — their approvals don't satisfy the rule. Dhruv is the only regular write-access approver, and he's OOO.

**Short-term fix (drafted as Slack message with step-by-step instructions):** Kyle Geoghan (kwgeoghan on GitHub, UFK4DNNHG on Slack) is an org owner and can admin-bypass the ruleset via GitHub's "Merge without waiting for requirements to be met" checkbox. Posted detailed walkthrough as threaded-reply-with-broadcast in #dev-squad.

**Also got the Slack tag wrong on first attempt** — initially tagged `U040W167JP6` (Ganesh Iyer) assuming he was Kyle, Craig caught it and fixed. Kyle Geoghan = `UFK4DNNHG` in Slack, `kwgeoghan` on GitHub.

**Longer-term fix (drafted as a Claude Code prompt for Kyle):** Create `pr-approvers` team with `push` permission on all org repos, add `craig-indemn`, `Rudra9214`, `dolly45` as members. Then their approvals count toward the ruleset's required-review rule and Dhruv isn't a SPOF for Dependabot PRs. Kyle to execute via his own Claude Code session.

## Key artifacts

- **operations_api PR #118** — https://github.com/indemn-ai/operations_api/pull/118
- **voice-service PR #59** — https://github.com/indemn-ai/voice-service/pull/59
- **New secret** `indemn/prod/services/operations-api/whitepaper-webhook-url` (value = whitepaper webhook `B09GPQTBZ5H`)
- **Backup file** `/opt/Intake-manager/.env.bak-2026-04-17` on copilot-prod

## Open follow-ups

1. PR #118 review + merge + deploy → then operations_api reads from dedicated whitepaper secret (removes dependency on cached env)
2. PR #59 review + merge + deploy + Redis flush → voice-service Cartesia data flow restored
3. Kyle executes the `pr-approvers` team setup → long-term unblock of Dependabot PRs
4. Kyle admin-bypass merges the 3 Dependabot PRs (llm-evaluate #36, ug-apis #10, wedding-ai-agent #13) → OneLeet alerts cleared before SLA breach
5. intake-manager env still hand-maintained on copilot-prod → migrate to AWS-managed via aws-env-loader (repo has the script but incomplete + not wired into deploy)
6. voice-service latent issues: Cartesia `limit` ignored, `accent` filter no-op at this API version — either upgrade `Cartesia-Version` or adjust UI claims
7. `indemn/dev/shared/slack-webhook-url` has the same overloaded-secret footgun in dev — likely also pointing at a non-errors webhook and 6 dev services are misrouting. Not urgent (dev) but worth aligning with the prod fix after PR #118 lands.
