# Notes: 2026-04-14-impl-spec-gaps.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-gaps.md
**Read:** 2026-04-16 (full file — 763 lines)
**Category:** spec-gap-tracking

## Key Claims

- **90 gaps identified across 7 verification passes** of the base (non-consolidated) specs: Phase 0-1 (base + addendum), Phase 2-3, Phase 4-5, Phase 6-7.
- **Verification passes**:
  1. White paper sections (55 gaps)
  2. INDEX.md decisions 160+ (+7)
  3. Internal consistency (+5)
  4. Implementability (+4)
  5. Artifact-specific mechanisms (+10)
  6. Edge cases + ops (+5)
  7. Final sweep (+4)
- **Gaps by phase**: Phase 0-1 → 27, Phase 2-3 → 22, Phase 4-5 → 23, Phase 6-7 → 4, Cross-cutting → 10.
- **All 90 gaps resolved in the consolidated specs** (per 2026-04-14-impl-spec-verification-report.md).

### Gap categories (selected representative examples):

- **Missing function implementations**: `build_event_metadata()`, `evaluate_rules()`, `process_with_associate`, `process_bulk_batch`, `claim_by_id`, `_resolve_target_entity`, `_get_entity_fields`, `_has_any_permission`, `_get_field_metadata`, `_find_state_field`.
- **Missing mechanism specifications**: dynamic entity relationships (circular references), flexible data validation, message-to-log transfer atomicity, watch cache + invalidation, veto rule detection, claim sort order, OAuth token refresh, credential cache invalidation, Attention TTL cleanup, zombie detection, scoped watch→Runtime notification path, three-layer config merge, handoff state consistency.
- **Missing CLI/API surface**: `indemn entity modify/enable/disable/migrate/cleanup`, `indemn org clone/diff/deploy/export/import`, `indemn platform upgrade`, `indemn audit verify`, `indemn bulk status/list/cancel/retry`, `indemn lookup import --from-csv`, `indemn integration rotate-credentials/upgrade`.
- **Missing flow specifications**: HITL via Temporal signals, MFA challenge flow, platform admin session flow, recovery flows (password reset, backup codes), claims refresh on role change.
- **Explicit documentation of decisions**: compliance mode flag (strict_deterministic), bootstrap entity cascade guard, Tier 3 self-service signup scope, default-assistant auth inheritance, bulk_operation_id = temporal_workflow_id, explicit deferred features per phase.

## Architectural Decisions

Notable gap-resolution decisions:
- **EntityDefinition scope**: resolved as per-org with `org_id` field (Option A) — necessary for env-as-org clone.
- **CLI always in API mode** (not direct MongoDB).
- **OrgScopedCollection + contextvars**: organizational scoping via Python `contextvars` set by auth middleware, read by entity operations.
- **Temporal TracingInterceptor for OTEL** — required.
- **Retry policies per activity, not one-size-fits-all** — G-90.
- **Multi-entry-point Dockerfile for kernel image** — G-88.
- **Graceful shutdown for all services** — G-84.

## Layer/Location Specified

Gap resolutions that touch architectural layer:

- **G-21 `process_with_associate` activity implementation**: specified to run as kernel Temporal activity in `kernel/temporal/activities.py`. Calls CLI commands via **HTTP to the API** (not subprocess from inside Temporal worker). **This is where Finding 0 is BAKED INTO THE GAP RESOLUTION.** The spec gap identified that implementation detail was missing; the resolution specified kernel-side implementation. The deviation from the design (harness-based implementation) was not caught.
- **G-22 Context propagation through associate execution**: correlation_id and depth propagate through Temporal activity → HTTP API call → save_tracked() via headers. Correct.
- **G-47 events stream Change Stream pipeline**: kernel-side MongoDB Change Stream filter. Correct.
- **G-59 default assistant auth inheritance**: default assistant authenticates via user's Session JWT. The gap resolution does NOT say "default assistant runs as a harness instance" — it leaves that implementation detail open. **This is how Finding 0b entered the spec.**
- **G-65 harness CLI authentication**: service token injected as env var / CLI flag / config. Implementation detail left open but trusted.
- **G-88 multi-entry-point Dockerfile**: three CMD values for API, queue_processor, temporal_worker — implicitly places Temporal Worker inside `indemn-kernel` image. Consistent with the infrastructure artifact's 5-services structure (vs. design's 6 with async-deepagents harness).

**Finding 0 relevance**:
- **The 90-gap analysis was COMPLETE at the mechanism level but SILENT at the architectural-layer level.**
- Gap resolutions for agent execution (G-21) and default assistant (G-59) both baked the deviation deeper into the specs.
- The gap analysis author was writing to the base/addendum specs (Phase 0-1 base, Phase 2-3, Phase 4-5, Phase 6-7) that already had the deviation. Fixing the gaps did not re-check where the mechanisms should live.
- Pass 2 audit (2026-04-16) identified this methodology limitation and closed it.

