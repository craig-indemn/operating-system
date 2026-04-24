---
ask: "Go-live day session 2 — monitoring, fixes, and feature additions during first full production day"
created: 2026-04-23
workstream: gic-email-intelligence
session: 2026-04-23b
sources:
  - type: codebase
    description: "15+ commits across pipeline, automation, proxy, and skill files"
  - type: unisoft-prod
    description: "44 agent submissions automated, 43 completed, 0 notification failures after fix"
  - type: mongodb
    description: "152 emails processed, classification rules refined, folder workflow live"
  - type: langsmith
    description: "Used for root cause analysis on earlier session's issues"
  - type: railway
    description: "All 4 prod services running: sync, processing, automation, api"
---

# Go-Live Day Session 2 — 2026-04-23

## Summary

Production monitoring and improvement session on the first full day of go-live. Started with 22 emails processed from the morning session. Ended with 152 emails, 44 agent submissions automated (43 completed, 1 legitimate failure), and multiple systemic improvements deployed.

## Production Results

| Metric | Value |
|--------|-------|
| Total emails processed | 152 |
| Agent submissions automated | 44 (43 completed, 1 failed — agency not found) |
| Duplicate quotes created | 0 (all duplicates linked to same quote) |
| Processing failures | 0 (after ObjectId fix) |
| Notification emails sent | Working (verified on Q:146337) |

## Issues Found and Fixed

### 1. Emails not moved to "indemn processed" folder
- **Symptom:** First 2 automated emails stayed in Inbox
- **Root cause:** Those emails were automated before the `--move-to` flag was added to the skill (morning session)
- **Fix:** Verified they were already moved externally (404 from Graph API). Updated MongoDB.

### 2. Agent Contact not set on quotes
- **Symptom:** `AgentContactID: 0` on all automated quotes
- **Root cause:** No mechanism to look up agent contacts. Unisoft has a `GetContacts` operation (AssociationType=3) that returns contacts by agent number.
- **Fix:** 
  - Added `get_contacts()` to `unisoft_client.py`
  - Added `unisoft contacts list --agent-number N` CLI command
  - Added `--agent-contact-id` flag to `unisoft quote create`
  - Updated skill Step 3.7 to look up contacts before creating quote
- **Verified:** Q:146274 onwards has `AgentContactID` set correctly

### 3. Applicant email vs agent email confusion
- **Symptom:** Email field on quotes sometimes had agent's email instead of applicant's
- **Root cause:** Extraction captures both `Email` (agent) and `Applicant Email` (insured) — skill didn't distinguish
- **Fix:** Added explicit guidance to skill: use `Applicant Email` from ACORD 125, never `Email`/`agent_email`/`from_address`

### 4. Multi-LOB creating two quotes
- **Symptom:** MEY ENTERPRISE got Q:146250 (GL/Liquor) + Q:146251 (CP) — should be one quote
- **Root cause:** System created one submission per LOB, automation created one quote per submission
- **Fix:** 
  - Added LOB/SubLOB Decision Rules to skill (GL+CP → CP/PK Package, restaurant GL → CG/HM, contractor GL → CG/AC)
  - Changed linker to create single submission for multi-LOB
  - Made rules explicit with reasoning, not a terse table
- **Decision:** LLM handles this (not deterministic code) because there are many nuances the LLM can read from extraction context

### 5. Sync service stopped after deploy
- **Symptom:** 11 emails sitting in inbox unsynced for 1+ hour
- **Root cause:** Sync crashed with `KeyError: 'address'` — an email had a recipient with no `emailAddress.address` field. Additionally, the cron schedule was missing, and the sync service had no cron set on production.
- **Fix:**
  - Safe `.get()` access for recipient email addresses in sync.py
  - Set cron `*/5 * * * *` via Railway GraphQL API
  - Discovered `railway up` is needed (not just `git push`) because services aren't connected to GitHub for auto-deploy
  - Learned prod proxy binary is `UniProxy-Prod.exe` (not `UniProxy.exe`) — must copy after compile

### 6. Processing too slow (1 email per cron tick)
- **Root cause:** `--workers 1` (sequential), each email takes 30-45s (2-3 LLM calls)
- **Fix:** Set `--workers 3` on processing start command via Railway API. Cleared backlog 3x faster.

### 7. Application Acknowledgement email not sending
- **Symptom:** Activities created but `Notification` object empty, no email sent
- **Root cause investigation:**
  - First thought: `AgentNo: 0` on activity → fixed by auto-resolving from quote
  - Second: `AgentNo` set but still no notification → the `SetActivity` API alone doesn't send emails
  - Third: Tried `SetActivityNotification` (separate SOAP operation) → deserialization error in proxy
  - Fourth: Debugged proxy XML generation (discovered prod binary is `UniProxy-Prod.exe`, not `UniProxy.exe`)
  - **Final fix:** Pass populated `Notification` object INSIDE the `Activity` DTO on `SetActivity`. One call creates activity AND sends email. This is how the Unisoft UI does it.
