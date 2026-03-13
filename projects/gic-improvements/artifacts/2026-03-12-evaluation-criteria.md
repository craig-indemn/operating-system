---
ask: "Establish evaluation criteria, baseline metrics, and test design for each GIC improvement opportunity"
created: 2026-03-12
workstream: gic-improvements
session: 2026-03-12-b
sources:
  - type: mongodb
    description: "tiledesk.observatory_conversations — baseline metrics for each opportunity"
  - type: github
    description: "evaluations/ codebase — framework capabilities, rubric/test set structure"
---

# GIC Evaluation Criteria & Baseline Metrics

## Two Measurement Layers

### Layer 1: Evaluation Rubric (before/after agent changes)
Run the evaluation framework against the GIC bot before and after each change. Produces a weighted score per rule and overall. This tells us: **did the agent's behavior improve?**

### Layer 2: Observatory Monitoring (ongoing real conversations)
Track observatory metrics over time. This tells us: **are real customer outcomes improving?**

Both layers are needed — evaluation confirms the agent behaves correctly in controlled scenarios, observatory confirms it matters in production.

---

## Overall Baselines (Observatory)

| Metric | Current Baseline | Target Direction |
|--------|-----------------|-----------------|
| Autonomous resolution rate | 8.1% (300/3,701) | Increase |
| Total failure rate | 44% (1,615/3,701) | Decrease |
| Frustrated user rate | 7.8% (288/3,701) | Decrease |
| Average conversation depth | 13.0 turns | Decrease |
| Average self-served depth | 8.5 turns | Decrease |

---

## Per-Opportunity Evaluation Design

### Opportunity 5: Policy Number Parsing

**Observatory Baselines:**
| Metric | Baseline |
|--------|----------|
| API failure rate (missing_backend_data / external_api_calls) | 15.2% (486/3,198) |
| Policy_check path failure+partial rate | 27.0% (47/174) |
| Conversations with system_error:api_issue | 486 |

**Evaluation Rubric Rules:**

| Rule ID | Name | Severity | Pass Conditions | Fail Conditions |
|---------|------|----------|----------------|-----------------|
| POLICY_FORMAT_HANDLING | Handle common policy number formats | High | Bot extracts and looks up policy when user provides number with common prefixes ("policy#", "Policy:"), suffixes ("-0", "- 3"), or extra spaces | Bot fails to look up policy or returns "not found" when policy number is valid but formatted with common variations |
| POLICY_FAILURE_RECOVERY | Graceful handling of lookup failure | Medium | When lookup fails, bot offers to try again with cleaned number, asks user to verify, or offers alternative (handoff, email) | Bot gives up after single failure without offering recovery options |
| POLICY_DATA_DISPLAY | Display relevant policy information | Medium | When lookup succeeds, bot displays: status, insured name, payment info. If within 60 days of expiration, flags renewal. | Bot returns successful lookup but omits key fields the user likely needs |

**Test Cases (Single-Turn + Multi-Turn):**
- Clean policy number: "0185FL00184576" → should succeed
- With prefix: "policy#0185FL00184576" → should succeed
- With suffix: "0185FL00184576 - 3" → should succeed
- With prefix + suffix: "Policy Number: 0185FL00210200 - 0" → should succeed
- With label: "policy 0185FL00184576" → should succeed
- GL format: "GL 1131943D" → should succeed
- Multiple formats in one message: "can you check 0185FL00184576-3 and GL 1131943D"
- Invalid number: "12345" → should handle gracefully
- Multi-turn: user provides messy format, bot fails, user clarifies → bot should recover

**Monitoring Metrics (post-implementation):**
- `missing_backend_data` tag count (target: <5% of API calls, down from 15.2%)
- `system_error:api_issue` tag count
- `stages.tool_outcome: failure` for policy_check path (target: <10%, down from 27%)

---

### Opportunity 14: Bot Expectations Gap

