---
name: onboarding
description: Set up all tools for your role at Indemn. Checks what's installed, installs what's missing, and verifies authentication. Run this first.
---

# Onboarding

Role-based setup for the Indemn Operating System. Detects what's installed, guides you through what's missing.

## What You'll Need

Before starting, here's what each tool requires. Some are fully self-service, some need credentials or admin access.

| Tool | Self-Service? | What You Need |
|------|--------------|---------------|
| GitHub (`gh`) | Yes | GitHub account with indemn-ai org access |
| Vercel (`vercel`) | Yes | Vercel account on Indemn team, or `VERCEL_TOKEN` |
| Postgres (`psql`) | Yes | Nothing — connection string is provided |
| Linear (`linearis`) | Yes | Linear account > Settings > create Personal API Key |
| Stripe (`stripe`) | Yes | Stripe Dashboard access (for `stripe login`) or API key |
| Slack (`agent-slack`) | Yes | Slack Desktop app installed and signed in |
| Airtable (curl) | Yes | Airtable account > Builder Hub > create Personal Access Token (needs scopes: `data.records:read`, `data.records:write`, `schema.bases:read` + grant access to all bases) |
| Apollo (curl) | Needs paid plan | Apollo.io paid plan > Settings > Integrations > API key |
| Google Workspace (`gog`) | **Needs GCP project** | Desktop app OAuth credentials JSON — can self-service with your own GCP project, or use the shared Indemn project (ask Kyle) |
| Neonctl (`neonctl`) | Optional | Only needed for branch management, not for queries |

## Step 1: Determine Role

Ask the user their role if not already known:
- **Engineer**: All tools — slack, google-workspace, linear, github, stripe, airtable, apollo, vercel, postgres
- **Executive**: Core tools — slack, google-workspace, postgres (read-only via meeting-intelligence skill)
- **Sales**: Customer tools — slack, google-workspace, postgres (read-only via meeting-intelligence skill), apollo

## Step 2: Check Prerequisites

```bash
echo "=== Prerequisites ==="
which node && echo "Node.js: OK" || echo "Node.js: MISSING — brew install node"
which npm && echo "npm: OK" || echo "npm: MISSING — comes with Node.js"
which brew && echo "Homebrew: OK" || echo "Homebrew: MISSING — /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
which jq && echo "jq: OK" || echo "jq: MISSING — brew install jq"
```

## Step 3: Run Status Checks

For each tool in the user's role, run the status check from its skill. Collect results into a summary:

| Tool | Installed | Authenticated |
|------|-----------|---------------|
| Each tool... | Yes/No | Yes/No |

## Step 4: Install Missing Tools

For each tool that's not installed, run the install command from its skill:

| Tool | Install Command |
|------|----------------|
| gog (Google Workspace) | `brew install steipete/tap/gogcli` |
| linearis (Linear) | `npm install -g linearis` |
| gh (GitHub) | `brew install gh` |
| stripe | `brew install stripe/stripe-cli/stripe` |
| vercel | `npm install -g vercel` |
| neonctl | `npm install -g neonctl` |
| psql | `brew install libpq` |
| agent-slack | Runs via npx, no install needed |

## Step 5: Authenticate

For each tool that's installed but not authenticated, walk the user through the auth flow from its skill. Order by ease:

1. **Slack** — `npx agent-slack auth import-desktop` (automatic, 5 seconds)
2. **GitHub** — `gh auth login` (browser flow)
3. **Vercel** — `vercel login` (browser flow)
4. **Stripe** — `stripe login` (browser flow, note: connects to sandbox by default)
5. **Linear** — paste API key into `.env`
6. **Airtable** — paste PAT into `.env`
7. **Google Workspace** — needs OAuth credentials JSON first, then `gog auth add email`
8. **Apollo** — paste API key into `.env` (requires paid plan)

Collect any needed credentials from the user interactively.

## Step 6: Set Environment Variables

All env vars live in the repo's `.env` file (gitignored), sourced from `~/.zshrc`.

Check current state:
```bash
env | grep -E "(SLACK_TOKEN|LINEAR_API_KEY|LINEAR_API_TOKEN|STRIPE_API_KEY|VERCEL_TOKEN|NEON_API_KEY|NEON_CONNECTION_STRING|AIRTABLE_PAT|APOLLO_API_KEY)" | sed 's/=.*/=***/' | sort
```

If `.env` doesn't exist yet, create it in the repo root with:
```bash
# Linear bridge
export LINEAR_API_TOKEN="${LINEAR_API_KEY}"

# Neon Postgres
export NEON_CONNECTION_STRING="postgresql://neondb_owner:REDACTED_NEON_PASSWORD@ep-dark-hat-ah6i1mwb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

Then add to `~/.zshrc`:
```bash
[ -f "$HOME/Repositories/operating-system/.env" ] && source "$HOME/Repositories/operating-system/.env"
```

## Step 7: Verify Everything

Run all status checks again. Print a final summary showing all green, or highlight what still needs attention.

## Step 8: First Commands

Once everything is authenticated, run one test command per tool to confirm end-to-end:
```bash
gh api user --jq '.login'
vercel whoami
/opt/homebrew/opt/libpq/bin/psql "$NEON_CONNECTION_STRING" -c 'SELECT count(*) FROM "Meeting"'
linearis issues list --limit 1
gog gmail search "newer_than:1d" --max 1 --json
stripe config --list
npx agent-slack auth test
curl -s "https://api.airtable.com/v0/meta/bases" -H "Authorization: Bearer $AIRTABLE_PAT" | jq '.bases | length'
```

Report results to the user.
