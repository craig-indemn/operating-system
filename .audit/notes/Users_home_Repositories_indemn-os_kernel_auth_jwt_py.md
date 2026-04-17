# Notes: /Users/home/Repositories/indemn-os/kernel/auth/jwt.py

**File:** /Users/home/Repositories/indemn-os/kernel/auth/jwt.py
**Read:** 2026-04-16 (full file — 171 lines)
**Category:** code

## Key Claims

- JWT creation, verification, magic link tokens, partial (MFA challenge) tokens.
- In-memory revocation cache per API instance: `_revocation_cache: dict[str, float]`, TTL 900s.
- `create_access_token(actor_id, org_id, roles)` — JWT with `{actor_id, org_id, roles, jti, exp, iat}`.
- `verify_access_token(token)` — decode + check jti against revocation cache + evict expired entries.
- `create_partial_token(actor, session)` — 5-min token for MFA challenge; `purpose: "mfa_challenge"`.
- `verify_partial_token(token)` — checks purpose.
- `generate_magic_link_token(actor, purpose, expires_hours=4)` — for password reset/email verification.
- `verify_magic_link_token(token, purpose)` — checks purpose.
- Revocation cache bootstrap: `bootstrap_revocation_cache()` loads recently-revoked sessions on startup.
- Revocation cache watcher: `watch_revocations()` — async background task watching Session Change Stream for `status: "revoked"`.
- `revoke_in_cache(jti)` — direct add.
- `_evict_expired_cache()` — TTL eviction.

## Architectural Decisions

- Platform-wide JWT signing key (per design).
- HS256 algorithm (from `settings.jwt_algorithm`).
- jti (UUID) in every token for revocation tracking.
- 15-minute access token expiry (`jwt_access_token_expire_minutes`).
- In-memory revocation cache invalidated via MongoDB Change Streams on Session entity.
- Cache TTL = 15 minutes = max access token lifetime (older revocations are moot because tokens are already expired).
- Bootstrap on instance startup prevents stale cache until Change Stream catches up.
- Partial tokens and magic link tokens use `purpose` field for context-specific use.

## Layer/Location Specified

- Kernel code: `kernel/auth/jwt.py`.
- Runs in kernel API server process (tokens created at login, verified on every request).
- `watch_revocations` runs as a background task in the API server.
- `bootstrap_revocation_cache` runs on API server startup.
- Per design: JWT + revocation cache are kernel-side.

**No layer deviation.**

## Dependencies Declared

- `jwt` (PyJWT)
- `time`
- `datetime`, `timedelta`, `timezone`
- `uuid.uuid4`
- `kernel.config.settings`
- `kernel_entities.session.Session`
- `kernel.db.get_database` (for Change Stream)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/auth/jwt.py`
- Called from: `kernel/auth/middleware.py`, `kernel/auth/session_manager.py`, `kernel/api/auth_routes.py`, `kernel/api/registration.py`
- Bootstrap called from: `kernel/api/app.py` startup

## Cross-References

- Design: 2026-04-11-authentication-design.md §"Session Management: Hybrid JWT + Session Entity"
- Phase 1 spec §1.22 Authentication
- Phase 4-5 spec §4.9 Revocation Cache with Bootstrap
- `kernel_entities/session.py` — Session entity with access_token_jti field

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Per-instance in-memory cache — cross-instance coordination via Change Stream is scale-appropriate for MVP. Scale-up path (Redis Pub/Sub) is a design open item.
- 15-minute cache TTL matches access token lifetime — clean retention logic.
- Bootstrap loads last 15 minutes of revocations on startup to cover the gap until Change Stream catches up — correct per design.
- Magic link token expiry defaults to 4 hours — reasonable for email delivery + user action.
- `watch_revocations` is a fire-and-forget coroutine; crashes are logged but not re-started. This could leave revocation cache stale until next instance restart — potential operational concern but MVP-acceptable.

Auth JWT is correctly placed and implements the design. No architectural concerns.
