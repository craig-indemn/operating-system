# OS Bugfix Session — Resume Prompt

**Living document.** Update the "UPDATED PRIORITY" block whenever the main session surfaces new high-priority bugs in `os-learnings.md`. Update the "Recent fork-session progress" block whenever the fork session marks rows 🟡 In-progress / 🟢 Fixed.

**How to use:**
1. In the bugfix session, run `/clear` to wipe conversation history (or close + reopen the session in the same worktree).
2. Paste the prompt below as the first message in the cleared/fresh session.
3. The session bootstraps from durable shared context (`vision.md`, `roadmap.md`, `os-learnings.md`, `INDEX.md`, `CLAUDE.md`, the trace artifacts) — no human-in-the-middle handoff required beyond the prompt itself.

**Why this works:** the shared context lives in project files, not in conversations. A fresh session reading `os-learnings.md` sees what the previous instance marked 🟡 In-progress and 🟢 Fixed. The resume prompt just adds framing ("you're a resumed session, here's what's urgent right now") — the actual context comes from the files.

**Last updated:** 2026-04-28 — after burst #4 of bugfix-resume (waves 1-6 in one continuous session) cleared the entire load-bearing stack: bulk-delete operator filters + workflow counts + preview ObjectId/retry (Bugs #23/#24/#32), reprocess primitive (Bug #10), boundary coercion + auto_resolve flag (Bug #9), CLI papercut cluster (Bugs #11/#20/#21/#28), always-fresh entity skill rendering, and Bug #30 propagation via auto-emit partialFilterExpression. **The kernel is in genuinely solid shape now.** What's left in `os-learnings.md` is mostly customer-system domain work (belongs to the main session) plus one substantive OS feature and a handful of small papercuts. The next session may wrap up faster than previous bursts.

---

## The prompt (paste verbatim into the cleared/fresh bugfix session)

