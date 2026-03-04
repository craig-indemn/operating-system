---
name: postgres
description: Connect to Neon Postgres databases using neonctl and psql. Use for any direct database queries, schema exploration, or data analysis.
---

# Postgres (Neon)

Direct database access via `neonctl` (Neon management) and `psql` (SQL queries).

## Prerequisites

- **psql**: No account needed — it's just the Postgres client binary
- **neonctl**: Neon account with access to the Indemn project (for branch management, not required for basic queries)
- **1Password**: Connection string stored in 1Password vault `indemn-os`

## Status Check

```bash
(which psql || test -x /opt/homebrew/opt/libpq/bin/psql) && echo "PSQL INSTALLED" || echo "PSQL NOT INSTALLED"
which neonctl && echo "NEONCTL INSTALLED" || echo "NEONCTL NOT INSTALLED"
```

Test connection:
```bash
psql-connect.sh -c "SELECT 1" 2>/dev/null && echo "CONNECTED" || echo "CONNECTION FAILED"
```

## Setup

### Install psql
```bash
brew install libpq
```
**Note**: Homebrew installs psql to `/opt/homebrew/opt/libpq/bin/psql` but does NOT add it to PATH (to avoid conflicts with a full Postgres install). Either add it to PATH:
```bash
echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```
Or use the full path directly: `/opt/homebrew/opt/libpq/bin/psql`

### Install neonctl
```bash
npm install -g neonctl
```

### Authenticate neonctl (optional — only needed for branch/project management)
```bash
neonctl auth
```
Opens browser for OAuth. Or use API key:
1. Neon Console > Account Settings > API Keys > Create
2. Set: `export NEON_API_KEY="..."`

### Connection string
Stored in 1Password at `op://indemn-os/Neon Connection String/credential`. Access via `psql-connect.sh` wrapper — no local env vars needed.

## Usage

**Important**: This database uses **PascalCase** table and column names. You must double-quote all identifiers in SQL.

### Connect interactively
```bash
psql-connect.sh
```

### Run a query
```bash
psql-connect.sh -c 'SELECT count(*) FROM "Meeting"'
```

### Explore the schema
```bash
# List all tables
psql-connect.sh -c "\dt"

# Describe a table
psql-connect.sh -c '\d "Meeting"'

# List tables with row counts
psql-connect.sh -c "SELECT schemaname, tablename, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC"
```

### Query with JSON output
```bash
psql-connect.sh -t -A -c 'SELECT json_agg(row_to_json(t)) FROM (SELECT * FROM "Meeting" LIMIT 5) t'
```

### Neonctl management
```bash
neonctl projects list
neonctl branches list
neonctl connection-string
```

### Important
- **Read-only unless explicitly authorized.** Do not INSERT, UPDATE, or DELETE without permission.
- **PascalCase identifiers.** All table and column names must be double-quoted (e.g. `"Meeting"`, `"BusinessSignal"`).
- **Dynamic schema discovery.** Use `\dt` and `\d "TableName"` to discover the current schema before querying.
- For domain-specific meeting queries, see the `/meeting-intelligence` skill.
