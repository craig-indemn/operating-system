#!/bin/bash
# =============================================================================
# Populate SM Secrets from EC2 .env Files
# =============================================================================
# Run ON the dev EC2 instance (i-0fde0af9d216e9182).
# Reads values from /opt/{service}/.env and writes directly to AWS SM.
# No secrets are printed — only OK/SKIP/FAIL status per secret.
#
# Usage:
#   bash populate-sm-secrets.sh          # dry-run (shows what would happen)
#   bash populate-sm-secrets.sh --apply  # actually write to SM
# =============================================================================

set -euo pipefail

REGION="us-east-1"
DRY_RUN=true
[ "${1:-}" = "--apply" ] && DRY_RUN=false

if $DRY_RUN; then
  echo "=== DRY RUN — pass --apply to actually write secrets ==="
  echo ""
fi

# ---- helpers ----------------------------------------------------------------

get_val() {
  # Reads KEY=VALUE from a file. Handles values with = in them.
  # Strips one layer of surrounding single or double quotes.
  local file="$1" key="$2"
  [ -f "$file" ] || return 0
  local line
  line=$(grep -m1 "^${key}=" "$file" 2>/dev/null) || return 0
  local val="${line#*=}"
  # Strip one layer of surrounding quotes — check which quote type wraps it
  case "$val" in
    \"*\") val="${val#\"}"; val="${val%\"}" ;;
    \'*\') val="${val#\'}"; val="${val%\'}" ;;
  esac
  printf '%s' "$val"
}

get_val_multi() {
  # Try multiple files for the same key, return first match
  local key="$1"
  shift
  for file in "$@"; do
    local v
    v=$(get_val "$file" "$key")
    if [ -n "$v" ]; then
      printf '%s' "$v"
      return
    fi
  done
}

put_secret_json() {
  # Build JSON from key=value pairs using python3 (handles all escaping)
  # Usage: put_secret_json "path" "json_key1" "value1" "json_key2" "value2" ...
  local path="$1"
  shift

  # Write args to a temp file to avoid shell argument length/escaping issues
  local tmpargs
  tmpargs=$(mktemp)
  while [ $# -ge 2 ]; do
    printf '%s\n' "$1"
    printf '%s\n' "$2"
    shift 2
  done > "$tmpargs"

  local tmpjson
  tmpjson=$(mktemp)
  local rc=0
  python3 -c "
import json, sys

lines = open(sys.argv[1]).read().splitlines()
d = {}
for i in range(0, len(lines), 2):
    key = lines[i]
    val = lines[i+1] if i+1 < len(lines) else ''
    if val:  # skip empty values
        d[key] = val
if not d:
    sys.exit(1)
with open(sys.argv[2], 'w') as f:
    json.dump(d, f, ensure_ascii=False)
print(len(d))
" "$tmpargs" "$tmpjson" 2>/dev/null || rc=$?
  rm -f "$tmpargs"

  if [ $rc -ne 0 ] || [ ! -s "$tmpjson" ]; then
    echo "SKIP: $path — no values found"
    rm -f "$tmpjson"
    return
  fi

  local key_count
  key_count=$(cat "$tmpjson" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

  if $DRY_RUN; then
    echo "DRY:  $path — ${key_count} keys"
  else
    aws secretsmanager put-secret-value \
      --secret-id "indemn/dev/${path}" \
      --secret-string "file://${tmpjson}" \
      --region "$REGION" >/dev/null 2>&1 \
      && echo "OK:   $path (${key_count} keys)" \
      || echo "FAIL: $path"
  fi
  rm -f "$tmpjson"
}

put_secret_plain() {
  # For plain string secrets (not JSON)
  local path="$1" value="$2"

  if [ -z "$value" ]; then
    echo "SKIP: $path — no value found"
    return
  fi

  if $DRY_RUN; then
    echo "DRY:  $path — plain string (${#value} chars)"
  else
    local tmpval
    tmpval=$(mktemp)
    printf '%s' "$value" > "$tmpval"
    aws secretsmanager put-secret-value \
      --secret-id "indemn/dev/${path}" \
      --secret-string "file://${tmpval}" \
      --region "$REGION" >/dev/null 2>&1 \
      && echo "OK:   $path" \
      || echo "FAIL: $path"
    rm -f "$tmpval"
  fi
}

put_secret_raw_json() {
  # For values that are already JSON blobs (e.g. GOOGLE_AUTH_CREDEINTIALS)
  local path="$1" value="$2"

  if [ -z "$value" ]; then
    echo "SKIP: $path — no value found"
    return
  fi

  # Validate it's actual JSON
  if ! printf '%s' "$value" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    echo "SKIP: $path — value is not valid JSON"
    return
  fi

  if $DRY_RUN; then
    local key_count
    key_count=$(printf '%s' "$value" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,dict) else 'array')")
    echo "DRY:  $path — raw JSON (${key_count} keys)"
  else
    local tmpval
    tmpval=$(mktemp)
    printf '%s' "$value" > "$tmpval"
    aws secretsmanager put-secret-value \
      --secret-id "indemn/dev/${path}" \
      --secret-string "file://${tmpval}" \
      --region "$REGION" >/dev/null 2>&1 \
      && echo "OK:   $path" \
      || echo "FAIL: $path"
    rm -f "$tmpval"
  fi
}

# ---- env file paths ---------------------------------------------------------

TILEDESK="/opt/tiledesk/.env"
BOT="/opt/bot-service/.env"
PAYMENT="/opt/payment-service/.env"
VOICE="/opt/voice-service/.env"
MIDDLEWARE="/opt/middleware-service/.env"
KB="/opt/openai-fastapi/.env"
UTILITY="/opt/utility-service/.env"
OPS="/opt/operations_api/.env"
EMAIL="/opt/email-channel-service/.env"

# ---- shared secrets ---------------------------------------------------------

echo "=== SHARED SECRETS ==="

put_secret_json "shared/stripe-keys" \
  "secret_key"             "$(get_val_multi STRIPE_SECRET_KEY "$PAYMENT" "$TILEDESK")" \
  "publishable_key"        "$(get_val_multi STRIPE_PUBLISHABLE_KEY "$PAYMENT" "$TILEDESK")" \
  "webhook_secret"         "$(get_val_multi STRIPE_WEBHOOK_SECRET "$PAYMENT" "$TILEDESK")" \
  "connect_webhook_secret" "$(get_val_multi STRIPE_CONNECT_WEBHOOK_SECRET "$PAYMENT" "$TILEDESK")"

put_secret_json "shared/firebase-credentials" \
  "project_id"          "$(get_val "$TILEDESK" FIREBASE_PROJECT_ID)" \
  "client_email"        "$(get_val "$TILEDESK" FIREBASE_CLIENT_EMAIL)" \
  "private_key"         "$(get_val "$TILEDESK" FIREBASE_PRIVATE_KEY)" \
  "api_key"             "$(get_val "$TILEDESK" FIREBASE_API_KEY)" \
  "auth_domain"         "$(get_val "$TILEDESK" FIREBASE_AUTH_DOMAIN)" \
  "database_url"        "$(get_val "$TILEDESK" FIREBASE_DATABASE_URL)" \
  "storage_bucket"      "$(get_val "$TILEDESK" FIREBASE_STORAGE_BUCKET)" \
  "messaging_sender_id" "$(get_val "$TILEDESK" FIREBASE_MESSAGING_SENDER_ID)" \
  "app_id"              "$(get_val "$TILEDESK" FIREBASE_APP_ID)" \
  "service_account_json" "$(get_val "$TILEDESK" FIREBASE_SERVICE_ACCOUNT_JSON)"

put_secret_plain "shared/sendgrid-api-key" \
  "$(get_val "$TILEDESK" SENDGRID_API_KEY)"

put_secret_json "shared/twilio-credentials" \
  "account_sid" "$(get_val_multi TWILIO_ACCOUNT_SID "$VOICE" "$MIDDLEWARE")" \
  "auth_token"  "$(get_val_multi TWILIO_AUTH_TOKEN "$VOICE" "$MIDDLEWARE")"

put_secret_json "shared/google-oauth" \
  "client_id"     "$(get_val "$TILEDESK" GOOGLE_CLIENT_ID)" \
  "client_secret" "$(get_val "$TILEDESK" GOOGLE_CLIENT_SECRET)" \
  "callback_url"  "$(get_val "$TILEDESK" GOOGLE_CALLBACK_URL)"

put_secret_plain "shared/groq-api-key" \
  "$(get_val "$BOT" GROQ_API_KEY)"

put_secret_plain "shared/bland-api-key" \
  "$(get_val "$MIDDLEWARE" BLAND_API_KEY)"

put_secret_plain "shared/airtable-api-key" \
  "$(get_val_multi AIRTABLE_API_KEY "$UTILITY" "$OPS" "$TILEDESK")"

put_secret_json "shared/google-cloud-sa" \
  "project_id"    "$(get_val "$VOICE" GOOGLE_PROJECT_ID)" \
  "client_email"  "$(get_val "$VOICE" GOOGLE_CLIENT_EMAIL)" \
  "private_key"   "$(get_val "$VOICE" GOOGLE_PRIVATE_KEY)"

put_secret_json "shared/service-tokens" \
  "system_user_token"          "$(get_val_multi SYSTEM_USER_TOKEN "$TILEDESK" "$MIDDLEWARE")" \
  "apps_access_token"          "$(get_val_multi APPS_ACCESS_TOKEN "$TILEDESK" "$MIDDLEWARE")" \
  "conversation_service_token" "$(get_val_multi CONVERSATION_SERVICE_TOKEN "$TILEDESK" "$MIDDLEWARE")"

put_secret_json "shared/copilot-api-credentials" \
  "username" "$(get_val_multi COPILOT_API_USERNAME "$KB" "$OPS" "$MIDDLEWARE")" \
  "password" "$(get_val_multi COPILOT_API_PASSWORD "$KB" "$OPS" "$MIDDLEWARE")" \
  "api_key"  "$(get_val_multi COPILOT_API_KEY "$KB" "$OPS" "$MIDDLEWARE")"

# ---- service-specific secrets -----------------------------------------------

echo ""
echo "=== SERVICE-SPECIFIC SECRETS ==="

put_secret_json "services/middleware/aws-s3-credentials" \
  "access_key_id"     "$(get_val "$MIDDLEWARE" AWS_ACCESS_KEY_ID)" \
  "secret_access_key" "$(get_val "$MIDDLEWARE" AWS_SECRET_ACCESS_KEY)" \
  "bucket_name"       "$(get_val "$MIDDLEWARE" S3_BUCKET_NAME)" \
  "private_bucket_name" "$(get_val "$MIDDLEWARE" PRIVATE_S3_BUCKET_NAME)"

# Carrier credentials — dynamic, many fields per carrier
CARRIER_TMP=$(mktemp)
if python3 -c "
import json, sys
carriers = {}
try:
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip('\"').strip(\"'\")
            prefix = key.split('_')[0]
            if prefix in ('MARKEL', 'CMF', 'GIC', 'BONZAH', 'INSURICA', 'SALESFORCE'):
                carriers[key.lower()] = val
except FileNotFoundError:
    pass
if carriers:
    with open(sys.argv[2], 'w') as out:
        json.dump(carriers, out, ensure_ascii=False)
    print(len(carriers))
else:
    sys.exit(1)
" "$OPS" "$CARRIER_TMP" 2>/dev/null; then
  CARRIER_COUNT=$(python3 -c "import sys,json; print(len(json.load(open(sys.argv[1]))))" "$CARRIER_TMP")
  if $DRY_RUN; then
    echo "DRY:  services/operations-api/carrier-credentials — ${CARRIER_COUNT} keys"
  else
    aws secretsmanager put-secret-value \
      --secret-id "indemn/dev/services/operations-api/carrier-credentials" \
      --secret-string "file://${CARRIER_TMP}" \
      --region "$REGION" >/dev/null 2>&1 \
      && echo "OK:   services/operations-api/carrier-credentials (${CARRIER_COUNT} keys)" \
      || echo "FAIL: services/operations-api/carrier-credentials"
  fi
else
  echo "SKIP: services/operations-api/carrier-credentials — no values found"
fi
rm -f "$CARRIER_TMP"

put_secret_json "services/copilot-server/chat21-credentials" \
  "admin_token" "$(get_val "$TILEDESK" CHAT21_ADMIN_TOKEN)" \
  "jwt_secret"  "$(get_val "$TILEDESK" CHAT21_JWT_SECRET)"

put_secret_json "services/copilot-server/admin-credentials" \
  "super_password"           "$(get_val "$TILEDESK" SUPER_PASSWORD)" \
  "admin_password"           "$(get_val "$TILEDESK" ADMIN_PASSWORD)" \
  "apps_access_token_secret" "$(get_val "$TILEDESK" APPS_ACCESS_TOKEN_SECRET)"

put_secret_plain "services/operations-api/mixpanel-token" \
  "$(get_val "$OPS" MIXPANEL_TOKEN)"

# Google auth credentials — already a JSON blob, pass through as-is
# Use python3 to read from the file directly to avoid shell mangling the JSON
GA_TMP=$(mktemp)
if python3 -c "
import sys, json
env_file = sys.argv[1]
key = 'GOOGLE_AUTH_CREDEINTIALS'
try:
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith(key + '='):
                val = line[len(key)+1:]
                # Strip surrounding quotes
                if (val.startswith('\"') and val.endswith('\"')) or \
                   (val.startswith(\"'\") and val.endswith(\"'\")):
                    val = val[1:-1]
                # Validate it's JSON
                parsed = json.loads(val)
                with open(sys.argv[2], 'w') as out:
                    json.dump(parsed, out, ensure_ascii=False)
                print(len(parsed) if isinstance(parsed, dict) else 'array')
                sys.exit(0)
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    print(f'error: {e}', file=sys.stderr)
    sys.exit(1)
sys.exit(1)
" "$EMAIL" "$GA_TMP" 2>/dev/null; then
  GA_COUNT=$(python3 -c "import sys,json; print(len(json.load(open(sys.argv[1]))))" "$GA_TMP")
  if $DRY_RUN; then
    echo "DRY:  services/email-channel/google-auth-credentials — raw JSON (${GA_COUNT} keys)"
  else
    aws secretsmanager put-secret-value \
      --secret-id "indemn/dev/services/email-channel/google-auth-credentials" \
      --secret-string "file://${GA_TMP}" \
      --region "$REGION" >/dev/null 2>&1 \
      && echo "OK:   services/email-channel/google-auth-credentials" \
      || echo "FAIL: services/email-channel/google-auth-credentials"
  fi
else
  echo "SKIP: services/email-channel/google-auth-credentials — no value or invalid JSON"
fi
rm -f "$GA_TMP"

echo ""
echo "=== Done ==="
if $DRY_RUN; then
  echo "This was a dry run. Run with --apply to write to SM."
fi
