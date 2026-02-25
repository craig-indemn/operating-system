---
name: google-workspace
description: Access Gmail, Google Calendar, Drive, Docs, and Sheets using the gog CLI. Use for any Google Workspace interaction.
---

# Google Workspace

Unified access to Gmail, Calendar, Drive, Docs, and Sheets via `gog` (gogcli).

## Status Check

```bash
which gog && echo "INSTALLED" || echo "NOT INSTALLED"
```

```bash
gog gmail search "newer_than:1d" --max 1 --json 2>/dev/null && echo "AUTHENTICATED" || echo "NOT AUTHENTICATED"
```

## Prerequisites

gog needs a **Google Cloud OAuth credentials JSON** (Desktop app type) to access Google Workspace APIs. This is a one-time setup. Two paths:

### Option A: Use Your Own Google Account (self-service, no admin needed)

1. Go to https://console.cloud.google.com and sign in with the Google account you want to connect
2. **Create a project**: Top bar > project dropdown > "New Project" > name it anything (e.g. "claude-workspace") > Create
3. **Enable APIs**: Left sidebar > "APIs & Services" > "Enable APIs and Services" > search and enable each:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
   - Google Sheets API
4. **Configure OAuth consent screen**: APIs & Services > OAuth consent screen > Select "External" > Create
   - App name: anything (e.g. "gog CLI")
   - User support email: your email
   - Developer contact email: your email
   - Click through the rest (scopes, test users) — no changes needed
   - On the Test Users page, add your own email address
   - Save
5. **Create credentials**: APIs & Services > Credentials > "Create Credentials" > "OAuth client ID"
   - Application type: **Desktop app**
   - Name: anything (e.g. "gog")
   - Click Create
   - Click **"Download JSON"** — save the file somewhere you'll remember (e.g. `~/Downloads/`)
6. You now have the credentials JSON. Continue to Setup below.

**Note**: While the app is in "Testing" mode, only test users you added in step 4 can authorize. This is fine for personal use. To let other team members use the same project, add their emails as test users or publish the app.

### Option B: Use the Indemn Shared Credentials (recommended for team members)

1. Download `google-oauth-credentials.json` from 1Password (Engineering vault → "Google Workspace OAuth — gog CLI")
2. Continue to Setup below.

If the file isn't in 1Password yet, ask Craig to upload it or follow Option A to create your own.

Either option produces the same result: a credentials JSON file that gog uses to authenticate.

## Setup

### Install

**macOS:**
```bash
brew install steipete/tap/gogcli
```

**Linux (Ubuntu/Debian):**
```bash
curl -sL https://github.com/steipete/gogcli/releases/latest/download/gogcli_0.11.0_linux_amd64.tar.gz | tar xz
sudo mv gog /usr/local/bin/
```
If the version above is outdated, check https://github.com/steipete/gogcli/releases for the latest.

### Load credentials
```bash
gog auth credentials set ~/path/to/downloaded-credentials.json
```

### Authenticate
```bash
gog auth add your-email@indemn.ai
```
This opens a browser for Google OAuth consent. Sign in with your @indemn.ai account, approve permissions. The refresh token is stored locally and auto-refreshes — you only do this once.

## Usage

Quick reference for each service. Full command details in the individual reference files.

### Gmail

```bash
# Search threads
gog gmail search "from:person@company.com subject:renewal" --max 10 --json

# Get a specific message
gog gmail get <messageId> --json

# Send email
gog gmail send --to="person@company.com" --subject="Follow up" --body="Message text"
```

See `references/gmail.md` for full reference (drafts, labels, attachments, reply threading, search syntax).

### Calendar

```bash
# Today's events
gog calendar events --today --json

# This week
gog calendar events --week --json

# Next 7 days
gog calendar events --days 7 --json

# Create event with Google Meet
gog calendar create primary --summary="Meeting" --from="2026-01-15T10:00:00" --to="2026-01-15T10:30:00" --attendees="person@company.com" --with-meet --send-updates=all
```

See `references/calendar.md` for full reference (search, free/busy, focus time, out-of-office, relative time values).

### Drive

```bash
# List files in a folder (--parent takes a folder ID, not a path)
gog drive ls --parent=<folderId> --json

# Search files
gog drive search "quarterly report" --json

# Download / export
gog drive download <fileId> --format=pdf --out=./report.pdf

# Upload a file (stays in original format)
gog drive upload ./report.pdf --parent=<folderId> --name="Report Name"
```

**Upload as Google Doc:** `gog drive upload` keeps the file in its native format. To convert a local file (markdown, text, html, docx) into an editable Google Doc, use the Drive API multipart upload with `mimeType: application/vnd.google-apps.document`. See `references/drive.md` for the full curl pattern.

**Domain sharing:** `gog drive share` supports `--email` (individual) and `--anyone` (public), but not org-wide sharing. To share with an entire Google Workspace domain (e.g., everyone at indemn.ai), use the Drive API permissions endpoint with `"type":"domain"`. See `references/drive.md` for the curl pattern.

### Docs

```bash
# Read a document as plain text
gog docs cat <docId>

# Create a document
gog docs create "Document Title" --parent=<folderId>

# Export
gog docs export <docId> --format=pdf --out=./doc.pdf
```

See `references/docs.md` for full reference (info, copy, export formats).

### Sheets

```bash
# Read values
gog sheets get <spreadsheetId> "Sheet1!A1:D10" --json

# Update values (pipe separates cells, comma separates rows)
gog sheets update <spreadsheetId> "Sheet1!A1:C1" "Name|Email|Status"

# Append a row
gog sheets append <spreadsheetId> "Sheet1!A:C" "Alice|alice@co.com|Active"
```

See `references/sheets.md` for full reference (metadata, create, copy, export, value format syntax, --values-json).

### Global Flags

These work on all gog commands:

- `--json` — JSON output
- `--plain` — TSV output (no colors)
- `--account=STRING` — specify account email (if multiple accounts authenticated)
- `--force` — skip confirmations
- `--no-input` — never prompt for input
