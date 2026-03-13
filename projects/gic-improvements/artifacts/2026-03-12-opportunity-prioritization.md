---
ask: "Prioritize GIC agent improvement opportunities based on real customer impact using observatory data and actual conversation analysis"
created: 2026-03-12
workstream: gic-improvements
session: 2026-03-12-b
sources:
  - type: mongodb
    description: "tiledesk.observatory_conversations — outcome breakdowns, system tags, intent distributions, resolution paths, tool outcomes for GIC org 65eb3f19e5e6de0013fda310"
  - type: mongodb
    description: "tiledesk.messages — actual conversation transcripts for product inquiries, policy lookups, service requests"
---

# GIC Opportunity Prioritization

## Observatory Baseline (Official Data)

**3,701 real conversations** (5,330 total minus 1,629 no_interaction):

| Outcome | Count | % | Customer Impact |
|---------|-------|---|-----------------|
| resolved_with_handoff | 1,395 | 38% | Resolved, but needed a human |
| missed_handoff | 618 | 17% | User needed help, didn't get it |
| partial_then_left | 549 | 15% | Got partial answer, gave up |
| unknown | 331 | 9% | Can't tell |
| resolved_autonomous | 300 | 8% | Bot handled it fully |
| unresolved_timeout | 248 | 7% | Complete dead end |
| unresolved_abandoned | 180 | 5% | User walked away |
| out_of_hours_handoff | 69 | 2% | Tried to hand off, nobody there |

**Key metrics:**
- Autonomous resolution rate: **8%** (300/3,701)
- Total failure rate: **44%** (missed_handoff + partial + timeout + abandoned + out_of_hours)
- Average depth: **13.0 turns**
- Average self-served depth: **8.5 turns**
- Frustrated users: **288 (7.8%)**

---

## Active Opportunities

### Opportunity 5: Policy Number Parsing (HIGH LEVERAGE)
- **Impact:** 486 out of 3,198 conversations with API calls had data failures — **15% failure rate**
- **Downstream:** 316 required a human to do what the bot should have done, 99 missed handoff entirely, 17 abandoned, 14 left after partial, 5 timed out
- **135 conversations (28% of failures) ended in complete failure** for the customer
- **Root cause:** Three-layer gap — LLM extraction includes prefixes/suffixes, bot-service no validation, operations_api only does trim()+toUpperCase()
- **Fix:** Format normalization in operations_api — strip "policy#", extract base number before "-" suffix, validate format
- **Layer:** operations_api code change
- **Measurement:** `missing_backend_data` and `system_error:api_issue` tag counts should decrease; `stages.tool_outcome: failure` for policy_check should decrease

### Opportunity 14: Bot Expectations Gap (HIGH LEVERAGE)
- **Impact:** 437 product inquiry conversations end in bad outcomes (51% of 860 product inquiries)
- **What happens:** Bot collects 20+ turns of info for quotes it can't generate, doesn't tell users upfront what will happen. Users ask "now what do I do?" after providing everything.
- **Evidence from actual conversations:**
  - Commercial Auto (40 turns): Bot collects state, vehicle type, VIN, year, make, model, driver, coverage — then chat times out
  - Commercial Auto (40 turns): Bot collects 25+ turns of info, says "connecting you to live agent" — nobody connects
  - General Liability (32 turns): Bot collects everything, says "I've collected all info!" and closes. User asks "y ahora que hago?" (now what do I do?)
- **Root cause:** System prompt says "I don't generate quotes directly" but this isn't communicated to the user until deep in the conversation
- **Fix:** At the start of any quote/product conversation, set expectations: "I can collect your information to send to an underwriter, or you can submit directly at [portal URL]. Which would you prefer?"
- **Layer:** System prompt + opener
- **Measurement:** Product inquiry `partial_then_left` and `missed_handoff` rates should decrease; average self-served depth for product inquiries with bad outcomes should decrease

### Opportunity 13: Missed Handoff Fallback (HIGH LEVERAGE)
- **Impact:** 618 conversations (17% of all real conversations) where handoff was needed but never completed
- **Breakdown:**
  - 403 (65%): User left waiting — CSR assigned but user went silent/disengaged before help arrived
  - 215 (35%): No CSR available — handoff triggered, no agent ever joined
