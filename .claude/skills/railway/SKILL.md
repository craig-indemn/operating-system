---
name: railway
description: Deploy and manage services on Railway — web services, cron jobs, environments, custom domains. Use when deploying backend services or managing Railway infrastructure.
---

# Railway

Deploy and manage cloud services via the `railway` CLI. Supports web services, cron jobs, databases, environments, custom domains, and monorepo deployments.

## Status Check

```bash
which railway && echo "INSTALLED" || echo "NOT INSTALLED"
```

```bash
railway whoami 2>/dev/null && echo "AUTHENTICATED" || echo "NOT AUTHENTICATED"
```

## Setup

### Install

**macOS (Homebrew):**
```bash
brew install railway
```

**npm (cross-platform, requires Node 16+):**
```bash
npm i -g @railway/cli
```

**Shell script (macOS/Linux/WSL):**
```bash
bash <(curl -fsSL cli.new)
```

**Upgrade:**
```bash
railway upgrade
```

### Authenticate

**Interactive (opens browser):**
```bash
railway login
```

**Headless / SSH (no browser):**
```bash
railway login --browserless
```

**CI/CD automation — use tokens instead of login:**
- `RAILWAY_TOKEN` — project-scoped (deploy, redeploy, logs)
- `RAILWAY_API_TOKEN` — account/workspace-scoped (full API access)

```bash
RAILWAY_TOKEN=xxxx railway up
```

## Usage

### Project Management

```bash
railway init                    # Create a new project
railway link                    # Link current directory to a project/service
railway unlink                  # Unlink directory
railway list                    # List all projects
railway status                  # Show linked project/service/environment
railway open                    # Open project in browser dashboard
```

### Deploying

```bash
# Standard deploy (streams build + deploy logs)
railway up

# Detached (returns immediately, deploy continues in background)
railway up -d

# CI mode (streams build logs only, exits when build completes)
railway up --ci

# Deploy to a specific service
railway up --service my-api

# Deploy to a specific environment
railway up --environment staging

# Deploy without linking (requires both flags)
railway up --project <id> --environment production

# Deploy a subdirectory
railway up ./backend

# Redeploy (same code, fresh container — good for env var changes)
railway redeploy

# Restart a crashed service
railway restart

# Remove most recent deployment
railway down
```

### Environment Variables

```bash
railway variable list                  # List all variables
railway variable set KEY=VALUE         # Set a variable
railway variable set KEY=VALUE -s api  # Set for a specific service
railway variable delete KEY            # Delete a variable
```

Variables are injected at both build and runtime. Use **reference variables** to connect services:
```
DATABASE_URL=${{postgres.DATABASE_URL}}
BACKEND_URL=http://${{api.RAILWAY_PRIVATE_DOMAIN}}:${{api.PORT}}
```

### Environments

```bash
railway environment              # Switch active environment (interactive)
railway environment list         # List all environments
```

Create environments in the dashboard or via API. Every project starts with `production`. Create `staging`, `dev`, or PR environments as needed. Each environment is an isolated network -- services in different environments cannot communicate privately.

### Services

```bash
railway service                  # Switch linked service (interactive)
railway add                      # Add a new service to the project
railway scale                    # Scale replicas
```

### Logs and Debugging

```bash
railway logs                     # View deployment logs
railway logs -f                  # Follow/tail logs
railway ssh                      # SSH into running container
```

### Domains and Networking

```bash
railway domain                   # Generate or manage domains
```

**Private networking (service-to-service):** All services in a project get automatic DNS at `<service-name>.railway.internal`. Use `http://` (not `https://`) for internal traffic. No configuration needed.

**Public networking:** Services do NOT get a public domain by default. Generate a `*.up.railway.app` domain or add a custom domain in service settings.

**Custom domains:** Add in service Settings > Public Networking, configure a CNAME record in your DNS provider pointing to the Railway-provided value. SSL is auto-provisioned via Let's Encrypt.

### Local Development

```bash
# Run a command with Railway env vars injected
railway run <command>

# Open a shell with Railway env vars available
railway shell

# Local dev with Docker Compose (experimental)
railway dev
```

### Volumes and Storage

```bash
railway volume list              # List volumes
railway volume add               # Add a persistent volume
```

**Buckets** (S3-compatible object storage) are created in the dashboard. $0.015/GB-month, free egress and API operations.

### Cron Jobs

Set via service Settings > Cron Schedule or in `railway.json`:
```json
{ "deploy": { "cronSchedule": "0 */6 * * *" } }
```

- Standard 5-field crontab syntax, UTC only
- Minimum interval: 5 minutes
- Only one execution at a time (overlapping runs are skipped)
- Service must exit cleanly when done
- Billed only for compute time during execution

### Config as Code

Place `railway.json` or `railway.toml` at your repo root. Config in code overrides dashboard settings.

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile",
    "watchPatterns": ["src/**"]
  },
  "deploy": {
    "startCommand": "node index.js",
    "preDeployCommand": ["npm run db:migrate"],
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

Environment-specific overrides:
```json
{
  "environments": {
    "staging": { "deploy": { "startCommand": "npm run staging" } },
    "pr": { "deploy": { "startCommand": "npm run preview" } }
  }
}
```

### Monorepo Deployment

Deploy multiple services from one repo by setting a **Root Directory** per service in Settings:
- Service A: root directory `/frontend`
- Service B: root directory `/backend`

Use **Watch Paths** to prevent unnecessary rebuilds (e.g., `/packages/backend/**` for the backend service). Each service can have its own `railway.json` at its root directory.

For JS workspaces (pnpm/yarn/bun), Railway auto-detects packages and configures service names, build commands, and watch paths.

### Databases

Railway provides one-click database templates:
- **PostgreSQL** (including HA with automatic failover)
- **MySQL**
- **Redis**
- **MongoDB**

Databases get persistent volumes automatically. Access externally via TCP Proxy, or internally via private networking (`<db-service>.railway.internal`). These are container-based databases -- you are responsible for backups, tuning, and DR.

## Global CLI Flags

```
-s, --service <name|id>       Target a specific service
-e, --environment <name>      Target a specific environment
--json                        JSON output
-y, --yes                     Auto-confirm prompts
```

## Full Reference

For comprehensive details on all topics (CLI commands, config-as-code options, networking specs, cron patterns, pricing, scaling, production checklist, monorepo patterns, and recent platform updates), see:

- `references/railway-guide.md` — complete Railway reference
- Railway Docs: https://docs.railway.com
- Railway Changelog: https://railway.com/changelog
