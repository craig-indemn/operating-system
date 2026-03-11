#!/usr/bin/env bash
set -euo pipefail

# mongosh-connect.sh [dev|prod] [database] [mongosh flags...]
# Connects to MongoDB Atlas via AWS Secrets Manager — credentials never exposed.

ENV="${1:-dev}"; shift 2>/dev/null || true
DB="${1:-tiledesk}"; shift 2>/dev/null || true

URI=$(aws secretsmanager get-secret-value \
  --secret-id "indemn/${ENV}/shared/mongodb-uri" \
  --query 'SecretString' --output text 2>/dev/null) || {
  echo "ERROR: Failed to read ${ENV}/shared/mongodb-uri from AWS Secrets Manager" >&2
  echo "Check: aws sts get-caller-identity" >&2
  exit 1
}

exec mongosh "${URI}/${DB}" --quiet "$@"
