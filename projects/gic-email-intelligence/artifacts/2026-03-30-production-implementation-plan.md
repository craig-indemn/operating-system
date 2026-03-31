# GIC Email Intelligence — Production Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move GIC Email Intelligence from localhost to production — fix the extraction pipeline, deploy to Railway + Amplify, add auth, process historical data.

**Architecture:** Railway (3 services: API + sync cron + processing cron), AWS Amplify (frontend at `gic.indemn.ai`), shared JWT auth with Observatory/copilot-server, MongoDB Atlas (dev + prod clusters).

**Tech Stack:** Python 3.12, FastAPI, LangChain (structured output + multimodal), React 19 + Vite + Tailwind, Railway, AWS Amplify, MongoDB Atlas, S3, PyJWT.

**Design doc:** `projects/gic-email-intelligence/artifacts/2026-03-30-production-deployment-plan.md`
**Pipeline review:** `projects/gic-email-intelligence/artifacts/2026-03-30-pipeline-architecture-review.md`

---

## Parallelization Map

```
Track A (Pipeline Fix)          Track B (Infrastructure)         Track C (Auth)
========================        =========================        ========================
Task 1: Extraction module       Task 6: Railway setup
Task 2: Pipeline reorder        Task 7: Amplify setup
Task 3: Disable assess/draft    Task 8: DNS setup
Task 4: Classifier update
Task 5: Local pipeline test     ─── must complete before ───>    Task 9: Auth backend
                                                                  Task 10: Auth frontend
                                                                  Task 11: Observatory link

                        ─── All tracks merge ───>

Track D (Production)
========================
Task 12: Dockerfile for Railway
Task 13: Deploy to dev
Task 14: Dev pipeline test
Task 15: Deploy to prod
Task 16: Clean slate migration
Task 17: Historical backfill
Task 18: Verify & go live
```

Tracks A and B can run in parallel. Track C depends on Track B (needs deployed backend to test against). Track D depends on all three.

---

## Track A: Pipeline Fix

### Task 1: Build the extraction module

**Files:**
- Create: `src/gic_email_intel/agent/extractor.py`
- Modify: `pyproject.toml:19` (bump langchain-anthropic version)
- Test: `tests/test_extractor.py`

**Step 1: Bump langchain-anthropic dependency**

In `pyproject.toml`, change:
```
    "langchain-anthropic>=0.3",
```
to:
```
    "langchain-anthropic>=1.1.0",
```

Then run:
```bash
cd /Users/home/Repositories/gic-email-intelligence && uv sync
```
Expected: resolves successfully, installs langchain-anthropic 1.1.0+

**Step 2: Write the extraction module**

Create `src/gic_email_intel/agent/extractor.py`:

