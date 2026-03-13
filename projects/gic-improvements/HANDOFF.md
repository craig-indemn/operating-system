# GIC Improvements — Session Handoff

## Resume Instructions
Read these files in order:
1. `projects/gic-improvements/INDEX.md` — project status, evaluation IDs, open questions
2. `projects/gic-improvements/artifacts/2026-03-13-revised-deployment-plan.md` — revised ticket structure and deployment plan

## Current State

**DEPLOYING TO PRODUCTION. Dev work complete. Craig deploying via copilot-dashboard UI.**

### What Was Done This Session (2026-03-13-a)

1. **Kyle's feedback integrated:**
   - Ship now, don't wait for GIC approval
   - Reframe report — strip internal gaps, enhancement-only
   - Contact collection (#13) deprioritized — portal has broker context
   - New: handoff diligence + CSR conversation summary
   - Ship together, track individually in Linear

2. **Two new features designed and implemented on dev bot:**
   - Handoff diligence — agent asks "what do you need help with?" before handoff
   - CSR conversation summary — agent posts structured summary before handoff, visible to both broker and CSR

3. **Root cause investigation — bot-service text drop:**
   - `return_tools()` in bot_agent_graph.py drops LLM text content when a tool call is in the same response
   - Fix: two-turn handoff — summary in text-only response, handoff tool call in next response after user confirms
   - Confirmed working: 15/19 eval (78.9%)

4. **Linear tickets updated:**
   - AI-333, AI-334 descriptions revised
   - AI-340 created: handoff diligence
   - AI-341 created: CSR conversation summary

5. **Report reframed:**
   - Stripped: KB disconnected, quote collection without disclosure, silent handoff failures
   - Added: handoff context gathering, CSR summary, expanded knowledge access
   - PDF: `~/Repositories/indemn-observability/reports/GIC_Agent_Enhancement_Report_March_13__2026.pdf`
   - Sent to Kyle + Ryan via Slack with deployment plan

6. **Test set updated to v6 (19 items):**
   - Added handoff diligence scenario
   - Added CSR summary scenario
   - Updated criteria for explicit handoff test

### What's Next — IMMEDIATE (production deployment)

**Craig is doing these via the copilot-dashboard UI:**

1. **System prompt** (AI-337 + AI-340 + AI-341) — paste the dev bot prompt into prod bot config
   - Dev bot prompt is the source of truth: `bot_configurations._id: 6787a63d2ea6350012955ee0`
   - Prod bot config: `bot_configurations._id: 66334509c3ba1c2ecdc87cf0`

2. **First message** — **BLOCKED: needs JC approval** per Kyle (ts=1773430596)
   - New text ready but hold until JC approves
   - Must update BOTH `bot_configurations` AND `distributions` (widget override at `_id: 667b9bb696b11e957d9830a9`)

3. **KB retrieval** (AI-336) — need to do via MongoDB since UI may not expose all settings:
   - Add faqs-retriever tool to prod bot_tools
   - Fix Pinecone namespace: `65eb3f19e5e6de0013fda310` → `6613cbc6658ad379b7d516c9`
   - Add KB ID mapping: `6852bf20940d780013ef4a28`
   - Set top_k: 25

4. **Policy tool output** (AI-338) — update POLICY CHECK tool instructions via UI
   - Prod POLICY CHECK tool _id: `67e2916c79a7c700137bf131`
   - Add structured display order with expiration date

5. **Policy number normalization** (AI-335) — PR to operations_api
   - Code: `normalizePolicyNumber()` in `src/services/customers/gic_policy_details.ts`
   - Two rules: Granada suffix strip, USLI/MV space insertion
   - Analysis: `artifacts/2026-03-12-policy-number-analysis.md`

6. **Snapshot observatory metrics** before deploy for clean before/after boundary

7. **Start 4-week monitoring** (AI-339)

### Waiting On
- Ryan's perspective on shipping and messaging
- JC approval on first message change

## Key References
- **Linear parent**: AI-333 (GIC Agent Improvements — Production Deployment)
- **Production bot:** `66026a302af0870013103b1e` (prod tiledesk)
- **Prod bot config _id:** `66334509c3ba1c2ecdc87cf0`
- **Test bot (dev):** `6787a63d2ea6350012955ed9` (bot_config _id: `6787a63d2ea6350012955ee0`)
- **Distribution (widget override):** `667b9bb696b11e957d9830a9`
- **Rubric:** `3bd8cc49-7eef-4110-95ac-01fdc4419cc5` (5 rules, v2)
- **Test Set:** `0977c5bc-2987-40fa-95bb-31f14781a7c1` (19 items, v6)
- **Best eval:** `2dff7636-296d-4da1-9b5a-145ee610c4b1` — 15/19 (78.9%)
- **Eval model:** `openai:gpt-4.1` | **Eval DB:** dev cluster, `tiledesk` database
- **Enhancement report PDF:** `~/Repositories/indemn-observability/reports/GIC_Agent_Enhancement_Report_March_13__2026.pdf`
- **KB retrieval config (FIXED on dev only):**
  - Pinecone namespace: `6613cbc6658ad379b7d516c9` (dev org — where vectors actually exist)
  - KB ID filter: `6852bf20940d780013ef4a28` ("New knowledge base 5" — what vectors are tagged with)
  - top_k: 25
- **Prod Pinecone namespace:** `65eb3f19e5e6de0013fda310` — has ZERO vectors, needs to be changed to dev namespace
- **Prod bot tools:** POLICY CHECK (_id: `67e2916c79a7c700137bf131`), human_handoff (_id: `67e2916c79a7c700137bf12c`, `67e3803879a7c700138954ce`), policy_unavailable (_id: `67e2916c79a7c700137bf11e`)
- **Bot-service architecture note:** `return_tools()` drops LLM text when tool call present. Handoff summary must be text-only response before tool call response. See `bot-service/app/services/graphs/bot_agent_graph.py` lines 530-540.