- **336 were explicit handoff requests** — users who specifically asked for a human
- **Root cause:** No fallback behavior when handoff fails — conversation just dies silently
- **Fix:** When no CSR connects within timeout, offer alternatives: collect contact info for callback, provide email addresses, suggest trying during business hours. Don't let the conversation die.
- **Layer:** System prompt + flow logic
- **Measurement:** `missed_handoff` outcome count should decrease; `csr_never_joined` conversations should end with contact info collected rather than silent timeout

### Opportunity 7: After-Hours Detection
- **Impact:** 69 conversations where users go **11 turns deep on average** before discovering nobody's available. Some go up to 28 turns.
- **Root cause:** No time check at conversation start. After-hours message triggered only at handoff.
- **Fix:** Check time at conversation start. If outside 8:30AM-5:00PM ET Mon-Fri, tell user immediately with options (leave message, come back during hours, self-service via portal).
- **Layer:** System prompt or first-message logic
- **Measurement:** `out_of_hours_handoff` outcome should drop to near zero; depth of after-hours conversations should drop dramatically

### Opportunity 3: Generic Opener
- **Impact:** 100% of conversations start with "Hello, I am Fred! GIC's virtual chat assistant. How can I assist you today?" — tells user nothing about capabilities
- **Fix:** Replace with opener that names what Fred can do: policy lookup, quote submission guidance, appetite questions, portal help
- **Layer:** MongoDB `first_message` field in distribution/widget config
- **Measurement:** Intent distribution shift (fewer catch-all "informational", more specific intents); resolved_autonomous rate improvement

### Opportunity 4: Yes/No Grammar Vulnerability
- **Impact:** Minor — adds occasional wasted turn when bot asks "Could you please provide X?" and user responds "yes"
- **Fix:** System prompt instruction to use direct requests ("What's the address?") instead of indirect questions ("Could you provide the address?")
- **Layer:** System prompt (bundle with other prompt changes)
- **Measurement:** Contributes to overall depth reduction

### Opportunity 6: KB Gaps — WC Class Codes
- **Impact:** 109 conversations tagged `missing_knowledge`
- **Fix:** Add WC class code appetite data to GIC KB
- **Layer:** Knowledge base content
- **Measurement:** `missing_knowledge` tag count should decrease

---

## Bundled Minor Improvements

### Opportunity 10: Renewal/Expiration Date (bundle with tool config)
- Bot shows payment info and status but not expiration/renewal dates
- Only 4 "Policy Renewal" conversations in dataset — very low volume
- Add to tool output instructions if touching that config

### Opportunity 11: Portal/Email Routing (bundle with KB)
- Bot gives email addresses but not always portal URLs
- Not a driver of failure — users get routing info, underlying problems are different
- Ensure portal URLs are in KB content when updating for opportunity 6

---

## Parked Opportunities

| # | Opportunity | Reason |
|---|---|---|
| 1 | Slot-filling | Infrastructure-level (bot-service ACTION:QUESTION framework), not worth prompt mitigation |
| 2 | Tone/acknowledgment | Cosmetic — not driving abandonment or failure, 7.8% frustrated user rate is from structural issues |
| 8 | Proactive constraint surfacing | Actual conversations show the problem is bot expectations gap (opportunity 14), not missing constraint data |
| 9 | "Thank you" false closure | Only 136 inferred_resolution dropoffs (3.7%), most are legitimate — no signal of false closure |
| 12 | "True" boolean bug | Front-end widget issue, 1 occurrence, not agent-level |

---

## Implementation Grouping

**Group A — System Prompt + Opener (opportunities 3, 4, 7, 14):**
All are prompt/config changes, no code deploys. Can be done together.
- Rewrite opener with capabilities
- Add expectations-setting for product/quote conversations
- Add after-hours time check instruction
- Switch to direct request phrasing

**Group B — Operations API Code Change (opportunity 5, bundle 10):**
Code change in operations_api. Separate deploy.
- Policy number format normalization
- Bundle: add expiration date to tool output instructions

**Group C — Knowledge Base Content (opportunity 6, bundle 11):**
KB content additions, no code changes.
- WC class code appetite data
- Bundle: portal URLs in KB content

**Group D — Handoff Fallback (opportunity 13):**
Prompt + possibly flow logic change.
- Fallback behavior when CSR doesn't connect
- Contact info collection before/during handoff
