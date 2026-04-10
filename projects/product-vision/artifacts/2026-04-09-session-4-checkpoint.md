---
ask: "Comprehensive checkpoint of session 4 — what was accomplished, how the thinking evolved, what's decided, what's still open"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08/09
sources:
  - type: conversation
    description: "Craig and Claude — full-day session pressure-testing and refining OS primitives against real systems"
---

# Session 4 Checkpoint

## What This Session Was About

Session 3 ended with a core unresolved question: "How does the system wire entity changes to consequences?" Four approaches had been tried (routing rules, implicit wiring, connections, subscriptions) and none clicked.

Session 4 started by reading ALL 27 prior artifacts to have complete context. Then, instead of trying to solve the wiring question in the abstract, we pressure-tested the architecture against a real production system (GIC Email Intelligence) and let the answer emerge from real usage.

## The Journey — How Thinking Evolved

### Phase 1: GIC Deep Dive
Three parallel research agents explored the GIC email intelligence codebase, project artifacts, and infrastructure. This gave us: the complete data model (8 entities, 14 email types, 8-stage submission lifecycle), the full processing pipeline (sync → extract → classify → link → assess → draft), carrier logic (USLI/Hiscox/Granada), ball holder tracking, hard rules overriding LLM, fuzzy matching, and all the real-world edge cases.

### Phase 2: Wiring Question Resolved — Watches
Tracing GIC through the OS primitives revealed: the wiring mechanism should be **watches on roles** — actor-centric ("what does this role care about?") rather than system-centric ("when X happens, route to Y"). Watches are: entity type + event + conditions. One mechanism for all cases (sequential pipeline, conditional routing, fan-out, threshold-based). Configurable per org via CLI. Visible at a glance with `indemn role list --show-watches`.

### Phase 3: The Actor Spectrum
Craig's insight: deterministic and reasoning actors shouldn't be separate mechanisms. An associate that classifies USLI emails (deterministic — check the domain) and classifies unknown emails (reasoning — use LLM judgment) should be ONE framework. The resolution: **the actor is the executor, the skill is the program, the interpreter can be deterministic or LLM-based.** The OS doesn't care how the actor decides — it just sees CLI commands being executed.

### Phase 4: Entity Polymorphism for Integrations
Craig's insight: an Outlook email IS an email entity. External system integration isn't a separate "adapter layer" — it's how the entity is implemented for that provider. `indemn email fetch-new` works regardless of provider. **This collapsed Layer 4 (integrations) into Layer 1 (entity framework).** One primitive, not two.

### Phase 5: Kernel vs. Domain Separation
Actor and Role aren't domain entities — they're the OS itself. The distinction: **OS primitives (the kernel)** are Entity framework, Message, Actor, Role, Organization. **Domain entities** are built ON the kernel (Submission, Email, etc.). Both have CLI. Both are queryable. But kernel primitives exist at a different level. The kernel starts bare — domain-specific things are NOT baked in.

### Phase 6: Entry Points and Triggers
Channels (voice, chat, SMS) aren't trigger types — they're entry points that create entities. Then the kernel takes over. Three trigger types for actors: **message** (watch matches entity change), **schedule** (cron), **direct invocation** (CLI/API call). Everything else (webhooks, API calls, form submissions) creates entities, which flow through the message system.

### Phase 7: Assignment Simplified
Assignment is NOT a kernel primitive (varies too much by domain). Messages always target **roles**, not actors. Messages carry entity context (via enrichment). Actor-specific filtering is a query, not routing. Entities can have fields that reference actors (e.g., submission.underwriter = JC) — these are domain fields, not kernel concepts. Queue queries filter by context. No `target-from-field`. No special actor reference types. The kernel does less. The domain has full flexibility.

### Phase 8: Kernel Capabilities Model
Craig's concern: deterministic logic shouldn't require writing Python code (breaks CLI-configurable promise). Resolution: **kernel capabilities** are reusable entity methods (auto-classify, fuzzy-search, pattern-extract, stale-check) activated on entities via CLI and parameterized by per-org configuration (rules, lookups, thresholds). Skills (markdown) orchestrate capabilities and provide LLM fallback when capabilities can't handle a case.

