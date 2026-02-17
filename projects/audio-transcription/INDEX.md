# Audio Transcription

Transcribe Alliance Insurance phone call recordings into text using Qwen3-ASR via MLX on MacBook Pro (M4 Pro, 24 GB). Audio from Brian Leftwich (Alliance COO), forwarded by Peter Duffy.

## Status
Session 2026-02-16-b closed. Transcription running overnight with `--shuffle`.

**What happened this session:**
- Investigated parallel transcription — tested 2 separate processes with symlink directories
- Confirmed parallel MLX on Apple Silicon doesn't help: unified memory bandwidth is the bottleneck, not GPU cores or RAM
- Total throughput with 2 workers was worse than 1, system became sluggish
- Added `--shuffle` flag to transcribe.py for random sampling across all call types
- ~536 files transcribed so far out of ~30,816 valid files (6,189 under 1KB filtered out of original 37,005)

**Currently running:**
```bash
cd projects/audio-transcription
.venv/bin/python transcribe.py audio_files --output-dir transcripts --resume --shuffle
```

**Next steps:**
- Check transcript count and quality after overnight run
- Review sample transcripts across different call types (axfer vs exten, different extensions)
- Decide on output format for delivery (plain text, timestamped SRT, speaker-labeled)
- If full batch needed urgently, consider cloud transcription API (~$600-900 for all files in hours)
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
| 2026-02-16 | [parallelism-investigation](artifacts/2026-02-16-parallelism-investigation.md) | Can we run multiple transcription processes in parallel on Apple Silicon? |

## Decisions
- 2026-02-16: Ollama can't do audio models — ruled out immediately
- 2026-02-16: NeMo + MPS silently corrupts output (conformer encoder attention) — ruled out after extensive debugging
- 2026-02-16: NeMo + CPU works (28s/4min) but mlx-qwen3-asr is faster and native to Apple Silicon
- 2026-02-16: **mlx-qwen3-asr (Qwen3-ASR 0.6B) via MLX** — 24s/4min, native Metal GPU, 2 GB memory
- 2026-02-16: Single process is optimal — unified memory bandwidth is the bottleneck, not GPU cores or RAM capacity
- 2026-02-16: Multi-process fork crashes (Metal context corruption); separate processes work mechanically but reduce total throughput
- 2026-02-16: Use `--shuffle` for representative sampling instead of alphabetical grinding

## Open Questions
- What output format does the team need? (plain text, timestamped SRT, speaker-labeled?)
- Should we run the 1.7B model on a subset for quality comparison?
- What happens with the transcripts after — fed into the platform? Used for training data?
