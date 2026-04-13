---
ask: "How does authentication work end-to-end in the kernel — session management, auth methods, MFA policy, platform admin cross-org access, recovery flows, and audit?"
created: 2026-04-11
workstream: product-vision
session: 2026-04-11-b
sources:
  - type: conversation
    description: "Craig and Claude designing authentication end-to-end — the largest remaining architectural gap from the post-trace synthesis (item 10)"
  - type: artifact
    description: "2026-04-10-base-ui-and-auth-design.md (the original auth sketch — this artifact supersedes its auth section)"
  - type: artifact
    description: "2026-04-10-integration-as-primitive.md (Integration primitive used for identity providers)"
  - type: artifact
    description: "2026-04-10-session-5-checkpoint.md (captured the auth skeleton: methods on Actor, IdP as Integration, Actor lifecycle states, role-grant)"
  - type: artifact
    description: "2026-04-09-data-architecture-solutions.md (Session 4 security decisions: OrgScopedCollection, AWS Secrets Manager, tamper-evident audit)"
  - type: artifact
    description: "2026-04-11-base-ui-operational-surface.md (base UI design that depends on the default assistant's auth model)"
---

# Authentication Design

## Context

Item 10 from the post-trace synthesis. The architectural skeleton existed from session 5 (authentication methods as a list on Actor, identity providers as Integrations, role-grant authority, actor lifecycle states) but had never been designed end-to-end. This is the dedicated design session that closes the gap.

Authentication is the largest remaining architectural gap because it blocks real customer deployment. The OS cannot accept external users until login flows, permission enforcement, and audit are nailed down end-to-end.

## Principles at Stake

Same principles we've held throughout:

- **Compose over new primitives.** Use existing primitives (Actor, Role, Integration) and extend them where possible. New bootstrap entities only when forced.
- **Everything is data.** Auth config, sessions, identity providers — queryable, auditable, stored as entities where possible.
- **Kernel vs domain.** Kernel handles mechanics (validation, session lifecycle, token issuance, MFA challenge flow). Domain or per-org config decides policy (who needs MFA, what lockout thresholds, which roles exist).
- **Credentials never inline in MongoDB.** Always Secrets Manager. Already decided in session 4.
- **CLI and API parity.** `indemn login` and the UI login flow use the same underlying mechanisms. Same permissions enforced.
- **Audit everything.** Every auth event flows through the same change-tracking machinery as everything else.
- **OrgScopedCollection is our data isolation primitive.** Auth enforces who can access; OrgScopedCollection enforces what they can see.
- **Low complexity, high reliability.** Every addition has to earn its place. Pressure test for edge cases. Scope is tight.

## Forcing Functions (Scenarios the Design Must Cover)

Ten scenarios this design has to cover cleanly. If the design handles these, it's enough for MVP.

1. **A new Indemn team member joins.** Craig invites them, they set a password + MFA, they can log in and operate.
2. **An enterprise customer (GIC) enables SSO.** They configure Okta, their users log in via SSO without passwords. Admin password fallback still works.
3. **A Tier 3 developer signs up self-service.** Visits indemn.ai, creates an account, org provisioned, gets API credentials, starts building.
4. **An associate needs a service token.** Created when the associate is provisioned, rotatable, scoped to its permissions.
5. **Kyle needs emergency admin access when SSO is broken.** Password fallback works even when standard flow is SSO.
6. **An attacker tries to brute-force a password.** Rate limiting, lockout, audit trail.
7. **A user's laptop is stolen.** Revoke all sessions for that user without touching their password.
8. **A user changes roles mid-session.** Existing sessions reflect new permissions on next request, without full re-login.
9. **Platform admin needs to build inside a customer org.** Routine operational work, not incident response. Time-limited, audited, customer-visible, but optimized for "Indemn staff building customer workflows" as a daily pattern.
10. **A user's MFA device is lost.** Recovery flow that doesn't introduce a back door.

Deferred beyond MVP: OAuth app registration, SAML specifically (OIDC is simpler), SCIM provisioning, social login, delegated consent UI.

## What Was Already Decided (Session 5)

From the base-ui-and-auth-design artifact and session 5 checkpoint:

- **Authentication methods are a list on Actor.** Multiple methods per actor. Credentials referenced via `secret_ref` to Secrets Manager.
- **Identity providers are Integrations** (`system_type: identity_provider`). SSO login flow: IdP auth via adapter → validated token → actor lookup → OS session issued.
- **SSO and password can coexist per org.** Admin emergency access via password even when standard flow is SSO.
- **Role-grant authority is a meta-permission** (`can_grant` on Role).
- **Actor lifecycle states**: provisioned → active → suspended → deprovisioned.
- **Credentials never stored inline in MongoDB.**
- **Role creation has two ergonomic paths** — named shared roles (humans) and inline roles (associates). Inline roles have `can_grant: null`.

The skeleton was solid. What was missing was the detailed design of how it actually works end-to-end — sessions, revocation, MFA policy, platform admin cross-org, recovery, audit.

## Architectural Shape

Auth in the OS is built from:

