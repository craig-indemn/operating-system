---
name: code-dev
description: Code development workflow orchestration with Hive checkpointing. Guides design, review, planning, execution, testing, and deployment phases with systematic decision capture. Use when starting a code feature, resuming development work, or at phase transitions.
user-invocable: false
---

# Code Development System

Orchestrates code development workflows across design → review → planning → execution → testing → deployment, with systematic checkpointing to the Hive at every decision point.

**No separate state store.** Composes Hive CLI (workflow state) + beads (tasks) + git (code) + Linear (issues). The Hive workflow entity is the unifying state tracker.

## Starting a Feature

### New feature
```bash
# Create the workflow entity
hive create workflow "<feature name>" \
  --objective "<what we're building and why>" \
  --domains <domain> \
  --refs project:<project-id> \
  --status active

# Check for existing context
hive search "<feature keywords>" --recent 90d
hive refs <project-id> --depth 2
```

### Resuming a feature
```bash
# Read current state
hive get <workflow-id>
# See all connected records
hive refs <workflow-id> --depth 2
# Recent decisions
hive search "<feature>" --tags decision --recent 30d
```

## Checkpointing Patterns

### Decision Checkpoints (during work)

At every design decision, trade-off, or architectural choice:

```bash
hive create decision "<what was decided>" \
  --domains <domain> \
  --refs workflow:<workflow-id>,project:<project-id> \
  --rationale "<why this choice — full reasoning>" \
  --alternatives "<what was considered and rejected>"
```

**What qualifies as a decision checkpoint:**
- Architectural choices (which pattern, which library, which approach)
- Trade-off resolutions (speed vs quality, simple vs extensible)
- Rejected alternatives (what was considered and why it was dropped)
- Scope decisions (what's in, what's deferred)
- Design iterations (previous approach → new approach, why the change)

**Aim for 10-20+ per design session.** More is better. These are the reasoning trail.

### Session Summary (at session close)

```bash
hive create note "<workflow name> session summary" \
  --tags session_summary \
  --domains <domain> \
  --refs workflow:<workflow-id> \
  --body "<what was accomplished, decisions made, what's next>"
```

### Workflow State Update (at session close)

```bash
hive update <workflow-id> \
  --current-context "<phase, progress, blockers, next steps>"
```

## Phase Reference

See `references/phases.md` for per-phase detailed instructions on what to checkpoint and when.

## Context Assembly

When starting a session on a code workflow, the context assembly agent uses the `code-dev` playbook (`systems/hive/playbooks/code-dev.md`) to gather:

1. Full decision trail from the Hive (ALL checkpoints with rationale)
2. Workflow current_context (where things stand)
3. Codebase state (read key files, recent commits)
4. Related workflows and external system data

This is how session 25 knows *why* things were designed the way they are.
