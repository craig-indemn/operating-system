#!/usr/bin/env python3
"""
Transcribe audio files using Qwen3-ASR via MLX on Apple Silicon.

Usage:
    python transcribe.py <input_dir> [--output-dir <output_dir>] [--resume]

Single-process, GPU-optimized. Loads the model once and processes all files
sequentially. MLX runs on the Metal GPU — a single process fully saturates it.

Supports: .wav, .flac, .mp3, .m4a, .ogg, .wma, .aac
Use --resume to skip files that already have transcripts (safe to ctrl-c and restart).
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from mlx_qwen3_asr import transcribe_batch, load_audio, Session

SUPPORTED_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".ogg", ".wma", ".aac"}
MIN_FILE_SIZE = 1024  # skip files under 1KB (empty/corrupt)


def find_audio_files(input_dir: Path) -> list[Path]:
    """Recursively find all supported audio files above minimum size."""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(f for f in input_dir.rglob(f"*{ext}") if f.stat().st_size >= MIN_FILE_SIZE)
        files.extend(f for f in input_dir.rglob(f"*{ext.upper()}") if f.stat().st_size >= MIN_FILE_SIZE)
    return sorted(set(files))


def get_duration(audio_path: Path) -> float:
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
            capture_output=True, text=True, check=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using Qwen3-ASR (MLX)")
    parser.add_argument("input_dir", type=Path, help="Directory containing audio files")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: ./transcripts/)")
    parser.add_argument("--model", default="Qwen/Qwen3-ASR-0.6B", help="Model name (default: Qwen/Qwen3-ASR-0.6B)")
    parser.add_argument("--timestamps", action="store_true", help="Include word-level timestamps")
    parser.add_argument("--manifest", action="store_true", help="Write a JSONL manifest of all transcriptions")
    parser.add_argument("--resume", action="store_true", help="Skip files that already have transcripts")
    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"ERROR: Input directory does not exist: {args.input_dir}")
        sys.exit(1)

    output_dir = args.output_dir or Path("./transcripts")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find audio files
    audio_files = find_audio_files(args.input_dir)
    if not audio_files:
        print(f"No audio files found in {args.input_dir}")
        sys.exit(1)

    total_found = len(audio_files)

    # Filter already-transcribed files if resuming
    if args.resume:
        remaining = []
        for af in audio_files:
            rel_path = af.relative_to(args.input_dir)
            out_file = output_dir / rel_path.with_suffix(".txt")
            if not out_file.exists():
                remaining.append(af)
        skipped = total_found - len(remaining)
        if skipped:
            print(f"Resuming: {skipped} already done, {len(remaining)} remaining")
        audio_files = remaining

    total = len(audio_files)
    if total == 0:
        print("Nothing to transcribe — all files already done.")
        return

    print(f"Files: {total} | Model: {args.model}")
    print(f"Output: {output_dir}")

    # Load model once
    print("Loading model...", flush=True)
    t0 = time.time()
    session = Session(args.model)
    print(f"Model loaded in {time.time() - t0:.1f}s\n")

    # Process files one at a time (GPU-bound — single process saturates it)
    manifest_path = output_dir / "manifest.jsonl" if args.manifest else None
    manifest_file = open(manifest_path, "a") if manifest_path else None
    errors = []
    completed = 0
    total_audio_duration = 0.0
    total_process_time = 0.0

    try:
        for i, audio_file in enumerate(audio_files, 1):
            rel_path = audio_file.relative_to(args.input_dir)
            out_file = output_dir / rel_path.with_suffix(".txt")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            duration = get_duration(audio_file)
            print(f"[{i}/{total}] {audio_file.name} ({duration:.0f}s)", end=" ", flush=True)

            try:
                start = time.time()
                result = session.transcribe(
                    str(audio_file),
                    return_timestamps=args.timestamps,
                )
                elapsed = time.time() - start
                total_audio_duration += duration
                total_process_time += elapsed

                # Write transcript
                if args.timestamps and hasattr(result, "segments") and result.segments:
                    lines = []
                    for seg in result.segments:
                        lines.append(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")
                    out_file.write_text("\n".join(lines))
                else:
                    out_file.write_text(result.text)

                completed += 1
                print(f"-> {elapsed:.1f}s ({len(result.text)} chars)")

                # Append to manifest incrementally (survives ctrl-c)
                if manifest_file:
                    entry = {
                        "source_file": str(audio_file),
                        "transcript_file": str(out_file),
                        "duration_seconds": round(duration, 1),
                        "process_seconds": round(elapsed, 1),
                        "char_count": len(result.text),
                        "transcript": result.text,
                    }
                    manifest_file.write(json.dumps(entry) + "\n")
                    manifest_file.flush()

            except Exception as e:
                print(f"-> ERROR: {e}")
                errors.append({"file": str(audio_file), "error": str(e)})

            # Progress stats every 100 files
            if i % 100 == 0 and total_process_time > 0:
                rtf = total_process_time / total_audio_duration if total_audio_duration > 0 else 0
                avg_per_file = total_process_time / completed if completed > 0 else 0
                eta_hours = (total - i) * avg_per_file / 3600
                print(f"\n  --- {i}/{total} done | RTF: {rtf:.3f}x | ~{avg_per_file:.1f}s/file | ETA: {eta_hours:.1f}h ---\n")

    except KeyboardInterrupt:
        print(f"\n\nInterrupted! {completed} files saved. Run with --resume to continue.")

    finally:
        if manifest_file:
            manifest_file.close()

    # Write errors
    if errors and args.manifest:
        errors_path = output_dir / "errors.jsonl"
        with open(errors_path, "w") as f:
            for entry in errors:
                f.write(json.dumps(entry) + "\n")

    # Summary
    print(f"\nDone! {completed}/{total} transcribed ({len(errors)} errors)")
    if total_audio_duration > 0:
        print(f"Audio: {total_audio_duration/3600:.1f}h | Time: {total_process_time/3600:.1f}h | RTF: {total_process_time/total_audio_duration:.3f}x")
    print(f"Transcripts: {output_dir}")


if __name__ == "__main__":
    main()
