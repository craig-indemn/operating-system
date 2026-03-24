---
ask: "Synthesize 7 parallel research streams into a single decision-ready brief for the Hive blueprint execution system"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-b
sources:
  - type: research
    description: "7 parallel research documents: problem statement, LangGraph, workflows, execution, state-of-art, Hive integration, edge cases"
  - type: design
    ref: "projects/os-development/artifacts/2026-03-08-hive-design.md"
    name: "Hive design document"
---

# Blueprint Research Synthesis

---

## 1. Convergent Findings

**Seven independent research streams agree on these points:**

**Deterministic orchestration around bounded agent autonomy.** Every research stream — LangGraph, state-of-art frameworks, Anthropic's own guidance, McKinsey's analysis, the workflow mapping, and the edge case analysis — converges on: a deterministic engine enforces step transitions and manages dependencies; agents execute within bounded steps; agents do not decide what phase they're in or what comes next. This is the dominant production pattern of 2025-2026. The existing dispatch engine already implements this (loop picks next task, session executes, verification checks). Blueprints generalize it.

**Fresh context per step is non-negotiable.** The dispatch engine, Anthropic's long-running agent harness, the Hive's context assembly model, and the state-of-art research all independently arrive at: each step gets its own fresh context window with curated state, not accumulated session history. The 1M context window is large but not infinite. Context pollution across steps degrades quality. State lives externally (Hive records, git, files), not in the session's memory.

**Durable execution state is table stakes.** The dispatch engine's lack of crash recovery is flagged as a critical limitation by the execution research, the edge case analysis, and the state-of-art survey. Every production system (Temporal, Inngest, Restate, LangGraph with checkpointing) persists execution state at step boundaries. The Hive is the natural persistence layer, but the current dispatch engine stores nothing durable about its own execution.

**Two tiers of complexity exist and both are real.** The workflow mapping found 4 simple workflows (1-3 steps, single session), 7 medium workflows (3-7 steps, 2-4 systems), and 5 complex workflows (7+ steps, multi-session, 4+ systems). The edge case research identified that forcing simple workflows through a complex orchestrator violates the OS philosophy. The LangGraph research confirmed that LangGraph adds overhead unjustified for sequential 3-step flows. Both tiers need first-class support.

**The existing primitives are 80% of what's needed.** The workflow mapping, execution research, and Hive integration analysis all find: the session manager (spawn/monitor sessions), the Agent SDK (autonomous execution), the Hive CLI (state/knowledge), and the skill system (capability encoding) already exist. The gap is orchestration — connecting steps across time with state management, scheduling, conditional routing, fan-out, and observability. Not a new system; an orchestration layer over existing primitives.

**Self-compressing artifacts are the key differentiator.** The state-of-art survey found MIT's criticism: "most systems don't retain feedback, accumulate knowledge, or improve over time." The Hive's design — where execution produces knowledge records that feed future context assembly — directly addresses this. The flywheel mechanism (work produces context for future work) emerged independently in the Hive design, the content system integration, and the code-dev system design.

**Event-driven + scheduled = complete trigger model.** Claude Code now has three scheduling tiers (cloud, desktop, `/loop`) plus Channels for event-driven triggers. The state-of-art confirms this dual model is standard. The workflow mapping identified daily scheduled workflows (morning consultation) and event-triggered workflows (PR merged, email received) as equally important.

---

## 2. Contradictions to Resolve

### Contradiction 1: LangGraph as the orchestration engine vs. simplicity requirement

**Side A (problem statement):** "LangGraph is the orchestration engine for complex blueprints."

**Side B (all research streams):** LangGraph adds LangChain dependency, memory overhead (2GB reported for basic tasks), debugging complexity, Python-process-bound execution, and version coupling. The OS philosophy says "no magic, no abstraction for abstraction's sake." Simple blueprints (7 of 16 identified workflows) don't need LangGraph. The existing dispatch engine is 520 lines of custom Python. Anthropic's own guidance says "the most successful implementations use simple, composable patterns rather than complex frameworks."

