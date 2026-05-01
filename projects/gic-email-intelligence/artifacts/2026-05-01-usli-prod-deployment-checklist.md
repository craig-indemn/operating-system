---
ask: "Self-contained checklist for the USLI quote automation production rollout. Designed for a fresh Claude session — minimal context required to execute, all key IDs/paths inline. Pre-staged work documented so the new session can skip what's already done."
created: 2026-05-01
workstream: gic-email-intelligence
session: 2026-05-01-h-prep
status: pre-staged, awaiting cutover
sources:
  - type: artifact
    description: "Implementation plan task H.0–H.6 (2026-04-29-usli-quote-automation-implementation-plan.md) — original spec; this checklist captures what's pre-staged + what's left"
  - type: artifact
    description: "Datadog alert spec (2026-05-01-usli-datadog-alerts-spec.md) — Dhruv configures via UI"
---

# USLI Quote Automation — Production Deployment Checklist

**Goal:** Activate the USLI quote-response automation in prod. The single-flip moment is `aws ssm put-parameter ... pause-usli-automation false`. Everything else is pre-staged.

**Reading order for fresh session:**
1. This checklist (you're here) — execution
2. `2026-04-29-usli-quote-automation-design.md` — what the system does (skim if needed)
3. `2026-05-01-usli-deterministic-lookup-architecture.md` — Tier 1/2/3 lookup model
4. `2026-04-29-usli-quote-automation-implementation-plan.md` — the full plan if a step needs context

## Identifiers (paste-ready)

```
GitHub:
  Repo:          indemn-ai/gic-email-intelligence
  PR:            https://github.com/indemn-ai/gic-email-intelligence/pull/23
  Branch:        feat/usli-quote-automation
  Latest SHA:    655a950 (28 commits, ~3878 +/27 -, 30 files)
  Reviewers:     dolly45, dhruvrajkotia
  Linear:        DEVOPS-162

AWS:
  Account:       780354157690
  Region:        us-east-1
  Prod EC2:      i-00ef8e2bfa651aaa8 (prod-services)
  Dev EC2:       i-0fde0af9d216e9182 (dev-services)
  Proxy EC2:     i-0dc2563c9bc92aa0e (Windows; UAT proxy port 5000, Prod proxy port 5001)

Mongo:
  Cluster:       dev-indemn-pl-0.mifra5.mongodb.net (PrivateLink)
  Prod DB:       gic_email_intelligence
  Dev sandbox:   gic_email_intelligence_devsoak

Param Store (prod, all SET as of 2026-05-01):
  /indemn/prod/gic-email-intelligence/usli-quote-action-id      = 67
  /indemn/prod/gic-email-intelligence/usli-quote-letter-name    = "USLI Quote"
  /indemn/prod/gic-email-intelligence/pause-usli-automation     = true   ← flip to false at GO LIVE
  /indemn/prod/gic-email-intelligence/automation-start-date     = 2026-04-29T22:50:00Z (existing)
  /indemn/prod/gic-email-intelligence/pause-automation          = false  (existing — global cron is running)
  /indemn/prod/gic-email-intelligence/soak-mode                 = false  (existing — production)

Customer mailbox:
  Account:       quote@gicunderwriters.com
  New folder:    "Indemn USLI Processed" (created 2026-05-01)

Gmail draft (G.5 customer comms):
  draftId:       r5499973616452698529
  Account:       craig@indemn.ai
  To:            jcdp@gicunderwriters.com
  Edit before send: replace [REPLACE WITH DATE] with the actual launch date

Datadog:
  Spec:          projects/gic-email-intelligence/artifacts/2026-05-01-usli-datadog-alerts-spec.md
  Owner:         Dhruv (UI config)
  Two monitors:  failure-rate > 10% over 1h; failed_recovery_review > 0
```

## Pre-staged (✅ done — do NOT redo)

| Item | Status | Verification |
|---|---|---|
| Prod Param Store: `usli-quote-action-id=67`, `usli-quote-letter-name="USLI Quote"`, `pause-usli-automation=true` | ✅ | `aws ssm get-parameters --names .../usli-quote-action-id .../usli-quote-letter-name .../pause-usli-automation` |
| Prod customer mailbox folder `Indemn USLI Processed` | ✅ | Visible in JC's Outlook under Inbox |
| Prod `unisoft_agents` collection | ✅ 2,898 agents (synced 4/22, fine) | `db.unisoft_agents.countDocuments({})` against prod DB |
| Prod proxy `GetQuotesForLookupByCriteria` smoke test | ✅ Returns Crown Park results | See `2026-05-01-usli-prod-proxy-smoke.log` if archived |
| Gmail draft to JC | ✅ Saved as draft `r5499973616452698529` | `gog gmail drafts get r5499973616452698529 --account=craig@indemn.ai` |
| `aws-env-loader.sh` PARAM_MAP entries | ✅ Already on feature branch (lines 242-245) | grep `usli` `scripts/aws-env-loader.sh` |
| Datadog alert spec | ✅ Spec at `2026-05-01-usli-datadog-alerts-spec.md` | Dhruv configures via UI |
| UAT validation in dev-services | ✅ 2/3 emails processed end-to-end (Q:17379, Q:17380), 1 legitimate fail | See run logs in commits `702ebd9`, `655a950` |

## Hard gates (verify BEFORE starting H.3)

```bash
# Gate 1: DEVOPS-158 must be Done (target ~2026-05-06)
linearis-proxy.sh issues list --filter '{"id":{"eq":"DEVOPS-158"}}' --json | jq -r '.[].state'
# Expected: "Done". If "In Progress", STOP — H.3 deploys are blocked until soak completes.

# Gate 2: PR #23 must be approved + merged to main
gh pr view 23 --repo indemn-ai/gic-email-intelligence --json state,reviewDecision
# Expected: state="MERGED", reviewDecision="APPROVED"

# Gate 3: Datadog monitors configured (Dhruv) + verified
# Verify by checking the Datadog UI for "gic-email-automation-usli" monitors.
# Run synthetic-test pattern from 2026-05-01-usli-datadog-alerts-spec.md to confirm they fire.

# Gate 4: prod-services healthy
aws ssm send-command --instance-ids i-00ef8e2bfa651aaa8 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker ps --filter name=gic-email --format \"table {{.Names}}\\t{{.Status}}\""]' \
  --query 'Command.CommandId' --output text
# Expected: 4 containers Up — gic-email-{api,sync,processing,automation}
```

If ANY gate is red, do not proceed.

## H.3 — Deploy to prod-services

```bash
# 1. Push main → prod (this is the prod deploy trigger)
cd /Users/home/Repositories/gic-email-intelligence-migration   # or any worktree with the indemn remote
git fetch indemn
git push indemn indemn/main:prod                                # standard convention; OR open a "prod" branch PR
# build-prod.yml fires on push-to-prod, builds :prod tag, deploys to prod-services
```

```bash
# 2. Watch the build
gh run list --workflow=build-prod.yml --repo indemn-ai/gic-email-intelligence --limit 3
gh run watch <run-id> --repo indemn-ai/gic-email-intelligence --interval 15 --exit-status
```

```bash
# 3. Verify the new container started PAUSED
aws ssm send-command --instance-ids i-00ef8e2bfa651aaa8 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker ps --filter name=gic-email --format \"table {{.Names}}\\t{{.Status}}\""]' \
  --query 'Command.CommandId' --output text
# Expected: 5 containers — including new gic-email-automation-usli

aws ssm send-command --instance-ids i-00ef8e2bfa651aaa8 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker logs gic-email-automation-usli --tail 5"]' \
  --query 'Command.CommandId' --output text
# Expected: "USLI automation paused via PAUSE_USLI_AUTOMATION=true. Skipping tick."
```

If the new container is NOT in the paused-skipping-tick state, STOP and investigate before unpause.

## H.4 — Verify Datadog alerts firing on synthetic events

Per the alert spec, manually trigger each monitor's threshold once and confirm Slack notification arrives within 10 min.

**Monitor 1 — failure rate:** mark a test email as `automation_status: failed` 11 times in a 1h window.

```python
# Inside prod gic-email-api container:
from gic_email_intel.core.db import get_sync_db
from datetime import datetime, timezone
db = get_sync_db()
# Pick 11 throwaway test emails (oldest USLI emails are fine — they'll be reset after)
ids = [e["_id"] for e in db.emails.find({"classification.email_type": "usli_quote"}, {"_id": 1}).sort("received_at", 1).limit(11)]
db.emails.update_many({"_id": {"$in": ids}}, {"$set": {"automation_status": "failed", "automation_completed_at": datetime.now(timezone.utc), "automation_result": {"error": "synthetic test for monitor 1"}}})
print(f"Marked {len(ids)} test emails as failed; expect Datadog alert within 10 min")
```

After alert fires, RESET those emails:
```python
db.emails.update_many({"_id": {"$in": ids}}, {"$unset": {"automation_status": "", "automation_completed_at": "", "automation_result": ""}})
```

**Monitor 2 — failed_recovery_review:** mark one email's `automation_status` to `failed_recovery_review`. Reset after.

```python
target = db.emails.find_one({"classification.email_type": "usli_quote"}, sort=[("received_at", 1)])
db.emails.update_one({"_id": target["_id"]}, {"$set": {"automation_status": "failed_recovery_review", "automation_recovery_note": "synthetic test for monitor 2"}})
# Expect Slack alert within 5 min
db.emails.update_one({"_id": target["_id"]}, {"$unset": {"automation_status": "", "automation_recovery_note": ""}})
```

If either alert does NOT fire, STOP and re-engage Dhruv before H.5.

## H.5 — Send T-0 customer comms + GO LIVE

```bash
# 1. Edit the date placeholder in the JC draft
gog gmail drafts get r5499973616452698529 --account=craig@indemn.ai > /tmp/jc_draft.txt
# Edit /tmp/jc_draft.txt to replace [REPLACE WITH DATE] with the actual date
# Then update the draft:
gog gmail drafts update r5499973616452698529 --account=craig@indemn.ai \
  --to "jcdp@gicunderwriters.com" \
  --subject "GIC USLI Quote Automation — Launching Today" \
  --body-file /tmp/jc_draft_edited.txt

# 2. Send the draft
gog gmail drafts send r5499973616452698529 --account=craig@indemn.ai
```

```bash
# 3. THE flip — go live
aws ssm put-parameter \
  --name /indemn/prod/gic-email-intelligence/pause-usli-automation \
  --value false --overwrite

# Settings reload per cron tick (~15 min interval). New state takes effect on next tick.
```

```bash
# 4. Watch first tick — confirm processing starts
aws ssm send-command --instance-ids i-00ef8e2bfa651aaa8 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker logs gic-email-automation-usli --tail 30"]' \
  --query 'Command.CommandId' --output text
# Expected: "X email(s) pending automation\nFiltering for email type: usli_quote\n--- Email 1/X ---..."
# (Or "No emails pending automation" if the queue is empty when the tick fires)
```

## H.6 — 24h post-cutover watch

Monitor (loose schedule — every 4h for first 24h):

```bash
# Failure rate
aws ssm send-command --instance-ids i-00ef8e2bfa651aaa8 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker exec gic-email-api python -c \"from gic_email_intel.core.db import get_sync_db; from datetime import datetime, timedelta, timezone; db=get_sync_db(); cutoff=datetime.now(timezone.utc)-timedelta(hours=24); c=db.emails.count_documents({\\\"classification.email_type\\\":\\\"usli_quote\\\",\\\"automation_completed_at\\\":{\\\"$gte\\\":cutoff}}); f=db.emails.count_documents({\\\"classification.email_type\\\":\\\"usli_quote\\\",\\\"automation_status\\\":\\\"failed\\\",\\\"automation_completed_at\\\":{\\\"$gte\\\":cutoff}}); print(f\\\"24h: {c} processed, {f} failed ({100*f/c if c else 0:.1f}%)\\\")\""]' \
  --query 'Command.CommandId' --output text

# Customer-copy uploads (must remain 0 — defense-in-depth)
# Check Unisoft attachments via the proxy or sample a few Quotes manually

# Folder counts in customer mailbox
# Compare "Indemn USLI Processed" count vs "Indemn - Processing" + Inbox

# Datadog: watch the 2 monitors
```

## ROLLBACK — if something goes wrong post-go-live

**Hard pause (under 1 min, no redeploy):**
```bash
aws ssm put-parameter \
  --name /indemn/prod/gic-email-intelligence/pause-usli-automation \
  --value true --overwrite
# Settings reload per tick — within 15 min the cron stops processing.
```

**Immediate hard pause (no wait):**
```bash
aws ssm send-command --instance-ids i-00ef8e2bfa651aaa8 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker stop gic-email-automation-usli"]' \
  --query 'Command.CommandId' --output text
# Container stays stopped until manually restarted; no risk of further processing.
```

**Full rollback to pre-feature `:prod` image** (if the feature breaks the existing flow somehow — unlikely since USLI is additive):
```bash
# Roll prod back to the pre-PR-23 SHA
cd /Users/home/Repositories/gic-email-intelligence-migration
git fetch indemn
# The previous prod tip was 6d40b81 per the cutover handoff. Verify the actual previous SHA:
git log --oneline indemn/prod -5
# Then push the pre-PR SHA back:
git push indemn <previous-prod-sha>:prod --force-with-lease
# build-prod.yml fires, builds + deploys the rollback image. The new automation-usli-cron
# container will exit because docker-compose.yml on the rolled-back image doesn't reference it.
```

**Note:** the pause flag is the right move 99% of the time. Full rollback is a last resort — the existing `gic-email-automation` cron and the rest of the prod system would also roll back, which is heavier than necessary if the bug is just in the USLI flow.

## Backfill — post-cutover (after H.6 stable for 24h)

### B1. K.8 — backfill `Submission.ConfirmationNo` on ~7 historical USLI Quotes

These are Mongo submissions with `unisoft_quote_id != null` whose Unisoft Submission has `ConfirmationNo` null. The deterministic-lookup loop closure works going forward only; this fills the legacy gap so Tier 1 can find them.

```python
# Inside prod gic-email-api container:
from gic_email_intel.core.db import get_sync_db
import os, httpx
db = get_sync_db()
proxy = os.environ["UNISOFT_PROXY_URL"].rstrip("/")
key = os.environ["UNISOFT_API_KEY"]
headers = {"X-Api-Key": key, "Content-Type": "application/json"}

candidates = list(db.submissions.find({
    "intake_channel": "usli_retail_web",
    "unisoft_quote_id": {"$ne": None},
    "reference_numbers": {"$exists": True, "$ne": []},
}, projection={"reference_numbers": 1, "unisoft_quote_id": 1, "named_insured": 1}))

print(f"Candidates: {len(candidates)}")
for s in candidates:
    quote_id = s["unisoft_quote_id"]
    ref = s["reference_numbers"][0]
    # Fetch existing submissions on this quote
    r = httpx.post(f"{proxy}/api/soap/GetSubmissions", json={"QuoteId": quote_id}, headers=headers, timeout=30)
    subs = r.json().get("Submissions") or []
    for sub in subs:
        if sub.get("CarrierNo") == 2 and not sub.get("ConfirmationNo"):
            print(f"Q:{quote_id} Sub:{sub['SubmissionId']} ({s.get('named_insured', '?')[:30]}) → stamp {ref}")
            sub["ConfirmationNo"] = ref
            r2 = httpx.post(f"{proxy}/api/soap/SetSubmission",
                            json={"PersistSubmission": "Update", "Submission": sub},
                            headers=headers, timeout=30)
            print(f"  → {r2.json().get('_meta', {}).get('ReplyStatus')}")
            break
```

Run this script via `docker exec gic-email-api python /tmp/k8_backfill.py` once. Idempotent — re-runs are safe (only stamps null-ref Submissions).

### B2. Cutover-window stranded emails (~6 from 2026-04-29 21:10–22:50Z)

Pre-cutover-cutoff USLI emails that were never automated. Process via one-shot with a temporary lower start date:

```bash
aws ssm send-command --instance-ids i-00ef8e2bfa651aaa8 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker exec -e AUTOMATION_START_DATE=2026-04-29T21:00:00Z gic-email-automation-usli python -m gic_email_intel.cli.main automate run --type usli_quote --max 10"]' \
  --query 'Command.CommandId' --output text
```

The temporary env override only applies to this exec — the persistent container env stays at `2026-04-29T22:50:00Z`.

### B3. Pre-cutover historical USLI emails (hundreds-to-thousands going back to project inception)

**Recommendation: do NOT backfill.** Each backfilled email fires `SendActivityEmail` to the retail agent — confusing for old quotes. The Unisoft audit-trail Quote isn't valuable enough to justify it.

If JC asks for specific historical ones, run them one-shot via the B2 pattern (lower the start_date temporarily).

## Outstanding human-blockers as of 2026-05-01

These are NOT in your control as a Claude session:

- **Dolly + Dhruv approve PR #23** — needs a human nudge if not acknowledged
- **DEVOPS-158 closes** — 7-day soak that started 2026-04-29 22:50 UTC, target ~2026-05-06
- **Dhruv configures Datadog monitors** per the spec doc

## When to stop and ask

Stop and check with Craig if:
- Hard gates 1–4 are not all green
- Datadog synthetic tests don't fire
- First post-go-live tick produces > 30% failures
- Anything looks unfamiliar in production state

The pause flag is your safety net — flip it at any sign of trouble. Settings reload per tick means you have under 15 min for the system to stop processing, and `docker stop` is instant.