- **Verified:** Q:146337 → notification sent to `anita@gcainsurance.com`, subject "We're working on it!"

### 8. Activity/notification was LLM-dependent (unreliable)
- **Symptom:** LLM agent sometimes skipped Step 7 (activity creation)
- **Fix:** Made it deterministic — `gic emails complete --quote-id N` automatically creates the activity and sends the notification. No LLM involvement. The function resolves everything from the quote ID: agent number, contact email, notification template, merge fields.

### 9. ObjectId corruption by LLM
- **Symptom:** VELMURUGAN RAJAPPAN failed repeatedly with `'69ea2395a8b74a4c97555b4t' is not a valid ObjectId`
- **Root cause:** Gemini LLM corrupts hex characters when passing ObjectId strings to tool calls (`7` → `t`)
- **Fix:** Added `_safe_object_id()` in tools.py that recovers from corruption by trying all 16 hex variants for each non-hex character against the database

### 10. Portal classification rule too broad
- **Symptom:** All `quote@gicunderwriters.com` "Application Request" emails classified as `gic_application` (skipping automation)
- **Root cause:** Hard rule #7 treated ALL portal submissions the same. JC confirmed only 4 product lines have Quote IDs: Boats & Yachts, Workers Compensation, Welders, Caterers.
- **Fix:** Rule 7 now checks the product line prefix in the subject. Only those 4 → `gic_application`. All others (HandyPerson, Rental Dwelling, Commercial Auto, General Contractor, etc.) → `agent_submission`.
- **Additional fix:** Rule 7 now fires regardless of what the LLM classified (was only overriding `agent_submission`, missed `gic_portal_submission`)

### 11. Graph API message ID changes on folder move
- **Symptom:** Emails moved to "Indemn - Processing" couldn't be moved again (404)
- **Root cause:** Graph API returns a NEW message ID when moving between folders. We weren't updating `graph_message_id` in MongoDB.
- **Fix:** `move_email_to_folder()` now captures the new ID from the move response and updates MongoDB

## Features Built

### Email Folder Workflow
Emails move between Outlook folders as they progress through the pipeline:
1. **Classified as `agent_submission`** → moved to "Indemn - Processing" (claiming it)
2. **Automation succeeds (new quote)** → moved to "indemn processed"
3. **Automation succeeds (duplicate)** → moved to "Duplicates"
4. **Automation fails** → moved back to Inbox (released for manual handling)

Implementation: `core/email_mover.py` shared helper, auto-creates folders, non-fatal on errors.

### Deterministic Activity + Notification
`gic emails complete --quote-id N` automatically:
1. Calls `GetQuote` to resolve AgentNo, Name, AgentContactID
2. Fetches notification template via `GetActionNotifications`
3. Resolves contact email via `GetContacts`
4. Renders merge fields: `[NoticeDate]`, `[ApplicantName]`, `[QuoteId]`
5. Creates activity with populated Notification via `SetActivity` (one call)
6. Skips all of this for duplicate emails

### Duplicate Detection → Folder Routing
When `emails complete --quote-id N` runs, checks if the submission already had that quote_id BEFORE this email was processed. If yes → duplicate → "Duplicates" folder, no activity/notification. Check happens before denormalization to avoid false positives.

### Agent Contact Lookup
- `unisoft contacts list --agent-number N` — calls `GetContacts` (AssociationType=3)
- `--agent-contact-id` flag on `unisoft quote create`
- Skill Step 3.7 instructs agent to look up contacts

### Processing Parallelization
- `--workers 3` on processing start command
- Clears email backlogs ~3x faster

## Infrastructure State

### Railway Production
| Service | Status | Start Command | Cron |
|---------|--------|---------------|------|
| sync | Running | `python scripts/run_with_primary.py outlook-inbox sync` | */5 * * * * |
| processing | Running | `outlook-agent process --batch --workers 3` | */5 * * * * |
| automation | Running | `gic automate run -t agent_submission` | */5 * * * * |
| api | Running | uvicorn | continuous |

### Key Lessons Learned
1. **`railway up` is required** — `git push` triggers builds but services may not auto-deploy. Always `railway up -s <service>` from local code.
2. **Prod proxy binary is `UniProxy-Prod.exe`** — must `Copy-Item` after compiling to `UniProxy.exe`
3. **Use `aws s3 cp` on EC2** — `Read-S3Object` (PowerShell) silently fails to overwrite. Use `aws s3 cp` instead.
4. **Graph API message ID changes on move** — must capture new ID from move response
5. **LLMs corrupt hex strings** — ObjectId recovery needed for any tool that accepts IDs from LLM
6. **Notifications go inside SetActivity** — not via separate `SetActivityNotification` call (deserialization issues in proxy)
7. **Dev crons should be disabled** — all dev crons (sync, processing, automation) disabled to avoid noise

