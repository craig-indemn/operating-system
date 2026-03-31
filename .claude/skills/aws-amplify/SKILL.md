---
name: aws-amplify
description: Deploy and manage frontend apps on AWS Amplify Hosting — React/Vite SPAs, custom domains, PR previews, branch environments. Use when deploying frontend applications or managing Amplify infrastructure.
---

# AWS Amplify Hosting

Deploy and manage frontend apps via `aws amplify` CLI. Indemn uses Amplify Hosting for all customer-facing frontends — React/Vite SPAs with Git-based CI/CD, CloudFront CDN, and custom domains on `indemn.ai`.

## Status Check

```bash
aws amplify list-apps --query 'apps[].name' --output table && echo "AMPLIFY CLI WORKING" || echo "AMPLIFY CLI FAILED"
```

## Setup

### Prerequisites
- AWS CLI v2 installed and authenticated (`aws sts get-caller-identity`)
- GitHub repo in `indemn-ai` org
- No additional tools needed — `aws amplify` is built into the AWS CLI

### Create a New App (Console)
1. Open AWS Amplify Console > **Create new app**
2. Select **GitHub** as source provider
3. Authorize and select the `indemn-ai/<repo>` repository
4. Select branch (typically `main`)
5. Review auto-detected build settings, ensure `baseDirectory: dist` for Vite
6. Deploy

### Create a New App (CLI)

```bash
# Create the app
aws amplify create-app \
  --name "my-app" \
  --repository "https://github.com/indemn-ai/my-app" \
  --platform WEB \
  --iam-service-role-arn "arn:aws:iam::780354157690:role/amplifyconsole-backend-role" \
  --environment-variables VITE_API_URL=https://api.example.com

# Connect a branch
aws amplify create-branch \
  --app-id <app-id> \
  --branch-name main \
  --stage DEVELOPMENT \
  --enable-auto-build

# Connect production branch
aws amplify create-branch \
  --app-id <app-id> \
  --branch-name prod \
  --stage PRODUCTION \
  --enable-auto-build
```

### Add amplify.yml to Repo (Vite)

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci --cache .npm --prefer-offline
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - .npm/**/*
      - node_modules/**/*
```

### SPA Routing Rule (Required)

Add in Amplify Console > Hosting > Rewrites and redirects:

| Source | Target | Type |
|--------|--------|------|
| `/<*>` | `/index.html` | 404 (Rewrite) |

This serves `index.html` for all routes that would otherwise 404, letting the client-side router handle navigation. All existing Indemn apps use this pattern.

## Usage

### List Apps
```bash
aws amplify list-apps --query 'apps[].{Name:name,Id:appId,Domain:defaultDomain}' --output table
```

### Get App Details
```bash
aws amplify get-app --app-id <app-id>
```

### List Branches
```bash
aws amplify list-branches --app-id <app-id> --query 'branches[].{Name:branchName,Stage:stage,Status:activeJobId}' --output table
```

### Trigger a Build
```bash
aws amplify start-job --app-id <app-id> --branch-name main --job-type RELEASE
```

### Check Build Status
```bash
# List recent jobs
aws amplify list-jobs --app-id <app-id> --branch-name main --max-results 5 \
  --query 'jobSummaries[].{Id:jobId,Status:status,Commit:commitId,StartedAt:startTime}' --output table

# Get specific job details
aws amplify get-job --app-id <app-id> --branch-name main --job-id <job-id>
```

### Environment Variables
```bash
# Set env vars (updates entire map — merge with existing)
aws amplify update-app --app-id <app-id> \
  --environment-variables VITE_API_URL=https://api.example.com,VITE_ENV=production

# Branch-level overrides
aws amplify update-branch --app-id <app-id> --branch-name prod \
  --environment-variables VITE_API_URL=https://api.indemn.ai
```

**Important:** `VITE_*` variables are bundled into the client-side JS at build time. They are NOT runtime secrets. Never put API keys or tokens in `VITE_*` variables.

### Custom Domains
```bash
# List domain associations
aws amplify list-domain-associations --app-id <app-id> \
  --query 'domainAssociations[].{Domain:domainName,Status:domainStatus}' --output table

# Add subdomain (e.g., gic.indemn.ai)
aws amplify create-domain-association \
  --app-id <app-id> \
  --domain-name indemn.ai \
  --sub-domain-settings '[{"prefix":"gic","branchName":"prod"},{"prefix":"devgic","branchName":"main"}]'
```

Since `indemn.ai` is managed in Route 53 (hosted zone `Z06753801TP0QWFKAPKF8`), DNS records are configured automatically. SSL certificates are provisioned via ACM (13-month validity, auto-renew).

### Delete an App
```bash
aws amplify delete-app --app-id <app-id>
```

## Indemn's Existing Apps

| App | App ID | Domain | Branches |
|-----|--------|--------|----------|
| **indemn_website_new_design** | dtcj1bgtehwe7 | indemn.ai, www.indemn.ai, dev.indemn.ai | prod, main |
| **www-eventsguard-mga** | doad5nmc93nu5 | eventguard.ai, www.eventguard.ai, dev.eventguard.ai | prod, main |
| **discovery-chat-ui** | d3neigmx9zhm7s | discovery.indemn.ai, devdiscovery.indemn.ai | prod, main |
| **a2p-compliance-showcase-demo** | d2d7s1wcuvgj1p | a2p.indemn.ai | main |
| **indemn-website-v2** | d3ph1qhzicbpxv | (no custom domain) | — |
| **livekit-ui** | dfb09y54v7muh | (no custom domain) | — |

### Branch Convention
- `main` branch = DEVELOPMENT stage (e.g., `dev.indemn.ai`)
- `prod` branch = PRODUCTION stage (e.g., `indemn.ai`, `www.indemn.ai`)

### DNS
- **indemn.ai** — Route 53 hosted zone `Z06753801TP0QWFKAPKF8`
- **eventguard.ai** — Route 53 hosted zone `Z088799613KMQ5R7SJRHA`

## Key Concepts

- **Platform `WEB`** = static SPA (React/Vite). **`WEB_COMPUTE`** = SSR (Next.js). Always use `WEB` for Indemn's React apps.
- **Atomic deploys** — old version serves until new build is fully deployed.
- **PR previews** — each PR gets a unique URL at `pr-<n>.<appid>.amplifyapp.com`. Enable in Console > Hosting > Previews.
- **`amplify.yml` in repo overrides console build settings.** Keep it in the repo for version control.
- **50-branch limit per app** — includes PR preview branches.

## Detailed Reference

For full `amplify.yml` spec, custom headers, monorepo config, pricing, and domain setup details:
- `references/amplify-guide.md` — comprehensive reference (grep for section headers)
