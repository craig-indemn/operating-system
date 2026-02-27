---
name: local-dev
description: Start, stop, and manage Indemn platform services locally. Use when testing features, debugging issues, or running the full stack for development. Covers service groups, federation builds, and log management.
---

# Local Dev

Run Indemn services locally via `local-dev.sh`. All infrastructure (MongoDB, Redis, RabbitMQ) is remote — only application services run on your machine.

## Status Check

Find the workspace directory (where `local-dev.sh` lives) and run:

```bash
# Find workspace — check common locations
WORKSPACE="${INDEMN_WORKSPACE:-$(dirname "$(find ~/Repositories ~/code ~/dev ~/Projects -name 'local-dev.sh' -maxdepth 1 2>/dev/null | head -1)" 2>/dev/null)}"
cd "$WORKSPACE" && bash ./local-dev.sh status
# macOS with bash 3: bash ./local-dev.sh status
```

## Prerequisites

- bash 4+ (`brew install bash`) — macOS ships with bash 3
- `uv` for Python services, `node@22` for Node services
- Environment file: `.env.dev` (or `.env.prod`) in the workspace directory
- First-time: `bash ./local-dev.sh setup` to install Node deps

## Quick Reference

All commands run from the workspace directory (where `local-dev.sh` lives):

```bash
LOCALDEV="bash ./local-dev.sh"
# macOS with system bash: LOCALDEV="bash ./local-dev.sh"

# Start a group
$LOCALDEV start platform --env=dev

# Start a single service
$LOCALDEV start bot-service --env=dev

# Check what's running
$LOCALDEV status

# Stop
$LOCALDEV stop all          # everything
$LOCALDEV stop 8001         # specific port

# Logs
$LOCALDEV logs bot-service  # tail one service
$LOCALDEV logs combined     # interleaved all
tail -100 .logs/bot-service.log  # last 100 lines
```

## Service Groups

| Group | Services | Ports | Use Case |
|-------|----------|-------|----------|
| `minimal` | bot-service, evaluations, evaluations-ui | 8001, 8002, 5174 | Agent testing & eval development |
| `platform` | bot-service, platform-v2, platform-v2-ui, evaluations | 8001, 8003, 5173, 8002 | Agent builder + Jarvis development |
| `chat` | bot-service, middleware, copilot-server, conversation-service, point-of-sale | 8001, 8000, 3000, 9090, 3002 | End-to-end chat widget testing |
| `analytics` | observability, observability-ui | 8004, 5175 | Analytics dashboard |

## Federation Testing (React in Angular)

The `platform` group starts platform-v2-ui as a Vite **dev server** on :5173. For Angular federation testing, you need the **federation build** instead:

```bash
# 1. Start platform group
cd "$WORKSPACE" && bash ./local-dev.sh start platform --env=dev

# 2. Also start copilot-server and copilot-dashboard (not in platform group)
bash ./local-dev.sh start copilot-server --env=dev
bash ./local-dev.sh start copilot-dashboard --env=dev

# 3. Replace dev server with federation build
lsof -ti :5173 | xargs kill -9 2>/dev/null
# Use whichever directory name exists (org or legacy)
PLATFORM_UI=$(ls -d "$WORKSPACE"/copilot-dashboard-react/ui "$WORKSPACE"/indemn-platform-v2/ui 2>/dev/null | head -1)
cd "$PLATFORM_UI" && npm run build:federation && npx serve dist-federation -l 5173 --cors -n &

# 4. Hard refresh Angular in browser (Cmd+Shift+R)
```

**After code changes to federated components:**
```bash
lsof -ti :5173 | xargs kill -9 2>/dev/null
cd "$PLATFORM_UI" && npm run build:federation && npx serve dist-federation -l 5173 --cors -n &
# Then Cmd+Shift+R in Angular browser
```

**Services needed for full federation test:**

| Service | Port | Role |
|---------|------|------|
| copilot-server | 3000 | Auth + API gateway |
| copilot-dashboard | 4500 | Angular host app |
| federation bundle | 5173 | React federated modules |
| platform-v2 | 8003 | Platform API backend |
| bot-service | 8001 | V1 agent runtime |
| evaluations | 8002 | Evaluation service backend |

## Marketing Website (indemn.ai)

The public website at indemn.ai lives in a **separate repo**: `indemn_website_new_design`. It's a React + Vite SPA (MUI, React Router) deployed to AWS S3/CloudFront.

**IMPORTANT:** The `main` branch is often broken (dev WIP). Always use the `prod` branch for local dev.

**Port conflict:** The website runs on port **3000**, same as copilot-server. Don't run both at the same time.

```bash
cd ~/Repositories/indemn_website_new_design
git checkout prod        # main is often broken — prod is the deployed code
npm install              # first time only
npm run dev              # starts on http://localhost:3000
```

| Detail | Value |
|--------|-------|
| Repo | `indemn-ai/indemn_website_new_design` |
| Branch | `prod` (production), `main` (dev — may be broken) |
| Port | 3000 |
| Framework | React 18 + Vite + MUI + React Router |
| Hosting | AWS S3 + CloudFront (NOT Vercel) |
| Deploy flow | `main` → PR to `prod` → auto-deploy to S3/CloudFront |

## All Services

| Service | Port | Dir | Start Command |
|---------|------|-----|---------------|
| **marketing-website** | **3000** | **indemn_website_new_design** (separate repo) | **`npm run dev`** (on `prod` branch) |
| bot-service | 8001 | bot-service | `uv run python app.py` |
| evaluations | 8002 | evaluations | `uv run uvicorn indemn_evals.api.main:app --port 8002 --reload` |
| evaluations-ui | 5174 | evaluations/ui | `npm run dev -- --port 5174` |
| platform-v2 | 8003 | copilot-dashboard-react (or indemn-platform-v2) | `uv run uvicorn indemn_platform.api.main:app --port 8003 --reload` |
| platform-v2-ui | 5173 | copilot-dashboard-react/ui (or indemn-platform-v2/ui) | `npm run dev -- --port 5173` |
| copilot-server | 3000 | copilot-server | `npm start` |
| copilot-dashboard | 4500 | copilot-dashboard | `npm start` |
| middleware | 8000 | middleware-socket-service | `npm start` |
| copilot-sync | 5555 | copilot-sync-service | `npm start` |
| kb-service | 8080 | kb-service | `uv run python app.py` |
| conversation-service | 9090 | conversation-service | `uv run python app.py` |
| observability | 8004 | Indemn-observatory (or indemn-observability) | `source venv/bin/activate && uvicorn ...` |
| observability-ui | 5175 | Indemn-observatory/frontend (or indemn-observability/frontend) | `npm run dev -- --port 5175` |
| voice-service | 9192 | voice-service | `npm start` |
| point-of-sale | 3002 | point-of-sale | `npm run dev -- --port 3002` |

## Common Patterns

**Check what's blocking a port:**
```bash
lsof -i :8001 -P | grep LISTEN
```

**Kill a stuck service:**
```bash
lsof -ti :8001 | xargs kill -9
```

**Use prod data locally (read-only):**
```bash
bash ./local-dev.sh start platform --env=prod
```

**Login (dev):** `support@indemn.ai` / `nzrjW3tZ9K3YiwtMWzBm`

**Login via API (if form doesn't work):**
```bash
TOKEN=$(curl -s -X POST http://localhost:3000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"support@indemn.ai","password":"nzrjW3tZ9K3YiwtMWzBm"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```
