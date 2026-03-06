#!/usr/bin/env bash
# =============================================================================
# AWS Environment Loader — Template
# =============================================================================
# Pulls secrets from AWS Secrets Manager and config from Parameter Store,
# writes them to an env file that docker-compose can consume.
#
# Runs on the HOST (not inside containers) — uses the EC2 instance profile
# for AWS auth. No AWS CLI needed in the container image.
#
# Usage:
#   AWS_ENV=dev AWS_SERVICE={service-name} bash scripts/aws-env-loader.sh .env.aws
#
# Required:
#   AWS_ENV          - Environment name (dev/prod)
#   $1               - Output file path (default: .env.aws)
#
# Optional:
#   AWS_SERVICE      - Service name for service-specific secrets
#   AWS_REGION       - AWS region (default: us-east-1)
#
# =============================================================================
# HOW TO CUSTOMIZE:
#   1. Copy this file to your repo as scripts/aws-env-loader.sh
#   2. Set AWS_SERVICE default to your service name (line marked CUSTOMIZE)
#   3. Add service-specific load_secret calls in the SERVICE-SPECIFIC section
#   4. Update the PARAM_MAP dict with your service's parameter mappings
# =============================================================================

set -euo pipefail

# Ensure aws CLI is on PATH (common install locations on EC2)
for p in /usr/local/bin /usr/bin /snap/bin; do
  [ -x "$p/aws" ] && { export PATH="$p:$PATH"; break; }
