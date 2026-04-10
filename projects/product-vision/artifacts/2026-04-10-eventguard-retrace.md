---
ask: "Does the EventGuard end-to-end insurance flow (consumer quote → bind → pay → policy → certificate delivery, across 351 venues, fully automated) work cleanly on the updated 6-primitive kernel?"
created: 2026-04-10
workstream: product-vision
session: 2026-04-10-a
sources:
  - type: conversation
    description: "Craig and Claude tracing EventGuard against the updated architecture"
  - type: artifact
    description: "2026-04-10-gic-retrace-full-kernel.md (first retrace, different shape of workload)"
  - type: artifact
    description: "2026-04-10-integration-as-primitive.md (sixth primitive, used heavily by EventGuard)"
  - type: artifact
    description: "2026-04-10-base-ui-and-auth-design.md (identity providers as Integrations, ephemeral locks)"
  - type: local
    description: "EventGuard production context from business.md, product.md, platform-tiers-and-operations.md"
---

# EventGuard Retrace Against the Updated Kernel

## Purpose

Second pressure test of the updated architecture. GIC validated the kernel against a B2B email-driven submission pipeline with heavy HITL. EventGuard validates it against a fundamentally different shape of workload:

- **Consumer-facing**, not B2B
- **Real-time channels** (chat, voice, embedded widgets) as the primary entry point, not email polling
- **Payment integration** (Stripe) with both outbound calls and inbound webhooks
- **Fully autonomous flow** — no HITL in the happy path, the AI completes the entire transaction
- **High-volume distribution** — 351 venue deployments, each with venue-specific branding
- **Policy issuance** — EventGuard issues policies directly, it's not just a processing pipeline
- **Certificate generation** — PDFs delivered to consumers via email

If the kernel holds up for both GIC (B2B, email-heavy, HITL-rich) and EventGuard (consumer, real-time, payment-heavy, autonomous), that covers a wide surface.

## EventGuard Setup on the Kernel

### Organization

For this trace, assume Indemn is the org running EventGuard as a service offering. Jewelers Mutual (JM) is modeled as a Carrier entity within Indemn's org. A more sophisticated model might make JM its own org with Indemn acting as a platform operator — worth revisiting when we design the delegated-admin story for Tier 3.

```bash
indemn org create indemn --admin-email admin@indemn.ai
```

### Domain entities

Created as data via `indemn entity create`:

- **Venue** — a partner venue hosting an EventGuard widget. Fields: `name`, `address`, `contact_email`, `tier`, `branding_config`, `active_since`, `status`
- **VenueAgreement** — commercial relationship between EventGuard and a venue. Fields: `venue_id`, `revenue_share_pct`, `start_date`, `end_date`, `status`
- **Deployment** — a specific distribution surface (widget, landing page, voice endpoint) tied to a venue. Fields: `venue_id`, `surface_type`, `associate_id`, `branding_config`, `status`, `widget_snippet`, `metrics`
- **Interaction** — a live conversation between a consumer and an associate. Fields: `venue_id`, `deployment_id`, `channel_type`, `started_at`, `ended_at`, `status`, `transcript`, `linked_application_id`
- **Application** — a consumer's insurance application in progress. Fields: `venue_id`, `customer_name`, `customer_email`, `customer_phone`, `event_date`, `event_type`, `guest_count`, `coverage_selections`, `data` (flexible per product), `status`
- **Quote** — a priced quote for an application. Fields: `application_id`, `premium`, `coverages`, `quote_number`, `expires_at`, `status`
- **Policy** — a bound policy. Fields: `application_id`, `quote_id`, `policy_number`, `effective_date`, `expiration_date`, `premium`, `carrier_id`, `status`
- **Payment** — a Stripe charge record. Fields: `application_id`, `amount`, `currency`, `stripe_payment_intent_id`, `status`, `method`, `charged_at`
- **Certificate** — the policy document PDF. Fields: `policy_id`, `pdf_ref` (S3), `format`, `issued_at`
- **Customer** — the end consumer. Fields: `name`, `email`, `phone`
- **Carrier** — Jewelers Mutual as the underlying carrier. Fields: `name`, `binding_authority`, `product_config`

### Integrations (primitive #6)

All org-level. No actor-level integrations needed in EventGuard's happy path — the associates use the org's integrations to act on behalf of consumers.

