# Cross-Reference Matrix — Spec-vs-Implementation Pass 2 (Architectural Layer)

Generated: 2026-04-16

Files audited: 104

---

## Layer / Location Declarations

Where each artifact says things should live. Discrepancies between artifacts indicate Finding 0-class deviations.

| Source File | Category | Layer/Location Declared |
|---|---|---|
| `2026-04-13-white-paper.md` | design-source | - **Kernel processes (inside trust boundary, share one image):** API Server, Queue Processor, Temporal Worker |   - API Server: "The gateway. REST API, WebSocket for real-time UI updates, webhook endp |
| `2026-04-10-realtime-architecture-design.md` | design-source | **THIS IS THE CRITICAL ARTIFACT FOR FINDING 0.** The harness pattern is defined here with explicit layer placement: |  | - **Harness = deployable image outside kernel.** Part 4: "A harness is the glue |
| `2026-04-10-integration-as-primitive.md` | design-source | - **Adapters = kernel code**. Layer table (line 68-72): |   - **Integration** (primitive) — "The record: provider, owner, credentials, status" — lives in MongoDB as a bootstrap entity, managed via CLI |
| `2026-03-30-design-layer-3-associate-system.md` | design-source | This is the earliest design document for the associate system. It pre-dates the harness-pattern formalization (which came in 2026-04-10-realtime-architecture-design.md). Key layer statements: |  | - * |
| `2026-04-09-entity-capabilities-and-skill-model.md` | design-source | - **Kernel capabilities**: "Code (Python, maintained by Indemn/Tier 3 developers)" — live in the kernel codebase as code additions. Code location. | - **Per-org configuration**: "Data (created via CLI |
| `2026-04-11-authentication-design.md` | design-source | **All authentication mechanics are explicitly kernel-side:** |  | - "Kernel handles mechanics (validation, session lifecycle, token issuance, MFA challenge flow)." | - "Domain or per-org config decide |
| `2026-04-10-bulk-operations-pattern.md` | design-source | - **`bulk_execute` Temporal workflow = kernel code.** Line 55: "One workflow definition in kernel code handles all bulk operations." | - **Auto-generated CLI per entity**: "thin wrapper that construct |
| `2026-04-11-base-ui-operational-surface.md` | design-source | **THIS ARTIFACT DIRECTLY TIES THE ASSISTANT TO THE HARNESS PATTERN.** |  | Critical claims (line 167, 306, 346-347): | - "Because the conversation panel is a running harness instance — a real-time act |
| `2026-04-09-data-architecture-everything-is-data.md` | design-source | - **Kernel (Git) = PLATFORM code**, specifically: |   - The kernel (entity framework, condition evaluator, queue processor, Temporal integration) |   - Kernel capabilities (reusable entity methods — a |
| `2026-04-13-simplification-pass.md` | design-source | - **Coalescing**: explicitly moved OUT of the kernel. Now UI-only. | - **Rule evaluation trace**: explicitly removed as a separate concept — now metadata on the existing changes collection. | - **No o |
| `2026-04-10-base-ui-and-auth-design.md` | design-source | - **Base UI is outside the kernel** — it's "a consumer of entity API + the same auth context." No direct database access. | - **Identity providers are Integrations** — credentials and config in Integr |
| `2026-04-10-post-trace-synthesis.md` | design-source | This is a synthesis document; it doesn't itself introduce layer/location claims. It points to where the follow-up design work should happen. |  | Layer-relevant framings in this artifact: | - **Bulk o |
| `2026-04-14-impl-spec-phase-0-1-consolidated.md` | spec | - **Kernel code** lives in `kernel/` directory: |   - `kernel/entity/` (framework) |   - `kernel/message/` (queue + emit) |   - `kernel/watch/` (cache, evaluator, scope) |   - `kernel/rule/` (engine,  |
| `2026-04-14-impl-spec-phase-2-3-consolidated.md` | spec | **CRITICAL — This is the Finding 0 source in the spec:** |  | The Phase 2 spec places agent execution INSIDE THE KERNEL at these specific locations: |  | | Location | Content | | |---|---| | | `kernel |
| `2026-04-14-impl-spec-phase-4-5-consolidated.md` | spec | ### Phase 4 Locations | - **UI code** in `ui/src/` — React app, runs in browser | - **UI WebSocket handler** in `kernel/api/websocket.py` — kernel-side | - **Entity metadata endpoint** in `kernel/api/ |
| `2026-04-14-impl-spec-phase-6-7-consolidated.md` | spec | **This spec is largely OPERATIONAL — it's about configuring data in the deployed OS, not adding code.** |  | No kernel-side layer additions are specified. All activity is CLI-based configuration: | -  |
| `activities.py` | code | **EXACT SOURCE OF FINDING 0.** |  | - **Agent execution runs inside `kernel/temporal/activities.py`** — a kernel module. | - **The module runs in the kernel Temporal Worker process** — a kernel proces |
| `assistant.py` | code | **Wrong layer per design.** |  | - **This code**: `kernel/api/assistant.py` — runs inside kernel API server process, with direct DB access. | - **Per design (2026-04-11-base-ui-operational-surface.md  |
| `workflows.py` | code | - This file: `kernel/temporal/workflows.py` — kernel code, runs in the kernel Temporal Worker process. | - Workflows are registered by `kernel/temporal/worker.py` in `task_queue="indemn-kernel"`. |  | |
| `worker.py` | code | **This file is the kernel Temporal Worker entry point.** |  | - Runs as `python -m kernel.temporal.worker`. | - Deployed as the `indemn-temporal-worker` Railway service per Phase 0-1 spec. | - Inside  |
| `adapter.py` | code | - Adapters are kernel code, per design (2026-04-10-integration-as-primitive.md line 71: "Python in the OS codebase (platform code)"). | - `kernel/integration/adapter.py` — the correct location. | - Ma |
| `registry.py` | code | - Kernel code in `kernel/integration/registry.py`. | - In-process registry (no external state). | - Per design (2026-04-10-integration-as-primitive.md): "Adapter registry keyed by version: `ADAPTER_RE |
| `dispatch.py` | code | - Kernel code: `kernel/integration/dispatch.py`. | - Correct layer per design (Integration primitive + adapters as kernel code). | - Entry point for all adapter usage — ensures consistent auth handlin |
| `resolver.py` | code | - Kernel code: `kernel/integration/resolver.py`. | - Matches design: resolver logic lives in kernel. | - No layer deviation. |
| `websocket.py` | code | - Kernel code: `kernel/api/websocket.py`. | - Runs in kernel API server process. | - Direct MongoDB access (uses `get_database()` which is inside trust boundary). | - Per design (2026-04-11-base-ui-op |
| `events.py` | code | - Kernel code: `kernel/api/events.py`. | - Runs in kernel API server process. | - Direct database access to `message_queue` Change Stream. | - Per design: the `indemn events stream` CLI is a long-runn |
| `interaction.py` | code | - Kernel code: `kernel/api/interaction.py`. | - Handoff mechanics live in the kernel — correct per design. | - Per design (2026-04-10-realtime-architecture-design.md Part 6 Handoff): "Handoff between  |
| `generator.py` | code | - Kernel code: `kernel/skill/generator.py`. | - Per design (2026-04-09-entity-capabilities-and-skill-model.md): "entity skills are auto-generated from entity definitions." Implementation matches desig |
| `schema.py` | code | - Kernel code: `kernel/skill/schema.py`. | - Beanie document — registered with the kernel's `init_beanie` at startup. | - Per design: skills are data in MongoDB, loaded at runtime. |  | **No layer dev |
| `session_manager.py` | code | - Kernel code: `kernel/auth/session_manager.py`. | - Matches design (2026-04-11-authentication-design.md): session lifecycle is kernel-side. | - Runs in kernel API server process (called by auth endpo |
| `jwt.py` | code | - Kernel code: `kernel/auth/jwt.py`. | - Runs in kernel API server process (tokens created at login, verified on every request). | - `watch_revocations` runs as a background task in the API server. |  |
| `auth_routes.py` | code | - Kernel code: `kernel/api/auth_routes.py`. | - Runs in kernel API server process. | - All auth flows live in the kernel per design. |  | **No layer deviation.** |  | Per design (2026-04-11-authentica |
| `registration.py` | code | - Kernel code: `kernel/api/registration.py`. | - Runs in kernel API server. | - Uses `find_scoped`, `get_scoped`, `save_tracked` — all through OrgScopedCollection + save_tracked in kernel. | - Bulk en |
| `bulk.py` | code | - Kernel code: `kernel/api/bulk.py`. | - Bulk ops are a kernel-provided pattern per design — runs in kernel Temporal worker. | - This file is the API surface for bulk operations; the actual workflow + |
| `AssistantProvider.tsx` | code-ui | - UI code: `ui/src/assistant/AssistantProvider.tsx`. | - Runs in browser. | - Talks to kernel API endpoint `/api/assistant/message` (in kernel/api/assistant.py). |  | **Layer issue (inherited from ker |
| `useAssistant.ts` | code-ui | - UI code: `ui/src/assistant/useAssistant.ts`. | - Runs in browser. | - Pure React — no external dependencies. |  | **No layer concerns for this file.** It's just a React context helper. |
| `org_lifecycle.py` | code | - Kernel code: `kernel/api/org_lifecycle.py`. | - Called by admin routes and CLI commands (`indemn org export/import/clone/diff/deploy`). | - Direct MongoDB access (uses `get_database()` + Beanie docu |
| `cache.py` | code | - Kernel code: `kernel/watch/cache.py`. | - Runs in whichever kernel process loads it (API Server for watch evaluation during save_tracked). | - Per design: watch evaluation is kernel-side; cache impr |
| `evaluator.py` | code | - Kernel code: `kernel/watch/evaluator.py`. | - Pure module — no external dependencies beyond stdlib. | - Used by watches during emission (in `kernel/message/emit.py`) and by rules (`kernel/rule/engin |
| `Dockerfile` | infrastructure | - **This is the KERNEL image** per white paper § Service Architecture: "Three kernel processes share one image with different entry points." | - The image contains `kernel/`, `kernel_entities/`, `seed |
| `docker-compose.yml` | infrastructure | - Two kernel processes run in local dev: API Server, Queue Processor. | - Temporal dev server runs locally. | - **The Temporal Worker (`kernel/temporal/worker.py`) is missing from docker-compose.yml.* |
| `2026-03-24-associate-domain-mapping.md` | design-source | - **This artifact is early-session domain mapping.** It does NOT specify kernel/harness/code paths. | - Key constraint it establishes: the platform must model ~20 domain objects generically; each asso |
| `2026-03-24-source-index.md` | design-source | - None. Source index only. |
| `2026-03-25-associate-architecture.md` | design-source | - "Bot-service as deployment/hosting layer (or its evolution)" — tentative. The later 2026-04-10-realtime-architecture-design.md resolved this: bot-service is legacy, the OS uses harness images per ki |
| `2026-03-25-domain-model-research.md` | design-source | - "Platform layer" (Associate, Skill, Workflow, Rule, Template, KnowledgeBase, Channel, Organization, Project, Task, Interaction, Correspondence, Document, Email, Draft, ParameterAudit) — these are wh |
| `2026-03-25-domain-model-v2.md` | design-source | - **Platform layer vs Insurance domain separation** — same split as earlier domain-model-research. | - Platform entities: Associate, Skill, Workflow, Template, KnowledgeBase, Organization, Task, Docum |
| `2026-03-25-platform-tiers-and-operations.md` | design-source | - No code-layer or process-layer claims. | - Business/operational claims only. | - Tier 3 signup self-service → later becomes the auth-design Tier 3 signup flow. | - "What you build deploys and runs O |
| `2026-03-25-session-notes.md` | design-source | - None. Session notes document intent and context, not code placement. |
| `2026-03-25-the-operating-system-for-insurance.md` | design-source | - No code paths or process topology. Vision-level framing. | - Implicit: OS is ONE deployment; customers run ON it (not self-hosted). Later formalized as PaaS. |
| `2026-03-25-why-insurance-why-now.md` | design-source | - No code paths or process placement. | - Platform-level business framing only. |
| `2026-03-30-design-layer-1-entity-framework.md` | design-source | - **One deployable unit** — modular monolith, single process. Consistent with later "one image, three entry points" decision. | - Code organized by sub-domain under `sub_domains/` directory. | - `plat |
| `2026-03-30-entity-system-and-generator.md` | design-source | - **Generator as core kernel capability.** Later: kernel capabilities library includes auto-classify, fuzzy-search, pattern-extract, stale-check, etc. The entity generator itself becomes part of the k |
| `2026-03-30-vision-session-2-checkpoint.md` | session-checkpoint | - No new layer specifications beyond what's in the 7 summarized artifacts. | - Confirms: modular monolith, MongoDB, generator kernel. | - Still pre-dates harness pattern (Session 5) and "everything is |
| `2026-04-02-core-primitives-architecture.md` | design-source | - **One implementation for async and real-time** — same associate pattern. | - **MongoDB as source of truth for messages** — unified queue. | - **Polling + findOneAndUpdate for claim** — MVP. Change S |
| `2026-04-02-design-layer-4-integrations.md` | design-source | - Adapter classes live in code (kernel) — "Python code, written once per provider." | - Integration entity in DB. | - Adapter registry in code. | - Web operator skills as markdown (per carrier portal) |
| `2026-04-02-design-layer-5-experience.md` | design-source | - UI code separate from kernel (consumes API). | - React app reading API metadata endpoint for auto-generation. | - WebSocket service as real-time push layer (at this stage, separate service listening |
| `2026-04-02-implementation-plan.md` | design-source | - Modular monolith, one deployable unit — RETAINED in final. | - Repository structure (core/, domains/, api/, cli/, skills/) — later changed to (kernel/, kernel_entities/, seed/, ui/, tests/). | - Aut |
| `2026-04-03-message-actor-architecture-research.md` | design-source | - Outbox + publisher + work queue all in kernel code. | - No kernel/harness boundary yet (pre-Session 5). | - MongoDB collection names: outbox, work_queue — later became message_queue + message_log. |
| `2026-04-07-challenge-developer-experience.md` | design-pressure-test | - No new layer claims. This is a pressure-test transcript. | - Agent flags YAML-vs-Python ambiguity which later resolved (Python classes dynamic from JSON data). |
| `2026-04-07-challenge-distributed-systems.md` | design-pressure-test | - Entity save + message emission: one MongoDB transaction on replica set. | - Outbox pattern (alternative): `_outbox` array on entity document. | - Messages: **two collections** (hot + cold). Hot is i |
| `2026-04-07-challenge-insurance-practitioner.md` | design-pressure-test | - No specific layer claims. The pressure test is about DOMAIN complexity; the architectural response is that: |   - **Kernel stays domain-agnostic** (no hardcoded insurance concepts). |   - **Insuranc |
| `2026-04-07-challenge-mvp-buildability.md` | design-pressure-test | - No specific layer/location claims. This is a buildability review, not architecture. | - Implicit: the proposed architecture is sound at scale but wrong-sized for MVP. |  | **Finding 0 relevance**: T |
| `2026-04-07-challenge-realtime-systems.md` | design-pressure-test | - **Real-time layer = separate concern** that integrates with but doesn't depend on entity system for hot path. | - **Interaction Host**: stateful process per session. Owns conversation state in memor |
| `2026-04-08-actor-references-and-targeting.md` | design-source | - **Targeting resolution** = queue query layer (either UI or API), NOT kernel message-generation. | - **Actor reference fields** = domain entity fields. | - **`target_actor_id` denormalization** = mes |
| `2026-04-08-actor-spectrum-and-primitives.md` | design-source | - **CLI = universal interface** — no distinction between who invokes it (human, LLM agent, deterministic script). | - **Actor location NOT specified** — stays open. This artifact says "the actor is th |
| `2026-04-08-entry-points-and-triggers.md` | design-source | - **Channel infrastructure (voice/chat/SMS)** = separate from actor framework. Per later artifacts, this infrastructure lives in the harness image (the harness hosts the transport + the agent framewor |
| `2026-04-08-kernel-vs-domain.md` | design-source | - **Kernel primitives live in OS kernel code.** Not specified *where* in the file/module sense — just that they're kernel-level. | - **Domain entities live in each system's codebase / configuration**  |
| `2026-04-08-pressure-test-findings.md` | design-source | - **Message split** = kernel-level (two MongoDB collections: message_queue + message_log). NOT in the entity framework layer. Kernel invariant. | - **Changes collection** = kernel-level MongoDB. Same  |
| `2026-04-08-primitives-resolved.md` | design-source | - **Entity framework** = PLATFORM (universal behavior across orgs). Lives in kernel code. Instances + configuration live in MongoDB (per org). | - **Actor framework** = APPLICATIONS (per-org configura |
| `2026-04-08-session-3-checkpoint.md` | session-checkpoint | - **5-layer architecture** at this stage: |   - L1 Entity framework (kernel) |   - L2 API + CLI + Skills (kernel, auto-generated from entities) |   - L3 Associate system (LangChain deep agents with CL |
| `2026-04-09-architecture-ironing-round-2.md` | design-source | - **Kernel capability library** = kernel code, Python modules providing reusable methods. | - **Condition evaluator** = kernel (`kernel/watch/evaluator.py`, shared with rule engine). | - **Message sch |
| `2026-04-09-architecture-ironing-round-3.md` | design-source | - **Emission point** = inside `save_tracked()` in the entity framework (kernel). Not in user code. | - **Watch evaluation** = inside `save_tracked()`, against full change metadata. Kernel. | - **Queue |
| `2026-04-09-architecture-ironing.md` | design-source | - **Temporal workflow** = generic `ProcessMessageWorkflow` (3 activities). Location: left open here (resolved as kernel Temporal Worker by Phase 2-3 spec; per realtime-architecture-design should be ha |
| `2026-04-09-capabilities-model-review-findings.md` | design-review | - **Condition evaluator** = kernel, shared across watches + rules. | - **Rule engine** = `kernel/rule/engine.py`. | - **Lookup resolution** = `kernel/rule/lookup.py`. | - **Evaluation trace** = record |
| `2026-04-09-consolidated-architecture.md` | design-source | - **Entity framework, message system, watch system, role/permissions, capabilities, rules, lookups** — all kernel code. | - **Queue (message_queue/log)** = kernel-managed MongoDB. | - **Queue Processo |
| `2026-04-09-data-architecture-review-findings.md` | design-review | - **OrgScopedCollection** = kernel-level wrapper, hidden in kernel init. | - **PlatformCollection** = kernel-level, platform-admin-only. | - **AWS Secrets Manager** = external service. | - **Skill con |
| `2026-04-09-data-architecture-solutions.md` | design-source | - **OrgScopedCollection** = kernel-level Python class, wraps Motor collection. Hidden in kernel init. | - **PlatformCollection** = kernel-level Python class, only accessible to platform-admin. | - **A |
| `2026-04-09-session-4-checkpoint.md` | session-checkpoint | - All kernel primitives: kernel code. | - Associate execution: Temporal workflows — **location not yet specified in this checkpoint**. Left open until session 5. | - Harness pattern not yet designed.  |
| `2026-04-09-temporal-integration-architecture.md` | design-source | - **Outbox poller = regular Python process** (explicitly noted as "not in Temporal"). Kernel code, lives alongside other kernel runtime processes. | - **Watch evaluation = outbox poller** (in this art |
| `2026-04-09-unified-queue-temporal-execution.md` | design-source | - **Queue = MongoDB `message_queue` collection** — kernel-level infrastructure. | - **Queue history = MongoDB `message_log`** — kernel-level. | - **Watch evaluation = outbox poller (regular Python)**  |
| `2026-04-10-crm-retrace.md` | design-retrace | - **Actor schema**: add `owner_actor_id: Optional[ObjectId]` field. Kernel-level. | - **Credential resolver**: `kernel/integration/resolver.py` — extended to check `owner_actor_id`'s Integrations. Ker |
| `2026-04-10-eventguard-retrace.md` | design-retrace | - **Channel infrastructure (WebSocket server, voice transport)** = lives in harness. Per 2026-04-10-realtime-architecture-design, the transport is bundled with the Runtime deployment. So the WebSocket |
| `2026-04-10-gic-retrace-full-kernel.md` | design-retrace | - **Entity CLI/API**: kernel auto-generated. | - **Integration resolution + adapter dispatch**: kernel (`kernel/integration/*`). | - **Adapter credentials**: AWS Secrets Manager (external), fetched vi |
| `2026-04-10-session-5-checkpoint.md` | session-checkpoint | This is THE session where the Finding 0 resolution is locked: | - **Harness = deployable image OUTSIDE kernel**, one per kind+framework combination. | - **"One harness serves many associates, loading  |
| `2026-04-13-documentation-sweep.md` | design-source | - **Webhook endpoint**: `kernel/api/webhook.py` (per later Phase 2-3 spec). | - **Adapter interface**: `kernel/integration/adapter.py` (abstract base class) — extended with inbound methods. | - **Adap |
| `2026-04-13-infrastructure-and-deployment.md` | design-source | - **API Server (kernel/api/)** = kernel image, public-facing. Railway service `indemn-api`. | - **Queue Processor (kernel/queue_processor.py)** = kernel image, internal. Railway service `indemn-queue- |
| `2026-04-13-remaining-gap-sessions.md` | design-source | - **Repository structure**: |   ``` |   indemn-os/ |     kernel/ |     seed/ |     harnesses/ |       voice-deepagents/ |       chat-deepagents/ |     ui/ |     tests/ |     Dockerfile (multi-entry-po |
| `2026-04-13-session-6-checkpoint.md` | session-checkpoint | - **Kernel architecture** = COMPLETE (sessions 3-6, 50+ artifacts). No new primitives. | - **Infrastructure gap sessions** (Infrastructure & Deployment, Development Workflow, Operations, etc.) — at WH |
| `2026-04-14-impl-spec-gaps.md` | spec-gap-tracking | Gap resolutions that touch architectural layer: |  | - **G-21 `process_with_associate` activity implementation**: specified to run as kernel Temporal activity in `kernel/temporal/activities.py`. Calls |
| `2026-04-14-impl-spec-phase-0-1-addendum.md` | spec-superseded | - `kernel_entities/attention.py` — Attention Document class | - `kernel_entities/runtime.py` — Runtime Document class | - `kernel_entities/session.py` — Session Document class | - `kernel/entity/migra |
| `2026-04-14-impl-spec-phase-0-1.md` | spec-superseded | Same as consolidated — see notes for `2026-04-14-impl-spec-phase-0-1-consolidated.md`. This base spec is the precursor. |  | **Finding 0 relevance**: Phase 0-1 has no Finding 0 issue. `kernel/temporal |
| `2026-04-14-impl-spec-phase-2-3.md` | spec-superseded | - **`kernel/temporal/client.py`** — Temporal client factory. | - **`kernel/temporal/workflows.py`** — ProcessMessageWorkflow, HumanReviewWorkflow, BulkExecuteWorkflow. | - **`kernel/temporal/activitie |
| `2026-04-14-impl-spec-phase-4-5.md` | spec-superseded | - **`ui/src/`** — React app. | - **`kernel/api/assistant.py`** — kernel endpoint. (Finding 0b code site.) | - **`kernel/api/websocket.py`** — UI real-time. | - **`kernel/api/events.py`** — scoped even |
| `2026-04-14-impl-spec-phase-6-7.md` | spec-superseded | - **Phase 6 Indemn CRM**: domain entities created via CLI in indemn org. All data, no kernel code changes. | - **Phase 7 GIC**: domain entities created via CLI in gic org. All data. | - **Integration  |
| `2026-04-14-impl-spec-verification-report.md` | spec-verification | - **EntityDefinition**: MongoDB, per-org scoped with index `(org_id, name)`. | - **Schema migration** (section 1.29): `kernel/entity/migration.py`. CLI commands + batching + dry-run. | - **CLI auto-re |
| `2026-04-15-shakeout-session-findings.md` | runtime-findings | - **Findings 1-12, 17 (fixed)**: all patches in kernel code (API, CLI, UI). Kernel-layer implementation. | - **Finding 18 (assistant has no tools)**: refers to `kernel/api/assistant.py` — **confirms F |
| `2026-04-15-spec-vs-implementation-audit.md` | earlier-audit | - **All deviations are at the mechanism/code-correctness level**, NOT architectural layer level. | - This audit CONFIRMED Finding 0b (D-03) as a runtime-observable problem but described it as "add too |
| `architecture.md` | stakeholder-context | - **Ryan's layered architecture** — conceptual, not code-level: |   - L1 Runtime infra (LLM/Voice/Channels/VectorDB) → kernel + external services |   - L2 Integration (Carrier APIs, AMS, Web operators |
| `business.md` | stakeholder-context | - No specific layer/location claims. Business/strategy context. | - Implicit: the OS is the NEW platform Craig is building. Current codebases continue serving current customers. |  | **Finding 0 relev |
| `craigs-vision.md` | stakeholder-context | - **Platform** = the user interface backed by the domain model (entities + workflows + UI). | - **Associates** = processing nodes (AI capabilities). Operate on domain objects through the platform (i.e |
| `product.md` | stakeholder-context | - No specific layer/location claims. Product strategy. | - Implicit: the OS kernel's entity framework + capability library + skill model must support the 7 canonical domain objects and 6 reused capabi |
| `strategy.md` | stakeholder-context | - No specific layer/location claims. Strategic + political context. |  | **Finding 0 relevance**: The Series A urgency + "make it impossible to say no" pressure pushes toward shipping quickly. Finding |
| `2026-03-25-the-vision-v1.md` | stakeholder-context | No specific code locations. Vision statement. |  | - **9 sub-domains** listed (later: 70 entities across the sub-domains per domain-model-research). | - **Implicit**: platform and domain layer separat |
| `2026-03-25-the-vision.md` | stakeholder-context | - **9 sub-domains** (domain layer): |   - Core Insurance, Risk & Parties, Submission & Quoting, Policy Lifecycle, Claims, Financial, Authority & Compliance, Distribution & Delivery, Platform Layer | - |


## Cross-Reference Graph

Which artifacts reference which other artifacts.


### `2026-04-13-white-paper.md` references:
- 2026-04-10-realtime-architecture-design.md — source for Runtime/Attention/harness pattern detail (referenced implicitly by § "Attention, Runtime, and Real-Time")
- 2026-04-11-authentication-design.md — source for § 4 Authentication
- 2026-04-11-base-ui-operational-surface.md — source for § 5 Base UI
- 2026-04-10-bulk-operations-pattern.md — source for § 6 Bulk Operations
- 2026-04-10-integration-as-primitive.md — source for Integration primitive treatment
- 2026-04-09-data-architecture-everything-is-data.md — source for § "Everything Is Data"
- 2026-04-09-entity-capabilities-and-skill-model.md — source for Skills + Capabilities + --auto pattern
- 2026-03-30-design-layer-3-associate-system.md — source for Actor/associate system
- 2026-04-13-simplification-pass.md — referenced implicitly (white paper post-simplification state)

### `2026-04-10-realtime-architecture-design.md` references:
- 2026-04-10-eventguard-retrace.md — surfaced mid-conversation event delivery gap
- 2026-04-10-crm-retrace.md — surfaced actor-context scoping need
- 2026-04-10-post-trace-synthesis.md — categorized the open design items
- 2026-04-10-base-ui-and-auth-design.md — proposed ephemeral entity locks, unified into Attention here
- 2026-04-10-integration-as-primitive.md — Integration owners, adapter pattern, reused for voice clients
- 2026-04-10-bulk-operations-pattern.md — referenced as a Part 10 open item

### `2026-04-10-integration-as-primitive.md` references:
- 2026-04-02-design-layer-4-integrations.md (original Integration + adapter pattern)
- 2026-04-08-actor-spectrum-and-primitives.md (entity polymorphism for integrations)
- 2026-04-08-primitives-resolved.md (Layer 4 collapses into Layer 1)
- 2026-04-09-data-architecture-solutions.md (Integration entity stores secret_ref)
- 2026-04-09-capabilities-model-review-findings.md (adapter versioning for external API changes)
- 2026-04-10-realtime-architecture-design.md (Integration primitive reused for voice_client provider — humans taking over voice calls)

### `2026-03-30-design-layer-3-associate-system.md` references:
- 2026-04-10-realtime-architecture-design.md — FORMALIZES what this artifact introduces: the harness pattern, Runtime entity, one image per kind+framework combo, ~60-line harness script
- 2026-04-09-entity-capabilities-and-skill-model.md — the skill model (entity skills auto-generated, workflow skills human-authored)
- 2026-04-09-data-architecture-everything-is-data.md — the entity framework
- Hive blueprint system (referenced as possible workflow runner)
- Jarvis, Intake Manager (existing Indemn agents using deepagents)

### `2026-04-09-entity-capabilities-and-skill-model.md` references:
- 2026-04-08-primitives-resolved.md
- 2026-04-08-actor-references-and-targeting.md
- 2026-03-30-design-layer-3-associate-system.md — the associate system that reads skills and executes CLI
- 2026-04-10-realtime-architecture-design.md — resolves WHERE the LLM-based skill interpreter runs (in harness)

### `2026-04-11-authentication-design.md` references:
- 2026-04-10-base-ui-and-auth-design.md — supersedes the auth portion
- 2026-04-10-integration-as-primitive.md — Integration primitive used for identity providers
- 2026-04-10-session-5-checkpoint.md — auth skeleton from session 5
- 2026-04-09-data-architecture-solutions.md — session 4 security decisions
- 2026-04-11-base-ui-operational-surface.md — base UI design depends on default assistant's auth model

### `2026-04-10-bulk-operations-pattern.md` references:
- 2026-04-10-gic-retrace-full-kernel.md (coalescing surfaced)
- 2026-04-10-eventguard-retrace.md (351 venue deployments forced the issue)
- 2026-04-10-crm-retrace.md (overdue sweep + health monitoring)
- 2026-04-10-post-trace-synthesis.md (identified as item 7)
- 2026-04-10-realtime-architecture-design.md (watch coalescing mechanism this builds on)

### `2026-04-11-base-ui-operational-surface.md` references:
- 2026-04-10-bulk-operations-pattern.md (bulk ops surface in UI via assistant + auto-generated CLI)
- 2026-04-10-base-ui-and-auth-design.md (initial sketch — this artifact supersedes the UI portion)
- 2026-04-10-gic-retrace-full-kernel.md (surfaced pipeline dashboard + queue health)
- 2026-04-10-realtime-architecture-design.md (provides Attention, scoped watches, Change Streams, harness pattern)
- 2026-04-10-post-trace-synthesis.md (items 8 and 9)
- 2026-04-11-authentication-design.md (auth portion — handles default assistant's user session inheritance)

### `2026-04-09-data-architecture-everything-is-data.md` references:
- 2026-04-09-architecture-ironing-round-3.md — precursor design iteration
- 2026-04-09-data-architecture-solutions.md — supplementary Session 4 data-architecture decisions (referenced from auth design for tamper-evident changes collection, OrgScopedCollection, AWS Secrets Manager)
- 2026-04-09-entity-capabilities-and-skill-model.md — kernel capabilities referenced here
- 2026-03-30-design-layer-3-associate-system.md — associate entity stored as data

### `2026-04-13-simplification-pass.md` references:
- All prior session 5-6 artifacts (referenced as "the complete architecture being reviewed")
- 2026-04-10-realtime-architecture-design.md (scoped watches, coalescing mechanism removed here, harness pattern retained)
- 2026-04-11-authentication-design.md (WebAuthn and requires_fresh_mfa deferred here)
- 2026-04-11-base-ui-operational-surface.md (UI coalescing = where coalescing now lives)
- 2026-04-10-integration-as-primitive.md (content visibility scoping on Integration kept)

### `2026-04-10-base-ui-and-auth-design.md` references:
- 2026-04-10-gic-retrace-full-kernel.md (surfaced the six concerns this addresses)
- 2026-04-10-integration-as-primitive.md (Integration primitive enables SSO)
- 2026-03-30-design-layer-1-entity-framework.md (original thin auth sketch)
- 2026-04-10-realtime-architecture-design.md (SUPERSEDES the ephemeral entity lock proposal here, unifies with Attention)
- 2026-04-11-authentication-design.md (SUPERSEDES the auth portion of this artifact)
- 2026-04-11-base-ui-operational-surface.md (SUPERSEDES the base UI portion of this artifact)
- 2026-04-13-simplification-pass.md (REMOVES watch coalescing from the kernel)

### `2026-04-10-post-trace-synthesis.md` references:
- 2026-04-10-gic-retrace-full-kernel.md
- 2026-04-10-eventguard-retrace.md
- 2026-04-10-crm-retrace.md (recommended third trace — later executed)
- 2026-04-10-integration-as-primitive.md
- 2026-04-10-base-ui-and-auth-design.md
- All the items listed point forward to later design artifacts

### `2026-04-14-impl-spec-phase-0-1-consolidated.md` references:
- 2026-04-13-white-paper.md (design-level source of truth)
- 2026-04-14-impl-spec-gaps.md (90 gaps identified)
- 2026-04-14-impl-spec-phase-0-1.md (superseded by this)
- 2026-04-14-impl-spec-phase-0-1-addendum.md (superseded by this)

### `2026-04-14-impl-spec-phase-2-3-consolidated.md` references:
- 2026-04-13-white-paper.md
- 2026-04-14-impl-spec-gaps.md
- 2026-04-14-impl-spec-phase-0-1-consolidated.md
- 2026-04-09-temporal-integration-architecture.md
- 2026-04-09-unified-queue-temporal-execution.md
- 2026-04-10-integration-as-primitive.md
- 2026-04-10-bulk-operations-pattern.md
- 2026-04-13-documentation-sweep.md

### `2026-04-14-impl-spec-phase-4-5-consolidated.md` references:
- 2026-04-13-white-paper.md
- 2026-04-14-impl-spec-gaps.md
- 2026-04-11-base-ui-operational-surface.md (rendering contract, assistant design)
- 2026-04-11-authentication-design.md (full auth)
- 2026-04-10-realtime-architecture-design.md (Attention, Runtime, harness pattern, scoped watches, handoff)
- 2026-04-13-documentation-sweep.md (owner_actor_id, content visibility, webhook dispatch)

### `2026-04-14-impl-spec-phase-6-7-consolidated.md` references:
- 2026-04-13-white-paper.md
- 2026-04-14-impl-spec-gaps.md
- 2026-04-10-crm-retrace.md (CRM modeled on the kernel)
- 2026-04-10-gic-retrace-full-kernel.md (GIC modeled on the kernel)
- 2026-04-13-remaining-gap-sessions.md (domain modeling process, operations, transition)

### `activities.py` references:
- Phase 2-3 consolidated spec: this file implements §2.4 Activities (lines 315-759 of the spec).
- `kernel/api/assistant.py`: a parallel, simpler agent execution (stripped-down, no tools) in the API server. Finding 2.
- `kernel/temporal/workflows.py`: defines ProcessMessageWorkflow that calls these activities.
- `kernel/temporal/worker.py`: registers these activities.
- `kernel/skill/schema.py`, `kernel/skill/integrity.py`: skill loading + hash verification.
- Design artifact 2026-04-10-realtime-architecture-design.md Part 4: "The harness uses the CLI, not a separate Python SDK" — explicit counter-claim to what this file does.

### `assistant.py` references:
- `kernel/api/app.py` — FastAPI app factory that mounts `assistant_router`
- `kernel/temporal/activities.py::_execute_reasoning` — the tool-use pattern that should be adapted for the assistant but isn't
- Design: 2026-04-11-base-ui-operational-surface.md §4.7 — assistant design
- Design: 2026-04-11-authentication-design.md §"Default Assistant Authentication" — auth model
- Design: 2026-04-10-realtime-architecture-design.md Part 4 — harness pattern
- Comprehensive audit Finding 2: assistant has no tools
- Comprehensive audit Finding 0: agent execution in wrong architectural layer (this file's layer issue is a consequence of the broader harness pattern gap)

### `workflows.py` references:
- Phase 2-3 consolidated spec §2.2 (ProcessMessageWorkflow), §2.3 (HumanReviewWorkflow), §2.10 (BulkExecuteWorkflow)
- `kernel/temporal/activities.py` — activity implementations
- Design: 2026-04-10-realtime-architecture-design.md Part 4 — should be in harness, not kernel
- Design: 2026-04-10-bulk-operations-pattern.md — BulkExecuteWorkflow in kernel is correct

### `worker.py` references:
- Phase 2-3 spec §2.1 (Temporal Connection and Worker Setup)
- `kernel/temporal/activities.py` — the activities this worker runs
- `kernel/temporal/workflows.py` — the workflows this worker runs
- `kernel/temporal/client.py` — client factory
- Dockerfile + docker-compose.yml — deployment configuration

### `adapter.py` references:
- Design: 2026-04-10-integration-as-primitive.md (THE source design for this file)
- Phase 3 spec §3.1 (adapter base class)
- `kernel/integration/registry.py` — registers adapter classes
- `kernel/integration/adapters/outlook.py`, `stripe_adapter.py` — concrete implementations
- `kernel/integration/dispatch.py` — dispatches to adapter methods
- `kernel/integration/resolver.py` — resolves which Integration to use

### `registry.py` references:
- Design: 2026-04-10-integration-as-primitive.md (adapter versioning + registry)
- Phase 3 spec §3.2 (adapter registry)
- `kernel/integration/adapter.py` — base class
- `kernel/integration/adapters/*.py` — call `register_adapter(...)` at module import
- `kernel/integration/dispatch.py` — uses `get_adapter_class(...)` to dispatch calls

### `dispatch.py` references:
- Design: 2026-04-10-integration-as-primitive.md (credential resolution, rotation)
- Phase 3 spec §3.5 (Adapter Dispatch with Auto-Refresh)
- `kernel/integration/adapter.py` — base class + error hierarchy
- `kernel/integration/registry.py` — adapter class lookup
- `kernel/integration/resolver.py` — integration resolution
- `kernel/integration/credentials.py` — credential fetch/store

### `resolver.py` references:
- Design: 2026-04-10-integration-as-primitive.md §"Credential Resolution" (priority chain)
- Phase 3 spec §3.3 (Credential Resolution)
- 2026-04-13-documentation-sweep.md — `owner_actor_id` documentation
- `kernel_entities/integration.py` — Integration entity schema
- `kernel_entities/actor.py` — Actor's `owner_actor_id` field

### `websocket.py` references:
- Design: 2026-04-11-base-ui-operational-surface.md §"Real-Time Update Filtering"
- Phase 4-5 spec §4.6 (Real-Time Updates via WebSocket)
- White paper § Production Requirements (WebSocket keepalive)
- `kernel/auth/jwt.py` — token verification

### `events.py` references:
- Design: 2026-04-10-realtime-architecture-design.md Part 8 (`indemn events stream` as the one new CLI primitive)
- Phase 4-5 spec §5.4 (events stream endpoint + CLI)
- Harness pattern usage: `subprocess.Popen(["indemn", "events", "stream", "--actor", associate_id, ...], stdout=PIPE)`

### `interaction.py` references:
- Design: 2026-04-10-realtime-architecture-design.md Part 6 (Handoff)
- Design: Part 7 (Voice Clients as Integrations)
- Phase 4-5 spec §5.6 (Handoff)
- `kernel_entities/attention.py` — Attention entity with purpose=observing
- `kernel_entities/runtime.py` — Runtime entity (not directly referenced, but handoff implies Runtime watches for changes)

### `generator.py` references:
- Design: 2026-04-09-entity-capabilities-and-skill-model.md (auto-generated entity skills)
- Phase 1 spec §1.19 Skill Entity
- `kernel/skill/schema.py` — Skill entity schema
- `kernel/entity/definition.py` — EntityDefinition shape

### `schema.py` references:
- Design: 2026-04-09-entity-capabilities-and-skill-model.md (skills are markdown, entity + associate types)
- Design: 2026-04-13-white-paper.md § Security (content hashing + tamper-evident)
- Phase 1 spec §1.19 Skill Entity
- `kernel/skill/integrity.py` — hash verification
- `kernel/skill/generator.py` — entity skill auto-generation

### `session_manager.py` references:
- Design: 2026-04-11-authentication-design.md §"Session Management"
- Phase 1 spec §1.22 Authentication
- Phase 4-5 spec §4.9 Authentication Completion
- `kernel_entities/session.py` — Session schema (bootstrap entity)
- `kernel/auth/jwt.py` — JWT signing/verification

### `jwt.py` references:
- Design: 2026-04-11-authentication-design.md §"Session Management: Hybrid JWT + Session Entity"
- Phase 1 spec §1.22 Authentication
- Phase 4-5 spec §4.9 Revocation Cache with Bootstrap
- `kernel_entities/session.py` — Session entity with access_token_jti field

### `auth_routes.py` references:
- Design: 2026-04-11-authentication-design.md (full auth design)
- Phase 1 spec §1.22 Authentication (basic password + token)
- Phase 4-5 spec §4.9 Authentication Completion (SSO, MFA, platform admin, recovery, refresh)
- Comprehensive audit: "Authentication — COMPLETE" (all items implemented)

### `registration.py` references:
- Design: 2026-04-13-white-paper.md § Entity (self-evidence property)
- Phase 1 spec §1.21 Auto-Generated API
- `kernel/api/serialize.py` — to_dict helper
- `kernel/entity/exposed.py` — @exposed decorator
- `kernel/capability/registry.py` — capability lookup
- `kernel/integration/dispatch.py` — adapter dispatch

### `bulk.py` references:
- Design: 2026-04-10-bulk-operations-pattern.md
- Phase 2-3 spec §2.10 Bulk Operations
- `kernel/temporal/workflows.py::BulkExecuteWorkflow`
- `kernel/temporal/activities.py::process_bulk_batch`
- `kernel/cli/bulk_commands.py`, `bulk_monitor.py`

### `AssistantProvider.tsx` references:
- Design: 2026-04-11-base-ui-operational-surface.md §4.7 The Assistant
- Phase 4-5 spec §4.7 Assistant Hook
- Kernel endpoint: `kernel/api/assistant.py::assistant_message`

### `useAssistant.ts` references:
- Design: 2026-04-11-base-ui-operational-surface.md §4.7 (assistant UI pattern)
- Phase 4-5 spec §4.7 Assistant Hook (named `useAssistant`)

### `org_lifecycle.py` references:
- Design: 2026-04-09-data-architecture-everything-is-data.md §"Environments = Orgs"
- Phase 6-7 spec §7.4 Org Export/Import Format
- Comprehensive audit §"Org Lifecycle — COMPLETE" confirms implementation

### `cache.py` references:
- Design: 2026-04-10-realtime-architecture-design.md (watch mechanism)
- 2026-04-13-simplification-pass.md (coalescing moved out — this file does NOT have coalescing, correct)
- Phase 1 spec §1.14 Watch Cache
- `kernel/watch/evaluator.py` — condition evaluation
- `kernel/message/emit.py` — uses cached watches

### `evaluator.py` references:
- Design: 2026-04-13-white-paper.md § Watches (single condition language)
- Phase 1 spec §1.15 Condition Evaluator
- 2026-04-10-realtime-architecture-design.md (watches + scoping)

### `Dockerfile` references:
- Phase 0-1 spec §0.3 Dockerfile
- Phase 0-1 spec §0.9 Deployment (Railway services)
- White paper § Service Architecture
- Design: 2026-04-10-realtime-architecture-design.md Part 4 (three harness images specified)

### `docker-compose.yml` references:
- Phase 0-1 spec §0.4 docker-compose.yml (expected configuration)
- `Dockerfile` — image definition
- `kernel/api/app.py` — API entry point
- `kernel/queue_processor.py` — queue processor entry point
- `kernel/temporal/worker.py` — Temporal worker entry point (NOT in compose)

### `2026-03-24-associate-domain-mapping.md` references:
- `context/craigs-vision.md` — source for "the underlying system" thesis
- Will be referenced by later domain-model-research and domain-model-v2 artifacts
- Informs entity-framework design (Layer 1) and associate-system design (Layer 3)

### `2026-03-24-source-index.md` references:
- All subsequent design artifacts in this project draw from these sources.
- Ryan's taxonomy (Outcomes > Journeys > Workflows > Capabilities) appears to have informed the six-primitives resolution later.
- Four Outcomes Matrix drives the 48 associates catalog (2026-03-24-associate-domain-mapping.md).

### `2026-03-25-associate-architecture.md` references:
- Succeeded by: 2026-03-30-design-layer-3-associate-system.md (more concrete architecture)
- 2026-04-10-realtime-architecture-design.md (harness pattern formalizes this)
- context/craigs-vision.md (thesis foundation)

### `2026-03-25-domain-model-research.md` references:
- Successor: 2026-03-25-domain-model-v2.md (refined model)
- 2026-03-24-associate-domain-mapping.md (same frequency analysis)
- Later: 2026-04-08-primitives-resolved.md (distills to 6 primitives)
- Later: 2026-04-09-data-architecture-everything-is-data.md (makes domain = data)

### `2026-03-25-domain-model-v2.md` references:
- Successor: 2026-03-30-entity-system-and-generator.md (how to generate this)
- 2026-04-08-primitives-resolved.md (final 6 primitives)
- 2026-04-09-data-architecture-everything-is-data.md (this becomes data, not code)
- Draft status per file — pending validation with Ryan (domain) and Dhruv (technical).

### `2026-03-25-platform-tiers-and-operations.md` references:
- Succeeded by: 2026-04-11-authentication-design.md (§ Tier 3 Self-Service Signup implements this)
- context/craigs-vision.md (vision thesis)
- context/business.md (business model)

### `2026-03-25-session-notes.md` references:
- All subsequent artifacts build on this session.

### `2026-03-25-the-operating-system-for-insurance.md` references:
- context/craigs-vision.md (thesis foundation)
- 2026-03-24-associate-domain-mapping.md (48 associates)
- Cam's Four Outcomes Product Matrix
- EventGuard, GIC, INSURICA, Union General (R&D for OS)
- Later: all subsequent design artifacts + the white paper

### `2026-03-25-why-insurance-why-now.md` references:
- Competitive landscape (Vertafore, Applied Systems, Duck Creek, Guidewire)
- Kyle's constraint-removal thesis
- EventGuard (proof of concept)

### `2026-03-30-design-layer-1-entity-framework.md` references:
- 2026-03-25-domain-model-v2.md (DDD classification)
- Superseded by:
  - 2026-04-09-data-architecture-everything-is-data.md (entities as data, not Python classes)
  - 2026-04-08-primitives-resolved.md (six primitives + kernel entities abstraction)
  - 2026-04-13-white-paper.md (final state)
- 2026-04-09-temporal-integration-architecture.md later replaces RabbitMQ event bus with MongoDB + Temporal pattern.

### `2026-03-30-entity-system-and-generator.md` references:
- 2026-03-25-domain-model-v2.md (entities to generate)
- Superseded technology choice: 2026-03-30-design-layer-1-entity-framework.md (Postgres → later MongoDB)
- 2026-04-09-data-architecture-everything-is-data.md (definitions become data)

### `2026-03-30-vision-session-2-checkpoint.md` references:
- All 7 session-2 artifacts (already read in manifest or being read).
- vision/2026-03-25-the-vision.md + vision-v1.md.
- context/ stakeholder docs.

### `2026-04-02-core-primitives-architecture.md` references:
- Supersedes: 2026-03-30-design-layer-1-entity-framework.md (mixin-based approach)
- Informed by: adversarial review findings (2026-04-07 challenges — 5 reviewers)
- Foreshadows:
  - 2026-04-08-primitives-resolved.md (6 primitives final)
  - 2026-04-09-data-architecture-everything-is-data.md
  - 2026-04-10-realtime-architecture-design.md (harness pattern — BUT this artifact claims "real-time uses same associate pattern as async" which was later refined to "harness pattern per kind+framework")
  - White paper message architecture

### `2026-04-02-design-layer-4-integrations.md` references:
- 2026-04-10-integration-as-primitive.md (elevates Integration to primitive #6; this artifact's patterns RETAINED).
- 2026-03-30-design-layer-3-associate-system.md (web operators share associate harness).
- Later: Phase 3 consolidated spec implements this exactly.

### `2026-04-02-design-layer-5-experience.md` references:
- Ryan's wireframes (retail agency, GIC wholesaler).
- Later: 2026-04-11-base-ui-operational-surface.md (SUPERSEDES the UI portion, drops ViewConfig as separate entity).
- 2026-04-10-realtime-architecture-design.md (real-time mechanism refined with harness pattern + Change Streams).

### `2026-04-02-implementation-plan.md` references:
- Supersedes/foreshadows:
  - 2026-04-02-core-primitives-architecture.md (same day, contradicts mixin approach)
  - Phase structure later resolved in 2026-04-13-white-paper.md § 11 (build sequence) — 8 phases
  - 2026-04-14 consolidated specs — implement the 8-phase structure

### `2026-04-03-message-actor-architecture-research.md` references:
- 2026-04-02-core-primitives-architecture.md (contemporaneous, integrates these findings)
- Later artifacts replace RabbitMQ with MongoDB-only messaging.
- Orleans virtual actor pattern → later harness pattern (one harness image serves many associates, spins up on demand).

### `2026-04-07-challenge-developer-experience.md` references:
- 2026-04-02-core-primitives-architecture.md (evaluated by this test)
- 2026-04-02-design-layer-4-integrations.md
- 2026-03-30-design-layer-1-entity-framework.md (YAML vs Python ambiguity)
- Informs: 2026-04-08-pressure-test-findings.md (consolidates all 5 challenges)

### `2026-04-07-challenge-distributed-systems.md` references:
- Feeds into: core-primitives-architecture (10 hardening requirements), primitives-resolved, pressure-test-findings synthesis, consolidated-architecture, all subsequent design artifacts

### `2026-04-07-challenge-insurance-practitioner.md` references:
- Project vision: domain-model-research, domain-model-v2, associate-architecture (early framing)
- Feeds into: pressure-test-findings (synthesis), white paper (kernel-vs-domain split)
- Later directly tested: GIC retrace (B2B), EventGuard retrace (consumer), CRM retrace (generic)

### `2026-04-07-challenge-mvp-buildability.md` references:
- Other pressure tests (realtime, distributed, insurance-practitioner, developer-experience)
- Feeds into: pressure-test-findings (synthesis), implementation-plan revisions, white paper

### `2026-04-07-challenge-realtime-systems.md` references:
- Project vision documents (pre-April 7)
- Feeds into: 2026-04-08-primitives-resolved.md, 2026-04-08-pressure-test-findings.md (synthesis), 2026-04-10-realtime-architecture-design.md (harness pattern), core-primitives-architecture (hardening requirements)

### `2026-04-08-actor-references-and-targeting.md` references:
- 2026-04-08-primitives-resolved.md (same day)
- 2026-04-08-kernel-vs-domain.md (assignment was a primitive there; this artifact rejects that; later artifacts reconcile)
- 2026-04-10-realtime-architecture-design.md (scoped watches use `field_path` + `active_context`, which IS the "target-from-field" idea — but now at watch-evaluation time, with explicit scope resolution)

### `2026-04-08-actor-spectrum-and-primitives.md` references:
- Feeds into: kernel-vs-domain (same-day), primitives-resolved (same-day), pressure-test-findings, integration-as-primitive (reverses integration collapse)

### `2026-04-08-entry-points-and-triggers.md` references:
- 2026-04-08-primitives-resolved.md (confirms 3 trigger types)
- 2026-04-08-kernel-vs-domain.md (establishes kernel primitives)
- 2026-04-10-integration-as-primitive.md (formalizes Integration including webhook dispatch)
- 2026-04-10-realtime-architecture-design.md (confirms channel = harness transport)
- 2026-04-13-documentation-sweep.md item 4 (inbound webhook dispatch)

### `2026-04-08-kernel-vs-domain.md` references:
- 2026-04-08-primitives-resolved.md (same session, earlier note)
- 2026-04-08-actor-spectrum-and-primitives.md (precursor)
- White paper (later) — the 6 primitives survive with one refinement: Integration is reinstated as primitive #6 (2026-04-10).
- authentication-design.md (later) — adds Session as 7th kernel entity.

### `2026-04-08-pressure-test-findings.md` references:
- 2026-04-08-actor-spectrum-and-primitives.md (origin)
- 2026-04-08-primitives-resolved.md (resolution of primitives)
- 2026-04-08-kernel-vs-domain.md (same day, adds Organization + Assignment)
- 2026-04-08-entry-points-and-triggers.md (Tier A — to be read)
- 2026-04-10-bulk-operations-pattern.md (resolved Finding 10)
- 2026-04-10-realtime-architecture-design.md (resolved Finding 1 — direct invocation via harness)
- 2026-04-11-authentication-design.md (advanced assignment thinking)
- 2026-04-13-simplification-pass.md (DROPPED message coalescing from Finding 10)

### `2026-04-08-primitives-resolved.md` references:
- 2026-04-08-actor-spectrum-and-primitives.md (precursor — actor spectrum insight)
- 2026-04-08-kernel-vs-domain.md (next — adds Organization and Assignment primitives, lifts primitive count to 6 kernel, keeps Integration collapsed for now)
- 2026-04-10-integration-as-primitive.md (supersedes the "integration collapse" claim — Integration is primitive #6)
- 2026-04-09-temporal-integration-architecture.md (adds Temporal as execution engine for associates)
- 2026-04-10-realtime-architecture-design.md (places agent execution in harness images outside kernel)

### `2026-04-08-session-3-checkpoint.md` references:
- `2026-04-02-core-primitives-architecture.md` — source of truth for architecture decisions at that time
- Session 1-2 artifacts (vision, research, domain model)
- `2026-04-07` adversarial review artifacts (challenge-* files)
- Session 4 checkpoint (resolves wiring question)
- Session 5 checkpoint (adds Integration primitive, Attention, Runtime, harness pattern)

### `2026-04-09-architecture-ironing-round-2.md` references:
- 2026-04-09-architecture-ironing.md (round 1)
- 2026-04-09-architecture-ironing-round-3.md (round 3 — event granularity + @exposed emission boundary)
- 2026-04-09-entity-capabilities-and-skill-model.md (capability model details)
- Phase 0-1 consolidated spec (implements these unifications)

### `2026-04-09-architecture-ironing-round-3.md` references:
- 2026-04-09-architecture-ironing.md (Round 1) — introduced outbox elimination, skill vs workflow, entity creation via CLI
- 2026-04-09-architecture-ironing-round-2.md — unified capabilities + entity methods, watch+rule condition language
- 2026-04-13-simplification-pass.md — later moved watch coalescing OUT of kernel (here it's still mentioned via message `batch_id`)
- Phase 2-3 consolidated spec — implements Queue Processor, save_tracked, message_queue, watch evaluation
- Phase 0-1 consolidated spec — changes collection, entity framework

### `2026-04-09-architecture-ironing.md` references:
- 2026-04-09-architecture-ironing-round-2.md (next round, 5 more issues)
- 2026-04-09-architecture-ironing-round-3.md (round 3, event granularity + @exposed)
- 2026-04-09-consolidated-architecture.md (integrates all 3 rounds)
- 2026-04-09-unified-queue-temporal-execution.md (same-day: associates as employees + one queue)
- 2026-04-09-data-architecture-everything-is-data.md (evolves "CLI generates Python class file" into "definitions live in MongoDB")

### `2026-04-09-capabilities-model-review-findings.md` references:
- 2026-04-09-entity-capabilities-and-skill-model.md (the design this reviews)
- 2026-04-09-data-architecture-review-findings.md (sister review — data architecture)
- 2026-04-10-gic-retrace-full-kernel.md (formal retrace uses these findings)
- Phase 0-1 consolidated spec (implements rules + lookups + veto + groups)
- Phase 2-3 consolidated spec (implements evaluate_rules + auto_classify)

### `2026-04-09-consolidated-architecture.md` references:
- 2026-04-08 primitives-resolved + kernel-vs-domain + pressure-test-findings + entry-points-and-triggers (precursors)
- 2026-04-09 data-architecture-everything-is-data + data-architecture-solutions + temporal-integration-architecture + unified-queue-temporal-execution + entity-capabilities-and-skill-model (same-session siblings)
- 2026-04-09 architecture-ironing (Rounds 1, 2, 3) — encoded decisions
- 2026-04-10-integration-as-primitive.md — SUPERSEDES the "Integration collapsed into Entity" position
- 2026-04-10-realtime-architecture-design.md — formalizes harness pattern (location locked as "outside kernel")
- 2026-04-13-white-paper.md — final consolidation
- 2026-04-13-simplification-pass.md — applies additional simplifications
- Phase 0-1 + 2-3 consolidated specs — implementation of this architecture (with Finding 0 deviation at Phase 2-3)

### `2026-04-09-data-architecture-review-findings.md` references:
- 2026-04-09-data-architecture-everything-is-data.md (the design this reviews)
- 2026-04-09-data-architecture-solutions.md (resolves all 14 findings)
- Phase 0-1 consolidated spec (implements most fixes)
- 2026-04-15-shakeout-session-findings.md (Finding 4 — dual base class emerged from #9)
- 2026-04-15-spec-vs-implementation-audit.md (D-01 dual base class)

### `2026-04-09-data-architecture-solutions.md` references:
- 2026-04-09-data-architecture-review-findings.md (the 14 findings this artifact resolves — Tier B)
- 2026-04-09-data-architecture-everything-is-data.md (same day, complementary — "everything is data")
- Phase 0-1 consolidated spec (implements OrgScopedCollection + changes collection + seed files)
- Phase 2-3 consolidated spec (Temporal Worker config)
- white-paper (integrates all these as the implemented architecture)

### `2026-04-09-session-4-checkpoint.md` references:
- Session 3 checkpoint (precursor)
- All session 4 artifacts (10+ new, listed)
- Session 5 checkpoint (adds Integration primitive, Attention, Runtime, harness pattern)
- Session 6 checkpoint (gap sessions, simplification pass, white paper)

### `2026-04-09-temporal-integration-architecture.md` references:
- 2026-04-09-unified-queue-temporal-execution.md (IMMEDIATELY SUPERSEDES this artifact on queue mechanism: queue is ALWAYS MongoDB; Temporal is execution engine, not queue backend)
- 2026-04-10-realtime-architecture-design.md (IMMEDIATELY SUPERSEDES this on worker location: async Temporal worker = harness image, not kernel module)
- Phase 2-3 consolidated spec §2.4 — implemented something between these three (Temporal in kernel, single `indemn-kernel` task queue, no harness) → Finding 0

### `2026-04-09-unified-queue-temporal-execution.md` references:
- 2026-04-09-temporal-integration-architecture.md (previous — this artifact supersedes "queue = Temporal task queue" with "queue = MongoDB + Temporal is execution only")
- 2026-04-10-realtime-architecture-design.md (one day later — places Temporal workers in harness images outside kernel)
- Phase 2-3 consolidated spec §2.4 (implements the activity pattern; choice of worker location = kernel → Finding 0)
- Phase 2-3 spec's `save_tracked` + optimistic dispatch = implementation of the closing-note "Optimization"

### `2026-04-10-crm-retrace.md` references:
- 2026-04-10-gic-retrace-full-kernel.md (first retrace)
- 2026-04-10-eventguard-retrace.md (second retrace — surfaced inbound webhook + actor-context watches + bulk ops)
- 2026-04-10-post-trace-synthesis.md (routing document for findings)
- 2026-04-10-integration-as-primitive.md (Integration primitive + owner model — extended here via owner_actor_id)
- 2026-04-10-realtime-architecture-design.md (adds Runtime; Associate gains `owner_actor_id`)
- 2026-04-11-authentication-design.md (formalizes default-assistant + owner-bound-service-token patterns)
- 2026-04-13-documentation-sweep.md (formalizes items 11 + 12 from this retrace)
- Phase 6-7 consolidated spec (implements this)

### `2026-04-10-eventguard-retrace.md` references:
- 2026-04-10-gic-retrace-full-kernel.md (first retrace)
- 2026-04-10-crm-retrace.md (third retrace, one day later, built on findings here)
- 2026-04-10-post-trace-synthesis.md (routing document)
- 2026-04-10-integration-as-primitive.md (primitive #6; EventGuard exercises inbound)
- 2026-04-10-base-ui-and-auth-design.md (identity providers as Integrations; ephemeral locks)
- 2026-04-10-realtime-architecture-design.md (RESOLVES the mid-conversation event delivery gap via harness + scoped events stream + Temporal signals; Runtime + Attention primitives)
- 2026-04-10-bulk-operations-pattern.md (resolves bulk operations as a kernel pattern)
- 2026-04-13-documentation-sweep.md (formalizes inbound webhook dispatch — item 4 — + internal Actors vs external entities — item 5)
- Phase 2-3 consolidated spec (implements inbound webhook + bulk + direct invocation)
- Phase 4-5 consolidated spec (Phase 5 §5.3 includes voice harness EXAMPLE; chat harness missing)

### `2026-04-10-gic-retrace-full-kernel.md` references:
- 2026-04-09 architecture-ironing rounds 1, 2, 3 (encoded decisions)
- 2026-04-09 consolidated-architecture.md (pre-retrace state)
- 2026-04-09 unified-queue-temporal-execution.md (queue model)
- 2026-04-10-integration-as-primitive.md (primitive #6; adapter dispatch)
- 2026-04-10-eventguard-retrace.md (second retrace — real-time + inbound webhooks)
- 2026-04-10-crm-retrace.md (third retrace — actor-level Integrations)
- 2026-04-10-post-trace-synthesis.md (routing document for items)
- 2026-04-10-realtime-architecture-design.md (resolves ephemeral locks as Attention, scoped watches, Runtime, harness pattern)
- 2026-04-10-bulk-operations-pattern.md (resolves bulk as kernel pattern)
- 2026-04-11-base-ui-operational-surface.md (resolves dashboards)
- 2026-04-13-simplification-pass.md (REMOVES watch coalescing from kernel)
- 2026-04-13-documentation-sweep.md (resolves computed-field scope as item 6)

### `2026-04-10-session-5-checkpoint.md` references:
- Session 4 checkpoint (foundation — 5 primitives → 6 in session 5)
- 2026-04-10 artifacts (all session 5 outputs): integration-as-primitive, gic-retrace-full-kernel, base-ui-and-auth-design, eventguard-retrace, post-trace-synthesis, crm-retrace, realtime-architecture-design
- Session 6 checkpoint (gap sessions add bulk ops, base UI operational surface, authentication design, simplification pass, documentation sweep)
- Phase 2-3 consolidated spec — DEVIATES from this session's harness decision at §2.4

### `2026-04-13-documentation-sweep.md` references:
- 2026-04-10-integration-as-primitive.md (Integration primitive — this sweep extends it with inbound)
- 2026-04-10-eventguard-retrace.md (surfaced items 4 and 5)
- 2026-04-10-gic-retrace-full-kernel.md (surfaced item 6)
- 2026-04-10-crm-retrace.md (surfaced items 11 and 12)
- 2026-04-10-realtime-architecture-design.md (Runtime, Associate with owner_actor_id)
- 2026-04-11-authentication-design.md (auth patterns, Session entity)
- 2026-04-10-post-trace-synthesis.md (the routing document that categorized these items)
- Phase 2-3 consolidated spec §3 (Integration Framework) implements adapter interface + registry + webhook endpoint
- Phase 4-5 consolidated spec (assistant) — Finding 0b evidence (deviates from documented auth pattern for default assistant)

### `2026-04-13-infrastructure-and-deployment.md` references:
- 2026-04-09-consolidated-architecture.md (the kernel architecture this supports)
- 2026-04-10-realtime-architecture-design.md (harness pattern; specifies 3 images including async)
- 2026-04-11-authentication-design.md (Session + auth middleware in API server)
- 2026-04-13-session-6-checkpoint.md (established this as gap session #1)
- 2026-04-13-white-paper.md (same day, reaffirms harness pattern)
- 2026-04-13-simplification-pass.md (same day, harness pattern survives simplification)
- Phase 0-1 consolidated spec (implements kernel image with API/QP/TW services)
- Phase 2-3 consolidated spec §2.4 (implements `process_with_associate` as kernel Temporal activity → Finding 0 code location)

### `2026-04-13-remaining-gap-sessions.md` references:
- 2026-04-13-infrastructure-and-deployment.md (infrastructure context; this artifact builds on it)
- 2026-04-13-session-6-checkpoint.md (gap session list)
- 2026-04-10-realtime-architecture-design.md (specifies 3 harness images; this artifact lists only 2)
- 2026-04-11-base-ui-operational-surface.md (monitoring surfaces)
- 2026-04-11-authentication-design.md (platform admin model)
- 2026-04-10-crm/eventguard/gic-retrace (8-step domain modeling formalized from these)

### `2026-04-13-session-6-checkpoint.md` references:
- Session 5 checkpoint (predecessor)
- 2026-04-10 bulk-operations-pattern
- 2026-04-11 base-ui-operational-surface
- 2026-04-11 authentication-design
- 2026-04-13 documentation-sweep
- 2026-04-13 simplification-pass
- 2026-04-13 infrastructure-and-deployment
- 2026-04-13 remaining-gap-sessions
- 2026-04-13 white-paper (final deliverable)
- 2026-04-14 impl-spec-phase-* (derived from white paper)

### `2026-04-14-impl-spec-gaps.md` references:
- 2026-04-13-white-paper.md (design source of truth — basis for Pass 1)
- 2026-04-13-simplification-pass.md (simplifications applied)
- 2026-04-13-infrastructure-and-deployment.md (Pass 6 grounding)
- 2026-04-14-impl-spec-phase-0-1 base + addendum (verified)
- 2026-04-14-impl-spec-phase-2-3 base (verified)
- 2026-04-14-impl-spec-phase-4-5 base (verified)
- 2026-04-14-impl-spec-phase-6-7 base (verified)
- 2026-04-14-impl-spec-phase-0-1-consolidated (gap resolutions applied)
- 2026-04-14-impl-spec-phase-2-3-consolidated (gap resolutions applied)
- 2026-04-14-impl-spec-phase-4-5-consolidated (gap resolutions applied)
- 2026-04-14-impl-spec-phase-6-7-consolidated (gap resolutions applied)
- INDEX.md (160+ decisions — Pass 2 grounding)
- 2026-04-14-impl-spec-verification-report.md (confirms all 90 gaps resolved)

### `2026-04-14-impl-spec-phase-0-1-addendum.md` references:
- 2026-04-14-impl-spec-phase-0-1.md (base — this addendum completes it)
- 2026-04-14-impl-spec-phase-0-1-consolidated.md (SUPERSEDES this)
- 2026-04-10-realtime-architecture-design.md (source for Attention + Runtime specs)
- 2026-04-11-authentication-design.md (source for Session spec)
- 2026-04-09-data-architecture-solutions.md (source for migration/validation)
- 2026-04-08-pressure-test-findings.md (source for pre-transition validation hooks)

### `2026-04-14-impl-spec-phase-0-1.md` references:
- 2026-04-13-white-paper.md (design source of truth)
- 2026-04-14-impl-spec-phase-0-1-addendum.md (companion — Attention/Runtime/Session + migration/rotation/approval mechanisms)
- 2026-04-14-impl-spec-phase-0-1-consolidated.md (SUPERSEDES this — integrates base + addendum + gap resolutions)
- 2026-04-14-impl-spec-gaps.md (90 gaps identified in this base spec)
- 2026-04-14-impl-spec-verification-report.md (verification against consolidated spec)

### `2026-04-14-impl-spec-phase-2-3.md` references:
- 2026-04-13-white-paper.md
- 2026-04-09-temporal-integration-architecture.md (source)
- 2026-04-09-unified-queue-temporal-execution.md (source)
- 2026-04-10-integration-as-primitive.md (source)
- 2026-04-09-entity-capabilities-and-skill-model.md (source — `--auto` pattern, skill model)
- 2026-04-10-bulk-operations-pattern.md (source — bulk workflows)
- 2026-04-14-impl-spec-phase-0-1.md (foundation, this builds on)
- 2026-04-14-impl-spec-phase-2-3-consolidated.md (SUPERSEDES this)
- 2026-04-14-impl-spec-gaps.md (22 gaps identified)

### `2026-04-14-impl-spec-phase-4-5.md` references:
- 2026-04-13-white-paper.md
- 2026-04-11-base-ui-operational-surface.md (source)
- 2026-04-10-realtime-architecture-design.md (source — SPECIFIES 3 harness images)
- 2026-04-11-authentication-design.md (source — full auth)
- 2026-04-14-impl-spec-phase-0-1.md (foundation)
- 2026-04-14-impl-spec-phase-2-3.md (predecessor — Phase 2-3 established the `process_with_associate` Finding 0 pattern)
- 2026-04-14-impl-spec-phase-4-5-consolidated.md (SUPERSEDES this)
- 2026-04-14-impl-spec-gaps.md (23 gaps identified)

### `2026-04-14-impl-spec-phase-6-7.md` references:
- 2026-04-10-crm-retrace.md (Phase 6 blueprint)
- 2026-04-10-gic-retrace-full-kernel.md (Phase 7 blueprint)
- 2026-04-13-remaining-gap-sessions.md (8-step domain modeling)
- 2026-04-14-impl-spec-phase-0-1.md (foundation)
- 2026-04-14-impl-spec-phase-2-3.md (associate execution + integrations)
- 2026-04-14-impl-spec-phase-4-5.md (Base UI + real-time)
- 2026-04-14-impl-spec-phase-6-7-consolidated.md (SUPERSEDES this)
- 2026-04-14-impl-spec-gaps.md (4 gaps — smallest phase gap count)

### `2026-04-14-impl-spec-verification-report.md` references:
- 2026-04-13-white-paper.md (design source of truth — 937 lines)
- 2026-04-13-simplification-pass.md (correctly reflected in specs)
- 2026-04-13-infrastructure-and-deployment.md (5 services / trust boundary)
- 2026-04-14-impl-spec-gaps.md (90-gap identification this verification addresses)
- All 4 consolidated specs (phase-0-1, phase-2-3, phase-4-5, phase-6-7)
- INDEX.md (160+ locked decisions)
- 2026-04-15-comprehensive-audit.md (called out the methodology gap this verification missed)
- 2026-04-16-pass-2-audit.md (closed the gap, confirmed Finding 0)

### `2026-04-15-shakeout-session-findings.md` references:
- indemn-os repo at commit `f41b505` (pre-shakeout baseline)
- 2026-04-14-impl-spec-phase-0-1-consolidated.md (implemented)
- 2026-04-14-impl-spec-phase-2-3-consolidated.md (implemented)
- 2026-04-14-impl-spec-phase-4-5-consolidated.md (implemented)
- 2026-04-14-impl-spec-phase-6-7-consolidated.md (implemented)
- 2026-04-15-comprehensive-audit.md (Pass 1 audit — identified Finding 0, motivated Pass 2)
- 2026-04-16-pass-2-audit.md (closed the methodology gap and confirmed Finding 0 + 0b architecturally)

### `2026-04-15-spec-vs-implementation-audit.md` references:
- 2026-04-13-white-paper.md (design source of truth)
- INDEX.md (160+ decisions)
- All 4 consolidated specs
- 2026-04-14-impl-spec-gaps.md + verification-report.md
- 2026-04-15-shakeout-session-findings.md (19 findings)
- 2026-04-15-comprehensive-audit.md (same-day comprehensive audit; motivated Pass 2)
- 2026-04-16-pass-2-audit.md (next-day Pass 2 that closed the methodology gap)
- indemn-os repo at post-shakeout commit

### `architecture.md` references:
- Ryan's wireframes (GIC Email Intelligence repo)
- Kyle's Indemn Technology Systems Map (Google Doc)
- Engineering Priorities Landscape document
- Domain model research (5-angle pressure test)
- Intake Manager codebase
- GIC Email Intelligence codebase
- Later feeds: white paper, realtime-architecture-design, all design artifacts

### `business.md` references:
- Kyle's Google Docs: Revenue Activation, The Proposal, Revenue Engines, Customer OS, Framework VP Pipeline.
- Ian's Four Outcomes Product Matrix.
- Cam's Four Outcomes framework.
- Pipeline dashboard (status currently broken per known issues).
- Meeting intelligence DB.

### `craigs-vision.md` references:
- Ryan's taxonomy (Outcomes → Journeys → Workflows → Capabilities) — Craig adds Domain Objects as the foundational layer
- Cam's 48-item associate matrix (Craig reframes as "processing nodes on a unified platform")
- Kyle's "factory that builds them" framing — Craig: "the factory IS the platform"
- Dhruv's Intake Manager (evolving into the platform core)
- Slack thread with Ryan/Dhruv (March 17) where the Domain Objects + Capabilities + Workflow Templates + Channels + Configuration architecture was first sketched

### `product.md` references:
- Four Outcomes Product Matrix Google Sheet (Ian, Cam)
- Series A source docs (associate-suite, four-outcomes-framework, customer-segments, four-outcomes-product-strategy)
- Package Options Google Doc
- 2026-03-24-associate-domain-mapping.md (the research)
- white paper Section 4 (Tier definitions align with customer segments P1-P3)

### `strategy.md` references:
- Revenue Engines Google Doc (Kyle + Cam alignment)
- Cam Bridge Context Layer Design Doc
- Constraint Removal AI Thought Piece
- Craig/Cam 1:1 + Craig/Kyle Sync meeting notes
- Ryan's wireframes + taxonomy document
- Dhruv's Intake Manager codebase

### `2026-03-25-the-vision-v1.md` references:
- `2026-03-25-the-vision.md` (v2, the successor — factory framing vs. lab framing)
- Ryan's wireframes
- Intake Manager (Dhruv's code)
- GIC Email Intelligence (Craig's code)
- EventGuard
- Cam's 48-associate pricing matrix

### `2026-03-25-the-vision.md` references:
- Vision v1 (predecessor — lab framing vs. factory framing)
- white-paper (descendant — synthesizes vision + architecture + spec)
- All architecture artifacts (implement this vision)
- Four Outcomes Product Matrix
- Ryan's wireframes


## All Architectural Decisions

Aggregated decisions across artifacts. Look for conflicts.


### From `2026-04-13-white-paper.md`:
- **Kernel is domain-agnostic**: no insurance concepts in kernel. Insurance is one domain. Kernel proven against 3 workloads including a zero-insurance B2B case.
- **Everything is data**: entities, skills, rules, lookups, roles, configurations — all stored in database, all managed via CLI. Environments are organizations (dev/staging/prod as separate orgs on same kernel).
- **One save, one event**: selective emission — only state transitions, exposed operations, and entity creation/deletion produce events. Field-only updates are silent.
- **Atomic save-and-emit transaction**: entity save + watch evaluation + message writes = single transaction. "If any part fails, none of it commits."
- **Optimistic dispatch + sweep backstop**: after transaction commits, API fires-and-forgets a workflow start. Queue Processor sweeps for undispatched messages as reliability backstop.
- **Unified queue**: human and AI actors share the same message queue; human claims via UI, associates claim via durable workflow. This enables gradual rollout.
- **Actor spectrum**: deterministic ↔ reasoning, with hybrid via `--auto` pattern (deterministic first, LLM fallback).
- **Credentials never in DB**: Integration entities store reference to external secrets manager. Kernel reads credentials at runtime.
- **Tables over charts**: default UI is interactive tables. Charts reserved for time-series.
- **Auto-generation only for Base UI**: "It is not a bespoke dashboard application with per-organization custom views. No custom UI code per entity. No custom UI code per organization."
- **WebSocket keepalive requirement**: proxy drops idle WebSocket after 60s. All WebSocket handlers — including real-time UI channel AND chat harness — must send ping frames every 30-45s.

### From `2026-04-10-realtime-architecture-design.md`:
- **THE key design decision (Part 4, verbatim)**: "The harness uses the CLI, not a separate Python SDK. This is the key design decision. The CLI is already the universal interface. The harness is 'just another client' of the CLI, calling it via subprocess. No dual interface, no second code path, no framework-specific adapters in the kernel."
- Harnesses are **deployable images**, one per `kind+framework` combo: `indemn/runtime-voice-deepagents`, `indemn/runtime-chat-deepagents`, `indemn/runtime-async-deepagents`.
- Each harness image contains: framework (e.g. deepagents), transport (LiveKit/WebSocket/Twilio/Temporal), harness glue script, `indemn` CLI pre-installed.
- Harness is generic per kind+framework, loads associate config at session start.
- **Transport is NOT a separate kernel concept**. "It's bundled with the Runtime's deployment."
- Watch scoping is **emit-time resolution** (not claim-time filtering). The kernel writes `target_actor_id`; claim queries just filter by it.
- Watch coalescing: applied AFTER scope resolution; only coalesces within a single target actor.
- Heartbeat updates **bypass audit logging** — the kernel has a special path for `indemn attention heartbeat` that updates `last_heartbeat`/`expires_at` without generating a change record. Only open/close/expiration generate changes.
- The Runtime is the persistent bridge during handoff; handler changes, but the Runtime's bridging logic swaps modes.
- Associate carries `owner_actor_id` for delegated credential access (e.g., scheduled sync associates bound to a specific human).

### From `2026-04-10-integration-as-primitive.md`:
- **Adapters remain the same**: Python classes in the OS codebase, organized in an adapter registry, implementing per-provider operations. The design explicitly says "The adapter pattern remains exactly as designed".
- Adapter registry keyed by version: `ADAPTER_REGISTRY["outlook_v2"] = OutlookV2Adapter`.
- Credential resolution order: actor personal → org-level with role-based access → fail.
- Operations that MUST be org-level regardless (carrier payment, regulatory filing) can declare "org-only" and the resolver skips the actor step.
- AWS Secrets Manager is the credential store with pathed secret refs: `/indemn/{env}/org/{org_id}/integration/{id}` and `/indemn/{env}/actor/{actor_id}/integration/{id}`.
- Credential rotation is first-class CLI: `indemn integration rotate-credentials`. Records in changes collection. For OAuth providers requiring user interaction, rotation creates Draft-like work item in owner's queue.
- Every credential access is logged via changes collection + OTEL traces.
- No code path reads credentials from MongoDB. No API response or CLI output contains credentials.
- Integration health: Integration has its own status field; watches on status changes surface problems to ops roles.

### From `2026-03-30-design-layer-3-associate-system.md`:
- **Agent framework: LangChain deep agents (deepagents package).** Rationale: already used (Jarvis, Intake Manager). Full middleware stack. Skills + sandbox + todo + subagents.
- **CLI interaction via `execute()` in sandbox.** Same as Claude Code pattern. "Skills document CLI commands. No tools abstraction needed."
- **Sandbox provider: Daytona** (evaluating at time of writing). Isolated, pre-configured, secure, scalable.
- **Web operators use same harness**. One framework for all agent types. Browser tools added to sandbox.
- **Associate = first-class OS entity**, CLI-creatable. Same pattern as all entities.
- **Skills: auto-generated (entity) + human-authored (workflow).** Entity skills tell WHAT operations exist; workflow skills tell WHEN and HOW to combine them.
- **Permission enforcement at entity layer, not sandbox layer.** "If the associate tries `indemn policy delete POL-001` and it doesn't have policy write permission, the CLI returns a permission error. The entity layer enforces this, not the sandbox."
- **Workflow runner decision deferred.** Custom for MVP, Temporal at scale, blueprint runner if open-sourced. The Workflow entity design is runner-agnostic.
- **Skill composition through entity permissions.** Entity permissions control which entity skills are available; workflow skills reference only entities the associate has access to.

### From `2026-04-09-entity-capabilities-and-skill-model.md`:
- **Kernel capabilities = Python code in the OS, universally available.** The capability library is part of the kernel, not per-entity code.
- **Per-org configuration = rules and lookups stored as data** (Rule and Lookup entities), created via CLI, no code.
- **Skill interpreter reads markdown.** Skills are markdown files describing orchestration and calling CLI commands. The LLM executes them.
- **LLM invocation only when deterministic path fails** (the `--auto` pattern's `needs_reasoning` return value).
- **No per-org code.** An FDE or associate sets up a new org entirely via CLI — no Python required.
- **Tier 3 adapter/capability contribution**: new capability needing a kernel addition = "Indemn engineer (or Tier 3 developer) builds it and adds it to the OS."
- **Deterministic mode for associates** — e.g., Stale Checker: `--mode deterministic`. No LLM, just executes the one command.
- **Capability activation is per-entity-type**, configured with `--evaluates <rule-type>` and `--sets-field <field>` parameters.

### From `2026-04-11-authentication-design.md`:
- **Session is a bootstrap entity** because: on the hot path for every API call, revocation requires persistent state, session listing + forced logout require queryable state, audit requires persistent records.
- JWT signing key: **platform-wide** (one key, rotated on schedule). Per-org isolation via `org_id` in claims + OrgScopedCollection enforcement, not key separation.
- **Credentials never stored inline in MongoDB.** Always Secrets Manager (except Argon2id password hashes, which are non-reversible).
- Argon2id password hashes stored in MongoDB (defense-in-depth via OrgScopedCollection). Raw secrets (TOTP seeds, refresh tokens, backup codes, API key pre-hashes) in AWS Secrets Manager.
- Role-granted additive changes: next refresh (within access-token lifetime) picks up new claims. No immediate action.
- Role-revoked destructive changes: `claims_stale = true`, auto-refresh on next request.
- Default assistant = **projection of user into a running actor**. Its harness authenticates with the user's session JWT (injected at session start). Every action audited as "user X via default associate performed Y." When user logs out, assistant's session dies.
- Owner-bound scheduled associates (Craig's Gmail sync, scheduled background workers) use their own service tokens, independent of user sessions.
- **Auth API endpoints are hand-built workflows, NOT auto-generated CRUD**. "/auth/login, /auth/refresh, /auth/logout, /auth/challenge, /auth/recover" are specifically not entity auto-generated.
- **Kernel auth middleware is kernel code** (not entity-generated). Handles validation + rate limiting + audit.
- JWT signing/validation = kernel code.
- Revocation cache = kernel code.
- Password hashing (Argon2id) = kernel dependency.
- TOTP library (pyotp) = kernel dependency.
- Platform admin cross-org model uses `_platform` org + PlatformCollection — a separate accessor that bypasses OrgScopedCollection filtering.
- No back doors. No security questions. No SMS (phishable).

### From `2026-04-10-bulk-operations-pattern.md`:
- **No new primitive, no new entity.** The pattern is composed from existing kernel machinery.
- **Generic workflow in kernel code**: one `bulk_execute` Temporal workflow that parameterizes across all bulk operations.
- **Idempotency at entity level**: state machines, `external_ref`, method author responsibility. Not enforced by kernel for bulk-method in MVP.
- **Rule of thumb**: if a change should cascade, make it a method (@exposed) and use `bulk-method`. `bulk-update` is explicitly silent.
- **Error classification**: StateMachineError / ValidationError / PermissionDenied / EntityNotFound = permanent (skip); VersionConflict = transient (retry once, then permanent); Network / MongoDB / lock timeout = transient (propagate, Temporal retries whole activity).
- **Default = skip**; `abort` is explicit opt-in for operations where partial completion is worse than total failure.
- **Scope resolution happens per-event at emit time.** Coalescing applied per-target-actor, so each stakeholder sees their own coalesced batch.
- **Unified mechanism for scheduled + ad-hoc**: kernel makes no distinction. Scheduled associates invoke bulk CLI; ad-hoc invocation invokes bulk CLI. Both flow through the same `bulk_execute` workflow.
- **CLI auto-generates** the bulk-* verbs per entity (no manual registration).

### From `2026-04-11-base-ui-operational-surface.md`:
- **UI derives from the system**: entities + roles + watches + permissions + integrations define what the UI shows.
- No bespoke per-org dashboards at MVP.
- Adding a domain entity means UI reflects it immediately. Changing permissions changes what the role can see and do.
- Auto-generation is the ONLY UI construction path for MVP. Future customization is additive.
- **Assistant is always-visible, top-bar input** — not sidebar, not modal, not floating widget, not full-page home. "Visible but non-dominant."
- Assistant panel: overlay, not modal (does not hide current view). Streaming responses. Inline entity renderings using same UI components as rest of the app. ESC closes. Persistent conversation per user.
- Context-awareness: UI sends context payload per assistant turn (view_type, current_entity, current_filter, role_focus, recent_actions). Implicit grounding of "this" etc.
- Assistant panel is a running HARNESS INSTANCE, receiving scoped events via `indemn events stream`. "The conversation panel is just another real-time channel with a running actor, reusing the mechanism from the realtime-architecture design session."
- Real-time update filtering is a design constraint: subscription rebuilt on filter change / pagination change. Flagged for implementation spec.

### From `2026-04-09-data-architecture-everything-is-data.md`:
- **Clean split**:
  - OS Codebase (Git) = the PLATFORM (kernel + kernel capabilities + CLI + API + UI — deployed once per release)
  - MongoDB = all configuration AND business data
  - S3 = unstructured files
  - Temporal Cloud = execution state (durable workflows)
  - OTEL = observability traces (ephemeral)
- **Per-org config in MongoDB**: entity definitions, skills, rules, lookups, role configs, associate configs, capability activations.
- **Per-org business data**: entity instances, message_queue, message_log, changes collection.
- **Kernel data (cross-org)**: Organization, Actor, Role definitions (bootstrap entities).
- **Files: S3, not GridFS.** Scoped by org. Referenced by entity fields.
- Built-in version control via changes collection. Every change rollbackable. History queryable. Diffs available. Exports provide snapshots.
- **Clone/diff/deploy semantics**:
  - `indemn org clone gic --as gic-staging` copies entity definitions, skills, rules, lookups, watches, associate configs, role configs.
  - **Does NOT copy**: entity instances (business data), message queue/log.
  - `indemn org diff` shows config differences.
  - `indemn deploy --from-org gic-staging --to-org gic` is a Temporal deployment workflow with validate → apply → verify → rollback-on-failure.
- **Import/export**: YAML format for the export of org configuration.
- **Rollback** is CLI command. "Shows preview of what would be rolled back. Requires confirmation."
- Version control granularity: every entity-def modification, every rule change, every skill update is a change record. Specific-object history available.

### From `2026-04-13-simplification-pass.md`:
- **Watch coalescing is a UI concern, NOT a kernel mechanism.** Kernel removes:
  - `coalesce` field on watch definitions
  - `batch_id` field on message schema
  - Time-window grouping logic in emission path
- **Kernel preserves:**
  - One save = one event
  - Per-entity messages in the queue (associates still process individually)
  - Scoped watches (still write `target_actor_id`)
  - Correlation_id-based grouping is possible client-side
- **Rule evaluation detail stored in change record metadata**: rules_checked, matched, vetoed, needs_reasoning as fields on the change record. Debuggability preserved.
- **Runtime stays** — kernel dispatches work to Runtimes, monitors health, routes real-time events through them. Dependency is real.
- "Bootstrap entity" renamed to "kernel entity" (self-evident terminology).
- Schema migration is first-class MVP. "We're building a real system. Entities will evolve through real usage within weeks."
- Content visibility scoping is MVP. "We are starting with CRM use case." Personal integrations need privacy from day one.
- Rule groups with lifecycle are MVP. "Without groups, 50 rules become unmanageable."

### From `2026-04-10-base-ui-and-auth-design.md`:
- Base UI is a rendering layer over primitives. No separate UI data model, no separate UI state layer beyond standard front-end caching.
- 1:1 mapping with CLI: "Anything a role can do via CLI, they can do in the UI. Nothing in the UI requires CLI fallback."
- **Watch coalescing**: originally proposed as kernel addition with `coalesce` config on watches and `batch_id` on messages. **LATER SIMPLIFIED OUT** per 2026-04-13-simplification-pass.md — moved to UI-only rendering by correlation_id.
- **Ephemeral entity locks**: originally proposed as small kernel collection with TTL expiration + heartbeat protocol. **LATER UNIFIED INTO ATTENTION** per 2026-04-10-realtime-architecture-design.md — "Attention unifies UI soft-locks and active routing context."
- Authentication methods coexist per actor (password + MFA, SSO + password fallback, API keys + interactive).
- "No credentials are ever stored inline. Everything references AWS Secrets Manager."
- Password is a kernel-native method (not via Integration).
- SSO is via Integration using `system_type: identity_provider`.
- Role stays as one primitive with two creation ergonomics; inline roles have `can_grant: null`.
- Parallel scaling of associates: multiple associates share an explicit named role (Path 1); first to claim wins.

### From `2026-04-10-post-trace-synthesis.md`:
- No new primitive or new kernel entity required by the two retraces.
- The three identified "architectural gaps" (coalescing, ephemeral locks, actor-context watch scoping) are ALL additive — none require changing existing watch behavior.
- All three slot into the existing primitive model without introducing new primitives.
- Categorization:
  - Must-design before spec (architectural): items 1, 2, 3, 7
  - Design before spec (supporting infrastructure): items 4, 8, 9
  - Separate session (own scope): item 10 (auth)
  - Just documentation: items 5, 6

### From `2026-04-14-impl-spec-phase-0-1-consolidated.md`:
- **Modular monolith**: one image, three entry points. API (port 8000), Queue Processor, Temporal Worker.
- **Trust boundary**: kernel processes (API Server, Queue Processor, Temporal Worker) have DB creds. "Everything else uses the API."
- **Entity types**:
  - Kernel entities: Python classes in `kernel_entities/`. Always available. 7 total.
  - Domain entities: Defined as data in MongoDB `entity_definitions` collection. Dynamic classes created at startup.
  - Both share BaseEntity. Both get auto-generated CLI, API, skills.
- **`save_tracked()` is the critical atomic transaction**: version check → entity write → computed fields → changes record (with hash chain) → watch evaluation → message creation.
- **Context variables** (`contextvars`) for `current_org_id`, `current_actor_id`, `current_correlation_id`, `current_depth`. Set by auth middleware on each request.
- **OrgScopedCollection** wraps all application queries. Never use raw Motor collections. `org_id` comes from contextvars.
- **PlatformCollection** for cross-org admin (bypasses org scoping).
- **Auth middleware**: sets context vars on each request, loads roles, validates JWT, sets `request.state.actor`.
- **JWT signing**: HS256, 15min expiry, jti for revocation.
- **Argon2id** for password hashing (time_cost=3, memory=64MB, parallelism=4, hash_len=32).
- **Selective emission**: only state transitions, exposed operations, and creation/deletion emit events.
- **Auto-generation from entity definitions**: CLI commands, API routes, skill markdown, UI (UI in Phase 4).

### From `2026-04-14-impl-spec-phase-2-3-consolidated.md`:
### Phase 2 (CRITICAL — Source of Finding 0)

- **`kernel/temporal/worker.py` is the kernel Temporal Worker entry point** (`python -m kernel.temporal.worker`). Per its docstring: "Executes associate workflows and kernel workflows."
- **Worker registers** 3 workflows (ProcessMessageWorkflow, HumanReviewWorkflow, BulkExecuteWorkflow) and 6 activities (claim_message, load_entity_context, **process_with_associate**, complete_message, fail_message, process_bulk_batch).
- Worker config: max_concurrent_activities=20, max_concurrent_workflow_tasks=10, graceful_shutdown_timeout=30, OTEL TracingInterceptor.
- **`process_with_associate` IS THE AGENT EXECUTION LOOP placed inside the kernel Temporal Worker as an activity.** It:
  - Loads associate config (Actor.get)
  - Sets auth context (current_org_id, current_actor_id, current_correlation_id, current_depth)
  - Loads + verifies skills (Skill.find_one, verify_content_hash)
  - Dispatches to `_execute_deterministic`, `_execute_reasoning`, or `_execute_hybrid` based on associate.mode
- **`_execute_reasoning` implements the LLM tool-use loop INSIDE THE KERNEL**:
  - `import anthropic` at line 557
  - `client = anthropic.AsyncAnthropic()` at line 563
  - `client.messages.create(model=model, tools=[{execute_command tool}], ...)` at line 590
  - Iterates up to 20 times, feeding tool results back to LLM
  - "For Phase 2 MVP: use Anthropic API directly. Future: pluggable LLM provider per associate.llm_config"
- **`_execute_deterministic` parses markdown skill line-by-line** and executes CLI commands via HTTP.
- **`_execute_hybrid`**: try deterministic first; if any step returns `needs_reasoning`, fall back to `_execute_reasoning`.
- **`_execute_command_via_api`**: the agent executes "CLI commands" by making HTTP POST to the kernel's API. Parses `indemn email classify EMAIL-001 --auto` → POST to `/api/emails/EMAIL-001/classify`. **This is the agent-to-kernel interface within the same monolith.**
- Context propagation via headers: `X-Correlation-ID`, `X-Cascade-Depth`. API middleware reads headers and sets contextvars.
- **Optimistic dispatch**: API fires-and-forgets Temporal workflow start after save_tracked() commits.
- **Sweep backstop**: Queue processor checks every few seconds for undispatched associate-eligible messages.
- **Direct invocation endpoint** `/api/associates/{associate_id}/invoke` creates queue entry AND starts workflow immediately.

### Phase 3 (Integration Framework)

- Adapter base class `Adapter(ABC)` in `kernel/integration/adapter.py` — abstract methods for fetch/send/charge/validate_webhook/parse_webhook/auth_initiate/auth_callback/refresh_token.
- Adapter registry `ADAPTER_REGISTRY` in `kernel/integration/registry.py`, keyed by `provider:version`.
- Credential resolver `resolve_integration()` in `kernel/integration/resolver.py`.
- Credential management with OAuth token refresh in `kernel/integration/credentials.py`.
- Adapter dispatch in `kernel/integration/dispatch.py` with auto-refresh on AdapterAuthError.
- Webhook endpoint in `kernel/api/webhook.py` — `/webhook/{provider}/{integration_id}` — looks up Integration, invokes adapter's validate_webhook + parse_webhook.
- Outlook adapter (email) and Stripe adapter (payments) as reference implementations in `kernel/integration/adapters/`.

### From `2026-04-14-impl-spec-phase-4-5-consolidated.md`:
### Phase 4 Assistant (THIS IS THE SECOND SOURCE OF FINDING 0)

**`kernel/api/assistant.py` is defined at line 836-876**:

```python
# kernel/api/assistant.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from kernel.auth.middleware import get_current_actor

assistant_router = APIRouter(prefix="/api/assistant", tags=["assistant"])

@assistant_router.post("/message")
async def assistant_message(data: dict, actor=Depends(get_current_actor)):
    """Process an assistant message. The default associate runs with
    the user's own session — same permissions, audit as 'user via assistant'. [G-59]"""
    content = data.get("content", "")
    context = data.get("context", {})

    async def generate():
        import anthropic
        client = anthropic.AsyncAnthropic()
        skills = await load_skills_for_roles(actor.role_ids)

        async with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=f"You are the user's assistant in the Indemn OS. "
                   f"You can execute operations using the Indemn API. "
                   f"The user is viewing: {context}.\n\n"
                   f"Available operations:\n{skills}",
            messages=[{"role": "user", "content": content}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    return StreamingResponse(generate(), media_type="text/plain")
```

**This endpoint:**
- Lives in `kernel/api/` (kernel API server process, inside trust boundary)
- Imports `anthropic` directly
- Creates an LLM stream with NO TOOLS (no `tools=[]` parameter)
- System prompt says "You can execute operations" but LLM has no mechanism to do so
- Returns text-only streaming response

**Per design (2026-04-11-base-ui-operational-surface.md)**: the assistant should be a running harness instance (chat-kind Runtime), outside the kernel, using the CLI for all operations via `execute_command`-style tool-use.

**Per design (2026-04-11-authentication-design.md line 463-482)**: "the default assistant inherits the user's session. Its harness authenticates using the user's session JWT (injected at session start)."

**The Phase 4 spec deviates from the design** by placing the assistant inside the kernel API server as a stripped-down streaming endpoint with no tools. This is Finding 2 (no tools) which is a direct consequence of Finding 0 (no harness pattern).

### Phase 5 Harness Pattern (correctly specified, but not implemented as deployable)

**`harnesses/voice-deepagents/main.py` at line 1587-1734** shows a complete harness example:
- Uses LiveKit `Agent` + `AgentSession`
- CLI wrapper (`cli(command)`) that runs `subprocess.run(["indemn"] + command.split())`
- Authenticates via `INDEMN_SERVICE_TOKEN` environment variable
- Creates Interaction, opens Attention, loads skills via CLI
- Uses `deepagents.create_deep_agent(...)` locally inside the harness
- Three-layer config merge: Runtime defaults → Associate override → Deployment override
- Event listener subprocess: `indemn events stream --actor X --interaction Y`
- Heartbeat loop: `cli("attention heartbeat ...")` every 30s
- On session end: closes Attention + transitions Interaction

**Per Phase 5 acceptance criteria (line 2051-2053):**
"HARNESS USES CLI ONLY — All harness-to-kernel communication via CLI subprocess → no direct MongoDB → no Python SDK"

**Per comprehensive audit:** "No harness code exists. The Phase 4-5 spec shows a complete voice harness example, but it's spec, not code." The harness example was included as documentation in the spec but never implemented as a deployable image.

### The Asymmetry

- **Phase 4 assistant**: spec'd as kernel endpoint (in-kernel, no tools, text streaming only). Implemented as specified.
- **Phase 5 voice harness**: spec'd as separate deployable with CLI pattern (outside kernel, full tools via deepagents). NOT implemented.

The Phase 5 spec gets the harness pattern RIGHT (matches the design). The Phase 4 spec gets the assistant pattern WRONG (should be a chat-harness but is a kernel endpoint).

**Why the inconsistency in the specs themselves:**
- Phase 4 (Base UI) needed the assistant to work at the end of Phase 4.
- Phase 5 (Real-Time, harnesses) comes AFTER Phase 4.
- So Phase 4 couldn't use a harness — the harness pattern is defined in Phase 5.
- Phase 4 improvised with a kernel-side endpoint.
- Phase 5's harness example was voice-only — no chat-runtime harness for the assistant was specified.

### From `2026-04-14-impl-spec-phase-6-7-consolidated.md`:
- **Naming collision resolution**: Kernel already has `Organization` entity (multi-tenancy scope). CRM customer orgs use `Company` to avoid collision. This is a Phase 6 decision, not a Phase 0 decision.
- Phase 6 applies the white paper's 8-step domain modeling process as a concrete CLI sequence.
- Meeting intelligence extraction is LLM-based (mode: reasoning). Overdue check is deterministic.
- Scheduled associates: Overdue Checker (`0 8 * * *`), Craig Gmail Sync (`*/5 * * * *`).
- Gmail sync associates are owner-bound (`--owner-actor craig@indemn.ai`), using owner's Integration credentials.
- Phase 7 reuses Phase 6's pattern: define entities, configure roles + watches, create rules and lookups, write skills, set up integrations, test in staging, deploy to production.
- Org clone/diff/deploy for staging → production promotion.
- "What is NOT exported: entity instances (business data), messages, changes, sessions, attentions, secrets/credentials."
- Hard rules (USLI domain, Hiscox domain) + veto rules (USLI subject contains "Decline" → force_reasoning).
- Lookup tables for carrier/LOB mappings.

### From `activities.py`:
**This file implements the agent execution loop as a kernel Temporal activity.** Exactly matches the Phase 2-3 consolidated spec.

- `process_with_associate` is a `@activity.defn`. It runs in the Temporal worker process. The Temporal worker is the `indemn-temporal-worker` Railway service — a kernel process.
- Loads associate via `Actor.get(ObjectId(associate_id))` — direct MongoDB access via Beanie.
- Sets contextvars: `current_org_id`, `current_actor_id`, `current_correlation_id`, `current_depth`.
- Loads skills via `_load_skills` — direct MongoDB query via Beanie: `await Skill.find_one({"name": name, "status": "active"})`.
- Verifies skill content hash via `verify_content_hash` (kernel/skill/integrity.py).
- Dispatches to one of three execution paths based on `associate.mode`:
  - `deterministic`: `_execute_deterministic`
  - `reasoning`: `_execute_reasoning`
  - `hybrid` (default): `_execute_hybrid`
- `_execute_reasoning` instantiates `anthropic.AsyncAnthropic()` client INSIDE the activity, iterates up to 20 times with tool-use loop, adds `execute_command` tool, calls `client.messages.create(model=model, tools=[{execute_command}], ...)`.
- `_execute_command_via_api` creates an access token via `kernel.auth.jwt.create_access_token` (lines 582) for the associate, makes HTTP POST to `{settings.api_url}/api/{entity_type}s/{entity_id}/{operation}` with Bearer token + correlation/depth headers.
- The agent's tool executions go through the kernel's own API — via HTTP — on the same process or a sibling kernel process. **Everything happens inside the kernel's trust boundary.**
- `process_bulk_batch` is ALSO in this file — handles bulk ops with MongoDB transactions. This is legitimately kernel-side work per the design (bulk is a kernel-provided pattern).

### From `assistant.py`:
- This is an HTTP endpoint in the kernel API server (`kernel/api/` directory).
- Runs in the kernel API server process (`indemn-api` Railway service).
- Inside trust boundary (has direct MongoDB access via `Role.find`, `Skill.find`, `ENTITY_REGISTRY`).
- Directly imports `anthropic` at line 37.
- Stream response via FastAPI's `StreamingResponse`.
- Auth via `get_current_actor` from `kernel.auth.middleware` — uses the USER's JWT. The assistant inherits the user's session.
- Skill list injected via string concatenation into the LLM system prompt — NOT as structured tools.

**This is a degraded/stripped-down agent execution:**
- No tools (no `tools=[]` param on `client.messages.stream`)
- No iteration loop (just streams one response)
- No `execute_command` mechanism
- No actual integration with the CLI
- Just text streaming

**Compare with `kernel/temporal/activities.py::_execute_reasoning`:**
- `_execute_reasoning` has tools (the `execute_command` tool is defined)
- `_execute_reasoning` has an iteration loop (up to 20 iterations)
- `_execute_reasoning` actually routes tool calls to `_execute_command_via_api`
- But `_execute_reasoning` runs in the Temporal Worker for associate-triggered work, NOT for user-facing assistant interactions

**Two parallel code paths:**
1. Associate-processing path (`kernel/temporal/activities.py::process_with_associate` → `_execute_reasoning`): has tools
2. User assistant path (`kernel/api/assistant.py::assistant_message`): no tools

### From `workflows.py`:
- **All three workflow types live in the kernel Temporal Worker.** They execute the activities defined in `kernel/temporal/activities.py`.
- **`ProcessMessageWorkflow` calls `process_with_associate`** — the activity that contains the agent execution loop (Finding 0 code).
- Workflow durability: if worker crashes mid-workflow, Temporal replays from the last checkpoint (activity result).
- Timeout defaults: claim=30s, load_context=30s, process=10min with 2min heartbeat_timeout, complete=30s.
- Retry policies: 2-3 attempts with backoff; non-retryable for PermanentProcessingError, SkillTamperError, PermissionError.
- `HumanReviewWorkflow` uses Temporal signals — UI posts to endpoint → endpoint sends signal → workflow resumes.
- `BulkExecuteWorkflow` uses deliberate coupling: `bulk_operation_id = temporal_workflow_id`.

### From `worker.py`:
- **Single task queue for everything: `"indemn-kernel"`.**
- All workflows and activities live on this one queue.
- The worker is the `indemn-temporal-worker` Railway service — a kernel process with direct MongoDB access.
- OTEL tracing on every workflow + activity.
- Lifecycle: setup_logging → init_tracing → init_database → connect Temporal client → start worker.

### From `adapter.py`:
- Adapters live in the kernel (`kernel/integration/adapter.py`).
- Inherit from `ABC`.
- Methods are optional — subclasses override what they support.
- Error hierarchy enables retry classification (auth → refresh; rate → backoff; timeout → retry; not_found/validation → permanent).
- `parse_webhook` docstring says returns `{entity_type, lookup_by, lookup_value, operation, params}` — a standardized inbound webhook parse format.

### From `registry.py`:
- Registry is a module-level dict — simple in-process singleton.
- Keyed by `{provider}:{version}` format — enables per-org adapter version upgrades.
- Registration happens via `register_adapter` call — typically at module import time from concrete adapter modules.
- Lookup raises `AdapterNotFoundError` (a concrete exception) rather than returning None — forces callers to handle.

### From `dispatch.py`:
- Integration resolution → credential fetch → adapter instantiation → optional token refresh = single `get_adapter` call.
- Adapter's `_secret_ref` attribute stored on instance for retry logic reference.
- Token refresh is transparent: `adapter.needs_token_refresh()` check triggers refresh before returning adapter.
- `execute_with_retry` handles three error classes: auth (refresh + retry), rate-limit (backoff + retry), timeout (immediate retry).
- No retry on `AdapterValidationError` or `AdapterNotFoundError` (permanent errors).

### From `resolver.py`:
- **Priority chain matches the design** (2026-04-10-integration-as-primitive.md): actor → org.
- **Step 2 (owner's personal)** supports owner-bound associates from the CRM retrace (e.g., Craig's Gmail sync associate uses Craig's Gmail integration).
- Queries MongoDB directly via Beanie (`Integration.find_one`, `Actor.get`, `Role.find`) — inside trust boundary.
- `require_org_only=True` skips personal integrations (for operations that must use org credentials like carrier payment).
- Matches the access.roles check for org-level integrations — role names in the Integration's access.roles list must intersect the actor's role names.

### From `websocket.py`:
- One MongoDB Change Stream per WebSocket connection, filtered by org_id.
- Subscriptions are client-side: the browser sends subscribe messages; the server filters the change stream accordingly.
- Authentication via query param (not header) — necessary for browser WebSocket API which can't set Authorization header directly.
- Cleanup: cancel watcher task on disconnect; remove connection from `_connections`.
- Subscription filter supports entity_type, entity_id, collection.

### From `events.py`:
- Implements the `indemn events stream` backend per design (2026-04-10-realtime-architecture-design.md).
- Server-Sent Events / ndjson format — suitable for long-running subprocess consumption by harnesses.
- Scope filter: `target_actor_id == actor OR target_actor_id IS NULL` — delivers both scoped-to-this-actor messages AND unscoped messages that match the role.
- Interaction filter checks multiple places where interaction_id might live (context, entity_id, event_metadata) — defensive.
- Media type `application/x-ndjson` — streaming JSON lines.
- Auth via middleware (`get_current_actor`) — requires bearer token.

### From `interaction.py`:
- Handoff is a field update on Interaction (`handling_actor_id` / `handling_role_id`) per design.
- Attention opens and closes as part of handoff — ties into the unified Attention mechanism.
- Re-targeting pending messages ensures queue items follow the new handler.
- Observe is a first-class state (per design) — Attention with purpose="observing", not a separate mechanism.
- Auth via `get_current_actor` — requires valid session.
- Does not validate role permissions to transfer (assumes middleware + entity layer handle it).

### From `generator.py`:
- Skill generation happens at entity definition creation/modification time (called elsewhere).
- Output is markdown — human-readable and LLM-consumable.
- Entity auto-generation creates CLI commands (list/get/create/update, optionally transition, + per-capability `<cap_name> --auto`).
- No logic — pure text generation.

### From `schema.py`:
- Skills stored in MongoDB per design ("everything is data").
- Content hashed for tamper detection (per white paper § Security).
- Two types (entity + associate) per design.
- Status workflow: active / pending_review / deprecated — supports skill approval workflow.
- `org_id` is optional — None means system-level (shared across orgs, for auto-generated entity skills).

### From `session_manager.py`:
- Session is kernel entity (bootstrap) — matches design.
- JWT creation via `kernel.auth.jwt.create_access_token`.
- Role names loaded at session creation time and embedded in JWT claims.
- Session status transitions via state machine (`transition_to("revoked")`).
- `save_tracked` used for revocation (audit trail in changes collection) — correct.
- `system:revocation` sentinel actor_id for system-initiated revocations.

### From `jwt.py`:
- Platform-wide JWT signing key (per design).
- HS256 algorithm (from `settings.jwt_algorithm`).
- jti (UUID) in every token for revocation tracking.
- 15-minute access token expiry (`jwt_access_token_expire_minutes`).
- In-memory revocation cache invalidated via MongoDB Change Streams on Session entity.
- Cache TTL = 15 minutes = max access token lifetime (older revocations are moot because tokens are already expired).
- Bootstrap on instance startup prevents stale cache until Change Stream catches up.
- Partial tokens and magic link tokens use `purpose` field for context-specific use.

### From `auth_routes.py`:
- Platform admin session creation validates actor is in `_platform` org with `platform_admin` role.
- Max duration 24h enforced in code (per design).
- Platform admin session stores `platform_admin_context` dict on Session entity.
- Auth events written via `write_auth_event_in_org` (from `kernel.auth.audit`) — per design, audited in the TARGET org's changes collection.
- Target org notification via `_notify_platform_admin_access` helper.
- Access token created with `["platform_admin"]` role in JWT for target org.
- MFA flow: partial token issued on password success, TOTP or backup code verifies → real access token.
- SSO flow: redirect to IdP via Integration adapter → callback validates token → issue OS session.
- Tier 3 signup creates Org + Actor + password method + verification magic link.

### From `registration.py`:
- **Self-evidence property**: define an entity, its API routes appear automatically via `register_entity_routes`.
- All routes require authentication (Depends on `get_current_actor`) and permission check (`check_permission`).
- All reads use `find_scoped`/`get_scoped` — org scoping automatically applied.
- Create/update/transition all go through `save_tracked` (the atomic transaction).
- Capability routes take `?auto=true` query param — matches `--auto` CLI pattern.
- State field changes rejected on PUT; must use /transition endpoint (state machine bypass protection per comprehensive audit).
- Bulk endpoint starts Temporal workflow with `task_queue="indemn-kernel"`.
- Integration dispatch endpoint accepts system_type + params, calls adapter method.

### From `bulk.py`:
- Bulk monitoring queries Temporal directly (not MongoDB) — consistent with design ("execution state lives in Temporal").
- `list_workflows` uses Temporal's workflow query syntax: `"WorkflowType = 'BulkExecuteWorkflow'"`.
- Cancel is graceful (cancels at next batch boundary per design).
- Auth required on all endpoints.
- Workflow dispatched to `task_queue="indemn-kernel"` — consistent with current kernel worker.

### From `AssistantProvider.tsx`:
- Assistant UI uses HTTP POST + streaming text response (not WebSocket).
- Auth: user's JWT via Bearer header (matches design — "inherits user's session").
- Context: minimal (view_type + path) — much simpler than the design's expected context (view_type, current_entity, current_filter, role_focus, recent_actions).
- Streaming: reads response body as chunks, updates last message reactively.
- Error handling: replaces streaming message with error text if fetch fails.

### From `useAssistant.ts`:
- Standard React context pattern for sharing assistant state across the UI.
- Message schema is minimal: id, role, content — plain text only.
- Default context values are no-ops (prevents crashes if hook used outside provider).

### From `org_lifecycle.py`:
- **Config-only operations, matching design**: entity instances NOT exported/cloned per design.
- **Secrets excluded**: integrations exported without `secret_ref`, `last_checked_at`, `last_error`.
- **Human actors excluded**: only associate actors exported (`type: "associate"`). Matches design (human actors are per-person, not org configuration).
- **Skill content hash recomputed on import** (via `compute_content_hash`) — maintains tamper-evidence.
- Categories exported: org settings, entities, rules, lookups, skills, roles, actors (associates only), integrations, capabilities.
- Diff computes per-category: only_in_a, only_in_b, modified.
- Deploy: dry-run preview shows changes; apply mode updates target (only_in_a + modified, skips only_in_b).
- Insert-or-update pattern for each category in `_apply_config_item`.

### From `cache.py`:
- Per-instance in-memory cache (no shared cache).
- TTL refresh is async — returns stale cache while reload runs in background.
- Immediate invalidation on Role save (called from save_tracked hooks).
- Module-level state `_cache`, `_cache_loaded_at`.
- Cross-instance consistency handled by TTL + save-triggered invalidation. Future: Change Stream on roles collection.

### From `evaluator.py`:
- Single JSON condition language for watches and rules (per design).
- Pure function — no I/O, deterministic.
- Operator dispatch via dict lookup.
- Strict operator set — unknown operators raise ValueError.
- Timezone-aware datetime handling in `older_than`.

### From `Dockerfile`:
- **Single image for all kernel processes.** Different Railway services override CMD to run:
  - API Server: `python -m kernel.api.app`
  - Queue Processor: `python -m kernel.queue_processor`
  - Temporal Worker: `python -m kernel.temporal.worker`
- Matches Phase 0-1 spec §0.3 Dockerfile and §0.9 Deployment.
- No `harnesses/` directory copied — Dockerfile doesn't include harness code.

### From `docker-compose.yml`:
- Local dev uses three services: API, Queue Processor, Temporal dev.
- **The Temporal Worker is NOT in docker-compose.yml** — this is a notable absence.
- Volume mount enables hot reload.
- Remote infrastructure: MongoDB Atlas, AWS Secrets Manager (env vars expected).

### From `2026-03-24-associate-domain-mapping.md`:
- **Domain model must support Tier 1 objects**: Policy, Customer, Coverage, Carrier, Document, Agent, LOB. These are universal (>50% of associates).
- **Tier 2 (must-model)**: Task, Rule, AuditLog, Submission, KnowledgeBase, Quote, Message, Conversation.
- **Capabilities** treated as first-class (Generate, Search, Validate, Route, Classify, Extract, Score, Notify, Draft, Recommend, Monitor, Quote, Triage, Schedule, Transform, Verify, Aggregate, Bind, Enforce, Enrich).
- **Platform is one system, three configurations** — Agencies/Carriers/Distribution share domain objects + capabilities; differences are in primacy, channel, and rules.
- **Workflow engine must support both reactive and proactive patterns** — event-driven triggers + request-response.
- **AuditLog is automatic infrastructure**, not per-associate implementation.
- **Knowledge layer is segmentable by audience** (internal, agents, consumers).

### From `2026-03-24-source-index.md`:
- None. This is a provenance catalog, not an architectural document.

### From `2026-03-25-associate-architecture.md`:
- **Skills = markdown documents** (like Claude Code). Tentative at this stage; later resolved in entity-capabilities-and-skill-model (2026-04-09) as markdown.
- **Associate = deep agent** with CLI/API tool access.
- **LangFuse** as observability — later superseded in white paper by OTEL-centric observability.
- **Evaluation framework** extends from conversation quality to workflow outcomes.
- **48 associates are configurations of one system** (reinforces earlier mapping's claim).

### From `2026-03-25-domain-model-research.md`:
- **Platform vs Domain separation** — this is where the "everything is data" decision originates. Platform layer (Associate, Skill, Workflow, Rule, Template, KnowledgeBase, Channel, Organization, Task, Interaction, Correspondence, Document, Email, Draft, ParameterAudit) vs. insurance-specific entities.
- Phasing: don't need all 70 entities on day one.
- **Incremental expansion through sub-domains** — each adds its own schemas/APIs/CLI without restructuring.
- **Platform Layer is infrastructure**, separate from domain (recognizable to insurance people).

### From `2026-03-25-domain-model-v2.md`:
- Every aggregate root → own schema, state machine, API, CLI. This becomes the "entity auto-generation" concept in later designs.
- Configuration vs transaction pattern — pervasive decision.
- ParameterAudit dropped as domain entity; acknowledged as "cross-cutting audit infrastructure (event store), not domain entity." This foreshadows the changes collection + OTEL in the final architecture.
- 3-phase build mapping (Foundation → Middle Market → Carrier Grade).
- Phase 1: ~25 total things (entities + children + reference tables).

### From `2026-03-25-platform-tiers-and-operations.md`:
- **Tier 3 is the primary development model** — internal Indemn devs + FDEs use the same CLI as external Tier 3 customers. This means the CLI must be complete and self-sufficient.
- **Self-service Tier 3 signup** — sign up on website, get CLI + API access, no sales call. Later formalized in auth design (2026-04-11) Tier 3 signup flow.
- **PaaS model** — Indemn hosts everything customers build; no "on-prem" deployment.
- **Usage-based Tier 3 pricing** (deferred design per artifact).
- Future team structure: OS Core, Applications, Deployment/FDE, Current Operations, Sales/GTM.

### From `2026-03-25-session-notes.md`:
- **CLI is universal control plane** — Craig: "With the click of a button, theoretically, or a few buttons, you could set up an end-to-end insurance business. All through the CLI, we as a team and the customers themselves could use our CLI and automate everything."
- **Not a migration** — new platform, built alongside existing; existing customers migrate over time or stay.
- **OS as engine that builds OS** — "the engine actually implementing the work from beginning to end."

### From `2026-03-25-the-operating-system-for-insurance.md`:
- **OS is the hub** — everything connects to it via the CLI and APIs.
- **Every entity has state machine + API + CLI command** — later resolved as auto-generation from entity definitions.
- **CLI as universal installer** — Tier 3 deployment model. CLI commands like `indemn org create`, `indemn product configure`, `indemn associate deploy`, `indemn channel connect`, `indemn integration connect`.
- **"Configuration, not construction"** — new customer = data configuration, not code writing. Later formalized in "everything is data" data architecture.

### From `2026-03-25-why-insurance-why-now.md`:
- **AI-native from day one** — "Every entity has a CLI. Every operation is agent-accessible."
- **Not AI as feature on legacy systems** — AI as foundation, insurance modeled around it.
- **Automation spectrum supported structurally** — platform must support fully-automated, HITL, and human-directed flows.

### From `2026-03-30-design-layer-1-entity-framework.md`:
- **Modular monolith, not microservices** — solo builder, operational simplicity, splittable later.
- **Beanie as ODM** — Pydantic models ARE MongoDB documents. Later kept in consolidated spec.
- **FastAPI + Typer** — same mental model, auto-registration from entity classes.
- **RabbitMQ for domain events** — "Already in infrastructure (Amazon MQ). Domain events published to RabbitMQ, subscribers consume." **NOTE: This was later superseded** — the white paper and consolidated specs use MongoDB message_queue + message_log (not RabbitMQ) as the message bus. RabbitMQ is referenced in indemn-microservices repo but the OS uses MongoDB.
- **AutoRegisterMixin** — entity classes auto-register API routes, CLI commands, skills.
- **Python classes as entity definitions** — "The entity classes ARE the definitions." **NOTE: This was later superseded** — 2026-04-09-data-architecture-everything-is-data.md moves entity definitions from Python classes on disk to MongoDB documents with dynamic class creation.
- **Sub-domain organization** — file structure by sub-domain. Later simplified via dynamic entity definitions.
- Services emit events via RabbitMQ; consumers subscribe.

### From `2026-03-30-entity-system-and-generator.md`:
- **Build generator pattern from scratch** — purpose-built for insurance + CLI-first.
- **Postgres (this early doc)** — later SUPERSEDED by MongoDB decision (Beanie ODM, Pydantic-native, document-oriented fits flexible data).
- **YAML as entity definition format** — later partially changed: entity definitions stored as JSON in MongoDB per 2026-04-09-data-architecture-everything-is-data.md; YAML is used for org export/import only.
- **Auto-generate everything** — RETAINED as core principle.
- **Skills as self-documentation** — RETAINED.

### From `2026-03-30-vision-session-2-checkpoint.md`:
- **MongoDB (not Postgres)** — "team already uses it everywhere, document model fits insurance's inherent field variability."
- **Build from scratch**, don't adopt CRM framework.
- **Generator as OS kernel** — declarative entity definition → auto-generate everything.
- **Skills serve three audiences** — AI associates, Tier 3 developers, engineers.
- **Product configuration vs custom entities** — OS provides complete domain model; users configure, don't create new entities (with Tier 3 exception).
- **Dog-food the OS for Indemn's own CRM** — first customer is Indemn itself.

### From `2026-04-02-core-primitives-architecture.md`:
**Foundation hardening from adversarial review (2026-04-07):**
1. **Version field on every entity** — optimistic concurrency (prevents silent overwrite).
2. **Transactional entity+message atomicity** — same MongoDB transaction. "Cost: 5-15% write latency. Benefit: eliminates silent message loss." This is the #1 architectural invariant (later expressed as save_tracked()).
3. **Message infrastructure: MongoDB only (MVP)** — messages collection, findOneAndUpdate for atomic claim, polling (5-second adaptive). No separate broker. Scale path: Change Streams → Redis Pub/Sub → RabbitMQ (additive).
4. **Message schema** — includes correlation_id, causation_id, depth (cascade tracking), status, claimed_by, visibility_timeout, attempt_count, max_attempts, priority, due_by, context, changes. "Traceability from day one — impossible to retrofit."
5. **Visibility timeout** — 5 min for associates, 24 hours for humans. Stuck message recovery.
6. **Cascade depth tracking + circuit breaker** — default max 10 depth.
7. **Idempotent message processing** — handlers must be idempotent; ProcessedLog pattern.
8. **Routing rules as separate entity** — configurable per org via CLI, NOT hardcoded on entity classes.
9. **Selective message emission** — state transitions / @exposed / create/delete only.
10. **MessageBus abstraction (Protocol)** — MongoDB impl now, swappable later.

Also decided:
- **Context pre-loading** on messages (attached entity graph, configurable depth).
- **Personal AI assistant per human actor** — same role permissions, same queue.
- **UI auto-generated from role** — role defines what entities + queue; UI follows.
- **Build entities by hand first, extract framework.** Inverts the original plan.

**Real-time unification (this is notable):**
- "Real-time and async use the same associate pattern."
- Non-blocking entity saves during voice calls (`asyncio.create_task`).
- Interaction entity (normal entity) tracks conversation.
- Channel adapters provide I/O; associate doesn't know which channel.
- Rejected: separate Interaction Host, Message suppression during interactions, Entity Sync Worker, Redis Streams coordination, "system of engagement" vs "system of record."

### From `2026-04-02-design-layer-4-integrations.md`:
- **Integration as entity** (status state machine, CLI-configurable). Later elevated to primitive in 2026-04-10-integration-as-primitive.md.
- **Adapter pattern** = abstract per system type, implemented per provider. Unchanged in final architecture.
- **ADAPTER_REGISTRY** — provider name → adapter class. Later keyed by `provider:version` (2026-04-10).
- **Web operators reuse associate harness** — browser automation added to sandbox. Same deep-agent architecture.
- **Wrap existing implementations as adapters** — no rebuild, standard interface on current code.
- **Mapping functions per provider** — code translation between external format and OS entity fields. Written once per provider.
- **Entity ops don't know the method** — API vs web operator vs email vs file, adapter handles it.

### From `2026-04-02-design-layer-5-experience.md`:
- **One source of truth** — UI uses same API as CLI and associates.
- **ViewConfig as CLI-configurable entity** (later NOT implemented — superseded by auto-generation from entity definitions only; per white paper, "no custom UI code per entity or per org" and ViewConfig deferred as DashboardConfig/AlertConfig/Widget post-MVP).
- **Real-time via RabbitMQ** (this stage) — later REPLACED by MongoDB Change Streams per 2026-04-11-base-ui-operational-surface.md.
- **Draft entity for HITL** — no separate HITL mechanism.
- **Auto-generated admin UI** — later formalized as the Base UI (2026-04-11-base-ui-operational-surface.md).
- **Deployment entity for consumer surfaces** — retained in the final architecture.

### From `2026-04-02-implementation-plan.md`:
- **Phase 0 precedes all code** — conventions must exist before 10+ parallel sessions write code.
- **Mixin-based Entity** (StateMachineMixin, EventMixin, PermissionsMixin, AutoRegisterMixin) — later SUPERSEDED by 2026-04-02-core-primitives-architecture.md ("One Entity class with uniform capabilities, configuration-driven activation. No mixins.").
- **Phase 2 parallel sessions** by sub-domain (A-I: Core Insurance, Risk & Parties, Submission & Quoting, Policy Lifecycle, Financial, Distribution & Delivery, Platform-Agents, Platform-Operations, Reference Tables).
- **RabbitMQ event bus** — later superseded by MongoDB messages.
- **Phase 4 = Indemn runs on OS** — dog-fooding.
- **Phase 5 = first external customer** — the Series A proof.

**Phase numbering evolution:**
- This artifact: 6 phases (0-5).
- Final white paper: 8 phases (0-7).
- Final phase numbering differs because the architecture evolved:
  - Phase 2 (this artifact = entity vertical) → split into Phase 1 (kernel framework) + Phase 6 (dog-fooding) in the final.
  - Phase 3 (this artifact = associates + integrations) → split into Phase 2 (associate execution) + Phase 3 (integrations) in the final.
  - Phase 4 (this artifact = Indemn on OS) → became Phase 6 (dog-fooding) in the final.
  - Phase 5 (this artifact = first external customer) → became Phase 7 in the final.
  - NEW in final: Phase 4 (Base UI), Phase 5 (Real-Time — harness pattern).

### From `2026-04-03-message-actor-architecture-research.md`:
- **Outbox pattern** for entity save + message creation — RETAINED as principle (becomes save_tracked()).
- **Selective emission** (state transitions + @exposed + create/delete only) — RETAINED.
- **Correlation IDs** for cascade tracing — RETAINED.
- **Cascade depth limit** (default 10) — RETAINED.
- **Idempotent processing** — RETAINED (visibility timeout + max attempts).
- **Work queue as MongoDB collection** — RETAINED (message_queue + message_log in final).
- **findOneAndUpdate for atomic claim** — RETAINED.
- **RabbitMQ as event bus (hybrid)** — LATER REJECTED in favor of MongoDB-only per 2026-04-02-core-primitives-architecture.md + subsequent artifacts.
- **Context enrichment per role** — RETAINED as "scoped watches with field_path/active_context" (2026-04-10).

### From `2026-04-07-challenge-developer-experience.md`:
This pressure test identified concerns that were addressed in later artifacts:
- Routing rule format → watches (later in 2026-04-10-realtime-architecture-design.md)
- Observability → OTEL + correlation IDs + changes collection (2026-04-09-data-architecture-solutions.md + white paper)
- Entity definition location → JSON in MongoDB, dynamic classes (2026-04-09-data-architecture-everything-is-data.md)
- Testing strategy → Phase 0 unit/integration/e2e layering

No new architectural decision introduced HERE — this is a challenge, later addressed.

### From `2026-04-07-challenge-distributed-systems.md`:
- **10 priority-ordered recommendations** (1-6 for initial implementation, 7-10 deferred):
  1. Transactional entity+message writes
  2. Visibility timeout
  3. Cascade depth + circuit breaker
  4. Idempotent handlers
  5. Correlation/causation IDs + depth
  6. Optimistic concurrency (version field)
  7. Routing rule caching
  8. Hot/cold message split
  9. MessageBus abstraction interface
  10. Change streams (replace polling)
- **Hot/cold message split**: `message_queue` (pending + processing) and `message_archive` (completed + failed). Move on completion (txn).
- **MessageBus abstraction interface** for swappable backend (MongoDB → RabbitMQ later).
- **Start with polling, migrate to Change Streams** when needed.
- **Don't shard MongoDB** for MVP (insurance volumes don't justify it; design data model with org_id prefix for future sharding).

### From `2026-04-07-challenge-insurance-practitioner.md`:
The response's architectural implications (inferred from the prompt + pressure test category):
- **Insurance domain is deep**. Platform must support per-carrier/per-state/per-product rules without coding each specially.
- **Party/Role model** needs to support many-to-many with roles varying by context (producer for one carrier, retail customer for another).
- **Entity state machines must allow re-entry / retry** (cancellation→reinstatement, quote→expired→re-quoted).
- **Compliance audit trail** is not optional — every change needs who, when, why, old-value, new-value.
- **The kernel-vs-domain separation** (later formalized) is the right answer: insurance-specific rules go in per-org configuration, not kernel code.

### From `2026-04-07-challenge-mvp-buildability.md`:
- **Ship smallest thing that proves thesis** — not smallest architecture, smallest EXPERIENCE.
- **Reduce from 44 entities to 5 (or 7) for MVP.**
- **Hand-build the first entities, extract the generator later.**
- **Don't build framework before knowing what pattern to generate** (auto-generators are traps before they're force multipliers).
- **Don't put LLM in entity write path** (same as distributed-systems pressure test).
- **Find one friendly agency for realistic dog-fooding** (not use our own CRM).

### From `2026-04-07-challenge-realtime-systems.md`:
- **Two-mode split is architecturally dangerous** — need unified model where real-time IS queue-backed (direct invocation claims the queue entry, same as any actor).
- **Recommends NOT putting LLM in entity write path** — entity changes don't trigger synchronous LLM as side effect. Enqueue instead.
- **State machine transitions must be atomic** (conditional update filter on status + version).
- **Saga pattern for multi-entity operations** (MongoDB 4.0+ transactions or compensating transactions).
- **Actor-entity affinity during interactions** (soft-lock priority on entities the associate is actively using).

### From `2026-04-08-actor-references-and-targeting.md`:
- **Watch evaluation must be entity-local** (no cross-entity reads during watch eval).
- **Rejected kernel-level actor-specific targeting** — keep kernel simple.
- **Domain entity fields can hold actor references** — no special kernel treatment.
- **Message schema has `target_actor_id` field** (optional, not populated initially). At scale, populated from context for pre-targeted routing.
- **Queue query semantics**: target_role match + (target_actor_id null OR target_actor_id me).

### From `2026-04-08-actor-spectrum-and-primitives.md`:
- **One actor framework for all execution modes**. No separate deterministic vs reasoning infrastructure.
- **Scheduled tasks are associates with time-based triggers** (no separate primitive).
- **Queue is universal. CLI is universal. Messaging is universal.**
- **"I don't want to waste LLM processing on things that can be done deterministically" — the `--auto` pattern's motivation.**
- **Integration collapsed into Entity** (later REVERSED — Integration is primitive #6).

### From `2026-04-08-entry-points-and-triggers.md`:
- **Actor model is CLEAN**: actors don't know about WebSockets/SIP/Twilio. They know entities + CLI. Channel infrastructure creates entities and provides I/O. Actors read/write entities. Channel translates.
- **One uniform path for all external events**: entry point → entity change → watch → message → actor (or schedule → actor).
- **Direct invocation is a first-class trigger**, not a backdoor. Used for real-time (voice/chat) to avoid queue polling latency, and for testing/debugging.
- **Schedule trigger** creates queue item (per round 1 architecture ironing) so all work is visible in queue. Actor's watch does NOT need a schedule entry; the kernel scheduler directly creates queue items for scheduled associates.

### From `2026-04-08-kernel-vs-domain.md`:
- **Kernel vs. domain line is about universality**: kernel = what's true for every system; domain = per-system data.
- **Actor roles stack in an org**: "An actor with multiple roles sees the union of all their roles' watches in their queue."
- **Assignment replaces per-entity assignment fields** (`assigned_to`, `underwriter`, `reviewer` field patterns) with one universal OS capability.
- **Actor types declared**: human, associate. (Later white paper adds the "associate is just an actor" framing stronger — the type is more about identity lifecycle than behavior.)
- **CLI-level primitives** for all kernel operations — `indemn role`, `indemn actor`, `indemn assign`, `indemn assignment`.

### From `2026-04-08-pressure-test-findings.md`:
- **Four primitives are locked** (Entity, Message, Actor, Role). Concept count is right (6 to start + 4 more for depth).
- **Direct invocation is a first-class trigger type** (not just a backdoor for real-time — the documented pattern).
- **Message storage is two collections from day 1** — split is architectural, not a later optimization.
- **OTEL is not a feature — it IS the observability layer.** Every span, every primitive touch.
- **Skills CAN be deterministic/reasoning/hybrid** but the FORMAT is open at this point.
- **Testing + debugging CLI is a day-one deliverable** — not an after-thought.
- **Provider versioning of adapters is REQUIRED for MVP** — external APIs break.

### From `2026-04-08-primitives-resolved.md`:
- **4 primitives here**: Entity, Message, Actor, Role. (Organization, Assignment added in kernel-vs-domain the same day; Integration promoted back to primitive #6 two days later.)
- **Execution mode is an actor property, NOT a separate kernel concept.** "Signal in, CLI commands out" — OS is uniform.
- **No routing rules, no connection layer, no subscription layer.** Role watches are sufficient + complete (one mechanism handles sequential pipeline, conditional routing, fan-out, specific conditions).
- **Per-org watch configuration via CLI** — `indemn role add-watch underwriter --entity Assessment --on created --when "needs_review=true"`.
- **Individual actor filtering is UI-level, not a watch.** All actors with same role get same messages.
- **Integration is encapsulated inside entity implementations.** (Later superseded.)

### From `2026-04-08-session-3-checkpoint.md`:
- **2 implementation primitives**: Entity + Message. Everything composes.
- **4 conceptual primitives**: Entity + Message + Actor + Role (pre-Integration, pre-Organization as primitive).
- **Uniform Entity class** — no mixins.
- **Same associate pattern for async and real-time** — channels are I/O.
- **Entity methods are deterministic** — LLM reasoning via associates.
- **Adapters are actors** — receive messages about entity changes, sync to external.
- **MessageBus abstraction** for swappable backend (RabbitMQ later).

### From `2026-04-09-architecture-ironing-round-2.md`:
- **Unified capability/method concept**: user-facing abstraction is "entity methods"; kernel provides a library of reusable methods that can be activated on any entity type.
- **Shared condition evaluator** across watches + rules. Single implementation, single trace format.
- **Entity is source of truth, messages are references** (not snapshots). Small perf cost (load entity per message), big consistency benefit (no stale copies).
- **Three data stores each optimized for their query pattern** — no redundancy despite capturing similar events.

### From `2026-04-09-architecture-ironing-round-3.md`:
- **Emission model locked**: entity saves emit events at @exposed method completion; not mid-method, not per-field. This is the selective-emission discipline.
- **Watch evaluation happens against full change metadata**, not separate sub-events.
- **Outbox eliminated (Round 1 + confirmed here).** Write to message_queue inside entity transaction. No separate outbox collection.
- **Queue Processor is THE kernel process** that bridges queue → Temporal. Named and defined.
- **Claiming ≠ assignment.** Different concepts. Kernel supports both; skill decides when to combine.
- **Bootstrap entities are "full entities with 2 safety rules"** — not specially-structured; just special on cache + cascade.
- **Schema changes are explicit CLI operations** (`indemn entity modify`), not mid-flight schema inference.
- **Condition evaluator is ONE evaluator, ONE format.** Shared between rules and watches.
- **Unified versioning + audit** — the changes collection is dual-purpose. Elegant consolidation.

### From `2026-04-09-architecture-ironing.md`:
- **Generic single workflow** for associate processing (no per-associate workflow code).
- **Outbox eliminated** — entity save + watches + messages = one MongoDB transaction.
- **Schedules → queue items** (synthetic messages with `event_type: scheduled_task`).
- **Real-time = queue + direct invocation in parallel** (direct invocation claims the queue entry).
- **Bootstrap entities**: Organization, Actor, Role are entities that the kernel knows specially. Later: 7 kernel entities (add Integration, Attention, Runtime, Session).
- **Entity creation via CLI generates Python class file** — later superseded by "entity definitions live in MongoDB + dynamic class creation at startup" (2026-04-09-data-architecture-everything-is-data.md).

### From `2026-04-09-capabilities-model-review-findings.md`:
- **JSON for conditions** with all/any/not combinators + standard operators.
- **Lookups as separate concept** from rules. Bulk-importable, maintained by non-technical users.
- **Veto rules** override positive matches + force reasoning.
- **Rule groups with lifecycle** (Draft/Active/Archived).
- **Evaluation traces in data, not logs** — queryable.

### From `2026-04-09-consolidated-architecture.md`:
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

### From `2026-04-09-data-architecture-review-findings.md`:
- **OrgScopedCollection wrapper** = defense-in-depth for multi-tenancy (resolved in data-architecture-solutions).
- **AWS Secrets Manager** (not MongoDB) for credentials with `secret_ref` on Integration.
- **Hash chain + insert-only changes collection** = tamper-evident audit.
- **Separate Atlas clusters** for prod vs. non-prod (already in place per infrastructure artifact).
- **Schema migration as first-class capability** (resolved in data-architecture-solutions #12).
- **Raw Motor for dynamic domain entities; Beanie for kernel entities** — this became the dual base class split (`DomainBaseEntity` + `KernelBaseEntity`) surfaced in shakeout Finding 4.

### From `2026-04-09-data-architecture-solutions.md`:
- **Single MongoDB access pattern (OrgScopedCollection)** becomes a kernel invariant. All entity CRUD goes through it. Violation is a bug at kernel level.
- **Credentials never flow through entity-framework layers** — kernel adapter code resolves them separately, on demand.
- **Schema changes are an administrative operation**; rolling restart is acceptable (seconds).
- **Rule actions are bounded** — no side-effects beyond field writes through the set-fields action; no state transitions.
- **Tamper evidence via MongoDB permissions + hash chain** — dual defense-in-depth.
- **Accept dynamic-class ergonomic tradeoffs** (no IDE autocomplete) — CLI/skills are the interface, not in-code instantiation.

### From `2026-04-09-session-4-checkpoint.md`:
(from this checkpoint)

5 kernel primitives at this point: Entity, Message, Actor, Role, Organization. (Integration promoted to primitive #6 in session 5.)

22 architectural decisions + 6 security decisions + 5 infrastructure decisions. Key:
- Watches as wiring
- One condition language (JSON)
- Kernel capabilities = entity methods (unified)
- Skills are markdown
- Everything is data
- Temporal for associate execution (NOT human queues)
- Unified MongoDB queue
- OTEL baked in
- Changes collection + hash chain
- Assignment is domain concern
- Schema migration first-class
- Rolling restart on entity type changes (Beanie for all)
- Seed YAML + template org
- Capability schema versioning
- Scheduled = queue items
- Real-time = queue entry + direct invocation in parallel
- Generic Temporal workflow (claim → process → complete)
- OrgScopedCollection
- AWS Secrets Manager for credentials
- Skill content hashing + version approval
- Rule validation at creation (state fields excluded from set-fields)
- Sandbox contract (Daytona)

### From `2026-04-09-temporal-integration-architecture.md`:
- **Multi-entity atomicity via saga pattern**: workflow wraps multiple activities; if worker crashes, Temporal replays and skips completed activities. "No orphaned state."
- **Workflow versioning** handled by Temporal's built-in mechanism — in-flight workflows continue on old workers; new workflows route to new workers.
- **Rules are configuration data** — next workflow execution picks up new rules; in-flight workflows continue with evaluated results stored in Temporal event history.
- **Workflows per Temporal queue** — not explicitly specified here; left implicit.
- **CLI for Temporal ops**: `indemn schedule create --workflow ... --cron ...`

### From `2026-04-09-unified-queue-temporal-execution.md`:
- **Queue and execution are SEPARATE concerns.** MongoDB is queue infrastructure; Temporal is durable-execution infrastructure for associates. They coordinate via the claim primitive.
- **One message_queue schema for all actors.** Fields: org_id, entity_type, entity_id, event, target_role, status, claimed_by, claimed_at, visibility_timeout, priority, context (enriched entity data), correlation_id, causation_id, depth, created_at. (This schema broadly matches what ended up in `kernel/message/schema.py`.)
- **Humans interact via UI + CLI against MongoDB** directly. Associates interact via Temporal workflows.
- **Watch evaluation lives in the outbox poller** (or optimistically in the save path per the closing note).
- **Temporal Cloud is the execution host** ($100/mo).

### From `2026-04-10-crm-retrace.md`:
- **Kernel is domain-agnostic**: validated across 3 shape dimensions — B2B insurance pipeline, consumer real-time insurance, generic B2B intelligence. "Every row is different. The kernel is the same. That's the story."
- **Owner-bound associate pattern**: `owner_actor_id` field on Actor (or specifically on Associate subtype). One-field kernel addition + resolver check + audit logging.
- **Consent and lifecycle for owner-bound associates**:
  - Consent required at creation (recorded in changes)
  - Revocable by owner via `indemn associate remove-owner`
  - Transferable with new owner's consent
  - On owner deprovisioning: paused; platform admin reviews
- **Privacy as Integration-level policy, not kernel rule**: Integration declares `content_visibility`. Kernel enforces via S3 path structure + IAM.
- **Entity methods can be read-only aggregations** (query capabilities). Doesn't need new primitive; just naming.
- **Scope: actor_context confirmed as cross-cutting need** (also surfaced in EventGuard).

### From `2026-04-10-eventguard-retrace.md`:
- **Real-time entry point pattern**: channel infrastructure accepts connection → creates Interaction entity → Interaction:created event → watch matches → direct invocation claims queue entry (parallel path) → Temporal workflow starts → workflow holds WebSocket as I/O.
- **Outbound + inbound Integration methods** unified under one Adapter interface (fetch/send/charge + validate_webhook/parse_webhook + auth_initiate).
- **Webhook handler is infrastructure, not an actor** — an entry point. Kernel applies resulting entity ops through entity methods (not raw).
- **WebhookResult** = structured `{entity_type, lookup_by, lookup_value, operation, params}`.
- **Actor-context watch scoping** = new kernel mechanism. Extends watches with scope qualifier referencing claiming actor's current working context.
- **Temporal signals to running workflows** = the delivery mechanism for `actor_context` scoped events when target actor's workflow is active.
- **Bulk operations as first-class**: `indemn deployment bulk-create --from-csv` → batches of ~50 per txn → coalesced events for ops visibility.
- **Per-venue branding via Deployment entity config** — no per-venue associate proliferation.

### From `2026-04-10-gic-retrace-full-kernel.md`:
- **6 primitives validated** for B2B insurance pipeline. No primitive changes.
- **Watches as wiring survives the pressure test**: zero orchestration code.
- **Unified queue works for mixed human+associate roles**: rollout is a role assignment change, not infrastructure.
- **`--auto` pattern pays off**: cost scales with edge case complexity, not volume.
- **Temporal wraps each associate's execution** for durability.
- **Scheduled work = synthetic queue items targeting a role** (minor aesthetic vs. real events; acceptable).

### From `2026-04-10-session-5-checkpoint.md`:
Most consequential session 5 decisions:
- **Integration = primitive #6** (elevated from entity).
- **Attention + Runtime as bootstrap entities.**
- **Harness pattern formalized**: deployable images per kind+framework, using CLI via subprocess.
- **Three harness images**: voice-deepagents + chat-deepagents + async-deepagents.
- **CLI ≠ universal interface**; universal is entity framework's auto-generated surface (CLI + API both).

### From `2026-04-13-documentation-sweep.md`:
- **Inbound webhook is an entry point, not an actor.** Kernel generic endpoint. Adapter-layer validation and parsing. Entity methods handle actual mutations.
- **Two kinds of "people" in the model**: Internal Actors (authenticated, roled, queued, CLI-empowered) and External Entities (domain data, subjects of work).
- **Method activation configs on entity definition vs. Lookups as shared data** — clean separation.
- **Owner-bound associates** get delegated credential access through owner's Integrations + two distinct auth patterns (session-inherited vs. service-token).
- **Content visibility as Integration field** (not per-entity, not per-message). Default per ownership.
- **S3 path structure encodes visibility** — paths are infrastructure, access control is IAM.
- **Explicit-share escape hatch** for per-instance "share this one email thread with the team."

### From `2026-04-13-infrastructure-and-deployment.md`:
- **Modular monolith**: one codebase, multiple entry points, one Docker image for kernel. Clear internal boundaries.
- **Trust boundary is enforced by deployment** (only kernel processes have MongoDB credentials via Railway env vars).
- **CLI unification eliminates "works locally but breaks in prod" bugs**: no direct-DB mode anywhere.
- **Optimistic dispatch simplifies the happy path** (no Temporal in the save txn; just HTTP fire-and-forget after commit).
- **Sweep backstop handles failure cases** without coupling entity save to Temporal availability.
- **Real-time harnesses from day one** (not deferred).

### From `2026-04-13-remaining-gap-sessions.md`:
- **Harnesses are separate Docker images** in `harnesses/` dir. Explicitly listed (voice-deepagents + chat-deepagents; async-deepagents not mentioned here either).
- **MongoDB Atlas is the only SPOF**.
- **Multi-provider LLM coexistence** as a resilience feature.
- **Tier 2 is the primary onboarding path** via FDE + platform admin session.
- **Current system and OS are fully separated** — no bridge.
- **8-step domain modeling process** standardized from retraces.
- **Real-time implementation deferred to per-component spec** (not in white paper).

### From `2026-04-13-session-6-checkpoint.md`:
- **6 structural primitives** (confirmed, no changes from session 5): Entity, Message, Actor, Role, Organization, Integration.
- **7 kernel entities** (renamed from "bootstrap"): Organization, Actor, Role, Integration, Attention, Runtime, Session (Session added in authentication-design).
- **Watch coalescing REMOVED from kernel** — UI rendering concern. This is the biggest simplification-pass outcome: no `coalesce` field on watches, no `batch_id` on messages, no grouping logic in emission path.
- **Rule evaluation traces moved to changes collection metadata** — no separate trace collection.
- **WebAuthn + per-operation MFA re-verification deferred** post-MVP.

### From `2026-04-14-impl-spec-gaps.md`:
Notable gap-resolution decisions:
- **EntityDefinition scope**: resolved as per-org with `org_id` field (Option A) — necessary for env-as-org clone.
- **CLI always in API mode** (not direct MongoDB).
- **OrgScopedCollection + contextvars**: organizational scoping via Python `contextvars` set by auth middleware, read by entity operations.
- **Temporal TracingInterceptor for OTEL** — required.
- **Retry policies per activity, not one-size-fits-all** — G-90.
- **Multi-entry-point Dockerfile for kernel image** — G-88.
- **Graceful shutdown for all services** — G-84.

### From `2026-04-14-impl-spec-phase-0-1-addendum.md`:
All decisions here SURVIVE into consolidated spec.
- Attention lifecycle is `active → expired/closed` (transitions from session 5).
- Runtime lifecycle from session 5.
- Session from authentication-design.

### From `2026-04-14-impl-spec-phase-0-1.md`:
All decisions here SURVIVE into the consolidated spec, with additions from the addendum (Attention, Runtime, Session kernel entity full specs) and gap resolutions (90 items: schema migration, CLI auto-registration, org clone/diff/deploy, etc.).

### From `2026-04-14-impl-spec-phase-2-3.md`:
- **Temporal integration patterns** (from session 4 designs).
- **Generic single workflow** for all associate processing.
- **Kernel capabilities via `--auto` pattern** (per session 4).
- **Adapter pattern with `provider:version` registry** (from session 5 integration-as-primitive).
- **Webhook endpoint** at `/webhook/{provider}/{integration_id}` (from documentation-sweep item 4).

### From `2026-04-14-impl-spec-phase-4-5.md`:
- **React + Vite** for UI, hand-built pattern + auto-generation from entity metadata.
- **Full authentication end-to-end** per authentication-design.
- **Assistant as kernel endpoint** (Finding 0b entry point).
- **Voice harness as example code only** in Phase 5 §5.3.
- **Chat + async harnesses MISSING from spec.**

### From `2026-04-14-impl-spec-phase-6-7.md`:
- **Phase 6 and 7 are operational, not code phases.**
- **CRM and GIC retrace artifacts are the blueprints** — Phase 6-7 implements them on the kernel.
- **Domain modeling process is standardized** (entities → roles → rules → skills → integrations → test → deploy+tune).

### From `2026-04-14-impl-spec-verification-report.md`:
- **Per-org EntityDefinition**: `org_id` on EntityDefinition; `init_database` merges definitions across orgs for class creation. Rejected "system-scoped definitions" in favor of clone-compatible per-org.
- **Kernel entity namespace is reserved**: `init_database` guards against domain entity names matching kernel entity names.
- **CLI auto-registered from entity metadata** via same pattern as API registration.
- **Org clone/diff/deploy are Phase 1 capabilities**, not deferred to Phase 6.
- **`save_tracked` returns created_messages** for optimistic dispatch to consume.

### From `2026-04-15-shakeout-session-findings.md`:
(made during shakeout)

1. **Separate collections for kernel entities** (removed `is_root=True`) — matches spec, eliminates bug class.
2. **Explicit `to_dict()` at each route** (Option A serialization) — no middleware, no custom Pydantic types.
3. **JSON as default CLI format** — "agent-first CLI, agents need complete structured data."
4. **Watch cache invalidation in `save_tracked()`** — the only place that guarantees all Role saves are covered.
5. **Runtime entity registration** — `register_domain_entity()` called inline on definition create + capability enable.

### From `2026-04-15-spec-vs-implementation-audit.md`:
(from this audit)

- **The single biggest user-visible gap is D-03 (assistant no tools)** — described in spec as "at forefront" primary human-to-system interface; implemented as text-only chatbot.
- **D-02 is the #1 invariant violation** — atomicity of entity write + changes + messages is the core system invariant. The shakeout fix regressed it.
- **D-01 (dual base class) is correct engineering** — the fix for Beanie+dynamic-model issues is the right approach. Spec needs to document it.

### From `architecture.md`:
- **AI agents are a CHANNEL, not a separate system** — foundational.
- **Object-oriented system modeling insurance business**.
- **CLI-first everything**: CLI stands up customer, deploys associates, configures products, runs evaluations.
- **Three tiers of platform usage**: Managed service / Self-service workflows / Build on the platform.
- **5 universal findings**:
  1. Separate platform from domain
  2. Policy lifecycle is backbone
  3. Configuration ≠ transactions
  4. "Customer" is wrong — real entities are Insured, RetailAgent, Agency, Carrier, DistributionPartner
  5. Financial layer is severely underdeveloped.
- **Not a migration — a new platform built alongside the current system.**

### From `business.md`:
Non-architectural — business + strategy. Key implications for the OS:
- **OS must serve all three tiers** (middle market, enterprise, product partnerships).
- **OS must be the "factory that builds them"** (Gastown).
- **Platform IS the moat** — compounding across deployments.
- **GIC + INSURICA + JM (top 3 customers) prove 80% of product thesis** → the OS must handle all three shapes of workload (B2B pipeline, renewals, embedded consumer).
- **Agent-accessible platform** — deep implications for the harness pattern (per Finding 0).

### From `craigs-vision.md`:
**Craig's vision is the architectural north star.** It does not specify implementation layers — it specifies the principles those layers must satisfy:

1. **Entity-first**: everything in the insurance business is an entity with schema + state machine + API.
2. **AI-native from the ground up**: not bolted on. CLI / API / skills designed for agent consumption.
3. **AI agents are a channel**, not a separate system. This has direct implications for the harness pattern — agents are clients into the OS, not something the OS embeds/runs.
4. **Compatible + replacement**: must integrate with existing insurance systems AND be capable of replacing them.
5. **Compounding advantage**: once entities + skills + agents are all first-class, building new capabilities compounds. Platform effect.
6. **Associates = processing nodes operating on the platform**, not standalone products.
7. **The CLI pattern**: agents creating/evaluating/modifying agents via CLI is the template. The OS CLI IS the platform's agent interface.

### From `product.md`:
- **Platform is ONE system, configured per customer/persona**. Agencies/Carriers/Distribution are configurations, not separate architectures.
- **All engines share ONE brain** (knowledge base) → kernel's skill + capability model.
- **Associates = configured compositions** → per-org configuration in rules + lookups + skills.
- **7 domain objects + 6 capabilities = 84% of pricing matrix** → if kernel supports these 7 + 6, most of the product matrix is buildable.
- **Workflow templates** = composed capability sequences = skills that orchestrate CLI invocations.

### From `strategy.md`:
Non-architectural. Strategic implications:
- **Platform must coexist with current customer delivery** — additive, not disruptive.
- **Current implementations inform platform design.**
- **Dog-food Indemn CRM first (Phase 6)** before first external customer (Phase 7).
- **Ryan → Dhruv → George → Kyle/Cam** engagement sequence.

### From `2026-03-25-the-vision-v1.md`:
Vision-level, not architecture. But establishes the principles:
- **CLI-first, Agent-first**.
- **Object-oriented insurance system.**
- **Associates = configured compositions.**
- **Platform is the moat.**

### From `2026-03-25-the-vision.md`:
- **Factory metaphor for platform**: models operations once, configures per customer.
- **Configuration, not custom code**: 48 associates = configurations.
- **ONE platform for three target groups** (Agencies/Carriers/Distribution).
- **Incremental build**: 3-phase domain model (initial 25 entities → financial + distribution → authority + compliance + claims).


## Open Questions / Ambiguities

Things flagged as unresolved across the source artifacts.


### From `2026-04-13-white-paper.md`:
or Ambiguities

- **The white paper does not resolve the ambiguity** about whether the agent execution loop (skill interpreter, LLM tool-use loop, execute_command) runs inside the Temporal Worker process (kernel-side, with db access) OR inside a Harness process (outside trust boundary, CLI-only). Both readings are supported by the text:
  - "Temporal Worker. Executes associate workflows — the generic claim-process-complete cycle, bulk operations, platform deployments" → reads as kernel-side execution
  - "Each harness is a thin piece of glue code — roughly 60 lines — that loads the associate's configuration at session start and uses the CLI for all OS interactions" → reads as agent code in harness
  - This is the exact ambiguity that Finding 0 traces to. The source design artifact (2026-04-10-realtime-architecture-design.md) resolves it; the white paper summary does not.
- "Configurable widgets and custom dashboards may be added in the future when forcing functions demand it" — deferred.
- "Active alerting is deferred. The mechanism will likely be watches on kernel entities with actions that invoke notification integrations."
- Fresh MFA re-verification "deferred beyond MVP, where session-level MFA verification is sufficient."
- Tier 3 billing, plan selection, team invitation "deferred beyond MVP."
- Content visibility rules for personal integrations — default stated, but configurable per integration with no schema committed.

### From `2026-04-10-realtime-architecture-design.md`:
or Ambiguities

The artifact itself lists deferred items (Part 10):
- Bulk operations pattern (resolved by 2026-04-10-bulk-operations-pattern.md)
- Inbound webhook dispatch documentation (Integration artifact update)
- Pipeline dashboard layer
- Queue health tooling
- Authentication (resolved by 2026-04-11-authentication-design.md)
- Content visibility scoping
- Voice handoff UX specifics
- Runtime auto-deployment (what happens when work comes in for a Runtime with no instances)
- Runtime health-based dispatch (round-robin vs smart load-aware)
- Runtime migration across framework versions

The artifact is UNAMBIGUOUS on the key architectural-layer claim: **agent execution (LLM loop, skill interpreter, tool-use) lives in harness images outside the kernel**. The harness uses the CLI; it is not part of the kernel's trust boundary.

**This is the design statement that the current code violates (per Finding 0).** The kernel currently has the full agent loop inside `kernel/temporal/activities.py::process_with_associate`, running in the kernel's Temporal Worker — exactly what this artifact says should NOT happen.

### From `2026-04-10-integration-as-primitive.md`:
or Ambiguities

From the artifact itself (Open Questions section):
- **Adapter contribution path for Tier 3**: when a Tier 3 developer needs to connect to a provider the OS doesn't support yet, what's the path? Contributing a new adapter to the kernel (platform PR) is the obvious answer. Whether there's a **managed-extension mechanism (custom adapter loaded at runtime)** is an open design question. Deferred until real Tier 3 use case.
  - **This is the Pass 2 question for integration adapters**: Are adapters in the kernel image (correct per this artifact) or should they be plugin-loadable? The artifact explicitly leaves this open. Current implementation has adapters in the kernel (per Finding-0 audit). This aligns with the design's default; the open question is only about future Tier 3 extension.
- **Consent flows for OAuth providers**: how the `indemn integration configure` CLI launches and captures browser consent in headless context. Likely a short-lived web endpoint. Unresolved.
- **Integration dependencies**: does a domain entity declare which Integrations it depends on, or does it discover them at runtime? Runtime discovery via `system_type` lookup is the MVP; explicit dependencies could be added later.

No architectural-layer deviation likely here — the design is consistent: Integration record in DB, adapters in kernel code. Both align with what Pass 2 audit should expect to find implemented.

### From `2026-03-30-design-layer-3-associate-system.md`:
or Ambiguities

- **Sandbox provider**: Daytona is explicitly "being considered" but not locked. Line 55-62.
- **Workflow runner**: explicitly deferred. "Start with a custom runner for MVP. Migrate to Temporal or blueprint engine when reliability requirements demand it." Line 329.
- **Relationship between Workflow entity and the associate's deep agent loop**: The Workflow entity has step types including `associate` (invoke an associate with an objective). But this artifact doesn't resolve how the workflow runner interacts with the sandbox-based associate execution. This was resolved later in the realtime architecture design (Runtime entity + harness pattern + Temporal task queue for async runtimes).
- **No explicit kernel/image boundary stated here.** The boundary is implied by the sandbox (agent lives in sandbox), but the formal "harnesses are separate deployable images outside the kernel's trust boundary" language came in 2026-04-10-realtime-architecture-design.md.

**Pass 2 check on sandbox**: The comprehensive audit's section 3a asks: "Is sandbox execution implemented? Per design, sandboxes wrap agent execution. With agent execution in-kernel, where would sandboxes go?" Per this artifact + the realtime architecture design, sandboxes wrap agent execution in the harness. The current kernel code (per Finding 0) has no harness, so sandbox execution is also not present — the agent loop in `kernel/temporal/activities.py` does not run in Daytona or any sandbox. This is a **secondary consequence of Finding 0**.

### From `2026-04-09-entity-capabilities-and-skill-model.md`:
or Ambiguities

- **Where the skill interpreter/agent runs is not explicitly stated here.** It's implicit that it's a separate thing calling the CLI, but the artifact doesn't name the location. Resolved by the realtime architecture design.
- **Rule engine location**: not explicit. "Kernel evaluates rules" language — so rule engine is in the kernel. Confirmed by Pass 1 audit which verified rule engine in `kernel/rule/engine.py`.
- **Skill schema and integrity**: this artifact says skills are markdown. Doesn't detail tamper-evidence or version approval (those are in the white paper + base UI design and auth design).

**Pass 2 check on skill execution location**: Per this artifact and the realtime architecture design, the skill interpreter (deterministic interpreter or LLM) runs in the harness (outside kernel). The current code has the skill interpreter inside `kernel/temporal/activities.py::_execute_reasoning` (LLM path) and corresponding deterministic path also in the kernel. **Skill execution location is wrong in the current code — it's a secondary consequence of Finding 0.**

**Pass 2 check on capability library**: This artifact says capabilities are Python code in the kernel — which aligns with the current implementation (capabilities in `kernel/capability/`). No layer deviation expected here.

**Pass 2 check on skill tamper-evidence**: Skills are stored in DB, versioned through changes collection, updatable through CLI. Per the white paper § Security, "Skills are tamper-evident. Content hashes are computed on creation and verified on load." This is a kernel-side function (hash check at load time). Current code has `kernel/skill/integrity.py` — needs verification that this integrity is actually invoked when skills are loaded by the (currently kernel-side) agent execution.

### From `2026-04-11-authentication-design.md`:
or Ambiguities

From the artifact's own "Open Follow-Ups" section:
- JWT signing key rotation schedule (operational, not architectural)
- Per-operation sensitivity marking (which ops get `requires_fresh_mfa` is domain, not kernel)
- Platform admin role granularity within `_platform` org
- Cross-session coordination for revocation cache at scale (Redis Pub/Sub possibility)
- Session entity archival strategy (default 7-day TTL-delete after expiration)

**Pass 2 observations:**
- Authentication mechanics are all kernel-side per design, which matches expected implementation. Current code has `kernel/auth/*` which aligns.
- The default assistant auth pattern (user session inheritance) does assume a chat-harness model: "Its harness authenticates using the user's session JWT (injected at session start)." If there is no chat harness implemented (Finding 0), the default assistant auth pattern is broken in spirit — the current `kernel/api/assistant.py` is NOT a harness, it's an endpoint. It streams text with the user's session but does NOT follow the harness pattern (no CLI calls, no injected JWT at session start in the harness-pattern sense).
- **Platform admin cross-org detail should be verified** in implementation — work-type tagging, target-org audit writes, notification config per customer org.
- **Tier 3 signup flow** should be verified — org + first admin + password + magic_link verify + first API key.
- **No architectural-layer deviations expected for authentication proper** (per comprehensive audit's section 3a: "Cross-checked extensively. Likely OK"). Only the default assistant auth pattern is entangled with Finding 0.

### From `2026-04-10-bulk-operations-pattern.md`:
or Ambiguities

From the artifact itself:
- **Whether `bulk_op_requested` queue message is useful in practice** or adds noise. Alternative: skip-the-queue (write directly to Temporal). Deferred to spec phase.
- Exact auto-generated CLI argument shapes, source abstractions, dry-run semantics, progress streaming format, cancellation semantics, per-batch retry policy, rate limiting for bulk ops touching external Integrations — all deferred to spec phase.
- Future: `bulk_apply` DSL for multi-entity-per-row, saga compensation for cross-batch rollback, `BulkOperation` entity for long-term spec history, cumulative state aggregation across batches. Added when forcing functions appear.

**Pass 2 observations:**
- **No architectural-layer deviation expected for bulk operations.** The design explicitly places `bulk_execute` in kernel code, running in the Temporal Worker. This is legitimate kernel territory — deterministic workflow orchestration with no agent reasoning.
- **The CLI verbs (bulk-create / bulk-transition / bulk-method / bulk-update / bulk-delete) should be checkable in the implementation.** Per comprehensive audit: "5 CLI verbs (create, transition, method, update, delete) — IMPLEMENTED" and "Selective emission discipline (bulk-update is silent) — IMPLEMENTED".
- **Potential subtle check**: does `bulk_execute` workflow live in the kernel Temporal Worker, SEPARATELY from any agent-execution activity? Per the design, yes — it's a generic workflow, not tangled with agent execution. If the current code conflates them (`process_with_associate` inside same worker as `bulk_execute`), that's fine topologically — both legitimately run in kernel-side Temporal Worker. But if the kernel-side Temporal Worker ALSO runs agent loops (per Finding 0), that's the problem — those loops should be in harness images subscribing to separate task queues, per the async-deepagents harness model.

### From `2026-04-11-base-ui-operational-surface.md`:
or Ambiguities

From the artifact itself (Open Follow-Ups):
- Contextual awareness indicator in UI (should UI show "Context: SUB-042" next to input?)
- Multi-window/multi-tab behavior (per-tab conversation? shared?)
- Widget ordering on role landing pages (MVP: alphabetical; post-MVP: per-role config)
- Assistant interruption semantics (can user cancel a running assistant turn?)

Deferred:
- UI component library choice (React-based assumed but unspecified)
- Styling conventions, keyboard shortcuts, pagination defaults
- Responsive behavior (mobile, tablet)
- Accessibility conformance
- Export formats
- Future `Widget` / `DashboardConfig` / `AlertConfig` entities

**Pass 2 critical observation:**
- **This artifact is the second independent confirmation of Finding 0's architectural claim.** The assistant MUST be a harness instance per this design. Current implementation has `kernel/api/assistant.py` — a stripped-down endpoint inside the API server process that streams text from Claude WITHOUT tools and WITHOUT the harness pattern. Per this design, that's architecturally wrong: the assistant should be a chat-runtime harness instance that the user's browser connects to (via WebSocket, per realtime-architecture-design), NOT an endpoint in the kernel's API server.
- **Kernel aggregation capabilities** should be verifiable in code: state-distribution, throughput, dwell-time, queue-depth, cascade-lineage. Per comprehensive audit: state_distribution + queue_depth in `aggregations.py` + `admin_routes.py` — CONFIRMED PRESENT.
- **Tables-over-charts discipline** is a UI behavioral expectation, checkable by reviewing the UI code (no chart components for things that should be tables).
- **Auto-generated-only discipline** is checkable by reviewing UI code (no per-org or per-entity custom UI code).

**The assistant-as-harness claim from this artifact + the assistant-via-harness-JWT claim from auth design + the three-harness-images claim from realtime-architecture = THREE independent statements that agent execution (including the assistant) lives in harness images outside the kernel.** Finding 0 is not a single-artifact claim; it's a cross-artifact consistent design that the implementation violates.

### From `2026-04-09-data-architecture-everything-is-data.md`:
or Ambiguities

- **Hot-reload signal for entity definition changes** — "Changes take effect immediately (or after a hot-reload signal)." Mechanism not specified in this artifact. Likely addressed in implementation spec (e.g., Change Stream on entity_definitions collection → in-process reload).
- **YAML export format** — not fully specified (what exactly is in it? how are relationships serialized?)
- **Rollback semantics** — preview shown, confirmation required. Specific behavior for cascading rollbacks (e.g., rolling back a skill change that affected a running associate) not detailed.
- **Versioning granularity for skills** — changes collection records content. How is skill content diffing surfaced? Full content? Field-level?

**Pass 2 observations:**
- **No architectural-layer deviation expected for data architecture.** The design cleanly separates platform (code in Git) from application (data in MongoDB). Current implementation has this split.
- **Clone/diff/deploy semantics** should be verifiable per comprehensive audit: "Clone (config only, no entity instances) — IMPLEMENTED", "Diff (show config differences between orgs) — IMPLEMENTED", "Export (YAML directory: entities/, roles/, rules/{entity}/, skills/*.md, lookups/, actors/, integrations/, capabilities/) — IMPLEMENTED". This artifact says clone doesn't copy instances; implementation should match.
- **Version tracking within the changes collection** should match design: every entity-def modification, rule change, skill update gets a change record.
- **What's NOT clearly stated here but is in section 3a**: the assignment of "Org lifecycle" as a Pass 2 review subsystem. Per this artifact, the design is clear — implementation should match.

### From `2026-04-13-simplification-pass.md`:
or Ambiguities

- **What "UI-only coalescing" looks like concretely** is not fully specified. "UI groups them for display by correlation_id. One rendered row: '47 submissions became stale' with drill-down." The implementation detail is deferred.
- **Change record metadata for rule evaluation** — schema not fully specified. Example JSON provided; exact field names not locked.

**Pass 2 observations:**
- **Watch coalescing MUST NOT be in the kernel implementation.** Per the simplification, the kernel emission path should NOT have a `coalesce` field, a `batch_id`, or time-window grouping logic. If current code has any of these, it's a post-simplification regression. Per comprehensive audit's section 3a: "Watch coalescing — simplified out per `2026-04-13-simplification-pass.md`. Verify the simplification was actually applied (UI-only coalescing, no kernel mechanism)." This is a Pass 2 check point.
- **Rule evaluation context** should be in changes collection records, not a separate trace collection. Verifiable in implementation.
- **Harness pattern is confirmed as Layer 3 architectural concept** — this simplification pass did NOT deprecate it. The harness pattern survived the review.
- **No changes to Integration adapter location, skill execution location, auth middleware location, or base UI auto-generation.** Post-simplification design matches the individual artifacts (realtime-architecture, integration-as-primitive, auth design, base UI operational surface).

This artifact confirms that Finding 0's concern (harness pattern required) is NOT something simplified away. The harness pattern is explicitly preserved in Layer 3 of the simplified architecture.

### From `2026-04-10-base-ui-and-auth-design.md`:
or Ambiguities

From the artifact's own Open section:
- MFA policy placement (resolved in 2026-04-11-authentication-design.md: role-level + actor override + org default)
- Tier 3 self-service signup full flow (partially resolved in auth design; billing deferred)
- Delegated admin across orgs (resolved in auth design via `_platform` org + PlatformCollection)
- Adapter for each identity provider — list and prioritize (deferred; MVP: OIDC generic + Okta)

**Pass 2 observations:**
- This artifact has been LARGELY SUPERSEDED by later design sessions. Most of its concrete decisions were refined:
  - Watch coalescing → simplified out
  - Ephemeral locks → unified into Attention
  - Auth → full design session produced 2026-04-11-authentication-design.md
  - Base UI → full design session produced 2026-04-11-base-ui-operational-surface.md
- **Useful historical context** for understanding why Attention exists (it unifies two originally-separate ideas: UI soft-locks + active routing).
- **Role's two ergonomic paths** (named shared vs inline) is STILL CURRENT per the comprehensive audit (Role fields include `is_inline`, `bound_actor_id`).
- **Actor lifecycle states** (provisioned → active → suspended → deprovisioned) is STILL CURRENT per comprehensive audit.
- **Authentication methods on Actor** is STILL CURRENT.
- **No architectural-layer deviation specific to this artifact.** It's an early sketch — successors are the authoritative source.
- The "Base UI is outside the kernel" framing is consistent with all subsequent artifacts: UI is a consumer of the kernel's API, not a kernel component.

### From `2026-04-10-post-trace-synthesis.md`:
or Ambiguities

This artifact catalogs ten open items. Most are resolved by subsequent artifacts:
- Items 1, 2, 3 → 2026-04-10-realtime-architecture-design.md
- Item 4 → referenced as open in realtime-architecture-design Part 10 "deferred items", never fully formalized as a separate artifact; the pattern is stated: adapter inbound methods + kernel webhook endpoint
- Items 5, 6 → documentation clarification (absorbed into white paper / consolidated specs)
- Item 7 → 2026-04-10-bulk-operations-pattern.md
- Items 8, 9 → 2026-04-11-base-ui-operational-surface.md
- Item 10 → 2026-04-11-authentication-design.md
- Item 1 was later simplified out of kernel entirely per 2026-04-13-simplification-pass.md
- Item 2 was later unified with Attention per 2026-04-10-realtime-architecture-design.md

**Pass 2 observations:**
- This artifact is a ROUTING document — it points to where architectural decisions should be made. It surfaces issues without resolving them.
- The follow-up artifacts (realtime-architecture, bulk-operations, base-ui-operational-surface, authentication, simplification) ARE the authoritative sources for Pass 2.
- **Inbound webhook dispatch** is the one item that was NOT given its own design artifact. It remained at the level of "update the Integration artifact" which appears to not have happened as a standalone update. The Integration primitive artifact (2026-04-10-integration-as-primitive.md) mentions inbound webhooks briefly ("Integrations support both outbound and inbound connectivity"), and the realtime-architecture-design Part 10 lists "Inbound webhook dispatch documentation" as open. This may be a missing-formalization issue — implementation details for webhooks need verification against existing kernel adapter dispatch patterns.
- **No Finding 0-class deviations expected from this artifact.** It's a checkpoint/routing document, not an architectural-layer statement.

### From `2026-04-14-impl-spec-phase-0-1-consolidated.md`:
or Ambiguities

- **Phase 0-1 doesn't contradict the harness pattern** — it explicitly defers harnesses to Phase 5.
- Phase 0-1 doesn't discuss where agent execution belongs — that's Phase 2 scope.
- Phase 0-1 explicitly defers the "base UI" including the assistant pattern to Phase 4.
- **The open question is whether Phase 2 spec places agent execution in the kernel or in a harness.** This file itself is consistent with the harness design — it just doesn't implement it.

**Pass 2 observations:**
- **No architectural-layer deviation specific to Phase 0-1.** The spec is faithful to the design artifacts.
- **Phase 0-1 establishes the foundation correctly**: modular monolith with trust boundary, kernel/non-kernel split, CLI-in-API-mode discipline, three kernel processes.
- **The seven kernel entities** (Organization, Actor, Role, Integration, Attention, Runtime, Session) are all defined in Phase 1 per design.
- **Integration adapters deferred to Phase 3** — consistent with design (Integration primitive in Phase 1, adapters in Phase 3).
- **Harness pattern deferred to Phase 5** — consistent with design. This means Phase 2-4 must build things WITHOUT harnesses; the question is how associate execution works in Phase 2 without the harness pattern being ready.
- **The phasing creates a potential architectural risk**: Phase 2 (Associate Execution) comes BEFORE Phase 5 (Real-Time, harness pattern formalized). If Phase 2 implements agent execution without a harness (because harnesses are Phase 5), the natural place to put it is the kernel's Temporal Worker. Which is exactly what Finding 0 describes. The Phase 2 consolidated spec needs to resolve this tension.

### From `2026-04-14-impl-spec-phase-2-3-consolidated.md`:
or Ambiguities

**The big one — Pass 2 Finding 0 source:**

The Phase 2-3 spec embeds agent execution in the kernel Temporal Worker. The design (2026-04-10-realtime-architecture-design.md) says agent execution should be in harness images outside the kernel. The spec does NOT explain why it deviates from the design. It also does not acknowledge the deviation.

**Why the deviation likely happened (my inference):**
1. Phase 5 (harness pattern, Real-Time) comes AFTER Phase 2 (Associate Execution) in the build sequence.
2. Phase 2 needs agent execution to work, but harnesses aren't available until Phase 5.
3. The spec solved this by placing agent execution inside the kernel's existing Temporal Worker — a kernel process that's already available in Phase 2.
4. **The spec should have either:**
   - Reordered phases (Phase 5 harness pattern before Phase 2 associate execution), OR
   - Explicitly created the async-deepagents harness image in Phase 2 as an additional deployable (leveraging the harness pattern ahead of the full real-time formalization), OR
   - At minimum, flagged this as a temporary placement with a migration plan to move agent execution to a harness image in Phase 5.

None of these happened. The spec placed agent execution in kernel/temporal/activities.py with no migration plan. The build implemented the spec faithfully. Pass 1 audit checked field-level correctness and missed the layer issue. Finding 0 emerged only when Craig asked "why isn't the assistant using the harness pattern?"

**Secondary observations:**
- **`_execute_reasoning` uses `anthropic` library directly.** Per the design, the kernel should be LLM-agnostic — the harness picks the framework. This embedding of `anthropic` in the kernel is a direct violation of the LLM-agnostic design principle.
- **Sandbox execution (Daytona per design layer 3)** is entirely absent. The agent runs inside the kernel Temporal activity with full DB access, not inside a sandbox.
- **Skill integrity check** (`verify_content_hash`) is correctly placed per design (line 409 of this spec) — it IS a kernel function, but is invoked inside the kernel-side agent execution. If agent execution moves to a harness, the integrity check should happen when skills are loaded by the harness from the kernel.
- **Scheduled associate execution** uses application-level cron in queue processor for MVP (Option A), not Temporal Schedules. Per design this is acceptable (both designs mentioned this path).
- **Direct invocation** endpoint exists. Per design this supports real-time channels (Phase 5) as well as testing.
- **Phase 3 (Integrations)** is consistent with design — no layer deviations.

**Pass 2 conclusion for this spec**: Phase 2 is where Finding 0 entered the spec. Phase 3 (Integrations) is clean.

### From `2026-04-14-impl-spec-phase-4-5-consolidated.md`:
or Ambiguities

**Pass 2 findings in this spec:**

1. **The `kernel/api/assistant.py` endpoint violates the harness pattern.** It's a kernel-side text-only LLM streaming endpoint. Per design, the assistant should be a running chat-harness instance — an instance of `indemn/runtime-chat-deepagents:1.2.0` that the user's browser connects to via WebSocket, uses CLI via subprocess, runs deepagents locally, and inherits the user's session JWT.

2. **No `harnesses/chat-deepagents/` specified.** Phase 5 includes only the voice harness example. The chat harness — which is what the assistant needs — is missing from the spec entirely.

3. **No `harnesses/async-deepagents/` specified.** Per the realtime-architecture-design, async agent execution should live in `indemn/runtime-async-deepagents:1.2.0`. This harness is also missing from the spec. The async agent execution instead lives in `kernel/temporal/activities.py::process_with_associate` (from Phase 2-3 spec).

4. **The assistant auth flow in the spec matches the design superficially** ("inherits user's session") but the LOCATION is wrong (in kernel endpoint, not in harness).

5. **Phase 5 harness example uses `deepagents.create_deep_agent(...)`** which is the correct framework per the design. But the Phase 2 agent execution uses `anthropic` client directly (no deepagents). Two different agent implementations — the kernel-side one is simpler (no skill loading via deepagents middleware, no todo list, no subagents), the harness one is the full deepagents pattern. These should converge to one implementation, living in the harness.

6. **Phase 5 integration between Runtime entity + harness instance + Temporal task queue is partially specified.** The Runtime entity has a `kind: async_worker` variant per the design, but this spec only shows voice. Async runtimes subscribing to Temporal task queues (per the design's line 460-463) are not explicitly specified in this Phase 5 spec — they're implicit in the Phase 2 Temporal worker spec but that worker is kernel-side.

**Pass 2 conclusion for this spec**: Phase 4 (Base UI + assistant) has a layer deviation — the assistant should be a chat-harness. Phase 5 (Real-Time, voice harness) is clean design-wise but only includes one of three expected harness images, and the other two (chat, async) are missing from the spec entirely.

### From `2026-04-14-impl-spec-phase-6-7-consolidated.md`:
or Ambiguities

**Pass 2 observations:**

- **No Finding 0-class layer deviations added by this spec.** It's an operational phase spec that relies on Phases 0-5 being correct.
- **Phase 6-7 does NOT fix Finding 0.** If agent execution stays in `kernel/temporal/activities.py`, Phase 6 associates (Meeting Processor, etc.) and Phase 7 associates (Classifier, etc.) all run inside the kernel's Temporal Worker, not in harnesses.
- **Phase 6 assistant usage** ("what's the story with INSURICA?") depends on the Phase 4 assistant having tools. Per the comprehensive audit, the assistant has no tools (Finding 2). Without resolution of Finding 0/2, the Phase 6 assistant test case (#6 in acceptance criteria: "THE ASSISTANT ANSWERS 'what's the story with X?' comprehensively") cannot be met.
- **Phase 6's daily dog-fooding test** is what would have surfaced Finding 0 — if Indemn tried to use the assistant daily, the lack of tools would have been noticed immediately. Per the comprehensive audit, Phase 6 hasn't been implemented yet — which is why Finding 0 wasn't surfaced by dog-fooding.
- **No new harnesses specified here.** If chat-harness or async-deepagents harnesses are needed for proper agent execution, they would need to be added in an earlier phase or as a retrofit. Phase 6-7 doesn't include them.

**Pass 2 conclusion for this spec**: Phase 6-7 is operational and adds no architectural deviations. It inherits Finding 0 from Phase 2 and Finding 2 from Phase 4. It's the phase that would have surfaced these issues through real usage.

### From `activities.py`:
or Ambiguities

**This file IS the Finding 0 code site for async/scheduled agent execution.** It violates the design explicitly.

- **Why it was written this way**: Per the Phase 2-3 spec, this is exactly what was specified. The spec placed agent execution in kernel Temporal activities. The code implements the spec faithfully. The deviation entered the pipeline at the spec level, not the code level.
- **Migration path**: The `process_with_associate` function and its helpers (`_execute_deterministic`, `_execute_reasoning`, `_execute_hybrid`, `_execute_command_via_api`, `_load_skills`, `_parse_skill_steps`) should move OUT of the kernel and INTO `harnesses/async-deepagents/`. The kernel keeps only `claim_message`, `load_entity_context`, `complete_message`, `fail_message`, `process_human_decision`, `process_bulk_batch`, `preview_bulk_operation` — the deterministic workflow activities that are legitimately kernel-side.
- **Async agent task queue**: Per design, the async-deepagents harness subscribes to a Temporal task queue named after the Runtime. The kernel's queue processor (or API-optimistic-dispatch) writes to that queue; the harness claims. Today, everything runs on the kernel's "indemn-kernel" task queue.
- **Shared `_execute_command_via_api` logic**: In the harness pattern, this would be replaced by `subprocess.run(["indemn", ...])` calling the CLI which already calls the API. The harness doesn't need to know about the API directly.

**Other observations:**

- `_parse_skill_steps` is a simple line-by-line parser (backtick-delimited indemn commands, "If"/"When" conditions). Not a full DSL. This is consistent with the spec ("This is a simple line-by-line interpreter, NOT a full DSL engine").
- `process_bulk_batch` uses `entity_cls.find_scoped(spec.filter_query)` — scoped queries. MongoDB transactions per batch. Looks correct per bulk-operations-pattern design.
- `process_bulk_batch` does raw `update_one` for bulk-update (silent — bypasses `save_tracked`) per the selective emission discipline. Correct.
- Context propagation via headers (`X-Correlation-ID`, `X-Cascade-Depth`) is consistent with the spec.
- No sandbox wrapping agent execution. Per Layer 3 design, agent should run in Daytona. Not implemented — secondary consequence of Finding 0.

### From `assistant.py`:
or Ambiguities

**Pass 2 findings in this file:**

1. **Wrong architectural layer.** Assistant should be a chat-harness instance, not a kernel API endpoint. This is the second arm of Finding 0 (the first being `kernel/temporal/activities.py::process_with_associate` for async).

2. **No tools.** The `client.messages.stream(...)` call has no `tools=[]` parameter. The LLM cannot execute any commands. This is Finding 2 from the comprehensive audit.

3. **Skill list injected as text, not as structured tools.** Skills are concatenated into the system prompt as a bullet list. A proper implementation would register each skill's operations as tools with explicit schemas — matching the `execute_command` pattern in `_execute_reasoning`.

4. **Duplicated `anthropic` usage.** Two places in the kernel import and use `anthropic`: this file and `kernel/temporal/activities.py`. Per the design, neither should exist in the kernel — LLM usage belongs in harness images.

5. **Migration path:**
   - Short-term fix (keeps Finding 0 unresolved but fixes Finding 2): add `tools=[execute_command]` param here and wire up a command executor mirroring `_execute_command_via_api` from activities.py.
   - Proper fix (resolves Finding 0 and 2): delete this file. Build `harnesses/chat-deepagents/`. User browser connects to chat-harness via WebSocket. Harness runs deepagents with CLI sandbox. JWT injected at session start.

6. **The current implementation says "You can execute any CLI command" in the system prompt** but has no mechanism to do so. This is misleading — the LLM will claim it executed commands when it didn't. Until fixed, this is an active user-facing bug.

**Secondary observations:**

- The skill list enumeration in `_load_skills_for_roles` iterates `ENTITY_REGISTRY` and checks role permissions — this is reasonable permission-aware surfacing but the output format (a text bullet list in the system prompt) isn't useful without tools.
- Streaming response is `media_type="text/plain"` — not Server-Sent Events or JSON Lines. This is a simple implementation but not ideal for surfacing structured tool results or entity renderings (which the design says the assistant should do).
- **Per Phase 4-5 spec line 836-876, the spec explicitly implemented this file as spec'd.** The spec itself was the deviation. The code matches the spec but the spec deviates from the design.

### From `workflows.py`:
or Ambiguities

**Pass 2 findings:**

- **`ProcessMessageWorkflow` shouldn't exist in the kernel's Temporal worker** — at least the part that calls `process_with_associate`. Options for fix:
  1. Move `ProcessMessageWorkflow` to `harnesses/async-deepagents/`; kernel's workflows.py only keeps `HumanReviewWorkflow` and `BulkExecuteWorkflow`.
  2. Keep `ProcessMessageWorkflow` in the kernel but replace `process_with_associate` with a task-queue-routing activity that dispatches to a Runtime-specific queue.
  3. Split: the kernel's `ProcessMessageWorkflow` handles "process human review" and "process bulk"; a harness's `ProcessMessageWorkflow` handles "process associate work."
- **`HumanReviewWorkflow` and `BulkExecuteWorkflow` are correctly placed.** They should remain in the kernel.

**Secondary observations:**
- `workflow.patched("v2-enhanced-error-handling")` is called — G-77 versioning. Looks correct.
- Non-retryable errors (PermanentProcessingError, SkillTamperError, PermissionError) correctly configured.
- Human review timeout defaults to 48 hours — matches design.
- Bulk abort mode raises `BulkAbortError` which is non-retryable.
- Sentinel ObjectId `"000000000000000000000000"` used for human review claim — slightly hacky but fine.

This file itself is not the primary Finding 0 location (that's activities.py), but it's a direct caller of the problematic activity.

### From `worker.py`:
or Ambiguities

**Pass 2 findings:**

- **The worker registers `process_with_associate` as an activity.** Per design, agent execution should be in a separate harness image, not in the kernel worker.
- **Fix direction**: Split this worker into two:
  1. Kernel worker (this file): registers `claim_message`, `load_entity_context`, `complete_message`, `fail_message`, `process_human_decision`, `process_bulk_batch`, `preview_bulk_operation`. Keep `HumanReviewWorkflow` and `BulkExecuteWorkflow`. Remove `ProcessMessageWorkflow` and `process_with_associate`.
  2. Async-deepagents harness worker (new, in `harnesses/async-deepagents/`): registers `ProcessMessageWorkflow` + agent execution activities. Subscribes to a Runtime-specific task queue.
- The split requires:
  - A task queue naming convention (e.g., `"runtime-{runtime_id}"`)
  - The queue processor's dispatch to write to the appropriate task queue based on the associate's Runtime
  - The harness image to read its Runtime ID from env and subscribe to its task queue

**Secondary observations:**
- `graceful_shutdown_timeout=30` is reasonable.
- `max_concurrent_activities=20` and `max_concurrent_workflow_tasks=10` are deliberate caps to prevent MongoDB overload.
- OTEL tracing is correctly wired.

This file is concise and the architectural issue is clear: it registers too much. The kernel worker should be lighter and a harness worker should handle agent execution.

### From `adapter.py`:
or Ambiguities

**No Pass 2 layer deviation for this file.** The adapter base class is correctly placed in the kernel per the design.

**Secondary observations:**
- The class is `ABC` but uses `raise NotImplementedError` rather than `@abstractmethod`. This is intentional — methods are optional, not required.
- Error hierarchy is well-designed for retry classification.
- Constructor signature (`config`, `credentials`) makes adapters stateless between invocations — consistent with how `kernel/integration/dispatch.py` instantiates them per-call.

**Note on the design's open question** (from 2026-04-10-integration-as-primitive.md): Tier 3 developers who need a new provider adapter have "the obvious answer" of contributing a kernel PR. Whether there's a managed-extension mechanism (loading external adapters at runtime without kernel deploy) is explicitly deferred. Current implementation only supports kernel-bundled adapters. This is correct per design.

### From `registry.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The design allows for plugin-loadable adapters in the future (explicitly deferred). Current registry is static (registered at import time).
- Tier 3 custom adapter path is not implemented (deferred per design).
- No validation that `adapter_cls` actually inherits `Adapter` — type hint is advisory only.

The registry is minimal and correctly placed. No architectural concerns.

### From `dispatch.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Setting `adapter._secret_ref` as an instance attribute is slightly hacky — could be a constructor param.
- `execute_with_retry` is a function, not a decorator. Callers wrap method invocations explicitly.
- Only retries once — no exponential backoff or multiple attempts. Consistent with "fail fast" semantics for integrations.
- Token refresh on `get_adapter` is "check proactively" (via `needs_token_refresh()`); `execute_with_retry` also handles reactive refresh on AdapterAuthError. Both paths exist.

Dispatch is correctly placed in the kernel and follows the design pattern.

### From `resolver.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The comprehensive audit verified "Credential resolution (actor→owner→org) IMPLEMENTED".
- Owner-bound resolution (step 2) is what enables scheduled associates bound to humans (CRM use case).
- No fallback to contextvars if `actor_id` parameter is None but `current_actor_id.get()` is also None — would raise `ObjectId(None)` error. Minor robustness concern, not architectural.
- Error message gives the CLI command to create an integration — useful UX.

Resolver is well-placed and matches design expectations.

### From `websocket.py`:
or Ambiguities

**No Pass 2 layer deviation for the UI WebSocket.**

**Secondary observations:**
- **WebSocket keepalive**: white paper says "the real-time UI channel, the chat harness — must send ping frames every 30-45 seconds." This WebSocket handler handles `ping` messages from the client but doesn't proactively send pings to keep the connection alive. May rely on client-side pings to prevent proxy timeouts.
- Database-level `db.watch()` rather than per-collection watches — single stream, filtered client-side via subscription. Efficient for many subscribed collections.
- Filter-aware per the spec requirement: subscriptions specify entity_type/entity_id/collection filters.
- Auth via query param: not ideal for security (URL logs can leak tokens) but required for browser WebSocket API compatibility. Standard tradeoff.
- `_serialize_for_ws` handles ObjectIds and datetimes for JSON transmission.

This file implements the UI real-time mechanism correctly. It's unrelated to Finding 0 — which concerns where agent execution lives, not how UI receives updates.

**Note on chat-harness WebSocket**: the design's chat-harness pattern would have a SEPARATE WebSocket endpoint served by the chat-deepagents harness image (not by the kernel API server). That WebSocket would carry the assistant conversation. Currently, the assistant is a kernel API endpoint (`kernel/api/assistant.py`), not a WebSocket, so no parallel chat-harness WebSocket exists. This is the broader Finding 0 — not this file's concern.

### From `events.py`:
or Ambiguities

**No Pass 2 layer deviation for this file.**

**Secondary observations:**
- Auth uses the current_actor's org_id to filter — one actor can only see events for their own org. Good.
- Actor filter uses `$or` to include both scoped-to-actor messages AND unscoped messages — correct for the harness use case (a harness may receive both kinds).
- Interaction filter is defensive (checks 3 places) — addresses the inconsistency in where interaction_id is stored.
- The NDJSON format means consumers get one event per line — easy to parse with `for line in stream.stdout` in a harness.
- **The endpoint exists but no harness consumes it.** When harnesses are built per Finding 0's fix, this endpoint is ready to serve them.

This is a correctly-placed kernel API endpoint. The architectural fix is to add harness consumers.

### From `interaction.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Handoff requires an Interaction entity definition; per the comprehensive audit, Interaction as a domain entity is not defined in the seed data (Phase 6/7 defines it, but Phase 6 hasn't run).
- Re-targeting pending messages via direct `update_many` bypasses save_tracked — this is a raw update without audit. For the handoff use case this may be acceptable (the audit is on the Interaction entity's save_tracked), but technically any message update should go through a consistent path.
- Role-based transfer (`to_role`) doesn't assign a specific actor — someone in that role must claim. The Runtime handling the conversation is expected to bridge turns to the queue targeting the role.
- Observe creates a 1-hour TTL Attention — UI should heartbeat to extend. If user just observes and leaves, Attention auto-expires.

**Dependency on harness existence**: The design says "The Runtime hosting the Interaction subscribes (via its harness's Change Stream) to updates on the Interaction entity. When handling_actor_id or handling_role_id changes, the Runtime's session logic switches." This requires a harness to exist and run. Per Finding 0, no harnesses exist yet. So this handoff endpoint works at the entity level (updates handler, closes/opens Attention) but the actual mode switch in a running harness can't happen — there are no running harnesses.

This file is correctly specified and implemented; it's waiting for harnesses to exist to be fully functional end-to-end.

### From `generator.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Generates CLI commands section listing capabilities — associates reading skills can learn available commands.
- No examples section — could be added later for better LLM consumption.
- No error-handling examples or edge case documentation — minimalist.
- Output is deterministic given the same definition — good for caching/hashing.

This is a simple, correctly-placed kernel utility.

### From `schema.py`:
or Ambiguities

**No Pass 2 layer deviation for schema.**

**Secondary observations:**
- The `content_hash` field supports tamper detection. The hash is verified when skills are loaded (`verify_content_hash` in `kernel/skill/integrity.py`).
- `status: pending_review` supports the skill approval workflow (new versions pending approval before activation).
- Version field is incremented on updates — multiple versions can exist in changes collection.
- No `description` field in the schema, but the `_load_skills_for_roles` in assistant.py references `skill.description` — potential minor inconsistency. May be added via `extra="allow"` or via Pydantic extra fields.

Schema is clean and appropriately placed.

### From `session_manager.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The revocation cache (in-memory per instance) is separate from this file — lives in `kernel/auth/jwt.py` per Phase 4 spec.
- Session TTL cleanup (7 days after expiration) not visible here — likely a queue processor sweep.
- `create_session` doesn't currently handle refresh tokens — refresh is opaque random string stored in Secrets Manager per design, implemented separately.

Kernel-side session manager is correctly placed per design. No architectural concerns.

### From `jwt.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Per-instance in-memory cache — cross-instance coordination via Change Stream is scale-appropriate for MVP. Scale-up path (Redis Pub/Sub) is a design open item.
- 15-minute cache TTL matches access token lifetime — clean retention logic.
- Bootstrap loads last 15 minutes of revocations on startup to cover the gap until Change Stream catches up — correct per design.
- Magic link token expiry defaults to 4 hours — reasonable for email delivery + user action.
- `watch_revocations` is a fire-and-forget coroutine; crashes are logged but not re-started. This could leave revocation cache stale until next instance restart — potential operational concern but MVP-acceptable.

Auth JWT is correctly placed and implements the design. No architectural concerns.

### From `auth_routes.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Password login flow handles MFA via partial_token pattern — clean separation of authentication phases.
- SSO flow uses the Integration primitive — the identity provider is an Integration. Matches design.
- Platform admin session writes audit in target org — matches design precisely.
- Tier 3 signup minimal: org + first admin + password + email verification. Billing/plans deferred per design.
- Auth events view filtered by actor's org (via middleware) — appropriate permission model.

Large file but straightforward implementation of the auth design. No architectural concerns.

### From `registration.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The auto-generation pattern is central to the "self-evidence" design — define entity → all routes exist.
- State machine bypass protection via PUT rejection is explicit per comprehensive audit.
- Optimistic dispatch is fired after save_tracked — correct per design's "optimistic dispatch + sweep backstop" pattern.
- Integration route accepts system_type from request body — minor API ergonomics concern but works.
- Per-entity bulk endpoint matches the auto-generated CLI verb pattern.

This file is correctly placed kernel-side and implements the self-evidence design.

### From `bulk.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Auth only checks for authenticated actor — doesn't check per-entity permissions at this layer. Per-entity bulk start endpoint (in registration.py) does check permissions. This endpoint is more generic.
- No permission check on cancel — any authenticated actor can cancel any bulk. Possible security concern (should be limited to ops or the initiating actor).
- Error handling is minimal; catches generic Exception on describe.
- `list_workflows` iteration could be paginated — returns all results currently.

This file is correctly placed and implements the bulk monitoring design. Permission model for cancel may be a minor improvement opportunity but not a layer issue.

### From `AssistantProvider.tsx`:
or Ambiguities

**Pass 2 findings:**
- **UI implements HTTP + streaming pattern matching the kernel-endpoint assistant.** If the assistant were a proper chat-harness, the UI would likely use WebSocket (per realtime-architecture-design's harness pattern for chat), and the connection management would be different (long-lived WebSocket vs. one-shot HTTP POST).
- **Context is minimal** — just view_type + path. Per design (base-ui-operational-surface.md §4.7):
  ```
  {
    "view_type": "EntityDetail",
    "current_entity": {"type": "Submission", "id": "SUB-042"},
    "current_filter": null,
    "role_focus": "underwriter",
    "recent_actions": [...]
  }
  ```
  Current implementation has only `{view_type, current_path}`. Additional context (current_entity, filter, role_focus, recent_actions) is missing. Needs richer context building in future iterations.
- **No inline entity rendering** in this provider — streaming just builds a text string. The design calls for "inline entity renderings" but implementation uses plain text. Deferred to post-MVP per spec.

**Secondary observations:**
- Auth is handled at the fetch level via `getToken()` — consistent with the user-session-inheritance design.
- Error recovery is minimal — user sees "Error: could not reach assistant" with no retry.
- The streaming uses `TextDecoder().decode()` on each chunk — handles partial UTF-8 characters potentially incorrectly; typically OK for English but edge case in multi-byte chars.

This UI provider is a reasonable implementation for the kernel-endpoint-based assistant. When the architecture moves to chat-harness, this provider will need to be rewritten to use WebSocket and handle structured messages with tool results and entity renderings.

### From `useAssistant.ts`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- `AssistantMessage.content` is a string — limits the ability to render structured content (entities, tool results). Design mentions "inline entity renderings" which would require richer content type (e.g., `string | EntityCard | ToolResult`). Current implementation is text-only (matches deferred scope).
- Role field only has "user" | "assistant" — no "tool" role for tool-use interleaving (which Claude API supports). If assistant gains tools, this should expand.

This is a minimal, idiomatic React context hook. No architectural concerns.

### From `org_lifecycle.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The exclusion list for each category (what gets stripped during export) is hardcoded per category. Works for MVP but could be moved to metadata on the entity schemas.
- Archive/deprecated items are filtered at export (rules with status != archived, skills with status != deprecated).
- Integrations exported without credentials — credential rotation/setup remains a separate flow on import.
- `deploy_org` doesn't remove items only in target (only_in_b) — safe default, but users may want an opt-in "strict deploy" mode.
- Version increment on existing records during import — preserves version tracking.
- No Temporal workflow for deploy (spec mentions saga-compensated deployments but this is a simple sequential implementation). Acceptable for MVP.

**Per comprehensive audit**: "Export (YAML directory: entities/, roles/, rules/{entity}/, skills/*.md, lookups/, actors/, integrations/, capabilities/) — IMPLEMENTED". This file produces a nested dict, not YAML files directly. The YAML-directory format is likely handled by the CLI command (`kernel/cli/org_commands.py`), which calls this module's functions and then writes YAML to disk.

Org lifecycle is correctly placed kernel-side and matches design intent. No architectural concerns.

### From `cache.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- **NO COALESCING LOGIC** in this file — correctly simplified out per 2026-04-13-simplification-pass.md.
- Per-instance cache is acceptable for MVP; cross-instance drift is bounded by 60s TTL + explicit invalidation.
- Async reload on TTL expiry returns stale data during the reload — acceptable for watch evaluation.
- Future enhancement: Change Stream on roles collection (mentioned in docstring) would give faster cross-instance invalidation.

This file correctly implements the simplified watch cache per design. No architectural concerns.

### From `evaluator.py`:
or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- All 15 operators from the design present — matches comprehensive audit's "COMPLETE" status.
- Dot-notation nested field access enables conditions like `{"field": "submission.organization.primary_owner_id", ...}`.
- Timezone handling is defensive: adjusts now() to naive if actual datetime is naive.
- `contains` uses string conversion — may not handle arbitrary objects cleanly but works for expected types.

Pure, correctly-placed evaluator. No architectural concerns.

### From `Dockerfile`:
or Ambiguities

**Finding 0 confirmation at the infrastructure layer:**
- **The kernel image is correctly built**, but:
- **No harness images exist.** Per design, there should be three additional images: `indemn/runtime-voice-deepagents`, `indemn/runtime-chat-deepagents`, `indemn/runtime-async-deepagents`. None are present in the repo.
- Because no harness images exist, Finding 0's structural gap is present at every layer — design (harness pattern), code (in-kernel agent execution), and infrastructure (no harness Docker images).

**Fix direction:**
- Create `harnesses/async-deepagents/Dockerfile` + Python harness script.
- Create `harnesses/chat-deepagents/Dockerfile` + Python harness script.
- Create `harnesses/voice-deepagents/Dockerfile` + Python harness script (spec'd but not implemented).
- Each harness image includes: harness script, `indemn` CLI pre-installed, framework (deepagents), transport (LiveKit/WebSocket/Temporal).
- Configure Railway services for each harness image with appropriate environment variables (RUNTIME_ID, INDEMN_SERVICE_TOKEN, INDEMN_API_URL).

**Secondary observations:**
- Single-image multi-entry-point is fine for the kernel (3 kernel processes share code).
- No health check in Dockerfile — Railway likely provides health checks via HTTP endpoints configured elsewhere.
- `--no-dev` correctly excludes dev dependencies.
- uv.lock frozen sync ensures reproducible builds.

Dockerfile is correctly configured for the kernel, but missing the harness counterparts required by the design.

### From `docker-compose.yml`:
or Ambiguities

**Pass 2 findings:**

1. **Temporal Worker missing from local dev.** Developers testing associate execution need to manually run `python -m kernel.temporal.worker`. Could be added to docker-compose for convenience.

2. **No harness services.** Per Finding 0, harnesses should exist as separate services. Once harnesses are built, they should be added to docker-compose.yml for local dev:
   ```yaml
   indemn-async-deepagents:
     build: ./harnesses/async-deepagents
     environment:
       - INDEMN_API_URL=http://indemn-api:8000
       - INDEMN_SERVICE_TOKEN=...
       - RUNTIME_ID=...
   ```
   Similarly for chat and voice harnesses.

**Secondary observations:**
- `JWT_SIGNING_KEY=dev-signing-key-not-for-production` is correct for local dev.
- No health checks defined — relies on `depends_on` for startup order (not for readiness).
- `--reload` flag on uvicorn enables hot reload during development.
- No volume for UI (dev server runs separately).
- Atlas dev cluster referenced by env var — no local MongoDB container.

docker-compose matches the Phase 0-1 spec. The gaps (no Temporal Worker service, no harness services) reflect the broader Finding 0 architectural incompleteness, not a local dev config bug per se.

### From `2026-03-24-associate-domain-mapping.md`:
or Ambiguities

- Where do domain objects live (DB schema? code structure)?  — resolved in entity-framework (later)
- Where do capabilities live (kernel? domain?) — resolved as "kernel capabilities" in 2026-04-09-entity-capabilities-and-skill-model.md
- How do the 48 associates map to runtime images/processes — resolved in realtime-architecture-design (2026-04-10)
- How is the no-code configuration (Strategy Studio) implemented — deferred per later artifacts

**No Finding 0-class deviation concerns from this artifact.** It's domain catalog, not architectural-layer placement.

### From `2026-03-24-source-index.md`:
or Ambiguities

- Not applicable — this is a provenance document.

**No architectural content. No Finding 0-class concerns.** Pass 2 audit scope: this file establishes context but doesn't constrain architecture.

### From `2026-03-25-associate-architecture.md`:
or Ambiguities

Artifact itself lists 7 open decisions — all resolved in later artifacts:
1. V2 redesign scope → resolved: new codebase, not evolution of V2
2. Bot-service role → resolved: not evolved, new kernel image + harness images
3. Skill format → resolved: markdown (2026-04-09)
4. Domain access control → resolved: Role-based permissions (white paper, auth-design)
5. Workflow execution → resolved: watches + scheduled triggers + direct invocation
6. Multi-agent coordination → resolved: unified queue + watches
7. State management → resolved: Attention entity + Temporal workflow state

**Early artifact. No Finding 0-class deviations introduced here. The LLM-framework-specific framing (LangChain deep agents) later generalizes to "harness pattern" — each framework gets its own harness image.**

### From `2026-03-25-domain-model-research.md`:
or Ambiguities

- Exact final primitive count — resolved to 6 (2026-04-08)
- How to unify IM + GIC Submission models — resolved: both become domain entity definitions stored as data per-org.
- What counts as "platform" vs "domain" — resolved: domain is per-org data; platform is kernel code + kernel entities.

**Early exploratory artifact. No Finding 0-class deviations introduced here — this is domain analysis, not layer placement.**

### From `2026-03-25-domain-model-v2.md`:
or Ambiguities

- FormSchema location (Core Insurance or Platform) — later resolved: it's an entity definition field spec.
- DTC model (EventGuard) Application entity — later resolved via Interaction/Application pattern.
- "Can this be built?" — later resolved via entity framework (dynamic class generation from definitions).

**Exploratory domain modeling. No Finding 0-class deviation claims here — this is entity classification, not layer placement.**

### From `2026-03-25-platform-tiers-and-operations.md`:
or Ambiguities

- Tier 3 pricing model (per API call / per entity / per agent) — deferred
- Team restructuring pace — deferred
- Hiring plan — deferred

**Business/operational artifact. No Finding 0-class deviations. The Tier 3 CLI-based development model is consistent with later CLI-first architectural decisions.**

### From `2026-03-25-session-notes.md`:
or Ambiguities

- Associate mechanics refinement deferred ("still work to refine the associates and how those play into everything else")
- Stakeholder political strategy

**No architectural-layer claims. No Finding 0-class concerns.**

### From `2026-03-25-the-operating-system-for-insurance.md`:
or Ambiguities

- How to make implementation "trivially fast" technically — resolved via CLI auto-generation from entity definitions.
- How carriers/distribution work on the OS — resolved via entity modeling (Carrier, DistributionPartner primitives).

**Vision framing document. No Finding 0-class deviations. Establishes the "applications run on the OS" mental model that informs later kernel vs. harness separation.**

### From `2026-03-25-why-insurance-why-now.md`:
or Ambiguities

- None architecturally.

**Business rationale document. No Finding 0-class concerns. Establishes the "every entity has CLI, every operation is agent-accessible" principle that later becomes the auto-generation design.**

### From `2026-03-30-design-layer-1-entity-framework.md`:
or Ambiguities

**This artifact was largely superseded.** It established:
- Modular monolith (RETAINED)
- FastAPI + Typer + Beanie + Pydantic (RETAINED)
- Auto-registration pattern (RETAINED — became auto-generation from entity definitions)
- Base Entity class + Mixins pattern (RETAINED conceptually)

It proposed and later REVISED:
- RabbitMQ for events → replaced with MongoDB message_queue + Temporal dispatch
- Python classes as entity definitions → replaced with data-driven definitions (EntityDefinition collection + dynamic class creation)
- Sub-domain folder organization → replaced with kernel/kernel_entities split + domain entities as data

**Pass 2 check**: This artifact's "modular monolith, one deployable unit" aligns with the kernel deployment. But its pre-harness-pattern framing didn't constrain future harness design. Finding 0 (harness pattern) emerged later and is independent of this artifact's decisions.

**Potential discrepancy**: The artifact proposes `platform/entities/associate.py` — an associate entity in the platform sub-domain. The implementation has `kernel_entities/actor.py` (Actor primitive, which Associate specializes via `type="associate"`). Naming evolved but semantic intent preserved.

### From `2026-03-30-entity-system-and-generator.md`:
or Ambiguities

- Postgres vs MongoDB — later resolved to MongoDB.
- YAML format — later resolved to JSON in database (MongoDB), with YAML for org export/import.

**Early artifact. Core idea (auto-generation) retained. Specific tech (Postgres, YAML definitions) later revised. No Finding 0-class deviation.**

### From `2026-03-30-vision-session-2-checkpoint.md`:
or Ambiguities

Listed in artifact: Tier 3 pricing, website alignment, product showcases, customer migration, competitive positioning, revenue projections.

**Session checkpoint. Summarizes session 2 outputs. No new architectural-layer claims beyond the summarized artifacts. Next phase: design.**

### From `2026-04-02-core-primitives-architecture.md`:
or Ambiguities

Listed in artifact:
1. Interaction Host detailed design — RESOLVED in 2026-04-10-realtime-architecture-design.md as harness pattern
2. Routing rule code extension — eventually watches not code
3. Hot/cold message collection split — resolved as message_queue + message_log
4. Admin CLI for observability — implemented per Phase 1-5 specs
5. Testing patterns — resolved in spec

**IMPORTANT — this artifact's claim that "real-time and async use the same associate pattern" was refined, not contradicted, by 2026-04-10-realtime-architecture-design.md:**
- SAME pattern: CLI-based, skill-driven, deep-agent-based.
- DIFFERENT deployment: separate harness image per (kind, framework) combo.
- So the pattern stays the same; the DEPLOYABLE topology differs.

**Finding 0 connection:**
- This artifact emphasizes "same associate pattern for async and real-time" — the implementation respects this (both currently run in-kernel). But the 2026-04-10 artifact refines this to "same pattern, separate harness images outside kernel."
- The Phase 2-3 spec interpreted "same pattern" as "run in one place (kernel)" — missing the 2026-04-10 refinement.

**No new Finding 0-class deviation introduced here. This artifact's message architecture matches what's built; the real-time unification claim was later refined to harness-per-framework, not contradicted.**

### From `2026-04-02-design-layer-4-integrations.md`:
or Ambiguities

- Credential storage — at this stage "config" dict; later explicitly moved to AWS Secrets Manager via `secret_ref`.
- Credential resolution priority — later explicitly defined (actor → owner → org).
- Webhook inbound dispatch — not detailed here; later formalized in Phase 3 spec.

**No Finding 0-class deviation.** This artifact's adapter pattern is the foundation of what's implemented. The evolution (Integration → primitive #6 with ownership model, `secret_ref`, provider_version) is consistent refinement, not contradiction. Implementation matches.

**Web operator treatment**: "deep agent associates with browser sandbox — same harness as all associates" — this reinforces that when harnesses are eventually built (Finding 0 fix), web operators share the same harness pattern. Current code has no web operators, no harnesses — consistent with Finding 0.

### From `2026-04-02-design-layer-5-experience.md`:
or Ambiguities

- Should ViewConfig be a first-class entity or handled via auto-generation from role? — later resolved: pure auto-generation for MVP.
- Real-time architecture — later refined.

**No Finding 0-class deviation.** UI-as-API-consumer principle retained; ViewConfig abstraction deferred; real-time moved from RabbitMQ to Change Streams. Implementation matches the later refinements.

### From `2026-04-02-implementation-plan.md`:
or Ambiguities

- Mixin vs uniform Entity class — resolved same day in core-primitives-architecture.md (uniform).
- RabbitMQ vs MongoDB for messages — resolved same day in core-primitives-architecture.md (MongoDB).
- Daytona vs local Docker for sandbox — later resolved: Daytona candidate but implementation has no sandbox (Finding 0 consequence).

**No Finding 0-class deviation from this artifact specifically.** It's a phasing plan that was later refined to the 8-phase structure. The current implementation follows the refined 8-phase structure. This artifact's "Phase 3 = associate runtime + integrations" became the final Phase 2 + Phase 3 — also consistent with how things were built.

### From `2026-04-03-message-actor-architecture-research.md`:
or Ambiguities

- RabbitMQ vs MongoDB-only for messaging → resolved: MongoDB-only. "One database, one transaction boundary. Entity+message atomicity is trivial with MongoDB transactions. No dual-write problem."
- Hybrid pattern (RabbitMQ routing + MongoDB work queue) was later dropped in favor of single-queue simplicity.

**No Finding 0-class deviation introduced here.** The message architecture principles (outbox, selective emission, correlation, cascade limit, idempotency, atomic claim) are all retained in the final architecture. The RabbitMQ-as-event-bus recommendation was later rejected in favor of MongoDB-only messaging. Implementation matches.

This artifact informs the Phase 1 save_tracked() and message queue design.

### From `2026-04-07-challenge-developer-experience.md`:
or Ambiguities

Questions raised and later resolved:
- Routing rule format → watches
- Observability → OTEL + changes + correlation IDs
- YAML vs Python entity definitions → JSON data + dynamic classes
- Testing patterns → spec layers
- Timeline — build attempts showed actual pace

**No Finding 0-class deviation identified by this challenger.** The developer-experience review did not surface the harness pattern issue (that emerged later from the real-time session). This challenge focused on framework ergonomics.

### From `2026-04-07-challenge-distributed-systems.md`:
or Ambiguities

- **Outbox pattern vs. direct message_queue write in transaction**: Craig later chose DIRECT write (no separate outbox, per round-1 architecture ironing). Equivalent reliability, one fewer collection.
- **Cascade depth hard-stop value**: 10 mentioned here, confirmed in later artifacts.
- **Optimistic concurrency** (version field): mentioned here, confirmed in core-primitives-architecture hardening requirements.

**Supersedence note**:
- All 10 recommendations survive. Several were modified in implementation:
  - #1 Transactional writes → implemented as `save_tracked()` (confirmed in spec; later regressed in shakeout; later fixed per comprehensive audit).
  - #2 Visibility timeout → implemented.
  - #3 Cascade depth → implemented with max depth 10.
  - #4 Idempotent handlers → required by design; implementation discipline.
  - #5 Correlation/causation IDs → implemented.
  - #6 Optimistic concurrency → implemented via version field + conditional updates.
  - #8 Hot/cold split → implemented (message_queue + message_log).
  - #9 MessageBus abstraction → partial (kernel writes directly; Bus interface for potential broker migration).
  - #10 Change Streams → implemented for UI real-time; polling replaced in events stream.

### From `2026-04-07-challenge-insurance-practitioner.md`:
or Ambiguities

- **How much insurance domain sits in the kernel vs. per-org data** — RESOLVED: zero insurance in kernel. All per-org.
- **How to support N-level MGA/agent hierarchies** — per-org domain entities (Agency, Agent, Producer) with relationships and access control.
- **How to handle state-specific compliance regimes** — per-org rules + lookups + required-field rules.

**Supersedence note**:
- The insurance domain concerns ARE addressed by the final architecture:
  - Domain-agnostic kernel means all insurance specifics are per-org data.
  - Flexible entity framework (EntityDefinition in MongoDB) means per-customer entity schemas.
  - Rules + Lookups + Required-field rules allow per-state / per-product configuration.
- But Finding 0 (agent execution in kernel) MEANS the agent reasoning capacity is limited — a 20-iteration LLM loop cannot handle the cascades of insurance edge cases this pressure test lists (rerig → extended binder → carrier change → retroactive endorsement).
- Full deepagents in harness (per design) is needed to handle these workflows; current implementation doesn't support that.

### From `2026-04-07-challenge-mvp-buildability.md`:
or Ambiguities

- **Timeline**: the subsequent 6-phase implementation plan compressed to 6 weeks. The final 8-phase white paper extended substantially. In practice (Phase 6 dog-fooding pending, Phase 7 first customer pending), this pressure test's estimate is proving directionally correct.
- **Scope**: the 44-entity count was reduced significantly in subsequent artifacts. The current kernel has ~7 kernel entities + ability to configure domain entities via CLI — NOT 44 kernel entities. The domain can have many entities per deployment (44+), but none are in kernel code.

**Supersedence note**:
- The 5-entity MVP proposal was NOT literally adopted (the kernel entity set is 7, reflecting architectural needs).
- The "build 3-5 by hand, extract the generator" principle WAS adopted: the 7 kernel entities are hand-written (Python classes with `KernelBaseEntity`); domain entities use the CLI-driven dynamic definition pattern.
- "No full deep-agent runtime for MVP" — PARTIALLY. The current code has `_execute_reasoning` in kernel (not deep-agent with middleware). Full deepagents is deferred to harness pattern (Finding 0).
- "Find friendly agency for dogfooding" — reflects in Phase 7 (GIC).

### From `2026-04-07-challenge-realtime-systems.md`:
or Ambiguities

- At time of writing (April 7), the harness pattern wasn't yet formalized. The Interaction Host was the placeholder concept.
- Actor-entity affinity mechanism: surfaced as concept, resolved as **Attention** entity in 2026-04-10-realtime-architecture-design.md.

**Supersedence note**: All recommendations in this pressure test SURVIVE. The Interaction Host concept evolved into the harness pattern. Finding 0 is the architectural-layer deviation between this pressure test's guidance and the current implementation.

### From `2026-04-08-actor-references-and-targeting.md`:
or Ambiguities

- **Tension with kernel-vs-domain.md**: that artifact listed Assignment as a primitive; this artifact says "Assignment is not a primitive." **Resolution**: Assignment-as-relationship is a common pattern but not a kernel primitive. Kernel entities are still 6 (later 7 with Session).
- **Scope qualifier on watches** (`scope: actor_context`) introduced later (EventGuard retrace) bridges this design with the target-from-field rejection: scope resolution happens in watch eval but uses `field_path` on the watch definition, not kernel-level actor-ref inference.

**Supersedence note**:
- "Assignment is not a primitive" SURVIVES.
- "Messages target roles; context enables filtering" MOSTLY survives but CLARIFIED: **scoped watches** (2026-04-10-realtime-architecture-design.md) add emit-time scope resolution via `field_path` — a middle path between pure role targeting and kernel actor resolution. The design is: watch declares `scope: actor_context` with `field_path: owner_actor_id`; evaluator reads that field from the event entity and writes `target_actor_id` on the message.
- So the current final design is: target_actor_id IS populated from watch scope configuration, but through declarative `field_path` on the watch, not kernel magic.

### From `2026-04-08-actor-spectrum-and-primitives.md`:
or Ambiguities

Listed at end of artifact (4 open questions, resolved in primitives-resolved.md):
1. Minimal definition of Actor
2. How does a Role declare "what comes to me" → watches
3. Where does entity end and actor begin → entity = universal, actor = per-org
4. Scheduled task = actor with time-based trigger → yes

**Supersedence note**:
- "Everything is CLI" principle SURVIVES.
- Actor-skill-interpreter model SURVIVES.
- Three skill modes SURVIVE.
- **Integration collapse REVERSED** — Integration reinstated as primitive #6 two days later.
- "Actor location not specified" → CLOSED as "harness image outside kernel" per April 10 realtime-architecture-design.

### From `2026-04-08-entry-points-and-triggers.md`:
or Ambiguities

- **Channel activation**: artifact says "Interaction entity created → watch matches → actor triggered." This is partially superseded: real-time channels also use **direct invocation in parallel** (per round 1 ironing — queue entry + direct invoke simultaneously) to avoid polling latency.
- **Scheduled work location**: unspecified here. Per realtime-architecture-design, async scheduled associates live in the async-deepagents harness. Current code has them as kernel Temporal activities → Finding 0.

**Supersedence note**:
- 6 entry points + 3 trigger types SURVIVE as the canonical set.
- "Channels are entry points, not trigger types" SURVIVES.
- Real-time latency concern resolved via direct invocation parallel path.
- Schedule trigger as synthetic queue item SURVIVES (per round-1 ironing).

### From `2026-04-08-kernel-vs-domain.md`:
or Ambiguities

- **"Start bare" is a guiding principle but doesn't enumerate the tipping point.** When does something become universal enough to promote? Not specified.
- **The 6 primitives here** will become:
  - White paper-era: 6 primitives = Entity, Message, Actor, Role, Organization, Integration (Assignment becomes an Entity relationship pattern, not a top-level primitive). NOTE: Assignment is demoted or integrated differently in later artifacts.
  - 7 kernel entities (Organization, Actor, Role, Integration, Attention, Runtime, Session)
- **Supersedence note for vision map**:
  - "Actor identity is OS-level" — SURVIVES.
  - "Assignment as universal OS capability" — appears to be partially absorbed into Role + Actor references in later artifacts; need to verify in later retraces whether Assignment remains a distinct top-level primitive or becomes a relationship pattern.
  - "Multi-assignment" — survives; implemented via context + actor references.
  - "Start bare, add later" — SURVIVES as a principle.

### From `2026-04-08-pressure-test-findings.md`:
or Ambiguities

**Resolved in later artifacts** — already addressed per this note. Nothing architecturally open.

**Finding 11 (Assignment lifecycle)** still somewhat open at MVP scope: "simple assignment" is sufficient; richer lifecycle = later. Need to verify in Pass 4 whether assignment-at-claim-time race-condition check was implemented.

**Supersedence note**:
- Finding 10 bulk ops initial proposal (batch_id + coalescing window) is SUPERSEDED by 2026-04-10-bulk-operations-pattern.md (bulk as a kernel pattern/workflow) + 2026-04-13-simplification-pass.md (coalescing removed entirely from kernel, UI-only).
- All other findings survive.

### From `2026-04-08-primitives-resolved.md`:
or Ambiguities

**Deliberately open at this point:**
- Where the "LLM interpreter" runs — not specified. Left open for later artifacts.
- Integration collapse vs. Integration as primitive — resolved the OTHER way two days later (Integration IS a primitive).

**Potential trap**: This artifact's "integration collapse" claim was REVERSED. Reading artifacts chronologically, one might incorrectly carry forward the "one primitive, not two" position. The correct later resolution (2026-04-10-integration-as-primitive.md + white paper) is: 6 primitives including Integration.

**Supersedence note for vision map**: "The wiring IS the set of watches across all roles" survives all the way through. Core to the design. Not superseded.

### From `2026-04-08-session-3-checkpoint.md`:
or Ambiguities

At end of session 3, all open:
- Wiring question (resolved in session 4 as watches on roles)
- Testing/debugging CLI
- Declarative system definition
- Bulk operations
- Rule composition details
- Build order + acceptance criteria
- Stakeholder engagement

**Supersedence note**:
- 2 implementation primitives → evolved to 6 structural primitives (session 4 + 5).
- 10 hardening requirements SURVIVE.
- 4 conceptual primitives → evolved to 6 (add Organization + Integration).
- Implementation plan phases → evolved to 8.

### From `2026-04-09-architecture-ironing-round-2.md`:
or Ambiguities

- **Capability activation lifecycle** (enable/disable, multiple versions) — deferred.
- **Context depth for message references** — resolved in round 1 (configurable per watch, default shallow).

**Supersedence note**: All 5 resolutions SURVIVE into final architecture.

### From `2026-04-09-architecture-ironing-round-3.md`:
or Ambiguities

- **Cache invalidation timing**: "immediately invalidate" — stated as immediate; implementation may be eventually-consistent if Change Streams are used (Pass 2 noted Change Stream-based invalidation is the final design).
- **Cascade guard depth threshold**: "depth 1" for self-referencing bootstrap cascades. Is depth 10 still the max globally? Yes (from Phase 2-3 spec).
- **Schema evolution for existing data**: "Pydantic handles missing fields with defaults" — relies on Pydantic behavior. Field removal leaves data in DB but ignored.
- **Entity class file on disk vs. DB**: this artifact says "Updates the Python class file" for `indemn entity modify`. That contradicts "Beanie for everything, load definitions from DB at startup" in 2026-04-09-data-architecture-solutions.md. Later artifacts resolve this as **entity definitions live ONLY in MongoDB (`entity_definitions` collection)** and classes are created via `create_model` at startup — no Python class files on disk for domain entities.

**Supersedence note**:
- "One save = one event" — SURVIVES. Core invariant.
- "@exposed methods are the emission boundary" — SURVIVES.
- "Queue Processor" name — SURVIVES. Implemented as `kernel/queue_processor.py`.
- "Entity class files on disk" — SUPERSEDED. Entity definitions live in MongoDB only.
- "message batch_id coalescing window" — SUPERSEDED by simplification-pass.md (UI-only coalescing).
- "Changes collection = version history" — SURVIVES.
- "JSON-only conditions" — SURVIVES. One evaluator shared by rules + watches.

### From `2026-04-09-architecture-ironing.md`:
or Ambiguities

- **Entity class file on disk vs. DB**: round 1 says "CLI generates Python class file"; data-architecture-everything-is-data evolves this to MongoDB-only (dynamic class creation at startup). The final implementation has BOTH: kernel entity class files on disk (static), domain entities only in MongoDB (dynamic).
- **Generic workflow location**: deferred.

**Supersedence note**:
- All 7 resolutions SURVIVE.
- "CLI generates Python class file" → PARTIALLY SUPERSEDED (only for kernel entities; domain entities are DB-only).
- Real-time direct invocation parallel pattern SURVIVES (per Phase 2-3 spec's direct_invoke endpoint).
- Schedules-as-queue-items SURVIVES.

### From `2026-04-09-capabilities-model-review-findings.md`:
or Ambiguities

Resolved in subsequent artifacts:
- Multi-entity atomicity → implemented via save_tracked wrapping multiple entity saves in one txn.
- Watch vs processing_status → watches are the wiring (consolidated-architecture, white paper).
- Ball-holder computed field → documented in computed field scope (documentation-sweep item 6).
- Draft consolidation → domain skill concern.

**Supersedence note**: All 8 findings SURVIVE into the final architecture. The 27 GIC gaps are tracked into the gap identification + consolidated specs.

### From `2026-04-09-consolidated-architecture.md`:
or Ambiguities

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

### From `2026-04-09-data-architecture-review-findings.md`:
or Ambiguities

All 14 findings RESOLVED in data-architecture-solutions. Implementation status per Pass 2:
- #1 OrgScopedCollection: implemented (noted in Pass 2).
- #2 AWS Secrets Manager: Integration entity has `secret_ref` field (from Phase 2-3 spec).
- #3 Skill content hashing: implemented (`kernel/skill/integrity.py`).
- #4 Rule action injection: Phase 0-1 spec excludes state fields from set-fields.
- #5 Sandbox: absent (Finding 0 consequence).
- #6 Changes hash chain: implemented but verify is broken (shakeout Finding 14).
- #7 Environment isolation: separate clusters already in place.
- #8 Dynamic entity limitations: handled per design.
- #9 Hot-reload: dual base class solution, implemented during shakeout.
- #10 Platform upgrade: CLI scaffold exists.
- #11 Seed templates: partial (basic seed loading exists).
- #12 Schema migration: implemented (section 1.29 of Phase 0-1 spec).
- #13 Thundering herd: Temporal worker config (from infrastructure artifact).
- #14 Queue Processor HA: deployment platform + monitoring.

**Supersedence note**: All 14 findings SURVIVE. Data-architecture-solutions.md is the resolution artifact.

### From `2026-04-09-data-architecture-solutions.md`:
or Ambiguities

- **Skill version approval workflow** — per-org opt-in; not specified in detail (admin role approves). Left for implementation.
- **Capability schema versioning migration scripts** — the pattern is stated; actual migration-script format/location left for implementation.
- **Daytona deployment model** — external service; integration pattern not detailed here (tied to the harness pattern specified later).
- **Where OrgScopedCollection is instantiated** — per-request or per-connection? Implementation detail.

**Finding 0 relevance**:
- **Daytona sandbox is absent in current implementation** — consequence of Finding 0 (agent execution in kernel Temporal worker has no sandbox wrapping).
- **AWS Secrets Manager for credentials** — Phase 2-3 spec said credentials live in AWS Secrets Manager per `secret_ref`. Need to verify in Pass 4 code audit whether adapters actually use Secrets Manager.
- **Hash chain verification** is flagged in Pass 2 as unresolved — `kernel/changes/hash_chain.py` has serialization mismatch.

**Supersedence note for vision map**: All 14 solutions survive. Data architecture is the foundation for Phase 0-1 — there's no later artifact that supersedes these solutions at the architectural level.

### From `2026-04-09-session-4-checkpoint.md`:
or Ambiguities

Listed as "STILL OPEN" at end of session 4:
- GIC pipeline full retrace against final architecture (done in session 5)
- EventGuard, CRM traces (done in session 5)
- Testing/debugging CLI (gap session #3/4 in session 6)
- Declarative system definition
- Bulk operations (designed session 6)
- Rule composition details (session 5 + consolidated specs)
- No single source of truth document (white paper in session 6)
- Simplification pass (session 6)
- Implementation build order (white paper Section 10, phase specs)
- Stakeholder engagement
- First entity to hand-build

**Supersedence note**: All session 4 decisions SURVIVE. Session 5 adds Integration as 6th primitive, Attention + Runtime as new bootstrap entities, harness pattern, scoped watches, watch coalescing, owner_actor_id, handoff mechanics. Session 6 adds authentication design (Session as 7th kernel entity), base UI operational surface, bulk operations pattern, simplification pass (removes watch coalescing from kernel), documentation sweep.

### From `2026-04-09-temporal-integration-architecture.md`:
or Ambiguities

Listed in the artifact itself:
1. One workflow per actor vs per pipeline — **resolved later as per-message workflow** (ProcessMessageWorkflow generic).
2. Human queue as Temporal query — practical at scale? **Resolved**: queue stays in MongoDB (unified-queue design supersedes).
3. Outbox poller vs. MongoDB Change Streams — **resolved in favor of optimistic dispatch + sweep** per Phase 2-3 spec.
4. Simple operations — is Temporal overhead justified? **Resolved**: yes for durability; MVP scheduled tasks use app-level cron.
5. Temporal as single point of failure — **accepted risk**; entity saves + human actors continue if Temporal down.

**Supersedence note for vision map**:
- "Temporal replaces hand-rolled durable execution" — SURVIVES.
- "Outbox for entity → Temporal bridge" — REPLACED by optimistic dispatch + sweep.
- "Workers are kernel processes" — SUPERSEDED; workers are harness images one day later.
- "Scheduled tasks via Temporal Schedules" — deferred post-MVP; Phase 2 spec uses app-cron.

### From `2026-04-09-unified-queue-temporal-execution.md`:
or Ambiguities

- **Workflows per role vs. per pipeline** — resolved as generic `ProcessMessageWorkflow`.
- **Multi-org task queue sharing** — not discussed. (Phase 2-3 spec uses single `"indemn-kernel"` queue for everything, not per-Runtime as realtime-architecture-design later specifies.)
- **Worker deployment location** — DELIBERATELY OPEN in this artifact. This openness is what lets the Phase 2-3 spec interpret it as "kernel process" without contradicting this design doc. But the realtime-architecture-design (next day) closes the open question as "harness image outside kernel."

**Supersedence note for vision map**:
- "Queue = MongoDB, execution = Temporal" — SURVIVES, core invariant.
- "Associates are employees" — SURVIVES.
- "Outbox poller pattern" — superseded by optimistic dispatch + sweep backstop.
- "Worker location" — DELIBERATELY OPEN here; CLOSED by realtime-architecture-design as "harness image outside kernel." Specs that say "kernel process" contradict the later closure.
- The "Optimization" closing note → becomes the Phase 2-3 MVP mechanism.

### From `2026-04-10-crm-retrace.md`:
or Ambiguities

Deferred by the retrace:
- Exact privacy policy default per Integration type (resolved in documentation-sweep: actor-owned = metadata_shared, org-owned = full_shared).
- S3 IAM policy structure (infrastructure).
- Whether query capabilities need a special marker (resolved: just @exposed methods that are read-only).
- Whether "Associates with owner_actor_id" needs a new entity type (resolved in documentation-sweep: Associate is a subtype of Actor; owner_actor_id is a field on that subtype).

**Supersedence note for vision map**:
- **`owner_actor_id` pattern** — SURVIVES, formalized in documentation-sweep + authentication-design.
- **Content visibility policy** — SURVIVES, formalized in documentation-sweep.
- **Query capabilities pattern** — SURVIVES as a documentation note, not architectural change.
- **Multi-source entity enrichment** — SURVIVES as a pattern.
- **Kernel domain-agnosticism** — SURVIVES (validated).

**Finding 0 implication**: Phase 6 dog-fooding is blocked by Finding 0. Not just the kernel API endpoint assistant — every scheduled CRM associate would need to run in the async harness that doesn't exist.

### From `2026-04-10-eventguard-retrace.md`:
or Ambiguities

Open-in-retrace (resolved in later artifacts):
- Actor-context scope semantics — resolved via Attention entity + scoped watches (2026-04-10-realtime-architecture-design.md).
- Webhook dispatch — resolved (documentation-sweep + Phase 2-3 spec).
- Bulk operations — resolved (bulk-operations-pattern).
- Internal vs external entities — resolved (documentation-sweep item 5).
- Real-time crash recovery UX — left open; degraded-but-acceptable UX accepted.

**Finding 0 direct quotes from this artifact (relevant to discrepancy report)**:
- Phase 2 (consumer interaction begins): "Channel infrastructure (WebSocket server) receives the connection."
- Phase 10 (real-time update to consumer): "The Quote Assistant associate is still in a live conversation with the consumer. How does it find out the policy is done so it can tell the consumer 'All set!'?" Answer: Temporal signals bridged from watches (Approach 1, recommended).
- These phases require the chat-harness. Not implemented in current code.

**Supersedence note**:
- All findings survive in post-retrace artifacts and specs.
- Watch coalescing is retained here (for bulk venue creation ops queue) but later REMOVED from kernel (2026-04-13-simplification-pass.md). EventGuard's 351-venue bulk-create would still work without coalescing — UI groups by correlation_id.

### From `2026-04-10-gic-retrace-full-kernel.md`:
or Ambiguities

- **Worker location** — implicit in "workflow executes the command"; made explicit one day later in realtime-architecture-design. Retrace author did NOT surface this as an issue; they took "workflow runs the command" as valid at any deployment location.
- **Multi-LOB drafts** — domain skill concern; kernel supports; skill decides.
- **Queue health tooling** — data exists, CLI surface to be defined.

**Supersedence note**:
- Watch coalescing as kernel feature (Finding 1): REMOVED from kernel per simplification-pass (now UI-only).
- Ephemeral locks (Finding 3): RESOLVED/GENERALIZED as Attention entity (realtime-architecture).
- Computed field scope (Finding 6): RESOLVED as item 6 in documentation-sweep (on method activation config, not Lookup).
- All other findings survive.
- **GIC pipeline structure SURVIVES**. The retrace is the canonical B2B email-pipeline reference.

### From `2026-04-10-session-5-checkpoint.md`:
or Ambiguities

Listed as "STILL OPEN":
- Design sessions remaining: bulk operations, pipeline dashboard + queue health, authentication (all done in session 6)
- Documentation sweep (items 4, 5, 6, 11, 12 — done in session 6)
- Simplification pass (done in session 6)
- Spec writing (white paper + consolidated specs in session 6 / April 13-14)
- Stakeholder engagement (ongoing)

**Supersedence note**:
- Session 5 decisions SURVIVE as authoritative.
- **The three-harness-image architecture is Finding 0's reference design.** This session explicitly specifies it.
- Subsequent drift (infrastructure artifact missing async-deepagents, Phase 2-3 spec placing `process_with_associate` in kernel) is where the implementation diverged from this session's design.

### From `2026-04-13-documentation-sweep.md`:
or Ambiguities

Deferred by this artifact:
- Exact S3 IAM policy structure
- UI rendering of content visibility indicators
- Bulk content migration tooling
- Content search across visibility boundaries (answered NO for MVP — searchable metadata only)

**Supersedence note for vision map**:
- All 5 clarifications survive. They're canonical.
- The default-assistant auth pattern (inherits user Session JWT via harness) is a load-bearing statement for Finding 0b.
- Owner-bound associate pattern requires the async-deepagents harness — currently missing in implementation (Finding 0 consequence).

### From `2026-04-13-infrastructure-and-deployment.md`:
or Ambiguities

Listed as "What's Deferred":
- ECS migration: Railway may be sufficient long-term.
- Auto-scaling: manual replica management for now.
- Multi-region deployment: single region (US East).
- Redis: not in stack; additive if needed.
- Service mesh / API gateway: Railway networking sufficient.

**The CRITICAL ambiguity this artifact introduces**:
- Is there a third harness image for async? The artifact implies "additional harness images added as new Runtime kind+framework combinations are needed" but doesn't list async-deepagents. The realtime-architecture-design explicitly requires it.
- **Pass 2 already confirmed Finding 0 at spec + code + infra levels. This infrastructure document is where the drift crept in at the infra-design level.**

**Supersedence note for vision map**:
- **5 services (or 6 with async-deepagents included)** — reconcile with realtime-architecture-design: authoritative is 6 services.
- **Trust boundary specification** — SURVIVES (exactly matches white paper).
- **CLI unification (always API mode)** — SURVIVES.
- **Optimistic + sweep dispatch** — SURVIVES. Implemented in Phase 2-3 spec.
- **Railway + US East + Atlas + Temporal Cloud** — SURVIVES.
- **WebSocket keepalive** — SURVIVES (requirement for harnesses + UI).
- **Cloudflare before external customers** — SURVIVES as operational requirement.
- **The async-deepagents harness must be present** per realtime-architecture-design; the omission here is an artifact drafting error, not a supersedence.

**Vision-map implication**: The final authoritative infrastructure design has 6 services, 4 images (`indemn-kernel`, `indemn-ui`, `indemn/runtime-voice-deepagents`, `indemn/runtime-chat-deepagents`, `indemn/runtime-async-deepagents`). Kernel Temporal Worker handles ONLY kernel workflows (Bulk, Deploy, HumanReview). Async associates run in the runtime-async image.

### From `2026-04-13-remaining-gap-sessions.md`:
or Ambiguities

- **Async-deepagents harness omission**: same as infrastructure-and-deployment. The repository structure in this artifact lists voice + chat + NOT async. **This is a cross-artifact drafting omission that directly caused Finding 0.**
- **Real-time implementation**: deferred to per-component spec (not in white paper). Phase 5 consolidated spec's voice harness example is the closest thing to an implementation spec — chat + async remain unimplemented.

**Supersedence note**:
- 17 decisions + universal pattern + 8-step process SURVIVE.
- **Harness directory listing is incomplete**: per realtime-architecture-design, 3 images (voice, chat, async) are required. This artifact + infrastructure artifact both show only 2. For the vision map, the authoritative answer is 3 (per the earlier, more thorough design artifact).
- Tier 2 as primary onboarding path SURVIVES.
- Coexistence model (no bridge) SURVIVES.

### From `2026-04-13-session-6-checkpoint.md`:
or Ambiguities

Listed as "next phase work":
- Write spec document (done April 13-14)
- Derive build sequence (white paper §11)
- Stakeholder engagement (ongoing)
- Build first use case (Phase 6-7 pending)

**Supersedence note**:
- Session 6 decisions SURVIVE as final design phase. White paper follows.
- **Watch coalescing removal** is the key simplification — verified in shakeout.
- **Session ≠ Session 6 checkpoint; Session = 7th kernel entity** (authentication-design).
- Harness pattern remains as locked in session 5. This checkpoint confirms nothing about harness pattern changed.
- **But**: infrastructure-and-deployment artifact (written in session 6) has the async-deepagents omission that propagated Finding 0 into the specs.

### From `2026-04-14-impl-spec-gaps.md`:
or Ambiguities

**Meta-gap**: This 90-gap analysis asked "what mechanisms are missing?" and was thorough. It did NOT ask "are the mechanisms in the right layer?" The Pass 2 audit (2026-04-16) explicitly called this out as the methodology gap. This file is PROOF of the gap:
- 90 gaps about WHAT needs to exist
- ZERO gaps about WHERE the existing mechanisms should live

**Supersedence note**:
- All 90 gap resolutions SURVIVE. They're correct at the mechanism level.
- None of them are superseded; all are integrated into the consolidated specs.
- **The methodology of this gap analysis is what's superseded** — Pass 2 demonstrated that layer-level verification was needed on top.

**Vision-map implication**: The consolidated specs have 90 correctly-resolved mechanism gaps + 2 un-caught architectural-layer deviations (Finding 0 + 0b). The gap analysis verified mechanisms; Pass 2 verified layers. Both are needed for the full picture.

### From `2026-04-14-impl-spec-phase-0-1-addendum.md`:
or Ambiguities

None unique to addendum. All content SURVIVES into consolidated spec.

**Supersedence note**: SUPERSEDED by consolidated spec. This addendum's content is embedded there.

### From `2026-04-14-impl-spec-phase-0-1.md`:
or Ambiguities

Everything from the base spec either:
- SURVIVES in the consolidated spec (all architecture decisions)
- Was addressed by the addendum (Attention, Runtime, Session full specs, schema migration, rule validation, etc.)
- Was resolved via the 90-gap analysis and added to the consolidated spec (CLI auto-registration, org lifecycle, audit verify, skill approval, credential rotation).

**Supersedence note**: This base spec is SUPERSEDED by the consolidated spec. For all analysis purposes, use the consolidated spec note as the authoritative reference.

### From `2026-04-14-impl-spec-phase-2-3.md`:
or Ambiguities

- All 22 gaps from gap analysis SURVIVE resolution in consolidated spec.
- **Finding 0 deviation (agent execution in kernel) is NOT flagged as a gap** — it's baked into both this spec and the consolidated spec.

**Supersedence note**: SUPERSEDED by consolidated. The Finding 0 deviation EXISTS IN BOTH.

### From `2026-04-14-impl-spec-phase-4-5.md`:
or Ambiguities

Phase 4-5 ships with Finding 0b baked in + only voice harness example. The gap analysis identified 23 mechanism-level gaps but did NOT flag:
- Assistant missing tools
- Chat harness missing from spec
- Async harness missing from spec

These are layer-level issues that the gap methodology missed.

**Supersedence note**: SUPERSEDED by consolidated. Finding 0b is in both versions.

### From `2026-04-14-impl-spec-phase-6-7.md`:
or Ambiguities

- Phase 6 parallel-run mechanism (resolved in consolidated + gap-resolutions).
- Phase 7 GIC migration concrete steps — resolved via coexistence model (no bridge; parallel runs).
- **Blocking issue for both**: Finding 0. The harnesses don't exist. Dog-fooding cannot happen on in-kernel agent execution (no CRM Assistant can run, no personal syncs can run as intended).

**Supersedence note**: SUPERSEDED by consolidated. Phase 6/7 are operational blueprints; their execution is blocked by Finding 0 until harnesses are built.

### From `2026-04-14-impl-spec-verification-report.md`:
or Ambiguities

**The verification report confidently says specs are ready to build.** It does NOT identify Finding 0 (agent execution in wrong layer). Why?

- The report checked white-paper mechanism completeness, not architectural-layer placement.
- The report checked spec internal consistency, not spec-vs-design-artifact at layer level.
- The report validated 90+ gap resolutions, but the gaps were all mechanism-level, not layer-level.

**This artifact is the primary example of the methodology gap that motivated Pass 2.** The verification was genuine and thorough, but it took the consolidated specs as its architectural authority and checked implementation inside the spec's self-consistency. It did not step out to the source design artifacts (realtime-architecture-design, integration-as-primitive, infrastructure-and-deployment, white paper) to ask "are these specs in the right architectural layer?"

**Supersedence note for vision map**:
- All 29 verification findings SURVIVE as spec corrections.
- This artifact itself is NOT superseded — it's a verification checkpoint.
- But its "specs are ready to build from" conclusion is **qualified** by Finding 0: the specs are ready at the field/mechanism level but deviate at the architectural-layer level for agent execution and the assistant.
- The Phase 2-3 spec §2.4 and Phase 4-5 spec §4.7 Finding 0 issues exist IN the verified specs and were NOT flagged by this verification.

**Recommendation**: the vision map should treat this artifact as the "spec internal consistency" reference; the Pass 2 audit is the "spec vs source design at layer level" reference. Both are needed.

### From `2026-04-15-shakeout-session-findings.md`:
or Ambiguities

**Untested in shakeout** (noted as remaining):
- WebSocket real-time updates during live entity changes
- UI entity creation form (submit new entity)
- Org deploy (promote source → target)

**Finding 18's proposed fix** (add tools to kernel endpoint) is a LOCAL fix that restores functionality but entrenches Finding 0b architecturally. The deeper fix requires building the chat harness.

**Finding 14 (hash chain)** still open; Pass 2 noted as unresolved.

**Supersedence note for vision map**:
- The 13 fixed findings are architecturally correct fixes at the mechanism level.
- **Finding 18 is a symptom of Finding 0b**; the shakeout session surfaced it but didn't trace to architectural root cause.
- **Finding 15 (generic update bypasses state machine)** is a spec-level bug — the generic `PUT` endpoint should not accept state-machine fields. Should be fixed in the kernel registration code.
- **Finding 16 (bootstrap bypasses save_tracked)** is a minor invariant violation in `platform_init` — acceptable for bootstrap but should be flagged.
- **Finding 14 (hash chain)** is a compliance-critical correctness bug.

**Vision-map implication**: Shakeout confirmed the kernel core loop works end-to-end. But the spec's Finding-0b deviation (assistant as kernel endpoint without tools) surfaces immediately in practice — confirming this is not a hypothetical layer problem but a working implementation that can't do the assistant's job.

### From `2026-04-15-spec-vs-implementation-audit.md`:
or Ambiguities

**The methodology gap this audit demonstrates**:
- The audit compared spec vs implementation at the mechanism level thoroughly (13 deviations identified).
- The audit did NOT ask whether the spec's mechanisms were in the right architectural layer.
- Finding 0 / 0b root causes (agent execution location) were not surfaced because the audit started from the consolidated specs as authoritative, not from the source design artifacts.
- The comprehensive audit (same day) and Pass 2 audit (next day) closed this gap by cross-referencing specs back to source design artifacts.

**Priority recommendations from this audit**:
1. Fix D-02 (transaction scope) — #1 invariant violation.
2. Fix D-03 (assistant tools) — biggest functional gap. (Pass 2: better fix is the harness pattern.)
3. Document D-01 (dual base class).
4. Fix D-07 (rule group status).
5. Fix D-08 (hash chain verification).
6. Fix D-04 (explicit state field name).
7. D-11 (watch cache) — consider Change Stream for multi-instance.

**Supersedence note for vision map**:
- **D-02 is confirmed RESOLVED** per Pass 2 audit priority 3.
- **D-03 is Finding 0b** per Pass 2 — the proper resolution is the chat-harness pattern, not local tools addition.
- **D-04, D-07, D-08** remain open.
- **D-01 (dual base class)** — design decision that survives in code; spec should acknowledge.
- All other D-xx are either resolved or minor.

### From `architecture.md`:
or Ambiguities

- **Status of Intake Manager vs GIC Submission unification** — open at time of writing, addressed by the new OS's generic entity framework.
- **22 entities → 70 entities**: domain model research flagged as DRAFT, needs review for redundancies. Status at time of writing: "should be validated with Ryan and Dhruv during stakeholder engagement."
- **Three tiers of platform usage** — MVP doesn't ship all three; Tier 2 is primary per gap sessions.

**Supersedence note**:
- "AI agents are a CHANNEL" thesis SURVIVES.
- "5 core concepts" map to later primitives: Domain Objects → Entity, Capabilities → entity methods, Workflow Templates → Skills, Channels → entry points, Customer Configuration → rules + lookups.
- 70-entity domain catalog NOT directly in kernel (kernel has 7 kernel entities; domain entities are per-org data).
- "Not a migration — new platform alongside current" SURVIVES.
- Post-bind / financial gap (policy/commission/claim/payment) — still not in kernel; to be implemented as per-org domain entities when customers need them.

### From `business.md`:
or Ambiguities

- **Moat articulation** — still "uninspired" per leadership acknowledgment. Craig's domain-model thesis is the default.
- **Customer OS adoption** — 67% of WON customers "Never" contacted. Process + discipline issue.
- **Selling manager gap** — nobody day-to-day manages sales team (Ian/Rocky/Marlon).
- **Website** — discipline, not project. Drew building new site.

**Supersedence note**:
- All business context is CURRENT at April 16, 2026. Subject to change weekly.
- Customer priorities (INSURICA/GIC/JM) are the targets for OS Phase 7 rollout.
- Gastown vision (AI Agent Factory, Q3 2026) is the end-state OS must enable.
- The OS's success = unlocking Gastown = Craig's technical priority.

### From `craigs-vision.md`:
or Ambiguities

- **How much of existing insurance systems (AMS, CMS, etc.) to integrate vs. replace** is not specified. Left to per-customer strategy.
- **How "workflow templates" compose capabilities** is not fully specified at this level — later artifacts resolve this as skills that invoke CLI commands.
- **"AI-first" at the interface level** — left as a principle; implementation spec is in the white paper + realtime-architecture-design.

**Supersedence note for vision map**:
- Entire vision SURVIVES. This IS the north star. Later artifacts specify the means; this artifact specifies the ends.
- The "AI agents are a channel" statement is ONE of the most load-bearing claims for Finding 0. It's foundational evidence that agent execution must be outside the platform core.
- The moat thesis (insurance-native domain model + agent-accessible + compounding) survives and motivates everything.

### From `product.md`:
or Ambiguities

- **Associate names canonicalization** — ~25 unique names across the matrix, but configurations vary per target group.
- **"In Development" items (8)** — some overlap with existing associate names, some net-new. Roadmap items.
- **Packaging tiers vs. pricing matrix line items** — the packaging tiers map loosely to associate bundles; exact per-tier associate set TBD.

**Supersedence note**:
- Product strategy is CURRENT. The OS kernel must support the 7 domain objects + 6 capabilities as per-org configurable entities/methods.
- "Associates are configurations, not products" SURVIVES as architectural principle.
- The OS's success = supporting the 48-associate matrix via 7 domain objects + 6 capabilities + per-org config.

### From `strategy.md`:
or Ambiguities

- **Moat sentence** — still "uninspired" per leadership.
- **Selling manager gap** — nobody manages sales team day-to-day.
- **Cam's 7-phase plan** — not tracked as kernel OS work; separate pipeline dashboard project.

**Supersedence note**: Strategy context SURVIVES as directional context. Success criteria for OS (domain model + one associate + portal + E2E proof) are the Phase 6/7 completion criteria.

### From `2026-03-25-the-vision-v1.md`:
or Ambiguities

- **v1 vs v2 difference**: v1 is "Insurance Lab" framing; v2 is "Factory" framing. Both survive into the white paper. V2 is the later superseding artifact.

**Supersedence note**: Vision v1 is SUPERSEDED by v2 (same day, refined framing). The architectural implications are the same — platform + associates + domain entities + CLI-first. V2 adds "factory" metaphor and EventGuard-as-proof emphasis.

### From `2026-03-25-the-vision.md`:
or Ambiguities

- **How the factory actually works at the code level** — deferred to architecture sessions (3-6) and specs (4/14).
- **Roadmap phase details** — "*Detailed phased roadmap to be developed*" — done in white paper + consolidated specs.
- **Moat articulation** — still evolving.

**Supersedence note**:
- Vision v2 is the CANONICAL vision. V1 is earlier, similar content.
- Vision SURVIVES through all subsequent design — the white paper is the formalization.
- **Key claims load-bearing for Finding 0**: "AI can transact, not just talk"; "Delivery channels as first-class"; "Associates = configurations of same system"; "Object-oriented insurance system." All require the harness pattern as implemented per session 5 realtime-architecture-design. Kernel-embedded agent execution contradicts.