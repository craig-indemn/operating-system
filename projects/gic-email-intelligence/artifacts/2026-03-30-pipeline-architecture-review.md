---
ask: "Complete end-to-end understanding of how the GIC Email Intelligence pipeline works, every step, every file, every limitation"
created: 2026-03-30
workstream: gic-email-intelligence
session: 2026-03-30-a
sources:
  - type: codebase
    description: "Full read of all key backend files: sync, agent harness, all 5 skills, tools, config, Docker, API main"
---

# GIC Email Intelligence — Complete Pipeline Architecture Review

Post-demo review ahead of production deployment. Every step documented from Outlook to final result.

## Phase 1: Email Sync (Outlook → MongoDB + S3)

**Trigger:** Supervisord runs `outlook-inbox sync` in a loop every 60 seconds. Or manually via CLI.

**Entry point:** `src/gic_email_intel/cli/commands/sync.py`

**What happens:**

1. `GraphClient` (`src/gic_email_intel/core/graph_client.py`) authenticates to Microsoft Graph API using **OAuth2 client credentials** (tenant ID + app registration + client secret). This is a service-level connection to `quote@gicunderwriters.com` — not a delegated user login.

2. The sync checks `sync_state` collection for `last_sync_at`. If it exists, it fetches only messages newer than that timestamp. First run fetches everything.

3. For each message from Graph API, it:
   - Deduplicates by `graph_message_id` (unique index — if already in DB, skip)
   - Parses sender address/name, recipients, received timestamp
   - Resolves the Outlook folder name (Inbox, Archive, etc.)
   - Stores the **text-only** body (Graph API `Prefer: outlook.body-content-type="text"` header — no HTML)
   - If `hasAttachments=true`: fetches each attachment's metadata + base64 `contentBytes`, decodes, **uploads to S3** (`indemn-gic-attachments` bucket), stores the S3 key as `storage_path`
   - Inserts the email document into `emails` collection with `processing_status: "pending"`

4. Updates `sync_state` with new `last_sync_at` timestamp and total email count.

**Data created:** One document per email in `emails` collection. Attachments as files in S3 (not stored in MongoDB). Each email starts at status `"pending"`.

**Key files:**
- `src/gic_email_intel/cli/commands/sync.py` — Sync command
- `src/gic_email_intel/core/graph_client.py` — Microsoft Graph API client (OAuth2, pagination, rate limiting, retry)
- `src/gic_email_intel/core/s3_client.py` — S3 upload/download/presigned URL helpers

## Phase 2: Agent Processing Pipeline

**Trigger:** Supervisord runs `outlook-agent process --batch` in a loop every 60 seconds. Finds all emails with `processing_status: "pending"`.

**Entry point:** `src/gic_email_intel/agent/harness.py`

For each pending email, it runs through up to 5 skills sequentially. Each skill is a **LangGraph ReAct agent** — an LLM (Claude Sonnet by default) with a set of structured tools. The LLM gets a markdown prompt (the skill file), a user message describing the task, and can call tools iteratively up to 15 times (recursion_limit).

**LLM setup:** `src/gic_email_intel/agent/llm.py` — `ChatAnthropic(model="claude-sonnet-4-6", temperature=0, max_tokens=4096)`. Model overridable via `--model` flag (e.g., `claude-haiku-4-5-20251001` for batch).

### Step 1: Email Classifier

**Skill:** `src/gic_email_intel/agent/skills/email_classifier.md`
**Tools:** `get_email`, `save_classification`

The LLM reads the email (via `get_email` which returns the full JSON including body text and attachment metadata — names, sizes, content types — but NOT attachment content). It classifies:
- `email_type` — one of 14 types (usli_quote, agent_submission, usli_decline, gic_portal_submission, etc.)
- `line_of_business` — e.g., "General Liability", "Golf Cart"
- `named_insured` — extracted insured name
- `reference_numbers` — all ref numbers found in subject + body
- `intent_summary` — one-sentence description
- `lines_of_business` — all LOBs detected (for multi-LOB emails)

