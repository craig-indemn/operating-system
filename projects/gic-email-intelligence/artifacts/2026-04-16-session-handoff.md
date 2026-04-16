---
ask: "Comprehensive handoff prompt for next session — full context transfer"
created: 2026-04-16
workstream: gic-email-intelligence
session: 2026-04-16a
sources:
  - type: codebase
    description: "GIC email intelligence repo + OS project files"
  - type: google-doc
    description: "JC meeting transcript Apr 13"
---

# Session Handoff — 2026-04-16

Copy this entire block as the prompt for the next session:

---

`/project gic-email-intelligence`

## Context

This is the GIC Email Intelligence project — an end-to-end system that connects GIC Underwriters' Outlook inbox (quote@gicunderwriters.com) to their Unisoft AMS. The pipeline syncs emails, extracts data from PDFs, classifies email types, links emails to applicants, and automates Quote ID creation in Unisoft via a deepagent.

**Where we are (2026-04-16):**
- Demo with JC + Mike Burke completed 2026-04-13. Positive response.
- System live in dev against Unisoft UAT. Sync every 5 min, processing every 5 min, automation every 15 min.
- ~4,500 emails processed, 163 linked to AMS (135 automation + 28 portal), 60% automation rate on new applications.
- **Heading to production rollout** with a defined 10-step plan and human-in-the-loop task system.
- **Pivot after quotes:** endorsements inbox becomes next priority. USLI development paused (portal changing end of month).

**Read these files IN ORDER before doing anything:**

### 1. Project state
- `projects/gic-email-intelligence/INDEX.md` — the Status section at the top has the current plan, decisions, and production rollout steps. Read first ~80 lines.

### 2. Most recent artifacts (2026-04-13 through 2026-04-16)
- `projects/gic-email-intelligence/artifacts/2026-04-14-meeting-summary.md` — decisions from the JC/Mike demo, action items split by owner
- `projects/gic-email-intelligence/artifacts/2026-04-14-followup-email.md` — the email sent to JC + Mike with the production rollout plan
- `projects/gic-email-intelligence/artifacts/2026-04-13-gic-demo-briefing.md` — the briefing document JC received (also as PDF)
- `projects/gic-email-intelligence/artifacts/2026-04-13-session-checkpoint.md` — full state capture from 2026-04-13: proxy fix, pipeline recovery, config state

### 3. Earlier context
- `projects/gic-email-intelligence/artifacts/2026-04-08-data-snapshot.md` — complete data picture: email counts by type, extraction coverage, AMS linkage breakdown
- `projects/gic-email-intelligence/artifacts/2026-04-07-agency-verification.md` — 73 automation failures investigated. 37 agencies confirmed missing in UAT. These are the agencies JC may or may not have in production — the answer is still TBD.
- `projects/gic-email-intelligence/artifacts/2026-04-07-demo-readiness-plan.md` — the 4 workstreams, success criteria, "no ad-hoc processing" principle

## What's Next

The demo with JC and Mike is done. We have meeting notes with their decisions and action items. **The production rollout plan still needs to be developed with the user** — read the meeting summary and follow-up email, then work through the plan together. The user's thinking may have evolved since the meeting.

**Key sources to read before planning:**
- `artifacts/2026-04-14-meeting-summary.md` — decisions and action items from the JC meeting
- `artifacts/2026-04-14-followup-email.md` — the recap sent to JC + Mike with what Craig said he'd do

**Do not assume the plan.** Read the sources, understand what was agreed, then discuss with the user what they want to tackle and in what order. Things like dependencies, sequencing, and parallel work are conversations to have — not conclusions to present.

After the quotes inbox work, endorsements are the next domain. Mike Burke will provide a list of rule-based "no-brainer" endorsements. USLI development is paused pending their portal change. Details in the meeting summary.

## The Processing Pipeline (understand how data flows)

Read these files in the GIC repo (`/Users/home/Repositories/gic-email-intelligence/`):

### Core pipeline
- `src/gic_email_intel/agent/harness.py` — THE PIPELINE. `process_email()` does: extract → classify → link → enrich. Has deterministic classifier hard rules, submission enrichment from extractions, carrier response skip optimization. Understand `_enforce_classification_rules()` and `_enrich_submission_from_extractions()`.
- `src/gic_email_intel/agent/extractor.py` — PDF extraction. Form extractor (`devformextractor.indemn.ai`) is PRIMARY, pdfplumber is fallback. `_extract_via_form_extractor()` calls the LLMWhisperer-backed service. Has retry logic.
- `src/gic_email_intel/agent/skills/email_classifier.md` — classifier prompt with hard rules (policy numbers, internal senders, carrier domains, form requests)

### CLI commands
- `src/gic_email_intel/cli/commands/emails.py` — `next` (atomic claim for automation), `complete` (records results + denormalizes to submission INCLUDING unisoft_quote_id), `reset`. The `complete` command now propagates quote_id and source directly.
- `src/gic_email_intel/cli/commands/automate.py` — `run` (invoke deepagent), `backfill-ams` (resolve Quote IDs for legacy submissions). The automation query matches both `$exists:false` and `null`.

