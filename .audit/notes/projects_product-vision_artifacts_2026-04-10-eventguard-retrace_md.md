# Notes: 2026-04-10-eventguard-retrace.md

**File:** projects/product-vision/artifacts/2026-04-10-eventguard-retrace.md
**Read:** 2026-04-16 (full file — 641 lines)
**Category:** design-retrace

## Key Claims

- **Second pressure test**: consumer-facing, real-time channels (chat/voice/widgets), Stripe payments with inbound webhooks, fully autonomous flow, 351 venues, policy issuance, PDF certificate delivery.
- **End-to-end flow traced**: venue onboarding → widget activation → real-time consumer chat → progressive Application build → rule-driven Quote → Stripe payment (outbound + inbound webhook) → Policy issuance → Certificate generation → email+SMS delivery → interaction close.
- **KERNEL ADDITION surfaced**: **Real-time actor mid-conversation event delivery.** A running real-time actor holding a WebSocket can't queue-poll for sub-second event delivery. Needs Temporal-signal-based delivery bridged from matching watches.
- **Solution**: watches gain `scope: "actor_context"` qualifier → kernel maintains (actor_id → current_context_entity_id) mapping for active actors → matching watch sends Temporal signal to running workflow (not a queue write).
- **Integration primitive validated for inbound**: kernel `POST /webhook/{provider}/{integration_id}` + adapter methods `validate_webhook` and `parse_webhook` + `WebhookResult` structure applied via entity methods (state-machine enforcement preserved).
- **One associate serves 351 venues** — Quote Assistant loads per-venue Deployment + branding config at conversation start.
- **Selective emission discipline protects from watch storms** during conversation: mid-turn field updates don't trigger emissions because they're not @exposed method calls; only state transitions + @exposed calls + create/delete emit.
- **Fully autonomous flow validates kernel-is-not-HITL-biased** — zero HITL in happy path, same primitives.
- **Crash recovery UX during real-time**: Temporal replays workflow, agent resumes with "let me confirm where we were..." — acceptable degraded UX.
- **Consumer is NOT an Actor** — external counterparty entity (Customer with email/phone). No auth, no role, no queue. Establishes distinction internal-Actor vs external-entity.
- **Approach 1 (Temporal signals bridged from watches) recommended** for mid-conversation event delivery. Approaches 2 (polling) and 3 (pub/sub) rejected.

## Architectural Decisions

- **Real-time entry point pattern**: channel infrastructure accepts connection → creates Interaction entity → Interaction:created event → watch matches → direct invocation claims queue entry (parallel path) → Temporal workflow starts → workflow holds WebSocket as I/O.
- **Outbound + inbound Integration methods** unified under one Adapter interface (fetch/send/charge + validate_webhook/parse_webhook + auth_initiate).
- **Webhook handler is infrastructure, not an actor** — an entry point. Kernel applies resulting entity ops through entity methods (not raw).
- **WebhookResult** = structured `{entity_type, lookup_by, lookup_value, operation, params}`.
- **Actor-context watch scoping** = new kernel mechanism. Extends watches with scope qualifier referencing claiming actor's current working context.
- **Temporal signals to running workflows** = the delivery mechanism for `actor_context` scoped events when target actor's workflow is active.
- **Bulk operations as first-class**: `indemn deployment bulk-create --from-csv` → batches of ~50 per txn → coalesced events for ops visibility.
- **Per-venue branding via Deployment entity config** — no per-venue associate proliferation.

## Layer/Location Specified

- **Channel infrastructure (WebSocket server, voice transport)** = lives in harness. Per 2026-04-10-realtime-architecture-design, the transport is bundled with the Runtime deployment. So the WebSocket server is in `indemn/runtime-chat-deepagents` image (chat) and LiveKit Agents runs in `indemn/runtime-voice-deepagents` image.
- **Temporal workflows hold WebSocket as I/O** — this means the real-time workflow runs in the harness (the harness image has the workflow), not in the kernel.
- **Webhook endpoint**: `kernel/api/webhook.py` (kernel).
- **Adapter base class + interface**: `kernel/integration/adapter.py` (kernel).
- **Adapter implementations**: `kernel/integration/adapters/stripe_adapter.py`, etc. (kernel).
- **Adapter registry**: `kernel/integration/registry.py` (kernel).
- **Integration resolver**: `kernel/integration/resolver.py` (kernel, resolves org-level Integrations for adapter use).
- **`scope: actor_context` evaluation + Temporal signal delivery**: kernel-level watch system + new signal bridge.
- **One Temporal workflow per active conversation** = runs in the chat-harness process.
- **Temporal-signal bridge**: likely lives in the kernel (watch-evaluator writes to Temporal API when `actor_context` scoped match + target workflow active).

**Finding 0 relevance**:
- EventGuard's real-time flow (Phase 2+) REQUIRES the harness pattern. Without chat-harness image, no real-time consumer interactions. Without async-harness, no scheduled quote expiration. Without voice-harness, no voice-channel EventGuard.
- The whole "Quote Assistant holds open WebSocket + receives Temporal signals for mid-conversation Policy:created events" is IMPOSSIBLE in the current implementation (no harnesses).
- Phase 5 consolidated spec's voice-harness example was inspired by EventGuard (mirrored in the spec example). But the chat-harness is also needed and is MISSING from the spec.

## Dependencies Declared

- Stripe (payment provider; provider_version `stripe_2024_06_20`)
- LiveKit (voice provider)
- Twilio (SMS)
- SendGrid (outbound email delivery)
- Mint (document generation — PDF certificates)
- MongoDB Change Streams (for real-time UI updates, separate from Temporal signals)
- Temporal Cloud (workflows, signals, replay)
- S3 (certificate storage)
- AWS Secrets Manager (Stripe webhook secret, etc.)

## Code Locations Specified

- Entity set (all kernel-created via CLI): `Venue, VenueAgreement, Deployment, Interaction, Application, Quote, Policy, Payment, Certificate, Customer, Carrier`.
- Method activations: `auto-quote`, `completeness-check`, `expire-stale` (scheduled), `charge`, `handle-webhook`, `issue`, `generate` (certificate), `close` (interaction), `bulk-create` (deployment), `generate-widget-snippet`.
- Rules (EventGuard-specific): rating, required-fields, quote-expiration.
- Roles: `quote_assistant, payment_processor, policy_issuer, certificate_issuer, delivery, ops, venue_onboarder`, + scheduled `quote_expirer`.
- Associates: `Quote Assistant` (reasoning mode, Claude Sonnet 4.6), `Policy Issuer` (hybrid), `Certificate Generator` (hybrid), `Delivery` (hybrid), `Quote Expiration Checker` (scheduled).
- **Per design**: Quote Assistant + Policy Issuer + Certificate Generator + Delivery → async-deepagents or chat-deepagents harness instances depending on Runtime kind. Quote Assistant is chat-kind (real-time) → chat-deepagents. Others are async-kind → async-deepagents.
- **Per current code**: NONE exist; all kernel-side Temporal activities.

## Cross-References

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

## Open Questions or Ambiguities

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
