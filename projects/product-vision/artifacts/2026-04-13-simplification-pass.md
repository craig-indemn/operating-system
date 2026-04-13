---
ask: "Review the entire architecture with fresh eyes — does every concept earn its complexity? What can be simplified, merged, or deferred?"
created: 2026-04-13
workstream: product-vision
session: 2026-04-13-a
sources:
  - type: conversation
    description: "Craig and Claude conducting the simplification pass — reviewing all 20+ concepts across sessions 5-6 for complexity justification"
  - type: artifact
    description: "All prior session 5-6 artifacts — the complete architecture being reviewed"
---

# Simplification Pass

## Context

Craig flagged from session 4: "a lot of this can be simplified." The simplification pass is the scheduled review after all design sessions complete, asking "does this earn its complexity?" for every concept in the architecture.

The architecture grew substantially through sessions 5-6: Integration elevated to primitive #6, Attention and Runtime added as kernel entities, scoped watches with two resolution types, watch coalescing, harness pattern, Session as kernel entity, five auth method types, platform admin cross-org model, bulk operations pattern, base UI rendering contract, assistant-at-the-forefront design, content visibility scoping, and more.

This pass reviews all of it.

## The Simplest Expression of the Kernel

Before looking for what to cut, establish the floor — the absolute minimum needed to explain the OS:

**Six things.**

1. **Entity** — your data, with structure and lifecycle. Auto-generates CLI, API, docs.
2. **Message** — when entities change, work flows. The nervous system.
3. **Actor** — anything that does work. Human or AI. Same queue.
4. **Role** — what an actor can do, and what comes to them.
5. **Organization** — who this data belongs to.
6. **Integration** — how the system connects to the outside world.

That's the pitch. Investor, engineer, customer — those six concepts tell the whole story. Everything else serves one of these six. The simplification pass asks: did anything drift beyond serving them?

## Review Method

Cataloged every concept in the architecture (~20 distinct named things beyond the six primitives). Checked each against:
- Does it serve one of the six primitives?
- Is it the simplest way to serve that primitive?
- Can it be merged with something else?
- Can it be deferred without architectural change?

## Architectural Simplifications Accepted

### 1. Watch coalescing removed from kernel → UI rendering concern

**What we had**: watches declared a `coalesce` config (strategy, time window, summary template). The kernel grouped matching events into batched queue items with a shared `batch_id`. This added: a coalesce field on watches, a batch_id field on messages, time-window grouping logic in the kernel's emission path.

**The forcing function**: "50 stale submissions shouldn't spam ops queue as 50 rows."

**The simpler answer**: the kernel emits 50 individual messages (preserving "one save = one event"). They share a `correlation_id` (the bulk operation's Temporal workflow ID, or the scheduled task's execution trace). The UI groups them for display by correlation_id. One rendered row: "47 submissions became stale" with drill-down.

**What this removes**:
- `coalesce` field on watch definitions
- `batch_id` field on message schema
- Time-window grouping logic in the kernel's message emission path

**What this preserves**:
- One save = one event (untouched)
- Per-entity messages in the queue (associates still process individually)
- Scoped watches (still write `target_actor_id`, UI groups per target actor)
- The visual outcome (ops sees "47 stale" with drill-down)

For associates: 50 individual messages is the right model — each gets claimed and processed individually. Coalescing was only ever about human queue display, which is a UI concern.

### 2. Rule evaluation traces → metadata in the changes collection

**What we had**: "Every entity that passes through rule evaluation gets a trace record: rules evaluated, matched, won/lost, entity state at evaluation time. Not logs. Always. Queryable." This implied a separate evaluation trace collection or records.

**The simpler answer**: when `classify --auto` runs and rules evaluate, the resulting entity change is recorded in the changes collection (already happens). The change record's metadata includes which rules were evaluated and which matched:

```json
{
  "entity_id": "EMAIL-001",
  "field": "classification",
  "old_value": null,
  "new_value": "usli_quote",
  "method": "auto-classify",
  "rule_evaluation": {
    "rules_checked": 47,
    "matched": ["R-003 (usli-from-domain)"],
    "vetoed": [],
    "needs_reasoning": false
  },
  "actor": "Email Classifier",
  "timestamp": "..."
}
```

**What this removes**: a separate evaluation trace concept and potentially a separate collection.

**What this preserves**: full debuggability. "Why was this classified as usli_quote?" is answered by `indemn history --entity EMAIL-001` reading the changes collection entry.

## Architectural Simplification Considered and Rejected

### Runtime stays as a kernel entity

Considered demoting Runtime from kernel entity to kernel-provided (but not kernel-dependent) entity. The argument: Runtime isn't on the hot path the way Organization (tenancy), Actor (identity), Role (routing), or Session (authentication) are.

**Craig's decision: keep Runtime as a kernel entity.** It's "the most important part, the center of everything" (from session 5). The kernel dispatches work to Runtimes, monitors their health, and routes real-time events through them via Attention's runtime_id reference. The dependency is real even if less frequent than session validation.

**Seven kernel entities remain**: Organization, Actor, Role, Integration, Attention, Runtime, Session.

## Naming Improvement

**"Bootstrap entity" → "kernel entity."**

"Bootstrap entity" was our internal working term. "Kernel entity" is more self-evident: entities the kernel provides and depends on, as opposed to domain entities that applications create. Craig's own language consistently used "kernel" ("should probably be in the kernel"). The spec uses "kernel entity."

