#!/usr/bin/env bash
set -euo pipefail

# local-dev-aws.sh [local-dev.sh args...]
# Pulls platform secrets from AWS Secrets Manager and runs local-dev.sh
# without needing a .env file with credentials.
#
# Usage: local-dev-aws.sh start platform --env=dev

# Parse --env flag from args to determine which AWS prefix to use
ENV="dev"
for arg in "$@"; do
  case "$arg" in
    --env=prod) ENV="prod" ;;
    --env=dev)  ENV="dev" ;;
  esac
done

echo "Pulling secrets from AWS (indemn/${ENV}/shared/*)..." >&2

# Shared infrastructure secrets from AWS Secrets Manager
# Path format: indemn/{env}/shared/{secret-name}
SM_PREFIX="indemn/${ENV}/shared"

export MONGODB_URI=$(aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/mongodb-uri" \
  --query 'SecretString' --output text 2>/dev/null) || true

export RABBITMQ_CONNECT_URL=$(aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/rabbitmq-url" \
  --query 'SecretString' --output text 2>/dev/null) || true
export CLOUDAMQP_URL="${RABBITMQ_CONNECT_URL:-}"

export OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/openai-api-key" \
  --query 'SecretString' --output text 2>/dev/null) || true

export ANTHROPIC_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/anthropic-api-key" \
  --query 'SecretString' --output text 2>/dev/null) || true

export PINECONE_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/pinecone-api-key" \
  --query 'SecretString' --output text 2>/dev/null) || true

export LANGSMITH_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/langsmith-api-key" \
  --query 'SecretString' --output text 2>/dev/null) || true

# Temp file for parsing JSON secrets safely
TMPFILE=$(mktemp)

# Non-secret config
export AWS_ACCOUNT_ID="780354157690"
export AWS_DEFAULT_REGION="us-east-1"

# Find workspace directory
WORKSPACE="${INDEMN_WORKSPACE:-$(dirname "$(find ~/Repositories ~/code ~/dev ~/Projects -name 'local-dev.sh' -maxdepth 1 2>/dev/null | head -1)" 2>/dev/null)}"

if [ -z "$WORKSPACE" ] || [ ! -f "$WORKSPACE/local-dev.sh" ]; then
  echo "ERROR: Could not find local-dev.sh. Set INDEMN_WORKSPACE env var." >&2
  exit 1
fi

# Also pull structured secrets
aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/redis-credentials" \
  --query 'SecretString' --output text > "$TMPFILE" 2>/dev/null || true

if [ -s "$TMPFILE" ]; then
  export REDIS_HOST=$(python3 -c "import json; d=json.load(open('$TMPFILE')); print(d['host'])")
  export REDIS_PORT=$(python3 -c "import json; d=json.load(open('$TMPFILE')); print(d['port'])")
  export REDIS_PASSWORD=$(python3 -c "import json; d=json.load(open('$TMPFILE')); print(d['password'])")
  export CACHE_REDIS_URL=$(python3 -c "import json; d=json.load(open('$TMPFILE')); print(d['url'])")
  export REDIS_URL="$CACHE_REDIS_URL"
fi

LIVEKIT_CREDS=$(aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/livekit-credentials" \
  --query 'SecretString' --output text 2>/dev/null) || true

if [ -n "$LIVEKIT_CREDS" ]; then
  export LIVEKIT_URL=$(echo "$LIVEKIT_CREDS" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['url'])")
  export LIVEKIT_API_KEY=$(echo "$LIVEKIT_CREDS" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['api_key'])")
  export LIVEKIT_API_SECRET=$(echo "$LIVEKIT_CREDS" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['api_secret'])")
fi

# Firebase credentials + auth secrets (needed by copilot-server)
# Note: The firebase-credentials secret may have malformed JSON in the
# service_account_json field. We parse tolerantly — extract known fields
# with regex, then try json.load on the embedded service account for
# client_email and private_key.
aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/firebase-credentials" \
  --query 'SecretString' --output text > "$TMPFILE" 2>/dev/null || true

if [ -s "$TMPFILE" ]; then
  eval "$(python3 -c "
import re, json

raw = open('$TMPFILE').read()

# Extract simple string fields via regex (tolerant of malformed JSON)
fields = {
    'FIREBASE_PROJECT_ID': 'project_id',
    'FIREBASE_APIKEY': 'api_key',
    'FIREBASE_API_KEY': 'api_key',
    'FIREBASE_AUTHDOMAIN': 'auth_domain',
    'FIREBASE_STORAGEBUCKET': 'storage_bucket',
    'FIREBASE_MESSAGINGSENDERID': 'messaging_sender_id',
    'FIREBASE_APP_ID': 'app_id',
}
for env_var, key in fields.items():
    m = re.search(r'\"' + key + r'\"\s*:\s*\"([^\"]*?)\"', raw)
    if m and m.group(1):
        print(f'export {env_var}=\"{m.group(1)}\"')

# Try to extract client_email and private_key from service_account_json
sa_match = re.search(r'\"service_account_json\"\s*:\s*[\"\\']+(\\{.+?\\})[\"\\']', raw, re.DOTALL)
if sa_match:
    try:
        sa = json.loads(sa_match.group(1))
        ce = sa.get('client_email', '')
        if ce:
            print(f'export FIREBASE_CLIENT_EMAIL=\"{ce}\"')
        pk = sa.get('private_key', '')
        if pk:
            escaped = pk.replace('\\\\', '\\\\\\\\').replace('\"', '\\\\\"')
            print(f'export FIREBASE_PRIVATE_KEY=\"{escaped}\"')
    except Exception:
        pass
else:
    # Fallback: top-level client_email/private_key
    for env_var, key in [('FIREBASE_CLIENT_EMAIL', 'client_email')]:
        m = re.search(r'\"' + key + r'\"\s*:\s*\"([^\"]*?)\"', raw)
        if m and m.group(1):
            print(f'export {env_var}=\"{m.group(1)}\"')
" 2>/dev/null)" || true
fi

aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/auth-secrets" \
  --query 'SecretString' --output text > "$TMPFILE" 2>/dev/null || true

if [ -s "$TMPFILE" ]; then
  eval "$(python3 -c "
import json
d = json.load(open('$TMPFILE'))
for env_var, key in [('GLOBAL_SECRET','global_secret'),('JWT_SECRET','jwt_secret'),('SESSION_SECRET','session_secret')]:
    val = d.get(key, '')
    if val:
        print(f'export {env_var}=\"{val}\"')
" 2>/dev/null)" || true
fi

# VAPID keys (needed by copilot-server for web push notifications)
aws secretsmanager get-secret-value \
  --secret-id "${SM_PREFIX}/vapid-keys" \
  --query 'SecretString' --output text > "$TMPFILE" 2>/dev/null || true

if [ -s "$TMPFILE" ]; then
  export VAPID_PUBLIC_KEY=$(python3 -c "import json; d=json.load(open('$TMPFILE')); print(d['public_key'])")
  export VAPID_PRIVATE_KEY=$(python3 -c "import json; d=json.load(open('$TMPFILE')); print(d['private_key'])")
fi

# Ensure MongoDB URI includes database name (default: tiledesk)
if [ -n "${MONGODB_URI:-}" ]; then
  # Append /tiledesk if URI has no database path
  if ! echo "$MONGODB_URI" | grep -qE '\.net/.+'; then
    export MONGODB_URI="${MONGODB_URI}/tiledesk"
  fi
fi

# Set aliases used by different services
export DATABASE_URI="${MONGODB_URI:-}"
export MONGO_URL="${MONGODB_URI:-}"
export MONGO_URI="${MONGODB_URI:-}"
export VOICE_SERVICE_URL="${VOICE_SERVICE_URL:-http://localhost:9192}"

cd "$WORKSPACE"

# Inject Firebase config into copilot-dashboard's dashboard-config.json
# This matches what EC2 does via envsubst on the template at container startup.
DASHBOARD_CONFIG="$WORKSPACE/copilot-dashboard/src/dashboard-config.json"
PATCHED_DASHBOARD=false
if [ -f "$DASHBOARD_CONFIG" ] && [ -n "${FIREBASE_API_KEY:-}" ]; then
  cp "$DASHBOARD_CONFIG" "$DASHBOARD_CONFIG.bak"
  PATCHED_DASHBOARD=true
  python3 -c "
import json
with open('$DASHBOARD_CONFIG') as f:
    config = json.load(f)
import os
config['firebaseConfig'] = {
    'apiKey': os.environ.get('FIREBASE_API_KEY', ''),
    'authDomain': os.environ.get('FIREBASE_AUTHDOMAIN', ''),
    'projectId': os.environ.get('FIREBASE_PROJECT_ID', ''),
    'storageBucket': os.environ.get('FIREBASE_STORAGEBUCKET', ''),
    'messagingSenderId': os.environ.get('FIREBASE_MESSAGINGSENDERID', ''),
    'appId': os.environ.get('FIREBASE_APP_ID', ''),
}
vpk = os.environ.get('VAPID_PUBLIC_KEY', '')
if vpk:
    config['vapidPublicKey'] = vpk
with open('$DASHBOARD_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
" 2>/dev/null || true
  echo "Injected Firebase config into dashboard-config.json" >&2
fi

# Write env vars to a temp .env file so local-dev.sh can source it
ENVFILE="$WORKSPACE/.env.${ENV}"
CREATED_ENVFILE=false
if [ ! -f "$ENVFILE" ]; then
  CREATED_ENVFILE=true
  # Write non-multiline vars via env grep
  env | grep -E '^(MONGODB_URI|DATABASE_URI|MONGO_URL|MONGO_URI|CACHE_REDIS_URL|REDIS_URL|REDIS_HOST|REDIS_PORT|REDIS_PASSWORD|RABBITMQ_CONNECT_URL|CLOUDAMQP_URL|OPENAI_API_KEY|ANTHROPIC_API_KEY|PINECONE_API_KEY|LANGSMITH_API_KEY|LIVEKIT_|VOICE_SERVICE_URL|AWS_|FIREBASE_PROJECT_ID|FIREBASE_APIKEY|FIREBASE_API_KEY|FIREBASE_AUTHDOMAIN|FIREBASE_STORAGEBUCKET|FIREBASE_MESSAGINGSENDERID|FIREBASE_APP_ID|FIREBASE_CLIENT_EMAIL|GLOBAL_SECRET|JWT_SECRET|SESSION_SECRET|VAPID_)=' > "$ENVFILE"
  # Write private key separately (may contain newlines)
  if [ -n "${FIREBASE_PRIVATE_KEY:-}" ]; then
    printf 'FIREBASE_PRIVATE_KEY=%s\n' "$FIREBASE_PRIVATE_KEY" >> "$ENVFILE"
  fi
fi

# Cleanup on exit: restore dashboard-config.json and remove temp files
cleanup() {
  if $PATCHED_DASHBOARD && [ -f "$DASHBOARD_CONFIG.bak" ]; then
    mv "$DASHBOARD_CONFIG.bak" "$DASHBOARD_CONFIG"
    echo "Restored original dashboard-config.json" >&2
  fi
  rm -f "$TMPFILE"
  if $CREATED_ENVFILE; then rm -f "$ENVFILE"; fi
}
trap cleanup EXIT

exec /opt/homebrew/bin/bash ./local-dev.sh "$@"
