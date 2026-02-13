# Airtable REST API Reference

Base URL: `https://api.airtable.com/v0`
Auth: `Authorization: Bearer $AIRTABLE_PAT`

## Endpoints

### Meta API (discover bases and tables)

**List bases:**
```
GET /meta/bases
```

**List tables in a base:**
```
GET /meta/bases/{baseId}/tables
```

### Records API

**List records:**
```
GET /v0/{baseId}/{tableIdOrName}
```
Query params:
- `maxRecords` — max records to return (default 100)
- `pageSize` — records per page (max 100)
- `offset` — pagination cursor from previous response
- `filterByFormula` — Airtable formula to filter records
- `sort[0][field]` — field to sort by
- `sort[0][direction]` — `asc` or `desc`
- `fields[]` — specific fields to return
- `view` — return records from a specific view

**Get a record:**
```
GET /v0/{baseId}/{tableIdOrName}/{recordId}
```

**Create records:**
```
POST /v0/{baseId}/{tableIdOrName}
Body: {"records": [{"fields": {"Name": "Value"}}]}
```
Max 10 records per request.

**Update records (PATCH = partial, PUT = full replace):**
```
PATCH /v0/{baseId}/{tableIdOrName}
Body: {"records": [{"id": "recXXX", "fields": {"Status": "Done"}}]}
```

**Delete records:**
```
DELETE /v0/{baseId}/{tableIdOrName}?records[]={recordId}
```
Max 10 records per request.

## Formula Examples

```
filterByFormula=AND({Status}='Active', {Company}='INSURICA')
filterByFormula=SEARCH('renewal', LOWER({Notes}))
filterByFormula=IS_AFTER({Created}, '2025-01-01')
filterByFormula={Priority}>=3
```

## Rate Limits
- 5 requests per second per base
- Batch operations (up to 10 records) count as 1 request

## Indemn-Specific Bases
Base IDs and table names will be populated after initial connection. Run the list bases command to discover them:
```bash
curl -s "https://api.airtable.com/v0/meta/bases" -H "Authorization: Bearer $AIRTABLE_PAT" | jq '.bases[] | {id, name}'
```
