---
ask: "What is the OS kernel architecture as it stands right now — the complete current design in one place?"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08/09
sources:
  - type: synthesis
    description: "Consolidation of all session 4 artifacts into one coherent architecture document"
---

# The OS Kernel Architecture — Consolidated

## What We're Building

A domain-agnostic operating system kernel that any business application can be built on. The first application is insurance — but the kernel itself has no insurance assumptions. It provides: entity management, messaging, actor processing, role-based access and routing, observability, and versioning. Everything else is domain.

## The Five Kernel Primitives

### 1. Entity
Data with structure, lifecycle, CLI, API, and auto-generated documentation ("skills").

- **Defined as data in MongoDB.** `indemn entity create` writes a definition to the database. The entity framework creates Beanie Document subclasses dynamically from stored definitions at startup.
- **Each entity type gets auto-generated:** CLI commands, API routes, and a skill (markdown documentation).
- **State machines** are optional — activated when defined. Transitions are enforced.
- **Computed fields** (e.g., ball_holder derived from stage) defined declaratively in the entity definition.
- **Relationships** to other entities (Link/BackLink) defined in the entity definition.
- **Provider-specific implementations** — an Outlook email IS an email entity. `indemn email fetch-new` dispatches to the right implementation based on org configuration. The integration layer IS the entity framework. Not a separate layer.
- **Entity type changes trigger rolling restart** of API server and Temporal Workers. CLI is ephemeral (always loads fresh definitions).
- **Schema migration is first-class:** `indemn entity migrate` handles renames, type changes, with batching, dry-run, aliases during migration windows, progress reporting, audit trail, and rollback. Additive changes (new fields) need no migration.

### 2. Message
The nervous system. Generated when entities change. Stored in MongoDB.

- **One save = one event.** A single entity save produces one event with full metadata (method invoked, state transitioned, fields changed). Not separate events per change type.
- **Emission boundary: @exposed method invocations.** Entity changes during a method execution produce one event when the method completes. Individual field changes within a method don't independently generate events.
- **Selective emission:** Only state transitions, @exposed methods, and entity creation/deletion generate messages. Not every field change.
- **Split storage:** `message_queue` (active/pending — hot) and `message_log` (completed — cold). Queue performance never degrades regardless of history.
- **Messages carry entity references, not copies.** The entity in MongoDB is the source of truth. Messages contain entity_type, entity_id, event_type, target_role, correlation_id, and a minimal summary for queue display. Actors load fresh entity data when processing.
- **Written in the same MongoDB transaction as the entity save.** Entity save + watch evaluation + message_queue writes = one atomic transaction.

### 3. Actor
Any participant — human or automated — that processes triggers by executing CLI commands.

- **The OS doesn't distinguish between human and automated actors.** Same queue. Same claiming mechanism (`findOneAndUpdate`). Same visibility. Associates are employees.
- **Actors have roles** (one or more). The role determines what they can access and what comes to them.
- **Three trigger types:**
  - **Message:** a watch on the actor's role matches an entity change
  - **Schedule:** a cron expression fires → creates a message in the queue → same path as message-triggered
  - **Direct invocation:** CLI/API call (used for real-time channels — voice/chat — where latency matters)
- **The actor spectrum:** Deterministic ↔ reasoning ↔ hybrid. The OS doesn't care HOW the actor decides what to do. It just sees: trigger in → CLI commands executed → entity changes out.
- **Associates** are actors with: skills (markdown behavioral instructions), execution mode, and optional LLM configuration. The agent harness is pluggable (harness-agnostic — not tied to LangChain or any specific framework).
- **Skills are always markdown.** Stored in MongoDB. Entity skills are auto-generated documentation. Associate skills are behavioral instructions. Both loaded into agent context. Skills orchestrate entity operations and provide LLM fallback when deterministic capabilities can't handle a case.
- **Claiming is transient** (about the message). **Assignment is persistent** (about the entity). The skill decides when to assign (e.g., underwriter review assigns, classifier does not).

### 4. Role
Defines permissions AND watches. One concept, two functions.

- **Permissions:** which entity types the role can read/write, which operations it can perform.
- **Watches:** what entity changes generate messages for actors with this role. Watches are the wiring mechanism. Actor-centric routing: "what does this role care about?"
- **Watch format:** entity type + event + JSON conditions. One condition language shared by watches and rules. One evaluator.
- **Per-org configurable** via CLI. The entire system behavior is visible via `indemn role list --show-watches`.
- **Watches handle all routing patterns:** sequential pipelines, conditional routing, fan-out, threshold-based triggers.
- **Automatically generates:** queue view (what needs my attention), UI scoping (what I can see), CLI scoping (what commands I have).

### 5. Organization
Multi-tenancy scope. Everything is scoped by org_id.

- **Environments are orgs.** Dev, staging, prod are different organizations. `indemn org clone gic --as gic-staging`. `indemn org diff gic-staging gic`. `indemn deploy --from-org gic-staging --to-org gic`.
- **Separate Atlas clusters for dev and prod** (already in place).
- **Bootstrap entity:** Organization is an entity in the entity framework that the kernel also understands specially (provides org_id scoping).

