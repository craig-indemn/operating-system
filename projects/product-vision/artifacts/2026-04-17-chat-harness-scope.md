---
ask: "Scope the chat harness (Gates 3-4) from the design specs — every claim extracted, architectural decisions made, open questions resolved. The chat harness + assistant UI panel are one work item."
created: 2026-04-17
workstream: product-vision
session: 2026-04-17-a
sources:
  - type: artifact
    ref: "2026-04-11-base-ui-operational-surface.md"
    description: "Assistant panel design — placement, context, streaming, persistence, entity rendering"
  - type: artifact
    ref: "2026-04-11-authentication-design.md"
    description: "Default assistant auth — user JWT inheritance, owner_actor_id pattern"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5-consolidated.md"
    description: "Phase 4 assistant implementation (§4.7), Phase 5 harness pattern (§5.3)"
  - type: artifact
    ref: "2026-04-10-realtime-architecture-design.md"
    description: "Chat-kind Runtime, harness session lifecycle, mid-conversation events, handoff"
---

# Chat Harness + Assistant Panel Scope (Gates 3-4)

## What This Is

`indemn/runtime-chat-deepagents` — the second harness image. A WebSocket server that bridges the UI's assistant panel to the deepagents framework via CLI. One image serves many associates — the default per-user CRM Assistant AND any other chat-kind associate.

**This is one work item, not two.** The chat harness (server) and assistant panel (UI client) must be built and verified together. You can't test one without the other.

---

## 1. Design Claims Extracted (47 total, grouped by topic)

### 1.1 Assistant Panel — UI Design

**Placement**: "An always-visible assistant input in the top bar of every view — like a search bar, primary position, persistent." Not a right-side panel, not Cmd-K, not a floating widget. Slim input, keyboard-focused, `/` or Cmd-K to focus. (base-ui-operational-surface)

**Conversation panel**: Slides in from right (~400-500px wide) on engagement. Does NOT hide the current view — non-blocking. Users work in main view while assistant thinks. ESC closes, state persists. (base-ui-operational-surface)

**Streaming**: "Streaming responses visible token-by-token as the assistant generates them." (base-ui-operational-surface)

**Entity rendering**: "When the assistant returns entities, they render as the same interactive table/form components the rest of the UI uses. A query like 'show me the oldest triaging submissions' produces a mini interactive table with the same row actions as the full list view. The assistant is not generating prose about data — it renders the data using UI components." (base-ui-operational-surface)

**Persistent conversation**: "Each human user has one ongoing conversation thread with their default associate. Reopening the panel shows recent context. Multi-step operational work works across the sequence without re-grounding every time." (base-ui-operational-surface)

**Context-aware (implicit)**: "The UI sends a context payload with each assistant turn derived from the user's current state: `{view_type, current_entity, current_filter, role_focus, recent_actions}`. When the user types 'what's blocking this?' while looking at SUB-042, the assistant's context includes 'the user is looking at Submission SUB-042' and resolves 'this' implicitly." (base-ui-operational-surface)

**Real-time event subscription**: "The conversation panel is a running harness instance — subscribes to entity events for the user's context via `indemn events stream`. When SUB-042 changes mid-conversation, the assistant knows immediately." (base-ui-operational-surface)

**Not Clippy**: "Only responds when addressed. Silence is the default. No unprompted suggestions." (base-ui-operational-surface)

**CLI execution**: "The assistant can execute any CLI command the user has access to." (base-ui-operational-surface)

**Complexity ladder**: "click → pattern-match → instruct → command. Four surfaces (buttons, tables, assistant, CLI) same system, no privileged interface." (base-ui-operational-surface)

### 1.2 Authentication

**Default assistant = user projection**: "The default assistant is not an independent entity — it is a projection of the user into a running actor. Its harness authenticates using the user's session JWT (injected at session start). Every action taken by the assistant is audited as 'user X via default associate performed Y.' Permissions exactly match the user's. When the user logs out, the assistant's session dies with it." (authentication-design)

**Two auth modes on one harness**:
- Default assistant: user's session JWT (inherited at connection)
- Service associates: Runtime service token (from env var)
- Both valid on the same harness image — per-session detection based on connection metadata

**Owner-bound scheduled associates are different**: They use service tokens + `owner_actor_id` for credential resolution. NOT the chat harness pattern.

### 1.3 Harness Pattern (Server-Side)

**WebSocket server**: "Chat: WebSocket server (Python/Node, your choice)." (realtime-architecture-design Part 5)

**Image**: `indemn/runtime-chat-deepagents:X.Y.Z` — contains deepagents + WebSocket library + `indemn` CLI + bridge script. (realtime-architecture-design Part 4)

**CLI is the universal interface**: "The harness uses the CLI, not a separate Python SDK. This is the key design decision." (realtime-architecture-design Part 4)

