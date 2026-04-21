#!/bin/bash
# =============================================================================
# Step 3: Create Roles
# =============================================================================
# One role for now: team_member. Everyone gets it. Full read/write on
# everything. Watches and role differentiation (account_lead, executive)
# come later when we design automations.
#
# Syntax:
#   indemn role create --data '{"name": "...", "permissions": {...}}'
#   indemn actor add-role --email addr@indemn.ai --role role_name
# =============================================================================

indemn role create --data '{"name": "team_member", "permissions": {"read": ["*"], "write": ["*"]}}'

# Grant to everyone
indemn actor add-role --email craig@indemn.ai --role team_member
indemn actor add-role --email kyle@indemn.ai --role team_member
indemn actor add-role --email cam@indemn.ai --role team_member
indemn actor add-role --email dhruv@indemn.ai --role team_member
indemn actor add-role --email jonathan@indemn.ai --role team_member
indemn actor add-role --email rudra@indemn.ai --role team_member
indemn actor add-role --email peter@indemn.ai --role team_member
indemn actor add-role --email drew@indemn.ai --role team_member
indemn actor add-role --email george@indemn.ai --role team_member
indemn actor add-role --email ganesh@indemn.ai --role team_member
indemn actor add-role --email ian@indemn.ai --role team_member
indemn actor add-role --email marlon@indemn.ai --role team_member
indemn actor add-role --email ryan@indemn.ai --role team_member
indemn actor add-role --email dolly@indemn.ai --role team_member