```bash
# Stripe for payments
indemn integration create \
  --owner org \
  --name "EventGuard Stripe" \
  --system-type payment \
  --provider stripe \
  --provider-version stripe_2024_06_20 \
  --access-roles "quote_assistant,payment_processor,admin"

# LiveKit for voice channels
indemn integration create \
  --owner org \
  --name "EventGuard Voice" \
  --system-type voice \
  --provider livekit \
  --provider-version livekit_v2 \
  --access-roles "quote_assistant,admin"

# Twilio for SMS receipts
indemn integration create \
  --owner org \
  --name "EventGuard SMS" \
  --system-type sms \
  --provider twilio \
  --access-roles "delivery,admin"

# SendGrid (or similar) for outbound email delivery of certificates
indemn integration create \
  --owner org \
  --name "EventGuard Email Delivery" \
  --system-type email_outbound \
  --provider sendgrid \
  --access-roles "delivery,admin"

# PDF generation adapter (internal or external service)
indemn integration create \
  --owner org \
  --name "EventGuard Document Gen" \
  --system-type document_generation \
  --provider mint \
  --access-roles "certificate_issuer,admin"
```

### Methods activated on entities

```bash
# Application
indemn entity add-method Application auto-quote --evaluates rating-rule --produces Quote
indemn entity add-method Application completeness-check --evaluates required-field-rule

# Quote
indemn entity add-method Quote expire-stale --when '{"field": "expires_at", "op": "older_than", "value": "0s"}' --sets-field status:expired

# Payment
indemn entity add-method Payment charge --system-type payment --calls-adapter charge
indemn entity add-method Payment handle-webhook --system-type payment --calls-adapter parse_webhook

# Policy
indemn entity add-method Policy issue --from-quote --from-payment --generates-policy-number

# Certificate
indemn entity add-method Certificate generate --calls-adapter generate_pdf --uploads-to s3

# Interaction
indemn entity add-method Interaction close --sets-field status:closed,ended_at:now

# Deployment
indemn entity add-method Deployment bulk-create --input-csv
indemn entity add-method Deployment generate-widget-snippet
```

### Rules and lookups (per-org, EventGuard-specific)

```bash
# Rating rules for the EventGuard product
indemn rule create --entity Application --org indemn \
  --when '{"all": [{"field": "event_type", "op": "equals", "value": "wedding"}, {"field": "guest_count", "op": "lte", "value": 100}]}' \
  --action set-fields --sets '{"rating_tier": "small_wedding", "base_premium": 175}'

indemn rule create --entity Application --org indemn \
  --when '{"all": [{"field": "event_type", "op": "equals", "value": "wedding"}, {"field": "guest_count", "op": "gt", "value": 100}]}' \
  --action set-fields --sets '{"rating_tier": "large_wedding", "base_premium": 295}'

# Required fields for completeness
indemn required-field-rule create --org indemn --entity Application \
  --fields "customer_name,customer_email,event_date,event_type,venue_id,guest_count"

# Quote expiration threshold
indemn rule create --entity Quote --org indemn \
  --when '{"all": [{"field": "created_at", "op": "older_than", "value": "72h"}]}' \
  --action set-fields --sets '{"status": "expired"}'
```

### Roles with watches

```bash
# Named shared role for consumer-facing assistants
indemn role create quote_assistant \
  --permissions "read:Venue,read:Deployment,read:Application,write:Application,read:Quote,write:Quote,read:Payment,write:Payment,read:Interaction,write:Interaction" \
  --watches '[
    {"entity": "Interaction", "event": "created", "when": {"field": "channel_type", "op": "in", "value": ["chat", "voice"]}},
    {"entity": "Payment", "event": "transitioned", "when": {"field": "to", "op": "equals", "value": "completed"}, "scope": "actor_context"},
    {"entity": "Policy", "event": "created", "scope": "actor_context"}
  ]'

# Payment processor handles webhook-driven Payment updates
indemn role create payment_processor \
  --permissions "read:Payment,write:Payment" \
  --watches '[]'  # Entry-point-driven (Stripe webhooks), not watch-triggered

# Policy issuer creates Policy from completed Payment
indemn role create policy_issuer \
  --permissions "read:Application,read:Quote,read:Payment,read:Carrier,write:Policy" \
  --watches '[{"entity": "Payment", "event": "transitioned", "when": {"field": "to", "op": "equals", "value": "completed"}}]'

# Certificate issuer generates PDF for new policies
indemn role create certificate_issuer \
  --permissions "read:Policy,read:Application,read:Customer,write:Certificate" \
  --watches '[{"entity": "Policy", "event": "created"}]'

# Delivery actor sends certificate to customer via email + SMS
indemn role create delivery \
  --permissions "read:Certificate,read:Policy,read:Customer,write:Customer" \
  --watches '[{"entity": "Certificate", "event": "created"}]'

# Ops for monitoring and error handling
indemn role create ops \
  --permissions "read:all,write:Application,write:Policy" \
  --watches '[
    {"entity": "Payment", "event": "transitioned", "when": {"field": "to", "op": "equals", "value": "failed"}},
    {"entity": "Policy", "event": "transitioned", "when": {"field": "to", "op": "equals", "value": "error"}},
    {"entity": "Interaction", "event": "fields_changed", "when": {"field": "status", "op": "equals", "value": "abandoned"}}
  ]'

# Venue onboarder handles new venue setup (human-heavy)
indemn role create venue_onboarder \
  --permissions "read:Venue,write:Venue,read:VenueAgreement,write:VenueAgreement,read:Deployment,write:Deployment" \
  --watches '[{"entity": "Venue", "event": "created"}]'
```

