---
ask: "What did three independent reviewers (platform architect, DX engineer, distributed systems engineer) find when pressure-testing the OS primitives?"
created: 2026-04-08
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: review
    description: "Three independent agent reviews: platform architect, developer experience, distributed systems"
  - type: artifact
    description: "2026-04-08-kernel-vs-domain.md, 2026-04-08-primitives-resolved.md, 2026-04-08-entry-points-and-triggers.md"
---

# Pressure Test Findings — Three Independent Reviews

## What Was Validated

All three reviewers agree: **the four primitives (Entity, Message, Actor, Role) are sound.**

- **Concept count is right.** 6 concepts to get started (Entity, Message, Actor, Role, Watch, Organization), 4 more for depth. Comparable to Stripe's concept count.
- **Watches as wiring mechanism is "a genuine insight."** Actor-centric routing (what does this role care about?) is more intuitive than system-centric routing (when X happens, route to Y).
- **The actor spectrum works.** Deterministic, reasoning, hybrid — same framework, same I/O. All three reviewers confirmed.
- **Watch evaluation scales.** Even at 1M+ entity saves/hour, watch evaluation is sub-millisecond. The bottleneck is message write throughput, not watch matching. A single Atlas M30 handles 2,000-5,000 transactions/second.
- **The hardening requirements address the dangerous failure modes.** Transactions, visibility timeouts, correlation IDs, cascade depth, idempotency — the adversarial review process was effective.
- **The kernel-vs-domain separation is correct.** Same primitives work for insurance email processing, end-to-end sales (EventGuard), internal CRM, and content management.

## Findings: Must Address in the Design

### 1. Voice Channels Need Direct Invocation

The message-trigger path (entity created → watch matches → actor polls/claims) adds 2.5-5 seconds before the associate starts processing. For voice calls, the caller hears dead air.

**Fix:** Voice and real-time chat channel adapters directly invoke the associate AND create the Interaction entity + message in parallel (for audit and other watches). The associate doesn't wait for the queue. Already supported by the "direct invocation" trigger type — needs to be the documented pattern for real-time channels.

**Latency breakdown (message path vs. direct invocation):**
| Step | Message path | Direct invocation |
|------|-------------|-------------------|
| Channel infrastructure accepts call | 50-200ms | 50-200ms |
| Create Interaction entity | 10-25ms | 10-25ms (parallel) |
| Message delivery to queue | 0-5000ms (polling) | SKIPPED |
| Actor claims message | 3-8ms | SKIPPED |
| Load context | 15-50ms | 15-50ms |
| First LLM call | 800-2000ms | 800-2000ms |
| **Total to first response** | **1.1-7.3 seconds** | **0.9-2.3 seconds** |

### 2. Audit Trail Is Missing (Regulatory Requirement)

Entity version field increments but previous values are gone. Insurance regulators will ask "who changed what, when, from what value to what value, and why."

**Fix:** A `changes` collection recording every entity mutation: entity_id, entity_type, field_name, old_value, new_value, actor_id, reason, timestamp. Written in the same transaction as the entity save. This is the audit trail that regulators require.

The correlation_id and causation_id on messages provide cascade tracing. The changes collection provides field-level mutation history. Together, they answer "what happened and why" at any point in time.

### 3. Watch Conditions Must Be Entity-Local Only

If a watch condition references a related entity (e.g., "carrier.type = external"), that requires a MongoDB read inside the save transaction, blowing up latency (adding 3-10ms per cross-entity lookup).

**Fix:** Framework-enforced constraint — watch conditions can only reference fields on the entity that changed. If cross-entity conditions are needed, either:
- Denormalize the field onto the entity (computed field that caches the related value)
- Let the actor filter after claiming the message (claim, check related entity, skip if condition not met)

### 4. Split Message Storage From Day One

One `messages` collection grows indefinitely. After months, queue queries degrade as indexes exceed available RAM.

**Fix:** Two collections from the start:
- `message_queue` — active messages (pending, processing). Stays tiny (hundreds to low thousands of documents at any time). All queries are fast.
- `message_log` — completed messages (audit trail). Grows forever but is only queried for debugging and compliance.

