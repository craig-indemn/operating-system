---
ask: "Deep dive into COP-325 evaluations feedback — comprehensive context for session continuity"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-b
sources:
  - type: linear
    description: "COP-325 - Evaluations Feedback - UI & Functional Issues (created by Dhruv)"
  - type: slack
    description: "Dhruv's message in #dev-squad thread ts=1771886515.822799"
  - type: mongodb
    description: "Dev evaluations DB — runs, results, rubrics, test sets for Wedding Bot (agent 676be5cbab56400012077f4a)"
  - type: github
    description: "indemn-platform-v2/ui/src (React evaluation components), evaluations/src (backend), percy-service (Jarvis)"
---

# COP-325: Evaluations Feedback Deep Dive — Session Context

## What We're Doing

Dhruv (Engineering Lead) tested the evaluations feature on dev and filed **COP-325** with 10 feedback items + screenshots. Dolly (QA) added 3 more in comments. Dhruv also posted in #dev-squad with 3 strategic asks. We are deep-diving into each item, grounding it in the codebase and live data, then building a comprehensive specification for resolving all of them.

## Methodology

For EACH feedback item, we create a file (`issue-NN-slug.md`) containing:
1. **Feedback** — exact quote from Dhruv/Dolly
2. **Assessment** — what's happening in the code and data (grounded, not speculative)
3. **Resolution / Implementation** — specific code changes with file paths and line numbers
4. **Linear Response** — draft comment to post on COP-325 after testing, to close the item

## Architecture (critical context)

- **Evaluation React UI** lives in `indemn-platform-v2/ui/src/` (NOT the evaluations repo)
- React components are served via **Module Federation** into the Angular copilot-dashboard
- Angular wrappers in `copilot-dashboard/src/app/_react_wrappers/` mount React components
- **Evaluations backend** lives in `evaluations/src/indemn_evals/` (FastAPI + MongoDB)
- **Percy-service** handles Jarvis (agent builder) and baseline generation
- Dev EC2: `ssh -i /Users/home/Repositories/ptrkdy.pem ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com`
- Dev evaluations API: `https://devevaluations.indemn.ai/api/v1/` (container was restarted this session — had stale MongoDB connection)
- Dev MongoDB: `MONGODB_DEV_URI` env var (evaluations database)
- Wedding Bot agent_id: `676be5cbab56400012077f4a`

## Key Files

| Area | File | Purpose |
|------|------|---------|
| Matrix view | `indemn-platform-v2/ui/src/components/evaluation/utils.ts` | `buildMatrixData()` — line 113 is the raw dict bug |
| Matrix component | `indemn-platform-v2/ui/src/components/evaluation/EvaluationMatrix.tsx` | Renders the grid |
| Runs table | `indemn-platform-v2/ui/src/components/evaluation/EvaluationsPanel.tsx` | Runs list with date column |
| Run detail | `indemn-platform-v2/ui/src/pages/EvaluationRunDetail.tsx` | Detail view with metadata, matrix, cards |
| Federated run detail | `indemn-platform-v2/ui/src/federation/components/FederatedEvaluationRunDetail.tsx` | Federated version — test set bug here |
| Agent detail (V1) | `indemn-platform-v2/ui/src/pages/AgentDetailV1.tsx` | Agent card page with purple theme issue |
| Scoring logic | `indemn-platform-v2/ui/src/lib/scoring.ts` | Two-score system — fallback bug here |
| Run modal | `indemn-platform-v2/ui/src/components/evaluation/RunEvaluationModal.tsx` | "None (criteria only)" option |
| Theme/colors | `indemn-platform-v2/ui/src/index.css` | CSS variables, brand colors, light/dark mode |
| Constants | `indemn-platform-v2/ui/src/components/evaluation/constants.ts` | Component scope colors (purple!) |
| Test set detail | `indemn-platform-v2/ui/src/components/evaluation/TestSetDetail.tsx` | Uses `purple-500` for scenario badges |
| Tool log append | `evaluations/src/indemn_evals/engine/single_turn.py` lines 60-86 | `_format_tool_trace()` |
| V2 trigger endpoint | `evaluations/src/indemn_evals/api/routes/evaluations.py` | Scope filter bug lines 632-648 |
| Evaluator builder | `evaluations/src/indemn_evals/engine/builders.py` | Criteria + rubric evaluator prompts |
| Summary dashboard | `indemn-platform-v2/ui/src/components/evaluation/EvaluationSummaryDashboard.tsx` | Shows both scores |

## Dev Evaluation Runs (Wedding Bot)

| Run ID | Date | Total | Passed | Test Set | Rubric | Notes |
|--------|------|-------|--------|----------|--------|-------|
| `8970c070` | Feb 24, 09:54 | 14 | 5 | `7be041da` | `6ece933d` | Dhruv's latest run — rubric works |
| `7c5ce17d` | Feb 24, 04:24 | 15 | 14 | `3e3c1f7c` | `6ece933d` | **Our run — rubric 0/0 due to scope filter "function"** |
| `5b841c47` | Feb 23, 21:12 | 15 | 10 | `3e3c1f7c` | `6ece933d` | **Dhruv's screenshot run** — rubric works (82/90) |

