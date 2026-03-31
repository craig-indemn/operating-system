---
ask: "Explore the intake-manager codebase and understand how to integrate GIC Email Intelligence into it as a unified solution"
created: 2026-03-23
workstream: gic-email-intelligence
session: 2026-03-23-a
sources:
  - type: github
    description: "Full codebase exploration of intake-manager repo (indemn-ai/intake-manager, main branch)"
  - type: github
    description: "Full codebase exploration of gic-email-intelligence repo (local, main branch)"
---

# Intake Manager Integration Analysis

## Executive Summary

The **intake-manager** (built by Dhruv Rajkotia and Rudra Thakar) and **GIC Email Intelligence** (built by Craig) are complementary systems on the same tech stack (FastAPI + MongoDB + LangChain + React). Intake-manager is a **document processing pipeline** (documents in → parameters extracted → validation → quote). GIC is an **inbox intelligence layer** (understand conversations, track submission lifecycle, suggest actions, draft replies). The natural integration is GIC's intelligence becoming intake-manager's "inbox view" while intake-manager's extraction + validation + quoting stays as the processing backbone.

---

## Intake Manager — What the Team Built

### Overview

Production insurance underwriting submission platform. Processes insurance applications through document extraction, AI-powered parameter validation, and multi-provider insurance quote generation.

**Tech stack:** FastAPI (Python 3.11+), Next.js 16 (React 19, TypeScript), MongoDB Atlas (Motor async), LangChain/LangGraph, Docker + Datadog.

**Contributors:** Dhruv Rajkotia (~25 commits), Rudra Thakar (~22 commits). Active development — latest commits are coverage hallucination detection, Northfield territory enrichment, quote comparison UI.

### Architecture

```
Email arrives (Gmail/Outlook via Composio webhook)
    ↓
outlook_message_service / gmail_thread_service
    ↓ (fetch message + attachments, dedup, dispatch)
POST /api/intake/submission (multipart/form-data)
    ↓ (202 Accepted, continues in background)
Pipeline Orchestrator (v1 or v2)
    ↓
    ├── IntakeStep — create/get submission, attach documents
    ├── DocumentProcessingStep — OCR/text extraction (Form Extractor API)
    ├── WorkflowDetectionStep — auto-detect workflow (rule-based + LLM fallback)
    ├── ExtractionStep — LangChain structured extraction into parameters
    └── ValidationStep — LangGraph multi-step validation
    ↓
Quote Generation (on demand)
    ├── Parameter extraction + normalization
    ├── Provider dispatch (ACIC XML, Nationwide PL SAML)
    └── AI comparison summary
```

**Two pipeline modes:**
- **v1 (default):** GPT-based multi-step pipeline (intake → OCR → workflow detection → extraction → validation)
- **v2:** Claude deep agent single-step extraction (replaces steps 2-5)

### Backend Structure (`app/`)

