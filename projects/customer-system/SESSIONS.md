# Customer System — SESSIONS

> **Append-only log of session objectives + outcomes.** New entries at the **top**. Each session adds one entry at end of session. Loaded on-demand when a session needs to look back at history or learn the objective-statement format from prior entries.
>
> The full Journey lives in `CLAUDE.md § 5`. This file is the lighter-weight per-session log.

---

## Session 18 — 2026-05-05 — Pre-TD-2 OS hardening sprint complete; all 5 Tier 1 items shipped + deployed + verified

**Workstream:** OS hardening sprint — ship foundation fixes so TD-2 cascade lands on clean infrastructure.

**Objective:** Ship the 5 Tier 1 items (bulk_save_tracked, indemn diagnose, list filter fix, polymorphic --include-related, Employee entity_resolve) + os-learnings.md badge audit. NOT start TD-2.

**Parallel sessions during:** None active. Pricing Framework at Phase D visual v6 (separate worktree, untouched).

**Outcome:**
- **bulk_save_tracked** — `kernel/entity/save.py` new sibling to `save_tracked_impl`. insert_many(ordered=False) + in-memory hash-chained change records + batched watch evaluation. Wired from fetch_new.py. 12 unit tests.
- **`indemn diagnose` command group** — 3 sub-commands (actor/message/cron) + `/api/_diagnose/*` API endpoints. Deployed + verified end-to-end against live Email Fetcher. 12 unit tests. Auth help docstring updated with INDEMN_SERVICE_TOKEN.
- **List endpoint --data filter** — root cause was CLI missing the flag entirely (API `?filter=` param was always correct). Added `--data` to list command → passes as `filter` query param. Verified: valid field filters, bogus field → 400. 4 tests.
- **Polymorphic --include-related** — `is_polymorphic_relationship` + `target_type_field` on FieldDefinition. `_build_related_entities` resolves target type at runtime. Touchpoint entity def updated with the flag. 5 tests.
- **Employee entity_resolve activated** — single API call. Verified: Kyle@indemn.ai → score 1.0.
- **os-learnings.md audit** — 7 rows corrected from stale 🔴/🟡 to 🟢 (Slack ingestion, Document.source enum, list filter, fetch_new bottleneck, Employee resolve, CLI diagnostics gap, polymorphic include-related).
- **indemn-os CLAUDE.md updated** — documents bulk_save_tracked + diagnose commands for discoverability.
- Test count: 481 → 514 (+33 new, 0 regressions).

**Indemn-os commits:** `d1f695a` (main feat), `12ce818` (role_ids fix), `0e95ea5` (Message schema fix), `d746ea4` (docs). All pushed + deployed to indemn-api / queue-processor / temporal-worker / runtime-async.

**Handoff to Session 19:** TD-2 cascade activation begins. Start with MeetingClassifier on Armadillo's Apr 28 discovery meeting per trace-as-build-method. Next-session prompt at `PROMPT-2026-05-05-td2-cascade.md`.

**Touched:** `kernel/entity/save.py`, `kernel/capability/fetch_new.py`, `kernel/api/diagnose_routes.py`, `kernel/api/app.py`, `kernel/entity/definition.py`, `kernel/message/emit.py`, `indemn_os/diagnose_commands.py`, `indemn_os/main.py`, `indemn_os/auth_commands.py`, `CLAUDE.md` (indemn-os), `os-learnings.md`, 4 new test files.

---

## Session 17 — 2026-05-04 — TD-1 verified done end-to-end; Bug #50 (queue visibility-extend + attempt_count cap) + fetch_new chunk-cap with oldest-first sort + Bug #12 reframe + 7 zombie polling loops killed; pre-TD-2 OS hardening sprint planned

**Workstream:** TD-1 verification + foundations cleanup. Started as the kickoff TD-2 cascade-activation session per Session 16's handoff, but pre-flight Bug #49 verification surfaced a chronic Email Fetcher subprocess slowness + multi-pod completion race that had to be resolved before the cascade could land cleanly. Three coupled bugs fell out of the verification; all three fixed in-session.

**Objective (kickoff):** Pre-flight verify Bug #49 fix dropped dead_letter rate to near-zero post-2026-05-04 deploy, then begin TD-2 cascade activation starting with MeetingClassifier on Armadillo's Apr 28 discovery meeting per trace-as-build-method.

**Objective (revised mid-session per Craig):** Address the bugs and improvements impeding effective work with the OS first; foundations must be solid before TD-2's cascade goes on top. Resolve TD-1's open issues + plan a pre-TD-2 OS hardening sprint.

**Parallel sessions during:** Pricing Framework Session 3+ ran in parallel in `.claude/worktrees/gic-feature-scoping/` (Phase D visual v6 generated from full staging JSON). No cross-impact on Session 17's TD-1 verification or Bug #50 / fetch_new state. Workstream A files preserved verbatim per parallel-session discipline.

