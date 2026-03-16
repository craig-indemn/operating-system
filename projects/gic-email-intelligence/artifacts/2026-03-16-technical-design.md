---
ask: "Comprehensive technical design for the GIC email intelligence system — every detail thought through, validated against actual data, ready for implementation"
created: 2026-03-16
workstream: gic-email-intelligence
session: 2026-03-16-a
sources:
  - type: conversation
    description: "Multi-session design process — data extraction, UI brainstorming, technical architecture, agent harness design"
  - type: email-data
    description: "3,165 classified emails, 280 PDF vision extractions, 5,888 attachments from quote@gicunderwriters.com"
  - type: microsoft-graph
    description: "Live inbox analysis — folder structure, threading patterns, reference number formats, email type distribution"
---

# GIC Email Intelligence — Technical Design

## 1. System Overview

An intelligent email operations system that transforms GIC Underwriters' quote@gicunderwriters.com inbox from a chaotic email queue into an organized, automated submission pipeline. The system ingests emails, classifies them using an AI agent, links them to submissions, extracts structured data from attachments, and suggests autonomous actions.

### What the Demo Proves

1. We can read their emails and extract data correctly — every field traceable to its source
2. We understand their workflows and what happens next — stage detection, missing info identification
3. We can act autonomously — draft follow-ups, identify bottlenecks, suggest next steps
4. This is better than Outlook — organized by submission, not by email

### Stakeholders

- **Juan Carlos (JC)** — EVP, Chief Underwriting Officer. Decision maker.
- **Maribel** — GIC staff, champion for email automation. The end user.
- **Mukul Gupta** — Granada Insurance (parent company), technical coordination.

### Partnership

$5K implementation + $3K/month for web chat, email agent with data extraction, analytics, and voice agent prototyping.

---

## 2. Architecture

Three layers with clean separation of concerns. The CLI is the product. The agent is the brain. The frontend is the window.

```
┌──────────────────────────────────────────────┐
│  Frontend (React + shadcn/ui)                │
│  Board view + Submission detail view         │
├──────────────────────────────────────────────┤
│  API Layer (FastAPI)                         │
│  REST endpoints + WebSocket for live updates │
│  Calls the same core library as the CLI      │
├──────────────────────────────────────────────┤
│  Core Library (Python)                       │
│  Ingestion, data access, state management    │
│  All business logic lives here               │
├─────────────────┬────────────────────────────┤
│  CLI (Typer)    │  DeepAgent + Skills        │
│  Human/script   │  Autonomous processing     │
│  interface      │  Drives the CLI            │
├─────────────────┴────────────────────────────┤
│  MongoDB (gic_email_intelligence database)   │
│  Atlas cluster — alongside tiledesk          │
└──────────────────────────────────────────────┘
```

### Key Principles

- **CLI is the interface to the system.** Every read and write operation the agent performs goes through CLI commands. The CLI can be tested independently, used by humans, scripted, or driven by an agent.
- **Agent is the intelligence.** The DeepAgent (LangChain-based, model-agnostic) reads skills, executes CLI commands, makes decisions. It does the classifying, linking, and drafting — the CLI just provides the data and saves the results.
- **Skills teach the agent.** Each processing workflow is a packaged skill that instructs the agent on what to do, what domain knowledge to apply, and how to use the CLI. Skills are updatable without code changes.
- **API and CLI share a core library.** The FastAPI backend and the Typer CLI both call the same Python functions. No logic duplication.
- **Ingestion is dumb plumbing.** The Graph API polling loop just downloads and stores. No intelligence. Runs on a cron schedule.

### Why This Pattern Matters

This is Indemn's first instance of a generalizable agentic workflow system. The same pattern — DeepAgent + Skills + CLI — applies to any future system: RingCentral voice integration, Unisoft management system, another customer's inbox. Each gets its own CLI, its own skills, same agent harness.

---

## 3. Lifecycle Stages

Validated against 3,165 classified emails and 115 named insureds that appear across multiple email types.

### Board Columns (Action-Oriented)

| Column | What's in it | Maribel's action | Color accent |
|--------|-------------|-----------------|-------------|
| **New** | Submissions just arrived, unreviewed | Review, request info or submit to carrier | Blue |
| **Awaiting Info** | Info request sent to agent, waiting for reply | Monitor, follow up if stale | Amber |
| **With Carrier** | Submitted to USLI/Hiscox, waiting for response. **Note:** This stage has no automated entry path — GIC submits to carriers via carrier portals or outbound email from staff mailboxes, which quote@ never sees. For the demo, this column starts empty. Populated only via manual drag. In the demo script, Maribel can drag a submission here to show the interaction. In production, Unisoft integration would automate this. An empty column is better than an incorrectly populated one — the demo's credibility depends on accuracy. | Wait (system monitors) | Gray |
| **Quoted** | Carrier returned a quote, ready to forward | Forward quote to agent | Green |
| **Attention** | Declined, carrier pending, urgent followups, stale items | Triage — each card shows why it's here | Red |

### Stage Mapping from Email Types

