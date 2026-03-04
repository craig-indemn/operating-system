---
name: 1password
description: Manage personal secrets via 1Password CLI (op) — read tokens, store credentials, manage vaults. Use when accessing personal API tokens, storing new credentials, or managing the cli-secrets vault.
---

# 1Password CLI

Personal secrets management via `op` CLI + service account. All OS personal tokens live in the `cli-secrets` vault. Authentication is via `OP_SERVICE_ACCOUNT_TOKEN` env var (loaded automatically by SessionStart hook).

## Status Check

```bash
op whoami && echo "1PASSWORD AUTHENTICATED" || echo "1PASSWORD NOT CONFIGURED"
```

Verify vault access:
```bash
op vault get "cli-secrets" --format json | python3 -c "import sys,json; v=json.load(sys.stdin); print(f'Vault: {v[\"name\"]} ({v[\"id\"]})')"
```

## How It Works

Each team member has their own **1Password service account** with read/write access to a vault named `cli-secrets`. The service account token (`OP_SERVICE_ACCOUNT_TOKEN`) is stored in `.env` and loaded into Claude Code sessions automatically via the `load-env.sh` SessionStart hook.

This means:
- No desktop app interaction needed — fully headless
- Works in Claude Code's sandboxed shell (desktop app biometric prompts don't surface there)
- Each person's tokens are isolated in their own vault
- Wrapper scripts in `scripts/secrets-proxy/` call `op read` to pull secrets at runtime

## Setup (New Team Member)

### 1. Install CLI
```bash
brew install 1password-cli
```

### 2. Create a Service Account
1. Go to your **personal** 1Password account (not the team account)
2. Navigate to: Developer > Service Accounts > New Service Account
3. Name it something like `cli-secrets-sa`
4. Grant it **Read & Write** access to a vault named `cli-secrets`
5. Copy the service account token (starts with `ops_...`)

### 3. Add Token to .env
Add to your OS repo `.env` file:
```bash
export OP_SERVICE_ACCOUNT_TOKEN="ops_your_token_here"
```

### 4. Create Vault and Store Tokens
```bash
# Create the vault (if it doesn't exist)
op vault create "cli-secrets"

# Store personal tokens — item titles must match exactly
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

### 5. Verify
```bash
op read "op://cli-secrets/Airtable PAT/credential"
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
- Authentication is via service account token, not desktop app
- The vault name `cli-secrets` is generic by design — not tied to any specific org
