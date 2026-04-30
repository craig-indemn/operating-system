# Customer System — CURRENT

> **Fast-changing state.** What just happened, what's in flight, parallel sessions, blockers, next steps. Rewritten every session. Read this *after* CLAUDE.md to know where things actually stand right now.

**Last updated:** 2026-04-30 (end of Session 14 — TD-1 substantially executed; voice-deepagents canonical rebuild + Slack live-fetch debug pending for next session)

---

## Top of roadmap

**TD-1 ~85% complete.** Sub-pieces 1, 2, 3, 5, 8 done end-to-end. Sub-piece 4 (Slack) — adapter built + deployed + Integration entity created + transitioned to active, but `resolve_integration()` lookup is not finding it (live fetch returns "No messaging integration available"). Sub-piece 6 (`log-touchpoint` skill) — uploaded + assigned to OS Assistant; chat-side end-to-end test pending. Sub-piece 7 (Voice harness) — v1 BUILT BUT WRONG SHAPE (uses `livekit.agents.Agent` with single custom `execute` tool — does NOT use deepagents framework, no Interaction/Attention, no harness_common). Per `docs/architecture/realtime.md` + `associates.md`, v1 needs DELETE + REBUILD against the canonical pattern (deepagents + Interaction + Attention + LiveKit-as-I/O-only + DeepagentsLLM adapter).

After TD-1 closes: TD-2 cascade activation begins (already designed in Session 13).

---

## Pipeline associate states (Session 14 changes)

| Associate | State | Notes |
|---|---|---|
| Email Classifier (EC) | **suspended** | Unchanged. Will activate in TD-2. |
| Touchpoint Synthesizer (TS) | **suspended** | Unchanged. Will gain Deal-creation in TD-2. |
| Intelligence Extractor (IE) | **active** | Unchanged. Now inherits gemini-3-flash-preview from runtime default (was 2.5-flash). |
| **Email Fetcher** (NEW Session 14) | **active** | id `69f2bf30942e5629f07a8313`. Cron `*/5 * * * *`. Inherits gemini-3-flash-preview/global. **Verified end-to-end: trace `019ddf95-d579-7390-9483-beece987389f` 18:10-18:15Z fetched 326 new emails, 7 LLM turns all `finish=STOP`.** Currently autonomous and running. |
| **Meeting Fetcher** (NEW Session 14) | **active** | id `69f39ec6c0b340cf765a38d6`. Cron `*/15 * * * *`. Activated 18:46Z; first cron at 19:00Z. 30-day backfill done: fetched=396 created=2 skipped=394 errors=0. |
| **Drive Fetcher** (NEW Session 14) | **active** | id `69f3abbe268936150b46a0fa`. Cron `0 * * * *`. Activated 19:21Z; first cron at 20:00Z. 30-day backfill done: fetched=1161 created=493 skipped=668 errors=0. |
| **Slack Fetcher** | **NOT YET CREATED** | Adapter built + deployed. Integration entity active. fetch_new dispatch BLOCKED — see Blockers. Once unblocked, build slack_fetcher role + skill + actor. |
| **Reviewer role** | wired | Watch `ReviewItem created`. Craig assigned. Smoke-tested end-to-end Session 14. |

**4 NEW associates designed in Session 13's TD-2 alignment** — to be built when TD-2 executes (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher).

---

## Material state in dev OS (Session 14 changes)

**Hydrated customer constellations** (carried forward unchanged):
- GR Little, Alliance Insurance, Armadillo Insurance.

**New entities created Session 14:**
- **ReviewItem entity** — collection `review_items`, 9 fields incl. polymorphic target_entity_type/id, 8-value enum reason, state machine open→in_review→resolved/dismissed. Smoke-tested.
- **SlackMessage entity** — collection `slack_messages`, 16 fields, state machine received→classified/irrelevant/needs_review→processed. external_ref = `{channel_id}:{slack_ts}`.
- **Document.external_ref** field added (sparse+unique+indexed) for Drive fetch_new dedup.
- **Document.source enum** extended with `slack_file_attachment`.
- **493 new Drive Documents** from 30-day backfill.
- **326 new Email entities** from Email Fetcher's first autonomous run.
- 2 new Meetings from 30-day backfill (most already in DB; 394 deduped).
- **Slack Integration entity** — id `69f3bb5097300b115e7236dd`, owner=org, system_type=messaging, provider=slack, secret_ref=`indemn/dev/integrations/slack-oauth`, status=active.
- **voice-deepagents-dev runtime entity** — id `69f3b7fc97300b115e7236a0`, kind=realtime_voice, framework=livekit, llm_config=gemini-3-flash-preview/global. Service token at `indemn/dev/shared/runtime-voice-service-token`.

