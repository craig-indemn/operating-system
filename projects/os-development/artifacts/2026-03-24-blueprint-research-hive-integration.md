---
ask: "How do blueprints integrate with and change the existing Hive system?"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-a
sources:
  - type: codebase
    description: "Full audit of systems/hive/, systems/dispatch/, systems/os-terminal/, systems/session-manager/, .claude/skills/, hive/.registry/, lib/os_state.py"
  - type: design
    description: "2026-03-08-hive-design.md, 2026-03-24-blueprint-system-problem-statement.md, 2026-03-24-hive-phase6-brainstorm.md"
---

# Blueprint System Research: Hive Integration Findings

Raw findings organized by research angle. No solutions proposed — this is the factual landscape that a design session should work from.

---

## 1. Existing Entity Types and What Needs to Change

### Current Entity Types in `.registry/types/`

15 entity type YAMLs exist:

| Type | Key Fields | Status Field Values |
|------|-----------|-------------------|
| `person` | name, email, role, company | active, inactive, archived |
| `company` | name, industry, relationship | — |
| `product` | name, company, status | — |
| `project` | name, description, team, domains | active, paused, completed, archived |
| `workflow` | name, objective, status, current_context, sessions, project, artifacts | active, paused, completed |
| `meeting` | — | — |
| `brand` | — | — |
| `platform` | — | — |
| `channel` | — | — |
| `linear_issue` | key, title, status, assignee, team | (sync adapter mapped) |
| `calendar_event` | — | (sync adapter mapped) |
| `slack_message` | — | (sync adapter mapped) |
| `github_pr` | — | (sync adapter mapped) |
| `email_thread` | — | (sync adapter mapped) |

### The `workflow` Entity Is the Closest Existing Concept

The `workflow` type was designed to be "INDEX.md as a typed entity that updates itself." Its fields:
- `name` (string, required)
- `objective` (string, required)
- `status` (enum: active, paused, completed)
- `current_context` (string — free-text state summary)
- `sessions` (list — session IDs)
- `project` (ref → project)
- `artifacts` (list — knowledge record IDs)
- `domains` (list, required)
- `tags` (list)

**Gaps for blueprints:** The workflow entity has no concept of:
- Steps or phases as structured data (steps are just prose in `current_context`)
- Blueprint definition reference (what pattern this workflow follows)
- Execution state (running, failed, waiting_for_input)
- Parallel execution tracking
- Scheduling information (cron, triggers)
- Harness type per step
- Step dependencies or ordering
- Cost/token tracking
- Execution history distinct from knowledge artifacts

### The `project` Entity

Fields: name, description, team, domains, tags, status (active, paused, completed, archived). Projects group workflows but have no execution semantics.

### Ontology (`ontology.yaml`)

Current tags that touch workflow/execution concepts:
- `session_summary` (kind) — created at session close
- `context_assembly` (kind) — context note written by assembly session
- `feedback` (kind) — self-improvement signal

No tags exist for: blueprint definition, execution log, step result, execution trace, scheduled task.

Current statuses: backlog, ideating, active, in-review, done, archived.

No statuses exist for: running, failed, waiting_for_input, scheduled, cancelled, timed_out.

Current priorities: low, medium, high, critical.

### What's Missing from the Type Registry

Blueprints introduce concepts that don't map to any existing type:
1. **Blueprint definition** — the reusable template (steps, harness per step, scheduling config)
2. **Blueprint execution** — a specific run of a blueprint (state machine, current step, step results)
3. **Step execution** — individual step within an execution (harness, input, output, status, metrics)
4. **Schedule** — cron or trigger configuration for automated runs

These are either new entity types, new knowledge record tags, or some combination.

---

## 2. Existing Playbooks and Their Fate

### Current Playbooks (in `systems/hive/playbooks/`)

Four playbooks exist as markdown files:

