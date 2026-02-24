---
ask: "Deep dive into COP-325 Issue 1: Matrix view Question field showing raw dict + item 6 false failure"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-a
sources:
  - type: linear
    description: "COP-325 - Evaluations Feedback - UI & Functional Issues"
  - type: mongodb
    description: "Dev evaluations DB — run 5b841c47, test set 3e3c1f7c, rubric 6ece933d"
  - type: github
    description: "indemn-platform-v2/ui/src/components/evaluation/utils.ts, evaluations/src/indemn_evals/engine/single_turn.py"
---

# Issue 1: Matrix View — Question Field Showing Raw Dict + Tool Log Causing False Failures

## Feedback (from Dhruv)

In the Matrix view, the Question field is rendering as a raw dict (e.g., `{"bot_id": ""}`). Also item #6 looks like a valid response coming from the AI Agent, but it's still being treated as a failure. Likely caused by appending the `--- TOOL EXECUTION LOG ---` on our side, which is causing some evaluations to fail.

## Sub-Issue A: Raw Dict in Question Column

### Root Cause

In `indemn-platform-v2/ui/src/components/evaluation/utils.ts` line 113:

```ts
const question = result.input?.message || JSON.stringify(result.input);
```

For **scenario** test items, `input.message` is `null` — scenarios use `input.initial_message` and `input.persona` instead. The fallback `JSON.stringify(result.input)` dumps the entire input object, which includes `bot_id`, `session_id`, `conversation_id`, etc.

### Evidence

Run `5b841c47` against test set `3e3c1f7c` (Wedding Bot, 15 items):
- Items 1-7 are single_turn → `input.message` is populated → displays correctly
- Items 8-15 are scenarios → `input.message` is null → falls back to raw JSON

### Resolution

Update the fallback chain in `utils.ts` line 113:

```ts
// Before
const question = result.input?.message || JSON.stringify(result.input);

// After
const question = result.input?.message
  || result.input?.initial_message
  || result.input?.item_name
  || JSON.stringify(result.input);
```

Also update line 114 (response fallback) similarly if needed.

### Complexity

Trivial — single line change in `utils.ts`.

---

## Sub-Issue B: Tool Execution Log Causing False R05 Failures

### Root Cause

The evaluations engine appends a `--- TOOL EXECUTION LOG ---` to the bot's response text before sending it to LLM judges. This happens in `evaluations/src/indemn_evals/engine/single_turn.py` lines 60-86.

The **criteria evaluator** is explicitly told to use the tool log as evidence (correct behavior). But the **rubric rule evaluators** (LLM judges) also receive the full output including the tool log, and they interpret it as part of the agent's response to the user.

### Evidence

Run `5b841c47`, Item 6 — "Greeting and Role Identification":

**Bot response (actual):**
> I can help you get a wedding insurance quote (liability, cancellation, or both), answer common coverage questions, and guide you through purchasing a policy and getting a certificate of insurance for your venue. To get started, what type of insurance coverage are you looking for — liability, cancellation, or both?

**What the evaluator saw:**
> [above response] + `--- TOOL EXECUTION LOG --- Result: ["This is just a Conditional Flow Logic that needs to be followed strictly:...`

**R05 (Response Clarity and Coherence) judge reasoning:**
> "However, the response includes irrelevant technical details or debug information at the end: '--- TOOL EXECUTION LOG ---'. This padding is verbose, confusing, and irrelevant to the user's question, violating the rule's requirement for conciseness and relevance."

The judge correctly identified the tool log as irrelevant noise — it just doesn't know that it's metadata appended by the harness, not part of the bot's actual response.

### Impact

R05 failed on 5 out of 15 items in this run. Across multiple runs, R05 is the most frequently failed rule at 67% pass rate (vs 93-100% for other rules). This is almost certainly inflated by the tool log issue.

### Resolution Options

**Option A (Recommended): Separate the tool log from the response for rubric evaluators**

Pass the tool log as a separate field to evaluators. Criteria evaluators use it as evidence. Rubric evaluators evaluate only the clean response text.

In `single_turn.py`, instead of:
```python
response_text += tool_trace  # appended to response
```

Return both:
```python
return {"response": response_text, "tool_trace": tool_trace}
```

Update rubric evaluator prompts to receive `response` only. Update criteria evaluator to receive `response + tool_trace`.

**Option B: Add explicit instruction to rubric evaluator prompts**

Add to each rubric LLM judge system prompt:
> "The agent output may include a '--- TOOL EXECUTION LOG ---' section. This is debugging metadata appended by the evaluation harness, NOT part of the agent's response to the user. Ignore it when evaluating response quality."

Option A is cleaner but requires backend changes. Option B is a prompt-only fix.

### Complexity

Option A: Medium — changes to single_turn.py, multi_turn_simulated.py, and evaluator builder logic in builders.py.
Option B: Low — prompt change in builders.py only.

---

## Linear Response (draft — post after testing)

> Resolved in [commit/PR].
>
> **Raw dict in Question column:** Fixed the display fallback for scenario-type test items. The matrix now shows `initial_message` for scenarios instead of the raw JSON input object.
>
> **Tool Execution Log causing false failures:** The `--- TOOL EXECUTION LOG ---` was being appended to the bot's response text and sent to all evaluators including rubric rule judges. The judges correctly identified it as irrelevant noise but incorrectly penalized the bot for it. Fixed by [separating the tool log from the response / updating evaluator prompts to exclude it]. R05 pass rate should normalize after this fix.
