---
ask: "How should Gas Town, Dolt, and Obsidian integrate into the Indemn Operating System?"
created: 2026-03-04
workstream: os-development
session: 2026-03-04-a
sources:
  - type: artifact
    ref: "projects/os-development/artifacts/2026-03-04-gastown-research.md"
    description: "Gas Town / Wasteland / Dolt research — architecture, comparison, action items"
  - type: artifact
    ref: "projects/os-development/artifacts/2026-02-19-dispatch-system-design.md"
    description: "Original dispatch system design — ralph loop, three primitives, SDK findings"
  - type: artifact
    ref: "projects/os-development/artifacts/2026-03-01-ea-session-management-design.md"
    description: "EA & session management design — tmux sessions, event-driven state, switchboard"
  - type: local
    ref: "docs/posts/welcome_to_gastown.txt"
    description: "Steve Yegge's Gas Town launch post"
  - type: local
    ref: "docs/posts/gastown_emergency_manual.txt"
    description: "Yegge's Gas Town workflows and crew patterns"
  - type: local
    ref: "docs/posts/wasteland.txt"
    description: "Wasteland federation protocol post"
---

# Design: Gas Town Integration & OS Evolution

**Date:** 2026-03-04
**Status:** Draft — design conversation, needs refinement before implementation

## Problem

The OS has three primitives: Skills (capabilities), Projects (memory), Systems (processes). We built a custom dispatch engine (ralph loop) for autonomous code execution, but Gas Town is a far more mature multi-agent orchestrator that solves the same problem at larger scale. Meanwhile, our state management (flat JSON files) won't scale, and our project artifacts live only on the local filesystem.

## Core Decision

**Gas Town is the hands. The OS is the brain.**

- Gas Town handles multi-agent code execution (replace our custom dispatch)
- The OS handles intelligence, tools, and operational workflows
- Dolt becomes the shared state layer (eventually)
- Obsidian provides a human-readable view over project knowledge (eventually)

---

## Architecture: The Five Layers

```
┌─────────────────────────────────────────────────┐
│              Indemn OS (Brain)                   │
│  Skills · Projects · Workflow Intelligence       │
│  EA switchboard · Tool integrations              │
├─────────────────────────────────────────────────┤
│              OS Terminal (Eyes)                   │
│  React + xterm.js · Remote · Mobile              │
├────────────────────┬────────────────────────────┤
│  Regular Sessions  │   Gas Town Rigs (Hands)    │
│  (lightweight)     │   Mayor · Polecats · Crew  │
│  EA · research ·   │   Refinery · Convoys       │
│  intelligence work │   Multi-agent code work    │
├────────────────────┴────────────────────────────┤
│              Dolt (Memory)                       │
│  Session state · Beads · Agent history           │
│  Queryable · Versioned · Federable               │
├─────────────────────────────────────────────────┤
│              tmux (Substrate)                    │
│  All sessions live here — OS and Gas Town        │
└─────────────────────────────────────────────────┘
```

### Layer Responsibilities

**OS (Brain)** — Decides what to do. Creates beads epics with acceptance criteria. Chooses whether work needs a single session or a Gas Town swarm. Manages project memory. Runs workflow skills (call prep, weekly summary). Connects to business tools (Slack, MongoDB, Stripe, etc.).

**OS Terminal (Eyes)** — Visual interface for everything. Shows both regular sessions and Gas Town sessions in the same grid. Remote access via Tailscale. Mobile responsive.

**Sessions + Gas Town (Hands)** — Two types of execution:
- Regular sessions: single Claude Code instance for research, intelligence, design work
- Gas Town rigs: Mayor + Polecats + Crew for heavy multi-agent code work

**Dolt (Memory)** — Structured, queryable, versioned state. Replaces flat JSON files. Shared between OS and Gas Town.

**tmux (Substrate)** — Everything is a tmux session. Regular OS sessions and Gas Town agents all live here.

---

