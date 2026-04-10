---
ask: "Research message-driven and event-driven architecture patterns that match the four-primitive design: Entity, Message, Actor, Role"
created: 2026-04-03
workstream: product-vision
session: 2026-04-03-a
sources:
  - type: research
    description: "Web research across actor model implementations, event-driven architecture at scale, messaging infrastructure, work queue patterns, context enrichment, and real-world production systems"
  - type: local
    description: "Core primitives architecture artifact (2026-04-02), implementation plan, entity framework design, associate system design"
---

# Message & Actor Architecture Research

Research findings for the four-primitive OS design (Entity, Message, Actor, Role). Focused on practical implementation patterns for Python + MongoDB + FastAPI.

---

## 1. Actor Model Implementations — What Translates to This System

### The Frameworks

**Erlang/OTP** — The original. Each process (actor) has a mailbox (queue). Messages are pattern-matched. Supervisors restart failed actors. The "let it crash" philosophy means actors don't try to recover from errors; they die and get restarted clean. Decades of production use in telecom, banking, messaging systems. Key insight: the supervision tree is what makes it work at scale, not just the message passing.

**Akka (JVM)** — Erlang's patterns in Scala/Java. Typed actors with message routing. Supervision strategies: restart, stop, escalate, resume. Akka Cluster for distributed actors. Routers handle fan-out patterns (round-robin, broadcast, smallest-mailbox). Key insight: routers are first-class — they sit between senders and actors, distributing messages based on strategy.

**Microsoft Orleans** — The virtual actor ("grain") pattern. Actors are automatically activated on first message and deactivated when idle. No explicit lifecycle management. Each grain has its own message queue. Single-threaded execution per grain (no concurrency bugs inside a grain). The runtime handles placement, activation, and deactivation. Key insight: **grains process one message at a time, single-threaded**. This eliminates race conditions but means a slow message blocks the queue.

