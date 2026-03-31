---
ask: "Move GIC Email Intelligence to production — Railway backend, Amplify frontend, fix pipeline, Observatory integration, auth, historical data processing"
created: 2026-03-30
workstream: gic-email-intelligence
session: 2026-03-30-a
sources:
  - type: codebase
    description: "Full pipeline architecture review of gic-email-intelligence repo"
  - type: web
    description: "Railway docs, AWS Amplify docs, LangChain docs — researched and encapsulated as OS skills"
  - type: codebase
    description: "Observatory auth module (auth.py, routers/auth.py) — JWT validation, copilot-server integration"
---

# GIC Email Intelligence — Production Deployment Plan

## Context

Demo delivered to JC (EVP/CUO) and Maribel (operations) on March 25. They were impressed by the email intelligence — the ability to see all submissions organized and understood. Less impactful: auto-drafts and ball-holder tracking (insufficient data to make accurate judgments).

**Direction shift:** Focus on data quality and the extraction pipeline. This system becomes the pipeline into GIC's Agency Management System (Unisoft). JC needs access to the UI and the extracted data. Auto-reply and assessment features stay in the codebase but are disabled until data sources exist to make them accurate.

**Key insight from GIC:** They use Outlook as a to-do list — enter data into AMS, then delete the email. The ultimate value: "we already extracted and organized this data, you just verify and push it to AMS."

## Scope

### In Scope
1. Fix the extraction pipeline (structured output with real PDF reading)
2. Reorder pipeline: extract → classify → link
3. Disable assess/draft stages (keep in code, configurable)
4. Deploy backend to Railway (API + cron jobs)
5. Deploy frontend to AWS Amplify (`gic.indemn.ai`)
6. Auth via copilot-server (same as Observatory)
7. Observatory navigation link
8. Dev + prod environments
9. Process 6 months of historical data through new pipeline

