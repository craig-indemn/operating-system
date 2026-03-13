# GIC Improvements — Session Handoff

## Resume Instructions
Read these files in order:
1. `projects/gic-improvements/INDEX.md` — project status, evaluation IDs, open questions
2. `projects/gic-improvements/PLAN.md` — end-to-end plan (Phases 1-6)
3. `projects/gic-improvements/artifacts/2026-03-12-v3-baseline-evaluation-results.md` — V3 baseline: 7/17, 10/10 opportunity items FAIL
4. `projects/gic-improvements/artifacts/2026-03-12-policy-number-analysis.md` — 192 real policy lookups, carrier format map, normalization rules
5. `projects/gic-improvements/artifacts/2026-03-12-opportunity-prioritization.md` — 7 active opportunities with implementation groups
6. `projects/gic-improvements/artifacts/2026-03-12-retrieval-investigation.md` — KB retrieval root cause analysis and fix

## Current State

**Phase 3 (Post-Implementation Evaluation) COMPLETE. 12/17 passed (70.6%) — up from 7/17 baseline (41.2%). Test criteria updated to v4 for future runs.**

### What Was Done This Session (2026-03-12-g)

1. **KB Retrieval Root Cause Investigation** — traced the full FAQs retriever code path in bot-service:
   - `bot_details.py` → aggregation from `faq_kbs` → `bot_kb_mappings` → `connected_kbs`
   - `agent_tools.py:223-333` → embeds query → queries Pinecone with namespace + KB ID filter → TYPE_BOOST scoring → optional Cohere reranking
   - No similarity threshold (all top-k results returned)
   - Default top_k=10, embedding model: text-embedding-3-small

2. **Found TWO root causes for retrieval failure:**
   - **Wrong Pinecone namespace**: Bot config had `65eb3f19e5e6de0013fda310` (prod GIC org namespace) — this namespace DOES NOT EXIST in Pinecone. Vectors are in `6613cbc6658ad379b7d516c9` (dev org namespace, 30,971 vectors).
   - **Wrong KB ID in filter**: Bot KB mapping pointed to `6787a6702ea6350012955f33` (original dev GIC KB), but vectors in Pinecone are tagged with `id_kb: 6852bf20940d780013ef4a28` ("New knowledge base 5"). The Pinecone filter `{"id_kb": {"$in": ["6787a6702ea6350012955f33"]}}` matched nothing.

3. **Applied fixes to test bot:**
   - Updated `kb_configuration.namespace` → `6613cbc6658ad379b7d516c9` (where vectors actually are)
   - Updated `bot_kb_mappings.id_kb` → `6852bf20940d780013ef4a28` (what vectors are tagged with)
   - Increased `top_k_documents_count` → 25 (to compensate for ~5x vector duplication in Pinecone)

4. **Verified retrieval works** — direct Pinecone queries with corrected config return relevant results:
   - "email for submitting a quote": score 0.82, returns `quotes@gicunderwriters.com` ✓
   - "class codes for service industry": score 0.50, returns class codes ✓
   - "portal URL for new business": score 0.51, returns submission guidance ✓

5. **Added verified emails to system prompt:**
   - Handoff fallback: `csr@gicunderwriters.com` (verified from KB)
   - Quote protocol: `quote@gicunderwriters.com` (verified from KB)

6. **Documented additional findings:**
   - Prod bot has NO faqs-retriever tool — KB access doesn't exist in production at all
   - ~5x vector duplication in Pinecone (same data trained into multiple KBs over time)
   - 69 class code entries covering 59 unique codes (no 8810 — common clerical code not in KB)
   - Business hours confirmed from KB: 8:30 AM - 5:00 PM

### What Was Done Previous Session (2026-03-12-f)

1. V3 baseline evaluation: 7/17 (41.2%), perfectly calibrated
2. Group A: System prompt fully rewritten (not patched), first_message updated
3. Group B: `normalizePolicyNumber()` added to operations API (local, not deployed), expiration date in tool output
4. Group D: Handoff fallback covered by prompt rewrite
5. KB content investigation: 269 trained entries in dev GIC KB

### Post-Implementation Evaluation Results

**Run:** `0a30f458-7a9d-4b08-8d3e-091dae4cc178` — 12/17 passed (70.6%)
**Baseline:** `4ee5b3af-f0b1-43f8-9883-303da9e3927a` — 7/17 passed (41.2%)
**Improvement:** +5 items, +29.4 percentage points
**Rubric:** 85/85 (100%) — zero behavioral regressions