**The resolution space:** LangGraph is one possible engine for complex orchestration, not the only option. The two-tier finding suggests a simple runner for simple blueprints and a more capable engine for complex ones. LangGraph, custom Python with asyncio, or Claude Code's native Agent Teams could fill the complex tier. The decision should be deferred until the simple tier proves insufficient.

### Contradiction 2: Session-count agnostic vs. session-as-primitive

**Side A (problem statement):** "Session-count agnostic — may execute in a single session or span many. State lives in the Hive, not the session."

**Side B (brainstorm + infrastructure):** "Sessions are the underlying primitive of Hive workflows — every piece of work happens through a session." The session manager owns session lifecycle. The Hive UI shows session tiles. Everything passes through a tmux terminal.

**The resolution space:** Both are true at different layers. The blueprint doesn't care how many sessions a step uses (agnostic). But the runner executes each step via a session (primitive). State lives in the Hive; execution happens in sessions. These aren't contradictory — the blueprint's state model is Hive-centric; its execution model is session-centric.

### Contradiction 3: Infrastructure-level tracing vs. self-compressing artifacts

**Side A (problem statement):** "Infrastructure-level tracing, not self-reported by the executing session."

**Side B (Hive design):** "Self-compressing — artifacts created during execution are Hive records." Skills like code-dev and brainstorm-hive create Hive records as byproducts of working. That IS self-reporting.

**The resolution space:** Both are needed. Infrastructure-level tracing captures what the runner observes (step started, step completed, duration, cost, exit code). Self-compressing artifacts capture what the session produced (decisions, designs, code). They serve different purposes: tracing is for operational observability; artifacts are for knowledge accumulation. The blueprint system needs both, and they are complementary, not competing.

### Contradiction 4: Harness-agnostic vs. everything-in-tmux

**Side A (problem statement):** "Steps can execute via Claude Code sessions, Python scripts, CLI commands, LangGraph agents, or any other harness."

**Side B (brainstorm):** "The execution primitive is a tmux terminal — anything that can run in a terminal can be a step."

**The resolution space:** tmux is the visibility layer, not the execution constraint. Agent SDK `query()` calls don't need tmux (they're programmatic async Python). Python scripts don't need tmux. But if you want them visible on the Wall, they need a tmux pane. Resolve by making tmux optional: autonomous steps can run headless (Agent SDK, subprocess); interactive steps get tmux sessions. The runner wraps both.

### Contradiction 5: The Hive as brain vs. execution state store

**Side A (Hive design):** "The Hive is a brain. Systems are the hands. The brain remembers; the hands do work."

**Side B (problem statement):** "Blueprint state lives in the Hive, not in sessions." Execution state (which step is running, retry counts, partial results) is operational data — not knowledge.

**The resolution space:** The session manager already resolves this pattern: operational state in `sessions/*.json` files, durable knowledge in Hive records. Blueprint execution can follow the same split: a lightweight execution state file (or MongoDB collection) for real-time operational data, with summary records in the Hive for knowledge retention and context assembly.

---

## 3. Key Technical Findings

**1. Claude Code now has three scheduling tiers.** Cloud tasks (run on Anthropic infrastructure, survive restarts, 1-hour minimum interval), Desktop tasks (local, survive restarts, 1-minute interval), and `/loop` (session-scoped, 1-minute interval, 3-day expiry). Plus Channels for event-driven triggers. This eliminates the need to build scheduling infrastructure. Blueprints can use Claude Code's native scheduling.

**2. Claude Agent Teams (March 2026) changes the coordination model.** Teams have shared task lists with self-coordination, direct teammate-to-teammate communication, and plan approval gates. This is a natural fit for parallel blueprint steps: the blueprint runner is the lead; parallel workers are teammates. This may eliminate the need for custom fan-out implementation.

**3. The MongoDB checkpoint saver for LangGraph has async issues.** `AsyncMongoDBSaver` was removed from LangGraph 1.0 due to MongoDB Python driver limitations. Only synchronous `MongoDBSaver` works. If LangGraph is used, it must run synchronously or use SQLite/Postgres for checkpoints.

