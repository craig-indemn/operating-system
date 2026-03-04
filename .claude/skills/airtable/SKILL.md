---
name: airtable
description: Query and manage Airtable bases and records via REST API. Use for bot configs, EventGuard ops, and operational data.
---

# Airtable

Access Indemn's 211 Airtable bases via REST API with curl. Covers bot configurations, EventGuard operations, and other structured data.

## Status Check

```bash
curl-airtable.sh "https://api.airtable.com/v0/meta/bases" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK — {len(d.get(\"bases\",[]))} bases')" && echo "AUTHENTICATED" || echo "AUTH FAILED"
```

## Setup

1. Go to https://airtable.com > Profile menu > Builder Hub > Personal Access Tokens
2. Create token with scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
3. Scope to all bases (or specific ones)
4. Store in 1Password:
```bash
op item create --vault "indemn-os" --category "API Credential" --title "Airtable PAT" credential="pat..."
```

## Usage

All commands use `curl-airtable.sh` which injects the auth header from 1Password.

### List all bases
```bash
curl-airtable.sh "https://api.airtable.com/v0/meta/bases" | jq '.bases[] | {id, name}'
```

### List tables in a base
```bash
curl-airtable.sh "https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables" | jq '.tables[] | {id, name}'
```

### Read records
```bash
curl-airtable.sh "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}" | jq '.records[:5]'
```

### Read with filtering
```bash
curl-airtable.sh "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?filterByFormula={FIELD}='VALUE'" | jq '.records'
```

### Create a record
```bash
curl-airtable.sh "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}" \
  -X POST -H "Content-Type: application/json" \
  -d '{"fields": {"Name": "New Record", "Status": "Active"}}'
```

### Update a record
```bash
curl-airtable.sh "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/{RECORD_ID}" \
  -X PATCH -H "Content-Type: application/json" \
  -d '{"fields": {"Status": "Complete"}}'
```

### Pagination
Airtable returns max 100 records per request. If there's more, the response includes an `offset` field:
```bash
curl-airtable.sh "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?offset={OFFSET_VALUE}"
```

For base IDs and table schemas used at Indemn, see `references/api-spec.md`.
