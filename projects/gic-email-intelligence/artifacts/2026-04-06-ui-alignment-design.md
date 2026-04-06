---
ask: "UI alignment for customer demo — connect the GIC web app to Unisoft AMS data and showcase automation"
created: 2026-04-06
workstream: gic-email-intelligence
session: 2026-04-06a
sources:
  - type: codebase
    description: "GIC email intelligence UI (React/Vite) and API (FastAPI)"
  - type: codebase
    description: "Unisoft proxy API (C# on EC2) and Python client"
  - type: unisoft-api
    description: "WSDL complete spec at research/unisoft-api/wsdl-complete.md"
---

# Design: UI Alignment — Inbox + AMS Unified View

**Date:** 2026-04-06
**Status:** Draft
**Goal:** Make the GIC web app show email intelligence and AMS data in one place, showcasing the automation that connects them.

## Problem

The current UI tells the story of "we organized your inbox" — it shows emails, classifications, extractions, and a pipeline. But it doesn't show the AMS connection. The customer can't see:

- Whether an applicant has been entered into Unisoft
- What data is in the AMS vs what's in the emails
- What automation did (or failed to do)

The demo story should be: **"We connected your Outlook inbox to your AMS. Every application is visible in one place — what came in via email, what's in Unisoft, and what was automated."**

## Design Principles

1. **One consolidated view per applicant.** Data from email extractions and AMS merges into a single view. No side-by-side duplication.
2. **Source provenance on every field.** Each data point shows where it came from: email extraction, AMS, or both. The user always knows what's verified vs what's only in one system.
3. **AMS is the source of truth for AMS data.** When both systems have a value, AMS wins for AMS-native fields (Quote ID, agent number, LOB code). Email extraction wins for fields AMS doesn't track (email body, classification, intent).
4. **Automation is shown, not sold.** The UI shows what was automated factually — "Quote ID created by automation" — without marketing language. The customer draws their own conclusions.
5. **Build on what exists.** 80-90% of the UI is already built. Changes are additive, not a rewrite.

## Current State

### What exists

**Queue view (SubmissionQueue.tsx):** Table with columns: Insured, Retail Agent, LOB, Stage, Emails, Folder, Last Activity. Expandable rows show linked emails. Click opens detail view.

**Detail view (RiskRecord.tsx, 970 lines):** Left sidebar with metadata (agent, LOB, stage, ball holder, dates). Main content: 8-stage progress bar, situation assessment, AI summary, extracted data, gap analysis, documents, conversation timeline, draft responses.

**Insights (Insights.tsx):** Analytics dashboard with email type distribution, LOB breakdown, daily volume chart, top agents, carrier activity, stage distribution.

**Backend API:** Board endpoint returns submissions grouped by stage. Detail endpoint assembles submission + emails + extractions + drafts + assessments + completeness. Unisoft proxy provides full AMS API access.

### What's missing

- No AMS data anywhere in the UI
- No Quote ID displayed
- No automation status shown
- No way to see what's in Unisoft vs what's in emails
- Insights tab has no automation metrics

### Data available for linking

| Source | How to get Quote ID | Coverage |
|--------|-------------------|----------|
| Our automation (`agent_submission`) | `email.automation_result.unisoft_quote_id` | ~120 emails, 8 quotes created so far |
| Unisoft portal (`gic_portal_submission`) | `email.classification.reference_numbers[0]` — the number in the subject line IS the Quote ID | 19 emails |
| Granada portal (`gic_application`) | Search Unisoft by insured name via `GetQuotesByName2` or use producer code from extraction | 26 emails |
| Carrier responses (USLI, Hiscox, etc.) | Linked to submissions that already have Quote IDs from the above channels | ~3,000 emails |

## Architecture

### Data Flow

```
Email arrives → Pipeline extracts/classifies → Submission created in MongoDB
                                                      │
                                    ┌─────────────────┤
                                    ▼                  ▼
                            Automation agent      Portal/manual
                            creates Quote ID      (Quote ID in
                            in Unisoft            reference_numbers)
                                    │                  │
                                    ▼                  ▼
                            automation_result     classification
                            .unisoft_quote_id     .reference_numbers
                                    │                  │
                                    └─────┬────────────┘
                                          ▼
                                  Backend resolves Quote ID
                                  per submission (from any source)
                                          │
                                          ▼
                                  GetQuote API call to Unisoft
                                  returns full AMS record
                                          │
                                          ▼
                                  Frontend shows consolidated
                                  applicant view with sources
```

### Quote ID Resolution Logic

For a given submission, find its Quote ID by checking (in order):

