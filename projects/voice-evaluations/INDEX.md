# Voice Evaluations

Incorporating voice agents into the Indemn evaluation framework. Currently, only web agents are evaluated via the evaluation harness and displayed in the copilot dashboard. Voice agents use a completely different backend (voice-livekit calling OpenAI directly, NOT bot-service) and their data lives in MongoDB + LiveKit + S3 rather than LangSmith. The goal is to bridge this gap — enabling evaluation of voice agents through the existing harness, surfacing voice analytics in the Observatory, and building the OS-level skills (LiveKit, updated MongoDB) needed to interact with voice data.

## Status
**Session 2026-02-27-a** (COMPLETE): Project created. Comprehensive research across 6 repos, MongoDB prod data, Slack/email, LiveKit exports. Design document written with 5-phase roadmap.

**Session 2026-02-27-b** (COMPLETE): Design review and iteration. Ran 5-agent parallel code review that verified every claim in the design. Found and fixed 17 issues. Design document fully grounded — zero assumptions.

**Session 2026-02-27-c** (COMPLETE): Implementation plan created and executed across all 5 waves (14 tasks). All code written and committed across 5 repos: voice-livekit (trace metadata), evaluations (transcript engine + API), indemn-observability (channel fix + Langfuse connector + evaluate UI + voice metrics), indemn-platform-v2 (transcript type in UI), operating-system (Langfuse skill + MongoDB patterns).

**Session 2026-02-27-d** (COMPLETE): Testing, code review, and bug-fixing. Full line-by-line code review across all 5 repos found 3 bugs in agent-written observatory code + several documentation inaccuracies — all fixed. Static verification all pass (Python compile, TypeScript, 79 unit tests). Browser testing: Evaluate button/dialog PASS, voice channel badge and transcript badge CANNOT VERIFY (need data ingestion + running a transcript eval).

**Session 2026-02-27-e** (COMPLETE): Committed all bug fixes across 3 repos. Ran transcript evaluation on web conversations — PASS (2 items, 76/102 criteria, 12/12 rubric). Federation build browser testing in copilot-dashboard — Transcript Criteria stat card PASS, evaluation scores display correctly. **Blocked on Langfuse credentials** for voice data ingestion into Observatory and remaining verification.

**Session 2026-03-02-a** (COMPLETE): Resumed project, audited git state across all repos. All implementation commits are local only (not pushed). Commit locations verified:
- **evaluations** (`main`): `c651b79` feat + `1eddab9` fix — 2 unpushed commits
- **voice-livekit** (`main`): `9df3389` trace metadata — 1 unpushed commit
- **indemn-platform-v2** (`main`): `ffcd1e9` transcript UI — 1 unpushed commit (+ 3 other COP-325 commits)
- **indemn-observability** (`demo-gic`): `e3fa4a4` feat + `1a54bab` fix — on feature branch, not on main

**Session 2026-03-02-b** (COMPLETE): Langfuse credentials confirmed working (1,142 live voice traces verified). Implemented Langfuse sync task + transcript evaluation fix. Initial sync: 16 traces → 620 runs, 11 matched / 5 unmatched. Hit bugs: Langfuse Z suffix requirement, limit=100 cap. Both fixed.

**Session 2026-03-02-c** (COMPLETE): Investigated all three sync discrepancies, fixed bugs, completed end-to-end testing:
1. **11→8 request_ids** (BUG): phone+time fallback returned latest request instead of closest match, causing N:1 collisions when same phone called repeatedly within 5-min window. Fixed with closest-by-time matching + exclude_request_ids dedup. After fix: 11 matched → 11 distinct request_ids (1:1).
2. **5 unmatched traces** (EXPECTED): No matching requests exist in dev MongoDB for those calls/times.
3. **0 TOOL observations** (EXPECTED): Dev Langfuse only has SPAN + GENERATION types. No TOOL-type observations in dev data.
4. **Voice conversations invisible to ingestion** (BUG): Voice requests store `conversation_start_time` as Unix timestamp float, not ISO string. Ingestion query used string comparison — voice requests never matched. Fixed with `$or` filter adding `createdAt` (Date type) fallback.
5. **API 500 on voice conversations** (BUG): `started_at` stored as float, API model expected string. Fixed by normalizing Unix timestamps to ISO strings in `build_observatory_document()`.
6. **Observatory UI verified**: Voice conversations appear with "voice" channel badge in Conversations tab. Conversation detail panel opens correctly with Messages and Full Trace tabs.

