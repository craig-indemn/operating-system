---
ask: "How does the kernel handle actor references on entities — assignment, targeting, reassignment?"
created: 2026-04-08
updated: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude working through assignment mechanics — simplified from target-from-field to context-based filtering"
---

# Actor References and Message Targeting

## Decision: Assignment Is Not a Primitive

Assignment varies too much by domain to be a kernel primitive. Insurance assignment (underwriter of record, binding authority) is fundamentally different from CRM assignment (deal owner, round-robin) is different from content assignment (author, reviewer).

The kernel provides the mechanism. The domain provides the semantics.

## The Simple Design: Messages Target Roles, Context Enables Filtering

**Messages always target roles. The kernel does not do actor-specific targeting.**

Messages already include entity context (related entities resolved and attached). So a message about Assessment ASS-001 carries:

```json
{
  "entity_type": "Assessment",
  "entity_id": "ASS-001",
  "event": "created",
  "target_role": "underwriter",
  "context": {
    "assessment": { "needs_review": true, "confidence": 0.5 },
    "submission": { "id": "SUB-001", "underwriter": "JC", "stage": "processing" }
  }
}
```

The submission data — including who the underwriter is — is already in the message context.

**An actor's queue is just a query:**
"Show me messages where `target_role = underwriter` AND (`context.submission.underwriter = me` OR `context.submission.underwriter is null`)"

JC sees: messages about submissions he owns, plus unassigned submissions anyone can claim. Sarah sees the same — her submissions plus the unassigned pool.

## Why This Is Better Than `target-from-field`

The previous design proposed `--target-from-field` on watches, which would have the kernel resolve actor references through entity relationships during message generation. This was rejected because:

1. **Cross-entity reads during message generation.** The watch triggers on Assessment:created, but targeting info is on the related Submission. The kernel would follow entity relationships to resolve — inconsistent with the rule that watch evaluation is entity-local.

2. **Unnecessary kernel complexity.** The kernel would need to understand entity relationships, resolve field paths, verify actors have the right role, handle null/inactive cases.

3. **Solving the wrong problem at the wrong layer.** The question isn't "how does the kernel route to specific actors." It's "how does the right person see the right work." Context + query answers that without kernel machinery.

## Actor References Are Just Entity Fields

- `Submission.underwriter` is a regular field that happens to hold an actor ID
- The entity framework doesn't treat it specially
- It shows up in the message context because the submission is a related entity
- The queue UI/query filters by it
- Different domains use different field names with different semantics — the kernel doesn't care

## Assignment Is a Domain Concern

```bash
# Assign (just set a field)
indemn submission update SUB-001 --underwriter jc

# Reassign (just change the field)
indemn submission update SUB-001 --underwriter sarah

# Query assignments (just a field filter)
indemn submission list --underwriter jc
```

- Audit trail captures every change (who, when, from, to, reason)
- Future messages include the new value in context
- Queue queries automatically reflect the change
- The domain decides: what fields reference actors, what they mean, what lifecycle they have

## How the Three Scenarios Work

### Scenario 1: No Assignment
Assessment created, no underwriter set on submission. Message goes to underwriter role with context showing `underwriter: null`. All underwriters see it. First to claim wins.

### Scenario 2: With Assignment
Assessment created, submission.underwriter = JC. Message goes to underwriter role with context including `underwriter: "JC"`. JC's queue query filters to show his submissions. JC claims it.

### Scenario 3: Reassignment
Underwriter changes from JC to Sarah. Submission field updated. Audit trail records the change. Future messages carry `underwriter: "Sarah"` in context. Sarah's queue now shows these. Existing messages in queue still have `underwriter: "JC"` in context — JC can still process them, or they time out via visibility timeout.

## Scale Optimization (Later, If Needed)

At scale (50 underwriters, 1000 pending messages), every underwriter's queue query scans all underwriter messages and filters by context. This works but is less efficient than pre-targeted routing.

If needed, `target_actor_id` can be added as a denormalized field on the message — populated during message creation by reading actor references from the entity context. The message schema already has this field (from the core primitives design). We just don't populate it initially.

**This is a performance optimization, not an architectural change.** The design supports it without modification when the time comes.

## What the Kernel Provides

| Kernel provides | Domain provides |
|----------------|-----------------|
| Messages target roles (via watches) | Which fields reference actors |
| Messages include entity context (context enrichment) | What those references mean |
| Atomic message claiming (findOneAndUpdate) | Assignment lifecycle (simple field change, workflow, approval) |
| Audit trail (changes collection) | Reassignment process |
| Queue query infrastructure | Queue filters (UI-level) |
