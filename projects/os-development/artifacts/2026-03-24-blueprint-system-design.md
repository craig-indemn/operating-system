---
ask: "Design the complete Hive Blueprint System — execution engine, definition format, data model, observability, integration, and implementation plan"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-c
sources:
  - type: design
    ref: "projects/os-development/artifacts/2026-03-24-blueprint-system-problem-statement.md"
    name: "Blueprint problem statement"
  - type: research
    ref: "projects/os-development/artifacts/2026-03-24-blueprint-research-synthesis.md"
    name: "Synthesis of 6 parallel research streams"
  - type: design
    ref: "projects/os-development/artifacts/2026-03-08-hive-design.md"
    name: "Hive design document"
  - type: session
    description: "Brainstorm session on Phase 6 agentic OS vision"
    ref: "projects/os-development/artifacts/2026-03-24-hive-phase6-brainstorm.md"
---

# The Hive Blueprint System — Design Document

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
Hive UI (Wall + Focus Area)               <-- Tiles show blueprint executions
    |                                          Click to observe, interact, drill down
    v
Blueprint Runner (Python, asyncio)         <-- The engine: reads YAML, executes steps
    |                                          Persists state to MongoDB per step
    |--- Scheduler (cron + event triggers)     Launches blueprints on schedule/event
    |--- Notification Service (Slack)          Pushes alerts for human-in-the-loop
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
    |--- MongoDB: hive.blueprint_executions Execution state (operational)
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
| **Notifier** | Slack message sender for human-in-the-loop | `systems/hive/notifier.py` |
| **Blueprint CLI** | `hive blueprint` subcommands for management | Integrated into `systems/hive/cli.py` |
| **Execution Records** | Per-execution state in MongoDB | `hive.blueprint_executions` collection |
| **Definition Cache** | Parsed YAML cached in MongoDB for fast listing | `hive.blueprint_defs` collection |

### Key Design Decisions

1. **No Agent SDK.** Sessions are created via the session manager CLI (`session create`) which launches Claude Code in a tmux terminal. The runner monitors execution by watching session state JSON files. This avoids the SDK's reliability issues (monkey-patched message parsers, rate limit event crashes, output format failures).

2. **Blueprint state lives in a separate MongoDB collection** (`blueprint_executions`), not the Hive `records` collection. A daily blueprint produces ~365 execution documents/year. Mixing these with knowledge records would pollute semantic search and dominate `hive recent` feeds.

3. **YAML files are the source of truth** for blueprint definitions, not MongoDB. They are git-tracked, human-readable, and diff-able. MongoDB caches parsed definitions for fast listing and search.

4. **The runner is a single Python asyncio process.** It can execute multiple blueprints concurrently (each blueprint is an asyncio task). Parallel steps within a blueprint use `asyncio.gather()` with configurable concurrency limits.

5. **Playbooks are absorbed as the context-assembly step** of their corresponding blueprints. The morning playbook becomes the `gather-context` step of the `morning-consultation` blueprint. The playbook content is inlined as the step's `prompt` or referenced via `playbook_path`.

---

## 2. Blueprint Definition Format

### Schema

Blueprint definitions are YAML files in `hive/blueprints/`. Each file defines a single blueprint.

```yaml
# Required fields
name: string                    # Unique identifier (kebab-case)
description: string             # Human-readable purpose
version: integer                # Schema version (always 1 for now)

# Classification
domains: [string]               # Hive domains this blueprint operates in
tags: [string]                  # Free-form tags for categorization
system: string                  # Owning system (hive, content, code-dev, etc.)

# Scheduling and triggers (optional)
schedule:
  cron: string                  # Standard cron expression
  timezone: string              # Default: America/Vancouver
triggers:                       # Event-based triggers (optional, list)
  - type: file_change           # Watch for file changes
    path: string                # Glob pattern to watch
  - type: hive_record           # Trigger on Hive record creation/update
    filter:                     # MongoDB-style filter on the record
      type: string
      tags: [string]
  - type: webhook               # HTTP endpoint trigger
    path: string                # URL path suffix: /api/blueprints/trigger/<path>
  - type: manual                # Only runs when explicitly invoked

# Inputs and outputs
inputs:                         # Parameters the blueprint accepts
  param_name:
    type: string                # string, number, boolean, list, record_id
    required: boolean
    default: any
    description: string
outputs:                        # What the blueprint produces (declared, not enforced)
  output_name:
    type: string
    description: string

# Execution configuration
config:
  max_duration_minutes: integer # Kill the execution after this long (default: 480 = 8h)
  max_cost_usd: number          # Budget cap across all session steps (default: 50.0)
  max_concurrent_sessions: int  # Max parallel sessions (default: 3)
  retry_policy:                 # Default retry for all steps
    max_retries: integer        # Default: 2
    backoff_seconds: integer    # Default: 30
  notification:
    on_complete: boolean        # Slack notify on completion (default: false)
    on_failure: boolean         # Slack notify on failure (default: true)
    on_human_needed: boolean    # Slack notify when human input needed (default: true)
    channel: string             # Slack channel (default: #os-notifications)

# Steps
steps: [Step]                   # Ordered list of steps (see Step Types below)
```

### Step Types

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
  playbook_path: string         # Path to a playbook .md file (contents become the prompt)
  context_from: [string]        # Step IDs whose outputs are injected as context
  system_append: string         # Appended to the system prompt

  # Autonomy
  autonomous: boolean           # true = no human interaction expected (default: true)
  interactive: boolean          # true = human joins this session (default: false)

  # Session lifecycle
  timeout_minutes: integer      # Max session duration (default: 60)
  close_on_complete: boolean    # Auto-close session when done (default: true for autonomous)

  # Output
  outputs:
    session_id: session_id      # Always available
    session_output: last_message # Last assistant message from the session
    hive_records: hive_records_created  # Record IDs created during the session
```

**How session monitoring works (without Agent SDK):**

1. Runner calls `session create <name> --model <model> --permissions <perm> [--add-dir ...]`
2. Runner parses the session_id from stdout
3. Runner waits for the session state file to show `status: idle` (Claude ready)
4. Runner calls `session send <name> "<prompt>"` to inject the prompt
5. Runner enters a poll loop watching the session state file:
   - `status: active` — session is working, continue waiting
   - `status: idle` — session finished the prompt, step is done
   - `status: ended` / `status: ended_dirty` — session terminated
   - If `interactive: true`, runner does NOT poll for completion; it waits until the human closes the session or until `timeout_minutes` expires
6. Runner reads the session state file for duration, context usage
7. If `close_on_complete: true` and autonomous, runner calls `session close <name> --non-interactive`

**Cost tracking without Agent SDK:** The session state file does not contain token counts or cost. The runner tracks wall-clock duration per session step. Cost estimation is derived from duration + model tier (rough heuristic: Opus ~$0.06/minute of active processing). Exact cost tracking requires post-hoc analysis via the Anthropic usage dashboard or future session manager enhancements to capture the Claude Code status bar metrics.

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
    feature_spec: "${steps.design.outputs.spec}"
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
    objective: "Analyze Slack channels for signals"
    autonomous: true

  - id: analyze-email
    type: session
    depends_on: [prepare]
    objective: "Analyze email threads for action items"
    autonomous: true

  - id: analyze-linear
    type: session
    depends_on: [prepare]
    objective: "Analyze Linear issues for status"
    autonomous: true

  # This step waits for all three to complete (fan-in)
  - id: consolidate
    type: session
    depends_on: [analyze-slack, analyze-email, analyze-linear]
    objective: "Consolidate analysis from all three sources"
    context_from: [analyze-slack, analyze-email, analyze-linear]
    autonomous: true
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
    source: "${steps.list-prs.outputs.result}"  # JSON array from a previous step
    max_concurrency: 3          # How many to run in parallel (default: 1 = sequential)
  objective: "Review PR #${item.pr.number} in ${item.pr.repo}"
  autonomous: true
  outputs:
    review_results: collected   # Collects outputs from all iterations into a list
```

