# Customer System — Project CLAUDE.md

> **STOP. READ THIS WHOLE FILE BEFORE DOING ANYTHING ELSE.**
>
> This document carries the cumulative thinking of this project across many sessions. The vision, the journey, the insights, the principles. The artifacts on disk hold the depth; this file holds the *spirit*. Reading this is non-negotiable — not because it's a rule, but because everything that follows depends on you having internalized what's here.
>
> The single biggest failure mode is acting before you've absorbed the cumulative thinking. You will re-derive decisions Craig has already made. You will propose roadmaps already pushed back on. You will lose the thread. Don't.
>
> **Critical framing:** the customer system and the Indemn Operating System are not separate efforts. The customer system is the *first build* on the OS. Every bug we hit is an OS bug. Every gap we find is an OS gap. Every learning here flows back into the OS itself — the OS repo, its docs, its architecture. You cannot build the customer system competently without deeply understanding the OS. The OS code lives at `/Users/home/Repositories/indemn-os/`. The OS docs live at `/Users/home/Repositories/indemn-os/docs/`. **Read them.** See "The OS — what it is and how to internalize it" section below.
>
> Sister-document: `INDEX.md` is the living history — decisions log, status updates, open questions, every artifact ever produced. Read it after this file. Treat it as the project's running ledger.

---

## The vision — what we're building, in our own words

We're building a system that captures every interaction Indemn has with a customer (every email, every meeting, every document, every internal analysis) and turns it into a structured graph of entities that *together* form the comprehensive understanding of that customer. Not a CRM. Not a database. A **constellation** around each Company — Contacts, Touchpoints, Operations, Opportunities, Phases, Proposal, Deal, Documents, Associates — where the entities and their relationships *are* the customer profile.

The Proposal entity is the culmination. It begins **empty at DISCOVERY** and hydrates continuously across stages. Every stage of the sales journey produces an artifact — a follow-up email at DISCOVERY, a demo recap at DEMO, an objection response at NEGOTIATION, **the rendered Proposal document at PROPOSAL stage**. Every artifact is the same mechanism: `(Deal + recent Touchpoints + extracted entities + raw source content + Playbook for Deal.stage) → artifact`. Only the Playbook record changes per stage. The system that drafts a follow-up email is the same system that renders the final Proposal — just at a different stage.

The customer system is the **first real domain built on the Indemn Operating System**. Building it is building the OS. Every bug we find is an OS bug. Every capability we need is an OS capability. The OS gets better as we build the customer system, and we ship the customer system because the OS is good enough.

This is what Kyle asked for in his original framing: *"a source of truth updated daily, interactable by AI systems and humans."* This is what Cam wants: *"a system that completely controls the process — on an automated basis or by a tickle, it reaches out and says hey, you haven't talked to so-and-so in a week."* This is what George needs: *"reduce pre-meeting review from 20 minutes to 5."* The same system answers all three.

---

## The unifying frame — internalize before doing anything

**Everything we are working on is part of the same system.**

- Proposal generation is not a different thing from email artifact generation. It is the same mechanism at a different stage.
- The dashboards Kyle wants are not a separate project. They are a view onto the entity graph this system is hydrating.
- The persistent-AI workflow Kyle described — "Walker said yes → Peter scrapes the site → Ganesha reviews → Kyle shares" — is not a new feature. It is Commitment entities + watches + role-based notifications, all primitives we already have.
- The OS bugs we find are not distractions. They are constraints that, once removed, accelerate every subsequent piece of work. Each bug fixed makes the next thing 2-3x faster. **That's the acceleration mechanic.**
- Every quick win we ship — a generated email, a hydrated customer page, a fixed bug — is a puzzle piece in the overall vision. Not a standalone task.
- The team will use the OS in production via the CLI. Everything we build here is the foundation for that.

When you find yourself thinking about a "feature" or a "phase" without immediately seeing how it ties into the proposal-generation-as-the-spine vision, you are not aligned. Stop and re-read this section.

---

## How we got here — the journey across sessions

This project did not arrive at its current shape in one stroke. It was built across many sessions, each adding a layer. To understand *why* the system is what it is, you need to understand the path.

### Session 1 (2026-04-14/15) — Genesis

