---
ask: "Design exportable deliverables for the CLI — eval reports, agent cards, markdown dumps, and eval analysis skill"
created: 2026-03-13
workstream: jarvis-cli-mcp
session: 2026-03-13-b
sources:
  - type: github
    description: "indemn-platform-v2 React-PDF report components (EvalReportDocument, AgentCardDocument, styles, covers)"
  - type: github
    ref: "indemn-platform-v2/ui/src/components/report/"
    name: "Dashboard PDF report templates"
  - type: github
    ref: "operating-system/.claude/skills/eval-analysis/SKILL.md"
    name: "OS eval-analysis skill (source for CLI adaptation)"
---

# Design: CLI Exports — Eval Reports, Agent Cards, and Analysis

**Date:** 2026-03-13
**Status:** Approved

## Problem

The CLI can manage agents and run evaluations, but can't produce the deliverables the team actually shares — PDF reports and structured analysis. Today you either download from the Copilot Dashboard UI or manually scrape data and pipe through markdown-to-pdf. This adds three CLI commands and one skill to close that gap.

## Scope

**Three CLI commands:**

| Command | Output | Description |
|---------|--------|-------------|
| `indemn eval export <run-id>` | `.md` file | Full markdown dump — conversations, scores, criteria, rubric results |
| `indemn eval report <run-id>` | `.pdf` file | Branded customer-facing PDF, identical to dashboard "Export PDF" |
| `indemn agents card <agent-id>` | `.pdf` file | Branded agent card PDF, identical to dashboard agent detail export |

**One skill:**

| Skill | Description |
|-------|-------------|
| `eval-analysis` | Guides Claude through failure triage using CLI commands. Adapted from the OS eval-analysis skill. |

All commands fetch data from existing API endpoints (Copilot Server + Evaluations Service) and render locally. PDFs use `@react-pdf/renderer` running in Node.js (same library the dashboard uses, works headless). No new server endpoints needed.

## Key Decisions

- Port React-PDF templates from `indemn-platform-v2` rather than rebuilding — identical output to dashboard
- Bundle Barlow font files and logo in the npm package — no external asset fetching
- Agent card uses Copilot Server V1 data only — no platform-v2 dependency
- Eval analysis skill uses CLI commands (not MCP, not curl) — CLI-first
- `@react-pdf/renderer` as new dependency (~5MB) — proven Node.js headless rendering

---

## Data Flow

Each command fetches from APIs the CLI already talks to. No new endpoints needed.

### `eval export` and `eval report` — same data, different output format

1. `GET /runs/{run_id}` — run summary (pass/fail counts, rubric_id, test_set_id, agent_id, component_scores)
2. `GET /runs/{run_id}/results` — per-item results (conversations, criteria_scores, rubric_scores)
3. `GET /rubrics/{rubric_id}` — rubric definition (rules, severity, component_scope)
4. `GET /test-sets/{test_set_id}` — test set definition (items, success_criteria, personas)
5. `GET /bots/{agent_id}/context` — bot context (name, org name — used for report title/customer name)

### `agents card`

1. `GET /organization/:org_id/ai-studio/v2/bots/:id` — agent details (name, description, channels)
2. `GET /organization/:org_id/ai-studio/bots/:id/configurations` — config (system_prompt, LLM model/provider, greeting)
3. `GET /organization/:org_id/ai-studio/bots/:id/functions` — functions list (name, type, description)
4. Agent's knowledge_bases come back in the v2 bots response (already populated)
5. `GET /runs?agent_id={id}&status=completed&limit=10` — recent eval runs for the history page

All calls go through the existing `IndemnClient` SDK. No new SDK methods needed — just new CLI commands that compose existing SDK calls and render output.

---

## CLI Command Design

```bash
# Eval export — markdown dump
indemn eval export <run-id> [--output path.md]
# Default output: ./Indemn_Evaluation_{AgentName}_{Date}.md

# Eval report — branded PDF
indemn eval report <run-id> [--output path.pdf]
# Default output: ./Indemn_Evaluation_{CustomerName}_{Date}.pdf
# Auto-detects V1 (matrix) vs V2 (per-item) from run data

# Agent card — branded PDF
indemn agents card <agent-id> [--output path.pdf]
# Default output: ./Indemn_Agent_Card_{AgentName}_{Date}.pdf
```

