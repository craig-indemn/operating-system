# Jarvis CLI & MCP Server

Build a CLI tool and MCP server around Indemn's platform APIs so developers (internal first, then external customers) can programmatically manage AI agents — creating agents, prompts, functions, knowledge bases, running evaluations, and pulling analytics. Everything currently done via the Copilot Dashboard UI, made available through command-line and AI-assisted workflows (Claude Code skills, MCP servers).

## Status
**Phase 1 complete. Published to npm. Phase 2 (exports) designed.**

- **npm:** `@indemn/cli@1.0.0` published publicly. Install: `npm install -g @indemn/cli`
- **GitHub:** https://github.com/craig-indemn/indemn-cli (private)
- **indemn-cli repo:** `/Users/home/Repositories/indemn-cli/` (main branch) — 23 TypeScript source files, 55 MCP tools, 5 skills, builds cleanly
- **Copilot Server:** `feat/api-key-auth` merged to main via PR #806 (2026-03-13). Deployed to devcopilot.indemn.ai.
- **Claude Code:** MCP server added to user config, plugin installed via local marketplace
- **Design coverage:** 100% — URL scraping, file upload, function params, pagination, eval advanced flags, models all implemented
- **Demo:** Recorded and shared with dev-squad on 2026-03-13. Full flywheel: create agent → configure → evaluate → improve → re-evaluate. Clean sweep.
- **E2E:** 50/51 tests passing. Only failure: `testset list` without `--agent-id` (evals server 500, not our bug).
- **README:** Updated with team setup instructions and full command reference.

### What Just Happened (2026-03-13, this session)
1. Full design audit — compared 787-line design doc against all source files
2. Fixed prod readiness issues: added `zod` to explicit deps, fixed MCP chat race condition, renamed `--version` to `--revision` (Commander.js conflict)
3. Added missing features: `indemn eval list`, `rubric get --revision N`, `testset get --revision N`
4. Improved `testset list` error message (suggests `--agent-id` when server 500s)
5. Pushed `feat/api-key-auth` branch, PR #806 created, CI checks passed, PR merged to main
6. Fixed package-lock.json npm version mismatch (npm 11 vs CI npm 10)
7. Reset `~/.indemn/config.json` to use remote dev defaults (removed localhost override)
8. Deleted copilot-server local `.env`, stopped local server
9. Updated README with team setup section and new commands

### Next: Install & Test Against Remote Dev

1. **Verify deployment landed** — `curl https://devcopilot.indemn.ai/auth/api-keys` should respond (not 404)
2. **Test `indemn login --env dev`** — Firebase MFA against remote dev (first real E2E login test)
3. **Generate a fresh API key** — current key was generated against localhost, need one for remote dev
4. **Re-run E2E tests against remote dev** — verify everything works without local server
5. **Install CLI the way others would** — git clone, npm install, npm link, follow README
6. **Install as Claude Code plugin** — `claude plugins install /path/to/indemn-cli`, verify MCP + skills
7. **Share with team** — Slack instructions, help others set up
8. **Improvements** — user has ideas to implement after testing

### Production Readiness Checklist
- [x] Prod Firebase config in auth.ts (`prod-gemini-470505`)
- [x] Prod host URLs in client.ts (`copilot.indemn.ai/api`, `evaluations.indemn.ai`, `proxy.indemn.ai`)
- [x] API key prefix: server uses `ind_dev_` (dev) / `ind_live_` (prod) based on NODE_ENV
- [x] `zod` as explicit dependency
- [x] MCP chat greeting race condition fixed
- [x] All 55 MCP tools with schemas
- [x] README with team setup instructions
- [ ] Login flow tested E2E against remote dev
- [ ] Login flow tested E2E against prod
- [ ] Deploy API key auth to prod copilot-server
- [ ] Generate prod API keys for team

## Key Technical Details

### Copilot Server Changes (now merged to main)
**New files (our code):**
- `models/apiKey.js` — Mongoose schema for API keys (key_hash, user_id, org_id, status)
- `services/apiKeyService.js` — createKey, validateKey, listKeys, revokeKey
- `routes/apiKeys.js` — POST/GET/DELETE at `/auth/api-keys`
- `middleware/apiKeyToJwt.js` — converts `Bearer ind_*` to JWT transparently (avoids modifying existing routes)

**Modified files (minimal changes to existing code):**
- `app.js` — 4 lines: mount apiKeyToJwt middleware before passport.initialize()
- `middleware/passport.js` — try/catch around `new URL(decoded.aud)` to fix crash on non-URL audience

**Zero existing route files modified.**

