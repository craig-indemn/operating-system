#!/usr/bin/env python3
"""
Split vision_sample.jsonl into batches for parallel processing.
Each batch is a JSON file containing ~15 emails with PDF paths.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
BATCH_DIR = DATA_DIR / "batches"
BATCH_SIZE = 15

def main():
    BATCH_DIR.mkdir(exist_ok=True)

    # Load sample
    samples = []
    with open(DATA_DIR / "vision_sample.jsonl") as f:
        for line in f:
            samples.append(json.loads(line))

    # Split into batches
    batches = []
    for i in range(0, len(samples), BATCH_SIZE):
        batch = samples[i:i + BATCH_SIZE]
        batch_num = len(batches)
        batch_file = BATCH_DIR / f"batch_{batch_num:03d}.json"
        batch_file.write_text(json.dumps(batch, indent=2))
        batches.append({
            "batch_num": batch_num,
            "file": str(batch_file),
            "count": len(batch),
            "types": list(set(e["email_type"] for e in batch)),
        })

    # Write batch index
    index_file = BATCH_DIR / "batch_index.json"
    index_file.write_text(json.dumps(batches, indent=2))

    print(f"Created {len(batches)} batches of ~{BATCH_SIZE} emails each")
    print(f"Batch files: {BATCH_DIR}/batch_XXX.json")
    print(f"Index: {index_file}")
    for b in batches:
        print(f"  Batch {b['batch_num']:>3}: {b['count']} emails — {', '.join(b['types'])}")


if __name__ == "__main__":
    main()
