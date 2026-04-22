# GIC Email Intelligence

Build a comprehensive understanding of GIC Underwriters' quoting operation by analyzing their quote@gicunderwriters.com inbox, then design and demo an intelligent system that organizes their workflows, identifies automation opportunities, and eventually connects to all their communication channels (email, phone via RingCentral). The system should be state-based, data-driven, with a data layer that ingestion and processing mechanisms build on top of.

## Status

**Session 2026-04-22. Going live to production tomorrow (2026-04-23). Pre-launch cleanup in progress.**

**To resume this project, read `artifacts/2026-04-17-session-handoff.md` — it has full context, infrastructure map, technical lessons, and the 7-step prod cutover plan.**

**What was done (2026-04-16 through 2026-04-22):**

1. Phase 1: Task creation end-to-end in UAT — proxy nested-DTO fix, custom ActionId 40, GroupId 2, CLI commands, skill Steps 6-8 with fail-fast discipline.
2. Phase 2: Multi-field agency matching — 1571 agents synced to MongoDB, phone+address+name+email scoring via rapidfuzz. Finds agencies that name search alone misses.
3. Phase 3: 3-layer duplicate detection — submission check, cross-submission check, Unisoft HasDuplicates flag.
4. Gemini migration — all LLM calls moved from Claude Sonnet (depleted) to Gemini 2.5 Pro/Flash via Vertex AI. Skills inlined in system prompt (deepagents SkillsMiddleware doesn't work with flat files).
5. Dual proxy — UAT port 5000 + Prod port 5001 on same EC2. Config-file-based routing. DNS identity fix for prod WCF auth. Prod endpoint discovered from ClickOnce app config.
6. Prod discovery — task groups: NEW BIZ (#3), NEW BIZ Workers Comp (#4). 21 LOBs. UniClient WS-Security creds work for both envs.
7. Infrastructure — proxy source in repo, dev crons paused, Railway deployed with Gemini, comprehensive proxy README with troubleshooting.
8. Write access to quotes inbox obtained (TJ at Grove Networks, confirmed 2026-04-22).
9. JC call 2026-04-22: confirmed ready for prod. Will send underwriter assignment field info (AssignedTo vs Owner). Going live 2026-04-23.

**Pre-launch items (do before going live):**
- Add `--assigned-to` flag to quote create CLI (JC sending which field to use)
- Update skill with prod GroupIds (3/4 instead of 2)
- Sync prod agents to MongoDB
- Implement email-to-subfolder move (write access now available)
- Update Railway env to point at prod proxy (port 5001)
- Deploy + smoke test one email against prod
- Verify task appears in JC's NEW BIZ queue

**Next session: clear context, resume from handoff, execute pre-launch + go live.**

**What was done (2026-04-16 session b):**

1. Read JC's Apr 16 09:15 update email — production unblock: URL `ins-gic-client-prod-app.azurewebsites.net`, user `indemnai`, prod groups `New Biz` + `New Biz Workers Comp` created. Still awaiting Mike's endorsement rundown.
2. Locked in production rollout plan with decisions: group-only task assignment, UAT-first with self-created test group, own MongoDB-side duplicate detection, 4-phase ordering (tasks → agency search → dup detection → prod cutover). Saved as `2026-04-16-production-rollout-plan.md`.
3. **Phase 1 complete: Unisoft task creation end-to-end in UAT.**
   - Patched proxy on EC2 `i-0dc2563c9bc92aa0e` twice: added Task/TaskAssociation/TaskGroup/TaskAction to `dtoNamespaces`, then fixed `AppendDtoField` to recurse into nested sub-DTOs (was hardcoded to nil, silently dropping TaskAssociation data). Recompiled, restarted once. Both patches backed up.
   - Created custom Section 5 action via `SetTaskAction`: ActionId 40 "Review automated submission" (distinct signal for team).
   - Created UAT test group via `SetTaskGroup`: GroupId 2 "Indemn Automation - New Biz".
   - Verified end-to-end: TaskId 16853 (Talavera Trucking, QuoteId 17273, group-assigned, +1 day due).
   - Discovered 50-char subject limit — handled via ellipsis truncation in CLI.
4. Added `unisoft task` CLI subcommands: create, get, groups, actions, group-create, action-create. All verified in UAT including long-subject truncation (TaskId 16854 for IGLESIA TABERNACULO).
5. Updated `create-quote-id.md` skill: new Step 6 (Create Task) with LOB→Group routing table; Step 7 renumbered (activity); Step 8 handles 3 outcomes (full success, partial success with Quote ID recorded on failed status, total failure). Added fail-fast discipline rules — no silent half-success states per user's requirement.
6. `gic emails complete` accepts `--task-id`, denormalizes `unisoft_task_id` onto submission.
7. Committed as `4b8a708 feat(tasks): add Unisoft task creation to new-biz automation`.

**Session 2026-04-16c — LLM migration to Gemini via Vertex AI + proxy source in repo:**

8. **Anthropic credits exhausted mid-session.** User approved migrating all LLM calls to Gemini. Confirmed Vertex AI works using the existing `indemn/dev/shared/google-cloud-sa` service account (project `prod-gemini-470505`, location `us-central1`). The SA JSON is stored as a minimal 3-field form with literal `\n` in the private key — bootstrap helper handles the reconstruction.
9. **Migrated LLM stack:**
   - Added `langchain-google-vertexai` dependency.
   - New `core.gemini_auth.ensure_google_credentials()` helper.
   - Config: `llm_provider` default → `google_vertexai`, added `llm_model_fast` for extraction, added `google_cloud_project`/`location`/`application_credentials`/`sa_json` fields.
   - `agent/llm.py`: added Vertex AI branch with `fast=True` flag for cheap model.
   - `agent/extractor.py`: switched to `ChatVertexAI` with `gemini-2.5-flash` default (extraction was the #1 cost driver).
   - `automation/agent.py`: default model now `google_vertexai:gemini-2.5-pro`.
10. **Critical fix: skill inlining.** The existing `skills=[SKILLS_DIR + "/"]` parameter never worked — `SkillsMiddleware` expects a directory-per-skill layout with `SKILL.md` inside, not a flat-file absolute path. Claude inferred the workflow from the system prompt; Gemini ad-hoc'd and skipped Step 6 entirely. Fix: drop `skills=` and load the skill content directly into the system prompt via `_build_system_prompt()`.
11. **Verified end-to-end in UAT:** Dana DiSanto email (69e005bb357e1315daee5126) → Quote 17342 + Task 16855 (group 2, ActionId 40, truncated subject, QuoteId/AgentNo/LOB association). Agent correctly marked activity-logging failure in completion notes per skill's best-effort rules.
12. **Bug fix:** `unisoft activity create` `--submission-id` was required; skill omits it. Made optional with default 0. Submission-id 0 is valid for quote-level activities (JC confirmed).
13. **PATH fix:** `build_env()` now adds `.venv/bin` to PATH so the agent finds `gic` without globbing.
14. **Proxy source in repo.** `C:\unisoft\UniProxy.cs` had been living only on EC2. Pulled via SSM→S3→local to `unisoft-proxy/server/UniProxy.cs`. Added README covering build, SSM deploy, env vars, `dtoNamespaces` extension pattern, and the account-lockout warning for rapid restarts.
15. Committed as `0ae581d feat: migrate all LLM calls to Gemini via Vertex AI + fix skill inlining` and `541b908 chore(proxy): check in UniProxy.cs source + deploy README`.

**Next steps:**

- **Deploy to Railway** (will require setting `GOOGLE_SA_JSON` env on automation + processing + api services and keeping `LLM_PROVIDER=google_vertexai`).
- **Decide cron strategy** — user flagged concern about burning credits processing all UAT emails continuously. Options: pause dev crons, rate-limit, or let them run on cheaper Gemini.
- **Audit attachment upload** — Gemini smoke test jumped from Quote to Task without uploading attachments. Verify if it's a skill adherence issue, CLI gap, or S3 creds issue.
- **Deploy** the updated CLI + skill to Railway automation service (`railway up -s automation`), let a cron tick create a task end-to-end through the deepagent, verify in UAT.
- **Phase 2:** Agency search — phone + address fallback when producer code and name don't match.
- **Phase 3:** MongoDB-side duplicate detection before creating Quote IDs.
- **Phase 4:** Production cutover — point proxy at prod Unisoft URLs, discover real GroupIds via `unisoft task groups` as `indemnai`, update skill, run first prod email end-to-end.
- **Parallel:** Connect endorsements inbox (read access already granted). Chase Makul on quote inbox write access for email-to-subfolder move.

**Previous session (2026-04-13 → 2026-04-16):**

1. Demo with JC and Mike Burke (2026-04-13). Meeting summary at `2026-04-14-meeting-summary.md`. Follow-up email sent to JC + Mike.
2. Recovered pipeline — Anthropic API credits exhausted Apr 10, 310 emails stuck. New key set, reprocessed.
3. Fixed `emails complete` to propagate `unisoft_quote_id` directly to submission (no more backfill needed).
4. Set up `gic.indemn.ai` pointing at main branch. Updated `TILEDESK_DB_URI` to prod for JC login access.
5. Unisoft proxy fix — Unisoft changed UAT endpoint URLs (`services.uat.gicunderwriters.co` → `ins-gic-service-uat-app.azurewebsites.net`). Proxy updated and verified working.
6. Confirmed activity creation works (submission-id 0 is fine) — agent inconsistently skips the step.

**Previous session (2026-04-08a):**

1. Verified 9 reprocessed emails: Vivian Menendez (Q:17262), Crystal Cleaning (Q:17261, Q:17263) — automation completed. Producer code #2120 fix working.
2. Fixed 6 orphaned quote IDs — automation_result had quote_id on email docs but not propagated to submissions. Directly linked all 6. Total AMS-linked: 163 (135 auto, 28 portal).
3. Insights page polish — fixed pipeline label, collapsed Configuration section, fixed stale Data Limitations text.
4. Demo preparation artifact — full walkthrough narrative, 9 questions for JC, 5-phase production roadmap.
5. Demo briefing PDF for JC at `2026-04-13-gic-demo-briefing.pdf`.

**Previous session (2026-04-07a → 2026-04-08):**

**What was done (2026-04-07 through 2026-04-08):**

**UX (queue):**
1. Detail view tightened — header dedup, compact ApplicantPanel/pipeline/UW prompt, unified right column.
2. Renamed "Submissions" to "Applicants" everywhere.
3. AMS filter (Linked/Auto/Portal/Failed/Not linked), Type filter (App/USLI/Portal/Reply/Internal).
4. Filter state preserved across detail view navigation (overlay pattern).
5. Compact table — 37px rows (was 93px), 2.5x data density. Added Type column, Received date. Dropped Folder/Open columns.
6. Compact filter bar — all controls at 10px matching table density.
7. "Needs attention" in queue for failed automation, with full reason in detail view AutomationBanner.

**UX (detail view):**
8. Gap analysis + LOB requirements temporarily commented out (not serving AMS linkage objective).
9. Fixed Dec 31 date bug (was using null `first_email_at`, now uses `created_at`).
10. Processing timeline — shows Received → Extracted → Classified → AMS with timestamps and field counts.
11. AutomationBanner shows actual failure reason ("Not yet in AMS — {reason}") instead of generic "No Unisoft record linked".
12. ApplicantPanel merge fix — null AMS fields no longer override extraction/email data. Fixes blank LOB, agent, address for portal-created quotes.

**UX (Insights):**
13. "Inbox → AMS Journey" section — replaces old "Automation" section. Summary cards (In AMS / Needs Attention / Pending / Rate), category progress bars, full failure reasons.
14. Journey section rendered first on page (CSS order).
15. Failure reasons expanded from 60→200 chars, word-wrap instead of truncate.
16. Pipeline label fixed, Configuration section collapsed by default, stale Data Limitations text updated.

**Pipeline:**
17. Form extractor as primary extraction (was pdfplumber fallback). WAF allowlist rule added for Railway IP on `indemn-waf`. Form extractor MongoDB URI updated from dead `pj4xyep` cluster to `mifra5` on EC2 `dev-services`.
18. Retry logic on all LLM calls (extraction, classification, linking, deepagent) — 4x with exponential backoff on 429.
19. Skip LLM extraction for carrier response emails (USLI/Hiscox) — data already in AMS.
20. SubLOB made optional in CLI (was required, broke WC quotes).
21. Deterministic classifier hard rules post-LLM (policy numbers in subject, internal GIC senders, form requests).
22. Automation query matches both `$exists:false` and `null` for reset emails.
23. Automation status + error denormalized onto submission documents for board visibility.
24. Submission enrichment from extraction data — fills named_insured, line_of_business, retail_agent_name, retail_agency_name from PDF extractions when missing. Runs in pipeline after every email. Backfilled 401 existing submissions.
25. Producer code lookup priority in automation skill — try by code first before name search.

**Research:**
26. Agency verification — 73 failures investigated against Unisoft's 1,571 agents. 37 agencies confirmed missing, 1 search bug (#2120), 5 misclassifications, 4 questions for JC documented.
27. USLI direct portal finding — ~2,800 USLI carrier quotes have no application in inbox (agents submitted to USLI directly, bypassing GIC email). 68% of email volume. Question for JC.
28. Proxy Criteria DTO fix — added `Criteria` to `dtoNamespaces` registry, recompiled proxy on EC2.
29. Portal quotes are blank shells in UAT — portal creates Quote ID but doesn't populate data in test environment. Expected to be populated in production.
30. AMS backfill — 138 linked (was 43). 110 automation + 28 portal.

**Previous session (2026-04-06b):**

**What was done session 2026-04-06b:**
1. **UI alignment — full AMS integration built and deployed.** Design doc at `artifacts/2026-04-06-ui-alignment-design.md`. Backend: async Unisoft client (`core/unisoft.py`), Quote ID resolution service (`core/ams_link.py`), AMS endpoint (`GET /submissions/{id}/ams`), automation stats in analytics, batch backfill CLI. Frontend: AMS column in queue table with Auto/Portal badges, ApplicantPanel component (merges email + AMS data with source indicators), AutomationBanner component (4 states), automation section in Insights.
2. **CRITICAL FIX: Extraction lookup was broken.** `get_submission_detail()` queried `extractions.find({submission_id})` but only 3 of 7,968 extractions had `submission_id` set. Fixed to query via email chain: `extractions.find({email_id: {$in: email_ids}})`. Now all 3,444 submissions with extractions show data.
3. **Backfill completed.** 43 submissions linked to Unisoft Quote IDs (28 automation, 15 portal). CLI: `gic automate backfill-ams`.
4. **Detail view redesign.** Removed redundant "Submission data" block from left column. Left = conversation only. Right = AutomationBanner + ApplicantPanel + AI Analysis + Stage + Documents. Banner moved to right column above applicant data.
5. **Railway crash notifications fixed.** Root cause: sync/processing had no cron schedule (treated as regular services, exit = crash). Also production environment had stale cron schedules. Fixed: set cron `*/5 * * * *` on dev sync/processing, removed all prod cron schedules, `restartPolicyType` removed from `railway.json` (set per-service via API).
6. **Automation cron running.** Every 15 min, up to 5 `agent_submission` emails. ~28 quotes created in Unisoft UAT so far.

**UX polish needed (next session):**
- ApplicantPanel currently uses rigid field name mapping — shows limited fields because extraction field names vary across document types (e.g., `applicant_mailing_address` vs `insured_address` vs `business_address`). Needs to show the ~10 most important fields cleanly regardless of exact field names, with AMS data as override when present.
- The panel should be clean and focused for the customer demo — not a dump of all 49 fields, but a curated summary of who/what/through whom/when.
- Source indicators (email vs AMS vs both) need to be subtle, not prominent.
- The existing ExtractedData component still exists but may be redundant with the new ApplicantPanel.

**Previous session (2026-04-06a):** Automation deployed to Railway. Critical bug fix: `_serialize_email()` mutation bug broke extraction data delivery to agent.

**What was done session 2026-04-06a:**
1. **Railway MongoDB migration** — All services updated from old `devadmin` credentials to new `dev-indemn` credentials on `mifra5` cluster. Both dev and prod environments were broken; dev fixed, prod services stopped (not needed).
2. **Direct Atlas connection** — Railway's static IP (`162.220.234.15`) added to Atlas Network Access allowlist. Services now connect directly via SRV URI — no more EC2 socat proxy needed for Railway. Eliminates primary rotation failures.
3. **Health check fix** — `/api/health` now has 3-second async timeouts on all DB calls. Deploys were failing because the health endpoint hung when DB was unreachable. `railway.json` healthcheck removed (was breaking cron services); set per-service via API.
4. **Automation service deployed** — New Railway cron service (`automation`), runs every 15 minutes, processes up to 5 `agent_submission` emails per tick. Static outbound IP enabled. Start command configured via Railway GraphQL API (cron schedule, healthcheck disabled, start command).
5. **deepagents stdin fix** — `LocalShellBackend.execute()` hangs in headless Docker because `subprocess.run(shell=True, capture_output=True)` has no stdin. Monkey-patched to pass `stdin=subprocess.DEVNULL`.
6. **ANTHROPIC_API_KEY fix** — The `LLM_API_KEY` → `ANTHROPIC_API_KEY` bridging in `create_automation_agent()` wasn't reliable. Set `ANTHROPIC_API_KEY` directly as Railway env var.
7. **CRITICAL BUG FIX: `_serialize_email()` mutation** — `gic emails next --json` was only returning the email object, NOT submission or extractions. Root cause: `_serialize_email()` converts ObjectIds to strings IN PLACE, then the subsequent MongoDB lookups for submission/extraction used string IDs (which never match ObjectId fields). Fix: save ObjectId refs before serialization. This was the root cause of ALL agent failures — the agent never had extraction data.
8. **Unisoft proxy API key** — The proxy's `PROXY_API_KEY` env var is `84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de` (not `gic-proxy-2026`). Updated on automation service.
9. **Verbose logging** — Added `--verbose` flag to `gic automate run` that streams every LLM call and tool execution. Uses LangGraph `stream_mode="values"` with message dedup. This is how we diagnosed the serialization bug.
10. **Validation results (post-fix)** — 8 quotes created (Q:17143-17152), 4 legitimate failures (agencies not in Unisoft, email with no attachments). 67% success rate on first real batch.

**Previous session (2026-04-03a):** Extraction overhaul, classification refinement, skill rewrite, attachment upload built and deployed.

**To resume this project, read these files in order:**
1. This INDEX.md Status section (current state, what was done, what's next)
2. `artifacts/2026-04-08-data-snapshot.md` — Complete data picture: email counts, extraction coverage, AMS linkage, automation by date
3. `artifacts/2026-04-07-demo-readiness-plan.md` — 4 workstreams, success criteria, no-ad-hoc principle
4. `artifacts/2026-04-07-agency-verification.md` — 73 failures investigated, 37 agencies missing, 4 questions for JC
5. The UI code in the GIC repo: `ui/src/pages/SubmissionQueue.tsx` (compact table), `ui/src/pages/RiskRecord.tsx` (detail view + processing timeline), `ui/src/pages/Insights.tsx` (journey view), `ui/src/components/ApplicantPanel.tsx`, `ui/src/components/AutomationBanner.tsx`, `ui/src/components/ProcessingTimeline.tsx`
6. The pipeline: `src/gic_email_intel/agent/harness.py` (pipeline + enrichment + classifier rules), `src/gic_email_intel/automation/agent.py` (deepagent), `src/gic_email_intel/automation/skills/create-quote-id.md`
7. The backend AMS: `src/gic_email_intel/core/unisoft.py` (async client), `src/gic_email_intel/core/ams_link.py` (Quote ID resolution), `src/gic_email_intel/api/routes/submissions.py` (AMS endpoint + board), `src/gic_email_intel/api/routes/stats.py` (analytics + journey)
8. Unisoft API: `research/unisoft-api/wsdl-complete.md` — 910 operations, 1668 types. Proxy on EC2 `i-0dc2563c9bc92aa0e`.

**What was done this session (2026-04-03a):**
1. **PDF extraction overhaul** — Replaced Claude Vision with pdfplumber (local, free) + Haiku (text-only, ~10x cheaper). Tested on 2 emails (6 PDFs total), all fields extracted correctly. `pdfplumber>=0.11.9` added as dependency. Form extractor OCR kept as fallback for scanned PDFs (WAF blocking discovered on `devformextractor.indemn.ai`).
2. **Infrastructure mapping** — Confirmed all GIC data lives on dev Atlas cluster. Railway prod connects to prod Atlas which is empty. Both APIs serve the same dev data. EC2 socat proxy routing documented. Saved as memory for future sessions.
3. **Classification refinement** — Full inbox snapshot: 3,548 emails, 88% carrier responses (already have Quote IDs), 5% new business (need Quote IDs), 4% ongoing conversation, 2% noise. Only `agent_submission` (122) needs Quote ID automation. `gic_portal_submission` and `gic_application` already have Quote IDs from their portals (assumption — verify with JC). Granada/GIC relationship clarified: sister companies under Granada Financial Group, GIC is MGA with binding authority.
4. **Classifier hardened** — Added "Hard Rules" section: any `*@usli.com` email is always a USLI type, any `*@hiscox.com` is always hiscox_quote. Forwarded emails check original sender first.
5. **Deep agent skill rewrite** — `create-quote-id.md` now includes: business context (GIC/Granada relationship), three sub-patterns within agent_submission (direct agent 53%, Granada portal 29%, GIC forward 17%), data mapping guidance, attachment upload step.
6. **Attachment upload — full chain built and deployed:**
   - Proxy: `POST /api/file/upload` and `GET /api/file/attachments` — BasicHttpBinding + MTOM to IINSFileService. WCF message contract pattern (metadata in SOAP headers, file in body). MustUnderstand header handler.
   - Python client: `upload_quote_attachment()`, `get_quote_attachments()`
   - CLI: `unisoft attachment upload --quote-id N --file a.pdf --file b.pdf` (multi-file)
   - Tested end-to-end: file uploaded to Quote 17140, confirmed in Azure Blob Storage at `gicins.blob.core.windows.net`
7. **Bug fix** — `gic emails get --attachment` was matching on `name` field but MongoDB stores `filename`. Fixed.
8. **WSDL doc surfaced** — `research/unisoft-api/wsdl-complete.md` added to hydration list. Contains all 910 IIMSService operations + 7 INSFileService operations with DTOs. Raw Fiddler captures in `research/unisoft-api/raw-payloads/soap/`.

**What was done session 2026-04-02a:**
1. **JC walkthrough captured** — Reviewed JC's screen-share video, captured the complete workflow as `research/jc-walkthrough-workflow.md`. Key findings: two entry paths (portal creates Quote ID automatically, email needs manual creation), three required fields for Quote ID (LOB, SubLOB, Agency), effective date = current date, expiration = +1 year.
2. **USLI GL automation analysis** — Complete field mapping from MongoDB production data. Downloaded and read all 16 pages of an actual USLI PDF (MGL026M2518). Confirmed: effective date is NOT in the PDF ("Please bind effective: ___" is blank). Confirmed: FormOfBusiness "L" works for LLC (tested). Confirmed: Unisoft requires EffectiveDate (BRConstraint). All 73 activity ActionIds mapped from API.
3. **Unisoft CLI built** — `unisoft quote create/get`, `unisoft submission create/list`, `unisoft activity create/list/actions`, `unisoft agents search/list/get`, `unisoft lobs list/sublobs`, `unisoft carriers list`, `unisoft call <op> <params>`. Tested end-to-end: Quote 17139 → Submission 15445 → Activity 46828.
4. **Email CLI extended** — Added `emails next` (atomic claim for automation), `emails complete` (record results), `emails reset` (reprocess). In the GIC repo.
5. **Automation agent built** — LangChain `deepagents` SDK with `LocalShellBackend`. Agent executes `gic` and `unisoft` CLI commands via bash. Skills loaded from filesystem. First skill: `create-quote-id.md` for Phase 1 Quote ID creation.
6. **Live test: 7 emails processed** — 1 success (Quote 17140: Florida International University, CG/SE, Agent 6544), 5 failures with clear explanations, 1 timeout. Agent correctly refuses when data is insufficient.
7. **Bugs fixed** — Case-sensitive API params (`QuoteID` not `QuoteId`), `SetSubmission` needs `PersistSubmission` field, Anthropic API key loading from project settings.

**Architecture:**
```
Email Pipeline (Railway)                    Automation Agent (new, same repo)
  sync → extract → classify → link            invoked with: gic automate run
  (pdfplumber + Haiku for extraction)          ↓
                                             gic emails next --json (claim email)
                                               ↓
                                             reads skill based on email type
                                               ↓
                                             unisoft quote create (Quote ID)
                                               ↓
                                             gic emails get --attachment (download PDFs from S3)
                                             unisoft attachment upload --quote-id N --file *.pdf
                                               ↓
                                             gic emails complete (record result)
                                               ↓
                                             Unisoft AMS (UAT) — quote + attachments
```

- Deep agent: `deepagents` SDK, `LocalShellBackend`, Claude Sonnet
- Two CLIs on PATH: `gic` (email data) + `unisoft` (AMS operations)
- Skills: markdown documents encoding workflows per email type
- Agent bootstraps own context via CLI — no injected prompts
- State tracking: `automation_status` field on email documents in MongoDB

**Proxy details (unchanged):**
- URL: `http://54.83.28.79:5000`
- EC2: `i-0dc2563c9bc92aa0e` (t3.small, Elastic IP 54.83.28.79, Windows Service `UniProxy`)
- RDP: `aws ssm start-session --target i-0dc2563c9bc92aa0e --document-name AWS-StartPortForwardingSession --parameters '{"portNumber":["3389"],"localPortNumber":["3389"]}'` then localhost:3389, Administrator / Welcome1!, Unisoft: ccerto / GIC2026$$!

**Live test results (7 agent_submission emails):**

| Insured | Result | Reason |
|---|---|---|
| Florida International University | **Quote 17140** | CG/SE, Agent 6544 (Estrella #284) |
| Blue Florida Services LLC | Failed | Estrella #326 not in Unisoft (66 Estrella entries, none with #326 — confirmed real gap) |
| Unknown (Rental Dwelling) | Failed | No insured, no agent, no extraction — empty portal notification |
| Imperial Services of Palm Beach | Failed | From quotes@granadainsurance.com — wrong classification (Granada portal, not agent submission) |
| Test Mukul | Failed | Test record + Granada portal |
| Crystal Cleaning Solutions | Failed | Agent found (5982) but address required by Unisoft, no extraction |
| Enkelana Caffe | Failed | Pre-fix test, no result recorded |

**Failure analysis:**
- **3 classification errors** — Granada portal emails and empty notifications misclassified as `agent_submission`. Fix in pipeline.
- **1 real agent gap** — Estrella #326 not registered in Unisoft. GIC business decision: add manually or automate agency creation.
- **1 missing extraction** — PDF not extracted, so no address data. Fix in pipeline.
- **1 pre-fix test** — Before API key loading was fixed.

**End-to-end test completed (2026-04-03):**
Quote #17142 created for Andres Perez Rentals Inc (CP/LR, Agent 5628). 3 PDF attachments uploaded to Azure Blob Storage (same location as portal uploads). Applicant info confirmed in Unisoft: name, address, city, state, zip, form of business, business description. Activity logging (ActionId 6) added to skill but not yet tested in a live run.

**Next steps (resume here):**
1. **UX polish** — The ApplicantPanel needs refinement. Currently uses rigid field name mapping that misses data when extraction field names vary (e.g., `insured_address` vs `applicant_mailing_address`). Should show ~10 most important fields cleanly with AMS override. Needs to look good for customer demo. The dev URL is `https://main.d244t76u9ej8m0.amplifyapp.com`.
2. **S3 credentials for Railway** — attachment uploads skip in Railway because AWS S3 creds aren't configured on the automation service.
3. **Unisoft name search** — Only 43 of 3,300+ submissions have Quote IDs. The remaining ~3,000 (mostly carrier responses) could be linked by searching Unisoft by insured name (`GetQuotesByName2`). This would dramatically increase AMS coverage in the UI.
4. **Business decisions for JC** — (a) agency creation policy, (b) Estrella #326-type gaps, (c) confirm portal auto-creates Quote IDs, (d) 4 agencies not in Unisoft.
5. **Get production API endpoints** from Unisoft/JC
6. **Phase 2** — submission creation, carrier response handling

**Previous session (2026-04-01b):** Unisoft REST proxy built and deployed. See below.

**Previous session (2026-03-31b):** Phase 1 research — workflow map, software guide, API reference from transcript + web research + video analysis.

**What was done this session (2026-03-30/31):**
1. **Production deployment plan** — Full brainstorm: Railway backend, Amplify frontend, shared JWT auth, MongoDB proxy, weekly backfill strategy. See `artifacts/2026-03-30-production-deployment-plan.md`.
2. **Fixed extraction pipeline** — Replaced broken ReAct pdf-extractor with structured output module. Downloads from S3, sends as multimodal content blocks, gets validated Pydantic model.
3. **Pipeline reorder** — extract → classify → link (was classify → link → extract). Classifier now has extraction context.
4. **Configurable stages** — `PIPELINE_STAGES=extract,classify,link` env var. Assess/draft disabled by default.
5. **JWT auth** — Copilot-server integration. Login page, signin proxy, GIC org scoping. Fixed: token "JWT " prefix stripping, CORS origins, 401 race condition.
6. **Railway deployment** — 3 services (API, sync cron, processing cron). MongoDB proxy through dev-services EC2. Primary detection script. Static IP `162.220.234.15`.
7. **Amplify deployment** — `gic.indemn.ai` (prod), dev on Amplify default domain. Route 53 DNS.
8. **Observatory link** — PR #57 at indemn-ai/indemn-observatory, GIC org scoped. Awaiting review.
9. **Week 1 backfill** — 124 emails processed (123 succeeded, 1 failed). Revealed empty body + empty extracted_fields bugs.
10. **Bug fixes:** Graph API datetime format (Z suffix), PDF attachment URLs (VITE_API_BASE), CORS origins, orphaned submissions cleanup.
11. **Root cause: empty extracted_fields** — `dict[str, Any]` → `list[ExtractedField]`. LangChain/Anthropic set `additionalProperties=false` on dict schemas. See pydantic-ai #4117.
12. **Root cause: empty email bodies** — Graph API `Prefer: text` returns empty for HTML-only emails. Removed preference, added `_extract_body()` helper.
13. **Skills created** — Railway CLI, AWS Amplify, LangChain. All in OS `.claude/skills/` with references.

**Production URLs:**
- Frontend: `https://gic.indemn.ai` (prod) / `https://main.d244t76u9ej8m0.amplifyapp.com` (dev)
- API: `https://api-production-e399.up.railway.app` (prod) / `https://api-production-79f0.up.railway.app` (dev)
- Login: `support@indemn.ai` (or any copilot account with GIC org)
- GitHub: `craig-indemn/gic-email-intelligence` (private)
- Railway project: `4011d186-1821-49f5-a11b-961113e6f78d` (environments: development, production)
- Amplify app: `d244t76u9ej8m0` (branches: main → dev, prod → gic.indemn.ai)

**Infrastructure:**
- MongoDB proxy: dev-services EC2 (44.196.55.84), ports 27017-27019 (dev), 27020-27022 (prod)
- Static IP: `162.220.234.15` (Railway Pro, per-service — must enable on each service in dashboard)
- Sync cron: **paused** (pending re-sync)
- Processing cron: **paused** (pending re-sync + clean slate)

**Backfill plan (not yet executed):**
1. Delete all emails from MongoDB
2. Re-sync all emails from Graph API (with body fix — captures HTML)
3. Clean slate all derived data
4. Process 1 month (March 2026) in weekly batches with Haiku (~$25-35 estimated)

**Known issues to address:**
- UI: extracted fields section vs gap analysis is confusing (layout/UX issue, noted in `artifacts/2026-03-31-ui-issues-noted.md`)
- Socat proxy not persistent (nohup, not systemd — dies on EC2 reboot)
- MongoDB proxy is temporary — remove when Atlas IP allowlist updated with Railway static IP
- Observatory link PR awaiting team review

**Key references:**
- Pipeline review: `artifacts/2026-03-30-pipeline-architecture-review.md`
- Deployment plan: `artifacts/2026-03-30-production-deployment-plan.md`
- Implementation plan: `artifacts/2026-03-30-production-implementation-plan.md`
- MongoDB proxy: `artifacts/2026-03-30-mongodb-proxy-setup.md`
- UI issues: `artifacts/2026-03-31-ui-issues-noted.md`

---

**What was built this session (2026-03-30):**
1. **Production deployment plan** — Full brainstorm: Railway backend, Amplify frontend, shared JWT auth, MongoDB proxy, weekly backfill strategy. See `artifacts/2026-03-30-production-deployment-plan.md`.
2. **Fixed extraction pipeline** — Replaced broken ReAct pdf-extractor (couldn't see PDFs) with structured output module. Downloads from S3, sends as multimodal content blocks, gets validated Pydantic model. Unbiased schema (`dict[str, Any]`).
3. **Pipeline reorder** — extract → classify → link (was classify → link → extract). Classifier now has extraction context.
4. **Configurable stages** — `PIPELINE_STAGES=extract,classify,link` env var. Assess/draft disabled by default.
5. **JWT auth** — Copilot-server integration. Login page, signin proxy, GIC org scoping. Token prefix "JWT " handling.
6. **Railway deployment** — 3 services (API, sync cron, processing cron). MongoDB proxy through dev-services EC2. Primary detection script. Static IP `162.220.234.15`.
7. **Amplify deployment** — `gic.indemn.ai` (prod), dev on Amplify default domain. Route 53 DNS.
8. **Observatory link** — Mail icon in header links to `gic.indemn.ai/?token=${jwt}` (code written, not yet deployed).
9. **Clean slate on prod** — All derived data deleted. 3,469 emails reset to pending.
10. **Skills created** — Railway CLI, AWS Amplify, LangChain. All in OS `.claude/skills/` with references.

**Production URLs:**
- Frontend: `https://gic.indemn.ai` (prod) / `https://main.d244t76u9ej8m0.amplifyapp.com` (dev)
- API: `https://api-production-e399.up.railway.app` (prod) / `https://api-production-79f0.up.railway.app` (dev)
- Login: `support@indemn.ai` (or any copilot account with GIC org)
- GitHub: `craig-indemn/gic-email-intelligence` (private)
- Railway project: `4011d186-1821-49f5-a11b-961113e6f78d`
- Amplify app: `d244t76u9ej8m0`

**Backfill status:** Week 1 (Mar 1-8, 124 emails) processing with Haiku. Weeks 2-4 pending assessment.

**What's NOT done:**
1. Backfill weeks 2-4 (Mar 8-31)
2. Sync cron bug (datetime timezone format)
3. Observatory link deployment
4. LOB configs beyond GL/Golf Cart
5. No URL routing in frontend
6. MongoDB proxy is temporary (remove when Atlas IP allowlist updated)
7. Socat not persistent (nohup, not systemd — dies on EC2 reboot)

**Key references:**
- Pipeline review: `artifacts/2026-03-30-pipeline-architecture-review.md`
- Deployment plan: `artifacts/2026-03-30-production-deployment-plan.md`
- Implementation plan: `artifacts/2026-03-30-production-implementation-plan.md`
- MongoDB proxy: `artifacts/2026-03-30-mongodb-proxy-setup.md`

---

**Session 2026-03-25. Demo delivered to JC and Maribel.** Full system live with 3,469 emails, 2,894 submissions, all assessed. Indemn branding applied. Outlook Add-in working. Demo walked through Overview → submission examples → Outlook sidebar → golf cart automation path.

**What was built this session (2026-03-24/25):**
1. **Business model research** — 7 research documents (171KB) analyzing GIC's actual operations from email data, web research, Gmail threads, Ryan's UX observations. Key finding: 93% of inbox is automated USLI notifications, only 5% of submissions need human work. See `research/business-model-synthesis.md`.
2. **8-stage lifecycle redesign** — Replaced broken 5-stage model. Added situation assessment layer ("understand before acting"), carrier/agent entities, ball-holder tracking. Design reviewed 3 times. See `artifacts/2026-03-24-data-model-redesign.md`.
3. **Full implementation** — 25 files changed (backend + frontend), 4-wave parallel execution. Models, tools, pipeline, API routes, all UI pages updated.
4. **Assessment backfill** — All 2,894 submissions assessed via parallel subagents. 105 legitimate drafts generated (82 decline notifications, 15 info requests, 8 quote forwards).
5. **Root cause fix: draft accuracy** — Disabled draft types the system can't produce accurately (status_update, followup, remarket_suggestion) until data sources exist. Documented WHY each is disabled and WHAT enables it.
6. **Fresh data sync** — Synced 255 new emails (Mar 16-25), classified and linked via subagents. 13 recent submissions had PDFs extracted and assessed.
7. **UI honest-ification** — UI only shows what's real. Gap analysis hidden for generic LOBs. Auto-notified USLI submissions dimmed. UW buttons are honest manual stage transitions. Pipeline bar simplified for auto-notified.
8. **Indemn branding** — Barlow font, CSS variable design system, GIC logo + "Powered by Indemn", Indemn iris accent color. Clickable table rows.
9. **Overview page** — 5-section demo narrative (what we did, what we found, how it works, what it means, automation path).
10. **Outlook Add-in** — Deployed to Vercel, cloudflared tunnel to localhost, 4 demo emails seeded.

**Previous sessions:** 2026-03-20 (Outlook Add-in), 2026-03-18/19 (inbox intelligence tool), 2026-03-16 (full implementation), 2026-03-13 (initial data extraction + classification).

**Repo:** `/Users/home/Repositories/gic-email-intelligence/` (50+ commits on `main`, local only)

### Research
Living research corpus in `research/` — 7 documents, 171KB, updated 2026-03-24. Start with `research/business-model-synthesis.md` for the unified picture. See `research/README.md` for full index.

### Current State (as of 2026-03-25)
- **3 tabs**: Submissions (queue), Overview (demo narrative), Insights (merged analytics + system)
- **3,469 emails** synced (last sync Mar 25), classified, linked to 2,894 submissions
- **2,894 submissions** — all assessed. 8-stage lifecycle: received, triaging, awaiting_agent_info, awaiting_carrier_action, processing, quoted, declined, closed
- **~330 PDF extractions** across ~30 submissions. 97% of PDFs still unextracted (extraction is the main data gap)
- **105 suggested drafts** — 82 decline notifications, 15 info requests, 8 quote forwards. All backed by assessments, all enabled draft types only.
- **3 new MongoDB collections**: assessments (2,894), carriers (3: USLI, Hiscox, Granada), agents (55)
- **Indemn design system** — Barlow font, CSS variables, GIC logo, "Powered by Indemn"
- **Outlook Add-in** — deployed at gic-addin.vercel.app. Needs cloudflared tunnel to connect to local backend.
- **LOB configs**: GL (10 fields) and Golf Cart (17 fields) configured. 35 others use generic 8-field config.
- **Draft types**: 3 enabled (info_request, quote_forward, decline_notification). 3 disabled (status_update, followup, remarket_suggestion) — documented in situation_assessor.md and harness.py.

### To Run
```bash
# Backend
cd /Users/home/Repositories/gic-email-intelligence
uv run uvicorn gic_email_intel.api.main:app --port 8080

# Frontend
cd ui && npm run dev

# Outlook Add-in (optional — needs tunnel)
nohup cloudflared tunnel --url http://localhost:8080 > /tmp/cloudflared.log 2>&1 &
# Get tunnel URL from /tmp/cloudflared.log, then:
cd addin && VITE_API_BASE=https://<tunnel>.trycloudflare.com/api VITE_API_TOKEN=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ npm run build
cp manifest.xml dist/ && cd dist && npx vercel --prod --yes && npx vercel alias gic-addin.vercel.app

# Web app URL
open "http://localhost:5173/?token=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ"
```

### Demo Examples (verified, extraction-backed)
| Submission | LOB | Story | Draft |
|-----------|-----|-------|-------|
| Vivaria Florida LLC | GL | Complete ACORD submission, 100% extracted, system correctly didn't request info | None (correct) |
| Klein International LLC | GL | USLI pending file, agent partial reply, draft requests remaining items | info_request to lbenitez@doraladvisors.com |
| Magdalena Soto | Commercial Property | USLI decline with 2 specific reasons from PDFs | decline_notification to glendys@sebandainsurance.com |
| William Wacaster | Golf Cart | Portal submission, 95% extracted, ready for UW — the automation story | None (correct) |

### Key Architecture Decisions
- **Situation assessment is the single source of truth** for completeness, gap analysis, and draft decisions. `compute_completeness()` is the fallback only when no assessment exists.
- **Draft types are gated** — only info_request, quote_forward, decline_notification are enabled. Others disabled until data sources exist (management system API, outbound tracking, carrier appetite data). Guard in harness.py `ENABLED_DRAFT_TYPES`.
- **Assessments drive everything downstream** — the pipeline is: classify → link → extract → assess → [maybe draft]. The assessor replaces the old stage_detector. See `situation_assessor.md`.
- **Two operating modes**: brokered (USLI/Hiscox) vs direct_underwritten (golf carts on Granada paper). Encoded in `operating_mode` field and LOB config `workflow_type`.
- **Auto-notified USLI submissions** (95% of volume) get template assessments and are dimmed in the UI. The 5% that need human work are the focus.

### What's NOT Done
1. **PDF extraction coverage** — only ~330 of 3,100+ PDFs extracted (10%). This is the biggest data gap. Submissions without extractions have inaccurate completeness and may have wrong drafts.
2. **LOB configs** — only GL and Golf Cart configured. 35 LOBs use generic 8-field config. Gap analysis hidden for these.
3. **Disabled draft types** — status_update, followup, remarket_suggestion need: management system API (Unisoft/Jeremiah), outbound email tracking, carrier appetite data.
4. **No URL routing** — React useState navigation, no shareable URLs, browser back doesn't work.
5. **Push to GitHub** — still local only, need indemn-ai org permissions.
6. **Production deployment** — running on localhost. Needs AWS (ECS/EC2 + domain + SSL).
7. **Email sending** — drafts are suggestions only. Actual sending requires Mail.Send permission from GIC.

### Session 2026-03-20 — What Was Built

**Outlook Add-in (end-to-end working)**
- React task pane (350px sidebar) with 6 components: TaskPane, SubmissionHeader, AddinSummary, AddinGapAnalysis, AddinDraft
- Office.js integration: reads current email subject/body, extracts ref numbers, calls backend lookup
- ItemChanged handler for re-fetching when switching emails (pinning works on M365 work accounts)
- `displayReplyAllFormAsync()` for "Reply with this" — opens native Outlook reply with draft pre-filled
- Markdown-to-HTML conversion in draft preview and reply (bold, italic, bullets)
- Deployed to Vercel at `gic-addin.vercel.app`
- Indemn BubbleMark (iris) branding at 16/32/80px

**Backend: Lookup Endpoint**
- `POST /api/lookup-email` with 5-step matching waterfall: internet_message_id → submission ref numbers → email classification ref numbers → subject match → fuzzy name match
- Extracted `get_submission_detail()` helper from inline route handler for reuse
- Server-side reference number extraction from subject (catches non-USLI formats)
- CORS updated for Vercel + cloudflare tunnel origins

**Email Seeding Script**
- `scripts/seed_outlook.py` — OAuth flow + Graph API sendMail to personal Outlook.com
- 5 demo emails covering: carrier pending, declined, quoted, new, awaiting info
- Entra app registered: `0ec79e75-d1c6-4f65-8418-22a4ed7a6506` (personal account, Mail.ReadWrite + Mail.Send + User.Read)

**Infrastructure**
- Hello-world sideload validation at `addin-test.vercel.app` (confirmed Office.js loads on personal Outlook.com)
- Cloudflared tunnel for exposing localhost:8080 to Vercel-hosted add-in
- 4-round design review cycle before implementation (all issues resolved)

**To run the demo:**
1. `cd /Users/home/Repositories/gic-email-intelligence && uv run uvicorn gic_email_intel.api.main:app --port 8080`
2. `cloudflared tunnel --url http://localhost:8080` — note the tunnel URL
3. Rebuild add-in with tunnel URL: `cd addin && VITE_API_BASE=https://<tunnel>.trycloudflare.com/api VITE_API_TOKEN=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ npm run build`
4. Deploy: `cp manifest.xml dist/ && cd dist && npx vercel --prod --yes`
5. Sideload `addin/manifest.xml` on Outlook.com
6. Open a seeded email → click "Analyze Email"

### Session 2026-03-18/19 — What Was Built

**Thread Parser & Conversation View**
- Email thread parser splits embedded reply chains into individual messages (Outlook, Gmail, Spanish separators)
- Conversations auto-expand as chat-style bubbles (GIC = blue/right, external = white/left)

**Reasoning Chain (Detail View Right Column)**
- AI Summary → What We Know (with sources) → LOB Requirements → Gap Analysis → Suggested Draft
- Stage-aware gap analysis: new submissions check full LOB requirements, quoted submissions only check quote details, declines show no requirements
- Two-tier gap analysis: Active Requests (amber, from conversation) + General Requirements (collapsed)
- Amber highlighting connects conversation → gap analysis → draft body

**Draft Workflow**
- Drafts as "Suggested Reply" in conversation, pinnable to bottom as compose bar
- Edit/Approve/Dismiss with editable text area
- After approve: Copy Draft (clipboard) + Open in Outlook (mailto)
- Auto-prompt "Mark as done?" after sending → resolves submission
- Missing/internal recipients flagged with editable To field, send blocked until resolved
- Manual "Mark as Done" button in detail header

**Board: Triaged Inbox**
- 3 action queues: Ready to Send, Needs Review, Monitoring
- Cards show lifecycle badges (📋 New, ✅ Quoted, ⚠️ Declined) + AI action summaries
- Meaningful empty states ("All caught up", "Nothing needs your attention")
- Dashboard bar with queue counts and sync status

**Done State & History**
- POST /api/submissions/{id}/resolve with resolution type (quote_forwarded, info_request_sent, decline_notified, manually_closed)
- Resolved submissions excluded from board and dashboard counts
- History section in Analytics with color-coded resolution badges
- GET /api/submissions/history endpoint

**Analytics & How It Works**
- Analytics tab: volume chart, email type breakdown, LOB distribution, top agents, resolution history
- How It Works tab: 7 sections explaining methodology with real numbers (3,214 emails, 13 types, 280 PDFs, etc.)
- Stage-aware requirement profiles explained with color-coded cards

**Data Quality & Infrastructure**
- 105 LOB variants → 35 clean categories
- All 5,888 attachments uploaded to S3
- PDF extraction from all email types (not just carrier)
- Batch processing with --model and --limit flags (Haiku for cost efficiency)

### What's NOT Done
1. **Full batch processing** — Only 100 of 3,155 emails processed through linker/stage/draft pipeline. 9 submissions still have no drafts (Haiku failed silently). Many email loops not yet closed because related emails haven't been linked.
2. **OCR for scanned PDFs** — Some USLI quote PDFs are scanned images. AI vision can identify them but can't extract premium/limits/effective date. Need OCR preprocessing (Tesseract/Textract).
3. **HTML attachment extraction** — Mercado Insurance has an HTML application file that the extractor doesn't handle.
4. **Push to GitHub** — Need indemn-ai org permissions
5. **Deploy to AWS** — Docker image → ECS/EC2, domain (gic.indemn.ai), SSL. Would eliminate need for cloudflared tunnel.
6. **Demo video recording** — Craig wants to record a walkthrough before showing to GIC
7. **Pinning on personal Outlook.com** — SupportsPinning in manifest but pin icon doesn't appear on consumer accounts. Works on M365 work accounts (GIC deployment).
8. **Remove debug output** — TaskPane shows debug JSON on no-match state. Remove before demo.
9. **Production auth** — Add-in uses embedded API token. Production needs Office.js SSO (`getAccessTokenAsync`).
10. **internetMessageId storage** — Not in sync pipeline yet. Production needs it for exact email matching.

### What's Built (2026-03-16-b)
- **98 files, ~13,000 LOC, 108 tests passing**, frontend builds clean
- **Backend**: Python 3.12, FastAPI (9 endpoints + WebSocket with 6 event types) + Typer CLI (7 groups, 25+ commands) + LangChain agent (5 skills, 11 tools)
- **Frontend**: React 19 + TypeScript + Vite + shadcn/ui — Kanban board (5 columns), slide-in detail overlay (timeline, extracted data, LOB-specific completeness ring, draft cards), clickable notification filters, per-field source indicators
- **Docker**: Multi-stage build, supervisord (API + sync + agent), rate limiting, health check
- **Code review**: 25 issues found → all 25 resolved
- **Design audit**: 16 gaps found → all 16 closed — every section of the 1,527-line design matches

### Database State
- 3,214 emails in MongoDB (3,165 migrated + 49 synced live)
- 2,885 pre-classified, 286 extractions, 8 drafts
- 10 sample submissions created by agent (all email types verified)
- S3 bucket `indemn-gic-attachments` with 68 attachments

### UX Testing Findings (2026-03-16-b, late session)
Craig did hands-on browser testing and found the UI was showing system internals instead of actionable info. Key feedback:
- **Cards were confusing**: red age badges (94d), agent reasoning text leaking into attention_reason field, too much crammed in
- **Detail view was useless**: wall of empty `--` dashes, "No extracted data yet" jargon, developer field names, suggested action buried at bottom
- **Email bodies were empty**: migrated emails had no body text (HTML-only emails, text came back empty from Graph API). Fixed by re-fetching from Graph API.
- **Drafts kept getting wiped**: E2E test had `delete_many({})` on drafts collection — fixed to scope cleanup

**Fixes applied:**
- Cards: removed age badges, removed agent reasoning text, show only name/LOB/agent/last-activity/email-count/attention-tag
- Detail: AI suggested action moved to TOP of right column, empty fields hidden, "What We Know" replaces "Extracted Data", human-readable field labels, "Still needed" with Title Case
- Agent: attention_reason validated as enum value, prevents freeform reasoning
- Data: re-fetched email bodies from Graph API for sample submissions

**CRITICAL NEXT SESSION**: The UI needs a full UX review with Craig before demo. Every view and flow must be crafted for maximum impact with Kyle and the GIC customer (JC, Maribel). Current state is functional but not yet demo-polished.

### What's NOT Done
1. **UX polish for demo** — every view and interaction needs to be reviewed for clarity, impact, and user-friendliness. Board cards, detail layout, search behavior, notification flow, email readability.
2. **Full batch processing** — 2,885 classified emails need agent linking + stage detection → ~$15-20 LLM cost, ~1-2 hours with 5 workers. 10-email sample proved pipeline works. Note: will need to re-fetch email bodies from Graph API for all 3,165 emails first.
3. **Push to GitHub** — need `indemn-ai` org permissions
4. **Deploy to AWS** — Docker image tested locally, need ECS/EC2 + domain (`gic.indemn.ai`) + SSL
5. **Demo dry run** — see demo script artifact for full plan

**Previous session (2026-03-16-a — design):**

**Previous sessions (2026-03-13-a and 2026-03-13-b combined):**

**What happened this session (2026-03-13-a and 2026-03-13-b combined):**

### API Setup & Exploration
- Set up Microsoft Graph API integration (Entra app registration, Exchange Online RBAC scoping)
- Confirmed read-only access working, credentials in 1Password
- PowerShell setup script saved for customer at `projects/gic-improvements/artifacts/outlook-integration-setup.ps1`

### Full Data Extraction
- Pulled all 3,165 emails + 5,888 attachments (2.2 GB) via extract_emails.py
- 5,746 PDFs, 102 images, 39 other file types
- Data stored in `data/emails.jsonl` + `data/attachments/`

### PDF Vision Pass (280 samples)
- Strategically sampled 280 PDFs across all email types and business lines
- Processed via 19 parallel Claude subagents reading actual PDFs
- Results in `data/results/batch_XXX_results.json` + `data/all_vision_results.json`
- Document types found: 145 quote letters, 105 application forms, 17 reports, 5 pending notices, plus loss runs, decline letters, portal screenshots, MVRs, driver's licenses, ACORD forms

### Full Email Classification (all 3,165)
- Classified every email via 32 parallel Claude subagents (text-only, no PDFs)
- Results in `data/class_results/cbatch_XXX_results.json` + `data/all_classifications.json`

### Email Type Distribution (complete)
| Type | Count | % |
|------|-------|---|
| USLI Quote | 2,553 | 80.7% |
| USLI Pending | 212 | 6.7% |
| USLI Decline | 147 | 4.6% |
| Agent Submission | 73 | 2.3% |
| Agent Reply | 37 | 1.2% |
| GIC Application | 32 | 1.0% |
| Report | 30 | 0.9% |
| Hiscox Quote | 24 | 0.8% |
| GIC Internal | 21 | 0.7% |
| Agent Followup | 10 | 0.3% |
| Other + misc | 26 | 0.8% |

### Lines of Business (40+ discovered)
Top 15: Personal Liability (887), GL (519), Special Events (245), Non Profit (215), Commercial Package (205), Property (205), Professional Liability/E&O (128), Allied Healthcare (74), Contractors Equipment (71), Excess Liability (64), Umbrella (46), Multi-Class Package (44), Personal Catastrophe/Collections (43), Builder's Risk (42), Excess Personal Liability (39). Plus Marine, Medical Professional, Home Business, Workers Comp, Auto, Trucking, Property Management, Real Estate, D&O, HandyPerson, Liquor Liability, Restaurant, Roofing, Pest Control, and more.

### UI Design (agreed)
- Two-view architecture: **Board** (submission pipeline) → **Submission Detail** (timeline + extracted data + suggested actions)
- Board columns: New → Awaiting Info → With Carrier → Quoted → Attention (updated 2026-03-16, see technical design)
- Detail view: left panel = chronological timeline of all interactions; right panel = extracted data with completeness ring + autonomous draft responses
- Tech: React + shadcn/ui frontend, Python backend
- Full design in `artifacts/2026-03-13-demo-ui-design.md`

### Business Context (from Gmail)
- **Juan Carlos (JC)** — EVP, Chief Underwriting Officer at GIC. Primary contact.
- **Maribel** — GIC staff, champion for email automation/analytics. The end user.
- **Mukul Gupta** — Granada Insurance (GIC parent), technical coordination
- Feb 26 call agreed: start with extracting submission data into viewable dashboard, then auto-responses, then core system data funneling
- Kyle's partnership: $5K implementation + $3K/month for web chat, email agent with data extraction, analytics, and voice agent prototyping
- **Jeremiah** — GIC contact for management system (Unisoft) APIs. Intro requested but not yet made.

**Next session — detailed technical design:**
1. **Validate lifecycle stages against actual email data** — are New/Info Needed/With Carrier/Quoted/Action Required the right stages?
2. **Submission linking logic** — how to connect emails to submissions (reference numbers, conversation threads, named insured matching)
3. **Backend architecture** — real-time email polling, classification pipeline, data model, API design
4. **Autonomous response drafting** — what the system needs to know, how to generate accurate follow-ups, studying GIC's actual info request email patterns
5. **Data model design** — submission schema, email-to-submission linking, state transitions
6. **Real-time ingestion** — how new emails are detected, processed, and displayed
7. **Demo data strategy** — do we use live data or a snapshot? How do we handle the demo environment?
8. **Testing strategy** — how we verify data extraction quality, stage detection accuracy, draft quality
9. **Implementation plan** — what to build first, dependencies, timeline

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Microsoft Graph API | API | https://graph.microsoft.com/v1.0/users/quote@gicunderwriters.com |
| GIC Underwriters | Customer | https://www.gicunderwriters.com |
| Entra App Registration | Auth | App ID: 4bf2eacd-4869-4ade-890c-ba5f76c7cada, Tenant: 7c0931fd-6924-44fe-8fac-29c328791072 |
| Credentials | 1Password | GIC Outlook Integration |
| RingCentral Integration | OS Project | projects/ringcentral-integration/INDEX.md |
| GIC Improvements | OS Project | projects/gic-improvements/INDEX.md |
| Audio Transcription | Reference | projects/audio-transcription/INDEX.md (similar pipeline approach) |
| Feb 26 Meeting Notes | Gmail | Thread: Gemini notes "Indemn & GIC - Agentic Email Automation" Feb 26, 2026 |
| Kyle's Follow-Up | Gmail | "GIC + Indemn - Feb 26 Follow-Up and Next Steps" |
| Partnership Agreement | Gmail | "GIC + Indemn - Updated Partnership Agreement" — $5K impl + $3K/month |
| Unisoft Integration Meeting | Google Drive | Doc: 15D0-idP_qtjPzWWljXAX09rqq7AwqwJ3QBe2uH3w158, Recording: 1xdfJi48zZx71tZGfNmCE7CQcd4ffngeI |
| Unisoft Communications | Software Vendor | unisoftonline.com, HQ: Miami FL, President: Hugo Montiel |
| GIC Unisoft Portal | AMS Portal | gicunderwriters.unisoftonline.com |
| Unisoft UAT Environment | Testing | Windows-only, access arranged by Hugo (pending) |
| Granada Insurance API | API (UAT) | services-uat.granadainsurance.com (OAuth, policy lookup confirmed) |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-13 | [exploration-objectives](artifacts/2026-03-13-exploration-objectives.md) | What are the objectives of exploration and what do we need to learn before building the demo? |
| 2026-03-13 | [email-taxonomy-and-schema](artifacts/2026-03-13-email-taxonomy-and-schema.md) | Email types discovered from 25 samples + proposed extraction schema |
| 2026-03-13 | [hybrid-split-view-ui-concept](artifacts/2026-03-13-hybrid-split-view-ui-concept.md) | UI concept: hybrid split view with inbox panel + intelligence panel (brainstorm output) |
| 2026-03-13 | [demo-ui-design](artifacts/2026-03-13-demo-ui-design.md) | Final demo UI design — board view + submission detail with autonomous actions |
| 2026-03-16 | [technical-design](artifacts/2026-03-16-technical-design.md) | Comprehensive technical design — architecture, data model, CLI, agent harness, skills, deployment, implementation plan |
| 2026-03-16 | Repo: `/Users/home/Repositories/gic-email-intelligence/` | Full implementation — all 10 phases, 98 files, 79 tests |
| 2026-03-16 | [design-vs-implementation-audit](artifacts/2026-03-16-design-vs-implementation-audit.md) | Section-by-section design audit — 13 MATCH, 3 PARTIAL, 16 gaps identified (all resolved) |
| 2026-03-16 | [demo-script](artifacts/2026-03-16-demo-script.md) | Full demo script for GIC team — flow, live sync testing, Q&A prep, submission picks |
| 2026-03-16 | [ux-testing-findings](artifacts/2026-03-16-ux-testing-findings.md) | Hands-on browser testing findings — card confusion, detail view problems, fixes applied |
| 2026-03-17 | [ux-deep-audit](artifacts/2026-03-17-ux-deep-audit.md) | Deep UX audit from customer perspective — every submission reviewed, 7 of 10 broken, root causes identified |
| 2026-03-18 | [detail-view-reasoning-chain](artifacts/2026-03-18-detail-view-reasoning-chain.md) | Brainstorm: redesign detail view as transparent reasoning chain — conversation → extraction → LOB requirements → gap analysis → editable draft |
| 2026-03-18 | [workflow-integration-design](artifacts/2026-03-18-workflow-integration-design.md) | Approve → Open in Outlook workflow, board draft status visibility, mailto vs Outlook deeplink vs Graph API |
| 2026-03-18 | [gap-analysis-redesign](artifacts/2026-03-18-gap-analysis-redesign.md) | Two-tier gap analysis: active requests (from conversation) vs general LOB requirements, amber color-coding across conversation + gaps + draft |
| 2026-03-18 | [board-redesign-triaged-inbox](artifacts/2026-03-18-board-redesign-triaged-inbox.md) | Brainstorm: replace lifecycle columns with action queues (Ready to Send, Needs Review, Monitoring) + dashboard analytics bar |
| 2026-03-18 | [analytics-view-design](artifacts/2026-03-18-analytics-view-design.md) | Analytics view design — volume, types, LOBs, agents, operational health metrics |
| 2026-03-18 | [lifecycle-done-state-history](artifacts/2026-03-18-lifecycle-done-state-history.md) | Done state design: what "done" means, resolution types, history view, first-time onboarding |
| 2026-03-19 | [outlook-addin-research](artifacts/2026-03-19-outlook-addin-research.md) | Outlook Add-in development research — architecture, APIs, deployment, testing, constraints for GIC plugin |
| 2026-03-19 | [outlook-addin-design](artifacts/2026-03-19-outlook-addin-design.md) | Outlook Add-in design — task pane UI, lookup endpoint, email seeding, demo strategy, deployment plan |
| 2026-03-20 | Implementation plan at `docs/plans/2026-03-20-outlook-addin-implementation.md` (in repo) | 14-task implementation plan with parallel tracks for backend, frontend, seeding, and integration |
| 2026-03-23 | [intake-manager-integration-analysis](artifacts/2026-03-23-intake-manager-integration-analysis.md) | Full exploration of intake-manager codebase + side-by-side comparison + integration vision for merging GIC intelligence into intake-manager |
| 2026-03-23 | [gic-demo-strategy](artifacts/2026-03-23-gic-demo-strategy.md) | Demo strategy for JC/Maribel: 3-act narrative, targeted reclassification, UI reshape to Ryan's wireframes, golf cart LOB focus, 2-day execution plan |
| 2026-03-24 | [session-handoff](artifacts/2026-03-24-session-handoff.md) | Comprehensive handoff: system state, data pipeline, UI status, critical draft accuracy issue, golf cart analysis, what needs fixing |
| 2026-03-24 | [data-model-redesign](artifacts/2026-03-24-data-model-redesign.md) | Comprehensive data model & lifecycle redesign — 8-stage model, situation assessment layer, context-aware draft generation, sourced from 7 research documents |
| 2026-03-24 | [implementation-plan](artifacts/2026-03-24-implementation-plan.md) | 4-wave implementation plan with 15 parallel tasks — backend, frontend, migration, browser testing |
| 2026-03-25 | [demo-talking-points](artifacts/2026-03-25-demo-talking-points.md) | Demo walkthrough for JC — 4 acts, talking points, examples, Q&A prep |
| 2026-03-30 | [pipeline-architecture-review](artifacts/2026-03-30-pipeline-architecture-review.md) | Complete end-to-end pipeline walkthrough — every step, every file, every limitation. Pre-production review. |
| 2026-03-30 | [production-deployment-plan](artifacts/2026-03-30-production-deployment-plan.md) | Full production plan — Railway backend, Amplify frontend, pipeline fix, auth, Observatory integration, historical data processing, definition of done |
| 2026-03-30 | [production-implementation-plan](artifacts/2026-03-30-production-implementation-plan.md) | Bite-sized implementation plan — 16 tasks across 4 parallel tracks (pipeline fix, infra, auth, production) |
| 2026-03-30 | [mongodb-proxy-setup](artifacts/2026-03-30-mongodb-proxy-setup.md) | EC2 socat proxy setup for Railway → Atlas connectivity. Temporary. Includes teardown instructions. |
| 2026-03-31 | [ui-issues-noted](artifacts/2026-03-31-ui-issues-noted.md) | UI issues from prod review — extracted fields vs gap analysis confusion, PDF links (fixed), empty bodies (fixed) |
| 2026-03-31 | [ui-polish-design](artifacts/2026-03-31-ui-polish-design.md) | UI redesign for JC daily use — expandable email rows, Outlook folder column/filter, remove completeness bar, clarify detail view layout |
| 2026-03-31 | [unisoft-workflow-map](research/unisoft-workflow-map.md) | How GIC takes info from Outlook and enters it into Unisoft AMS — workflow by email type, data mapping, automation priorities |
| 2026-03-31 | [unisoft-software-guide](research/unisoft-software-guide.md) | Unisoft Communications as software — company, products, tech stack, UI structure, customer base, UAT exploration plan |
| 2026-03-31 | [unisoft-api-reference](research/unisoft-api-reference.md) | API capabilities — Unisoft (pending), Granada API (confirmed), industry standards, integration strategy, questions for Hugo |
| 2026-04-01 | [unisoft-rest-proxy-design](artifacts/2026-04-01-unisoft-rest-proxy-design.md) | REST proxy design — wraps all 910 Unisoft SOAP operations via HTTP/JSON, runs on t3.micro Windows EC2 (~$20/month) |
| 2026-04-01 | [usli-gl-automation-analysis](research/usli-gl-automation-analysis.md) | USLI GL (MGL) automation analysis — complete field mapping, all 73 activity ActionIds, verified data gaps (EffectiveDate is NOT in email or PDF), example record walkthrough |
| 2026-04-02 | [jc-walkthrough-workflow](research/jc-walkthrough-workflow.md) | JC's actual Unisoft workflow from video: two entry paths (portal vs email), 3 required fields for Quote ID (LOB, SubLOB, Agency), phased automation strategy, effective date = current date, full lifecycle through carrier response |
| 2026-04-06 | [ui-alignment-design](artifacts/2026-04-06-ui-alignment-design.md) | Design for inbox + AMS unified view — architecture, data flow, API contracts, TypeScript types, component specs, build order |
| 2026-04-07 | [demo-readiness-plan](artifacts/2026-04-07-demo-readiness-plan.md) | Demo readiness plan — 4 workstreams: validate automation, maximize AMS linkage, UI clarity, demo prep. Success criteria, current state analysis, no-ad-hoc-processing principle |
| 2026-04-07 | [agency-verification](artifacts/2026-04-07-agency-verification.md) | 73 automation failures investigated — 37 agencies confirmed missing from Unisoft, 1 search bug, 4 misclassified, 4 questions for JC |
| 2026-04-08 | [data-snapshot](artifacts/2026-04-08-data-snapshot.md) | Complete data picture — 3,948 emails, 98.7% extracted, 131 AMS-linked, automation by date, UI visibility gaps |
| 2026-04-08 | [session-handoff](artifacts/2026-04-08-session-handoff.md) | Comprehensive session handoff prompt — all files to read, pipeline/proxy/automation/UI/infrastructure context |
| 2026-04-08 | [demo-preparation](artifacts/2026-04-08-demo-preparation.md) | Demo narrative, 5-screen walkthrough, 9 questions for JC, 5-phase production roadmap |
| 2026-04-08 | [jc-meeting-email](artifacts/2026-04-08-jc-meeting-email.md) | Email draft to JC setting up the demo meeting |
| 2026-04-13 | [gic-demo-briefing](artifacts/2026-04-13-gic-demo-briefing.md) | PDF briefing for JC — what we built, Unisoft automation details, results, next steps |
| 2026-04-13 | [session-checkpoint](artifacts/2026-04-13-session-checkpoint.md) | Full state capture — proxy fix, pipeline recovery, config state, open items |
| 2026-04-14 | [meeting-summary](artifacts/2026-04-14-meeting-summary.md) | Meeting with JC + Mike Burke — decisions, action items, production rollout plan |
| 2026-04-14 | [followup-email](artifacts/2026-04-14-followup-email.md) | Follow-up email to JC and Mike — recap, next steps, what's needed from each person |
| 2026-04-16 | [session-handoff](artifacts/2026-04-16-session-handoff.md) | Comprehensive handoff prompt for next session — current state, production rollout plan, file reference, environment setup |
| 2026-04-08 | [demo-preparation](artifacts/2026-04-08-demo-preparation.md) | Demo narrative, 5-screen walkthrough, 9 questions for JC, 5-phase production roadmap |
| 2026-04-16 | [production-rollout-plan](artifacts/2026-04-16-production-rollout-plan.md) | Production rollout plan with decisions — task creation approach, UAT-first, own dup detection, 4-phase ordering |
| 2026-04-16 | [task-creation-uat-foundation](artifacts/2026-04-16-task-creation-uat-foundation.md) | Unisoft task creation end-to-end working in UAT — proxy nested-DTO fix, custom ActionId 40, test GroupId 2, reference payload, 50-char subject limit |
| 2026-04-17 | [session-handoff](artifacts/2026-04-17-session-handoff.md) | Full session handoff — Phases 1-3, Gemini migration, Railway deploy, dual proxy, prod discovery |

## Key Data Files
| File | What it contains |
|------|-----------------|
| `data/emails.jsonl` | All 3,165 emails — metadata + body text + attachment info |
| `data/attachments/` | 5,888 raw attachment files (2.2 GB), organized by email index |
| `data/all_classifications.json` | Claude classification of all 3,165 emails (type, line of business, named insured, reference numbers) |
| `data/all_vision_results.json` | Claude vision extraction of 280 sampled PDFs (structured insurance data) |
| `data/vision_sample.jsonl` | The 280 emails selected for PDF vision processing |
| `data/batches/` | Batch files for vision processing (19 batches) |
| `data/class_batches/` | Batch files for classification (32 batches) |
| `data/results/` | Per-batch vision results |
| `data/class_results/` | Per-batch classification results |
| `extract_emails.py` | Email + attachment extraction script |
| `sample_for_vision.py` | Strategic PDF sampling script |
| `prepare_batches.py` | Vision batch preparation script |
| `prepare_classification_batches.py` | Classification batch preparation script |

## Decisions
- 2026-03-13: Microsoft Graph API with client credentials flow for email access (read-only Mail.Read)
- 2026-03-13: Exchange Online RBAC scopes access to quote@gicunderwriters.com only
- 2026-03-13: System should be state-based and data-driven with a data layer that processing builds on top of
- 2026-03-13: Claude vision for PDF attachment extraction (no OCR libraries)
- 2026-03-13: The submission is the central entity, not the email — emails are events in a submission's lifecycle
- 2026-03-13: Demo is a standalone React + Python web app, not an Outlook plugin
- 2026-03-13: Two-view UI: Board (pipeline) → Submission Detail (timeline + data + suggested actions)
- 2026-03-13: React + shadcn/ui for frontend, Python for backend
- 2026-03-13: Autonomous responses shown as drafts in demo (no write access), approve/send in production
- 2026-03-13: Need comprehensive technical design before building — every detail thought through
- 2026-03-16: 5 action-oriented columns: New, Awaiting Info, With Carrier, Quoted, Attention (validated against data)
- 2026-03-16: Reference numbers are primary linking key (96.2% coverage). Conversation threading is useless.
- 2026-03-16: Agent harness with CLI + Skills pattern — CLI is the CRUD interface, DeepAgent is the brain
- 2026-03-16: This is the first instance of Indemn's generalizable agentic workflow pattern (DeepAgent + Skills + CLI)
- 2026-03-16: MongoDB on existing Atlas cluster, separate `gic_email_intelligence` database
- 2026-03-16: AWS deployment (ECS/EC2 + S3) alongside existing infrastructure
- 2026-03-16: LOB requirements derived from quote output data (quote fields ≈ application input). Start with GL.
- 2026-03-16: Live connection for demo, not a snapshot
- 2026-03-16: Neutral/white-label UI — no specific branding, brand later
- 2026-03-16: Clean and professional visual style — advanced but approachable
- 2026-03-16: Implementation uses structured LangChain tools (call core library directly) instead of CLI subprocess for agent — faster, type-safe, no shell quoting issues
- 2026-03-16: Auth via Authorization Bearer header for REST, query param for WebSocket (browser WS API doesn't support custom headers)
- 2026-03-16: Token persisted in sessionStorage to survive React Router navigation
- 2026-03-16: Atomic $min for first_email_at instead of read-then-write (race condition fix)
- 2026-03-16: Single $facet aggregation for board view instead of N+1 per-stage queries
- 2026-03-16: Cards show only what matters: name, LOB, agent, last activity, email count. No age badges.
- 2026-03-16: Detail view leads with action (AI draft), not data. Empty fields hidden. Human-readable labels.
- 2026-03-16: UX must be reviewed and polished per-view before demo — functional != demo-ready
- 2026-03-18: Emails in quote@ contain full conversation threads embedded in the body — parse them, don't treat as single messages
- 2026-03-18: Detail view right column is a transparent reasoning chain: Summary → Extraction → Requirements → Gap Analysis
- 2026-03-18: Gap analysis has two tiers: Active Requests (from conversation, amber) + General LOB Requirements (collapsed, gray)
- 2026-03-18: Amber color-coding connects gap items across conversation, gap analysis, and draft body
- 2026-03-18: Draft lives in the conversation as "Suggested Reply", pinnable to bottom as compose bar
- 2026-03-18: Don't fall back to internal GIC addresses for drafts — flag missing recipients, let user fill in
- 2026-03-18: Extract PDFs from ALL email types, not just carrier notifications (agent replies have loss runs too)
- 2026-03-18: Board redesigned from lifecycle stages to action queues: Ready to Send, Needs Review, Monitoring
- 2026-03-18: The product is an inbox augmentation tool — eventually an Outlook plugin, first objective is automating info requests
- 2026-03-18: Analytics view shows email volume, types, LOBs, agents — real-time understanding of the inbox
- 2026-03-18: LOB normalization: 105 variants consolidated to 35 clean categories
- 2026-03-18: Gap analysis is stage-aware: new submissions check full LOB requirements, quoted checks only quote details, declined has no requirements
- 2026-03-18: "Done" means: draft sent (auto-prompted), manually closed, or superseded. Resolution types: quote_forwarded, decline_notified, info_request_sent, followup_sent, manually_closed
- 2026-03-18: Resolved submissions excluded from board, visible in Analytics History section
- 2026-03-18: How It Works page explains methodology — data sources, classification, linking, extraction, stage-aware requirements, draft generation, pipeline
- 2026-03-18: Use Haiku for batch processing (10x cheaper), Sonnet for PDF extraction quality
- 2026-03-18: Some USLI PDFs are scanned images — need OCR preprocessing for premium/limits extraction
- 2026-03-19: Build Outlook Web Add-in (Office.js) as task pane sidebar — React app deployed to Vercel, reads current email via Office.js, matches to backend via reference numbers
- 2026-03-19: Reply mechanism: displayReplyAllFormAsync() — opens native Outlook reply with draft pre-filled, no Mail.Send permission needed
- 2026-03-19: Demo strategy: seed emails from GIC's quote@ into Craig's personal Outlook.com inbox via Graph API delegated permissions, sideload add-in there
- 2026-03-19: Matching waterfall: internet_message_id (real deployment) → reference_numbers (demo) → fuzzy insured name (fallback)
- 2026-03-19: Standalone web app stays as analytics/management view, add-in is the day-to-day workflow tool
- 2026-03-20: Outlook Add-in renamed to "Indemn Email Intelligence" with Indemn BubbleMark branding
- 2026-03-20: Lookup endpoint enhanced: email classification ref matching + subject matching + server-side extraction (handles non-USLI ref formats)
- 2026-03-20: Demo emails seeded via sendMail to personal Outlook.com (craigindemn@outlook.com) — direct inbox creation doesn't activate add-ins
- 2026-03-20: Pinning (SupportsPinning) requires VersionOverridesV1_1, not V1_0 — works on M365 work accounts, not personal Outlook.com
- 2026-03-20: Cloudflared tunnel needed for demo (add-in on Vercel can't reach localhost backend)
- 2026-03-30: Post-demo direction shift: focus on data quality and extraction pipeline, not auto-drafts/ball-holder. System becomes pipeline into AMS (Unisoft).
- 2026-03-30: Railway for backend (3 services: API, sync cron, processing cron), AWS Amplify for frontend
- 2026-03-30: Pipeline reorder: extract → classify → link. Extraction first so classifier has PDF content.
- 2026-03-30: Assess and draft stages disabled by default via PIPELINE_STAGES config. Re-enable when data sources exist.
- 2026-03-30: JWT auth via copilot-server (prod: copilot.indemn.ai). Shared JWT_SECRET, HS256, no exp verification.
- 2026-03-30: GIC org scoped access: @indemn.ai = admin, GIC org members = access, others = 403.
- 2026-03-30: MongoDB Atlas proxy via dev-services EC2 (socat). Temporary until Atlas IP allowlist updated.
- 2026-03-30: Railway static IP per-service, not per-project. Must enable on each service individually.
- 2026-03-30: railway.json should NOT set startCommand or healthcheckPath — these are per-service via GraphQL API.
- 2026-03-30: Copilot-server returns token as "JWT <jwt>" — backend must strip prefix from token VALUE, not just header.
- 2026-03-30: Haiku for batch processing (~4x cheaper than Sonnet, sufficient for extraction/classification).
- 2026-03-31: dict[str, Any] DOES NOT WORK with LangChain structured output — LangChain/Anthropic set additionalProperties=false. Use list[ExtractedField] with explicit key/value pairs instead. (pydantic-ai #4117)
- 2026-03-31: Graph API Prefer: text header causes HTML-only emails to return empty body. Remove the preference, capture native format.
- 2026-03-31: VITE_API_BASE must be used everywhere the frontend calls the API — relative /api only works with local Vite proxy.
- 2026-03-31: Unisoft AMS contact is Hugo Montiel (President), not Jeremiah. JC cc'd Craig on email to Hugo for UAT + quoting API access.
- 2026-03-31: Unisoft API likely limited to initial data entry (LOB, basic info → quote ID). Activities (like "Submit Application to Carrier") may not be API-accessible — browser automation is the fallback.
- 2026-03-31: Three-pillar research approach for Unisoft integration: (1) workflow map from transcript, (2) software understanding from web research + UAT, (3) API capabilities. Understand before solutioning.
- 2026-03-31: Unisoft tech stack is ASP.NET MVC, C#, SQL Server, Entity Framework — modern enough for REST APIs, but no public API docs exist. Internal REST/SOAP infrastructure confirmed from job postings.
- 2026-03-31: "Delete from Outlook = done" is GIC's current coordination mechanism for the shared inbox. Our system replaces this.
- 2026-03-31: USLI quotes are JC's #1 automation priority — "very repetitive and boxed up." Personal liability has "never been efficiently put into the management system."
- 2026-04-01: Unisoft ClickOnce app talks to APIs, NOT direct database. Multi-layer: REST gateway + WCF SOAP + file service + SignalR. UI automation NOT needed.
- 2026-04-01: SetQuote (SOAP) is the core write operation. Fields include LOB (2-char code like CG), SubLOB (2-char like AC), AgentNumber (int), Name, Address, etc. Action=Insert for new.
- 2026-04-01: Two auth flows: REST uses JWT (POST /api/authentication/login), SOAP uses WS-Security (UniClient/J5j!}7=r/z) + GetToken (GIC_UAT).
- 2026-04-01: 70 SOAP operations + 32 REST endpoints confirmed from Fiddler capture. Full API surface in research/unisoft-api-reference.md.
- 2026-04-01: USLI carrier number is 2, USLI contact email is joanneh@usli.com, GIC broker ID is 1. LOB code CG = General Liability.
- 2026-04-01: Windows EC2 (i-0dc2563c9bc92aa0e) used for Fiddler recon. Stop when not in use (~$0.17/hr). RDP via SSM port forwarding.
- 2026-04-01: Fiddler recon approach (install app, intercept traffic, map API) proved faster and more complete than waiting for official API docs from Unisoft.
- 2026-04-01: WCF WSHttpBinding + WS-SecureConversation CONFIRMED WORKING from .NET Framework 4.8 on EC2. GetToken → GetInsuranceLOBs full round-trip successful.
- 2026-04-01: WSHttpBinding is NOT supported in modern .NET 6/7/8. .NET Framework 4.8 is required for the SOAP client.
- 2026-04-01: REST proxy design: HttpListener console app on t3.micro Windows EC2 (~$20/month). Generic passthrough for all 910 operations via POST /api/soap/{OperationName}. JSON in, JSON out.
- 2026-04-01: API returns 18 LOBs (not 21 from UI). "Boats & Yachts" = sub-LOB OM/BY, "Commercial Auto" = sub-LOB TR/CA. 46 carriers, 3,142 agents confirmed.
- 2026-04-01: Every SOAP operation requires AccessToken from GetToken. Proxy manages this automatically — callers never see it.
- 2026-04-01: (os-outlook session) Row click expands emails inline, "Open" button navigates to detail view. Folder awareness added. Overview tab hidden. 1-month backfill complete (617 emails, zero failures). Crons restored.
- 2026-04-02: Automation architecture: LangChain deepagents SDK with LocalShellBackend. Agent executes CLI commands via bash, same pattern as Claude Code. Two CLIs: `gic` (email data) and `unisoft` (AMS). Skills are markdown documents per workflow.
- 2026-04-02: Automation is a SEPARATE service from the email pipeline. Not a new pipeline stage. Agent picks up processed emails and acts on them independently.
- 2026-04-02: EffectiveDate = current date, ExpirationDate = +1 year. Confirmed from JC walkthrough — the policy effective date doesn't exist at quote stage (USLI PDF "Please bind effective: ___" is blank).
- 2026-04-02: FormOfBusiness accepts any single character. L=LLC, C=Corp, I=Individual, P=Partnership. Tested and confirmed.
- 2026-04-02: Unisoft API parameter names are CASE-SENSITIVE. QuoteID works, QuoteId returns null. Documented in proxy README.
- 2026-04-02: SetSubmission requires `PersistSubmission: "Insert"` as a top-level field (not inside the Submission object). Fixed in client.
- 2026-04-02: Granada Insurance is NOT in Unisoft's agent list or broker list (confirmed in UAT UI). Granada portal emails misclassified as agent_submission — these are internal, not agent-originated.
- 2026-04-02: Estrella Insurance has 66 franchise entries in Unisoft, each under a different DBA. Matching by franchise number (e.g., #326) is a real gap — some franchises aren't registered.
- 2026-04-02: Classification accuracy directly bounds automation success rate. Pipeline classification must be correct before automation runs at scale.
- 2026-04-02: The Unisoft CLI and automation code live in the GIC email intelligence repo (craig-indemn/gic-email-intelligence). The proxy code + research live in the OS repo (projects/gic-email-intelligence/).
- 2026-04-02: CLI entry point: `gic` (maps to gic_email_intel.cli.main:app). Subcommands: emails, submissions, extractions, automate, sync, stats, drafts, migrate.
- 2026-04-02: Agent uses Sonnet for automation (cost-effective, sufficient reasoning for the workflow).
- 2026-04-02: Vision from product roadmap: Unisoft CLI is an adapter. Eventually wraps into Indemn's own AMS CLI (`indemn quote create ...`) with Unisoft as a sync backend. Build for today, design for transition.
- 2026-04-03: PDF extraction overhauled: pdfplumber (local, free) + Haiku replaces Claude Vision. ~10x cheaper. Form extractor OCR kept as fallback for scanned PDFs.
- 2026-04-03: Only `agent_submission` emails need Quote ID automation. `gic_portal_submission` and `gic_application` already have Quote IDs from their respective portals (assumption — verify with JC).
- 2026-04-03: GIC and Granada are sister companies under Granada Financial Group. GIC is MGA with binding authority for Granada. Granada portal submissions landing in GIC's inbox are real work that GIC underwrites.
- 2026-04-03: Deep agent skill rewritten with business context (GIC/Granada relationship), three sub-patterns (direct agent, Granada portal, GIC forward), and data mapping guidance. Agent uses LLM intelligence to handle inconsistent field names across extraction types.
- 2026-04-03: Attachment upload to Unisoft is the next build item after classification refinement. `AddQuoteAttachment` via MTOM exists in the API but is not yet in the proxy. This closes the loop — making email submissions equivalent to portal submissions.

- 2026-04-07: Form extractor is the source of truth for ALL document extraction, not pdfplumber. pdfplumber is last-resort fallback only.
- 2026-04-07: No ad-hoc processing. All data processing runs through the same pipeline crons. Historical reprocessing = reset status to pending, let the cron pick it up.
- 2026-04-07: Submission enrichment from extraction data (name, LOB, agent, agency) runs in pipeline, not as backfill. Priority: AMS > Extraction > Classification > Email. No new LLM calls.
- 2026-04-07: "Submissions" renamed to "Applicants" in all user-facing UI. API/code paths remain "submissions".
- 2026-04-07: ApplicantPanel merge: AMS wins only when the specific AMS field has a value. Null AMS fields fall through to extraction/email data.
- 2026-04-07: Gap analysis temporarily removed from detail view — doesn't serve current AMS linkage objective. Re-enable for UW workflow.
- 2026-04-07: Automation failures reframed as "Needs attention" — not failed, just needs additional information or agency setup.
- 2026-04-08: Railway API service does NOT auto-deploy on git push. Must manually run `railway up -s api --environment development -d`.
- 2026-04-08: Portal-created quotes in Unisoft UAT are blank shells — Quote ID exists but no data populated. Expected to have full data in production.
- 2026-04-08: ~2,800 USLI carrier quotes have no original application in GIC's inbox — agents submitted directly to USLI's retail web portal. Whether to create Unisoft records for these is a question for JC.
- 2026-04-16: Tasks assigned to GROUP not individual users — AssignedToUser empty, GroupId set. Matches JC's "team picks it up from there" intent.
- 2026-04-16: Develop task creation in UAT with a self-created test group before touching prod. Prod has 2 groups (New Biz, New Biz Workers Comp).
- 2026-04-16: Build our own MongoDB-side duplicate detection (normalize name + address, search existing submissions) rather than relying solely on Unisoft's similar-name prompts.
- 2026-04-16: Rollout ordering — (1) Task creation in UAT → (2) Agency search phone+address fallback → (3) Own duplicate detection → (4) Prod cutover. Endorsements ingestion + activity reliability run in parallel.
- 2026-04-16: LOB → group routing — WC goes to `New Biz Workers Comp`; all other LOBs go to `New Biz`.
- 2026-04-17: Migrated ALL LLM calls from Claude Sonnet to Gemini 2.5 Pro/Flash via Vertex AI. Motivated by Anthropic credit exhaustion + existing Gemini credit. Uses SA `indemn/dev/shared/google-cloud-sa` (project `prod-gemini-470505`).
- 2026-04-17: Skill must be INLINED in system prompt, not loaded via deepagents SkillsMiddleware. Middleware expects directory-per-skill layout with SKILL.md; our flat-file never loaded. Claude inferred; Gemini didn't. Inlining is the reliable path for non-Claude models.
- 2026-04-17: Phase 2 (agency search) approach: sync full Unisoft agent data to MongoDB `unisoft_agents` collection, match locally with multi-field scoring (phone 40%, name 30%, address 15%, email 15%). Avoids broken `GetAgentsByAddress` proxy Criteria namespace collision.
- 2026-04-17: Dev crons paused via `PAUSE_AUTOMATION=true` and `PAUSE_PROCESSING=true` env vars in Railway. Crons fire but exit immediately. Prevents Gemini credit burn while we're not actively testing.
- 2026-04-17: Dual proxy architecture — UAT on port 5000, Prod on port 5001, same EC2 instance. Config-file-based (`{ServiceName}.env`), exe-filename-based service name detection. Fully reproducible from README.
- 2026-04-17: Prod SOAP endpoint is `services.gicunderwriters.co/management/imsservice.svc` (discovered from ClickOnce app config download, NOT the URL JC sent which was the ClickOnce download link). ClientId = `GIC`. WS-Security user = `UniClient` (same password as UAT).
- 2026-04-17: WCF DNS identity is REQUIRED for prod — `EndpointIdentity.CreateDnsIdentity("gicunderwriters.co")` must be set on the endpoint address. Without it, WCF message-level security context negotiation fails with `MessageSecurityException` even if credentials are correct and cert validation is skipped. This is NOT a cert issue — it's a WCF secure conversation requirement.
- 2026-04-17: Prod task groups: NEW BIZ = GroupId 3, NEW BIZ Workers Comp = GroupId 4. Update the automation skill with these IDs when switching to prod.
- 2026-04-22: Write access to quotes inbox obtained (TJ at Grove Networks). Unblocks email-to-subfolder move.
- 2026-04-22: JC confirmed ready for production. Going live 2026-04-23. JC will send underwriter assignment field details.
- 2026-04-22: Need to set underwriter/AssignedTo on quote creation — `indemnai` is the "Instant Quote" user JC created for this purpose. Waiting on JC for which field his team looks at.

## Open Questions (deferred — not blocking demo)
- How does RingCentral data merge into the same pipeline? (Same pattern: RingCentral CLI + skills)
- How do we handle the bilingual aspect? (Classifier skill handles Spanish; draft generator needs Spanish templates)
- Business-line-specific requirements beyond GL? (Each LOB gets a config file following GL pattern, expand post-demo)
- Multi-tenancy for other brokers? (Add tenant_id to all collections if needed)
- Email sending in production? (Requires Mail.Send permission, separate Entra consent from GIC)

## Open Questions (Unisoft Integration)
- ~~What does the quoting API actually support?~~ **ANSWERED 2026-04-01:** 910 SOAP operations via WCF, 32 REST endpoints. Full CRUD for quotes, submissions, activities, policies, agents, carriers, claims. Mapped via Fiddler interception + WSDL fetch.
- Is the Granada API (`services-uat.granadainsurance.com`) built by Unisoft or custom by Mukul Gupta?
- ~~What are all the subline options per LOB in Unisoft?~~ **ANSWERED 2026-04-01:** All 18 LOBs and all sub-LOBs mapped from live API. See explore-results.txt. CG has 4, CP has 13, PL has 8, TR has 8, ML has 4, HO has 2, OM has 2. Others have none.
- Do GIC portal submissions auto-create records in Unisoft? **ASSUMPTION 2026-04-03:** Yes. `gic_portal_submission` emails include the Quote ID in the subject (e.g., "144301"). `gic_application` emails (HandyPerson/General Contractor portal confirmations from quote@gicunderwriters.com) are assumed to also auto-create Quote IDs, though the ID isn't in the email body. **Verify with JC.** If confirmed, only `agent_submission` emails need Quote ID automation.
- Does Unisoft support ACORD data standards?
- Is there a production API endpoint (not just UAT)? **Still need from JC/Robert.**
- ~~Can documents be uploaded via API?~~ **ANSWERED 2026-04-01:** Yes, AddQuoteAttachment via MTOM (IINSFileService). Not yet in proxy (uses different WCF channel + multipart encoding). Can be added later.
- Can we get webhook/event notifications from Unisoft? (SignalR hub exists at `ins-gic-nothub-prod-app.azurewebsites.net` — could potentially subscribe to events, needs investigation)

## Open Questions (Workflow Understanding — To Answer Through Alignment)
- Which part of the workflow is fuzziest? Decision-making ("how do they know what to do?"), data entry ("what gets typed where?"), or end-to-end flow ("what triggers what?")?
- From JC's walkthrough, what surprised Craig? Surprises point to wrong assumptions we might be carrying.
- How do we frame the automation? "Pre-fill so they click save" vs "end-to-end with review" vs something else?
- The "delete from Outlook = done" coordination — are we replacing it or augmenting it?
- What does "done" mean for each email type? Is it always "entered into Unisoft" or are there different endpoints?
- How does the team decide which carrier to submit to? Rule-based or judgment-based?
- What's the decision tree for "needs more info" vs "ready to submit"?
- Why has personal liability "never been efficiently put into the management system"? What's different about it?

## UAT Access (confirmed 2026-03-30)
- URL: `https://ins-gic-client-uat-app.azurewebsites.net/publish.htm`
- Username: `ccerto` / Password: `GIC2026$$!`
- Platform: ClickOnce Windows app (Azure-hosted) — requires Windows
- API: Pending — JC emailed Robert Gonzalez (robert@unisoftonline.com) 2026-03-30 for swagger docs, no reply
- Also requested: endorsements@gicunderwriters.com read-only access (JC → Mukul, 2026-03-31)
