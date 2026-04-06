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
2. **Portal reference**: Any linked email with `classification.email_type == "gic_portal_submission"` that has a numeric reference number (5+ digits) in `classification.reference_numbers`. Validated by calling `GetQuote` to confirm the record exists before storing.
3. **Manual lookup**: (future) Search Unisoft by insured name

Once a Quote ID is resolved and validated, store it on the submission document (`unisoft_quote_id`) so it doesn't need to be re-resolved on every page load.

**Assumption:** For `gic_portal_submission` emails (from `noreply@unisoftonline.com` or `noreply@gicunderwriters.com`), the numeric reference number in the subject line (e.g., "New Quote Submission - 144301") is the Unisoft Quote ID. This is validated by calling `GetQuote` before storing — if the Quote ID doesn't exist in Unisoft, it's not linked.

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

#### 0. Async Unisoft client for the web API

New module: `src/gic_email_intel/core/unisoft.py`

The existing `UnisoftClient` (in `unisoft-proxy/client/`) uses synchronous `requests`, which would block the async event loop. The web API needs an async wrapper using `httpx.AsyncClient`.

```python
import httpx
from gic_email_intel.config import settings

class AsyncUnisoftClient:
    """Async Unisoft proxy client for use in FastAPI routes."""

    def __init__(self):
        self.base_url = settings.unisoft_proxy_url  # new config field
        self.api_key = settings.unisoft_api_key      # new config field
        self._client = httpx.AsyncClient(timeout=30.0)

    async def call(self, operation: str, params: dict = None) -> dict:
        resp = await self._client.post(
            f"{self.base_url}/api/soap/{operation}",
            json=params or {},
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
        )
        return resp.json()

    async def get_quote(self, quote_id: int) -> dict | None:
        data = await self.call("GetQuote", {"request": {"QuoteID": quote_id}})
        return data.get("Quote")
```

Config additions to `config.py`:
```python
unisoft_proxy_url: str = ""   # e.g., "http://54.83.28.79:5000"
unisoft_api_key: str = ""
```

Railway env vars needed on the `api` service: `UNISOFT_PROXY_URL`, `UNISOFT_API_KEY`.

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

    # Check portal reference numbers (gic_portal_submission emails)
    async for email in db["emails"].find({"submission_id": submission_id}):
        email_type = (email.get("classification") or {}).get("email_type")
        if email_type == "gic_portal_submission":
            refs = (email.get("classification") or {}).get("reference_numbers", [])
            for ref in refs:
                if ref.isdigit() and len(ref) >= 5:
                    qid = int(ref)
                    # Validate: confirm this Quote ID exists in Unisoft
                    if await _validate_quote_exists(qid):
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
    "zip": "32217",
    "lob": "CG",
    "lob_description": "General Liability",
    "sub_lob": "LL",
    "sub_lob_description": "Liquor Liability",
    "agent_number": 6598,
    "agent_name": "Good Deal Insurance - Duval",
    "form_of_business": "C",
    "effective_date": "2026-04-06T00:00:00",
    "expiration_date": "2027-04-06T00:00:00",
    "status": 1,
    "status_label": "New",
    "created_date": "2026-04-06T00:00:00",
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

**Field mapping from SOAP → JSON:**

| SOAP Field | JSON Field | Type | Notes |
|-----------|-----------|------|-------|
| `Name` | `name` | string | |
| `Address` | `address` | string | |
| `City` | `city` | string | |
| `State` | `state` | string | |
| `Zip` | `zip` | string | String to preserve leading zeros |
| `LOB` | `lob` | string | 2-char code |
| `LOBDescription` | `lob_description` | string | |
| `SubLOB` | `sub_lob` | string | |
| `SubLOBDescription` | `sub_lob_description` | string | |
| `AgentNumber` | `agent_number` | int | |
| `AgentName` | `agent_name` | string | |
| `FormOfBusiness` | `form_of_business` | string | I/C/L/P |
| `EffectiveDate` | `effective_date` | string | ISO datetime |
| `ExpirationDate` | `expiration_date` | string | ISO datetime |
| `Status` | `status` | int | Numeric code |
| _(derived)_ | `status_label` | string | 1=New, 2=Active, etc. (map in backend) |
| `CreatedDate` | `created_date` | string | ISO datetime |
| `PolicyState` | `policy_state` | string | |
| `Premium` | `premium` | float | |

**Error responses:**
- Quote ID not linked: `{"quote_id": null, "source": null}` (200 OK)
- Unisoft proxy unreachable: `{"quote_id": 17146, "source": "automation", "quote": null, "error": "AMS unavailable"}` (200 OK, degraded)
- GetQuote returns error: `{"quote_id": 17146, "source": "automation", "quote": null, "error": "Quote not found in AMS"}` (200 OK)

#### 3. Quote ID in board response

Add `unisoft_quote_id` and `unisoft_source` fields to the submission objects returned by the board endpoint. These are read from the submission document (populated by the resolution service or by a batch job).

#### 4. Batch Quote ID resolution

One-time script or pipeline step that resolves Quote IDs for all existing submissions. Run once to backfill, then automation and the detail view handle new ones going forward.

#### 5. Automation stats in analytics endpoint

Add to the existing `/api/stats/analytics` response. Computed via MongoDB aggregation on the `emails` collection:

```python
# Automation stats aggregation
pipeline = [
    {"$match": {"classification.email_type": "agent_submission"}},
    {"$group": {
        "_id": "$automation_status",
        "count": {"$sum": 1},
    }},
]
# Results: {_id: "completed", count: 8}, {_id: "failed", count: 12}, {_id: null, count: 110}
# null = no automation_status = pending

# Failure reasons: group by error message prefix (first 60 chars)
failure_pipeline = [
    {"$match": {"automation_status": "failed"}},
    {"$project": {"reason": {"$substrCP": ["$automation_result.error", 0, 60]}}},
    {"$group": {"_id": "$reason", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10},
]

# Quotes in AMS: count submissions with unisoft_quote_id set
quotes_in_ams = await db["submissions"].count_documents({"unisoft_quote_id": {"$exists": True, "$ne": None}})
```

Response shape:

```json
{
  "automation": {
    "total_processed": 25,
    "succeeded": 8,
    "failed": 12,
    "pending": 110,
    "success_rate": 0.40,
    "failure_reasons": [
      {"reason": "Agency not found in Unisoft", "count": 5},
      {"reason": "Missing address", "count": 3},
      {"reason": "Infrastructure error", "count": 4}
    ],
    "quotes_in_ams": 27,
    "quotes_from_automation": 8,
    "quotes_from_portal": 19
  }
}
```

### TypeScript Types

New interfaces for `api/types.ts`:

```typescript
// AMS data from Unisoft
export interface AMSQuote {
  name: string
  address: string
  city: string
  state: string
  zip: string
  lob: string
  lob_description: string
  sub_lob: string | null
  sub_lob_description: string | null
  agent_number: number
  agent_name: string
  form_of_business: string
  effective_date: string
  expiration_date: string
  status: number
  status_label: string
  created_date: string
  policy_state: string
  premium: number
}

export interface AMSData {
  quote_id: number | null
  source: 'automation' | 'portal' | null
  quote: AMSQuote | null
  automation?: {
    status: string
    completed_at: string
    notes: string | null
    error: string | null
  }
  error?: string
}

// Automation stats (added to Analytics)
export interface AutomationStats {
  total_processed: number
  succeeded: number
  failed: number
  pending: number
  success_rate: number
  failure_reasons: Array<{ reason: string; count: number }>
  quotes_in_ams: number
  quotes_from_automation: number
  quotes_from_portal: number
}
```

Updates to existing interfaces:

```typescript
// Add to Submission interface
export interface Submission {
  // ... existing fields ...
  unisoft_quote_id?: number | null
  unisoft_source?: 'automation' | 'portal' | null
}

// Add to Analytics interface
export interface Analytics {
  // ... existing fields ...
  automation: AutomationStats
}
```

New React Query hook in `api/hooks.ts`:

```typescript
export function useAMSData(submissionId: string) {
  return useQuery({
    queryKey: ['ams', submissionId],
    queryFn: () => api.get(`/submissions/${submissionId}/ams`).then(r => r.data),
    staleTime: 5 * 60 * 1000, // 5 min client-side cache
    retry: 1, // Don't hammer Unisoft if it's down
  })
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

Source indicators (using Lucide icons for cross-browser consistency):
- `<Mail size={12} />` = from email extraction only (muted color)
- `<Database size={12} />` = from AMS only (accent color)
- `<CheckCircle size={12} />` = in both systems, values match (green)

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

**Deferred until customer validation.** The rename from "Submission" to "Applicant" is a user-facing label change. Unisoft uses "Submission" with a specific meaning (distinct from "Quote"), and GIC staff may have their own preferences. Propose the rename during the demo and get explicit buy-in before implementing.

Candidate renames (pending approval):
- "Submission queue" → "Applicants"
- "Risk / Insured" column → "Applicant"
- Keep "submission" in code and API paths regardless

## Build Order

| Step | What | Files | Dependency |
|------|------|-------|------------|
| 0 | Async Unisoft client for web API | `core/unisoft.py`, `config.py` | None |
| 1 | Quote ID resolution service | `core/ams_link.py` | Step 0 |
| 2 | Batch backfill existing submissions | `cli/commands/automate.py` (new `backfill-ams` command) | Step 1 |
| 3 | AMS data endpoint | `api/routes/submissions.py` | Steps 0, 1 |
| 4 | Add `unisoft_quote_id` to board response | `api/routes/submissions.py` | Step 1 |
| 5 | Automation stats in analytics | `api/routes/stats.py` | None (parallel with 0-4) |
| 6 | TypeScript types + React Query hook | `api/types.ts`, `api/hooks.ts` | Steps 3, 4, 5 (API contract) |
| 7 | Queue table AMS column | `pages/SubmissionQueue.tsx` | Step 6 |
| 8 | Consolidated applicant panel | `pages/RiskRecord.tsx`, new component | Step 6 |
| 9 | Automation status banner | `pages/RiskRecord.tsx` | Step 6 |
| 10 | Insights automation section | `pages/Insights.tsx` | Step 6 |
| 11 | Deploy and test | Railway + Amplify | All above |

**Parallelism:** Steps 0-4 (backend AMS) and Step 5 (automation stats) can be built in parallel. Frontend steps 7-10 can begin once Step 6 (types) is done.

**Deployment:** The Railway `api` service needs two new env vars: `UNISOFT_PROXY_URL` and `UNISOFT_API_KEY`. The Amplify frontend redeploys automatically on push.

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