**Proto.Actor** — Cross-language (Go, C#, Kotlin, experimental Python). Supports both classical actors and Orleans-style virtual actors. Optimizes for locality — actors migrate toward the nodes that interact with them most. Key insight: the virtual actor pattern works across languages, suggesting it's architecturally sound regardless of runtime.

### What Translates to Python/MongoDB

The OS doesn't need a full actor runtime. The actors (humans and associates) already exist outside the message system. What translates:

| Actor Model Concept | OS Translation | Implementation |
|---|---|---|
| **Mailbox / queue per actor** | Each actor has a work queue | MongoDB collection with per-actor filtering, or dedicated queues |
| **Single-threaded processing** | One message at a time per actor | Natural for humans; for associates, process sequentially from queue |
| **Supervision** | Escalation on failure | Message re-routes to supervisor role after timeout/failure |
| **Virtual activation** | Associates spin up on message arrival | Associate invoked when queue has work, idle otherwise |
| **Message routing** | Role-based routing rules | Routing config determines which roles receive which message types |
| **Pattern matching** | Message type + entity type determines handler | Python match/case on message type |
| **Let it crash** | Associate failure = message returns to queue | Failed processing re-queues with retry count |

**The key realization: you don't need an actor framework.** The OS actors are humans (who process messages through UI) and associates (who are invoked by the system). The "actor runtime" is the queue + routing system, not a library. Orleans' insight is the most relevant: virtual actors that activate on demand and deactivate when idle. That IS the associate model.

### What NOT to Do

- Don't build an in-process actor runtime (Pykka, etc.) — the actors are external processes (humans, LLM agents), not threads
- Don't force single-threaded semantics on human actors — humans can work on multiple queue items
- Don't implement full supervision trees — escalation rules on messages are sufficient
- Don't try to make actors stateful in memory — state lives in entities (MongoDB), actors are stateless processors

---

## 2. Event-Driven Architecture at Scale — "Every Change Generates Events"

### The Practical Reality

The design says "every entity change generates messages." This is the Event Notification pattern. At scale, this creates known challenges:

**Event Storms** — A single operation can cascade. Binding a policy: Quote transitions -> message -> Policy created -> message -> Payment initiated -> message -> Commission calculated -> message -> Certificate generated -> message -> Notification sent. One user action = 6+ messages. If each message triggers further entity changes, the graph can explode.

**Mitigation strategies that work:**
1. **Distinguish internal vs. external events.** Entity state changes within a single service operation are internal. Only the final result publishes external messages. The `BindingService.bind()` method changes Quote, creates Policy, etc. internally. One message out: "binding.completed" with all the context.
2. **Batch/coalesce.** Multiple field changes on the same entity in the same operation = one message, not one per field. Debounce rapid changes.
3. **Priority tiers.** Not all messages are equal. State transitions > field updates > relationship changes. Route high-priority messages first.
4. **Load shedding.** Under extreme load, drop low-priority messages (field change notifications) while preserving critical ones (state transitions).

**Backpressure** — When message production exceeds consumption:
- **Queue depth monitoring** — alert when any actor's queue grows beyond threshold
- **Rate limiting at the source** — slow down message generation if queues are deep
- **Consumer groups / horizontal scaling** — multiple workers per role for high-volume message types
- **Dead letter handling** — messages that can't be processed after N retries go to a dead letter queue for manual review

**Filtering** — Not every actor needs every message. The routing rules (defined by Role) filter messages before they hit actor queues. This is the most important performance mechanism. Without it, every actor gets every message and must discard irrelevant ones.

### The Right Granularity

**Don't emit on every field change.** Emit on:
- Entity creation
- Entity deletion
- State machine transitions (the most important)
- Explicit business operations (@exposed methods)
- Relationship changes (entity linked/unlinked)

**Don't emit on:**
- Draft saves / partial updates (until explicitly "submitted")
- Internal computed field updates
- Read operations
- Timestamp updates

This keeps the message volume manageable. A busy insurance agency might process 100 submissions/day. Even with 10 messages per submission lifecycle, that's 1,000 messages/day — trivial for any messaging system. Scale concern is future-state with hundreds of organizations.

### The Outbox Pattern — Critical for MongoDB

The biggest risk in "every change generates events": the entity is saved to MongoDB but the message fails to publish (or vice versa). This creates inconsistency.

**The Transactional Outbox Pattern solves this:**
1. When an entity changes, write the message to an `outbox` collection in the SAME MongoDB transaction as the entity save
2. A separate process reads the outbox and publishes to the message broker
3. After successful publish, mark the outbox entry as sent

With MongoDB 4.0+ multi-document transactions and Beanie's session support, this is straightforward:

```python
async def save_with_events(entity, events):
    async with await motor_client.start_session() as session:
        async with session.start_transaction():
            await entity.save(session=session)
            for event in events:
                await outbox_collection.insert_one(event.dict(), session=session)
```

**Alternative: MongoDB Change Streams** — Watch the entity collections directly. When a document changes, the change stream emits an event. No outbox needed. But: change streams only tell you WHAT changed, not WHY. A state transition and a field update look the same. You lose business intent. This is fine for audit/replication but not for business routing.

**Recommendation: Outbox pattern for business messages, Change Streams as a safety net for audit/sync.**

---

## 3. Message Infrastructure — The Right Choice

### Option Analysis

#### RabbitMQ (already in stack — Amazon MQ)

**Strengths for this system:**
- Already operational (Amazon MQ), team knows it
- Sophisticated routing (topic exchanges, headers exchanges) — can route messages to queues based on message type, entity type, org, role
- Per-queue ordering guarantees
- Dead letter exchanges for failed messages
- Priority support (quorum queues: 2 levels; classic queues: up to 255 levels)
- Consumer acknowledgments with redelivery
- Durable queues survive restarts

**Weaknesses for this system:**
- **Per-actor queues don't scale.** Creating a RabbitMQ queue per actor (per human user, per associate) means potentially thousands of queues. RabbitMQ handles thousands of queues but each queue consumes memory and file handles. At 10K+ queues, cluster management becomes complex.
- Priority support in quorum queues is limited (high/normal only, though RabbitMQ 4.0 improved this)
- No built-in message aging/escalation — must be implemented in application logic
- No built-in "queue depth per consumer" visibility without management API polling

**Verdict: Good for inter-service messaging and fan-out. Not ideal as the per-actor work queue.**

#### Redis Streams

**Strengths:**
- Consumer groups with load balancing across consumers
- Message acknowledgment and pending message tracking
- Built-in support for consumer lag monitoring
- Very fast (sub-millisecond latency)
- XPENDING command shows unacknowledged messages per consumer — built-in queue depth visibility
- Already in the stack (Redis Cloud)

**Weaknesses:**
- No built-in priority queues (must use multiple streams + application logic)
- No built-in routing (application must decide which stream a message goes to)
- Memory-bound (all messages in RAM, though can be configured for disk)
- No dead letter queue natively
- Losing messages on Redis failure (unless using Redis Cluster with replication)

**Verdict: Fast and simple. Good for high-throughput scenarios. Lacks the routing sophistication needed for role-based message delivery.**

#### MongoDB Change Streams

**Strengths:**
- Zero additional infrastructure — events come from the database itself
- See entity changes in real-time with full document pre/post images
- Cursor-based — resume from any point after failure
- Works with existing Motor/Beanie stack
- Majority-committed guarantee (only see durable changes)
- Pipeline filtering (server-side, not all events sent to all consumers)

**Weaknesses:**
- **Change Streams are not a message broker.** They tell you what changed, not what the business intent was. An `update` operation doesn't carry "this was a state transition" vs. "this was a field correction."
- No consumer groups — each watcher is independent
- No acknowledgment/retry semantics — if your consumer crashes, you must track resume tokens yourself
- No routing — every watcher sees everything (filtered by pipeline, but no dynamic routing)
- Not designed for work queue semantics (ordering, priority, claiming)
- Performance impact on MongoDB cluster under heavy write load

**Verdict: Useful as an audit/sync mechanism. Not suitable as the primary message system. Lacks business intent, routing, and work queue semantics.**

#### NATS JetStream

**Strengths:**
- Lightweight, cloud-native, high performance
- Work queue retention policy — exactly-once consumption
- Consumer groups (pull-based consumers with load balancing)
- Subject-based routing (hierarchical subjects like `org.123.submission.created`)
- Persistence with configurable retention
- Python asyncio client (nats.py)
- Simple operational model

**Weaknesses:**
- Not in the current stack — new infrastructure to manage
- No built-in priority queues
- Less sophisticated routing than RabbitMQ (subject matching vs. header/topic exchanges)
- Smaller ecosystem and community than RabbitMQ or Redis
- Would need Amazon MQ replacement or self-hosted

**Verdict: Excellent messaging system, but adding new infrastructure without clear advantage over RabbitMQ (which is already running).**

### Recommended Approach: Hybrid — RabbitMQ for Routing + MongoDB for Queues

The insight: the system has TWO distinct messaging needs that no single technology handles well.

**Need 1: Event Bus (pub/sub + routing)** — When an entity changes, broadcast to interested parties. Role-based routing, fan-out, topic matching. **RabbitMQ does this excellently.**

**Need 2: Per-Actor Work Queues (task queue)** — Each actor has a prioritized, ordered queue of work items. Supports aging, escalation, claiming, completion. **MongoDB does this naturally.**

**The architecture:**

```
Entity change occurs
    → Outbox pattern: message written to outbox collection (same transaction)
    → Outbox publisher reads outbox, publishes to RabbitMQ
    → RabbitMQ routes based on message type + role routing rules
    → Route handlers write to actor work queues (MongoDB collection)
    → Actors read from their queue (UI for humans, trigger for associates)
```

**Why MongoDB for work queues:**
- Queues are just documents in a collection — `{actor_id, message_type, entity_ref, priority, status, created_at, claimed_at, completed_at, escalation_at, context}`
- Rich querying: "give me all unclaimed messages for actor X, ordered by priority then age"
- Atomic claim: `findOneAndUpdate({actor_id: X, status: "pending"}, {$set: {status: "claimed", claimed_at: now}})`
- Escalation: simple query for messages past their escalation threshold
- No additional infrastructure
- The queue IS the data model — queryable, indexable, aggregatable
- Queue depth per actor = simple count query
- Dashboard showing all queues = aggregation pipeline

**Why RabbitMQ for the event bus:**
- Already running (Amazon MQ)
- Topic exchanges handle role-based routing: `submission.state_changed` routes to queues bound with routing keys matching role subscriptions
- Fan-out when multiple roles need the same message
- Durable delivery guarantees
- Decoupled from the work queue — the bus is the transport, the queue is the destination

This is not novel. It's the pattern used by most production systems: a message broker for transport + a database for stateful work queues. The broker handles delivery; the database handles state.

---

## 4. Work Queue Patterns — Per-Actor Queues

### The Queue as a MongoDB Collection

```python
class WorkQueueItem(Document):
    """A message in an actor's work queue."""
    
    org_id: ObjectId                    # Multi-tenant scoping
    actor_id: str                       # Who this message is for
    actor_role: str                     # Role that caused routing
    
    # Message content
    message_type: str                   # "submission.state_changed", "task.assigned"
    entity_type: str                    # "Submission", "Policy"
    entity_id: ObjectId                 # Reference to the entity
    operation: str                      # "created", "transitioned", "updated"
    summary: str                        # Human-readable summary
    
    # Context (enriched — see section 5)
    context: dict                       # Pre-resolved related entity data
    
    # Queue management
    priority: int = 5                   # 1 (critical) to 10 (background)
    status: str = "pending"             # pending, claimed, completed, failed, escalated
    
    # Timing
    created_at: datetime
    claimed_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Escalation
    escalation_at: Optional[datetime]   # When to escalate if not processed
    escalation_target: Optional[str]    # Actor/role to escalate to
    escalation_count: int = 0           # How many times escalated
    
    # Retry tracking
    attempt_count: int = 0
    max_attempts: int = 3
    last_error: Optional[str]
    
    class Settings:
        name = "work_queue"
        indexes = [
            # Primary query: get my pending work, highest priority first, oldest first
            [("org_id", 1), ("actor_id", 1), ("status", 1), ("priority", 1), ("created_at", 1)],
            # Escalation sweep: find messages past their escalation time
            [("status", 1), ("escalation_at", 1)],
            # Metrics: queue depth by role
            [("org_id", 1), ("actor_role", 1), ("status", 1)],
            # Cleanup: completed messages older than retention
            [("status", 1), ("completed_at", 1)],
        ]
```

### Queue Operations

**Claim a message (atomic):**
```python
item = await WorkQueueItem.find_one_and_update(
    {"actor_id": actor_id, "status": "pending"},
    {"$set": {"status": "claimed", "claimed_at": datetime.utcnow()}},
    sort=[("priority", 1), ("created_at", 1)]  # Highest priority, oldest first
)
```

**Complete a message:**
```python
await item.set({"status": "completed", "completed_at": datetime.utcnow()})
```

**Fail and retry:**
```python
if item.attempt_count < item.max_attempts:
    await item.set({
        "status": "pending",
        "attempt_count": item.attempt_count + 1,
        "last_error": str(error),
        "claimed_at": None
    })
else:
    await item.set({"status": "failed", "last_error": str(error)})
```

**Escalation sweep (runs on interval):**
```python
overdue = WorkQueueItem.find({
    "status": "pending",
    "escalation_at": {"$lt": datetime.utcnow()}
})
async for item in overdue:
    await item.set({
        "actor_id": item.escalation_target,
        "escalation_count": item.escalation_count + 1,
        "escalation_at": calculate_next_escalation(item)
    })
```

### Priority Aging Pattern

Messages should not sit at the bottom of the queue forever. Priority aging increases a message's effective priority as it ages:

```python
def effective_priority(item: WorkQueueItem) -> float:
    """Lower number = higher priority. Age boosts priority."""
    age_hours = (datetime.utcnow() - item.created_at).total_seconds() / 3600
    age_boost = min(age_hours * 0.5, 4)  # Max 4 priority levels boost over 8 hours
    return item.priority - age_boost
```

This can be implemented as a computed sort in the query, or by periodically updating priority on aging messages.

### Comparison with Dedicated Queue Systems

| Feature | MongoDB Queue | BullMQ (Redis) | Celery (RabbitMQ) |
|---|---|---|---|
| Priority | Full (any number of levels) | Yes (limited) | Yes (via separate queues) |
| Ordering | Full control via sort | FIFO within priority | FIFO per queue |
| Aging/escalation | Custom queries on timestamps | Custom (delayed jobs) | Custom (ETA/countdown) |
| Per-actor queues | Filter by actor_id | Separate queue per actor | Separate queue per actor |
| Queue depth visibility | Simple count query | Redis commands | Management API |
| Rich querying | Full MongoDB query language | Limited (Redis) | Limited |
| Additional infrastructure | None | Redis | RabbitMQ (already have) |
| Processing guarantee | findOneAndUpdate atomic | Redis transactions | AMQP acks |

**The MongoDB queue wins for this system because:**
1. The queue items ARE data — they should be queryable, reportable, aggregatable
2. Per-actor filtering is a query, not a separate queue (avoids thousands of queues)
3. Priority, aging, and escalation are just fields and queries
4. No additional infrastructure
5. The dashboard showing queue state is just a MongoDB query
6. History (completed items) stays in the same collection for analytics

---

## 5. Context Enrichment on Messages

### The Problem

When a message says "Submission SUB-001 transitioned to triaged," the actor receiving it needs context: What's in the submission? Who's the insured? What carrier? What product? Without context, the actor (human or associate) must make round-trips to fetch data before they can act.

### Three Patterns

**Pattern A: Thin Events (Event Notification)**
- Message contains only: entity_id, entity_type, operation, timestamp
- Consumer fetches what it needs via API/CLI
- Pro: Minimal message size, always fresh data
- Con: N+1 query problem, requires source to be available, slow for associates

**Pattern B: Fat Events (Event-Carried State Transfer)**
- Message contains the full entity state + related entities
- Consumer has everything it needs
- Pro: Self-contained, no round-trips
- Con: Large messages, stale data risk, coupling between producer and consumer schema

**Pattern C: Enriched Events (the hybrid)**
- Message generated as thin event
- Enrichment step resolves related entities based on routing destination's needs
- Consumer receives message with relevant context attached
- Pro: Right-sized context per consumer, decoupled enrichment
- Con: Enrichment adds latency, must define what to resolve per role

### Recommendation: Pattern C — Enriched Events with Role-Based Context Rules

The OS already has the concept of "context scoping" per role (from the core primitives design). Use this same mechanism to define what context to attach to messages:

```python
# Role defines what context its actors need
role_context_rules = {
    "intake_associate": {
        "submission.state_changed": {
            "include": ["submission", "insured", "carrier", "product"],
            "depth": 1,  # Resolve one level of relationships
            "history": 5  # Last 5 interactions
        }
    },
    "underwriter": {
        "submission.state_changed": {
            "include": ["submission", "insured", "carrier", "product", "quote"],
            "depth": 2,
            "history": 10
        }
    }
}
```

**The enrichment happens at routing time** — when the RabbitMQ consumer receives a thin event and writes to the actor's work queue, it resolves the context based on the target role's rules and attaches it to the work queue item.

```
Entity changes → Thin event to RabbitMQ
    → Router receives event
    → For each target role:
        → Resolve context per role's context rules
        → Write enriched work queue item to MongoDB
```

This means:
- The event bus carries thin events (fast, small)
- Each actor's work queue item has pre-resolved context (ready to act on)
- Different roles get different context for the same event
- Associates receive rich context — can reason immediately without CLI round-trips
- Humans see full context in their dashboard without page loads

### Context Freshness

Pre-resolved context can become stale if the related entity changes between enrichment and processing. For most insurance workflows, this is acceptable — if a contact's phone number changes between message creation and processing, the actor will see the old number but the entity itself has the new one. For critical fields, the actor can always re-fetch.

For associates: the context is a starting point for reasoning. The associate still has CLI access to fetch current data if needed. Think of it like Claude Code's CLAUDE.md — pre-loaded context that gets the agent started, with tools available for deeper exploration.

---

## 6. Real-World Systems Using This Pattern

### Systems That Match

**Temporal** — Workflows as durable state machines. Activities (actors) process tasks from queues. Task queues per workflow type. Exactly-once execution. Temporal's insight: separate the workflow definition (what happens) from the execution (how it's scheduled and retried). **Relevant lesson: the OS's "emergent workflows from entity state machines" is good for simple flows, but complex flows benefit from explicit orchestration. Temporal defers this decision correctly.**

