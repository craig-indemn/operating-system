---
ask: "Deep dive into COP-325 Issue 10: Two different scores (98% vs 93%)"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-b
sources:
  - type: github
    description: "indemn-platform-v2/ui/src/lib/scoring.ts lines 85-99 — rubric score fallback logic"
  - type: mongodb
    description: "Dev evaluations DB — run 7c5ce17d has rubric_rules_total=0 but component_scores.general={passed:14, total:15}"
---

# Issue 10: Two Different Scores (98% vs 93%)

## Feedback (from Dhruv)

Two different percentages displayed — what do they mean?

## Assessment

On run `7c5ce17d` the UI shows:
- **98%** criteria score (41/42 criteria passed) — correct
- **93%** rubric score (14/15) — **wrong**, this run has no rubric scores

### Root cause: scoring fallback misinterprets component_scores

`scoring.ts` lines 85-99:

```tsx
if (run.rubric_rules_total !== undefined && run.rubric_rules_total > 0) {
  rubricRulesPassed = run.rubric_rules_passed ?? 0;
  rubricRulesTotal = run.rubric_rules_total;
} else {
  // Fallback for old runs: component_scores sum
  const cs = run.component_scores;
  if (cs) {
    const sums = sumComponentScores(cs);
    rubricRulesPassed = sums.passed;
    rubricRulesTotal = sums.total;
  } else {
    rubricRulesPassed = 0;
    rubricRulesTotal = 0;
  }
}
```

Run `7c5ce17d` has:
- `rubric_rules_total: 0` → fails the `> 0` check
- `component_scores: { general: { passed: 14, total: 15 } }` → fallback reads this as rubric data

But `component_scores` on this run is **item-level pass/fail** (14/15 items passed), not rubric rule scores. The fallback was designed for old runs that don't have `rubric_rules_total` at all — it shouldn't activate when the field exists but is zero.

### The distinction

- `rubric_rules_total: 0` means "this run had no rubric evaluation" (new run, field exists)
- `rubric_rules_total: undefined` means "this is an old run before we added this field" (fallback needed)

The current code treats both the same way.

## Resolution

### scoring.ts — fix the fallback condition

The fallback should only activate when the new fields don't exist at all (old runs), not when they exist and are zero:

```tsx
// Check if the new rubric fields exist on the run (even if zero)
const hasNewRubricFields = run.rubric_rules_total !== undefined;

if (hasNewRubricFields) {
  // New run: use the actual values (may be 0/0 for criteria-only runs)
  rubricRulesPassed = run.rubric_rules_passed ?? 0;
  rubricRulesTotal = run.rubric_rules_total ?? 0;
} else {
  // Old run: fall back to component_scores
  const cs = run.component_scores;
  if (cs) {
    const sums = sumComponentScores(cs);
    rubricRulesPassed = sums.passed;
    rubricRulesTotal = sums.total;
  } else {
    rubricRulesPassed = 0;
    rubricRulesTotal = 0;
  }
}
```

With this fix, run `7c5ce17d` (rubric_rules_total=0) returns `rubricRate: null`, and the UI correctly shows no rubric score.

Old runs without the field still fall back to component_scores as before.

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `ui/src/lib/scoring.ts` | Fix rubric fallback — distinguish "field is zero" from "field doesn't exist" | 85-99 |

## Complexity

Low — change one conditional check.

## Linear Response (draft)

> Fixed. The two percentages are Criteria Score (per-item success criteria) and Rubric Score (universal quality rules). The bug was that criteria-only runs (no rubric) were incorrectly showing a rubric score by misinterpreting item-level component data as rubric data. Criteria-only runs now correctly show only the criteria score.
