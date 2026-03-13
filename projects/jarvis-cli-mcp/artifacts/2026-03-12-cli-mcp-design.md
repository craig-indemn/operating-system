---
ask: "Design a CLI and MCP server for programmatic management of Indemn AI agents"
created: 2026-03-12
workstream: jarvis-cli-mcp
session: 2026-03-12-a
sources:
  - type: github
    description: "Percy Service, Copilot Server, Copilot Dashboard, Evaluations Service, middleware-socket-service codebase exploration"
  - type: github
    ref: "copilot-server/docs/openapi.yaml"
    name: "Copilot Server OpenAPI Spec"
  - type: github
    description: "Claude Code plugin format verified from installed plugins at ~/.claude/plugins/"
---

# Design: Indemn CLI & MCP Server

**Date:** 2026-03-12
**Status:** Approved (revised with codebase-grounded corrections)

## Problem

The Indemn platform's agent management capabilities are locked behind the Copilot Dashboard UI. There's no programmatic way to create agents, manage prompts, configure functions, build knowledge bases, run evaluations, or chat with agents. Internal engineers and conversational designers can't leverage AI-assisted workflows (Claude Code) for agent development, and external customers have no API/CLI access to build automation on top of the platform.

## Users

1. **Internal Indemn team** — Engineers and conversational designers using Claude Code with skills. Need AI-assisted workflows for building and evaluating agents.
2. **External customers** — Developers at insurance companies who use the Indemn platform to build their own agents. Need a proper developer experience with CLI, SDK, and API keys.

## Key Decisions

- **API keys for auth** — One-time Firebase login generates a persistent API key. No OAuth flows.
- **New repo** (`indemn-cli`) — CLI is a distribution surface, not core business logic. Own release cycle.
- **TypeScript** — Matches Copilot Server stack, npm distribution, mature MCP SDK.
- **Copilot Server is primary API** — Agent CRUD, functions, KBs. Evaluations Service for evals.
- **Bundled package** — One npm install gives you CLI + MCP server + skills + plugin.
- **Skills migrate from Percy Service** — CLI package becomes the canonical developer-facing skills. Percy keeps its own copies for Jarvis runtime use.
- **Environment configurable** — All hostnames configurable between prod (`copilot.indemn.ai`) and dev (`devcopilot.indemn.ai`). Dev hostnames use `dev` prefix.
- **Chat goes through middleware-socket-service** — Same path as production, using Socket.IO protocol.

---

## Architecture

### Three-Layer Design

```
┌──────────────────────────────────────────────────────┐
│                     @indemn/cli                       │
├─────────────┬──────────────┬─────────────────────────┤
│   CLI       │  MCP Server  │  Skills + Plugin        │
│  (terminal) │  (Claude)    │  (workflow guides)       │
├─────────────┴──────────────┴─────────────────────────┤
│                      SDK                              │
│    (TypeScript API client — shared foundation)        │
├────────────────────┬──────────────────┬──────────────┤
│  Copilot Server    │ Evaluations Svc  │ Middleware    │
│  Agents, Functions │ Rubrics, Tests,  │ Chat via      │
│  KBs, Config       │ Runs, Results    │ Socket.IO     │
└────────────────────┴──────────────────┴──────────────┘
```

- **SDK** does all the work (API calls, auth, error handling)
- **CLI** calls SDK, formats output for terminal
- **MCP** calls SDK, exposes as tools for Claude Code
- **Skills** guide Claude through complex multi-step workflows using MCP tools

### Package Structure

```
indemn-cli/
├── .claude-plugin/
│   └── plugin.json          # Claude Code plugin manifest
├── .mcp.json                # MCP server configuration
├── src/
│   ├── sdk/                 # Core API client (shared foundation)
│   │   ├── client.ts        # HTTP client, auth, environment config
│   │   ├── agents.ts        # Agent CRUD operations
│   │   ├── config.ts        # Bot configuration (prompts, LLM, greeting)
│   │   ├── functions.ts     # Function/tool management
│   │   ├── kb.ts            # Knowledge base operations
│   │   ├── rubrics.ts       # Rubric CRUD + versioning
│   │   ├── test-sets.ts     # Test set CRUD + versioning
│   │   ├── eval.ts          # Evaluation trigger, runs, results
│   │   └── chat.ts          # Agent chat via Socket.IO
│   ├── cli/                 # CLI commands (thin wrappers over SDK)
│   │   ├── index.ts         # Entry point, command registration
│   │   ├── auth.ts          # indemn login/logout/whoami
│   │   ├── agents.ts        # indemn agents list/get/create/update/delete/clone
│   │   ├── config.ts        # indemn config get/set (prompt, LLM, greeting)
│   │   ├── functions.ts     # indemn functions list/create/update/delete/test/import/export
│   │   ├── kb.ts            # indemn kb list/create/delete + data source CRUD + link/unlink
│   │   ├── eval.ts          # indemn eval run/status/results + rubric/testset CRUD
│   │   └── chat.ts          # indemn chat <agent-id>
│   └── mcp/                 # MCP server (exposes SDK as tools)
│       ├── server.ts        # MCP server setup
│       └── tools.ts         # Tool definitions mapping to SDK
├── skills/                  # Claude Code skills
│   ├── eval-orchestration/
│   │   └── SKILL.md
│   ├── test-set-creation/
│   │   └── SKILL.md
│   ├── rubric-creation/
│   │   └── SKILL.md
│   └── agent-setup/
│       └── SKILL.md
├── package.json
└── tsconfig.json
```