## Dependencies Declared

- Pydantic v2 (model_dump)
- Motor + Beanie 1.26+
- Temporal SDK + TracingInterceptor
- argon2-cffi
- jsonschema
- croniter
- Railway + Cloudflare
- Grafana Cloud (OTEL)

## Code Locations Specified

All gap resolutions are path-level references to the consolidated specs' files. Key locations:

- `kernel/entity/base.py` (G-17 `_previous_state`, G-68 OrgScopedCollection, G-71 contextvars)
- `kernel/entity/factory.py` (G-02 dynamic relationships, G-72 flexible data cross-entity schema)
- `kernel/entity/migration.py` (G-13, G-14)
- `kernel/entity/flexible.py` (G-03, G-72)
- `kernel/watch/cache.py` (G-09)
- `kernel/watch/validation.py` (G-18)
- `kernel/watch/evaluator.py` (G-06 older_than operator)
- `kernel/rule/engine.py` (G-07 evaluate_rules, G-08 veto, G-56 compliance mode)
- `kernel/message/emit.py` (G-01 build_event_metadata, G-04 MessageLog, G-05 transfer atomicity)
- `kernel/skill/schema.py` (G-10 Skill entity)
- `kernel/api/registration.py` (G-11 @exposed routes)
- `kernel/api/org_lifecycle.py` (G-14 org commands, G-52 export format)
- `kernel/api/auth_routes.py` (G-35/G-36/G-37/G-38/G-39/G-40 auth flows)
- `kernel/api/direct_invoke.py` (scheduled + real-time activation)
- `kernel/api/bulk.py` (G-24 bulk endpoints)
- `kernel/api/webhook.py` (G-11 webhook endpoint)
- `kernel/temporal/worker.py` (G-19 TracingInterceptor, G-23 production config, G-77 versioning)
- `kernel/temporal/workflows.py` (G-20 HumanReviewWorkflow, G-24 BulkExecuteWorkflow)
- `kernel/temporal/activities.py` (G-21 process_with_associate, G-64 auth context, G-80 process_bulk_batch)
- `kernel/integration/adapter.py` (G-27 error hierarchy, G-31 async correctness)
- `kernel/integration/credentials.py` (G-26 OAuth refresh, G-28 cache invalidation, G-30 migration)
- `kernel/cli/org_commands.py` (G-14)
- `kernel/cli/skill_commands.py` (G-58 skill approval)
- `ui/src/assistant/*` (G-32 field→control mapping, G-34 subscription)
- `Dockerfile` (G-88)
- `docker-compose.yml` (G-89)

## Cross-References

- 2026-04-13-white-paper.md (design source of truth — basis for Pass 1)
- 2026-04-13-simplification-pass.md (simplifications applied)
- 2026-04-13-infrastructure-and-deployment.md (Pass 6 grounding)
- 2026-04-14-impl-spec-phase-0-1 base + addendum (verified)
- 2026-04-14-impl-spec-phase-2-3 base (verified)
- 2026-04-14-impl-spec-phase-4-5 base (verified)
- 2026-04-14-impl-spec-phase-6-7 base (verified)
- 2026-04-14-impl-spec-phase-0-1-consolidated (gap resolutions applied)
- 2026-04-14-impl-spec-phase-2-3-consolidated (gap resolutions applied)
- 2026-04-14-impl-spec-phase-4-5-consolidated (gap resolutions applied)
- 2026-04-14-impl-spec-phase-6-7-consolidated (gap resolutions applied)
- INDEX.md (160+ decisions — Pass 2 grounding)
- 2026-04-14-impl-spec-verification-report.md (confirms all 90 gaps resolved)

## Open Questions or Ambiguities

**Meta-gap**: This 90-gap analysis asked "what mechanisms are missing?" and was thorough. It did NOT ask "are the mechanisms in the right layer?" The Pass 2 audit (2026-04-16) explicitly called this out as the methodology gap. This file is PROOF of the gap:
- 90 gaps about WHAT needs to exist
- ZERO gaps about WHERE the existing mechanisms should live

**Supersedence note**:
- All 90 gap resolutions SURVIVE. They're correct at the mechanism level.
- None of them are superseded; all are integrated into the consolidated specs.
- **The methodology of this gap analysis is what's superseded** — Pass 2 demonstrated that layer-level verification was needed on top.

**Vision-map implication**: The consolidated specs have 90 correctly-resolved mechanism gaps + 2 un-caught architectural-layer deviations (Finding 0 + 0b). The gap analysis verified mechanisms; Pass 2 verified layers. Both are needed for the full picture.
