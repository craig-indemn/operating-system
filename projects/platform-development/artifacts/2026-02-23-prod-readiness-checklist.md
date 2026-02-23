---
ask: "Production readiness checklist for Jarvis baseline generation feature"
created: 2026-02-23
workstream: platform-development
session: 2026-02-23-d
sources:
  - type: github
    description: "percy-service, evaluations, copilot-dashboard CI/CD workflows and docker configs"
  - type: ec2
    description: "Dev EC2 deployment at ec2-44-196-55-84.compute-1.amazonaws.com"
---

# Production Readiness Checklist: Jarvis Baseline Generation

## Context

The Jarvis baseline generation feature (skills architecture + evaluation harness) is validated on dev EC2. Three successful runs against Wedding Bot producing quality rubrics (6 universal rules) and test sets (15 items). Need to deploy to production.

**Current state:**
- percy-service: code on `main`, deployed to dev EC2 (`ec2-44-196-55-84`), port 8013→8000
- evaluations: code on `main`, deployed to dev EC2, port 8005→8080
- copilot-dashboard: evaluation UI wrappers exist, loads React components via Module Federation from platform-v2 UI. Currently 18 commits behind prod.

**Deployment model:**
- percy-service + evaluations: push to `prod` branch → GitHub Actions → self-hosted runner on prod EC2
- copilot-dashboard: PR from `main` to `prod` → team approval → GitHub Actions → self-hosted runner

---

## Checklist

### 1. Prod EC2 — Docker Container Setup

These services need Docker containers running on the prod EC2 instance.

**percy-service:**
- [ ] Create `/opt/percy-service/` directory on prod EC2
- [ ] Copy `docker-compose.yml` to prod EC2
- [ ] Create `.env` with production values (see Environment Variables below)
- [ ] Create `shared-datadog` Docker network if it doesn't exist
- [ ] Pull and start container: `docker compose pull percy-service && docker compose up -d`
- [ ] Verify health: `curl http://localhost:8003/api/v1/health`

**evaluations:**
- [ ] Create `/opt/evaluations/` directory on prod EC2
- [ ] Copy `docker-compose.yml` to prod EC2
- [ ] Create `.env` with production values (see Environment Variables below)
- [ ] Pull and start container: `docker compose pull app && docker compose up -d`
- [ ] Verify health: `curl http://localhost:8005/api/v1/health`

**Connectivity:**
- [ ] Verify percy-service can reach evaluations via Docker DNS: `docker exec percy-service curl http://evaluations:8080/api/v1/health`
- [ ] Verify evaluations can reach bot-service: `docker exec evaluations curl https://bot.indemn.ai/health` (or internal Docker DNS if bot-service is on same host)

### 2. Self-Hosted Runners (Prod)

CI/CD deploys to self-hosted runners tagged `[self-hosted, linux, x64, prod]`.

- [ ] Install GitHub Actions runner on prod EC2 for percy-service repo (at `~/actions-runner-percy-service/`)
- [ ] Install GitHub Actions runner on prod EC2 for evaluations repo (at `~/actions-runner-evaluations/`)
- [ ] Register runners with correct labels: `self-hosted, linux, x64, prod`
- [ ] Install as systemd services for auto-restart
- [ ] Verify runners appear as "Online" in GitHub repo Settings → Actions → Runners

### 3. Environment Variables

**percy-service `.env` (prod):**
```
MONGO_URL=mongodb+srv://devadmin:<password>@prod-indemn.3h3ab.mongodb.net
MONGO_DB_NAME=tiledesk
ANTHROPIC_API_KEY=<prod key>
OPENAI_API_KEY=<prod key>
PINECONE_API_KEY=<prod key>
COHERE_API_KEY=<prod key>
EVALUATION_SERVICE_URL=http://evaluations:8080
CO_PILOT_URL=https://copilot.indemn.ai
LANGCHAIN_API_KEY=<langsmith key>
LANGCHAIN_PROJECT=PROD-percy-service
LANGCHAIN_TRACING_V2=true
ENVIRONMENT=prod
JARVIS_TEMPLATE_ID=jarvis_evaluation_v2
```