### Out of Scope (Future)
- AMS integration (Unisoft/Jeremiah)
- Email sending / Mail.Send permission
- Additional LOB configs beyond GL and Golf Cart
- Re-enabling assess/draft stages
- Outlook Add-in for production (needs GIC's M365 tenant)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    AWS Amplify                       │
│  gic.indemn.ai (prod)  /  dev.gic.indemn.ai (dev)  │
│  React + Vite SPA, Indemn design system             │
│  VITE_API_BASE → Railway API URL per branch         │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────┐
│               Railway Project                        │
│                                                      │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ api (web)   │  │ sync     │  │ processing    │  │
│  │ Always-on   │  │ Cron 5m  │  │ Cron 5m       │  │
│  │ Port 8080   │  │          │  │               │  │
│  │ FastAPI     │  │ outlook- │  │ outlook-agent │  │
│  │ + health    │  │ inbox    │  │ process       │  │
│  │   check     │  │ sync     │  │ --batch       │  │
│  └──────┬──────┘  └────┬─────┘  └───────┬───────┘  │
│         └──────────────┼─────────────────┘           │
│                        │ All share env vars          │
└────────────────────────┼─────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     MongoDB Atlas    S3 Bucket    Anthropic API
     (dev/prod)       attachments  (LLM calls)
```

### Railway Services (one repo, three services)

| Service | Type | Start Command | Schedule |
|---------|------|---------------|----------|
| api | Web service | `uvicorn gic_email_intel.api.main:app --host 0.0.0.0 --port 8080` | Always-on |
| sync | Cron job | `outlook-inbox sync` | Every 5 minutes |
| processing | Cron job | `outlook-agent process --batch` | Every 5 minutes |

All deploy from the same Docker image with different start commands. Supervisord removed.

### Environments

| Environment | Railway | Amplify | MongoDB | Purpose |
|-------------|---------|---------|---------|---------|
| prod | `production` | `prod` branch → `gic.indemn.ai` | Prod Atlas cluster, `gic_email_intelligence` | JC uses this |
| dev | `development` | `main` branch → `dev.gic.indemn.ai` | Dev Atlas cluster, `gic_email_intelligence_dev` | Development |
| PR preview | Auto-created | Auto-created | Shares dev database | Code verification |

PR preview environments only spin up the API service (not sync/processing crons).

### DNS

| Domain | Points To | Managed In |
|--------|-----------|------------|
| `gic.indemn.ai` | Amplify (prod branch) | Route 53 |
| `dev.gic.indemn.ai` | Amplify (main branch) | Route 53 |
| `api.gic.indemn.ai` | Railway (prod API) | Route 53 |
| `api-dev.gic.indemn.ai` | Railway (dev API) | Route 53 |

## Auth

### How It Works

GIC Email Intelligence uses the same auth system as Observatory and Copilot Dashboard:

1. **Login page** on GIC frontend — email/password form
2. **Signin proxied** through GIC backend to copilot-server (`/auth/signin`) — avoids CORS
3. **JWT returned** to frontend, stored in localStorage
4. **JWT validated locally** by GIC backend — same `JWT_SECRET` as copilot-server/Observatory, HS256, no-exp verification (copilot tokens don't include exp)
5. **Org-scoped access** — after decoding JWT, check user's org membership:
   - `@indemn.ai` email → full access (admin)
   - GIC org ID (`65eb3f19e5e6de0013fda310`) in `tiledesk.project_users` → full access
   - Everyone else → 403 Forbidden

### Observatory Integration

Observatory adds a navigation link: `gic.indemn.ai/?token=${localStorage.getItem('token')}`. GIC frontend picks up token from URL, stores in localStorage, strips from URL. If token is expired/invalid, redirects to login page.

### Required Env Vars (Auth)

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET` | Same as copilot-server — for local JWT validation |
| `COPILOT_SERVER_URL` | For proxying signin requests (e.g., `https://devcopilot.indemn.ai/api`) |
| `TILEDESK_DB_URI` | For org membership lookup in `tiledesk.project_users` |
| `GIC_ORG_ID` | `65eb3f19e5e6de0013fda310` — hardcoded, used for access control |

## Pipeline Changes

### Current Pipeline (broken)
```
sync → classify (text-only, blind to PDFs) → link → extract (can't see PDFs) → assess → draft
```

### New Pipeline
```
sync → extract (structured output, real PDF reading) → classify (with extraction context) → link
                                                                                              ↓
                                                              [assess → draft: disabled, configurable]
```

### 1. Fix Extraction (the big change)

Replace the broken ReAct-based pdf-extractor with a single structured output LLM call:

- Download all attachments from S3 for the email
- Build a multimodal `HumanMessage` with:
  - Text context (email subject, body, sender)
  - Each attachment as a content block: PDFs as `type: "file"`, images as `type: "image"`, others as appropriate
- Call `model.with_structured_output(EmailExtraction, method="json_schema")` — one LLM call per email
- Get back validated Pydantic model
- Save to `extractions` collection

**Unbiased extraction schema** — we don't know what the PDF contains, so the schema must be flexible:

```python
class AttachmentExtraction(BaseModel):
    attachment_name: str
    document_type: str  # LLM determines: quote_letter, application, loss_run, drivers_license, acord_form, etc.
    summary: str  # What this document is and what it contains
    extracted_fields: dict[str, Any]  # Open-ended — whatever the LLM finds relevant
    reference_numbers: list[str]  # Always useful for linking

class EmailExtraction(BaseModel):
    attachments: list[AttachmentExtraction]
```

The `extracted_fields` is free-form. The LLM decides what's important based on the actual document content. LOB-specific field checking happens downstream when comparing against LOB configs.

**Requires:** `langchain-anthropic>=1.1.0` for native Anthropic structured output (constrained decoding).

### 2. Reorder Pipeline

Extraction runs first. Classifier gets extraction data as context — instead of guessing from attachment filenames, it sees "this email has a USLI GL quote letter with premium $2,400 for Vivaria Florida LLC."

Update classifier skill to accept and use extraction context.

### 3. Disable Assess/Draft

Add config: `PIPELINE_STAGES=extract,classify,link` (default). When assess/draft are omitted, harness skips them. Code, skills, and tools all stay. Document in skill files what enables each disabled stage.

### 4. Adapt for Railway

- Remove `supervisord.conf`
- Update Dockerfile: single process, `CMD` set per service
- Add `railway.json` with service definitions + cron schedules
- Three services share same image, different start commands

### 5. Auth Middleware

- New auth module (simplified from Observatory's `auth.py`)
- JWT validation: decode with shared `JWT_SECRET`, HS256
- Org check: query `tiledesk.project_users` for GIC org ID
- Indemn employees bypass org check
- Login page + signin proxy endpoint
- Keep `API_TOKEN` as fallback for internal/CLI use

### 6. Frontend Updates

- CORS origins for `gic.indemn.ai`, `dev.gic.indemn.ai`, Railway domains
- `VITE_API_BASE` points to Railway API URL (branch-level overrides)
- Token from URL param + localStorage (replace sessionStorage)
- Login page component
- Hide draft cards, ball-holder indicators, assessment summaries (disabled features)
- Focus detail view on: email content, extracted data, LOB requirements

## Historical Data Processing

### Strategy: Clean Slate for 6 Months

Delete existing submissions, extractions, assessments, drafts for emails from last 6 months. Keep raw emails. Re-run new pipeline (extract → classify → link) to produce clean, consistent data.

### Rollout

1. **Dev, small sample (20-50 emails)** — Verify pipeline works end-to-end. Check extraction accuracy, classification improvement, linking correctness.
2. **Dev, full 6 months** — Run complete backfill. Spot-check results across email types and LOBs.
3. **Prod** — Same clean slate + backfill. This is what JC sees.

### Implementation

- Migration script with `--dry-run` and `--execute` modes
- Reprocessing command with `--limit` for sample runs and `--since` for date range
- Estimated LLM cost: ~$30-150 for full 6-month backfill (depends on PDF sizes)

## Definition of Done

This phase is complete when:

1. **Backend on Railway** — API (always-on) + sync cron + processing cron, healthy in prod
2. **Frontend on Amplify** — `gic.indemn.ai` live, `dev.gic.indemn.ai` for dev
3. **Auth working** — JC logs in via copilot-server auth, org-scoped access enforced
4. **Observatory link** — Click-through from Observatory with token passthrough
5. **Pipeline accurate** — Extract → classify → link running on cron, extractions read real PDF content
6. **6 months clean data** — Historical backfill complete in prod, accurate extracted data
7. **Email sync live** — New emails processed automatically within 5-10 minutes

## Execution Order

### Phase 1: Pipeline Fix (code work, local)
1. Fix extraction — structured output with real PDF reading
2. Reorder pipeline — extract → classify → link
3. Disable assess/draft stages (configurable)
4. Test locally with small sample (20-50 emails in dev DB)
5. Verify extraction quality, classification improvement

### Phase 2: Infrastructure Setup
6. Railway: create project, configure 3 services, set env vars for dev
7. Amplify: create app, connect repo, configure `amplify.yml`, set env vars
8. DNS: `gic.indemn.ai`, `dev.gic.indemn.ai`, `api.gic.indemn.ai` in Route 53
9. Deploy to dev environment, verify everything works

### Phase 3: Auth
10. Implement auth module (JWT validation, org check, signin proxy)
11. Add login page to frontend
12. Test auth flow end-to-end in dev
13. Add Observatory navigation link

### Phase 4: Production
14. Configure Railway prod environment + Amplify prod branch
15. Deploy to prod
16. Run clean slate migration + 6-month backfill in prod
17. Verify JC can log in and see accurate data
18. Enable live email sync cron

### Open Items / Research Needed
- **Railway account setup** — Craig has created an account, need to link repo and configure
- **Copilot server credentials** — Need `JWT_SECRET` and `COPILOT_SERVER_URL` for prod
- **Tiledesk DB URI** — Need connection string for org membership lookup
- **JC's copilot account** — Verify JC has a copilot-server account with GIC org membership
- **Observatory change** — Someone needs to add the nav link in Observatory's header/sidebar
