#!/usr/bin/env python3
"""
GIC Email Intelligence — Full Extraction Pipeline

Pulls all emails from quote@gicunderwriters.com via Microsoft Graph API,
downloads attachments, and extracts text from PDFs.

Usage:
    python3 extract_emails.py                  # Full extraction
    python3 extract_emails.py --resume         # Resume from where we left off
    python3 extract_emails.py --folder Inbox   # Single folder only
    python3 extract_emails.py --limit 50       # Limit total emails
    python3 extract_emails.py --skip-attachments  # Metadata + body only
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# --- Configuration ---
TENANT_ID = "7c0931fd-6924-44fe-8fac-29c328791072"
CLIENT_ID = "4bf2eacd-4869-4ade-890c-ba5f76c7cada"
CLIENT_SECRET = "1qD8Q~nzvBeCEkPNBMw6arYukIgJB~KfGf~WQciv"
USER_EMAIL = "quote@gicunderwriters.com"
GRAPH_BASE = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}"

DATA_DIR = Path(__file__).parent / "data"
EMAILS_JSONL = DATA_DIR / "emails.jsonl"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
PROGRESS_FILE = DATA_DIR / "extraction_progress.json"

# Graph API returns max 1000 per page, but 50 is more reliable
PAGE_SIZE = 50

# Fields to retrieve per message
MESSAGE_FIELDS = ",".join([
    "id", "subject", "from", "toRecipients", "ccRecipients",
    "receivedDateTime", "hasAttachments", "conversationId",
    "parentFolderId", "isRead", "importance", "internetMessageHeaders"
])


def get_token():
    """Get OAuth2 access token using client credentials."""
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    token_data = resp.json()
    return token_data["access_token"], time.time() + token_data["expires_in"] - 60


class GraphClient:
    """Microsoft Graph API client with auto-refreshing token."""

    def __init__(self):
        self.token, self.token_expiry = get_token()
        self.session = requests.Session()
        self._update_headers()

    def _update_headers(self):
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Prefer": 'outlook.body-content-type="text"',
        })

    def _ensure_token(self):
        if time.time() > self.token_expiry:
            print("  [token refresh]")
            self.token, self.token_expiry = get_token()
            self._update_headers()

    def get(self, url, params=None, retries=3):
        """GET with auto-refresh and retry."""
        for attempt in range(retries):
            self._ensure_token()
            try:
                resp = self.session.get(url, params=params, timeout=30)
                if resp.status_code == 429:  # throttled
                    retry_after = int(resp.headers.get("Retry-After", 10))
                    print(f"  [throttled, waiting {retry_after}s]")
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    print(f"  [retry {attempt+1}/{retries}: {e}]")
                    time.sleep(2 ** attempt)
                else:
                    raise

    def get_raw(self, url, retries=3):
        """GET raw bytes (for attachment download)."""
        for attempt in range(retries):
            self._ensure_token()
            try:
                resp = self.session.get(url, timeout=60)
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 10))
                    print(f"  [throttled, waiting {retry_after}s]")
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                return resp
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    print(f"  [retry {attempt+1}/{retries}: {e}]")
                    time.sleep(2 ** attempt)
                else:
                    raise


def get_folders(client):
    """Get all mail folders with their IDs and names."""
    folders = []
    url = f"{GRAPH_BASE}/mailFolders?$select=id,displayName,totalItemCount&$top=100"
    while url:
        data = client.get(url)
        for f in data.get("value", []):
            folders.append({
                "id": f["id"],
                "name": f["displayName"].strip(),
                "count": f["totalItemCount"],
            })
            # Check for child folders
            children_url = f"{GRAPH_BASE}/mailFolders/{f['id']}/childFolders?$select=id,displayName,totalItemCount&$top=100"
            children = client.get(children_url)
            for child in children.get("value", []):
                folders.append({
                    "id": child["id"],
                    "name": f"{f['displayName'].strip()}/{child['displayName'].strip()}",
                    "count": child["totalItemCount"],
                })
        url = data.get("@odata.nextLink")
    return folders


def extract_email_record(msg, folder_name):
    """Convert a Graph API message into our extraction record."""
    from_addr = msg.get("from", {}).get("emailAddress", {})
    return {
        "id": msg["id"],
        "conversation_id": msg.get("conversationId", ""),
        "folder": folder_name,
        "received_at": msg.get("receivedDateTime", ""),
        "subject": msg.get("subject", ""),
        "from_address": from_addr.get("address", ""),
        "from_name": from_addr.get("name", ""),
        "to_addresses": [
            r["emailAddress"]["address"]
            for r in msg.get("toRecipients", [])
        ],
        "cc_addresses": [
            r["emailAddress"]["address"]
            for r in msg.get("ccRecipients", [])
        ],
        "body_text": msg.get("body", {}).get("content", ""),
        "has_attachments": msg.get("hasAttachments", False),
        "is_read": msg.get("isRead", False),
        "importance": msg.get("importance", "normal"),
        "attachments": [],  # filled in later
    }


def download_attachments(client, message_id, email_idx):
    """Download all attachments for a message. Returns attachment metadata."""
    attachment_dir = ATTACHMENTS_DIR / str(email_idx)

    # First, list attachments (without contentBytes)
    list_url = f"{GRAPH_BASE}/messages/{message_id}/attachments?$select=id,name,contentType,size,isInline"

    try:
        data = client.get(list_url)
    except Exception as e:
        print(f"  [attachment list error for {email_idx}: {e}]")
        return []

    attachments = []
    for att in data.get("value", []):
        att_meta = {
            "name": att.get("name", "unknown"),
            "content_type": att.get("contentType", ""),
            "size": att.get("size", 0),
            "is_inline": att.get("isInline", False),
        }

        # Download actual file content (skip inline images like logos/signatures)
        if not att.get("isInline", False) and att.get("size", 0) > 0:
            att_id = att["id"]
            detail_url = f"{GRAPH_BASE}/messages/{message_id}/attachments/{att_id}"
            try:
                att_data = client.get(detail_url)
                content_bytes = att_data.get("contentBytes")
                if content_bytes:
                    attachment_dir.mkdir(parents=True, exist_ok=True)
                    safe_name = "".join(
                        c if c.isalnum() or c in ".-_ " else "_"
                        for c in att.get("name", "unknown")
                    )
                    file_path = attachment_dir / safe_name
                    raw = base64.b64decode(content_bytes)
                    file_path.write_bytes(raw)
                    att_meta["saved_path"] = str(file_path.relative_to(DATA_DIR))
                    att_meta["saved_size"] = len(raw)
            except Exception as e:
                att_meta["save_error"] = str(e)

        attachments.append(att_meta)

    return attachments


def get_attachment_stats(email_records):
    """Count attachments by type for summary stats."""
    stats = {"total": 0, "pdf": 0, "image": 0, "html": 0, "other": 0}
    total_size = 0

    for record in email_records:
        for att in record.get("attachments", []):
            stats["total"] += 1
            total_size += att.get("saved_size", 0)
            ct = att.get("content_type", "").lower()
            name = att.get("name", "").lower()

            if ct == "application/pdf" or name.endswith(".pdf"):
                stats["pdf"] += 1
            elif ct.startswith("image/"):
                stats["image"] += 1
            elif ct == "text/html" or name.endswith(".html"):
                stats["html"] += 1
            else:
                stats["other"] += 1

    stats["total_size_mb"] = round(total_size / (1024 * 1024), 1)
    return stats


def load_progress():
    """Load extraction progress for resume."""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"completed_folders": [], "total_emails": 0, "total_attachments": 0}


def save_progress(progress):
    """Save extraction progress."""
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


def main():
    parser = argparse.ArgumentParser(description="GIC Email Extraction Pipeline")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--folder", type=str, help="Extract single folder only")
    parser.add_argument("--limit", type=int, default=0, help="Max emails to extract (0=all)")
    parser.add_argument("--skip-attachments", action="store_true", help="Skip attachment downloads")
    # --skip-pdf-extract kept for backwards compat but no longer does anything
    parser.add_argument("--skip-pdf-extract", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    # Setup
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)

    client = GraphClient()
    progress = load_progress() if args.resume else {
        "completed_folders": [], "total_emails": 0, "total_attachments": 0
    }

    # Phase 1: Get folder list
    print("=== Phase 1: Discovering folders ===")
    folders = get_folders(client)
    for f in folders:
        print(f"  {f['name']}: {f['count']} emails")

    if args.folder:
        folders = [f for f in folders if f["name"].lower() == args.folder.lower()]
        if not folders:
            print(f"Folder '{args.folder}' not found")
            sys.exit(1)

    total_expected = sum(f["count"] for f in folders)
    print(f"\nTotal emails to extract: {total_expected}")

    # Phase 2: Extract emails + attachments
    print("\n=== Phase 2: Extracting emails ===")
    email_records = []

    # Load existing records if resuming
    if args.resume and EMAILS_JSONL.exists():
        with open(EMAILS_JSONL, "r") as f:
            for line in f:
                if line.strip():
                    email_records.append(json.loads(line))
        print(f"  Loaded {len(email_records)} existing records")

    existing_ids = {r["id"] for r in email_records}
    email_idx = len(email_records)

    # Open JSONL for appending
    mode = "a" if args.resume else "w"
    jsonl_file = open(EMAILS_JSONL, mode)

    try:
        for folder in folders:
            if args.resume and folder["name"] in progress["completed_folders"]:
                print(f"\n  Skipping {folder['name']} (already completed)")
                continue

            if folder["count"] == 0:
                progress["completed_folders"].append(folder["name"])
                continue

            print(f"\n  --- {folder['name']} ({folder['count']} emails) ---")
            folder_count = 0

            url = (
                f"{GRAPH_BASE}/mailFolders/{folder['id']}/messages"
                f"?$select={MESSAGE_FIELDS}"
                f"&$top={PAGE_SIZE}"
                f"&$orderby=receivedDateTime desc"
            )

            while url:
                data = client.get(url)
                messages = data.get("value", [])

                for msg in messages:
                    if msg["id"] in existing_ids:
                        continue

                    if args.limit and email_idx >= args.limit:
                        print(f"\n  Reached limit of {args.limit} emails")
                        url = None
                        break

                    record = extract_email_record(msg, folder["name"])

                    # Download attachments
                    if msg.get("hasAttachments") and not args.skip_attachments:
                        record["attachments"] = download_attachments(
                            client, msg["id"], email_idx
                        )
                        progress["total_attachments"] += len(record["attachments"])

                    # Write to JSONL
                    jsonl_file.write(json.dumps(record) + "\n")
                    jsonl_file.flush()
                    email_records.append(record)
                    existing_ids.add(msg["id"])
                    email_idx += 1
                    folder_count += 1

                    if email_idx % 25 == 0:
                        print(f"    {email_idx} emails extracted ({folder_count} from {folder['name']})...")
                        progress["total_emails"] = email_idx
                        save_progress(progress)

                url = data.get("@odata.nextLink") if url else None

            progress["completed_folders"].append(folder["name"])
            progress["total_emails"] = email_idx
            save_progress(progress)
            print(f"    {folder['name']}: {folder_count} emails extracted")

    finally:
        jsonl_file.close()
        progress["total_emails"] = email_idx
        save_progress(progress)

    print(f"\n=== Extraction complete ===")
    print(f"  Total emails: {email_idx}")
    print(f"  Total attachments: {progress['total_attachments']}")
    print(f"  JSONL: {EMAILS_JSONL}")
    print(f"  Attachments: {ATTACHMENTS_DIR}")

    # Phase 3: Summary stats
    if not args.skip_attachments:
        stats = get_attachment_stats(email_records)
        print(f"\n=== Attachment Summary ===")
        print(f"  Total attachments: {stats['total']}")
        print(f"  PDFs: {stats['pdf']}")
        print(f"  Images: {stats['image']}")
        print(f"  HTML: {stats['html']}")
        print(f"  Other: {stats['other']}")
        print(f"  Total size: {stats['total_size_mb']} MB")
        print(f"\n=== Pipeline complete ===")
        print(f"  {email_idx} emails with metadata + body + raw attachments on disk")
        print(f"  Next step: Run Claude vision pass on all PDF attachments")
    else:
        print(f"\n=== Pipeline complete (attachments skipped) ===")


if __name__ == "__main__":
    main()