---

## Environment Configuration

All service URLs are configurable. Dev hostnames use `dev` prefix:

| Service | Production | Dev |
|---------|-----------|-----|
| Copilot Server | `https://copilot.indemn.ai` | `https://devcopilot.indemn.ai` |
| Evaluations Service | `https://evaluations.indemn.ai` | `https://devevaluations.indemn.ai` |
| Middleware (chat) | `https://proxy.indemn.ai` | `https://devproxy.indemn.ai` |

The SDK auto-resolves all URLs from the configured environment. Config stored in `~/.indemn/config.json`.

---

## API Routing

The SDK routes to the correct backend transparently:

| Operation | Backend | Base Path |
|-----------|---------|-----------|
| Agents, functions, KBs, config | Copilot Server | `/organization/:org_id/ai-studio/...` |
| Knowledge bases | Copilot Server | `/organization/:org_id/knowledge-bases/...` |
| Evaluations, rubrics, test sets, runs | Evaluations Service | `/api/v1/...` |
| Chat (interactive) | Middleware Socket Service | Socket.IO connection |

### Copilot Server Route Structure

**Critical:** All AI Studio routes are org-scoped. The route hierarchy is:

```
Source: copilot-server/app.js → routes/organization.js → routes/ai-studio.js

/organization/:id_organization/ai-studio/
├── bots                                    [GET, POST]
├── v2/bots                                 [GET] (expanded format)
├── bots/:id_bot                            [GET, PUT, DELETE]
├── v2/bots/:id_bot                         [GET] (expanded format)
├── v2/bots/clone                           [POST]
├── bots/:id_bot/configurations             [GET, PUT]
├── bots/:id_bot/configurations/voice/numbers [POST, GET, DELETE, PATCH]
├── bots/:id_bot/functions                  [GET, POST]
├── bots/:id_bot/functions/:id_function     [PUT, DELETE]
├── bots/:id_bot/functions/:id_function/test-rest-api  [POST]
├── bots/:id_bot/functions/:id_function/parameters     [GET, POST, PUT, DELETE]
├── bots/:id_bot/functions/export           [POST]
├── bots/:id_bot/functions/import           [POST]
├── bots/:id_bot/mappings                   [GET, POST]
├── bots/:id_bot/mappings/:id_mapping       [DELETE]
├── bots/:id_bot/ai-suggestions             [POST]
├── bots/:id_bot/relevant-answers           [GET]
├── master-functions                        [GET]
└── llm-models                              [GET]

/organization/:id_organization/knowledge-bases/
├── /                                       [GET, POST]
├── /:id_kb                                 [GET, PUT, DELETE]
├── /:id_kb/data-source                     [GET, POST]
├── /:id_kb/data-source/:id_data_source     [PUT, DELETE]
├── /:id_kb/data-source/:id_data_source/re-import [PUT]
├── /:id_kb/import                          [POST]
├── /:id_kb/export                          [POST]
└── /:id_kb/upload-urls                     [POST - multipart]
```

**Notes:**
- The reverse proxy adds an `/api/` prefix, so the full URL is `https://copilot.indemn.ai/api/organization/:org_id/...`
- The SDK must store and inject `org_id` into every request path (resolved during login)
- All endpoints return `{ success: true, data: ... }` on success

### Evaluations Service Route Structure

