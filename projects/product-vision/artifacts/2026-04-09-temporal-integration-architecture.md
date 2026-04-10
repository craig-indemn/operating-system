---
ask: "How does the OS architecture change with Temporal integrated? What replaces what, what stays, how does GIC work?"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: research
    description: "Temporal.io deep research — architecture, Python SDK, observability, versioning, production use cases"
  - type: conversation
    description: "Craig and Claude designing Temporal integration into OS kernel"
---

# Temporal Integration Architecture

## Why Temporal

The OS was building durable execution primitives piecemeal: message queue, claiming, visibility timeouts, dead letters, retry, crash recovery, multi-entity atomicity. Temporal provides all of these as a cohesive, battle-tested system ($100/month managed). Major production users include OpenAI (Codex), Replit (agent orchestration), Netflix, DoorDash, Snap.

Key value: we stop building distributed systems plumbing and focus on the domain — entities, capabilities, skills, and workflows.

## What Temporal Replaces

| We Were Going to Build | Temporal Provides |
|---|---|
| MongoDB `message_queue` collection | Task queues (managed) |
| `findOneAndUpdate` claiming logic | Automatic task dispatch to workers |
| Visibility timeout sweep | Start-to-Close + Heartbeat timeouts |
| Dead letter collection + retry logic | Retry policies + failed workflow states |
| Message_queue + message_log split | Temporal stores execution history internally |
| Batch transaction for multi-entity atomicity | Saga pattern — workflow wraps multiple activities |
| Cron + CLI for scheduled tasks | Temporal Schedules (built-in cron) |
| Custom crash recovery | Automatic replay from event history |
| Custom correlation ID tracking | Native OTEL tracing integration |

## What Stays Exactly the Same

- **Entity framework** (Beanie, Pydantic, MongoDB) — all entity definitions, state machines, computed fields
- **Entity CLI/API** (FastAPI, Typer) — auto-generated, unchanged
- **Kernel capabilities** (auto-classify, fuzzy-search, etc.) — same code, called from Temporal activities
- **Skills** (markdown) — same format, same role
- **Roles** (permissions + watches) — same concept, same CLI
- **OTEL** — Temporal has native OTEL integration, everything joins into one trace

## The New Flow

```
Entity save → (same MongoDB txn) write outbox record
→ Outbox poller reads record, evaluates watches
→ For each matching watch: signal/start Temporal workflow
→ Temporal dispatches to worker
→ Worker executes activities (CLI commands, LLM calls, rule evaluation)
→ Activities change entities → more outbox records → more workflows
→ System churns
```

### Outbox Pattern for Reliability

Entity save and outbox record are in the same MongoDB transaction. No event is ever lost between entity save and Temporal notification.

```
Entity.save() + outbox.insert() → one MongoDB transaction (atomic)
Outbox poller → reads pending records → evaluates watches → signals Temporal → marks record processed
```

If the poller crashes after reading but before signaling Temporal, the record remains in the outbox. Next poll picks it up. At-least-once delivery guaranteed.

## GIC Pipeline on Temporal

Each actor invocation is a Temporal workflow. Routing between actors is still watches. The system churns: entity changes → watches → workflows → entity changes.

### Step 1: Email Sync (Temporal Schedule)
```
Temporal Schedule: every 60s → start EmailSyncWorkflow
  → Activity: indemn email fetch-new (polls Outlook, creates Email entities)
  → Email entities saved → outbox → watches evaluate
```

### Step 2: Watch → Extractor Workflow
```
Email:created WHERE has_attachments → extractor watch matches
  → Temporal starts ExtractPDFsWorkflow(email_id)
    → Activity: download attachments from S3
    → Activity: OCR + LLM extraction → create Extraction entities
    → If worker crashes → Temporal replays, skips completed activities
  → Extraction entities saved → outbox → watches
```

### Step 3: Watch → Classifier Workflow
```
Extraction:created → classifier watch matches
  → Temporal starts ClassifyEmailWorkflow(email_id)
    → Activity: indemn email classify --auto (kernel rules)
    → If needs_reasoning: Activity: LLM call with skill
    → Activity: save classification on Email
  → Email.classification set → outbox → watches
```

### Step 4: Watch → Linker Workflow
```
Email:classification_set → linker watch matches
  → Temporal starts LinkEmailWorkflow(email_id)
    → Activity: indemn email link --auto (reference match, fuzzy search)
    → If needs_reasoning: Activity: LLM picks best match
    → Activity: create Submission (if new)
    → Activity: update Email (link to submission)
    → Both in same workflow — crash recovery via replay
  → Submission created → outbox → watches
```

### Step 5: Watch → Assessor Workflow
```
Submission:created → assessor watch matches
  → Temporal starts AssessSubmissionWorkflow(submission_id)
    → Activity: completeness check (kernel capability)
    → Activity: LLM situation assessment
    → Activity: create Assessment entity
    → Activity: update Submission stage
  → Assessment with needs_review=true → outbox → watches
```

### Step 6: Watch → Human Review (Long-Running Workflow)
```
Assessment:created WHERE needs_review=true → underwriter watch matches
  → Temporal starts HumanReviewWorkflow(assessment_id)
    → Workflow WAITS for signal (indefinitely)
    → JC sees it in his queue (UI queries Temporal for pending workflows)
    → JC clicks "Approve" → UI signals Temporal workflow
    → Workflow resumes → Activity: update Submission stage
    → If no action in 48 hours → workflow timer → escalation
```

