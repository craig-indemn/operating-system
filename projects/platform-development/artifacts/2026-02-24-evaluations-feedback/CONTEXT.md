---
ask: "Deep dive into COP-325 evaluations feedback — comprehensive context for session continuity"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-a
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

We are NOT implementing yet — we are building the spec first. Implementation comes after all items are understood.

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
| Agent detail (V1) | `indemn-platform-v2/ui/src/pages/AgentDetailV1.tsx` | Agent card page with purple theme issue |
| Scoring logic | `indemn-platform-v2/ui/src/lib/scoring.ts` | Two-score system (criteria vs rubric) |
| Run modal | `indemn-platform-v2/ui/src/components/evaluation/RunEvaluationModal.tsx` | "None (criteria only)" option |
| Theme/colors | `indemn-platform-v2/ui/src/index.css` | CSS variables, brand colors, light/dark mode |
| Federation styles | `indemn-platform-v2/ui/src/federation/styles.ts` | Inlined Tailwind for federation |
| Constants | `indemn-platform-v2/ui/src/components/evaluation/constants.ts` | Component scope colors (purple!) |
| Test set detail | `indemn-platform-v2/ui/src/components/evaluation/TestSetDetail.tsx` | Uses `purple-500` for scenario badges |
| Tool log append | `evaluations/src/indemn_evals/engine/single_turn.py` lines 60-86 | `_format_tool_trace()` |
| Evaluator builder | `evaluations/src/indemn_evals/engine/builders.py` | Criteria + rubric evaluator prompts |
| Summary dashboard | `indemn-platform-v2/ui/src/components/evaluation/EvaluationSummaryDashboard.tsx` | Shows both scores |

## Indemn Brand Colors (from index.css)

```
--color-iris: #4752a3       (primary brand blue)
--color-lilac: #a67cb7      (secondary)
--color-eggplant: #1e2553   (dark background)
--color-lime: #e0da67       (accent)
Light mode background: #f8f9fc
Light mode surface-1: #ffffff
Light mode surface-2: #f0f1f5
```

The copilot-dashboard (Angular) uses a dark navy/eggplant color scheme. The React components should match.

## Evaluation Data Model (two-tier scoring)

- **Criteria Score**: `criteria_passed / criteria_total` — checks per-item `success_criteria`
- **Rubric Score**: `rubric_rules_passed / rubric_rules_total` — checks universal rubric rules
- **Overall pass**: `criteria_passed AND rubric_passed`
- Both scores displayed separately in the UI (this is Issue 10)

## Dev Evaluation Runs (Wedding Bot)

| Run ID | Date | Total | Passed | Test Set | Notes |
|--------|------|-------|--------|----------|-------|
| `8970c070` | Feb 24, 09:54 | 14 | 5 | `7be041da` (14 items) | Dhruv's latest run — matrix NOT showing (Issue 6) |
| `7c5ce17d` | Feb 24, 04:24 | 15 | 14 | `3e3c1f7c` (15 items) | Our run — matrix works |
| `5b841c47` | Feb 23, 21:12 | 15 | 10 | `3e3c1f7c` (15 items) | **Dhruv's screenshot run** — shows raw dict + R05 failures |

Rubric used: `6ece933d` — "Wedding Bot Rubric" with 6 rules:
- R01: Professional and User-Friendly Tone (medium, persona)
- R02: No Fabrication or Assumption (high, instruction_compliance)
- R03: Stays Within Wedding Insurance Scope (medium, instruction_compliance)
- R04: No Harmful or Inappropriate Content (high, safety)
- R05: Response Clarity and Coherence (medium, response_quality)
- R06: Empathetic and Persistent Information Collection (low, persona)

---

## Progress: Issues Completed

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
1. **TestSetDetail.tsx** lines 120, 211: `purple-500` → `blue-800` for scenario badges/filter (Option A: different blue shades for single_turn vs scenario)
2. **constants.ts** line 7: `#8b5cf6` → `#1E40AF` for prompt scope color
3. **AgentDetailV1.tsx** lines 225/237/258, **FederatedEvaluationRunDetail.tsx** lines 149/163, **EvaluationsPanel.tsx** line 127: `bg-background` (`#f8f9fc`) → `bg-transparent` in federated paths so Angular host white shows through
4. **ComponentScoreBadge.tsx** lines 47-53: Tailwind default `green-600/yellow-600/red-600` → design system tokens `text-success/text-warning/text-error`

### Issue 5: Remove Metadata Section ✅

