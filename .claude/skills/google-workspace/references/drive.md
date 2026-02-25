# Drive Reference — gog drive

Complete reference for Google Drive operations via the `gog` CLI.

**Important**: The `--parent` flag takes a **folder ID**, not a folder path. Use `gog drive ls` or `gog drive search` to find folder IDs first.

## List Files

```bash
gog drive ls [--parent=STRING] [--max=20] [--json]
```

Lists files in a folder. Defaults to root if no parent specified.

```bash
# List root
gog drive ls --json

# List files in a specific folder (by folder ID)
gog drive ls --parent=1aBcDeFgHiJkLmNoPqRsTuVwXyZ --json

# Limit results
gog drive ls --max=50 --json
```

## Search Files

```bash
gog drive search <query> [--max=20] [--json]
```

Full-text search across file names and content.

```bash
# Search by name or content
gog drive search "INSURICA call prep" --json

# Limit results
gog drive search "quarterly report" --max=10 --json
```

## Get File Metadata

```bash
gog drive get <fileId>
```

Returns metadata for a specific file (name, type, size, modified date, etc.).

```bash
gog drive get 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## Download / Export File

```bash
gog drive download <fileId> [--out=STRING] [--format=pdf|csv|xlsx|docx|txt]
```

Downloads a file. For Google Workspace files (Docs, Sheets, Slides), use `--format` to export to a specific format.

```bash
# Download a regular file
gog drive download 1aBcDeFgHiJkLmNoPqRsTuVwXyZ

# Download to a specific path
gog drive download 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --out=./local-copy.pdf

# Export a Google Doc as PDF
gog drive download 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=pdf --out=./report.pdf

# Export a Google Sheet as CSV
gog drive download 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=csv --out=./data.csv

# Export a Google Doc as plain text
gog drive download 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=txt
```

## Upload File

```bash
gog drive upload <localPath> [--parent=STRING] [--name=STRING]
```

Uploads a local file to Drive. `--parent` is a folder ID.

```bash
# Upload to root
gog drive upload ./report.pdf

# Upload to a specific folder
gog drive upload ./report.pdf --parent=1aBcDeFgHiJkLmNoPqRsTuVwXyZ

# Upload with a different name
gog drive upload ./local-report.pdf --parent=1aBcDeFgHiJkLmNoPqRsTuVwXyZ --name="Q1 Report.pdf"
```

## Create Folder

```bash
gog drive mkdir <name> [--parent=STRING]
```

Creates a new folder. `--parent` is a folder ID.

```bash
# Create in root
gog drive mkdir "New Customer"

# Create inside an existing folder
gog drive mkdir "Meeting Notes" --parent=1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## Delete File

```bash
gog drive delete <fileId>
```

Moves a file to trash.

```bash
gog drive delete 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## Move File

```bash
gog drive move <fileId> [flags]
```

Moves a file to a different location.

```bash
gog drive move 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## Rename File

```bash
gog drive rename <fileId> <newName>
```

```bash
gog drive rename 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Updated Report Name.pdf"
```

## Share File

```bash
gog drive share <fileId> [--email=STRING --role=reader|writer] [--anyone]
```

```bash
# Share with a specific person (read-only)
gog drive share 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --email=person@company.com --role=reader

# Share with edit access
gog drive share 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --email=person@company.com --role=writer

# Share with anyone who has the link
gog drive share 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --anyone
```

### Share with an entire Google Workspace domain

The `gog` CLI doesn't support domain-level sharing. Use the Drive API directly:

```bash
# Get access token (see "Upload as Google Doc" section for full token flow)
ACCESS_TOKEN=$(...) # see token acquisition steps above

# Share with everyone at indemn.ai (editor access)
curl -s -X POST "https://www.googleapis.com/drive/v3/files/<fileId>/permissions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"domain","domain":"indemn.ai","role":"writer"}'

# Share with everyone at indemn.ai (read-only)
curl -s -X POST "https://www.googleapis.com/drive/v3/files/<fileId>/permissions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"domain","domain":"indemn.ai","role":"reader"}'
```

**Permission types reference:**

