---
ask: "How should the blueprint execution architecture work? Storage, entity model, runner mechanics, observability, failure handling, and the two-tier execution question."
created: 2026-03-24
workstream: os-development
session: 2026-03-24-a
sources:
  - type: codebase
    description: "Full read of systems/dispatch/engine.py, systems/hive/ (CLI, records, entity_ops, knowledge_ops, search, sync, config, db, embed), systems/session-manager/cli.py, existing playbooks, skills, registry types, and ontology"
  - type: design
    ref: "projects/os-development/artifacts/2026-03-08-hive-design.md"
    name: "Hive design document"
  - type: design
    ref: "projects/os-development/artifacts/2026-02-19-dispatch-system-design.md"
    name: "Dispatch system design"
  - type: design
    ref: "projects/os-development/artifacts/2026-03-24-blueprint-system-problem-statement.md"
    name: "Blueprint system problem statement"
  - type: session
    ref: "projects/os-development/artifacts/2026-03-24-hive-phase6-brainstorm.md"
    name: "Hive phase 6 brainstorm"
---

# Blueprint Execution Architecture — Research Findings

Raw findings organized by research angle. No proposals — just observations, constraints, tensions, and patterns from the existing codebase and design documents.

---

## 1. How Should Blueprint Definitions Be Stored?

### What Exists Today

The system already has two storage patterns:

**Pattern A: Files as source of truth (knowledge records).** Markdown with YAML frontmatter in `hive/` directories. Git-tracked. MongoDB indexes them (derived) for search. The `sync_core.py` module walks knowledge dirs, parses frontmatter, upserts to MongoDB. The CLI's `create_knowledge()` writes the file AND indexes to MongoDB atomically.

**Pattern B: MongoDB as source of truth (entities).** Entity records like `person`, `company`, `workflow` live exclusively in MongoDB. Schema-validated via YAML type definitions in `hive/.registry/types/`. No file representation. Backed up via MongoDB dumps. Created and queried via `entity_ops.py`.

**Pattern C: Files with no Hive indexing (dispatch specs).** The dispatch system uses beads (a separate task tracker with its own JSON/CLI) for spec storage. The epic and its children are beads, accessed via `bd show`, `bd list`, `bd close`. Target repo is stored in epic notes as `target_repo: /path/to/repo`. Learnings are append-only markdown in `systems/dispatch/active/learnings.md`.

### Observations on Blueprint Storage

