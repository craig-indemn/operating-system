# Customer System — CURRENT

> **Fast-changing state.** What just happened, what's in flight, parallel sessions, blockers, next steps. Rewritten every session. Read this *after* CLAUDE.md to know where things actually stand right now.

**Last updated:** 2026-05-04 (end of Session 16 — Bug #40 + #48 + #49 closed; all 4 fetchers running cron_runner-mode autonomously LLM-free; 3-day soak verified 1863 completions / 0 LangSmith traces; cron_runner heartbeat + OTEL span shipped to close the dead_letter rate). Pricing Framework Session 3 closed in parallel — Phase D staging-data path locked.

---

## ACTIVE PARALLEL WORKSTREAMS

There are **two parallel customer-system workstreams** active right now:

### Workstream A — Pricing Framework (Cam-assigned action item; SIDE-PROJECT but high-value)

**Source of truth:** `artifacts/2026-04-30-associate-pricing-framework.md` § 0 Session Handoff

**Status (2026-05-04):** **Pricing Framework Session 3 Phase C complete; Phase D in progress.** Phase A + Phase B + Phase C complete. **All 13 active customers walked + all 55 Cam rows swept + all LOE tables populated.** 5 prospects out-of-scope per Craig 2026-05-01. **Phase D §11.1 Cam sheet update spec + §11.2 HTML UI visualization plan drafted; §11.3 locks the hand-authored normalized staging-data path; local draft data object now exists.**

| # | Customer | Status |
|---|---|---|
| 8.1 | GIC | ✅ |
| 8.2 | JM | ✅ |
| 8.3 | INSURICA | ✅ |
| 8.4 | UG | ✅ |
| 8.5 | Distinguished Programs | ✅ |
| 8.6 | Johnson | ✅ |
| 8.7 | Branch | ✅ |
| 8.8 | O'Connor | ✅ |
| 8.9 | Rankin (Session 2) | ✅ |
| 8.10 | Tillman (Session 2) | ✅ |
| 8.11 | Family First (Session 2) | ✅ |
| 8.12 | Silent Sport (pilot) | ✅ |
| 8.21 | Alliance Insurance Services (Session 2 — reclassified active customer per Craig) | ✅ |
| 8.22–8.26 | GR Little, Armadillo, FoxQuilt, Charley, Physicians Mutual | 🔒 out-of-scope |

**5-phase plan locked:**
| Phase | What | Status |
|---|---|---|
| A | Customer walks | ✅ Complete |
| B | Per-associate sweep (47 deployable + 8 in-dev rows; per-row redundancy applied) | ✅ Complete (Session 2) |
| C | LOE pass per catalog entry — hours only, no money; collaborative (Craig authors, I capture) | ✅ Complete (Session 3) |
| D | Output presentation — Cam sheet update spec + HTML UI visualization | 🟡 In progress (§11.1/§11.2 drafted; §11.3 staging-data path locked) |
| E | OS data-model bounce-off — put framework into operating system to bounce customer/associate/skill data models | ⏳ After / with D |

**Catalog state (post-Session 3):** 8 channels · **28 systems** (added Zola embedded-chat; removed ECM Portal as a separate system per Craig 2026-05-01 — not used as a system) · **57 tool skills** · **46 pathway skills** (post §7 audit — was 55, consolidated 9 channel-split / lumped / LOB-split / KB-scope merges) · 4 catalog gaps tracked. **LOE populated for all catalog entries in §10.**

**Key framework rules locked (Session 1 + Session 2):**
- Paths ARE skills (end-to-end, not function-call-level; cohesive sequence within one associate is one good pathway — not broken up just because it has multiple steps)
- Two skill types: tool skill (atomic, high reuse) + pathway skill (workflow, medium reuse). Browser automation / field writes / navigation are IMPLICIT in `web operator` system integration type, NOT separate tool skills.
- **Skills are NOT channel-scoped** (Session 2 — Tillman correction). Same skill deployed across multiple channels is one skill, not multiple.
- Skill specificity emerges per case (LOB / carrier / system / customer rule)
- Bundle-by-task rule: same agent multi-task = ONE associate; different agents different objectives = SPLIT
- Built-only (don't include proposals or planned things; built includes prototypes)
- Implementation cost = (channels) + (skills) + (systems), with channels/systems at deal level
- **Cam catalog rows are official — we don't merge them** (Session 2). When skills are shared across rows, each row writes its skills out redundantly.
- **Each new carrier × workflow = new skill instance** (per Craig's Working Copy on Intake-for-AMS)

**4 catalog gaps tracked (unchanged this session):**
1. Lead Associate for MGA tier (surfaced at JM, UG, Branch)
2. Quote & Bind for Agency/Broker tier (surfaced at Silent Sport)
3. Document Fulfillment Associate (surfaced at Branch — Aria)
4. Claims Status Associate (surfaced at Branch — Colleen)

**§7 catalog audit (Session 2):** 9 pathway-skill consolidations applied — 3 channel-split merges (path-025/026, 037/038, 040/041) · 1 escalation merge (path-013→012) · 1 intake-disambiguation merge (path-029→025) · 1 LOB-split merge (path-045→044) · 3 KB-scope merges (path-017/018/022→016). Merged entries kept as numbered placeholders for audit trail.

**Resume protocol for next Pricing Framework session (Phase D continuation):**

1. **Hydrate** — standard PROMPT.md set (customer-system CLAUDE.md · vision.md · roadmap.md · os-learnings.md · CURRENT.md · SESSIONS.md · indemn-os CLAUDE.md). Skim §8 + §9 in the working doc but **don't re-read in full** unless authoring a specific row.
2. **Focus reads** — `artifacts/2026-04-30-associate-pricing-framework.md` §0 Session Handoff + §2 Formula + §4 End-state sheet design + §9 Per-associate sweep + §10 LOE tables + §11 Phase D output presentation.
3. **Confirm understanding back to Craig** — framework rules · 5-phase plan · Phase A/B/C complete · Phase D output goal.
4. **Review §11.1.9 computability checks** — five representative examples are drafted with first/repeat totals and traceable components. Validate component inclusion with Craig before using them in the staging sheet.
5. **Continue local staging data object** — `artifacts/2026-05-04-pricing-framework-staging-data.json` exists with §10 catalogs, 13 customers, 4 gaps, and 5 computability fixtures. Next: hand-author §9 associate rows into it, then export the testing sheet + HTML from that object. Rebuild with `npm --prefix projects/customer-system/tools run build:pricing-staging-data`.

**Discipline reminders for Phase D:**
- **Don't touch Cam's sheet** until §11 produces the migration spec and Craig signs off.
- Keep output hours-only unless Craig explicitly asks for money mapping.
- Preserve Cam catalog rows as official; redundant row-level skill listing remains intentional.

### Workstream B — Bug #40/#48/#49 closed; TD-2 next

State below is from **Session 16 close (2026-05-04)** — Bug #40 fully closed (cron_runner mode + heartbeat + OTEL span); Bug #48 (CLI URL slug) closed; Bug #12 re-fixed; Slack Integration recovered. Pricing framework session ran in parallel and did not modify any of this state.

---

## Top of roadmap

**Bug #40 + Bug #48 + Bug #49 COMPLETE.** All four scheduled fetchers (Email, Meeting, Drive, Slack) running `mode=cron_runner` since 2026-05-01 19:59:58Z. **3-day soak: 1863 cron_runner completions, 0 LangSmith deepagents traces, 11 dead_letter (all root-caused to Bug #49 — cron_runner heartbeat timeout — now fixed).** ~1000 LLM calls/day eliminated as designed.

**Next gate: TD-2 cascade activation begins.** 4 NEW associates to build (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher); update EC v9 → v10 (signature parsing + ReviewItem-on-ambiguity); update TS v6 → v7 (Deal-creation atomic with Proposal-at-DISCOVERY); IE full-cascade verification; activate progressively bottom-up; systematic historical replay across ~930 emails + 67 meetings + 860 SlackMessages. Designs are in `roadmap.md § TD-2`.

---

## Pipeline associate states (Session 16 changes)

| Associate | State | Notes |
|---|---|---|
| Email Classifier (EC) | **suspended** | Unchanged. Will activate in TD-2 (v9 → v10 with signature parsing + ReviewItem on ambiguity). |
| Touchpoint Synthesizer (TS) | **suspended** | Unchanged. Will gain Deal-creation + Proposal-at-DISCOVERY atomic in TD-2 (v6 → v7). |
| Intelligence Extractor (IE) | **active** | Unchanged. Inherits gemini-3-flash-preview/global. Will be verified through full cascade in TD-2. |
| **Email Fetcher** | **active, mode=cron_runner** | Flipped 2026-05-01 19:59:58Z. id `69f2bf30942e5629f07a8313`. */5 cron. **770 cron_runner completions in 3 days, 5 dead_letter (Bug #49 heartbeat timeout — fixed today), 0 LangSmith traces.** |
| **Meeting Fetcher** | **active, mode=cron_runner** | Flipped 2026-05-01 20:07:45Z. id `69f39ec6c0b340cf765a38d6`. */15 cron. **259 completions, 0 dead_letter, 0 LangSmith traces.** |
| **Drive Fetcher** | **active, mode=cron_runner** | Flipped 2026-05-01 20:07:45Z. id `69f3abbe268936150b46a0fa`. hourly. **65 completions, 0 dead_letter, 0 LangSmith traces.** |
| **Slack Fetcher** | **active, mode=cron_runner** | Flipped 2026-05-01 20:07:45Z. id `69f4a473a0cbb2f5d2d0386f`. */5 cron. **769 completions, 6 dead_letter (Bug #49 — fixed today), 0 LangSmith traces.** |
| Voice OS Assistant | **active** (mode=hybrid, unchanged from Session 15) | Used by Railway voice runtime for log-touchpoint flow. Not affected by cron_runner work. |
| Reviewer role | wired | Unchanged from Session 14. |

**4 NEW associates designed in Session 13's TD-2 alignment** — to be built when TD-2 executes (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher).

---

## Material state in dev OS (Session 16 changes)

**Hydrated customer constellations** (carried forward unchanged): GR Little, Alliance Insurance, Armadillo Insurance.

**Entity-state changes Session 16:**
- 4 fetcher actors flipped: `mode=hybrid` → `mode=cron_runner` (Email/Meeting/Drive/Slack-Fetcher).
- 4 fetcher skills updated to v3 cron_runner shape: `email-fetcher`, `meeting-fetcher`, `drive-fetcher`, `slack-fetcher` — pushed to dev OS.
- Slack Integration `69f3bb5097300b115e7236dd` walked `error → configured → connected → active` (recovery from a pre-session auto-error transition at 2026-05-01 18:53:00Z; details in os-learnings Bug #45-family followup).
- AWS Secret `indemn/dev/shared/mongodb-uri` re-fixed (Bug #12 regressed between Session 15 and Session 16 — secret was reverted to broken `dev-indemn-pl-0` host; restored to `dev-indemn` host).

**Entities ingested since cron_runner flip (3 days):**
- Emails: 506 (Email-Fetcher every 5 min)
- Meetings: 2 (Meeting-Fetcher every 15 min — low weekend activity)
- Documents: 1 (Drive-Fetcher hourly — low weekend activity)
- SlackMessages: 0 (Slack-Fetcher every 5 min — bot is in 4 channels; no new content over the soak window)

---

## Indemn-os main commits this session (Session 16)

**Pending end-of-session push** (uncommitted at the time of writing — git working tree on indemn-os main branch):

| Commit-to-be | What |
|---|---|
| (Bug #40 + #49 cron_runner) | `feat(harness): cron_runner actor mode + heartbeat + OTEL span — Bug #40, #49` — kernel_entities/actor.py mode Literal extended; harnesses/async-deepagents/cron_runner.py NEW (with `cron_runner.run` OTEL span); harnesses/async-deepagents/main.py branches on mode==cron_runner with concurrent heartbeat loop wrapping `asyncio.to_thread(run_cron_skill, ...)`; tests/test_cron_runner.py NEW (25 tests — parser × 11, executor happy + 7 failure modes × 8, sync-helper pin, mode-Literal pin, OTEL span × 2, heartbeat shape × 1); tests/test_load_message_context.py stub-list update for `harness.cron_runner`. |
| (Bug #48 CLI URL) | `fix(api+cli): meta endpoint surfaces collection slug; CLI honors it — Bug #48` — kernel/api/meta.py adds `collection` field to list + detail endpoints via `_route_slug_for`; indemn_os/src/indemn_os/main.py splits cli_name (singular Typer) from URL slug (collection from meta), all `/api/{slug}s/` → `/api/{slug}/`; bulk_commands.py accepts `url_slug` kwarg; tests/test_meta_collection_field.py + tests/test_cli_url_slug_resolution.py NEW (9 tests). |

Test count: 515 unit tests pre-session → **527 unit tests post-session** (3 new for Bug #48 in `tests/unit/`, plus 9 retest growth from earlier work + 3 new for Bug #40/#49 OTEL + heartbeat in harness tests). Plus 25 harness tests for cron_runner (60 → 85 in `harnesses/async-deepagents/tests/`).

---

## Railway deployments updated this session

| Service | What changed |
|---|---|
| `indemn-api` | Bug #40 (Pydantic Actor.mode Literal change) + Bug #48 (meta endpoint collection field). Deployed twice — once for Bug #40, once for Bug #48 on top. |
| `indemn-queue-processor` | Bug #40 (Pydantic Literal — needs to load Actor records with cron_runner mode). |
| `indemn-temporal-worker` | Bug #40 (Pydantic Literal — needs `load_actor` activity to handle cron_runner). |
| `indemn-runtime-async` | Bug #40 (cron_runner module + import path fix from `from cron_runner import` → `from harness.cron_runner import`) + Bug #48 (Dockerfile pip-installs indemn_os during build → harness picks up new client URL behavior) + Bug #49 (heartbeat loop + OTEL span). Deployed four times: initial + import fix + Bug #48 follow-on + Bug #49 follow-on. |

---

## OS bugs resolved this session

| Bug | Status before | Status after | Commit / artifact |
|---|---|---|---|
| **Bug #40** (no deterministic scheduled-actor execution path) | open from Session 14, deferred to Session 16 | 🟢 **fixed** — chose `cron_runner` actor mode (Option A) | indemn-os main commit pending push (cron_runner module + tests) |
| **Bug #48** (CLI URL slug ignores collection_name; client-side counterpart of Bug #39) | NEW — surfaced during Bug #40 verification on Slack-Fetcher 404s | 🟢 **fixed** — meta endpoint surfaces `collection`; CLI uses it | indemn-os main commit pending push (meta + indemn_os CLI + tests) |
| **Bug #49** (cron_runner doesn't heartbeat → 11 spurious dead_letters over 3 days) | NEW — surfaced during 3-day soak investigation; root cause confirmed via `temporal workflow describe` showing `Activity Heartbeat timeout` | 🟢 **fixed** — concurrent heartbeat loop wraps subprocess work; OTEL span added in same fix | indemn-os main commit pending push (heartbeat in main.py + OTEL in cron_runner.py + 3 new tests) |
| **Bug #12** (mongodb-uri AWS Secret host) | re-broken between Session 15 and Session 16 | 🟢 **re-fixed** | AWS Secrets Manager update (no code change) |
| **Bug #45-family followup** (Slack Integration auto-transitioned to error 18:53Z pre-session) | observed | 🟡 walked back to active; root cause not yet pinned | data fix; investigation logged in os-learnings (one-off — no recurrence over 769 Slack-Fetcher runs) |

**Bugs deferred (next session or beyond):**
- **Bug #19 follow-on** — process improvement (test fixture pattern), no code action.
- **Slack Integration auto-error root cause** — couldn't find the kernel handler that transitioned the integration to error. Since the 20:26Z reset + Bug #48 fix, no recurrences over 3 days. Worth investigating only if it recurs.
- **`kernel/cli/app.py` Bug #48 propagation** — parallel kernel-side CLI surface still uses naive plural for entity URL slugs. Same fix needed; lower priority since the harness uses `indemn_os/` CLI.

---

## Parallel sessions

**Pricing Framework session (parallel)** — running in `.claude/worktrees/gic-feature-scoping/`. Session 3 closed 2026-05-04 (Phase C complete; Phase D staging-data path locked). Did not modify any of Session 16's TD-1/Bug-#40/#48/#49 state.

**Currently no other parallel sessions.** Next session resumes single-thread.

---

## What just shipped (Session 16)

Session 16 closed Bug #40 + Bug #48 + Bug #49 end-to-end. The scheduled-actor execution path is now deterministic across all 4 fetchers — no LLM calls on cron ticks, ~1000 LLM calls/day saved, no spurious dead_letters from heartbeat timeouts.

### Bug #40 closure (cron_runner actor mode v1)

- **Design choice resolved:** Option A (`cron_runner` actor mode) over Option B (new `ScheduledActorWorkflow` peer). Rationale captured in os-learnings Bug #40 row.
- **Implementation:** Pydantic Literal extension on `Actor.mode`; new `harnesses/async-deepagents/cron_runner.py` module with `parse_command_from_skill` (extracts argv from skill's `## Command` section + bash fence + indemn-only allowlist) and `run_cron_skill` (validates trigger is synthetic `_*`, loads first skill via existing CLI, parses + execs, marks queue based on JSON `errors` field). Branch added in `process_with_associate` BEFORE the agent build.
- **22 unit tests in v1.** Skills migrated: all 4 fetcher skills rewritten to cron_runner shape and pushed to dev OS as v3 each.
- **All 4 fetcher actors flipped** to `mode=cron_runner` and verified end-to-end.

### Bug #49 closure (cron_runner heartbeat + OTEL span)

Surfaced during 3-day-soak dead_letter investigation. 11 dead_letter messages all marked "Bug #38 orphan cleanup" — initially framed as runtime-restart symptom. Direct Temporal investigation (`temporal workflow describe msg-69f81d4a1f2c3ee82ecb65bf`) showed the actual cause: `Status: FAILED, Cause: activity Heartbeat timeout`, RunTime 8m15s. cron_runner v1 had no `activity.heartbeat()` call; subprocess.run blocked the worker thread for the duration of the fetch; Temporal cancelled after 90s heartbeat_timeout; both retries hit same timing; workflow ended FAILED.

**Fix:** in `process_with_associate`'s cron_runner branch (main.py), wrap `run_cron_skill` in `await asyncio.to_thread(...)` and run a concurrent `_cron_heartbeat_loop` (sleeps 30s + heartbeats). `activity.heartbeat("starting_cron_runner")` fires immediately at branch entry. Cancel + await the heartbeat task in finally. Mirrors the agent path's pattern. Activity-level concern lives in the activity, NOT in cron_runner.py — keeps `run_cron_skill` sync + simple.

**OTEL span added in same fix:** `cron_runner.run` span via `opentelemetry.trace.get_tracer(__name__)` with attributes `associate.id`, `associate.name`, `message.id`, `entity.type`, `argv`, `tool`, `result.fetched|created|skipped_duplicates`, `result.errors_count`, `outcome`. Lives under the parent activity span (TracingInterceptor) so the full chain is queryable in Grafana by trace_id. Per vision §2 item 7 — OTEL is canonical for system-level observability; LangSmith stays for AI-agent observability and that's why cron_runner runs continue to show 0 LangSmith traces (correct state, not a gap).

**3 new tests** (heartbeat shape pin × 1, OTEL span × 2 using `InMemorySpanExporter`).

### Bug #48 closure (CLI URL slug)

- **Surfaced from:** Slack-Fetcher cron_runner exec hit 404 on `indemn slackmessage fetch-new`. Server-side route is `/api/slack_messages/` (Bug #39 fix); CLI client was hitting `/api/slackmessages/` (naive plural).
- **Two-part fix:** (1) `kernel/api/meta.py` list + detail endpoints surface `collection` field via `_route_slug_for`; (2) `indemn_os/src/indemn_os/main.py` + `bulk_commands.py` use `meta.collection` for URL construction, with `cli_name = name.lower()` kept for the singular Typer subcommand name.
- **9 unit tests** (source-level pins via `inspect.getsource`).
- **Live verified:** `indemn slackmessage list/fetch-new` now succeed; runtime cron_runner success log on Slack-Fetcher.

### Bug #12 re-fix

- AWS Secret `indemn/dev/shared/mongodb-uri` was reverted between Session 15 and Session 16. Re-applied the same fix (pull working URI from chat-deepagents Railway env, `aws secretsmanager update-secret`). Open question: what reverted it? No code change.

### Slack Integration recovery

- Found at `status=error` (auto-transitioned 2026-05-01 18:53:00Z, before Session 16 started). Walked `error → configured → connected → active`. Stayed active through 769+ Slack-Fetcher cron_runner completions over 3 days. One-off, not recurring; root-cause investigation deferred.

### Cumulative cron_runner soak (3 days, 2026-05-01 → 2026-05-04 — pre-Bug-#49-fix metrics)

| Fetcher | Cadence | Completions | DLQ (Bug #49) | LangSmith traces | Pending backlog |
|---|---|---|---|---|---|
| Email-Fetcher | */5 | 770 | 5 | 0 | 14 |
| Meeting-Fetcher | */15 | 259 | 0 | 0 | 4 |
| Drive-Fetcher | hourly | 65 | 0 | 0 | 1 |
| Slack-Fetcher | */5 | 769 | 6 | 0 | 12 |
| **Totals** | | **1863** | **11** | **0** | **31** |

**Cost reduction confirmed:** 0 LangSmith deepagents traces across 1863 cron_runner runs. ~1000 LLM calls/day Bug #40's design intent eliminated.

**Bug #49 fix expected impact:** dead_letter rate should drop to near-zero on cron_runner runs (Bug #38 orphans from genuine runtime restarts will still occur but should be << 11/1863). Verify over next 24-48h.

---

## Open design questions (carried forward)

These mostly fold into TD-4's research session per the Session 13 alignment:

1. **Opportunity vs Problem entity** — surfaces from TD-4 research observing unmapped pain
2. **Document-as-artifact pattern for emails** — RESOLVED in TD-5 alignment (Email entity with `status: drafting`)
3. **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle's Apr 24 ask) — research-driven in TD-4
4. **Origin / referrer tracking** — surfaces from TD-4 research
5. **Playbook hydration mechanism** — RESOLVED in TD-4 alignment
6. **Drive content extraction** — current Drive adapter populates metadata only; Google Docs/Sheets/Slides export, PDF text extraction, image OCR are future enrichment passes
7. **Slack Integration auto-error transition root cause** (NEW) — couldn't pin the kernel-side handler that transitioned the integration to error 2026-05-01 18:53Z. Defer investigation unless it recurs; same approach as Bug #12 regression (re-fix on detection).
8. **Bug #12 mongodb-uri secret revert mechanism** (NEW) — what process reverts this secret? Worth a pre-session-hook validation script in the future.

---

## Operating-system worktree state at close

**Branch:** `os-roadmap` (this worktree at `.claude/worktrees/roadmap/`).

**Uncommitted changes at session close (will commit in EOS protocol):**
- `M projects/customer-system/CURRENT.md` — this rewrite
- `M projects/customer-system/SESSIONS.md` — Session 16 entry to append at top
- `M projects/customer-system/os-learnings.md` — Bug #40 close + Bug #48 NEW row + Bug #49 NEW row + Bug #12 regression note + Bug #45-family followup observation
- `M projects/customer-system/roadmap.md` — Where we are now updated
- `M projects/customer-system/CLAUDE.md` — Session 16 entry in § 5 Journey
- `M projects/customer-system/INDEX.md` — Decisions, Open Questions, Artifacts updates
- `M projects/customer-system/skills/slack-fetcher.md` — v3 cron_runner shape
- `?? projects/customer-system/skills/email-fetcher.md` — NEW v3 cron_runner shape
- `?? projects/customer-system/skills/meeting-fetcher.md` — NEW v3 cron_runner shape
- `?? projects/customer-system/skills/drive-fetcher.md` — NEW v3 cron_runner shape

**Indemn-os repo state (uncommitted, 2 logical commits):**
- Bug #40 + #49 (cron_runner mode + heartbeat + OTEL): `M kernel_entities/actor.py`, `?? harnesses/async-deepagents/cron_runner.py`, `M harnesses/async-deepagents/main.py`, `?? harnesses/async-deepagents/tests/test_cron_runner.py`, `M harnesses/async-deepagents/tests/test_load_message_context.py`
- Bug #48 (CLI URL): `M kernel/api/meta.py`, `M indemn_os/src/indemn_os/main.py`, `M indemn_os/src/indemn_os/bulk_commands.py`, `?? tests/unit/test_meta_collection_field.py`, `?? tests/unit/test_cli_url_slug_resolution.py`

---

## Next session — focus

**Use `PROMPT.md` as the kickoff prompt** with this objective slot:

> *TD-2 cascade activation. Bug #40 + #48 + #49 closed; the scheduled-actor execution path is fully deterministic, 4 fetchers run LLM-free, dead_letter rate near zero. Next: build the 4 NEW associates (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher) per `roadmap.md § TD-2`; update EC v9 → v10 (fold signature parsing + ReviewItem-on-ambiguity); update TS v6 → v7 (fold Deal-creation + atomic Proposal-at-DISCOVERY + multi-Deal ambiguity → ReviewItem); IE full-cascade verification through TS-created Touchpoints + Option B source pointers + Deal/Proposal existence; activate progressively bottom-up; done-test = systematic historical replay across ~930 emails + 67 meetings + 860 SlackMessages. Trace-as-build-method per CLAUDE.md § 2 — for each new associate: pick a real scenario (Armadillo's Apr 28 discovery meeting for MC; Apr 7-8 Retention Associate Slack thread for SC; Armadillo's processed Touchpoints for PH; Armadillo's bare Company for CE), trace manually first via CLI, write skill from what worked, activate after the trace produces correct state on real data. Multi-session work; close cleanly per session.*

**Key follow-ups carried into next session:**
- TD-2 cascade activation (highest priority)
- Bug #19 follow-on (test fixture pattern improvement; no code action — surfaces as we add tests)
- Slack Integration auto-error root cause (only investigate if it recurs)
- `kernel/cli/app.py` Bug #48 propagation (lower priority — parallel CLI surface used inside kernel image; harness uses `indemn_os/` so impact is limited)
- Bug #12 mongodb-uri secret regression — consider a pre-session-hook validation script
- Drive "full crawl" — only 30-day backfill done; if "every Drive file ever" is required, run `indemn document fetch-new --data '{"since":"2020-01-01"}'` once. Current hourly cron is picking up new content correctly post-Bug-#46-fix; no immediate action needed.
- **24-48h Bug #49 verification** — confirm dead_letter rate dropped to near-zero on cron_runner runs after the heartbeat fix deployed today.

**Bug #40/#48/#49 done-test (all passing):**
- All 4 fetcher actors `mode=cron_runner` ✓
- cron_runner exec + success log lines visible for all 4 ✓
- 0 LangSmith deepagents traces post-flip across 3 days / 1863 completions ✓
- ~1000 LLM calls/day eliminated (cost reduction objective met) ✓
- Heartbeat loop wrapping subprocess (Bug #49 fix) ✓
- `cron_runner.run` OTEL span emitted with associate/result attributes ✓
- 25/25 cron_runner unit tests pass ✓
- 527/527 full unit suite pass (1 pre-existing pollution failure orthogonal) ✓

After Session 16 closes: **TD-2 begins.**

---

*This file is rewritten every session. Don't append — replace. The history lives in SESSIONS.md.*
