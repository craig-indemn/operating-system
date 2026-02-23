---
ask: "Comprehensive audit of the EventGuard Wedding Insurance Bot baseline evaluation — rubric, test set, results, Jarvis prompt comparison, and recommendations for improving baseline generation"
created: 2026-02-23
workstream: platform-development
session: 2026-02-23-a
sources:
  - type: mongodb
    description: "tiledesk DB on dev cluster via percy-service container — evaluation_runs, rubrics, test_sets, evaluation_results, faq_kbs, bot_tools, jarvis_jobs, platform_templates"
  - type: github
    description: "percy-service/scripts/seed_jarvis_templates.py — EVALUATION_JARVIS_PROMPT, TEST_SET_CREATOR_PROMPT, RUBRIC_CREATOR_PROMPT"
  - type: local
    description: "Dev EC2 (ec2-44-196-55-84.compute-1.amazonaws.com) — queries run via sudo docker exec percy-service"
---

# EventGuard Evaluation Audit

Comprehensive audit of the baseline evaluation created for the EventGuard Wedding Insurance Bot on 2026-02-23. Covers the rubric, test set, evaluation results, Jarvis prompt analysis, and detailed recommendations.

---

## 1. Evaluation Run Summary

| Field | Value |
|-------|-------|
| Run ID | `0786fe77-067a-4f89-aea9-f921f12d37c9` |
| MongoDB `_id` | `699c6a6be000d1fd60b0e8e6` |
| Agent ID | `676be5cbab56400012077f4a` (Wedding Bot) |
| Project ID | `676be5cbab56400012077f03` |
| Status | `completed` |
| Started | 2026-02-23 14:55:39 UTC |
| Completed | 2026-02-23 15:10:49 UTC (~15 min) |
| Total items | 24 (10 single-turn + 14 scenarios) |
| Passed | 2 |
| Failed | 22 |
| Concurrency | 3 |
| Bot LLM | OpenAI gpt-5.2 |
| Rubric ID | `f3cf94bd-bba1-4aeb-9a94-24991cd1b496` |
| Test Set ID | `0e2ab005-51fb-4944-a61a-3f0ff8831f24` |

### Component Scores from Run

| Scope | Score | Passed | Total |
|-------|-------|--------|-------|
| general (rubric) | 57.5% | 42 | 73 |
| prompt (rubric) | 82.3% | 315 | 383 |
| criteria (scenario-specific) | 50.7% | 68 | 134 |

---

## 2. Database Location

**Critical finding:** Evaluation data for V1 bots lives in the **tiledesk** database, NOT the separate `evaluations` database. The `evaluations` DB exists but contains older data from the separate evaluations service (Family First runs). The current evaluation framework stores in tiledesk:

| Collection | Count | Purpose |
|------------|-------|---------|
| `evaluation_runs` | 56 | Run metadata and aggregate scores |
| `evaluation_results` | 245 | Per-item results with criteria/rubric scores |
| `rubrics` | 36 | Rubric definitions |
| `test_sets` | 12 | Test set definitions |
| `test_cases` | 273 | Individual test case records |
| `jarvis_jobs` | 7 | Jarvis baseline generation job tracking |
| `question_sets` | 22 | Legacy question sets |
| `scenarios` | 16 | Legacy scenarios |

---

## 3. Jarvis Prompt Comparison: Database vs Codebase

### Templates in Database

The `tiledesk.platform_templates` collection contains 29 templates. The evaluation-related ones:

| Template ID | Name | Updated | Prompt Length |
|-------------|------|---------|-------------|
| `jarvis_evaluation_v1` | Jarvis (Evaluation) | 2026-02-20 | 11,673 chars |
| `jarvis_indemn_v1` | Jarvis (Indemn) | 2026-02-20 | 13,591 chars |
| `jarvis_org_admin_v1` | Jarvis (Organization Admin) | 2026-02-20 | 13,568 chars |
| `jarvis_user_v1` | Jarvis (User) | 2026-02-20 | 13,509 chars |

### Codebase Source

File: `percy-service/scripts/seed_jarvis_templates.py`

| Prompt | Code Location (line) | Purpose |
|--------|---------------------|---------|
| `EVALUATION_JARVIS_PROMPT` | Line 401 | Evaluation orchestrator (mode detection, workflow management) |
| `TEST_SET_CREATOR_PROMPT` | Line 676 | Subagent: creates test sets |
| `RUBRIC_CREATOR_PROMPT` | Line 941 | Subagent: creates rubrics |

### Comparison Result

