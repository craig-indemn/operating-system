---
name: onboarding
description: Set up a new team member's entire development environment. Clones repos, installs dependencies, configures credentials, starts services, and verifies everything works. Run this first on any new machine.
argument-hint: [engineer | executive | sales]
---

# Onboarding

Full environment setup for Indemn team members. Detects platform, installs prerequisites, clones repos, configures credentials, installs dependencies, starts services, and verifies everything works.

## CRITICAL: You Are the Installer

**YOU (Claude Code) run every command. DO NOT ask the user to copy-paste commands into their terminal.** You have full Bash access — use it. The user's only jobs are:

1. **Approve** when you ask to run a command (they click Allow)
2. **Click through browser flows** (GitHub login) when a command opens their browser
3. **Provide files or information** you can't determine yourself (e.g., "download .env.dev from 1Password")

Never say "run this command" — just run it.

## Phase 1: Environment Detection

Detect everything about the machine. Run all of these yourself:

```bash
echo "=== Platform ==="
uname -s       # Darwin = macOS, Linux = Linux
uname -m       # arm64 (Apple Silicon), x86_64 (Intel)
echo "=== Shell ==="
echo "$SHELL"
echo "=== Existing Tools ==="
which brew 2>/dev/null && echo "Homebrew: $(brew --version | head -1)" || echo "Homebrew: NOT INSTALLED"
which bash && echo "Bash: $(bash --version | head -1)" || echo "Bash: MISSING"
which node && echo "Node: $(node --version)" || echo "Node: NOT INSTALLED"
which uv && echo "uv: $(uv --version)" || echo "uv: NOT INSTALLED"
which gh && echo "gh: $(gh --version | head -1)" || echo "gh: NOT INSTALLED"
which git && echo "Git: $(git --version)" || echo "Git: NOT INSTALLED"
which mongosh && echo "mongosh: $(mongosh --version 2>/dev/null)" || echo "mongosh: NOT INSTALLED"
which psql 2>/dev/null && echo "psql: OK" || (which /opt/homebrew/opt/libpq/bin/psql 2>/dev/null && echo "psql: OK (homebrew path)" || echo "psql: NOT INSTALLED")
```

Then ask the user: **"Where would you like your workspace directory?"** (e.g., `~/Repositories`, `~/code`, `~/dev`). Default to `~/Repositories` if they have no preference. Create it if it doesn't exist.

## Phase 2: Prerequisites

Install everything that's missing. Detect platform and use the right commands:

### macOS

```bash
# Homebrew (if missing)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Core tools
brew install bash node@22 uv gh mongosh
brew install libpq  # PostgreSQL client

# Link node@22 if needed
brew link node@22

# Verify bash 4+
/opt/homebrew/bin/bash --version | head -1
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update

# bash 4+ is pre-installed on modern Linux
# Node 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt install -y nodejs

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# gh CLI
sudo apt install gh

# mongosh
# See https://www.mongodb.com/docs/mongodb-shell/install/

# psql
sudo apt install -y postgresql-client
```

After installing, verify:
```bash
bash --version | head -1
node --version
uv --version
gh --version | head -1
```

## Phase 3: Repository Setup

### 3a. GitHub Authentication

```bash
gh auth status
# If not authenticated:
gh auth login --web -h github.com
```

Verify org access:
```bash
gh repo list indemn-ai --limit 1 && echo "ORG ACCESS OK" || echo "NO ORG ACCESS - ask admin for invite"
```

### 3b. Clone Repositories

Clone all platform repos from the `indemn-ai` org into the workspace directory:

```bash
WORKSPACE="<their chosen workspace directory>"
cd "$WORKSPACE"

# Core platform services
REPOS=(
  "indemn-ai/bot-service"
  "indemn-ai/copilot-server"
  "indemn-ai/copilot-dashboard"
  "indemn-ai/copilot-dashboard-react"
  "indemn-ai/evaluations"
  "indemn-ai/Indemn-observatory"
  "indemn-ai/middleware-socket-service"
  "indemn-ai/conversation-service"
  "indemn-ai/kb-service"
  "indemn-ai/copilot-sync-service"
  "indemn-ai/point-of-sale"
  "indemn-ai/voice-service"
  "indemn-ai/payment-service"
)

for repo in "${REPOS[@]}"; do
  name="${repo#*/}"
  if [ -d "$name" ]; then
    echo "SKIP: $name (already exists)"
  else
    echo "Cloning $repo..."
    gh repo clone "$repo"
  fi
done
```

