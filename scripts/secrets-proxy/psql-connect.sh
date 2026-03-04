#!/usr/bin/env bash
set -euo pipefail

# psql-connect.sh [psql flags...]
# Connects to Neon Postgres via 1Password — credentials never exposed.

CONN=$(op read "op://cli-secrets/Neon Connection String/credential" 2>/dev/null) || {
  echo "ERROR: Failed to read Neon Connection String from 1Password" >&2
  echo "Check: op whoami && op item get 'Neon Connection String' --vault cli-secrets" >&2
  exit 1
}

exec /opt/homebrew/opt/libpq/bin/psql "$CONN" "$@"
