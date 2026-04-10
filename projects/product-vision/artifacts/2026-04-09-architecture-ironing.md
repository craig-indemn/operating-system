---
ask: "Systematically find and resolve places where the architecture treats one thing as two things, or has hidden inconsistencies"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude working through seven architectural issues identified by pattern-matching for 'two categories when conceptually it should be one'"
---

# Architecture Ironing — Seven Issues Resolved

## The Pattern We're Looking For

The associate/person routing split was caught because it violated a core principle: associates are employees, not a different category. The pattern to find: **any place where the architecture treats something as two categories when conceptually it should be one.**

---

## Issue #7: Skill vs. Workflow Orchestration (HIGH RISK)

**Problem:** The skill (markdown) says "do step 1, then step 2." The Temporal workflow defines Activity 1, Activity 2. Orchestration logic lives in two places.

**Resolution: The Temporal workflow is GENERIC. It doesn't encode the step sequence.**

Every associate uses the same workflow:
```
Activity 1: Claim message from queue
Activity 2: Process (the actor does its thing — reads skills, runs capabilities, LLM if needed)
Activity 3: Complete message
```

The `Process` activity is where all actor-specific logic lives. The skill IS the source of truth for what the actor does. The workflow is just the durable execution wrapper — claim, process, complete.

For multi-entity operations within a single Process activity: idempotency handles crash recovery (check if entity already exists before creating). For truly long-running multi-step processes (binding flow with payment), a specialized workflow with separate activities per step is used — but that's the exception.

**Outcome:** No orchestration duplication. The skill orchestrates. Temporal wraps durably. One source of truth.

---

## Issue #3: CLI Entity Creation vs. Code (HIGH RISK)

**Problem:** We say `indemn entity create Document --fields "..."`. But entities are Python classes (Beanie + Pydantic). How does CLI create a class?

**Resolution: Entities are Python classes. The CLI generates those classes. No distinction.**

The original design had the entity generator: Python classes as declarative definitions, auto-registration produces CLI/API/skills/events. That design was correct.

`indemn entity create` writes a Python class file:
```bash
indemn entity create Document --fields "name:str, content:text, category:str" \
  --state-machine "uploaded,categorized,processed,archived"
```

Generates:
```python
# entities/document.py
class Document(Entity):
    name: str
    content: str
    category: str
    status: Literal["uploaded", "categorized", "processed", "archived"] = "uploaded"
    state_machine = {"uploaded": ["categorized"], "categorized": ["processed"], ...}
```

Auto-registration discovers it. CLI, API, skills generated. A developer can also hand-write or modify this file. Kernel capabilities activated separately via CLI.

**ONE kind of entity.** The CLI is a convenience for generating the class file. A developer can hand-write the same thing. Both paths produce the same result. Both can have kernel capabilities, computed fields, and custom methods.

**Outcome:** No "CLI entities" vs. "code entities." One entity model consistent with the original generator design.

---

## Issue #2: Outbox vs. Message Queue (MEDIUM RISK)

**Problem:** The outbox is "entity changed." The message_queue is "work item for an actor." Two collections carrying similar data.

**Resolution: Eliminate the separate outbox. Write directly to message_queue in the entity save transaction.**

```
Entity save + watch evaluation + message_queue writes → one MongoDB transaction
```

The message_queue IS the single source of truth for pending work. The Temporal dispatcher reads the message_queue for items targeting roles with associates and starts workflows.

```
Entity save → (same txn) evaluate watches → write to message_queue
                                                    ↓
                                            Temporal dispatcher reads queue
                                            for associate-eligible items
                                            → starts workflows
```

One collection. One transaction. One source of truth.

**Outcome:** No separate outbox. Fewer concepts, fewer hops. The message_queue serves as both the work queue and the durable event record.

---

## Issue #1: Scheduled vs. Message-Triggered Actors (MEDIUM RISK)

**Problem:** Message-triggered associates claim from the queue via Temporal. Scheduled associates run via Temporal Schedules. Two paths for the same kind of actor.

