---
ask: "Revise the Hive Blueprint System design to address all critical and important findings from 5 parallel reviews"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-d
sources:
  - type: design
    ref: "projects/os-development/artifacts/2026-03-24-blueprint-system-design.md"
    name: "Blueprint system design v1"
  - type: review
    description: "5 parallel code reviews: YAML format, execution engine, observability, architecture, edge cases"
  - type: design
    ref: "projects/os-development/artifacts/2026-03-08-hive-design.md"
    name: "Hive design document"
  - type: session
    description: "Brainstorm session on Phase 6 agentic OS vision"
    ref: "projects/os-development/artifacts/2026-03-24-hive-phase6-brainstorm.md"
---

# The Hive Blueprint System — Design Document (v2)

## Vision

The Blueprint System is the execution engine that turns the Hive from a knowledge store into an agentic operating system. Blueprints are executable workflow definitions: they encode how to accomplish a type of work — the steps, what context each step needs, what each step produces, and where the output goes. They replace dispatch, absorb playbooks, and provide the missing orchestration layer over the OS's existing primitives (sessions, skills, CLI tools, Hive records).

**Core value:** Any workflow Craig does more than once becomes a blueprint. Once encoded, it can be scheduled, run autonomously, observed in real-time, resumed after crashes, and composed with other blueprints. The system generates institutional memory as a byproduct of execution.

---

## 1. Architecture Overview

### The Full Stack

```
Craig (director)
    |
    v
Hive UI (Wall + Focus Area)               <-- Tiles show blueprint executions + notifications
    |                                          Click to observe, interact, drill down
    v
Blueprint Runner (Python, asyncio)         <-- The engine: reads YAML, executes steps
    |                                          Persists state to MongoDB per step
    |--- Scheduler (cron + event triggers)     Launches blueprints on schedule/event
    |--- Notification System (hive notify)     Hive-native alerts for human-in-the-loop
    |
    v
Step Executors (per step type)
    |--- CLIExecutor          subprocess.run() for shell commands
    |--- SessionExecutor      session manager CLI + state file watching
    |--- ScriptExecutor       subprocess.run() for Python/Node scripts
    |--- BlueprintExecutor    recursive Runner invocation for sub-blueprints
    |
    v
Existing OS Primitives
    |--- Session Manager      tmux sessions, worktrees, state files
    |--- Hive CLI             Record CRUD, search, sync
    |--- Skills               Atomic capabilities (/slack, /github, /hive, etc.)
    |--- Git                  Code changes, branch management
    |
    v
Hive Data Layer
    |--- MongoDB: hive.records              Entities + knowledge index
    |--- MongoDB: hive.blueprint_defs       Blueprint definitions (parsed YAML cache)
    |--- MongoDB: hive.blueprint_executions Execution state (operational, no TTL)
    |--- MongoDB: hive.notifications        Notification records
    |--- Filesystem: hive/blueprints/       YAML definition files (git-tracked)
    |--- Filesystem: hive/knowledge dirs    Knowledge records produced by execution
```

### Component Inventory

| Component | What It Is | Where It Lives |
|-----------|-----------|---------------|
| **Blueprint Definitions** | YAML files defining workflows | `hive/blueprints/*.yaml` (git-tracked) |
| **Blueprint Runner** | Python asyncio engine that executes blueprints | `systems/hive/blueprint_runner.py` |
| **Step Executors** | Per-type execution logic (cli, session, script, blueprint) | `systems/hive/executors/` |
| **Scheduler** | Cron-based trigger + file/event watcher | `systems/hive/blueprint_scheduler.py` |
| **Notifier** | `hive notify` CLI + Wall tile rendering + pluggable delivery | `systems/hive/notifier.py` + Hive CLI |
| **Blueprint CLI** | `hive blueprint` subcommands for management | Integrated into `systems/hive/cli.py` |
| **Execution Records** | Per-execution state in MongoDB | `hive.blueprint_executions` collection |
| **Notification Records** | Notification state in MongoDB | `hive.notifications` collection |
| **Definition Cache** | Parsed YAML cached in MongoDB for fast listing | `hive.blueprint_defs` collection |

### Key Design Decisions

1. **No Agent SDK.** Sessions are created via the session manager CLI (`session create`) which launches Claude Code in a tmux terminal. The runner monitors execution by watching session state JSON files. This avoids the SDK's reliability issues (monkey-patched message parsers, rate limit event crashes, output format failures).

2. **Blueprint state lives in a separate MongoDB collection** (`blueprint_executions`), not the Hive `records` collection. A daily blueprint produces ~365 execution documents/year. Mixing these with knowledge records would pollute semantic search and dominate `hive recent` feeds.

3. **YAML files are the source of truth** for blueprint definitions, not MongoDB. They are git-tracked, human-readable, and diff-able. MongoDB caches parsed definitions for fast listing and search.

4. **The runner is a single Python asyncio process** (same process as the scheduler). It can execute multiple blueprints concurrently (each blueprint is an asyncio task). Parallel steps within a blueprint use `asyncio.gather()` with configurable concurrency limits. A global concurrency limit caps total simultaneous sessions across all blueprints.

5. **Playbooks are absorbed as the context-assembly step** of their corresponding blueprints. The morning playbook becomes the `gather-context` step of the `morning-consultation` blueprint. The playbook content is inlined as the step's `prompt` or referenced via `playbook_path`.

6. **Worktrees provide isolation, not advisory locks.** Every session created via `session create` gets its own git worktree. Two blueprints working on the same OS repo get separate worktrees automatically. External repo contention is a known limitation — see the Resource Contention section.

7. **No TTL on execution records.** Execution history is valuable data — trend analysis, debugging, pattern recognition. No auto-deletion. If volume becomes an issue, archive rather than delete.

8. **Notifications are Hive-native.** The runner calls `hive notify` (a new CLI command) which creates a notification record in the `hive.notifications` collection. Delivery is Wall tiles (always) plus optional pluggable channels. Blueprints never reference Slack or any specific channel directly.

9. **Two execution modes: single-session and multi-session.** Single-session mode runs the entire blueprint in one Claude Code session. Multi-session mode orchestrates separate sessions per step. The mode determines how the runner tracks state and what observability looks like.

10. **Context assembly is a dedicated step, not the runner doing it programmatically.** For multi-session blueprints, context assembly is an explicit session step that follows a playbook (the LLM decides what Hive CLI queries to run based on the playbook). For single-session blueprints, context assembly instructions are baked into the session prompt. The runner never calls `hive search`/`hive refs`/`hive recent` itself — this preserves the Hive design's principle that "context assembly is an LLM agent that uses the Hive CLI as its toolkit."

---

## 2. Blueprint Definition Format

### Schema

Blueprint definitions are YAML files in `hive/blueprints/`. Each file defines a single blueprint.

```yaml
# Required fields
name: string                    # Unique identifier (kebab-case)
description: string             # Human-readable purpose
version: integer                # Schema version (always 1 for now)

# Execution mode
mode: single-session | multi-session  # Default: multi-session
  # single-session: all steps become structured instructions in one session prompt.
  #   The runner creates one Claude Code session, sends a combined prompt, and
  #   tracks execution at the session level only (no step-level state transitions).
  # multi-session: each session step gets its own Claude Code session.
  #   The runner tracks per-step state and orchestrates step dependencies.

# Classification
domains: [string]               # Hive domains this blueprint operates in
tags: [string]                  # Free-form tags for categorization
system: string                  # Owning system (hive, content, code-dev, etc.)
                                # This is about ownership/classification, not capability restriction.
                                # A code-dev blueprint can use any system's skills.

# Scheduling and triggers (optional)
schedule:
  cron: string                  # Standard cron expression
  timezone: string              # Default: America/Vancouver
triggers:                       # Event-based triggers (optional, list)
  - type: file_change           # Watch for file changes
    path: string                # Glob pattern to watch
    debounce_seconds: integer   # Trailing-edge debounce: fire N seconds after the last change
  - type: hive_record           # Trigger on Hive record creation/update
    filter:                     # MongoDB-style filter on the record
      type: string
      tags: [string]
    debounce_seconds: integer
  - type: webhook               # HTTP endpoint trigger
    path: string                # URL path suffix: /api/blueprints/trigger/<path>
    secret: string              # Optional validation token
  - type: manual                # Only runs when explicitly invoked

# Inputs and outputs
inputs:                         # Parameters the blueprint accepts
  param_name:
    type: string                # string, number, boolean, list, record_id
    required: boolean
    default: any
    description: string
outputs:                        # What the blueprint produces (declared, not enforced)
  output_name:                  # These are documentation only. The runner does not auto-populate
    type: string                # them. Callers access sub-blueprint outputs via the step's
    description: string         # outputs (e.g., ${steps.implement.outputs.sub_status}).

# Execution configuration
config:
  max_duration_minutes: integer # Kill the execution after this long (default: 480 = 8h)
  max_cost_usd: number          # Advisory budget cap — based on rough duration heuristic,
                                # NOT exact. Logged but not strictly enforced. (default: 50.0)
  max_concurrent_sessions: int  # Max parallel sessions within THIS blueprint (default: 2)
  retry_policy:                 # Default retry for all steps
    max_retries: integer        # Default: 2
    backoff_seconds: integer    # Default: 30
  notification:
    on_complete: boolean        # Notify on completion (default: false)
    on_failure: boolean         # Notify on failure (default: true)
    on_human_needed: boolean    # Notify when human input needed (default: true)

# Steps (multi-session mode: orchestrated; single-session mode: structured instructions)
steps: [Step]                   # Ordered list of steps (see Step Types below)
```

### Single-Session Mode

When `mode: single-session`, the blueprint runs entirely in one Claude Code session. This is for simple workflows where the overhead of multi-session orchestration is unnecessary — the majority of blueprints.

**Semantics:**

- The runner creates one session (using the blueprint-level `model`, `permissions`, `add_dirs`, `worktree` fields — see below).
- The `steps` list is converted to a numbered instruction set in the prompt. Each step's `name` and `prompt` (or `command` for CLI steps) becomes an instruction.
- The session receives one combined prompt: context assembly instructions (if `playbook_path` is set) + the numbered step instructions.
- The runner tracks execution at the **session level only**. The execution record has one synthetic step entry representing the entire session.
- `depends_on`, `condition`, `for_each`, and `on_failure` are **ignored** in single-session mode. Step ordering is sequential as written.
- Output capture: the session writes output to Hive records (the self-compressing pattern). The runner queries for records created during the execution window. `last_message` is not available in single-session mode.
- CLI steps (`type: cli`) in a single-session blueprint become instructions for the session to run those commands itself (e.g., "Run `hive sync` first, then..."). They are NOT run by the runner as subprocesses.
- Interactive steps are not supported in single-session mode. Use multi-session for interactive workflows.

**Single-session-specific fields (top-level, alongside `steps`):**

```yaml
# These fields apply to the single session created in single-session mode.
# In multi-session mode, these fields are ignored (each step defines its own session config).
model: string                   # Claude model (default: opus)
permissions: string             # Permission mode (default: bypassPermissions)
add_dirs: [string]              # Additional directories for the session
worktree: boolean               # Create a git worktree (default: true)
playbook_path: string           # Context assembly playbook — contents prepended to the prompt
timeout_minutes: integer        # Max session duration (default: 60)
```

**Observability in single-session mode:**

- The execution record has `status` (running, completed, failed, timed_out, cancelled) and one step entry.
- The Wall tile shows the blueprint name, status, duration, and cost estimate — but no step progress bar.
- `hive blueprint status` shows session-level information (duration, context remaining, Hive records created).
- Crash recovery re-runs the entire session (no step-level checkpoint to resume from).

### Step Types (Multi-Session Mode)

Every step has these common fields:

```yaml
- id: string                    # Unique within this blueprint (kebab-case)
  name: string                  # Human-readable label
  type: cli | session | script | blueprint  # Step type
  description: string           # What this step does

  # Conditional execution (optional)
  condition: string             # Python expression evaluated against execution context
                                # e.g., "steps.validate.exit_code == 0"
                                # e.g., "inputs.skip_tests != true"

  # Dependencies (optional — for parallel groups, default is sequential)
  depends_on: [string]          # Step IDs that must complete before this step runs

  # Retry override (optional — overrides blueprint-level retry_policy)
  retry:
    max_retries: integer
    backoff_seconds: integer

  # Output capture (optional)
  outputs:
    variable_name: string       # How to extract output (see Output Capture below)

  # Failure handling
  on_failure: stop | continue | skip_dependents  # Default: stop
```

#### Type: `cli`

Runs a shell command via `subprocess.run()`. For simple, deterministic operations (sync, git, file operations, Hive CLI calls).

