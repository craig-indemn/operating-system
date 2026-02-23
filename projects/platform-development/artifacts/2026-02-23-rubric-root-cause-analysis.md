---
ask: "Deep root cause analysis of why the Jarvis rubric_creator subagent created 18 workflow-specific rules instead of 5-8 universal ones — trace the full data flow, understand what the subagent actually received, and determine whether this is a prompt issue or a systemic design issue"
created: 2026-02-23
workstream: platform-development
session: 2026-02-23-b
sources:
  - type: github
    description: "percy-service — seed_jarvis_templates.py (prompts), deep_agent.py (subagent spawning), connectors/implementations/platform_api/evaluations.py (BotContextConnector), connectors/registry.py, api/v1_agents.py, api/main.py"
  - type: github
    description: "evaluations repo — api/main.py, api/routes/ (all route files) — confirmed NO /bots/{id}/context endpoint in local repo"
  - type: github
    description: "deepagents package (installed) — middleware/subagents.py (task tool, _validate_and_prepare_state, SubAgentMiddleware), graph.py (create_deep_agent)"
  - type: mongodb
    description: "tiledesk DB on dev cluster — bot_configurations (system_prompt, 5153 chars), bot_tools (21 unique), bot_kb_mappings (1 KB)"
  - type: local
    description: "Dev EC2 — tested bot_context endpoint via HTTP from percy-service container, verified environment variables"
---

# Rubric Creator Root Cause Analysis

Why the Jarvis rubric_creator produced 18 workflow-specific rules instead of 5-8 universal ones. This is NOT "the subagent defying its prompt" — it's a systemic design gap between the rubric architecture and V1 bot system prompts.

---

## 1. Executive Summary

**Previous diagnosis (session 2026-02-23-a):** "The problem is not stale prompts — it's that the rubric_creator subagent is not following its own instructions."

**Actual diagnosis (this session):** The rubric_creator IS following its instructions. The prompt says "extract ALWAYS/NEVER/MUST directives from the system prompt." The Wedding Bot's system prompt has 10+ workflow-specific directives using CRITICAL/MUST/MANDATORY/NEVER language. The prompt's universal applicability filter is guidance-level (soft), not structural (hard). When faced with a dense workflow prompt where every step is labeled CRITICAL, the LLM extracts them all.

**This is a systemic issue**, not just a prompt-tuning problem. The rubric_creator prompt was designed for agents with clean system prompts that clearly separate universal behavioral standards from workflow instructions. V1 bots like the Wedding Bot don't make this separation — their system prompts are dense workflow manuals where every instruction uses equally strong language.

---

## 2. The Full Data Flow (Verified End-to-End)

### 2.1 Template → Database → Subagent Prompt

```
percy-service/scripts/seed_jarvis_templates.py
  RUBRIC_CREATOR_PROMPT (line 941-1168)
    ↓ seed_templates() upserts to MongoDB
tiledesk.platform_templates (template_id: "jarvis_evaluation_v1")
  graph.nodes[0].config.subagents[1].system_prompt = RUBRIC_CREATOR_PROMPT
    ↓ percy-service startup (api/main.py)
GraphFactory → GraphCompiler → DeepAgentComponent.create_node()
    ↓ deep_agent.py line 236-243
subagent config → SubAgent TypedDict:
  {
    "name": "rubric_creator",
    "description": "Creates evaluation rubrics...",
    "system_prompt": RUBRIC_CREATOR_PROMPT,  ← PASSED UNCHANGED
    "tools": [bot_context_tool, rubrics_tool],
    "model": "anthropic:claude-haiku-4-5"
  }
    ↓ deepagents library (middleware/subagents.py line 275-280)
create_agent(model, system_prompt=RUBRIC_CREATOR_PROMPT, tools=tools)
```

**Verified:** The RUBRIC_CREATOR_PROMPT is passed completely unchanged from the seed script through the database through the component to the LLM. No truncation, no modification, no middleware injection on the subagent side.

### 2.2 Subagent Invocation (Task Tool)

When Jarvis calls `task(name="rubric_creator", task="Create a rubric for bot_id: 676be5cbab56400012077f4a")`:

