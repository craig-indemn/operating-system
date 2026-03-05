---
ask: "How does Gas Town relate to the OS? Should we adopt it, take inspiration, or stay independent?"
created: 2026-03-04
workstream: os-development
session: 2026-03-04-a
sources:
  - type: medium
    name: "Welcome to Gas Town"
    description: "Steve Yegge's launch post — architecture, stages of AI coding, Mad Max metaphors"
  - type: medium
    name: "Gas Town Emergency User Manual"
    description: "Yegge's workflows — outer/middle/inner loops, crew cycling, PR sheriffs, invisible garden"
  - type: medium
    name: "Welcome to the Wasteland: A Thousand Gas Towns"
    description: "Federation protocol — wanted boards, stamps, character sheets, Dolt-backed reputation"
  - type: github
    ref: "https://github.com/steveyegge/gastown"
    description: "Gas Town repo — 189k lines Go, v0.10.0, 10.9k stars"
  - type: github
    ref: "https://github.com/steveyegge/beads"
    description: "Beads repo — 701 Go files, v0.58.0, 18k stars, Dolt SQL backend"
  - type: web
    description: "Dolt documentation, DoltHub blog posts on agentic memory and agent branching"
---

# Gas Town & Wasteland Research

Research into Steve Yegge's Gas Town multi-agent orchestration system, the Wasteland federation protocol, and Dolt database — how they relate to the Indemn Operating System and where to go next.

## Decision: Use Gas Town Alongside the OS

**Gas Town handles multi-agent code execution. The OS handles intelligence, tools, and operational work.**

They're complementary, not competing:
- Gas Town = engineering orchestrator (run 30 agents on code simultaneously)
- Indemn OS = operational intelligence layer (connect every company tool, track projects, compose workflows)

A Gas Town rig is essentially one piece of the OS — the OS can start a rig via a session, just like it starts any other Claude Code session.

## Gas Town Architecture

### Core Concepts (Mad Max terminology)
| Concept | What It Is | OS Equivalent |
|---------|-----------|---------------|
| Town | Workspace directory (`~/gt/`) | OS repo root |
| Mayor | Primary AI coordinator | EA (Executive Assistant) session |
| Polecats | Ephemeral worker agents | Dispatch sessions (ralph loop) |
| Crew | Persistent named workers | Project sessions |
| Rigs | Project containers wrapping git repos | `--add-dir` repos in sessions |
| Hooks | Git worktree persistence for agent state | Session state files (`sessions/*.json`) |
| Convoys | Work bundles assigned to agents | Beads epics |
| Refinery | Per-rig merge queue (bors-style batch-then-bisect) | No equivalent |
| Deacon | Daemon watchdog (health, stuck detection, restart) | No equivalent |
| Witness | Per-rig polecat lifecycle manager | No equivalent |
| Dogs | Deacon's maintenance crew (Doctor, Reaper, Compactor) | No equivalent |

### How It Works
1. All agents (Mayor, Polecats, Crew, etc.) run as **tmux sessions**
2. Each tmux session runs `claude --dangerously-skip-permissions`
3. Claude Code hooks fire `gt prime` at session start → injects role context, workspace state, mail
4. Agents communicate via mail system (async) and nudges (tmux send-keys)
5. `gt daemon` runs background Go process: Dolt server, health monitoring, stuck detection, auto-restart
6. Work assigned via `gt sling <bead> <rig>` → finds idle polecat, creates worktree, starts session
7. Polecats self-manage completion via `gt done` (push branch, submit MR, go idle)

### Codebase Stats
- **Gas Town**: Go, 189k lines, 1,189 files, v0.10.0, 10.9k stars, 2,400+ PRs merged
- **Beads**: Go, 701 Go files, v0.58.0, 18k stars, Dolt SQL backend (schema v6)
- **100% vibe-coded** — Yegge has never read the code