```yaml
- id: sync-external
  name: "Sync external systems"
  type: cli
  command: "hive sync"
  timeout_seconds: 120          # Kill if exceeds (default: 300)
  working_dir: string           # Optional, default: OS_ROOT
  env:                          # Additional environment variables (optional)
    KEY: value
  outputs:
    exit_code: exit_code        # Always available
    stdout: stdout              # Full stdout capture
    stderr: stderr              # Full stderr capture
```

#### Type: `session`

Creates a Claude Code session via the session manager. This is the primary step type for work requiring LLM reasoning. The runner creates the session, sends the prompt, and monitors the session state file for completion.

```yaml
- id: gather-context
  name: "Gather morning context"
  type: session
  objective: "Gather context using morning consultation playbook"

  # Session configuration
  model: opus                   # Claude model (default: opus)
  permissions: bypassPermissions # Permission mode (default: bypassPermissions)
  add_dirs: [string]            # Additional directories for the session
  worktree: boolean             # Create a git worktree (default: true)

  # Prompt construction
  prompt: string                # Direct prompt text (use | for multiline)
  playbook_path: string         # Path to a playbook .md file
                                # When both playbook_path and prompt are set:
                                # the playbook content is prepended, the prompt is appended.
                                # The session receives: [playbook content]\n\n[prompt]
  context_from: [string]        # Step IDs whose Hive record outputs are injected as context.
                                # The runner queries Hive records created by those steps
                                # and includes them in the prompt.
  system_append: string         # Appended to the system prompt

  # Autonomy
  autonomous: boolean           # true = no human interaction expected (default: true)
  interactive: boolean          # true = human joins this session (default: false)

  # Session lifecycle
  timeout_minutes: integer      # Max session duration (default: 60)
  close_on_complete: boolean    # Auto-close session when done (default: true for autonomous)

  # Output (see Output Capture section for the definitive list)
  outputs:
    context_record: hive_record # Primary: a Hive record created by the session
    session_id: session_id      # The session UUID
```

**Session output capture — definitive list of output types:**

| Output Type | Available On | Description |
|-------------|-------------|-------------|
| `session_id` | session | The session UUID from the state file |
| `session_name` | session | The tmux session name |
| `hive_record` | session | Query for the most recent Hive record created during this step's execution window, matching the blueprint's domains and any `--refs` matching the workflow. Returns the record's content. |
| `hive_records_created` | session | List of record IDs created during the step's execution window |
| `exit_code` | cli, script | Process return code |
| `stdout` | cli, script | Full stdout as string |
| `stderr` | cli, script | Full stderr as string |
| `json_stdout` | script | Parse stdout as JSON. If parsing fails, the step status is `failed` with the parse error. |
| `execution_id` | blueprint | The child execution's ID |
| `status` | blueprint | The child execution's final status |
| `collected` | for_each | Gathers outputs from all iterations into a list |

**`last_message` is deliberately excluded.** Tmux pane buffer capture is unreliable — it mixes ANSI escape codes, tool calls, and assistant output. The primary output mechanism is **Hive records**: session prompts instruct the session to write structured output as a Hive knowledge record, and subsequent steps query for it. This is the self-compressing pattern — the output IS the knowledge record.

**For debugging only**, if raw tmux output is needed, use `tmux capture-pane -t <session_name> -p` manually. This is not an automated output type.

**How session monitoring works (the full state machine):**

The session state file (`sessions/{uuid}.json`) has these statuses, set by hooks:

| Status | Set By | Meaning |
|--------|--------|---------|
| `started` | `session create` | Session created, Claude Code not yet launched |
| `active` | Hook: `SessionStart`, `UserPromptSubmit` | Claude Code is processing |
| `idle` | Hook: `Stop` | Claude Code waiting for input |
| `context_low` | Hook: `update-context.py` | Context window below 10% — functionally equivalent to `idle` |
| `ended` | Hook: `SessionEnd`, `session close` | Session ended cleanly |
| `ended_dirty` | `session close` (error path), `session destroy` | Session ended with issues |

**Three-phase session monitoring:**

1. **Wait for launch.** After `session create`, poll for `active` (Claude Code launched and initialized). Timeout: 60 seconds. If `started` persists beyond timeout, the session failed to launch — mark step as `failed`.

2. **Send prompt.** Once status is `active` or `idle` (Claude is ready), send the prompt via `session send`. For prompts longer than 2KB, write to a temp file and use `session send <name> --prompt-file /tmp/bp-{exec_id}-{step_id}.md`.

3. **Wait for completion.** Poll for the transition from `active` to `idle` or `context_low`. The runner must distinguish the post-send idle from the pre-send idle by checking that `last_activity` timestamp is after the send time. Terminal states (`ended`, `ended_dirty`) during polling indicate the session crashed.

   - **For autonomous steps:** Wait for `idle` or `context_low`. Then close the session with `session close <name> --skip-cleanup` (fast close that skips commit/push/INDEX.md steps).
   - **For interactive steps:** Do NOT poll for completion. Set the step status to `waiting_for_human`. When `timeout_minutes` expires, fire a notification via `hive notify`. Continue waiting up to 24 hours. If the 24-hour deadline expires without the session ending, mark the step as `timed_out` (NOT `completed`).

4. **Stuck-session detection.** During the poll loop, periodically verify the tmux session is alive via `tmux has-session -t <name>`. If the tmux session has disappeared but the state file still shows `active`, mark the step as `failed` with error "Session process disappeared."

**Cost tracking without Agent SDK:** The session state file does not contain token counts or cost. The runner tracks wall-clock duration per session step. Cost estimation is derived from duration + model tier (rough heuristic: Opus ~$0.06/minute of active processing). This is advisory only — `max_cost_usd` in the blueprint config is a soft warning, not a hard enforcement boundary. Exact cost tracking requires post-hoc analysis via the Anthropic usage dashboard.

#### Type: `script`

Runs a Python or Node.js script. For data processing, API calls, transformations — anything that benefits from a real programming environment rather than a shell one-liner.

```yaml
- id: process-data
  name: "Process meeting transcripts"
  type: script
  path: "systems/hive/scripts/process_transcripts.py"  # Relative to OS_ROOT
  args: ["--limit", "100", "--format", "json"]
  interpreter: python3          # python3 | node (default: inferred from extension)
  timeout_seconds: 600
  working_dir: string           # Optional
  env:
    BATCH_SIZE: "50"
  outputs:
    exit_code: exit_code
    stdout: stdout
    result: json_stdout         # Parse stdout as JSON
```

#### Type: `blueprint`

Invokes another blueprint as a sub-execution. This is the fractal mechanism. The sub-blueprint runs as a child execution with its own execution record, linked to the parent.

```yaml
- id: implement-feature
  name: "Run implementation blueprint"
  type: blueprint
  blueprint: feature-implementation   # Name of the blueprint to invoke
  inputs:                             # Pass inputs to the sub-blueprint
    repo_path: "${inputs.repo_path}"
    feature_spec: "${steps.design.outputs.spec_record}"
  timeout_minutes: 240
  outputs:
    sub_execution_id: execution_id    # The child execution's ID
    sub_status: status                # completed | failed | timed_out
```

**Sub-blueprint mechanics:**
- The runner creates a new execution record with `parent_execution_id` set
- The sub-blueprint runs within the same runner process (recursive call, not a subprocess)
- The parent step's status reflects the sub-blueprint's final status
- Sub-blueprints can nest to any depth (with a practical limit of 5 to prevent runaways)
- On crash recovery, child executions are recovered first, then parents resume

### Parallel Step Groups

Steps with explicit `depends_on` fields execute in dependency order. Steps that share the same set of dependencies (or have no dependencies beyond the same predecessor) can execute in parallel.

The simplest pattern: use `depends_on` to create a fan-out/fan-in structure.

```yaml
steps:
  - id: prepare
    type: cli
    command: "hive sync"

  # These three run in parallel after 'prepare' completes
  - id: analyze-slack
    type: session
    depends_on: [prepare]
    autonomous: true
    prompt: |
      Analyze Slack channels for signals.
      Write your findings as a Hive note:
      hive create note "Slack analysis ${execution.started_at}" \
        --tags research,signals --domains indemn

  - id: analyze-email
    type: session
    depends_on: [prepare]
    autonomous: true
    prompt: |
      Analyze email threads for action items.
      Write your findings as a Hive note:
      hive create note "Email analysis ${execution.started_at}" \
        --tags research,signals --domains indemn

  - id: analyze-linear
    type: session
    depends_on: [prepare]
    autonomous: true
    prompt: |
      Analyze Linear issues for status.
      Write your findings as a Hive note:
      hive create note "Linear analysis ${execution.started_at}" \
        --tags research,signals --domains indemn

  # This step waits for all three to complete (fan-in)
  - id: consolidate
    type: session
    depends_on: [analyze-slack, analyze-email, analyze-linear]
    context_from: [analyze-slack, analyze-email, analyze-linear]
    autonomous: true
    prompt: |
      Consolidate analysis from all three sources.
      The Hive records created by the parallel steps are included above.
      Write a consolidated summary as a Hive note.
```

The runner resolves the dependency DAG at execution time. Steps whose dependencies are all satisfied are eligible to run. Eligible steps are launched concurrently up to `config.max_concurrent_sessions`.

### Loops

Loops are expressed using the `for_each` field on a step. The step executes once per item in the list.

```yaml
- id: review-prs
  name: "Review each open PR"
  type: session
  for_each:
    variable: pr                # Variable name available in prompt as ${item.pr}
    source: "${steps.list-prs.outputs.result}"  # Resolved to JSON array at execution time
    max_concurrency: 3          # How many to run in parallel (default: 1 = sequential)
  autonomous: true
  prompt: |
    Review PR #${item.pr.number} in ${item.pr.repo}.
    Write findings as a Hive note:
    hive create note "PR review: #${item.pr.number}" --tags review,code --domains indemn
  outputs:
    review_results: collected   # Collects Hive record outputs from all iterations into a list
```

Each iteration creates its own step record in the execution (suffixed: `review-prs.0`, `review-prs.1`, etc.). The `collected` output type gathers all iteration outputs into a list.

**`for_each.source` type rules:**

The `source` field accepts three forms:
1. **Variable interpolation** — `"${steps.list-prs.outputs.result}"` — resolved at execution time, must evaluate to a JSON array or a YAML-native list.
2. **YAML native list** — a direct list in the YAML:
   ```yaml
   source:
     - architecture
     - edge-cases
     - implementation-feasibility
   ```
3. **JSON string literal** — `'["a", "b", "c"]'` — parsed as JSON after interpolation.

Resolution order: interpolation first, then if the result is a string, JSON parse. If the result is already a list (YAML native), use directly. If the resolved value is not iterable, the step fails with an error.

### Conditional Routing

Conditions are Python expressions evaluated in a restricted namespace containing:

- `steps.<step_id>.status` — completed, failed, skipped, timed_out, waiting_for_human, crashed
- `steps.<step_id>.exit_code` — for cli/script steps
- `steps.<step_id>.outputs.<name>` — captured outputs
- `inputs.<param_name>` — blueprint inputs
- `env.<VAR_NAME>` — environment variables
- Available builtins: `len`, `str`, `int`, `float`, `bool`, `any`, `all`, `min`, `max`

```yaml
- id: deploy
  name: "Deploy to production"
  type: cli
  condition: "steps.tests.status == 'completed' and steps.tests.exit_code == 0"
  command: "vercel deploy --prod"

- id: notify-failure
  name: "Notify on test failure"
  type: cli
  condition: "steps.tests.status == 'failed' or steps.tests.exit_code != 0"
  command: "hive notify 'Tests failed for ${inputs.feature_name}' --priority high"
```

If a condition evaluates to `false`, the step is marked `skipped`. Steps that `depend_on` a skipped step evaluate their own conditions independently — a skipped dependency does not automatically skip dependents unless the condition explicitly checks for it.

**Security boundary:** Condition expressions are safe because blueprint YAML files are authored locally by Craig, git-tracked, and trusted. If blueprints ever become multi-user editable, switch to a safe expression evaluator.

### Variable Interpolation

Blueprint definitions support variable interpolation using `${...}` syntax:

- `${inputs.param_name}` — blueprint input parameters
- `${steps.step_id.outputs.output_name}` — output from a previous step
- `${execution.id}` — current execution ID
- `${execution.started_at}` — execution start time
- `${item.variable_name}` — current item in a `for_each` loop
- `${env.VAR_NAME}` — environment variable

**Resolution rules:**