**4. The dispatch engine's Agent SDK workarounds must carry forward.** The monkey-patch for `rate_limit_event` message parsing and the `CLAUDECODE` env var unset are required for any code that spawns Claude Code sessions. These are SDK-level issues, not dispatch-specific.

**5. Resource contention has no solution today.** Two blueprints targeting the same repo would corrupt each other's git staging. No file locking, no advisory locks, no coordination. Concurrent Hive CLI writes could produce slug collisions. This is a hard problem that needs explicit design.

**6. The Hive's semantic search is O(N) and doesn't scale with execution records.** All knowledge embeddings are fetched and compared in Python. Adding thousands of step execution records would degrade search. Execution records should either skip embeddings or live in a separate collection.

**7. Existing playbooks are already proto-blueprints.** The 4 playbooks (morning, content, code-dev, ceo-weekly) have numbered steps, clear inputs/outputs, and produce structured output. Converting them to blueprints is a mapping exercise, not a rewrite.

**8. The morning consultation is the highest-value first blueprint.** Daily, touches 7 systems, the data-gathering phase is fully automatable, and it already has a playbook. It would exercise scheduling, multi-system context assembly, and the Hive knowledge pipeline.

**9. Step-level execution records in the Hive `records` collection would pollute search.** A morning blueprint running daily produces ~2,500 step records/year. The Wall's `hive recent 30d --limit 200` fetch would be dominated by execution noise. Step-level data needs to be stored separately or aggregated into execution-level records.

**10. No notification system exists.** Everything is pull-based. A blueprint blocking on human approval at 3am has no way to notify Craig. The Hive Wall requires Craig to be looking at it. Push notifications (Slack, mobile) are absent from the architecture.

**11. Inngest and Restate offer lightweight durable execution without Temporal's operational overhead.** Both are open-source, single-binary, and designed for AI agent workloads. Restate has a built-in execution timeline UI. Inngest guarantees exactly-once step execution. Either would be simpler than Temporal and more capable than custom Python. But both add dependencies the OS currently avoids.

**12. Spec-Driven Development validates blueprints-as-specs.** GitHub Spec Kit, AWS Kiro, and Tessl all demonstrate: structured specifications drive what agents produce. This is exactly the blueprint model. The Hive's blueprint concept aligns with the SDD movement.

---

## 4. Patterns That Work (from State-of-the-Art)

### Proven in Production

**Deterministic orchestration + bounded agent steps.** Used by Uber (LangGraph), OpenAI Codex (Temporal), Replit Agent (Temporal), LinkedIn (LangGraph). The orchestrator is deterministic code; agents execute within steps; the orchestrator manages state and transitions.

**Durable execution with step-level checkpointing.** Temporal (event history replay), LangGraph (super-step checkpoints), Inngest (step-level persistence), Restate (journal-based recovery). On failure, only the failed step re-executes. Completed steps are never re-run.

**Workflow/Activity separation.** Temporal's core pattern: workflows are deterministic orchestration logic; activities are where non-deterministic work happens (LLM calls, API calls, side effects). Keeping orchestration deterministic enables replay. Activities can be retried independently. This maps to: blueprint runner = workflow, step execution = activity.

**External state artifacts for context persistence across windows.** Anthropic's own long-running agent harness uses `claude-progress.txt`, feature list JSON, and git history. The agent saves its plan to files because context gets truncated. This IS the Hive's self-compressing model — artifacts feed future context assembly.

**Approval gates via suspend/resume.** Inngest and Restate pause execution during human approval with zero compute cost. The execution is suspended, a notification is sent, and it resumes when the human responds. No polling, no active wait.

**YAML-defined workflows with AI agent steps.** Kestra demonstrates: YAML workflow definitions that include AI agent decision steps. Declarative structure for the workflow; dynamic decisions within steps. Git-versionable.

### Proven to Fail

**Pure agent autonomy without grounding.** AutoGPT, BabyAGI. Agents without deterministic guardrails, state management, and external grounding hallucinate, loop, and destroy wallets.

**CrewAI at scale.** Teams spend 3-6 months building, hit limitations, face 50-80% rewrite. Beginner-friendly but doesn't scale to complex workflows.

