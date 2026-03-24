---
ask: "Research LangGraph as a workflow orchestration engine for the Hive blueprint system"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-a
sources:
  - type: web
    description: "LangGraph official docs (persistence, interrupts, subgraphs, streaming)"
  - type: web
    description: "Community posts, production experience reports, framework comparisons"
  - type: web
    description: "Grid Dynamics LangGraph-to-Temporal migration case study"
  - type: web
    description: "Anthropic engineering blog on long-running agent harnesses"
  - type: codebase
    description: "indemn-platform-v2 graph_factory — existing LangGraph usage"
  - type: codebase
    description: "systems/dispatch/engine.py — existing Agent SDK dispatch engine"
  - type: codebase
    description: "systems/session-manager/cli.py — existing session/tmux management"
---

# Research: LangGraph as Blueprint Orchestration Engine

Raw findings organized by research angle. No recommendations — just what was found.

---

## Angle 1: What LangGraph Actually Offers

### Core Abstraction: StateGraph

LangGraph is built around `StateGraph` — a state machine where nodes are Python functions and edges define control flow. State is a `TypedDict` that flows through the graph. Each node receives the current state, does work, and returns state updates.

**Version:** LangGraph 1.0 shipped October 22, 2025. No breaking changes from pre-1.0. The core graph primitives (state, nodes, edges) and execution model are unchanged. Commitment to stability until 2.0. The Indemn team currently pins `langgraph>=0.2` in `pyproject.toml`.

**A node is just an async function:**
```python
async def my_node(state: dict) -> dict:
    # Do anything — call APIs, run subprocess, invoke LLMs
    result = await some_work(state["input"])
    return {"output": result}
```

Nodes can call `asyncio.to_thread()` for blocking operations and `asyncio.gather()` for concurrent async tasks within a single node.

### Checkpointing (Persistence)

LangGraph saves graph state as "checkpoints" at super-step boundaries (after each batch of parallel nodes completes). Organized into threads identified by `thread_id`.

**What a checkpoint captures:**
- All state channel values
- Next nodes to execute
- Metadata (source, node writes, step counter)
- Timestamps
- Parent checkpoint reference (for history traversal)
- Pending writes from partially-completed supersteps

**Available backends:**
| Backend | Package | Use Case |
|---------|---------|----------|
| InMemorySaver | langgraph-checkpoint | Dev/testing |
| SqliteSaver / AsyncSqliteSaver | langgraph-checkpoint-sqlite | Local experimentation |
| PostgresSaver / AsyncPostgresSaver | langgraph-checkpoint-postgres | Production |
| CosmosDBSaver / AsyncCosmosDBSaver | langgraph-checkpoint-cosmosdb | Azure production |
| MongoDBSaver / AsyncMongoDBSaver | langgraph-checkpoint-mongodb (v0.3.1, Jan 2026) | MongoDB environments |