```
Source: evaluations/src/indemn_evals/api/main.py → routes/

/api/v1/
├── rubrics                                 [GET, POST]
├── rubrics/:rubric_id                      [GET, PUT, DELETE]
├── rubrics/:rubric_id/versions             [GET] (list all versions)
├── rubrics/:rubric_id/versions/:version    [GET] (get specific version)
├── test-sets                               [GET, POST]
├── test-sets/:test_set_id                  [GET, PUT, DELETE]
├── test-sets/:test_set_id/versions         [GET] (list all versions)
├── test-sets/:test_set_id/versions/:version [GET] (get specific version)
├── evaluations                             [POST] (trigger V2 evaluation — requires test_set_id)
├── runs                                    [GET, POST] (GET lists runs, POST triggers V1 evaluation)
├── runs/:run_id                            [GET]
├── runs/:run_id/results                    [GET]
├── datasets                                [GET, POST]
├── datasets/:dataset_id                    [GET, PUT, DELETE]
├── datasets/:dataset_id/test-cases         [GET, POST]
├── test-cases/:test_case_id                [GET, DELETE]
├── question-sets                           [GET, POST] (V1 legacy — full CRUD + versioning)
├── question-sets/:question_set_id          [GET, PUT, DELETE]
├── question-sets/:question_set_id/versions [GET]
├── question-sets/:question_set_id/versions/:version [GET]
├── bots/:bot_id/context                    [GET]
├── evaluator-configs                       [GET, POST]
├── evaluator-configs/:config_id            [GET, PUT, DELETE]
├── evaluators/types                        [GET]
└── evaluate-transcript                     [POST]
```

**Notes:**
- The Evaluations Service currently has **zero authentication** — all endpoints are publicly accessible, relying on network-level security. Adding API key auth is required for Phase 2 (external customers) and is greenfield work (new FastAPI middleware from scratch).
- Two evaluation trigger paths exist: `POST /evaluations` (V2, requires `test_set_id`) and `POST /runs` (V1, requires `dataset_id` + `agent_id`). The CLI uses the V2 path. V1 question sets exist but are intentionally out of scope for Phase 1.
- List endpoints return at most 100-1000 results (e.g., runs: 100, results: 1000). The CLI should support `--limit` and `--page` flags for pagination.

---

## Authentication

### Current Auth in Copilot Server

```
Source: copilot-server/middleware/passport.js

- JWT scheme: Authorization header uses "jwt" scheme, NOT "Bearer"
  → ExtractJwt.fromAuthHeaderWithScheme("jwt")
  → Requests use: Authorization: jwt <token>
- Also extracted from query param: ?secret_token=<token>
- Secret resolution is dynamic per JWT audience claim:
  → /bots/{id} → bot's secret from faq_kb.secret
  → /projects/{id} → project's jwtSecret
  → /subscriptions/{id} → subscription's secret
  → default → GLOBAL_SECRET env var
- Basic auth also supported (email + password via bcrypt)
```

### API Key Auth Design

API keys need a **new Passport strategy** that runs alongside the existing JWT/Basic strategies.

**Flow (two-step token exchange):**

```
Source: copilot-server/routes/firebaseAuth.js (existing Firebase verification)
        copilot-server/routes/auth.js (existing JWT issuance)

1. User runs `indemn login`
2. CLI uses Firebase client SDK (`firebase/auth`) with Indemn's web project config
   - Headless mode: `signInWithEmailAndPassword(auth, email, password)`
   - Browser mode: opens browser for SSO/MFA, localhost callback receives token
3. Firebase returns an ID token (Firebase JWT)
4. CLI sends Firebase ID token to `POST /api/auth/firebase` on Copilot Server
   → Server verifies via Firebase Admin SDK, returns a Copilot Server JWT
5. CLI sends Copilot Server JWT to `POST /api/auth/api-keys`
   → Server generates persistent API key, returns it with org_id and user_id
6. CLI stores API key + org_id + user_id in `~/.indemn/config.json`
7. All subsequent CLI/MCP requests include `Authorization: Bearer <api-key>`
8. New Passport strategy intercepts `Bearer` scheme, validates against `api_keys` collection, resolves user + org context
```

**Why Bearer works:** Copilot Server's existing JWT strategy only handles the `jwt` scheme (`Authorization: jwt <token>`). The `valid-token.js` middleware just checks for a two-part Authorization header — it doesn't care about the scheme name. So `Bearer` can coexist without conflict.

**Firebase client config:** The CLI needs the Indemn Firebase web project config (apiKey, projectId, authDomain). This is public configuration (not a secret) — it gets bundled into the CLI package, same as how the Copilot Dashboard bundles it.

### Config File

