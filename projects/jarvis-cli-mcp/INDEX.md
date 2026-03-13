# Jarvis CLI & MCP Server

Build a CLI tool and MCP server around Indemn's platform APIs so developers (internal first, then external customers) can programmatically manage AI agents — creating agents, prompts, functions, knowledge bases, running evaluations, and pulling analytics. Everything currently done via the Copilot Dashboard UI, made available through command-line and AI-assisted workflows (Claude Code skills, MCP servers).

## Status
**Phase 1 implementation complete. Local E2E testing in progress — blocked on JWT auth.**

- **indemn-cli repo:** `/Users/home/Repositories/indemn-cli/` — 23 TypeScript source files, builds cleanly with zero type errors
- **Copilot Server:** `feat/api-key-auth` branch with API key model, service, routes, Bearer passport strategy
- **Code reviewed:** 3 parallel reviews completed, 3 bugs found and fixed (Firebase auth unwrapping, duplicate app init, MCP chat race condition)

### What's Been Tested (Working)
1. CLI builds and `indemn --help` shows all commands
2. `npm link` — `indemn` command available globally at `/opt/homebrew/bin/indemn`
3. Evals service CRUD — `indemn rubric list/create/get/delete` all work against `devevaluations.indemn.ai`
4. Test sets endpoint returns 500 on dev evals service (server-side issue, not CLI bug)
5. Firebase auth flow — `signInWithEmailAndPassword` works with dev Firebase project (`gmail-agent-449107`)
6. Firebase signin → server returns `requiresMfa: true` — MFA flow triggers correctly, code prompt fires
7. MFA verify endpoint validates correctly (rejects bad codes with proper error)
8. MCP server — all 37 tools register successfully

### What's Blocked: JWT Auth for API Key Testing
The copilot-server's passport JWT strategy has a bug at `middleware/passport.js:102`:
```javascript
const audUrl = new URL(decoded.aud); // throws "Invalid URL" when aud="tiledesk"
```
The server's own `generateJWT()` in `firebaseAuth.js` sets `audience: process.env.SIGN_OPTIONS_ISSUER` which is `"tiledesk"` — not a valid URL. This causes:
- **With `aud` field:** `new URL("tiledesk")` throws uncaught TypeError, request hangs forever
- **Without `aud` field:** Falls through to `done(null, configSecret)` but still returns "Unauthorized"

This means NO authenticated endpoints work locally with manually-created JWTs. The Firebase flow works up to MFA, but MFA emails don't send locally (`EMAIL_ENABLED=false` in .env).

### Path Forward (Next Session)
**Option A — Fix the passport bug (recommended):**
Add try/catch around `new URL(decoded.aud)` in `passport.js:102` on the `feat/api-key-auth` branch. When `aud` is not a valid URL (like `"tiledesk"`), fall through to `done(null, configSecret)`. This is a real bug that affects production too (it just happens to be caught by something else in the deployed stack). Then manually-created JWTs will work and we can test the full API key flow.

**Option B — Test against remote dev:**
Push `feat/api-key-auth` branch to remote, deploy to dev, test against `devcopilot.indemn.ai/api`. MFA emails would actually send. Requires deployment approval.

**Option C — Disable MFA locally:**
The Mongoose schema has `mfaEnabled: { default: true }`. Even with the DB field set to `false`, the server returns `requiresMfa: true`. Could modify the `firebaseAuth.js` route to skip MFA check locally.

## Key Discoveries During Testing

### Firebase Project Mismatch (FIXED)
- **Dev environment:** Firebase project `gmail-agent-449107` (from AWS Secrets Manager `indemn/dev/shared/firebase-credentials`)
- **Production:** Firebase project `prod-gemini-470505` (from `copilot-dashboard/src/dashboard-config.json`)
- The dashboard-config.json in the repo is the PRODUCTION config. On dev, `envsubst` injects dev Firebase credentials at container startup.
- **Fix applied:** `auth.ts` now has per-environment Firebase configs (`FIREBASE_CONFIGS[env]`)

### URL Prefix (FIXED)
- Deployed copilot-server is behind a reverse proxy that adds `/api` prefix
- Locally, routes are at root (no `/api` prefix)
- **Fix applied:** Moved `/api` into `DEFAULT_HOSTS` values (`https://devcopilot.indemn.ai/api`). Added env var overrides: `INDEMN_COPILOT_URL`, `INDEMN_EVALS_URL`, `INDEMN_MIDDLEWARE_URL`. For local: `INDEMN_COPILOT_URL=http://localhost:3000`

### MFA in Auth Flow (FIXED)
- The copilot-server has MFA on login. CLI now handles it: `login()` accepts `mfaCodePrompt` callback, detects `requiresMfa: true`, prompts for code, calls `/auth/firebase/mfa/verify`.

