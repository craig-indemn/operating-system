---
ask: "Complete end-to-end walkthrough of the email-to-AMS pipeline — every step, every file, every data flow — for production readiness review"
created: 2026-04-22
workstream: gic-email-intelligence
session: 2026-04-22a
sources:
  - type: codebase
    description: "Full read of harness.py, agent.py, extractor.py, email_classifier.md, create-quote-id.md, sync.py, emails.py, submissions.py, automate.py, cli.py"
---

# Production Process Walkthrough — 2026-04-22

## The Full Process: Email → Unisoft AMS (End-to-End)

### Phase 1: Email Sync (`src/gic_email_intel/cli/commands/sync.py`)

**Trigger:** Railway cron every 5 min (currently running)

1. `GraphClient` connects to Microsoft Graph API using client credentials (tenant + app ID + secret)
2. Queries `quote@gicunderwriters.com` for messages since last sync timestamp
3. For each new email:
   - Dedups by `graph_message_id`
   - Captures: subject, from, to, cc, body (HTML→text extraction), folder, received_at
   - Downloads attachments → uploads to S3 (`indemn-gic-attachments` bucket)
   - Inserts into MongoDB `emails` collection with `processing_status: "pending"`
4. Updates `sync_state` with last sync timestamp

**What's in the email doc at this point:** Raw email data, attachment metadata with S3 paths, `processing_status: "pending"`, no classification, no submission link.

---

### Phase 2: Processing Pipeline (`src/gic_email_intel/agent/harness.py`)

**Trigger:** Railway cron (currently PAUSED via `PAUSE_PROCESSING=true`)

For each email with `processing_status: "pending"`, runs in order:

#### Step 2a: Extract (`src/gic_email_intel/agent/extractor.py`)
- Checks if email has PDFs worth extracting (skips carrier responses — USLI/Hiscox)
- Downloads PDFs from S3
- Sends to form-extractor service (LLMWhisperer OCR) → gets raw text
- Falls back to pdfplumber if form-extractor is down
- Sends text to **Gemini 2.5 Flash** with structured output schema → `EmailExtraction`
- Saves to `extractions` collection with `key_details`, `extracted_fields`, etc.
- Sets `processing_status: "extracted"`

#### Step 2b: Classify (`src/gic_email_intel/agent/skills/email_classifier.md` via LangGraph ReAct agent)
- LLM reads the email, checks extractions if available
- Classifies into one of 14 types:
  - `usli_quote`, `usli_pending`, `usli_decline`
  - `agent_submission`, `agent_reply`, `agent_followup`
  - `gic_portal_submission`, `gic_application`, `gic_info_request`, `gic_internal`
  - `hiscox_quote`, `renewal_request`, `report`, `other`
- Identifies LOB, named insured, reference numbers
- **Hard rules enforced AFTER LLM** (`_enforce_classification_rules` in harness.py):
  - Policy numbers in subject → never `agent_submission`
  - Internal GIC senders (bind@, backoffice@, csr@, endorsement@) → `gic_internal`
  - "Request for forms" → `other`
- Sets `processing_status: "classified"`

#### Step 2c: Link (submission-linker skill)
- Links email to an existing submission or creates new one
- Uses reference numbers, insured name, conversation threading
- Sets `processing_status: "linked"`

#### Step 2d: Enrich (`_enrich_submission_from_extractions` in harness.py)
- Fills missing submission fields from extraction data
- Priority: AMS > Extraction > Classification > Email
- Maps varied field names (e.g., `applicant_name` → `named_insured`)
- No LLM calls — just copies existing data

#### Step 2e: Complete
- Sets `processing_status: "complete"`
- Assess and draft stages are disabled (not in `PIPELINE_STAGES` config)

---

### Phase 3: Automation (`src/gic_email_intel/cli/commands/automate.py` → `src/gic_email_intel/automation/agent.py`)

**Trigger:** Railway cron (currently PAUSED via `PAUSE_AUTOMATION=true`), or manual `gic automate run`

1. Counts emails where `processing_status: "complete"` AND `automation_status` is null AND has `submission_id`
2. For each (up to `--max`, default 50):
   - Creates a fresh **Gemini 2.5 Pro deepagent** with `LocalShellBackend`
   - System prompt includes the full `create-quote-id.md` skill inlined
   - Agent invokes with "Process the next email of type 'agent_submission'"

