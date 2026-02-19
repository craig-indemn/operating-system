---
ask: "Create an initial context artifact for the platform-development project that serves as the definitive knowledge base for LLM sessions working on indemn-platform-v2, evaluations, copilot-dashboard, bot-service, and supporting services"
created: 2026-02-19
workstream: platform-development
session: 2026-02-19-a
sources:
  - type: github
    description: "Git history, branch state, and uncommitted changes across 5 repos"
  - type: github
    description: "CLAUDE.md files from indemn-platform-v2, bot-service, and Repositories root"
  - type: github
    description: "docs/plans/ directory in indemn-platform-v2 — 80+ design docs, specs, and handoffs"
  - type: github
    description: "Evaluations repo README and directory structure"
  - type: github
    description: "Copilot-dashboard PR history and file structure"
---

# Platform Development — Initial Context

Definitive context document for all LLM sessions working on the Indemn agent platform. Covers architecture, current state, key patterns, known issues, and development workflows across all services.

---

## 1. What Indemn Is

Indemn is an AI agent platform for insurance — conversational agents (chat + voice) for lead generation, FAQ, sales funnels, and customer service. Agents are embedded on customer websites via a widget and can access knowledge bases and tools.

The platform has **two distinct agent systems**:

| System | Runtime | Config DB | Config UI | How it works |
|--------|---------|-----------|-----------|-------------|
| **V1 Agents** | bot-service (:8001) | tiledesk (`faq_kbs`, `bot_configurations`) | copilot-dashboard (Angular :4500) | Widget -> middleware -> bot-service `/chat/invoke` -> LLM |
| **V2 Agents** | indemn-platform-v2 (:8003) | indemn_platform (`agents`, `templates`) | Jarvis (AI agent builder) | Config-driven LangGraph, LLM calls direct to Anthropic/OpenAI |

**Jarvis** is itself a V2 agent that builds other agents. Its LLM calls go directly to Anthropic via `langchain-anthropic` — bot-service is NOT involved. Bot-service is only involved when the evaluation service tests a V1 agent.

---

## 2. Service Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTENDS                                       │
│  copilot-dashboard (:4500)  │  platform-v2 UI (:5173/5174)  │  POS (:3002) │
│  Angular, hosts federation  │  React, federation source      │  Chat widget │
└────────────┬────────────────┴──────────────┬─────────────────┴──────┬───────┘
             │                               │                        │
             ▼                               ▼                        ▼
┌─────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────┐
│  copilot-server     │  │  indemn-platform-v2      │  │  middleware-socket    │
│  (:3000) Node.js    │  │  (:8003) FastAPI          │  │  (:8000) Socket.IO   │
│  Auth + API gateway │  │  Agent builder + Jarvis   │  │  Chat relay          │
└─────────┬───────────┘  │  + Federation bundle      │  └──────────┬───────────┘
          │              └────────────┬───────────────┘             │
          │                          │                              ▼
          ▼                          ▼                   ┌──────────────────────┐
┌─────────────────────┐  ┌──────────────────────────┐   │  bot-service         │
│  conversation-svc   │  │  evaluations             │   │  (:8001) FastAPI     │
│  (:9090) Persists   │  │  (:8002) FastAPI          │   │  V1 agent runtime    │
│  chat history       │  │  Eval harness + LangSmith │   │  LLM + tools + KBs  │
└─────────────────────┘  └──────────────────────────┘   └──────────────────────┘
```

### Service Details

| Service | Repo Path | Port | Branch | Package Mgr | Hard Dependencies |
|---------|-----------|------|--------|-------------|-------------------|
| **indemn-platform-v2** | `/Users/home/Repositories/indemn-platform-v2` | 8003 | `main` | uv (Python), npm (UI) | MongoDB Atlas |
| **evaluations** | `/Users/home/Repositories/evaluations` | 8002 | `main` (use this, NOT `feat/ff_evaluation`) | uv (Python), npm (UI) | MongoDB Atlas, LangSmith, bot-service |
| **bot-service** | `/Users/home/Repositories/bot-service` | 8001 | `main` | uv | MongoDB, RabbitMQ, Redis, Pinecone |
| **copilot-dashboard** | `/Users/home/Repositories/copilot-dashboard` | 4500 | `fix/ci-docker-build-push` (local), PR #950 merged | npm | copilot-server for auth |
| **copilot-server** | `/Users/home/Repositories/copilot-server` | 3000 | `main` | npm | MongoDB |
| **middleware-socket-service** | `/Users/home/Repositories/middleware-socket-service` | 8000 | — | npm | MongoDB, RabbitMQ |
| **kb-service** | — | 8080 | — | uv | MongoDB, RabbitMQ, OpenAI |
| **conversation-service** | — | 9090 | — | uv | MongoDB, Redis, RabbitMQ |

**All infrastructure is remote** — MongoDB (Atlas), Redis (Cloud), RabbitMQ (Amazon MQ). Nothing runs locally except the application services.

---

## 3. Repo Structure: indemn-platform-v2

This is the primary repo for active development. It contains both the V2 agent platform AND the evaluation UI.

```
indemn_platform/
├── api/              # FastAPI routes: agents, v1_agents, templates, components,
│                     #   connectors, connector_bindings, conversations, scenarios,
│                     #   simulations, websocket, org_evaluations, deps, auth, schemas, settings
├── components/       # Graph node implementations: parameter_collection, supervisor,
│                     #   deep_agent, router, connector_invocation
├── connectors/       # Connector framework + implementations/platform_api/
│   └── implementations/platform_api/evaluations.py  # 7 connectors
├── graph_factory/    # Config → LangGraph: factory, compiler, state_builder, llm_factory
├── simulation/       # Simulation harness: harness, runner, scenario, evaluator
├── models/           # Pydantic: agent, v1_agent, template, component, connector, etc.
├── repositories/     # Data access (per-model repos, v1_agent reads from tiledesk DB)
├── jarvis/           # Jarvis prompts + permission scopes + runner.py (headless jobs)
└── scoring.py        # Single source of truth for score calculation (backend)

