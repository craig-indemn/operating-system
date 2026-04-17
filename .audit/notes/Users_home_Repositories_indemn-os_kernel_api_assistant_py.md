# Notes: /Users/home/Repositories/indemn-os/kernel/api/assistant.py

**File:** /Users/home/Repositories/indemn-os/kernel/api/assistant.py
**Read:** 2026-04-16 (full file — 107 lines)
**Category:** code

## Key Claims

- Module docstring: "Assistant API — streaming LLM endpoint. [G-59]. The default assistant runs with the user's own session JWT. Every action is audited as 'actor {user.id} via default_associate'."
- Defines `/api/assistant/message` POST endpoint that streams text responses.
- Uses `anthropic.AsyncAnthropic()` client, `client.messages.stream(...)` with `model="claude-sonnet-4-6"`.
- **NO tools parameter passed to `client.messages.stream`**.
- System prompt says "You can execute any CLI command the user has permission for" but the LLM has no mechanism to do so.
- Helper `_load_skills_for_roles` builds a skill-list string from entity registry + role permissions, injected into the system prompt.

## Architectural Decisions

- This is an HTTP endpoint in the kernel API server (`kernel/api/` directory).
- Runs in the kernel API server process (`indemn-api` Railway service).
- Inside trust boundary (has direct MongoDB access via `Role.find`, `Skill.find`, `ENTITY_REGISTRY`).
- Directly imports `anthropic` at line 37.
- Stream response via FastAPI's `StreamingResponse`.
- Auth via `get_current_actor` from `kernel.auth.middleware` — uses the USER's JWT. The assistant inherits the user's session.
- Skill list injected via string concatenation into the LLM system prompt — NOT as structured tools.

**This is a degraded/stripped-down agent execution:**
- No tools (no `tools=[]` param on `client.messages.stream`)
- No iteration loop (just streams one response)
- No `execute_command` mechanism
- No actual integration with the CLI
- Just text streaming

**Compare with `kernel/temporal/activities.py::_execute_reasoning`:**
- `_execute_reasoning` has tools (the `execute_command` tool is defined)
- `_execute_reasoning` has an iteration loop (up to 20 iterations)
- `_execute_reasoning` actually routes tool calls to `_execute_command_via_api`
- But `_execute_reasoning` runs in the Temporal Worker for associate-triggered work, NOT for user-facing assistant interactions

**Two parallel code paths:**
1. Associate-processing path (`kernel/temporal/activities.py::process_with_associate` → `_execute_reasoning`): has tools
2. User assistant path (`kernel/api/assistant.py::assistant_message`): no tools

## Layer/Location Specified

**Wrong layer per design.**

- **This code**: `kernel/api/assistant.py` — runs inside kernel API server process, with direct DB access.
- **Per design (2026-04-11-base-ui-operational-surface.md line 167, 306)**: "the conversation panel is a running harness instance — a real-time actor." "The conversation panel is just another real-time channel with a running actor, reusing the mechanism from the realtime-architecture design session. The assistant panel is a running instance of a chat-kind Runtime (or integrated into an existing runtime)."
- **Per design (2026-04-11-authentication-design.md line 463-482)**: "The default assistant is not an independent entity — it is a projection of the user into a running actor. Its harness authenticates using the user's session JWT (injected at session start). Every action taken by the assistant is audited as 'user X via default associate performed Y.' Permissions exactly match the user's. When the user logs out, the assistant's session dies with it."

**The design calls for:**
- Assistant as a **chat-harness instance** (harness image outside kernel)
- **User's browser connects via WebSocket** to the chat-harness Runtime
- **Chat-harness inherits user session JWT** (injected at session start)
- **Chat-harness uses CLI** via subprocess for all operations
- **Chat-harness runs deepagents** or similar framework locally
- **Agent has tools** that actually call `execute_command` via CLI

**Current implementation:**
- Assistant as a **stripped-down endpoint in kernel API server**
- Browser POSTs to `/api/assistant/message`
- Endpoint inherits user JWT via middleware
- Endpoint uses `anthropic` directly (no CLI, no harness)
- Endpoint runs inside kernel trust boundary
- **No tools at all**

**This is Finding 2 from the comprehensive audit**: "Assistant has no tools (CRITICAL)".

