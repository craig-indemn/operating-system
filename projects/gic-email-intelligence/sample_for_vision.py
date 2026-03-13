#!/usr/bin/env python3
"""
Select ~300 strategic PDF samples for Claude vision processing.

Sampling strategy:
- Proportional to email types, with minimum representation for rare types
- For USLI quotes (1,641 emails): sample ~100 across different business lines
- For "Other" (1,239): sample ~100 to discover what's hiding there
- For every other type: sample all or up to 20 each
- Deduplicate: for emails with 3 USLI copies (_Customer, _Retailer, _Applicant), keep only one
- Prefer diversity: spread across different senders, dates, business lines
"""

import json
import random
import os
from collections import defaultdict
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).parent / "data"
EMAILS_JSONL = DATA_DIR / "emails.jsonl"
SAMPLE_JSONL = DATA_DIR / "vision_sample.jsonl"

def classify_email(r):
    """Quick classification based on subject + sender."""
    subj = r.get('subject') or ''
    sender = r.get('from_address', '').lower()

    if subj.startswith('Re:') or subj.startswith('RE:'):
        return 'reply'
    elif subj.startswith('FW:') or subj.startswith('Fw:'):
        return 'forward'
    elif 'USLI' in subj and 'Quote' in subj:
        return 'usli_quote'
    elif 'USLI' in subj and 'Pending' in subj:
        return 'usli_pending'
    elif 'Info Request' in subj:
        return 'info_request'
    elif 'Application Request' in subj:
        return 'application'
    elif 'PHONE TICKET' in subj:
        return 'phone_ticket'
    elif 'Hiscox' in subj or sender == 'contact@hiscox.com':
        return 'hiscox'
    elif 'Decline' in subj:
        return 'decline'
    elif 'RENEWAL' in subj.upper():
        return 'renewal'
    elif 'Daily Report' in subj or 'Binder Follow' in subj:
        return 'report'
    elif sender.endswith('@usli.com'):
        return 'usli_other'
    elif sender.endswith('@gicunderwriters.com'):
        return 'gic_internal'
    elif sender.endswith('@unisoftonline.com'):
        return 'unisoft'
    else:
        return 'other'


def pick_best_pdf(attachments):
    """For emails with multiple PDF copies, pick the best one to read."""
    pdfs = [a for a in attachments if a.get('saved_path', '').endswith('.pdf')]
    if not pdfs:
        return None

    # Prefer Retailer version (has most detail), then plain, then Customer, then Applicant
    for preference in ['_Retailer', '_RetailerVersion', '.pdf']:
        for p in pdfs:
            name = p.get('name', '')
            if preference in name and not any(x in name for x in ['_Customer', '_Applicant']):
                return p

    # Just return the first one
    return pdfs[0]


def main():
    # Load all emails
    emails = []
    with open(EMAILS_JSONL) as f:
        for i, line in enumerate(f):
            r = json.loads(line)
            r['_idx'] = i
            r['_type'] = classify_email(r)
            r['_best_pdf'] = pick_best_pdf(r.get('attachments', []))
            emails.append(r)

    # Group by type
    by_type = defaultdict(list)
    for e in emails:
        if e['_best_pdf']:  # only emails with PDFs
            by_type[e['_type']].append(e)

    print("=== Emails with PDFs by Type ===")
    for t, es in sorted(by_type.items(), key=lambda x: -len(x[1])):
        print(f"  {len(es):>5}  {t}")

    # Sampling targets
    targets = {
        'usli_quote': 100,    # Largest group — sample across business lines
        'other': 24,          # All of them (only 24 with PDFs)
        'decline': 40,        # Important for understanding outcomes
        'hiscox': 15,         # Different carrier, need to see format
        'application': 19,    # All of them (only 19)
        'report': 16,         # All of them
        'reply': 9,           # All of them (only 9 with PDFs)
        'forward': 20,        # Check what's being forwarded
        'usli_other': 40,     # Large group — USLI reps, need variety
        'gic_internal': 10,   # Internal routing
        'usli_pending': 3,    # All of them
        'info_request': 1,    # All of them
        'phone_ticket': 2,    # All of them
        'renewal': 3,         # All of them
        'unisoft': 10,        # System reports
    }

    # Sample
    selected = []
    for email_type, target in targets.items():
        pool = by_type.get(email_type, [])
        if not pool:
            continue

        n = min(target, len(pool))

        if email_type == 'usli_quote':
            # Spread across different business line prefixes in subject
            # USLI quote subjects contain business identifiers
            random.shuffle(pool)
            seen_applicants = set()
            type_selected = []
            for e in pool:
                # Try to get diverse applicant names
                subj = e.get('subject', '')
                # Extract applicant name (after "for " in subject)
                parts = subj.split(' for ')
                applicant = parts[1].split(' from ')[0].strip() if len(parts) > 1 else subj
                applicant_key = applicant[:20].lower()

                if applicant_key not in seen_applicants:
                    seen_applicants.add(applicant_key)
                    type_selected.append(e)
                    if len(type_selected) >= n:
                        break

            # If we didn't get enough, add more
            if len(type_selected) < n:
                remaining = [e for e in pool if e not in type_selected]
                type_selected.extend(random.sample(remaining, min(n - len(type_selected), len(remaining))))

            selected.extend(type_selected)
        else:
            sampled = random.sample(pool, n)
            selected.extend(sampled)

    print(f"\n=== Selected {len(selected)} emails for vision processing ===")
    type_counts = defaultdict(int)
    for e in selected:
        type_counts[e['_type']] += 1
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:>4}  {t}")

    # Count total PDFs and pages to process
    total_pdfs = len(selected)

    # Write sample file
    with open(SAMPLE_JSONL, 'w') as f:
        for e in selected:
            record = {
                'email_idx': e['_idx'],
                'email_type': e['_type'],
                'subject': e.get('subject', ''),
                'from_address': e['from_address'],
                'from_name': e['from_name'],
                'folder': e['folder'],
                'received_at': e['received_at'],
                'body_text': e['body_text'],
                'pdf_path': e['_best_pdf']['saved_path'],
                'pdf_name': e['_best_pdf']['name'],
                'pdf_size': e['_best_pdf'].get('saved_size', 0),
                'all_attachment_names': [a['name'] for a in e.get('attachments', [])],
            }
            f.write(json.dumps(record) + '\n')

    print(f"\nSample written to: {SAMPLE_JSONL}")
    print(f"Total PDFs to process: {total_pdfs}")


if __name__ == "__main__":
    main()