ui/src/
├── pages/            # AgentList, AgentDetail, AgentDetailV1, BuildAgent, JarvisChat,
│                     #   EvaluationRunDetail, Templates/Components/Connectors CRUD
├── components/
│   ├── evaluation/   # V1: EvaluationMatrix, QuestionSets*. V2: TestResultCard,
│   │                 #   ConversationModal, EvaluationSummaryDashboard, TestSets*
│   ├── report/       # PDF: EvalReportDocument, AgentCardDocument
│   ├── graph/        # React Flow visualization
│   ├── chat/         # Chat interface components
│   └── builder/      # Agent builder components
├── federation/       # Angular integration via Module Federation + Shadow DOM
│   ├── createShadowMount.tsx    # CSS isolation factory
│   ├── EvaluationsPanel.ts      # mountEvaluationsPanel()
│   ├── EvaluationRunDetail.ts   # mountEvaluationRunDetail()
│   ├── AgentOverview.tsx        # mountAgentOverview()
│   ├── OrgEvaluations.tsx       # Org-wide evaluations
│   ├── JarvisChat.tsx           # Jarvis modal with federation context
│   ├── FederatedProvider.tsx    # Sets apiClient.defaults.baseURL from platformApiUrl
│   └── styles.ts               # Generated CSS string (from build)
├── api/hooks/        # React Query hooks
├── lib/
│   ├── scoring.ts    # Single source of truth for score calculation (frontend)
│   ├── generateEvalReport.tsx
│   └── generateAgentCard.tsx
└── vite.federation.config.ts    # Federation-specific Vite config

scripts/
├── seed_components.py           # Seed component definitions (required for Jarvis)
└── seed_jarvis_templates.py     # Seed Jarvis templates + 3 evaluation prompts

skills/evaluations/              # AI agent workflow skills for Jarvis
docs/plans/                      # 80+ design docs, specs, handoffs (KEY REFERENCE)
```

### Context Recovery

The `docs/plans/` directory contains detailed design documents, implementation plans, and session handoff notes from ALL major work. When you need to understand **why** something was built a certain way, **what was tried and failed**, or **what decisions were made**, search these files first.

Key patterns:
- `*-handoff.md` — Session handoffs with what was done, what's left, known issues
- `*-spec.md` — Design specifications with locked decisions
- `*-implementation-plan.md` — Bead-by-bead breakdown of work
- `*-manual-testing-walkthrough.md` — Step-by-step verification procedures

---

## 4. The Evaluation Framework (V2)

### Architecture

Two evaluation layers, each test item gets both:

| Layer | Scope | Source | Purpose |
|-------|-------|--------|---------|
| **Success Criteria** | Per test item | Embedded in `TestItem.expected.success_criteria` | Did the bot do the right thing for THIS question? |
| **Rubric Rules** | Universal (all items) | Separate Rubric document (optional) | Guardrails: no harmful content, stays in scope, follows instructions |

### Scoring Model

Scores are counted at the **individual check level**, not the item level:

| Metric | Formula | Display |
|--------|---------|---------|
| **Criteria Score** | `criteria_passed / criteria_total` | e.g. 38/45 = **84%** |
| **Rubric Score** | `rubric_rules_passed / rubric_rules_total` | e.g. 89/105 = **85%** |

Both shown **side by side** — no single headline score. Color: green >= 70%, yellow >= 50%, red < 50%.

**Scoring modules** (single source of truth — ALL consumers import from these):
- Frontend: `ui/src/lib/scoring.ts` — `getRunScoreMetrics(run)`, `getRunCriteriaScore(run)`, `getRunRubricScore(run)`, `getResultsScoreMetrics(results[])`
- Backend: `indemn_platform/scoring.py`

**Backfill**: `list_runs` and `get_run` endpoints auto-compute and persist flat counts for old runs missing them via `backfill_flat_counts()`.

### Evaluation Flow

```
Jarvis (or manual) creates:
  1. TestSet (items with success_criteria)
  2. Rubric (universal guardrail rules, optional)
       ▼
