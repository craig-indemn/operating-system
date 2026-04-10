---
ask: "What does the auto-generated base UI look like, how does it address the concerns from the GIC retrace, and how does authentication fit into the architecture?"
created: 2026-04-10
workstream: product-vision
session: 2026-04-10-a
sources:
  - type: conversation
    description: "Craig and Claude working through UI philosophy, usability concerns, auth design, and the associate-role asymmetry"
  - type: artifact
    description: "2026-04-10-gic-retrace-full-kernel.md (surfaced the concerns this artifact addresses)"
  - type: artifact
    description: "2026-04-10-integration-as-primitive.md (Integration primitive enables identity providers as Integrations)"
  - type: artifact
    description: "2026-03-30-design-layer-1-entity-framework.md (the original thin auth sketch)"
---

# Base UI and Authentication Design

## Framing

The GIC retrace surfaced six concerns (bulk event coalescing, pipeline overview, soft-lock during review, multi-LOB drafts, queue health tooling, computed field mapping scope). None are architectural breaks — they're usability requirements. Most get addressed by the UI layer the OS ships with. The rest are small kernel additions.

Separately, authentication was sketched in the original Layer 1 design but never fleshed out. Session 4 didn't touch it. It's a real gap, and it needs its own focused design. This artifact captures the current best thinking as a starting point for that focused session.

## Part 1: The Base UI

### Philosophy

The base UI is to the CLI what the auto-generated API is to the entity framework: **a self-evident surface derived from the primitives**. The CLI is the canonical interface — the base UI is a graphical presentation of the same operations, scoped by the current user's role, rendered from entity definitions and watches.

Constraints:
- **1:1 mapping with the CLI**. Anything a role can do via CLI, they can do in the UI. Nothing in the UI requires CLI fallback, and nothing in the CLI is hidden from the UI for users with the right permissions.
- **No bespoke per-org UI**. The base UI is the same for every organization. What differs is the rendered content based on entity definitions, activated methods, role permissions, and watches.
- **Auto-generated, not hand-built**. The UI reads the primitives and renders accordingly. Adding a new entity type doesn't require UI work — it shows up in the entity browser automatically, with its fields, state machine, and activated methods.
- **Admin-first**. The base UI is primarily a platform administration and operator interface. Customer-facing UIs (policyholder portals, agent workbenches) are built on top of the same primitives but are separate products — the base UI is what the Indemn team and FDEs use to run the platform.
- **Built on the same primitives the CLI uses**. The UI is just a consumer of entity API + the same auth context. There is no separate UI data model, no separate UI state layer beyond standard front-end caching.

### Components

The base UI is organized as a set of views, each a window into specific primitives:

| View | Sources From | Purpose |
|------|-------------|---------|
| **Queue** | `message_queue` filtered by the current user's roles | "What needs my attention right now?" Shows pending work items with entity context and available actions. |
| **Entity Explorer** | Entity definitions + role read permissions | Browse, filter, and sort any entity type the role has read access to. Auto-rendered tables, filter controls derived from field types. |
| **Entity Detail** | One entity + its state machine + its methods + related entities + recent changes from `changes` | View one entity in depth. Methods appear as action buttons. State machine rendered as a lifecycle diagram showing current position and available transitions. Related entities linked. Recent field-level changes displayed with actor attribution. |
| **Actor Management** | Actor entities + role assignments + authentication methods | List actors, assign/revoke roles, invite new actors, see who's doing what. Shows both human actors and associate actors. Role-grant authority enforced per the current user's permissions. |
| **Associate Management** | Associate actors + their claim history from `message_log` + their Temporal execution history + their current queue depth | For each associate: status, role/watches, current skill(s), recent runs, failure rate, LLM token usage. Buttons to start/stop, update skill, edit config, retry failed work items, inspect individual execution traces. |
| **Integration Management** | Integration entities + Secrets Manager status + adapter health | Per integration: provider, version, owner (org/actor), status, last health check, access roles. Buttons to configure, test connection, rotate credentials, upgrade provider version, pause. |
| **Rules and Lookups** | Rule and Lookup records per entity type | Browse rules by entity type. Edit, disable, test against sample data. Bulk import/export lookups from/to CSV. Rule evaluation traces available via trace view. |
| **Skills** | Skill records in MongoDB + version history from `changes` | View current skill content. Upload new version (enters pending_review). Approve/reject pending versions. See rollback history. |
| **Roles and Watches** | Named Role entities (shared human roles) | Create/edit shared roles. See watch definitions. See which actors hold each role. Can-grant authority surfaced. |
| **Trace and Audit** | `changes` + `message_log` + OTEL traces via `correlation_id` | Query entity history, trace cascade flows, generate compliance audit reports. Drill from a single entity event through the full execution tree. |
| **System Dashboards** | Aggregations over entities + `message_log` + Integration status + Temporal worker metrics | Metrics, throughput, state distributions, pipeline health, queue depths, integration health, error rates. |

