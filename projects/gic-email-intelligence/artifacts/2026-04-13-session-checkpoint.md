---
ask: "Session checkpoint — full state capture for handoff"
created: 2026-04-13
workstream: gic-email-intelligence
session: 2026-04-13a
sources:
  - type: codebase
    description: "Pipeline status, proxy debugging, Railway env vars, Amplify domain"
  - type: mongodb
    description: "Email processing status, automation results, quote ID linkage"
---

# Session Checkpoint — 2026-04-13

## What Was Done

### Pending Items (from Apr 8)
1. **Reprocess verification** — Vivian Menendez (Q:17262), Crystal Cleaning (Q:17261, Q:17263), producer code #2120 fix all confirmed working. 6 orphaned quote IDs fixed (automation_result had quote_id on email but not propagated to submission). Total AMS linked: 163 (was 138).
2. **Insights page polish** — Fixed pipeline label ("extract → classify → link"), collapsed Configuration section by default, fixed stale Data Limitations text. Deployed to Amplify.
3. **Demo preparation** — Created briefing PDF (`2026-04-13-gic-demo-briefing.pdf`), email draft for JC, full demo narrative with questions and production roadmap.

### Pipeline Recovery
- **Anthropic API credits exhausted** — all processing failed since Apr 10 (310 emails). New API key set on Railway (api, processing, automation services). Emails reset to pending and reprocessing.
- **`emails complete` fix** — now propagates `unisoft_quote_id` and `unisoft_source` to submission doc. No more backfill needed for future automation. Pushed to git, needs Railway API redeploy to take effect.

### Infrastructure
- **`gic.indemn.ai`** — pointed at main branch (Amplify domain association on `indemn.ai` with `gic` prefix). JC can access the app here.
- **`TILEDESK_DB_URI`** — changed to prod Atlas (`prod-indemn-pl-0.3h3ab.mongodb.net/tiledesk`) on the api service so JC can log in with his copilot-server credentials. GIC org `65eb3f19e5e6de0013fda310` exists in prod tiledesk, not dev.
- **RDP access** — IP `73.87.128.242` added to security group for port 3389. SSM port forward tunnel: `aws ssm start-session --target i-0dc2563c9bc92aa0e --document-name AWS-StartPortForwardingSession --parameters '{"portNumber":["3389"],"localPortNumber":["3389"]}'`. Credentials: `Administrator` / `Welcome123!`.

### Unisoft Proxy Fix (critical)
- **Root cause:** Unisoft pushed a ClickOnce app update today (3:49 PM) that changed all UAT service endpoint URLs. Old reverse-proxy domain `services.uat.gicunderwriters.co` now returns 500.
- **New URLs:**
  - IMS: `https://ins-gic-service-uat-app.azurewebsites.net/imsservice.svc`
  - Email: `https://ins-gic-emails-service-uat-app.azurewebsites.net/emailservice.svc`
  - Reports: `https://ins-gic-reports-service-uat-app.azurewebsites.net/reportingservice.svc`
  - File service: not yet checked — may also need updating
- **Fix applied:** Updated `UNISOFT_SOAP_URL` machine env var on EC2, restarted UniProxy service. Proxy is running on port 5000, verified GetQuote returns Success.
- **Activity creation verified:** `unisoft activity create --quote-id 17146 --submission-id 0 --action-id 6` works. Activity 46916 created. The automation agent inconsistently skips this step — skill/agent behavior issue, not API.

### Demo with JC (today)
- Demo completed. Transcript pending.
- Showed the pipeline, the UI, the automation results in Unisoft via RDP.
- Meeting outcomes and next steps TBD when transcript comes back.

## Current Numbers
- Emails: 4,526 (syncing live)
- Submissions: 3,796
- AMS linked: 163 (135 automation, 28 portal)
- Automation: 144 completed, 103 failed, 60% rate
- Pipeline backlog: ~298 emails still processing (API key was dead Apr 10-13)

## Open Items
1. **Pipeline backlog** — 298 emails reprocessing, should clear over next few hours
2. **Activity step inconsistency** — agent skips Step 6 (log activity) ~80% of the time. Skill needs tightening.
3. **File service endpoint** — may need URL update like IMS did (`services.uat.gicunderwriters.co/attachments/insfileservice.svc` → check new URL)
4. **Meeting transcript** — analyze when available, extract next steps and decisions
5. **Unisoft endpoint monitoring** — Unisoft can change URLs without notice. Consider adding health check that detects this.

## Key Config State

### Railway env vars (api service, development)
- `LLM_API_KEY` — updated to new Anthropic key (sk-ant-api03-TfMc...)
- `TILEDESK_DB_URI` — prod Atlas (`prod-indemn-pl-0.3h3ab.mongodb.net/tiledesk`)
- `UNISOFT_PROXY_URL` — `http://54.83.28.79:5000`

### EC2 Unisoft proxy (i-0dc2563c9bc92aa0e)
- `UNISOFT_SOAP_URL` — `https://ins-gic-service-uat-app.azurewebsites.net/imsservice.svc` (changed today)
- Service: UniProxy, startup type: Automatic, status: Running

### Amplify
- App: `d244t76u9ej8m0`
- Domain: `gic.indemn.ai` → main branch
- Previous `prod` branch exists but domain now points to `main`