Note the `scope: "actor_context"` on the quote_assistant watches for Payment and Policy — the associate should only be notified about events related to its current Interaction. This is a proposed scope qualifier on watches. More on this below in "What Surfaced."

### Associates

```bash
# The main real-time actor — runs the consumer conversation
indemn actor create --type associate --name "Quote Assistant" --role quote_assistant \
  --skill quote-assistant-skill \
  --mode reasoning \
  --llm-config '{"model": "claude-sonnet-4-6", "temperature": 0.3}'

# Policy issuer — deterministic binding
indemn actor create --type associate --name "Policy Issuer" --role policy_issuer \
  --skill policy-issuance-skill \
  --mode hybrid

# Certificate generator — deterministic PDF gen
indemn actor create --type associate --name "Certificate Generator" --role certificate_issuer \
  --skill certificate-generation-skill \
  --mode hybrid

# Delivery actor — sends certificate via email and SMS
indemn actor create --type associate --name "Delivery" --role delivery \
  --skill delivery-skill \
  --mode hybrid

# Scheduled: expire stale quotes
indemn actor create --type associate --name "Quote Expiration Checker" --role quote_expirer \
  --trigger "schedule:0 * * * *" \
  --permissions "read:Quote,write:Quote" \
  --watches '[]' \
  --skill quote-expiration-skill \
  --mode hybrid
```

### Human actors

```bash
indemn actor create --type human --name "EventGuard Ops" --email ops@indemn.ai
indemn actor add-role ops@indemn.ai --role ops
indemn actor add-role ops@indemn.ai --role venue_onboarder

indemn actor create --type human --name "George" --email george@indemn.ai
indemn actor add-role george@indemn.ai --role ops
```

## The End-to-End Flow

### Phase 1: Venue onboarding (admin/setup)

**Trigger**: Admin runs CLI to create a new venue partnership.

```bash
indemn venue create \
  --name "Grand Garden Estate" \
  --address "..." \
  --contact-email "events@grandgarden.com" \
  --tier "preferred"

indemn venue-agreement create \
  --venue VENUE-047 \
  --revenue-share-pct 15 \
  --start-date "2026-04-15"

indemn deployment create \
  --venue VENUE-047 \
  --surface-type web-embed \
  --associate "Quote Assistant" \
  --branding @venues/VENUE-047/branding.json

indemn deployment generate-widget-snippet DEP-047
# Returns JavaScript snippet to paste on venue's website
```

**What happens under the hood**:
- Venue, VenueAgreement, and Deployment entities created (each in their own transactions)
- Deployment:created event → `venue_onboarder` watch matches → Ops sees a queue item "new venue deployed, verify configuration"
- The widget snippet is the customer-visible artifact; paste it on the venue's site and the widget activates on page load

**For 351 venues**: 
```bash
indemn deployment bulk-create --from-csv @venues.csv --template event-guard-widget
```

The `bulk-create` method on Deployment is a kernel capability. It reads the CSV, creates entities in batches (e.g., 50 per transaction), and emits one summary event per batch plus coalesced events for operations visibility. This is where the proposed **bulk operations** and **watch coalescing** features earn their keep.

### Phase 2: Consumer interaction begins (real-time entry point)