POST /evaluations {bot_id, test_set_id, rubric_id?}
  → Groups items by type (single_turn / scenario)
  → For each item: calls bot-service /llm-evaluate/invoke (sync, returns tool trace)
  → LangSmith client.evaluate() runs:
      • criteria_evaluator (reads success_criteria from reference_outputs)
      • rubric_evaluators (one per rule, agent context baked into prompt)
  → Results: criteria_scores[] + rubric_scores[] + passed boolean per item
  → Run completion: compute flat counts
```

### Key Eval Endpoints

| Service | Endpoint | Purpose |
|---------|----------|---------|
| evaluations (:8002) | `POST /api/v1/evaluations` | Trigger evaluation run |
| evaluations (:8002) | `GET /api/v1/runs/{id}` | Run status + results |
| evaluations (:8002) | `GET /api/v1/test-sets` | CRUD test sets |
| evaluations (:8002) | `GET /api/v1/rubrics` | CRUD rubrics |
| bot-service (:8001) | `POST /llm-evaluate/invoke` | Sync endpoint for eval (returns tool trace) |
| platform-v2 (:8003) | `GET /api/v1/org-evaluations` | Org-wide eval status |

### Eval Connectors (for Jarvis)

All in `connectors/implementations/platform_api/evaluations.py` (120s timeout):
- **BotContextConnector** — Get V1 bot context (system prompt, tools, KBs)
- **TestSetsConnector** — CRUD test sets (replaces QuestionSetsConnector)
- **RubricsConnector** — CRUD rubrics
- **EvaluationsConnector** — Trigger runs (`test_set_id` preferred)
- **RunsConnector** — Get run status/results
- **QuestionSetsConnector** — Legacy, still present for historical reads

### Jarvis Evaluation Flow

Three prompts in `scripts/seed_jarvis_templates.py`:
- **EVALUATION_JARVIS_PROMPT** (~line 401): Orchestrates workflow, spawns 2 subagents in parallel
- **TEST_SET_CREATOR_PROMPT** (~line 892): Creates test items with observable success criteria
- **RUBRIC_CREATOR_PROMPT** (~line 1206): Creates universal guardrail rules

```
Jarvis → bot_context tool → analyze bot → spawn subagents:
  ├── test_set_creator → TestSets connector → creates 10-15 items
  └── rubric_creator → Rubrics connector → creates 5-8 universal rules
→ Auto-triggers evaluation → monitors → reports results
```

### V1/V2 Detection in UI

`results?.some(r => r.criteria_scores || r.item_type)` — V2 shows per-item cards + summary dashboard, V1 shows classic matrix.

---

## 5. Federation (React in Angular)

React components from indemn-platform-v2 render inside copilot-dashboard (Angular) via **Module Federation with Shadow DOM** for CSS isolation.

### Why Shadow DOM

Angular's PrimeFlex sets `.grid { display: flex }` which overrides Tailwind's `.grid { display: grid }`. CSS specificity tricks fail because Tailwind v4 uses `@layer utilities` (lower priority than unlayered CSS). Shadow DOM provides true encapsulation.

### How It Works

```
Angular (copilot-dashboard :4500)
  │
  loadRemoteModule('localhost:5173/assets/remoteEntry.js')
  │
  Angular wrapper component (in _react_wrappers/)
  │
  createShadowMount() → creates shadow root → injects CSS
  │
  React renders inside shadow root (Tailwind works correctly)
```

**Build time:** Vite plugin embeds all CSS as a JS string constant (`federation/styles.ts`)
**Mount time:** `createShadowMount` creates shadow root, injects CSS as `<style>` element
**Render:** React renders inside shadow root with full style isolation

### Federated Components

| React Component | Angular Wrapper | Mount Function |
|----------------|----------------|----------------|
| AgentOverview | `agent-overview.component.ts` | `mountAgentOverview()` |
| EvaluationsPanel | `evaluations-panel.component.ts` | `mountEvaluationsPanel()` |
| EvaluationRunDetail | `evaluation-run-detail.component.ts` | `mountEvaluationRunDetail()` |
| JarvisChat | `jarvis-chat.component.ts` | `mountJarvisChat()` |
| OrgEvaluations | `org-evaluations.component.ts` | `mountOrgEvaluations()` |

### Two API Clients in React

| Client | Fed Prop | Standalone Default | Used By |
|--------|----------|-------------------|---------|
| `apiClient` | `platformApiUrl` | `/api/v1` (relative) | useAgent, useAgents, useUpdateLifecycle, useUserPermissions |
| `EvaluationApiClient` | `apiBaseUrl` (evaluationServiceUrl) | `/eval-api/v1` (relative) | useEvaluationRuns, useTestSets, useRubrics, etc. |

### Federation Build & Serve

```bash
# Build + serve federation
cd ui && npm run build:federation && npx serve dist-federation -l 5173 --cors -n