**Cleanup completed:**
- Bug #36 side-effect: 500 emails + 5 unrelated meetings deleted (Armadillo email + meeting preserved).
- Bug #37 rows: deleted by fork session via the new bulk-delete skip_invalid path.

**Skill records uploaded:**
- `email-fetcher`, `meeting-fetcher`, `drive-fetcher` — operating skills for the 3 fetcher actors.
- `log-touchpoint` — manual-entry skill, assigned to OS Assistant (skills count 23→24).

**Runtime defaults flipped to gemini-3-flash-preview/global:**
- `async-deepagents-dev` — flipped Session 14. All 23+ async associates now inherit. IE picked up the new model on its next run.
- `chat-deepagents-dev` — flipped Session 14 for Bug #42 consistency.

---

## Parallel sessions

**Session 14's parallel fork session** — opened at session start to fix Bug #38/#37/#41. Closed mid-session with 3 indemn-os commits (`1026d78`, `c36969b`, `96684d5`) + 2 operating-system commits. All bugs verified fixed live. Fork is closed.

**Currently no active parallel sessions.** Next session resumes single-thread.

---

## Blockers (carried into next session)

### 🔴 Blocker #1 — Slack live fetch returns "No messaging integration available"

**Symptom:** `POST /api/slackmessages/fetch-new` (with body `{"limit": 5}`) returns:
```
{"error":"InternalServerError","type":"AdapterNotFoundError","message":"No messaging integration available. Create one with: indemn integration create --system-type messaging ..."}
```

**State at close:**
- Slack Integration entity exists: id `69f3bb5097300b115e7236dd`, owner_type=org, owner_id=`69e23d586a448759a34d3823`, system_type=`messaging`, provider=`slack`, status=`active`, secret_ref=`indemn/dev/integrations/slack-oauth`. Walked through state machine `configured → connected → active`.
- Bot token stored at AWS Secret `indemn/dev/integrations/slack-oauth` (key `bot_token`, len=57). Verified retrievable.
- SlackAdapter registered in kernel as (system_type="messaging", provider="slack") via `register_adapter("messaging", "slack", SlackAdapter)` in `kernel/integration/adapters/slack.py`.
- SlackAdapter import added to `kernel/integration/adapters/__init__.py`. Live deployed (commit `c87376d` → indemn-api).
- fetch_new capability activated on SlackMessage with config `{"system_type":"messaging"}`.

**Next step (priority for next session):** debug `kernel/integration/dispatch.py::resolve_integration()` — what filters does it apply when looking up an Integration by `system_type`? Likely candidates:
- Status filter expecting something other than `active` (e.g., `connected`, or both)
- Provider filter requiring something we didn't set
- Org-scope mismatch — auth context org vs Integration owner_id
- The kernel's adapter registry lookup may key on `(system_type, provider)` tuple but the API caller only passes `system_type`

The Slack token Craig provided is also exposed in plain conversation text — **rotate it** (regenerate at api.slack.com → re-store in AWS Secrets at the same path).

### 🔴 Blocker #2 — voice-deepagents v1 is structurally wrong; needs DELETE + REBUILD

