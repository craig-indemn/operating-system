---
ask: "What env vars does indemn-observability use, and which are secrets vs config?"
created: 2026-03-03
workstream: devops
session: 2026-03-03-a
sources:
  - type: github
    description: "Explored indemn-observability repo: .env, .env.example, .env_prod, docker-compose.yml, config.py, GitHub Actions workflows"
---

# Observability Environment Variable Inventory

Complete inventory of environment variables for indemn-observability, classified for AWS Secrets Manager vs Parameter Store.

## Secrets Manager Candidates (17 variables)

| Variable | Service | Sensitivity | Notes |
|----------|---------|-------------|-------|
| `ANTHROPIC_API_KEY` | Anthropic (Claude) | HIGH | ~100+ char secret key |
| `OPENAI_API_KEY` | OpenAI | HIGH | Optional; used if `LLM_PROVIDER=openai` |
| `GOOGLE_API_KEY` | Google (Gemini) | HIGH | Optional; used if `LLM_PROVIDER=google` |
| `LANGSMITH_API_KEY` | LangSmith | HIGH | 40+ char token |
| `LANGFUSE_SECRET_KEY` | Langfuse | HIGH | Secret key for trace ingestion |
| `LANGFUSE_PUBLIC_KEY` | Langfuse | MEDIUM | Public key for Langfuse |
| `MONGODB_URI` | MongoDB Atlas | HIGH | Full connection string with embedded credentials |
| `JWT_SECRET` | Auth | HIGH | JWT signing secret; must match Copilot's `GLOBAL_SECRET` |
| `GLOBAL_SECRET` | Auth | HIGH | Symmetric secret (takes precedence over JWT_SECRET) |
| `GLOBAL_SECRET_OR_PUB_KEY` | Auth | HIGH | Asymmetric JWT key (highest precedence) |
| `DEMO_PASSWORD` | Auth (Demo Mode) | HIGH | Demo login password |
| `DEMO_JWT_SECRET` | Auth (Demo Tokens) | HIGH | Demo JWT signing secret |
| `INTERNAL_API_KEY` | Service-to-Service | HIGH | 32+ char hex for admin endpoints |
| `DOCKER_USERNAME` | Docker Hub | MEDIUM | GitHub Actions only |
| `DOCKER_PASSWORD` | Docker Hub | HIGH | GitHub Actions only |
| `DEV_SLACK_URL` | Slack Webhooks | MEDIUM | GitHub Actions deployment notifications |
| `PROD_SLACK_URL` | Slack Webhooks | MEDIUM | GitHub Actions production notifications |

### Shared vs Service-Specific

Likely **shared across services** (same value in every service):
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY` — org-wide LLM keys
- `LANGSMITH_API_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY` — org-wide observability
- `MONGODB_URI` — same cluster, different databases
- `JWT_SECRET` / `GLOBAL_SECRET` — must match across services for auth
- `INTERNAL_API_KEY` — service-to-service auth
- `DOCKER_USERNAME` / `DOCKER_PASSWORD` — CI/CD only

Likely **service-specific**:
- `DEMO_PASSWORD`, `DEMO_JWT_SECRET` — observability-specific demo mode
- `GLOBAL_SECRET_OR_PUB_KEY` — may vary by service

## Parameter Store Candidates (23 variables)

| Variable | Service | Example Value | Notes |
|----------|---------|---------------|-------|
| `LANGSMITH_PROJECT_NAME` | LangSmith | `PROD-INDEMN` | Per-environment |
| `MONGODB_DB` | MongoDB | `tiledesk` | Database name |
| `MONGODB_REQUESTS_COLLECTION` | MongoDB | `requests` | Collection name |
| `AGGREGATIONS_PATH` | Data Processing | `data/aggregations.json` | File path |
| `CONVERSATIONS_PATH` | Data Processing | `data/observatory_output_v3.json` | File path |
| `LLM_PROVIDER` | LLM Config | `anthropic` | Provider selection |
| `LLM_MODEL` | LLM Config | `claude-haiku-4-5` | Model name |
| `LLM_TEMPERATURE` | LLM Config | `0` | Numeric |
| `LLM_MAX_TOKENS` | LLM Config | `1000` | Numeric |
| `LLM_NUM_CTX` | LLM Config | `32768` | Ollama only |
| `AUTH_ENABLED` | Authentication | `true`/`false`/`demo` | Feature flag |
| `COPILOT_SERVER_URL` | Copilot | `https://copilot.indemn.ai/api` | Per-environment |
| `GLOBAL_SECRET_ALGORITHM` | Auth (JWT) | `HS256` | Algorithm name |
| `DEMO_USERNAME` | Auth (Demo) | `gic` | Demo mode |
| `INDEMN_DOMAIN` | Auth | `indemn.ai` | Domain name |
| `CORS_ORIGINS` | API Security | Comma-separated URLs | Per-environment |
| `DD_SERVICE` | DataDog | `observatory-api` | Service name |
| `DD_ENV` | DataDog | `dev` or `prod` | Per-environment |
| `DD_VERSION` | DataDog | `1.0.0` | Version tag |
| `DD_LOGS_INJECTION` | DataDog | `true` | Feature flag |
| `DD_TRACE_ENABLED` | DataDog | `true`/`false` | Feature flag |
| `LANGFUSE_HOST` | Langfuse | `https://hipaa.cloud.langfuse.com` | URL |
| `EVALUATIONS_BASE_URL` | Evaluations | `http://localhost:8002` | Per-environment |
| `VITE_API_BASE` | Frontend | `http://localhost:8004` | Build-time |

## Critical Findings

1. **Dev/Prod configs nearly identical** — `.env` and `.env_prod` both point to same MongoDB cluster with same credentials. Need true environment isolation.
2. **MongoDB credentials embedded in connection string** — the entire `MONGODB_URI` is one secret. Consider whether to keep as single secret or decompose.
3. **JWT secrets shared across services** — `JWT_SECRET` and `GLOBAL_SECRET` must match Copilot server. These are cross-service shared secrets.
4. **GitHub Actions uses 4 separate secrets** — `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `DEV_SLACK_URL`, `PROD_SLACK_URL`. These should move to OIDC-based auth for Docker and Slack.

## Proposed Secrets Manager Path Convention

```
/dev/shared/anthropic-api-key
/dev/shared/mongodb-uri
/dev/shared/langsmith-api-key
/dev/shared/langfuse-keys          # JSON: {public_key, secret_key}
/dev/shared/jwt-secret
/dev/shared/internal-api-key
/dev/observability/demo-credentials  # JSON: {password, jwt_secret}
/prod/shared/anthropic-api-key
/prod/shared/mongodb-uri
...
```

## Proposed Parameter Store Path Convention

```
/dev/shared/llm-provider
/dev/shared/llm-model
/dev/shared/mongodb-db
/dev/observability/auth-enabled
/dev/observability/cors-origins
/dev/observability/copilot-server-url
/prod/shared/llm-provider
/prod/observability/auth-enabled
...
```