**Items that flipped FAIL → PASS (5):**
- WC class code question (#6) — KB retrieval fix
- Market inquiry - workers comp appetite (#6) — KB retrieval fix
- Product inquiry - commercial auto quote (#14) — Expectations gap prompt fix
- Product inquiry - Spanish-speaking agent (#14) — Expectations gap prompt fix
- Information collection with purpose transparency (#4) — Direct request prompt fix

**Remaining failures (5):**
| Item | Classification |
|------|---------------|
| Greeting - capabilities | Test design: eval doesn't send first_message |
| Failed handoff - no agent | Eval limitation: harness stops at handoff trigger |
| After-hours handoff recovery | Eval limitation: harness stops at handoff trigger |
| Explicit handoff - explain process | Real agent issue: doesn't explain handoff process |
| Policy messy format | Expected: normalizePolicyNumber() not deployed |

**Test criteria updated to v4** to fix eval limitations (handoff criteria now test pre-handoff behavior).

### What's Next — IMMEDIATE

1. **Deploy operations API change** for #5:
   - `normalizePolicyNumber()` in local repo only
   - Needs PR + deploy to dev for eval to pick it up

2. **Phase 4 (Production deployment)**:
   - Apply all prompt/config changes to prod bot (`66026a302af0870013103b1e`)
   - Add faqs-retriever tool to prod bot (currently missing)
   - Configure prod bot KB settings (namespace, KB ID mapping)
   - Deploy operations API code

3. **Phase 5 (Monitoring)** — 4 weeks post-deployment observatory tracking

## Implementation Status

| Opp | # | Fix | Level | Status |
|-----|---|-----|-------|--------|
| Opener | #3 | New first_message with capabilities | Bot config | **Done** |
| Direct requests | #4 | Core rule in rewritten prompt | Bot config | **Done** |
| Policy parsing | #5 | `normalizePolicyNumber()` in ops API | Code | **Done locally, not deployed** |
| WC class codes | #6 | KB retrieval fix (namespace + KB ID) | Retrieval config | **Done** |
| After-hours | #7 | Handoff failure recovery in prompt | Bot config | **Done** |
| Expiration date | #10 | Tool output instructions | Bot tool | **Done** |
| Portal URLs | #11 | KB retrieval fix (namespace + KB ID) | Retrieval config | **Done** |
| Handoff fallback | #13 | Handoff protocol in prompt + verified email | Bot config | **Done** |
| Expectations gap | #14 | Quote protocol in prompt + verified email | Bot config | **Done** |

## Key References
- **Production bot:** `66026a302af0870013103b1e` (prod tiledesk) — NO faqs-retriever tool
- **Test bot (dev):** `6787a63d2ea6350012955ed9` (bot_config _id: `6787a63d2ea6350012955ee0`)
- **Rubric:** `3bd8cc49-7eef-4110-95ac-01fdc4419cc5` (5 rules, **v2**)
- **Test Set:** `0977c5bc-2987-40fa-95bb-31f14781a7c1` (17 items, **v4** — eval-limitation fixes for handoff/greeting)
- **V3 baseline:** `4ee5b3af-f0b1-43f8-9883-303da9e3927a` — 7/17 (41.2%)
- **Post-implementation:** `0a30f458-7a9d-4b08-8d3e-091dae4cc178` — 12/17 (70.6%)
- **Eval model:** `openai:gpt-4.1` | **Eval DB:** dev cluster, `tiledesk` database
- Evaluations: port 8002 | Bot-service: port 8001 (has local IndexError fix at `bot_agent_graph.py:421`)
- AgencyCode hardcoded to `5883` in dev bot POLICY CHECK tool
- **KB retrieval config (FIXED):**
  - Pinecone namespace: `6613cbc6658ad379b7d516c9` (dev org — where vectors actually exist)
  - KB ID filter: `6852bf20940d780013ef4a28` ("New knowledge base 5" — what vectors are tagged with)
  - top_k: 25 (increased from default 10 to compensate for ~5x Pinecone duplication)
  - Pinecone index: `indemn`, host: `indemn-f6w06cd.svc.us-east-1-aws.pinecone.io`
- **KB content:** 269 entries in dev GIC KB (`6787a6702ea6350012955f33`), trained into Pinecone under KB `6852bf20940d780013ef4a28`
  - 69 class code entries (59 unique codes — mostly artisan/contractor trades, no 8810)
  - 24 portal entries
  - 50+ email routing entries (quote@, csr@, bind@, cancellation@, endorsements@, wc@, payments@, etc.)
- **Operations API code change:** `operations_api/src/services/customers/gic_policy_details.ts` — `normalizePolicyNumber()` added but not deployed
- **System prompt:** Original prod = 6,236 chars. New test bot prompt with verified emails. Prod bot is unchanged.
- **FAQs Retriever tool (dev):** `68e63cb1ba7a8376e67f0236`
