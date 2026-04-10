---
ask: "Third round of architecture ironing — event granularity, cascading, queue processor, claiming vs assignment, bootstrap circularity, schema evolution, condition format, and versioning"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude systematically finding and resolving architectural inconsistencies — round 3"
---

# Architecture Ironing — Round 3

## Issue #1: Event Granularity — One Save = One Event

**Problem:** When `policy.bind(quote)` runs — an @exposed method that transitions status and sets premium — does the system generate three separate events (method invoked, state changed, field changed)?

**Resolution: One save = one event.** The event is "Policy changed" with metadata about WHAT changed (method invoked, fields changed, state transitioned). Watch conditions evaluate against the full change metadata, not separate sub-events. One message per matching watch, not one message per change type.

The event payload:
```json
{
  "entity_type": "Policy",
  "entity_id": "POL-001",
  "method": "bind",
  "state_transition": {"from": "issued", "to": "active"},
  "fields_changed": ["status", "written_premium"],
  "timestamp": "..."
}
```

A watch on `Policy:state_changed[to=active]` matches. A watch on `Policy:method_invoked[bind]` matches. Both conditions are evaluated against the SAME event. Each matching watch produces one message. But it's one event, not three.

**Needs thorough auditing** — this is fundamental to how the system churns. Every entity save, every watch evaluation, every cascade must follow this one-save-one-event rule consistently.

## Issue #2: Emission Boundary — @exposed Methods

**Problem:** Does a rule setting a field (auto-classify sets `type`) generate events that trigger more watches?

**Resolution: @exposed method invocations are the emission boundary.** When `classify --auto` runs (an @exposed method), the save at the end of that method generates one event covering ALL changes made during execution (fields set by rules, state transitions, everything). Individual field changes within the method don't independently generate events.

The flow:
1. Associate calls `indemn email classify EMAIL-001 --auto`
2. The `classify` method runs (entity method / kernel capability)
3. Rules evaluate → set `classification.type = usli_quote`
4. Method completes → entity saves → ONE event generated
5. Watch evaluation → linker's watch on `Email:classification_set` matches → message created
6. Linker processes → eventually saves → another event → cascade continues

The emission is tied to the method invocation completing, not to individual field changes within it. This prevents mid-method cascading and keeps the event model clean.

## Issue #3: Queue Processor (Named)

**Resolution:** The separate process that reads message_queue and starts Temporal workflows for associate-eligible items is called the **Queue Processor**. It also handles: escalation deadline checks, schedule-created item dispatch, and queue health monitoring. One process, multiple responsibilities, all centered on the queue.

The message_queue serves as both:
1. The work queue (humans and associates see pending items)
2. The durable bridge between entity saves and Temporal dispatch

Same data, two purposes. No separate outbox. No redundancy.

## Issue #4: Claiming vs. Assignment — The Skill Decides

**Problem:** When an actor claims a message about an entity, does the entity get "assigned" to them?

**Resolution: Claiming is always transient (about the message). Assignment is an explicit operation the skill performs when appropriate.**

- Claiming: `findOneAndUpdate` on the message → this message is being processed by this actor
- Assignment: `indemn submission assign SUB-001 --underwriter {actor_id}` → this entity belongs to this actor persistently

