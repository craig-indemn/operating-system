---
ask: "Deep dive into COP-325 Issue 9: 'None (criteria only)' rubric option"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-b
sources:
  - type: github
    description: "indemn-platform-v2/ui/src/components/evaluation/RunEvaluationModal.tsx lines 139-141"
---

# Issue 9: "None (criteria only)" Rubric Option

## Feedback (from Dhruv)

The rubric dropdown shows a "None (criteria only)" option. What does this mean?

## Assessment

Working as designed. No code changes needed.

## Linear Response (draft)

> Test sets contain scenarios with their own success criteria — specific pass/fail conditions for each test case (e.g., "agent declines off-topic request and redirects to insurance"). Rubrics are universal quality rules that apply to every response (e.g., "professional tone", "no harmful content").
>
> When you run an evaluation, test set criteria always run. Rubric is optional — "None (criteria only)" means you're only checking whether the agent handled each scenario correctly, without scoring against universal rules. Useful when you want to test specific behaviors without the rubric overhead.
