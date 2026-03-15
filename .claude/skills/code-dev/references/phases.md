# Code Development Phases — Checkpoint Reference

## Phase: Design

Iterative brainstorming across multiple sessions. The bulk of context is created here.

**Knowledge to create:**
- Decision checkpoints at every resolved question (full rationale + alternatives)
- Design iteration records (previous approach → new approach, why)
- Research findings (external information brought in)
- Trade-off analyses
- Rejected approaches with reasoning

**Volume:** 10-20+ records per session. This is normal and valuable.

**Commands:**
```bash
# Decision with full context
hive create decision "Use MongoDB for entities, files for knowledge" \
  --domains indemn \
  --refs workflow:hive,project:os-development \
  --rationale "Entities need structured queries as starting points for context assembly. Knowledge is prose that gets discovered through traversal and search." \
  --alternatives "All files with MongoDB index, All MongoDB, Flat wiki notes only" \
  --tags architecture

# Research finding
hive create research "PKM tool comparison — Tana, Obsidian, Notion" \
  --domains indemn \
  --refs workflow:hive \
  --body "Findings from researching existing tools..."

# Update workflow at session end
hive update <workflow-id> --current-context "Design phase session 3. Key decisions: two-layer architecture, 14 CLI commands, type registry. Remaining: UI design, sync framework."
```

## Phase: Design Review

5+ independent sessions each review the design from a fresh perspective.

**Knowledge to create:**
- Review findings (concerns, validations, requested changes)
- Each reviewer's perspective as a separate record

**Commands:**
```bash
hive create note "Design review: API surface" \
  --tags session_summary \
  --domains indemn \
  --refs workflow:<id> \
  --body "Review focused on API surface. Findings: ..."
```

## Phase: Planning

Build implementation plan from finalized design.

**Knowledge to create:**
- The plan itself (as a design record)
- Task breakdown rationale
- Sequencing decisions
- Dependency analysis

**Commands:**
```bash
hive create design "Voice Scoring UI — Implementation Plan" \
  --domains indemn \
  --refs workflow:<id> \
  --status active \
  --body "Plan content..."

hive update <workflow-id> --current-context "Planning complete. 7 tasks in 4 waves. Execution starting."
```

## Phase: Execution

Implementation via parallel subtasks. Lower checkpoint volume — more mechanical.

**Knowledge to create:**
- Per-task completion records
- Implementation decisions made during coding (deviations from plan)
- Unexpected findings

**Commands:**
```bash
# When deviating from plan
hive create decision "Use argparse instead of Click for CLI" \
  --domains indemn \
  --refs workflow:<id> \
  --rationale "Consistency with session-manager pattern. Both Click and Typer installed but argparse matches existing code." \
  --tags architecture

# After completing a task
hive update <workflow-id> --current-context "Execution: 5/7 tasks complete. Task 6 (search) in progress."
```

## Phase: Code Review

Review implementation against the design.

**Knowledge to create:**
- Review findings, issues identified
- Design conformance assessment
- Fixes applied

## Phase: Testing

Testing and debugging. Often generates substantial knowledge.

**Knowledge to create:**
- Bug reports and root cause analyses
- What was tried and what worked
- Performance findings

**Commands:**
```bash
hive create note "Root cause: search ranking favors old records" \
  --tags feedback \
  --domains indemn \
  --refs workflow:<id> \
  --body "Found that the combined score formula weights semantic too heavily..."
```

## Phase: Deployment

Ship it.

**Knowledge to create:**
- Deployment record
- Issues encountered
- Rollback decisions if any

**Commands:**
```bash
hive update <workflow-id> --status completed \
  --current-context "Deployed. All tests passing. Monitoring for issues."
```
