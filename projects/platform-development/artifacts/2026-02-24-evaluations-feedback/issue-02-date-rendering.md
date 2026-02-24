---
ask: "Deep dive into COP-325 Issue 2: Date rendering issue in Evaluations tab"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-a
sources:
  - type: github
    description: "indemn-platform-v2/ui/src/components/evaluation/EvaluationsPanel.tsx lines 282-290, 390-391"
  - type: linear
    description: "COP-325 Issue 2 screenshot"
---

# Issue 2: Date Rendering Issue in Evaluations Tab

## Feedback (from Dhruv)

The date isn't rendering correctly in the Evaluations tab — looks like a simple UI bug.

## Assessment

The date IS rendering correctly ("Feb 23, 9:12 PM") — the issue is that the Date column is too narrow, causing the text to wrap across 3-4 lines (e.g., "Feb\n23,\n9:12\nPM").

The runs table has 7 columns (Date, Model, Rubric, Test Source, Score, Status, chevron) competing for horizontal space. The Date column has no `min-width` or `white-space: nowrap`, so it gets compressed first.

### Code Location

`indemn-platform-v2/ui/src/components/evaluation/EvaluationsPanel.tsx`:
- `formatDate` function at lines 282-290: produces "Feb 23, 9:12 PM" format
- Date cell at line 391: `<span className="text-sm">{formatDate(run.created_at)}</span>` — no `whitespace-nowrap`

## Resolution

Two changes:

1. **Add `whitespace-nowrap`** to the date cell so it stays on one line:
```tsx
// Line 391
<span className="text-sm whitespace-nowrap">{formatDate(run.created_at)}</span>
```

2. **Use a more compact format** to save horizontal space:
```ts
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
};
```
The format itself is fine — just needs `whitespace-nowrap`. Alternatively, could shorten to "2/23 9:12p" but the current format is more readable.

Also applies to `EvaluationSection.tsx` line 250 (same table in the agent overview card).

### Additional consideration

The API returns dates without timezone suffix (`'2026-02-24T09:54:18.779000'`). JavaScript parses this as local time, but the server stores UTC. This could cause times to display shifted by the user's timezone offset. Should append `Z` to the serialized datetime on the backend, or handle it in the frontend.

## Complexity

Trivial — add one CSS class.

## Linear Response (draft)

> Fixed. The date was rendering correctly but the column had no `white-space: nowrap`, causing the text to wrap across multiple lines when the table was narrow. Added `whitespace-nowrap` to keep dates on a single line.
