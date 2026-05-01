---
ask: "Design the v1 USLI quote automation — extend the existing pipeline so usli_quote emails create or enrich a Unisoft Submission, attach the retailer + applicant PDFs, and fire the agent-facing notification. Brainstormed with Craig 2026-04-29."
created: 2026-04-29
workstream: gic-email-intelligence
session: 2026-04-29-b
sources:
  - type: slack
    description: "Self-DM note from Craig 2026-04-28 capturing JC's verbal walkthrough — the workflow JC described on the phone"
  - type: codebase
    description: "Full read of unisoft-proxy/{client/cli.py, client/unisoft_client.py, server/UniProxy.cs}; agent/harness.py; automation/agent.py; cli/commands/emails.py — the existing surface this feature plugs into"
  - type: research
    description: "Unisoft API extraction — operations-index.md (89 ops captured), wsdl-complete.md (910 ops total), raw SOAP payloads for SetSubmission, SetActivity, GetQuote, GetSubmissions, GetActionNotifications, GetQuoteActions"
  - type: mongodb
    description: "Live query of gic_email_intelligence.emails + .submissions on dev cluster via SSM into dev-services — 397 USLI-quote-linked submissions in last 30d, 388/97% intake_channel=usli_retail_web, 4/397 with unisoft_quote_id already linked"
  - type: brainstorming
    description: "Two-path collapse, scope (usli_quote only), folder destination, automatic-on-activity-create wiring — all confirmed with Craig 2026-04-29"
---

# USLI Quote Automation — Design

> **UPDATE 2026-05-01:** The Quote-lookup mechanism has been rearchitected after empirical findings invalidated the original "name-search with ambiguous-folder fallback" approach. **See `2026-05-01-usli-deterministic-lookup-architecture.md` for the canonical lookup algorithm — supersedes the "branched on lookup" section below.** The original design here is preserved as historical record; the deterministic-lookup artifact is authoritative for D.2 implementation.
>
> **UPDATE 2026-05-01:** Phase B.1 finding flipped the action_id-only spec to a **(action_id, letter_name) PAIR**. ActionId 67 ("Send offer to agent") has 25 templates; LetterName="USLI Quote" picks the carrier-specific one. `_create_activity_and_notify` must filter `GetActionNotifications` by LetterName, not pick `templates[0]` blindly. See `2026-05-01-unisoft-quote-search-canonical-shape.md` plus the implementation plan's revised C.4.
>
> **UPDATE 2026-05-01:** Phase B.3 — PDF detection uses a **whitelist policy** (upload only if filename matches retailer/applicant; default-skip everything else). Family 2 (Retail Web) has no "customer" string in any filename, so blacklist-on-customer would miss the small bare {REF}.pdf declaration page. Attachment field name is `name`, not `filename`.

## Goal

Extend the existing GIC Email Intelligence automation pipeline to handle `usli_quote` emails — USLI's quote responses that arrive at `quote@gicunderwriters.com` for retail agents. The system creates or enriches a Unisoft **Submission** (carrier-side offer record) under the appropriate Quote, attaches the retailer-version and applicant-version PDFs, and fires an activity that auto-sends the agent the quote follow-up via Unisoft's notification template.

The agent_submission automation is the structural twin: this is the same shape (deep agent + skill + deterministic finalizer + folder routing), targeting a different email type with a different downstream workflow.

## Non-Goals

- **`usli_pending` and `usli_decline` automation.** Each is a distinct workflow (relay info request to agent / decline notification to agent) with its own ActionId and risk profile. Same skeleton, different skill — captured as v2 follow-ups.
- **Authoring email body copy in code.** Notification body comes from Unisoft's template config tied to the chosen ActionId, owned by JC. We render merge fields and send.
- **Re-doing classification or linking.** Today's pipeline already classifies USLI emails as `usli_quote` and links them to Mongo submissions correctly. This feature consumes that output and acts on it.
- **Bundling unrelated cleanup from the same Slack note.** "[LOB] - Business description" task title format and "attachments uploaded with email body" completeness are tracked as separate follow-ups (see "Out of scope" below).
- **Generalizing the deep agent to a multi-skill dispatcher.** For v1 we add a parallel `create_automation_agent_usli()` factory; multi-skill dispatch is a refactor for later.