Each iteration creates its own step record in the execution (suffixed: `review-prs.0`, `review-prs.1`, etc.). The `collected` output type gathers all iteration outputs into a list.

### Conditional Routing

Conditions are Python expressions evaluated in a restricted namespace containing:

- `steps.<step_id>.status` — completed, failed, skipped, timed_out
- `steps.<step_id>.exit_code` — for cli/script steps
- `steps.<step_id>.outputs.<name>` — captured outputs
- `inputs.<param_name>` — blueprint inputs
- `env.<VAR_NAME>` — environment variables

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
  command: "slack-env.sh python3 -c \"from slack_client import post; post('#engineering', 'Tests failed for ${inputs.feature_name}')\""
```

If a condition evaluates to `false`, the step is marked `skipped`. Steps that `depend_on` a skipped step evaluate their own conditions independently — a skipped dependency does not automatically skip dependents unless the condition explicitly checks for it.

### Variable Interpolation

Blueprint definitions support variable interpolation using `${...}` syntax:

- `${inputs.param_name}` — blueprint input parameters
- `${steps.step_id.outputs.output_name}` — output from a previous step
- `${execution.id}` — current execution ID
- `${execution.started_at}` — execution start time
- `${item.variable_name}` — current item in a `for_each` loop
- `${env.VAR_NAME}` — environment variable

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
    debounce_seconds: 30        # Don't fire more than once per 30s

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

**Scheduler implementation:** The scheduler is a long-running Python asyncio process (`blueprint_scheduler.py`). It:
1. Loads all blueprint definitions at startup
2. Creates `asyncio` tasks for cron schedules using the `croniter` library
3. Starts a filesystem watcher (using `watchdog`) for file_change triggers
4. Subscribes to a MongoDB change stream on `hive.records` for hive_record triggers
5. Starts a lightweight HTTP server (aiohttp) for webhook triggers
6. On trigger, calls the runner to start the blueprint execution
7. Reloads definitions when `hive/blueprints/*.yaml` files change

**Cron vs. Claude Code Desktop Tasks:** The scheduler uses its own cron implementation (not Claude Code desktop tasks) because: (a) desktop tasks require the Claude app to be open, (b) they cannot pass structured parameters, (c) they have a minimum 1-hour interval. The scheduler runs as a `launchd` service that auto-starts on boot and survives app restarts.

### Example 1: Morning Consultation (Simple)

```yaml
name: morning-consultation
description: "Daily morning planning — sync systems, gather context, present briefing"
version: 1
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
    channel: "#os-morning"

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
    on_failure: continue          # Don't block the morning if sync partially fails

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
      Write the context note, then exit with /exit.
    timeout_minutes: 15
    outputs:
      context_note: last_message

  - id: interactive-review
    name: "Morning review with Craig"
    type: session
    depends_on: [gather-context]
    interactive: true
    model: opus
    prompt: |
      You are running a morning planning session. Here is the assembled context:

      ${steps.gather-context.outputs.context_note}

      Present the day's landscape. Ask about priorities. Update records as discussed.
    timeout_minutes: 30
    close_on_complete: false       # Craig closes when done

  - id: save-summary
    name: "Save session summary"
    type: cli
    depends_on: [interactive-review]
    command: |
      hive create note "Morning consultation ${inputs.date}" \
        --tags session_summary \
        --domains indemn,career-catalyst,personal \
        --body "Morning consultation completed. See session for details."
    on_failure: continue
```

### Example 2: Feature Lifecycle (Complex, Multi-Phase)

```yaml
name: feature-lifecycle
description: "End-to-end feature development: design, review, plan, implement, test, deploy"
version: 1
domains: [indemn]
tags: [code-dev, feature]
system: code-dev

triggers:
  - type: manual

config:
  max_duration_minutes: 2880      # 48 hours max
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
  # Phase 1: Context Assembly
  - id: assemble-context
    name: "Assemble development context"
    type: session
    autonomous: true
    playbook_path: "systems/hive/playbooks/code-dev.md"
    prompt: |
      Assemble context for workflow: ${inputs.workflow_id}
      Objective: ${inputs.objective}
      Target repo: ${inputs.repo_path}
    timeout_minutes: 10
    outputs:
      context_note: last_message

  # Phase 2: Design (interactive — Craig drives)
  - id: design
    name: "Interactive design session"
    type: session
    depends_on: [assemble-context]
    interactive: true
    model: opus
    add_dirs: ["${inputs.repo_path}"]
    prompt: |
      We're designing: ${inputs.objective}

      Context from the Hive:
      ${steps.assemble-context.outputs.context_note}

      Use /brainstorm-hive to checkpoint decisions. Create 10-20+ decision records.
      When the design is complete, summarize it and exit.
    timeout_minutes: 120
    close_on_complete: false
    outputs:
      design_summary: last_message

  # Phase 3: Design Review (parallel — 3 independent reviews)
  - id: design-review
    name: "Independent design reviews"
    type: session
    depends_on: [design]
    for_each:
      variable: reviewer
      source: '["architecture", "edge-cases", "implementation-feasibility"]'
      max_concurrency: 3
    autonomous: true
    model: opus
    add_dirs: ["${inputs.repo_path}"]
    prompt: |
      You are reviewing a design from the perspective of: ${item.reviewer}

      Design summary:
      ${steps.design.outputs.design_summary}

      Workflow: ${inputs.workflow_id}
      Run: hive refs ${inputs.workflow_id} --tags decision --depth 1

      Write your review findings. Create Hive records for any concerns:
      hive create note "Review finding: [concern]" --tags design,review --refs workflow:${inputs.workflow_id}
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
    prompt: |
      Design reviews are complete. Here are the findings:

      ${steps.design-review.outputs.review_results}

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
      Write the plan as a Hive design record.
    timeout_minutes: 30
    outputs:
      plan: last_message

  # Phase 6: Implementation (sub-blueprint for each task)
  - id: implement
    name: "Execute implementation"
    type: blueprint
    depends_on: [plan]
    blueprint: task-execution
    inputs:
      workflow_id: "${inputs.workflow_id}"
      repo_path: "${inputs.repo_path}"
      plan: "${steps.plan.outputs.plan}"
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
      Report: does the implementation match the design?
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

### Example 3: Market Analysis (Parallel Fan-Out)

```yaml
name: market-analysis
description: "Analyze a market segment — parallel research across multiple dimensions"
version: 1
domains: [indemn]
tags: [research, analysis]
system: hive

triggers:
  - type: manual

config:
  max_duration_minutes: 120
  max_cost_usd: 20.0
  max_concurrent_sessions: 5
  notification:
    on_complete: true

inputs:
  segment:
    type: string
    required: true
    description: "Market segment to analyze (e.g., 'P&C insurance brokers')"
  depth:
    type: string
    required: false
    default: "standard"
    description: "Analysis depth: quick, standard, deep"

steps:
  - id: existing-knowledge
    name: "Check existing Hive knowledge"
    type: cli
    command: "hive search '${inputs.segment}' --recent 90d --limit 20 --format json"
    outputs:
      existing: json_stdout

  # Five parallel research streams (fan-out)
  - id: competitors
    name: "Competitor analysis"
    type: session
    depends_on: [existing-knowledge]
    autonomous: true
    prompt: |
      Research competitors in the ${inputs.segment} segment.
      Existing knowledge: ${steps.existing-knowledge.outputs.existing}
      Use web search and available tools. Create a Hive research record with findings.
    timeout_minutes: 20

  - id: customer-signals
    name: "Customer signal analysis"
    type: session
    depends_on: [existing-knowledge]
    autonomous: true
    prompt: |
      Analyze customer signals for ${inputs.segment}.
      Search Hive for meeting notes, quotes, and signals related to this segment.
      Run: hive search "${inputs.segment}" --tags meeting --recent 180d
      Create a Hive research record with findings.
    timeout_minutes: 20

  - id: market-size
    name: "Market sizing"
    type: session
    depends_on: [existing-knowledge]
    autonomous: true
    prompt: |
      Estimate market size and growth for ${inputs.segment}.
      Use web search for industry reports, analyst estimates.
      Create a Hive research record with findings.
    timeout_minutes: 20

  - id: product-gaps
    name: "Product gap analysis"
    type: session
    depends_on: [existing-knowledge]
    autonomous: true
    prompt: |
      Analyze product gaps for serving ${inputs.segment}.
      Check current product capabilities: hive list product --domains indemn
      Check feature requests: hive search "${inputs.segment} feature" --recent 180d
      Create a Hive research record with findings.
    timeout_minutes: 20

  - id: channel-strategy
    name: "Go-to-market channel analysis"
    type: session
    depends_on: [existing-knowledge]
    autonomous: true
    prompt: |
      Analyze go-to-market channels for ${inputs.segment}.
      What channels work for reaching this segment? Cost estimates?
      Create a Hive research record with findings.
    timeout_minutes: 20

  # Fan-in: consolidate all research
  - id: consolidate
    name: "Consolidate analysis"
    type: session
    depends_on: [competitors, customer-signals, market-size, product-gaps, channel-strategy]
    autonomous: true
    model: opus
    prompt: |
      Consolidate the market analysis for: ${inputs.segment}

      Research from 5 parallel streams is now in the Hive.
      Run: hive search "${inputs.segment}" --tags research --recent 1d

      Write a comprehensive market analysis as a Hive design record:
      hive create design "Market Analysis: ${inputs.segment}" \
        --domains indemn \
        --tags research,market-analysis \
        --body "<comprehensive analysis>"

      Include: executive summary, market size, competitive landscape,
      customer signals, product gaps, GTM recommendation, risks.
    timeout_minutes: 30
    outputs:
      analysis: last_message

  - id: notify
    name: "Notify completion"
    type: cli
    depends_on: [consolidate]
    command: |
      slack-env.sh python3 -c "
      from slack_client import post
      post('#research', 'Market analysis complete for: ${inputs.segment}. Check the Hive.')
      "
```

---

## 3. Execution Engine

### The Runner — Main Loop

The Blueprint Runner is an async Python application. Its core is a state machine that processes one execution at a time, advancing through steps according to the dependency DAG.

```python
# Pseudocode for the main execution loop
async def execute_blueprint(blueprint: BlueprintDef, inputs: dict, parent_execution_id: str = None):
    # 1. Create execution record in MongoDB
    execution = create_execution_record(blueprint, inputs, parent_execution_id)

    # 2. Build dependency DAG from steps
    dag = build_dag(blueprint.steps)

    # 3. Main loop: find eligible steps and execute them
    while not execution_complete(execution):
        eligible = find_eligible_steps(dag, execution)

        if not eligible:
            if has_running_steps(execution):
                await wait_for_any_step_completion(execution)
                continue
            else:
                # Deadlock or all remaining steps skipped
                break

        # Launch eligible steps (up to concurrency limit)
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

    # 4. Finalize
    execution.status = compute_final_status(execution)
    execution.ended_at = now()
    persist_execution_state(execution)

    # 5. Create Hive knowledge record summarizing the execution
    create_execution_summary_record(execution)

    # 6. Send notifications
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

#### Session Steps (Without Agent SDK)

This is the most complex executor. It uses the session manager CLI to create tmux sessions and monitors the session state JSON files for completion.

```python
SESSION_CLI = "/Users/home/Repositories/.venv/bin/python3 systems/session-manager/cli.py"
SESSIONS_DIR = "/Users/home/Repositories/operating-system/sessions"

async def execute_session_step(step_def, execution):
    session_name = f"bp-{execution.blueprint}-{step_def.id}-{execution.id[:8]}"

    # 1. Build the session create command
    cmd_parts = [SESSION_CLI, "create", session_name,
                 "--model", step_def.model or "opus",
                 "--permissions", step_def.permissions or "bypassPermissions"]

    if not step_def.worktree:
        cmd_parts.append("--no-worktree")
    for d in (step_def.add_dirs or []):
        cmd_parts.extend(["--add-dir", interpolate(d, execution)])

    # 2. Create the session
    proc = await asyncio.create_subprocess_exec(
        *cmd_parts,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=_clean_env(),  # Removes CLAUDECODE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return StepResult(status="failed", error=f"Session create failed: {stderr.decode()}")

    # Parse session_id from output
    session_id = _parse_session_id(stdout.decode())

    # 3. Wait for Claude Code to be ready (status: idle)
    state = await _wait_for_session_status(session_id, ["idle", "active"], timeout=60)
    if state is None:
        return StepResult(status="failed", error="Session never became ready")

    # 4. Build and send the prompt
    prompt = _build_prompt(step_def, execution)
    send_proc = await asyncio.create_subprocess_exec(
        *[SESSION_CLI, "send", session_name, prompt],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await send_proc.communicate()

    # 5. Monitor session state file
    if step_def.interactive:
        # For interactive steps: wait until human closes the session
        # or timeout expires. Do NOT auto-close.
        state = await _wait_for_session_status(
            session_id,
            ["ended", "ended_dirty"],
            timeout=step_def.timeout_minutes * 60,
            poll_interval=5,
        )
        if state is None:
            # Timed out waiting for human — notify and continue waiting
            await notify_human_needed(execution, step_def)
            state = await _wait_for_session_status(
                session_id,
                ["ended", "ended_dirty"],
                timeout=86400,  # Wait up to 24h for human
                poll_interval=30,
            )
    else:
        # For autonomous steps: wait for idle (prompt processed)
        # then close the session
        state = await _wait_for_session_status(
            session_id,
            ["idle"],
            timeout=step_def.timeout_minutes * 60,
            not_statuses=["ended", "ended_dirty"],
            poll_interval=3,
        )

        if state and state.get("status") == "idle":
            # Session processed the prompt, now close it
            if step_def.close_on_complete:
                close_proc = await asyncio.create_subprocess_exec(
                    *[SESSION_CLI, "close", session_name, "--non-interactive"],
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await close_proc.communicate()

    # 6. Read final state and extract outputs
    final_state = _read_session_state(session_id)
    duration = _compute_duration(final_state)

    return StepResult(
        status="completed",
        session_id=session_id,
        session_name=session_name,
        duration_s=duration,
        outputs=_extract_session_outputs(final_state, step_def),
    )


async def _wait_for_session_status(session_id, target_statuses, timeout, poll_interval=3, not_statuses=None):
    """Poll the session state file until the session reaches one of the target statuses."""
    state_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    deadline = time.time() + timeout

    while time.time() < deadline:
        state = read_state_file(state_path)
        if state:
            current_status = state.get("status")
            if current_status in target_statuses:
                return state
            if not_statuses and current_status in not_statuses:
                return state  # Unexpected terminal state
        await asyncio.sleep(poll_interval)

    return None  # Timed out
```

**Extracting session output (`last_message`):** The session state file does not contain the conversation transcript. To capture the last assistant message, the runner uses a convention: the session's prompt instructs it to write its final output to a known file path (e.g., `hive create note ...` which creates a knowledge record) or to a temporary output file. The runner then reads that file. For the `last_message` output type, the runner reads the session's tmux pane buffer:

```python
async def _capture_tmux_output(tmux_name, lines=200):
    """Capture the last N lines from the tmux pane buffer."""
    proc = await asyncio.create_subprocess_exec(
        "tmux", "capture-pane", "-t", tmux_name, "-p", "-S", f"-{lines}",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode()
```

This is imperfect — tmux pane buffers mix assistant output with tool calls and system messages. For production use, prompts should instruct sessions to write structured output to a known location (Hive record, file). The tmux capture is the fallback.

**Recommended output capture pattern:** Instead of relying on `last_message`, session steps should create Hive knowledge records as their output. The runner can then query `hive search --recent 5m --refs-to <workflow-id> --format json` to find records created during the step. This aligns with the self-compressing principle — the output IS the knowledge record.

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
    if isinstance(source_data, str):
        source_data = json.loads(source_data)

    sub_steps = []
    for i, item in enumerate(source_data):
        sub_step = copy.deepcopy(step_def)
        sub_step.id = f"{step_def.id}.{i}"
        sub_step.for_each = None  # Clear to prevent re-expansion
        sub_step._item = {step_def.for_each.variable: item}  # Available as ${item.var}
        sub_steps.append(sub_step)

    return sub_steps
```

Concurrency for `for_each` is controlled by `max_concurrency`. The runner uses `asyncio.Semaphore`:

```python
sem = asyncio.Semaphore(step_def.for_each.max_concurrency)

async def run_with_semaphore(sub_step):
    async with sem:
        return await execute_step(sub_step, execution)

results = await asyncio.gather(*[run_with_semaphore(s) for s in sub_steps])
```

#### Sub-Blueprint Execution

Sub-blueprints are recursive calls to the same runner function:

```python
async def execute_blueprint_step(step_def, execution):
    # Load the sub-blueprint definition
    sub_blueprint = load_blueprint(step_def.blueprint)
    sub_inputs = {k: interpolate(v, execution) for k, v in step_def.inputs.items()}

    # Execute recursively with parent link
    sub_execution = await execute_blueprint(
        sub_blueprint,
        sub_inputs,
        parent_execution_id=execution.execution_id,
    )

    return StepResult(
        status="completed" if sub_execution.status == "completed" else "failed",
        sub_execution_id=sub_execution.execution_id,
        sub_status=sub_execution.status,
    )
```

**Depth guard:** The runner tracks recursion depth. If depth exceeds 5, the step fails with an error. This prevents infinite loops from circular sub-blueprint references.

#### Conditional Routing Evaluation

Conditions are evaluated using Python's `eval()` in a restricted namespace:

```python
def evaluate_condition(condition_str, execution):
    """Evaluate a condition expression against execution state."""
    if not condition_str:
        return True  # No condition = always execute

    namespace = {
        "steps": _build_steps_namespace(execution),
        "inputs": execution.inputs,
        "env": dict(os.environ),
        "true": True,
        "false": False,
        "True": True,
        "False": False,
    }

    try:
        return bool(eval(condition_str, {"__builtins__": {}}, namespace))
    except Exception as e:
        # Condition evaluation failure — log and treat as false
        log.warning(f"Condition eval failed for '{condition_str}': {e}")
        return False
```

The `_build_steps_namespace` creates an object where `steps.step_id.status`, `steps.step_id.exit_code`, `steps.step_id.outputs.name` are all accessible via attribute access (using `types.SimpleNamespace`).

### State Persistence to MongoDB

The execution record is written to MongoDB at these points:

1. **Execution created** — initial record with status `running`
2. **Step started** — step status changes to `running`
3. **Step completed/failed/skipped** — step status updated with results
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

1. On startup, the runner queries MongoDB for executions with `status: running`
2. For each found execution:
   a. Steps with `status: completed` are skipped (never re-executed)
   b. Steps with `status: running` are treated as failed (the session that was running them is likely dead)
   c. Steps with `status: pending` proceed normally
3. The runner resumes the main loop from where it left off

```python
async def recover_executions():
    """Find and resume any in-flight executions after a crash."""
    collection = get_collection("blueprint_executions")
    in_flight = collection.find({"status": "running"})

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

        # Resume execution
        blueprint = load_blueprint(exec_doc["blueprint"])
        asyncio.create_task(resume_execution(blueprint, exec_doc))
```

A `crashed` step is treated like a failed step — the retry policy applies. If retries remain, the step re-executes. If exhausted, the step is marked `failed` and `on_failure` determines whether the execution continues.

### Resource Contention Handling

**Problem:** Two blueprints targeting the same repo would corrupt each other's git staging. Two sessions creating Hive records simultaneously could collide on slugs.

**Solution: Advisory Locks in MongoDB**

The runner maintains an advisory lock collection (`hive.blueprint_locks`):

```python
async def acquire_lock(resource: str, execution_id: str, timeout: int = 300) -> bool:
    """Try to acquire an advisory lock on a resource."""
    collection = get_collection("blueprint_locks")
    try:
        collection.insert_one({
            "resource": resource,       # e.g., "repo:/Users/home/Repositories/bot-service"
            "execution_id": execution_id,
            "acquired_at": now_iso(),
            "expires_at": datetime.utcnow() + timedelta(seconds=timeout),
        })
        return True
    except DuplicateKeyError:
        # Check if the existing lock has expired
        existing = collection.find_one({"resource": resource})
        if existing and existing["expires_at"] < datetime.utcnow():
            collection.delete_one({"resource": resource})
            return await acquire_lock(resource, execution_id, timeout)
        return False

async def release_lock(resource: str, execution_id: str):
    collection = get_collection("blueprint_locks")
    collection.delete_one({"resource": resource, "execution_id": execution_id})
```

**Lock scope:**
- Session steps that specify `add_dirs` acquire a lock on each directory
- CLI steps that modify files acquire a lock on the working directory
- Locks auto-expire (default 5 minutes) to prevent deadlocks from crashed processes
- The runner renews locks while a step is actively running

**Hive CLI slug collisions** are handled by the Hive CLI itself (it already appends `-2`, `-3` for duplicate slugs on the same day).

---

## 4. Observability

### Execution Record Data Model

Every blueprint execution creates a document in `hive.blueprint_executions`:

```json
{
  "execution_id": "morning-consultation-2026-03-24-07-00",
  "blueprint": "morning-consultation",
  "blueprint_version": 1,
  "status": "completed",
  "parent_execution_id": null,
  "trigger": "schedule",
  "inputs": {"date": "2026-03-24"},

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
      "session_name": "bp-morning-consultation-gather-context-abcd1234",
      "cost_estimate_usd": 0.45,
      "retry_count": 0,
      "outputs": {
        "context_note": "# Morning Consultation — 2026-03-24\n\n..."
      },
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
      "session_name": "bp-morning-consultation-review-abcd1234",
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

### Token Usage and Cost Tracking

Without the Agent SDK, exact token counts and costs are not available from the session. The runner tracks what it can:

| Metric | Source | Accuracy |
|--------|--------|----------|
| Wall-clock duration per step | Runner timestamps | Exact |
| CLI step exit codes | subprocess return code | Exact |
| Session step duration | Session state file timestamps | Exact |
| Context remaining % | Session state file (`context_remaining_pct`) | Exact (reported by hooks) |
| Cost estimate | Duration-based heuristic: Opus ~$0.06/min, Sonnet ~$0.02/min | Rough estimate |
| Records created | Query `hive recent 5m` after step completes | Best-effort |

**Future enhancement:** If the session manager is extended to capture Claude Code's status bar metrics (token counts, cost), the runner can read those from the session state file for exact figures. This is a session manager enhancement, not a blueprint system change.

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

# Validate a blueprint YAML without running it
hive blueprint validate <path-to-yaml>
hive blueprint validate hive/blueprints/morning-consultation.yaml

# Reload all blueprint definitions (after editing YAML files)
hive blueprint reload
```

**Output format follows the Hive convention:** JSON when piped, text when interactive.

Example output of `hive blueprint status`:

```
Blueprint: morning-consultation
Execution: morning-consultation-2026-03-24-07-00
Status: running
Started: 2026-03-24 07:00:00 (12m ago)
Trigger: schedule

Steps:
  [completed] sync                  45s     exit:0
  [completed] gather-context        7m 27s  session:abc-123
  [running]   interactive-review    4m 12s  session:ghi-456  (interactive)
  [pending]   save-summary          -       -

Cost estimate: $2.06
Records created: 2026-03-24-morning-context
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
| Step progress | Progress indicator (e.g., "3/5 steps") |
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

### Notification System

The notifier uses the existing Slack skill infrastructure (`slack-env.sh` + `slack_client.py`):

```python
# systems/hive/notifier.py

import subprocess
import json

def notify_slack(channel: str, message: str, blocks: list = None):
    """Send a Slack notification."""
    if blocks:
        payload = json.dumps({"channel": channel, "blocks": blocks})
        cmd = f'slack-env.sh python3 -c "from slack_client import post_blocks; post_blocks(\'{channel}\', {repr(payload)})"'
    else:
        cmd = f'slack-env.sh python3 -c "from slack_client import post; post(\'{channel}\', {repr(message)})"'

    subprocess.run(cmd, shell=True, timeout=30)


async def send_notifications(execution, notification_config):
    """Send notifications based on execution result and config."""
    if execution.status == "completed" and notification_config.on_complete:
        notify_slack(
            notification_config.channel,
            f"Blueprint *{execution.blueprint}* completed in {format_duration(execution.duration_s)}. "
            f"Cost: ~${execution.cost_estimate_usd:.2f}. "
            f"Records created: {len(execution.hive_records_created)}"
        )
    elif execution.status == "failed" and notification_config.on_failure:
        failed_step = next((s for s in execution.steps if s.status == "failed"), None)
        notify_slack(
            notification_config.channel,
            f"Blueprint *{execution.blueprint}* failed at step *{failed_step.name if failed_step else '?'}*. "
            f"Error: {failed_step.error if failed_step else 'unknown'}. "
            f"Resume: `hive blueprint resume {execution.execution_id}`"
        )


async def notify_human_needed(execution, step_def):
    """Notify Craig that a step needs human interaction."""
    notify_slack(
        execution.notification_channel or "#os-notifications",
        f"Blueprint *{execution.blueprint}* needs you at step *{step_def.name}*. "
        f"Attach: `session attach {step_def._session_name}`"
    )
```

---

## 5. Hive Integration

### New CLI Commands

All blueprint operations are under the `hive blueprint` subcommand:

| Command | Purpose |
|---------|---------|
| `hive blueprint list` | List all defined blueprints |
| `hive blueprint show <name>` | Show blueprint definition |
| `hive blueprint run <name>` | Start a blueprint execution |
| `hive blueprint executions` | List execution records |
| `hive blueprint status <id>` | Show real-time execution status |
| `hive blueprint cancel <id>` | Cancel a running execution |
| `hive blueprint resume <id>` | Resume from last completed step |
| `hive blueprint history <name>` | Execution history for a blueprint |
| `hive blueprint validate <path>` | Validate YAML syntax and references |
| `hive blueprint reload` | Re-parse all YAML definitions |

These are implemented as a new subparser group in `systems/hive/cli.py`, delegating to functions in a new `systems/hive/blueprint_cli.py` module.

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

### Context Assembly as a Blueprint Step

The existing playbooks (`morning.md`, `code-dev.md`, `content.md`, `ceo-weekly.md`) are absorbed as the first step of their corresponding blueprints. The playbook file itself remains — it's referenced by the `playbook_path` field on a session step. No content changes needed.

The pattern:

```yaml
steps:
  - id: assemble-context
    type: session
    autonomous: true
    playbook_path: "systems/hive/playbooks/code-dev.md"
    prompt: "Assemble context for workflow: ${inputs.workflow_id}"
    timeout_minutes: 15
```

The session step creates a Claude Code session, sends the playbook content as the prompt, and the session follows the playbook instructions (which include Hive CLI commands for context gathering). The session writes the context note to the Hive and exits. The next step receives the context note as input.

**This replaces the separate context assembly session mechanism** defined in the Hive design doc's "Session Initialization" section. Instead of the Hive UI spawning a context assembly session, it spawns a blueprint execution where the first step IS the context assembly. The working session is the second step. Same behavior, but now tracked, observable, and resumable.

### Execution Artifacts Feed the Knowledge Graph (Self-Compressing)

When a blueprint execution completes, the runner creates a Hive knowledge record:

```python
def create_execution_summary_record(execution):
    """Create a Hive knowledge record summarizing the execution."""
    # Build a rich summary from execution data
    step_summaries = []
    for step in execution.steps:
        status_icon = {"completed": "PASS", "failed": "FAIL", "skipped": "SKIP"}.get(step.status, "?")
        step_summaries.append(
            f"- [{status_icon}] {step.name} ({format_duration(step.duration_s)})"
        )

    body = f"""Blueprint: {execution.blueprint}
Trigger: {execution.trigger}
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

This means future context assembly sessions know not just what work has been done (from regular knowledge records), but how it was done (from execution summaries). The system learns its own patterns.

### What Happens to Existing Components

| Component | Current State | After Blueprints |
|-----------|-------------|-----------------|
| **Playbooks** (`systems/hive/playbooks/`) | 4 markdown files defining context assembly instructions | Preserved as-is. Referenced by blueprint session steps via `playbook_path`. No migration needed. |
| **Dispatch engine** (`systems/dispatch/engine.py`) | Ralph loop using Agent SDK | Deprecated. Replaced by `task-execution` blueprint (which uses session manager instead of Agent SDK). Migration: convert existing epics to blueprint definitions. |
| **Dispatch skill** (`.claude/skills/dispatch/SKILL.md`) | Skill that invokes the dispatch engine | Rewritten to invoke `hive blueprint run` instead. |
| **Code-dev skill** (`.claude/skills/code-dev/SKILL.md`) | Guides design/review/plan/execute/test phases | Preserved. Blueprints encode the workflow; the skill provides interactive guidance within individual sessions. They're complementary. |
| **Brainstorm-hive skill** (`.claude/skills/brainstorm-hive/SKILL.md`) | Checkpoints decisions during brainstorming | Preserved. Used within interactive blueprint steps. |
| **Session manager** (`systems/session-manager/cli.py`) | Creates/manages Claude Code sessions in tmux | Preserved as-is. The blueprint runner is a consumer of the session manager. |
| **Context assembly** (Hive design's "dedicated context assembly session") | A short-lived session that gathers context and writes a note | Becomes the first step of a blueprint. Same mechanism, now tracked and observable. |

### Wall UI Changes

The Wall data pipeline adds a third source:

| Source | What It Provides | Update Frequency |
|--------|-----------------|-----------------|
| `sessions/*.json` | Active session tiles | Real-time (hooks) |
| Hive API (MongoDB `records`) | Entity and knowledge tiles | 30s polling |
| **Blueprint API (MongoDB `blueprint_executions`)** | **Running/recent execution tiles** | **5s polling for running, 30s for completed** |

The Express backend (`systems/os-terminal/`) gains new routes:

```
GET /api/blueprints/definitions     List all blueprint definitions
GET /api/blueprints/executions      List executions (filterable by status, blueprint, recent)
GET /api/blueprints/executions/:id  Get single execution with step details
POST /api/blueprints/run            Start a blueprint execution
POST /api/blueprints/cancel/:id     Cancel a running execution
POST /api/blueprints/resume/:id     Resume a failed execution
```

---

## 6. Data Model

### Blueprint Definitions (YAML Files + MongoDB Cache)

**Source of truth:** `hive/blueprints/*.yaml` (git-tracked)

**MongoDB cache:** `hive.blueprint_defs` collection. Parsed from YAML on `hive blueprint reload` or when files change. Used for fast listing and search.

```json
// hive.blueprint_defs document
{
  "name": "morning-consultation",
  "description": "Daily morning planning — sync systems, gather context, present briefing",
  "version": 1,
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
  "yaml_hash": "sha256:abc123..."  // For change detection
}
```

**Indexes on `blueprint_defs`:**
- `name`: unique
- `tags`: multikey
- `system`: regular
- `schedule.cron`: regular (for scheduler to find scheduled blueprints)

### Execution Records

**Collection:** `hive.blueprint_executions`

Full schema (as shown in Section 4's data model example). Key fields:

```json
{
  "execution_id": "string",           // Unique: {blueprint}-{ISO timestamp} or UUID
  "blueprint": "string",              // References blueprint_defs.name
  "blueprint_version": "integer",
  "status": "string",                 // pending, running, completed, failed, cancelled, timed_out
  "parent_execution_id": "string?",   // For sub-blueprints
  "trigger": "string",                // schedule, manual, file_change, hive_record, webhook
  "inputs": "object",                 // Input parameters

  "started_at": "datetime",
  "ended_at": "datetime?",
  "duration_s": "number?",
  "cost_estimate_usd": "number?",

  "steps": [                          // Array of step records
    {
      "id": "string",
      "name": "string",
      "type": "string",               // cli, session, script, blueprint
      "status": "string",             // pending, running, completed, failed, skipped, timed_out, crashed
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

### Advisory Locks

**Collection:** `hive.blueprint_locks`

```json
{
  "resource": "string",              // Unique — the locked resource identifier
  "execution_id": "string",
  "step_id": "string",
  "acquired_at": "datetime",
  "expires_at": "datetime"           // Auto-expire for crash safety
}
```

**Indexes:**
- `resource`: unique
- `expires_at`: TTL index (MongoDB auto-deletes expired locks)

### Retention Policy

| Collection | Retention | Mechanism |
|------------|----------|-----------|
| `blueprint_defs` | Indefinite (mirrors YAML files) | Pruned on `hive blueprint reload` if YAML deleted |
| `blueprint_executions` | 90 days for step-level detail; summary record in Hive is permanent | TTL index on `ended_at` (90 days) for completed executions. Running executions never expire. |
| `blueprint_locks` | Auto-expire via TTL | TTL index on `expires_at` |

The 90-day TTL on executions means the operational detail (every step's stdout, timing, etc.) is temporary. The Hive knowledge summary record (tagged `execution_summary`) is permanent and searchable. This gives you the best of both worlds: detailed debugging data for recent executions, and long-term institutional memory via the Hive.

### Relationship to Hive Records

```
blueprint_defs (MongoDB)     <-- Cached from hive/blueprints/*.yaml
        |
        | 1:many
        v
blueprint_executions (MongoDB)  <-- Operational state, 90-day TTL
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

## 7. Implementation Plan

### Phase 1: Core Runner + CLI (Week 1-2)

**Goal:** The runner can execute a simple sequential blueprint with CLI and session steps. The CLI can list, show, run, and check status.

**Build order:**

1. **Blueprint definition schema** — Define the YAML schema, create a Python dataclass/Pydantic model to parse it. Write a validator.
   - File: `systems/hive/blueprint_schema.py`

2. **MongoDB collections** — Create `blueprint_defs`, `blueprint_executions`, `blueprint_locks` collections with indexes.
   - File: `systems/hive/blueprint_db.py`

3. **CLI executor** — `subprocess`-based CLI step execution with timeout, output capture.
   - File: `systems/hive/executors/cli_executor.py`

4. **Session executor** — Session manager integration: create session, send prompt, poll state file, close session.
   - File: `systems/hive/executors/session_executor.py`

5. **Script executor** — subprocess-based script execution.
   - File: `systems/hive/executors/script_executor.py`

6. **Blueprint runner** — Main execution loop with sequential step processing, state persistence, crash recovery.
   - File: `systems/hive/blueprint_runner.py`

7. **Blueprint CLI commands** — `hive blueprint list|show|run|executions|status|validate|reload` added to `systems/hive/cli.py`.
   - File: `systems/hive/blueprint_cli.py`

8. **First blueprint: morning-consultation** — Convert the morning playbook to a YAML blueprint (as shown in Example 1).
   - File: `hive/blueprints/morning-consultation.yaml`

9. **Second blueprint: weekly-summary** — A simpler variant to validate the pattern.
   - File: `hive/blueprints/weekly-summary.yaml`

10. **Third blueprint: hive-sync** — Trivial single-step CLI blueprint for testing scheduling later.
    - File: `hive/blueprints/hive-sync.yaml`

**Exit criteria:** `hive blueprint run morning-consultation` executes all 4 steps. Execution record appears in MongoDB. `hive blueprint status` shows real-time progress. Crash recovery works (kill runner, restart, it resumes).

### Phase 2: Parallel + Conditional + Sub-Blueprints (Week 2-3)

**Goal:** The runner handles the full step graph: dependency DAG, parallel fan-out, conditional routing, for_each loops, and sub-blueprint invocation.

**Build order:**

1. **DAG resolver** — Build dependency graph from step definitions, find eligible steps, detect cycles.
   - Add to: `systems/hive/blueprint_runner.py`

2. **Parallel execution** — `asyncio.gather` with semaphore-based concurrency limits.
   - Add to: `systems/hive/blueprint_runner.py`

3. **Condition evaluator** — Restricted `eval()` with namespace construction from execution state.
   - File: `systems/hive/blueprint_conditions.py`

4. **Variable interpolation** — `${...}` syntax resolution at step execution time.
   - File: `systems/hive/blueprint_interpolation.py`

5. **for_each expansion** — Expand loop steps into sub-steps, handle collected outputs.
   - Add to: `systems/hive/blueprint_runner.py`

6. **Blueprint executor** — Recursive sub-blueprint invocation with depth guard and parent linking.
   - File: `systems/hive/executors/blueprint_executor.py`

7. **Advisory locks** — MongoDB-based resource locking with TTL.
   - File: `systems/hive/blueprint_locks.py`

8. **Market-analysis blueprint** — Validates parallel fan-out (Example 3).
   - File: `hive/blueprints/market-analysis.yaml`

9. **task-execution blueprint** — Replaces dispatch: sequential task execution with verification. Sub-blueprint used by feature-lifecycle.
   - File: `hive/blueprints/task-execution.yaml`

**Exit criteria:** Market analysis blueprint runs 5 parallel sessions and consolidates. Feature lifecycle blueprint runs with sub-blueprint invocation. Conditional steps skip correctly. for_each loops iterate.

### Phase 3: Scheduler + Triggers + Notifications (Week 3-4)

**Goal:** Blueprints run on schedule, react to events, and notify Craig when human input is needed.

**Build order:**

1. **Notifier** — Slack notification via `slack-env.sh`.
   - File: `systems/hive/notifier.py`

2. **Notification integration** — Wire notifications into the runner (on_complete, on_failure, on_human_needed).
   - Add to: `systems/hive/blueprint_runner.py`

3. **Cron scheduler** — `croniter`-based schedule evaluation, runs as persistent process.
   - File: `systems/hive/blueprint_scheduler.py`

4. **File change trigger** — `watchdog`-based filesystem monitoring with debounce.
   - Add to: `systems/hive/blueprint_scheduler.py`

5. **Hive record trigger** — MongoDB change stream subscription on `hive.records`.
   - Add to: `systems/hive/blueprint_scheduler.py`

6. **Webhook trigger** — Lightweight aiohttp server for HTTP triggers.
   - Add to: `systems/hive/blueprint_scheduler.py`

7. **launchd service** — Auto-start scheduler on boot.
   - File: `systems/hive/com.indemn.hive-scheduler.plist`

8. **Schedule morning-consultation** — Enable the cron schedule and verify it fires at 7am.

9. **Execution summary records** — Auto-create Hive knowledge record on execution completion.
   - Add to: `systems/hive/blueprint_runner.py`

10. **Retention policy** — TTL index on `blueprint_executions` for 90-day cleanup.

**Exit criteria:** Morning consultation runs automatically at 7am. Craig gets a Slack notification when the interactive step is ready. Failed blueprints notify on `#os-notifications`. Execution summaries appear as Hive knowledge records.

### Phase 4: Wall UI Integration (Week 4-5)

**Goal:** Blueprint executions are visible on the Hive Wall as tiles. Real-time step progress. Drill-down to execution details.

**Build order:**

1. **Express API routes** — Blueprint definition listing, execution CRUD, running execution poll.
   - File: `systems/os-terminal/routes/blueprints.js`

2. **Blueprint execution tile component** — React component with step progress, status colors.
   - File: `systems/os-terminal/src/components/BlueprintTile.tsx`

3. **Execution detail view** — Focus area panel showing step-by-step execution state.
   - File: `systems/os-terminal/src/components/BlueprintDetail.tsx`

4. **Wall data merger** — Add blueprint execution tiles to the Wall alongside Hive record tiles and session tiles.
   - Modify: Wall data fetching logic

5. **Run/cancel/resume from UI** — Action buttons on blueprint tiles.

**Exit criteria:** Running blueprints appear as tiles on the Wall with real-time step progress. Completed/failed executions are visible with drill-down. Actions (run, cancel, resume) work from the UI.

### Phase 5: Dispatch Migration + System Integration (Week 5-6)

**Goal:** Dispatch is fully replaced. Code-dev and content systems use blueprints. The dispatch skill points to the blueprint system.

**Build order:**

1. **task-execution blueprint** — Full replacement for the dispatch ralph loop. Uses session manager for execution, separate sessions for verification.
   - File: `hive/blueprints/task-execution.yaml`

2. **Rewrite dispatch skill** — Points to `hive blueprint run task-execution` instead of `engine.py`.
   - File: `.claude/skills/dispatch/SKILL.md`

3. **feature-lifecycle blueprint** — End-to-end feature development (Example 2).
   - File: `hive/blueprints/feature-lifecycle.yaml`

4. **content-pipeline blueprint** — Content creation workflow (idea -> extraction -> draft -> review -> publish).
   - File: `hive/blueprints/content-pipeline.yaml`

5. **Deprecate `systems/dispatch/engine.py`** — Mark as deprecated, point to blueprints.

6. **Blueprint skill** — New `.claude/skills/blueprint/SKILL.md` documenting how to create and use blueprints.

**Exit criteria:** All dispatch use cases run via blueprints. The dispatch engine is deprecated. Feature lifecycle and content pipeline blueprints work end-to-end.

### The First 3 Blueprints (Full YAML)

These are built in Phase 1. Morning consultation is shown in Example 1 above. Here are the other two:

#### Blueprint: `weekly-summary`

```yaml
name: weekly-summary
description: "Weekly intelligence rollup — decisions, progress, signals, action items"
version: 1
domains: [indemn, career-catalyst, personal]
tags: [weekly, planning, summary]
system: hive

schedule:
  cron: "0 9 * * 5"              # Friday 9am
  timezone: "America/Vancouver"

config:
  max_duration_minutes: 30
  max_cost_usd: 5.0
  notification:
    on_complete: true
    channel: "#os-weekly"

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
        --tags session_summary \
        --domains indemn,career-catalyst,personal \
        --body "<the compiled summary>"
    timeout_minutes: 15

  - id: notify
    name: "Send to Slack"
    type: cli
    depends_on: [compile-summary]
    command: |
      slack-env.sh python3 -c "
      from slack_client import post
      post('#os-weekly', 'Weekly summary is ready in the Hive. Check the latest session_summary record.')
      "
    on_failure: continue
```

#### Blueprint: `hive-sync`

```yaml
name: hive-sync
description: "Sync all external systems into the Hive — knowledge files, Linear, Calendar, Slack, GitHub"
version: 1
domains: [indemn, career-catalyst, personal]
tags: [sync, maintenance]
system: hive

schedule:
  cron: "*/30 6-23 * * *"        # Every 30 minutes during waking hours
  timezone: "America/Vancouver"