```
app/
├── main.py                    # FastAPI entry, lifespan, router registration
├── db/mongo_connect.py        # Async MongoDB singleton (Motor)
├── models/                    # Pydantic data models
│   ├── submission.py          # Submission + processing stages
│   ├── workflow.py            # Workflow config (matching, extraction, validation, quotes)
│   ├── parameter.py           # Individual parameter records
│   ├── event.py               # Thread events + timeline
│   ├── step.py                # Step execution snapshots
│   ├── extraction.py          # Document extraction records
│   ├── quote.py               # Quote records
│   ├── quote_document.py      # Quote document storage
│   ├── submission_state.py    # Submission state tracking
│   ├── email_account.py       # Gmail/Outlook account model
│   ├── thread_attachment.py   # Attachment references
│   ├── merge_strategy.py      # Extraction merge strategies
│   └── extraction_schemas/    # LangChain Pydantic models for structured extraction
│       ├── base.py
│       ├── northfield.py
│       ├── general_liability.py
│       └── personal_lines.py
├── routers/                   # HTTP endpoint handlers
│   ├── intake.py              # POST /api/intake/submission
│   ├── submissions.py         # Submission CRUD
│   ├── validation.py          # Validation triggers
│   ├── quotes.py              # Quote generation (SSE streaming)
│   ├── parameters.py          # Parameter CRUD
│   ├── workflows.py           # Workflow CRUD
│   ├── threads.py             # Thread/event timeline
│   ├── progress.py            # SSE progress streaming
│   ├── audit.py               # Parameter change history
│   ├── form_schemas.py        # Dynamic UI schemas
│   ├── auth.py                # JWT auth (delegates to copilot-server)
│   ├── integrations.py        # Gmail/Outlook account management
│   └── webhooks.py            # Composio webhook handlers
├── services/
│   ├── pipeline/              # v1 submission processing
│   │   ├── orchestrator.py    # Event-driven step orchestration
│   │   ├── steps/             # Intake, DocumentProcessing, WorkflowDetection, Extraction, Validation
│   │   ├── retry_worker.py    # Background retry for failed jobs
│   │   └── error_classifier.py
│   ├── pipeline_v2/           # v2 Claude deep agent
│   │   └── steps/deep_agent_step.py
│   ├── extraction_service.py  # Document text fetching/combining
│   ├── validation/graph/      # LangGraph validation
│   │   ├── nodes/             # parameter, rule, schema, compliance, security checks
│   │   ├── subgraphs/         # Org-specific (Northfield)
│   │   └── config/organization_routing.py
│   ├── quote/                 # Quote orchestration
│   │   ├── quote_service.py   # Main orchestrator
│   │   ├── providers/acic/    # Atlantic Casualty XML API
│   │   ├── providers/nationwide/  # Nationwide SAML + PL/CL
│   │   └── providers/registry.py
│   ├── composio_service.py    # Composio API integration
│   ├── gmail_thread_service.py
│   ├── outlook_message_service.py
│   ├── workflow_service.py
│   ├── submission_service.py
│   └── attachment_storage_service.py
├── prompts/                   # LLM prompt templates (auto-registered)
└── middleware/                # Error handling, request tracking, auth
```

### Frontend Structure (`frontend/`)

Next.js 16 App Router with React 19, TypeScript, Tailwind CSS 4, Radix UI (shadcn), React Query + Zustand.

```
frontend/
├── app/
│   ├── layout.tsx             # Root layout, navigation
│   ├── page.tsx               # Home (org/workflow list)
│   ├── organization/[orgId]/
│   │   ├── page.tsx           # Org overview
│   │   ├── integrations/page.tsx  # Email account management
│   │   └── workflow/[workflowId]/
│   │       ├── page.tsx       # Submission list for workflow
│   │       └── submission/[threadId]/page.tsx  # Submission detail
│   └── submission/[threadId]/page.tsx  # Flat submission detail
├── components/
│   ├── ui/                    # shadcn/ui components
│   ├── forms/                 # Tab-specific form components (business, quote, vehicles, drivers, coverage, etc.)
│   ├── dynamic-form/          # Backend-driven form rendering
│   └── quote/                 # Quote comparison components
├── lib/
│   ├── api.ts                 # Axios client (workflowApi, submissionApi, parameterApi, quoteApi, etc.)
│   ├── types.ts               # TypeScript types mirroring backend Pydantic
│   └── utils.ts
├── hooks/use-submissions.ts   # React Query hooks
├── store/submission-store.ts  # Zustand (selectedThreadId, activeTab)
└── providers/query-provider.tsx
```

**Key frontend views:**
- Org overview → Workflow list → Submission list (with search/status filter) → Submission detail
- Submission detail has tabs: Business Info, Coverage, Vehicles, Drivers, Commodities, Mileage, Prior Carrier, Quote
- Dynamic forms rendered from backend schemas
- Quote comparison with multi-provider side-by-side

### MongoDB Collections (~16)

