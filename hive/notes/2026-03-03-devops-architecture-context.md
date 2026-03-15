---
title: Capture the planning discussion decisions for secrets, ECS, and deployment
  architecture
tags:
- note
domains:
- indemn
refs:
  project: devops
status: active
created: '2026-03-03'
---

# Capture the planning discussion decisions for secrets, ECS, and deployment architecture

# DevOps Architecture Context

## Current State

- 4-5 EC2 instances on AWS, manually provisioned
- GitHub Actions SSH into EC2, pull Docker images, run `docker compose up`
- Docker Hub for image registry (creds in GitHub env vars)
- `.env` files manually copied into containers — no centralized secrets
- Fixed dev/staging/prod EC2 instances, manual provisioning for new environments
- Multiple microservices, each with own Docker image. MongoDB + Redis backing services.

## Agreed Architecture Decisions

### Secrets & Config (Immediate — Implementing Now)

**Dual approach:**
- **AWS Secrets Manager** for credentials: DB passwords, API keys, tokens. Native rotation, JSON secrets, lifecycle management.
- **AWS Parameter Store** for non-sensitive config: service URLs, feature flags, env names. Free for standard parameters.

**Design principles:**
- Credentials injected by infrastructure, not fetched by app code
- On ECS (future): task definitions map secrets to env vars directly
- On EC2 (now): startup wrapper script pulls and sets env vars
- Hierarchical paths: `/{env}/{service-or-shared}/{name}`
- GitHub Actions uses OIDC federation (assume IAM role, no long-lived keys)

### Container Orchestration (Future Phase)

- ECS Fargate for dev/ephemeral (pay-per-use), ECS EC2 for prod (cost predictability)
- Ephemeral PR environments with auto-generated URLs
- TTL auto-cleanup (48h default)
- No SSH — ECS APIs and ECS Exec only
- AWS Cloud Map for service discovery

**Data layer for ephemeral envs:**
- Shared MongoDB staging with per-env namespacing (`pr-142-myapp`)
- Shared Redis with per-env key prefixes (`pr-142:cache:*`)
- Baseline DB snapshot seeds each new env
- Permanent envs (dev/staging/prod) get full isolation

### Infrastructure as Code

Terraform vs CDK not yet decided. Deferred.

## What to Implement Now

1. AWS Secrets Manager for observability repo credentials
2. AWS Parameter Store for observability non-sensitive config
3. Startup mechanism to pull values and expose as env vars (replacing .env)
4. IAM roles/policies with least-privilege (dev reads dev, not prod)
5. GitHub Actions OIDC federation for AWS auth
