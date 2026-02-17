# Audio Transcription

Transcribe Alliance Insurance phone call recordings into text, then extract structured data to define ~20 engagement types for building AI agents (web chat + voice). Audio from Brian Leftwich (Alliance COO), forwarded by Peter Duffy.

## Status
Session 2026-02-17-a closed. Extraction pipeline designed and built. Ready to test and run.

**What happened this session:**
- Stopped overnight transcription at 2,195 files (random sample sufficient)
- Gathered full Alliance context from Gmail and Slack — agent scope, commitments, CDD strategy
- Designed 5-step extraction pipeline: extract → cluster → classify → aggregate → capability doc
- Built `extract.py` — Ollama + Qwen3-14B with JSON Schema-constrained structured output
- Pulled Qwen3-14B model (9.3GB) into Ollama
- Created 9 beads tasks with dependencies for full pipeline tracking

**To resume:**
```bash
cd projects/audio-transcription

# Make sure Ollama is running
ollama serve &  # or check: ollama list

# Test on 10 files first
.venv/bin/python extract.py transcripts --limit 10 --shuffle

# Then full batch
.venv/bin/python extract.py transcripts --resume --shuffle --manifest
```

**Next up:** Test extraction on 10 samples (beads: audio-transcription-0wu), then run full batch overnight.

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

## Open Questions
- How long does extraction take per file? (need to test — likely slower than transcription since LLM generation is involved)
- Will Qwen3-14B quality be sufficient for structured extraction, or do we need Claude API for step 1?
- What's the right number of engagement types? CDD said ~20, but data may show more or fewer
