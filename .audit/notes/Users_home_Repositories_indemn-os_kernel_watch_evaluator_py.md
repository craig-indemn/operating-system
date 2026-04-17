# Notes: /Users/home/Repositories/indemn-os/kernel/watch/evaluator.py

**File:** /Users/home/Repositories/indemn-os/kernel/watch/evaluator.py
**Read:** 2026-04-16 (full file — 95 lines)
**Category:** code

## Key Claims

- Module docstring: "Condition evaluator — the single condition language. Shared by watches and rules. One evaluator, one syntax, one debugging surface. JSON format with field comparisons and logical composition (all, any, not)."
- `evaluate_condition(condition, entity_data)` — recursive evaluator.
- Supports logical composition: `all`, `any`, `not`.
- Supports 15 operators: equals, not_equals, contains, not_contains, starts_with, ends_with, gt, gte, lt, lte, in, not_in, matches, exists, older_than, within.
- Nested field access via dot notation (`_get_nested_field`).
- Duration string parsing for `older_than` / `within` (e.g., "7d", "30m", "24h", "60s").

## Architectural Decisions

- Single JSON condition language for watches and rules (per design).
- Pure function — no I/O, deterministic.
- Operator dispatch via dict lookup.
- Strict operator set — unknown operators raise ValueError.
- Timezone-aware datetime handling in `older_than`.

## Layer/Location Specified

- Kernel code: `kernel/watch/evaluator.py`.
- Pure module — no external dependencies beyond stdlib.
- Used by watches during emission (in `kernel/message/emit.py`) and by rules (`kernel/rule/engine.py`).

**No layer deviation.** Correct location.

## Dependencies Declared

- `re` (for matches operator)
- `datetime`, `timedelta`, `timezone`
- `typing.Any`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/watch/evaluator.py`
- Callers:
  - `kernel/message/emit.py` (watch condition evaluation)
  - `kernel/rule/engine.py` (rule condition evaluation)
  - `kernel/temporal/activities.py::_execute_deterministic` (skill condition evaluation)

## Cross-References

- Design: 2026-04-13-white-paper.md § Watches (single condition language)
- Phase 1 spec §1.15 Condition Evaluator
- 2026-04-10-realtime-architecture-design.md (watches + scoping)

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- All 15 operators from the design present — matches comprehensive audit's "COMPLETE" status.
- Dot-notation nested field access enables conditions like `{"field": "submission.organization.primary_owner_id", ...}`.
- Timezone handling is defensive: adjusts now() to naive if actual datetime is naive.
- `contains` uses string conversion — may not handle arbitrary objects cleanly but works for expected types.

Pure, correctly-placed evaluator. No architectural concerns.