### Automation agent
- `src/gic_email_intel/automation/agent.py` — deepagent using LangChain `create_deep_agent()` with `LocalShellBackend`. Has `stdin=DEVNULL` monkey-patch for headless Docker. Has retry logic for 429. `run_one()` processes a single email.
- `src/gic_email_intel/automation/skills/create-quote-id.md` — THE SKILL. Three sub-patterns (direct agent, Granada portal, GIC forward). LOB mapping table. Step 3 says try producer code first before name search. **NEEDS UPDATES** for production: (a) agency search with phone + address fallback, (b) duplicate detection, (c) task creation after Quote ID.
- `unisoft-proxy/client/cli.py` — `unisoft` CLI that the agent calls. `quote create`, `agents search`, `agents get`, `lobs list/sublobs`, `activity create`, etc.

## The Unisoft Proxy (how we talk to Unisoft)

- C# HttpListener app running as Windows Service `UniProxy` on EC2 `i-0dc2563c9bc92aa0e` (Elastic IP 54.83.28.79, port 5000).
- Source: `C:\unisoft\UniProxy.cs` on the EC2 instance. Compiled with .NET Framework 4.8.
- Wraps all 910 Unisoft SOAP operations as `POST /api/soap/{OperationName}` with JSON in/out.
- JSON→XML: `JsonToXml()` function. Nested DTOs need entries in `dtoNamespaces` dictionary (we added `Criteria` for quote search). WCF requires alphabetical field order.
- Auth: proxy manages WS-Security + AccessToken automatically. Callers just need `X-Api-Key` header.
- API key: `84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de`

### **CRITICAL: Unisoft endpoint URLs changed 2026-04-13**
- **Old:** `https://services.uat.gicunderwriters.co/management/imsservice.svc`
- **Current:** `https://ins-gic-service-uat-app.azurewebsites.net/imsservice.svc`
- Unisoft pushed a ClickOnce app update that changed their URLs. The proxy env var `UNISOFT_SOAP_URL` has been updated.
- If proxy starts failing with "content type text/html" errors, check if the endpoint URL changed again.
- Check ClickOnce app config at: `C:\Users\Administrator\AppData\Local\Apps\2.0\*\Unisoft.Insurance.BackOffice.GIC_Beta.exe.config` for current URLs.

### Modifying the proxy
SSM into the Windows EC2, edit `C:\unisoft\UniProxy.cs`, stop service, compile with:
```
csc.exe /out:UniProxy.exe /r:System.ServiceModel.dll /r:System.Runtime.Serialization.dll /r:System.Web.Extensions.dll UniProxy.cs
```
Then start service. **DO NOT rapid-restart** — each startup calls `OpenChannel()` which authenticates. Many failed attempts may trigger account lockout.

### Unisoft API spec
- `projects/gic-email-intelligence/research/unisoft-api/wsdl-complete.md` — 910 operations, 1668 data types. **Always read this before guessing API parameters.**
- `projects/gic-email-intelligence/research/unisoft-api/raw-payloads/soap/` — Fiddler captures of real requests/responses
- Desktop app config has WCF binding configurations to reference: `C:\Users\Administrator\AppData\Local\Apps\2.0\JTE4KCR4.O9O\DLX1JQR0.9YM\*\*.exe.config` on the EC2

## The Backend API

- `src/gic_email_intel/api/routes/submissions.py` — board endpoint (`GET /submissions`), detail endpoint, AMS endpoint (`GET /submissions/{id}/ams`). Board uses exclusion-based `$project` so new submission fields appear automatically. Extractions queried via `email_id` chain (not `submission_id`).
- `src/gic_email_intel/api/routes/stats.py` — analytics endpoint with `journey` field (AMS coverage by email type category), automation stats, failure reasons.
- `src/gic_email_intel/core/ams_link.py` — `resolve_quote_id()`: checks automation results → portal reference numbers → stores on submission.
- `src/gic_email_intel/core/unisoft.py` — async Unisoft client for FastAPI. Params format: `{"QuoteID": id}` NOT `{"request": {"QuoteID": id}}`.

## The Frontend

- `ui/src/pages/SubmissionQueue.tsx` — compact table (37px rows), Type/AMS/Stage columns, 7 filter dropdowns
- `ui/src/pages/RiskRecord.tsx` — detail view with overlay pattern (queue stays mounted). Right column: AutomationBanner → ProcessingTimeline → ApplicantPanel → AI Analysis → Status → Documents → Stage History
- `ui/src/components/ProcessingTimeline.tsx` — Received → Extracted → Classified → AMS timeline
- `ui/src/components/ApplicantPanel.tsx` — merges extraction + AMS data with source indicators
- `ui/src/components/AutomationBanner.tsx` — shows actual failure reason from `submission.automation_error`
- `ui/src/pages/Insights.tsx` — Journey section first (CSS order:-1), summary cards, category progress bars, full failure reasons. Configuration section collapsed by default.

## Infrastructure