| Playbook | Purpose | Lines | Structure |
|----------|---------|-------|-----------|
| `code-dev.md` | Context assembly for code development sessions | 110 | 6 assembly steps → context note format → principles |
| `content.md` | Context assembly for content creation sessions | 106 | 6 assembly steps → context note format → principles |
| `morning.md` | Morning planning consultation | 152 | 7 assembly steps → context note format → after-conversation steps → principles |
| `ceo-weekly.md` | Weekly summary for CEO/teammates | 91 | 7 data gathering steps → output format → distribution |

### How Playbooks Are Used Today

1. The session manager CLI (`session create --assembly --playbook <path>`) creates a short-lived context assembly session
2. The playbook markdown is sent as the first message to that session
3. The context assembly session reads the playbook, executes the `hive` CLI commands listed in it, synthesizes results into a context note
4. The context note is written to the Hive via `hive create note`
5. The assembly session terminates

### Playbook Structure (Common Pattern)

Every playbook follows the same structure:
1. **Inputs** — what the spawning request provides (workflow ID, date, etc.)
2. **Assembly Steps** — numbered steps, each with one or more `hive` CLI commands and instructions for what to do with results
3. **Context Note Format** — a markdown template showing how to structure the output
4. **Principles** — guidelines for the assembly agent (comprehensive not compressed, reference IDs, etc.)
5. **Save the Context Note** — the `hive create` command to persist the output

### Playbook-to-Blueprint Relationship

The problem statement says "Playbooks are absorbed as the context-assembly step of blueprints." Observations:

- Playbooks are purely informational — they describe how to gather context. They don't execute code, deploy artifacts, or change state.
- A blueprint step for "gather context" could reference a playbook by path and run it as the assembly phase.
- However, playbooks currently depend on being sent to a Claude Code session as a first message. There's no CLI that "runs a playbook" — a session interprets it.
- The morning playbook includes post-consultation steps (updating priorities, creating session summaries) that go beyond context assembly into actual work. It's already more than just "gather context."
- The CEO weekly playbook includes output distribution (Slack, email, PDF). It's a complete workflow, not just context assembly.

### What Actually References Playbooks

- `systems/session-manager/cli.py` line 236: reads playbook file and sends content as first message to assembly session
- `.claude/skills/morning/SKILL.md`: references `systems/hive/playbooks/morning.md` as the playbook to follow
- `.claude/skills/code-dev/SKILL.md`: references the code-dev playbook at `systems/hive/playbooks/code-dev.md`
- The Hive design doc (hive-design.md) describes playbooks as "system context playbooks" that each system defines

---

## 3. The Dispatch System and What's Reusable vs Deprecated

### Current Dispatch Architecture (`systems/dispatch/`)

Files:
- `engine.py` (521 lines) — the ralph loop implementation
- `SYSTEM.md` — system description
- `active/learnings.md` — append-only learnings from the last run
- `active/summary.md` — summary of last run

### How Dispatch Works Today

1. Takes a beads epic ID + target repo path
2. Reads children of the epic from `bd` CLI (beads task tracker)
3. Picks the next ready child (open, dependencies satisfied)
4. Spawns a Claude Code session via `claude-agent-sdk` `query()` with:
   - `cwd` = target repo
   - `add_dirs` = OS root
   - `setting_sources = ["user", "project"]` (loads skills)
   - `permission_mode = "bypassPermissions"`
   - `system_prompt` appended with task context + learnings
5. Runs a separate verification session (different Claude Code session)
6. If passes: marks bead closed, git commits, appends to learnings
7. If fails: marks bead open, appends failure to learnings, retries (max 3)
8. Loops until all tasks done or exhausted

### Reusable Components from Dispatch

