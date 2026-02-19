# Audio Transcription

Transcribe Alliance Insurance phone call recordings into text, then extract structured data to define ~20 engagement types for building AI agents (web chat + voice). Audio from Brian Leftwich (Alliance COO), forwarded by Peter Duffy.

## Status
Session 2026-02-18-b. **Pipeline complete.** All 5 steps done — capability document delivered.

**What happened this session:**
- Combined classify + aggregate steps to skip Ollama second pass (~20 hours saved)
- Built enriched working dataset (2MB, all fields from 1,543 substantive extractions)
- Classified all 1,542 calls into 20 engagement types using 5 parallel Claude subagents
- Synthesized per-type capability specs using 4 parallel Claude subagents
- Compiled final capability document: 20 per-type specs with resolution workflows, required knowledge, systems, automation feasibility, and cross-cutting requirements

**Pipeline progress:**
1. ~~Extract~~ (2,156 done)
2. ~~Cluster~~ (20 engagement types defined)
3. ~~Classify~~ (1,542 classified — combined with step 4)
4. ~~Aggregate~~ (20 per-type capability specs synthesized)
5. ~~Capability doc~~ (final deliverable complete)

**Key files:**
```bash
cd projects/audio-transcription

# Final deliverable:
# - artifacts/2026-02-18-capability-document.md — THE document: 20 per-type specs, automation matrix, cross-cutting requirements

# Supporting data:
# - engagement_types.json — 20 type definitions
# - classifications.jsonl — 1,542 file-to-type mappings
# - artifacts/2026-02-18-engagement-type-clustering.md — clustering analysis with examples and patterns
# - extractions/*.json — 2,156 extraction files
# - enriched_intents.jsonl — 1,543 intents with all fields
```

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Phone Call Recordings email | Gmail thread | Thread ID: 19c53c132df8e6eb |
| Apr 22 - July 21.zip | SharePoint | [link](https://myallianceinsurance-my.sharepoint.com/:u:/p/brian/IQBuEoxReAtpSLcFAP-jq1PmAQrGMASjPkP6wD1rDHNvO4E?e=6YsrGa) |
| Oct 21 2025 to Jan 20 2026.zip | SharePoint | [link](https://myallianceinsurance-my.sharepoint.com/:u:/p/brian/IQCZDWxYJBL5QKQ5mhLGZs7GAbTHxH8jNUnjyv2mBUJbdHU?e=8wye4P) |
| Alliance Insurance | Customer | [myallianceinsurance.com](http://www.myallianceinsurance.com/) |
| Qwen3-ASR (MLX) | GitHub | [moona3k/mlx-qwen3-asr](https://github.com/moona3k/mlx-qwen3-asr) |
| Peter's agent scope write-ups | Google Doc | [link](https://docs.google.com/document/d/126_2gj13e_hbSTVrnkqdt6rdnFyBeGz2CVRponqcvYk) |
| Alliance Sales Agent | Discovery | [alliance-sales](https://discovery.indemn.ai/alliance-sales) |
| Alliance Service Agent | Discovery | [alliance-service](https://discovery.indemn.ai/alliance-service) |
| Alliance Internal Agent | Discovery | [alliance-internal](https://discovery.indemn.ai/alliance-internal) |
| Extraction pipeline plan | Plan file | .claude/plans/serialized-exploring-glacier.md |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-16 | [transcription-pipeline-setup](artifacts/2026-02-16-transcription-pipeline-setup.md) | Set up local audio transcription for Alliance phone calls |
| 2026-02-16 | [parallelism-investigation](artifacts/2026-02-16-parallelism-investigation.md) | Can we run multiple transcription processes in parallel on Apple Silicon? |
| 2026-02-17 | [extraction-pipeline-design](artifacts/2026-02-17-extraction-pipeline-design.md) | How to extract structured data from transcripts to build agent capability document |
| 2026-02-18 | [engagement-type-clustering](artifacts/2026-02-18-engagement-type-clustering.md) | What are the natural engagement types in Alliance's phone calls and what does each require? |
| 2026-02-18 | [capability-document](artifacts/2026-02-18-capability-document.md) | What does Alliance's AI agent need to handle, and what are the acceptance criteria for building it? |
| 2026-02-19 | [classify-aggregate-synthesis](artifacts/2026-02-19-classify-aggregate-synthesis.md) | How did we classify 1,543 calls and synthesize capability specs without a second Ollama pass? |

## Decisions
- 2026-02-16: Ollama can't do audio models — ruled out immediately
- 2026-02-16: NeMo + MPS silently corrupts output (conformer encoder attention) — ruled out after extensive debugging
- 2026-02-16: NeMo + CPU works (28s/4min) but mlx-qwen3-asr is faster and native to Apple Silicon
- 2026-02-16: **mlx-qwen3-asr (Qwen3-ASR 0.6B) via MLX** — 24s/4min, native Metal GPU, 2 GB memory
- 2026-02-16: Single process is optimal — unified memory bandwidth is the bottleneck, not GPU cores or RAM capacity
- 2026-02-16: Multi-process fork crashes (Metal context corruption); separate processes work mechanically but reduce total throughput
- 2026-02-16: Use `--shuffle` for representative sampling instead of alphabetical grinding
- 2026-02-17: 2,195 transcripts is sufficient sample — stopped transcription, pivoting to extraction
- 2026-02-17: Extract ALL transcripts (inbound, outbound, internal), filter during clustering — outbound carrier calls contain valuable knowledge
- 2026-02-17: Qwen3-14B via Ollama for extraction — best quality/RAM tradeoff for 24GB M4 Pro
- 2026-02-17: Use Ollama JSON Schema format parameter for grammar-constrained output (not prompt-based)
- 2026-02-18: Extraction takes ~33s/file avg (vs 24s for transcription) — full batch ~20 hours
- 2026-02-18: Qwen3-14B quality is sufficient — 10/10 test extractions were accurate, well-structured
- 2026-02-18: 20 engagement types identified (target was ~20) — validated by 5 independent parallel analyses
- 2026-02-18: 77% of calls end as "callback_needed" — biggest AI agent value is closing the callback loop
- 2026-02-18: Carrier fragmentation (20+ carriers) means agent needs carrier-specific playbooks, not generic answers
- 2026-02-18: Payment processing is the single largest engagement type at 12% — highest automation value
- 2026-02-18: Combined classify + aggregate into single subagent-based step — skipped Ollama second pass entirely, saved ~20 hours
- 2026-02-18: Classification distribution shifted from clustering estimates but all 20 types represented — new-quote (13.6%) overtook make-payment (8.6%) as largest type
- 2026-02-18: 4 automation tiers identified — High (24% of calls: follow-up, payment, documents, info update), Medium-High (10%), Medium (40%), Low (26%)
- 2026-02-18: Phase 1 recommendation: start with High-automation tier (follow-up, payment, document request, info update) — structured workflows, clear resolution criteria, highest ROI

## Open Questions
- None — pipeline complete, capability document delivered
