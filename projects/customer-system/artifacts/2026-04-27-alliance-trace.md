---
ask: "Trace Alliance Insurance end-to-end through the OS to produce a v2 Proposal artifact for Cam, walking the actual lifecycle as if the OS were running per the vision (each associate playing its role, each watch firing, each entity being created at the right step). Document every step including gaps where the autonomous capability doesn't yet exist."
created: 2026-04-27
workstream: customer-system
session: 2026-04-27-alliance-trace
sources:
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-27-alliance-trace-plan.md"
    description: "The plan written before executing — what we expect to write to the OS, gaps we expect to surface, sequence"
  - type: local
    ref: "projects/customer-system/vision.md"
    description: "The vision this trace exercises"
  - type: local
    ref: "projects/customer-system/roadmap.md"
    description: "Phase A2 — Alliance proposal trace"
  - type: drive
    ref: "1KDeMtV3f1wbexq0KkZNZp7AGZCjYS7t0awz3CPCUj9I"
    name: "Alliance Insurance Services Proposal 2-11-26"
  - type: slack
    ref: "F0AGS9LL064 (file in #customer-implementation, ts 1771509641.962729)"
    name: "2026-02-18-capability-document.md"
  - type: slack
    ref: "thread #customer-implementation parent ts 1775611051.296399"
    description: "Apr 7-8 Retention Associate / compound outcome thread"
  - type: slack
    ref: "#customer-success-working ts 1770090453.076719"
    description: "Feb 1 Alliance & Indemn Solution Scoping call summary (kyle intelligence bot)"
  - type: os
    ref: "Alliance Company 69e41a82b5699e1b9d7e98eb, Deal ALLIANCE-2026 69e79a31f0d2c6b73f885a32"
    description: "Existing OS state in dev OS, _platform org"
---

# Alliance Trace — As If Running Per The Vision

This document walks Alliance Insurance through the OS step by step **as if the system were running according to the vision**. Each event — email arrival, meeting, Slack thread, document created — triggers the appropriate associate, whose work is documented and whose outputs are written to the OS via the `indemn` CLI.

**Claude-in-this-conversation plays each associate's role.** Where an autonomous capability is missing (Slack ingestion, Option B source pointers, the Apr 8 meeting transcript not in the OS), the gap is documented and the manual work proceeds.

The trace produces:
1. A real entity graph in the OS (`_platform` org)
2. This document (the trace narrative + step-by-step audit)
3. A v2 Alliance proposal artifact (the deliverable for Cam)
4. Updates to `os-learnings.md` (gaps surfaced)
5. Refinements to `roadmap.md` (e.g., Slack ingestion priority)

Read this with `2026-04-27-alliance-trace-plan.md` (the pre-execution plan).

---

## Pre-state — what's in the OS for Alliance before this trace begins

Verified via direct mongodb query 2026-04-27 (see `2026-04-27-alliance-trace-plan.md` for queries):