1. **Extensions to Actor** (authentication_methods, status state machine, mfa_exempt)
2. **Session** (one new bootstrap entity — the only new primitive)
3. **Identity provider Integrations** (existing primitive, specific use case)
4. **Auth events as first-class audit** (reuse changes collection with specific event types)
5. **Kernel-native auth methods** (password, TOTP — not Integrations)
6. **Kernel-provided login/session API endpoints** (hand-built workflows, not auto-generated CRUD)

## The Session Bootstrap Entity

### Why Session earns bootstrap status

The kernel cannot process any authenticated request without validating the session. It is on the hot path for every API call. Revocation requires persistent state — stateless JWTs alone cannot revoke cleanly. Session listing ("my devices") and forced logout require queryable state. Audit ("who was logged in from where when the incident happened") requires persistent records.

Bootstrap entity count moves **from 6 to 7**: Organization, Actor, Role, Integration, Attention, Runtime, **Session**.

### Session applies to all auth types, unified

Every authenticated identity — human, associate, Tier 3 developer — has a Session entity. One validation path, one revocation mechanism, one audit trail, one management surface.

```python
class Session(Entity):  # bootstrap entity
    actor_id: ObjectId
    org_id: ObjectId                       # scope — every session scoped to one org

    type: Literal[
        "user_interactive",                # Human user with short access + long refresh
        "associate_service",               # Associate authenticating as itself with long-lived token
        "tier3_api",                       # Tier 3 developer machine-to-machine
        "cli_automation",                  # Headless scripts using long-lived tokens
    ]

    created_at: datetime
    last_active_at: datetime
    expires_at: datetime                   # Session-level expiration

    auth_method_used: str                  # "password+totp", "sso:okta", "api_key", "service_token"
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_fingerprint: Optional[str]

    status: Literal["active", "expired", "revoked"]

    refresh_token_ref: Optional[str]       # Secrets Manager path (user_interactive only)
    access_token_jti: str                  # Current JWT ID for revocation list matching

    mfa_verified: bool                     # Did MFA complete during this session?
    mfa_verified_at: Optional[datetime]    # For fresh-MFA checks

    claims_stale: bool = False             # Force claims refresh on next request

    platform_admin_context: Optional[dict] # Present on platform admin cross-org sessions

    class Settings:
        name = "sessions"
        indexes = [
            [("actor_id", 1), ("status", 1)],
            [("access_token_jti", 1)],
            [("expires_at", 1)],           # TTL cleanup
            [("org_id", 1), ("type", 1), ("status", 1)],
        ]
```

Write cost is low. A Session is created once per token issuance, not per invocation. An associate invoked millions of times reuses its service token's Session. No write amplification.

Expired Sessions TTL-delete after a grace period (default 7 days). Audit lives in the changes collection independently.

## Session Management: Hybrid JWT + Session Entity

- **Access token**: JWT, short-lived (15 minutes default, configurable per org), carries `actor_id`, `org_id`, `role_set`, `jti`. Stateless verification — no DB hit on the hot path.
- **Refresh token** (user_interactive only): opaque random string, stored hashed in Secrets Manager via `refresh_token_ref` on the Session. Long-lived (7 days default). DB hit on refresh, refreshes are rare.
- **Long-lived tokens** (associate_service, tier3_api, cli_automation): opaque random string, hashed and stored. No refresh — rotation replaces. Validated by hash lookup against the Session.

### On every request (hot path)

1. Verify JWT signature (platform-wide signing key).
2. Check JWT expiry.
3. Check JWT `jti` against in-memory revocation list.
4. If `claims_stale == true` for the session, trigger auto-refresh with new claims (cheaper than full re-auth).
5. Set auth context: actor_id, org_id, role_set for downstream permission checks.

### On refresh

1. Look up Session by refresh token hash.
2. Verify status is active.
3. Check the actor's current role set — if changed, re-issue access token with new claims.
4. Rotate the refresh token (old one invalidated, new one issued with overlap window ~30s for race handling).
5. Update `last_active_at` on the Session.

### On revocation

1. Mark Session status as revoked.
2. Add JWT `jti` to the revocation list (cache TTL = remaining access token lifetime).
3. Change Stream event fires, every API instance picks up the revocation.
4. Audit: `auth.session_revoked` event in changes collection.

### JWT signing key: platform-wide

One signing key for the entire platform (rotated on schedule). Per-org isolation is achieved via `org_id` in the JWT claims + OrgScopedCollection enforcement, not via cryptographic key separation. Simpler key management, same security guarantee.

### Revocation cache lifecycle

- **In-memory per API instance**, keyed by JWT jti.
- **Invalidated via Change Stream** on Session entity `status_changed[to=revoked]` events.
- **Bootstrap on instance startup**: query Sessions revoked in the last 15 minutes (= max access token lifetime), populate the cache. Prevents a freshly-started instance from having a stale cache until Change Stream catches up.
- **TTL eviction**: entries expire at 15 minutes (matching max access token lifetime). Older revocations are moot because their access tokens are already expired.

## Authentication Methods

### The five method types (MVP)

Reduced from the initial seven by merging `service_token` and `api_key` into a unified `token` type, and deferring WebAuthn to post-MVP.