Actor and Role are also **bootstrap entities** — entities managed through the same CLI/API as everything else, but the kernel depends on them for permissions, routing, and identity.

## Entity Methods and Kernel Capabilities

Entity methods and kernel capabilities are the same thing (unified concept).

- **Kernel capabilities** are reusable entity methods: auto-classify, fuzzy-search, pattern-extract, stale-check, auto-link, auto-route, rule-evaluate. Built into the OS as code. Any entity can activate them.
- **Activated via CLI:** `indemn entity enable Email auto-classify --evaluates classification-rule`
- **Parameterized by per-org configuration:** rules, lookups, thresholds — all created via CLI, stored in MongoDB.
- **The `--auto` pattern:** Entity methods try configured rules deterministically first. If no rule matches, they return `needs_reasoning: true`. The associate's skill provides the LLM fallback.
- **Custom @exposed methods** can be hand-written on entity classes by Tier 3 developers. They appear in CLI/API/skills identically to capability-sourced methods.

**Rules** are per-org condition → action patterns:
```bash
indemn rule create --entity Email --org gic \
  --when '{"all": [{"field": "from_address", "op": "ends_with", "value": "@usli.com"}]}' \
  --action set-fields --sets '{"type": "usli_quote"}'
```

**Lookups** are mapping tables (separate from rules to prevent rule explosion):
```bash
indemn lookup create --org gic --name usli-prefix-lob \
  --data '{"MGL": "general_liability", "XPL": "excess_personal_liability"}'
```

**Veto rules** override positive matches and force reasoning:
```bash
indemn rule create --entity Email --org gic --veto \
  --when '{"all": [{"field": "from_address", "op": "ends_with", "value": "@usli.com"}, {"field": "subject", "op": "contains", "value": "Decline"}]}' \
  --forces-reasoning "USLI email but subject suggests decline"
```

Rule validation at creation: fields must exist in schema, creator must have write permission, state machine fields are excluded from set-fields actions.

## The Unified Queue

MongoDB `message_queue` is the universal work queue. **Both humans and associates see the same items.**

- **Humans** see their queue via UI, claim via UI actions (which call the API).
- **Associates** claim via Temporal workflows. The Queue Processor reads the queue for items targeting roles with associates and starts Temporal workflows. The workflow's first activity claims the message from the queue.
- **If someone else already claimed it** (human got there first, or another associate), the workflow exits gracefully.
- **If Temporal is down,** items stay in the queue. Humans claim them. Nothing is lost. When Temporal recovers, the backlog processes.
- **Gradual rollout:** Add an associate to a role alongside humans. Both see the same queue. The associate processes what it can. Humans handle what it can't. Remove humans from the role when the associate is trusted.

## Temporal Integration

Temporal Cloud ($100/month) is the execution engine for associate work. It provides durable workflows with crash recovery, retries, timeouts, and OTEL tracing.

**What Temporal replaces:** Custom message claiming, visibility timeouts, dead letter queues, retry logic, crash recovery, multi-entity atomicity (saga pattern).

**What Temporal does NOT replace:** Entity framework, CLI/API, watches, kernel capabilities, skills, the MongoDB queue.

**Generic workflow for all associates:**
```
Activity 1: Claim message from MongoDB queue (findOneAndUpdate)
Activity 2: Process (the actor does its thing — loads skills, runs capabilities, LLM if needed)
Activity 3: Complete message (mark complete, move to message_log)
```

The skill is the source of truth for orchestration. The Temporal workflow is a generic durability wrapper. No per-actor workflow code.

**Scheduled tasks create queue items** (same path as message-triggered work):
```
Schedule fires → message created in queue → Temporal workflow starts → claims → processes
```

**Real-time channels** (voice, chat) create a queue entry for visibility AND invoke the associate directly for latency. The direct invocation claims the queue entry immediately.

**Human-in-the-loop:** Works through the queue. Humans see pending items, claim them, process via UI/CLI. The same queue associates use. No separate HITL mechanism.

## Everything Is Data

The OS codebase (git) is the PLATFORM. The database is the APPLICATION.

**MongoDB stores:**
- Entity definitions (schema, state machine, relationships, computed fields, activated capabilities)
- Skills (markdown content)
- Rules and lookups
- Role configurations (permissions, watches)
- Associate configurations
- Entity instances (business data)
- Message queue and message log
- Changes collection (version history for ALL configuration)

**S3 stores:** Unstructured files (PDFs, images, attachments). Referenced by entity fields.

**Temporal Cloud:** Associate execution only. No application data stored.

**OTEL backend (Grafana Cloud):** Ephemeral traces for observability.

## Built-In Version Control

The changes collection records every mutation to every configuration object. It IS the version history.

```bash
indemn history --org gic --last 20          # Recent changes
indemn history --org gic --skill email-classification  # Specific object
indemn org diff gic-staging gic             # Diff between orgs
indemn rollback --org gic --change CHANGE-047  # Roll back specific change
indemn rollback --org gic --to "2026-04-09 14:00"  # Roll back to point in time
indemn org export gic > gic-config.yaml     # Export for backup/review
indemn org import --from-file gic-config.yaml --to gic-new  # Import
```

