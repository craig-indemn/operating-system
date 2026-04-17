# Notes: /Users/home/Repositories/indemn-os/kernel/auth/session_manager.py

**File:** /Users/home/Repositories/indemn-os/kernel/auth/session_manager.py
**Read:** 2026-04-16 (full file — 68 lines)
**Category:** code

## Key Claims

- Module docstring: "Session lifecycle management. Creates, validates, and revokes Session entities. Phase 1: basic session creation for password and token auth. Phase 4 adds: SSO, MFA, platform admin sessions, revocation cache."
- `create_session(actor, auth_method, session_type, ip_address, user_agent, expire_minutes)` — creates Session entity, issues JWT, returns `(session, token)`.
- `revoke_session(session_id)` — transitions Session to revoked via save_tracked.
- `revoke_all_sessions(actor_id)` — revokes all active sessions for an actor.

## Architectural Decisions

- Session is kernel entity (bootstrap) — matches design.
- JWT creation via `kernel.auth.jwt.create_access_token`.
- Role names loaded at session creation time and embedded in JWT claims.
- Session status transitions via state machine (`transition_to("revoked")`).
- `save_tracked` used for revocation (audit trail in changes collection) — correct.
- `system:revocation` sentinel actor_id for system-initiated revocations.

## Layer/Location Specified

- Kernel code: `kernel/auth/session_manager.py`.
- Matches design (2026-04-11-authentication-design.md): session lifecycle is kernel-side.
- Runs in kernel API server process (called by auth endpoints).

**No layer deviation.**

## Dependencies Declared

- `bson.ObjectId`
- `datetime`, `timedelta`, `timezone`
- `kernel.auth.jwt.create_access_token`
- `kernel.config.settings`
- `kernel_entities.session.Session`
- `kernel_entities.role.Role`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/auth/session_manager.py`
- Called by: `kernel/api/auth_routes.py` (login endpoint), `kernel/api/registration.py` (Tier 3 signup)

## Cross-References

- Design: 2026-04-11-authentication-design.md §"Session Management"
- Phase 1 spec §1.22 Authentication
- Phase 4-5 spec §4.9 Authentication Completion
- `kernel_entities/session.py` — Session schema (bootstrap entity)
- `kernel/auth/jwt.py` — JWT signing/verification

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The revocation cache (in-memory per instance) is separate from this file — lives in `kernel/auth/jwt.py` per Phase 4 spec.
- Session TTL cleanup (7 days after expiration) not visible here — likely a queue processor sweep.
- `create_session` doesn't currently handle refresh tokens — refresh is opaque random string stored in Secrets Manager per design, implemented separately.

Kernel-side session manager is correctly placed per design. No architectural concerns.