**Session 2026-03-02-d** (COMPLETE): End-to-end verification + scope fix.
1. **Transcript evaluation on voice** — triggered via API, completed: 1 voice conversation, 19/45 criteria (used wrong test set — faq bot criteria against voice conv, expected meaningless results). Backend pipeline confirmed working.
2. **Copilot Dashboard** — user verified transcript results visible with Transcript type badge in federation UI.
3. **Observatory UI** — user verified voice conversations with voice badge, detail panel working.
4. **Evaluate scope fix** — EvaluateDialog was disabled for voice because `botId` came from UI scope filter (always null). Root cause: `agent_id` not in API response (missing from MongoDB projection + response model) + proxy passed `bot_id` param but evaluations service expects `agent_id`. Fixed: added `agent_id` to projection/model/response, frontend reads from conversation data, proxy uses correct param name. Now filters test sets/rubrics to the selected conversation's agent.
5. **Voice agent has 0 test sets** — correct behavior, none created yet.

**Session 2026-03-02-e** (COMPLETE): Prod data testing + documentation.
1. **Prod Langfuse sync** — 266 traces → 17,326 runs, 258 matched (97%), 8 unmatched, 0 failed. Much better match rate than dev (97% vs 69%).
2. **Prod ingestion** (Feb 28, narrow window) — 84 conversations processed with reuse_classifications, 13 voice conversations visible in Observatory with voice badge, classifications, and Langfuse trace data (LLM calls + tool calls).
3. **Index fix** — wrapped Langfuse sync index creation in try/except (was timing out on prod MongoDB, blocking the entire sync pipeline).
4. **3 prod voice agents identified**: `695c3df0922e070f5e057517`, `697259edec2b21075fda6439`, `68e74763f060f50013a79d68`.

**Session 2026-03-03-a** (COMPLETE): Code review, fixes, and integration testing.
1. Code review (2 rounds), all fixes applied and verified across 4 repos.
2. Runtime bugs fixed (Pydantic date shadowing, BSON encoding).
3. Integration testing: Observatory API all pass, Evaluations API pass. Platform-v2 UI partially tested.

**Session 2026-03-03-b** (COMPLETE): Commits, branches, and UI testing.
1. **All review fixes committed** across 4 repos.
2. **Feature branches created**: evaluations→`feat/voice-transcript-evaluation` (4 commits), voice-livekit→`feat/langfuse-trace-metadata` (2 commits), platform-v2→`feat/transcript-type-ui` (2 commits). Main branches reset to pre-work state. Observatory already on `demo-gic` (8 voice commits).
3. **Federation build** completed for platform-v2/ui, served on :5173.
4. **Copilot dashboard UI test** — transcript badge on TestResultCard renders correctly (emerald TRANSCRIPT badge verified by Craig). TestSetDetail filter and TestItemFormModal not yet tested (need transcript items in test_sets collection).
5. **Switched all services to prod MongoDB** (evaluations, observatory, copilot-server).
6. **Ran prod ingestion** — Langfuse sync 459 runs, ingestion 84/84 conversations. BUT voice conversations not tagged as voice.
7. **BLOCKER: Voice channel detection bug** — Voice requests on prod have `channel.name: 'chat21'` (not 'voice'). Pipeline only checks `channel.name` for channel detection. Voice calls identifiable by `attributes.CallSid`, `attributes.channel: 'VOICE'`, or `conversation_start_time` as float — but pipeline doesn't check these. Result: 10,553 observatory conversations, 0 tagged as voice despite 3,292 voice requests existing. Must fix `pipeline.py` channel detection.
8. **Date range bug** — Langfuse sync with same-day `date_from`/`date_to` produces zero-width range (both become `00:00:00`). Workaround: use next day as `date_to`. Needs proper fix in tasks.py to add end-of-day to `date_to`.

