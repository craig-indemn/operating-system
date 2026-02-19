---
name: project
description: Resume, create, and manage workstream projects — persistent context, artifacts, and task tracking across sessions. Use when the user mentions a project by name, asks to pick up where they left off, wants to save work as an artifact, or asks about project status.
argument-hint: [project-name | new <name> | save <slug> | status | close-session]
---

# Project Tracking

Persistent project state across Claude Code sessions. Each workstream has an INDEX.md (narrative context), artifacts (distilled outputs), and beads (task tracking).

## Status Check

```bash
ls projects/ 2>/dev/null && echo "PROJECTS DIR EXISTS" || echo "NO PROJECTS DIR"
which bd && echo "BEADS INSTALLED" || echo "BEADS NOT INSTALLED"
```

## Commands

### Resume a project: `/project <name>`

1. Read `projects/<name>/INDEX.md`
2. Run `cd projects/<name> && bd ready` to see pending tasks
3. Present a brief status to the user: where we left off, what's next, any open questions
4. Ask where they want to pick up

### Create a new project: `/project new <name>`

1. Create the directory structure:
   ```bash
   mkdir -p projects/<name>/artifacts
   ```
2. Initialize beads:
   ```bash
   cd projects/<name> && bd init
   ```
3. Create INDEX.md from the template below
4. Ask the user to describe the workstream in one paragraph
5. Fill in the Status section with "New workstream. No sessions yet."

### Save an artifact: `/project save <slug>`

1. Determine the current working project from conversation context
2. Write the artifact to `projects/<project>/artifacts/YYYY-MM-DD-<slug>.md`
3. Include the metadata header:
   ```markdown
   ---
   ask: "<the question or task that prompted this output>"
   created: YYYY-MM-DD
   workstream: <project-name>
   session: YYYY-MM-DD-<letter>
   sources:
     - type: <tool-type>
       description: "<what was queried or pulled>"
   ---
   ```
4. The body should be **distilled output** — organized and summarized, not raw API responses
5. Update the Artifacts table in INDEX.md with the new entry

### View all projects: `/project status`

1. List all directories under `projects/`
2. For each, read the `## Status` section from INDEX.md
3. Run `bd ready` in each project's directory to count pending tasks
4. Present a summary table:
   ```
   | Project | Status | Pending Tasks |
   |---------|--------|---------------|
   ```

### Close a session: `/project close-session`

1. Update the Status section of the active project's INDEX.md:
   - What was accomplished this session
   - What the suggested next steps are
2. Add any new decisions to the Decisions section
3. Add any new open questions to the Open Questions section
4. Commit the changes:
   ```bash
   cd <repo-root> && git add projects/<name>/ && git commit -m "project(<name>): close session YYYY-MM-DD"
   ```

## INDEX.md Template

```markdown
# <Project Name>

<One paragraph description of this workstream.>

## Status
New workstream. No sessions yet.

## External Resources
| Resource | Type | Link |
|----------|------|------|

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|

## Decisions

## Open Questions
```

## Artifact Format

Every artifact uses this header:

```markdown
---
ask: "The question or task that prompted this artifact"
created: YYYY-MM-DD
workstream: project-name
session: YYYY-MM-DD-a
sources:
  - type: google-drive|google-doc|postgres|mongodb|slack|github|linear|stripe|airtable|apollo|web
    description: "What was queried or pulled"
  - type: google-doc
    ref: "https://docs.google.com/..."
    name: "Document Name"
---

# Artifact Title

[Distilled, useful content]
```

## Beads Usage

Beads is scoped per-project. Always `cd` into the project directory before running `bd` commands. See `/beads` skill for comprehensive task tracking reference including epics, dependencies, acceptance criteria, and dispatch integration.

## Conventions

- **Artifact slugs**: lowercase, hyphenated, descriptive. E.g. `google-drive-inventory`, `ecm-api-review`, `renewal-requirements`.
- **Session IDs**: `YYYY-MM-DD-a`, incrementing the letter if multiple sessions happen in one day.
- **Distill, don't dump**: Artifacts contain organized, useful summaries. Raw data stays in the tools that produced it.
- **INDEX.md is the source of truth**: If it's not in INDEX.md, it doesn't exist for resume purposes.
- **Commit after close-session**: Project state should be committed so it survives across machines and sessions.
