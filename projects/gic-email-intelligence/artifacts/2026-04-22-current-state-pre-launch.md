---
ask: "Snapshot of exactly where everything stands before production launch — what works, what needs changing, what's blocking"
created: 2026-04-22
workstream: gic-email-intelligence
session: 2026-04-22a
sources:
  - type: codebase
    description: "Full code review of pipeline, agent, skill, CLI — all source files read"
  - type: unisoft-uat
    description: "End-to-end test: LUSSO STONE DESIGN LLC → Quote 17345, Task 16856"
  - type: google-doc
    ref: "https://docs.google.com/document/d/1Tb07Om95dllD9Fg4BqCWk0ny0b7GTaKPvYU3ndtsxJA"
    name: "JC call Apr 22 — production rollout decisions"
---

# Current State — Pre-Launch Snapshot (Apr 22, 2026)

## What We Tested Today

### Full Pipeline Test (LUSSO STONE DESIGN LLC)
- **Email:** `69e8e29537cce43fd4593b38` from `quote@granadainsurance.com`
- **Extract:** Form extractor (primary path, NOT fallback) → Gemini 2.5 Pro → 21 fields including Producer Code 5820, phone, address
- **Classify:** `agent_submission`, LOB = General Liability, insured = Lusso Stone Design LLC
- **Link:** Created new submission, linked
- **Enrich:** Agent name (Luis Benitez) and agency name (Doral Insurance Advisors, Inc.) populated
- **Automate:** Agent found agency by producer code 5820, created Quote 17345, uploaded attachment, created Task 16856 in UAT group 2

### Bugs Found and Fixed
1. **`EXTRACTIONS` not imported in harness.py** — enrichment step was crashing on every email, marking them `failed`. Fixed: added `EXTRACTIONS` to import statement.
2. **Field name mapping missed capitalized variants** — Gemini Pro returns `Producer Name`, `Applicant Name` (human-readable) vs the snake_case the mapping expected (`producer_name`, `applicant_name`). Fixed: added capitalized variants to FIELD_MAP. Also moved `producer_name`/`Producer Name` to `retail_agency_name` (producer = agency, not individual agent).

## Infrastructure Status

| Component | Status |
|-----------|--------|
| Sync cron (Railway) | Running — last sync 17:00 UTC, 5,555 emails total |
| Processing cron (Railway) | PAUSED since Apr 16 |
| Automation cron (Railway) | PAUSED since Apr 16 |
| EC2 proxy UAT (:5000) | Running |
| EC2 proxy Prod (:5001) | Running |
| Form extractor | Working (devformextractor.indemn.ai) |
| Gemini Vertex AI | Working (rate limits hit occasionally, retry logic handles) |
| MongoDB (dev-indemn Atlas) | 5,555 emails, 514 pending |

## What Needs to Change for Production (from JC call)

### Must-Have Before Launch

| # | Change | Current | Needed | Status |
|---|--------|---------|--------|--------|
| 1 | **Task due date** | Next business day | Same day as email received | Code change needed |
| 2 | **Underwriter/AssignedTo** | Not set (empty) | User JC will provide | Waiting on JC email |
| 3 | **Activity type** | ActionId 6 "Application received from agent" | "Application acknowledgement" (sends email to agent) | Need to find ActionId, may need underwriter set first |
| 4 | **Skill GroupIds** | GroupId 2 (UAT test) | GroupId 3 (NEW BIZ), GroupId 4 (WC) | Code change in skill |
| 5 | **Entered-by user** | `ccerto` | `indemnai` | Code change in CLI defaults or skill |
| 6 | **Railway env vars** | UAT proxy (port 5000) | Prod proxy (port 5001) + prod API key | Railway config change |
| 7 | **Sync prod agents** | 1,571 UAT agents | Prod agents (may differ) | Run `unisoft agents sync` against prod |
| 8 | **Upload email as attachment** | Not implemented | Upload the actual email (.eml or rendered) into Unisoft applications subfolder | New feature needed |
| 9 | **Attachment subfolder routing** | All go to root attachments | Applications go to "applications" subfolder | Need to investigate Unisoft API for folder targeting |
| 10 | **Email folder move** | Not implemented | Move processed emails to "indemn processed" subfolder | Graph API Move action |
| 11 | **Create inbox folders** | Don't exist | "indemn process" and "indemn processed" folders | Graph API CreateFolder |

### Nice-to-Have (Not Blocking Launch)

| # | Change | Notes |
|---|--------|-------|
| 12 | USLI instant quote processing | Future phase — create quote + "send offer to agent" activity |
| 13 | Endorsements processing | Same pipeline, different skill — deferred |
| 14 | Inbox analysis doc for JC/investors | JC wants the analysis shared |
| 15 | LangChain deprecation warning | ChatVertexAI deprecated, switch to ChatGoogleGenerativeAI |

### Activity Change Detail

**Current flow (UAT):**
- Step 7: `unisoft activity create --quote-id N --action-id 6 --notes "Application received from agent via email automation"`
- ActionId 6 = "Application received from agent" — audit trail only, no notification

**Needed flow (Production):**
- Step 7: `unisoft activity create --quote-id N --action-id {TBD} --notes "..."`
- Activity = "application acknowledgement" — sends email to agent contact with quote ID
- **Requires underwriter/agent contact to be set on the quote first** — the activity email says "the account manager assigned to your submission is {underwriter}"
- Craig's note: In dev, use the current activity (ActionId 6) AFTER underwriter is assigned, not the acknowledgement one (which would send real emails). Switch to acknowledgement only in production.

### Due Date Change Detail

**Current:** `cli.py` line 325-333 calculates next business day (Mon-Fri skip)
**Needed:** Use the email's `received_at` date (same day), not today + 1 business day

This means the task CLI needs to accept a `--due-date` override, or the skill needs to pass the email's received date.

## Data Snapshot

- **Total emails:** 5,555
- **Pending (unprocessed):** 514 (Apr 16-22, processing paused)
- **Today's emails:** 67 (all pending)
- **Processing status breakdown:** 4,767 complete, 514 pending, 273 failed, 1 classified
- **Automation:** 163 AMS-linked (135 automation, 28 portal), ~60% rate on agent_submissions

## Production Launch Sequence (Updated from JC Call)

1. JC alerts team today → catch up on old inbox items
2. Craig prepares checklist and deployment overview → send to JC
3. JC emails underwriter user to Craig
4. Craig makes code changes (due date, underwriter, activity, GroupIds, entered-by)
5. Craig syncs prod agents to MongoDB
6. Craig creates inbox folders (indemn process, indemn processed)
7. Craig updates Railway env vars for prod proxy
8. Craig deploys latest code to Railway
9. **Apr 23 at 12:01 AM ET:** Enable automation with date filter (only emails from Apr 23+)
10. Thursday morning: all hands monitoring
11. Midday decision: let it ride or pause for fixes
