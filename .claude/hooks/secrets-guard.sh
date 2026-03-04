#!/usr/bin/env bash
# secrets-guard.sh — PreToolUse hook that blocks credential exposure.
# Blocks: .env reads, secret var echoing, raw env dumps.
# Allows: wrapper scripts, already-secure CLIs (gh, gog, stripe, vercel, aws).
#
# Protocol: exit 0 = allow, exit 2 = block (reason on stderr).

set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null || echo "")
TOOL_INPUT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('tool_input',{})))" 2>/dev/null || echo "{}")

block() {
  echo "$1" >&2
  exit 2
}

# --- Read tool: block .env file reads ---
if [ "$TOOL_NAME" = "Read" ]; then
  FILE_PATH=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('file_path',''))" 2>/dev/null || echo "")
  if echo "$FILE_PATH" | grep -qiE '\.env($|\.legacy$|\.local$|\.dev$|\.prod$|\.secret)'; then
    block "BLOCKED: Reading .env files exposes credentials. Use wrapper scripts instead: mongosh-connect.sh, psql-connect.sh, curl-airtable.sh, curl-langfuse.sh, linearis-proxy.sh, curl-apollo.sh, slack-env.sh. For AWS config (non-secret): read values from CLAUDE.md."
  fi
  exit 0
fi

# --- Bash tool: block credential-leaking commands ---
if [ "$TOOL_NAME" = "Bash" ]; then
  COMMAND=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('command',''))" 2>/dev/null || echo "")

  # Allow wrapper scripts unconditionally
  if echo "$COMMAND" | grep -qE '(mongosh-connect|psql-connect|curl-airtable|curl-langfuse|linearis-proxy|curl-apollo|slack-env|local-dev-aws)\.sh'; then
    exit 0
  fi

  # Allow already-secure CLIs
  if echo "$COMMAND" | grep -qE '^(gh |gog |stripe |vercel |aws |op |bd |linearis )'; then
    exit 0
  fi

  # Block: source .env / . .env
  if echo "$COMMAND" | grep -qE '(source|\.)\s+[^ ]*\.env'; then
    block "BLOCKED: Sourcing .env files exposes credentials in the session. Use wrapper scripts instead — they pull secrets at runtime from AWS Secrets Manager or 1Password."
  fi

  # Block: reading .env files with cat/head/tail/less/more
  if echo "$COMMAND" | grep -qE '(cat|head|tail|less|more)\s+[^ ]*\.env'; then
    block "BLOCKED: Reading .env files exposes credentials. Secrets are managed via wrapper scripts (AWS Secrets Manager + 1Password)."
  fi

  # Block: bare printenv / env (full environment dump)
  if echo "$COMMAND" | grep -qE '^\s*(printenv|env)\s*$'; then
    block "BLOCKED: Full environment dump may expose credentials. To check a specific non-secret var: echo \$AWS_ACCOUNT_ID"
  fi

  # Block: echoing known secret variable names
  SECRET_VARS="MONGODB_PROD_URI|MONGODB_DEV_URI|MONGODB_URI|NEON_CONNECTION_STRING|AIRTABLE_PAT|LINEAR_API_TOKEN|LINEAR_API_KEY|APOLLO_API_KEY|LANGFUSE_SECRET_KEY|LANGFUSE_PUBLIC_KEY|SLACK_XOXC_TOKEN|SLACK_XOXD_COOKIE|SLACK_TOKEN|GEMINI_API_KEY|TOGETHER_API_KEY|STRIPE_API_KEY|OS_TERMINAL_TOKEN"
  if echo "$COMMAND" | grep -qE "(echo|printf|cat).*\\\$(${SECRET_VARS})"; then
    block "BLOCKED: Echoing secret variables exposes credentials. Use the appropriate wrapper script to access the service directly."
  fi

  # Block: direct variable expansion in mongosh/psql commands (legacy patterns)
  if echo "$COMMAND" | grep -qE 'mongosh\s+"\$MONGODB'; then
    block "BLOCKED: Use mongosh-connect.sh instead of mongosh with raw URI. Example: mongosh-connect.sh dev tiledesk --eval 'db.stats()'"
  fi

  if echo "$COMMAND" | grep -qE 'psql\s+"\$NEON'; then
    block "BLOCKED: Use psql-connect.sh instead of psql with raw connection string. Example: psql-connect.sh -c 'SELECT 1'"
  fi

  # Allow everything else
  exit 0
fi

# All other tools: allow
exit 0
