---
name: beads
description: Task tracking with first-class dependencies, epics, acceptance criteria, and dispatch integration. Use when creating tasks, breaking down work, managing epics, checking what's ready, or preparing work for dispatch.
argument-hint: [ready | create | epic | status | graph]
---

# Beads Task Tracking

Lightweight issue tracker with first-class dependency support, hierarchical epics, acceptance criteria, and workflow automation. Beads are scoped per-project — always `cd` into the project directory before running `bd` commands.

## Status Check

```bash
which bd && bd --version && echo "BEADS OK" || echo "BEADS NOT INSTALLED"
```

## Core Concepts

- **Beads** are tasks with status, priority, dependencies, and acceptance criteria
- **Epics** are parent beads with children — used as dispatch containers
- **Dependencies** control ordering — a blocked bead can't be worked until its blockers close
- **Ready** means open + unblocked + not deferred — the next thing to work on
- Beads are scoped per-project: each project has its own `.beads/` database
- IDs are prefixed by project (e.g., `os-development-a1b`)

## Commands

### See what's ready: `/beads ready`

```bash
bd ready                          # Top 10 ready tasks
bd ready --pretty                 # Tree format with status symbols
bd ready --parent <epic-id>       # Ready tasks within an epic
bd ready -p 0                     # Only P0 (critical)
bd ready --unassigned             # Unclaimed work
```

### Create a task: `/beads create`

```bash
# Simple task
bd create "Fix login redirect bug" -p 1

# Task with acceptance criteria (required for dispatch)
bd create "Add scoring table component" \
  --acceptance "Component renders rubric items with pass/fail indicators" \
  -d "Create a React component that displays evaluation scoring results"

# Task with dependencies
bd create "Wire scoring into eval view" \
  --deps "os-development-a1b,os-development-a2c" \
  --acceptance "Clicking eval shows scoring tab with real data"

# Task with due date
bd create "Ship demo to client" --due "next friday" -p 0

# Quick capture (returns just the ID)
bd q "Investigate memory leak in bot-service"
```

### Create an epic (dispatch container): `/beads epic`

An epic groups related tasks. For dispatch, the epic IS the spec — its children are the tasks the engine executes.

```bash
# Create the epic
bd create "Scoring UI for evaluations" \
  --type epic \
  --notes "target_repo: /Users/home/Repositories/indemn-platform-v2" \
  --acceptance "All tests pass AND scoring UI renders correctly" \
  -d "Build the scoring table component and wire it into the evaluation detail view"

# Create children under the epic
bd create "Create ScoringTable component" \
  --parent <epic-id> \
  --acceptance "Component renders rubric items with pass/fail indicators" \
  -d "React component displaying evaluation scores with Tailwind styling"

bd create "Add score calculation logic" \
  --parent <epic-id> \
  --acceptance "Score percentage calculated correctly from rubric results" \
  -d "Calculate and display overall score from individual rubric items" \
  --deps "<first-child-id>"

bd create "Wire into evaluation detail view" \
  --parent <epic-id> \
  --acceptance "Clicking an eval shows scoring tab with real data from API" \
  -d "Integrate ScoringTable into the existing evaluation detail page" \
  --deps "<first-child-id>,<second-child-id>"

# View the epic structure
bd children <epic-id> --pretty
bd graph <epic-id>
```

**Dispatch flow:** After creating the epic + children → `/dispatch <epic-id>`

### Bulk create from markdown: `/beads create --file`

Create multiple tasks from a markdown file:

```bash
bd create -f tasks.md --parent <epic-id>
```

Markdown format:
```markdown
# Task Title
Description text here.

**Acceptance:** What defines done.

---

# Another Task Title
Another description.

**Acceptance:** Another criteria.
```

### View a task: `/beads show`

```bash
bd show <id>                     # Full details
bd show <id> --json              # Machine-readable
bd show <id> --children          # Show children only
bd show <id> --refs              # Issues referencing this one
```

### Update a task: `/beads update`

```bash
bd update <id> --status in_progress    # Start working
bd update <id> --claim                 # Atomically claim (assign + in_progress)
bd update <id> --acceptance "Updated criteria"
bd update <id> --append-notes "Found edge case in auth flow"
bd update <id> -p 0                    # Escalate priority
bd update <id> --add-label "dispatch,urgent"
```

### Close a task: `/beads close`

```bash
bd close <id>                          # Mark done
bd close <id> -r "Completed and verified"
bd close <id> --suggest-next           # Show newly unblocked tasks
```

