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
