# Notes: 2026-04-09-data-architecture-solutions.md

**File:** projects/product-vision/artifacts/2026-04-09-data-architecture-solutions.md
**Read:** 2026-04-16 (full file — 265 lines)
**Category:** design-source

## Key Claims

- **OrgScopedCollection wrapper** — all application code touches MongoDB through a wrapper that ALWAYS injects `org_id`. Raw Motor is hidden in kernel init. Developers CAN'T write an unscoped query. Cross-org queries use a separate **`PlatformCollection`** accessor, available only to platform-admin role.
- **Per-org secrets via AWS Secrets Manager.** Integration entities store `secret_ref`, NEVER actual credentials. Entity framework never sees secrets.
- **Skill security via content hashing + version approval.** `indemn skill update` creates new version in `pending_review`; old version active until approved. On load: hash verified; direct DB modification breaks hash → skill rejected. Associates can NEVER modify skills (admin/FDE only).
- **Rule-action validation at creation time**: `indemn rule create` validates fields exist, role has write permission, and **state-machine fields (status, stage) are REJECTED** — state transitions must use `transition_to()`.
- **Sandbox = Daytona configuration**: no outbound network except via `indemn` CLI; no env vars; no fs outside `/workspace`; no shell metacharacters (`subprocess.run(args_list)`, never `shell=True`); resource limits per associate.
- **Audit trail = append-only + hash chain.** MongoDB app user has `insert` only on `changes`; no update, no delete. Each change record has `previous_hash` (SHA-256 of previous). `indemn audit verify` detects tampering.
- **Environment isolation**: already solved by separate dev/prod Atlas clusters. Deploy command reads staging, writes prod.
- **Dynamic entity class limitations — accept and design around.** Two-pass resolution for circular relationships; validate index field names at entity creation; kernel capabilities provide hooks; `map_from` for simple computed fields; no IDE autocomplete / static type-checking (accepted).
- **API Server entity resolution**: **Beanie for EVERYTHING**. Entity definitions load from DB at startup; entity type creation triggers automated rolling restart. No lazy loading, no Motor/Beanie split.
- **Platform upgrade** = capability schema versioning + migration scripts.
- **Standard library** = seed YAML in codebase (`seed/entities/*.yaml`, `seed/skills/*.md`, `seed/roles/*.yaml`). `indemn platform init` creates `_template` org from seed. `indemn org create --from-template standard` clones.
- **Schema migration — FIRST-CLASS capability**: add-field (no migration), deprecate-field (background cleanup), rename-field (batched `$rename` with alias window), convert-field (batched transform with union window). All idempotent, dry-runnable, batched, auditable, rollbackable.
- **Thundering herd** = Temporal Worker config (`max_concurrent_activities`, retry policies, task queue rate limiting). No custom batching needed.
- **Queue Processor HA** = deployment platform (Railway/ECS auto-restart, health checks, optionally leader election at scale).

## Architectural Decisions

- **Single MongoDB access pattern (OrgScopedCollection)** becomes a kernel invariant. All entity CRUD goes through it. Violation is a bug at kernel level.
- **Credentials never flow through entity-framework layers** — kernel adapter code resolves them separately, on demand.
- **Schema changes are an administrative operation**; rolling restart is acceptable (seconds).
- **Rule actions are bounded** — no side-effects beyond field writes through the set-fields action; no state transitions.
- **Tamper evidence via MongoDB permissions + hash chain** — dual defense-in-depth.
- **Accept dynamic-class ergonomic tradeoffs** (no IDE autocomplete) — CLI/skills are the interface, not in-code instantiation.

## Layer/Location Specified

- **OrgScopedCollection** = kernel-level Python class, wraps Motor collection. Hidden in kernel init.
- **PlatformCollection** = kernel-level Python class, only accessible to platform-admin.
- **AWS Secrets Manager** = external service. Credentials live there; kernel adapter code reads via `secret_ref`.
- **Skill storage** = MongoDB + content hash. Updates via CLI file push. Direct DB modification caught.
- **Rule validation** = CLI-time in `indemn rule create` command handler.
- **Daytona** = external sandbox service. Wraps agent execution. PER DESIGN the agent runs inside Daytona — THIS IS RELEVANT TO FINDING 0 (the current implementation has no sandbox because agent execution is in the kernel Temporal worker, not in a harness that wraps it with Daytona).
- **Changes collection** = MongoDB. Insert-only permission on app user. Hash chain verified via `indemn audit verify`.
- **Seed files** = codebase (`seed/entities/`, `seed/skills/`, `seed/roles/`). `_template` org auto-created at platform init.
- **Migration machinery** = `indemn entity migrate ...` CLI command. Implementation kernel-side.
- **Temporal Worker** = referenced as existing infrastructure. This file does NOT specify worker location (in-kernel vs harness) — consistent with the April 9 open question.

## Dependencies Declared

- Motor + Beanie + Pydantic (MongoDB driver stack)
- AWS Secrets Manager
- **Daytona** (sandbox) — explicit
- Railway / ECS (deployment platform, for auto-restart)
- Temporal Worker SDK config (max_concurrent_activities, retry policies)
- CLI (Typer)
- Atlas (separate dev/prod clusters)

## Code Locations Specified

- Conceptual:
  - `OrgScopedCollection` class
  - `PlatformCollection` class
  - Integration entity's `secret_ref` field
  - Skills with content hash + version
  - Changes collection with `previous_hash`
  - `seed/entities/*.yaml`, `seed/skills/*.md`, `seed/roles/*.yaml`
- Implementation mapping (from code read in Pass 2):
  - Pass 2 noted OrgScopedCollection / PlatformCollection in `kernel/scoping/` (inferred; not yet audited directly).
  - Changes hash chain in `kernel/changes/hash_chain.py` (Pass 2 noted hash-chain verification issue unresolved).

## Cross-References

- 2026-04-09-data-architecture-review-findings.md (the 14 findings this artifact resolves — Tier B)
- 2026-04-09-data-architecture-everything-is-data.md (same day, complementary — "everything is data")
- Phase 0-1 consolidated spec (implements OrgScopedCollection + changes collection + seed files)
- Phase 2-3 consolidated spec (Temporal Worker config)
- white-paper (integrates all these as the implemented architecture)

## Open Questions or Ambiguities

- **Skill version approval workflow** — per-org opt-in; not specified in detail (admin role approves). Left for implementation.
- **Capability schema versioning migration scripts** — the pattern is stated; actual migration-script format/location left for implementation.
- **Daytona deployment model** — external service; integration pattern not detailed here (tied to the harness pattern specified later).
- **Where OrgScopedCollection is instantiated** — per-request or per-connection? Implementation detail.

**Finding 0 relevance**:
- **Daytona sandbox is absent in current implementation** — consequence of Finding 0 (agent execution in kernel Temporal worker has no sandbox wrapping).
- **AWS Secrets Manager for credentials** — Phase 2-3 spec said credentials live in AWS Secrets Manager per `secret_ref`. Need to verify in Pass 4 code audit whether adapters actually use Secrets Manager.
- **Hash chain verification** is flagged in Pass 2 as unresolved — `kernel/changes/hash_chain.py` has serialization mismatch.

**Supersedence note for vision map**: All 14 solutions survive. Data architecture is the foundation for Phase 0-1 — there's no later artifact that supersedes these solutions at the architectural level.