### Starting Copilot Server Locally
- Copy `.env.aws` to `.env` in copilot-server directory (DO NOT commit)
- `cd /Users/home/Repositories/copilot-server && npm start`
- Port 3000, connects to remote dev MongoDB/Redis/RabbitMQ
- Non-fatal errors on startup: MongoParseError (secondary URI), migration aggregation error — server still works
- Clean up: delete `.env` when done

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Copilot Server OpenAPI Spec | OpenAPI 3.0.3 | copilot-server/docs/openapi.yaml (64KB) |
| Percy Service | GitHub Repo | indemn-ai/percy-service |
| Copilot Server | GitHub Repo | indemn-ai/copilot-server |
| Copilot Dashboard | GitHub Repo | indemn-ai/copilot-dashboard |
| Evaluations Service | GitHub Repo | indemn-ai/evaluations |
| Middleware Socket Service | GitHub Repo | indemn-ai/middleware-socket-service |
| Architecture Docs | Local | docs/architecture/ (17 service docs) |
| Copilot Server API (prod) | Production | https://copilot.indemn.ai |
| Copilot Server API (dev) | Dev | https://devcopilot.indemn.ai |
| Evaluations Service API (prod) | Production | https://evaluations.indemn.ai/api/v1 |
| Evaluations Service API (dev) | Dev | https://devevaluations.indemn.ai/api/v1 |
| Middleware / Chat (prod) | Production | https://proxy.indemn.ai |
| Middleware / Chat (dev) | Dev | https://devproxy.indemn.ai |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-12 | [system-landscape-research](artifacts/2026-03-12-system-landscape-research.md) | What are the existing APIs, auth models, and developer tooling across Percy Service, Copilot Server, and Copilot Dashboard? |
| 2026-03-12 | [cli-mcp-design](artifacts/2026-03-12-cli-mcp-design.md) | Design a CLI and MCP server for programmatic management of Indemn AI agents |
| 2026-03-12 | [cli-mcp-implementation-plan](artifacts/2026-03-12-cli-mcp-implementation-plan.md) | 11-step implementation plan for Phase 1 |

## Decisions
- 2026-03-12: API keys for auth — one-time Firebase login generates persistent key, stored in ~/.indemn/config.json. SHA-256 hashed in DB.
- 2026-03-12: New repo (`indemn-cli`) — CLI is a distribution surface, not core business logic
- 2026-03-12: TypeScript — matches Copilot Server stack, npm distribution, mature MCP SDK
- 2026-03-12: Copilot Server is primary API for agent management; Evaluations Service for evals
- 2026-03-12: Bundled package — one npm install gives CLI + MCP server + skills + plugin
- 2026-03-12: Three-phase rollout: internal (2-3 weeks) → customer-ready (2-3 weeks) → ecosystem (ongoing)
- 2026-03-12: Chat goes through middleware-socket-service via Socket.IO (same production path as widget)
- 2026-03-12: Environment configurable — all hostnames support prod/dev (dev prefix convention)
- 2026-03-12: API key auth uses Bearer scheme (distinct from existing JWT scheme in Copilot Server)
- 2026-03-12: Plugin uses Claude Code format: .claude-plugin/plugin.json (metadata only) + .mcp.json (flat format) + skills/
- 2026-03-12: Firebase configs per environment — dev uses `gmail-agent-449107`, production uses `prod-gemini-470505`
- 2026-03-12: URL prefix `/api` baked into DEFAULT_HOSTS, with env var overrides for local testing

## Open Questions
- API key scoping: Should keys have granular scopes (read-only, agent-management, eval-only) or full access?
- Passport JWT bug: Is the `new URL(decoded.aud)` crash happening in production too, or is it caught by something else in the deployed stack?

## Implementation Notes for Future Sessions
- **Design document:** `projects/jarvis-cli-mcp/artifacts/2026-03-12-cli-mcp-design.md` — 787 lines, triple-reviewed, is the source of truth
- **Key repos to read:** copilot-server (routes/ai-studio.js, routes/auth.js, middleware/passport.js), evaluations (api/routes/), middleware-socket-service (utils/clientSocketListners.js)
- **All Copilot Server routes are org-scoped:** `/api/organization/:org_id/ai-studio/...`
- **Chat silent failure:** middleware drops invalid bot_type silently — CLI needs timeout
- **stream_bot_uttered fires BEFORE session_confirm** — greeting streams first
- **KB unlink needs mapping ID lookup** — GET mappings, find by kb_id, DELETE by mapping_id
- **bot_type accepts ObjectId or name** — prefer ObjectId (names are non-unique)
- **Test user:** `support@indemn.ai` / `nzrjW3tZ9K3YiwtMWzBm` (Firebase password for dev project)
- **Dev evals test-sets endpoint:** Returns 500 (server-side issue)