1. **`password`** — kernel-native. Argon2id hash stored in MongoDB (Argon2id is non-reversible; defense-in-depth via OrgScopedCollection). Password itself never stored.
2. **`totp`** — kernel-native. TOTP shared secret stored in Secrets Manager via `secret_ref`. Standard RFC 6238 implementation via pyotp.
3. **`sso`** — via Integration. `provider_integration_id` references an identity_provider Integration. Login flow redirects to IdP, validates the returned token via the adapter's JWKS, looks up Actor by verified email or external_id.
4. **`token`** — kernel-native long-lived opaque token. Usage field distinguishes: `associate_service`, `tier3_api_key`, `cli_automation`. Hashed and stored; validated by lookup.
5. **`magic_link`** — kernel-native one-time token for invitations and recovery. Stored hashed in Secrets Manager. On use, converts to setting a password method or completing SSO binding, then deactivates.

### Deferred to post-MVP

- **WebAuthn / passkeys** — more secure than TOTP but significantly more complex (browser cryptographic primitives, credential registration, attestation). Additive — can be added later as a new method type without architectural change.

### Authentication methods on Actor

```python
authentication_methods: list[AuthMethod]

AuthMethod = {
    "type": Literal["password", "totp", "sso", "token", "magic_link"],
    "enabled": bool,
    "created_at": datetime,
    "last_used_at": Optional[datetime],
    "secret_ref": Optional[str],              # Secrets Manager path
    "provider_integration_id": Optional[str], # For sso: which IdP Integration
    "metadata": dict                          # Method-specific (token usage, backup codes ref, etc.)
}
```

### Method resolution during login

- **Password login**: look up actor by email → find password method → verify hash against Secrets Manager → check if target role requires MFA → if yes, prompt second factor → verify TOTP → issue session with `mfa_verified = true`.
- **SSO**: redirect to IdP → validate returned token → look up actor by verified identity → find SSO method referencing the IdP Integration → issue session (MFA handled by IdP, session marked `mfa_verified = true` if IdP provided MFA claim).
- **Token** (all usages): look up Session by token hash → verify active and not expired → set auth context. No DB-heavy refresh dance; stateless access via hash lookup.
- **Magic link**: verify token hash against stored reference → transition Actor from `provisioned` to `active` (if invitation) → prompt user to set a password method → issue user_interactive session.

## MFA Policy

**Placement: Role-level with Actor override and Organization default.**

```python
class Role(Entity):
    mfa_required: bool = False             # This role requires MFA verification

class Actor(Entity):
    mfa_exempt: bool = False               # Emergency/accessibility override

class Organization(Entity):
    default_mfa_required: bool = False     # Org-wide default for roles that don't specify
```

Resolution at login:
1. User authenticates via their chosen method.
2. Kernel computes effective MFA requirement:
   - If actor is `mfa_exempt`, no MFA required (audited, requires admin to set).
   - Otherwise, if any of the actor's active roles has `mfa_required = true`, MFA required.
   - Otherwise, if the org has `default_mfa_required = true` and no roles explicitly say otherwise, MFA required.
3. If MFA required and not yet verified this session, prompt for TOTP.
4. On successful verification, set `session.mfa_verified = true` and `session.mfa_verified_at = now`.

This matches operational language: "all underwriters must have MFA" (role-level), "this specific actor is exempt for accessibility" (actor override, audited), "our entire org requires MFA" (org default).

### Fresh MFA re-verification for sensitive operations

Some operations should require MFA verified in the last N minutes even within an MFA-verified session: rotating credentials, granting admin roles, platform admin cross-org access, deleting high-value entities.

Extension to `@exposed`:

```python
@exposed(requires_fresh_mfa=15)  # MFA must be verified within last 15 minutes
async def rotate_credentials(self):
    ...
```

Auth middleware checks `session.mfa_verified_at > now - requires_fresh_mfa` before allowing the call. If stale, returns a challenge response; user re-verifies TOTP; cached for N minutes after success.

Small extension to the existing `@exposed` mechanism. No new primitive.

## Platform Admin Cross-Org Model

Refined based on Craig's signal: "We will be building most things for the customer." Platform admin access is an **operational pattern**, not rare incident response. FDEs and implementation engineers are routinely building inside customer orgs.

### The `_platform` system org

A special system organization with ID `_platform`. Indemn staff are members with platform admin roles. The kernel specifically honors platform admin roles for cross-org operations via `PlatformCollection` (mentioned in session 4 data architecture review) — the accessor that bypasses normal OrgScopedCollection filtering.

### Platform admin session mechanics

When a platform admin needs to act inside a customer org:

```bash
indemn platform access-org gic-underwriters \
  --work-type build \
  --duration 4h \
  --reason "building renewal workflow per SOW #12"
```

Creates a Session with:

```python
{
    "type": "user_interactive",
    "actor_id": fde_actor_id,
    "org_id": "gic-underwriters",          # Target org, not FDE's home org
    "platform_admin_context": {
        "work_type": "build",              # build | debug | incident | routine
        "reason": "building renewal workflow per SOW #12",
        "originating_actor": "fde@indemn.ai",
        "home_org": "_platform",
        "duration": "4h",
        "idle_timeout": "30m"
    },
    "expires_at": now + 4h,
    ...
}
```

### Duration and renewal

