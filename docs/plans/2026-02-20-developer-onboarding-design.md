# Design: Developer Onboarding System

**Date:** 2026-02-20
**Status:** Approved

## Problem

A new developer joining Indemn needs to go from a fresh machine to a fully working local development environment. Today this requires manually cloning 13+ repos, configuring environment variables, installing dependencies across Python and Node services, and wiring everything together. The operating system has the pieces (local-dev.sh, .env.template, skills) but no automated path from zero to running.

## Design Principles

- **Claude Code is the conductor** — the developer runs `/onboarding`, Claude Code does everything
- **Platform agnostic** — macOS (Intel/Apple Silicon) and Linux (Ubuntu/Debian)
- **No assumptions** — don't assume workspace location, directory structure, or what's pre-installed
- **Flexible by role** — Engineers get full stack, Executives get intelligence tools, Sales gets CRM tools
- **Idempotent** — safe to re-run; skips what's already done, fixes what's broken
- **Modular phases** — each phase can be run independently for troubleshooting

## Architecture

The onboarding skill orchestrates six phases. Each phase is self-contained and can be re-run.

```
Phase 1: Environment Detection
  └─ OS, architecture, shell, existing tools, workspace location

Phase 2: Prerequisites
  └─ Homebrew/apt, bash 4+, node 22, uv, gh, git, mongosh, psql

Phase 3: Repository Setup
  └─ gh auth, clone all org repos, operating-system

Phase 4: Environment Configuration
  └─ .env.dev from 1Password, validate infrastructure connections

Phase 5: Dependency Installation
  └─ uv sync (Python services), npm install (Node services), local-dev.sh setup

Phase 6: Start & Verify
  └─ Start services via local-dev.sh, health check, smoke test, report
```

## Repo Mapping

The new developer clones from the `indemn-ai` GitHub org. Some repos have different names than the legacy local directory names used by `local-dev.sh`.

| Org Repo | Legacy Local Name | Notes |
|----------|------------------|-------|
| `indemn-ai/bot-service` | `bot-service` | Direct match |
| `indemn-ai/copilot-server` | `copilot-server` | Direct match |
| `indemn-ai/copilot-dashboard` | `copilot-dashboard` | Direct match |
| `indemn-ai/copilot-dashboard-react` | `indemn-platform-v2` | Name mismatch — local-dev.sh updated |
| `indemn-ai/evaluations` | `evaluations` | Direct match |
| `indemn-ai/Indemn-observatory` | `indemn-observability` | Name mismatch — local-dev.sh updated |
| `indemn-ai/middleware-socket-service` | `middleware-socket-service` | Direct match |
| `indemn-ai/conversation-service` | `conversation-service` | Direct match |
| `indemn-ai/kb-service` | `kb-service` | Direct match |
| `indemn-ai/copilot-sync-service` | `copilot-sync-service` | Direct match |
| `indemn-ai/point-of-sale` | `point-of-sale` | Direct match |
| `indemn-ai/voice-service` | `voice-service` | Direct match |
| `indemn-ai/payment-service` | `payment-service` | Direct match |
| `craig-indemn/operating-system` | `operating-system` | `onboarding` branch (no personal projects) |

`local-dev.sh` is updated to auto-detect which directory name exists — supports both org names and legacy names.

## Credential Strategy

- A pre-filled `.env.dev` with all infrastructure credentials is stored in 1Password
- During onboarding, Claude Code asks the developer to download it from 1Password
- Claude Code places it at `<workspace>/.env.dev` and validates connections (MongoDB, Redis, RabbitMQ)
- No interactive credential collection for 100+ variables

## Role Definitions

| Role | Repos | Tools | Local Services |
|------|-------|-------|---------------|
| **Engineer** | All 13 platform repos + operating-system | All CLI tools (gh, uv, node, mongosh, psql, etc.) | Full local-dev stack |
| **Executive** | operating-system only | gog, slack, psql (read-only) | None |
| **Sales** | operating-system only | gog, slack, apollo | None |

## Platform Support

| Prerequisite | macOS | Linux (Ubuntu/Debian) |
|-------------|-------|----------------------|
| Package manager | Homebrew | apt |
| bash 4+ | `brew install bash` | Pre-installed |
| Node 22 | `brew install node@22` | `curl -fsSL https://deb.nodesource.com/setup_22.x \| sudo bash && sudo apt install -y nodejs` |
| uv | `brew install uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| gh | `brew install gh` | `sudo apt install gh` |
| mongosh | `brew install mongosh` | See MongoDB docs |
| psql | `brew install libpq` | `sudo apt install postgresql-client` |

## Verification

Phase 6 verifies everything works:

1. **Infrastructure connections** — MongoDB ping, Redis ping, RabbitMQ connection
2. **Service health** — HTTP health check on each running service port
3. **Smoke test** — Login via copilot-server API, verify token returned
4. **Report** — Table of all services with status, ports, and access URLs

## Changes Required

1. **`local-dev.sh`** — Add directory name mapping (org names ↔ legacy names)
2. **`.claude/skills/onboarding/SKILL.md`** — Full rewrite as onboarding conductor
3. **`onboarding` branch** — Created, clean of personal projects

## Future Extensions

- Vault/secrets manager integration (beyond 1Password manual download)
- CI/CD setup (GitHub Actions access, deployment permissions)
- IDE configuration (VS Code extensions, settings)
- Docker setup for services that support containerized dev