**The DB prompt matches the code.** Both the evaluation orchestrator and subagent prompts were seeded on 2026-02-20 and the opening text matches character-for-character. The most recent seed was applied to the database.

**The problem is not stale prompts — it's that the rubric_creator subagent is not following its own instructions.**

---

## 4. Rubric Audit

### Rubric Metadata

| Field | Value |
|-------|-------|
| Rubric ID | `f3cf94bd-bba1-4aeb-9a94-24991cd1b496` |
| Name | EventGuard Wedding Insurance Bot Rubric |
| Version | 1 |
| Created | 2026-02-23 14:55:18 UTC |
| Total Rules | **18** |

### The Core Problem: 18 Rules, Should Be 5-8

The `RUBRIC_CREATOR_PROMPT` explicitly states:
- *"Aim for roughly **5-8 rules**"*
- *"Every rubric rule MUST make sense to check on every single response"*
- *"DOES NOT belong in rubric (situational): Agent triggers handoff for distressed users, Agent uses KB search for factual questions, Agent collects date of birth before quoting"*

The created rubric has 18 rules, and **15 of them are workflow-specific** — they fail the universal applicability test.

### Rules That ARE Universal (Keep)

| ID | Name | Severity | Category | Why Universal |
|----|------|----------|----------|---------------|
| `no_hallucination_and_uncertainty_acknowledgment` | No Hallucination | high | safety | Checkable on any response — agent must never fabricate |
| `professional_tone_and_clarity` | Professional Tone | medium | persona | Checkable on any response — tone applies everywhere |
| `graceful_error_handling_and_fallback` | Graceful Error Handling | medium | response_quality | Checkable when errors occur — universal error behavior |

### Rules That Are NOT Universal (Move to Scenario Criteria)

| ID | Name | Severity | Why NOT Universal |
|----|------|----------|-------------------|
| `flow_initialization_compliance` | Flow Init Compliance | high | Only applies when starting a quote request |
| `parameter_validation_before_execution` | Parameter Validation | high | Only applies during parameter collection phases |
| `venue_specific_restriction_enforcement` | Venue Restriction | high | Only applies when venue has specific mandates |
| `conditional_parameter_logic_enforcement` | Conditional Logic | high | Only applies during coverage selection |
| `minimum_cancellation_budget_validation` | Budget Validation | high | Only applies when budget is submitted with a minimum threshold |
| `disqualifying_condition_handling` | Weapons Disqualification | high | Only applies during underwriting with weapons mentioned |
| `coverage_exclusion_communication` | Coverage Exclusions | high | Only applies when animals/amusement devices mentioned |
| `date_validation_prerequisite` | Date Validation | high | Only applies when event_date is collected |
| `quote_follow_up_prerequisite` | Quote Follow-Up | high | Only applies after quote generation |
| `email_quote_prerequisite_validation` | Email Quote Prereq | high | Only applies when user requests email quote |
| `state_validation_eligibility_handling` | State Validation | high | Only applies during state validation step |
| `payment_prerequisite_sequencing` | Payment Sequencing | high | Only applies during purchase/payment flow |
| `modification_and_user_data_immutability` | Modification Rules | medium | Only applies when user requests changes |
| `flow_executor_suggested_tool_compliance` | Flow Executor Compliance | medium | Only applies during active tool execution |
| `partner_flow_preference_collection` | Partner Flow | medium | Only applies in the partner flow path |

### Impact of Non-Universal Rules in Rubric