**Trigger**: A consumer visits the Grand Garden Estate website. The widget loads in their browser, opens a WebSocket connection to the OS's channel infrastructure.

**What happens**:

1. Channel infrastructure (WebSocket server) receives the connection. Extracts the Deployment ID from the widget snippet.
2. Creates an **Interaction** entity:
   ```
   {
     deployment_id: "DEP-047",
     venue_id: "VENUE-047",
     channel_type: "chat",
     status: "active",
     started_at: "2026-04-10T14:30:00Z"
   }
   ```
3. Interaction:created event → watches evaluate. `quote_assistant` watch matches on `channel_type in ["chat", "voice"]`.
4. **Real-time path** (per ironing round 1 resolution): queue entry created + direct invocation of the Quote Assistant associate simultaneously. The direct invocation claims the queue entry immediately.
5. Temporal workflow starts for the Quote Assistant with the Interaction ID in context.
6. Workflow loads the associate's skill, loads the Interaction + linked Deployment + Venue (with branding config).
7. Opens the WebSocket connection as I/O for the associate.
8. Associate sends first message: "Hi! I can help you get event insurance for Grand Garden Estate. What's the date of your event?"

**Latency check**: direct invocation path skips queue polling. First response latency is LLM-bound (~1-2s), not queue-bound. Matches the GIC retrace's real-time analysis.

### Phase 3: The conversation (entity updates during active dialog)

As the consumer answers questions, the associate captures data by updating the Application entity.

```
Consumer: "June 15th"
  → Associate: [creates Application entity linked to the Interaction, sets event_date]
  → Associate: "How many guests are you expecting?"

Consumer: "About 150"  
  → Associate: [updates Application.guest_count]
  → Associate: "What type of event is this — wedding, corporate, birthday?"

Consumer: "Wedding"
  → Associate: [updates Application.event_type]
  → [Application.event_type + guest_count now sufficient for rating]
```

**Emission behavior**: These field updates don't trigger @exposed method invocations, so per selective emission rules, they don't generate messages. No cascade. Good — we don't want other actors reacting to partial application state.

Exception: when the associate calls `indemn application create` at the start, that IS an @exposed creation and generates an Application:created event. But no watches are configured for that (no one cares about unpriced applications).

**Transaction granularity**: Each user turn produces an entity update that's committed before the next user turn. These are small, fast transactions. The associate maintains conversation state in its Temporal workflow context; if the worker crashes, the workflow replays and resumes from the last completed activity (last entity update). The conversation resumes with "Sorry, let me confirm — you said 150 guests for a wedding on June 15th?"

### Phase 4: Quote generation (deterministic via kernel capability)

Once the required fields are collected, the associate calls the quote method:

```
Associate: [calls indemn application quote APP-091 --auto]
```

**What happens**:
1. `auto-quote` method on Application loads rating rules for this org
2. Evaluates rules against the application fields
3. Matches the large_wedding rule (event_type=wedding, guest_count>100) → base_premium=295
4. Applies coverage adjustments from customer selections
5. Creates a Quote entity with status=active, expires_at=now+72h
6. Transaction commits: Application.status=quoted + Quote created + Application.quote_id set
7. Two events emitted: Quote:created and Application:transitioned[to=quoted]

No LLM invoked for the quote itself — it's entirely rule-driven. This is the `--auto` pattern paying off for a standardized product.

**Associate continues the conversation**:
```
"Based on your event details, your quote is $295 for full event cancellation coverage. 
 Shall I get this set up for you?"
```

### Phase 5: Payment (outbound Integration + inbound webhook)

```
Consumer: "Yes, let's do it."
```

The associate creates a Payment entity and initiates the Stripe flow:

1. `indemn payment create --application APP-091 --amount 295 --currency usd`
2. Creates Payment entity in status=pending
3. `indemn payment charge PAY-091` — charge method on Payment entity
4. `charge` method resolves the Stripe Integration (owner=org=indemn, system_type=payment, active)
5. Fetches credentials from Secrets Manager via secret_ref
6. Calls StripeAdapter.create_payment_intent(amount, currency, metadata={application_id: APP-091})
7. Stripe returns a client_secret
8. Payment updated with stripe_payment_intent_id
9. Associate sends the client_secret to the chat widget UI, which renders Stripe Elements
10. Consumer enters card details in Stripe's hosted UI (not the chat)
11. Stripe processes the charge client-side
12. Meanwhile, the associate tells the consumer: "Great, I've prepared your payment form. Let me know once you've completed the payment."