- **Default duration**: 4 hours
- **Max duration**: 24 hours (configurable per-customer)
- **Auto-renewable on activity**: while the platform admin is actively making requests, the session renews. Idle timeout (default 30 minutes of no activity) triggers expiration.
- **Short duration for security ops**: incident response sessions use `--work-type incident --duration 15m` — short-lived, not auto-renewed, for damage control.

### Work-type tagging

`--work-type` categorizes the session for audit and notification:
- **`build`**: routine building of customer workflows (FDE work)
- **`debug`**: investigating a specific issue
- **`incident`**: responding to a security or operational incident
- **`routine`**: regular operational check-ins

Customer notifications and audit reports can filter by work type.

### Customer notification (configurable per customer org)

Each customer org configures its platform-admin notification policy:

- **`notify_on_start`**: Slack/email alert when a platform admin session begins (default)
- **`notify_on_every_request`**: alert on every operation (most verbose, for high-sensitivity customers)
- **`daily_summary`**: one daily digest of all platform admin activity
- **`silent`**: audit record only, no notifications

Default: `notify_on_start`.

### Scope limits (even for platform admin)

- **Cannot read secrets**: Secrets Manager references remain opaque. Platform admin sees `secret_ref: "/indemn/prod/org/gic/integration/INT-001"` but cannot resolve the secret value.
- **Cannot modify Integration credentials**: except via the specific audited `indemn integration rotate-credentials` flow.
- **Cannot impersonate customer users**: the session identity is the Indemn actor, not a customer user clone. All audit records attribute actions to the Indemn identity.
- **Cannot escalate privileges**: platform admin has platform admin role; they cannot grant themselves additional customer-org roles.

### Audit guarantees

Every operation by a platform admin is recorded in the **target org's changes collection** (not the Indemn `_platform` org's) with:
- `actor_type: platform_admin`
- `acting_actor_id`: the Indemn actor
- `home_org`: `_platform`
- `session_id`: the platform admin session
- `work_type`, `reason`: from the session context
- `timestamp`: the action time

Customer orgs can retrospectively audit all platform admin activity via the base UI changes view, filtered by `actor_type = platform_admin`.

## Tier 3 Self-Service Signup

**MVP scope**: enough for developers to sign up, get an org, and start building.

### Flow

1. Developer visits `indemn.ai/signup`.
2. Form: email, password, org name.
3. Kernel creates:
   - `Organization` entity with the provided name
   - `Actor` entity (first admin) with `status: provisioned`
   - `password` authentication method (hash stored in MongoDB)
   - `magic_link` method for email verification
4. Email sent with verification link (via Indemn's platform-level email delivery Integration).
5. User clicks verification link.
6. Kernel verifies the magic_link token, transitions Actor to `active`, deactivates the magic_link method.
7. Kernel issues the first API key for the Actor (a `token` method with `usage: tier3_api_key`).
8. Developer is presented with: developer portal link, API docs, starter tutorial, their API key (shown once, cannot be retrieved later).

### Not in MVP

- Billing integration
- Plan selection
- Email domain verification (enterprise sign-ups flow through a different path)
- Sub-user invitation from Tier 3 admin to team members
- OAuth app management

These are commercial/operational concerns beyond the core auth design. Deferred until there's a real customer need.

## Recovery Flows

Three recovery scenarios, each with a distinct mechanism. **No back doors. No security questions. No SMS (phishable).**

### 1. Password reset

1. User clicks "Forgot password" on login.
2. Enters email.
3. Kernel looks up Actor, creates a `magic_link` method with a one-time token, sends email.
4. User clicks link → magic_link verified → prompted for new password.
5. New password hash replaces old (or the old password method is deactivated and a new one is created).
6. All existing sessions for that actor are revoked (security).
7. User logs in with new password.
8. Audit: `auth.password_changed`, `auth.session_revoked` (for each revoked session).

### 2. MFA recovery

Two paths, in order of preference:

**a) Backup codes** (pre-generated at MFA enrollment):
1. At TOTP enrollment, kernel generates 10 single-use backup codes, stores them hashed in Secrets Manager, displays once to user.
2. If MFA device lost, user enters a backup code on the MFA challenge screen.
3. Code is verified against hashes, marked used.
4. User logs in successfully, immediately prompted to re-enroll MFA on a new device.

**b) Admin reset** (when backup codes are lost too):
1. User contacts an admin with `can_grant` on their role.
2. Admin runs `indemn actor mfa-reset sarah@gicunderwriters.com`.
3. Kernel disables the TOTP method on the target actor.
4. Next time the actor logs in, they are forced to re-enroll MFA.
5. Audit: `auth.mfa_reset` with acting admin identity and reason.

### 3. Emergency access (org admin fully locked out)

1. The org's last admin cannot log in (password + MFA both unrecoverable, no other admin has `can_grant`).
2. Requires Indemn platform admin intervention.
3. Platform admin creates a cross-org session with `--work-type incident --reason "emergency access recovery for org admin"`.
4. Resets the customer admin's auth methods via an audited flow.
5. Sends a new magic_link to the customer admin.
6. Full notification to the customer org and permanent audit record.

## Authentication Audit

Auth events go in the changes collection with specific event types. Same collection as entity mutations, same tamper-evident hash chain (from session 4 security design).

### Event types

