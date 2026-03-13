---
ask: "Revise GIC deployment plan based on Kyle's feedback — ship without approval, track individually, reframe report, add handoff diligence + CSR summary"
created: 2026-03-13
workstream: gic-improvements
session: 2026-03-13-a
sources:
  - type: slack
    description: "Kyle's feedback in mpdm-kwgeoghan--ryan--craig group DM (ts=1773409077.478229, ts=1773411674.695249)"
  - type: linear
    description: "Existing tickets AI-333 through AI-339"
---

# Revised GIC Deployment Plan

## Kyle's Directives (March 13, 2026)

1. **Ship fixes now** — don't wait for GIC approval. We're early stage, move fast.
2. **Reframe the report** — strip internal gaps (KB disconnected, quote collection without disclosure, silent handoffs). Customer-facing doc shows enhancements only.
3. **Contact collection (#13) lower priority** — portal already has broker context via API.
4. **New: Handoff diligence + CSR summary** — agent asks what the broker needs before handing off, then posts a conversation summary visible to both parties so the CSR isn't starting from scratch.
5. **Ship together, track individually** — deploy all changes at once, but each change gets its own Linear ticket with expected improvement. Measure broadly post-deploy.
6. **EventGuard is the benchmark** — GIC is heading toward that level of formal process. This is the starting template.
7. **Hold on dashboard work** — CSR-facing changes wouldn't land with JC. Only if requested or clear win.

---

## Revised Ticket Structure

### Parent: AI-333 — GIC Agent Improvements — Production Deployment

**Updated description:** Ship all improvements together. Each change tracked individually with expected improvement and evaluation evidence. Measure broadly post-deploy via observatory. No approval gate — deploy and reframe report as enhancement summary.

---

### AI-334 — GIC: Reframe improvement report as enhancement summary

**Type:** Report / Deliverable
**Priority:** 2 (High)
**Points:** 3
**Expected improvement:** N/A — customer deliverable
**Eval evidence:** N/A

**What changed from original:** Was "Generate improvement evaluation report for customer approval." Now: reframe as forward-looking enhancement summary. No approval gate.

**Remove from report (internal gaps):**
- KB being disconnected (wrong Pinecone namespace — our bug)
- Quote collection without disclosure (expectations gap — should have caught this)
- Silent handoff failures (no fallback — our operational gap)

**Keep and reframe as enhancements:**
- Smarter opener with clear capabilities
- After-hours early detection — Fred now tells users immediately
- Improved policy lookup accuracy — handles more format variations
- Better WC/appetite answers from expanded KB access
- Handoff diligence + CSR summary — Fred gathers context and briefs the CSR
- Policy details now include expiration dates

**Framing:** "Here's what Fred can do now that he couldn't before" — not "here's what was broken."

Observatory baselines and monitoring plan stay — they show we're measuring impact. Forward-looking tone.

---

### AI-335 — GIC: Deploy policy number normalization

**Type:** Code deploy (operations_api PR)
**Priority:** 2 (High)
**Points:** 2
**Expected improvement:** Policy lookup failure rate from 15% → ~6%. Fixes 63% of format-addressable failures.
**Eval evidence:** Single scenario — policy lookup with messy format (prefix + suffix). Agent should successfully look up the policy.

**What:** `normalizePolicyNumber()` in `operations_api/src/services/customers/gic_policy_details.ts`. Two data-driven rules based on 192 real lookups:
1. Granada suffix strip: "0185FL00190350 - 0" → "0185FL00190350"
2. USLI/MV space insertion: "GL1234567" → "GL 1234567"

**Observatory metric:** `missing_backend_data` tag count, `system_error:api_issue` count.

---

### AI-336 — GIC: Add faqs-retriever tool and fix KB retrieval config on prod bot

**Type:** Config change (prod MongoDB)
**Priority:** 2 (High)
**Points:** 2
**Expected improvement:** Missing knowledge conversations: 109 → near zero. 270+ KB entries become accessible for the first time in production.
**Eval evidence:** Single-turn — WC class code question. Agent should retrieve and present specific class codes.

**What:**
1. Add faqs-retriever tool to prod bot_tools
2. Fix Pinecone namespace: `65eb3f19e5e6de0013fda310` → `6613cbc6658ad379b7d516c9`
3. Add correct KB ID mapping: `6852bf20940d780013ef4a28`
4. Set top_k to 25

**Note:** This is an internal fix (KB was never connected in prod). Report frames it as "expanded KB access" — an enhancement, not a bug fix.

**Observatory metric:** `missing_knowledge` tag count.

---

### AI-337 — GIC: Apply system prompt and opener updates to prod bot

**Type:** Config change (prod MongoDB)
**Priority:** 2 (High)
**Points:** 3
**Expected improvement:** Product inquiry bad outcomes: 51% → ~30%. After-hours wasted turns: avg 11 → 1-2. Direct request phrasing reduces wasted turns.
**Eval evidence:** Scenarios — product inquiry (agent sets expectations early), after-hours (agent detects and offers alternatives), direct request (agent uses "What is the policy number?" not "Could you please provide...?")

**What:**
- Full system prompt rewrite (not patch) — consolidated from 6,236 chars
- New first_message with specific capabilities listed
- Quote protocol with verified email (quote@gicunderwriters.com)
- After-hours detection (8:30 AM - 5:00 PM)
- Direct request phrasing
- Check both locations: `bot_configurations.first_message.text` and `distributions` for widget override

**Observatory metrics:** Product inquiry outcome rates, after-hours conversation depth, overall conversation depth.

---

### AI-338 — GIC: Update POLICY CHECK tool output instructions

**Type:** Config change (prod MongoDB)
**Priority:** 3 (Medium)
**Points:** 1
**Expected improvement:** Expiration date now surfaced on every policy lookup. Renewal status flagged proactively.
**Eval evidence:** Single-turn — policy lookup. Agent should display expiration date and renewal status.

**What:** Replace current tool output instructions with structured display order including expiration date, effective date, and renewal flags.

**Observatory metric:** Qualitative — check conversation transcripts for expiration date mentions.

---

### NEW — GIC: Handoff diligence — gather context before handoff

**Type:** Config change (system prompt addition)
**Priority:** 2 (High)
**Points:** 2
**Expected improvement:** Cold handoffs reduced. CSR receives context about what the broker needs. Broker doesn't have to repeat themselves.
**Eval evidence:** Single scenario — user immediately asks for a human. Agent should ask one question ("What do you need help with so I can connect you with the right person?") before triggering handoff. If user insists, hand off immediately.

**What:** System prompt instruction:
> When a user requests to speak with a human or live agent, ask one clarifying question first: "What do you need help with so I can make sure the right person is available?" If the user provides context, acknowledge it and proceed with handoff. If the user insists on speaking to a human without providing context, hand off immediately — do not block or gate access to a live agent.

**Behavior:**
- Light touch — one question, not an intake form
- Never block handoff if user insists
- Context gathered feeds into the CSR summary (next ticket)

**Observatory metric:** Qualitative — check handoff conversations for context gathering before transfer.

---

### NEW — GIC: CSR conversation summary at handoff

**Type:** Config change (system prompt addition)
**Priority:** 2 (High)
**Points:** 2
**Expected improvement:** CSR starts with full context. No redundant questions. Faster resolution.
**Eval evidence:** Single scenario — multi-turn conversation ending in handoff. Agent should post a structured summary message before/at handoff that captures what was discussed, what was asked, and any data looked up.

**What:** System prompt instruction:
> When triggering a handoff to a live agent, post a summary message in the conversation immediately before the handoff. The summary should be visible to both the broker and the CSR. Format:
>
> "Handing off to a representative. Here's a summary of our conversation:
> - **Request:** [what the broker needs]
> - **Details discussed:** [key information gathered — policy numbers looked up, coverage questions asked, etc.]
> - **Status:** [what was resolved vs. what still needs attention]"
>
> Keep the summary concise — 3-5 bullet points maximum. Include any policy numbers, names, or specific data points that were part of the conversation.

**Behavior:**
- Visible to both broker and CSR
- Posted as a regular chat message (no code changes needed)
- Captures the "why" from handoff diligence plus any prior conversation context

**Observatory metric:** Qualitative — check handoff conversations for summary presence and completeness.

---

### AI-339 — GIC: 4-week post-deployment observatory monitoring

**Type:** Monitoring
**Priority:** 3 (Medium)
**Points:** 1 per week (4 total)
**Expected improvement:** N/A — measurement
**Eval evidence:** N/A

**What:** Weekly observatory queries comparing against pre-deployment baselines:
- Autonomous resolution rate (baseline: 8%)
- Total failure rate (baseline: 44%)
- Policy API failure rate (baseline: 15%)
- Product inquiry bad outcome rate (baseline: 51%)
- Missed handoff count (baseline: 618)
- After-hours wasted conversations (baseline: 69)
- Missing knowledge count (baseline: 109)
- Frustrated user rate (baseline: 7.8%)

Weekly artifact saved to `projects/gic-improvements/artifacts/`.

---

## Execution Order

All changes ship together. But the work sequence is:

1. **Dev bot first** — apply handoff diligence + CSR summary prompt changes to dev test bot (already has all other improvements)
2. **Run eval** — verify new scenarios pass, no regressions
3. **Production deploy** (all at once):
   - AI-335: PR + deploy operations_api (policy normalization)
   - AI-336: MongoDB changes (faqs-retriever + KB config)
   - AI-337: MongoDB changes (system prompt + opener)
   - AI-338: MongoDB changes (tool output instructions)
   - Handoff diligence: included in AI-337's prompt
   - CSR summary: included in AI-337's prompt
4. **Snapshot observatory metrics** at deployment moment
5. **AI-334: Reframe report** — can be done in parallel with deploy
6. **AI-339: Begin monitoring** — weekly for 4 weeks

---

## Notes

- Handoff diligence and CSR summary are prompt-only changes — they technically live in the system prompt (same as AI-337). Separate tickets for tracking per Kyle's directive, but the actual change is part of the prompt rewrite.
- Contact collection (#13 from original plan) deprioritized per Kyle — portal already has broker context.
- Dashboard work on hold per Kyle — CSR-facing, wouldn't land with JC.
- EventGuard is the benchmark for formal process. This GIC deployment is the starting template for getting there.