```
You are resuming the parallel OS-bugfix session that has been running alongside the customer-system 
main session. The previous instance was cleared to free context. Pick up from the durable shared 
context — `os-learnings.md` is your work queue.

The MAIN session is using the OS in production now (not in a blocked trace). Your job is to keep 
working systematically through the open bugs in `os-learnings.md`, in priority order, so the OS 
keeps getting better underneath them. Each bug fix should be small, well-tested, deployed, and 
documented before you move to the next.

==== Working directories (unchanged) ====
- Project context: /Users/home/Repositories/operating-system/.claude/worktrees/<your-worktree>/projects/customer-system/
- OS kernel code: /Users/home/Repositories/indemn-os/
- OS docs: /Users/home/Repositories/indemn-os/docs/

==== Start-of-session protocol (mandatory) ====

1. Read these files in full:
   - projects/customer-system/CLAUDE.md
   - projects/customer-system/vision.md
   - projects/customer-system/roadmap.md
   - projects/customer-system/os-learnings.md          ← YOUR WORK QUEUE. Confirm the current state.
   - projects/customer-system/INDEX.md                 ← Decisions log + open questions
   - projects/customer-system/artifacts/2026-04-24-os-bugs-and-shakeout.md   ← Bug-level deep detail
   - /Users/home/Repositories/indemn-os/CLAUDE.md
   - /Users/home/Repositories/indemn-os/docs/architecture/entity-framework.md
   - /Users/home/Repositories/indemn-os/docs/architecture/watches-and-wiring.md
   - /Users/home/Repositories/indemn-os/docs/architecture/associates.md

2. Check `os-learnings.md` for in-flight work:
   - Rows marked 🟡 In-progress = work the PREVIOUS instance started. Decide whether to continue 
     it (look at any branch in indemn-os matching the bug's name; check git log for commits) or 
     restart from scratch.
   - Rows marked 🟢 Fixed since 2026-04-27 = the previous instance(s) completed something. Don't 
     redo. Read the linked commits to understand what's already there before designing.
   - Rows still 🔴 Open = available work.

3. Before writing any code, confirm your understanding by writing back: 
   a) the top-3 bugs you intend to tackle in priority order (RE-PRIORITIZED based on what you see in 
      os-learnings.md NOW — see "UPDATED PRIORITY" below), 
   b) why those three (what they unblock for the customer system + Phase B foundation), 
   c) any in-progress work from the previous instance you're picking up vs starting fresh, 
   d) where the work happens (which files in indemn-os/), 
   e) how you'll test each fix.

==== UPDATED PRIORITY (post-Apr-28 burst — kernel substantially hardened) ====

**Read this first.** The previous session shipped 9 fixes across one continuous burst. The 
kernel is in genuinely solid shape — most of the load-bearing items in `os-learnings.md` are 
now 🟢. Before you pick up new work, internalize what's true now vs what was true a session 
ago, because it changes the priority shape:

What the kernel now has (don't re-derive these from os-learnings.md — read the architecture 
docs to understand the current contract):

- **Filter safelist** in `kernel/api/_filter_safelist.py` — three layers (field-name allowlist, 
  operator allowlist `$in/$nin/$ne/$gt/$gte/$lt/$lte/$exists`, per-field type coercion including 
  Pydantic alias support). Used by both list endpoint and per-entity bulk routes.
- **Bulk workflow surfaces real counts** — `BulkExecuteWorkflow` returns `{matched, succeeded, 
  errored, errors}` with `completed_no_match` status when matched=0. `GET /api/bulk/{id}` fetches 
  `handle.result()` on terminal states. Preview activity has bounded retry policy.
- **Reprocess primitive** in `kernel/message/reprocess.py` — emits ONE message scoped to a named 
  role's watch, fresh `correlation_id`, `causation_id="reprocess:<hex>"`, `event_metadata.reprocess=True`, 
  `event_metadata.reprocess_requested_by=<actor_id>`. New `POST /api/{collection}/{id}/reprocess` 
  endpoint + auto-registered CLI `indemn <entity> reprocess <id> --role <role>`.
- **Boundary coercion** in `_resolve_relationship_dict_inputs` — dict on relationship field gets 
  a 400 with shape hint by default; opt-in `auto_resolve: bool` field flag triggers `entity_resolve` 
  with single-1.0 auto-link. Set `auto_resolve=true` on Email.company etc. and the API boundary 
  handles dict-shaped LLM input transparently.
- **Auto-fresh entity skills** — `indemn skill get <Entity>` re-renders from current 
  EntityDefinition + current generator at GET time. Stored Skill row is a cache, not source of 
  truth. Every generator improvement propagates to every entity instantly.
- **Auto-emit partialFilterExpression on unique+nullable** — the reconciler treats `unique: true` 
  on an Optional field as "unique-when-set" automatically. Bug #30-class create-500s are 
  prevented at the kernel level, no operator opt-in needed. Existing latent traps (deals.deal_id, 
  emails.external_ref) auto-healed at deploy time.
- **CLI parity** — `indemn actor transition/delete` exist; `actor list --type` filters via the 
  safelist; transition API canonical body field is `to`; `/api/queue/stats` aliased.

The customer-system-vs-OS reframe matters: a lot of "open" rows in os-learnings.md are actually 
**customer-system domain work** (skill updates, entity-definition tweaks, integration setup), 
not OS kernel work. The fork session is for OS work. Hand domain work back to the main session.

Suggested order for the next burst (push back if you spot a dependency):

1. **`--include-related` reverse relationships.** This is the only substantive OS-feature gap 
   left. Today `--include-related` follows forward references (fields where `is_relationship: 
   true` on this entity) but not reverse — entities that point AT this one are invisible. For 
   the customer-system constellation queries (vision.md item #5: "the constellation is queryable"), 
   this is the missing piece. Fix probably lives in `kernel/message/emit.py::_build_context` 
   (where the depth>=2 lookup happens today) or wherever the API endpoint with `include_related=true` 
   resolves relationships. Walk all EntityDefinitions, find ones with `is_relationship: true` 
   pointing at THIS entity, query each, attach to `_related`. Test against Touchpoint (the 
   canonical reverse-ref case: `Meeting.touchpoint -> Touchpoint`).

2. **Bug #5 + Bug #7 + Bug #8 — adapter / CLI ergonomics cluster.** Small.
   - Bug #5: `indemn fetch-new --help` shows `---cap` and `---slug` triple-dash internal-routing 
     params. Hide them; add `--data` JSON-shape docs per capability.
   - Bug #7: Google Workspace adapter logs "Missing required parameter 'fileId'" 50+ times per 
     fetch — short-circuit when fileId is empty.
   - Bug #8: Adapter swallows per-user `except Exception` — track success rate; raise if all/most 
     users fail with the same error class.

3. **Bug #15 — naive collection pluralization.** `Company` → `companys`, `Opportunity` → 
   `opportunitys`. Use the `inflect` library OR require explicit `collection_name` in entity 
   defs and fail loudly if missing. Existing collections (`companys`, `opportunitys`) need 
   migration or doc update — flag the migration path before starting.

4. **Bug #19 — Change records sometimes have non-Date timestamp.** Find the code path writing 
   strings; ensure `datetime.now(UTC)` server-side. Low severity but observability nuisance.

5. **Ingestion durability companion to Bug #10** — Gmail/Meet adapters copy transcripts into 
   Document at ingestion time so they survive 30-day source retention. Substantive integration 
   work. The reprocess primitive (already done) only helps if the source content still exists.

6. **Bug #12 + Bug #13 — infrastructure config (asks Craig).** `mongodb-uri` AWS secret has wrong 
   host; Railway doesn't auto-deploy on push to main. Both require explicit user authorization. 
   Just flag and ask before doing anything.

**Customer-system domain work — DO NOT do these in the fork session, hand back to the main 
session:**
- Bug #16/#17 finishing — Email Classifier + Touchpoint Synthesizer skill updates (or just set 
  `auto_resolve=true` on the relationship fields, now that the kernel supports it; that may 
  obviate the skill changes entirely).
- Email.interaction → Touchpoint rename (entity definition change).
- Document.source enum missing `slack_file_attachment`.
- Proposal state machine `superseded` transition.
- Touchpoint scope/Contact-resolution chicken-and-egg (skill design).
- Slack ingestion design (split between adapter [OS] and integration setup [domain]).

**One-off cleanup pending** (mechanical, do whenever): `indemn bulk cancel <wf>` against the 5+ 
zombie bulk workflows from before the Bug #32 retry-policy fix. They'll auto-clear on Temporal's 
workflow execution timeout, just slowly.

==== Operational notes for this session ====

- The kernel is healthier than at any previous bugfix burst. Your work may be smaller in scope. 
  That's fine — don't manufacture work to fill a session. If the priorities above are cleared 
  and what's left in os-learnings.md is genuinely customer-system territory, **end the burst 
  cleanly and let the main session run**.
- The chat runtime is still failing startup with `Error 401: Invalid service token` — pre-existing, 
  needs Craig to rotate the token. Don't try to fix it yourself; flag if it surfaces.
- The deploy pattern for kernel-image services (api / temporal-worker / queue-processor) is: 
  deploy `indemn-api` for any API/route/handler change; deploy `indemn-temporal-worker` 
  additionally if you touched workflow code (`kernel/temporal/workflows.py` or activities); 
  the queue-processor rarely needs separate deploy. The reconciler runs at every kernel-image 
  startup so any one of them updating indexes is fine.
- Bug #30 propagation auto-heals on deploy now. If you see a "Dropped kernel index ... Created 
  kernel index ... partialFilter=..." log line at startup, it's the reconciler self-healing a 
  latent unique+nullable trap. Working as designed.

==== Rules of engagement (unchanged) ====

- **Production safety.** Read .claude/rules/production-safety.md. NEVER write to production systems 
  or modify EC2 instances without explicit user permission. The OS API runs on Railway — read state 
  freely; deployments need explicit OK. Read-only on shared databases (you can write to dev MongoDB 
  via the API; never via mongosh).

- **Branch-per-bug.** Make a feature branch in indemn-os, push, merge once tests pass. Craig has 
  authorized you to merge PRs that look good (per his note in the previous session). If unsure, 
  flag and ask.

- **Update os-learnings.md when a bug changes status.** Mark a row 🟡 In-progress when you start; 
  🟢 Fixed when commit lands in main + is deployed (with commit ref and date). Don't delete fixed 
  rows — they're the trail.

- **Coordinate via os-learnings.md.** The main session is running in parallel. Re-read 
  os-learnings.md before starting each new bug. Mark rows 🟡 immediately when you start so the 
  main session knows not to grab them.

- **Log new bugs you discover.** Add a row to os-learnings.md with detail before continuing.

- **Test what you fix.** Use existing tests/unit, tests/integration, tests/e2e. Add basic coverage 
  for the fix path if none exists. Run the relevant test suite before declaring done.

- **Update OS docs to reflect what changed.** /Users/home/Repositories/indemn-os/docs/architecture/*.md 
  and /Users/home/Repositories/indemn-os/docs/guides/*.md need to stay accurate.

- **Push back on the priority order if you spot a dependency.** If the code says #2 needs #1 to 
  land first or vice versa, flag it before starting.

- **Use TaskCreate to track progress.** The previous sessions used the task system; continue.

Begin by completing the start-of-session protocol, then write back with the 5-part response from 
step 3. We iterate from there.
```