**MongoDB checkpoint saver status:** The `langgraph-checkpoint-mongodb` package exists (v0.3.1, maintained by 10gen + LangChain team). However, there is an open issue (#6506) where `AsyncMongoDBSaver` was removed from `langgraph.checkpoint.mongodb.aio` in LangGraph 1.0 due to MongoDB Python driver limitations (INTPYTHON-725, INTPYTHON-690). The async checkpoint saver no longer supports `AsyncMongoClient` instances. The synchronous `MongoDBSaver` still works.

**Fault tolerance:** When a node fails mid-superstep, LangGraph stores pending writes from other nodes that completed successfully. On resume, only failing branches need to retry. Resume happens by re-invoking the graph with the same `thread_id`.

**State serialization:** Default `JsonPlusSerializer` handles LangChain primitives, datetimes, enums via ormsgpack + JSON. Optional pickle fallback for unsupported types (Pandas dataframes, etc.). Optional AES encryption.

### Human-in-the-Loop (Interrupts)

The `interrupt()` function pauses graph execution at a specific point. It accepts any JSON-serializable value which is surfaced to the caller. Resume via `Command(resume=value)`.

**How it works:**
1. `interrupt(payload)` raises a special exception caught by the runtime
2. LangGraph saves state via checkpointer
3. Graph pauses indefinitely
4. Caller invokes graph again with `Command(resume=user_response)` and same `thread_id`
5. The node restarts from the beginning — `interrupt()` returns the resume value

**Critical caveats:**
- The node restarts from the beginning when resumed. Code before `interrupt()` runs again. Side effects before `interrupt()` must be idempotent.
- Multiple interrupts in one node rely on index-based matching. Order matters. Conditionally skipping interrupts causes index mismatches.
- Never wrap `interrupt()` in bare `try/except` — it catches the special exception.
- Only JSON-serializable values can be passed to `interrupt()`.
- Requires a checkpointer and `thread_id` in config. Without persistence, interrupts cannot work.

### Subgraphs (Fractal Composition)

Subgraphs are complete, self-contained graphs embedded as nodes within a parent graph. Each has its own state schema and can have its own checkpointing.

**Two communication patterns:**
1. **Shared state:** Parent and subgraph share state keys. Add compiled subgraph directly as a node. Data flows automatically.
2. **Isolated state:** Different schemas. Wrap subgraph in a node function that transforms state at boundaries.

**Nesting:** Subgraphs can contain subgraphs. Each level transforms state. State isolation is enforced per level.

**Checkpointing with subgraphs:** Parent graph must be compiled with a checkpointer for subgraph persistence to work. Stateful subgraphs inherit the parent's checkpointer. Checkpoint `checkpoint_ns` field identifies parent ("") vs subgraph ("node_name:uuid").

**Limitations:**
- Per-thread parallel calls do not support parallel tool calls when subgraphs share the same thread
- State inspection only works for "statically discoverable" subgraphs (added as nodes or called inside nodes) — not for subgraphs invoked dynamically via tools
- Multiple per-thread subgraphs need unique node names to avoid checkpoint conflicts

### Parallel Execution (Fan-out/Fan-in)

**Static parallelism:** Add multiple edges from a single node to multiple destination nodes. LangGraph auto-detects and runs them concurrently in a "superstep." All nodes in a superstep must complete before the graph proceeds.

**Dynamic parallelism (Send API):** The `Send` API enables runtime-determined parallelism. A routing function returns a list of `Send` objects, each specifying which node to invoke and its state. LangGraph executes all in parallel within a single superstep.

```python
def continue_to_analysis(state):
    return [Send("analyze", {"item": item}) for item in state["items"]]
```

This is the map-reduce pattern — number and configuration of parallel tasks determined at runtime.

**State merging:** When parallel nodes update the same state key, reducers merge updates. The `operator.add` reducer for lists, custom `merge_dicts` for dicts, `add_messages` for LangChain messages. `defer=True` on nodes provides explicit synchronization for asymmetric paths.

**Error handling:** If one parallel node fails, the entire superstep fails atomically. With checkpointing, successful nodes' results are internally saved, so only failing branches retry on resume.

**Rate limiting:** `max_concurrency` config throttles concurrent node execution. Five parallel API calls can exhaust quotas fast.

### Streaming

LangGraph 1.0 streams everything: LLM tokens, tool calls, state updates, node transitions.

**Stream modes:**
- `updates` — node name + state update after each node
- `messages` — individual LLM tokens with metadata
- `custom` — arbitrary events emitted via `get_stream_writer()` within node functions
- Multiple modes can be combined

Custom streaming allows nodes to emit progress events — useful for observability of long-running steps.

### What LangGraph Does NOT Provide

- No built-in scheduling/cron. You must trigger graph execution externally.
- No built-in retry policies per node (only superstep-level fault tolerance via checkpointing).
- No built-in timeout per node. Must wrap with `asyncio.wait_for()`.
- No built-in observability/monitoring (depends on LangSmith or external systems).
- No distributed execution across machines. Single-process Python.
- No built-in CI/CD or deployment pipeline.
- No visual workflow designer.

---

## Angle 2: How LangGraph Would Integrate with Claude Code Sessions

### The Fundamental Architecture Question

The blueprint system's execution primitive is a tmux terminal running a Claude Code session (via Agent SDK or `claude -p`). LangGraph nodes would need to **spawn and manage these external processes**.

### Pattern: LangGraph Node as Session Spawner

A LangGraph node function can do anything Python can do — including spawning subprocesses, calling the Claude Agent SDK, or invoking the session manager CLI. The pattern would be:

```python
async def implementation_step(state: BlueprintState) -> dict:
    # 1. Assemble context from Hive (state carries workflow_id, etc.)
    context = await assemble_context(state["workflow_id"], state["step_objective"])

    # 2. Spawn Claude Code session via Agent SDK
    result = await run_agent_sdk_session(
        prompt=state["step_prompt"],
        context=context,
        target_repo=state["target_repo"],
    )

    # 3. Return artifacts/state updates
    return {"step_output": result, "artifacts": result.artifacts}
```

### What the Existing Dispatch Engine Already Does

The current `systems/dispatch/engine.py` (520 lines) is a Python script that:
1. Reads tasks from beads (CLI tool)
2. Spawns Claude Code sessions via `claude_agent_sdk.query()`
3. Streams responses from sessions
4. Runs separate verification sessions
5. Manages retry logic (3 retries per task)
6. Commits on pass, logs learnings on fail
7. Loops until all tasks pass

This is essentially a hardcoded single-graph workflow: `pick_task -> implement -> verify -> (pass: commit, fail: retry)`. LangGraph would make this composable and configurable.

### Integration Points

**Agent SDK compatibility:** The dispatch engine already uses `claude_agent_sdk.query()` with `async for` streaming. This works inside a LangGraph async node. The `ClaudeAgentOptions` class provides `cwd`, `add_dirs`, `setting_sources`, `permission_mode`, `model`, and `system_prompt` configuration.

**Session manager compatibility:** The session manager CLI (`session create/list/attach/send/close/destroy`) creates tmux sessions with git worktrees. LangGraph nodes could call this CLI for interactive sessions. For autonomous sessions, the Agent SDK is more appropriate (programmatic control, streaming, structured output).

**Hive CLI compatibility:** LangGraph nodes would call `hive` CLI commands for context assembly, record creation, and workflow state updates. The Hive CLI outputs JSON when piped, which LangGraph nodes can parse.

### Challenges

1. **Session duration:** Claude Code sessions via Agent SDK can run for minutes (or longer with 1M context). LangGraph nodes would need to await these long-running async operations. No built-in timeout handling — must wrap with `asyncio.wait_for()`.

2. **Interactive sessions:** For human-in-the-loop steps, LangGraph's `interrupt()` could pause the graph. But the actual interaction happens in a tmux terminal, not through LangGraph's resume mechanism. The graph would need to: interrupt -> spawn interactive session in tmux -> wait for session close signal -> resume with session results.

3. **Session state vs graph state:** Sessions produce artifacts (code, files, Hive records) as side effects. The graph state tracks workflow progress. These must stay in sync. The Hive is the natural synchronization point — both the graph and sessions read/write Hive records.

4. **Nested session issue:** The Agent SDK cannot run inside a Claude Code session due to `CLAUDECODE` env var guard. The dispatch engine handles this with `os.environ.pop("CLAUDECODE", None)`. LangGraph would need the same pattern — the orchestrator process must run outside Claude Code.

5. **Process boundaries:** LangGraph runs in a single Python process. If that process dies, checkpointing allows resume. But all Agent SDK sessions spawned by nodes also die. The graph would resume from the last checkpoint, but completed session work (code commits, Hive records) persists. Idempotency of session side effects becomes critical.

---

## Angle 3: LangGraph's Limitations

### From Production Reports and Community

**Memory consumption:** Multiple reports of excessive RAM usage. One developer reported "2GB of RAM for basic retrieval tasks." The graph state, checkpointing, and LangChain abstraction layers contribute.

**Debugging complexity:** Complex abstraction layers make tracing actual API calls difficult. Errors are hard to locate within intricate chain operations. Production problem diagnosis becomes speculative without proper observability.

**Performance overhead:** LangChain middleware adds latency at scale. One developer achieved 40% performance improvement by switching to direct SDK calls. For the blueprint system, the overhead is likely negligible relative to Claude Code session duration (minutes), but matters for high-throughput fan-out.

**Conditional logic constraints:** Multi-step reasoning with conditional branching encounters framework constraints. The system forces users into predefined patterns rather than enabling fully custom logic flows.

**Version compatibility:** Frequent API changes break existing implementations. Migration documentation criticized as inadequate. Examples become outdated within months. LangGraph 1.0 commitment to stability may mitigate this going forward.

**Ecosystem coupling:** Tight coupling to LangChain. The `langgraph` package depends on `langchain-core`. For the blueprint system, this coupling introduces unnecessary dependencies if LangGraph is used only for orchestration (not for LLM calls — those go through Claude Agent SDK).

**No built-in production-grade capabilities:** Retries, fallbacks, observability, monitoring all require external systems. This is by design (LangGraph stays lightweight), but creates operational overhead.

### Specific to the Blueprint Use Case

**Single-process execution:** LangGraph runs in one Python process. The blueprint system envisions parallel sessions across multiple tmux terminals. The orchestrator process is the bottleneck — if it dies, everything stops. Checkpointing helps, but the gap between "graph resumed" and "sessions resumed" creates complexity.

**No native scheduling:** Blueprints need cron/event-triggered execution (e.g., morning consultation at 7am). LangGraph provides no scheduler. Must pair with `cron`, `apscheduler`, or Claude Code's native scheduling.

**Interrupt model mismatch for interactive sessions:** LangGraph's interrupt model is designed for: pause graph -> caller resumes with value. The blueprint interactive model is: pause graph -> spawn tmux session -> human works interactively -> session produces artifacts -> graph resumes using artifacts. The interrupt model can be adapted but it's not a natural fit.

**State size concerns:** As workflows grow (20+ session feature development), the checkpointed state accumulates. LangGraph stores the full state at each superstep boundary. With MongoDB checkpointing, this means growing document sizes. Need to design state to be references (Hive record IDs) not content.

**No distributed execution:** Fan-out of 10 Claude Code sessions means 10 concurrent async tasks in one Python process. The Agent SDK streams responses, so each session is an open async connection. This is feasible but has resource limits. For truly large-scale parallel work (process 1000 meeting transcripts), a distributed approach is needed.

---

## Angle 4: Alternatives Assessment

### Temporal

**What it is:** General-purpose durable execution platform. Workflows are code (Python, Go, TypeScript, Java). Activities are discrete tasks. Workers poll task queues. Event sourcing provides persistence.

**Grid Dynamics migration case study (LangGraph to Temporal):** Their initial LangGraph + Redis architecture was "incredibly brittle in practice." Problems included: cache conflicts wiping state, "thousands of lines of custom retry and error handling code," race conditions, stale state, stuck agents. With Temporal, state became "an integral part of the workflow itself." Retry logic became declarative `RetryPolicy` on activities. Scaling became operational (adjust Kubernetes replicas).

**Strengths for the blueprint use case:**
- True durable execution — workflows survive process crashes, server restarts
- Built-in retry policies per activity (not just superstep-level)
- Long-running workflows natively supported (hours, days, weeks)
- Signals/queries for external event injection (interactive session completion)
- Horizontal scaling via stateless workers
- Full execution history for observability
- Used by Uber, Snap, Coinbase in production at scale

**Weaknesses for the blueprint use case:**
- Requires running a Temporal Server (self-hosted or Temporal Cloud). This is infrastructure Craig doesn't currently have. Significant operational overhead for a single-user system.
- Steep learning curve. Deterministic workflow constraints (no random, no direct I/O in workflows, only in activities).
- Overkill for simple 3-step blueprints. The framework assumes distributed systems problems that a single-user OS doesn't have.
- No native LLM/AI agent support — you build it on top. Less community/ecosystem for AI agent patterns than LangGraph.
- Activities must be self-contained with serializable arguments. No shared in-memory state.

### Prefect

**What it is:** Python-native workflow orchestration, originally for data pipelines. DAGs built dynamically as Python code runs. Agent infrastructure spins up containers.

**Strengths:** Python-native, good UI dashboard, scheduling built-in, container-based isolation.
**Weaknesses:** Data pipeline oriented. No human-in-the-loop. No state machine / cyclic graph support. Poor fit for interactive agent workflows. Overkill infrastructure (container orchestration) for a single-user system.

### CrewAI

**What it is:** Role-based multi-agent orchestration with sequential handoffs.

**Strengths:** Simple Python/YAML setup, predictable collaboration, 1200+ integrations.
**Weaknesses:** Sequential flow limits dynamic interaction. Less flexible for parallel behavior. Not designed for spawning external processes or managing tmux sessions. Agent abstraction doesn't match the "session as primitive" model.

### AutoGen (Microsoft Agent Framework)

**What it is:** Multi-agent conversation framework, now unified with Semantic Kernel.

**Strengths:** Deep Azure integration, built-in memory/state/tools.
**Weaknesses:** Azure-centric. Agent-to-agent conversation model doesn't fit the "session spawns, does work, reports back" pattern. Heavy Microsoft ecosystem dependency.

### PydanticAI

**What it is:** Type-safe agent framework focused on structured outputs and validation.

**Strengths:** Type safety, Pydantic validation, multi-provider support, clean API. Reached stable v1 September 2025.
**Weaknesses:** Designed for individual agent definitions, not workflow orchestration. No state machine, no checkpointing, no fan-out. Not a LangGraph alternative — it's complementary. Some suggest combining PydanticAI for agent definitions + LangGraph for orchestration.

### Custom Python (asyncio + state machine)

**What it is:** Build the orchestration layer yourself using Python's asyncio, dataclasses for state, MongoDB for persistence.

**Strengths:**
- Zero framework dependencies
- Total control over execution model
- State model maps directly to Hive entities (no impedance mismatch)
- Can be exactly as simple or complex as needed
- No abstraction layers obscuring behavior
- Already proven: the existing dispatch engine is 520 lines of custom Python
- No version compatibility risks

**Weaknesses:**
- Reinventing: state machine primitives, checkpointing, parallel execution, error recovery
- More code to write and maintain
- No streaming/observability infrastructure out of the box
- Risk of ad-hoc patterns rather than principled design
- Harder for others to understand without framework conventions

### Dagster

**What it is:** Data orchestrator treating data assets as first-class citizens.

**Strengths:** Great for data pipelines, asset versioning, lineage tracking, UI.
**Weaknesses:** Not designed for agent loops, human-in-the-loop, or dynamic workflows. Asset-centric model doesn't match session-based work.

---

## Angle 5: LangGraph Observability and Tracing

### Native Integration with LangSmith

LangGraph has deep integration with LangSmith (LangChain's observability platform). Setting `LANGCHAIN_TRACING_V2=true` enables automatic tracing of all LangGraph executions — LLM calls, tool invocations, node transitions, state updates.

**What LangSmith provides:**
- Nested spans for distributed tracing (each node, each LLM call, each tool invocation)
- Custom dashboards tracking: token usage, latency (P50, P99), error rates, cost breakdowns, feedback scores
- Execution replay and debugging
- As of July 2025: trace-to-server-log connection for LangGraph Platform deployments

### Alternative: Langfuse

Langfuse provides open-source LLM observability with LangChain/LangGraph integration. The Indemn team already has Langfuse configured (see `/langfuse` skill). LangGraph can emit traces to Langfuse via the LangChain callback system.

### The Blueprint Observability Gap

The problem statement requires "infrastructure-level tracing, not self-reported by the executing session." LangGraph's tracing covers the orchestrator level (which node ran, state changes, timing). But the actual work happens inside Claude Code sessions — those traces are invisible to LangGraph.

**What LangGraph can trace:**
- Graph execution flow (node transitions, parallel branches)
- State mutations at each step
- Duration per node
- Custom events emitted via streaming

**What LangGraph cannot trace:**
- Token usage inside Claude Code sessions (Agent SDK reports this at session end, not per-token)
- What the Claude Code session actually did (file edits, CLI commands, decisions)
- LLM calls within Claude Code (those happen in Claude's infrastructure, not LangGraph's)

**Implication:** Full observability requires combining LangGraph-level tracing (orchestration flow) with session-level reporting (what the session produced, cost, duration). The Hive is the natural aggregation point — awareness records from sessions + graph execution traces.

---

## Angle 6: What Indemn Already Has with LangGraph

### indemn-platform-v2: A Full LangGraph Graph Factory

The Indemn team has built a production-grade graph factory system in `indemn-platform-v2` using LangGraph. Key components:

**GraphCompiler** (`graph_factory/compiler.py`):
- Takes a `GraphDefinition` (JSON/Pydantic model) and compiles it to a `CompiledStateGraph`
- Validates graph structure (reachable nodes, valid edges, component existence)
- Supports regular edges and conditional edges (`state_based` routing)
- Dynamic state class creation from schema definitions

**GraphFactory** (`graph_factory/factory.py`):
- Facade coordinating compiler, LLM factory, cache, and repositories
- Hash-based cache invalidation (SHA256 of graph + overrides config)
- LRU graph cache (default 100 entries)
- Agent-specific LLM config with per-node overrides
- Deep merge of agent overrides into template configs
- Two paths: agent has own graph (new) or falls back to template (legacy)

**State Builder** (`graph_factory/state_builder.py`):
- Dynamic `TypedDict` creation from JSON schema
- Supported reducers: `add_messages`, `add` (operator.add), `merge` (dict merge)
- Type mapping: list, dict, string, int, bool, float (with JSON Schema aliases)

**Component System** (`components/`):
- `BaseComponent` abstract class — stateless factories creating node functions
- `ComponentDefinition` dataclass for registry metadata
- Components: `deep_agent`, `router`, `supervisor`, `parameter_collection`, `connector_invocation`
- Component registry with version support
- Connector-to-tool conversion (wrapping connectors as LangChain `StructuredTool`)

**DeepAgentComponent** (`components/deep_agent.py`):
- Wraps LangChain Deep Agents library as a reusable LangGraph node
- Configurable: connector IDs, system prompt, subagents, model (provider + name)
- Multi-provider LLM support (Anthropic, OpenAI)
- User context propagation (org_id, user_id, role) for API auth

**What they use:**
- `langgraph>=0.2` (not yet updated to 1.0)
- `langgraph.graph.StateGraph`, `START`, `END`
- `langgraph.graph.add_messages` reducer
- `langgraph.checkpoint.base.BaseCheckpointSaver` (abstracted)
- `langgraph.checkpoint.mongodb.aio.AsyncMongoDBSaver` (referenced in design docs, may have issues with LangGraph 1.0)
- `langgraph.checkpoint.memory.MemorySaver` (for testing)
- `langgraph.types.Command` (for conditional routing)
- `langgraph.graph.state.CompiledStateGraph`

**What they don't use (yet):**
- `interrupt()` / human-in-the-loop
- Subgraph composition (agents are flat graphs)
- `Send` API / dynamic parallelism
- Streaming modes
- Custom checkpointer backends

### Team Expertise Assessment

The indemn-platform-v2 codebase shows competent LangGraph usage focused on config-driven agent graph compilation. The team understands: state schemas, node composition, conditional routing, checkpointing, and cache management. They have not yet exercised: interrupts, subgraphs, parallel fan-out, or streaming — which are the features most relevant to the blueprint system.

---

## Angle 7: The Anthropic Perspective on Long-Running Agents

Anthropic's engineering blog on "Effective Harnesses for Long-Running Agents" describes a pattern relevant to the blueprint system:

**Two-agent architecture:**
1. **Initializer agent** — runs once to scaffold the environment
2. **Coding agent** — makes incremental progress per session, leaving clean state for the next

**State persistence across context windows:**
- `claude-progress.txt` — structured log of work history
- Git repository — version control for reverting
- Feature list file (JSON) — comprehensive pass/fail status

**Key insight:** "Finding a way for agents to quickly understand the state of work when starting with a fresh context window." This aligns directly with the Hive's self-compressing model — sessions create artifacts that feed future context assembly.

**Anthropic does NOT mention LangGraph, Temporal, or other orchestration frameworks.** Their pattern is: file-based state + git + structured progress tracking + the agent's own reasoning. The orchestration is implicit in the agent's instructions, not externalized in a framework.

---

## Angle 8: Critical Tensions for the Blueprint System

These tensions emerged from the research and don't have obvious resolutions:

### Tension 1: Framework Overhead vs. Reinventing Primitives

LangGraph provides state machines, checkpointing, parallel execution, and interrupts out of the box. But it brings: LangChain dependency, Python-process-bound execution, memory overhead, debugging complexity, and version coupling. Building custom provides total control but means reimplementing those primitives.

The existing dispatch engine is 520 lines of custom Python. It works. It's simple. But it handles only one workflow shape (linear task list with retries). Blueprints need: conditional routing, parallel fan-out, sub-blueprints, human-in-the-loop, and mixed harness types.

### Tension 2: Orchestrator Process Durability

LangGraph's checkpointing lets a graph resume after process death. But the blueprint orchestrator is a Python process on Craig's machine. If it dies, sessions it spawned may still be running in tmux (they're independent processes). On resume, the graph doesn't know what happened in those sessions. The Hive records are the sync point, but the graph state may be stale relative to actual session output.

Temporal solves this with durable execution infrastructure (server + workers + event history). But Temporal requires running a server — infrastructure a single-user OS doesn't justify.

### Tension 3: Interactive vs. Autonomous Execution Models

LangGraph's interrupt model: graph pauses -> caller resumes with a value. Blueprint interactive model: graph pauses -> human works in a live tmux session -> session produces side effects (code, Hive records) -> graph resumes based on those side effects. These are different control flow patterns. The "resume value" in the blueprint model is "what did the session produce," not "what did the user approve."

### Tension 4: Observability Across Boundaries

LangGraph can trace its own execution. Claude Code sessions are opaque processes from LangGraph's perspective. Full blueprint observability requires: graph-level traces (LangGraph) + session-level metrics (Agent SDK cost/duration reports) + artifact-level tracking (Hive records). No single system provides all three.

### Tension 5: Simplicity Requirement

The problem statement demands: "Simple blueprints should be simple to define and run. Complexity only when needed." A 3-step interactive workflow shouldn't require a LangGraph graph definition. But a 20-session feature lifecycle with parallel execution and sub-blueprints needs real orchestration primitives. Supporting both extremes in one system is the hard design problem.

---

## Raw Data: Version and Compatibility Details

| Component | Version | Notes |
|-----------|---------|-------|
| LangGraph (stable) | 1.0.x (Oct 2025) | No breaking changes until 2.0 |
| LangGraph (indemn pinned) | >=0.2 | Not yet updated to 1.0 |
| langgraph-checkpoint-mongodb | 0.3.1 (Jan 2026) | AsyncMongoDBSaver has issues in LangGraph 1.0 |
| Python requirement | >=3.10 | Matches indemn-platform-v2 requirement (>=3.11) |
| Claude Agent SDK | v0.1.38 | Used by dispatch engine |
| LangChain Core dependency | >=0.3 | Required by LangGraph |
| MongoDB checkpoint storage | `records` collection pattern | Could align with Hive `records` collection |

## Raw Data: Feature Matrix for Blueprint Requirements

| Requirement | LangGraph | Temporal | Custom Python |
|-------------|-----------|----------|---------------|
| State machine / nodes+edges | Native | Native (code) | Must build |
| Checkpointing | Native (multi-backend) | Native (event history) | Must build (MongoDB) |
| Parallel fan-out | Native (Send API) | Native (activities) | asyncio.gather() |
| Human-in-the-loop | Native (interrupt) | Native (signals/queries) | Must build |
| Sub-workflows | Native (subgraphs) | Native (child workflows) | Must build |
| Conditional routing | Native (conditional edges) | Native (code) | if/else |
| Streaming/progress | Native (multi-mode) | Limited | Must build |
| Scheduling/cron | Not included | Cron workflows | apscheduler / cron |
| Distributed execution | Not supported | Native | Must build |
| External process spawn | Via async node function | Via activities | subprocess / asyncio |
| Retry per step | Not built-in (superstep only) | Native (RetryPolicy) | Must build |
| Timeout per step | Not built-in (asyncio.wait_for) | Native (activity timeout) | asyncio.wait_for() |
| MongoDB integration | Checkpoint saver exists | Must build | Direct pymongo |
| LLM/AI-native | Yes (LangChain ecosystem) | No (generic) | No |
| Infrastructure needed | Python process | Temporal Server + Workers | Python process |
| Learning curve | Medium (graph model) | High (deterministic constraints) | Low (it's your code) |
| Existing team expertise | Yes (indemn-platform-v2) | No | Yes (dispatch engine) |
