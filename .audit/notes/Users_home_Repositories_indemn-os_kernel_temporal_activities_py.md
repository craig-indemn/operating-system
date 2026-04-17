# Notes: /Users/home/Repositories/indemn-os/kernel/temporal/activities.py

**File:** /Users/home/Repositories/indemn-os/kernel/temporal/activities.py
**Read:** 2026-04-16 (full file — 633 lines)
**Category:** code

## Key Claims

- Module docstring: "Temporal activities — the functions workflows call. Activities handle the actual work: claiming messages, loading context, processing via associate skills, completing/failing messages, and bulk operations."
- Defines Temporal activities decorated with `@activity.defn`:
  - `claim_message` (lines 60-64)
  - `load_entity_context` (lines 67-82)
  - **`process_with_associate`** (lines 85-126) — THE AGENT EXECUTION ACTIVITY
  - `process_human_decision` (lines 129-162)
  - `complete_message` (lines 165-169)
  - `fail_message` (lines 172-176)
  - `process_bulk_batch` (lines 182-286)
  - `preview_bulk_operation` (lines 289-309)
- Helper functions:
  - `_load_skills` — loads skills from MongoDB + verifies content hash
  - **`_execute_deterministic`** (lines 328-367) — parses markdown skill, runs CLI commands via HTTP
  - **`_execute_reasoning`** (lines 370-487) — LLM tool-use loop with Anthropic API
  - `_execute_hybrid` (lines 490-500) — tries deterministic, falls back to reasoning
  - `_parse_skill_steps`, `_parse_simple_condition` (skill parser)
  - `_execute_command_via_api` — translates CLI commands to API POSTs via httpx
- Imports `anthropic` INSIDE `_execute_reasoning` (line 376 `import anthropic`).

## Architectural Decisions

**This file implements the agent execution loop as a kernel Temporal activity.** Exactly matches the Phase 2-3 consolidated spec.

- `process_with_associate` is a `@activity.defn`. It runs in the Temporal worker process. The Temporal worker is the `indemn-temporal-worker` Railway service — a kernel process.
- Loads associate via `Actor.get(ObjectId(associate_id))` — direct MongoDB access via Beanie.
- Sets contextvars: `current_org_id`, `current_actor_id`, `current_correlation_id`, `current_depth`.
- Loads skills via `_load_skills` — direct MongoDB query via Beanie: `await Skill.find_one({"name": name, "status": "active"})`.
- Verifies skill content hash via `verify_content_hash` (kernel/skill/integrity.py).
- Dispatches to one of three execution paths based on `associate.mode`:
  - `deterministic`: `_execute_deterministic`
  - `reasoning`: `_execute_reasoning`
  - `hybrid` (default): `_execute_hybrid`
- `_execute_reasoning` instantiates `anthropic.AsyncAnthropic()` client INSIDE the activity, iterates up to 20 times with tool-use loop, adds `execute_command` tool, calls `client.messages.create(model=model, tools=[{execute_command}], ...)`.
- `_execute_command_via_api` creates an access token via `kernel.auth.jwt.create_access_token` (lines 582) for the associate, makes HTTP POST to `{settings.api_url}/api/{entity_type}s/{entity_id}/{operation}` with Bearer token + correlation/depth headers.
- The agent's tool executions go through the kernel's own API — via HTTP — on the same process or a sibling kernel process. **Everything happens inside the kernel's trust boundary.**
- `process_bulk_batch` is ALSO in this file — handles bulk ops with MongoDB transactions. This is legitimately kernel-side work per the design (bulk is a kernel-provided pattern).

## Layer/Location Specified

**EXACT SOURCE OF FINDING 0.**

- **Agent execution runs inside `kernel/temporal/activities.py`** — a kernel module.
- **The module runs in the kernel Temporal Worker process** — a kernel process (`python -m kernel.temporal.worker`) deployed as the `indemn-temporal-worker` Railway service per docker-compose and Phase 0-1 spec.
- **The Temporal Worker is inside the trust boundary** (direct MongoDB access per Phase 0-1 CLAUDE.md line 382).
- **`anthropic` library is imported inside the kernel** (line 376 of this file).
- **Skill loading via direct MongoDB query** (line 319) — not via CLI.
- **Agent's tool execution goes through kernel's own HTTP API** — the agent posts to `{settings.api_url}/api/...` which is the same kernel's API server.

