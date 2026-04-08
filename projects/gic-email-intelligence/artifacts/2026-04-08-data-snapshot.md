---
ask: "Complete picture of processed vs unprocessed data, time periods, AMS linkage, and UI visibility"
created: 2026-04-08
workstream: gic-email-intelligence
session: 2026-04-07a
sources:
  - type: mongodb
    description: "gic_email_intelligence database — emails, extractions, submissions collections"
  - type: railway
    description: "Cron service status and logs"
---

# Data Snapshot — 2026-04-08

## Email Corpus

| Metric | Value |
|--------|-------|
| Total emails | 3,948 |
| Date range | Sep 29, 2025 → Apr 8, 2026 (6 months) |
| Inbox | quote@gicunderwriters.com |
| Sync | Live, every 5 min via MS Graph API |
| Last sync | 2026-04-08 15:35 UTC |

### Daily email volume (last week)
| Date | Emails |
|------|--------|
| Apr 8 (Wed) | 62 |
| Apr 7 (Tue) | 157 |
| Apr 6 (Mon) | 123 |
| Apr 5 (Sun) | 4 |
| Apr 4 (Sat) | 10 |
| Apr 3 (Fri) | 58 |
| Apr 2 (Thu) | 170 |
| Apr 1 (Wed) | 122 |

## Processing Pipeline

All three stages run via Railway cron. Pipeline order: extract → classify → link.

| Stage | Status | Coverage |
|-------|--------|----------|
| Extraction (form extractor + pdfplumber) | Active, every 5 min | 98.7% (3,608 of 3,657 emails with PDFs) |
| Classification | Active, every 5 min | 99.5% (3,930 classified, 18 unclassified) |
| Linking (email → submission) | Active, every 5 min | 3,575 submissions created from 3,948 emails |
| Processing complete | — | 96.7% (3,818 of 3,948 at `complete` status) |

**Gaps:** 28 emails with PDFs but no extractions — mostly non-document attachments (voicemails, phishing alerts, daily reports). 6 emails received today still processing (normal lag).

### Email type distribution
| Type | Count | % | Description |
|------|-------|---|-------------|
| usli_quote | 2,632 | 67% | USLI carrier quote responses |
| usli_pending | 366 | 9% | USLI needs more info |
| usli_decline | 233 | 6% | USLI declined |
| agent_submission | 191 | 5% | New applications from retail agents |
| agent_reply | 154 | 4% | Agent responding to info request |
| other | 91 | 2% | Various |
| agent_followup | 56 | 1% | Agent checking status |
| gic_portal_submission | 54 | 1% | Applications via Unisoft portal |
| gic_internal | 33 | 1% | Internal GIC communication |
| gic_application | 28 | 1% | Granada portal applications |
| renewal_request | 21 | <1% | Renewal of existing policy |
| unclassified | 18 | <1% | Not yet classified |
| hiscox_quote | 14 | <1% | Hiscox carrier quotes |
| report | 53 | 1% | Automated reports |
| gic_info_request | 4 | <1% | GIC requesting info |

## AMS Linkage (Unisoft)

| Metric | Value |
|--------|-------|
| Total linked | 131 of 3,575 submissions (3.7%) |
| Via automation (deepagent) | 104 |
| Via portal (reference number) | 27 |
| Not linked | 3,444 |

### Why most are not linked

| Category | Count | Reason |
|----------|-------|--------|
| USLI direct portal submissions | ~2,800 | Agent submitted to USLI directly, bypassing GIC email. No application email exists, so no Quote ID was ever created in Unisoft. **Question for JC: should we auto-create these?** |
| Agent submissions — failed automation | 68 | Agency not in Unisoft (37 confirmed missing), misclassified (5, now fixed), missing data (6), disambiguation failure (7) |
| Agent submissions — pending | 2 | Not yet processed by automation cron |
| Other types | ~550 | Agent replies, followups, renewals, internal — don't have their own Quote IDs |

### AMS automation by date
| Date | Completed | Failed |
|------|-----------|--------|
| Apr 8 (Wed) | 10 | 4 |
| Apr 7 (Tue) | 19 | 14 |
| Apr 6 (Mon) | 88 | 46 |
| Apr 3 (Fri) | 1 | 0 |
| Apr 2 (Thu) | 1 | 4 |

**The bulk on Apr 6** was the initial batch run. Apr 7-8 is the cron running every 15 min on new emails plus retries of fixes.

### Automation success rate: 63.6%
- 119 completed, 68 failed, 2 processing, 2 pending
- All failures investigated — 37 agencies confirmed not in Unisoft, rest are classification/data issues (now fixed)

## Active Infrastructure

| Service | Schedule | Status |
|---------|----------|--------|
| Sync (Outlook → MongoDB) | Every 5 min | Running |
| Processing (extract → classify → link) | Every 5 min | Running |
| Automation (deepagent → Unisoft) | Every 15 min | Running |
| API (FastAPI on Railway) | Always on | Running |
| UI (React on Amplify) | Auto-deploy on push | Running |

## What's visible in the UI

| Feature | Visible? | Notes |
|---------|----------|-------|
| Applicant queue with all submissions | Yes | Renamed from "Submissions" to "Applicants" |
| AMS status (Q:ID, Auto/Portal badges) | Yes | In AMS column |
| AMS filter (Linked/Auto/Portal/Failed/Not linked) | Yes | Dropdown filter |
| Email type filter (New Apps/Carrier/Portal/Agent) | Yes | Dropdown filter |
| Failure reasons | Yes | "Failed" badge with truncated reason, full on hover |
| Filter persistence across navigation | Yes | Overlay pattern |
| Applicant data merged (email + AMS) | Yes | Detail view right column |
| Source indicators (Both/AMS/Email) | Yes | Icons on each field |
| Automation banner | Yes | Detail view shows success/failed/portal/none |
| Pipeline stepper | Yes | Compact 8-stage dots |
| Insights/analytics | Yes | Volume, types, agents, automation section |

## What's NOT clear in the UI

1. **No extraction status indicator** — can't tell from the queue which applicants have rich data vs minimal
2. **"Not linked" is ambiguous** — could mean "hasn't been automated yet" or "can't be linked" (USLI direct). No distinction.
3. **No daily activity view** — can't see "what happened today" or "what's new since yesterday"
4. **Automation activity timeline** — Insights shows totals but not daily trends of automation completions/failures