```json
// ~/.indemn/config.json
{
  "api_key": "ind_live_abc123...",
  "org_id": "64a...",
  "user_id": "64b...",
  "environment": "production",
  "hosts": {
    "production": {
      "copilot": "https://copilot.indemn.ai",
      "evaluations": "https://evaluations.indemn.ai",
      "middleware": "https://proxy.indemn.ai"
    },
    "dev": {
      "copilot": "https://devcopilot.indemn.ai",
      "evaluations": "https://devevaluations.indemn.ai",
      "middleware": "https://devproxy.indemn.ai"
    }
  }
}
```

### Backend Changes Required

**Copilot Server (Phase 1):**
1. New `api_keys` MongoDB collection (key_hash, user_id, org_id, name, scopes, created_at, last_used_at, revoked). Keys are hashed with SHA-256 before storage (fast lookup, key is high-entropy so no need for bcrypt). The raw key is returned only once at creation time; only the hash is stored.
2. New route file `routes/apiKeys.js` mounted at `/auth/api-keys` in `app.js` (separate from the existing 871-line `routes/auth.js`, following the pattern of `routes/firebaseAuth.js` mounted at `/auth/firebase`)
3. `POST /api/auth/api-keys` — generate key (requires valid Firebase JWT in Authorization header)
4. `GET /api/auth/api-keys` — list user's keys
5. `DELETE /api/auth/api-keys/:id` — revoke key
6. New Passport strategy for `Bearer` scheme that validates API keys against `api_keys` collection
7. Update `passport.authenticate()` calls to include the new strategy: `["basic", "jwt", "bearer"]`
8. Keys prefixed with `ind_live_` / `ind_test_` for identification

**Evaluations Service (Phase 2 — greenfield):**
1. New FastAPI middleware for API key validation (no auth exists today)
2. Either query Copilot Server's `api_keys` collection directly (shared MongoDB access) or call a validation endpoint on Copilot Server

**Percy Service:** No changes needed.

---

## CLI Commands

```
indemn login                                    # Authenticate via Firebase, generate API key
indemn login --env dev                          # Authenticate against dev environment
indemn logout                                   # Clear stored credentials
indemn whoami                                   # Show current user/org/environment

indemn agents list                              # List all agents in org
indemn agents get <agent-id>                    # Agent details (config, prompt, functions, KBs)
indemn agents create --name "..."               # Create new agent
indemn agents update <agent-id>                 # Update agent metadata (name, description, webhook)
indemn agents delete <agent-id>                 # Soft-delete agent (sets trashed: true)
indemn agents clone <agent-id>                  # Clone an existing agent

indemn config get <agent-id>                    # Get full bot configuration (prompt, LLM, greeting)
indemn config set <agent-id>                    # Update bot configuration
indemn config get <agent-id> --field prompt     # Get just the system prompt
indemn config set <agent-id> --prompt "..."     # Set system prompt (also: --prompt-file <path>)
indemn config set <agent-id> --model "..."      # Set LLM model

indemn functions list <agent-id>                # List functions for agent
indemn functions create <agent-id>              # Create function
indemn functions update <agent-id> <func-id>    # Update function (agent-id required — API is bot-scoped)
indemn functions delete <agent-id> <func-id>    # Delete function (agent-id required)
indemn functions test <agent-id> <func-id>      # Test REST API function
indemn functions export <agent-id>              # Export all functions
indemn functions import <agent-id> --url "..."  # Import functions from URL

indemn kb list                                  # List knowledge bases in org
indemn kb create --name "..." --type qna        # Create KB (types: qna, url, file)
indemn kb get <kb-id>                           # Get KB details
indemn kb update <kb-id> --name "..."           # Update KB
indemn kb delete <kb-id>                        # Delete KB
indemn kb data list <kb-id>                     # List data sources in KB
indemn kb data add <kb-id>                      # Add data source (QA pair, URL, or file)
indemn kb data update <kb-id> <source-id>       # Update data source
indemn kb data delete <kb-id> <source-id>       # Delete data source
indemn kb link <agent-id> <kb-id> [<kb-id>...]  # Map KB(s) to agent (accepts array of KB IDs)
indemn kb unlink <agent-id> <kb-id>             # Remove KB mapping (SDK resolves mapping_id via lookup)
indemn kb export <kb-id> --format csv           # Export KB data
indemn kb import <kb-id>                        # Import KB data

indemn chat <agent-id>                          # Interactive chat session via Socket.IO

indemn eval run <agent-id>                      # Trigger evaluation run
indemn eval status <run-id>                     # Check run status (poll until completed/failed)
indemn eval results <run-id>                    # View detailed results
indemn eval bot-context <agent-id>              # Get bot context (prompt, tools, KBs)
indemn rubric list                              # List rubrics (optionally --agent-id filter)
indemn rubric get <rubric-id>                   # Get rubric (latest version)
indemn rubric create                            # Create rubric (interactive or --file)
indemn rubric update <rubric-id>                # Update rubric (creates new version)
indemn rubric delete <rubric-id>                # Delete rubric (all versions)
indemn rubric versions <rubric-id>              # List rubric versions
indemn testset list                             # List test sets
indemn testset get <testset-id>                 # Get test set (latest version)
indemn testset create                           # Create test set (interactive or --file)
indemn testset update <testset-id>              # Update test set (creates new version)
indemn testset delete <testset-id>              # Delete test set (all versions)
indemn testset versions <testset-id>            # List test set versions

indemn mcp serve                                # Start MCP server
```

