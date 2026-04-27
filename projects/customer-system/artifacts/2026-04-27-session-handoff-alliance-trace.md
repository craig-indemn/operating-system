---
ask: "Comprehensive session-handoff artifact ensuring 100% knowledge transfer to the next session. Captures what we set out to do today (Apr 27), what happened, current entity state, decisions aligned, open questions, gaps surfaced, AND — most importantly — the explicit next-session priorities Craig set: (1) re-generate the v2 proposal styled to match Cam's actual proposal templates from Drive; (2) build a customer-facing trace-showcase artifact (HTML or styled MD) for Kyle in the spirit of 2026-04-24-information-flow-v2.html. Read this FIRST in the next session."
created: 2026-04-27
workstream: customer-system
session: 2026-04-27-alliance-trace
sources:
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-27-alliance-trace-plan.md"
    description: "Pre-execution plan for the trace"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-27-alliance-trace.md"
    description: "The trace narrative — every step documented"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-27-alliance-proposal-v2.md"
    description: "The v2 proposal artifact (markdown) generated this session — the basis for next session's styled regeneration"
  - type: conversation
    description: "Apr 27 working session — vision crystallization morning + Alliance v2 trace afternoon + bugfix fork in parallel"
---

# Session Handoff — 2026-04-27 (Alliance v2 Trace + Vision/Roadmap Crystallization)

This artifact is the single starting point for the next session. Read this in full before any other work in the next session. Sister files: `vision.md` + `roadmap.md` + `os-learnings.md` + `INDEX.md` + `CLAUDE.md` + `fork-prompts/os-bugfix-resume.md` are all current and coherent — this handoff stitches them together for fast onboarding.

---

## What we set out to do (Apr 27)

Per Craig's session-start prompt:

1. Trace Alliance Insurance end-to-end through the OS to produce a v2 (revised) Proposal document and the "story" of how we got there — same shape as the GR Little email demo but for the PROPOSAL stage / NEGOTIATION transition. Cam needs v2.
2. Secondary trace: Arches Insurance.
3. Brainstorm + vision refresh — the trace and the brainstorm are one activity. Output: refreshed vision document, updated roadmap, the v2 Alliance proposal artifact.
4. Wait for Craig's alignment before substantive trace work.

## What happened (in order)

1. **Comprehensive prep + brainstorm** (morning) — read all required project artifacts + OS docs (CLAUDE.md, vision-and-trajectory inspiration, Kyle Apr 21 + Apr 24 transcripts in full, OS white paper + 6 architecture docs + domain modeling guide, etc.). Found Cam's Arches forwarded message in Slack (Rocky's intro for Jeff Hamilton at Arches Insurance Agency). Identified Cam's proposal folder Drive `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph` (6 customer proposals: Alliance, Branch, Johnson, GIC, Charley, Physicians Mutual + SaaS Agreement). Pulled v1 Alliance proposal from Drive Doc `1KDeMtV3...`.

2. **Vision crystallization brainstorm with Craig** — long conversation aligning on:
   - Scope: customer-system as primary, OS as parallel track, horizons (2)/(3) visible but out-of-scope-here
   - Spine ordering: dual-track frame → end-state → breakthrough as lens
   - End-state: foundation (9 structural capabilities) + two threads on top (meeting view + proposal generation), with horizons visible
   - The Two Threads — both surface OUT of one foundation, not separate features
   - Roadmap shape: Phase A (shake-out traces) → Phase B (build to autonomous, sub-phases B1-B4) → Phase C (dashboarding) → Phase D (adoption) → Phase E (evaluations + feedback loop) → Phase F (Slack ingestion DEFERRED — later moved up after the trace)
   - Continuous threads: OS bug convergence (forks) + OS-side milestones + shared-context-update mechanism
   - Persistent-AI loops out of scope for this roadmap
   - Document split: lean spine files at project root (`vision.md` + `roadmap.md`), depth in artifacts + os-learnings.md

3. **Created `vision.md` + `roadmap.md` at project root** — the customer-system equivalent of the OS repo's documentation system.

4. **Updated INDEX.md + os-learnings.md per discipline** — new decisions appended, new artifacts in table, new open questions.

5. **Set up the parallel OS-bugfix fork session** — Craig forked from this session early; the fork prompt I wrote (`fork-prompts/os-bugfix-resume.md`) became the operational discipline for parallel work.

6. **Saved the Alliance trace plan** (`artifacts/2026-04-27-alliance-trace-plan.md`) before executing — reusable template for any future trace. Craig pushed back HARD on the initial bulk-load approach: "TRACING means going from beginning to end HOW THE INFORMATION WOULD ACTUALLY FLOW IN REAL LIFE... AND YOU SHOULD ACT AS THE ASSOCIATE, NOT JUST USE THE CLI."