## Session Types

### Current: Regular Sessions

```
session create platform-dev --add-dir /path/to/repo
```

Creates a Claude Code instance in a tmux session with a git worktree. Good for:
- Research and exploration
- Design conversations
- Intelligence work (call prep, weekly summaries)
- Light implementation (single-file changes, quick fixes)
- EA orchestration

### New: Gas Town Sessions

```
session create platform-swarm --type gastown --rig platform-v2
```

Creates (or attaches to) a Gas Town rig. The Mayor is the session's primary interface. Good for:
- Multi-file feature implementation
- Large refactors
- Epic execution (10+ tasks)
- Parallel code work across a repo

### How They Relate

The EA (our switchboard session) sits above both types:
- EA can create regular sessions for lightweight work
- EA can create Gas Town rigs for heavy code work
- EA reads results from both via beads and project state
- EA updates INDEX.md regardless of which execution mode was used

A Gas Town Mayor is NOT the EA. The Mayor is a project-specific coordinator — like a team lead for one repo. The EA is the executive who decides what each team works on.

```
EA (switchboard)
├── platform-dev (regular session — design/research)
├── voice-evals (regular session — evaluation analysis)
├── platform-swarm (Gas Town rig)
│   ├── Mayor (coordinator for platform-v2 repo)
│   ├── Polecat: Toast (working on auth refactor)
│   ├── Polecat: Shadow (working on API migration)
│   └── Crew: jack (design review)
└── bot-service-swarm (Gas Town rig)
    ├── Mayor (coordinator for bot-service repo)
    └── Polecats working on LLM provider abstraction
```

### Session Manager Changes

The `session` CLI needs a new session type:

```bash
# Current
session create <name> [--add-dir <repos>] [--model <model>]

# New
session create <name> --type gastown --rig <rig-name> [--repo <git-url>]
```

Under the hood:
1. If the Gas Town rig doesn't exist, run `gt rig add <rig-name> <repo-url>`
2. Start the Mayor: `gt mayor attach` (or equivalent)
3. Register as a session in our state system
4. OS Terminal shows the Mayor's tmux pane in the grid

The regular `session list` command shows both types:
```
NAME              TYPE      STATUS    CONTEXT    AGENTS
platform-dev      regular   active    72%        1
voice-evals       regular   idle      45%        1
platform-swarm    gastown   active    —          8 (1 mayor, 5 polecats, 2 crew)
```

---

## Gas Town as Dispatch Engine

### What We Replace

Our custom dispatch system (`systems/dispatch/engine.py`) used the Agent SDK to:
1. Read a beads epic
2. Pick the next incomplete task
3. Spawn a fresh Claude Code session
4. Run the task
5. Verify in a separate session
6. Mark done or retry
7. Repeat

Gas Town does all of this and more:
- Mayor coordinates instead of a sequential loop
- Polecats are the workers (fresh context per task, like our ralph loop)
- Refinery handles the merge queue (we had no equivalent)
- Deacon monitors for stuck/dead agents (we had no equivalent)
- Convoys batch related tasks (we did one-at-a-time)

### What Changes

| Before (Custom Dispatch) | After (Gas Town) |
|---|---|
| OS creates beads epic | OS creates beads epic (same) |
| OS runs `engine.py` with spec | OS tells EA to start a Gas Town rig |
| Engine spawns sessions via Agent SDK | Mayor slings beads to polecats |
| Engine verifies in separate session | Refinery processes MRs |
| Engine loops until done | Mayor tracks convoy completion |
| Results in learnings file | Results in beads state + git history |

### What We Keep

- **Beads epics as the spec format** — Gas Town uses beads natively. No translation needed.
- **OS creates the specs** — the intelligence to decompose work into tasks stays in the OS.
- **Verification standards** — we can define verification criteria in the epic's acceptance criteria.
- **Project memory** — OS still updates INDEX.md with results.

### What We Retire