**Orleans (Halo, Azure services)** — Virtual actors with per-grain queues, single-threaded execution. Used in production for Xbox services handling millions of concurrent game sessions. **Relevant lesson: the virtual actor pattern (activate on message, deactivate when idle) maps directly to how associates should work.**

**Uber Cadence/Temporal** — Started at Uber for trip lifecycle management. Entities (trips, drivers, riders) with state machines. Events routed to workers. Per-entity message ordering. **Relevant lesson: even Uber's massive scale used explicit workflow orchestration, not purely emergent workflows.**

**Banking Systems (ING, others)** — Event-driven with strict ordering, exactly-once processing, audit trails. Use outbox pattern extensively. CQRS for read models. **Relevant lesson: in regulated environments, the outbox pattern and idempotent consumers are not optional.**

**Salesforce Flow / ServiceNow** — Entities (records) with state machines (record types, stages). Automation rules fire on record changes. Assignments route to queues per user. Approval processes are messages routed through role hierarchies. **Relevant lesson: this is the closest analog to the OS design. It works. The pitfalls are: rule explosion (too many routing rules), cascade storms (one change triggers 50 automations), and debugging opacity (hard to trace why something happened).**

### What Worked

1. **Keeping the event bus separate from work queues.** Every successful system separates the transport (how messages get from A to B) from the work management (priority, ordering, claiming, completion).