**Session 2026-03-04-a** (COMPLETE): Date fix, AWS pipeline, feature branches, dev testing, investigation, PRs, Linear.
1. **Fixed date_to bug** — `admin.py` now serializes `date_to` as end-of-day (`T23:59:59.999`) via `_date_to_iso()` helper. All 3 endpoints use it.
2. **Added Langfuse sync to AWS pipeline** — `step_handler.py` has new `start_sync_langfuse_traces` action. `state_machine.json` runs LangSmith + Langfuse syncs in parallel. Tested locally.
3. **Dev pipeline test** — All 4 steps completed (sync-traces: 192, sync-langfuse: 59, ingest: 24, aggregate: 581). 0 voice conversations because dev MongoDB has no voice requests after Feb 27.
4. **Dev voice request gap investigated** — Voice requests stopped being written to dev MongoDB after Feb 27. Prod is healthy (19 voice requests in March, most recent today). Root cause: conversation-service's RabbitMQ consumer thread likely died on dev (hard restart limit of 5 attempts, health check doesn't detect dead consumer). Not a code bug — dev infrastructure issue. Does NOT affect prod.
5. **Feature branches pushed + PRs created** with Dhruv and Dolly as reviewers:
   - indemn-ai/Indemn-observatory#19 — 9 commits (Langfuse sync, voice channel, evaluate UI, pipeline Lambda)
   - indemn-ai/evaluations#7 — 4 commits (transcript evaluation engine)
   - indemn-ai/copilot-dashboard-react#2 — 2 commits (transcript type badge)
   - indemn-ai/voice-livekit#79 — 2 commits (trace metadata)
6. **Linear updated** — Parent issue COP-359 with 7 sub-issues in "Automated Testing and Evaluation" project. 5 in Acceptance (dev complete), 2 in Backlog (prod deployment + test set creation).
7. **Transcript evaluation verified** — Craig ran evaluation from Observatory on Ronnie2 voice conversation. 6/6 criteria, 2/2 rubric rules. `item_type: transcript`.

**Session 2026-03-04-b** (COMPLETE): Phase 2 research — LiveKit API validation.
1. **LiveKit API tested** — Room creation, agent dispatch with metadata, room participation with audio tracks. All core capabilities validated against dev LiveKit Cloud (`wss://test-ympl759t.livekit.cloud`).
2. **LiveKit OS skill created** — `.claude/skills/livekit/SKILL.md` with status check, credential loading (AWS Secrets Manager), and usage patterns for room management, dispatch, and participation.
3. **Architecture confirmed** — Evaluation harness creates room → dispatches voice agent with bot_id in metadata → joins as participant → audio conversation via TTS/STT → evaluates transcript. Tests exact production code path.
4. **voice-livekit entrypoint analyzed** — `ctx.job.metadata` is available but not yet read. ~5 line change needed to check metadata for bot_id before phone lookup fallback.
5. **Live agent dispatch tested** — Dispatched to `dev-indemn` on EC2, agent picked up in <3s, connected to room, blocked at `wait_for_participant()` (expected — eval mode code change needed).
6. **Design document written** — Complete Phase 2 design covering voice-livekit eval mode, VoiceAgentClient, voice simulation engine, trigger routing, dashboard UI changes, and 5 implementation milestones.

**Session 2026-03-05-a** (COMPLETE): Phase 2 implementation, testing, and verification.
1. **Implementation complete** — All 3 streams implemented in parallel:
   - **voice-livekit** `feat/eval-mode` (1 commit): Eval mode branch in `entrypoint()` — reads `ctx.job.metadata` for `bot_id`, skips SIP extraction, recording, transcription. Production path unchanged.
   - **evaluations** `feat/voice-simulation` (2 commits): VoiceAgentClient (LiveKit room lifecycle, TTS→audio→STT), voice simulation engine (conversation loop, Langfuse enrichment), VOICE_SIMULATION enums, config, dependencies, routing.
   - **indemn-platform-v2** `feat/voice-simulation-type` (3 commits): Voice Sim toggle in form, purple badge, filter chip, stat card, TestSetsList breakdown.
2. **Code review** — 3 parallel review agents (one per stream) + full implementation review against design doc. Found and fixed:
   - DeepgramClient constructor (positional → keyword `api_key=`)
   - deepgram-sdk version pin (`>=3.7.0,<4.0.0` — v6 has breaking API)
   - Dead `fixed_responses` argument removed
   - Filter chip toggle inconsistency fixed
   - Missing TestSetsList type breakdown added