**Resolution: Scheduled tasks create messages in the queue. Associates process queue items regardless of how they arrived.**

When a schedule fires:
```
Schedule fires → creates message in queue
  (type: scheduled_task, target_role: stale_checker, entity_type: Submission)
→ Temporal workflow starts → claims from queue → processes → entity changes
```

Message-triggered:
```
Entity change → watch matches → message in queue
  (type: entity_change, target_role: classifier, entity_type: Email)  
→ Temporal workflow starts → claims from queue → processes → entity changes
```

Same queue. Same claiming. Same Temporal workflow. Same history. The only difference is what put the message in the queue — a watch or a schedule.

An associate can be BOTH message-triggered and schedule-triggered. A human can also check their inbox AND run a weekly report. Same model for everyone.

**Outcome:** All work flows through the queue. Schedules create queue items. One path for all work.

---

## Issue #5: Real-Time Direct Invocation vs. Queue (MEDIUM RISK)

**Problem:** Voice/chat associates are invoked directly for latency. But the queue is "where all work is visible." Direct invocations would be invisible.

**Resolution: Create a queue entry for visibility, invoke directly for execution.**

When a voice call comes in:
1. Interaction entity created
2. Message written to queue (same as everything else — watch matches)
3. SIMULTANEOUSLY: associate invoked directly (no waiting for Temporal dispatch)
4. The direct invocation **claims the queue entry immediately** (so nobody else picks it up)
5. Call proceeds (associate handles the live interaction)
6. When done, queue message marked complete

The queue entry exists for visibility and history. The execution bypasses the queue → Temporal dispatch path for latency. But the work IS in the queue.

Like a hospital ER: patient registered (queue entry), treated immediately (direct invocation) rather than waiting their turn.

**Outcome:** Real-time work IS in the queue. Just claimed immediately by direct invocation.

---

## Issue #4: Organization as Primitive vs. Entity (LOW RISK)

**Problem:** Organization is a kernel primitive (multi-tenancy scope). But it has data. Is it an entity?

**Resolution: Organization IS an entity that the kernel also understands specially.**

Organization, Actor, and Role are **bootstrap entities** — entities in the entity framework that the kernel also depends on. They have CLI, API, skills, state machines, computed fields — managed like all entities. But the kernel treats them specially:
- Organization provides org_id scoping
- Actor provides identity for claiming and processing
- Role provides permissions and watches for routing

`indemn org create`, `indemn actor create`, `indemn role create` — all entity operations. The kernel just happens to care about these particular entity types.

**Outcome:** Org, Actor, Role are entities. Managed normally. Kernel treats them specially.

---

## Issue #6: Context Enrichment Depth (LOW RISK)

**Problem:** Messages carry entity context. How deep? What about staleness?

**Resolution: Configurable per watch. Default shallow. Actors fetch more via CLI if needed.**

```bash
indemn role add-watch underwriter --entity Assessment --on created --context-depth 2
```

- Depth 1 (default): just the changed entity
- Depth 2: + directly related entities
- Depth 3: + their related entities

Context is a snapshot at message creation time. If the actor needs current data, they re-fetch via CLI. Same as how Claude Code pre-loads CLAUDE.md — starting context, not live data.

**Outcome:** Implementation detail, not architectural. Configurable, default shallow.

---

## Summary of Changes to the Architecture

| Issue | Resolution | What Changed |
|-------|-----------|-------------|
| Skill vs. workflow | Generic workflow, skill is source of truth | No Temporal-specific orchestration code per actor |
| Entity creation | CLI generates Python classes, same as hand-written | Consistent with original generator design |
| Outbox vs. queue | Eliminated outbox, write to queue in entity txn | One fewer collection, one fewer hop |
| Scheduled vs. triggered | Schedules create queue items, same path | All work through the queue |
| Real-time vs. queue | Queue entry created + direct invocation claims it | All work visible in queue |
| Org/Actor/Role | Bootstrap entities — entities the kernel knows about | Managed normally, kernel treats specially |
| Context depth | Configurable per watch, default shallow | Implementation detail |