```python
"""Structured extraction from email attachments.

Downloads attachments from S3, sends them to Claude as multimodal content blocks,
and gets back structured extraction data via constrained decoding.

This replaces the broken ReAct-based pdf-extractor skill which could not
actually see PDF content (it only had access to attachment metadata).
"""

import base64
import json
import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from gic_email_intel.config import settings
from gic_email_intel.core.db import get_sync_db, EMAILS, EXTRACTIONS
from gic_email_intel.core.s3_client import download_attachment

logger = logging.getLogger(__name__)

# Supported MIME types for multimodal content blocks
PDF_TYPES = {"application/pdf"}
IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# Max payload ~30MB to stay under 32MB API limit with base64 overhead
MAX_PAYLOAD_BYTES = 30 * 1024 * 1024


class AttachmentExtraction(BaseModel):
    """Extraction result for a single attachment."""
    attachment_name: str = Field(description="Original filename of the attachment")
    document_type: str = Field(description="What kind of document this is, e.g. quote_letter, application, loss_run, acord_form, drivers_license, cancellation_notice, binder, invoice, portal_screenshot, unknown")
    summary: str = Field(description="Brief description of what this document contains and its purpose")
    extracted_fields: dict[str, Any] = Field(description="All relevant data extracted from the document as key-value pairs. Extract whatever is present — names, dates, amounts, addresses, reference numbers, policy details, vehicle info, business details, etc.")
    reference_numbers: list[str] = Field(description="Any reference numbers, policy numbers, quote numbers, or tracking IDs found in the document")


class EmailExtraction(BaseModel):
    """Extraction result for all attachments on an email."""
    attachments: list[AttachmentExtraction] = Field(description="Extraction results for each processable attachment")
    email_summary: str = Field(description="Brief summary of the email content and what the attachments represent together")


def _build_content_blocks(email: dict) -> tuple[list[dict], int]:
    """Download attachments from S3 and build multimodal content blocks.

    Returns (content_blocks, total_bytes). Skips attachments that are too large
    or have unsupported types.
    """
    blocks = []
    total_bytes = 0

    # Start with email text context
    subject = email.get("subject", "No subject")
    body = email.get("body_text", "")
    sender = email.get("from_address", "")
    sender_name = email.get("from_name", "")

    text_context = f"Email from: {sender_name} <{sender}>\nSubject: {subject}\n\nBody:\n{body[:3000]}"
    blocks.append({"type": "text", "text": text_context})

    for att in email.get("attachments", []):
        storage_path = att.get("storage_path", "")
        if not storage_path:
            continue

        content_type = att.get("content_type", "").lower()
        name = att.get("name", "unknown")

        # Determine if we can process this attachment
        is_pdf = content_type in PDF_TYPES or name.lower().endswith(".pdf")
        is_image = content_type in IMAGE_TYPES

        if not is_pdf and not is_image:
            logger.debug(f"Skipping unsupported attachment type: {name} ({content_type})")
            continue

        try:
            content = download_attachment(storage_path)
        except Exception as e:
            logger.warning(f"Failed to download {name} from S3: {e}")
            continue

        # Check payload size
        if total_bytes + len(content) > MAX_PAYLOAD_BYTES:
            logger.warning(f"Skipping {name} — would exceed payload limit ({total_bytes + len(content)} bytes)")
            continue

        total_bytes += len(content)
        encoded = base64.standard_b64encode(content).decode("utf-8")

        # Add label
        blocks.append({"type": "text", "text": f"\n--- Attachment: {name} ---"})

        if is_pdf:
            blocks.append({
                "type": "file",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": encoded,
                },
            })
        elif is_image:
            mime = content_type if content_type in IMAGE_TYPES else "image/jpeg"
            blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime,
                    "data": encoded,
                },
            })

    # Add final instruction
    blocks.append({
        "type": "text",
        "text": "\nExtract all relevant structured data from each attachment. Be thorough — extract every piece of useful information you can find. Do not guess or fabricate data that isn't present.",
    })

    return blocks, total_bytes


def extract_email_attachments(
    email_id: str,
    model_override: str | None = None,
) -> dict | None:
    """Extract structured data from all attachments on an email.

    Downloads PDFs and images from S3, sends them to Claude as multimodal
    content blocks, and saves structured extraction results.

    Args:
        email_id: The email document ID.
        model_override: Override the LLM model.

    Returns:
        Dict with extraction results, or None if no extractable attachments.
    """
    db = get_sync_db()
    email = db[EMAILS].find_one({"_id": ObjectId(email_id)})
    if not email:
        logger.error(f"Email not found: {email_id}")
        return None

    # Check for extractable attachments
    has_extractable = any(
        att.get("storage_path") and (
            att.get("content_type", "").lower() in PDF_TYPES | IMAGE_TYPES
            or att.get("name", "").lower().endswith(".pdf")
        )
        for att in email.get("attachments", [])
    )

    if not has_extractable:
        return None

    # Build multimodal content blocks
    content_blocks, total_bytes = _build_content_blocks(email)

    # Only the text context block means no attachments were downloadable
    if len(content_blocks) <= 2:  # text context + final instruction only
        logger.warning(f"No attachments could be downloaded for email {email_id}")
        return None

    logger.info(f"Extracting from email {email_id}: {total_bytes / 1024:.0f}KB in attachments")

    # Create LLM with structured output
    model = model_override or settings.llm_model
    llm = ChatAnthropic(
        model=model,
        api_key=settings.llm_api_key,
        temperature=0,
        max_tokens=8192,
    )
    structured_llm = llm.with_structured_output(EmailExtraction, method="json_schema")

    # Single LLM call with all attachments
    message = HumanMessage(content=content_blocks)
    result: EmailExtraction = structured_llm.invoke([message])

    # Save extractions to MongoDB
    now = datetime.now(timezone.utc)
    extraction_ids = []

    for att_extraction in result.attachments:
        doc = {
            "email_id": ObjectId(email_id),
            "submission_id": email.get("submission_id"),
            "source_attachment_name": att_extraction.attachment_name,
            "pdf_document_type": att_extraction.document_type,
            "summary": att_extraction.summary,
            "extracted_fields": att_extraction.extracted_fields,
            "reference_numbers": att_extraction.reference_numbers,
            # Flatten common fields from extracted_fields for backward compatibility
            "named_insured": att_extraction.extracted_fields.get("named_insured"),
            "carrier": att_extraction.extracted_fields.get("carrier"),
            "premium": att_extraction.extracted_fields.get("premium"),
            "coverage_limits": att_extraction.extracted_fields.get("coverage_limits"),
            "effective_date": att_extraction.extracted_fields.get("effective_date"),
            "retail_agent_name": att_extraction.extracted_fields.get("retail_agent_name"),
            "retail_agency_name": att_extraction.extracted_fields.get("retail_agency_name"),
            "key_details": {
                k: v for k, v in att_extraction.extracted_fields.items()
                if k not in {
                    "named_insured", "carrier", "premium", "coverage_limits",
                    "effective_date", "retail_agent_name", "retail_agency_name",
                }
            },
            "extracted_at": now,
            "created_at": now,
        }
        insert_result = db[EXTRACTIONS].insert_one(doc)
        extraction_ids.append(str(insert_result.inserted_id))

    return {
        "email_id": email_id,
        "extraction_count": len(extraction_ids),
        "extraction_ids": extraction_ids,
        "email_summary": result.email_summary,
    }
```

