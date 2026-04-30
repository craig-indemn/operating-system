# Customer System — SESSIONS

> **Append-only log of session objectives + outcomes.** New entries at the **top**. Each session adds one entry at end of session. Loaded on-demand when a session needs to look back at history or learn the objective-statement format from prior entries.
>
> The full Journey lives in `CLAUDE.md § 5`. This file is the lighter-weight per-session log.

---

## Session 14 — 2026-04-30 — TD-1 substantial execution (Drive end-to-end, Slack adapter, voice harness v1, Bug #38/#41/#42 closeouts)

**Objective:** Execute TD-1. Pre-flight cleanup → ReviewItem infrastructure → activate fetcher actors bottom-up → Slack adapter NEW build → voice harness verification → log-touchpoint skill. Per Craig mid-session: "We are implementing EVERYTHING to completion" — Drive, Slack, and Voice all in this session, no deferring.

**Parallel sessions during:**
- Bug #38/#37/#41 fork session ran early in Session 14 (per Bug #38 handoff prompt at session start). Closed with 3 indemn-os commits (`1026d78`, `c36969b`, `96684d5`) and 2 operating-system commits. Three bugs verified fixed live. Fork closed mid-session.

**Outcome:**

- **TD-1 ~85% complete.** Sub-pieces 1, 2, 3, 5, 8 closed end-to-end. Sub-pieces 4 (Slack), 6 (log-touchpoint chat verification), 7 (voice canonical rebuild) partial — see Handoff.
- **Pre-flight cleanup:** Bug #36's 500 emails + 5 unrelated meetings deleted (Armadillo email + meeting preserved). Bug #37 rows deleted by fork session via the new bulk-delete skip_invalid path.
- **ReviewItem entity + Reviewer role created** — collection `review_items`, polymorphic target_entity_type/id, 8-value enum reason, state machine open→in_review→resolved/dismissed. Smoke-tested end-to-end (created → watch fired → message routed → resolution flow). Craig assigned to reviewer role.
- **Email Fetcher activated end-to-end** — id `69f2bf30942e5629f07a8313`, cron `*/5 * * * *`, gemini-3-flash-preview/global, autonomous. Trace `019ddf95-d579-7390-9483-beece987389f` 18:10-18:15Z verified: 7 LLM turns all `finish=STOP`, agent fetched 326 new emails.
- **Meeting Fetcher activated** — id `69f39ec6c0b340cf765a38d6`, cron `*/15 * * * *`. 30-day backfill (per-user via direct API to dodge CLI 600s timeout) returned fetched=396 created=2 skipped=394 errors=0.
- **Drive adapter (NEW kernel build)** — `fetch_documents()` method on GoogleWorkspaceAdapter (per-user DWD impersonation, paginate by pageToken, dedup by drive_file_id, format Document-shaped dicts with `external_ref = drive_file_id`). 6 unit tests in `TestFetchDocumentsContract` GREEN. Document `external_ref` field added (sparse+unique). fetch_new capability activated. Deployed (indemn-os commit `c87376d`). 30-day backfill: fetched=1161 created=493 skipped=668 errors=0.
- **Drive Fetcher activated** — id `69f3abbe268936150b46a0fa`, hourly cron, gemini-3-flash-preview/global.
- **Slack adapter (NEW kernel build)** — `kernel/integration/adapters/slack.py`: Slack Web API via httpx; conversations.list (public+private, no DMs, paginate cursor); conversations.history (paginate cursor, oldest/latest); strict params; rate-limit + auth error typing; SlackMessage-shaped dicts with `external_ref = "{channel_id}:{slack_ts}"`. 9 unit tests in `TestSlackAdapterContract` GREEN. Self-registered via `register_adapter("messaging", "slack", ...)`. SlackMessage entity created (16 fields). fetch_new capability activated. Deployed (commit `c87376d`). **Slack Integration entity created + transitioned to active** (id `69f3bb5097300b115e7236dd`, secret_ref pointing at `indemn/dev/integrations/slack-oauth`). Bot token stored in AWS Secrets. **Live fetch BLOCKED — see Handoff Bug #45.**
- **Document.source enum** extended with `slack_file_attachment`.
- **log-touchpoint skill** uploaded + assigned to OS Assistant (skills count 23→24). Chat-side end-to-end verification pending.
- **voice-deepagents v1 built but architecturally wrong** — uses `livekit.agents.Agent` with single custom `execute` tool. Does NOT use deepagents library, harness_common modules, Interaction/Attention entity lifecycle. Per `docs/architecture/realtime.md` + `docs/architecture/associates.md` (which I read mid-session after Craig's correction "I would read files to understand first"), the canonical voice harness MUST mirror chat-deepagents structure: deepagents `create_deep_agent`, three-layer config merge, harness_common interaction/attention/runtime/backend modules, and a DeepagentsLLM adapter wrapping the agent for LiveKit's AgentSession. **v1 needs DELETE + REBUILD.** Voice runtime entity already in place (id `69f3b7fc97300b115e7236a0`); service token at `indemn/dev/shared/runtime-voice-service-token`. v1 commit at `62f47f9` will be reverted/replaced next session.
- **Bug #42 reframe + resolution.** Original framing was wrong. Actual root cause: Gemini 2.5 Flash returns `MALFORMED_FUNCTION_CALL` on the deepagents `write_todos` schema (Pythonic `default_api.WriteTodosTodos(...)` syntax instead of valid JSON). Verified across 3 traces. Resolution: switched to `gemini-3-flash-preview/global`. Both runtime defaults flipped (async-deepagents-dev + chat-deepagents-dev). IE picked up the new model on its next run.
- **LangSmith query gotcha discovered** — `order: "DESC"` (uppercase) returns HTTP 422 silently; must use `"desc"` (lowercase). The fork session's earlier "0 traces visible" symptom was this query bug — traces had been arriving the entire time post-LangSmith-wiring.
- **Bug #38 + #37 follow-on + #41 fixed by fork session** — 3 indemn-os commits. Stale message backlog drained (1015 EC + 28 TS messages parked cleanly via the new `parked` status + WorkflowAlreadyStartedError catch).
- **Bug #43** (Drive adapter scope was understated) — closed in-session with the actual Drive adapter build.
- **Bug #44** logged + partially addressed — voice-deepagents v1 built (but per Blocker #2 it's wrong shape; v2 rebuild pending). Per-actor default_assistant pattern confirmed deferred per Craig (shared OS Assistant suffices for now).
- **Bug #45 NEW** — Slack `resolve_integration()` not finding active Integration. Symptom: `POST /api/slackmessages/fetch-new` returns "No messaging integration available." State + debug-pointer in CURRENT.md Blocker #1.

**Major architectural learnings (Session 14):**
1. **Trace-as-build worked at the kernel level too.** Drive adapter built TDD-style (6 tests RED → implementation GREEN), deployed, verified live with real backfill. Same for Slack adapter (9 tests). 437 unit tests pass overall (was 428 + 6 Drive + 9 Slack).
2. **The OS canonical voice harness pattern is in `docs/architecture/realtime.md` + `docs/architecture/associates.md`.** Specifically: voice harness lifecycle = Interaction creation → Attention with `purpose=real_time_session` + heartbeat → build deepagents agent → events stream subprocess → process voice frames → close. The framework expectation is deepagents (not LiveKit's native Agent class) with LiveKit as audio I/O.
3. **Three-layer LLM config merge** (Runtime defaults → Associate skill → Deployment override) happens at invocation time in `kernel/temporal/activities.py::load_actor`. Voice harness needs to honor this.
4. **`harness_common`** has the OS-level lifecycle helpers (`interaction.py`, `attention.py`, `runtime.py`, `backend.py`) — both async-deepagents and chat-deepagents use them. voice-deepagents must too.
5. **Restricted tool surface in v1 was a mistake.** v2 should give the agent the full deepagents toolset (execute + write_todos + read_file/write_file + glob/grep + task subagent dispatch) — same as chat-deepagents. The agent picks what to use per skill instructions.

**Handoff to next session:**

Use `PROMPT.md` as kickoff. Two priorities:

1. **Bug #45 — Slack live fetch debug.** Read `kernel/integration/dispatch.py::resolve_integration()` to see what filters it applies on lookup by system_type. Likely candidates: status filter expecting something other than `active`; org_id mismatch; (system_type, provider) tuple key in the adapter registry. Fix → 90-day Slack backfill → build slack_fetcher role + skill + Slack-Fetcher actor (5min cron) → activate.

2. **Voice-deepagents canonical rebuild (Bug #44 / Blocker #2).** DELETE v1 files (`harnesses/voice-deepagents/{tools.py, assistant.py, main.py, tests/test_tools.py}`; pyproject.toml + Dockerfile reusable parts only). REBUILD mirroring `harnesses/chat-deepagents/`:
   - `agent.py` — copy `chat-deepagents/agent.py` verbatim, swap DEFAULT_PROMPT for voice-specific guidance (concise, ask-one-question-at-a-time, no JSON dumps to user). Uses `deepagents.create_deep_agent` + `init_chat_model` + `build_backend`.
   - `session.py` — copy `chat-deepagents/session.py` and swap WebSocket I/O for LiveKit. Keep Interaction + Attention + heartbeat + events stream subprocess + three-layer config merge. Per-turn flow: STT text in → `agent.astream_events(...)` → final text out → TTS.
   - `llm_adapter.py` — `DeepagentsLLM(livekit.agents.llm.LLM)` wrapping the deepagents CompiledStateGraph for LiveKit's AgentSession. Translates `chat_ctx` ↔ deepagents `messages`. Streams response back via LiveKit's expected ChatStream interface.
   - `main.py` — LiveKit Agents `WorkerOptions(entrypoint_fnc=...)` constructing VoiceSession per room.
   - `pyproject.toml` — add `deepagents`, `langchain`, `langchain-google-vertexai`, `langgraph` alongside livekit deps.
   - tests for the LLM adapter + VoiceSession.
   
   Voice runtime entity ready (id `69f3b7fc97300b115e7236a0`); service token at `indemn/dev/shared/runtime-voice-service-token`. Repoint deployment image once v2 builds.

After both: TD-1 done-test verification + close. Then TD-2 cascade activation begins.

**Touched (Session 14):**

*indemn-os commits to main (3 + voice v1):*
- `1026d78` (fork) `fix(queue+activities): unjam dispatch + tolerate malformed rows (Bug #38, Bug #37 follow-on)`
- `c36969b` (fork) `fix(queue): sort dispatch sweep pending-first (Bug #38 followup)`
- `96684d5` (fork) `fix(harness): handle synthetic kernel-internal entity_types (Bug #41)`
- `c87376d` (this thread) `feat(adapters): Drive fetch_documents + Slack adapter (TD-1 sub-pieces 4+5)`
- `62f47f9` (this thread) `feat(harnesses): voice-deepagents — LiveKit Agents harness for voice (TD-1 sub-piece 7)` — **voice v1, will be replaced**

*operating-system commits (in this end-of-session protocol commit):*
- `projects/customer-system/CURRENT.md` rewrite
- `projects/customer-system/SESSIONS.md` Session 14 entry (this entry)
- `projects/customer-system/os-learnings.md` updates: Bug #42 reframe + #43 close + #44 add + #45 add
- `projects/customer-system/artifacts/2026-04-30-slack-adapter-design.md` (NEW)
- `projects/customer-system/artifacts/2026-04-30-voice-deepagents-runbook.md` (NEW; describes v1 — will need update after v2 rebuild)
- `projects/customer-system/skills/log-touchpoint.md` (NEW)
- `projects/customer-system/CLAUDE.md` (Journey § 5: Session 14 entry)

*OS state created (live in dev OS):*
- ReviewItem entity + Reviewer role (Craig assigned)
- SlackMessage entity (16 fields)
- voice-deepagents-dev runtime entity (id `69f3b7fc97300b115e7236a0`) + service token in AWS Secrets
- Slack Integration entity (id `69f3bb5097300b115e7236dd`, status active, secret_ref `indemn/dev/integrations/slack-oauth`)
- Slack bot_token in AWS Secrets at `indemn/dev/integrations/slack-oauth`
- Email-Fetcher / Meeting-Fetcher / Drive-Fetcher actors + roles + skills (all active, autonomous)
- log-touchpoint skill record + assigned to OS Assistant
- Document.external_ref field + Document.source enum extended
- 493 new Drive Documents from backfill
- 326 new Email entities from Email Fetcher's first run
- async-deepagents-dev runtime + chat-deepagents-dev runtime llm_config flipped to gemini-3-flash-preview/global
- Email-Classifier (now llm_config inheriting gemini-3-flash-preview), TS unchanged, IE picked up new model

---

## Session 13 — 2026-04-29 — Comprehensive roadmap alignment (TD-1 through TD-11)

**Objective:** Continue from Session 12. Test the new shared-context hydration system. Discuss the roadmap holistically — get foundational alignment on what we're actually going to build, in what order, and how each piece works in practice. Per Craig: dive deep into the roadmap, attack it aggressively, deliver something tangible to the team. Avoid the prior failure mode of "fuzzy on what's tangibly going to be accomplished."

**Parallel sessions during:** None — Session 13 was a single-thread alignment session in the roadmap worktree.

**Outcome:**

- **Roadmap restructured as 11 Tangible Deliverables (TD-1 through TD-11)**, replacing the prior Phase A → F structure. Same vision, same work, different organization. Phases were fuzzy on what's tangibly shipped to whom; TDs make it explicit. (`74b6012`)
- **TD-1 detailed at full fidelity (~180 lines)** — 4 source adapters + 4 scheduled fetcher actors + manual entry via per-actor assistant. Per-event Touchpoints (1:1 with source-events). Slack adapter NEW build (direct API, all channels, no DMs initially). Drive pull-all + lazy-classify. Pre-flight Bug #36/#37 cleanup. (`64830cd`)
- **TD-2 detailed at full fidelity (~170 lines)** — 7-associate cascade (EC, MC, SC, TS gains Deal-creation, IE, Proposal-Hydrator, Company-Enricher) + ReviewItem universal-escape-valve pattern. Bottom-up activation. Done-test = systematic historical replay. (`605dc01`)
- **TD-3 detailed at full fidelity (~280 lines)** — React+Vite+shadcn UI matching Ganesh's repo conventions (`https://github.com/ganesh-iyer/implementation-playbook`). 7 pages. Per-customer constellation page mirrors trace-showcase HTML 5-section spine (single-scrolling, inline timeline expand). Role-aware personalized dashboard. Persistent assistant across all pages. (`0941968`)
- **TD-4 through TD-11 structurally aligned** (~30-70 lines each — sufficient to start work; deeper detail filled in when each TD is approached). (`8310734`)
- **Where-we-are-now refresh + deepagents-skills-layer drop sync** (`e5c2bfb`, `4d7b648`)

**Major architectural decisions (full list in INDEX.md § Decisions; load-bearing ones below):**

- **Tangible-deliverable framing for roadmap** — TD-1 through TD-11 with continuous threads
- **7-associate cascade architecture** — one associate per significantly-different (trigger, entities, context, skill) per Craig's principle. EC, MC, SC, TS (gains Deal-creation), IE, Proposal-Hydrator, Company-Enricher
- **ReviewItem universal-escape-valve pattern** — any associate creates one when uncertain; never blocks; reviewing IS training data; replaces "needs_review" entity-state pattern except for source-classifier total-failure
- **Per-event Touchpoints** — 1:1 with discrete source-events (Email, Meeting, SlackMessage); threading is metadata; new replies are SEPARATE Touchpoints
- **Slack adapter design** — direct Slack API (not agent-slack); all channels via Slack admin; no DMs initially (team uses channels for customer chatter); polling 5min then Events API push later; per-message granularity
- **Drive ingestion design** — pull all of Drive; Documents source-agnostic; lazy classification (at IE touchpoint extraction or manual via UI or future workflow-driven); folder context as hint
- **Manual entry via per-actor assistant** — uses existing OS kernel-level Deployment pattern; new domain skill `log-touchpoint`; no special infrastructure
- **TD-3 stack: React + Vite + shadcn** matching Ganesh's customer-success repo conventions; direct OS API (no adapter); reuse existing chat-deepagents + voice-deepagents harnesses
- **TD-4 process: conversational research via Claude Code** — not auto-mining; phase 1 research determines actual stages; phase 2 per-stage deep-dive; phase 3 mostly-static refinement
- **Artifact Generator: one associate, Playbook-driven, multi-deployment** (async + realtime chat + realtime voice). Drafted email = Email entity with `status: drafting`.
- **TD-9 evaluations: LangSmith API directly for now**; Path 3 kernel-adapter integration deferred to TD-11
- **TD-10 Commitment-Tracker: both event + schedule triggers; OS queue + Slack DM notifications; Commitment-level escalation chain with Role defaults**
- **TD-11 detailed alignment deferred to `../product-vision/`** (the OS-level project)
- **Stage progression UI is descriptive, not prescriptive** — stage transition criteria defined later in TD-4 research, not in TD-3 UI gating

**Resolved long-running open design questions:**
- Document-as-artifact for emails → Email with `status: drafting`
- Playbook hydration mechanism → mostly-static, conversational refinement
- Touchpoint↔Deal chicken-and-egg → TS atomically creates Deal + empty Proposal when external scope + no active Deal
- Internal Touchpoints contributing to Proposal → YES, treated same as external
- Multi-Deal ambiguity for internal → assigns to latest + creates ReviewItem

Carried forward (fold into TD-4 research):
- Opportunity vs Problem entity
- 12 sub-stages with archetypes (Kyle's Apr 24 ask)
- Origin/referrer tracking

**Handoff to next session:**

Use `PROMPT.md` as the kickoff prompt. Objective slot:

> *Execute TD-1 — adapters running cleanly + historical hydration. Start with pre-flight cleanup (bulk-delete Bug #36's 500 emails + 6 meetings; delete Bug #37's 2 malformed Email rows). Create ReviewItem entity + Reviewer role (pre-flight infrastructure for TD-2). Then activate the four scheduled fetcher actors in bottom-up order: Email-Fetcher (5min), Meeting-Fetcher (15min, with 30-day backfill), Drive-Fetcher (hourly, with full crawl). The Slack adapter is a multi-session NEW build — start design + scaffold this session, finish in subsequent sessions. Verify each step manually before activating recurring. EC/TS/IE remain suspended — TD-1 does NOT activate the cascade. Touch all relevant docs at end of session per CLAUDE.md § 7. See `roadmap.md § TD-1` for full architecture detail.*

**Key TD-1 risks to watch:**
- Cascade-firing-before-ready: pre-flight cleanup MUST complete before any actor activation
- Slack adapter is the largest NEW build — likely multi-session work
- Voice harness refinement may be needed (per Craig: not actually tested or used much)

**Touched:**
- Modified: `roadmap.md` (entire restructure + all 11 TD detail sections; ~580 line growth net), `CLAUDE.md` (light — pipeline-associates section, journey Session 12 entry expanded), `CURRENT.md` (rewrite end-of-session)
- Created: this Session 13 entry in SESSIONS.md
- No entity changes in dev OS, no parallel kernel-fix work, no skill updates

---

## Session 12 — 2026-04-29 — Bug #35/#36/#37 closeouts + Armadillo trace + Hard Rule #1 inversion + shared-context hydration redesign

Three parallel threads ran on this Session 12. The combined output is captured below. The full INDEX.md Status entry has the comprehensive narrative; this is the per-thread breakdown.

**Thread 1 — Main customer-system session: Armadillo trace + Hard Rule #1 inversion (EC v9)**

*Objective:* Continue Phase B1. With Bug #35 hopefully resolved by the parallel kernel-fix thread, take a real new-prospect (Armadillo Insurance) through the OS as designed and verify the autonomous Email Classifier flow works end-to-end. Surface design gaps along the way.

*Outcome:*
- Hard Rule #1 inverted in EC: "Never auto-create a Company" → "Resolve before create" (resolve-first IS the dedup defense, now reliable post-Bug-#34/#36). Step 5 decision table updated so 0/0 outcome auto-creates Company + Contact instead of stalling at `needs_review`. EC v9 deployed (`9eef4959ae701614`).
- Armadillo Insurance traced end-to-end as designed. Origin: Matan Slagter (CEO) → David Wellner (COO) intro at InsurtechNY (Apr 2). Discovery call Apr 28. Autonomous flow created Company `69f22186…444d` + 2 Contacts. Manual orchestration created Deal `69f223cc…4470` + linked Touchpoints (Deal-creator associate gap surfaced). 14 entities extracted by IE against DISCOVERY Playbook.
- Artifacts shipped to Kyle: yesterday's roadmap doc (Drive + Slack) + Armadillo trace HTML (Slack file attachment, not Drive — Drive renders HTML as raw source). Caveat-framed: still in flux, building intuition.
- Brain-dump request sent to Kyle for TFG / John Scanland — second prospect for next trace pass.

**Thread 2 — Parallel kernel-fix session: Bugs #35 + #36 + #37 closed, then deepagents skills layer dropped entirely**

*Objective:* Close Bug #35 (deepagents skill discovery — Session 11's identified blocker) and any related kernel issues that surface during root-cause investigation.

*Outcome:*
- **Bug #35 closed twice over** — first via two stacked fixes (commits `8141a80` absolute-path return, `2ba6f63` yaml.safe_dump for frontmatter). Live-verified. Then **the whole deepagents skills layer was dropped** (commit `7281b83` `refactor(harness): load skills via CLI in DEFAULT_PROMPT`). Reasoning: deepagents filesystem-skills was designed for "many skills, agent dynamically chooses" — our associates have ONE skill each, so progressive-disclosure-via-filesystem is the wrong fit. New canonical pattern: agent runs `execute('indemn skill get <name>')` (system-prompt directive); skill content arrives as tool result on turn 1, stays in agent's message history; symmetric with how associates load entity skills + everything else. Eliminates Bug #35 class entirely (no path resolution against backend root_dir, no YAML escaping, no SKILL.md format). The two stacked fixes are no longer load-bearing — the layer they fixed is gone.
- **Bug #36 closed** — Gmail + Calendar `fetch_new` adapters silently ignored `until` parameter. Deeper root cause: `**params` on public adapter methods silently absorbed any unknown kwargs. Fix plumbs `until` end-to-end (Gmail `before:` operator + sub-day filter, Meet `timeMax`-equivalent), replaces `**params` with `**unknown_params` raising `AdapterValidationError`. 15 new unit tests (commit `477a98f`). Outlook propagation: commit `3fc4b55`.
- **Bug #37 closed** — Email list endpoint poisoned by malformed `company` field. Opt-in tolerance via `_DomainQuery.to_list(skip_invalid=False)` — strict default preserved for migrations/audit, user-facing list opts in (commit `a5aa89f`). 2 bad rows identified for cleanup.

**Thread 3 — Parallel hydration-redesign session: shared-context layering**

*Objective:* Solve the meta-problem of 500K-token hydration. Sessions had been reading Track 1 + Track 2 (~500K tokens) before any work, leaving little headroom for actual building. Design a single steady-state prompt usable across N parallel + N sequential sessions that hydrates the shared mental model efficiently while preserving deep understanding of OS + customer-system vision.

*Outcome:*
- `customer-system/CLAUDE.md` rewritten as comprehensive shared-mind doc — what we're building / how / why / architecture / journey / foundations / best practices / index. Replaces the prior bloated cumulative-history version.
- `customer-system/CURRENT.md` created — fast-changing state file (50-100 lines). Rewritten each session.
- `customer-system/SESSIONS.md` created (this file) — append-only per-session log.
- `customer-system/PROMPT.md` created — the session-start prompt template. Sets always-loaded reads + objective + execution discipline.
- Design captured in `docs/plans/2026-04-28-shared-context-hydration-design.md`.
- Total always-loaded hydration reduced ~5x (500K → ~95K).

**Combined parallel-sessions during:** Three threads (above) plus an unrelated parallel devops session (commit `345cd51`) that shipped a similar hydration-first handoff prompt for the devops project.

**Handoff to next session:**
- Use `PROMPT.md` as the session-start prompt. Test the new layered hydration model.
- Phase B1 work continues: drain remaining test cases, reactivate TS + IE, watch full cascade end-to-end on next live email.
- TFG / John Scanland is the next planned trace target (waiting on Kyle's brain dump).
- Cleanup tasks: 500 emails + 6 meetings from Bug #36 side-effect; 2 malformed Email rows from Bug #37 data side. Either clean up or accept-fix-forward.
- 5 new design gaps logged (Deal-lifecycle automation, Employee entity_resolve, Company hydration on auto-create, Contact richer-field parsing, internal docs spanning multiple prospects). Highest-priority is Deal-lifecycle automation.

**Touched (combined):**
- Created (Thread 3): `customer-system/CURRENT.md`, `customer-system/SESSIONS.md`, `customer-system/PROMPT.md`, `docs/plans/2026-04-28-shared-context-hydration-design.md`
- Rewrote (Thread 3): `customer-system/CLAUDE.md`
- Updated (Thread 1): `customer-system/INDEX.md` (Session 12 entry), `customer-system/skills/email-classifier.md` (v9), `customer-system/os-learnings.md` (5 new entries)
- Created (Thread 1): `customer-system/artifacts/2026-04-29-armadillo-followup-email-draft.md`, `customer-system/artifacts/2026-04-29-armadillo-trace-showcase.html`
- Kernel commits (Thread 2): `8141a80`, `2ba6f63`, `477a98f`, `a5aa89f` on indemn-os main
- Material in dev OS (Thread 1): Armadillo Company `69f22186…444d` + Deal `69f223cc…4470` + 2 Contacts + 2 Touchpoints + 14 extracted entities

---

*Future sessions append new entries above this line.*
