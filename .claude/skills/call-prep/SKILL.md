---
name: call-prep
description: Prepare for a customer call by pulling context from meetings, pipeline, Slack, and email. Use when the user asks about preparing for a call, what they should know before a meeting, customer context before a conversation, or needs a briefing on a company.
argument-hint: [company-name]
allowed-tools: Bash(psql *), Bash(curl *), Bash(gog *), Bash(npx agent-slack *)
---

# Call Prep

Build a comprehensive briefing for an upcoming customer call.

**Target customer**: $ARGUMENTS

If $ARGUMENTS is empty, ask the user which customer they're preparing for.

## Skills Used

- `/meeting-intelligence` — meeting history, signals, objections, quotes, contacts (see its `references/data-dictionary.md` for schema and query patterns)
- `/pipeline-deals` — deal status, pipeline API
- `/slack` — recent team discussion about the customer
- `/google-workspace` — recent email threads (Gmail)

## Workflow

1. **Meeting History** — Last 5 meetings with this customer including summaries. Use meeting-intelligence patterns for `"Meeting"` + `"MeetingExtraction"` joined through `"Company"`.
2. **Signals & Objections** — Recent signals (expansion, churn_risk, blocker, champion, health) and objections. Use meeting-intelligence patterns for `"Signal"` and `"MeetingExtraction"` where `"extractionType" = 'objection'`.
3. **Recent Slack Mentions** — Search Slack for the customer name. Use slack skill patterns.
4. **Recent Emails** — Search Gmail for the customer name. Use google-workspace Gmail search patterns.
5. **Deal Status** — Current pipeline position and scoring. Use pipeline-deals patterns for both the API and direct `"Deal"` table queries.
6. **Key Contacts** — Known contacts at this company. Use meeting-intelligence patterns for `"Contact"` filtered by `"companyId"`.

## Output Structure

**Briefing: [Company Name]**

- **Last Meeting**: Date, title, 1-2 sentence summary
- **Relationship Summary**: Meeting count, timeframe, key attendees
- **Key Contacts**: Name, role, email
- **Active Signals**: Type, description, date — grouped by positive/negative
- **Open Objections**: Objection, category, whether response worked
- **Recent Activity**: Slack discussion summary + email thread summary
- **Deal Status**: Stage, ARR, score, staleness
- **Suggested Talking Points**: 3-5 points based on signals, objections, and recent activity