**Output:** Defaults to human-readable tables, `--json` flag for scripting. `--env dev|production` flag on any command to override default environment. `--limit` and `--page` flags on list commands for pagination (APIs return at most 100-1000 results).

**Auth commands (`login`, `logout`, `whoami`)** are CLI-only — no corresponding MCP tools. Auth is session-level, configured via environment variables for MCP (`INDEMN_API_KEY`).

### Implementation Notes

**`indemn config get/set`:** These are convenience wrappers over the bot configurations endpoint (`GET/PUT /organization/:org_id/ai-studio/bots/:id_bot/configurations`). The system prompt is at `ai_config.system_prompt` within the configuration object. The SDK extracts/injects specific fields.

**`indemn kb link`:** Calls `POST /organization/:org_id/ai-studio/bots/:id_bot/mappings` with body `{ id_kb: ["kb_id_1", "kb_id_2"] }` — the API expects an array of KB IDs.

**`indemn kb unlink`:** The API deletes by `mapping_id`, not `kb_id`. The SDK must first `GET /mappings` for the agent, find the mapping with the matching `kb_id`, then `DELETE /mappings/:mapping_id`.

**`indemn functions update/delete`:** The Copilot Server API nests functions under bots (`/bots/:id_bot/functions/:id_function`), so the agent-id is required for all function operations.

**`indemn agents clone`:** Calls `POST /organization/:org_id/ai-studio/v2/bots/clone` with body `{ source_id_bot: "<agent-id>" }`.

**`indemn kb data add` with file type:** Knowledge bases of type `file` require multipart form uploads via `POST /:id_kb/upload-urls` (FormData with file + metadata). The SDK must handle multipart encoding, distinct from the standard JSON API calls used everywhere else.

**MCP `get_prompt`/`set_prompt` tools:** These are convenience wrappers that call the same underlying `get_config`/`set_config` SDK methods, extracting/injecting only the `ai_config.system_prompt` field. They exist as separate MCP tools for ergonomics — Claude can call `set_prompt` directly without needing to know the full configuration structure.

---

## Chat Protocol

`indemn chat` connects through **middleware-socket-service** via Socket.IO — the same path as the production widget. This ensures CLI chat behavior matches what end users experience.

```
Source: middleware-socket-service/utils/clientSocketListners.js
        middleware-socket-service/utils/messageStream.js

Connection URL: https://proxy.indemn.ai (prod) or https://devproxy.indemn.ai (dev)
Protocol: Socket.IO 4.x
Auth: None required (CORS: *)
```

### Event Sequence

```
CLI                              MIDDLEWARE                    BOT-SERVICE
 |                                  |                              |
 |-- session_request ------------>  |                              |
 |   {                              |                              |
 |     session_id: null,            |-- validate bot               |
 |     bot_type: "<id-or-name>",    |-- create session_id          |
 |     user_id: "<uuid>",          |-- store in Redis             |
 |     customData: {}               |-- join Socket.IO room        |
 |   }                              |                              |
 |                                  |-- publish session_confirm    |
 |                                  |-- trigger initial greeting   |
 | <-- stream_bot_uttered (×N) ---- |  (initial greeting streams   |
 |   { text, streaming, streamId,   |   BEFORE session_confirm)    |
 |     isFirstChunk, streamFinished }|                              |
 |                                  |                              |
 | <-- session_confirm ------------ |  (emitted AFTER greeting)    |
 |   { session_id, bot_type }       |                              |
 |                                  |                              |
 |-- user_uttered ----------------> |                              |
 |   {                              |-- publish to RabbitMQ        |
 |     message: "user text",        |-- call /chat/invoke -------> |
 |     messageType: "text",         |                              |
 |     bot_type, user_id,           | <-- stream response -------- |
 |     session_id,                  |                              |
 |     is_user_message_sent: true   |                              |
 |   }                              |                              |
 |                                  |                              |
 | <-- stream_bot_uttered (×N) ---- |                              |
 |   { text chunks... }             |                              |
 | <-- stream_bot_uttered ----------|                              |
 |   { streamFinished: true }       |  (end of response)           |
 |                                  |                              |
 |-- session_closed --------------> |                              |
 |   { session_id }                 |-- mark closed in Redis       |
 |                                  |                              |
```

