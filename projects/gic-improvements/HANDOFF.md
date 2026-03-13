# GIC Improvements — Session Handoff

## Resume Instructions
Read these files in order:
1. `projects/gic-improvements/INDEX.md` — project status, evaluation IDs, open questions
2. `projects/gic-improvements/PLAN.md` — end-to-end plan (Phases 1-6)
3. `projects/gic-improvements/artifacts/2026-03-12-opportunity-prioritization.md` — 7 active opportunities

## Current State

**Phase 4 (Production Deployment) IN PROGRESS. Linear tickets created (AI-333 parent + 6 sub-issues). Customer report PDF finalized and shared with Kyle + Ryan for review.**

### What Was Done This Session (2026-03-12-i)

1. **Report refinements based on user feedback:**
   - Reframed entire report from "failure" language to improvement-focused framing
   - Renamed "Total Failure Rate" → "Unresolved Rate", "Failure Breakdown" → "Improvement Opportunity Areas"
   - Changed "Problem/Solution" labels to "Finding/Improvement" on improvement cards
   - Softened bar chart labels (e.g., "Bad Product Inquiries" → "Product Inquiry Gaps")
   - Changed "automated evaluation" → "systematic testing" for customer-facing language

2. **Redesigned page 2 with system-level metrics:**
   - Queried observatory data to understand conversation flow: 5,330 total, 1,629 excluded (zero user messages), 3,701 real
   - Discovered 46% system resolution rate (300 AI + 1,395 CSR = 1,695 resolved), not just 8% AI-only
   - New metric cards: 46% Resolved, 38% By Representative, 8% By AI Alone, 15% Partially Addressed
   - Bar chart switched from raw numbers to percentages of conversations
   - Opportunities table now shows % impact instead of raw counts

3. **Monitoring page reframed with positive metrics:**
   - System Resolution Rate: 46% → 55-60%
   - AI Resolution Rate: 8% → 15-20%
   - Policy Lookup Success: 85% → 92-95%
   - Product Inquiry Guidance: 49% → 70-75%
   - User Satisfaction: 92% → 95-96%
   - Handoff Completion: 75% → 85-88%

4. **Visual polish:** Left border accents on improvement/proposed change cards, fixed arrow rendering, fixed label wrapping

5. **Shared report with Kyle and Ryan** via Slack group DM with full context on the work done

### What's Next — IMMEDIATE

1. **Wait for Kyle/Ryan feedback** on report
2. **Deliver report** to GIC for approval (AI-334)
3. **After approval**: Execute AI-335 through AI-338 (code PR + manual config changes)
4. **Post-deployment**: AI-339 monitoring

## Key References
- **Linear parent**: AI-333 (GIC Agent Improvements — Production Deployment)
- **Production bot:** `66026a302af0870013103b1e` (prod tiledesk) — NO faqs-retriever tool
- **Test bot (dev):** `6787a63d2ea6350012955ed9` (bot_config _id: `6787a63d2ea6350012955ee0`)
- **Prod bot config _id:** `66334509c3ba1c2ecdc87cf0`
- **Rubric:** `3bd8cc49-7eef-4110-95ac-01fdc4419cc5` (5 rules, v2)
- **Test Set:** `0977c5bc-2987-40fa-95bb-31f14781a7c1` (17 items, v4)
- **V3 baseline:** `4ee5b3af-f0b1-43f8-9883-303da9e3927a` — 7/17 (41.2%)
- **Post-implementation:** `0a30f458-7a9d-4b08-8d3e-091dae4cc178` — 12/17 (70.6%)
- **Eval model:** `openai:gpt-4.1` | **Eval DB:** dev cluster, `tiledesk` database
- **Report PDF:** `~/Repositories/indemn-observability/reports/GIC_Agent_Improvement_Report_March_12__2026.pdf`
- **Report data:** `~/Repositories/indemn-observability/data/gic-improvement-report.json`
- **Report renderer:** `~/Repositories/indemn-observability/scripts/generate-gic-improvement-report.jsx`
- **KB retrieval config (FIXED on dev only):**
  - Pinecone namespace: `6613cbc6658ad379b7d516c9` (dev org — where vectors actually exist)
  - KB ID filter: `6852bf20940d780013ef4a28` ("New knowledge base 5" — what vectors are tagged with)
  - top_k: 25
- **Prod Pinecone namespace:** `65eb3f19e5e6de0013fda310` — has ZERO vectors, needs to be changed to dev namespace
- **Prod bot tools:** POLICY CHECK (_id: `67e2916c79a7c700137bf131`), human_handoff (_id: `67e2916c79a7c700137bf12c`, `67e3803879a7c700138954ce`), policy_unavailable (_id: `67e2916c79a7c700137bf11e`)