Bulk deployments via Temporal workflows: `indemn deploy --from-org gic-staging --to-org gic` validates → applies → verifies → rolls back on failure.

## Unified Observability (OTEL)

correlation_id on messages = OTEL trace_id. Everything is one trace:

- Entity changes → OTEL span
- Watch evaluation → OTEL span (child of entity change)
- Rule evaluation → OTEL span (which rules matched, results)
- Message creation → OTEL span
- Temporal workflow → OTEL span (automatic via TracingInterceptor)
- LLM calls → OTEL span (model, tokens, duration)
- CLI commands → OTEL span

All nested in one trace. `indemn trace entity EMAIL-001` queries OTEL data. `indemn trace cascade --id abc-123` shows the full tree.

Three data stores, three purposes, one trace ID:
- **Changes collection:** field-level entity mutations (compliance, years retention)
- **Message log:** completed work items (operations, months-years)
- **OTEL traces:** execution path details (debugging, days-weeks)

## Security Model

- **OrgScopedCollection:** All database access through a wrapper that always injects org_id. Raw Motor collection hidden. Cross-tenant leaks structurally prevented.
- **AWS Secrets Manager:** Per-org credentials (OAuth tokens, API keys). Integration entities store refs, not secrets.
- **Skill content hashing:** Tamper detection on load. Modified skills rejected. Version approval workflow.
- **Rule validation:** State machine fields excluded from set-fields. Fields validated against schema.
- **Sandbox (Daytona):** No outbound network (except CLI), no env var access, no filesystem escape, resource limits.
- **Tamper-evident audit:** Append-only changes collection + sequential hash chain.
- **Separate dev/prod clusters:** Already in place.

## Entry Points

External events enter the OS by creating entities:

| Entry Point | Creates |
|---|---|
| Channel (voice, chat, SMS) | Interaction entity (channel stays open as I/O) |
| Webhook | Entity created or updated |
| API call | Entity created or updated |
| Polling (scheduled) | Entities created (e.g., email fetch-new) |
| CLI command | Entity created or updated |
| Form submission | Entity created |

Once the entity exists, the kernel takes over: watch evaluation → messages → actors → CLI commands → entity changes → more messages → the system churns.

## Standard Entity Library

Seed YAML files in the OS codebase define standard entity types. On `indemn platform init`, a template org is created from seed files. New orgs clone from the template:

```bash
indemn org create gic --from-template standard
```

Updates to the standard library: update seed YAML, run `indemn platform seed --update`. Existing orgs can pull updates selectively.

## Platform Upgrades

Kernel capabilities declare configuration schema versions. Entity definitions store which version they use. Platform upgrades include migration scripts:

```bash
indemn platform upgrade --dry-run  # Shows what would change
indemn platform upgrade            # Runs migrations, auditable, rollbackable
```

## Infrastructure

| Component | Choice | Monthly Cost |
|---|---|---|
| MongoDB Atlas | M10 (MVP), separate dev/prod clusters | $60 |
| Temporal Cloud | Essentials plan | $100 |
| Compute | Railway (MVP) → ECS Fargate (scale) | $30-50 |
| S3 | Single bucket, versioning enabled | $5 |
| OTEL | Grafana Cloud free tier | $0 |
| **Total** | | **~$200/month** |

## How a System Gets Built on the OS

1. **Define domain entities** — `indemn entity create Submission --fields '...' --state-machine '...'`
2. **Activate capabilities** — `indemn entity enable Submission auto-classify --evaluates classification-rule`
3. **Configure per-org rules** — `indemn rule create --entity Submission --org gic --when '...' --then '...'`
4. **Define roles with watches** — `indemn role create classifier --watches '...'`
5. **Create associates** — `indemn associate create --name "Classifier" --role classifier --skill email-classification`
6. **Assign humans to roles** — `indemn actor add-role jc@gicunderwriters.com --role underwriter`
7. **Schedule infrastructure** — `indemn associate create --name "Email Sync" --trigger "schedule:*/1 * * * *" --skill email-fetching`
8. **The system runs** — entities change → watches match → actors process → entity changes → the system churns

## What's Still Open

- **No single kernel specification.** This document is the closest, but it needs to become the actionable spec.
- **GIC end-to-end retrace** with the final architecture (initial trace was pre-Temporal, pre-unified-queue).
- **Simplification pass** — Craig: "a lot of this can be simplified."
- **Testing/debugging CLI** — commands sketched but not specified.
- **Declarative system definition** — YAML manifests for `indemn system apply` not finalized.
- **Bulk operations** — concept raised but not designed.
- **Rule composition details** — AND/OR/NOT, lookups, veto rules, groups — conceptually decided, not fully specified.
- **Build order** — what gets built first, acceptance criteria.
- **Stakeholder engagement** — Ryan → Dhruv → George → Kyle/Cam.