| Component | Reusability | Notes |
|-----------|------------|-------|
| `query()` call pattern via Agent SDK | High | The core pattern of spawning autonomous Claude Code sessions with managed context works. Blueprints would use the same SDK. |
| `ClaudeAgentOptions` configuration | High | cwd, add_dirs, setting_sources, permission_mode, system_prompt append — all directly applicable. |
| Separate verification session pattern | Medium | Good for code tasks, but blueprints need more flexible verification (not always a separate Claude session). |
| Learnings file (append-only) | Medium | The concept of accumulating context across steps is sound. But it's a flat file, not Hive-native. |
| Beads integration (`bd` CLI) | Low | Blueprints replace beads for task decomposition. Beads is a CLI-level task tracker; blueprints are Hive-native execution plans. |
| `git_commit()` after each task | Medium | Useful for code-related blueprint steps but not general-purpose. |
| `run_task_session()` async function | High | The actual SDK session execution with output capture. Nearly directly reusable. |
| `build_task_context()` context assembly | Low | Too beads-specific. Blueprint context assembly uses the Hive. |
| Rate limit event monkey-patch | High | Required workaround for `claude-agent-sdk` message parser. Must carry forward. |

### What Dispatch Doesn't Have That Blueprints Need

- No parallel execution (purely sequential)
- No conditional routing (always linear task list)
- No human-in-the-loop (fully autonomous)
- No scheduling
- No mixed harness support (Claude Code sessions only)
- No Hive integration (doesn't create Hive records, doesn't query Hive for context)
- No infrastructure-level tracing (just prints to stdout)
- No crash recovery (if the engine dies, start over)
- State is in beads + flat files, not in the Hive

### The Problem Statement Says "Dispatch is replaced by the blueprint execution framework"

The dispatch engine is 521 lines of Python. Its core value is the ralph loop pattern and the Agent SDK integration. A blueprint execution framework would need to:
1. Subsume the ralph loop (sequential task execution with retry) as one execution pattern
2. Add parallel, conditional, and sub-blueprint patterns
3. Replace beads with Hive-native step tracking
4. Add observability (tracing, cost tracking)
5. Add scheduling
6. Keep the Agent SDK integration for Claude Code session steps

---

## 4. Wall UI Changes Needed

### Current Wall Architecture

The Wall (`systems/os-terminal/src/components/Wall.tsx`) renders tiles from two sources:
1. **Active sessions** — from `useSessions()` hook, converted to `HiveRecord` format via `sessionToTile()`
2. **Hive records** — from `useHiveRecords()` hook, which receives data via WebSocket from the server's `hive-watcher.ts`

### Current Tile Rendering

`HiveTile.tsx` renders tiles using progressive disclosure based on height:
- **Compressed** (< 65px): badge + title only
- **Standard** (65-105px): badge + title + timestamp
- **Expanded** (105-165px): + context line + tags + context bar (sessions) + connections
- **Featured** (> 165px): + description

### Current Type Color Map (`colors.ts`)

Every entity type has a color. Session tiles have their own accent color system (started=blue, active=green, idle=amber, context_low=red). Knowledge tags also have colors (decision=amber, design=orange, etc.).

### What the Wall Doesn't Currently Show

