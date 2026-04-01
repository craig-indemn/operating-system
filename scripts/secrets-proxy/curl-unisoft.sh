#!/usr/bin/env bash
set -euo pipefail

# curl-unisoft.sh <method> <operation> [json-body]
# Authenticated Unisoft REST proxy calls via 1Password — credentials never exposed.
#
# Usage:
#   curl-unisoft.sh GET health
#   curl-unisoft.sh POST GetInsuranceLOBs '{}'
#   curl-unisoft.sh POST SetQuote '{"Action":"Insert","Quote":{...}}'

PROXY_BASE="http://54.83.28.79:5000"

if [ $# -lt 2 ]; then
  echo "Usage: curl-unisoft.sh <GET|POST> <operation> [json-body]" >&2
  echo "  curl-unisoft.sh GET health" >&2
  echo "  curl-unisoft.sh POST GetInsuranceLOBs '{}'" >&2
  exit 1
fi

METHOD="$1"
OP="$2"
BODY="${3:-"{}"}"

API_KEY=$(op read "op://cli-secrets/Unisoft Proxy API Key/credential" 2>/dev/null) || {
  echo "ERROR: Failed to read Unisoft Proxy API Key from 1Password" >&2
  echo "Check: op whoami && op item get 'Unisoft Proxy API Key' --vault cli-secrets" >&2
  exit 1
}

if [ "$METHOD" = "GET" ]; then
  exec curl -4 -s "${PROXY_BASE}/api/${OP}" -H "X-Api-Key: ${API_KEY}"
else
  exec curl -4 -s -X POST "${PROXY_BASE}/api/soap/${OP}" \
    -H "X-Api-Key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "${BODY}"
fi
