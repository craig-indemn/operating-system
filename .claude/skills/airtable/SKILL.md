---
name: airtable
description: Query and manage Airtable bases and records via REST API. Use for bot configs, EventGuard ops, and operational data.
---

# Airtable

Access Indemn's 211 Airtable bases via REST API with curl. Covers bot configurations, EventGuard operations, and other structured data.

## Status Check

```bash
[ -n "$AIRTABLE_PAT" ] && echo "TOKEN SET" || echo "AIRTABLE_PAT not set"
```

Verify access:
```bash
curl -s "https://api.airtable.com/v0/meta/bases" \
  -H "Authorization: Bearer $AIRTABLE_PAT" | head -c 200 && echo " — AUTHENTICATED" || echo "AUTH FAILED"
```

## Setup

1. Go to https://airtable.com > Profile menu > Builder Hub > Personal Access Tokens
2. Create token with scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
3. Scope to all bases (or specific ones)
4. Set environment variable:
```bash
export AIRTABLE_PAT="pat..."
```
Add to `~/.zshrc` to persist.

## Usage

### List all bases
```bash
curl -s "https://api.airtable.com/v0/meta/bases" \
  -H "Authorization: Bearer $AIRTABLE_PAT" | jq '.bases[] | {id, name}'
```

### List tables in a base
```bash
curl -s "https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables" \
  -H "Authorization: Bearer $AIRTABLE_PAT" | jq '.tables[] | {id, name}'
```

### Read records
```bash
curl -s "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}" \
  -H "Authorization: Bearer $AIRTABLE_PAT" | jq '.records[:5]'
```

### Read with filtering
```bash
curl -s "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?filterByFormula={FIELD}='VALUE'" \
  -H "Authorization: Bearer $AIRTABLE_PAT" | jq '.records'
```

### Create a record
```bash
curl -s -X POST "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}" \
  -H "Authorization: Bearer $AIRTABLE_PAT" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"Name": "New Record", "Status": "Active"}}'
```

### Update a record
```bash
curl -s -X PATCH "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/{RECORD_ID}" \
  -H "Authorization: Bearer $AIRTABLE_PAT" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"Status": "Complete"}}'
```

### Pagination
Airtable returns max 100 records per request. If there's more, the response includes an `offset` field:
```bash
curl -s "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?offset={OFFSET_VALUE}" \
  -H "Authorization: Bearer $AIRTABLE_PAT"
```

For base IDs and table schemas used at Indemn, see `references/api-spec.md`.
