# Notes: 2026-04-10-base-ui-and-auth-design.md

**File:** projects/product-vision/artifacts/2026-04-10-base-ui-and-auth-design.md
**Read:** 2026-04-16 (full file — 404 lines)
**Category:** design-source

## Key Claims

- This is an EARLIER sketch of Base UI + Auth from 2026-04-10. Both topics were later superseded by dedicated sessions:
  - UI portion superseded by 2026-04-11-base-ui-operational-surface.md
  - Auth portion superseded by 2026-04-11-authentication-design.md
  - Ephemeral entity lock concept later unified into Attention (per realtime-architecture-design)
  - Watch coalescing later simplified out of the kernel (per 2026-04-13-simplification-pass.md)
- Base UI is "a self-evident surface derived from the primitives" — 1:1 with CLI, no bespoke per-org UI, auto-generated, admin-first, built on same primitives as CLI.
- Base UI view inventory: Queue / Entity Explorer / Entity Detail / Actor Management / Associate Management / Integration Management / Rules and Lookups / Skills / Roles and Watches / Trace and Audit / System Dashboards.
- Auto-generation mechanics: field definitions → table columns + filter controls + input widgets. Field types → appropriate widgets. State machines → lifecycle diagrams + current-state badges + transition buttons. Relationships → drill-through. Activated methods → action buttons. Entity skills → help text/descriptions.
- GIC retrace addressed via UI layer mostly; two small kernel additions required: watch coalescing + ephemeral entity locks (both later simplified/unified).
- Authentication section is "a starting sketch, not a solved design. It's enough to capture where the pieces go and what needs a focused session."
- Authentication methods are a list on Actor (multiple coexist): password, sso (via Integration), mfa_totp, service_token, api_key, webauthn.
- Identity providers are Integrations (system_type: identity_provider).
- Role-grant authority as meta-permission on Role: `can_grant`. Associates have `can_grant: null`.
- Actor lifecycle states: provisioned → active → suspended → deprovisioned.
- Bootstrap flow: `indemn org create "Acme Insurance" --admin-email ...`.
- Associate service token lifecycle: generated at creation, stored hashed in Secrets Manager, returned once, rotatable.
- "Two ergonomic paths" for Role creation: Path 1 (named shared roles — human job functions) vs Path 2 (inline roles on associate creation — automation scope).

## Architectural Decisions

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

## Layer/Location Specified

- **Base UI is outside the kernel** — it's "a consumer of entity API + the same auth context." No direct database access.
- **Identity providers are Integrations** — credentials and config in Integration records, adapters in kernel.
- **Password hashes in Secrets Manager** (per this artifact; later refined in auth design to Argon2id in MongoDB with defense-in-depth).
- **Ephemeral entity locks** originally proposed as kernel-side (small collection with TTL + heartbeat protocol) — **later subsumed into Attention entity** (bootstrap entity) per realtime-architecture-design. Same location (kernel) but different mechanism name.
- **Watch coalescing** originally kernel-side (coalesce field + batch_id + emission-time grouping logic) — **later moved out of kernel** entirely per simplification pass. UI-only grouping by correlation_id.
- **Auto-generated UI** — single codebase, no per-org variants. Adding an entity = UI reflects automatically.
- Associate service tokens authenticate "to the kernel API" from associate deployments (Temporal worker, etc.). Clearly framed as associate → kernel interface.

## Dependencies Declared

- AWS Secrets Manager (credentials, token hashes)
- MongoDB Change Streams (for real-time UI updates, implied)
- Okta (example SSO provider)
- JWKS validation (for SSO ID tokens)
- Temporal workers (associate deployment)
- Current user's role context (for UI permission scoping)

## Code Locations Specified

- **Base UI** — separate codebase from kernel, consumer of entity API
- **Entity API** — kernel-side
- **Auto-generation logic** — kernel-side (reads primitives + role permissions, renders UI via API metadata)
- **Identity provider adapters** — kernel code (like any other Integration adapter)
- **Password method** — kernel-native, not via Integration

## Cross-References

- 2026-04-10-gic-retrace-full-kernel.md (surfaced the six concerns this addresses)
- 2026-04-10-integration-as-primitive.md (Integration primitive enables SSO)
- 2026-03-30-design-layer-1-entity-framework.md (original thin auth sketch)
- 2026-04-10-realtime-architecture-design.md (SUPERSEDES the ephemeral entity lock proposal here, unifies with Attention)
- 2026-04-11-authentication-design.md (SUPERSEDES the auth portion of this artifact)
- 2026-04-11-base-ui-operational-surface.md (SUPERSEDES the base UI portion of this artifact)
- 2026-04-13-simplification-pass.md (REMOVES watch coalescing from the kernel)

## Open Questions or Ambiguities

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