### Phase 9: Temporal Integration
Temporal replaces custom message queue infrastructure (claiming, timeouts, dead letters, retry, crash recovery). Key insight from validation: **human queues stay in MongoDB. Temporal is the execution engine for associates only.** The unified queue (MongoDB message_queue) is where ALL work lives. Associates claim from it via Temporal workflows. Humans claim from it via UI. Same queue. Same visibility. Interchangeable actors. Associates are employees.

### Phase 10: Everything Is Data
Entity definitions, skills, rules, lookups, associate configs — all stored in MongoDB, not in code files. The OS codebase (git) is the PLATFORM. The database is the APPLICATION. Environments (dev/staging/prod) are just different orgs. `indemn org clone`, `indemn org diff`, `indemn deploy` manage the lifecycle. Built-in version control via the changes collection. No git repos per tenant.

### Phase 11: Three Rounds of Architecture Ironing
Systematically found and resolved 19 architectural inconsistencies across three rounds:
- Round 1 (7 issues): skill vs. workflow orchestration, entity creation, outbox elimination, scheduled tasks, real-time, bootstrap entities, context depth
- Round 2 (5 issues): capabilities + entity methods unified, condition language unified, message data, entity skills vs. associate skills, audit systems
- Round 3 (7 issues): event granularity, emission boundary, Queue Processor, claiming vs. assignment, bootstrap circularity, schema evolution, condition format (JSON only)

### Phase 12: Security and Operations Hardening
Three independent reviewers (platform engineering, DevOps, security) attacked the architecture. 14 findings across critical/high/medium severity. All 14 addressed with solutions that add no new infrastructure and no new architectural concepts — just enforcement, validation, and discipline applied to existing patterns.

## What's DECIDED (Do Not Re-Litigate)

### Kernel Primitives
1. **Entity** — data with structure, lifecycle, CLI/API, auto-generated skills. Definitions stored in MongoDB. Framework creates Beanie classes dynamically from stored definitions. Provider-specific implementations (Outlook email IS an email entity).
2. **Message** — generated by entity changes (one save = one event). Stored in MongoDB message_queue. Split into message_queue (hot/active) and message_log (cold/completed). Contains entity references (not copies) — entities are source of truth.
3. **Actor** — identity + role(s). Processes triggers by executing CLI commands. Human or automated. The OS doesn't distinguish. Associates are employees.
4. **Role** — permissions (what you can access) + watches (what entity changes you care about). Watches ARE the wiring. Per-org configurable. The entire system behavior is visible via `indemn role list --show-watches`.
5. **Organization** — multi-tenancy scope. Environments are orgs. `indemn org clone/diff/deploy`.

### Architecture Decisions
6. **Watches** as the wiring mechanism — actor-centric routing.
7. **One condition language** — JSON format, shared by watches and rules. One evaluator.
8. **Kernel capabilities = entity methods** — unified concept. Reusable methods activated on entities via CLI, parameterized by per-org config.
9. **Skills are markdown** — stored in MongoDB. Entity skills (auto-generated docs) + associate skills (behavioral instructions). Both loaded into agent context.
10. **Everything is data** — entity definitions, skills, rules, lookups, configs stored in MongoDB. OS codebase (git) is the platform. Database is the application.
11. **Temporal for associate execution** — durable workflows with crash recovery, retries, timeouts. NOT for human queues.
12. **Unified MongoDB queue** — message_queue is the universal work queue. Humans and associates see the same items. Associates claim via Temporal workflow. Humans claim via UI.
13. **OTEL baked in** — correlation_id = trace_id. Entity changes, rule evaluations, LLM calls, Temporal workflows — all spans in one trace.
14. **Audit trail** — changes collection records every mutation. Append-only + hash chain for tamper evidence. Three systems (changes, message_log, OTEL) linked by trace_id.
15. **Assignment is a domain concern** — not a kernel primitive. Entity fields can reference actors. Queue queries filter by context. Claiming is transient (message-level). Assignment is persistent (entity-level). The skill decides when to assign.
16. **Schema migration is first-class** — `indemn entity migrate` with batching, dry-run, aliases during migration window, progress reporting, audit.
17. **Rolling restart on entity type changes** — Beanie for everything, definitions from DB, restart on type changes. CLI is ephemeral (always fresh).
18. **Seed YAML + template org** for standard entity library bootstrap.
19. **Capability schema versioning** for platform upgrades.
20. **Scheduled tasks create queue items** — same path as message-triggered work. All work through the queue.
21. **Real-time channels** — create queue entry for visibility + direct invocation claims immediately for latency.
22. **Generic Temporal workflow** — claim → process → complete. Skill is source of truth for orchestration. No per-actor workflow code.

