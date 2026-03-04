#!/usr/bin/env bash
set -euo pipefail

# curl-langfuse.sh <api-path> [curl flags...]
# Authenticated Langfuse API calls via 1Password — credentials never exposed.

if [ $# -lt 1 ]; then
  echo "Usage: curl-langfuse.sh <api-path> [curl flags...]" >&2
  exit 1
fi

API_PATH="$1"; shift

HOST=$(op read "op://cli-secrets/Langfuse Keys/host" 2>/dev/null) || {
  echo "ERROR: Failed to read Langfuse Keys from 1Password" >&2
  exit 1
}
PUB=$(op read "op://cli-secrets/Langfuse Keys/public_key" 2>/dev/null) || {
  echo "ERROR: Failed to read Langfuse public key from 1Password" >&2
  exit 1
}
SEC=$(op read "op://cli-secrets/Langfuse Keys/secret_key" 2>/dev/null) || {
  echo "ERROR: Failed to read Langfuse secret key from 1Password" >&2
  exit 1
}

exec curl -s -u "${PUB}:${SEC}" "${HOST}${API_PATH}" "$@"
