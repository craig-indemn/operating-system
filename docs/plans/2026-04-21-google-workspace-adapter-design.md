# Design: Google Workspace Integration + Meeting Ingestion

**Date:** 2026-04-21
**Status:** Approved (brainstormed with Craig)

## Problem

Indemn has meeting transcripts scattered across individual team members' Google Drives (Gemini "Notes by Gemini" documents). Kyle wants a prospect dashboard with next steps populated from real meetings. We need to pull meetings org-wide into the OS, extract intelligence, and link it to prospects.

## Design Principles (from OS vision)

1. **The entity command IS the interface.** `indemn meeting fetch-new` dispatches through the Integration primitive automatically. The adapter maps directly to the entity.
2. **Integration is primitive #6.** One org-level Integration entity with domain-wide delegation covers all users.
3. **Adapters are kernel code** keyed by provider:version. They know HOW to talk to the provider. The Integration entity knows WHICH provider and credentials.
4. **The universal pattern:** Entry point -> creates entity -> watches fire -> associates process.

## Architecture

### The Flow

```
indemn meeting fetch-new
  -> kernel resolves Integration (system_type="google_workspace", owner_type="org")
  -> reads provider="google", provider_version="v1"
  -> finds adapter: ADAPTER_REGISTRY["google:v1"] -> GoogleWorkspaceAdapter
  -> fetches service account key from AWS Secrets Manager via secret_ref
  -> adapter.fetch() impersonates each domain user, searches Drive for new Gemini notes
  -> adapter returns data shaped as Meeting entity fields
  -> kernel creates Meeting entities (stage="recorded")
  -> associate continues: reads transcript, extracts child entities, transitions to "extracted"
```

### Components

#### 1. Integration Entity (data in MongoDB)

Created via CLI:
```bash
indemn integration create \
  --owner org \
  --name "Google Workspace" \
  --system-type google_workspace \
  --provider google \
  --provider-version v1 \
  --config '{"domain": "indemn.ai"}' \
  --secret-ref "indemn/dev/shared/google-workspace-sa"
```

Fields:
- `name`: "Google Workspace"
- `system_type`: "google_workspace"
- `provider`: "google"
- `provider_version`: "v1"
- `owner_type`: "org"
- `config`: `{"domain": "indemn.ai"}`
- `secret_ref`: "indemn/dev/shared/google-workspace-sa" (service account JSON key)

#### 2. Google Workspace Adapter (`kernel/integration/adapters/google_workspace.py`)

Implements the Adapter interface:

**`fetch(since, user_emails, query, limit)`**
- Uses service account key for domain-wide delegation
- If `user_emails` not provided, uses Admin SDK to list all domain users
- For each user, impersonates via JWT and searches Drive
- Default query: `name contains 'Notes by Gemini'` with `mimeType='application/vnd.google-apps.document'`
- Exports each Google Doc as plain text
- Deduplicates by Drive file ID across users
- Returns list of dicts shaped as Meeting entity fields:
  ```python
  {
      "title": "Meeting Title",
      "date": "2026-04-20T14:00:00Z",
      "source": "google_meet",
      "transcript": "<full text content>",
      "summary": "<extracted from Gemini Summary section>",
      "transcript_ref": "<Google Drive file ID>",
      "external_ref": "<Google Drive file ID>",  # dedup key
      "team_members": ["Kyle", "Craig"],  # parsed from "Invited" line
      "duration_minutes": null,  # not available from transcript
  }
  ```

**`test()`**
- Verifies service account can impersonate a user and list Drive files
- Returns `{"status": "ok", "domain": "indemn.ai", "users_accessible": N}`

**Dependencies:** `google-auth`, `google-api-python-client` (added to kernel dependencies)

#### 3. `fetch_new` Capability on Meeting Entity

A kernel capability enabled via:
```bash
indemn entity enable Meeting --capability fetch_new \
  --config '{"system_type": "google_workspace"}'
```

When invoked (`indemn meeting fetch-new`):
1. Resolves Integration with `system_type` from capability config
2. Instantiates adapter with credentials
3. Calls `adapter.fetch(since=<last_fetched_at>)`
4. For each result, checks `external_ref` for dedup (skip if Meeting with that external_ref already exists)
5. Creates Meeting entities via `save_tracked()`
6. Returns count of new meetings created

The `since` parameter defaults to the most recent Meeting's `date` field, or a configurable lookback window.

#### 4. Meeting Ingestion Associate (one associate, full pipeline)

**Trigger:** Scheduled (cron — e.g., every 30 minutes)

