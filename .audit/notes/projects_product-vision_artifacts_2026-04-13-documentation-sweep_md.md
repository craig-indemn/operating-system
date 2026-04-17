# Notes: 2026-04-13-documentation-sweep.md

**File:** projects/product-vision/artifacts/2026-04-13-documentation-sweep.md
**Read:** 2026-04-16 (full file — 330 lines)
**Category:** design-source

## Key Claims

**Five clarifications — not new decisions, just explicit capture of things already emergent from prior retraces/designs:**

### Item 4 — Inbound webhook dispatch via Integration adapters

- **Endpoint**: `POST /webhook/{provider}/{integration_id}` (kernel-provided, generic — not per-provider).
- **Flow**: external POST → kernel finds Integration by ID → adapter from registry by `provider_version` → `adapter.validate_webhook` (401 on invalid) → `adapter.parse_webhook` returns `WebhookResult` → kernel applies via entity methods (not raw updates).
- **Adapter interface extended**: outbound (fetch/send/charge) + inbound (validate_webhook/parse_webhook) + auth_initiate.
- **`WebhookResult` shape**: `{entity_type, lookup_by, lookup_value, operation: transition|update|create, params}`. Kernel resolves entity via lookup then applies operation through the entity's own methods — state machine + permission + event emission all enforced normally.
- **Not all adapters need inbound** — base Adapter raises `NotImplementedError`; kernel only registers webhook endpoint for adapters with inbound.

### Item 5 — Internal Actors vs External Counterparty Entities

- **Two categories**:
  - **Internal Actors** (authenticate, have roles, process triggers, appear in actor list): humans + associates. Authenticated via Session.
  - **External counterparty entities** (no auth, no roles): Customers buying insurance (EventGuard consumers), retail agents, carrier contacts. Domain data, subject of work.
- **Subtle case**: a retail agent submitting to GIC is an external entity in GIC's org. If they log into their own agency's org, they become an internal Actor there. Same person; different relationship per org.
- **Spec requirement**: Actor bootstrap entity must explicitly cover only authenticated participants. Contact/Customer/Agent entities must be documented as not Actors.

### Item 6 — Computed field mapping scope

- **Method activation configs**: for intrinsic entity behavior (e.g., `Submission.ball_holder` mapping from `stage`). Stored with the method activation on the entity definition. NOT a Lookup.
- **Lookups**: cross-entity reference data, shared across entity types or rules, bulk-importable from CSV, maintained by non-technical users, changes frequently.
- **Rule of thumb**: if it defines HOW an entity behaves → on the entity definition. If it's referenced BY behavior from a shared pool → a Lookup.

### Item 11 — `owner_actor_id` on Associates (formalized)

- **Associate IS a type of Actor** (inherits Actor).
- **`owner_actor_id: Optional[ObjectId]`** — when set, establishes delegation between human and associate.
- **Two capabilities granted when set**:
  1. **Credential resolution chain**: associate → owner → org (with role access). `Resolution order: 1. Associate's own personal Integration → 2. Owner's personal Integration (audit: "associate X used owner Y's integration Z") → 3. Org Integration with role access → 4. Fail.`
  2. **Differentiated auth patterns**:
     - **Default assistant in UI**: inherits user's Session JWT (acts AS user). Short-lived, tied to user session.
     - **Owner-bound scheduled associate**: own service token (Session of type `associate_service`). Runs independently.
- **Consent required** at creation, recorded in changes collection.
- **Revocable** via `indemn associate remove-owner`.
- **Transferable** with new owner's consent.
- **On owner deprovisioning**: paused; platform admin reviews.

### Item 12 — Content visibility scoping

- **`Integration.content_visibility` field**: `"full_shared" | "metadata_shared" | "owner_only"`.
- **Defaults**:
  - Org-owned Integrations → `full_shared` (visible to all with read permission)
  - Actor-owned Integrations → `metadata_shared` (metadata in entity, full content in owner-scoped S3)
- **Three levels**:
  - `full_shared`: everything in org-scoped S3 (`s3://.../org/{org_id}/...`)
  - `metadata_shared`: metadata in entity fields (from, to, subject, timestamp, 200-char preview); full content in owner-scoped S3 (`s3://.../org/{org_id}/actor/{actor_id}/...`)
  - `owner_only`: nothing shared; all data owner-scoped
- **S3 path-based access control** enforced via IAM policies.
- **Edge cases**: deprovisioned actor → data persists but only accessible to platform admin; per-entity sharing override via explicit audited action (`indemn file share INT-091 --content full_body`).

## Architectural Decisions