3. **Static verification** — Python AST compile PASS, module imports PASS, 79 existing tests PASS, TypeScript compile PASS.
4. **Testing plan created** — 7-layer plan from static verification through end-to-end. Critical path: deploy eval mode to EC2 → smoke test VoiceAgentClient → full evaluation → dashboard verification.
5. **Layer 4 COMPLETE** — `feat/eval-mode` deployed to EC2 dev container (`voice-livekit-dev`, agent_name=`dev-indemn`). Agent registered successfully. Prod containers untouched ("Up 2 weeks"). Had to regenerate `uv.lock` (uuid-utils malformed source field). Rollback: `cd /opt/dev/voice-livekit && sudo git checkout main && sudo docker compose up -d --build voice-livekit-dev call-end-consumer-dev`.
6. **Layer 5 COMPLETE** — VoiceAgentClient smoke test PASSED. Full multi-turn voice conversation verified:
   - Room creation + agent dispatch with eval metadata: PASS
   - Agent greeting received: "Hello! How can I assist you today?"
   - TTS message sent → agent responded with full paragraph: PASS
   - Follow-up turn: PASS
   - **Major refactor**: Replaced Deepgram audio→STT with LiveKit's `lk.transcription` text stream. The agent already publishes transcriptions via `TextOutputOptions(sync_transcription=True)`. This is more reliable (no silence detection issues), simpler (~170 vs ~240 lines), and removes Deepgram as a dependency.
   - **Bot compatibility note**: Bot `69a9965f39619c27c64fddd6` (V1 service intake agent) has invalid tool names → OpenAI rejects with 400. Used `69a52911e577e75c7e4ecdb6` (covertree-3486) instead — works perfectly. This is a pre-existing bot config issue, not eval mode.
   - **Evaluations branch**: 4 commits on `feat/voice-simulation` (feat + fix + tests + transcription refactor). LOCAL ONLY, not pushed yet.
7. **Layer 6 COMPLETE** — End-to-end evaluation through evaluations service API PASSED.
   - Created voice_simulation test set via API (3 criteria)
   - Triggered evaluation → voice conversation ran in 69 seconds
   - Results: 2/3 criteria passed, `item_type: "voice_simulation"`, full transcript in MongoDB
   - **Bugs found & fixed**: (a) `RuntimeError: Cannot run the event loop while another loop is running` — LangSmith's `client.evaluate()` runs inside FastAPI's event loop, so `asyncio.new_event_loop()` fails. Fixed with `ThreadPoolExecutor`. (b) Transcription truncation — agent's long responses arrived in multiple chunks; `TRANSCRIPTION_SETTLE_SEC` increased from 3.0 to 5.0. (c) Previous runs went to wrong MongoDB — evaluations service `.env` had different URI. Fixed by setting `MONGODB_URI` from AWS at startup.
   - **Evaluations branch**: 6 commits on `feat/voice-simulation`. LOCAL ONLY, not pushed yet.
   - **Layer 7 COMPLETE** — Dashboard visual verification PASSED. User confirmed all UI elements render correctly: purple "Voice Simulation" badge on result cards, filter chip, Voice Sim toggle in test item form, stat card in summary dashboard, conversation transcript with User:/Agent: turns.
   - **Evaluations branch pushed**: `git push indemn feat/voice-simulation` — 6 commits now on remote.
   - **All 7 layers PASS** — Phase 2 ready for PR.
   - **Known issue**: Transcription settle time (5s) may still truncate very long agent responses. The 3rd criterion failed because agent response was cut off mid-sentence. Consider implementing a smarter "final transcription" detection (e.g., checking if transcription text stopped growing) instead of fixed timeout.
   - **Test set in dev tiledesk**: `test_set_id: 75213fa3-6d63-4c82-b34f-51516ef65583` (Voice Sim Smoke Test, 1 item, 3 criteria). Bot: `69a52911e577e75c7e4ecdb6` (covertree-3486, org: Dev-Dhruv, project: DEV KAI).
   - **Run result in dev tiledesk**: `run_id: 6bed835e-3b8c-4632-b528-361184d00eb5`, `evaluation_results` collection has full document with transcript, criteria_scores, trajectory.
   - **Starting services with dev creds**: Use `local-dev-aws.sh` wrapper which pulls from AWS Secrets Manager (`dev/shared/*`). Updated wrapper to include Redis, LiveKit, and other structured secrets.
   - **local-dev-aws.sh fixed**: Now writes `.env.dev` from exported env vars so `local-dev.sh` can source it. Also pulls `CACHE_REDIS_URL` from `dev/shared/redis-credentials` and LiveKit creds from `dev/shared/livekit-credentials`.