**Key limitation:** The classifier only sees email text and attachment filenames. It does NOT see PDF content. For USLI emails, the subject line and USLI reference prefix give clear signals (MGL = GL, XPL = Excess Personal Liability). For agent submissions where the body just says "please see attached" — it's guessing from attachment names.

**Status after:** `"classified"`

### Step 2: Submission Linker

**Skill:** `src/gic_email_intel/agent/skills/submission_linker.md`
**Tools:** `get_email`, `search_submissions`, `create_submission`, `link_email_to_submission`, `update_submission_stage`, `update_submission`, `get_lob_config`

1. Reads the email's classification for reference numbers
2. Searches existing submissions by ref number (exact match on `reference_numbers` array)
3. If no match, tries fuzzy insured name match (rapidfuzz, same LOB, within 90 days)
4. If still no match, creates a new submission
5. Links the email to the submission (`email.submission_id` = submission ObjectId)
6. Updates submission counters atomically ($inc email_count/attachment_count, $min first_email_at)
7. Sets the submission stage based on email type (e.g., usli_quote → "quoted", usli_decline → "declined")
8. Detects operating context:
   - `operating_mode` — brokered vs direct_underwritten (from LOB config `workflow_type`)
   - `intake_channel` — gic_portal, granada_portal, usli_retail_web, csr_relay, or agent_email (from `from_address` patterns)
   - `automation_level` — `auto_notified` for USLI direct quotes (agent submitted via USLI Retail Web, GIC only notified)

**Status after:** `"linked"`

### Step 3: PDF Extractor

**Only runs if** the email has PDF attachments (checked by `has_extractable_pdf()` in harness.py).
**Skill:** `src/gic_email_intel/agent/skills/pdf_extractor.md`
**Tools:** `get_email`, `save_extraction`

The skill instructions say: "Read the email, identify PDF attachments, for each PDF attachment extract structured data, save extraction."

**CRITICAL PROBLEM: The agent cannot actually see PDF content.** The `get_email` tool returns attachment metadata (name, content_type, size, storage_path) but NOT the actual PDF bytes. There is no tool to download from S3 and present content to the LLM. The `save_extraction` tool just stores whatever the LLM outputs. So the LLM is producing extractions based on filenames and email context, not actual document content.

The good extractions that exist in the database came from two **separate** paths:
1. **Batch scripts** (`prepare_batches.py`, `data/batches/`) — sent real PDF bytes to Claude vision outside the agent framework
2. **Claude Code subagents** during demo prep — could read files directly from disk

The agent-based pipeline's extraction step does not produce real extractions. This is the #1 issue for production.

**Status after:** `"extracted"` (set by harness.py directly after skill runs)

### Step 4: Situation Assessor

**Only runs if** not `skip_linking` and the email has a linked submission.
**Skill:** `src/gic_email_intel/agent/skills/situation_assessor.md` (351 lines)
**Tools:** `get_email`, `list_emails`, `get_submission`, `list_extractions`, `get_lob_config`, `save_assessment`, `update_submission_stage`

Reads everything — the submission, all linked emails with bodies, all extractions, the LOB config. Produces a comprehensive `SituationAssessment`:
- `situation_type` — 11 values: new_submission, info_response, carrier_quote, carrier_decline, carrier_pending, quote_comparison, followup_inquiry, renewal, internal_routing, misdirected, noise
- `operating_mode`, `intake_channel`
- `situation_summary` — human-readable interpretation
- `data_completeness` — 0.0 to 1.0
- `fields_present` / `fields_missing` — checked against LOB config required_fields and ALL sources
- `data_sources` — maps each field to value + source + confidence
- `fields_conflicting` — fields where sources disagree
- `recommended_stage` + `ball_holder`
- `next_action` — 11 values: send_info_request, route_to_uw, forward_quote, extract_attachments, notify_decline, remarket, relay_to_carrier, send_status_update, monitor, close, none
- `draft_appropriate` (bool) + `draft_type`
- `confidence` — min of 5 factors (classification, completeness, conflicts, pattern, extraction)
- `needs_review` — true if confidence < 0.7

