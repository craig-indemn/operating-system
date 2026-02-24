---
ask: "Deep dive into COP-325 Issue 5: Remove internal IDs from evaluation run detail"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-a
sources:
  - type: github
    description: "indemn-platform-v2/ui/src — EvaluationRunDetail.tsx lines 152-169, FederatedEvaluationRunDetail.tsx lines 162, 194-222"
  - type: linear
    description: "COP-325 Issue 5"
---

# Issue 5: Remove Internal Metadata (Run ID, Agent ID) from Run Detail

## Feedback (from Dhruv)

Internal IDs (Run ID, Agent ID) shouldn't be shown to end users.

## Assessment

Both the standalone and federated run detail pages display a metadata grid with internal IDs:

### Standalone — `EvaluationRunDetail.tsx` lines 152-169

```tsx
<div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
  <div>
    <span className="text-muted">Run ID</span>
    <p className="font-mono">{run.run_id.slice(0, 8)}...</p>
  </div>
  <div>
    <span className="text-muted">Agent ID</span>
    <p className="font-mono">{run.agent_id}</p>
  </div>
  <div>
    <span className="text-muted">Progress</span>
    <p>{run.completed}/{run.total} evaluated</p>
  </div>
  <div>
    <span className="text-muted">Test Items</span>
    <p>{run.total} {isV2Run ? 'items' : 'questions'}</p>
  </div>
</div>
```

### Federated — `FederatedEvaluationRunDetail.tsx` lines 194-222

Same structure but with 6 columns: Run ID, Agent ID, Rubric, Test Set, Progress, Test Items. Also has the run ID in the ExpandablePanel subtitle (line 162):
```tsx
subtitle={`Run ${runId?.slice(0, 8)}...`}
```

**What to remove:** Run ID, Agent ID — these are MongoDB ObjectIDs / UUIDs with no meaning to end users.

**What to keep:** Progress, Test Items, Rubric, Test Set — these provide useful context about the evaluation run.

## Resolution

### 1. EvaluationRunDetail.tsx — remove Run ID and Agent ID

Replace lines 152-169:
```tsx
{run && (
  <div className="grid grid-cols-2 gap-4 text-sm">
    <div>
      <span className="text-muted">Progress</span>
      <p>{run.completed}/{run.total} evaluated</p>
    </div>
    <div>
      <span className="text-muted">Test Items</span>
      <p>{run.total} {isV2Run ? 'items' : 'questions'}</p>
    </div>
  </div>
)}
```

Grid changes from `grid-cols-4` to `grid-cols-2` since we're removing 2 of the 4 items.

### 2. FederatedEvaluationRunDetail.tsx — remove Run ID and Agent ID, update subtitle

Remove Run ID and Agent ID from lines 195-202. Keep Rubric, Test Set, Progress, Test Items. Grid changes from `grid-cols-6` to `grid-cols-4`.

Update subtitle (line 162) to remove the run ID hash:
```tsx
subtitle="Run Detail"
```

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `ui/src/pages/EvaluationRunDetail.tsx` | Remove Run ID + Agent ID from metadata grid | 152-169 |
| `ui/src/federation/components/FederatedEvaluationRunDetail.tsx` | Remove Run ID + Agent ID from metadata grid, update subtitle | 162, 194-202 |

## Complexity

Trivial — delete two grid items from each file.

## Linear Response (draft)

> Fixed. Removed internal Run ID and Agent ID from the evaluation run detail view. The metadata section now shows only user-relevant info: progress, test items, rubric, and test set.