All runs have `question_set_id: null` and `test_set_id: populated`.

Rubric `6ece933d` — "Wedding Bot Rubric" with 6 rules (all `component_scope: prompt or general`, none `function`).

---

## Progress: Issues Spec'd (1-10)

### Issue 1: Matrix View — Raw Dict + Tool Log False Failures ✅

**File:** `issue-01-matrix-question-and-tool-log.md`

**Sub-Issue A (Raw dict):** `utils.ts` line 113 falls back to `JSON.stringify(result.input)` when `input.message` is null (scenarios use `initial_message`). Fix: add fallback chain `message || initial_message || item_name`.

**Sub-Issue B (Tool log):** The `--- TOOL EXECUTION LOG ---` is appended to bot responses before sending to ALL evaluators. Rubric judges (especially R05 Response Clarity) penalize it as "irrelevant padding." R05 has 67% pass rate — worst of all rules — almost entirely due to this. Fix: separate tool log from response for rubric evaluators (Option A, recommended) or add prompt instruction to ignore it (Option B, quick).

### Issue 2: Date Rendering ✅

**File:** `issue-02-date-rendering.md`

The date renders correctly ("Feb 23, 9:12 PM") but the column lacks `whitespace-nowrap`, so it wraps across 3-4 lines when the table is narrow. Fix: add `whitespace-nowrap` to the date cell in `EvaluationsPanel.tsx` line 391.

### Issue 3 + Issue 4: Purple Theme + Card Background ✅

**File:** `issue-03-purple-theme.md` (covers both issues)

Federated React components use off-brand colors that don't match the copilot-dashboard Angular host. Grounded against the Angular app's actual colors: `$brand-primary: #1E40AF`, `tw-bg-white`, `tw-text-slate-800`, `tw-bg-blue-100` sidebar.

4 violations across 6 files:
1. **TestSetDetail.tsx** lines 120, 211: `purple-500` → `blue-800` for scenario badges/filter
2. **constants.ts** line 7: `#8b5cf6` → `#1E40AF` for prompt scope color
3. **AgentDetailV1.tsx** lines 225/237/258, **FederatedEvaluationRunDetail.tsx** lines 149/163, **EvaluationsPanel.tsx** line 127: `bg-background` → `bg-transparent` in federated paths
4. **ComponentScoreBadge.tsx** lines 47-53: Tailwind defaults → design system tokens

### Issue 5: Remove Metadata Section ✅

**File:** `issue-05-remove-metadata.md`

Remove Run ID and Agent ID from the run detail view. Keep Progress, Test Items, Rubric, Test Set. Changes to `EvaluationRunDetail.tsx` (lines 152-169) and `FederatedEvaluationRunDetail.tsx` (lines 162, 194-202).

### Issue 6: Matrix Not Showing — Scope Filter Bug ✅ (REWRITTEN)

**File:** `issue-06-matrix-not-showing.md`

**Original spec was wrong.** The matrix IS showing — it's all dashes/0%. Root cause: run `7c5ce17d` was triggered with `component_scope: "function"` but all 6 rubric rules have scope `prompt` or `general`. The scope filter eliminated all rules, but `rubric_id` was still written to the run. Fix: if scope filter eliminates all rules, proceed criteria-only WITHOUT attaching the rubric. Backend change in `evaluations/src/indemn_evals/api/routes/evaluations.py` after line 646.

### Issue 7: Test Set Not Showing in Detail View ✅

**File:** `issue-07-test-set-not-showing.md`

`FederatedEvaluationRunDetail.tsx` reads V1 `question_set_id` (always null) instead of V2 `test_set_id` (always populated). All runs affected. The correct pattern exists in `EvaluationsPanel.tsx` (`getTestSourceLabel` prefers `test_set_id`). Fix: add `useTestSets` hook, add `getTestSetLabel()`, prefer V2 over V1.

### Issue 8: Clarify "instruction_compliance" Metric ✅ (Linear response only)

**File:** `issue-08-instruction-compliance.md`

Not a bug. Category label on rubric rules. Linear response explains the four categories and the difference between category (semantic) and component_scope (filtering).

### Issue 9: "None (criteria only)" Rubric Option ✅ (Linear response only)

**File:** `issue-09-criteria-only-option.md`

Working as designed. Linear response explains that test sets have per-item success criteria (specific pass/fail for each scenario), rubrics are universal quality rules that apply to every response, and rubric is optional.

### Issue 10: Two Different Scores (98% vs 93%) ✅

**File:** `issue-10-two-scores.md`

The 93% "rubric score" on run `7c5ce17d` is **wrong** — this run has `rubric_rules_total: 0`. The scoring fallback in `scoring.ts` lines 85-99 misinterprets `component_scores` (item-level 14/15 passed) as rubric data when `rubric_rules_total` is 0. Fix: distinguish "field is zero" (new run, criteria-only) from "field doesn't exist" (old run, needs fallback).

---

## Progress: Issues Not Yet Started

### Dolly's Comments (Issues 11-14)

