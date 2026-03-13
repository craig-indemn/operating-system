# Jarvis CLI & MCP Server

Build a CLI tool and MCP server around Indemn's platform APIs so developers (internal first, then external customers) can programmatically manage AI agents — creating agents, prompts, functions, knowledge bases, running evaluations, and pulling analytics. Everything currently done via the Copilot Dashboard UI, made available through command-line and AI-assisted workflows (Claude Code skills, MCP servers).

## Status
**Phase 1 E2E testing in progress. Core agent CRUD, config, functions, evals working. KB data source fixes committed but untested. Chat untested.**

- **indemn-cli repo:** `/Users/home/Repositories/indemn-cli/` — 23 TypeScript source files, builds cleanly
- **Copilot Server:** `feat/api-key-auth` branch — API key model, service, routes, apiKeyToJwt middleware, passport aud fix
- **Code reviewed:** 3 parallel reviews completed, 3 bugs found and fixed

### E2E Test Results (2026-03-13)

| Command | Status | Notes |
|---------|--------|-------|
| `indemn whoami` | PASS | |
| `indemn agents list/create/get/update/clone/delete` | PASS | All CRUD works |
| `indemn config get/set` | PASS | Prompt read/write works |
| `indemn functions list/create` | PASS | |
| `indemn kb list/create/delete` | PASS | Type auto-uppercased now |
| `indemn kb link` | PASS | |
| `indemn kb data add` | FIXED (untested) | Now sends `{ type: "text", payload: { question, answer } }` |
| `indemn kb data list` | FIXED (untested) | Now unwraps `{ dataSources, total, page, pages }` |
| `indemn kb unlink` | FIXED (untested) | Now reads `connectedBots[].id_mapping` from response |
| `indemn rubric list/create/delete` | PASS | Against remote evals service |
| MCP server (37 tools) | PASS | All tools register with schemas |
| `indemn chat` | UNTESTED | Socket.IO chat session — code exists but never tested |
| Login flow (Firebase+MFA) | UNTESTED E2E | MFA emails don't send locally |
| Skills (eval-orchestration, agent-setup, etc.) | UNTESTED | Need Claude Code plugin install |

### Demo Goal (Next Session)
Full flywheel demo: create agent → scrape website KB → create custom functions → test agent via chat → run evaluations → modify agent based on results → re-evaluate. All via CLI + MCP + skills.

### What Must Be Verified Before Demo
1. **KB data add/list/unlink** — fixes committed but not tested against server
2. **Chat** — `indemn chat <agent-id>` never tested
3. **Skills** — install plugin in Claude Code, test `/agent-setup`, `/eval-orchestration`
4. **Full login flow** — either fix MFA locally or test against remote dev
5. **Review design doc completeness** — compare `artifacts/2026-03-12-cli-mcp-design.md` against actual implementation, ensure 100% coverage

## Key Technical Details

### Copilot Server Changes (feat/api-key-auth branch)
**New files (our code):**
- `models/apiKey.js` — Mongoose schema for API keys (key_hash, user_id, org_id, status)
- `services/apiKeyService.js` — createKey, validateKey, listKeys, revokeKey
- `routes/apiKeys.js` — POST/GET/DELETE at `/auth/api-keys`
- `middleware/apiKeyToJwt.js` — converts `Bearer ind_*` to JWT transparently (avoids modifying existing routes)

**Modified files (minimal changes to existing code):**
- `app.js` — 4 lines: mount apiKeyToJwt middleware before passport.initialize()
- `middleware/passport.js` — try/catch around `new URL(decoded.aud)` to fix crash on non-URL audience

**Zero existing route files modified.**

### Starting Copilot Server Locally
1. Copy `.env.aws` to `.env` in `/Users/home/Repositories/copilot-server/`
2. **Append `/tiledesk` to DATABASE_URI** — without this, mongoose connects to `test` db instead of `tiledesk`
3. `cd /Users/home/Repositories/copilot-server && npm start` — port 3000
4. Non-fatal startup errors (MongoParseError, migration) — server still works
5. **Clean up: delete `.env` when done**