| Collection | Purpose |
|---|---|
| `submission_data` | Main submission records (thread_id, id_workflow, status, processing_stage, parameters, validation_result) |
| `workflows_config` | Workflow definitions per org (matching config, extraction config, validation config, quote config) |
| `submission_parameters` | Individual parameters (thread_id + field_path unique, value, validation_status, audit trail) |
| `form_extractor.extractions` | Document OCR/text extractions (session_id = thread_id, filename, raw_text) |
| `thread_events` | Event timeline (thread_id, event_number, event_type, triggered_by) |
| `step_snapshots` | Pipeline step execution details (inputs, outputs, duration_ms) |
| `submission_states` | Submission state tracking (overall_status, last_activity) |
| `quotes` | Generated quotes (thread_id, provider, version, is_latest, quote_data) |
| `quote_documents` | Quote PDFs/documents (quote_id, storage_url) |
| `email_connected_accounts` | Gmail/Outlook OAuth accounts per org (Composio) |
| `email_triggers` | Composio trigger subscriptions |
| `email_processed_threads` | Email deduplication tracker |
| `parameter_audit_logs` | Parameter change history |
| `failed_pipeline_jobs` | Dead-letter retry queue |
| `form_schemas` | Dynamic UI form schemas |
| `thread_attachments` | Attachment storage references |

### API Endpoints

**No auth:** `/api/intake/submission`, `/api/progress/stream` (SSE), `/api/webhooks/composio`, `/api/auth/verify`, `/health`

**Auth required (JWT via copilot-server):**
- Submissions: GET/PATCH/DELETE by thread_id, list by workflow
- Parameters: GET/PATCH single, POST bulk-update, GET failed
- Validation: POST trigger
- Quotes: POST generate (SSE streaming), GET list, WebSocket alternative
- Workflows: GET list by org, GET single
- Threads: GET events
- Audit: GET logs
- Form Schemas: GET list, GET single
- Integrations: Gmail/Outlook account CRUD, trigger management

### Authentication

JWT tokens generated by **copilot-server** (external). Backend validates via `GET /users/` on copilot-server. Frontend stores in `sessionStorage.authToken`, attaches as `Authorization: JWT <token>`.

### Deployment

Docker (python:3.12-slim backend, Node.js frontend). docker-compose with separate backend (port 8000) and frontend (port 3001). AWS ALB for SSL termination + routing (`/api/*` → backend, else → frontend). Datadog APM + structured JSON logging.

### Recent Development Focus

- Coverage hallucination detection (3-layer defense: prompt fix, hard-block on ratio detection, auto-correct)
- Northfield territory enrichment + Additional Insureds
- Quote comparison UI (multi-provider side-by-side)
- Dead-letter retry worker for failed pipeline jobs
- Composio webhook fixes
- Nationwide CL (Commercial Lines) integration

---

## GIC Email Intelligence — What We Built

### Overview

Email intelligence system for GIC Underwriters. Analyzes the quote@gicunderwriters.com inbox — classifies emails, links them into submissions via reference numbers, extracts data from PDFs, identifies gaps in submissions, and drafts replies. Includes a web dashboard and an Outlook Add-in.

**Tech stack:** FastAPI (Python 3.12), React 19 + Vite + Tailwind (frontend), React + Office.js (Outlook Add-in), MongoDB Atlas, LangChain/LangGraph, S3 for attachments.

### Key Capabilities Intake-Manager Lacks

1. **Multi-email submission linking** — Reference numbers (USLI/GIC patterns) + fuzzy name matching link emails across threads into one submission. Intake-manager treats each email/thread as independent.

2. **Email classification** — 14 email types (usli_quote, agent_submission, gic_application, etc.) with line-of-business detection. Intake-manager has workflow detection but not email-type classification.

3. **Conversation view** — Thread parser splits embedded reply chains into individual messages displayed as chat bubbles. Intake-manager has thread events but no conversation parsing.

4. **Business lifecycle stages** — new → awaiting_info → with_carrier → quoted → attention. Reflects insurance submission lifecycle, not processing pipeline stages.

5. **Gap analysis** — LOB-specific required fields, stage-aware (new submissions check everything, quoted submissions only check quote details). Two tiers: Active Requests (from conversation, amber) + General Requirements (collapsed, gray).

6. **AI draft generation** — Suggested reply emails: info_request, quote_forward, decline_notification, followup. Drafts include correct recipients, markdown formatting, "Reply with this" via Office.js.

7. **Triaged action queues** — Board view: Ready to Send, Needs Review, Monitoring. Cards show lifecycle badges + AI action summaries. Meaningful empty states.

8. **Done state + history** — Resolve submissions (quote_forwarded, decline_notified, info_request_sent, manually_closed). Resolved disappear from board, appear in Analytics history.