### Frontend/UI
Gas Town has three UI surfaces (none are full terminal emulators like our OS Terminal):
1. **Web dashboard** — Go html/template + htmx + SSE. Shows Mayor status, Deacon health, convoy progress. No React, no build step.
2. **Terminal UI** — Bubbletea (Go). Convoy management and event feed views.
3. **Markdown rendering** — glamour for styled terminal output.

### Multi-Runtime Support
Not Claude Code exclusive — also supports Codex CLI, Gemini CLI, OpenCode, Cursor, Copilot, Pi.

## Dolt: SQL Database with Git Semantics

### What It Is
A MySQL-compatible database where every Git operation works on tables: clone, branch, commit, merge, diff, push, pull. Written in Go, ships as a single ~100MB binary.

### Why It Matters for Multi-Agent Work
| Problem | Dolt Solution |
|---------|--------------|
| Agents corrupt each other's state | Each agent works on its own branch |
| Need to verify agent work before committing | Data pull requests on DoltHub |
| Agent made a mistake | Instantaneous rollback (pointer move) |
| "Which agent changed this?" | `dolt log` + `dolt blame` |
| Federated collaboration | Push/pull to remotes (Wasteland protocol) |

### Key Properties
- MySQL wire protocol — any MySQL client works
- Cell-level three-way merge (not row or line)
- Prolly Trees (B-Trees + Merkle DAGs) for efficient diffing
- Server mode (`dolt sql-server` on port 3306) for concurrent agent access
- Version control exposed as SQL stored procedures: `CALL dolt_commit(...)`, `CALL dolt_merge(...)`
- Query any historical commit: `SELECT * FROM table AS OF 'abc123'`

### DoltHub
GitHub for databases. Public/private databases, data PRs, clone/push/pull, hosted instances.

### Installation
```bash
brew install dolt
```

### Beads on Dolt
Beads v0.55+ uses Dolt as primary storage (not JSONL):
- Schema v6 with `issues`, `dependencies`, `labels`, `comments`, `events` tables
- One Dolt SQL server per town (port 3307)
- All agents write to `main` with `BEGIN`/`DOLT_COMMIT`/`COMMIT` atomicity
- JSONL is disaster-recovery export only (every 15 minutes)

## Wasteland: Federation Protocol

### Core Idea
Link thousands of Gas Town instances in a trust network. Shared **wanted board** of work. People post ideas, others use their Gas Towns to build them, earn reputation stamps.

### Three Actors
- **Rigs**: Agent instances (can be single agent, Gas Town, or another orchestrator). Each has a handle, trust level, and work history.
- **Posters**: Put work on the wanted board.
- **Validators**: Attest to quality of completed work (requires maintainer-level trust).

### Work Lifecycle
Open → Claimed → In Review → Completed

### Stamps (Reputation)
- Multi-dimensional attestation: quality, reliability, creativity (scored independently)
- Includes confidence level and severity
- Anchored to specific evidence (commit, PR, description)
- **Yearbook rule**: you can't stamp your own work
- Stamps accumulate into a portable, auditable reputation profile