- `systems/dispatch/engine.py` — replaced by Gas Town's Mayor + Polecats
- The ralph loop concept — Gas Town's parallel execution is strictly better
- Our dispatch skill — replaced with a Gas Town integration skill
- Custom verification sessions — Refinery handles merge verification

### The New Flow

```
1. Working in OS on a project
2. Build a well-defined beads epic with acceptance criteria
3. Say "swarm this" (instead of "dispatch this")
4. OS creates a Gas Town rig (or uses existing one for this repo)
5. Mayor picks up the epic, creates convoy, slings to polecats
6. Polecats execute tasks in parallel
7. Refinery merges completed work
8. EA monitors progress, reports back
9. OS updates INDEX.md with results
```

---

## Dolt as State Backend

### Why

Current state (`sessions/*.json`):
- Not queryable (must read all files to answer "which sessions are active?")
- Not versioned (file watcher sees latest state only)
- Not concurrent-safe (two writers can clobber)
- Not federable (single machine only)

Dolt gives us:
- SQL queries on session state
- Full version history (who changed what, when)
- Branch/merge for experiments
- Concurrent access from multiple processes
- Foundation for future federation

### What Needs Careful Thought

**This is not a trivial migration.** Questions to answer before implementing:

1. **Process management.** Dolt runs as a MySQL-compatible server. Who starts it? Gas Town already runs a Dolt server (port 3307) for beads. Do we share it or run a separate one?

2. **Schema design.** What tables? `sessions`, `session_events`, `agent_states`? How does this relate to beads tables? Dolt schema is SQL DDL — need to design it right.

3. **OS Terminal integration.** Currently uses `fs.watch` on `sessions/*.json`. With Dolt, either:
   - Poll SQL queries on an interval
   - Use Dolt's replication/subscription features
   - Keep a thin file-watcher layer that reads from Dolt
   - Use a Dolt trigger/hook mechanism

4. **Session manager hooks.** Currently write JSON files. Would need to write SQL instead. The hooks are Python — `doltpy` or MySQL client.

5. **Backward compatibility.** Can we run both (JSON files + Dolt) during migration? File watcher continues to work while we build Dolt integration.

6. **Gas Town's Dolt instance.** Gas Town runs Dolt for beads. Our OS session state is different data. Options:
   - Same Dolt server, different database
   - Same Dolt server, same database, different tables
   - Separate Dolt server (avoid coupling)

7. **Beads migration.** We currently use beads with JSONL backend. Gas Town uses beads with Dolt backend. When we adopt Gas Town, beads automatically moves to Dolt. But our existing beads data in `projects/*/.beads/` would need migration.

### Recommended Approach

**Phase 1: Don't touch Dolt yet.** Install Gas Town, use it for code work. Gas Town manages its own Dolt instance for beads. OS continues with JSON files.

**Phase 2: Evaluate.** After using Gas Town for a few weeks, understand how Dolt actually works in practice. Observe Gas Town's Dolt usage patterns.

**Phase 3: Design schema.** Design OS-specific tables (sessions, events, etc.) based on real usage patterns.

**Phase 4: Migrate.** Build Dolt integration for the OS, run parallel with JSON files, cut over when stable.

---

## Obsidian Integration

### The Simple Version (Do This First)

Open `projects/` as an Obsidian vault. That's it.

- INDEX.md files become navigable wiki pages
- Artifacts are linked notes with metadata headers
- Decisions sections become searchable
- Cross-references between projects work via relative links
- Zero code changes to the OS

### What This Gives You

- Visual graph of project relationships
- Full-text search across all artifacts and decisions
- Mobile access via Obsidian Sync (optional)
- Backlinks — see which artifacts reference each other
- Daily notes could map to session logs

### Design Considerations for Later

If we want to design the project structure around Obsidian's strengths:

1. **Wikilinks.** Obsidian uses `[[page-name]]` links. Our current artifacts use relative Markdown links `[slug](artifacts/slug.md)`. Both work in Obsidian, but wikilinks enable bidirectional linking.