9. **Outlook Add-in** — Task pane sidebar in Outlook. Reads current email, matches to backend submission, shows analysis + gap analysis + draft. "Reply with this" opens native Outlook reply.

10. **Analytics** — Volume chart, email type breakdown, LOB distribution, top agents, resolution history.

### Backend Structure

```
src/gic_email_intel/
├── api/
│   ├── main.py          # FastAPI app (CORS, rate limiting, static mount)
│   ├── auth.py          # Token verification
│   └── routes/          # health, submissions, emails, stats, ws
├── cli/
│   ├── main.py          # Typer root (7 command groups, 25+ commands)
│   └── commands/        # sync, emails, submissions, extractions, drafts, stats, migrate
├── agent/
│   ├── harness.py       # Skill executor (ReAct agent via LangGraph)
│   ├── llm.py           # LLM factory (Anthropic/OpenAI)
│   ├── tools.py         # 15+ LangChain tools
│   ├── skills/          # Markdown skill definitions
│   └── lob_configs/     # JSON LOB requirement configs
├── core/
│   ├── db.py            # MongoDB (sync + async via pymongo + motor)
│   ├── models.py        # Pydantic domain models (6 entities, 6 enums)
│   ├── graph_client.py  # Microsoft Graph API (direct, not Composio)
│   ├── s3_client.py     # S3 attachment storage
│   ├── linker.py        # Reference number extraction + fuzzy matching
│   ├── lob_config.py    # LOB requirement loader + completeness computation
│   └── thread_parser.py # Email thread chain parsing
└── config.py            # Pydantic Settings
```

### Frontend Structure

```
ui/src/
├── App.tsx              # Root with tabs: Inbox, Analytics, How It Works
├── pages/               # Board, SubmissionDetail, Analytics, HowItWorks
├── components/          # ActionColumn, SubmissionCard, DraftCard, GapAnalysis, etc.
├── api/                 # client (axios), types (20+ interfaces), hooks (React Query)
└── hooks/               # useWebSocket (live updates via MongoDB change streams)
```

### Outlook Add-in

```
addin/src/
├── TaskPane.tsx          # Root (6 states, ItemChanged handler)
├── components/           # SubmissionHeader, AddinSummary, AddinGapAnalysis, AddinDraft
└── api/                  # client (lookupEmail), extract (reference numbers), types
```

### MongoDB Collections (5 + 1 system)

| Collection | Purpose |
|---|---|
| `emails` | Full email records (graph_message_id, subject, body, classification, submission_id, attachments) |
| `submissions` | Insurance submissions (named_insured, LOB, stage, reference_numbers, email_count, resolved_at) |
| `extractions` | Structured PDF data (named_insured, carrier, premium, coverage_limits, effective_date) |
| `drafts` | Suggested replies (draft_type, to_email, subject, body, status) |
| `sync_state` | Outlook sync metadata |

---

## Side-by-Side Comparison

### Capabilities Matrix

| Capability | Intake Manager | GIC Email Intelligence |
|---|---|---|
| **Email ingestion** | Composio webhooks (Gmail + Outlook) | Direct Microsoft Graph API polling |
| **Document OCR** | Form Extractor API | None (relies on text-based PDFs, Claude Vision for images) |
| **LLM extraction** | LangChain structured extraction → flat `parameters` dict | Claude Vision on PDFs → structured fields |
| **Multi-email linking** | None — one thread = one submission | Reference numbers link emails into submission lifecycles |
| **Email thread parsing** | None | Splits embedded reply chains into conversation view |
| **Email classification** | Workflow detection (rule-based + LLM) | 14 email types + line of business + intent |
| **Stage model** | Processing pipeline: received → extracting → validated → completed | Business lifecycle: new → awaiting_info → with_carrier → quoted |
| **Validation** | LangGraph multi-step (schema, rules, compliance, security, org-specific) | LOB-specific gap analysis (stage-aware, two-tier) |
| **Quoting** | Multi-provider (ACIC XML, Nationwide PL SAML) | None |
| **Draft generation** | None | AI reply drafts (info request, quote forward, decline, followup) |
| **Board/triage view** | Submission list by workflow + search + status filter | Triaged action queues (Ready to Send, Needs Review, Monitoring) |
| **Outlook Add-in** | None | Sidebar with analysis + gap analysis + "Reply with this" |
| **Done state + history** | None | Resolve → disappears from board → Analytics history |
| **Analytics** | None | Volume, types, LOBs, agents, resolutions |
| **Auth** | JWT via copilot-server | Embedded API token |
| **Multi-tenant** | Yes (organization_id + workflow scoping) | No (single-tenant GIC) |
| **Dynamic forms** | Yes (backend-driven form schemas) | No |
| **Quote comparison** | Yes (multi-provider side-by-side) | No |
| **Deployment** | Docker + EC2 + ALB + Datadog | Local only (cloudflared tunnel for demo) |
| **Tests** | 6 test files | 14 test files (108 passing) |
| **CLI** | None | Typer CLI (7 groups, 25+ commands) |
| **WebSocket** | None (uses SSE for progress) | MongoDB change stream broadcasts |