If confidence >= 0.7 and recommended_stage is set, auto-advances the submission stage and adds to stage_history.

**Status after:** `"assessed"`

### Step 5: Draft Generator (conditional)

**Only runs if** `should_generate_draft()` returns true:
1. Submission has a `latest_assessment_id`
2. That assessment has `draft_appropriate: true`
3. The `draft_type` is in `ENABLED_DRAFT_TYPES` = {"info_request", "quote_forward", "decline_notification"}

**Skill:** `src/gic_email_intel/agent/skills/draft_generator.md`
**Tools:** `get_email`, `list_emails`, `get_submission`, `get_assessment`, `save_draft`

Reads the assessment for context (missing fields, reasoning), reads emails for tone. Generates an email draft and saves to `drafts` collection with status `"suggested"`.

**Disabled draft types** (guarded at multiple layers):
- `status_update` — no management system API access. **Enable when:** Unisoft/Jeremiah connected.
- `followup` — no outbound email tracking. **Enable when:** sent folder access available.
- `remarket_suggestion` — no carrier appetite data. **Enable when:** carrier appetite configured per LOB.

**Status after:** `"complete"` (or `"failed"` on error)

### Processing Status Flow

```
pending → classified → linked → extracted → assessed → complete
                                                      → failed (on any error)
```

## Phase 3: API Serving (MongoDB → Frontend)

**Entry point:** `src/gic_email_intel/api/main.py`

FastAPI serves both the REST API (under `/api/`) and the static React frontend (from `ui/dist/` if it exists).

**Auth:** Bearer token in `Authorization` header or `?token=` query param. Single shared secret (`API_TOKEN` env var) — not per-user.

**Key endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check (no auth) — DB status, sync status, pending count |
| GET | `/api/submissions` | Board view — all submissions by 8 stages, paginated, newest first |
| GET | `/api/submissions/{id}` | Detail — emails, extractions, drafts, assessment, completeness, LOB requirements |
| GET | `/api/submissions/search?q=` | Search by ref#, GIC#, insured name, agent, LOB |
| GET | `/api/submissions/history` | Resolved submissions |
| POST | `/api/lookup-email` | Outlook Add-in — 5-step matching waterfall |
| POST | `/api/submissions/{id}/stage` | Manual stage update |
| POST | `/api/submissions/{id}/resolve` | Mark as resolved |
| GET | `/api/assessments/{id}` | Get assessment document |
| PATCH | `/api/drafts/{id}` | Update draft status/body |
| GET | `/api/emails/{id}` | Full email + thread parsing |
| GET | `/api/emails/{id}/attachments/{name}` | Download attachment (presigned S3 URL) |
| GET | `/api/stats` | Notification counts |
| WS | `/api/ws` | Real-time updates via MongoDB change streams |

**WebSocket events:** `new_email`, `classification_complete`, `stage_change`, `new_draft`, `stats_update`, `sync_status`. All driven by MongoDB change streams on emails, submissions, drafts, and sync_state collections.

**CORS:** Configured for localhost:5173, localhost:3000, gic.indemn.ai, Vercel add-in domains, cloudflare tunnel.

## Phase 4: Frontend

**React 19 + TypeScript + Vite + TanStack Query + Tailwind CSS**

Three tabs: Submissions (queue), Overview (demo narrative), Insights (merged analytics + system).

**API integration:** Axios with Bearer token interceptor. Token from URL `?token=` param stored in sessionStorage. TanStack Query auto-refreshes every 30 seconds. WebSocket for real-time push.

**Navigation:** useState-based (no React Router). No shareable URLs. Browser back doesn't work.

**Indemn design system:** Barlow font, CSS custom properties for colors/spacing/shadows, GIC logo + "Powered by Indemn" chrome bar.