# After code changes: rebuild + restart + hard refresh Angular
lsof -ti :5173 | xargs kill -9 2>/dev/null
npm run build:federation && npx serve dist-federation -l 5173 --cors -n
# Then Cmd+Shift+R in Angular browser
```

**Federation services needed:** copilot-server (3000), copilot-dashboard (4500), federation (5173), platform-v2 (8003)

### Federation Context Flow (Angular -> Jarvis)

```
Angular bot-details.component.ts
    │ openJarvisModal() sets jarvisContext = { page, botId, action }
    ▼
Angular wrapper → mountJarvisChat(container, { context, ... })
    ▼
federation/JarvisChat.tsx (JarvisAppWrapper)
    │ Extracts action → initialPrompt, passes context as federationContext
    ▼
federation/components/JarvisApp.tsx → pages/JarvisChat.tsx
    │ getCombinedContext() merges federationContext with BuilderContext
    ▼
hooks/useJarvisChat.ts (sendMessage includes context in WebSocket payload)
    ▼
api/websocket.py format_jarvis_context()
    │ "CRITICAL: User is viewing V1 bot with bot_id=XXX"
    ▼
Jarvis LLM → recognizes bot → proceeds with workflow
```

---

## 6. Jarvis — The AI Agent Builder

Jarvis is a V2 agent (deep_agent component) that builds other agents through conversation. Calls Anthropic API **directly** — NOT through bot-service.

### Templates

| Template ID | Purpose |
|-------------|---------|
| `jarvis_indemn_v1` | Full access (create components, public templates) |
| `jarvis_org_admin_v1` | Org-scoped (create templates/agents within org) |
| `jarvis_user_v1` | Read-only (view agents, test connectors) |
| `jarvis_evaluation_v1` | Evaluation-focused (rubrics, test sets, runs) |

### Tools (Platform API Connectors)

`list_agents`, `get_agent`, `create_agent`, `update_agent`, `list_templates`, `get_template`, `create_template`, `list_components`, `get_component`, `list_connectors`, `get_connector`, `test_connector`, `bot_context`, `rubrics_*`, `question_sets_*`, `test_sets_*`, `evaluations_*`, `runs_*`

### Workflow

1. **Understand** — Gather user intent and requirements
2. **Discover** — List available templates, components, connectors
3. **Propose** — Suggest agent configuration
4. **Refine** — Iterate based on feedback
5. **Confirm** — Get explicit user approval
6. **Finalize** — Create agent via API

Never finalize without user approval. Seeds required: `seed_components.py` then `seed_jarvis_templates.py`. To update Jarvis: delete agent (`curl -X DELETE .../agents/jarvis-default`), restart backend.

### Headless Runner

`jarvis/runner.py` handles background baseline generation. Polls `jarvis_jobs` collection, initialized in `main.py` via `set_jarvis_runner_dependencies()`. Uses same GraphFactory.

---

## 7. V2 Agent Architecture

### Core Hierarchy

**Component** (atomic node) -> **Connector** (external integration) -> **Template** (reusable graph) -> **Agent** (customer instance)

### Graph Compilation

```
MongoDB config → GraphFactory.get_graph(agent_id) → GraphCompiler → CompiledStateGraph → Execute
```

### Key Data Models

**AgentModel (V2):**
```python
{
    "agent_id": str,           # Slug ID
    "name": str,
    "graph": {                 # Agent's OWN graph
        "state_schema": {...},
        "nodes": [...],        # Each: {id, component_id, config}
        "edges": [...],        # {from, to}
        "conditional_edges": [...]
    },
    "template_id": ObjectId,   # Origin tracking (optional)
    "overrides": {},
    "connector_bindings": {},
    "organization_id": ObjectId,
    "status": "draft|ready_for_testing|active",
    "is_v2": True
}
```

**V1AgentDetail** (read-only from tiledesk DB):
```python
{
    "id": str,                 # MongoDB ObjectId string
    "name": str,
    "channels": ["web", "whatsapp"],
    "organization_id": str,
    "system_prompt": str,
    "tools": [{...}],
    "knowledge_bases": [{...}],
    "llm_config": {"provider": str, "model": str, "parameters": {...}}
}
```

**TemplateModel:**
```python
{
    "template_id": str,
    "graph": {
        "nodes": [{...}],
        "edges": [{...}],
        "conditional_edges": [{...}]
    },
    "llm_config": {...},
    "visibility": "public|organization|private"
}
```

### Authentication

```python
# Every API request (from deps.py):
AuthContext(user_id: ObjectId, organization_id: ObjectId, is_indemn_employee: bool)
# Org scoping on all queries, indemn employees see all
```

### WebSocket Event Flow (Jarvis)

```
User message → WebSocket → Jarvis (deep_agent) → Platform API tools → REST API → MongoDB
                  (Anthropic API direct, NOT bot-service)                     ↓
