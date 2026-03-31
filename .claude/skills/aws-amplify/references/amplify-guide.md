# AWS Amplify Hosting — Comprehensive Reference

Detailed reference for AWS Amplify Hosting. The main SKILL.md covers daily commands. This file covers the full specification, edge cases, and deep configuration.

---

## Table of Contents

- [amplify.yml Build Specification](#amplifyyml-build-specification)
- [Environment Variables](#environment-variables)
- [Custom Headers](#custom-headers)
- [Rewrites and Redirects](#rewrites-and-redirects)
- [Custom Domains](#custom-domains)
- [Monorepo Configuration](#monorepo-configuration)
- [PR Previews](#pr-previews)
- [AWS CLI Commands](#aws-cli-commands)
- [Pricing](#pricing)
- [Indemn Existing Apps — Full Details](#indemn-existing-apps--full-details)
- [Amplify Gen 1 vs Gen 2](#amplify-gen-1-vs-gen-2)
- [Troubleshooting](#troubleshooting)

---

## amplify.yml Build Specification

### Full YAML Structure

```yaml
version: 1

env:
  variables:
    KEY: value                  # Available to all phases

backend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npx ampx pipeline-deploy --branch $AWS_BRANCH --app-id $AWS_APP_ID

frontend:
  buildPath: /                  # For monorepos: directory to run install/build from
  phases:
    preBuild:
      commands:
        - npm ci --cache .npm --prefer-offline
    build:
      commands:
        - npm run build
    postBuild:
      commands:
        - echo "Build complete"
  artifacts:
    baseDirectory: dist         # Where build output lives (Vite = dist, CRA = build)
    files:
      - '**/*'                  # Which files to deploy
    discard-paths: yes          # Optional: flatten directory structure
  cache:
    paths:
      - .npm/**/*
      - node_modules/**/*

test:
  phases:
    preTest:
      commands: []
    test:
      commands:
        - npm test
    postTest:
      commands: []
  artifacts:
    files:
      - location
    configFilePath: location
    baseDirectory: location

# Top-level hooks (not under frontend/backend)
hooks:
  postDeploy:
    - echo "Deployed successfully"
```

### Field Reference

| Field | Description |
|-------|-------------|
| `version` | Always `1` |
| `appRoot` | For monorepos — path to the app within the repo |
| `env.variables` | Key-value pairs available to all build phases |
| `backend` | Amplify CLI commands for backend provisioning (Gen 1/Gen 2) |
| `frontend.buildPath` | Where to run commands from (default: app root) |
| `frontend.phases.preBuild` | Runs before build, after dependencies available |
| `frontend.phases.build` | Your build commands |
| `frontend.phases.postBuild` | Runs after build completion and artifact copying |
| `frontend.artifacts.baseDirectory` | Directory containing build output |
| `frontend.artifacts.files` | File patterns to deploy (use `**/*` for all) |
| `frontend.artifacts.discard-paths` | Flatten directory structure (yes/no) |
| `frontend.cache.paths` | Paths cached between builds (relative to project root) |
| `test` | Test phase — runs after frontend build |
| `hooks.postDeploy` | Commands run after successful deployment |

### Cache Rules

- Paths are relative to project root
- Cannot traverse outside the project root (no `../`)
- Cached on first build, restored on subsequent builds
- Common paths: `node_modules/**/*`, `.npm/**/*`, `.next/cache/**/*`

### Indemn Standard amplify.yml (Vite + React)

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

---

## Environment Variables

### Two Distinct Types

1. **Amplify environment variables** — set in Console > Hosting > Environment variables. Available during build process. Encrypted at rest. Max 5,500 chars per value. Cannot start with `AWS` prefix.

2. **Framework-prefixed variables** (`VITE_*` for Vite, `REACT_APP_*` for CRA) — bundled into the client-side JavaScript at build time. Visible to end users in the browser. NEVER put secrets here.

### Built-In Variables (Available During Build)

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_APP_ID` | Current app ID | `d2d7s1wcuvgj1p` |
| `AWS_BRANCH` | Branch name | `main` |
| `AWS_COMMIT_ID` | Commit ID (or "HEAD" for rebuilds) | `abc123` |
| `AWS_JOB_ID` | Job ID (zero-padded) | `0000000001` |
| `AWS_CLONE_URL` | Git clone URL | `git@github.com:indemn-ai/app.git` |
| `AWS_PULL_REQUEST_ID` | PR number (only during PR builds) | `42` |
| `AWS_PULL_REQUEST_SOURCE_BRANCH` | PR source branch | `feature-x` |
| `AWS_PULL_REQUEST_DESTINATION_BRANCH` | PR target branch | `main` |

### Special Control Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `_BUILD_TIMEOUT` | Build timeout in minutes (5-120) | `30` |
| `USER_DISABLE_TESTS` | Skip test step during build | `true` |
| `AMPLIFY_DIFF_DEPLOY` | Enable diff-based deploy (skip if no changes) | `true` |
| `AMPLIFY_DIFF_DEPLOY_ROOT` | Root path for diff comparisons | `dist` |
| `AMPLIFY_MONOREPO_APP_ROOT` | Monorepo app root path | `apps/frontend` |
| `AMPLIFY_ENABLE_DEBUG_OUTPUT` | Print stack traces for debugging | `true` |
| `_LIVE_UPDATES` | Upgrade build tools to latest version | `[{"name":"Node.js","pkg":"nvm","type":"nvm","version":"18"}]` |

### Setting Variables via CLI

```bash
# App-level (all branches inherit)
aws amplify update-app --app-id <app-id> \
  --environment-variables VITE_API_URL=https://api.indemn.ai,VITE_ENV=production

# Branch-level override
aws amplify update-branch --app-id <app-id> --branch-name main \
  --environment-variables VITE_API_URL=https://dev-api.indemn.ai,VITE_ENV=development

# Read current variables
aws amplify get-app --app-id <app-id> --query 'app.environmentVariables'
aws amplify get-branch --app-id <app-id> --branch-name main --query 'branch.environmentVariables'
```

### Secrets

Do NOT store secrets in environment variables (they appear in build logs). For secrets:
- **Gen 2 apps**: Use Amplify's Secret management feature
- **Gen 1/Hosting-only**: Store in AWS Systems Manager Parameter Store and read during build:
  ```yaml
  preBuild:
    commands:
      - export SECRET=$(aws ssm get-parameter --name /dev/app/secret --with-decryption --query Parameter.Value --output text)
  ```

### Node.js Version

Override the default Node.js version:
```yaml
frontend:
  phases:
    preBuild:
      commands:
        - nvm install 20
        - nvm use 20
        - npm ci
```

Or use `_LIVE_UPDATES`:
```json
[{"name":"Node.js","pkg":"nvm","type":"nvm","version":"20"}]
```

---

## Custom Headers

### customHttp.yml

Place in project root. Overrides console-configured headers.

```yaml
customHeaders:
  - pattern: '**'
    headers:
      - key: 'Strict-Transport-Security'
        value: 'max-age=31536000; includeSubDomains'
      - key: 'X-Frame-Options'
        value: 'SAMEORIGIN'
      - key: 'X-XSS-Protection'
        value: '1; mode=block'
      - key: 'X-Content-Type-Options'
        value: 'nosniff'
      - key: 'Content-Security-Policy'
        value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.indemn.ai https://*.amazonaws.com; font-src 'self' data:;"

  - pattern: '/assets/*'
    headers:
      - key: 'Cache-Control'
        value: 'public, max-age=31536000, immutable'

  - pattern: '/index.html'
    headers:
      - key: 'Cache-Control'
        value: 'no-cache, no-store, must-revalidate'
```

### Cache-Control Details

- Default CDN `s-maxage`: 31,536,000 seconds (1 year)
- `s-maxage` controls CDN edge caching; `max-age` controls browser caching
- Custom Cache-Control only applies to 200 OK responses
- Vite hashed assets (`/assets/index-abc123.js`) should use `immutable` — the hash changes on rebuild
- `index.html` should use `no-cache` so browsers always fetch the latest version (which references the correct hashed assets)

### Security Headers Checklist

| Header | Purpose | Recommended Value |
|--------|---------|-------------------|
| `Strict-Transport-Security` | Force HTTPS | `max-age=31536000; includeSubDomains` |
| `X-Frame-Options` | Prevent clickjacking | `SAMEORIGIN` |
| `X-XSS-Protection` | XSS filter | `1; mode=block` |
| `X-Content-Type-Options` | Prevent MIME sniffing | `nosniff` |
| `Content-Security-Policy` | Content restrictions | App-specific (see above) |
| `Referrer-Policy` | Control referrer info | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Restrict browser features | `camera=(), microphone=(), geolocation=()` |

**Note:** None of the existing Indemn Amplify apps have custom headers configured. This is an opportunity to improve security posture.

---

## Rewrites and Redirects

### SPA Routing (Required for React Router)

**Simple rule (Indemn standard):**
```json
[
  {
    "source": "/<*>",
    "target": "/index.html",
    "status": "404-200",
    "condition": null
  }
]
```

This returns `index.html` with 200 status for any path that would otherwise 404. The client-side router then handles the route.

**Regex rule (more precise, excludes static files):**
```json
[
  {
    "source": "</^[^.]+$|\\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json|webp)$)([^.]+$)/>",
    "target": "/index.html",
    "status": "200",
    "condition": null
  }
]
```

### Redirect Types

| Status | Type | Use Case |
|--------|------|----------|
| `301` | Permanent redirect | Old URL to new URL (cached by browsers) |
| `302` | Temporary redirect | Temporary URL change |
| `200` | Rewrite | Proxy requests without URL change (CORS workaround) |
| `404-200` | Custom | Serve index.html for missing routes (SPA) |
| `404` | Not found | Custom 404 page |

### Common Patterns

```json
[
  {"source": "/old-page", "target": "/new-page", "status": "301"},
  {"source": "/api/<*>", "target": "https://api.indemn.ai/<*>", "status": "200"},
  {"source": "/<*>", "target": "/index.html", "status": "404-200"}
]
```

**Rule ordering matters** — Amplify evaluates top to bottom, first match wins. Put specific redirects before the SPA catch-all.

### API Proxy (CORS Workaround)

200 rewrites can proxy API requests to avoid CORS:
```json
[
  {
    "source": "/api/<*>",
    "target": "https://api.indemn.ai/<*>",
    "status": "200"
  }
]
```
The browser sees the request going to `gic.indemn.ai/api/...` while Amplify proxies to the external API.

### CLI Commands

```bash
# Get current redirect rules (returns JSON)
aws amplify get-app --app-id <app-id> --query 'app.customRules'

# Update redirect rules
aws amplify update-app --app-id <app-id> \
  --custom-rules '[{"source":"/<*>","target":"/index.html","status":"404-200"}]'
```

---

## Custom Domains

### Indemn's DNS (Route 53)

Both primary domains are managed in Route 53:
- **indemn.ai** — Hosted zone `Z06753801TP0QWFKAPKF8`
- **eventguard.ai** — Hosted zone `Z088799613KMQ5R7SJRHA`

Since Route 53 manages these domains, Amplify configures DNS records automatically when you add a custom domain.

### Current Domain Mapping

| Subdomain | App | Branch |
|-----------|-----|--------|
| `indemn.ai` (root) | indemn_website_new_design | prod |
| `www.indemn.ai` | indemn_website_new_design | prod |
| `dev.indemn.ai` | indemn_website_new_design | main |
| `a2p.indemn.ai` | a2p-compliance-showcase-demo | main |
| `discovery.indemn.ai` | discovery-chat-ui | prod |
| `devdiscovery.indemn.ai` | discovery-chat-ui | main |
| `eventguard.ai` (root) | www-eventsguard-mga | prod |
| `www.eventguard.ai` | www-eventsguard-mga | prod |
| `dev.eventguard.ai` | www-eventsguard-mga | main |

### Adding a Custom Domain (CLI)

```bash
# Add subdomain on indemn.ai
aws amplify create-domain-association \
  --app-id <app-id> \
  --domain-name indemn.ai \
  --sub-domain-settings '[
    {"prefix":"gic","branchName":"prod"},
    {"prefix":"devgic","branchName":"main"}
  ]'

# Check domain status
aws amplify get-domain-association --app-id <app-id> --domain-name indemn.ai \
  --query 'domainAssociation.{Status:domainStatus,Subdomains:subDomains[].{Prefix:subDomainSetting.prefix,Branch:subDomainSetting.branchName,Verified:verified}}'

# Update subdomain mapping
aws amplify update-domain-association \
  --app-id <app-id> \
  --domain-name indemn.ai \
  --sub-domain-settings '[{"prefix":"gic","branchName":"prod"}]'

# Delete domain association
aws amplify delete-domain-association --app-id <app-id> --domain-name indemn.ai
```

### SSL Certificates

- Amplify provisions SSL via AWS Certificate Manager automatically
- Certificates are valid for 13 months and auto-renew
- Requires the CNAME verification record to remain in DNS
- All traffic served via HTTPS/2

### Third-Party DNS (Not Route 53)

If the domain is NOT in Route 53, you must manually configure DNS:

1. **CNAME for verification**: `_<hash>.example.com` -> ACM validation value
2. **CNAME for subdomain**: `www` -> `d111111abcdef8.cloudfront.net`
3. **ANAME/ALIAS for root**: `example.com` -> Amplify CloudFront domain

Verification can take up to 48 hours. Complete DNS updates immediately after adding the domain.

### Automatic Subdomains for Branches

For Route 53 domains, Amplify can auto-create subdomains for every connected branch:
```bash
aws amplify create-domain-association \
  --app-id <app-id> \
  --domain-name indemn.ai \
  --auto-sub-domain-creation-patterns '["*"]' \
  --auto-sub-domain-iam-role "arn:aws:iam::780354157690:role/amplifyconsole-backend-role" \
  --sub-domain-settings '[{"prefix":"app","branchName":"prod"}]'
```

This creates `<branch>.app.indemn.ai` automatically for new branches.

---

## Monorepo Configuration

### When to Use

When the frontend lives in a subdirectory of a larger repo (e.g., `ui/` or `apps/frontend/`).

### Setup

1. Set `AMPLIFY_MONOREPO_APP_ROOT` env var to the subdirectory path
2. Or check "My app is a monorepo" during initial console setup

### amplify.yml for Monorepo

```yaml
version: 1
applications:
  - appRoot: ui
    frontend:
      buildPath: /
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build --workspace=ui
      artifacts:
        baseDirectory: ui/dist
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
```

### Key Fields

- `appRoot` — subdirectory containing the app
- `buildPath: /` — run install from repo root (for workspace dependency resolution)
- `baseDirectory` — path to build output relative to repo root

### Package Manager Support

**npm workspaces**: Works out of the box.

**pnpm**: Add `.npmrc` with `node-linker=hoisted` and install pnpm in preBuild:
```yaml
preBuild:
  commands:
    - npm install -g pnpm
    - pnpm install --frozen-lockfile
```

**Turborepo**: Amplify auto-detects. Use `turbo build --filter=ui` in build commands.

**Nx**: Amplify auto-detects. Use `npx nx build ui` in build commands.

---

## PR Previews

### Setup

1. Open Amplify Console > Hosting > Previews
2. Install the Amplify GitHub App (not OAuth — the GitHub App)
3. Select which branches get PR previews enabled
4. Configure access control (optional password protection)

### How It Works

- Each PR gets a unique URL: `pr-<number>.<appid>.amplifyapp.com`
- Preview URL is posted as a status check on the GitHub PR
- Preview is built using the branch's environment variables
- When the PR is merged or closed, the preview is deleted automatically

### Limitations

- Each PR preview counts toward the 50-branch-per-app limit
- PR previews are not available with AWS CodeCommit (not relevant — Indemn uses GitHub)
- Build notifications for PR previews use the same webhook as branch builds

### CLI (No direct CLI for previews — use console)

PR previews are configured in the console. The underlying mechanism creates temporary branches, which can be listed:
```bash
aws amplify list-branches --app-id <app-id> \
  --query 'branches[?contains(branchName, `pr-`)].{Name:branchName,Stage:stage}' --output table
```

---

## AWS CLI Commands

### Complete Command Reference

**App Management:**
```bash
aws amplify create-app           # Create new app
aws amplify get-app              # Get app details
aws amplify list-apps            # List all apps
aws amplify update-app           # Update app settings (env vars, build spec, redirects)
aws amplify delete-app           # Delete app
```

**Branch Management:**
```bash
aws amplify create-branch        # Connect a branch
aws amplify get-branch           # Get branch details
aws amplify list-branches        # List all branches for an app
aws amplify update-branch        # Update branch settings (env vars, stage)
aws amplify delete-branch        # Disconnect a branch
```

**Domain Management:**
```bash
aws amplify create-domain-association    # Add custom domain
aws amplify get-domain-association       # Get domain status
aws amplify list-domain-associations     # List domains for an app
aws amplify update-domain-association    # Update domain config
aws amplify delete-domain-association    # Remove custom domain
```

**Jobs (Builds/Deployments):**
```bash
aws amplify start-job            # Trigger a build (--job-type RELEASE)
aws amplify stop-job             # Cancel a running build
aws amplify get-job              # Get build details (steps, logs)
aws amplify list-jobs            # List recent builds
aws amplify delete-job           # Delete a build record
```

**Deployments (Manual — for CI/CD pipelines):**
```bash
aws amplify create-deployment    # Create deployment (returns upload URL + zipUploadUrl)
aws amplify start-deployment     # Start deploying uploaded artifacts
```

**Webhooks:**
```bash
aws amplify create-webhook       # Create build trigger webhook
aws amplify get-webhook          # Get webhook URL
aws amplify list-webhooks        # List webhooks for an app
aws amplify update-webhook       # Update webhook branch target
aws amplify delete-webhook       # Delete webhook
```

**Other:**
```bash
aws amplify get-artifact-url     # Get download URL for build artifact
aws amplify list-artifacts       # List artifacts for a job
aws amplify generate-access-logs # Generate access logs for a domain
aws amplify tag-resource         # Tag an Amplify resource
aws amplify untag-resource       # Remove tags
aws amplify list-tags-for-resource  # List tags
```

### Useful Query Patterns

```bash
# All apps with their default domains
aws amplify list-apps --query 'apps[].{Name:name,Id:appId,Domain:defaultDomain,Repo:repository}' --output table

# All branches for an app with their stages
aws amplify list-branches --app-id <id> \
  --query 'branches[].{Branch:branchName,Stage:stage,AutoBuild:enableAutoBuild,LastDeploy:updateTime}' --output table

# Last 5 builds with status
aws amplify list-jobs --app-id <id> --branch-name main --max-results 5 \
  --query 'jobSummaries[].{Id:jobId,Status:status,Type:jobType,Started:startTime,Ended:endTime}' --output table

# All custom domains across all apps
for id in $(aws amplify list-apps --query 'apps[].appId' --output text); do
  echo "=== $id ==="
  aws amplify list-domain-associations --app-id "$id" \
    --query 'domainAssociations[].{Domain:domainName,Status:domainStatus}' --output table 2>/dev/null
done
```

---

## Pricing

### Free Tier (12 months)

| Resource | Free Amount |
|----------|-------------|
| Build minutes | 1,000/month |
| CDN storage | 5 GB |
| Data transfer out | 15 GB/month |
| SSR requests | 500,000/month |
| SSR duration | 100 GB-hours/month |

### After Free Tier

| Resource | Cost |
|----------|------|
| **Build minutes (Standard)** — 8GB RAM, 4 vCPU | $0.01/minute |
| **Build minutes (Large)** — 16GB RAM, 8 vCPU | $0.025/minute |
| **Build minutes (XLarge)** — 72GB RAM, 36 vCPU | $0.10/minute |
| **CDN storage** | $0.023/GB/month |
| **Data transfer out** | $0.15/GB served |
| **SSR requests** | $0.30/million requests |
| **SSR duration** | $0.20/GB-hour |
| **WAF (optional)** | $15/month/app + standard WAF charges |

### Cost Estimate for a Typical Indemn App

- **Builds**: ~20 deploys/month x 2 min avg = 40 min = $0.40/month
- **Storage**: ~50MB build output = $0.001/month
- **Transfer**: ~1GB/month (low-traffic internal tool) = $0.15/month
- **Total**: Under $1/month for a typical internal-facing SPA

Team collaboration is always free with no per-seat charges.

---

## Indemn Existing Apps — Full Details

### indemn_website_new_design (dtcj1bgtehwe7)

- **Repository**: `indemn-ai/indemn_website_new_design`
- **Domains**: `indemn.ai` (root), `www.indemn.ai`, `dev.indemn.ai`
- **Branches**: `prod` (PRODUCTION), `main` (DEVELOPMENT)
- **Notable**: Has Slack notification in postDeploy hook

### www-eventsguard-mga (doad5nmc93nu5)

- **Repository**: `indemn-ai/www-eventsguard-mga`
- **Domains**: `eventguard.ai` (root), `www.eventguard.ai`, `dev.eventguard.ai`
- **Branches**: `prod` (PRODUCTION), `main` (DEVELOPMENT)
- **Notable**: Uses both the simple `404-200` and the regex SPA rewrite rules

### discovery-chat-ui (d3neigmx9zhm7s)

- **Repository**: `indemn-ai/discovery-chat-ui`
- **Domains**: `discovery.indemn.ai`, `devdiscovery.indemn.ai`
- **Branches**: `prod` (PRODUCTION), `main` (DEVELOPMENT)

### a2p-compliance-showcase-demo (d2d7s1wcuvgj1p)

- **Repository**: `indemn-ai/a2p-compliance-showcase-demo`
- **Domains**: `a2p.indemn.ai`
- **Branches**: `main` only (demo app, no prod/dev split)

### indemn-website-v2 (d3ph1qhzicbpxv)

- **Repository**: `indemn-ai/indemn-website-v2`
- **Domains**: None (uses default Amplify domain only)
- **Status**: Likely superseded by `indemn_website_new_design`

### livekit-ui (dfb09y54v7muh)

- **Repository**: `indemn-ai/livekit-ui`
- **Domains**: None (uses default Amplify domain only)
- **Notable**: Generates `.env.production` from Amplify env vars during preBuild

---

## Amplify Gen 1 vs Gen 2

### What They Are

- **Amplify Hosting** — the deployment/hosting service. Git-based CI/CD, CDN, custom domains, PR previews. This is what Indemn uses for all frontend apps.
- **Amplify Gen 1** — the older CLI-driven backend provisioning (`amplify init`, `amplify add api`, CloudFormation). Uses `amplify/` directory with JSON config.
- **Amplify Gen 2** — the newer TypeScript-first backend definition. Code-first, uses CDK under the hood. `amplify/` directory with TypeScript files (`backend.ts`, `auth/resource.ts`, `data/resource.ts`).

### For Indemn

Indemn uses **Amplify Hosting only** — no Amplify backend provisioning. The backends are custom services (bot-service, platform-v2, etc.) deployed on EC2.

You do NOT need:
- The Amplify CLI (`npm install -g @aws-amplify/cli`)
- The `amplify/` directory
- Any `@aws-amplify/*` npm packages (unless the frontend uses Amplify UI components)
- Gen 2 `defineBackend()` or `defineAuth()`

You only need:
- `aws amplify` (part of AWS CLI v2) for infrastructure management
- `amplify.yml` in the repo root for build configuration
- Optionally `customHttp.yml` for custom headers

---

## Troubleshooting

### Build Fails — "Module not found"

Check that `preBuild` runs `npm ci` (not `npm install`) and that `package-lock.json` is committed. If using pnpm, ensure `.npmrc` has `node-linker=hoisted`.

### 404 on Page Refresh

Missing SPA rewrite rule. Add the `404-200` redirect:
```json
{"source": "/<*>", "target": "/index.html", "status": "404-200"}
```

### Build Succeeds but App Shows Old Version

- Check `index.html` Cache-Control — should be `no-cache`
- Amplify CDN may be serving cached content. Trigger a cache invalidation by re-deploying or wait for `s-maxage` to expire.
- Verify the correct branch was deployed (`aws amplify list-jobs`)

### Environment Variables Not Available at Runtime

`VITE_*` variables are compile-time only. They are baked into the bundle during `npm run build`. If you change an env var, you must trigger a new build.

### Custom Domain Stuck in "Pending Verification"

- For Route 53 domains: Usually resolves within minutes. If stuck, check the hosted zone for missing CNAME records.
- For third-party DNS: Ensure CNAME verification record is correctly configured. Propagation can take up to 48 hours.
- If stuck for days, delete the domain association and re-add it.

### Build Timeout

Default is 30 minutes. Increase with:
```bash
aws amplify update-app --app-id <app-id> \
  --environment-variables _BUILD_TIMEOUT=60
```

### Debug Build Issues

Enable verbose output:
```bash
aws amplify update-app --app-id <app-id> \
  --environment-variables AMPLIFY_ENABLE_DEBUG_OUTPUT=true
```

### Node.js Version Mismatch

Amplify may use a different Node version than your local environment. Pin it:
```yaml
preBuild:
  commands:
    - nvm install 20
    - nvm use 20
```

### Branch Auto-Build Not Triggering

- Verify the branch has `enableAutoBuild: true`
- Check that the GitHub App (not OAuth) is installed for PR builds
- Check the webhook: `aws amplify list-webhooks --app-id <app-id>`
