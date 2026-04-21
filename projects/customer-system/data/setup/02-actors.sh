#!/bin/bash
# =============================================================================
# Step 2: Create Actors (Team Members)
# =============================================================================
# Every person on the team is an Actor in the OS. Craig already exists from
# bootstrap. These commands create the rest of the team.
#
# Syntax: indemn actor create --type human --name "Name" --email addr@indemn.ai
#
# Note: Authentication methods (password, SSO) are configured separately.
# This just creates the actor records so they can be referenced as owners,
# assignees, and role holders.
# =============================================================================

# Leadership
indemn actor create --type human --name "Kyle Geoghan" --email kyle@indemn.ai
indemn actor create --type human --name "Cam Torstenson" --email cam@indemn.ai

# Engineering
indemn actor create --type human --name "Dhruv Vasishtha" --email dhruv@indemn.ai
indemn actor create --type human --name "Jonathan Chen" --email jonathan@indemn.ai
indemn actor create --type human --name "Rudra Thakar" --email rudra@indemn.ai
indemn actor create --type human --name "Peter Duffy" --email peter@indemn.ai
indemn actor create --type human --name "Drew" --email drew@indemn.ai

# Operations & Customer Success
indemn actor create --type human --name "George Remmer" --email george@indemn.ai
indemn actor create --type human --name "Ganesh Iyer" --email ganesh@indemn.ai
indemn actor create --type human --name "Ian Seidner" --email ian@indemn.ai

# Sales
indemn actor create --type human --name "Marlon" --email marlon@indemn.ai

# Platform
indemn actor create --type human --name "Ryan Frere" --email ryan@indemn.ai
indemn actor create --type human --name "Dolly Talreja" --email dolly@indemn.ai
