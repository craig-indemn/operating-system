---
ask: "Redesign the data model and submission lifecycle to accurately model GIC's business, fixing the draft accuracy problem and the broken 5-stage model"
created: 2026-03-24
workstream: gic-email-intelligence
session: 2026-03-24-b
sources:
  - type: research
    description: "7 research documents in projects/gic-email-intelligence/research/ — business model synthesis, email workflow patterns, submission lifecycle, company profile, LOB catalog, carrier relationships, agent network"
  - type: mongodb
    description: "gic_email_intelligence database — 3,214 emails, 2,754 submissions, 304 extractions, 122 drafts analyzed"
  - type: github
    description: "Current data model at gic-email-intelligence/src/gic_email_intel/core/models.py"
---

# Data Model & Submission Lifecycle Redesign

## Why This Redesign

The current system classifies emails and generates drafts without understanding how GIC's business actually works. It goes straight from classification to action: *classify email → check missing fields → draft reply.* This produces incorrect results:

- Golf cart portal submissions with complete applications get info request drafts asking for data already in the PDF (submission-lifecycle.md — Failure #5)
- A quote comparison email (Jessica Herrero Garcia / American Modern) was treated as a new submission needing an info request (submission-lifecycle.md — Jessica case)
- 85% of submissions sit in "quoted" forever with no further tracking (submission-lifecycle.md — Failure #1)
- Declines and pending files are lumped together in "attention" despite needing completely different actions (submission-lifecycle.md — Failure #3)
- Agent replies don't trigger stage advancement — submissions stay stuck in "awaiting_info" (submission-lifecycle.md — Failure #4, Arenal Property Management case)

The redesign adds a **situation assessment** layer between classification and action, replaces the broken 5-stage model with an 8-stage lifecycle, and makes draft generation conditional on actually understanding the submission context.

### Design Principles

**1. Model the business, not the emails.** Stages reflect where the submission is in the real business process, not just what the last email type was. (business-model-synthesis.md — "The Two Operating Modes")

**2. Two operating modes need different treatment.** GIC as broker (USLI/Hiscox) follows a different lifecycle than GIC as carrier (golf carts on Granada paper). (business-model-synthesis.md — Mode 1 vs Mode 2)

**3. Understand before acting.** Before generating any draft, produce a situation assessment. Only draft when an email is the correct next action. (Craig's directive: "understand → interpret → present → then act")

---

## The 8-Stage Submission Lifecycle

### Why the Current 5-Stage Model is Broken

| Stage | Count | % | Problem | Source |
|-------|-------|---|---------|--------|
| new | 53 | 1.9% | Doesn't distinguish unread from being-worked-on | submission-lifecycle.md — Failure #1 |
| awaiting_info | 32 | 1.2% | Doesn't track whether agent already replied | submission-lifecycle.md — Failure #4 |
| with_carrier | 1 | 0.04% | Barely used; USLI auto-flow bypasses it entirely | submission-lifecycle.md — Failure #3 |
| quoted | 2,347 | 85.2% | Black hole — no further tracking, no closure | submission-lifecycle.md — Failure #1 |
| attention | 321 | 11.7% | Lumps declines (151) and pending files (170) together | submission-lifecycle.md — Failure #3 |

### The Two Lifecycles That Actually Exist

**Lifecycle A: Carrier-Automated (95% of volume, 5% of GIC's work)**

```
Agent uses USLI Retail Web → USLI auto-quotes → Notification arrives at GIC → Done
```

GIC is a passthrough. The agent already has the quote. GIC tracks for commission purposes.

Source: email-workflow-patterns.md — "93% machine-generated"; submission-lifecycle.md — "Two Lifecycles"

**Lifecycle B: Human-Processed (5% of volume, 90% of GIC's work)**

```
Submission arrives → GIC triages → [Info gap? Request it] →
[Carrier review? Submit] → Carrier responds → GIC delivers to agent → Close
```

This involves actual underwriting judgment, multi-party communication, and follow-up management. This is where AI adds value.

### The 8-Stage Model

```
                    BROKERED (USLI, Hiscox)

received → triaging → awaiting_carrier_action → quoted → closed
               │                ▲                  │
               ▼                │                  ▼
       awaiting_agent_info → processing        declined → closed


                    DIRECT (Golf Cart / Granada)

received → triaging → processing (UW review) → quoted → closed
               │                                  │
               ▼                                  ▼
       awaiting_agent_info                    declined → closed
```

| Stage | Ball Holder | What It Means | Enters When | Exits When | Source |
|-------|------------|---------------|-------------|------------|--------|
| `received` | Queue | Arrived, nobody has looked at it | Email classified and linked | System or human begins review | submission-lifecycle.md — Failure #1 |
| `triaging` | GIC | Assessing LOB, completeness, carrier fit | Review begins | Decision on next step | business-model-synthesis.md — Value Chain |
| `awaiting_agent_info` | Agent | Info request sent, waiting for reply | Info request sent | agent_reply email arrives | email-workflow-patterns.md — Pattern 3 |
| `awaiting_carrier_action` | Carrier | Submitted to carrier, waiting for response | Carrier submission made | Carrier quote/decline/pending email arrives | carrier-relationships.md — USLI flow |
| `processing` | GIC | All info in hand, actively working | Agent reply received, or UW review begins | Quote issued or declined | submission-lifecycle.md — Failure #4 |
| `quoted` | Agent | Quote delivered, pending bind decision | Quote forwarded to agent | Bind, expiration, or withdrawal | submission-lifecycle.md — Failure #1 |
| `declined` | GIC/Agent | Carrier or GIC declined. May remarket. | Decline received | Remarketed, notified, or closed | submission-lifecycle.md — Failure #3 |
| `closed` | Done | Final disposition reached | Bound, expired, withdrawn, manually closed | N/A | submission-lifecycle.md — Failure #6 |

### Auto-Quoted USLI Fast Path

For the 95% of submissions that are USLI auto-quotes:

```
received → closed (automation_level: auto_notified)
```

Skip triaging entirely. USLI prefix gives LOB deterministically (lob-catalog.md — 24 prefixes). Quote already delivered to agent through USLI Retail Web. No draft, no human processing.

### Stage Transition Rules

| Transition | From → To | Trigger | Auto? | Precondition | Source |
|-----------|-----------|---------|-------|--------------|--------|
| begin_triage | received → triaging | Classification + linking complete | Yes | — | submission-lifecycle.md |
| request_info | triaging → awaiting_agent_info | Assessment says fields genuinely missing | No | assessment.draft_appropriate AND fields_missing not empty | submission-lifecycle.md — Failure #5 |
| submit_to_carrier | triaging → awaiting_carrier_action | Submission forwarded to carrier | No | operating_mode == "brokered" | business-model-synthesis.md |
| begin_uw_review | triaging → processing | Application complete, UW review needed | No | operating_mode == "direct_underwritten" | business-model-synthesis.md — Mode 2 |
| agent_replied | awaiting_agent_info → processing | agent_reply email linked | Yes | — | submission-lifecycle.md — Failure #4 |
| carrier_quoted | awaiting_carrier_action → quoted | usli_quote/hiscox_quote email linked | Yes | — | carrier-relationships.md |
| carrier_declined | awaiting_carrier_action → declined | usli_decline email linked | Yes | — | email-workflow-patterns.md |
| quote_issued | processing → quoted | Quote delivered to agent | No | — | business-model-synthesis.md |
| uw_declined | processing → declined | GIC/UW declines the risk | No | — | business-model-synthesis.md |
| bound | quoted → closed | Bind instruction received | No | resolution: "bound" | submission-lifecycle.md |
| expired | quoted → closed | Quote effective date passed | Yes | resolution: "expired" | submission-lifecycle.md |
| remarket | declined → triaging | GIC tries another carrier | No | — | email-workflow-patterns.md — decline-then-remarket |
| manually_close | any → closed | User closes submission | No | resolution: "manually_closed" | submission-lifecycle.md — Failure #6 |

### Data Gaps in Lifecycle Model

These transitions are based on research but have limited supporting data:

| Area | What We Don't Know | Why It Matters | How to Resolve |
|------|-------------------|----------------|----------------|
| Post-quote lifecycle | Bind rates, expiration timing | Can't model quoted → closed accurately | bind@ inbox is outside our data; ask JC |
| Triaging as a real step | Whether Maribel explicitly triages or goes straight to action | Affects whether triaging is a user-visible stage or system-internal | Ask JC — question #3 in business-model-synthesis.md |
| Remarket frequency | How often GIC remarkets after decline | Affects whether declined → triaging is common or rare | Few examples in email data; ask JC |
| Multi-carrier submissions | Whether GIC submits to multiple carriers simultaneously | Would need parallel awaiting_carrier_action tracking | Not observed in data; ask JC |
| SLAs | How long each stage should take | Can't set stale thresholds accurately | No baseline from GIC; ask JC — question #7 |

---

## Situation Assessment — The Understanding Layer

### Why It Exists

The current pipeline: `classify → link → check_missing_fields → ALWAYS generate draft`

The new pipeline: `classify → link → extract → ASSESS SITUATION → determine next action → [maybe draft]`

The situation assessment is a structured interpretation that the system produces for every submission. It answers four questions:

1. **Context** — What is this situation? (portal submission? quote comparison? carrier response?)
2. **Data State** — What do we actually know? (fields confirmed present vs genuinely missing)
3. **Process State** — Where are we in the lifecycle? (recommended stage + ball holder)
4. **Next Action** — What should happen next? (and is it an email, or something else?)

### Schema

```python
class SituationAssessment(BaseModel):
    submission_id: str
    assessed_at: datetime

    # --- Context ---
    situation_type: str              # "new_submission" | "info_response" |
                                     # "carrier_quote" | "carrier_decline" |
                                     # "carrier_pending" | "quote_comparison" |
                                     # "followup_inquiry" | "renewal" |
                                     # "internal_routing"
    operating_mode: str              # "brokered" | "direct_underwritten"
    intake_channel: str              # "agent_email" | "gic_portal" |
                                     # "usli_retail_web" | "csr_relay" | "renewal"
    situation_summary: str           # Human-readable interpretation

    # --- Data State ---
    data_completeness: float         # 0.0 to 1.0
    fields_present: list[str]        # Confirmed from emails + extractions
    fields_missing: list[str]        # Genuinely not found anywhere
    data_sources: dict[str, str]     # field → source ("portal PDF", "agent email")

    # --- Process State ---
    recommended_stage: str
    ball_holder: str

    # --- Next Action ---
    next_action: str                 # "send_info_request" | "route_to_uw" |
                                     # "forward_quote" | "extract_attachments" |
                                     # "notify_decline" | "remarket" |
                                     # "monitor" | "close" | "none"
    next_action_reasoning: str       # WHY this is the right next step
    draft_appropriate: bool          # Should we generate a draft?
    draft_type: Optional[str] = None # If yes, what kind
    confidence: float                # 0.0-1.0; low = flag for human review
```

### How It Fixes the Three Original Problems

**Golf cart portal submissions (Wacaster, Escalona, Lopez):**
- `intake_channel: "gic_portal"` + extraction shows 15/17 fields present
- `situation_type: "new_submission"`, `data_completeness: 0.88`
- `next_action: "route_to_uw"`, `draft_appropriate: false`
- No info request generated. System recognizes portal collected the data.
- Source: submission-lifecycle.md — Failure #5

**Jessica Herrero Garcia (quote comparison):**
- Email contains American Modern quote PDF for Jeffrey Cueto, not a GIC application
- `situation_type: "quote_comparison"`
- `next_action_reasoning: "Attached PDF is a competing quote from American Modern, not a new application"`
- `draft_appropriate: false`
- Source: submission-lifecycle.md — Jessica case

**Auto-quoted USLI submissions:**
- `automation_level: "auto_notified"`, `intake_channel: "usli_retail_web"`
- `next_action: "close"`, `draft_appropriate: false`
- Source: email-workflow-patterns.md — "95% auto-quoted"

### Draft Generation Decision Table

| Situation | Next Action | Draft? | Draft Type | Source |
|-----------|------------|--------|------------|--------|
| Portal submission, data complete | Route to UW | **No** | — | submission-lifecycle.md — Failure #5 |
| Portal submission, data incomplete | Request genuinely missing items | **Yes** | info_request | email-workflow-patterns.md |
| Agent email, data incomplete | Request missing items | **Yes** | info_request | email-workflow-patterns.md — Pattern 3 |
| Agent email, data complete | Route to carrier or UW | **No** | — | business-model-synthesis.md |
| USLI auto-quote notification | Close or monitor | **No** | — | email-workflow-patterns.md |
| USLI pending (carrier wants info) | Request info from agent | **Yes** | info_request | carrier-relationships.md — 212 pending |
| USLI decline | Notify agent | **Yes** | decline_notification | email-workflow-patterns.md |
| Carrier quote (human-processed) | Forward to agent | **Yes** | quote_forward | business-model-synthesis.md |
| Quote comparison email | Present for comparison | **No** | — | submission-lifecycle.md — Jessica case |
| Agent follow-up on stale submission | Status update | **Yes** | status_update | email-workflow-patterns.md — followup pattern |
| CSR relay (internal routing) | Route internally | **No** | — | agent-network.md — CSR relay |

---

## Updated Enums

```python
class Stage(str, Enum):
    """8-stage lifecycle. Source: submission-lifecycle.md"""
    RECEIVED = "received"
    TRIAGING = "triaging"
    AWAITING_AGENT_INFO = "awaiting_agent_info"
    AWAITING_CARRIER_ACTION = "awaiting_carrier_action"
    PROCESSING = "processing"
    QUOTED = "quoted"
    DECLINED = "declined"
    CLOSED = "closed"


class BallHolder(str, Enum):
    """Who holds the ball. Source: agent-network.md — Ryan's wireframes"""
    QUEUE = "queue"
    GIC = "gic"
    AGENT = "agent"
    CARRIER = "carrier"
    DONE = "done"


class Resolution(str, Enum):
    """How closed submissions ended. Source: submission-lifecycle.md — Failure #6"""
    BOUND = "bound"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    REMARKETED = "remarketed"
    DECLINED_NO_ALTERNATIVE = "declined_no_alternative"
    MANUALLY_CLOSED = "manually_closed"


class AutomationLevel(str, Enum):
    """GIC involvement level. Source: email-workflow-patterns.md"""
    AUTO_NOTIFIED = "auto_notified"
    ACTIVELY_PROCESSED = "actively_processed"
    UNKNOWN = "unknown"


class IntakeChannel(str, Enum):
    """How submission entered. Source: email-workflow-patterns.md"""
    AGENT_EMAIL = "agent_email"
    GIC_PORTAL = "gic_portal"
    USLI_RETAIL_WEB = "usli_retail_web"
    CSR_RELAY = "csr_relay"
    RENEWAL = "renewal"


class DraftType(str, Enum):
    """Draft types — expanded from 4 to 6."""
    INFO_REQUEST = "info_request"
    QUOTE_FORWARD = "quote_forward"
    FOLLOWUP = "followup"
    DECLINE_NOTIFICATION = "decline_notification"
    STATUS_UPDATE = "status_update"              # NEW
    REMARKET_SUGGESTION = "remarket_suggestion"  # NEW
```

`AttentionReason` is **eliminated**. Its concerns are properly distributed:
- `declined` → first-class `declined` stage
- `carrier_pending` → `awaiting_carrier_action` stage
- `agent_urgent` → surfaced by email_count + recency, not a stage
- `stale` → `is_stale` boolean on submission (preserves actual stage)

---

## Updated Submission Schema

```python
class Submission(BaseModel):
    # === Identity ===
    gic_number: Optional[str] = None
    named_insured: str
    named_insured_normalized: str = ""
    line_of_business: str = ""

    # === Operating Context (NEW) ===
    operating_mode: str = "brokered"           # "brokered" | "direct_underwritten"
                                               # Source: business-model-synthesis.md
    intake_channel: str = "agent_email"        # IntakeChannel enum values
                                               # Source: email-workflow-patterns.md
    automation_level: str = "unknown"          # AutomationLevel enum values
                                               # Source: submission-lifecycle.md

    # === Lifecycle (REDESIGNED) ===
    stage: Stage = Stage.RECEIVED
    ball_holder: str = "queue"                 # BallHolder enum values
    stage_changed_at: datetime
    stage_history: list[StageHistoryEntry] = []

    # === Resolution (NEW) ===
    resolution: Optional[str] = None           # Resolution enum values
    resolved_at: Optional[datetime] = None

    # === Stale Tracking (REDESIGNED) ===
    is_stale: bool = False
    stale_since: Optional[datetime] = None

    # === Carrier ===
    carrier: Optional[str] = None
    carrier_reference: Optional[str] = None    # USLI ref number

    # === Agent ===
    retail_agent_name: Optional[str] = None
    retail_agent_email: Optional[str] = None
    retail_agency_name: Optional[str] = None
    retail_agency_code: Optional[str] = None   # 4-digit code; source: agent-network.md

    # === Submission Data ===
    assigned_to: Optional[str] = None
    premium: Optional[str] = None
    coverage_limits: Optional[str] = None
    effective_date: Optional[str] = None
    reference_numbers: list[str] = []

    # === Activity ===
    email_count: int = 0
    attachment_count: int = 0
    first_email_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    last_activity_type: Optional[str] = None
    last_activity_from: Optional[str] = None

    # === Deduplication ===
    potential_duplicate_of: Optional[str] = None

    # === Timestamps ===
    created_at: datetime
    updated_at: datetime
```

**Removed:** `attention_reason` — eliminated as described above.

**Unchanged:** Email, Extraction, Classification, SyncState models. These capture data correctly; the problem was in interpretation and action, not data capture.

---

## Enhanced LOB Configuration

```python
class LobConfig(BaseModel):
    """LOB config drives workflow behavior, not just gap analysis.

    Source: lob-catalog.md — three operational tiers;
    business-model-synthesis.md — Data Model Recommendation #3
    """
    # Identity
    canonical_name: str
    aliases: list[str] = []

    # Operational classification
    tier: str = "tier_1_high_volume"        # "tier_1_high_volume" |
                                            # "tier_2_specialty" |
                                            # "tier_3_direct"
                                            # Source: lob-catalog.md
    workflow_type: str = "brokered"         # "brokered" | "direct_underwritten"
                                            # DO NOT assume — derive from data
                                            # Source: business-model-synthesis.md

    # Carrier mapping
    carrier_options: list[str] = []         # Source: carrier-relationships.md
    primary_carrier: Optional[str] = None

    # Identification signals
    usli_prefixes: list[str] = []           # Source: lob-catalog.md — 24 prefixes
    portal_source: Optional[str] = None     # Source: email-workflow-patterns.md

    # Requirements
    required_fields: list[str] = []
    required_documents: list[str] = []
    common_missing: list[str] = []

    # Metrics
    typical_premium_range: Optional[str] = None
    typical_cycle_days: Optional[int] = None  # Source: submission-lifecycle.md

    notes: str = ""
```

### Current LOB Config State

| LOB | Fields | Documents | Workflow Type | Carriers | Source |
|-----|--------|-----------|--------------|----------|--------|
| General Liability | 10 | 2 | brokered | USLI, Hiscox | gl.json (existing) |
| Golf Cart | 17 | 2 | direct_underwritten | GIC/Granada | golf_cart.json (existing) |
| Other 37 LOBs | 8 (generic) | 0 | **To be determined from data** | Varies | Not yet configured |

### LOB Configuration Playbook

To configure a new LOB, follow this repeatable process:

1. **Pull email threads** for the LOB from MongoDB — read 5-10 representative submissions
2. **Identify carriers** from email types (usli_quote = USLI, hiscox_quote = Hiscox, etc.)
3. **Determine workflow_type** — if carrier response emails exist from external carriers, it's brokered. If only GIC-originated communications exist, investigate whether it's direct.
4. **Extract required fields** from info request emails — what does GIC actually ask agents for in this LOB?
5. **Extract required documents** from attachments — what PDFs typically accompany submissions?
6. **Identify USLI prefix** from reference numbers in carrier emails
7. **Check for portal source** — are there gic_portal_submission emails for this LOB?
8. **Calculate typical_cycle_days** from first_email_at to stage_changed_at for quoted submissions
9. **Write the config JSON** and validate against the email data

---

## Enhanced Draft Model

```python
class Draft(BaseModel):
    """Drafts now linked to situation assessments.

    Every draft must be traceable to the reasoning that produced it.
    """
    submission_id: str
    assessment_id: Optional[str] = None      # Links to SituationAssessment

    draft_type: DraftType
    to_email: str = ""
    subject: str = ""
    body: str = ""

    trigger_reason: str = ""                 # From assessment.next_action_reasoning
    missing_items: list[str] = []            # Only genuinely missing fields

    confidence: float = 1.0                  # From assessment.confidence
    needs_review: bool = False               # True if confidence < threshold

    status: DraftStatus = DraftStatus.SUGGESTED
    generated_at: datetime
    created_at: datetime
```

---

## Enhanced Stage History

```python
class StageHistoryEntry(BaseModel):
    """Captures ball-holder and transition context."""
    stage: Stage
    ball_holder: BallHolder
    reason: Optional[str] = None
    triggered_by: Optional[str] = None       # "email:<id>" | "user:<name>" |
                                             # "system:auto_advance" |
                                             # "system:stale_check"
    assessment_id: Optional[str] = None      # Link to assessment
    changed_at: datetime
```

---

## Summary of Changes

| Component | Current | Proposed | Why |
|-----------|---------|----------|-----|
| Stages | 5 | 8 | Current model doesn't reflect real business process |
| Ball holder | Not tracked | Explicit everywhere | Need to know whose turn it is |
| Operating mode | Not tracked | brokered / direct_underwritten | Two fundamentally different workflows |
| Intake channel | Not tracked | 5 channels | Portal submissions need different treatment |
| Automation level | Not tracked | auto_notified / actively_processed | 95% of submissions need no GIC effort |
| Situation assessment | Doesn't exist | New model between extraction and action | "Understand before acting" layer |
| Draft generation | Always generates | Gated by assessment.draft_appropriate | Only draft when email is correct next action |
| Resolution | Partial | First-class with 6 types | Submissions can actually end |
| Stale tracking | Stage-based (loses info) | Boolean flag | Staleness is a property, not a stage |
| LOB config | Fields + docs only | Adds tier, workflow_type, carriers, portal, prefixes | Config must drive workflow behavior |
| AttentionReason | 4 reasons in catch-all | Eliminated | Each concern has its proper home |
| Draft types | 4 | 6 (added status_update, remarket_suggestion) | New response patterns identified in research |

## New MongoDB Collection

| Collection | Purpose | New? |
|------------|---------|------|
| emails | Raw emails | Existing — unchanged |
| submissions | Core business entity | Existing — schema updated |
| extractions | PDF/attachment data | Existing — unchanged |
| drafts | Email draft suggestions | Existing — schema updated |
| assessments | Situation assessments | **New** |
| sync_state | Outlook sync cursor | Existing — unchanged |

---

## Open Questions for JC

These gaps in the model need input from GIC. Ranked by impact on system accuracy.

1. **Golf cart program structure** — Is it on Granada paper? Underwriting guidelines? Target volume? (business-model-synthesis.md — Question #1)
2. **Management system API** — Can we get access via Jeremiah? What data is available? (business-model-synthesis.md — Question #2)
3. **Email workflow ownership** — Is Maribel the sole processor? How is work assigned? (business-model-synthesis.md — Question #3)
4. **Post-quote lifecycle** — What happens after "quoted"? Bind process? (business-model-synthesis.md — Question #4)
5. **Other direct-underwritten LOBs** — Are roofing, pest control, or other portal LOBs also on Granada paper? (Design question — do not assume)
6. **Carrier appetite rules** — How does GIC decide USLI vs Hiscox for GL? (business-model-synthesis.md — Question #8)
