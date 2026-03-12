# GIC Improvements — Session Handoff

## Resume Instructions
Read these files in order:
1. `projects/gic-improvements/INDEX.md` — project status, evaluation IDs, open questions
2. `projects/gic-improvements/PLAN.md` — end-to-end plan (Phases 1-6)
3. `projects/gic-improvements/artifacts/2026-03-12-v3-baseline-evaluation-results.md` — V3 baseline: 7/17, 10/10 opportunity items FAIL
4. `projects/gic-improvements/artifacts/2026-03-12-policy-number-analysis.md` — 192 real policy lookups, carrier format map, normalization rules
5. `projects/gic-improvements/artifacts/2026-03-12-opportunity-prioritization.md` — 7 active opportunities with implementation groups

## Current State

**Phase 2 (Implementation) is in progress. Groups A, B, D are applied to the test bot. Groups C (#6, #11) are blocked on a retrieval quality investigation.**

### What Was Done This Session (2026-03-12-f)

1. **Ran V3 baseline evaluation** — run `4ee5b3af`, 7/17 passed (41.2%). 10/10 opportunity items FAIL as expected, 7/7 regression guards PASS, rubric 85/85 (100%). Perfectly calibrated.

2. **Group A — System prompt fully rewritten** (not patched):
   - Rewrote entire system prompt from scratch rather than bolting on sections
   - Resolved conflicts: old "trigger handoff immediately" vs new "collect contact first"; old "gather info for quotes" vs new "present options first"
   - Removed corporate jargon ("Engagement Optimization Objective")
   - Consolidated 3 scattered quote-handling sections into one coherent "Quote and Product Inquiry Protocol"
   - Added: direct request phrasing rule, handoff protocol with contact collection, handoff failure recovery, quote/portal choice before info collection
   - Updated first_message with specific capability listing
   - Prompt went from 6,236 → 5,829 chars (smaller despite adding 4 behaviors)
   - **IMPORTANT:** Fabricated URLs and emails were initially added then removed. The prompt now says "the GIC agent portal" and "the appropriate email address" without specific URLs — those need to be filled in with real data.

3. **Group B — Policy number normalization** (operations API code change):
   - Analyzed 192 real policy lookups from observatory (101 success, 91 failure)
   - Mapped 13 insurance carriers to their exact policy number formats
   - Two data-driven normalization rules fix 100% of addressable failures (57/91 = 63% of total):
     - Rule 1: Strip edition suffixes from Granada-format numbers only (`0185FL00190350-0` → `0185FL00190350`)
     - Rule 2: Insert space after GL/SE/CP prefix when directly followed by digit (`GL1322059` → `GL 1322059`)
   - Rules are surgically targeted — they don't touch carriers that legitimately use hyphens (Kinsale, Topa, Mid-Continent, Sirius, etc.)
   - Code: `normalizePolicyNumber()` in `operations_api/src/services/customers/gic_policy_details.ts`
   - **NOT DEPLOYED** — code is in local repo only. Needs PR + deploy to dev for eval to pick it up.

4. **Group B — Expiration date in tool output** (#10):
   - Updated POLICY CHECK tool output instructions to explicitly list expiration date in display order
   - Applied to test bot tool config in dev MongoDB

5. **Group D — Handoff fallback** (#13):
   - Covered by the system prompt rewrite (handoff protocol + failure recovery sections)

6. **KB content investigation** (#6, #11):
   - Discovered the KB is NOT empty — it has 593 trained entries across 8 knowledge bases
   - 140 class code entries with specific codes (98111, 97650, 96816, etc.)
   - 72 portal entries with real URLs and navigation guidance
   - 20+ email routing entries with real emails (quote@gicunderwriters.com, csr@gicunderwriters.com, cancellation@granadainsurance.com, etc.)
   - All entries are trained (indexed in Pinecone under namespace `65eb3f19e5e6de0013fda310`)
   - **The problem is retrieval quality, not missing content.** The agent searches but doesn't find relevant entries for broad queries like "what class codes for service industry in Florida?"

### What's Next — IMMEDIATE

1. **Investigate retrieval quality** for #6 and #11:
   - Understand how the FAQs retriever tool works (bot-service code path)
   - Check retrieval config: top-k, similarity threshold, reranking
   - Run test queries against Pinecone directly to see what comes back for "service industry class codes" and "portal URL for new business submission"
   - Compare what the retriever returns vs what's actually in the KB
   - Fix the retrieval pipeline so the agent surfaces existing content
   - This may require changes to retrieval config, re-embedding, or query reformulation

2. **Deploy operations API change** for #5:
   - The `normalizePolicyNumber()` function is in the local repo but not deployed
   - Needs a PR to operations_api and deployment to dev environment
   - Without this, the eval won't test the parsing improvement

3. **Run post-implementation evaluation**:
   - Same test set (v3), same rubric (v2), same eval model (openai:gpt-4.1)
   - Compare to v3 baseline (7/17)
   - Expected: significant improvement on prompt-level changes (#3, #4, #7, #10, #13, #14)
   - #5 depends on API deploy, #6 and #11 depend on retrieval fix

4. **Fill in real URLs/emails in system prompt**:
   - The portal URL and support email were removed because they were fabricated
   - Once real values are confirmed (from KB data: quote@gicunderwriters.com exists, portal URL TBD), add them back

## Implementation Status

| Opp | # | Fix | Level | Status |
|-----|---|-----|-------|--------|
| Opener | #3 | New first_message with capabilities | Bot config | **Done** |
| Direct requests | #4 | Core rule in rewritten prompt | Bot config | **Done** |
| Policy parsing | #5 | `normalizePolicyNumber()` in ops API | Code | **Done locally, not deployed** |
| WC class codes | #6 | Retrieval quality investigation | Retrieval | **Blocked — data exists, retrieval fails** |
| After-hours | #7 | Handoff failure recovery in prompt | Bot config | **Done** |
| Expiration date | #10 | Tool output instructions | Bot tool | **Done** |
| Portal URLs | #11 | Retrieval quality investigation | Retrieval | **Blocked — data exists, retrieval fails** |
| Handoff fallback | #13 | Handoff protocol in prompt | Bot config | **Done** |
| Expectations gap | #14 | Quote protocol in prompt | Bot config | **Done** |

## Key References
- **Production bot:** `66026a302af0870013103b1e` (prod tiledesk)
- **Test bot (dev):** `6787a63d2ea6350012955ed9` (bot_config _id: `6787a63d2ea6350012955ee0`)
- **Rubric:** `3bd8cc49-7eef-4110-95ac-01fdc4419cc5` (5 rules, **v2**)
- **Test Set:** `0977c5bc-2987-40fa-95bb-31f14781a7c1` (17 items, **v3** — opportunity-aligned criteria)
- **V3 baseline:** `4ee5b3af-f0b1-43f8-9883-303da9e3927a` — 7/17 (41.2%)
- **Eval model:** `openai:gpt-4.1` | **Eval DB:** dev cluster, `tiledesk` database
- Evaluations: port 8002 | Bot-service: port 8001 (has local IndexError fix at `bot_agent_graph.py:421`)
- AgencyCode hardcoded to `5883` in dev bot POLICY CHECK tool
- KB namespace: `65eb3f19e5e6de0013fda310` (prod GIC, read-only from Pinecone)
- **KB content is in `knowledge_bases_data_sources` collection**, linked by `id_organization: ObjectId("65eb3f19e5e6de0013fda310")`
- **8 KBs, 593 entries total, all trained.** Key KBs: `66f1449d9afe08001361012c` (class codes, 255 entries), `66fa34ca93b5a4001355ff5c` (GIC KB, 270 entries)
- **Operations API code change:** `operations_api/src/services/customers/gic_policy_details.ts` — `normalizePolicyNumber()` function added but not deployed
- **System prompt backup:** Original prod prompt is 6,236 chars. New test bot prompt is 5,829 chars. Prod bot is unchanged.