All three commands show a spinner while fetching data and generating output, then print the output file path on success.

**`--json` flag:** Not applicable — these commands produce files, not structured data. The existing `eval results <run-id> --json` covers the raw JSON use case.

**MCP tools:** Three new tools to match — `export_eval_markdown`, `export_eval_report`, `export_agent_card`. Each returns the file path of the generated output. This lets Claude generate deliverables in conversation.

---

## PDF Generation — Porting React-PDF Templates

The dashboard uses `@react-pdf/renderer` to generate PDFs client-side in the browser. This same library works in Node.js — we import it, render the React components to a buffer, and write to disk. No browser needed.

### Files ported from `indemn-platform-v2/ui/src/components/report/`

| Dashboard File | CLI File (new) | Purpose |
|---|---|---|
| `styles.ts` | `src/report/styles.ts` | Brand colors, Barlow font registration, shared StyleSheet |
| `AgentCardCover.tsx` | `src/report/agent-card/cover.tsx` | Cover page with name, description, channels, eval summary |
| `AgentCardDocument.tsx` | `src/report/agent-card/document.tsx` | 7-page document (cover, prompt, tools, KBs, LLM config, eval history, metadata) |
| `EvalReportDocument.tsx` | `src/report/eval-report/document.tsx` | V1 (matrix) and V2 (per-item) report formats |
| `EvalReportV2Cover.tsx` | `src/report/eval-report/v2-cover.tsx` | V2 cover with summary stats |
| `EvalReportItemPage.tsx` | `src/report/eval-report/item-page.tsx` | Per-item detail pages |
| `EvalReportCover.tsx` | `src/report/eval-report/cover.tsx` | V1 cover with weighted scores |
| `EvalReportMatrixPage.tsx` | `src/report/eval-report/matrix-page.tsx` | V1 matrix summary |
| `EvalReportExamplePage.tsx` | `src/report/eval-report/example-page.tsx` | V1 per-question detail |

### Adaptations needed

- **Font loading:** Replace `window.location.origin` URL-based font loading with local file paths. Bundle Barlow `.ttf` files (Regular, Medium, SemiBold, Bold) in `src/report/assets/fonts/`.
- **Logo:** Bundle `indemn-logo.png` in `src/report/assets/`.
- **Remove `import.meta.env`:** Node.js doesn't have Vite — replace with direct path resolution via `__dirname` or `import.meta.url`.
- **Agent card data mapping:** Map Copilot Server V1 fields to the `AgentCardData` interface. Skip V2-only fields (`capabilities`, `use_cases`). Lifecycle and owner fields come from the bot response if available.
- **Scoring utilities:** Port `getScoreHexColor()` and `calculateWeightedScores()` as standalone functions in `src/report/scoring.ts`.
- **Render method:** Replace browser `pdf().toBlob()` with Node.js `pdf().toBuffer()`, then `fs.writeFileSync()`.

### New dependency

`@react-pdf/renderer` (~5MB). Already proven in Node.js — the library's `renderToBuffer` API is the headless equivalent of the browser blob generation.

---

## File Structure

```
src/
├── report/
│   ├── styles.ts              # Ported brand styles + font registration
│   ├── scoring.ts             # getScoreHexColor, calculateWeightedScores
│   ├── generate.ts            # renderToBuffer + write-to-disk logic
│   ├── assets/
│   │   ├── fonts/
│   │   │   ├── Barlow-Regular.ttf
│   │   │   ├── Barlow-Medium.ttf
│   │   │   ├── Barlow-SemiBold.ttf
│   │   │   └── Barlow-Bold.ttf
│   │   └── indemn-logo.png
│   ├── agent-card/
│   │   ├── document.tsx       # AgentCardDocument
│   │   └── cover.tsx          # AgentCardCover
│   └── eval-report/
│       ├── document.tsx       # EvalReportDocument (V1 + V2)
│       ├── cover.tsx          # V1 cover
│       ├── v2-cover.tsx       # V2 cover
│       ├── matrix-page.tsx    # V1 matrix
│       ├── example-page.tsx   # V1 per-question
│       └── item-page.tsx      # V2 per-item
├── cli/
│   ├── eval.ts                # Add export + report subcommands
│   └── agents.ts              # Add card subcommand
└── mcp/
    └── tools.ts               # Add export_eval_markdown, export_eval_report, export_agent_card
```