2. **Explicit workflow definitions for complex processes.** Emergent workflows work for simple chains (A -> B -> C). For anything with branching, parallelism, timeouts, or error handling, an explicit workflow definition is needed.

3. **Idempotent message processing.** Every handler must be safe to execute twice. Messages WILL be delivered more than once (broker retry, consumer crash, network partition). Design for it from day one.

4. **Correlation IDs / tracing.** When message A generates messages B, C, D which generate E, F, G... you need a correlation ID that traces back to the original trigger. Without this, debugging is impossible.

5. **Rate limiting on cascade depth.** Set a maximum cascade depth (e.g., 10 hops). If a message generates a message that generates a message... past 10 levels, stop and alert. This prevents infinite loops.

### What Didn't Work / Pitfalls

1. **"Every field change is an event."** Systems that emit events on every field update drown in noise. The insurance domain changes slowly (submissions take hours/days, not milliseconds). Emit on business-meaningful changes only.

2. **No distinction between commands and events.** Commands ("create this policy") and events ("policy was created") are fundamentally different. Commands can fail and be rejected. Events are facts. Mixing them leads to architectures that look event-driven but behave like synchronous RPC.

3. **Debugging distributed message flows.** The number one complaint in production event-driven systems. You MUST build observability from day one: correlation IDs, message flow visualization, dead letter inspection, replay capability.

