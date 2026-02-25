# Evaluation API Data Shapes

Response shapes from the evaluations API at `localhost:8002`. All endpoints prefixed with `/api/v1`.

## EvaluationRun

**Endpoint:** `GET /runs/{run_id}`

```json
{
  "run_id": "uuid",
  "dataset_id": "uuid",
  "agent_id": "mongodb-objectid",
  "status": "pending | running | completed | failed",
  "total": 13,
  "completed": 13,
  "passed": 8,
  "failed": 5,
  "concurrency": 3,
  "started_at": "datetime",
  "completed_at": "datetime",
  "error": "string | null",
  "rubric_id": "uuid | null",
  "rubric_version": 1,
  "test_set_id": "uuid | null",
  "test_set_version": 1,
  "component_scope_filter": "string | null",
  "component_ids_filter": ["string"] ,
  "component_scores": {
    "prompt": { "score": 0.85, "total": 20, "passed": 17 },
    "knowledge_base": { "score": 0.75, "total": 8, "passed": 6 },
    "function": { "score": 1.0, "total": 4, "passed": 4 },
    "general": { "score": 0.9, "total": 10, "passed": 9 }
  },
  "criteria_passed": 35,
  "criteria_total": 40,
  "rubric_rules_passed": 90,
  "rubric_rules_total": 100,
  "bot_llm_provider": "openai",
  "bot_llm_model": "gpt-4.1",
  "created_at": "datetime"
}
```

**Key fields:**
- `component_scores` — rubric rule pass rates broken down by component scope (prompt, knowledge_base, function, general). Null if no rubric used.
- `criteria_passed/total` — aggregate criterion-level pass counts across ALL results
- `rubric_rules_passed/total` — aggregate rubric rule pass counts across ALL results
- `test_set_id` — present for V2 runs. `dataset_id` is for V1 question-set-based runs.

## EvaluationResult

**Endpoint:** `GET /runs/{run_id}/results`

Returns an array of results, one per test item.

```json
{
  "result_id": "uuid",
  "run_id": "uuid",
  "test_case_id": "uuid (matches TestItem.item_id)",
  "langsmith_run_id": "uuid | null",
  "input": {
    "persona": "...",
    "initial_message": "...",
    "max_turns": 8
  },
  "output": {
    "messages": [
      { "role": "user", "content": "..." },
      { "role": "assistant", "content": "..." }
    ]
  },
  "scores": {
    "evaluator_name": { "score": 0.8, "comment": "JSON string with details" }
  },
  "item_name": "PTO Policy Inquiry",
  "item_type": "scenario",
  "criteria_scores": [
    {
      "criterion": "Agent retrieves PTO policy from handbook KB",
      "passed": false,
      "score": 0.0,
      "reasoning": "Agent did not find PTO information..."
    }
  ],
  "criteria_passed": false,
  "rubric_scores": [
    {
      "rule_id": "BRIEF_RESPONSES",
      "rule_name": "Brief, Focused Responses",
      "severity": "medium",
      "passed": true,
      "score": 1.0,
      "reasoning": "Agent kept responses concise..."
    }
  ],
  "rubric_passed": true,
  "passed": false,
  "duration_ms": 45000,
  "created_at": "datetime"
}
```

**V1 vs V2 scoring:**
- **V1** (question-set runs): `scores` dict populated, `criteria_scores`/`rubric_scores` are null. The `comment` field in scores is a JSON string — parse it for per-criterion details.
- **V2** (test-set runs): `criteria_scores[]` and `rubric_scores[]` populated with structured data. `scores` may still be present.

**Passed logic:** `passed = criteria_passed AND rubric_passed`. An item fails if ANY criterion fails OR any high-severity rubric rule fails.

## Rubric

**Endpoint:** `GET /rubrics/{rubric_id}`

