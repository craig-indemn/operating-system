---
ask: "Is it possible to build an Outlook Add-in for GIC Email Intelligence? How would it work, how do we test it, and what's the vision?"
created: 2026-03-19
workstream: gic-email-intelligence
session: 2026-03-19-a
sources:
  - type: web
    description: "Microsoft Office Add-ins documentation — Outlook task pane, Office.js APIs, manifest format, sideloading, deployment"
  - type: web
    description: "Microsoft Graph API — mailFolders/inbox/messages, personal account support, delegated permissions"
---

# Outlook Add-in Design for GIC Email Intelligence

## Vision

The Outlook Add-in brings GIC Email Intelligence directly into Maribel's Outlook inbox. Instead of switching to a separate web app, she opens an email and a sidebar panel shows the AI analysis, gap assessment, and suggested reply. She clicks "Reply with this" and Outlook opens a native reply window with the draft pre-filled. Zero workflow change.

The standalone web app ("Indemn Intake Manager") becomes the analytics/management view — volume trends, resolution history, methodology. Day-to-day work happens inside Outlook.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Outlook (quote@gicunderwriters.com)             │
│                                                   │
│  ┌──────────────────┐  ┌──────────────────────┐  │
│  │   Email List      │  │  Task Pane (350px)   │  │
│  │                   │  │                      │  │
│  │  ► Blaze Pilates  │  │  Submission Header   │  │
│  │    USLI Quote...  │  │  AI Summary          │  │
│  │                   │  │  Gap Analysis        │  │
│  │    Ojeda Trucking │  │  Suggested Draft     │  │
│  │    Agent Reply... │  │  [Reply with this]   │  │
│  │                   │  │                      │  │
│  │                   │  │  → Open full view     │  │
│  └──────────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────┘
                               │
                    fetch() with extracted
                    ref numbers + insured name
                               │
                               ▼
                  ┌─────────────────────┐
                  │  Existing Backend    │
                  │  FastAPI :8080       │
                  │                     │
                  │  POST /api/lookup   │  ← new endpoint
                  │  GET /api/subs/{id} │  ← existing
                  └─────────────────────┘
                          │
                    MongoDB + S3
```

## What We're Building

### 1. Outlook Add-in (React app, ~6 components)

A small React app that runs in Outlook's task pane (350px wide sidebar). Deployed to Vercel as a static site. Lives in a new `addin/` directory in the existing repo. Types are copied from `ui/src/api/types.ts` (subset: `SubmissionDetail`, `Draft`, `LobRequirements`, `Extraction`, `Completeness`). This is intentional for demo speed — production should extract shared types to a top-level `shared/types.ts` or generate from Pydantic models.

**Project structure:**
```
gic-email-intelligence/
  addin/                    ← new
    src/
      main.tsx              ← Office.onReady() bootstrap
      TaskPane.tsx           ← root component
      components/
        SubmissionHeader.tsx
        AddinSummary.tsx
        AddinGapAnalysis.tsx
        AddinDraft.tsx
      api/
        client.ts           ← fetch wrapper with embedded token
        types.ts             ← subset of types copied from ui/src/api/types.ts
        extract.ts           ← reference number regex extraction
    manifest.xml
    package.json
    vite.config.ts          ← includes HTTPS config for local sideloading
    tsconfig.json            ← includes "types": ["office-js"]
  ui/                       ← existing standalone app
  src/                      ← existing backend
```

**Components:**
- `main.tsx` — Wraps React bootstrap in `Office.onReady()` callback. React renders only after Office.js is initialized.
- `TaskPane.tsx` — Root. Reads current email via Office.js, calls backend, manages states. Registers `Office.EventType.ItemChanged` handler for pinnable task pane — re-fetches when user switches emails.
- `SubmissionHeader.tsx` — Insured name, LOB badge, stage badge. One compact line.
- `AddinSummary.tsx` — AI summary in a blue card. 2-3 sentences.
- `AddinGapAnalysis.tsx` — Active requests (amber items) + collapsed LOB requirements.
- `AddinDraft.tsx` — Draft body + "Reply with this" button + "Edit first" expand.

**Bootstrap flow:**
```typescript
// main.tsx
import { createRoot } from 'react-dom/client'
import { TaskPane } from './TaskPane'