**Step 3: Run to verify it compiles**

```bash
cd /Users/home/Repositories/gic-email-intelligence && uv run python -c "from gic_email_intel.agent.extractor import extract_email_attachments; print('OK')"
```
Expected: `OK` (imports successfully)

**Step 4: Commit**

```bash
git add src/gic_email_intel/agent/extractor.py pyproject.toml
git commit -m "feat: structured output extraction module — replaces broken ReAct extractor"
```

---

### Task 2: Reorder pipeline in harness

**Files:**
- Modify: `src/gic_email_intel/agent/harness.py:100-212`
- Modify: `src/gic_email_intel/config.py`

**Step 1: Add PIPELINE_STAGES config**

In `src/gic_email_intel/config.py`, add to the Settings class:

```python
    # Pipeline
    pipeline_stages: str = "extract,classify,link"  # comma-separated, options: extract,classify,link,assess,draft
```

**Step 2: Rewrite process_email in harness.py**

Replace the `process_email` function to:
1. Run extract FIRST (using new structured output module)
2. Run classify SECOND (with extraction context available)
3. Run link THIRD
4. Conditionally run assess and draft only if in `pipeline_stages`

The key changes:
- Import and call `extract_email_attachments` from the new module instead of running the pdf-extractor skill
- Move extraction before classification
- Gate assess/draft on `settings.pipeline_stages`
- Update the classifier's user message to mention extraction data is available

**Step 3: Update classifier context in harness.py**

In `format_context()`, update the email-classifier message to tell the agent that extraction data may be available:

```python
    if skill_name == "email-classifier":
        return (
            f"Classify email {context['email_id']}. "
            "Read it with the get_email tool. Check for any extractions with "
            "list_extractions if the email has a submission_id — extraction data "
            "from PDFs may help you classify more accurately. Then save the classification."
        )
```