**File:** `issue-05-remove-metadata.md`

Remove Run ID and Agent ID from the run detail view — internal IDs shouldn't be shown to end users. Keep Progress, Test Items, Rubric, Test Set. Changes to `EvaluationRunDetail.tsx` (lines 152-169) and `FederatedEvaluationRunDetail.tsx` (lines 162, 194-202).

### Issue 6: Matrix Not Showing for New Evaluation ✅

**File:** `issue-06-matrix-not-showing.md`

Verified against live data: run `8970c070` HAS a rubric, the evaluator config EXISTS with 6 evaluators, and the V1 `scores` field IS populated alongside V2 fields (no data format mismatch — previous session's hypothesis was wrong). Root cause: V2 runs default to "cards" view mode, not matrix. V1 runs show the matrix directly. Fix: add `useEffect` to default to matrix view when evaluator config is available.

---

## Progress: Issues Not Yet Started

### Issue 7: Test Set Not Showing in Detail View

`EvaluationRunDetail.tsx` doesn't fetch the TestSet object — it only has `run.test_set_id` as a reference. The detail view needs to load the actual test set to display it. The EvaluationsPanel has a `testSetMap` for the list view but the detail page doesn't.

### Issue 8: Clarify "instruction_compliance" Metric

`instruction_compliance` is a **rubric rule category** (not a standalone metric). Defined in Jarvis's rubric_creator prompt in `percy-service/scripts/seed_jarvis_templates.py`. Rules with `category: "instruction_compliance"` test whether the agent follows its configured instructions. Dhruv also wants a writeup on how "category" works — need to document: categories are semantic groupings (persona, instruction_compliance, safety, response_quality), component_scopes are technical groupings (prompt, knowledge_base, function, general).

### Issue 9: "None (criteria only)" Rubric Option

`RunEvaluationModal.tsx` lines 139-141 — when using a V2 test set, the rubric dropdown includes an empty option "None (criteria only)". This means run with success_criteria evaluation only, no rubric rules. This is working as designed but may need better labeling/documentation.

### Issue 10: Two Different Scores (98% vs 93%)

`lib/scoring.ts` — two independent metrics:
- **Criteria Score** = `criteria_passed / criteria_total` (98%)
- **Rubric Score** = `rubric_rules_passed / rubric_rules_total` (93%)

Displayed separately in `EvaluationSummaryDashboard.tsx`. The 98% is in the run detail, the 93% is the rubric score shown alongside. Need to make the UI clearer about what each score means.

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

## Dev EC2 Access

```bash
ssh -i /Users/home/Repositories/ptrkdy.pem ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com
```

- Evaluations container: `docker logs evaluations`, `docker restart evaluations`
- Internal API: `docker exec evaluations curl -s http://localhost:8000/api/v1/...`
- Container had stale MongoDB connection (replica set primary election). Restarted this session — API working now.
- 1,511 zombie processes on this EC2 (noted but not addressed)

## Next Steps

1. **Continue writing up remaining issues one at a time**: 7, 8, 9, 10, then Dolly's 11-14, then Dhruv's S1-S3
2. For each, read the relevant code in `indemn-platform-v2/ui/src/`, check live data via `https://devevaluations.indemn.ai/api/v1/` (API is working), and produce a file with: feedback quote, code-grounded assessment, resolution with specific file/line changes, and draft Linear response
3. Once all issues are documented, compile into a single implementation plan
4. Implementation order: trivial UI fixes first (2, 3/4, 5), then data bugs (1A, 6, 7), then evaluator logic (1B, 11), then features (8, 9, 10, 12-14, S1-S3)

## Key Decisions Made This Session

- **Colors must match Angular host**: The copilot-dashboard Angular app uses `$brand-primary: #1E40AF`, `tw-bg-white`, `tw-text-slate-800`, Tailwind blue family. Federated React components must use these colors, NOT the React app's own `index.css` design system (`--color-iris: #4752a3`, etc.).
- **Option A for type badges**: Use different blue shades — `blue-500` for single_turn, `blue-800` for scenario — to maintain visual differentiation within the Angular palette.
- **Issue 4 folded into Issue 3**: Both are about federated components not matching the Angular host visually. Single spec file covers both.
- **V1/V2 data format mismatch was wrong**: The backend populates BOTH `scores` (V1 keys) and `rubric_scores`/`criteria_scores` (V2 arrays) on the same result. `buildMatrixData()` works with V2 results because V1 `scores` keys are present.