2. **Tags.** Obsidian's tag system could classify artifacts: `#decision`, `#research`, `#implementation`, `#bug-fix`. Currently we use the `ask` field in frontmatter — could add tags.

3. **Templates.** Obsidian templates could auto-fill artifact metadata headers. Equivalent to our `/project save` but from the Obsidian side.

4. **Canvas.** Obsidian Canvas could visualize architecture (like the five-layer diagram above) as a living document.

5. **Sync scope.** If using Obsidian Sync, decide what to sync:
   - Just `projects/` — lightweight, focused
   - `projects/` + `docs/` — includes design docs and plans
   - Full OS repo — everything, but might be noisy

### Recommended Approach

**Now:** Don't change anything. Focus on Gas Town integration.
**Soon:** Open `projects/` in Obsidian, see how it feels.
**Later:** If it's useful, consider adjusting artifact format for better Obsidian compatibility (tags, wikilinks).

---

## OS Skills in Gas Town

Gas Town agents are Claude Code sessions. Claude Code automatically loads skills from `~/.claude/skills/` (user-level) and `.claude/skills/` (project-level). Gas Town's `gt prime` adds role context on top, but the underlying skill discovery still works.

### Skill Loading by Agent Type

| Agent | Skill Access | Rationale |
|-------|-------------|-----------|
| Mayor | Full OS skills (symlinked to `~/.claude/skills/`) | May need Slack, MongoDB, GitHub, etc. for coordination |
| Crew | Full OS skills | Design work may involve checking external systems |
| Polecats | Repo skills only (`.claude/skills/` in target repo) | Focused code execution — extra skills waste tokens |

### Implementation

**Phase 1:** Symlink essential OS skills to `~/.claude/skills/`:
```bash
ln -s ~/Repositories/operating-system/.claude/skills/mongodb ~/.claude/skills/mongodb
ln -s ~/Repositories/operating-system/.claude/skills/github ~/.claude/skills/github
ln -s ~/Repositories/operating-system/.claude/skills/slack ~/.claude/skills/slack
# ... selective, not all 15+
```

**Phase 2:** Evaluate Gas Town's plugin system (`plugins/` directory). If it provides better per-agent skill scoping than symlinks, migrate OS skill content into Gas Town plugins.

### Key Insight

Most Gas Town agents (especially polecats) don't need most OS skills. A polecat implementing a React component doesn't need Slack access. The convention: **Mayor and Crew get full skills. Polecats get repo-specific only.** This saves tokens and keeps agents focused.

---

## The Dispatch Skill Evolution

The current `/dispatch` skill would evolve:

### Before (Custom Engine)
```
/dispatch → reads spec → runs engine.py → ralph loop → reports results
```

### After (Gas Town)
```
/dispatch → reads epic → creates Gas Town rig (or uses existing) →
            Mayor picks up convoy → polecats swarm → reports results
```

The skill's job changes from "run our engine" to "bridge OS → Gas Town":
1. Read the beads epic and validate it
2. Ensure a Gas Town rig exists for the target repo
3. Create a convoy with the epic's tasks
4. Hand off to the Mayor
5. Monitor progress and report back to the OS
6. Update project state when complete

---

## What We're NOT Changing

- **Skills architecture** — stays as-is. Gas Town has no equivalent.
- **Project memory** — INDEX.md + artifacts pattern stays. Gas Town doesn't do narrative memory.
- **OS Terminal** — stays as our visual interface. Gas Town's htmx dashboard is simpler.
- **Workflow skills** — `/call-prep`, `/weekly-summary`, etc. stay in the OS. Gas Town is code-only.
- **Tool integrations** — Slack, MongoDB, Stripe, etc. stay as OS skills.
- **EA concept** — stays as the switchboard above all sessions including Gas Town.
- **tmux as substrate** — both systems use tmux. They coexist.

---