Update `SKILL_TOOL_MAP` to give the classifier access to `list_extractions`:

```python
    "email-classifier": [get_email, list_extractions, save_classification],
```

**Step 4: Test the pipeline order change compiles**

```bash
cd /Users/home/Repositories/gic-email-intelligence && uv run python -c "from gic_email_intel.agent.harness import process_email; print('OK')"
```

**Step 5: Commit**

```bash
git add src/gic_email_intel/agent/harness.py src/gic_email_intel/config.py
git commit -m "feat: reorder pipeline to extract→classify→link, disable assess/draft via config"
```

---

### Task 3: Update classifier skill to use extraction context

**Files:**
- Modify: `src/gic_email_intel/agent/skills/email_classifier.md`

**Step 1: Add extraction-aware instructions to the classifier**

Add a new section after the "## Instructions" section:

```markdown
## Using Extraction Data

If the email has been linked to a submission (has submission_id), check for extractions:
1. Call `list_extractions(submission_id)` to see if any PDF extractions exist
2. If extractions exist, use them to inform your classification:
   - Document types tell you what kind of email this is (a quote_letter means carrier_quote, an application means agent_submission)
   - Extracted fields like carrier name, premium, reference numbers help confirm the LOB and email type
   - This is especially important for emails with vague subjects like "see attached"
3. If no extractions exist, classify based on email text and attachment filenames as before
```

**Step 2: Commit**

```bash
git add src/gic_email_intel/agent/skills/email_classifier.md
git commit -m "feat: classifier skill uses extraction data for better accuracy"
```

---

### Task 4: Add clean slate migration script

**Files:**
- Create: `scripts/clean_slate.py`

**Step 1: Write the migration script**

```python
"""Clean slate migration — delete derived data for a date range, re-process from raw emails.

Usage:
    uv run python scripts/clean_slate.py --since 2025-10-01 --dry-run
    uv run python scripts/clean_slate.py --since 2025-10-01 --execute
"""
import argparse
from datetime import datetime, timezone

from gic_email_intel.core.db import get_sync_db, EMAILS, SUBMISSIONS, EXTRACTIONS, ASSESSMENTS, DRAFTS


def clean_slate(since: str, dry_run: bool = True):
    db = get_sync_db()
    since_dt = datetime.fromisoformat(since).replace(tzinfo=timezone.utc)

    # Find emails in the date range
    email_filter = {"received_at": {"$gte": since_dt}}
    email_count = db[EMAILS].count_documents(email_filter)
    email_ids = [doc["_id"] for doc in db[EMAILS].find(email_filter, {"_id": 1})]

    # Find submissions linked to these emails
    sub_filter = {"_id": {"$in": [
        doc["submission_id"] for doc in db[EMAILS].find(
            {"_id": {"$in": email_ids}, "submission_id": {"$ne": None}},
            {"submission_id": 1}
        )
    ]}}
    sub_ids = [doc["_id"] for doc in db[SUBMISSIONS].find(sub_filter, {"_id": 1})]

    # Count what would be deleted
    extraction_count = db[EXTRACTIONS].count_documents({"email_id": {"$in": email_ids}})
    assessment_count = db[ASSESSMENTS].count_documents({"submission_id": {"$in": sub_ids}})
    draft_count = db[DRAFTS].count_documents({"submission_id": {"$in": sub_ids}})

    print(f"Since: {since}")
    print(f"Emails in range: {email_count}")
    print(f"Submissions to delete: {len(sub_ids)}")
    print(f"Extractions to delete: {extraction_count}")
    print(f"Assessments to delete: {assessment_count}")
    print(f"Drafts to delete: {draft_count}")

    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return

    # Delete derived data
    db[DRAFTS].delete_many({"submission_id": {"$in": sub_ids}})
    db[ASSESSMENTS].delete_many({"submission_id": {"$in": sub_ids}})
    db[EXTRACTIONS].delete_many({"email_id": {"$in": email_ids}})
    db[SUBMISSIONS].delete_many({"_id": {"$in": sub_ids}})

    # Reset emails to pending
    db[EMAILS].update_many(
        {"_id": {"$in": email_ids}},
        {"$set": {
            "processing_status": "pending",
            "classification": None,
            "submission_id": None,
            "processing_error": None,
            "processed_at": None,
            "updated_at": datetime.now(timezone.utc),
        }}
    )

    print(f"\nDeleted {len(sub_ids)} submissions, {extraction_count} extractions, {assessment_count} assessments, {draft_count} drafts")
    print(f"Reset {email_count} emails to pending")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", required=True, help="ISO date (e.g., 2025-10-01)")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    clean_slate(args.since, dry_run=not args.execute)
```

