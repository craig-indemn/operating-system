---
ask: "Brainstorm and plan meeting ingestion into the OS + prospect delivery tracking for Kyle"
created: 2026-04-20
workstream: customer-system
session: 2026-04-20-roadmap
sources:
  - type: conversation
    description: "Craig + Claude brainstorm on prospect delivery and meeting ingestion"
  - type: conversation
    description: "Craig's sync with Kyle and Cam on next steps"
---

# Meeting Ingestion + Prospect Delivery Plan

## Context

Craig talked with Cam and Kyle. First priority: ~10 new prospects. Kyle wants a prospect dashboard — list of prospects, next steps per prospect, delegation to the right people, delivery on time. To populate this intelligently, we need meeting ingestion — pull transcriptions from Google Drive, extract intelligence, link to prospects.

## Two Interconnected Workstreams

### 1. Kyle's Prospect Dashboard

**What Kyle wants:** Look at a list of prospects. See what the next steps are for each one. Know who's doing what. Update and delegate. Have it top-of-mind at any given point.

**How it maps to the OS:** Companies in `prospect` stage + their action items (Tasks) + assigned actors + due dates. No new "delivery plan" entity needed yet — Task entities linked to Companies give Kyle the view he needs. When the pattern for a structured delivery plan becomes clearer from actual use, we can extract it into its own entity.

### 2. Meeting Ingestion Pipeline

**The pattern (OS universal pattern):**
1. Integration adapter polls Google Drive for new meeting recordings/transcripts
2. Meeting entity created with transcript, participants, date, linked Company/Contacts
3. Watch fires → meeting intelligence associate processes the transcript
4. Associate extracts: action items (Tasks), decisions (Decisions), customer signals (Signals), commitments (Commitments)
5. Extracted data linked to Company/Contact entities
6. Kyle sees the prospect list with fresh next steps populated from the latest meetings

## Entity Model — What Exists

Entities already defined in the OS (created in prior session). All need refinement — relationship fields are strings instead of proper ObjectId relationships, some types are wrong (duration as str instead of int), enums not specified.

### Meeting
- **Fields:** title, date, duration_minutes, source, transcript_ref, recording_ref, summary, notes, company, contacts, team_members
- **State machine:** recorded → processed → intelligence_extracted
- **Needs:** transcript content field, proper relationships (company → Company, contacts → Contact), source enum (google_meet, granola, notion), external_ref for dedup, google_drive_file_id

### Task (= Action Items)
- **Fields:** title, description, assignee, due_date, priority, category, effort, source, source_meeting, source_implementation, company, notes
- **State machine:** open → in_progress/cancelled, in_progress → completed/blocked/cancelled, blocked → in_progress/cancelled
- **Needs:** proper relationships (company → Company, source_meeting → Meeting, assignee → Actor), enum values for priority and category

### Commitment
- **Fields:** description, made_by, made_by_side, made_to, due_date, due_date_precision, company, meeting, notes
- **State machine:** open → fulfilled/missed/dismissed, missed → fulfilled/dismissed
- **Needs:** proper relationships

### Signal
- **Fields:** type, description, source, severity, attributed_to, company, meeting, notes
- **No state machine** (stateless — signals are observations)
- **Needs:** proper relationships, type enum (health, expansion, churn_risk, champion, blocker, insight)

### Decision
- **Fields:** description, decided_by, participants, rationale, impact, supersedes, company, meeting, notes
- **No state machine** (stateless)
- **Needs:** proper relationships

## Google Integration — Research Needed

### The Question
Gemini transcriptions are saved in the meeting organizer's Google Drive. Kyle's concern: only accessible from the owner's account. Craig's intuition: corporate Google Workspace should give org-level access.

### Two Auth Paths (OS supports both)

**Path A: Org-level (preferred)** — Google Workspace domain-wide delegation. A service account authorized by the Workspace admin can access any user's Drive files. One Integration entity, owner_type=org.

**Path B: Per-user OAuth** — Each team member authenticates their Google account. Actor-level Integration entities. More operational overhead, but works if admin access isn't available.

### Research Tasks — ALL RESOLVED
1. **Format**: Google Docs (`application/vnd.google-apps.document`), title pattern: `"<Title> - YYYY/MM/DD HH:MM TZ - Notes by Gemini"`, paired with recordings (video/mp4). Export as text via `gog drive download <id> --format txt`.
2. **Admin access**: Craig got Workspace Super Admin access. Domain-wide delegation authorized.
3. **Scopes**: `https://www.googleapis.com/auth/drive` + `https://www.googleapis.com/auth/admin.directory.user.readonly`
4. **gog CLI**: Has built-in service account + domain-wide delegation support (`gog auth service-account set`)
5. **Transcript format**: Structured sections: Summary, Decisions, Next Steps, Details. Gemini does the extraction.

### What's Been Set Up
- **Service account**: `indemn-os@indemn.iam.gserviceaccount.com` (Client ID: `117418661528962049769`)
- **GCP project**: `indemn`
- **Domain-wide delegation**: Authorized in Google Workspace Admin Console
- **AWS Secrets Manager**: Key stored at `indemn/dev/shared/google-workspace-sa`
- **gog configured**: Service account set for craig@, kyle@, cam@indemn.ai
- **Verified**: Can read Kyle's and Cam's Drive files via impersonation — org-wide access confirmed

### Other Meeting Sources (defer for v1)
- Granola — has its own transcription format
- Notion — has its own transcription format
- Standardize on Google Meet + Gemini as v1 canonical source

## Execution Plan

### Track A: Entity Refinement (now)
1. Review existing Meeting, Task, Commitment, Signal, Decision definitions
2. Update with proper relationships, enums, correct types
3. Verify via CLI

### Track B: Google Adapter Research (next)
1. Investigate Gemini transcriptions in Craig's Drive via `gog` CLI
2. Understand data format and structure
3. Determine auth path (domain-wide delegation vs per-user)
4. Build the adapter

### Track C: Meeting Intelligence Associate (after B)
1. Define the extraction skill (what to extract, how to link)
2. Build the associate
3. Wire watches: Meeting created → associate processes → entities created
4. Test end-to-end with real meetings

### Track D: Kyle's View (alongside C)
1. Filter Companies by prospect stage
2. Show Tasks per company with assignee and due date
3. Surface overdue items
4. Allow Kyle to create/update Tasks manually too