- `auth.login_attempt` — success or failure, with method, IP, user_agent
- `auth.session_created`
- `auth.session_refreshed`
- `auth.session_revoked`
- `auth.session_expired`
- `auth.mfa_enrolled`
- `auth.mfa_challenged` — success or failure
- `auth.mfa_reset`
- `auth.password_changed`
- `auth.method_added`
- `auth.method_removed`
- `auth.role_granted`
- `auth.role_revoked`
- `auth.lifecycle_transitioned` — Actor state change
- `auth.platform_admin_access` — cross-org access start
- `auth.brute_force_lockout` — rate limit triggered

### Surfaces

- **Base UI**: admins see an "Auth Events" view scoped to their org. Regular users see their own events (login history, session list, recent auth activity).
- **CLI**: `indemn audit auth --actor sarah@... --since 7d` queries auth events from the changes collection.
- **Export**: standard changes collection export — auth events flow with everything else.

## Role Change Handling: Claims Refresh, Not Revocation

When an actor's role set changes mid-session, the user should not be logged out. But existing access tokens carry the old role set in their claims.

### Mechanism

- **Role granted** (additive, no security concern): next access-token refresh picks up new claims (within the access token lifetime, max 15 minutes). No immediate action needed.
- **Role revoked** (removes permissions, security concern): kernel sets `claims_stale = true` on all active sessions of the affected actor. Next API request detects stale claims, triggers auto-refresh (mini-refresh — no re-authentication, just new access token with updated claims). User sees new permissions reflected on next interaction without being kicked to a login screen.
- **Actor suspended or deprovisioned**: full session revocation, not just claims refresh. User is logged out entirely.

### Why not always revoke on role change

Full revocation means the user gets dumped to a login screen — jarring and unnecessary for routine role changes. Claims refresh is cheaper, matches user expectations, and still delivers the security guarantee (new access tokens have the updated role set).

## Default Assistant Authentication

The base UI has a default associate for every human actor (`owner_actor_id` binding from session 5). When a user is logged in, the default assistant is active. How does it authenticate?

**Decision: the default assistant inherits the user's session.**

The default assistant is not an independent entity — it is a projection of the user into a running actor. Its harness authenticates using the user's session JWT (injected at session start). Every action taken by the assistant is audited as "user X via default associate performed Y." Permissions exactly match the user's. When the user logs out, the assistant's session dies with it.

### Distinct from owner-bound scheduled associates

Other owner-bound associates — Craig's Gmail sync, scheduled background workers — use their own service tokens. They run independently of user sessions, on cron or on message triggers. They access the owner's Integrations via the credential resolution model from the CRM retrace (session 5).

**Two patterns**:

| Pattern | Authentication | Lifetime |
|---|---|---|
| Default assistant in UI | User session inheritance | Tied to user session |
| Owner-bound scheduled associate | Own service token + owner's Integration access | Runs independently |

Both patterns are valid. The right choice depends on the associate's lifecycle.

## First-Org Bootstrap

The invitation flow assumes email delivery via an org-level Integration. But the first org on the platform doesn't have one yet — Indemn is bootstrapping.

**Resolution**: `indemn platform init --first-admin email@indemn.ai` prints a one-time magic_link token to stdout. The first admin uses it to set up the `_platform` org. After the first admin configures the platform's email delivery Integration, subsequent invitations use email.

Same mechanism (magic_link method), different delivery channel for bootstrap (stdout instead of email).

## Pre-Auth Rate Limiting

Brute-force protection happens in the kernel auth middleware, before password verification.

- Counts failed attempts keyed by `(ip_address, email_hash)` in an in-memory counter per API instance, synced via Change Stream for cross-instance coordination.
- Per-org configurable thresholds: N failures within T minutes → L-minute lockout.
- Default: 5 failures in 10 minutes → 30-minute lockout.
- Lockout released by time, not user action.
- Audit: every failure is `auth.login_attempt[success=false]`. Lockout triggers `auth.brute_force_lockout`.

## Kernel Additions Required

| # | Addition | Type |
|---|---|---|
| 1 | **Session bootstrap entity** (universal across all auth types) | New bootstrap entity |
| 2 | Actor.authentication_methods field | Extension |
| 3 | Actor.status state machine (provisioned → active → suspended → deprovisioned) | Extension |
| 4 | Actor.mfa_exempt field | Extension |
| 5 | Role.mfa_required field | Extension |
| 6 | Role.can_grant field | Extension (already decided session 5) |
| 7 | Organization.default_mfa_required field | Extension |
| 8 | @exposed.requires_fresh_mfa parameter | Extension to @exposed mechanism |
| 9 | Auth API endpoints (/auth/login, /auth/refresh, /auth/logout, /auth/challenge, /auth/recover) | Hand-built workflows (not auto-generated) |
| 10 | Kernel auth middleware (validation + rate limiting + audit) | Kernel code |
| 11 | JWT signing/validation (platform-wide key) | Kernel code |
| 12 | Revocation cache (Change Stream invalidation + startup bootstrap) | Kernel code |
| 13 | Password hashing (Argon2id) | Kernel dependency |
| 14 | TOTP library | Kernel dependency |
| 15 | Platform admin cross-org model (`_platform` org + PlatformCollection + work-type tagging) | Extension |