**Skill:** Markdown instructions describing:
1. Call `indemn meeting fetch-new` to pull new meetings from Google
2. For each newly created Meeting (stage="recorded"):
   - Read the transcript content
   - Parse Gemini's structured sections:
     - **Summary** -> Meeting.summary (already set by adapter)
     - **Next Steps** -> Task entities (title, assignee parsed from `[Person Name]`, source="meeting_extraction", linked to Meeting and Company)
     - **Decisions** -> Decision entities (description, participants, linked to Meeting and Company)
     - **Details** -> available as Meeting.transcript for deeper analysis
   - Match meeting participants to existing Company/Contact entities (fuzzy match on names)
   - Set Meeting.company if a clear match exists
   - Create child entities via CLI (`indemn task create`, `indemn decision create`, etc.)
   - Transition Meeting to `extracted`

**Company matching:** The associate skill describes how to match meeting titles and participants to existing Companies. For example, "Customer Status: CDD" -> Company "CDD". "Demo with Arian Taghdiri (GIRG)" -> Company "GIRG". This is where the associate's reasoning helps — fuzzy matching that rules can't do.

**Associate mode:** hybrid (rules for parsing structure, LLM for entity matching and ambiguous cases)

### Gemini Transcript Format (verified)

```
Notes
<date>
<title>
Invited <participant names>
Attachments <title>
Meeting records Recording

Summary
<AI summary with topic headings>

Decisions
<ALIGNED/DISAGREED markers with descriptions>

Next steps
* [Person Name] Task description
* [Person Name] Task description

Details
* <Paragraph per topic, speaker-attributed>
```

### What Signals and Commitments Look Like

Signals and Commitments are extracted from the Details section, not from explicit Gemini sections:
- **Signals**: "George mentioned they are awaiting feedback from Ben" -> Signal(type="blocker", company="GIC")
- **Commitments**: "Ganesh plans to send Insurica a recorded demo today" -> Commitment(made_by="Ganesh", made_to="Insurica", made_by_side="indemn")

These require LLM reasoning — the associate reads the Details section and identifies signals/commitments that aren't captured in Gemini's structured output.

## What Already Exists

- Meeting, Task, Decision, Signal, Commitment entities defined in the OS
- Integration kernel entity with create, set-credentials, test, health CLI
- Adapter base class with fetch/send/test interface
- Adapter registry and dispatch (resolve integration -> instantiate adapter -> execute)
- Outlook and Stripe adapters as reference implementations
- Google Workspace service account with domain-wide delegation authorized
- Service account key stored in AWS Secrets Manager (`indemn/dev/shared/google-workspace-sa`)
- `gog` CLI confirmed working for impersonation (Craig, Kyle, Cam)

## What Needs to Be Built

### Kernel Code (indemn-os repo)
1. `kernel/integration/adapters/google_workspace.py` — adapter implementation
2. Register adapter in `kernel/integration/adapters/__init__.py`
3. `fetch_new` kernel capability (generic, works for any entity with an integration adapter)
4. CLI command for `fetch-new` on entity types with the capability enabled
5. Add `google-auth` and `google-api-python-client` to kernel dependencies

### OS Configuration (via CLI)
6. Create Integration entity for Google Workspace
7. Enable `fetch_new` capability on Meeting entity
8. Create the Meeting Ingestion skill
9. Create the associate actor with scheduled trigger

### Not Built Yet (deferred)
- Watching for new meetings in real-time (Change Streams on Google Drive) — poll is sufficient for now
- Granola/Notion adapters — Google Meet + Gemini is the v1 source of truth
- Automatic company/contact matching rules — the associate uses LLM reasoning for now, rules added when patterns emerge

## Credential Flow

```
Integration.secret_ref = "indemn/dev/shared/google-workspace-sa"
  -> AWS Secrets Manager
  -> Returns JSON service account key
  -> google.oauth2.service_account.Credentials.from_service_account_info()
  -> subject=<user_email> for impersonation
  -> Google Drive API calls as that user
```

## Success Criteria

1. `indemn meeting fetch-new` pulls Gemini meeting notes from all Indemn team members' Drives
2. Meeting entities created with transcript, summary, participants, linked to Companies
3. Task entities created from "Next Steps" with assignee and due dates
4. Decision entities created from "Decisions" section
5. Signal and Commitment entities created from "Details" section via LLM extraction
6. No duplicate meetings (dedup by external_ref = Drive file ID)
7. Kyle can see prospect Companies with their associated Tasks in the UI
