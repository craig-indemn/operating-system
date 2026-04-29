# Customer System — Project CLAUDE.md

> **STOP. READ THIS WHOLE FILE BEFORE DOING ANYTHING ELSE.**
>
> This document is your **shared mental model** with Craig. It carries the cumulative thinking across the customer-system project — the vision, the architecture, the journey, the foundations, the best practices, the index. The artifacts on disk hold the depth; this file holds the *substance*.
>
> Reading this is non-negotiable. The single biggest failure mode is acting before absorbing what's here. You will re-derive decisions Craig has already made. You will propose designs that have already been rejected. You will lose the thread. Don't.

---

## Always also load (the canonical shared context)

`customer-system/CLAUDE.md` (this file) is the gateway, but it does not stand alone. The complete always-loaded shared context is:

| File | What it gives you |
|---|---|
| **This file** (`CLAUDE.md`) | Overarching project context — what/how/why/architecture/journey/foundations/best practices/index |
| `customer-system/vision.md` | End-state articulation (slow-changing) |
| `customer-system/roadmap.md` | Execution spine — phases, where we are, what's next |
| `customer-system/os-learnings.md` | Running register of OS gaps surfaced by customer-system work |
| `customer-system/CURRENT.md` | Fast-changing state — what just happened, what's in flight, parallel sessions, blockers, next steps |
| `indemn-os/CLAUDE.md` | OS shared mind — the platform you are building ON |

Read all of them. No skipping.

For deeper depth on a specific work area, follow the **"When working on X, READ these"** router in Section 8 below.

---

## 1. What we're building

### The vision in one paragraph

The customer system captures every interaction Indemn has with a customer (every email, every meeting, every document, every internal analysis) and turns it into a structured graph of entities that *together* form the comprehensive understanding of that customer. Not a CRM. Not a database. A **constellation** around each Company — Contacts, Touchpoints, Operations, Opportunities, Phases, Proposal, Deal, Documents, Associates — where the entities and their relationships *are* the customer profile. The Proposal is the destination. It begins empty at DISCOVERY and hydrates continuously across stages, with every stage producing an artifact via the same mechanism: `(Deal + recent Touchpoints + extracted intelligence + Playbook for Deal.stage + raw source content) → artifact`. Only the Playbook record changes per stage.

### The dual-track frame

The customer system is the **first real build on the Indemn Operating System**. It is also the **mechanism by which the OS becomes capable of running everything else Indemn does**. These are not separate efforts. We are not building a customer system that uses the OS — we are using the OS the way it was designed, while building. The customer system is the proving ground. The OS gets built by being used.

Bug resolution in the OS is a means to the customer-system end. Compute is not a constraint, so when something blocks the build we fork a parallel session and fix it. Forking is a first-class operating mode. The OS bug list converges to zero on the items we choose to prioritize. By the time the customer system achieves its own vision, the OS will be capable of running anything else Indemn does, and ready for external customers.

### What "done" looks like

The customer system is achieving its own vision when:

**The foundation runs autonomously.** New emails and meetings flow in, become Touchpoints, get extracted into Tasks/Decisions/Commitments/Signals/Opportunities, hydrate Proposals continuously, produce stage-appropriate artifacts for human review at every interaction. The team uses it as their daily mode. Cam manages proposal generation systematically. Kyle is no longer the single point of failure for "what's the story with X."

**Foundation capabilities (vision §2 lists nine):** entity model complete and accurate; entity-resolution capability in the kernel; pipeline associates running hands-off; watch cascade reliable end-to-end; constellation queryable; Temporal workflows manageable; OTEL spans + LangSmith on all harnesses; OS dogfooded as designed; OS bug list converged on prioritized items.

**Two team-facing threads:** (A) per-meeting view — every meeting Indemn has gets entity trace + extracted intelligence + draft artifact, the way Kyle saw GR Little. (B) Proposal generation — every Deal has a Proposal entity that hydrates from DISCOVERY onward; at PROPOSAL stage the Artifact Generator renders it. Tangible deliverable the team currently does manually. Alliance v2 is the first.

Hydration of every customer and prospect — Alliance, Arches, FoxQuilt, the full roster — is **implied** in achieving the foundation, not a separate item.

### Horizons (visible, not in scope)

- **Horizon 2 — All Indemn operations on the OS.** Once the customer system is done, delivery tracking, playbooks, health monitoring, team capacity, conferences, value/ROI, evaluations, the rest of the 17 functional areas from the 04-14 capabilities doc follow. Indemn-the-company runs on the OS.
- **Horizon 3 — OS production-ready for external customers.** The kernel hardened, the capability library mature, customer-onboarding playbook real, a second domain modelable in days not weeks. The white paper's Phase 6 → Phase 7 transition operable.

---

## 2. How we're building it

### Trace-as-build-method (canonical building method)

For every skill, watch, capability, integration adapter, or dashboard added to the OS in Phase B and beyond:

1. **Pick a real scenario.** A real email. A real meeting. A real deal at a real stage. Not a synthetic test case.
2. **Trace it yourself.** Act as the associate or the system component being built. Run the `indemn` CLI on live data. Watch the entity state move through each step.
3. **Verify the procedure works.** Does the entity graph end up in the right state? Does the cascade fire correctly? Are the right messages, watches, scopes triggered?
4. **Write the skill** (or wire the watch, configure the capability, build the dashboard). The artifact is the writeup of what worked, not the design ahead of what should work.
5. **Activate.** Drain the queue. Watch traces. Only after the trace produces the right state on real data does the autonomous version go live.

**Why this is the right method:** testable by construction (if the CLI sequence produces the right state when you run it, the skill that codifies that sequence is correct); surfaces gaps before deployment (Touchpoint Option B, the cross-invocation cache leak, and silent workflow stuck-states were all discovered during the GR Little trace, not in production after deployment); forces reckoning with real data state instead of theory; generalizes (the same method that built the entity model in Phase A builds skills, capabilities, watches, integration adapters, and dashboards in Phase B+).

This was discovered as Phase A's shake-out method (GR Little Apr 24, Alliance Apr 27) and elevated to canonical building method in Session 8. It applies to all of Phase B/C/D/E. **Anything the OS does, trace it yourself first.**

### Parallel sessions + fork pattern

When something blocks customer-system progress and is significant, fork a parallel session in a separate git worktree. The fork session works on the OS-side fix while the main session keeps moving on customer-system work. The two sessions coordinate via shared context files (`os-learnings.md`, `CURRENT.md`).