### 3c. Clone Operating System

```bash
cd "$WORKSPACE"
if [ -d "operating-system" ]; then
  echo "SKIP: operating-system (already exists)"
else
  gh repo clone craig-indemn/operating-system -- -b onboarding
fi
```

### 3d. Copy local-dev.sh

The `local-dev.sh` script lives in the operating-system repo but runs from the workspace root:

```bash
cp "$WORKSPACE/operating-system/local-dev.sh" "$WORKSPACE/local-dev.sh"
# Also copy the env template
cp "$WORKSPACE/operating-system/.env.template" "$WORKSPACE/.env.template" 2>/dev/null || true
```

**Note:** `local-dev.sh` auto-detects directory names — works with both org names (`copilot-dashboard-react`, `Indemn-observatory`) and legacy names (`indemn-platform-v2`, `indemn-observability`).

## Phase 4: Environment Configuration

### 4a. Get .env.dev from 1Password

Ask the user:

> "Download the `.env.dev` file from 1Password (it's in the Engineering vault, named 'Local Dev Environment'). Save it anywhere and tell me where you put it."

Then copy it:
```bash
cp "<path they give you>" "$WORKSPACE/.env.dev"
```

If they don't have 1Password access yet, fall back to the template:
```bash
cp "$WORKSPACE/.env.template" "$WORKSPACE/.env.dev"
echo "MANUAL SETUP NEEDED: Edit .env.dev with real credentials"
```

### 4b. Validate Connections

```bash
cd "$WORKSPACE"
/opt/homebrew/bin/bash ./local-dev.sh validate --env=dev
```

On Linux, use the system bash (which is 4+ by default):
```bash
bash ./local-dev.sh validate --env=dev
```

This checks: MongoDB, Redis, RabbitMQ, API keys, port availability.

### 4c. Shell Configuration (optional)

Add auto-sourcing of the env file to their shell:
```bash
SHELL_RC="$HOME/.bashrc"
[ "$(basename $SHELL)" = "zsh" ] && SHELL_RC="$HOME/.zshrc"
WORKSPACE_ABS="$(cd "$WORKSPACE" && pwd)"
if ! grep -q ".env.dev" "$SHELL_RC" 2>/dev/null; then
  echo "[ -f \"$WORKSPACE_ABS/.env.dev\" ] && source \"$WORKSPACE_ABS/.env.dev\"" >> "$SHELL_RC"
  echo "Added .env.dev sourcing to $SHELL_RC"
fi
```

## Phase 5: Install Dependencies

```bash
cd "$WORKSPACE"

# Run local-dev.sh setup (installs Node dependencies + sharp fix)
/opt/homebrew/bin/bash ./local-dev.sh setup
# Linux: bash ./local-dev.sh setup

# Python services use `uv run` which auto-installs — but pre-sync for faster first start:
for dir in bot-service evaluations kb-service conversation-service; do
  if [ -d "$WORKSPACE/$dir" ] && [ -f "$WORKSPACE/$dir/pyproject.toml" ]; then
    echo "Syncing $dir..."
    (cd "$WORKSPACE/$dir" && uv sync)
  fi
done

# Observatory uses venv instead of uv
OBSERVATORY_DIR=$(ls -d "$WORKSPACE"/Indemn-observatory "$WORKSPACE"/indemn-observability 2>/dev/null | head -1)
if [ -n "$OBSERVATORY_DIR" ] && [ -f "$OBSERVATORY_DIR/requirements.txt" ]; then
  echo "Setting up observatory venv..."
  (cd "$OBSERVATORY_DIR" && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt)
fi
```

## Phase 6: Start & Verify

### 6a. Start Services

