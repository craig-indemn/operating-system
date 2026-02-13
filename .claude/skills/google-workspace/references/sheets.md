# Sheets Reference — gog sheets

Complete reference for Google Sheets operations via the `gog` CLI.

## Get Values

```bash
gog sheets get <spreadsheetId> <range> [--dimension=ROWS|COLUMNS] [--render=FORMATTED_VALUE|UNFORMATTED_VALUE|FORMULA] [--json]
```

Reads cell values from a spreadsheet.

```bash
# Read a specific range
gog sheets get 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:D10" --json

# Read an entire column
gog sheets get 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A:A" --json

# Read by columns instead of rows
gog sheets get 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:D10" --dimension=COLUMNS --json

# Get raw/unformatted values
gog sheets get 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:D10" --render=UNFORMATTED_VALUE --json

# Get formulas instead of computed values
gog sheets get 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:D10" --render=FORMULA --json
```

### Range Syntax

Ranges use standard A1 notation:
- `Sheet1!A1:D10` — specific rectangle
- `Sheet1!A:A` — entire column A
- `Sheet1!1:1` — entire row 1
- `Sheet1!A1:D` — column A through D, all rows from 1
- `Sheet1` — entire sheet

If the sheet name contains spaces, wrap in single quotes: `'My Sheet'!A1:D10`

## Update Values

```bash
gog sheets update <spreadsheetId> <range> [values...] [--values-json=STRING] [--input=RAW|USER_ENTERED]
```

Updates cell values. Values use **pipe-separated cells** and **comma-separated rows**.

```bash
# Update a single cell
gog sheets update 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1" "Hello"

# Update a row (pipe separates cells)
gog sheets update 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:C1" "Name|Email|Status"

# Update multiple rows (comma separates rows, pipe separates cells)
gog sheets update 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:C2" "Name|Email|Status,Alice|alice@co.com|Active"

# Using JSON for complex values
gog sheets update 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:B2" --values-json='[["Name","Score"],["Alice",95]]'

# RAW input (values stored exactly as provided, no parsing)
gog sheets update 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1" "=SUM(B1:B10)" --input=RAW

# USER_ENTERED (values parsed as if typed in the UI — formulas evaluated, dates parsed)
gog sheets update 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1" "=SUM(B1:B10)" --input=USER_ENTERED
```

### Value Format

| Format | Syntax | Example |
|--------|--------|---------|
| Single cell | `"value"` | `"Hello"` |
| Single row | `"cell1\|cell2\|cell3"` | `"Name\|Email\|Status"` |
| Multiple rows | `"row1cell1\|row1cell2,row2cell1\|row2cell2"` | `"Alice\|95,Bob\|87"` |
| JSON | `--values-json='[[...],[...]]'` | `--values-json='[["A",1],["B",2]]'` |

## Append Values

```bash
gog sheets append <spreadsheetId> <range> [values...] [--values-json=STRING] [--insert=OVERWRITE|INSERT_ROWS]
```

Appends rows after the last row with data in the specified range.

```bash
# Append a row
gog sheets append 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A:C" "NewName|new@email.com|Pending"

# Append multiple rows
gog sheets append 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A:C" "Alice|a@co.com|Active,Bob|b@co.com|Pending"

# Append using JSON
gog sheets append 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A:C" --values-json='[["Alice","a@co.com","Active"]]'

# Insert new rows instead of overwriting
gog sheets append 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A:C" "NewRow|Data|Here" --insert=INSERT_ROWS
```

## Clear Range

```bash
gog sheets clear <spreadsheetId> <range>
```

Clears all values in the specified range (formatting is preserved).

```bash
gog sheets clear 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A2:D100"
```

## Format Cells

```bash
gog sheets format <spreadsheetId> <range>
```

Format cells in a range.

```bash
gog sheets format 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:D1"
```

## Get Spreadsheet Metadata

```bash
gog sheets metadata <spreadsheetId>
```

Returns spreadsheet metadata including sheet names, sheet IDs, and properties.

```bash
gog sheets metadata 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

Use this to discover sheet names before reading/writing data.

## Create Spreadsheet

```bash
gog sheets create <title> [--sheets=STRING]
```

Creates a new spreadsheet.

```bash
# Create with default single sheet
gog sheets create "Q1 Tracking"

# Create with named sheets
gog sheets create "Sales Pipeline" --sheets="Deals,Contacts,Notes"
```

## Copy Spreadsheet

```bash
gog sheets copy <spreadsheetId> <title>
```

Creates a copy of an existing spreadsheet.

```bash
gog sheets copy 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Pipeline Tracker - Copy"
```

## Export Spreadsheet

```bash
gog sheets export <spreadsheetId> [--format=pdf|xlsx|csv]
```

Exports the spreadsheet to a local file.

```bash
# Export as Excel
gog sheets export 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=xlsx

# Export as CSV
gog sheets export 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=csv

# Export as PDF
gog sheets export 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=pdf
```

## Common Patterns

**Read a sheet to understand its structure:**
```bash
# 1. Get metadata to see sheet names
gog sheets metadata 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
# 2. Read the header row
gog sheets get 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!1:1" --json
# 3. Read all data
gog sheets get 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A1:Z1000" --json
```

**Add a record to a tracker:**
```bash
gog sheets append 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!A:D" "2025-01-15|INSURICA|Renewal|In Progress"
```

**Update a specific cell:**
```bash
gog sheets update 1aBcDeFgHiJkLmNoPqRsTuVwXyZ "Sheet1!D5" "Completed"
```

**Create a report from scratch:**
```bash
# 1. Create the spreadsheet
gog sheets create "Weekly Report" --sheets="Summary,Details"
# 2. Add headers
gog sheets update <newId> "Summary!A1:D1" "Metric|This Week|Last Week|Change"
# 3. Add data
gog sheets append <newId> "Summary!A:D" "Revenue|$45K|$42K|+7%"
```

**Export for sharing:**
```bash
gog sheets export 1aBcDeFgHiJkLmNoPqRsTuVwXyZ --format=xlsx
```
