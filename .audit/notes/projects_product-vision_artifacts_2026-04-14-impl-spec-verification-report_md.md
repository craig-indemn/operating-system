# Notes: 2026-04-14-impl-spec-verification-report.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-verification-report.md
**Read:** 2026-04-16 (full file — 455 lines)
**Category:** spec-verification

## Key Claims

- **4-pass verification** of all 4 consolidated implementation specs against: white paper (937 lines), INDEX.md (447 lines, 160+ locked decisions), all 65+ design artifacts, gap identification (90 gaps across 7 passes), session checkpoints, adversarial reviews.
- **29 total findings resolved in the specs** across 4 passes.
- **Overall assessment**: "These specifications are architecturally sound and comprehensive. [...] The specifications are ready to build from."

### Findings by category:

**Critical (resolved)**:
- C-1: Duplicate `$or` in claim query → fixed with `$and` wrapping
- C-2: `entity.dict()` → `model_dump()` (Pydantic v2 compat)
- S-6: `_should_emit` priority reordered (creation > transition > method)
- B-4: `check_permission` implemented with wildcard + per-request caching
- F-1: EntityDefinition scope resolved as per-org (Option A), `org_id` field added + index `(org_id, name)`

**Important (resolved)**:
- M-1: Schema migration implementation added as section 1.29
- M-2: CLI auto-registration added as section 1.30
- M-6: `indemn org clone/diff/deploy` added as section 1.31
- C-3: Literal with runtime enums → str + __init__ validation (more robust)
- B-5: WebSocket handler registration via `add_api_websocket_route`

**Nice-to-have (resolved)**:
- M-3: Skill approval workflow — section 1.33
- M-4: `indemn audit verify` — section 1.32
- M-5: Seed template via org clone
- M-7: Cascade viewer (API + UI)
- M-8: Credential rotation — section 1.34

**Second-pass findings (R-1 through R-5)**: helper functions filled in (claim_by_id, _resolve_target_entity, _get_entity_fields, _has_any_permission, _get_field_metadata, save_tracked returns created_messages).

**Third-pass findings (T-1 through T-7)**:
- T-1 **CRITICAL**: Kernel entity namespace collision — Phase 6 CRM's domain entity named "Organization" collides with kernel entity. Fixed by renaming CRM entity to "Company" + adding guard in init_database.
- T-2: async/sync mismatch in `_resolve_target_entity` → fixed as async.
- T-3: `_find_state_field` priority → uses `is_state_field` flag, not field name.
- T-4: save_tracked return value propagated in BaseEntity wrapper.
- T-5: Scheduled message role_id vs role_name → lookup name by id.
- T-6: Auth helper functions documented or implemented.
- T-7: Missing imports fixed.

**Fourth-pass findings (P4-1, P4-2)**: missing `jsonschema` and `croniter` in pyproject.toml; two narrative "Organization" references after rename.

## Architectural Decisions

- **Per-org EntityDefinition**: `org_id` on EntityDefinition; `init_database` merges definitions across orgs for class creation. Rejected "system-scoped definitions" in favor of clone-compatible per-org.
- **Kernel entity namespace is reserved**: `init_database` guards against domain entity names matching kernel entity names.
- **CLI auto-registered from entity metadata** via same pattern as API registration.
- **Org clone/diff/deploy are Phase 1 capabilities**, not deferred to Phase 6.
- **`save_tracked` returns created_messages** for optimistic dispatch to consume.

## Layer/Location Specified

- **EntityDefinition**: MongoDB, per-org scoped with index `(org_id, name)`.
- **Schema migration** (section 1.29): `kernel/entity/migration.py`. CLI commands + batching + dry-run.
- **CLI auto-registration** (section 1.30): `kernel/cli/registration.py` — mirrors API registration; uses CLIClient HTTP client; supports table/JSON output.
- **Org clone/diff/deploy** (section 1.31): `kernel/api/org_lifecycle.py` + `kernel/cli/org_commands.py`. Clone copies config not instances; diff shows per-category; deploy supports dry-run.
- **Audit verify** (section 1.32): `kernel/changes/` + CLI.
- **Skill approval workflow** (section 1.33): Skill status `pending_review` + approve endpoints.
- **Credential rotation** (section 1.34): Provider-specific rotation + cache invalidation + audit.