config:
  max_duration_minutes: 10
  max_cost_usd: 0                # No LLM cost — all CLI
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
    depends_on: []               # Parallel with sync-knowledge
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

---

## Open Questions

These are genuinely uncertain areas where the recommended resolution is provided but may change during implementation.

### 1. Session Output Capture Reliability

**Question:** The `last_message` output type relies on tmux pane buffer capture, which mixes tool calls with assistant output. Is this reliable enough for production?

**Recommended resolution:** For v1, instruct session prompts to write structured output to Hive records (the self-compressing pattern). Use `hive_records_created` as the primary output mechanism, not `last_message`. The tmux capture is the fallback for quick-and-dirty pipelines. If exact output capture becomes critical, enhance the session manager to write the last assistant message to a sidecar file (a minor change to the session close hook).

### 2. Scheduler Process Management

**Question:** The scheduler is a long-running Python process. How do we ensure it stays running? launchd? Supervisor?

**Recommended resolution:** Use `launchd` (macOS native). Create a `.plist` file that auto-starts the scheduler on boot and restarts it on crash. This is the standard macOS approach for persistent daemons. The scheduler itself logs to `~/.logs/hive-scheduler.log` using the same convention as other OS services.

### 3. Execution ID Format

**Question:** Should execution IDs be `{blueprint}-{timestamp}` (human-readable) or UUIDs (guaranteed unique)?