### CLI Implementation

The CLI chat client needs:
1. **socket.io-client** npm package for Socket.IO 4.x connection
2. Handle `stream_bot_uttered` events that may arrive BEFORE `session_confirm` (greeting streams first, then confirm — see `middleware-socket-service/utils/serverSocketListners.js` lines 64-178)
3. Stream text chunks to stdout as they arrive (`isFirstChunk` → start new line, intermediate → append, `streamFinished` → newline)
4. Readline interface for user input
5. Session persistence (store `session_id` to resume conversations with `--session`)
6. `bot_type` accepts either the agent's MongoDB ObjectId string OR its name string — the middleware checks `ObjectId.isValid(bot_type)` and resolves accordingly. **Prefer ObjectId** because name lookup (`{ bot_name: bot_type }`) is non-unique — multiple bots can share a name, causing unpredictable resolution. ObjectId is guaranteed unique.
7. **Silent failure on invalid bot:** If `bot_type` resolves to no bot (invalid ID/name, or bot is trashed), the middleware silently returns with no error event emitted to the client (`clientSocketListners.js` lines 47-51). The CLI must implement its own timeout (e.g., 10 seconds waiting for `session_confirm`) and display an error if it never arrives.

---

## MCP Tools

Mirror CLI commands 1:1. All tools return structured JSON.

```
# Agent management
list_agents, get_agent, create_agent, update_agent, delete_agent, clone_agent

# Configuration (prompt, LLM, greeting)
get_config, set_config, get_prompt, set_prompt

# Functions (all require agent_id)
list_functions, create_function, update_function, delete_function,
test_function, export_functions, import_functions

# Knowledge bases
list_knowledge_bases, get_knowledge_base, create_knowledge_base,
update_knowledge_base, delete_knowledge_base
list_kb_data, add_kb_data, update_kb_data, delete_kb_data
link_kb, unlink_kb, export_kb, import_kb

# Chat
chat_with_agent

# Evaluations
run_evaluation, get_eval_status, get_eval_results, get_bot_context

# Rubrics (versioned)
list_rubrics, get_rubric, create_rubric, update_rubric, delete_rubric,
list_rubric_versions

# Test sets (versioned)
list_test_sets, get_test_set, create_test_set, update_test_set,
delete_test_set, list_test_set_versions
```

---

## Skills

| Skill | Purpose | MCP Tools Used |
|-------|---------|----------------|
| **eval-orchestration** | Full evaluation lifecycle — bot context, directive allocation, rubric, test set, run, analyze | `get_bot_context`, `get_prompt`, `list_functions`, `create_rubric`, `create_test_set`, `run_evaluation`, `get_eval_results` |
| **test-set-creation** | Design test sets — multi-turn scenarios with personas, single-turn diagnostics, voice simulations | `get_bot_context`, `get_prompt`, `create_test_set` |
| **rubric-creation** | Create universal behavioral rubrics from prompt analysis with 3-message self-check | `get_bot_context`, `get_prompt`, `create_rubric` |
| **agent-setup** | End-to-end agent creation — name, prompt, functions, KB, test chat | `create_agent`, `set_prompt`, `create_function`, `create_knowledge_base`, `link_kb`, `chat_with_agent` |

Skills are migrated from Percy Service (`percy-service/skills/evaluations/`) and adapted for the MCP tool interface. Percy Service keeps its own copies for Jarvis runtime use — the two may diverge over time.

---

## Plugin Structure

The plugin follows the Claude Code plugin format verified from installed plugins at `~/.claude/plugins/`.

```
Source: ~/.claude/plugins/cache/*/  (installed plugin examples)
        ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/plugin-structure/

indemn-cli/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── skills/
│   ├── eval-orchestration/
│   │   └── SKILL.md
│   ├── test-set-creation/
│   │   └── SKILL.md
│   ├── rubric-creation/
│   │   └── SKILL.md
│   └── agent-setup/
│       └── SKILL.md
└── [src/, package.json, etc.]
```

