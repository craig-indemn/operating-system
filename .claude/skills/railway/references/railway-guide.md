# Railway Platform — Complete Reference

Comprehensive reference for the Railway cloud platform. Covers all major features as of early 2026.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [CLI Reference](#cli-reference)
3. [Deployment Model](#deployment-model)
4. [Config as Code](#config-as-code)
5. [Environments](#environments)
6. [Variables](#variables)
7. [Cron Jobs](#cron-jobs)
8. [Networking](#networking)
9. [Databases](#databases)
10. [Storage — Volumes and Buckets](#storage)
11. [Functions](#functions)
12. [Monorepo Support](#monorepo-support)
13. [Scaling and Regions](#scaling-and-regions)
14. [Pricing](#pricing)
15. [Production Readiness Checklist](#production-readiness-checklist)
16. [Recent Platform Updates (2025-2026)](#recent-platform-updates)

---

## Core Concepts

### Hierarchy

**Workspace** > **Project** > **Service** > **Deployment**

- **Workspace**: Team or account level. Owns billing, members, and projects.
- **Project**: Groups related services under a shared private network. A project = an application stack (API + frontend + database + workers).
- **Service**: A deployment target within a project. Each service has its own source, build/start commands, variables, domains, logs, and metrics. Service names are limited to 32 characters.
- **Environment**: Provides isolation within a project. Every project starts with `production`. Additional persistent environments (staging, dev) or ephemeral PR environments can be created. All service configuration is scoped per-environment.
- **Deployment**: A built, deliverable unit of a service. Each git push or `railway up` creates a new deployment with its own image, logs, and metrics.

### Service Types

- **Persistent Services**: Always-running — web apps, APIs, message queues, databases.
- **Cron Jobs**: Run on a schedule, execute to completion, then stop. Billed only during execution.
- **Functions**: Single TypeScript files running on Bun. Deploy in seconds, no repo needed. Max 96KB per file.

### Service Sources

Services deploy from one of three sources:
1. **GitHub Repository**: Connect a repo + branch. Auto-deploys on push.
2. **Docker Image**: Public images from Docker Hub, GHCR, Quay.io, GitLab CR, or Microsoft CR. Private registries require Pro plan.
3. **Local Directory**: Via CLI (`railway link` + `railway up`).

---

## CLI Reference

### Installation

```bash
# macOS (Homebrew)
brew install railway

# npm (cross-platform, requires Node 16+)
npm i -g @railway/cli

# Shell script (macOS/Linux/WSL)
bash <(curl -fsSL cli.new)

# Windows (Scoop)
scoop install railway

# Upgrade to latest
railway upgrade
```

### Authentication

```bash
railway login                    # Opens browser for OAuth
railway login --browserless      # For headless/SSH (prints code to enter at URL)
railway whoami                   # Check current user and workspace
railway logout                   # Sign out
```

**CI/CD tokens:**
- `RAILWAY_TOKEN` — project-scoped. Supports: deploy, redeploy, log viewing.
- `RAILWAY_API_TOKEN` — account/workspace-scoped. Full API access.

Set as environment variable before running commands:
```bash
export RAILWAY_TOKEN=xxxx-xxxx-xxxx
railway up --ci
```

### All Commands

#### Project Management
```bash
railway init                     # Create a new project interactively
railway link                     # Link current directory to project + service
railway unlink                   # Unlink current directory
railway list                     # List all projects in workspace
railway status                   # Show linked project, service, environment
railway open                     # Open project in browser dashboard
railway project                  # Switch linked project (interactive)
```

#### Deploying
```bash
railway up                       # Deploy: scan, compress, upload, build, deploy (streams all logs)
railway up -d                    # Detached: returns after upload, deploy continues in background
railway up --ci                  # CI mode: streams build logs only, exits when build completes
railway up --json                # JSON output (implies CI mode)
railway up --service my-api      # Deploy to specific service
railway up --environment staging # Deploy to specific environment
railway up --project <id> --environment production  # Deploy without linking (both flags required)
railway up ./backend             # Deploy from a subdirectory
railway up ./backend --path-as-root  # Treat subdirectory as the repo root
railway up --no-gitignore        # Include gitignored files in upload
railway up --verbose             # Debug output
railway redeploy                 # Redeploy latest deployment (same code, new container)
railway restart                  # Restart a crashed deployment
railway down                     # Remove most recent deployment
```

#### Services
```bash
railway service                  # Switch linked service (interactive picker)
railway add                      # Add a new service to the project
railway scale                    # Scale service replicas
railway delete                   # Delete a service
```

#### Environments
```bash
railway environment              # Switch active environment (interactive)
railway environment list         # List all environments
railway environment new <name>   # Create a new environment
railway environment new <name> --copy <env-id>  # Clone from existing
```

#### Variables
```bash
railway variable list            # List all variables for linked service
railway variable set KEY=VALUE   # Set a variable
railway variable set KEY=VALUE -s api  # Set for a specific service
railway variable delete KEY      # Delete a variable
```

#### Logs and Debugging
```bash
railway logs                     # View recent deployment logs
railway logs -f                  # Follow/tail logs in real time
railway ssh                      # SSH into running service container
railway run <command>            # Run a local command with Railway env vars injected
railway shell                    # Open a subshell with all Railway env vars
```

#### Networking
```bash
railway domain                   # Generate or manage public domains
railway connect                  # Connect to a database via CLI
```

#### Volumes and Storage
```bash
railway volume list              # List attached volumes
railway volume add               # Add a persistent volume
railway bucket                   # Manage storage buckets (added early 2026)
```

#### Local Development
```bash
railway dev                      # Local dev: runs image-based services via Docker Compose,
                                 # code services natively. Optional Caddy reverse proxy with
                                 # HTTPS via mkcert. Experimental feature.
```

#### Utility
```bash
railway docs                     # Open Railway docs in browser
railway starship                 # Set up Starship prompt integration
railway completions <shell>      # Generate shell completions (bash, zsh, fish)
```

### Global Flags

```
-s, --service <name|id>          Target a specific service
-e, --environment <name>         Target a specific environment
--json                           JSON output format
-y, --yes                        Auto-confirm prompts
```

---

## Deployment Model

### Build Process

Railway builds from source using one of two builders:

**Railpack (default):** Railway's custom builder (successor to Nixpacks). Auto-detects language/framework and builds accordingly. Supports Node.js, Python, Go, Rust, Ruby, PHP, Java, Elixir, and more.

**Dockerfile:** If a `Dockerfile` exists at the root (or configured path), Railway uses it. Specify a custom Dockerfile path in settings or `railway.json`.

### Build Configuration

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.prod",
    "buildCommand": "yarn build",
    "watchPatterns": ["src/**", "package.json"],
    "railpackVersion": "0.7.0"
  }
}
```

- `builder`: `RAILPACK` or `DOCKERFILE`
- `buildCommand`: Custom build command (runs during build phase)
- `dockerfilePath`: Path to Dockerfile (if not at root)
- `watchPatterns`: Gitignore-style patterns. Only changes matching these patterns trigger rebuilds. Critical for monorepos.
- `railpackVersion`: Pin a specific Railpack version

### Deploy Configuration

```json
{
  "deploy": {
    "startCommand": "node index.js",
    "preDeployCommand": ["npm run db:migrate"],
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5,
    "overlapSeconds": "60",
    "drainingSeconds": "10"
  }
}
```

- `startCommand`: The command that starts your service
- `preDeployCommand`: Runs between build and deploy in a separate container. Has access to private network and env vars. Filesystem changes do NOT persist. If it exits non-zero, deployment stops.
- `healthcheckPath`: HTTP path Railway polls for 200 OK before routing traffic. Enables zero-downtime deploys.
- `healthcheckTimeout`: Max seconds to wait for healthy response (default 300)
- `restartPolicyType`: `ON_FAILURE`, `ALWAYS`, or `NEVER`
- `restartPolicyMaxRetries`: Max restart attempts (up to 10)
- `overlapSeconds`: How long the old deployment stays running alongside the new one
- `drainingSeconds`: Time between SIGTERM and SIGKILL during shutdown

### Healthchecks

- Railway sends `GET` requests to the healthcheck path
- Uses hostname `healthcheck.railway.app` in the `Host` header
- Waits for HTTP 200 before switching traffic
- If timeout expires without healthy response, deploy fails
- Healthchecks are NOT used for ongoing monitoring after deployment goes live

### Deployment Actions

- **Rollback**: Revert to a previous deployment's image + config
- **Redeploy**: Same code, fresh container (useful after env var changes)
- **Restart**: Recover a crashed deployment (auto-retried up to 10 times)
- **Cancel**: Stop an in-progress build/deploy
- **Remove**: Delete a deployment

### GitHub Auto-Deploys

When a service is connected to a GitHub repo:
- Every push to the linked branch triggers a build + deploy
- Configure **Check Suites** to wait for GitHub Actions/CI to pass before deploying
- **PR Environments** auto-create ephemeral environments for pull requests

### Docker Image Auto-Updates

For services deploying Docker images:
- Railway monitors for image updates
- Versioned tags (e.g., `nginx:1.25.3`): stages new versions for review
- Unversioned tags (e.g., `nginx:latest`): auto-redeploys to fetch latest digest
- Configurable schedules and maintenance windows

---

## Config as Code

Place `railway.json` or `railway.toml` at the root of your repo (or service root directory for monorepos).

**Priority order (highest to lowest):**
1. Environment-specific code config
2. Base code config
3. Dashboard service settings

### Complete railway.json Example

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile",
    "buildCommand": "yarn build",
    "watchPatterns": ["src/**", "package.json", "Dockerfile"],
    "railpackVersion": "0.7.0"
  },
  "deploy": {
    "startCommand": "node dist/index.js",
    "preDeployCommand": ["npm run db:migrate"],
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5,
    "cronSchedule": "0 */6 * * *",
    "multiRegionConfig": {
      "us-west2": { "numReplicas": 2 },
      "us-east4-eqdc4a": { "numReplicas": 2 },
      "europe-west4-drams3a": { "numReplicas": 1 }
    },
    "overlapSeconds": "60",
    "drainingSeconds": "10"
  },
  "environments": {
    "staging": {
      "deploy": {
        "startCommand": "npm run staging",
        "multiRegionConfig": {
          "us-west2": { "numReplicas": 1 }
        }
      }
    },
    "pr": {
      "deploy": {
        "startCommand": "npm run preview"
      }
    }
  }
}
```

### railway.toml Equivalent

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"
buildCommand = "yarn build"
watchPatterns = ["src/**", "package.json", "Dockerfile"]

[deploy]
startCommand = "node dist/index.js"
preDeployCommand = ["npm run db:migrate"]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 5
cronSchedule = "0 */6 * * *"

[deploy.multiRegionConfig.us-west2]
numReplicas = 2

[deploy.multiRegionConfig.us-east4-eqdc4a]
numReplicas = 2

[environments.staging.deploy]
startCommand = "npm run staging"

[environments.pr.deploy]
startCommand = "npm run preview"
```

---

## Environments

### Types

**Production**: Created by default with every project. The baseline environment.

**Persistent environments** (staging, dev, QA): Created manually. Two options:
- **Duplicate**: Copies all services, variables, and config from an existing environment. Services are staged (not auto-deployed) and require manual approval.
- **Empty**: Blank slate with no services.

**PR Environments**: Ephemeral, auto-created when a PR is opened against a connected GitHub repo. Auto-deleted when the PR merges or closes.

### PR Environment Features

- Auto-domain provisioning if the base environment uses Railway domains
- **Focused PR Environments** (Jan 2026): For monorepos, only services affected by changed files are deployed. Unaffected services are skipped but can be manually triggered.
- Bot PR support (Dependabot, Renovate, Claude Code) togglable in settings
- Use the `"pr"` key in config-as-code for PR-specific overrides

### Environment Sync

Import services between environments. Shows "New," "Edited," or "Removed" status tags for staged review before deploying.

### Environment RBAC (Enterprise)

Restrict access to sensitive environments. Non-admin members can see environments exist but cannot access resources or configurations.

### Key Behaviors

- Each environment has its own isolated private network
- Variables do NOT automatically inherit between environments
- Duplicating an environment copies variables at that point in time (no ongoing sync)
- Services in different environments cannot communicate over the private network

---

## Variables

### Setting Variables

**Dashboard:** Service > Variables tab. Add individually or bulk import.

**CLI:**
```bash
railway variable set DATABASE_URL=postgres://...
railway variable set API_KEY=secret -s my-api -e production
railway variable list
railway variable delete OLD_KEY
```

**Config as Code:** Variables cannot be set in `railway.json`/`railway.toml`. Use the dashboard, CLI, or API.

### Reference Variables

Dynamically reference another service's variables using `${{ServiceName.VARIABLE}}`:

```
DATABASE_URL=${{postgres.DATABASE_URL}}
REDIS_URL=${{redis.REDIS_URL}}
BACKEND_URL=http://${{api.RAILWAY_PRIVATE_DOMAIN}}:${{api.PORT}}
```

Reference variables auto-update when the referenced value changes (e.g., when a domain changes).

### Railway-Provided Variables

These are automatically available in every service:

| Variable | Description |
|----------|-------------|
| `RAILWAY_ENVIRONMENT_NAME` | Current environment name |
| `RAILWAY_ENVIRONMENT_ID` | Current environment ID |
| `RAILWAY_SERVICE_NAME` | Current service name |
| `RAILWAY_PROJECT_ID` | Project ID |
| `RAILWAY_PRIVATE_DOMAIN` | Internal DNS name (`service.railway.internal`) |
| `RAILWAY_PUBLIC_DOMAIN` | Public domain (if assigned) |
| `PORT` | The port Railway assigns |

### Shared Variables

Project-level variables shared across all services. Set in project Settings > Shared Variables. Individual services can override shared variables.

### Sealed Variables

Write-only variables hidden from the UI and API after creation. Useful for sensitive credentials. Once sealed, the value cannot be read back — only overwritten or deleted.

### Variable Scoping

Variables are scoped per-service, per-environment. Changing a variable in staging does not affect production.

---

## Cron Jobs

### Configuration

Set the cron schedule in one of two places:

**Dashboard:** Service > Settings > Cron Schedule

**Config as Code:**
```json
{ "deploy": { "cronSchedule": "0 3 * * *" } }
```

### Syntax

Standard 5-field crontab format:

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

### Examples

```
*/15 * * * *       Every 15 minutes
0 */6 * * *        Every 6 hours
30 9 * * 1-5       Weekdays at 9:30 AM UTC
0 3 * * *          Daily at 3:00 AM UTC
0 0 1 * *          First day of each month at midnight UTC
0 8 * * 1          Every Monday at 8:00 AM UTC
```

### Constraints and Behavior

- **Timezone**: UTC only. Calculate offsets manually for other timezones.
- **Minimum interval**: 5 minutes between executions.
- **Precision**: NOT guaranteed to the exact minute. Can vary by a few minutes.
- **Concurrency**: Only one execution at a time. If the previous run is still active when the next is scheduled, the next run is skipped.
- **Process lifecycle**: The service must exit cleanly when the task completes. Close database connections, flush buffers, then exit with code 0. A hanging process blocks all subsequent runs.
- **Billing**: Only billed for compute time during execution. Between runs, no resources are consumed and nothing is billed.
- **Logging**: Logs from each execution are visible in the service's log viewer, tagged by deployment.
- **No built-in retry**: If a run fails, it does not automatically retry. The next execution happens at the next scheduled time.

### What Cron Jobs Are NOT

- Not for web servers or always-running processes
- Not for sub-5-minute intervals
- Not for tasks requiring exact-second timing
- No built-in state management or coordination between runs
- No built-in error alerting (use webhooks or external monitoring)

### Pattern: Cron with Healthcheck

If your cron service also exposes an HTTP endpoint for monitoring, set a healthcheck. Railway checks health before marking the deployment as live.

---

## Networking

### Private Networking (Service-to-Service)

All services within a project share a private network. No configuration needed.

**DNS format:** `<service-name>.railway.internal`

**Example:** A service named `api` is reachable at `http://api.railway.internal:3000` from any other service in the same project and environment.

**Key details:**
- Encrypted via WireGuard mesh tunnels
- Use `http://` (not `https://`) for internal traffic
- Each environment has its own isolated network
- Services in different projects or environments CANNOT communicate privately
- IPv4 and IPv6 resolution (environments created after Oct 2025)
- No port exposure or configuration required
- Free — no egress charges for private network traffic

**Reference variables for internal URLs:**
```
BACKEND_URL=http://${{api.RAILWAY_PRIVATE_DOMAIN}}:${{api.PORT}}
DB_HOST=${{postgres.RAILWAY_PRIVATE_DOMAIN}}
```

### Public Networking

Services do NOT get a public domain by default. You must explicitly generate one.

**Railway-provided domains:** `*.up.railway.app`. Generated in service Settings > Public Networking.

**Custom domains:** Add in service Settings > Public Networking > Custom Domain. Railway provides a CNAME value. Create a CNAME record in your DNS provider pointing to it.

**Domain limits by plan:**
| Plan | Custom Domains per Service |
|------|---------------------------|
| Trial | 1 |
| Hobby | 2 |
| Pro | 20 (can request increase) |

**Wildcard domains:** Supported at any subdomain level (`*.example.com`, `*.sub.example.com`). Nested wildcards (`*.*.example.com`) are NOT supported. Railway provides two CNAME records — one for the wildcard and one for `_acme-challenge` (SSL verification).

**Target ports (Magic Ports):** Map different domains to different ports on the same service:
- `https://example.com/` -> `:8080`
- `https://admin.example.com/` -> `:9000`

### SSL/TLS

- Automatic Let's Encrypt certificates for all custom domains
- RSA 2048-bit keys
- 90-day validity, auto-renewed at 30 days remaining
- Typically issued within an hour of DNS setup
- External/custom SSL certificates NOT supported

**Cloudflare-specific:**
- If proxying (orange cloud), set SSL/TLS to **Full** (NOT Full Strict)
- Without proxying, you may see `ERR_TOO_MANY_REDIRECTS`
- For wildcard domains on Cloudflare: enable Universal SSL and Full encryption

### Root/Apex Domain Configuration

DNS standards require A/AAAA records at the root level, but Railway only provides CNAMEs. Solutions:
- Use a DNS provider that supports **CNAME flattening**: Cloudflare, DNSimple, Namecheap, bunny.net
- If your provider doesn't support it (AWS Route 53, GoDaddy, Hostinger, Azure DNS), switch nameservers to Cloudflare

### TCP Proxy

For non-HTTP protocols (databases, game servers, IoT, raw TCP):
- Assigned a unique domain + port (e.g., `shuttle.proxy.rlwy.net:15140`)
- Supports custom domains via CNAME
- Can coexist with HTTP domains on the same service
- Required for external access to databases

### Public Network Specs and Limits

| Spec | Limit |
|------|-------|
| Max concurrent connections per domain | 10,000 |
| Max requests per second per domain | ~11,000 |
| Max combined header size | 32 KB |
| Max HTTP request duration | 15 minutes |
| WebSocket support | Yes (HTTP/1.1) |
| HTTP/2 | Yes (from internet to edge) |
| TLS versions | 1.2 and 1.3 |
| Proxy keep-alive timeout | 60 seconds |

### DDoS Protection

Railway added DDoS protection in Feb 2026. For additional protection, place Cloudflare or a similar WAF in front of public-facing services.

---

## Databases

### Managed Database Templates

Railway provides one-click database deployment templates:

| Database | Template | Notes |
|----------|----------|-------|
| PostgreSQL | Official | Most popular. HA option available (auto-failover). |
| MySQL | Official | Standard MySQL deployment. |
| Redis | Official | In-memory data store. HA with Sentinel available via template. |
| MongoDB | Official | Document database. |

Any Docker-based database works too: ClickHouse, CockroachDB, TimescaleDB, InfluxDB, Neo4j, Cassandra, etc.

### Key Features

- Persistent volumes for data durability (auto-attached)
- TCP Proxy for external connectivity
- Private networking for internal service connections (free, no egress)
- Database View in dashboard for running queries (expanded to all DB types in Mar 2026)
- DB Metrics dashboard (CPU, memory, disk, connections)
- Volume backups for point-in-time recovery

### Important Caveats

These are NOT fully managed databases like AWS RDS or MongoDB Atlas:
- **You** are responsible for backups, disaster recovery, performance tuning, and security hardening
- No automatic failover (except HA Postgres template)
- No automated patch management
- For compliance-critical workloads, consider external managed database services

### Connecting to Databases

**From other Railway services (private network):**
```
DATABASE_URL=postgresql://user:pass@${{postgres.RAILWAY_PRIVATE_DOMAIN}}:5432/railway
```

**From external clients (TCP Proxy):**
```
DATABASE_URL=postgresql://user:pass@shuttle.proxy.rlwy.net:15140/railway
```

**From CLI:**
```bash
railway connect postgres   # Opens interactive psql/mongosh/redis-cli session
```

---

## Storage

### Volumes

Persistent disk storage that survives deployments and restarts.

- Mount at any path inside the container (e.g., `/data`, `/var/lib/postgresql/data`)
- Ephemeral storage: 1 GB (free), 100 GB (paid plans)
- Volume storage: $0.15/GB/month
- Zero-downtime volume resizing (as of Jan 2026)
- Volume backups available for disaster recovery

### Buckets (S3-Compatible Object Storage)

GA since Nov 2025. Private, S3-compatible object storage.

**Use cases:** File uploads, user-generated content, static assets, backups.

**Pricing:**
| Item | Cost |
|------|------|
| Storage | $0.015/GB-month |
| Egress (from bucket) | Free |
| API operations | Free (unlimited) |
| Service egress (serving files through your app) | $0.05/GB |

**Creating:** Canvas > New > Bucket > Select region. Region cannot be changed post-creation.

**Accessing:** S3-compatible credentials available in the Credentials tab. Works with any S3 SDK (AWS SDK, Bun, FastAPI, Laravel, etc.).

**Available credentials:** `BUCKET`, `SECRET_ACCESS_KEY`, `ACCESS_KEY_ID`, `REGION`, `ENDPOINT`

**Supported operations:** Put, Get, Head, Delete, List, Copy, Presigned URLs, Object tagging, Multipart uploads.

**NOT supported:** Server-side encryption, versioning, object locks, lifecycle configuration.

**Environment isolation:** Each environment gets isolated bucket instances with separate credentials.

---

## Functions

Lightweight TypeScript services running on Bun. No repo, no build step.

- Deploy code changes in seconds
- Built-in code editor with syntax highlighting
- Supports any NPM package with auto-install (pin versions: `import { Hono } from "hono@4"`)
- Access service variables via `import.meta.env`, `process.env`, or `Bun.env`
- Volume attachment for persistent storage
- Automatic versioning with rollback support

**Constraints:**
- Single file per function
- Maximum file size: 96 KB

**Best for:** Webhook handlers, scheduled tasks, simple APIs, prototyping.

---

## Monorepo Support

### Pattern 1: Isolated Components (No Shared Code)

Each service lives in a subdirectory with no shared dependencies.

**Setup per service:**
1. Create a service in the project
2. Set **Root Directory** in Settings (e.g., `/frontend`, `/backend`, `/worker`)
3. Set **Watch Paths** to only trigger on relevant file changes
4. Optionally place a `railway.json` in each service's root directory

**Example project structure:**
```
my-monorepo/
├── frontend/
│   ├── railway.json
│   ├── Dockerfile
│   └── src/
├── backend/
│   ├── railway.json
│   ├── Dockerfile
│   └── src/
└── worker/
    ├── railway.json
    ├── Dockerfile
    └── src/
```

### Pattern 2: JavaScript Workspaces (pnpm/yarn/bun)

For monorepos using package managers with workspace support, Railway auto-detects packages when importing.

**What Railway auto-configures per package:**
- Service name (from `package.json` name)
- Start command (e.g., `pnpm --filter [package] start`)
- Build command
- Watch paths
- Config as Code file detection

**Workspace managers supported:** pnpm, npm, yarn, bun.

### Watch Paths

Prevent unnecessary rebuilds by specifying which file changes should trigger a service's build.

```json
{
  "build": {
    "watchPatterns": [
      "/packages/backend/**",
      "/shared/**",
      "package.json"
    ]
  }
}
```

Gitignore-style patterns. Only changes matching at least one pattern trigger a rebuild.

### Focused PR Environments (Jan 2026)

For monorepo PRs, only services affected by changed files are deployed. Unaffected services are skipped (but can be manually deployed). This speeds up PR environments and reduces resource usage.

### CLI with Monorepos

Link to a specific service before running commands:
```bash
cd my-monorepo
railway link           # Select the specific service
railway up             # Deploys only the linked service
railway up ./backend   # Or specify subdirectory explicitly
```

---

## Scaling and Regions

### Horizontal Scaling (Replicas)

Scale services to multiple instances:

```bash
railway scale             # Interactive
```

Or via config:
```json
{
  "deploy": {
    "multiRegionConfig": {
      "us-west2": { "numReplicas": 2 }
    }
  }
}
```

**Replica limits by plan:**
| Plan | Max Replicas |
|------|-------------|
| Hobby | 6 |
| Pro | 42 |
| Enterprise | 50 |

**Deploy-less scaling** (Feb 2026): Scale replicas up/down without triggering a new deployment.

### Multi-Region Deployment

Deploy replicas across multiple regions:

```json
{
  "deploy": {
    "multiRegionConfig": {
      "us-west2": { "numReplicas": 2 },
      "us-east4-eqdc4a": { "numReplicas": 2 },
      "europe-west4-drams3a": { "numReplicas": 1 },
      "asia-southeast1-eqsg3a": { "numReplicas": 1 }
    }
  }
}
```

### Available Regions

Railway operates in multiple regions globally. Key regions include:
- US West (us-west2)
- US East (us-east4-eqdc4a)
- Europe West (europe-west4-drams3a)
- Asia Southeast / Singapore (asia-southeast1-eqsg3a)

Check docs for the full list, as new regions are added regularly.

### App Sleep

For cost optimization on multi-region standby services, App Sleep pauses inactive instances and wakes them on incoming requests. Adds cold-start latency but reduces costs.

---

## Pricing

### Plans

| Plan | Monthly Fee | Included Credits | Best For |
|------|-------------|-----------------|----------|
| Free Trial | $0 | $5 one-time | Testing, evaluation |
| Hobby | $5/mo | $5/mo | Side projects, personal apps |
| Pro | $20/mo/seat | $20/mo | Teams, production workloads |
| Enterprise | Custom | Custom | Compliance, SSO, RBAC |

### Resource Pricing (Beyond Included Credits)

| Resource | Cost |
|----------|------|
| vCPU | $20/vCPU/month (billed per minute) |
| Memory | $10/GB/month (billed per minute) |
| Network Egress | $0.05/GB |
| Volume Storage | $0.15/GB/month |
| Bucket Storage | $0.015/GB/month |
| Bucket Egress | Free |
| Bucket API Operations | Free (unlimited) |

### Plan Limits

| Limit | Hobby | Pro | Enterprise |
|-------|-------|-----|-----------|
| Max vCPU per service | 48 | 1,000 | 2,400 |
| Max RAM per service | 48 GB | 1 TB | 2.4 TB |
| Max replicas | 6 | 42 | 50 |
| Custom domains per service | 2 | 20 | Custom |
| Image retention (rollback) | 72 hours | Longer | Custom |
| Private registries | No | Yes | Yes |
| Environment RBAC | No | No | Yes |
| SAML SSO | No | No | Yes |
| Audit logs | No | No | Yes |

### Billing Details

- Billed by the minute for compute (CPU + RAM)
- No charge per service count — only actual resource consumption
- Included credits do NOT roll over between billing cycles
- Private networking traffic is free
- Cron jobs billed only during execution time
- PR environments consume resources while active
- Invoices under $0.50 are deferred
- Only credit cards accepted (Enterprise: custom invoicing)

### Cost Optimization Tips

- Use private networking for database connections (free, no egress)
- Use cron jobs instead of always-on scheduled workers
- Enable App Sleep for low-traffic multi-region standby services
- Use Focused PR Environments to deploy only affected services in monorepo PRs
- Monitor estimated usage in Workspace Settings > Usage

---

## Production Readiness Checklist

Railway's official checklist for production deployments:

### Performance and Reliability
- [ ] Deploy to the region closest to your users
- [ ] Use private networking for all service-to-service communication
- [ ] Configure appropriate restart policy (ON_FAILURE recommended)
- [ ] Run at least 2 replicas for critical services
- [ ] Review vCPU and memory allocation for your workload
- [ ] Use HA database configurations (e.g., HA Postgres template, Redis Sentinel)

### Observability and Monitoring
- [ ] Use Log Explorer for centralized cross-service log querying
- [ ] Enable deployment notifications (email/in-app)
- [ ] Configure webhooks for external alerting (Slack, Discord, PagerDuty)

### Quality Assurance
- [ ] Configure Check Suites to gate deploys on CI passing
- [ ] Maintain separate production and staging environments
- [ ] Enable PR environments for pre-merge testing
- [ ] Track Railway config in code (railway.json or railway.toml)
- [ ] Understand rollback capabilities and test the process

### Security
- [ ] Keep backend services off the public network — use private networking
- [ ] Place Cloudflare or similar WAF in front of public services
- [ ] Seal sensitive variables (write-only, hidden from UI/API)
- [ ] Enable 2FA enforcement for the workspace
- [ ] Use environment RBAC for sensitive environments (Enterprise)

### Disaster Recovery
- [ ] Consider multi-region deployment for critical services
- [ ] Enable and schedule volume backups
- [ ] Document recovery procedures

---

## Recent Platform Updates

Railway ships weekly. Notable updates from 2025-2026:

### March 2026
- **One-click CDN** — simplified CDN deployment
- **Railway x Stripe Projects** — Stripe integration for monetized templates
- **HA Postgres improvements** — one-click highly available PostgreSQL
- **New dashboard layout** — redesigned UI
- **DNS management** — buy and manage domains directly in Railway
- **Database queries for all DB types** — expanded DB View
- **Smart Diagnosis** — AI-powered error analysis
- **AI Agent Panel** — automation control panel
- **Buckets in CLI** — manage storage buckets from the command line

### February 2026
- **Smart Diagnosis** — intelligent diagnostic tools for debugging
- **IPv6 public networking support**
- **Agent Skill 2.0** — updated Claude Code plugin for Railway
- **DDoS protection** — built-in mitigation
- **Deploy-less horizontal scaling** — scale replicas without redeploying
- **Magic Domains** — automated domain configuration
- **Chat with Canvas** — conversational UI for project management
- **DB Metrics and Network Flows** — visualization dashboards

### January 2026
- **$100M Series B fundraise**
- **Architecture View** — visual service dependency graph
- **Focused PR Environments** — monorepo-aware PR deploys
- **Railway Agent Skill** — Claude Code integration
- **Login with Railway** — use Railway as an OAuth provider
- **Zero-downtime volume resizing**
- **Enforced 2FA** option for workspaces
- **Singapore Buckets** — object storage in Singapore region

### Late 2025 (October-December)
- **Buckets GA** (Nov) — S3-compatible object storage
- **AI Magic Config** — auto-generate railway.json from repo analysis
- **Restricted Environments / RBAC** (Nov)
- **Audit Logs** (Dec) — activity tracking for enterprise
- **railway dev TUI** (Dec) — local development with Docker Compose integration
- **HA Postgres template** (Dec)
- **Smart Canvas** (Dec) — intelligent visual project editor
- **Enterprise SSO / SAML** (Oct)
- **Metal Builders** (Oct) — bare-metal build infrastructure
- **HTTP Metrics** (Oct) — application performance monitoring
- **Secure DB queries** (Oct) — encrypted database access in dashboard
- **Repo-aware settings** (Oct) — auto-detect config from repository
- **IPv4 Private Networks** (Oct) — previously IPv6 only

---

## External Links

- Railway Docs: https://docs.railway.com
- Railway Changelog: https://railway.com/changelog
- Railway CLI source: https://github.com/railwayapp/cli
- Railway Templates: https://railway.com/templates
- Railway Help Station: https://station.railway.com
- Config JSON Schema: https://railway.com/railway.schema.json