1. **Automation result**: Any linked email with `automation_result.unisoft_quote_id` set
2. **Portal reference**: Any linked email from `noreply@unisoftonline.com` with a numeric reference number in `classification.reference_numbers`
3. **Manual lookup**: (future) Search Unisoft by insured name

Once a Quote ID is resolved, store it on the submission document (`unisoft_quote_id`) so it doesn't need to be re-resolved on every page load.

### AMS Data Retrieval

The `GetQuote` API returns the full Unisoft record for a Quote ID:

- Applicant: Name, Address, City, State, Zip, FormOfBusiness, FEIN, Phone, Email
- Coverage: LOB, SubLOB, PolicyState, EffectiveDate, ExpirationDate, Premium, Term
- Agent: AgentNumber, AgentName
- Status: QuoteType (N=New, R=Renewal), Status code, CreatedDate
- Policy: PolicyNumber (if bound), CarrierNumber, CarrierName

This is called on-demand when the detail view opens, not pre-fetched for every submission. Cached server-side for 5 minutes to avoid excessive API calls.

## Changes

### Backend

#### 1. Quote ID resolution service

New module: `src/gic_email_intel/core/ams_link.py`

```python
async def resolve_quote_id(db, submission_id: ObjectId) -> int | None:
    """Find the Unisoft Quote ID for a submission from any source."""
    # Check if already resolved and stored
    sub = await db["submissions"].find_one({"_id": submission_id})
    if sub and sub.get("unisoft_quote_id"):
        return sub["unisoft_quote_id"]

    # Check automation results on linked emails
    async for email in db["emails"].find({"submission_id": submission_id}):
        qid = (email.get("automation_result") or {}).get("unisoft_quote_id")
        if qid:
            # Store on submission for future lookups
            await db["submissions"].update_one(
                {"_id": submission_id},
                {"$set": {"unisoft_quote_id": qid, "unisoft_source": "automation"}}
            )
            return qid

    # Check portal reference numbers
    async for email in db["emails"].find({"submission_id": submission_id}):
        if email.get("from_address", "").lower() in ("noreply@unisoftonline.com",):
            refs = (email.get("classification") or {}).get("reference_numbers", [])
            for ref in refs:
                if ref.isdigit() and len(ref) >= 5:
                    qid = int(ref)
                    await db["submissions"].update_one(
                        {"_id": submission_id},
                        {"$set": {"unisoft_quote_id": qid, "unisoft_source": "portal"}}
                    )
                    return qid

    return None
```

#### 2. AMS data endpoint

New route: `GET /api/submissions/{id}/ams`

Returns the Unisoft quote record if a Quote ID is linked. Calls `GetQuote` via the proxy. Response shape:

```json
{
  "quote_id": 17146,
  "source": "automation",
  "quote": {
    "name": "Enkelana Caffe",
    "address": "3861 Baymeadows Road",
    "city": "Jacksonville",
    "state": "FL",
    "zip": 32217,
    "lob": "CG",
    "lob_description": "General Liability",
    "sub_lob": "LL",
    "sub_lob_description": "Liquor Liability",
    "agent_number": 6598,
    "agent_name": "Good Deal Insurance - Duval",
    "form_of_business": "C",
    "effective_date": "2026-04-06",
    "expiration_date": "2027-04-06",
    "status": "New",
    "created_date": "2026-04-06",
    "policy_state": "FL",
    "premium": 0.0
  },
  "automation": {
    "status": "completed",
    "completed_at": "2026-04-06T14:52:00Z",
    "notes": "LOB=CG, SubLOB=LL, Agent=6598"
  }
}
```

Returns `{"quote_id": null, "source": null}` if no Quote ID is linked.

#### 3. Quote ID in board response

Add `unisoft_quote_id` and `unisoft_source` fields to the submission objects returned by the board endpoint. These are read from the submission document (populated by the resolution service or by a batch job).

#### 4. Batch Quote ID resolution

One-time script or pipeline step that resolves Quote IDs for all existing submissions. Run once to backfill, then automation and the detail view handle new ones going forward.

#### 5. Automation stats in analytics endpoint

Add to the existing `/api/stats/analytics` response:

```json
{
  "automation": {
    "total_processed": 25,
    "succeeded": 8,
    "failed": 12,
    "pending": 110,
    "success_rate": 0.40,
    "failure_reasons": [
      {"reason": "Agency not in Unisoft", "count": 5},
      {"reason": "Missing address", "count": 3},
      {"reason": "Infrastructure error", "count": 4}
    ],
    "quotes_in_ams": 27,
    "quotes_from_automation": 8,
    "quotes_from_portal": 19
  }
}
```

### Frontend

#### 6. Queue table — AMS column

**Replace the "Stage" column with "AMS Status"** (or add alongside):