## Decisions Summary

| # | Decision | Where it landed |
|---|---|---|
| 1 | v1 scope = `usli_quote` only | Pendings + declines deferred |
| 2 | One skill handles both paths (broker + Retail Web auto-quote), branched by Unisoft search result | Two-path collapse |
| 3 | New Outlook folder `Indemn USLI Processed` for success | Mirrors existing folder routing |
| 4 | Agent email auto-fires by activity creation (deterministic, hidden from LLM) | Same shape as `_create_activity_and_notify` today |
| 5 | Notification body is Unisoft-template-driven, not code-authored | JC owns the template content |
| 6 | Quote lookup = name search + multi-field disambiguation; ref-based lookup is an *upgrade* if Retail Web stamps it | Investigation defers to build time |
| 7 | Failure modes mirror today: Inbox on failure, Duplicates on dup, success folder on success | Plus new "Needs Review" for ambiguous lookups |

## Background — Two Paths, One Volume Signal

USLI quote responses at `quote@` are produced by two distinct upstream flows:

### Path 1 — GIC manually submits to USLI (broker workflow)

JC creates the Quote in Unisoft, creates the Submission with carrier=USLI, logs the "submitted to USLI" activity. Eventually USLI's quote response email arrives. **The Quote and the USLI Submission both exist in Unisoft when our email arrives.** Our job: enrich the existing Submission with the quote info (`ConfirmationNo`, possibly `QuotedAmount`/`PolicyNo`), attach the retailer + applicant PDFs, and create the agent-facing activity.

### Path 2 — Agent submits directly via USLI Retail Web (auto-quote)

Agent goes to USLI Retail Web → USLI auto-quotes → USLI emails the agent the quote and CC's GIC. **Nothing exists in Unisoft when our email arrives.** Our job: create the Quote, create the USLI Submission, attach PDFs, create the activity.

### What the data tells us

Live query of `gic_email_intelligence.submissions` on the dev cluster (last 30 days):

| Signal | Value |
|---|---|
| USLI-quote-linked Mongo submissions | **397** (~13/day) |
| `intake_channel: usli_retail_web` | **388 / 97.7%** |
| `automation_level: auto_notified` | **385 / 96.9%** |
| With `unisoft_quote_id` already in Mongo | **4** — linkage doesn't exist today; this feature builds it |
| With `unisoft_submission_id` | **0** |

**Path 2 is the dominant case (~97%).** Path 1 is real but small. Both are handled by the same skill and the same code path; the Quote-lookup step is the disambiguator.

### One skill, branched on lookup

```
After identifying the email as usli_quote:
  Search Unisoft by insured name (+ agent + LOB + recency)
  ├─ 0 hits  → Path 2: create Quote + Submission + activity
  ├─ 1 hit, USLI Submission exists with same ConfirmationNo → DUPLICATE: skip
  ├─ 1 hit, USLI Submission exists with different/no ConfirmationNo → Path 1 enrich:
  │    SetSubmission Action=Update with ConfirmationNo + QuotedAmount, then activity
  ├─ 1 hit, no USLI Submission yet → Path 1 fork: create new USLI Submission, then activity
  └─ >1 hits → fail to "Needs Review" folder for human triage
```

## Workflow End-to-End

Mapped step-by-step to real CLI commands (existing or to-be-added).