### Trust Levels
1. Registered participant (browse, claim, submit)
2. Contributor (accumulated stamps)
3. Maintainer (can validate others' work — issue stamps)

### Federation
- Anyone can create their own wasteland (team, company, university, OSS project)
- Each wasteland is a sovereign Dolt database with shared schema
- Rig identity is portable across wastelands — stamps follow you
- Dolt's git semantics enable sync without custom conflict resolution

### Built On
- **Dolt** for structured data federation (clone, push, pull on SQL tables)
- **Git PR workflow** for all work types (not just code)
- **DoltHub** for database hosting and collaboration

## Comparison: Gas Town vs Indemn OS

### Gas Town Has, OS Doesn't
- Scale to 20-30 simultaneous agents with role hierarchy
- Dolt SQL backend (queryable, versioned, concurrent-safe)
- Merge queue (Refinery — batch-then-bisect)
- Inter-agent messaging (mail + nudges)
- Daemon watchdog chain (Deacon → Dogs)
- Federation protocol (Wasteland)
- Multi-runtime support (Claude, Codex, Gemini, Cursor, etc.)
- Formulas (30+ TOML workflow templates)

### OS Has, Gas Town Doesn't
- **Terminal UI** — full xterm.js browser-based terminal emulation with remote access
- **Skills architecture** — 15+ SKILL.md files for external tool integration
- **Business tool integration** — Slack, Gmail, Calendar, MongoDB, Stripe, Airtable, etc.
- **Project memory** — INDEX.md with decisions, artifacts, narrative continuity
- **Workflow skills** — `/call-prep`, `/weekly-summary`, `/follow-up-check`
- **Remote access** — Tailscale Serve, token auth, mobile responsive
- **Voice layer** — designed (not built) STT/TTS sidecar

### Complementary Integration Points
1. **OS creates specs → Gas Town executes them**: OS builds well-defined epics, Gas Town swarms 20+ agents to implement
2. **Dolt as OS state backend**: Replace `sessions/*.json` with Dolt tables
3. **Beads is already shared**: Same `bd` tool. Beads epics are the handoff protocol.
4. **OS skills inside Gas Town agents**: SKILL.md files are portable Markdown — any Claude session can load them
5. **Wasteland for multi-user**: When OS supports multiple engineers, Wasteland is the federation model

## Architecture Vision

```
┌─────────────────────────────────────────────────┐
│                 Indemn OS (Brain)                │
│  Skills · Projects · Workflow Intelligence      │
│  /call-prep · /weekly-summary · /eval-analysis  │
│  Slack · Gmail · MongoDB · Stripe · Linear      │
├─────────────────────────────────────────────────┤
│              OS Terminal (Eyes)                  │
│  React + xterm.js · Remote · Mobile · Voice(v3) │
├────────────────────┬────────────────────────────┤
│  Session Manager   │   Gas Town (Hands)         │
│  (lightweight)     │   Mayor · Polecats · Crew  │
│  EA · project      │   Refinery · Convoys       │
│  sessions          │   Multi-agent code work    │
├────────────────────┴────────────────────────────┤
│              Dolt (Memory)                      │
│  Session state · Beads · Agent history          │
│  Queryable · Versioned · Federable              │
├─────────────────────────────────────────────────┤
│              tmux (Substrate)                   │
│  All sessions live here — OS and Gas Town       │
└─────────────────────────────────────────────────┘
```

The OS is the brain (intelligence, tools, decisions). Gas Town is the hands (multi-agent code execution). OS Terminal is the eyes (visual interface). Dolt is the memory (structured, versioned state). tmux is the substrate (everything runs here).

## Action Items

| Action | Priority | Notes |
|--------|----------|-------|
| Install Gas Town (`brew install gastown`) | High | Get familiar with Mayor workflow |
| Install Dolt (`brew install dolt`) | High | Evaluate as state backend |
| Set up a Gas Town rig for one Indemn service repo | High | Test the integration model |
| Evaluate Dolt for OS session state | Medium | Replace `sessions/*.json` |
| Consider Obsidian for project artifacts | Medium | Point at `projects/` for visual browsing |
| Study Wasteland protocol | Low | Future multi-engineer coordination |
| Explore Beads Linear sync | Low | May complement `/linear` skill |

## Open Questions
- Can Gas Town rigs be started/stopped from OS sessions via the session manager?
- Does Gas Town's tmux socket isolation conflict with our session manager's tmux usage?
- If Dolt replaces JSON state files, what's the migration path? Can the OS Terminal's file watcher be replaced with Dolt subscriptions?
- Should Obsidian vault point at the OS repo directly, or should we sync artifacts to a separate vault?
- How does Gas Town's `gt daemon` coexist with our session manager hooks?