### Multi-Entity Atomicity Solved
The linker workflow creates a Submission AND updates an Email. Both are activities in the same workflow. If the worker crashes after creating the Submission but before updating the Email, Temporal replays: sees Submission activity completed (skips), executes Email update. No orphaned state.

## Human-in-the-Loop via Temporal Signals

When a human needs to decide (approve draft, review assessment, reassign submission):
1. Watch matches → Temporal workflow starts
2. Workflow waits for signal (human hasn't looked yet)
3. Human's queue = Temporal query for pending workflows by role
4. Human decides → UI signals workflow
5. Workflow resumes → executes remaining activities
6. Timer-based escalation if no action

The workflow tracks: when created, when human notified, when decided, duration. All in execution history. All OTEL-traced.

## Scheduled Tasks via Temporal Schedules

```bash
indemn schedule create --name email-sync --workflow EmailSyncWorkflow --cron "*/1 * * * *"
indemn schedule create --name stale-check --workflow StaleCheckWorkflow --cron "0 * * * *"
indemn schedule create --name weekly-summary --workflow WeeklySummaryWorkflow --cron "0 8 * * 1"
```

Same infrastructure. Visible, pausable, with full execution history.

## Unified Observability (OTEL)

Temporal's TracingInterceptor creates OTEL spans for all workflow and activity executions. Combined with entity-level and LLM-level OTEL spans, everything is ONE trace:

```
Trace: abc-123
├── Entity: Email created [3ms]
│   └── Outbox: record written
├── Outbox poller: watch evaluated → classifier match [0.5ms]
├── Temporal: ClassifyEmailWorkflow started
│   ├── Activity: indemn email classify --auto [1.5ms]
│   │   └── Rule evaluation: 47 rules, usli-quote matched [0.2ms]
│   └── Activity: save classification [4ms]
├── Entity: Email classification set [4ms]
│   └── Outbox: record written
├── Outbox poller: watch evaluated → linker match [0.3ms]
├── Temporal: LinkEmailWorkflow started
│   ├── Activity: indemn email link --auto [8ms]
│   │   ├── Pattern extraction [0.5ms]
│   │   └── Fuzzy search [3ms]
│   ├── Activity: create Submission [5ms]
│   └── Activity: update Email [3ms]
└── ... (cascade continues, all in same trace)
```

`indemn trace entity EMAIL-001` queries OTEL data. `indemn trace cascade --id abc-123` shows the full tree. Rule evaluation traces, LLM calls, Temporal workflows — all nested spans in one trace.

## Workflow Versioning

Temporal's built-in versioning handles deployment:
- Deploy new classifier logic → new workers with new code
- In-flight emails continue with old version (Temporal routes to old workers)
- New emails use new version
- Once old workflows complete → decommission old workers

For rule versioning: rules are configuration data. Next workflow execution picks up new rules. In-flight workflows that already evaluated rules continue with their results (in Temporal event history).

## The Kernel With Temporal

| Kernel Component | What It Does |
|---|---|
| **Entity framework** | Data structure, state machine, CLI/API, skills |
| **Kernel capabilities** | auto-classify, fuzzy-search, rule evaluation — called from Temporal activities |
| **Watch system** | Entity changes → which Temporal workflows to start |
| **Outbox** | Reliable entity change → Temporal signal delivery |
| **Roles + permissions** | Access control + watch definitions |
| **OTEL** | Everything instrumented — entity, watch, Temporal, LLM, CLI — one trace |

| Temporal Component | What It Does |
|---|---|
| **Task queues** | Dispatch work to workers |
| **Workflow execution** | Durable multi-step processing with crash recovery |
| **Activity management** | Timeouts, retries, heartbeats |
| **Signals** | Human-in-the-loop (wait for decisions, approvals) |
| **Schedules** | Cron-like recurring workflows |
| **Versioning** | Deploy new logic while old executions complete |
| **History** | Complete audit trail of every execution |

## Cost Projection

| Scale | Actions/Month | Temporal Cost | Notes |
|-------|--------------|---------------|-------|
| 1 org, 1K emails/day | 750K | $100 (included) | MVP |
| 10 orgs, 1K emails/day each | 7.5M | ~$375 | Early growth |
| 100 orgs, 1K emails/day each | 75M | ~$3,750 | Scale |
| 100 orgs, 10K emails/day each | 750M | ~$37,500 | Large scale |

At large scale, Temporal cost is meaningful but proportional to the value delivered. Self-hosting becomes an option if cost is a concern (but adds operational overhead).

## Open Questions for Validation

1. **One workflow per actor vs. one workflow per pipeline** — per-actor preserves the "system churning" model (watches between steps). Per-pipeline is simpler but makes the orchestration explicit, not emergent.
2. **Human queue as Temporal query** — practical? Performance at scale?
3. **Outbox poller vs. MongoDB Change Streams** — which is better for entity change → Temporal signal?
4. **Simple operations** (stale check = one query) — is Temporal overhead justified?
5. **Temporal as single point of failure** — if Temporal Cloud has an outage, no workflows execute (entity saves still work)
