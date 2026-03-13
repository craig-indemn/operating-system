#!/usr/bin/env python3
"""
Prepare batches for full email classification pass.
Text-only — just subject, sender, body snippet. No PDFs.
Larger batches since we're only sending text.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
CLASS_BATCH_DIR = DATA_DIR / "class_batches"
BATCH_SIZE = 100  # text-only, can handle more per agent

def main():
    CLASS_BATCH_DIR.mkdir(exist_ok=True)

    emails = []
    with open(DATA_DIR / "emails.jsonl") as f:
        for i, line in enumerate(f):
            r = json.loads(line)
            # Strip boilerplate caution banner
            body = r.get('body_text') or ''
            if 'know the content is safe.' in body:
                body = body.split('know the content is safe.')[1]

            # Trim body to first 1000 chars (enough for classification)
            body = body.strip()[:1000]

            emails.append({
                'idx': i,
                'folder': r['folder'],
                'subject': r.get('subject') or '',
                'from_address': r['from_address'],
                'from_name': r['from_name'],
                'to_addresses': r.get('to_addresses', []),
                'received_at': r['received_at'],
                'has_attachments': r['has_attachments'],
                'attachment_names': [a['name'] for a in r.get('attachments', [])],
                'body_snippet': body,
            })

    # Split into batches
    batches = []
    for i in range(0, len(emails), BATCH_SIZE):
        batch = emails[i:i + BATCH_SIZE]
        batch_num = len(batches)
        batch_file = CLASS_BATCH_DIR / f"cbatch_{batch_num:03d}.json"
        batch_file.write_text(json.dumps(batch, indent=2))
        batches.append({"batch_num": batch_num, "count": len(batch)})

    print(f"Created {len(batches)} classification batches of ~{BATCH_SIZE} emails each")
    print(f"Total emails: {len(emails)}")
    print(f"Batch dir: {CLASS_BATCH_DIR}")

if __name__ == "__main__":
    main()
