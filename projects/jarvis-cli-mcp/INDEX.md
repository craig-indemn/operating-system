# Jarvis CLI & MCP Server

Build a CLI tool and MCP server around Indemn's platform APIs so developers (internal first, then external customers) can programmatically manage AI agents — creating agents, prompts, functions, knowledge bases, running evaluations, and pulling analytics. Everything currently done via the Copilot Dashboard UI, made available through command-line and AI-assisted workflows (Claude Code skills, MCP servers).

## Status
**Phase 1 E2E testing substantially complete. Core CLI, MCP server, and evals working. KB data source commands need fixes.**

- **indemn-cli repo:** `/Users/home/Repositories/indemn-cli/` — 23 TypeScript source files, builds cleanly with zero type errors
- **Copilot Server:** `feat/api-key-auth` branch — API key model, service, routes, apiKeyToJwt middleware, passport aud fix
- **Code reviewed:** 3 parallel reviews completed, 3 bugs found and fixed (Firebase auth unwrapping, duplicate app init, MCP chat race condition)

### E2E Test Results (2026-03-13)

| Command | Status | Notes |
|---------|--------|-------|
| `indemn whoami` | PASS | Shows API key, org, env |
| `indemn agents list` | PASS | Table + `--json` output |
| `indemn agents create` | PASS | Creates agent, returns ID |
| `indemn agents get <id>` | PASS | Fixed v2 array response unwrap |
| `indemn agents update <id>` | PASS | Updates description |
| `indemn agents clone <id>` | PASS | Fixed clone response format |
| `indemn agents delete <id>` | PASS | Confirmation prompt works |
| `indemn config get/set` | PASS | Prompt read/write works |
| `indemn functions list/create` | PASS | CRUD works |
| `indemn kb list/create/delete` | PASS | Type must be uppercase (QNA) |
| `indemn kb link` | PASS | Links KB to agent |
| `indemn kb data add` | FAIL | API expects `{ type, payload }` not `{ question, answer }` |
| `indemn kb data list` | FAIL | Response is `{ dataSources, total, page }`, SDK expects array |
| `indemn kb unlink` | FAIL | Mapping lookup needs investigation |
| `indemn rubric list/create/delete` | PASS | Against remote evals service |
| MCP server (37 tools) | PASS | All tools register with correct schemas |

### What's Left
1. **KB data source fixes** — update SDK to match copilot-server API format (`{ type: "text"|"url"|"file", payload: {...} }`) and handle paginated response
2. **KB unlink** — debug mapping ID lookup
3. **Chat testing** — `indemn chat <agent-id>` via Socket.IO (not yet tested this session)
4. **Login flow E2E** — blocked on MFA emails not sending locally; works against remote dev
5. **Skills testing** — `/agent-setup`, `/eval-orchestration`, etc. in Claude Code with plugin
6. **Push `feat/api-key-auth` to remote** — needs deployment approval for full remote testing

## Key Discoveries During Testing

### Passport JWT `new URL()` Bug (FIXED)
- `middleware/passport.js:102` did `new URL(decoded.aud)` where aud="tiledesk" — not a valid URL
- Caused uncaught TypeError, requests hung forever
- **Fix applied:** try/catch around `new URL()`, falls through to `done(null, configSecret)` when aud is not a URL

### API Key-to-JWT Middleware (NEW — avoids modifying existing routes)
- Instead of adding `"bearer"` to all 160 `passport.authenticate()` calls across 37 route files, created `middleware/apiKeyToJwt.js`
- Intercepts `Authorization: Bearer ind_*`, validates key, generates JWT, rewrites header to `Authorization: jwt <token>`
- Existing passport JWT strategy handles it transparently — zero changes to existing route files
- Mounted in `app.js` before `passport.initialize()`

### DATABASE_URI Needs Database Name
- `.env.aws` has `DATABASE_URI=mongodb+srv://...@dev-indemn.pj4xyep.mongodb.net` — no database name
- Mongoose defaults to `test` database, not `tiledesk`
- **For local testing:** append `/tiledesk` to the URI: `DATABASE_URI=mongodb+srv://...@dev-indemn.pj4xyep.mongodb.net/tiledesk`
- This is only a local testing issue — deployed server likely has the full URI

### v2 Bots Endpoint Returns Array
- `GET /organization/:org_id/ai-studio/v2/bots/:id` returns an array even for a single bot
- **Fix applied:** SDK `getAgent()` unwraps: `Array.isArray(result) ? result[0] : result`