Office.onReady(() => {
  createRoot(document.getElementById('root')!).render(<TaskPane />)
})
```

**ItemChanged handler for pinnable task pane:**
```typescript
// TaskPane.tsx — inside useEffect
Office.context.mailbox.addHandlerAsync(
  Office.EventType.ItemChanged,
  () => {
    // Re-read current email and re-fetch submission data
    loadCurrentEmail()
  }
)
```

**Six states:**
1. **Initializing** — Office.js loading (brief, shows spinner).
2. **Loading** — Skeleton shimmer while matching email to submission.
3. **Matched** — Full analysis: header → summary → gaps → draft → "Open full view" link.
4. **No match** — "This email isn't part of a tracked submission."
5. **Error** — "Couldn't reach the server." + Retry button.
6. **No email selected** — "Select an email to see analysis."

**Reply mechanism:**
`displayReplyAllFormAsync()` — Office.js built-in (requirement set 1.9+). Opens Outlook's native reply window pre-filled with our draft text as HTML. No Mail.Send permission needed. Maribel edits if she wants, then clicks Send. Email goes through normal Exchange flow.

### 2. Backend: Lookup Endpoint (~50 lines)

```
POST /api/lookup-email
{
  "reference_numbers": ["MGL026F9DR4"],
  "insured_name": "Blaze Pilates",
  "subject": "Re: USLI Quote - MGL026F9DR4 - Blaze Pilates",
  "sender": "notifications@usli.com",
  "internet_message_id": "<abc123@outlook.com>"
}
```

**Matching waterfall:**
1. `internet_message_id` — exact match against emails collection. **Note:** This field is not currently stored in MongoDB. The sync pipeline's `DEFAULT_SELECT` in `graph_client.py` does not request `internetMessageId`, and the Email model does not have this field. For production at GIC, we need to: (a) add `internetMessageId` to `DEFAULT_SELECT`, (b) add the field to the Email model, (c) re-sync to populate it, (d) create a MongoDB index on it. **For the demo, this step is skipped** — seeded emails will have different internet message IDs anyway.
2. `reference_numbers` — match against submissions' reference_numbers array. **Primary matching path for the demo.** 96% of emails have extractable reference numbers.
3. Insured name fuzzy match + sender domain — fallback for the ~4% without reference numbers. Pre-filter candidates to bound the search: last 90 days, limit 200 submissions. Uses the existing `fuzzy_match_insured` from `linker.py` with `rapidfuzz`.

**Implementation sketch:**
```python
async def lookup_email(body: LookupRequest) -> dict:
    db = get_async_db()

    # Step 1: internet_message_id (production only — field not yet in DB)
    if body.internet_message_id:
        email = await db["emails"].find_one({"internet_message_id": body.internet_message_id})
        if email and email.get("submission_id"):
            return await get_submission_detail(str(email["submission_id"]))

    # Step 2: reference numbers — $in match against submissions
    if body.reference_numbers:
        sub = await db["submissions"].find_one(
            {"reference_numbers": {"$in": body.reference_numbers}}
        )
        if sub:
            return await get_submission_detail(str(sub["_id"]))

    # Step 3: fuzzy insured name — bounded candidate search
    if body.insured_name:
        cutoff = datetime.now(timezone.utc) - timedelta(days=90)
        candidates = []
        async for sub in db["submissions"].find(
            {"created_at": {"$gte": cutoff}},
            {"_id": 1, "named_insured_normalized": 1}  # NOTE: must use normalized field for rapidfuzz
        ).limit(200):
            candidates.append(sub)
        match = fuzzy_match_insured(body.insured_name, candidates)
        if match:
            return await get_submission_detail(str(match["_id"]))

    raise HTTPException(404, "No matching submission found")
```

**Prerequisite refactor:** `get_submission_detail()` does not exist as a standalone function yet. The assembly logic currently lives inline in the `submission_detail()` route handler at `submissions.py` lines 248-365. Before implementing the lookup endpoint, extract that into a reusable `async def get_submission_detail(submission_id: str) -> dict` helper that both the existing `GET /api/submissions/{id}` route and the new `POST /api/lookup-email` can call. The return type should be `dict`, not `SubmissionDetailResponse` — the Pydantic model at `models.py` line 241 is missing `summary` and `lob_requirements` fields that the route returns. The existing route already returns a plain dict, so follow the same pattern.

**Returns:** The full `SubmissionDetailResponse` — same shape as `GET /api/submissions/{id}`: `submission`, `emails`, `extractions`, `drafts`, `completeness`, `summary`, `lob_requirements`. The add-in uses `summary`, `drafts`, `lob_requirements`, and `completeness`; the other fields are available for the "Open full view" link.

### 3. Client-Side Reference Number Extraction (~10 lines)

The add-in reads the email subject and body via Office.js, runs regex to extract:
- USLI reference numbers: `/\b[A-Z]{2,3}\d{3}[A-Z0-9]{3,}\b/g` — **must match the exact backend pattern** from `linker.py` line 37. The `{2,3}` allows 2-letter USLI prefixes (SP for Specified Professions, PM for Property Manager, etc.) which `{3}` would miss.
- Insured name: from subject patterns like "USLI Quote - REF - InsuredName"
- GIC numbers: `/GIC-\d+/g`

Ported from the backend's `extract_reference_numbers()` in `linker.py`. **Do not write a new regex** — the backend pattern is authoritative and tested against 3,214 emails.

### 4. Manifest File (XML, ~60 lines)

Tells Outlook:
- Add-in name: "GIC Email Intelligence"
- Source URL: `https://gic-addin.vercel.app` (production) or `https://localhost:3000` (dev)
- Activation: `MessageReadCommandSurface` — shows when reading an email
- Pinnable: `SupportsPinning` element set to `true` — panel stays open across emails
- Minimum requirement set: **1.9** (covers `displayReplyAllFormAsync`, `item.body.getAsync`, `item.internetMessageId`)
- Ribbon button with icon to toggle the task pane

