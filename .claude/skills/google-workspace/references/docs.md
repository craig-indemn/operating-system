# Docs Reference — gog docs

Complete reference for Google Docs operations via the `gog` CLI.

## Read Document Content

```bash
gog docs cat <docId> [--max-bytes=2000000]
```

Prints the document content as plain text. Default max is 2MB.

```bash
# Read a document
gog docs cat 1aBcDeFgHiJkLmNoPqRsTuVwXyZ

# Limit output size
gog docs cat 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --max-bytes=50000
```

## Create Document

```bash
gog docs create <title> [--parent=STRING]
```

Creates a new Google Doc. `--parent` is a folder ID, not a path.

```bash
# Create in root
gog docs create "Call Prep - INSURICA"

# Create in a specific folder
gog docs create "Meeting Notes - Q1" --parent=1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## Export Document

```bash
gog docs export <docId> [--format=pdf|docx|txt] [--out=STRING]
```

Exports a Google Doc to a local file in the specified format.

```bash
# Export as PDF
gog docs export 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=pdf --out=./report.pdf

# Export as Word document
gog docs export 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=docx --out=./report.docx

# Export as plain text
gog docs export 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=txt --out=./report.txt
```

## Get Document Metadata

```bash
gog docs info <docId>
```

Returns metadata about the document (title, last modified, owner, etc.).

```bash
gog docs info 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## Copy Document

```bash
gog docs copy <docId> <title>
```

Creates a copy of a document with a new title.

```bash
gog docs copy 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Template Copy - New Client"
```

## Common Patterns

**Read a doc for analysis:**
```bash
# Find the doc
gog drive search "Quarterly Report" --json
# Read its content
gog docs cat <docId>
```

**Create a doc from a template:**
```bash
# Copy the template
gog docs copy <templateDocId> "New Client Onboarding - Acme Corp"
```

**Export for offline use:**
```bash
gog docs export <docId> --format=pdf --out=./document.pdf
```

**Note**: Google Docs does not support direct content writing via the gog CLI. To populate a new doc, create it with `gog docs create`, then use the Google Docs web UI or the Docs API directly. For reading content, `gog docs cat` is the primary command.