**Per design (2026-04-10-realtime-architecture-design.md), this should be:**
- Agent execution in a **harness image outside the kernel** — `indemn/runtime-async-deepagents:1.2.0`.
- The harness subscribes to a Temporal task queue named after the Runtime (not the kernel's "indemn-kernel" queue).
- The harness uses `deepagents.create_deep_agent(...)` (not direct `anthropic`).
- The harness calls the kernel's CLI (`indemn` subprocess), which internally calls the kernel's API.
- The harness authenticates via service token (outside trust boundary).
- No direct MongoDB access. No direct `anthropic` import in the kernel.

**What's different between design and code:**

| Concern | Design | Code (this file) |
|---|---|---|
| Where agent loop lives | harness image | kernel/temporal/activities.py |
| Framework | deepagents (with middleware: todo, skills, filesystem, subagent, summarization, HITL) | Direct anthropic.AsyncAnthropic() |
| Skill loading | CLI subprocess: `indemn skill get <name>` | Direct MongoDB: `Skill.find_one({...})` |
| Tool-use interface | deepagents' sandbox with `execute()` running `indemn` CLI as subprocess | Anthropic tool-use with custom `execute_command` tool that POSTs to API |
| Trust boundary | harness is OUTSIDE kernel trust boundary, authenticates with service token | inside kernel trust boundary, direct DB access |
| Sandbox | Daytona wraps agent execution | No sandbox — runs in kernel Temporal worker process |
| Auth | Service token for Runtime; per-actor CLI auth | `create_access_token` inline, JWT for associate itself |

**Secondary observations:**

- The `_execute_reasoning` LLM loop is simpler than deepagents:
  - No todo list middleware
  - No filesystem middleware (no read_file/write_file/glob/grep)
  - No subagents
  - No auto-summarization at 85% context
  - No human-in-the-loop middleware
  - Only one tool: `execute_command`
- Per the Layer 3 associate system design: "An Associate IS Claude Code for Insurance" — with full deepagents middleware. The current implementation is far simpler. Either the design needs to be narrowed or the implementation needs to be upgraded.
- **The 20-iteration limit** is a simple max. Deepagents has better mechanisms (context summarization, todo tracking).

## Dependencies Declared

- `temporalio` — `@activity.defn`, `activity.info()`, `activity.heartbeat()`
- `bson` — ObjectId
- `httpx` — for API calls (CLI-command-via-API)
- `orjson` — serialization
- **`anthropic`** — imported inside `_execute_reasoning` (line 376) — directly in kernel code
- `kernel.*` — multiple internal imports (entity registry, auth jwt, config, context, message schemas, skill integrity, watch evaluator, observability)
- `kernel_entities.actor.Actor` — imported lazily (TYPE_CHECKING + inline imports)
- `kernel_entities.role.Role` — imported lazily in `_get_roles`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/temporal/activities.py`
- Contains: 8 Temporal activities + helper functions
- Runs in: kernel Temporal Worker process (`python -m kernel.temporal.worker`)
- Registered by: `kernel/temporal/worker.py` (per Phase 2-3 spec)
- Called by: `kernel/temporal/workflows.py::ProcessMessageWorkflow`, `::HumanReviewWorkflow`, `::BulkExecuteWorkflow`

## Cross-References

- Phase 2-3 consolidated spec: this file implements §2.4 Activities (lines 315-759 of the spec).
- `kernel/api/assistant.py`: a parallel, simpler agent execution (stripped-down, no tools) in the API server. Finding 2.
- `kernel/temporal/workflows.py`: defines ProcessMessageWorkflow that calls these activities.
- `kernel/temporal/worker.py`: registers these activities.
- `kernel/skill/schema.py`, `kernel/skill/integrity.py`: skill loading + hash verification.
- Design artifact 2026-04-10-realtime-architecture-design.md Part 4: "The harness uses the CLI, not a separate Python SDK" — explicit counter-claim to what this file does.

## Open Questions or Ambiguities

**This file IS the Finding 0 code site for async/scheduled agent execution.** It violates the design explicitly.

- **Why it was written this way**: Per the Phase 2-3 spec, this is exactly what was specified. The spec placed agent execution in kernel Temporal activities. The code implements the spec faithfully. The deviation entered the pipeline at the spec level, not the code level.
- **Migration path**: The `process_with_associate` function and its helpers (`_execute_deterministic`, `_execute_reasoning`, `_execute_hybrid`, `_execute_command_via_api`, `_load_skills`, `_parse_skill_steps`) should move OUT of the kernel and INTO `harnesses/async-deepagents/`. The kernel keeps only `claim_message`, `load_entity_context`, `complete_message`, `fail_message`, `process_human_decision`, `process_bulk_batch`, `preview_bulk_operation` — the deterministic workflow activities that are legitimately kernel-side.
- **Async agent task queue**: Per design, the async-deepagents harness subscribes to a Temporal task queue named after the Runtime. The kernel's queue processor (or API-optimistic-dispatch) writes to that queue; the harness claims. Today, everything runs on the kernel's "indemn-kernel" task queue.
- **Shared `_execute_command_via_api` logic**: In the harness pattern, this would be replaced by `subprocess.run(["indemn", ...])` calling the CLI which already calls the API. The harness doesn't need to know about the API directly.

**Other observations:**

- `_parse_skill_steps` is a simple line-by-line parser (backtick-delimited indemn commands, "If"/"When" conditions). Not a full DSL. This is consistent with the spec ("This is a simple line-by-line interpreter, NOT a full DSL engine").
- `process_bulk_batch` uses `entity_cls.find_scoped(spec.filter_query)` — scoped queries. MongoDB transactions per batch. Looks correct per bulk-operations-pattern design.
- `process_bulk_batch` does raw `update_one` for bulk-update (silent — bypasses `save_tracked`) per the selective emission discipline. Correct.
- Context propagation via headers (`X-Correlation-ID`, `X-Cascade-Depth`) is consistent with the spec.
- No sandbox wrapping agent execution. Per Layer 3 design, agent should run in Daytona. Not implemented — secondary consequence of Finding 0.