**Recommended resolution:** `{blueprint}-{YYYY-MM-DD-HH-MM-SS}` for human readability. If two executions of the same blueprint start in the same second (unlikely), append a counter: `-2`, `-3`. This matches the Hive's date-slug convention for knowledge records.

### 4. Interactive Step + Autonomous Blueprint Tension

**Question:** A scheduled blueprint has an interactive step. It runs at 7am, reaches the interactive step, and... Craig is asleep. What happens?

**Recommended resolution:** The step enters `waiting_for_human` status. A Slack notification fires immediately. The execution pauses at that step — no timeout kills it. When Craig attaches and completes the interactive session, the blueprint resumes from the next step. The `timeout_minutes` on an interactive step is a soft limit — it triggers a notification, not a kill. Interactive steps in scheduled blueprints are explicitly acknowledged as "Craig will do this when he's ready."

### 5. Blueprint Versioning

**Question:** When a YAML definition changes, what happens to running executions of the old version?

**Recommended resolution:** Running executions continue with the definition they started with (the full definition is embedded in the execution record at start time). New executions use the updated definition. The `blueprint_version` field tracks this. No migration mechanism needed — blueprints evolve through YAML edits, and the old execution records preserve their original definition.

---

## Addendum: Corrections from Design Review (2026-03-24 walkthrough)

