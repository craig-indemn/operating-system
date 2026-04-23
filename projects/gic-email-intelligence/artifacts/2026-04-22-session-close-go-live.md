---
ask: "Session close — production is live, full state capture for morning monitoring"
created: 2026-04-22
workstream: gic-email-intelligence
session: 2026-04-22a
sources:
  - type: codebase
    description: "20+ code changes across session, all committed and deployed"
  - type: unisoft-prod
    description: "Connectivity verified, test quote created and deleted"
  - type: railway
    description: "Dev paused, prod live, all env vars confirmed"
---

# Session Close — Production Go-Live

## Status: PRODUCTION IS LIVE

Prod processing and automation unpaused at ~10:30 PM ET Apr 22. Dev paused. First emails will process after midnight when Apr 23 emails arrive.

## What's Running

| Service | Environment | Status |
|---------|------------|--------|
| sync | prod | Running (has been syncing all day) |
| processing | prod | **LIVE** — every 5 min, no batch limit, filters to Apr 23+ |
| automation | prod | **LIVE** — every 5 min, processes agent_submission emails |
| api | prod | Running, serving gic.indemn.ai |
| sync | dev | Running (harmless) |
| processing | dev | Paused |
| automation | dev | Paused |

## Production Configuration

| Setting | Value |
|---------|-------|
| UNISOFT_PROXY_URL | http://54.83.28.79:5001 (prod) |
| UNISOFT_API_KEY | prod-84208b3... |
| UNISOFT_TASK_ACTION_ID | 70 (Review automated submission) |
| UNISOFT_ACTIVITY_ACTION_ID | 197 (Application Acknowledgement — sends email to agent) |
| PROCESSING_START_DATE | 2026-04-23 |
| indemnai user | Underwriter on all quotes |
| Cron schedule | */5 * * * * (every 5 min, both services) |
| Batch limit | None (processes all pending per tick) |

## UAT Shakeout Results (Final)

- **47 agent_submission emails** processed (Apr 21-22)
- **28 completed** (60% in UAT, ~85% expected in prod due to agent mismatch)
- **19 failed** — 11 from prod/UAT agent mismatch (will succeed in prod), 7 genuine agency gaps, 1 unsupported LOB
- **0 pipeline failures** after fixes

## Bugs Found and Fixed This Session

1. EXTRACTIONS import missing — enrichment was crashing
2. Field name mapping — Gemini Pro capitalized variants
3. S3 credentials missing on Railway automation
4. Graph API credentials missing on Railway automation
5. Linker recursion on already-linked emails
6. Batch processing didn't pick up "classified" status emails
7. Classification: quote@gicunderwriters.com "Application Request" misclassified as agent_submission (72 emails) — hard rule added
8. Period filter used last_activity_at instead of created_at
9. Agent Submissions filter matched intake_channel='agent_email' (too broad)
10. Prod API MongoDB URI was old socat proxy format
11. Denormalization gap — email automation results not syncing to submissions

## Features Built This Session

1. --assigned-to on quote create (underwriter = indemnai)
2. Task due date = same day as email received
3. Attachment category routing (application, email, loss-run, other)
4. Email export as .eml
5. Inbox folder management (create, list, move)
6. Move email on completion (--move-to flag)
7. LangSmith tracing (explicit callback for deepagent)
8. Environment-driven ActionIds (activity: 6/197, task: 40/70)
9. PROCESSING_START_DATE env var for go-forward filtering
10. UI: red failure pills with error text
11. UI: renamed filters (Automation, Email type)
12. UI: Period filter (Today/Last 2 days/This week/30 days/All time)
13. "indemn processed" folder created in production inbox
14. Matching task groups created in UAT (3=NEW BIZ, 4=WC)
15. "Review automated submission" task action created in prod (ActionId 70)

## Morning Monitoring Checklist

1. Open gic.indemn.ai — Period: Today, Email type: Agent Submissions
2. Open LangSmith — smith.langchain.com, projects gic-email-processing and gic-email-automation
3. RDP to EC2 for Unisoft prod — check NEW BIZ task queue
4. Check first few quotes: correct LOB, agency, attachments (PDF in Application folder, .eml in Email folder)
5. Check first task: [Auto] subject, due today, entered by indemnai, group NEW BIZ
6. Check the Application Acknowledgement activity fired (ActionId 197)
7. Check "indemn processed" folder — processed emails should appear there

## If Something Goes Wrong

Pause instantly — no deployment needed:
```bash
cd /Users/home/Repositories/gic-email-intelligence
railway variables --environment production -s processing --set "PAUSE_PROCESSING=true"
railway variables --environment production -s automation --set "PAUSE_AUTOMATION=true"
```

## Key URLs

- Dashboard: https://gic.indemn.ai
- LangSmith: https://smith.langchain.com
- Railway: https://railway.com/project/4011d186-1821-49f5-a11b-961113e6f78d
- RDP: `aws ssm start-session --target i-0dc2563c9bc92aa0e --document-name AWS-StartPortForwardingSession --parameters '{"portNumber":["3389"],"localPortNumber":["3389"]}'`
- Prod Unisoft login: indemnai / GIC2000undw!
