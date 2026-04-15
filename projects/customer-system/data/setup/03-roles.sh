#!/bin/bash
# =============================================================================
# Step 3: Create Roles
# =============================================================================
# One role for now: team_member. Everyone gets it. Full read/write on
# everything. Watches and role differentiation (account_lead, executive)
# come later when we design automations.
# =============================================================================

indemn role create team_member \
  --permissions '{"read": ["*"], "write": ["*"]}' \
  --description "Full access to all customer system entities"

# Grant to everyone
indemn actor grant "Craig Certo" --role team_member
indemn actor grant "Kyle Geoghan" --role team_member
indemn actor grant "Cam Torstenson" --role team_member
indemn actor grant "Dhruv Vasishtha" --role team_member
indemn actor grant "Jonathan Chen" --role team_member
indemn actor grant "Rudra Thakar" --role team_member
indemn actor grant "Peter Duffy" --role team_member
indemn actor grant "Drew" --role team_member
indemn actor grant "George Remmer" --role team_member
indemn actor grant "Ganesh Iyer" --role team_member
indemn actor grant "Ian Seidner" --role team_member
indemn actor grant "Marlon" --role team_member
indemn actor grant "Ryan Frere" --role team_member
indemn actor grant "Dolly Talreja" --role team_member