### Data Model Comparison

| Aspect | Intake Manager | GIC |
|---|---|---|
| **Submission ID** | `thread_id` (from email thread/message ID) | `_id` (ObjectId) |
| **Submission fields** | Flat `parameters` dict (dynamic, schema-driven) | Structured fields (named_insured, LOB, stage, reference_numbers, carrier, premium, etc.) |
| **Email storage** | No separate email collection — email becomes the submission | `emails` collection with full metadata, body, classification, submission linkage |
| **Stage tracking** | `processing_stage` (pipeline progress) | `stage` (business lifecycle) + `stage_history[]` |
| **Extraction storage** | `form_extractor.extractions` (raw text from OCR) + `submission_parameters` (structured values) | `extractions` collection (structured PDF data per attachment) |
| **Drafts** | None | `drafts` collection (type, recipient, body, status) |
| **Events** | `thread_events` + `step_snapshots` (pipeline execution tracking) | Stage history embedded in submission |
| **Organization** | `id_workflow` → `workflows_config.id_organization` | None (single-tenant) |

---

## Integration Vision

### The Natural Merge

The two systems are **complementary, not competing**:

- **Intake-manager** = the **processing engine** (documents → parameters → validation → quote)
- **GIC Email Intelligence** = the **inbox intelligence layer** (understand conversations, track lifecycle, suggest actions)

**Unified system:**
1. GIC's email intelligence becomes intake-manager's **"inbox view"** — triaged board, gap analysis, draft replies, Outlook Add-in
2. Intake-manager's extraction + validation + quoting stays as the **processing backbone**
3. GIC's multi-email linking fills intake-manager's biggest gap — linking emails into submission lifecycles
4. GIC's conversation view enriches intake-manager's event timeline

### What Moves into Intake-Manager

**Backend additions (new modules):**
- `emails` collection + email sync service (Graph API or enhanced Composio)
- Email classification pipeline (14 types + LOB detection)
- Reference number extraction + submission linking (`linker.py`)
- Stage lifecycle management (business stages, not just processing stages)
- Gap analysis engine (LOB configs + stage-aware completeness)
- Draft generation service
- Board/triage aggregation endpoints
- Lookup endpoint (for Outlook Add-in matching)
- Analytics/stats endpoints
- WebSocket change stream broadcasts
- Thread parser (conversation chain splitting)

**Frontend additions (new views/components):**
- Inbox/Board view (triaged action queues)
- Submission detail: conversation view + reasoning chain (summary → extraction → requirements → gaps → draft)
- Draft workflow (approve → copy/reply → mark as done)
- Analytics page (volume, types, LOBs, agents, history)
- Done state + history

**Outlook Add-in (new directory):**
- Separate Vite + React app (Office.js requires its own build)
- Task pane sidebar components
- Manifest XML

### What Stays in Intake-Manager As-Is

- Pipeline orchestrator (v1 + v2)
- Document processing (OCR via Form Extractor)
- LangChain structured extraction into parameters
- LangGraph validation workflow
- Quote generation (ACIC, Nationwide PL)
- Dynamic forms
- Workflow configuration
- JWT auth via copilot-server
- Composio email integration
- Docker + deployment infrastructure

### Key Integration Decisions