### Railway (dev)
- API service (always-on, manual deploy via `railway up -s api --environment development -d`)
- Sync cron (5min), processing cron (5min), automation cron (15min)
- MongoDB: `mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net`
- DB: `gic_email_intelligence`
- TILEDESK_DB_URI points to **prod** Atlas for GIC org membership checks (JC login)
- LLM_API_KEY: current Anthropic key — top up if pipeline fails with "credit balance too low"

### Amplify frontend
- App ID: `d244t76u9ej8m0`
- Custom domain: **`gic.indemn.ai`** (points at `main` branch)
- Also accessible at `main.d244t76u9ej8m0.amplifyapp.com`
- Auto-deploys on git push to main

### EC2 Unisoft proxy
- Instance: `i-0dc2563c9bc92aa0e` (Windows, t3.small). Elastic IP 54.83.28.79.
- SSM access via `AWS-RunPowerShellScript`
- RDP access: `aws ssm start-session --target i-0dc2563c9bc92aa0e --document-name AWS-StartPortForwardingSession --parameters '{"portNumber":["3389"],"localPortNumber":["3389"]}'`
- RDP credentials: `Administrator` / `Welcome123!`

### EC2 dev-services
- Instance: `i-0fde0af9d216e9182` (Ubuntu). Hosts form extractor + other dev services.
- Form extractor at port 8003 behind ALB `form-extractor-api` with WAF `indemn-waf` (Railway IP allowlisted).

### WAF
- `indemn-waf` has `AllowRailwayStaticIP` rule at priority 0 for Railway's static IP `162.220.234.15`.

### Auth
- Frontend auth proxies through copilot-server (production): `https://copilot.indemn.ai/api`
- JWT validation against prod tiledesk DB. GIC org ID: `65eb3f19e5e6de0013fda310`
- Indemn employees (@indemn.ai) get admin. External users need GIC org membership.

## Current Pipeline Status

As of 2026-04-16:
- Emails: ~4,500+
- Submissions: ~3,800
- AMS linked: 163 (135 automation, 28 portal)
- Automation: 144 completed, 103 failed, ~60% rate. All failures are legitimate gaps (missing agencies, franchise disambiguation).
- 7 GIC internal forwards still classified as `agent_submission` (5/7 automated successfully, not harmful)

## Known Issues / Open Items

1. **Activity step inconsistency** — the automation agent skips Step 6 (log activity) ~80% of the time. Skill needs tightening but this doesn't break anything.
2. **File service endpoint** — may have also changed URLs when the IMS endpoint did. Check `UNISOFT_FILE_URL` env var vs current desktop app config.
3. **Attachment upload skipped** — "S3 credentials unavailable" in many automation runs. S3 creds missing in Railway automation service env vars.
4. **Pipeline backlog** — 300 emails were reset Apr 13 after API key ran out. Should be cleared by now.
5. **Meeting transcript** — saved at `2026-04-14-meeting-summary.md`. Original Google Doc: `1cV3dRLUZT49dixc7v_j7Fc4ho2QwcUImsUG3XYTqEr0`.

## Do NOT

- Do not assume API parameter formats — read the WSDL spec at `projects/gic-email-intelligence/research/unisoft-api/wsdl-complete.md`
- Do not run ad-hoc one-time scripts — all processing goes through the pipeline
- Do not skip reading `harness.py` — it has the enrichment, classifier rules, and carrier skip logic that are critical
- Do not assume the Railway API has the latest code — it needs manual redeployment via `railway up -s api --environment development -d`
- Do not rapid-restart the Unisoft proxy — each startup authenticates. Multiple failed attempts may trigger account lockout.
- Do not modify `gic.indemn.ai` DNS or Amplify config without verifying first — it's pointing at the dev deployment for JC access.
- Do not assume UAT vs production data parity — agencies, producer codes, and franchise entries may differ.
- Do not make claims about what's happening without verifying — check logs, check database, check actual API responses.

## Key Files Quick Reference

| Need to... | File |
|------------|------|
| Understand current state | `projects/gic-email-intelligence/INDEX.md` |
| See JC decisions | `artifacts/2026-04-14-meeting-summary.md` |
| See data numbers | `artifacts/2026-04-08-data-snapshot.md` |
| Read Unisoft API | `research/unisoft-api/wsdl-complete.md` |
| Modify the pipeline | `src/gic_email_intel/agent/harness.py` |
| Modify automation agent skill | `src/gic_email_intel/automation/skills/create-quote-id.md` |
| Modify proxy (C#) | `C:\unisoft\UniProxy.cs` on EC2 |
| Check recent work | `artifacts/2026-04-13-session-checkpoint.md` |

## Environment Setup

```bash
# MongoDB direct connection (for queries)
mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/gic_email_intelligence"

# Unisoft CLI from local machine
cd /Users/home/Repositories/gic-email-intelligence
UNISOFT_API_KEY=84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de \
  PYTHONPATH=unisoft-proxy/client \
  .venv/bin/python unisoft-proxy/client/cli.py {command}

# GIC CLI (via Railway, or locally if env vars set)
uv run gic {command}

# Test API through proxy
curl "http://54.83.28.79:5000/api/soap/GetQuote" \
  -H "X-Api-Key: 84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de" \
  -H "Content-Type: application/json" \
  -d '{"QuoteID": 17146}'
```