**One new bootstrap entity. Five auth method types. Everything else is extensions or middleware.** Proportional to what auth requires.

## Pressure-Tested Scenarios

All ten forcing functions walk cleanly through the design.

### Scenario 1: New Indemn team member

1. Craig runs `indemn actor create --name "Alex" --email alex@indemn.ai --role engineer`.
2. Kernel creates Actor in `provisioned` status, creates a magic_link method, sends invitation email via platform email Integration.
3. Alex clicks the email link, verifies the magic_link token.
4. Kernel prompts Alex to set a password.
5. Alex sets password (Argon2id hash stored in MongoDB).
6. Kernel prompts Alex to enroll MFA (TOTP). Alex scans QR code, confirms, generates backup codes, saves codes.
7. Actor transitions to `active`. magic_link method deactivated. password + totp methods active.
8. Alex logs in for the first time with password + TOTP, gets a `user_interactive` Session, starts working.

### Scenario 2: Enterprise SSO (GIC Okta)

1. GIC admin runs `indemn integration create --owner org --name "GIC Okta" --system-type identity_provider --provider okta --provider-version okta_oidc_v1`.
2. Configures the Integration with Okta OIDC discovery URL and client credentials (stored in Secrets Manager via secret_ref).
3. For each existing GIC user, admin adds an `sso` method referencing this Integration.
4. Users log in via SSO: visit GIC's login, click "Sign in with Okta," redirect to Okta, authenticate there, return with validated token, kernel looks up Actor by verified email, issues user_interactive Session.
5. GIC admin retains password method for emergency access. Uses password fallback if Okta is ever down.
6. Both methods coexist. GIC chooses which is primary via org policy.

### Scenario 3: Tier 3 self-service signup

1. Developer visits indemn.ai/signup, fills out form: email, password, org name "DevCorp."
2. Kernel creates Organization "DevCorp," creates admin Actor in `provisioned` status with password + magic_link methods.
3. Email sent with verification link.
4. Developer clicks link, Actor transitions to `active`, first API key issued.
5. Developer is shown their API key (once), developer portal link, starter tutorial.
6. Developer starts building immediately using the API key in their scripts.

### Scenario 4: Associate service token

1. When an associate is created via `indemn actor create --type associate --name "Classifier" ...`, kernel auto-generates a `token` method with `usage: associate_service`.
2. Token hash stored in Secrets Manager; raw token returned to the creator once.
3. Associate's harness (Temporal worker, chat runtime) reads the token at startup, authenticates, gets a `associate_service` Session.
4. Session persists for the associate's deployment lifetime. Rotation via `indemn actor rotate-credentials ASSOCIATE-001` creates a new token + Session.
5. Old session is revoked after a grace period to allow deployment rollout.

### Scenario 5: Emergency admin access (SSO broken)

1. GIC's Okta has an outage. Nobody can log in via SSO.
2. GIC admin uses their retained password method: visits login, chooses "Password login," enters credentials, completes MFA (TOTP via authenticator app — independent of Okta).
3. Gets a user_interactive Session and operates the system.
4. Once Okta recovers, standard SSO flow resumes for other users.
5. Password fallback is always available — password methods never get disabled unless the org explicitly removes them.

### Scenario 6: Brute force protection

1. Attacker tries to brute-force Sarah's password.
2. After each failed attempt, kernel auth middleware records the failure keyed by `(ip_address, sarah@gicunderwriters.com)`.
3. After 5 failures in 10 minutes, lockout: the middleware returns 429 Too Many Requests for the next 30 minutes.
4. During lockout, even correct passwords are rejected (prevents timing attacks).
5. Audit: 5 `auth.login_attempt[success=false]` events + 1 `auth.brute_force_lockout` event.
6. Ops sees the lockout event in the Auth Events view.
7. Sarah is notified (via configured channel) that her account had failed login attempts.
8. Lockout expires automatically after 30 minutes. If attacks continue, the next window triggers another lockout.

### Scenario 7: Stolen laptop revocation

1. Kyle's laptop is stolen.
2. Kyle calls Indemn on-call.
3. On-call platform admin: `indemn platform access-org indemn --work-type incident --duration 15m --reason "kyle laptop stolen"`. Short duration for security op.
4. `indemn session revoke --actor kyle@indemn.ai --all`.
5. Kernel iterates Kyle's active Sessions (all types), marks each revoked.
6. Change Stream fires; revocation cache on every API instance picks up the revoked JWT jtis within seconds.
7. All Kyle's tokens fail on next use.
8. Audit: every revocation logged with reason, acting admin, timestamp.
9. Kyle logs in from a new device with SSO (password unchanged). New Session created. Back to work.

Unified Session + revocation cache handles this cleanly. No special case.

### Scenario 8: Role change mid-session

Sarah is a CSR. JC grants her temporary underwriter access for cross-training.

1. `indemn actor add-role sarah@gicunderwriters.com --role underwriter`.
2. Kernel validates JC's role has `can_grant: ["underwriter"]`. ✓
3. Role added to Sarah's Actor.
4. Kernel marks Sarah's active Sessions as `claims_stale = true`.
5. Sarah's next API request detects stale claims, auto-refreshes. New access token has expanded role set.
6. Sarah's UI re-queries permissions on the refreshed session; underwriter views appear automatically.
7. **No re-login. No "session expired" message.**