```
0. Email arrives at quote@. Existing pipeline runs:
     sync → extract → classify → link
   email.classification.email_type = "usli_quote", linked to a Mongo submission.

1. Automation cron tick (every 15 min):
     gic automate run --type usli_quote --max 50

2. For each claim, the deep agent runs `process-usli-quote.md`:

   2a. Claim the email
       gic emails next --type usli_quote --json
       (returns email + linked submission + extractions)

   2b. Extract identity from email + extractions
       - insured = classification.named_insured
       - usli_ref = classification.reference_numbers[0]   (e.g. "MGL026A0EZ4")
       - agent_name, agency = parsed from subject (Retail Web pattern) or email body
       - lob = mapped from classification.line_of_business → Unisoft code (CG, CP, PL, ...)

   2c. Resolve the agent in Unisoft
       unisoft agents match --name "<agency>" [--phone ...] --compact
       unisoft contacts list --agent-number <N> --compact
       Pick the contact whose Email matches retail_agent_email (from Mongo submission)
       or the first active contact otherwise. Capture AgentContactID.

   2d. Find the Unisoft Quote
       unisoft quote search --name "<insured>" [--lob <code>]   (NEW CLI command)

       Filter results by:
         - effective_date within last 60 days
         - matches resolved agent_number
         - LOB matches
       Branch on result count:
         0 hits  → Path 2: go to step 2e
         1 hit   → Path 1: capture quote_id, go to step 2f
         >1 hits → fail to "Needs Review" folder, complete as failed, STOP

   2e. [Path 2 only] Create the Quote
       unisoft quote create --lob ... --sublob ... --agent <N> --name "<insured>" \
           --agent-contact-id <CID> --assigned-to indemnai \
           --address ... --policy-state FL --business-description "..."
       Capture quote_id from response.

   2f. Idempotency + Submission shape check
       unisoft submission list --quote-id <quote_id>

       Among returned submissions, look for any with CarrierNo=2 (USLI):
         - matching ConfirmationNo == usli_ref → DUPLICATE: complete as duplicate, STOP
         - exists with diff/empty ConfirmationNo → Path 1 update: go to step 2g (update)
         - none exists                          → go to step 2g (create)

   2g. Create or update the USLI Submission
       (Create case)
       unisoft submission create --quote-id <quote_id> --carrier 2 --broker 1 \
           --confirmation-no <usli_ref> \                 (NEW flag)
           --description "USLI Quote — <LOB display>" \
           --entered-by indemnai
       (Update case — Path 1 enrich)
       unisoft submission update --submission-id <M> --confirmation-no <usli_ref> \    (NEW command)
           [--quoted-amount <N>] [--policy-no <P>]
       Capture submission_id (M) from response.

   2h. Upload retailer + applicant PDFs (skip customer-version)
       For each PDF attachment whose filename / content matches "retailer" or "applicant":
         gic emails get <email_id> --attachment "<name>" --output /tmp/<name>
         unisoft attachment upload --quote-id <quote_id> --file /tmp/<name> \
             --category 15 --subcategory 30                # Documents / Offer
       Skip filenames matching "customer".

   2i. Record completion (deterministic activity + notification fires here)
       gic emails complete <email_id> \
           --quote-id <quote_id> \
           --submission-id <M> \
           --action-id <USLI_QUOTE_FOLLOWUP_ACTION_ID> \   (NEW flag)
           --notes "USLI Quote <usli_ref> — Path <1|2>" \
           --move-to "Indemn USLI Processed"

   The `gic emails complete` finalizer:
     a. Calls SetActivity with ActionId=<configured>, QuoteId, SubmissionId=M,
        AgentNo, LoggedByUser=indemnai
     b. Calls SendActivityEmail (IEmailService) with the rendered template body
        from GetActionNotifications + agent contact email
     c. Marks email automation_status=completed in Mongo
     d. Moves email to "Indemn USLI Processed" folder
```

## Pipeline Integration

Where this hooks into the existing system. **No changes to sync, classification, or linking** — those already produce `usli_quote` emails linked to submissions. The new code is in the automation layer only.

### Files touched