### .claude-plugin/plugin.json

`plugin.json` is metadata only — it does NOT reference `.mcp.json`. Claude Code discovers `.mcp.json` by convention at the repo root (same as any project). Verified against installed plugins at `~/.claude/plugins/cache/` (e.g., `linear/`, `frontend-design/`) — none have a `mcpServers` field in `plugin.json`.

```json
{
  "name": "indemn-cli",
  "version": "1.0.0",
  "description": "Manage Indemn AI agents — create, configure, evaluate, and chat with agents programmatically",
  "author": {
    "name": "Indemn",
    "email": "support@indemn.com"
  },
  "homepage": "https://docs.indemn.com/cli",
  "repository": "https://github.com/indemn-ai/indemn-cli",
  "license": "MIT",
  "keywords": ["ai-agents", "insurance", "evaluations", "indemn"]
}
```

### .mcp.json

Flat format — server definitions at the top level, NOT nested under a `"mcpServers"` key. Verified against the Linear plugin's `.mcp.json` at `~/.claude/plugins/cache/claude-plugins-official/linear/`.

```json
{
  "indemn": {
    "command": "npx",
    "args": ["@indemn/cli", "mcp", "serve"],
    "env": {
      "INDEMN_API_KEY": "${INDEMN_API_KEY}"
    }
  }
}
```

### Install

```bash
claude plugins install @indemn/cli
```

---

## Rollout

### Phase 1 — Internal (2-3 weeks)
- Build SDK + CLI + MCP server (new `indemn-cli` repo)
- Add API key infrastructure to Copilot Server (collection, endpoints, Passport strategy)
- Ship skills (migrated from Percy Service + new agent-setup)
- Package as Claude Code plugin
- Chat via Socket.IO through middleware-socket-service
- Dogfood with engineers and conversational designers
- Includes: agent CRUD, clone, config/prompt management, functions (full CRUD + test + import/export), KB (full CRUD + data sources + link/unlink), chat, evaluations (trigger + status + results), rubric CRUD, test set CRUD
- **Note:** Evaluation commands call the Evaluations Service without API key auth in Phase 1 (the service has no auth today and relies on network-level security). This is acceptable for internal use. Phase 2 adds proper auth for external customers.

### Phase 2 — Customer-ready (2-3 weeks after Phase 1)
- API key management UI in dashboard (Settings → API Keys)
- **Evaluations Service auth** — build FastAPI middleware for API key validation (greenfield — no auth exists today)
- Developer documentation
- Published to npm as `@indemn/cli`
- OpenAPI spec audit and update to match actual API behavior
- Rate limiting on API key endpoints
- Agent export/import (full config + functions + KBs as portable bundle)

### Phase 3 — Ecosystem (ongoing)
- Additional skills based on usage patterns
- Analytics/observability commands
- Conversation history access
- Webhook management via CLI
- Voice configuration management
- Generated TypeScript SDK types from OpenAPI spec for customers building their own integrations

### Not in Scope
- Rewriting Copilot Server APIs — we wrap what exists
- Building a developer portal — markdown docs initially
- V2 agent management via Percy Service — V1 through Copilot Server for now

---

## Appendix A: Key Request/Response Shapes

### Agent Create
```
POST /api/organization/:org_id/ai-studio/bots
Body: { "name": "My Agent", "channels": ["WEB"] }
Response: { "success": true, "data": { "_id": "...", "name": "...", ... } }
```

### Agent Update
```
PUT /api/organization/:org_id/ai-studio/bots/:id_bot
Body: { "name": "...", "description": "...", "webhook_url": "...", "webhook_enabled": true }
```

### Bot Configuration Get/Set
```
GET /api/organization/:org_id/ai-studio/bots/:id_bot/configurations
Response: { "success": true, "data": {
  "ai_config": {
    "system_prompt": "You are...",
    "system_prompt_ops": {...},
    "use_default_prompt": false,
    "kb_configuration": { "namespace": "...", "index_name": "...", "embedding_provider": "..." },
    "is_reranking_enabled": true,
    "identify_next_step_enabled": true
  },
  "first_message": { "text": "Hello!", "quick_replies": [...] },
  "is_button_enabled": true
}}

PUT /api/organization/:org_id/ai-studio/bots/:id_bot/configurations
Body: { "system_prompt": "You are a helpful insurance agent...", "first_message": { "text": "Hi!" } }
```

