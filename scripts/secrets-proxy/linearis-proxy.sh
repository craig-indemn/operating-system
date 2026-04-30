#!/usr/bin/env bash
set -euo pipefail

# linearis-proxy.sh [linearis args...]
# Runs linearis with Linear API token from 1Password — credentials never exposed.

TOKEN=$(op read "op://cli-secrets/Linear API Token/credential" 2>/dev/null) || {
  echo "ERROR: Failed to read Linear API Token from 1Password" >&2
  echo "Check: op whoami && op item get 'Linear API Token' --vault cli-secrets" >&2
  exit 1
}

LINEAR_API_KEY="$TOKEN" LINEAR_API_TOKEN="$TOKEN" exec linearis "$@"