**LangGraph + Redis for persistence.** Grid Dynamics case study: "incredibly brittle in practice." Cache conflicts, stale state, custom retry logic. Migrated to Temporal.

**Polling as the only event mechanism.** "Polling tax" — wastes 95% of API calls, never achieves real-time responsiveness, burns quotas.

**Single-framework commitment before understanding needs.** The CrewAI migration problem. Starting with the lightest viable approach and escalating is better than committing to a heavy framework early.

---

## 5. The Simplest Architecture That Could Work

### Core Principle

A blueprint is a YAML file with steps. A runner reads the YAML, executes steps in order, persists state to MongoDB, and creates Hive knowledge records from outputs. That's it. Everything else is additive complexity.

### V1: Sequential Runner + YAML Definitions

**Blueprint definition: a YAML file in `hive/blueprints/`.**

```yaml
name: morning-consultation
description: Daily morning planning briefing
schedule: "0 7 * * 1-5"  # 7am weekdays, via Claude Code desktop tasks
domains: [indemn, career-catalyst, personal]

steps:
  - id: sync
    type: cli
    command: "hive sync"
    description: "Sync all external systems"

  - id: gather
    type: session
    objective: "Gather context using morning playbook"
    playbook: systems/hive/playbooks/morning.md
    autonomous: true

  - id: review
    type: session
    objective: "Present briefing for interactive review"
    context_from: [gather]
    autonomous: false  # human drives this step

  - id: checkpoint
    type: cli
    command: "hive create session_summary '${TITLE}' --domains ${DOMAINS}"
    description: "Save session summary"
```

**Blueprint execution state: a document in a `blueprint_executions` MongoDB collection (NOT the `records` collection).**

```json
{
  "execution_id": "morning-2026-03-24",
  "blueprint": "morning-consultation",
  "status": "running",
  "started_at": "2026-03-24T07:00:00Z",
  "steps": [
    {"id": "sync", "status": "completed", "started": "...", "ended": "...", "duration_s": 45},
    {"id": "gather", "status": "completed", "started": "...", "ended": "...", "cost_usd": 0.12, "session_id": "abc"},
    {"id": "review", "status": "waiting_for_human", "started": "...", "session_id": "def"},
    {"id": "checkpoint", "status": "pending"}
  ]
}
```

**The runner: a Python script (~300-500 lines) that:**

