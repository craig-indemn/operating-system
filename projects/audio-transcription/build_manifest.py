#!/usr/bin/env python3
"""
Build manifest.jsonl from completed transcripts after parallel transcription.

Scans the transcript directory, matches back to source audio files,
and produces the same manifest format as transcribe.py --manifest.

Usage:
    python build_manifest.py [--audio-dir audio_files] [--transcript-dir transcripts]
"""

import argparse
import json
import subprocess
from pathlib import Path


def get_duration(audio_path: Path) -> float:
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
    parser = argparse.ArgumentParser(description="Build manifest from completed transcripts")
    parser.add_argument("--audio-dir", type=Path, default=Path("audio_files"))
    parser.add_argument("--transcript-dir", type=Path, default=Path("transcripts"))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    output = args.output or (args.transcript_dir / "manifest.jsonl")

    txt_files = sorted(args.transcript_dir.glob("*.txt"))
    print(f"Found {len(txt_files)} transcripts")

    count = 0
    with open(output, "w") as f:
        for i, txt in enumerate(txt_files, 1):
            audio_name = txt.stem + ".WAV"
            audio_path = args.audio_dir / audio_name
            if not audio_path.exists():
                # Try lowercase
                audio_name = txt.stem + ".wav"
                audio_path = args.audio_dir / audio_name
            if not audio_path.exists():
                continue

            transcript = txt.read_text()
            duration = get_duration(audio_path)

            entry = {
                "source_file": str(audio_path),
                "transcript_file": str(txt),
                "duration_seconds": round(duration, 1),
                "char_count": len(transcript),
                "transcript": transcript,
            }
            f.write(json.dumps(entry) + "\n")
            count += 1

            if i % 1000 == 0:
                print(f"  {i}/{len(txt_files)}...")

    print(f"Manifest written: {output} ({count} entries)")


if __name__ == "__main__":
    main()
