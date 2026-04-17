# Notes: 2026-04-14-impl-spec-phase-4-5-consolidated.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-4-5-consolidated.md
**Read:** 2026-04-16 (full file — 2076 lines; read sections 1-200, 683-900 in full; section headers via grep; Phase 5 harness/runtime sections 1480-2076 in full)
**Category:** spec

## Key Claims

- Phase 4 = Base UI (React + Vite + TanStack + Tailwind). Phase 5 = Real-Time (Attention, Runtime, harness pattern, scoped watches, handoff).
- **Explicitly deferred**: Custom per-org dashboards, DashboardConfig/AlertConfig/Widget entities, active alerting, WebAuthn, per-operation MFA re-verification, billing/plans, assistant inline entity rendering, collaborative editing.
- Tech stack: React 18+, Vite, TanStack Query/Table, React Hook Form + Zod, React Router v6, Tailwind, native WebSocket, fetch.
- "No component library. The UI auto-generates from entity schemas."
- UI application structure at `ui/src/` with auth/, layout/, views/, components/, assistant/, hooks/.
- Entity list, detail, queue, role overview, cascade viewer — all auto-generated from entity metadata.
- Real-time updates via WebSocket (server-side handler at `kernel/api/websocket.py`).
- Assistant top-bar input always visible. Slide-in panel from right. ESC closes.
- Phase 4 auth completes: SSO login flow, MFA challenge, platform admin sessions, recovery flows, claims refresh, pre-auth rate limiting, auth audit events, revocation cache with bootstrap, Tier 3 signup.
- Pipeline metrics capabilities: state_distribution, queue_depth (Phase 4 via aggregations.py).
- **Phase 5 harness pattern** — complete voice harness example at `harnesses/voice-deepagents/main.py`.
- `indemn events stream` CLI — subscribes to MongoDB Change Stream on message_queue filtered by target_actor_id + interaction_id.
- Scoped watch resolution (field_path + active_context) in `kernel/watch/scope.py`.
- Runtime deployment: manual for MVP (push image to registry → create Railway service → configure env vars → mark active).

## Architectural Decisions

### Phase 4 Assistant (THIS IS THE SECOND SOURCE OF FINDING 0)

**`kernel/api/assistant.py` is defined at line 836-876**:

```python
# kernel/api/assistant.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from kernel.auth.middleware import get_current_actor

assistant_router = APIRouter(prefix="/api/assistant", tags=["assistant"])

@assistant_router.post("/message")
async def assistant_message(data: dict, actor=Depends(get_current_actor)):
    """Process an assistant message. The default associate runs with
    the user's own session — same permissions, audit as 'user via assistant'. [G-59]"""
    content = data.get("content", "")
    context = data.get("context", {})

    async def generate():
        import anthropic
        client = anthropic.AsyncAnthropic()
        skills = await load_skills_for_roles(actor.role_ids)

        async with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=f"You are the user's assistant in the Indemn OS. "
                   f"You can execute operations using the Indemn API. "
                   f"The user is viewing: {context}.\n\n"
                   f"Available operations:\n{skills}",
            messages=[{"role": "user", "content": content}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    return StreamingResponse(generate(), media_type="text/plain")
```

**This endpoint:**
- Lives in `kernel/api/` (kernel API server process, inside trust boundary)
- Imports `anthropic` directly
- Creates an LLM stream with NO TOOLS (no `tools=[]` parameter)
- System prompt says "You can execute operations" but LLM has no mechanism to do so
- Returns text-only streaming response

**Per design (2026-04-11-base-ui-operational-surface.md)**: the assistant should be a running harness instance (chat-kind Runtime), outside the kernel, using the CLI for all operations via `execute_command`-style tool-use.

**Per design (2026-04-11-authentication-design.md line 463-482)**: "the default assistant inherits the user's session. Its harness authenticates using the user's session JWT (injected at session start)."

**The Phase 4 spec deviates from the design** by placing the assistant inside the kernel API server as a stripped-down streaming endpoint with no tools. This is Finding 2 (no tools) which is a direct consequence of Finding 0 (no harness pattern).