| `type` | `domain`/`emailAddress` | Effect |
|--------|------------------------|--------|
| `user` | `emailAddress` | Share with one person |
| `domain` | `domain` | Share with everyone in a Google Workspace org |
| `anyone` | _(none)_ | Public link sharing |

## List Permissions

```bash
gog drive permissions <fileId>
```

Shows who has access to a file and their roles.

```bash
gog drive permissions 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## Get Web URL

```bash
gog drive url <fileId>
```

Returns the URL to open a file in the browser.

```bash
gog drive url 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## Copy File

```bash
gog drive copy <fileId> <name>
```

Creates a copy of a file with a new name.

```bash
gog drive copy 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Report Copy"
```

## List Shared Drives

```bash
gog drive drives
```

Lists all shared drives the authenticated account has access to.

## Upload as Google Doc (Conversion)

`gog drive upload` uploads files in their native format (e.g., `.md` stays as `text/markdown`). To upload a local file **and convert it to a Google Doc** so it's editable in Drive, use the Google Drive API directly via curl.

This requires exchanging the gog refresh token for an access token first.

### Step 1: Get an access token

```bash
# Read credentials
CLIENT_ID=$(python3 -c "import json; print(json.load(open('$HOME/Library/Application Support/gogcli/credentials.json'))['client_id'])")
CLIENT_SECRET=$(python3 -c "import json; print(json.load(open('$HOME/Library/Application Support/gogcli/credentials.json'))['client_secret'])")

# Export refresh token to temp file, extract it
gog auth tokens export craig@indemn.ai --out=/tmp/_gog_token.json --overwrite
REFRESH_TOKEN=$(python3 -c "import json; print(json.load(open('/tmp/_gog_token.json'))['refresh_token'])")
rm -f /tmp/_gog_token.json

# Exchange for access token
ACCESS_TOKEN=$(curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "refresh_token=$REFRESH_TOKEN" \
  -d "grant_type=refresh_token" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### Step 2: Upload with conversion

```bash
curl -s -X POST "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,mimeType,webViewLink" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "metadata={\"name\":\"Document Title\",\"mimeType\":\"application/vnd.google-apps.document\"};type=application/json;charset=UTF-8" \
  -F "file=@/path/to/local/file.md;type=text/markdown"
```

**Key:** Setting `mimeType` to `application/vnd.google-apps.document` in the metadata tells the Drive API to convert the uploaded file into a native Google Doc.

### Optional: Upload to a specific folder

Add `"parents":["FOLDER_ID"]` to the metadata JSON:

```bash
curl -s -X POST "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,mimeType,webViewLink" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "metadata={\"name\":\"Document Title\",\"mimeType\":\"application/vnd.google-apps.document\",\"parents\":[\"FOLDER_ID\"]};type=application/json;charset=UTF-8" \
  -F "file=@/path/to/local/file.md;type=text/markdown"
```

### Supported source formats for conversion

| Local format | Content type | Converts to |
|-------------|-------------|------------|
| `.md`, `.txt`, `.html` | `text/markdown`, `text/plain`, `text/html` | Google Doc |
| `.csv` | `text/csv` | Google Sheet |
| `.pptx` | `application/vnd.openxmlformats-officedocument.presentationml.presentation` | Google Slides |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | Google Doc |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | Google Sheet |

---

## Common Patterns

**Find a folder, then list its contents:**
```bash
# 1. Search for the folder
gog drive search "Customers" --json
# 2. Use the folder ID from results to list contents
gog drive ls --parent=<folderId> --json
```

**Upload a file to a specific folder:**
```bash
# 1. Find the target folder
gog drive search "Meeting Notes" --json
# 2. Upload using the folder ID
gog drive upload ./notes.pdf --parent=<folderId>
```

**Export a Google Doc for local processing:**
```bash
# 1. Search for the doc
gog drive search "Quarterly Report" --json
# 2. Export as text for analysis
gog drive download <fileId> --format=txt --out=./report.txt
```

**Share a file and get its link:**
```bash
gog drive share <fileId> --email=person@company.com --role=reader
gog drive url <fileId>
```
