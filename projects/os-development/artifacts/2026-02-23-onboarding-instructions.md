---
ask: "Provide instructions for a new team member to get set up with the operating system and local development environment"
created: 2026-02-23
workstream: os-development
session: 2026-02-23-a
sources:
  - type: github
    description: "indemn-ai org repo listing, craig-indemn/operating-system onboarding branch"
  - type: web
    description: "Claude Code installation, local-dev.sh, onboarding skill design"
---

# Getting Started with Indemn Development

## Prerequisites (do these first)

1. Get invited to the `indemn-ai` GitHub organization (ask Craig or admin)
2. Install [Claude Code](https://claude.com/claude-code) — this is your primary development tool
3. Download the `.env.dev` file from 1Password (Engineering vault → "Local Dev Environment")
4. **Get your IP whitelisted in MongoDB Atlas** — ask Dhruv or an admin to add your IP to the dev cluster's Network Access list. Run `curl -s ifconfig.me` to get your IP. This is required before any services can connect to the database.
5. **Google Workspace credentials** (optional, for OS tools) — download `google-oauth-credentials.json` from 1Password (Engineering vault → "Google Workspace OAuth — gog CLI")

## Setup (Claude Code does everything)

```bash
# 1. Clone the operating system repo
gh auth login
gh repo clone craig-indemn/operating-system -- -b onboarding
cd operating-system

# 2. Open Claude Code and run the onboarding
claude
```

Then in Claude Code, type:

```
/onboarding engineer
```

Claude Code will:
- Detect your platform and install prerequisites (node, uv, bash 4+, etc.)
- Clone all 13 platform service repos
- Ask you for the `.env.dev` file from 1Password
- Install all dependencies
- Start the platform services
- Verify everything is working

## What you'll end up with

- All Indemn services cloned and configured
- Local dev environment pointing at the dev database
- Services running at `http://localhost:8001` (bot-service), `:8003` (platform), `:5173` (UI), etc.
- Login: `support@indemn.ai` / `nzrjW3tZ9K3YiwtMWzBm`

## Daily usage

```bash
# Start services
bash ./local-dev.sh start platform --env=dev

# Check status
bash ./local-dev.sh status

# Stop everything
bash ./local-dev.sh stop all

# View logs
bash ./local-dev.sh logs bot-service
```

## Service groups

| Group | What it starts | Use case |
|-------|---------------|----------|
| `minimal` | bot-service, evaluations, evaluations-ui | Agent testing |
| `platform` | bot-service, platform-v2, platform-v2-ui, evaluations | Agent builder development |
| `chat` | bot-service, middleware, copilot-server, conversation-service, point-of-sale | End-to-end chat testing |
| `analytics` | observability, observability-ui | Analytics dashboard |

## Troubleshooting

If something goes wrong during onboarding, you can re-run `/onboarding engineer` — it's idempotent (skips what's already done).

For service-specific issues:
- **Port in use:** `lsof -ti :<port> | xargs kill -9`
- **Node service broken:** `cd <service> && rm -rf node_modules && npm install`
- **Python service broken:** `cd <service> && uv sync`
- **MongoDB won't connect:** Check your IP is whitelisted in MongoDB Atlas (Settings → Network Access)
