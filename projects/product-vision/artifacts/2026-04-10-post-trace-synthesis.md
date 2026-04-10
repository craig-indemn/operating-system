---
ask: "What do the GIC and EventGuard retraces collectively tell us about the kernel, and what design work remains before we can write the spec?"
created: 2026-04-10
workstream: product-vision
session: 2026-04-10-a
sources:
  - type: artifact
    description: "2026-04-10-gic-retrace-full-kernel.md (first retrace — B2B email pipeline with heavy HITL)"
  - type: artifact
    description: "2026-04-10-eventguard-retrace.md (second retrace — consumer real-time with zero HITL)"
  - type: artifact
    description: "2026-04-10-integration-as-primitive.md"
  - type: artifact
    description: "2026-04-10-base-ui-and-auth-design.md"
---

# Post-Trace Synthesis

## Purpose

Two retraces have now been completed against the updated 6-primitive kernel: GIC Email Intelligence and EventGuard. They were chosen to expose different failure modes. GIC is B2B, email-driven, heavy HITL, batch-burst volume, closely resembles a classic insurance workflow. EventGuard is consumer-facing, real-time, zero HITL in the happy path, continuous volume, 351 distribution surfaces, payment-heavy. The only thing they share is the kernel.

This artifact distills what the two traces collectively validated, what design work they surfaced, and what's needed before the architecture can be encapsulated as a spec and built from.

## What Two Very Different Traces Validated

Both retraces passed on the kernel primitives without requiring any changes to the core model:

### The six primitives handle both workloads

Entity, Message, Actor, Role, Organization, Integration. No new primitive surfaced in either trace. No existing primitive felt forced or superfluous. The primitives are stable.

### The kernel is not secretly shaped for one workload type

GIC is batch-burst email processing. EventGuard is continuous real-time consumer interaction. Same primitives serve both. No primitive is biased toward one model. The kernel-vs-domain separation holds — all business logic in both cases is per-org data (rules, lookups, skills, activations), not kernel code.

### Integration as primitive #6 earns its elevation

GIC exercised outbound email polling (Outlook fetch). EventGuard exercised outbound payment calls (Stripe charge) AND inbound webhooks (Stripe payment confirmation) AND real-time voice/chat (LiveKit) AND document generation (Mint). Same primitive, same adapter pattern, same credential management via Secrets Manager. The primitive naturally extends to inbound connectivity without structural changes.

### Watches handle all orchestration

Both pipelines emerge from watches on events — no explicit workflow orchestration code. GIC's pipeline (Email → Extraction → Classification → Linking → Assessment → Draft → Review) and EventGuard's pipeline (Interaction → Application → Quote → Payment → Policy → Certificate → Delivery) are both constructed entirely through watches. Each step is a separate actor watching the previous step's event. The system churns.

### The `--auto` pattern scales to both deterministic-heavy and reasoning-heavy workloads

GIC uses `--auto` for classification (USLI hard rules), linking (reference patterns + fuzzy search), stale detection (rule-based). EventGuard uses `--auto` for rating (rule-based premium calculation). In both cases, LLM is only invoked when the deterministic path returns `needs_reasoning`. LLM cost is proportional to edge case complexity, not volume.

### The unified queue works for mixed human/associate operation and for fully autonomous operation

GIC has heavy HITL (JC reviews, Maribel operates) — same queue serves humans and associates. EventGuard has zero HITL in the happy path — same primitives, just no humans in the critical path. The kernel doesn't mandate HITL; it's a policy choice per watch.

### Selective emission prevents watch storms

GIC's pipeline has many intermediate entity updates (extraction data, classification fields, link updates). EventGuard has many per-turn Application field updates during active conversations. Neither generates cascading watches because only state transitions and `@exposed` method calls emit messages. Field updates are silent.

### Multi-entity atomicity holds via single-transaction actor turns

GIC's linker creates a Submission and updates an Email in one transaction. EventGuard's policy issuer creates a Policy and updates an Application in one transaction. Temporal replay handles crash recovery between turns. No explicit sagas needed for single-actor operations.

### One actor can serve a high-volume deployment

EventGuard's Quote Assistant serves all 351 venues by loading per-venue branding from the Deployment at conversation start. No per-venue actor proliferation. The skill handles branding context-loading as part of its orchestration.

## Design Items Surfaced (Across Both Traces)

### Architectural gaps (small kernel additions, but real mechanism changes)

