#!/usr/bin/env bash
set -euo pipefail

# curl-airtable.sh <url> [curl flags...]
# Authenticated Airtable API calls via 1Password — credentials never exposed.

if [ $# -lt 1 ]; then
  echo "Usage: curl-airtable.sh <url> [curl flags...]" >&2
  exit 1
fi

URL="$1"; shift

PAT=$(op read "op://cli-secrets/Airtable PAT/credential" 2>/dev/null) || {
  echo "ERROR: Failed to read Airtable PAT from 1Password" >&2
  echo "Check: op whoami && op item get 'Airtable PAT' --vault cli-secrets" >&2
  exit 1
}

exec curl -s -H "Authorization: Bearer $PAT" "$URL" "$@"
