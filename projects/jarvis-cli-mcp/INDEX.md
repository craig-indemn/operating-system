# Jarvis CLI & MCP Server

Build a CLI tool and MCP server around Indemn's platform APIs so developers (internal first, then external customers) can programmatically manage AI agents — creating agents, prompts, functions, knowledge bases, running evaluations, and pulling analytics. Everything currently done via the Copilot Dashboard UI, made available through command-line and AI-assisted workflows (Claude Code skills, MCP servers).

## Status
Design complete, approved, and triple-reviewed against codebase. All route paths, auth schemes, chat protocol, plugin format, and API shapes verified against actual source code across 6 repositories. Ready for implementation.

**Next step:** Create implementation plan and begin Phase 1 build.

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

## Decisions
- 2026-03-12: API keys for auth — one-time Firebase login generates persistent key, stored in ~/.indemn/config.json. SHA-256 hashed in DB.
- 2026-03-12: New repo (`indemn-cli`) — CLI is a distribution surface, not core business logic
- 2026-03-12: TypeScript — matches Copilot Server stack, npm distribution, mature MCP SDK
- 2026-03-12: Copilot Server is primary API for agent management; Evaluations Service for evals
- 2026-03-12: Bundled package — one npm install gives CLI + MCP server + skills + plugin
- 2026-03-12: Skills migrate from Percy Service to CLI package; Percy keeps its own copies for Jarvis runtime
- 2026-03-12: Three-phase rollout: internal (2-3 weeks) → customer-ready (2-3 weeks) → ecosystem (ongoing)
- 2026-03-12: Chat goes through middleware-socket-service via Socket.IO (same production path as widget)
- 2026-03-12: Environment configurable — all hostnames support prod/dev (dev prefix convention)
- 2026-03-12: API key auth uses Bearer scheme (distinct from existing JWT scheme in Copilot Server)
- 2026-03-12: Plugin uses Claude Code format: .claude-plugin/plugin.json (metadata only) + .mcp.json (flat format) + skills/
- 2026-03-12: Prompt get/set are SDK convenience wrappers over bot configurations endpoint
- 2026-03-12: Function update/delete require agent-id (API is bot-scoped)
- 2026-03-12: Two-step Firebase login: Firebase ID token → POST /api/auth/firebase → Copilot Server JWT → POST /api/auth/api-keys → persistent API key
- 2026-03-12: Eval commands work without auth in Phase 1 (Evaluations Service has no auth, network-level security)

## Open Questions
- API key scoping: Should keys have granular scopes (read-only, agent-management, eval-only) or full access?
- Evaluations Service auth (Phase 2): Share MongoDB collection with Copilot Server, or call a validation endpoint?

## Implementation Notes for Future Sessions
- **Design document:** `projects/jarvis-cli-mcp/artifacts/2026-03-12-cli-mcp-design.md` — 787 lines, triple-reviewed, is the source of truth
- **Key repos to read:** copilot-server (routes/ai-studio.js, routes/auth.js, middleware/passport.js), evaluations (api/routes/), middleware-socket-service (utils/clientSocketListners.js)
- **All Copilot Server routes are org-scoped:** `/api/organization/:org_id/ai-studio/...`
- **Chat silent failure:** middleware drops invalid bot_type silently — CLI needs timeout
- **stream_bot_uttered fires BEFORE session_confirm** — greeting streams first
- **KB unlink needs mapping ID lookup** — GET mappings, find by kb_id, DELETE by mapping_id
- **bot_type accepts ObjectId or name** — prefer ObjectId (names are non-unique)