Every test case gets scored against ALL 18 rubric rules. A simple test like "I need to correct my phone number" (#7) gets checked against:
- Payment prerequisite sequencing (irrelevant)
- Email quote validation (irrelevant)
- Flow initialization compliance (irrelevant)
- Budget validation (irrelevant)
- Weapons disqualification (irrelevant)

This inflates failure counts and makes the rubric scores meaningless. The `general` component score of 57.5% and `prompt` score of 82.3% don't reflect actual agent quality — they reflect irrelevant rules being applied to irrelevant tests.

---

## 5. Test Set Audit

### Test Set Metadata

| Field | Value |
|-------|-------|
| Test Set ID | `0e2ab005-51fb-4944-a61a-3f0ff8831f24` |
| Name | EventGuard Wedding Insurance Bot - Comprehensive Test Set |
| Version | 1 |
| Created | 2026-02-23 14:55:02 UTC |
| Total Items | 24 (10 scenarios + 14 single-turn) |

### The Core Problem: Single-Turn Tests Assume Mid-Conversation Context

The `TEST_SET_CREATOR_PROMPT` says:
- Multi-turn scenarios are *"your primary content"*
- Single-turn items are for *"diagnostic purposes"* — testing *"specific directive compliance"* and *"ALWAYS/NEVER/MUST statements"*
- Single-turn items should test things that don't require workflow context

**6 of the 10 single-turn tests assume mid-conversation state that doesn't exist:**

| # | Test Name | Input Message | Bot Response | Problem |
|---|-----------|---------------|-------------|---------|
| 1 | Liability requires only alcohol_required | "I'll go with liability coverage only." | "Could you provide me with the state?" | Bot starts from scratch — asks for state first, not alcohol |
| 3 | Both coverage conditional logic | "I want both liability and cancellation coverage" | "Could you provide me with the state?" | Same — bot initializes flow, doesn't jump to parameter collection |
| 5 | Cancellation requires only budget | "I want cancellation coverage only." | "Could you provide me with the state?" | Same |
| 2 | Payment retry on missing SECTION OMEGA | "I completed the payment but didn't see a confirmation" | Explains SECTION OMEGA, asks if they saw it | No payment context exists — can't re-execute payment_model_function |
| 8 | Budget below minimum → block | "I can only afford $1,000 for coverage." | Unknown | No budget minimum context exists |
| 9 | is_modify_quote=false → block changes | "I'd like to add cancellation to my liability quote." | Unknown | No prior quote or is_modify_quote flag exists |

**4 single-turn tests that work correctly:**

| # | Test Name | Input Message | Why It Works |
|---|-----------|---------------|-------------|
| 6 | Agent must ask for insurance_coverage | "I need a quote for my wedding." | Valid start-of-conversation — tests initial behavior |
| 7 | Empathetic contact modification | "I need to correct my phone number." | Valid standalone — tests tone/helpfulness |
| 10 | Clear error on unrelated request | "Can you help me figure out my tax deductions?" | Valid off-topic test — no prior context needed |
| 4 | Budget meets minimum → proceed | "Our budget is $15,000." | Criteria actually passed — bot acknowledged the budget |

### Scenario Turn Limits Too Short

The bot's full workflow has 12+ steps:
```
initial_conditions → coverage selection → parameters → state validation →
quote generation → quote follow-up → contact details → event details →
underwriting → complete_purchase → payment_validation → payment button →
payment model → feedback
```

Several scenarios can't reach their test targets within `max_turns`:

| # | Scenario | max_turns | Target Phase | Criteria Passed | Issue |
|---|----------|-----------|-------------|-----------------|-------|
| 14 | Guest weapons → disqualification | 8 | event_details (step 8+) | 3/7 | Ran out of turns before underwriting |
| 20 | Animals/amusement devices | 10 | event_details (step 8+) | 3/7 | Same |
| 23 | Full happy path (end-to-end) | 15 | payment (step 12+) | 7/15 | Made it through quote_follow_up + contact but stalled at event_details |
| 24 | Professional security → continue | 10 | event_details (step 8+) | 2/7 | Couldn't reach underwriting phase |

### Missing Venue Context in Flow Init Scenarios

Scenarios #17, #21, and #22 test venue-specific routing (all mandates true, cancellation unavailable, partner flow). These require `cancellation_available`, `mandate_liability`, and `mandate_cancellation` flags in the initial payload.

**Without these flags, the bot defaults to the generic path** (asking user to choose coverage type). This is correct bot behavior — but the test expects venue-specific routing that can't happen without the venue context.

| # | Scenario | Expected Routing | Actual Behavior | Root Cause |
|---|----------|-----------------|-----------------|------------|
| 17 | All Mandates True | Route to `all_mandate_conditions_true` | Asked user to choose coverage type | No mandate flags in initial payload |
| 21 | Cancellation Unavailable | Route to `cancellation_available_false` | Asked user to choose coverage type | No `cancellation_available=false` flag |
| 22 | Partner Flow (liability only) | Route to `partner_flow` | Asked user to choose coverage type | No partial mandate flags |
| 16 | Default path (no mandates) | Ask user to choose | Asked user to choose | **PASSED** — this is the default behavior |

---

## 6. Detailed Evaluation Results

### Result-by-Result Summary

| # | Type | Name | Criteria | Rubric | Pass | Key Issue |
|---|------|------|----------|--------|------|-----------|
| 1 | single_turn | Liability → only alcohol_required | FAIL | FAIL | FAIL | No flow context — bot asks for state |
| 2 | single_turn | Payment retry on missing SECTION OMEGA | FAIL | PASS | FAIL | No payment context — can't re-execute |
| 3 | single_turn | Both coverage conditional logic | FAIL | FAIL | FAIL | No flow context — bot asks for state |
| 4 | single_turn | Budget meets minimum → proceed | PASS | FAIL | FAIL | Criteria passed! Rubric failed on irrelevant rules |
| 5 | single_turn | Cancellation → only budget | FAIL | FAIL | FAIL | No flow context — bot asks for state |
| 6 | single_turn | Must ask for insurance_coverage | FAIL | FAIL | FAIL | Bot correctly asks for coverage type, but criteria wants "clear explanation of each option" |
| 7 | single_turn | Empathetic contact modification | PASS | PASS | **PASS** | Works perfectly — valid standalone test |
| 8 | single_turn | Budget below minimum → block | FAIL | FAIL | FAIL | No minimum_cancellation_required in context |
| 9 | single_turn | is_modify_quote=false → block changes | FAIL | FAIL | FAIL | No prior quote or modify flag exists |
| 10 | single_turn | Clear error on unrelated request | FAIL | PASS | FAIL | Rubric passed! Criteria failed on "smoothly redirects back to quoting" |
| 11 | scenario | Quote mod: budget adjustment | FAIL | FAIL | FAIL | Bot starts flow initialization instead of modification |
| 12 | scenario | Human handoff: Slack notification first | FAIL | FAIL | FAIL | Slack notification tool returned `invalid_token` error |
| 13 | scenario | Quote mod: adding cancellation + date | FAIL | FAIL | FAIL | Got 4/7 criteria — reached date validation but stalled on budget/modify |
| 14 | scenario | Underwriting: guest weapons → disqualify | FAIL | FAIL | FAIL | 3/7 — couldn't reach event_details/underwriting phase |
| 15 | scenario | State validation: eligible state | FAIL | FAIL | FAIL | Bot asked for state even though user said "California" in message. State validation returned restriction |
| 16 | scenario | Flow init: default path | PASS | PASS | **PASS** | 5/5 criteria — bot correctly follows default flow |
| 17 | scenario | Flow init: all mandates true | FAIL | FAIL | FAIL | 4/6 — no mandate flags, bot defaults to user choice |
| 18 | scenario | Quote email request | FAIL | FAIL | FAIL | No prior quote_follow_up context |
| 19 | scenario | State validation: restricted state | FAIL | PASS | FAIL | Rubric passed! State validation didn't return restriction for "[restricted state]" literal |
| 20 | scenario | Underwriting: animals/amusement | FAIL | FAIL | FAIL | 3/7 — couldn't reach underwriting phase within turns |
| 21 | scenario | Flow init: cancellation unavailable | FAIL | FAIL | FAIL | No cancellation_available=false flag |
| 22 | scenario | Flow init: partner flow | FAIL | FAIL | FAIL | No partial mandate flags |
| 23 | scenario | Full happy path (end-to-end) | FAIL | FAIL | FAIL | **7/15** criteria — made it through quote + contact but ran out of turns |
| 24 | scenario | Underwriting: professional security | FAIL | PASS | FAIL | Rubric passed! Couldn't reach underwriting to test |

### Patterns in Failures

**Category A — Missing conversation context (8 items):** #1, #2, #3, #5, #8, #9, #11, #18
These all assume prior workflow state that doesn't exist. The bot correctly starts from scratch but the test expects mid-flow behavior.

**Category B — Insufficient turn budget (4 items):** #14, #20, #23, #24
The bot is progressing through its workflow correctly but runs out of turns before reaching the phase being tested.

**Category C — Missing venue/initial payload context (3 items):** #17, #21, #22
The flow init scenarios need venue-specific mandate flags that aren't being passed.

**Category D — External/data issues (3 items):** #12 (Slack token invalid), #15 (state validation returned unexpected restriction for California), #19 (literal "[restricted state]" not recognized)

**Category E — Criteria too strict (2 items):** #6 (wants explanation of each option — bot just asked the question), #10 (wants smooth redirect to quoting — bot answered the question well)

**Category F — Legitimate passes (2 items):** #7, #16

**Category G — False negatives from rubric (2 items):** #4 (criteria passed but rubric failed on irrelevant workflow rules), #2/#10/#19/#24 (rubric passed but criteria failed for separate reasons)

---

## 7. Bot Configuration Reference

### Bot Identity

| Field | Value |
|-------|-------|
| Name | Wedding Bot |
| `_id` | `676be5cbab56400012077f4a` |
| Type | `copilot_faq_kb` |
| Project | `676be5cbab56400012077f03` |
| Organization | `676be5a7ab56400012077e7d` |
| Created | 2024-12-25 |
| Last Updated | 2026-02-23 06:24:19 UTC |

### Bot Tools (46 total — duplicates present)

The bot has 46 tools, but many are duplicated (two copies of most tools). Unique tools in workflow order:

| Tool | Type | Workflow Phase |
|------|------|---------------|
| `@initial_conditions_insurance` | custom_tool | **Phase 1: Flow initialization** — determines routing based on venue mandates |
| `@cancellation_available_false` | custom_tool | Phase 1 route: liability-only path |
| `@all_mandate_conditions_true` | custom_tool | Phase 1 route: both coverage mandated |
| `@partner_flow` | custom_tool | Phase 1 route: user preference for additional coverage |
| `@get_insurance_quote` | custom_tool | **Phase 2: Parameter collection** — conditional on coverage type |
| `@generate_quote` | rest_api | **Phase 3: Quote generation** — calls API |
| `@State_Validation` | rest_api | **Phase 4: State validation** — checks eligibility |
| `@insurance_confirm` | custom_tool | Phase 4 branch: handles state restrictions |
| `@quote_follow_up` | custom_tool | **Phase 5: Quote selection** — user picks a quote |
| `@Email Quote` | rest_api | Phase 5 optional: email quote to user |
| `@contact_details` | rest_api | **Phase 6: Contact collection** — name, email, phone |
| `@event_details` | custom_tool | **Phase 7: Event details** — date, venue, guests, underwriting |
| `@validate_date` | rest_api | Phase 7 sub: date eligibility check |
| `@modify_quote` | rest_api | Optional: quote modification flow |
| `@complete_purchase` | custom_tool | **Phase 8: Purchase finalization** |
| `@payment_validation` | rest_api | **Phase 9: Payment validation** — checks missing params |
| `@Payment Button Function` | rest_api | **Phase 10: Payment link generation** |
| `@payment model function` | rest_api | **Phase 11: Payment processing** — must see SECTION OMEGA |
| `@Capture user feedback 1` | user_feedback_tool | **Phase 12: Post-payment feedback** |
| `@human_handoff` | human_handoff | Any time: live agent transfer |
| `@human_handoff_slack_notification` | rest_api | Pre-handoff: Slack team notification |
| `@Offline handoff` | offline_human_handoff | Frustrated user fallback |
| `@Offline handoff for distressed users` | offline_human_handoff | Distressed user escalation |
| `@FAQs Retriever` | faqs-retriever | Any time: knowledge base search |
| `@REST API 1` | rest_api | Unknown purpose |

**Note on duplicates:** Tools appear twice (46 total for ~23 unique). This is likely because the bot belongs to a project with multiple knowledge base / tool sets. The duplicate tools could cause model confusion about which version to call.

### Bot Prompt

The bot prompt was NOT found in `bot_configurations`, `llm_configurations`, or `structure_agents` for this bot_id. The V1 bot-service likely constructs the system prompt dynamically at runtime from:
1. The default prompt template (Sales/Customer Service/Claims — all empty in dev)
2. The tool descriptions (each tool has its own instruction text)
3. The knowledge base content
4. The project/organization configuration

This means the bot's "prompt" is effectively the concatenation of all 46 tool descriptions plus any KB content. The tool descriptions contain the actual behavioral instructions (conditional logic, parameter validation rules, prerequisite chains, etc.).

---

## 8. Jarvis Job History

The most recent Jarvis job in the `jarvis_jobs` collection is from **2026-02-10** (FAQ Bot baseline generation, failed with connection error). The EventGuard baseline from today was created through **interactive Jarvis** in devcopilot, not through the headless job system.

| Job ID | Date | Type | Status | Bot |
|--------|------|------|--------|-----|
| `698bc5cb...` | 2026-02-10 | baseline_generation | completed | FAQ Bot (failed: connection error) |
| `6984efeb...` | 2026-02-05 | baseline_generation | completed | Unknown |
| `6984ef14...` | 2026-02-05 | baseline_generation | completed | Unknown |
| (4 more) | 2026-02-05 | baseline_generation | completed | Unknown |

---

## 9. Recommendations

### Immediate: Fix This Evaluation

1. **Rewrite rubric** — Strip to 3-5 truly universal rules:
   - No hallucination / uncertainty acknowledgment (high, safety)
   - Professional tone and clarity (medium, persona)
   - Stays in scope / graceful error handling (medium, response_quality)
   - Parameter validation — never assume values (high, instruction_compliance) — this one IS universal enough
   - No harmful content (high, safety)

2. **Move 14 workflow rules into scenario criteria** — Each workflow-specific rule becomes a success criterion on the scenario that tests that behavior.

3. **Convert 6 single-turn tests to multi-turn scenarios** — Tests #1, #2, #3, #5, #8, #9 need conversation context established first.

4. **Increase max_turns** — Underwriting scenarios need 12-15 turns. Full happy path needs 18-20.

5. **Add venue context to flow init scenarios** — Either pass initial payload flags or note that these scenarios can't be tested without venue configuration.

6. **Fix scenario #19** — Replace literal "[restricted state]" with an actual restricted state name.

7. **Investigate Slack token** — #12 failed because `human_handoff_slack_notification` returned `invalid_token`.

### Medium-term: Improve Jarvis Baseline Generation

8. **Strengthen rubric_creator prompt** — The universal applicability guidance is clear but the subagent ignored it. Options:
   - Add explicit examples for insurance bots (what belongs vs doesn't)
   - Add a hard cap: "NEVER create more than 8 rules"
   - Add a self-check step: "Before creating, verify each rule passes the universal test"
   - Add negative examples from this actual rubric

9. **Strengthen test_set_creator prompt** — The single-turn guidance is good but the subagent created context-dependent single-turn tests. Options:
   - Add explicit guidance: "Single-turn tests must NOT assume any prior conversation context"
   - Add: "If a behavior requires prior workflow steps, it MUST be a multi-turn scenario"
   - Add max_turns guidance based on workflow depth analysis

10. **Investigate bot tool duplicates** — 46 tools for ~23 unique tools. Clean up or understand why duplicates exist.

11. **Add venue context support** — The evaluation framework may need a way to inject initial payload data (venue mandates, feature flags) into test scenarios.

---

## 10. Reference: Evaluation Data Access

### How to Query (from local machine via EC2)

```bash
# SSH to dev EC2
ssh -i /Users/home/Repositories/ptrkdy.pem ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com

# Run Python queries via percy-service container (has pymongo)
sudo docker exec percy-service python3 -c "
import os, pymongo
client = pymongo.MongoClient(os.environ.get('MONGO_URL'))
tdb = client[os.environ.get('V1_MONGODB_DB', 'tiledesk')]
# ... queries here
"
```

**Note:** Direct mongosh connection from local machine fails due to Atlas IP whitelist. All queries must go through the EC2 → percy-service container path.

### Key Collections and IDs

| Entity | Collection | ID Field | This Run's ID |
|--------|-----------|----------|---------------|
| Evaluation run | `tiledesk.evaluation_runs` | `run_id` | `0786fe77-067a-4f89-aea9-f921f12d37c9` |
| Rubric | `tiledesk.rubrics` | `rubric_id` | `f3cf94bd-bba1-4aeb-9a94-24991cd1b496` |
| Test set | `tiledesk.test_sets` | `test_set_id` | `0e2ab005-51fb-4944-a61a-3f0ff8831f24` |
| Results | `tiledesk.evaluation_results` | `run_id` (filter) | 24 documents |
| Bot | `tiledesk.faq_kbs` | `_id` | `ObjectId("676be5cbab56400012077f4a")` |
| Bot tools | `tiledesk.bot_tools` | `bot_id` | `ObjectId("676be5cbab56400012077f4a")` |
| Jarvis template | `tiledesk.platform_templates` | `template_id` | `jarvis_evaluation_v1` |

### Query for Results

```python
# Get all results for today's run
results = list(tdb["evaluation_results"].find(
    {"run_id": "0786fe77-067a-4f89-aea9-f921f12d37c9"}
).sort("created_at", 1))

# Result document structure
{
    "result_id": "uuid",
    "run_id": "uuid",
    "test_case_id": "uuid",
    "item_name": "Test name",
    "item_type": "single_turn | scenario",
    "input": {"bot_id": "...", "message": "...", "persona": "...", "initial_message": "...", "max_turns": N},
    "output": {"response": "Full conversation transcript"},
    "criteria_scores": [...],     # Per-item success criteria results
    "criteria_passed": bool,
    "rubric_scores": [...],       # Universal rubric rule results (large)
    "rubric_passed": bool,
    "passed": bool,               # AND of criteria_passed and rubric_passed
    "duration_ms": int,
    "created_at": datetime
}
```
