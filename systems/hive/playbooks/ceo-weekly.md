# CEO Weekly View — Context Assembly Playbook

## Purpose
Generate a shareable weekly summary for the CEO and teammates. Not raw data — a curated,
executive-level view of what happened, what's in flight, and what needs attention.

## What to Gather

### 1. Weekly Activity Overview
```bash
hive recent 7d --format json
```
Summarize: how many records created/updated, across which domains, key types.

### 2. Completed Work
```bash
hive list workflow --status done --recent 7d --format json
```
What workflows were completed this week? Include objectives and outcomes.

### 3. Active Workflows
```bash
hive list workflow --status active --format json
```
What's currently in progress? Current phase, blockers, expected next steps.

### 4. Key Decisions Made
```bash
hive search "" --tags decision --recent 7d --format json
```
Decisions made this week with rationale. These are the "why" behind the work.

### 5. Customer & Pipeline Activity
```bash
hive list meeting --recent 7d --format json
hive list linear_issue --status active --format json
```
Meetings held, issues in progress, customer signals.

### 6. Cross-Domain Connections
```bash
hive discover --limit 10 --format json
```
Any interesting connections between work areas.

### 7. Graph Health
```bash
hive health --format json
```
System health metrics — good to include as a footnote.

## Output Format

Generate a markdown document suitable for sharing (email, Slack, or PDF via /markdown-pdf):

```markdown
# Weekly Intelligence Summary — Week of [Date]

## Highlights
- [3-5 bullet points of the most important things that happened]

## Completed This Week
| Workflow | Domain | Outcome |
|----------|--------|---------|
| [name] | [domain] | [what was accomplished] |

## In Progress
| Workflow | Domain | Status | Next Steps |
|----------|--------|--------|------------|
| [name] | [domain] | [current phase] | [what's next] |

## Key Decisions
- **[Decision title]** — [rationale summary]

## Customer & External
- [Meetings, pipeline updates, external signals]

## Attention Items
- [Stale workflows, blocked items, things needing input]

## Metrics
- Records created/updated this week: [N]
- Active workflows: [N]
- Graph health score: [N]/100
```

## Distribution
- Save as artifact: `hive create note "Weekly summary [date]" --tags session_summary --domains indemn`
- Convert to PDF if needed: `/markdown-pdf`
- Share via Slack or email as appropriate
