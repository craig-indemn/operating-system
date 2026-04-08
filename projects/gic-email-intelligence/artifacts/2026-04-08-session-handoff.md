---
ask: "Handoff prompt for next session — full context transfer"
created: 2026-04-08
workstream: gic-email-intelligence
session: 2026-04-07a
sources:
  - type: codebase
    description: "GIC email intelligence repo + OS project files"
---

# Session Handoff — 2026-04-08

Copy this entire block as the prompt for the next session:

---

`/project gic-email-intelligence`

## Context

This is the GIC Email Intelligence project — an end-to-end system that connects GIC Underwriters' Outlook inbox (quote@gicunderwriters.com) to their Unisoft AMS. The pipeline syncs emails, extracts data from PDFs, classifies email types, links to applicant records, and automates Quote ID creation in Unisoft via a deepagent.

The system is live in dev: sync every 5 min, processing every 5 min, automation every 15 min. 4,035 emails processed, 132 linked to AMS, 60% automation rate on new applications.

**Read these files in order before doing anything:**

### 1. Project state
- `projects/gic-email-intelligence/INDEX.md` — read the full Status section (first ~90 lines). This has everything done in the last session (30 items), all decisions, and next steps.

### 2. Key artifacts
- `projects/gic-email-intelligence/artifacts/2026-04-08-data-snapshot.md` — complete data picture: email counts by type, extraction coverage, AMS linkage breakdown, automation by date, what's visible in the UI vs not
- `projects/gic-email-intelligence/artifacts/2026-04-07-demo-readiness-plan.md` — 4 workstreams (validate automation, maximize AMS linkage, UI clarity, demo prep), success criteria, the "no ad-hoc processing" principle
- `projects/gic-email-intelligence/artifacts/2026-04-07-agency-verification.md` — 73 automation failures investigated, 37 agencies confirmed missing from Unisoft, 4 questions for JC (including the USLI direct portal question about ~2,800 carrier responses)

### 3. The processing pipeline (understand how data flows)
Read these files in the GIC repo (`/Users/home/Repositories/gic-email-intelligence/`):
- `src/gic_email_intel/agent/harness.py` — THE PIPELINE. `process_email()` does: extract → classify → link → enrich. Has deterministic classifier hard rules, submission enrichment from extractions, carrier response skip optimization. Understand `_enforce_classification_rules()` and `_enrich_submission_from_extractions()`.
- `src/gic_email_intel/agent/extractor.py` — PDF extraction. Form extractor (`devformextractor.indemn.ai`) is PRIMARY, pdfplumber is fallback. `_extract_via_form_extractor()` calls the LLMWhisperer-backed service. `extract_email_attachments()` is the entry point. Has retry logic.
- `src/gic_email_intel/agent/skills/email_classifier.md` — classifier prompt with hard rules (policy numbers, internal senders, carrier domains, form requests)
- `src/gic_email_intel/cli/commands/emails.py` — `next` (atomic claim for automation), `complete` (records results + denormalizes to submission), `reset`. The `complete` command copies `automation_status` and `automation_error` onto the submission document.
- `src/gic_email_intel/cli/commands/automate.py` — `run` (invoke deepagent), `backfill-ams` (resolve Quote IDs). The automation query matches both `$exists:false` and `null`.

### 4. The automation agent (understand how quotes are created)
- `src/gic_email_intel/automation/agent.py` — deepagent using LangChain `create_deep_agent()` with `LocalShellBackend`. Has `stdin=DEVNULL` monkey-patch for headless Docker. Has retry logic for 429. `run_one()` processes a single email.
- `src/gic_email_intel/automation/skills/create-quote-id.md` — THE SKILL. Three sub-patterns (direct agent, Granada portal, GIC forward). LOB mapping table. **Step 3 says try producer code first before name search.** SubLOB is optional.
- `unisoft-proxy/client/cli.py` — `unisoft` CLI that the agent calls. `quote create`, `agents search`, `agents get`, `lobs list/sublobs`, etc.