### Phase 6: Stripe webhook (inbound Integration)

After Stripe processes the payment, it sends a webhook to the OS.

**Entry point**: `POST /webhook/stripe/{integration_id}`

1. OS webhook handler receives the POST. Looks up Integration by ID.
2. Gets Stripe adapter for the Integration's provider_version.
3. Calls `adapter.validate_webhook(headers, body)` — validates signature using webhook secret from Secrets Manager.
4. On valid signature: calls `adapter.parse_webhook(body)` — returns a structured event describing the entity changes to apply.
5. For `payment_intent.succeeded`: the adapter returns `{target_entity: "Payment", lookup_by: "stripe_payment_intent_id", lookup_value: "pi_abc123", updates: {status: "completed", charged_at: "2026-04-10T14:38:00Z"}}`
6. Kernel applies the updates via Payment entity methods (so state machine enforcement and audit trail work).
7. Payment save → Payment:transitioned[to=completed] event → watches fire.

**Key point**: the webhook handler is **infrastructure**, not an actor. It's an entry point that creates/updates entities. Once the entity changes, the kernel takes over via watches.

### Phase 7: Policy issuance (watch-triggered, deterministic associate)

**Trigger**: `policy_issuer` watch matches `Payment:transitioned[to=completed]`.

1. Queue Processor writes a message to message_queue targeting `policy_issuer` role.
2. Policy Issuer associate (Temporal workflow) claims it.
3. Loads Payment + linked Application + Quote + Carrier.
4. Verifies Quote is still valid (not expired).
5. Calls `indemn policy issue --application APP-091 --quote QUO-091 --payment PAY-091`
6. The `issue` method:
   - Generates policy_number (e.g., EG-2026-00023456)
   - Creates Policy entity with effective/expiration dates from Application
   - Transitions Policy to status=active
   - All in one transaction: Policy created + Application.status=policy_issued + Application.policy_id set
7. Two events: Policy:created + Application:transitioned[to=policy_issued].
8. Policy Issuer marks its message complete.

### Phase 8: Certificate generation (watch-triggered)

**Trigger**: `certificate_issuer` watch matches `Policy:created`.

1. Certificate Generator claims the message.
2. Loads Policy + Application + Customer.
3. Calls `indemn certificate generate --policy POL-091`
4. The `generate` method:
   - Loads the PDF template for this product (EventGuard event cancellation cert)
   - Resolves the document_generation Integration (Mint adapter)
   - Calls adapter.generate_pdf(template, data) → returns PDF bytes
   - Uploads PDF to S3 at `s3://indemn-files/eventguard/certificates/POL-091.pdf`
   - Creates Certificate entity with pdf_ref
5. Transaction: Certificate created.
6. Certificate:created event.

### Phase 9: Delivery (watch-triggered)

**Trigger**: `delivery` watch matches `Certificate:created`.

1. Delivery associate claims.
2. Loads Certificate + Policy + Customer.
3. Sends certificate via email (SendGrid Integration):
   - `indemn email send --to {customer.email} --template certificate-delivery --attach {certificate.pdf_ref}`
   - Method resolves the email_outbound Integration, sends via SendGrid adapter
4. Sends SMS notification (Twilio Integration):
   - `indemn sms send --to {customer.phone} --message "Your EventGuard policy is confirmed. Certificate sent to your email."`

### Phase 10: Real-time update to the consumer (THE TRICKY PART)

**The question**: the Quote Assistant associate is still in a live conversation with the consumer. How does it find out the policy is done so it can tell the consumer "All set! Your policy is confirmed"?

**The problem**: watches generate queue messages, but a running real-time actor isn't polling a queue during an active interaction. The Quote Assistant's Temporal workflow is holding the WebSocket and waiting for the next user message or an external signal.

**Approach 1: Watch-triggered Temporal signals.** The Quote Assistant's watches include `Policy:created[scope:actor_context]`. When the watch fires for a Policy whose application_id matches the Quote Assistant's current Interaction's linked_application_id, the kernel sends a Temporal signal to the running workflow. The workflow handles the signal by sending a proactive message to the WebSocket: "All set! Your policy is confirmed."

This requires the kernel to understand "actor_context scope" — meaning the watch matches only entities related to the actor's current working context (the Interaction it's handling). And the kernel needs a bridge from "watch fires" to "Temporal signal to a specific workflow instance."