done
command -v aws >/dev/null 2>&1 || { echo "ERROR: aws CLI not found" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found" >&2; exit 1; }

AWS_ENV="${AWS_ENV:?ERROR: AWS_ENV must be set (dev/prod)}"
# [CUSTOMIZE] Change this default to your service name
AWS_SERVICE="${AWS_SERVICE:-CHANGEME}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ENV_FILE="${1:-.env.aws}"

log() { echo "[aws-env-loader] $*" >&2; }

# Start with empty env file
> "$ENV_FILE"

# Write a var to the env file
write_var() {
  local name="$1" value="$2"
  echo "${name}=${value}" >> "$ENV_FILE"
  log "  ${name}"
}

# ---------------------------------------------------------------------------
# Fetch a single secret string from Secrets Manager
# ---------------------------------------------------------------------------
get_secret() {
  local secret_id="$1"
  aws secretsmanager get-secret-value \
    --secret-id "$secret_id" \
    --region "$AWS_REGION" \
    --query 'SecretString' \
    --output text 2>/dev/null
}

# ---------------------------------------------------------------------------
# Fetch all parameters under a path from Parameter Store
# ---------------------------------------------------------------------------
get_parameters_by_path() {
  local path="$1"
  aws ssm get-parameters-by-path \
    --path "$path" \
    --region "$AWS_REGION" \
    --recursive \
    --query 'Parameters[].{Name:Name,Value:Value}' \
    --output json 2>/dev/null || echo "[]"
}

# ---------------------------------------------------------------------------
# Export a secret as one or more env vars
# $1 = secret ID in Secrets Manager (relative to indemn/{env}/)
# $2+ = env var mappings: "ENV_VAR_NAME" for plain strings,
#        "ENV_VAR_NAME=json_key" for JSON fields
# ---------------------------------------------------------------------------
load_secret() {
  local secret_id="$1"
  shift

  local value
  value=$(get_secret "indemn/${AWS_ENV}/${secret_id}")
  if [ -z "$value" ]; then
    log "WARN: Secret indemn/${AWS_ENV}/${secret_id} not found, skipping"
    return
  fi

  for mapping in "$@"; do
    if [[ "$mapping" == *"="* ]]; then
      # JSON field extraction: ENV_VAR=json_key
      local var_name="${mapping%%=*}"
      local json_key="${mapping#*=}"
      local field_value
      field_value=$(echo "$value" | python3 -c "import sys,json; print(json.load(sys.stdin)['${json_key}'])" 2>/dev/null)
      if [ -n "$field_value" ]; then
        write_var "$var_name" "$field_value"
      fi
    else
      # Plain string: ENV_VAR
      write_var "$mapping" "$value"
    fi
  done
}

# ===========================================================================
# [COPY AS-IS] Shared Secrets — identical across all services
# ===========================================================================
log "Loading secrets for env=${AWS_ENV}, service=${AWS_SERVICE} → ${ENV_FILE}"
log "Loading shared secrets..."

load_secret "shared/mongodb-uri" \
  "MONGODB_URI" "MONGO_URL" "MONGO_URI" "DATABASE_URI"

load_secret "shared/redis-credentials" \
  "REDIS_HOST=host" "REDIS_PORT=port" "REDIS_USERNAME=username" \
  "REDIS_PASSWORD=password" "REDIS_URL=url" "CACHE_REDIS_URL=url"

load_secret "shared/rabbitmq-url" \
  "RABBITMQ_CONNECT_URL" "CLOUDAMQP_URL"

load_secret "shared/openai-api-key" \
  "OPENAI_API_KEY"

load_secret "shared/anthropic-api-key" \
  "ANTHROPIC_API_KEY"

load_secret "shared/google-api-key" \
  "GOOGLE_API_KEY"

load_secret "shared/cohere-api-key" \
  "COHERE_API_KEY"

load_secret "shared/langsmith-api-key" \
  "LANGSMITH_API_KEY" "LANGCHAIN_API_KEY"

load_secret "shared/langfuse-keys" \
  "LANGFUSE_PUBLIC_KEY=public_key" "LANGFUSE_SECRET_KEY=secret_key"

load_secret "shared/pinecone-api-key" \
  "PINECONE_API_KEY"

load_secret "shared/voice-api-keys" \
  "ELEVENLABS_API_KEY=elevenlabs" "DEEPGRAM_API_KEY=deepgram" "CARTESIA_API_KEY=cartesia"

load_secret "shared/livekit-credentials" \
  "LIVEKIT_API_KEY=api_key" "LIVEKIT_API_SECRET=api_secret" "LIVEKIT_URL=url"

load_secret "shared/slack-webhook-url" \
  "SLACK_WEBHOOK_URL"

load_secret "shared/auth-secrets" \
  "GLOBAL_SECRET=global_secret" "JWT_SECRET=jwt_secret" "SESSION_SECRET=session_secret"

load_secret "shared/support-email" \
  "SUPPORT_EMAIL_USERNAME=username" "SUPPORT_EMAIL_PASSWORD=password"

load_secret "shared/vapid-keys" \
  "VAPID_PUBLIC_KEY=public_key" "VAPID_PRIVATE_KEY=private_key"

# ===========================================================================
# [CUSTOMIZE] Service-Specific Secrets
# ===========================================================================
# Add load_secret calls for secrets unique to this service.
# Use paths like: "services/{service-name}/{secret-name}"
#
# Examples:
#   load_secret "services/bot-service/groq-api-key" "GROQ_API_KEY"
#   load_secret "services/copilot-server/stripe-keys" \
#     "STRIPE_SECRET_KEY=secret_key" "STRIPE_PUBLISHABLE_KEY=publishable_key"
#
log "Loading ${AWS_SERVICE} secrets..."

# [ADD SERVICE-SPECIFIC load_secret CALLS HERE]

# ===========================================================================
# [COPY AS-IS] Parameter Store Loading
# ===========================================================================
log "Loading parameters from /indemn/${AWS_ENV}/..."

params_json=$(get_parameters_by_path "/indemn/${AWS_ENV}/")

if [ "$params_json" != "[]" ] && [ -n "$params_json" ]; then
  echo "$params_json" | python3 -c "
import sys, json

# ===========================================================================
# [CUSTOMIZE] PARAM_MAP — maps Parameter Store names to env var names
# ===========================================================================
# Keys: the last segment of the PS path (e.g., 'mongodb-db' from '/indemn/dev/shared/mongodb-db')
# Values: the env var name to write
#
# Start with the shared params (included below), then add service-specific ones.
# Only include params your service actually needs — unused params are harmless
# but add noise to the env file.
# ===========================================================================
PARAM_MAP = {
    # -- Shared params (most services need these) --
    'environment': 'ENVIRONMENT',
    'mongodb-db': 'MONGODB_DB',
    'mongodb-openai-db': 'MONGO_OPENAI_DB',
    'mongodb-airtable-db': 'MONGO_AIRTABLE_DB',
    'pinecone-environment': 'PINECONE_ENVIRONMENT',
    'pinecone-index-name': 'PINECONE_INDEX_NAME',
    'llm-provider': 'LLM_PROVIDER',
    'llm-model': 'LLM_MODEL',
    'llm-temperature': 'LLM_TEMPERATURE',
    'llm-max-tokens': 'LLM_MAX_TOKENS',
    'langchain-tracing-v2': 'LANGCHAIN_TRACING_V2',
    'langchain-project': 'LANGCHAIN_PROJECT',
    'langfuse-host': 'LANGFUSE_HOST',
    'sign-options-issuer': 'SIGN_OPTIONS_ISSUER',
    'indemn-domain': 'INDEMN_DOMAIN',
    'global-secret-algorithm': 'GLOBAL_SECRET_ALGORITHM',
    'bot-engine-prompt-template': 'BOT_ENGINE_PROMPT_TEMPLATE',
    'bot-engine-voice-prompt-template': 'BOT_ENGINE_VOICE_PROMPT_TEMPLATE',
    'identify-next-step-enabled': 'IDENTIFY_NEXT_STEP_ENABLED',
    'bot-service-url': 'BOT_SERVICE_URL',
    'copilot-server-url': 'CO_PILOT_URL',
    'middleware-url': 'MIDDLEWARE_URL',
    'sync-service-url': 'SYNC_SERVICE_URL',
    'kb-service-url': 'VECTOR_DB_SYNC_API_URL',
    'conversation-service-url': 'CONVERSATION_URL',
    'platform-url': 'PLATFORM_URL',
    'evaluation-service-url': 'EVALUATION_SERVICE_URL',
    'payment-url': 'PAYMENT_URL',
    'voice-service-url': 'VOICE_SERVICE_URL',

    # -- [ADD SERVICE-SPECIFIC PARAMS HERE] --
    # Example:
    # 'dd-service': 'DD_SERVICE',
    # 'dd-env': 'DD_ENV',
    # 'stripe-connect-client-id': 'STRIPE_CONNECT_CLIENT_ID',
}

params = json.load(sys.stdin)
aliases = {}

with open('${ENV_FILE}', 'a') as f:
    for p in params:
        param_name = p['Name'].rsplit('/', 1)[-1]
        env_var = PARAM_MAP.get(param_name)
        if env_var:
            f.write(f'{env_var}={p[\"Value\"]}\n')
            print(f'  {env_var}', file=sys.stderr)
            # Track values for aliases
            if env_var == 'LANGCHAIN_PROJECT':
                aliases['LANGSMITH_PROJECT_NAME'] = p['Value']
            if env_var == 'MONGODB_DB':
                aliases['MONGO_DB'] = p['Value']
                aliases['MONGO_DB_NAME'] = p['Value']

    # Write aliases
    for alias_var, alias_val in aliases.items():
        f.write(f'{alias_var}={alias_val}\n')
        print(f'  {alias_var} (alias)', file=sys.stderr)
"
  log "Loaded parameters from Parameter Store"
fi

var_count=$(wc -l < "$ENV_FILE" | tr -d ' ')
log "Done: ${var_count} vars written to ${ENV_FILE}"
