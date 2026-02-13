---
name: vercel
description: Manage Vercel deployments, environments, and domains using the vercel CLI. Use for deployment and hosting tasks.
---

# Vercel

Deployment management via official `vercel` CLI. Hosts the meetings intelligence system and pipeline API.

## Status Check

```bash
which vercel && echo "INSTALLED" || echo "NOT INSTALLED"
```

```bash
vercel whoami 2>/dev/null && echo "AUTHENTICATED" || echo "NOT AUTHENTICATED"
```

## Setup

### Install
```bash
npm install -g vercel
```

### Authenticate

**Option A: Interactive**
```bash
vercel login
```

**Option B: Token (persistent, for automation)**
1. Vercel Dashboard > Settings > Tokens > Create
2. Set environment variable:
```bash
export VERCEL_TOKEN="..."
```
Note: Tokens expire after 10 days of inactivity.

## Usage

### List Projects
```bash
vercel project ls
```

### Deployment Status
```bash
vercel ls --limit 10
vercel inspect <deployment-url>
```

### Deploy
```bash
vercel deploy              # Preview deployment
vercel deploy --prod       # Production deployment
```

### Environment Variables
```bash
vercel env ls
vercel env pull .env.local
vercel env add SECRET_KEY
```

### Logs
```bash
vercel logs <deployment-url>
vercel logs <deployment-url> --follow
```

### Domains
```bash
vercel domains ls
vercel domains inspect meetings.indemn.ai
```

### Key Projects
- `indemn-pipeline` — Pipeline API (`https://indemn-pipeline.vercel.app/api/*`)
- Meetings intelligence system — deployment in progress (Prisma migration incomplete)
