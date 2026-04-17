# Notes: 2026-04-10-realtime-architecture-design.md

**File:** projects/product-vision/artifacts/2026-04-10-realtime-architecture-design.md
**Read:** 2026-04-16 (full file — 927 lines)
**Category:** design-source

## Key Claims

- Resolves three tangled items: Attention (unified active working context), scoped watches (field_path + active_context resolution), Runtime (deployable host for associate execution), and the **harness pattern** (how agent frameworks bridge to the kernel).
- Two new bootstrap entities introduced: **Attention** and **Runtime**.
- Primitive count stays at six; Attention and Runtime are bootstrap entities, not primitives.
- Scope resolution happens at emit time, writing `target_actor_id` on the message. No runtime scope expression evaluation.
- Watch coalescing: watches with `coalesce` strategy batch events sharing the same correlation_id within a window.
- **One Runtime hosts many Associates** via Associate.runtime_id pointer. Runtime provides execution environment; Associate provides per-session config (skills, LLM, mode, prompt).
- Three-layer customer-facing flexibility: Runtime defaults → Associate override → Deployment override.
- Handoff is a field update: Interaction.handling_actor_id OR Interaction.handling_role_id changes; Runtime notices via Change Stream and switches modes.
- Voice clients for humans are Integrations (reuses the Integration primitive).
- One new infrastructure CLI command required: `indemn events stream` — long-running subscription to MongoDB Change Streams, emits events as JSON lines on stdout.
- Everything else auto-generates from entities.

## Architectural Decisions

- **THE key design decision (Part 4, verbatim)**: "The harness uses the CLI, not a separate Python SDK. This is the key design decision. The CLI is already the universal interface. The harness is 'just another client' of the CLI, calling it via subprocess. No dual interface, no second code path, no framework-specific adapters in the kernel."
- Harnesses are **deployable images**, one per `kind+framework` combo: `indemn/runtime-voice-deepagents`, `indemn/runtime-chat-deepagents`, `indemn/runtime-async-deepagents`.
- Each harness image contains: framework (e.g. deepagents), transport (LiveKit/WebSocket/Twilio/Temporal), harness glue script, `indemn` CLI pre-installed.
- Harness is generic per kind+framework, loads associate config at session start.
- **Transport is NOT a separate kernel concept**. "It's bundled with the Runtime's deployment."
- Watch scoping is **emit-time resolution** (not claim-time filtering). The kernel writes `target_actor_id`; claim queries just filter by it.
- Watch coalescing: applied AFTER scope resolution; only coalesces within a single target actor.
- Heartbeat updates **bypass audit logging** — the kernel has a special path for `indemn attention heartbeat` that updates `last_heartbeat`/`expires_at` without generating a change record. Only open/close/expiration generate changes.
- The Runtime is the persistent bridge during handoff; handler changes, but the Runtime's bridging logic swaps modes.
- Associate carries `owner_actor_id` for delegated credential access (e.g., scheduled sync associates bound to a specific human).

## Layer/Location Specified

**THIS IS THE CRITICAL ARTIFACT FOR FINDING 0.** The harness pattern is defined here with explicit layer placement:

- **Harness = deployable image outside kernel.** Part 4: "A harness is the glue code between a specific framework (deepagents, LangChain, custom) and the OS kernel. It runs as a deployable image (usually Docker), one image per kind+framework combination."
- **Three harness images** (Part 4, line 473-477):
  - `indemn/runtime-voice-deepagents:1.2.0` — voice + deepagents + LiveKit Agents
  - `indemn/runtime-chat-deepagents:1.2.0` — chat + deepagents + WebSocket server
  - `indemn/runtime-async-deepagents:1.2.0` — async + deepagents + Temporal worker
- **The harness contains the agent framework and runs it.** In the voice example (line 493-600), `create_deep_agent(...)` and `livekit_agent.run()` are called INSIDE the harness process. The harness is ~60 lines of glue code that creates the agent, opens Attention, streams events, manages heartbeat.
- **Harness authenticates to OS via CLI.** Each harness instance authenticates using a service token, uses the CLI for all OS interactions, including: `actor get`, `interaction create`, `attention open/heartbeat/close`, `events stream`, `interaction transition`.
- **Async agent execution ALSO lives in a harness.** Line 460-463: "For async runtimes: subscribing to a Temporal task queue named after the Runtime" — i.e., the async-deepagents harness image has its own Temporal worker that subscribes to a task queue named after its Runtime. The kernel dispatches work TO this queue; it does not execute the agent loop itself.
- **Real-time transport** (Part 5): "Each real-time Runtime's harness embeds or integrates with a channel-specific transport framework: Voice: LiveKit Agents, Chat: WebSocket server (Python/Node, your choice), SMS: HTTP handlers for Twilio webhooks, Embedded widget: WebSocket or HTTP long-poll."
- **Transport is bundled with Runtime deployment, NOT a kernel concept.** Line 638.
- **Kernel's role in agent dispatch** = write message with target_actor_id + push via Change Stream (for real-time) OR make work available on Temporal task queue (for async). Kernel does NOT run the agent loop.

