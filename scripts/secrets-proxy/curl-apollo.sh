#!/usr/bin/env bash
set -euo pipefail

# curl-apollo.sh <endpoint> [json-body]
# Authenticated Apollo.io API calls via 1Password — credentials never exposed.
# The api_key is injected into the JSON body (Apollo's auth pattern).

if [ $# -lt 1 ]; then
  echo "Usage: curl-apollo.sh <endpoint> [json-body]" >&2
  echo "Example: curl-apollo.sh /api/v1/mixed_companies/search '{\"q_organization_name\":\"Acme\"}'" >&2
  exit 1
fi

ENDPOINT="$1"; shift
BODY="${1:-\{\}}"; shift 2>/dev/null || true

KEY=$(op read "op://cli-secrets/Apollo API Key/credential" 2>/dev/null) || {
  echo "ERROR: Failed to read Apollo API Key from 1Password" >&2
  echo "Check: op whoami && op item get 'Apollo API Key' --vault cli-secrets" >&2
  exit 1
}

# Inject api_key into the JSON body
BODY_WITH_KEY=$(echo "$BODY" | python3 -c "
import sys, json
body = json.load(sys.stdin)
body['api_key'] = '$KEY'
print(json.dumps(body))
")

exec curl -s -X POST "https://api.apollo.io${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -H "Cache-Control: no-cache" \
  -d "$BODY_WITH_KEY" "$@"
