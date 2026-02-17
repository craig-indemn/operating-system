#!/usr/bin/env python3
"""
Extract structured data from call transcripts using Ollama (Qwen3-14B).

Usage:
    python extract.py <transcript_dir> [--output-dir <output_dir>] [--resume] [--shuffle]

Reads .txt transcripts, sends each to Ollama with a structured JSON schema,
and writes one .json extraction per file. Resume-safe with --resume.

Requires: Ollama running locally with the target model pulled.
"""

import argparse
import json
import random
import re
import sys
import time
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MIN_TRANSCRIPT_SIZE = 50  # skip transcripts under 50 chars (empty/corrupt)

# Call direction from filename prefix
DIRECTION_MAP = {
    "in-": "inbound",
    "out-": "outbound",
    "exten-": "extension_transfer",
    "q-": "queue",
    "internal-": "internal",
    "axfer-": "attended_transfer",
    "parked-": "parked",
    "ptimeout-": "park_timeout",
}

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "is_substantive": {
            "type": "boolean",
            "description": "False if voicemail, spam, pure transfer, hold, or too short to analyze",
        },
        "caller_intent": {
            "type": "string",
            "description": "What the caller wanted, in 1-2 sentences",
        },
        "resolution_steps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "What the agent did to resolve the call, step by step",
        },
        "outcome": {
            "type": "string",
            "enum": ["resolved", "transferred", "callback_needed", "unresolved", "voicemail", "spam", "not_applicable"],
        },
        "knowledge_required": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Domain knowledge the agent needed to handle this call",
        },
        "systems_referenced": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Tools, systems, or databases mentioned or used",
        },
        "summary": {
            "type": "string",
            "description": "2-3 sentence summary of the call",
        },
    },
    "required": [
        "is_substantive",
        "caller_intent",
        "resolution_steps",
        "outcome",
        "knowledge_required",
        "systems_referenced",
        "summary",
    ],
}

SYSTEM_PROMPT = """You are analyzing phone call transcripts from Alliance Insurance Services, an independent insurance agency. Extract structured information from each transcript.

If the call is not substantive (voicemail greeting, spam/solicitation, pure transfer with no real conversation, hold music, or too short to analyze meaningfully), set is_substantive to false, set outcome appropriately, and keep other fields minimal.

For substantive calls, extract:
- caller_intent: What the caller wanted (1-2 sentences)
- resolution_steps: What the agent did, step by step
- outcome: How the call ended
- knowledge_required: What domain knowledge the agent needed
- systems_referenced: Any tools, software, carrier portals, or databases mentioned
- summary: 2-3 sentence overview

Respond in JSON."""


def get_direction(filename: str) -> str:
    """Parse call direction from filename prefix."""
    for prefix, direction in DIRECTION_MAP.items():
        if filename.startswith(prefix):
            return direction
    return "unknown"


def extract_one(transcript: str, direction: str, model: str) -> dict:
    """Send one transcript to Ollama and return structured extraction."""
    user_prompt = f"Call direction: {direction}\n\nTranscript:\n{transcript}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": EXTRACTION_SCHEMA,
        "options": {"temperature": 0},
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    response.raise_for_status()
    result = response.json()
    content = result["message"]["content"]
    extraction = json.loads(content)

    # Add metadata from the response
    extraction["_model"] = model
    extraction["_eval_count"] = result.get("eval_count", 0)
    extraction["_total_duration_ms"] = round(result.get("total_duration", 0) / 1e6)

    return extraction