**Finding 2 is a direct consequence of Finding 0:**
- Because the assistant was written as an endpoint (not a harness), it's in a request/response model, not a persistent-session streaming model.
- Because it's a one-shot endpoint, it's harder to implement the tool-use loop cleanly.
- The `_execute_reasoning` pattern exists in `kernel/temporal/activities.py` but wasn't re-used for the assistant endpoint.
- Per the comprehensive audit: "The associate execution system (`_execute_reasoning` in activities.py) has the exact tool-use pattern needed — `execute_command` tool that translates CLI commands to API calls — but the assistant endpoint doesn't use it."

**Fix direction:**
- Move the assistant OUT of `kernel/api/` and INTO `harnesses/chat-deepagents/`.
- Browser connects via WebSocket to the chat-harness runtime (not to kernel API server's `/api/assistant/message`).
- Chat-harness uses deepagents, has full tool access via CLI subprocess.
- Kernel provides the user's JWT, the user's default associate config, and `indemn events stream` for real-time events.

## Dependencies Declared

- `fastapi` — APIRouter, Depends
- `fastapi.responses.StreamingResponse` — for streaming text back to client
- `pydantic.BaseModel` — request body validation
- `kernel.auth.middleware.get_current_actor` — auth
- `kernel.db.ENTITY_REGISTRY` — to enumerate entities for skill list
- `kernel.skill.schema.Skill` — to list skills for the prompt
- `kernel_entities.role.Role` — to load role permissions
- **`anthropic`** — LLM client (imported lazily inside `generate()` at line 37)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/api/assistant.py`
- Endpoint: `POST /api/assistant/message`
- Registered in FastAPI app via `assistant_router` — presumably imported and mounted in `kernel/api/app.py`

## Cross-References

- `kernel/api/app.py` — FastAPI app factory that mounts `assistant_router`
- `kernel/temporal/activities.py::_execute_reasoning` — the tool-use pattern that should be adapted for the assistant but isn't
- Design: 2026-04-11-base-ui-operational-surface.md §4.7 — assistant design
- Design: 2026-04-11-authentication-design.md §"Default Assistant Authentication" — auth model
- Design: 2026-04-10-realtime-architecture-design.md Part 4 — harness pattern
- Comprehensive audit Finding 2: assistant has no tools
- Comprehensive audit Finding 0: agent execution in wrong architectural layer (this file's layer issue is a consequence of the broader harness pattern gap)

## Open Questions or Ambiguities

**Pass 2 findings in this file:**

1. **Wrong architectural layer.** Assistant should be a chat-harness instance, not a kernel API endpoint. This is the second arm of Finding 0 (the first being `kernel/temporal/activities.py::process_with_associate` for async).

2. **No tools.** The `client.messages.stream(...)` call has no `tools=[]` parameter. The LLM cannot execute any commands. This is Finding 2 from the comprehensive audit.

3. **Skill list injected as text, not as structured tools.** Skills are concatenated into the system prompt as a bullet list. A proper implementation would register each skill's operations as tools with explicit schemas — matching the `execute_command` pattern in `_execute_reasoning`.

4. **Duplicated `anthropic` usage.** Two places in the kernel import and use `anthropic`: this file and `kernel/temporal/activities.py`. Per the design, neither should exist in the kernel — LLM usage belongs in harness images.

5. **Migration path:**
   - Short-term fix (keeps Finding 0 unresolved but fixes Finding 2): add `tools=[execute_command]` param here and wire up a command executor mirroring `_execute_command_via_api` from activities.py.
   - Proper fix (resolves Finding 0 and 2): delete this file. Build `harnesses/chat-deepagents/`. User browser connects to chat-harness via WebSocket. Harness runs deepagents with CLI sandbox. JWT injected at session start.

6. **The current implementation says "You can execute any CLI command" in the system prompt** but has no mechanism to do so. This is misleading — the LLM will claim it executed commands when it didn't. Until fixed, this is an active user-facing bug.

**Secondary observations:**

- The skill list enumeration in `_load_skills_for_roles` iterates `ENTITY_REGISTRY` and checks role permissions — this is reasonable permission-aware surfacing but the output format (a text bullet list in the system prompt) isn't useful without tools.
- Streaming response is `media_type="text/plain"` — not Server-Sent Events or JSON Lines. This is a simple implementation but not ideal for surfacing structured tool results or entity renderings (which the design says the assistant should do).
- **Per Phase 4-5 spec line 836-876, the spec explicitly implemented this file as spec'd.** The spec itself was the deviation. The code matches the spec but the spec deviates from the design.
