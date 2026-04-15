#!/bin/bash
# =============================================================================
# Step 2: Create Actors (Team Members)
# =============================================================================
# Every person on the team is an Actor in the OS. Craig already exists from
# bootstrap. These commands create the rest of the team.
#
# Note: Authentication methods (password, SSO) are configured separately.
# This just creates the actor records so they can be referenced as owners,
# assignees, and role holders.
# =============================================================================

# Leadership
indemn actor create --name "Kyle Geoghan" --email kyle@indemn.ai --type human
indemn actor create --name "Cam Torstenson" --email cam@indemn.ai --type human

# Engineering
indemn actor create --name "Dhruv Vasishtha" --email dhruv@indemn.ai --type human
indemn actor create --name "Jonathan Chen" --email jonathan@indemn.ai --type human
indemn actor create --name "Rudra Thakar" --email rudra@indemn.ai --type human
indemn actor create --name "Peter Duffy" --email peter@indemn.ai --type human
indemn actor create --name "Drew" --email drew@indemn.ai --type human

# Operations & Customer Success
indemn actor create --name "George Remmer" --email george@indemn.ai --type human
indemn actor create --name "Ganesh Iyer" --email ganesh@indemn.ai --type human
indemn actor create --name "Ian Seidner" --email ian@indemn.ai --type human

# Sales
indemn actor create --name "Marlon" --email marlon@indemn.ai --type human

# Platform
indemn actor create --name "Ryan Frere" --email ryan@indemn.ai --type human
indemn actor create --name "Dolly Talreja" --email dolly@indemn.ai --type human