### Function Create
```
POST /api/organization/:org_id/ai-studio/bots/:id_bot/functions
Body: { "type": "rest_api", "description": "Get quote details" }
Response: { "success": true, "data": { "_id": "...", "type": "...", ... } }
```

### KB Mapping Create
```
POST /api/organization/:org_id/ai-studio/bots/:id_bot/mappings
Body: { "id_kb": ["kb_id_1", "kb_id_2"] }
Response: { "success": true, "data": [{ "_id": "mapping_id", "id_bot": "...", "id_kb": "..." }] }
```

### KB Mapping Delete (by mapping ID, not KB ID)
```
DELETE /api/organization/:org_id/ai-studio/bots/:id_bot/mappings/:id_mapping
```

### Evaluation Trigger (V2 path — used by CLI)
```
Source: evaluations/src/indemn_evals/api/routes/evaluations.py lines 42-87

POST https://evaluations.indemn.ai/api/v1/evaluations
Body: {
  "bot_id": "agent-id",                    # Required — MongoDB ObjectId for tiledesk bot
  "test_set_id": "test-set-id",            # Required for V2
  "rubric_id": "rubric-id",                # Optional (rubric rules applied if provided)
  "concurrency": 1,                        # Default 1
  "eval_model": "openai:gpt-4.1-mini",    # Default eval judge model
  "keep": true,                            # Default true — keep dataset after run
  "limit": null,                           # Optional — limit number of test items
  "component_scope": null,                 # Optional — filter by: prompt|knowledge_base|function|general
  "component_ids": [],                     # Optional — filter by specific component IDs
  "conversation_ids": [],                  # Optional — for transcript mode
  "mode": null                             # Optional — set to "transcript" for historical eval
}
Response: {
  "run_id": "...",
  "dataset_id": "...",
  "config_id": "...",
  "status": "pending",
  "total": 15,
  "items_count": 15,
  "rules_count": 6,
  "component_scope_filter": null,
  "component_ids_filter": []
}
```

Note: V1 legacy path uses `POST /api/v1/runs` with `dataset_id` + `agent_id` + `question_set_id`. Not exposed in the CLI.

### Evaluation Run Status
```
Source: evaluations/src/indemn_evals/api/routes/runs.py

GET https://evaluations.indemn.ai/api/v1/runs/:run_id
Response: {
  "run_id": "...",
  "dataset_id": "...",
  "agent_id": "...",
  "status": "pending|running|completed|failed",
  "total": 15,
  "completed": 12,
  "passed": 10,
  "failed": 2,
  "concurrency": 1,
  "started_at": "2026-03-12T...",
  "completed_at": "2026-03-12T...",
  "error": null,                           # Present when status is "failed"
  "langsmith_experiment_id": "...",         # Present when completed
  "criteria_passed": 45,
  "criteria_total": 50,
  "rubric_rules_passed": 8,
  "rubric_rules_total": 10,
  "component_scores": { "prompt": { "score": 0.95, "total": 20, "passed": 19 }, ... },
  "rubric_id": "...",                      # Lineage tracking
  "rubric_version": 1,
  "test_set_id": "...",
  "test_set_version": 1,
  "bot_llm_provider": "anthropic",         # LLM config snapshot at run time
  "bot_llm_model": "claude-sonnet-4-20250514"
}
```

### Rubric Create
```
POST https://evaluations.indemn.ai/api/v1/rubrics
Body: {
  "agent_id": "...",
  "name": "Universal Rules",
  "rules": [
    {
      "id": "rule_01",
      "name": "No Hallucination",
      "severity": "high",
      "category": "accuracy",
      "description": "...",
      "evaluation_criteria": { "pass_conditions": [...], "fail_conditions": [...] }
    }
  ]
}
Response: { "rubric_id": "...", "version": 1, ... }
```

### Test Set Create
```
POST https://evaluations.indemn.ai/api/v1/test-sets
Body: {
  "agent_id": "...",
  "name": "Core Workflows",
  "items": [
    {
      "type": "single_turn",
      "name": "Greeting test",
      "inputs": { "message": "Hello" },
      "expected": { "success_criteria": ["Responds with greeting", "Identifies as insurance agent"] }
    },
    {
      "type": "scenario",
      "name": "Happy path quote",
      "inputs": {
        "initial_message": "I need a quote",
        "persona": "Cooperative user who provides all information readily",
        "max_turns": 5
      },
      "expected": { "success_criteria": ["Collects name, age, coverage type", "Provides quote"] }
    }
  ]
}
Response: { "test_set_id": "...", "version": 1, ... }
```