On message completion: move from queue to log (insert to log + delete from queue, in a transaction). Queue performance never degrades regardless of history length.

**Queue indexes (optimized for operations):**
- `(org_id, target_role, status, priority, created_at)` — primary queue query
- `(status, visibility_timeout)` — stuck message recovery
- `(correlation_id)` — debugging active cascades

**Log indexes (optimized for audit):**
- `(entity_type, entity_id, created_at)` — audit trail per entity
- `(correlation_id, created_at)` — cascade reconstruction
- `(org_id, created_at)` — org-scoped history

### 5. Observability Baked Into Architecture (OTEL)

Craig's addition: the OS should have built-in logging, traceability, and observability using open standards (OpenTelemetry). Not bolted on later — baked into the kernel.

Every entity save, every message generated, every watch evaluation, every actor invocation, every CLI command — instrumented with OTEL spans and traces. The correlation_id on messages should be an OTEL trace ID (or linked to one).

This means:
- Every entity change is a span with: entity_type, entity_id, actor_id, fields_changed, duration
- Every message is a span with: correlation_id, causation_id, depth, target_role, target_actor
- Every actor invocation is a span with: actor_id, trigger_type, message_id, CLI commands executed, duration, success/failure
- Every CLI command is a span with: command, args, entity affected, result

Standard OTEL exporters (Jaeger, Grafana Tempo, Datadog) give visibility for free. No custom monitoring system needed.

### 6. Pre-Transition Business Validation

State machines validate the transition graph (is this transition allowed?). Pydantic validates field types (is the data well-formed?). Neither validates business invariants (can this entity actually move to this state given its current data?).

**Example:** A Submission can't transition to "submitted" if required fields (per the product's form schema) are missing. The state machine allows it. Pydantic doesn't catch it (the fields are Optional).

**Fix:** Pre-transition hooks on entities that validate business invariants before allowing a state change. These are entity-level (universal for all orgs) and can reference entity fields + org configuration.

```python
class Submission(Entity):
    def validate_transition(self, to_status):
        if to_status == "submitted":
            missing = self.get_missing_required_fields()
            if missing:
                raise TransitionValidationError(f"Cannot submit: missing {missing}")
```

## Findings: Define During Implementation (All Important)

### 7. Deterministic Skill Format Specification

The OS promises "deterministic skills that don't need LLM" but hasn't specified the format. Three options proposed:

**Option A: Structured YAML (like GitHub Actions)**
```yaml
name: usli-auto-classifier
trigger: Email:created
steps:
  - condition: "{{ entity.sender_domain == 'usli.com' }}"
    on_false: skip
  - cli: "indemn email classify {{ entity.id }} --type usli_quote"
  - cli: "indemn email link {{ entity.id }}"
```

**Option B: Python functions**
```python
@skill("usli-auto-classifier", mode="deterministic")
async def classify_usli(ctx: SkillContext):
    if ctx.entity.sender_domain != "usli.com":
        return
    await ctx.cli(f"indemn email classify {ctx.entity.id} --type usli_quote")
```

**Option C: Formalized markdown with structured execution blocks**
```markdown
---
name: usli-auto-classifier
mode: deterministic
---
1. CHECK: entity.sender_domain == "usli.com" → SKIP if false
2. RUN: indemn email classify {entity.id} --type usli_quote
3. RUN: indemn email link {entity.id}
```

Decision needed during implementation. The format should be harness-agnostic (works with any agent framework, not just LangChain).

### 8. Testing and Debugging CLI (Day-One Requirement)

**Debugging commands:**
```bash
# What happened to this entity change?
indemn trace entity EMAIL-001 --last-change
# Output: Entity changed at 14:02:33. processing_status: null → extracted.
#         Message MSG-042 generated. Target role: classifier.
#         Claimed by: Email Classifier at 14:02:35. Completed at 14:02:38.

# Why did nothing happen?
indemn trace entity EMAIL-001 --last-change
# Output: Field change on 'processing_status' — not a state transition
#         or @exposed method. Selective emission skipped.
#         HINT: Add to emitted_fields to generate messages for this field.

# What's in this role's queue?
indemn queue show classifier --org gic

# Follow a cascade from start to finish
indemn trace cascade --correlation-id abc-123

# What's stuck?
indemn messages dead-letter --org gic
indemn messages retry MSG-099
```

