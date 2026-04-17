# Notes: 2026-04-11-authentication-design.md

**File:** projects/product-vision/artifacts/2026-04-11-authentication-design.md
**Read:** 2026-04-16 (full file — 731 lines)
**Category:** design-source

## Key Claims

- Auth design closes post-trace synthesis item 10. Blocks real customer deployment until resolved.
- **Session becomes the 7th bootstrap entity** (Organization, Actor, Role, Integration, Attention, Runtime, **Session**).
- Session applies uniformly across all auth types (user_interactive / associate_service / tier3_api / cli_automation). One validation path, one revocation mechanism, one audit trail.
- Hybrid access model: short-lived JWT access tokens (15 min default, stateless verification) + long-lived opaque refresh tokens (user_interactive only, stored hashed in Secrets Manager) + long-lived tokens (validated by hash lookup) for associates/api/cli.
- Five auth method types (MVP): password (Argon2id, MongoDB), totp (seed in Secrets Manager, pyotp), sso (via Integration), token (opaque long-lived), magic_link (one-time invitation/recovery).
- WebAuthn/passkeys, SAML, SCIM, social login, OAuth app registration all deferred post-MVP.
- MFA policy: role-level `mfa_required` + actor `mfa_exempt` override + org `default_mfa_required`. Resolution: actor exempt > role required > org default.
- Fresh MFA re-verification: `@exposed(requires_fresh_mfa=N)` parameter. Small extension to @exposed decorator mechanism.
- Platform admin cross-org model: `_platform` system org + PlatformCollection accessor + 4h default session + work-type tagging (build/debug/incident/routine) + per-customer notification config + strict scope limits.
- Claims refresh on role change (not revocation): `claims_stale = true` on Session, next request auto-refreshes. Full revocation only on actor suspension/deprovisioning.
- Default assistant in UI inherits user's session; owner-bound scheduled associates use their own service tokens.
- Pre-auth rate limiting in kernel auth middleware. Sliding window keyed by (IP, email hash). Default 5 failures in 10 min → 30-min lockout.
- Revocation cache in-memory per API instance, invalidated via Change Stream on Session `status_changed[to=revoked]`, bootstrap on instance startup from last 15 minutes.
- First-org bootstrap: magic_link token via stdout for the first admin.
- Auth events in changes collection with specific types (auth.login_attempt, auth.session_created, auth.mfa_reset, auth.platform_admin_access, auth.brute_force_lockout, etc.).

## Architectural Decisions

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

## Layer/Location Specified

**All authentication mechanics are explicitly kernel-side:**

- "Kernel handles mechanics (validation, session lifecycle, token issuance, MFA challenge flow)."
- "Domain or per-org config decides policy (who needs MFA, what lockout thresholds, which roles exist)."
- Kernel auth middleware runs on every request (hot path): verify JWT signature → expiry → `jti` against revocation list → if `claims_stale` refresh claims → set auth context.
- Kernel auth API endpoints: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/challenge`, `/auth/recover` — hand-built workflows.
- Revocation cache: "in-memory per API instance, invalidated via Change Stream."
- Rate limiting: "in the kernel auth middleware, before password verification."
- JWT signing: platform-wide key, kernel code.
- `PlatformCollection` accessor: in the kernel, bypasses normal OrgScopedCollection filtering.

**Default assistant auth flow (line 463-482):**
- Default assistant is "a projection of the user into a running actor."
- "Its harness authenticates using the user's session JWT (injected at session start)."
- This aligns with 2026-04-10-realtime-architecture-design.md: the default assistant is an instance of a chat harness running the user's default associate.
- **This implies**: the default assistant's agent execution should run in a chat harness, inheriting the user's session via injected JWT. NOT inside the kernel's API server process.

**Associate service token auth flow (line 556-564, scenario 4):**
- When an associate is created, kernel auto-generates a `token` method with `usage: associate_service`.
- Token hash stored in Secrets Manager; raw token returned once.
- "Associate's harness (Temporal worker, chat runtime) reads the token at startup, authenticates, gets an `associate_service` Session."
- **This explicitly names the harness (Temporal worker for async, chat runtime for real-time) as the thing that authenticates.** Not the kernel. The harness is the client that uses the token.
- This is again the harness-pattern framing: agent execution environments are harnesses that authenticate TO the kernel via service tokens.

## Dependencies Declared

- Argon2id (password hashing — kernel dependency)
- pyotp (TOTP — kernel dependency)
- AWS Secrets Manager (for all non-hash secrets: TOTP seeds, refresh tokens, backup codes, SSO OAuth creds)
- MongoDB Change Streams (revocation cache invalidation)
- JWT library (for HS256 signing/validation)
- Identity providers via Integration (Okta, Azure AD, etc.) — uses existing Integration primitive
- Email delivery Integration (for magic links — first-org bootstrap prints to stdout)

## Code Locations Specified

- **Session bootstrap entity** — kernel-side (new bootstrap entity)
- **Actor extensions** (authentication_methods, status state machine, mfa_exempt) — kernel-side entity definition
- **Role extensions** (mfa_required, can_grant) — kernel-side entity definition
- **Organization extension** (default_mfa_required) — kernel-side entity definition
- **Auth middleware** — kernel code
- **JWT signing/validation** — kernel code
- **Revocation cache** — kernel code
- **Auth API endpoints** (login/refresh/logout/challenge/recover) — hand-built kernel code, not auto-generated
- **PlatformCollection** — kernel accessor code
- **Password hashing (Argon2id)** — kernel dependency
- **TOTP** — kernel dependency

No specific file paths are prescribed; the artifact specifies "kernel code" and "kernel dependency."

## Cross-References

- 2026-04-10-base-ui-and-auth-design.md — supersedes the auth portion
- 2026-04-10-integration-as-primitive.md — Integration primitive used for identity providers
- 2026-04-10-session-5-checkpoint.md — auth skeleton from session 5
- 2026-04-09-data-architecture-solutions.md — session 4 security decisions
- 2026-04-11-base-ui-operational-surface.md — base UI design depends on default assistant's auth model

## Open Questions or Ambiguities

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
