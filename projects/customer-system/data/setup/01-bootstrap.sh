#!/bin/bash
# =============================================================================
# Step 1: Bootstrap the Organization
# =============================================================================
# The _platform org already exists with craig@indemn.ai as admin.
# This step is documented for completeness — the bootstrap was performed
# during initial OS setup and does not need to be re-run.
#
# Original bootstrap command (already executed):
#   indemn platform init --first-admin craig@indemn.ai --org-name "Indemn"
#
# To verify the org exists:
#   indemn org list
# =============================================================================

echo "Checking if org already exists..."
if indemn org list 2>/dev/null | grep -q "Indemn"; then
  echo "Org 'Indemn' already exists. Skipping bootstrap."
else
  echo "Org not found. Running bootstrap..."
  indemn platform init --first-admin craig@indemn.ai --org-name "Indemn"
fi
