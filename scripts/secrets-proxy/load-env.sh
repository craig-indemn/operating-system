#!/usr/bin/env bash
# load-env.sh — SessionStart hook that loads .env vars into CLAUDE_ENV_FILE.
# This runs as a hook (not a Claude tool call), so the guard doesn't apply.
# Only loads vars that wrapper scripts and skills need at runtime.

set -euo pipefail

ENV_FILE="/Users/home/Repositories/operating-system/.env"

if [ ! -f "$ENV_FILE" ]; then
  exit 0
fi

if [ -z "${CLAUDE_ENV_FILE:-}" ]; then
  exit 0
fi

# Source .env to get the values
source "$ENV_FILE"

# Write secrets-proxy PATH
echo "PATH=/Users/home/Repositories/operating-system/scripts/secrets-proxy:\$PATH" >> "$CLAUDE_ENV_FILE"

# Write 1Password service account token (needed by all op-based wrapper scripts)
if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]; then
  echo "OP_SERVICE_ACCOUNT_TOKEN=$OP_SERVICE_ACCOUNT_TOKEN" >> "$CLAUDE_ENV_FILE"
fi

# Write non-secret config vars used by skills and scripts
[ -n "${AWS_ACCOUNT_ID:-}" ] && echo "AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID" >> "$CLAUDE_ENV_FILE"
[ -n "${AWS_DEFAULT_REGION:-}" ] && echo "AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION" >> "$CLAUDE_ENV_FILE"
[ -n "${AWS_DEV_INSTANCE_ID:-}" ] && echo "AWS_DEV_INSTANCE_ID=$AWS_DEV_INSTANCE_ID" >> "$CLAUDE_ENV_FILE"
[ -n "${AWS_PROD_INSTANCE_ID:-}" ] && echo "AWS_PROD_INSTANCE_ID=$AWS_PROD_INSTANCE_ID" >> "$CLAUDE_ENV_FILE"
[ -n "${OS_ROOT:-}" ] && echo "OS_ROOT=$OS_ROOT" >> "$CLAUDE_ENV_FILE"