- **Inbound webhook is an entry point, not an actor.** Kernel generic endpoint. Adapter-layer validation and parsing. Entity methods handle actual mutations.
- **Two kinds of "people" in the model**: Internal Actors (authenticated, roled, queued, CLI-empowered) and External Entities (domain data, subjects of work).
- **Method activation configs on entity definition vs. Lookups as shared data** — clean separation.
- **Owner-bound associates** get delegated credential access through owner's Integrations + two distinct auth patterns (session-inherited vs. service-token).
- **Content visibility as Integration field** (not per-entity, not per-message). Default per ownership.
- **S3 path structure encodes visibility** — paths are infrastructure, access control is IAM.
- **Explicit-share escape hatch** for per-instance "share this one email thread with the team."

## Layer/Location Specified

- **Webhook endpoint**: `kernel/api/webhook.py` (per later Phase 2-3 spec).
- **Adapter interface**: `kernel/integration/adapter.py` (abstract base class) — extended with inbound methods.
- **Adapter registry**: `kernel/integration/registry.py` — keyed by `provider:version`.
- **WebhookResult**: schema type (kernel).
- **Internal Actor / External Entity distinction**: documentation-level. Implementation means: Actor entity auto-registered for auth; Contact/Customer/Agent entities are just Entity framework.
- **Method activation config**: stored on entity definition (MongoDB `entity_definitions` collection).
- **Lookup**: kernel entity type, stored in MongoDB, queried by rules/capabilities.
- **`owner_actor_id`**: field on Associate schema.
- **Session of type `associate_service`**: introduced here; formalized in authentication-design.
- **Content visibility field**: on Integration schema.
- **S3 access control**: IAM policy on path prefix (`actor/{actor_id}/...`) — infrastructure layer.
- **`indemn file download` + `indemn file share`**: CLI commands; implementation kernel-side.

**Finding 0 relevance**:
- Default assistant inherits user's Session JWT → per design, this runs in a harness instance (chat-harness) that's launched with the user's session. Pass 2 notes: current code has assistant as kernel endpoint (`kernel/api/assistant.py`) with no tools — Finding 0b.
- Owner-bound associate pattern (e.g., Craig's Gmail Sync) — requires the async-deepagents harness (scheduled trigger). Pass 2 notes: async harness not implemented; all scheduled associates run as Temporal activities in kernel — Finding 0.
- Webhook dispatch pattern is correctly kernel-side (entry point, not actor work).

## Dependencies Declared

- Adapter registry + per-provider adapter implementations
- AWS Secrets Manager (for webhook secrets)
- S3 + IAM (for content visibility)
- MongoDB (for Integration entities, entity_definitions)
- Session entity with types `user_session`, `associate_service`, etc.

## Code Locations Specified

- `kernel/integration/adapter.py` — Adapter base class (extended interface)
- `kernel/integration/registry.py` — ADAPTER_REGISTRY by `provider:version`
- `kernel/api/webhook.py` — generic webhook endpoint
- `kernel/integration/credentials.py` — credential resolution chain
- `kernel/integration/adapters/{stripe_adapter,outlook}.py` — reference implementations
- Associate entity schema (inherits Actor) with `owner_actor_id`
- Integration entity schema with `content_visibility`

## Cross-References

- 2026-04-10-integration-as-primitive.md (Integration primitive — this sweep extends it with inbound)
- 2026-04-10-eventguard-retrace.md (surfaced items 4 and 5)
- 2026-04-10-gic-retrace-full-kernel.md (surfaced item 6)
- 2026-04-10-crm-retrace.md (surfaced items 11 and 12)
- 2026-04-10-realtime-architecture-design.md (Runtime, Associate with owner_actor_id)
- 2026-04-11-authentication-design.md (auth patterns, Session entity)
- 2026-04-10-post-trace-synthesis.md (the routing document that categorized these items)
- Phase 2-3 consolidated spec §3 (Integration Framework) implements adapter interface + registry + webhook endpoint
- Phase 4-5 consolidated spec (assistant) — Finding 0b evidence (deviates from documented auth pattern for default assistant)

## Open Questions or Ambiguities

Deferred by this artifact:
- Exact S3 IAM policy structure
- UI rendering of content visibility indicators
- Bulk content migration tooling
- Content search across visibility boundaries (answered NO for MVP — searchable metadata only)

**Supersedence note for vision map**:
- All 5 clarifications survive. They're canonical.
- The default-assistant auth pattern (inherits user Session JWT via harness) is a load-bearing statement for Finding 0b.
- Owner-bound associate pattern requires the async-deepagents harness — currently missing in implementation (Finding 0 consequence).
