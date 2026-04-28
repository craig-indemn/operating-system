# Customer System — Roadmap

> Living source of truth for **how we get from where we are now to the vision**. Updated every session that moves the work forward. Read with `vision.md` (what we're building, why, and the lens) and `os-learnings.md` (running register of OS bugs + capability gaps + design questions).
>
> Last updated: **2026-04-28** (morning — trace-showcase HTML + Cam/Kyle share).

---

## Where we are now (2026-04-27)

**Foundation status — not yet running autonomously.**

- **27 entity definitions live** in dev OS, `_platform` org. Includes Playbook entity (DISCOVERY record seeded), all 22 from the Apr 22 brainstorm.
- **Pipeline associates state:** Email Classifier — *suspended*. Touchpoint Synthesizer — *suspended*. Intelligence Extractor — *active* (was activated Apr 24 to test, failed structurally). All three need work before they can be re-enabled hands-off.
- **GR Little hydrated end-to-end** (the one customer that has been traced through the system): canonical Company picked from 5 dupes, Walker + Heather Contacts, Deal at DISCOVERY, Meeting linked, Touchpoint synthesized manually, intelligence extracted manually, 3 Opportunities created, empty Proposal v1, follow-up email drafted. **Kyle saw it Apr 24 and validated.** The 4 Company dupes are flagged but not deleted (Bug #23 blocks bulk-delete with operator filters).
- **~930 emails ingested** across 11 team members (Kyle + team). 284 irrelevant, 180 processed E2E, 114 needs_review. Queue drained to zero. ~67 meetings ingested for Apr 20-21 window.
- **Alliance not yet hydrated.** First proposal trace is today's session.
- **OS bugs** — 29 logged, 4 fixed. Critical/blocking open: Touchpoint source pointers (Option B), entity-resolution kernel capability (Bug #16 root fix), Bug #29 (entity-def replacement doesn't evict API routes), Bug #23 (bulk-delete operator filters).
- **Open design questions** — Opportunity vs Problem; Document-as-artifact pattern for emails. See `os-learnings.md` for full list.

For deeper status: `artifacts/2026-04-25-session-handoff-and-roadmap.md` (the previous session's roadmap, which this supersedes).

---

## Phases (pre-scoped)

The phases are sequential at the level of "Phase B starts when Phase A is done," but iteration happens *throughout*. Phases are the work; iteration is the mode.

---

### Phase A — Shake-out traces (in flight)

**Purpose.** Validate the vision against real customer situations. Each trace produces an artifact that demonstrates what the system should produce. The traces are exploratory — Claude-in-conversation plays the role of the autonomous Artifact Generator. Output: artifacts to react to + gaps to log.

- **A1 — GR Little discovery-call meeting view** *(done, Kyle validated 2026-04-24)*
  - Output: `artifacts/2026-04-24-grlittle-followup-email-draft.md` + `artifacts/2026-04-24-information-flow-v2.html`
  - Validates: DISCOVERY-stage artifact mechanism (follow-up email)
- **A2 — Alliance proposal generation** *(✅ done 2026-04-27)*
  - Output: `artifacts/2026-04-27-alliance-proposal-v2.md` + `artifacts/2026-04-27-alliance-trace.md` + `artifacts/2026-04-27-alliance-trace-plan.md`
  - Validates: PROPOSAL/NEGOTIATION-stage artifact mechanism (revised proposal doc) — same `(Deal + recent Touchpoints + extracted intel + Playbook for stage + raw source) → artifact` mechanism as A1, only the Playbook record differs.
  - Generated via the trace pattern (act as each associate, write entities to OS at each step). Hydrated 60+ entities into Alliance constellation.
  - PROPOSAL-stage Playbook record `69efbcf34d65e2ca69b0dd6e` created — reusable for all customers.
  - In parallel: 7 OS bugs fixed/in-progress by the bugfix fork session (Touchpoint Option B, silent stuck-state, cache leak, API 500-detail, Bug #30 Meeting create, entity-skill JSON examples, Bug #29 route eviction).
- **A2 follow-on — Styled PDF rendering pipeline + Cam-portfolio match** *(✅ done 2026-04-27 evening)*
  - Output: `templates/proposal/` (template.hbs + template.css + saas-agreement.partial.hbs + assets) + `tools/render-proposal.js` + `artifacts/2026-04-27-alliance-proposal-v2.{json,html,pdf}` + `skills/artifact-generator.md`
  - Validates: HTML→PDF via puppeteer-core against system Chrome is the right tooling for the Artifact Generator's rendering step. The Handlebars JSON contract cleanly separates content (associate produces) from presentation (template provides).
  - Match-quality with Cam's portfolio (Alliance v1, Charley, Branch, Johnson, GIC, Physicians Mutual, Arches) verified through several rounds of visual diff. 9 pages matching Cam's section-per-page rhythm. Brand-consistent footer swoosh (rounded top-left, sharp bottom-left, bleeds right + bottom, white logo via CSS filter). 15 style guidelines captured in the skill.
  - Document `69efbdea4d65e2ca69b0dd80` in OS updated: `mime_type: application/pdf`, `file_size: 178935`, content pointer to repo file path.

- **A2 follow-on — Kyle-facing trace-showcase HTML for Alliance** *(✅ done 2026-04-28 morning)*
  - Output: `artifacts/2026-04-27-alliance-trace-showcase.html` — single self-contained file (833 lines, all CSS inline) using the Kyle-validated GR Little v2 visual language as the base. Five sections: proposal cover hero with Drive PDF link / vertical 8-event timeline / extraction table (10 quote→entity→proposal-line rows) / mechanism table with PROPOSAL "you are here" + Demo "skipped" / proposal-as-spine showing v1 → v2.
  - v2 PDF uploaded to Cam's proposals folder on Drive (`1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`, file ID `1pM3tYg6rHzG8RW6xU_titouiq_iddhIC`); Drive link wired into the showcase hero CTA.
  - Shared with Cam + Kyle in `mpdm-cam--kwgeoghan--craig-1` (channel `C0A3B18LY07`) — thread reply to Cam's Apr 21 ask about proposal output, with `reply_broadcast=True` so it surfaces at channel-top.

**Phase A is COMPLETE.** Two stages traced (DISCOVERY + PROPOSAL/NEGOTIATION), both Kyle-facing artifacts shipped (GR Little visual Apr 24, Alliance showcase Apr 28), proposal PDF in Cam's portfolio for review/sending. Mechanism validated across two distinct stages. Intermediate stages (CONTACT, DEMO, VERBAL/SIGNED) hydrate naturally from B3 stage research.

**Next: Phase B starts.** With the OS bugs fixed in parallel during the trace, the foundation is much closer to being shipped autonomously. B1 (foundation hardening) absorbs the remaining bugs from `os-learnings.md` — most direct unblock is propagating the entity-resolution kernel capability (shipped Apr 27) into the Email Classifier + Touchpoint Synthesizer skills so Bug #16 (auto-create Companies) is closed end-to-end. B2 (hydration) starts with the rest of the active prospects + customer roster.

---

### Phase B — Build to autonomous (the bulk)

**Purpose.** Develop the entire customer system to the point where it runs autonomously per the vision. **This is when "the customer system is achieving its own vision."**

The work in B is large and pre-scoped here. Bug-fixing forks happen in parallel as soon as B starts.

#### B1 — Foundation hardening

The 9-item structural list from `vision.md §2`, made real:

- **Entity model complete + accurate.** Touchpoint Option B implemented (`source_entity_type` + `source_entity_id` fields; Synthesizer populates them). Playbook entity definition consulted by both Extractor and Artifact Generator. Open entity-model questions resolved (Opportunity vs Problem; Document-as-artifact for emails — see `os-learnings.md` Open Design Questions).
- **Entity-resolution capability built in the kernel.** New CLI: `indemn entity resolve --type Company --domain X --name Y --email Z` returns ranked matches with confidence. Associates call it before any `create`. Root fix for Bug #16 / 446-Companies.
- **Pipeline associates reactivated and running hands-off.** Email Classifier, Touchpoint Synthesizer, Intelligence Extractor. No silent stuck states (workflow detects empty agent output). No cross-invocation cache leaks (`/large_tool_results/` scoped per `message_id`). Generated entity skill teaches actual filter syntax.
- **Watch cascade reliable end-to-end.** Email/meeting → Touchpoint → intelligence → opportunities → proposal → artifact. Every link works. Reverse-lookup capability where needed (`--include-related` follows reverse refs, or rename the flag).
- **Temporal workflows manageable + OTEL spans observable.** Deep tracing on every operation. We can see what is happening at any point in any workflow.
- **LangSmith on all harnesses.** AI observability everywhere associates run. Evaluations infrastructure ready for use as the feedback mechanism (Phase E).
- **OS itself dogfooded as designed.** Patterns designed but never used in practice get used during this work. This is the test that the OS is what we believe it to be.
- **All P0/P1 OS bugs from `os-learnings.md` resolved.** Including: Bug #29 (route eviction in `kernel/api/registration.py`), Bug #23 + #24 (bulk-delete operator filters + status reporting), Bug #22 (per-associate service tokens or `effective_actor_id` for forensics), Bug #9 (associates pass dicts vs ObjectIds — skill prompt + entity-skill enhancement), Bug #10 (no backfill / re-trigger for historical entities), Bug #18 (Synth doesn't update `Meeting.touchpoint` back-reference — subsumed by Option B), plus the medium register (#25-28, #19-21, #5-8, #11-13, #15, #2-4).

**B1 done test.** A new email or meeting can be dropped into the system and the cascade runs cleanly without manual intervention.

#### B2 — Hydration

Get every customer/prospect into the system with full constellation populated.

- **Recurring email fetch** — scheduled associate, all 11 team members, runs continuously
- **Meeting backfill** — 30-day window, full team, both Apollo/Granola + Google Meet sources
- **Drive ingestion (standalone)** — Cam's proposal folder, the shared Kyle/Cam folder, customer-specific Drive folders. Standalone files become Documents linked to Companies. *Required for Alliance trace and proposal generation.*
- **Hydrate Alliance** — Company canonical (BT Core + Applied Epic + Dialpad in CustomerSystem), all Contacts (Christopher Cook, Brian Leftwich, ~5 others), all Emails (Kyle's full thread history), all Meetings (Jan-Feb discovery + Apr 8 renewal-wedge call), all Touchpoints synthesized, intelligence extracted, all Operations (renewals, customer service, new business intake), all Opportunities (renewal automation, etc.), Documents (v1 proposal, Craig's 30-page analysis), Proposal v2 in `drafting`, Phases for the renewal wedge approach.
- **Hydrate Arches** — same shape. Jeff Hamilton as primary contact; agency profile ($35M, personal-lines focused, building commercial team); pain points as Signals → Opportunities; Proposal in `drafting` for Inbox + Knowledge + Submission + Quote + Front Desk + Strategy Studio Associates.
- **Hydrate FoxQuilt** — same shape. Karim Jamal (CEO), Nick Goodfellow (VP Ops); Operations and Opportunities from the demo call; Proposal in `drafting`.
- **Hydrate the rest** — all 18 current customers + active prospects (Tillman, Rankin, O'Connor, Amynta, IIANC five via Pat Klene, etc.) — same shape, varying depth depending on data available.
- **Per-customer human enrichment via CLI** — Operations, Opportunities, CustomerSystem, BusinessRelationship, Documents that can't be auto-extracted. Craig + Cam as the operators.
- **Internal meetings handled** — Touchpoint scope=internal for daily syncs etc. Hydration includes them.
- **Constellation queryable** — for every customer, the full picture loads via CLI/UI in seconds.

**B2 done test.** Run `indemn company get <name> --include-related --depth 3` for any customer and get the complete picture.

#### B3 — Stage research + Playbook completion

With hydrated data, mine historical patterns to define each stage. The Playbook hydrates from observed reality, not from Kyle's PLAYBOOK-v2 doc as spec.

- **Analyze Touchpoints across customers per stage** — CONTACT, DISCOVERY, DEMO, PROPOSAL, NEGOTIATION, VERBAL/SIGNED. What does each stage actually look like in practice?
- **Resolve open entity-model questions** — Opportunity vs Problem; Document-as-artifact pattern for emails.
- **Produce Playbook records for all six stages** — `entry_signals`, `required_entities`, `expected_next_moves`, `artifact_intent` for each.
- **Refine the two stages we shook out** — DISCOVERY (from GR Little) and PROPOSAL (from Alliance) Playbooks, based on Kyle/Cam feedback.
- **12 sub-stages with archetype multi-select** — Kyle's Apr 24 ask. Surfaces from research naturally; we don't pre-design it. Probably implemented as Stage records gaining a `parent_stage` field for hierarchy + multi-select archetype field on Deal.

**B3 done test.** Six Playbook records exist, each grounded in observed historical patterns. The Artifact Generator can produce stage-appropriate artifacts for any stage.

#### B4 — Autonomous artifact production

Wire the Artifact Generator to run for every Touchpoint at every stage.

- **Artifact Generator associate built** — the role Claude plays in the traces. Reads `(Deal + recent Touchpoints + extracted intel + Playbook for Deal.stage + raw source content) → stage-appropriate draft`.
- **Watches every Touchpoint → processed** — produces draft when Touchpoint is fully extracted.
- **Drafts surface to OS queue** — for human review with one-click send. The OS queue IS the team's notification surface (no separate Slack/email layer for this — that's covered when the dashboard hooks up in Phase C).
- **Document-as-artifact pattern resolved** — drafted emails/recaps/proposals have a defined home in the entity graph (Email entity with `status: drafting`? Document with `mime_type: message/rfc822`? Resolved by B3.)
- **End-to-end autonomous** — every customer interaction produces a draft for human review. **This is when the customer system is achieving its own vision.**

**B4 done test.** A new meeting happens. Within minutes, a draft artifact appears in the OS queue for the appropriate human, ready to review and send.

---

### Phase C — Dashboarding (after autonomous)

**Purpose.** Surface the running system to the team in a usable form. The OS queue is the foundation; dashboards are how the team interacts with it.

- **Per-meeting view** — the GR Little artifact, but for every meeting (customer + internal), autogenerated and live. Shows entity trace, extracted intel, draft artifact, suggested next steps.
- **Per-customer page** — the constellation, navigable. Company hub → Contacts, Touchpoints, Operations, Opportunities, Proposal, Phases, Documents, Associates. Drill in any direction.
- **Sales pipeline list view (Kyle's V0)** — flat table of all customers/prospects with the columns Kyle keeps asking for: customer value, success path, days to next step, next step, owner. Hydrated with real pipeline data.
- **Push-to-talk to update** — voice agent with access to all entities; sales reps speak updates rather than typing. Kyle's Apr 24 ask.
- **All hooked up to the OS queue** — the dashboard IS the notification surface. New drafts, stale Deals, missed Commitments all surface in views the team is already looking at.

**C done test.** Cam opens the dashboard daily; sees customers needing proposals; reviews drafts in-line; sends with edits. George prep is 5 minutes not 20.

---

### Phase D — Adoption (light)

**Purpose.** The team uses the OS as their daily mode of work. Behavior change is real but low-ceremony.

- **Per-role onboarding** — Cam's flow, George's flow, Ganesha's flow, Peter's flow. Each gets the entry points + the daily rhythm they need.
- **Documentation of operational learnings** — captured continuously per Kyle's Apr 24 ask.
- **Light ceremony.** No formal "training program." More like "here's how you check on a customer" / "here's how you respond to a draft" / "here's how you log an interaction."

**D done test.** A new team member can be onboarded into the OS as their daily mode in a single sit-down session.

---

### Phase E — Evaluations + continuous improvement loop

**Purpose.** Verify autonomous AI work + drive iteration through evaluations as the feedback mechanism.

- **Foundation is in B1** — LangSmith on all harnesses, deep OTEL tracing, evaluations infrastructure ready.
- **Continuous use starts now** — evaluations on segments / specific associates are used as the feedback mechanism for tracing situations and improving the system. Whenever an associate behaves wrong, we run an evaluation on the segment to pinpoint why and refine.
- **Full eval coverage on all workflows is the future build** — every autonomous workflow has a rubric and a test set; quality is measured continuously.
- **Becomes how we trust autonomous work.** Combined with deep tracing, this is the verification layer — without it, we can't responsibly let AI run hands-off.

**E done test.** Every autonomous associate has a rubric + test set; evaluation results are visible in the dashboard; regressions caught automatically.

---

### Phase F — Slack ingestion *(MOVED to early Phase B per Apr 27 Alliance trace)*

**Purpose.** Add Slack as a Touchpoint source.

**Why moved up (was deferred):** the Apr 27 Alliance trace surfaced that key analytical artifacts and team-internal-thinking touchpoints already live in Slack and are foundational for the customer constellation:
- **Capability Document** (Craig's 30-page Alliance analysis) — Slack file in `#customer-implementation`
- **Apr 7-8 Retention Associate / compound outcome design thread** — Slack thread that produced the Decisions driving the v2 proposal
- **Apr 21 Cam mpdm packaging** — multi-party DM where the proposal-generation thread originated

Without Slack ingestion, ~half the touchpoints in Alliance's trace had to be manually reconstructed. Slack is foundational, not deferrable. New placement: **B2 sub-phase or its own B5**, not Phase F.

**Work needed:**
- Slack adapter (channels + DMs + MPDMs) — same pattern as Gmail / Google Workspace adapters
- Threads become Touchpoints — operating at thread level, not individual messages
- File attachments become Documents — extend Document.source enum with `slack_file_attachment`
- Sources include: customer-specific channels, tagged messages in general channels, MPDMs that reference a customer
- Backfill mechanism for historical Slack content (same as Bug #10 family)

---

## Continuous threads (run alongside everything)

These are not phases — they run continuously from the moment Phase B starts.

### OS bug convergence (active immediately)

**Critical operational discipline.** As soon as Phase B starts, fork parallel sessions to work bugs from `os-learnings.md`. Compute is not a constraint. The bug list converges to zero on what we choose to prioritize.

- **Bug list lives in `os-learnings.md`** — ranked by impact (critical/blocking → high → medium → open design questions). Source-of-truth detail in `artifacts/2026-04-24-os-bugs-and-shakeout.md`.
- **Top priorities** — Touchpoint Option B; entity-resolution kernel capability; Bug #29 (route eviction); Bug #23 (bulk-delete operator filters); Bug #22 (service-token forensics).
- **Forking pattern** — when something blocks customer-system progress, fork an isolated git worktree, fix the bug in the OS repo, merge back. The customer-system trace work doesn't block.
- **Fix-inline pattern** — when an OS fix is small and on the path of current work, do it inline. Don't fork unnecessarily.

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

- **Persistent-AI loops** (Walker → Peter → Ganesha → Kyle pattern that Kyle described Apr 24) — separate part of the system, future design. The Commitment + Task entities support it structurally; the wiring (associate that watches Commitments, notifies assignees, tracks fulfillment) is its own design problem to be tackled after B/C are in motion.

---

## References

| File | What's in it |
|---|---|
| `vision.md` | What we're building, why, the breakthrough as the lens. |
| `os-learnings.md` | Running register of OS bugs, capability gaps, design questions. |
| `INDEX.md` | Append-only project history. Status, Decisions, Open Questions, full Artifacts table. |
| `CLAUDE.md` | Cumulative thinking, journey, principles, start-of-session protocol. **Always read first.** |
| `artifacts/2026-04-25-session-handoff-and-roadmap.md` | The previous session's roadmap — superseded by this document but preserved for history. |
| `artifacts/2026-04-22-entity-model-brainstorm.md` | Entity field-level specs. |
| `artifacts/2026-04-22-entity-model-design-rationale.md` | Why the entity model is shaped this way. The Alliance test. |
| `artifacts/2026-04-23-playbook-as-entity-model.md` | The breakthrough articulated. |
| `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` | Latest design refinements (Apr 24). |
| `artifacts/2026-04-24-extractor-pipeline-gap.md` | Why the Extractor failed Apr 24; Option B is the chosen fix. |
| `artifacts/2026-04-24-extractor-procedure-and-requirements.md` | Procedure for autonomous Extractor + 9 OS capability gaps. |
| `artifacts/2026-04-24-information-flow-v2.html` | The Kyle-validated visual demo (open in browser). |
| `artifacts/2026-04-24-grlittle-followup-email-draft.md` | The GR Little artifact + entity-to-line mapping. |
| `artifacts/2026-04-24-os-bugs-and-shakeout.md` | Bug-level deep detail. |
| `/Users/home/Repositories/indemn-os/docs/white-paper.md` | The OS canonical vision. |
| `/Users/home/Repositories/indemn-os/CLAUDE.md` | The OS builder's manual. |

---

*This document is updated every session that moves the work forward. When state changes, update "Where we are now"; when a phase completes, mark it done; when scope shifts, append a Decision in `INDEX.md` first, then revise here.*
