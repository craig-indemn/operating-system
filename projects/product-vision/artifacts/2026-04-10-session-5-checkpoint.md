---
ask: "Comprehensive checkpoint of session 5 — the journey, what was accomplished, what's decided, what's still open, and how the next session should resume"
created: 2026-04-10
workstream: product-vision
session: 2026-04-10-a
sources:
  - type: conversation
    description: "Craig and Claude — full-day session re-validating the kernel against real workloads, resolving the biggest open architectural gaps, and opening the design-session phase of work"
---

# Session 5 Checkpoint

## What This Session Was About

Session 4 ended with the kernel substantially resolved (6 primitives, Temporal, unified queue, everything-is-data, watches as wiring) but with several things still open: no single specification, no end-to-end retrace of real workloads against the final architecture, a known need for simplification, and a set of open items that hadn't been designed.

Session 5 picked up with four goals:

1. **Re-validate the kernel against real workloads.** The session 4 checkpoint noted that the GIC retrace was done BEFORE key architectural changes (Temporal, unified queue, everything-is-data). The final architecture needed to be pressure-tested against real scenarios.
2. **Identify what's missing.** If the kernel has gaps, they should surface from real use cases, not speculation.
3. **Begin design sessions on open items.** Once gaps are known, work through them to designs that could inform a spec.
4. **Establish the path to spec.** What's the sequence from "architecture designed" to "spec written and building."

All four happened.

## The Journey — How This Session Evolved

### Phase 1: Rereading the full prior context

Session began by reading all 40+ prior artifacts. Initially I missed two files that errored on token limit (`2026-04-07-challenge-insurance-practitioner.md` and `2026-04-07-challenge-developer-experience.md`). Craig caught this and pushed me to re-read properly — "otherwise we're going to continue to repeat questions that we've already covered." I chunked through them and found important findings that had been addressed in session 4's evolution but gave me the complete picture.

**Lesson for next session: read EVERY file to completion. If a file errors on token limit, use offset/limit or grep to read it in chunks. Do not move on until you have the full content.**

### Phase 2: Integration elevated to primitive #6

Discussion about user credential management (personal credentials for team members — Gmail, Slack, Calendar — vs. org-level shared integrations). This exposed that Integration had never been properly formalized in the architecture. Session 4 had Integration as an entity, but the framing was ambiguous: "the integration layer collapses into the entity framework" (session 4) left it unclear whether Integration was a first-class primitive or just one of many domain entities.

Resolution: **Integration is elevated to the 6th kernel primitive.** It's infrastructure (every system needs external connectivity), it has its own lifecycle, it handles credentials, it's shared across entity types, and it supports both org-level and actor-level ownership. Adapters are its implementation (kernel code); Integration is the abstraction (bootstrap entity).

Artifact: `2026-04-10-integration-as-primitive.md`

Decisions locked:
- Six primitives: Entity, Message, Actor, Role, Organization, Integration
- Integration owner field (org_id or actor_id) enables personal and org credentials with one primitive
- AWS Secrets Manager for credential storage, Integration stores secret_ref
- Adapter versioning via `provider_version` field
- Both outbound and inbound methods in adapters (inbound webhook dispatch via `/webhook/{provider}/{integration_id}`)

### Phase 3: GIC retrace against the updated kernel

With all six primitives in place, traced the GIC email intelligence pipeline end-to-end. Worked through every step: email sync (scheduled via Integration), extraction, classification with `--auto` pattern, linking with reference patterns + fuzzy search, assessment, draft generation, human review, stale detection.

**The kernel held up.** Zero primitive changes required. Six concerns surfaced as follow-ups: bulk event coalescing, pipeline dashboards, ephemeral entity locks, multi-LOB draft handling (domain skill), queue health tooling, computed field activation scope.

None of the concerns were architectural — they were usability/tooling gaps.

Artifact: `2026-04-10-gic-retrace-full-kernel.md`

### Phase 4: Base UI design, auth sketch, and associate-role resolution

Discussion of how the GIC concerns get addressed. Most of them resolve via the auto-generated base UI. This led to a focused pass on what the base UI looks like (auto-generated from entity definitions, 1:1 with CLI, role-scoped, admin-first).