### 5. Authentication

**Demo:** API token embedded as a Vite environment variable (`VITE_API_TOKEN`). The add-in's fetch wrapper includes it as `Authorization: Bearer <token>` on every request. Simple, no login flow needed.

```typescript
// addin/src/api/client.ts
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8080/api'
const API_TOKEN = import.meta.env.VITE_API_TOKEN
const WEB_BASE = import.meta.env.VITE_WEB_BASE || 'http://localhost:5173'

export async function lookupEmail(params: LookupRequest) {
  const res = await fetch(`${API_BASE}/lookup-email`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_TOKEN}`,
    },
    body: JSON.stringify(params),
  })
  if (!res.ok) {
    if (res.status === 404) return null  // no matching submission
    throw new Error(`Lookup failed: ${res.status}`)
  }
  return res.json()
}

/** URL for "Open in Intake Manager" link */
export function intakeManagerUrl(submissionId: string): string {
  return `${WEB_BASE}/?token=${API_TOKEN}&submission=${submissionId}`
}
```

**Production:** Use Office.js `getAccessTokenAsync()` (SSO) to obtain an Exchange identity token, validate it server-side against GIC's Entra tenant. This requires adding the add-in's app ID to the Entra app registration. Not needed for the demo.

### 6. CORS Configuration

The backend's CORS allowlist in `src/gic_email_intel/api/main.py` must be updated:

```python
allow_origins=[
    "http://localhost:5173",     # existing standalone app (dev)
    "http://localhost:3000",     # add-in dev server
    "https://gic.indemn.ai",    # existing standalone app (prod)
    "https://gic-addin.vercel.app",  # add-in on Vercel
]
```

For Vercel preview deployments (which generate unique URLs), add a pattern match or use `https://*.vercel.app` during development.

## Demo Strategy

### Problem
Craig has Mail.Read (app-only) on GIC's quote@ inbox. He cannot log into Outlook as quote@, cannot forward emails, and cannot change GIC permissions. He needs test emails in an inbox where he can sideload the add-in.

### Solution: Seed Emails into Personal Outlook

Craig has a personal Outlook.com account. The plan:

1. **Register a new Entra app** for personal account access with `Mail.ReadWrite` delegated permission. **Important:** The app must be registered as "Accounts in any organizational directory **and personal Microsoft accounts**" (multi-tenant + personal), not single-tenant. The OAuth endpoint must use `/consumers/` or `/common/` authority, not a tenant-specific URL. This is a common stumbling block — personal Outlook.com accounts are consumer Microsoft accounts, not organizational.
2. **OAuth sign-in** with personal account, grant consent
3. **Seeding script** reads 5 representative emails from MongoDB (via existing backend/DB), creates them in Craig's personal inbox via `POST /me/mailFolders/inbox/messages`. **Important:** Set `"isDraft": false` on each created message so they appear as received emails, not drafts.
4. **Sideload** the add-in manifest on Outlook.com. **Note:** Personal Outlook.com accounts use a different sideloading path than M365 work accounts: Settings → View all Outlook settings → Mail → Customize actions → Custom add-ins.
5. **Demo**: Open email → sidebar shows analysis → click "Reply with this" → Outlook reply opens

### Validate sideloading early

Before building the full add-in, create a minimal "hello world" manifest + HTML page, deploy to Vercel, and sideload it on the personal Outlook.com account. This validates:
- The sideloading path works for personal accounts
- The task pane renders correctly
- Requirement set 1.9 is available on Outlook.com

### Demo Email Selection (5 emails covering key scenarios)

| Email | Type | What the sidebar shows |
|-------|------|----------------------|
| Blaze Pilates | USLI Quote | Quoted stage, premium/limits extracted, "Forward to agent" draft |
| Ojeda Trucking | Agent Submission | New submission, missing loss runs + application, info request draft |
| ESR Cleaning | Carrier Pending | Awaiting info, carrier requesting specific items, follow-up draft |
| Mercado Insurance | USLI Decline | Declined, "Notify agent" draft |
| A complete submission | Agent Reply | All gaps filled, green "Complete" state |

