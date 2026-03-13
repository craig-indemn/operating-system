---
ask: "Deep research on GIC agent — configuration, backend architecture, policy API, knowledge bases, and quantified baseline metrics for each improvement opportunity"
created: 2026-03-12
workstream: gic-improvements
session: 2026-03-12-a
sources:
  - type: mongodb
    description: "tiledesk.bot_configurations, faq_kbs, bot_tools, knowledge_bases, requests, messages, observatory_conversations for GIC org 65eb3f19e5e6de0013fda310"
  - type: github
    description: "operations_api (policy API), bot-service (tool execution)"
  - type: google-doc
    ref: "https://docs.google.com/document/d/1oiVuIhvTYHTkHuyfeluFNibE-AR3UeOx_3c0uRhyvLQ/edit"
    name: "Ryan's GIC UX Observation Report"
  - type: slack
    description: "Kyle's assignment message in mpdm-kwgeoghan--ryan--craig"
---

# GIC Agent Research: Configuration, Architecture & Baseline Metrics

## Agent Identity

| Field | Value |
|-------|-------|
| **Name** | GIC Underwriters Inc |
| **Bot ID** | `66026a302af0870013103b1e` |
| **Org ID** | `65eb3f19e5e6de0013fda310` |
| **Project ID** | `65eb3f65e5e6de0013fda4f9` |
| **Persona** | Fred — GIC's virtual chat assistant |
| **LLM** | OpenAI `gpt-4.1`, temperature 0.0 |
| **Pinecone namespace** | `65eb3f19e5e6de0013fda310` (org ID) |
| **Pinecone index** | `indemn` |

### Other Bots in GIC Project
| Bot | ID | Purpose |
|-----|----|---------|
| DEV - GIC | `66f137239afe08001360f7bb` | Development copy |
| GIC Underwriters Inc (DEV-Policy Lookup API) | `6870203be09a76001341743a` | Policy API testing |
| Fred, WC Intake for GIC | `695e6ec3922e070f5e0a9a3b` | Workers comp intake specialization |
| Workers Comp, Document Retriever | `69614bea922e070f5e10cde7` | WC document retrieval |
| Agent Service Voice Prototype #1 | `67d30ac0323aa30013f2d3f8` | Voice prototype |
| Agent Service Voice Prototype #2 | `69254bf059a39000136e10e3` | Voice prototype |

---

## System Prompt (Full)

The system prompt is ~3,000 words. Key sections:

### Persona Definition
> You are Fred, a GIC agent assistant designed to support insurance agents using the GIC underwriters broker portal with their insurance-related inquiries. Your primary goal is to provide specific, factual information about the platform's functionality and available insurance products to help agents understand their options, while ensuring that you do not make any general statements or provide advice beyond the scope of the knowledge base.

### Engagement Optimization
> Maximize meaningful user interaction through intelligent handoff management and proactive capability demonstration, balancing self-service success with appropriate human escalation timing.

### Flow Guidelines (ROOT CAUSE of slot-filling behavior)
> You will encounter JSON data containing an ACTION field that dictates your behavior:
> - If ACTION is "EXECUTE", invoke the specified function (FUNCTION NAME) with the provided PARAMETERS
> - If ACTION is "QUESTION", prompt the user to provide the required PARAMETER NAME, ensuring all necessary details are collected

**This instruction explicitly creates the one-question-per-turn pattern.** The system prompt tells Fred to collect parameters one at a time when the ACTION is "QUESTION".

### Post-Answer Behavior (ROOT CAUSE of excessive follow-ups)
> 2. After providing an answer or assistance, ask if there's anything else you can help with. Offer relevant information, suggestions, or additional assistance when appropriate.
> 3. If the user has no further questions, thank them for their time and remind them that they can reach out anytime.

### Function Capability Guardrails
- NEVER claim ability to "generate quotes," "create quotes," or "provide pricing"
- NEVER use language that implies real-time document creation
- Use "I can help you prepare" instead of "I can generate"
- Frame as "gathering details to help route your request"

### Quote Interaction Protocol
> 1. "I can help you understand what information you'll need for a quote and collect these so they are available to live representative."
> 2. "I don't generate quotes directly, but I can help you prepare for the quoting process."
> 3. Direct to proper channels using document routing knowledge base

### Knowledge Base Integration
- Access document routing FAQ using faq_retriever before initiating policy_lookup
- Access portal troubleshooting FAQ before activating human_handoff
- Format guidance as: "Based on your situation, here's what I recommend: [guidance]. Would you like me to [next step]?"

