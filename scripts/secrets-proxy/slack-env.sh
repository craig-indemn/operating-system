#!/usr/bin/env bash
set -euo pipefail

# slack-env.sh <command...>
# Exports Slack tokens from 1Password, then runs the given command.
# The slack_client.py Keychain fallback still takes priority if available.
#
# Usage: slack-env.sh python3 -c "from slack_client import get_client; ..."

if [ $# -lt 1 ]; then
  echo "Usage: slack-env.sh <command...>" >&2
  exit 1
fi

XOXC=$(op read "op://cli-secrets/Slack Tokens/xoxc_token" 2>/dev/null) || {
  echo "ERROR: Failed to read Slack Tokens from 1Password" >&2
  echo "Check: op whoami && op item get 'Slack Tokens' --vault cli-secrets" >&2
  exit 1
}
XOXD=$(op read "op://cli-secrets/Slack Tokens/xoxd_cookie" 2>/dev/null) || {
  echo "ERROR: Failed to read Slack cookie from 1Password" >&2
  exit 1
}

export SLACK_XOXC_TOKEN="$XOXC"
export SLACK_XOXD_COOKIE="$XOXD"

exec "$@"
