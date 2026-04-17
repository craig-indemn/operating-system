# Notes: 2026-04-14-impl-spec-phase-0-1.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-0-1.md
**Read:** 2026-04-16 (sampled opening + repo structure; 1518 lines total. SUPERSEDED by 2026-04-14-impl-spec-phase-0-1-consolidated.md)
**Category:** spec-superseded

## Key Claims

Base Phase 0+1 implementation spec. **SUPERSEDED** by the consolidated spec (which integrates this base + the addendum + gap resolutions).

Key content:
- **Phase 0** = Development Foundation: repository structure, conventions, environment, CI/CD, deploy config.
- **Phase 1** = Kernel Framework: entity + message + watch + rule + capability + auth middleware + Session + 7 kernel entities.
- **Repository structure**: `indemn-os/` with `kernel/`, `seed/`, `harnesses/`, `ui/`, `tests/`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `CLAUDE.md`.
- **Kernel modules**: entity (base/definition/factory/state_machine/computed/flexible), message (schema/queue/emit), watch (evaluator/cache/scope), rule (schema/engine/lookup), capability, auth, api, cli, temporal, queue_processor.
- **First key architecture decisions** that evolved per the 90-gap analysis + consolidated spec:
  - Entity definitions in MongoDB (not Python files)
  - Dynamic class creation via `create_model`
  - 7 kernel entities (Organization, Actor, Role, Integration, Attention, Runtime, Session)
  - `save_tracked()` atomic transaction
  - `OrgScopedCollection` wrapper

## Architectural Decisions

All decisions here SURVIVE into the consolidated spec, with additions from the addendum (Attention, Runtime, Session kernel entity full specs) and gap resolutions (90 items: schema migration, CLI auto-registration, org clone/diff/deploy, etc.).

## Layer/Location Specified

Same as consolidated — see notes for `2026-04-14-impl-spec-phase-0-1-consolidated.md`. This base spec is the precursor.

**Finding 0 relevance**: Phase 0-1 has no Finding 0 issue. `kernel/temporal/client.py` is a stub here; actual agent execution comes in Phase 2-3 (where Finding 0 enters).

## Dependencies Declared

See consolidated spec note for comprehensive list. Same dependencies.

## Code Locations Specified

Same as consolidated spec — this is the base layout for `kernel/` modules. Addendum adds Attention + Runtime + Session schemas; consolidated spec adds gap resolutions.

## Cross-References

- 2026-04-13-white-paper.md (design source of truth)
- 2026-04-14-impl-spec-phase-0-1-addendum.md (companion — Attention/Runtime/Session + migration/rotation/approval mechanisms)
- 2026-04-14-impl-spec-phase-0-1-consolidated.md (SUPERSEDES this — integrates base + addendum + gap resolutions)
- 2026-04-14-impl-spec-gaps.md (90 gaps identified in this base spec)
- 2026-04-14-impl-spec-verification-report.md (verification against consolidated spec)

## Open Questions or Ambiguities

Everything from the base spec either:
- SURVIVES in the consolidated spec (all architecture decisions)
- Was addressed by the addendum (Attention, Runtime, Session full specs, schema migration, rule validation, etc.)
- Was resolved via the 90-gap analysis and added to the consolidated spec (CLI auto-registration, org lifecycle, audit verify, skill approval, credential rotation).

**Supersedence note**: This base spec is SUPERSEDED by the consolidated spec. For all analysis purposes, use the consolidated spec note as the authoritative reference.
