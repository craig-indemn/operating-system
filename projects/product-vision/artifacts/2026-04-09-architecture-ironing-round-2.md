---
ask: "Second round of architecture ironing — five more places where concepts should be unified or clarified"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude systematically finding and resolving architectural inconsistencies"
  - type: artifact
    description: "2026-04-09-architecture-ironing.md (round 1)"
---

# Architecture Ironing — Round 2

## Issue #1: Kernel Capabilities + Entity Methods = One Thing

**Problem:** Two concepts — "kernel capabilities" (reusable operations activated via CLI) and "entity methods" (@exposed Python methods on entity classes) — that look identical from the outside.

**Resolution: Unified.** Kernel capabilities ARE entity methods. When you activate a capability on an entity, it adds a method to that entity class. The method's implementation comes from the kernel (reusable code). It appears in CLI, API, and the auto-generated skill exactly like a hand-written method.

```bash
# Activating a capability = adding a reusable method to the entity
indemn entity enable Email auto-classify --evaluates classification-rule
# Result: `indemn email classify --auto` now works

# Writing a custom method = adding a specific method to this entity class
# (developer adds @exposed method in the Python class file)
# Result: `indemn email my-custom-method` now works
```

From the CLI, API, skill, associate perspective: there is no difference. The entity has methods. Some are reusable (came from kernel method library), some are custom (hand-written). Same interface, same auto-generated documentation, same invocation pattern.

**There is no separate "kernel capability" concept visible to users.** There are entity methods. The kernel has a library of reusable methods that can be activated on any entity type. But the surface is just: entities have methods.

---

## Issue #2: Watch Conditions + Rule Conditions = One Condition Language

**Problem:** Watches evaluate conditions for routing (`needs_review=true`). Rules evaluate conditions for classification (`from_address ends_with @usli.com`). Two evaluation systems doing the same kind of work.

**Resolution: One condition evaluator. One syntax. One set of operators.**

The condition language supports:
- **Field comparison:** `equals`, `not_equals`, `contains`, `ends_with`, `starts_with`, `matches` (regex), `gt`, `lt`, `gte`, `lte`, `in`, `not_in`
- **Composition:** `all` (AND), `any` (OR), `not`
- **Storage:** Structured JSON (CLI accepts shorthand for simple cases)

Watches and rules both use this language:

```bash
# Watch (routing condition):
indemn role add-watch underwriter --entity Assessment --on created \
  --when "needs_review = true"

# Rule (classification condition):
indemn rule create --entity Email --org gic \
  --when "from_address ends_with @usli.com" \
  --action set-fields --sets '{"type": "usli_quote"}'
```

Same evaluator. Same tracing. Same debugging. `indemn trace` shows condition evaluation for both watches and rules in the same format.

**Watches and rules remain separate concepts** (watches belong to roles for routing, rules belong to entity methods/capabilities for behavior). But they share the condition language and evaluator. Separate concepts, one engine.

---

## Issue #3: Message Queue Data vs. Temporal Workflow State

**Problem:** When a Temporal workflow starts, the message data is in MongoDB (message_queue) AND in Temporal (workflow input). Same data in two places.

**Resolution: Entities are the source of truth. Messages carry references, not copies.**

The message in the queue carries minimal data:

```json
{
  "entity_type": "Assessment",
  "entity_id": "ASS-001",
  "event_type": "created",
  "target_role": "underwriter",
  "correlation_id": "trace-abc-123",
  "created_at": "2026-04-09T14:00:00Z",
  "summary": {"display": "Assessment for Acme LLC - GL"}
}
```

The `entity_id` is the reference. When an actor processes the message, their first step: load the entity from MongoDB. Fresh, current, authoritative. No stale copies.

The Temporal workflow input is the same minimal reference: message_id or entity_type + entity_id. The workflow's Process activity loads entity data from MongoDB.

**For human UI:** When rendering queue items, the UI batch-loads entity data for visible items. The `summary` field provides just enough for a list row without loading the full entity.

**For targeting/filtering:** UI queries join queue items with entity data (e.g., "show me underwriter queue items where submission.underwriter = JC"). This is a query, not pre-computed routing.

