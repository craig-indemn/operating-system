---
name: meeting-intelligence
description: Query meeting transcripts, extracted intelligence (decisions, quotes, signals, objections), and customer insights from the Neon Postgres database. Use when the user asks about meetings, customers, or company intelligence.
allowed-tools: Bash(psql *)
---

# Meeting Intelligence

Query Indemn's meeting intelligence database. 3,141 meetings with transcripts, 14,612 extracted insights, 3,240 signals, 3,681 quotes, 1,469 action items.

**Connection**: `source .env && /opt/homebrew/opt/libpq/bin/psql "$NEON_CONNECTION_STRING" -c "<query>"`

All table and column names are **PascalCase and must be double-quoted**.

## Core Tables & Key Columns

**Meetings**
- `"Meeting"` — `id`, `title`, `date`, `source`, `"meetingType"`, `category`, `"companyId"`
- `"MeetingUtterance"` — `"meetingId"`, `"speakerName"`, `text`, `"startMs"` (183K rows — always filter by `"meetingId"`)
- `"MeetingParticipant"` — `"meetingId"`, `"speakerName"`, `"speakingTime"`, `"utteranceCount"`

**Extracted Intelligence**
- `"MeetingExtraction"` — `"meetingId"`, `"extractionType"`, `category`, `text`, `confidence`, `context`, `rationale`
  - `"extractionType"` values: `decision` (5,691), `learning` (4,691), `problem` (2,622), `objection` (1,608)
  - `confidence` (learnings only): `insight`, `worked`, `didnt_work`
  - `"companyId"` is almost always NULL — join through `"Meeting"."companyId"` instead

**Signals & Quotes**
- `"Signal"` — `"meetingId"`, `"companyId"`, `"signalType"`, `sentiment`, `text`, `"meetingDate"`
  - `"signalType"` values: `health`, `expansion`, `champion`, `churn_risk`, `blocker`
- `"Quote"` — `"meetingId"`, `"companyId"`, `text`, `"speakerName"`, `sentiment`, `"usableFor"`, `"meetingDate"`
  - `sentiment`: `positive`, `neutral`, `negative`
  - `"usableFor"`: `internal`, `case_study`, `pitch`, `testimonial`

**Action Items**
- `"ActionItem"` — `"meetingId"`, `description`, `owner`, `"dueDate"`, `status`, `category`, `customer`

**Companies & Contacts**
- `"Company"` — `id`, `name`, `domain`, `type`, `industry`, `"healthColor"`, `"healthScore"`
- `"Contact"` — `"companyId"`, `name`, `email`, `title`
- `"Deal"` — `"companyId"`, `status`, `"expectedARR"`, `"compositeScore"`, `"isStale"`, `"staleDays"`
- `"StaleAlert"` — `"dealId"`, `reason`, `"suggestedAction"`, `"isResolved"`
- `"Implementation"` — `"companyId"`, `"customerName"`, `stage`, `"healthStatus"`, `"hasVoiceAgent"`, `"hasChatAgent"`
- `"ImplementationMilestone"` — `"implementationId"`, `"isCompleted"`

## Key JOINs

- Extractions to companies: `"MeetingExtraction"` → `"Meeting"."companyId"` → `"Company"`
- Signals to companies: `"Signal"."companyId"` → `"Company"`
- Quotes to companies: `"Quote"."companyId"` → `"Company"`
- Action items to meetings: `"ActionItem"."meetingId"` → `"Meeting"`
- Deals to companies: `"Deal"."companyId"` → `"Company"`
- Stale alerts to deals: `"StaleAlert"."dealId"` → `"Deal"`
- Implementations to milestones: `"ImplementationMilestone"."implementationId"` → `"Implementation"`

## Full Reference

For complete column listings, enum values, query patterns, data flow diagrams, and domain explanations, see `references/data-dictionary.md`.
