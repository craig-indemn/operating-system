#!/bin/bash
# =============================================================================
# Step 1: Bootstrap the Organization
# =============================================================================
# Creates the Indemn organization and the first admin actor.
# This is the very first thing that runs on a fresh OS instance.
#
# The first-admin flag prints a one-time magic link token to stdout
# (no email Integration exists yet). Craig uses it to complete setup.
# =============================================================================

indemn platform init --first-admin craig@indemn.ai --org-name "Indemn"
