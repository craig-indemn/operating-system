# Customer System — CURRENT

> **Fast-changing state.** What just happened, what's in flight, parallel sessions, blockers, next steps. Rewritten every session. Read this *after* CLAUDE.md to know where things actually stand right now.

**Last updated:** 2026-05-04 (end of Session 17 — TD-1 verified done end-to-end; Bug #50 (queue visibility-extend + attempt_count cap) deployed; `fetch_new` chunk-cap with oldest-first sort deployed; Bug #12 REFRAME (mongosh-connect.sh inline host swap) shipped; 7 zombie polling loops killed → dev API response time recovered 5-8s → 60-100ms; pre-TD-2 OS hardening sprint planned for next session). Pricing Framework Session 3 closed in parallel — visual v6 generated from full staging JSON.

---

## ACTIVE PARALLEL WORKSTREAMS

There are **two parallel customer-system workstreams** active right now:

### Workstream A — Pricing Framework (Cam-assigned action item; SIDE-PROJECT but high-value)

**Source of truth:** `artifacts/2026-04-30-associate-pricing-framework.md` § 0 Session Handoff

**Status (2026-05-04):** **Pricing Framework Session 3 Phase C complete; Phase D in progress.** Phase A + Phase B + Phase C complete. **All 13 active customers walked + all 55 Cam rows swept + all LOE tables populated.** 5 prospects out-of-scope per Craig 2026-05-01. **Phase D §11.1 Cam sheet update spec + §11.2 HTML UI visualization plan drafted; §11.3 locks the normalized staging-data path; local draft data object + testing-sheet CSV pack exist; Phase D mental-model artifact captures the Cam/Kyle visual thesis; HTML visual v6 is now the current full-catalog review artifact generated from staging JSON.**

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
2. **Focus reads** — `artifacts/2026-04-30-associate-pricing-framework.md` §0 Session Handoff + §2 Formula + §4 End-state sheet design + §9 Per-associate sweep + §10 LOE tables + §11 Phase D output presentation + `artifacts/2026-05-04-pricing-framework-mental-model.md`.
3. **Confirm understanding back to Craig** — framework rules · 5-phase plan · Phase A/B/C complete · Phase D output goal.
4. **Review §11.1.9 computability checks** — five representative examples are drafted with first/repeat totals and traceable components. Validate component inclusion with Craig before using them in the staging sheet.
5. **Review visual v6 + generated testing data** — `artifacts/2026-05-04-pricing-framework-visual-v6.html` is the current full-catalog review artifact generated from `artifacts/2026-05-04-pricing-framework-staging-data.json`. It renders all 55 §9 associate rows, 50 derived customer-deployment rows, 166 skills total (103 §10 skills + 63 §9-derived pathway skills), §10 catalogs, 13 customers, 4 gaps, and 5 computability fixtures through the customer-deployment map, raw catalog explorer, and multi-select configuration builder. Local testing-sheet CSVs are generated under `artifacts/2026-05-04-pricing-framework-testing-sheet/`. Next: review generated `path-derived-row-*` IDs with Craig and decide whether to keep them for staging or renumber them into canonical `path-*`. Rebuild data with `npm --prefix projects/customer-system/tools run build:pricing-staging-data`; rebuild the visual with `npm --prefix projects/customer-system/tools run build:pricing-visual-v6`.

**Discipline reminders for Phase D:**
- **Don't touch Cam's sheet** until §11 produces the migration spec and Craig signs off.
- Keep output hours-only unless Craig explicitly asks for money mapping.
- Preserve Cam catalog rows as official; redundant row-level skill listing remains intentional.

### Workstream B — TD-1 verified done; pre-TD-2 OS hardening sprint queued

State below is from **Session 17 close (2026-05-04)** — TD-1 done-test verified passing end-to-end; Bug #50 (queue visibility-extend + attempt_count cap) shipped; `fetch_new` chunk-cap with oldest-first sort shipped; Bug #12 reframed (wrapper inline host-swap; stop overwriting shared secret); 7 zombie polling loops killed; dev API response time recovered to baseline. Next session is the OS hardening sprint before TD-2 cascade activation.

---

## Top of roadmap

**TD-1 VERIFIED DONE end-to-end (Session 17).** All done-test items passing on production state:

- 4 fetcher actors active, `mode=cron_runner`, correct cron schedules (Email */5, Meeting */15, Drive hourly, Slack */5)
- Last 30 min of production: 7 email + 8 slack + 2 meeting completions — data flowing cleanly
- Substantial entity counts: 3375 emails, 305 meetings, 867 SlackMessages, 1379 documents
- Zero `dead_letter` messages since Bug #50 deploy (21:33 UTC) verified across the post-deploy soak
- ReviewItem entity (9 fields) + Reviewer role (1 watch on `ReviewItem created`) wired and ready
- EC/TS suspended; IE active — cascade NOT activated by design
- `Document.source` enum includes `slack_file_attachment`
- Voice OS Assistant active; `log-touchpoint` skill v3 (4600+ chars)

**Next gate: pre-TD-2 OS hardening sprint** (next session). Tier 1 items in priority order:
1. `fetch_new` bulk_save_tracked (replaces sequential save loop with batched insert + audit chain + watch eval — proper foundation, half day)
2. `indemn diagnose` command group (actor / message / cron-runs surfaces — half day)
3. List endpoint arbitrary field filters regression (~1-2 hours)
4. `--include-related` polymorphic Option B support (~2 hours)
5. Employee `entity_resolve` activation (5 min, TD-2 blocker)
6. os-learnings.md status badge cleanup (~30 min — several rows mismarked 🔴 are actually 🟢)

After Tier 1 lands: **TD-2 cascade activation begins** — 4 NEW associates (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher) + EC v9→v10 + TS v6→v7 + IE verification + ReviewItem cascade-wide. Trace-as-build-method per CLAUDE.md § 2.

Next-session prompt drafted at: `projects/customer-system/PROMPT-2026-05-05-os-hardening.md`.

---

## Pipeline associate states (Session 17 close — unchanged from Session 16)

| Associate | State | Notes |
|---|---|---|
| Email Classifier (EC) | **suspended** | Unchanged. Will activate in TD-2 (v9 → v10 with signature parsing + ReviewItem on ambiguity). |
| Touchpoint Synthesizer (TS) | **suspended** | Unchanged. Will gain Deal-creation + Proposal-at-DISCOVERY atomic in TD-2 (v6 → v7). |
| Intelligence Extractor (IE) | **active** | Unchanged. Inherits gemini-3-flash-preview/global. Will be verified through full cascade in TD-2. |
| **Email Fetcher** | **active, mode=cron_runner** | Skill v5 (post Session 17 — now passes `--data '{"limit": 100}'` per Bug #50 follow-on). Bug #50 fix live; Email completing cleanly within visibility (first post-fix completion 2026-05-04T21:33:49Z). |
| **Meeting Fetcher** | **active, mode=cron_runner** | Skill v4. Completing cleanly. |
| **Drive Fetcher** | **active, mode=cron_runner** | Skill v4. Completing cleanly. |
| **Slack Fetcher** | **active, mode=cron_runner** | Skill v4. Completing cleanly. |
| Voice OS Assistant | **active** (mode=hybrid, unchanged from Session 15) | Used by Railway voice runtime for log-touchpoint flow. |
| Reviewer role | wired | Unchanged from Session 14 — ready for TD-2. |

**4 NEW associates designed in Session 13's TD-2 alignment** — to be built when TD-2 executes (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher).

---

## Material state in dev OS (Session 17 changes)

**Hydrated customer constellations** (carried forward unchanged): GR Little, Alliance Insurance, Armadillo Insurance.

**Entity-state changes Session 17:**
- 4 fetcher skills updated to v4-v5 (now pass `--data '{"limit": 100}'` per Bug #50 follow-on chunk-cap design): `email-fetcher` v5, `slack-fetcher` v4, `meeting-fetcher` v4, `drive-fetcher` v4 — pushed to dev OS.
- 86 stuck `_scheduled` messages from the morning's secret-revert window manually marked `dead_letter` with audit-trail `last_error` reason (cleared the recovery-loop deadlock so Bug #50 fix could verify cleanly on fresh cron ticks).
- Slack 3-day watermark gap (May 1 15:39Z stale → 14 min current) drained via chunked `indemn slackmessage fetch-new --data '{"since":..., "until":...}'`. Server-side fetch completed in ~10 min despite CLI ReadTimeout — work persisted, watermark advanced cleanly.

---

## Indemn-os main commits this session (Session 17)

| Commit | What |
|---|---|
| `18ab3b9` (merged via `7c3a54c`) | `fix(queue+harness): wire queue visibility extension + cap visibility-recovery at max_attempts — Bug #50` — kernel/queue_processor.py splits visibility-recovery into dead-letter (attempt_count >= max_attempts via $expr) + recovery passes; kernel/api/queue_routes.py adds POST /api/message_queues/{id}/extend-visibility endpoint; indemn_os queue_commands.py adds `indemn queue extend-visibility <id>` CLI; harnesses/async-deepagents/main.py cron heartbeat loop now calls extend-visibility every 30s alongside activity.heartbeat. 12 new unit tests in `tests/unit/test_check_visibility_timeouts_attempt_cap.py` + `tests/unit/test_extend_visibility_endpoint.py`. 1 new shape pin in `harnesses/async-deepagents/tests/test_cron_runner.py::test_cron_heartbeat_loop_extends_queue_visibility`. |
| `06d2bbd` (merged via `a09c67b`) | `fix(capability): fetch_new sorts oldest-first + caps saves at params['limit'] — Bug #50 follow-on` — kernel/capability/fetch_new.py: after dedup, sort genuinely-new items ascending by watermark field (date / posted_at / created_date) so when limit is set, the cap applies to OLDEST-first slice (preserves watermark-correctness invariant against APIs that return newest-first like Gmail). 4 new unit tests in `tests/unit/test_fetch_new_chunk_cap.py`. |

Test count: 477 unit tests pre-session → **481 unit tests post-session** (4 new for `fetch_new` chunk-cap; the 12 Bug #50 tests had been counted already at the Session 16/17 boundary). Full kernel suite passes; no regressions.

---

## Operating-system worktree commit this session (Session 17)

`3ddc02a` (`os-roadmap` branch, unpushed at write time — will go up at EOS): `project(customer-system): TD-1 foundations — Bug #50 + fetch_new chunk-cap + Bug #12 reframe + os-learnings`

- 4 fetcher skill files updated with `--data '{"limit": 100}'` cron command line (email-fetcher.md, slack-fetcher.md, meeting-fetcher.md, drive-fetcher.md)
- `scripts/secrets-proxy/mongosh-connect.sh` does inline `-pl-0 → ` host swap; comment block tells future operators NOT to overwrite the shared secret
- `os-learnings.md` updated: NEW Bug #50 entry (🟢 Fixed end-to-end with full audit trail); NEW `fetch_new` sequential save_tracked bottleneck entry (🔴 — proper bulk_save_tracked is queued for next session); NEW CLI diagnostics gap entry (🔴 — `indemn diagnose` command group queued); Bug #12 REFRAME entry marked 🟢 Fixed.

---

## Railway deployments updated this session

| Service | What changed |
|---|---|
| `indemn-api` | Bug #50 (extend-visibility endpoint + queue_processor recovery split) + fetch_new chunk-cap. Deployed 2x — once for Bug #50 cluster, once for chunk-cap. |
| `indemn-queue-processor` | Bug #50 (visibility-recovery split: dead-letter at max_attempts, recover otherwise). |
| `indemn-runtime-async` | Bug #50 (cron heartbeat loop now calls extend-visibility every 30s). New image hash `874723f6...`. |

**First-round deploy mistake & lesson:** initial `railway up --ci --detach` was triggered from the operating-system worktree CWD instead of the indemn-os repo CWD — uploaded the wrong source, build silently used a stale image. Caught + corrected by re-running `railway up` from `/Users/home/Repositories/indemn-os` directly. Deploy IDs: indemn-api `9c5bc78c`, indemn-queue-processor `633a045f`, indemn-runtime-async `4cbe96eb`.

---

## OS bugs resolved this session

| Bug | Status before | Status after | Commit / artifact |
|---|---|---|---|
| **Bug #50a** (Mongo queue visibility-recovery is independent of Temporal heartbeat; long-running cron_runner subprocesses race the queue's recovery sweep) | NEW — surfaced mid-session investigating Email/Slack chronic stuckness post-cron_runner-flip | 🟢 **fixed** — extend-visibility endpoint + heartbeat-loop wire | indemn-os main `18ab3b9` (12 tests + endpoint + CLI + harness wire) |
| **Bug #50b** (visibility-recovery loop unconditionally returns to pending without checking `max_attempts` — stuck messages attempt 7+ times indefinitely) | NEW — surfaced in same investigation, observed stuck email_fetcher message at attempt_count=7 / max_attempts=3 | 🟢 **fixed** — recovery now splits dead_letter (cap exceeded) vs pending (recover) | bundled with #50a in `18ab3b9` |
| **`fetch_new` chunk-cap + oldest-first sort** (chronic >5min subprocess on Email Fetcher's 11-mailbox fan-out — root bottleneck is sequential `save_tracked` per entity) | NEW — surfaced from Bug #50 deploy verification | 🟢 **bridging fix shipped** — `params["limit"]` caps saves per call after sorting oldest-first by watermark field. Proper foundation fix (`bulk_save_tracked`) queued for Session 18 OS hardening sprint | indemn-os main `06d2bbd` (4 tests) |
| **Bug #12 REFRAME** (Sessions 15+16's "re-fix" was actually wrong — overwrote correct private-link host with public one; auto-restore is correct platform behavior) | 🔴 reframed | 🟢 **fixed via wrapper** — `scripts/secrets-proxy/mongosh-connect.sh` does inline host swap; doesn't touch shared secret | os-roadmap `3ddc02a` |
| **Zombie polling loops** (7 leftover `until [...]; do sleep 10/8; done` shells from prior sessions hammering api.os.indemn.ai + LangSmith for days) | observed mid-session (caused dev API response time 5-8s) | 🟢 **killed** — dev API recovered to 60-100ms baseline | local cleanup; no commit |

**Bugs deferred (next session — pre-TD-2 OS hardening sprint):**
- **`fetch_new` bulk_save_tracked** (replaces the sequential per-entity save loop with batched insert + audit chain + watch eval; proper foundation, ~half day)
- **`indemn diagnose` command group** (actor / message / cron-runs surfaces; ~half day) — the chunk-cap + the Bug #50 fix work today proved how badly we need this
- **List endpoint arbitrary field filters regression** (~1-2 hours)
- **`--include-related` polymorphic Option B Touchpoint.source_entity_id** (~2 hours)
- **Employee `entity_resolve` activation** (5 min — TD-2 blocker)
- **os-learnings.md status badge audit** (~30 min cleanup)

**Bugs deferred (further out):**
- Bug #19 follow-on (test fixture process improvement; no code action)
- `kernel/cli/app.py` Bug #48 propagation (lower priority — parallel CLI surface in kernel image; harness uses `indemn_os/`)
- Slack Integration auto-error root cause (only investigate if it recurs)
- Bug #12 mongodb-uri secret revert mechanism (now mitigated by wrapper fix; pre-session validation script optional)

---

## Parallel sessions

**Pricing Framework session (parallel)** — running in `.claude/worktrees/gic-feature-scoping/`. Session 3 closed 2026-05-04; visual v6 generated from full staging JSON. Did not modify any of Session 17's TD-1 / Bug #50 / fetch_new state.

**Currently no other parallel sessions.** Next session resumes single-thread on the OS hardening sprint.

---

## What just shipped (Session 17) — narrative

Session 17 took TD-1 from "marked complete in roadmap.md" to "verified done end-to-end on production state" and shipped the Tier-zero fixes that made it true. Three coupled bugs fell out of the verification:

### Bug #50 closure (queue visibility-extend + attempt_count cap)

Bug #49 (Session 16) added a Temporal activity heartbeat in cron_runner — kept the activity alive past 90s heartbeat_timeout. **But the Mongo queue's `visibility_timeout` (5 min, set on every claim in `kernel/message/mongodb_bus.py`) was independent — nothing extended it while the runtime was still working.** Slow Email/Slack fetches on backed-up watermarks raced the queue's recovery sweep: pod A still working, queue recovers at 5 min, pod B claims it (multi-pod is by design), pod A's later `complete` hits 404 "Message not found." Net effect: subprocesses succeed but bookkeeping fails, watermark never advances, backlog grows.

Compounded by **Bug #50b** — pre-fix `kernel/queue_processor.py::check_visibility_timeouts` unconditionally recovered every timed-out `processing` message back to `pending` with no max_attempts check. The bus's `claim` path increments `attempt_count` on every claim, but nothing capped it — so a stuck message could attempt 7+ times indefinitely (observed: stuck email_fetcher message `69f89bec1f2c3ee82ecb66c4` at attempt_count=7 / max_attempts=3).

**Fix shape:** new `POST /api/message_queues/{id}/extend-visibility` endpoint resets visibility_timeout to now + 5min; idempotent on terminal status; refuses pending. New `indemn queue extend-visibility <id>` CLI mirrors complete/fail verbs. Cron heartbeat loop now calls `await asyncio.to_thread(indemn, "queue", "extend-visibility", message_id)` alongside `activity.heartbeat()` — same 30s cadence; CLIError caught + logged. Recovery sweep splits into two `update_many` calls: first dead-letters messages where `attempt_count >= max_attempts` via `$expr: {$gte: ["$attempt_count", "$max_attempts"]}`, then recovers the rest. Logs `Dead-lettered N messages over max_attempts (Bug #50)`.

**Verified live post-deploy:** vis_gap > 5min observed on multiple email_fetcher messages (10.9min, 8.8min, 7.8min — proving extend-visibility fires); queue_processor logs `Dead-lettered N messages over max_attempts (Bug #50)` repeatedly (proving 50b cap fires); slack/meeting/drive fetchers completing cleanly post-deploy. Email Fetcher first post-fix completion at 2026-05-04T21:33:49Z — first email completion since 14:26 UTC that day.

### `fetch_new` chunk-cap + oldest-first sort

Bug #50 fix proved Email Fetcher *could* now complete via heartbeat extension, but each subprocess was still chronically slow (5-10 min) because of the per-entity sequential `save_tracked()` loop in `kernel/capability/fetch_new.py`. With ~150-300ms per save × N new entities × 11-mailbox fan-out, accumulated backlog stays painful even with extension.

**Bridging fix:** `params["limit"]` caps saves per call. Subsequent ticks pick up the rest. Critical correctness invariant: when `limit` is set, the cap must apply to the OLDEST-first slice — otherwise APIs that return newest-first (Gmail's default) would advance the watermark past unsaved older items, leaving them stranded forever. Implementation sorts new items ascending by watermark field (`date` / `posted_at` / `created_date`) before slicing.

**Skill updates:** all 4 fetcher skills now pass `--data '{"limit": 100}'`. 100 saves × ~200ms = ~20s, well under the 5-min visibility window.

**Real foundation fix (`bulk_save_tracked`) queued for next session** — single Pydantic validation pass + insert_many + batched audit chain + batched watch evaluation. Ships in OS hardening sprint per `PROMPT-2026-05-05-os-hardening.md` Tier 1 #1.

### Bug #12 REFRAME

Per Craig 2026-05-04: "the mongo DB in the secret is needed. its just us that needs to use this other value." The shared `mongodb-uri` AWS Secret correctly stores the private-link host (`dev-indemn-pl-0`) the platform NEEDS. Sessions 15+16's "re-fixes" (overwriting with the public host) were the actual bug — the Railway platform's auto-restore was correct behavior, not a regression.

**Fix:** `scripts/secrets-proxy/mongosh-connect.sh` now does an inline `-pl-0` → `` host swap (`LOCAL_URI="${URI/-pl-0/}"`). Pattern catches both `dev-indemn-pl-0` and `prod-indemn-pl-0`. Comment block in the script explicitly documents the rationale + tells future operators NOT to "fix" this by writing the public host back to the shared secret. Verified: `db.runCommand({ping: 1})` returns `ok: 1`.

### Zombie polling cleanup

Process audit found 7 leftover `until [...]; do sleep 10/8; done` shells from prior sessions:
- `94677` (Thu01PM) — polled api.os.indemn.ai/api/_meta/queue-stats every 10s for **3 days** waiting for an email_fetcher message that completed long ago
- `90472` (Fri09AM) — polled LangSmith every 8s for a Slack Fetcher run completion
- `40577, 81319, 93507, 93871, 94021` — stale `/tmp/claude-501` output-polling shells from prior background tasks that never terminated cleanly

All 7 killed. **Dev API response time dropped from 5-8s to 60-100ms** post-cleanup — the zombies were genuinely loading the API. Today's session's own background polling shells preserved.

---

## Open design questions (carried forward)

These mostly fold into TD-4's research session per the Session 13 alignment:

1. **Opportunity vs Problem entity** — surfaces from TD-4 research observing unmapped pain
2. **Document-as-artifact pattern for emails** — RESOLVED in TD-5 alignment (Email entity with `status: drafting`)
3. **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle's Apr 24 ask) — research-driven in TD-4
4. **Origin / referrer tracking** — surfaces from TD-4 research
5. **Playbook hydration mechanism** — RESOLVED in TD-4 alignment
6. **Drive content extraction** — current Drive adapter populates metadata only; Google Docs/Sheets/Slides export, PDF text extraction, image OCR are future enrichment passes
7. **Slack Integration auto-error transition root cause** — couldn't pin the kernel-side handler that transitioned the integration to error 2026-05-01 18:53Z. Defer investigation unless it recurs.
8. **Bug #12 mongodb-uri secret revert mechanism** — what process reverts this secret? Now mitigated by wrapper fix; pre-session-hook validation script optional.
9. **fetch_new bulk_save_tracked architecture** (NEW) — shape drafted in PROMPT-2026-05-05-os-hardening.md Tier 1 #1; details to surface during implementation.
10. **`indemn diagnose` command group surface** (NEW) — sub-commands sketched in same PROMPT; specifics to surface during implementation.

---

## Operating-system worktree state at close

**Branch:** `os-roadmap` (this worktree at `.claude/worktrees/roadmap/`).

**Uncommitted changes at session close (will commit in EOS protocol):**
- `M projects/customer-system/CURRENT.md` — this rewrite
- `M projects/customer-system/SESSIONS.md` — Session 17 entry to append at top
- `M projects/customer-system/os-learnings.md` — already-staged Session 17 entries committed in `3ddc02a`; any further refinements this EOS
- `M projects/customer-system/roadmap.md` — Where we are now updated
- `M projects/customer-system/CLAUDE.md` — Session 17 entry in § 5 Journey
- `M projects/customer-system/INDEX.md` — Decisions, Open Questions, Artifacts updates
- `?? projects/customer-system/PROMPT-2026-05-05-os-hardening.md` — drafted next-session prompt

**Indemn-os repo state (all pushed to origin/main):**
- `7c3a54c` Merge: Bug #50 fix
- `18ab3b9` fix(queue+harness): wire queue visibility extension + cap visibility-recovery at max_attempts — Bug #50
- `a09c67b` Merge: fetch_new chunk cap + oldest-first sort (Bug #50 follow-on)
- `06d2bbd` fix(capability): fetch_new sorts oldest-first + caps saves at params['limit'] — Bug #50 follow-on

---

## Next session — focus

**Use `PROMPT-2026-05-05-os-hardening.md` as the kickoff prompt** (drafted this session; saved at `projects/customer-system/PROMPT-2026-05-05-os-hardening.md`).

> *Pre-TD-2 OS hardening sprint. TD-1 verified done end-to-end. Tier 1 items in priority order: (1) `fetch_new` bulk_save_tracked replaces sequential save loop — proper foundation, ~half day; (2) `indemn diagnose` command group — actor / message / cron-runs CLI surfaces, ~half day; (3) List endpoint arbitrary field filters regression fix — ~1-2 hours; (4) `--include-related` polymorphic Option B support — ~2 hours; (5) Employee `entity_resolve` activation — 5 min, TD-2 blocker. Plus Tier 1.5 os-learnings.md status badge audit (~30 min). After Tier 1 lands: TD-2 cascade activation begins (next-next session) — start with MeetingClassifier on Armadillo's Apr 28 discovery meeting per trace-as-build-method.*

**Key follow-ups carried into next session:**
- Pre-TD-2 OS hardening sprint (highest priority — Tier 1 list above)
- Then TD-2 cascade activation (after Tier 1 lands cleanly)
- Bug #19 follow-on (test fixture pattern improvement; no code action)
- Slack Integration auto-error root cause (only investigate if it recurs)
- `kernel/cli/app.py` Bug #48 propagation (lower priority)
- Drive "full crawl" — only 30-day backfill done; if "every Drive file ever" is required, run `indemn document fetch-new --data '{"since":"2020-01-01"}'` once

**TD-1 done-test (all passing — verified end-to-end Session 17):**
- All 4 fetcher actors `mode=cron_runner` with correct cron schedules ✓
- New entities flowing within configured cadence ✓ (7 email + 8 slack + 2 meeting completions in 30 min)
- Substantial entity counts (3375 emails, 305 meetings, 867 slack, 1379 docs) ✓
- Bug #36 / #37 cleanup verified Session 14 ✓
- Voice + chat log-touchpoint end-to-end ✓
- Document.source enum includes slack_file_attachment ✓
- ReviewItem entity (9 fields) + Reviewer role wired ✓
- Cascade NOT activated (EC suspended, TS suspended, IE active) ✓
- Bug #49/#50 verification: ZERO dead_letters since Bug #50 deploy at 21:33 UTC ✓

After Session 17 closes: **OS hardening sprint, then TD-2.**

---

*This file is rewritten every session. Don't append — replace. The history lives in SESSIONS.md.*