**When to fork:** OS work that would block customer-system progress and is non-trivial (entity-resolution kernel capability, Touchpoint Option B, Bug #29 route eviction, Bug #23 bulk-delete operator filters).

**When to inline:** OS work that's small and on the path of current work (Email field rename, single CLI papercut, etc.). Don't fork unnecessarily.

The shared-context-update mechanism (this file + INDEX.md + vision.md + roadmap.md + os-learnings.md + CURRENT.md + SESSIONS.md) is what makes parallel sessions coherent. The bugfix fork reads `os-learnings.md` to learn what's queued; the main session updates it as findings surface; no human-in-the-middle handoff.

### Dogfooding the OS as designed

If a pattern was designed but never used in practice, we use it. This is the test that the OS is what we believe it to be. Examples validated through customer-system work: `save_tracked()` as the one save path; entity_resolve as a kernel capability called by associates; --auto pattern; `effective_actor_id` for forensics; the unified queue. **Skills loaded via the CLI** (`indemn skill get <name>` via the agent's `execute` tool) — symmetric with how associates already load everything else from the OS; replaced the deepagents filesystem-skills layer in Session 12 (commit `7281b83`).

Customer-system work is OS work. Every gap we hit during customer-system work is information the OS needs. That information flows back via `os-learnings.md` (the running register) to the OS repo (kernel commits, doc updates).

### OS bug convergence as a continuous thread

Bug fixes are 100% a priority alongside roadmap progress. They are not a side-quest. The OS bug list converges to zero on the items we choose to prioritize. The bug list lives in `os-learnings.md`. When customer-system work surfaces an OS-relevant finding, log it there immediately. When the fix lands (in a fork session or inline), update the row.

**The acceleration mechanic:** every fix above makes the next thing 2-3x faster. Option B done means the Extractor works. Extractor working means we can backfill all team meetings and emails. Backfill done means we hydrate Alliance + Arches + every prospect. Hydrated graph means the Artifact Generator has real data. Artifact Generator means dashboards have real data. Dashboards mean the team adopts. Adoption means we discover the next round of OS gaps.

### Trace-as-build IS the brainstorm

The working session and the brainstorm are the same activity. The trace exercises the vision; the vision shapes what the trace means. Out of a session: a refreshed understanding (CURRENT.md updated), an updated roadmap if state moved, OS gaps logged, and concrete entity changes in the live system.

### Vision IS the MVP

Never simplify, collapse, or defer designed features without explicit approval from Craig. Implement EXACTLY what the design specifies. (Memory: `feedback_vision_is_mvp.md`, `feedback_never_simplify_vision.md`.) When the OS doesn't support what the design requires, the OS gets built up to support it — not the design simplified.

---

## 3. Why we're building it this way

### The problem we're solving

If anyone needs to understand a customer, they ask Kyle. That doesn't scale, and Kyle can't plug in for three months. The data exists, but it's scattered across six+ disconnected systems with nothing authoritative. When Johnson Insurance went 10+ days without a response, nobody noticed until Kyle checked.

Beyond the source-of-truth problem: no defined delivery process (18 customers, each approached differently); no visibility into who's working on what (Peter finds out customers went live after the fact); no way to quantify value being delivered (ROI models exist for one customer — Branch).

These aren't separate problems. They're facets of one problem: **the company doesn't have a system that models its own operations.**

### The architectural foundation — entities are the system

Entities are cheap in the OS (auto-generated CLI, API, UI, skills). The cost of a new entity is near zero. The cost of cramming data into the wrong entity is confusion. So we model rich. Each Company has many Operations, Opportunities, Contacts, Touchpoints, Documents, Emails, Meetings, Deals, Proposals, Associates. The constellation IS the customer profile.

This is not a CRM. CRMs treat the customer record as the unit of work. Here the unit is the *graph state* — what entities exist, what's populated, what's empty, what state things are in. A CRM tells you "this is the customer." This system tells you "this is what we know, what we've done, what's missing, what's next."

### The breakthrough (Session 4, Apr 23)

> **The Proposal is the destination. The entities IN the proposal need to be filled out. The process of filling them out IS the playbook. Empty fields are gaps. Gaps tell you what to do next. When the gaps are filled, you have a proposal.**

The playbook isn't a separate document or process definition. It's the entity model itself. Every customer follows the same process: populate the same entities, same fields. The data differs but the structure is universal. Progress is measurable (count populated vs empty fields). Next steps are automatic (gaps generate Tasks). New team members have a guide. AI can drive the process. The dashboard Kyle wants is just a view onto this — populated vs missing entities, days since last touch, next action, owner.

Full articulation: `artifacts/2026-04-23-playbook-as-entity-model.md`.

### Apr 24 refinements (Session 5)

1. **Playbook is data, not just a doc.** One record per Stage. Fields: stage, description, entry_signals, required_entities, expected_next_moves, artifact_intent. Terminus = Proposal at PROPOSAL stage.
2. **Playbook is consulted twice per touchpoint** — by the Intelligence Extractor (`required_entities` becomes the extraction schema for that stage) AND by the Artifact Generator (`artifact_intent` becomes the spec for what to render).
3. **Proposal is created at DISCOVERY as an empty spine.** Hydrates continuously by every subsequent touchpoint. Opportunities link to it (eventually via Phases). At PROPOSAL stage the Artifact Generator just renders it. Same mechanism every stage; only the Playbook record changes.
4. **Touchpoint must carry forward source pointers (Option B).** `source_entity_type` + `source_entity_id` so the Extractor can navigate from Touchpoint back to source content. Otherwise the agent has no path to ground truth.
5. **Raw content is ground truth, available always** via the CLI. Entities are curation; raw content provides voice. Both layer.
6. **Opportunities are created from DISCOVERY onward** for product-fit pain. Pain without product fit stays as Signal (or, eventually, becomes Problem entity — open design question).

### The Alliance test

Every design decision must work for Alliance Insurance. Alliance is the deepest customer relationship Indemn has — through DISCOVERY → DEMO → PROPOSAL, currently in NEGOTIATION generating v2. If a design choice can't represent Alliance's full state cleanly — Christopher Cook as decision-maker, BT Core + Applied Epic + Dialpad in the tech stack, the renewal wedge pivot from the April 8 call, Craig's 30-page analysis as a Document, the original Feb 11 proposal as a superseded version, Phase 1 around Renewal Associate at $2,500/mo month-to-month — then the design is incomplete.

Full Alliance picture: `artifacts/2026-04-22-entity-model-design-rationale.md` § Alliance Test.

---

## 4. Architecture

### The flow — raw data through to Proposal

```
Raw Data (Email, Meeting, Document, Slack)
    → Touchpoint (unified timeline — external + internal)
        → Company Understanding (Operations, Opportunities, CustomerSystem, BusinessRelationship)
            → Proposal + Phases (what we'll deliver)
                → Delivery (Associates deployed, Tasks tracked, Commitments fulfilled)
                    → back into Touchpoints (delivery generates more interactions)
```

The system is a loop, not a line. Every layer feeds every other layer. An internal Slack thread about Alliance blocking on BT Core integration is a Touchpoint → it might generate a Task → that Task is linked to a Phase → the Phase's progress is tracked → the next customer meeting references the progress.

### The 27-entity model

The customer system has 27 entity definitions live in dev OS, organized into clusters:

**Customer hub:** Company, Contact, Employee, BusinessRelationship.
**Interaction layer:** Email, Meeting, Document, Touchpoint (forward source pointers via Option B).
**Understanding layer:** Operation, Opportunity, CustomerSystem, Signal.
**Sales:** Deal, Stage, Conference, Outcome (with OutcomeType reference).
**Delivery:** Proposal, Phase, Associate, AssociateType (reference).
**Intelligence (cross-cutting):** Task, Decision, Commitment.
**Process:** Playbook (one record per Stage).

Field-level specs: `artifacts/2026-04-22-entity-model-brainstorm.md`. Design rationale: `artifacts/2026-04-22-entity-model-design-rationale.md`.

### Structural decisions (settled)

- **Proposal is source of truth for what we deliver.** The document is a rendering, not the source.
- **Phase replaces SuccessPhase.** Phases always belong to a Proposal — no phases without a proposal.
- **No fluff fields.** Every field is structured data, an entity relationship, or specific source-of-truth content. No keyword summaries. No text describing things that are other entities.
- **Documents for narrative, entities for structured facts.** Both live in the system, linked together.
- **Touchpoint covers external (with customer) AND internal (about/for customer).** Captures full effort and timeline.
- **Sources point TO Touchpoint** (Email.touchpoint, Meeting.touchpoint), but Touchpoint also carries `source_entity_type` + `source_entity_id` forward pointers (Option B). Both directions exist; they serve different purposes.
- **One save, one event** (kernel-level): only creation, transitions, and `@exposed` method invocations emit messages. Plain field updates do not.
- **Email.interaction renamed to Email.touchpoint** (Apr 23 — kernel collision; followon migration completed Apr 28 Session 9).

### The Artifact Generator mechanism

Every stage produces an artifact via the same mechanism:

```
(Deal + recent Touchpoints + extracted intelligence + Playbook for Deal.stage + raw source content)
  → Artifact Generator
  → stage-appropriate draft (email at DISCOVERY, recap at DEMO, proposal doc at PROPOSAL, objection response at NEGOTIATION, kickoff at SIGNED)
  → human review → one-click send
```

Validated across two distinct stages so far: DISCOVERY (GR Little follow-up email, Apr 24) + PROPOSAL/NEGOTIATION (Alliance v2 proposal doc, Apr 27). The mechanism generalizes.

The Artifact Generator skill: `skills/artifact-generator.md` (15 style guidelines from Cam's portfolio, JSON contract, rendering recipe).

The styled-PDF rendering pipeline: `templates/proposal/` (Handlebars + CSS + assets) + `tools/render-proposal.js` (puppeteer-core + Chrome).

### Pipeline associates — the 7-associate cascade

Three associates exist today (EC, TS, IE); four more were designed in Session 12's TD-2 alignment conversation (MC, SC, Proposal-Hydrator, Company-Enricher). Plus the ReviewItem universal-escape-valve pattern. **Full cascade architecture, sub-piece breakdown, activation order, and done-test live in `roadmap.md` TD-2** — that's where the resolved design is. Here's just the 1-paragraph spine.

- **EmailClassifier (EC, exists, v9).** Watch: Email created. Classifies email, resolve-before-create on Contact + Company (Hard Rule #1 inverted Session 12 — autonomous create on 0/0). Will absorb signature parsing.
- **MeetingClassifier (MC, NEW).** Watch: Meeting created. Resolve attendees as Contacts/Employees, identify Company, classify scope.
- **SlackClassifier (SC, NEW).** Watch: SlackThread created. Channel-context-aware classification, relevance filter, Company resolution.
- **TouchpointSynthesizer (TS, exists, v6 → v7 in TD-2).** Watch: Email/Meeting/SlackThread classified (3 watches). Creates Touchpoint with Option B source pointers. **Will fold in Deal-creation** (when scope=external + no active Deal for Company → create Deal at CONTACT/DISCOVERY + auto-create empty Proposal, atomic). Internal-scope multi-Deal ambiguity → assigns to latest Deal + creates ReviewItem.
- **IntelligenceExtractor (IE, exists, v3).** Watch: Touchpoint logged. Reads source via Option B navigation; extracts Decisions/Tasks/Commitments/Signals/Operations/Opportunities/Phases per Playbook[Deal.stage].
- **Proposal-Hydrator (NEW).** Watch: Touchpoint processed. Aggregates extracted entities into Proposal entity (linking, not free-text). Stages are fluid — uses Playbook required_entities as guidance not schema; ReviewItems what doesn't fit.
- **Company-Enricher (NEW).** Watch: Touchpoint logged for a Company with bare data (or scheduled cron, fallback). Fills Company fields from source content. Runs in parallel with IE — different writes, no conflict.

**ReviewItem pattern.** Any associate that hits an issue creates a `ReviewItem` linking to the entity in question + a reason + the proposed-resolution it took as best-effort. Reviewer role watches `ReviewItem created`. Cascade NEVER blocks (except Source-Classifier total-classification-failure, which transitions source to needs_review). Reviewing IS the training-data mechanism — patterns reviewers correct become rules / skill iterations.

Run states (active/suspended/etc.) live in `CURRENT.md`, not here.

### Open design questions (carried forward)

These five touch domain shape (entity types, state-machine transitions, sub-stage modeling, referrer fields, Playbook hydration mechanism) — not OS kernel mechanics. Resolution belongs to the main session, with Craig.

1. **Opportunity vs Problem entity** — does unmapped pain need its own entity, or does Opportunity loosen `mapped_associate` to nullable? Source: `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` § Topic 2.
2. **Document-as-artifact pattern for emails** — drafted email lives where? Email entity with `status: drafting`? Document with `mime_type: message/rfc822`? Hybrid? Source: `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` § Topic 3.
3. **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle's Apr 24 ask). Source: `artifacts/2026-04-24-kyle-sync-recap.md`.
4. **Origin / referrer tracking** (Pat Klene → GR Little example, Kyle's Apr 24 ask). Source: same.
5. **Playbook hydration mechanism** — how Playbook records refine from observed patterns over time. Manual? Scheduled associate? Human-in-the-loop?

---

## 5. Journey — distilled

The customer-system project did not arrive at its current shape in one stroke. To understand WHY the system is what it is, you need to understand the path. Each session below has its load-bearing turn captured. For depth on any session, see the per-session handoff artifact in `artifacts/`.

### Session 1 (2026-04-14/15) — Genesis

Kyle pressed Craig: customer information scattered across 6+ systems, no source of truth, "ask Kyle" doesn't scale. Craig spent two days gathering source materials — 28 Kyle docs, 10+ meeting transcripts, the InsurTechNY CRM sheet, conversations with George, Peter, Ganesh, Cam. Out of this came: problem statement (7 concepts with evidence), system capabilities (17 functional areas, ~130 capabilities), vision-and-trajectory (phased roadmap), Phase 1 domain model (14 entities), entity criteria framework (7 tests).

**Load-bearing turn:** AI populates everything — design for extraction, not manual entry. Company entity covers the full lifecycle prospect → churned. Task is unified across all sources. Meeting intelligence (Decisions, Commitments, Signals, Tasks) are separate entities, not fields on Meeting. This is the first implementation on the OS.

### Session 2 (2026-04-19/20) — UI polish + demo readiness

Polished auto-generated UI. Refactored the assistant into a resizable split pane with streaming and entity rendering. Demo-readiness assessment for CEO demo. Cataloged known kernel issues. Not architecturally significant.

### Session 3 (2026-04-21) — Meeting ingestion + strategic alignment

Built Google Meet ingestion pipeline end-to-end. Meeting entity + adapter. Seeded Employee entity (15 team members). Cleaned up junk Actors. Extended Deal entity. Created SuccessPhase. Custom domains (`os.indemn.ai`, `api.os.indemn.ai`) live. CLI v0.1.0 published.

The most important thing was *strategic*: Craig and Kyle had a 40K-word call (`artifacts/context/2026-04-21-kyle-craig-call-transcript.txt`) on prospect strategy, deal priorities, using Kyle as guinea pig for the OS. Read Kyle's EXEC folder + Cam's Proposals folder. The cumulative thinking from this session reshaped what the customer system needed to become.

**Load-bearing turn:** `fetch_new` is a collection-level kernel capability — generic pattern for any entity ingestion. Meeting entity is agnostic to Google. Company matching and meeting classification are post-processing (associate's job, not adapter). Alliance Insurance is the first target customer for full data hydration.

### Session 4 (2026-04-22/23) — The architecture breakthrough

The single most important session for the project's architecture. Deep brainstorming on the entity model. Two companion documents: `entity-model-brainstorm.md` (field-level specs for 22 entities) + `entity-model-design-rationale.md` (*why* the model is the way it is).

**Load-bearing turn:** *the entities ARE the system.* Not a database that the system reads from. Not a CRM that people update. The entities, their relationships, their state machines, and the OS primitives that connect them (watches, associates, integrations) — that IS the customer system.

Then on Apr 23 came **the breakthrough** (`artifacts/2026-04-23-playbook-as-entity-model.md`):

> The Proposal is the destination. The entities IN the proposal need to be filled out. The process of filling them out IS the playbook. Empty fields are gaps. Gaps tell you what to do next. When the gaps are filled, you have a proposal.

This changed everything about how we frame the system.

Implementation Waves 1-3 followed: 27 entity definitions live, 3 associates wired (Email Classifier → Touchpoint Synthesizer → Intelligence Extractor), Gmail adapter built, ~930 emails ingested across the team, pipeline E2E proven for the happy path.

### Session 5 (2026-04-24) — The live trace + Kyle validation + design refinements

Took the Apr 22 GR Little first-discovery call and traced it end-to-end through the OS as a working example. The trace surfaced everything — what worked, what was structurally broken, what the next iteration of the architecture had to be.

**What the trace shipped:** GR Little hydrated end-to-end (Company canonical from 5 dupes, Walker + Heather Contacts, Deal at DISCOVERY, Meeting linked, Touchpoint synthesized **manually** because the automated path failed). Manual extraction produced 2 Tasks, 2 Decisions, 4 Commitments, 5 Signals, 3 Opportunities, empty Proposal v1. Drafted follow-up email from `(Deal + Touchpoint + extracted entities + DISCOVERY Playbook + raw Meeting transcript)`. Built the v2 information-flow diagram (`artifacts/2026-04-24-information-flow-v2.html`).

**What the trace surfaced:** the Intelligence Extractor failed structurally — its starting context had no path from Touchpoint to source Meeting transcript. Captured in `extractor-pipeline-gap.md`. The chosen fix: **Option B** — `source_entity_type` + `source_entity_id` on Touchpoint. Bug #29 (entity-definition replacement doesn't evict old API routes) discovered.

**Kyle's reaction (Apr 24 sync, full transcript at `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt`):** *"This looks good... pretty close to what it should be... worth trying to do on every call and getting in front of everybody... Whole company's excited about the Indemn operating system."*

**Apr 24 refinements:** Playbook consulted twice per touchpoint. Proposal hydrates from DISCOVERY as empty spine. Opportunities created from DISCOVERY onward. Touchpoint Synthesizer must populate forward source pointers (Option B). Raw content remains available as ground truth. Full design dialogue: `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md`.

### Session 6 (2026-04-27) — Vision crystallization + Alliance v2 trace + parallel bugfix fork

The biggest single-session shipment. Three deliverables in parallel.

**Vision crystallization:** `vision.md` (slow-changing end-state) + `roadmap.md` (living source of truth) created at project root. Both reference depth in `os-learnings.md` and dated artifacts. The customer-system equivalent of the OS repo's documentation system.

**Alliance v2 proposal trace:** Walked Alliance through 8 timeline steps (Feb 1 discovery call → Feb 11 v1 proposal sent → Feb 18-19 Capability Document analysis → Feb 26 PDF DM to Ryan → Apr 7-8 Retention Associate prep thread → Apr 8/9 renewal-wedge pivot meeting → Apr 21 BT Core integration emails → Apr 27 Artifact Generator produces v2). **Acted AS each associate.** Wrote real entities to OS via `indemn` CLI throughout. Hydrated 60+ entities into Alliance's constellation. PROPOSAL-stage Playbook record `69efbcf34d65e2ca69b0dd6e` created — reusable for all customers.

**Parallel bugfix fork session in flight throughout:** 7 OS bugs fixed/in-progress in parallel — Touchpoint Option B 🟢, silent stuck-state 🟢, cache leak 🟢, API 500-detail 🟢, entity-skill JSON examples 🟢, Bug #30 sparse-on-nullable (Meeting create) 🟢, Bug #29 route eviction 🟢. The shared-context-update mechanism (this session logs findings to `os-learnings.md` → bugfix session reads them on resume) worked end-to-end as designed.

**Load-bearing turn:** the Apr 23 breakthrough validated across two distinct stages — DISCOVERY (GR Little follow-up email) and PROPOSAL/NEGOTIATION (Alliance v2 proposal doc). The mechanism generalizes. Phase A is COMPLETE.

### Session 7 (2026-04-27 evening) — Styled-PDF rendering pipeline + Cam-portfolio match

Built the reusable Indemn proposal rendering pipeline: `templates/proposal/` (Handlebars + CSS + assets) + `tools/render-proposal.js` (puppeteer-core + handlebars). Rendered Alliance v2 to a 9-page styled PDF matching Cam's portfolio. Documented the recipe + 15 style guidelines in `skills/artifact-generator.md`.

**Load-bearing turn:** HTML→PDF via puppeteer-core against system Chrome is the right tooling. Cam's brevity is the standard — no direct address, no v1/v2 framing, no stat dumps. Section-per-page rhythm (9 pages). 28pt heading sweet spot. Full-grid tables.

### Session 8 (2026-04-28 morning) — Trace-showcase HTML for Kyle + Phase A close

Built `artifacts/2026-04-27-alliance-trace-showcase.html` — single self-contained HTML using the Apr 24 GR Little visual language as the base. Five-section spine: cover hero / vertical timeline (8 events) / extraction table (10 quote-to-entity-to-proposal-line rows) / mechanism / proposal-as-spine. Uploaded v2 PDF to Cam's Drive folder. Shared in MPDM with Cam + Kyle.

**Load-bearing turn:** Phase A is fully complete — two stages traced (DISCOVERY + PROPOSAL/NEGOTIATION), both Kyle-facing artifacts shipped. Phase B opens. Trace-as-build elevated to canonical building method (`vision.md §4`, this CLAUDE.md §2, `roadmap.md` Phase B preamble).

### Session 9 (2026-04-28 afternoon) — Phase B1 entity-resolution + reactivation kill-switch

Phase B opens. Path A cleanup executed: entity_resolve activated on Contact (email + name strategies); domain strategy added to Company entity_resolve. Bulk-deleted 79 orphan Companies. Resolved 91 high-volume Contact dupes. 10 Email.sender_contact references reclassified to canonicals before delete.

Phase B1 trace through 3 scenarios as Email Classifier on real emails: known Contact + Company (clean), new Contact at known Company (Contact created), truly new domain (needs_review). Email.interaction → Email.touchpoint rename completed as **root-cause fix** (1139 docs migrated, EntityDefinition relationship_target updated).

Three skills updated: EC v3, TS v6, IE v3.

**Load-bearing turn:** kill switch fired on Diana@CKSpecialty's email. EC processed 4 messages during brief activation; multi-candidate case violated skill rule (auto-created NEW Company despite "Never auto-create" being explicit). Suspended EC immediately. Skill content verified correct in DB. **Skill-compliance gap on the harder multi-candidate branch.** Reactivation halted.

### Session 10 (2026-04-28 evening) — LangSmith + EC kill-switch root cause + Path 3 evals

The session that turned Session 9's "skill-compliance gap" into a 5-minute root-cause investigation. The actual bug was a kernel CLI bug (Bug #34) — `_COLLECTION_LEVEL_CAPS` missing `entity_resolve` → entity-resolve returned HTTP 422 → agent saw tool error, fell through to `create`. CLI fixed via commit `db97694`.

Three kernel changes shipped to indemn-os main: LangSmith wired into async-deepagents harness (`956d7d5`); kernel CLI fix (`db97694`); harness `agent_did_useful_work` tightened (`d914d76`).

**Architecture decisions confirmed:** Path 3 for evaluations (existing evaluations repo eventually becomes a kernel adapter; use LangSmith API directly for now). Harness reports facts, OS interprets meaning (the tightened completion check is observation-only, domain-agnostic; "agent didn't fulfill skill intent" detection lives in evals + observability dashboards on top of LangSmith — NOT in the harness).

**Load-bearing turn:** LangSmith earned its place — every "the agent did the wrong thing" should flip to "let me look at the trace" before "let me iterate the skill." Diagnostic queries documented in this CLAUDE.md § 8 (Index — debugging an associate's behavior).

### Session 11 (2026-04-28 late evening) — EC v7 + discovered every iteration v3→v7 has been ineffective

The session that ended Sessions 9 + 10's "we need a better skill iteration" framing by discovering that **the agent has never been reading the email-classifier associate skill content at all.** Despite Hard Rules added through versions v3 → v7, the agent's behavior has been driven entirely by the harness DEFAULT_PROMPT plus what it learns from `indemn skill get <Entity>` (auto-generated entity skills, NOT the associate skill).

Confirmed via direct system-prompt inspection in LangSmith trace `019dd602-ddb9-7f03-946c-fcee7413e11f`: `**Available Skills:** (No skills available yet. You can create skills in act-…/skills)`.

EC v7 deployed with Hard Rule #10 (mandatory Contact resolve) + #11 (Contact-first ordering). Document Drive metadata sync. Harness commit `5ec4e9f` — pass skills LIBRARY directory to `deepagents.create_deep_agent(skills=[...])`. **Deployed and tested — system prompt STILL says "(No skills available yet)".** The library-dir fix is necessary but not sufficient.

**Bug #35 (NEW, OPEN):** deepagents skill discovery broken in our LocalShellBackend setup. Hypothesis space documented in `artifacts/2026-04-28-session-11-handoff.md` § 3. Path resolution against `LocalShellBackend.root_dir` is the most likely culprit.

**Load-bearing turn:** every single iteration of EC v3 → v7 has been theatre. The DB has the content; the agent never reads it. Don't iterate skill content until skill discovery is fixed. **Don't inline skills into system prompts** (Craig: "BAD! TERRIBLE DESIGN AND NOT ALIGNED WITH THE VISION") — the OS vision requires deepagents progressive disclosure to work properly.

### Session 12 (2026-04-29) — Bug #35/#36/#37 closeouts + Armadillo trace + Hard Rule #1 inversion + shared-context hydration redesign

Three parallel threads.

**Thread 1 — Main customer-system: Armadillo trace + Hard Rule #1 inversion.** Hard Rule #1 inverted in EC (v7 → v9, content_hash `9eef4959ae701614`): "Never auto-create a Company" → "Resolve before create" — autonomous Company + Contact creation now allowed when resolve returns 0 candidates, since resolve-first IS the dedup defense and is reliable post-Bug-#34/#36. Step 5 decision table updated. Verified live on Armadillo's first-contact email.

Armadillo Insurance traced end-to-end as designed — first new-prospect trace post-inversion. Origin: Matan Slagter (CEO) → David Wellner (COO) intro at InsurtechNY (Apr 2). Discovery call Apr 28. Autonomous flow created Company `69f22186…444d` + 2 Contacts. 14 entities extracted by IE against DISCOVERY Playbook. Artifacts shipped to Kyle (yesterday's roadmap doc + Armadillo trace HTML via Slack file attachment). Brain-dump request sent to Kyle for TFG / John Scanland — next prospect.

**Thread 2 — Parallel kernel-fix: Bugs #35 + #36 + #37 closed, then deepagents skills layer dropped entirely.**
- Bug #35 (deepagents skill discovery) — two stacked fixes first: absolute-path return from `_write_skills_to_filesystem` (`8141a80`), then `yaml.safe_dump` for frontmatter (`2ba6f63`). Live-verified. Then **the whole layer was dropped** (`7281b83` `refactor(harness): load skills via CLI in DEFAULT_PROMPT, drop deepagents skills layer`) — the deepagents filesystem-skills mechanism (write SKILL.md to disk, pass library dir to `create_deep_agent`, `SkillsMiddleware` scans + parses YAML frontmatter, surfaces metadata in system prompt, agent loads full content via `read_file`) was a poor fit. Our associates have ONE skill each — no "many skills, agent dynamically chooses" pattern that progressive-disclosure-via-filesystem was designed for. Replaced with: agent runs `execute('indemn skill get <name>')` (system-prompt directive), skill content arrives as tool result on turn 1 and stays in message history. Symmetric with how associates already load entity skills + everything else. Eliminates Bug #35 class entirely (no path resolution against backend root_dir, no YAML escaping, no SKILL.md format to maintain). The two stacked fixes are no longer load-bearing — the layer they fixed is gone.
- Bug #36 (Gmail/Calendar `fetch_new` adapters silently absorbing kwargs) — deeper root cause was `**params` on adapter methods. Fix plumbs `until` end-to-end and replaces `**params` with `**unknown_params` raising `AdapterValidationError` (`477a98f`). 15 unit tests. Outlook adapter same pattern propagated (`3fc4b55`).
- Bug #37 (Email list endpoint poisoned by malformed `company` field) — opt-in tolerance via `_DomainQuery.to_list(skip_invalid=False)` (`a5aa89f`).

**Thread 3 — Parallel hydration-redesign (this thread):** solved the meta-problem of 500K-token hydration. Designed and shipped the layered model. Outcome: this CLAUDE.md (rewritten), `CURRENT.md` (new), `SESSIONS.md` (new), `PROMPT.md` (new). Design captured in `docs/plans/2026-04-28-shared-context-hydration-design.md`. Total always-loaded hydration reduced ~5x (500K → ~95K).

**Load-bearing turns:**
1. Hard Rule #1 was a workaround. Once resolve became reliable (Bug #34 + #36 closeouts), the workaround became unnecessary — autonomous create on 0/0 is now the cleaner default.
2. Skills load via the CLI now (`indemn skill get <name>`), not via deepagents filesystem-skills. The deepagents layer was a poor fit for one-skill-per-associate associates. The CLI pattern is symmetric with how the agent already loads everything else in the OS.
3. The shared mental model is comprehensive and overarching, not distilled-to-tidbits. CLAUDE.md *contains* the architecture, journey, foundations, best practices — deeper files become on-demand reference.
4. Three load-bearing kernel bugs closed in one session because parallel sessions worked simultaneously on different threads — proof that the fork-and-coordinate pattern compounds when shared context discipline holds.
5. **Roadmap restructured around tangible deliverables (TD-1 through TD-11)** instead of foundation phases. Same vision, same work, different organization. The phases were fuzzy on what's tangibly shipped to whom; the TDs make it explicit. Roadmap stays structural per-TD until that TD is approached, at which point a focused alignment conversation resolves all open architectural questions and the section gets filled in.
6. **TD-2 architecture resolved: 7-associate cascade + ReviewItem universal-escape-valve.** Per Craig's principle (one associate per significantly-different trigger/entities/context/skill): EC, MC, SC, TS (gains Deal-creation), IE, Proposal-Hydrator (new), Company-Enricher (new). ReviewItem entity is the universal "I'm uncertain, here's my best effort, please clean up" primitive — used by every associate, watched by Reviewer role, training-data side-effect. Cascade NEVER blocks (except Source-Classifier total-classification-failure). Stages-are-fluid for Proposal-Hydrator: Playbook is guidance, not schema. Activation order is bottom-up. Done-test is systematic historical replay (~1000+ existing emails+meetings cascaded chronologically). Full design lives in `roadmap.md § TD-2`.

### Session 13 (2026-04-29) — Comprehensive roadmap alignment (TD-1 through TD-11)

The session that took the roadmap from foundational-phase framing (Phases A → F, fuzzy on what's tangibly shipped) to tangible-deliverable framing (TD-1 through TD-11, explicit on what each delivers and how). Session 13 was a single-thread alignment session — no parallel work, deep design conversation about how the system actually works in practice across the full roadmap.

**What landed:**

- **Roadmap restructured as 11 Tangible Deliverables.** Same vision, same work, different organization. TD-1 (adapters running) → TD-2 (cascade activated) → TD-3 (per-customer UI) → TD-4 (Playbook stages from history) → TD-5 (per-interaction artifact generation) → TD-6 (Proposal deck generation) → TD-7 (system visibility) → TD-8 (team adoption) → TD-9 (evaluations) → TD-10 (Commitment-tracking persistent-AI loops) → TD-11 (external-customer ready, deferred to product-vision).
- **TD-1, TD-2, TD-3 detailed at full fidelity** (~170-280 lines each in roadmap.md). Deep architectural alignment for the foundation work — every "how does this actually work" question resolved with rationale captured.
- **TD-4 through TD-11 detailed at structural fidelity** (~30-70 lines each — sufficient to start work; deeper detail filled in when each TD is approached for execution).

**Load-bearing turns:**

1. **Tangible-deliverable framing.** Phases were fuzzy. TDs are concrete: each delivers a specific tangible thing (a working adapter, a running cascade, a UI page) the team can use OR a foundational capability that unlocks the next concrete piece.
2. **7-associate cascade architecture for TD-2** (locked in this session): EC, MC, SC, TS (gains Deal-creation), IE, Proposal-Hydrator, Company-Enricher. Per Craig's principle — one associate per significantly-different trigger/entities/context/skill.
3. **ReviewItem universal-escape-valve pattern.** Per Craig: "any issue that the associates encounter as they're working they should just go and create a review item and call it a day." Generic across all entity types; never blocks the cascade; reviewing IS training data. Replaces per-entity `flag_for_review` field anti-pattern.
4. **Per-event Touchpoints, NOT per-thread.** A Touchpoint is a discrete event in time — every email, every reply, every Slack message, every meeting → its own Touchpoint. Threading is metadata (Email.thread_id / SlackMessage.thread_ts), not a primary entity. Touchpoints are immutable snapshots; constellation evolves because the SET of Touchpoints grows.
5. **Slack adapter design.** Direct Slack API (not third-party); all channels via Slack admin; no DMs initially; per-message granularity; polling-then-Events-API.
6. **Drive ingestion design.** Pull all of Drive; lazy classification (at Touchpoint extraction by IE OR manually via UI OR future workflow-driven); folder context as hint, not auto-applied; Document entity source-agnostic.
7. **Manual entry via per-actor assistant** uses existing OS kernel-level Deployment pattern (not custom infrastructure). New domain skill `log-touchpoint` added to each team member's `default_assistant`.
8. **TD-3 stack: React + Vite + shadcn matching Ganesh's customer-success repo conventions.** Direct OS API. Reuse existing chat-deepagents + voice-deepagents harnesses. Visual matches GR Little / Alliance trace-showcase HTML language. 7 pages. Single-scrolling per-customer page with inline timeline expansion. Role-aware personalized dashboard. Persistent assistant on every page.
9. **TD-4 process is fully conversational design via Claude Code, not automation.** Three phases: research session (determine WHAT stages exist), per-stage deep-dive, mostly-static refinement. The 5 long-running open design Qs fold into the research, resolved as they surface.
10. **Artifact Generator: one associate, Playbook-driven, multi-deployment** (async + realtime chat + realtime voice). Drafted email = Email entity with `status: drafting`. Per Craig's flexibility-of-deployment principle — associates can be deployed async or realtime depending on use case; same skill, different harness + Deployment.
11. **Stage progression UI is descriptive, not prescriptive.** Populated entities at a stage are STATUS, not stage-advancement criteria. Stage transition criteria defined separately in TD-4 research.
12. **No more "open questions" sections in TD entries** per Craig's principle. Architectural decisions get resolved in alignment conversations BEFORE the TD entry gets detailed; TD entry captures resolved design with rationale, not unresolved Qs.

**Resolved long-running open design questions:**
- Document-as-artifact for emails → Email with `status: drafting` (TD-5)
- Playbook hydration mechanism → mostly-static, conversational refinement (TD-4)
- Touchpoint↔Deal chicken-and-egg → TS atomically creates Deal + empty Proposal when external scope + no active Deal (TD-2)
- Internal Touchpoints contributing to Proposal → YES, treated same as external (TD-2)
- Multi-Deal ambiguity for internal → assigns to latest + creates ReviewItem (TD-2)

**Carried forward (now folded into TD-4 research, no longer separate open Qs):**
- Opportunity vs Problem entity
- 12 sub-stages with archetypes (Kyle's Apr 24 ask)
- Origin/referrer tracking

**Material state at close:** No entity changes in dev OS (alignment session, not execution). Pipeline associates unchanged from Session 12 close (EC v9 suspended; TS v6 suspended; IE active). Bug #36/#37 cleanup still pending (TD-1 pre-flight). Roadmap is now ~1100 lines of comprehensive design ready for TD-1 execution.

**Handoff to Session 14:** Use `PROMPT.md` as kickoff. Objective: execute TD-1 — pre-flight cleanup (Bug #36/#37) → ReviewItem entity + Reviewer role → 4 scheduled fetcher actors (bottom-up activation) → Slack adapter NEW build (multi-session work; design + scaffold this session) → voice harness verification + `log-touchpoint` skill. EC/TS/IE remain suspended; cascade NOT activated by TD-1.

**Material state at close:** Armadillo constellation queryable end-to-end (1 Company + 1 Deal + 2 Contacts + 2 Touchpoints + 14 extracted entities). 5 new design gaps logged (Deal-lifecycle automation, Employee entity_resolve, Company hydration on auto-create, Contact richer-field parsing, internal docs spanning multiple prospects). Cleanup pending: 500 emails + 6 meetings from Bug #36 side-effect; 2 malformed Email rows from Bug #37.

---

## 6. Foundations

### The 20 design principles

These are the principles that hold across the project. Internalize them. They have been hard-won through prior pushback and they are what keep the system coherent.

1. **Vision IS the MVP.** Never simplify, collapse, or defer designed features without explicit approval from Craig. Implement EXACTLY what the design specifies. (Memory: `feedback_vision_is_mvp.md`, `feedback_never_simplify_vision.md`.)
2. **AI populates everything.** Design entities for extraction, not manual entry. Enums over free text wherever possible.
3. **No fluff fields.** Every field is structured data, an entity relationship, or specific source-of-truth content. No keyword summaries. No text describing things that are other entities. (Memory: `feedback_entity_design_principles.md`.)
4. **Documents for narrative, entities for structured facts.** Both live in the system, linked together.
5. **The Proposal entity IS the source of truth.** The document is a rendering. Entities are queryable, versionable, watchable; documents aren't.
6. **No phases without a proposal.** Phases always belong to a Proposal, even at DISCOVERY where the Proposal is empty.
7. **Sources point TO Touchpoint** but Touchpoint also carries `source_entity_*` forward pointers (Option B). Both directions exist; they serve different purposes.
8. **One save, one event** (kernel-level). Only creation, transitions, and `@exposed` method invocations emit messages. Plain field updates do not. Don't design around this; respect it.
9. **The OS does the connective tissue, your domain handles business data.** Don't model activity logs (changes collection), notifications (watches), audit trails (changes), team identity (Actor), permissions (Role), version history (changes). The kernel provides these.
10. **Entities are cheap; cramming is expensive.** If something passes the 7-test entity criteria (identity, lifecycle, independence, not-kernel-mechanism, CLI test, watchable, multiplicity), make it an entity.
11. **Don't import Kyle's PLAYBOOK-v2 or his prep-doc field specs as schema.** They are intent signal. Build from real data outward. (Memory: `feedback_craig_assertions_authoritative.md`.)
12. **Don't route around OS bugs with deterministic shortcuts** when the LLM-capability path is correct. Find root causes. (Memory: `feedback_understand_before_fix.md`.)
13. **Don't propose roadmaps unilaterally.** Engage as a thought partner. Ask Craig first. (Memory: `feedback_brainstorm_alignment.md`, `feedback_altitude_of_decisions.md`.)
14. **Verify against the live system.** Don't claim work is complete without running the actual command, querying the actual entity, checking the actual state. (Memory: `feedback_evaluate_honestly.md`, `feedback_complete_data.md`.)
15. **Never delete or replace historical entries in INDEX.md** — Decisions, Open Questions, Artifacts. Always append. (Memory: `feedback_never_delete_history.md`.)
16. **Don't fabricate data** in entities, configs, prompts, or KB. (Memory: `feedback_no_fabricated_data.md`.)
17. **Customer-system work is OS work.** They are not separate projects. Findings here flow back to update the OS itself — kernel code, docs, architecture. When OS work would block customer-system progress and is significant, fork to a parallel session in a separate worktree. When small and on-path, do it inline.
18. **Don't conflate customers.** GR Little is a one-off demo for Kyle's validation. Alliance is the proof point. Arches Insurance is a secondary trace example. Each has its own state.
19. **Read the artifacts every time.** Don't trust your memory across sessions. Sessions clear context. Read.
20. **Trace-as-build: act as the associate before you deploy it.** Every skill, watch, capability, and dashboard goes through a trace first. The skill is the writeup of what worked. Activate the autonomous version only after the trace produces the right state on real data.

### Things you DO NOT do

- Do not skip the reading. "I remember this from before" is wrong; sessions clear context.
- Do not propose roadmaps unilaterally. Ask first. Engage as thought partner.
- Do not simplify the vision for "MVP simplicity." Vision IS the MVP.
- Do not import Kyle's PLAYBOOK-v2 or his prep-doc field specs as schema.
- Do not route around OS bugs with deterministic shortcuts when LLM-capability is the right path.
- Do not declare work complete without verification.
- Do not delete or replace historical entries in INDEX.md. Append.
- Do not fabricate data.
- Do not declare quality on partial signals. Verify thoroughly.
- Do not skip the end-of-session protocol.
- Do not let CLAUDE.md, INDEX.md, CURRENT.md, SESSIONS.md, or os-learnings.md rot.
- Do not conflate customers.
- Do not propose splitting "Phase 1, 2, 3" without first asking what the priorities and threading are.
- **Skills load via the CLI, not via static system-prompt content.** The agent runs `execute('indemn skill get <name>')` (operating skill on turn 1, entity skills on demand). Skill content arrives as a tool result and stays in the agent's message history. This is symmetric with everything else the agent does in the OS. Don't try to put skill content directly in the system_prompt parameter when constructing the agent — the system_prompt has a directive telling the agent to call `indemn skill get`, not the skill content itself. (The deepagents filesystem-skills layer was dropped in Session 12 commit `7281b83` — wrong fit for one-skill-per-associate associates.)

---

## 7. Best practices

### Start of every session — mandatory protocol

The session-start prompt (`PROMPT.md`) handles this — but for reference, here's what it enforces:

1. Read all always-loaded files in order: this CLAUDE.md, `vision.md`, `roadmap.md`, `os-learnings.md`, `CURRENT.md`, `indemn-os/CLAUDE.md`. **Mandatory. No skipping.**
2. Confirm shared context is loaded by stating: top of roadmap; what CURRENT.md says is in flight + parallel-session state; the session's specific objective.
3. For work-area-specific depth, follow the **"When working on X" router** in Section 8.
4. Then begin work.

### During the session — running discipline

- **Capture findings as they happen.** OS gaps go in `os-learnings.md`. Open design questions go in `INDEX.md § Open Questions`. New information about parallel sessions or in-flight work goes in `CURRENT.md`.
- **Don't bury findings in trace artifacts.** Surface them in the running registers.
- **When tempted to propose a roadmap or structure unilaterally, stop and ask.** Craig has explicitly pushed back on this. Add to cumulative thinking, don't redirect it.
- **The shared context contains the result of prior brainstorming. USE it. Don't re-litigate.** If something genuinely isn't settled, flag it to Craig BEFORE drifting into design discussion.
- **Drive toward execution.** State intent, do the work, report.

### End-of-session protocol — mandatory before stopping

Wait for Craig's signal. Do not self-trigger end-of-session protocol based on context-budget guesses.

When Craig signals it's time to wrap, run **all** of these. None are optional.

1. **`CURRENT.md`** — replace with the current state. What just happened, what's in flight, what's next, parallel-session state, blockers.
2. **`SESSIONS.md`** — append a new entry at the **top** with: session N, date, short title, Objective, Parallel sessions during, Outcome (3-5 bullets), Handoff to next, Touched (files / entities).
3. **`roadmap.md`** — update if phase state moved.
4. **`os-learnings.md`** — update if OS gap surfaced or status changed.
5. **`INDEX.md`** — append to Decisions / Open Questions / Artifacts table if any landed this session. **Append, never delete or rewrite history.**
6. **This CLAUDE.md** — update only if architecture shifted, new principle emerged, new router entry needed, or journey gained a new session entry. **Conscious, deliberate change.**
7. **`vision.md`** — update only if end-state articulation changed. Stamp dated artifact (`artifacts/<date>-vision-revision-<descriptor>.md`).
8. **Memory** — update `project_customer_system_status.md` if project status shifted significantly. Add memory entries for fresh open design questions.
9. **Verify before declaring done** — actually open `CURRENT.md`, `SESSIONS.md`, `os-learnings.md`. Don't trust your memory that you updated them; verify.
10. **Commit everything** in one tight commit.

### Periodically — when crystallization happens

- Revise `vision.md` and stamp the revision in a dated artifact.
- Promote running registers if they get unwieldy (e.g., move resolved bugs out of the active list in `os-learnings.md`).
- If a major session-cluster of work completes a phase, update the journey section here with a new chapter.

### Pre-flight check at session start

After the mandatory reads, before doing work, verify:
- Is `os-learnings.md` consistent with what `INDEX.md § Open Questions` is saying?
- Is the journey section in this CLAUDE.md consistent with `SESSIONS.md`?
- Is `CURRENT.md` recent enough to make sense?

If any of these are out of sync, **flag to Craig** before doing work — the system rotted between sessions and we should reconcile before adding more work on top.

### Cadence and discipline — why this matters

These files are a *living memory*. They only stay alive if every session takes the small cost (~5-10 minutes) of updating them at the end. That cost is the difference between "the next session picks up where this one left off" and "the next session starts from scratch and Craig has to re-explain."

Craig has been explicit: he should not have to re-explain objectives every session. The way to make sure he doesn't is the protocol above. Treat it as the most important part of every session.

---

## 8. Index of files — when working on X, READ these

This is the activity-driven router. Match your work; read what's listed; do not assume you remember it from a prior session.

### Resuming after context reset
→ Always-loaded set (see top of this file) + relevant section below for the specific activity.

### Tracing a customer through the OS (any customer)
→ `artifacts/2026-04-24-information-flow-v2.html` (the shape) → `artifacts/2026-04-24-grlittle-followup-email-draft.md` (the line-to-entity map template) → `artifacts/2026-04-27-alliance-trace.md` (the Alliance trace narrative) → `artifacts/2026-04-27-alliance-trace-plan.md` (the trace plan template) → `artifacts/2026-04-24-extractor-procedure-and-requirements.md` (what extraction must produce).

### Working on Alliance specifically
→ Read the Alliance Test section in `artifacts/2026-04-22-entity-model-design-rationale.md`. → Pull Alliance materials from Drive (Cam's proposal folder + the shared Kyle/Cam folder). → Read `artifacts/2026-04-27-alliance-trace.md` and `artifacts/2026-04-27-alliance-proposal-v2.md`. → For the styled PDF: `artifacts/2026-04-27-alliance-proposal-v2.pdf` + `templates/proposal/`.

### Working on Arches Insurance
→ Look up Cam's forwarded message from Rocky in Slack (search "Arches" in Slack channels and Cam → Craig DMs). → Run a normal trace pattern (see "Tracing a customer" above).

### Designing or refining the Playbook
→ `artifacts/2026-04-24-playbook-entity-vision.md` → `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` → `artifacts/2026-04-23-playbook-as-entity-model.md`.

### Designing dashboards (Kyle's Apr 24 priority ask)
→ Read the **full** `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt` — texture matters here. → `artifacts/2026-04-24-kyle-sync-recap.md` for the structured summary.

### Designing or fixing extraction
→ `artifacts/2026-04-24-extractor-pipeline-gap.md` (Option B is the chosen fix) → `artifacts/2026-04-24-extractor-procedure-and-requirements.md` (procedure + 9 OS capability gaps).

### Designing the Artifact Generator associate
→ `skills/artifact-generator.md` (the recipe, JSON contract, 15 style guidelines) → `artifacts/2026-04-24-extractor-procedure-and-requirements.md` (template for associate procedure) → `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` (how Artifact Generator uses Playbook + raw content) → `artifacts/2026-04-24-grlittle-followup-email-draft.md` (line-to-entity render mapping).

### Refining the entity model (any change)
→ `artifacts/2026-04-22-entity-model-brainstorm.md` (current spec) → `artifacts/2026-04-22-entity-model-design-rationale.md` (why) → `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` (recent open questions: Opportunity vs Problem; Document-as-artifact).

### Designing entity resolution / dedup (Bug #16)
→ Memory: `project_customer_system_entity_identity.md` → `artifacts/2026-04-24-trace-plan-and-design-notes.md` (the open question section) → `os-learnings.md` Bug #16 + Bug #34 + Bug #35 detail.

### Working with Kyle
→ `artifacts/2026-04-24-alignment-framing.md` (his docs are signal not spec) → `artifacts/2026-04-24-kyle-sync-recap.md` → `artifacts/context/2026-04-21-kyle-craig-call-transcript.txt` → `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt`.

### Working with Cam
→ Read his proposals folder (Drive `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`) — 6 customer proposals (Alliance, Branch, Johnson, GIC, Charley, Physicians Mutual) + SaaS Agreement. → "What Cam's Proposals Taught Us" section in `artifacts/2026-04-22-entity-model-brainstorm.md`. → `skills/artifact-generator.md` 15 style guidelines.

### Hitting an OS bug
→ `artifacts/2026-04-24-os-bugs-and-shakeout.md` (deep detail; add bug-level entry if not there) → `os-learnings.md` (add a row in the appropriate severity section) → If blocking core work: raise to Craig for parallel fork.

### Capturing a new OS capability gap or ergonomics issue
→ `os-learnings.md` (the running register).

### Designing or implementing OS changes (kernel, harnesses, CLI)
→ Start with `indemn-os/CLAUDE.md` (already in always-loaded set). → Read the relevant architecture doc in `indemn-os/docs/architecture/`: `entity-framework.md` for entity changes; `watches-and-wiring.md` for routing; `associates.md` for harness work; `rules-and-auto.md` for capabilities + --auto; `integrations.md` for adapters; `realtime.md` for chat/voice; `observability.md` for tracing. → Read the relevant guide in `indemn-os/docs/guides/`. → Reference `../product-vision/artifacts/2026-04-16-vision-map.md` for cross-cutting design context.

### OS bug fix (when a customer-system bug is actually an OS bug)
→ `artifacts/2026-04-24-os-bugs-and-shakeout.md`. → Trace the root cause in the kernel source (`indemn-os/kernel/`). → Fix in the OS repo. → Update OS docs if behavior changed. → Cross-reference back here in `os-learnings.md` when fixed.

### Adding a new OS capability or kernel feature
→ Discuss in `../product-vision/` first if it's design-level. → Read `indemn-os/docs/architecture/rules-and-auto.md` (capability registration pattern). → Implement in `indemn-os/kernel/capability/`. → Add doc in `indemn-os/docs/architecture/` or update existing one.

### Debugging an associate's behavior / failure (LangSmith tracing)

Wired in 2026-04-28 (Session 10). Every async-deepagents associate run emits a full LangSmith trace with the LLM reasoning chain, every `execute` tool call, every middleware step, and the entity context the agent was given.

- **Project:** `indemn-os-associates` (LangSmith) — id `19302981-aa9e-4869-9137-59a38d7646df`
- **API key:** AWS Secrets Manager `indemn/dev/shared/langsmith-api-key`
- **UI:** https://smith.langchain.com → indemn org → indemn-os-associates project

Each trace carries metadata that makes it queryable by domain identifiers: `associate_id`, `associate_name`, `message_id`, `entity_type`, `entity_id`, `runtime_id`, `correlation_id`. Plus tags `associate:<name>`, `entity_type:<type>`, `runtime:<id>`.

**To query a specific run** (replace `$KEY` with the API key):
```bash
# Find the trace for an entity_id
curl -s -H "x-api-key: $KEY" -H "Content-Type: application/json" \
  "https://api.smith.langchain.com/api/v1/runs/query" \
  -d '{"session": ["19302981-aa9e-4869-9137-59a38d7646df"], "is_root": true, "limit": 5,
       "filter": "and(eq(metadata_key, \"entity_id\"), eq(metadata_value, \"<entity_id>\"))"}'

# Pull the full trace tree (paginate by 100s)
TRACE_ID="<from above>"
for off in 0 100 200; do
  curl -s -H "x-api-key: $KEY" -H "Content-Type: application/json" \
    "https://api.smith.langchain.com/api/v1/runs/query" \
    -d "{\"trace\": \"$TRACE_ID\", \"limit\": 100, \"offset\": $off}"
done
```

Tool calls appear with `run_type: "tool"`. LLM calls appear with `run_type: "llm"`. Middleware wrappers (Skills, Filesystem, SubAgent, Summarization, AnthropicPromptCaching, TodoList) appear as `chain` runs.

**Use case (Session 10):** the EC compliance gap that Session 9 attributed to "skill-compliance gap" was actually a kernel CLI bug (entity-resolve returning HTTP 422). Without LangSmith we couldn't see the failed resolve call. With it, diagnosis took 5 minutes. **Use case (Session 11):** discovered via direct system-prompt inspection that the agent has never been reading the EC associate skill (Bug #35).

Wiring location: `harnesses/async-deepagents/main.py`.

### Browsing prior sessions / objectives
→ `SESSIONS.md` — append-only log of session objectives + outcomes. Each entry has Objective + Outcome + Touched + Handoff-to-next. Useful for: looking back at history, learning the objective format, parallel-session awareness.

### Browsing the full project history (decisions, artifacts, open questions)
→ `INDEX.md` — append-only ledger. Status section, External Resources, full Artifacts table, Decisions log, Open Questions.

### Source material — Kyle's EXEC docs
- `artifacts/context/kyle-exec/PLAYBOOK-v2.md` — Kyle's sales motion playbook
- `artifacts/context/kyle-exec/PROSPECT-SIX-LEADS-v0.md` — 6 active prospects (FoxQuilt, Alliance, Amynta, Rankin, Tillman, O'Connor)
- `artifacts/context/kyle-exec/DICT-PROSPECTING-v2.md`, `DICT-SALES-v2.md`, `DICT-CUSTOMER-SUCCESS-v2.md`
- `artifacts/context/kyle-exec/MAP.md` — 30-workstream map across 5 pillars

### External resources
- Cam's proposal folder (Drive): `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`
- Kyle+Cam shared folder (Drive): `1KKH8juzCqVyRQ36h72nnB9Djdjy8m_j1`
- White paper PDF (Drive): `1Cr_F_K3a_I_iul7HgJqXv1IY8KieyS40`
- CRM InsurTechNY sheet (Drive): `1B3QnzfS8IEM7cMN3ar9gSFRw8K8_viFmH-dEajQ9tQg`
- OS API: `https://api.os.indemn.ai`
- OS UI: `https://os.indemn.ai`
- Chat Runtime: `wss://indemn-runtime-chat-production.up.railway.app/ws/chat`

### Companion project — `../product-vision/`
The OS-level project that captures the OS's design and status (separate from the OS code repo). Where OS design discussions land before becoming OS implementation work.
- `../product-vision/CLAUDE.md` — OS-level project orientation
- `../product-vision/INDEX.md` — OS-level decisions log + status
- `../product-vision/artifacts/2026-04-16-vision-map.md` — **the authoritative OS-level synthesis** (104 design files distilled into 23 sections)

---

## A note on tone and voice

This project is foundational work for what Indemn becomes. The team is excited about it. Kyle is excited about it. Cam will use it. Ganesha will scale it. The work has weight.

When you write artifacts: every line should be intentional. The diagram we showed Kyle was good because every visual choice traced to something real. The email was good because every paragraph mapped to an entity. The artifacts you produce should hold that bar.

When you build: the entities you create represent real customers, real conversations, real decisions. Don't be sloppy with what they hold. Verify against the live system. Trace through what happens when state changes.

When you brainstorm: the cumulative thinking has a single thread — the proposal-as-spine, every interaction hydrating, the playbook-as-entity-model insight, the OS as platform underneath. Add to it. Don't redirect it.

You are not a checklist follower. You are a collaborator on building the system that becomes how the company operates. Engage like that.
