---
ask: "How do humans and associates share the same queue while getting different execution engines? How does gradual rollout work?"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude refining Temporal integration — unified queue, associates as employees"
  - type: review
    description: "Temporal integration validation agent findings"
  - type: artifact
    description: "2026-04-09-temporal-integration-architecture.md"
---

# Unified Queue + Temporal Execution

## The Principle: Associates Are Employees

The distinction between human and associate should not be baked into the infrastructure. Both are actors with roles. Both see the same queue. Both claim the same work. Both can be assigned to the same entities. The system doesn't care whether the actor is human or automated.

A task assigned to an associate may be reassigned to a human. A task that starts with a human may be routed to an associate. When rolling out gradually, humans perform work first, then associates take over — same role, same queue, different actor.

## The Design: One Queue, Two Execution Modes

**The queue is ALWAYS MongoDB. For everyone.** Temporal is the execution engine that associates use to PROCESS items from the shared queue.

```
Entity save → outbox record (same MongoDB transaction)
→ Outbox poller reads record, evaluates watches
→ Writes to MongoDB message_queue (ALWAYS, regardless of who has the role)
→ If role has associate actors: ALSO starts a Temporal workflow
```

The queue is the universal inbox. Both humans and associates see it. The arbitration point is the **claim** — same `findOneAndUpdate`, same message, whether JC claims it or the Classifier Associate claims it.

What happens AFTER claiming is different:
- **Human claims** → processes via UI/CLI interactively → marks complete
- **Associate claims** → Temporal workflow executes activities (CLI, LLM, rules) → marks complete

That's an implementation detail of the actor, not the queue.

## How Associates Pick Up Work

When the outbox poller writes to the message_queue, it checks: does this role have associate actors? If yes, start a Temporal workflow. The workflow's first activity is: **claim the message from the queue.**

```
Temporal Workflow: ProcessMessageWorkflow
  Activity 1: Claim message from MongoDB message_queue (findOneAndUpdate)
    → Already claimed by someone else? Exit gracefully.
    → Claimed successfully? Proceed.
  Activity 2: Load entity context
  Activity 3: Execute skill (kernel capability --auto, LLM if needed)
  Activity 4: Save entity changes
  Activity 5: Mark message complete
```

If someone else already claimed the message (human got there first), the workflow exits. No conflict. No wasted work.

If Temporal is down, items stay in the queue. Humans claim them. Nothing is lost.

If the associate fails mid-processing, the message returns to the queue (visibility timeout). A human can claim it. Or the associate retries (Temporal handles this).

## The Queue

The MongoDB `message_queue` collection serves ALL actors:

```
{
  org_id: "gic",
  entity_type: "Email",
  entity_id: "EMAIL-001",
  event: "created",
  target_role: "classifier",
  status: "pending",          // pending → processing → completed / failed
  claimed_by: null,           // actor ID when claimed
  claimed_at: null,
  visibility_timeout: null,   // stuck recovery
  priority: "normal",
  context: {                  // enriched entity data
    email: { from: "agent@usli.com", subject: "GL Quote...", ... },
    extractions: [ ... ]
  },
  correlation_id: "trace-abc-123",   // = OTEL trace ID
  causation_id: null,
  depth: 0,
  created_at: "2026-04-09T14:00:00Z"
}
```

**Human actors** query the queue via UI: `GET /api/queue?role=underwriter&status=pending`
**Associate actors** claim via Temporal workflow: `findOneAndUpdate({target_role: "classifier", status: "pending"}, {$set: {status: "processing", claimed_by: "associate-001"}})`

Same collection. Same schema. Same claiming mechanism. Same visibility.

## Gradual Rollout (GIC Example)

### Week 1: Humans Only
```bash
indemn actor add-role jc --role classifier
```
Emails arrive → message_queue → JC sees them in his UI → claims → classifies manually.
No Temporal workflows start (no associates on the role).

### Week 2: Associate Added Alongside Human
```bash
indemn associate create --name "Email Classifier" --role classifier --skill email-classification --mode hybrid
```
Emails arrive → message_queue → BOTH JC and the associate see them.
Temporal workflow starts, claims the message, classifies it automatically.
JC sees items being processed. If the associate gets one wrong, JC corrects it.
If the associate can't handle one (needs_reasoning, low confidence), it goes back to the queue. JC claims it.

### Week 3: Associate Takes Over
```bash
indemn actor remove-role jc --role classifier
```
The associate handles all classification. JC focuses on underwriting.
No infrastructure change. Same queue. Same messages. Different actor on the role.