UI ← BuilderContext ← WebSocket broadcast ← Event emission ←────────────────┘
```

---

## 8. Bot-Service Architecture

Bot-service is the V1 agent execution runtime. Key endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /chat` | Main conversational agent (LangServe streaming) |
| `POST /llm-evaluate/invoke` | Sync endpoint for evaluations (returns tool trace) |
| `POST /suggestions/invoke` | CSR response suggestions |
| `POST /conversation/summary/invoke` | Summarize conversation |

Key internals:
- `app/services/graphs/bot_agent_graph.py` — LangGraph state machine
- `app/utils/model_utils.py` — Multi-provider LLM abstraction (OpenAI, Anthropic, Google, Cohere, Groq, Bedrock, Mistral, X.AI)
- `app/services/tools/` — Tool implementations
- `app/services/bot_details.py` — Bot config fetching from MongoDB

**Critical for evaluations**: Middleware-socket-service (:8000) MUST be running. Bot-service crashes in `slot_sync.py` when it can't POST to localhost:8000.

---

## 9. Deployment Infrastructure

### Dev EC2 — All Deployed

| Subdomain | Service | EC2 Port | Container |
|-----------|---------|----------|-----------|
| `devcopilot.indemn.ai` | copilot-dashboard (Angular) | 4500 | existing |
| `devplatform.indemn.ai` | platform-v2 (React + API + federation) | 8006 | `copilot-dashboard-react` |
| `devevaluations.indemn.ai` | evaluations | 8005 | `evaluations` |

### Container Architecture (platform-v2 and evaluations)

Single container per service: nginx + uvicorn + supervisord

```
Docker Container
  nginx (port 80 → mapped to host port)
    ├── /            → React SPA (dist/)
    ├── /api/v1/     → proxy uvicorn :8000
    ├── /ws          → proxy uvicorn :8000 (websocket)
    └── /eval-api/   → proxy evaluations container (platform-v2 only)
  uvicorn (port 8000, internal)
    └── FastAPI app
  supervisord (process manager)
```

### Config Flow (Angular -> React Federation in Production)

```
Dockerfile CMD (copilot-dashboard):
  envsubst < dashboard-config-template.json > dashboard-config.json
  → Replaces ${PLATFORM_API_URL}, ${PLATFORM_WS_URL}, ${EVALUATION_SERVICE_URL}, ${FEDERATION_REMOTE_URL}

Angular startup:
  AppConfigService loads dashboard-config.json (overrides environment.ts)

React wrapper (federation):
  config.federationRemoteUrl → loadRemoteModule() → remoteEntry.js
  config.evaluationServiceUrl → EvaluationApiClient
  config.platformApiUrl → apiClient.defaults.baseURL
  config.platformWsUrl → Jarvis WebSocket
```

### Docker Images

| Service | Image | Registry |
|---------|-------|----------|
| platform-v2 | `copilot-dashboard-react` | ghcr.io/indemn-ai/copilot-dashboard-react |
| evaluations | `evaluations` | (Docker Hub or ghcr.io) |

### CI/CD

- Push to `main` -> build Docker image -> deploy to dev EC2 (self-hosted runner)
- Push to `prod` -> build Docker image -> deploy to prod EC2

---

## 10. Evaluation UI Flow

```
AgentDetailV1 (/agents/v1/:botId)
    ├── Header badges: Criteria % + Rubric % (from getRunScoreMetrics)
    ├── EvaluationSection (summary card with dual scores + runs table)
    │       └── Click run → EvaluationRunDetail (/agents/v1/:botId/runs/:runId)
    │                           ├── Run summary card
    │                           ├── Export PDF button → generateEvalReport()
    │                           ├── LangSmith link
    │                           └── V1: EvaluationMatrix with modals
    │                               V2: TestResultCard per item + EvaluationSummaryDashboard
    │
    └── Download Agent Card button → generateAgentCard()
            └── AgentCardDocument (6 pages, @react-pdf/renderer)
                ├── Cover (logo, V1 badge, name, channels, criteria rate)
                ├── System Prompt (full, monospace Courier)
                ├── Tools (2-column grid)
                ├── Knowledge Bases (2-column grid)
                ├── LLM Configuration (provider, model, params)
                └── Metadata (bot ID, org ID)

OrgEvaluations (/org-evaluations)
    └── Agent table with score column (criteria score from latest COMPLETED run)
        org_evaluations.py picks latest completed run, not just latest run
```

---

## 11. Local Development

### Starting Services

```bash
# Start a service group
cd /Users/home/Repositories && /opt/homebrew/bin/bash ./local-dev.sh start <group> --env=dev

# Groups: minimal, platform, chat, analytics, all
# "platform" = bot-service + platform-v2 + platform-v2-ui + evaluations
```

### Federation Development

```bash
# For federation testing (React in Angular):
# 1. Start required services
/opt/homebrew/bin/bash ./local-dev.sh start platform --env=dev

# 2. Replace dev server with federation build
lsof -ti :5173 | xargs kill -9 2>/dev/null
cd indemn-platform-v2/ui && npm run build:federation && npx serve dist-federation -l 5173 --cors -n &

# 3. Standalone React development (separate port)
cd indemn-platform-v2/ui && npm run dev -- --port 5174
```