## Implementation Phases

### Phase 0: Learn (This Week)
- Install Gas Town: `brew install gastown`
- Install Dolt: `brew install dolt`
- Set up a Gas Town workspace: `gt install ~/gt --git`
- Add one Indemn service repo as a rig
- Use Mayor-only mode to get comfortable
- Document learnings

### Phase 1: Side-by-Side (Next 1-2 Weeks)
- Run Gas Town alongside the OS — separate systems, shared beads
- Use Gas Town for one real code task (pick a platform-v2 feature)
- Keep OS session manager and JSON state files unchanged
- Observe: how does the Mayor's workflow feel? How do polecats perform?
- Observe: how does Gas Town's Dolt instance behave?

### Phase 2: Light Integration (2-4 Weeks Out)
- Teach the session manager about Gas Town rigs as a session type
- OS Terminal shows Gas Town Mayor sessions in the grid
- `/dispatch` skill bridges OS → Gas Town
- Symlink key OS skills for Gas Town agent access
- Retire custom dispatch engine (`systems/dispatch/engine.py`)

### Phase 3: Deep Integration (Future)
- Evaluate Dolt for OS state backend
- Design schema, build migration
- Obsidian vault over projects/
- Consider Wasteland federation for multi-engineer (Craig + Cam)
- Gas Town plugins for Indemn-specific workflows

---

## Resolved Design Decisions

### Tension 1: Two tmux worlds → Surface interactive sessions only (Option B)
Register Mayor and Crew as sessions in our state. Polecats, Refinery, Witness, Deacon are Gas Town internals — invisible to OS Terminal. You interact with Mayors and Crew; polecats are fire-and-forget. Swarm status comes from the Mayor or `gt convoy list`, not the terminal grid. Can add polecat visibility later if needed.

### Tension 2: Session lifecycle ownership → Thin delegation (Option C)
The `session` CLI is the unified interface. For regular sessions, it manages directly. For Gas Town rigs, it delegates to `gt` commands. `session create X --type gastown` calls `gt rig add` + `gt mayor attach`. `session close X` calls Gas Town's shutdown. Gas Town's daemon and Deacon handle internal lifecycle (restarts, health, stuck detection). Our session manager doesn't try to manage Gas Town internals.

### Tension 3: State source of truth → JSON now, Dolt later (Option A → B)
Phase 1-2: Keep JSON for OS sessions. Gas Town manages its own Dolt state. OS Terminal merges both sources for a unified view. **Craig's hunch: everything will probably move to Dolt eventually.** Once we understand Dolt through Gas Town usage, migrating OS state to Dolt is likely the right call. Don't rush it — learn first, then migrate with confidence.

### Tension 4: Beads scoping → Gas Town model, one database, prefixed IDs (Option A)
All beads in one Dolt database. Each rig/project gets a prefix (`plat-`, `bot-`, `eval-`). Cross-project queries are trivial ("what's unblocked everywhere?"). Existing per-project JSONL beads migrate to Dolt when Gas Town is adopted. `bd ready` shows everything by default; filter by prefix for project-specific views.

