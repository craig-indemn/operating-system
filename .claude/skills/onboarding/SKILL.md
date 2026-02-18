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
| Slack (`slack_sdk`) | **Needs Slack app or browser token** | Option A: Workspace admin approves Indemn OS Slack app → get `xoxp-` token. Option B: Extract browser token from Slack Desktop (no admin needed, can expire). See `/slack` skill for details. |
| Airtable (curl) | Yes | Airtable account > Builder Hub > create Personal Access Token (needs scopes: `data.records:read`, `data.records:write`, `schema.bases:read` + grant access to all bases) |
| Apollo (curl) | Needs paid plan | Apollo.io paid plan > Settings > Integrations > API key |
| MongoDB (`mongosh`) | Yes | Nothing — connection strings are provided |
| Google Workspace (`gog`) | **Needs GCP project** | Desktop app OAuth credentials JSON — can self-service with your own GCP project, or use the shared Indemn project (ask Kyle) |
| Neonctl (`neonctl`) | Optional | Only needed for branch management, not for queries |

## Step 1: Determine Role

Ask the user their role if not already known:
- **Engineer**: All tools — slack, google-workspace, linear, github, stripe, airtable, apollo, vercel, postgres, mongodb
- **Executive**: Core tools — slack, google-workspace, postgres (read-only via meeting-intelligence skill)
- **Sales**: Customer tools — slack, google-workspace, postgres (read-only via meeting-intelligence skill), apollo

## Step 2: Check Prerequisites

```bash
echo "=== Prerequisites ==="
which node && echo "Node.js: OK" || echo "Node.js: MISSING — brew install node"
which npm && echo "npm: OK" || echo "npm: MISSING — comes with Node.js"
which brew && echo "Homebrew: OK" || echo "Homebrew: MISSING — /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
which jq && echo "jq: OK" || echo "jq: MISSING — brew install jq"
which mongosh && echo "mongosh: OK" || echo "mongosh: MISSING — brew install mongosh"
/usr/bin/python3 -c "import slack_sdk" 2>/dev/null && echo "slack_sdk: OK" || echo "slack_sdk: MISSING — pip3 install slack_sdk"
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
| mongosh (MongoDB) | `brew install mongosh` |
| slack_sdk (Python) | `pip3 install slack_sdk` |

## Step 5: Authenticate

For each tool that's installed but not authenticated, walk the user through the auth flow from its skill. Order by ease:

1. **Slack** — Get token (see `/slack` skill for full details):
   - **Quick path**: Extract browser token from Slack Desktop → set `SLACK_XOXC_TOKEN` + `SLACK_XOXD_COOKIE` in `.env`
   - **Proper path**: Create Slack app at api.slack.com/apps, add user scopes from `references/slack-scopes.md`, install to workspace (needs admin approval) → set `SLACK_TOKEN` in `.env`
   - Then: `pip3 install slack_sdk`
2. **GitHub** — `gh auth login` (browser flow)
3. **Vercel** — `vercel login` (browser flow)
4. **Stripe** — `stripe login` (browser flow, note: connects to sandbox by default)
5. **Linear** — paste API key into `.env`
6. **Airtable** — paste PAT into `.env`
7. **MongoDB** — connection strings are provided, just add `MONGODB_PROD_URI` and `MONGODB_DEV_URI` to `.env` (see `/mongodb` skill)
8. **Google Workspace** — needs OAuth credentials JSON first, then `gog auth add email`
9. **Apollo** — paste API key into `.env` (requires paid plan)

Collect any needed credentials from the user interactively.

## Step 6: Set Environment Variables

All env vars live in the repo's `.env` file (gitignored), sourced from `~/.zshrc`.

Check current state:
```bash
env | grep -E "(SLACK_TOKEN|SLACK_XOXC_TOKEN|LINEAR_API_KEY|LINEAR_API_TOKEN|STRIPE_API_KEY|VERCEL_TOKEN|NEON_API_KEY|NEON_CONNECTION_STRING|MONGODB_PROD_URI|MONGODB_DEV_URI|AIRTABLE_PAT|APOLLO_API_KEY)" | sed 's/=.*/=***/' | sort
```

If `.env` doesn't exist yet, create it in the repo root with:
```bash
# Linear bridge
export LINEAR_API_TOKEN="${LINEAR_API_KEY}"

# Neon Postgres
export NEON_CONNECTION_STRING="<get from admin — do not hardcode>"
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
source /Users/home/Repositories/operating-system/.env && PYTHONPATH=/Users/home/Repositories/operating-system/lib /usr/bin/python3 -c "from slack_client import get_client; r = get_client().auth_test(); print(f'Slack: {r[\"user\"]}@{r[\"team\"]}')"
source /Users/home/Repositories/operating-system/.env && mongosh "$MONGODB_PROD_URI/tiledesk" --quiet --eval "db.runCommand({ping:1}).ok"
curl -s "https://api.airtable.com/v0/meta/bases" -H "Authorization: Bearer $AIRTABLE_PAT" | jq '.bases | length'
```

Report results to the user.