| File | Change | Rationale |
|---|---|---|
| `automation/agent.py` | Add `create_automation_agent_usli()` factory + `_build_usli_system_prompt()` that loads the new skill. Keep `create_automation_agent()` as-is for `agent_submission`. | Different skill, different system prompt. v1 keeps the two factories parallel — multi-skill dispatch refactor is later. |
| `automation/skills/process-usli-quote.md` | NEW skill markdown. Mirrors structure of `create-quote-id.md` — business context, sub-patterns, decision rules, step-by-step. | Source of truth for the agent's behavior. |
| `cli/commands/emails.py` | `_create_activity_and_notify()` → generalize to `_create_activity_and_notify(quote_id, action_id, submission_id=None)`. Update `complete_email()` to accept `--submission-id` and `--action-id`. | Same helper, parameterized over ActionId. |
| `cli/commands/automate.py` | Wire `--type usli_quote` to the new agent factory (existing infra dispatches by type already). | Add the type→factory map. |
| `unisoft-proxy/client/cli.py` | NEW: `unisoft quote search --name <S> [--lob <X>] [--limit N]`. NEW flag: `unisoft submission create --confirmation-no <REF>`. NEW: `unisoft submission update --submission-id <M> --confirmation-no <REF>`. | Wraps `GetQuotesByName2` and `SetSubmission Action=Update`. The proxy already supports the underlying SOAP ops. |
| `agent/harness.py` | No changes needed. | Linker already populates `automation_level: auto_notified` and `intake_channel: usli_retail_web` correctly. |

### Outlook folder addition

New folder under the quote@ inbox: **`Indemn USLI Processed`**. Auto-created by `email_mover.py` on first use (matches the existing pattern for `Indemn - Processing`, `indemn processed`, `Duplicates`).

### Cron entry point

Add a new automation cron, parallel to the existing one. (Or reuse the existing `automation-cron` container with two scheduled commands — TBD at implementation time. Both work.)

```yaml
# docker-compose.yml — option A: separate container
automation-usli-cron:
  command: python -m gic_email_intel.cli.main automate run --loop --interval 900 --type usli_quote --max 50
```

## CLI Surface — New / Changed Commands

### `unisoft quote search` (NEW)

Wraps `GetQuotesByName2` (and optionally `GetQuotesForLookupByCriteria` if we discover at build time that ref-based exact lookup is viable).

```bash
unisoft quote search --name "ABANOLAND LLC" [--lob CG] [--limit 10] [--compact]
```

Returns a list of Quote summaries: `QuoteID`, `Name`, `AgentNumber`, `LOB`, `EffectiveDate`, `ConfirmationNumber`. The skill instructs the agent to filter by recency + agent + LOB.

### `unisoft submission create --confirmation-no` (NEW flag)

Threads `ConfirmationNo` through to the SubmissionDTO. Empty string means nil — same convention as today.

### `unisoft submission update` (NEW command)

Wraps `SetSubmission Action=Update`. Loads the existing Submission shape via `GetSubmissions`, applies the diff (ConfirmationNo, QuotedAmount, PolicyNo), submits with `Action=Update`. Same fetch-then-modify pattern we use for attachment delete.

### `gic emails complete --submission-id --action-id` (NEW flags)

The finalizer accepts the SubmissionId and the ActionId. The `_create_activity_and_notify(quote_id, action_id, submission_id=None)` helper does both SetActivity (binding to the Submission via SubmissionId) and SendActivityEmail. Same two-call pattern as today, parameterized.

## Skill Outline — `process-usli-quote.md`

The skill mirrors `create-quote-id.md` in shape: business context → sub-patterns → decision rules → step-by-step. Key sections:

**Business context.** USLI is GIC's volume carrier. USLI quotes arrive in two upstream flows (Path 1 broker / Path 2 Retail Web). The skill explains both and instructs the agent to discover which by what it finds in Unisoft.

**Sub-patterns within `usli_quote`.** Three subject shapes today:
- `"USLI Retail Web Quote {REF} for {INSURED} from {AGENT} at {AGENCY}"` — `no-reply@usli.com`. Agent + agency in subject — extract directly. Dominant volume.
- `"USLI Instant Quote Services Quote {REF} for {INSURED}"` — instant quote service. Look up agent from email body or extraction.
- `"USLI Quote {REF} for {INSURED}     *****see Notes*****"` — manual underwriter (rare, small volume).

**Decision rules.**
- LOB mapping (USLI ref prefix → LOB): MGL→CG, MPL→CP, MSE→Special Events, etc. Reference table in the skill.
- PDF version detection: filenames or PDF first-page content typically contain "Retailer Copy" / "Applicant Copy" / "Customer Copy". Upload retailer + applicant; skip customer.
- Path branching by Unisoft Quote search result (the "branched on lookup" diagram above is the canonical version).