### What the Demo Looks Like

1. Craig opens Outlook on the web
2. Clicks on the "Blaze Pilates" email
3. Clicks the GIC Email Intelligence icon in the ribbon (or it auto-activates)
4. Sidebar slides in showing:
   - "Blaze Pilates LLC — GL — Quoted"
   - AI summary: "USLI returned a quote for Blaze Pilates. Premium $2,847, GL limits $1M/$2M, effective 4/1/2026. Ready to forward to retail agent."
   - Gap Analysis: green checkmarks, all quote details extracted
   - Draft: "Hi [Agent], Please find the attached quote for Blaze Pilates LLC..."
   - [Reply with this] button
5. Craig clicks "Reply with this" — Outlook's native reply window opens with the draft pre-filled
6. "Open in Intake Manager →" link opens the full web app for analytics/history

## Deployment

### Demo (immediate)
- Add-in → Vercel (static React app)
- Backend → existing localhost:8080 or deploy to AWS
- Manifest → points to Vercel URL
- Sideloaded on Craig's personal Outlook.com

### Production (GIC deployment)
- Add-in → Vercel or same AWS instance as backend
- Backend → AWS (ECS/EC2) at gic.indemn.ai
- Manifest → GIC's M365 admin uploads in admin center (Settings → Integrated Apps)
- Assigned to Maribel's account → appears in her Outlook within 24-72 hours
- Works across Outlook on the web, new Outlook on Windows, Mac
- **Requirement set 1.13** needed for shared mailbox support (quote@ is likely a shared mailbox). This is higher than the demo's 1.9. The add-in should target 1.9 as minimum but test with 1.13 features for production.

### Permissions Required
- **No new permissions on GIC's tenant** — the add-in reads emails via Office.js (user's own session), not Graph API
- **Backend stays Mail.Read** — sync pipeline unchanged
- **Craig's personal account**: Mail.ReadWrite delegated (for seeding test emails only, not production)
- **Production auth**: Add-in app ID registered in GIC's Entra tenant for SSO validation (future)

## What Changes vs Stays the Same

| Piece | Changes? | Notes |
|-------|----------|-------|
| Backend API | +1 endpoint, CORS update | `POST /api/lookup-email` + Vercel origin in CORS |
| MongoDB | No change (demo), migration (prod) | Production needs `internetMessageId` field + index |
| Sync pipeline | No change (demo), +1 field (prod) | Production needs `internetMessageId` in `DEFAULT_SELECT` |
| Standalone web app | No change | Continues as analytics/management view |
| Frontend components | New `addin/` directory | Separate narrow-layout components, shared types |

## Technical Constraints

- **350px width** — everything must stack vertically, no side-by-side layouts
- **HTTPS required** — Vercel handles this automatically
- **CORS** — backend must allow requests from the Vercel domain (see Section 6)
- **No offline** — add-in requires network to reach backend
- **Office.onReady()** — React must not render until Office.js initializes
- **ItemChanged event** — task pane must re-fetch when user navigates between emails
- **Personal Outlook.com** — supports Office Add-ins with requirement set up to ~1.9. Sufficient for the demo. Production at GIC (M365 work account with shared mailbox) needs requirement set 1.13.
- **Vite HTTPS for local dev** — Office Add-ins require HTTPS even on localhost. Configure `server.https` in `vite.config.ts` with a self-signed certificate (Vite supports this via `@vitejs/plugin-basic-ssl` or manual cert config). Without this, sideloading from localhost will fail silently.
- **TypeScript types** — Install `@types/office-js` and add `"types": ["office-js"]` to `tsconfig.json`. Without this, `Office` is untyped and `Office.context.mailbox` calls will have no autocomplete or type checking.

## Production Roadmap (post-demo)

These items are NOT needed for the demo but are needed for production deployment at GIC:

1. **Add `internetMessageId` to sync pipeline** — Add to `DEFAULT_SELECT` in `graph_client.py`, add field to Email model, create MongoDB index. Re-sync to backfill. Enables instant exact matching.
2. **SSO authentication** — Replace embedded token with `Office.getAccessTokenAsync()`. Register add-in in GIC's Entra tenant. Validate Exchange identity token server-side.
3. **Shared mailbox support** — Target requirement set 1.13 in manifest. Test that the add-in activates when Maribel opens emails in the quote@ shared mailbox.
4. **Admin deployment** — GIC's M365 admin deploys via Integrated Apps instead of user sideloading. Assign to specific users/groups.