```json
{
  "rubric_id": "uuid",
  "agent_id": "mongodb-objectid",
  "version": 1,
  "name": "O'Connor Internal Ops Associate Rubric",
  "description": "...",
  "severity_definitions": {
    "high": "Critical violation...",
    "medium": "Moderate violation...",
    "low": "Minor violation..."
  },
  "rules": [
    {
      "id": "BRIEF_RESPONSES",
      "name": "Brief, Focused Responses",
      "severity": "medium",
      "category": "response_quality",
      "description": "Agent should provide concise answers...",
      "prompt_reference": "Section: Communication Style",
      "evaluation_criteria": {
        "pass_conditions": ["Response is under 3 sentences for simple questions"],
        "fail_conditions": ["Response includes unnecessary preamble or filler"]
      },
      "examples": {
        "violation": "...",
        "correct": "..."
      },
      "component_scope": "prompt | knowledge_base | function | general | null",
      "component_ids": ["objectid", "..."],
      "component_names": ["HR Handbook KB"]
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Key fields:**
- `rules[].evaluation_criteria` — pass/fail conditions the evaluator LLM uses to judge
- `rules[].severity` — high severity failures cause the entire item to fail
- `rules[].component_scope` — links rule to a specific component type for component-level scoring
- `rules[].component_ids` / `component_names` — links rule to specific bot components (KBs, tools, etc.)

## TestSet

**Endpoint:** `GET /test-sets/{test_set_id}`

```json
{
  "test_set_id": "uuid",
  "agent_id": "mongodb-objectid",
  "version": 2,
  "name": "O'Connor Internal Ops Associate Test Set",
  "description": "...",
  "items": [
    {
      "item_id": "uuid (matches EvaluationResult.test_case_id)",
      "type": "single_turn | scenario",
      "name": "PTO Policy Inquiry",
      "inputs": {
        "message": "What is our PTO policy?",
        "persona": "An employee asking about...",
        "initial_message": "Hi, I need to know...",
        "max_turns": 8
      },
      "expected": {
        "success_criteria": [
          "Agent retrieves PTO policy from knowledge base",
          "Response includes accrual rates or refers to handbook"
        ],
        "should_use_tools": ["search_kb"],
        "should_not_use_tools": ["live_handoff"],
        "expected_outcome": "Employee gets PTO info"
      },
      "tags": ["hr", "policy"],
      "priority": "high"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Key fields:**
- `items[].item_id` — join key to `EvaluationResult.test_case_id`
- `items[].type` — `single_turn` sends one message; `scenario` runs multi-turn simulation with persona
- `items[].inputs` — for single_turn: `message`; for scenario: `persona`, `initial_message`, `max_turns`
- `items[].expected.success_criteria` — the criteria that become `criteria_scores[]` in results

## BotContext

**Endpoint:** `GET /bots/{agent_id}/context`

```json
{
  "bot_id": "mongodb-objectid",
  "bot_name": "O'Connor Internal Operations Associate",
  "organization_id": "mongodb-objectid",
  "organization_name": "O'Connor Insurance",
  "system_prompt": "You are an AI assistant for O'Connor Insurance...",
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4.1",
    "parameters": { "temperature": 0.3 }
  },
  "tools": [
    {
      "id": "objectid",
      "name": "Live Chat Handoff",
      "tool_name": "live_handoff",
      "type": "human_handoff",
      "description": "Transfer to a live agent when...",
      "output_instructions": "..."
    }
  ],
  "knowledge_bases": [
    {
      "id": "objectid",
      "name": "O'Connor Employee Handbook",
      "type": "file",
      "document_count": 3
    }
  ],
  "harness_context": {
    "version": "1.0",
    "description": "LangGraph-based agent...",
    "execution_flow": [
      { "step": 1, "node": "invoke_model", "description": "..." }
    ],
    "key_behaviors": ["..."],
    "evaluation_notes": ["..."]
  }
}
```

**Key fields:**
- `system_prompt` — the full agent prompt; cross-reference against agent behavior to distinguish real bugs from expected behavior
- `tools[]` — available tools with their descriptions; critical for understanding handoff, search, and function-calling behavior
- `knowledge_bases[]` — connected KBs; check if test items assume KB content that may not exist
- `harness_context` — how bot-service executes the agent; useful for understanding tool call flow

## Versioning Endpoints

Both test sets and rubrics support version history:

```bash
# List all versions
GET /test-sets/{test_set_id}/versions
GET /rubrics/{rubric_id}/versions

# Get a specific version
GET /test-sets/{test_set_id}/versions/{version}
GET /rubrics/{rubric_id}/versions/{version}
```

PUT to update creates a new version automatically — previous versions are preserved.

## Listing Runs for an Agent

```bash
GET /runs?agent_id={agent_id}&status=completed&limit=5
```

Returns runs sorted by `created_at` descending. Use this when given an agent_id instead of a run_id.