**What the agent does (following the skill in `src/gic_email_intel/automation/skills/create-quote-id.md`):**

3. **Step 1 — Claim:** `gic emails next --type agent_submission --json` atomically claims email (sets `automation_status: "processing"`)
4. **Step 1 — Dup check layer 1:** If `submission.unisoft_quote_id` already set → complete with existing ID, stop
5. **Step 2 — LOB:** Maps classification LOB → 2-char Unisoft code, looks up sub-LOBs via `unisoft lobs sublobs --lob {CODE}`
6. **Step 3 — Agency:** Tries producer code first → `unisoft agents get --number N`, then multi-field fuzzy match → `unisoft agents match --name --phone --city --state --email --compact`
7. **Step 3.5 — Dup check layer 2:** `gic submissions check-duplicate --name "..." --compact` — fuzzy name match against submissions with existing quote IDs
8. **Step 4 — Create Quote:** `unisoft quote create --lob --agent --name ...` → gets back QuoteId. Checks `HasDuplicates` flag (layer 3)
9. **Step 5 — Attachments:** Downloads PDFs from S3 via `gic emails get {ID} --attachment`, uploads to Unisoft via `unisoft attachment upload --quote-id N --file path`
10. **Step 6 — Create Task:** `unisoft task create --quote-id N --group-id G --subject "[Auto] ..."` — currently GroupId 2 (UAT), needs 3/4 for prod
11. **Step 7 — Activity:** `unisoft activity create --quote-id N --action-id 6 --notes "Application received from agent via email automation"`
12. **Step 8 — Complete:** `gic emails complete {ID} --quote-id N --task-id M --notes "LOB=XX, Agent=NNNN"` — denormalizes quote_id, task_id, automation_status onto submission for board visibility

**Failure modes:**
- Can't determine LOB → fail
- Agency not in Unisoft → fail with search details
- Quote creation error → fail
- Task creation fails after Quote created → fail with Quote ID in error (no silent half-success)
- Attachment/activity failures → note but continue (best-effort)

---

## Key Code Files

| Purpose | File |
|---------|------|
| Email sync from Outlook | `src/gic_email_intel/cli/commands/sync.py` |
| Processing pipeline orchestrator | `src/gic_email_intel/agent/harness.py` |
| PDF/document extraction | `src/gic_email_intel/agent/extractor.py` |
| Classifier skill (LLM prompt) | `src/gic_email_intel/agent/skills/email_classifier.md` |
| Submission linker skill | `src/gic_email_intel/agent/skills/submission_linker.md` |
| Submission enrichment | `_enrich_submission_from_extractions()` in harness.py |
| Automation agent (deepagent) | `src/gic_email_intel/automation/agent.py` |
| Automation skill | `src/gic_email_intel/automation/skills/create-quote-id.md` |
| Automation CLI (run loop) | `src/gic_email_intel/cli/commands/automate.py` |
| Email CLI (next, complete, reset) | `src/gic_email_intel/cli/commands/emails.py` |
| Submission CLI (check-duplicate) | `src/gic_email_intel/cli/commands/submissions.py` |
| Unisoft CLI (quote, task, agents) | `unisoft-proxy/client/cli.py` |
| Config/settings | `src/gic_email_intel/config.py` |

---

## UAT vs Production Differences

| Component | UAT | Production |
|-----------|-----|------------|
| Proxy port | 5000 | 5001 |
| Proxy URL | `http://54.83.28.79:5000` | `http://54.83.28.79:5001` |
| API key | `84208b3...` | `prod-84208b3...` |
| SOAP endpoint | `ins-gic-service-uat-app.azurewebsites.net` | `services.gicunderwriters.co` |
| File service | `services.uat.gicunderwriters.co/attachments/insfileservice.svc` | `services.gicunderwriters.co/attachments/insfileservice.svc` |
| ClientId | `GIC_UAT` | `GIC` |
| Desktop login | `ccerto` / `GIC2026$$!` | `indemnai` / `GIC2000undw!` |
| Task groups | GroupId 2 (Indemn Automation - New Biz) | GroupId 3 (NEW BIZ), GroupId 4 (NEW BIZ Workers Comp) |
| Entered-by user | `ccerto` | `indemnai` |
| Agents collection | 1,571 synced from UAT | Needs sync from prod |
| WCF DNS Identity | Not required | Required: `gicunderwriters.co` (auto-detected by proxy) |

