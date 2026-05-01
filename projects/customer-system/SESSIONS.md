# Customer System — SESSIONS

> **Append-only log of session objectives + outcomes.** New entries at the **top**. Each session adds one entry at end of session. Loaded on-demand when a session needs to look back at history or learn the objective-statement format from prior entries.
>
> The full Journey lives in `CLAUDE.md § 5`. This file is the lighter-weight per-session log.

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