**Approach 2: Polling during the conversation.** The Quote Assistant periodically (every 1-2 seconds) queries its own queue for messages. When a matching message arrives, it processes it. This is simpler but adds latency and query load.

**Approach 3: Event subscription via a dedicated mechanism.** The associate, during an active conversation, subscribes to events tagged with its Interaction's correlation_id. A lightweight pub/sub layer delivers matching events to subscribers. This works but introduces a new mechanism not currently in the architecture.

**My recommendation**: Approach 1 (Temporal signals bridged from watches) is cleanest. It requires:
- A watch scope qualifier (`actor_context` meaning "only match entities related to my current Interaction")
- A kernel mechanism that bridges watch matches to Temporal workflow signals when the target workflow is running
- The Quote Assistant's Temporal workflow declaring a signal handler for mid-interaction updates

This is the most architecturally significant finding from the EventGuard retrace. It's a kernel addition — not just a UI concern like GIC's bulk coalescing. **Real-time actors need a mid-conversation event delivery mechanism.**

### Phase 11: Interaction closure

Once the policy is confirmed and the associate sends the confirmation message, the consumer typically responds "thanks!" or closes the widget. The associate:

1. Sends a wrap-up message
2. Calls `indemn interaction close INT-091` (transitions Interaction to closed, sets ended_at)
3. Interaction:transitioned[to=closed] event
4. Ops role doesn't watch for closed interactions in the happy path (only abandoned ones)
5. Temporal workflow completes, WebSocket closes

### Phase 12: Quote expiration (scheduled cleanup)

Every hour, the Quote Expiration Checker runs:

1. Schedule fires → creates queue item for `quote_expirer` role
2. Quote Expiration Checker claims, calls `indemn quote expire-stale`
3. Method finds all Quotes where status=active AND expires_at < now
4. Bulk update: sets status=expired on matching quotes
5. Events emitted per update (possibly coalesced, depending on watch configuration)
6. No downstream watches care about expired quotes in EventGuard's simple model

## What Held Up

1. **Integration as primitive works for both outbound and inbound.** Stripe charges (outbound via adapter.charge) and Stripe webhooks (inbound via adapter.parse_webhook) both flow through the same Integration primitive. The adapter interface covers both directions.

2. **Webhooks as entry points are clean.** The kernel has a generic webhook endpoint `/webhook/{provider}/{integration_id}` that dispatches to the Integration's adapter for validation and parsing. No new primitive needed — Integration naturally extends to inbound.

3. **Real-time channel activation via direct invocation works.** Interaction entity created at connection open, direct invocation of the associate skips queue-poll latency. Matches the design from ironing round 1.

4. **Multi-actor choreography via watches.** Payment → Policy → Certificate → Delivery, each step is a separate actor watching the previous event. No orchestration code, no explicit workflow definition — the pipeline emerges from watches.

5. **Fully autonomous flow validates the kernel's neutrality.** GIC has lots of HITL; EventGuard has none in the happy path. Same primitives work for both. The kernel doesn't prescribe HITL — it's a policy choice per role/watch. This validates the "kernel is domain-agnostic" claim.

6. **High-volume deployments via bulk operations.** 351 Deployments created via `indemn deployment bulk-create --from-csv`. Bulk operations as a first-class capability is exercised here. No per-venue customization beyond branding config stored on the Deployment.

7. **One associate serves all 351 venues.** The Quote Assistant loads venue-specific branding from the Deployment at conversation start. No need for 351 associate actors. The skill knows how to query for Deployment→Venue context.

8. **Selective emission handles conversation state.** Field updates during active dialog don't trigger cascading watches because they're not @exposed method calls. Only meaningful state transitions and explicit method invocations generate messages. Prevents watch storms from per-turn updates.

9. **Certificate PDF generation via Integration.** Document generation is an Integration (Mint adapter). Treats PDF generation as another external system connection, consistent with how everything else works. No special case.

10. **Crash recovery during real-time**: Temporal workflow replay recovers conversation state from entity reads. The associate resumes with "Let me confirm what you told me so far..." — not ideal UX but no data loss. Acceptable for the rarity of mid-conversation worker crashes.

## What Surfaced (New — Not in GIC)

### 1. Real-time actor mid-conversation event delivery — KERNEL ADDITION

**The problem**: A running real-time actor holding an open channel needs to receive events related to its current Interaction as they happen. Watches generate queue messages, but queue-polling isn't appropriate for sub-second delivery during a live conversation.