**Kernel-side responsibilities (what the kernel DOES do):**
- Store entities (Attention, Runtime, Associate, Interaction)
- Evaluate watches with scope resolution at emit time
- Write messages to message_queue with target_actor_id
- Serve `indemn events stream` subscription via Change Streams
- Generate service tokens for Runtime instances
- Track Runtime instances via `register-instance` / `heartbeat` CLI
- Provide the CLI and the API the harness talks to

**Harness-side responsibilities (what the harness DOES do):**
- Create Interaction entity via CLI
- Open Attention via CLI
- Load Associate config via CLI
- Build the agent (using `create_deep_agent`, or LangChain, or custom framework)
- Run the agent event loop (including LLM calls, tool-use, `execute_command`)
- Stream scoped events from `indemn events stream` into the agent
- Send heartbeat via CLI
- Clean up (close Attention, transition Interaction) on disconnect

## Dependencies Declared

- MongoDB (for Change Streams, source of truth for entities and message_queue)
- Temporal (for async runtime task queues — BUT the worker is IN the harness image, not the kernel)
- LiveKit Agents SDK (voice transport — in voice harness image)
- WebSocket library (chat harness)
- Twilio (SMS harness)
- Daytona (sandbox for deepagents; in example voice harness — NOTE: sandbox wraps agent execution, which is in harness)
- deepagents framework (in harness images)
- `indemn` CLI (pre-installed in each harness image)

## Code Locations Specified

- **`indemn/runtime-voice-deepagents:1.2.0`** — voice harness image — contains: deepagents, LiveKit Agents SDK, voice harness script (~60 lines), `indemn` CLI
- **`indemn/runtime-chat-deepagents:1.2.0`** — chat harness image — contains: deepagents, WebSocket server, chat harness script, `indemn` CLI
- **`indemn/runtime-async-deepagents:1.2.0`** — async harness image — contains: deepagents, Temporal worker, async harness script, `indemn` CLI
- The example voice harness is a complete ~60 line Python script showing the pattern: load associate via CLI → create Interaction via CLI → open Attention via CLI → build deepagents agent in Daytona sandbox → subscribe to events stream → register with LiveKit → run main loop with event pump + heartbeat → clean up on disconnect
- Kernel-side: the one new CLI primitive is `indemn events stream` (implementation backed by MongoDB Change Streams on message_queue filtered by target_actor_id)

## Cross-References

- 2026-04-10-eventguard-retrace.md — surfaced mid-conversation event delivery gap
- 2026-04-10-crm-retrace.md — surfaced actor-context scoping need
- 2026-04-10-post-trace-synthesis.md — categorized the open design items
- 2026-04-10-base-ui-and-auth-design.md — proposed ephemeral entity locks, unified into Attention here
- 2026-04-10-integration-as-primitive.md — Integration owners, adapter pattern, reused for voice clients
- 2026-04-10-bulk-operations-pattern.md — referenced as a Part 10 open item

## Open Questions or Ambiguities

The artifact itself lists deferred items (Part 10):
- Bulk operations pattern (resolved by 2026-04-10-bulk-operations-pattern.md)
- Inbound webhook dispatch documentation (Integration artifact update)
- Pipeline dashboard layer
- Queue health tooling
- Authentication (resolved by 2026-04-11-authentication-design.md)
- Content visibility scoping
- Voice handoff UX specifics
- Runtime auto-deployment (what happens when work comes in for a Runtime with no instances)
- Runtime health-based dispatch (round-robin vs smart load-aware)
- Runtime migration across framework versions

The artifact is UNAMBIGUOUS on the key architectural-layer claim: **agent execution (LLM loop, skill interpreter, tool-use) lives in harness images outside the kernel**. The harness uses the CLI; it is not part of the kernel's trust boundary.

**This is the design statement that the current code violates (per Finding 0).** The kernel currently has the full agent loop inside `kernel/temporal/activities.py::process_with_associate`, running in the kernel's Temporal Worker — exactly what this artifact says should NOT happen.