7. **Resolved CLI auth** — Craig's `~/.indemn/credentials` was stale; refreshed via `/auth/refresh` endpoint. The right CLI binary is `/Users/home/Repositories/indemn-os/.venv/bin/indemn` (the system alias points at bot-service's binary — wrong).

8. **Pulled the Capability Document from Slack** — when Craig mentioned the "30-page analysis is in Slack, not Drive" → searched Slack → found `2026-02-18-capability-document.md` (Slack file `F0AGS9LL064` in `#customer-implementation`). Downloaded. This is the analytical foundation for everything Alliance.

9. **Hit Bug #30 (Meeting create returns 500) + the API 500-detail issue** mid-trace. Logged immediately to `os-learnings.md`. **The bugfix fork session picked them up via the resume-prompt mechanism and shipped both within minutes** — proving the shared-context-update mechanism works end-to-end. Then the trace resumed with the now-informative API errors.

10. **Walked the Alliance trace through 8 timeline steps** acting as each associate at each step:
    - Step 1 (Feb 1) — Discovery call: Meeting + 2 Contacts (Christopher, Brian) + Touchpoint with Option B pointers + 7 Commitments + 4 Signals
    - Step 2 (Feb 11) — v1 proposal sent: Email + Document (v1 proposal text) + Touchpoint + 1 Decision + 1 Commitment + 1 Signal + Proposal v1 walked drafting → internal_review → sent → under_review
    - Step 3 (Feb 18-19) — Capability Document analysis: Document (42K markdown) + Touchpoint + 6 Operations + 7 CustomerSystem + 7 Opportunities (mapped to AssociateTypes) + 6 Signals
    - Step 4 (Feb 26) — Capability doc PDF DM to Ryan: reference Touchpoint
    - Step 5 (Apr 7-8) — Retention Associate prep thread: BT Core CustomerSystem + Touchpoint + 3 Decisions (Retention Associate framing; compound outcome; BT Core OAuth) + 3 Signals
    - Step 6 (Apr 8/9) — Renewal-wedge pivot meeting: Touchpoint + 1 Decision (the pivot itself) + 1 Commitment (ship v2 by Apr 26) + 1 Signal
    - Step 7 (Apr 21) — BT Core integration emails: reclassified 2 misclassified emails to Alliance + Touchpoint + 1 Signal (Bug #16 instance)
    - Step 8 (Apr 27, today) — Artifact Generator generates v2: PROPOSAL-stage Playbook record + Proposal v2 (drafting → internal_review) + 3 Phases (Retention/Lead Capture/Service-expansion) + Opportunities → Phases linkage + Document for rendered v2 + Proposal v1 walked under_review → rejected (gap: should be superseded; state machine doesn't allow)

11. **Rendered the v2 proposal artifact** — `artifacts/2026-04-27-alliance-proposal-v2.md` — markdown form, full structure, line-to-entity mapping table proving every claim traces to OS entities.

12. **Updated all spine files per the end-of-session discipline** — INDEX.md, roadmap.md, CLAUDE.md, os-learnings.md.

## Current entity state in dev OS `_platform` org

Alliance constellation hydrated to 60+ entities, queryable from Company hub:

```
indemn company get 69e41a82b5699e1b9d7e98eb --include-related --depth 3
```

**By type:**
- Company: `69e41a82b5699e1b9d7e98eb` (canonical Alliance Insurance — partially enriched; needs name/domain/website/location backfill)
- Contacts: Christopher Cook `69efb8f350cea0a476d6fa69`, Brian Leftwich `69efb8f450cea0a476d6fa6b`
- Meeting: Feb 1 discovery `69efb8c150cea0a476d6fa66` (the only Meeting we could create — Apr 8 meeting NOT in OS)
- Documents: v1 proposal `69efba5f50cea0a476d6fa8e`; Capability Document `69efbb1150cea0a476d6fa9f`; rendered v2 `69efbdea4d65e2ca69b0dd80`
- Touchpoints: 7 — Feb 1 `69efb91d50cea0a476d6fa6d`, Feb 11 `69efba8350cea0a476d6fa90`, Feb 19 `69efbb2950cea0a476d6faa1`, Feb 26 `69efbc6a4d65e2ca69b0dd46`, Apr 7-8 `69efbc6c4d65e2ca69b0dd4c`, Apr 8 meeting `69efbc914d65e2ca69b0dd5c`, Apr 21 BT Core thread `69efbcad4d65e2ca69b0dd68`
- Operations: 6 — Renewal outreach, Inbound, Quote, Billing, Payment, Stewardship
- CustomerSystem: 8 — Alliance internal CRM, Conga Sign, Salesforce, Ascend, Carrier portal cluster, RCE, Canopy Connect, BT Core
- Opportunities: 7 — all mapped to AssociateTypes + (most) to Phases
- Proposals: v1 `69efba9650cea0a476d6fa9a` (status=rejected; should be superseded), v2 `69efbd174d65e2ca69b0dd70` (status=internal_review)
- Phases on v2: Phase 1 Retention Associate compound `69efbd344d65e2ca69b0dd72`, Phase 2 Lead Capture `69efbd354d65e2ca69b0dd74`, Phase 3 Service expansion `69efbd354d65e2ca69b0dd76`
- Decisions: 5
- Commitments: 9
- Signals: 13+
- Playbook: PROPOSAL stage `69efbcf34d65e2ca69b0dd6e` (reusable for all customers)

## Decisions aligned this session

(All also appended to INDEX.md Decisions log.)

- 2026-04-27: Vision document split — `vision.md` (slow-changing end-state) + `roadmap.md` (living source of truth) at project root. Lean spine files; depth in artifacts/os-learnings.
- 2026-04-27: Customer-system "done" = foundation (9 structural capabilities) + two threads on top (meeting view + proposal generation). Hydration of all customers/prospects implied in achieving foundation, not separate.
- 2026-04-27: Comprehensive pre-scoped roadmap — Phases A→F + continuous threads. All work pre-scoped here, not "what emerges later."
- 2026-04-27: OS bug list converges to zero on items we choose to prioritize. Compute is not a constraint. Forking parallel sessions is first-class operating mode, starting as soon as Phase B begins.
- 2026-04-27: LangSmith on all harnesses + deep OTEL tracing as foundation requirement (B1). Evaluations as feedback mechanism active throughout.
- 2026-04-27: Persistent-AI loops are explicitly OUT of scope for this roadmap.
- 2026-04-27: Phase A complete after A2 (Alliance proposal trace).
- 2026-04-27: Trace-mode discipline — trace as if the OS were running per the vision. Act AS each associate, document every step, write entities to OS via CLI throughout. NOT a bulk hydration.
- 2026-04-27: Slack ingestion is FOUNDATIONAL, not deferrable Phase F. Roadmap.md updated to move Slack to early Phase B.
- 2026-04-27: Shared-context-update mechanism worked end-to-end as designed. `fork-prompts/os-bugfix-resume.md` is the operational discipline for future parallel-session work.
- 2026-04-27: v2 Alliance proposal generation pattern confirmed — `(Deal at PROPOSAL + recent Touchpoints + extracted intel + Playbook + raw source content from prior versions + example proposals from Drive) → Artifact Generator → rendered Document`. Same mechanism as GR Little; only Playbook record changes per stage. Validates the Apr 23 breakthrough across two distinct stages.

## Open questions added this session

(All also appended to INDEX.md Open Questions.)

- Where exactly do the 12 sub-stages with archetype multi-select live structurally? (Resolved during B3 stage research.)
- How does the OS preserve transcripts/files past the source's retention window? (Apollo/Granola/Slack 30-day retention loses ground-truth content.)
- How is "scope" determined for Touchpoints when participants aren't yet Contacts (chicken-and-egg with Synth flow)?
- Does the shared-context-update mechanism scale to N parallel sessions? Probably not as-is at very high N — refinement is its own work item that surfaces as parallel sessions multiply.

## OS bugs landed this session (parallel bugfix fork)

🟢 = merged to main + deployed; 🟡 = PR open awaiting review

- 🟢 Touchpoint Option B (source pointers — schema + Synth skill v3)
- 🟢 Silent workflow stuck-state — agent-output detection + queue fail
- 🟢 Cross-invocation tool-cache leak — per-activity scoping
- 🟢 API 500-detail — validation errors now informative (was generic "Internal Server Error")
- 🟢 Entity-skill JSON-shape examples — generator emits payload examples
- 🟢 Bug #30 sparse-on-nullable-unique fix (Meeting create) — also unblocks Company create (Bug #25)
- 🟢 Bug #29 route eviction — entity-def hot-update now works without redeploy

Several unblocked the trace as it progressed (Bug #30 + API 500-detail came online mid-trace).

## OS gaps SURFACED this session (logged to os-learnings.md, work TBD)

- **Bug #30 fix needs propagation to all entities** — applied to Meeting.external_ref but not Email.external_ref (and likely Document.drive_file_id and others). Audit needed.
- **Stale entity-skill rendering** — skills aren't auto-regenerated when the generator code changes. Older entities serve their pre-fix skill content. Affects every quality improvement going forward.
- **Email entity field still references `Interaction` instead of `Touchpoint`** — pre-Apr-23-rename gap. The `interactions` collection still exists alongside `touchpoints`.
- **Slack ingestion is foundational** — Roadmap.md updated; new Slack adapter work needed (channels + DMs + MPDMs + file attachments → Documents).
- **Document.source enum missing `slack_file_attachment`** — used `manual_upload` as workaround for the Capability Document.
- **Proposal state machine lacks `superseded` transition path** — v1 ended up at `rejected` instead of `superseded` because no path exists.
- **Bug #10 backfill mechanism continues to bite** — Feb 1 + Apr 8 Meetings are past 30-day retention window; can't be ingested now.
- **Touchpoint scope/Contact-resolution chicken-and-egg** — Synth needs Contact existence to determine scope, but Contacts get created in the same cascade.

---

## NEXT SESSION — explicit Craig priorities

Craig stated at session end (verbatim from his message):
> "I want to continue this work in a new session. Starting with actually having the proposal generated based on the proposal templates we have (to match the theme, styling, etc). And like I shared with Kyle, having an artifact that I can use to showcase how we traced through everything and how it all fits together in the operating system."

Two explicit deliverables for next session, in this priority order:

### Next-session deliverable 1 — Re-render v2 proposal styled to match Cam's existing proposal templates

**The v2 proposal we generated today** (`artifacts/2026-04-27-alliance-proposal-v2.md`) is **content-correct but stylistically generic markdown**. Cam's actual proposal portfolio in Drive `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph` follows a specific visual + structural style — it's what Cam's customers expect and what the team uses for every proposal.

**What to do:**
1. **Read each proposal in the Drive folder** to understand the template — Charley, Branch, Johnson, GIC, Physicians Mutual, plus the SaaS Agreement. Look at:
   - Header / cover page format
   - Section ordering + naming conventions ("Strategic Partnership Proposal: Your Digital Workforce Roadmap" — title pattern; "Unlocking Revenue Capacity" / "Addressing the Implementation Gap" — section pattern)
   - Phase tables — formatting, column conventions, currency formatting
   - Implementation Timeline section — Days 1-7 / 8-30 / 31-60 cadence
   - Implementation Roles & Commitment table — week-by-week format with Alliance commit + Indemn responsibility columns
   - Operational Guardrails section
   - Investment Summary table
   - Acceptance & Authorization signature block
   - Embedded SaaS Agreement
2. **Re-generate the v2 proposal in the same form** — could be a Google Doc (via `gog docs` API), an HTML/PDF, or markdown that matches the visual rhythm. Goal: when Cam opens it, it FEELS like one of his proposals (because it IS), but the content is the trace-derived v2 (renewal-wedge first; Retention Associate compound; real Alliance numbers; etc.).
3. **The substantive content is DONE** — it lives in the Proposal v2 entity + Phases in the OS + the v1 source-text + the Capability Document. The next session's work is render-and-style, not re-think.
4. **Likely tools:** `gog docs cat` to read each Cam template, then create a new Doc via `gog docs create` (if supported) or generate PDF. The Artifact Generator associate would have access to the proposals folder per Craig's direction — same path.

**The v2 in `artifacts/2026-04-27-alliance-proposal-v2.md` is the substantive draft Cam should review for content / structure. The styled render is what gets sent to Christopher.**

### Next-session deliverable 2 — Customer-facing trace-showcase artifact for Kyle

In the spirit of `artifacts/2026-04-24-information-flow-v2.html` (the visual one-pager that Kyle validated for GR Little), build the **Alliance v2 equivalent**: a polished visual artifact showing how the OS traced everything Alliance-related and produced the v2 proposal. Kyle wants to see + show this internally.

**What it should show:**
- The Alliance timeline (Feb 1 discovery → Feb 11 v1 → Feb 18-19 Capability Doc → Apr 7-8 prep thread → Apr 8 pivot → Apr 21 BT Core → Apr 27 v2 generation)
- Per-timeline-event: which entities were created (Touchpoint, Decisions, Signals, Commitments, Operations, Opportunities)
- The Proposal-as-spine growth — Proposal v1 sent → Proposal v2 rendered, with the Phases + Opportunities visible underneath
- The mechanism table — same `(Deal + Touchpoints + extracted intel + Playbook + raw source) → artifact` mechanism every step, only Playbook record changes
- Quote → entity → proposal-line table (parallel to GR Little artifact's quote→entity→email-line) — showing how specific Alliance content (e.g., Christopher's stewardship-prep ask, Peter's data validation, the renewal-wedge pivot) traces to specific entities and ultimately to specific lines in the v2 proposal

**Should be a single HTML file** (per `2026-04-24-information-flow-v2.html` precedent) — Kyle opens in browser, can show internally without rendering software. Visually polished, not raw markdown.

### Next-session prep (the same start-of-session protocol from CLAUDE.md applies)

1. Read CLAUDE.md fully (newly updated with Session 6 entry + Phase A done state).
2. Read INDEX.md (newly updated Status, 5 Decisions appended today, 4 Open Questions appended today, 4 new artifacts in table).
3. Read os-learnings.md (newly updated — 7 bugs landed today + new gaps logged).
4. Read this handoff in full (you're doing that now).
5. Read `vision.md` + `roadmap.md` (created today; both lean spine files).
6. Read the trace + plan + proposal artifacts:
   - `artifacts/2026-04-27-alliance-trace-plan.md`
   - `artifacts/2026-04-27-alliance-trace.md`
   - `artifacts/2026-04-27-alliance-proposal-v2.md` ← the substantive draft to re-render in styled form
7. Read the GR Little reference artifacts:
   - `artifacts/2026-04-24-information-flow-v2.html` (open in browser) ← THE TEMPLATE for next-session deliverable 2
   - `artifacts/2026-04-24-grlittle-followup-email-draft.md` ← line-to-entity mapping pattern
8. Pull every file from Cam's proposal folder (`1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`) — for next-session deliverable 1.
9. Check `fork-prompts/os-bugfix-resume.md` — see what the bugfix session has shipped since the handoff.
10. Then BEGIN deliverable 1 (styled v2) — get Cam's reaction. THEN deliverable 2 (trace-showcase HTML for Kyle).

### What NOT to redo

- Don't re-walk the trace. The entity graph is hydrated.
- Don't re-design v2. The entity-driven content is in the OS + the markdown draft. Re-rendering is style + structure work.
- Don't re-litigate the Slack-as-foundational decision (it's in roadmap.md).
- Don't re-create the PROPOSAL-stage Playbook record (it exists at `69efbcf34d65e2ca69b0dd6e`).

### Follow-on work after the two deliverables

Once next-session deliverables 1 + 2 land:
- **Phase B begins.** B1 (foundation hardening) absorbs remaining bugs from `os-learnings.md` (entity-resolution capability is the biggest one). B2 (hydration) starts with Arches + FoxQuilt + active prospects (Tillman, Rankin, O'Connor, Amynta, IIANC five via Pat Klene, etc.).
- Cam reviews v2 → revisions → ship to Christopher.
- Watch for Christopher's response → if positive, update Deal stage → trigger NEGOTIATION-stage Playbook seed (next Playbook record).

---

## How this session worked operationally (worth preserving for next session)

- **Trace mode discipline** — write entities to OS via CLI at every step; document every step; play associates explicitly. Not bulk-load.
- **Shared-context-update mechanism** — main session logged findings to `os-learnings.md`; bugfix session read them on resume; no human-in-the-middle handoff. Confirmed working at scale today (7 bugs landed in parallel during one trace).
- **Living `fork-prompts/os-bugfix-resume.md`** — the paste-ready prompt for the bugfix session. Update its "Recent fork-session progress" snapshot whenever a fork session marks a row 🟡 / 🟢. The "UPDATED PRIORITY" block adapts to new findings.
- **Token refresh** — the indemn auth token has a 15-minute lifetime; refresh via `POST /auth/refresh` with the refresh_token from `~/.indemn/credentials`. The CLI doesn't auto-refresh; expect to refresh every ~15 minutes during long work sessions.
- **The right CLI binary** — `/Users/home/Repositories/indemn-os/.venv/bin/indemn`, NOT the alias which points at bot-service's binary.
- **mongosh wrapper has wrong host (Bug #12)** — for direct mongo queries use `mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/indemn_os" --quiet --eval '...'` directly.

---

## Session sign-off

This handoff is the load-bearing knowledge transfer. Everything else (CLAUDE.md, INDEX.md, vision.md, roadmap.md, os-learnings.md, the trace + proposal artifacts, the fork-prompt) is current and coherent as of this checkpoint. The next session can start with this artifact + the CLAUDE.md start-of-session protocol and have 100% of what it needs.

The two next-session deliverables — styled-v2-proposal + trace-showcase-HTML-for-Kyle — are explicit + scoped + tooled (gog drive + gog docs + the existing artifact-as-template patterns). Begin there.

End of session 2026-04-27.