---

## Pipeline CLI Reference

```bash
# === SYNC ===
gic sync                              # Incremental sync since last run
gic sync --since 2026-04-22           # Sync from specific date
gic sync --full                       # Full re-sync (all emails)

# === PROCESSING ===
gic process --email {ID}              # Process single email
gic process --batch                   # Process all pending
gic process --batch --since 2026-04-22 --until 2026-04-23  # Date range
gic process --batch --limit 10        # Limit count
gic process --batch --model gemini-2.5-flash  # Override model

# === AUTOMATION ===
gic automate run -t agent_submission --max 1 --verbose  # One email, verbose
gic automate run -t agent_submission --max 5            # Batch of 5
gic automate backfill-ams --dry-run                     # Check linkage gaps

# === EMAIL MANAGEMENT ===
gic emails list --type agent_submission                 # List by type
gic emails get {ID} --json --body                       # Full email details
gic emails next --type agent_submission --json           # Claim next for automation
gic emails complete {ID} --quote-id N --task-id M       # Mark success
gic emails complete {ID} --status failed --error "..."  # Mark failure
gic emails reset {ID}                                   # Reset for reprocessing

# === SUBMISSIONS ===
gic submissions check-duplicate --name "..." --compact  # Dup check
gic submissions search --insured "..." --fuzzy          # Search

# === UNISOFT ===
unisoft lobs list                                       # All LOBs
unisoft lobs sublobs --lob CG                           # Sub-LOBs
unisoft agents match --name "..." --phone "..." --compact  # Fuzzy match
unisoft agents search --name "..."                      # Keyword search
unisoft agents sync                                     # Sync all agents to MongoDB
unisoft quote create --lob CG --agent N --name "..."    # Create quote
unisoft quote get --id N                                # Verify quote
unisoft task create --quote-id N --group-id G --subject "..."  # Create task
unisoft task groups                                     # List task groups
unisoft activity create --quote-id N --action-id 6 --notes "..."  # Log activity
unisoft attachment upload --quote-id N --file path      # Upload PDF

# === ENVIRONMENT ===
# UAT
export UNISOFT_API_KEY=84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de
export UNISOFT_PROXY_URL=http://54.83.28.79:5000

# Prod
export UNISOFT_API_KEY=prod-84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de
export UNISOFT_PROXY_URL=http://54.83.28.79:5001
```

---

## Kill Switches

| Env Var | Effect | Where |
|---------|--------|-------|
| `PAUSE_PROCESSING=true` | Processing cron exits immediately | harness.py line 401 |
| `PAUSE_AUTOMATION=true` | Automation cron exits immediately | automate.py line 52 |
| `PIPELINE_STAGES=extract,classify,link` | Controls which stages run | harness.py `_active_stages()` |

---

## Data Flow Summary

```
Outlook (quote@gicunderwriters.com)
  │
  ▼ [Graph API, every 5 min]
MongoDB: emails (processing_status: pending)
  │
  ▼ [Processing pipeline]
  ├── Extract: PDFs → form-extractor → Gemini Flash → extractions collection
  ├── Classify: email → Gemini Flash ReAct → classification on email doc
  ├── Link: email → submission (create or match)
  └── Enrich: extraction fields → submission fields
  │
  ▼ [processing_status: complete, automation_status: null]
Automation Agent (Gemini 2.5 Pro deepagent)
  │
  ├── Claim email (atomic find-and-update)
  ├── Dup check layers 1+2 (submission check + cross-submission fuzzy)
  ├── LOB mapping + Sub-LOB lookup
  ├── Agency matching (producer code → fuzzy multi-field → live search)
  ├── Create Quote in Unisoft
  ├── Dup check layer 3 (Unisoft HasDuplicates)
  ├── Upload attachments to Unisoft
  ├── Create Task for underwriting team
  ├── Log activity
  └── Record result (denormalize to submission)
  │
  ▼
Unisoft AMS: Quote + Task in NEW BIZ queue
  │
  ▼ [Human]
GIC underwriting team picks up task, reviews, submits to carrier
```