### Week 4: Escalation
A weird email the associate can't classify. The associate marks it needs_review.
A new message appears in the underwriter queue (JC's role).
JC reviews it manually. The system churns.

**At no point does the infrastructure change. The only thing that changes is who has which role.**

## Why This Is Better Than Split Routing

The previous design routed to MongoDB for humans and Temporal for associates. That broke when:
- A task assigned to an associate needs to be reassigned to a human (different system)
- Gradual rollout requires infrastructure changes, not just role changes
- An associate fails and the task should fall to a human (cross-system fallback)
- You want to see ALL pending work in one place regardless of who will process it

The unified queue solves all of these. The queue is one system. The execution differs by actor type. Work flows between humans and associates by changing role assignments, not by changing infrastructure.

## Associates as Employees

In this model, the associate truly is an employee:

| Trait | Human | Associate | Same? |
|-------|-------|-----------|-------|
| Has a role | ✓ | ✓ | ✓ |
| Sees the queue | ✓ (via UI) | ✓ (via Temporal workflow) | ✓ |
| Claims work | ✓ (findOneAndUpdate) | ✓ (same mechanism) | ✓ |
| Can be assigned to entities | ✓ (actor reference in context) | ✓ (same) | ✓ |
| Can be added/removed from roles | ✓ (CLI) | ✓ (CLI) | ✓ |
| Work is visible in queue history | ✓ (message_log) | ✓ (same collection) | ✓ |
| Work is traced | ✓ (OTEL) | ✓ (OTEL + Temporal) | ✓ |
| **How they process** | UI/CLI interactively | Temporal workflow | **Different** |

The ONLY difference is execution mode. Everything else is identical.

## The Architecture

```
Entity save → outbox (same MongoDB txn)
    │
    ▼
Outbox poller
    │ evaluates watches (cached, sub-millisecond)
    │
    ├──────────────────────────────┐
    ▼                              ▼
message_queue                 If role has associates:
(MongoDB)                     start Temporal workflow
    │                              │
    │                              ▼
    │                         Workflow Activity 1:
    │                         claim from message_queue
    │                              │
    │                         ┌────┴────┐
    │                         │ Claimed │ Already taken?
    │                         │         │ → exit
    │                         ▼         
    │                    Activity 2-N:
    │                    CLI, LLM, rules
    │                         │
    ▼                         ▼
Human sees it            Associate
in their UI              processes it
    │                         │
    ▼                         ▼
Human claims             Both produce:
and processes            entity changes
    │                    → outbox
    ▼                    → watches
Both produce:            → message_queue
entity changes           → system churns
→ outbox → watches → message_queue → system churns
```

## What Lives Where

| Component | Where | Why |
|-----------|-------|-----|
| Entity framework | MongoDB (Beanie, Pydantic) | Data + state machines + CLI/API |
| Work queue | MongoDB message_queue | Universal — humans + associates see same items |
| Queue history | MongoDB message_log | Completed items, audit, reporting |
| Watch evaluation | Outbox poller (regular Python) | Cached, fast, not in Temporal |
| Associate execution | Temporal workflows | Durable, crash recovery, retries, OTEL |
| Human interaction | UI + CLI against MongoDB | Rich queries, filtering, context |
| Scheduled tasks (simple) | OS scheduler / cron | Already transactional |
| Scheduled tasks (multi-step) | Temporal Schedules | Crash recovery for multi-step |
| Audit trail | MongoDB changes collection | Same transaction as entity save |
| Observability | OTEL (entity + Temporal + LLM) | One trace for everything |

## Temporal's Role (Specific)

Temporal handles ONLY the execution of associate work:
- **Durable execution:** if worker crashes, replay from last completed activity
- **Timeouts:** if LLM hangs, kill after configured timeout
- **Retries:** if CLI command fails, retry with backoff
- **Saga compensation:** if multi-entity operation fails partway, compensate
- **OTEL tracing:** automatic spans for workflow + activity execution

Temporal does NOT handle:
- Queue management (that's MongoDB)
- Watch evaluation (that's the outbox poller)
- Human task management (that's MongoDB + UI)
- Entity storage (that's MongoDB)
- Rule evaluation (that's kernel capabilities)

## Temporal Cloud

- **Cost:** $100/month (Essentials, 1M actions included)
- **Outage impact:** Automated processing pauses. Outbox accumulates. Human actors continue via MongoDB. When Temporal recovers, backlog processes. Nothing lost.
- **OTEL integration:** Native TracingInterceptor — all workflow/activity spans join the entity trace automatically

## The Outbox Poller Detail

The outbox poller is the bridge between the entity framework and everything downstream:

1. Read pending outbox records (from MongoDB, in batch)
2. For each record: evaluate cached watches for this org + entity type + event
3. For each matching watch: write to message_queue (always)
4. For roles with associates: start Temporal workflow
5. Mark outbox records as processed
6. If step 4 fails (Temporal down): don't mark as processed, retry next poll

The poller runs as a lightweight process. Poll interval configurable (default 1 second). At-least-once delivery guaranteed by the outbox pattern.

**Optimization:** Evaluate watches in the entity save path (inside the transaction). The outbox record then already says "target_role: classifier, has_associates: true." The poller just dispatches — no evaluation needed. This eliminates the "evaluate differently on retry" concern and moves the fast, cached evaluation into the save transaction where it adds microseconds.
