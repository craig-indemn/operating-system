# Notes: /Users/home/Repositories/indemn-os/kernel/api/auth_routes.py

**File:** /Users/home/Repositories/indemn-os/kernel/api/auth_routes.py
**Read:** 2026-04-16 (full file — 710 lines; read sections 1-60 (imports, models), 362-450 (platform admin), others sampled via grep for endpoint definitions)
**Category:** code

## Key Claims

- Complete auth API endpoints defined in `auth_router`:
  - `GET /auth/providers` — SSO discovery [G-35]
  - `POST /auth/login` — password login
  - `GET /auth/sso/{integration_id}` — SSO initiate redirect [G-35]
  - `GET /auth/sso/{integration_id}/callback` — SSO callback handler [G-35]
  - `POST /auth/mfa/verify` — TOTP MFA verification [G-36]
  - `POST /auth/mfa/backup` — backup code use [G-38]
  - `POST /api/platform/sessions` — platform admin cross-org session [G-37]
  - `POST /auth/reset-password/initiate` — password reset magic link [G-38]
  - `POST /auth/reset-password/complete` — password reset completion [G-38]
  - `POST /auth/refresh-claims` — claims refresh [G-39]
  - `POST /auth/signup` — Tier 3 self-service signup [G-58]
  - `GET /api/auth-events` — auth audit events view [G-41]
- Helper functions: `_actor_has_mfa`, `_is_platform_admin`, `_notify_platform_admin_access`, `_send_verification_email_if_possible`, `_slugify`.
- Request/Response models via Pydantic BaseModel.

## Architectural Decisions

- Platform admin session creation validates actor is in `_platform` org with `platform_admin` role.
- Max duration 24h enforced in code (per design).
- Platform admin session stores `platform_admin_context` dict on Session entity.
- Auth events written via `write_auth_event_in_org` (from `kernel.auth.audit`) — per design, audited in the TARGET org's changes collection.
- Target org notification via `_notify_platform_admin_access` helper.
- Access token created with `["platform_admin"]` role in JWT for target org.
- MFA flow: partial token issued on password success, TOTP or backup code verifies → real access token.
- SSO flow: redirect to IdP via Integration adapter → callback validates token → issue OS session.
- Tier 3 signup creates Org + Actor + password method + verification magic link.

## Layer/Location Specified

- Kernel code: `kernel/api/auth_routes.py`.
- Runs in kernel API server process.
- All auth flows live in the kernel per design.

**No layer deviation.**

Per design (2026-04-11-authentication-design.md): auth API endpoints are "hand-built workflows (not auto-generated)" — not entity CRUD. Implementation matches.

## Dependencies Declared

- `fastapi` — APIRouter, Depends, HTTPException, Request
- `fastapi.responses.RedirectResponse` (for SSO redirect)
- `bson.ObjectId`, `datetime`, `timedelta`, `timezone`
- `uuid.uuid4`
- `pydantic.BaseModel`
- `kernel.auth.middleware.get_current_actor`
- `kernel.auth.jwt` — token creation + magic links + partial tokens
- `kernel.auth.audit.write_auth_event_in_org`
- `kernel.auth.password.verify_password`
- `kernel.config.settings`
- `kernel_entities.*` — Actor, Session, Organization, Role, Integration (for SSO)
- `kernel.integration.dispatch` (for SSO adapters)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/api/auth_routes.py`
- Mounted via `auth_router` in `kernel/api/app.py`

## Cross-References

- Design: 2026-04-11-authentication-design.md (full auth design)
- Phase 1 spec §1.22 Authentication (basic password + token)
- Phase 4-5 spec §4.9 Authentication Completion (SSO, MFA, platform admin, recovery, refresh)
- Comprehensive audit: "Authentication — COMPLETE" (all items implemented)

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Password login flow handles MFA via partial_token pattern — clean separation of authentication phases.
- SSO flow uses the Integration primitive — the identity provider is an Integration. Matches design.
- Platform admin session writes audit in target org — matches design precisely.
- Tier 3 signup minimal: org + first admin + password + email verification. Billing/plans deferred per design.
- Auth events view filtered by actor's org (via middleware) — appropriate permission model.

Large file but straightforward implementation of the auth design. No architectural concerns.