Every view is a projection of the underlying primitives through the lens of the current user's role. A view that doesn't apply to a role (e.g., Rule management for a user without admin permissions) doesn't appear in the navigation. The UI respects the permission model enforced at the entity layer.

### Auto-generation mechanics

**Entity views are generated from**:
- Field definitions → table columns, filter controls, detail view field rendering
- Field types → appropriate input widgets (date picker, enum dropdown, reference picker, etc.)
- State machine → lifecycle diagram + current-state badge + transition buttons
- Relationships → drill-through links to related entities
- Activated methods → action buttons with per-method forms derived from method parameters
- Entity skills → help text, field descriptions, operation documentation
- Computed fields → read-only badges/labels

**Queue views are generated from**:
- Role watches → what messages appear
- Message entity context → how each row is summarized
- Available actions → derived from methods the role can invoke on the context entity
- Priority and age → sorting and visual emphasis

**Dashboards are generated from**:
- Entity definitions with state machines → state distribution charts per entity type
- Message log → throughput metrics, average time in each state, actor productivity
- Integration records → health grid per integration
- Temporal worker metrics → execution success rates, failure reasons, queue depths

No view is hand-coded per entity. Adding a new domain entity (via `indemn entity create`) makes it appear in the Entity Explorer automatically. Activating a method on an entity makes the button appear in Entity Detail. Creating a new role with watches makes the corresponding queue view available to actors in that role.

### How the UI addresses the GIC retrace concerns

**1. Bulk event coalescing for human queues.** When the stale checker flags 50 submissions in one transaction, the kernel emits 50 events. The operations role's queue view should render these as a single batched item, not 50 rows.

**Kernel addition**: watches declare an optional coalescing strategy.

```bash
indemn role add-watch operations \
  --entity Submission \
  --event fields_changed \
  --when '{"field": "is_stale", "op": "equals", "value": true}' \
  --coalesce '{"strategy": "by_correlation_id", "window": "5m", "summary_template": "{{count}} submissions flagged stale", "priority": "inherit"}'
```

When the kernel processes the batch of events (all sharing the same correlation_id from the stale_check execution), it writes the message_queue rows with a shared `batch_id` and the summary. The UI queries the queue and groups by `batch_id`, rendering the batch as one row with drill-down to the individual items.

Claiming happens per-item when the user takes action on a specific submission. Claiming the batch-level row is not supported — it's a rendering convenience, not a new kind of work unit.

**2. Pipeline dashboard (not a queue).** The pipeline view answers "how many submissions are in each stage, how fast are we processing, where are the bottlenecks." This is auto-generated from the entity's state machine and the message log:

- State distribution pie/sankey per entity type (reads entity state counts)
- Throughput metrics (reads `message_log` for completion timestamps per state)
- Bottleneck detection (compares time in each state against baselines)
- Queue depth per role (reads `message_queue`)
- Integration health (reads Integration status)

No new kernel primitive. Just rendering on top of what exists.

**3. Soft-lock during human review.** When a user opens an entity for interactive review, the UI places an ephemeral lock. Other users see "JC is reviewing this" and can choose to proceed with caution.

**Kernel addition**: an ephemeral entity lock mechanism.

```bash
indemn entity lock ENTITY-ID --as me --duration 5m --purpose review
indemn entity unlock ENTITY-ID
indemn entity lock-status ENTITY-ID
```

Locks are stored in a small `entity_locks` collection (or as fields on the entity) with TTL expiration. The UI heartbeats to keep the lock alive during active viewing. On navigation away or inactivity, the lock expires. Another UI opening the same entity queries `lock-status` and surfaces the result.

Locks are informational, not blocking — they warn users but don't prevent claims on the underlying messages. This preserves the "humans can override the associate" property in edge cases.

**4. Multi-LOB draft consolidation.** This stays a domain concern. The draft_writer skill handles coalescing drafts from the same source by querying for related drafts with the same source_email_id. No kernel or UI involvement needed.

**5. Queue and integration health tooling.** First-class in the System Dashboards view and as CLI commands:

- `indemn queue show --role underwriter`
- `indemn queue stats`
- `indemn associate health`
- `indemn integration health`
- `indemn trace cascade CORRELATION-ID`
- `indemn metrics throughput --entity Email --period 1d`

All are reads over existing stores. The UI renders them as a live dashboard; the CLI is the canonical interface.

**6. Computed field mapping scope.** Documentation clarification, not a UI concern. The mapping config for a computed field belongs on the method activation, not as a shared Lookup.

### The two kernel additions this requires

Only two, and both are additive:

1. **Watch coalescing.** Watches gain an optional `coalesce` config. When present, the kernel writes message_queue rows for the resulting messages with a shared `batch_id`. The UI renders batches as single rows.

2. **Ephemeral entity locks.** A lightweight lock mechanism (CLI + collection + TTL expiration + UI heartbeat protocol) for surfacing "someone is actively viewing/reviewing this entity."

Everything else in the base UI is a rendering layer over primitives that already exist.

## Part 2: Authentication

### The gap

Authentication was thinly sketched in the original Layer 1 design: JWT for humans, service tokens for associates, API keys for Tier 3. Nothing about how users actually log in, how SSO works, how MFA fits, how user lifecycle works, how role-grant authority works, how the bootstrap admin for a new org gets their credentials. Session 4 didn't touch auth.

This section is a starting sketch, not a solved design. It's enough to capture where the pieces go and what needs a focused session.

### What needs to exist

1. **Actor authentication methods** — how a given actor establishes identity
2. **Identity provider integration** — SSO support for enterprise customers
3. **Session management** — token issuance, expiration, refresh, revocation
4. **MFA** — optional per method or required per role
5. **User lifecycle states** — provisioned, active, suspended, deprovisioned
6. **Role-grant authority** — who can assign which roles to which actors
7. **Bootstrap flow** — how a new organization gets its first admin
8. **Associate service token lifecycle** — generation, rotation, revocation, audit
9. **Tier 3 API key management** — self-service signup, key rotation, scoping
10. **Audit of authentication events** — successful logins, failed attempts, token issuance, credential rotation

### Proposal: Authentication methods as a list on Actor

An Actor carries one or more authentication methods. Each method describes how the actor establishes identity. Multiple methods can coexist.

```python
class Actor(Entity):
    name: str
    email: str
    org_id: ObjectId
    type: Literal["human", "associate", "tier3_developer"]
    status: Literal["provisioned", "active", "suspended", "deprovisioned"]
    
    # Roles held by this actor (union of named shared roles + any inline role from associate creation)
    roles: list[str]
    
    # Inline role reference for associates (the role created alongside this actor)
    inline_role_id: Optional[ObjectId]
    
    # Authentication methods — multiple can coexist
    authentication_methods: list[dict]
    # Examples:
    # {"type": "password", "hash_ref": "secrets://indemn/prod/actor/{id}/password"}
    # {"type": "sso", "integration_id": "INT-OKTA-001", "external_id": "okta-user-123"}
    # {"type": "mfa_totp", "secret_ref": "secrets://..."}
    # {"type": "service_token", "token_hash_ref": "secrets://..."}
    # {"type": "api_key", "key_hash_ref": "secrets://..."}
    # {"type": "webauthn", "credential_refs": ["secrets://..."]}
```

No credentials are ever stored inline. Everything references AWS Secrets Manager. The kernel's authentication code reads the secrets at validation time.

Multiple methods per actor enables:
- Password + SSO coexistence (SSO primary, password fallback for emergencies)
- MFA as a secondary required method (login requires password + MFA TOTP)
- API keys alongside interactive login for developers
- Graceful migration when adding new methods to existing actors

### Proposal: Identity providers are Integrations

When the org wants SSO, they create an Integration with `system_type: identity_provider`:

```bash
indemn integration create \
  --owner org \
  --name "GIC Okta" \
  --system-type identity_provider \
  --provider okta \
  --provider-version okta_oidc_v1 \
  --access-roles "*"  # any actor can use the IdP to log in

indemn integration configure INT-OKTA-001 --config @okta-oidc-config.json
indemn integration transition INT-OKTA-001 --to active
```

Login flow:
1. User visits login page → sees "Sign in with Okta" button because the org has an active identity_provider Integration
2. Clicks button → OS redirects to Okta (via the Integration's adapter's auth_initiate method)
3. User authenticates at Okta → returns with an ID token
4. OS's identity adapter validates the token against Okta's JWKS
5. Extracts verified email from the token
6. Looks up Actor by email within the org
7. Verifies the actor has an `sso` method referencing this Integration
8. Issues an OS session JWT with the actor's role set
9. User is logged in