**One harness, many associates**: "The harness is generic per kind+framework combination. When a session starts, the Runtime instance identifies WHICH associate this session is for and loads that Associate's configuration." (realtime-architecture-design Part 3)

**Three-layer config merge**: Runtime defaults → Associate override → Deployment override. Merged at session start. (Phase 4-5 spec § 5.3)

**Events stream subscription**: "Subscribe to scoped events for mid-conversation delivery. `indemn events stream --actor {associate_id} --interaction {interaction_id} --format json-lines`. Harness feeds it to the running agent." (Phase 4-5 spec § 5.3)

**Heartbeat loop**: Send heartbeat every 30s to keep Attention alive. (Phase 4-5 spec § 5.3)

**Graceful shutdown**: Transition Attention to closed, update Interaction status, best-effort cleanup on disconnect. (Phase 4-5 spec § 5.3)

### 1.4 Session Lifecycle

Per-WebSocket-connection lifecycle (from Phase 4-5 spec § 5.3 voice example, generalized to chat):

1. WebSocket connects (from UI or external client)
2. Identify associate from connection metadata (Deployment, direct invocation, or default)
3. Load associate config via CLI (`indemn actor get`)
4. Create Interaction entity (`indemn interaction create --channel-type chat`)
5. Open Attention (`purpose=real_time_session`, with `runtime_id`, `session_id`)
6. Three-layer LLM config merge
7. Build deepagents agent
8. Start `indemn events stream --interaction {id}` subprocess
9. Start heartbeat loop (30s intervals)
10. Process messages: user turn → agent → streamed response
11. Mid-conversation events fed to agent from events stream
12. On disconnect: close Attention, update Interaction status, cleanup

### 1.5 Handoff (Designed — Not an Open Question)

Full flow from realtime-architecture-design Part 9, Example 2 (CRM chat handoff):

**Associate handling mode** (default):
- User messages → WebSocket → harness → deepagents agent → response → WebSocket → UI
- Agent uses CLI for all OS operations

**Handoff trigger** (`indemn interaction transfer --to-role human_role` or `--to-actor actor_id`):
- Kernel updates `Interaction.handling_actor_id`
- Harness watches Interaction via Change Stream, detects the change
- Harness gracefully ends deepagents session
- Switches to "bridge to human" mode

**Human handling mode**:
- User messages → WebSocket → harness → writes to message queue for the human handler
- Human sees the conversation in their UI queue
- Human types response → UI submits via `indemn interaction respond`
- Harness picks up response via Change Stream → sends on WebSocket to user

**Hand back**:
- Human clicks "hand back" → `indemn interaction transfer --to-actor {original_associate}`
- Kernel updates `handling_actor_id` back
- Harness restarts deepagents session

**UI knows the mode** because it subscribes to Interaction entity via Change Streams. When `handling_actor_id` changes, UI switches display accordingly.

### 1.6 Mid-Conversation Event Delivery

**Mechanism**: "When a scoped watch matches an Attention with a `runtime_id` and `session_id`, the kernel writes the message to message_queue with `target_actor_id`. The harness's `indemn events stream` subscription picks it up via MongoDB Change Streams (~50-100ms latency)." (realtime-architecture-design Part 5)

**Example**: Payment completes during a conversation → watch fires → message with target_actor_id → harness events stream picks it up → feeds to running agent → agent says "Great news, the payment just completed."

---

## 2. Architectural Decisions Made (This Session)

### 2.1 Streaming Wire Format

**Decision**: WebSocket with typed JSON messages.

Harness → UI (server to client):
```json
{"type": "token", "content": "The"}
{"type": "tool_call", "name": "execute", "args": {"command": "indemn testtask get ..."}}
{"type": "tool_result", "name": "execute", "content": "{...}"}
{"type": "entity", "data": {"_id": "...", "type": "TestTask", "status": "...", ...}}
{"type": "event", "data": {"entity_type": "...", "change": "..."}}
{"type": "done"}
```

UI → Harness (client to server):
```json
{"type": "message", "content": "what's blocking this?", "context": {"view_type": "detail", "entity_type": "TestTask", "entity_id": "..."}}
{"type": "connect", "associate_id": "...", "auth_token": "..."}
{"type": "disconnect"}
```

The `entity` type enables the UI to render structured data as interactive tables/forms instead of prose. The `context` field on user messages enables implicit entity resolution ("this" = current entity).

### 2.2 Conversation Persistence

**Decision**: Conversation history lives in deepagents' LangGraph checkpointer, keyed by Interaction ID. MongoDB collection as checkpoint store (per-org, scoped).

