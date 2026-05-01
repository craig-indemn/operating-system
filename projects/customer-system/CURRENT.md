# Customer System — CURRENT

> **Fast-changing state.** What just happened, what's in flight, parallel sessions, blockers, next steps. Rewritten every session. Read this *after* CLAUDE.md to know where things actually stand right now.

**Last updated:** 2026-05-01 (end of TD-1 Roadmap Session 15 — TD-1 fully closed; voice + chat round-trips verified; 7 OS bugs resolved; chat + voice harnesses migrated to CLI-only skill loading)

---

## ACTIVE PARALLEL WORKSTREAMS

There are **two parallel customer-system workstreams** active right now:

### Workstream A — Pricing Framework (Cam-assigned action item; SIDE-PROJECT but high-value)

**Source of truth:** `artifacts/2026-04-30-associate-pricing-framework.md` § 0 Session Handoff

**Status (2026-05-01):** **Session 2 closed.** Phase A + Phase B complete. **All 13 active customers walked + all 55 Cam rows swept.** 5 prospects out-of-scope per Craig 2026-05-01. **Phase C next** (LOE pass).

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
| C | LOE pass per catalog entry — hours only, no money; collaborative (Craig authors, I capture) | ⏳ Next |
| D | Output presentation — Cam sheet update spec + HTML UI visualization | ⏳ After C |
| E | OS data-model bounce-off — put framework into operating system to bounce customer/associate/skill data models | ⏳ After / with D |

**Catalog state (post-Session 2):** 8 channels · **28 systems** (added Zola embedded-chat) · **57 tool skills** (added tool-049 to tool-057) · **46 pathway skills** (post §7 audit — was 55, consolidated 9 channel-split / lumped / LOB-split / KB-scope merges) · 4 catalog gaps tracked.

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

**Resume protocol for next pricing-framework session:** read `artifacts/2026-04-30-associate-pricing-framework.md § 0` (full handoff) + this CURRENT.md + standard PROMPT.md hydration set. Then begin Phase C — LOE pass per catalog entry. Recommended order: channels (8 entries, smallest catalog) → systems (28) → tool skills (57) → pathway skills (46). Hours only, no money. Craig authors estimates, I capture structure.

### Workstream B — TD-1 Roadmap Execution (the main customer-system roadmap)

State below is from **Session 15 close (2026-05-01)** — TD-1 is now fully closed. Pricing framework session ran in parallel and did not modify TD-1 state.

---

## Top of roadmap

**TD-1 COMPLETE.** All four scheduled fetchers (Email, Meeting, Drive, Slack) active and autonomous. Voice harness v2 deployed to Railway and verified end-to-end: real Touchpoint creation via voice multi-turn conversation. Chat-side log-touchpoint flow verified end-to-end: real Touchpoint creation via chat-deepagents WebSocket. Both transports use Voice OS Assistant + `log-touchpoint` skill. **All TD-1 done-test items passing.**

After TD-1: **Bug #40 architectural design** is the gate to TD-2 (per Craig's directive — needs deep design in fresh session). Then TD-2 cascade activation begins (already designed in Session 13). 4 NEW associates to build (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher).

---

## Pipeline associate states (Session 15 changes)

| Associate | State | Notes |
|---|---|---|
| Email Classifier (EC) | **suspended** | Unchanged. Will activate in TD-2. |
| Touchpoint Synthesizer (TS) | **suspended** | Unchanged. Will gain Deal-creation in TD-2. |
| Intelligence Extractor (IE) | **active** | Unchanged. Inherits gemini-3-flash-preview/global. |
| Email Fetcher | **active** | Unchanged from Session 14. id `69f2bf30942e5629f07a8313`. */5 cron. |
| Meeting Fetcher | **active** | Unchanged from Session 14. id `69f39ec6c0b340cf765a38d6`. */15 cron. |
| Drive Fetcher | **active** | Unchanged from Session 14, but now actually picking up new files since Bug #46 watermark fix this session (was silently re-fetching same content for ~17h pre-fix). id `69f3abbe268936150b46a0fa`. hourly. |
| **Slack Fetcher** (NEW Session 15 activation) | **active** | id `69f4a473a0cbb2f5d2d0386f`. Cron `*/5 * * * *`. role=`slack_fetcher`. skill=`slack-fetcher`. runtime=async-deepagents-dev. First autonomous tick verified at 13:45:37Z (LangSmith trace `019de3c9-ab78-7383-b273-5c0d051d9431`). |
| **Voice OS Assistant** (NEW Session 15) | **active** | id `69f4c62d03e56394d808b79c`. role=team_member. runtime=voice-deepagents-dev (`69f3b7fc97300b115e7236a0`). skills=`["log-touchpoint"]`. mode=hybrid. Multi-turn voice round-trip created Touchpoint `69f4ed4f03e56394d808bc88` via Railway worker. |
| **Reviewer role** | wired | Unchanged from Session 14. |

