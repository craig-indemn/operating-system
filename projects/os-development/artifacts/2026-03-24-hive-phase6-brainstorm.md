---
ask: "Brainstorm the next phase of the Hive — what does it need to become Craig's single operating system for all work and life?"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-a
sources:
  - type: session
    description: "Voice brainstorming — Craig walking through vision, daily workflow, new concepts"
  - type: design
    description: "Builds on 2026-03-08-hive-design.md (phases 1-5 complete)"
---

# Hive Phase 6 Brainstorm — The Agentic Operating System

## The Core Model

The Hive is the harness for a swarm of bees (Claude Code sessions) that do work and create honey (knowledge, code, output). As work is done, notes are created which are interconnected. Information flows in, gets organized and processed, enables execution of tasks, which create more notes in the Hive.

**Three layers:**
- **Inputs** — briefs from external systems (Linear, email, calendar, Slack, etc.). Everything must flow into the Hive.
- **Processing** — context curation, task execution via sessions, knowledge creation as byproduct
- **Outputs** — deployed artifacts in many forms (code, docs, emails, blog posts, messages, newsletters, mockups). At the end of the day, everything is files being deployed somewhere.

## Sessions as the Primitive

Sessions are the underlying primitive of Hive workflows. Every piece of work happens through a session. Key properties:

1. **Context curation enables session start/resume** — the two concepts of (a) sessions and (b) context curation allow starting and resuming without losing context.
2. **Self-compressing system** — as a workflow executes, artifacts are created in the Hive. When context is curated afterwards for the next session, those artifacts get hydrated in. It's a self-curating system where you dump linked artifacts as you go that paint the full picture.
3. **Not all sessions are interactive** — increasingly, workflows will execute without a human in the loop. But by nature of those processes, the Hive is updated.
4. **Scheduling** — workflows should be schedulable. Claude Code now has cron/scheduling capabilities via a command that should be explored.

## Blueprints

A new concept: **blueprints** are execution plans for Claude Code sessions.

A blueprint is essentially a skill-defined runbook — an algorithm for how to accomplish a task using Hive systems (sessions, CLI, search, context curation). The Hive CLI is the interface the agent uses.

**Two types:**
- **One-time blueprint** — a specific migration task, a feature build, a particular codebase change. Executed once.
- **Repeatable blueprint** — agnostic to a specific codebase. Executed daily, weekly, on schedule. Examples: morning consultation, weekly summary, sync operations, content pipeline stages.

**Execution involves:**
- Sub-tasks via task lists to outline the plan in detail
- Sometimes the plan is the same every time (repeatable) — a plan file + Hive context hydration executes on repeat
- The blueprint defines the algorithm; the session executes it

## Threads (Workflow Executions)

A thread is a workflow execution — a state machine of steps (nodes) executed in order to achieve a task.

**Implementation should be dual:**
1. **Workflow object** — create a note, workflow created/updated over time as tasks execute
2. **Skill-defined runbook** — describes how to accomplish the task using Hive primitives (sessions, CLI, search, context)

## Craig's Daily Reality

~15 big-picture ideas/projects, continually driving work across them. Typically 3-5 sessions active simultaneously, each centered on a project/idea/task. With 1M token context windows, sessions can run beginning-to-end without compaction.

**What matters most:** When opening a session, context is curated correctly. The session understands:
- Where the repos are for that particular thing
- What's happening in Craig's life
- Recent messages received
- Calls he's been on
- Deliverables due
- Tasks being worked on
- Code being pushed
- Messages being sent
- Documents being created
- Blogs planned
- Cadence for recurring things

Everything in one place — work and personal. No distinction.

## Output Types

Everything is ultimately files being deployed. The deployment location varies:
- Code pushed to a repository (feature, service, infrastructure)
- Google Doc landing in Drive, shared with someone
- Message sent to Slack
- Email sent
- Blog post deployed to blog site
- Newsletter deployed to newsletter site
- Product showcase deployed to website
- Mockups or wireframes deployed to a site

## The Vision

A Bloomberg terminal for everything happening simultaneously. But start simple and grow.

**Automate things that take time. Enable things never possible before:**
- Research capability at scale
- Parallel work on multiple things
- Being a founder, CEO, CTO, good dad simultaneously
- Managing everything happening in life
- Eventually all through voice — talk to the Hive while running, accomplish everything

**The Hive should:**
- Prepare for the day
- Show everything happening at once
- Execute work autonomously when possible
- Update itself as work happens
- Curate context for every new session
- Deliver outputs to the right places
