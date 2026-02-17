---
ask: "How do we extract structured data from 2,195 call transcripts to build an AI agent capability document for Alliance Insurance?"
created: 2026-02-17
workstream: audio-transcription
session: 2026-02-17-a
sources:
  - type: gmail
    description: "Alliance email threads — roadmap proposal, solution scoping, AI update, phone recordings, internal agent data ingestion"
  - type: slack
    description: "Slack searches — #customer-implementation, #daily-standup, #customer-success-working for Alliance strategy context"
  - type: code
    description: "mlx-qwen3-asr library analysis, Ollama structured output API research"
  - type: web
    description: "Qwen3 model research — optimal model for 24GB Apple Silicon"
---

# Extraction Pipeline Design

## Business Context

Alliance Insurance (Winston-Salem, NC) gets ~100 missed calls/week. Indemn committed to building web chat + voice agents to handle these calls. Alliance provided 37,005 phone call recordings (9.4GB WAV) from their LightSpeed phone system.

**CDD Feb 16 strategy:** "Distill into roughly 20 engagement types. Emphasis on proprietary knowledge, not channel-based structure."

**Commitments from meetings/Slack:**
- Web chat + voice solution to eliminate 100 missed calls/week
- Renewals automation for routine service tasks
- Bilingual support (Spanish, likely Vietnamese)
- BT Core AMS integration
- No-cost Phase 1 pilot focused on missed calls

**What exists already:**
- External Sales + Service agents (web chat) — live on discovery.indemn.ai/alliance-*
- Internal agent with 44 documents across 6 categories
- Peter's scope write-ups: https://docs.google.com/document/d/126_2gj13e_hbSTVrnkqdt6rdnFyBeGz2CVRponqcvYk

## Transcription Status

- 2,195 of ~30,816 valid files transcribed (random sample via --shuffle)
- Transcription running sequentially at ~24s/file (Qwen3-ASR 0.6B via MLX)
- Parallel MLX doesn't work on Apple Silicon (unified memory bandwidth bottleneck)
- Sample includes: inbound (705), outbound (693), extension transfers (546), queue (168), parked (43), internal (16), attended transfers (14)

## Extraction Pipeline (5 steps)

```
transcripts/*.txt → [extract.py / Ollama Qwen3-14B] → extractions/*.json
    → [cluster / Claude interactive] → engagement_types.json
    → [classify.py / Ollama] → classified extractions
    → [aggregate / Claude per-category] → capability specs
    → final capability document
```

### Step 1: extract.py (BUILT, ready to run)

Script at `projects/audio-transcription/extract.py`. Uses Ollama REST API with JSON Schema-constrained output (grammar-level enforcement, not prompt-based).

**Model:** Qwen3-14B (Q4_K_M, 9.3GB) — pulled and ready in Ollama.

**Extraction schema per transcript:**
- `is_substantive` (bool) — false for voicemails, spam, transfers
- `caller_intent` (string) — what the customer wanted
- `resolution_steps` (string[]) — what the agent did, step by step
- `outcome` (enum) — resolved/transferred/callback_needed/unresolved/voicemail/spam
- `knowledge_required` (string[]) — domain knowledge needed
- `systems_referenced` (string[]) — tools/systems mentioned
- `summary` (string) — 2-3 sentence overview

Call direction parsed from filename prefix (in-/out-/exten-/q-/etc.).

Follows same patterns as transcribe.py: --resume, --shuffle, incremental JSONL manifest, per-file error handling, ctrl-c safe.

### Step 2: Cluster (interactive with Craig)

Sample ~100-150 substantive inbound extractions, feed to Claude to discover natural categories. Refine collaboratively. Save as engagement_types.json.

### Step 3: classify.py (TO BUILD)

Lightweight second pass — reads extraction JSON + engagement type list, adds engagement_type field. Uses Ollama on the summary (not raw transcript) so it's fast.

### Step 4: Aggregate (Claude, per-category)

Each category's extractions fit in context (~100 calls × 200 words = ~20K tokens). Claude synthesizes: typical resolution path, required knowledge, edge cases.

### Step 5: Compile capability document

Final artifact: what Alliance's phone agent needs to handle and how. Acceptance criteria for the AI agent.

## Beads Task Tracking

| ID | Task | Status |
|----|------|--------|
| 77r | Set up Ollama + pull Qwen3-14B | closed |
| lu4 | Build extract.py | closed |
| 0wu | Test extraction on 10 samples | next |
| k71 | Run full extraction batch | blocked by 0wu |
| 4qi | Cluster into engagement types | blocked by k71 |
| taa | Build classify.py | blocked by 4qi |
| 8ct | Run classification batch | blocked by taa |
| z5j | Aggregate per-category specs | blocked by 8ct |
| 8ge | Compile final capability document | blocked by z5j |

## Key Decision: Extract All, Filter Later

Process all 2,195 transcripts (inbound, outbound, internal, etc.) and filter to inbound customer-facing during clustering. Outbound carrier calls contain valuable knowledge about resolution patterns.

## To Resume

```bash
cd projects/audio-transcription

# Test on 10 files first
.venv/bin/python extract.py transcripts --limit 10 --shuffle

# Then full batch overnight
.venv/bin/python extract.py transcripts --resume --shuffle --manifest
```

Ollama must be running: `ollama serve` or check `ollama list`.
