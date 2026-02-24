---
ask: "Deep dive into COP-325 Issue 6: Matrix not showing for new evaluation run"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-a
sources:
  - type: github
    description: "indemn-platform-v2/ui/src — EvaluationRunDetail.tsx, FederatedEvaluationRunDetail.tsx, EvaluationMatrix.tsx, utils.ts"
  - type: mongodb
    description: "Dev evaluations DB — run 8970c070, evaluator-configs for agent 676be5cbab56400012077f4a"
  - type: linear
    description: "COP-325 Issue 6"
---

# Issue 6: Matrix Not Showing for New Evaluation

## Feedback (from Dhruv)

The matrix view isn't showing for the new evaluation run.

## Assessment

Dhruv's run `8970c070` (14 items, 5 passed, test set `7be041da`, rubric `6ece933d`).

### Data verification — everything is present

Verified against live dev API:

1. **Run has a rubric**: `rubric_id: 6ece933d`, `rubric_version: 1` — confirmed
2. **Evaluator config exists**: `/evaluator-configs?agent_id=676be5cbab56400012077f4a` returns 4 configs, including one for rubric `6ece933d` with 6 enabled evaluators
3. **Results have V1 scores field populated**: Each result has `scores` with keys matching the evaluator `feedback_key`s (`rule_01_professional_and_userfri`, etc.)
4. **Results also have V2 fields**: `criteria_scores` array and `rubric_scores` array

The previous session's hypothesis about "V1/V2 data format mismatch" is **incorrect** — the backend populates both formats on the same result. The V1 `scores[key]` lookup in `buildMatrixData()` (utils.ts line 121) works because the V1 keys are present.

### Root cause: V2 runs default to "cards" view, not matrix

The rendering code:

```tsx
// EvaluationRunDetail.tsx line 25
const [viewMode, setViewMode] = useState<ViewMode>('cards');
```

For V2 runs (`isV2Run = true`), the component renders:
1. Summary dashboard
2. A view toggle (`Per-Item View` | `Matrix View`)
3. Default: cards view (Per-Item)

For V1 runs (non-V2), the matrix renders **directly** — no toggle, no cards view.

So Dhruv likely opened the run detail, saw the cards view, and expected to see the matrix (like V1 runs show). The view toggle exists but may not be obvious — it's a small segmented control that could be missed.

### Additional risk: evaluator config API failure

If the `/evaluator-configs` API call fails silently (CORS, network, timeout), `evaluatorConfig?.evaluators` would be falsy and clicking "Matrix View" would show: *"Matrix view requires evaluator configuration (rubric)."*

This applies to both standalone (`EvaluationRunDetail.tsx` line 239) and federated (`FederatedEvaluationRunDetail.tsx` line 290).

## Resolution

Two options depending on what Dhruv wants:

### Option A (Recommended): Default to matrix view for V2 runs that have a rubric

```tsx
// EvaluationRunDetail.tsx line 25
// Default to matrix if evaluator config is available
const [viewMode, setViewMode] = useState<ViewMode>('cards');

// After evaluatorConfig loads, switch to matrix if available
useEffect(() => {
  if (evaluatorConfig?.evaluators) {
    setViewMode('matrix');
  }
}, [evaluatorConfig]);
```

Same change in `FederatedEvaluationRunDetail.tsx`.

This gives V2 runs with a rubric the same default experience as V1 runs (matrix first), while runs without a rubric still default to cards.

### Option B: Keep cards as default, make the toggle more prominent

If the per-item cards view is the intended default for V2, make the view toggle more visible — larger buttons, a label, or a hint that "Matrix View" is available.

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `ui/src/pages/EvaluationRunDetail.tsx` | Default to matrix when rubric available | 25 (+ useEffect) |
| `ui/src/federation/components/FederatedEvaluationRunDetail.tsx` | Same | ~28 (+ useEffect) |

## Complexity

Low — add a `useEffect` to switch default view mode when evaluator config loads.

## Linear Response (draft)

> Fixed. V2 evaluation runs now default to Matrix View when a rubric is configured (matching V1 behavior). Runs without a rubric still default to Per-Item View. The view toggle remains available for switching between modes.