Reverse flow (role revocation): claims marked stale, next request refreshes to narrower permissions, underwriter views disappear.

### Scenario 9: Platform admin building for customer

FDE building a custom workflow for GIC.

1. `indemn platform access-org gic-underwriters --work-type build --duration 4h --reason "building renewal workflow per SOW #12"`.
2. Kernel validates FDE is a member of `_platform` org with platform admin role.
3. Session created: `type=user_interactive`, `org_id=gic-underwriters`, `platform_admin_context={work_type: "build", reason: ..., originating_actor: fde@indemn.ai, home_org: _platform, duration: 4h, idle_timeout: 30m}`, `expires_at=now+4h`.
4. GIC's configured notification fires. GIC has `notify_on_start`, so their admin gets a Slack message: "FDE at Indemn started a 4-hour build session in your org. Reason: building renewal workflow per SOW #12."
5. FDE works inside GIC's org: creates entity definitions, configures rules, activates capabilities, tests workflows. Every operation is audited in GIC's changes collection with `actor_type: platform_admin`, `acting_actor_id: fde@indemn.ai`, `session_id`, `work_type: build`.
6. Session auto-renews on activity. FDE takes a lunch break; after 30 minutes of no activity, session enters paused state. FDE returns, resumes activity, session reactivates.
7. When the FDE is done (or the 4 hours pass), session expires. Final audit record written.
8. GIC's admin can retrospectively audit everything via the base UI's changes view filtered by `actor_type = platform_admin`.

Routine build work, fully audited, customer-visible, scope-limited.

### Scenario 10: MFA device lost

Sarah loses her phone.

**Backup code path** (preferred):
1. Sarah logs in with password, prompted for MFA.
2. Sarah enters a backup code instead of TOTP.
3. Kernel verifies against hashed backup codes in Secrets Manager, marks code used.
4. Session issued with `mfa_verified = true`.
5. Sarah is prompted to re-enroll MFA on a new device. She does.

**Admin reset path** (if backup codes also lost):
1. Sarah calls JC.
2. JC runs `indemn actor mfa-reset sarah@gicunderwriters.com`.
3. Kernel verifies JC has `can_grant` authority on Sarah's role.
4. Sarah's TOTP method disabled. Audit: `auth.mfa_reset` with JC as acting admin.
5. Next time Sarah logs in, she authenticates with password only (no MFA prompt since TOTP is disabled), then is immediately prompted to enroll new TOTP.
6. She enrolls, generates new backup codes, is logged in.

No back doors. No security questions. Recovery requires either pre-generated codes or an authorized admin with full audit.

## What's Decided

1. **Authentication is designed end-to-end.** Item 10 from the post-trace synthesis is resolved.
2. **Session is a new bootstrap entity.** Bootstrap count moves from 6 to 7 (Org, Actor, Role, Integration, Attention, Runtime, Session).
3. **Session applies to all auth types uniformly.** type field distinguishes user_interactive, associate_service, tier3_api, cli_automation. One validation path, one revocation mechanism, one audit trail.
4. **Hybrid JWT + Session model.** Short-lived access tokens (15 min default, stateless verification), long-lived opaque refresh tokens (for user_interactive, stored hashed in Secrets Manager). Platform-wide JWT signing key.
5. **Five authentication method types for MVP**: password, totp, sso, token, magic_link. WebAuthn deferred.
6. **Authentication methods are a list on Actor** (decided session 5, formalized here).
7. **Identity providers are Integrations** (decided session 5, formalized here).
8. **Actor lifecycle state machine**: provisioned → active → suspended → deprovisioned. Formalized as an entity state machine.
9. **MFA policy placement**: Role-level `mfa_required` with Actor-level `mfa_exempt` override and Organization-level `default_mfa_required`. Resolution: actor exempt > role required > org default.
10. **Fresh MFA re-verification**: `@exposed(requires_fresh_mfa=N)` decorator parameter. Small extension to existing mechanism.
11. **Platform admin cross-org model**: `_platform` system org, PlatformCollection accessor, time-limited sessions (4h default, 24h max), auto-renewable on activity with idle timeout, work-type tagging (build/debug/incident/routine), per-customer notification config, strict scope limits (no secrets, no credential modification, no impersonation), audit in target org's changes collection with full provenance.
12. **Claims refresh on role change**: Role revocation marks sessions `claims_stale = true`, next request auto-refreshes. Role granting picks up on next natural refresh. Full session revocation only on actor suspension/deprovisioning.
13. **Default assistant authentication**: inherits user's session. Owner-bound scheduled associates use their own service tokens.
14. **Credential storage**: Argon2id password hashes in MongoDB (non-reversible, defense-in-depth via OrgScopedCollection). Raw secrets (TOTP seeds, refresh tokens, backup codes, API key pre-hashes) in AWS Secrets Manager.
15. **Tier 3 signup MVP**: org + first admin + password + email verification + first API key. Billing, plans, domain verification, sub-user invitation deferred.
16. **Recovery flows**: password reset via magic_link, MFA recovery via backup codes or admin reset, emergency access via platform admin intervention. No back doors.
17. **Auth events in changes collection** with specific event types. Same tamper-evident hash chain as entity mutations.
18. **Pre-auth rate limiting** in kernel auth middleware. Keyed by (IP, email), in-memory per instance with Change Stream sync. Per-org configurable thresholds.
19. **Revocation cache**: in-memory per API instance, invalidated via Change Stream on Session `status_changed[to=revoked]`, bootstrap on instance startup from the last 15 minutes of revoked sessions.
20. **First-org bootstrap**: magic_link token via stdout for the first admin, before email Integration exists.