The skill decides whether to assign:
- Classification skill: claims, processes, moves on (no assignment — the classifier doesn't "own" the email)
- Underwriter review skill: claims AND assigns (because underwriter ownership is persistent for the submission's lifecycle)

Claiming and assignment are separate concepts that COMPOSE. Sometimes claiming leads to assignment. Sometimes it doesn't. The skill controls this, not the kernel.

## Issue #5: Bootstrap Entity Meta-Circularity

**Problem:** Role is an entity. Modifying a Role (adding a watch) goes through the entity save path. The save triggers watch evaluation. If a watch exists on Role:modified, it fires. Potential issues: cache staleness (the watch we just added isn't in the cache yet) and infinite loops (a watch on Role changes that itself modifies Roles).

**Example walkthrough:**
1. Admin sets up: `indemn role add-watch admin --entity Role --on modified` (notify admin of config changes)
2. Later: `indemn role add-watch underwriter --entity Assessment --on created --when '{"needs_review": true}'`
3. This modifies the underwriter Role entity → saves → watch evaluation
4. The admin watch on Role:modified matches → message created → admin notified ✓ (useful)
5. BUT: the watch we just added to underwriter is NOT in the cached watches yet (up to 60s stale)
6. AND: if the admin watch's actor tries to modify the Role (add audit timestamp), it triggers another Role:modified → infinite loop

**Resolution: Cache invalidation + cascade guard.**

- **Cache invalidation:** When a bootstrap entity (Role, Actor, Org) saves, immediately invalidate the watch cache. The next entity save reloads fresh watches. Configuration changes take effect immediately.
- **Cascade guard:** The kernel detects when a watch evaluation would trigger a change to the same bootstrap entity type being evaluated. Self-referencing cascades on bootstrap entities are blocked at depth 1.

Bootstrap entities are still full entities — same save path, same audit trail, same CLI. But with two safety measures that prevent meta-circularity.

## Issue #6: Schema Evolution — Entities Must Be Updatable

**Problem:** Entities are Python class files. Adding a field means modifying the Python file. How?

**Resolution:** `indemn entity modify` handles schema evolution:

```bash
indemn entity modify Submission --add-field "priority:str"
indemn entity modify Submission --remove-field "priority"
indemn entity modify Submission --rename-field "old_name" "new_name"
```

- `--add-field`: Updates the Python class file, adds the field with a default value. Existing documents in MongoDB are fine (Pydantic handles missing fields with defaults).
- `--remove-field`: Updates the Python class file, removes the field. Existing documents in MongoDB still have the data but it's ignored by Pydantic.
- System restart or hot-reload picks up the change.
- The changes collection records the schema change for versioning and rollback.

## Issue #7: Condition Language — JSON Only

**Resolution:** Craig's decision: JSON for all conditions. No CLI shorthand. One format everywhere.

```bash
indemn rule create --entity Email --org gic \
  --when '{"all": [{"field": "from_address", "op": "ends_with", "value": "@usli.com"}, {"not": {"field": "subject", "op": "contains", "value": "Decline"}}]}' \
  --action set-fields --sets '{"type": "usli_quote"}'
```

The skill documents the JSON schema. Associates and humans use the same format. No parsing of shorthand expressions. One condition evaluator, one format.

For readability, complex conditions go in YAML files:
```bash
indemn rule create --from-file rules/usli-classification.yaml
```

But the stored format and the CLI format are always JSON.

## Versioning: Changes Collection IS the Version History

**The insight:** Every configuration change in the OS creates a change record in the changes collection. This collection is BOTH the compliance audit trail AND the version history. One system, two purposes.

**What gets versioned (all automatically via changes collection):**

| What | How Changed | Versioned By |
|---|---|---|
| Rules | CLI (`indemn rule create/modify/delete`) | Changes collection |
| Watches | CLI (`indemn role add-watch/remove-watch`) | Changes collection |
| Associate config | CLI (`indemn associate configure`) | Changes collection |
| Entity schema | CLI (`indemn entity modify`) | Changes collection + git |
| Skills (files) | File edit | Git + changes collection |
| Lookups | CLI (`indemn lookup create/modify`) | Changes collection |
| Capability activation | CLI (`indemn entity enable`) | Changes collection |

**Rollback = replay changes in reverse:**

```bash
# See recent changes
indemn history --org gic --last 10

# Roll back a specific change
indemn rollback CHANGE-047
# Reads the change record, applies the old_value

# Roll back to a point in time
indemn rollback --org gic --to "2026-04-09 14:00"
# Reads all changes after that time, applies them in reverse order

# Preview before applying
indemn rule create --org gic --when '...' --then '...' --dry-run
# Shows what would be affected without making changes
```

**Bulk deployment via Temporal:**

For deploying a SET of related changes:
```bash
indemn deploy --from-file changes/gic-v2.yaml
```

This starts a Temporal deployment workflow that:
1. Validates all changes (pre-check)
2. Creates a deployment record
3. Applies changes in order
4. Verifies each step
5. If any step fails → saga compensation rolls back previous steps

`indemn deploy rollback DEPLOY-003` reverses the deployment using recorded before-values.

**Open question (identified by Craig):** Entity class files and skill markdown files are currently in git (the repository). This creates a split: some configuration is versioned by the changes collection (runtime CLI changes), some by git (file changes). These need to be unified — discussed in next round.

## Cumulative Changes (Rounds 1 + 2 + 3)

| Round | Issue | Resolution |
|-------|-------|-----------|
| R1 | Skill vs. workflow orchestration | Generic workflow, skill is source of truth |
| R1 | Entity creation (CLI vs. code) | CLI generates Python classes, same as hand-written |
| R1 | Outbox vs. queue | Eliminated outbox, write to queue in entity txn |
| R1 | Scheduled vs. triggered | Schedules create queue items, same path |
| R1 | Real-time vs. queue | Queue entry + direct invocation claims immediately |
| R1 | Org/Actor/Role | Bootstrap entities the kernel knows specially |
| R1 | Context depth | Configurable per watch, default shallow |
| R2 | Capabilities + entity methods | Unified — capabilities add methods to entities |
| R2 | Watch + rule conditions | One condition language, one evaluator |
| R2 | Message data vs. Temporal state | Entities are source of truth, messages carry references |
| R2 | Entity skills vs. associate skills | Same format, different purposes, compose naturally |
| R2 | Audit/log/trace | Three systems, three purposes, one trace ID |
| R3 | Event granularity | One save = one event, full change metadata |
| R3 | Emission boundary | @exposed methods are the boundary |
| R3 | Queue Processor | Named — handles dispatch, escalation, schedules |
| R3 | Claiming vs. assignment | Separate concepts, skill decides when to assign |
| R3 | Bootstrap circularity | Cache invalidation + cascade guard |
| R3 | Schema evolution | `indemn entity modify` + changes collection |
| R3 | Condition format | JSON only, no CLI shorthand |
| R3 | Versioning | Changes collection = version history, Temporal for bulk deploys |