**Session 2026-03-06-a** (COMPLETE): Voice metrics + transcription reliability + project cleanup.
1. **Transcription reliability** — `TRANSCRIPTION_SETTLE_SEC` reduced from 5.0s to 2.0s. Added room disconnect handler (`_room_disconnected` event) that breaks out of waits immediately on disconnect. Verified: `settle_wait_ms` consistently ~2001ms in live evaluations.
2. **Voice metrics** — Per-turn metrics (tts_generation_ms, audio_publish_ms, agent_response_ms, first_transcription_ms, transcription_stream_count, settle_wait_ms, total_turn_ms) + session aggregates (greeting_latency_ms, total_duration_ms, turn_count, averages). `get_metrics()` method on VoiceAgentClient. Persisted as top-level `voice_metrics` field in evaluation_results for MongoDB queryability.
3. **Dev testing** — 3 evaluations against covertree-3486 bot. 108 unit tests passing. Voice metrics populated correctly in all results.
4. **Git cleanup** — Pushed `ddaf12d` to `indemn/feat/voice-simulation` (7 commits total). Created evaluations PR #9 and copilot-dashboard-react PR #3. All 7 PRs now open.
5. **Linear consolidation** — COP-359 renamed to "Voice Evaluation" (was Phase 1 only), moved to Acceptance. Old 7 granular sub-issues canceled, replaced with 3 consolidated: COP-366 (transcript eval, Acceptance), COP-367 (voice simulation + metrics, Acceptance), COP-364 (deploy to prod, Backlog). AI-284 canceled as covered by COP-359.

## All Dev Work Complete — PRs Open for Review

Linear: **COP-359** (Acceptance) with 3 sub-issues:
- **COP-366** (Acceptance): Voice transcript evaluation
- **COP-367** (Acceptance): Voice simulation + voice metrics
- **COP-364** (Backlog): Deploy to prod

### PRs (7 total, all ready for review)

