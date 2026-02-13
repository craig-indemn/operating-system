---
name: follow-up-check
description: Find overdue action items, unmet commitments, and missing follow-ups from meetings. Use when the user asks about follow-ups, what's overdue, dropped balls, things that need attention, or outstanding commitments.
allowed-tools: Bash(psql *), Bash(gog *), Bash(npx agent-slack *)
---

# Follow-Up Check

Surface action items and commitments that need attention — things that may have fallen through the cracks.

## Skills Used

- `/meeting-intelligence` — action items, commitments, decisions (see its `references/data-dictionary.md` for schema and query patterns)
- `/pipeline-deals` — stale deals needing attention
- `/google-workspace` — verify if follow-up emails were sent (optional)

## Workflow

1. **Overdue Action Items** — Items past their due date that aren't completed. Use meeting-intelligence patterns for `"ActionItem"` joined through `"Meeting"`.
2. **Upcoming Action Items** — Items due in the next 7 days that aren't completed. Same pattern.
3. **Stale Deals** — Deals flagged as stale with unresolved alerts. Use pipeline-deals patterns for `"Deal"` + `"StaleAlert"`.
4. **Commitments Without Follow-Through** — Recent decisions with `category = 'commitment'` from the last 14 days that don't have corresponding action items. This is a heuristic — present results as "worth reviewing."
5. **Verify Follow-Up Emails** (optional) — For high-priority overdue items with known contacts, check Gmail for recent outreach. Use google-workspace Gmail search patterns. Only run if the user asks or if specific items stand out.

## Output Structure

**Follow-Up Check — [Today's Date]**

- **Overdue** (count):
  Table with: Item, Owner, Due Date, From Meeting, Meeting Date

- **Due This Week** (count):
  Table with: Item, Owner, Due Date, From Meeting

- **Stale Deals** (count):
  Table with: Company, Stage, Days Stale, Reason, Suggested Action

- **Commitments Without Follow-Through**:
  List of decisions/commitments that may lack action items

- **Recommended Actions**:
  Top 3-5 things that need attention right now, prioritized by urgency