**Step 2: Commit**

```bash
git add scripts/clean_slate.py
git commit -m "feat: clean slate migration script for historical reprocessing"
```

---

### Task 5: Local pipeline test (small sample)

**Step 1: Run clean slate on dev with small sample**

```bash
cd /Users/home/Repositories/gic-email-intelligence
uv run python scripts/clean_slate.py --since 2026-03-01 --dry-run
```

Review the counts. If they look right:

```bash
uv run python scripts/clean_slate.py --since 2026-03-01 --execute
```

**Step 2: Process a small batch**

```bash
uv run outlook-agent process --batch --limit 10
```

**Step 3: Verify results**

Start the API and frontend, open the browser, check:
- Submissions have extractions with real PDF data
- Classification is correct (especially for emails with vague subjects)
- Linking worked properly

```bash
uv run uvicorn gic_email_intel.api.main:app --port 8080 &
cd ui && npm run dev &
open "http://localhost:5173/?token=$API_TOKEN"
```

**Step 4: Commit any fixes**

```bash
git add -A && git commit -m "fix: pipeline adjustments from local testing"
```

---

## Track B: Infrastructure Setup (parallel with Track A)

### Task 6: Railway project setup

**Step 1: Install Railway CLI**

```bash
brew install railway
railway login
railway whoami
```

**Step 2: Create Railway project and link repo**

```bash
cd /Users/home/Repositories/gic-email-intelligence
railway init  # Create new project, name it "gic-email-intelligence"
```

**Step 3: Create railway.json config**

Create `railway.json` in repo root:

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn gic_email_intel.api.main:app --host 0.0.0.0 --port 8080",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

Note: This configures the API service. Sync and processing cron services will be configured via the Railway dashboard (separate services in the same project with different start commands and cron schedules).

**Step 4: Set environment variables for dev**

```bash
railway variable set MONGODB_URI="<dev-atlas-uri>"
railway variable set MONGODB_DATABASE="gic_email_intelligence_dev"
railway variable set GRAPH_TENANT_ID="<value>"
railway variable set GRAPH_CLIENT_ID="<value>"
railway variable set GRAPH_CLIENT_SECRET="<value>"
railway variable set GRAPH_USER_EMAIL="quote@gicunderwriters.com"
railway variable set LLM_PROVIDER="anthropic"
railway variable set LLM_API_KEY="<value>"
railway variable set LLM_MODEL="claude-sonnet-4-6"
railway variable set S3_BUCKET="indemn-gic-attachments"
railway variable set AWS_REGION="us-east-1"
railway variable set AWS_ACCESS_KEY_ID="<value>"
railway variable set AWS_SECRET_ACCESS_KEY="<value>"
railway variable set API_TOKEN="<dev-token>"
railway variable set SYNC_INTERVAL_SECONDS="300"
railway variable set PIPELINE_STAGES="extract,classify,link"
railway variable set LOG_LEVEL="info"
```

Note: Auth-related vars (JWT_SECRET, COPILOT_SERVER_URL, TILEDESK_DB_URI) added in Task 9.

**Step 5: Create sync and processing cron services**

Via Railway dashboard (or CLI):
- Add service "sync" — same repo, start command: `outlook-inbox sync`, cron schedule: `*/5 * * * *`
- Add service "processing" — same repo, start command: `outlook-agent process --batch`, cron schedule: `*/5 * * * *`