**4 NEW associates designed in Session 13's TD-2 alignment** — to be built when TD-2 executes (MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher).

---

## Material state in dev OS (Session 15 changes)

**Hydrated customer constellations** (carried forward unchanged): GR Little, Alliance Insurance, Armadillo Insurance.

**New entities created Session 15:**
- **Voice OS Assistant actor** — id `69f4c62d03e56394d808b79c`, role=team_member, runtime=voice runtime, skills=["log-touchpoint"], mode=hybrid, status=active. Bound to voice runtime, used by Railway voice-deepagents service.
- **Slack-Fetcher actor** — id `69f4a473a0cbb2f5d2d0386f`, role=slack_fetcher (NEW), skills=["slack-fetcher"] (NEW), trigger_schedule="*/5 * * * *", runtime=async-deepagents-dev, status=active.
- **slack_fetcher role** — id `69f4a428a0cbb2f5d2d03869`, permissions read=[SlackMessage, Integration], write=[SlackMessage].
- **slack-fetcher skill** — id `69f4a456a0cbb2f5d2d0386e`, single-CLI deterministic skill mirroring email-fetcher pattern.
- **Voice runtime upgraded** — `voice-deepagents-dev` (id `69f3b7fc97300b115e7236a0`) walked configured → deploying → active. Currently 1 instance heartbeating from Railway (older test instances TTL-expired).
- **Voice runtime service-token actor (`runtime-service:voice-deepagents-dev`)** — granted `harness_service` role (id `69e244027202d4c8f7bbb9c4`, read/write *) for register-instance + heartbeat permission.
- **Slack Integration `access.roles` populated** — `[team_member, platform_admin, slack_fetcher]` (Bug #45a workaround until kernel fix lands; resolver fix Bug #45c lets future Integrations leave access null).
- **860 SlackMessages backfilled** — spanning 2023-11-17 → 2026-05-01 across 4 channels (conversation-design 435, voice 217, customer-implementation 200, test-reports 8). 274 within 90-day target window + 586 deeper.
- **2 Touchpoints created via end-to-end tests:**
  - `69f4ed4f03e56394d808bc88` — voice round-trip (Branch + Dan Spiegel + summary "discussed renewal pricing and timeline")
  - `69f4f2ca03e56394d808bd6d` — chat round-trip (same shape)
- **log-touchpoint skill v3** — entity-resolve param shape corrected from `{"name": ...}` to `{"candidate": {"name": ...}}` (matches kernel resolver contract).

---

## Indemn-os main commits this session (Session 15)

In chronological order:

| Commit | What |
|---|---|
| `eea170d` | `fix(adapters): register Slack adapter under (slack, v1) not (messaging, slack) — Bug #45b` |
| `20c074c` | `fix(capability): fetch_new watermark falls through date→posted_at→created_date — Bug #46` |
| `6671dea` | `feat(harnesses): voice-deepagents v2 — canonical pattern (deepagents + Interaction/Attention + DeepagentsLLM adapter) (Bug #44)` |
| `a35913f` | `fix(voice-deepagents): bootstrap + events drain + dep + tests verified end-to-end` |
| `0e1fff4` | `fix(voice-deepagents): runtime register at boot + workspace fallback + agent_name dispatch` |
| `33d12f7` | `fix(harness_common): resolve indemn binary via sys.executable, not PATH lookup` |
| `27e9304` | `feat(voice-deepagents): wire LangSmith metadata + tags + run_name` |
| `fcdd8f8` | `fix(voice-deepagents): Dockerfile CMD passes 'start' subcommand to agents.cli.run_app` |
| `0e8c657` | `fix(voice-deepagents): pre-download turn-detector model via huggingface_hub at build` (rolled back by `cdc8479`) |
| `cdc8479` | `fix(voice-deepagents): drop turn_detector — VAD-only for now` |
| `7197f08` | `refactor(harnesses): chat + voice load skills via CLI in DEFAULT_PROMPT — drop deepagents skills layer` |
| `5036bc1` | `fix(integration): resolver tolerates null/missing access on org integrations — Bug #45c` |
| `00b7407` | `fix(api): route generation honors explicit --collection-name override — Bug #39` |
| `bee1a7e` | `docs: add voice-deepagents + harness_common to Railway deploy table — Bug #13 followup` |

Test count: started session at 437 unit tests → ended at **456** (added 5 watermark + 5 resolver + 5 route-slug + 8 chat agent + 11 voice llm_adapter; voice tests run in harness venv, kernel suite is 456).

---

## Railway deployments updated this session

| Service | What changed |
|---|---|
| `indemn-api` | Bug #45b adapter registry fix; Bug #46 watermark fallback; Bug #45c resolver tolerance; Bug #39 route slug. |
| `indemn-runtime-chat` | Service token corrected (Bug #47); migrated to CLI-only skill loading (`7197f08`). |
| `indemn-runtime-voice` (NEW Railway service this session) | id `df2349d6-0939-43e3-9261-87dfaf70e6ec`. Built from `harnesses/voice-deepagents/Dockerfile`. Env: LIVEKIT/DEEPGRAM/CARTESIA from secrets, GCP service account JSON, INDEMN_SERVICE_TOKEN, RUNTIME_ID=`69f3b7fc97300b115e7236a0`, VOICE_ASSOCIATE_ID=`69f4c62d03e56394d808b79c`, AGENT_NAME=`voice-deepagents`, LANGSMITH config. Connects to LiveKit Cloud `wss://test-ympl759t.livekit.cloud` with explicit-dispatch agent name. Verified end-to-end. |

---

## OS bugs resolved this session

| Bug | Status before | Status after | Commit / artifact |
|---|---|---|---|
| **Bug #44** (voice harness wrong shape) | open from Session 14 | 🟢 fixed | `6671dea` rebuild + 7 follow-up fixes |
| **Bug #45a** (Slack Integration null access — workaround) | open | 🟢 patched (data) — superseded by Bug #45c kernel fix | live patch on Slack Integration |
| **Bug #45b** (Slack adapter wrong register_adapter args) | open | 🟢 fixed | `eea170d` |
| **Bug #45c** (kernel resolver intolerant of null access) | NEW | 🟢 fixed | `5036bc1` |
| **Bug #46** (kernel watermark hardcoded to `date`) | NEW | 🟢 fixed | `20c074c` |
| **Bug #47** (chat-deepagents stale Railway service token) | NEW | 🟢 fixed | Railway env update + redeploy |
| **Bug #12** (mongodb-uri AWS Secret wrong host) | open | 🟢 fixed | AWS Secrets Manager update |
| **Bug #13** (Railway auto-deploy doc/reality) | already fixed 2026-04-28 | 🟢 docs catch-up | `bee1a7e` (added voice harness rows) |
| **Bug #39** (collection-name route generation) | open | 🟢 fixed | `00b7407` |

**Bugs deferred to next session:**
- **Bug #19 follow-on** — process improvement (test pattern), no code action.
- **Bug #40** — deterministic scheduled-actor execution path. Per Craig: think deeply about it in a fresh session. Two design choices to weigh: (A) new `cron_runner` actor mode that bypasses the LLM and treats the skill content as a literal CLI command, or (B) new `ScheduledActorWorkflow` peer to `ProcessMessageWorkflow` that runs `indemn` CLI directly via Temporal activity (no harness involved).

---

## Parallel sessions

**Pricing Framework session (parallel)** — running in `.claude/worktrees/gic-feature-scoping/`. Closed earlier today: commit `381b773` "Pricing Framework Session 1 close — 9/18 customers walked." Their CURRENT.md edits added the dual-workstream structure preserved above. Did NOT touch TD-1 work.

**Currently no other parallel sessions.** Next session resumes single-thread.

---

## What just shipped (Session 15)

Massive validation + cleanup session. TD-1 fully closed; harness architecture cleaned up; 7 OS bugs resolved end-to-end.

### TD-1 closure
- **Slack-Fetcher activated** — full chain: Bug #45a workaround (access.roles patch) → Bug #45b fix + deploy → Slack-Fetcher actor active → 90-day backfill (860 messages) → autonomous run verified via LangSmith trace `019de3c9-ab78-7383-b273-5c0d051d9431`.
- **Voice harness v2 canonical rebuild + Railway deploy** — DELETE v1 → REBUILD mirroring chat-deepagents (`harnesses/voice-deepagents/{agent,llm_adapter,session,main}.py` + Dockerfile + tests). Deployed to new Railway service `indemn-runtime-voice` (id `df2349d6`). Multi-turn voice test created real Touchpoint `69f4ed4f03e56394d808bc88` with Branch + Dan Spiegel.
- **Chat-side log-touchpoint verified** — chat-deepagents Touchpoint `69f4f2ca03e56394d808bd6d` created via deployed `indemn-runtime-chat` after migration to CLI-only skill loading.
- **Voice OS Assistant actor created + activated** — bound to voice runtime, log-touchpoint skill assigned, mode=hybrid.

### Architectural cleanup
- **chat + voice harnesses migrated to CLI-only skill loading** (`7197f08` mirroring async-deepagents `7281b83`). Drops the deepagents filesystem-skills layer entirely. Eliminates the Bug #35 class for both harnesses. New `build_system_prompt(associate)` helper composes per-associate system prompts with `execute('indemn skill get <ref>')` directives.
- **harness_common.cli resolves indemn via sys.executable** (`33d12f7`). Eliminates the `/opt/homebrew/bin/indemn` (Node.js CLI from `@indemn/cli` npm package) collision that was silently breaking the harness in spawn-mode subprocesses. Prior PATH-based lookup worked on Railway by coincidence; broke on local dev.

### LangSmith tracing on voice
- **Voice DeepagentsLLM passes RunnableConfig with metadata + tags + run_name** (`27e9304`). Voice traces now appear in `indemn-os-associates` project queryable by associate_id / entity_id / runtime_id (per CLAUDE.md § 8 debugging recipe). Verified live.

### Bug fixes (kernel + integration)
- **Bug #46** — kernel `fetch_new` watermark fallback chain (`date` → `posted_at` → `created_date`). Pre-fix: SlackMessage + Document silently re-fetched the same content every cron tick. Post-fix verified live: Document fetch-new immediately surfaced 5 NEW Drive files that the broken cron had been missing for ~17h.
- **Bug #45c** — kernel resolver `Step 3` query uses `$or` to tolerate null/missing `access` on org integrations. Plus better error message when integration exists but doesn't match (uses `Integration.find().count()` to hint at status/access mismatch).
- **Bug #39** — `register_entity_routes` honors `_collection_name` (set by `--collection-name` operator override) and `Settings.name` (kernel Beanie entities) before falling back to naive plural.
- **Bug #12** — `indemn/dev/shared/mongodb-uri` AWS Secret value corrected (was wrong host `dev-indemn-pl-0`; should be `dev-indemn`). Wrapper scripts now connect cleanly.
- **Bug #47** — `indemn-runtime-chat` Railway env `INDEMN_SERVICE_TOKEN` was stale (didn't match AWS Secrets Manager value). Service had been failing startup with 401 for unknown duration. Updated + redeployed.
- **Bug #13 followup** — added voice-deepagents + harness_common rows to docs/guides/development.md deploy table.

### Skills
- **slack-fetcher skill** (NEW, v1) — created at `projects/customer-system/skills/slack-fetcher.md`, uploaded to dev OS.
- **log-touchpoint skill** (v3) — entity-resolve param shape corrected to `{"candidate": {...}}`.

---

## Open design questions (carried forward)

These mostly fold into TD-4's research session per the Session 13 alignment:

1. **Opportunity vs Problem entity** — surfaces from TD-4 research observing unmapped pain
2. **Document-as-artifact pattern for emails** — RESOLVED in TD-5 alignment (Email entity with `status: drafting`)
3. **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle's Apr 24 ask) — research-driven in TD-4
4. **Origin / referrer tracking** — surfaces from TD-4 research
5. **Playbook hydration mechanism** — RESOLVED in TD-4 alignment
6. **Drive content extraction** — current Drive adapter populates metadata only; Google Docs/Sheets/Slides export, PDF text extraction, image OCR are future enrichment passes
7. **Bug #40 architecture** (NEW, design-level) — `cron_runner` actor mode vs `ScheduledActorWorkflow` peer to ProcessMessageWorkflow. Deep design needed in next session.

---

## Operating-system worktree state at close

**Branch:** `os-roadmap` (this worktree at `.claude/worktrees/roadmap/`).

**Commits to push at end of session protocol** — pricing-framework session's `381b773` + this session's project-doc updates committed in protocol.

**Uncommitted changes at session close (will commit in protocol):**
- `M projects/customer-system/CURRENT.md` — this rewrite
- `M projects/customer-system/SESSIONS.md` — Session 15 entry to append at top
- `M projects/customer-system/os-learnings.md` — Bug #45/46/47/45c/39/12/13/40 row updates + Bug #45b row
- `M projects/customer-system/roadmap.md` — TD-1 marked complete; "Where we are now" updated
- `M projects/customer-system/CLAUDE.md` — Session 15 entry in § 5 Journey
- `M projects/customer-system/INDEX.md` — Decisions, Open Questions, Artifacts updates
- `M projects/customer-system/skills/log-touchpoint.md` — v3 entity-resolve param shape fix
- `M projects/customer-system/artifacts/2026-04-30-voice-deepagents-runbook.md` — v2 rewrite
- `?? projects/customer-system/skills/slack-fetcher.md` — NEW slack-fetcher skill content

---

## Next session — focus

**Use `PROMPT.md` as the kickoff prompt** with this objective slot:

> *Bug #40 architectural work — deterministic scheduled-actor execution path. The 4 fetcher actors (Email, Meeting, Drive, Slack) currently run via mode=hybrid + LLM agent on every cron tick. ~1000 LLM calls/day across 4 fetchers for what should be deterministic shell exec. Two design choices to think deeply about: **(A) New `cron_runner` actor mode** that bypasses the LLM and treats the skill content as a literal CLI command. Skill format convention needed (e.g., `## Command\n<command>` section, or one-line skills). Update Email/Meeting/Drive/Slack-Fetcher actors to use it. **(B) New `ScheduledActorWorkflow`** peer to `ProcessMessageWorkflow` — runs `indemn` CLI directly via Temporal activity, no harness involved. Bigger architectural lift but cleaner separation. Pick the right approach + execute. After Bug #40: TD-2 begins (cascade activation: build MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher; activate progressively bottom-up; systematic historical replay across the ~930 emails + 67 meetings + 860 SlackMessages).*

**Key follow-ups carried into next session:**
- Bug #40 deep design + implementation (highest priority for next session per Craig)
- Bug #19 follow-on (test fixture pattern improvement) — no code action; surfaces as we add tests
- Voice runtime stale instances (~13 expired ones in `instances` array) — kernel TTL sweep handles naturally; no action needed
- Slack token rotation — old token still in plain-text conversation history from Session 14; non-blocking
- Drive "full crawl" — only 30-day backfill done; if "every Drive file ever" is required, run `indemn document fetch-new --data '{"since":"2020-01-01"}'` once. Per Session 15 closeout: hourly cron is now picking up new content correctly post-Bug-#46-fix; treating "harness running and picking up new content" as the spirit of the done-test.

**TD-1 done-test (now ALL passing):**
- All 4 fetcher actors active with `trigger_schedule` running ✓
- New entities flow in within configured cadence ✓
- Backfills: 30-day Meeting ✓, 90-day Slack ✓ (+ 586 deeper bonus), Drive 30-day ✓
- Pre-flight cleanup verified ✓ (Session 14)
- Manual entry working via OS Assistant `log-touchpoint` skill — voice ✓ (Touchpoint `69f4ed4f`), chat ✓ (Touchpoint `69f4f2ca`)
- Document.source enum includes `slack_file_attachment` ✓
- All entities sit at `received`/`logged` — cascade NOT activated ✓

After TD-1 closes (today): Bug #40 design (next session) → TD-2 begins.

---

*This file is rewritten every session. Don't append — replace. The history lives in SESSIONS.md.*