| Email Type | Count | Stage Transition |
|-----------|-------|-----------------|
| agent_submission (73) | → | Creates new submission in **New** |
| gic_application (32) | → | Creates new submission in **New** |
| renewal_request (6) | → | Creates new submission in **New** |
| gic_info_request (2) | → | If existing submission found → moves to **Awaiting Info**. If no match → creates new submission in **New** (not Awaiting Info — we don't know enough yet). |
| agent_reply (37) | → | If all info received → **New** (ready to submit to carrier). If partial → stays **Awaiting Info** |
| agent_followup (10) | → | First followup: stays in current stage (linked for record). Second+ followup for same submission → moves to **Attention** (reason: agent_urgent). |
| report (30) | → | No stage change — informational, linked to submission if ref matches |
| gic_internal (21) | → | No stage change — internal communication, linked if relevant |
| other (13) | → | No stage change — classified for record, linked if possible |
| usli_quote (2,553) | → | Moves submission to **Quoted** |
| hiscox_quote (24) | → | Moves submission to **Quoted** |
| usli_pending (212) | → | Moves submission to **Attention** (reason: carrier_pending) |
| usli_decline (147) | → | Moves submission to **Attention** (reason: declined) |

### Attention Reasons

Cards in the Attention column each display a reason tag:

| Reason | Trigger | Visual |
|--------|---------|--------|
| `declined` | Carrier declined the submission | Red tag |
| `carrier_pending` | Carrier needs more info to finalize | Amber tag |
| `agent_urgent` | Agent has followed up 2+ times | Red tag with count |
| `stale` | No activity for 5+ days in any active stage | Gray tag with age |

### Data Validation

The 115 named insureds appearing across multiple email types confirm real lifecycle patterns:
- CASH OUT HOME INVESTMENTS LLC: decline(5), quote(2), pending(1) — multiple carrier attempts
- SKY 360 HOA: quote(3), agent_submission(1) — agent submitted, got quotes
- DORIAN POMA: pending(2), quote(1), decline(1) — full lifecycle visible
- JORISA OBOSH LLC: agent_reply(2), usli_pending(1) — info exchange visible

---

## 4. Submission Linking Algorithm

Conversation threading is useless — 99.8% of Graph API conversations are single-email threads. Linking relies on reference numbers and named insured matching.

### Reference Number Formats (from 3,088 extracted references)

| Format | Example | Source | Count |
|--------|---------|--------|-------|
| USLI prefix + alphanumeric | MGL026F9DR4, XPL026M5341 | Carrier quote/pending/decline | 1,453 |
| 6-digit numeric | 143192, 139617 | GIC internal submission ID | 45 |
| Long numeric (13+ digits) | 3389234676956 | USLI tracking system | 55 |
| Other formats | WCV 0663292, 04-CIM-000064734 | Various carriers, policy numbers | 1,526 |

### USLI Reference Prefix → LOB Mapping

Deterministic — the prefix encodes the line of business:

| Prefix | LOB | Count |
|--------|-----|-------|
| MPL | Professional Liability | 784 |
| MGL | General Liability | 477 |
| XPL | Excess Personal Liability | 308 |
| MCP | Commercial Package | 283 |
| MSE | Special Events | 281 |
| NPP | Commercial Property | 211 |
| SP | Specified Professions | 84 |
| CEQ | Contractors Equipment | 84 |
| MAH | Artisan/Handy | 75 |
| PCL | Personal Catastrophe | 71 |
| BRK | Builders Risk | 53 |
| INM | Inland Marine | 27 |
| PM | Property Manager | 23 |
| MHB | Home Business | 22 |
| MPR | Property | 19 |
| MDP | Dwelling Property | 18 |
| REA | Real Estate | 17 |
| XSL | Excess Surplus Lines | 15 |
| EPL | Employment Practices | 12 |
| STK | GL (variant) | 9 |
| NDO | Non Profit D&O | 8 |
| CUP | Contractors Umbrella | 7 |
| MLQ | Liquor Liability | 5 |
| HOP | Homeowners | 4 |

### USLI Subject Line Patterns

99.7% of USLI quotes contain the reference number in the subject:
- `Quote [REF] for [INSURED] from [AGENT] at [AGENCY]` — 51%
- `Quote [REF] for [INSURED]` — 44%
- Other patterns — 5%

### GIC Info Request Subject Pattern

Highly consistent outbound format: `Info Request for [INSURED_NAME]- [GIC_NUMBER]`

Agent replies come back as: `Re: Info Request for [INSURED_NAME]- [GIC_NUMBER]`

### Linking Algorithm

```
For each new email:
  1. Extract all reference numbers from subject + body + classification
  2. PRIMARY: If any reference number matches an existing submission → link to it
  3. SECONDARY: If GIC submission number (6-digit) matches → link to it
  4. TERTIARY: Fuzzy-match named insured (>85% similarity)
     within a time window (±90 days from email received_at) and same LOB → link to it
     - Algorithm: `rapidfuzz.fuzz.token_sort_ratio` on `named_insured_normalized` (uppercase, trimmed)
     - If multiple matches >85%: take highest score. If top two scores within 5 points, reject as ambiguous → create new submission
     - Same LOB required (prevents linking a GL submission to a Workers Comp one for the same insured)
  5. If no match → create new submission
```

The agent (not the CLI) makes the linking decision. The CLI provides:
- `submissions search --ref <number>` — find by reference number
- `submissions search --insured <name> --fuzzy` — find by name similarity
- `submissions link-email <submission-id> <email-id>` — save the link
- `submissions create` — create new submission

### Duplicate Detection

Agent submissions and GIC applications often arrive without USLI reference numbers (the carrier hasn't assigned one yet). When a USLI quote arrives later, fuzzy matching may fail to connect it to the original submission, creating a duplicate.

**Detection:** After each `submissions create`, run a lightweight check:
```
outlook-inbox submissions detect-duplicates --submission <new-id>
```
This searches for other submissions with:
- Similar named insured (`token_sort_ratio > 75%`)
- Same LOB
- Created within 30 days

If potential duplicates are found, the submission gets a `potential_duplicate_of: [submission_id]` field. The board card shows a small warning indicator. The operator can review and merge via `submissions merge` or dismiss.

This prevents the silent problem of orphaned submissions that never advance past "New" because their later emails went to a different submission.

---

## 5. Data Model

MongoDB collections in the `gic_email_intelligence` database on the existing Atlas cluster.

### Collection: `emails`

```javascript
{
  _id: ObjectId,
  graph_message_id: String,        // Microsoft Graph ID — deduplication key
  conversation_id: String,          // Graph conversation ID (mostly useless)
  folder: String,                   // "PRIVATE LABEL", "Inbox", "Archive", etc.
  subject: String,
  from_address: String,
  from_name: String,
  to_addresses: [String],
  cc_addresses: [String],
  received_at: ISODate,
  body_text: String,                // Plain text body (may be empty)
  body_html: String,                // HTML body (fallback when text is empty)
  is_read: Boolean,
  importance: String,
  attachments: [{
    name: String,
    content_type: String,
    size: Number,
    storage_path: String            // S3 key (e.g., "attachments/{email_id}/{filename}"). Sync uploads directly to S3.
  }],

  // Processing state
  processing_status: String,        // "pending" | "processing" | "classified" | "linked" | "extracted" | "complete" | "failed"
  processing_error: String,         // Why it failed (nullable)
  processing_started_at: ISODate,   // When processing began (for timeout detection)
  processed_at: ISODate,            // When processing finished

  // Classification (written by agent)
  classification: {
    email_type: String,             // "usli_quote", "agent_submission", etc.
    line_of_business: String,
    named_insured: String,
    reference_numbers: [String],
    intent_summary: String,
    classified_at: ISODate
  },

  // Linking
  submission_id: ObjectId,          // FK to submissions (nullable until linked)

  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
- `graph_message_id` (unique) — deduplication
- `processing_status` — find unprocessed emails
- `submission_id` — find all emails for a submission
- `classification.named_insured` — text index for fuzzy search
- `classification.reference_numbers` — find by ref number
- `received_at` — chronological queries

### Collection: `submissions`

```javascript
{
  _id: ObjectId,
  gic_number: String,               // 6-digit GIC submission ID (nullable)
  named_insured: String,
  named_insured_normalized: String,  // Uppercase, trimmed — for matching
  line_of_business: String,

  // Stage
  stage: String,                     // "new" | "awaiting_info" | "with_carrier" | "quoted" | "attention"
  attention_reason: String,          // "declined" | "carrier_pending" | "agent_urgent" | "stale" (nullable)
  stage_changed_at: ISODate,
  stage_history: [{
    stage: String,
    reason: String,
    changed_at: ISODate,
    triggered_by_email: ObjectId     // Which email caused the transition
  }],

  // Parties
  retail_agent_name: String,
  retail_agent_email: String,
  retail_agency_name: String,
  carrier: String,                   // "USLI", "Hiscox", "Dellwood", "Swyfft", etc.
  assigned_to: String,               // GIC staff member (nullable)

  // Quote data (populated when quoted)
  premium: String,
  coverage_limits: String,
  effective_date: String,

  // Reference numbers (one submission can have multiple)
  reference_numbers: [String],

  // Denormalized counters (updated on each email link)
  email_count: Number,
  attachment_count: Number,
  first_email_at: ISODate,
  last_activity_at: ISODate,
  last_activity_type: String,        // Email type of most recent activity (for display: "Agent replied 2h ago")
  last_activity_from: String,        // Who triggered the last activity (sender name)

  // NOTE: age_days is NOT stored — computed at query time as Math.floor((now - first_email_at) / 86400000)

  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
- `stage` — board view grouping
- `named_insured_normalized` — linking searches
- `reference_numbers` — linking searches
- `gic_number` — linking searches
- `last_activity_at` — staleness detection + stale submission cron
- `stage, last_activity_at` — board view sorting

### Collection: `extractions`

```javascript
{
  _id: ObjectId,
  email_id: ObjectId,               // FK to emails
  submission_id: ObjectId,           // FK to submissions
  source_attachment_name: String,
  pdf_document_type: String,         // "quote_letter", "application", "loss_run", "pending_notice", etc.

  // Structured data varies by document type and LOB
  // Common fields promoted to top level:
  named_insured: String,
  carrier: String,
  premium: String,
  coverage_limits: String,
  effective_date: String,
  retail_agent_name: String,
  retail_agency_name: String,
  reference_numbers: [String],

  // LOB-specific data in a flexible structure
  key_details: Object,               // Varies by LOB — endorsements, optional coverages, property details, etc.

  extracted_at: ISODate,
  created_at: ISODate
}
```

**Indexes:**
- `submission_id` — detail view extraction lookup
- `email_id` — link extractions back to source email

### Collection: `drafts`

```javascript
{
  _id: ObjectId,
  submission_id: ObjectId,           // FK to submissions
  draft_type: String,                // "info_request", "quote_forward", "followup", "decline_notification"

  to_email: String,
  subject: String,
  body: String,

  // Context for why this draft was generated
  trigger_reason: String,            // "missing_information", "stale", "quote_received", "declined" — high-level category
  missing_items: [String],           // What info is still needed (for info_request drafts)

  status: String,                    // "suggested" | "approved" | "sent" | "dismissed"

  generated_at: ISODate,
  created_at: ISODate
}
```

**Indexes:**
- `submission_id` — detail view draft lookup
- `submission_id, status` — find active drafts for a submission (for `has_draft` computation)

### Collection: `sync_state`

```javascript
{
  _id: "outlook_sync",
  last_sync_at: ISODate,
  last_message_received_at: ISODate,
  emails_synced: Number,
  status: String                     // "idle" | "syncing" | "error"
}
```

---

## 6. CLI Design

The CLI (`outlook-inbox`) is the interface between the agent and the system. It provides CRUD operations — no intelligence. Built with Typer (Python).

### Commands

```bash
# ─── Sync (ingestion — no intelligence) ───────────────────────
outlook-inbox sync                              # Pull new emails since last sync
outlook-inbox sync --since 2025-09-01           # Pull all emails from date
outlook-inbox sync --full                       # Full re-sync

# ─── Emails (read/write) ──────────────────────────────────────
outlook-inbox emails list --status pending --json --limit 20
outlook-inbox emails list --status classified --json
outlook-inbox emails list --type agent_submission --json
outlook-inbox emails list --submission <submission-id> --json  # All emails linked to a submission (for timeline)
outlook-inbox emails get <email-id> --include-body --include-attachments --json
outlook-inbox emails get <email-id> --attachment <name> --output ./file.pdf

outlook-inbox emails save-classification <email-id> \
  --type usli_quote \
  --lob "General Liability" \
  --insured "Acme LLC" \
  --refs MGL026F9DR4 \
  --summary "USLI GL quote for Acme LLC, $1,200 premium"

# ─── Submissions (read/write) ─────────────────────────────────
outlook-inbox submissions list --json
outlook-inbox submissions list --stage new --json
outlook-inbox submissions list --stage attention --reason declined --json
outlook-inbox submissions search --ref MGL026F9DR4 --json
outlook-inbox submissions search --insured "Acme" --fuzzy --json
outlook-inbox submissions get <submission-id> --json

outlook-inbox submissions create \
  --insured "Acme LLC" \
  --lob "General Liability" \
  --source-email <email-id>

outlook-inbox submissions link-email <submission-id> <email-id>
outlook-inbox submissions unlink-email <submission-id> <email-id>

outlook-inbox submissions update <submission-id> \
  --agent-name "Maria Chen" \
  --agent-email "maria@apex.com" \
  --agency "Apex Insurance" \
  --carrier USLI \
  --premium "$1,200" \
  --limits "$1M/$2M" \
  --effective-date "2026-04-01" \
  --add-ref MGL026F9DR4

outlook-inbox submissions update-stage <submission-id> quoted \
  --triggered-by <email-id>

outlook-inbox submissions update-stage <submission-id> attention \
  --reason declined --triggered-by <email-id>

outlook-inbox submissions merge <target-id> <source-id>  # Merge source into target, relink all emails

# ─── Extractions (read/write) ─────────────────────────────────
outlook-inbox extractions list --submission <submission-id> --json
outlook-inbox extractions save <email-id> \
  --attachment "quote.pdf" \
  --doc-type quote_letter \
  --data '{"premium": "$1,200", "limits": "$1M/$2M", ...}'

# ─── Drafts (read/write) ──────────────────────────────────────
outlook-inbox drafts list --submission <submission-id> --json
outlook-inbox drafts save <submission-id> \
  --type info_request \
  --to "agent@agency.com" \
  --subject "Info Request for Acme LLC- 143200" \
  --body "Dear Maria, we need the following..." \
  --trigger-reason missing_information \
  --missing-items "loss runs" "subcontractor breakdown"
outlook-inbox drafts update <draft-id> --status approved

# ─── Stats ────────────────────────────────────────────────────
outlook-inbox stats                              # Board-level counts per stage
outlook-inbox stats --attention-breakdown        # Attention reasons breakdown

# ─── Maintenance ──────────────────────────────────────────────
outlook-inbox submissions detect-stale --threshold-days 5     # Move stale submissions to Attention
outlook-inbox submissions detect-duplicates --submission <id>  # Check for potential duplicate submissions
```

All list/get commands support `--json` for machine-readable output (what the agent uses) and default to human-readable tables.

### CLI Architecture

```
outlook-inbox (Typer app)
  ├── commands/
  │   ├── sync.py          # Graph API ingestion
  │   ├── emails.py        # Email CRUD
  │   ├── submissions.py   # Submission CRUD
  │   ├── extractions.py   # Extraction CRUD
  │   ├── drafts.py        # Draft CRUD
  │   └── stats.py         # Aggregation queries
  ├── core/
  │   ├── db.py            # MongoDB connection + collections
  │   ├── models.py        # Pydantic models (shared with API)
  │   ├── graph_client.py  # Microsoft Graph API client
  │   ├── linker.py        # Reference number parsing, fuzzy matching
  │   └── config.py        # Environment variables, settings
  └── main.py              # Typer app entry point
```

The `core/` module is shared between the CLI and the FastAPI backend. No logic duplication.

---

## 7. Agent Harness + Skills

### Agent Harness

A standalone DeepAgent implementation using LangChain. Model-agnostic — works with Claude, GPT-4, or any LLM that supports tool use. The agent:

1. Loads a skill (instructions + domain knowledge)
2. Has access to the CLI as a tool (executes `outlook-inbox` commands)
3. Reads data via CLI, applies intelligence, writes results via CLI
4. Handles ambiguity, edge cases, and multi-step reasoning

### Skills

Each skill is a self-contained instruction set. The agent loads one skill per task.

#### Skill: `email-classifier`

**Purpose:** Classify a raw email — determine type, LOB, named insured, reference numbers, intent.

**Input:** Agent reads email via `outlook-inbox emails get <id> --include-body --json`

**Domain knowledge the skill provides:**
- The 13 email types: `usli_quote`, `usli_pending`, `usli_decline`, `agent_submission`, `agent_reply`, `gic_application`, `report`, `hiscox_quote`, `gic_internal`, `agent_followup`, `renewal_request`, `gic_info_request`, `other`
- The 40+ lines of business and their naming variations
- Reference number formats (USLI prefix patterns, GIC 6-digit, etc.)
- USLI subject line parsing patterns
- How to handle bilingual (Spanish) emails
- How to handle empty body text (check attachments, subject is enough for USLI)

**Output:** Agent writes via `outlook-inbox emails save-classification <id> --type ... --lob ... --insured ... --refs ... --summary ...`

**Key decision points the agent handles:**
- Ambiguous LOB (is "Commercial Package" the LOB or just a bundle?)
- Named insured normalization (LLC, Inc, Corp variations)
- Multiple reference numbers in one email
- Emails that don't fit clean categories (classified as "other" with detailed summary)

#### Skill: `submission-linker`

**Purpose:** Link a classified email to the correct submission, or create a new one.

**Input:** Agent reads classification via `outlook-inbox emails get <id> --json`, then searches submissions.

**Domain knowledge the skill provides:**
- The linking priority cascade (ref number → GIC number → fuzzy name match)
- USLI reference prefix → LOB mapping (for validation)
- Time window for fuzzy matching (±90 days)
- When to create a new submission vs link to existing
- How renewals relate to existing submissions (same insured, new submission)

**Workflow:**
```
1. Read the classified email
2. Extract reference numbers
3. Search: outlook-inbox submissions search --ref <number> --json
4. If found → link and update stage
5. If not found → search by insured name:
   outlook-inbox submissions search --insured <name> --fuzzy --json
6. Evaluate matches (same LOB? recent? confidence level?)
7. If confident match → link
8. If no match → create new submission:
   outlook-inbox submissions create --insured ... --lob ... --source-email ...
9. Update submission stage based on email type:
   outlook-inbox submissions update-stage <id> <stage>
```

#### Skill: `pdf-extractor`

**Purpose:** Extract structured insurance data from PDF attachments using vision.

**Input:** Agent reads the PDF file via the CLI or directly (file path from `outlook-inbox emails get <id> --json`).

**Domain knowledge the skill provides:**
- Document type identification (quote letter vs application vs loss run vs pending notice)
- What fields to extract per document type
- USLI quote letter structure (where to find premium, limits, endorsements, optional coverages)
- How to handle multi-page documents
- Key details that matter per LOB

**Output:** Agent writes via `outlook-inbox extractions save <email-id> --attachment <name> --doc-type ... --data '{...}'`

#### Skill: `stage-detector`

**Purpose:** Re-evaluate a submission's stage based on its full email history.

**Input:** Agent reads submission history via `outlook-inbox submissions get <id> --json`

**Domain knowledge the skill provides:**
- Stage transition rules (which email types trigger which transitions)
- Staleness thresholds (5+ days = stale)
- Attention reason classification
- How to handle conflicting signals (quote received but also pending on different LOB)
- Priority: most recent email type generally wins

**Output:** Agent writes via `outlook-inbox submissions update-stage <id> <stage> --reason ...`

#### Skill: `draft-generator`

**Purpose:** Generate a suggested response based on submission state and missing information.

**Input:** Agent reads full submission context via `outlook-inbox submissions get <id> --json` + `outlook-inbox extractions list --submission <id> --json`

**Domain knowledge the skill provides:**
- GIC's outbound email format: `Info Request for [INSURED]- [GIC_NUMBER]`
- What information is required per LOB (data-derived, starting with GL)
- Professional tone matching GIC's communication style
- How to identify what's missing vs what's been provided
- Follow-up escalation patterns (1st request, 2nd request, urgent)
- Quote forwarding format (key terms to highlight for the agent)

**LOB-specific configs** (loaded per submission):
- Required fields and documents per LOB
- Common missing items per LOB
- Derived from our vision extraction data (quote output ≈ application input requirements)
- Start with GL, expand to other LOBs over time

**Output:** Agent writes via `outlook-inbox drafts save <submission-id> --type ... --to ... --subject ... --body ... --trigger-reason ... --missing-items ...`

#### Meta-Skill: `process-new-email`

**Purpose:** Orchestrates the individual skills for end-to-end processing of a new email. This is NOT a single LLM invocation — it is **Python orchestration code** that calls each sub-skill as a separate, focused agent invocation, passing context between them.

**Orchestration (Python, not LLM):**
```python
def process_new_email():
    # 1. Atomically claim the next pending email (prevents duplicate processing)
    email = db.emails.find_one_and_update(
        {"processing_status": "pending"},
        {"$set": {"processing_status": "processing", "processing_started_at": now()}},
        sort=[("received_at", 1)]  # Oldest first
    )
    if not email:
        return None  # Nothing to process

    email_id = str(email["_id"])

    try:
        # 2. Classify (separate agent invocation)
        result = run_skill("email-classifier", context={"email_id": email_id})
        # Agent reads email via CLI, classifies, saves via CLI
        # Updates processing_status to "classified"

        # 3. Link to submission (separate agent invocation)
        result = run_skill("submission-linker", context={"email_id": email_id})
        # Agent reads classification, searches submissions, links or creates
        # Updates processing_status to "linked"

        # 4. Detect stage (separate agent invocation)
        submission_id = get_submission_id_for_email(email_id)
        result = run_skill("stage-detector", context={"submission_id": submission_id})

        # 5. Extract PDF if applicable (conditional)
        if has_extractable_pdf(email):
            result = run_skill("pdf-extractor", context={"email_id": email_id})
            # Updates processing_status to "extracted"

        # 6. Generate draft if applicable (conditional)
        if should_generate_draft(submission_id):
            result = run_skill("draft-generator", context={"submission_id": submission_id})

        # 7. Mark complete
        db.emails.update_one(
            {"_id": email["_id"]},
            {"$set": {"processing_status": "complete", "processed_at": now()}}
        )

    except Exception as e:
        db.emails.update_one(
            {"_id": email["_id"]},
            {"$set": {"processing_status": "failed", "processing_error": str(e)}}
        )
```

**Key design decisions:**
- Each sub-skill is a **separate, fresh LLM invocation** — focused context, no token accumulation
- Python orchestration handles the flow control, error handling, and conditional logic
- The LLM handles intelligence (classification decisions, linking judgment, draft writing)
- Atomic `find_one_and_update` prevents duplicate processing when multiple workers run
- Timeout guard: a cron job resets emails stuck in "processing" for >5 minutes back to "pending"

**Conditional logic (Python, not LLM):**
```python
def has_extractable_pdf(email):
    """Only extract PDFs for quotes, applications, and pending notices."""
    etype = email.get("classification", {}).get("email_type", "")
    has_pdf = any(a["content_type"] == "application/pdf" for a in email.get("attachments", []))
    return has_pdf and etype in ("usli_quote", "usli_pending", "agent_submission", "gic_application", "hiscox_quote")

def should_generate_draft(submission_id):
    """Generate drafts for submissions that need action."""
    sub = db.submissions.find_one({"_id": submission_id})
    if not sub:
        return False
    # Generate drafts for: new (info request), quoted (quote forward), attention (followup/notification)
    return sub["stage"] in ("new", "quoted", "attention")
```

### Agent Execution Mechanism

The agent harness is a Python module using LangChain. Each skill invocation is a fresh agent with **structured tools** (not string CLI commands) for reliability.

**Structured tools (not string commands):**

Instead of the agent constructing shell strings (`"emails save-classification <id> --type usli_quote --lob GL"`), each CLI operation is registered as a structured tool with typed parameters. The harness translates tool calls to CLI invocations internally.

```python
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

# Each CLI operation is a structured tool with typed parameters
@tool
def list_emails(status: str = None, submission_id: str = None, limit: int = 20) -> str:
    """List emails filtered by status or submission. Returns JSON array."""
    cmd = ["outlook-inbox", "emails", "list", "--json"]
    if status: cmd += ["--status", status]
    if submission_id: cmd += ["--submission", submission_id]
    cmd += ["--limit", str(limit)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout

@tool
def get_email(email_id: str, include_body: bool = True) -> str:
    """Get full email details including body and attachment metadata. Returns JSON."""
    cmd = ["outlook-inbox", "emails", "get", email_id, "--json"]
    if include_body: cmd += ["--include-body"]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout

@tool
def save_classification(email_id: str, email_type: str, line_of_business: str,
                        named_insured: str, reference_numbers: list[str],
                        intent_summary: str) -> str:
    """Save email classification results."""
    cmd = ["outlook-inbox", "emails", "save-classification", email_id,
           "--type", email_type, "--lob", line_of_business,
           "--insured", named_insured, "--summary", intent_summary]
    for ref in reference_numbers:
        cmd += ["--refs", ref]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout

@tool
def search_submissions(ref: str = None, insured: str = None, fuzzy: bool = False) -> str:
    """Search submissions by reference number or insured name. Returns JSON array."""
    cmd = ["outlook-inbox", "submissions", "search", "--json"]
    if ref: cmd += ["--ref", ref]
    if insured: cmd += ["--insured", insured]
    if fuzzy: cmd += ["--fuzzy"]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout

# ... similar structured tools for all other CLI operations

def run_skill(skill_name: str, context: dict) -> dict:
    """Run a skill as a fresh agent invocation."""
    skill_text = load_skill(skill_name)  # Read from skills/ directory
    llm = ChatAnthropic(model=os.environ["LLM_MODEL"])

    # Select tools relevant to this skill
    tools = SKILL_TOOL_MAP[skill_name]  # e.g., email-classifier gets [get_email, save_classification]

    # Build the agent with skill as system prompt, context as user message
    agent = create_react_agent(
        llm,
        tools,
        state_modifier=skill_text  # Skill instructions as system context
    )

    # Invoke with context (e.g., "Classify email {email_id}")
    user_message = format_context(skill_name, context)
    result = agent.invoke(
        {"messages": [("user", user_message)]},
        config={"recursion_limit": 15}  # Max 15 tool calls per skill invocation
    )
    return parse_result(result)
```

**Key design decisions:**
- **Structured tools, not string commands.** Each CLI operation has typed parameters. The LLM fills in structured fields (email_id, type, lob), the harness constructs the CLI call. No shell quoting issues.
- **Skill-specific tool subsets.** The email-classifier only sees `get_email` and `save_classification`. The submission-linker sees `search_submissions`, `create_submission`, `link_email`. Each skill gets only the tools it needs.
- **Recursion limit of 15.** Prevents runaway loops. Most skills need 2-5 tool calls. If a skill hits 15, something is wrong.
- **Fresh agent per skill.** No context accumulation across skills. Each skill gets maximum context for its specific task.

**`outlook-agent` CLI:**
```bash
# Process a single email through the full pipeline
outlook-agent process --email <email-id>

# Process all pending emails (serial, one at a time)
outlook-agent process --batch

# Process pending emails with concurrency (for initial load)
outlook-agent process --batch --workers 5

# Run a single skill for debugging
outlook-agent run-skill email-classifier --email <email-id>
outlook-agent run-skill draft-generator --submission <submission-id>
```

The `outlook-agent` CLI is separate from `outlook-inbox`. `outlook-inbox` is the system interface (CRUD). `outlook-agent` is the intelligence runner.

### Agent Processing Modes

**Initial load — uses existing data where available:**

The initial load is ~3,165 emails. We already have `all_classifications.json` from the exploration phase. Rather than re-classifying every email through the LLM (expensive, slow), we:

1. **Migrate existing classifications** — import `all_classifications.json` directly into MongoDB, setting `processing_status: "classified"` for all emails. This costs $0 and takes seconds.
2. **Run linking + stage detection** — agent processes classified emails through the linker and stage detector. This is the LLM-intensive step but much cheaper than full classification. ~$15 for 3,165 emails.
3. **Run PDF extraction** — agent extracts high-value PDFs (quotes, applications). We already have 280 vision results that can be migrated. New extractions for remaining PDFs if needed.
4. **Run draft generation** — agent generates drafts for submissions that need action. Only ~100-200 drafts needed.

**Estimated initial load:** ~$20-30 total, ~1-2 hours with 5 workers.

```bash
# Step 1: Migrate existing data (Python script, no LLM)
outlook-inbox migrate-classifications --from data/all_classifications.json
outlook-inbox migrate-extractions --from data/all_vision_results.json

# Step 2: Link + stage detect (LLM-intensive)
outlook-agent process --batch --workers 5 --skip-classification

# Step 3: Draft generation
outlook-agent process --batch --skip-classification --skip-linking --only-drafts
```

**Real-time mode (continuous):**
```bash
# Runs on schedule (every 60 seconds)
outlook-inbox sync
# Agent processes any new pending emails (serial — low volume, ~17/day)
outlook-agent process --batch
```

### Staleness Detection

A scheduled job (every hour) runs:
```bash
outlook-inbox submissions detect-stale --threshold-days 5
```
This finds submissions eligible for staleness. **Terminal stages** (excluded from staleness): `stage: "attention"` with `reason: "declined"`. All other stage/reason combinations are eligible, including `quoted` (a quote sitting un-forwarded for 5+ days should be flagged). Also excludes submissions where any linked email has `processing_status: "processing"` (agent is actively working on it).

---

## 8. Ingestion Layer

Pure plumbing. No intelligence. Runs on a cron schedule.

### Graph API Integration

- **Auth:** Client credentials flow (application permission)
- **App ID:** 4bf2eacd-4869-4ade-890c-ba5f76c7cada
- **Tenant:** 7c0931fd-6924-44fe-8fac-29c328791072
- **Permission:** Mail.Read (application, read-only)
- **Scope:** Restricted to quote@gicunderwriters.com via Exchange Online RBAC
- **Credentials:** Stored in 1Password ("GIC Outlook Integration"), loaded as environment variables

### Sync Process

```
1. Read last_sync_at from sync_state collection
2. Query Graph API: GET /users/quote@gicunderwriters.com/messages
   - $filter: receivedDateTime gt {last_sync_at}
   - $select: id,conversationId,subject,from,toRecipients,ccRecipients,
              receivedDateTime,body,hasAttachments,isRead,importance,
              parentFolderId
   - $orderby: receivedDateTime asc
   - $top: 100 (paginate)
3. For each email:
   a. Check graph_message_id doesn't already exist (dedup)
   b. Store email document with processing_status: "pending"
   c. If has_attachments:
      - GET /messages/{id}/attachments
      - For each attachment: GET individual attachment for contentBytes
      - Save to disk/S3 at attachments/{email_id}/{filename}
      - Store metadata in email.attachments array
4. Update sync_state with new timestamp
5. Push "new_emails" event to WebSocket
```

### Folder Resolution

Graph API returns `parentFolderId` as an ID, not a name. On first sync, fetch folder list and cache the ID → name mapping:
```
GET /users/quote@gicunderwriters.com/mailFolders
```

Known folders from the data:
- PRIVATE LABEL (2,961 emails) — carrier automated responses
- Inbox (99) — active human work
- Archive (51) — processed items
- GIC REPORTS (28) — system reports
- HISCOX QUOTES (9) — carrier-specific
- Others: Deleted Items, GIC NEWSLETTER, Junk E-mail, Sent Items, WC SUBMISSION REPORT

### Rate Limiting

Graph API has throttling limits. The sync process:
- Respects `Retry-After` headers
- Uses pagination ($top=100) to avoid timeout
- Backs off exponentially on 429 responses
- Logs all sync operations for debugging

---

## 9. Backend API

FastAPI application serving the React frontend. Shares the core library with the CLI.

### Authentication (Demo)

For the demo: **shared secret via URL token**. The app URL includes a token parameter (`?token=<random-secret>`). The backend validates the token on every request. No login screen, no user accounts. This prevents casual access while keeping the demo frictionless.

For production: integrate with GIC's identity provider (Entra ID SSO) or add a simple email/password auth layer.

### CORS

FastAPI CORS middleware configured to allow:
- The frontend origin (e.g., `https://gic.indemn.ai` or `http://localhost:5173` for dev)
- WebSocket upgrade requests from the same origin
- Credentials headers for the auth token

### Endpoints

```
GET  /api/health                         # Health check — returns sync status, last sync time, db connectivity
GET  /api/submissions?days=30&limit=50   # Board view — submissions grouped by stage, filtered by recency
GET  /api/submissions/:id                # Detail view — full submission with emails, extractions, drafts
GET  /api/submissions/search?q=          # Unified search (insured, agent, ref, LOB, free text)
GET  /api/emails/:id                     # Full email body (text + HTML) for inline expansion
GET  /api/emails/:id/attachments/:name   # Download/view attachment (returns file or pre-signed S3 URL)
GET  /api/stats                          # Notification counts: new, needs_response, stale
POST /api/submissions/:id/stage          # Manual stage override (drag on board)
POST /api/submissions/:id/assign         # Assign to GIC staff
WS   /api/ws                             # Real-time updates (requires token in query param)
```

### Search Implementation

`GET /api/submissions/search?q=&limit=8` searches across multiple fields using MongoDB:
- Reference numbers: exact match on `reference_numbers` array (highest priority — exact hit)
- Named insured: regex match on `named_insured_normalized` (starts-with preferred over contains)
- GIC number: exact match on `gic_number`
- Agent name: regex match on `retail_agent_name`
- LOB: regex match on `line_of_business`
- Results are ranked: exact ref match > starts-with name match > contains match
- Default limit: 8 for dropdown preview, 50 for full search page
- Returns submission-shaped results (same shape as board cards) for instant dropdown
- Frontend debounces search input (300ms) to avoid flooding

### WebSocket Events

```javascript
// Server → Client
{ "type": "new_email", "submission_id": "...", "email_summary": "..." }
{ "type": "stage_change", "submission_id": "...", "old_stage": "...", "new_stage": "..." }
{ "type": "classification_complete", "email_id": "...", "submission_id": "..." }
{ "type": "draft_ready", "submission_id": "...", "draft_type": "..." }
{ "type": "stats_update", "counts": { "new": 5, "awaiting_info": 12, ... } }
{ "type": "sync_status", "status": "syncing" | "idle" | "error", "last_sync_at": "..." }
```

**Event emission mechanism:** The FastAPI server runs a MongoDB change stream listener on the `emails`, `submissions`, and `drafts` collections. When a document changes (insert or update), the change stream handler maps the change to the appropriate WebSocket event type and broadcasts to all connected clients. This decouples the CLI/agent (which write directly to MongoDB) from the WebSocket server (which reads changes).

```python
# In FastAPI startup
async def watch_changes():
    async with db.emails.watch() as stream:
        async for change in stream:
            if change["operationType"] == "insert":
                await broadcast({"type": "new_email", ...})
            elif change["operationType"] == "update":
                fields = change["updateDescription"]["updatedFields"]
                if "classification" in fields:
                    await broadcast({"type": "classification_complete", ...})
    # Similar watchers for submissions and drafts collections
```

**Reconnection strategy (demo):** Frontend uses exponential backoff reconnection (1s, 2s, 4s, max 30s). On reconnect, the client **refetches the board view via REST** (`GET /api/submissions`). No event replay — this is a demo simplification. For production, add an events collection for replay.

**Heartbeat:** Server sends `{ "type": "ping" }` every 30 seconds. Client responds with `{ "type": "pong" }`. If client receives no ping within 45 seconds, client triggers reconnection.

### Notification Count Definitions

`GET /api/stats` returns:
```json
{ "new": 5, "needs_response": 12, "stale": 2 }
```

- **new**: Count of submissions with `stage: "new"` (unreviewed)
- **needs_response**: Count of submissions with `stage: "awaiting_info"` where the latest linked email is an `agent_reply` (agent responded, GIC needs to act) OR `stage: "quoted"` (quote ready to forward)
- **stale**: Count of submissions where `last_activity_at` is >5 days ago and stage is not terminal

### Board View Response Shape

```javascript
GET /api/submissions?days=30&limit=50
// days: only show submissions with activity in last N days (default 30)
// limit: max submissions per stage (default 50)
// Without the time filter, the Quoted column would show 800+ old submissions
// and overwhelm the board. Default to recent activity for an active pipeline view.
{
  "stages": {
    "new": {
      "count": 5,         // total in this stage (may exceed limit)
      "has_more": false,   // true if count > limit
      "submissions": [
        {
          "id": "...",
          "named_insured": "Rodriguez Grocery & Deli",
          "line_of_business": "GL",
          "retail_agent_name": "Maria Chen",
          "retail_agency_name": "Apex Insurance",
          "first_email_at": "2026-03-13T14:30:00Z",   // frontend computes age_days
          "last_activity_at": "2026-03-16T10:15:00Z",  // frontend computes "2h ago"
          "last_activity_type": "agent_reply",          // frontend renders "Agent replied"
          "last_activity_from": "Maria Chen",
          "email_count": 4,
          "assigned_to": null,
          "attention_reason": null,                     // populated for Attention stage cards
          "has_draft": true                             // computed: any draft with status="suggested" for this submission
        }
      ]
    },
    "awaiting_info": { ... },
    "with_carrier": { ... },
    "quoted": { ... },
    "attention": { ... }
  },
  "sync_status": {
    "last_sync_at": "2026-03-16T10:14:30Z",
    "status": "idle"
  }
}
```

**`has_draft` computation:** Aggregation pipeline checks `drafts` collection for any document matching `{ submission_id, status: "suggested" }`. Done in a single `$lookup` in the submissions aggregation, not N+1 queries.

### Detail View Response Shape

```javascript
GET /api/submissions/:id
{
  "submission": { /* full submission document */ },
  "emails": [
    {
      "id": "...",
      "email_type": "agent_submission",
      "subject": "...",
      "from_name": "...",
      "from_address": "...",
      "received_at": "...",
      "body_preview": "...",        // First 200 chars
      "body_url": "/api/emails/{id}",  // Fetch full body on expand (avoids loading all bodies upfront)
      "attachments": [
        {
          "name": "application.pdf",
          "size": 1234,
          "content_type": "application/pdf",
          "download_url": "/api/emails/{id}/attachments/application.pdf"
        }
      ],
      "classification": { ... }
    }
  ],
  "extractions": [
    {
      "source_attachment_name": "quote.pdf",
      "pdf_document_type": "quote_letter",
      "premium": "$1,200",
      "coverage_limits": "$1M/$2M",
      "key_details": { ... }
    }
  ],
  "drafts": [
    {
      "draft_type": "info_request",
      "subject": "Info Request for Rodriguez Grocery- 143200",
      "body": "...",
      "missing_items": ["loss runs", "subcontractor breakdown"],
      "status": "suggested"
    }
  ],
  "completeness": {
    "total_fields": 10,
    "filled_fields": 7,
    "missing": ["loss_history", "prior_carrier", "years_in_business"],
    "percentage": 70
  }
}
```

---

## 10. Frontend

React + shadcn/ui + TypeScript. Desktop-first. Clean, professional, advanced but approachable.

### Visual Style

| Element | Style |
|---------|-------|
| Background | `slate-50` — light warm gray |
| Cards | White, `border-gray-200`, subtle shadow on hover, `rounded-lg` |
| Typography | Inter (shadcn default) |
| Card title | 14px semibold, `gray-900` |
| Card metadata | 12px regular, `gray-500` |
| Stage dots | 8px colored circles next to column headers — only color accent |
| LOB tags | Small pills, `gray-100` bg, `gray-600` text |
| Age badges | Green (<2d) / amber (2-5d) / red (>5d) text only |
| Top bar | White, bottom border, flat |
| Search bar | Full-width input, `gray-100` bg, icon prefix |
| Detail overlay | Slides in from right, white bg, subtle left shadow |
| Buttons | shadcn defaults — primary is `gray-900` |
| Branding | Neutral/white-label — no specific branding, can be added later |

### View 1: Board

Full-width Kanban. 5 columns at ~370px each (at 1920px). Cards are ~80px tall, showing:
- Insured name (bold)
- LOB tag (pill)
- Agent name + agency
- Age badge
- Last activity

**Card sort order within columns:** Primary sort by `last_activity_at` ascending (oldest activity first — these need attention most). In the Attention column, secondary sort by `attention_reason` priority: `agent_urgent` > `declined` > `carrier_pending` > `stale`. 6-7 cards visible per column without scrolling.

**Top bar:** Time filter (left: "Last 7 days / 30 days / All" — default 30 days), search input (center), notification counts (right: "3 new · 5 need response · 2 stale"). No logo/branding.

**Interactions:**
- Click card → opens detail overlay
- Search → instant dropdown with submission previews
- Click notification count → filters board

### View 2: Submission Detail

Full-screen overlay, slides in from right. Close returns to board.

**Header:** Back arrow, insured name (large), submission number, LOB tag, stage badge, assigned_to, agent name + email, age, effective date.

**Left column (55%) — Timeline:**
- Vertical line on left connecting entries
- Small icon per entry type (envelope, file, arrow)
- Entry card: white bg, compact, expands on click
- Newest at top
- Entry types: email received, email sent (by GIC), carrier notification, status change, system note
- Attachments listed inline on email entries

**Right column (45%) — Extracted Data + Suggested Action:**

*Extracted data:*
- Key-value pairs grouped by section (Insured, Coverage, Carrier, Business Details)
- Collapsible sections, all expanded by default
- Values in `gray-900`, labels in `gray-500`
- Source indicator on each value — small "PDF" or "Email" chip
- Each field clickable → highlights source in timeline

*Completeness ring:*
- Circular progress, thin stroke
- Green >80%, amber 50-80%, red <50%
- Center: "7/10" large text
- Below: missing fields in `red-500`, present fields in `gray-400`

*Suggested action (pinned at bottom):*
- `blue-50` background with `blue-400` left border
- Action type label, recipient, subject preview
- Expandable to show full draft text
- "Suggested by AI" label with subtle sparkle icon
- In demo: display only. In production: approve/send button.

### Transitions

Minimal. Card hover lifts slightly. Detail overlay slides in 200ms. No bouncing or spring animations.

---

## 11. LOB Requirements

Each line of business has different information requirements. These are derived from our data and will be refined by GIC.

### Approach

1. **Data-derived initial version** — analyze vision extractions per LOB for field requirements (quote output fields ≈ application input fields for most structured data like insured, address, limits, business type). For **document requirements** (loss runs, signed applications, inspection reports), derive from the 212 USLI pending notices and 73 agent submission emails, which show what documents are commonly included or requested.
2. **LOB config files** — each LOB gets a JSON config defining required fields and documents
3. **Start with GL** for the demo (highest volume: 519 emails, 20 vision extractions)
4. **Expandable** — each new LOB is a new config file, loaded by the draft-generator skill

### GL Config (Starting Point)

```javascript
{
  "lob": "General Liability",
  "aliases": ["GL", "Commercial General Liability", "CGL"],
  "usli_prefixes": ["MGL", "STK"],
  "required_fields": [
    "named_insured",
    "business_address",
    "entity_type",
    "business_description",
    "years_in_business",
    "annual_revenue",
    "coverage_limits",
    "effective_date",
    "prior_insurance_carrier",
    "loss_history"
  ],
  "required_documents": [
    "signed_application",
    "loss_runs_3_years"
  ],
  "common_missing": [
    "loss_runs_3_years",
    "subcontractor_details",
    "years_in_business"
  ],
  "carriers": ["USLI", "Hiscox"],
  "typical_premium_range": "$800 - $5,000",
  "notes": "Most common LOB. Eligible for contractual liability removal. Excess quote often available."
}
```

### Completeness Calculation

The completeness ring in the detail view is calculated per submission:
```
total = len(lob_config.required_fields) + len(lob_config.required_documents)
filled = count of fields present in extractions + count of documents received
percentage = filled / total * 100
missing = list of unfilled fields/documents
```

---

## 12. Deployment

### Infrastructure

All on AWS, alongside existing Indemn services.

| Component | Where | Notes |
|-----------|-------|-------|
| Backend (FastAPI + CLI) | ECS container or EC2 | Long-running process (polling + WebSocket) |
| Frontend | S3 + CloudFront or served from backend | Static React build |
| Database | MongoDB Atlas | Separate `gic_email_intelligence` database on existing cluster |
| Attachments | S3 bucket | Email attachments stored here, not on container filesystem |
| Secrets | AWS Secrets Manager | Graph API credentials, LLM API key |

### Docker

Single Dockerfile for the backend. Includes:
- FastAPI server
- CLI (`outlook-inbox`) installed as a package
- Cron job for `outlook-inbox sync` every 60 seconds
- Agent harness for processing

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -e .
# FastAPI serves on 8080
# Cron runs sync every 60s
# Agent processes pending emails after each sync
CMD ["supervisord", "-c", "supervisord.conf"]
```

### Environment Variables

```bash
# MongoDB
MONGODB_URI=mongodb+srv://...
MONGODB_DATABASE=gic_email_intelligence

# Microsoft Graph API
GRAPH_TENANT_ID=7c0931fd-6924-44fe-8fac-29c328791072
GRAPH_CLIENT_ID=4bf2eacd-4869-4ade-890c-ba5f76c7cada
GRAPH_CLIENT_SECRET=<from secrets manager>
GRAPH_USER_EMAIL=quote@gicunderwriters.com

# LLM (model-agnostic)
LLM_PROVIDER=anthropic  # or openai, etc.
LLM_API_KEY=<from secrets manager>
LLM_MODEL=claude-sonnet-4-6  # configurable

# S3
S3_BUCKET=indemn-gic-attachments
AWS_REGION=us-east-1

# App
API_PORT=8080
SYNC_INTERVAL_SECONDS=60
LOG_LEVEL=info
```

### Domain and SSL

- Domain: subdomain like `gic.indemn.ai` (or `gic-demo.indemn.ai`)
- SSL: AWS ACM certificate (free, auto-renewing)
- If ECS: ALB with ACM cert, WebSocket-aware listener
- If EC2: nginx reverse proxy with Let's Encrypt or ACM via ALB

### Health Check

`GET /api/health` returns:
```json
{
  "status": "ok",
  "db": "connected",
  "sync": { "status": "idle", "last_sync_at": "...", "emails_synced": 3165 },
  "agent": { "pending_emails": 0, "last_processed_at": "..." }
}
```
ECS/ALB health check targets this endpoint.

### Data Isolation

The `gic_email_intelligence` database is separate from `tiledesk` and `indemn_platform` on the same Atlas cluster. Access is controlled by:
- Dedicated MongoDB user with read/write only on `gic_email_intelligence`
- No cross-database queries
- Attachments in a dedicated S3 bucket with separate IAM policy
- MongoDB Atlas automatic backups provide point-in-time recovery

### Graceful Degradation

| Failure | Behavior |
|---------|----------|
| **Graph API down/throttled** | Sync retries with exponential backoff. Frontend shows "Last synced: X minutes ago" banner when stale >5 min. Board shows existing data normally. |
| **LLM API down** | New emails accumulate in `pending` status. Board shows existing classified data. Agent retries on next cycle. Frontend shows "X emails processing" indicator. |
| **MongoDB down** | Complete failure — API returns 503. Frontend shows error page. Atlas auto-recovery handles most cases. |
| **Agent crashes** | Supervisord restarts the process. Partially processed emails resume from last saved status (classification saved? skip to linking). |

---

## 13. Security and Privacy

GIC's email data contains PII, business financials, and insurance details.

| Concern | Mitigation |
|---------|-----------|
| Data at rest | MongoDB Atlas encryption (default). S3 server-side encryption (AES-256). |
| Data in transit | HTTPS everywhere. TLS for MongoDB connections. |
| Access control | Dedicated MongoDB user. S3 bucket policy. No shared credentials. |
| Graph API scope | Read-only (Mail.Read). Restricted to quote@gicunderwriters.com via Exchange RBAC. |
| LLM data | Email content sent to LLM for classification/extraction. No training on customer data (Anthropic enterprise terms). |
| No email sending | Demo is read-only. Mail.Send permission is a separate future grant. |
| Credential storage | All secrets in AWS Secrets Manager or 1Password. Nothing hardcoded. |
| Web app access | Shared secret token in URL for demo. Entra ID SSO for production. |
| API rate limiting | Basic rate limiting via FastAPI middleware (100 req/min per IP for demo). |

---

## 14. Cost Estimation

At ~500 emails/month. Token estimates include agent harness overhead (skill instructions ~2,000 tokens, CLI tool definitions ~500 tokens, multi-turn reasoning ~1,000 tokens per interaction):

| Operation | Per email (input + output) | Monthly volume | Cost estimate |
|-----------|--------------------------|---------------|--------------|
| Classification | ~5,000 input + 500 output | 500 emails | ~$5 |
| Linking | ~4,000 input + 300 output | 500 emails | ~$3 |
| PDF extraction (vision) | ~8,000 input + 1,000 output | ~200 PDFs | ~$15 |
| Stage detection | ~3,000 input + 200 output | 500 emails | ~$2 |
| Draft generation | ~6,000 input + 1,000 output | ~100 drafts | ~$5 |
| **Total LLM cost** | | | **~$30/month** |

Using Claude Sonnet pricing. Actual costs may vary based on email body length and PDF page counts. Still negligible against the $3K/month agreement (~1% of revenue).

Additional infrastructure costs:
- MongoDB Atlas: existing cluster, minimal additional cost
- S3: ~$0.05/month for 2-3 GB of attachments
- ECS/EC2: ~$20-50/month for a small container
- Domain + SSL: ACM certificate (free) + Route 53 hosted zone (~$0.50/month)
- **Total infrastructure: ~$25-55/month**

---

## 15. Testing Strategy

Each skill is tested independently against the existing classified data as ground truth.

| Component | Test approach | Ground truth |
|-----------|-------------|-------------|
| CLI | Unit tests — each command works correctly with test data | MongoDB test database |
| `email-classifier` skill | Run against 50 hand-verified emails | `all_classifications.json` |
| `submission-linker` skill | Run against 115 multi-type insureds | Known groupings from data analysis |
| `stage-detector` skill | Run against submissions with known email history | Manual verification of expected stages |
| `pdf-extractor` skill | Run against 20 PDFs with known content | `all_vision_results.json` |
| `draft-generator` skill | Generate 10 drafts for known scenarios | Human review for tone, accuracy, completeness |
| Ingestion | Test sync against live inbox, verify deduplication | Compare email count with Graph API |
| API | Integration tests — each endpoint returns expected shape | Frontend contract |
| Frontend | Manual testing against real data | Visual verification |

### End-to-End Pipeline Test

Automated test that runs the full pipeline on a known set of emails:
1. Seed test database with 10 known emails (covering all major types)
2. Run `outlook-agent process --batch`
3. Assert: all 10 emails classified correctly (type, LOB, named insured)
4. Assert: emails linked to expected submissions (known ref number groupings)
5. Assert: submission stages match expected values
6. Assert: API returns correct board view and detail view shapes
7. Assert: WebSocket emits expected events during processing

This test runs in CI and catches regressions when skills or CLI commands change.

### Pre-Demo Dry Run

Manual full-scale test:
1. Run initial load on complete inbox (3,165 emails)
2. Verify submission count and groupings make sense
3. Spot-check 20 submissions across all stages
4. Verify board view renders correctly
5. Verify detail view shows correct timeline and extracted data
6. Verify drafts are reasonable for known scenarios
7. Test live sync — send a test email, verify it appears within 60 seconds
8. Test WebSocket — verify board updates in real-time when new email arrives
9. Test error recovery — stop the agent, let emails accumulate, restart, verify catch-up

---

## 16. Implementation Sequence

### Phase 1: Foundation
1. Project scaffolding — Python package with CLI + FastAPI + core library
2. MongoDB connection and collection setup
3. CLI: `sync` command (Graph API integration)
4. CLI: `emails list/get` commands
5. CLI: `submissions` CRUD commands
6. CLI: `extractions` and `drafts` CRUD commands
7. Initial data load — migrate existing `emails.jsonl` into MongoDB

### Phase 2: Agent Processing
8. Agent harness — standalone DeepAgent with CLI tool access
9. `email-classifier` skill
10. `submission-linker` skill
11. `stage-detector` skill
12. Run initial classification + linking on all 3,165 emails
13. Verify results against existing classifications

### Phase 3: Frontend
14. React + shadcn/ui project setup
15. Board view — 5 columns, submission cards, search
16. Submission detail — timeline + extracted data
17. WebSocket integration for live updates
18. Stats/notification counts

### Phase 4: Intelligence
19. `pdf-extractor` skill
20. `draft-generator` skill + GL LOB config
21. Completeness calculation
22. Suggested action display in detail view

### Phase 5: Demo Ready
23. Live sync running continuously
24. End-to-end testing
25. Deploy to AWS
26. Dry run with GIC data
27. Demo presentation

---

## 17. Open Questions (Deferred)

These are acknowledged but not blocking the demo:

- **Multi-tenancy** — Currently single-tenant (GIC only). If we offer to other brokers, add `tenant_id` to all collections.
- **Email sending (production)** — Requires Mail.Send permission grant from GIC. Separate Entra consent.
- **RingCentral integration** — Future system. Same pattern: RingCentral CLI + skills + same agent harness. Phone tickets would appear in submission timelines alongside emails.
- **Unisoft integration** — Depends on Jeremiah intro (not yet made). Would be another CLI + skill set.
- **Analytics dashboard** — Future feature. The data model supports it (stage history, timing, agent/LOB breakdowns).
- **Bilingual (Spanish)** — The classifier skill handles Spanish emails. Draft generator would need Spanish templates.
- **Business-line-specific requirements beyond GL** — Each LOB gets its own config file following the GL pattern. Expand post-demo.

---

## 18. Key Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-13 | Microsoft Graph API with client credentials flow | Read-only, application-level access to shared mailbox |
| 2026-03-13 | Submission is the central entity, not the email | Emails are events in a submission's lifecycle |
| 2026-03-13 | React + shadcn/ui + Python backend | Clean, professional, matches team expertise |
| 2026-03-13 | Two-view UI: Board → Submission Detail | Action-oriented, shows pipeline and depth |
| 2026-03-16 | 5 action-oriented columns (New, Awaiting Info, With Carrier, Quoted, Attention) | Validated against data. Tells Maribel what to DO, not just where things ARE |
| 2026-03-16 | Reference numbers as primary linking key | 96.2% coverage. Conversation threading is useless (99.8% single-email) |
| 2026-03-16 | Agent harness with CLI + Skills pattern | Generalizable to any future system. CLI is testable independently. Agent adds intelligence. |
| 2026-03-16 | CLI is the product, agent is the brain | Clean separation. CLI handles CRUD. Agent handles reasoning. |
| 2026-03-16 | MongoDB on existing Atlas cluster | Consistent with Indemn infrastructure. Separate database for isolation. |
| 2026-03-16 | AWS deployment (ECS/EC2 + S3) | Alongside existing services. Docker for portability. |
| 2026-03-16 | Start with GL for LOB requirements | Highest volume, best data coverage. Expand post-demo. |
| 2026-03-16 | Live connection for demo | "This is running on your live inbox right now" — the selling moment. |
| 2026-03-16 | Neutral/white-label UI | Focus on product, brand later. Clean and professional. |
| 2026-03-16 | LOB requirements derived from quote output data | Quote fields ≈ application input requirements. GIC refines in production. |
