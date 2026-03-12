# GIC Improvements — Session Handoff

## Resume Instructions
Read these files in order:
1. `projects/gic-improvements/INDEX.md` — project status, evaluation IDs, open questions
2. `projects/gic-improvements/PLAN.md` — end-to-end plan (Phases 1-6)
3. `projects/gic-improvements/artifacts/2026-03-12-baseline-evaluation-results.md` — baseline: 13/15 with OLD criteria
4. `projects/gic-improvements/artifacts/2026-03-12-opportunity-prioritization.md` — 7 active opportunities with implementation groups
5. `projects/gic-improvements/artifacts/2026-03-12-agent-research.md` — agent config, system prompt, tools, policy API (reference as needed)

## Current State

**Phase 1 (Evaluation Setup) is complete. Test set v3 criteria have been aligned to opportunities but a NEW BASELINE has NOT been run yet.**

The previous baseline (`081e50a2`, 13/15) used v2 criteria that were too lenient — several opportunities passed when they should fail. The test set was updated to v3 with tightened criteria that will FAIL on pre-improvement behavior and PASS after improvements.

## What Was Done This Session (2026-03-12-e)

1. **Fixed evaluator model cache bug:** Eval service uses `dev/tiledesk` DB (not `dev/evaluations`) because `evaluations/.env` has `MONGODB_DATABASE=tiledesk`. Deleted stale config with `claude-sonnet-4-5-20250514`.
2. **Switched eval model to `openai:gpt-4.1`** — Anthropic rate-limited every run.
3. **Calibrated rubric v2:** Rewrote Rule 03 (persona) from subjective to concrete criteria.
4. **Ran baseline with v2 rubric:** `081e50a2` — 13/15 passed. All rubric rules 100%. 2 handoff failures.
5. **Analyzed baseline:** Found most opportunities incorrectly PASS because criteria accept "graceful failure" instead of requiring the improvement behavior.
6. **Updated test set to v3 (17 items)** — criteria now aligned to each opportunity:

### Test Set v3 Changes (what changed and why)

| Opportunity | Item | Change | Expected Before/After |
|-------------|------|--------|----------------------|
| **#5** Policy parsing | Messy format scenario | Require successful extraction + lookup, not fallback | FAIL→PASS |
| **#10** Expiration date | Happy path policy lookup | Added "displays expiration/renewal date" criterion | FAIL→PASS |
| **#14** Expectations gap | Commercial auto quote | Require portal URL + user choice before collecting info | FAIL→PASS |
| **#4** Direct requests | Info collection scenario | Explicit "What is X?" vs "Could you provide X?" | FAIL→PASS |
| **#6** WC class codes | WC class code question | Require specific content, not "I don't know" | FAIL→PASS |
| **#11** Portal URLs | Portal navigation | Require specific portal URL | FAIL→PASS |
| **#3** Opener | **NEW:** "Greeting - capabilities" | Agent must list specific capabilities on "Hi there" | FAIL→PASS |
| **#7** After-hours | **NEW:** "After-hours handoff failure recovery" | After handoff fails, agent offers alternatives + collects contact info | FAIL→PASS |
| **#13** Handoff fallback | Explicit handoff + Failed handoff | Already fails — no change | FAIL→PASS |

## What's Next — IMMEDIATE

1. **Run new baseline with v3 test set** — this is the true "before" measurement. Expected: many more failures since criteria now test for the improvements we haven't made yet.
   ```
   POST http://localhost:8002/api/v1/evaluations
   {"bot_id": "6787a63d2ea6350012955ed9", "test_set_id": "0977c5bc-2987-40fa-95bb-31f14781a7c1", "rubric_id": "3bd8cc49-7eef-4110-95ac-01fdc4419cc5", "eval_model": "openai:gpt-4.1", "concurrency": 1}
   ```
2. **Analyze v3 baseline with `/eval-analysis`** — save as artifact, confirm each opportunity's items FAIL as expected.
3. **Phase 2 Implementation** — make the actual improvements (Groups A-D per PLAN.md).
4. **Post-implementation eval** — re-run same test set + rubric, compare to v3 baseline.

## Key References
- **Production bot:** `66026a302af0870013103b1e` (prod tiledesk)
- **Test bot (dev):** `6787a63d2ea6350012955ed9` (bot_config _id: `6787a63d2ea6350012955ee0`)
- **Rubric:** `3bd8cc49-7eef-4110-95ac-01fdc4419cc5` (5 rules, **v2**)
- **Test Set:** `0977c5bc-2987-40fa-95bb-31f14781a7c1` (17 items, **v3** — opportunity-aligned criteria)
- **Old baseline (v2 criteria):** `081e50a2-425f-40c8-a01f-5e43985a7f34` — 13/15 (criteria too lenient)
- **Eval model:** `openai:gpt-4.1` | **Eval DB:** dev cluster, `tiledesk` database
- **Eval service .env issue:** `evaluations/.env` has `MONGODB_DATABASE=tiledesk` overriding local-dev settings
- Evaluations: port 8002 | Bot-service: port 8001 (has local IndexError fix at `bot_agent_graph.py:421`)
- AgencyCode hardcoded to `5883` in dev bot POLICY CHECK tool
- KB namespace: `65eb3f19e5e6de0013fda310` (prod GIC, read-only)
