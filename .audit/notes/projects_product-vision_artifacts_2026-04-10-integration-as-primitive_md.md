# Notes: 2026-04-10-integration-as-primitive.md

**File:** projects/product-vision/artifacts/2026-04-10-integration-as-primitive.md
**Read:** 2026-04-16 (full file — 270 lines)
**Category:** design-source

## Key Claims

- Integration is elevated to a **bootstrap kernel primitive**, alongside Organization, Actor, and Role. Not just a domain entity.
- Six bootstrap primitives the kernel knows about specially: Entity, Message, Actor, Role, Organization, Integration.
- **Integration is the abstraction. Adapter is the implementation.** These are two halves of one system at different levels.
- Integration entity holds: provider, owner (org or actor), secret_ref, config, status, access control (roles for org-level).
- Credentials never live in MongoDB — they live in AWS Secrets Manager, referenced by `secret_ref`.
- Actor-level integrations take precedence over org-level in credential resolution.
- Adapter versioning: `provider_version` field + registry keyed by version enables per-org adapter upgrades.
- One Outlook Integration serves Email, Calendar, Contacts, potentially Tasks. One Stripe Integration serves Payment, Invoice, Subscription.
- Integration has its own lifecycle: `configured → connected → active → error → reconfigured`.
- Watches can fire on Integration status changes (`Integration:status_changed[status=error]`) to route problems to ops role.
- Integration has both org-level and actor-level ownership via `owner` field.

## Architectural Decisions

- **Adapters remain the same**: Python classes in the OS codebase, organized in an adapter registry, implementing per-provider operations. The design explicitly says "The adapter pattern remains exactly as designed".
- Adapter registry keyed by version: `ADAPTER_REGISTRY["outlook_v2"] = OutlookV2Adapter`.
- Credential resolution order: actor personal → org-level with role-based access → fail.
- Operations that MUST be org-level regardless (carrier payment, regulatory filing) can declare "org-only" and the resolver skips the actor step.
- AWS Secrets Manager is the credential store with pathed secret refs: `/indemn/{env}/org/{org_id}/integration/{id}` and `/indemn/{env}/actor/{actor_id}/integration/{id}`.
- Credential rotation is first-class CLI: `indemn integration rotate-credentials`. Records in changes collection. For OAuth providers requiring user interaction, rotation creates Draft-like work item in owner's queue.
- Every credential access is logged via changes collection + OTEL traces.
- No code path reads credentials from MongoDB. No API response or CLI output contains credentials.
- Integration health: Integration has its own status field; watches on status changes surface problems to ops roles.

## Layer/Location Specified

- **Adapters = kernel code**. Layer table (line 68-72):
  - **Integration** (primitive) — "The record: provider, owner, credentials, status" — lives in MongoDB as a bootstrap entity, managed via CLI.
  - **Adapter** (implementation) — "The kernel code that executes provider-specific operations" — Python in the OS codebase (platform code). Examples: `OutlookEmailAdapter.fetch()`, `StripePaymentAdapter.charge()`.
- **Adapters live in the kernel**. Line 71 explicitly: "Python in the OS codebase (platform code)".
- **Adapter registry is kernel code**. "Python classes in the OS codebase, organized in an adapter registry."
- **Adapter dispatch flow** (line 76-84): When `indemn email fetch-new` is called →
  - kernel looks up Integration for this org (and/or actor)
  - reads Integration.provider → "outlook"
  - finds adapter in `ADAPTER_REGISTRY["outlook"]` → OutlookEmailAdapter
  - reads Integration.secret_ref → fetches credentials from AWS Secrets Manager
  - instantiates adapter with credentials
  - invokes adapter.fetch() → returns Email entity data
  - entity framework creates Email entities, kernel takes over
- **The entire adapter dispatch happens kernel-side.** No mention of adapters running in a harness or external process. The kernel knows the provider mapping, the kernel fetches credentials, the kernel invokes the adapter.
- **Integration credential resolution is in the kernel** — it's the same code path for any external operation.
- **Webhook dispatch**: not explicitly stated here but implied by the Integration primitive housing inbound connectivity too (deferred to "Inbound webhook dispatch documentation" in 2026-04-10-realtime-architecture-design.md's Part 10 open items).

## Dependencies Declared

- AWS Secrets Manager — for credential storage, referenced by `secret_ref`
- OAuth providers — for rotation flows requiring user consent
- OTEL tracing — for per-access credential audit

## Code Locations Specified

- **Adapters**: Python in the OS codebase (platform code)
- **Adapter registry**: in the OS codebase, keyed by `provider_version`
- **No specific directory prescribed** beyond "in the OS codebase"

## Cross-References

- 2026-04-02-design-layer-4-integrations.md (original Integration + adapter pattern)
- 2026-04-08-actor-spectrum-and-primitives.md (entity polymorphism for integrations)
- 2026-04-08-primitives-resolved.md (Layer 4 collapses into Layer 1)
- 2026-04-09-data-architecture-solutions.md (Integration entity stores secret_ref)
- 2026-04-09-capabilities-model-review-findings.md (adapter versioning for external API changes)
- 2026-04-10-realtime-architecture-design.md (Integration primitive reused for voice_client provider — humans taking over voice calls)

## Open Questions or Ambiguities

From the artifact itself (Open Questions section):
- **Adapter contribution path for Tier 3**: when a Tier 3 developer needs to connect to a provider the OS doesn't support yet, what's the path? Contributing a new adapter to the kernel (platform PR) is the obvious answer. Whether there's a **managed-extension mechanism (custom adapter loaded at runtime)** is an open design question. Deferred until real Tier 3 use case.
  - **This is the Pass 2 question for integration adapters**: Are adapters in the kernel image (correct per this artifact) or should they be plugin-loadable? The artifact explicitly leaves this open. Current implementation has adapters in the kernel (per Finding-0 audit). This aligns with the design's default; the open question is only about future Tier 3 extension.
- **Consent flows for OAuth providers**: how the `indemn integration configure` CLI launches and captures browser consent in headless context. Likely a short-lived web endpoint. Unresolved.
- **Integration dependencies**: does a domain entity declare which Integrations it depends on, or does it discover them at runtime? Runtime discovery via `system_type` lookup is the MVP; explicit dependencies could be added later.

No architectural-layer deviation likely here — the design is consistent: Integration record in DB, adapters in kernel code. Both align with what Pass 2 audit should expect to find implemented.
