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

echo "Pulling secrets from AWS (${ENV}/shared/*)..." >&2

# Shared infrastructure secrets from AWS Secrets Manager
export MONGODB_URI=$(aws secretsmanager get-secret-value \
  --secret-id "${ENV}/shared/mongodb-uri" \
  --query 'SecretString' --output text 2>/dev/null) || true

export REDIS_URL=$(aws secretsmanager get-secret-value \
  --secret-id "${ENV}/shared/redis-url" \
  --query 'SecretString' --output text 2>/dev/null) || true

export RABBITMQ_URL=$(aws secretsmanager get-secret-value \
  --secret-id "${ENV}/shared/rabbitmq-url" \
  --query 'SecretString' --output text 2>/dev/null) || true

export OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "${ENV}/shared/openai-api-key" \
  --query 'SecretString' --output text 2>/dev/null) || true

export ANTHROPIC_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "${ENV}/shared/anthropic-api-key" \
  --query 'SecretString' --output text 2>/dev/null) || true

export PINECONE_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "${ENV}/shared/pinecone-api-key" \
  --query 'SecretString' --output text 2>/dev/null) || true

# Non-secret config
export AWS_ACCOUNT_ID="780354157690"
export AWS_DEFAULT_REGION="us-east-1"

# Find workspace directory
WORKSPACE="${INDEMN_WORKSPACE:-$(dirname "$(find ~/Repositories ~/code ~/dev ~/Projects -name 'local-dev.sh' -maxdepth 1 2>/dev/null | head -1)" 2>/dev/null)}"

if [ -z "$WORKSPACE" ] || [ ! -f "$WORKSPACE/local-dev.sh" ]; then
  echo "ERROR: Could not find local-dev.sh. Set INDEMN_WORKSPACE env var." >&2
  exit 1
fi

# Create empty env file so local-dev.sh doesn't complain
TMPENV=$(mktemp)
trap "rm -f $TMPENV" EXIT

cd "$WORKSPACE"
exec /opt/homebrew/bin/bash ./local-dev.sh "$@"