| Decision | Options | Recommendation |
|---|---|---|
| **Email ingestion** | A) Keep Composio only, B) Add direct Graph API alongside, C) Replace Composio with Graph API | **B** — Composio for multi-provider breadth, Graph API for deep Outlook integration (message IDs, threading, add-in matching) |
| **Submission model** | A) Keep flat `parameters` dict, B) Add structured fields alongside, C) Migrate to structured model | **B** — Add GIC's structured fields (named_insured, LOB, stage, reference_numbers) as top-level fields on submission_data. Keep parameters dict for extraction/validation/quoting pipeline. |
| **Stage model** | A) Keep processing_stage only, B) Add business_stage alongside, C) Merge into one | **B** — Two orthogonal stage tracks: `processing_stage` (pipeline progress) + `business_stage` (lifecycle: new → awaiting_info → with_carrier → quoted → attention). They serve different purposes. |
| **Frontend framework** | A) Next.js only, B) Migrate GIC views to Next.js, C) Micro-frontend | **B** — Port GIC's React/Vite views into Next.js App Router pages. The Outlook Add-in stays as separate Vite build (Office.js requirement). |
| **Database** | A) Separate databases, B) Same database new collections, C) Merge collections | **B** — Add `emails`, `drafts` collections to intake-manager's database. Extractions can coexist (GIC's `extractions` has different schema from `form_extractor.extractions`). |
| **Auth** | A) Keep JWT only, B) Add token auth for add-in, C) Unify via SSO | **B** — JWT for web app (copilot-server), API token for Outlook Add-in (simpler for iframe). Production: Office.js SSO via `getAccessTokenAsync`. |
| **Email storage** | A) Don't store emails (current intake-manager), B) Add emails collection | **B** — GIC's `emails` collection is essential for conversation view, classification, reference number linking, and audit trail. |

### Migration Approach

**Phase 1: Backend integration (parallel to existing)**
- Add GIC's collections to intake-manager's database
- Port GIC's core modules: linker, thread_parser, lob_config, classification
- Add new API routes alongside existing: `/api/inbox/*` (board, detail, lookup, analytics)
- Add draft generation service
- Keep existing pipeline untouched

**Phase 2: Frontend integration**
- Port Board view to Next.js
- Port Submission detail (conversation + reasoning chain) to Next.js
- Port Analytics page
- Port Draft workflow
- Wire up to existing auth

**Phase 3: Deep integration**
- Connect email classification → workflow detection (classification enriches workflow matching)
- Connect extraction → gap analysis (extracted parameters feed completeness computation)
- Connect draft generation → quote pipeline (draft can trigger quoting)
- Unified submission lifecycle (processing_stage + business_stage on same record)

**Phase 4: Outlook Add-in**
- Port add-in directory into intake-manager repo
- Point add-in at intake-manager's API
- Production deployment (eliminate cloudflared tunnel)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| **Schema collision** | Medium — both use MongoDB with different collection structures | Use new collection names, don't modify existing collections |
| **Auth model mismatch** | Low — GIC uses tokens, intake-manager uses JWT | Add-in uses separate auth path; web views use existing JWT |
| **Frontend framework gap** | Medium — porting React/Vite to Next.js requires routing/SSR changes | Port incrementally, page by page. Add-in stays as Vite. |
| **Pipeline disruption** | High — intake-manager is in production | Phase 1 adds routes alongside, never modifies existing pipeline |
| **Multi-tenant gap** | Medium — GIC is single-tenant, intake-manager is multi-org | Add organization_id to GIC collections. GIC becomes one org's "inbox view" configuration. |
| **Email ingestion conflict** | Low — Composio and Graph API can coexist | Graph API for deep features (message IDs, threading), Composio for breadth |

---

## Files Reference

**Intake Manager repo:** `/Users/home/Repositories/intake-manager/`
**GIC Email Intelligence repo:** `/Users/home/Repositories/gic-email-intelligence/`
**Intake Manager CLAUDE.md:** `/Users/home/Repositories/intake-manager/CLAUDE.md`
**GIC design doc:** `artifacts/2026-03-19-outlook-addin-design.md`
**GIC technical design:** `artifacts/2026-03-16-technical-design.md`