### Clone Response Format
- `POST .../v2/bots/clone` returns `{ new_agent_id, new_agent_name }` not an Agent object
- **Fix applied:** CLI handles both formats

### Firebase Project Mismatch (FIXED)
- **Dev environment:** Firebase project `gmail-agent-449107` (from AWS Secrets Manager `indemn/dev/shared/firebase-credentials`)
- **Production:** Firebase project `prod-gemini-470505` (from `copilot-dashboard/src/dashboard-config.json`)
- **Fix applied:** `auth.ts` now has per-environment Firebase configs (`FIREBASE_CONFIGS[env]`)

### URL Prefix (FIXED)
- Deployed copilot-server is behind a reverse proxy that adds `/api` prefix
- Locally, routes are at root (no `/api` prefix)
- **Fix applied:** Moved `/api` into `DEFAULT_HOSTS` values. Added env var overrides: `INDEMN_COPILOT_URL`, `INDEMN_EVALS_URL`, `INDEMN_MIDDLEWARE_URL`. For local: `INDEMN_COPILOT_URL=http://localhost:3000`

### MFA in Auth Flow (FIXED)
- The copilot-server has MFA on login. CLI now handles it: `login()` accepts `mfaCodePrompt` callback, detects `requiresMfa: true`, prompts for code, calls `/auth/firebase/mfa/verify`.

### Starting Copilot Server Locally
1. Copy `.env.aws` to `.env` in copilot-server directory (DO NOT commit)
2. **Append `/tiledesk` to DATABASE_URI** in `.env`
3. `cd /Users/home/Repositories/copilot-server && npm start`
4. Port 3000, connects to remote dev MongoDB/Redis/RabbitMQ
5. Non-fatal errors on startup: MongoParseError (secondary URI), migration aggregation error — server still works
6. Clean up: delete `.env` when done

### Generating Test JWTs (Bypasses Firebase + MFA)
```javascript
// In copilot-server directory:
node -e "const jwt = require('jsonwebtoken'); console.log(jwt.sign({_id:'65f839af9ca3710013305a3e', email:'support@indemn.ai'}, 'nodeauthsecret', {issuer:'tiledesk', subject:'user'}))"
```
Use the token: `curl -H "Authorization: jwt <token>" http://localhost:3000/testauth`

### Creating API Keys and Testing CLI
```bash
# 1. Generate JWT and create API key
TOKEN="<jwt from above>"
curl -X POST http://localhost:3000/auth/api-keys -H "Authorization: jwt $TOKEN" -H "Content-Type: application/json" -d '{"name":"test"}'

# 2. Write CLI config
cat > ~/.indemn/config.json << EOF
{"api_key":"<key>","org_id":"<org_id>","user_id":"65f839af9ca3710013305a3e","environment":"dev"}
EOF

# 3. Run CLI commands against local server
INDEMN_COPILOT_URL=http://localhost:3000 indemn agents list
```

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
- 2026-03-13: API key-to-JWT middleware instead of modifying existing routes — minimal copilot-server changes

## Open Questions
- API key scoping: Should keys have granular scopes (read-only, agent-management, eval-only) or full access?
- KB data source API format: CLI sends `{ question, answer }` but API expects `{ type: "text"|"url"|"file", payload: {...} }` — need to inspect payload structure for QNA type

## Implementation Notes for Future Sessions
- **Design document:** `projects/jarvis-cli-mcp/artifacts/2026-03-12-cli-mcp-design.md` — 787 lines, triple-reviewed, is the source of truth
- **Key repos to read:** copilot-server (routes/ai-studio.js, routes/auth.js, middleware/passport.js, middleware/apiKeyToJwt.js), evaluations (api/routes/), middleware-socket-service (utils/clientSocketListners.js)
- **All Copilot Server routes are org-scoped:** `/api/organization/:org_id/ai-studio/...`
- **Chat silent failure:** middleware drops invalid bot_type silently — CLI needs timeout
- **stream_bot_uttered fires BEFORE session_confirm** — greeting streams first
- **KB unlink needs mapping ID lookup** — GET mappings, find by kb_id, DELETE by mapping_id
- **bot_type accepts ObjectId or name** — prefer ObjectId (names are non-unique)
- **Test user:** `support@indemn.ai` / `nzrjW3tZ9K3YiwtMWzBm` (Firebase password for dev project)
- **Dev evals test-sets endpoint:** Returns 500 (server-side issue)
- **Org ID for dev:** `69a40cd971552df0c6b6807f`
- **User ID for test user:** `65f839af9ca3710013305a3e`
