---
ask: "Resolve the five documentation items from the post-trace synthesis — clarifications and formalizations that don't require new architectural decisions, just explicit capture of what was already designed."
created: 2026-04-13
workstream: product-vision
session: 2026-04-13-a
sources:
  - type: artifact
    description: "2026-04-10-integration-as-primitive.md (Integration primitive — needs inbound webhook extension)"
  - type: artifact
    description: "2026-04-10-eventguard-retrace.md (surfaced items 4 and 5)"
  - type: artifact
    description: "2026-04-10-gic-retrace-full-kernel.md (surfaced item 6)"
  - type: artifact
    description: "2026-04-10-crm-retrace.md (surfaced items 11 and 12)"
  - type: artifact
    description: "2026-04-10-realtime-architecture-design.md (Runtime + Associate entity with owner_actor_id)"
  - type: artifact
    description: "2026-04-11-authentication-design.md (default assistant auth model, owner-bound associate auth model)"
  - type: artifact
    description: "2026-04-10-post-trace-synthesis.md (categorized these as items 4, 5, 6, 11, 12)"
---

# Documentation Sweep — Five Clarifications

## Context

Items 4, 5, 6, 11, and 12 from the post-trace synthesis. These are not architectural decisions — they are clarifications and formalizations of design that already emerged from the retraces and design sessions. Each was identified, discussed, and resolved during prior work but never captured in a dedicated place. This artifact makes them explicit for the spec.

## Item 4: Inbound Webhook Dispatch via Integration Adapters

### What was surfaced

The EventGuard retrace exposed that Integration adapters need both outbound methods (charge, fetch, send) and inbound methods (validate_webhook, parse_webhook). The integration-as-primitive artifact described outbound connectivity but didn't explicitly cover how inbound webhooks enter the OS.

### The clarification

**Inbound webhooks are an entry point, not an actor.** They are infrastructure that creates or updates entities, after which the kernel takes over via watches. The webhook handler is a kernel-provided generic endpoint, not a per-provider endpoint.

**Endpoint**: `POST /webhook/{provider}/{integration_id}`

**Flow**:
1. External system (Stripe, Granola, Slack, etc.) sends a POST to the endpoint.
2. Kernel looks up the Integration by ID. Validates the Integration is active and matches the provider.
3. Gets the adapter for the Integration's `provider_version` from the adapter registry.
4. Calls `adapter.validate_webhook(headers, body)` — validates the webhook signature using the Integration's secret_ref (fetched from Secrets Manager). Rejects invalid signatures with 401.
5. Calls `adapter.parse_webhook(body)` — returns a structured description of what entity operations to perform.
6. Kernel applies the operations via entity methods (not raw updates). State machine enforcement, permission checks, and event emission all work normally.
7. Returns 200 to the external system.

**Adapter interface extension**:

```python
class Adapter(ABC):
    # Outbound (already documented)
    @abstractmethod
    async def fetch(self, **params) -> list[dict]: ...
    
    @abstractmethod
    async def send(self, payload: dict) -> dict: ...
    
    @abstractmethod
    async def charge(self, amount: Decimal, **params) -> dict: ...
    
    # Inbound (this clarification)
    @abstractmethod
    async def validate_webhook(self, headers: dict, body: bytes) -> bool: ...
    
    @abstractmethod
    async def parse_webhook(self, body: dict) -> WebhookResult: ...
    
    # Auth initiation (for OAuth flows — already implied by the auth design)
    @abstractmethod
    async def auth_initiate(self, redirect_uri: str) -> str: ...
```

**`WebhookResult` structure**:
```python
WebhookResult = {
    "entity_type": str,           # "Payment"
    "lookup_by": str,             # "stripe_payment_intent_id"
    "lookup_value": str,          # "pi_abc123"
    "operation": str,             # "transition" | "update" | "create"
    "params": dict,               # {"to_status": "completed", "charged_at": "..."}
}
```

The kernel resolves the entity using `lookup_by` + `lookup_value`, then applies the operation via the entity's own methods. This ensures state machine enforcement and event emission work normally — webhooks don't bypass entity integrity.

**Not all adapters need inbound methods.** An AMS adapter that only pushes data outbound doesn't implement `validate_webhook` or `parse_webhook`. The base Adapter class provides default implementations that raise `NotImplementedError`. The kernel only registers the webhook endpoint for Integrations whose adapter implements the inbound interface.

**Security**: webhook validation is per-provider. Stripe uses signature verification via a webhook secret. Slack uses request signing. Google uses push notification tokens. Each adapter handles its provider's specific validation mechanism, using the Integration's secret_ref for the verification key.