**Observatory Baselines:**
| Metric | Baseline |
|--------|----------|
| Product inquiry bad outcome rate | 51% (437/860) |
| Product inquiry autonomous resolution rate | 13% (108/860) |
| Bad outcome avg depth | 10.6 turns |
| Bad outcome avg self-served depth | 10.2 turns |

**Evaluation Rubric Rules:**

| Rule ID | Name | Severity | Pass Conditions | Fail Conditions |
|---------|------|----------|----------------|-----------------|
| EXPECTATIONS_UPFRONT | Set expectations within first 2 responses | High | When user asks about a quote or product, bot explains within first 2 responses: (1) what it can do (collect info, answer questions), (2) what it can't do (generate quotes), (3) self-service alternative (portal URL) | Bot begins collecting information without first explaining what will happen with it, or collects 3+ turns of info before mentioning it can't generate quotes |
| PORTAL_ROUTING | Offer self-service portal option | High | Bot provides portal URL or self-service path as an option for quote submission, not just as a fallback | Bot only mentions portal after user explicitly asks, or never mentions it |
| COLLECTION_PURPOSE | State purpose of info collection | Medium | When collecting info, bot states it's gathering for a human representative and sets timeline expectation | Bot collects info without explaining why or what happens next |

**Test Cases (Multi-Turn Simulated):**
Personas that ask about quotes/products:
- "I need a quote for commercial auto in Florida" → bot should set expectations immediately
- "Do you have a market for a car carrier truck?" → bot should explain capabilities before collecting details
- "I need general liability for my business" → bot should offer portal option upfront
- "Can you quote me on workers comp?" → bot should be transparent about limitations
- Spanish-speaking personas (significant portion of GIC traffic): "necesito hacer una cotización para un comercial auto"

**Monitoring Metrics (post-implementation):**
- Product inquiry bad outcome rate (target: <35%, down from 51%)
- Product inquiry avg self-served depth for bad outcomes (target: <6 turns, down from 10.2)
- Product inquiry autonomous resolution rate (target: >20%, up from 13%)

---

### Opportunity 13: Missed Handoff Fallback

**Observatory Baselines:**
| Metric | Baseline |
|--------|----------|
| Missed handoffs | 618 (17% of real conversations) |
| CSR never joined | 238 |
| User went silent waiting | 403 |

**Evaluation Rubric Rules:**

| Rule ID | Name | Severity | Pass Conditions | Fail Conditions |
|---------|------|----------|----------------|-----------------|
| HANDOFF_FALLBACK | Offer alternatives when handoff fails | High | When handoff is triggered and no agent connects (simulated in eval), bot offers alternatives within reasonable time: leave contact info, email address, try again during business hours | Bot says "connecting you to an agent" and then goes silent, or conversation ends without alternatives |
| CONTACT_COLLECTION | Collect contact info before/during handoff | Medium | Bot collects user's name, email, or phone before or during handoff attempt so follow-up is possible even if handoff fails | Bot triggers handoff without collecting any contact info for follow-up |
| HANDOFF_TRANSPARENCY | Set expectations about handoff process | Medium | Bot explains what will happen: estimated wait time, what to do if nobody connects, that their info has been saved | Bot says "connecting you now" with no context about what to expect |

**Test Cases (Multi-Turn Simulated):**
Personas that trigger handoff scenarios:
- "I need to speak with someone" → bot should collect contact info before handoff
- User goes through product inquiry → reaches handoff point → no agent available → bot should offer alternatives
- "Can I talk to a live agent?" → bot should explain process and collect info
- After-hours handoff request → bot should explain availability and offer alternatives

Note: In evaluation, handoff tools fail gracefully (no humans), making this naturally testable.

**Monitoring Metrics (post-implementation):**
- `missed_handoff` outcome count (target: <400, down from 618)
- `csr_never_joined` conversations that still capture contact info (new metric to track)
- `user_silent_after_csr` count (target: <300, down from 403)

---

### Opportunity 7: After-Hours Detection

**Observatory Baselines:**
| Metric | Baseline |
|--------|----------|
| Out-of-hours handoff conversations | 69 |
| Avg depth before user finds out | 11.3 turns |
| Max depth before user finds out | 28 turns |