- Blueprints have two distinct aspects: the **definition** (static template — what steps, what order, what node types) and the **execution state** (dynamic — which steps have run, what's pending, what failed). These may want different storage strategies.

- Blueprint definitions are prose-heavy (step descriptions, context instructions, acceptance criteria) but also structured (DAG of nodes, typed fields, conditional routing). This is a hybrid that doesn't cleanly fit either existing pattern.

- The problem statement says "simple blueprints should be simple to define and run" and "a single session should be able to read a blueprint and follow it." This implies human-readable format matters — a session needs to literally read the file and understand it.

- Git-tracking blueprint definitions gives version history (important when blueprints evolve). MongoDB-only loses that.

- The ontology's disjoint constraint means if `blueprint` becomes an entity type, it cannot be a knowledge tag. The registry currently has 9 entity types and 18 tags.

- Knowledge directories are organized by tag convention: `notes/`, `decisions/`, `designs/`, `research/`, `sessions/`. Adding `blueprints/` would follow the pattern.

- The dispatch system's spec format (YAML with tasks, acceptance criteria, depends_on, target_repo) is the closest existing analog to a blueprint definition. It was designed for code execution only. The problem statement explicitly says "Dispatch is replaced by the blueprint execution framework."

### Tensions

- **File readability vs. structured execution.** A blueprint that a Claude Code session can "just read and follow" wants to be markdown. A blueprint that an orchestration engine parses wants to be structured YAML/JSON. These pull in opposite directions.

- **Template vs. instance.** A "morning consultation" blueprint is a reusable template. Each Monday's 7am execution is an instance. The dispatch system conflates these (the beads epic IS the instance). The Hive's workflow entity is close to an instance but doesn't reference a template.

- **Where does the DAG live?** The Hive's entity schemas are flat key-value with list/ref fields. A DAG of nodes with edges and conditional routing is richer structure than any existing entity type handles. The `workflow.yaml` type has: name, objective, status, current_context, sessions, project, artifacts, domains, tags. No concept of steps or nodes.

---

## 2. What Entity Types / Knowledge Types Are Needed?

### Current Entity Types (9)

`person`, `company`, `product`, `project`, `workflow`, `meeting`, `brand`, `platform`, `channel`. Plus 5 sync-added types: `linear_issue`, `calendar_event`, `email_thread`, `slack_message`, `github_pr`.

### Current Knowledge Tags (18)

`note`, `decision`, `design`, `research`, `session_summary`, `feedback`, `context_assembly`, `brainstorming`, `architecture`, `ui`, `voice`, `scoring`, `content`, `extraction`, `draft`, `blog`, `newsletter`, `video`, `linkedin`, `hive-improvement`.

### What the Blueprint System Might Need

**A blueprint definition.** Either an entity type (if it needs structured queries as a starting point for context assembly) or a knowledge tag (if it's prose that gets discovered through traversal). The design doc's principle: "entity type when the context assembly agent needs structured queries as a starting point." Blueprints probably need to be found by name and structured fields (trigger type, system, status, schedule).

**An execution record.** Each run of a blueprint. Needs structured fields: start time, end time, status, which steps completed, total cost, trigger (manual, scheduled, event). This is operational data (like session state files) but also knowledge the Hive should retain for context assembly ("what has this blueprint produced recently?").

**Step execution records.** Per-step within an execution: status, duration, token usage, cost, output artifacts, error messages. This is fine-grained observability data. The question is whether each step is a Hive record or whether the execution record aggregates step data internally.

**Artifact linkage.** Steps produce outputs that should become Hive knowledge records (or entity updates). The dispatch engine currently handles this with git commits and beads status updates. The problem statement says "artifacts created during execution are Hive records (self-compressing)."

### Observations on the Entity/Knowledge Split

- The existing `workflow` entity is the closest analog to an execution. It has `objective`, `status`, `current_context`, `sessions`, `artifacts`. But it tracks long-running multi-session work, not a single blueprint run.

- If each blueprint execution creates a workflow entity, and a long feature workflow involves many blueprint runs (design blueprint, then implementation blueprint, then testing blueprint), you get nested workflows or workflow-execution relationships.

- The dispatch system's state is currently in three places: beads (task status), `active/learnings.md` (accumulated knowledge), and git (code). A blueprint execution would consolidate this into Hive records.

- The session manager creates session state files (`sessions/{uuid}.json`) for real-time operational data, then creates a Hive session-summary knowledge record at close. This "ephemeral state file + durable Hive record" pattern is a potential model for execution records.

- The Hive's `records` collection uses a single MongoDB collection with a `type` discriminator. Adding new types (blueprint, execution) follows the established pattern. The `entity_ops.py` already handles schema validation, ref building, and CRUD generically.

### Record Volume Considerations

- A morning consultation blueprint runs 365 times/year. Each run produces 6-10 Hive queries during context assembly plus a context note. That's 365 execution records + 365 context notes per year for one blueprint.

- A parallel fan-out processing 1000 meeting transcripts produces 1000+ step records per execution. At this scale, individual step records in the `records` collection may be excessive.

- The search module (`search.py`) fetches ALL knowledge records with embeddings for semantic search (in-Python cosine similarity). Adding thousands of step execution records would degrade search performance.

---

## 3. How Does the Runner Spawn and Monitor Different Node Types?

### Existing Spawn Mechanisms

**Agent SDK (dispatch engine).** `engine.py` uses `claude_agent_sdk.query()` to spawn Claude Code sessions. Key parameters: `cwd`, `add_dirs`, `setting_sources`, `permission_mode`, `system_prompt` (with appended context), `model`. It processes the async message stream, collecting `TextBlock` content and `ResultMessage` cost data. Error handling catches generic exceptions and returns `(False, error_message)`.

**Session manager (tmux).** `session-manager/cli.py` creates tmux sessions, launches `claude` CLI inside them via `tmux send-keys`. For assembly sessions, it sends the first message (playbook + objective) after a 5-second sleep. It monitors sessions by reading state files written by hooks. Session close sends cleanup commands one at a time, waiting for idle state between each.

**Cron (sync).** `sync_cron.sh` runs individual sync adapters on schedule via crontab. Each adapter failure is isolated. Logging to `.logs/hive-sync.log`.

### Observations on Spawning

- The dispatch engine and session manager represent two fundamentally different spawn patterns. The dispatch engine uses Agent SDK programmatically (async Python, structured output, message streaming). The session manager uses tmux + CLI (imperative, send-keys, hook-based state tracking). The problem statement says the execution primitive is "a tmux terminal (Hive session)."

- The Agent SDK gives structured output (`output_format` with JSON schema), cost tracking (`ResultMessage.total_cost_usd`), and programmatic message processing. But it has issues: the monkey-patched `_tolerant_parse` for unknown message types (`rate_limit_event`), and the verification session had to give up on `output_format` because "rate_limit_event kills the stream before ResultMessage arrives."

- The tmux approach gives a visible terminal (important for the Hive UI Wall tiles), human joinability (can attach and interact), and full Claude Code features (skills, TUI, conversation history). But it's harder to programmatically monitor — the session manager relies on hooks and state file polling.

- For non-Claude-Code nodes (Python scripts, CLI commands), the session manager's tmux pattern works but is overkill. A simple `subprocess.run()` would suffice.

- The nested session problem (`CLAUDECODE` env var) is a recurring theme. Both the dispatch engine (`os.environ.pop("CLAUDECODE", None)`) and the session manager (`env -u CLAUDECODE`) handle it. Any runner needs this workaround.

### Monitoring Patterns

- The dispatch engine monitors by consuming the async message stream and waiting for completion. No intermediate status — it's blocking per task.

- The session manager monitors via hook-written state files (`sessions/{uuid}.json`). Hooks fire on `SessionStart`, `Stop`, `UserPromptSubmit`, `TaskCompleted`, `SessionEnd`. The `update-state.py` hook writes status changes; `update-context.py` tracks context window usage.

- The dispatch engine has no visibility into what the spawned session is doing mid-execution. It gets the full output only after the session completes. The verification session is similarly opaque during execution.

- The session manager's `cmd_close` polls state file for idle status, with a 30-second timeout and fallback to user confirmation. This is brittle — the comment about Claude Code's TUI not reliably submitting when text and Enter are sent together hints at real-world fragility.

### Sub-Blueprint Spawning

- The problem statement says "a blueprint step can be a sub-blueprint." The dispatch engine has no concept of nesting — it's a flat list of tasks with dependencies. Beads has parent-child relationships (used for epic → task), but the engine only processes one level deep.

- Sub-blueprint execution implies the runner recursively invokes itself. The current dispatch engine is a single Python process with a while loop. Recursive invocation would mean either nested process spawning or re-entering the main loop with a sub-spec.

---

## 4. How Does Human-in-the-Loop Work Mechanically?

### Current Interactive Patterns

- The session manager's `cmd_create` with `--assembly` flag sends a first message and sets assembly metadata. The session runs autonomously, writes a context note, and "terminates." But the termination is manual — the playbook says "exit" but the session manager doesn't enforce it.

- The dispatch skill (`SKILL.md`) says "Confirm with the user before launching" — this is an interactive confirmation in the OS session that invokes dispatch, not in the dispatched session itself.

- The session manager has `cmd_send` which sends text to a tmux pane via `tmux send-keys`. This is the mechanical path for injecting human input into a running session.

- The session manager's `cmd_close` is the only mechanism that interacts with a running session programmatically: it sends cleanup commands and waits for idle between each.

### Observations on Human-in-the-Loop

- The problem statement requires "Human-in-the-loop at any step (interactive mode, notification when input needed)." Currently, there's no notification mechanism. The Hive UI Wall tiles are the planned notification surface, but the UI is not yet built.

- The session manager's hook system (globally installed in `~/.claude/settings.json`) fires events but doesn't trigger notifications. Events go to state files, not to any push notification channel.

- "Approval gates" don't exist in any current system. The dispatch engine runs fully autonomously (or fails). The closest analog is the dispatch skill's pre-launch confirmation with the user.

- Mechanically, an approval gate would need to: (1) pause execution, (2) notify the user, (3) wait for input, (4) resume. The session manager's tmux model supports this — a session can sit idle waiting for input. But the runner needs to know the session is waiting vs. still working.

- The brainstorm says "almost everything involves a Claude Code session." If a blueprint step needs human input, the most natural mechanism is opening/highlighting a session tile on the Wall and waiting for the user to interact.

- Voice-first interaction (Wispr Flow) means the user talks into the active session. The notification needs to surface the session tile so the user can switch focus to it.

---

## 5. How Does the Runner Handle Failures, Retries, Timeouts, and Crash Recovery?

### Existing Failure Handling

**Dispatch engine failure patterns:**
- Per-task retry with `MAX_RETRIES_PER_TASK = 3`. Tracks `attempts` dict per task ID.
- On session failure: appends to learnings, resets task status to "open," increments attempt counter.
- On verification failure: same retry loop, but verification has its own `MAX_VERIFY_RETRIES = 3`.
- On verification parse failure ("Could not parse"): retries specifically for parse errors, separate from pass/fail retries.
- Exhausted retries: task is left open, engine moves on to next ready task. Reports at end.
- Blocked tasks (deps not met because upstream failed): reported but not retried.
- No crash recovery — if the process dies, state is partially in beads and partially in memory (`attempts` dict). Restarting the engine would re-read beads status but lose attempt counts.

**Session manager failure patterns:**
- Stale detection: `cmd_list` checks if tmux session exists for active state files. If tmux is gone, marks as `ended_dirty`.
- `cmd_close` timeout: 30-second wait for idle, then interactive prompt to interrupt.
- `cmd_destroy`: force-kills tmux, marks state as `ended_dirty`, preserves worktree.
- No automatic recovery — human must notice stale sessions and clean up.

### Observations on Failure Handling

- The dispatch engine's retry loop injects failure information as context for the next attempt (appended to learnings file). This is effective for iterative debugging but doesn't distinguish between transient failures (rate limits, timeouts) and permanent failures (wrong approach).

- The Agent SDK `query()` raises exceptions that the engine catches generically. Rate limit events specifically caused issues — the monkey-patch in `engine.py` silently drops `rate_limit_event` messages. The comment "rate_limit_event kills the stream before ResultMessage arrives" suggests this is an unresolved reliability issue.

- Crash recovery is completely absent from the dispatch system. The engine is a single Python process that loops. If it crashes mid-execution (power failure, OOM, etc.), the in-progress task is left in `in_progress` status in beads, attempt counts are lost, and learnings may be partially written.

- The session manager's approach of persisting state to JSON files on every event is more crash-resilient. If the process dies, the state files reflect the last known state. But it doesn't have automatic restart — someone needs to recreate the session.

- Blueprint executions spanning hours/days (content pipeline, feature development) have high crash exposure. A 20-session feature workflow needs durable state that survives process crashes.

- The problem statement says "crash recovery (resume from last completed step)." This implies persistent execution state with per-step completion tracking. The dispatch engine's beads-based tracking (open/closed per task) is the right concept but lacks durability for attempt counts and intermediate state.

### Timeout Patterns

- The dispatch engine has no per-task timeout. A Claude Code session runs until it completes, errors, or hits the SDK's built-in limits (max_turns, max_budget_usd are not currently set in the implementation session — only model and permission_mode are configured).

- `subprocess.run` calls in the session manager use explicit timeouts (5s, 10s, 30s for different operations).

- The sync cron has no timeout — each adapter runs until completion.

- Long-running Claude Code sessions (1M token context windows) could theoretically run for hours. Without a timeout mechanism, a stuck session blocks the pipeline.

---

## 6. What Does the Observability Data Model Look Like?

### Existing Observability

**Dispatch engine:** Prints to stdout/stderr during execution. Session cost via `ResultMessage.total_cost_usd`. Final summary written to `systems/dispatch/active/summary.md` with pass/fail counts. No duration tracking. No token usage breakdown.

**Session manager:** State files track `created_at`, `last_activity`, `context_remaining_pct`, and event logs. Hooks update these in real-time. But this is session-level, not task-level.

**Hive sync:** `sync_cron.sh` logs timestamps and adapter stats to `.logs/hive-sync.log`. Stats include fetched/created/updated/errors counts per adapter.

### Problem Statement Requirements

"Infrastructure-level tracing, not self-reported by the executing session."
"Token usage, duration, cost per step and per execution."
"Full execution history with artifacts produced."
"Visible on the Hive Wall as tiles."

### Observations on Tracing

- The Agent SDK's `ResultMessage` provides `total_cost_usd` but only at session completion. There's no mid-session cost reporting. Token usage per turn is not exposed in the current SDK usage.

- For non-SDK nodes (Python scripts, CLI commands), there's no token usage — just duration and exit code.

- "Infrastructure-level tracing" means the runner measures from the outside, not asking the session to self-report. The dispatch engine does this for cost (it reads `ResultMessage`) but not for duration or tokens.

- If each step execution becomes a Hive record, the observability data would live in the same `records` collection as everything else. Semantic search over observability records seems low-value compared to structured queries (show me all failed executions in the last week, show me total cost by blueprint).

- The Hive's MongoDB indexes are optimized for entity lookup, tag filtering, and text search. Observability queries (time-range aggregation, cost summation, failure rate calculation) would benefit from different indexes (compound on `{type: 1, status: 1, created_at: -1}` — which already exists).

- The existing `sync_state` collection tracks per-adapter sync metadata. A similar `execution_state` collection (or documents in the `records` collection) could track per-blueprint execution metadata.

### Cost Tracking Specifics

- The dispatch engine's cost tracking only captures implementation session cost, not verification session cost (the verify session doesn't check `ResultMessage`). Total execution cost is underreported.

- Claude Code subscription billing complicates per-execution cost tracking. The Agent SDK reports `total_cost_usd` per session, but this may not reflect actual billing (subscription has limits, then overage pricing).

- For scheduled autonomous workflows (morning consultation, weekly summary), cost tracking is critical for budgeting. Running 365 morning consultations/year at $X each is a meaningful expense.

---

## 7. Two-Tier Execution: When Is "Claude Reads the File" Sufficient?

### The Spectrum

The problem statement describes a spectrum: "Fully interactive (human drives every step) -> hybrid -> fully autonomous (runs on schedule, no human)."

But there's also a complexity spectrum that's orthogonal: "Simple sequence of steps in one session" -> "DAG with conditional routing, fan-out, mixed harnesses, crash recovery."

### What "Claude Reads the File and Follows It" Looks Like Today

- The playbooks (`code-dev.md`, `content.md`, `morning.md`, `ceo-weekly.md`) are exactly this pattern. They describe steps, the Claude Code session follows them, calling `hive` CLI commands along the way.

- The context assembly session (`context_assembly.sh` reference implementation + session manager's `--assembly` flag) is a session that reads a playbook, executes the steps, writes output, and exits. No orchestration engine — just a Claude Code session following instructions.

- The code-dev skill and brainstorm-hive skill define checkpointing patterns that sessions follow. The session creates Hive records as a byproduct of working. No external orchestrator.

- The dispatch skill's `/dispatch create` flow has the user interactively build a spec, then dispatch it. The interactive spec-building is "Claude reads the skill and follows it." The dispatching is the orchestration engine.

### Where "Claude Reads the File" Breaks Down

1. **Parallel fan-out.** A single Claude Code session cannot spawn parallel sub-sessions natively. It can call `session create` multiple times, but it can't monitor them concurrently. The session manager's `cmd_send` and state file polling are sequential.

2. **Crash recovery.** If a session dies mid-execution of a multi-step blueprint, there's no way to resume from the last completed step. The session's context is gone. A new session would need to re-read the blueprint and figure out where things left off — possible via Hive records if checkpointing was done, but fragile.

3. **Mixed harnesses.** A session can call Python scripts and CLI commands via Bash, but it can't easily spawn an Agent SDK session (nested session problem). The dispatch engine's workaround (`env -u CLAUDECODE`) wouldn't work from within a Claude Code session's Bash tool.

4. **Scheduling.** A Claude Code session can't schedule itself for later execution. Cron can invoke `claude -p` or the Agent SDK, but that's an external process, not the session managing its own schedule.

5. **Token budget management.** A single session executing a long blueprint accumulates context. At 1M tokens, this is less of a concern, but for blueprints with many steps producing large outputs, the context fills. The dispatch engine's "fresh context per task" principle addresses this.

6. **Infrastructure-level tracing.** A session can self-report (create Hive records after each step), but "infrastructure-level tracing, not self-reported" explicitly rejects this. An external observer needs to track what the session is doing.

### Where "Claude Reads the File" Is Sufficient

1. **Interactive daily workflows.** Craig opens a session, the blueprint provides structure. The session follows the pattern. No external orchestration needed — Craig IS the orchestrator.

2. **Simple sequential autonomous workflows.** A morning consultation that gathers context, writes a briefing, and exits. One session, linear steps, no parallelism. `claude -p` with a playbook file injected as system prompt.

3. **Ad-hoc work becoming blueprints.** When the pattern is emerging, it's still human-directed. The session follows a checklist, but the checklist is informal.

4. **Session-internal sub-tasks.** Within a code development session, the code-dev skill guides through phases. Each phase has checkpointing. But it's one session doing one thing.

### The Line

The line appears to be: **does execution span more than one session, and does it need to be autonomous?**

- Single-session, interactive: Claude reads the file.
- Single-session, autonomous: `claude -p` with playbook. Maybe scheduled via cron.
- Multi-session, interactive: Workflow entity tracks state, context assembly rehydrates each session. Claude reads the workflow state and continues.
- Multi-session, autonomous: This is where an orchestration engine is needed. Something must track which steps have completed, spawn the next session, handle failures, and manage the overall lifecycle.

The complicating factor is that these aren't discrete categories. A workflow might start interactive, become autonomous for some steps, need human approval at a gate, then continue autonomously.

---

## 8. How Does Parallel Fan-Out Work?

### Current Parallelism

There is none. The dispatch engine processes tasks sequentially: "Pick the first ready task" → execute → verify → next. Dependencies are respected (blocked tasks wait) but independent tasks could run in parallel and don't.

The session manager can have multiple sessions running simultaneously (different tmux sessions), but these are independently managed. There's no coordination between them.

### Fan-Out Mechanics

A fan-out requires:
1. **Spawning N parallel executions** from a single step.
2. **Monitoring all N** for completion/failure.
3. **Collecting results** from all N.
4. **Handling partial failure** — what happens if 3 of 10 fail?
5. **Enforcing concurrency limits** — can't spawn 1000 simultaneous Claude Code sessions.

### Spawning

- Agent SDK `query()` is async. Multiple queries could be awaited concurrently with `asyncio.gather()` or `asyncio.TaskGroup`. The dispatch engine already uses `asyncio.run()` as its entry point.

- tmux sessions can be created in rapid succession. The session manager creates one at a time, but nothing prevents calling `cmd_create` in a loop.

- For non-Claude nodes (Python scripts, CLI), `asyncio.create_subprocess_exec()` or `concurrent.futures.ProcessPoolExecutor` handle parallelism.

### Monitoring

- Agent SDK: each `query()` call is an independent async generator. You'd need to track multiple generators, which means multiple `async for` loops running concurrently.

- tmux: monitoring is poll-based (read state files). Polling N sessions means N file reads per poll cycle.

- For a fan-out of 1000 items (process all meeting transcripts), creating 1000 Claude Code sessions is impractical. This suggests a different execution model for high-fan-out: a single session processing items in a loop, or batched parallelism (10 at a time).

### Concurrency Limits

- Claude Code subscription has rate limits. The dispatch engine's monkey-patched `rate_limit_event` handling hints at this being a real constraint. Running 10 parallel Agent SDK sessions might hit API rate limits.

- System resources: each tmux session is a terminal process. Each Claude Code instance is a Node.js process (~200-500MB RAM). 10 concurrent sessions = 2-5GB RAM.

- The Hive's local MongoDB and Ollama embedding service are shared resources. Concurrent CLI operations could contend on MongoDB writes.

### Result Collection

- Agent SDK: results come from the async generator (TextBlock content, ResultMessage cost). Collecting from N generators means accumulating results in a shared data structure.

- If results are Hive records (knowledge notes created by each parallel session), collection is "query the Hive for all records created by this execution." The refs system supports this — each record refs the execution.

### Partial Failure

- The dispatch engine's approach: continue with remaining tasks, report failures at the end. This is a "best effort" strategy.

- For fan-out, partial failure options include: fail fast (abort on first failure), fail tolerant (continue, report failures), retry failed items, or require minimum success threshold.

- The problem statement doesn't specify a partial failure strategy for fan-out.

---

## 9. Lessons from the Dispatch System

### What Worked

- **Fresh context per task.** Each task gets its own session with curated context. No context pollution across tasks. This is a sound principle that should carry forward.

- **Verification as a separate session.** Independent judgment. The implementer doesn't grade its own work. The verify prompt template is well-structured.

- **Beads integration for task tracking.** Using an existing CLI tool for task status rather than building custom state management. The dispatch engine reads/writes beads via subprocess calls — clean separation.

- **Learnings as append-only context.** Knowledge accumulates across tasks without polluting any single session's context window. Each task gets the full learnings history injected.

- **CLI-first approach.** The engine is a Python script run via bash. The skill is a SKILL.md that tells a session how to invoke it. Fits the OS philosophy.

### What Didn't Work / Limitations

- **No crash recovery.** Process death loses in-memory state (attempt counts). Beads retains task status but not execution metadata.

- **No parallelism.** Sequential task execution even when tasks are independent. The `get_ready_children` function identifies all ready tasks but only the first is picked.

- **No cost aggregation.** Implementation session cost is printed but not stored. Verification session cost is not captured at all.

- **Fragile SDK interaction.** Monkey-patching `parse_message` to handle unknown message types. Verification session giving up on `output_format` due to stream killing. These are workarounds for SDK immaturity.

- **No timeout mechanism.** Sessions run indefinitely. A stuck implementation session blocks the entire pipeline.

- **No intermediate visibility.** You can't see what the dispatched session is doing. It's a black box until it completes.

- **Target repo is a hack.** Stored in beads epic notes as `target_repo: /path/to/repo` and parsed with string splitting. This is metadata that belongs in structured fields.

- **Single-level task hierarchy.** The engine processes epic → children (one level). No nesting, no sub-epics.

- **No mixed harness support.** Every task is a Claude Code session via Agent SDK. No mechanism for Python scripts, CLI commands, or other execution types.

- **Code-only.** The dispatch system was designed for code development (target repos, git commits, test verification). The blueprint system needs to handle content, research, operations, and any other workflow type.

### Dispatch → Blueprint Migration Path

The dispatch engine is 520 lines of Python. Its core concepts (fresh context per task, verification separation, learnings accumulation, iterative retry) are sound. Its limitations (no parallelism, no crash recovery, no mixed harnesses, code-only) are exactly what the blueprint system needs to solve.

The beads integration would need to be replaced or augmented. Beads is a task tracker for implementation plans within a session. Blueprints are broader — they encode workflow patterns across sessions and harnesses.

---

## 10. Existing Infrastructure Constraints and Affordances

### MongoDB (Local)

- Single `records` collection with type discriminator. Adding new types is a configuration change (YAML in `.registry/types/`).
- Indexes: `record_id` (unique), `type`, `tags`, `domains`, `status`, `refs_out.*`, `wiki_links`, `content_embedding`, `created_at`, `updated_at`, full-text on `title` + `content`, compound indexes.
- Separate `sync_state` collection for adapter metadata. Potential model for execution metadata.
- Local instance (no Atlas). Fast, private, free. But no replication, no Atlas Search, no change streams.
- At scale of hundreds to low thousands of records, performance is fine. Thousands of step execution records could change the math.

### Ollama Embedding

- Local `nomic-embed-text` model. Semantic search works by fetching ALL knowledge embeddings and computing cosine similarity in Python. O(N) for every search query.
- Adding thousands of execution/step records with embeddings would degrade semantic search. Execution records likely don't need semantic search — structured queries suffice.

### Session Manager

- tmux-based. Sessions are tmux sessions. State tracked via JSON files + hooks.
- Assembly sessions supported (`--assembly` flag). Sends playbook + objective as first message.
- Session close creates Hive session-summary record. Graceful degradation if Hive CLI unavailable.
- `session create`, `session send`, `session close`, `session destroy` — the full lifecycle.

### Agent SDK

- Installed: `claude-agent-sdk` v0.1.38.
- Auth: `CLAUDE_CODE_OAUTH_TOKEN` or subscription via `claude -p`.
- Nested session workaround: `env -u CLAUDECODE`.
- Hooks available but not used in dispatch engine (only in session manager).
- Known issues: unknown message types require monkey-patching, `output_format` unreliable with rate limits.

### Hive CLI

- 14+ commands. JSON when piped, text when interactive.
- Unified entity/knowledge routing. Layer-transparent.
- Used by playbooks, skills, session close hooks, sync cron.
- The primary interface for agents executing within sessions.

### Cron

- Already used for sync adapters (5-minute calendar, 10-minute slack, 10-minute linear, 15-minute github).
- `sync_cron.sh` pattern: single adapter per invocation, logging, environment setup.
- Could be extended for blueprint scheduling. But cron is limited — no event triggers, no dependency awareness, no result handling.

### Skills

- Skills are SKILL.md files that Claude Code sessions read and follow.
- Skills can be auto-invoked by Claude or manually invoked by user.
- Skills cannot spawn sub-sessions (no Agent SDK access from within a session).
- Skills can call any CLI tool via Bash (including `hive`, `session`, `bd`).
- The dispatch skill orchestrates by calling the engine.py via `env -u CLAUDECODE python3 ...`. A blueprint skill could follow the same pattern.

---

## 11. Open Tensions and Unresolved Questions

### Definition Format: Declarative vs. Imperative

Playbooks today are imperative markdown ("do step 1, then step 2, then step 3"). The dispatch spec is declarative YAML ("here are the tasks, here are their dependencies, here's the acceptance criteria"). Blueprints could be either or both. The problem statement leans declarative ("executable workflow definition") but also says "a single session should be able to read a blueprint and follow it" which leans imperative.

### Orchestrator Complexity: LangGraph vs. Custom

The problem statement says "LangGraph is the orchestration engine for complex blueprints." LangGraph provides: state machines, conditional routing, parallel branches, persistence (SQLite checkpointing), and streaming. But it's a significant dependency — the OS philosophy says "no magic, no abstraction for abstraction's sake" and "the right amount of complexity is the minimum needed for the current task."

The dispatch engine is 520 lines of custom Python. It handles sequential execution, retry, and verification. Adding parallelism, conditional routing, and crash recovery to custom code is possible but increasingly complex. LangGraph handles these natively but adds a dependency and a conceptual framework that may not fit the CLI-first philosophy.

The web-operator project already uses LangGraph (observed in the `feat-web-operator-improvement` branch analysis: "LangGraph SQLite checkpoints.db"). So there's precedent in the ecosystem.

### State Ownership: Hive vs. Runner

The problem statement says "Blueprint state lives in the Hive, not in sessions." But the Hive is optimized for knowledge (semantic search, graph traversal, context assembly). Execution state is operational data (which step is running, retry counts, partial results). These have different access patterns.

The session manager resolves this by using JSON state files for operational data and Hive records for durable knowledge. A similar split might work for blueprints: runner state in a dedicated store (file, SQLite, or MongoDB collection) and Hive records for the knowledge artifacts.

### Observability Granularity: Per-Step vs. Per-Execution

Recording every step of every execution in the Hive could create noise (thousands of step records for a fan-out). But the problem statement requires "token usage, duration, cost per step." This tension suggests either: (a) step data lives in the execution record as nested data (not individual Hive records), or (b) step records exist but are excluded from semantic search.

### Schedule Mechanism: Cron vs. Event-Driven

Cron handles time-based scheduling. But blueprints might trigger on events (new Linear issue, Slack mention, email arrival). The sync adapters already pull data from these systems on schedule. An event-driven trigger would need a webhook receiver or a poll-and-compare mechanism.

### Self-Compressing vs. Self-Polluting

The brainstorm emphasizes "self-compressing" — as execution proceeds, artifacts are created that feed context assembly. But if every execution creates dozens of records, the graph gets noisy. The monthly maintenance task ("archive stale notes") and the `hive archive` command exist for this, but the volume from automated executions could overwhelm manual curation.

### The "Two Types" Dimension

The brainstorm distinguishes "one-time blueprints" (specific feature build) from "repeatable blueprints" (morning consultation, content pipeline). These have different needs:
- One-time: definition is consumed once, execution state is the permanent record.
- Repeatable: definition is the permanent artifact, execution instances are ephemeral (or archived).

This maps somewhat to the entity/knowledge split but not cleanly. A repeatable blueprint definition feels like an entity (found by name, structured fields, referenced from executions). A one-time blueprint is closer to a knowledge record (prose-heavy, project-specific, eventually archived).
