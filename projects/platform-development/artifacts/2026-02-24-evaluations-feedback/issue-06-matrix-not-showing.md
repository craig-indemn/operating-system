---
ask: "Deep dive into COP-325 Issue 6: Matrix not showing for new evaluation run"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-b
sources:
  - type: github
    description: "evaluations/src/indemn_evals/api/routes/evaluations.py — V2 trigger endpoint, scope filter logic lines 632-648, run creation lines 786-806"
  - type: mongodb
    description: "Dev evaluations DB — run 7c5ce17d (rubric_rules_passed=0, rubric_rules_total=0), rubric 6ece933d (6 rules, all prompt/general scope)"
  - type: linear
    description: "COP-325 Issue 6"
---

# Issue 6: Matrix Not Showing — Scope Filter Silently Eliminates All Rubric Rules

## Feedback (from Dhruv)

The matrix view isn't showing for the new evaluation run.

## Assessment

Investigated run `7c5ce17d` (15 items, 14 passed, rubric `6ece933d`, test set `3e3c1f7c`).

### What we see in the UI

- Rubric shows "Wedding Bot Rubric v1" — present
- Matrix renders but every cell is a dash, every compliance row is 0%
- The matrix IS visible (the view toggle works), but the scores are empty

### Data from API

```
GET /api/v1/runs/7c5ce17d-cf2a-4c1b-9552-3fab2425175d

rubric_id: 6ece933d-0f8b-4020-ab52-987dc0c4d0ad
rubric_version: 1
component_scope_filter: "function"
rubric_rules_passed: 0
rubric_rules_total: 0
criteria_passed: 41
criteria_total: 42
```

Individual results confirm: `rubric_scores: null`, `rubric_passed: null`. Only `criteria_scores` is populated. The rubric evaluator never ran.

### Root cause: component_scope filter eliminated all rules

The rubric has 6 rules:

| Rule | component_scope |
|------|----------------|
| Professional and User-Friendly Tone | prompt |
| No Fabrication or Assumption | prompt |
| Stays Within Wedding Insurance Scope | prompt |
| No Harmful or Inappropriate Content | general |
| Response Clarity and Coherence | general |
| Empathetic and Persistent Information Collection | prompt |

The run was triggered with `component_scope: "function"`. The filter in `evaluations.py` lines 633-637:

```python
rules = [r for r in rules if (
    r.get("component_scope") == body.component_scope or
    r.get("component_scope") is None
)]
```

This keeps rules where scope is `"function"` or `None`. All 6 rules are `"prompt"` or `"general"` — none match. `rules` becomes empty, `evaluator_config` stays `None`, and no rubric evaluators are built.

**But `rubric_id` is still written to the run** (line 795: `rubric_id=body.rubric_id`). So the UI shows a rubric is attached, but there are no scores — a misleading state.

### The bug

The backend allows a run to be created with a `rubric_id` even when the scope filter eliminates all of that rubric's rules. The run appears to have a rubric (UI shows it, matrix renders), but rubric evaluation never executed (all dashes, 0%).

## Resolution

If the scope filter eliminates all rubric rules, proceed as criteria-only **without attaching the rubric to the run**.

### Backend fix — `evaluations/src/indemn_evals/api/routes/evaluations.py`

After the scope filter (line 646), check if rules survived. If not, clear the rubric reference so the run accurately reflects what was evaluated:

```python
# Line 646 (after existing scope filters)
rules_count = len(rules)

# If scope filter eliminated all rules, treat as criteria-only run
if not rules:
    # Don't attach rubric — no rules survived the scope filter
    body.rubric_id = None
```

This ensures:
- `rubric_id` on the run is `None` → UI correctly shows no rubric
- `rubric_version` on the run is `None` (line 796: `rubric_version=rubric_version if body.rubric_id else None`)
- No evaluator config is created (line 699: `if evaluator_config:` stays falsy)
- Matrix view shows "no rubric" instead of misleading empty scores
- Criteria evaluation still runs normally

### Frontend — no changes needed

If the backend correctly omits `rubric_id` when no rules survive, the UI already handles criteria-only runs correctly (no matrix, no rubric label).

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `evaluations/src/indemn_evals/api/routes/evaluations.py` | Clear rubric_id when scope filter eliminates all rules | After line 646 |

## Complexity

Low — add a 2-line guard after the existing scope filter.

## Linear Response (draft)

> Fixed. When the component scope filter eliminates all rubric rules, the run now proceeds as criteria-only without attaching the rubric. Previously, the rubric was recorded on the run even though no rules were evaluated, causing the matrix to show all empty scores. Now the UI accurately reflects what was evaluated.