**One MongoDB read per message processing** (load entity). At 3-10ms, negligible compared to LLM calls (1-3 seconds). The benefit: no stale data, no duplication, entities are always the single source of truth.

---

## Issue #4: Entity Skills vs. Associate Skills — Confirmed Not a Problem

Both are files loaded into agent context. Same format (markdown). Different creation and purpose:

| | Entity Skills | Associate Skills |
|---|---|---|
| **Created by** | Auto-generated from entity class | Hand-authored or AI-generated |
| **Purpose** | Document what CLI commands exist for this entity | Describe how to process a specific type of work |
| **Used by** | Associates, developers, humans — anyone using the entity | Associates — behavioral instructions for processing |
| **Example** | "Submission has these fields, these states, these commands..." | "When a new email arrives, classify it like this..." |

An associate loads both: entity skills for WHAT operations are available, associate skills for HOW to orchestrate them. They compose naturally. An associate processing emails loads the Email entity skill (what commands exist) and the email-classification associate skill (when and how to use them).

They're both context files for agents. Different purposes, same format, same loading mechanism. The name overlap is acknowledged but not a structural problem.

---

## Issue #5: Audit Trail vs. Message Log vs. OTEL Traces

**Problem:** Three systems capturing "what happened." Potential redundancy.

**Resolution: Three systems, three purposes, one trace ID linking them.**

| System | Captures | Who Asks | Retention | Query Pattern |
|--------|----------|----------|-----------|---------------|
| **Changes collection** | Field-level entity mutations (who, what, from, to, when, why) | Compliance: "who changed this policy's premium?" | Years (regulatory) | By entity_id |
| **Message log** | Completed work items (what processed, by whom, result) | Operations: "how many submissions processed yesterday?" | Months-years | By role, date, entity_type |
| **OTEL traces** | Full execution path (spans, timing, parameters, errors) | Developer: "why did this take 10 seconds?" | Days-weeks | By trace_id, span attributes |

**Not redundant — three optimized views of the same events:**
- Changes collection: permanent compliance record, indexed by entity
- Message log: permanent operations record, indexed by work
- OTEL: ephemeral observability, indexed by execution

**OTEL is the connective tissue.** The correlation_id (= OTEL trace_id) links all three. The `indemn trace entity EMAIL-001` command:
1. Queries OTEL for execution spans (timing, errors, path)
2. Queries changes collection for field mutations (what changed)
3. Queries message log for work items (who processed what)
4. Presents all three in a unified timeline

Three data stores, one unified view. Different retention, different query patterns, linked by the same trace ID.

**Changes collection** is written in the entity save transaction (same MongoDB transaction as the entity — guaranteed consistent, never gaps).

**Message log** is written when messages complete (direct write for reliability — not derived from OTEL export, which could have gaps).

**OTEL traces** are exported to the observability backend (Jaeger, Grafana Tempo, etc.) — ephemeral, for debugging and performance analysis.

---

## Cumulative Architecture Changes (Rounds 1 + 2)

| What Changed | Before | After |
|---|---|---|
| Kernel capabilities | Separate concept from entity methods | Unified — capabilities add methods to entities |
| Condition language | Separate for watches and rules | One evaluator, one syntax, shared |
| Message content | Rich context (entity data copies) | Minimal references, actors load fresh data |
| Outbox | Separate collection | Eliminated — write to message_queue in entity txn |
| Scheduled work | Separate path (Temporal Schedules) | Creates queue items, same path as message-triggered |
| Real-time work | Bypasses queue entirely | Queue entry created + direct invocation claims immediately |
| Entity creation | Ambiguous (CLI vs. code) | CLI generates Python classes, same as hand-written |
| Workflow orchestration | Could be in skill AND Temporal workflow | Generic workflow, skill is source of truth |
| Human vs. associate routing | Split (MongoDB for humans, Temporal for associates) | Unified queue, Temporal for associate execution |
| Org/Actor/Role | Ambiguous (primitive vs. entity) | Bootstrap entities — entities the kernel knows specially |
| Context depth | Undefined | Configurable per watch, default shallow |
| Entity skills vs. associate skills | Potentially confusing overlap | Same format, different purposes, compose naturally |
| Audit/log/trace | Potentially redundant | Three systems, three purposes, one trace ID |