**Step 6: Commit railway.json**

```bash
git add railway.json
git commit -m "infra: add Railway config-as-code"
```

---

### Task 7: Update Dockerfile for Railway

**Files:**
- Modify: `Dockerfile`
- Delete: `supervisord.conf` (no longer needed)

**Step 1: Update Dockerfile to single-process**

Replace the existing Dockerfile with a version that doesn't use supervisord:

```dockerfile
# ---- Node stage: build React frontend ----
FROM node:22-slim AS frontend-builder
WORKDIR /app/ui
COPY ui/package.json ui/package-lock.json ./
RUN npm ci
COPY ui/ .
RUN npm run build

# ---- Python stage: install deps ----
FROM python:3.12-slim AS python-builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock* ./
COPY src/ src/
RUN uv sync --frozen --no-dev || uv sync --no-dev

# ---- Runtime stage ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app

# Install curl for health checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python env and code
COPY --from=python-builder /app /app

# Copy built frontend into static serving location
COPY --from=frontend-builder /app/ui/dist /app/ui/dist

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Don't run as root
RUN useradd -u 10001 -m appuser
RUN chown -R 10001:10001 /app
USER 10001

# Default: run the API. Railway overrides this per service.
CMD ["uvicorn", "gic_email_intel.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Step 2: Commit**

```bash
git rm supervisord.conf
git add Dockerfile
git commit -m "infra: single-process Dockerfile for Railway (remove supervisord)"
```

---

### Task 8: Amplify setup + DNS

**Step 1: Create amplify.yml in repo root**

```yaml
version: 1
applications:
  - appRoot: ui
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: dist
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
```

**Step 2: Create Amplify app via AWS CLI**

```bash
aws amplify create-app \
  --name "gic-email-intelligence" \
  --repository "https://github.com/<owner>/gic-email-intelligence" \
  --platform WEB \
  --environment-variables VITE_API_BASE=https://api-dev.gic.indemn.ai
```

Connect the `main` branch for dev:
```bash
aws amplify create-branch --app-id <APP_ID> --branch-name main
```

Connect the `prod` branch for production:
```bash
aws amplify create-branch --app-id <APP_ID> --branch-name prod \
  --environment-variables VITE_API_BASE=https://api.gic.indemn.ai
```

**Step 3: Add custom domain in Route 53**

```bash
aws amplify create-domain-association \
  --app-id <APP_ID> \
  --domain-name indemn.ai \
  --sub-domain-settings \
    prefix=gic,branchName=prod \
    prefix=dev.gic,branchName=main
```

**Step 4: Add SPA rewrite rule**

Via Amplify console or CLI, add redirect rule:
- Source: `/<*>`
- Target: `/index.html`
- Status: `404-200`

**Step 5: Set up Railway custom domains**

In Railway dashboard:
- API service (prod): add custom domain `api.gic.indemn.ai`
- API service (dev): add custom domain `api-dev.gic.indemn.ai`

Configure CNAME records in Route 53 pointing to Railway's provided domains.

**Step 6: Commit amplify.yml**

```bash
git add amplify.yml
git commit -m "infra: add Amplify build config"
```

---

## Track C: Auth

### Task 9: Backend auth module

**Files:**
- Rewrite: `src/gic_email_intel/api/auth.py`
- Modify: `src/gic_email_intel/config.py`
- Modify: `src/gic_email_intel/api/main.py`
- Create: `src/gic_email_intel/api/routes/auth.py`

**Step 1: Add auth config to Settings**

In `src/gic_email_intel/config.py`, add:

```python
    # Auth
    jwt_secret: str = ""  # Same as copilot-server, for JWT validation
    copilot_server_url: str = ""  # For proxying signin requests
    tiledesk_db_uri: str = ""  # For org membership lookup
    gic_org_id: str = "65eb3f19e5e6de0013fda310"