1. Reads the YAML definition
2. Creates an execution document in MongoDB
3. Iterates through steps sequentially
4. For `cli` steps: runs `subprocess.run()`, captures exit code and output
5. For `session` steps with `autonomous: true`: spawns via Agent SDK `query()` (reusing dispatch engine's pattern)
6. For `session` steps with `autonomous: false`: spawns via session manager `session create`, waits for session close
7. Updates execution state in MongoDB after each step
8. On completion: creates a Hive knowledge record summarizing the execution
9. On failure: updates step status, stops (or continues depending on `on_failure` config)
10. On crash and restart: reads execution state from MongoDB, resumes from last incomplete step

**What this gives you:**
- Sequential execution with state persistence (crash recovery)
- Two step types: CLI commands and Claude Code sessions (autonomous or interactive)
- Scheduling via Claude Code's native desktop/cloud tasks
- Observability via the execution state document (queryable, displayable on Wall)
- Self-compressing: each execution produces a Hive summary record
- Blueprint definitions are git-tracked YAML files
- Simple blueprints remain simple

**What this deliberately omits (future work):**
- Parallel fan-out (v2 — use Claude Agent Teams or asyncio.gather)
- Conditional routing (v2 — add `if` conditions on step definitions)
- Sub-blueprints (v2 — a step type `blueprint` that invokes another definition)
- Event-driven triggers (v2 — use Claude Code Channels)
- LangGraph integration (v3 — only if custom runner proves insufficient for complex workflows)
- Per-step permission granularity (v2 — different `allowed_tools` per step)
- Notifications (v2 — Slack ping when a step enters `waiting_for_human`)
- Resource locking (v2 — advisory locks on repos)
- Execution record display on the Wall (v1.5 — add blueprint execution tile type to the UI)

### The Type/Tag Decision

**Blueprint definitions: knowledge records tagged `blueprint`.** They are YAML-heavy markdown files in `hive/blueprints/`, git-tracked, indexed to MongoDB. They are discovered through search and tag filtering, not through structured entity queries. A session can read the file and follow it. No new entity type needed.

**Blueprint executions: a separate MongoDB collection `blueprint_executions`.** Not entity records. Not knowledge records. Operational state, like session state files. Queryable for observability. Summarized as Hive knowledge records on completion. This avoids polluting semantic search with execution noise.

### Why Not LangGraph for V1

LangGraph solves problems V1 doesn't have (parallel branches, conditional edges, subgraph composition). It adds problems V1 doesn't need (LangChain dependency, memory overhead, debugging opacity, async MongoDB checkpoint issues). The V1 runner is ~400 lines of Python — less than the existing dispatch engine. If V1 proves insufficient for complex workflows, LangGraph (or Temporal, or Inngest) can be evaluated for V2 with real usage data, not theoretical requirements.

### Why Not Claude Agent Teams for V1

Agent Teams are experimental (March 2026), and the coordination model (shared task lists, teammate-to-teammate communication) is richer than V1 needs. V1 steps are sequential. Teams become relevant when parallel fan-out is needed (V2).

### Migration Path

1. Build the V1 runner alongside the dispatch engine (coexistence)
2. Convert the morning consultation playbook to a YAML blueprint (first blueprint)
3. Convert weekly summary, call-prep to YAML blueprints
4. Once V1 is proven, migrate dispatch's ralph loop to a blueprint pattern
5. Deprecate the dispatch engine
6. Add parallel/conditional/sub-blueprint capabilities as needed (V2)

---

## 6. Open Questions

**1. Scheduling mechanism.** Claude Code's desktop tasks, cloud tasks, and `/loop` cover different durability tiers. Which tier is right for recurring blueprints? Desktop tasks require the app to be open. Cloud tasks require network access. Can the runner itself be scheduled via launchd/cron and just invoke `python3 runner.py run morning-consultation`?

**2. Human-in-the-loop notification.** When a step enters `waiting_for_human`, how is Craig notified? Slack message? macOS notification? Just a Wall tile change? This determines whether autonomous blueprints can block on human input at all, or whether blocking steps must be interactive-only.

**3. Resource locking for concurrent execution.** Two blueprints targeting the same repo need coordination. Advisory locks in MongoDB? File locks? A simple "one execution per repo at a time" rule? The concurrency model must be explicit before parallel execution is added.

**4. Execution record retention policy.** A daily blueprint produces 365 execution documents/year. Weekly health checks produce 52. When are old executions archived or deleted? Is there a TTL? Does the Hive's monthly archival process cover this?

**5. The Agent SDK's reliability.** The monkey-patched message parser, the `output_format` failures during rate limits, and the general SDK immaturity are risks. Is the SDK stable enough for production autonomous execution? Should the `claude -p` CLI be the fallback for V1?

**6. Session cleanup for recurring blueprints.** Each autonomous step creates state artifacts (session state files, potentially worktrees). 365 daily runs = 365+ state files, 365+ worktrees. The cleanup mechanism is undefined. Auto-cleanup after successful execution? TTL on state files?

**7. Blueprint definition format details.** How are step inputs/outputs declared? How does a step reference output from a previous step (`context_from: [gather]`)? Is there variable interpolation in commands? What's the schema validation story?

**8. The skill-blueprint relationship.** Skills like code-dev and brainstorm-hive are `user-invocable: false` auto-invoked instructions. Blueprints are executable YAML with step definitions. Do skills remain for interactive guidance while blueprints handle orchestrated execution? Or do blueprints absorb skills?

**9. Domain scoping for autonomous blueprints.** An Indemn deployment blueprint should not create records in the personal domain. Is this enforced by the runner, by the Hive CLI, or by convention? The current system has no domain-level access control.

**10. How does the Wall show blueprint execution?** A new tile type? A special rendering of workflow entities? Inline step progress? The UI data pipeline (200-record limit, 30-second polling) may need adjustment for real-time execution visibility.
