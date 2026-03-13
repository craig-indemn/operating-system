# GIC Improvements — Session Handoff

## Resume Instructions
Read these files in order:
1. `projects/gic-improvements/INDEX.md` — project status, evaluation IDs, open questions
2. `projects/gic-improvements/PLAN.md` — end-to-end plan (Phases 1-6)
3. `projects/gic-improvements/artifacts/2026-03-12-opportunity-prioritization.md` — 7 active opportunities

## Current State

**Phase 4 (Production Deployment) IN PROGRESS. Linear tickets created (AI-333 parent + 6 sub-issues). Customer report PDF generated — needs minor fixes before delivery.**

### What Was Done This Session (2026-03-12-h)

1. **Production bot investigation** — confirmed prod bot (`66026a302af0870013103b1e`) has NEVER had a faqs-retriever tool. Only tools: POLICY CHECK, human_handoff (x2), policy_unavailable. Has 3 KB mappings (270 QNA entries + 2 FILE KBs from Jul 2025) but no way to query them.

2. **Pinecone namespace confirmed empty** — prod org namespace `65eb3f19e5e6de0013fda310` has zero vectors across entire Pinecone index. ALL GIC bots in prod (including newer Voice Prototype #2, WC Intake, Doc Retriever) point to this empty namespace. GIC vectors only exist in dev namespace `6613cbc6658ad379b7d516c9` (30,971 vectors).

3. **GIC org inventory** — 8 bots in GIC prod org. 3 newer bots have faqs-retriever tools but broken retrieval (same empty namespace). New KBs added Jul 2025: "Broker Portal Troubleshooting FAQ" (FILE, 1 source), "Email, Document Routing FAQ" (FILE, 1 source). Also: "GIC-Crawl-Nov_2025" (URL, 16 sources).

4. **Linear tickets created** — parent AI-333 with 6 sub-issues:
   - AI-334: Generate improvement report (customer deliverable) — **blocking, must complete first**
   - AI-335: Deploy policy number normalization (code PR)
   - AI-336: Add faqs-retriever + fix KB config on prod bot (manual config, includes MongoDB commands)
   - AI-337: Apply system prompt + opener updates (manual config, full prompt in comment)
   - AI-338: Update POLICY CHECK tool output instructions (manual config)
   - AI-339: 4-week post-deployment monitoring
   All under project "Automated Testing and Evaluation", team "Agentic AI", label "GIC", assigned Craig.

5. **Customer report PDF generated** — 7-page branded report at `~/Repositories/indemn-observability/reports/GIC_Agent_Improvement_Report_March_12__2026.pdf`
   - Data: `indemn-observability/data/gic-improvement-report.json`
   - Renderer: `indemn-observability/scripts/generate-gic-improvement-report.jsx`
   - Pages: Cover, Current Performance, Opportunities, Improvements Validated (2 pages), Proposed Changes, Monitoring Plan
   - **Known issues to fix**: (1) "Autonomous Resolution Rate" label wraps awkwardly on page 2, (2) → arrows render as apostrophes in before/after text on pages 4-5
   - **User has additional feedback** to incorporate in next session

### What's Next — IMMEDIATE

1. **Fix report rendering issues** and incorporate user feedback (they said they have feedback)
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
