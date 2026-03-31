---
ask: "Redesign the GIC Email Intelligence UI for JC's daily use — searchable, filterable, sortable submissions table with Outlook folder awareness, expandable email rows, and a clearer detail view layout"
created: 2026-03-31
workstream: gic-email-intelligence
session: 2026-03-31-b
sources:
  - type: user-feedback
    description: "Craig brainstorming session — JC uses Outlook as a to-do list, enters data into AMS, deletes processed emails"
  - type: codebase
    description: "ui/src/pages/SubmissionQueue.tsx, ui/src/pages/RiskRecord.tsx, src/gic_email_intel/api/routes/submissions.py, src/gic_email_intel/cli/commands/sync.py"
---

# UI Polish: Data-First Submissions Table + Detail Clarity

## Context

The GIC Email Intelligence UI is functionally complete and deployed at `gic.indemn.ai`. Before giving JC (EVP/CUO) daily access, the UI needs to be polished for his actual workflow:

- JC uses **Outlook as a to-do list** — he reads emails, enters data into Unisoft AMS, then deletes the email
- The app should be a **structured view of their Outlook inbox** — not a workflow tool, not a triage dashboard
- Outlook folder status (Inbox, Deleted Items, USLI folder) tells JC what's been processed vs. what hasn't
- The primary goal is showing **what data has been extracted from emails** in a searchable, filterable, sortable way

## Design

### 1. Submission Table Enhancements (SubmissionQueue)

#### 1a. Expandable rows — inline email list

Each submission row gets a chevron on the left. Clicking the chevron (not the row itself) expands an inline email table underneath, indented:

| | Subject | From | Folder | Received | Attachments |
|---|---|---|---|---|---|
| | RE: GL Quote - Plaza 6201 | Mike Torres | Inbox | Mar 5 | 2 PDFs |
| | FW: ACORD 125 attached | Sarah Kim | Deleted Items | Mar 3 | 1 PDF |

- Clicking the row itself still opens the full RiskRecord detail view (existing behavior)
- Email data fetched on expand (not preloaded) via new lightweight endpoint
- Folder column shows the Outlook folder name (Inbox, Deleted Items, Inbox/USLI, etc.)
- Attachment count shows how many downloadable files each email has

#### 1b. New columns

| Column | Description | Replaces |
|--------|-------------|----------|
| **Emails** | Count badge (e.g., "3") showing number of linked emails | Nothing (new) |
| **Folder** | Dominant Outlook folder for the submission's emails. Shows "Inbox" if any email is in Inbox, otherwise "Deleted Items", etc. | **Action needed** (removed) |

The "Action needed" column is removed — it's based on ball_holder/draft logic that isn't relevant to JC's current data-entry workflow.

#### 1c. New filter: Folder status

Added to the existing filter bar alongside Stage, Line, Retail Agent, Sort, and Hide Auto-Notified:

| Value | Meaning |
|-------|---------|
| All | Default — no folder filter |
| Has emails in Inbox | At least one linked email is still in the Inbox (not yet processed by JC) |
| All deleted | Every linked email has been moved to Deleted Items (JC already entered into AMS) |
| In USLI folder | Emails routed to a USLI subfolder |

This is the most valuable filter for JC — it directly answers "what haven't I entered into the AMS yet?"

#### 1d. Column layout (final)

| Risk / Insured | Retail Agent | Line | Stage | Emails | Folder | Last Activity |
|---|---|---|---|---|---|---|

Everything else stays: search, stage filter, line filter, agent filter, sort, hide auto-notified toggle, submission count, sync footer.

### 2. Detail View Changes (RiskRecord)

#### 2a. Remove completeness bar

The `CompletenessBar` component ("12 of 17 fields extracted" with progress bar and missing field tags) is removed entirely from the detail view. The left side shows data, the right side shows gaps — no quantification overlay.

#### 2b. Clarify left/right relationship

The two-column layout stays with a clearer purpose for each side:

**Left column (55%) = "What we have"**
- Submission data card — key field values extracted from emails and PDFs. Pure data, no completeness indicator.
- Conversation timeline — email thread as chat bubbles
- Draft card (if applicable) — pinned at bottom or inline

**Right column (45%) = "What's needed / what's happening"**
- Stage progress bar + UW decision prompt
- Gap Analysis — framed as "Still needed", explicitly referencing the data shown on the left. Each missing field should indicate it wasn't found in any email or PDF, connecting visually to the left column's data card.
- Documents list
- Stage history

The key change: Gap Analysis explicitly references the left side — "these are the gaps in the data shown on the left" — rather than feeling like a separate, redundant analysis.

### 3. Backend Changes

#### 3a. Folder summary on submissions board endpoint

The `/submissions` board endpoint needs to return folder summary data for each submission. This requires joining email data during the aggregation:

```
// Add to the board aggregation pipeline per submission:
{
  email_count: <number of linked emails>,
  folder_summary: "Inbox" | "Deleted Items" | "Mixed" | "USLI",
  // Logic: if any email is in "Inbox" → "Inbox"
  //        if all emails in "Deleted Items" → "Deleted Items"
  //        if any email in folder containing "USLI" → "USLI"
  //        otherwise → most common folder
}
```

Implementation: `$lookup` from emails collection, `$addFields` to compute the summary. This adds one join to the existing faceted aggregation.

#### 3b. New endpoint: submission emails (lightweight)

```
GET /submissions/{id}/emails
```

Returns a lightweight list of emails for the expandable row (no body text, no thread parsing):

```json
[
  {
    "id": "...",
    "subject": "RE: GL Quote - Plaza 6201",
    "from_name": "Mike Torres",
    "from_address": "mike@agency.com",
    "folder": "Inbox",
    "received_at": "2026-03-05T14:30:00Z",
    "attachment_count": 2,
    "email_type": "agent_submission"
  }
]
```

This is much lighter than the full submission detail endpoint (no body, no extractions, no thread parsing).

#### 3c. Folder status filter parameter

Add `folder_status` query parameter to the board endpoint:

```
GET /submissions?folder_status=inbox  // has emails in Inbox
GET /submissions?folder_status=deleted  // all emails in Deleted Items
GET /submissions?folder_status=usli  // has emails in USLI folder
```

Implementation: filter in the `$match` stage of the aggregation, after the email `$lookup`.

### 4. No Changes To

- **Overview page** — stays as-is (demo narrative). Should already update dynamically with data.
- **Insights page** — stays as-is (analytics + system status). Should already update dynamically with data.
- **Login page** — no changes
- **Chrome bar / branding** — no changes

## Data Availability

Folder data is **already synced**. The sync pipeline resolves `parentFolderId` via Graph API `mailFolders` endpoint and stores the display name as `folder` on each email document in MongoDB. No sync changes needed.

## Files to Modify

| File | Change |
|------|--------|
| `ui/src/pages/SubmissionQueue.tsx` | Expandable rows, new columns (Emails, Folder), remove Action Needed column, add Folder Status filter |
| `ui/src/pages/RiskRecord.tsx` | Remove CompletenessBar, clarify Gap Analysis framing |
| `ui/src/api/hooks.ts` | New `useSubmissionEmails(id)` hook for expandable rows |
| `ui/src/api/types.ts` | Add `email_count`, `folder_summary` to Submission type |
| `src/gic_email_intel/api/routes/submissions.py` | Add email folder summary to board aggregation, new `/submissions/{id}/emails` endpoint, `folder_status` filter |

## Verification

1. `cd ui && npm run build` — zero errors
2. Browser: submissions table shows Emails count and Folder column
3. Browser: click chevron on a row → emails expand inline with folder info
4. Browser: click row itself → opens RiskRecord detail (existing behavior preserved)
5. Browser: Folder Status filter works — "Has emails in Inbox" shows only unprocessed submissions
6. Browser: detail view has no completeness bar
7. Browser: gap analysis clearly references the left column's data
