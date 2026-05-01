# Customer System — Roadmap

> Living source of truth for **how we get from where we are now to the vision**. Updated every session that moves the work forward. Read with `vision.md` (what we're building, why, and the lens) and `os-learnings.md` (running register of OS bugs + capability gaps + design questions).
>
> Last updated: **2026-05-01** (Session 15 close — TD-1 fully closed end-to-end; voice harness v2 deployed to Railway with multi-turn round-trip verified; chat-side log-touchpoint verified; 7 OS bugs resolved; chat + voice harnesses migrated to CLI-only skill loading. Bug #40 deferred to Session 16 for deep architectural design.).

---

## Where we are now (2026-05-01)

**TD-1 COMPLETE.** All four scheduled fetchers (Email, Meeting, Drive, Slack) active and autonomous on Railway. Voice harness v2 deployed; multi-turn voice round-trip created real Touchpoint `69f4ed4f03e56394d808bc88` end-to-end. Chat-side log-touchpoint verified end-to-end (Touchpoint `69f4f2ca03e56394d808bd6d`). Both transports use Voice OS Assistant (id `69f4c62d03e56394d808b79c`) with `log-touchpoint` skill. All TD-1 done-test items passing. **Next gate: Bug #40 deep architectural work in Session 16, then TD-2 begins.**

For deeper context on Session 15 closeout: `CURRENT.md`, `SESSIONS.md` Session 15 entry, `CLAUDE.md § 5 Journey` Session 15.

---

## Pre-Session-15 baseline (carried for reference — see CURRENT.md for current state)

**TD-1 ~85% complete (Session 14 close).** Three of four scheduled fetcher actors running autonomously (Email-Fetcher every 5 min, Meeting-Fetcher every 15 min, Drive-Fetcher every hour). Slack adapter built + deployed but live fetch blocked by Bug #45 (resolve_integration not finding the active Integration). Voice harness v1 built (commit `62f47f9`) but architecturally wrong — does NOT use deepagents framework or Interaction/Attention lifecycle per `docs/architecture/realtime.md` + `associates.md`; v2 canonical rebuild pending. log-touchpoint skill uploaded + assigned to OS Assistant; chat-side end-to-end test pending. **Phase A complete (Sessions 6-8). Phase B1 substantially de-risked (Session 12). Bug-fix work converging — Bug #38, #41, #42 resolved this session via parallel fork + main thread.**

**Specific Session 14 progress against TD-1 done-test:**
- ✓ Pre-flight cleanup verified: 0 unrelated emails/meetings from Bug #36 (500 + 5 deleted; Armadillo preserved); 2 Bug #37 rows deleted by fork session.
- ✓ ReviewItem entity + Reviewer role created (TD-2 pre-flight infrastructure done early per Session 13 plan).
- ✓ Email-Fetcher actor active. Trace `019ddf95-d579-7390-9483-beece987389f` 18:10-18:15Z verified end-to-end: 7 LLM turns all `finish=STOP`, fetched 326 emails.
- ✓ Meeting-Fetcher actor active. 30-day backfill done: fetched 396, created 2 net new, 394 deduped.
- ✓ Drive-Fetcher actor active. NEW kernel build: `fetch_documents()` on GoogleWorkspaceAdapter (commit `c87376d`). 30-day backfill: fetched 1161, created 493, deduped 668. Drive content extraction (Google Docs/Sheets/Slides export, PDF text) deferred to follow-up enrichment pass.
- ⚠ **Slack-Fetcher activation BLOCKED by Bug #45** — adapter built (`kernel/integration/adapters/slack.py` in commit `c87376d`, 9 unit tests GREEN), SlackMessage entity created, Integration entity active, but `resolve_integration()` doesn't find it. Live fetch returns "No messaging integration available." 90-day backfill + actor build pending the dispatch fix.
- ✓ Document.source enum extended with `slack_file_attachment`.
- ⚠ **log-touchpoint skill** uploaded + assigned to OS Assistant; chat-side end-to-end test still pending (WebSocket interaction).
- ⚠ **Voice harness v1 wrong shape; v2 canonical rebuild pending.** Per `docs/architecture/realtime.md`, the canonical voice harness mirrors chat-deepagents structure: deepagents `create_deep_agent` + harness_common (Interaction lifecycle, Attention with heartbeat, runtime registration, backend factory) + three-layer LLM config merge + LiveKit only handles audio I/O via DeepagentsLLM adapter. v1 (commit `62f47f9`) used `livekit.agents.Agent` with single custom `execute` tool — not aligned. **DELETE + REBUILD next session.** Voice runtime entity (id `69f3b7fc97300b115e7236a0`) + service token (`indemn/dev/shared/runtime-voice-service-token`) ready for v2.

**Bugs resolved this session:**
- Bug #38 (queue dispatch jam — uncaught WorkflowAlreadyStartedError + stale message retries + suspended-actor watch fan-out). Fork session, indemn-os commits `1026d78` + `c36969b`.
- Bug #37 follow-on (bulk-delete poison on malformed entities). Fork session, bundled in `1026d78`.
- Bug #41 (harness `_scheduled` entity-load CLI failure). Fork session, indemn-os commit `96684d5`.
- Bug #42 (Gemini 2.5 Flash MALFORMED_FUNCTION_CALL on `write_todos` schema). Resolved by switching runtime defaults to `gemini-3-flash-preview/global`. Both async-deepagents-dev + chat-deepagents-dev runtimes flipped.
- Bug #43 (Drive adapter scope was understated). Closed in-session by actually building the adapter.

**Bugs still open (logged for next session):**
- Bug #44 (voice-deepagents canonical rebuild — v1 built but wrong shape). Per-actor default_assistant pattern deferred per Craig (shared OS Assistant suffices for now).
- Bug #45 NEW (Slack `resolve_integration()` not finding active Integration). Highest priority next session — closes TD-1 sub-piece 4.

**LangSmith query gotcha discovered:** `order: "DESC"` (uppercase) returns HTTP 422 silently; must use `"desc"`. Worth noting in CLAUDE.md § 8 LangSmith debugging recipe.

For deeper context on the journey here: `CLAUDE.md § 5 Journey`, `INDEX.md § Status`, `SESSIONS.md`.

---

## Pre-Session-14 baseline (carried for reference)

**Phase A complete. Phase B1 substantially de-risked. Foundation is closer to running autonomously than at any prior point.**

- **27 entity definitions live** in dev OS, `_platform` org. Includes Playbook entity with both DISCOVERY and PROPOSAL stage records seeded.
- **Pipeline associates state:**
  - Email Classifier — *suspended* (kill switch held; v9 in DB ready, content_hash `9eef4959ae701614`). Hard Rule #1 inverted (resolve-before-create > never-auto-create). Verified live on Armadillo's first-contact email — autonomous Company + Contact creation worked.
  - Touchpoint Synthesizer — *suspended* (unchanged). Has not been triggered autonomously since Session 9.
  - Intelligence Extractor — *active*. Silent-stuck-state regression that previously caught it is fixed (Session 10 commit `d914d76`). Ran on Armadillo extracting 14 entities against the DISCOVERY Playbook.
- **Hydrated customers / prospects:**
  - **GR Little** hydrated end-to-end. Kyle validated Apr 24.
  - **Alliance** hydrated end-to-end (60+ entities). v2 proposal rendered, PDF in Cam's Drive folder, trace-showcase HTML shared with Cam + Kyle.
  - **Armadillo Insurance** hydrated end-to-end as designed (Apr 29) — first new-prospect trace post-Hard-Rule-#1-inversion. 1 Company + 1 Deal + 2 Contacts (Matan Slagter CEO, David Wellner COO) + 2 Touchpoints + 14 extracted entities.
- **~930+ emails ingested** across 11 team members. ~67+ meetings ingested. Queue drained.
- **OS bugs:** load-bearing kernel work substantially done. Bug #35 (deepagents skill discovery — was THE blocker), Bug #36 (Gmail/Calendar `fetch_new` adapter `**params` absorption), Bug #37 (Email list endpoint malformed-doc tolerance) all closed this session. Plus burst #4 fixes from Apr 27-28 (Bug #23/#24 bulk-delete operators, Bug #10 reprocess primitive, Bug #9 boundary coercion, Bug #29 route eviction, Bug #30 partialFilterExpression auto-emit, --include-related reverse refs, always-fresh entity-skill rendering, several CLI papercut fixes). The kernel is in genuinely solid shape now.
- **5 new design gaps logged this session** — Deal-lifecycle automation gap (no Deal-creator associate yet, Touchpoint↔Deal chicken-and-egg, Proposal-at-DISCOVERY auto-create not wired), Employee `entity_resolve` not activated, Company hydration is bare on auto-create, Contact richer-field parsing from email signatures, internal docs spanning multiple prospects.
- **Cleanup pending:** 500 unrelated Emails + 6 unrelated Meetings on Kyle's mailbox from Bug #36 side-effect (sit at status `received`, EC suspended so untouched). 2 malformed Email rows from Bug #37 data side (`69ea548e…6e92` Oneleet, `69ea556f…7387` Linear Orbit).
- **Open design questions (long-running, none resolved this session):** Opportunity vs Problem entity; Document-as-artifact pattern for emails; 12 sub-stages with archetype multi-select (Kyle's Apr 24 ask); origin/referrer tracking; Playbook hydration mechanism. See `os-learnings.md` for full list.

For deeper context on the journey here: `CLAUDE.md § 5 Journey`, `INDEX.md § Status`, `SESSIONS.md`.

---

## Tangible deliverables (TD-1 through TD-11)

The roadmap is organized around tangible deliverables, not foundation phases. Each TD is a concrete piece the team can use OR a foundational capability that unlocks the next concrete piece. They run mostly sequentially — the early ones are foundation, the later ones are team-facing.

Each TD entry below is **structural only** — title, what-it-delivers, done-test, dependencies, open questions to resolve before/during execution. The deep architectural detail (which associate, what trigger, what data flow, etc.) gets resolved in a focused alignment conversation BEFORE the TD is executed, and the resolved detail then gets written into the TD section. This way fidelity grows as we work through, rather than being written speculatively at high resolution.

**The trace-as-build-method principle threads through every TD.** Pick a real scenario. Run it manually first via the CLI. Verify entity state ends up correct. Then write the skill / wire the watch / build the UI / activate the autonomous version. The artifact is the writeup of what worked.

**The dogfooding principle threads through every TD.** If we can't use the OS to deliver a TD, we fix the OS until we can.

---

### TD-1 — Adapters running cleanly + historical hydration

**Delivers:** Email + Meeting + Slack + Drive data flowing in continuously to dev OS via four source adapters running on independent schedules. Manual Touchpoint entry via the per-actor assistant for unrecorded interactions. Pre-flight cleanup of Bug #36 + Bug #37 leftover data. Foundation for everything downstream. **No cascade activation yet** — entities sit at `received` / `logged` status waiting for TD-2.

#### What flows in, and what entity each source produces

Per the design discussion: each source-event produces a **discrete entity**; Touchpoints are 1:1 with source-events (immutable snapshots in time, NOT grouped by thread). Threading is metadata, not a primary entity.

| Source | Entity created per event | Threading metadata | Existing or new? |
|---|---|---|---|
| Gmail email | `Email` (one per individual email message, with `thread_id`) | `Email.thread_id` | Existing; Gmail adapter shipped Apr 23 |
| Google Meet meeting | `Meeting` (one per scheduled meeting / conference record) | n/a (meetings are discrete) | Existing; Meet adapter shipped Apr 21 |
| Slack message | `SlackMessage` (one per individual message, with `thread_ts`) | `SlackMessage.thread_ts` | **NEW — adapter to be built** |
| Drive file (standalone) | `Document` (one per Drive file) | `Document.source_folder_path` for context | Drive adapter exists for one-off pulls; need systematic ingestion via fetch-new |
| Email attachment | `Document` (one per attachment, linked to parent Email) | parent Email reference | Created inline by Email adapter when processing attachments |
| Slack file attachment | `Document` (one per file, linked to parent SlackMessage) | parent SlackMessage reference | Created inline by Slack adapter when processing file uploads |
| Manual entry (assistant-driven) | `Touchpoint` directly (with `summary` field populated by user) | n/a | NEW skill on per-actor assistant; uses existing voice/chat harnesses |

**Document entity is source-agnostic.** Whatever fields exist on Document accommodate Drive, email-attachment, Slack-attachment, and manual-upload origins. Adapters extract whatever metadata the source provides and populate generic Document fields. No Drive-specific top-level fields like `source_folder_id` — folder context goes in the existing generic source-metadata field on Document.

#### The four source adapters

##### Email adapter (Gmail) — exists

Already shipped (Apr 23). Pulls Email entities + creates linked Document entities per attachment. Incremental by `since` watermark via Bug #36 fix (Apr 28). Outlook adapter has the same pattern; Bug #36 propagation completed in commit `3fc4b55`.

**Scope:** all 11 team mailboxes, all incoming + outgoing emails since the watermark. Email entities created at status `received`.

##### Meeting adapter (Google Meet) — exists

Already shipped (Apr 21). Pulls Meeting entities from Google Meet conference records via the Google Workspace adapter. Includes structured transcripts (speaker+timestamp), Gemini smart notes, recordings, Calendar attendees. Incremental by `since` watermark.

**Scope:** all team members' meetings (via domain-wide delegation). Meeting entities created at status `logged`.

##### Slack adapter — NEW, to be built

**Architectural choices (resolved):**
- **Scope: all channels.** Craig has Slack admin permission; the OS-Slack app gets workspace-wide access. Adapter pulls every channel. DMs/MPDMs out of scope initially — team uses channels for customer-relevant chatter.
- **Direct Slack API.** Not `agent-slack` (third party). Build the adapter from scratch using Slack's REST API + (later) Events API. Standard pattern matching Outlook/Stripe/Google Workspace adapters in `kernel/integration/adapters/`.
- **Per-message granularity.** One `SlackMessage` entity per individual message. `SlackMessage.thread_ts` captures threading. Touchpoints are 1:1 with SlackMessages (no thread-level grouping).
- **Polling first; Events API later.** Polling cadence as fast as practical (target every 5 min). Move to push/webhook (Slack Events API) post-TD-2 once base data flow is proven.
- **File attachments → Documents.** When a SlackMessage has file uploads, adapter creates linked Document entities (source: `slack_file_attachment`). Document.source enum needs the new value if not already there.

**Adapter responsibilities:**
- OAuth-based authentication via OS Integration entity (system_type: `messaging`, provider: `slack`, owner_type: `org`, secret_ref to AWS Secrets Manager)
- `fetch_new` capability — pull SlackMessages since watermark (most recent `SlackMessage.ts` per channel)
- Per-channel pagination (Slack's `conversations.history` API with cursor)
- Per-message: extract text content, user (sender), channel, timestamp, thread_ts, file attachments
- File attachment processing: create Document with filename, mime_type, size, content (text-extracted where possible), parent SlackMessage reference
- Adapter is "dumb" — no classification logic, no Company resolution. SlackMessages dumped at status `received`; SlackClassifier (TD-2) handles classification.

**Initial backfill:** one-time CLI invocation with explicit `since` (e.g., last 90 days) to populate historical Slack content. Per-channel pagination handles volume.

##### Drive adapter — exists; needs systematic ingestion wired

Drive adapter exists for one-off file pulls. TD-1 wires it for systematic incremental ingestion.

**Architectural choices (resolved):**
- **Pull all of Drive** — not allowlisted folders. Drive becomes a central searchable space. Documents may or may not be customer-relevant; many won't be. That's fine.
- **Documents created with `company = null`** by default. Lazy classification:
  - **At Touchpoint extraction** — IE links the Document to a Touchpoint AND classifies Document.company to the Touchpoint's Company when a Document is referenced (e.g., meeting transcript says "we shared the v1 proposal"). Folder context (`Document.source_folder_path`) serves as a hint at this moment.
  - **Manual via UI** (TD-3) — team browses Documents, assigns Company explicitly. Frequent at first while workflows are being established.
  - **Future workflow-driven** — when documents are created out of tasks assigned to customers, attach automatically. Out of scope for current roadmap.
- **Documents that never get classified** — fine; they live in the central searchable space, queryable by other dimensions (folder, content, type, date). Per principle #3 (no fluff fields), null `company` is honest.
- **Incremental fetch by `modifiedTime` watermark** — same pattern as every other adapter. No special "Drive changes API" complexity. Adapter queries `where modifiedTime > most_recent_document.external_modified_at`.
- **Maximum metadata extraction.** For each Document: folder structure, owner, permissions, mime_type, size, modified time, original filename, extracted text content. All populated through generic Document fields.

**File type handling:**
- Google Docs / Sheets / Slides → native export to text/plain or markdown for content extraction
- PDFs → text extraction (PDF.js, pdfminer, or similar)
- Images → metadata only initially; OCR is a future enhancement
- Videos → metadata only; transcription is a future enhancement
- Files above some threshold (e.g., 100MB) → metadata + pointer to original; no content extraction

**Deletion handling:** Drive file deleted → Document marked deleted (don't hard-delete; preserves audit trail).

#### The four scheduled fetcher actors

Per the design discussion: **one actor per source, deterministic mode (no LLM), trigger_schedule cron, kill-switch each independently.**

| Actor | trigger_schedule | Deterministic skill |
|---|---|---|
| **Email-Fetcher** | every 5 min | Run `indemn email fetch-new` (no params); adapter handles incremental via watermark |
| **Meeting-Fetcher** | every 15 min | Run `indemn meeting fetch-new`; adapter handles incremental |
| **Slack-Fetcher** | every 5 min (polling) | Run `indemn slackmessage fetch-new`; adapter paginates per channel; later replaced by Slack Events API webhook |
| **Drive-Fetcher** | every hour | Run `indemn document fetch-new`; adapter queries by modifiedTime watermark |

**Pull-as-fast-as-possible philosophy.** Cadences are aggressive. Each actor's skill is trivial (single CLI call). API rate limits are the practical ceiling — if we hit them, we back off; otherwise pull frequently.

**Recurring vs. backfill.** Same actor handles both. Recurring is automatic via schedule. Backfill is human-initiated via CLI with explicit `since`/`until` params (e.g., `indemn meeting fetch-new --data '{"since": "2026-04-01", "until": "2026-04-29"}'`). For Meetings: 30-day backfill once. For Slack: 90-day backfill once after adapter is built.

**Kill-switch.** Each actor can be transitioned to `suspended` independently. The cascade activation order in TD-2 starts with everything suspended; we activate progressively.

#### Manual Touchpoint entry flow

Per the design discussion, manual entry **uses the existing OS-level per-actor assistant pattern**, not custom infrastructure. Each team member has their own `default_assistant` associate (kernel-provisioned), surfaced in the UI via Deployment, runs through the chat-deepagents (web) or voice-deepagents (voice) Runtime.

**New domain skill: `log-touchpoint`** — added to each team member's assistant's skills list. The skill instructs the assistant:
- When the user wants to log a touchpoint (manually-recorded call, in-person interaction, anything not auto-ingested), collect:
  - Participants (resolve as Contacts/Employees via `indemn contact entity-resolve` / `indemn employee entity-resolve`)
  - Customer Company (resolve via `indemn company entity-resolve`)
  - Date / time
  - Scope (external vs. internal)
  - Summary (the user's free-text recap)
- Once collected, the assistant calls `indemn touchpoint create --data '...'` with all fields populated.
- The Touchpoint cascades through IE → Proposal-Hydrator just like an automated one — IE reads `Touchpoint.summary` for source content (no source_entity_id needed since the assistant provided summary directly).

**Voice harness refinement** — flagged as TD-1 sub-piece. Per Craig: we haven't actually tested or used the voice harness much. Likely needs work before push-to-talk manual-entry is reliable. Scope: confirm voice harness wires up correctly, test end-to-end with a `log-touchpoint` skill, refine as needed.

**ManualTouchpoint entity deferred.** A "manually recorded touchpoint" entity that goes through SC/MC/EC-equivalent classification was considered but deferred. The simpler assistant-creates-Touchpoint-directly flow works for now. Revisit if assistant-driven flow hits limits.

#### Pre-flight cleanup (Bug #36 + #37 leftover data)

Must complete before any TD-2 cascade activation. Otherwise TD-2's progressive activation would inherit dirty data.

- **Bug #36 side-effect: 500 unrelated Emails + 6 unrelated Meetings on Kyle's mailbox.** Bulk-delete (clean slate, per Craig). Use `indemn email bulk-delete` and `indemn meeting bulk-delete` with appropriate filters (e.g., `created_at` range matching the broken-adapter-run window).
- **Bug #37 data side: 2 malformed Email rows** (`69ea548e…6e92` Oneleet, `69ea556f…7387` Linear Orbit). Delete via `indemn email delete <id>`.

#### Sub-pieces (concrete work to do)

1. **Bug #36 + #37 cleanup** — bulk-delete pre-flight
2. **Email-Fetcher actor** — create + configure (trigger_schedule: every 5 min); deterministic skill; activate
3. **Meeting-Fetcher actor + 30-day backfill** — create actor; one-time backfill; activate recurring
4. **Slack adapter (NEW)** — full build:
   - OS Integration entity for Slack workspace + secret_ref
   - `kernel/integration/adapters/slack.py` — implements Adapter base class, fetch-new for SlackMessages with file-attachment processing, OAuth flow, channel pagination
   - Tests
   - Self-register adapter in `kernel/integration/adapters/__init__.py`
   - SlackMessage entity definition (if not already exists) — fields: text, user, channel, ts, thread_ts, file_attachments references
   - 90-day backfill one-time
   - Slack-Fetcher actor (every 5 min); activate recurring
5. **Drive ingestion** — wire systematic fetch-new on existing Drive adapter; Document entity additions if any (review existing fields first); Drive-Fetcher actor (hourly); one-time backfill with no `since` (pulls everything in scope); activate recurring
6. **`log-touchpoint` skill** — written and assigned to each team member's default_assistant
7. **Voice harness verification + refinement** — confirm chat-deepagents + voice-deepagents Runtimes work; test end-to-end manual entry via voice
8. **Document.source enum check** — confirm `slack_file_attachment` is in the enum (was an open from prior session); add if missing

#### Activation order

Bottom-up per the OS bug-cleanup-first principle:

1. Pre-flight cleanup (Bug #36 + #37) — complete before any actor activation
2. Email-Fetcher activated — already-functional Gmail adapter; lowest risk; verify it pulls cleanly
3. Meeting-Fetcher activated — same; plus run 30-day backfill manually first to populate historical
4. Drive-Fetcher activated — Drive adapter exists; one-time backfill; then recurring
5. Slack adapter built (multi-day work) — backfill 90-day once built; Slack-Fetcher activated
6. `log-touchpoint` skill deployed to assistants; voice harness verified

After all 4 fetcher actors active + adapters working + manual entry path live: TD-1 is done. Cascade is still suspended; TD-2 takes over.

#### Done-test

- All 4 fetcher actors active with their `trigger_schedule` running
- New Email/Meeting/SlackMessage/Document entities appear in dev OS within their configured cadence
- 30-day Meeting backfill complete; 90-day Slack backfill complete; full Drive crawl complete
- Pre-flight cleanup verified: 0 unrelated emails/meetings from Bug #36; 2 malformed rows from Bug #37 deleted
- A team member can talk to / chat with their UI assistant and successfully log a Touchpoint via the `log-touchpoint` skill
- Document.source enum includes `slack_file_attachment`
- All entities sit at appropriate `received` / `logged` status — cascade NOT activated (EC/TS/IE remain suspended; MC/SC/Proposal-Hydrator/Company-Enricher don't exist yet)

#### Dependencies

- **No upstream TD dependencies** — TD-1 is the foundation
- **OS bug fixes already in place** — Bug #36 fix (`477a98f`, propagated to Outlook in `3fc4b55`); Bug #34 CLI fix (`db97694`); LangSmith tracing (`956d7d5`); skills-via-CLI refactor (`7281b83`)
- **Slack workspace admin permissions** — Craig grants the OS-Slack app workspace-wide access
- **AWS Secrets Manager** — Slack credentials at `indemn/dev/integrations/slack-oauth` (or similar path)
- **Existing Runtime infrastructure** — chat-deepagents + voice-deepagents Runtimes deployed (already on Railway)

#### Out of scope for TD-1

- **The cascade activation** — TD-2. EC/TS/IE/MC/SC/Proposal-Hydrator/Company-Enricher all remain suspended or unbuilt during TD-1. Data flows IN; no autonomous processing on it.
- **Per-customer constellation UI** — TD-3. UI for browsing Documents, assigning Company manually, etc. lives in TD-3.
- **Slack Events API push** — TD-1 starts with polling; Events API webhook migration is post-TD-2.
- **DM ingestion** — out of TD-1 scope. Team uses channels for customer-relevant chatter.
- **OCR / video transcription** — Drive ingestion handles text-extractable file types; OCR + video transcription are future enhancements.

---

### TD-2 — Cascade activated progressively

**Delivers:** A 7-associate cascade running autonomously on incoming Email/Meeting/Slack data. Every interaction flows through it, every entity emerges from it, the Proposal entity continuously hydrates as a side-effect. The spine of the customer system.

#### What the cascade does

When an Email, Meeting, or Slack thread arrives in dev OS (via TD-1 adapters), it cascades through:

```
Source entity created (Email | Meeting | Slack thread)
  → [EC | MC | SC]                        Source classifier (one fires per source type)
    → Source classified (Company + Contacts linked)
      → TS                                 Source-agnostic Touchpoint creator (folds Deal-creation)
        → Touchpoint logged (+ Deal + empty Proposal if needed, atomic)
          → IE                              Source-agnostic intelligence extractor
            → Touchpoint processed
              → Proposal-Hydrator           Aggregates extracted entities into the Proposal
              → Company-Enricher            (parallel, separate trigger — fills bare Companies)
```

By the time the cascade finishes for a single Email/Meeting/Slack thread, the customer constellation has gained: a Touchpoint with Option B source pointers; potentially a new Contact (with signature-parsed fields); potentially a new Company (Hard-Rule-#1 inverted: resolve-before-create, autonomous create on 0/0); potentially a new Deal at CONTACT or DISCOVERY (with empty Proposal attached); extracted intelligence (Decisions, Tasks, Commitments, Signals, Operations, Opportunities, Phases linked to the Touchpoint and the Deal); the Proposal entity updated with new entity references; the Company auto-enriched with any new structured info from the source.

#### The 7 associates — why each exists

Per the principle established in this design conversation: **a new associate is justified only when the trigger, entities used, context, or skill are significantly different from existing associates.** One associate can have multiple skills; one trigger should be one associate; decouple things separate in nature.

| Associate | Trigger | Writes | Why separate |
|---|---|---|---|
| **EmailClassifier (EC)** — exists, v9 | `Email created` | Email.company, Email.sender_contact, Email.status | Email-specific relevance filter (spam/newsletter/real); Hard-Rule-#1-inverted resolve-before-create logic; signature parsing for richer Contact fields. **Will absorb signature parsing.** |
| **MeetingClassifier (MC)** — new | `Meeting created` | Meeting.company, Meeting.attendees_contacts, Meeting.attendees_employees, Meeting.scope, Meeting.status | Meeting data shape is fundamentally different (structured attendee list from Google Meet API; transcript; usually pre-classified as relevant); reasoning is "resolve attendees + identify customer Company from external attendees" not "filter spam". |
| **SlackClassifier (SC)** — new | `SlackThread created` | SlackThread.company, SlackThread.participants_contacts, SlackThread.participants_employees, SlackThread.scope, SlackThread.status | Slack context (channel name, DM/MPDM membership) is different from email/meeting; relevance filtering is needed (much off-topic noise); thread-vs-message granularity is different. |
| **TouchpointSynthesizer (TS)** — exists, v6 (will gain Deal-creation) | `Email/Meeting/SlackThread classified` (3 watches) | Touchpoint (created), Email/Meeting/SlackThread.touchpoint, Deal (created if external + no active Deal), Proposal (created empty if Deal created), ReviewItem (if multi-Deal ambiguity for internal scope) | Source-agnostic — one Touchpoint shape regardless of source type. Folds Deal-creation atomically because Deal exists in our model purely as the carrier for a Proposal — they co-evolve. Same trigger as Touchpoint creation, same context (the source + Company + Contact). |
| **IntelligenceExtractor (IE)** — exists, v3 | `Touchpoint logged` | Decision, Task, Commitment, Signal, Operation, Opportunity, Phase (all created and linked to Touchpoint + Deal), Touchpoint.status (transitions to processed) | Source-agnostic — reads source content via Option B navigation, extracts structured intelligence. Different from Classifiers (those classify a single source; IE creates many entities) and from TS (TS doesn't read source content). |
| **Proposal-Hydrator (PH)** — new | `Touchpoint processed` | Proposal (updated — new entity references added), Proposal.status (potentially advanced), ReviewItem (if extracted entity doesn't fit cleanly) | Aggregates extracted entities INTO the Proposal entity. Different context from IE (IE reads source content; PH reads aggregated entity graph + Playbook). Different reasoning (IE extracts from text; PH consolidates from entities). Different writes (IE creates many entities; PH updates one Proposal entity by adding references). |
| **Company-Enricher (CE)** — new | `Touchpoint logged` for a Company with bare data (or scheduled cron) | Company (updated — fields filled from source content) | Different from IE (IE writes intelligence entities; CE updates Company directly). Different concern (intelligence-extraction vs Company-profile-completion). Triggers in parallel with IE — no conflict because they write to different entities. |

**Why not fewer than 7?** Folding more responsibilities into existing associates would: (a) conflate triggers that aren't actually the same trigger; (b) create context bloat per LLM call (IE would need to know about Proposals AND Companies AND extraction); (c) make failure modes harder to debug (one associate failing affects multiple concerns); (d) violate the "one trigger per associate" principle.

**Why not more than 7?** Splitting further would: (a) over-fragment work that shares context (e.g., splitting "extract Decisions" from "extract Tasks" into separate associates would duplicate source-reading); (b) increase cascade coordination complexity for no decoupling gain; (c) stretch the cascade depth (we'd be at 6-8 levels deep, and while the kernel circuit breaker is at 10, depth has practical observability cost).

The 7 associates correspond to 7 fundamentally different (trigger, entities, context, reasoning) tuples. That's the right number.

#### ReviewItem — universal escape valve for human review

Per the design decision in this conversation: **any associate that encounters any issue while working creates a `ReviewItem` and continues. It never blocks. It never throws. It creates a ReviewItem, makes its best-effort write, and moves on.**

This is a foundational pattern, not a narrow one. Use cases include but are not limited to:
- EC: ambiguous Company match (multiple at score 1.0)
- EC: 0 candidates AND signature-parse can't determine company affiliation
- MC: meeting attendees include unfamiliar emails that don't clearly resolve to any Contact/Employee
- SC: thread relevance unclear; mentioned customers ambiguous
- TS: multi-Deal ambiguity for internal Touchpoint (assigns to latest Deal + creates ReviewItem)
- TS: scope determination unclear (could be external OR internal)
- IE: source content references entities that don't exist (e.g., "the BT Core integration" — no CustomerSystem entity for it yet)
- IE: extracted Decision conflicts with prior recorded Decision
- Proposal-Hydrator: extracted Operation doesn't fit any existing Phase, and Playbook doesn't suggest one
- Company-Enricher: source mentions critical fields that need confirmation (e.g., "they're at $35M ARR" — should this update Company.annual_revenue?)

**ReviewItem entity structure:**
- `target_entity_type: str` — what entity needs review (Touchpoint, Email, Company, etc.)
- `target_entity_id: ObjectId` — which one
- `created_by_associate: str` — which associate flagged it (for triage + improvement signal)
- `reason: str` — why it needs review (free-text or enum like `ambiguous_match`, `multi_deal_internal`, `unfamiliar_reference`, etc.)
- `context: dict` — the data the associate had when it encountered the issue (e.g., the candidate IDs, the source quote)
- `proposed_resolution: str` (optional) — what the associate did as best-effort, so reviewer can accept/override
- `status: "open" | "in_review" | "resolved" | "dismissed"`
- `resolved_by_actor_id: ObjectId` (when reviewed)
- `resolution: str` (what the reviewer did)

**Reviewer role** — has watches on `ReviewItem created`. Anyone in this role gets messages. Reviewer can claim, look at the linked entity, fix anything wrong (e.g., reassign a Touchpoint to a different Deal), and transition the ReviewItem to `resolved` or `dismissed`.

**Why this is THE pattern:**
1. Associates never block — the cascade always completes its best effort
2. Visibility — every uncertain decision is surfaced, not buried in a `needs_review` state on the underlying entity
3. **Reviewing IS training data** — the corrections reviewers make become signal for the next iteration of the associate's skill or rules. Over time, patterns reviewers correct get codified into deterministic rules (the `--auto` flywheel from `rules-and-auto.md`)
4. Generic — works across all entity types and all associates without polluting individual schemas with `flag_for_review` fields

**Source-classifier exception:** EC, MC, SC are slightly different. If they cannot classify at all (0 Company candidates with no signal, sender domain unknown, attendee list all-external-but-unidentifiable), the source entity transitions to `needs_review` (terminal in the cascade — TS won't fire) and a ReviewItem is created. The cascade halts at that source until the reviewer resolves it. This is the one place we accept blocking, because proceeding without classification would create wrong downstream entities.

For all other associates (TS, IE, Proposal-Hydrator, Company-Enricher): best-effort + ReviewItem + continue. No blocking.

#### Proposal-Hydrator nuance: stages are fluid

Per the design conversation, the Proposal-Hydrator's logic is NOT "use Playbook[Deal.stage].required_entities as a hard schema and only add entities matching the schema." That's too rigid because conversations are fluid — a DISCOVERY-stage email might surface PROPOSAL-stage information; a NEGOTIATION-stage call might contain DEMO-stage questions.

Instead, Proposal-Hydrator's logic:
1. Read entities IE just extracted on this Touchpoint
2. For each extracted entity, determine if it fits the Proposal structure:
   - Operation extracted? Link to Proposal.operations
   - Opportunity extracted with a mapped AssociateType? Link to Proposal.opportunities
   - Phase extracted? Link to Proposal.phases
   - Decision/Commitment/Task/Signal? Already linked to Touchpoint and Deal — Proposal references Deal so they're transitively visible; no explicit Proposal-link needed
3. Read `Playbook[Deal.stage].required_entities` as guidance, NOT schema:
   - If the extraction added entities that the current stage didn't expect, that's interesting (might suggest the Deal should advance to next stage, or the Playbook needs refinement) — flag via ReviewItem
   - If the current stage's required_entities aren't yet populated, don't error — just leave them empty (constellation UI will show them as gaps signaling next-actions)
4. Update `Proposal.status` if appropriate (e.g., all DISCOVERY required_entities now populated → Deal can advance to DEMO; this is a signal, not an automatic transition — Deal stage transitions are human-initiated for now)

The Proposal entity is mostly references to other entities, not free-text — per principle #3 (no fluff fields). Proposal-Hydrator does not write narrative descriptions; the narrative emerges from the linked entities.

#### Sub-pieces (work to do)

1. **ReviewItem entity definition + Reviewer role** (pre-flight infrastructure for everything below)
2. **MC (MeetingClassifier) skill + role + watch + actor** — including manual trace on a real meeting (e.g., the Apr 28 Armadillo discovery call)
3. **SC (SlackClassifier) skill + role + watch + actor** — depends on TD-1 Slack adapter complete
4. **EC update** — fold signature parsing into the Contact-creation step; add ReviewItem creation on ambiguity (replacing the current "transition to needs_review and stop" pattern for non-source-classification ambiguity); ensure compatibility with v9's Hard-Rule-#1 inversion
5. **TS update** — fold Deal-creation logic; auto-create empty Proposal when creating Deal; handle internal-scope multi-Deal ambiguity via ReviewItem
6. **IE verification** — already active, but verify it works through the full cascade with TS-created Touchpoints + Option B source pointers; trace manually on Armadillo
7. **Proposal-Hydrator skill + role + watch + actor** — including manual trace on Armadillo's processed Touchpoints
8. **Company-Enricher skill + role + watch + actor** — including manual trace on Armadillo's bare Company
9. **Activation, in bottom-up order** — see below

#### Activation order: bottom-up

Per the trace-as-build-method principle and Craig's "be careful not to have a cascade happen when we're not ready" guidance, activate from the bottom of the cascade upward. Each level proves before the next is built. This way the foundation is verified at each step, and we avoid the dirty-cascade-on-unverified-data scenario.

**Pre-flight (must complete before any activation):**
- Bug #36 cleanup: 500 unrelated Emails + 6 unrelated Meetings — either delete or transition to `irrelevant`
- Bug #37 row cleanup: 2 malformed Email rows
- ReviewItem entity definition created in dev OS
- Reviewer role created with watches on `ReviewItem created`

**Activation sequence:**

1. **EC** — already at v9, verified live on Armadillo. Fold in signature parsing (skill update). Fold in ReviewItem creation for non-source-classification ambiguity. Drain a small batch of test emails. Confirm the new behavior. Then activate recurring (TD-1's recurring fetch can turn on after this).
2. **MC** — trace manually on the Apr 28 Armadillo discovery meeting. Verify attendee resolution, Company identification, scope classification. Write skill. Wire watch + role. Drain a small batch of Meetings. Activate.
3. **SC** — depends on TD-1 Slack adapter complete. Trace manually on a real Slack thread (e.g., the Apr 7-8 Retention Associate prep thread for Alliance). Verify channel-context-aware classification. Write skill. Wire. Drain. Activate.
4. **TS** — currently at v6, suspended. Fold in Deal-creation + empty Proposal creation + internal-scope multi-Deal ambiguity → ReviewItem. Trace manually on a classified Email/Meeting/SlackThread → produced Touchpoint + Deal + Proposal. Update skill (v7). Drain a small batch. Activate.
5. **IE** — currently active. Verify it works through the full cascade with TS-created Touchpoints + Option B source pointers + the fact that Deal/Proposal now exist. Trace manually on Armadillo's Touchpoints (already extracted, but re-verify). Optionally update skill if the Proposal-existence changes its work. Continue active.
6. **Proposal-Hydrator** — trace manually on Armadillo's processed Touchpoints. Confirm extracted entities link correctly to Proposal. Confirm fluid-stage handling (entities extracted that the current stage didn't expect → ReviewItem). Write skill. Wire watch + role. Drain. Activate.
7. **Company-Enricher** — trace manually on Armadillo's bare Company. Confirm enrichment logic. Decide trigger (event vs cron — default to event-triggered on `Touchpoint logged` for a bare Company). Write skill. Wire. Drain. Activate.

After all 7 are active, run the done-test (below).

#### Done-test: systematic historical replay

Rather than waiting for one new prospect's first email, we systematically replay the historical data through the cascade as if it's happening in real time:

1. We have ~930 emails + ~67 meetings already in dev OS (un-cascaded or partially-cascaded). Plus future Slack hydration from TD-1.
2. Reset relevant entities to `received`/`logged` state where needed.
3. Use the kernel `reprocess` primitive (Bug #10 closeout, commit `662dc2d`) to emit the watch-trigger for each Email/Meeting/SlackThread, in chronological order.
4. Observe the cascade fire end-to-end on each one. Watch LangSmith traces. Verify:
   - Source classification is correct (Company + Contacts/Employees linked)
   - Touchpoint created with proper scope + source pointers
   - Deal + Proposal auto-created when appropriate
   - Intelligence extracted (Decisions/Tasks/Commitments/Signals/Operations/Opportunities/Phases)
   - Proposal updated with entity references
   - Company enriched
   - ReviewItems created where the cascade hit ambiguity
5. Spot-check the resulting constellation for ~3 customers (Alliance, Armadillo, GR Little, plus any new ones that emerged in the historical replay) — does the picture match what we know about each?

**Done when:** historical replay completes cleanly across the full dataset, the constellation for each known customer looks correct, the ReviewItem queue is reasonable (mostly genuine edge cases, not systemic failures).

This gives us 1000+ data points of cascade verification, surfaces edge cases the design didn't anticipate, hydrates the constellation for many customers naturally as a side-effect, and produces concrete material for the TD-3 UI to render.

#### Dependencies

- **TD-1 complete** — adapters running, data available in dev OS, Bug #36 + #37 cleanup done.
- **ReviewItem entity + Reviewer role** — pre-flight infrastructure. Created before any associate activation.
- **Hard Rule #1 inversion** — already done in EC v9 (Session 12).
- **LangSmith tracing** — already wired (Session 10).
- **Reprocess primitive** — already shipped (Bug #10 closeout, commit `662dc2d`).
- **Sources need to be fully ingested** — Email + Meeting + Slack adapters from TD-1, plus Drive ingestion for documents that get linked to Touchpoints.

#### Out of scope for TD-2

- **Artifact Generator** — TD-5. The cascade ends with the Proposal entity hydrated; producing draft artifacts (follow-up emails, recaps, proposal decks) is downstream.
- **UI** — TD-3. The cascade populates the entity graph; visualizing it for the team is downstream.
- **Manual entity creation paths** — TD-1 (UI form + voice/talk-to-add). The cascade handles autonomous ingestion; manual paths bypass Classifier+TS but still trigger IE.
- **External-customer multi-tenancy** — TD-11. The cascade is built for Indemn-the-company in the `_platform` org.

---

### TD-3 — Customer constellation queryable + per-customer UI

**Delivers:** A custom React + Vite + shadcn UI layer over the OS API that visualizes the customer constellation. The team can open the UI, see a personalized dashboard, navigate to any customer's full picture, browse meetings/documents centrally, and interact with their per-actor assistant via chat or voice. Replaces "ask Kyle" for understanding any customer. Replaces the team's siloed search across Gmail, Google Meet recordings, and Slack for finding documents.

#### Stack + architecture (resolved)

- **Tech stack: React + Vite + shadcn.** Matches the conventions Ganesh is using in his customer-success repo (`https://github.com/ganesh-iyer/implementation-playbook`). Component-level architecture after auditing his repo to align with his specific structure, file organization, and component patterns.
- **Visual language: GR Little / Alliance trace-showcase HTML aesthetic.** Iris/lilac accents, Barlow font, generous whitespace, sectioned cards, dark-on-cream text. The visual system Cam and Kyle have validated. shadcn provides the primitive components; we style them to match.
- **API access: direct OS API.** No "customer-system UI adapter." UI is a thin surface on top of the customer system on the OS. Every API call uses existing `/api/{collection}/...` endpoints. Auth via JWT session token from existing OS auth.
- **Hosting: Railway or Amplify (frontend).** Static SPA build deployed independently of the OS API. Separate domain (e.g., `customer.os.indemn.ai`) or alongside `os.indemn.ai`.
- **AI assistant: reuse chat-deepagents + voice-deepagents harnesses.** The per-actor `default_assistant` associate, configured via Deployment for the UI surface (web Deployment for chat, voice Deployment for push-to-talk). The OS Base UI already has this pattern wired (refinement opportunity post-async-deepagents skills-via-CLI refactor in commit `7281b83` — apply those lessons to the chat/voice harnesses).
- **Real-time: WebSocket** subscriptions per active page, filtered by relevance (per-customer page subscribes to `Company:{id}` + entity changes related to that company). Aligns with existing OS real-time architecture (`indemn-os/docs/architecture/realtime.md` — cross-reference during execution).
- **Auth + org-scoping:** uses existing OS auth (JWT). All data automatically scoped to actor's `org_id` per kernel `find_scoped` pattern. UI doesn't think about org isolation.
- **Mobile: responsive.** Sections stack on narrow viewports; pills wrap; cards become full-width.

#### Page list (7 pages)

| Route | Purpose |
|---|---|
| `/` | **Personalized dashboard** — role-aware widgets + assistant prominent |
| `/customers` | Customer list (browse all Companies) |
| `/customers/<id>` | **Per-customer constellation** (the meaty 5-section page; central artifact) |
| `/meetings` | Meetings list (browse all meetings, internal + external) |
| `/meetings/<id>` | Per-Meeting detail (= per-Touchpoint detail with meeting-specific affordances) |
| `/touchpoints/<id>` | Per-Touchpoint detail (deep-linkable; less commonly entered from list pages) |
| `/documents` | Documents browse (central searchable space — Drive + email-attachments + Slack-attachments + manual) |
| `/documents/<id>` | Per-Document detail (content preview, metadata, "Assign Company" action) |

ReviewItems surfaced contextually within customer/document pages rather than a dedicated page. Can add `/reviews` later if reviewing volume warrants it.

#### Per-customer constellation page detail (the central artifact)

Single-scrolling page. Mirrors the trace-showcase HTML's 5-section spine, with each section adapted to render live entity data with WebSocket updates. Inline timeline expansion (click a Touchpoint → expands below).

##### Section 1 — Customer hero

- **Company name** as headline (large)
- **Domain + summary blurb** — pulled from Company entity description if populated
- **Current Deal stage badge** with iris/lilac styling (CONTACT / DISCOVERY / DEMO / PROPOSAL / NEGOTIATION / VERBAL / SIGNED)
- **Key Contacts** — chip cards showing primary Contacts (name + title from signature parsing + click → Contact detail)
- **Owner** — from `Deal.next_step_owner` or similar
- **Last touchpoint** — relative date + source-type icon
- **Live cascade indicator** if a new Touchpoint is currently being processed for this customer
- **Action affordances** — "Log Touchpoint" (calls assistant `log-touchpoint` skill), "Generate Proposal v(n+1)" (initiates Artifact Generator from TD-8 — async OR opens chat/voice session per Craig's flexibility-of-deployment principle), "View Proposal PDF"
- WebSocket subscription: `Company:{id}` + `Deal:{id}` change events

##### Section 2 — Touchpoint timeline (the spine)

- **Vertical timeline, newest at top.** Vertical line down the left, dots per Touchpoint
- **Each Touchpoint row collapsed:** timestamp (relative + absolute on hover), source-type pill (Email/Meeting/Slack/Manual), scope pill (External/Internal), one-line `summary`, participant chips, linked Document chips
- **Click row → expands inline** with: source content snippet (email body excerpt / meeting transcript first ~500 chars / Slack message + thread context / manual summary); extracted intelligence cards (Decisions/Tasks/Commitments/Signals/Operations/Opportunities, each linked to its entity); linked Documents; linked Phase if extracted; actions ("Re-extract", "Flag for review", "View source")
- **Threading visualization:** subtle connector line / indent for same-`thread_id` Touchpoints (visual grouping without changing data model — Touchpoints stay 1:1 with source-events per TD-1)
- **Filters at top:** source-type, scope, date range, participant, Touchpoint state
- **Real-time:** WebSocket on `Touchpoint:created` filtered by `company={id}`; new Touchpoints appear at top with brief highlight animation. Cascade-in-progress indicator if new Email/Meeting/SlackMessage just landed and EC/TS hasn't fired yet
- **Performance:** initial render 25-50 most recent Touchpoints; lazy-load older as user scrolls. Matters for customers with 100+ Touchpoints (Alliance has 60+)

##### Section 3 — Constellation panel (structured-data side)

- Collapsible sub-sections per entity type, each with count + summary preview, expands to full list:
  - **Contacts** — name, title, email, days-since-last-touch, linked-Touchpoints count
  - **Operations** — name, frequency/scale, source-Touchpoints provenance
  - **Opportunities** — description, mapped AssociateType, status (`unmapped → mapped → validated → proposed → addressed → resolved`), source Touchpoints
  - **CustomerSystem** — tools/systems they use (BT Core, Applied Epic, Dialpad, etc.) + linked Operations
  - **Documents** — name, mime_type, source pill (Drive/email_attachment/Slack/manual), date, "Assign Company" action if `company` is null
  - **Phases** — Proposal phases (name, scope, status, investment)
  - **Decisions** — text, source Touchpoint, date
  - **Signals** — type pill (health/expansion/champion/churn_risk/blocker/insight), description, source Touchpoint, sentiment
- **Provenance per entity:** every linked entity shows which Touchpoint(s) extracted it (small chip with source-type icon, click → jumps to that Touchpoint in Section 2)
- **Actions:** click entity → entity detail; per-section "Add new" (assistant or simple form for manual entry); cross-section filter "show only entities from Touchpoint X"

##### Section 4 — Stage progression panel (where we are)

**Descriptive status, not prescriptive gating.** Per Craig's clarification, the populated-entities list is a status display showing what's been collected at this stage; it's NOT the criteria for stage advancement. Stage transition criteria will be defined separately in TD-4 research and incorporated into this section later.

- **Horizontal stage strip:** CONTACT → DISCOVERY → DEMO → PROPOSAL → NEGOTIATION → VERBAL → SIGNED
- **Current stage** highlighted with iris accent ("you are here")
- **Past stages** marked done with transition date; skipped stages rendered honestly (e.g., Alliance jumped DISCOVERY → PROPOSAL — "Demo skipped")
- **Days at current stage** subtle indicator (becomes a staleness signal)
- **Click past stage → expands** to show what happened during that stage (Touchpoints, entities created, Decisions)
- **Current-stage detail:**
  - **What's been populated at this stage** — descriptive status: "DISCOVERY entities populated so far: 3 Operations, 2 Opportunities, 5 Decisions, 7 Signals"
  - **Expected next moves** (from `Playbook[Deal.stage].expected_next_moves`) — list rendered as suggestions, each clickable to log a Touchpoint or trigger artifact generation
  - **Artifact intent at this stage** — what the Artifact Generator (TD-5/TD-8) is expected to produce; PROPOSAL stage links to current Proposal entity; DISCOVERY stage links to follow-up email draft if generated
- **Stage transition affordance:** "Advance to next stage" button — manual decision, no entity-completion gate. Future (post-TD-4): incorporate stage criteria when defined
- **Real-time:** subscribes to `Deal:{id}` state-transition events; required-entity creates filtered by Deal

##### Section 5 — Proposal-as-spine panel (the destination)

- **Status badge** — drafting / under_review / sent / accepted / rejected / superseded (Proposal entity state machine, including `superseded` transition added in TD-6)
- **Version history bar** — v1 → v2 → v3 etc. with statuses; click a version → see that snapshot
- **Phases section** — for each Phase: name + scope, linked Operations + Opportunities + AssociateTypes (chips clickable to entity), investment, status (proposed / accepted / in-flight / complete)
- **Empty / TBD fields rendered honestly** — for early-stage Deals with mostly-empty Proposals: "No phases defined yet — DISCOVERY in progress, phases will populate as Opportunities are identified." Per principle #3, no fluff narrative; the entity structure shows what's known vs unknown
- **Investment summary** — rolled up from Phases
- **Linked source Document** — link to rendered PDF if exists (e.g., Alliance v2 PDF in Cam's Drive folder)
- **Actions:**
  - **"Generate new version"** — initiates Artifact Generator (TD-8). Per Craig's flexibility-of-deployment principle: can run async (auto-draft, queue for review) OR open a realtime chat/voice session for iterative work with the human
  - **"View PDF"** — opens rendered Proposal PDF
  - **"Edit manually"** — manual override; opens entity editor on Proposal
  - **"Send to customer"** — one-click email send via Email integration (action lives here but functionality is TD-7)
- **Real-time:** subscribes to `Proposal:{id}` change events; new Phase/Operation links appear live as cascade fires

#### Personalized dashboard (`/`) detail

The home is **NOT a customer list.** It's a per-actor, role-aware dashboard with entity widgets + the assistant as a core integrated element.

##### Dashboard composition

Same primitive entity-rendering components, different arrangements per role. Examples:

| Role | Prominent widgets |
|---|---|
| **Cam** | Proposals queue (drafts to review, sent awaiting response, ready-to-render) · Customer prep for upcoming meetings · Documents pending classification · Recent Touchpoints across his customers |
| **George** | Upcoming meetings (next 24-48h) with prep affordance · Customers needing attention (stale Touchpoints) · Recent customer activity · Open Commitments owed to George |
| **Kyle** | Pipeline overview (all customers with stage + days-since-last-touch + value) · Recent Decisions across customers · Recent Signals (especially churn_risk + champion) · Open ReviewItems flagged for his attention |
| **Ganesha** | Customer-implementation status · Delivery Tasks · Phase progression on active Proposals · Open technical Commitments |
| **Peter** | Open technical Tasks · Customer-system data status · Recent Slack threads in implementation channels |

Layout primitives are the same (entity widgets, list/card components); each role gets a different default arrangement. Roles can be customized later if individuals want different defaults.

##### Assistant integration on the dashboard

- **Primary input element at top** — bigger and more prominent than other pages. The assistant is the first thing the eye lands on
- **Recent assistant actions widget** — what the assistant has been doing autonomously (e.g., "Drafted follow-up email for Armadillo," "Flagged 2 ReviewItems for your attention")
- **Proactive surfacing** — the assistant proactively raises things ("3 customers no contact in 14 days — want to draft check-ins?") rendered as suggestions the actor can accept/dismiss
- **Quick-action chips** — common skills rendered as one-click affordances (`log-touchpoint`, `assign-company-to-document`, `prep-for-meeting`, `summarize-customer`, etc.)

##### Dashboard real-time

- WebSocket subscription per widget filtered by relevance (e.g., Pipeline widget subscribes to all `Deal` changes for org; Recent Touchpoints widget subscribes to `Touchpoint:created` org-wide)
- Widgets refresh independently; no full-page reloads
- Assistant's recent actions stream in via the chat-deepagents harness's existing event mechanism

#### Other pages (lower-density coverage — they're simpler than the per-customer page)

##### `/customers` — Customer list

- Table of all Companies. Columns: name, current Deal stage, last touchpoint (relative date), days-since-last-touch, owner, # Touchpoints
- Sort/filter on any column; search by name
- Click a row → per-customer constellation page
- Real-time: last-touchpoint dates + Deal stage update live
- Pure navigation surface — no analytical depth (that's TD-7's pipeline view)

##### `/meetings` — Meetings list

- Browse all meetings (across all customers + internal)
- Filterable by date range, customer, attendee, scope (external/internal)
- Each row: date, title, attendees (chips), customer (link), summary preview
- Click → per-Meeting detail
- Addresses real team gap: today's tools (Apollo / Granola / Google Meet) are siloed; this is the unified view

##### `/meetings/<id>` — Per-Meeting detail

- Same architecture as per-Touchpoint detail, with meeting-specific UI affordances:
  - Transcript player (if recording exists)
  - Recording link (Google Meet's recording URL)
  - Gemini smart notes section (rendered)
  - Full transcript (with speaker labels, scrollable, searchable)
  - Attendee chips with role indicators (external Contact vs internal Employee)
  - Linked Touchpoint
  - Extracted intelligence (Decisions / Tasks / Commitments / Signals — per the Touchpoint linked to this Meeting)
  - Navigate-to-customer-constellation affordance
- TD-7 enriches this page later with: stage-appropriate next-step suggestions, draft follow-up artifact (e.g., follow-up email at DISCOVERY), the "per-meeting view" from vision §2 thread A

##### `/touchpoints/<id>` — Per-Touchpoint detail (deep-linkable)

- Standalone page for when inline expansion isn't enough (e.g., 50K-character meeting transcript, large email body)
- Full source content (entire email body / full meeting transcript / full Slack thread context / manual summary)
- All extracted intelligence (every linked entity)
- All linked Documents
- Full Touchpoint metadata
- Navigation back to customer constellation
- Deep-linkable from outside the UI (e.g., from Slack: "see the full Touchpoint at customer.os.indemn.ai/touchpoints/<id>")

##### `/documents` — Documents browse (central searchable space)

- Browse all Documents from any source (Drive / email-attachment / Slack-attachment / manual)
- Filterable by Company (including null), source type, mime_type, folder path (for Drive Documents), date
- Each row: name, mime_type pill, source pill, Company link or "Assign Company" affordance if null, date
- Search by content text (Drive adapter extracts text content per TD-1)
- Pagination + lazy-load for scale (Drive could have thousands of files)

##### `/documents/<id>` — Per-Document detail

- Content preview (rendered for Google Docs / Sheets / Slides / PDFs; metadata-only for images/videos)
- Full metadata (source, folder path, owner, mime_type, size, modified time, original filename)
- **"Assign Company" action** — manual classification path. Per TD-1's lazy-classify story, the team frequently assigns Company to Documents while workflows are being established. This is the primary surface for that
- **CLI-friendly identifier** — copy-button showing `indemn document get <id>` or similar; for pulling the doc into Claude Code or other workflows
- Download link (original file)
- Linked Touchpoints (where this Document was referenced — populated lazily by IE during extraction)
- Linked Company (if assigned)

#### Persistent assistant integration

- **Per-actor `default_assistant` associate** — kernel-provisioned, runs on chat-deepagents (web) or voice-deepagents (voice) Runtime
- **Persistent input element on every page** — always-visible at top (matches OS Base UI pattern)
- **Page context awareness** — when on a customer page, assistant knows which Company; when on a Document page, knows which Document; when on a Meeting page, knows which Meeting
- **Skills loaded:** `log-touchpoint` (TD-1), `assign-company-to-document`, `prep-for-meeting`, `summarize-customer`, `draft-follow-up-email`, etc. Skills accumulate as we build out customer-system capabilities (each TD adds skills to the assistant)
- **Voice path:** push-to-talk via voice-deepagents harness; same skills available
- **Real-time streaming responses** via the chat-deepagents harness's `astream_events` mechanism (per OS architecture — already wired in Base UI; refinements applied based on async-deepagents skills-via-CLI work)
- **Mid-conversation event awareness** — if a new Touchpoint arrives while user is talking to assistant about a customer, the assistant gets notified via the events stream subprocess (per existing OS pattern)
- **ReviewItem surfacing through assistant** — when the team's customers have open ReviewItems, the assistant proactively raises them; user can resolve directly in conversation

#### Real-time architecture

- **WebSocket connection per active page** to OS API's existing real-time endpoint (cross-reference `indemn-os/docs/architecture/realtime.md`)
- **Subscription model:** per-page filter (e.g., per-customer page subscribes to `Company:{id}` + `Touchpoint:created where company={id}` + `Document:created where company={id}` + reverse-related entity creates)
- **Sub-section level updates:** sections within a page subscribe independently (timeline updates without re-rendering hero; constellation panel updates without re-rendering timeline)
- **Disconnect handling:** reconnect with exponential backoff; resync state on reconnect
- **Existing OS WebSocket endpoint** (e.g., `wss://api.os.indemn.ai/api/ws` — verify exact path during implementation)

#### Document classification affordances (lazy-classify story from TD-1)

Per TD-1, Documents created from Drive ingestion + email/Slack attachments default to `company = null`. The UI is THE primary classification surface (alongside IE's lazy linking at touchpoint extraction):

- **Per-Document "Assign Company" button** on `/documents/<id>` — opens a Company picker; resolve via `entity_resolve`; auto-link on single 1.0 match; ReviewItem on ambiguity
- **Bulk-assign affordance on `/documents`** — select multiple Documents, assign same Company in one action
- **Folder-context hints** — when assigning a Drive Document, the UI shows the folder path; if folder name matches a Company name, suggests it as the default
- **The team will use this frequently at first** — per Craig, until autonomous workflows mature, manual classification via UI is the primary path

#### ReviewItem surfacing (contextual)

- ReviewItems created by associates (TD-2 universal escape valve) surface in:
  - **Per-customer constellation page** — small badge on entities with open ReviewItems linking to them; click to expand, resolve, dismiss
  - **Documents page** — ReviewItems for Document classification edge cases surface in-line on the Document row
  - **Dashboard** — Reviewer-role widget shows open ReviewItems
  - **Assistant** — proactively raises ReviewItems for customers the user owns
- No dedicated `/reviews` page for now; can add later if reviewing volume warrants

#### Sub-pieces (concrete work to do)

1. **Audit Ganesh's repo** (`https://github.com/ganesh-iyer/implementation-playbook`) — document conventions: file structure, shadcn component usage, testing approach, state management, routing pattern. Output: a short conventions doc to align our build with his
2. **Audit existing Base UI's chat-deepagents wiring** — what works, what needs improvement post-async-deepagents skills-via-CLI refactor (commit `7281b83`); document refinements to apply
3. **Tech-stack scaffolding** — set up React + Vite + shadcn project matching Ganesh's conventions; routing (probably react-router or similar per his repo); WebSocket client; OS API client wrapper
4. **Authentication flow** — wire JWT auth against existing OS auth; session token handling; logout; role-based UI gating where applicable (e.g., Cam-specific dashboard widgets)
5. **Persistent assistant integration** — chat-deepagents WebSocket connection from the UI; voice-deepagents push-to-talk integration; page-context awareness; real-time response streaming
6. **`/customers/<id>` per-customer constellation page** — the central artifact; 5 sections; matches trace-showcase visual; WebSocket subscriptions per section
7. **`/` personalized dashboard** — role-aware widget composition; assistant prominently integrated; per-role default layouts
8. **Other pages** — `/customers` list, `/meetings` list + detail, `/touchpoints/<id>` detail, `/documents` browse + detail
9. **Document classification affordances** — "Assign Company" actions, bulk-assign, folder-context hints
10. **ReviewItem contextual surfacing** — badges, in-line affordances, dashboard widget, assistant proactive raising
11. **Mobile responsiveness pass** — every page renders cleanly on narrow viewports; sections stack; cards full-width
12. **Deployment** — Railway or Amplify build/deploy pipeline; environment configuration; domain (`customer.os.indemn.ai` or co-located with `os.indemn.ai`)

#### Activation order

Bottom-up: prep audits first, then core infrastructure, then per-customer page (the central artifact), then dashboard, then other pages, then polish.

1. **Pre-flight prep** — audit Ganesh's repo + Base UI; document conventions and refinements
2. **Tech-stack scaffolding + auth + WebSocket** — minimum viable shell
3. **`/customers/<id>` per-customer constellation page** — build all 5 sections; verify against Alliance + Armadillo + GR Little (the 3 hydrated customers); iterate visual to match trace-showcase
4. **Persistent assistant integration** — chat first, voice later; verify with `log-touchpoint` skill
5. **`/customers` list page** — basic table; navigate-to-customer-page
6. **`/` personalized dashboard** — role-aware widget composition; default layouts per role
7. **`/meetings` list + `/meetings/<id>` detail** — meeting-specific affordances
8. **`/documents` browse + `/documents/<id>` detail** — including classification affordances
9. **`/touchpoints/<id>` detail** — for deep-linking
10. **ReviewItem contextual surfacing** — across all relevant pages
11. **Mobile pass** — responsive testing + fixes
12. **Deploy + share** — get team using it; iterate based on feedback

#### Done-test

- All 7 pages render cleanly with real entity data from dev OS (Alliance + Armadillo + GR Little + remaining hydrated customers from TD-5)
- Per-customer constellation page matches the trace-showcase visual (verified by Cam + Kyle eyeball comparison)
- Per-Document "Assign Company" action works end-to-end; team uses it for unclassified Drive Documents
- Real-time updates: a new Touchpoint arriving via TD-1 cascade appears in the relevant per-customer page's timeline within seconds (no refresh needed)
- Persistent assistant works on every page; `log-touchpoint` skill end-to-end via web (chat) and voice (push-to-talk) Deployments
- Personalized dashboard renders different widget arrangements for different roles (verify with at least Cam, George, Kyle role tests)
- Meetings list aggregates all meetings across customers + internal; per-Meeting detail shows transcript + smart notes + linked Touchpoint
- Documents browse lets the team find any Document by name, content text, folder, source, mime_type
- Mobile responsive — every page renders on phone-width viewport
- Deployed at the chosen domain; team accesses it daily

#### Dependencies

- **TD-1 must be complete** — adapters running, data flowing in, manual entry path live. Without data, the UI has nothing to render
- **TD-2 must be complete or substantially in flight** — cascade producing entities (Touchpoints, extracted intel, Proposal hydration). Without cascade, the UI shows raw sources without structure
- **At least 3-5 customers hydrated** in dev — currently have GR Little, Alliance, Armadillo. TD-5 expands; TD-3 doesn't formally depend on TD-5 but the UI is more meaningful with more customers
- **Existing chat-deepagents + voice-deepagents harnesses** — already deployed; refinements applied post-async-deepagents work
- **Existing OS auth** — JWT sessions, already operational
- **Existing OS WebSocket endpoint** — verify path/protocol during implementation; align with `realtime.md`

#### Out of scope for TD-3

- **Sales pipeline list view (Kyle's V0 ask)** — TD-7. The dashboard's pipeline widget is a preview; the full sales-pipeline-with-analysis surface lives in TD-7
- **Per-meeting artifact-quality view** (vision §2 thread A) — TD-7 enriches `/meetings/<id>` with stage-appropriate next-step suggestions + draft follow-up artifact
- **Flow diagram of actors + data flow** — TD-7
- **Push-to-talk for sales rep field updates beyond `log-touchpoint`** — TD-7 expands voice skills; TD-3 has the basic voice path
- **`/reviews` dedicated page** — deferred until reviewing volume warrants
- **Custom dashboard layouts per individual** (vs. per role) — defer until role defaults prove insufficient
- **External-customer multi-tenancy** — TD-11. UI is built for Indemn-the-company in `_platform` org

---

### TD-4 — Playbook stages defined from history

**Delivers:** Playbook records grounded in observed historical patterns across customers. **Count emergent from research, not pre-assumed** — could be 6 stages, could be more, could be sub-stages, could be Kyle's 12-with-archetypes framing. Each Playbook record defines `entry_signals`, `required_entities`, `expected_next_moves`, `artifact_intent`. Resolves the long-running open design questions through observation, not speculation.

#### Process (resolved)

Per Craig's direction, **TD-4 is fully conversational design via Claude Code**, not automation. Three phases:

**Phase 1 — Research session.** Large brainstorming + systematic review session. Read every hydrated Touchpoint across every customer. Identify patterns. **Determine what stages actually exist** — the current 6 (CONTACT/DISCOVERY/DEMO/PROPOSAL/NEGOTIATION/VERBAL/SIGNED) is a hypothesis to test against data. Output: refined understanding of the customer journey shape across all of Indemn's customer relationships.

**Phase 2 — Per-stage deep-dive.** One focused session per stage (or sub-stage, depending on what Phase 1 surfaces). Define `entry_signals`, `required_entities`, `expected_next_moves`, `artifact_intent` for that stage. Write Playbook records to dev OS.

**Phase 3 — Refinement.** Playbook records are **mostly static once defined**. Refined over time as we observe new patterns, but not auto-mined. No Playbook-Researcher associate. Refinement happens conversationally when team or Claude notices "this stage's Playbook doesn't match what's happening."

#### Open design questions fold into the research

The 5 open Qs (Opportunity vs Problem; Document-as-artifact for emails; 12 sub-stages with archetypes; origin/referrer tracking; Playbook hydration mechanism) are **resolved as they surface in the research**, not pre-resolved as separate work:

- **Opportunity vs Problem** — surfaces when the research observes unmapped pain in real conversations that doesn't fit Opportunity
- **Document-as-artifact for emails** — folded into TD-5 (resolved as Email entity with `status: drafting`)
- **12 sub-stages with archetypes** — Kyle's framing tested against research data; actual structure emerges
- **Origin/referrer tracking** — surfaces from observing how customers come in (Pat Klene → GR Little; Matan → David → Armadillo)
- **Playbook hydration mechanism** — resolved by "mostly static, conversational refinement"
- **Internal docs spanning multiple prospects** (Kyle's Apr 8 Warranty Prep covering Amynta + Fair + Armadillo) — surfaces during research; how they attach in the entity graph emerges

#### Done-test

All stages identified through research. Playbook records exist for each (count emergent). Each grounded in observed patterns from multiple customers. The 5 open design Qs resolved through the research. Artifact Generator (TD-5) can read these Playbook records and produce stage-appropriate artifacts.

#### Dependencies

- **TD-1 + TD-2 hydrated data** — hard dependency. Can't research without data.
- **TD-3 UI** — soft dependency. Helps team review Playbook drafts visually.
- **TD-5** — TD-4 outputs feed TD-5; TD-5 doesn't gate TD-4 research.

---

### TD-5 — Per-interaction artifact generation

**Delivers:** Every Touchpoint that completes processing produces a stage-appropriate draft artifact — follow-up email at DISCOVERY, recap at DEMO, objection response at NEGOTIATION, kickoff at SIGNED, etc. Drafts surface to the OS queue for human review with one-click send.

#### Architecture (resolved)

**One Artifact Generator associate, Playbook-driven behavior.** Per Craig's principle (one trigger → one associate), not multiple per-stage associates. Same trigger (`Touchpoint:processed`), same skill structure, reads `Playbook[Deal.stage].artifact_intent` to decide WHAT to produce per stage. Stage-specific behavior comes from Playbook records, not associate identity.

**Drafted-artifact storage = Email entity with `status: drafting`.** When Artifact Generator produces a follow-up email at DISCOVERY (or recap at DEMO, etc.), the draft lives as an Email entity with the new `drafting` state. Drafts queryable as Emails (consistent with the rest of the email lifecycle). PROPOSAL deck remains a Document (different mime_type, different entity). This resolves the "Document-as-artifact for emails" open Q from prior sessions.

**Both async + realtime deployments.** Per Craig's flexibility-of-deployment principle:
- **Async deployment** — auto-runs on `Touchpoint:processed` for autonomous draft production; surfaces to OS queue for review
- **Realtime chat deployment** — Cam invokes "let's draft v3 of Alliance proposal" via UI chat surface; conversational iteration with the associate
- **Realtime voice deployment** — push-to-talk: "Hey, let's talk through the Alliance proposal" → voice conversation
- Same skill, multiple Deployments. Standard OS pattern.

#### Sub-pieces

- Artifact Generator associate built (the role Claude played in GR Little + Alliance traces; one associate, Playbook-driven)
- Watches `Touchpoint:processed` → produces draft when fully extracted (async deployment)
- Reads `Playbook[Deal.stage].artifact_intent` for the spec
- Reads `(Deal + recent Touchpoints + extracted intelligence + Playbook + raw source content)` for materials
- Drafts surface to OS queue for human review
- Email state machine extended with `drafting` state for drafted-email storage
- One-click send via existing Email/Slack integrations (action lives in TD-3 Section 5; functionality in TD-5)
- Realtime chat + voice Deployments wired (alongside async) — same associate, multiple harness configs

#### Done-test

A new meeting happens → within minutes a draft artifact appears in the OS queue for the appropriate human → review and one-click send. Cam can also invoke realtime "draft v3 of Alliance" via UI chat for conversational iteration.

#### Dependencies

- **TD-4** — Playbook records define what to render per stage
- **TD-3** — UI surface for review (Section 5 of per-customer page; dashboard widgets)
- **TD-2** — cascade running so Touchpoints reach `processed` state autonomously

---

### TD-6 — Proposal deck generation autonomous

**Delivers:** Special case of TD-5 for PROPOSAL stage. The proposal deck renders automatically from the live entity graph — Operations, Opportunities, Phases, AssociateTypes, all pulled from the constellation. Cam reviews + sends with edits. Replaces Cam's manual proposal authoring.

#### Architecture (resolved)

**TD-6 is the PROPOSAL-stage instance of TD-5's Artifact Generator.** Same associate (Artifact Generator), same Playbook-driven behavior — when `Playbook[Deal.stage=PROPOSAL].artifact_intent` says "render styled PDF," the associate calls the existing `templates/proposal/` rendering pipeline (Handlebars + CSS + puppeteer-core, shipped Apr 27 Session 7) and uploads to Drive.

**Both deployment modes (async + realtime) apply here too.** Cam can:
- Wait for autonomous v3 to be drafted when Deal hits PROPOSAL stage (async)
- Invoke "let's draft v3 of Alliance" via UI chat for conversational iteration (realtime chat)
- Push-to-talk "talk through the Alliance proposal" (realtime voice)

Per the flexibility-of-deployment principle.

#### Sub-pieces

- Artifact Generator's Playbook-driven behavior handles PROPOSAL stage via the same mechanism as other stages
- Pulls from live entity graph (Operations, Opportunities, Phases, AssociateTypes, BusinessRelationship)
- Uses existing `templates/proposal/` pipeline (template.hbs + template.css + saas-agreement.partial.hbs + assets, all shipped)
- Renders to PDF via puppeteer-core against system Chrome
- Uploads to Cam's Drive folder (`1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`)
- Creates new Proposal entity in dev OS with `supersedes` link to prior version
- **Proposal state machine `superseded` transition** added (open from Sessions 6-9 — finally resolved here)
- Drive ingestion of historical proposals from Cam's portfolio (already in TD-1; provides context for the Artifact Generator's stylistic alignment)

#### Done-test

A Deal transitions to PROPOSAL stage → Artifact Generator produces a styled PDF rendered from the live entity graph → uploaded to Cam's Drive folder → Cam reviews and sends with edits, or pushes back with feedback that informs the next iteration. OR Cam invokes realtime "draft v3" via UI chat for iterative work.

#### Dependencies

- **TD-1** (Drive ingestion of Cam's portfolio for stylistic context)
- **TD-4** (PROPOSAL Playbook record defines what to render)
- **TD-5** (Artifact Generator associate built; both async + realtime deployments wired)
- **Proposal state machine `superseded` transition** — small kernel/entity-definition update needed alongside TD-6 work

---

### TD-7 — System visibility (sales pipeline + per-meeting enrichment + flow diagram)

**Delivers:** Team-facing analytical surfaces that build on TD-3's UI infrastructure. The pieces Kyle has been asking for since Apr 24, plus operational visibility into what the cascade is doing in real-time.

#### Architecture (resolved)

Most of TD-7 builds on TD-3's existing UI — adds pages/widgets/skills rather than new infrastructure. Five sub-pieces (A through E):

#### (A) Sales pipeline list view — `/pipeline` page

Per Kyle's V0 ask. Flat table of all customers/prospects:

- **Columns:** customer value, success path, days to next step, next step, owner, current stage, days-since-last-touch, # Touchpoints
- Sortable/filterable on any column
- Drills into per-customer constellation
- Real-time updates as Touchpoints arrive change last-touch dates / Deal stages
- The dashboard's per-role pipeline widget (TD-3) is a preview; this is the deeper analytical surface

#### (B) Per-meeting view enrichment — extends `/meetings/<id>` from TD-3

Per vision §2 thread A — "every meeting Indemn has gets entity trace + extracted intelligence + draft artifact, the way Kyle saw GR Little." TD-7 adds to TD-3's basic per-Meeting page:

- **Stage-appropriate next-step suggestions** (per `Playbook[Deal.stage].expected_next_moves`)
- **Draft follow-up artifact** rendered inline (produced by Artifact Generator from TD-5)
- **Comparative context** — what other meetings has the team had with this customer, with quick navigation between them

#### (C) Flow diagram — `/system` page

Real-time visualization of the running system:

- What associates are active/suspended/processing, on what entities, with what state
- Real-time cascade visualization — a new Email arrives → see EC pick it up → TS create Touchpoint → IE extract → Proposal-Hydrator update — visualized as messages flowing through the cascade
- Useful for ops + debugging + transparency to the team
- Built on a graph/tree library from Ganesh's stack (likely React Flow)
- Real-time via WebSocket on associate state + cascade messages

#### (D) Voice skills beyond `log-touchpoint` — accumulated incrementally on per-actor `default_assistant`

Initial set:
- `assign-company-to-document`
- `prep-for-meeting` (read recent activity, summarize what to know)
- `summarize-customer`
- `mark-decision` / `mark-commitment` / `mark-task` (log intelligence directly)
- `update-deal-stage` (when sales rep wants to advance a stage)
- `query-pipeline` ("what customers haven't been touched in two weeks?")

Each skill = markdown file + add to assistant's skills list. Incremental — additional skills get added as the team identifies needs.

#### (E) Drafts review surface — distributed across existing UI

Drafts surface in:
- TD-3's dashboard widgets (Cam's "drafts to review" widget, etc.)
- TD-3's Proposal-as-spine page section
- TD-7's per-meeting view enrichment (draft follow-up rendered on the meeting page)

No separate "drafts queue" page; drafts live where they're contextually relevant.

#### Done-test

- Cam opens dashboard daily — sees customers needing proposals, reviews drafts inline, sends with edits
- George prep is 5 minutes not 20
- Kyle sees the live state of every prospect via `/pipeline`, feels confident he can step away
- Ops can debug a stuck cascade via `/system`
- Team uses voice push-to-talk for routine updates without context-switching to the UI

#### Dependencies

- **TD-3** (UI infrastructure)
- **TD-4 + TD-5** (drafts exist to review)
- **TD-6** (Proposals to review)
- **TD-2** (cascade running so the system view shows live activity)

---

### TD-8 — Team adoption (daily mode of work)

**Delivers:** The team uses the OS as their daily mode. Behavior change is real but low-ceremony.

#### Architecture (resolved)

**Light onboarding docs + in-product UI hints + assistant-as-help.** Not a heavyweight training program. Per Craig's "low ceremony" framing.

#### (A) Per-role onboarding flows

Single sit-down session per person initially; team self-serves from there. Documents live in `projects/customer-system/onboarding/<role>.md`:

- **Cam** — proposal queue daily review, customer prep before calls, draft revision flow, generate Proposal v(n+1) command (async OR realtime chat for iterative work)
- **George** — pre-meeting prep flow (target 5 min not 20), customer state lookup, recent-activity summary
- **Ganesha** — customer-implementation status tracking, Phase progression review, technical Tasks management
- **Peter** — technical handoffs, customer-system data review, implementation Tasks, recent Slack threads in implementation channels
- **Kyle** — pipeline overview, prospect state at-a-glance, push-to-talk for quick field updates

#### (B) Operational learnings captured continuously

Per Kyle's Apr 24 ask. When team members hit friction, log it. Mechanism: a `team-learning` ReviewItem variant (or simple Slack channel) where the team drops "this was confusing" / "this would help" notes. Folded into TD-9 evaluations + skill iteration.

#### (C) Assistant-as-help

Just-in-time learning via the per-actor `default_assistant`. Team member asks the assistant "How do I assign a Document to a customer?" → assistant explains AND does it. The assistant is the running help layer — not a static doc.

#### Done-test

Each team member uses the OS daily as their primary mode of work. Cam reviews drafts daily. George preps in 5 min not 20. Kyle stops being the single point of failure for "what's the status with X?". A new team member can be onboarded in a single sit-down session.

#### Dependencies

- **TD-3 + TD-7** (UI is usable)
- **TD-5** (drafts surface for review)
- **TD-6** (proposals working)
- **TD-2** (cascade running so data is fresh)

---

### TD-9 — Evaluations + continuous improvement loop

**Delivers:** Every autonomous associate has rubric + test set. Quality measured continuously. Regressions caught automatically. The verification layer that makes autonomous work trustworthy.

#### Architecture (resolved)

**Three-source evaluation structure** — rubrics + test sets accumulate from three streams simultaneously:

- **(A) Build-time** — every new associate (MC, SC, Proposal-Hydrator, Company-Enricher in TD-2; Artifact Generator in TD-5) gets a rubric + test set when shipping
- **(B) Retroactive** — EC, TS, IE need rubrics + test sets too (currently rely on LangSmith trace inspection only). One-time work to backfill
- **(C) Failure-driven** — when an associate behaves wrong, the failure becomes a test case automatically (mining from LangSmith traces); ongoing flywheel

**Path 3 timing — LangSmith API directly for now; kernel-adapter integration deferred.**

Per Session 10's Path 3 decision: existing `evaluations` repo eventually becomes a kernel adapter (`system_type: evaluation`, provider: `langsmith` or `indemn-evals`). For TD-9, integrate **LangSmith API directly** (rubrics + test sets via LangSmith Python/curl client). Kernel-adapter integration happens later — possibly alongside TD-11 when the OS gets hardened for external customers.

**ReviewItem → training-data flywheel.** When a Reviewer corrects a ReviewItem (e.g., reassigns a Touchpoint to a different Deal), that correction:
- Becomes a test case for the originating associate (added to its test set automatically)
- Surfaces as a candidate for skill iteration (the pattern reviewers correct → eventually a rule or skill update)

This is the mechanism that makes "reviewing IS training data" real (per TD-2's ReviewItem pattern).

#### Sub-pieces

- LangSmith API integration for rubric/test-set authoring
- Per-associate rubrics for all 8 associates (EC, MC, SC, TS, IE, Proposal-Hydrator, Company-Enricher, Artifact Generator)
- Per-associate test sets (capturing real failure modes from LangSmith traces)
- Continuous evaluation runs — when an associate behaves wrong, run an eval on the segment to pinpoint why and refine
- Eval results visible in dashboard (TD-7 extension — possibly a `/system` page section)
- ReviewItem → test-case automation (Reviewer correction becomes a test case)
- Path 3 kernel-adapter integration deferred

#### Done-test

Every autonomous associate has a rubric + test set. Eval results visible in dashboard. Regressions caught automatically. ReviewItem corrections feed back as test cases. Combined with deep tracing (LangSmith already wired, Session 10), this is the verification layer that lets us trust autonomous work.

#### Dependencies

- **TD-2** — associates running so evals have something to evaluate
- **LangSmith already wired** (Session 10, commit `956d7d5`)
- **TD-7** — dashboard extension for surfacing eval results
- **Path 3 kernel-adapter integration** — deferred to TD-11 timeframe

---

### TD-10 — Persistent-AI loops (Commitment-tracking pattern)

**Delivers:** Commitments tracked end-to-end. The "Walker → Peter → Ganesha → Kyle" pattern Kyle described Apr 24. When a Commitment is created during a meeting/email/Slack interaction, the system watches it, notifies the assignee, tracks fulfillment, escalates up the chain when overdue.

#### Architecture (resolved)

**Commitment-Tracker associate, both event + schedule triggers.**

- **Event-based** — watches `Commitment:created` and `Commitment:transitioned` events. Fires immediate notification when a new Commitment is created ("Peter, you just committed in this meeting to send Walker the data this week"). Fires when Commitment status transitions ("fulfilled" / "overdue" / etc.)
- **Schedule-based (cron)** — runs every N hours, scans Commitments by due_date, fires escalation notifications for overdue items

Both triggers, same associate. Event for immediacy; schedule for sweeps.

**Notification channels: OS queue + Slack DM.**

- **OS queue** — primary; persistent; surfaces in dashboard (TD-3 widget); queryable
- **Slack DM** — high-immediacy; for time-sensitive notifications
- **Email** — out of scope (heavyweight for Commitment notifications; OS queue + Slack covers the use case)

**Escalation chain: Commitment-level field, defaults from Role.**

- `Commitment.assignee` (primary) — the human responsible
- `Commitment.escalation_chain` (ordered list) — fallback assignees if primary doesn't fulfill
- Defaults populated from the assignee's Role definition (Roles can have a default escalation chain), but override-able per-Commitment

Per Kyle's Walker → Peter → Ganesha → Kyle example: Walker's role's escalation chain is `[Peter, Ganesha, Kyle]`; when a Commitment defaulted to Walker is overdue, system notifies Peter; if still unresolved after another window, Ganesha; then Kyle.

#### Sub-pieces

- Commitment-Tracker associate built
- Watches on `Commitment:created` + `Commitment:transitioned` events
- `trigger_schedule` for periodic overdue sweeps
- Escalation chain field on Commitment + Role defaults
- Slack integration for DM notifications
- OS queue integration (Commitments surface in dashboard)
- UI surface — Commitments per customer (TD-3 constellation panel sub-section), per assignee (dashboard widget for "your Commitments"), overdue list view
- Fulfillment detection — when a subsequent Touchpoint references the Commitment as fulfilled (e.g., "Peter sent Walker the data on Thursday"), IE extracts that fact, Commitment-Tracker transitions Commitment to `fulfilled`

#### Done-test

A Commitment created during a meeting → flows through to assignee within minutes (Slack DM + OS queue). Tracked through fulfillment automatically. Overdue triggers escalation up the chain (Walker → Peter → Ganesha → Kyle pattern works end-to-end).

#### Dependencies

- **TD-2** — Commitments populated by IE
- **TD-3** — UI surface for Commitment review per-customer + dashboard widget
- **TD-5** — assistant can draft follow-up artifacts when Commitments come due
- **Slack integration** for DM notifications (Slack adapter from TD-1 + outbound DM capability)

---

### TD-11 — External-customer ready (Horizon 3)

**Delivers:** The OS is production-ready for external customers (non-Indemn). After Indemn-the-company is fully running on its own OS (TD-1 through TD-10), harden the platform for external onboarding. The white paper's Phase 6 → Phase 7 transition becomes operable.

#### Architecture (placeholder — detailed alignment deferred)

TD-11 is intentionally a **placeholder pointing at horizon work**. The customer-system project's roadmap doesn't carry the heavy OS-platform-readiness alignment work — that lives in **`../product-vision/`** (the OS-level project). When we approach TD-11, the alignment conversation moves to that project.

#### Pieces (high-level)

- **Kernel hardening** — production-grade error handling, rate limiting, observability. Most of this is OS-side, not customer-system-side.
- **Customer-onboarding playbook** — the 8-step domain modeling process from `indemn-os/docs/guides/domain-modeling.md` proven via real onboarding of a non-Indemn customer.
- **Second domain modelable in days** — either a fork attempt or planned next domain (delivery tracking, evaluations, conferences) coming online quickly. Validates that the OS is genuinely domain-agnostic.
- **Multi-tenancy edge cases resolved** — anything that surfaces with a non-Indemn org on the platform.
- **Compliance + audit trail surface** — changes collection + hash-chain verification surfaced in UI for auditability.
- **Path 3 evaluations as kernel adapter** (deferred from TD-9) — likely lands here as part of platform productization.

#### Done-test

A non-Indemn business modeled on the OS in <1 week. Customer-onboarding playbook is real and follows the 8-step process. Multi-tenancy holds. Path 3 kernel-adapter integration complete.

#### Dependencies

- **TD-1 through TD-10** — Indemn fully running on its own OS first
- **`../product-vision/`** — detailed alignment for TD-11 happens there, not here

---

## Continuous threads (run alongside every TD)

These are not deliverables — they run continuously across every TD.

### OS bug convergence (always-active)

**Operational discipline.** When customer-system work surfaces an OS-relevant finding, log it in `os-learnings.md`. If it blocks current TD work and is non-trivial, fork a parallel session to fix it. The customer-system development work doesn't block on bug fixes — they run in parallel.

- **Bug list lives in `os-learnings.md`** — ranked by impact (critical/blocking → high → medium → open design questions).
- **Top priorities at any time** — pulled from `os-learnings.md`'s "Critical / blocking the next phase" section. As of Session 12 close: most load-bearing work is done; remaining is mostly customer-system domain work + a handful of CLI papercuts.
- **Forking pattern** — when something blocks current TD work, fork to a separate git worktree, fix the OS-side bug in the OS repo, merge back. Coordinate with main session via shared context (`os-learnings.md` + `CURRENT.md`).
- **Fix-inline pattern** — when an OS fix is small and on the path of current work, do it inline. Don't fork unnecessarily.
- **Bugs are not pre-allocated to TDs** — they surface as we work; we fix them where they surface.

### OS-side milestones

As we build, the OS itself accumulates milestones beyond bug fixes. Track them so they don't drift.

- **Architecture docs reflect what we built** — `/Users/home/Repositories/indemn-os/docs/architecture/*.md` updated when patterns change.
- **Capability library expands** — each new kernel capability (entity-resolution, etc.) registered in `kernel/capability/` with docs.
- **Second domain modelable in days** — proven by either a fork attempt or a planned next domain (e.g., delivery tracking, evaluations) coming online quickly after customer-system is autonomous.
- **`product-vision/` project tracks design-level updates** to the OS (where OS design discussions land before becoming OS implementation work).

### Shared-context-update mechanism

**Critical operational discipline.** Multiple parallel sessions need shared context. Without a mechanism for this, the parallel work fragments and we lose the coherence the OS repo's documentation system gives us.

- **The mechanism today** — `CLAUDE.md` (always-loaded orientation), `INDEX.md` (append-only history), `vision.md` (slow-changing end-state), `roadmap.md` (living, where-we-are + path), `os-learnings.md` (running OS-finding register).
- **Per-session updates** — every session that completes work updates `roadmap.md` "Where we are now" + appends to `INDEX.md` Decisions/Open Questions/Artifacts. Every session that surfaces an OS-relevant finding appends to `os-learnings.md`. Per the discipline in `CLAUDE.md`.
- **Per-fork updates** — when a fork fixes a bug, the bug row in `os-learnings.md` is updated to fixed; the OS architecture doc (if affected) is updated; CLAUDE.md "Where we are now" reflects state.
- **Open question** — does this mechanism scale to N parallel sessions? Probably not as-is. Refinement is its own work item that surfaces during Phase B as parallel sessions multiply. May need: a session-state tracker (already exists at `systems/session-manager/`); a more structured handoff protocol; agent-based reconciliation. This is a meta-thread that runs throughout.

---

## Out of scope (for this roadmap)

This roadmap covers everything Indemn-the-company will run on the OS, plus the readiness for external customers (TD-11 / Horizon 3). What's explicitly NOT in this roadmap:

- **External-customer-specific domain modeling** — once TD-11 lands, modeling a non-Indemn business on the OS is a new project. Each external customer is its own domain configuration.
- **Voice agent products** for external customers (EventGuard-style autonomous voice flows) — different product, different system, not customer-system scope.
- **Mobile UI** — not in TD-3 scope. Web-first; mobile is a future consideration after team adoption (TD-8) proves the desktop experience works.
- **Inbound webhook from external customers' systems** — not in scope until TD-11.

Note: Persistent-AI loops (Walker → Peter → Ganesha → Kyle pattern, Kyle's Apr 24 ask) are now TD-10 — folded back in. They were previously deferred but the Commitment-tracking work belongs in this roadmap because the Commitment + Task + assignee-notification mechanism is part of the customer system's foundation.

---

## References

| File | What's in it |
|---|---|
| `vision.md` | What we're building, why, the breakthrough as the lens. |
| `os-learnings.md` | Running register of OS bugs, capability gaps, design questions. |
| `INDEX.md` | Append-only project history. Status, Decisions, Open Questions, full Artifacts table. |
| `CLAUDE.md` | Cumulative thinking, journey, principles, start-of-session protocol. **Always read first.** |
| `CURRENT.md` | Fast-changing state (parallel sessions, blockers, in-flight). Read after CLAUDE.md every session. |
| `SESSIONS.md` | Append-only per-session log of objectives + outcomes. |
| `PROMPT.md` | The session-start prompt template — pasteable into N parallel + N sequential sessions. |
| `artifacts/2026-04-22-entity-model-brainstorm.md` | Entity field-level specs. |
| `artifacts/2026-04-22-entity-model-design-rationale.md` | Why the entity model is shaped this way. The Alliance test. |
| `artifacts/2026-04-23-playbook-as-entity-model.md` | The breakthrough articulated. |
| `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` | Latest design refinements (Apr 24). |
| `artifacts/2026-04-24-extractor-pipeline-gap.md` | Why the Extractor failed Apr 24; Option B is the chosen fix. |
| `artifacts/2026-04-24-extractor-procedure-and-requirements.md` | Procedure for autonomous Extractor + 9 OS capability gaps. |
| `artifacts/2026-04-24-information-flow-v2.html` | The GR Little visual demo (open in browser). |
| `artifacts/2026-04-27-alliance-trace-showcase.html` | The Alliance trace-showcase visual (the language for TD-3 UI). |
| `artifacts/2026-04-24-grlittle-followup-email-draft.md` | The GR Little artifact + entity-to-line mapping. |
| `artifacts/2026-04-24-os-bugs-and-shakeout.md` | Bug-level deep detail. |
| `/Users/home/Repositories/indemn-os/docs/white-paper.md` | The OS canonical vision. |
| `/Users/home/Repositories/indemn-os/CLAUDE.md` | The OS builder's manual. |

---

*This document is updated every session that moves the work forward. When state changes, update "Where we are now"; when a phase completes, mark it done; when scope shifts, append a Decision in `INDEX.md` first, then revise here.*
