---
ask: "Session record — meeting ingestion pipeline built end-to-end with Google Meet API"
created: 2026-04-21
workstream: customer-system
session: 2026-04-21-roadmap
---

# Session Record — 2026-04-21: Meeting Ingestion + Entity Work

## What Was Done

### Meeting Ingestion Pipeline (end-to-end)

**Google Workspace Integration:**
- Domain-wide delegation set up (service account `indemn-os@indemn.iam.gserviceaccount.com`)
- DWD scopes: `drive`, `admin.directory.user.readonly`, `meetings.space.readonly`, `calendar.readonly`
- Service account key in AWS Secrets Manager (`indemn/dev/shared/google-workspace-sa`)
- Railway API has AWS credentials (IAM user `railway-dev-services`, least-privilege)
- Integration entity created and active in the OS

**Adapter (3 major rewrites):**
1. v1: Drive filename search (bad — fragile, missing files, wrong content)
2. v2: Google Meet REST API (good — proper conference records with linked artifacts)
3. v3: Meet API + Calendar API + Admin SDK (complete — all data captured)

**What the adapter captures per meeting:**
- Conference metadata: start/end time, duration, meeting code, meeting URL, organizer
- Participants: name, Google user ID, email (resolved via Admin SDK + Calendar), join/leave times, attended vs invited, RSVP status
- Recording: Drive URL
- Transcript: structured entries (speaker + text + timestamp, expire 30 days) preferred over Doc export
- Smart Notes (Gemini): separate doc content with Summary/Decisions/Next Steps/Details
- Calendar event: title, full attendee list with emails

**Data quality fixes:**
- Lobby dedup: Google creates multiple conference records per meeting room. Kept the real meeting, discarded empty lobbies
- Participant merging: Calendar attendees (everyone invited) merged with Meet participants (who actually joined)
- External participant email resolution via Calendar attendee matching (fuzzy name + email prefix)
- Transcript speaker names resolved using participant list (handles external people)
- Line ending normalization for Gemini notes parsing (`\r\n` → `\n`)
- Summary extraction regex fixed

**Kernel infrastructure built:**
- `fetch_new` collection-level kernel capability (generic — works for any entity type)
- Collection-level API route: `POST /api/{entities}/{cap-name}` (no entity_id)
- Collection-level CLI command: `indemn meeting fetch-new [--data '{"since": "..."}']`
- Google Workspace adapter: `kernel/integration/adapters/google_workspace.py`
- Integration CLI improvements: `--config`, `--secret-ref`, `update`, `transition` commands
- Entity CLI improvements: `get` and `delete` commands (with API endpoints)

### Entity Definitions Created/Modified

**New entities:**
- Employee: name, email, title, slack_id, slack_display_name, google_user_id, actor_id, status
- Meeting fields added: meeting_code, meeting_url, organizer, participants, notes

**Existing entities recreated with proper types:**
- Meeting, Task, Decision, Signal, Commitment — deleted and recreated with proper ObjectId relationships, enums, correct types

### Employee Entity Seeded (15 people)

Data from Google Admin SDK + Slack + Actor linkage:
- Craig Certo, Kyle Geoghan, Cameron Torstenson, Dhruv Rajkotia, Ganesh Iyer
- George Remmer, Peter Duffy, Jonathan Nellermoe, Ian Seidner, Dolly Talreja
- Rudraraj Thakar, Marlon Simpson, Kai Taylor, Rocky Vest, George Redenbaugh

### Actor Cleanup

- Deleted 11 junk actors (runtime-service accounts, test workers, duplicates)
- Fixed 3 wrong names (Jonathan Chen→Nellermoe, Dhruv Vasishtha→Rajkotia, Marlon→Simpson)
- Created 3 missing actors (Kai, Rocky, George Redenbaugh)
- Activated all team actors
- Removed Drew, Ryan (per Craig)

### Meeting Data Ingested

20 meetings from April 20-21 across all domain users:
- 10 with full content (transcripts, notes, summaries, recordings)
- 10 without content (team didn't enable recording/transcription — some use Granola instead)
- All participants resolved with emails (internal via Admin SDK, external via Calendar)
- No duplicates (lobby entries filtered)

## Known Issues

- UI shows `[object Object]` for the `participants` list field — UI doesn't know how to render nested dicts in table columns
- `team_members` field includes external participants (should only be internal) — post-processing concern
- Kyle actor conflict: other session set password on deleted actor `69e28fedf508e1ceb69654c7`. Need to re-set on correct actor `69e4065ed260a73f432839aa`
- Meetings without Google artifacts (Granola meetings) have no content — need Granola adapter or team process change
- Calendar API adds ~10 seconds per meeting for event lookup — full org ingestion takes ~3-5 minutes

## What's Next

1. Merge os-customer-system branch work (Deal entity, SuccessPhase, UI improvements, Kyle docs)
2. Employee entity resolution in meetings (match participants to Employees + Contacts)
3. Meeting classification (customer/internal/etc.) and Company linking
4. Extraction associate (Tasks, Decisions, Signals, Commitments from transcripts)
5. Kyle's prospect dashboard (Deals + Tasks + assignees)