**Transcript evaluation:**
| PR | Repo | What |
|----|------|------|
| [#19](https://github.com/indemn-ai/Indemn-observatory/pull/19) | Indemn-observatory | Langfuse sync, voice channel detection, evaluate UI, AWS pipeline Lambda |
| [#7](https://github.com/indemn-ai/evaluations/pull/7) | evaluations | Transcript evaluation engine + API |
| [#2](https://github.com/indemn-ai/copilot-dashboard-react/pull/2) | copilot-dashboard-react | Transcript type badge + filter |
| [#79](https://github.com/indemn-ai/voice-livekit/pull/79) | voice-livekit | Trace metadata (call_sid, id_bot, room_name) |

**Voice simulation:**
| PR | Repo | What |
|----|------|------|
| [#9](https://github.com/indemn-ai/evaluations/pull/9) | evaluations | Voice simulation engine + voice metrics (7 commits) |
| [#83](https://github.com/indemn-ai/voice-livekit/pull/83) | voice-livekit | Eval mode for voice agent dispatch |
| [#3](https://github.com/indemn-ai/copilot-dashboard-react/pull/3) | copilot-dashboard-react | Voice simulation UI (badges, filters, stat card) |

### Remaining for prod (COP-364)
1. Review and merge all 7 PRs
2. Add Langfuse env vars to prod Observatory (`LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`)
3. Update AWS Lambda (`step_handler.py`) and Step Function (`state_machine.json`)
4. Deploy voice-livekit eval mode to prod EC2 containers
5. Create voice agent test sets and verify end-to-end

### Testing Status — ALL PASS
- [x] Static verification (compile, import, type check)
- [x] 108 unit tests passing
- [x] EC2 dev deployment — `dev-indemn` eval mode registered
- [x] VoiceAgentClient smoke test — multi-turn conversation, transcription stream
- [x] End-to-end voice evaluation via API — voice_metrics in results, settle ~2s
- [x] Dashboard visual verification — purple badge, filter chip, stat card, form toggle
- [x] Voice metrics verified — per-turn timing (TTS, publish, response, transcription), session aggregates

See testing plan: [phase2-testing-plan](artifacts/2026-03-05-phase2-testing-plan.md)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| evaluations | GitHub repo + local | indemn-ai/evaluations, `/Users/home/Repositories/evaluations` |
| copilot-dashboard | GitHub repo + local | indemn-ai/copilot-dashboard, `/Users/home/Repositories/copilot-dashboard` |
| indemn-platform-v2 | GitHub repo + local | craig-indemn/indemn-platform-v2, `/Users/home/Repositories/indemn-platform-v2` |
| voice-service | GitHub repo + local | indemn-ai/voice-service, `/Users/home/Repositories/voice-service` |
| voice-livekit | GitHub repo + local | indemn-ai/voice-livekit, `/Users/home/Repositories/voice-livekit` |
| indemn-observability | GitHub repo + local | indemn-ai/indemn-observability, `/Users/home/Repositories/indemn-observability` |
| percy-service | GitHub repo + local | indemn-ai/percy-service, `/Users/home/Repositories/percy-service` |
| copilot-dashboard-react | GitHub repo + local | indemn-ai/copilot-dashboard-react, `/Users/home/Repositories/indemn-platform-v2` (local clone, push to `indemn` remote) |
| Platform Development project | OS project | `projects/platform-development/INDEX.md` |
| LiveKit Cloud | SIP host | `tk2bj7pt8eg.us.sip.livekit.cloud` |
| S3 recordings | AWS | `indemn-call-transcripts` bucket |
| Linear parent issue | Linear | COP-359 — Voice Evaluation (Acceptance) |
| Linear sub-issues | Linear | COP-366 (transcript eval, Acceptance), COP-367 (voice sim + metrics, Acceptance), COP-364 (deploy to prod, Backlog) |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-27 | [initial-context](artifacts/2026-02-27-initial-context.md) | Comprehensive research synthesis across all repos — current state of evaluations, voice stack, observatory, data gaps, and integration challenges |
| 2026-02-27 | [voice-tracing-discovery](artifacts/2026-02-27-voice-tracing-discovery.md) | Langfuse + LiveKit Cloud tracing discovery — how voice traces work, data formats, access patterns, Slack/email evidence |
| 2026-02-27 | [design-document](artifacts/2026-02-27-design-document.md) | Comprehensive design: 5-phase roadmap, architecture, data flows, implementation details for voice evaluations + observatory |
| 2026-03-02 | [langfuse-sync-implementation](artifacts/2026-03-02-langfuse-sync-implementation.md) | Langfuse sync implementation, initial test results, discrepancies to investigate, env config notes |
| 2026-03-02 | [prod-test-results](artifacts/2026-03-02-prod-test-results.md) | Prod data test: Langfuse sync (266 traces, 97% match), ingestion (13 voice convos), Observatory verification |
| 2026-03-04 | [phase1-complete-handoff](artifacts/2026-03-04-phase1-complete-handoff.md) | Phase 1 completion: what was built, PRs, Linear issues, prod checklist, Phase 2 objectives |
| 2026-03-04 | [phase2-livekit-api-validation](artifacts/2026-03-04-phase2-livekit-api-validation.md) | Phase 2 research: LiveKit API validation — room creation, agent dispatch, room participation all tested |
| 2026-03-04 | [phase2-voice-simulation-design](artifacts/2026-03-04-phase2-voice-simulation-design.md) | Phase 2 design: voice simulation evaluation — architecture, changes per repo, implementation milestones |
| 2026-03-05 | [phase2-testing-plan](artifacts/2026-03-05-phase2-testing-plan.md) | Phase 2 testing plan: 7-layer verification from static checks through end-to-end dashboard verification |

## Known Limitations
- **Pre-Phase-1B traces lack metadata**: ALL current traces (dev AND prod confirmed) have NO `call_sid` or `id_bot` in Langfuse metadata. Only phone+time fallback works. The voice-livekit commit (`9df3389`) adds this metadata going forward, but only helps for NEW calls after deployment.
- **Phone+time fallback works well on prod**: 97% match rate (258/266 traces) on prod vs 69% on dev. The 3% unmatched are likely calls with no corresponding MongoDB request.
- **Phone+time fallback edge case**: 5-minute window can fail if same number calls multiple times rapidly AND there are more traces than requests in the window. Closest-match + dedup mitigates but doesn't eliminate.
- **Prod vs Dev Langfuse**: Prod project `cmht0a7ll001qad07jn0ko84c` (1,146 traces). Dev project `cmht0gwcr001oad07czzyujje` (180 traces). **CRITICAL**: Prod Langfuse matches PROD MongoDB only. Dev matches DEV MongoDB only. Mismatched creds/DB = 0 joins.
- **MongoDB index creation on prod**: The Langfuse sync compound index (`extra.metadata.source` + `_synced_at`) times out on prod MongoDB. Wrapped in try/except so it doesn't block the sync. The index is a performance optimization for incremental sync — not required for correctness.
- **Federation build required for Copilot Dashboard**: The Angular copilot-dashboard loads React components via Module Federation from :5173. The Vite dev server does NOT work — must run `npm run build:federation` in platform-v2/ui then `npx serve dist-federation -l 5173 --cors -n`. Hard refresh (Cmd+Shift+R) after rebuilding.
- **Daily pipeline doesn't include voice yet**: The deployed prod Step Function only runs LangSmith sync. Langfuse sync step is written (in PR #19) but not deployed to prod yet. Dev pipeline tested and working.
- **Dev voice requests stopped after Feb 27**: conversation-service's RabbitMQ consumer thread likely died on dev. Prod is unaffected (voice requests being written daily). Dev infrastructure issue, not a code bug.

## Not Built
- **Advanced voice metrics** — End reason breakdown, STT confidence scores, interruption rate. Basic per-turn timing (TTS, response latency, transcription latency) IS built. See design document Phase 2C.
- **Rubric evaluators on voice**: Only criteria evaluators tested on voice. Rubric evaluators (per-rule LLM judges) were tested on web but not voice.
- **Voice agent test set**: No test sets exist for any prod voice agent yet. COP-364 (deploy to prod) includes creating these.
- **Per-turn tool call matching**: Voice simulation appends all Langfuse tool calls at end of transcript rather than inline per turn (Langfuse traces lack turn indices). v1 tradeoff.
- **Concurrent voice simulations**: Safe at concurrency=1, needs async conversion for higher concurrency.

## Decisions
- 2026-02-27: Voice trace data access pattern: OTLP → Langfuse → Langfuse API. Mirrors the web pattern (LangChain callbacks → LangSmith → LangSmith API). Langfuse is the canonical data source for voice traces, not LiveKit Cloud or direct data hooks.
- 2026-02-27: Tracing platform consolidation is out of scope. Work with what exists (Langfuse for voice, LangSmith for web).
- 2026-02-27: Two evaluation modes for voice: (1) Voice Replay Evaluation — judge real conversations from Observatory/Langfuse, build first. (2) Voice Simulation — text-mode endpoint on voice-livekit for proactive testing, build second. Replay is the MVP; simulation goes on the roadmap.
- 2026-02-27: Observatory → Evaluation bridge is a new flow: select conversations in Observatory, trigger evaluation, results appear in Copilot Dashboard. Benefits both web and voice.
- 2026-03-02: Voice requests store `conversation_start_time` as Unix float, not ISO string. Ingestion must handle both via `$or` on `createdAt` (Date). All four date-filtered methods in MongoDBSourceConnector updated.
- 2026-03-02: Pre-Phase-1B Langfuse traces have no `call_sid` or `id_bot` metadata. Phone+time fallback is the only working join. Must use closest-match + dedup to prevent N:1 collisions when same number calls repeatedly.
- 2026-03-02: Dev Langfuse has no TOOL-type observations (only SPAN + GENERATION). Prod likely has them. Not a code issue.
- 2026-03-02: Transcript evaluation test sets — the test item questions/scenarios are organizing containers only. In transcript mode, only the `success_criteria` fields matter. All criteria from all items are collected and applied to the real conversation transcript. The agent is never invoked.
- 2026-03-02: The daily pipeline (EventBridge → Step Function → Lambda) currently only does LangSmith sync. Langfuse sync step must be added to `step_handler.py` and `state_machine.json`. Langfuse env vars must be added to the deployed Observatory environment.
- 2026-03-03: Observatory date handling uses proper `date` types in Pydantic models (auto-validated by Pydantic v2), converted to ISO strings for MongoDB job storage, then parsed back to `datetime` in task functions. Field named `date` required import alias `date_type` to avoid shadowing.
- 2026-03-03: All deprecated `datetime.utcnow()` and `datetime.utcfromtimestamp()` replaced with timezone-aware equivalents across observatory codebase (pipeline.py, structure.py, auth.py, aggregations.py).
- 2026-03-03: Langfuse observation pagination added — loops with `page` parameter until fewer than 100 results. Rate-limited with `asyncio.sleep(0.05)` between pages.
- 2026-03-03: Voice requests on prod use `channel.name: 'chat21'` (same as web). Voice must be detected via `attributes.CallSid` or `attributes.channel == 'VOICE'`. Pipeline channel detection in `pipeline.py` needs fixing.
- 2026-03-03: Langfuse sync date_to must be end-of-day or next day — same-day dates create zero-width range. Fixed in admin.py with `_date_to_iso()` helper.
- 2026-03-04: percy-service (indemn-ai/percy-service) is the backend for the platform. indemn-platform-v2 was separated into percy-service (backend) + copilot-dashboard-react (frontend, indemn-ai/copilot-dashboard-react). Run percy-service on :8003, NOT indemn-platform-v2's stale Python backend.
- 2026-03-04: Feature branch `feat/voice-evaluation-support` on indemn-observability has all 9 voice commits cherry-picked onto `indemn/main`. PRs go to `indemn` remote (indemn-ai/Indemn-observatory), not `origin` (craig-indemn fork).
- 2026-03-04: Feature branch `feat/transcript-type-ui` on indemn-platform-v2 targets `indemn` remote (indemn-ai/copilot-dashboard-react). 2 UI-only commits.
- 2026-03-04: Dev voice requests stopped after Feb 27 — conversation-service RabbitMQ consumer thread likely dead. Prod unaffected. Dev infrastructure issue, not blocking prod deployment.
- 2026-03-04: Transcript evaluation is distinct from replay. Replay re-invokes the current agent with historical user messages. Transcript evaluation scores the actual historical conversation as-is without invoking the agent.
- 2026-03-04: Phase 2 objective: simulation-based evaluation for voice agents — same test scenario approach as web, with added speech-to-text complexity. Design iteration needed before implementation.
- 2026-03-05: Phase 2 implementation uses 3 parallel streams (voice-livekit, evaluations, platform-v2). All independent — no cross-repo dependencies during development.
- 2026-03-05: VoiceAgentClient uses RMS energy-based silence detection (threshold 200, 1.5s gap). Simpler than Silero VAD, sufficient for controlled eval environment.
- 2026-03-05: deepgram-sdk pinned to `>=3.7.0,<4.0.0` — v4+ has breaking API changes (`listen.rest.v("1")` removed).
- 2026-03-05: Voice simulation tool calls fetched from Langfuse post-conversation and appended at end of transcript (not inline per turn). Acceptable v1 tradeoff — Langfuse traces lack turn indices.
- 2026-03-05: `create_llm_simulated_user` called without `fixed_responses` — initial message handled manually before the conversation loop to match voice flow (agent greets first, then user responds).

## Open Questions
- ~~Where do turn-by-turn voice transcripts live?~~ ANSWERED: LiveKit chat_history.json has full turn-by-turn with metrics. Also exported to Langfuse via OTLP. MongoDB `bot_external_event_logs` has summaries only.
- ~~What tracing system is used for voice?~~ ANSWERED: **Langfuse** (HIPAA instance at `hipaa.cloud.langfuse.com`, project `cmht0a7ll001qad07jn0ko84c`). OpenTelemetry spans from LiveKit Agents SDK exported via OTLP.
- Should we consolidate on one tracing platform (Langfuse or LangSmith) or build connectors for both? Dhruv was researching this as of Feb 5 meeting.
- ~~How should voice agents be invoked for evaluation?~~ ANSWERED: Transcript-based replay (Mode A) is built and working. The harness reads actual conversation messages from MongoDB, enriches voice conversations with tool calls from Langfuse, and evaluates the transcript against success criteria. Agent is not invoked. Voice simulation (Mode B) requires a new HTTP endpoint on voice-livekit — future work.
- ~~What Langfuse API credentials do we have?~~ ANSWERED: Credentials confirmed working. 1,146 live traces (prod). Stored in OS `.env` as `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`. Also added to Observatory `.env` for the sync task.
- LiveKit Cloud API doesn't expose programmatic download for observability data (Jonathan confirmed Feb 24). Is Langfuse the sole programmatic data source, or is there another path?
- ~~Are voice-specific evaluation criteria needed beyond text content?~~ ANSWERED: Not for MVP. Existing success criteria framework works for voice transcript evaluation. Voice-specific metrics (latency, interruptions, STT confidence) are Phase 2C — not built yet.
- ~~How do we join Langfuse traces with MongoDB conversation data?~~ ANSWERED: Two-hop join via CallSid. Phase 1B traces have `metadata.call_sid` → `requests.attributes.CallSid` → `request_id`. Fallback for pre-Phase-1B: extract phone from `lk.room_name` + time-window match on `requests.createdAt`. Prod match rate: 97%.
- ~~For the Observatory Langfuse connector: should it mirror the LangSmith connector pattern?~~ ANSWERED: Yes, transforms Langfuse observations to same run schema (run_type, inputs, outputs, tokens, etc.) with `extra.metadata.source = "langfuse"` to distinguish. Same `upsert_runs_batch()` writer path.