### Login

**Dev login:** `support@indemn.ai` / `nzrjW3tZ9K3YiwtMWzBm`

If form doesn't work, authenticate via API:
```bash
TOKEN=$(curl -s -X POST http://localhost:3000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"support@indemn.ai","password":"nzrjW3tZ9K3YiwtMWzBm"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

### Test URLs

- Standalone React: `http://localhost:5174/agents/v1/{botId}`
- Angular: `http://localhost:4500/#/organization/{orgId}/ai-studio/bot/{botId}/configurations?tab=overview`
- Bot detail URL: `/#/organization/{orgId}/ai-studio/bot/{botId}/configurations?tab=overview`

### Seeding Data

```bash
cd /Users/home/Repositories/indemn-platform-v2
uv run python scripts/seed_components.py
uv run python scripts/seed_jarvis_templates.py
```

Required for Jarvis to work. Re-seed templates if Jarvis behaves unexpectedly, then delete jarvis-default and restart.

---

## 12. Key Gotchas

### Critical

1. **TWO Vite configs for federation:** `vite.config.ts` (dev/build) and `vite.federation.config.ts` (federation build). Exposes must be in BOTH or Angular gets "Cannot find remote module".
2. **dashboard-config.json clobbers environment.ts:** Angular's `AppConfigService` completely replaces config. For local dev, MUST have real values for `platformApiUrl`, `platformWsUrl`, `evaluationServiceUrl`, `federationRemoteUrl`. `${...}` placeholders cause silent failures.
3. **Platform-v2 is port 8003, NOT 8000.** Port 8000 is middleware-socket-service.
4. **Middleware must be running for evaluations.** Bot-service crashes in `slot_sync.py` without it.
5. **Eval service must use same MongoDB cluster** as platform backend. Mismatched clusters -> "Bot not found".
6. **Scoring is flat check-level, not item-level.** `scoring.ts` and `scoring.py` are the single source of truth. Never compute scores inline.

### Backend

7. **GraphFactory init** requires seeded templates/components.
8. **Jarvis agent persistence:** `jarvis-default` created once at startup. To update: delete agent, restart.
9. **Eval connector timeout:** 120s (not 10s) because LLM calls take 30s+.
10. **V1 Agent Repository** reads from shared tiledesk DB (different from platform DB).
11. **org_evaluations picks latest completed run** for scoring. Failed/pending/running runs are skipped.

### Frontend

12. **Federation bundle rebuild required** after ANY code changes to federated components. Hard refresh Angular after.
13. **Brand colors:** Iris `#4752a3`, Eggplant `#1e2553`, Lilac `#a67cb7`.
14. **Angular wrapper route params:** Read `organizationid` from `ActivatedRoute.snapshot.paramMap`, NOT `@Input()`.

---

## 13. Environment Variables

### Platform-v2

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `MONGO_URL` | Yes | `mongodb://localhost:27017` | MongoDB Atlas connection string |
| `MONGO_DB_NAME` | No | `indemn_platform` | |
| `OPENAI_API_KEY` | Yes | — | |
| `ANTHROPIC_API_KEY` | Yes | — | |
| `LANGSMITH_API_KEY` | No | — | Enables tracing |
| `EVALUATION_SERVICE_URL` | No | `http://localhost:8002` | |
| `PLATFORM_URL` | No | `http://localhost:8000` | Set to `:8003` for local dev |
| `BOT_SERVICE_URL` | No | `http://localhost:8001` | Used by eval engines |
| `VITE_FEDERATION_BASE_URL` | No | `http://localhost:5173` | Image URLs in federation |

### Evaluations

| Variable | Required | Default |
|----------|----------|---------|
| `LANGSMITH_API_KEY` | Yes | — |
| `OPENAI_API_KEY` | Yes | — |
| `MONGODB_URI` | No | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | No | `evaluations` |
| `BOT_SERVICE_URL` | No | `http://localhost:8001` |

### Bot-Service

`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MONGO_URL`, `MONGO_DB_NAME`, `REDIS_HOST`, `REDIS_PORT`, `RABBITMQ_CONNECT_URL`, `PINECONE_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT`

---

## 14. Current State (as of 2026-02-19)

### What's Built and Deployed

- V2 evaluation framework fully implemented (TestSets, criteria evaluator, tool trace, flat scoring)
- Federation integration: 5 React components rendering inside Angular via Shadow DOM
- Jarvis evaluation workflow with subagent spawning (test_set_creator + rubric_creator)
- Agent Card PDF generation (6-page)
- Evaluation Report PDF generation
- Org-level evaluations page
- Lifecycle badges and ownership transfer
- Docker + CI/CD for dev EC2 deployment
- AWS subdomains configured (devplatform, devevaluations, devcopilot)

### What Needs Work

