---
ask: "Checkpoint all knowledge, decisions, and open questions about meeting ingestion into the OS"
created: 2026-04-21
workstream: customer-system
session: 2026-04-21-roadmap
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
  - type: google-drive
    description: "Investigation of Gemini meeting files structure, metadata, ownership"
  - type: conversation
    description: "Craig + Claude brainstorming on adapter design, entity model, refinements"
---

# Meeting Ingestion Checkpoint — 2026-04-21

## What We're Building

Kyle wants a prospect dashboard: list of ~10 prospects, next steps per prospect, delegation, always up to date. To populate it intelligently, we need to ingest meeting data into the OS, extract intelligence, and link it to prospects/customers.

## The Overall Workflow

```
1. INGEST: Pull meeting data from Google into OS Meeting entities
2. EXTRACT: Associate processes meetings — creates Tasks, Decisions, Signals, Commitments
3. CLASSIFY: Associate links meetings to Companies, categorizes (customer/internal/etc.)
4. SURFACE: Kyle sees prospects + action items + who's assigned + what's overdue in the UI
```

We are currently on step 1 (ingest) and shaking it out.

## What's Built and Working

### Infrastructure
- Google Workspace domain-wide delegation set up (service account `indemn-os@indemn.iam.gserviceaccount.com`)
- Service account key in AWS Secrets Manager (`indemn/dev/shared/google-workspace-sa`)
- Railway API has AWS credentials to read Secrets Manager
- IAM user `railway-dev-services` with least-privilege (read dev secrets only, explicit prod deny)
- DWD scopes authorized: `drive`, `admin.directory.user.readonly`

### Entity Definitions Created
- **Meeting**: title, date, duration_minutes, company, contacts, team_members, source, transcript, summary, transcript_ref, recording_ref, external_ref, stage, notes
  - State machine: recorded → transcribed → extracted → reviewed
- **Task**: title, description, company, source_meeting, assignee, due_date, priority, category, source, stage, notes
- **Decision, Signal, Commitment**: linked to Company + source_meeting

### Kernel Code Shipped
- `kernel/integration/adapters/google_workspace.py` — adapter that fetches from Google Drive via domain-wide delegation
- `kernel/capability/fetch_new.py` — collection-level capability (creates entities from external systems)
- Collection-level capability route: `POST /api/meetings/fetch-new`
- Collection-level CLI command: `indemn meeting fetch-new [--data '{"since": "..."}']`
- Integration CLI improvements: `--config`, `--secret-ref` on create; `update` and `transition` commands
- Entity CLI improvements: `get` and `delete` commands (with API endpoints)

### OS Configuration Done
- Integration entity created: Google Workspace, org-level, active
- `fetch_new` capability enabled on Meeting entity
- `indemn meeting fetch-new` works end-to-end — creates Meeting entities from Google Drive

## What We Learned About Google Meet Files

### Three file types per meeting
1. **"Title - YYYY/MM/DD HH:MM TZ - Notes by Gemini"** — AI-generated Google Doc with structured sections (Summary, Decisions, Next Steps, Details)
2. **"Title - YYYY/MM/DD HH:MM TZ - Transcript"** — Word-for-word speaker-attributed transcript
3. **"Title - YYYY/MM/DD HH:MM TZ - Recording"** — Video file (mp4)

### Key facts discovered
- Files are owned by the **meeting organizer**, shared with attendees
- Notes and Recording can have **different timestamps** (e.g., 11:13 vs 11:15) — same meeting
- Not all meetings have all 3 files. Some have only Notes, some only Transcript
- **`videoMediaMetadata.durationMillis`** on Recording gives exact duration
- **`owners[0].displayName`** gives the organizer name
- Files in organizer's Drive have parent folders. Shared files have `parents: None` in other users' views
- The Transcript file has clean **comma-separated attendees** in an "Attendees" line
- Google sends an **email notification** with links to all meeting artifacts when recording is ready
- **There is NO hidden metadata** linking the files together (no appProperties, no shared ID)

### Current adapter approach
- Search each user's Drive for files matching name patterns
- Group by title + date (ignoring time differences)
- Export docs as text, parse structured content
- Dedup by Drive file ID (external_ref)

### Problems with current adapter
- Grouping by filename is fragile (time differences)
- Not finding all files for a meeting (Recording in organizer's Drive, not attendee's)
- Summary extraction regex doesn't work yet
- No `notes` field on Meeting entity (need to add it)
- No duration extraction (available from recording metadata)
- No organizer attribution
- Team members are strings, not entity references

## Open Question — Better Discovery Method

Craig pointed out: Google sends an email with links to all artifacts. There may be a more programmatic way to discover meetings than searching Drive by filename. Options to investigate:

1. **Google Calendar API** — calendar events have conferenceData with recording links
2. **Google Meet API** — may expose recordings/transcripts directly
3. **Google Workspace Events API** — push notifications on new meeting artifacts
4. **Gmail API** — the "recording ready" email has all links in one place
5. **Drive API with better query** — there might be a folder structure or metadata we're missing

Craig's instinct: "feels weird that we need to search the inbox when Gemini is the one sending the emails. The information should be stored somewhere we can access in a better way."

**This needs web research before we continue building.**

## Decisions Made

- Meeting entity is agnostic to Google — adapter maps Drive data to Meeting fields
- `fetch_new` is a collection-level kernel capability — generic pattern for any entity type
- One associate for the full pipeline — fetch + extract (not two separate associates)
- Company matching is post-processing (associate job), not adapter job
- Meeting classification (customer/internal/etc.) is a broader system to define
- Need an **Employee** entity in the customer success domain — links to Actor IDs, referenced in meetings
- `notes` field needed on Meeting for Gemini notes (separate from transcript)
- Duration from recording metadata (not transcript timestamps)
- Organizer should be stored on Meeting
- People in meetings who aren't Contacts or Employees should be auto-created with available info

## What Still Needs to Happen

### Immediate (get ingestion right)
1. **Research** — find the best programmatic way to discover Google Meet meetings and their artifacts
2. **Fix adapter** — implement whatever discovery method research reveals
3. **Add `notes` field** to Meeting entity definition
4. **Organizer field** — add and populate
5. **Duration** — extract from recording metadata
6. **Summary extraction** — fix the Gemini notes parsing

### Next (after ingestion works)
7. **Employee entity** — create definition, seed with team data, link to Actors
8. **People resolution** — match meeting attendees to Employees + Contacts
9. **Meeting classification** — define categories, associate logic
10. **Extraction associate** — skill + actor for processing meetings into Tasks/Decisions/etc.
11. **Company matching** — associate logic to link meetings to Companies

### After that (Kyle's view)
12. **Prospect dashboard** — Companies in prospect stage + Tasks + assignees + due dates
