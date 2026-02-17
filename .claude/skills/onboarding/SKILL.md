---
name: onboarding
description: Set up all tools for your role at Indemn. Checks what's installed, installs what's missing, and verifies authentication. Run this first.
---

# Onboarding

Role-based setup for the Indemn Operating System. Detects what's installed, installs what's missing, verifies authentication.

## CRITICAL: You Are the Installer

**YOU (Claude Code) run every command. DO NOT ask the user to copy-paste commands into their terminal.** You have full Bash access — use it. The user's only jobs are:

1. **Approve** when you ask to run a command (they click Allow)
2. **Click through browser flows** (Google OAuth, GitHub login) when a command opens their browser
3. **Provide information** you can't determine yourself (e.g., "where did you save the credentials file?", "what's your email?")

Never say "run this command" or "paste this into your terminal." Instead, just run it. If it needs sudo and fails, explain why and ask them to approve the elevated command.

## What You'll Need From the User

Before starting, here's what each tool requires. Some are fully self-service (you install everything), some need the user to provide a credential or click through a browser flow.

| Tool | What You Do | What the User Does |
|------|------------|-------------------|
| Google Workspace (`gog`) | Install binary, load credentials, run auth command | Provides credentials JSON file location, clicks through Google consent in browser |
| GitHub (`gh`) | Install CLI, run auth command | Clicks through GitHub login in browser |
| Slack (`slack_sdk`) | Install Python package, write .env | Provides Slack token (or you extract browser token) |
| Linear (`linearis`) | Install CLI, write .env | Provides API key from Linear settings |
| Vercel (`vercel`) | Install CLI, run auth command | Clicks through Vercel login in browser |
| Stripe (`stripe`) | Install CLI, run auth command | Clicks through Stripe login in browser |
| Postgres (`psql`) | Install client, write connection string to .env | Nothing — connection string is provided |
| MongoDB (`mongosh`) | Install shell, write connection string to .env | Nothing — connection strings are provided |
| Airtable (curl) | Write .env | Provides Personal Access Token from Airtable |
| Apollo (curl) | Write .env | Provides API key (requires paid plan) |

## Step 1: Determine Role

Ask the user their role if not already known:
- **Engineer**: All tools — slack, google-workspace, linear, github, stripe, airtable, apollo, vercel, postgres, mongodb
- **Executive**: Core tools — google-workspace, slack, postgres (read-only via meeting-intelligence skill)
- **Sales**: Customer tools — slack, google-workspace, postgres (read-only via meeting-intelligence skill), apollo

## Step 2: Detect Platform and Check Prerequisites

Run these commands yourself:

```bash
echo "=== Platform ==="
uname -s  # Darwin = macOS, Linux = Linux
uname -m  # x86_64 or arm64
```

```bash
echo "=== Prerequisites ==="
which node && echo "Node.js: OK" || echo "Node.js: MISSING"
which npm && echo "npm: OK" || echo "npm: MISSING"
which curl && echo "curl: OK" || echo "curl: MISSING"
which jq && echo "jq: OK" || echo "jq: MISSING"
which python3 && echo "Python3: OK" || echo "Python3: MISSING"
python3 -c "import slack_sdk" 2>/dev/null && echo "slack_sdk: OK" || echo "slack_sdk: MISSING"
```

**Install anything that's missing — do not ask the user to do it:**
- macOS: `brew install node jq` (if Homebrew is missing, install it: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)
- Linux: `sudo apt update && sudo apt install -y nodejs npm jq python3 python3-pip curl`

## Step 3: Run Status Checks

For each tool in the user's role, run the status check from its skill yourself. Collect results into a summary and show the user:

| Tool | Installed | Authenticated |
|------|-----------|---------------|
| Each tool... | Yes/No | Yes/No |

## Step 4: Install Missing Tools

**Run the install commands yourself.** Detect the platform and use the right command:

| Tool | macOS | Linux (Ubuntu/Debian) |
|------|-------|----------------------|
| gog (Google Workspace) | `brew install steipete/tap/gogcli` | Download binary from GitHub releases (see `/google-workspace` skill) |
| linearis (Linear) | `npm install -g linearis` | `npm install -g linearis` |
| gh (GitHub) | `brew install gh` | `sudo apt install gh` or see [install instructions](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) |
| stripe | `brew install stripe/stripe-cli/stripe` | Download from https://github.com/stripe/stripe-cli/releases |
| vercel | `npm install -g vercel` | `npm install -g vercel` |
| neonctl | `npm install -g neonctl` | `npm install -g neonctl` |
| psql | `brew install libpq` | `sudo apt install postgresql-client` |
| mongosh (MongoDB) | `brew install mongosh` | See https://www.mongodb.com/docs/mongodb-shell/install/ |
| slack_sdk (Python) | `pip3 install slack_sdk` | `pip3 install slack_sdk` |

**Note:** On Linux, if `npm` is not available, install Node.js first: `sudo apt install nodejs npm`

## Step 5: Authenticate

For each tool that needs authentication, **run the commands yourself**. The user only interacts when a browser opens or when you need a credential they must provide.

1. **Google Workspace** — Ask the user: "Do you have a credentials JSON file that was shared with you? Where is it saved?" Then run:
   - `gog auth credentials set <path-they-gave-you>`
   - `gog auth add their-email@indemn.ai` — this opens a browser. Tell the user: "A browser window should open. Sign in with your Google account and approve the permissions. Let me know when you're done."
2. **GitHub** — Run `gh auth login --web`. Tell the user a browser will open for GitHub login.
3. **Vercel** — Run `vercel login`. Browser flow.
4. **Stripe** — Run `stripe login`. Browser flow (note: connects to sandbox by default).
5. **Linear** — Ask the user for their API key (from Linear > Settings > Personal API Keys). Write it to `.env` yourself.
6. **Airtable** — Ask the user for their PAT. Write it to `.env` yourself.
7. **MongoDB** — Connection strings are provided. Write `MONGODB_PROD_URI` and `MONGODB_DEV_URI` to `.env` yourself (see `/mongodb` skill).
8. **Slack** — Ask the user if they have a Slack token. If not, see `/slack` skill for options. Write token(s) to `.env` yourself.
9. **Apollo** — Ask the user for their API key. Write it to `.env` yourself (requires paid plan).

## Step 6: Set Environment Variables

**Create and configure the .env file yourself.** Do not ask the user to edit files.

Check current state:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel) && [ -f "$REPO_ROOT/.env" ] && echo ".env exists" || echo ".env does not exist"
```

If `.env` doesn't exist, create it yourself using the Write tool. Include any credentials collected during Step 5.

Then add the auto-source line to the user's shell rc file. Detect which shell and write it yourself:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
SHELL_RC="$HOME/.bashrc"
[ "$(basename $SHELL)" = "zsh" ] && SHELL_RC="$HOME/.zshrc"
if ! grep -q "operating-system/.env" "$SHELL_RC" 2>/dev/null; then
  echo "[ -f \"$REPO_ROOT/.env\" ] && source \"$REPO_ROOT/.env\"" >> "$SHELL_RC"
  echo "Added .env sourcing to $SHELL_RC"
fi
```

## Step 7: Verify Everything

Run all status checks again yourself. Print a final summary showing all green, or highlight what still needs attention.

## Step 8: First Commands

Run one test command per tool to confirm end-to-end. **You run these, not the user:**

```bash
gog gmail search "newer_than:1d" --max 1 --json
```

For tools that need .env loaded:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel) && source "$REPO_ROOT/.env" && PYTHONPATH="$REPO_ROOT/lib" python3 -c "from slack_client import get_client; r = get_client().auth_test(); print(f'Slack: {r[\"user\"]}@{r[\"team\"]}')"
```

Report results to the user. If everything passes, tell them they're all set and show them a few example things they can ask you to do.
