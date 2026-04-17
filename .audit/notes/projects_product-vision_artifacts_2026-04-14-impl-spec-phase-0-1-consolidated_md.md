# Notes: 2026-04-14-impl-spec-phase-0-1-consolidated.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-0-1-consolidated.md
**Read:** 2026-04-16 (full file — 3891 lines; read in chunks via offset/limit + targeted grep to cover all architectural sections. Section headers reviewed via grep; key sections read in full: 0-490, 2956-3075 auth, 380-430 CLAUDE.md)
**Category:** spec

## Key Claims

- Authoritative Phase 0+1 spec. Supersedes the base spec and addendum.
- "The architecture is final — this spec does not redesign. It specifies HOW to build what's been designed."
- **Explicitly deferred to later phases:**
  - Associate execution via Temporal (Phase 2)
  - Integration adapters (Phase 3; Integration kernel entity IS in Phase 1)
  - Base UI (Phase 4)
  - SSO, TOTP MFA, magic links (Phase 4)
  - **Real-time channels, harness pattern (Phase 5)**
- Phase 0 produces: repo + conventions + env + CI + deployment config.
- Phase 1 produces: base entity framework + auto-gen CLI/API/skill + state machines + changes collection + message queue + watches + rules + lookups + capability library + auth middleware + Session entity + 7 kernel entities.
- Repository structure (`indemn-os/`):
  - `kernel/` — all kernel code
  - `kernel_entities/` — 7 kernel entity classes
  - `seed/` — seed YAML (entities, skills, roles)
  - `tests/` — unit, integration, e2e
  - `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `CLAUDE.md`, `README.md`
- **`kernel/temporal/` in Phase 0-1 = STUBS ONLY**: `__init__.py` + `client.py` (Temporal client factory). "Phase 2 activation" for everything else. No `worker.py`, no `activities.py`, no `workflows.py` yet.
- Deployment: one Docker image, three Railway services: `indemn-api`, `indemn-queue-processor`, `indemn-temporal-worker`.
- CLAUDE.md conventions state:
  - "Modular monolith. One repo, one Docker image, three entry points."
  - **"Trust boundary: kernel processes (API, QP, TW) have direct MongoDB. Everything else uses the API."**
  - **"CLI always in API mode. Never direct MongoDB from CLI."**

## Architectural Decisions

- **Modular monolith**: one image, three entry points. API (port 8000), Queue Processor, Temporal Worker.
- **Trust boundary**: kernel processes (API Server, Queue Processor, Temporal Worker) have DB creds. "Everything else uses the API."
- **Entity types**:
  - Kernel entities: Python classes in `kernel_entities/`. Always available. 7 total.
  - Domain entities: Defined as data in MongoDB `entity_definitions` collection. Dynamic classes created at startup.
  - Both share BaseEntity. Both get auto-generated CLI, API, skills.
- **`save_tracked()` is the critical atomic transaction**: version check → entity write → computed fields → changes record (with hash chain) → watch evaluation → message creation.
- **Context variables** (`contextvars`) for `current_org_id`, `current_actor_id`, `current_correlation_id`, `current_depth`. Set by auth middleware on each request.
- **OrgScopedCollection** wraps all application queries. Never use raw Motor collections. `org_id` comes from contextvars.
- **PlatformCollection** for cross-org admin (bypasses org scoping).
- **Auth middleware**: sets context vars on each request, loads roles, validates JWT, sets `request.state.actor`.
- **JWT signing**: HS256, 15min expiry, jti for revocation.
- **Argon2id** for password hashing (time_cost=3, memory=64MB, parallelism=4, hash_len=32).
- **Selective emission**: only state transitions, exposed operations, and creation/deletion emit events.
- **Auto-generation from entity definitions**: CLI commands, API routes, skill markdown, UI (UI in Phase 4).

## Layer/Location Specified

- **Kernel code** lives in `kernel/` directory:
  - `kernel/entity/` (framework)
  - `kernel/message/` (queue + emit)
  - `kernel/watch/` (cache, evaluator, scope)
  - `kernel/rule/` (engine, lookup)
  - `kernel/capability/` (registry, auto_classify)
  - `kernel/auth/` (middleware, jwt, password, token, rate_limit)
  - `kernel/scoping/` (org_scoped, platform)
  - `kernel/changes/` (collection, hash_chain)
  - `kernel/observability/` (tracing, logging)
  - `kernel/api/` (app, registration, meta, websocket, webhook, health, errors, bootstrap)
  - `kernel/cli/` (app, registration, client, *_commands)
  - `kernel/skill/` (schema, generator, integrity)
  - `kernel/queue_processor.py` (sweep process)
  - `kernel/temporal/` (STUBS in Phase 0-1: client.py only)
  - `kernel/seed.py` (seed loader)
- **Kernel entities** in `kernel_entities/` — 7 classes (organization, actor, role, integration, attention, runtime, session).
- **Seed YAML** in `seed/entities/`, `seed/skills/`, `seed/roles/`.
- Dockerfile: multi-entry-point (one image, different CMDs per service).
- docker-compose: API + Queue Processor + Temporal dev.

**Critical Layer Statement** (CLAUDE.md, line 381-383):
```
- Modular monolith. One repo, one Docker image, three entry points.
- Trust boundary: kernel processes (API, QP, TW) have direct MongoDB. Everything else uses the API.
- CLI always in API mode. Never direct MongoDB from CLI.
```

**Phase 0-1 spec is silent on harnesses** — explicitly deferred to Phase 5. The repo structure does NOT include a `harnesses/` directory. The spec assumes harnesses will be added later.

**Phase 0-1 spec sets up `kernel/temporal/client.py` as a STUB**. The full `kernel/temporal/` is populated in later phases. Notably:
- Phase 2 activates Temporal execution (the spec says this — "Temporal client factory (Phase 2 activation)" in the repo structure at line 147).
- The Phase 2 spec must specify what gets added to `kernel/temporal/` and where agent execution lives.
- **If Phase 2 adds `activities.py` with `process_with_associate` inside the kernel's Temporal Worker (which the Pass 1 audit found), that's where Finding 0's code path was introduced.**

## Dependencies Declared

Python 3.12+, uv, Beanie/Motor/PyMongo (MongoDB), FastAPI/uvicorn, Typer, httpx, Pydantic, pyjwt, argon2-cffi, pyotp, temporalio, OpenTelemetry, boto3 (AWS), orjson, python-multipart, pyyaml, jsonschema, croniter.

## Code Locations Specified

See "Layer/Location Specified" above for full tree. The key architectural-layer claims:
- All kernel code in `kernel/`
- All kernel entities in `kernel_entities/`
- No harness code in Phase 0-1 repo
- Temporal code starts as stub, expected to grow in later phases

## Cross-References

- 2026-04-13-white-paper.md (design-level source of truth)
- 2026-04-14-impl-spec-gaps.md (90 gaps identified)
- 2026-04-14-impl-spec-phase-0-1.md (superseded by this)
- 2026-04-14-impl-spec-phase-0-1-addendum.md (superseded by this)

## Open Questions or Ambiguities

- **Phase 0-1 doesn't contradict the harness pattern** — it explicitly defers harnesses to Phase 5.
- Phase 0-1 doesn't discuss where agent execution belongs — that's Phase 2 scope.
- Phase 0-1 explicitly defers the "base UI" including the assistant pattern to Phase 4.
- **The open question is whether Phase 2 spec places agent execution in the kernel or in a harness.** This file itself is consistent with the harness design — it just doesn't implement it.

**Pass 2 observations:**
- **No architectural-layer deviation specific to Phase 0-1.** The spec is faithful to the design artifacts.
- **Phase 0-1 establishes the foundation correctly**: modular monolith with trust boundary, kernel/non-kernel split, CLI-in-API-mode discipline, three kernel processes.
- **The seven kernel entities** (Organization, Actor, Role, Integration, Attention, Runtime, Session) are all defined in Phase 1 per design.
- **Integration adapters deferred to Phase 3** — consistent with design (Integration primitive in Phase 1, adapters in Phase 3).
- **Harness pattern deferred to Phase 5** — consistent with design. This means Phase 2-4 must build things WITHOUT harnesses; the question is how associate execution works in Phase 2 without the harness pattern being ready.
- **The phasing creates a potential architectural risk**: Phase 2 (Associate Execution) comes BEFORE Phase 5 (Real-Time, harness pattern formalized). If Phase 2 implements agent execution without a harness (because harnesses are Phase 5), the natural place to put it is the kernel's Temporal Worker. Which is exactly what Finding 0 describes. The Phase 2 consolidated spec needs to resolve this tension.