**Kernel entities** (7): Organization, Actor, Role, Integration, Attention, Runtime, Session.
**Domain entities**: everything else — created per application via CLI, stored as data in MongoDB.

## MVP Scope Review

Reviewed all concepts for MVP necessity. Craig's guidance: "otherwise don't see the benefit" of deferring most things. The architecture is designed to be built — aggressive scope reduction undermines the point.

### Deferred from MVP (confirmed by Craig)

| Feature | Reason for deferral |
|---|---|
| **WebAuthn / passkeys** | TOTP is sufficient for MFA in MVP. WebAuthn adds significant browser-side complexity. Additive later as a new auth method type. |
| **Per-operation MFA re-verification** (`requires_fresh_mfa` on @exposed) | Session-level MFA is sufficient for MVP. Per-operation sensitivity is a refinement. |

### Kept in MVP (Craig pushed back on proposed deferrals)

| Feature | Why it stays |
|---|---|
| **Schema migration** (full: rename, type-change, batching, aliases, rollback) | "Schema migration is important." We're building a real system. Entities will evolve through real usage within weeks. Deferring migration means deferring the ability to learn from production. |
| **All 5 Attention purposes** (real_time_session, observing, review, editing, claim_in_progress) | They're enum values. The implementation cost of 5 vs 3 is zero. No reason to artificially limit. |
| **Content visibility scoping** (full_shared / metadata_shared / owner_only on Integration) | "We are starting with CRM use case." Personal integrations (Gmail, Slack, Calendar) need privacy from day one. The CRM is the dog-fooding use case. |
| **Rule groups with lifecycle** (draft → active → archived, ownership, conflict detection) | Without groups, 50 rules become unmanageable. Without lifecycle, you can't test rules before deploying to production. Basic organizational hygiene. |

### Already correctly scoped (no change)

| Feature | Status |
|---|---|
| Platform admin work-type tagging + configurable notifications | Deferred — MVP uses simple fixed-duration sessions with always-notify |
| Throughput + dwell-time aggregation capabilities | Deferred — require historical aggregation over message_log, more complex than state-distribution and queue-depth |
| Assistant inline entity rendering | Deferred — text responses with entity links for MVP, inline rendering is UX polish |
| Tier 3 self-service (billing, plans, sub-users) | Deferred — basic signup only for MVP |

## The Complexity Verdict

**The architecture is proportional.** Every concept serves one of the six primitives. Every addition was forced by a real use case from the three retraces (GIC, EventGuard, CRM). No concept exists for theoretical reasons.

**Two mechanisms were moved to where they belong:**
1. Watch coalescing → UI rendering concern (not kernel)
2. Rule evaluation traces → changes collection metadata (not separate records)

**Two features are confirmed deferred:**
1. WebAuthn (TOTP sufficient)
2. Per-operation MFA re-verification (session-level sufficient)

**Everything else earns its place and stays in MVP.** The architecture doesn't need to be redesigned. It needed two mechanisms simplified and two features deferred.

## Updated Architecture Summary (Post-Simplification)

### Six structural primitives (unchanged)
Entity, Message, Actor, Role, Organization, Integration.

### Seven kernel entities (unchanged, renamed from "bootstrap entities")
Organization, Actor, Role, Integration, Attention, Runtime, Session.

### Core mechanisms (two removed)
- ~~Watch coalescing~~ → UI rendering concern
- ~~Separate rule evaluation traces~~ → changes collection metadata
- Everything else: watches, scoped watches (field_path + active_context), rules, lookups, kernel capabilities, the --auto pattern, skills, Temporal, harness pattern, bulk operations, changes collection, message queue/log, OTEL, OrgScopedCollection — all remain as designed.

### What the spec needs to capture

The spec should present the architecture in layers of increasing detail:

**Layer 0 — The pitch (6 concepts)**: Entity, Message, Actor, Role, Organization, Integration. Everything composes from these.

**Layer 1 — The kernel (adds ~5 concepts)**: Watches (on roles, the wiring mechanism), Rules + Lookups (per-org configuration), Skills (markdown behavioral instructions), the Queue (MongoDB message_queue, unified for humans and associates), Temporal (durable execution for associates).

**Layer 2 — The operational surface (adds ~5 concepts)**: Kernel entities beyond the primitives (Attention, Runtime, Session), Authentication (session management, 5 auth methods, MFA, platform admin), Base UI (auto-generated operational surface, assistant at the forefront).

**Layer 3 — Patterns and mechanisms (adds ~5 concepts)**: Bulk operations pattern, Harness pattern (thin CLI-based per-framework), Scoped watches (field_path + active_context), Content visibility scoping, Schema migration.

**Layer 4 — Infrastructure (adds ~5 concepts)**: OTEL (baked-in observability), OrgScopedCollection (defense-in-depth isolation), Changes collection (tamper-evident audit), Message queue/log split, AWS Secrets Manager for credentials.

Each layer builds on the previous. A reader can stop at any layer and have a complete (if less detailed) understanding. The six primitives carry the whole story; everything else is implementation.

## What Comes Next

The simplification pass is complete. The architecture is final. What remains:

1. **Spec writing** — one actionable document (or a small set of connected ones) that an engineer or agent can build from. The spec should use the layered presentation above.
2. **Stakeholder engagement** — Ryan → Dhruv → George → Kyle/Cam, with the spec as the deliverable.
3. **Begin building** — first entity by hand, prove the full stack works.

The path from "architecture designed" to "building" is now: write the spec, present to stakeholders, start coding. No more design work unless the spec-writing process surfaces a gap.