**Testing commands:**
```bash
# Test state machine transitions
indemn entity test Submission --transitions

# Simulate: which watches would fire for this change?
indemn simulate entity-change Email --field processing_status --to classified

# Dry-run a skill against real data
indemn associate test "Classifier" --input EMAIL-001 --dry-run

# Simulate full pipeline
indemn simulate pipeline --create Email --data '{"sender": "agent@usli.com"}' --trace
```

### 9. Declarative System Definition (YAML + CLI)

CLI for associates and runtime. YAML manifests for developers:

```yaml
# systems/gic-email-intelligence.yaml
org: gic-underwriters
roles:
  classifier:
    watches: ["Email:created", "Email:status_changed[processing_status=extracted]"]
  linker:
    watches: ["Email:status_changed[processing_status=classified]"]
associates:
  - name: Email Classifier
    role: classifier
    skills: [email-classification]
    mode: hybrid
actors:
  - email: jc@gicunderwriters.com
    roles: [underwriter]
schedules:
  - name: email-sync
    command: "indemn email fetch-new"
    every: "1m"
```

```bash
indemn system apply systems/gic-email-intelligence.yaml  # Idempotent
indemn system diff systems/gic-email-intelligence.yaml    # Show what would change
indemn system export --org gic > current-state.yaml       # Export current config
```

### 10. Bulk Operations

Everything is entity-at-a-time. Real operations need batch: import 500 submissions, renew 200 policies.

**Fix:** Bulk operation support at the entity level. `indemn submission import --file submissions.csv` does batch inserts in a single transaction, generates one batch message instead of 500 individual messages. Actors can process the batch as a unit.

Message schema addition: `batch_id` field and a coalescing window (e.g., 5 seconds) where messages to the same actor for the same entity type are grouped.

## Findings: Bank for Later (But Design-Compatible)

### 11. Assignment May Need Lifecycle

The platform architect argues assignment needs richer lifecycle: pending → active → reassigned → completed → escalated. Plus: approval-required assignment, round-robin load balancing, escalation chains, reassignment with context transfer.

For MVP: simple assignment (entity + actor + role context) is sufficient. But assignment could become an entity that composes from existing primitives when the need arises. The current design doesn't prevent this evolution.

**Assignment race condition fix (implement now):** At message claim time, verify the assignment is still current. If the actor was unassigned between message creation and processing, re-route the message to the role's general queue.

### 12. Partial Multi-Entity Failures (Phantom Messages)

If an actor changes entities A and B but crashes before C, messages from A and B are in the system. Downstream actors process them as legitimate.

**MVP approach:** Design skills so the most failure-prone operation runs first. If it fails, no orphans.

**Future approach:** Batch-save transactions for atomic multi-entity operations. Or saga-style compensation using correlation_id to mark orphaned messages.

### 13. Provider Versioning for Adapters

External APIs change (Outlook Graph API has had 3 breaking changes in 18 months). The adapter registry needs version support: `"outlook_v1": OutlookV1, "outlook_v2": OutlookV2`. Integration entity stores which version it was configured against. Migration path: `indemn integration upgrade INT-001 --to outlook_v2 --dry-run`.

### 14. Governor Limits on Watches

Misconfigured watches can generate message avalanches. When an org creates a watch, the system should estimate message volume based on historical entity change rates. Watches above a threshold require explicit confirmation. Salesforce learned this the hard way with Process Builder.

## Scale Thresholds (For Reference)

| Metric | Comfortable | Watch Carefully | Needs Action |
|--------|-------------|-----------------|-------------|
| Entity saves/hour (all orgs) | <100,000 | 100K-1M | >1M |
| Messages/hour | <500,000 | 500K-2M | >2M |
| Concurrent LLM actor sessions | <200 | 200-1,000 | >1,000 |
| Message queue collection size | <10,000 docs | 10K-100K | >100K (split not working) |
| Atlas tier needed | M30 | M60 | M80+ or sharding |
| Watch count per org | <200 | 200-500 | >500 (governor limits) |