**Finding 0 relevance — METHODOLOGY GAP**:

The verification report exhaustively verified specs against:
- White paper ✓
- INDEX.md ✓
- Design artifacts (for mechanism completeness) ✓
- Session checkpoints ✓
- Gap identification ✓
- Adversarial reviews ✓

**But it did NOT verify**:
- Where agent execution runs at the architectural-layer level
- Whether harness images are separately deployable
- Whether kernel Temporal Worker handles only kernel workflows or also associate workflows
- Trust-boundary placement of `anthropic` library imports
- Task queue topology (single `indemn-kernel` vs per-Runtime queues)

**This is the methodology gap** that the 2026-04-15 comprehensive audit called out and the 2026-04-16 Pass 2 audit closed. The verification report was thorough at the field/mechanism level but did not ask "where does this live?" at the architectural layer.

## Dependencies Declared

- Pydantic v2 (compatibility fix via `model_dump`)
- argon2-cffi (proper import path)
- jsonschema (flexible entity validation)
- croniter (scheduled associate cron evaluation)
- Motor + Beanie 1.26+ (MongoDB async driver)
- Temporal SDK
- FastAPI (with `add_api_websocket_route`)
- Typer (CLI)

## Code Locations Specified

- `kernel/entity/migration.py` (added section 1.29)
- `kernel/cli/registration.py` (section 1.30)
- `kernel/api/org_lifecycle.py` + `kernel/cli/org_commands.py` (section 1.31)
- `kernel/api/bulk.py`
- `kernel/changes/hash_chain.py` + `indemn audit verify` (section 1.32)
- `kernel/cli/skill_commands.py` (section 1.33 approval)
- `kernel/integration/rotation.py` (section 1.34)
- `kernel/auth/middleware.py` (check_permission now implemented)
- `kernel/entity/base.py::save_tracked_impl` (returns `created_messages`)
- `kernel/entity/factory.py::_resolve_target_entity` (async, guarded for kernel names)

## Cross-References

- 2026-04-13-white-paper.md (design source of truth — 937 lines)
- 2026-04-13-simplification-pass.md (correctly reflected in specs)
- 2026-04-13-infrastructure-and-deployment.md (5 services / trust boundary)
- 2026-04-14-impl-spec-gaps.md (90-gap identification this verification addresses)
- All 4 consolidated specs (phase-0-1, phase-2-3, phase-4-5, phase-6-7)
- INDEX.md (160+ locked decisions)
- 2026-04-15-comprehensive-audit.md (called out the methodology gap this verification missed)
- 2026-04-16-pass-2-audit.md (closed the gap, confirmed Finding 0)

## Open Questions or Ambiguities

**The verification report confidently says specs are ready to build.** It does NOT identify Finding 0 (agent execution in wrong layer). Why?

- The report checked white-paper mechanism completeness, not architectural-layer placement.
- The report checked spec internal consistency, not spec-vs-design-artifact at layer level.
- The report validated 90+ gap resolutions, but the gaps were all mechanism-level, not layer-level.

**This artifact is the primary example of the methodology gap that motivated Pass 2.** The verification was genuine and thorough, but it took the consolidated specs as its architectural authority and checked implementation inside the spec's self-consistency. It did not step out to the source design artifacts (realtime-architecture-design, integration-as-primitive, infrastructure-and-deployment, white paper) to ask "are these specs in the right architectural layer?"

**Supersedence note for vision map**:
- All 29 verification findings SURVIVE as spec corrections.
- This artifact itself is NOT superseded — it's a verification checkpoint.
- But its "specs are ready to build from" conclusion is **qualified** by Finding 0: the specs are ready at the field/mechanism level but deviate at the architectural-layer level for agent execution and the assistant.
- The Phase 2-3 spec §2.4 and Phase 4-5 spec §4.7 Finding 0 issues exist IN the verified specs and were NOT flagged by this verification.

**Recommendation**: the vision map should treat this artifact as the "spec internal consistency" reference; the Pass 2 audit is the "spec vs source design at layer level" reference. Both are needed.
