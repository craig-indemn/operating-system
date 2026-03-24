---
ask: "Define the problem the Hive blueprint system needs to solve — all situations, constraints, and requirements"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-a
sources:
  - type: session
    description: "Brainstorming session — blueprint design for the Hive agentic OS"
  - type: design
    description: "Builds on 2026-03-08-hive-design.md, 2026-03-24-hive-phase6-brainstorm.md"
---

# Blueprint System — Problem Statement

## What We're Solving

Craig operates ~15 ongoing projects/ideas simultaneously, facilitated through 3-5 active Claude Code sessions at any time. Every piece of work — code, content, research, communication, operations — flows through sessions. The Hive is the knowledge/awareness layer that connects everything.

**The gap:** Sessions are islands. Each starts blank. There's no way to define a repeatable workflow, schedule it, track its execution, or observe what happened. Work that follows a known pattern (morning planning, content creation, feature development, data analysis) is re-discovered every time instead of being encoded and automated.

## What a Blueprint Is

A blueprint is an executable workflow definition. It encodes: "here's how to accomplish this type of work" — the steps, what context each step needs, what each step produces, and where the output goes.

**Key properties:**
- **Spectrum of automation:** Fully interactive (human drives every step) → hybrid (human drives some, autonomous for others) → fully autonomous (runs on schedule, no human)
- **Session-count agnostic:** May execute in a single session or span many. State lives in the Hive, not the session. If a session ends, another can resume from where the Hive says we are.
- **Self-compressing:** As execution proceeds, artifacts are created in the Hive. These artifacts feed context assembly for subsequent steps or future executions. The blueprint generates its own institutional memory.
- **Fractal:** A blueprint step can be a sub-blueprint. A "feature lifecycle" blueprint's "implementation" step could itself be a blueprint with design → code → test → deploy sub-steps.
- **Harness-agnostic:** Steps can execute via Claude Code sessions, Python scripts, CLI commands, LangGraph agents, or any other harness. The execution primitive is a tmux terminal (Hive session) — anything that can run in a terminal can be a step.

## Situations It Must Handle

### 1. Interactive daily workflows
Craig opens a session to work on a project. The blueprint provides structure: gather context (step 1), understand current state (step 2), do the work (step 3), update Hive and commit (step 4). Craig drives it, but the pattern is encoded.

### 2. Scheduled autonomous workflows
Morning consultation runs at 7am weekdays. Sync external systems, compile briefing, surface attention items, write context note. No human needed until the briefing is ready to review.

### 3. Complex multi-step workflows
Content creation: extract ideas → draft → refine with feedback → publish → cross-post. Each step may be a separate session. Some steps need human approval (review draft), others are autonomous (deploy to blog).

### 4. Parallel fan-out
Analyze 10 Slack channels, process 1000 meeting transcripts, review 50 PRs. The blueprint spawns parallel sub-executions, collects results, consolidates.

### 5. Mixed harness execution
Step 1: Python script ingests data from API. Step 2: Claude Code session analyzes the data. Step 3: CLI command deploys the output. Step 4: Notification sent via Slack.

### 6. Long-running multi-session workflows
Feature development across 20+ sessions over weeks. The blueprint tracks: design phase (sessions 1-8), review phase (sessions 9-13), implementation (sessions 14-18), testing, deployment. Each session creates artifacts that feed the next.

### 7. System-building
"I want to build a market analysis system." One session creates the blueprint, the system scaffolding, the CLI, and schedules the first execution. The blueprint itself becomes a reusable capability.

### 8. Ad-hoc work becoming blueprints
Craig works on something new interactively. The pattern emerges. The work artifacts and decision trail become the basis for a blueprint that can be re-executed or scheduled.

## Requirements

### Execution
- Steps execute via different harnesses (Claude Code, Python, CLI, sub-blueprint)
- Parallel execution within a blueprint (fan-out/fan-in)
- Conditional routing (if step 2 fails, skip to step 5)
- Human-in-the-loop at any step (interactive mode, notification when input needed)
- Crash recovery (resume from last completed step)

### Observability
- Infrastructure-level tracing, not self-reported by the executing session
- See what's executing, what's scheduled, what's completed, what failed
- Token usage, duration, cost per step and per execution
- Full execution history with artifacts produced
- Visible on the Hive Wall as tiles

### State & Knowledge
- Execution state persisted in the Hive (not in session memory)
- Artifacts created during execution are Hive records (self-compressing)
- Context assembly pulls relevant execution history for new sessions
- Workflow entities track long-running multi-session work

### Integration
- Blueprints can use any Hive skill (CLI tools, APIs, databases)
- Blueprints can be scheduled (cron or event-triggered)
- Blueprints belong to systems but can use multiple systems
- The Hive CLI should be the primary interface for agents executing blueprint steps
- Compatible with future harness changes (LangGraph, direct API, etc.)

### Simplicity
- Simple blueprints should be simple to define and run
- Complexity only when needed (don't require LangGraph for a 3-step workflow)
- Use existing OS primitives where possible (skills, sessions, CLI)
- A single session should be able to read a blueprint and follow it

## Decisions Already Made
- Skills = atomic capabilities; Blueprints = executable workflows
- Playbooks are absorbed as the context-assembly step of blueprints
- Dispatch is replaced by the blueprint execution framework
- Tracing is infrastructure-level (the runner observes), not self-reported
- LangGraph is the orchestration engine for complex blueprints
- Blueprint state lives in the Hive, not in sessions — session-count agnostic
