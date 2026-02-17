# Audio Transcription

Transcribe Alliance Insurance phone call recordings into text using Qwen3-ASR via MLX on MacBook Pro (M4 Pro, 24 GB). Audio from Brian Leftwich (Alliance COO), forwarded by Peter Duffy.

## Status
Session 2026-02-16-a closed. Pipeline built, tested, ready to run.

**What happened this session:**
- Read Peter's forwarded email from Brian Leftwich (Alliance COO) with two SharePoint zip links
- Downloaded and extracted 37,005 WAV files (9.4 GB) of phone call recordings
- Evaluated Ollama (can't do audio), NeMo/Canary-Qwen-2.5B (MPS silently corrupts output), and mlx-qwen3-asr
- Built and tested transcription pipeline: Qwen3-ASR 0.6B via MLX, 24s per 4-min call, 2 GB memory
- Investigated multi-process parallelism — single process is optimal (GPU-bound on one Metal GPU)
- ~515 files transcribed in early partial runs

**To resume:**
```bash
cd projects/audio-transcription
.venv/bin/python transcribe.py audio_files --output-dir transcripts --manifest --resume
```

**Next steps:**
- Run full transcription batch (~3.5-7 days, ctrl-c safe with --resume)
- Review transcript quality across different call types (short vs long, inbound vs outbound)
- Decide on output format for delivery (plain text, timestamped SRT, speaker-labeled)
- Check with Peter/Kyle on what to do with transcripts once complete

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Phone Call Recordings email | Gmail thread | Thread ID: 19c53c132df8e6eb |
| Apr 22 - July 21.zip | SharePoint | [link](https://myallianceinsurance-my.sharepoint.com/:u:/p/brian/IQBuEoxReAtpSLcFAP-jq1PmAQrGMASjPkP6wD1rDHNvO4E?e=6YsrGa) |
| Oct 21 2025 to Jan 20 2026.zip | SharePoint | [link](https://myallianceinsurance-my.sharepoint.com/:u:/p/brian/IQCZDWxYJBL5QKQ5mhLGZs7GAbTHxH8jNUnjyv2mBUJbdHU?e=8wye4P) |
| Alliance Insurance | Customer | [myallianceinsurance.com](http://www.myallianceinsurance.com/) |
| Qwen3-ASR (MLX) | GitHub | [moona3k/mlx-qwen3-asr](https://github.com/moona3k/mlx-qwen3-asr) |
| Canary-Qwen-2.5B | HuggingFace | [nvidia/canary-qwen-2.5b](https://huggingface.co/nvidia/canary-qwen-2.5b) |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-16 | [transcription-pipeline-setup](artifacts/2026-02-16-transcription-pipeline-setup.md) | Set up local audio transcription for Alliance phone calls |

## Decisions
- 2026-02-16: Ollama can't do audio models — ruled out immediately
- 2026-02-16: NeMo + MPS silently corrupts output (conformer encoder attention) — ruled out after extensive debugging
- 2026-02-16: NeMo + CPU works (28s/4min) but mlx-qwen3-asr is faster and native to Apple Silicon
- 2026-02-16: **mlx-qwen3-asr (Qwen3-ASR 0.6B) via MLX** — 24s/4min, native Metal GPU, 2 GB memory
- 2026-02-16: Single process is optimal — multiple workers share one GPU with no throughput gain
- 2026-02-16: Multi-process fork on macOS crashes (Metal GPU context corruption) — do not attempt

## Open Questions
- What output format does the team need? (plain text, timestamped SRT, speaker-labeled?)
- Should we run the 1.7B model on a subset for quality comparison?
- What happens with the transcripts after — fed into the platform? Used for training data?