```python
# deepagents/middleware/subagents.py line 335-336
_EXCLUDED_STATE_KEYS = {"messages", "todos", "structured_response"}
subagent_state = {k: v for k, v in runtime.state.items() if k not in _EXCLUDED_STATE_KEYS}
subagent_state["messages"] = [HumanMessage(content=description)]
```

The subagent receives:
- **System prompt:** Full RUBRIC_CREATOR_PROMPT (unchanged)
- **Messages:** Single HumanMessage with the task description
- **Tools:** `bot_context` + `rubrics` (from connector registry)
- **NO parent conversation history** — clean isolation by design

### 2.3 Bot Context Retrieval

```
rubric_creator calls bot_context tool with bot_id
    ↓ connector_to_tool() wraps BotContextConnector
BotContextConnector._invoke()
    ↓ HTTP GET
http://evaluations:8080/api/v1/bots/676be5cbab56400012077f4a/context
    ↓ Returns 200
{
  "bot_id": "676be5cbab56400012077f4a",
  "bot_name": "Wedding Bot",
  "organization_id": "...",
  "system_prompt": "<5,153 chars>",
  "tools": [<21 unique tools with full descriptions>],
  "knowledge_bases": [{"name": "Wedding KB", "type": "QNA", "document_count": 0}],
  "llm_config": {"provider": "openai", "model": "gpt-5.2"},
  "harness_context": {<v1 execution flow description>}
}
```

**Important:** The evaluations service endpoint `/api/v1/bots/{bot_id}/context` exists on the dev deployment (`http://evaluations:8080`) and returns a 200. However, this endpoint is NOT present in the local evaluations repo (`/Users/home/Repositories/evaluations/`). The deployed evaluations service has code not reflected in the local repo. The endpoint returns deduplicated tools (21, not the raw 46 in the DB).

**Environment on percy-service container:**
```
EVALUATION_SERVICE_URL=http://evaluations:8080
PLATFORM_URL=NOT SET
BOT_SERVICE_URL=NOT SET
```

---

## 3. What the Rubric Creator Actually Saw

### 3.1 The Wedding Bot System Prompt (5,153 chars)

This is the EXACT system_prompt returned by bot_context. It is stored in `tiledesk.bot_configurations` where `bot_id = ObjectId("676be5cbab56400012077f4a")`, in `ai_config.system_prompt`. Field `use_default_prompt` is `True`.

```
You are Indemn's Wedding Bot, dedicated to providing a seamless and delightful
experience for customers and prospects exploring wedding insurance. Your primary
goal is to guide users through the insurance process by delivering clear, accurate
information about Indemn's services and ensuring a smooth, hassle-free purchase journey.

Strict Flow Control:
Follow the instruction sets without assumptions, hallucinations, or deviation.

Parameter Validation Before Execution:
Each tool (function) has its own set of required parameters.
Before executing any function:
You must never execute any tool unless all its required parameters have been
explicitly and freshly confirmed from the user except when those values are
Supplied in the initial payload provided externally at the start of the session.
[...]

Flow Structure to Follow:
Initialization:
Execute @initial_conditions_insurance BEFORE any other processing.
[...]

CRITICAL: During event details collection phase only, when user provides
{{ event_date }}, execute @validate_date function FIRST [...]

Minimum Cancellation Budget Validation (CRITICAL - MUST ENFORCE): [...]

MANDATORY: When user requests email quote, automatically execute
@quote_follow_up first [...]
```

### 3.2 Directive Inventory

Every ALWAYS/NEVER/MUST/CRITICAL/MANDATORY directive in the system prompt:

| # | Directive | Keyword | Actually Universal? |
|---|-----------|---------|---------------------|
| 1 | "Follow the instruction sets without assumptions, hallucinations, or deviation" | Strict | **YES** |
| 2 | "always maintain a structured, professional, and user-friendly tone" | Always | **YES** |
| 3 | "Seek clarification when necessary instead of making assumptions" | — | **YES** |
| 4 | "must never execute any tool unless all required parameters have been explicitly confirmed" | MUST NEVER | **AMBIGUOUS** — applies to all tool calls, which are most responses |
| 5 | "Execute @initial_conditions_insurance BEFORE any other processing" | BEFORE | No — flow init only |
| 6 | "ensure all required parameters for each tool are collected" | ensure | No — tool execution only |
| 7 | "CRITICAL: During event details collection phase only, execute @validate_date FIRST" | CRITICAL | No — event details only |
| 8 | "Minimum Cancellation Budget Validation (CRITICAL - MUST ENFORCE)" | CRITICAL, MUST | No — budget only |
| 9 | "If not yet received, politely remind the user to complete the payment" | — | No — payment only |
| 10 | "CRITICAL: When user requests quote modification AND provides event_date, execute @validate_date FIRST" | CRITICAL | No — modification only |
| 11 | "EXECUTE @modify_quote when user requests changes following its built-in logic" | EXECUTE | No — modification only |
| 12 | "When a specific tool is suggested by the flow executor, execute ONLY that tool" | ONLY | **AMBIGUOUS** — applies to all suggested tools |
| 13 | "MANDATORY: When user requests email quote, execute @quote_follow_up first" | MANDATORY | No — email quote only |
| 14 | "Never assume success unless explicit confirmation (SECTION OMEGA) is received" | Never | No — payment only |

**Score: 3 clearly universal, 2 ambiguous, 9 clearly workflow-specific. All 14 use equally strong language.**

### 3.3 Tool Descriptions (21 tools)

Each tool has a description field (50-627 chars) and an output_instructions field (60-758 chars). The tools contain additional behavioral directives:

| Tool | Description Contains |
|------|---------------------|
| @human_handoff_slack_notification | "must ALWAYS execute FIRST when user requests an agent" |
| @get_insurance_quote | "Parameters must be collected one at a time" + conditional logic rules |
| @initial_conditions_insurance | "must be executed first in the following cases" |
| @Email Quote | "PREREQUISITE CHECK: can ONLY be used after @quote_follow_up" |
| @validate_date | "must be executed before @modify_quote" |
| @payment_validation | "For each missing parameter, ask the user ONE question at a time" |
| @event_details | "FIREARMS/WEAPONS HANDLING" logic, "Do not prompt venue related questions" |
| @contact_details | "Do not assume or hallucinate, make sure to prompt all the parameters" |

The tool descriptions are MORE workflow-specific instructions, all using strong directive language.

---

## 4. Why the Rubric Creator Produced 18 Rules

### 4.1 The RUBRIC_CREATOR_PROMPT's Instructions

The prompt tells the subagent (Step 2):
> "Read the system prompt and identify... Universal prohibitions (NEVER/DO NOT directives)... Universal requirements (ALWAYS/MUST directives)... Important: Only include ALWAYS/NEVER directives that are genuinely universal."

And (Step 3):
> "Add Standard Quality and Safety Rules: No hallucination, Stays in scope, No harmful content, Response coherence"

The filtering instruction at the bottom says:
> "Every rubric rule MUST make sense to check on every single response... Ask yourself: Would I check this rule on a greeting? On a factual question? On an off-topic request?"

### 4.2 What the LLM Actually Did

The rubric_creator:

1. **Fetched bot_context** ✅
2. **Read the 5,153-char system prompt** — found 14 directives using ALWAYS/NEVER/MUST/CRITICAL/MANDATORY
3. **Read 21 tool descriptions** — found additional behavioral directives
4. **Extracted rules from the directives** ✅ — this is what the prompt asked for
5. **Failed to rigorously apply the universal applicability filter** ❌

### 4.3 Why the Filter Failed

**The Wedding Bot's system prompt makes universal vs. situational distinction structurally hard:**

1. **Conflated language:** Universal rules ("don't hallucinate") and workflow rules ("execute @validate_date FIRST") both use MUST/NEVER/CRITICAL. No linguistic signal distinguishes them.

