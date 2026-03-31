# Jarvis CLI & MCP Server

Build a CLI tool and MCP server around Indemn's platform APIs so developers (internal first, then external customers) can programmatically manage AI agents — creating agents, prompts, functions, knowledge bases, running evaluations, and pulling analytics. Everything currently done via the Copilot Dashboard UI, made available through command-line and AI-assisted workflows (Claude Code skills, MCP servers).

## Status
**Production beta (2026-03-31). CLI deployed, tested, announced to dev-squad.**

- **npm:** `@indemn/cli@1.3.1` published publicly. Install: `npm install -g @indemn/cli`
- **Showcase page:** blog.indemn.ai/products/indemn-cli/ (committed, not yet deployed)
- **GitHub:** https://github.com/craig-indemn/indemn-cli (private — pending migration to indemn-ai org)
- **indemn-cli repo:** `/Users/home/Repositories/indemn-cli/` (main branch) — 35+ TypeScript source files, 58 MCP tools, 6 skills, builds cleanly
- **Copilot Server:** API key auth merged (PR #806). Security hardening PR #835 awaiting reviewer approval.
- **Claude Code:** MCP server added to user config, plugin installed via local marketplace
- **Design coverage:** 100% — URL scraping, file upload, function params, pagination, eval advanced flags, models all implemented
- **E2E:** 50/51 tests passing. Only failure: `testset list` without `--agent-id` (evals server 500, not our bug).
- **README:** Updated with team setup instructions and full command reference.

### What Just Happened (2026-03-13, Phase 2 complete)
**All 12 tasks complete. Published @indemn/cli@1.1.1 with CLI exports.**

Implemented CLI exports (Phase 2) following the plan at `/Users/home/Repositories/indemn-cli/docs/plans/2026-03-13-cli-exports.md`:

1. **Task 1** — Added `@react-pdf/renderer`, `react`, `@types/react` deps; JSX config in tsconfig; postbuild asset copy script
2. **Task 2** — Bundled 4 Barlow TTF fonts + Indemn logo PNG in `src/report/assets/`
3. **Task 3** — Created `src/report/styles.ts` (brand styles, font registration with local paths) and `src/report/scoring.ts` (all scoring utilities ported from dashboard)
4. **Task 4** — Created `src/report/agent-card/` — types.ts, cover.tsx, document.tsx (7-page agent card: cover, system prompt, tools, KBs, LLM config, eval history, metadata)
5. **Task 5** — Created `src/report/eval-report/` — types.ts, cover.tsx, v2-cover.tsx, item-page.tsx, matrix-page.tsx, example-page.tsx, document.tsx (V1 matrix + V2 per-item reports)
6. **Task 6** — Created `src/report/generate.tsx` (renderToBuffer driver for both PDF types)
7. **Task 7** — Added `indemn eval export <run-id>` to `src/cli/eval.ts` (markdown dump)
8. **Task 8** — Added `indemn eval report <run-id>` to `src/cli/eval.ts` (branded PDF)
9. **Task 9** — Added `indemn agents card <agent-id>` to `src/cli/agents.ts` (agent card PDF)
10. **Task 10** — Added 3 MCP tools (`export_eval_markdown`, `export_eval_report`, `export_agent_card`) to `src/mcp/tools.ts`
11. **Task 11** — Created `skills/eval-analysis/SKILL.md` + `references/data-shapes.md` (adapted from OS skill, uses `indemn` CLI instead of curl)

Shared export logic lives in `src/report/export.ts` — used by both CLI commands and MCP tools.

**All code builds cleanly with `npm run build`. No type errors.**

### Task 12 — E2E Test + Publish (DONE)

All 3 commands tested against real dev data, PDFs visually verified, published as `@indemn/cli@1.1.1`.
- `eval export` — 78KB markdown, 19 items with conversations + dual scores
- `eval report` — 295KB branded PDF, cover + per-item pages
- `agents card` — 169KB branded PDF, 5 pages (cover, prompt, tools, KBs, LLM config)
- 58 MCP tools registered (55 + 3 export)
- Note: agent card only works with agents in the configured org (cross-org returns 404)

### Production Readiness Checklist
- [x] Prod Firebase config in auth.ts (`prod-gemini-470505`)
- [x] Prod host URLs in client.ts (`copilot.indemn.ai/api`, `evaluations.indemn.ai`, `proxy.indemn.ai`)
- [x] API key prefix: server uses `ind_dev_` (dev) / `ind_live_` (prod) based on NODE_ENV
- [x] `zod` as explicit dependency
- [x] MCP chat greeting race condition fixed
- [x] All 58 MCP tools with schemas (55 core + 3 export)
- [x] README with team setup instructions
- [x] Security audit completed (2026-03-24)
- [x] JWT expiration (24h) on API-key-generated tokens
- [x] Strict token format validation (regex)
- [x] API key name field validation (trim, length, safe chars)
- [x] Config file permissions locked to 600
- [x] socket.io-parser DoS vulnerability patched
- [x] `@indemn/cli@1.2.0` published to npm
- [x] GLOBAL_SECRET verified set in prod
- [ ] Merge copilot-server PR #835 (awaiting reviewer)
- [ ] Deploy copilot-server to prod
- [ ] Test login flow E2E against prod

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
| 2026-03-24 | [production-hardening-plan](../../docs/plans/2026-03-24-cli-production-hardening.md) | Security audit + hardening plan for production deployment |

## Decisions
- 2026-03-31: Production beta announced to dev-squad. Every CLI command tested E2E against prod. 6 bugs found and fixed during testing.
- 2026-03-31: Added `org list` and `org switch` — API key authenticates user, server validates org membership per-request
- 2026-03-31: Added `indemn init` — copies skills to .claude/skills/indemn/ for auto-discovery
- 2026-03-31: Consolidated 5 skills into 2 (agent-builder, evaluations) with complete command reference
- 2026-03-31: Fixed login — password prompt rewritten (muted readline), --env flag routing fixed (Commander global option conflict)
- 2026-03-31: Fixed --model (wraps in llm_config with auto provider detection), functions update (includes type), kb import (bulk QNA), is_required display
- 2026-03-24: Security hardening — JWT 24h expiry, strict token regex, name validation, config chmod 600, socket.io-parser patched
- 2026-03-24: Published @indemn/cli@1.2.0 with security fixes
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

### Next: Phase 3 — Remote MCP Server

Add HTTP transport (SSE or Streamable HTTP) so users can connect from Claude AI, ChatGPT, and Gemini by pasting a URL — no npm install required.

Options explored during brainstorming (2026-03-18):
- **Option A:** Hosted MCP service (new deployment at mcp.indemn.ai)
- **Option B:** MCP endpoints on copilot-server (reuse existing auth)
- **Option C:** Serverless MCP (Vercel functions)
- **Option D:** Dual transport in CLI (local stdio + remote HTTP)

Key considerations: API key auth already exists, chat tool uses Socket.IO (stateful), 58 tools are stateless CRUD wrappers.

### Product Showcase

Live at: https://blog.indemn.ai/products/indemn-cli/
- 3 demo videos recorded (Claude Code, Claude AI desktop, Gemini CLI)
- ChatGPT demo pending (requires Plus/Pro for MCP)
- MCP configured locally for Claude Desktop and Gemini CLI

## Open Questions
- **Access control for production CLI usage** — Team members have full write access to all agents in their active org. Need per-user or per-agent scoping. Options: scoped API keys, role-based permissions, org-level agent ownership.
- **Repo migration** — Dhruv creating repo under `indemn-ai` org. Then migrate from `craig-indemn/indemn-cli`, set up CI/CD for automated npm publishing, establish Linear project for CLI work.
- **Server-side bugs** — `kb data update` returns "reject is not defined"; `functions import --url` fails parsing some OpenAPI specs. Both copilot-server issues.
- Which remote MCP transport to use — SSE or Streamable HTTP? (Phase 3)
- Where to host the remote MCP server — Vercel, copilot-server, or standalone? (Phase 3)