**Evaluation Rubric Rules:**

| Rule ID | Name | Severity | Pass Conditions | Fail Conditions |
|---------|------|----------|----------------|-----------------|
| AFTER_HOURS_DETECTION | Surface after-hours status early | High | If conversation occurs outside business hours (8:30AM-5:00PM ET Mon-Fri), bot mentions this within first 2 responses and offers alternatives (leave info, portal self-service, call back during hours) | Bot proceeds with full interaction for 3+ turns before revealing that no live agents are available |
| AFTER_HOURS_OPTIONS | Provide useful after-hours alternatives | Medium | Bot offers at least 2 alternatives: leave contact info for callback, use portal for self-service, email for non-urgent requests | Bot only says "offices are closed" without offering alternatives |

**Test Cases (Multi-Turn Simulated):**
- Simulated after-hours conversation: user asks about policy → bot should surface hours immediately
- After-hours quote request → bot should redirect to portal or collect info for next-day follow-up
- After-hours urgent request → bot should provide emergency contact or email

Note: Testing after-hours detection depends on whether the system prompt can check time, or if this requires flow logic. Test design may need adjustment based on implementation approach.

**Monitoring Metrics (post-implementation):**
- `out_of_hours_handoff` outcome count (target: <10, down from 69)
- Avg depth of after-hours conversations (target: <4, down from 11.3)

---

### Opportunity 3: Generic Opener

**Observatory Baselines:**
| Metric | Baseline |
|--------|----------|
| Current opener | "Hello, I am Fred! GIC's virtual chat assistant. How can I assist you today?" |
| Intent distribution — informational (catch-all) | 35% (1,857/5,330) |
| Autonomous resolution rate | 8.1% |

**Evaluation Rubric Rules:**

| Rule ID | Name | Severity | Pass Conditions | Fail Conditions |
|---------|------|----------|----------------|-----------------|
| OPENER_CAPABILITIES | Opener communicates capabilities | Low | First message names at least 3 specific things the bot can do (e.g., policy lookup, quote prep guidance, portal help, appetite questions) | First message is generic greeting with no indication of capabilities |

Note: The opener is a static `first_message` field in MongoDB, not generated by the LLM. Evaluation tests the downstream effect — does a better opener lead to more specific user intents and faster resolution?

**Test Cases:** Not directly testable as a rubric rule (static message). Measured via observatory monitoring.

**Monitoring Metrics (post-implementation):**
- Intent distribution shift: `informational` percentage (target: <30%, down from 35%)
- Autonomous resolution rate (target: >10%, up from 8.1%)
- Average depth for first 2 turns (do users get to their intent faster?)

---

### Opportunity 4: Yes/No Grammar Vulnerability

**Evaluation Rubric Rules:**

| Rule ID | Name | Severity | Pass Conditions | Fail Conditions |
|---------|------|----------|----------------|-----------------|
| DIRECT_REQUESTS | Use direct request phrasing | Low | Bot uses direct requests ("What is the address?" / "Please provide the policy number") when collecting information | Bot uses indirect questions that can be answered with yes/no ("Could you please provide the address?" / "Would you be able to share the policy number?") |

**Test Cases (Multi-Turn Simulated):**
- Persona that responds "yes" to indirect questions → bot should not ask indirect questions in the first place
- Information collection scenario → bot should use direct phrasing throughout

**Monitoring Metrics:** Contributes to overall depth reduction. No isolated metric.

---

### Opportunity 6: KB Gaps — WC Class Codes

**Observatory Baselines:**
| Metric | Baseline |
|--------|----------|
| Conversations tagged missing_knowledge | 109 |

**Evaluation Rubric Rules:**