Also addressed: authentication was thinly sketched in session 3's Layer 1 design and never fleshed out. Produced a starting sketch covering authentication methods as a list on Actor, identity providers as Integrations (reuses primitive #6), SSO + password coexistence, role-grant authority, actor lifecycle.

**Key correction from Craig**: the asymmetry of "each associate has its own named role" (as I'd done in the GIC retrace) was awkward. Associates shouldn't need singleton named roles that nobody else holds. Resolution: Role has two ergonomic creation paths — Path 1 (named shared roles for organizational job functions held by humans) and Path 2 (inline roles defined on associate creation, for automation scope). One primitive, two paths. Role-grant authority only matters for Path 1.

Artifact: `2026-04-10-base-ui-and-auth-design.md`

Decisions locked:
- Base UI is auto-generated from primitives, 1:1 with API (not CLI — correction came later), role-scoped
- Two kernel additions needed for base UI: watch coalescing, ephemeral entity locks (later unified into Attention)
- Identity providers are Integrations (reuse of primitive #6)
- Authentication methods as a list on Actor
- Role creation has two ergonomic paths (named shared vs inline-on-associate)
- Full authentication design deferred to its own session

### Phase 5: EventGuard retrace — second pressure test

With GIC covered, traced EventGuard end-to-end. Fundamentally different workload shape: consumer-facing, real-time (voice and chat), Stripe payment integration with inbound webhooks, fully autonomous (no HITL), 351 venue deployments, policy issuance with certificate delivery.

**The kernel still held up.** But this trace surfaced the **biggest architectural gap of the session**: how does a running real-time actor (Quote Assistant holding a live WebSocket or voice call) receive events that happen during the conversation (Stripe webhook completes → Payment → Policy → need to tell the customer "all set!")?

Watches generate queue messages, but a running real-time actor isn't polling a queue. Needed a new mechanism.

Also surfaced:
- Inbound webhook dispatch as a first-class Integration concept
- Bulk operations pattern (351 deployments forces the issue)
- Internal Actors vs external counterparty entities distinction

Artifact: `2026-04-10-eventguard-retrace.md`

### Phase 6: Post-trace synthesis

Stepped back. Two retraces done, very different workload shapes, same kernel. Categorized what's validated, what's open, what needs design, what's documentation, what's deferred to its own session. Produced a 10-item open list with a status table and a proposed sequence (CRM trace → design sessions → simplification → spec).

Artifact: `2026-04-10-post-trace-synthesis.md`

### Phase 7: CRM retrace — third pressure test

Third retrace: Indemn's own internal CRM. Completely different from the two insurance traces. Generic B2B concepts (Organization, Contact, Deal, Meeting, MeetingIntelligence, ActionItem, Interaction, HealthSignal). Heavy actor-level integrations (15 team members × 4 integration types = 60 actor-level integrations). Read-heavy queries ("what's the story with INSURICA?") rather than write pipelines. Dog-fooding the "Indemn runs on the OS" thesis.

**The kernel held up AND the domain-agnostic claim validated cleanly.** Zero insurance concepts required.

Surfaced one new architectural addition: **associates with `owner_actor_id`** — for "associate acting on behalf of a human using their personal credentials." Craig's personal Gmail sync associate needs to use Craig's personal Gmail integration, which is owned by Craig, not by the sync associate. Resolution: associates have an optional owner_actor_id field; credential resolution checks the owner's personal integrations in addition to the associate's own.

Also surfaced: content visibility scoping for personal-integration-derived entities (Craig's private email creates an Interaction whose metadata is shared but whose full content is owner-scoped).

**Decision: three traces is enough.** Different enough to exercise different kernel mechanisms; no more retraces would stress new territory.

Artifact: `2026-04-10-crm-retrace.md`

### Phase 8: First design session — Real-time architecture

With retraces complete and gaps identified, worked through the biggest gap in detail: how real-time actors receive mid-conversation events, how handoff between actors/roles works, how scoped events reach specific actors.

This phase was the longest discussion in the session. Multiple passes, corrections, and course corrections. Notable evolution:

**Pass 1 — Attention as a bootstrap entity.** Craig pointed out that the "active_context table" I was proposing was a standalone store inconsistent with the "everything is an entity" philosophy. Resolution: unify with the "ephemeral entity locks" concept from the base UI artifact. Both are "an actor is currently attending to this entity with a TTL-expiring heartbeat." One unified concept: **Attention**.

**Pass 2 — Scoped watches.** Two resolution types: `field_path` (for ownership-style scoping in CRM — traverse an entity relationship to resolve an actor_id) and `active_context` (for real-time routing — look up matching Attention records). Emit-time resolution produces `target_actor_id` on messages. No runtime scope evaluation at claim time. Plus watch coalescing for bulk event scenarios.

**Pass 3 — How does the chat conversation actually flow into the agent?** Craig pushed back on my hand-waving about real-time mechanics. Worked through Channel Manager concept, then Temporal workflows, then ultimately landed on a cleaner model.

**Pass 4 — Redis pushed back.** I had introduced Redis pub/sub for delivering mid-conversation events. Craig caught that we had never committed to Redis. Resolution: MongoDB Change Streams (already in the stack) for event delivery. No new dependency.

**Pass 5 — Real-time runtime vs async runtime.** Temporal workflows aren't the right shape for holding WebSocket connections. Real-time actors run in a different runtime than async actors. Same kernel surface, different execution model.

**Pass 6 — Runtime as a bootstrap entity.** Craig pushed that the runtime is "the most important part, the center of everything, and should probably be in the kernel." Resolution: **Runtime** as a bootstrap entity. Describes the deployable host for associate execution: kind, framework, transport, capacity, deployment image. One Runtime hosts many Associates. Framework is data, not code — plug-and-play at the entity level.

**Pass 7 — Harness interface, then retracted.** I proposed a Python SDK layer for harness-kernel communication. Craig pushed back: "the whole point of deepagents is that it uses the CLI." Retracted the SDK. Harnesses use the CLI via subprocess for their OS interactions. No dual interface.

**Pass 8 — Full framework feature access.** Craig emphasized that harnesses must be able to use ALL features of LiveKit, deepagents, sandboxes, etc. Resolution: thin contract. The kernel doesn't call into the harness; the harness uses the CLI autonomously. This lets the harness use its framework fully.

**Pass 9 — I had hardcoded model/skill in the harness example.** Craig caught that this assumes one model per harness, which misses the point — Associates carry the config, harnesses load it per session. Correction: **one harness serves many associates, loading associate config at session start.**

**Pass 10 — Handoff as observation + intervention.** Craig's framing: an actor or role can "take over a runtime and see what's happening in real time and jump in at any point." Resolution: Attention has a `purpose=observing` state for real-time watchers. Transfer to an actor or to a role is a CLI command (`indemn interaction transfer`). The Runtime notices and switches between "run associate in-process" and "bridge to human via queue" modes.

**Pass 11 — Voice clients for humans are Integrations.** Craig proposed that when a human joins a voice call (to take over from an associate), their voice client is an Integration (`system_type: voice_client`, actor-owned). Reuses primitive #6. No new concept.

**Pass 12 — CLI auto-generation clarification.** Craig pushed back on my listing "new CLI commands to design" — most of them are auto-generated from entity definitions. The only genuinely new infrastructure CLI command is `indemn events stream`.

All of this converged into a single comprehensive artifact covering Attention, Runtime, scoped watches, watch coalescing, the harness pattern, channel transport, customer-facing flexibility, handoff, voice clients, CLI surface, and worked examples.

Artifact: `2026-04-10-realtime-architecture-design.md`

### Phase 9: CLI vs API clarification

Last substantive correction of the session. I had been saying "CLI everywhere" as if CLI were the universal interface. Craig pointed out this is wrong: both CLI and API are auto-generated surfaces from entity definitions. The UI uses the API (programmatic), the CLI is for humans/agents/scripts. Both respect the same permissions, auth, and self-evident property.

**The "universal interface" is the entity framework's auto-generated surface, which manifests as both CLI and API simultaneously.**

Captured as a decision in INDEX.md.

### Phase 10: Checkpoint (this artifact)

Written to enable the next session to resume with full context.

## What's DECIDED in Session 5 (Do Not Re-Litigate)

### Kernel primitive set

The six structural primitives are stable: **Entity, Message, Actor, Role, Organization, Integration.** Integration was elevated to primitive #6 in this session; the rest are unchanged from session 4.

### Bootstrap entity set

Entities the kernel knows about specifically because it depends on them, managed like any entity through normal CRUD:

- **Organization** (multi-tenancy scope)
- **Actor** (identity, humans and associates and tier3 devs)
- **Role** (permissions + watches)
- **Integration** (external system connection, org or actor-owned)
- **Attention** (active working context, NEW this session)
- **Runtime** (deployable host for associate execution, NEW this session)

### Integration primitive details

- Owner field (`org_id` or `actor_id`) enables org-level and actor-level integrations with one primitive
- Credentials never stored inline — `secret_ref` points to AWS Secrets Manager
- Adapter pattern for implementation, keyed by `provider_version` for migration safety
- Inbound webhook dispatch via `/webhook/{provider}/{integration_id}` endpoint, validated via the Integration's secret_ref, parsed into entity operations
- Identity providers are Integrations (for SSO)
- Voice clients for humans are Integrations (for human participation in real-time voice)
- Adapters have both outbound methods (charge, fetch, send) and inbound methods (validate_webhook, parse_webhook, auth_initiate)

### Attention

- Bootstrap entity unifying UI soft-locks and real-time active-session contexts
- Fields: actor_id, target_entity, related_entities, purpose, runtime_id, workflow_id, session_id, opened_at, last_heartbeat, expires_at
- Purposes: real_time_session, observing, review, editing, claim_in_progress
- Heartbeat-maintained with TTL expiration
- Heartbeat updates bypass audit logging (noise reduction)
- Enables: soft-locks, scoped event routing, presence awareness, zombie session detection, capacity management

### Runtime

- Bootstrap entity for associate execution
- Fields: name, kind (realtime_chat/voice/sms, async_worker), framework, framework_version, transport, transport_config, llm_config, deployment_image, deployment_platform, deployment_ref, capacity, instances, status
- Lifecycle: configured → deploying → active → draining → stopped
- **One Runtime hosts many Associates** — Associate has `runtime_id` pointing to its Runtime
- Framework is data (deepagents, langchain, custom) — plug-and-play via the harness pattern
- Runtime entity is the description; deployment instances are where scale happens

### Harness pattern

- A harness is deployable glue code (e.g., Docker image) per kind+framework combination
- Uses the OS CLI via subprocess for kernel interactions
- Loads Associate config at session start — one harness serves any associate of the right kind
- Has full access to its framework's features (LiveKit, deepagents, sandboxes, etc.)
- Harness is NOT a kernel concept; it's deployment infrastructure

### CLI and API as parallel auto-generated surfaces

- Both derived from entity definitions via auto-registration
- Both respect the same permissions, auth, and self-evident property
- The base UI uses the API, not the CLI
- Harnesses use the CLI (subprocess) for convenience in their deployable scripts
- Agents use whichever fits their context
- `indemn events stream` is the ONE new infrastructure CLI command introduced in this session; everything else is auto-generated

### Scoped watches

- Watches gain an optional `scope` field with two resolution types:
  - `field_path`: traverses an entity relationship to resolve an actor_id (for ownership-style scoping)
  - `active_context`: queries Attention records for actors whose working context includes this entity (for real-time routing)
- Scope resolved at emit time, produces `target_actor_id` on the message
- Claim queries filter by `target_actor_id = self OR null`
- Sub-millisecond overhead

### Watch coalescing

- Watches gain an optional `coalesce` field with strategies (`by_correlation_id`, etc.) and a time window
- Groups events from the same source into a single batched queue item with summary template
- Applied after scope resolution (per-target-actor)
- Additive: unscoped, uncoalesced watches behave exactly as before

### Handoff

- Interaction has `handling_actor_id` and optionally `handling_role_id`
- Transfer is an @exposed method: `indemn interaction transfer --to actor` or `--to-role role`
- Runtime notices via Change Stream on the Interaction and switches modes
- Observation is a first-class state (Attention with purpose=observing)
- Transfer can go to an actor or a role

### Associate fields added

- `runtime_id` — which Runtime hosts this associate
- `owner_actor_id` — optional, for delegated credential access (associate acts on behalf of a human using their personal integrations)
- `llm_config`, `prompt`, `mode`, `skills` — per-associate config loaded by harness at session start

### Role creation — two ergonomic paths

- **Path 1 (named shared)**: `indemn role create underwriter ...` — for organizational job functions humans hold, reusable, grantable per `can_grant`
- **Path 2 (inline on associate)**: `indemn actor create --type associate --permissions ... --watches ... --skill ...` — kernel creates a singleton role bound to the associate; not listed as a named role; `can_grant: null`
- Same primitive (Role), two creation workflows

### Rule system (correction from earlier session)

- Rules have exactly two actions: `set-fields` and `force-reasoning`
- The `--veto` flag is sugar for "priority: high + action: force-reasoning"
- Lookups stay separate from rules (per capabilities-model-review finding) — they're bulk-importable mapping tables
- My fabricated action types (map-lookup, transition, call-capability) were retracted

### Associate execution mode

- Deterministic mode collapsed into hybrid — a "deterministic associate" is a hybrid associate whose kernel capabilities always succeed
- If LLM-free execution is ever required for compliance, a mode flag can raise on `needs_reasoning` instead of falling back

### Temporal role

- Temporal is for **async associate execution**: claim-process-complete cycles with durability, retries, saga compensation
- Temporal is NOT for real-time (LiveKit/WebSocket sessions run in Runtime processes directly)
- Temporal is NOT for pub/sub (use MongoDB Change Streams)
- Generic Temporal workflow per actor invocation; skill is source of truth for orchestration
- Per-step specialized workflows only for true long-running sagas (rare)

### Default chat assistant in base UI

- Every human actor has a default associate bound to them via `owner_actor_id`, scoped to their roles and permissions
- The assistant acts through the same CLI/API any other associate uses; the UI chat is just a surface
- Natural extension of the "personal AI assistant per role" idea from core primitives
- No new mechanism — pre-configured associate automatically provisioned for every human actor
- To be formalized in the base UI spec

### Three-layer customer-facing flexibility

- Transport behavior on Deployment entity
- Conversation style on Associate skill
- Execution environment on Runtime
- Per-session override merge: Runtime defaults → Associate → Deployment

## Architecture State at End of Session 5

### What we have

- Six structural primitives, stable and validated against three different workload shapes
- Six bootstrap entities (Organization, Actor, Role, Integration, Attention, Runtime)
- Watch mechanism with condition filtering, scoping (two resolution types), and coalescing
- Temporal for async durable execution
- MongoDB for everything (config, data, queue, audit, change streams for event delivery)
- AWS Secrets Manager for credentials
- S3 for files
- Channel-specific runtimes for real-time (voice/chat/sms) with pluggable frameworks
- Handoff semantics for mixed human/associate conversations
- CLI and API as parallel auto-generated surfaces

### What three traces validated

| Dimension | GIC | EventGuard | CRM |
|---|---|---|---|
| Domain | Insurance (B2B MGA) | Insurance (consumer embedded) | Generic B2B (non-insurance) |
| Workload shape | Batch-burst email pipeline | Continuous real-time + webhooks | Mixed scheduled + events + heavy reads |
| HITL | Heavy | None (fully autonomous) | Heavy (humans drive) |
| Integration ownership | Org-level only | Org-level only | Mixed org + actor (60+ actor-level) |
| Kernel additions surfaced | Coalescing, ephemeral locks | Actor-context watches + real-time event delivery, inbound webhooks | `owner_actor_id`, privacy scoping |
| Domain-agnostic test | Partial (insurance) | Partial (insurance) | **Full (no insurance)** |

Same six primitives. Different column for every row. That's the validation story.

## What's STILL OPEN

### Design work remaining (before spec can be written)

From the post-trace synthesis + additions:

**Architectural gaps (needs design session):**
- ~~Item 1: Watch coalescing~~ — DONE in this session
- ~~Item 2: Ephemeral entity locks~~ — DONE in this session (unified into Attention)
- ~~Item 3: Actor-context watches + signal delivery~~ — DONE in this session
- **Item 7: Bulk operations pattern** — not done, needs design session. EventGuard's 351 deployments + GIC's scheduled bulk updates force the issue.

**Supporting infrastructure (needs design):**
- **Item 8: Pipeline dashboard layer** — sketched, needs rendering contract design
- **Item 9: Queue health tooling** — sketched, needs CLI surface design

**Authentication (own session):**
- **Item 10: Authentication** — sketched in base-ui-and-auth artifact, needs full design. MFA policy placement, Tier 3 self-service signup, session management, platform-admin cross-org scope, specific IdP adapters to ship.

**Small extensions (need captured in artifact):**
- **Item 11: owner_actor_id on associates** — shape clear, needs to be formalized into the Integration artifact or a follow-up
- **Item 12: Content visibility scoping for personal-integration-derived entities** — policy decision per Integration type, needs documentation

**Documentation updates (quick):**
- **Item 4: Inbound webhook dispatch** — update the Integration artifact to explicitly cover inbound
- **Item 5: Internal Actors vs external counterparty entities** — clarification for the spec
- **Item 6: Computed field mapping scope** — mapping belongs on method activation, not as a shared Lookup

**Deferred UX work:**
- Voice handoff UX (human takes over a live phone call — the mechanism works, the flow design is pending)
- Default chat assistant in base UI (mechanism agreed, specifics to be formalized with the base UI spec)

### The simplification pass

The architecture grew substantially in session 5 (Attention, Runtime, scoped watches, watch coalescing, owner_actor_id, handoff semantics, voice clients as Integrations). **The simplification pass is still scheduled for after all design sessions complete.** Craig's instinct from session 4 ("a lot of this can be simplified") should be honored — but only after we're sure we're not simplifying away something we'll need to add back.

### The spec itself

- Still not written
- The consolidated architecture artifact from session 4 is stale (doesn't include Integration elevation, Attention, Runtime, scoped watches, etc.)
- Writing the spec is the final step after all design work and simplification

### Strategic/stakeholder work

Unchanged from session 4:
- Ryan/Dhruv/George engagement — designed but not started
- Kyle + Cam pitch — waiting on the spec
- Champion strategy — how Craig presents the vision to the company
- The deliverable format — what does the final roadmap/vision document look like?

## Sequence From Here

Per the plan Craig accepted in session 5:

1. ~~**CRM trace**~~ — DONE
2. **Design sessions on remaining open items**
   - Bulk operations pattern
   - Pipeline dashboard + queue health (probably one session)
   - Authentication (own session)
3. **Documentation updates** (quick sweep of items 4, 5, 6, 12)
4. **Simplification pass** — fresh eyes on everything, "does this earn its complexity?" for each concept
5. **Spec writing** — one actionable document (or a small set of connected ones)
6. **Stakeholder engagement** — Ryan → Dhruv → George → Kyle/Cam
7. **Begin building**

## Artifacts From Session 5 (All)

In chronological order:

| Order | Artifact | What It Captures |
|---|---|---|
| 1 | `2026-04-10-integration-as-primitive.md` | Integration elevated to the 6th primitive, owner field, adapter versioning, relationship to adapters |
| 2 | `2026-04-10-gic-retrace-full-kernel.md` | First retrace — GIC against the full kernel, six concerns surfaced |
| 3 | `2026-04-10-base-ui-and-auth-design.md` | Base UI philosophy + components, auth sketch, associate role resolution (two paths) |
| 4 | `2026-04-10-eventguard-retrace.md` | Second retrace — EventGuard, real-time architectural gap surfaced |
| 5 | `2026-04-10-post-trace-synthesis.md` | What two retraces together validated, 10-item design work list, proposed sequence |
| 6 | `2026-04-10-crm-retrace.md` | Third retrace — generic CRM, `owner_actor_id` finding, domain-agnostic claim validated |
| 7 | `2026-04-10-realtime-architecture-design.md` | First design-session output — Attention + Runtime + scoped watches + handoff + harness pattern |
| 8 | `2026-04-10-session-5-checkpoint.md` | THIS FILE |

## How to Resume (Next Session)

### READ EVERY FILE. NO SHORTCUTS.

Craig explicitly said: "I want the new session to read all the files otherwise we are going to not have the full context. I know it's a lot, but I think it's important."

**This checkpoint is NOT a substitute for reading the artifacts. It's a companion that helps orient after you've read everything.**

### Reading order

**Part 1: Foundation (sessions 1-4, everything from before today)**
1. `projects/product-vision/INDEX.md` — the index with all decisions
2. `projects/product-vision/artifacts/context/business.md`
3. `projects/product-vision/artifacts/context/product.md`
4. `projects/product-vision/artifacts/context/architecture.md`
5. `projects/product-vision/artifacts/context/strategy.md`
6. `projects/product-vision/artifacts/context/craigs-vision.md`
7. `projects/product-vision/artifacts/2026-03-25-session-notes.md`
8. `projects/product-vision/artifacts/2026-03-25-the-operating-system-for-insurance.md`
9. `projects/product-vision/artifacts/2026-03-25-why-insurance-why-now.md`
10. `projects/product-vision/artifacts/2026-03-25-platform-tiers-and-operations.md`
11. `projects/product-vision/artifacts/2026-03-25-associate-architecture.md`
12. `projects/product-vision/artifacts/2026-03-30-entity-system-and-generator.md`
13. `projects/product-vision/artifacts/2026-03-30-vision-session-2-checkpoint.md`
14. `projects/product-vision/artifacts/2026-03-30-design-layer-1-entity-framework.md`
15. `projects/product-vision/artifacts/2026-03-30-design-layer-3-associate-system.md`
16. `projects/product-vision/artifacts/2026-04-02-core-primitives-architecture.md`
17. `projects/product-vision/artifacts/2026-04-02-design-layer-4-integrations.md`
18. `projects/product-vision/artifacts/2026-04-02-design-layer-5-experience.md`
19. `projects/product-vision/artifacts/2026-04-02-implementation-plan.md`
20. `projects/product-vision/artifacts/2026-04-03-message-actor-architecture-research.md`
21. `projects/product-vision/artifacts/2026-04-07-challenge-insurance-practitioner.md` — **use offset/limit or grep if token limit errors**
22. `projects/product-vision/artifacts/2026-04-07-challenge-distributed-systems.md`
23. `projects/product-vision/artifacts/2026-04-07-challenge-developer-experience.md` — **use offset/limit or grep if token limit errors**
24. `projects/product-vision/artifacts/2026-04-07-challenge-realtime-systems.md`
25. `projects/product-vision/artifacts/2026-04-07-challenge-mvp-buildability.md`
26. `projects/product-vision/artifacts/2026-04-08-session-3-checkpoint.md`
27. `projects/product-vision/artifacts/2026-04-08-actor-spectrum-and-primitives.md`
28. `projects/product-vision/artifacts/2026-04-08-primitives-resolved.md`
29. `projects/product-vision/artifacts/2026-04-08-entry-points-and-triggers.md`
30. `projects/product-vision/artifacts/2026-04-08-kernel-vs-domain.md`
31. `projects/product-vision/artifacts/2026-04-08-pressure-test-findings.md`
32. `projects/product-vision/artifacts/2026-04-08-actor-references-and-targeting.md`
33. `projects/product-vision/artifacts/2026-04-09-entity-capabilities-and-skill-model.md`
34. `projects/product-vision/artifacts/2026-04-09-capabilities-model-review-findings.md`
35. `projects/product-vision/artifacts/2026-04-09-temporal-integration-architecture.md`
36. `projects/product-vision/artifacts/2026-04-09-unified-queue-temporal-execution.md`
37. `projects/product-vision/artifacts/2026-04-09-data-architecture-everything-is-data.md`
38. `projects/product-vision/artifacts/2026-04-09-architecture-ironing.md`
39. `projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-2.md`
40. `projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-3.md`
41. `projects/product-vision/artifacts/2026-04-09-data-architecture-review-findings.md`
42. `projects/product-vision/artifacts/2026-04-09-data-architecture-solutions.md`
43. `projects/product-vision/artifacts/2026-04-09-session-4-checkpoint.md`
44. `projects/product-vision/artifacts/2026-04-09-consolidated-architecture.md` — **STALE; superseded by session 5 additions**

**Part 2: Session 5 artifacts (today's work)**
45. `projects/product-vision/artifacts/2026-04-10-integration-as-primitive.md`
46. `projects/product-vision/artifacts/2026-04-10-gic-retrace-full-kernel.md`
47. `projects/product-vision/artifacts/2026-04-10-base-ui-and-auth-design.md`
48. `projects/product-vision/artifacts/2026-04-10-eventguard-retrace.md`
49. `projects/product-vision/artifacts/2026-04-10-post-trace-synthesis.md`
50. `projects/product-vision/artifacts/2026-04-10-crm-retrace.md`
51. `projects/product-vision/artifacts/2026-04-10-realtime-architecture-design.md`

**Part 3: This checkpoint (read LAST)**
52. `projects/product-vision/artifacts/2026-04-10-session-5-checkpoint.md`

That's 52 files. It's a lot. It's necessary. The session 4 checkpoint said the same thing about the session 4 artifacts, and reading them all was essential for the work that happened in session 5. Nothing has changed — you need the full context to continue productively.

### What to do after reading

1. **Acknowledge where we are.** The kernel is stable. Six primitives, six bootstrap entities (Org, Actor, Role, Integration, Attention, Runtime). Three traces validated the architecture against very different workloads. The first design session (real-time architecture) is complete.

2. **Ask Craig what he wants to tackle next.** The open items are categorized in this checkpoint. The natural next steps are:
   - **Bulk operations pattern** (item 7) — concrete forcing function from EventGuard
   - **Pipeline dashboard + queue health** (items 8, 9) — probably one session, related scope
   - **Authentication** (item 10) — own session, largest remaining gap
   - **Documentation sweep** (items 4, 5, 6, 12) — quick wins, could be done together
   
3. **Don't re-litigate decisions.** The "What's Decided" section of this checkpoint is the result of extensive discussion and pressure-testing. Proposing to undo something in that section requires a concrete new reason, not "I'm not sure about this." Honor the work that's been done.

4. **Keep the simplification pass in mind.** The architecture grew today. Craig is explicitly concerned about complexity. When new additions come up, ask "does this earn its complexity?" For now, capture what's needed — the simplification pass is scheduled for after all design sessions are complete.

5. **Read the prior session's work as source of truth.** If there's tension between an earlier artifact and a later artifact, the later one wins. Architecture evolved through the sessions; early decisions got revised or overturned as the design matured. The most recent artifacts (especially today's) are authoritative.

### Guidance from Craig (captured across the session)

- "A lot of this can be simplified" (but not until design sessions are complete)
- "I don't think the system is complicated for us to implement, as long as we're clear about what we're building, why, and how it should be used, and we document everything"
- The runtime is "the most important part, the center of everything"
- "We want the deployed interface that users are interacting with to be flexible"
- "I don't want to be stuck with one [framework] and that's why the channel manager could or could not be in the kernel"
- "I don't want to leave it up to an implementation detail on the voice thing" — no hand-waving on latency
- "The whole point of us using deep agents is because the deep agent uses the CLI"
- "The CLI commands are auto-created by the entities so I don't understand your question there" — don't list auto-generated CLI as new design work
- "I want the new session to read all the files otherwise we are going to not have the full context"

### What will NOT help the next session

- Skipping files to "save time" — Craig explicitly doesn't want this
- Re-asking questions that are already answered (entity as data, Temporal for async, CLI + API both auto-generated, etc.)
- Inventing concepts or actions that aren't in the artifacts (like I did with fabricated rule actions)
- Introducing new dependencies (like Redis) without justification
- Conflating "CLI" with "universal interface" — the universal interface is the entity framework's auto-generated surface, which exists as both CLI and API
- Forcing simplification during design sessions instead of during the dedicated simplification pass

## Final Note

Session 5 made the architecture more complete and more ready to encapsulate. The kernel passed three real pressure tests. The biggest architectural gap (real-time event delivery) is resolved. The plug-and-play framework concern is addressed via Runtime as data. The human/associate handoff is a clean extension of existing primitives.

What remains is finite and scoped: a few more design sessions, a documentation sweep, a simplification pass, and the spec itself. The path to "start building" is now a checklist of known work, not an open-ended exploration.

Session 6 can be productive if it starts from the full context. Don't shortcut the reading.
