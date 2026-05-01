---
ask: "Specify the Datadog monitors that need to land before USLI quote automation goes live in prod (H.2). Configured by Dhruv via the Datadog UI; this doc captures the queries + thresholds + routing so the spec is reproducible."
created: 2026-05-01
workstream: gic-email-intelligence
session: 2026-05-01-h-prep
sources:
  - type: artifact
    description: "Implementation plan task H.2 — original spec called for 3 alerts; one was dropped per the deterministic-lookup architecture (Indemn USLI Needs Review folder no longer exists)"
  - type: codebase
    description: "DD_SERVICE=gic-email-automation-usli set on the new container in docker-compose.yml; failed_recovery_review status used by automation/recovery.py:reset_stale_automation"
---

# USLI Quote Automation — Datadog Alert Spec (H.2)

Two monitors must land BEFORE the H.5 cutover (unpause `pause-usli-automation` in prod Param Store). Per the H.2 plan rule: "alerting on a paused service is fine; alerting after unpause is too late."

PR #19 (Datadog APM wiring, merged 2026-04-30) ensures the new container `gic-email-automation-usli` reports as a separate `DD_SERVICE` to Datadog. Both monitors below scope by service tag.

## Monitor 1: USLI automation failure rate > 10% over 1h

**Type:** Metric monitor (logs-derived ratio)
**Service tag:** `service:gic-email-automation-usli`
**Window:** 1h rolling
**Threshold:** alert > 10%, warn > 5%

**Query approach** (one of two patterns depending on what telemetry already exists):

A. **Logs-driven ratio.** If the existing `gic-email-automation` service has a log-based metric for `automation_status:failed`, replicate the same query for the new service:
   ```
   sum:gic_email_automation.failed{service:gic-email-automation-usli}.as_count()
   /
   ( sum:gic_email_automation.completed{service:gic-email-automation-usli}.as_count()
   + sum:gic_email_automation.failed{service:gic-email-automation-usli}.as_count() )
   ```

B. **MongoDB-derived.** If no log metric exists yet, set up a synthetic check that periodically queries the prod Mongo and exports a metric:
   ```python
   db.emails.count_documents({
       "classification.email_type": "usli_quote",
       "automation_status": "failed",
       "automation_completed_at": {"$gte": one_hour_ago}
   })
   ```
   Datadog has built-in MongoDB integration — easier path is to add a check via the Datadog Agent already on the EC2.

**Notification:** Slack `#deployment` (matches the cutover Slack pattern in build.yml).
**Message body:**
```
USLI automation failure rate exceeded threshold ({{value}}%) over the last hour.
Service: gic-email-automation-usli
Recent failures: <link to log query>
Investigate via: docker logs gic-email-automation-usli --tail 100
Mitigation: aws ssm put-parameter --name /indemn/prod/gic-email-intelligence/pause-usli-automation --value true --overwrite
```

## Monitor 2: failed_recovery_review count > 0 (any service)

**Type:** Metric monitor (Mongo-derived) or recurring check
**Tag scope:** any (this status is set by `automation/recovery.py:reset_stale_automation` regardless of email type — it covers BOTH the existing `automation-cron` AND the new `automation-usli-cron`)
**Threshold:** alert > 0 (single occurrence pages)

**Query:**
```python
db.emails.count_documents({"automation_status": "failed_recovery_review"})
```

This catches the case where a stale claim is suspected to overlap with an existing Quote in Unisoft (the recovery loop fail-closed). Each occurrence is operationally important — it means a worker crashed mid-flight and we couldn't safely re-queue. Manual review required.

**Notification:** Same channel as Monitor 1.
**Message body:**
```
Stale-automation recovery flagged {{value}} email(s) for human review (possible duplicate Quote in Unisoft).
Query for details:
  db.emails.find({automation_status: "failed_recovery_review"}).sort({automation_completed_at:-1}).limit(5)
Resolution: inspect each, verify Quote state in Unisoft, then either re-queue (`gic emails reset <id>`)
or mark resolved manually (set automation_status to completed/failed with appropriate notes).
```

## Monitor that was dropped vs the original H.2 spec

The original plan listed a third alert: `Indemn USLI Needs Review folder count > 5`. **Dropped** per the 2026-05-01 deterministic-lookup architecture, which replaced human-triage routing with a highest-QuoteId tiebreak in `find_quote_for_usli_ref`. The folder no longer exists; nothing routes there.

## Verification before H.5

After Dhruv configures both monitors, run a synthetic test event to verify each fires:

**Monitor 1 (failure rate):** mark a test email's `automation_status` to `failed` 11 times in a 1h window. Watch for alert in Slack within 10 min of threshold breach.

**Monitor 2 (failed_recovery_review):** manually set one test email's `automation_status` to `failed_recovery_review`. Watch for alert in Slack within 5 min.

Reset the test emails after verification.

## Configuration ownership

- **Dhruv** — configures both monitors via Datadog UI before H.5 cutover.
- **Craig** — verifies via the synthetic-test pattern above before unpausing the cron.
- **No code change required** — monitors are independent of the Python codebase and live entirely in Datadog's config.

## Follow-up (post-H, K phase)

Add a Datadog dashboard for the USLI flow with:
  - Volume per hour (claimed / completed / failed counts)
  - P50/P95 cron-tick duration
  - Tier-1-hit-rate (the G.3 architecture metric — increases over time as loop-closure stamping fills)
  - Customer-copy upload count (must remain 0 — defense-in-depth, not actionable but visible)

Tracked as K.6 in the implementation plan.