### 5. The Unisoft proxy (understand how we talk to Unisoft)
- The proxy is a C# HttpListener app running as Windows Service `UniProxy` on EC2 `i-0dc2563c9bc92aa0e` (Elastic IP 54.83.28.79, port 5000).
- Source: `C:\unisoft\UniProxy.cs` on the EC2 instance. Compiled with .NET Framework 4.8.
- It wraps all 910 Unisoft SOAP operations as `POST /api/soap/{OperationName}` with JSON in/out.
- JSON→XML: `JsonToXml()` function. Nested DTOs need entries in `dtoNamespaces` dictionary (we added `Criteria` for quote search). WCF requires alphabetical field order.
- XML→JSON: `XmlToJson()` function. Arrays detected by repeated child elements or `*DTO` suffix.
- Auth: proxy manages WS-Security + AccessToken automatically. Callers just need `X-Api-Key` header.
- API key: `84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de`
- To modify: SSM into the Windows EC2, edit `C:\unisoft\UniProxy.cs`, stop service, compile with `csc.exe /out:UniProxy.exe /r:System.ServiceModel.dll /r:System.Runtime.Serialization.dll /r:System.Web.Extensions.dll UniProxy.cs`, start service.
- Unisoft API spec: `projects/gic-email-intelligence/research/unisoft-api/wsdl-complete.md` — 910 operations, 1668 data types. **Always read this before guessing API parameters.**

### 6. The backend API
- `src/gic_email_intel/api/routes/submissions.py` — board endpoint (`GET /submissions`), detail endpoint, AMS endpoint (`GET /submissions/{id}/ams`). Board uses exclusion-based `$project` so new submission fields appear automatically. Extractions queried via `email_id` chain (not `submission_id`).
- `src/gic_email_intel/api/routes/stats.py` — analytics endpoint with `journey` field (AMS coverage by email type category), automation stats, failure reasons (200 char limit).
- `src/gic_email_intel/core/ams_link.py` — `resolve_quote_id()`: checks automation results → portal reference numbers → stores on submission.
- `src/gic_email_intel/core/unisoft.py` — async Unisoft client for FastAPI. `get_quote()` calls proxy. Params: `{"QuoteID": id}` NOT `{"request": {"QuoteID": id}}`.

### 7. The frontend
- `ui/src/pages/SubmissionQueue.tsx` — compact table (37px rows), Type/AMS/Stage columns, 7 filter dropdowns, "Needs attention" for failed automation
- `ui/src/pages/RiskRecord.tsx` — detail view with overlay pattern (queue stays mounted). Right column: AutomationBanner → ProcessingTimeline → ApplicantPanel → AI Analysis → Status → Documents → Stage History. Gap analysis temporarily commented out.
- `ui/src/components/ProcessingTimeline.tsx` — Received → Extracted → Classified → AMS timeline with timestamps
- `ui/src/components/ApplicantPanel.tsx` — merges extraction + AMS data with source indicators. AMS wins only when specific field has value (null AMS falls through).
- `ui/src/components/AutomationBanner.tsx` — shows actual failure reason from `submission.automation_error`
- `ui/src/pages/Insights.tsx` — Journey section first (CSS order:-1), summary cards, category progress bars, full failure reasons

### 8. Infrastructure
- **Railway (dev)**: API service (always-on, manual deploy via `railway up`), sync cron (5min), processing cron (5min), automation cron (15min). MongoDB: `mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net`. DB: `gic_email_intelligence`.
- **Amplify**: Frontend auto-deploys on git push to main. App ID: `d244t76u9ej8m0`. URL: `https://main.d244t76u9ej8m0.amplifyapp.com`. VITE_API_BASE points to Railway API.
- **EC2 Unisoft proxy**: `i-0dc2563c9bc92aa0e` (Windows, t3.small). Elastic IP 54.83.28.79. SSM access via `AWS-RunPowerShellScript`.
- **EC2 dev-services**: `i-0fde0af9d216e9182` (Ubuntu). Hosts form extractor + all other dev services. Form extractor at port 8003 behind ALB `form-extractor-api` with WAF `indemn-waf` (Railway IP allowlisted).
- **WAF**: `indemn-waf` has `AllowRailwayStaticIP` rule at priority 0 for Railway's static IP `162.220.234.15`.

## Pending items to check
1. **9 reprocessed emails** — check results (memory: `project_gic_reprocess_check.md`). 5 misclassified should now be reclassified, Vivian Menendez + Crystal Cleaning should have Quote IDs, One Insurance Services should use producer code #2120.
2. **Insights page review** — some sections (Email Analytics chart, Agents & Workflow, Configuration/LOB table) were designed for the old objective. May need updating.
3. **Demo preparation** (Workstream 4) — narrative for JC, questions to ask, production roadmap.

## Do NOT
- Do not assume API parameter formats — read the WSDL spec
- Do not run ad-hoc one-time scripts — all processing goes through the pipeline
- Do not skip reading the harness.py pipeline code — it has the enrichment, classifier rules, and carrier skip logic that are critical to understand
- Do not assume the Railway API has the latest code — it needs manual redeployment via `railway up -s api --environment development -d`