---

## Markdown Export Format

`indemn eval export` produces a structured markdown file with all evaluation data:

```markdown
# Evaluation Results — {agent_name}

Run: {run_id} | Date: {date} | Agent: {agent_id}
Model: {provider}/{model} | Results: {passed}/{total} passed

Component Scores:
- Prompt: {score}% ({passed}/{total})
- Knowledge Base: {score}% ({passed}/{total})
- Function: {score}% ({passed}/{total})
- General: {score}% ({passed}/{total})

---

## Test Case: {name}
**Type:** {type} | **Result:** {PASS/FAIL} | **Duration:** {duration}ms

### Conversation

> **User:** {message}

> **Agent:** {message}

### Criteria Scores
| Criterion | Result | Reasoning |
|-----------|--------|-----------|
| {criterion} | PASS/FAIL | {reasoning} |

### Rubric Scores
| Rule | Severity | Result | Reasoning |
|------|----------|--------|-----------|
| {rule_name} | {severity} | PASS/FAIL | {reasoning} |

---

## Test Case: {next item}
...
```

---

## Eval Analysis Skill

Adapted from the OS skill at `.claude/skills/eval-analysis/SKILL.md`. Ships in `skills/eval-analysis/SKILL.md` inside the `@indemn/cli` package.

### What changes from the OS version

- Replace all `curl` calls with `indemn` CLI commands
- Remove `python3 -m json.tool` — use `--json` flag instead
- Remove OS-specific references (subagents, markdown-pdf skill, project artifacts)
- Steps 1–7 workflow stays the same — Claude does the reasoning

### Command mapping

| OS Skill (curl) | CLI Skill (indemn) |
|---|---|
| `curl .../runs/{run_id}` | `indemn eval status <run-id> --json` |
| `curl .../runs/{run_id}/results` | `indemn eval results <run-id> --json` |
| `curl .../rubrics/{rubric_id}` | `indemn rubric get <rubric-id> --json` |
| `curl .../test-sets/{test_set_id}` | `indemn testset get <testset-id> --json` |
| `curl .../bots/{agent_id}/context` | `indemn eval bot-context <agent-id> --json` |
| `curl -X PUT .../test-sets/{id}` | `indemn testset update <id> --file updated.json` |
| `curl -X PUT .../rubrics/{id}` | `indemn rubric update <id> --file updated.json` |

### The 7-step workflow (unchanged)

1. **Resolve run** — UUID = run_id, ObjectId = agent_id (fetch latest completed run)
2. **Pull all data** — run summary, results, rubric, test set, bot context
3. **Present run overview** — summary table with pass rates and component scores
4. **Analyze each failed item** — Claude classifies: agent/eval/test/KB problem
5. **Aggregate findings** — group by category
6. **Prioritized recommendations** — specific fix text for criteria/rules
7. **Offer to execute fixes** — update test set/rubric via CLI (creates new version, non-destructive)

### Export traces section

Instead of the OS markdown-pdf skill, uses:
- `indemn eval export <run-id>` for the markdown dump
- `indemn eval report <run-id>` for the branded PDF

### Data shapes reference

The `references/data-shapes.md` file ships as-is — the API response shapes are identical regardless of whether you call via curl or CLI.

---

## Implementation Notes

### TypeScript + JSX for React-PDF

The report files use `.tsx` extension for JSX syntax. The `tsconfig.json` already targets ESNext with NodeNext modules. Need to add:
```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "@react-pdf/renderer"
  }
}
```

Actually, `@react-pdf/renderer` uses standard React JSX. We need `react` as a dependency (peer dep of react-pdf) but only for the PDF rendering — it never runs in a browser.

### Asset bundling

Font files and logo need to be included in the npm package. Add to `package.json`:
```json
{
  "files": ["dist/", "skills/", ".claude-plugin/", "src/report/assets/"]
}
```

Or copy assets to `dist/report/assets/` during build.

### Package size

Current: ~85KB. Adding `@react-pdf/renderer` + `react` + font files will increase to ~10-15MB. Acceptable for a CLI tool installed globally.

---

## Version

This ships as `@indemn/cli@1.1.0` (minor version bump — new features, no breaking changes).