### Phase 5 Harness Pattern (correctly specified, but not implemented as deployable)

**`harnesses/voice-deepagents/main.py` at line 1587-1734** shows a complete harness example:
- Uses LiveKit `Agent` + `AgentSession`
- CLI wrapper (`cli(command)`) that runs `subprocess.run(["indemn"] + command.split())`
- Authenticates via `INDEMN_SERVICE_TOKEN` environment variable
- Creates Interaction, opens Attention, loads skills via CLI
- Uses `deepagents.create_deep_agent(...)` locally inside the harness
- Three-layer config merge: Runtime defaults → Associate override → Deployment override
- Event listener subprocess: `indemn events stream --actor X --interaction Y`
- Heartbeat loop: `cli("attention heartbeat ...")` every 30s
- On session end: closes Attention + transitions Interaction

**Per Phase 5 acceptance criteria (line 2051-2053):**
"HARNESS USES CLI ONLY — All harness-to-kernel communication via CLI subprocess → no direct MongoDB → no Python SDK"

**Per comprehensive audit:** "No harness code exists. The Phase 4-5 spec shows a complete voice harness example, but it's spec, not code." The harness example was included as documentation in the spec but never implemented as a deployable image.

### The Asymmetry

- **Phase 4 assistant**: spec'd as kernel endpoint (in-kernel, no tools, text streaming only). Implemented as specified.
- **Phase 5 voice harness**: spec'd as separate deployable with CLI pattern (outside kernel, full tools via deepagents). NOT implemented.

The Phase 5 spec gets the harness pattern RIGHT (matches the design). The Phase 4 spec gets the assistant pattern WRONG (should be a chat-harness but is a kernel endpoint).

**Why the inconsistency in the specs themselves:**
- Phase 4 (Base UI) needed the assistant to work at the end of Phase 4.
- Phase 5 (Real-Time, harnesses) comes AFTER Phase 4.
- So Phase 4 couldn't use a harness — the harness pattern is defined in Phase 5.
- Phase 4 improvised with a kernel-side endpoint.
- Phase 5's harness example was voice-only — no chat-runtime harness for the assistant was specified.

## Layer/Location Specified

### Phase 4 Locations
- **UI code** in `ui/src/` — React app, runs in browser
- **UI WebSocket handler** in `kernel/api/websocket.py` — kernel-side
- **Entity metadata endpoint** in `kernel/api/meta.py` — kernel-side
- **Assistant endpoint** at `kernel/api/assistant.py` — **kernel-side, should be in chat-harness per design**
- **Auth completion** in `kernel/auth/*` and `kernel/api/auth_routes.py` — kernel-side (correct)
- **Pipeline metrics** in `kernel/capability/aggregations.py` — kernel-side (correct)
- **Tier 3 signup** in `kernel/api/registration.py` — kernel-side (correct)

### Phase 5 Locations
- **Harness code** in `harnesses/voice-deepagents/main.py` — **separate deployable image, outside kernel** (correct per design)
- **TTL cleanup** in `kernel/queue_processor.py` — kernel-side (correct)
- **Zombie detection** in `kernel/queue_processor.py` — kernel-side (correct)
- **Events stream endpoint** in `kernel/api/events.py` — kernel-side (correct)
- **Scoped watch resolution** in `kernel/watch/scope.py` — kernel-side (correct)
- **Handoff endpoint** in `kernel/api/interaction.py` — kernel-side (correct)
- **Voice client integration** — reuses Integration primitive (correct)

### The gap:
- No `harnesses/chat-deepagents/` specified in Phase 5 — only voice harness example.
- No plan to move `kernel/api/assistant.py` → `harnesses/chat-deepagents/` specified.
- Per the design (realtime-architecture-design Part 4), three harness images are expected: `runtime-voice-deepagents`, `runtime-chat-deepagents`, `runtime-async-deepagents`. The Phase 5 spec only shows voice.

## Dependencies Declared

