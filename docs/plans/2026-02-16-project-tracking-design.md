# Design: Project Tracking System

**Date:** 2026-02-16
**Status:** Approved

## Problem

Claude Code sessions are ephemeral. When a session ends, all context about what was done, why, and what's next disappears. Resuming work requires re-explaining everything. There's no trail of decisions, no organized artifacts, and no way to look back at how we got from A to B.

## Design Principles

- The operating system is the **command center** — where thinking, decisions, and orchestration happen
- Service repos hold code; the OS holds the *why* behind the code
- Artifacts are distilled outputs, not raw data dumps
- Logging is manual but lightweight — save what matters, skip the noise
- The system should enable retrospective analysis to improve skills over time

## Structure

```
projects/
  <workstream>/
    INDEX.md              # The resume file — status, links, artifacts, decisions
    artifacts/
      YYYY-MM-DD-<slug>.md
    .beads/               # Beads task tracker scoped to this project
```

### Workstreams vs. Projects

Workstreams are the default container — ongoing areas of work (Johnson Insurance, Series A, Platform Development). Discrete projects with a clear start/end can spin out of a workstream or exist on their own.

## INDEX.md — The Resume File

The single file Claude reads when resuming a workstream. Must be scannable by a human and parseable by Claude in one read.

```markdown
# Workstream Name

One-paragraph description of what this workstream is about.

## Status
Current state. What happened last session. What's next.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| ... | Google Doc | [link](...) |
| ... | Slack channel | #channel |
| ... | GitHub repo | org/repo (branch: feature) |
| ... | MongoDB | org_id: ... |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| YYYY-MM-DD | [slug](artifacts/YYYY-MM-DD-slug.md) | The question that prompted this |

## Decisions
- YYYY-MM-DD: Decision made and brief rationale

## Open Questions
- Unresolved question or uncertainty
```

### Resume Flow
1. User says "let's work on X"
2. Claude reads `projects/X/INDEX.md`
3. Claude runs `bd ready` in the project's beads directory
4. Claude gives brief status and asks where to pick up

### Maintenance
INDEX.md is updated incrementally at the end of a working session. Status section gets refreshed, new artifacts/decisions/links added. Should take ~30 seconds.

## Artifact Format

```markdown
---
ask: "The question or task that prompted this artifact"
created: YYYY-MM-DD
workstream: workstream-name
session: YYYY-MM-DD-a
sources:
  - type: google-drive|google-doc|postgres|mongodb|slack|github|etc
    description: "What was queried or pulled"
  - type: google-doc
    ref: "https://..."
    name: "Document Name"
---

# Artifact Title

[Distilled, useful content — not raw API responses]
```

**Key fields:**
- `ask` — The *why*. Most important field. What question or task warranted this artifact's existence.
- `sources` — Provenance. Where the raw data came from.
- `session` — Groups artifacts produced in the same working session.
- Body — Distilled output. Organized, summarized, useful.

**Creation:** Manual but lightweight. When a session produces something worth keeping, save it as an artifact. Can be triggered by asking Claude to "save this as an artifact."

## Beads Integration

Each workstream gets its own beads instance for scoped task tracking.

```bash
cd projects/<workstream> && bd init
bd create "Task description" -p <priority>
bd dep add <child> <parent>   # dependency tracking
bd ready                       # what's unblocked
```

**Layer responsibilities:**
- **INDEX.md** — Where are we and why (narrative)
- **Artifacts** — What did we produce (outputs)
- **Beads** — What needs doing next (tasks)

## The `/project` Skill

A skill that ties the system together:

- `/project <name>` — Resume a workstream. Reads INDEX.md, runs `bd ready`, shows status.
- `/project new <name>` — Scaffold directory, INDEX.md template, init beads.
- `/project save <slug>` — Save current output as artifact with metadata, update INDEX.md.
- `/project status` — Quick view across all workstreams (reads every INDEX.md Status section).
- `/project close-session` — End-of-session: update INDEX.md status, commit changes.

## Documentation Updates

The following files need to be updated so the OS knows about the project system:

- **CLAUDE.md** — Add Projects section to the skill table and context hydration table
- **conventions.md** — Add project conventions (naming, artifact format, when to save)
- **context-and-next-steps.md** — Add to "What's Built" section

## Skill Improvement Feedback Loop

Project logs enable retrospective analysis:
- Which skills are used most? Where is there friction?
- What steps repeat across projects that could be automated?
- What external resources keep getting looked up that should be in a skill reference?

The `ask` + `sources` metadata on artifacts provides the data: what we were trying to do, and what tools we used. This is exactly what's needed to spot skill gaps and drive improvement.