| Scenario | Behavior |
|----------|----------|
| Variable exists and has a value | Substituted |
| Variable exists but value is `null` | Substituted with empty string `""` |
| Variable does not exist (e.g., `${steps.nonexistent.outputs.foo}`) | **Step fails** with error "Unresolved variable: steps.nonexistent.outputs.foo" |
| Escaping: literal `${` in a prompt | Use `$${` which renders as literal `${`. E.g., `$${PATH}` becomes `${PATH}` in the output. |
| Nested interpolation (`${steps.${inputs.name}.outputs.x}`) | **Not supported.** The interpolation engine does a single pass. Use a CLI step to resolve dynamic references. |
| Interpolation in non-string fields (e.g., `timeout_minutes: ${inputs.timeout}`) | **Not supported.** Interpolation only applies to string-typed fields (prompt, command, args, paths). Numeric/boolean config fields must be literal values. |

Interpolation happens at step execution time, not at blueprint parse time. This means a step's command can reference outputs from steps that haven't run yet at parse time — they resolve when the step actually executes.

### Schedule and Trigger Definitions

```yaml
# Cron schedule — uses standard 5-field cron syntax
schedule:
  cron: "0 7 * * 1-5"          # 7am weekdays
  timezone: "America/Vancouver"

# Event triggers — multiple triggers supported, any one fires the blueprint
triggers:
  - type: file_change
    path: "hive/notes/*.md"     # Glob pattern, watched via filesystem polling
    debounce_seconds: 30        # Trailing-edge: fire 30s after the LAST change.
                                # Changed files are NOT passed as input.

  - type: hive_record
    filter:
      type: knowledge
      tags: { "$in": ["feedback"] }
    debounce_seconds: 60

  - type: webhook
    path: "deploy-complete"     # POST /api/blueprints/trigger/deploy-complete fires this
    secret: "${env.WEBHOOK_SECRET}"  # Optional validation

  - type: manual                # Only fires via `hive blueprint run <name>`
```

**Scheduler implementation:** The scheduler runs in the same Python asyncio process as the runner. It:
1. Loads all blueprint definitions at startup
2. Creates `asyncio` tasks for cron schedules using the `croniter` library
3. Starts a filesystem watcher (using `watchdog`) for file_change triggers
4. Subscribes to a MongoDB change stream on `hive.records` for hive_record triggers
5. Starts a lightweight HTTP server (aiohttp) for webhook triggers
6. On trigger, calls the runner to start the blueprint execution
7. Reloads definitions when `hive/blueprints/*.yaml` files change

**Circular trigger prevention:** Each execution record includes a `trigger_chain` field — a list of `(blueprint_name, trigger_type)` tuples tracing how this execution was triggered. If the chain exceeds `max_trigger_chain_depth: 5` (configurable), the execution is rejected with a warning notification. This prevents A -> B -> A infinite loops.

**Cron vs. Claude Code Desktop Tasks:** The scheduler uses its own cron implementation (not Claude Code desktop tasks) because: (a) desktop tasks require the Claude app to be open, (b) they cannot pass structured parameters, (c) they have a minimum 1-hour interval. The scheduler runs as a `launchd` service that auto-starts on boot and survives app restarts.

---

## 3. Execution Engine

### The Runner — Main Loop

The Blueprint Runner is an async Python application. Its core is a state machine that processes one execution at a time, advancing through steps according to the dependency DAG. A global semaphore limits total concurrent sessions across all blueprints.

```python
# Global concurrency limit across all blueprints
GLOBAL_SESSION_SEMAPHORE = asyncio.Semaphore(
    int(os.environ.get("BLUEPRINT_GLOBAL_MAX_SESSIONS", "4"))
)

async def execute_blueprint(blueprint: BlueprintDef, inputs: dict,
                            parent_execution_id: str = None,
                            trigger_chain: list = None):
    # 0. Snapshot the definition into the execution record
    definition_snapshot = blueprint.to_dict()  # Full YAML content, frozen at start

    # 1. Create execution record in MongoDB
    execution = create_execution_record(
        blueprint, inputs, parent_execution_id,
        definition_snapshot=definition_snapshot,
        trigger_chain=trigger_chain or [],
    )

    # 2. Check execution mode
    if blueprint.mode == "single-session":
        return await execute_single_session(blueprint, execution)

    # 3. Multi-session: build dependency DAG from steps
    dag = build_dag(blueprint.steps)

    # 4. Main loop: find eligible steps and execute them
    while not execution_complete(execution):
        eligible = find_eligible_steps(dag, execution)

        if not eligible:
            if has_running_steps(execution):
                await wait_for_any_step_completion(execution)
                continue
            else:
                # Deadlock or all remaining steps skipped
                break

        # Launch eligible steps (up to per-blueprint concurrency limit)
        tasks = []
        for step_def in eligible[:blueprint.config.max_concurrent_sessions]:
            if evaluate_condition(step_def.condition, execution):
                task = asyncio.create_task(execute_step(step_def, execution))
                tasks.append(task)
            else:
                mark_step_skipped(execution, step_def.id)

        # Wait for at least one task to complete
        if tasks:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for completed_task in done:
                step_result = completed_task.result()
                update_step_record(execution, step_result)
                persist_execution_state(execution)  # MongoDB write

    # 5. Finalize
    execution.status = compute_final_status(execution)
    execution.ended_at = now()
    persist_execution_state(execution)

    # 6. Create Hive knowledge record summarizing the execution
    create_execution_summary_record(execution)

    # 7. Send notifications
    await send_notifications(execution, blueprint.config.notification)

    return execution
```

### Single-Session Execution

```python
async def execute_single_session(blueprint: BlueprintDef, execution):
    """Execute a single-session blueprint: one session, combined prompt."""
    session_name = f"bp-{blueprint.name[:12]}-{execution.id[:8]}"

    # 1. Build the combined prompt from steps
    prompt_parts = []
    if blueprint.playbook_path:
        playbook_content = read_file(blueprint.playbook_path)
        prompt_parts.append(playbook_content)
        prompt_parts.append("")  # separator

    prompt_parts.append("## Instructions\n")
    for i, step in enumerate(blueprint.steps, 1):
        instruction = f"{i}. **{step.name}**"
        if step.type == "cli":
            instruction += f"\n   Run: `{step.command}`"
        if step.prompt:
            instruction += f"\n   {step.prompt}"
        if step.description:
            instruction += f"\n   ({step.description})"
        prompt_parts.append(instruction)

    prompt_parts.append("\nWrite all significant output as Hive records. "
                       "When done, exit with /exit.")

    combined_prompt = interpolate("\n".join(prompt_parts), execution)

    # 2. Create session
    async with GLOBAL_SESSION_SEMAPHORE:
        session_id = await create_and_send_session(
            session_name, combined_prompt, blueprint, execution
        )

        # 3. Wait for completion (session-level only)
        final_state = await wait_for_session_completion(
            session_id, session_name,
            timeout_minutes=blueprint.timeout_minutes or 60,
            autonomous=True,
        )

    # 4. Capture output
    execution.steps = [{
        "id": "_session",
        "name": f"Single-session: {blueprint.name}",
        "type": "session",
        "status": "completed" if final_state else "timed_out",
        "session_id": session_id,
        "session_name": session_name,
        "started_at": execution.started_at,
        "ended_at": now_iso(),
        "duration_s": compute_duration(execution.started_at),
        "hive_records_created": query_records_created_since(execution.started_at),
    }]

    execution.status = "completed" if final_state else "timed_out"
    execution.ended_at = now()
    persist_execution_state(execution)
    create_execution_summary_record(execution)
    await send_notifications(execution, blueprint.config.notification)
    return execution
```

### Step Execution — Per Type

#### CLI Steps

```python
async def execute_cli_step(step_def, execution):
    command = interpolate(step_def.command, execution)
    working_dir = step_def.working_dir or OS_ROOT

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=working_dir,
        env={**os.environ, **(step_def.env or {})},
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=step_def.timeout_seconds or 300,
        )
    except asyncio.TimeoutError:
        process.kill()
        return StepResult(status="timed_out", exit_code=-1)

    return StepResult(
        status="completed" if process.returncode == 0 else "failed",
        exit_code=process.returncode,
        stdout=stdout.decode(),
        stderr=stderr.decode(),
        duration_s=(end - start).total_seconds(),
    )
```

#### Session Steps

This is the most complex executor. It uses the session manager CLI to create tmux sessions and monitors the session state JSON files for completion.

```python
SESSION_CLI = "/Users/home/Repositories/.venv/bin/python3 systems/session-manager/cli.py"
SESSIONS_DIR = "/Users/home/Repositories/operating-system/sessions"

async def execute_session_step(step_def, execution):
    session_name = _make_session_name(execution, step_def)

    # 1. Build the session create command
    cmd_parts = [SESSION_CLI, "create", session_name, "--json",
                 "--model", step_def.model or "opus",
                 "--permissions", step_def.permissions or "bypassPermissions"]

    if not step_def.worktree:
        cmd_parts.append("--no-worktree")
    for d in (step_def.add_dirs or []):
        cmd_parts.extend(["--add-dir", interpolate(d, execution)])

    # 2. Create the session (respecting global concurrency limit)
    async with GLOBAL_SESSION_SEMAPHORE:
        proc = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=_clean_env(),  # Removes CLAUDECODE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            return StepResult(status="failed",
                              error=f"Session create failed: {stderr.decode()}")

        # Parse session_id from JSON output (--json flag)
        create_result = json.loads(stdout.decode())
        session_id = create_result["session_id"]

        # 3. PHASE 1: Wait for Claude Code to launch (status: active)
        state = await _wait_for_session_status(
            session_id, target=["active", "idle"],
            timeout=60, poll_interval=2,
        )
        if state is None:
            return StepResult(status="failed", error="Session never became ready")

        # 4. Build and send the prompt
        prompt = _build_prompt(step_def, execution)
        if len(prompt) > 2048:
            # Write long prompts to a temp file
            prompt_file = f"/tmp/bp-{execution.id[:8]}-{step_def.id}.md"
            with open(prompt_file, "w") as f:
                f.write(prompt)
            send_args = [SESSION_CLI, "send", session_name,
                         "--prompt-file", prompt_file]
        else:
            send_args = [SESSION_CLI, "send", session_name, prompt]

        send_time = time.time()
        send_proc = await asyncio.create_subprocess_exec(
            *send_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await send_proc.communicate()

        # 5. PHASE 2: Wait for prompt to be received (status: active)
        await _wait_for_session_status(
            session_id, target=["active"],
            timeout=30, poll_interval=1,
        )

        # 6. PHASE 3: Monitor for completion
        if step_def.interactive:
            return await _handle_interactive_step(
                session_id, session_name, step_def, execution
            )
        else:
            return await _handle_autonomous_step(
                session_id, session_name, step_def, execution, send_time
            )


async def _handle_autonomous_step(session_id, session_name, step_def,
                                   execution, send_time):
    """Wait for autonomous session to finish processing."""
    timeout = (step_def.timeout_minutes or 60) * 60
    deadline = time.time() + timeout

    while time.time() < deadline:
        # Check tmux session is alive
        if not await _tmux_session_alive(session_name):
            return StepResult(status="failed",
                              error="Session process disappeared")

        state = _read_session_state(session_id)
        if state:
            status = state.get("status")
            last_activity = state.get("last_activity", 0)

            # Session finished if idle/context_low AFTER we sent the prompt
            if status in ("idle", "context_low") and last_activity > send_time:
                # Close the session (fast — skip git cleanup)
                close_proc = await asyncio.create_subprocess_exec(
                    *[SESSION_CLI, "close", session_name, "--skip-cleanup"],
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await close_proc.communicate()

                # Extract output: query Hive records created during this step
                records_created = await _query_records_created(
                    execution, step_def, send_time
                )

                return StepResult(
                    status="completed",
                    session_id=session_id,
                    session_name=session_name,
                    duration_s=time.time() - send_time,
                    hive_records_created=records_created,
                    outputs=_extract_hive_outputs(records_created, step_def),
                )

            if status in ("ended", "ended_dirty"):
                return StepResult(status="completed",
                                  session_id=session_id,
                                  duration_s=time.time() - send_time)

        await asyncio.sleep(3)

    # Timed out
    return StepResult(status="timed_out", session_id=session_id)


async def _handle_interactive_step(session_id, session_name, step_def,
                                    execution):
    """Wait for human to work in and close the interactive session."""
    # Mark step as waiting_for_human
    update_step_status(execution, step_def.id, "waiting_for_human")

    # Notify if configured
    if execution.notification_config.on_human_needed:
        await hive_notify(
            f"Blueprint *{execution.blueprint}* needs you at step *{step_def.name}*. "
            f"Attach: `session attach {session_name}`",
            priority="high",
            execution_id=execution.execution_id,
            step_id=step_def.id,
        )

    # Wait for session to end (human closes it)
    timeout = (step_def.timeout_minutes or 60) * 60
    state = await _wait_for_session_status(
        session_id, target=["ended", "ended_dirty"],
        timeout=timeout, poll_interval=5,
    )

    if state is None:
        # First timeout: notify again, keep waiting up to 24 hours
        await hive_notify(
            f"Blueprint *{execution.blueprint}* still waiting at step *{step_def.name}* "
            f"(timed out after {step_def.timeout_minutes}m). "
            f"Attach: `session attach {session_name}`",
            priority="critical",
            execution_id=execution.execution_id,
            step_id=step_def.id,
        )

        state = await _wait_for_session_status(
            session_id, target=["ended", "ended_dirty"],
            timeout=86400,  # 24 hours
            poll_interval=30,
        )

        if state is None:
            # 24 hours with no response — mark as timed_out, NOT completed
            return StepResult(status="timed_out", session_id=session_id,
                              error="Interactive step timed out after 24h")

    return StepResult(status="completed", session_id=session_id,
                      duration_s=_compute_duration_from_state(state))


def _build_prompt(step_def, execution):
    """Build the full prompt for a session step.

    Order: playbook content (if any) + context_from records + prompt text.
    """
    parts = []

    # 1. Playbook content (prepended)
    if step_def.playbook_path:
        playbook = read_file(interpolate(step_def.playbook_path, execution))
        parts.append(playbook)
        parts.append("")  # separator

    # 2. Context from previous steps' Hive records
    if step_def.context_from:
        parts.append("## Context from previous steps\n")
        for step_id in step_def.context_from:
            step_records = execution.steps[step_id].hive_records_created
            for record_id in step_records:
                # Read the Hive record content
                content = subprocess_run(f"hive get {record_id} --format md")
                parts.append(f"### From step: {step_id}\n{content}\n")

    # 3. Prompt text (appended)
    if step_def.prompt:
        parts.append(interpolate(step_def.prompt, execution))

    return "\n".join(parts)


def _make_session_name(execution, step_def):
    """Generate a short session name for blueprint sessions.

    Format: bp-{blueprint_short}-{step_short}-{exec_8}
    Keeps names under 40 characters for tmux/git branch friendliness.
    """
    bp_short = execution.blueprint[:12]
    step_short = step_def.id[:10]
    exec_short = execution.id[:8]
    return f"bp-{bp_short}-{step_short}-{exec_short}"


async def _tmux_session_alive(session_name):
    """Check if the tmux session still exists."""
    tmux_name = f"os-{session_name}"
    proc = await asyncio.create_subprocess_exec(
        "tmux", "has-session", "-t", tmux_name,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.communicate()
    return proc.returncode == 0


async def _wait_for_session_status(session_id, target, timeout,
                                    poll_interval=3):
    """Poll the session state file until the session reaches a target status."""
    state_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    deadline = time.time() + timeout

    while time.time() < deadline:
        state = read_state_file(state_path)
        if state:
            current_status = state.get("status")
            if current_status in target:
                return state
            # Terminal states always return immediately
            if current_status in ("ended", "ended_dirty"):
                return state
        await asyncio.sleep(poll_interval)

    return None  # Timed out
```