- **Interaction entity** = conversation metadata (who's handling, channel_type, status, timestamps)
- **Checkpointer** = message history + tool state (what the agent said/did)
- On panel reopen: UI reconnects, harness loads checkpoint for existing Interaction, conversation continues

This matches "persistent conversation per user" and "multi-step operational work works across the sequence without re-grounding."

### 2.3 Auth Detection Per Session

**Decision**: Harness detects auth mode from the WebSocket connect message.

- If `auth_token` starts with `indemn_` → service token → Runtime-level permissions
- If `auth_token` is a JWT → user session → user's permissions (default assistant mode)
- The harness passes the token through to CLI calls, so permission enforcement happens at the kernel API

---

## 3. What Needs to Be Built

### 3.1 Chat Harness (Server — `harnesses/chat-deepagents/`)

| File | What | Lines est. |
|---|---|---|
| `Dockerfile` | FROM harness-base, adds WebSocket + checkpointer deps | ~20 |
| `pyproject.toml` | Dependencies: deepagents, websockets/starlette, langchain-google-vertexai | ~15 |
| `main.py` | FastAPI/Starlette WebSocket server, connection handler, heartbeat | ~80 |
| `session.py` | Per-connection session manager: Interaction + Attention lifecycle, mode switching | ~100 |
| `agent.py` | Agent builder (reuse pattern from async harness) | ~30 |
| `events.py` | `indemn events stream` subprocess consumer, feeds events to agent | ~50 |

Total: ~300 lines of harness code.

### 3.2 Shared Harness Common Additions

| Addition | What |
|---|---|
| `harness_common/interaction.py` | CLI wrappers: create, respond, transfer, close |
| `harness_common/attention.py` | CLI wrappers: open, heartbeat, close |

### 3.3 Assistant Panel (UI — `ui/src/`)

| Component | What |
|---|---|
| `AssistantInput` | Top-bar input, always visible, `/` or Cmd-K focus |
| `ConversationPanel` | Right-side overlay (~400-500px), slides in/out |
| `MessageList` | Renders conversation: user messages, agent responses, tool calls |
| `StreamingMessage` | Token-by-token rendering of agent responses |
| `EntityResult` | Renders entity data as interactive table/form (reuse existing components) |
| `ContextBuilder` | Builds `{view_type, entity_type, entity_id, ...}` from current UI state |
| `useAssistantWebSocket` | Hook: WebSocket connection, reconnection, message parsing |
| `useInteraction` | Hook: subscribe to Interaction entity changes (mode switching) |

### 3.4 Kernel Additions (if not already built)

| Item | Status |
|---|---|
| `indemn events stream` (SSE endpoint) | CLI exists; need to verify API-side SSE/Change Stream endpoint works |
| `indemn interaction create/respond/transfer` | Interaction entity exists; CLI commands may need to be added (same as queue complete/fail pattern) |
| Attention open/close via CLI | @exposed methods exist on Attention; CLI commands may need explicit wrappers |
| Checkpointer MongoDB collection | New — LangGraph checkpoint store scoped by org_id |

---

## 4. What's Already Built

- `harness_common/` (cli.py, runtime.py, backend.py) ✅
- Three-layer LLM config merge ✅
- Runtime entity + register-instance + heartbeat ✅
- Service token auth + user JWT auth in middleware ✅
- Attention entity with heartbeat @exposed ✅
- Interaction entity with handling_actor_id ✅
- `indemn events stream` CLI command ✅
- Watch scope resolution (field_path + active_context) ✅
- Message queue with target_actor_id ✅
- deepagents integration pattern (from async harness) ✅
- Base UI exists (`ui/src/`) ✅

---

## 5. Implementation Order

1. **Interaction + Attention CLI wrappers** (harness_common additions)
2. **Chat harness server** (WebSocket + session lifecycle + agent)
3. **Events stream integration** (subprocess consumer → agent)
4. **Checkpointer setup** (MongoDB LangGraph checkpoint store)
5. **Handoff mode switching** (Change Stream → mode detection → bridge)
6. **Assistant panel UI** (input + panel + streaming + entity render + context)
7. **E2E verification** (open UI → type message → agent responds → entity updated → traces in Grafana)

Items 1-5 are server-side. Item 6 is client-side. Item 7 ties them together.

---

## 6. Verification Criteria

1. **Connection**: UI opens WebSocket → harness accepts → Interaction created → Attention opened
2. **Conversation**: User sends message with context → agent responds → response streams token-by-token
3. **Entity rendering**: Agent returns entity data → UI renders as interactive table
4. **Persistence**: Close panel → reopen → conversation history intact
5. **Context awareness**: "what's blocking this?" while viewing entity → agent resolves "this" correctly
6. **Mid-conversation events**: Entity changes → events stream picks up → agent acknowledges
7. **Handoff**: Transfer to human → harness switches mode → human responds → user sees it
8. **Auth**: Default assistant uses user's JWT → permissions match user's roles
9. **Heartbeat**: Attention stays alive during conversation → expires after disconnect + TTL
10. **Observability**: Full trace in Grafana — WebSocket → agent → CLI calls → entity changes