## What's Deferred

### To spec phase (not blocking)

- Password complexity rules (min length, required character classes) — per-org config, default to NIST guidelines
- Password history (can't reuse last N passwords) — per-org config
- Session concurrent limit per user — per-org config, default unlimited
- Idle timeout for user_interactive sessions — per-org config, default no idle timeout on access tokens
- Exact JWT claim format and signing algorithm
- Token rotation schedule (how often does Indemn rotate the platform-wide JWT signing key)
- Exact TOTP parameters (period, digits, algorithm — default to RFC 6238)
- Backup code count and format (default: 10 codes, 8 characters each)
- API key format (length, entropy, prefix)
- Email templates for invitation, password reset, MFA reset, platform admin notification
- UI/UX details of login flow, MFA challenge, recovery

### To future design (when forcing functions appear)

- **WebAuthn / passkeys** — more secure MFA option than TOTP. Add as a new method type when browser support and operational needs align.
- **SAML** — if a customer requires it. OIDC handles most enterprise SSO. SAML added if forced.
- **SCIM provisioning** — automated user provisioning from enterprise identity systems. Added when a customer demands it.
- **OAuth app registration** — for third-party apps that want to authenticate on behalf of users. Deferred until there's a real use case.
- **Social login** (Google, GitHub) — for Tier 3 convenience. Not MVP.
- **Delegated consent UI** — for users to grant third-party apps permission to access their data. Deferred with OAuth.
- **Passwordless login** — email magic-link as primary method (not just recovery). Deferred.
- **Hardware security keys** — for platform admin only. Deferred.

### To separate operational design

- Billing and plan selection for Tier 3 signup
- Email domain verification for enterprise orgs
- Self-service sub-user invitation for Tier 3 admins
- Customer notification channels beyond Slack/email (Teams, PagerDuty, webhook)
- Platform admin role granularity (not all Indemn staff need full platform admin)

## Relationship to Prior Decisions

- **Session 4 security design** (OrgScopedCollection, AWS Secrets Manager, tamper-evident changes collection): this artifact builds on all three. OrgScopedCollection handles data isolation; Secrets Manager holds credentials; changes collection captures auth events.
- **Session 5 default chat assistant** (INDEX.md 2026-04-10): this artifact formalizes the assistant's auth model — user session inheritance.
- **Session 5 owner_actor_id on associates** (from CRM retrace): orthogonal to assistant auth. Owner-bound scheduled associates use their own service tokens, default assistant in UI inherits user session. Both patterns valid.
- **Session 5 Integration as primitive #6**: reused for identity providers (SSO). Same adapter pattern, same credential management via secret_ref.
- **Session 5 `owner_actor_id` credential resolution**: platform admin model doesn't use this — platform admin accesses via `_platform` org membership and PlatformCollection accessor, not owner-based delegation.
- **Session 6 bulk operations pattern**: bulk ops respect auth. The `bulk_execute` Temporal workflow runs under the initiating actor's session; permissions checked per entity operation, not once at the start.
- **Session 6 base UI operational surface**: the base UI uses auth events to populate the "Auth Events" view; auth middleware enforces role-based permissions for the auto-generated entity views.

## Open Follow-Ups (Not Blocking Architecture)

- **JWT signing key rotation schedule.** Platform-wide signing key needs periodic rotation. Exact schedule (quarterly? yearly?) is operational, not architectural. Mechanism: kernel supports multiple valid signing keys (new + recent for verification, one current for signing).
- **Per-operation sensitivity marking.** Which operations get `requires_fresh_mfa` is a domain decision, not a kernel decision. The kernel provides the mechanism; specific entities mark their sensitive methods.
- **Platform admin role granularity within `_platform` org.** Not all Indemn staff need full platform admin across all customer orgs. Sub-roles (support-read-only, fde-build, incident-respond, security-audit) can be designed when team operational patterns clarify.
- **Cross-session coordination for the revocation cache at scale.** At small scale, Change Stream on Session updates is sufficient. At scale, might need Redis Pub/Sub or an explicit revocation topic. Additive when forcing function appears.
- **Session entity archival strategy.** TTL-delete after 7 days of being expired. But for compliance-heavy customers, might want longer retention. Per-org config when needed.

## Summary

Authentication is designed end-to-end with one new bootstrap entity (Session), five auth method types, a hybrid JWT + opaque refresh token model, role-level MFA policy with overrides, a platform admin cross-org model optimized for routine building-for-customers work, claims refresh for mid-session role changes, recovery flows without back doors, and full audit integration with the existing changes collection.

The ten forcing functions all walk cleanly through the design. Complexity is proportional to requirements. The architecture earns every addition.

Item 10 resolved. Remaining: documentation sweep (items 4, 5, 6, 11, 12), simplification pass, spec writing.