```

**Step 2: Rewrite auth.py with JWT validation**

Replace `src/gic_email_intel/api/auth.py` with a module that:
- Decodes JWTs using `jwt_secret` (HS256, no exp verification — copilot tokens don't have exp)
- Checks if user email is `@indemn.ai` → full access
- If not, queries `tiledesk.project_users` for GIC org membership
- Falls back to `API_TOKEN` check for internal/CLI use
- Returns a `CurrentUser` dataclass with `user_id`, `email`, `is_admin`

Reference: Observatory's `src/observatory/api/auth.py` (lines 56-452) for the exact JWT format and validation logic.

Add `PyJWT` to dependencies in `pyproject.toml`:
```
    "PyJWT>=2.8",
```

**Step 3: Create auth routes**

Create `src/gic_email_intel/api/routes/auth.py` with:
- `GET /api/auth/status` → returns auth mode
- `GET /api/auth/me` → returns current user info
- `POST /api/auth/signin` → proxies to copilot-server `/auth/signin`

Reference: Observatory's `src/observatory/api/routers/auth.py` for the signin proxy pattern.

**Step 4: Register auth routes in main.py**

Add to `src/gic_email_intel/api/main.py`:
```python
from gic_email_intel.api.routes import auth
app.include_router(auth.router, prefix="/api")
```

**Step 5: Update CORS origins in main.py**

Update the `allow_origins` list to include the production domains:
```python
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://gic.indemn.ai",
        "https://dev.gic.indemn.ai",
    ],