### Dependencies: `/beads deps`

```bash
bd dep add <blocked-id> <blocker-id>   # blocked-id waits for blocker-id
bd dep remove <blocked-id> <blocker-id>
bd dep list <id>                       # Show deps and dependents
bd dep tree <id>                       # Full dependency tree
bd dep cycles                          # Detect circular deps
bd dep relate <id1> <id2>              # Bidirectional "relates-to" link
```

### Search and filter: `/beads search`

```bash
bd search "scoring"                    # Full-text search
bd list --status open --type epic      # All open epics
bd list --label dispatch               # Labeled tasks
bd list --overdue                      # Past due date
bd list --parent <epic-id> --all       # All children including closed
bd count --by-status                   # Counts grouped by status
bd count --by-priority                 # Counts grouped by priority
```

### Labels: `/beads label`

```bash
bd label add dispatch <id>             # Tag for dispatch
bd label add urgent <id>
bd label remove dispatch <id>
bd label list-all                      # All labels in use
bd list --label dispatch               # Find labeled tasks
```

### Comments: `/beads comments`

```bash
bd comments <id>                       # View comments
bd comments add <id> "Found root cause — the auth middleware strips the session token"
```

### Visualize: `/beads graph`

```bash
bd graph <id>                          # Dependency graph for a task
bd graph --all                         # All open issues
bd graph --compact                     # Tree format, one line per issue
bd list --pretty                       # Tree view with status symbols
```

### Project status: `/beads status`

```bash
bd status                              # Database overview and stats
bd epic status                         # Epic completion percentages
bd blocked                             # Show all blocked tasks
bd stale                               # Tasks not updated in 30+ days
bd stale -d 7                          # Not updated in 7+ days
```

### Lint (quality check): `/beads lint`

```bash
bd lint                                # Check tasks for missing required sections
bd lint --type epic                    # Check epics for Success Criteria
```

Required sections by type:
- **bug**: Steps to Reproduce, Acceptance Criteria
- **task/feature**: Acceptance Criteria
- **epic**: Success Criteria

## Dispatch Integration

The path from conversation to autonomous execution:

```
1. Work on a project, discuss what needs building
2. /beads epic → create epic with --repo and --acceptance (backstop)
3. Create children under the epic with per-task --acceptance criteria
4. /beads lint → verify all tasks have acceptance criteria
5. /dispatch <epic-id> → engine grinds through tasks autonomously
```

**Key fields for dispatch:**
- `--notes "target_repo: /path"` on the epic — tells the engine where to run code
- `--acceptance` on each child — what the verification session checks
- `--acceptance` on the epic — backstop criteria for the overall work
- Dependencies between children — engine respects ordering

## Advanced Features

### Defer (snooze)

```bash
bd defer <id> --until "next monday"    # Hidden from bd ready until then
bd defer <id> --until "+2d"            # Defer 2 days
bd undefer <id>                        # Restore immediately
```

### Estimates

```bash
bd create "Build API endpoint" -e 120  # 120 minutes estimate
bd update <id> -e 60                   # Revise estimate
```

### External references

```bash
bd create "Fix issue" --external-ref "gh-42"    # Link to GitHub issue
bd create "Port from Linear" --external-ref "LIN-123"
```

### Molecules (workflow templates)

Molecules are reusable workflow templates with sequenced steps and gates.

```bash
bd formula list                        # Available workflow templates
bd formula show <name>                 # View template details
bd mol pour <formula> --title "Sprint 1"  # Instantiate workflow
bd mol progress <mol-id>              # Workflow progress
bd mol current <mol-id>               # Current step
```

### Gates (async coordination)

Gates block workflow steps until a condition is met.

```bash
bd gate list                           # Open gates
bd gate check                          # Evaluate all open gates
bd gate resolve <id>                   # Manually close a gate
```

Gate types: `human` (manual), `timer` (time-based), `gh:run` (CI), `gh:pr` (PR merge), `bead` (another task)

### Swarms (parallel epic coordination)

```bash
bd swarm create <epic-id>              # Create parallel swarm from epic
bd swarm status                        # Swarm progress
```

## Conventions

- Always `cd` into the project directory before running `bd` commands
- Use `--acceptance` on every task destined for dispatch
- Use `--type epic` + `--repo` for dispatch containers
- Priority scale: P0 (critical) → P4 (nice-to-have), default P2
- Use `bd q` for quick capture during conversation, fill in details later
- Use `--suggest-next` when closing tasks to surface newly unblocked work