**1. Watch coalescing for bulk event emission (from GIC).** When a scheduled capability like stale-check updates N entities in one transaction, N events are emitted to N watches — which can spike human queues with unrelated-seeming rows. Proposed mechanism: watches declare an optional `coalesce` strategy. Messages from the same source event (same correlation_id) within a time window collapse to a single batched queue item with a summary template. Individual items are still claimable via drill-down. Additive — default behavior is unchanged.

**2. Ephemeral entity locks for "user is actively viewing" (from GIC).** During human review of a draft or submission, the UI needs to warn other users "JC is reviewing this" without hard-blocking claims. Proposed mechanism: lightweight CLI `indemn entity lock/unlock/lock-status` with TTL expiration, heartbeat from the UI during active review, informational (not blocking) surfacing to other viewers. Small addition — one small collection or entity fields, expiration via TTL index.

**3. Actor-context watch scoping + mid-conversation event delivery (from EventGuard).** This is the biggest of the three. A running real-time actor holding an open channel (WebSocket, voice) needs to receive events related to its current Interaction as they happen, not via queue polling. Proposed mechanism: watches support a `scope: actor_context` qualifier. When a watch with that scope matches, the kernel checks if the entity is in the context of a currently-running actor and routes the event as a Temporal signal to that actor's workflow instead of writing to the queue. The running workflow handles the signal by sending a proactive message on the open channel. Additive — regular watches still write to queue.

All three are additive. None requires changing how existing watches behave. All three slot into the existing primitive model without introducing new primitives.

### Documentation clarifications (not mechanism changes, just making things explicit)

**4. Inbound webhook dispatch via Integration adapters (from EventGuard).** The Integration artifact described outbound calls (charge, fetch, send). EventGuard exposed that inbound webhooks use the same Integration primitive but through an adapter's inbound methods (validate_webhook, parse_webhook). The integration artifact should be updated to explicitly cover:
- Kernel webhook endpoint at `/webhook/{provider}/{integration_id}`
- Adapter interface with both outbound and inbound methods
- Signature validation using the Integration's secret_ref
- Parsing webhook payloads into entity operations (not raw updates — go through entity methods for state machine enforcement)

**5. Internal Actors vs. external counterparty entities (from EventGuard).** Actors (humans, associates, Tier 3 developers) authenticate and have roles. External counterparties (Customer buying insurance, Agent submitting work, Carrier as underwriter) are entities without auth. Both concepts exist; they live in different parts of the primitive model. The spec should state this explicitly to prevent confusion.

**6. Computed field mapping scope (from GIC).** When activating a computed field on an entity type (e.g., Submission.ball_holder derived from stage), the mapping belongs on the method activation, not as a separate shared Lookup. Lookups are for cross-entity data tables maintained by non-technical users. Method activation configs are for intrinsic entity behavior. Clarification to document.

### Design work (things we know we need, but haven't designed yet)

**7. Bulk operations pattern (from both).** GIC flagged it in previous reviews; EventGuard made it concrete (351 deployments). Needs explicit design:
- Transaction batching strategy (how many entities per transaction to balance atomicity with lock duration)
- Event emission for bulk operations (one batch event? N individual events? Both with `batch_id` linkage?)
- Integration with watch coalescing (bulk creation produces coalesced messages, not 351 rows)
- Progress reporting during long-running bulk operations
- Idempotency (re-runnable if interrupted)
- Rollback on partial failure
- CLI ergonomics (`--from-csv`, `--template`, `--dry-run`, `--batch-size`)

**8. Pipeline dashboard layer (from GIC).** Not a kernel primitive — an auto-generated reporting layer in the base UI. Sources: entity state machine distributions, message log throughput, Temporal execution stats, Integration health. Design is mostly about the rendering contract (how entity definitions map to default dashboards) and the query interface over the existing stores.

**9. Queue health tooling (from GIC).** First-class CLI commands and UI dashboard for queue depth per role, associate health, integration health, trace cascades. Data exists in existing stores; the design work is the CLI surface and the UI rendering.

### Auth (separate design session)

