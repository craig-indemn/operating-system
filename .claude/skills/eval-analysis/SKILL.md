---
name: eval-analysis
description: Analyze evaluation results to classify failures as agent issues vs evaluation issues. Use when the user asks to analyze eval results, understand why tests failed, triage failures, or improve evaluation scores.
argument-hint: [run-id or agent-id]
allowed-tools: Bash(curl *)
---

# Eval Analysis

Analyze evaluation run results, classify each failure, and recommend fixes.

**Input:** `$ARGUMENTS` — a run_id (UUID) or agent_id (MongoDB ObjectId)

## Step 1: Resolve the Run

Determine what `$ARGUMENTS` is:
- **UUID format** (contains hyphens, 36 chars) → it's a `run_id`. Use directly.
- **ObjectId format** (24 hex chars) → it's an `agent_id`. Fetch the latest completed run:
  ```bash
  curl -s "http://localhost:8002/api/v1/runs?agent_id=$ARGUMENTS&status=completed&limit=1" | python3 -m json.tool
  ```
  Extract `run_id` from the first result.

If no completed runs exist, tell the user and stop.

## Step 2: Pull All Data

Make these calls (parallelize where possible):

```bash
# Run summary
curl -s "http://localhost:8002/api/v1/runs/{run_id}" | python3 -m json.tool

# Per-item results
curl -s "http://localhost:8002/api/v1/runs/{run_id}/results" | python3 -m json.tool

# Rubric (get rubric_id from run summary)
curl -s "http://localhost:8002/api/v1/rubrics/{rubric_id}" | python3 -m json.tool

# Test set (get test_set_id from run summary)
curl -s "http://localhost:8002/api/v1/test-sets/{test_set_id}" | python3 -m json.tool

# Bot context (get agent_id from run summary)
curl -s "http://localhost:8002/api/v1/bots/{agent_id}/context" | python3 -m json.tool
```

For exact response shapes, see `references/data-shapes.md`.

## Step 3: Present Run Overview

Show the user a summary table:

```
Run: {run_id}
Agent: {bot_name} ({agent_id})
LLM: {bot_llm_provider}/{bot_llm_model}
Status: {passed}/{total} items passed ({pass_rate}%)

Criteria: {criteria_passed}/{criteria_total} checks passed
Rubric: {rubric_rules_passed}/{rubric_rules_total} rules passed

Component Scores:
  prompt:         {score}% ({passed}/{total})
  knowledge_base: {score}% ({passed}/{total})
  function:       {score}% ({passed}/{total})
  general:        {score}% ({passed}/{total})
```

## Step 4: Analyze Each Failed Item

For every result where `passed == false`:

1. **Get the test item** — match `test_case_id` to the test set's `items[].item_id` to get the item name, type, inputs, and success_criteria
2. **Check criteria scores** — from `criteria_scores[]`, list which criteria passed and which failed with their reasoning
3. **Check rubric scores** — from `rubric_scores[]`, list which rules passed and which failed with their reasoning
4. **Check for divergence** — flag when criteria say FAIL but rubric says PASS (or vice versa). Divergence is a strong signal of an evaluation problem.
5. **Read the conversation** — look at `output` field for the full agent response or conversation transcript
6. **Cross-reference system prompt** — check if the agent's behavior aligns with what the system prompt instructs
7. **Classify** — assign one of four categories (see below)

### Failure Categories

| Category | Signal | Action |
|----------|--------|--------|
| **Real Agent Problem** | Both criteria and rubric agree agent misbehaved, or output contradicts system prompt | Investigate agent code/prompt |
| **Evaluation Problem** | Criteria ambiguous/too strict, evaluator reasoning shows misunderstanding, agent response was reasonable | Update test set criteria |
| **Test Design Problem** | Test assumptions wrong (e.g., assumed KB lacked info it has), criteria contradict agent's actual capabilities | Redesign test item |
| **KB/Retrieval Problem** | Agent behavior correct but retrieval returned wrong content, or KB is missing needed info | Fix KB content or retrieval config |

### Divergence Analysis

When `criteria_passed != rubric_passed` for an item, this is a first-class finding:
- **Criteria FAIL + Rubric PASS** → criteria are likely too strict or testing the wrong thing
- **Criteria PASS + Rubric FAIL** → rubric may have rules that don't apply to this scenario, or agent violated a behavioral rule despite answering correctly

Always highlight divergences prominently in the report.

## Step 5: Aggregate Findings

Group all failed items by category:

```
## Findings

### Real Agent Problems (N items)
- Item X: [description of what went wrong]

### Evaluation Problems (N items)
- Item Y: [why the criteria/rubric is wrong]

### Test Design Problems (N items)
- Item Z: [what assumption was incorrect]

### KB/Retrieval Problems (N items)
- Item W: [what retrieval issue occurred]
```

## Step 6: Recommendations

Prioritize fixes:

- **P1 — Evaluation fixes** (false failures inflate failure count, masking real issues): specific criteria rewrites or rubric rule adjustments
- **P2 — Agent investigation** (real bugs): which code paths or prompt sections to examine
- **P3 — KB/Retrieval fixes**: which knowledge bases need content updates or which retrieval configs need tuning

For each recommendation, be specific: quote the current criterion/rule, explain what's wrong, and propose the exact replacement text.

## Step 7: Offer to Execute Fixes

Ask the user if they want to apply the evaluation fixes. If yes:

**Update test set criteria** (creates a new version, non-destructive):
```bash
curl -s -X PUT "http://localhost:8002/api/v1/test-sets/{test_set_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [... updated items array ...]
  }' | python3 -m json.tool
```

**Update rubric rules** (creates a new version, non-destructive):
```bash
curl -s -X PUT "http://localhost:8002/api/v1/rubrics/{rubric_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [... updated rules array ...]
  }' | python3 -m json.tool
```

Both PUT endpoints create new versions — the previous version is preserved and accessible via the `/versions` endpoints.

After applying fixes, suggest re-running the evaluation to verify improvements.