**Classification**: Architectural gap. Not a usability concern — a missing mechanism.

**Proposed mechanism**: 
- Watches support a `scope: "actor_context"` qualifier, meaning "only match entities related to the claiming actor's current working context."
- The kernel maintains a mapping of (actor_id → current_context_entity_id) for actors currently processing interactions.
- When a watch with actor_context scope fires, the kernel checks if the matching entity is in the scope of any currently-active actor. If yes, the kernel sends a Temporal signal (or equivalent) to that actor's running workflow instead of writing to the queue.
- The real-time associate's workflow declares a signal handler for these mid-context events.

This is additive to the existing watch model. Regular watches still write to the queue. Actor-context watches signal running workflows when applicable, fall back to queue writes otherwise.

**Alternative considered**: polling during conversation. Rejected because it adds latency and query load for the fast-path case.

### 2. Webhook handling as an Integration extension

**The observation**: GIC's integrations were all outbound (fetch emails from Outlook, send drafts via email, call carrier APIs). EventGuard introduces inbound: Stripe webhooks arriving at the OS.

**Finding**: Integration as primitive #6 naturally extends to inbound, but the Integration artifact didn't explicitly cover this. Adapters need both outbound methods (charge, fetch, send) and inbound methods (validate_webhook, parse_webhook, auth_initiate for OAuth).

**Classification**: Documentation clarification, not a new primitive. The Integration artifact should be updated to explicitly describe:
- Inbound webhook dispatch at `/webhook/{provider}/{integration_id}`
- Adapter interface with both outbound and inbound methods
- Webhook validation via the Integration's secret_ref
- Parsing webhooks into structured entity operations (not raw entity updates — go through entity methods for state machine enforcement)

### 3. Actor-context scoping for watches

**The observation**: The quote_assistant's watches include Payment and Policy events, but only those related to its current Interaction's application. A naive implementation would deliver ALL payment completions to every quote_assistant, which is wrong.

**Finding**: Watches need a scoping qualifier that references the claiming actor's context. Proposed syntax: `scope: "actor_context"` with the kernel understanding that actor_context means "related entities traversed from the actor's current working entity" (its active Interaction, in the real-time case).

This is related to #1 but more general. It could also apply to non-real-time actors: an underwriter watching for events related to submissions they've claimed but not yet completed. Useful for coordinating multi-step human work.

**Classification**: Small kernel addition. Extends watches with a scope qualifier. The kernel needs a lightweight concept of "what's this actor currently working on" — for real-time, it's the open Interaction; for others, it's the message they've claimed. Straightforward.

### 4. Bulk operations as a first-class pattern

**The observation**: EventGuard has 351 venues. Creating them one at a time is impractical. The bulk-create capability is exercised here.

**Finding**: This was flagged in the pressure test findings from session 4 as a deferred item. EventGuard is a concrete use case. Worth prioritizing in the spec. Design questions:
- Batch size for transactions (how many entities per transaction?)
- Event emission for bulk operations (per-entity events or batch-level events?)
- Coalescing (this is where watch coalescing pays off — bulk creation of 351 Deployments should not spam the venue_onboarder queue)
- Progress reporting and rollback on partial failure
- Idempotency (bulk operations must be re-runnable)

### 5. Dog-fooding the base UI for the platform itself

EventGuard is Indemn's own product. Running it on the OS means the Indemn team uses the base UI to monitor and operate it. The base UI's dashboards, integration management, actor management — all apply. This is the "Indemn runs on the OS" thesis in practice.

The analytics Craig specifically asked for (metrics, aggregations, reporting on system changes) are directly relevant here:
- Conversion rate per venue (Applications → Policies)
- Revenue per venue (Policies × premium)
- Quote abandonment rate (Applications → quoted → not paid)
- Average conversation duration
- Policy issuance latency (payment_completed → certificate_delivered)
- Integration health (Stripe webhook delivery success rate, LiveKit uptime)

All sourced from the changes collection + message log + entity aggregations. No new primitives needed — just default dashboards in the base UI.

### 6. Consumer identity is implicit, not an Actor

The consumer buying event insurance is NOT an Actor in the OS. They don't have a role, they don't log in, they don't appear in the actor list. They're a Customer entity with contact info. The Interaction is between the Quote Assistant actor and a (non-actor) customer via a channel.

