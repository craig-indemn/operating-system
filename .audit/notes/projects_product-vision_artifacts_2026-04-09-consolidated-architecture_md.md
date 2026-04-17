# Notes: 2026-04-09-consolidated-architecture.md

**File:** projects/product-vision/artifacts/2026-04-09-consolidated-architecture.md
**Read:** 2026-04-16 (full file — 273 lines)
**Category:** design-source

## Key Claims

- **Domain-agnostic OS kernel.** First application is insurance; kernel has no insurance assumptions. Provides: entity management, messaging, actor processing, role-based access + routing, observability, versioning.
- **5 kernel primitives at this point**: Entity, Message, Actor, Role, Organization. Assignment is described as a domain pattern; Integration is collapsed into Entity framework (not yet restored as primitive). **Later superseded**: Integration promoted to primitive #6 (2026-04-10-integration-as-primitive.md); Assignment position re-examined.
- **Entity defined as data in MongoDB** — `indemn entity create` writes definition; entity framework creates Beanie Document subclasses dynamically at startup from definitions.
- **Each entity type gets auto-generated CLI commands, API routes, and skill markdown.**
- **State machines optional**, activated when defined. Transitions enforced.
- **Computed fields, relationships (Link/BackLink), provider-specific implementations** declared in entity definition.
- **Entity type changes trigger rolling restart** of API server and Temporal Workers. CLI ephemeral.
- **Schema migration first-class** (`indemn entity migrate`).
- **One save = one event.** Emission boundary = @exposed method completion. Selective emission: state transitions + @exposed methods + create/delete only.
- **Message split**: message_queue (hot) + message_log (cold). Messages carry entity references, not copies.
- **Entity save + watch eval + message_queue writes = ONE atomic MongoDB transaction.**
- **Unified queue**: humans + associates see same items. Same claim mechanism. Associates = employees.
- **Temporal Integration** (Temporal Cloud, $100/mo): execution engine for associate work. Generic `ProcessMessageWorkflow` wraps claim → process → complete. Skill is source of truth for orchestration.
- **Real-time channels** create queue entry AND invoke associate directly (direct invocation claims the entry immediately).
- **Changes collection IS the version history** (dual purpose).
- **OTEL observability unified**: correlation_id = trace_id. Everything one trace.
- **3 data stores, 3 purposes**: Changes collection (compliance, years), Message log (operations, months-years), OTEL traces (debugging, days-weeks).
- **Security model**: OrgScopedCollection, AWS Secrets Manager, skill content hashing, rule validation, Daytona sandbox, append-only changes + hash chain, separate dev/prod clusters.
- **Entry points (for creating entities)**: Channel (voice/chat/SMS), Webhook, API call, Polling (scheduled), CLI command, Form submission. Once entity exists, kernel takes over via watches.
- **Infrastructure cost ~$200/mo MVP**: MongoDB Atlas M10 ($60), Temporal Cloud ($100), Railway ($30-50), S3 ($5), Grafana Cloud free ($0).

## Architectural Decisions

- **5 primitives at this point.** Integration collapsed into Entity; Assignment described as a pattern, not primitive. (Both later revised.)
- **Entity definitions live in MongoDB** (NOT class files on disk) — superseding the round-3 mention of "updates the Python class file."
- **Rolling restart on entity type changes** — accepted tradeoff.
- **CLI is ephemeral** (loads fresh definitions per invocation); API Server + Temporal Workers restart.
- **Generic single workflow for all associate processing** — no per-associate workflow code.
- **Scheduled tasks = create queue item** (same path as message-triggered).
- **Real-time channels = queue entry + direct invocation** (parallel).
- **Three observability data stores with different retention** — clear separation of concerns.
- **Harness-agnostic agent**: "The agent harness is pluggable (harness-agnostic — not tied to LangChain or any specific framework)." This is the KEY LLM-agnostic claim at the architecture level.
- **Assignment is skill-decided, not kernel-mandatory** — consistent with round-3 architecture ironing.

## Layer/Location Specified

