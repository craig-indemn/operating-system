---
ask: "What types of emails are in GIC's quote inbox, and which ones need Quote IDs?"
created: 2026-04-03
workstream: gic-email-intelligence
session: 2026-04-03a
sources:
  - type: mongodb
    description: "Classification distribution from gic_email_intelligence.emails on dev Atlas cluster"
---

# GIC Quote Inbox — Classification Snapshot

**Date:** 2026-04-03
**Database:** `gic_email_intelligence` on dev Atlas (`dev-indemn.pj4xyep.mongodb.net`)
**Total emails:** 3,548
**Date range:** 2025-09-29 to 2026-04-02 (~6 months)
**Pipeline status:** Sync and processing crons paused. 12 emails unclassified.

## Full Distribution

| Type | Count | % | Description |
|---|---|---|---|
| usli_quote | 2,567 | 72.4% | USLI sent back a quote |
| usli_pending | 348 | 9.8% | USLI needs more info before quoting |
| usli_decline | 211 | 5.9% | USLI declined to quote |
| agent_submission | 122 | 3.4% | Retail agent emailing applications/attachments for new quote |
| agent_reply | 104 | 2.9% | Agent responding to info request from GIC |
| other | 42 | 1.2% | Voicemails, spam, newsletters |
| agent_followup | 31 | 0.9% | Agent checking on status/timeline |
| report | 29 | 0.8% | Bounce-backs, automated reports |
| gic_application | 23 | 0.6% | GIC staff creating a new submission (often forwarded from agents) |
| gic_internal | 16 | 0.5% | GIC staff communicating internally |
| gic_portal_submission | 16 | 0.5% | Auto-generated from GIC/Unisoft web portal |
| UNCLASSIFIED | 12 | 0.3% | Pipeline hasn't processed yet |
| renewal_request | 12 | 0.3% | Renewal of existing policy |
| hiscox_quote | 11 | 0.3% | Hiscox carrier quote |
| gic_info_request | 4 | 0.1% | GIC asking agent for more info |

## Grouped by Automation Action

### Carrier Responses (88%) — Already have a Quote ID
- **usli_quote** (2,567), **usli_pending** (348), **usli_decline** (211), **hiscox_quote** (11)
- Total: 3,137 emails
- These are responses to existing submissions. The Quote ID already exists in Unisoft.
- **Automation action:** Log carrier response as an activity against existing Quote ID.

### New Business (5%) — Need a Quote ID created
- **agent_submission** (122), **gic_application** (23), **gic_portal_submission** (16), **renewal_request** (12)
- Total: 173 emails
- These are new quote requests that need a Quote ID created in Unisoft.
- **Automation action:** Create Quote ID (LOB, SubLOB, Agency), then create Submission, then log Activity.

### Ongoing Conversation (4%) — About existing quotes
- **agent_reply** (104), **agent_followup** (31), **gic_info_request** (4), **gic_internal** (16)
- Total: 155 emails
- No Quote ID creation needed. These attach to existing quotes.
- **Automation action:** Link to existing submission, update status if applicable.

### Noise (2%) — No action needed
- **other** (42), **report** (29), **UNCLASSIFIED** (12)
- Total: 83 emails
- Voicemails, bounce-backs, newsletters, unprocessed emails.
- **Automation action:** None.

## Notes

- The 122 `agent_submission` emails include some Granada portal emails and GIC internal forwards. Classification accuracy for this type needs review — see Work Item 2 in INDEX.md.
- `gic_portal_submission` now has 16 hits (was 0 in earlier analysis — the pipeline has been processing).
- 88% of the inbox is automated USLI notifications. Only 5% of emails need the Quote ID creation workflow.
- Extraction overhaul completed 2026-04-03: pdfplumber + Haiku replaces Claude Vision (~10x cheaper).