#### Parallel Fan-Out

The runner's main loop naturally handles parallelism through the dependency DAG:

```python
async def find_eligible_steps(dag, execution):
    """Find steps whose dependencies are all satisfied."""
    eligible = []
    for step_id, step_def in dag.items():
        step_state = execution.steps.get(step_id)
        if step_state and step_state.status != "pending":
            continue  # Already running, completed, or skipped

        deps_satisfied = all(
            execution.steps[dep_id].status in ("completed", "skipped")
            for dep_id in step_def.depends_on
        )
        if deps_satisfied:
            eligible.append(step_def)

    return eligible
```

`for_each` steps are expanded into individual sub-steps at execution time:

```python
async def expand_for_each(step_def, execution):
    """Expand a for_each step into individual sub-step definitions."""
    source_data = evaluate_expression(step_def.for_each.source, execution)

    # Handle YAML native list (already a list) vs string (needs JSON parse)
    if isinstance(source_data, str):
        source_data = json.loads(source_data)
    if not isinstance(source_data, (list, tuple)):
        raise ValueError(f"for_each source must be iterable, got {type(source_data)}")

    sub_steps = []
    for i, item in enumerate(source_data):
        sub_step = copy.deepcopy(step_def)
        sub_step.id = f"{step_def.id}.{i}"
        sub_step.for_each = None  # Clear to prevent re-expansion
        sub_step._item = {step_def.for_each.variable: item}  # Available as ${item.var}
        sub_steps.append(sub_step)

    return sub_steps
```

Concurrency for `for_each` is controlled by `max_concurrency`. The runner uses both the per-step semaphore and the global session semaphore:

```python
step_sem = asyncio.Semaphore(step_def.for_each.max_concurrency)

async def run_with_semaphores(sub_step):
    async with step_sem:
        async with GLOBAL_SESSION_SEMAPHORE:
            return await execute_step(sub_step, execution)

results = await asyncio.gather(*[run_with_semaphores(s) for s in sub_steps])
```

#### Sub-Blueprint Execution

Sub-blueprints are recursive calls to the same runner function:

```python
async def execute_blueprint_step(step_def, execution):
    # Load the sub-blueprint definition
    sub_blueprint = load_blueprint(step_def.blueprint)
    sub_inputs = {k: interpolate(v, execution) for k, v in step_def.inputs.items()}

    # Execute recursively with parent link and trigger chain
    sub_execution = await execute_blueprint(
        sub_blueprint,
        sub_inputs,
        parent_execution_id=execution.execution_id,
        trigger_chain=execution.trigger_chain + [
            (execution.blueprint, "sub-blueprint")
        ],
    )

    return StepResult(
        status="completed" if sub_execution.status == "completed" else "failed",
        sub_execution_id=sub_execution.execution_id,
        sub_status=sub_execution.status,
    )
```

**Depth guard:** The runner tracks recursion depth via `trigger_chain` length. If depth exceeds 5, the step fails with an error. This prevents infinite loops from circular sub-blueprint references.

#### Conditional Routing Evaluation

Conditions are evaluated using Python's `eval()` in a restricted namespace:

```python
SAFE_BUILTINS = {
    "len": len, "str": str, "int": int, "float": float,
    "bool": bool, "any": any, "all": all, "min": min, "max": max,
    "True": True, "False": False, "true": True, "false": False,
    "None": None, "none": None,
}

def evaluate_condition(condition_str, execution):
    """Evaluate a condition expression against execution state."""
    if not condition_str:
        return True  # No condition = always execute

    namespace = {
        "__builtins__": SAFE_BUILTINS,
        "steps": _build_steps_namespace(execution),
        "inputs": execution.inputs,
        "env": dict(os.environ),
    }

    try:
        return bool(eval(condition_str, namespace))
    except Exception as e:
        # Condition evaluation failure — log and treat as false
        log.warning(f"Condition eval failed for '{condition_str}': {e}")
        return False
```

The `_build_steps_namespace` creates an object where `steps.step_id.status`, `steps.step_id.exit_code`, `steps.step_id.outputs.name` are all accessible via attribute access (using `types.SimpleNamespace`).

### State Persistence to MongoDB

The execution record is written to MongoDB at these points:

1. **Execution created** — initial record with status `running`, includes `definition_snapshot`
2. **Step started** — step status changes to `running`
3. **Step status change** — `waiting_for_human`, `completed`, `failed`, `skipped`, `timed_out`, `crashed`
4. **Execution completed/failed** — final status, ended_at timestamp

Each write is an atomic `update_one` with `$set` on the changed fields. The entire execution record is NOT rewritten each time — only the changed step is updated:

```python
async def update_step_in_db(execution_id, step_id, step_update):
    collection = get_collection("blueprint_executions")
    collection.update_one(
        {"execution_id": execution_id, "steps.id": step_id},
        {"$set": {
            f"steps.$.status": step_update.status,
            f"steps.$.ended_at": step_update.ended_at,
            f"steps.$.duration_s": step_update.duration_s,
            f"steps.$.exit_code": step_update.exit_code,
            f"steps.$.outputs": step_update.outputs,
            f"steps.$.error": step_update.error,
            "updated_at": now_iso(),
        }}
    )
```

### Crash Recovery

If the runner process dies (machine restart, crash, OOM kill), executions can resume:

1. On startup, the runner waits for MongoDB connectivity with exponential backoff (1s, 2s, 4s... up to 60s). This prevents crash loops when MongoDB is the cause.
2. The runner queries MongoDB for executions with `status: running`
3. For each found execution:
   a. Load the blueprint from the **`definition_snapshot`** field in the execution record (NOT from the current YAML file — the definition may have changed since the execution started)
   b. Steps with `status: completed` are skipped (never re-executed)
   c. Steps with `status: running` are treated as `crashed` (the session that was running them is likely dead) — retry policy applies
   d. Steps with `status: pending` proceed normally
   e. Steps with `status: waiting_for_human` remain in that state (the notification was already sent)
4. **Child-first recovery:** Sub-blueprint executions (those with `parent_execution_id` set) are recovered first. Parents resume once their child executions are resolved.
5. The runner resumes the main loop from where it left off

```python
async def recover_executions():
    """Find and resume any in-flight executions after a crash."""
    # Wait for MongoDB with exponential backoff
    await wait_for_mongodb(max_wait=60)

    collection = get_collection("blueprint_executions")

    # Recover children first, then parents
    in_flight = list(collection.find({"status": "running"}).sort(
        [("parent_execution_id", -1)]  # Children (non-null parent) first
    ))

    for exec_doc in in_flight:
        # Mark any 'running' steps as 'crashed' so they can be retried
        for step in exec_doc.get("steps", []):
            if step["status"] == "running":
                step["status"] = "crashed"
                step["error"] = "Runner process crashed during execution"

        collection.update_one(
            {"execution_id": exec_doc["execution_id"]},
            {"$set": {"steps": exec_doc["steps"], "updated_at": now_iso()}}
        )

        # Load blueprint from the frozen snapshot, NOT current YAML
        blueprint = BlueprintDef.from_dict(exec_doc["definition_snapshot"])
        asyncio.create_task(resume_execution(blueprint, exec_doc))
```

A `crashed` step is treated like a failed step — the retry policy applies. If retries remain, the step re-executes. If exhausted, the step is marked `failed` and `on_failure` determines whether the execution continues.

### Resource Contention

**Worktrees provide isolation for the OS repo.** Every session created via `session create` gets its own git worktree. Two blueprints working on the OS repo get separate worktrees automatically. No advisory locks needed for OS repo access.

