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
  - type: review
    description: "5 parallel code reviews — migration feasibility, schema validation, lifecycle completeness, entity modeling, cross-channel awareness"
  - type: review
    description: "Final code review — 3 critical, 4 moderate, 3 minor, 5 ambiguity issues resolved in round 3"
---

# Data Model & Submission Lifecycle Redesign

## Why This Redesign

The current system classifies emails and generates drafts without understanding how GIC's business actually works. It goes straight from classification to action: *classify email -> check missing fields -> draft reply.* This produces incorrect results:

- Golf cart portal submissions with complete applications get info request drafts asking for data already in the PDF (submission-lifecycle.md -- Failure #5)
- A quote comparison email (Jessica Herrero Garcia / American Modern) was treated as a new submission needing an info request (submission-lifecycle.md -- Jessica case)
- 85% of submissions sit in "quoted" forever with no further tracking (submission-lifecycle.md -- Failure #1)
- Declines and pending files are lumped together in "attention" despite needing completely different actions (submission-lifecycle.md -- Failure #3)
- Agent replies don't trigger stage advancement -- submissions stay stuck in "awaiting_info" (submission-lifecycle.md -- Failure #4, Arenal Property Management case)

The redesign adds a **situation assessment** layer between classification and action, replaces the broken 5-stage model with an 8-stage lifecycle, introduces entity collections for carriers and agents, supports line-level modeling for multi-LOB submissions, and makes draft generation conditional on actually understanding the submission context.

### Design Principles

**1. Model the business, not the emails.** Stages reflect where the submission is in the real business process, not just what the last email type was. (business-model-synthesis.md -- "The Two Operating Modes")

**2. Two operating modes need different treatment.** GIC as broker (USLI/Hiscox) follows a different lifecycle than GIC as carrier (golf carts on Granada paper). (business-model-synthesis.md -- Mode 1 vs Mode 2)

**3. Understand before acting.** Before generating any draft, produce a situation assessment. Only draft when an email is the correct next action. (Craig's directive: "understand -> interpret -> present -> then act")

**4. Separate entities deserve separate collections.** Carriers and agents are first-class entities with their own attributes, not just strings on a submission. (business-model-synthesis.md -- Recommendations #2, #5)

---

## The 8-Stage Submission Lifecycle

### Why the Current 5-Stage Model is Broken

| Stage | Count | % | Problem | Source |
|-------|-------|---|---------|--------|
| new | 53 | 1.9% | Doesn't distinguish unread from being-worked-on | submission-lifecycle.md -- Failure #1 |
| awaiting_info | 32 | 1.2% | Doesn't track whether agent already replied | submission-lifecycle.md -- Failure #4 |
| with_carrier | 1 | 0.04% | Barely used; USLI auto-flow bypasses it entirely | submission-lifecycle.md -- Failure #3 |
| quoted | 2,347 | 85.2% | Black hole -- no further tracking, no closure | submission-lifecycle.md -- Failure #1 |
| attention | 321 | 11.7% | Lumps declines (151) and pending files (170) together | submission-lifecycle.md -- Failure #3 |

### The Two Lifecycles That Actually Exist

**Lifecycle A: Carrier-Automated (95% of volume, 5% of GIC's work)**

```
Agent uses USLI Retail Web -> USLI auto-quotes -> Notification arrives at GIC -> Done
```

GIC is a passthrough. The agent already has the quote. GIC tracks for commission purposes.

Source: email-workflow-patterns.md -- "93% machine-generated"; submission-lifecycle.md -- "Two Lifecycles"

**Lifecycle B: Human-Processed (5% of volume, 90% of GIC's work)**

```
Submission arrives -> GIC triages -> [Info gap? Request it] ->
[Carrier review? Submit] -> Carrier responds -> GIC delivers to agent -> Close
```

This involves actual underwriting judgment, multi-party communication, and follow-up management. This is where AI adds value.

### The 8-Stage Model

```
                    BROKERED (USLI, Hiscox)

received -> triaging -> awaiting_carrier_action -> quoted -> closed
               |                ^                    |
               v                |                    v
       awaiting_agent_info -> processing          declined -> closed


                    DIRECT (Golf Cart / Granada)

received -> triaging -> processing (UW review) -> quoted -> closed
               |                                    |
               v                                    v
       awaiting_agent_info                      declined -> closed
```

| Stage | Ball Holder | What It Means | Enters When | Exits When | Source |
|-------|------------|---------------|-------------|------------|--------|
| `received` | Queue | Arrived, nobody has looked at it | Email classified and linked | System or human begins review | submission-lifecycle.md -- Failure #1 |
| `triaging` | GIC | Assessing LOB, completeness, carrier fit | Review begins | Decision on next step | business-model-synthesis.md -- Value Chain |
| `awaiting_agent_info` | Agent | Info request sent, waiting for reply | Info request sent | agent_reply email arrives | email-workflow-patterns.md -- Pattern 3 |
| `awaiting_carrier_action` | Carrier | Submitted to carrier, waiting for response | Carrier submission made | Carrier quote/decline/pending email arrives | carrier-relationships.md -- USLI flow |
| `processing` | GIC | All info in hand, actively working | Agent reply received, or UW review begins | Quote issued or declined | submission-lifecycle.md -- Failure #4 |
| `quoted` | Agent | Quote delivered, pending bind decision | Quote forwarded to agent | Bind, expiration, or withdrawal | submission-lifecycle.md -- Failure #1 |
| `declined` | GIC | Carrier or GIC declined. May remarket. Ball transfers to agent after GIC notifies agent and decides whether to remarket. | Decline received | Remarketed, notified, or closed | submission-lifecycle.md -- Failure #3 |
| `closed` | Done | Final disposition reached | Bound, expired, withdrawn, manually closed | N/A | submission-lifecycle.md -- Failure #6 |

### Auto-Quoted USLI Fast Path

For the 95% of submissions that are USLI auto-quotes:

```
received -> closed (automation_level: auto_notified)
```

Skip triaging entirely. USLI prefix gives LOB deterministically (lob-catalog.md -- 24 prefixes). Quote already delivered to agent through USLI Retail Web. No draft, no human processing.

### Stage Transition Rules

| Transition | From -> To | Trigger | Auto? | Precondition | Source |
|-----------|-----------|---------|-------|--------------|--------|
| auto_close | received -> closed | USLI auto-quote fast path | Yes | automation_level == "auto_notified" | email-workflow-patterns.md -- 95% auto-quoted |
| begin_triage | received -> triaging | Classification + linking complete | Yes | -- | submission-lifecycle.md |
| request_info | triaging -> awaiting_agent_info | Assessment says fields genuinely missing | No | assessment.draft_appropriate AND fields_missing not empty | submission-lifecycle.md -- Failure #5 |
| submit_to_carrier | triaging -> awaiting_carrier_action | Submission forwarded to carrier | No | operating_mode == "brokered" | business-model-synthesis.md |
| begin_uw_review | triaging -> processing | Application complete, UW review needed | No | operating_mode == "direct_underwritten" | business-model-synthesis.md -- Mode 2 |
| agent_replied | awaiting_agent_info -> processing | agent_reply email linked | Yes | -- | submission-lifecycle.md -- Failure #4 |
| reassess | awaiting_agent_info -> triaging | Agent reply changes nature of submission (different LOB, different carrier needed) | No | -- | submission-lifecycle.md |
| more_info_needed | processing -> awaiting_agent_info | GIC discovers additional info needed during processing | No | -- | email-workflow-patterns.md -- Deep Breath Holdings hull value case |
| relay_info | processing -> awaiting_carrier_action | GIC relays agent info to carrier | No | operating_mode == "brokered" | carrier-relationships.md -- Blaze Pilates relay pattern |
| carrier_quoted | awaiting_carrier_action -> quoted | usli_quote/hiscox_quote email linked | Yes | -- | carrier-relationships.md |
| carrier_declined | awaiting_carrier_action -> declined | usli_decline email linked | Yes | -- | email-workflow-patterns.md |
| carrier_needs_info | awaiting_carrier_action -> awaiting_agent_info | USLI pending file -- GIC needs to relay info request to agent | No | ball_holder changes to agent | carrier-relationships.md -- 212 pending emails; email-workflow-patterns.md -- Blaze Pilates pattern |
| quote_issued | processing -> quoted | Quote delivered to agent | No | -- | business-model-synthesis.md |
| uw_declined | processing -> declined | GIC/UW declines the risk | No | -- | business-model-synthesis.md |
| partial_decline | quoted -> declined | Carrier quotes one component but declines another | No | ball_holder: gic | email-workflow-patterns.md -- Big Rock Groups / Cash Out Home Investments |
| bound | quoted -> closed | Bind instruction received | No | resolution: "bound" | submission-lifecycle.md |
| expired | quoted -> closed | Quote effective date passed | Yes | resolution: "expired" | submission-lifecycle.md |
| decline_accepted | declined -> closed | GIC decides not to remarket, notifies agent | No | resolution: "declined_no_alternative" | submission-lifecycle.md |
| remarket | declined -> triaging | GIC tries another carrier | No | -- | email-workflow-patterns.md -- decline-then-remarket |
| manually_close | any -> closed | User closes submission | No | resolution: "manually_closed" | submission-lifecycle.md -- Failure #6 |

### Data Gaps in Lifecycle Model

These transitions are based on research but have limited supporting data:

| Area | What We Don't Know | Why It Matters | How to Resolve |
|------|-------------------|----------------|----------------|
| Post-quote lifecycle | Bind rates, expiration timing | Can't model quoted -> closed accurately | bind@ inbox is outside our data; ask JC |
| Triaging as a real step | Whether Maribel explicitly triages or goes straight to action | Affects whether triaging is a user-visible stage or system-internal | Ask JC -- question #3 in business-model-synthesis.md |
| Remarket frequency | How often GIC remarkets after decline | Affects whether declined -> triaging is common or rare | Few examples in email data; ask JC |
| Multi-carrier submissions | Whether GIC submits to multiple carriers simultaneously | Would need parallel awaiting_carrier_action tracking | Not observed in data; ask JC |
| SLAs | How long each stage should take | Can't set stale thresholds accurately | No baseline from GIC; ask JC -- question #7 |

---

## Line-Level Modeling (Grouped Submissions)

### Problem

When a multi-LOB email arrives (e.g., Commercial Package with GL + Property), it needs to be tracked as separate submissions per LOB-per-carrier, because each line has its own independent lifecycle. GL might get quoted while Property gets declined. The system must handle partial quote / partial decline without collapsing distinct outcomes into a single submission.

### Approach: Grouped Submissions

Keep `Submission` as one record per LOB-per-carrier (the current model). Add a `submission_group_id` to link related submissions for the same insured/intake event.

```python
# On Submission:
submission_group_id: Optional[str] = None  # Links related submissions for same insured/intake
```

**How it works:**
- For 95%+ of submissions (single-LOB), `submission_group_id` is null -- not part of a group
- When a multi-LOB email arrives, create separate submissions for each LOB, all sharing the same `submission_group_id`
- Each submission has its own independent `stage`, `carrier`, `ball_holder`, lifecycle
- The Risk Record view assembles all submissions in a group to show the full picture for an insured
- Partial outcomes are natural: one submission in `quoted`, another in `declined`, both in the same group

**Example:** Commercial Package email for "Acme Corp" with GL + Property:
- Submission A: Acme Corp / GL / USLI -- `submission_group_id: "grp_abc123"`, stage: quoted
- Submission B: Acme Corp / Property / USLI -- `submission_group_id: "grp_abc123"`, stage: declined

Source: Ryan's wireframes -- indemn_placement_flows.html: "System splits into parallel streams per line, each tracked independently." Status tracking per submission per carrier: sent -> pending -> clarifying -> quoted -> declined -> bound.

### Multi-LOB Email Splitting Mechanism (AMBIGUITY-3)

The email classifier already outputs `line_of_business: str`. For multi-LOB emails, the classifier outputs a new field: `lines_of_business: list[str]`.

**Classification model change:**
```python
class Classification(BaseModel):
    email_type: EmailType
    line_of_business: str = ""               # Primary LOB (backward compat)
    lines_of_business: list[str] = []        # NEW: all LOBs detected (multi-LOB emails)
    named_insured: str = ""
    reference_numbers: list[str] = []
    intent_summary: str = ""
    classified_at: datetime
```

**Linker behavior:**
- When the linker sees `len(lines_of_business) > 1`, it creates one submission per LOB, all sharing the same `submission_group_id` (generated as a new ObjectId)
- Each submission links to the same email via `Email.submission_ids` (see Phase 2 migration)
- If the classifier only detects one LOB (the common case), `lines_of_business` has one entry and behavior is unchanged

### Email.submission_id Singular to Many (AMBIGUITY-4)

**Phase 2 change:** `Email.submission_id: Optional[str]` becomes `Email.submission_ids: list[str] = []`.

- For the 95%+ of single-LOB emails, this list has one entry
- For multi-LOB emails in a submission group, this list has entries for each submission
- Migration: rename field, wrap existing string value in a list
- This IS a breaking change -- all queries using `Email.submission_id` must update to `Email.submission_ids`
- Given MongoDB's document model, a list field is more natural than a junction collection

---

## Carrier Entity

### Why a Separate Collection

Carriers are referenced across submissions but have their own attributes (submission method, response patterns, supported LOBs, binding authority). Storing carrier data as strings on submissions means duplicating and potentially inconsistent data. Currently 3 known carriers (USLI, Hiscox, Granada/GIC); GIC's website claims 15+ markets.

Source: business-model-synthesis.md -- Recommendation #2.

### Schema

```python
class Carrier(BaseModel):
    name: str                              # "USLI", "Hiscox", "Granada/GIC"
    carrier_type: str                      # "external" | "affiliated"
    submission_method: str = "unknown"     # "portal" | "email" | "api" | "unknown"
    response_email_patterns: list[str] = [] # Regex for subject line matching
    reference_format: Optional[str] = None  # e.g., "[PREFIX][NUMBERS]" for USLI
    supported_lobs: list[str] = []
    appetite_rules: dict = {}              # Future: structured appetite
    binding_authority: bool = False        # Can GIC bind on their behalf?
    am_best_rating: Optional[str] = None
    notes: str = ""
    created_at: datetime
    updated_at: datetime
```

### Impact on Submission

`Submission.carrier` changes from a plain string to a reference:

```python
# On Submission (replaces carrier: Optional[str]):
carrier_id: Optional[str] = None          # FK to carriers collection
carrier_name: Optional[str] = None        # Denormalized for display
```

---

## Agent/Agency Entity

### Why a Separate Collection

Agents submit across multiple LOBs and over time. Tracking agent-level patterns (completeness, response time, preferred channel) enables better draft personalization and workload insights. Currently agent data is scattered across submission fields.

Source: business-model-synthesis.md -- Recommendation #5; agent-network.md.

### Schema

```python
class Agent(BaseModel):
    name: str
    email: Optional[str] = None
    agency_name: Optional[str] = None
    agency_code: Optional[str] = None      # 4-digit code (e.g., "7406")
    lobs_submitted: list[str] = []         # Derived from submission data
    submission_count: int = 0
    avg_completeness: Optional[float] = None
    response_time_avg_days: Optional[float] = None
    preferred_channel: Optional[str] = None # "email" | "portal" | "phone"
    active: bool = True
    notes: str = ""
    created_at: datetime
    updated_at: datetime
```

### Impact on Submission

```python
# On Submission (in addition to existing denormalized fields):
retail_agent_id: Optional[str] = None      # FK to agents collection
```

Existing denormalized fields (`retail_agent_name`, `retail_agent_email`, `retail_agency_name`, `retail_agency_code`) are retained for display to avoid JOIN overhead on every list view.

### Ongoing Agent/Carrier Creation (AMBIGUITY-2)

**Agents:** When the linker creates a new submission with a `retail_agent_name`/`email` not found in the agents collection, it creates a new Agent record automatically. Deduplication: match on normalized email address first, then fuzzy name match (same logic as submission linking). If ambiguous, create a new record and flag `potential_duplicate_of` for manual review.

**Carriers:** Carriers are NOT auto-created. They are a configured entity (like LOB configs). If a carrier is detected that's not in the collection, the submission gets `carrier_name` set but `carrier_id` left null. An operator adds the carrier entity later. This prevents polluting the carriers collection with misclassified carrier names.

---

## Cross-Channel Awareness

### Problem

The same insured name or agent may appear in both chat (CS stream) and email (Placement stream). When this happens, the system should surface it -- not merge the records, but flag the overlap so operators see the full picture.

Source: business-model-synthesis.md -- Recommendation #8; agent-network.md -- Ryan's wireframe cross-team visibility flag.

### Schema

```python
class CrossChannelFlag(BaseModel):
    channel: str                # "chat" | "voice" | "email"
    summary: str                # "Agent Tai-Siu asked about this risk via chat on 2026-03-15"
    detected_at: datetime
    reference_id: Optional[str] = None  # chat conversation ID, call ID, etc.

# On Submission:
cross_channel_flags: list[CrossChannelFlag] = []
```

This is an awareness mechanism, not a merge. The flag is informational: "this insured/agent also appeared on another channel." No automated action is taken. Operators decide whether to investigate.

---

## Situation Assessment -- The Understanding Layer

### Why It Exists

The current pipeline: `classify -> link -> check_missing_fields -> ALWAYS generate draft`

The new pipeline: `classify -> link -> extract -> ASSESS SITUATION -> determine next action -> [maybe draft]`

The situation assessment is a structured interpretation that the system produces for every submission. It answers four questions:

1. **Context** -- What is this situation? (portal submission? quote comparison? carrier response?)
2. **Data State** -- What do we actually know? (fields confirmed present vs genuinely missing)
3. **Process State** -- Where are we in the lifecycle? (recommended stage + ball holder)
4. **Next Action** -- What should happen next? (and is it an email, or something else?)

### Schema

```python
class FieldSource(BaseModel):
    """Tracks where a field value came from, with confidence."""
    value: str
    source: str           # "portal PDF", "agent email", "USLI quote letter"
    confidence: float = 1.0

class SituationAssessment(BaseModel):
    submission_id: str
    assessed_at: datetime

    # --- Context ---
    situation_type: str              # "new_submission" | "info_response" |
                                     # "carrier_quote" | "carrier_decline" |
                                     # "carrier_pending" | "quote_comparison" |
                                     # "followup_inquiry" | "renewal" |
                                     # "internal_routing" | "misdirected" | "noise"
    operating_mode: str              # "brokered" | "direct_underwritten"
    intake_channel: str              # "agent_email" | "gic_portal" |
                                     # "granada_portal" | "usli_retail_web" |
                                     # "csr_relay"
    situation_summary: str           # Human-readable interpretation

    # --- Data State ---
    data_completeness: float         # 0.0 to 1.0
    fields_present: list[str]        # Confirmed from emails + extractions
    fields_missing: list[str]        # Genuinely not found anywhere
    data_sources: dict[str, list[FieldSource]] = {}       # field -> list of (value, source) pairs
    fields_conflicting: dict[str, list[FieldSource]] = {} # fields where sources disagree

    # --- Process State ---
    recommended_stage: str
    ball_holder: str

    # --- Next Action ---
    next_action: str                 # "send_info_request" | "route_to_uw" |
                                     # "forward_quote" | "extract_attachments" |
                                     # "notify_decline" | "remarket" |
                                     # "relay_to_carrier" | "send_status_update" |
                                     # "monitor" | "close" | "none"
    next_action_reasoning: str       # WHY this is the right next step
    draft_appropriate: bool          # Should we generate a draft?
    draft_type: Optional[str] = None # If yes, what kind
    confidence: float                # 0.0-1.0; low = flag for human review
```

### situation_type Values (11 total)

| Value | Meaning | Source |
|-------|---------|--------|
| `new_submission` | Fresh submission from agent or portal | email-workflow-patterns.md |
| `info_response` | Agent reply with requested information | email-workflow-patterns.md -- Pattern 3 |
| `carrier_quote` | Carrier issued a quote | carrier-relationships.md |
| `carrier_decline` | Carrier declined the risk | email-workflow-patterns.md |
| `carrier_pending` | Carrier needs more information | carrier-relationships.md -- 212 pending |
| `quote_comparison` | Agent sent a competing quote for comparison | submission-lifecycle.md -- Jessica case |
| `followup_inquiry` | Agent following up on status | email-workflow-patterns.md -- followup pattern |
| `renewal` | Renewal request for existing policy | email-workflow-patterns.md -- Pattern F |
| `internal_routing` | CSR relay or internal handoff | agent-network.md -- CSR relay |
| `misdirected` | Bind requests in wrong inbox, routing questions | email-workflow-patterns.md |
| `noise` | Test submissions, spam, non-submission emails | email-workflow-patterns.md |

### next_action Values (11 total)

| Value | Meaning | Source |
|-------|---------|--------|
| `send_info_request` | Draft an info request to agent | email-workflow-patterns.md -- Pattern 3 |
| `route_to_uw` | Route to underwriting review | business-model-synthesis.md -- Mode 2 |
| `forward_quote` | Forward carrier quote to agent | business-model-synthesis.md |
| `extract_attachments` | Process attachments before deciding | email-workflow-patterns.md |
| `notify_decline` | Notify agent of decline | email-workflow-patterns.md |
| `remarket` | Try another carrier | email-workflow-patterns.md -- decline-then-remarket |
| `relay_to_carrier` | Gather info from agent and forward to carrier (USLI pending pattern) | carrier-relationships.md -- 212 pending; email-workflow-patterns.md -- Blaze Pilates |
| `send_status_update` | Respond to agent follow-up with submission status | email-workflow-patterns.md -- followup pattern |
| `monitor` | No action needed, track passively | email-workflow-patterns.md |
| `close` | Close the submission | submission-lifecycle.md |
| `none` | No action at all (noise, misdirected) | email-workflow-patterns.md |

### Data Sources and Conflict Resolution

The `data_sources` field maps each extracted field to a list of `(value, source, confidence)` tuples, supporting multi-source fields. When sources disagree, the field appears in `fields_conflicting`.

**Example -- Jessica Herrero Garcia case:**
`named_insured` would appear in `fields_conflicting` with two entries:
- `FieldSource(value="Jessica Maria Herrero Garcia", source="agent email", confidence=0.9)`
- `FieldSource(value="Jeffrey Cueto", source="American Modern quote PDF", confidence=0.8)`

This surfaces the conflict for human review rather than silently picking one value.

Source: submission-lifecycle.md -- Jessica case.

### Confidence Scoring

Confidence is computed from these factors:

| Factor | Description | Range | Computable Now? |
|--------|-------------|-------|----------------|
| `classification_confidence` | How confident the email classifier was | 0.0-1.0 | **Not yet.** Phase 1 defaults: 1.0 for USLI-prefix-identified emails (deterministic), 0.8 for emails with clear type patterns, 0.5 for ambiguous. Future: add confidence output to the classifier. |
| `data_completeness` | `len(fields_present) / len(lob_config.required_fields)` | 0.0-1.0 | **Yes.** Directly computable from extraction data and LOB config. |
| `conflict_count` | Number of fields in `fields_conflicting` (0 = good, each conflict reduces confidence) | Penalty: 0.2 per conflict | **Yes.** Count of entries in `fields_conflicting`. |
| `pattern_match` | Whether situation_type matches a high-frequency pattern | 0.0-1.0 | **Set by assessor.** auto_quote = 1.0, standard info request = 0.9, unusual pattern = 0.5. |
| `extraction_status` | Whether all attachments were successfully extracted (partial extraction reduces confidence) | 0.0-1.0 | **Yes.** 1.0 if all PDFs extracted, 0.5 if some failed, 0.0 if none attempted. |

```
confidence = min(classification_confidence, data_completeness, 1.0 - (conflict_count * 0.2), pattern_match, extraction_status)
```

**Threshold:** `confidence < 0.7` -> `needs_review = true` (flag for human review instead of auto-suggesting draft).

**Note:** This confidence formula is a starting point. It should be tuned based on operator feedback -- specifically, which assessments led to incorrect actions (wrong stage, inappropriate draft, missed draft opportunity). The factors and weights may evolve.

Source: Review finding -- confidence was undefined, creating implementation risk.

### How It Fixes the Three Original Problems

**Golf cart portal submissions (Wacaster, Escalona, Lopez):**
- `intake_channel: "gic_portal"` + extraction shows 15/17 fields present
- `situation_type: "new_submission"`, `data_completeness: 0.88`
- `next_action: "route_to_uw"`, `draft_appropriate: false`
- No info request generated. System recognizes portal collected the data.
- Source: submission-lifecycle.md -- Failure #5

**Jessica Herrero Garcia (quote comparison):**
- Email contains American Modern quote PDF for Jeffrey Cueto, not a GIC application
- `situation_type: "quote_comparison"`
- `named_insured` appears in `fields_conflicting` with two sources
- `next_action_reasoning: "Attached PDF is a competing quote from American Modern, not a new application"`
- `draft_appropriate: false`
- Source: submission-lifecycle.md -- Jessica case

**Auto-quoted USLI submissions:**
- `automation_level: "auto_notified"`, `intake_channel: "usli_retail_web"`
- `next_action: "close"`, `draft_appropriate: false`
- Source: email-workflow-patterns.md -- "95% auto-quoted"

### Draft Generation Decision Table

| Situation | Next Action | Draft? | Draft Type | Source |
|-----------|------------|--------|------------|--------|
| Portal submission, data complete | Route to UW | **No** | -- | submission-lifecycle.md -- Failure #5 |
| Portal submission, data incomplete | Request genuinely missing items | **Yes** | info_request | email-workflow-patterns.md |
| Agent email, data incomplete | Request missing items | **Yes** | info_request | email-workflow-patterns.md -- Pattern 3 |
| Agent email, data complete | Route to carrier or UW | **No** | -- | business-model-synthesis.md |
| Agent reply with complete info | Advance stage | **No** | -- | email-workflow-patterns.md |
| Agent reply with partial info | Follow-up for remaining items | **Yes** | info_request | email-workflow-patterns.md -- Blaze Pilates |
| USLI auto-quote notification | Close or monitor | **No** | -- | email-workflow-patterns.md |
| USLI pending (carrier wants info) | Request info from agent | **Yes** | info_request | carrier-relationships.md -- 212 pending |
| USLI decline | Notify agent | **Yes** | decline_notification | email-workflow-patterns.md |
| Carrier quote (human-processed) | Forward to agent | **Yes** | quote_forward | business-model-synthesis.md |
| Hiscox quote | Forward to agent with portal link | **Yes** | quote_forward | carrier-relationships.md |
| Quote comparison email | Present for comparison | **No** | -- | submission-lifecycle.md -- Jessica case |
| Agent follow-up on stale submission | Status update | **Yes** | status_update | email-workflow-patterns.md -- followup pattern |
| Renewal request | Route to UW or extract attachments | **No** | -- | email-workflow-patterns.md -- Pattern F |
| CSR relay (internal routing) | Route internally | **No** | -- | agent-network.md -- CSR relay |

---

## Assessment Pipeline

### Pipeline Redesign

The processing pipeline changes from a linear 5-step sequence to a 6-step sequence with assessment as the decision-making hub.

**Current pipeline:**
```
classify → link → stage_detect → extract → draft
```

**New pipeline:**
```
classify → link → extract → assess → [maybe draft]
```

Key change: extraction moves BEFORE assessment. The assessor needs extraction data to avoid the golf cart portal problem -- if you assess before extracting PDFs, you don't know that the portal application already contains the data you'd otherwise ask for.

**ProcessingStatus flow:**
```
pending → processing → classified → linked → extracted → assessed → complete (or failed)
```

The `assessed` status means the SituationAssessment has been created and the submission stage has been updated.

### Updated harness.py Pipeline

```python
def process_email(email_id: str, ...):
    # 1. Classify (unchanged)
    run_skill("email-classifier", {"email_id": email_id})

    # 2. Link to submission (unchanged)
    run_skill("submission-linker", {"email_id": email_id})

    # 3. PDF extraction — MOVED BEFORE assessment (was step 4)
    if has_extractable_pdf(email):
        run_skill("pdf-extractor", {"email_id": email_id})

    # 4. Situation assessment — NEW (replaces stage-detector)
    submission_id = get_submission_id_for_email(email_id)
    if submission_id:
        run_skill("situation-assessor", {"submission_id": submission_id})

    # 5. Draft generation — GATED by assessment
    #    Only runs if assessment.draft_appropriate == true
    #    The assessor sets a flag; harness checks it
    if submission_id and should_generate_draft(submission_id):
        run_skill("draft-generator", {"submission_id": submission_id})
```

The `should_generate_draft()` function changes from checking stage membership to checking the assessment:

```python
def should_generate_draft(submission_id: str) -> bool:
    """Check if a draft should be generated based on the latest assessment."""
    db = get_sync_db()
    sub = db[SUBMISSIONS].find_one({"_id": ObjectId(submission_id)})
    if not sub or not sub.get("latest_assessment_id"):
        return False
    assessment = db[ASSESSMENTS].find_one(
        {"_id": ObjectId(sub["latest_assessment_id"])}
    )
    return assessment is not None and assessment.get("draft_appropriate") is True
```

### The `situation-assessor` Skill (Replaces `stage-detector`)

The `stage-detector` skill is **REMOVED**. Its logic is absorbed into the `situation-assessor`, which is a single unified skill that reads submission context and produces a SituationAssessment. This replaces the current 2-step approach of stage_detect (determine stage) + should_generate_draft() (gate drafts).

**Skill specification:**

| Property | Value |
|----------|-------|
| Input | `submission_id` |
| Tools | `get_email`, `list_emails`, `get_submission`, `list_extractions`, `get_lob_config`, `save_assessment`, `update_submission_stage` |
| Reads | All linked emails (with bodies), all extractions, the LOB config for this LOB, the carrier entity |
| Produces | A SituationAssessment document saved to the `assessments` collection |
| Updates | `submission.stage` (if recommended_stage differs and confidence >= 0.7), `submission.ball_holder`, `submission.latest_assessment_id` |
| Triggers draft | Only if `assessment.draft_appropriate == true` |

**Tool map entry:**

```python
SKILL_TOOL_MAP = {
    # ... existing skills ...
    "situation-assessor": [
        get_email, list_emails, get_submission, list_extractions,
        get_lob_config, save_assessment, update_submission_stage,
    ],
    # stage-detector: REMOVED — absorbed into situation-assessor
}
```

**New tools required:**
- `get_submission(submission_id)` — returns full submission document
- `list_extractions(submission_id)` — returns all extractions for a submission
- `get_lob_config(lob)` — returns LOB config JSON for the given LOB
- `save_assessment(submission_id, assessment_json)` — saves a SituationAssessment to the assessments collection, updates submission.latest_assessment_id

**Assessment → submission update flow (AMBIGUITY-1 resolution):**
1. Assessor creates SituationAssessment document, saves to assessments collection via `save_assessment`
2. `save_assessment` tool atomically: inserts the assessment document AND updates `submission.latest_assessment_id`
3. Assessor then calls `update_submission_stage` if `recommended_stage` differs from current stage AND `confidence >= 0.7`, which updates `stage` and `ball_holder`
4. If `confidence < 0.7`, the assessment is saved but the stage is NOT changed — it's flagged for human review via `needs_review: true` on the assessment
5. This is atomic within a single skill execution: assessment save + submission update happen in the same agent invocation

### The `draft-generator` Skill (Updated, Not Removed)

The `draft-generator` skill is **KEPT** but its role changes. It no longer decides WHETHER to draft — the assessor decides that. The draft generator only runs when called, and receives the assessment context.

**Changes to draft_generator.md:**
- Receives assessment context: `situation_type`, `next_action`, `missing_items`, `next_action_reasoning`
- Only called when `assessment.draft_appropriate == true`
- Uses new DraftType values (adds `status_update`, `remarket_suggestion`)
- Subject line patterns use new stage awareness (e.g., stage `awaiting_carrier_action` vs `awaiting_agent_info` changes the subject)

**Updated tool map:**

```python
"draft-generator": [
    get_email, list_emails, get_submission, get_assessment, save_draft,
],
```

New tool `get_assessment(assessment_id)` returns the latest SituationAssessment so the draft generator has the assessor's reasoning.

### LLM Prompt Changes (CRITICAL-2)

**1. `stage_detector.md` → REMOVED**

Replaced entirely by `situation_assessor.md`. The stage detection logic (transition rules, conflict resolution) is now part of the assessor's responsibilities.

**2. `draft_generator.md` → UPDATED**

```markdown
# Draft Generator Skill

You are generating professional email drafts for GIC Underwriters.
You are called ONLY when a situation assessment has determined a draft is appropriate.

## Context Available

Read the latest assessment for context:
- assessment.situation_type — what kind of situation this is
- assessment.next_action — what the draft should accomplish
- assessment.next_action_reasoning — WHY this is the right action
- assessment.fields_missing — genuinely missing items (verified against extractions)
- assessment.fields_conflicting — fields where sources disagree

## Draft Types (6 total)

| Type | When | Template |
|------|------|---------|
| info_request | Assessment says fields genuinely missing | Request specific items from agent |
| quote_forward | Quote received, ready to send to agent | Forward quote with key terms |
| followup | Stale submission, no agent response | Professional follow-up |
| decline_notification | Carrier declined | Notify agent with next steps |
| status_update | Agent follow-up on submission status | Update agent on current state |
| remarket_suggestion | Decline received, remarket possible | Suggest alternative carriers/options |

## Subject Line Patterns (Stage-Aware)

- awaiting_agent_info: "Info Request for [INSURED]- [GIC_NUMBER]"
- awaiting_carrier_action: "Status Update: [INSURED]- [GIC_NUMBER]"
- declined: "Decline Notice: [INSURED]- [GIC_NUMBER]"
- quoted: "Quote for [INSURED]- [GIC_NUMBER]"

## Instructions

1. Read the assessment: `get_assessment(assessment_id)`
2. Read the submission: `get_submission(submission_id)`
3. Read linked emails for tone/context: `list_emails(submission_id=<id>)`
4. Generate draft using assessment.next_action as the guide
5. Save: `save_draft(submission_id, draft_type, to_email, subject, body, ...)`

CRITICAL: Do NOT independently decide what's missing. Use assessment.fields_missing.
The assessment has already checked extractions — do not re-derive the gap analysis.
```

**3. `situation_assessor.md` → NEW**

```markdown
# Situation Assessor Skill

You are evaluating a submission's situation to determine the correct stage,
ball holder, and next action. You replace the old stage-detector with a
comprehensive understanding of the submission context.

## System Context

GIC Underwriters operates in two modes:
- **Brokered** (USLI, Hiscox): GIC brokers between retail agents and carriers
- **Direct underwritten** (Golf Cart / Granada): GIC underwrites on its own paper

## The 8 Stages

| Stage | Ball Holder | Meaning |
|-------|------------|---------|
| received | queue | Arrived, unreviewed |
| triaging | gic | Assessing completeness and carrier fit |
| awaiting_agent_info | agent | Info request sent, waiting for reply |
| awaiting_carrier_action | carrier | Submitted to carrier, waiting |
| processing | gic | All info in hand, actively working |
| quoted | agent | Quote delivered, pending bind decision |
| declined | gic | Carrier/GIC declined, may remarket |
| closed | done | Final disposition reached |

## Input

Read ALL of the following before producing your assessment:
1. The submission: `get_submission(submission_id)`
2. All linked emails (with bodies): `list_emails(submission_id=<id>)` then
   `get_email(email_id)` for each
3. All extractions: `list_extractions(submission_id=<id>)`
4. The LOB config: `get_lob_config(lob_name)`

## Output

Produce a SituationAssessment JSON with ALL required fields.

## Key Rules

1. **Check extraction data BEFORE declaring fields missing.** If a PDF
   extraction shows named_insured, business_address, etc., those fields
   are PRESENT even if they weren't in the email body. This is the #1
   cause of incorrect info requests.

2. **Recognize portal submissions.** Emails from noreply@gicunderwriters.com
   with PDF attachments are portal submissions. The PDF typically contains
   most required fields. Set intake_channel: "gic_portal".

3. **Identify auto-quoted USLI notifications.** If the email is usli_quote
   and came through USLI Retail Web (agent submitted directly to USLI),
   set automation_level: "auto_notified". The agent already has the quote.
   next_action: "close" or "monitor". draft_appropriate: false.

4. **Detect field conflicts across sources.** When the same field has
   different values from different emails/extractions, put it in
   fields_conflicting with both FieldSource entries. Do NOT pick one
   silently.

5. **Stage determination follows transition rules.** Don't just map
   the latest email type to a stage. Consider the full email history
   and current stage. An agent_reply after an info_request means
   processing, not received.

## Save Results

1. Save the assessment: `save_assessment(submission_id, assessment_json)`
2. If recommended_stage differs from current AND confidence >= 0.7:
   `update_submission_stage(submission_id, stage, ball_holder, ...)`
3. If confidence < 0.7: save assessment but do NOT change stage.
   The assessment.needs_review will be set to true automatically.
```

### Submission Linker Tool Access (MODERATE-4)

The `submission-linker` skill needs expanded tool access to set fields it determines during linking. The linker identifies `operating_mode`, `intake_channel`, `automation_level`, `carrier_id`, and `carrier_name` from email patterns.

**Expanded `create_submission` tool:** Add parameters for the new fields:

```python
@tool
def create_submission(
    named_insured: str,
    line_of_business: str = "",
    source_email_id: str = None,
    gic_number: str = None,
    retail_agent_name: str = None,
    retail_agent_email: str = None,
    retail_agency_name: str = None,
    # NEW fields:
    operating_mode: str = "brokered",
    intake_channel: str = "agent_email",
    automation_level: str = "unknown",
    carrier_id: str = None,
    carrier_name: str = None,
) -> str:
```

**Add `update_submission` to the linker's tool set** for cases where the linker links to an existing submission and needs to update these fields:

```python
SKILL_TOOL_MAP = {
    "submission-linker": [
        get_email, search_submissions, create_submission,
        link_email_to_submission, update_submission_stage,
        update_submission,  # NEW — for setting operating_mode, intake_channel, etc.
    ],
}
```

**Detection logic in the linker:**
- `operating_mode`: Derived from LOB config's `workflow_type` field
- `intake_channel`: Determined from email `from_address` pattern:
  - `noreply@gicunderwriters.com` → `gic_portal`
  - `quotes@granadainsurance.com` → `granada_portal`
  - USLI auto-format subjects/references → `usli_retail_web`
  - CSR-forwarded emails (from `csr@` or internal GIC addresses) → `csr_relay`
  - All others → `agent_email`
- `automation_level`: Set to `auto_notified` for USLI auto-quotes, `unknown` otherwise (assessor may upgrade to `actively_processed`)

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


class ProcessingStatus(str, Enum):
    """Email processing pipeline status."""
    PENDING = "pending"
    PROCESSING = "processing"
    CLASSIFIED = "classified"
    LINKED = "linked"
    EXTRACTED = "extracted"
    ASSESSED = "assessed"          # NEW: after extraction, before complete
    COMPLETE = "complete"
    FAILED = "failed"


class BallHolder(str, Enum):
    """Who holds the ball. Source: agent-network.md -- Ryan's wireframes"""
    QUEUE = "queue"
    GIC = "gic"
    AGENT = "agent"
    CARRIER = "carrier"
    DONE = "done"


class Resolution(str, Enum):
    """How closed submissions ended. Source: submission-lifecycle.md -- Failure #6"""
    BOUND = "bound"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    REMARKETED = "remarketed"         # Set when GIC tried another carrier after initial
                                      # decline. The remarket transition (declined → triaging)
                                      # creates a new cycle, but if GIC decides to close the
                                      # original submission and track the remarket as a new
                                      # linked submission via submission_group_id, the original
                                      # resolves as REMARKETED.
    DECLINED_NO_ALTERNATIVE = "declined_no_alternative"
    MANUALLY_CLOSED = "manually_closed"


class AutomationLevel(str, Enum):
    """GIC involvement level. Source: email-workflow-patterns.md"""
    AUTO_NOTIFIED = "auto_notified"
    ACTIVELY_PROCESSED = "actively_processed"
    UNKNOWN = "unknown"


class IntakeChannel(str, Enum):
    """How submission entered. 5 channels.
    Source: email-workflow-patterns.md
    Note: renewal is a situation_type, not a channel -- renewals arrive via any channel.
    """
    AGENT_EMAIL = "agent_email"
    GIC_PORTAL = "gic_portal"
    GRANADA_PORTAL = "granada_portal"    # quotes@granadainsurance.com -- distinct system
    USLI_RETAIL_WEB = "usli_retail_web"
    CSR_RELAY = "csr_relay"


class DraftType(str, Enum):
    """Draft types -- expanded from 4 to 6."""
    INFO_REQUEST = "info_request"
    QUOTE_FORWARD = "quote_forward"
    FOLLOWUP = "followup"
    DECLINE_NOTIFICATION = "decline_notification"
    STATUS_UPDATE = "status_update"              # NEW
    REMARKET_SUGGESTION = "remarket_suggestion"  # NEW
```

`AttentionReason` is **eliminated**. Its concerns are properly distributed:
- `declined` -> first-class `declined` stage
- `carrier_pending` -> `awaiting_carrier_action` stage
- `agent_urgent` -> surfaced by email_count + recency, not a stage
- `stale` -> `is_stale` boolean on submission (preserves actual stage)

---

## Updated Submission Schema

```python
class Submission(BaseModel):
    # === Identity ===
    gic_number: Optional[str] = None
    named_insured: str
    named_insured_normalized: str = ""
    line_of_business: str = ""

    # === Group (Line-Level Modeling) ===
    submission_group_id: Optional[str] = None  # Links related submissions for same
                                               # insured/intake (multi-LOB).
                                               # Null for single-LOB (95%+ of cases).
                                               # Source: Ryan's wireframes

    # === Operating Context ===
    operating_mode: str = "brokered"           # "brokered" | "direct_underwritten"
                                               # Source: business-model-synthesis.md
    intake_channel: str = "agent_email"        # IntakeChannel enum values
                                               # Source: email-workflow-patterns.md
    automation_level: str = "unknown"          # AutomationLevel enum values
                                               # Source: submission-lifecycle.md

    # === Lifecycle ===
    stage: Stage = Stage.RECEIVED
    ball_holder: str = "queue"                 # BallHolder enum values
    stage_changed_at: datetime
    stage_history: list[StageHistoryEntry] = []

    # === Resolution ===
    resolution: Optional[str] = None           # Resolution enum values
    resolved_at: Optional[datetime] = None

    # === Assessment Link ===
    latest_assessment_id: Optional[str] = None # FK to assessments collection

    # === Stale Tracking ===
    is_stale: bool = False
    stale_since: Optional[datetime] = None

    # === Carrier (Entity Reference) ===
    carrier_id: Optional[str] = None           # FK to carriers collection
    carrier_name: Optional[str] = None         # Denormalized for display
    carrier_reference: Optional[str] = None    # The PRIMARY carrier reference number for this
                                               # submission. For USLI: prefix+number (e.g.,
                                               # MGL026F9DR4). For Hiscox: the quote reference.
                                               # This is the "official" ref that GIC and the
                                               # carrier use to identify the submission. When
                                               # there are multiple USLI refs (quote revisions),
                                               # carrier_reference is the LATEST one.

    # === Agent (Entity Reference) ===
    retail_agent_id: Optional[str] = None      # FK to agents collection
    retail_agent_name: Optional[str] = None    # Denormalized for display
    retail_agent_email: Optional[str] = None
    retail_agency_name: Optional[str] = None
    retail_agency_code: Optional[str] = None   # 4-digit code; source: agent-network.md

    # === Submission Data ===
    assigned_to: Optional[str] = None
    premium_quoted: Optional[float] = None     # Numeric for aggregation
    premium_bound: Optional[float] = None      # Numeric; set at bind time
    coverage_limits: Optional[str] = None      # String OK -- "$1M/$2M" format
    effective_date: Optional[str] = None
    reference_numbers: list[str] = []           # ALL reference numbers found across all emails
                                               # (USLI refs, GIC numbers, long tracking numbers).
                                               # Used for linking. Distinct from carrier_reference
                                               # which is the single primary carrier ref.

    # === Cross-Channel ===
    cross_channel_flags: list[CrossChannelFlag] = []

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

**Removed:** `attention_reason` -- eliminated as described above. `carrier` (plain string) -- replaced by `carrier_id` + `carrier_name`.

**Premium field migration (phased):** In Phase 1, ADD `premium_quoted: Optional[float]` and `premium_bound: Optional[float]` alongside the existing `premium: Optional[str]`. In Phase 2, migrate string premium values to float (parse "$1,329" -> 1329.0), then remove the old `premium` field. Both old and new fields coexist during Phase 1.

**Added:** `submission_group_id`, `latest_assessment_id`, `carrier_id`, `retail_agent_id`, `premium_quoted`, `premium_bound`, `cross_channel_flags`.

**Unchanged:** Extraction, Classification, SyncState models. These capture data correctly; the problem was in interpretation and action, not data capture.

**Email model change (Phase 2):** `Email.submission_id: Optional[str]` changes to `Email.submission_ids: list[str] = []`. For the 95%+ of single-LOB emails, this list has one entry. For multi-LOB emails in a submission group, this list has entries for each submission. Migration: rename field, wrap existing string value in a list. All queries using `Email.submission_id` must update to `Email.submission_ids`. See AMBIGUITY-4 in Migration Strategy.

---

## Enhanced LOB Configuration

```python
class LobConfig(BaseModel):
    """LOB config drives workflow behavior, not just gap analysis.

    Source: lob-catalog.md -- three operational tiers;
    business-model-synthesis.md -- Data Model Recommendation #3
    """
    # Identity
    canonical_name: str
    aliases: list[str] = []

    # Operational classification
    tier: str = "auto_brokered"            # "auto_brokered" |
                                            # "active_brokered" |
                                            # "direct_underwritten"
                                            # Source: lob-catalog.md
                                            # Note: research proposed 4 tiers; the 4th
                                            # "emerging/specialty" merges into active_brokered
                                            # for LOBs with minimal data.
    workflow_type: str = "brokered"         # "brokered" | "direct_underwritten"
                                            # Per-LOB configuration, NOT derived at runtime.
                                            # Configure during LOB playbook step 3.
                                            # Default: "brokered" (USLI handles 91% of emails).
                                            # Do not assume all non-Golf-Cart LOBs are brokered --
                                            # investigate portal LOBs (roofing, pest control)
                                            # before assigning.
                                            # Source: business-model-synthesis.md

    # Carrier mapping
    carrier_options: list[str] = []         # Source: carrier-relationships.md
    primary_carrier: Optional[str] = None

    # Identification signals
    usli_prefixes: list[str] = []           # Source: lob-catalog.md -- 24 prefixes
    portal_source: Optional[str] = None     # Source: email-workflow-patterns.md

    # Requirements
    required_fields: list[str] = []
    required_documents: list[str] = []
    common_missing: list[str] = []

    # Carrier appetite
    appetite_description: str = ""          # Placeholder for carrier appetite rules per LOB
                                            # Source: business-model-synthesis.md -- Rec #3

    # Metrics
    typical_premium_range: Optional[str] = None
    typical_cycle_days: Optional[int] = None  # Source: submission-lifecycle.md

    notes: str = ""
```

### Tier Definitions

| Tier | Old Name | Description | Example LOBs |
|------|----------|-------------|-------------|
| `auto_brokered` | tier_1_high_volume | USLI auto-quotes, GIC is passthrough | GL, Inland Marine, Commercial Property |
| `active_brokered` | tier_2_specialty | Requires GIC involvement to broker | Workers Comp, Liquor Liability, emerging/specialty LOBs |
| `direct_underwritten` | tier_3_direct | GIC underwrites on Granada paper | Golf Cart, potentially others TBD |

### Current LOB Config State

| LOB | Fields | Documents | Workflow Type | Carriers | Source |
|-----|--------|-----------|--------------|----------|--------|
| General Liability | 10 | 2 | brokered | USLI, Hiscox | gl.json (existing) |
| Golf Cart | 17 | 2 | direct_underwritten | GIC/Granada | golf_cart.json (existing) |
| Other 37 LOBs | 8 (generic) | 0 | **To be determined from data** | Varies | Not yet configured |

### USLI Prefix Ambiguity Note

NPP prefix is ambiguous -- maps to both Commercial Property and Non Profit. Need USLI data or JC input to resolve. XPL/PCL overlap for personal liability LOBs also needs investigation.

### LOB Configuration Playbook

To configure a new LOB, follow this repeatable process:

1. **Pull email threads** for the LOB from MongoDB -- read 5-10 representative submissions
2. **Identify carriers** from email types (usli_quote = USLI, hiscox_quote = Hiscox, etc.)
3. **Determine workflow_type** -- if carrier response emails exist from external carriers, it's brokered. If only GIC-originated communications exist, investigate whether it's direct. Configure as a per-LOB setting.
4. **Extract required fields** from info request emails -- what does GIC actually ask agents for in this LOB?
5. **Extract required documents** from attachments -- what PDFs typically accompany submissions?
6. **Identify USLI prefix** from reference numbers in carrier emails
7. **Check for portal source** -- are there gic_portal_submission emails for this LOB?
8. **Calculate typical_cycle_days** from first_email_at to stage_changed_at for quoted submissions
9. **Write the config JSON** and validate against the email data

**Minimum data threshold:** For LOBs with fewer than 10 emails, use the generic config. Do not attempt to build LOB-specific required_fields from insufficient data. Flag for future configuration when volume warrants it.

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
    needs_review: bool = False               # True if confidence < 0.7

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

**Migration notes:**
- Old `stage_history` entries lack `ball_holder`. The migration must handle dual-shape entries -- old entries without `ball_holder` are valid historical records and should not be discarded. See Migration Strategy section.
- Old field `triggered_by_email: Optional[str]` (contains email ObjectId or null) is renamed to `triggered_by: Optional[str]` (contains "email:\<id\>", "user:\<name\>", "system:auto_advance"). Migration: for existing entries where `triggered_by_email` is not null, transform to `"email:{value}"`. Reading code must check for both field names during the transition period.

---

## MongoDB Collections

| Collection | Purpose | Status |
|------------|---------|--------|
| emails | Raw emails | Existing -- unchanged |
| submissions | Core business entity | Existing -- schema updated |
| extractions | PDF/attachment data | Existing -- unchanged |
| drafts | Email draft suggestions | Existing -- schema updated |
| assessments | Situation assessments | **NEW** |
| carriers | Carrier entities | **NEW** |
| agents | Agent/agency entities | **NEW** |
| sync_state | Outlook sync cursor | Existing -- unchanged |

---

## Summary of Changes

| Component | Current | Proposed | Why |
|-----------|---------|----------|-----|
| Stages | 5 | 8 | Current model doesn't reflect real business process |
| Ball holder | Not tracked | Explicit everywhere | Need to know whose turn it is |
| Operating mode | Not tracked | brokered / direct_underwritten | Two fundamentally different workflows |
| Intake channel | Not tracked | 5 channels (renewal removed -- it's a situation_type) | Portal submissions need different treatment |
| Automation level | Not tracked | auto_notified / actively_processed | 95% of submissions need no GIC effort |
| Situation assessment | Doesn't exist | New model between extraction and action | "Understand before acting" layer |
| Draft generation | Always generates | Gated by assessment.draft_appropriate | Only draft when email is correct next action |
| Resolution | Partial | First-class with 6 types | Submissions can actually end |
| Stale tracking | Stage-based (loses info) | Boolean flag | Staleness is a property, not a stage |
| LOB config | Fields + docs only | Adds tier, workflow_type, carriers, portal, prefixes, appetite | Config must drive workflow behavior |
| LOB tiers | tier_1/2/3 | auto_brokered / active_brokered / direct_underwritten | Names describe operational workflow, not volume |
| AttentionReason | 4 reasons in catch-all | Eliminated | Each concern has its proper home |
| Draft types | 4 | 6 (added status_update, remarket_suggestion) | New response patterns identified in research |
| Carrier entity | String on submission | Separate collection + FK reference | 15+ carriers, each with own attributes |
| Agent entity | Fields on submission | Separate collection + FK reference + denormalized display | Agent-level patterns enable better personalization |
| Line-level modeling | Not supported | submission_group_id links multi-LOB submissions | Partial quote/decline handling |
| Cross-channel awareness | Not tracked | CrossChannelFlag list on submission | Surface overlap between chat/voice/email |
| Financial tracking | premium (string) | premium_quoted + premium_bound (float) | Numeric aggregation for revenue tracking. Phase 1: coexist. Phase 2: migrate + remove old. |
| ProcessingStatus | 7 values | 8 (added ASSESSED) | Assessment is a distinct pipeline step |
| data_sources | dict[str, str] | dict[str, list[FieldSource]] + fields_conflicting | Multi-source fields and conflict resolution |
| Confidence scoring | Undefined | 5-factor formula with 0.7 threshold | Implementation clarity; human review gating |
| Processing pipeline | classify → link → stage_detect → extract → draft | classify → link → extract → assess → [maybe draft] | Extraction before assessment; assessment gates drafts |
| stage-detector skill | Standalone skill | **REMOVED** — absorbed into situation-assessor | Single unified "understand" step |
| draft-generator skill | Decides whether + what to draft | Only called when assessment says draft_appropriate | Decouples "should we draft?" from "what to draft?" |
| Email.submission_id | Optional[str] (singular) | submission_ids: list[str] (Phase 2) | Multi-LOB emails link to multiple submissions |
| Classification | line_of_business: str | Adds lines_of_business: list[str] | Multi-LOB email detection |
| triggered_by_email | Optional[str] (email ID) | triggered_by: Optional[str] (typed prefix) | Supports email, user, and system triggers |
| Agent creation | Manual only | Auto-created by linker, dedup by email | Agents are first-class entities from submission #1 |
| Carrier creation | Manual only | Manual only (configured entity) | Prevents pollution from misclassified names |

---

## Migration Strategy

### Phase 1: Additive (No Breaking Changes)

All changes are backward-compatible. Deploy without coordinating frontend/backend.

| Action | Details |
|--------|---------|
| Add new fields with defaults | `submission_group_id`, `carrier_id`, `carrier_name`, `retail_agent_id`, `latest_assessment_id`, `premium_quoted`, `premium_bound`, `cross_channel_flags`, `is_stale`, `stale_since`, `resolution`, `resolved_at` -- all Optional/defaulted |
| Keep existing `premium` field | `premium: Optional[str]` stays alongside new `premium_quoted`/`premium_bound` during Phase 1. Both old and new coexist. |
| Create `assessments` collection | New collection, no existing data affected |
| Create `carriers` collection | Seed with 3 known carriers (USLI, Hiscox, Granada/GIC) |
| Create `agents` collection | Populate from distinct agent names/emails across submissions |
| Add indexes | `submission_group_id`, `carrier_id`, `retail_agent_id`, `latest_assessment_id` |
| Add `ASSESSED` to ProcessingStatus | Existing values unchanged |
| Add `lines_of_business` to Classification | New list field alongside existing `line_of_business` |

### Phase 2: Coordinated Cutover

Requires simultaneous deploy of migration script + updated backend + updated frontend + updated LLM prompts.

**Stage Migration Mapping:**

| Old Value | New Value | Notes |
|-----------|-----------|-------|
| `new` | `received` | Direct rename |
| `awaiting_info` | `awaiting_agent_info` | Direct rename |
| `with_carrier` | `awaiting_carrier_action` | Direct rename |
| `quoted` | `quoted` | Unchanged |
| `attention` + `declined` reason | `declined` | Decompose attention_reason |
| `attention` + `carrier_pending` reason | `awaiting_carrier_action` | Decompose attention_reason |
| `attention` + `stale`/`agent_urgent` reason | Recover from stage_history + set `is_stale: true` | See recovery algorithm below |

#### Attention Stage Recovery Algorithm (CRITICAL-3)

For submissions in `stage='attention'` with `reason='stale'` or `reason='agent_urgent'`, the actual stage they were in before being moved to attention must be recovered:

```python
def recover_attention_stage(submission):
    """For submissions in stage='attention' with reason='stale' or 'agent_urgent',
    recover the actual stage they were in before being moved to attention."""

    # Walk stage_history backwards to find the last non-attention stage
    for entry in reversed(submission['stage_history']):
        if entry['stage'] != 'attention':
            return map_old_stage_to_new(entry['stage'])

    # If no prior stage found (submission was created directly in attention),
    # default to 'received'
    return 'received'

def map_old_stage_to_new(old_stage):
    mapping = {
        'new': 'received',
        'awaiting_info': 'awaiting_agent_info',
        'with_carrier': 'awaiting_carrier_action',
        'quoted': 'quoted',
    }
    return mapping.get(old_stage, 'received')
```

**Edge case:** Submissions that entered attention multiple times -- always use the LAST non-attention stage in history (the `reversed()` iteration handles this correctly by finding the most recent one first).

#### triggered_by_email Field Rename (MODERATE-3)

- Old field: `triggered_by_email: Optional[str]` (contains email ObjectId or null)
- New field: `triggered_by: Optional[str]` (contains "email:\<id\>", "user:\<name\>", "system:auto_advance")
- Migration: for existing `stage_history` entries where `triggered_by_email` is not null, transform to `"email:{value}"`
- Reading code must check for both field names during the transition period (check `triggered_by` first, fall back to `triggered_by_email`)

#### Email.submission_id to submission_ids (AMBIGUITY-4)

- Change `Email.submission_id: Optional[str]` to `Email.submission_ids: list[str] = []`
- Migration: rename field, wrap existing string value in a list: `{"$rename": {"submission_id": "_old_submission_id"}}` then set `submission_ids: [_old_submission_id]` for non-null values
- All queries using `Email.submission_id` must update to `Email.submission_ids` (use `$elemMatch` or `$in` for lookups)
- This IS a breaking change requiring coordinated frontend/backend deploy

#### Premium String to Float Migration

- Parse string premium values to float: "$1,329" -> 1329.0, "$2,500.00" -> 2500.0
- Set `premium_quoted` from parsed value for submissions in `quoted` stage
- Remove old `premium: Optional[str]` field after migration verified
- Handle unparseable values by logging and leaving `premium_quoted` as null

**Migration script runs in 3 passes:**
1. Stage rename (new -> received, awaiting_info -> awaiting_agent_info, etc.)
2. attention_reason decomposition (split attention into declined, awaiting_carrier_action, or recovered stage using the recovery algorithm above)
3. Field renames and type migrations (triggered_by_email -> triggered_by, submission_id -> submission_ids, premium -> premium_quoted)

**stage_history dual-shape handling:** Old entries lack `ball_holder` and use `triggered_by_email`. Do not discard them. Backend must handle both shapes when reading history. New entries always include `ball_holder` and use `triggered_by`.

### Code Locations Requiring Updates (MODERATE-2)

All code locations that reference old stage names, attention_reason, or the old field names. Every location listed here must be updated as part of the Phase 2 coordinated deploy.

#### Backend (Python)

| File | Lines | What References Old Stages | Change Required |
|------|-------|---------------------------|----------------|
| `core/lob_config.py` | 84-113 | `compute_completeness()` stage switches: checks `stage == "attention"`, `reason == "declined"`, `reason == "carrier_pending"`, `stage == "quoted"` | Replace with new stage checks. See completeness changes below. |
| `agent/harness.py` | 106 | `should_generate_draft()` checks `sub["stage"] in ("new", "quoted", "attention")` | Replace with assessment-based check (see Assessment Pipeline section) |
| `agent/tools.py` | 256-260 | `update_submission_stage()` validates `valid_reasons = {"declined", "carrier_pending", "agent_urgent", "stale"}` | Remove attention_reason validation. Stage values become the new 8-stage enum. |
| `api/routes/submissions.py` | 39 | Board view `stages = ["new", "awaiting_info", "with_carrier", "quoted", "attention"]` | Replace with new 8 stages (excluding `closed` which goes to history view) |
| `api/routes/submissions.py` | 461 | `valid_stages = {"new", "awaiting_info", "with_carrier", "quoted", "attention"}` | Replace with new 8-stage set |
| `api/routes/submissions.py` | 209-243 | `generate_summary()` has stage+reason conditionals for attention/declined, attention/carrier_pending, attention/agent_urgent, attention/stale, quoted, awaiting_info | Rewrite with new stage names. `declined` is its own stage, `carrier_pending` is `awaiting_carrier_action`, etc. |
| `api/routes/submissions.py` | 321-356 | `get_submission_detail()` LOB requirements stage switch: `stage == "attention" and reason == "declined"`, `stage == "quoted"`, `stage == "attention" and reason == "carrier_pending"` | Replace with direct stage checks against new stages |
| `api/routes/stats.py` | 20-29 | `get_stats()` counts: `stage: "new"`, `stage: "awaiting_info"`, `stage: "attention"` | Replace with new stage names |
| `api/routes/stats.py` | 68-73 | `get_dashboard()` queue logic: `stage in ("awaiting_info", "with_carrier")` | Replace with `stage in ("awaiting_agent_info", "awaiting_carrier_action")` |
| `agent/skills/stage_detector.md` | entire file | Old 5-stage model, attention reasons, transition rules | **REMOVE** -- replaced by `situation_assessor.md` |
| `agent/skills/draft_generator.md` | entire file | References old stage-based draft decisions | **REWRITE** -- assessment-gated, new draft types |

#### Frontend (TypeScript/React)

| File | What References Old Stages |
|------|---------------------------|
| `ui/src/api/types.ts` | Stage type union, AttentionReason type, board response types |
| `ui/src/pages/SubmissionQueue.tsx` | Stage column definitions, stage colors, stage labels, board layout |
| `ui/src/pages/RiskRecord.tsx` | Stage display, attention_reason rendering, stage-based UI logic |
| `ui/src/pages/SystemIntelligence.tsx` | Stage breakdown display, stage counts |
| `ui/src/components/SubmissionCard.tsx` | Stage badge colors, attention_reason display, action queue logic |

All 5 frontend files must be updated in the same deploy as the backend migration.

#### compute_completeness() Changes with New Stages (MODERATE-2 detail)

```python
def compute_completeness(submission, extractions):
    stage = submission.get("stage", "received")

    # Declined: no requirements (no action needed)
    if stage == "declined":
        return {"total_fields": 0, "filled_fields": 0, "missing": [], "percentage": 100}

    # Closed: no requirements
    if stage == "closed":
        return {"total_fields": 0, "filled_fields": 0, "missing": [], "percentage": 100}

    # Quoted: check quote delivery requirements
    if stage == "quoted":
        required_fields = ["premium", "coverage_limits", "effective_date",
                          "carrier", "retail_agent_name"]
        required_documents = []

    # Awaiting carrier action: check carrier submission requirements
    elif stage == "awaiting_carrier_action":
        required_fields = ["carrier", "retail_agent_name", "retail_agency_name"]
        required_documents = []

    # Received, triaging, awaiting_agent_info, processing: full LOB requirements
    else:
        lob = submission.get("line_of_business", "")
        config = get_lob_config(lob)
        required_fields = config.get("required_fields", GENERIC_CONFIG["required_fields"])
        required_documents = config.get("required_documents", [])

    # ... rest of computation unchanged ...
```

---

## Known Limitations

| Limitation | Details | Source |
|------------|---------|--------|
| Multi-LOB email splitting | Mechanism specified: classifier outputs `lines_of_business` list, linker creates grouped submissions. Requires the classifier to correctly detect multi-LOB emails (accuracy not yet validated). Phase 2: `Email.submission_ids` replaces singular `submission_id`. | Ryan's wireframes |
| Outbound tracking | Only inbound to quote@ is monitored. Outbound inferred from reply chains and draft status (drafts approved/sent represent GIC outbound). Full outbound tracking requires sent-folder access from GIC. | business-model-synthesis.md -- System Failure #7 |
| Post-quote lifecycle | Limited data on bind rates and expiration timing. bind@ inbox is outside our data. | submission-lifecycle.md |
| USLI duplicate emails | USLI sends same quote 2-4 times. Deduplication strategy not yet defined. | email-workflow-patterns.md |
| Attachment significance | 10 of 12 email attachments can be signature images. Filtering strategy needed before extraction. | email-workflow-patterns.md |
| Email classification refinement | Some gic_info_request emails are miscategorized (Swyfft follow-ups, agent form requests). | email-workflow-patterns.md |

---

## Open Questions for JC

These gaps in the model need input from GIC. Ranked by impact on system accuracy.

1. **Golf cart program structure** -- Is it on Granada paper? Underwriting guidelines? Target volume? (business-model-synthesis.md -- Question #1)
2. **Management system API** -- Can we get access via Jeremiah? What data is available? (business-model-synthesis.md -- Question #2)
3. **Email workflow ownership** -- Is Maribel the sole processor? How is work assigned? (business-model-synthesis.md -- Question #3)
4. **Post-quote lifecycle** -- What happens after "quoted"? Bind process? (business-model-synthesis.md -- Question #4)
5. **Other direct-underwritten LOBs** -- Are roofing, pest control, or other portal LOBs also on Granada paper? (Design question -- do not assume)
6. **Carrier appetite rules** -- How does GIC decide USLI vs Hiscox for GL? (business-model-synthesis.md -- Question #8)
7. **NPP prefix resolution** -- Does NPP map to Commercial Property, Non Profit, or both? XPL/PCL overlap? (lob-catalog.md)