### Tension 5: Skills portability → Selective symlinks by agent type
Gas Town agents are Claude Code sessions — they discover skills from `~/.claude/skills/` automatically. Mayor and Crew get full OS skill access via symlinks. Polecats get repo-specific skills only (no symlinks needed — they just use the target repo's `.claude/skills/`). This keeps polecats focused and token-efficient.

### Tension 6: Cost and concurrency → Two Max subscriptions
Claude Max 5x: ~225 messages per 5-hour window, weekly cap. Max 20x: designed for concurrent sessions. Running 20-30 agents on a single subscription would hit rate limits quickly. **Decision: Craig will purchase a second Max 20x plan** to support concurrent agent workloads. With two subscriptions, realistic capacity is 8-12 concurrent agents before throttling. Full 20-agent swarms may still require token-conscious conventions (Sonnet for polecats, Opus for Mayor/design work).

### Tension 7: EA's Gas Town awareness → Dedicated Gas Town skill
Create a comprehensive `/gastown` skill that is an expert orchestrator of all Gas Town functions and concepts. The EA uses this skill alongside the `/sessions` skill. The `/sessions` skill gets updated to integrate with Gas Town (knows about rig session types, can delegate to `gt` commands). The `/gastown` skill covers: rig management, convoy creation, polecat workflows, Mayor interaction patterns, Dolt/beads integration, troubleshooting.

### Other Decisions
- 2026-03-04: Gas Town replaces custom dispatch engine — more mature, parallel, battle-tested
- 2026-03-04: Gas Town Mayor ≈ project-specific session lead, NOT the EA. EA sits above.
- 2026-03-04: Gas Town is a session type — OS can create/manage Gas Town rigs
- 2026-03-04: Obsidian is additive — open projects/ as vault, no code changes needed
- 2026-03-04: OS keeps: skills, project memory, terminal UI, workflow intelligence, tool integrations
- 2026-03-04: Gas Town gets: multi-agent code execution, merge queue, daemon watchdog
- 2026-03-04: OS is the configuration/intelligence layer; Gas Town is the runtime. OS defines *what*, Gas Town defines *how*.
- 2026-03-04: If Gas Town develops better systems for things the OS does (skills, memory, etc.), adopt them rather than maintaining ours out of pride.
- 2026-03-04: Everything is a session — Gas Town Mayor and Crew appear alongside regular sessions in OS Terminal. Polecats are Gas Town internals, invisible to the OS.
- 2026-03-04: Thinking happens in OS sessions. Execution (swarming) happens in Gas Town rigs. Boundary is fuzzy — Mayor can do design work too.

## Open Questions (Remaining)

1. **tmux socket bridging.** Gas Town uses per-town tmux sockets (`-L` flag). Our session manager uses the default server. When we register Mayor/Crew as OS sessions, we need the OS Terminal to connect to their tmux panes on Gas Town's socket. Does node-pty support connecting to a specific tmux socket? Or do we need to proxy somehow?

2. **Beads migration mechanics.** Existing per-project JSONL beads → one shared Dolt database. What's the actual migration command? Does `bd` support importing from JSONL into Dolt? Do we lose history?

3. **Gas Town daemon coexistence.** `gt daemon` manages Dolt server, health checks, auto-restart. Our session manager has hooks for state tracking. Do they conflict? Can both run simultaneously without interfering?

4. **Permissions per-rig.** Gas Town uses `--dangerously-skip-permissions`. Our OS uses `bypassPermissions` or `acceptEdits`. Can we configure permissions per Gas Town role (e.g., polecats get bypass, crew gets acceptEdits)?

5. **Repo directory layout.** Gas Town expects `~/gt/` as workspace. OS lives in `~/Repositories/operating-system/`. Service repos in `~/Repositories/`. How do rigs reference these? Does `gt rig add` clone into `~/gt/` or can it point to existing checkouts?

6. **Context injection overlap.** Gas Town's `gt prime` injects role context. Our CLAUDE.md hierarchy injects project context. When a Gas Town agent runs in a service repo, both fire. Do they complement or conflict? Is the context window getting stuffed with redundant instructions?

7. **Token efficiency conventions.** With two Max subscriptions, what's the budget discipline? Sonnet for polecats, Opus for Mayor? Max turns per polecat? When does the Mayor escalate vs. retry?

## Resolved Questions

- **Cost management** → Two Max 20x subscriptions. Realistic capacity ~8-12 concurrent agents.
- **Skills in Gas Town** → Symlink OS skills to `~/.claude/skills/` for Mayor/Crew. Polecats use repo skills only.
- **EA integration** → Dedicated `/gastown` skill + updated `/sessions` skill.
- **OS Terminal visibility** → Show Mayor and Crew only. Polecats are invisible Gas Town internals.
