# GIC Agent Improvements — End-to-End Plan

## Context

GIC Underwriters' AI agent "Fred" (bot ID `66026a302af0870013103b1e`) handles ~1,500 conversations/month but only resolves 8.1% autonomously. 44% of conversations end in failure (missed handoffs, timeouts, abandonment). Through observatory data analysis and actual conversation transcript review, we identified 7 improvement opportunities with quantified baselines. This plan covers the full lifecycle: evaluation setup → baseline → implementation → post-implementation evaluation → production deployment → monitoring → GIC reporting.

**Project context lives in:** `projects/gic-improvements/` (INDEX.md, HANDOFF.md, artifacts/)

---

## Phase 1: Evaluation Setup

### 1.1 Craig creates test agent (MANUAL — Craig does this)
- Copy production bot `66026a302af0870013103b1e` in copilot-dashboard to create a test agent
- Record the new test bot ID — all evaluations run against this bot
- This prevents evaluation traffic from affecting production conversations/metrics

### 1.2 Create GIC evaluation rubric
**API:** `POST /api/v1/rubrics` (evaluations service, port 8002)

Create rubric with `agent_id` = test bot ID, containing 13 rules:

**High severity (6 rules):**
- `POLICY_FORMAT_HANDLING` — Handle common policy number format variations
- `EXPECTATIONS_UPFRONT` — Set expectations within first 2 responses for product/quote inquiries
- `PORTAL_ROUTING` — Offer self-service portal option proactively
- `HANDOFF_FALLBACK` — Offer alternatives when handoff fails
- `AFTER_HOURS_DETECTION` — Surface after-hours status within first 2 responses
- `AFTER_HOURS_OPTIONS` — Provide useful after-hours alternatives

**Medium severity (5 rules):**
- `POLICY_FAILURE_RECOVERY` — Graceful recovery when policy lookup fails
- `POLICY_DATA_DISPLAY` — Display relevant policy fields including expiration
- `COLLECTION_PURPOSE` — State purpose of information collection
- `CONTACT_COLLECTION` — Collect contact info before/during handoff
- `HANDOFF_TRANSPARENCY` — Set expectations about handoff process
- `WC_CLASS_CODES` — Answer WC class code questions from KB
- `KB_ACCURACY` — Knowledge base answers are accurate

**Low severity (2 rules):**
- `OPENER_CAPABILITIES` — Opener communicates specific capabilities
- `DIRECT_REQUESTS` — Use direct request phrasing, not indirect questions

Full pass/fail conditions documented in `artifacts/2026-03-12-evaluation-criteria.md`.

### 1.3 Create GIC test set
**API:** `POST /api/v1/test-sets` (evaluations service)

Create test set with `agent_id` = test bot ID, containing:

**Single-turn items (~15):**
- Policy lookups with various formats: clean, with prefix, with suffix, with both, GL format, invalid
- WC class code questions: 8810, construction, trucking, service industry
- KB questions: portal navigation, document routing, email contacts

**Multi-turn scenario items (~10):**
- Product inquiry personas (English + Spanish): commercial auto quote, GL quote, WC quote
- Handoff scenarios: explicit agent request, handoff after failed lookup, handoff that times out
- After-hours scenarios: user arrives outside business hours with policy question, quote request
- Information collection: bot should state purpose and set expectations

**Transcript items (~10):**
- Select 10 real conversation IDs from observatory with known bad outcomes for regression testing
- Mix: policy lookup failures, product inquiry dead ends, missed handoffs

### 1.4 Run baseline evaluation
**API:** `POST /api/v1/evaluations`
```json
{
  "bot_id": "<test-bot-id>",
  "test_set_id": "<created-test-set-id>",
  "rubric_id": "<created-rubric-id>",
  "eval_model": "anthropic:claude-sonnet-4-5-20250514",
  "concurrency": 3
}
```

Record baseline scores:
- Overall weighted score
- Per-rule pass rates
- Per-severity breakdown (high/medium/low)

Save as artifact: `artifacts/2026-MM-DD-baseline-evaluation-results.md`

---

## Phase 2: Implementation

Four implementation groups, ordered by leverage and independence.

### 2.1 Group B — Policy Number Parsing (Opportunity #5)
**Repo:** `operations_api`
**File:** `src/services/customers/gic_policy_details.ts`

Changes:
- Add `normalizePolicyNumber()` function before the API call
- Strip common prefixes: "policy#", "policy:", "policy number:", "pol#"
- Strip endorsement suffixes: "- 0", "-3", " - 0" (everything after last hyphen preceded by space)
- Remove extra whitespace
- Validate against known GIC format patterns (e.g., `\d{4}FL\d{8}`, `GL \d+[A-Z]?`)
- Keep existing `trim().toUpperCase()`

