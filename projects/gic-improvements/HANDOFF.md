# GIC Improvements — Session Handoff

## Resume Instructions
Read these files in order:
1. `projects/gic-improvements/INDEX.md` — project status, evaluation IDs, open questions
2. `projects/gic-improvements/PLAN.md` — end-to-end plan (Phases 1-6)
3. `projects/gic-improvements/artifacts/2026-03-12-baseline-evaluation-results.md` — baseline: 13/15, full analysis
4. `projects/gic-improvements/artifacts/2026-03-12-evaluation-criteria.md` — per-opportunity baselines, test case designs, projected impact
5. `projects/gic-improvements/artifacts/2026-03-12-opportunity-prioritization.md` — 7 active opportunities, 5 parked, 2 bundled
6. `projects/gic-improvements/artifacts/2026-03-12-agent-research.md` — agent config, system prompt, tools, policy API (reference as needed)

## What Was Done

### Sessions 2026-03-12-a through 2026-03-12-c (Research → Eval Setup)
See previous handoff sections in git history.

### Session 2026-03-12-d (Eval Environment Audit)
1. Discovered eval environment had 5 critical differences from production
2. Fixed 4: KB namespace, AgencyCode hardcode, test data curation, identify_next_step re-enable
3. Applied local bot-service fix for IndexError at `bot_agent_graph.py:421`
4. Identified evaluator model caching issue — stale `claude-sonnet-4-5-20250514` config persisting

### Session 2026-03-12-e (Evaluator Fix + Baseline)
1. **Found the evaluator model cache bug:** The eval service uses `dev/tiledesk` DB (not `dev/evaluations`) because the evaluations repo has its own `.env` file with `MONGODB_DATABASE=tiledesk` that overrides the local-dev settings. The stale `evaluator_configs` document was in `dev/tiledesk`, not where we were looking (`dev/evaluations`).
2. **Deleted the stale evaluator config** (had `anthropic:claude-sonnet-4-5-20250514`, which 404s) and switched to `openai:gpt-4.1` to avoid Anthropic rate limits.
3. **First baseline run with gpt-4.1 (v1 rubric):** `1ddb3f3d` — 1/15 passed. Rule 03 (persona) failed on 14/15 items due to subjective evaluation criteria ("contextually appropriate").
4. **Analyzed results with /eval-analysis skill.** Found Rule 03 was inconsistently evaluated and overly strict — the only PASS (Item 10) had identical behavior to failures.
5. **Rewrote Rule 03** (rubric v2): Removed subjective "identifies as Fred when contextually appropriate" → replaced with concrete pass/fail conditions focused on professional tone, not claiming to be someone else, and not denying identity when asked.
6. **Clean baseline run (rubric v2):** `081e50a2` — **13/15 passed (86.7%)**. All 5 rubric rules at 100%. The 2 failures are both handoff workflow gaps (contact collection + fallback behavior).
7. **Saved baseline artifact** with full conversation transcripts for failed items.

## What's Next — Phase 2 Implementation

The baseline is established. Proceed to Phase 2 per PLAN.md. The implementation groups:

### Group A — System Prompt + Opener (Opportunities #3, #4, #7, #14)
- Opener rewrite with specific capabilities
- Expectations gap: tell users upfront the bot can't generate quotes
- After-hours detection and messaging
- Direct request phrasing instead of indirect questions

### Group B — Operations API Code (Opportunity #5, bundle #10)
- Policy number normalization in `operations_api/src/services/customers/gic_policy_details.ts`
- Add expiration date to POLICY CHECK tool output instructions

### Group C — Knowledge Base (Opportunity #6, bundle #11)
- WC class code appetite data
- Portal URLs in KB entries

### Group D — Handoff Fallback (Opportunity #13)
- **This directly addresses the 2 baseline failures**
- Pre-handoff contact collection
- Handoff expectation setting
- Failed handoff fallback behavior

### Implementation order suggestion:
Start with **Group D** (handoff) — it directly fixes the 2 baseline failures and gives immediate eval improvement signal. Then Group A (prompt), then Group B (API code), then Group C (KB).

## Key References
- **Production bot:** `66026a302af0870013103b1e` (prod tiledesk)
- **Test bot (dev):** `6787a63d2ea6350012955ed9` (dev tiledesk, bot_config _id: `6787a63d2ea6350012955ee0`)
- **Rubric ID:** `3bd8cc49-7eef-4110-95ac-01fdc4419cc5` (5 rules, **v2** — calibrated Rule 03)
- **Test Set ID:** `0977c5bc-2987-40fa-95bb-31f14781a7c1` (15 items, **v2** with real policy numbers)
- **Baseline Run:** `081e50a2-425f-40c8-a01f-5e43985a7f34` (13/15 — valid baseline)
- **Invalidated runs:** `c3e2e2f6` (wrong env), `7188e60e` (bot crash), `163ed045` (early crash), `1ddb3f3d` (uncalibrated rubric v1), `457a2e6a` (aborted, rate limits), `66ebc99d` (stuck)
- GIC org: `65eb3f19e5e6de0013fda310` | project: `65eb3f65e5e6de0013fda4f9`
- Policy API: `https://dev.ops.indemn.ai/v1/gic/policyDetails` (both dev and prod proxy to same GIC backend)
- Agency 5883 verified policies: `0185FL00190350` (active), `0185FL00183217` (cancelled), `0185FL00141155` (cancelled)
- COP-330 (Linear, Backlog): "Support input parameters for test scenarios"
- Bot-service IndexError: `bot_agent_graph.py:421` — local fix applied, not committed
- **Eval DB:** dev cluster, `tiledesk` database (NOT `evaluations`) — caused by evaluations repo `.env` file
- Evaluations: port 8002 | Bot-service: port 8001
- Eval model: `openai:gpt-4.1` (avoid Anthropic due to rate limits)

## Key Decisions
- Using existing dev bot `6787a63d2ea6350012955ed9` (synced to match prod) as test bot
- Rubric follows Percy skill: 3-6 universal rules only, workflow-specific behaviors in scenario success criteria
- KB namespace pointed at prod GIC Pinecone namespace (read-only retrieval) — Craig approved
- Policy API stays on dev (`dev.ops.indemn.ai`) — verified identical to prod
- AgencyCode hardcoded to `5883` — long-term fix is COP-330 (init_parameters for test scenarios)
- Test set uses real policy numbers curated from agency 5883 conversations
- `identify_next_step_enabled` re-enabled with local bot-service bugfix
- Eval model: `openai:gpt-4.1` (not Anthropic — rate limited)
- Rule 03 rewritten to focus on professional tone, not persona identification frequency