**evaluations `.env` (prod):**
```
MONGODB_URI=mongodb+srv://devadmin:<password>@prod-indemn.3h3ab.mongodb.net
MONGODB_DATABASE=tiledesk
TILEDESK_DATABASE=tiledesk
BOT_SERVICE_URL=https://bot.indemn.ai
OPENAI_API_KEY=<prod key>
ANTHROPIC_API_KEY=<prod key>
LANGSMITH_API_KEY=<langsmith key>
LANGSMITH_PROJECT_NAME=evaluations-prod
```

**Key differences from dev:**
- `MONGO_URL` / `MONGODB_URI` → prod Atlas cluster (`prod-indemn.3h3ab.mongodb.net`)
- `BOT_SERVICE_URL` → `https://bot.indemn.ai` (prod bot-service)
- `ENVIRONMENT` → `prod`
- `LANGCHAIN_PROJECT` / `LANGSMITH_PROJECT_NAME` → prod project names
- `CO_PILOT_URL` → `https://copilot.indemn.ai`

### 4. Template Seeding on Prod

The `jarvis_evaluation_v2` template needs to exist in prod MongoDB.

- [ ] SSH to prod EC2
- [ ] Run seed script in percy-service container:
  ```bash
  sudo docker exec percy-service python scripts/seed_jarvis_templates.py
  ```
- [ ] Verify template exists:
  ```bash
  sudo docker exec percy-service python3 -c "
  from pymongo import MongoClient
  import os
  client = MongoClient(os.environ['MONGO_URL'])
  db = client[os.environ['MONGO_DB_NAME']]
  t = db.jarvis_templates.find_one({'template_id': 'jarvis_evaluation_v2'})
  print('Found' if t else 'NOT FOUND')
  "
  ```

### 5. Deploy Code to Prod

**percy-service:**
- [ ] Ensure `main` is clean and passing CI
- [ ] Push to prod branch: `git push origin main:prod`
- [ ] Verify build-prod.yml runs successfully
- [ ] Verify container updated on prod EC2

**evaluations:**
- [ ] Ensure `main` is clean and passing CI
- [ ] Push to prod branch: `git push origin main:prod`
- [ ] Verify build-prod.yml runs successfully
- [ ] Verify container updated on prod EC2

**copilot-dashboard:**
- [ ] Create PR from `main` to `prod`
- [ ] Get team approval
- [ ] Merge PR → auto-deploys via prod.yml

### 6. Prod Smoke Test

After all services are deployed:

- [ ] Trigger a baseline generation via percy-service API:
  ```bash
  curl -X POST https://platform.indemn.ai/api/v1/jarvis/jobs \
    -H "Content-Type: application/json" \
    -H "X-Organization-Id: <prod_org_id>" \
    -d '{"job_type": "baseline_generation", "bot_ids": ["<prod_bot_id>"]}'
  ```
- [ ] Verify job completes successfully
- [ ] Verify rubric created with 3-6 universal rules
- [ ] Verify test set created with ~15 items
- [ ] Verify evaluation run completes with results
- [ ] Check results in copilot-dashboard UI

### 7. What Can Be Done Now (Before Prod EC2 Setup)

- [x] Code is on `main` for percy-service (all 9 commits including skill improvements)
- [x] Code is on `main` for evaluations
- [x] Feature validated with 3 successful runs on dev
- [ ] Prepare the copilot-dashboard PR from `main` to `prod`
- [ ] Document the prod `.env` values (gather API keys, confirm prod MongoDB credentials)
- [ ] Confirm prod bot-service URL and any bot IDs to test against

---

## Order of Operations

1. **Now**: Prepare copilot-dashboard PR, gather prod credentials/env vars
2. **Infra**: Set up Docker containers + runners on prod EC2
3. **Deploy**: Push percy-service and evaluations to `prod` branch, merge copilot-dashboard PR
4. **Seed**: Run template seeding on prod
5. **Test**: Smoke test baseline generation against a prod bot