The Wall has no concept of:
- **Execution state** — "this thing is running right now" (sessions have active/idle, but there's no "step 3 of 7 executing")
- **Progress indication** — no step progress bars, no completion percentage for multi-step workflows
- **Scheduled items** — no "runs at 7am tomorrow" indicator
- **Execution history** — no "last ran 2h ago, completed in 4m"
- **Step-level visibility** — no expanding a workflow tile to see its steps
- **Parallel execution indicator** — no "3 sub-tasks running in parallel"
- **Cost/token metrics** — sessions show context%, but nothing about API cost

### Current Tile Data Model (`types/hive.ts`)

```typescript
interface HiveRecord {
  record_id: string;
  type: string;           // entity type or 'knowledge'
  title?: string;
  name?: string;
  tags?: string[];
  domains?: string[];
  status?: string;
  priority?: string;
  system?: string;
  ref?: string;
  refs_out?: Record<string, string[]>;
  content?: string;
  created_at?: string;
  updated_at?: string;
  objective?: string;      // workflow-specific
  current_context?: string; // workflow-specific
  date?: string;           // meeting-specific
  [key: string]: unknown;  // extra fields
}
```

This is flexible via `[key: string]: unknown` but the rendering logic in `HiveTile.tsx` only handles known fields: `type`, `status`, `priority`, `tags`, `content`, `objective`, `current_context`, `date`, `_sessionId`, `_contextPct`, `_sessionType`, `_model`.

### Wall Ordering (`wallOrder.ts`)

Priority order: critical > high > medium > low. Status order: active > in-review > ideating > backlog > done > archived. Sessions always sort above everything.

The highlight reel (compressed mode) shows: active, in-review, critical/high priority, or updated within 24h.

### Action Menu (`ActionMenu.tsx`)

Current actions: Open in new session, Mark done, Change priority, Archive, Create linked note, Open in external system.

No actions for: Run blueprint, View execution history, Cancel execution, Retry failed step, View step output.

### Session-to-Tile Conversion

`sessionToTile()` converts active sessions to `HiveRecord` format with synthetic `record_id: "session:<uuid>"`, `type: "session"`, and stashed session data in `_sessionId`, `_contextPct`, `_sessionType`, `_model`.

Blueprint executions that spawn sessions need to show the relationship: "this session is step 3 of blueprint X."

---

## 5. New CLI Commands Needed

### Current Hive CLI Commands (14 total + 4 graph quality)

```
get, create, update, search, list, refs, recent, sync, feedback, status, init,
types (list|show), tags (list), domains (list),
archive, health, ontology (check|usage), discover
```

### Commands the Problem Statement Implies

From the requirements:

| Need | Current Coverage | Gap |
|------|-----------------|-----|
| Define a blueprint | None | `hive blueprint create/define` or store as knowledge/entity |
| Run a blueprint | None | `hive blueprint run <id>` |
| View blueprint execution status | None | `hive blueprint status <execution-id>` |
| List blueprints | None | `hive blueprint list` (all definitions) |
| List executions | None | `hive blueprint executions [--blueprint <id>]` |
| Schedule a blueprint | None | `hive blueprint schedule <id> <cron>` |
| Cancel an execution | None | `hive blueprint cancel <execution-id>` |
| Retry a failed step | None | `hive blueprint retry <execution-id> [--step <n>]` |
| View step output | `hive get` if step outputs are records | Step outputs need to be Hive records |
| Pause/resume execution | None | `hive blueprint pause/resume <execution-id>` |
| Fan-out tracking | None | Sub-execution tracking |

### CLI Routing Implications

The current CLI routing logic (`cli.py`, lines ~65-90) routes based on whether the first argument is a registered entity type or a known tag. Adding `blueprint` as a top-level subcommand would work like existing `types`, `tags`, `domains`, `archive`, `health`, `ontology`, `discover` — they're all direct subcommands that don't go through the type/tag routing.

The CLI uses `argparse` (not Click or Typer, despite the design doc suggesting those). The command structure is flat with subparsers. Adding a `blueprint` subcommand with its own sub-subparsers follows the pattern of `ontology` (which has `check` and `usage` sub-subcommands).

---

## 6. Context Assembly Changes

### Current Context Assembly Flow

1. Hive UI → user clicks tile → objective prompt → spawns context assembly session
2. Session manager creates `--assembly` session with `--playbook <path>` and `--objective <text>`
3. Assembly session reads playbook, runs Hive CLI commands, writes context note
4. Working session starts with context note content

### How Blueprints Change This

**Context assembly becomes a blueprint step.** Instead of a separate assembly session → working session flow, a blueprint could define:
- Step 1: Gather context (run assembly playbook)
- Step 2: Do the work (run in Claude Code session with context from step 1)
- Step 3: Checkpoint to Hive (create records from step 2 output)

**Context assembly for blueprint-aware sessions.** When a session starts that is part of a blueprint execution, the context should include:
- Blueprint definition (what's the plan)
- Current execution state (which step, what's completed, what failed)
- Outputs from previous steps (artifacts, decisions, learnings)
- The original workflow entity's `current_context`

This is richer than current context assembly, which only considers the workflow entity and general Hive knowledge.

### Current `session create --assembly` Implementation

In `session-manager/cli.py` (lines 222-252):
- Creates a normal session with `assembly = True` flag in state
- Stores `assembly_playbook`, `assembly_objective`, `assembly_tile_metadata`
- After 5s delay, sends the playbook content + objective as the first message
- The assembly session is expected to write a context note and exit

This is fragile:
- 5-second delay before sending the first message (waiting for Claude to be ready)
- No verification that the context note was actually written
- No structured output — just hoping the session follows the playbook
- No timeout — if the assembly session hangs, it runs forever

### Playbook References in Skills

- `/morning` SKILL.md: "Gather context using the morning consultation playbook (systems/hive/playbooks/morning.md)"
- `/code-dev` SKILL.md: "the context assembly agent uses the code-dev playbook (systems/hive/playbooks/code-dev.md)"

These skills reference playbooks but don't invoke context assembly sessions. They're instructions for sessions that are already running. The assembly session spawning is done by the Hive UI via the session manager CLI.

---

## 7. What Breaks? Risk Assessment

### Risk: Workflow Entity Overloading

The `workflow` entity currently serves as "long-running work state tracker." Blueprints add execution semantics on top. If blueprint execution state is grafted onto the workflow entity, the entity becomes overloaded — it simultaneously represents:
- The conceptual work item (objective, project, domain)
- The execution plan (steps, dependencies, harness config)
- The execution state (current step, step results, execution history)
- The scheduling configuration (cron, triggers)

The design doc explicitly says "Systems own workflow lifecycle, not the Hive." If blueprints own execution lifecycle, and workflows become blueprint-powered, does the Hive now own execution lifecycle?

### Risk: Entity/Knowledge Routing Ambiguity

The CLI's core design principle is that entity types and knowledge tags must be disjoint. If `blueprint` becomes an entity type, it can't also be a tag. If blueprint definitions are knowledge records (markdown with frontmatter), they can't also be entities. The design decision here affects the entire routing system.

### Risk: Session Manager Integration

The session manager creates sessions with worktrees, tmux, and Claude Code. Blueprint execution that spawns sessions needs to:
1. Create sessions via the session manager (reusing worktree/tmux infrastructure)
2. Track which blueprint step each session belongs to
3. Handle session crashes (session dies mid-step)
4. Handle session manager crashes (tmux disappears)

Currently, session state lives in `sessions/*.json` files. Blueprint execution state would need to reference session IDs. If a session ends dirty (tmux gone), the blueprint needs to know and either retry or fail the step.

### Risk: UI Data Pipeline

The Hive UI gets records via `hive recent 30d --limit 200 --format json` (in `hive-watcher.ts`, line 35). This fetches the last 200 records from the last 30 days. If blueprint executions create many records (step results, execution logs, learnings), the 200-record limit could push out "real" records that should be visible on the Wall.

The polling interval is 30 seconds (`POLL_INTERVAL_MS = 30_000`). For active blueprint executions, 30 seconds is too slow to show real-time progress.

### Risk: MongoDB Schema Changes

All records live in a single `records` collection with a type discriminator. Adding blueprint-related document types increases the collection's polymorphism. The current indexes are:
- `record_id` (unique)
- `type` (regular)
- `tags` (multikey)
- `domains` (multikey)
- `status` (regular)
- Various `refs_out.*` (multikey)
- `wiki_links` (multikey)
- `content_embedding` (regular array)
- `created_at`, `updated_at` (regular)
- Full-text on `title` + `content`
- Compound: `{type: 1, status: 1}`, `{type: 1, domains: 1}`, `{updated_at: -1, type: 1}`

Blueprint execution queries would likely need:
- "All executions of blueprint X" → `{type: "execution", blueprint_id: "X"}`
- "All running executions" → `{type: "execution", status: "running"}`
- "Steps for execution Y" → `{type: "step", execution_id: "Y"}`
- "Most recent execution of blueprint X" → sort by `created_at`, limit 1

These patterns work with the existing single-collection approach but need new indexes.

### Risk: Hive CLI Performance

The Hive CLI is invoked as a subprocess by the Express server (`routes/hive.ts`). Each API call spawns `python3 cli.py <args>`, which:
1. Imports pymongo
2. Connects to MongoDB
3. Loads the registry (reads YAML files from disk)
4. Executes the query
5. Serializes output

For real-time blueprint execution monitoring, this per-request overhead (~200-500ms) may be too slow. The hive-watcher already uses polling because of this.

### Risk: Dispatch Migration Path

The dispatch system has been used (learnings.md and summary.md show a completed 2-task test run). If blueprints replace dispatch, existing dispatch workflows in progress would need migration. Currently there's only test data in `active/`, so this is low risk.

### Risk: Playbook Format Incompatibility

Playbooks are markdown documents designed to be read by a Claude Code session as natural language instructions. If blueprints formalize steps as structured data (YAML, JSON), the existing playbooks can't be used directly — they'd need to be converted or wrapped.

### Risk: Knowledge Directory Structure

The `config.py` KNOWLEDGE_DIRS mapping determines where knowledge records are written:
```python
KNOWLEDGE_DIRS = {
    "note": "notes",
    "decision": "decisions",
    "design": "designs",
    "research": "research",
    "session_summary": "sessions",
    "feedback": "notes",
    "context_assembly": "sessions",
}
```

If blueprint definitions are knowledge records, they need a directory. If execution logs are knowledge records, they need a directory. The vault structure would grow.

### Risk: The `hive sync` Rebuild Assumption

Knowledge records are "files as source of truth, MongoDB as derived." Running `hive sync` rebuilds all knowledge records from files. If blueprint execution state is stored as knowledge records, a `hive sync` would need to correctly rebuild execution state. But execution state is inherently temporal — rebuilding it from static files loses ordering and timing.

### Things That Probably Don't Break

- **Entity CRUD** — creating entities, getting entities, updating entities. Blueprint types would just be new entity types.
- **Search** — semantic and keyword search work on any record type. Blueprint records would be searchable.
- **Refs traversal** — the graph traversal code is type-agnostic. Blueprint refs would work.
- **Sync adapters** — external system sync is independent of blueprints.
- **Session tile rendering** — existing session tiles would still work. Blueprint-spawned sessions would appear as normal sessions.

---

## 8. The Agent SDK Connection

### Current Usage in Dispatch

The `claude-agent-sdk` package (v0.1.38) is used only in `systems/dispatch/engine.py`. Key patterns:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

options = ClaudeAgentOptions(
    cwd=target_repo,
    add_dirs=[str(OS_ROOT)],
    setting_sources=["user", "project"],
    permission_mode="bypassPermissions",
    model="opus",
    system_prompt={"type": "preset", "preset": "claude_code", "append": context},
)

async with aclosing(query(prompt=prompt, options=options)) as messages:
    async for message in messages:
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    output_parts.append(block.text)
        elif isinstance(message, ResultMessage):
            cost = message.total_cost_usd
```

### Critical Workaround

The dispatch engine includes a monkey-patch for the Agent SDK message parser (lines 33-48) to handle unknown message types like `rate_limit_event`. This is labeled as a workaround for a known issue. Any blueprint execution framework using the Agent SDK would need this same workaround.

### Environment Variable Requirement

The engine unsets `CLAUDECODE` environment variable (`os.environ.pop("CLAUDECODE", None)`) to bypass the nested session guard. This is required for any code that spawns Claude Code sessions from within the OS.

### Session Manager vs Agent SDK

The session manager creates sessions via `tmux` + `claude` CLI. The dispatch engine creates sessions via the Agent SDK `query()` function. These are different mechanisms:

- **Session manager** → tmux-based, interactive, persistent, has worktrees and state files
- **Agent SDK** → programmatic, non-interactive, ephemeral, no worktrees or state files

Blueprint execution needs both: the session manager for interactive steps, the Agent SDK for autonomous steps. The problem statement says "The execution primitive is a tmux terminal (Hive session) — anything that can run in a terminal can be a step."

---

## 9. The LangGraph Decision

The problem statement says "LangGraph is the orchestration engine for complex blueprints." Observations:

### What LangGraph Would Replace

LangGraph would replace the dispatch engine's sequential loop as the orchestration mechanism. Instead of a Python while-loop iterating through beads, LangGraph would:
- Define blueprint steps as graph nodes
- Define transitions (including conditional) as edges
- Manage state between nodes
- Handle parallel execution via fan-out/fan-in

### What LangGraph Wouldn't Replace

- The Hive CLI (still the interface for agents)
- The Agent SDK (still how Claude Code sessions are spawned)
- The session manager (still how tmux sessions are managed)
- The Hive data model (still where records live)
- The UI (still how execution is visualized)

### Integration Questions

- LangGraph state management vs Hive record persistence — who is the source of truth for execution state?
- LangGraph's built-in checkpointing vs Hive's knowledge records — are these redundant or complementary?
- LangGraph runs as a Python process — how does it interface with the Hive CLI and session manager?

---

## 10. Existing Patterns That Blueprint Design Should Respect

### Pattern: CLI-First

Every system interaction goes through a CLI. The Hive CLI is the interface for agents. Blueprint execution should be controllable via `hive` CLI commands, not a separate tool.

### Pattern: Two-Layer Data Model

Entities (structured, MongoDB) vs knowledge (prose, markdown files). Blueprint definitions could be either. Blueprint execution state is inherently structured — it's a state machine, not prose.

### Pattern: Systems Own Their Lifecycle

"Systems own workflow lifecycle, not the Hive. The Hive stores the record; the context assembly agent reads it; but the system's CLI creates and updates it." Blueprints need a system that owns execution lifecycle. Is that the Hive itself, or a new "blueprint runner" system?

### Pattern: Skills Are the Interface

"Skills are the interface for everything." There should be a `/blueprint` skill (or `/hive` absorbs blueprint commands). Skills tell sessions how to use the tools.

### Pattern: Context Assembly Is an LLM Task

Context assembly is "an LLM agent that uses the Hive CLI as its toolkit." Blueprint-aware context assembly would use the same pattern but with additional queries (current execution state, step outputs, etc.).

### Pattern: Graceful Degradation

The session manager's Hive integration uses try/except and continues if the Hive CLI is unavailable. Blueprint execution should similarly degrade gracefully if the Hive is down.

### Pattern: Session State Files

Active sessions use `sessions/*.json` files (gitignored). Blueprint execution state needs to be similarly persistent but available across sessions. The design doc says "Blueprint state lives in the Hive, not in sessions."

### Pattern: Records as the Unit of Everything

"Everything is a record. Everything is a tile." Blueprint definitions, executions, and steps should be records that appear as tiles on the Wall.

---

## 11. Concrete Inventory of Files That Would Change

### Must Change

| File | Reason |
|------|--------|
| `hive/.registry/ontology.yaml` | New tags and possibly new statuses for blueprint-related records |
| `hive/.registry/types/` | New entity type YAML(s) for blueprint, execution, and/or schedule |
| `systems/hive/cli.py` | New `blueprint` subcommand(s) |
| `systems/hive/config.py` | New knowledge directory mapping if blueprint records are knowledge |
| `systems/hive/entity_ops.py` | New entity type support (if blueprint/execution are entities) |
| `systems/hive/SYSTEM.md` | Updated capabilities to include blueprint execution |
| `.claude/skills/hive/SKILL.md` | New commands documented |

### Likely Change

| File | Reason |
|------|--------|
| `systems/os-terminal/src/types/hive.ts` | New fields on HiveRecord for execution state |
| `systems/os-terminal/src/components/HiveTile.tsx` | New tile rendering for blueprint/execution records |
| `systems/os-terminal/src/components/Wall.tsx` | Height calculation for new tile types |
| `systems/os-terminal/src/components/ActionMenu.tsx` | New actions (run, cancel, retry, view steps) |
| `systems/os-terminal/src/utils/colors.ts` | New type colors for blueprint, execution, step |
| `systems/os-terminal/src/utils/wallOrder.ts` | New status ordering for running/failed/scheduled |
| `systems/os-terminal/server/routes/hive.ts` | New API endpoints for blueprint operations |
| `systems/os-terminal/server/hive-watcher.ts` | Faster updates for active executions |
| `systems/hive/playbooks/` | Playbooks either become blueprint definitions or are referenced by them |
| `systems/session-manager/cli.py` | Session creation needs blueprint execution context |

### Possibly Deprecated

| File | Reason |
|------|--------|
| `systems/dispatch/engine.py` | Replaced by blueprint execution framework |
| `systems/dispatch/SYSTEM.md` | Dispatch system replaced |
| `systems/dispatch/active/` | No longer needed |
| `.claude/skills/dispatch/` | Replaced by blueprint skill (if it exists) |

### New Files Needed

| Category | What |
|----------|------|
| Blueprint execution engine | Python module(s) in `systems/hive/` or new `systems/blueprint/` |
| Blueprint entity type(s) | YAML in `hive/.registry/types/` |
| Blueprint CLI commands | New module(s) in `systems/hive/` |
| Blueprint skill | `.claude/skills/blueprint/SKILL.md` or extend `/hive` |
| Blueprint knowledge directory | `hive/blueprints/` if definitions are knowledge records |

---

## 12. Scale Considerations

### Current Scale

The Hive design doc anticipates "hundreds to low thousands of records." Cosine similarity is computed in Python because "at the scale of hundreds to low thousands of records, this is fast enough."

### Blueprint Scale Impact

Each blueprint execution creates multiple records:
- 1 execution record
- N step records (one per step)
- M knowledge records (artifacts produced by steps)

A morning consultation blueprint running daily for a year = 365 executions x ~7 steps = ~2,555 step records + 365 execution records. A code development blueprint running 20 sessions with 5 steps each = 100 step records.

This could quickly reach the "low thousands" range just from blueprint execution data, before counting actual knowledge records. The cosine similarity approach and the `hive recent 30d --limit 200` fetch pattern may need revisiting.

---

## 13. Scheduling Infrastructure

### What Exists

The problem statement mentions "Claude Code now has cron/scheduling capabilities via a command that should be explored." The brainstorm doc says "Scheduling — workflows should be schedulable."

### What Doesn't Exist

- No cron daemon or scheduler in the OS
- No scheduled task runner
- No `hive schedule` command
- No database table for scheduled jobs
- The session manager has no concept of scheduled session creation

### The Primitive

"The execution primitive is a tmux terminal (Hive session)." Scheduling would need to:
1. Trigger at the specified time
2. Create a session via the session manager
3. Send the blueprint's first step as the initial message
4. Monitor execution

This is a background process. The OS currently has no long-running background processes (MongoDB is the only always-on service, managed by Homebrew). A scheduler would be the second.

### macOS launchd

macOS's native scheduling mechanism is launchd (not cron, though cron works). A plist in `~/Library/LaunchAgents/` could trigger `hive blueprint run <id>` at specified intervals.