Kyle pressed Craig: customer information is scattered (Pipeline API, Airtable, Sheets, Drive's 43 customer subfolders, Meeting Intelligence DB, Slack), no system is authoritative, "ask Kyle" doesn't scale, and Kyle can't plug in for three months. Craig spent two days gathering source materials — 28 Kyle docs, 10+ meeting transcripts, the InsurTechNY CRM sheet, conversations with George, Peter, Ganesh, Cam.

Out of this came the foundational artifacts:
- `2026-04-14-problem-statement.md` — the 7 concepts of the problem with evidence
- `2026-04-14-system-capabilities.md` — 17 functional areas, ~130 capabilities, attributed to who said what
- `2026-04-14-vision-and-trajectory.md` — the phased roadmap, shared with Kyle and Cam
- `2026-04-14-phase-1-domain-model.md` — 14 entities (Phase 1 spec)
- `2026-04-14-domain-model-thinking.md` — the 7-test entity criteria framework

**Key decisions that still hold:**
- AI populates everything — design for extraction, not manual entry.
- Company entity covers the full lifecycle from prospect through churned.
- Task is unified across all sources (meetings, implementations, manual) — one entity, one queue.
- Meeting intelligence (Decisions, Commitments, Signals, Tasks) are separate entities, not fields on Meeting.
- This is the first implementation on the Operating System — proves and refines the OS domain modeling process.

The vision-and-trajectory doc framed Phase 1-5 (Source of Truth → Delivery Tracking → Visibility & Intelligence → Pipeline & Conference → Value, ROI & Scaling). It's the document we still draw inspiration from for refresh.

### Session 2 (2026-04-19/20) — UI polish + demo readiness

Polished the auto-generated UI. Refactored the assistant into a resizable split pane with streaming and entity rendering. Did a demo-readiness assessment for a CEO demo. Cataloged known kernel issues. Not architecturally significant but moved the system toward usability.

### Session 3 (2026-04-21) — Meeting ingestion + strategic alignment

Built the Google Meet ingestion pipeline end-to-end. Meeting entity + adapter that captures conference records, structured transcripts (speaker+timestamp), Gemini smart notes, recordings, Calendar attendees. Seeded the Employee entity (15 team members linked to Actors). Cleaned up junk Actors. Extended the Deal entity. Created SuccessPhase. Custom domains (`os.indemn.ai`, `api.os.indemn.ai`) live. CLI v0.1.0 published.

The most important thing from this session was *strategic*: Craig and Kyle had a 40K-word call (`context/2026-04-21-kyle-craig-call-transcript.txt`) on prospect strategy, deal priorities, and using Kyle as guinea pig for the OS. Read Kyle's EXEC folder (PLAYBOOK-v2, dictionaries, MAP, prospect-six-leads). Read Cam's proposals folder (6 customer proposals — Alliance, Branch, Johnson, GIC, Charley, Physicians Mutual). The cumulative thinking from this session reshaped what the customer system needed to become.

**Key decisions:**
- `fetch_new` is a collection-level kernel capability — generic pattern for any entity ingestion.
- Meeting entity is agnostic to Google — adapter maps Meet/Calendar/Drive data to Meeting fields.
- Company matching and meeting classification are post-processing (associate's job, not adapter).
- Deal entity extended with `deal_id`, `next_step`, `next_step_owner`, `use_case`, `proposal_candidate`.
- Alliance Insurance is the first target customer for full data hydration.

### Session 4 (2026-04-22/23) — The architecture breakthrough

The single most important session for the project's architecture. Craig brainstormed deeply with Claude on the entity model. Two companion documents came out:
- `2026-04-22-entity-model-brainstorm.md` — field-level specs for 22 entities
- `2026-04-22-entity-model-design-rationale.md` — *why* the model is the way it is

**The core insight from the design rationale:** *the entities ARE the system.* Not a database that the system reads from. Not a CRM that people update. The entities, their relationships, their state machines, and the OS primitives that connect them (watches, associates, integrations) — that IS the customer system. When you look at a Company, you don't see a record with 50 fields. You see a hub surrounded by Operations (what they do), Opportunities (where the gaps are), Contacts (who we talk to), Touchpoints (every interaction), Documents (every file), Emails, Meetings, Deals, Proposals, Associates. The Company entity itself stays lean. The depth comes from the relationships.

**Key entities introduced:** Email, Document, Touchpoint (originally "Interaction" — renamed Apr 23 due to kernel collision), Operation, Opportunity, Proposal, Phase. AssociateDeployment renamed to Associate.

**Key decisions:**
- The Proposal entity IS the source of truth for what we deliver. The document is a rendering, not the source.
- Phase replaces SuccessPhase. Phases always live on Proposal — no phases without a proposal.
- No fluff fields. Every field is structured data, an entity relationship, or specific source-of-truth content. No keyword summaries. No text describing things that are other entities.
- Documents for narrative, entities for structured facts — both live in the system, linked together.
- Touchpoint covers external (with customer) AND internal (about/for customer) — captures full effort and timeline.
- Sources point TO Touchpoint (Email.touchpoint, Meeting.touchpoint), not the reverse — scales as new source types are added.

**Then on Apr 23 came the breakthrough — `2026-04-23-playbook-as-entity-model.md`:**

> **The Proposal is the destination. The entities IN the proposal need to be filled out. The process of filling them out IS the playbook.**
>
> The playbook isn't a separate document or process definition. It's the entity model itself. Empty fields are gaps. Gaps tell you what to do next. When the gaps are filled, you have a proposal.

This changed everything about how we frame the system. Every customer follows the same process: populate the same entities, same fields. The data differs but the structure is universal. Progress is measurable (count populated vs empty fields). Next steps are automatic (gaps generate Tasks). New team members have a guide. AI can drive the process.

Implementation Waves 1-3 followed: 27 entity definitions live, 3 associates wired (Email Classifier → Touchpoint Synthesizer → Intelligence Extractor), Gmail adapter built, ~930 emails ingested across the team, pipeline E2E proven for the happy path. Several infrastructure bugs fixed along the way (queue processor, runtime token, async harness skill loading and heartbeating).

### Session 5 (2026-04-24) — The live trace + Kyle validation + design refinements

The session this current orientation document was born out of. We took the Apr 22 GR Little first-discovery call and traced it end-to-end through the OS as a working example. The trace surfaced everything — what worked, what was structurally broken, what we'd need to fix, and what the next iteration of the architecture had to be.

**What we built:**
- GR Little hydrated end-to-end (Company canonical from 5 dupes, Walker + Heather Contacts, Deal at DISCOVERY, Meeting linked, Touchpoint synthesized **manually** because the automated path failed).
- Manual extraction produced 2 Tasks, 2 Decisions, 4 Commitments, 5 Signals, 3 Opportunities, empty Proposal v1.
- Drafted follow-up email from `(Deal + Touchpoint + extracted entities + DISCOVERY Playbook + raw Meeting transcript)`.
- Built the v2 information-flow diagram (`artifacts/2026-04-24-information-flow-v2.html`) — email hero + temporal timeline + extraction quote→entity→email-line table + mechanism table + Proposal spine growth.

**What we found:**
- The Intelligence Extractor failed structurally — its starting context had no path from Touchpoint to source Meeting transcript. The `--include-related` flag returned `_related: []`. The agent improvised, hit a `--filter` option that doesn't exist, found a cached transcript from a *different* prior agent invocation (cross-invocation cache leak), gave up silently. The workflow never marked the message complete or failed. **This was an information-access asymmetry, not an LLM-capability problem.** Captured in `2026-04-24-extractor-pipeline-gap.md`.
- The chosen fix: **Option B** — add `source_entity_type` + `source_entity_id` fields to Touchpoint; Touchpoint Synthesizer populates them on create; Extractor uses them to navigate. Small schema change, unblocks autonomous extraction.
- Bug #29 discovered: entity-definition replacement doesn't evict old API routes (FastAPI `include_router` appends, doesn't replace). Required redeploy to apply our new Playbook entity definition.

**What Kyle saw and said (Apr 24 sync, full transcript at `context/2026-04-24-kyle-craig-sync-transcript.txt`):**
- *"This looks good. Maybe a little too long, but it's pretty close to what it should be."*
- *"This is super cool... worth trying to do on every call and getting in front of everybody."*
- *"This is something we should be doing... almost automatically... Just trying to socialize it. Everything's a v0."*
- *"Whole company's excited about the Indemn operating system."*

**What Kyle wants next (priority order):** V0 sales dashboard with minimum-viable columns (customer value / success path / days to next step / next step / owner) + push-to-talk for sales reps to update; per-meeting artifact generation automated; 12 sub-stages instead of 6 (multi-select for archetypes, qualification built in); origin/referrer tracking (the Pat Klene → GR Little example); persistent-AI Commitment loop ("Walker said yes → notify Peter, Peter scrapes, Ganesha reviews, Kyle shares"); observatory daily/weekly reports.

**Design refinements aligned in conversation with Craig (`2026-04-24-design-dialogue-playbook-artifact-proposal.md`):**

1. **Playbook is consulted twice per touchpoint.** Once by the Intelligence Extractor — `Playbook[Deal.stage].required_entities` becomes the extraction schema for that stage. Different stages produce different extraction categories. Once by the Artifact Generator — `Playbook[Deal.stage].artifact_intent` becomes the spec for what to render.

2. **Proposal is created at DISCOVERY as an empty spine.** Hydrated continuously by every subsequent touchpoint. Opportunities link to it (eventually via Phases). At PROPOSAL stage the Artifact Generator just renders it. Same mechanism every stage; only the Playbook record changes.

3. **Opportunities are created from DISCOVERY onward** for pain points that map to an AssociateType. Pain points without product fit stay as Signals (or, eventually, become Problem entities — open question).

4. **Touchpoint Synthesizer must populate forward source pointers.** Option B from the extractor-pipeline-gap artifact.

5. **Raw Meeting/Email content remains available to associates as ground truth** via the CLI. Don't formalize as a separate pattern — it's already there. Touchpoint summary + extracted entities are *curation*; raw content provides *voice* and texture and ephemeral personal references (the "congrats on the twins" / "Kitty Hawk" passages in the GR Little email came directly from the transcript, not from any structured entity).

### Session 6 (2026-04-27) — Vision crystallization + Alliance v2 trace + parallel bugfix fork

The biggest single-session shipment so far. Three deliverables landed in parallel.

**Vision crystallization (morning):** Long brainstorm with Craig produced `vision.md` (slow-changing end-state articulation) + `roadmap.md` (living source of truth, Phases A→F + continuous threads + out-of-scope) at project root. Both are lean spine files referencing depth in `os-learnings.md` and dated artifacts. Established the customer-system equivalent of the OS repo's documentation system.

**Alliance v2 proposal trace (afternoon):** Walked Alliance Insurance through 8 timeline steps (Feb 1 discovery call → Feb 11 v1 proposal sent → Feb 18-19 Capability Document analysis → Feb 26 PDF DM to Ryan → Apr 7-8 Retention Associate prep thread → Apr 8/9 renewal-wedge pivot meeting → Apr 21 BT Core integration emails → Apr 27 Artifact Generator produces v2). **Acted AS each associate** (Email Classifier, Touchpoint Synthesizer, Intelligence Extractor, Artifact Generator) playing the role the autonomous flow would. **Wrote real entities to the OS via `indemn` CLI throughout** — not bulk-loaded. Hydrated 60+ entities into Alliance's constellation. Output: `artifacts/2026-04-27-alliance-trace-plan.md` (pre-execution plan, reusable template), `artifacts/2026-04-27-alliance-trace.md` (the trace narrative documenting every step + gap), `artifacts/2026-04-27-alliance-proposal-v2.md` (**the v2 deliverable for Cam** — renewal-wedge Phase 1 + lighter Phase 2/3, anchored on real Alliance data + the Retention Associate compound-outcome framing). PROPOSAL-stage Playbook record created — reusable for all future customers' PROPOSAL stage.

**Parallel bugfix fork session (in flight throughout):** Forked from this main session at the start of the trace. The shared-context-update mechanism (this main session logs findings to `os-learnings.md` → bugfix session reads them on resume → no human-in-the-middle handoff) worked end-to-end as designed. By session end: 7 OS bugs fixed/in-progress in parallel — Touchpoint Option B 🟢, silent stuck-state 🟢, cache leak 🟢, API 500-detail 🟢, entity-skill JSON examples 🟢, Bug #30 sparse-on-nullable (Meeting create) 🟢, Bug #29 route eviction 🟢. Several directly unblocked the trace as it progressed (Bug #30 + API 500-detail came online mid-trace, replacing 500 mystery errors with workable validation). New living document `fork-prompts/os-bugfix-resume.md` is the operational discipline for future parallel-session work — paste-ready resume prompt + recent-progress snapshot, updated as state changes.

**Key design validation:** the Apr 23 breakthrough ("entity model IS the playbook; same mechanism every stage; only Playbook record changes") now validated across two distinct stages — DISCOVERY (GR Little follow-up email) and PROPOSAL/NEGOTIATION (Alliance v2 proposal doc). The mechanism generalizes.

**New gaps surfaced** (logged in `os-learnings.md`): Slack ingestion is foundational (not deferrable Phase F — moved up in roadmap.md); Document.source enum missing slack_file_attachment; Proposal state machine lacks `superseded` transition path; Bug #30 fix needs propagation to all entities (e.g., Email.external_ref); stale entity-skill rendering (skills aren't auto-regenerated when generator changes); Email.interaction → Touchpoint rename gap; Touchpoint scope/Contact-resolution chicken-and-egg in the Synth flow; Bug #10 backfill continues to bite for past-30-day events.

**Phase A is COMPLETE after A2.** Phase B can begin.

### Session 11 (2026-04-28 late evening) — EC skill v7 + Document Drive sync shipped; **discovered every EC iteration v3→v7 has been ineffective** because deepagents skill discovery is broken; harness fix attempted but not fully resolved

The session that ended Sessions 9 + 10's "we need a better skill iteration" framing by discovering that the agent has never been reading the email-classifier associate skill content at all. Despite Hard Rules being added through versions v3 → v7, the agent's behavior has been driven entirely by the harness DEFAULT_PROMPT plus whatever it learned from `indemn skill get <Entity>` (auto-generated entity skills, NOT the associate skill).

**What landed:**
- EC skill v7 (content_hash `897d05babf0d3b83…`) — added Hard Rule #10 (Contact resolve mandatory) + Rule #11 (Contact-first ordering), strengthened Step 4 multi-1.0 ambiguity language with Diana@CKSpecialty as worked example. **Not yet read by the agent at runtime due to the deepagents discovery bug.**
- Document `69efbdea4d65e2ca69b0dd80` synced — `drive_file_id: 1pM3tYg6rHzG8RW6xU_titouiq_iddhIC` + `drive_url: https://drive.google.com/file/d/1pM3tYg6rHzG8RW6xU_titouiq_iddhIC/view`. Entity now reflects reality.
- Harness commit `5ec4e9f` on indemn-os main — pass skills LIBRARY directory to `deepagents.create_deep_agent(skills=[...])` instead of per-skill subdir paths. **Deployed and tested — system prompt STILL says "(No skills available yet)"** — see Bug #35 below.

**Five sequential traces on Diana@CKSpecialty in LangSmith project `indemn-os-associates`:**

| Run | Trace | Outcome | Diagnosis |
|---|---|---|---|
| #1 (Session 9, pre-LangSmith) | n/a | Auto-created Company | "skill compliance gap" hypothesis (wrong) |
| #2 (Session 10, LangSmith on, CLI broken) | `019dd522-…` | Auto-created Company | **CLI bug** — Bug #34. Fixed in `db97694`. |
| #3 (Session 10, CLI fixed, EC v4) | `019dd589-…` | Tried `email create`, E11000, narrative-completed | Skill update-vs-create + harness silent-stuck. Latter fixed in `d914d76`. |
| #4 (Session 10, EC v6, completion tightened) | `019dd5c1-…` | Linked Diana to existing Company. Skipped Step 3. | "v6 partial — needs v7" hypothesis. |
| #5 (Session 11, EC v7, harness "skills lib dir" fix) | `019dd602-…` | Agent finally called Contact resolve! BUT tried `email create` 4× (all failed). | **System prompt: "(No skills available yet)" — agent STILL not reading associate skill.** Bug #35. The Step 3 improvement came from the agent reading the Contact ENTITY skill (which has a Resolve section), NOT from the associate skill. |

**THE finding:** every single iteration of the EC skill (v3 → v7) has been theatre. The DB has the content. The agent never reads it. Bug #35 in os-learnings.md (NEW) — deepagents skills discovery in the LocalShellBackend setup doesn't find the SKILL.md files even with the library-dir path passed. Hypothesis space documented in `artifacts/2026-04-28-session-11-handoff.md` Section 3. Path resolution against backend `root_dir` is the most likely culprit.

**Architectural alignments confirmed (Craig + Claude):**
- DON'T inline skills into system prompts — the OS vision requires deepagents progressive disclosure to work properly. Inlining bypasses the mechanism instead of fixing it. (My initial proposal: rejected.)
- Harness reports facts; OS interprets meaning. The tightened `agent_did_useful_work` (Session 10) is observation-only — domain-agnostic. Detection of "agent didn't fulfill skill intent" lives in evals (Phase E) and observability dashboards on top of LangSmith — NOT in the harness.
- Path 3 for evaluations architecture stays — the existing `evaluations` repo eventually becomes a kernel adapter. Use LangSmith API directly for now.

**Other session noise/learning:**
- I over-engineered the `5ec4e9f` fix (refactored `_write_skills_to_filesystem` signature when a one-line change at the `create_deep_agent` call site would have sufficed). Craig pushed back: "AI slop". Future sessions: minimal change > comprehensive refactor.
- Branch confusion — Craig has been working in parallel on bugfix branches; my commits sometimes landed on the wrong branch. Always `git branch --show-current` + verify push destination before committing.
- LangSmith earned its place again — diagnosed the "(No skills available yet)" issue in 5 minutes by inspecting the system prompt directly. Without it we'd have iterated EC skill content blindly forever.

**Pipeline associates state:** EC suspended (kill switch held); TS suspended (unchanged); IE active. Diana reset to clean `received` state. No orphan Companies. Cleanup verified.

### Session 10 (2026-04-28 evening) — LangSmith tracing wired in; EC kill-switch root cause found + fixed; Path 3 evals architecture aligned

The session that turned Session 9's "research-level skill-compliance gap" into a 5-minute root-cause investigation. The hypothesis that the EC failure was an LLM-skill-following problem turned out to be wrong — the actual root cause was a kernel CLI bug. Without LangSmith we'd have spent the session iterating skill content blindly.

**LangSmith wired into async-deepagents harness** (vision §2 item 7 — foundation B1 milestone). Three env vars on Railway `indemn-runtime-async` (`LANGSMITH_API_KEY` from AWS Secrets, `LANGSMITH_TRACING=true`, `LANGSMITH_PROJECT=indemn-os-associates`) + a `config={metadata, tags, run_name}` dict on `agent.ainvoke()` so traces are queryable by `entity_id` / `message_id` / `associate_name` / `runtime_id` / `correlation_id`. Auto-tracing of LLM/tool/state-graph calls happens via deepagents being LangGraph-based. Project `19302981-aa9e-4869-9137-59a38d7646df` created at deploy time. **See "When working on X → Debugging an associate's behavior (LangSmith tracing)" for query patterns.**

**Architecture decision: evaluations service as OS adapter/integration (Path 3).** Read the `evaluations` repo (separate Indemn repo, port 8002, LangSmith-based, rubric + custom LLM judges, component-scoped, supports single-turn / multi-turn-replay / multi-turn-simulated). Designed three forks: standalone service learns to target OS associates / native OS evaluation kernel primitives / hybrid where OS gets `Run` + `eval` capability and the evaluations service stays as the LangSmith engine. **Picked Path 3 — eventually consolidate as a kernel adapter, but not now.** For this session: use the LangSmith Python/curl API directly + borrow rubric patterns from the evaluations repo without taking the dependency. Native OS evals stays a future fork-session.

**Three sequential agent runs on Diana@CKSpecialty's email (`69ea56250a2b41b7696076b3`)** isolating each issue:

| Run | Trace | Outcome | Diagnosis |
|---|---|---|---|
| #1 (pre-LangSmith) | n/a | EC auto-created Company `69f0df1bbca2d725ce90ed58` | Session 9 attributed to "skill compliance gap" — wrong |
| #2 (LangSmith on, CLI broken) | `019dd522-ac39-7fc2-bcab-dacdc450cfc5` | EC auto-created Company `69f0ee5b78abc86f9ca2a648` | **Trace showed `entity-resolve` returned HTTP 422** — CLI bug, agent fell through to create |
| #3 (CLI fixed, EC v4) | `019dd589-8d80-7aa3-93af-b59aff572184` | Resolve worked. EC tried `email create` instead of `update` (forgot context email exists), failed with E11000, narrated "email already exists", harness silent-completed | Two new issues: skill update-vs-create confusion + harness `agent_did_useful_work` looseness |
| #4 (EC v5 + tightened completion) | `019dd5c1-3aab-7ea3-aa08-d007044570a1` | ✅ Diana → `classified` linked to existing CK Specialty (`69eaa394...`). No dupe Companies. Version 6→8. | The actual fix sequence working end-to-end |

**Three kernel changes shipped to main (`db97694`, `956d7d5`, `d914d76`):**

1. **`indemn_os/main.py` — `_COLLECTION_LEVEL_CAPS` add `entity_resolve`** (kernel CLI bug fix). The published CLI hardcoded `{"fetch_new"}` — missing `entity_resolve`. So `indemn company entity-resolve --data '{"candidate":...}'` (no entity_id) routed through entity-level path, which list-and-loops with `limit=1000`, the API caps list at 100 → 422. Fix: add `entity_resolve` + comment requiring sync with `kernel/capability/__init__.py::COLLECTION_LEVEL_CAPABILITIES`. **One-line fix; agent had been doing the right thing the whole time.**
2. **LangSmith wiring** (cherry-picked into main from feat branch): `harnesses/async-deepagents/{main.py, pyproject.toml, uv.lock}`.
3. **`harnesses/async-deepagents/completion_logic.py` — tightened `agent_did_useful_work`**. Old contract: True if any mutating CLI call was *attempted* OR if final AI message had non-empty content. New contract: True iff at least one mutating CLI call's tool result indicates *success* (`[Command succeeded with exit code 0]`, no `[stderr]`, no `[Command failed]`). Removes the narrative-content fallback. Domain-agnostic — harness still doesn't know what each associate's job is, just observes "did any state-changing call succeed?". 24/24 tests passing including the new Diana failure pattern test.

**Per OS vision discussion: harness reports facts, OS interprets meaning.** The harness's tightened check is observation-only — "did any mutation succeed?" — not domain-aware. Detection of "agent didn't fulfill skill intent" lives in evals (Phase E) and observability dashboards on top of LangSmith traces. NOT in the harness. (My initial proposal was harness checks "did the watched entity transition" — Craig pushed back: that's domain knowledge that doesn't belong in glue code. Some associates legitimately don't transition their watched entity.)

**EC v6 (skill version stamp) deployed** with two new Hard Rules — #8 "resolve errors are showstoppers, not fallbacks; never fall through to create on resolve failure" and #9 "never call `indemn email create` — this skill operates on existing emails, the harness loaded one into your context and that's the one you classify". Plus new Step 0 "What you're processing (READ THIS FIRST)" emphasizing the email entity in input context IS the email to classify. Content_hash `5bbfdd13ad26c8db…`.

**State cleanup:** Rolled back the auto-created Company `69f0ee5b78abc86f9ca2a648` (run #2). Reset Diana to `received` via mongosh (state machine doesn't allow `classified → received`). After Run #4 verified Diana correctly lands at `classified` linked to the existing canonical CK Specialty.

**Bug filed for follow-up:** `kernel/cli/app.py` has the same divergence as `indemn_os/main.py` — no `_COLLECTION_LEVEL_CAPS` set at all (every cap routes through `_make_cap_cmd` as entity-level). Lower priority since the harness uses the published `indemn_os` CLI, but worth a separate fix. Test `tests/unit/test_adapter_cli_papercuts.py:92` already pins both surfaces against drift.

**EC v6 partial — still has gaps surfaced by Run #4 trace:**
- Skipped Contact resolve (Step 3) entirely — Diana's email isn't linked to a Contact
- Picked one Company candidate when resolve returned multiple at score 1.0 (should have gone needs_review per Hard Rule #3)
- These are non-destructive; Diana ended up linked to the right Company anyway. Defer to v7 (more explicit Step 3) or to eval-set coverage (Phase E).

**`indemn company list --search` doesn't work** (separate CLI gap surfaced repeatedly in traces; agent always falls back to entity-resolve). Worth filing as small CLI papercut.

### Session 9 (2026-04-28 afternoon) — Phase B1 entity-resolution skill propagation; trace-as-build captured; reactivation kill-switch fired

Phase B opens. Captured the **trace-as-build-method principle** durably (CLAUDE.md #20, vision §4, roadmap Phase B preamble) — every skill, watch, capability, and dashboard goes through a trace first before activation. The trace is the building method, not just shake-out validation. Adopted after Craig pushed back on "recommendation, not a plan" framing.

Built the Phase B1 plan artifact `artifacts/2026-04-28-phase-b1-data-state-and-trace-plan.md` (404 lines) — live OS state inventory, structural gaps, Path A cleanup pass, trace plan B1.1 → B1.7, explicit out-of-scope list, decisions log + checklist. Working memory for Phase B1.

**Path A executed cleanly.** Activated `entity_resolve` on Contact (email + name strategies); added `domain` strategy to Company `entity_resolve`. Bulk-deleted 79 orphan Companies (314 → 235). Resolved 91 high-volume Contact dupes across 10 groups (424 → 333). 10 Email.sender_contact references reclassified to canonicals via API before delete (clean audit trail).

**Phase B1 trace through 3 scenarios** acting as Email Classifier on real emails — known/known (clean), new Contact at known Company (Contact created), truly new domain (needs_review). Inline cleanup of LE × 4 + Justin Li × 3 dupes that the trace surfaced. Trace also covered TS for S1 + IE via Option B navigation — all worked end-to-end as Claude.

**Email.interaction → Email.touchpoint rename completed as ROOT-CAUSE FIX** (not a workaround — Craig pushed back on workaround language in TS skill v4). Migrated 1139 Email docs + updated `relationship_target` from Interaction to Touchpoint. Audited all 26 entities — only Email had the leftover. The `interactions` MongoDB collection kept (kernel chat/voice session log, different entity, IDs do not overlap with `touchpoints`).

**Three skills updated and deployed:** Email Classifier v3 (resolve-before-create with explicit decision tree, "Never auto-create Company"), Touchpoint Synthesizer v6 (Step 1a idempotency via Email.touchpoint back-reference, domain-gated Contact auto-create, Option B mandatory), Intelligence Extractor v3 (explicit two-step Option B navigation, mandatory Touchpoint transition every time).

**Reactivation B1.5 kill switch fired.** Reactivated EC, reprocessed Diana@CKSpecialty's email. EC processed 4 messages. Justin Li (single 1.0 match) classified correctly — clean. Diana (multi-candidate: 2 1.0 Contacts + 1 1.0 Company by domain) **violated the skill rule** — auto-created NEW Company despite explicit prohibition, did NOT mark needs_review on multi-match, did NOT transition email. Suspended EC immediately. Rolled back. Skill content verified correct in DB. **Skill-compliance gap on the harder multi-candidate branch.** Reactivation halted. Possible remedies: more explicit decision-tree language, force_reasoning veto rule on Company create, eval-driven fine-tuning. Out of scope for this session — research-level.

**Bugs reported to os-learnings.md:** (1) Silent-stuck-state regression — agent_did_useful_work() coverage gap on read-only-then-nothing-to-extract; (2) `--include-related` doesn't follow polymorphic Option B refs (workaround in IE skill); (3) List endpoint filter regression — silent filter drops on non-relationship fields, even unknown fields return 200 (workaround: use back-references for idempotency).

**Pipeline associate state at session end:** EC suspended (kill switch). TS suspended (unchanged). IE active (untouched). Three new skill versions deployed; only IE's hasn't been triggered autonomously yet.

### Session 8 (2026-04-28 morning) — Trace-showcase HTML + share to Cam + Kyle

Picked up from the Session 7 handoff and shipped Next-session deliverable 2: the Kyle-facing Alliance trace-showcase HTML. With it, Phase A is fully closed.

**What shipped:**
- `artifacts/2026-04-27-alliance-trace-showcase.html` — single self-contained HTML (833 lines, all CSS inline, system fonts, no external resources) using the Apr 24 GR Little v2 Kyle-validated visual language as the base. **Five-section spine matching the GR Little template:** (1) v2 proposal cover hero with 3-card Phase strip (WEDGE / WALK / RUN with terms) + iris CTA button to the Drive PDF; (2) vertical timeline of the 8 Alliance events Feb 1 → Apr 27 with source pills (Meeting / Email+Doc / Slack / Slack DM / Slack MPDM / OS) + per-event entity-pill chips capturing what hydrated at each step; (3) extraction table — 10 quote-to-entity-to-proposal-line rows showing how every load-bearing claim in v2 traces back to source (Christopher's Apr 7 stewardship-prep ask, Apr 8 renewal-wedge pivot, Peter's data validation, Capability Document, v1 proposal); (4) mechanism table with PROPOSAL stage "you are here" + Demo "skipped" honest about Alliance's actual journey; (5) 6-column proposal-as-spine showing v1 (sent → under_review) → v2 (rendered, now) with all 3 Phases populated under v2. Footer carries the full Alliance constellation entity-ID inventory.
- **v2 styled PDF uploaded to Cam's proposals folder on Drive** (`1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`, file ID `1pM3tYg6rHzG8RW6xU_titouiq_iddhIC`). Sits next to v1 in Cam's portfolio. Drive link wired into the showcase HTML hero CTA.
- **Shared in MPDM `mpdm-cam--kwgeoghan--craig-1`** (Cam + Kyle + Craig, channel `C0A3B18LY07`) as a thread reply to Cam's Apr 21 message about proposal output, with `reply_broadcast=True` so the message surfaces at channel-top. HTML uploaded twice — to thread and to channel-top — to work around Slack's broadcast file-attachment quirk. Tagged Cam (`<@U084CSZV49G>`) + Kyle (`<@UFK4DNNHG>`) in the body.

**Design choices that worked:** Vertical timeline (denser than the GR Little 4-event horizontal grid; right shape for 8+ events). Source-pill variety honored on each event (Slack channel / Slack DM / Slack MPDM / Meeting / Email+Doc / OS) — surfaces that the OS handles all touchpoint types uniformly. Mechanism table being honest about Alliance's non-canonical journey (Demo skipped) reinforces that the model represents real customer paths. No trace-gap caveat box — this is for showing what the OS produced, not what's still broken (the Slack-foundational / superseded-state / Apr 8 meeting reconstructed gaps live in `os-learnings.md`).

**Message framing for Cam + Kyle:** the work is part of the customer-success-system effort with Kyle, not just one-off proposal generation. Sales lifecycle modeled as entities, all Alliance data traced through, v2 proposal generated from that data. Looking to ship as a prototype product Cam + Kyle can both use and give feedback on. *"Proposal generation is the last step in the puzzle — the system covers everything that leads up to it too."*

**Phase A is fully closed after this session.** Two stages traced (DISCOVERY via GR Little, PROPOSAL/NEGOTIATION via Alliance), both Kyle-facing visual artifacts shipped, proposal PDF in Cam's portfolio for review/sending.

### Session 7 (2026-04-27 evening) — Styled-PDF rendering pipeline + Cam-portfolio match

Picked up from the Session 6 handoff and executed Next-session deliverable 1: re-render the Alliance v2 proposal styled to match Cam's portfolio. Built a reusable rendering pipeline that becomes the rendering step of the future autonomous Artifact Generator associate.

**What shipped:** `templates/proposal/template.hbs` + `template.css` + `saas-agreement.partial.hbs` + `assets/` (Indemn iris logo + 4 Barlow font weights), `tools/render-proposal.js` (Node + puppeteer-core + handlebars), `artifacts/2026-04-27-alliance-proposal-v2.json` (structured input — what the Artifact Generator produces from the entity graph), `artifacts/2026-04-27-alliance-proposal-v2.pdf` (9-page styled deliverable for Cam, ~175 KB), `skills/artifact-generator.md` (recipe + JSON contract + 15 style guidelines).

**Tooling decision:** HTML→PDF via puppeteer-core against system Chrome. Rationale: HTML/CSS lets non-developers edit the template, Chrome rendering is industry-best, no Chromium download needed. Footer is an inline SVG swoosh + white logo (CSS filter) + page number, delivered via puppeteer's `displayHeaderFooter` + `footerTemplate` (renders on every page).

**The hard-earned lessons** (captured in `skills/artifact-generator.md` and forming the 15 style guidelines):
- **Cam's brevity is the standard.** Early drafts were "word vomit" — 8-bullet stat lists, sub-sections like "What it does on Day 1" inside a phase, direct address to Christopher ("Christopher, this is what you described in your April 7 note"), v1/v2 comparison framing. Cam's portfolio is concise: ~80 words per opener, ~5 lines per phase, no direct address, no comparison framing. The cover's "Supersedes" line carries the v1→v2 context.
- **Section-per-page rhythm.** Cam's v1 is 9 pages: Cover / Unlocking Revenue Capacity / Addressing the Implementation Gap / Three-Phase Roadmap / Implementation Timeline / Implementation Roles & Commitment + Operational Guardrails / Investment Summary + Next Steps / SaaS Agreement / Acceptance. Use `start_new_page: true` on each major section.
- **Footer swoosh** SVG path: rounded TOP-LEFT corner only, sharp 90° bottom-left, flat top, bleeds RIGHT and BOTTOM. Logo rendered WHITE on swoosh via `filter: brightness(0) invert(1)`.
- **Section heading sweet spot is 28pt** — bigger wraps "Implementation Roles & Commitment" to 2 lines and creates layout breaks.
- **Tables: full grid borders + bold first column + 14pt cell padding.**
- **Operational Guardrails as sub-section under Implementation Roles**, never its own page.

**OS Document entity updated:** `69efbdea4d65e2ca69b0dd80` (Proposal v2 source_document) → `mime_type: application/pdf`, `file_size: 178935`, content pointer to repo path.

**Outstanding from Session 7:** Deliverable 2 (Kyle-facing trace-showcase HTML for Alliance) is the next-session top priority. Visual template at `artifacts/2026-04-24-information-flow-v2.html` (GR Little equivalent Kyle validated). Substantive content all in `artifacts/2026-04-27-alliance-trace.md` and `artifacts/2026-04-27-alliance-proposal-v2.md`.

---

## The OS — what it is and how to internalize it

You cannot build the customer system competently without deeply understanding the Indemn OS. The customer system is the first real domain built on it. The OS code lives at `/Users/home/Repositories/indemn-os/`. The OS itself has its own CLAUDE.md (a builder's manual), white paper, architecture docs, and step-by-step guides. **Read them all** before doing substantial work — and re-read the relevant ones whenever you're working in the corresponding area.

### What the OS is

An object-oriented insurance platform where every concept has schema + state machine + API + CLI. Define an entity and the kernel auto-generates its API endpoints, CLI commands, skill documentation (markdown), permissions integration, and UI views. AI agents are a *channel* into the platform, not a separate system — they use the same CLI as humans. This is the **self-evidence property:** building on the OS is defining what the system IS; the rest follows.

### Six structural primitives

| Primitive | What it is |
|---|---|
| **Entity** | A thing with identity, lifecycle, and fields. Kernel entities are Python classes; domain entities are data in MongoDB. Both share the same interface. |
| **Message** | A notification that an entity changed, routed to a role. The nervous system. Priority queue with visibility timeouts and cascade tracking. Split storage: `message_queue` (hot) + `message_log` (cold). |
| **Actor** | An identity — human, AI associate, or tier-3 developer. Authentication + role assignment + (for associates) skills, mode, runtime, LLM config. |
| **Role** | Permissions and watches. What actors can do and what flows to them. Inline roles (bound to an associate) or named shared roles (grantable). |
| **Organization** | Multi-tenancy scope. Every entity belongs to an org. Settings, template cloning, lifecycle (onboarding → active → suspended). |
| **Integration** | External system connections. Adapters, credentials (in AWS Secrets Manager, NEVER in MongoDB), ownership (org or actor), credential resolution chain (actor → owner → org). |

### Seven kernel entities (always present)

`Organization`, `Actor`, `Role`, `Integration`, `Attention` (real-time presence), `Runtime` (execution environment for associates), `Session` (auth state). Defined as Python classes in `kernel_entities/`. Cannot be redefined per-org.

### Domain entities (per-org, data-driven)

Defined as documents in MongoDB's `entity_definitions` collection. Per-organization. Dynamic Python classes created at startup via `kernel/entity/factory.py`. Domain entity names MUST NOT collide with kernel entity names. Reserved-name guard enforces this at startup AND at runtime registration.

The customer system has 27 domain entity definitions. They live as data in MongoDB; the kernel reads them and generates everything.

### Non-negotiable invariants

- **`save_tracked()` is the ONE save path.** All entity saves go through it — creates, updates, transitions, method invocations. One MongoDB transaction: optimistic concurrency check → computed fields → flexible data validation → entity write → changes record (with hash chain) → watch evaluation → message creation. No shortcuts. No bypass paths.
- **Selective emission.** Only entity creation + state machine transitions + `@exposed` method invocations emit messages. Plain field updates do NOT emit. This prevents watch storms.
- **Org isolation.** ALL queries use `find_scoped()` / `get_scoped()`. `org_id` is injected from contextvars by auth middleware. Never raw Motor queries except for infrastructure operations.
- **Trust boundary intact.** Harnesses authenticate via service token and use the CLI subprocess for ALL OS operations. Harnesses never import kernel modules directly.
- **Kernel is LLM-agnostic.** `grep -r "import anthropic" kernel/` returns nothing. LLM access happens in harnesses via the associate's `llm_config` (three-layer merge: Runtime + Associate + Deployment).
- **Skills are tamper-evident.** SHA-256 content hash computed on creation, verified on every load.
- **Credentials live only in AWS Secrets Manager.** Integration entities store `secret_ref` paths. Credentials never appear in entity queries, API responses, CLI output, or the changes collection.

### The 8-step domain modeling process

How to build any business domain on the OS. Read the worked examples in `/Users/home/Repositories/indemn-os/docs/guides/domain-modeling.md` (GIC insurance email processing + Indemn customer system).

1. **Understand the business** — narrative, workflows, people, systems, pain. No code.
2. **Identify entities** — apply the 7-test criteria (identity, lifecycle, independence, not-kernel-mechanism, CLI test, watchable, multiplicity). Design for AI extraction. Enums over free text.
3. **Identify roles and actors** — who participates, permissions, watches. Start with one role; differentiate later.
4. **Define rules and configuration** — per-org business logic, lookups, capability activation. Two rule actions only: `set_fields` (deterministic) and `force_reasoning` (veto).
5. **Write skills** — associate behavioral instructions in markdown.
6. **Set up integrations** — adapters, credentials, providers.
7. **Test in staging** — staging org, realistic data, validate end-to-end.
8. **Deploy and tune** — production, monitor `needs_reasoning` rate, add rules for patterns the LLM keeps handling.

### Required OS reading (read these before substantial customer-system work)

- **`/Users/home/Repositories/indemn-os/CLAUDE.md`** — the builder's manual. Compact reference. Always read this when working in the OS.
- **`/Users/home/Repositories/indemn-os/README.md`** — top-level orientation, what's running, repo structure.
- **`/Users/home/Repositories/indemn-os/docs/white-paper.md`** — the canonical vision document. The full WHY.
- **`/Users/home/Repositories/indemn-os/docs/architecture/overview.md`** — trust boundary, dispatch pattern, deployment topology, dependencies.
- **`/Users/home/Repositories/indemn-os/docs/architecture/entity-framework.md`** — self-evidence, save_tracked(), state machines, computed fields, schema migration. The deepest architecture doc.
- **`/Users/home/Repositories/indemn-os/docs/architecture/watches-and-wiring.md`** — watch conditions, scoping, unified queue, message cascade, selective emission. How everything connects.
- **`/Users/home/Repositories/indemn-os/docs/architecture/associates.md`** — actor model, skills, harness pattern, execution lifecycle, gradual rollout, the unified queue.
- **`/Users/home/Repositories/indemn-os/docs/architecture/rules-and-auto.md`** — rule engine, lookups, capabilities, the `--auto` pattern, `needs_reasoning` metric.
- **`/Users/home/Repositories/indemn-os/docs/architecture/integrations.md`** — adapters, credential resolution, webhooks, content visibility.
- **`/Users/home/Repositories/indemn-os/docs/guides/domain-modeling.md`** — the 8-step process with worked examples.

### Architecture docs you may need (situationally)

- `/Users/home/Repositories/indemn-os/docs/architecture/authentication.md` — JWT + sessions, MFA, platform admin
- `/Users/home/Repositories/indemn-os/docs/architecture/realtime.md` — Attention, Runtime, real-time chat/voice
- `/Users/home/Repositories/indemn-os/docs/architecture/observability.md` — changes collection, message log, OTEL tracing, debugging commands
- `/Users/home/Repositories/indemn-os/docs/architecture/infrastructure.md` — Railway services, deployment, cost
- `/Users/home/Repositories/indemn-os/docs/architecture/security.md` — org isolation, credential management, skill integrity, audit trail

### How-to guides

- `/Users/home/Repositories/indemn-os/docs/guides/adding-entities.md`
- `/Users/home/Repositories/indemn-os/docs/guides/adding-watches.md`
- `/Users/home/Repositories/indemn-os/docs/guides/adding-associates.md`
- `/Users/home/Repositories/indemn-os/docs/guides/adding-integrations.md`
- `/Users/home/Repositories/indemn-os/docs/guides/development.md` — local setup, testing, deploying, code conventions

### Sister project — `product-vision/`

The `projects/product-vision/` project is the design + status of the OS itself. It has:
- `CLAUDE.md` — OS-level project orientation, session bootstrap, design integrity rules
- `INDEX.md` — OS-level decisions log, status, open questions
- `artifacts/2026-04-16-vision-map.md` — **the authoritative OS-level synthesis** (104 design files distilled into 23 sections). Replaces reading individual design artifacts when working on OS internals.

When customer-system work surfaces something that needs to update the OS, the design discussion typically lands in product-vision; the implementation lands in `indemn-os/`; the customer-system project consumes the result.

---

## Learnings flow back to the OS — discipline

This is core to how this project works. **Building the customer system is shipping the OS.** Every gap we hit is information the OS needs.

### What "flowing back" looks like

When customer-system work reveals an OS issue, three things happen:

1. **It gets logged in this project.** The bug or gap goes into `artifacts/2026-04-24-os-bugs-and-shakeout.md` (running list — currently 29 bugs, 4 fixed). Or — for design-level gaps that aren't bugs but capability needs — they go into `artifacts/2026-04-24-extractor-procedure-and-requirements.md` (which lists the 9 OS capability gaps surfaced by the GR Little trace) and similar artifacts. The customer-system INDEX.md's "Open Questions" section also accumulates these.
2. **It informs OS design.** When the issue is significant enough (a missing capability, an architectural gap), it gets captured in product-vision/ artifacts AND in the OS repo's docs. The OS's vision-map gets refreshed periodically to absorb these. The OS's architecture docs get updated.
3. **It becomes OS implementation work.** Either:
   - In a parallel session in a forked worktree (when the OS work would block customer-system progress to inline),
   - Or as part of the customer-system roadmap when the OS fix is the unblock for the customer-system step we're on.

### Real examples from this project

- **Option B (Touchpoint source pointers).** Discovered Apr 24 in the GR Little trace — the Extractor associate had no path from Touchpoint to source Meeting transcript. Logged in `extractor-pipeline-gap.md`. The fix is a 2-field schema addition on Touchpoint + a Synthesizer update — small, but it unblocks autonomous extraction. This is OS work that came directly from customer-system work.
- **Bug #29 (entity-def replacement doesn't evict API routes).** Discovered Apr 24 trying to replace the stale Playbook entity definition. FastAPI's `include_router` appends rather than replaces. Required a redeploy to apply the new definition. Logged in `os-bugs-and-shakeout.md`. The fix is a kernel change (`register_entity_routes` should evict prefix routes before include).
- **Entity-resolution capability gap.** Discovered Apr 24 — Bug #16's root cause is that associates have no kernel-level capability to look up "is this Company already in the system?" before creating. The result was 446 Company records when ~90 are legitimate. Logged in `extractor-procedure-and-requirements.md` and in memory `project_customer_system_entity_identity.md`. This is a *new kernel capability* — not just a bug fix.
- **Cross-invocation tool-cache leak.** Discovered Apr 24 — an agent's `grep` matched content from a prior agent's cached tool result (`/large_tool_results/...` is shared per runtime container). This is a harness change in `harnesses/_base/harness_common/backend.py` to scope per-message_id.

Each of these started as a customer-system trace finding and became a queued OS update.

### The handoff document for OS-relevant findings

`os-learnings.md` (sibling of this file). Running register that catalogs every OS-relevant finding surfaced by customer-system work — bugs, missing capabilities, design gaps, ergonomics issues — ranked by what they unblock. Append-only with status updates. Source-of-truth detail lives in the linked source artifacts; this file is the index across them.

Read it at the start of any session that might touch OS internals. Update it whenever customer-system work surfaces something OS-relevant. When the OS-side implementation lands (kernel commit, doc update in `/Users/home/Repositories/indemn-os/docs/`), link it from the row.

The OS does not have its own copy of this register; we update OS docs (architecture, guides) directly when implementation lands, and `os-learnings.md` here is the queue + the trail.

### Discipline

When you hit something during customer-system work that's actually an OS-level concern:
1. Don't route around it silently. Don't add a workaround that buries the issue.
2. Log it in `os-bugs-and-shakeout.md` or `extractor-procedure-and-requirements.md` (or its successors) — whichever fits.
3. If it's blocking, surface to Craig — it may warrant a parallel forked session to fix.
4. If it's not blocking, log it and continue, but note it in the session handoff.
5. **Never simplify the customer-system design just because the OS doesn't support it yet.** Vision IS the MVP. The OS gets built up to support what the design requires.

The OS getting better is not a *consequence* of customer-system work — it's *part* of the work. Every session is potentially both.

---

## The cumulative thinking — what we know now

This is the substance distilled from the artifacts. Read it inline; reach for the artifacts when you need depth.

### The problem we're solving

If anyone needs to understand a customer, they ask Kyle. That doesn't scale, and Kyle can't plug in for three months. The data exists, but it's scattered across six+ disconnected systems with nothing authoritative, no one maintaining all of them. When Johnson Insurance went 10+ days without a response, nobody noticed until Kyle checked.

Beyond the source-of-truth problem: no defined delivery process (18 customers, each approached differently), no visibility into who's working on what (Peter finds out customers went live after the fact), no way to quantify value being delivered (ROI models exist for one customer — Branch).

These aren't separate problems. They're facets of one problem: **the company doesn't have a system that models its own operations.**

### The architectural foundation — entities are the system

Entities are cheap in the OS (auto-generated CLI, API, UI, skills). The cost of a new entity is near zero. The cost of cramming data into the wrong entity is confusion. So we model rich. Each Company has many Operations, Opportunities, Contacts, Touchpoints, Documents, Emails, Meetings, Deals, Proposals, Associates. The constellation IS the customer profile.

This is not a CRM. CRMs treat the customer record as the unit of work. Here the unit is the *graph state* — what entities exist, what's populated, what's empty, what state things are in. A CRM tells you "this is the customer." This system tells you "this is what we know, what we've done, what's missing, what's next."

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

### The breakthrough — the Playbook IS the entity model

(From `2026-04-23-playbook-as-entity-model.md`):

The Proposal is the destination. The entities IN the proposal need to be filled out. The process of filling them out IS the playbook. Empty fields are gaps. Gaps tell you what to do next. When the gaps are filled, you have a proposal.

This is why every customer follows the same process. Same entities. Same fields. The data differs; the structure is universal. Progress is measurable. Next steps are automatic. AI can drive it. The dashboard Kyle wants is just a view onto this — populated vs missing entities, days since last touch, next action, owner.

### The 2026-04-24 refinements (most recent crystallization)

1. **Playbook is data, not just a doc.** One record per Stage. Fields: stage, description, entry_signals, required_entities, expected_next_moves, artifact_intent. Terminus = Proposal at PROPOSAL stage.
2. **Playbook is consulted twice per touchpoint:** by the Extractor (what to extract at this stage) and by the Artifact Generator (what to render at this stage).
3. **Proposal hydrates from DISCOVERY onward.** Empty at first. Filled by every subsequent touchpoint. Rendered at PROPOSAL stage.
4. **Touchpoint must carry source pointers.** Option B: `source_entity_type` + `source_entity_id`. Otherwise associates can't navigate from Touchpoint back to the source content.
5. **Raw content is ground truth, available always.** Entities are curation; raw content provides voice. Both layer. Don't formalize the access pattern — it's already there via CLI.
6. **Opportunities created from DISCOVERY onward** for product-fit pain. Pain without product fit stays as Signal.

### The Alliance test (any design decision must pass it)

Every design decision must work for Alliance Insurance. Alliance is the deepest customer relationship Indemn has — through DISCOVERY → DEMO → PROPOSAL, currently in NEGOTIATION generating v2. If a design choice can't represent Alliance's full state cleanly — Christopher Cook as decision-maker, BT Core + Applied Epic + Dialpad in the tech stack, the renewal wedge pivot from the April 8 call, Craig's 30-page analysis as a Document, the original Feb 11 proposal as a superseded version, Phase 1 around Renewal Associate at $2,500/mo month-to-month — then the design is incomplete.

(Full Alliance picture in `2026-04-22-entity-model-design-rationale.md` — the Alliance Test section.)

---

## Foundational design principles — do not violate

These are the principles that hold across the project. Internalize them. They have been hard-won through prior pushback and they are what keep the system coherent.

1. **Vision IS the MVP.** Never simplify, collapse, or defer designed features without explicit approval from Craig. Implement EXACTLY what the design specifies. (Memory: `feedback_vision_is_mvp.md`, `feedback_never_simplify_vision.md`.)
2. **AI populates everything.** Design entities for extraction, not manual entry. Enums over free text wherever possible — AI classifies more reliably into defined categories than it generates consistent free text.
3. **No fluff fields.** Every field is structured data, an entity relationship, or specific source-of-truth content. No keyword summaries. No text describing things that are other entities. (Memory: `feedback_entity_design_principles.md`.)
4. **Documents for narrative, entities for structured facts.** Both live in the system, linked together. The narrative is the context; the entities are the actionable data.
5. **The Proposal entity IS the source of truth.** The document is a rendering. This inverts the traditional model — entities are queryable, versionable, watchable; documents aren't.
6. **No phases without a proposal.** Phases always belong to a Proposal, even at DISCOVERY where the Proposal is empty.
7. **Sources point TO Touchpoint, not the reverse** — but Touchpoint also carries `source_entity_*` forward pointers (Option B) so associates can navigate back to source content. Both directions exist; they serve different purposes.
8. **One save, one event** (kernel-level) — only creation, transitions, and `@exposed` method invocations emit messages. Plain field updates do not. Don't design around this; respect it.
9. **The OS does the connective tissue, your domain handles business data.** Don't model activity logs (changes collection), notifications (watches), audit trails (changes), team identity (Actor), permissions (Role), version history (changes). The kernel provides these.
10. **Entities are cheap; cramming is expensive.** If something passes the 7-test entity criteria (identity, lifecycle, independence, not-kernel-mechanism, CLI test, watchable, multiplicity), make it an entity.
11. **Don't import Kyle's PLAYBOOK-v2 or his prep-doc field specs as schema.** They are intent signal. Build from real data outward. (Memory: `feedback_craig_assertions_authoritative.md` — when Craig says something was designed a certain way, search until you find it.)
12. **Don't route around OS bugs with deterministic shortcuts** when the LLM-capability path is correct. Find root causes. (Memory: `feedback_understand_before_fix.md`.)
13. **Don't propose roadmaps unilaterally.** Engage as a thought partner. Ask Craig first. (Memory: `feedback_brainstorm_alignment.md`, `feedback_altitude_of_decisions.md`.)
14. **Verify against the live system.** Don't claim work is complete without running the actual command, querying the actual entity, checking the actual state. (Memory: `feedback_evaluate_honestly.md`, `feedback_complete_data.md`.)
15. **Never delete or replace historical entries in INDEX.md** — Decisions, Open Questions, Artifacts. Always append. (Memory: `feedback_never_delete_history.md`.)
16. **Don't fabricate data** in entities, configs, prompts, or KB. (Memory: `feedback_no_fabricated_data.md`.)
17. **Customer-system work is OS work.** They are not separate projects. Findings here flow back to update the OS itself — kernel code, docs, architecture. The 8-step domain modeling process *is* the OS being built. Where the boundary matters: don't let OS work eat the customer-system trace work *without intent*. When an OS fix would block customer-system progress and is significant, fork to a parallel session in a separate worktree. When an OS fix is small and on the path, do it inline.
18. **Don't conflate customers.** GR Little is a one-off demo for Kyle's validation. Alliance is the proof point. Arches Insurance is a secondary trace example. Each has its own state.
19. **Read the artifacts every time.** Don't trust your memory across sessions. Sessions clear context. Read.
20. **Trace-as-build: act as the associate before you deploy it.** Tracing isn't just the Phase A shake-out method — it's the canonical building method for all of Phase B+ and beyond. Every skill, watch, capability, and dashboard goes through a trace first: pick a real scenario, run the procedure yourself using the `indemn` CLI on live data, watch the entity state move through each step, and only write the skill content (or wire the watch / capability) once the procedure works. The skill is the writeup of what worked. This makes the build testable by construction — if you can run the CLI sequence and produce the right state, the skill is correct. It surfaces gaps before deployment (the way Option B + the cache leak + the silent stuck-state were discovered during the GR Little trace, not after). It forces reckoning with real data state instead of theory. Discovered as Phase A's shake-out method (GR Little Apr 24, Alliance Apr 27) and elevated to the building method itself in Session 8. Apply this to skill propagation, new associate creation, watch-cascade hardening, dashboard development, integration adapter work — anything the OS does, trace it yourself first. Activate the autonomous version only after the trace produces the right state on real data.

---

## Where we are now (as of 2026-04-28, end of session 11 — EC v7 + Document Drive sync shipped; deepagents skill discovery discovered broken (Bug #35); harness fix attempted but not fully resolved)

### What's hydrated, proven, and shared
- 27 entity definitions live, including the Playbook entity with the aligned shape.
- GR Little Apr 22 first-discovery call traced end-to-end + Kyle validated.
- **Alliance hydrated end-to-end via the Apr 27 trace** — 8 timeline steps, 60+ entities created (constellation now queryable from Company hub). v2 proposal artifact rendered for Cam. PROPOSAL-stage Playbook record created — reusable for any future customer.
- **Styled-PDF rendering pipeline shipped** — `templates/proposal/` (Handlebars + CSS + assets) + `tools/render-proposal.js` (puppeteer-core + Chrome) + `skills/artifact-generator.md` (15 style guidelines). Alliance v2 PDF at `artifacts/2026-04-27-alliance-proposal-v2.pdf` — 9 pages, brand-consistent with Cam's portfolio (verified via visual diff). Document `69efbdea4d65e2ca69b0dd80` in OS updated with PDF metadata.
- **v2 PDF uploaded to Cam's proposals folder on Drive** (`1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`, file ID `1pM3tYg6rHzG8RW6xU_titouiq_iddhIC`) — sits next to v1 in Cam's portfolio.
- **Trace-showcase HTML shipped** — `artifacts/2026-04-27-alliance-trace-showcase.html`, 833 lines, self-contained, five-section spine (cover hero / vertical timeline / extraction table / mechanism / proposal-as-spine). Wired with the Drive PDF link.
- **Shared with Cam + Kyle in MPDM** — `mpdm-cam--kwgeoghan--craig-1` channel `C0A3B18LY07`, thread reply to Cam's Apr 21 ask, with reply_broadcast so it surfaces at channel-top. Awaiting Cam's content/visual feedback on the proposal + Kyle's reactions on the showcase.
- ~930 emails ingested across the team. Gmail + Google Workspace + Google Meet API working.
- **Vision + roadmap crystallized at project root** (`vision.md` + `roadmap.md`). Comprehensive pre-scoped 4-phase roadmap (A→F + continuous threads).
- **Shared-context-update mechanism proven** — main session + parallel bugfix fork session ran simultaneously, coordinating via `os-learnings.md` and the living `fork-prompts/os-bugfix-resume.md`.

### Phase A is fully complete. Phase B opens next.

### Phase B1 progress (Sessions 9 + 10 combined)
- ✅ Trace-as-build-method captured (CLAUDE.md #20, vision §4, roadmap Phase B preamble) [S9]
- ✅ Phase B1 plan artifact written (`artifacts/2026-04-28-phase-b1-data-state-and-trace-plan.md`) [S9]
- ✅ Path A cleanup (orphans, contact dupes, capability activations) [S9]
- ✅ Email.interaction → Email.touchpoint rename (root-cause fix, 1139 docs migrated) [S9]
- ✅ Three skills updated and deployed: EC v6, TS v6, IE v3 [S9 + S10 — EC iterated to v6 after diagnosis]
- ✅ **LangSmith tracing wired into async-deepagents harness** (vision §2 item 7 foundation milestone) [S10]
- ✅ **Kernel CLI bug fix** — `_COLLECTION_LEVEL_CAPS` add `entity_resolve` (the Session 9 "skill compliance gap" was actually this CLI bug) [S10]
- ✅ **Tightened harness `agent_did_useful_work`** — closes the silent-stuck-state regression (now requires ≥1 successful mutating call) [S10]
- ✅ **Diana@CKSpecialty re-verified end-to-end** — EC correctly classifies + links to existing CK Specialty (`69eaa394...`) without creating a duplicate [S10]
- ⚠️ EC v6 partial — Contact resolve step still skipped; multi-1.0 candidate handling still picks one rather than going needs_review. Non-destructive; defer to v7 or eval coverage.

### Outstanding for next session (top priority)
- **EC v7 / eval coverage for the remaining gaps.** Diana run #4 (LangSmith trace `019dd5c1-3aab-7ea3-aa08-d007044570a1`) showed two still-non-compliant branches: agent skipped Contact resolve (Step 3) and picked a Company candidate when multiple at 1.0 (should have been needs_review per Hard Rule #3). Both non-destructive. Two options: (a) v7 with even more explicit Step 3 + multi-1.0 enforcement; (b) build an eval set covering these branches (Path 3 evals — Phase E foundation). Recommendation: try (a) once cheaply, then build (b) for durable regression protection.
- **Native OS evaluations design.** Path 3 was aligned this session — eventual goal is the evaluations service becomes a kernel adapter (`system_type: evaluation`, provider: `langsmith` or `indemn-evals`) so any associate gets evals as a first-class capability. Deferred to a separate fork-session. Design doc should land in `../product-vision/`.
- **Document entity sync** — Document `69efbdea4d65e2ca69b0dd80` in the OS could be updated with `drive_file_id: "1pM3tYg6rHzG8RW6xU_titouiq_iddhIC"` + `drive_url: <Drive link>` to keep the entity graph in sync with reality. Quick CLI update.
- **Watch for Cam + Kyle reactions** in MPDM `mpdm-cam--kwgeoghan--craig-1` (channel `C0A3B18LY07`).
- **Filed kernel bug** — `kernel/cli/app.py` has no `_COLLECTION_LEVEL_CAPS` set at all (separate from indemn_os, lower priority).

### Pipeline associates current state
- Email Classifier — **suspended** (deliberate after Session 10 verification). Skill v6 deployed, end-to-end verified working on Diana single-1.0-Company case. Multi-1.0 + Contact-create branches still need v7 / evals before broad reactivation.
- Touchpoint Synthesizer — **suspended** (unchanged from Session 9). Skill v6 with idempotency. Has not been triggered autonomously yet.
- Intelligence Extractor — **active** (untouched from Session 9). Skill v3. Silent-stuck-state regression that previously caught it is **fixed** as of Session 10 (tightened `agent_did_useful_work`).

### What landed Apr 28 evening (Session 10 — main session, NOT a fork)
- 🟢 LangSmith wired into async-deepagents harness (commit `956d7d5` cherry-picked to main — feat branch + langsmith dep + RunnableConfig metadata). Project `indemn-os-associates` (id `19302981-aa9e-4869-9137-59a38d7646df`). API key at AWS Secrets `indemn/dev/shared/langsmith-api-key`.
- 🟢 Kernel CLI fix: `indemn_os/main.py` `_COLLECTION_LEVEL_CAPS` add `entity_resolve` (commit `db97694`). One-line fix; root cause of Session 9's "skill compliance gap".
- 🟢 Harness completion check tightened: `agent_did_useful_work` requires successful mutation; narrative-content fallback removed (commit `d914d76`). 24/24 tests passing including the new Diana failure pattern test.
- 🟢 EC skill v6 deployed (Step 0 added + Hard Rules #8 #9 added; content_hash `5bbfdd13ad26c8db…`).

### What landed Apr 27 (parallel bugfix fork — burst #3)
- 🟢 Touchpoint Option B (source pointers) — schema + Synth skill v3
- 🟢 Silent workflow stuck-state — agent-output detection + queue fail
- 🟢 Cross-invocation tool-cache leak — per-activity scoping
- 🟢 API 500-detail — validation errors now informative
- 🟢 Entity-skill JSON-shape examples — generator now emits payload examples
- 🟢 Bug #30 sparse-on-nullable-unique (Meeting create unblocked; foundation for Email/Document creates)
- 🟢 Bug #29 route eviction — entity-def hot-update now works without redeploy
- 🟢 List endpoint arbitrary field filters (`?filter={...}` safelist with field-name allowlist + ObjectId hex coercion)
- 🟢 Bug #31 entity_resolve kernel capability — domain-agnostic ranked candidates, never auto-picks
- 🟢 Bug #22 effective_actor_id forensics chain — propagates env var → CLI header → middleware contextvar → ChangeRecord
- 🟢 async-harness import regression — package-qualified import after silent-stuck-state PR

### What landed Apr 28 (parallel bugfix fork — burst #4, multiple waves in one session)
- 🟢 Bug #23 + #24 — bulk-delete operator filter safelist (`$in`/`$nin`/`$ne`/`$gt`/`$gte`/`$lt`/`$lte`/`$exists`) + per-field type coercion (ObjectId hex / `$oid` / ISO 8601 / `$date`) + Pydantic alias support so `_id` works alongside canonical `id`. `BulkExecuteWorkflow` returns `{matched, succeeded, errored, errors}` with `completed_no_match` when matched=0. `GET /api/bulk/{id}` fetches `handle.result()` on terminal states.
- 🟢 Bug #32 — preview activity ObjectId serialization + bounded retry policy (latent, exposed by Bug #23's correct org_id contextvar fix).
- 🟢 Bug #10 — `reprocess` primitive in `kernel/message/reprocess.py` for backfilling watches against historical entities. Role-scoped (one role, not broadcast). Fresh `correlation_id` per call, `event_metadata.reprocess=True`. New `POST /api/{collection}/{id}/reprocess` + auto-registered CLI verb.
- 🟢 Bug #9 — boundary coercion in `_resolve_relationship_dict_inputs`. Default 400 with shape hint when LLM passes dict on a relationship field; opt-in `auto_resolve: bool` flag on FieldDefinition triggers `entity_resolve` with single-1.0 auto-link policy.
- 🟢 Bug #11 + #20 + #21 + #28 — CLI papercut cluster. `actor transition`/`delete` now exist; `actor list --type` filters via the safelist; transition API canonical body field is `to` (docs corrected); `/api/queue/stats` aliased to `/api/_meta/queue-stats`.
- 🟢 Always-fresh entity-skill rendering — `indemn skill get <Entity>` re-renders from current EntityDefinition + current generator at GET time. Stored Skill row is a cache; EntityDefinition is source of truth. Generator improvements propagate to every entity instantly.
- 🟢 Bug #30 propagation via auto-emit `partialFilterExpression` — reconciler treats `unique=True AND not required AND default is None` as "unique-when-set" automatically. Two latent create-500 traps (`deals.deal_id`, `emails.external_ref`) auto-healed at deploy time.

### What's broken or open
**Customer-system domain work (belongs to main session, not the fork):**
- Bug #16/#17 finishing — the kernel piece (entity_resolve capability) shipped Apr 27. Either update the Email Classifier + Touchpoint Synthesizer skills to call `indemn <entity> entity-resolve` before creating, OR (cleaner) set `auto_resolve=true` on the relationship fields per Apr 28's Bug #9 boundary fix and let the API handle it transparently.
- Email.interaction → Touchpoint rename (entity definition update — kernel-side rename happened Apr 23, the Email entity def still references the old name).
- Document.source enum missing `slack_file_attachment`.
- Proposal state machine lacks `superseded` transition.
- Touchpoint scope/Contact-resolution chicken-and-egg (skill design).

**True OS work still open (next fork burst):**
- `--include-related` doesn't follow reverse relationships — substantive feature, last big OS-feature gap. Important for vision.md item #5 ("the constellation is queryable").
- Bug #5 / #7 / #8 — adapter + CLI ergonomics papercuts.
- Bug #15 — naive collection pluralization (`Company` → `companys`).
- Bug #19 — change records sometimes have non-Date timestamp.
- Bug #12 / #13 — infrastructure config (asks Craig — wrong MongoDB URI in AWS secret; Railway auto-deploy docs).
- Ingestion-durability companion to Bug #10 (Gmail/Meet adapters copy transcripts into Document at ingestion so they survive 30-day source retention).

**Pre-existing chat runtime issue:** `indemn-runtime-chat` fails startup with `Error 401: Invalid service token`. Needs Craig to rotate the chat-runtime token. NOT a bug to fix in either session — flag and move on.

### Open design questions (carried forward, NOT yet resolved)
- **Opportunity vs Problem entity** — does unmapped pain need its own entity, or does Opportunity loosen `mapped_associate` to nullable?
- **Document-as-artifact pattern for emails** — Email entity, Document entity, or hybrid? Proposal→Document already designed; emails need resolution.
- **Stages — 12 sub-stages with multi-select for archetypes** (Kyle's ask). Open design.
- **Origin / referrer tracking** (Pat Klene → GR Little example) — field on Deal or new Introduction entity?

### Bug + enhancement registers
- `artifacts/2026-04-24-os-bugs-and-shakeout.md` — running OS bug list (29 bugs, 4 fixed). To consider promoting to `bugs.md` at the project root.
- `enhancements.md` — to be created as separate from bugs (per Apr 27 conversation with Craig).

### What we agreed about how the OS gets better
Every OS bug we hit during customer-system work gets logged. If a bug is *blocking* core work and significant to fix, raise to Craig — it may warrant a parallel session in a forked worktree. The fork keeps customer-system work moving while OS reliability gets attended to. Examples that would warrant a fork: Bug #29 (route eviction), entity-resolution capability for Bug #16, Option B for Touchpoint source pointers, Bug #23 (bulk-delete operator filters).

Examples of bugs that just get logged and worked around: CLI papercuts (missing singular `delete`, missing `actor transition`), UX gaps (unhelpful `--help` output), documentation/observability misses.

**The principle:** every issue we surface that, once fixed, makes our own life easier going forward — fix it. As we go, building gets faster. **That is the acceleration mechanic.**

---

## What we're doing next — the upcoming working session

**Goal:** trace Alliance Insurance end-to-end through the OS to produce a v2 (revised) Proposal document, plus the "story" of how we got there — the same shape as the GR Little email demo, but for the PROPOSAL stage / NEGOTIATION transition.

**Why Alliance:** the deepest customer relationship Indemn has — already through DISCOVERY, DEMO, PROPOSAL, currently in NEGOTIATION. Cam needs a v2 proposal soon (driven by customer feedback we'll discover during the trace itself). Tracing Alliance exercises every stage of the entity model and produces a real artifact Cam will react to.

**Secondary trace example:** Arches Insurance. Cam forwarded a message from Rocky in Slack about it; they're at PROPOSAL stage. To be loaded at session start (search Slack for "Arches" / Cam → Craig DMs).

**The working session is the brainstorm.** They are the same activity. The trace exercises the vision; the vision shapes what the trace means. Out of this session: a refreshed vision document (using `artifacts/2026-04-14-vision-and-trajectory.md` as inspiration), an updated roadmap, and the v2 Alliance proposal artifact.

**Pre-session prep (medium):**
1. Read this CLAUDE.md fully (you're doing that now).
2. Read `INDEX.md` — Status, Decisions log, Open Questions, full Artifacts table.
3. Read REQUIRED READING below.
4. Read `artifacts/2026-04-14-vision-and-trajectory.md` (the inspiration for the refresh).
5. Read `artifacts/2026-04-14-problem-statement.md` and `artifacts/2026-04-14-system-capabilities.md` (the original framing).
6. Read `artifacts/context/2026-04-21-kyle-craig-call-transcript.txt` (Kyle's original strategic thinking — the seed).
7. Read **the full** `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt` (his most recent comprehensive thinking — the recap is a summary; the transcript has texture).
8. Look up Cam's Arches Insurance message in Slack (forwarded from Rocky).
9. Identify what's in Cam's Drive folders for Alliance materials (no deep hydration — that happens in the trace).
10. **Draft a refreshed `vision-and-trajectory.md` dated today** as a starting point for the brainstorm. Concise. Synthesizes what we know now. Brings forward Kyle's framing + the Playbook-IS-entity-model insight + Proposal-as-spine + OS-as-platform.

**Do not pre-hydrate the entity graph for Alliance.** That happens in the trace itself — discovering what data needs to load is *part* of the working session.

---

## REQUIRED READING — at session start

Two tracks: **the project** (this CLAUDE.md and the customer-system artifacts) and **the OS** (the platform underneath). Both are required because the customer system is a build on the OS — you can't do one without understanding the other. Do not skip. Do not skim.

### Track 1 — This project (customer-system)

1. **This file** (`CLAUDE.md`) — orientation, vision, journey, principles.
2. **`INDEX.md`** — living history (Status, Decisions, Open Questions, full Artifacts table).
3. **`artifacts/2026-04-25-session-handoff-and-roadmap.md`** — the most recent comprehensive synthesis. Current state, bugs, agreed roadmap.
4. **`artifacts/2026-04-24-information-flow-v2.html`** — open in browser. The Kyle-validated demo. The shape of what we're building.
5. **`artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md`** — the architectural refinements aligned but not yet implemented.
6. **`artifacts/2026-04-24-kyle-sync-recap.md`** — Kyle's reactions, asks, action items. Then read the full transcript at `context/2026-04-24-kyle-craig-sync-transcript.txt` if going to design something Kyle has opinions about (dashboards, stages).
7. **`artifacts/2026-04-23-playbook-as-entity-model.md`** — the load-bearing key insight.
8. **`artifacts/2026-04-22-entity-model-brainstorm.md`** — current entity field-level spec.
9. **`artifacts/2026-04-22-entity-model-design-rationale.md`** — *why* the entity model is shaped this way.

### Track 2 — The OS (the platform you are building ON)

You **must** internalize how the OS works to build on it competently. The OS docs are not "on demand" — they are required.

1. **`/Users/home/Repositories/indemn-os/CLAUDE.md`** — the OS builder's manual. Compact reference. Read first.
2. **`/Users/home/Repositories/indemn-os/README.md`** — top-level OS orientation, what's running, repo structure.
3. **`/Users/home/Repositories/indemn-os/docs/white-paper.md`** — the canonical vision document for the OS. The full WHY.
4. **`/Users/home/Repositories/indemn-os/docs/architecture/overview.md`** — trust boundary, dispatch pattern, deployment topology.
5. **`/Users/home/Repositories/indemn-os/docs/architecture/entity-framework.md`** — `save_tracked()`, state machines, computed fields, the self-evidence property, schema migration. Deepest doc.
6. **`/Users/home/Repositories/indemn-os/docs/architecture/watches-and-wiring.md`** — watches, conditions, scoping, message cascade, selective emission. How everything connects.
7. **`/Users/home/Repositories/indemn-os/docs/architecture/associates.md`** — actor model, skills, harnesses, execution lifecycle, gradual rollout, the unified queue.
8. **`/Users/home/Repositories/indemn-os/docs/architecture/rules-and-auto.md`** — rule engine, lookups, capabilities, the `--auto` pattern.
9. **`/Users/home/Repositories/indemn-os/docs/architecture/integrations.md`** — adapters, credential resolution, webhooks.
10. **`/Users/home/Repositories/indemn-os/docs/guides/domain-modeling.md`** — the 8-step process with worked examples.

After REQUIRED READING (both tracks), check the **When working on X** section below for activity-specific reading.

---

## Files index — by purpose

### Spine (always loaded — these are this CLAUDE.md's siblings)
- **`CLAUDE.md`** (this file) — vision + journey + principles + orientation
- **`INDEX.md`** — append-only project history (Status, Decisions, Open Questions, full Artifacts table, External Resources)
- **`roadmap.md`** *(to be created from `artifacts/2026-04-25-session-handoff-and-roadmap.md` once it stabilizes)* — single source of truth for where we're at and where we're going. Living. Updated every session.
- **`vision.md`** *(to be created from refreshed `vision-and-trajectory.md` in upcoming session)* — narrative end-state articulation. Slow-changing.
- **`os-learnings.md`** — running register of OS-relevant findings (bugs, capability gaps, design questions, ergonomics) surfaced by customer-system work, ranked by impact, with status. The handoff doc that ensures every OS gap gets back to the OS itself. Read at start of any OS-touching session; append when findings surface.
- **`artifacts/2026-04-24-os-bugs-and-shakeout.md`** — bug-level deep detail (symptom, root cause, proposed fix). `os-learnings.md` references it.
- **`enhancements.md`** *(to be created if needed)* — separate from bugs if helpful; for now `os-learnings.md` covers both.

### Architecture & vision
- `artifacts/2026-04-22-entity-model-brainstorm.md` — field-level entity spec
- `artifacts/2026-04-22-entity-model-design-rationale.md` — *why* the entity model is shaped this way
- `artifacts/2026-04-23-playbook-as-entity-model.md` — the load-bearing key insight
- `artifacts/2026-04-24-playbook-entity-vision.md` — Playbook entity's role
- `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` — architectural refinements (Apr 24)
- `artifacts/2026-04-14-vision-and-trajectory.md` — original synthesis (inspiration for refresh)
- `artifacts/2026-04-14-domain-model-thinking.md` — entity criteria framework
- `artifacts/2026-04-14-problem-statement.md` — the 7 concepts with evidence
- `artifacts/2026-04-14-system-capabilities.md` — 17 functional areas, ~130 capabilities

### Trace artifacts & demos
- `artifacts/2026-04-24-information-flow-v2.html` — Kyle-facing demo (current)
- `artifacts/2026-04-24-information-flow.html` — v1 narrative version (superseded)
- `artifacts/2026-04-24-grlittle-followup-email-draft.md` — drafted email + line-to-entity mapping
- `artifacts/2026-04-24-trace-plan-and-design-notes.md` — GR Little trace plan + entity-identity open question
- `artifacts/2026-04-23-system-flow-v4.html` — earlier visual diagram for Kyle (superseded)

### Pipeline reliability & OS gaps
- `artifacts/2026-04-24-extractor-pipeline-gap.md` — why the Extractor failed; **Option B is the chosen path**
- `artifacts/2026-04-24-extractor-procedure-and-requirements.md` — procedure for autonomous Extractor + 9 OS capability gaps
- `artifacts/2026-04-24-os-bugs-and-shakeout.md` — running OS bug list (29 bugs, 4 fixed)
- `artifacts/2026-04-23-implementation-session.md` — the build record from Apr 22-23
- `artifacts/2026-04-23-pipeline-operations-guide.md` — how to run/monitor/troubleshoot the pipeline

### Session handoffs (chronological)
- `artifacts/2026-04-25-session-handoff-and-roadmap.md` — most recent (start here)
- `artifacts/2026-04-24-session-handoff.md` — Apr 24 morning handoff (start of that session)
- `artifacts/2026-04-21-session-handoff.md` — Apr 21 (customer-system parallel session)
- `artifacts/2026-04-21-unified-handoff.md` — universal session handoff (older but referenced)
- `artifacts/2026-04-20-session-handoff.md` — Apr 20

### Kyle interaction history
- `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt` — full Apr 24 sync transcript (where the demo was validated)
- `artifacts/2026-04-24-kyle-sync-recap.md` — processed summary of Apr 24 sync
- `artifacts/2026-04-24-alignment-framing.md` — pre-Apr 24-sync framing (treat Kyle's docs as signal not spec)
- `artifacts/2026-04-24-kyle-craig-apr23-sync.md` — Apr 23 sync transcript (verbal alignment)
- `artifacts/2026-04-24-kyle-prep-doc-apr24.md` — Kyle's Apr 24 prep doc (preserved as aspirational signal)
- `artifacts/context/2026-04-21-kyle-craig-call-transcript.txt` — Apr 21 strategic call (the seed of this project)

### Source material — Kyle's EXEC docs
- `artifacts/context/kyle-exec/PLAYBOOK-v2.md` — Kyle's sales motion playbook (per-stage operational detail)
- `artifacts/context/kyle-exec/PROSPECT-SIX-LEADS-v0.md` — the 6 active prospects (FoxQuilt, Alliance, Amynta, Rankin, Tillman, O'Connor)
- `artifacts/context/kyle-exec/DICT-PROSPECTING-v2.md` — Kyle's prospecting data dictionary
- `artifacts/context/kyle-exec/DICT-SALES-v2.md` — Kyle's sales data dictionary
- `artifacts/context/kyle-exec/DICT-CUSTOMER-SUCCESS-v2.md` — Kyle's customer success data dictionary
- `artifacts/context/kyle-exec/MAP.md` — Kyle's 30-workstream map across 5 pillars

### Original raw context
- `artifacts/context/2026-04-14-craigs-brain-dump.md` — Craig's raw notes from conversations with Kyle, George, Ganesh
- `artifacts/context/2026-04-14-source-inventory.md` — complete source inventory

### Historical / superseded
- `artifacts/2026-04-14-phase-1-domain-model.md` — superseded by 2026-04-22 brainstorm
- `artifacts/2026-04-19-known-issues.md`, `artifacts/2026-04-19-ui-evaluation.md`, `artifacts/2026-04-19-demo-readiness.md` — UI/demo prep artifacts
- `artifacts/2026-04-20-ui-and-assistant-session.md` — UI polish session
- `artifacts/2026-04-20-meeting-ingestion-plan.md` — earlier meeting ingestion plan
- `artifacts/2026-04-21-meeting-ingestion-checkpoint.md`, `artifacts/2026-04-21-meeting-ingestion-session.md` — meeting ingestion records
- `artifacts/2026-04-21-deal-entity-evolution.md` — Deal entity changes
- `artifacts/2026-04-21-action-items.md` — earlier action items

### The OS itself — `/Users/home/Repositories/indemn-os/`

The OS code, docs, and architecture. This is *the platform we are building on, and the platform we are simultaneously updating.*

**Top-level files:**
- `/Users/home/Repositories/indemn-os/CLAUDE.md` — builder's manual (compact reference for AI sessions)
- `/Users/home/Repositories/indemn-os/README.md` — top-level orientation, what's running, repo structure
- `/Users/home/Repositories/indemn-os/docs/white-paper.md` — the canonical vision document
- `/Users/home/Repositories/indemn-os/docs/getting-started.md` — CLI installation, first commands

**Architecture deep-dives** (`/Users/home/Repositories/indemn-os/docs/architecture/`):
- `overview.md` — trust boundary, dispatch pattern, deployment topology, dependencies
- `entity-framework.md` — self-evidence, save_tracked(), state machines, computed fields, schema migration
- `watches-and-wiring.md` — watch conditions, scoping, unified queue, message cascade, selective emission
- `rules-and-auto.md` — rule engine, lookups, capabilities, the --auto pattern, needs_reasoning metric
- `associates.md` — actor model, skills, harness pattern, execution lifecycle, gradual rollout
- `integrations.md` — adapters, credential resolution, webhooks, content visibility
- `authentication.md` — JWT + sessions, five auth methods, MFA, platform admin, recovery
- `realtime.md` — Attention, Runtime, scoped watches, handoff, voice/chat harnesses
- `observability.md` — changes collection, message log, OTEL tracing, debugging commands
- `infrastructure.md` — Railway services, local dev, deployment strategies, cost model
- `security.md` — org isolation, credential management, skill integrity, audit trail

**How-to guides** (`/Users/home/Repositories/indemn-os/docs/guides/`):
- `domain-modeling.md` — the 8-step process with worked examples (GIC + CRM)
- `adding-entities.md`, `adding-watches.md`, `adding-associates.md`, `adding-integrations.md`
- `development.md` — local setup, testing, deploying, code conventions

**Source code structure:**
- `kernel/` — the platform (entity framework, watches, rules, auth, API)
- `kernel_entities/` — 7 kernel entities (Organization, Actor, Role, Integration, Attention, Runtime, Session)
- `indemn_os/` — CLI package
- `harnesses/` — async, chat, voice runtime images
- `seed/` — standard entity templates and reference data

### Companion project — `../product-vision/`

The OS-level project that captures the OS's design and status (separate from the OS code repo). Where OS design discussions land before becoming OS implementation work.

- `../product-vision/CLAUDE.md` — OS-level project orientation, session bootstrap, design integrity rules
- `../product-vision/INDEX.md` — OS-level decisions log + status
- `../product-vision/artifacts/2026-04-16-vision-map.md` — **the authoritative OS-level synthesis** (104 design files distilled into 23 sections; replaces reading individual design artifacts)

### External resources (linked, not in repo)
- Cam's proposal folder (Drive): `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`
- Kyle+Cam shared folder (Drive): `1KKH8juzCqVyRQ36h72nnB9Djdjy8m_j1`
- White paper PDF (Drive): `1Cr_F_K3a_I_iul7HgJqXv1IY8KieyS40`
- CRM InsurTechNY sheet (Drive): `1B3QnzfS8IEM7cMN3ar9gSFRw8K8_viFmH-dEajQ9tQg`
- OS API: `https://api.os.indemn.ai`
- OS UI: `https://os.indemn.ai`
- Chat Runtime: `wss://indemn-runtime-chat-production.up.railway.app/ws/chat`

---

## When working on X, READ these

This is the activity-driven router. Match your work; read what's listed; do not assume you remember it from a prior session.

**Resuming after context reset:**
→ This file (full read) → `INDEX.md` → REQUIRED READING block above → relevant section below for the specific activity.

**Tracing a customer through the OS (any customer):**
→ `artifacts/2026-04-24-information-flow-v2.html` (the shape) → `artifacts/2026-04-24-grlittle-followup-email-draft.md` (the line-to-entity map template) → `artifacts/2026-04-24-trace-plan-and-design-notes.md` (the trace plan template) → `artifacts/2026-04-24-extractor-procedure-and-requirements.md` (what extraction must produce).

**Working on Alliance specifically:**
→ All REQUIRED READING above first. → Read the Alliance Test section in `artifacts/2026-04-22-entity-model-design-rationale.md` (pre-articulated full picture of Alliance in the OS). → Pull Alliance materials from Drive (Cam's proposal folder + the shared Kyle/Cam folder; meetings/emails surface during the trace itself). → Search prior artifacts for "Alliance" mentions (the Apr 8 renewal-wedge call, the Feb 11 v1 proposal, Craig's 30-page analysis are all referenced).

**Working on Arches Insurance:**
→ Look up Cam's forwarded message from Rocky in Slack (search "Arches" in Slack channels and Cam → Craig DMs). → Then run a normal trace pattern (see "Tracing a customer" above).

**Designing or refining the Playbook:**
→ `artifacts/2026-04-24-playbook-entity-vision.md` (entity shape and role) → `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` (Playbook consulted twice — Extractor + Artifact Generator) → `artifacts/2026-04-23-playbook-as-entity-model.md` (the underlying insight).

**Designing dashboards (Kyle's Apr 24 priority ask):**
→ Read **the full** `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt` — Kyle gave specific dashboard ideas: customer value, success path, days to next step, push-to-talk for sales reps to update fields, "automatic and okay if it'll be wrong." The recap summary will MISS texture. → `artifacts/2026-04-24-kyle-sync-recap.md` for the structured summary.

**Designing or fixing extraction:**
→ `artifacts/2026-04-24-extractor-pipeline-gap.md` (what's broken structurally — Option B is the chosen fix) → `artifacts/2026-04-24-extractor-procedure-and-requirements.md` (step-by-step procedure + 9 OS capability gaps).

**Designing the Artifact Generator associate:**
→ `artifacts/2026-04-24-extractor-procedure-and-requirements.md` (template for associate procedure) → `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` (how Artifact Generator uses Playbook + raw content) → `artifacts/2026-04-24-grlittle-followup-email-draft.md` (line-to-entity render mapping is the template).

**Refining the entity model (any change):**
→ `artifacts/2026-04-22-entity-model-brainstorm.md` (current spec) → `artifacts/2026-04-22-entity-model-design-rationale.md` (why) → `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` (recent open questions: Opportunity vs Problem; Document-as-artifact).

**Designing entity resolution / dedup (Bug #16):**
→ memory: `project_customer_system_entity_identity.md` → `artifacts/2026-04-24-trace-plan-and-design-notes.md` (the open question section) → `artifacts/2026-04-24-os-bugs-and-shakeout.md` Bug #16 detail.

**Working with Kyle (sync prep, prepping artifacts for him, anticipating his reactions):**
→ `artifacts/2026-04-24-alignment-framing.md` (how to position our work with Kyle — his docs are signal not spec) → `artifacts/2026-04-24-kyle-sync-recap.md` (most recent reactions + asks) → `artifacts/context/2026-04-21-kyle-craig-call-transcript.txt` (his original strategic thinking) → `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt` (his most recent comprehensive thinking — full content).

**Working with Cam:**
→ Read his proposals folder (Drive `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`) — 6 customer proposals (Alliance, Branch, Johnson, GIC, Charley, Physicians Mutual) + SaaS Agreement. Read the analysis of Cam's proposals at the end of `artifacts/2026-04-22-entity-model-brainstorm.md` ("What Cam's Proposals Taught Us" section).

**Hitting an OS bug:**
→ `artifacts/2026-04-24-os-bugs-and-shakeout.md` (check if logged; add bug-level detail if not) → `os-learnings.md` (add a row in the appropriate severity section if not there) → If blocking core work: raise to Craig for parallel fork. → If not blocking: log and move on.

**Capturing a new OS capability gap or ergonomics issue:**
→ `os-learnings.md` (the running register). For capability gaps that need an associate-procedure write-up too, also append to `artifacts/2026-04-24-extractor-procedure-and-requirements.md`.

**Designing or implementing OS changes (kernel, harnesses, CLI):**
→ Start with `/Users/home/Repositories/indemn-os/CLAUDE.md` (builder's manual). → Read the relevant architecture doc in `/Users/home/Repositories/indemn-os/docs/architecture/` (entity-framework for entity changes, watches-and-wiring for routing, associates for harness work, etc.). → Read the relevant guide in `/Users/home/Repositories/indemn-os/docs/guides/`. → Reference `../product-vision/artifacts/2026-04-16-vision-map.md` for cross-cutting design context (104 OS design files synthesized). → Read the relevant kernel source (`kernel/entity/save.py`, `kernel/api/registration.py`, etc.).

**OS bug fix (when a customer-system bug is actually an OS bug):**
→ `artifacts/2026-04-24-os-bugs-and-shakeout.md` — see if logged. → Trace the root cause in the kernel source (`/Users/home/Repositories/indemn-os/kernel/`). → Fix in the OS repo. → Update OS docs if behavior changed. → Cross-reference back here in the bug log when fixed.

**Adding a new OS capability or kernel feature:**
→ Discuss in `../product-vision/` first if it's design-level. → Read `/Users/home/Repositories/indemn-os/docs/architecture/rules-and-auto.md` (capability registration pattern). → Implement in `/Users/home/Repositories/indemn-os/kernel/capability/`. → Add doc in `/Users/home/Repositories/indemn-os/docs/architecture/` or update existing one. → Reference in customer-system artifacts where it gets used.

**Debugging an associate's behavior / failure (LangSmith tracing):**

Wired in 2026-04-28 (Session 10) — every async-deepagents associate run now emits a full LangSmith trace with the LLM reasoning chain, every `execute` tool call, every middleware step, and the entity context the agent was given. **This is the diagnostic layer that turns "the agent did the wrong thing and we don't know why" into a 5-minute root-cause investigation.**

- **Project:** `indemn-os-associates` (LangSmith)
- **API key:** AWS Secrets Manager `indemn/dev/shared/langsmith-api-key` (and `indemn/prod/shared/langsmith-api-key` for prod)
- **Project ID:** `19302981-aa9e-4869-9137-59a38d7646df`
- **UI:** https://smith.langchain.com → indemn org → indemn-os-associates project (filter by tags or metadata)

Each trace carries metadata that makes it queryable by domain identifiers, not just LangSmith-internal IDs:
```
associate_id, associate_name, message_id, entity_type, entity_id, runtime_id, correlation_id
```
plus tags `associate:<name>`, `entity_type:<type>`, `runtime:<id>`.

**To query a specific run** (replace `$KEY` with the API key):
```bash
# Find the trace for an entity_id
curl -s -H "x-api-key: $KEY" -H "Content-Type: application/json" \
  "https://api.smith.langchain.com/api/v1/runs/query" \
  -d '{"session": ["19302981-aa9e-4869-9137-59a38d7646df"], "is_root": true, "limit": 5,
       "filter": "and(eq(metadata_key, \"entity_id\"), eq(metadata_value, \"<entity_id>\"))"}'

# Pull the full trace tree (paginate by 100s; trace usually has ~130 runs)
TRACE_ID="<from above>"
for off in 0 100 200; do
  curl -s -H "x-api-key: $KEY" -H "Content-Type: application/json" \
    "https://api.smith.langchain.com/api/v1/runs/query" \
    -d "{\"trace\": \"$TRACE_ID\", \"limit\": 100, \"offset\": $off}"
done
```

Tool calls appear with `run_type: "tool"`. LLM calls appear with `run_type: "llm"` (model is `ChatVertexAI` for the current setup). Middleware wrappers (Skills, Filesystem, SubAgent, Summarization, AnthropicPromptCaching, TodoList) appear as `chain` runs.

**Use case that proved its value (Session 10):** the EC compliance gap that Session 9 attributed to "skill-compliance gap on multi-candidate branch" was actually a kernel CLI bug — `entity-resolve` was returning HTTP 422 because the published indemn_os CLI was missing it from `_COLLECTION_LEVEL_CAPS`. The agent saw a tool error and fell through to `create`. Without LangSmith we couldn't see the failed resolve call. With it, the diagnosis took 5 minutes. The "skill compliance" framing was wrong and we'd have spent the session iterating skill content blindly.

**Wiring location:** `harnesses/async-deepagents/main.py` — env vars (`LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_PROJECT`) on `indemn-runtime-async` Railway service + a `config={metadata, tags, run_name}` dict passed to `agent.ainvoke()`. Auto-tracing of LLM/tool/state-graph calls happens because deepagents is LangGraph-based.

**End of session, before stopping:**
→ Update `INDEX.md` (Status section, append to Decisions, append to Open Questions, append to Artifacts table). → Update `roadmap.md` (when it exists) to reflect new state and next steps. → Add new artifacts to the Files Index above. → Add new "When working on X" entries if a new activity type emerged. → Update the "Where we are now" section above if state shifted significantly. → If significant work happened, create a session-handoff artifact dated today.

---

## INDEX.md is the living history

This CLAUDE.md is orientation; it changes slowly. **`INDEX.md` is the running ledger** — it's where decisions get appended, where Open Questions accumulate, where Status reflects what just happened, where every artifact ever produced is listed with description.

When you're tempted to rewrite or restructure INDEX.md, **don't.** Append. The historical entries are the trail of how thinking evolved. Even superseded decisions are valuable — they show what we considered and why we changed direction. (Memory: `feedback_never_delete_history.md`.)

INDEX.md sections:
- **Status** — current snapshot. Updated each session.
- **External Resources** — links to Drive, Sheets, Railway, GitHub, etc.
- **Artifacts** — full table of every artifact with date and ask.
- **Decisions** — append-only log. New decisions go at the bottom.
- **Open Questions** — append-only log. When a question is resolved, note it but don't delete it.

Read INDEX.md every session. It's the project's memory.

---

## Cadence and discipline — how this system stays alive across context resets

**This is the most important section for the long-term health of the project.** Without this discipline, every session resets to zero and Craig has to re-explain the cumulative thinking. With this discipline, the project carries forward seamlessly. Treat the discipline below as non-negotiable.

### Start of every session — mandatory protocol

1. Read this CLAUDE.md **in full.** Not skim — read.
2. Read the **most recent session-handoff artifact** (`artifacts/<latest-date>-session-handoff*.md` or `artifacts/<latest-date>-session-N-handoff.md`). It contains a hard-coded reading list with absolute paths.
3. Read `INDEX.md` (Status, Decisions, Open Questions, full Artifacts table).
4. Read `os-learnings.md` (the running register of OS-relevant findings — what's queued, blocking, in-progress).
5. **Read both tracks of REQUIRED READING (Section "REQUIRED READING — at session start").** Track 1 = this project's artifacts. Track 2 = the OS docs at `/Users/home/Repositories/indemn-os/`. **Both tracks are non-negotiable.** Reading only Track 1 produces work that fights the OS instead of leveraging it. The discipline failure mode that has happened twice now (Sessions 8 and 9): the user's session-start prompt listed Track 1 files only, Claude trusted that list as exhaustive instead of cross-checking against this CLAUDE.md's REQUIRED READING block. **The session-start prompt is not the canonical reading authority — this CLAUDE.md is. If the session-start prompt is silent on Track 2, read Track 2 anyway.**
6. Read the **When working on X** section for the specific activity you're about to do.
7. Then begin work.

If you skip these reads "to save context," you will fail. The reading IS the work. The discipline of reading is what makes the work coherent.

**Coverage check (do this before claiming reading is done):** Can you answer (a) what `save_tracked()` does in a single transaction, (b) what the three event types that trigger selective emission are, (c) what the trust boundary separates, (d) what the `--auto` pattern is, (e) what the trace-as-build-method principle says (CLAUDE.md #20 / vision §4)? If any of these are blank, you haven't read enough.

### During the session — running discipline

- **Capture findings as they happen.** Bugs go in `artifacts/2026-04-24-os-bugs-and-shakeout.md` (deep detail) AND `os-learnings.md` (running register). Capability gaps go in `artifacts/2026-04-24-extractor-procedure-and-requirements.md` AND `os-learnings.md`. Open design questions go in `INDEX.md § Open Questions`. Don't bury findings in trace artifacts where they'll be lost.
- **When you make a design decision, ask:** am I aligned with Craig's prior thinking, or am I reconstructing? If reconstructing, stop and check. Reference the design-dialogue artifact (`artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md`) and `INDEX.md § Decisions` to confirm.
- **When tempted to propose a roadmap or structure unilaterally, stop and ask.** Craig has explicitly pushed back on this. Your job is to add to the cumulative thinking, not redirect it.
- **Quick wins toward the vision matter.** Surface area first; iterate to quality. Kyle's framing: "everything's a v0."

### When to run the end-of-session protocol

**Wait for Craig's signal.** Do not self-trigger the end-of-session protocol based on your guess about how much context is remaining — that judgment is unreliable and will cause you to wrap up prematurely. Craig will tell you when it's time to begin wrapping the session.

When he gives the signal, treat the protocol below as the immediate next thing — drop whatever you were mid-task on (capturing the in-progress state as part of the wrap), and run the full protocol before the session ends. The protocol is the work that makes the next session possible.

### End-of-session protocol — mandatory before stopping

Run **all** of these before declaring the session done. None are optional.

1. **`INDEX.md`** — append to Decisions any decisions made; append to Open Questions any unresolved questions; update Status section to reflect what just happened; add any new artifacts to the Artifacts table with dates and one-line descriptions. **Append, never delete or rewrite history.**
2. **`os-learnings.md`** — for every OS-relevant finding from this session: add a row in the appropriate severity section with a 1-2 sentence summary and links to source artifacts. If status of a previous finding changed (in-progress / fixed), update its row.
3. **`roadmap.md`** (when it exists) — update to reflect new state and immediate next steps.
4. **This CLAUDE.md** — update **"Where we are now"** section if state shifted (entity counts, pipeline state, what's open). Update **"How we got here — the journey across sessions"** by adding a new session entry if substantive work happened. Add new artifacts to the **Files Index**. Add new entries to **"When working on X, READ these"** if new activity types emerged. **Don't rewrite the cumulative thinking section** unless something genuinely changes our understanding — that section evolves slowly.
5. **Memory** — update `project_customer_system_status.md` if project status shifted significantly. Add new memory entries for fresh open design questions worth carrying across sessions (use `project_*` type, follow existing naming).
6. **Session handoff artifact** — if substantive work happened (not every session warrants one), create `artifacts/<today>-session-handoff-<descriptor>.md` summarizing: what we set out to do, what happened, current entity state, decisions aligned, open questions, what's next. The Apr 25 handoff is the template (`artifacts/2026-04-25-session-handoff-and-roadmap.md`).
7. **Verify before declaring done** — actually open `INDEX.md`, actually open `os-learnings.md`, actually re-read the "Where we are now" section. Don't trust your memory that you updated them; verify.

### Periodically — when crystallization happens

- Revise `vision.md` (when it exists) and stamp the revision in a dated artifact (`<today>-vision-revision-<descriptor>.md`).
- Promote running registers if they get unwieldy (e.g., move resolved bugs out of the active list).
- Re-evaluate the Files Index categorizations if they're not serving "when to read this" lookups well.
- If a major session-cluster of work completes a phase, write a phase-summary artifact and update the journey section of this CLAUDE.md with a new chapter.

### Pre-flight check at session start — verify the system didn't rot

When starting fresh, after the mandatory reads, before doing work, verify:
- Is `os-learnings.md` consistent with what `INDEX.md § Open Questions` is saying?
- Is the "Where we are now" section in this CLAUDE.md consistent with the most recent session-handoff artifact?
- Is the most recent INDEX.md Decisions entry recent enough that it makes sense Craig would have just been working on this?

If any of these are out of sync, **flag to Craig** before doing work — the system rotted between sessions and we should reconcile before adding more work on top.

### How this discipline keeps the project alive

This document, INDEX.md, os-learnings.md, and the artifact set are a *living memory*. They only stay alive if every session takes the small cost (5-10 minutes) of updating them at the end. That small cost is the difference between "the next session picks up where this one left off" and "the next session starts from scratch and Craig has to re-explain."

Craig has been explicit: he should not have to re-explain objectives every session. The way you make sure he doesn't is the protocol above. Treat it as the most important part of every session.

---

## What you DO NOT do

- **Do not skip the reading.** "I remember this from before" is wrong; sessions clear context.
- **Do not propose roadmaps unilaterally.** Ask first. Engage as thought partner.
- **Do not simplify the vision** for "MVP simplicity." Vision IS the MVP.
- **Do not import Kyle's PLAYBOOK-v2 or his prep-doc field specs as schema.** They are intent signal. Build from real data outward.
- **Do not route around OS bugs** with deterministic shortcuts when LLM-capability is the right path. Find root causes.
- **Do not declare work complete without verification.** Run the actual command, query the actual entity, check the actual state.
- **Do not delete or replace historical entries in INDEX.md.** Always append.
- **Do not fabricate data** in entities, configs, prompts, or KB.
- **Do not declare quality on partial signals.** Verify thoroughly.
- **Do treat customer-system work as OS work.** They are not separate projects. Customer-system findings flow back to update the OS itself — kernel code, docs, architecture. **But** don't let OS-fix work eat the customer-system trace work without intent. When OS work would block, fork to a parallel session.
- **Do NOT skip the end-of-session protocol** to "save context for actual work" when Craig signals the session is wrapping. The protocol IS the actual work. Without it, every future session pays. With it, the project carries forward seamlessly. (See "Cadence and discipline" — the end-of-session checklist is non-negotiable when invoked.)
- **Do NOT let CLAUDE.md, INDEX.md, or os-learnings.md rot.** Every session that does substantive work updates them. If a session ends with these out of sync with reality, the next session inherits noise and Craig has to re-explain. That is the failure mode this entire system is built to prevent.
- **Do not conflate customers.** GR Little (one-off demo for Kyle), Alliance (the proof point), Arches (secondary trace) — each has its own state.
- **Do not propose splitting "Phase 1, 2, 3" without first asking what the priorities and threading are.** The vision is the thread. Phases are puzzle pieces toward it, not the structure itself.

---

## A note on tone and voice

This project is foundational work for what Indemn becomes. The team is excited about it. Kyle is excited about it. Cam will use it. Ganesha will scale it. The work has weight, and shipping it well matters.

When you write artifacts: every line should be intentional. The diagram we showed Kyle was good because every visual choice traced to something real. The email was good because every paragraph mapped to an entity, with the personal touches drawn directly from the transcript. The artifacts you produce should hold that bar.

When you build: the entities you create represent real customers, real conversations, real decisions. Don't be sloppy with what they hold. Verify against the live system. Trace through what happens when state changes. Read the changes collection when you're not sure.

When you brainstorm: the cumulative thinking has a single thread — the proposal-as-spine, every interaction hydrating, the playbook-as-entity-model insight, the OS as platform underneath. Add to it. Don't redirect it.

You are not a checklist follower. You are a collaborator on building the system that becomes how the company operates. Engage like that.
