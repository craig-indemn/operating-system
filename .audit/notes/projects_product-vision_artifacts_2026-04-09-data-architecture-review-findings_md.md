# Notes: 2026-04-09-data-architecture-review-findings.md

**File:** projects/product-vision/artifacts/2026-04-09-data-architecture-review-findings.md
**Read:** 2026-04-16 (full file — 249 lines)
**Category:** design-review

## Key Claims

Three reviewers (platform engineering, DevOps, security) attacked "everything is data." **14 findings**:

### CRITICAL (before first external customer):
1. **Org isolation has no defense in depth** — single enforcement point (`get_current_org_id`) is single-miss-catastrophe. Fix: Motor middleware auto-injects org_id + CI cross-tenant isolation tests.
2. **Per-org secrets stored alongside data** — OAuth tokens + carrier API keys in MongoDB Integration entity. Fix: AWS Secrets Manager; entity stores `secret_ref`.
3. **Skill injection via DB modification** — modified skill turns associate into insider threat. Fix: content hashing + version approval + skill write permissions admin/FDE only + content analysis at creation.
4. **Rule action injection (state machine bypass)** — `set-fields` action could set status directly. Fix: whitelist settable fields; EXCLUDE state machine fields from set-fields.

### HIGH:
5. **Sandbox escape vectors unspecified** — no threat model, no sanitization, no isolation. Fix: Daytona config (no outbound network, no env vars, no fs escape, subprocess.run(args_list)).
6. **Changes collection lacks tamper evidence** — compromised admin could delete records. Fix: insert-only permission + SHA-256 hash chain.
7. **Environment isolation is purely logical** — dev/staging/prod as orgs in same DB → one bad query wipes all. Fix: separate Atlas clusters per environment.

### MEDIUM:
8. **Dynamic entity class limitations** — basic types work; relationships need two-pass resolution; index validation at creation; pre/post save hooks via kernel capabilities.
9. **Hot-reload for API server** — three options (lazy-per-request, periodic-poll, raw Motor). Recommendation: raw Motor for dynamic entities, Beanie for bootstrap entities only.
10. **Platform upgrade path for stored configuration** — "most dangerous gap in the everything-is-data model." Fix: capability config schema versioning + migration scripts + dry-run.
11. **Standard entity library bootstrap** — seed YAML + template org.
12. **Schema migration for renames/type changes** — explicit design needed for field rename/removal/type change.
13. **Thundering herd after Temporal recovery** — batching + backpressure.
14. **Queue Processor SPOF** — MVP: single instance + restart monitoring. Scale: leader election or Change Streams.

**MVP infrastructure recommendation**: ~$200/mo (Atlas M10 $60 + Temporal Cloud $100 + Railway $30-50 + S3 $5 + Grafana Cloud free).

## Architectural Decisions

- **OrgScopedCollection wrapper** = defense-in-depth for multi-tenancy (resolved in data-architecture-solutions).
- **AWS Secrets Manager** (not MongoDB) for credentials with `secret_ref` on Integration.
- **Hash chain + insert-only changes collection** = tamper-evident audit.
- **Separate Atlas clusters** for prod vs. non-prod (already in place per infrastructure artifact).
- **Schema migration as first-class capability** (resolved in data-architecture-solutions #12).
- **Raw Motor for dynamic domain entities; Beanie for kernel entities** — this became the dual base class split (`DomainBaseEntity` + `KernelBaseEntity`) surfaced in shakeout Finding 4.

## Layer/Location Specified

- **OrgScopedCollection** = kernel-level wrapper, hidden in kernel init.
- **PlatformCollection** = kernel-level, platform-admin-only.
- **AWS Secrets Manager** = external service.
- **Skill content hash** = on Skill entity.
- **Rule validation at creation** = CLI command handler + kernel rule engine.
- **Daytona sandbox** = external service wrapping agent execution.
- **Changes hash chain** = `kernel/changes/hash_chain.py`.
- **Separate Atlas clusters** = infrastructure config.
- **Dual base class (raw Motor + Beanie)** = kernel entity framework.

**Finding 0 relevance**:
- #5 Sandbox (Daytona) — currently absent per Pass 2, because agent execution is in kernel Temporal worker (no sandbox wrapping). Finding 0 consequence.
- #9 Dual base class — recommended here, implemented during shakeout.

## Dependencies Declared

- AWS Secrets Manager + IAM
- MongoDB Atlas (multiple clusters)
- Daytona (sandbox)
- Motor (raw MongoDB driver)
- Beanie (ODM for kernel entities)

## Code Locations Specified

- OrgScopedCollection class (kernel)
- PlatformCollection class (kernel, platform-admin-only)
- AWS Secrets Manager integration pattern
- `kernel/changes/hash_chain.py` (insert-only + chain)
- `kernel/entity/base.py` (dual base class post-shakeout)

## Cross-References

- 2026-04-09-data-architecture-everything-is-data.md (the design this reviews)
- 2026-04-09-data-architecture-solutions.md (resolves all 14 findings)
- Phase 0-1 consolidated spec (implements most fixes)
- 2026-04-15-shakeout-session-findings.md (Finding 4 — dual base class emerged from #9)
- 2026-04-15-spec-vs-implementation-audit.md (D-01 dual base class)

## Open Questions or Ambiguities

All 14 findings RESOLVED in data-architecture-solutions. Implementation status per Pass 2:
- #1 OrgScopedCollection: implemented (noted in Pass 2).
- #2 AWS Secrets Manager: Integration entity has `secret_ref` field (from Phase 2-3 spec).
- #3 Skill content hashing: implemented (`kernel/skill/integrity.py`).
- #4 Rule action injection: Phase 0-1 spec excludes state fields from set-fields.
- #5 Sandbox: absent (Finding 0 consequence).
- #6 Changes hash chain: implemented but verify is broken (shakeout Finding 14).
- #7 Environment isolation: separate clusters already in place.
- #8 Dynamic entity limitations: handled per design.
- #9 Hot-reload: dual base class solution, implemented during shakeout.
- #10 Platform upgrade: CLI scaffold exists.
- #11 Seed templates: partial (basic seed loading exists).
- #12 Schema migration: implemented (section 1.29 of Phase 0-1 spec).
- #13 Thundering herd: Temporal worker config (from infrastructure artifact).
- #14 Queue Processor HA: deployment platform + monitoring.

**Supersedence note**: All 14 findings SURVIVE. Data-architecture-solutions.md is the resolution artifact.