**Issue 11:** Scenario not executing as expected within defined turns should NOT be marked 100% compliant. Example: bot asks same state question multiple times but eval still passes. This is a criteria evaluator quality issue — the judge doesn't penalize repeated questions.

**Issue 12:** Support input parameters for test scenarios (reusable across conditions).

**Issue 13:** Allow repeated execution of the same scenario (regression testing).

**Issue 14:** Selective scenario execution (run subset, not entire suite).

### Dhruv's Strategic Asks (from Slack)

**S1:** Enable evaluations for everyone, not just Support/@indemn.ai users. Currently gated by `isIndemnEmployee` check in copilot-dashboard.

**S2:** Cost guardrails — each eval run uses LLM scoring. Long-term: add limits (X evals per user/day).

**S3:** Documentation — wants a model document for the data flow (MongoDB collections/schema + key fields).

---

## Implementation Plan (Issues 1-10)

### Phase 1: Trivial UI fixes (indemn-platform-v2)

| # | Issue | File(s) | Change |
|---|-------|---------|--------|
| 1 | Issue 2 | `EvaluationsPanel.tsx` | Add `whitespace-nowrap` to date cell |
| 2 | Issue 3+4 | 6 files | Purple → blue, bg-background → bg-transparent, score badge tokens |
| 3 | Issue 5 | `EvaluationRunDetail.tsx`, `FederatedEvaluationRunDetail.tsx` | Remove Run ID + Agent ID |

### Phase 2: Data display bugs (indemn-platform-v2)

| # | Issue | File(s) | Change |
|---|-------|---------|--------|
| 4 | Issue 7 | `FederatedEvaluationRunDetail.tsx` | Add `useTestSets`, prefer `test_set_id` over `question_set_id` |
| 5 | Issue 10 | `scoring.ts` | Fix rubric fallback — check `!== undefined` not `> 0` |
| 6 | Issue 1A | `utils.ts` | Fallback chain: `message \|\| initial_message \|\| item_name` |

### Phase 3: Backend fix (evaluations)

| # | Issue | File(s) | Change |
|---|-------|---------|--------|
| 7 | Issue 6 | `evaluations/api/routes/evaluations.py` | Clear rubric_id when scope filter eliminates all rules |

### Phase 4: Evaluator logic (evaluations)

| # | Issue | File(s) | Change |
|---|-------|---------|--------|
| 8 | Issue 1B | `evaluations/engine/single_turn.py` + `builders.py` | Separate tool log from response for rubric evaluators |

### Phase 5: Linear responses (no code)

| # | Issue | Action |
|---|-------|--------|
| 9 | Issue 8 | Post explanation of instruction_compliance categories |
| 10 | Issue 9 | Post explanation of criteria vs rubric scoring |

### Deploy order

1. Phases 1-2: PR to `indemn-platform-v2` → build federation → deploy `copilot-dashboard-react` container on dev
2. Phases 3-4: Push to `evaluations` main → deploy evaluations container on dev
3. Test all fixes on dev against Wedding Bot
4. Phase 5: Post Linear responses after testing confirms fixes

---

## Dev EC2 Access

```bash
ssh -i /Users/home/Repositories/ptrkdy.pem ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com
```

- Evaluations container: `docker logs evaluations`, `docker restart evaluations`
- Percy-service container: `docker logs percy-service`, `docker restart percy-service`
- Copilot-server: was unhealthy (stale MongoDB connection) — restarted this session
- Percy-service: was also unhealthy (same cause) — restarted this session
- Internal API: `docker exec evaluations curl -s http://localhost:8000/api/v1/...`

## Next Steps

1. **Implement Issues 1-10** following the implementation plan above
2. **Test on dev** — verify each fix against Wedding Bot runs
3. **Post Linear responses** for Issues 8 and 9
4. **Spec Dolly's Issues 11-14** — one at a time, same methodology
5. **Spec Dhruv's strategic asks S1-S3**

## Key Decisions Made

### Session 2026-02-24-a
- **Colors must match Angular host**: `$brand-primary: #1E40AF`, `tw-bg-white`, `tw-text-slate-800`, Tailwind blue family. NOT the React app's `--color-iris: #4752a3`.
- **Option A for type badges**: `blue-500` for single_turn, `blue-800` for scenario.
- **Issue 4 folded into Issue 3**: Both are federated color mismatches.

### Session 2026-02-24-b
- **Issue 6 rewritten**: Original spec was wrong (view toggle hypothesis). Real cause is scope filter eliminating all rubric rules while still attaching rubric_id.
- **Issue 7 root cause**: `FederatedEvaluationRunDetail.tsx` reads V1 `question_set_id` (always null) instead of V2 `test_set_id`.
- **Issue 10 root cause**: `scoring.ts` fallback treats `rubric_rules_total: 0` same as `undefined`, reads `component_scores` as rubric data.
- **Issue 6 fix**: If scope filter eliminates all rules, proceed criteria-only without attaching rubric.
- **Issue 8 and 9 are Linear responses only**: No code changes, just explanations.
- **Dev EC2 MongoDB issue**: copilot-server and percy-service both had stale MongoDB connections (replica set primary election). Restarted both.