### Starting Copilot Server Locally (if needed)
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
# Against remote dev (after deployment):
curl -X POST https://devcopilot.indemn.ai/api/auth/api-keys -H "Authorization: jwt $TOKEN" -H "Content-Type: application/json" -d '{"name":"test"}'
# Write config: ~/.indemn/config.json with api_key, org_id (69a40cd971552df0c6b6807f), user_id (65f839af9ca3710013305a3e), environment: dev
indemn agents list
```

### Current Config State
`~/.indemn/config.json` has been reset to use default remote dev hosts. The API key `ind_dev_a948...` was generated against localhost — it may or may not work against remote dev (depends on whether both point to the same MongoDB). If it doesn't, generate a fresh one after deployment.

### API Reference
- **KB create:** `POST /knowledge-bases` with `{ type: "text", payload: { question, answer, isManual: true } }`
- **KB URL scraping:** `POST /knowledge-bases/:id/import` with `{ type: "url", sources: [{ url, crawl_mode: "full" }] }`
- **KB file upload:** `POST /knowledge-bases/:id/upload-urls` (multipart FormData)
- **KB list data:** `GET /knowledge-bases/:id/data-source` returns `{ dataSources: [], total, page, pages }`
- **KB types are uppercase:** QNA, URL, FILE. Data source types are lowercase: text, url, file.
- **Mappings GET:** `[{ id: "kb_id", connectedBots: [{ id: "bot_id", id_mapping: "mapping_id" }] }]`
- **Function params add:** `POST .../functions/:id/parameters` expects array of params with `is_required` field
- **Function params update:** `POST .../functions/:id/parameters` (upsert with `id` in body)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Copilot Server OpenAPI Spec | OpenAPI 3.0.3 | copilot-server/docs/openapi.yaml (64KB) |
| Copilot Server | GitHub Repo | indemn-ai/copilot-server (main — API key auth merged) |
| Copilot Server PR #806 | GitHub PR | indemn-ai/copilot-server/pull/806 |
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
| 2026-03-13 | [cli-exports-design](artifacts/2026-03-13-cli-exports-design.md) | Design for CLI exports — eval reports (PDF), agent cards (PDF), markdown dumps, eval-analysis skill |

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
- 2026-03-13: URL scraping goes through `/import` endpoint (not `/data-source`) — triggers async kb-service crawling
- 2026-03-13: Function params API uses arrays and `is_required` field, update is POST upsert (not PUT)
- 2026-03-13: `--version` flag renamed to `--revision` on rubric/testset get (Commander.js conflict with program version)
- 2026-03-13: copilot-server uses npm 10 / Node 22 in CI — lock file must be generated with matching version
- 2026-03-13: Published `@indemn/cli@1.0.0` publicly on npm — no org plan needed, API key required to use
- 2026-03-13: GitHub repo at `craig-indemn/indemn-cli` (private) — `indemn-ai` org requires admin to create repos
- 2026-03-13: Port React-PDF templates from dashboard for eval reports and agent cards — same output, Node.js headless rendering
- 2026-03-13: Eval analysis skill uses CLI commands (`indemn eval status/results --json`), not MCP or curl

## Implementation Notes for Future Sessions
- **Design document:** `projects/jarvis-cli-mcp/artifacts/2026-03-12-cli-mcp-design.md` — 787 lines, source of truth
- **All Copilot Server routes are org-scoped:** `/organization/:org_id/ai-studio/...`
- **Chat silent failure:** middleware drops invalid bot_type silently — CLI has 10s timeout
- **stream_bot_uttered fires BEFORE session_confirm** — greeting streams first
- **bot_type accepts ObjectId or name** — prefer ObjectId (names are non-unique)
- **Test user:** `support@indemn.ai` / `nzrjW3tZ9K3YiwtMWzBm` (Firebase password for dev project)
- **Dev evals test-sets endpoint:** Returns 500 without agent_id filter (server-side issue)
- **Org ID for dev:** `69a40cd971552df0c6b6807f`
- **User ID for test user:** `65f839af9ca3710013305a3e`
- **JWT secret:** `nodeauthsecret` (GLOBAL_SECRET in .env.aws)
- **KB get returns array** — SDK extracts first element
- **KB export default format:** `csv` (server doesn't support `json` export)
- **copilot-server CI:** Node 22, npm 10, `npm ci` — lock file must match

### Next: Phase 2 — Exports Implementation

Design doc: `artifacts/2026-03-13-cli-exports-design.md`

1. Add `@react-pdf/renderer` + `react` dependencies, bundle Barlow fonts and logo
2. Port React-PDF templates from `indemn-platform-v2/ui/src/components/report/`
3. Implement `indemn eval export <run-id>` — markdown dump
4. Implement `indemn eval report <run-id>` — branded PDF
5. Implement `indemn agents card <agent-id>` — branded agent card PDF
6. Add 3 MCP tools: `export_eval_markdown`, `export_eval_report`, `export_agent_card`
7. Adapt `eval-analysis` skill from OS (curl → CLI commands)
8. Publish `@indemn/cli@1.1.0`

## Open Questions
- When do we deploy API key auth to prod copilot-server?
- Transfer `indemn-cli` repo to `indemn-ai` org when Craig gets create permissions?
