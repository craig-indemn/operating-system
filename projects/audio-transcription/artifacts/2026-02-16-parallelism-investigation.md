---
ask: "Can we run multiple transcription processes in parallel on Apple Silicon to speed up the 30K file batch?"
created: 2026-02-16
workstream: audio-transcription
session: 2026-02-16-b
sources:
  - type: code
    description: "mlx-qwen3-asr library source (site-packages) — encoder, decoder, generate, session modules"
  - type: local
    description: "Live testing of 2-worker parallel transcription on M4 Pro 24GB"
---

# Parallelism Investigation: MLX on Apple Silicon

## Question

With a 2GB model and 24GB RAM, can we run multiple Qwen3-ASR instances in parallel to speed up transcription?

## Answer: No

Multiple MLX processes on Apple Silicon do not increase throughput. In testing, two workers produced fewer total files per minute than a single worker, and made the system sluggish.

## Why

Apple Silicon uses **unified memory** — CPU and GPU share the same memory bus (~273 GB/s on M4 Pro). Transformer inference is memory-bandwidth-bound, not compute-bound. A single MLX process already saturates most of that bandwidth during model weight reads for each generated token.

Running two processes doubles bandwidth demand on a fixed pipe. Both slow down, and macOS itself competes for the same bus, causing system-wide lag.

This is fundamentally different from discrete GPU setups (NVIDIA) where each GPU has dedicated VRAM with its own bandwidth (e.g., A100 has 2 TB/s dedicated).

## What was tried

1. **multiprocessing.fork()** (session 2026-02-16-a) — Crashes. Metal GPU context corruption when forking.
2. **Separate processes via symlink directories** (session 2026-02-16-b) — Works mechanically but total throughput drops. System becomes sluggish. Two workers each run slower than a single worker.

## Library internals (mlx-qwen3-asr v0.2.3)

- `transcribe_batch()` exists but is a sequential loop — no GPU-level batching
- Audio encoder accepts batch dimension `(B, 128, T)` but serializes internally: `for b in range(B): self._encode_single(mel, ...)`
- Autoregressive decoder is single-sequence only
- True batched inference would require forking and rewriting the encoder + decode loop

## What would actually speed this up

| Option | Speed | Cost | Effort |
|--------|-------|------|--------|
| Cloud transcription API (Deepgram/AssemblyAI) | Hours | ~$600-900 | Low |
| Cloud GPU (A100/H100) with CUDA batching | Hours | ~$10-30 | Medium |
| Sequential on M4 Pro (current) | ~8 days | Free | None |
| Speculative decoding (library supports `draft_model`) | ~4 days? | Free | Low — untested |

## Decision

Run sequentially with `--shuffle` for representative sampling overnight. Revisit cloud options if the full batch is needed urgently.