**Outcome (Bug #50 — queue visibility extend + max_attempts cap):**

- **Two coupled defects surfaced from chronic Email/Slack stuckness investigation:**
  - **(50a)** Bug #49 (Session 16) added Temporal activity heartbeat in cron_runner — kept activity alive past 90s heartbeat_timeout. But Mongo's `message_queue.visibility_timeout` (5 min, set on every claim in `kernel/message/mongodb_bus.py`) was independent — nothing extended it while runtime was still working. Slow Email/Slack subprocesses raced the queue's recovery sweep: pod A still working, queue recovers at 5 min, pod B claims it (multi-pod is by design), pod A's later `complete` hits 404 "Message not found." Subprocesses succeed but bookkeeping fails, watermark never advances, backlog grows.
  - **(50b)** `kernel/queue_processor.py::check_visibility_timeouts` unconditionally recovered every timed-out `processing` message back to `pending` with no max_attempts check. The bus's `claim` path increments `attempt_count` on every claim, but nothing capped it — so a stuck message could attempt 7+ times indefinitely. Observed: stuck email_fetcher message `69f89bec1f2c3ee82ecb66c4` at attempt_count=7 / max_attempts=3, last_error "Command 'indemn email fetch-new' timed out after 600.0 seconds."
- **Implementation:**
  - `kernel/api/queue_routes.py` — new `POST /api/message_queues/{id}/extend-visibility` endpoint resets visibility_timeout = now + 5min; idempotent on terminal status (completed/dead_letter/failed); refuses pending (nothing to extend).
  - `indemn_os/src/indemn_os/queue_commands.py` — new `indemn queue extend-visibility <id>` CLI mirroring complete/fail verbs.
  - `harnesses/async-deepagents/main.py` — cron heartbeat loop now calls `await asyncio.to_thread(indemn, "queue", "extend-visibility", message_id)` alongside `activity.heartbeat()`. Same 30s cadence; CLIError caught + logged so single failure doesn't crash the loop (at worst lose race once).
  - `kernel/queue_processor.py::check_visibility_timeouts` — split into two `update_many` calls: (1) dead-letter messages where `attempt_count >= max_attempts` via `$expr: {$gte: ["$attempt_count", "$max_attempts"]}`, then (2) recover the rest to pending. Logs `Dead-lettered N messages over max_attempts (Bug #50)`.
- **12 new unit tests:** `tests/unit/test_check_visibility_timeouts_attempt_cap.py` × 4 (shape pins on $expr branch + recovery branch + ordering + behavior with mocked collection); `tests/unit/test_extend_visibility_endpoint.py` × 8 (route registration, terminal idempotency, 5-min offset, processing-only guard, happy path, 404, 400 on pending, all terminal statuses); 1 new shape pin in `harnesses/async-deepagents/tests/test_cron_runner.py::test_cron_heartbeat_loop_extends_queue_visibility` (queue extend-visibility called via asyncio.to_thread, uses input.message_id, CLIError caught + log.warning).
- **Deployment:** indemn-api + indemn-queue-processor + indemn-runtime-async all redeployed. **First-round deploy mistake:** initial `railway up --ci --detach` was triggered from the operating-system worktree CWD instead of indemn-os CWD — uploaded the wrong source, build silently used a stale image. Caught + corrected by re-running `railway up` from `/Users/home/Repositories/indemn-os` directly. New image hashes: api `3253bbf9...`, queue-processor `58f17e34...`, runtime-async `874723f6...`.
- **Verified live:** vis_gap > 5min observed on multiple email_fetcher messages (10.9min, 8.8min, 7.8min — proving extend-visibility fires on heartbeat); queue_processor logs `Dead-lettered N messages over max_attempts (Bug #50)` repeatedly (proving 50b cap fires); slack/meeting/drive completing cleanly post-deploy. Email Fetcher first post-fix completion at **2026-05-04T21:33:49Z** — first email completion since 14:26 UTC that day (7+ hours of stuckness ended).

**Outcome (`fetch_new` chunk-cap + oldest-first sort — Bug #50 follow-on):**

- **Surfaced from Bug #50 deploy verification:** Bug #50 fix proved Email Fetcher *could* now complete via heartbeat extension, but each subprocess was still chronically slow (5-10 min) due to per-entity sequential `save_tracked()` loop in `kernel/capability/fetch_new.py`. With ~150-300ms per save × N new entities × 11-mailbox fan-out, accumulated backlog stays painful even with extension. Verified there is **NO LLM call** in the email fetch path (cron_runner mode is genuinely deterministic; LangSmith traces stay at 0; verified via grep on `kernel/integration/adapters/google_workspace.py` and `kernel/capability/fetch_new.py`).
- **Bridging fix:** `params["limit"]` caps saves per call. Subsequent ticks pick up the rest. **Critical correctness invariant:** when `limit` is set, the cap must apply to OLDEST-first slice — otherwise APIs that return newest-first (Gmail's default) would advance the watermark past unsaved older items, leaving them stranded forever. Implementation in `kernel/capability/fetch_new.py`: after dedup, sort genuinely-new items ascending by watermark field (date / posted_at / created_date — same fall-through chain as Bug #46) before slicing.
- **4 new unit tests:** `tests/unit/test_fetch_new_chunk_cap.py` — limit caps saves at N; oldest-first when capped (newest-first input → 100 oldest saved; guards watermark-correctness invariant); no limit means unbounded (manual backfills preserved); dedup before cap (50 dupes + 100 new + limit=100 saves the 100 new ones).
- **Skill updates pushed to dev OS:** `email-fetcher` v5, `slack-fetcher` v4, `meeting-fetcher` v4, `drive-fetcher` v4 — all now pass `--data '{"limit": 100}'` on cron command line.
- **Real foundation fix (`bulk_save_tracked`) queued for next session** — single Pydantic validation pass + insert_many + batched audit chain + batched watch evaluation. Replaces the per-item loop entirely. ~half day; ships in OS hardening sprint per `PROMPT-2026-05-05-os-hardening.md` Tier 1 #1.

**Outcome (Bug #12 REFRAME):**

- Per Craig 2026-05-04: "the mongo DB in the secret is needed. its just us that needs to use this other value." The shared `mongodb-uri` AWS Secret correctly stores the private-link host (`dev-indemn-pl-0`) the platform NEEDS — resolves only inside AWS VPCs. Sessions 15+16's "re-fixes" (overwriting with the public host) were the actual bug; the Railway platform's auto-restore was correct behavior, not a regression.
- **Fix:** `scripts/secrets-proxy/mongosh-connect.sh` does inline `-pl-0` → `` host swap (`LOCAL_URI="${URI/-pl-0/}"`). Pattern catches both `dev-indemn-pl-0` → `dev-indemn` and `prod-indemn-pl-0` → `prod-indemn`. Comment block in script documents rationale + tells future operators NOT to "fix" by writing public host back to shared secret. Verified `db.runCommand({ping: 1})` returns `ok: 1`.

**Outcome (zombie polling cleanup):**

- 7 leftover `until [...]; do sleep N; done` shells from prior sessions identified and killed:
  - `94677` (Thu01PM) — polled api.os.indemn.ai/api/_meta/queue-stats every 10s for 3 days waiting for an email_fetcher message that completed long ago
  - `90472` (Fri09AM) — polled LangSmith every 8s for a Slack Fetcher run
  - `40577, 81319, 93507, 93871, 94021` — stale `/tmp/claude-501` output-polling shells from prior background tasks
- **Dev API response time recovered: 5-8s → 60-100ms** post-cleanup. The zombies were genuinely loading the API. Today's session's own background polling shells preserved.

**Outcome (TD-1 done-test verification):**

All TD-1 done-test items now passing on production state:
- 4 fetcher actors active, mode=cron_runner, correct cron schedules ✓
- Last 30 min: 7 email + 8 slack + 2 meeting completions ✓
- Entity counts substantial: 3375 emails, 305 meetings, 867 SlackMessages, 1379 documents ✓
- Bug #36/#37 cleanup verified (Session 14) ✓
- Voice + chat log-touchpoint end-to-end (Session 15) ✓
- Document.source enum includes slack_file_attachment ✓
- ReviewItem entity (9 fields) + Reviewer role (1 watch) wired ✓
- Cascade NOT activated (EC suspended, TS suspended, IE active) ✓
- Zero dead_letter messages since Bug #50 deploy at 21:33 UTC ✓

**Outcome (next-session prompt drafted):**

`projects/customer-system/PROMPT-2026-05-05-os-hardening.md` — full pasteable session-start prompt for the pre-TD-2 OS hardening sprint. Tier 1 list in priority order: (1) `fetch_new` bulk_save_tracked, (2) `indemn diagnose` command group, (3) List endpoint arbitrary field filters regression fix, (4) `--include-related` polymorphic Option B support, (5) Employee `entity_resolve` activation. Plus Tier 1.5 os-learnings.md status badge cleanup. Done-test acceptance criteria specified per item.

**os-learnings.md updates this session:**
- NEW row: Bug #50 (🟢 Fixed end-to-end with full audit trail of both 50a + 50b + tests + deployment + verification)
- NEW row: `fetch_new` sequential save_tracked bottleneck (🔴 Open — proper bulk_save_tracked is queued for OS hardening sprint; today's chunk-cap is bridging fix)
- NEW row: CLI debugging gap (🔴 Open — comprehensive list of every diagnostic reached for this session that should be `indemn diagnose <thing>`; `indemn diagnose` command group queued)
- UPDATED row: Bug #12 REFRAME marked 🟢 Fixed via wrapper change

**Test counts:**
- Pre-session: 477 unit tests (kernel) + 85 harness = 562 total
- Post-session: **481 unit tests** (kernel — 4 new for fetch_new chunk-cap; 12 new for Bug #50 had landed at the boundary of the count) + **86 harness tests** (1 new for cron heartbeat-loop visibility-extend shape pin). Total: **567 tests**, all passing.

**Touched (files / entities):**
- Indemn-os main commits pushed to origin/main this session:
  - `18ab3b9` `fix(queue+harness): wire queue visibility extension + cap visibility-recovery at max_attempts — Bug #50`
  - `7c3a54c` Merge: Bug #50 fix
  - `06d2bbd` `fix(capability): fetch_new sorts oldest-first + caps saves at params['limit'] — Bug #50 follow-on`
  - `a09c67b` Merge: fetch_new chunk-cap + oldest-first sort
- Operating-system worktree commit (`os-roadmap` branch — pushed at EOS):
  - `3ddc02a` `project(customer-system): TD-1 foundations — Bug #50 + fetch_new chunk-cap + Bug #12 reframe + os-learnings`
- This EOS commit (separate):
  - `CURRENT.md` rewritten (Workstream A preserved verbatim; Workstream B + merged sections updated)
  - `SESSIONS.md` Session 17 entry appended at top
  - `roadmap.md` Where-we-are updated
  - `CLAUDE.md` § 5 Journey Session 17 entry appended
  - `INDEX.md` Decisions / Open Questions / Artifacts updated
  - `PROMPT-2026-05-05-os-hardening.md` NEW (next-session prompt)
- Dev OS state: 4 fetcher skills updated to v4-v5; 86 stuck `_scheduled` messages from morning's secret-revert window manually marked dead_letter with audit-trail reason; Slack 3-day watermark drained.
- Production touched: indemn-api (×2), indemn-queue-processor, indemn-runtime-async

**Handoff to next session:** Use `PROMPT-2026-05-05-os-hardening.md` as kickoff. **Pre-TD-2 OS hardening sprint.** TD-1 verified done; this session resolves the Tier 1 OS friction items so TD-2's 7-associate cascade lands on a foundation that doesn't fight us. Tier 1 in priority order: (1) `fetch_new` bulk_save_tracked, (2) `indemn diagnose` command group, (3) list endpoint arbitrary field filters regression fix, (4) `--include-related` polymorphic Option B support, (5) Employee `entity_resolve` activation. Plus Tier 1.5 os-learnings.md status-badge audit. Done-test acceptance criteria per item in the prompt. After Tier 1 lands cleanly: TD-2 cascade activation begins (next-next session) — start with MeetingClassifier on Armadillo's Apr 28 discovery meeting per trace-as-build-method per CLAUDE.md § 2.

---

## Session 16 — 2026-05-01 → 2026-05-04 — Bug #40 closed via cron_runner mode + Bug #48 (CLI URL slug) + Bug #49 (cron_runner heartbeat + OTEL span); 3-day soak verifies 1863 completions / 0 LangSmith traces; ~1000 LLM calls/day eliminated

**Workstream:** TD-1 follow-on. Bug #40 was the explicit gate to TD-2 per Craig's directive at Session 15 close. Session 16 spans 2026-05-01 (initial implementation + flip + Bug #48 surfacing) and 2026-05-04 (3-day soak verification + Bug #49 root-cause + heartbeat fix + EOS).

**Objective:** Deep architectural design + implementation of Bug #40. Two design choices to weigh: (A) new `cron_runner` actor mode bypassing the LLM (skill content = literal CLI command, ~5-7 file change, faster); (B) new `ScheduledActorWorkflow` peer to `ProcessMessageWorkflow` (cleaner architectural separation; ~2x the work). All 4 fetchers currently functional via mode=hybrid + LLM agent — wasteful (~1000 LLM calls/day across 4 fetchers) but not broken. After Bug #40 closes: TD-2 begins (cascade activation: build MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher; activate progressively bottom-up; systematic historical replay).

**Parallel sessions during:** Pricing Framework Session 3 ran in parallel in `.claude/worktrees/gic-feature-scoping/` (Phase C LOE pass + Phase D start). No cross-impact — different worktree, separate workstream, only shared file is `CURRENT.md` where each session updates its own workstream section.

**Outcome (Bug #40):**

- **Design choice resolved: Option A (`cron_runner` actor mode)** over Option B (`ScheduledActorWorkflow` peer). Rationale: extends the existing `Actor.mode` primitive (deterministic | reasoning | hybrid | cron_runner) rather than introducing a parallel kernel-side workflow; uses Bug #41's existing harness foothold (`_load_message_context` already branches on `_*` synthetic types); routes through unchanged dispatch path; ~5-7 files vs ~2x for Option B with no observable runtime difference. Per CLAUDE.md "no abstraction for abstraction's sake."
- **Implementation:**
  - `kernel_entities/actor.py` — added `cron_runner` to mode Literal.
  - `harnesses/async-deepagents/cron_runner.py` — NEW (~200 LOC): `parse_command_from_skill` extracts argv from skill's `## Command` section + bash fence, indemn-only allowlist, single-command-only. `run_cron_skill` validates trigger is synthetic `_*`, loads first skill via existing CLI, parses command, exec via existing `harness_common.cli.indemn()` helper (env-var propagation INDEMN_EFFECTIVE_ACTOR_ID + INDEMN_CAUSATION_MESSAGE_ID intact), inspects JSON `errors` field (non-empty → fail), marks queue complete/fail.
  - `harnesses/async-deepagents/main.py::process_with_associate` — branches on `actor.mode == "cron_runner"` BEFORE building the agent; skips deepagents entirely.
  - **22 unit tests** in `harnesses/async-deepagents/tests/test_cron_runner.py` (parser shape × 11, executor happy + 7 failure modes × 8, sync-helper pin, mode-Literal pin via Pydantic field annotation introspection). Plus `test_load_message_context.py` stub-list update for `harness.cron_runner`.
- **Skills:** all 4 fetcher skills rewritten to cron_runner shape (`## Command` section + single-line CLI command + `## Why this exists` rationale). Pushed to dev OS as v3 each. Files NEW in repo: `email-fetcher.md`, `meeting-fetcher.md`, `drive-fetcher.md` (slack-fetcher.md updated).
- **Deployment:** indemn-api + indemn-queue-processor + indemn-temporal-worker (all needed for Pydantic Literal change to load Actor records with cron_runner mode) + indemn-runtime-async (cron_runner module). Initial runtime deploy hit `ModuleNotFoundError: No module named 'cron_runner'` — fixed import to `from harness.cron_runner import` (the `/app/harness/` package layout in container) and redeployed.
- **Live verification 2026-05-01 19:59:58Z (flip) → 2026-05-04 (3 days):** all 4 fetcher actors flipped to `mode=cron_runner` via `PUT /api/actors/<id> --data '{"mode": "cron_runner"}'`. cron_runner exec + success log lines visible in runtime logs for all 4. **3-day soak: 1863 cron_runner completions (Email 770, Meeting 259, Drive 65, Slack 769); 0 LangSmith traces for any of the 4 fetcher associates since 20:01:00Z.** ~1000 LLM calls/day eliminated.

**Outcome (Bug #48 — surfaced during Bug #40 verification):**

- **Surfaced from:** Slack-Fetcher cron_runner exec hit 404 on `indemn slackmessage fetch-new`. Server-side route is `/api/slack_messages/` (Bug #39 Session 15 fix); CLI client was hitting `/api/slackmessages/` (naive plural).
- **Two-part fix:**
  - `kernel/api/meta.py::get_entity_metadata` (list endpoint) — added `collection` field via `_route_slug_for(name, cls)`. Detail endpoint `get_entity_detail_metadata` had `collection` but used the broken `cls.Settings.name if hasattr(cls, "Settings") else entity_name.lower() + "s"` fallback (which returned naive plural for every domain entity). Replaced with `_route_slug_for(entity_name, cls)`.
  - `indemn_os/src/indemn_os/main.py` — split `cli_name = name.lower()` (singular Typer subcommand — operators still type `indemn slackmessage list`) from `slug = meta.get("collection") or (cli_name + "s")` (URL collection slug). All `f"/api/{slug}s/..."` templates → `f"/api/{slug}/..."`. `register_bulk_commands(name, entity_app, url_slug=slug)` plumbs the URL slug to bulk_commands.
  - `indemn_os/src/indemn_os/bulk_commands.py` — accepts `url_slug` kwarg.
- **9 unit tests:** `tests/unit/test_meta_collection_field.py` × 4 + `tests/unit/test_cli_url_slug_resolution.py` × 5. Source-level pins via `inspect.getsource`.
- **Deployment:** indemn-api + indemn-runtime-async redeployed.
- **Live verified:** `indemn slackmessage list --limit 3` returns 3 entries (was 404 pre-fix); `indemn slackmessage fetch-new` returns `{fetched: 1, created: 0, errors: []}`; runtime cron_runner success log on Slack-Fetcher.

**Outcome (Bug #49 — surfaced during 3-day soak EOS):**

- **Initially framed as:** "Bug #38 orphan cleanup, not a real cron_runner failure." 11 dead_letter messages over 3 days (5 Email + 6 Slack + 0 Meeting/Drive — Slack-heavy) all marked with the cleanup error message.
- **Direct investigation via Temporal CLI:** `temporal workflow describe msg-69f81d4a1f2c3ee82ecb65bf` returned `Status: FAILED, Failure: Activity task timed out → Cause: activity Heartbeat timeout`, RunTime 8m15s. Confirmed root cause is heartbeat timeout, not infrastructure restart.
- **Root cause:** `process_with_associate` activity has `heartbeat_timeout=timedelta(seconds=90)` (per `kernel/temporal/workflows.py`). The agent path runs `_heartbeat_loop` that fires `activity.heartbeat()` every 30s during `agent.ainvoke()`. The cron_runner branch shipped in Bug #40 v1 had NO heartbeat — `run_cron_skill` (sync) blocked on `subprocess.run`. Fetches under 90s succeeded; fetches over 90s (Slack with rate-limited channels) hit heartbeat_timeout, activity cancelled, both retries hit identical timing, workflow ended FAILED, message orphaned at status=processing → visibility timeout → next dispatch sweep → WorkflowAlreadyStartedError → Bug #38 cleanup → dead_letter. **The Slack > Email > 0 split is the predicted pattern** (Slack fetches slowest).
- **Fix:** in `harnesses/async-deepagents/main.py::process_with_associate`'s cron_runner branch, mirror the agent path: `activity.heartbeat("starting_cron_runner")` immediately, then `asyncio.create_task(_cron_heartbeat_loop)` (sleeps 30s + heartbeats), wrap sync `run_cron_skill` in `await asyncio.to_thread(...)` so the heartbeat runs concurrently. Cancel + await heartbeat task in finally. Activity-level concern lives in the calling activity — keeps `run_cron_skill` sync + simple.
- **OTEL span added in same fix:** `cron_runner.run` span in `cron_runner.py` via `opentelemetry.trace.get_tracer(__name__)` with attributes `associate.id`, `associate.name`, `message.id`, `entity.type`, `argv`, `tool`, `result.fetched|created|skipped_duplicates`, `result.errors_count`, `outcome`. Span lives under the parent activity span (TracingInterceptor) so the full chain is queryable in Grafana by trace_id. Per vision §2 item 7 — OTEL is canonical for system-level observability; LangSmith stays for AI-agent observability and the 0 LangSmith traces for cron_runner runs are the correct state, not a gap.
- **3 new tests:** `test_process_with_associate_heartbeats_cron_runner_branch` (source-level pin on the heartbeat shape) + `test_run_cron_skill_emits_otel_span_with_attributes` + `test_run_cron_skill_otel_span_records_failure_outcome` (using `opentelemetry.sdk.trace.export.in_memory_span_exporter`).
- **Deployment:** indemn-runtime-async redeployed. Verification: 24-48h post-deploy expectation is dead_letter rate drops to near-zero; Bug #38 orphans from genuine runtime restarts will still occur but should be << 11/1863.

**Side-fixes:**
- **Bug #12 re-fix** — AWS Secret `indemn/dev/shared/mongodb-uri` was reverted between Session 15 and Session 16 (host back to broken `dev-indemn-pl-0`). Re-applied the same fix (pull working URI from chat-deepagents Railway env, `aws secretsmanager update-secret`). No code change. Open question: what reverted it? Worth a pre-session-hook validation script.
- **Slack Integration recovery** — found at `status=error` (auto-transitioned 2026-05-01 18:53:00Z, before Session 16 started). Walked `error → configured → connected → active`. Stayed active through 769+ Slack-Fetcher cron_runner completions over 3 days — one-off, not recurring. Root-cause investigation deferred (couldn't pin the kernel handler that transitioned it to error).

**Test counts:**
- Pre-session: 510 unit tests (kernel) + 60 harness = 570 total.
- Post-session: **527 unit tests** (kernel — 9 new for Bug #48 + 8 retest growth from earlier work) + **85 harness tests** (60 → 85 — 25 cron_runner tests for Bug #40/#49 = 22 v1 + 3 for OTEL + heartbeat). Total: **612 tests, 611 passing** (1 pre-existing pollution failure on `test_effective_actor_id::test_harness_cli_wrapper_propagates_effective_actor_to_subprocess`, orthogonal — passes in isolation, fails when run with full suite due to module-level sys.modules.setdefault stubbing in `test_agent.py`; documented in os-learnings Bug #41 row).

**Touched (files / entities):**
- Indemn-os main commits pending push (2 logical commits):
  - **Bug #40 + #49** — `M kernel_entities/actor.py`, `?? harnesses/async-deepagents/cron_runner.py`, `M harnesses/async-deepagents/main.py`, `?? harnesses/async-deepagents/tests/test_cron_runner.py`, `M harnesses/async-deepagents/tests/test_load_message_context.py`
  - **Bug #48** — `M kernel/api/meta.py`, `M indemn_os/src/indemn_os/main.py`, `M indemn_os/src/indemn_os/bulk_commands.py`, `?? tests/unit/test_meta_collection_field.py`, `?? tests/unit/test_cli_url_slug_resolution.py`
- Operating-system worktree changes (this commit):
  - 4 fetcher skill files (3 NEW, 1 modified): `projects/customer-system/skills/{email,meeting,drive,slack}-fetcher.md`
  - Project docs: `CURRENT.md` (rewritten), `SESSIONS.md` (this entry), `os-learnings.md` (Bug #40 close + Bug #48 NEW + Bug #49 NEW + Bug #12 regression note + Bug #45-family followup), `roadmap.md` (Where we are now), `CLAUDE.md` (§ 5 Journey entry), `INDEX.md` (Decisions / Open Questions / Artifacts)
- Dev OS state: 4 fetcher actors flipped to `mode=cron_runner`; 4 fetcher skills updated to v3; Slack Integration walked back to active; AWS Secret `indemn/dev/shared/mongodb-uri` corrected
- Production touched: indemn-api (×2), indemn-queue-processor, indemn-temporal-worker, indemn-runtime-async (×4 — initial + import fix + Bug #48 + Bug #49)

**Handoff to next session:** Use `PROMPT.md` as kickoff. **TD-2 cascade activation begins.** 4 NEW associates to build (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher) per `roadmap.md § TD-2`; update EC v9 → v10 (signature parsing + ReviewItem-on-ambiguity); update TS v6 → v7 (Deal-creation + atomic Proposal-at-DISCOVERY + multi-Deal ambiguity → ReviewItem); IE full-cascade verification; activate progressively bottom-up; systematic historical replay across ~930 emails + 67 meetings + 860 SlackMessages. Trace-as-build-method per CLAUDE.md § 2 — for each new associate: pick a real scenario (Armadillo's Apr 28 discovery meeting for MC; Apr 7-8 Retention Associate Slack thread for SC; Armadillo's processed Touchpoints for PH; Armadillo's bare Company for CE), trace manually first via CLI, write skill from what worked, activate after the trace produces correct state. Multi-session work; close cleanly per session. **Plus 24-48h Bug #49 verification** — confirm dead_letter rate dropped to near-zero on cron_runner runs after the heartbeat fix deployed today.

---

## Pricing Framework Session 3 — 2026-05-04 — Phase C LOE pass complete across channels, systems, tool skills, and pathway skills

**Workstream:** Cam-assigned pricing framework action item. Continuation of Pricing Framework Session 2.

**Objective:** Complete Phase C — populate first-customer LOE and per-customer-after-first LOE for every catalog entry. Hours only, no money. Craig authors estimates; assistant captures structure.

**Outcome:**

- **Phase C complete.** §10 populated for all 4 catalogs: 8 channels · 28 systems · 57 tool skills · 46 non-merged pathway skills.
- **Systems catalog corrected:** ECM Portal removed as a separate system per Craig — "this isn't a thing, we don't use the ECM portal." Applied Epic remains the Johnson web-operator system. Catalog now consistently has 28 systems.
- **Channel LOE captured:** Web chat 10/10 · Outlook email 15/15 · outbound email +2/+2 · inbound voice 15/15 · outbound voice 20/5 · SMS 10/10 · schedule 5/5 · Teams 15/15.
- **Systems LOE captured:** all systems in §10.2 now have first/repeat estimates. Important defaults/anchors: general APIs 30/15 unless overridden; web operators have larger setup (Unisoft 40/10, Applied Epic 80/20); internal/platform/3rd-party services vary by setup complexity.
- **Tool skills LOE captured:** all 57 tool skills in §10.3 now have first/repeat estimates.
- **Pathway skills LOE captured:** all 46 non-merged pathway skills in §10.4 use Craig's Phase C assumption: pathways are generally sequences of steps; understanding/refining them is 30h first-customer and 15h subsequent. Bulk implementation work is already captured in channel/system/tool estimates.
- **Phase D started:** §11.1 Cam sheet update spec drafted (6 tabs, row keys, columns, formula contract) + §11.1.9 computability checks drafted for 5 representative examples + §11.2 HTML UI visualization plan drafted (views, visual language, normalized data contract). §11.3 now locks the data-shaping path: hand-author normalized JSON first, validate it against the local schema, then export the testing sheet + HTML from the same object. Local draft data object now exists with §10 catalogs, 13 customers, 4 gaps, and 5 fixture checks. Working doc §0 and CURRENT now point future sessions to the §9 associate-row pass instead of Phase C.
- **Phase D mental model captured:** `2026-05-04-pricing-framework-mental-model.md` records the key reframe from Craig: Cam's associate catalog is the familiar commercial surface, but it is not expressive enough by itself to describe implementation reality. The visual should bridge catalog rows to pathway skills, tool skills, systems/adapters, channels, customer proof, reuse/net-new status, LOE, and the OS structure. Qualifier questions and core-offering recommendations are downstream outputs of making that model visible, not the first-order artifact.
- **Visual v0 created:** `2026-05-04-pricing-framework-visual-v0.html` is a self-contained concept artifact using five representative examples (INSURICA Renewal, GIC/Johnson Intake for AMS, JM Quote & Bind, Tillman Front Desk, Branch Document Fulfillment gap). It starts with the mental model, then renders catalog-shaped rows with expandable implementation anatomy, customer proof, reusable inventory, and gap/net-new views.
- **Visual v1 created:** `2026-05-04-pricing-framework-visual-v1.html` supersedes v0 for review. It reflects Craig's correction that the visual is many-to-many and calculator-like: one associate has many configurations, and each configuration has many component rows. The core table now avoids list cells and renders one component per row, with subtotal/total equations and separate inventory relationship tables for channels, systems, pathway skills, and tool skills.
- **Visual v2 created:** `2026-05-04-pricing-framework-visual-v2.html` supersedes v1 for review. It reflects Craig's correction that the independent component inventories should be primary: web chat is web chat regardless of associate; systems/channels/pathways/tools have standalone LOE rows; an associate configuration is a recipe that references those rows. V2 shows all Phase C channels and systems, sample pathway/tool slices for the five recipes, selected recipe tables grouped by component type, and an LOE equation.
- **Visual v3 created:** `2026-05-04-pricing-framework-visual-v3.html` supersedes v2 for review. It keeps v2's independent component model but adds the missing orientation: the full 55-row associate catalog is visible on the left, an explicit equation strip shows Associate + Pathways + Tools + Channels + Systems = LOE, the center shows selected recipes/building blocks, the right shows the selected LOE calculator, and the bottom keeps independent component inventories.
- **Visual v4 created:** `2026-05-04-pricing-framework-visual-v4.html` supersedes v3 for review. It separates standard pathway skill templates from customer deployment instances: pathway skills own tool skill usage and compatible system categories, while deployments select actual channels and customer systems. The default lens is now Customer Deployment Map, with Associate Catalog, Pathway Skill Catalog, Calculator, and Component Inventories as supporting views.
- **Visual v5 created:** `2026-05-04-pricing-framework-visual-v5.html` supersedes v4 for review. It collapses the associate catalog and component inventories into one Raw Catalog Explorer, keeps Customer Deployment Map as the primary big-picture lens, and replaces the single-choice calculator with a multi-select Configuration Builder that mirrors deployment detail: associate + selected pathway skills + derived tool skills + selected channels + selected systems = LOE.
- **Full staging data generated:** `build-pricing-framework-staging-data.js` now parses §9 into all 55 associate rows, retains raw pathway/tool/channel/system text, maps known §10 component IDs where inferable, generates 63 staging pathway IDs directly from prose-defined §9 pathways without existing `path-*` references, adds system categories, enriches customer rows, derives 50 customer-deployment rows from customers-active mappings, preserves the 5 computability fixtures, and exports a local CSV testing-sheet pack under `2026-05-04-pricing-framework-testing-sheet/`. Current coverage: 166 skills total, 10 mapped associate rows, 3 mapped-with-derived rows, 42 derived-pathway rows, 0 `needs_review` rows.
- **Visual v6 generated from staging data:** `2026-05-04-pricing-framework-visual-v6.html` supersedes v5 for review. It keeps the v5 visual model but replaces the hardcoded sample data with the full generated staging object: 55 associates, 50 customer deployments, 109 pathway skills (46 canonical + 63 §9-derived), 57 tool skills, 8 channels, and 28 systems. The customer deployment map, raw catalog explorer, and multi-select configuration builder now all read from the same staging JSON.

**Touched (files / entities):**
- Modified: `projects/customer-system/artifacts/2026-04-30-associate-pricing-framework.md` (§0 handoff refreshed, §10 LOE tables populated, §11 Phase D sheet/UI spec + computability checks drafted)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-mental-model.md` (Phase D visual/mental-model artifact for Cam/Kyle catalog-to-component bridge)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-visual-v0.html` (self-contained Phase D HTML concept artifact)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-visual-v1.html` (construction/calculator HTML concept artifact; current review target)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-visual-v2.html` (independent-inventory + associate-recipe HTML concept artifact; current review target)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-visual-v3.html` (associate-catalog + equation-workspace HTML concept artifact; superseded for review by v4)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-visual-v4.html` (customer-deployment + pathway-template HTML concept artifact; superseded for review by v5)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-visual-v5.html` (unified raw-catalog + deployment-shaped builder HTML concept artifact; superseded for review by v6)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-visual-v6.html` (generated full-catalog review artifact backed by staging JSON; current review target)
- Added/modified: `projects/customer-system/artifacts/2026-05-04-pricing-framework-staging-data.schema.json` (Phase D normalized object contract for testing sheet + HTML; includes raw §9 fields, system categories, and customer-deployment rows)
- Added/modified: `projects/customer-system/artifacts/2026-05-04-pricing-framework-staging-data.json` (draft normalized object: 55 associates, 50 derived deployments, 166 skills including 63 §9-derived pathways, catalogs, customers, gaps, calculation fixtures)
- Added: `projects/customer-system/artifacts/2026-05-04-pricing-framework-testing-sheet/` (local CSV testing-sheet pack generated from staging data)
- Added/modified: `projects/customer-system/tools/build-pricing-framework-staging-data.js` (local builder; extracts §10 catalogs, parses §9 associate rows, verifies fixtures, exports testing sheet CSVs)
- Added: `projects/customer-system/tools/build-pricing-framework-visual-v6.js` (local visual builder; injects staging JSON into the v5 visual model to produce v6)
- Modified: `projects/customer-system/tools/package.json` (added `build:pricing-staging-data` and `build:pricing-visual-v6` scripts)
- Modified: `projects/customer-system/CURRENT.md` (Pricing Framework state updated: Phase C complete, Phase D in progress)
- Modified: `projects/customer-system/SESSIONS.md` (this entry)
- No OS entity changes
- No production changes

---

## Pricing Framework Session 2 — 2026-05-01 — Phase A close (4 customers walked) + §7 catalog audit + Phase B sweep across all 55 Cam rows + 5-phase plan locked

**Workstream:** Cam-assigned action item from Apr 30 pricing call (Pricing Framework). **Parallel side-project to TD-1**, not part of main customer-system roadmap. Continuation of Pricing Framework Session 1 (commit `381b773`).

**Objective:** Continue customer walk from 9 → 13 (Rankin · Tillman · Family First · Alliance), audit §7 pathway skills for framework consistency, sweep all 47 deployable + 8 in-development Cam rows for Phase B, lock the multi-phase plan structure for the rest of the work.

**Parallel sessions during:** None on this workstream. (TD-1 Session 15 ran in parallel earlier in the day in a different worktree, fully closed TD-1 — separate workstream, no cross-impact.)

**Outcome:**

- **Phase A complete (13 of 13 active customers walked).** New customers Session 2: 8.9 Rankin (Front Desk + Lead — Easy Links AMS · IIANC cohort) · 8.10 Tillman (Front Desk bilingual + Lead bilingual — Hawksoft AMS · IIANC · pre-revenue) · 8.11 Family First (Knowledge — caregiving Care Library Q&A; healthcare/caregiving outlier mapped to Agency/Broker per Craig) · 8.21 Alliance (Front Desk + Lead + Ticket internal "State of the Agency"; reclassified active customer per Craig — "if we built it, they're a customer to me"). 5 prospects (GR Little, Armadillo, FoxQuilt, Charley, Physicians Mutual) confirmed **out-of-scope** for this work.
- **§7 catalog audit — 9 pathway-skill consolidations applied** (55 → 46 pathway skills): 3 channel-split merges (path-025/026 · 037/038 · 040/041) · 1 escalation merge (path-013 → path-012) · 1 intake-disambiguation merge (path-029 → path-025) · 1 LOB-split merge (path-045 → path-044) · 3 KB-scope merges (path-017/018/022 → path-016). Merged entries kept as numbered placeholders for audit trail per never-delete-history discipline. Skills-not-channel-scoped rule enforced retroactively.
- **Phase B sweep complete across all 55 Cam rows** (47 deployable + 8 in-development). §9.1 Agency/Broker (13 rows) · §9.2 Carrier (14 rows) · §9.3 MGA (20 rows) · §9.4 Z in-development (8 rows). Per-row redundancy applied per Craig 2026-05-01: each row writes pathway skills + tool skills + channels + systems + customers active + status fully, even when content shared across Cam rows. Functional-emphasis distinction settled for Authority + Submission + Intake (MGA Rows 32 + 46 + 34): three lifecycle gates (pre-bind compliance · pre-carrier-submission eligibility filter · data flow at arrival), UG bundles all three.
- **5-phase plan locked:** A Customer walks (✅) → B Per-associate sweep (✅ this session) → C LOE pass per catalog entry (hours only, no money — Craig authors, I capture structure) → D Output presentation (Cam sheet update spec + HTML UI visualization) → E OS data-model bounce-off (put framework into operating system to bounce customer/associate/skill data models).
- **New tool skills added:** tool-049 Business-hours lookup (@bizHoursLookup / @checkBusinessHours — Rankin + Tillman) · tool-050 Bilingual handling / linguistic compass (Tillman) · tool-051 Auto · tool-052 Property · tool-053 Life · tool-054 Business · tool-055 Event · tool-056 Pet insurance intakes (Tillman per-product) · tool-057 Emergency redirection (Family First — 911/988/Poison Control routing). 8 new tool skills.
- **New systems catalog entry:** Embedded chat in partner surface (Zola pattern — JM Dahlia for Zola; per Craig 2026-05-01 — Systems-catalog item, not a separate Cam row).
- **Decisions captured:**
  - Cam catalog rows are official; we don't merge them (redundancy per row when skills are shared).
  - Dashboard Associate + Strategy Studio (across 3 tiers) ARE conversational associates (talk with staff/builders), not infrastructure.
  - Compliance Audit Trails + Secure Data Integration + E&O Risk Mitigation ARE infrastructure (kernel-provided), not runtime associates.
  - Skills are NOT channel-scoped (caught on Tillman's voice/web channel-split path entries; applied retroactively across catalog).
  - Each new carrier × workflow = new skill instance (per Craig's Working Copy on Intake-for-AMS).
  - Cohesive end-to-end sequence within one associate is ONE good pathway (path-003 GIC submission-into-AMS as canonical example) — don't break up just because it has multiple steps.
  - Functional emphasis differs across Authority/Submission/Intake (lifecycle gates, not duplicates).

**Catalog state at close:** 8 channels · 28 systems · 57 tool skills · 46 pathway skills · 4 catalog gaps tracked.

**Discipline notes (Session 2):**
- **Hydration miss** caught early — I claimed "all required files read" when I had skipped roadmap.md, os-learnings.md, CURRENT.md, SESSIONS.md, and most of the pricing-framework artifact. Craig caught it; I read everything before continuing. Per CLAUDE.md § 7 pre-flight discipline.
- **Channel-split discipline gap** — wrote Tillman with 4 channel-split path entries despite the rule being in §3 of the framework doc. Craig caught it; consolidated to 2 paths + applied retroactively across §7 (9 consolidations). The rule was internalized only after the correction.

**Handoff to Pricing Framework Session 3:**

Begin **Phase C — LOE pass per catalog entry**. Hours only, no money. Collaborative — Craig authors estimates, I capture structure. Recommended order: channels (8 entries, smallest catalog) → systems (28) → tool skills (57) → pathway skills (46). Anchors for Craig's authoring already exist in Appendix A (Working Copy annotations: Renewal Associate 30 + 30-50 hrs, Knowledge Associate 8-12 hrs, etc.).

After Phase C: Phase D output presentation (Cam sheet update spec + HTML UI visualization).

**Touched (files / entities):**
- Modified: `projects/customer-system/artifacts/2026-04-30-associate-pricing-framework.md` (4 new §8 customer entries + §9 sweep across all 55 rows + §7 catalog audit + 5-phase plan structure in §0/§9/§10/§11/§12 + §6 systems catalog Zola entry)
- Modified: `projects/customer-system/CURRENT.md` (Workstream A section refreshed)
- Modified: `projects/customer-system/SESSIONS.md` (this entry)
- No OS entity changes
- No code commits

---

## Session 15 — 2026-05-01 — TD-1 fully closed (Slack-Fetcher activation, voice harness v2 canonical rebuild + Railway deploy, chat + voice CLI-only skill loading, 7 OS bugs resolved)

**Objective:** Close out TD-1 from Session 14's ~85% state. Two priorities from PROMPT.md kickoff: (1) Bug #45 — debug Slack `resolve_integration()` to unblock Slack-Fetcher; build slack_fetcher role + skill + actor; activate; (2) voice-deepagents v2 canonical rebuild — DELETE v1 + REBUILD mirroring chat-deepagents. After both: TD-1 done-test verification + close. Then resolve all open OS bugs before session close per Craig's directive ("we want to resolve all the bugs before we close out the session").

**Parallel sessions during:** Pricing Framework Session 1 ran in parallel in `.claude/worktrees/gic-feature-scoping/`. Closed earlier in the day (commit `381b773`). Did NOT modify TD-1 state. CURRENT.md was rewritten by that session into a dual-workstream structure, preserved here.

**Outcome:**

- **TD-1 fully closed.** All 4 fetcher actors active and autonomous. Voice + chat round-trips both create real Touchpoints in dev OS via `log-touchpoint` skill. All TD-1 done-test items passing.
- **Bug #45 resolved as DUAL fix.** (a) Slack Integration was created with `access: null` → resolver Step 3 query (`access.roles: {$in: role_names}`) silently failed against the null path. Workaround: patch the live Integration with `access.roles=["team_member","platform_admin"]`. (b) Slack adapter's `register_adapter("messaging", "slack", SlackAdapter)` passed (system_type, provider) instead of (provider, version) — registered at key `messaging:slack` instead of `slack:v1`. Code fix: `register_adapter("slack", "v1", SlackAdapter)` (`eea170d`). Both layers verified live.
- **Bug #45c (NEW kernel-design fix).** Resolver Step 3 query now uses `$or` with branches for: explicit role match, null `access`, missing `access`, missing `access.roles`, empty `access.roles` list. Plus better error message via `Integration.find().count()` diagnostic when integration exists but doesn't match. Future org integrations created without explicit gating Just Work. (`5036bc1`)
- **Bug #46 (NEW).** Kernel `fetch_new` watermark was hardcoded to `entity.date`. Silently broken for SlackMessage (`posted_at`) + Document (`created_date`). Drive-Fetcher had been re-fetching same files hourly for ~17h. Fix: candidate-field list `("date", "posted_at", "created_date")` in `WATERMARK_FIELD_CANDIDATES`; per-candidate try/except. 8 unit tests pin the fallback chain. (`20c074c`) Verified live: Document fetch-new immediately surfaced 5 NEW Drive files post-fix.
- **Bug #47 (NEW).** chat-deepagents Railway env `INDEMN_SERVICE_TOKEN` was stale (didn't match AWS Secrets Manager value). Service had been failing startup with 401 for an unknown duration before this session. Discovered while attempting chat-side log-touchpoint test. Updated env var + redeployed; service healthy.
- **Voice harness v2 canonical rebuild + Railway deploy.** v1 (commit `62f47f9`) deleted; v2 mirrors chat-deepagents structure: `agent.py` (deepagents `create_deep_agent` + voice DEFAULT_PROMPT), `session.py` (VoiceSession with Interaction + Attention + 30s heartbeat + `indemn events stream` subprocess), `llm_adapter.py` (`DeepagentsLLM(LLM)` adapter wrapping the deepagents agent for LiveKit's AgentSession), `main.py` (LiveKit `WorkerOptions(entrypoint_fnc, prewarm_fnc)`). 17 unit tests (translation + extraction + DeepagentsLLM contract + event-queue drain). Indemn-os main commits `6671dea` (v2) + 7 follow-ups (`a35913f`, `0e1fff4`, `33d12f7`, `27e9304`, `fcdd8f8`, `cdc8479`). Deployed to NEW Railway service `indemn-runtime-voice` (id `df2349d6`). Multi-turn voice round-trip created real Touchpoint `69f4ed4f03e56394d808bc88` (Branch + Dan Spiegel + summary "discussed renewal pricing and timeline"). Full audio captured at `/tmp/voice-deepagents-run/audio-multi/`.
- **Chat-side log-touchpoint verified end-to-end.** Touchpoint `69f4f2ca03e56394d808bd6d` created via deployed `indemn-runtime-chat` after migration to CLI-only skill loading. Required Bug #47 fix first.
- **chat + voice harnesses migrated to CLI-only skill loading.** Mirrors async-deepagents `7281b83`. New `build_system_prompt(associate)` helper composes per-associate system prompts with `execute('indemn skill get <ref>')` directives. Drops the deepagents filesystem-skills layer entirely. Eliminates the Bug #35 class for both harnesses. 8 new unit tests in `chat-deepagents/tests/test_agent.py`. (`7197f08`)
- **`harness_common.cli` resolves indemn via `sys.executable`.** Eliminates the `/opt/homebrew/bin/indemn` (Node.js CLI from `@indemn/cli` npm package — only has `init`) collision that was silently breaking the harness in spawn-mode subprocesses. (`33d12f7`)
- **Voice DeepagentsLLM passes RunnableConfig with metadata + tags + run_name** (`27e9304`). Voice traces appear in `indemn-os-associates` LangSmith project queryable by associate_id / entity_id / runtime_id (per CLAUDE.md § 8). Verified live: trace `Voice OS Assistant → Interaction 69f4e424`.
- **Slack-Fetcher activation closes TD-1 sub-piece 4.** 90-day backfill via incremental `fetch-new` calls drained 860 SlackMessages spanning 2023-11-17 → 2026-05-01 across 4 channels (conversation-design 435, voice 217, customer-implementation 200, test-reports 8). Slack Fetcher actor `69f4a473a0cbb2f5d2d0386f` cron `*/5 * * * *` active and autonomous. First tick verified at 13:45:37Z (LangSmith trace `019de3c9-ab78-7383-b273-5c0d051d9431`).
- **Voice OS Assistant actor created.** id `69f4c62d03e56394d808b79c`. role=team_member, runtime=voice runtime, skills=["log-touchpoint"], mode=hybrid, status=active. Voice runtime service-token actor (`runtime-service:voice-deepagents-dev`) granted `harness_service` role for register-instance permission.
- **Bug #12 (mongodb-uri) closed.** AWS Secrets value `indemn/dev/shared/mongodb-uri` had wrong host (`dev-indemn-pl-0.mifra5.mongodb.net`); corrected to `dev-indemn.mifra5.mongodb.net` (pulled from chat-deepagents Railway env, which was the working production value). `mongosh-connect.sh` wrapper now connects cleanly.
- **Bug #13 (Railway docs) closed.** Doc was already corrected 2026-04-28; this session adds voice-deepagents + harness_common rows to the deploy table per development.md § 8. (`bee1a7e`)
- **Bug #39 (route slug) closed.** `register_entity_routes` honors `_collection_name` (operator override via `--collection-name`) and `Settings.name` (kernel Beanie entities) before falling back to naive plural. 5 new unit tests. (`00b7407`)
- **slack-fetcher skill** (NEW v1) at `projects/customer-system/skills/slack-fetcher.md`, uploaded to dev OS.
- **log-touchpoint skill v3** — entity-resolve param shape corrected from `{"name": ...}` to `{"candidate": {"name": ...}}` (matches kernel resolver contract; surfaced when first multi-turn voice test had agent calling resolve with the wrong shape).

**Major architectural lessons (Session 15):**

1. **Filesystem-skills layer is wrong shape for one-skill-per-associate associates.** Async-deepagents already migrated 2026-04-29 (commit `7281b83`); chat + voice followed this session. Three concrete benefits: eliminates Bug #35 class entirely (no path resolution against backend root_dir, no YAML escaping, no SKILL.md format), symmetric with how the agent loads entity skills + everything else in the OS, gives operators a system_prompt directive they can directly read.
2. **Subprocess env propagation in spawn-mode multi-process workers (LiveKit Agents) is unreliable for PATH.** `harness_common.cli` previously called `subprocess.run(["indemn", ...])` relying on PATH. Different binary (`/opt/homebrew/bin/indemn` is Node.js CLI) gets picked up sometimes. Fix: resolve absolute path via `sys.executable`'s parent dir at module load. Generalizable lesson for any harness shell-out.
3. **Kernel `fetch_new` watermark assumed `entity.date`.** New entity types (SlackMessage uses `posted_at`, Document uses `created_date`) silently re-fetched the same content every cron tick. Symptom invisible to logs (no error, just `created=0`). Surfaced only by running the actual flow on real backfilled data and noticing the drain pattern doesn't converge. Trace-as-build success.
4. **LiveKit Agents JobProcess crashes silently propagate "Read-only file system: /workspace".** Default `/workspace` directory only exists in Docker (the harness Dockerfile's `RUN mkdir -p /workspace`). For local dev `python -m harness.main`, macOS's read-only `/` makes `os.makedirs("/workspace/...")` fail. Fix: auto-fallback to `/tmp/indemn-workspace` when `/workspace` isn't writable. Bonus: `INDEMN_WORKSPACE_DIR` env override for explicit operator control.
5. **Resolver `access: null` → unreachable** is the wrong default for org integrations. Operator intent for null is "no role gate, any actor in this org can use it" — not "no access." Bug #45c fix uses $or to make both work.
6. **Three Touchpoints created via end-to-end test artifacts during the session** are kept in dev OS (not test-clean) — they document the verified behavior and serve as concrete examples for IE / TS-related future work. ID summary: voice round-trip `69f4ed4f03e56394d808bc88`, chat round-trip `69f4f2ca03e56394d808bd6d`, plus an earlier failed-then-recovered attempt `69f4e2c5...` from voice debugging.

**Bugs deferred to next session:**

- **Bug #40 (deterministic scheduled-actor execution path)** — the BIG one. Not closed. Per Craig: "We need to continue this in a new session and should think about bug 40 deeply there." Two design choices to weigh: (A) new `cron_runner` actor mode bypassing the LLM (skill = literal CLI command, ~5-7 file change) or (B) new `ScheduledActorWorkflow` peer to `ProcessMessageWorkflow` (cleaner architectural separation; ~2x the work). All 4 fetchers currently run via mode=hybrid + LLM agent for what should be deterministic shell exec. ~1000 LLM calls/day across 4 fetchers; functional but wasteful.
- **Bug #19 follow-on** (test fixture pattern improvement) — process improvement, no code action.

**Handoff to Session 16:** Use `PROMPT.md` as kickoff. Objective: deep design + implementation of Bug #40. Pick (A) or (B) with rationale, execute, deploy, verify all 4 fetchers continue working post-migration. Then begin TD-2 (cascade activation: build MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher; activate progressively bottom-up; systematic historical replay across the ~930 emails + 67 meetings + 860 SlackMessages).

**Touched (Session 15):**

*indemn-os commits to main (14):*
- `eea170d` `fix(adapters): register Slack adapter under (slack, v1) not (messaging, slack) — Bug #45b`
- `20c074c` `fix(capability): fetch_new watermark falls through date→posted_at→created_date — Bug #46`
- `6671dea` `feat(harnesses): voice-deepagents v2 — canonical pattern (deepagents + Interaction/Attention + DeepagentsLLM adapter) (Bug #44)`
- `a35913f` `fix(voice-deepagents): bootstrap + events drain + dep + tests verified end-to-end`
- `0e1fff4` `fix(voice-deepagents): runtime register at boot + workspace fallback + agent_name dispatch`
- `33d12f7` `fix(harness_common): resolve indemn binary via sys.executable, not PATH lookup`
- `27e9304` `feat(voice-deepagents): wire LangSmith metadata + tags + run_name`
- `fcdd8f8` `fix(voice-deepagents): Dockerfile CMD passes 'start' subcommand to agents.cli.run_app`
- `0e8c657` `fix(voice-deepagents): pre-download turn-detector model via huggingface_hub at build` (rolled back)
- `cdc8479` `fix(voice-deepagents): drop turn_detector — VAD-only for now`
- `7197f08` `refactor(harnesses): chat + voice load skills via CLI in DEFAULT_PROMPT — drop deepagents skills layer`
- `5036bc1` `fix(integration): resolver tolerates null/missing access on org integrations — Bug #45c`
- `00b7407` `fix(api): route generation honors explicit --collection-name override — Bug #39`
- `bee1a7e` `docs: add voice-deepagents + harness_common to Railway deploy table — Bug #13 followup`

*operating-system commits (in this end-of-session protocol commit):*
- `projects/customer-system/CURRENT.md` rewrite (Workstream B updated for Session 15)
- `projects/customer-system/SESSIONS.md` Session 15 entry (this entry)
- `projects/customer-system/os-learnings.md` updates: Bugs #44/#45/#45b/#45c/#46/#47/#39/#12/#13 row updates + #40 deferred-to-deep-design entry
- `projects/customer-system/roadmap.md` — TD-1 marked complete; "Where we are now" updated
- `projects/customer-system/CLAUDE.md` — Session 15 journey entry in § 5
- `projects/customer-system/INDEX.md` — Decisions, Open Questions, Artifacts updates
- `projects/customer-system/skills/log-touchpoint.md` — v3 entity-resolve param shape fix
- `projects/customer-system/skills/slack-fetcher.md` — NEW slack-fetcher skill content
- `projects/customer-system/artifacts/2026-04-30-voice-deepagents-runbook.md` — v2 rewrite

*Railway services updated:*
- `indemn-api` — 4 commits deployed (Bug #45b, Bug #46, Bug #45c, Bug #39)
- `indemn-runtime-chat` — service token corrected (Bug #47), CLI-only skill loading deployed
- `indemn-runtime-voice` (NEW) — built + deployed end-to-end

*OS state created (live in dev OS):*
- Voice OS Assistant actor (id `69f4c62d03e56394d808b79c`, status=active)
- Slack-Fetcher actor (id `69f4a473a0cbb2f5d2d0386f`, status=active)
- slack_fetcher role (id `69f4a428a0cbb2f5d2d03869`)
- slack-fetcher skill (id `69f4a456a0cbb2f5d2d0386e`)
- voice-deepagents-dev runtime walked configured → deploying → active
- runtime-service:voice-deepagents-dev actor granted harness_service role
- Slack Integration access.roles populated `["team_member","platform_admin","slack_fetcher"]`
- 860 SlackMessages backfilled
- 2 Touchpoints from end-to-end tests (`69f4ed4f...` voice; `69f4f2ca...` chat)
- log-touchpoke skill content_hash updated to v3

*AWS Secrets Manager updated:*
- `indemn/dev/shared/mongodb-uri` — host corrected (Bug #12)

*Audio artifacts (local-only, Mac):*
- `/tmp/voice-deepagents-run/audio/{user_question,greeting,response}.wav` — round-trip
- `/tmp/voice-deepagents-run/audio-multi/turn{1,2,3}_*.wav` — multi-turn

---

## Pricing Framework Session 1 — 2026-04-30 to 2026-05-01 — Side-project: walk current customers, reverse-engineer associate/skill/integration framework, map to Cam's catalog

**Workstream:** Cam-assigned action item from Apr 30 pricing call ("[Craig] Analyze Associate Usage" + "[Kyle + Craig] Analyze Customer Solutions"). **Parallel side-project to TD-1, not part of main customer-system roadmap.** Will end up driving augmentations to Cam's 47-row pricing spreadsheet so proposal generation becomes formulaic.

**Objective:** Build a framework that bridges what Indemn actually delivers (skills + integrations + channels composed into associates) with Cam's pricing catalog. Reverse-engineer from current customers first; sweep the catalog after. Output: an augmented Cam spreadsheet + framework rules.

**Parallel sessions during:** None on this workstream. (TD-1 ran in Session 14 same day; separate workstream — see entry below.)

**Outcome:**

- **9 of 18 customers walked** (12 active + 6 prospects-with-build-history; 8 AI_Investments dropped early per Craig). Done: GIC (8.1) · JM (8.2) · INSURICA (8.3) · UG (8.4) · Distinguished Programs (8.5) · Johnson (8.6) · Branch (8.7) · O'Connor (8.8) · Silent Sport (8.12, pilot state). Pending: Rankin (8.9) · Tillman (8.10) · Family First (8.11) · 6 prospects (8.21-8.26).
- **Framework rules established + applied retroactively:**
  1. Paths ARE skills (end-to-end process granularity)
  2. Two skill types: tool skill (atomic, high reuse) + pathway skill (workflow, medium reuse). Browser automation / field writes / navigation are IMPLICIT in `web operator` system integration type, not separate skills.
  3. Skill specificity is emergent (LOB / carrier / system / customer rule — encoded in skill name)
  4. Bundle-by-task rule: same agent multi-task = ONE associate; different agents different objectives = SPLIT. Applied retroactively (revisions to JM 3→2, UG Mobile Home 2→1, Silent Sport 2→1, Branch 2-bundled→5-distinct).
  5. Built-only catalog (don't include proposals; built = built regardless of "live" status)
  6. Implementation cost formula: `(channels) + (skills) + (systems)` at deal level
  7. Crawl/walk/run = customer-facing phasing language (immediate / near term / long term)
- **Catalog state at close:** 48 tool skills · 47 pathway skills · 8 channels · 27 systems · 4 catalog gaps tracked.
- **4 catalog gaps surfaced** in §2.05: Lead Associate for MGA tier · Quote & Bind for Agency/Broker tier · Document Fulfillment Associate (Branch Aria) · Claims Status Associate (Branch Colleen).
- **Discipline learned (load-bearing):** surface findings → discuss with Craig → only write to doc after agreement. Past-session failures: writing speculative LOE estimates, "NET NEW" claims, tier classifications, premature live-vs-prototype framing. Each got Craig pushback. **Pattern is: bring data + propose mapping + ask, then write only what's agreed.** This discipline is now codified in §0 of the working doc.
- **Per-customer process** standardized: OS (indemn CLI) + Drive (gog) + MongoDB tiledesk via SSM into prod-services + bot-service container + GitHub (gh) + Slack (#customer-implementation).
- **Bot tool URL location confirmed** at `configurationSchema.endpoint` and `executionSchema.actions[].url` — useful going forward for any future tool-URL extraction.
- **Operations_api repo identified** as the central proxy for ALL Indemn carrier API integrations (zurich, markel, chubb, bonzah, GIC Granada, insurica salesforce, joshu).
- **n8n.indemn.ai surfaced** as workflow automation layer hosting webhooks that wrap external APIs.
- **Comprehensive systems map built across 9 customers:** Granada Insurance · Unisoft AMS (web operator) · GIC PAS · Indemn Copilot · Salesforce · Nationwide PL/CL · ACIC · Northfield · Composio · Airtable (multiple bases) · Twilio · LiveKit · Cartesia · Google Cloud Translate · Stripe · n8n.indemn.ai · Branch GraphQL · Dialpad · Microsoft Power Automate · Microsoft Teams · plus Indemn-built customer-specific Railway services (claims-mcp-server, branch-ivr-webhook, branch-aria-documents, ug-apis, ug-service).

**Handoff to next pricing-framework session:**

Source of truth = `artifacts/2026-04-30-associate-pricing-framework.md § 0 Session Handoff`. Read that section first; it captures everything needed to continue.

Resume protocol:
1. Standard hydration via `PROMPT.md` (CLAUDE.md · vision.md · roadmap.md · os-learnings.md · CURRENT.md · indemn-os CLAUDE.md)
2. Read working doc § 0 (handoff) + § 2 (formula) + § 2.05 (catalog gaps) + § 8 (per-customer detail)
3. Read source-material artifact `2026-04-30-pricing-call-and-sheet-source-material.md` for Cam call decisions
4. Pick up at customer 8.9 Rankin

**Touched (files / entities):**
- Created: `projects/customer-system/artifacts/2026-04-30-pricing-call-and-sheet-source-material.md` (source material — Cam call + sheet schema)
- Created: `projects/customer-system/artifacts/2026-04-30-associate-pricing-framework.md` (working doc — primary handoff artifact)
- No OS entity changes
- No code commits

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
