#!/usr/bin/env bash
set -euo pipefail

# mongosh-connect.sh [dev|prod] [database] [mongosh flags...]
# Connects to MongoDB Atlas via AWS Secrets Manager — credentials never exposed.
#
# The shared secret stores the private-link SRV host (e.g. `dev-indemn-pl-0`)
# which resolves only inside AWS VPCs where indemn-api / indemn-queue-processor
# / indemn-runtime-* run. From a local laptop, that hostname returns NXDOMAIN.
# Swap it inline to the public-facing equivalent (`dev-indemn`) which both
# Atlas hostnames are aliases for.
#
# DO NOT "fix" this by writing the public host back to the shared secret —
# the platform NEEDS the private-link host. Bug #12 history: Sessions 15+16
# both did that thinking the secret was regressed; the deploy auto-restore
# correctly put the private-link value back, breaking nobody but us. The
# secret is correct; this script is the place that needs the swap. See
# `os-learnings.md § Bug #12 (REFRAME)`.

ENV="${1:-dev}"; shift 2>/dev/null || true
DB="${1:-tiledesk}"; shift 2>/dev/null || true

URI=$(aws secretsmanager get-secret-value \
  --secret-id "indemn/${ENV}/shared/mongodb-uri" \
  --query 'SecretString' --output text 2>/dev/null) || {
  echo "ERROR: Failed to read ${ENV}/shared/mongodb-uri from AWS Secrets Manager" >&2
  echo "Check: aws sts get-caller-identity" >&2
  exit 1
}

# Private-link → public host swap for local DNS resolution.
# Pattern matches `dev-indemn-pl-0` and `prod-indemn-pl-0` host aliases.
LOCAL_URI="${URI/-pl-0/}"

exec mongosh "${LOCAL_URI}/${DB}" --quiet "$@"