| State | Display |
|-------|---------|
| Quote ID linked (automation) | `Q:17146` with green "Auto" badge |
| Quote ID linked (portal) | `Q:144301` with blue "Portal" badge |
| Automation failed | Orange "Failed" badge with hover tooltip showing reason |
| Automation pending | Gray "Pending" badge |
| No automation needed | Empty (carrier responses, etc.) |

The Quote ID is clickable — opens the detail view focused on the AMS section.

#### 7. Detail view — consolidated applicant panel

Replace the current left sidebar metadata section with a **unified applicant card**. Fields are grouped:

**Applicant Info**
| Field | Value | Source |
|-------|-------|--------|
| Insured Name | ASIAN PINOY INC | Email + AMS |
| Address | 123 Main St, Miami, FL 33125 | AMS |
| Form of Business | Corporation | Email |
| Phone | (305) 555-1234 | AMS |
| Email | contact@asianpinoy.com | Email |

**Coverage**
| Field | Value | Source |
|-------|-------|--------|
| LOB | CG - General Liability | AMS |
| Sub-LOB | SE - Service/Maintenance | AMS |
| Effective Date | Apr 6, 2026 | AMS |
| Expiration Date | Apr 6, 2027 | AMS |
| Policy State | FL | AMS |

**Agent**
| Field | Value | Source |
|-------|-------|--------|
| Agent | Estrella Insurance #284 (6544) | AMS |
| Contact | Maria Poventud | Email |
| Email | maria.poventud@estrellainsurance.com | Email |

Source indicators:
- 📧 = from email extraction only
- 🏢 = from AMS only
- ✓ = in both systems (verified)

When no AMS data is available, the panel shows extraction data only with a note: "Not yet in AMS" or "AMS lookup pending."

#### 8. Detail view — automation status banner

At the top of the detail view, a contextual banner:

- **Automated successfully:** Green banner — "Quote Q:17146 created in Unisoft via automation on Apr 6 · Agent 6544 · CG/SE"
- **Automation failed:** Amber banner — "Automation failed: Agency not found in Unisoft. Searched for 'Kyra Insurance LLC' — 0 matches."
- **Portal created:** Blue banner — "Quote Q:144301 created via Unisoft online portal"
- **No AMS link:** Gray subtle note — "No Unisoft record linked"

#### 9. Insights tab — automation section

Add a new section to the existing Insights page (not a separate tab):

**"Automation" section with:**
- Summary cards: Quotes Created (auto), Quotes Created (portal), Pending, Failed
- Success rate donut or bar
- Failure reasons breakdown (bar chart or list)
- Recent automation activity feed (last 10 processed)

### Terminology

Rename throughout the UI:
- "Submission" → "Applicant" (in user-facing labels, not in code/API)
- "Submission queue" → "Applicants" (page title)
- "Risk / Insured" column → "Applicant"
- Keep "submission" in code and API paths for backward compatibility

## Build Order

| Step | What | Files | Dependency |
|------|------|-------|------------|
| 1 | Quote ID resolution service | `core/ams_link.py` | None |
| 2 | Batch backfill existing submissions | Script or management command | Step 1 |
| 3 | AMS data endpoint | `api/routes/submissions.py` | Step 1, Unisoft proxy |
| 4 | Add `unisoft_quote_id` to board response | `api/routes/submissions.py` | Step 1 |
| 5 | Automation stats in analytics | `api/routes/stats.py` | None |
| 6 | Queue table AMS column | `pages/SubmissionQueue.tsx`, `api/types.ts` | Step 4 |
| 7 | Consolidated applicant panel | `pages/RiskRecord.tsx`, new component | Step 3 |
| 8 | Automation status banner | `pages/RiskRecord.tsx` | Step 3 |
| 9 | Insights automation section | `pages/Insights.tsx` | Step 5 |
| 10 | Terminology rename | Multiple UI files | None (can be done anytime) |
| 11 | Deploy and test | Railway + Amplify | All above |

## Out of Scope

- Searching Unisoft by insured name for `gic_application` emails (Granada portal). These require fuzzy matching and disambiguation. Defer to a future iteration.
- Two-way sync (writing email data back to Unisoft fields beyond what automation already does).
- Creating new agency records in Unisoft for agencies that don't exist.
- Production Unisoft endpoints (currently UAT only).

## Success Criteria

The customer can:
1. Open the web app and see all their applicants with AMS status at a glance
2. Click any applicant and see a consolidated view of email + AMS data with source indicators
3. See which applicants were auto-entered into Unisoft and which came through the portal
4. Understand why automation failed for specific applicants
5. See overall automation metrics (success rate, failure reasons) in the Insights tab