## Phase 5: Docker / Deployment

**Dockerfile:** Multi-stage build:
1. `frontend-builder` — Node 22, builds React app → `ui/dist/`
2. `python-builder` — Python 3.12, installs deps via `uv sync`
3. `runtime` — Python 3.12 slim, supervisord, runs as unprivileged user (10001)

**Supervisord** manages three processes in one container:
1. **api** — `uvicorn` on port 8080 (auto-restart)
2. **sync** — Bash loop: `outlook-inbox sync; sleep $SYNC_INTERVAL_SECONDS` (every 60s)
3. **agent** — Bash loop: `outlook-agent process --batch; sleep $SYNC_INTERVAL_SECONDS` (every 60s)

**Health check:** `curl -f http://localhost:8080/api/health`

## Configuration (Environment Variables)

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONGODB_URI` | mongodb://localhost:27017 | MongoDB Atlas connection |
| `MONGODB_DATABASE` | gic_email_intelligence | Database name |
| `GRAPH_TENANT_ID` | (required) | Azure AD tenant for Graph API |
| `GRAPH_CLIENT_ID` | (required) | Azure app registration ID |
| `GRAPH_CLIENT_SECRET` | (required) | Azure app secret |
| `GRAPH_USER_EMAIL` | quote@gicunderwriters.com | Mailbox to sync |
| `LLM_PROVIDER` | anthropic | LLM provider |
| `LLM_API_KEY` | (required) | Anthropic API key |
| `LLM_MODEL` | claude-sonnet-4-6 | Default model |
| `S3_BUCKET` | indemn-gic-attachments | S3 bucket for attachments |
| `AWS_REGION` | us-east-1 | AWS region |
| `API_TOKEN` | (required) | Shared auth token |
| `API_PORT` | 8080 | Server port |
| `SYNC_INTERVAL_SECONDS` | 60 | Polling interval |
| `LOG_LEVEL` | info | Python logging level |

## MongoDB Collections

| Collection | ~Records | Purpose |
|-----------|----------|---------|
| emails | 3,469 | Every email from quote@ inbox |
| submissions | 2,894 | Insurance submissions (central entity) |
| extractions | 330 | Structured data from PDFs |
| assessments | 2,894 | Situation interpretations |
| drafts | 105 | Suggested email replies |
| carriers | 3 | USLI, Hiscox, Granada |
| agents | 55 | Retail agent entities |
| sync_state | 1 | Sync cursor |

## Key Issues for Production

### 1. PDF Extraction Does Not Work in the Agent Pipeline

The `pdf-extractor` skill has no tool to download PDFs from S3 and present them to the LLM. It can only see attachment filenames and email text. The agent produces guesses, not real extractions. All quality extractions came from batch scripts or Claude Code subagents that operated outside the agent framework.

**Fix needed:** Either add a `download_pdf` tool that fetches from S3 and returns content for vision, or replace the agent-based extraction with a direct programmatic step (download PDF → Claude vision API call → structured output → save).

### 2. Pipeline Order: Extraction Should Come Before Classification

Classification accuracy depends on PDF content. Many emails (especially agent submissions) are just "see attached" with the real information in PDFs. Classifying before extraction means the classifier works blind on these emails.

**Proposed reorder:** sync → extract → classify (with extraction context) → link → [assess/draft disabled]

### 3. Assessment and Draft Stages Should Be Disabled for Production

Post-demo feedback: auto-reply/draft functionality was less impactful. Ball-holder tracking isn't useful without complete information. Keep in codebase but don't spend compute. These stages should be configurable (off by default, enabled via env var or config).

### 4. Auth Is a Single Shared Token

Production needs per-user auth. The Observatory uses JWT with demo/full modes. GIC Email Intelligence should integrate with the same auth system.

### 5. Supervisord Loops vs Railway Cron

Railway has native cron jobs. The supervisord bash-loop pattern should be replaced with Railway's cron for sync and agent processing. The API stays as the main process.
