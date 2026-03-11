---
name: mongodb
description: Query MongoDB Atlas databases — tiledesk (bot configs, conversations, agents, orgs), plus middleware, observatory, and other operational databases. Use when the user asks about MongoDB data, bot configurations, conversations, organizations, or operational platform data.
---

# MongoDB (Atlas)

Direct database access via `mongosh` to Indemn's MongoDB Atlas clusters (prod and dev).

## Prerequisites

- **mongosh**: MongoDB Shell binary (no account needed)
- **AWS CLI**: Authenticated — MongoDB URIs stored in AWS Secrets Manager

## Status Check

```bash
which mongosh && echo "MONGOSH INSTALLED" || echo "MONGOSH NOT INSTALLED"
```

Test connection:
```bash
mongosh-connect.sh prod tiledesk --eval "db.runCommand({ping:1}).ok"
# Should return: 1
```

## Setup

### Install mongosh
```bash
brew install mongosh
```

### Connection strings
MongoDB URIs are stored in AWS Secrets Manager at `indemn/dev/shared/mongodb-uri` and `indemn/prod/shared/mongodb-uri`. Access via `mongosh-connect.sh` wrapper — no local env vars needed.

## Usage

### One-liner queries
```bash
mongosh-connect.sh prod tiledesk --eval '<js expression>'
```

### List collections with document counts
```bash
mongosh-connect.sh prod tiledesk --eval '
  db.getCollectionNames().forEach(c => {
    const n = db.getCollection(c).estimatedDocumentCount();
    if (n > 0) print(c + ": " + n);
  })
'
```

### Query with JSON output
```bash
mongosh-connect.sh prod tiledesk --eval '
  JSON.stringify(db.getCollection("organizations").findOne({name: "Indemn"}), null, 2)
'
```

### Sample a document shape
```bash
mongosh-connect.sh prod tiledesk --eval '
  JSON.stringify(db.getCollection("bot_configurations").findOne(), null, 2)
'
```

### Count with filter
```bash
mongosh-connect.sh prod tiledesk --eval '
  db.getCollection("requests").countDocuments({status: 1000})
'
```

### Aggregation
```bash
mongosh-connect.sh prod tiledesk --eval '
  JSON.stringify(db.getCollection("bot_tools").aggregate([
    {$group: {_id: "$type", count: {$sum: 1}}},
    {$sort: {count: -1}}
  ]).toArray(), null, 2)
'
```

### Switch databases
```bash
# Other databases on the same cluster:
mongosh-connect.sh prod middleware --eval '...'
mongosh-connect.sh prod observatory --eval '...'
mongosh-connect.sh prod quotes --eval '...'

# Dev cluster:
mongosh-connect.sh dev tiledesk --eval '...'
```

### Available databases
| Database | Size | Purpose |
|----------|------|---------|
| tiledesk | 11.4 GB | Primary — orgs, bots, conversations, KBs, tools, billing |
| chat21 | 2.5 GB | Chat engine data |
| observatory | 0.9 GB | Analytics and observability |
| bf-wedding | 0.5 GB | Legacy botfront project |
| quotes | 0.2 GB | Quote/proposal data |
| middleware | 0.06 GB | Middleware service data |
| airtable_sync | small | Airtable sync cache |
| evaluations | small | Evaluation service data |

## Before You Query

**Always read `references/query-patterns.md` first.** It has ready-to-use patterns for most common questions (active agents, conversation history, org lookups, billing, etc.). Don't explore the schema from scratch if a pattern already exists. Only fall back to sampling document shapes when query-patterns.md doesn't cover your need.

For full collection schemas: `references/schema-guide.md`

## Important

- **Read-only unless explicitly authorized.** Do not insert, update, or delete without permission.
- **Use `getCollection()`** — collection names may contain characters that don't work with dot notation.
- **Prefer `--quiet`** to suppress connection banners in output.
- **`estimatedDocumentCount()`** for fast counts, `countDocuments({})` for exact counts with filters.
