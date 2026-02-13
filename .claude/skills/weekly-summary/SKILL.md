---
name: weekly-summary
description: Generate a weekly intelligence summary across meetings, pipeline, customer signals, and team activity. Use when the user asks for a weekly recap, summary of the week, what happened this week, or wants a status update across the business.
allowed-tools: Bash(psql *), Bash(curl *), Bash(npx agent-slack *)
---

# Weekly Summary

Generate a cross-system intelligence summary for the past 7 days.

## Skills Used

- `/meeting-intelligence` — meetings, decisions, action items, signals, quotes (see its `references/data-dictionary.md` for schema and query patterns)
- `/pipeline-deals` — pipeline movement, deal status
- `/slack` — team channel highlights

## Workflow

1. **Meetings This Week** — All meetings from the last 7 days with title, date, category, and company. Use meeting-intelligence patterns for `"Meeting"` joined through `"Company"`.
2. **Key Decisions** — Decisions extracted from this week's meetings. Use meeting-intelligence patterns for `"MeetingExtraction"` where `"extractionType" = 'decision'`.
3. **Action Items** — Items created in the last 7 days, highlighting overdue or unassigned. Use meeting-intelligence patterns for `"ActionItem"`.
4. **Customer Signals** — New signals grouped by type (expansion, churn_risk, blocker, champion, health). Use meeting-intelligence patterns for `"Signal"` joined through `"Company"`.
5. **Pipeline Movement** — Deal stage changes, new stale alerts, pipeline summary. Use pipeline-deals patterns.
6. **Notable Quotes** — Positive or negative sentiment quotes from the week. Use meeting-intelligence patterns for `"Quote"`.

## Output Structure

**Weekly Intelligence Summary — [Date Range]**

- **Meetings**: Count and list with dates and companies
- **Key Decisions**: Decision, meeting, date — grouped by category
- **Action Items**: Open count, due this week, overdue — list high-priority items
- **Customer Signals**:
  - Expansion opportunities
  - At-risk accounts (churn/blocker signals)
  - New champion identifications
- **Pipeline**: Status summary, stage changes, stale deals
- **Notable Quotes**: Quote, speaker, company, meeting
- **Themes & Patterns**: 2-3 themes worth noting based on the week's data

If the user specifies a different timeframe, adjust accordingly.