**Symptom:** Current voice-deepagents v1 (committed at indemn-os main `62f47f9`) uses `livekit.agents.Agent` with a single custom `execute` tool. It does NOT use:
- The `deepagents` library (no `create_deep_agent`, no LangGraph state graph, no built-in `write_todos`/`read_file`/`task` tools)
- The `harness_common` modules (`interaction.py`, `attention.py`, `runtime.py`, `backend.py`)
- The Interaction + Attention entity lifecycle from `docs/architecture/realtime.md`
- Three-layer LLM config merge from `kernel/temporal/activities.py::load_actor`
- Filesystem skill progressive disclosure (chat-deepagents pattern; chat hasn't migrated to CLI-load yet)

**Per Craig's directive** — voice should be the same agent as chat-deepagents, just with audio I/O instead of text WebSocket.

**Next step (priority for next session):**
1. Delete v1 files: `harnesses/voice-deepagents/{tools.py, assistant.py, main.py, pyproject.toml, Dockerfile, tests/}` (note: `pyproject.toml` and `Dockerfile` may be partially reusable — review).
2. Rebuild v2 mirroring `harnesses/chat-deepagents/` structure:
   - `agent.py` — copy chat-deepagents/agent.py verbatim (deepagents `create_deep_agent`, three-layer llm_config merge, voice-specific DEFAULT_PROMPT)
   - `session.py` — VoiceSession class mirroring ChatSession (Interaction lifecycle, Attention with heartbeat, agent + checkpointer, `indemn events stream` subprocess for mid-conversation awareness)
   - `llm_adapter.py` — `DeepagentsLLM(livekit.agents.llm.LLM)` adapter that wraps a deepagents CompiledStateGraph for LiveKit's AgentSession (translates `chat_ctx` ↔ deepagents `messages`; invokes `agent.ainvoke()`; streams response back as `ChatStream`)
   - `main.py` — LiveKit Agents `WorkerOptions(entrypoint_fnc=...)` that constructs VoiceSession per room, spawns LiveKit AgentSession with DeepagentsLLM + Deepgram STT + Cartesia TTS + Silero VAD + EnglishModel turn detector
   - `pyproject.toml` — add `deepagents`, `langchain`, `langchain-google-vertexai`, `langgraph` alongside livekit deps
   - `Dockerfile` — same plus deepagents/langchain installed
   - tests for the LLM adapter + VoiceSession
3. Voice runtime entity already exists (id `69f3b7fc97300b115e7236a0`) — repoint to the new image once built.
4. Voice service token already in AWS Secrets at `indemn/dev/shared/runtime-voice-service-token`.

Architecture summary:
- LiveKit handles audio I/O + STT (Deepgram) + TTS (Cartesia)
- DeepagentsLLM adapter receives transcribed text from STT, invokes the deepagents agent (which has full toolset: execute, write_todos, read_file, etc., plus loads skills via filesystem progressive disclosure), returns final text response
- AgentSession routes the response text to TTS → audio out
- VoiceSession manages Interaction + Attention lifecycle (same as ChatSession)

---

## What just shipped (Session 14)

Massive session. TD-1 sub-pieces 1, 2, 3, 5, 8 closed end-to-end; 4 + 6 + 7 partial.

### TD-1 work
- **Pre-flight cleanup:** Bug #36 cleanup (500 emails + 5 meetings deleted; Armadillo preserved). Bug #37 rows deleted by fork session.
- **ReviewItem entity + Reviewer role** — created, Craig assigned, smoke-tested end-to-end (created → watch fired → message routed to reviewer queue → resolution flow worked).
- **Email Fetcher** — role + skill + actor (`69f2bf30942e5629f07a8313`); 5-min cron; activated end-to-end with verified gemini-3-flash-preview run (326 emails fetched).
- **Meeting Fetcher** — role + skill + actor (`69f39ec6c0b340cf765a38d6`); 15-min cron; 30-day backfill (per-user via direct API to dodge CLI 600s timeout) returned 396 fetched / 2 created / 394 skipped / 0 errors.
- **Drive adapter (NEW kernel build)** — `fetch_documents` method on GoogleWorkspaceAdapter (per-user Drive paginate by pageToken, dedup by drive_file_id, format Document-shaped dicts, `external_ref = drive_file_id`). 6 unit tests in `TestFetchDocumentsContract` — GREEN. `external_ref` field added to Document. fetch_new capability activated. Deployed (indemn-os commit `c87376d`). 30-day backfill: 1161 fetched / 493 created / 668 skipped / 0 errors.
- **Drive Fetcher** — role + skill + actor (`69f3abbe268936150b46a0fa`); hourly cron; activated.
- **Slack adapter (NEW kernel build)** — `kernel/integration/adapters/slack.py`: SlackAdapter class via Slack Web API (httpx-based); `conversations.list` (public+private, no DMs, paginate by cursor); `conversations.history` (paginate by cursor, `oldest`/`latest` from `since`/`until`); strict `**unknown_params` rejection; rate-limit + auth error typing; SlackMessage-shaped dicts with `external_ref = "{channel_id}:{slack_ts}"`. 9 unit tests in `TestSlackAdapterContract` — GREEN. Self-registered via `register_adapter("messaging", "slack", ...)`. SlackMessage entity created (16 fields + state machine). fetch_new capability activated. Deployed (indemn-os commit `c87376d`).
- **Document.source enum** — added `slack_file_attachment`.
- **log-touchpoint skill** — written, uploaded to dev OS, assigned to OS Assistant (skills count 23→24).
- **voice-deepagents v1** — built but architecturally wrong (single custom `execute` tool, NOT deepagents); committed `62f47f9` but flagged for DELETE + REBUILD next session.

### Bug fixes (parallel fork session early in Session 14)
- **Bug #38** (queue dispatch jam — uncaught WorkflowAlreadyStartedError + stale message retries + watch creation for suspended actors). Three coupled root causes, one PR. Indemn-os commits `1026d78` + `c36969b`. 16 new unit tests. Verified live: 1015 EC + 28 TS + 1 EF parked cleanly.
- **Bug #37 follow-on** (bulk-delete poison on malformed entities). `skip_invalid=True` propagated to bulk activities + DELETE-cleanup pass. Bundled in `1026d78`. Live verified: 2 stuck Bug #37 rows successfully deleted.
- **Bug #41** (harness `_scheduled` entity-load CLI failure). `_load_message_context` extracted with `entity_type.startswith("_")` branch. Indemn-os commit `96684d5`. 6 new unit tests.

### Bug #42 reframe + resolution
Original "agent reads skill but doesn't act" framing was WRONG. Actual root cause: **Gemini 2.5 Flash returns `MALFORMED_FUNCTION_CALL` on the deepagents `write_todos` schema**. Verified across 3 LangSmith traces — `default_api.WriteTodosTodos(...)` Pythonic syntax instead of valid JSON. Resolution: switched to `gemini-3-flash-preview/global`. Verified: 7 LLM turns, all `finish=STOP`, agent fetched 326 emails. **Then flipped both runtime defaults (async-deepagents-dev + chat-deepagents-dev) to gemini-3-flash-preview/global** — affects 23+ associates including IE. **LangSmith query gotcha discovered:** `order: "DESC"` (uppercase) returns HTTP 422 silently; must use `"desc"` lowercase. The fork's earlier "0 traces visible" symptom was this query bug — traces were arriving the entire time.

### Architectural / design artifacts (this session)
- `projects/customer-system/artifacts/2026-04-30-slack-adapter-design.md` (265 lines) — full Slack architecture for execution.
- `projects/customer-system/artifacts/2026-04-30-voice-deepagents-runbook.md` (deployment + verification, but **the v1 it describes needs rebuild** per realtime.md canonical pattern).

### Bugs logged (open or partial)
- **Bug #43** (Drive adapter scope) — closed in-session ✓
- **Bug #44** — voice-deepagents harness existed at session start as "doesn't exist"; v1 built but architecturally wrong; per-actor default_assistant pattern confirmed deferred (shared OS Assistant is fine for now per Craig).
- **Bug #45 (NEW, OPEN)** — Slack `resolve_integration()` lookup not finding our active Integration. Symptom + state captured above in Blocker #1.

---

## Open design questions (carried forward)

These mostly fold into TD-4's research session per the Session 13 alignment:

1. **Opportunity vs Problem entity** — surfaces from TD-4 research observing unmapped pain
2. **Document-as-artifact pattern for emails** — RESOLVED in TD-5 alignment (Email entity with `status: drafting`)
3. **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle's Apr 24 ask) — research-driven in TD-4
4. **Origin / referrer tracking** — surfaces from TD-4 research
5. **Playbook hydration mechanism** — RESOLVED in TD-4 alignment (mostly static, conversational refinement)
6. **Drive content extraction** — current Drive adapter populates metadata only; Google Docs/Sheets/Slides export, PDF text extraction, image OCR are future enrichment passes (separate `enrich_documents` capability or content-extraction skill on Drive-Fetcher cron)

---

## Recent OS commits to indemn-os main

- `62f47f9` — `feat(harnesses): voice-deepagents — LiveKit Agents harness for voice (TD-1 sub-piece 7)` — **v1 to be DELETED next session per Blocker #2**
- `c87376d` — `feat(adapters): Drive fetch_documents + Slack adapter (TD-1 sub-pieces 4+5)` — Drive working live; Slack adapter deployed but live fetch blocked by Bug #45
- `96684d5` — Bug #41 (harness `_scheduled` entity-load fix) — fork session
- `c36969b` — Bug #38 followup (sweep ordering) — fork session
- `1026d78` — Bug #38 + #37 follow-on (queue dispatch unjam + bulk-delete skip_invalid) — fork session
- All Session 12-13 commits prior

---

## Operating-system worktree state at close

**Branch:** `os-roadmap` (this worktree at `.claude/worktrees/roadmap/`).

**Commits ahead of origin:** 13 (all from Sessions 12-14 — push at end of session protocol).

**Uncommitted changes (will commit in protocol):**
- `M projects/customer-system/os-learnings.md` — Bug #42 reframe + #43 close + #44 add + #45 add + Drive/Slack/voice notes
- `?? projects/customer-system/CURRENT.md` — this rewrite
- `?? projects/customer-system/SESSIONS.md` — Session 14 entry to append
- `?? projects/customer-system/artifacts/2026-04-30-slack-adapter-design.md` — Slack design doc
- `?? projects/customer-system/artifacts/2026-04-30-voice-deepagents-runbook.md` — voice runbook (note: describes v1 — update to point at v2 rebuild)
- `?? projects/customer-system/skills/log-touchpoint.md` — manual-entry skill content
- `?? .claude/scheduled_tasks.lock` — runtime artifact (skip)

---

## Next session — focus

**Use `PROMPT.md` as the kickoff prompt** with this objective slot:

> *Continue TD-1 from Session 14 close. Two priorities: (1) Debug Bug #45 — Slack `resolve_integration()` is not finding our active Slack Integration (id `69f3bb5097300b115e7236dd`). Read `kernel/integration/dispatch.py::resolve_integration()` to see what filters apply. Likely status / org_id / provider mismatch. Once resolved: run 90-day Slack backfill, build slack_fetcher role + skill + Slack-Fetcher actor (every 5 min), activate. (2) Voice-deepagents canonical rebuild — DELETE the v1 files at `harnesses/voice-deepagents/{tools.py, assistant.py, main.py, tests/test_tools.py}` and REBUILD per `docs/architecture/realtime.md` + `docs/architecture/associates.md`. Mirror chat-deepagents structure: `agent.py` (copy chat-deepagents/agent.py with voice DEFAULT_PROMPT, deepagents `create_deep_agent` + three-layer llm_config), `session.py` (mirror ChatSession with Interaction + Attention + heartbeat + events stream), `llm_adapter.py` (DeepagentsLLM wrapping the agent for LiveKit AgentSession), `main.py` (LiveKit WorkerOptions). Voice-deepagents-dev runtime entity already exists (id `69f3b7fc97300b115e7236a0`); service token at `indemn/dev/shared/runtime-voice-service-token`. After both: TD-1 done-test verification (all 4 fetcher actors active + manual entry working via OS Assistant chat path). Touch all relevant docs at end-of-session per CLAUDE.md § 7.*

**Key risks to watch:**
- The Slack Integration debug may surface a deeper pattern (e.g., kernel adapter registry uses (system_type, provider) but API caller passes only system_type). Could be a small fix or a kernel-fork item.
- Voice-deepagents canonical rebuild is substantial (DeepagentsLLM adapter + Interaction/Attention wiring + tests). Could take most of a session.
- Slack token Craig provided was in plain text — should be **rotated** before going live.

**TD-1 done-test (full version in roadmap.md):**
- All 4 fetcher actors active with `trigger_schedule` running ✓✓✓✗ (Slack pending)
- New entities flow in within configured cadence ✓✓✓✗
- Backfills complete: 30-day Meeting ✓; full Drive crawl (30d done, full crawl is more) ~; 90-day Slack ✗
- Bug #36/#37 cleanup verified ✓
- Manual entry working via OS Assistant `log-touchpoint` skill — skill assigned, end-to-end chat test pending
- All entities sit at `received`/`logged` — cascade NOT activated ✓ (EC/TS suspended; IE was active but only on Touchpoints which haven't been created since suspension)

After TD-1 closes: TD-2 begins (cascade activation, progressive). TD-3 begins (UI build) in parallel once TD-2 has data flowing.

---

*This file is rewritten every session. Don't append — replace. The history lives in SESSIONS.md.*