2. **Ambiguous middle ground:** "Parameter Validation Before Execution" (directive #4) is the FIRST behavioral rule in the prompt, presented as foundational. It applies to every tool call — which happens in most responses for this bot. The LLM can reasonably argue it's "universal" for this agent.

3. **Volume overwhelms filtering:** When you have 14 directives all using CRITICAL/MUST/MANDATORY plus 21 tool descriptions with more directives, the soft guidance ("aim for roughly 5-8") loses to the apparent importance of each directive.

4. **Tool descriptions reinforce specificity:** The 21 tool descriptions provide deep workflow knowledge that makes it easy to understand each directive and create a detailed rule for it. More knowledge = more detailed rules.

5. **The "5-8" is soft language:** "Aim for roughly" does not create a hard constraint. An LLM that sees 14 CRITICAL directives will prioritize coverage over count.

### 4.4 The Systemic Issue

This is NOT specific to the Wedding Bot. Any V1 bot with a detailed system prompt will exhibit the same pattern because:

- **V1 bot system prompts are workflow instruction manuals.** They mix "be professional" with "execute @payment_validation before @Payment Button Function." There's no structural separation.

- **The rubric_creator prompt assumes a clean separation exists.** Its Step 2 says "identify rules that define how the agent should ALWAYS behave" — but in a V1 prompt, "how the agent should ALWAYS behave" includes "ALWAYS execute @initial_conditions_insurance first."

- **The bot_context endpoint returns everything.** 5,153 chars of prompt + 21 tool descriptions with behavioral instructions. The rubric_creator is swimming in workflow specifics with only a few sentences of universal behavioral standards.

- **The RUBRIC_CREATOR_PROMPT's filtering mechanism is guidance, not structure.** It relies on the LLM's judgment to distinguish universal from situational. For clean prompts (like a simple FAQ bot), this works. For dense workflow prompts, it doesn't.

---

## 5. Potential Solutions

### 5.1 Prompt-Level Fixes (Minimum Viable)

Strengthen the RUBRIC_CREATOR_PROMPT in `percy-service/scripts/seed_jarvis_templates.py` (line 941):

**Hard cap instead of soft guidance:**
```
Current:  "Aim for roughly **5-8 rules**"
Proposed: "You MUST create exactly 3-6 rules. NEVER exceed 6. If you identify more
           candidates, consolidate or drop the least universal ones."
```

**Concrete self-check with examples:**
```
Current:  "Ask yourself: Would I check this rule on a greeting?"
Proposed: "MANDATORY SELF-CHECK: For each candidate rule, test it against these 3 messages:
           1. 'Hello, I'm interested in wedding insurance'
           2. 'Can you help me with my taxes?'
           3. 'I need to correct my phone number'
           If the rule doesn't meaningfully apply to ALL THREE, it is NOT universal
           and MUST NOT be in the rubric. Move it to test set criteria instead."
```

**Explicit tool description guidance:**
```
Add: "Tool descriptions contain workflow-specific logic for individual functions.
      Do NOT derive rubric rules from tool descriptions or tool-specific behaviors.
      Rubric rules come from the agent's PERSONA and UNIVERSAL BEHAVIORAL STANDARDS
      only — not from how individual tools should be executed."
```

**Negative examples from this failure:**
```
Add: "WRONG — these are NOT universal rubric rules (they are scenario criteria):
      - 'Agent validates state before generating quote' (only during quoting)
      - 'Agent enforces minimum cancellation budget' (only during budget collection)
      - 'Agent executes payment validation before payment button' (only during payment)
      - 'Agent follows flow initialization routing' (only at conversation start)
      These belong as success_criteria on the specific test scenarios that test them."
```

### 5.2 Architectural Fixes (Address the Systemic Issue)

**Option A: Pre-process the system prompt before the rubric_creator sees it.**

Add a step to the evaluation orchestrator that extracts ONLY universal behavioral content from the system prompt and passes a filtered version to the rubric_creator. The full prompt + tools go to the test_set_creator (which needs workflow details).

```
Jarvis orchestrator:
  1. Call bot_context → get full prompt + tools
  2. Extract universal behavioral rules from prompt (LLM call or heuristic)
  3. Spawn rubric_creator with ONLY the extracted universal content
  4. Spawn test_set_creator with the full prompt + tools
```

**Option B: Structurally separate the rubric_creator's input.**

Modify the bot_context connector (or add a variant) that returns only:
- The first paragraph (identity/persona)
- Sentences containing ALWAYS/NEVER that don't reference specific tools
- A list of tool NAMES (not descriptions)
- KB names (not content)

The rubric_creator would receive a simplified context that naturally produces universal rules.

**Option C: Two-pass rubric creation.**

First pass: Create candidate rules (current behavior).
Second pass: A separate LLM call filters the candidates through the universal applicability test with the concrete 3-message check. Only rules that pass all 3 survive.

**Option D: Fixed rubric template + customization.**

Instead of generating rubrics from scratch, provide a standard rubric template with 4-5 universal rules that apply to ALL agents:
1. No hallucination / uncertainty acknowledgment
2. Professional tone and clarity
3. Stays in scope / graceful error handling
4. No harmful content
5. (Optional) Consistent identity

Let the rubric_creator only ADD rules if the system prompt has genuinely universal NEVER/ALWAYS directives (like "NEVER provide medical advice"). This flips the default from "generate everything" to "start with the standard, add only if justified."

### 5.3 Recommendation

**Short-term: 5.1 (prompt fixes) + 5.2 Option D (fixed template).**

The prompt fixes are quick and will significantly improve results. Option D addresses the systemic issue by changing the paradigm from "generate universal rules" (hard for LLMs with dense prompts) to "use standard rules, customize minimally" (much easier).

**Medium-term: 5.2 Option C (two-pass)** as a safety net. Even with better prompts, some bots will produce edge cases. A filtering pass catches those.

---

## 6. Test Set Creator Issues (Secondary)

The test_set_creator has different but related problems:

### 6.1 Single-turn tests assuming mid-conversation context

The TEST_SET_CREATOR_PROMPT (line 676) says:
> "Single-turn items isolate specific behaviors for diagnostic purposes"
> "Prompt directive tests — For each ALWAYS/NEVER/MUST statement in the system prompt, create an item that specifically tests compliance"

The bot's system prompt says: "If {{ insurance_coverage }} is both, ask {{ alcohol_required }} and {{ budget }}". The test_set_creator creates: `"I'll go with liability coverage only"` — testing the conditional logic directive. But this message assumes the bot already knows the conversation context and coverage selection phase is active.

**Root cause:** The test_set_creator doesn't understand that V1 bots start from scratch for each test item. Single-turn items get NO prior context.

**Fix:** Add explicit guidance:
```
"CRITICAL: Single-turn tests start a BRAND NEW conversation with NO prior context.
The bot has never spoken to this user before. There is no active workflow, no
collected parameters, no selected coverage. If a behavior requires prior workflow
steps to be meaningful, it MUST be a multi-turn scenario, not a single-turn test."
```

### 6.2 Insufficient max_turns

The prompt says: "simple flows 4-6, full workflows 6-10, complex scenarios 5-8"

The Wedding Bot has a 12+ step workflow. The guidance of "6-10" for full workflows is too low.

**Fix:** Add workflow depth analysis:
```
"Before setting max_turns, count the workflow steps in the system prompt. Each
step typically requires 2 turns (agent asks + user responds). A 12-step workflow
needs at minimum 12 turns. Set max_turns to 1.5x the step count for the target
phase. Late-stage tests (payment, underwriting) in a deep workflow may need 15-20 turns."
```

### 6.3 Missing venue/initial payload context

Flow init scenarios test venue-specific routing but don't pass the required flags (cancellation_available, mandate_liability, mandate_cancellation).

**This may be an evaluation framework limitation** — does the scenario format support injecting initial payload? The current schema has `persona`, `initial_message`, and `max_turns` but no `initial_context` or `payload` field.

---

## 7. Access Patterns (For Next Session)

### 7.1 Querying Dev MongoDB

Local machine CANNOT reach dev MongoDB Atlas (IP whitelist). Must go through EC2:

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

**For complex scripts:** Write to local `/tmp/`, SCP to EC2, docker cp into container, execute:
```bash
scp -i /Users/home/Repositories/ptrkdy.pem /tmp/script.py ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com:/tmp/
ssh -i /Users/home/Repositories/ptrkdy.pem ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com \
  "sudo docker cp /tmp/script.py percy-service:/tmp/ && sudo docker exec percy-service python3 /tmp/script.py"
```

### 7.2 Testing Bot Context Endpoint

From within the percy-service container:
```python
import requests
resp = requests.get("http://evaluations:8080/api/v1/bots/676be5cbab56400012077f4a/context")
data = resp.json()
# Keys: bot_id, bot_name, organization_id, system_prompt, tools, knowledge_bases, llm_config, harness_context
```

### 7.3 Key Environment Variables (percy-service container)

```
EVALUATION_SERVICE_URL=http://evaluations:8080
MONGO_URL=<atlas connection string>
V1_MONGODB_DB=tiledesk
```

---

## 8. Key IDs Reference

| Entity | ID | Collection |
|--------|-----|-----------|
| Evaluation run | `0786fe77-067a-4f89-aea9-f921f12d37c9` | tiledesk.evaluation_runs |
| Rubric | `f3cf94bd-bba1-4aeb-9a94-24991cd1b496` | tiledesk.rubrics |
| Test set | `0e2ab005-51fb-4944-a61a-3f0ff8831f24` | tiledesk.test_sets |
| Bot (Wedding Bot) | `676be5cbab56400012077f4a` | tiledesk.faq_kbs |
| Project | `676be5cbab56400012077f03` | — |
| Organization | `676be5a7ab56400012077e7d` | — |
| Jarvis template | `jarvis_evaluation_v1` | tiledesk.platform_templates |

---

## 9. File Reference

| What | File | Key Lines |
|------|------|-----------|
| RUBRIC_CREATOR_PROMPT | `percy-service/scripts/seed_jarvis_templates.py` | 941-1168 |
| TEST_SET_CREATOR_PROMPT | same file | 676-938 |
| EVALUATION_JARVIS_PROMPT | same file | 401-673 |
| DeepAgentComponent (subagent spawning) | `percy-service/indemn_platform/components/deep_agent.py` | 213-243 (subagent config), 134-264 (full create_node) |
| BotContextConnector | `percy-service/indemn_platform/connectors/implementations/platform_api/evaluations.py` | 39-69 |
| Connector registry | `percy-service/indemn_platform/connectors/registry.py` | full file |
| Connector registration | `percy-service/indemn_platform/connectors/implementations/platform_api/__init__.py` | full file |
| V1AgentRepository | `percy-service/indemn_platform/repositories/v1_agent_repository.py` | 97-225 (get_agent) |
| percy-service API routes | `percy-service/indemn_platform/api/main.py` | 191-202 (route mounting) |
| Subagent task tool | `deepagents/middleware/subagents.py` (installed package) | 335-374 (task invocation), 275-280 (create_agent) |
| Subagent state isolation | same file | 335-336 (_EXCLUDED_STATE_KEYS) |

---

## 10. Corrected Understanding (vs Previous Audit)

| Claim from session 2026-02-23-a | Actual Finding |
|----------------------------------|----------------|
| "The problem is that the rubric_creator subagent is not following its own instructions" | The subagent IS following instructions. It correctly extracts ALWAYS/NEVER/MUST directives. The filter for universal applicability is guidance-level and fails against dense workflow prompts. |
| "Bot prompt was NOT found in bot_configurations" | Bot prompt IS in bot_configurations (5,153 chars in ai_config.system_prompt). Previous session may have had a query issue. |
| "V1 bot-service constructs the system prompt dynamically at runtime from tool descriptions" | The system prompt IS stored. Bot-service does add dynamic elements ({{flow_executor_suggested_tool}}, {{current_date}}) but the core 5,153-char prompt exists in the DB. |
| "46 tools (duplicates of ~23 unique)" | bot_context endpoint returns 21 deduplicated tools. The raw DB has 46 but the endpoint handles dedup. |
| Previous audit didn't examine what bot_context actually returns | Now verified: 200 response with system_prompt (5,153 chars), 21 tools, 1 KB, LLM config, harness_context |