**Also (bundle #10):** Update POLICY CHECK tool output instructions in MongoDB `bot_tools` to include: "Always display effective date, expiration date, and renewal status if available in the response"

**Test:** Unit tests for `normalizePolicyNumber()` with all format variations. Integration test calling the endpoint with dirty policy numbers.

### 2.2 Group A — System Prompt Changes (Opportunities #3, #4, #7, #14)
**Location:** MongoDB `tiledesk.bot_configurations` → `ai_config.system_prompt` for test bot, then production bot

Changes to system prompt:
1. **Expectations gap (#14):** Add section at top of flow guidelines:
   > When a user asks about obtaining a quote, pricing, or submitting new business: IMMEDIATELY (within your first response) explain that you cannot generate quotes directly, but you can (a) collect information to pass to a live representative, or (b) direct them to the GIC agent portal at [URL] to submit directly. Let the user choose their path before collecting any information.

2. **After-hours (#7):** Add section:
   > If the current time is outside business hours (Monday-Friday 8:30 AM - 5:00 PM Eastern), inform the user immediately in your first response. Offer alternatives: leave contact information for a callback, use the portal for self-service, or return during business hours.

3. **Direct requests (#4):** Add to flow guidelines:
   > When collecting information from users, use direct requests ("What is the policy number?") rather than indirect questions ("Could you please provide the policy number?"). Never phrase information requests as yes/no questions.

4. **Opener (#3):** Update `first_message.text` in `bot_configurations` (and/or `distributions` if overridden):
   > Hi, I'm Fred — GIC's virtual assistant. I can help with: policy status & payments, quote submission guidance, coverage & appetite questions, or portal support. What do you need help with?

   Check both locations:
   - `bot_configurations` field: `first_message.text` (bot-level default)
   - `distributions` collection for distribution ID `667b9bb696b11e957d9830a9` (widget-level override takes precedence)

### 2.3 Group C — Knowledge Base Content (Opportunity #6, bundle #11)
**Location:** GIC KB (QNA type, ID `66fa34ca93b5a4001355ff5c`) via copilot-dashboard or KB API

Changes:
- Add WC class code appetite entries for common codes (8810 NOC, construction, transportation, service industry)
- Add portal URLs to relevant FAQ entries
- Ensure email contacts (quote@gicunderwriters.com, payments@gicunderwriters.com) are in routing FAQ entries

**Requires:** Craig to provide or confirm the actual WC appetite data and class codes GIC writes.

### 2.4 Group D — Handoff Fallback (Opportunity #13)
**Location:** System prompt additions + possibly bot-service flow logic

System prompt addition:
> If you have triggered a handoff to a live agent and the user appears to still be waiting (no agent has joined after your handoff message): offer to collect their name, phone number, and email so a representative can follow up. Provide the option to email their request to [appropriate GIC email] or try again during business hours. Never let the conversation end silently after a failed handoff.

**Note:** This is prompt-level first. If the bot can't detect that a handoff has failed (because it doesn't receive feedback), this may need flow-level changes in bot-service. Test in evaluation first — the eval harness naturally simulates failed handoffs since no humans are available.

---

## Phase 3: Post-Implementation Evaluation

### 3.1 Apply changes to test agent
Apply all Group A-D changes to the test bot (not production):
- Update system prompt in test bot's `bot_configurations.ai_config.system_prompt`
- Update first_message in test bot's config
- Update tool output instructions for test bot's POLICY CHECK tool
- KB changes apply to the shared KB (may need separate test KB — confirm with Craig)
- Policy parsing code change in operations_api applies globally (feature flag or test endpoint if needed)

### 3.2 Run post-implementation evaluation
Same rubric, same test set, same eval model as baseline:
```json
{
  "bot_id": "<test-bot-id>",
  "test_set_id": "<same-test-set-id>",
  "rubric_id": "<same-rubric-id>",
  "eval_model": "anthropic:claude-sonnet-4-5-20250514",
  "concurrency": 3
}
```

### 3.3 Compare results
Generate comparison artifact:
- Per-rule pass rate: baseline vs post-implementation
- Overall weighted score change
- Per-severity breakdown change
- Identify any regressions

Save as artifact: `artifacts/2026-MM-DD-post-implementation-evaluation-results.md`

### 3.4 Iterate if needed
If any rules regress or don't improve as expected, adjust implementation and re-run.

---

## Phase 4: Production Deployment

### 4.1 Deploy operations_api change
- PR for policy number normalization in operations_api
- Deploy to production

### 4.2 Apply prompt/config changes to production bot
- Update production bot `66026a302af0870013103b1e` system prompt
- Update production bot first_message
- Update production bot tool output instructions
- KB content already shared (unless we created a separate test KB)

### 4.3 Snapshot observatory metrics at deployment time
Record exact counts at deployment moment for all monitoring metrics so we have a clean before/after boundary.

---

## Phase 5: Monitoring (4 weeks post-deployment)

### 5.1 Weekly observatory queries
Run these queries weekly for 4 weeks and record results:

**Overall health:**
- Autonomous resolution rate (baseline: 8.1%)
- Total failure rate (baseline: 44%)
- Frustrated user rate (baseline: 7.8%)
- Average conversation depth (baseline: 13.0)

**Per-opportunity metrics:**
- Policy API failure rate: `missing_backend_data` / `external_api_calls` (baseline: 15.2%)
- Product inquiry bad outcome rate (baseline: 51%)
- Product inquiry avg self-served depth for bad outcomes (baseline: 10.2)
- Missed handoff count (baseline: 618)
- Out-of-hours handoff count (baseline: 69)
- Out-of-hours avg depth (baseline: 11.3)
- Missing knowledge count (baseline: 109)

### 5.2 Weekly monitoring artifact
Save each week's data as artifact: `artifacts/2026-MM-DD-monitoring-week-N.md`

---

## Phase 6: GIC Report

### 6.1 Generate improvement report
Create a PDF report for GIC using the markdown-pdf skill, containing:

1. **Executive Summary** — what we changed and the bottom-line impact
2. **Methodology** — evaluation framework, observatory monitoring, baseline/post metrics
3. **Opportunity Analysis** — for each implemented opportunity:
   - What the problem was (with real conversation examples)
   - What we changed
   - Evaluation score improvement (before/after rubric scores)
   - Production impact (observatory metric changes over 4 weeks)
4. **Overall Impact Dashboard** — key metrics before/after:
   - Autonomous resolution rate
   - Failure rate
   - Frustrated user rate
   - Average conversation depth
   - Policy lookup success rate
5. **Projections** — projected annual impact based on observed improvements
6. **Recommendations** — parked opportunities for future consideration

### 6.2 Deliver report
Share with GIC stakeholders. Format: Indemn-branded PDF.

---

## Session Boundaries

This work will span multiple sessions. Each session should:
1. Start by reading `projects/gic-improvements/HANDOFF.md`
2. Pick up from the current phase
3. End by updating HANDOFF.md and INDEX.md, committing changes

**Estimated session breakdown:**
- Session 3: Phase 1 (create rubric, test set, run baseline) — evaluations service must be running
- Session 4: Phase 2 (implementation groups B and A)
- Session 5: Phase 2 continued (groups C and D) + Phase 3 (post-implementation eval)
- Session 6: Phase 4 (production deployment) + Phase 5 start (monitoring)
- Sessions 7-9: Phase 5 (weekly monitoring check-ins)
- Session 10: Phase 6 (GIC report)

---

## Open Questions to Resolve

1. **Test bot ID** — Craig creates this manually, records the ID
2. **WC appetite data** — Craig needs to provide or confirm what class codes/appetite data to add to KB
3. **GIC business hours** — assumed 8:30AM-5:00PM ET Mon-Fri, need confirmation
4. **Portal URL** — exact URL for the GIC agent portal self-service submission
5. **Policy number formats** — all valid formats across GIC carriers for validation regex
6. **KB isolation** — do we need a separate test KB, or can we update the shared KB during testing?
7. **Operations API feature flag** — can we test the parsing change without affecting production, or do we deploy and test together?
8. **Handoff timeout detection** — can the bot detect when a handoff has failed (no CSR joined), or does this need bot-service changes?

---

## Key References

- **Project:** `projects/gic-improvements/` (INDEX.md, HANDOFF.md, artifacts/)
- **Production bot:** `66026a302af0870013103b1e`
- **Distribution:** `667b9bb696b11e957d9830a9`
- **Observatory query filter:** `{"scope.customer_id": "65eb3f19e5e6de0013fda310"}`
- **Evaluations API:** port 8002, `POST /api/v1/rubrics`, `POST /api/v1/test-sets`, `POST /api/v1/evaluations`
- **Policy API source:** `operations_api/src/services/customers/gic_policy_details.ts`
- **System prompt location:** MongoDB `tiledesk.bot_configurations` → `ai_config.system_prompt`
- **First message location:** `bot_configurations.first_message.text` (bot-level) or `distributions.first_message.text` (widget override, takes precedence)
- **Evaluation criteria detail:** `artifacts/2026-03-12-evaluation-criteria.md`
- **Opportunity detail:** `artifacts/2026-03-12-opportunity-prioritization.md`
