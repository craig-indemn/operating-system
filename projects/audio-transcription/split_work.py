#!/usr/bin/env python3
"""
Split audio files into N symlink directories for parallel transcription.

Creates split_1/, split_2/, ..., split_N/ with symlinks to the original files.
Skips files that already have transcripts in the output directory.

Usage:
    python split_work.py audio_files/ --workers 3 [--output-dir transcripts]
"""

import argparse
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".ogg", ".wma", ".aac"}
MIN_FILE_SIZE = 1024


def find_audio_files(input_dir: Path) -> list[Path]:
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(f for f in input_dir.rglob(f"*{ext}") if f.stat().st_size >= MIN_FILE_SIZE)
        files.extend(f for f in input_dir.rglob(f"*{ext.upper()}") if f.stat().st_size >= MIN_FILE_SIZE)
    return sorted(set(files))


def main():
    parser = argparse.ArgumentParser(description="Split audio files for parallel transcription")
    parser.add_argument("input_dir", type=Path, help="Directory containing audio files")
    parser.add_argument("--workers", type=int, default=3, help="Number of workers (default: 3)")
    parser.add_argument("--output-dir", type=Path, default=Path("transcripts"), help="Transcript output dir (to check resume state)")
    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"ERROR: {args.input_dir} does not exist")
        sys.exit(1)

    # Find all audio files
    all_files = find_audio_files(args.input_dir)
    print(f"Total audio files: {len(all_files)}")

    # Filter already-transcribed
    remaining = []
    for af in all_files:
        rel_path = af.relative_to(args.input_dir)
        out_file = args.output_dir / rel_path.with_suffix(".txt")
        if not out_file.exists():
            remaining.append(af)

    skipped = len(all_files) - len(remaining)
    print(f"Already transcribed: {skipped}")
    print(f"Remaining: {len(remaining)}")

    if not remaining:
        print("Nothing to split — all files already done.")
        return

    # Clean up old split directories
    for i in range(1, args.workers + 1):
        split_dir = Path(f"split_{i}")
        if split_dir.exists():
            for link in split_dir.iterdir():
                link.unlink()
            split_dir.rmdir()

    # Create split directories with symlinks
    chunks = [[] for _ in range(args.workers)]
    for i, f in enumerate(remaining):
        chunks[i % args.workers].append(f)

    for i, chunk in enumerate(chunks, 1):
        split_dir = Path(f"split_{i}")
        split_dir.mkdir(exist_ok=True)
        for f in chunk:
            link = split_dir / f.name
            link.symlink_to(f.resolve())
        print(f"  split_{i}/: {len(chunk)} files")

    # Print run commands
    print(f"\n--- Run these in {args.workers} separate terminals ---\n")
    for i in range(1, args.workers + 1):
        print(f"cd /Users/home/Repositories/operating-system/projects/audio-transcription && .venv/bin/python transcribe.py split_{i} --output-dir transcripts --resume")
    print(f"\nAll workers write to transcripts/ (shared). --resume is cross-worker safe.")
    print(f"Skip --manifest during parallel runs to avoid write conflicts.")
    print(f"After all workers finish, run: python build_manifest.py")


if __name__ == "__main__":
    main()