**10. Authentication.** Sketched in the base-ui-and-auth artifact but not designed in detail. Needs its own session:
- Actor authentication_methods list (password, SSO, MFA, service tokens, API keys)
- Identity providers as Integrations (reuses primitive #6)
- SSO + password coexistence (confirmed requirement)
- Role-grant authority as meta-permission (`can_grant` on Role)
- Actor lifecycle (provisioned → active → suspended → deprovisioned)
- Bootstrap flow for new orgs
- MFA policy placement (Role vs Actor vs authentication method)
- Tier 3 self-service signup flow
- Platform-admin cross-org scope
- Specific IdP adapters to ship (Okta, Azure AD, Google Workspace, generic OIDC, generic SAML)

## Status of These Items: Identified, Not Designed

Most of the items above are **identified and framed** in the retrace artifacts and the base-ui-and-auth artifact, but they are **not designed in detail**. The retraces produced findings; we haven't worked through implementation details for any of them beyond sketches. This is the next layer of work before we can write the actual spec.

Here's the status by item:

| # | Item | Status | Ready to spec? |
|---|------|--------|----------------|
| 1 | Watch coalescing | Sketched in base-ui artifact | No — needs mechanism design |
| 2 | Ephemeral entity locks | Sketched in base-ui artifact | No — needs protocol design |
| 3 | Actor-context watches + signal delivery | Identified in EventGuard retrace | No — needs kernel mechanism design |
| 4 | Inbound webhook dispatch | Implied in EventGuard retrace | Mostly — needs integration artifact update |
| 5 | Internal vs external entities | Identified in EventGuard retrace | Yes — just documentation |
| 6 | Computed field mapping scope | Identified in GIC retrace | Yes — just documentation |
| 7 | Bulk operations pattern | Identified, framed | No — needs real design |
| 8 | Pipeline dashboard layer | Sketched | No — needs rendering contract |
| 9 | Queue health tooling | Sketched | No — needs CLI surface design |
| 10 | Authentication | Sketched | No — needs dedicated design session |

Six of the ten require real design work before spec-readiness. Two are documentation clarifications. Two (coalescing, ephemeral locks) have shapes but need mechanism detail.

## Categorization for Tackling

**Must-design before spec (architectural):**
- Actor-context watch scoping + Temporal signal delivery (item 3) — most significant gap
- Watch coalescing (item 1) — proposed shape is solid but needs mechanism detail
- Ephemeral entity locks (item 2) — straightforward but needs protocol
- Bulk operations pattern (item 7) — EventGuard forces the issue

**Design before spec (supporting infrastructure):**
- Inbound webhook dispatch extension to Integration (item 4) — update the existing artifact
- Pipeline dashboard / base UI rendering contract (item 8)
- Queue health CLI surface (item 9)

**Separate session (own scope):**
- Authentication (item 10) — deserves its own design session

**Just documentation:**
- Internal vs external entities (item 5)
- Computed field mapping scope (item 6)

## What's Needed Before Spec

1. **A third trace.** Recommended: Indemn's own internal CRM use case. Removes insurance-specific assumptions entirely, tests the "kernel is domain-agnostic" claim directly, exercises actor-level integrations (personal Slack/Gmail/Calendar for team members) which neither GIC nor EventGuard did deeply. Dog-foods the "Indemn runs on the OS" thesis.

2. **Design passes on the architectural items** (1, 2, 3, 7 above). Each needs a focused session that produces a design artifact with enough detail that the mechanism is implementable. Item 3 is the most substantial and should probably come first.

3. **Auth design session** (item 10) — can happen in parallel with the other design passes since it's mostly orthogonal to the primitive mechanics.

4. **Documentation updates** (items 4, 5, 6) — can be folded into the spec-writing stage; no discussion needed.

5. **Simplification pass.** After all the design work lands, one more pass with fresh eyes asking "is this simpler than it needs to be?" Craig's instinct from session 4 was that a lot of this can be simplified. The design passes might add complexity that the simplification pass removes.

6. **Finally, write the spec.** One actionable document (or a small set of connected ones) clear enough that an engineer or agent can start building from it.

## Rough Sequence

```
CRM trace (third pressure test)
      ↓
Design session: Actor-context watches + signal delivery (the biggest gap)
      ↓
Design sessions in parallel: watch coalescing, ephemeral locks, bulk operations, pipeline dashboard, queue health, auth
      ↓
Documentation updates (inbound webhooks, entities vs counterparties, computed fields)
      ↓
Simplification pass
      ↓
Write the spec (white paper)
      ↓
Begin building
```

The CRM trace is recommended before the design sessions because it might surface more items that should be folded into the same design work. Better to collect all the findings, then design once across everything.

## What Two Traces Gave Us

Confidence that the kernel is real. Two different workload shapes, zero primitive changes, one real architectural gap and one set of documentation clarifications. The primitives are stable enough to be worth encapsulating. The remaining work is tooling, mechanism details, and supporting infrastructure — not core architecture.

We are closer to spec-ready than we were at the start of this session. Not there yet, but the path is clear.