### Security Decisions
23. **OrgScopedCollection wrapper** — all DB access through wrapper that always injects org_id.
24. **AWS Secrets Manager** for per-org credentials. Integration entities store refs, not secrets.
25. **Skill content hashing + version approval** — tamper detection, modification requires approval.
26. **Rule validation at creation** — state machine fields excluded from set-fields actions.
27. **Sandbox contract** — no network, no env vars, no filesystem escape. Enforced by Daytona.
28. **Separate dev/prod clusters** — already in place.

### Infrastructure
29. **MongoDB Atlas** — entity storage, message queue, configuration, audit trail
30. **S3** — unstructured files (PDFs, images), referenced by entity fields
31. **Temporal Cloud** ($100/month) — associate execution engine
32. **OTEL backend** (Grafana Cloud) — observability
33. **Deployment** — Railway (MVP) → ECS Fargate (scale)
34. **Estimated MVP cost** — ~$200/month

## What's STILL OPEN

### Architecture
- **The GIC pipeline has NOT been retraced end-to-end with the final architecture.** The initial trace was done before major changes (Temporal, unified queue, everything-is-data, schema migration). A fresh trace against the final architecture would validate everything holds together.
- **EventGuard, CRM, and CMS end-to-end traces were high-level.** They validated the primitives work but weren't traced at the GIC level of detail.

### Operational Surface (Discussed but Not Fully Designed)
- **Testing/debugging CLI** — commands sketched (`indemn trace`, `indemn queue show`, `indemn simulate`) but not specified in detail.
- **Declarative system definition** — YAML manifests for `indemn system apply` discussed but format not finalized.
- **Bulk operations** — `indemn entity import` concept raised but not designed.
- **Rule composition details** — AND/OR/NOT, lookups vs. rules, veto rules, rule groups. Conceptually decided, not specified.

### Specification
- **No single source of truth document.** The architecture is spread across 10+ session 4 artifacts. Needs consolidation into one specification.
- **The specification should be actionable** — clear enough that an engineer (or an agent) can start building from it.
- **Simplification pass needed.** Craig's instinct: "a lot of this can be simplified." The theoretical discussions may have over-specified things that are simpler in practice.

### Implementation
- **Build order** — hand-build first, extract framework. But what specifically gets built first, in what order, with what acceptance criteria?
- **The first entity** — which entity do we build by hand to prove the patterns? (Probably tied to the GIC retrace.)
- **Kernel capabilities** — which capabilities are needed for the first use case?
- **Temporal integration specifics** — workflow definitions, activity patterns, worker configuration.

### Stakeholder Engagement
- **Ryan, Dhruv, George engagement** — designed but not started during this session.
- **Champion strategy** — how Craig presents the vision to the company.
- **The deliverable format** — what does the final roadmap/vision document look like?

## All Artifacts From This Session (10 new)