## Item 5: Internal Actors vs External Counterparty Entities

### What was surfaced

The EventGuard retrace noted: "The consumer buying event insurance is NOT an Actor in the OS. They don't have a role, they don't log in, they don't appear in the actor list. They're a Customer entity with contact info." The CRM retrace reinforced: "External counterparties (Customer, retail Agent, partner Carrier) are entities without auth."

### The clarification

The OS has two categories of "people and organizations" and they live in different parts of the primitive model:

**Internal Actors** — authenticate, have roles, process triggers, appear in the actor list:
- Human users (Indemn staff, customer org employees, Tier 3 developers)
- Associates (AI agents with skills and execution modes)
- Authenticated via Session (see authentication design)
- Have roles that determine permissions and watches
- Process messages from the queue, take actions via CLI/API
- First-class in the Actor bootstrap entity

**External counterparty entities** — domain data, no authentication, no roles:
- Customers buying insurance (EventGuard consumers)
- Retail agents submitting business (GIC's retail agent contacts)
- Carrier contacts (underwriters at USLI, Hiscox)
- Any person or organization that is the subject of work but doesn't log into the OS
- Represented as domain entities: Contact, Customer, Agent, Carrier, Organization (the domain entity, distinct from the Organization bootstrap entity which is a tenancy container)

**The distinction is authentication and role-based participation.** Internal Actors authenticate and participate in the system's message flow (they have queues, they claim work, they execute commands). External counterparty entities are data that internal Actors operate on.

**Where it's subtle**: a retail agent submitting work to GIC is an external entity from GIC's OS perspective. But if that same retail agent logs into a different org on the platform (their own agency's org), they become an internal Actor in their own org. The person is the same; their relationship to the OS depends on which org they're interacting with.

**For the spec**: the Actor bootstrap entity should explicitly state that it covers only authenticated participants. The domain model should explicitly note that Contact, Customer, Agent, and similar entities are not Actors — they don't authenticate, they don't have roles, they don't receive messages. They are the subjects of work, not the workers.

## Item 6: Computed Field Mapping Scope

### What was surfaced

The GIC retrace identified that when activating a computed field on an entity type (e.g., `Submission.ball_holder` derived from `stage`), the mapping configuration should be stored on the method activation, not as a separate shared Lookup.

### The clarification

**Method activation configs are for intrinsic entity behavior. Lookups are for cross-entity reference data.**

When you activate a computed field:

```bash
indemn entity add-method Submission computed-field \
  --name ball_holder \
  --from stage \
  --mapping '{"received": "queue", "triaging": "gic", "awaiting_agent_info": "agent", "awaiting_carrier_action": "carrier", "processing": "gic", "quoted": "agent", "declined": "gic", "closed": "done"}'
```

The mapping `{"received": "queue", "triaging": "gic", ...}` is stored **with the method activation config on the entity definition**, not as a Lookup entity.

**Why not a Lookup**: Lookups are for data that:
- Is referenced by rules at runtime (e.g., "prefix MGL → general_liability")
- Is shared across entity types or across multiple rules
- Is bulk-importable from CSV
- Is maintained by non-technical users
- Changes frequently and independently of entity definitions

The ball_holder mapping is none of these. It's intrinsic to the Submission entity's behavior — the mapping IS the computed field definition. It changes only when the entity's state machine changes. It's not shared with other entities. It's not maintained by non-technical users.

**Rule of thumb**: if the data defines HOW an entity behaves, it belongs on the entity definition (method activation config). If the data is referenced BY entity behavior at runtime from a shared pool, it belongs in a Lookup.

**More examples**:

| Data | Where it lives | Why |
|---|---|---|
| stage → ball_holder mapping | Method activation config | Intrinsic entity behavior |
| USLI email prefix → LOB mapping | Lookup | Shared reference data, bulk-importable |
| State list for surplus lines filing | Lookup | Reference data maintained by compliance |
| Default priority per entity type | Method activation config | Intrinsic behavior |
| Carrier name variations → canonical carrier ID | Lookup | Shared reference data, many-to-one mapping |

## Item 11: `owner_actor_id` on Associates — Formalized

### What was surfaced

The CRM retrace introduced `owner_actor_id` on associates for delegated credential access. The realtime-architecture-design artifact included it in the Associate entity definition. The authentication design formalized the two auth patterns (default assistant inherits user session, owner-bound scheduled associates use own tokens).

### The formalization

**The `owner_actor_id` field on Associate is an optional binding that establishes a delegation relationship between a human actor and an associate.**

```python
class Associate(Actor):   # Associate is a type of Actor
    owner_actor_id: Optional[ObjectId] = None   # The human this associate acts on behalf of
    # ... other associate fields (skills, mode, runtime_id, etc.)
```

**When `owner_actor_id` is set, the associate gains two specific capabilities:**

### 1. Credential resolution through the owner's Integrations

When the associate invokes an entity method that resolves an Integration, the resolver checks the owner's context in addition to the associate's own:

```
Resolution order:
1. Does the associate itself have a personal Integration of this type? → use it.
2. Does the owner (owner_actor_id) have a personal Integration of this type? → use it.
   Audit: "associate X used owner Y's integration Z."
3. Does the org have an Integration of this type that the associate's role permits? → use it.
4. No match → fail with descriptive error.
```

This enables patterns like:
- Craig's Gmail Sync associate uses Craig's personal Gmail Integration
- A personal assistant associate accesses the owner's calendar Integration
- A delegated action associate sends email from the owner's email Integration

### 2. Differentiated authentication models

From the authentication design, two patterns coexist:

| Pattern | Authentication | Lifetime | Use case |
|---|---|---|---|
| **Default assistant in UI** | Inherits user's Session JWT | Tied to user session | Base UI assistant panel |
| **Owner-bound scheduled associate** | Own service token (via Session entity of type `associate_service`) | Runs independently | Craig's Gmail sync, scheduled personal workers |

The default assistant's harness receives the user's JWT at session start. It acts AS the user. Audit: "user X via default associate."

Owner-bound scheduled associates authenticate with their own service tokens. They run independently of the owner's session. Audit: "associate Y (owner: user X) via service token."

### Consent and lifecycle

- **Consent required**: when an associate is created with `owner_actor_id`, the owner must consent. Consent is recorded in the changes collection.
- **Revocable**: the owner can remove the binding at any time via `indemn associate remove-owner ASSOC-001`. The associate loses access to the owner's personal Integrations immediately.
- **Transferable**: ownership can be transferred (with new owner's consent) via `indemn associate transfer-owner ASSOC-001 --to new-owner@indemn.ai`.
- **On owner deprovisioning**: all associates with `owner_actor_id = deprovisioned actor` are paused. Platform admin reviews and either reassigns or retires them.

### CLI surface

```bash
# Create with owner
indemn actor create --type associate --name "Craig's Gmail Sync" \
  --owner-actor craig@indemn.ai \
  --role personal_sync \
  --trigger "schedule:*/15 * * * *" \
  --skill personal-email-sync

# List owner's associates
indemn associate list --owner craig@indemn.ai

# Remove ownership
indemn associate remove-owner ASSOC-001

# Transfer
indemn associate transfer-owner ASSOC-001 --to kyle@indemn.ai
```

Auto-generated from the Associate entity definition + the `owner_actor_id` field. No special CLI beyond standard entity CRUD.

## Item 12: Content Visibility Scoping for Personal-Integration-Derived Entities

### What was surfaced

The CRM retrace identified: when an Interaction is created from a personal Integration (e.g., Craig's Gmail sync creates an Interaction from a personal email), the team should see that Craig emailed Julia at INSURICA, but the full email body should not be visible to everyone.

### The policy decision

**Default: metadata shared, full content owner-scoped. Configurable per Integration.**

When an entity is created from a personal Integration's data:

- **Metadata** (from, to, subject, timestamp, content_preview — first ~200 chars) is shared with the team. Written to the entity's standard fields in the org-scoped MongoDB collection. Anyone with read permission on the entity type sees it.
- **Full content** (email body, attachment text, detailed transcript) is stored in an owner-scoped S3 path: `s3://indemn-files/{org_id}/actor/{actor_id}/{entity_type}/{entity_id}/`. Only the owner (and platform admins with explicit access) can retrieve it.

### How it works

The Integration entity gains an optional `content_visibility` field:

```python
class Integration(Entity):
    # ... existing fields ...
    
    content_visibility: Literal["full_shared", "metadata_shared", "owner_only"] = "metadata_shared"
    # full_shared: everything in org-scoped storage, any reader sees all
    # metadata_shared: metadata in entity, full content in owner-scoped S3 (DEFAULT for actor-owned Integrations)
    # owner_only: nothing shared, all data in owner-scoped S3 (for highly private sources)
```

Default per ownership:
- **Org-owned Integrations**: `full_shared` (the company's shared Outlook inbox is visible to everyone with read access)
- **Actor-owned Integrations**: `metadata_shared` (personal Gmail, personal Slack DMs — metadata visible, full content owner-scoped)

The entity method that syncs from the Integration reads this policy and writes accordingly:

```
sync associate processes new email from Craig's Gmail:
  → reads Integration.content_visibility = "metadata_shared"
  → creates Interaction entity with: from, to, subject, content_preview, occurred_at
  → writes full body + attachments to s3://indemn-files/indemn/actor/craig/interaction/INT-091/
  → Interaction entity stores full_content_ref pointing to the S3 path
  → when another team member views the Interaction, they see metadata fields
  → when they try to access full_content_ref, S3 returns 403 (wrong actor)
  → when Craig views it, S3 returns 200 (correct actor)
```

### The three levels

| Level | What's shared | Full content location | Use case |
|---|---|---|---|
| `full_shared` | Everything | Org-scoped S3 (`s3://.../org/{org_id}/...`) | Org-owned Integrations (company Outlook, shared Slack channels) |
| `metadata_shared` | Metadata fields on entity | Owner-scoped S3 (`s3://.../org/{org_id}/actor/{actor_id}/...`) | Personal email, personal Slack DMs — DEFAULT for actor-owned |
| `owner_only` | Nothing | Owner-scoped S3 | Highly private sources (personal notes, sensitive communications) |

### S3 access control

S3 path-based access control enforced via IAM policies:
- Org-scoped paths: any actor in the org with read permissions on the entity type can read
- Actor-scoped paths: only the owning actor (or platform admin with explicit access) can read
- The entity framework's file operations (`indemn file download`) check the requester's identity against the S3 path's ownership

### Edge cases

**Team member leaves**: when an actor is deprovisioned, their owner-scoped S3 data persists (for audit/compliance) but becomes accessible only to platform admins. If the data needs to be re-homed (e.g., a sales territory transfer), platform admin runs a migration.

**Shared Interaction from two sources**: Craig's personal Gmail sync creates an Interaction. The org-level Slack bot also creates an Interaction for the same conversation (Craig messaged Julia in a shared channel). Two Interaction entities exist, from different sources, with different visibility levels. The Contact/Organization timeline shows both. No conflict — they're separate entities with different provenance.

**Override per entity**: a user can explicitly share a specific piece of content by copying it to the org-scoped path. This is an explicit action (`indemn file share INT-091 --content full_body`), audited, irreversible (once shared, it's shared). Supports "I want my team to see this specific email thread."

## What's Decided (All Five Items)

1. **Inbound webhook dispatch**: kernel-provided generic endpoint at `/webhook/{provider}/{integration_id}`, adapter interface extended with `validate_webhook` and `parse_webhook`, entity operations applied through entity methods (not raw updates), state machine enforcement preserved.
2. **Internal Actors vs external counterparty entities**: Actors authenticate and participate via roles/watches/queue. External counterparties (Customer, Agent, Carrier contacts) are domain entities without auth. The same person can be an Actor in one org and an external entity in another. Spec should state this explicitly.
3. **Computed field mapping scope**: method activation configs for intrinsic entity behavior, Lookups for shared reference data. Rule of thumb: if it defines HOW the entity behaves, it's on the entity definition; if it's referenced BY behavior from a shared pool, it's a Lookup.
4. **`owner_actor_id` formalized**: optional field on Associate enabling delegated credential access through the owner's Integrations, with consent, revocability, transferability, and lifecycle handling on owner deprovisioning. Two auth patterns: default assistant inherits user session, owner-bound scheduled associates use own service tokens.
5. **Content visibility scoping**: `content_visibility` field on Integration with three levels (full_shared, metadata_shared, owner_only). Default for actor-owned: metadata_shared. Default for org-owned: full_shared. S3 path-based access control enforces the policy. Per-entity sharing override available as explicit audited action.

## What's Deferred

- Exact S3 IAM policy structure for actor-scoped paths (infrastructure detail)
- UI rendering of content visibility indicators ("this content is owner-scoped — only Craig can see the full email")
- Bulk content migration tooling (for territory transfers on deprovisioning)
- Content search across visibility boundaries (can a search query match against owner-scoped content if you're not the owner? Answer: no for MVP, searchable metadata only)

## Relationship to Prior Artifacts

This artifact does NOT modify prior artifacts. It captures clarifications that the spec should include. Each item references its source artifact. When the spec is written, these clarifications should be integrated into the relevant sections (Integration primitive, Actor model, entity definition model, associate model, and data storage model respectively).