Phase 4:
- React 18+, Vite, TanStack Query, TanStack Table, React Hook Form, Zod, React Router v6, Tailwind CSS
- `anthropic` (imported in `kernel/api/assistant.py` — this shouldn't be in kernel per design)
- MongoDB Change Streams (for WebSocket real-time updates)

Phase 5:
- Harness image deps: `livekit.agents` (voice), `deepagents` (framework), `indemn` CLI
- MongoDB Change Streams (for `indemn events stream`)
- Railway platform (for runtime deployment)

## Code Locations Specified

Phase 4 code:
- `ui/` — full React application
- `kernel/api/meta.py` (extended with full metadata contract)
- `kernel/api/websocket.py` (server-side WebSocket handler)
- `kernel/api/assistant.py` (assistant endpoint — Finding 0 secondary source)
- `kernel/api/auth_routes.py` (additions: SSO, MFA challenge, platform admin)
- `kernel/api/registration.py` (Tier 3 signup)
- `kernel/auth/rate_limit.py` (pre-auth rate limiting)
- `kernel/auth/audit.py` (auth audit events)
- `kernel/auth/jwt.py` (additions: revocation cache with bootstrap)
- `kernel/capability/aggregations.py` (pipeline metrics)

Phase 5 code:
- `harnesses/voice-deepagents/main.py` (complete voice harness example)
- `kernel/queue_processor.py` (additions: cleanup_expired_attentions, handle_zombie_sessions)
- `kernel/api/events.py` (events stream endpoint)
- `kernel/cli/events_commands.py` (CLI command)
- `kernel/watch/scope.py` (complete scoped watch resolution)
- `kernel/api/interaction.py` (handoff endpoints)

## Cross-References

- 2026-04-13-white-paper.md
- 2026-04-14-impl-spec-gaps.md
- 2026-04-11-base-ui-operational-surface.md (rendering contract, assistant design)
- 2026-04-11-authentication-design.md (full auth)
- 2026-04-10-realtime-architecture-design.md (Attention, Runtime, harness pattern, scoped watches, handoff)
- 2026-04-13-documentation-sweep.md (owner_actor_id, content visibility, webhook dispatch)

## Open Questions or Ambiguities

**Pass 2 findings in this spec:**

1. **The `kernel/api/assistant.py` endpoint violates the harness pattern.** It's a kernel-side text-only LLM streaming endpoint. Per design, the assistant should be a running chat-harness instance — an instance of `indemn/runtime-chat-deepagents:1.2.0` that the user's browser connects to via WebSocket, uses CLI via subprocess, runs deepagents locally, and inherits the user's session JWT.

2. **No `harnesses/chat-deepagents/` specified.** Phase 5 includes only the voice harness example. The chat harness — which is what the assistant needs — is missing from the spec entirely.

3. **No `harnesses/async-deepagents/` specified.** Per the realtime-architecture-design, async agent execution should live in `indemn/runtime-async-deepagents:1.2.0`. This harness is also missing from the spec. The async agent execution instead lives in `kernel/temporal/activities.py::process_with_associate` (from Phase 2-3 spec).

4. **The assistant auth flow in the spec matches the design superficially** ("inherits user's session") but the LOCATION is wrong (in kernel endpoint, not in harness).

5. **Phase 5 harness example uses `deepagents.create_deep_agent(...)`** which is the correct framework per the design. But the Phase 2 agent execution uses `anthropic` client directly (no deepagents). Two different agent implementations — the kernel-side one is simpler (no skill loading via deepagents middleware, no todo list, no subagents), the harness one is the full deepagents pattern. These should converge to one implementation, living in the harness.

6. **Phase 5 integration between Runtime entity + harness instance + Temporal task queue is partially specified.** The Runtime entity has a `kind: async_worker` variant per the design, but this spec only shows voice. Async runtimes subscribing to Temporal task queues (per the design's line 460-463) are not explicitly specified in this Phase 5 spec — they're implicit in the Phase 2 Temporal worker spec but that worker is kernel-side.

**Pass 2 conclusion for this spec**: Phase 4 (Base UI + assistant) has a layer deviation — the assistant should be a chat-harness. Phase 5 (Real-Time, voice harness) is clean design-wise but only includes one of three expected harness images, and the other two (chat, async) are missing from the spec entirely.