- **Significant issues on dev deployment** that need resolution (user-reported)
- **Architecture choices** that need to be thought through
- Copilot-dashboard local branch is on `fix/ci-docker-build-push`, not `main`
- Platform-v2 has 2 uncommitted modified files (`useConversations.ts`, `useLocalStorage.ts`)
- Bot-service has an untracked `CLAUDE.md`
- Evaluations repo has untracked beads files and report JSON files

### Recent Copilot-Dashboard PRs (merged)

- #957 (Feb 19): JWT invalidation — AuditLogsService cleanup
- #956 (Feb 18): JWT invalidation and state management
- #955 (Feb 16): Cross-org project user error fix
- #954 (Feb 12): Docker build-push-action upgrade
- #953 (Feb 12): Navigation edge cases fix
- #952 (Feb 12): DEV -> PROD merge
- #950 (Feb 11): Federation platform API routing (our work)

### Recent Platform-v2 Commits (on main)

Latest: `8d48a7b` fix(nginx): add CORS headers for federation cross-origin loading
Prior work: Docker/CI/CD fixes, eval V2 scoring, Jarvis prompt refinement, org-evaluations, CLAUDE.md rewrite, federation integration

---

## 15. Testing with agent-browser

```bash
# Navigation
agent-browser open http://localhost:5174
agent-browser wait 3000 / agent-browser wait "text=Loaded"

# Screenshots
agent-browser screenshot /tmp/shot.png --full

# Interact
agent-browser click "text=Login"
agent-browser fill "input[type=email]" "user@example.com"
agent-browser press Enter

# AI-friendly snapshot
agent-browser snapshot -i    # Returns @e1, @e2, ... refs

# JavaScript evaluation
agent-browser eval "document.title"
agent-browser eval "localStorage.getItem('token')"

# Console & errors
agent-browser console / agent-browser errors

# Angular Login Flow
TOKEN=$(curl -s -X POST http://localhost:3000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"support@indemn.ai","password":"nzrjW3tZ9K3YiwtMWzBm"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
agent-browser eval "localStorage.setItem('token', '$TOKEN'); localStorage.setItem('organizationId', '670869511b48a100132672c9'); localStorage.setItem('userId', '65f839af9ca3710013305a3e'); 'done'"
agent-browser open "http://localhost:4500/#/organization/670869511b48a100132672c9/ai-studio/bots"
```

---

## 16. Copilot-Dashboard Deep Dive

The Angular app (`@indemn/copilot-dashboard`) is the primary management UI. Angular 17, PrimeNG, Bootstrap, Tailwind CSS (via PostCSS). Module Federation via `@angular-architects/module-federation ^17.0.0`. React 18.2 is a direct dependency for federation.

### App Structure

```
src/app/
├── ai-studio/              # THE KEY MODULE — bot management
│   ├── bot-details/        # Main bot detail page (sidebar tabs + content area)
│   ├── bots-list/          # Bot listing page
│   ├── bot-prompt/         # System prompt editor ("Behavior" tab)
│   ├── bot-functions/      # Functions tab
│   ├── bot-knowledge-bases/# Referenced KBs tab
│   ├── bot-sidebar-tabs/   # Sidebar tab navigation
│   ├── talk-to-ai-agent/   # "Talk to AI Agent" tab (chat widget)
│   ├── create-ai-agent/    # New agent creation
│   ├── org-functions/      # Org-level functions
│   ├── org-knowledge-bases/# Org-level KBs
│   ├── knowledge-base-details/  # KB detail page
│   └── voice/              # Phone settings tab
├── _react_wrappers/        # Federation Angular wrapper components
│   ├── agent-overview/     # mountAgentOverview — bot eval summary
│   ├── evaluations-panel/  # mountEvaluationsPanel — runs/rubrics/test sets tabs
│   ├── evaluation-run-detail/ # mountEvaluationRunDetail — single run detail
│   ├── jarvis-chat/        # mountJarvisChat — Jarvis modal
│   ├── org-evaluations/    # mountOrgEvaluations — org-wide eval dashboard
│   ├── flow-based-editor/  # mountFlowBasedEditor (commented out in template)
│   └── test1/              # Test component (unused)
├── services/               # 40+ Angular services
│   ├── app-config.service.ts  # CRITICAL: loads dashboard-config.json, overrides environment.ts
│   ├── ai-agents.service.ts   # Bot CRUD via copilot-server API
│   ├── ai-functions*.service.ts
│   ├── knowledge-base.service.ts
│   └── ...
├── auth/                   # Login, signup, MFA, organization create
├── ws_requests/            # Conversation/chat views
├── distribute/             # Agent distribution configuration
├── models/                 # TypeScript interfaces
└── core/                   # Guards (AuthGuard, AdminGuard, etc.)
```

### Bot Details Page (THE main integration point)

`bot-details.component.ts` is where federation, Jarvis, and evaluations all converge:

**Sidebar tabs** (via `bot-sidebar-tabs` component):
- `overview` → AgentOverview (federation, indemn employees only)
- `behavior` → BotPrompt (Angular native, system prompt editor)
- `referred-kb` → BotKnowledgeBases (Angular native)
- `functions` → BotFunctions (Angular native)
- `talk-to-ai-agent` → TalkToAiAgent (Angular native, chat widget)
- `phone-settings` → PhoneSettings (Angular native)
- `evaluations` → EvaluationsPanel OR EvaluationRunDetail (federation, indemn employees only)

**Jarvis integration:**
- Purple FAB button (bottom-right, `pi-sparkles` icon, `z-index: 40`)
- `openJarvisModal(action?)` sets context `{ page: 'bot-details', botId, action }`
- `onJarvisClosed()` increments `evaluationsRefreshTrigger` to trigger React data refetch
- Refresh uses DOM event (`evaluations-refresh`) NOT React remount, preserving tab state

**Feature gating:** `isIndemnEmployee` checks `localStorage user.email.endsWith('@indemn.ai')` — overview, evaluations, and Jarvis FAB are only visible to Indemn employees.

**Run detail navigation:** `handleNavigateToRun(runId)` switches to evaluations tab and sets `selectedRunId`, which swaps EvaluationsPanel for EvaluationRunDetail inline.

### Federation Wrapper Pattern

All 5 wrappers follow the same pattern:
1. `ngOnInit` → `loadComponent()`
2. Get `config` from `AppConfigService.getConfig()`
3. Get `remoteEntry` from `config.federationRemoteUrl`
4. `loadRemoteModule({ type: 'module', remoteEntry, exposedModule: './ComponentName' })`
5. Get container via `document.querySelector('#containerName')`
6. Call `mountFunctionName(container, { props })` — returns unmount function
7. `ngOnDestroy` calls `unmount()`

**Props passed to each federated component:**

| Component | Key Props |
|-----------|-----------|
| AgentOverview | botId, botUpdatedAt, authToken, apiBaseUrl, platformApiUrl, organizationId, onOpenJarvis, onNavigateToRun, onNavigateToTab |
| EvaluationsPanel | botId, organizationId, authToken, apiBaseUrl, platformApiUrl, onNavigateToRun, onOpenJarvis |
| EvaluationRunDetail | botId, runId, authToken, apiBaseUrl, platformApiUrl, organizationId, onBack |
| JarvisChat | visible, wsUrl, authToken, apiBaseUrl, platformApiUrl, organizationId, context, onClose |
| OrgEvaluations | authToken, apiBaseUrl, platformApiUrl, organizationId, userId, onNavigateToAgent, onNavigateToRun, onOpenJarvis |

### Config Flow

`AppConfigService` loads `dashboard-config.json` (fetched from `environment.remoteConfigUrl`) at startup and completely replaces the environment config. The committed version has `${PLACEHOLDER}` values for Docker envsubst. Local dev uses `skip-worktree` to keep localhost values.

**Critical config fields for federation:**
```json
{
  "platformApiUrl": "http://localhost:8003/api/v1",
  "platformWsUrl": "ws://localhost:8003/ws",
  "evaluationServiceUrl": "http://localhost:8002/api/v1",
  "federationRemoteUrl": "http://localhost:5173/assets/remoteEntry.js",
  "SERVER_BASE_URL": "http://localhost:3000/"
}
```

### Key Routes (AI Studio)

| Route | Component | Guard |
|-------|-----------|-------|
| `/organization/:orgId/ai-studio/bots` | BotsListComponent | Auth + setOrganization |
| `/organization/:orgId/ai-studio/bot/:botId/configurations` | BotDetailsComponent | Auth + setOrganization |
| `/organization/:orgId/ai-studio/evaluations` | OrgEvaluationsComponent | Auth + setOrganization |
| `/organization/:orgId/ai-studio/bot/create` | CreateAiAgentComponent | Auth + setOrganization |
| `/organization/:orgId/ai-studio/knowledge-bases` | OrgKnowledgeBasesComponent | Auth + setOrganization |
| `/organization/:orgId/ai-studio/functions` | OrgFunctionsComponent | Auth + setOrganization |
| `/organization/:orgId/ai-studio/reviews` | ReviewsComponent | Auth + setOrganization |

---

## 17. Related Repos

| Repo | Purpose | Notes |
|------|---------|-------|
| `indemn-platform-v2-stream-11` | Worktree for Stream 11 (entry point) | May still exist at `/Users/home/Repositories/` |
| `copilot-dashboard-react` | GitHub name for platform-v2 in indemn-ai org | `indemn-ai/copilot-dashboard-react` |
| `designs/` | Design mockups | `copilot_dashboard_evaluations.md` |

---

## 18. Code Style

- Simplicity over cleverness. Readable > clever.
- Components are atomic: single responsibility, defined inputs/outputs.
- No over-engineering. Solve today's problem.
- Full type hints on all Python functions.
- Comments explain why, not what.
- Brand colors: Iris `#4752a3`, Eggplant `#1e2553`, Lilac `#a67cb7`
- Severity: High `#3a4389`, Medium `#4752a3`, Low `#7c85c0`