4. **Schema evolution.** Message schemas change over time. Old messages in queues may not match new consumers. Use versioned schemas or be very careful with backward-compatible changes only.

5. **"Just add another event handler."** Event handler sprawl is the EDA equivalent of spaghetti code. Every handler is invisible coupling. Document handlers, test them, and review additions carefully.

6. **Overloading the message system.** Using the same message broker for real-time notifications, background processing, analytics events, and audit logging. Different concerns need different channels or at minimum different priority tiers.

---

## Summary Recommendations

### Architecture

| Decision | Recommendation | Rationale |
|---|---|---|
| **Actor runtime** | Don't build one. Actors are external (humans, associates). | The "runtime" is the queue + routing system. |
| **Event bus** | RabbitMQ (already have it) | Routing, fan-out, durability. Keep it as transport. |
| **Work queues** | MongoDB collection | Per-actor filtering, priority, aging, escalation, queryable. No new infrastructure. |
| **Event publishing** | Outbox pattern (same transaction as entity save) | Guarantees consistency between entity state and published events. |
| **Context enrichment** | Enrichment at routing time, role-based context rules | Right-sized context per consumer. Associates get rich context. |
| **Message granularity** | Emit on state transitions + @exposed operations, not every field change | Prevents event storms while capturing business intent. |
| **Workflow orchestration** | Emergent for simple chains, explicit Workflow entity for complex flows | Both patterns coexist. Start emergent, add explicit when needed. |

### Build Order

1. **Outbox pattern on Entity base class** — Every entity save writes to outbox in same transaction
2. **Outbox publisher** — Background process reads outbox, publishes to RabbitMQ
3. **Work queue collection + operations** — The MongoDB queue with claim/complete/escalate
4. **Router** — RabbitMQ consumer that reads routing rules (from Role) and writes to work queues with enriched context
5. **Escalation sweep** — Periodic job that re-routes overdue messages
6. **Queue API** — Endpoints for actors to read their queue, claim items, mark complete
7. **Associate trigger** — When a message arrives in an associate's queue, invoke the associate

### What to Avoid

- Don't create a RabbitMQ queue per actor (thousands of queues)
- Don't emit events on every field change (event storms)
- Don't skip the outbox pattern (entity/event inconsistency)
- Don't use MongoDB Change Streams as the primary event mechanism (loses business intent)
- Don't build an in-process actor framework (the actors are external)
- Don't skip correlation IDs (debugging will be impossible)
- Don't assume exactly-once delivery (always design idempotent handlers)
