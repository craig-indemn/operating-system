---
name: 1password
description: Manage personal secrets via 1Password CLI (op) — read tokens, store credentials, manage vaults. Use when accessing personal API tokens, storing new credentials, or managing the cli-secrets vault.
---

# 1Password CLI

Personal secrets management via `op` CLI. All OS personal tokens live in the `cli-secrets` vault.

## Status Check

```bash
op whoami && echo "1PASSWORD AUTHENTICATED" || echo "1PASSWORD NOT CONFIGURED"
```

Verify vault access:
```bash
op vault get "cli-secrets" --format json | python3 -c "import sys,json; v=json.load(sys.stdin); print(f'Vault: {v[\"name\"]} ({v[\"id\"]})')"
```

## Prerequisites

- **1Password desktop app** installed and signed in
- **1Password CLI** (`op`) installed
- CLI integration enabled in desktop app (Settings > Developer > CLI Integration)

## Setup

### Install CLI
```bash
brew install 1password-cli
```

### Enable CLI Integration
1. Open 1Password desktop app
2. Settings > Developer > "Integrate with 1Password CLI"
3. This allows `op` to authenticate via the desktop app (biometric unlock)

### Create Vault
```bash
op vault create "cli-secrets"
```

### Store Personal Tokens
```bash
op item create --vault "cli-secrets" --category "API Credential" --title "Airtable PAT" credential=<value>
op item create --vault "cli-secrets" --category "API Credential" --title "Linear API Token" credential=<value>
op item create --vault "cli-secrets" --category "API Credential" --title "Neon Connection String" credential=<value>
op item create --vault "cli-secrets" --category "API Credential" --title "Langfuse Keys" \
  host=<value> public_key=<value> secret_key=<value>
op item create --vault "cli-secrets" --category "API Credential" --title "Slack Tokens" \
  xoxc_token=<value> xoxd_cookie=<value>
op item create --vault "cli-secrets" --category "API Credential" --title "Gemini API Key" credential=<value>
op item create --vault "cli-secrets" --category "API Credential" --title "Together API Key" credential=<value>
```

## Usage

### Read a secret
```bash
op read "op://cli-secrets/Airtable PAT/credential"
op read "op://cli-secrets/Langfuse Keys/public_key"
```

### List items in vault
```bash
op item list --vault "cli-secrets"
```

### Create a new item
```bash
op item create --vault "cli-secrets" --category "API Credential" --title "<name>" credential=<value>
```

### Create multi-field item
```bash
op item create --vault "cli-secrets" --category "API Credential" --title "<name>" field1=val1 field2=val2
```

### Update a field
```bash
op item edit "<title>" --vault "cli-secrets" credential=<new-value>
```

### Delete an item
```bash
op item delete "<title>" --vault "cli-secrets"
```

## Vault Convention

| Item Title | Fields | Used By |
|------------|--------|---------|
| Airtable PAT | credential | curl-airtable.sh |
| Linear API Token | credential | linearis-proxy.sh |
| Neon Connection String | credential | psql-connect.sh |
| Langfuse Keys | host, public_key, secret_key | curl-langfuse.sh |
| Slack Tokens | xoxc_token, xoxd_cookie | slack-env.sh |
| Gemini API Key | credential | image-gen wrapper |
| Together API Key | credential | together wrapper |

## Important

- All personal tokens go in the `cli-secrets` vault
- Shared infrastructure secrets (MongoDB URIs, Redis, etc.) are in AWS Secrets Manager — use the `/aws` skill
- Item titles must match exactly what wrapper scripts expect
- `op` authenticates via the desktop app — no separate login needed if CLI integration is enabled