- **Company `69e41a82b5699e1b9d7e98eb`** — "Alliance Insurance", type=Broker, cohort=Prospect, source="Existing", source_detail="IIANC cohort", owner+engineering_lead=`69e4066ad260a73f432839b8`. Created 2026-04-18 (post-hoc, by Craig presumably). Most fields null (website, domain, location, etc.).
- **Deal `69e79a31f0d2c6b73f885a32`** — `ALLIANCE-2026`, company=Alliance, stage=`proposal`, warmth=Warm, source=Referral, name="Alliance Renewal Associate", next_step="Update proposal based on Apr 8 call (renewals wedge); ship to Christopher by Apr 26 (back from ISU Apr 25)". Created 2026-04-21.
- **2 emails** about "Re: Indemn/Alliance - Exciting project with BT Core data" (Apr 21) — **misclassified to wrong Companies** (Bug #16 manifestation). `69ea550d0a2b41b769607126` (status=processed, company=`69ea8467ff375a32fa259cd9`) and `69ea5844a25d34b927d7405f` (status=classified, company=`69ea9eb7ff375a32fa25a3a4`).
- **Zero** Contacts, Meetings, Documents, Touchpoints, Operations, Opportunities, Proposals, Phases, CustomerSystem, BusinessRelationship, Tasks, Decisions, Commitments, Signals linked to Alliance.

The Company + Deal exist as bootstrap; the rest is missing — exactly the "near-clean slate" the trace must hydrate as if associates had been running.

**Trace gap #1:** the Company itself was manually created (Apr 18) by Craig, not by an Email Classifier on first contact. In the as-designed flow, the Company would be auto-created (cautiously, with the entity-resolution capability) by the Email Classifier on the first inbound email. We use the existing Company as canonical; in a future Alliance-style customer (e.g., a brand-new prospect), the Company creation would itself be an associate's work.

---

## Trace timeline

The narrative walks the actual events in order. Each step has:
- **Trigger** — what entity changed / what raw data arrived
- **Watch** — which Role's watch matched
- **Associate** — the AI actor that runs (played by Claude-in-this-conversation)
- **Inputs** — entities + raw content the associate has access to
- **Outputs** — entities created/updated, with their OS IDs
- **Gaps** — capabilities or data missing in the autonomous flow

---

*Trace begins below — entries appended as each step is executed.*

---

## Step 1 — Feb 1, 2026: Alliance & Indemn Solution Scoping (discovery call)

**Real-life trigger.** Christopher Cook + Brian Leftwich (Alliance) have a 1:02 PM ET Google Meet with Kyle (Indemn) — a solution scoping call that follows from a Pat Klene / 101 Weston Labs introduction. Granola records the call and produces an auto-summary; that summary is later posted to Slack `#customer-success-working` by the kyle intelligence bot (ts `1770090453.076719`).

In the as-designed flow, this single real-world event triggers a cascade of associate work:

### 1a — Google Workspace adapter discovers the Meet conference

**Trigger.** `Meeting.fetch_new` capability runs on a schedule (or on Meet API webhook). The adapter pulls the conference record + transcript + smart notes + recording from Apollo/Granola + Calendar attendees.

**Associate.** Google Workspace adapter (deterministic — no skill needed; runs the integration's `fetch()` method).

**Inputs.** Meet API conference record for 2026-02-01 18:02 UTC. Calendar attendees list.

**Outputs.** New Meeting entity at stage `recorded`, populated with title, date, source, summary, participants, recording_ref, transcript_ref. Initially `company: null` and `touchpoint: null` — those come from later associates.

**Done by.** Played here as Claude reconstructing the Meeting from the Slack auto-summary, since the actual Meet conference record is past the 30-day Apollo/Granola retention window. **Meeting ID `69efb8c150cea0a476d6fa66`** created with `source: "granola"`, `stage: "recorded"`, full summary in the summary field. `transcript: null` because the actual transcript is not retained.

**Gaps surfaced.**
- **Gap A1.1 — 30-day retention.** Apollo/Granola retain conference records for 30 days. Anything older requires manual reconstruction from auto-summary or other downstream artifacts. The OS doesn't currently re-fetch or persist the transcript itself; we lose ground-truth content after 30 days. *Implication for the vision: long-term, we need to copy transcripts into the OS at ingestion time so they survive the retention window.* Worth logging as a finding.
- **Gap A1.2 — Backfill is manual.** Bug #10 (no backfill mechanism) means historical meetings can't be reprocessed by associates that came online later. The Feb 1 meeting was captured at the time but never flowed through any associate (associates didn't exist Feb 1). Today there's no `indemn meeting reprocess <id>` to send historical Meetings through the post-Apr 24 pipeline.

---

### 1b — Email Classifier (or "Meeting Classifier") fires

**Trigger.** Watch fires on `Meeting.created`. The associate's job: determine which Company this meeting relates to and create Contacts for new external participants.

**Associate.** Email Classifier (the same associate handles both — its skill says `Email Classifier classifies emails AND meetings to a Company`. In practice today, Bug #17 says no Meeting Classifier exists in the pipeline at all — `fetch_new` leaves `meeting.company: null` and the Touchpoint Synthesizer assumes it's set. The two should be unified or the gap closed.)

**Inputs.**
- The Meeting entity (with title + summary + participant list)
- Existing Company list (queried via `indemn company list --search "Alliance"` — would return the canonical Alliance Company `69e41a82b5699e1b9d7e98eb` if entity-resolution capability existed; today returns multiple Alliance entries that need disambiguation)
- Existing Contact list (queried per-participant)

**Outputs.** Meeting.company set; Contacts created for new external participants.

**Done by.** Played here as Claude:
- Resolved Meeting.company → `69e41a82b5699e1b9d7e98eb` (canonical Alliance Insurance) via direct mongo lookup (since entity-resolution capability isn't built yet). `indemn meeting update 69efb8c150cea0a476d6fa66 --data '{"company":"...","contacts":[...]}'` applied.
- Created **Christopher Cook** Contact `69efb8f350cea0a476d6fa69` (CEO, role=Decision_Maker, is_primary=true, how_met=Referral, linked to Alliance).
- Created **Brian Leftwich** Contact `69efb8f450cea0a476d6fa6b` (Operating Lead, role=Day_to_Day, how_met=Discovery_Call, linked to Alliance).
- Set Meeting.contacts = [Christopher, Brian] and Meeting.team_members = ["Kyle"].

**Gaps surfaced.**
- **Gap A1.3 — No Meeting Classifier.** Bug #17. `fetch_new` leaves `meeting.company: null`; Touchpoint Synthesizer assumes it's set. Either (a) extend the Email Classifier's skill to also handle Meeting created events, or (b) build a dedicated Meeting Classifier associate. The skill content is the same — match participants/title/content to a Company; create Contacts on first encounter — but the trigger wiring is missing.
- **Gap A1.4 — No entity-resolution capability.** Already in os-learnings.md (critical). The Meeting Classifier needs `indemn entity resolve --type Company --domain X --name Y --participants ...` to safely match. Without it, the associate either auto-creates duplicates (Bug #16) or punts to a `needs_review` queue.
- **Gap A1.5 — Contact email population.** Christopher and Brian's email addresses aren't surfaced in the Slack auto-summary. The Meet API would have them in the participant list (their actual Google accounts), but post-30-day retention we don't have access. Created Contacts without emails; would need to be enriched later (e.g., from Apollo enrichment, or from the next email exchange that has them as recipients).

---

### 1c — Touchpoint Synthesizer fires

**Trigger.** Watch fires on `Meeting.transitioned` (recorded → transcribed) or directly on `Meeting.created` once it's classified to a Company. The Synthesizer creates a Touchpoint entity that represents this customer interaction in the unified timeline.

**Associate.** Touchpoint Synthesizer.

**Inputs.**
- The Meeting entity (with transcript + summary + participants_contacts + team_members)
- The Deal for this Company at this date (queried — `Deal ALLIANCE-2026 69e79a31f0d2c6b73f885a32` exists)
- The Contact records for participants (resolved by 1b)
- The Employee records for team members (Kyle's Employee `69e7c8b1bca4880e93ad5570`)

**Outputs.** Touchpoint entity with Option B source pointers populated (`source_entity_type: "Meeting"`, `source_entity_id: <meeting_id>`).

**Done by.** Played here as Claude. Created **Touchpoint `69efb91d50cea0a476d6fa6d`**:
- type=meeting, scope=external (since Christopher + Brian are Contacts, not Employees)
- date=2026-02-01T18:02:00Z, deal=ALLIANCE-2026
- participants_contacts=[Christopher, Brian], participants_employees=[Kyle]
- summary: synthesis of the Slack auto-summary distilled to the touchpoint level (the relationship establishment + the candidate solution surface + the 5 Indemn commitments + 1+1 customer commitments)
- **source_entity_type="Meeting", source_entity_id=69efb8c150cea0a476d6fa66** (Option B, just-deployed)

Also set Meeting.touchpoint = `69efb91d50cea0a476d6fa6d` to close the Bug #18 back-reference gap (explicit Synth update).

**Gaps surfaced.**
- **Gap A1.6 — Synth must consult the Deal.** The Touchpoint links to a Deal — at this point the Synth needs to look up "is there a Deal open for this Company at this date? what's its stage?" The current Synth skill doesn't explicitly call this out. With multiple Deals per Company over time, the Synth needs deterministic Deal-resolution logic.
- **Gap A1.7 — Synth must explicitly back-reference Meeting.touchpoint.** Bug #18. The Synth currently only updates 5 of 67 historical meetings with the back-pointer. Either the skill needs to enforce the post-create Meeting update, OR the relationship needs to flip direction (Meeting reads its Touchpoint from Touchpoint.source_entity_id with a reverse-lookup capability — which the kernel doesn't yet support, see the "--include-related doesn't follow reverse refs" finding).

---

### 1d — Intelligence Extractor fires

**Trigger.** Watch fires on `Touchpoint.created`. The Extractor reads the Touchpoint summary + navigates to the source content (via the Option B pointers) + extracts intelligence entities.

**Associate.** Intelligence Extractor.

**Inputs.**
- The Touchpoint entity
- The source Meeting (via `source_entity_type` + `source_entity_id` — Option B)
- Meeting.transcript (would normally be the primary source; null in our case because retention is past) → falls back to Meeting.summary
- The current Playbook record for `Deal.stage = proposal` — though for this Touchpoint at Feb 1, the Deal didn't exist yet at the time, so the relevant Playbook would be `discovery` or `contact`. (At time of historical synthesis today, the Deal.stage is `proposal`, but for an as-designed extraction we'd reach for the Playbook contemporaneous with the touchpoint date.)
- The Capability Document (would help inform Operations / Opportunities — but that document is dated Feb 18, post-this-touchpoint, so the Extractor wouldn't have it at Feb 1 and shouldn't synthesize from it.)

**Outputs.** Tasks, Decisions, Commitments, Signals, Operations, Opportunities — whichever the extracted content supports.

**Done by.** Played here as Claude. From the Slack auto-summary content (limited compared to a full transcript) the Extractor can pull:
- **7 Commitments** — 5 indemn-side from Kyle + 1 customer-side from Brian + 1 customer-side from Christopher. Each has `made_by`, `made_by_side`, `made_to`, `description`, links to source_meeting + touchpoint + company. Created (IDs: `69efb96350cea0a476d6fa72`, `...74`, `...76`, `...78`, `...7a`, `...7c`, `...7e`).
- **4 Signals** — 1 blocker (~100 missed calls/week), 1 champion (Christopher proactive CEO), 1 expansion (multi-line interest surfaced), 1 insight (Pat Klene / 101 Weston referral channel). Created (IDs: `69efb96750cea0a476d6fa80`, `...82`, `...84`, `...86`).
- **0 Decisions** — the call surfaced commitments but no specific directional decisions (those came later: v1 proposal Feb 11 was a Decision; renewal-wedge pivot Apr 8 was a Decision).
- **0 standalone Tasks** — the Commitments above cover the work; standalone implementation Tasks (e.g., "build prototype") aren't surfaced explicitly in the summary.
- **0 Operations / Opportunities** — these emerge from analysis (Capability Document Feb 18), not from a single discovery call summary.

**Gaps surfaced.**
- **Gap A1.8 — Auto-summary is thin source.** Extracting from a 200-word auto-summary captures less than extracting from a full transcript. The extracted entities are accurate but coarse (e.g., we know about "100 missed calls/week" but not the actual sub-flows that drive it; that came in the Capability Document weeks later). *Implication: the OS should preserve/ingest the full transcript when available, and the Extractor should always prefer transcript over summary.*
- **Gap A1.9 — Stage-contemporaneous Playbook lookup.** The Extractor needs the Playbook record for `Deal.stage AT TIME OF TOUCHPOINT`, not the current Deal.stage. For historical traces this matters; for live ingestion it's the same. The OS doesn't currently version/snapshot Playbooks per touchpoint date. *Question: do we treat Playbook as immutable per record (version=N), or do we keep historical snapshots? Lean: Playbook records should version like everything else.*

---

### 1f — Touchpoint Synthesizer transitions Touchpoint to processed

After Extractor completes, the Touchpoint is marked `processed`.

**Done.** `indemn touchpoint transition 69efb91d50cea0a476d6fa6d --to processed --reason "Intelligence extracted from Feb 1 discovery call: 7 commitments + 4 signals + 0 decisions + 0 standalone tasks"`. Status confirmed.

---

### Step 1 — entity inventory (created in this step)

| Entity | ID | Notes |
|---|---|---|
| Meeting | `69efb8c150cea0a476d6fa66` | stage=recorded, source=granola; company + contacts + team_members + touchpoint back-pointer set in 1b/1c |
| Contact (Christopher Cook) | `69efb8f350cea0a476d6fa69` | CEO, Decision_Maker, is_primary, how_met=Referral |
| Contact (Brian Leftwich) | `69efb8f450cea0a476d6fa6b` | Operating Lead, Day_to_Day, how_met=Discovery_Call |
| Touchpoint | `69efb91d50cea0a476d6fa6d` | type=meeting, scope=external, status=processed, **Option B pointers set** |
| Commitment × 7 | `69efb96350cea0a476d6fa72`–`...7e` | 5 indemn-side, 2 customer-side; all linked to source_meeting + touchpoint + company |
| Signal × 4 | `69efb96750cea0a476d6fa80`–`...86` | 1 blocker, 1 champion, 1 expansion, 1 insight |

### Step 1 — gaps logged

The gaps surfaced above (A1.1 through A1.9) are aggregated to `os-learnings.md` at the end of the trace, not inline (to avoid re-rebooting other sessions on each find).

---

## Step 2 — Feb 11, 2026: Kyle ships v1 proposal to Christopher

**Real-life trigger.** Kyle drafts the Crawl-Walk-Run v1 proposal in Google Docs (Drive `1KDeMtV3...`), reviews internally, sends it to Christopher via email on Feb 11 22:00 UTC with the Doc attached or shared. Christopher's team starts reviewing it, then goes silent for ~7 weeks until the Apr 8 reconnect.

### 2a — Gmail integration ingests the outbound Email

**Trigger.** Gmail adapter `fetch_new` capability (or push notification webhook) discovers Kyle's sent email.

**Associate.** Gmail adapter (deterministic).

**Outputs.** Email entity created with from/to/subject/body/has_attachments. **Email `69efba5e50cea0a476d6fa8b`** created with `status: processed`, `has_attachments: true`, `external_ref: synthetic:alliance-v1-2026-02-11` (had to set explicitly because Bug #30's sparse-on-nullable-unique fix wasn't propagated to Email — see new finding logged in os-learnings.md).

**Gaps.** **Gap A2.1** — Bug #30's fix only landed for `Meeting.external_ref`. Same pattern in `Email.external_ref` collides on `org_id_1_external_ref_1` unique index when two emails are created without external_ref. Logged to os-learnings.md as a new High-priority finding.

### 2b — Touchpoint Synthesizer creates Document from email attachment

**Trigger.** Watch fires on `Email.transitioned` (received → classified). Synth sees `has_attachments: true`, fetches the attachment metadata, creates a Document.

**Outputs.** **Document `69efba5f50cea0a476d6fa8e`** — name "Alliance Insurance Services Proposal 2-11-26 (v1)", source=google_drive, drive_file_id=`1KDeMtV3f1wbexq0KkZNZp7AGZCjYS7t0awz3CPCUj9I`, drive_url set, source_email back-pointer to the Email.

### 2c — Touchpoint Synthesizer creates Touchpoint

**Trigger.** Same Email transition. Synth groups emails by thread_id; first email in this thread → new Touchpoint.

**Outputs.** **Touchpoint `69efba8350cea0a476d6fa90`** — type=email, scope=external, deal=ALLIANCE-2026, participants_contacts=[Christopher], participants_employees=[Kyle], **source_entity_type=Email, source_entity_id=`69efba5e...8b`** (Option B). Summary captures the v1 proposal-send substance + the Crawl-Walk-Run framework as represented in the proposal.

**Gap A2.2** — Email entity definition still has `interaction` as the field name (pre-Apr 23 rename), pointing to → Interaction (deprecated; the `interactions` collection still exists in MongoDB alongside `touchpoints`). Skipped setting `Email.interaction` because it would point at the wrong collection. Logged.

### 2d — Intelligence Extractor fires

**Outputs.**
- **Decision `69efba8450cea0a476d6fa93`** — "Indemn ships v1 proposal to Alliance — three-phase Crawl-Walk-Run anchored on Revenue Capacity / Efficiency / Strategic Control" (decided_by Kyle).
- **Commitment `69efba8450cea0a476d6fa95`** — Kyle/Indemn to provide Phase 1 at waived investment.
- **Signal `69efba8550cea0a476d6fa97`** — insight: v1 proposal anchors on outcome categories matching the Indemn standard portfolio pattern (Branch, Johnson, GIC, Charley, Physicians Mutual). Generalizable template.

Touchpoint transitioned to processed.

### 2e — Proposal v1 entity created + walked through lifecycle

The Artifact Generator role doesn't exist yet today, but for trace fidelity we create the Proposal entity that v1 corresponds to. **Proposal v1 `69efba9650cea0a476d6fa9a`** created with version=1, source_document=Document, prepared_for=Christopher, prepared_by=Kyle, date_prepared=date_sent=2026-02-11. Walked through lifecycle: drafting → internal_review → sent → under_review (which is where it remained through the silence period until Apr 8).

### Step 2 — entity inventory

| Entity | ID | Notes |
|---|---|---|
| Email (v1 send) | `69efba5e50cea0a476d6fa8b` | external_ref set manually to bypass Bug #30-pattern issue on Email |
| Document (v1 proposal) | `69efba5f50cea0a476d6fa8e` | google_drive, source_email back-pointer |
| Touchpoint | `69efba8350cea0a476d6fa90` | type=email, status=processed, Option B pointers |
| Decision | `69efba8450cea0a476d6fa93` | "Indemn ships v1 proposal" |
| Commitment | `69efba8450cea0a476d6fa95` | Phase 1 waived investment |
| Signal | `69efba8550cea0a476d6fa97` | insight (proposal pattern) |
| Proposal v1 | `69efba9650cea0a476d6fa9a` | status=under_review |

---

## Step 3 — Feb 18-19, 2026: Capability Document analysis (the 30-page analysis Christopher referenced)

**Real-life trigger.** Craig spends Feb 18-19 analyzing 2,156 of Alliance's phone call recordings locally on Apple Silicon (Qwen3-ASR transcription + Qwen3-14B extraction + parallel Claude subagents for clustering + per-type synthesis). Output: the Capability Document (683 lines / 42KB markdown). On Feb 19, Craig posts to Slack `#customer-implementation` with the file attached + intro message tagging Kyle and Jonathan.

### 3a — Slack ingestion creates the Touchpoint + Document

In the as-designed flow, Slack ingestion (Phase F per old roadmap, but **the Alliance trace proves this is foundational, not deferrable**) would:
- Watch the customer-implementation channel
- See the message + attached file
- Create a Touchpoint (type=slack, scope=internal — Craig + Kyle + Jonathan all Indemn employees)
- Create a Document for the file attachment (source=slack_file_attachment — but the Document.source enum doesn't include 'slack' today, only google_drive / email_attachment / manual_upload)
- Classify to Alliance (the post mentions Alliance multiple times)

**Done by.** Played as Claude with manual creates (Slack adapter doesn't exist):
- Document **`69efbb1150cea0a476d6fa9f`** — 30K of the 42K markdown content embedded; references the Slack file F0AGS9LL064; source=manual_upload as workaround.
- Touchpoint **`69efbb2950cea0a476d6faa1`** — type=slack, scope=internal, source_entity_type=Document, source_entity_id=Document, summary captures the analytical substance (20 engagement types, 77% callback rate, Phase 1 tier, etc.).

### 3b — Intelligence Extractor reads the Document content + extracts a LOT

This is where the rich entity creation happens. The Capability Document contains structured per-engagement-type data; the Extractor produces:

**Operations (6):** Renewal outreach + rate review (`69efbb414d65e2ca69b0dd08`); Inbound call handling (`69efbb414d65e2ca69b0dd0a`); Quote generation (`69efbb424d65e2ca69b0dd0c`); Billing question handling (`69efbb424d65e2ca69b0dd0e`); Payment processing (`69efbb434d65e2ca69b0dd10`); Stewardship/renewal-prep for Producers (`69efbb434d65e2ca69b0dd12`).

**CustomerSystem (7):** Alliance internal CRM/notes (`69efbb5e4d65e2ca69b0dd14`); Conga Sign (`69efbb5f4d65e2ca69b0dd16`); Salesforce (`69efbb5f4d65e2ca69b0dd18`); Ascend (`69efbb604d65e2ca69b0dd1a`); Carrier portal cluster (`69efbb604d65e2ca69b0dd1c`); RCE (`69efbb614d65e2ca69b0dd1e`); Canopy Connect (`69efbb614d65e2ca69b0dd20`). *BT Core comes later in Step 5; not surfaced in the Capability Document itself.*

**Opportunities (7):** Each mapped to an AssociateType + linked back to source_touchpoint + source_document. Stewardship/Renewal-prep → Renewal Associate; Outbound renewal calls → Outbound Associate; Missed-call capture → Front Desk Associate; Billing questions → Service Associate; Payment processing → Service Associate; Internal knowledge → Knowledge Associate; Document Requests → Inbox Associate.

**Signals (6):** insight (77% callback_needed); insight (Phase-1 high-automation tier 24%); blocker (Spanish-language demand vs only 1 bilingual agent); insight (20+ carriers each with own playbook); insight (Renewal/Rate Review = 8.5% but the wedge); churn_risk (NC carrier exits Main Street America, NGM).

Touchpoint transitioned to processed.

### Step 3 — gaps surfaced

- **Gap A3.1 — Slack ingestion absent.** The single biggest "next-roadmap-priority" surfaced by this trace. Slack threads carry foundational analytical artifacts (the Capability Document is one example; Apr 7-8 prep thread is another; Apr 21 mpdm packaging is another). Without Slack ingestion, customer-system loses the internal-thinking layer of the Touchpoint timeline. *Reflects in roadmap.md update — Slack moves from Phase F to early-Phase-B.*
- **Gap A3.2 — Document.source enum missing 'slack'.** Used 'manual_upload' as workaround. Should add 'slack_file_attachment'.
- **Gap A3.3 — Backfill mechanism for historical Slack posts.** Same as Bug #10 but for Slack threads — once Slack adapter exists, would need to backfill historical Alliance content.

---

## Step 4 — Feb 26, 2026: Capability doc PDF DM to Ryan

**Real-life trigger.** Craig DMs the PDF version of the Capability Document to Ryan (Slack DM ts 1772811412.076349) — internal stewardship of the analytical artifact.

**Done.** Touchpoint **`69efbc6a4d65e2ca69b0dd46`** — slack/internal, source_entity points back at the existing Capability Document. No new entities; reference touchpoint that establishes Ryan as a stakeholder. Transitioned to processed.

---

## Step 5 — Apr 7-8, 2026: Pre-meeting prep thread (the Retention Associate / compound outcome design)

**Real-life trigger.** Christopher sent Kyle a stewardship-prep ask on Apr 7. Kyle posts in the `mpdm-ryan-kyle-peter-ian-craig` channel preparing for the Apr 8 2:30pm ET meeting with Christopher. Multi-team brainstorm produces the Retention Associate concept + compound-outcome packaging + BT Core integration approach + real Alliance numbers from Peter's data validation.

### 5a — Slack ingestion creates the Touchpoint

**Outputs (played by Claude):**
- New CustomerSystem **`69efbc6b4d65e2ca69b0dd4a`** — BT Core (Salesforce-based). First mention of BT Core in the timeline; the Apr 7-8 thread is where its centrality emerges.
- Touchpoint **`69efbc6c4d65e2ca69b0dd4c`** — slack/internal, participants Kyle + Craig + Jonathan + Dhruv + Peter + Cam.

### 5b — Intelligence Extractor

- **Decisions (3):** "Frame Christopher ask as Retention Associate compound" (Kyle, `69efbc6c4d65e2ca69b0dd4f`); "Adopt compound outcome packaging" (Cam, `69efbc6d4d65e2ca69b0dd51`); "Use Salesforce Connected App + OAuth for BT Core" (Dhruv, `69efbc6d4d65e2ca69b0dd53`).
- **Signals (3):** champion (Christopher proactive re-engagement, `69efbc6e4d65e2ca69b0dd55`); insight (Peter's real numbers — 9,516 accounts / 16,744 policies / 3,946 in next 90 days, `69efbc6e4d65e2ca69b0dd57`); blocker (BT Core integration gate, `69efbc6f4d65e2ca69b0dd59`).

Transitioned to processed.

### Step 5 — gaps

- Apr 7-8 thread is a 6-person internal Slack — would need Slack adapter handling MPDMs (multi-party DM channels) the same as regular channels.
- The "real numbers" Signal is critical for v2 (replaces the v1 "~4,000 customers" with the actual 9,516 accounts / 16,744 policies). This is a great example of how Touchpoint extraction directly informs proposal-generation accuracy.

---

## Step 6 — Apr 8/9, 2026: Actual meeting with Christopher (the renewal-wedge pivot)

**Real-life trigger.** Christopher + Kyle + Cam meet 2:30pm ET. The bandwidth conversation. Christopher likes the Retention Associate framing. Kyle commits to ship v2 by Apr 26.

### 6a — Meeting NOT in OS

**Gap A6.1 — The meeting itself isn't in the OS** (no Apollo/Granola capture in our hands; possibly retained on Apollo but past 30-day window now). For trace fidelity, we still create the Touchpoint with the content reconstructed from: the pre-thread (Step 5), the Deal next_step ("Update proposal based on Apr 8 call (renewals wedge); ship to Christopher by Apr 26"), the design rationale Alliance Test, and the Apr 25 handoff.

### 6b — Touchpoint reconstructed

**Outputs.**
- Touchpoint **`69efbc914d65e2ca69b0dd5c`** — meeting/external, participants Kyle + Cam + Christopher. Summary documents the bandwidth-driven pivot from Crawl-Walk-Run to renewal-wedge. **No source_entity_type set** because there is no Meeting entity to point at (gap).
- **Decision (renewal-wedge pivot, `69efbc914d65e2ca69b0dd5f`)** — the load-bearing Decision that drives v2 generation today.
- **Commitment (ship v2 by Apr 26, `69efbc914d65e2ca69b0dd61`)** — indemn-side, due_date set, Kyle + Cam.
- **Signal: insight (`69efbc924d65e2ca69b0dd63`)** — "bandwidth-constrained customers prefer narrow-wedge proposals over full Crawl-Walk-Run" — generalizable insight for future similar customers.

Transitioned to processed.

---

## Step 7 — Apr 21, 2026: BT Core integration emails (reclassify the misclassified ones — Bug #16 evidence)

**Real-life trigger.** Two emails between Kyle and Christopher Apr 21 about "Re: Indemn/Alliance - Exciting project with BT Core data." Email Classifier at the time created two new wrong Companies and classified the emails to them, instead of matching to the canonical Alliance Company. This is **Bug #16 manifest** — the exact failure mode.

### 7a — Reclassify

**Done.** `indemn email update 69ea550d... --data {"company": "<canonical_alliance>"}` and same for the other email. Both now point at canonical Alliance. (The auto-created wrong Companies remain as orphan rows pending the entity-resolution capability + cleanup pass.)

### 7b — Touchpoint for the Apr 21 BT Core thread

- Touchpoint **`69efbcad4d65e2ca69b0dd68`** — email/external, source_entity = the Email reclassified above.
- **Signal: blocker (`69efbcae4d65e2ca69b0dd6b`)** — Bug #16 instance documented as a Signal: "without entity-resolution, the customer-system loses timeline coherence — a customer's own emails wouldn't show up in their file."

Transitioned to processed.

---

## Step 8 — Apr 27, 2026 (today): Artifact Generator produces Proposal v2

**Real-life trigger.** Deal at PROPOSAL stage; latest Touchpoint is Apr 21; the Commitment to ship v2 by Apr 26 is overdue by 1 day. The Artifact Generator runs (played by Claude in this trace).

### 8a — Read the Playbook for PROPOSAL stage

The Playbook record for PROPOSAL stage didn't exist (only DISCOVERY existed). Created **Playbook record `69efbcf34d65e2ca69b0dd6e`** with the full PROPOSAL-stage shape: stage, description, entry_signals, required_entities, expected_next_moves, **artifact_intent**. The artifact_intent is the spec for what v2 must accomplish — anchored on real customer data, wedge-first sequencing, compound-outcome packaging, integration approach, concrete pricing.

This Playbook is also the template for any future PROPOSAL-stage artifact for any other customer.

### 8b — Read the entity graph

The Artifact Generator reads:
- Deal (ALLIANCE-2026, stage=proposal, next_step capturing the renewal-wedge ask)
- All Touchpoints since the last proposal version (Apr 7-8, Apr 8 meeting, Apr 21 — the conversations that shaped the v2 ask)
- Decisions (especially the renewal-wedge pivot + compound outcome packaging + BT Core OAuth)
- Signals (especially the real numbers + bandwidth constraint + 77% callback rate)
- Operations (especially Renewal outreach + Stewardship)
- Opportunities (especially the Retention Associate compound mapping)
- Proposal v1 + its source Document (the v1 proposal text — the structural template to evolve)
- Commitments (especially "ship v2 by Apr 26" + "Phase 1 waived investment from v1")
- CustomerSystem (BT Core, Alliance Internal CRM, etc. — for integration approach)

### 8c — Read example proposals from Drive

Per Craig's note, the Artifact Generator has access to Cam's proposals folder (`1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`) — Branch, Johnson, GIC, Charley, Physicians Mutual proposals + the SaaS Agreement. These all follow the same outcome-anchored, phased pattern. The Generator uses them as style and structure templates.

### 8d — Create Proposal v2 + Phases + link Opportunities

- **Proposal v2 `69efbd174d65e2ca69b0dd70`** — version=2, status=drafting, prepared_for=Christopher, prepared_by=Kyle, date_prepared=2026-04-27.
- **Phase 1 (`69efbd344d65e2ca69b0dd72`)** — Retention Associate compound, Months 1-2, $2,500/mo month-to-month, outcome=Client Retention, associates=[Renewal AT, Inbox AT, Knowledge AT].
- **Phase 2 (`69efbd354d65e2ca69b0dd74`)** — Lead Capture (bilingual), Months 3-4, $2,500/mo month-to-month, outcome=Revenue Growth, associates=[Front Desk AT].
- **Phase 3 (`69efbd354d65e2ca69b0dd76`)** — Service expansion (24% volume tier), Months 5+, $5K-10K/mo 12-month commitment, outcome=Operational Efficiency, associates=[Service AT, Inbox AT, Knowledge AT].
- **Opportunities → Phases linkage:** Stewardship + Outbound renewal → Phase 1; Missed-call capture → Phase 2; Billing + Payment + Knowledge + Document Requests → Phase 3.

### 8e — Render the v2 proposal Document

- **Document `69efbdea4d65e2ca69b0dd80`** — the rendered v2 proposal markdown. Full text in `artifacts/2026-04-27-alliance-proposal-v2.md`. Structure mirrors v1 (title, "Why this version" framing, customer-pain anchor, Phase tables, Implementation Roles, Operational Guardrails, Investment Summary, Next Steps, SaaS Agreement reference) but reorders to put renewal stewardship as Phase 1 + uses real Alliance numbers throughout + cites the compound-outcome framing.
- **Proposal v2.source_document** updated to point at this Document.
- **Proposal v2 transitioned drafting → internal_review** (awaiting Cam's pricing review + final alignment before send).

### 8f — Walk Proposal v1 forward

- v1 transitioned `under_review → rejected` to clear it as the active proposal. **Gap A8.1** — the Proposal state machine has `superseded` as a state but no transition path defined to reach it. v1 is more accurately *superseded*, not *rejected*. The rejected→superseded transition or a direct superseded path needs to be added.

### Step 8 — entity inventory

| Entity | ID | Notes |
|---|---|---|
| Playbook (PROPOSAL stage) | `69efbcf34d65e2ca69b0dd6e` | Reusable template for any customer's PROPOSAL stage |
| Proposal v2 | `69efbd174d65e2ca69b0dd70` | status=internal_review, source_document set |
| Phase 1 (Retention Associate compound) | `69efbd344d65e2ca69b0dd72` | $2,500/mo month-to-month, outcome=Client Retention |
| Phase 2 (Lead Capture bilingual) | `69efbd354d65e2ca69b0dd74` | $2,500/mo month-to-month, outcome=Revenue Growth |
| Phase 3 (Service expansion) | `69efbd354d65e2ca69b0dd76` | $5K-10K/mo 12-month, outcome=Operational Efficiency |
| Document (rendered v2) | `69efbdea4d65e2ca69b0dd80` | manual_upload; full text in artifacts/2026-04-27-alliance-proposal-v2.md |
| Proposal v1 | `69efba9650cea0a476d6fa9a` | now status=rejected (gap: should be superseded; state machine doesn't allow) |

---

## Trace summary — what the Alliance constellation now looks like in the OS

After the trace, the Alliance constellation is hydrated:
- **1 Company** (canonical Alliance, partially enriched — full enrichment is part of Phase B2 hydration ongoing work)
- **2 Contacts** (Christopher, Brian; need 5-6 more from Feb 1 meeting with richer source data)
- **1 Meeting** (Feb 1 — only one ingestible without Apollo backfill)
- **2 Documents** (v1 proposal + Capability Document) + **1 Document** for the rendered v2
- **7 Touchpoints** — Feb 1 / Feb 11 / Feb 19 / Feb 26 / Apr 7-8 / Apr 8/9 / Apr 21
- **6 Operations** — Alliance's actual business processes
- **8 CustomerSystem** — including BT Core, the carrier portal cluster, and the integration supporting tools
- **7 Opportunities** — all mapped to AssociateTypes + (where applicable) to Phases
- **2 Proposals** — v1 (now status=rejected; should be superseded) and v2 (status=internal_review)
- **3 Phases** — on Proposal v2, in order with the renewal wedge first
- **5 Decisions** — v1 ship; Retention Associate framing; compound outcome packaging; BT Core OAuth; renewal-wedge pivot
- **9 Commitments** — Feb 1 cohort + Phase 1 waived pilot + ship-v2-by-Apr-26
- **13+ Signals** — across champions / blockers / insights / churn_risk / expansion
- **1 Playbook record** (PROPOSAL stage; reusable for all customers)
- **The v2 proposal artifact** rendered to `artifacts/2026-04-27-alliance-proposal-v2.md`

This is the **constellation** — Alliance's full picture queryable from the Company hub via `indemn company get 69e41a82b5699e1b9d7e98eb --include-related --depth 3`. Cam can navigate the graph to find any piece. The v2 proposal is grounded in real source data, traceable line-by-line to entities.

## Trace gaps — aggregate (to be appended to os-learnings.md)

- **A1.1 / A3.3** — Apollo/Granola/Slack 30-day retention loses ground-truth content; OS should copy transcripts/Slack content into Document at ingestion to survive
- **A1.2 / A6.1** — Bug #10 backfill mechanism missing; historical events can't flow through pipelines that come online later
- **A1.3** — Bug #17 Meeting Classifier missing; Email Classifier should also handle Meetings or new Meeting Classifier needed
- **A1.4** — Entity-resolution kernel capability missing (Bug #16 root); demonstrated again in Step 7 with the 2 misclassified Apr 21 emails
- **A1.5** — Contact email population requires post-30-day enrichment path
- **A1.6** — Touchpoint Synthesizer needs explicit Deal-resolution logic (which Deal does this Touchpoint belong to?)
- **A1.7** — Bug #18 Synth must reliably back-reference Meeting.touchpoint
- **A1.8** — Auto-summary is thin source vs full transcript; Extractor should always prefer transcript
- **A1.9** — Stage-contemporaneous Playbook lookup needed (extract per the Stage at the touchpoint date, not current Stage)
- **A2.1** — Bug #30 sparse-on-nullable-unique fix not propagated to Email.external_ref (or other entities); audit needed
- **A2.2** — Email entity field still references `Interaction` (pre-Apr-23 rename); `interactions` collection still exists in MongoDB; Email.interaction needs renaming to Email.touchpoint
- **A3.1** — **Slack ingestion is foundational, not deferrable Phase F**; multiple Touchpoints in Alliance trace are Slack-sourced
- **A3.2** — Document.source enum missing `slack_file_attachment`
- **A8.1** — Proposal state machine lacks transition path to `superseded`; v1 ended up at `rejected` instead

These are aggregated and logged to os-learnings.md after this trace.