### Generating Test JWTs (Bypasses Firebase + MFA)
```javascript
// In copilot-server directory:
node -e "const jwt = require('jsonwebtoken'); console.log(jwt.sign({_id:'65f839af9ca3710013305a3e', email:'support@indemn.ai'}, 'nodeauthsecret', {issuer:'tiledesk', subject:'user'}))"
```

### Creating API Keys and Testing CLI
```bash
TOKEN="<jwt from above>"
curl -X POST http://localhost:3000/auth/api-keys -H "Authorization: jwt $TOKEN" -H "Content-Type: application/json" -d '{"name":"test"}'
# Write config: ~/.indemn/config.json with api_key, org_id (69a40cd971552df0c6b6807f), user_id (65f839af9ca3710013305a3e), environment: dev
INDEMN_COPILOT_URL=http://localhost:3000 indemn agents list
```

### KB Data Source API Format (for reference)
- **Create:** `POST /knowledge-bases/:id/data-source` with `{ type: "text", payload: { question, answer, isManual: true } }`
- **List:** `GET /knowledge-bases/:id/data-source` returns `{ dataSources: [], total, page, pages }`
- **Update:** `PUT /knowledge-bases/:id/data-source/:sourceId` with `{ payload: { question, answer, isManual: true } }`
- **KB types are uppercase:** QNA, URL, FILE. Data source types are lowercase: text, url, file.

### Mappings API Format (for reference)
- **GET** `/ai-studio/bots/:id/mappings` returns `[{ id: "kb_id", connectedBots: [{ id: "bot_id", id_mapping: "mapping_id" }] }]`
- **DELETE** `/ai-studio/bots/:id/mappings/:id_mapping`

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Copilot Server OpenAPI Spec | OpenAPI 3.0.3 | copilot-server/docs/openapi.yaml (64KB) |
| Copilot Server | GitHub Repo | indemn-ai/copilot-server (branch: feat/api-key-auth) |
| Copilot Dashboard | GitHub Repo | indemn-ai/copilot-dashboard |
| Evaluations Service | GitHub Repo | indemn-ai/evaluations |
| Middleware Socket Service | GitHub Repo | indemn-ai/middleware-socket-service |
| Copilot Server API (dev) | Dev | https://devcopilot.indemn.ai |
| Evaluations Service API (dev) | Dev | https://devevaluations.indemn.ai/api/v1 |
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
- 2026-03-12: Chat goes through middleware-socket-service via Socket.IO (same production path as widget)
- 2026-03-12: Environment configurable — all hostnames support prod/dev (dev prefix convention)
- 2026-03-12: Plugin uses Claude Code format: .claude-plugin/plugin.json + .mcp.json + skills/
- 2026-03-12: Firebase configs per environment — dev uses `gmail-agent-449107`, production uses `prod-gemini-470505`
- 2026-03-12: URL prefix `/api` baked into DEFAULT_HOSTS, with env var overrides for local testing
- 2026-03-13: API key-to-JWT middleware instead of modifying existing routes — minimal copilot-server changes

## Implementation Notes for Future Sessions
- **Design document:** `projects/jarvis-cli-mcp/artifacts/2026-03-12-cli-mcp-design.md` — 787 lines, source of truth
- **All Copilot Server routes are org-scoped:** `/organization/:org_id/ai-studio/...`
- **Chat silent failure:** middleware drops invalid bot_type silently — CLI has 10s timeout
- **stream_bot_uttered fires BEFORE session_confirm** — greeting streams first
- **bot_type accepts ObjectId or name** — prefer ObjectId (names are non-unique)
- **Test user:** `support@indemn.ai` / `nzrjW3tZ9K3YiwtMWzBm` (Firebase password for dev project)
- **Dev evals test-sets endpoint:** Returns 500 (server-side issue)
- **Org ID for dev:** `69a40cd971552df0c6b6807f`
- **User ID for test user:** `65f839af9ca3710013305a3e`
- **JWT secret:** `nodeauthsecret` (GLOBAL_SECRET in .env.aws)
