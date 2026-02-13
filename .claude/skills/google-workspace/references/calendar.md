# Calendar Reference — gog calendar

Complete reference for Google Calendar operations via the `gog` CLI.

## List Events

```bash
gog calendar events [calendarId] [--today] [--tomorrow] [--week] [--days=N] [--from=STRING --to=STRING] [--all] [--max=10] [--json]
```

The `calendarId` defaults to `primary` if omitted.

```bash
# Today's events
gog calendar events --today --json

# Tomorrow's events
gog calendar events --tomorrow

# This week
gog calendar events --week --json

# Next 14 days
gog calendar events --days=14 --json

# Custom date range
gog calendar events --from="2025-01-15" --to="2025-01-22" --json

# All events (no time filter)
gog calendar events --all --max=50 --json

# Events from a specific calendar
gog calendar events my-team-calendar-id --today --json
```

**Relative time values work for --from and --to:** `today`, `tomorrow`, `monday`, `+7d`, etc.

```bash
# Next 7 days using relative time
gog calendar events --from=today --to=+7d --json
```

## Search Events

```bash
gog calendar search <query> [--today] [--week] [--from=STRING --to=STRING] [--max=25] [--json]
```

Full-text search across event titles, descriptions, and other fields.

```bash
# Find meetings about a topic
gog calendar search "INSURICA" --json

# Search within this week
gog calendar search "standup" --week --json

# Search in a date range
gog calendar search "renewal" --from="2025-01-01" --to="2025-03-01" --max=20 --json

# Search today only
gog calendar search "sync" --today --json
```

## Create Event

```bash
gog calendar create <calendarId> --summary=STRING --from=STRING --to=STRING [--description=STRING] [--location=STRING] [--attendees=STRING] [--with-meet] [--all-day] [--send-updates=all|externalOnly|none]
```

```bash
# Simple event
gog calendar create primary --summary="Team Standup" --from="2025-01-15T10:00:00" --to="2025-01-15T10:30:00"

# Event with attendees and Google Meet
gog calendar create primary --summary="Call with INSURICA" --from="2025-01-15T14:00:00" --to="2025-01-15T15:00:00" --attendees="julia@insurica.com,cam@indemn.ai" --with-meet --send-updates=all

# Event with description and location
gog calendar create primary --summary="Client Lunch" --from="2025-01-15T12:00:00" --to="2025-01-15T13:00:00" --description="Discuss Q2 roadmap" --location="Downtown Grill"

# All-day event
gog calendar create primary --summary="Team Offsite" --from="2025-01-20" --to="2025-01-21" --all-day

# Notify only external attendees
gog calendar create primary --summary="Review" --from="2025-01-15T09:00:00" --to="2025-01-15T09:30:00" --attendees="partner@external.com" --send-updates=externalOnly
```

## Update Event

```bash
gog calendar update <calendarId> <eventId> [same flags as create]
```

```bash
# Change the time
gog calendar update primary abc123eventid --from="2025-01-15T11:00:00" --to="2025-01-15T11:30:00"

# Change the title
gog calendar update primary abc123eventid --summary="Updated Meeting Title"

# Add attendees
gog calendar update primary abc123eventid --attendees="new-person@company.com" --send-updates=all
```

## Delete Event

```bash
gog calendar delete <calendarId> <eventId>
```

```bash
gog calendar delete primary abc123eventid
```

## Check Free/Busy

```bash
gog calendar freebusy <calendarIds> --from=STRING --to=STRING
```

Check availability for one or more calendars.

```bash
# Check your availability
gog calendar freebusy primary --from="2025-01-15T08:00:00" --to="2025-01-15T18:00:00"

# Check multiple people
gog calendar freebusy "primary,colleague@indemn.ai" --from=today --to=tomorrow
```

## List Calendars

```bash
gog calendar calendars
```

Lists all calendars the authenticated account has access to, including shared calendars.

## Respond to Invitation

```bash
gog calendar respond <calendarId> <eventId>
```

Respond to a calendar invitation (accept, decline, tentative).

## Find Conflicts

```bash
gog calendar conflicts
```

Finds scheduling conflicts in your calendar.

## Focus Time

```bash
gog calendar focus-time --from=STRING --to=STRING
```

Creates a focus time block.

```bash
gog calendar focus-time --from="2025-01-15T09:00:00" --to="2025-01-15T12:00:00"
```

## Out of Office

```bash
gog calendar out-of-office --from=STRING --to=STRING
```

Creates an out-of-office event.

```bash
gog calendar out-of-office --from="2025-01-20" --to="2025-01-24"
```

## Common Patterns

**Morning briefing — what's on today:**
```bash
gog calendar events --today --json
```

**Find a meeting to prep for:**
```bash
gog calendar search "INSURICA" --week --json
```

**Schedule a meeting with Google Meet:**
```bash
gog calendar create primary --summary="Discovery Call" --from="2025-01-15T14:00:00" --to="2025-01-15T14:45:00" --attendees="prospect@company.com" --with-meet --send-updates=all
```

**Check availability before scheduling:**
```bash
gog calendar freebusy primary --from="2025-01-15T08:00:00" --to="2025-01-15T18:00:00"
```

**Week planning — see everything coming up:**
```bash
gog calendar events --days=7 --json
```