**External repo contention is a known limitation.** Two blueprints targeting the same external repo (e.g., `indemn-platform-v2`) via `add_dirs` would share that repo's working directory. If both modify files, they can corrupt each other's git staging. Mitigation options:
- Use `session create --add-dir` which gives read-only access (sessions cannot modify the external repo's working tree from the worktree).
- For blueprints that need to modify an external repo, ensure only one runs at a time by using the same `system` tag and `max_concurrent_sessions: 1` at the runner level.
- Future: extend the session manager to create worktrees of external repos.

**Hive CLI slug collisions** are handled by the Hive CLI itself (it already appends `-2`, `-3` for duplicate slugs on the same day).

**API rate limits:** The global session semaphore (`GLOBAL_SESSION_SEMAPHORE`, default 4) limits the total number of concurrent Claude Code sessions across all blueprints. This prevents hitting Anthropic API rate limits. Adjust via the `BLUEPRINT_GLOBAL_MAX_SESSIONS` environment variable.

---

## 4. Notification System

### Overview

Notifications are a Hive-native primitive. The blueprint runner (and any other system) creates notifications via `hive notify`. Delivery is Wall tiles (always) plus optional pluggable channels. Blueprints never reference Slack or any specific delivery channel directly.

### Notification Record Schema

**Collection:** `hive.notifications`

```json
{
  "_id": "ObjectId",
  "notification_id": "string",          // Auto-generated: notify-{YYYY-MM-DD-HH-MM-SS}-{counter}
  "message": "string",                  // Human-readable notification text
  "priority": "string",                 // low, normal, high, critical (default: normal)
  "status": "string",                   // unread, read, dismissed (default: unread)

  // Source attribution
  "source": "string",                   // What created this: "blueprint", "system", "manual"
  "execution_id": "string?",            // Blueprint execution that created it (if any)
  "step_id": "string?",                 // Step that created it (if any)
  "blueprint": "string?",               // Blueprint name (if any)

  // Classification
  "domains": ["string"],                // Inherited from blueprint or explicit
  "tags": ["string"],                   // Optional categorization

  // Lifecycle
  "created_at": "datetime",
  "read_at": "datetime?",              // When marked as read
  "dismissed_at": "datetime?",         // When dismissed
  "expires_at": "datetime?",           // Optional auto-dismiss (e.g., time-sensitive notifications)

  // Action (optional — what the user can do about it)
  "action": {
    "label": "string",                 // e.g., "Attach to session"
    "command": "string"                // e.g., "session attach bp-morning-review-abc12345"
  }
}
```

**Indexes on `notifications`:**
- `notification_id`: unique
- `status`: regular (find unread notifications)
- `created_at`: regular (temporal queries)
- `priority`: regular
- Compound: `{status: 1, priority: -1, created_at: -1}` (unread notifications sorted by priority then recency)

### `hive notify` CLI Command

```bash
# Create a notification
hive notify "message text" [--priority low|normal|high|critical] \
  [--source blueprint|system|manual] \
  [--execution-id <id>] [--step-id <id>] [--blueprint <name>] \
  [--domains dom1,dom2] [--tags tag1,tag2] \
  [--action-label "text" --action-command "cmd"] \
  [--expires-in <duration>]

# List notifications
hive notify list [--status unread|read|all] [--priority high,critical] [--limit N]

# Mark as read
hive notify read <notification-id>

# Dismiss
hive notify dismiss <notification-id>

# Dismiss all read
hive notify dismiss-read
```

**Output format follows the Hive convention:** JSON when piped, text when interactive.

### Wall Tile Rendering for Notifications

Notifications appear as tiles on the Wall with a distinct visual treatment:

| Field | Tile Visual |
|-------|-------------|
| `message` | Tile label (truncated to fit) |
| `priority` | Visual weight — critical: pulsing border, high: bold border, normal: standard, low: subtle |
| `status` | Brightness — unread: vivid, read: normal, dismissed: hidden |
| `source` | Icon indicator — blueprint icon, system icon, or manual icon |
| `action` | Clickable action button on the tile (if present) |

**New type badge color:**

| Type | Color | Hex |
|------|-------|-----|
| `notification` | Amber/warning yellow | `#f59e0b` |

Unread notifications sort to the top of the Wall regardless of other ordering rules. Critical and high priority notifications get additional visual emphasis (border glow, size boost).

**Read/dismiss interaction:**
- Clicking a notification tile marks it as `read`
- A dismiss button (X) on the tile marks it as `dismissed` (hidden from Wall)
- `hive notify dismiss-read` bulk-clears all read notifications

### Pluggable Delivery (Future)

V1 delivery: Wall tiles + `hive notify list` CLI. This is sufficient because Craig is always either looking at the Wall or working in a session where CLI is available.

Future delivery channels (configured per-notification-priority, not per-blueprint):
- Slack: route high/critical to a Slack channel
- macOS notifications: `osascript -e 'display notification ...'`
- Email: for critical issues when away from desk
- Mobile push: via a future mobile companion

Configuration would live in `hive/.registry/notification-config.yaml` (future, not designed here).

---

## 5. Observability

### Execution Record Data Model

Every blueprint execution creates a document in `hive.blueprint_executions`:

```json
{
  "execution_id": "morning-consultation-2026-03-24-07-00",
  "blueprint": "morning-consultation",
  "blueprint_version": 1,
  "status": "completed",
  "mode": "multi-session",
  "parent_execution_id": null,
  "trigger": "schedule",
  "trigger_chain": [["morning-consultation", "schedule"]],
  "inputs": {"date": "2026-03-24"},
  "definition_snapshot": { /* full parsed YAML, frozen at execution start */ },

  "started_at": "2026-03-24T07:00:00Z",
  "ended_at": "2026-03-24T07:38:22Z",
  "duration_s": 2302,

  "cost_estimate_usd": 2.30,

  "steps": [
    {
      "id": "sync",
      "name": "Sync external systems",
      "type": "cli",
      "status": "completed",
      "started_at": "2026-03-24T07:00:00Z",
      "ended_at": "2026-03-24T07:00:45Z",
      "duration_s": 45,
      "exit_code": 0,
      "retry_count": 0,
      "outputs": {},
      "error": null
    },
    {
      "id": "gather-context",
      "name": "Gather morning context",
      "type": "session",
      "status": "completed",
      "started_at": "2026-03-24T07:00:45Z",
      "ended_at": "2026-03-24T07:08:12Z",
      "duration_s": 447,
      "session_id": "abc-123-def",
      "session_name": "bp-morning-con-gather-con-abcd1234",
      "cost_estimate_usd": 0.45,
      "retry_count": 0,
      "outputs": {},
      "error": null,
      "hive_records_created": ["2026-03-24-morning-context"]
    },
    {
      "id": "interactive-review",
      "name": "Morning review with Craig",
      "type": "session",
      "status": "completed",
      "started_at": "2026-03-24T07:08:12Z",
      "ended_at": "2026-03-24T07:35:00Z",
      "duration_s": 1608,
      "session_id": "ghi-456-jkl",
      "session_name": "bp-morning-con-interactiv-ghi45678",
      "cost_estimate_usd": 1.61,
      "interactive": true,
      "retry_count": 0,
      "outputs": {},
      "error": null
    },
    {
      "id": "save-summary",
      "name": "Save session summary",
      "type": "cli",
      "status": "completed",
      "started_at": "2026-03-24T07:35:00Z",
      "ended_at": "2026-03-24T07:35:02Z",
      "duration_s": 2,
      "exit_code": 0,
      "retry_count": 0,
      "outputs": {},
      "error": null,
      "hive_records_created": ["2026-03-24-morning-consultation"]
    }
  ],

  "hive_records_created": [
    "2026-03-24-morning-context",
    "2026-03-24-morning-consultation"
  ],
  "summary_record_id": "2026-03-24-morning-execution-summary",

  "created_at": "2026-03-24T07:00:00Z",
  "updated_at": "2026-03-24T07:38:22Z"
}
```

### Step Status Enum

The complete set of step statuses:

| Status | Meaning |
|--------|---------|
| `pending` | Not yet started |
| `running` | Currently executing |
| `waiting_for_human` | Interactive step waiting for human to join/complete |
| `completed` | Finished successfully |
| `failed` | Finished with error |
| `skipped` | Condition evaluated to false |
| `timed_out` | Exceeded timeout |
| `crashed` | Runner process died during this step (set during crash recovery) |

### Token Usage and Cost Tracking

Without the Agent SDK, exact token counts and costs are not available from the session. The runner tracks what it can:

| Metric | Source | Accuracy |
|--------|--------|----------|
| Wall-clock duration per step | Runner timestamps | Exact |
| CLI step exit codes | subprocess return code | Exact |
| Session step duration | Session state file timestamps | Exact |
| Context remaining % | Session state file (`context_remaining_pct`) | Exact (reported by hooks) |
| Cost estimate | Duration-based heuristic: Opus ~$0.06/min, Sonnet ~$0.02/min | Rough estimate — advisory only |
| Records created | Query `hive recent 5m` after step completes | Best-effort |

**`max_cost_usd` is advisory.** The runner logs a warning when the estimated cost exceeds the budget. It does NOT hard-kill the execution. Cost enforcement would require exact token tracking, which is not available without Agent SDK integration or session manager enhancements.

### Hive CLI Blueprint Commands

The Hive CLI gains a `blueprint` subcommand group:

```bash
# List all blueprint definitions
hive blueprint list
hive blueprint list --system code-dev
hive blueprint list --tags daily

# Show a blueprint definition
hive blueprint show <name>
hive blueprint show morning-consultation

# Run a blueprint
hive blueprint run <name> [--input key=value ...]
hive blueprint run morning-consultation --input date=2026-03-24
hive blueprint run market-analysis --input segment="P&C brokers"

# List executions
hive blueprint executions [--blueprint <name>] [--status <status>] [--recent <duration>]
hive blueprint executions --blueprint morning-consultation --recent 7d
hive blueprint executions --status running

# Show execution status (real-time)
hive blueprint status <execution-id>
hive blueprint status morning-consultation-2026-03-24-07-00

# Cancel a running execution
hive blueprint cancel <execution-id>

# Resume a failed/crashed execution from last completed step
hive blueprint resume <execution-id>

# Show execution history for a blueprint
hive blueprint history <name> [--limit N]
hive blueprint history morning-consultation --limit 30

# Preview upcoming scheduled runs across all blueprints
hive blueprint schedule [--hours N]
hive blueprint schedule --hours 48

# Validate a blueprint YAML without running it
hive blueprint validate <path-to-yaml>
# Validates: YAML syntax, schema conformance, DAG cycle detection,
# referenced sub-blueprint existence, depends_on reference validity,
# condition expression syntax, variable reference validity

# Reload all blueprint definitions (after editing YAML files)
hive blueprint reload
```

**Output format follows the Hive convention:** JSON when piped, text when interactive.

Example output of `hive blueprint status`:

```
Blueprint: morning-consultation
Execution: morning-consultation-2026-03-24-07-00
Mode: multi-session
Status: running
Started: 2026-03-24 07:00:00 (12m ago)
Trigger: schedule

Steps:
  [completed]        sync                  45s     exit:0
  [completed]        gather-context        7m 27s  session:bp-morning-con-gather-con-abcd1234
  [waiting_for_human] interactive-review   4m 12s  session:bp-morning-con-interactiv-ghi45678
  [pending]          save-summary          -       -

Cost estimate: $2.06
Records created: 2026-03-24-morning-context
Notifications: 1 (high priority — waiting for human)
```

### Wall UI — Blueprint Tiles

Blueprint executions appear as tiles on the Hive Wall. They are a new tile data source alongside Hive records and session state files.

**Tile type: `blueprint_execution`**

| Field | Tile Visual |
|-------|-------------|
| Blueprint name | Tile title |
| Status | Background brightness (running=lifted, completed=surface, failed=error accent) |
| Current step name | Subtitle / context line |
| Duration | Timestamp area |
| Step progress | Progress indicator (e.g., "3/5 steps" for multi-session, none for single-session) |
| Domain | Accent bar color |
| Cost estimate | Secondary info |

**New type badge color:**

| Type | Color | Hex |
|------|-------|-----|
| `blueprint_execution` | Electric blue | `#2563eb` |

**Real-time updates:** The Wall polls blueprint executions via a new API route (`GET /api/blueprints/executions?status=running`). Poll interval: 5 seconds for running executions (faster than the 30s Hive poll since execution state changes rapidly). The Express backend queries the `blueprint_executions` MongoDB collection directly.

**Drill-down interaction:**
1. **Click a running blueprint tile** -> Focus area shows the execution detail view with step-by-step progress, each step's status, duration, and any outputs. If the current step is an interactive session, the Focus area can open the session's tmux terminal alongside the execution view.
2. **Click a completed blueprint tile** -> Shows the execution summary: all steps, durations, cost, and links to Hive records created. Clicking a step record drills into the specific step's outputs.
3. **Click a failed blueprint tile** -> Shows the error details: which step failed, the error message, retry history, and an action button to resume from the failed step.

### Wall Data Pipeline (Three Sources)

| Source | What It Provides | Update Frequency |
|--------|-----------------|-----------------|
| `sessions/*.json` | Active session tiles | Real-time (hooks) |
| Hive API (MongoDB `records`) | Entity and knowledge tiles | 30s polling |
| Blueprint API (MongoDB `blueprint_executions`) | Running/recent execution tiles | 5s polling for running, 30s for completed |
| **Notification API (MongoDB `notifications`)** | **Unread notification tiles** | **5s polling** |

---

## 6. Hive Integration

### Context Assembly as a Blueprint Step

The existing playbooks (`morning.md`, `code-dev.md`, `content.md`, `ceo-weekly.md`) are absorbed as the first step of their corresponding blueprints. The playbook file itself remains — it's referenced by the `playbook_path` field on a session step.

**For multi-session blueprints:** Context assembly is an explicit session step. The session follows the playbook instructions, which include Hive CLI commands for context gathering. The LLM decides what queries to run based on the playbook — the runner never calls `hive search`/`hive refs`/`hive recent` itself.

```yaml
steps:
  - id: assemble-context
    type: session
    autonomous: true
    playbook_path: "systems/hive/playbooks/code-dev.md"
    prompt: "Assemble context for workflow: ${inputs.workflow_id}"
    timeout_minutes: 15
```

**For single-session blueprints:** Context assembly instructions are baked into the `playbook_path` content, which is prepended to the combined prompt. The session itself runs the Hive CLI commands as part of its work.

**This preserves the Hive design principle:** "Context assembly is an LLM agent that uses the Hive CLI as its toolkit" — not a fixed algorithm in the runner.

### Execution Artifacts Feed the Knowledge Graph (Self-Compressing)

When a blueprint execution completes, the runner creates a Hive knowledge record:

```python
def create_execution_summary_record(execution):
    """Create a Hive knowledge record summarizing the execution."""
    step_summaries = []
    for step in execution.steps:
        status_icon = {"completed": "PASS", "failed": "FAIL",
                       "skipped": "SKIP", "timed_out": "TIMEOUT"}.get(step.status, "?")
        step_summaries.append(
            f"- [{status_icon}] {step.name} ({format_duration(step.duration_s)})"
        )

    body = f"""Blueprint: {execution.blueprint}
Trigger: {execution.trigger}
Mode: {execution.mode}
Duration: {format_duration(execution.duration_s)}
Cost estimate: ${execution.cost_estimate_usd:.2f}
Status: {execution.status}

## Steps
{chr(10).join(step_summaries)}

## Records Created
{chr(10).join(f'- {rid}' for rid in execution.hive_records_created)}
"""

    # Create via Hive CLI
    subprocess.run([
        "hive", "create", "note",
        f"Execution: {execution.blueprint} ({execution.started_at[:10]})",
        "--tags", "execution_summary,blueprint",
        "--domains", ",".join(execution.domains),
        "--refs", f"blueprint:{execution.blueprint}",
        "--body", body,
    ], timeout=30)
```

These summary records are lightweight — they capture what happened and link to the execution record in MongoDB for details. Context assembly sessions can find them:

```bash
hive search "morning consultation" --tags execution_summary --recent 7d
```

### What Happens to Existing Components

| Component | Current State | After Blueprints |
|-----------|-------------|-----------------|
| **Playbooks** (`systems/hive/playbooks/`) | 4 markdown files defining context assembly instructions | Preserved as-is. Referenced by blueprint session steps via `playbook_path`. No migration needed. |
| **Dispatch engine** (`systems/dispatch/engine.py`) | Ralph loop using Agent SDK | Deprecated. Replaced by `task-execution` blueprint (which uses session manager instead of Agent SDK). Migration: convert existing epics to blueprint definitions. |
| **Dispatch skill** (`.claude/skills/dispatch/SKILL.md`) | Skill that invokes the dispatch engine | Rewritten to invoke `hive blueprint run` instead. |
| **Code-dev skill** (`.claude/skills/code-dev/SKILL.md`) | Guides design/review/plan/execute/test phases | Preserved. Blueprints encode the workflow; the skill provides interactive guidance within individual sessions. They're complementary. |
| **Brainstorm-hive skill** (`.claude/skills/brainstorm-hive/SKILL.md`) | Checkpoints decisions during brainstorming | Preserved. Used within interactive blueprint steps. |
| **Session manager** (`systems/session-manager/cli.py`) | Creates/manages Claude Code sessions in tmux | Preserved. The blueprint runner is a consumer. Three enhancements needed (see below). |
| **Context assembly** (Hive design's "dedicated context assembly session") | A short-lived session that gathers context and writes a note | Becomes the first step of a blueprint. Same mechanism, now tracked and observable. |

### Session Manager Enhancements Needed

The session manager CLI needs three additions for blueprint integration:

1. **`--json` flag on `session create`** — Output machine-readable JSON instead of human-readable text. The runner parses `session_id` from this output.

2. **`--skip-cleanup` flag on `session close`** — Skip the natural-language cleanup commands (commit, push, INDEX.md update) and go directly to `/exit` + state update. Blueprint autonomous sessions typically don't need git cleanup — the runner controls when and how cleanup happens.

3. **`--prompt-file` flag on `session send`** — Read the prompt from a file instead of a command-line argument. Blueprint prompts can be thousands of characters, which exceeds reliable `tmux send-keys` delivery for very long strings.

### New Tags for Ontology

Add to `hive/.registry/ontology.yaml`:

```yaml
tags:
  # ... existing tags ...

  # Blueprint system tags
  blueprint: { description: "Blueprint definition or execution artifact", category: system }
  execution_summary: { description: "Summary of a blueprint execution", category: system }
  blueprint_output: { description: "Output produced by a blueprint step", category: system }
```

**Note:** `blueprint` is a tag, not an entity type. Blueprint definitions are YAML files; they don't need to be entities. Execution summaries are knowledge records tagged `execution_summary`. This keeps the entity type list clean and avoids the routing ambiguity issue.

### Skills vs Blueprints Boundary

**Skills = atomic capabilities** that sessions have. How to use a CLI, reference knowledge, domain expertise. Sessions spawned by blueprints use skills as tools.

**Blueprints = executable workflows** — sequences of work with scheduling, tracking, observability. They orchestrate sessions that use skills.

| Category | Stays as Skill | Becomes Blueprint |
|----------|---------------|------------------|
| Tool skills | /hive, /slack, /github, /linear, etc. | Never |
| Reference skills | /meeting-intelligence, /pipeline-deals | Never |
| Workflow skills | /brainstorm-hive (used within sessions) | /morning, /weekly-summary, /code-dev (the orchestration part) |

**Coexistence, not migration.** Blueprints are built alongside existing skills with zero breaking changes. Both work simultaneously. Migration is a deliberate one-time cutover when Craig is ready, not a gradual process during development.

### Wall UI API Routes

The Express backend (`systems/os-terminal/`) gains new routes:

```
GET /api/blueprints/definitions        List all blueprint definitions
GET /api/blueprints/executions         List executions (filterable by status, blueprint, recent)
GET /api/blueprints/executions/:id     Get single execution with step details
POST /api/blueprints/run               Start a blueprint execution
POST /api/blueprints/cancel/:id        Cancel a running execution
POST /api/blueprints/resume/:id        Resume a failed execution
GET /api/notifications                 List notifications (filterable by status, priority)
POST /api/notifications/:id/read       Mark notification as read
POST /api/notifications/:id/dismiss    Dismiss notification
```

---

## 7. Data Model

### Blueprint Definitions (YAML Files + MongoDB Cache)

**Source of truth:** `hive/blueprints/*.yaml` (git-tracked)

**MongoDB cache:** `hive.blueprint_defs` collection. Parsed from YAML on `hive blueprint reload` or when files change. Used for fast listing and search.

```json
{
  "name": "morning-consultation",
  "description": "Daily morning planning — sync systems, gather context, present briefing",
  "version": 1,
  "mode": "multi-session",
  "domains": ["indemn", "career-catalyst", "personal"],
  "tags": ["daily", "planning"],
  "system": "hive",
  "schedule": {"cron": "0 7 * * 1-5", "timezone": "America/Vancouver"},
  "triggers": [],
  "step_count": 4,
  "step_ids": ["sync", "gather-context", "interactive-review", "save-summary"],
  "has_interactive_steps": true,
  "file_path": "hive/blueprints/morning-consultation.yaml",
  "parsed_at": "2026-03-24T10:00:00Z",
  "yaml_hash": "sha256:abc123..."
}
```

**Indexes on `blueprint_defs`:**
- `name`: unique
- `tags`: multikey
- `system`: regular
- `schedule.cron`: regular (for scheduler to find scheduled blueprints)

### Execution Records

**Collection:** `hive.blueprint_executions`

Full schema:

```json
{
  "execution_id": "string",           // Unique: {blueprint}-{ISO timestamp} or append -2, -3
  "blueprint": "string",              // References blueprint_defs.name
  "blueprint_version": "integer",
  "mode": "string",                   // single-session | multi-session
  "status": "string",                 // pending, running, completed, failed, cancelled, timed_out
  "parent_execution_id": "string?",   // For sub-blueprints
  "trigger": "string",                // schedule, manual, file_change, hive_record, webhook, sub-blueprint
  "trigger_chain": "array",           // List of [blueprint, trigger_type] tuples for cycle detection
  "inputs": "object",                 // Input parameters
  "definition_snapshot": "object",    // Full parsed YAML, frozen at execution start.
                                      // Used by crash recovery instead of current YAML.

  "started_at": "datetime",
  "ended_at": "datetime?",
  "duration_s": "number?",
  "cost_estimate_usd": "number?",

  "steps": [                          // Array of step records
    {
      "id": "string",
      "name": "string",
      "type": "string",               // cli, session, script, blueprint
      "status": "string",             // pending, running, waiting_for_human, completed,
                                      // failed, skipped, timed_out, crashed
      "condition": "string?",
      "started_at": "datetime?",
      "ended_at": "datetime?",
      "duration_s": "number?",
      "exit_code": "integer?",        // CLI/script steps
      "session_id": "string?",        // Session steps
      "session_name": "string?",
      "sub_execution_id": "string?",  // Blueprint steps
      "interactive": "boolean",
      "retry_count": "integer",
      "cost_estimate_usd": "number?",
      "outputs": "object",            // Captured outputs
      "error": "string?",
      "hive_records_created": ["string"]
    }
  ],

  "hive_records_created": ["string"], // All records created across all steps
  "summary_record_id": "string?",    // ID of the Hive knowledge summary record

  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Indexes on `blueprint_executions`:**
- `execution_id`: unique
- `blueprint`: regular (list executions by blueprint)
- `status`: regular (find running executions)
- `parent_execution_id`: regular (find sub-executions)
- `started_at`: regular (temporal queries)
- `updated_at`: regular
- Compound: `{blueprint: 1, started_at: -1}` (history queries)
- Compound: `{status: 1, updated_at: -1}` (active execution listing)

**No TTL.** Execution records are retained indefinitely. Execution history is valuable for trend analysis, debugging, and pattern recognition. If volume becomes an issue (projected ~17k records/year at full utilization), implement archival to a cold collection rather than deletion.

### Relationship to Hive Records

```
blueprint_defs (MongoDB)     <-- Cached from hive/blueprints/*.yaml
        |
        | 1:many
        v
blueprint_executions (MongoDB)  <-- Operational state, no TTL
        |
        | creates (on completion)
        v
hive.records (MongoDB)          <-- Knowledge: execution_summary tagged notes
        |                           These are permanent, searchable, feed context assembly
        | references
        v
hive.records (MongoDB)          <-- Knowledge records created DURING execution
                                    (decisions, designs, notes, session summaries)
```

Blueprint executions do NOT pollute the `hive.records` collection with step-level data. They create exactly one summary record per execution (on completion) and zero or more knowledge records as a byproduct of the work done in each step.

---

## 8. Example Blueprints

### Example 1: Morning Consultation (Multi-Session, Interactive)

```yaml
name: morning-consultation
description: "Daily morning planning — sync systems, gather context, present briefing"
version: 1
mode: multi-session
domains: [indemn, career-catalyst, personal]
tags: [daily, planning]
system: hive

schedule:
  cron: "0 7 * * 1-5"
  timezone: "America/Vancouver"

config:
  max_duration_minutes: 45
  max_cost_usd: 5.0
  notification:
    on_complete: true
    on_human_needed: true

inputs:
  date:
    type: string
    required: false
    default: "today"
    description: "Date for the consultation (default: today)"

steps:
  - id: sync
    name: "Sync external systems"
    type: cli
    command: "hive sync"
    timeout_seconds: 120
    on_failure: continue

  - id: gather-context
    name: "Gather morning context"
    type: session
    depends_on: [sync]
    autonomous: true
    model: opus
    playbook_path: "systems/hive/playbooks/morning.md"
    prompt: |
      Today's date: ${inputs.date}
      Follow the morning consultation playbook.
      Write the assembled context as a Hive note:
      hive create note "Morning context ${inputs.date}" \
        --tags context_assembly,morning \
        --domains indemn,career-catalyst,personal \
        --body "<your assembled context>"
      Then exit with /exit.
    timeout_minutes: 15

  - id: interactive-review
    name: "Morning review with Craig"
    type: session
    depends_on: [gather-context]
    interactive: true
    model: opus
    context_from: [gather-context]
    prompt: |
      You are running a morning planning session.
      The context assembled by the previous step is included above.
      Present the day's landscape. Ask about priorities. Update records as discussed.
    timeout_minutes: 30
    close_on_complete: false

  - id: save-summary
    name: "Save session summary"
    type: cli
    depends_on: [interactive-review]
    command: |
      hive create note "Morning consultation ${inputs.date}" \
        --tags session_summary,morning \
        --domains indemn,career-catalyst,personal \
        --body "Morning consultation completed. See session for details."
    on_failure: continue
```

### Example 2: Quick Code Review (Single-Session)

```yaml
name: quick-code-review
description: "Review a PR — read the diff, post findings as a Hive note"
version: 1
mode: single-session
domains: [indemn]
tags: [code-review, code-dev]
system: code-dev

triggers:
  - type: manual

model: opus
permissions: bypassPermissions
timeout_minutes: 20

inputs:
  pr_number:
    type: number
    required: true
    description: "GitHub PR number to review"
  repo:
    type: string
    required: false
    default: "indemn-ai/indemn-platform-v2"
    description: "GitHub org/repo"

config:
  max_cost_usd: 3.0
  notification:
    on_complete: true

steps:
  - id: read-diff
    name: "Read the PR diff"
    type: cli
    command: "gh pr diff ${inputs.pr_number} --repo ${inputs.repo}"
    description: "Fetch the full diff for the PR"

  - id: read-description
    name: "Read the PR description"
    type: cli
    command: "gh pr view ${inputs.pr_number} --repo ${inputs.repo}"
    description: "Fetch the PR title, body, and metadata"

  - id: review
    name: "Review the code changes"
    type: session
    description: "Analyze the diff for bugs, design issues, and improvements"
    prompt: |
      Review the PR thoroughly. Look for:
      - Bugs and logic errors
      - Design issues and architectural concerns
      - Missing tests or edge cases
      - Performance implications

  - id: write-findings
    name: "Write review findings to the Hive"
    type: cli
    command: |
      hive create note "PR Review: #${inputs.pr_number}" \
        --tags review,code,blueprint_output \
        --domains indemn \
        --body "<your review findings>"
    description: "Create a Hive record with your review findings"
```

**How this runs in single-session mode:** The runner creates one session and sends a combined prompt:

```
1. **Read the PR diff**
   Run: `gh pr diff 42 --repo indemn-ai/indemn-platform-v2`
   (Fetch the full diff for the PR)

2. **Read the PR description**
   Run: `gh pr view 42 --repo indemn-ai/indemn-platform-v2`
   (Fetch the PR title, body, and metadata)

3. **Review the code changes**
   Analyze the diff for bugs, design issues, and improvements
   Review the PR thoroughly. Look for:
   - Bugs and logic errors
   ...

4. **Write review findings to the Hive**
   Run: `hive create note "PR Review: #42" ...`
   (Create a Hive record with your review findings)

Write all significant output as Hive records. When done, exit with /exit.
```

The session does all four steps as one coherent task. The runner tracks one session, not four steps.

### Example 3: Feature Lifecycle (Complex, Multi-Phase)

```yaml
name: feature-lifecycle
description: "End-to-end feature development: design, review, plan, implement, test, deploy"
version: 1
mode: multi-session
domains: [indemn]
tags: [code-dev, feature]
system: code-dev

triggers:
  - type: manual

config:
  max_duration_minutes: 2880
  max_cost_usd: 100.0
  max_concurrent_sessions: 2
  notification:
    on_failure: true
    on_human_needed: true
    on_complete: true

inputs:
  workflow_id:
    type: record_id
    required: true
    description: "Hive workflow entity ID for this feature"
  repo_path:
    type: string
    required: true
    description: "Absolute path to the target repository"
  objective:
    type: string
    required: true
    description: "What we're building and why"

steps:
  # Phase 1: Context Assembly (dedicated LLM step)
  - id: assemble-context
    name: "Assemble development context"
    type: session
    autonomous: true
    playbook_path: "systems/hive/playbooks/code-dev.md"
    prompt: |
      Assemble context for workflow: ${inputs.workflow_id}
      Objective: ${inputs.objective}
      Target repo: ${inputs.repo_path}

      Write the assembled context as a Hive note:
      hive create note "Context: ${inputs.objective}" \
        --tags context_assembly --refs workflow:${inputs.workflow_id} \
        --domains indemn --body "<assembled context>"
    timeout_minutes: 10

  # Phase 2: Design (interactive — Craig drives)
  - id: design
    name: "Interactive design session"
    type: session
    depends_on: [assemble-context]
    interactive: true
    model: opus
    add_dirs: ["${inputs.repo_path}"]
    context_from: [assemble-context]
    prompt: |
      We're designing: ${inputs.objective}

      The assembled context is included above.

      Use /brainstorm-hive to checkpoint decisions. Create 10-20+ decision records.
      When the design is complete, write a design summary as a Hive note:
      hive create note "Design: ${inputs.objective}" \
        --tags design --refs workflow:${inputs.workflow_id} \
        --domains indemn --body "<design summary>"
    timeout_minutes: 120
    close_on_complete: false

  # Phase 3: Design Review (parallel — 3 independent reviews)
  - id: design-review
    name: "Independent design reviews"
    type: session
    depends_on: [design]
    for_each:
      variable: reviewer
      source:
        - architecture
        - edge-cases
        - implementation-feasibility
      max_concurrency: 3
    autonomous: true
    model: opus
    add_dirs: ["${inputs.repo_path}"]
    prompt: |
      You are reviewing a design from the perspective of: ${item.reviewer}

      Workflow: ${inputs.workflow_id}
      Run: hive refs ${inputs.workflow_id} --tags decision,design --depth 1

      Write your review findings as a Hive note:
      hive create note "Review (${item.reviewer}): ${inputs.objective}" \
        --tags design,review --refs workflow:${inputs.workflow_id} \
        --domains indemn --body "<your review findings>"
    timeout_minutes: 30
    outputs:
      review_results: collected

  # Phase 4: Address review findings (interactive)
  - id: address-reviews
    name: "Address design review findings"
    type: session
    depends_on: [design-review]
    interactive: true
    model: opus
    context_from: [design-review]
    prompt: |
      Design reviews are complete. The findings from all reviewers are included above.
      Address each finding — update the design, create decision records for changes.
    timeout_minutes: 60
    close_on_complete: false

  # Phase 5: Implementation plan
  - id: plan
    name: "Create implementation plan"
    type: session
    depends_on: [address-reviews]
    autonomous: true
    model: opus
    add_dirs: ["${inputs.repo_path}"]
    prompt: |
      Create an implementation plan for: ${inputs.objective}
      Workflow: ${inputs.workflow_id}
      Repo: ${inputs.repo_path}

      Read all decisions: hive refs ${inputs.workflow_id} --tags decision
      Break the work into discrete tasks with acceptance criteria.
      Write the plan as a Hive design record:
      hive create note "Implementation plan: ${inputs.objective}" \
        --tags design,plan --refs workflow:${inputs.workflow_id} \
        --domains indemn --body "<implementation plan>"
    timeout_minutes: 30

  # Phase 6: Implementation (sub-blueprint for each task)
  - id: implement
    name: "Execute implementation"
    type: blueprint
    depends_on: [plan]
    blueprint: task-execution
    inputs:
      workflow_id: "${inputs.workflow_id}"
      repo_path: "${inputs.repo_path}"
    timeout_minutes: 480

  # Phase 7: Final verification
  - id: verify
    name: "Verify implementation against design"
    type: session
    depends_on: [implement]
    condition: "steps.implement.outputs.sub_status == 'completed'"
    autonomous: true
    model: opus
    add_dirs: ["${inputs.repo_path}"]
    prompt: |
      Verify the implementation of: ${inputs.objective}
      Workflow: ${inputs.workflow_id}

      Read the original design decisions: hive refs ${inputs.workflow_id} --tags decision
      Check the code: read key files, run tests.
      Write a verification report:
      hive create note "Verification: ${inputs.objective}" \
        --tags review,verification --refs workflow:${inputs.workflow_id} \
        --domains indemn --body "<verification report>"
    timeout_minutes: 30

  # Phase 8: Update workflow
  - id: update-workflow
    name: "Update workflow status"
    type: cli
    depends_on: [verify]
    command: |
      hive update ${inputs.workflow_id} \
        --current-context "Implementation complete. Verified against design. Ready for deployment." \
        --status completed
```

### Example 4: Hive Sync (CLI-Only, Scheduled)

```yaml
name: hive-sync
description: "Sync all external systems into the Hive"
version: 1
mode: multi-session
domains: [indemn, career-catalyst, personal]
tags: [sync, maintenance]
system: hive

schedule:
  cron: "*/30 6-23 * * *"
  timezone: "America/Vancouver"

config:
  max_duration_minutes: 10
  max_cost_usd: 0
  notification:
    on_failure: true

steps:
  - id: sync-knowledge
    name: "Sync knowledge files to MongoDB"
    type: cli
    command: "hive sync --no-embed"
    timeout_seconds: 60
    on_failure: continue

  - id: sync-linear
    name: "Sync Linear issues"
    type: cli
    depends_on: []
    command: "hive sync linear"
    timeout_seconds: 60
    on_failure: continue

  - id: sync-calendar
    name: "Sync Google Calendar"
    type: cli
    depends_on: []
    command: "hive sync calendar"
    timeout_seconds: 60
    on_failure: continue

  - id: sync-github
    name: "Sync GitHub PRs"
    type: cli
    depends_on: []
    command: "hive sync github"
    timeout_seconds: 60
    on_failure: continue

  - id: sync-slack
    name: "Sync Slack mentions"
    type: cli
    depends_on: []
    command: "hive sync slack"
    timeout_seconds: 60
    on_failure: continue
```

### Example 5: Weekly Summary (Multi-Session, Scheduled)

```yaml
name: weekly-summary
description: "Weekly intelligence rollup — decisions, progress, signals, action items"
version: 1
mode: multi-session
domains: [indemn, career-catalyst, personal]
tags: [weekly, planning, summary]
system: hive

schedule:
  cron: "0 9 * * 5"
  timezone: "America/Vancouver"

config:
  max_duration_minutes: 30
  max_cost_usd: 5.0
  notification:
    on_complete: true

steps:
  - id: sync
    name: "Sync external systems"
    type: cli
    command: "hive sync"
    timeout_seconds: 120
    on_failure: continue

  - id: gather-data
    name: "Gather weekly data from Hive"
    type: cli
    depends_on: [sync]
    command: |
      echo "=== RECENT 7D ===" && \
      hive recent 7d --format json && \
      echo "=== ACTIVE WORKFLOWS ===" && \
      hive list workflow --status active --format json && \
      echo "=== DECISIONS ===" && \
      hive search "" --tags decision --recent 7d --format json && \
      echo "=== EXECUTION SUMMARIES ===" && \
      hive search "" --tags execution_summary --recent 7d --format json
    outputs:
      weekly_data: stdout

  - id: compile-summary
    name: "Compile weekly summary"
    type: session
    depends_on: [gather-data]
    autonomous: true
    model: opus
    prompt: |
      Compile a weekly intelligence summary from this data:

      ${steps.gather-data.outputs.weekly_data}

      Structure:
      1. Key decisions made this week (with rationale)
      2. Progress on active workflows (what moved, what's stalled)
      3. Notable signals (customer signals, market, competitive)
      4. Action items for next week
      5. Blueprint execution summary (what ran, success rate, cost)

      Write the summary as a Hive record:
      hive create note "Weekly Summary ${execution.started_at}" \
        --tags session_summary,weekly \
        --domains indemn,career-catalyst,personal \
        --body "<the compiled summary>"
    timeout_minutes: 15

  - id: notify
    name: "Send completion notification"
    type: cli
    depends_on: [compile-summary]
    command: "hive notify 'Weekly summary is ready. Check the latest session_summary record.' --priority normal"
    on_failure: continue
```

---

## 9. Implementation Plan

### Phase 1: Core Runner + CLI (Week 1-2)

**Goal:** The runner can execute a simple sequential blueprint (both single-session and multi-session modes) with CLI and session steps. The CLI can list, show, run, and check status.

**Build order:**

1. **Blueprint definition schema** — Define the YAML schema including `mode` field, create a Python dataclass/Pydantic model to parse it. Write a validator (syntax, schema, DAG cycles, reference validity).
   - File: `systems/hive/blueprint_schema.py`

2. **MongoDB collections** — Create `blueprint_defs`, `blueprint_executions`, `notifications` collections with indexes.
   - File: `systems/hive/blueprint_db.py`

3. **Notification system** — `hive notify` CLI command, notification record CRUD, list/read/dismiss.
   - File: `systems/hive/notifier.py`
   - Add to: `systems/hive/cli.py`

4. **CLI executor** — `subprocess`-based CLI step execution with timeout, output capture.
   - File: `systems/hive/executors/cli_executor.py`

5. **Session executor** — Session manager integration: create session (`--json`), send prompt (`--prompt-file`), three-phase poll (launch → send → completion), close session (`--skip-cleanup`), stuck-session detection.
   - File: `systems/hive/executors/session_executor.py`

6. **Session manager enhancements** — Add `--json` to create, `--skip-cleanup` to close, `--prompt-file` to send.
   - Modify: `systems/session-manager/cli.py`

7. **Script executor** — subprocess-based script execution.
   - File: `systems/hive/executors/script_executor.py`

8. **Blueprint runner** — Main execution loop with sequential step processing, single-session mode, state persistence, crash recovery with `definition_snapshot`, global concurrency semaphore.
   - File: `systems/hive/blueprint_runner.py`

9. **Blueprint CLI commands** — `hive blueprint list|show|run|executions|status|validate|reload|schedule` added to `systems/hive/cli.py`.
   - File: `systems/hive/blueprint_cli.py`

10. **Variable interpolation** — `${...}` syntax resolution with escaping (`$${}`) and error handling.
    - File: `systems/hive/blueprint_interpolation.py`

11. **First blueprints** — `morning-consultation.yaml` (multi-session), `quick-code-review.yaml` (single-session), `hive-sync.yaml` (CLI-only).
    - Files: `hive/blueprints/`

**Exit criteria:** `hive blueprint run morning-consultation` executes all 4 steps. `hive blueprint run quick-code-review --input pr_number=42` runs in single-session mode. Execution records appear in MongoDB with `definition_snapshot`. `hive blueprint status` shows real-time progress. `hive notify list` shows notifications. Crash recovery works (kill runner, restart, it resumes using the snapshot).

### Phase 2: Parallel + Conditional + Sub-Blueprints (Week 2-3)

**Goal:** The runner handles the full step graph: dependency DAG, parallel fan-out, conditional routing, for_each loops (with YAML native list support), and sub-blueprint invocation.

**Build order:**

1. **DAG resolver** — Build dependency graph from step definitions, find eligible steps, detect cycles.
2. **Parallel execution** — `asyncio.gather` with semaphore-based concurrency limits (per-step + global).
3. **Condition evaluator** — Restricted `eval()` with safe builtins and namespace construction.
   - File: `systems/hive/blueprint_conditions.py`
4. **for_each expansion** — Expand loop steps into sub-steps, handle collected outputs, support YAML native lists.
5. **Blueprint executor** — Recursive sub-blueprint invocation with depth guard, parent linking, trigger chain.
   - File: `systems/hive/executors/blueprint_executor.py`
6. **Market-analysis blueprint** — Validates parallel fan-out.
7. **task-execution blueprint** — Replaces dispatch.
8. **feature-lifecycle blueprint** — Full end-to-end (Example 3).

**Exit criteria:** Market analysis blueprint runs 5 parallel sessions and consolidates. Feature lifecycle blueprint runs with sub-blueprint invocation. Conditional steps skip correctly. for_each loops iterate with YAML native list sources.

### Phase 3: Scheduler + Triggers (Week 3-4)

**Goal:** Blueprints run on schedule, react to events, and notify Craig when human input is needed.

**Build order:**

1. **Notification integration** — Wire notifications into the runner (on_complete, on_failure, on_human_needed).
2. **Cron scheduler** — `croniter`-based schedule evaluation, same process as runner.
3. **File change trigger** — `watchdog`-based filesystem monitoring with trailing-edge debounce.
4. **Hive record trigger** — MongoDB change stream subscription on `hive.records`.
5. **Webhook trigger** — Lightweight aiohttp server for HTTP triggers.
6. **Circular trigger prevention** — `trigger_chain` tracking with max depth.
7. **launchd service** — Auto-start scheduler/runner on boot.
   - File: `systems/hive/com.indemn.hive-scheduler.plist`
8. **Schedule morning-consultation** — Enable the cron schedule and verify it fires at 7am.
9. **Execution summary records** — Auto-create Hive knowledge record on execution completion.

**Exit criteria:** Morning consultation runs automatically at 7am. Craig gets a Wall notification when the interactive step is ready. Failed blueprints create high-priority notifications. `hive blueprint schedule` shows upcoming runs. Execution summaries appear as Hive knowledge records.

### Phase 4: Wall UI Integration (Week 4-5)

**Goal:** Blueprint executions and notifications are visible on the Hive Wall as tiles. Real-time step progress. Drill-down to execution details.

**Build order:**

1. **Express API routes** — Blueprint definition listing, execution CRUD, notification CRUD.
   - File: `systems/os-terminal/routes/blueprints.js`
2. **Blueprint execution tile component** — React component with step progress, status colors.
   - File: `systems/os-terminal/src/components/BlueprintTile.tsx`
3. **Notification tile component** — React component with priority visual treatment, action buttons.
   - File: `systems/os-terminal/src/components/NotificationTile.tsx`
4. **Execution detail view** — Focus area panel showing step-by-step execution state.
   - File: `systems/os-terminal/src/components/BlueprintDetail.tsx`
5. **Wall data merger** — Add blueprint + notification tiles to the Wall alongside Hive record tiles and session tiles. 5s polling for running executions and unread notifications.
6. **Type colors** — Add `blueprint_execution: #2563eb` and `notification: #f59e0b` to `TYPE_COLORS`.
7. **Run/cancel/resume from UI** — Action buttons on blueprint tiles.

**Exit criteria:** Running blueprints appear as tiles on the Wall with real-time step progress. Notifications appear with priority-based visual treatment. Completed/failed executions are visible with drill-down. Actions (run, cancel, resume, dismiss notification) work from the UI.

### Phase 5: Dispatch Migration + System Integration (Week 5-6)

**Goal:** Dispatch is fully replaced. Code-dev and content systems use blueprints. The dispatch skill points to the blueprint system.

**Build order:**

1. **task-execution blueprint** — Full replacement for the dispatch ralph loop.
2. **Rewrite dispatch skill** — Points to `hive blueprint run task-execution`.
3. **feature-lifecycle blueprint** — Validated end-to-end.
4. **content-pipeline blueprint** — Content creation workflow.
5. **Deprecate `systems/dispatch/engine.py`**.
6. **Blueprint skill** — New `.claude/skills/blueprint/SKILL.md`.

**Exit criteria:** All dispatch use cases run via blueprints. The dispatch engine is deprecated. Feature lifecycle and content pipeline blueprints work end-to-end. Existing skills continue to work unchanged.

---

## 10. Open Questions

These are genuinely uncertain areas where the recommended resolution is provided but may change during implementation.

### 1. Session Output Capture Reliability

**Question:** Without `last_message`, how reliably can the runner capture Hive records created by a session?

**Recommended resolution:** The runner queries `hive recent 5m --format json` after a session step completes, filtering by records that match the execution's domains and were created after the step started. This is best-effort — if the session creates a record with unexpected tags or domains, it might be missed. For critical data flow, session prompts should be explicit about the record's tags and refs. If exact output capture becomes critical, enhance the session manager to write the last assistant message to a sidecar file.

### 2. Scheduler Process Management

**Question:** How do we ensure the scheduler/runner stays running?

**Recommended resolution:** Use `launchd` (macOS native). Create a `.plist` file that auto-starts on boot and restarts on crash. Log to `.logs/hive-scheduler.log`. Add a heartbeat mechanism (write a timestamp to a MongoDB document every 60 seconds) so monitoring can detect if the process silently hangs.

### 3. Execution ID Format

**Question:** Should execution IDs be `{blueprint}-{timestamp}` (human-readable) or UUIDs (guaranteed unique)?

**Recommended resolution:** `{blueprint}-{YYYY-MM-DD-HH-MM-SS}` for human readability. If two executions of the same blueprint start in the same second, append a counter: `-2`, `-3`. This matches the Hive's date-slug convention.

### 4. Blueprint Versioning

**Question:** When a YAML definition changes, what happens to running executions?

**Resolved:** Running executions continue with the definition they started with. The `definition_snapshot` field in the execution record contains the full parsed YAML, frozen at execution start. Crash recovery loads from the snapshot, not the current file. New executions use the updated definition.

### 5. Data Privacy Across Domains

**Question:** Can a blueprint in one domain access data from another domain?

**Acknowledged limitation:** Yes. The `domains` field is metadata for classification and context assembly, not an access control mechanism. Autonomous blueprints with `bypassPermissions` can access any file, any MongoDB record, any Hive record. This is acceptable for the single-user (Craig) use case. If multi-user access is added in the future, domain-scoped access control becomes a requirement.

### 6. Testing and Dry-Run

**Question:** How do you test a new blueprint without real side effects?

**Recommended resolution for v1:** `hive blueprint validate` covers syntax, schema, DAG, and reference validation. For execution testing, run the blueprint manually and observe. A `--dry-run` flag that logs what each step WOULD do without executing is a future enhancement. For now, the cost is low — Craig can cancel a misbehaving blueprint immediately.

---

## Key Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-24 | Skills = atomic capabilities; Blueprints = executable workflows | Skills are what sessions can do. Blueprints are how work gets orchestrated. Skills live inside blueprints. |
| 2026-03-24 | Playbooks absorbed as context step of blueprints | No separate playbook mechanism. The playbook file is referenced by `playbook_path` on a session step. |
| 2026-03-24 | Dispatch replaced by blueprint system | The ralph loop becomes a `task-execution` blueprint using session manager instead of Agent SDK. |
| 2026-03-24 | Tracing is infrastructure-level, not self-reported | The runner observes sessions externally via state files. No instrumentation inside sessions. |
| 2026-03-24 | Two harnesses: Claude Code sessions (primary) + LangGraph deep agents (fallback) | Session steps for most work. Script steps can invoke LangGraph for specialized agents. |
| 2026-03-24 | No Agent SDK — sessions via session manager CLI | Avoids SDK reliability issues. State files + tmux is simpler and more debuggable. |
| 2026-03-24 | Blueprint state in separate MongoDB collection | Avoids polluting semantic search and `hive recent` with high-volume execution records. |
| 2026-03-24 | Worktrees for isolation, not advisory locks | The session manager already creates worktrees. Advisory locks add complexity without clear benefit for OS repo access. External repo contention is a known limitation. |
| 2026-03-24 | No TTL on execution records | Execution history is valuable. Archive if volume is an issue, never auto-delete. |
| 2026-03-24 | Hive-native notifications via `hive notify` | Blueprints never reference delivery channels. Wall tiles are the primary surface. Pluggable delivery is future work. |
| 2026-03-24 | Coexistence, not migration | Blueprints and skills work simultaneously. Cutover is deliberate, not gradual. |
| 2026-03-24 | Context assembly is a dedicated LLM step, not runner logic | The runner never calls `hive search`/`hive refs`/`hive recent` itself. Context assembly is an LLM agent task. For single-session blueprints, context instructions are baked into the prompt. |
| 2026-03-24 | `definition_snapshot` stored in execution record | Crash recovery uses the snapshot. Running executions are immune to YAML changes. |
| 2026-03-24 | Global concurrency limit across all blueprints | Default 4 sessions. Prevents hitting API rate limits when multiple blueprints run concurrently. |
| 2026-03-24 | `last_message` excluded as output type | Tmux pane capture is unreliable. Hive records are the primary output mechanism. |
| 2026-03-24 | `waiting_for_human` is a first-class step status | Interactive steps that timeout enter this state, not `failed` or `completed`. |
| 2026-03-24 | Single-session mode for simple blueprints | The majority of blueprints run in one session. Steps become structured instructions. No step-level state tracking. |
| 2026-03-24 | `playbook_path` content prepended, `prompt` appended | When both are set, the session receives playbook first, then the specific prompt. |
| 2026-03-24 | Variable interpolation: missing = error, null = empty, `$${` = escape | No silent failures on missing variables. Null outputs become empty strings. `$${}` escapes literal `${`. |
| 2026-03-24 | `for_each.source` supports YAML native lists | In addition to JSON strings and interpolated variables. Cleaner syntax for static lists. |
| 2026-03-24 | Interactive step 24h timeout marks as `timed_out`, not `completed` | A step where the human never responded should never be marked successful. |
| 2026-03-24 | Three-phase session wait: launch → send → completion | Prevents race conditions between session creation and prompt delivery. |
| 2026-03-24 | Stuck-session detection via `tmux has-session` | Poll loop checks tmux session existence. Catches hung sessions before timeout. |
| 2026-03-24 | `max_cost_usd` is advisory, not enforced | Duration-based cost heuristic is too rough for hard enforcement. Logged as warning. |
| 2026-03-24 | Shortened session naming: `bp-{bp_12}-{step_10}-{exec_8}` | Keeps names under 40 characters for tmux/git friendliness. |
| 2026-03-24 | Circular trigger prevention via `trigger_chain` | Tracks the chain of blueprint triggers. Rejects execution if depth exceeds 5. |