def find_transcripts(input_dir: Path) -> list[Path]:
    """Find all .txt transcript files above minimum size."""
    files = [
        f for f in input_dir.rglob("*.txt")
        if f.stat().st_size >= MIN_TRANSCRIPT_SIZE
        and f.name != "manifest.jsonl"
    ]
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="Extract structured data from call transcripts (Ollama)")
    parser.add_argument("input_dir", type=Path, help="Directory containing .txt transcripts")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: ./extractions/)")
    parser.add_argument("--model", default="qwen3:14b", help="Ollama model (default: qwen3:14b)")
    parser.add_argument("--resume", action="store_true", help="Skip files that already have extractions")
    parser.add_argument("--shuffle", action="store_true", help="Randomize file order")
    parser.add_argument("--manifest", action="store_true", help="Write a JSONL manifest")
    parser.add_argument("--limit", type=int, default=0, help="Process only N files (0 = all)")
    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"ERROR: Input directory does not exist: {args.input_dir}")
        sys.exit(1)

    output_dir = args.output_dir or Path("./extractions")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verify Ollama is running
    try:
        requests.get("http://localhost:11434/api/tags", timeout=5)
    except requests.ConnectionError:
        print("ERROR: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    # Find transcripts
    transcript_files = find_transcripts(args.input_dir)
    if not transcript_files:
        print(f"No transcript files found in {args.input_dir}")
        sys.exit(1)

    total_found = len(transcript_files)

    # Filter already-extracted files if resuming
    if args.resume:
        remaining = []
        for tf in transcript_files:
            rel_path = tf.relative_to(args.input_dir)
            out_file = output_dir / rel_path.with_suffix(".json")
            if not out_file.exists():
                remaining.append(tf)
        skipped = total_found - len(remaining)
        if skipped:
            print(f"Resuming: {skipped} already done, {len(remaining)} remaining")
        transcript_files = remaining

    if args.shuffle:
        random.shuffle(transcript_files)

    if args.limit > 0:
        transcript_files = transcript_files[:args.limit]

    total = len(transcript_files)
    if total == 0:
        print("Nothing to extract — all files already done.")
        return

    print(f"Files: {total} | Model: {args.model}")
    print(f"Output: {output_dir}")

    # Warm up the model with a short prompt
    print("Warming up model...", flush=True)
    t0 = time.time()
    try:
        extract_one("Test call. Hello, goodbye.", "inbound", args.model)
        print(f"Model ready in {time.time() - t0:.1f}s\n")
    except Exception as e:
        print(f"ERROR: Could not connect to Ollama or model not available: {e}")
        print(f"Make sure '{args.model}' is pulled: ollama pull {args.model}")
        sys.exit(1)

    # Process transcripts
    manifest_path = output_dir / "manifest.jsonl" if args.manifest else None
    manifest_file = open(manifest_path, "a") if manifest_path else None
    errors = []
    completed = 0
    total_process_time = 0.0

    try:
        for i, transcript_file in enumerate(transcript_files, 1):
            rel_path = transcript_file.relative_to(args.input_dir)
            out_file = output_dir / rel_path.with_suffix(".json")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            transcript = transcript_file.read_text().strip()
            direction = get_direction(transcript_file.name)
            char_count = len(transcript)

            print(f"[{i}/{total}] {transcript_file.name} ({char_count} chars, {direction})", end=" ", flush=True)

            try:
                start = time.time()
                extraction = extract_one(transcript, direction, args.model)
                elapsed = time.time() - start
                total_process_time += elapsed

                # Add file metadata
                extraction["_source_file"] = str(transcript_file)
                extraction["_direction"] = direction
                extraction["_char_count"] = char_count

                # Write extraction
                out_file.write_text(json.dumps(extraction, indent=2))
                completed += 1

                substantive = "Y" if extraction.get("is_substantive") else "N"
                outcome = extraction.get("outcome", "?")
                print(f"-> {elapsed:.1f}s [{substantive}] {outcome}")

                # Manifest
                if manifest_file:
                    manifest_entry = {
                        "source_file": str(transcript_file),
                        "extraction_file": str(out_file),
                        "direction": direction,
                        "is_substantive": extraction.get("is_substantive"),
                        "outcome": extraction.get("outcome"),
                        "process_seconds": round(elapsed, 1),
                    }
                    manifest_file.write(json.dumps(manifest_entry) + "\n")
                    manifest_file.flush()

            except Exception as e:
                print(f"-> ERROR: {e}")
                errors.append({"file": str(transcript_file), "error": str(e)})

            # Progress stats every 100 files
            if i % 100 == 0 and total_process_time > 0:
                avg_per_file = total_process_time / completed if completed > 0 else 0
                eta_hours = (total - i) * avg_per_file / 3600
                print(f"\n  --- {i}/{total} done | ~{avg_per_file:.1f}s/file | ETA: {eta_hours:.1f}h ---\n")

    except KeyboardInterrupt:
        print(f"\n\nInterrupted! {completed} files extracted. Run with --resume to continue.")

    finally:
        if manifest_file:
            manifest_file.close()

    # Write errors
    if errors:
        errors_path = output_dir / "errors.jsonl"
        with open(errors_path, "w") as f:
            for entry in errors:
                f.write(json.dumps(entry) + "\n")

    # Summary
    print(f"\nDone! {completed}/{total} extracted ({len(errors)} errors)")
    if total_process_time > 0 and completed > 0:
        print(f"Time: {total_process_time/3600:.1f}h | Avg: {total_process_time/completed:.1f}s/file")
    print(f"Extractions: {output_dir}")


if __name__ == "__main__":
    main()