| Rule ID | Name | Severity | Pass Conditions | Fail Conditions |
|---------|------|----------|----------------|-----------------|
| WC_CLASS_CODES | Answer WC class code questions | Medium | Bot provides specific appetite/eligibility information for common WC class codes (8810, construction, transportation, service industry) | Bot says "I couldn't find information" or gives a generic non-answer for common WC class codes |
| KB_ACCURACY | Knowledge base answers are accurate | Medium | Bot's answers match the information in the knowledge base without fabrication | Bot fabricates information not present in KB or contradicts KB content |

**Test Cases (Single-Turn):**
- "Do you have a market for class code 8810?" → should have answer after KB update
- "What WC class codes do you write for construction?" → should provide specific info
- "Can you write workers comp for a trucking company?" → should know appetite
- "What's your appetite for class code 5645?" → should have info or clearly state unavailable

**Monitoring Metrics (post-implementation):**
- `missing_knowledge` tag count (target: <50, down from 109)

---

## Evaluation Execution Plan

### Step 1: Create GIC Rubric
Create a rubric in the evaluations database with all rules above. Assign to GIC bot ID `66026a302af0870013103b1e`.

Rules by severity:
- **High (6 rules):** POLICY_FORMAT_HANDLING, EXPECTATIONS_UPFRONT, PORTAL_ROUTING, HANDOFF_FALLBACK, AFTER_HOURS_DETECTION, AFTER_HOURS_OPTIONS (added as medium but should be high given user impact)
- **Medium (5 rules):** POLICY_FAILURE_RECOVERY, POLICY_DATA_DISPLAY, COLLECTION_PURPOSE, CONTACT_COLLECTION, HANDOFF_TRANSPARENCY, WC_CLASS_CODES, KB_ACCURACY
- **Low (2 rules):** OPENER_CAPABILITIES, DIRECT_REQUESTS

### Step 2: Create GIC Test Set
Create test set with items covering all rules. Mix of:
- **Single-turn** (policy lookups, KB questions): ~15 items
- **Multi-turn simulated** (product inquiries, handoff scenarios, after-hours): ~10 scenarios with personas
- **Transcript evaluation** (replay real bad conversations): ~10 real conversation IDs from observatory

### Step 3: Run Baseline Evaluation
```
POST /api/v1/evaluations
{
  "bot_id": "66026a302af0870013103b1e",
  "rubric_id": "<created-rubric-id>",
  "test_set_id": "<created-test-set-id>",
  "eval_model": "anthropic:claude-sonnet-4-5-20250514",
  "concurrency": 3
}
```

### Step 4: Record Baseline Scores
Capture per-rule pass rates and overall weighted score. This becomes the benchmark.

### Step 5: Implement Changes (Groups A-D)

### Step 6: Run Post-Implementation Evaluation
Same rubric, same test set, same eval model. Compare per-rule pass rates.

### Step 7: Monitor Observatory
Track monitoring metrics weekly for 4 weeks post-implementation to confirm real-world impact.

---

## Projected Impact

| Opportunity | Conversations Affected | Current Failure | Target | Projected Improvement |
|---|---|---|---|---|
| #5 Policy Parsing | 486 API failures | 15.2% failure rate | <5% | ~330 conversations rescued from failure path |
| #14 Expectations Gap | 437 bad product inquiries | 51% bad outcome | <35% | ~140 fewer wasted conversations |
| #13 Handoff Fallback | 618 missed handoffs | 17% of all convos | <11% | ~220 conversations with better outcome |
| #7 After-Hours | 69 wasted convos | 11.3 avg depth | <4 avg depth | 69 users not wasting time |
| #6 KB Gaps | 109 missing knowledge | 109 conversations | <50 | ~60 questions answered |
| #3 Opener | All conversations | Generic | Specific | Hard to quantify; enables other improvements |
| #4 Grammar | Subset of convos | Indirect phrasing | Direct | Minor depth reduction |

**Combined projected impact on overall metrics:**
- Autonomous resolution rate: 8.1% → projected 12-15% (policy fixes + expectations routing to portal)
- Total failure rate: 44% → projected 35-38% (handoff fallback + policy fixes + after-hours)
- Frustrated user rate: 7.8% → projected 5-6% (fewer dead ends)