### Class Code Recognition
- Recognition patterns: "GL CLASS CODE [number]", "class code [number]", "[5-digit number] [description]"
- Processing: extract numeric code, search KB with multiple variations
- If no match: "I couldn't find specific information about class code [number] in my current knowledge base."

### Summary/Analysis Prompts
The bot has separate prompts for conversation summarization (used by CSR tools) and real-time conversation analysis/categorization. The analysis prompt categorizes into: Insurance Product Offerings, Policy Service Request, Technical Issue, Immediately Requested Handoff, or Other.

---

## Tools (3)

### 1. POLICY CHECK (REST API)
- **Type:** `rest_api`
- **Endpoint:** `POST https://ops.indemn.ai/v1/gic/policyDetails`
- **Body:** `{"agencyCode": "{{AgencyCode}}", "policyNumber": "{{ policyNumber }}"}`
- **Auth:** None (the operations_api handles auth to GIC's API)
- **Output instructions:** If valid response, answer user's question. If error, move to @policy_unavailable and ask for live agent confirmation. If isEnrolledInAutoPay is TRUE, mention Auto Pay enrollment.

### 2. policy_unavailable (Custom Tool)
- **Type:** `custom_tool`
- **Instructions:** If userConfirmationForLiveAgent is "true", proceed to @human_handoff. Else ask "is there anything I can help you?"

### 3. human_handoff
- **Type:** `human_handoff`
- **Description:** Handoff to human agent when user requests it. Must trigger as it's connected to other workflows.

### Tool Execution Flow (bot-service)
1. LLM decides to invoke tool based on conversation context
2. LLM extracts parameters from user message (e.g., policyNumber: "0185FL00184576")
3. `CustomTool._run()` → `ToolHandler.run()` builds session_parameters by merging:
   - init_parameters (session_id, project_id)
   - bot_config
   - LLM-extracted parameters
   - external_conversation_variables from Redis (where AgencyCode comes from)
4. `RestApiCallAction.execute()` substitutes placeholders in URL and body
5. `normalize_placeholders()` converts `{{ policyNumber }}` → `{policyNumber}`, then `.format()` substitutes
6. `convert_to_correct_type()` converts string values to appropriate types
7. API response returned to LLM for interpretation

**Critical: There is NO validation of policyNumber format before the API call.** The LLM extracts it from the user message and it's passed through as-is after placeholder substitution.

---

## Policy API Architecture

### Service Chain
```
Fred (bot-service) → operations_api → Granada Insurance external API
```

### operations_api (Pass-Through Proxy)
- **Repo:** `/Users/home/Repositories/operations_api`
- **Route:** `src/routes/gic-policy-details.ts`
- **Service:** `src/services/customers/gic_policy_details.ts`
- **Validation:** Joi schema — agencyCode (string|number, required), policyNumber (string, required)
- **Normalization:** agencyCode → String().trim(); policyNumber → .trim().toUpperCase()
- **NO format validation** — no stripping of prefixes ("policy#"), suffixes ("- 3"), or special characters

### External GIC API (Granada Insurance)
- **Base URL:** `https://services-uat.granadainsurance.com` (GIC_BASE_URL env var)
- **Endpoint:** `GET /v1/insuredpolicy/details?agencyCode={code}&policyNumber={number}`
- **Auth:** OAuth tokens via `POST /v1/token/generate` (Basic Auth with GIC_USERNAME/GIC_PASSWORD)
- **Token caching:** Redis key `gic_tokens` with TTL from API response
- **Token refresh:** Auto-refresh on 401, retry original request
- **Retry:** Exponential backoff on 500 errors (3 attempts, 1s/2s/4s)
- **SSL:** `rejectUnauthorized: false` (GIC UAT uses self-signed cert)

### Policy Number Parsing Issue (ROOT CAUSE)
The parsing chain:
1. **User types:** "policy#0185FL00184576 - 3" or "Policy Number: 0185FL00210200 - 0"
2. **LLM extracts:** "0185FL00184576 - 3" or "0185FL00210200 - 0" (may or may not clean it)
3. **bot-service:** No preprocessing — passes LLM output directly
4. **operations_api:** trim() + toUpperCase() only → "0185FL00184576 - 3"
5. **GIC API:** Receives the unclean string, returns 404

**Fix opportunity:** Add format normalization in operations_api — strip common prefixes, extract base policy number, handle endorsement suffixes.

---

## Knowledge Bases (3)

### 1. GIC KB (QNA)
- **ID:** `66fa34ca93b5a4001355ff5c`
- **Type:** QNA
- **Created:** 2024-09-30
- **Content:** Stored in Pinecone (vectorized), not in MongoDB. Contains Q&A pairs about GIC products, appetite, and procedures.
- **Gap identified by Ryan:** Missing WC class code coverage (8810 NOC), missing detailed carrier appetite data.

### 2. Broker Portal Troubleshooting FAQ (FILE)
- **ID:** `687bba3e357e3f001354857d`
- **Type:** FILE
- **Created:** 2025-07-19
- **Purpose:** Referenced in system prompt — "Access portal troubleshooting FAQ before activating human_handoff"

### 3. Email, Document Routing FAQ (FILE)
- **ID:** `687e4e4fc640870013a98928`
- **Type:** FILE
- **Created:** 2025-07-21
- **Purpose:** Referenced in system prompt — "Access document routing FAQ using faq_retriever before policy_lookup"

---

## Baseline Metrics (Jan-Mar 2026)

### Conversation Volume
| Metric | Value |
|--------|-------|
| Total closed conversations (all-time) | 40,747 |
| Billable conversations (depth > 2, not test, all-time) | 30,741 |
| Bot conversations (all-time) | 15,338 |
| Bot conversations (Jan-Mar 2026) | 2,148 |
| Monthly avg (Oct 2025-Mar 2026) | ~1,450 |

### Monthly Breakdown (Recent)
| Month | Conversations | Avg Depth | With Bot |
|-------|--------------|-----------|----------|
| 2026-03 (partial) | 684 | 12.7 | 321 |
| 2026-02 | 1,769 | 13.2 | 889 |
| 2026-01 | 1,835 | 12.9 | 938 |
| 2025-12 | 1,375 | 12.4 | 763 |
| 2025-11 | 1,290 | 13.1 | 650 |
| 2025-10 | 1,761 | 13.4 | 421 |

### Depth Distribution (Jan-Mar 2026 bot conversations)
| Depth Range | Count | % |
|-------------|-------|---|
| 3-4 | 770 | 36% |
| 5-7 | 472 | 22% |
| 8-11 | 466 | 22% |
| 12-15 | 162 | 8% |
| 16-19 | 97 | 5% |
| 20-29 | 127 | 6% |
| 30+ | 54 | 3% |

### Observatory Outcomes (5,330 analyzed conversations)
| Outcome | Count | % |
|---------|-------|---|
| Success | 1,695 | 32% |
| Excluded | 1,629 | 31% |
| Failure | 1,115 | 21% |
| Partial | 549 | 10% |
| Unknown | 331 | 6% |

### Observatory System Tags (frequency across all GIC conversations)
| Tag | Count | Interpretation |
|-----|-------|---------------|
| autonomously_handled | 3,217 | Bot resolved without human |
| external_api_calls | 3,198 | Policy API was called |
| handoff_needed_ever | 2,110 | Required human at some point |
| handoff_completed | 1,395 | Successfully transferred to human |
| timeout | 845 | Conversation timed out |
| missed_handoff | 643 | Handoff needed but not completed |
| missing_backend_data | 486 | API returned no data |
| system_error:api_issue | 486 | API call failed |
| user_silent_after_csr | 456 | User left after CSR joined |
| user_disengaged_after_handoff | 405 | User left during/after handoff |
| early_handoff | 340 | Handed off prematurely |
| csr_never_joined | 238 | Handoff triggered but no agent available |
| missing_knowledge | 109 | KB gap identified |
| out_of_hours_handoff | 75 | Handoff attempted outside business hours |
| system_error:model_issue | 11 | LLM error |

### Intent Distribution
| Intent | Count | % |
|--------|-------|---|
| informational | 1,857 | 35% |
| service_request | 1,528 | 29% |
| product_inquiry | 860 | 16% |
| handoff_request | 804 | 15% |
| technical | 281 | 5% |

### Message-Level Pattern Counts (Jan-Mar 2026 bot conversations)
| Pattern | Count | Context |
|---------|-------|---------|
| "How can I assist you today" | 4,655 | Generic opener on ~every conversation |
| "Could you please provide" / "Would you be able to" | 891 | Yes/no grammar vulnerability |
| "Thank you for providing/confirming/sharing" | 814 | Unnecessary acknowledgment filler |
| Handoff messages ("transferred to live agent") | 999 | 46% of bot conversations |
| Messages containing policy numbers | 602 | Policy lookup attempts |
| Policy lookup failure messages | 83 | ~14% of policy-related conversations |
| After-hours notifications | 35 | "Offices currently closed" messages |

---

## Improvement Opportunities — Root Cause & Baseline

### Opportunity 1: Reduce Slot-Filling Turns (Ryan #1)
- **Behavior:** Bot asks one question per turn — vehicle count, then state, then business name
- **Root cause:** System prompt flow guidelines explicitly instruct: "If ACTION is 'QUESTION', prompt the user to provide the required PARAMETER NAME" — one parameter at a time
- **Baseline:** Average conversation depth is 12.7-13.2 messages. 36% of conversations are depth 3-4 (likely abandoned due to friction)
- **Fix:** Modify system prompt to front-load required fields in a single message
- **Layer:** System prompt

### Opportunity 2: Tone — Too Formal, Excessive Acknowledgment (Ryan #2, #3, #6)
- **Behavior:** "Thank you for providing the business name. To check the status..." — 47 words for 1 ask
- **Root cause:** System prompt persona is generic, no register-matching instruction. Post-answer behavior explicitly says "ask if there's anything else" and "thank them for their time"
- **Baseline:** 814 "Thank you for providing/confirming" messages across 2,148 conversations = ~38% of conversations have unnecessary filler
- **Fix:** Rewrite persona section to match producer shorthand, remove affirmation openers, eliminate post-turn pleasantries
- **Layer:** System prompt (persona definition)

### Opportunity 3: Generic Opener (Ryan #4)
- **Behavior:** "Hello, I am Fred! GIC's virtual chat assistant. How can I assist you today?"
- **Root cause:** No specific opener instruction in system prompt — defaults to generic
- **Baseline:** 4,655 "How can I assist you today" messages = effectively 100% of conversations use this opener
- **Fix:** Add specific opening message that names GIC's supported intents (policy lookup, quote submission, appetite questions, cancellations, certificate requests)
- **Layer:** System prompt (first-turn utterance)

### Opportunity 4: Yes/No Grammar Vulnerability (Ryan #7)
- **Behavior:** "Could you please provide the address?" → user responds "yes" (grammatically correct non-answer)
- **Root cause:** System prompt uses polite question constructions throughout. No instruction to use direct requests
- **Baseline:** 891 "could you please provide" / "would you be able to" messages across 2,148 conversations
- **Fix:** Add system prompt instruction to replace indirect questions with direct requests ("What's the address?" not "Could you provide the address?")
- **Layer:** System prompt

### Opportunity 5: Policy Number Parsing (Ryan #13, Craig #18)
- **Behavior:** "policy#0185FL00184576 - 3" fails, "0185FL00184576" succeeds
- **Root cause:** Three-layer gap:
  1. **LLM:** Extracts policy number from user message but may include prefixes/suffixes
  2. **bot-service:** No validation or preprocessing of extracted parameter
  3. **operations_api:** Only does trim() + toUpperCase(), passes unclean string to GIC API
- **Baseline:** 602 messages with policy numbers, 83 lookup failure messages = ~14% failure rate. Observatory tags show 486 "missing_backend_data" and 486 "system_error:api_issue" events
- **Fix:** Add format normalization in operations_api: strip "policy#", "policy:", extract base number before "-" suffix, validate expected format (e.g., regex for GIC policy patterns like `\d{4}FL\d{8}`)
- **Layer:** operations_api service + optionally system prompt (instruct bot to clean policy number before tool call)

### Opportunity 6: Knowledge Base Gaps — WC Class Codes (Ryan #5)
- **Behavior:** "No direct FAQ entry" for WC class code 8810 NOC
- **Root cause:** GIC KB (QNA type) lacks WC class code entries. The system prompt has class code recognition logic but the KB doesn't have matching content
- **Baseline:** Observatory shows 109 conversations tagged "missing_knowledge"
- **Fix:** Add WC class code appetite data to the GIC KB, particularly for construction-adjacent, habitational, transportation, and service industry codes
- **Layer:** Knowledge base content

### Opportunity 7: After-Hours Detection (Ryan #11)
- **Behavior:** Bot completes full intake flow, only shows "offices currently closed" at the end
- **Root cause:** No time check at conversation initiation. After-hours message is triggered by the handoff flow, not proactively
- **Baseline:** 35 after-hours notifications detected in messages, 75 "out_of_hours_handoff" events in observatory
- **Fix:** Add time check to system prompt or flow logic — if outside 8:30AM-5:00PM ET Mon-Fri, surface immediately with options
- **Layer:** System prompt + possibly flow logic

### Opportunity 8: Proactive Constraint Surfacing (Ryan #10)
- **Behavior:** Bot collects 4 turns of info for commercial auto delivery, then human discovers $500K max limit
- **Root cause:** System prompt says to gather info for handoff but doesn't instruct to check known constraints first. KB may have appetite data but bot doesn't proactively surface limits
- **Baseline:** 340 "early_handoff" events suggest conversations where handoff happened prematurely; 643 "missed_handoff" events where needed handoff didn't happen
- **Fix:** Add system prompt instruction: before intake, check KB for known constraints on the requested coverage type and surface them
- **Layer:** System prompt

### Opportunity 9: "Thank You" False Closure (Ryan #15)
- **Behavior:** "Thank you" treated as session-ending signal
- **Root cause:** System prompt says "If the user has no further questions, thank them for their time" — creates reciprocal closure pattern. No explicit instruction to NOT treat thanks as closure
- **Baseline:** Needs targeted measurement — 845 "timeout" events in observatory may include premature closures
- **Fix:** Add explicit instruction: don't auto-close on thanks alone, require explicit closure or confirm "Anything else?"
- **Layer:** System prompt

### Opportunity 10: Renewal/Expiration Date Not Surfaced (Ryan #14)
- **Behavior:** Policy lookup shows premium and balance but not expiration date or renewal status
- **Root cause:** The policy API response from GIC likely includes this data, but the bot's output instructions don't mention displaying it. Instructions only say "answer the user's question based on the data" and mention AutoPay
- **Baseline:** Part of the 602 policy-number-containing conversations. Specifically impacts renewal inquiries
- **Fix:** Add explicit output instruction: "Always display effective date, expiration date, and renewal status. If within 60 days of expiration, flag it"
- **Layer:** Tool output instructions (POLICY CHECK tool)

### Opportunity 11: Agent Portal/Email Routing (Ryan #12)
- **Behavior:** Bot references portal or email without including the URL
- **Root cause:** Email/Document Routing FAQ KB exists but may not include portal URLs in its content. System prompt doesn't instruct to always include self-service links
- **Baseline:** Part of service_request intent (1,528 conversations)
- **Fix:** Ensure KB contains portal URLs; add system prompt instruction to always include portal URL when routing
- **Layer:** Knowledge base + system prompt

### Opportunity 12: "True" Boolean UI Bug (Ryan #8)
- **Behavior:** "true" appears as user message in chat
- **Root cause:** Front-end chat widget passing boolean values as message strings
- **Baseline:** Low frequency, observed in 1 of 14 reviewed conversations
- **Fix:** Front-end fix in point-of-sale or middleware-socket-service
- **Layer:** Front-end (not agent-level)

### Opportunity 13: Missed Handoffs
- **Behavior:** Handoff needed but never completed
- **Root cause:** CSR not available, or handoff flow not triggered properly
- **Baseline:** 643 "missed_handoff" events, 238 "csr_never_joined" events in observatory
- **Fix:** Improve handoff reliability; add fallback messaging when no CSR available
- **Layer:** Flow logic + platform configuration

---

## Architecture Reference

### Message Flow
```
Producer (browser) → point-of-sale widget → middleware-socket-service → bot-service /chat
                                                                           ↓
                                                                    LangGraph agent
                                                                           ↓
                                                              Tool calls (POLICY CHECK)
                                                                           ↓
                                                              operations_api /v1/gic/policyDetails
                                                                           ↓
                                                              Granada Insurance external API
```

### Key File Locations
| Component | Location |
|-----------|----------|
| Bot configuration | MongoDB `tiledesk.bot_configurations` (bot_id: `66026a302af0870013103b1e`) |
| System prompt | Same document, `ai_config.system_prompt` field |
| Tools | MongoDB `tiledesk.bot_tools` (3 tools linked to bot_id) |
| Knowledge bases | MongoDB `tiledesk.knowledge_bases` + Pinecone namespace `65eb3f19e5e6de0013fda310` |
| Policy API route | `/Users/home/Repositories/operations_api/src/routes/gic-policy-details.ts` |
| Policy API service | `/Users/home/Repositories/operations_api/src/services/customers/gic_policy_details.ts` |
| Tool execution | `/Users/home/Repositories/bot-service/app/services/tools/agent_tools.py` |
| REST API call handler | `/Users/home/Repositories/bot-service/app/services/tools/tool_execution.py` |
| Placeholder substitution | `/Users/home/Repositories/bot-service/app/utils/utils.py` |
| Agent graph | `/Users/home/Repositories/bot-service/app/services/graphs/bot_agent_graph.py` |
| Observatory data | MongoDB `tiledesk.observatory_conversations` (scope.customer_id: `65eb3f19e5e6de0013fda310`) |
