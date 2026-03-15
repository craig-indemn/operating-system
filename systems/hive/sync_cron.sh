#!/usr/bin/env bash
# sync_cron.sh — Run a single Hive sync adapter with logging.
# Called by crontab entries. Each adapter failure is isolated.
#
# Usage: sync_cron.sh <adapter>
# Example: sync_cron.sh linear
set -uo pipefail

ADAPTER="${1:?Usage: sync_cron.sh <adapter>}"
HIVE_CLI="/Users/home/Repositories/.venv/bin/python3 /Users/home/Repositories/operating-system/systems/hive/cli.py"
LOG_DIR="/Users/home/Repositories/operating-system/.logs"
LOG_FILE="$LOG_DIR/hive-sync.log"

mkdir -p "$LOG_DIR"

# Add secrets-proxy to PATH for adapter CLIs
export PATH="/Users/home/Repositories/operating-system/scripts/secrets-proxy:$PATH"

# Source 1Password service account token if available
ENV_FILE="/Users/home/Repositories/operating-system/.env"
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
fi

TS=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TS] sync $ADAPTER: starting" >> "$LOG_FILE"

OUTPUT=$($HIVE_CLI sync "$ADAPTER" 2>&1)
EXIT_CODE=$?

TS=$(date '+%Y-%m-%d %H:%M:%S')
if [ $EXIT_CODE -eq 0 ]; then
    # Extract stats from JSON output (last line)
    STATS=$(echo "$OUTPUT" | tail -1)
    echo "[$TS] sync $ADAPTER: OK — $STATS" >> "$LOG_FILE"
else
    echo "[$TS] sync $ADAPTER: FAILED (exit $EXIT_CODE) — $OUTPUT" >> "$LOG_FILE"
fi
