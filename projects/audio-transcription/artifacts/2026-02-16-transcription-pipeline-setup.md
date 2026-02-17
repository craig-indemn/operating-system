---
ask: "Set up local audio transcription for Alliance Insurance phone call recordings on MacBook Pro"
created: 2026-02-16
workstream: audio-transcription
session: 2026-02-16-a
sources:
  - type: gmail
    description: "Peter Duffy forwarded email from Brian Leftwich (Alliance COO) with two SharePoint zip links containing phone call recordings"
  - type: web
    ref: "https://huggingface.co/nvidia/canary-qwen-2.5b"
    name: "NVIDIA Canary-Qwen-2.5B model page"
  - type: web
    ref: "https://github.com/moona3k/mlx-qwen3-asr"
    name: "mlx-qwen3-asr — native Apple Silicon ASR"
---

# Transcription Pipeline Setup

## Summary

Built a local audio transcription pipeline for 37,005 Alliance Insurance phone call recordings (9.4 GB) running on MacBook Pro M4 Pro (24 GB). After evaluating multiple approaches, settled on **mlx-qwen3-asr** (Qwen3-ASR 0.6B) running natively on Apple Silicon via MLX.

## Model Selection Journey

| Approach | Result |
|----------|--------|
| **Ollama + Canary-Qwen** | Dead end — Ollama doesn't support audio models |
| **NeMo + CPU** | Works, 28.4s/4min call, correct output |
| **NeMo + MPS (fp32)** | OOM — model too large for GPU at fp32 |
| **NeMo + MPS (fp16)** | Fits in memory, but produces garbage output ("Transcript") |
| **NeMo + MPS (bf16)** | Partial output then degeneration ("Okay,!!!!!!!") |
| **NeMo + MPS (fp32, chunked)** | No OOM, still garbage — MPS fallback ops silently corrupt conformer encoder attention |
| **mlx-qwen3-asr (MLX native)** | 24.2s/4min call, perfect output, native GPU acceleration |

**Root cause of NeMo MPS failure:** The FastConformer encoder uses attention operations that MPS computes incorrectly (silent corruption, no errors). Even without the fallback flag, MPS runs but produces wrong results. This is a fundamental NeMo/MPS incompatibility, not a configuration issue.

## Final Stack

- **Model:** Qwen3-ASR 0.6B via mlx-qwen3-asr 0.2.3
- **Framework:** MLX 0.30.6 (Apple's native ML framework for Apple Silicon)
- **GPU:** M4 Pro Metal GPU, ~2 GB per process
- **Speed:** 24.2s for a 4-minute call (~10x real-time)
- **Quality:** WER 2.29% on LibriSpeech clean (state-of-the-art for this size)
- **Features:** Word-level timestamps, speaker diarization (optional)

## Audio Data Profile

- **Source:** Alliance Insurance phone system (Brian Leftwich, COO)
- **Files:** 37,005 WAV files across two date ranges
  - Apr 22 – Jul 21 (5.2 GB zip)
  - Oct 21, 2025 – Jan 20, 2026 (3.7 GB zip)
- **Format:** GSM-MS codec, 8kHz mono, 13 kb/s
- **Sizes:** 60 bytes (empty) to 8.5 MB (~87 min)
- **After filtering (>1KB):** ~30,800 files

## Parallelism Finding

Attempted multi-process parallelism (`multiprocessing.fork` with 4 workers). Results:

1. **Fork + shared queue:** 3 of 4 workers exited immediately (queue race condition)
2. **Fork + split lists:** Crashed machine — one process hit 72 GB RAM. `fork` on macOS corrupts Metal GPU contexts, causing runaway memory allocation.
3. **Subprocess isolation:** Each worker runs at ~2 GB, safe — but each takes 42s instead of 24s because they share the same GPU.

**Conclusion:** Single-process is optimal for single-GPU work. The Metal GPU is the bottleneck; multiple processes just split GPU time without throughput gain.

## Pipeline Usage

```bash
cd projects/audio-transcription

# Run (ctrl-c safe, restart with --resume)
.venv/bin/python transcribe.py audio_files --output-dir transcripts --manifest --resume

# With timestamps
.venv/bin/python transcribe.py audio_files --output-dir transcripts --manifest --resume --timestamps
```

- `--resume` skips files with existing transcripts
- `--manifest` writes incremental JSONL (appends per file, survives ctrl-c)
- `--timestamps` adds word-level timing
- Model loads once via `Session` API, reuses for all files

## Estimated Runtime

- ~30,800 files at ~10-20s avg per file ≈ **85-170 hours (3.5-7 days)**
- Safe to stop and restart anytime with `--resume`

## Sample Transcript

**File:** `q-300-+13364138311-20250930-164205-1759264925.7795.WAV` (4m 10s)

> Good afternoon. Thank you for calling Alliance Insurance. This is Gina. Hi, my name is Lauren Douglas, and I was just calling. Um, I just sold my car and I dropped my tag off today, so I was just calling just to cancel my insurance. Okay, and it's under your name, Lauren Douglas. Yes, ma'am. All right, in just a moment. [...]
