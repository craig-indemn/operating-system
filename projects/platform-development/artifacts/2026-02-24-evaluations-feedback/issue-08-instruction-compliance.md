---
ask: "Deep dive into COP-325 Issue 8: Clarify 'instruction_compliance' metric"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-b
sources:
  - type: github
    description: "percy-service/skills/evaluations/rubric-creation/SKILL.md line 108 — category field definition"
---

# Issue 8: Clarify "instruction_compliance" Metric

## Feedback (from Dhruv)

What is "instruction_compliance"? Wants clarity on what this metric means.

## Assessment

Not a bug. `instruction_compliance` is a category label on rubric rules — it means the rule checks whether the agent follows its configured instructions. It doesn't affect scoring; it's context for the LLM evaluator.

Four categories exist: `persona` (tone/style), `instruction_compliance` (follows instructions), `safety` (no harmful content), `response_quality` (clarity/coherence).

No code changes needed.

## Linear Response (draft)

> `instruction_compliance` is a **rubric rule category** — a semantic label indicating the rule checks whether the agent follows its configured instructions. There are four categories:
> - **persona** — tone, communication style
> - **instruction_compliance** — follows configured instructions
> - **safety** — no harmful or inappropriate content
> - **response_quality** — clarity, coherence, accuracy
>
> Categories are informational context for the LLM evaluator — they don't affect scoring or filtering. Separately, **component_scope** (prompt, general, function, knowledge_base) determines which rules are included when running an evaluation with a scope filter.