```

**Step 6: Test auth locally**

```bash
cd /Users/home/Repositories/gic-email-intelligence
uv run python -c "from gic_email_intel.api.auth import verify_token; print('OK')"
```

**Step 7: Commit**

```bash
git add src/gic_email_intel/api/auth.py src/gic_email_intel/api/routes/auth.py src/gic_email_intel/config.py src/gic_email_intel/api/main.py pyproject.toml
git commit -m "feat: JWT auth module — copilot-server integration, GIC org scoping"
```

---

### Task 10: Frontend login page + auth flow

**Files:**
- Create: `ui/src/pages/Login.tsx`
- Modify: `ui/src/api/client.ts`
- Modify: `ui/src/App.tsx`

**Step 1: Update API client for JWT auth**

Replace `ui/src/api/client.ts` to:
- Check for token in URL param → store in localStorage (not sessionStorage)
- Strip token from URL after capturing
- Check `localStorage.getItem('jwt_token')` for existing session
- Add auth interceptor
- Add 401 response interceptor → redirect to login
- Export `getToken()`, `setToken()`, `clearToken()`, `isAuthenticated()` helpers

**Step 2: Create Login page**

Create `ui/src/pages/Login.tsx`:
- Email + password form with Indemn design system styling
- Calls `POST /api/auth/signin`
- On success: stores JWT in localStorage, navigates to main app
- Error handling for invalid credentials
- GIC logo + "Email Intelligence" branding

**Step 3: Add auth gating to App.tsx**

Wrap the app in an auth check:
- On load, call `GET /api/auth/me` to validate existing token
- If valid → show the app
- If no token or invalid → show Login page
- Add logout button to chrome bar

**Step 4: Test login flow locally**

Start backend with `JWT_SECRET` and `COPILOT_SERVER_URL` configured, verify:
- Login page renders
- Signin works with valid credentials
- Invalid credentials show error
- Authenticated state persists across refresh
- 401 redirects to login

**Step 5: Commit**

```bash
git add ui/src/pages/Login.tsx ui/src/api/client.ts ui/src/App.tsx
git commit -m "feat: login page + JWT auth flow in frontend"
```

---

### Task 11: Observatory navigation link

**Files:**
- Modify: `/Users/home/Repositories/indemn-observability/frontend/src/components/layout/Header.tsx`

**Step 1: Add "Email Intelligence" link to Observatory header**

Add a button/link in the Observatory header that navigates to:
```
https://gic.indemn.ai/?token=${localStorage.getItem('token')}
```

Use Lucide `Mail` icon. Place it near the existing controls (mode toggle, help, export).

**Step 2: Commit to Observatory repo**

```bash
cd /Users/home/Repositories/indemn-observability
git add frontend/src/components/layout/Header.tsx
git commit -m "feat: add Email Intelligence link for GIC"
```

---

## Track D: Production

### Task 12: Frontend UI simplification

**Files:**
- Modify: `ui/src/pages/RiskRecord.tsx`
- Modify: `ui/src/pages/SubmissionQueue.tsx`

**Step 1: Hide disabled features**

Since assess/draft stages are disabled:
- Hide draft cards section in RiskRecord (conditionally — only show if drafts exist)
- Hide ball-holder indicators (the data won't be populated)
- Hide assessment summary section (conditionally)
- Keep: email content, extracted data display, LOB requirements, timeline

These should be conditional checks (if data exists, show it) rather than hard removal — so when assess/draft are re-enabled, the UI automatically shows them again.

**Step 2: Commit**

```bash
git add ui/src/pages/RiskRecord.tsx ui/src/pages/SubmissionQueue.tsx
git commit -m "feat: hide disabled features (drafts, assessment, ball-holder) when data absent"
```

---

### Task 13: Deploy to dev

**Step 1: Push to main branch**

```bash
cd /Users/home/Repositories/gic-email-intelligence
git push origin main
```

**Step 2: Verify Railway dev deployment**

```bash
railway logs -f  # Watch build + deploy
```

Then test:
```bash
curl https://api-dev.gic.indemn.ai/api/health
```

**Step 3: Verify Amplify dev deployment**

Check Amplify console for build status. Then open:
```
https://dev.gic.indemn.ai
```

**Step 4: Test end-to-end in dev**

- Login page works
- Submissions load
- Click into a submission → see extracted data
- Sync cron running (check Railway logs)
- Processing cron running

---

### Task 14: Create prod branch and deploy

**Step 1: Create prod branch**

```bash
cd /Users/home/Repositories/gic-email-intelligence
git checkout -b prod
git push origin prod
```

**Step 2: Configure Railway prod environment**

```bash
railway environment  # Switch to production
railway variable set MONGODB_URI="<prod-atlas-uri>"
railway variable set MONGODB_DATABASE="gic_email_intelligence"
# ... set all prod env vars (pull from AWS Secrets Manager / Parameter Store)
```

**Step 3: Verify prod deployment**

```bash
curl https://api.gic.indemn.ai/api/health
open https://gic.indemn.ai
```

---

### Task 15: Run clean slate + backfill in prod

**Step 1: Run clean slate**

```bash
MONGODB_URI=<prod-uri> uv run python scripts/clean_slate.py --since 2025-10-01 --dry-run
```

Review counts. Then execute:

```bash
MONGODB_URI=<prod-uri> uv run python scripts/clean_slate.py --since 2025-10-01 --execute
```

**Step 2: Run backfill in small batches**

```bash
MONGODB_URI=<prod-uri> uv run outlook-agent process --batch --limit 50
```

Verify results look good. Then run full:

```bash
MONGODB_URI=<prod-uri> uv run outlook-agent process --batch
```

**Step 3: Verify in UI**

Open `https://gic.indemn.ai`, log in, verify:
- Submissions have real extracted data
- Classification is accurate
- 6 months of data present

---

### Task 16: Final verification

**Step 1: Verify all Definition of Done criteria**

- [ ] Backend on Railway — API healthy, sync cron running, processing cron running
- [ ] Frontend on Amplify — `gic.indemn.ai` loads, `dev.gic.indemn.ai` loads
- [ ] Auth — JC can log in, Indemn employees can log in, unauthorized users rejected
- [ ] Observatory link — click-through works with token passthrough
- [ ] Pipeline — extract → classify → link producing accurate data
- [ ] 6 months clean data — historical backfill complete, spot-checks pass
- [ ] Email sync live — new emails processed within 5-10 minutes

**Step 2: Notify JC**

Once all checks pass, JC can start using the system.