---

## Recent fork-session progress (snapshot — derived from `os-learnings.md`, kept here for quick scan)

This block is a courtesy summary of what the bugfix session has done recently, so Craig can see at a glance what state the parallel work is in without re-reading `os-learnings.md`. Update whenever a fork session marks rows 🟡 / 🟢.

**As of 2026-04-28 morning (post-bugfix-resume #4, sixth wave — Bug #30 prevention auto-emit shipped):**

Ninth burst (continued from same session — defensive-by-default fix):
- 🟢 **Bug #30 propagation → auto-emit partialFilterExpression on unique+nullable fields** — merged `db23749` (feature commit `2948491`). Instead of auditing each entity def and adding `sparse: true` manually, the reconciler now auto-emits the partial filter when `unique=True AND not required AND default is None`. New helper `_is_effectively_nullable(fdef)`. The kernel takes a stand: `unique: true` on an `Optional` field means "unique-when-set", full stop. **Healing on deploy:** 2 latent create-500 traps auto-fixed at indemn-api startup — `deals.deal_id` and `emails.external_ref` both went from `unique=True, partialFilter=None` to `unique=True, partialFilter={field: {$type: <bson_type>}}`. 4 new unit tests; existing tests updated for the new contract; full 320-test suite green. **Prevents future Bug #30-class incidents entirely** — every nullable+unique field is correctly indexed by default, no operator opt-in required.

**As of 2026-04-28 morning (post-bugfix-resume #4, fifth wave — always-fresh entity skills shipped):**

Eighth burst (continued from same session — compounding-leverage fix):
- 🟢 **Stale entity-skill rendering** — merged `e83a17d` (feature commit `2f163b1`). Picked always-fresh-on-GET via new `_refresh_entity_skill` helper called inside `get_skill`, `get_skill_by_name`, `list_skills`. For `type="entity"`, looks up current EntityDefinition by `(name, org_id)` and re-renders via `generate_entity_skill` — the stored Skill row becomes a cache, not source of truth. Associate skills (authored) still serve stored content with content_hash tamper detection. Hash recomputed only when content actually changes (no spurious churn). Org-scoped lookup. Fallback to stored content if EntityDefinition was deleted. 6 unit tests; full 316-test suite green. **Verified live:** Contact (`updated_at: 2026-04-18` — never touched after any of the round's generator improvements) now serves 2121-char content with JSON `--data` examples, the Reading section, and `--include-related` docs. Every future generator improvement now propagates to every entity instantly — compounding fix.

**As of 2026-04-28 morning (post-bugfix-resume #4, fourth wave — CLI/API papercut cluster shipped):**

Seventh burst (continued from same session, after the customer-system-vs-OS reframe — focus stays on true OS work):
- 🟢 **Bug #11 + #20 + #21 + #28 — Actor CLI parity, transition field naming, queue stats alias** — merged `e9d04da` (feature commit `008efcd`). Bug #20: added `actor transition <id> --to <state>` (the documented CLI that didn't exist) + `actor delete <id> [--yes]` routing through bulk-delete (gets the same audit + watch-evaluation path as every other delete; Bug #23's $oid fix made it reliable). Bug #28: `actor list --type associate` was sending `?type=...` which the auto-list ignored; switched `--type` and `--status` to flow through the standard `?filter={...}` safelist (Bug #23) so they actually filter. Bug #21: `docs/guides/adding-entities.md:135` showed curl with `target_state` but the API has only ever accepted `to`; corrected the doc to canonical `to` (matches CLI's `--to` flag). Bug #11: `/api/queue/stats` 404'd because the handler was at `/api/_meta/queue-stats`; aliased so both work, `/api/queue/stats` now canonical for human use. Full 310-test suite green (no new tests — config-style changes covered by live verification). **Verified live:** queue stats both paths return identical 6-row aggregate; actor list --type returns only the 4 associates instead of 23+ all actors; active→suspended→active round-trip on OS Assistant via the API confirms transition CLI's target endpoint is wired right; `target_state` body still rejected with `'to' state is required` confirming canonical name.

**As of 2026-04-27 late-evening (post-bugfix-resume #4, third wave — Bug #9 boundary coercion shipped):**

Sixth burst (continued from same session):
- 🟢 **Bug #9 — dict-shaped values for relationship fields now caught at the API boundary** — merged `31bb594` (feature commit `9f83ac5`). Two-layer fix in new `_resolve_relationship_dict_inputs(entity_cls, name, data)` helper called before `_coerce_objectid_fields` in both create and update. **Default reject:** dict on relationship field → 400 with field + target + canonical `_id` shape + offending value verbatim + pointer to `entity-resolve`. **Opt-in entity_resolve fallback** via new `auto_resolve: bool = False` on FieldDefinition; when set + target has entity_resolve activated, calls resolve and auto-links only on single 1.0 candidate (else 400 with candidate list). Defense-in-depth on top of the skill examples (`b83fa08`) so a misbehaving LLM gets self-correcting 400s instead of dead letters. 14 unit tests; 310-test suite green. **Verified live:** POST/PUT with dict company → 400 with full shape hint; hex string still works (helper is idempotent on non-dict values). Deployed `indemn-api`.

Fifth burst (continued from same session):
- 🟢 **Bug #10 — `reprocess` primitive for backfilling watches against historical entities** — merged `662dc2d` (feature commit `767a3ef`). New `kernel/message/reprocess.py::reprocess_for_role(entity, role_name, event_type="created")` emits ONE message scoped to the named role's watch — not broadcast. Validates role has a matching watch and surfaces actual events when there's no match. Fresh correlation_id per call (new chain), `causation_id="reprocess:<hex>"` sentinel, `event_metadata.reprocess=True` + `reprocess_requested_by` (Bug #22 forensics chain). New `POST /api/{collection}/{id}/reprocess` endpoint + auto-registered CLI verb `indemn <entity> reprocess <id> --role <role>`. 13 unit tests; full 296-test suite green. **Verified live:** all 6 scenarios pass (happy path; unknown role → 400 with "add-watch" hint; wrong event_type → 400 listing actual events; 404 on missing entity; 400 on missing role param; distinct correlation_ids on repeat). Companion ingestion-durability gap (copy transcripts into Document at ingestion time so they survive 30-day source retention) remains 🟡 partial — separate ingestion-side change.

**As of 2026-04-27 evening (post-bugfix-resume #4 — Bug #23/#24 cleanup-at-scale work done):**

Fourth burst (cleanup-at-scale + verification-driven follow-ups):
- 🟢 **Bug #23 + #24 — bulk-delete operator filters + visible bulk counts** — merged `0ed8c80` (feature commit `62f3254`) + alias-fix `6b8c62e` + Bug #32 fix `b5e4757`. New `kernel/api/_filter_safelist.py::parse_filter` provides a shared three-layer safelist: field-name allowlist via `entity_cls.model_fields` (with Pydantic alias support so `_id` works alongside the canonical `id`), operator allowlist (`$in`/`$nin`/`$ne`/`$gt`/`$gte`/`$lt`/`$lte`/`$exists`), per-field type coercion (ObjectId hex / `$oid` → `bson.ObjectId`; ISO 8601 / `$date` → `datetime`; including `$in` list elements). `_parse_list_filter` becomes a thin wrapper. Per-entity `_register_bulk_route::start_bulk` validates `filter_query` at the API boundary → fast 400 on bad input. Activity re-runs `parse_filter` to produce typed values for `find_scoped()` (typed values can't cross Temporal serialization). `BulkExecuteWorkflow` returns `{matched, succeeded, errored, errors}` with status `completed_no_match` when matched=0. `GET /api/bulk/{id}` fetches `handle.result()` on terminal states and merges into response. 56 unit tests pass + full 283-test suite green. **Verified live:** Test 1 `$in` deleted 2 throwaway companies; Test 2 `$gte` datetime dry-run returned 3 matches with JSON-safe sample; Test 3 no-match → `completed_no_match`; Test 4 bad input → 400 with field-level error. Deployed both `indemn-api` and `indemn-temporal-worker`.
- 🟢 **Bug #32 — preview activity ObjectId serialization + missing retry policy** — surfaced during Bug #23 verification. Pre-existing latent bug exposed by Bug #23's correct `current_org_id.set()` fix (old code's missing org_id meant samples were empty in non-admin queries → no serialization needed → bug masked). `preview_bulk_operation` returned `[e.model_dump() for e in sample]` — raw ObjectId values that Temporal's data converter couldn't encode → activity failed forever. Plus the workflow's `execute_activity(preview, ...)` had no retry_policy → infinite retry. Fix: use `kernel.api.serialize.to_dict()` for sample entities + `RetryPolicy(maximum_attempts=3, non_retryable_error_types=["PermanentProcessingError"])`. Merged `b5e4757`, deployed temporal-worker. Explains the 5+ zombie workflows visible in `bulk list` from earlier today (and one from Apr 18) — they're stuck in the same retry loop. Pre-existing zombies won't auto-clear; can be `indemn bulk cancel <wf>`.

**As of 2026-04-27 (post-bugfix-resume #3 — three burst sessions done; kernel substantially hardened):**

Pre-existing in-progress PRs from the first burst (reviewed and merged):
- 🟢 **Touchpoint Option B** — `indemn entity modify Touchpoint --add-field` + `indemn-api` redeploy + Synth skill v3.
- 🟢 **Cross-invocation tool-cache leak** — merged `ac6d475` (feature commit `4e7e83d`). 6 unit tests. Deployed.
- 🟢 **Silent workflow stuck-state** — merged `67f006c` (feature commit `852eeaa`). 20 unit tests. Deployed.
- 🟢 **Generated entity skill teaches actual filter syntax + Bug #6** — merged `f4fc121` (feature commit `6af2166`). 18 unit tests. Deployed.

Top-4 from the second burst (post-Alliance-trace findings):
- 🟢 **#1 — API 500 transparency** — merged `cf5acd8` (feature commit `914fc61`). Pydantic ValidationError → 400 with field-level errors; catch-all Exception → 500 with `{error, type, message}`. 10 unit tests. Deployed.
- 🟢 **#2 — Meeting create HTTP 500** — fixed by Bug #30 (declarative index reconciliation + sparse → partialFilterExpression translation). Same root cause unblocked Bug #25 (Company create 500). Merged `869a153` + `f09a07b` + `83d2494`. Deployed. Verified end-to-end.
- 🟢 **#3 — Entity skill JSON-shape examples** — merged `b83fa08` (feature commit `ab987c6`). Working `--data` payloads for create/update with type-appropriate placeholders (ObjectId hex, ISO datetime, first enum value, state field excluded). 18 new unit tests (28 total in file). Deployed.
- 🟢 **#4 — Bug #29 entity-def route eviction** — merged `83d2494` (feature commit `0bd4e50`). `_evict_routes_for_prefix` helper called in `register_entity_routes` before `app.include_router`. 7 unit tests inc. end-to-end TestClient roundtrip. Deployed.

Third burst (systematic continuation after the trace-blocking work cleared):
- 🟢 **List endpoint arbitrary field filters** — merged `df92cca` (feature commit `6293260`). New `_parse_list_filter` validates field names, coerces ObjectId hex strings, rejects operator dicts (forward-compat). CLI gains `--data '{"field":"value"}'` plus `--search`/`--sort`. Skill generator's Reading section teaches the new pattern. 14 parser tests + 3 generator tests. Deployed. Verified live.
- 🟢 **Bug #31 — entity_resolve kernel capability (subsumes Bug #16 + #17 root)** — merged `a5a1c97` (feature commit `579c713`). Domain-agnostic kernel capability: `field_equality` strategy (with normalizer registry: email/domain/lowercase_trim/none) + `fuzzy_string` strategy via rapidfuzz. Combined with max-score-per-id + matched_on union, sorted, capped. Added to COLLECTION_LEVEL_CAPABILITIES. Skill generator emits a Resolve section when activated. 29 unit tests. Activated on Company. **Verified live against real Alliance + FoxQuilt data:** the dupe pairs surface correctly (canonical + auto-create artifact), no false positives on nonexistent names. Bug #16 + #17 marked 🟡 (kernel ready, skill update pending — Email Classifier + Touchpoint Synthesizer skills still need to call resolve before creating).
- 🟢 **Bug #22 — effective_actor_id forensics chain** — merged `e9d45e8` (feature commit `dae5bf2`) + trace serializer fix `056cba2`. New optional field on ChangeRecord, contextvar, header-based propagation, env-var passthrough. Compound index on `(org_id, effective_actor_id, timestamp)`. Trace endpoint surfaces both `actor_id` and `effective_actor_id`. 10 unit tests + full 226-test suite green. **Verified live** — POST a Company create with `X-Effective-Actor-Id: <Email Classifier>`; trace returns both fields. Going forward every harness-driven mutation carries the associate identity.
- 🟢 **async-harness import regression** — merged `65dddfa`. The silent-stuck-state PR's bare `from completion_logic import ...` failed in production (worked under pytest only); aligned to `from harness.completion_logic` like the file's other imports. Caused a deploy-failure email storm before the fix; should be quiet now.

**Production state 2026-04-27 end of third burst:**
- `indemn-api`: healthy, all of the above deployed. Health check passing.
- `indemn-runtime-async`: healthy, both harness fixes (cache-leak + silent-stuck-state + the import fix) deployed.
- `indemn-runtime-chat`: ⚠️ FAILING STARTUP — `Error 401: Invalid service token`. Pre-existing, NOT from any recent fork work. Needs Craig to rotate the chat-runtime service token. Out of scope for the next bugfix session.
- `indemn-temporal-worker` + `indemn-queue-processor`: healthy. WARN-level noise about workflow-already-started + bulk activation retries (transient, related to test cleanups).

**Bugs cleared this round (no longer blocking customer-system work):**
Bug #1, #2 (cache-leak path), #6, #9, #10, #11, #14, #20, #21, #23, #24, #25, #28, #29, #30, #31, #32; Bug #16/#17 (kernel ready, skill update belongs to main session); #22.

**Reframe (Apr 28 morning):** what's left in `os-learnings.md` mostly isn't OS-kernel work — it's customer-system domain-skill / entity-definition work that belongs to the main session (Bug #16/#17 finishing, Email.interaction → Touchpoint rename, Document.source slack_file_attachment, Proposal `superseded` transition, Touchpoint scope/Contact-resolution chicken-and-egg, Slack ingestion design). After this seventh burst, the truly remaining OS-kernel work is small papercuts:

**True OS work still open (next burst candidates):**
- `--include-related` reverse relationships (kernel relationship traversal — substantive)
- Ingestion durability companion to #10: Gmail/Meet adapters copy transcripts into Document at ingestion so they survive 30-day source retention (kernel integration adapter)
- Bug #5 (`fetch-new --help` triple-dash flags + missing `--data` doc), Bug #15 (naive collection pluralization), Bug #19 (changes timestamp string vs Date), Bug #7 (adapter noisy fileId warnings), Bug #8 (adapter swallows per-user errors) — small CLI/adapter cleanup.
- Bug #12 (wrong MongoDB URI in AWS secret), Bug #13 (Railway auto-deploy docs/setup) — infrastructure config.

**Customer-system domain work (handed back to main session):**
Bug #16/#17 finishing (Email Classifier + Touchpoint Synthesizer call `entity_resolve` before creating, OR opt into Bug #9's `auto_resolve` flag), Email.interaction → Touchpoint rename, Document.source enum, Proposal state machine, Touchpoint scope/Contact-resolution, Slack ingestion design.

**One-off cleanup pending:** `indemn bulk cancel <wf>` the 5+ zombie bulk workflows from before the Bug #32 retry-policy fix; or leave them to time out on Temporal's workflow execution timeout.

---

## How to update this file

1. **When the main session surfaces a new high-priority bug**, edit the "UPDATED PRIORITY" block above to add it (and re-rank if needed).
2. **When a fork session marks a row 🟡 / 🟢 in `os-learnings.md`**, add/update the entry in "Recent fork-session progress" so Craig and future fork sessions can see at-a-glance status without re-reading the full register.
3. **When the trace narrative changes** (e.g., a new live trace is in flight, or the active trace changes), update the file references in the start-of-session protocol.
4. **When the rules of engagement change** (e.g., new constraints from `production-safety.md`, new branch-naming convention, etc.), edit the "Rules of engagement" block.

The file's value is that it's always usable as-is — a fresh fork session pasting the latest version always lands on the highest-priority work and never duplicates effort.

---

## Sister artifacts

- `projects/customer-system/fork-prompts/` — this directory holds prompts for parallel-session work tied to the customer-system project
- `projects/customer-system/os-learnings.md` — the work queue; this prompt's authority comes from that file being the canonical state
- `projects/customer-system/roadmap.md` — the "Continuous threads" section calls out **OS bug convergence** and **shared-context-update mechanism** as first-class operating disciplines; this file is one realization of both
- `projects/customer-system/CLAUDE.md` — the project orientation that the resumed session reads at bootstrap