| Artifact | What It Captures |
|----------|-----------------|
| `2026-04-08-actor-spectrum-and-primitives.md` | The actor spectrum insight — deterministic/reasoning as interpreter choice, not separate mechanisms. Entity polymorphism for integrations. |
| `2026-04-08-primitives-resolved.md` | Watches as wiring, actor definition, entity/actor boundary, scheduled tasks. The four open questions answered. |
| `2026-04-08-entry-points-and-triggers.md` | How external events enter the OS. Three trigger types. Channels are entry points, not triggers. |
| `2026-04-08-kernel-vs-domain.md` | Kernel primitives vs. domain entities. Assignment not a primitive. Actor references via context. |
| `2026-04-08-pressure-test-findings.md` | First round of independent reviews (platform architect, DX, distributed systems). 8 key findings. |
| `2026-04-08-actor-references-and-targeting.md` | Messages target roles, context enables filtering. No target-from-field. Entities are source of truth. |
| `2026-04-09-entity-capabilities-and-skill-model.md` | Kernel capabilities + per-org config + markdown skills. The "auto" pattern. GIC pipeline mapped. |
| `2026-04-09-capabilities-model-review-findings.md` | Second round of reviews (scalability, GIC e2e trace, rule engine). Findings on multi-entity atomicity, rule composition, evaluation traces. |
| `2026-04-09-temporal-integration-architecture.md` | How Temporal fits. What it replaces. GIC pipeline on Temporal. OTEL unification. |
| `2026-04-09-unified-queue-temporal-execution.md` | THE key insight: one queue for everyone. Associates are employees. Temporal for execution, MongoDB for visibility. Gradual rollout. |
| `2026-04-09-data-architecture-everything-is-data.md` | Entity definitions, skills, rules as database data. Built-in version control. Environments as orgs. The complete data architecture. |
| `2026-04-09-architecture-ironing.md` | Round 1: 7 issues resolved (skill/workflow, entity creation, outbox, schedules, real-time, bootstrap, context). |
| `2026-04-09-architecture-ironing-round-2.md` | Round 2: 5 issues resolved (capabilities+methods, conditions, message data, skill types, audit systems). |
| `2026-04-09-architecture-ironing-round-3.md` | Round 3: 7 issues resolved (event granularity, emission, Queue Processor, claiming/assignment, bootstrap circularity, schema evolution, JSON conditions, versioning). |
| `2026-04-09-data-architecture-review-findings.md` | Third round of reviews (platform eng, DevOps, security). 14 findings with priority matrix. |
| `2026-04-09-data-architecture-solutions.md` | All 14 findings addressed. Solutions maintain simplicity. No new infrastructure. |
| `2026-04-09-session-4-checkpoint.md` | THIS FILE. |

## How to Resume (Next Session)

### Context Loading
1. Read this checkpoint FIRST — it has the complete journey and current state
2. Read `2026-04-09-unified-queue-temporal-execution.md` — the core architectural insight (unified queue, associates as employees)
3. Read `2026-04-09-data-architecture-everything-is-data.md` — the data architecture
4. Read `2026-04-09-data-architecture-solutions.md` — all security/ops solutions
5. If needed for specific topics: read the relevant ironing or review artifacts

### What Craig Said That Matters
- "I think there's still a ways to go for us to feel really confident about this."
- "A lot of this can be simplified."
- "Overall, I don't think the system is complicated for us to implement, as long as we're clear about what we're building, why, and how it should be used, and we document everything."
- "The context matters a lot, because the iteration and the whole process are important for understanding how we got from the beginning to the end."
- The architecture needs to become ACTIONABLE — clear enough to build from.

### Suggested Next Steps
1. **Consolidate into a single specification.** Take all artifacts from sessions 1-4 and produce one document: "The OS Kernel Specification." What we're building, why, how it works, how to use it.
2. **Retrace GIC end-to-end with the final architecture.** Validate every decision holds up when you walk through real email → submission → assessment → draft → human review.
3. **Simplification pass.** Read the spec with fresh eyes and ask: "Is this simpler than it needs to be?" Remove anything that doesn't earn its complexity.
4. **Build order.** Define what gets built first, what the acceptance criteria are, and how to validate each piece.
5. **First entity by hand.** Build one entity (probably Email or Submission) end-to-end: definition in DB, Beanie class, CLI, API, skill, watches, rule evaluation, Temporal workflow, queue. Prove the full stack works.
