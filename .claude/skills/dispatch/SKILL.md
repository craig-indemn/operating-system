---
name: dispatch
description: Autonomous execution of implementation plans — runs Claude Code sessions via Agent SDK against beads epics. Use when the user wants to dispatch work to another repo, execute a plan autonomously, or run tasks through the ralph loop.
argument-hint: [<epic-id> | status <epic-id> | create]
---

# Dispatch

Execute beads epics autonomously via the Agent SDK. Each child task runs in a fresh Claude Code session with full OS framework (skills, CLAUDE.md, conventions). Verification runs in a separate session.

## Status Check

```bash
test -f systems/dispatch/engine.py && echo "ENGINE EXISTS" || echo "ENGINE MISSING"
/Users/home/Repositories/.venv/bin/python3 -c "from claude_agent_sdk import query; print('SDK OK')" 2>/dev/null && echo "SDK OK" || echo "SDK MISSING"
which bd && echo "BEADS OK" || echo "BEADS MISSING"
```

## Commands

### Execute a dispatch: `/dispatch <epic-id>`

1. Verify the epic exists: `bd show <epic-id> --json`
2. Verify it has `target_repo` in notes and the repo path exists
3. Show the user what will be dispatched:
   - Epic title and backstop acceptance criteria
   - List of child tasks with their acceptance criteria
   - Target repo
4. Confirm with the user before launching
5. Run the engine:
   ```bash
   env -u CLAUDECODE /Users/home/Repositories/.venv/bin/python3 systems/dispatch/engine.py <epic-id> --beads-dir <project-beads-dir>
   ```
6. When complete, read `systems/dispatch/active/summary.md` and present results
7. Offer to save results as a project artifact via `/project save dispatch-results`

### Check dispatch status: `/dispatch status <epic-id>`

1. Run `bd children <epic-id>` to see task statuses
2. If `systems/dispatch/active/learnings.md` exists, show recent learnings
3. Present a summary: how many passed, failed, remaining

### Create a dispatch epic: `/dispatch create`

Help the user create an epic + child tasks interactively from conversation context.

1. Ask what they want to build and which repo to target
2. Break the work into discrete tasks with acceptance criteria
3. Create the epic:
   ```bash
   bd create "<title>" --type epic --notes "target_repo: <target-repo-path>" --acceptance "<backstop criteria>" -d "<description>"
   ```
4. Create child tasks under the epic:
   ```bash
   bd create "<task title>" --parent <epic-id> --acceptance "<acceptance criteria>" -d "<task description>"
   ```
5. Show the full plan: `bd children <epic-id>`
6. Ask if they want to dispatch immediately or refine further

## How It Works

The dispatch engine (`systems/dispatch/engine.py`) is a **ralph loop**:

```
Read epic → Find ready child → Run implementation session → Run verification session → Update beads → Loop
```

- **Fresh context per task** — each task gets its own Claude Code session with managed context
- **Verification by separate session** — independent judgment, not self-verification
- **Beads-native** — tasks are beads, status tracked by beads, dependencies respected
- **Full OS framework** — dispatched sessions load skills and CLAUDE.md via `setting_sources=["user", "project"]`
- **Learnings carry forward** — append-only file grows across tasks, injected as context
- **Git commits on pass** — each passing task gets its own commit in the target repo

## Integration with Projects

Dispatch is project-aware:
- Epic beads live in the project's beads instance
- Context from the project (INDEX.md decisions) can be included in the epic description
- Results can be saved as project artifacts
- The dispatch flow: project work → create spec (epic + tasks) → dispatch → results → update project
