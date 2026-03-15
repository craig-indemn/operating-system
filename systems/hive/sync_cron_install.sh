#!/usr/bin/env bash
# sync_cron_install.sh — Install or remove Hive sync cron jobs.
#
# Usage:
#   sync_cron_install.sh install   # Add cron entries
#   sync_cron_install.sh remove    # Remove cron entries
#   sync_cron_install.sh status    # Show current cron entries
set -euo pipefail

SYNC_SCRIPT="/Users/home/Repositories/operating-system/systems/hive/sync_cron.sh"
MARKER="# hive-sync"

case "${1:-status}" in
    install)
        # Remove existing hive-sync entries, then add new ones
        { crontab -l 2>/dev/null || true; } | { grep -v "$MARKER" || true; } | cat - <<EOF | crontab -
*/5 * * * * $SYNC_SCRIPT calendar $MARKER
*/10 * * * * $SYNC_SCRIPT slack $MARKER
*/15 * * * * $SYNC_SCRIPT linear $MARKER
*/15 * * * * $SYNC_SCRIPT github $MARKER
EOF
        echo "Installed hive sync cron jobs:"
        crontab -l | grep "$MARKER"
        ;;
    remove)
        { crontab -l 2>/dev/null || true; } | { grep -v "$MARKER" || true; } | crontab -
        echo "Removed all hive sync cron jobs"
        ;;
    status)
        echo "Current hive sync cron jobs:"
        crontab -l 2>/dev/null | grep "$MARKER" || echo "  (none installed)"
        ;;
    *)
        echo "Usage: $0 {install|remove|status}" >&2
        exit 1
        ;;
esac