These corrections were made during the design walkthrough and override any conflicting content in the sections above:

### 1. No 90-Day TTL on Execution Records
Execution history is valuable data — trend analysis, debugging, pattern recognition. No auto-deletion. If volume becomes an issue, archive rather than delete.

### 2. Worktrees Replace Advisory Locks
The OS already uses git worktrees for session isolation. Every session created via `session create` gets its own worktree. Two blueprints working on the same repo get separate worktrees. The `blueprint_locks` collection and advisory lock mechanism described in Section 3 are unnecessary and should be removed.

### 3. Single-Session Mode
The majority of blueprints execute in a single Claude Code session. Added `mode: single-session | multi-session` to the definition format. In single-session mode, steps are structured instructions sent as one prompt to one session. The runner tracks execution at the session level, not step level. Multi-session mode is the orchestrated version with separate sessions per step.

### 4. Context Assembly Is Built Into Every Session Step
Every session step runs context assembly before the work prompt. The runner calls `hive search`, `hive refs`, `hive recent` based on the blueprint's domains, system, and any referenced entities. The assembled context is prepended to the step prompt. This uses the existing Hive CLI — no new infrastructure. Playbooks provide system-specific context assembly instructions referenced via `playbook_path`.

### 5. Hive-Native Notification System
Notifications are a Hive primitive, not Slack-specific. The runner calls `hive notify` (new CLI command) which creates a notification record. A pluggable delivery layer routes to configured channels (Wall tiles always, plus optional Slack, macOS notifications, email, mobile push). Blueprints never reference Slack directly.

### 6. Skills vs Blueprints Boundary
Skills = atomic capabilities sessions have (how to use a CLI, reference knowledge). Blueprints = executable workflows (sequences of work with scheduling, tracking, observability). Skills live inside blueprints — sessions spawned by blueprints use skills as tools. Workflow-like skills (/morning, /code-dev, /weekly-summary) become blueprints. Tool skills (/hive, /slack, /github) stay as skills.

### 7. Coexistence, Not Migration
Blueprints are built alongside existing skills with zero breaking changes. Both work simultaneously. Migration is a deliberate one-time programmatic cutover when Craig is ready, not a gradual process during development.

### 8. Decisions Recorded in Hive
All design decisions from this session are recorded as Hive knowledge records (tagged `decision`, refs project:hive). They are searchable and will be surfaced by context assembly in future sessions working on the blueprint system.