**Password-based auth is a kernel-native method** (not via Integration). Stored as a hash per-actor in Secrets Manager. Orgs can disable it once SSO is established, or keep it as an admin fallback.

**SSO + password coexistence** (confirmed requirement): an org can have both an active identity_provider Integration and password auth enabled simultaneously. Users can log in via either. Each actor's authentication_methods list determines which methods work for that specific actor. Admin emergency access is typically password-based even when the org's standard flow is SSO.

### Proposal: Role-grant authority

Role-grant is a meta-permission on Role. It defines which other roles this role's holders can grant to other actors.

```bash
indemn role create admin \
  --permissions "read:all,write:all" \
  --can-grant '["admin", "underwriter", "operations", "team_lead", "csr"]'

indemn role create team_lead \
  --permissions "read:all,write:Submission,write:Assessment" \
  --can-grant '["csr"]'

indemn role create underwriter \
  --permissions "read:all,write:Submission,write:Draft,write:Assessment"
  # No --can-grant; underwriters cannot grant roles
```

Granting a role is a method on Actor (`indemn actor add-role jc --role csr`). The method validates that the caller has a role whose `can_grant` includes the target role. Failures are logged to the changes collection.

**Associates never need can-grant**, because they never hire. The inline roles created for associates during `indemn actor create --type associate` have `can_grant: null`. This is why role-grant complexity only applies to named shared roles (Path 1 roles).

### Proposal: Actor lifecycle states

```
provisioned → active → suspended → deprovisioned
                ↑        ↓
                └────────┘  (reactivation)
```

- **provisioned**: actor record exists, but the actor hasn't completed first login. Has no active sessions. Typically created by an admin via invitation; becomes active when the user completes the invitation flow (clicks a one-time link, sets a password or logs in via SSO).
- **active**: normal operating state.
- **suspended**: temporarily disabled. Existing sessions are revoked. Authentication methods are rejected. Can be reactivated by an admin.
- **deprovisioned**: permanently disabled. Not deleted from the database (historical data integrity) but cannot authenticate, cannot be reactivated without a new actor record. Integration and message history referencing this actor is preserved.

