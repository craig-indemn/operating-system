---
ask: "Deep dive into COP-325 Issue 7: Test set not showing in run detail view"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-b
sources:
  - type: github
    description: "indemn-platform-v2/ui/src — FederatedEvaluationRunDetail.tsx lines 39, 59-68, 207-212; EvaluationsPanel.tsx lines 316-331 (correct pattern)"
  - type: mongodb
    description: "Dev evaluations DB — all 6 Wedding Bot runs have question_set_id=None, test_set_id=populated"
---

# Issue 7: Test Set Not Showing in Run Detail View

## Feedback (from Dhruv)

The test set isn't displayed on the evaluation run detail page.

## Assessment

The federated run detail view (`FederatedEvaluationRunDetail.tsx`) shows "—" for the test set on **every run**, not just one.

### Root cause: V1 field lookup on V2 data

Line 39 fetches V1 question sets:
```tsx
const { data: questionSets } = useQuestionSets(botId);
```

Lines 60-68 look up the test source using V1 `question_set_id`:
```tsx
const getQuestionSetLabel = () => {
  if (!run?.question_set_id) return null;  // Always null for V2 runs
  const qs = questionSets?.find(q => q.question_set_id === run.question_set_id);
  ...
};
```

All V2 runs have `question_set_id: null` and `test_set_id: populated`. Verified across all 6 Wedding Bot runs in the database — every one has `question_set_id=None`.

### The correct pattern already exists

`EvaluationsPanel.tsx` (the runs list) handles this correctly at lines 327-331:

```tsx
const getTestSourceLabel = (run: EvaluationRun): string => {
  if (run.test_set_id) return getTestSetLabel(run);
  return getQuestionSetLabel(run);
};
```

It prefers `test_set_id` (V2), falls back to `question_set_id` (V1). The detail page just never adopted this pattern.

`EvaluationSection.tsx` (agent overview) also handles both (lines 56-62).

## Resolution

### FederatedEvaluationRunDetail.tsx

1. **Import `useTestSets` hook** (line 16) — already exported from `useEvaluations.ts` line 674.

2. **Fetch test sets** (add after line 39):
```tsx
const { data: testSets } = useTestSets(botId);
```

3. **Add V2 test set lookup** (add after `getQuestionSetLabel`):
```tsx
const getTestSetLabel = () => {
  if (!run?.test_set_id) return null;
  const ts = testSets?.find(t => t.test_set_id === run.test_set_id);
  const version = run.test_set_version ? `v${run.test_set_version}` : '';
  if (ts) {
    return { name: ts.name, version };
  }
  return { name: '(Deleted)', version };
};
```

4. **Prefer test set over question set** (update line 71):
```tsx
const testSourceLabel = getTestSetLabel() || getQuestionSetLabel();
```

5. **Update rendering** (lines 207-212): replace `questionSetLabel` with `testSourceLabel`:
```tsx
<span className="text-muted">{run?.test_set_id ? 'Test Set' : 'Question Set'}</span>
<p title={testSourceLabel ? `${testSourceLabel.name} ${testSourceLabel.version}` : '--'}>
  {testSourceLabel ? `${testSourceLabel.name} ${testSourceLabel.version}` : '--'}
</p>
```

### EvaluationRunDetail.tsx (standalone)

The standalone detail page doesn't show test set or rubric at all (only Run ID, Agent ID, Progress, Test Items). No change needed here — Issue 5 is already removing Run ID and Agent ID, but adding test set/rubric to standalone is out of scope for this issue.

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `ui/src/federation/components/FederatedEvaluationRunDetail.tsx` | Add `useTestSets` hook, add `getTestSetLabel()`, prefer V2 test set over V1 question set | 16, 39, 68-76, 71, 207-212 |

## Complexity

Low — follow the existing pattern from `EvaluationsPanel.tsx`. Add a hook call and a lookup function.

## Linear Response (draft)

> Fixed. The run detail view now correctly displays the test set name for V2 evaluation runs. Previously it only checked the V1 `question_set_id` field (always null for V2 runs), causing "—" to show for every run. Now it checks `test_set_id` first (V2), falling back to `question_set_id` (V1) — matching the pattern already used in the runs list.