- **Entity framework, message system, watch system, role/permissions, capabilities, rules, lookups** — all kernel code.
- **Queue (message_queue/log)** = kernel-managed MongoDB.
- **Queue Processor** = kernel process.
- **Changes collection** = kernel-managed MongoDB, append-only.
- **Entity storage** = MongoDB via Beanie.
- **Temporal Cloud** = external service, executes associate workflows. **Worker location NOT explicitly specified in this artifact** — left open.
- **OrgScopedCollection / PlatformCollection** = kernel code wrapper.
- **AWS Secrets Manager** = external. Integration stores `secret_ref`.
- **Daytona** = external sandbox. Agent execution wrapped by Daytona.
- **Agent harness** = "pluggable, harness-agnostic, not tied to LangChain or any specific framework." Location: stated as "the agent harness" as a concept, not placed in a process.
- **Deployment**: Railway MVP → ECS Fargate scale.

**Finding 0 relevance**:
- This artifact is **April 9**, before the harness pattern was formalized (April 10).
- It explicitly says the agent harness is "pluggable" and "harness-agnostic" — consistent with the April 10 design placing the harness outside the kernel.
- But it does NOT yet say "the harness is a separate image." That formalization is in 2026-04-10-realtime-architecture-design.md.
- The Phase 2-3 spec that violates Finding 0 took the "pluggable" language to mean "LLM provider is configurable within kernel code," not "LLM execution is outside kernel." The April 10 realtime-architecture-design locks the stronger interpretation.

## Dependencies Declared

- MongoDB Atlas M10 (MVP)
- Temporal Cloud (Essentials)
- Railway / ECS Fargate
- S3
- Grafana Cloud (OTEL backend)
- Beanie, Pydantic, FastAPI, Typer
- AWS Secrets Manager
- Daytona (sandbox)

## Code Locations Specified

- Conceptual (no absolute paths):
  - Entity framework → Beanie Documents created dynamically
  - `message_queue` + `message_log` collections
  - `changes` collection with hash chain
  - `ProcessMessageWorkflow` Temporal generic
  - OTEL spans at every primitive
  - Direct-invocation pattern
  - CLI surface: `indemn entity`, `indemn rule`, `indemn role`, `indemn associate`, `indemn actor`, `indemn history`, `indemn rollback`, `indemn org`, `indemn deploy`, `indemn trace`, `indemn queue`
- Implementation mapping (Pass 2 + spec cross-references):
  - All of the above appear in Phase 0-1 + Phase 2-3 consolidated specs.

## Cross-References

- 2026-04-08 primitives-resolved + kernel-vs-domain + pressure-test-findings + entry-points-and-triggers (precursors)
- 2026-04-09 data-architecture-everything-is-data + data-architecture-solutions + temporal-integration-architecture + unified-queue-temporal-execution + entity-capabilities-and-skill-model (same-session siblings)
- 2026-04-09 architecture-ironing (Rounds 1, 2, 3) — encoded decisions
- 2026-04-10-integration-as-primitive.md — SUPERSEDES the "Integration collapsed into Entity" position
- 2026-04-10-realtime-architecture-design.md — formalizes harness pattern (location locked as "outside kernel")
- 2026-04-13-white-paper.md — final consolidation
- 2026-04-13-simplification-pass.md — applies additional simplifications
- Phase 0-1 + 2-3 consolidated specs — implementation of this architecture (with Finding 0 deviation at Phase 2-3)

## Open Questions or Ambiguities

Listed at end of artifact:
- No single kernel spec (this is closest, but needs becoming actionable spec)
- GIC end-to-end retrace with final architecture (pre-Temporal trace stale)
- Simplification pass pending (Craig: "a lot of this can be simplified")
- Testing/debugging CLI not specified
- Declarative system definition YAML not finalized
- Bulk operations design
- Rule composition details (AND/OR/NOT, lookups, veto rules, groups)
- Build order + acceptance criteria
- Stakeholder engagement sequence

**All resolved in later artifacts** (April 10+ retraces, bulk-operations-pattern, realtime-architecture-design, simplification-pass, white paper, consolidated specs).

**Supersedence note**:
- "5 primitives" → updated to 6 (Integration restored, 2026-04-10).
- "Integration collapsed into Entity" → REVERSED.
- Harness location (left open here) → CLOSED as "outside kernel" (2026-04-10-realtime-architecture-design.md).
- All other claims SURVIVE.
