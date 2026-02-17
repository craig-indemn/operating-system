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

First detect the platform:
```bash
echo "=== Platform ==="
uname -s  # Darwin = macOS, Linux = Linux
```

Then check prerequisites (adapt install commands to platform):
```bash
echo "=== Prerequisites ==="
which node && echo "Node.js: OK" || echo "Node.js: MISSING"
which npm && echo "npm: OK" || echo "npm: MISSING"
which curl && echo "curl: OK" || echo "curl: MISSING"
which jq && echo "jq: OK" || echo "jq: MISSING"
which python3 && echo "Python3: OK" || echo "Python3: MISSING"
python3 -c "import slack_sdk" 2>/dev/null && echo "slack_sdk: OK" || echo "slack_sdk: MISSING — pip3 install slack_sdk"
```

**Install missing prerequisites:**
- macOS: `brew install node jq` (install Homebrew first if missing: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)
- Linux: `sudo apt update && sudo apt install -y nodejs npm jq python3 python3-pip curl`

## Step 3: Run Status Checks

For each tool in the user's role, run the status check from its skill. Collect results into a summary:

| Tool | Installed | Authenticated |
|------|-----------|---------------|
| Each tool... | Yes/No | Yes/No |

## Step 4: Install Missing Tools

For each tool that's not installed, run the install command from its skill. Detect the platform first (`uname -s`) and use the appropriate command:

| Tool | macOS | Linux (Ubuntu/Debian) |
|------|-------|----------------------|
| gog (Google Workspace) | `brew install steipete/tap/gogcli` | Download binary from GitHub releases (see `/google-workspace` skill) |
| linearis (Linear) | `npm install -g linearis` | `npm install -g linearis` |
| gh (GitHub) | `brew install gh` | `sudo apt install gh` or [install instructions](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) |
| stripe | `brew install stripe/stripe-cli/stripe` | Download from https://github.com/stripe/stripe-cli/releases |
| vercel | `npm install -g vercel` | `npm install -g vercel` |
| neonctl | `npm install -g neonctl` | `npm install -g neonctl` |
| psql | `brew install libpq` | `sudo apt install postgresql-client` |
| mongosh (MongoDB) | `brew install mongosh` | See https://www.mongodb.com/docs/mongodb-shell/install/ |
| slack_sdk (Python) | `pip3 install slack_sdk` | `pip3 install slack_sdk` |

**Note:** On Linux, if `npm` is not available, install Node.js first: `sudo apt install nodejs npm`

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
8. **Google Workspace** — needs an OAuth credentials JSON file (Desktop app type). Ask the user: "Do you have a credentials JSON file that was shared with you?" If yes, use it directly. If no, they need to create their own GCP project — see the Prerequisites section of the `/google-workspace` skill. Once they have the JSON:
   - `gog auth credentials set ~/path/to/credentials.json`
   - `gog auth add their-email@indemn.ai` (opens browser for Google consent)
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
export NEON_CONNECTION_STRING="postgresql://neondb_owner:REDACTED_NEON_PASSWORD@ep-dark-hat-ah6i1mwb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

Then add to the user's shell rc file. Detect which shell they use and add to the right file:
- **zsh** (macOS default): `~/.zshrc`
- **bash** (Linux default): `~/.bashrc`

```bash
[ -f "<repo-path>/.env" ] && source "<repo-path>/.env"
```
Claude should detect the repo root with `git rev-parse --show-toplevel` and the shell with `echo $SHELL`, then substitute the correct values.

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
REPO_ROOT=$(git rev-parse --show-toplevel) && source "$REPO_ROOT/.env" && PYTHONPATH="$REPO_ROOT/lib" /usr/bin/python3 -c "from slack_client import get_client; r = get_client().auth_test(); print(f'Slack: {r[\"user\"]}@{r[\"team\"]}')"
REPO_ROOT=$(git rev-parse --show-toplevel) && source "$REPO_ROOT/.env" && mongosh "$MONGODB_PROD_URI/tiledesk" --quiet --eval "db.runCommand({ping:1}).ok"
curl -s "https://api.airtable.com/v0/meta/bases" -H "Authorization: Bearer $AIRTABLE_PAT" | jq '.bases | length'
```

Report results to the user.