This is different from GIC, where the consumer-side doesn't really exist — everything is internal (underwriters, CSRs) plus external actors (retail agents) who are Agent entities but don't log in either.

**Finding**: The Actor primitive is for internal participants (employees, associates, platform users). External consumers and counterparties are Customer/Agent/Carrier entities without auth. This is fine — it matches how the architecture already works — but worth making explicit in the spec.

## What's Still Domain, Not Kernel

- Rating rules for event insurance (per-org config)
- Required fields for applications (per-org config)  
- Certificate PDF template (product config)
- Venue branding details (on Deployment entity)
- Specific conversation flow for wedding insurance (skill for quote_assistant)
- Business rules about quote validity, cancellation windows, etc.

All of this is data/skills/rules, not kernel primitives. The kernel is unchanged — EventGuard is configured on it.

## Verdict

**The kernel holds up for EventGuard.** The 6-primitive model supports a completely different shape of workload than GIC — consumer-facing, real-time, payment-heavy, fully autonomous, high-volume distribution — without requiring any primitive changes.

**One kernel addition needed** that didn't come up in GIC:
- **Actor-context watch scoping + Temporal signal delivery for real-time actors.** Running real-time actors receive mid-conversation event updates via Temporal signals when watches fire for entities related to their current working context. This needs explicit design but is additive (the existing watch → queue path is unchanged).

**Several things validated**:
- Integration as primitive covers both outbound and inbound external connectivity
- Watches handle multi-actor choreography across the full quote→bind→pay→policy→certificate→deliver pipeline
- The kernel-vs-domain separation holds — all EventGuard business logic is data
- Fully autonomous flows work with zero HITL — the kernel doesn't mandate HITL
- One associate can serve thousands of distribution surfaces (no per-deployment associate proliferation)
- Crash recovery via Temporal replay + entity reads works for real-time (with a degraded UX of "let me re-confirm where we were")

**Things to document in the spec** (not new primitives, but things the Integration artifact and overall architecture should cover explicitly):
- Inbound webhook dispatch via Integration adapters
- Bulk operations patterns (bulk-create, bulk-update, transaction batching, progress reporting)
- Actor-context scope qualifier on watches
- Real-time actor signal delivery
- The distinction between internal Actors (who authenticate) and external entities like Customer/Agent/Counterparty (who don't)

## Cross-Trace Comparison: GIC vs. EventGuard

| Dimension | GIC | EventGuard |
|-----------|-----|-----------|
| Workload shape | B2B email pipeline | Consumer real-time + autonomous |
| Primary entry point | Scheduled Outlook polling | Real-time channel activation + webhooks |
| HITL | Heavy (JC reviews, Maribel ops) | None in happy path |
| Number of distinct associates | ~7 | ~5 |
| Primary Integrations | Outlook, AMS (future), carrier APIs (future) | Stripe, LiveKit, Twilio, SendGrid, Mint |
| Deployments | 1 org, 1 setup | 351 deployment entities |
| Volume shape | Batch-burst (email sync produces 10-50 at a time) | Continuous real-time + scheduled expiration |
| Kernel additions surfaced | Coalescing, ephemeral locks, pipeline dashboards | Actor-context watch scoping + Temporal signals, bulk operations pattern |
| Validated primitives | Entity, Message, Actor, Role, Org, Integration | All six + heavier exercise of Integration (inbound + outbound) and real-time channels |

Together, the two traces give good confidence that the kernel is not secretly shaped for one workload type. A CRM retrace as the third would further validate the domain-agnostic claim by removing insurance-specific assumptions entirely.

## Open Items From This Trace

- **Design actor-context watch scoping + Temporal signal delivery for real-time actors.** This is the main architectural gap. Not a new primitive, but a new mechanism on existing primitives. Needs its own focused design.
- **Document inbound webhook dispatch in the Integration primitive**. Update the integration artifact to cover adapters having both outbound and inbound methods, webhook endpoint dispatch, webhook signature validation via secret_ref.
- **Design bulk operations patterns**. Batch size, transactions, event emission, coalescing, progress reporting, idempotency, rollback. EventGuard is the concrete use case.
- **Clarify internal Actors vs. external entities** in the spec. Actors authenticate and have roles; Customers/Agents/Counterparties are entities without auth. Both concepts exist; both are valid.
- **Real-time crash recovery UX** — the "let me re-confirm where we were" pattern is acceptable but worth designing explicitly. What information is restored from the entity? What's lost from in-memory workflow state?