### Env Vars Added This Session
| Service | Variable | Value |
|---------|----------|-------|
| processing (prod) | GRAPH_CLIENT_ID | 4bf2eacd-... |
| processing (prod) | GRAPH_CLIENT_SECRET | 1qD8Q~... |
| processing (prod) | GRAPH_TENANT_ID | 7c0931fd-... |
| processing (prod) | GRAPH_USER_EMAIL | quote@gicunderwriters.com |

## Files Changed (Key Commits)

| File | Change |
|------|--------|
| `core/email_mover.py` | **NEW** — shared folder move helper with ID tracking |
| `agent/harness.py` | Classification rule 7 rewritten (portal product lines), folder move after classification |
| `agent/tools.py` | `_safe_object_id()` for LLM hex corruption recovery |
| `cli/commands/emails.py` | Deterministic activity+notification, duplicate detection, folder routing |
| `cli/commands/sync.py` | Safe `.get()` for recipient addresses |
| `automation/agent.py` | Added contacts CLI to system prompt |
| `automation/skills/create-quote-id.md` | Multi-LOB rules, applicant email guidance, contact lookup step, simplified Step 7+8 |
| `agent/skills/submission_linker.md` | Single submission for multi-LOB |
| `unisoft-proxy/client/cli.py` | Contacts list, agent-contact-id, notification builder |
| `unisoft-proxy/client/unisoft_client.py` | get_contacts() method |
| `unisoft-proxy/server/UniProxy.cs` | ActivityNotification DTO namespace |

## Open Items (updated 2026-04-24)

### RESOLVED
1. ~~VELMURUGAN RAJAPPAN~~ — processed, Q:146307, automated successfully
2. ~~Rental Dwelling classification~~ — confirmed by JC: only Boats/Yachts, WC, Welders, Caterers are exempt. Implemented.
3. ~~MEY ENTERPRISE duplicate quote~~ — JC handled manually
4. ~~BUILDERS SERVICES~~ — legitimate agency gap, moved to Inbox for manual handling
5. ~~SetActivityNotification proxy~~ — not needed, inline Notification in SetActivity works

### ACTIVE — Notification delivery inconsistency (PRIORITY)
The Application Acknowledgement notification is **intermittently failing in production**. This is the #1 issue for the next session.

**What works:**
- `_create_activity_and_notify()` works perfectly when run locally (tested on Q:146341, Q:146348 — both sent successfully)
- Q:146337 sent notification in production (anita@gcainsurance.com)
- The activity IS created correctly in production every time (ActionId 197, AgentNo set)

**What doesn't work:**
- Q:146340, 146336, 146334, 146348, 146350 — activity created but Notification object is empty in Unisoft
- The `Notes` field on the activity is also empty in production but should have text — suggesting the proxy is dropping some DTO fields during serialization

**What we know:**
- The code path IS being executed (activity gets created with correct ActionId/AgentNo)
- The Notification object IS being built (tested locally)
- The `SetActivity` payload includes both `Notes` and `Notification` when built locally
- But Unisoft receives the activity WITHOUT Notes and WITHOUT Notification populated
- This points to a **proxy serialization issue** — the C# proxy may be dropping fields from the Activity DTO under certain conditions
- WCF DataContractSerializer requires strict alphabetical field ordering — a field out of order is silently ignored
- The proxy's `AppendDtoField` sorts alphabetically, but there may be edge cases with nested DTOs

**Debug approach for next session:**
1. Use the `Debug_` prefix endpoint on the proxy to capture the exact XML being sent for a SetActivity call that includes Notification
2. Compare with the working Q:146337 XML (if captured) and the raw SOAP capture in `research/unisoft-api/raw-payloads/soap/IIMSService__SetActivity.txt`
3. Check if the issue is field ordering, namespace, or a specific field value (like HTML in EmailMessageBody) breaking serialization
4. The proxy binary on EC2 is `UniProxy-Prod.exe` — must deploy using: `aws s3 cp` → compile → `Copy-Item UniProxy.exe UniProxy-Prod.exe`

**Stderr traceback logging added** — next production failure should show the full traceback in Railway logs if there's a Python-side exception. If no traceback appears, the issue is proxy-side (XML serialization).

### ACTIVE — LangSmith tracing broken
- Zero traces in either `gic-email-automation` or `gic-email-processing` projects
- The `LANGCHAIN_*` env vars are set on Railway services
- The `_langsmith_config()` in `agent.py` builds a tracer callback
- Likely broke during `railway up` deploys — may need `langsmith` package explicitly in dependencies or the tracer setup changed
- Not blocking but useful for debugging

## To Resume Next Session

1. Read this artifact for full context
2. Read `artifacts/2026-04-23-go-live-day-handoff.md` for morning session context
3. Check `gic.indemn.ai` for current email/automation status
4. Check MongoDB: `mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/gic_email_intelligence" --eval 'db.emails.countDocuments({received_at:{$gte:ISODate("2026-04-24T00:00:00Z")}})'`
5. Continue monitoring and improving