**Step-by-step.** Mirrors the workflow above (steps 2a–2i).

**When to fail.**
- Quote not found in Unisoft → Path 2 fallback (create Quote). If Quote creation also fails (e.g., agency not in Unisoft), fail-closed → Inbox folder.
- Multiple Unisoft Quotes match → "Needs Review" folder.
- USLI ref already on a Submission for this Quote → Duplicate folder.
- Activity creation fails after Submission creation → fail with `automation_result.error` capturing the partial state (`Submission M created on Quote N, activity creation failed: <reason>`). Do NOT mark as completed.

## Idempotency

Three-layer pattern, mirrors today's agent_submission flow:

1. **Mongo-side: `submission.unisoft_submission_id` already set** → email is a duplicate of one we already processed. Mark complete, route to Duplicates folder, no SOAP calls.
2. **Unisoft-side: Submission with carrier=2 + matching ConfirmationNo exists on the Quote** → another email for the same USLI ref already created the Submission (e.g., USLI sent the same notification twice, or we re-processed an old email). Skip, route to Duplicates, no activity.
3. **Unisoft-side: HasDuplicates=true on Quote create response (Path 2 only)** → Unisoft flagged the new Quote as a potential duplicate of an existing Quote. Don't fail the workflow (the Quote was created); note the dup IDs in completion notes for human review.

The pre-recovery check pattern (from migration phase B.7) applies here too: if `automation_status=processing` for >60min on a usli_quote email, recovery checks for a matching Mongo submission with `unisoft_submission_id` set before resetting; if found, treats as already-processed.

## Failure Modes & Folder Routing

| Outcome | Folder | Activity? | Email? | Notes |
|---|---|---|---|---|
| Success — new Submission created | `Indemn USLI Processed` | yes | yes | `automation_status=completed` |
| Success — Path 1 enrichment (existing Submission updated) | `Indemn USLI Processed` | yes | yes | `automation_result.notes` records "enriched existing submission" |
| Duplicate (Mongo or Unisoft side) | `Duplicates` | no | no | `automation_status=completed`, `automation_result.notes` describes which layer detected it |
| Quote not found AND Quote-creation fails (agency not in Unisoft, etc.) | `Inbox` | no | no | `automation_status=failed`, manual handling |
| Multiple Quotes match — ambiguous | **`Indemn USLI Needs Review`** (NEW folder) | no | no | `automation_status=failed`, JC manually picks the right Quote |
| Activity creation fails after Submission created | `Inbox` | no — partial | no | `automation_status=failed`, error includes Submission ID |
| Email send fails after activity created | `Inbox` | yes | no — partial | `automation_status=failed`, error includes Activity ID |

The `Indemn USLI Needs Review` folder is new. Alternative: route to `Inbox` and let JC find ambiguous cases there. **Decision deferred to JC** at build time — easier to ask once we have the system running.

## Email Recipient Resolution

Same approach as today's `agent_submission` flow:
- Resolve agent number via `unisoft agents match` (multi-field) using extraction data
- `unisoft contacts list --agent-number N` returns contacts with email addresses
- Pick the contact whose Email matches the email's `submission.retail_agent_email` (already populated by linker — sample shows `cesarjalas@gefsinsurance.com`)
- If no match, pick first active contact
- Set `AgentContactID` on the Quote (Path 2 — at quote create) — Path 1, AgentContactID is already set by JC's earlier broker workflow

`SendActivityEmail` then uses the contact's email as recipient. Notification body is rendered from the Unisoft template configured for the chosen ActionId.

## Build-Time Verification (open items, not design questions)

These get resolved during implementation, not now:

1. **Confirm exact ActionId for "USLI quote follow-up"** — JC mentioned a "USLI quote dropdown" in the UI. Best candidates from `GetQuoteActions`:
   - **101** — "Send offer follow up to agent" (closest match to JC's words)
   - 89 — "Quote follow-up"
   - 88 — "Submission follow-up"
   Pick by inspecting the Unisoft UI dropdown JC uses, or asking JC directly.

2. **Confirm the notification template is configured** for the chosen ActionId. Call `GetActionNotifications(ActionId=<chosen>)` against UAT — non-empty result means template exists. If empty, JC sets one up in the Unisoft admin UI as a precondition.

3. **Inspect a real Retail-Web-originated Quote in Unisoft (UAT or prod read-only)** — does `Quote.ConfirmationNumber`, `Quote.ApplicationNumber`, `Quote.OriginatingSystem`, or `Quote.Source` get stamped with the USLI ref? If yes, prefer ref-based exact lookup (`GetQuotesForLookupByCriteria` with that field) over `GetQuotesByName2`. **Upgrade-only optimization** — name search remains the v1 default.

4. **PDF version-detection signal.** Inspect 5–10 real USLI quote emails. Confirm whether retailer / applicant / customer versions are distinguishable by:
   - Filename pattern (likely)
   - PDF first-page text content
   - Email body description
   Pick the most reliable signal and codify in the skill. If filenames are inconsistent, fallback is content-pattern matching in the extractor.

5. **Folder for ambiguous lookups (>1 Quote matches).** New folder `Indemn USLI Needs Review` vs. routing back to `Inbox`. Quick decision with JC during soak.

6. **Confirm broker ID + carrier no in prod Unisoft.** Currently documented as BrokerId=1 (GIC), CarrierNo=2 (USLI). Validate against prod `GetCarriersForLookup` and `GET /api/1.0/brokers` — these may differ between UAT and prod (UAT is `GIC_UAT`, prod is `GIC`).

## Out of Scope — Tracked Separately

From the same Slack note (2026-04-28), two unrelated cleanup items that are NOT this feature:

1. **Task title format.** Update `agent_submission` automation to set task subject as `[LOB] - Business description` instead of `[Auto] {INSURED_NAME} — {LOB} via {AGENCY}`. Small change in `create-quote-id.md` step 6 + the `_truncate_subject` helper in `unisoft-proxy/client/cli.py`. Separate PR.
2. **Email body uploaded with attachments.** When uploading the email .eml to the Quote, ensure the email body content is preserved (currently only attachments come through). Investigation in `gic emails export` and the `--category email` upload path. Separate PR.

Captured here for traceability — neither blocks this feature, neither is included in this design.

## Rollout

1. **Build in dev branch.** Branch from `indemn/main` (post-cutover, post-soak — earliest 2026-04-30 morning).
2. **Test against dev-services + UAT Unisoft.** Same SOAK_MODE pattern from Phase G — flag-gated to skip Outlook folder moves and SendActivityEmail until validated. Process N real `usli_quote` emails into the soak DB; verify Quote + Submission + activity creation in UAT.
3. **Validate with JC** — pick 5 cleanly-handled cases from the soak run and walk JC through what was created in Unisoft UAT. Get sign-off.
4. **Deploy to dev-services prod (live mode).** Process actual incoming `usli_quote` emails into Unisoft UAT for ~24h. Watch for ambiguous-lookup cases, agency-not-found failures, multi-LOB edges.
5. **Cut over to prod-services + prod Unisoft.** Same pattern as the migration cutover — pause flag flip, customer comms to JC, monitor.

Estimated build time: ~1.5 weeks (1 week build + 0.5 week soak/validation), parallelizable with the post-cutover stabilization work. The skill markdown + CLI additions are mechanically straightforward; the soak/validation cycle is the long pole.

## Linear / Tracking

Create a child issue under DEVOPS-151 (parent epic) — proposed `DEVOPS-160 USLI quote automation`. Coordinate with JC on the ActionId + notification template precondition before starting build.

## What This Replaces / What Stays

- **Replaces:** the current "do nothing" behavior on `usli_quote` emails. Today they get classified, linked, marked `processing_status=complete`, and sit in the inbox. Volume estimate: ~13/day, ~4,000/year.
- **Stays:** classification (Rule 7 + LLM), linking (linker creates the Mongo submission), `automation_level: auto_notified` flag (unchanged — informational). Today's `agent_submission` automation is unaffected.
- **Adds:** Unisoft-side records (Quote/Submission for Path 2 emails — Path 1 already had them), agent-facing follow-up email per quote, complete audit trail in Unisoft for every USLI quote that lands at `quote@`.