```bash
cd "$WORKSPACE"
# macOS:
/opt/homebrew/bin/bash ./local-dev.sh start platform --env=dev
# Linux:
# bash ./local-dev.sh start platform --env=dev
```

The `platform` group starts: bot-service (8001), platform-v2 (8003), platform-v2-ui (5173), evaluations (8002).

### 6b. Health Check

Wait for services to start (local-dev.sh does this automatically), then verify:

```bash
echo "=== Service Health ==="
curl -sf http://localhost:8001/health && echo "bot-service: OK" || echo "bot-service: FAIL"
curl -sf http://localhost:8003/health && echo "platform-v2: OK" || echo "platform-v2: FAIL"
curl -sf http://localhost:8002/health && echo "evaluations: OK" || echo "evaluations: FAIL"
curl -sf http://localhost:3000/ && echo "copilot-server: OK" || echo "copilot-server: FAIL"
```

### 6c. Smoke Test

```bash
# Login via API
TOKEN=$(curl -s -X POST http://localhost:3000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"support@indemn.ai","password":"nzrjW3tZ9K3YiwtMWzBm"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('token','FAILED'))")

if [ "$TOKEN" != "FAILED" ] && [ -n "$TOKEN" ]; then
  echo "LOGIN: OK (token received)"
else
  echo "LOGIN: FAILED (check copilot-server logs)"
fi
```

### 6d. Report

Present the user with a summary:

```
Onboarding Complete!

Services Running:
  bot-service         http://localhost:8001
  platform-v2         http://localhost:8003
  platform-v2-ui      http://localhost:5173
  evaluations         http://localhost:8002

Dashboard:           http://localhost:4500
Login:               support@indemn.ai / nzrjW3tZ9K3YiwtMWzBm

Key Commands:
  ./local-dev.sh status              # Check what's running
  ./local-dev.sh start <group> --env=dev  # Start a group
  ./local-dev.sh stop all            # Stop everything
  ./local-dev.sh logs <service>      # View logs
  ./local-dev.sh logs combined       # All logs interleaved

Service Groups:
  minimal   - bot-service + evaluations (agent testing)
  platform  - bot + platform + evaluations (agent builder)
  chat      - full chat stack (widget testing)
  analytics - observability dashboard
```

## Role-Specific Flows

### Engineer (default)

All six phases. Full repo clone, full service stack.

### Executive

Phases 1-2 only (detect + prerequisites), then:
- Install only: `gog` (Google Workspace), Slack SDK, `psql`
- Authenticate Google Workspace (browser flow)
- Configure `.env` with Postgres connection string (read-only meetings DB)
- Skip repo cloning, dependency installation, and service startup
- Verify: `gog gmail search "newer_than:1d" --max 1`

### Sales

Phases 1-2 only, then:
- Install only: `gog` (Google Workspace), Slack SDK
- Authenticate Google Workspace
- Skip everything else
- Verify: `gog gmail search "newer_than:1d" --max 1`

## Troubleshooting

### "Port already in use"
```bash
# Find what's using a port
lsof -i :<port> -P | grep LISTEN
# Kill it
lsof -ti :<port> | xargs kill -9
```

### "Directory not found" when starting services
The service directory name may not match. Check `local-dev.sh` output — it auto-detects both org and legacy directory names.

### MongoDB connection fails
- Check `.env.dev` has the correct `MONGODB_URI`
- Verify your IP is whitelisted in MongoDB Atlas (Settings → Network Access)
- Ask admin to add your IP if needed

### Node service won't start
```bash
cd <service-dir> && rm -rf node_modules && npm install
```

### Python service won't start
```bash
cd <service-dir> && uv sync
```

## Conventions

- Workspace directory is user's choice — never assume `~/Repositories`
- All infrastructure is remote (MongoDB Atlas, Redis Cloud, Amazon MQ) — nothing runs locally except application services
- `.env.dev` for development, `.env.prod` for production data (read-only)
- `local-dev.sh` is the single entry point for service management
- Python services use `uv`, Node services use `npm`
- Observatory is the exception — uses `venv` + `pip`, not `uv`
