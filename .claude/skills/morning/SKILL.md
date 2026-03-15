---
name: morning
description: Daily planning session — pulls calendar, active work, priorities, and what needs attention. Start the day with a comprehensive briefing and set priorities through conversation.
---

# Morning Consultation

Start the day by reviewing everything in flight and setting priorities.

## How It Works

1. Gather context using the morning consultation playbook (`systems/hive/playbooks/morning.md`)
2. Present the day's landscape
3. Have a conversation about priorities
4. Update records based on decisions made
5. Close with a session summary

## Quick Start

Run the morning consultation context assembly:

```bash
# Calendar — what's on the schedule for the next 48 hours
hive list calendar_event --status active --format json

# Active workflows — what's in flight across all domains
hive list workflow --status active --format json

# Recent activity — what happened in the last 24 hours
hive recent 24h --format json

# Synced items — unaddressed items from external systems
hive list linear_issue --status active --format json
hive list email_thread --status active --format json
hive list github_pr --status active --format json
hive list slack_message --status active --format json
```

## Present the Briefing

### Calendar
Show upcoming events for the next 48 hours with attendee context. Pull entity profiles for attendees who are Hive records — their role, company, recent interactions.

### Active Work
List all active workflows with their current state and last activity. Organize by domain. Flag anything stale (>7 days without update) — these need a conscious decision: push forward, pause, or drop.

### Needs Attention
- Critical/high priority items
- Unread emails and Slack messages
- Open PRs needing review
- Linear issues in progress
- Stale workflows
- Items that have been high-priority for multiple days without progress

### Yesterday
Summarize what happened in the last 24 hours — completions, new records, decisions made. Give a sense of momentum.

### Cross-Domain Connections
Surface any connections between work in different domains — development work that could become content, shared patterns, cross-pollination opportunities.

## During the Conversation

As Craig discusses priorities:

```bash
# Adjust priorities
hive update <id> --priority critical|high|medium|low

# Mark completed items
hive update <id> --status done

# Capture decisions
hive create note "..." --tags decision --domains <domain>

# Capture ideas
hive create note "..." --tags note --domains <domain>

# Pause a workflow
hive update <workflow-id> --status paused

# Get more detail on any record
hive get <id> --format json
hive refs <id> --format json
```

## Closing

Create a session summary capturing what was decided:

```bash
hive create note "Morning consultation YYYY-MM-DD" \
  --tags session_summary \
  --domains indemn,career-catalyst,personal \
  --body "Priorities set: [list]. Decisions: [list]. Focus for today: [list]."
```
