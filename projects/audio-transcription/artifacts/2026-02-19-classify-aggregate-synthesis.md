---
ask: "How did we classify 1,543 calls and synthesize per-type capability specs without a second Ollama pass?"
created: 2026-02-19
workstream: audio-transcription
session: 2026-02-18-b
sources:
  - type: local
    description: "2,156 extraction JSONs, enriched_intents.jsonl (1,543 substantive), engagement_types.json (20 types)"
  - type: code
    description: "5 parallel Claude subagents for classification, 4 parallel Claude subagents for synthesis"
---

# Combined Classify + Aggregate Synthesis

## Problem

The original pipeline had 3 remaining steps after clustering: classify (Ollama second pass on 2,156 files, ~20 hours), aggregate (per-type synthesis), and capability document. We needed to get from "20 engagement types defined" to "capability document delivered" without burning another day on Ollama.

## Decision: Skip Ollama, Use Claude Subagents

Instead of running Ollama on every extraction a second time, we combined classification and aggregation into a single Claude subagent-based workflow. Classification is a lightweight task (read intent, pick from 20 options) that doesn't need a local LLM — Claude subagents can do it while simultaneously pre-digesting the data for synthesis.

**Time saved:** ~20 hours of Ollama processing eliminated. Total wall-clock time for classify + aggregate + compile: ~30 minutes.

## Method

### Step 1: Enriched Working Dataset
Built `enriched_intents.jsonl` — pulled all useful fields from each of the 1,543 substantive extraction JSONs into a single compact file (2MB). Fields: file, direction, outcome, caller_intent, resolution_steps, knowledge_required, systems_referenced, summary.

The existing `substantive_intents.jsonl` from the clustering step was missing resolution_steps and summary, which are critical for synthesis.

### Step 2: Split into 5 Batches
Same pattern as clustering: 5 files of ~308 lines each (`classify_batch_1.jsonl` through `classify_batch_5.jsonl`). Each batch ~400KB, ~81K tokens — fits comfortably in a subagent context window.

### Step 3: Classify + Pre-digest (5 Parallel Subagents)
Each subagent received their batch + `engagement_types.json` (20 types with descriptions and 3 examples each).

Each subagent did two things per call:
1. **Classified** — assigned best-fit engagement_type id with confidence (high/medium/low)
2. **Pre-digested** — grouped calls by type and produced per-type summaries: count, resolution patterns, knowledge required, systems, outcome distribution, edge cases, representative examples

Output per subagent: `classify_result_[1-5].json` with classifications array + type_digests object.

**Results:**
- 1,542 of 1,543 classified (one dropped in batch 5 — 99.9% coverage)
- Confidence: 80% high, 19% medium, 1% low
- All 20 types represented in every batch

### Step 4: Merge + Verify
Combined all 5 outputs into `classifications.jsonl` (permanent record) and `merged_digests.json` (per-type data from all 5 batches).

Distribution vs. clustering estimates:

| Type | Classified | Clustering Est. | Delta |
|------|-----------|----------------|-------|
| new-quote | 210 (13.6%) | 160 (10%) | +50 |
| billing-question | 145 (9.4%) | 85 (6%) | +60 |
| follow-up | 138 (8.9%) | 70 (5%) | +68 |
| make-payment | 133 (8.6%) | 190 (12%) | -57 |
| renewal-review | 131 (8.5%) | 100 (6%) | +31 |

Shifts are expected — clustering estimates were rough eyeballs from 5 independent agents. The formal classification produced more accurate counts.

### Step 5: Synthesize Per-Type Specs (4 Parallel Subagents)
Grouped the 20 types into 4 groups of 5, balanced by digest size:
- Group 1: new-quote, billing-question, follow-up, make-payment, renewal-review (largest types)
- Group 2: routing-triage, claims, vehicle-change, document-request, coverage-question
- Group 3: cancellation, coverage-modification, reinstatement, mortgage-lender, info-update
- Group 4: coi-request, commercial-specialty, dmv-compliance, workers-comp, driver-change

Each subagent received merged digests for their 5 types + cross-cutting patterns from the clustering artifact. Each produced per-type capability specs with: typical caller, resolution workflow, required knowledge, systems & tools, outcome distribution, edge cases & escalation triggers, automation feasibility, and concrete agent requirements.

### Step 6: Compile Capability Document
Merged all 20 per-type specs with an executive summary, automation prioritization matrix, and cross-cutting requirements section into the final deliverable: `artifacts/2026-02-18-capability-document.md`.

## Key Outputs

| File | Purpose |
|------|---------|
| `enriched_intents.jsonl` | Working dataset with all fields (2MB, 1,543 lines) |
| `classifications.jsonl` | Permanent record: every substantive call mapped to engagement type |
| `merged_digests.json` | Per-type analysis from all 5 classification batches (350KB) |
| `classify_result_[1-5].json` | Raw classification + digest output per batch |
| `synthesis_group_[1-4].md` | Per-type capability specs from synthesis subagents |
| `artifacts/2026-02-18-capability-document.md` | **Final deliverable** |

## Subagent Architecture

```
enriched_intents.jsonl (1,543 calls)
    ├── classify_batch_1.jsonl (309) ──→ Subagent 1 ──→ classify_result_1.json
    ├── classify_batch_2.jsonl (309) ──→ Subagent 2 ──→ classify_result_2.json
    ├── classify_batch_3.jsonl (309) ──→ Subagent 3 ──→ classify_result_3.json
    ├── classify_batch_4.jsonl (308) ──→ Subagent 4 ──→ classify_result_4.json
    └── classify_batch_5.jsonl (308) ──→ Subagent 5 ──→ classify_result_5.json
                                              │
                                    merged_digests.json
                                              │
    ├── Group 1 (5 types) ──→ Synthesis Agent 1 ──→ synthesis_group_1.md
    ├── Group 2 (5 types) ──→ Synthesis Agent 2 ──→ synthesis_group_2.md
    ├── Group 3 (5 types) ──→ Synthesis Agent 3 ──→ synthesis_group_3.md
    └── Group 4 (5 types) ──→ Synthesis Agent 4 ──→ synthesis_group_4.md
                                              │
                              capability-document.md (final)
```

## Automation Tiers (from capability document)

| Tier | Types | % of Calls | Automatable |
|------|-------|------------|-------------|
| **P1 — High** | Follow-up, Make Payment, Document Request, Info Update | 24% | 50-80% |
| **P2 — Medium-High** | Coverage Mod, Coverage Question, COI, Driver Change, Routing/Triage | 18% | 40-65% |
| **P3 — Medium** | New Quote, Billing Question, Cancellation, Mortgage/Lender, DMV/Compliance | 30% | 25-50% |
| **P4 — Low** | Renewal Review, Claims, Reinstatement, Workers' Comp, Commercial/Specialty | 26% | 10-25% |

## Complete Pipeline Summary

| Step | Tool | Time | Output |
|------|------|------|--------|
| Transcribe | Qwen3-ASR 0.6B via MLX | ~15 hours | 2,196 transcripts |
| Extract | Qwen3-14B via Ollama | ~20 hours | 2,156 extraction JSONs |
| Cluster | 5 parallel Claude subagents | ~20 min | 20 engagement types |
| Classify + Aggregate | 5 + 4 parallel Claude subagents | ~30 min | 1,542 classifications + 20 capability specs |
| Compile | Manual synthesis | ~10 min | Capability document |
| **Total** | | **~36 hours** | **From raw audio to agent spec** |