Transitions require appropriate permissions (admin can move any actor through any state; self can't suspend self).

### Proposal: Bootstrap flow for a new org

When a new organization is created on the platform:

```bash
indemn org create "Acme Insurance" --admin-email admin@acme.com
# Creates Organization entity
# Creates the first admin Actor in "provisioned" state
# Sends an invitation email with a one-time token
# Admin clicks link, completes setup (sets password, configures SSO if desired, enables MFA if required)
# Actor transitions to "active"
# Admin can now provision additional actors, configure Integrations, create roles, etc.
```

This is platform-level bootstrap. For a new org, the platform admin (Indemn internal) initiates. For Tier 3 self-service signup, the signup form creates both the Org and the first admin Actor in one flow.

### Proposal: Associate service token lifecycle

Associates authenticate to the kernel API using service tokens. When an associate is created:

```bash
indemn actor create --type associate --name "Email Classifier" \
  --permissions "read:Email,write:Email" \
  --watches '...' \
  --skill email-classification
# Generates a service token
# Stores the token hash in Secrets Manager at /indemn/prod/actor/{id}/service_token
# Returns the token ONCE to the creator (for initial configuration)
# Subsequent calls cannot retrieve the raw token — only rotation
```

Rotation:
```bash
indemn actor rotate-credentials ACTOR-001
# Generates new service token, updates Secrets Manager, returns new token once
# Old token remains valid for a grace period (5 minutes) to allow redeployment
# After grace period, old token is revoked
```

The associate's deployment (e.g., its Temporal worker) reads the service token at startup via its own access to Secrets Manager. The token is injected as an environment variable or config file. Rotation requires redeployment or dynamic reload depending on how the worker is packaged.

## Part 3: On Associates and Roles — Clarification

The GIC retrace and previous discussions gave each associate its own named role (`classifier`, `linker`, `assessor`). This is awkward because those roles are singletons — no human would ever hold them, and they're not organizational job functions. The role-grant meta-permission also doesn't fit naturally when the role is automation scope, not a hireable position.

### Resolution

**Role stays as one primitive. Two ergonomic paths for creation.**

### Path 1: Named shared roles (organizational job functions)

For roles held by humans, potentially shared with associates that do the same work as the humans.

```bash
indemn role create underwriter \
  --permissions "read:all,write:Submission,write:Draft,write:Assessment" \
  --watches '[{"entity": "Assessment", "event": "created", "when": {"field": "needs_review", "op": "equals", "value": true}}, ...]' \
  --can-grant '["underwriter_trainee"]'

indemn actor add-role jc@gicunderwriters.com --role underwriter
indemn actor add-role sarah@gicunderwriters.com --role underwriter
```

Used for: underwriter, operations, admin, csr, team_lead, processor, and any job title humans hold. Created explicitly, reusable, named, potentially grantable.

### Path 2: Inline roles on associate creation (automation scope)

For roles specific to an associate's scope and not meant to be shared with humans. No separate `indemn role create` step.

```bash
indemn actor create --type associate --name "Email Classifier" \
  --permissions "read:Email,write:Email" \
  --watches '[{"entity": "Email", "event": "created", "when": {"field": "has_attachments", "op": "equals", "value": false}}, {"entity": "Extraction", "event": "created"}]' \
  --skill email-classification \
  --mode hybrid
```

Under the hood, this creates a Role entity for the associate. It's marked as `inline: true` and `bound_actor_id: <the associate's id>`. It has `can_grant: null` because there's nothing to grant. It's not shown in the role list as a separate named concept; it's part of the associate's definition.

### When associates share a role (parallel scaling)

If you want to run 5 classifier associates in parallel for load, use Path 1: create an explicit named role, assign all 5 associates to it.

```bash
indemn role create parallel_classifier \
  --permissions "read:Email,write:Email" \
  --watches '...'

indemn actor create --type associate --name "Classifier 1" --role parallel_classifier --skill ...
indemn actor create --type associate --name "Classifier 2" --role parallel_classifier --skill ...
# etc.
```

All five claim from the same queue. First to claim wins. Load balances naturally.

### What this gives us

- **One primitive (Role)** with two creation ergonomics
- **Human organizational roles** are named, shared, potentially grantable in a hierarchy
- **Associate-specific roles** are inline, singleton, not grantable
- **Role-grant complexity only applies to Path 1** — the hierarchical grant authority story is entirely about humans and named roles
- **Associates are still employees** — the kernel sees Role + watches + permissions uniformly regardless of path
- **The UI reflects this**: the "Roles" view shows Path 1 (named, reusable). The "Associates" view shows individual associates with their inline permissions and watches visible. Two views of the same underlying data, organized by how users think about them

## Summary of Additions From This Artifact

### Small kernel additions
- **Watch coalescing**: optional `coalesce` config on watches; `batch_id` on messages; grouping logic in queue query/rendering
- **Ephemeral entity locks**: lock/unlock/lock-status CLI; small collection or entity fields; TTL expiration; heartbeat protocol

### New framings (not new primitives)
- **Base UI is auto-generated** from the primitives, 1:1 with CLI, role-scoped, admin-first
- **Identity providers are Integrations** (reuses primitive #6 for SSO)
- **Authentication methods are a list on Actor**, supporting multiple methods per actor, credentials in Secrets Manager only
- **Role has two creation paths** — named shared (for humans/organizational job functions) and inline (for associate-specific scope). Same primitive, different ergonomics.
- **Role-grant authority** is a meta-permission on named shared roles; not used for inline associate roles

### Still needed
- **Focused authentication design session** to work out lifecycle flows, MFA policy, bootstrap details, session management specifics, and the exact credential storage model
- **Design of the base UI rendering contract** — what exact data structure the UI consumes to auto-generate each view
- **Design of the ephemeral lock protocol** — lock duration defaults, heartbeat frequency, conflict resolution strategies

## What's Open From This Artifact

- **MFA policy placement**: should MFA requirements live on the Role, the Actor, or the authentication method? Currently thinking Role ("underwriters must have MFA enabled") with Actor override ("this specific actor is MFA-exempt" only for accessibility or emergency cases).
- **Tier 3 bootstrap for self-service signup**: the full flow for a developer who visits the website, signs up, gets an org provisioned, gets admin role, and can start building. Has commercial implications (billing, usage metering) beyond pure auth.
- **Delegated admin across orgs**: for the Indemn team running the platform, there's a concept of "platform admin" who can operate across all orgs. This is outside the normal org-scoped model. Needs its own permission scope — `PlatformCollection` was mentioned in the data architecture review as a separate accessor for cross-org queries.
- **Adapter for each identity provider**: Okta, Azure AD, Google Workspace, Auth0, generic OIDC, generic SAML. Need to list and prioritize which adapters ship with the base platform.
