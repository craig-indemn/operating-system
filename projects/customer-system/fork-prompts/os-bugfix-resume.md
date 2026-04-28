# OS Bugfix Session — Resume Prompt

**Living document.** Update the "UPDATED PRIORITY" block whenever the main session surfaces new high-priority bugs in `os-learnings.md`. Update the "Recent fork-session progress" block whenever the fork session marks rows 🟡 In-progress / 🟢 Fixed.

**How to use:**
1. In the bugfix session, run `/clear` to wipe conversation history (or close + reopen the session in the same worktree).
2. Paste the prompt below as the first message in the cleared/fresh session.
3. The session bootstraps from durable shared context (`vision.md`, `roadmap.md`, `os-learnings.md`, `INDEX.md`, `CLAUDE.md`, the trace artifacts) — no human-in-the-middle handoff required beyond the prompt itself.

**Why this works:** the shared context lives in project files, not in conversations. A fresh session reading `os-learnings.md` sees what the previous instance marked 🟡 In-progress and 🟢 Fixed. The resume prompt just adds framing ("you're a resumed session, here's what's urgent right now") — the actual context comes from the files.

**Last updated:** 2026-04-27 — after the third bugfix-session burst that cleared the API-500-transparency / Meeting-create / Bug #29 / index-reconciliation / list-filter / entity-resolve / effective-actor-id stack. The Alliance trace is no longer blocked on a kernel bug; the next session is systematic bug clearing.

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

==== UPDATED PRIORITY (post-Apr-27 third bugfix burst) ====

The trace-blocking bugs are all fixed. The kernel now has: typed 500 errors, declarative index 
reconciliation with sparse-via-partialFilterExpression, route eviction on entity-def replace, 
entity_resolve capability with field_equality + fuzzy_string strategies, list-endpoint arbitrary 
field filters, effective_actor_id forensics chain, and a clean modify_fields path on 
entity-def modify. The next priorities are mostly mechanical bugs that improve daily ergonomics 
+ enable scale cleanup.

Suggested order (push back if dependencies surface):

1. **Bug #23 + Bug #24 — `bulk-delete` operator filters + `bulk status` counts.** 
   Critical for cleanup at scale. Today only simple equality filters work in bulk-delete; `$in`, 
   `$gte`, `$ne`, `$oid`, `$date` are silently dropped (Bug #23). And `bulk status` returns 
   `COMPLETED` even when zero records matched (Bug #24), so you can't tell the operation did 
   nothing. Combined, they make non-trivial cleanup almost impossible — the 446-Company half-finished 
   cleanup in the GR Little trace stalled here. The fix probably touches `kernel/temporal/workflows.py::BulkExecuteWorkflow` 
   or `kernel/api/bulk.py` filter parsing. Pair with the new list-filter parser pattern 
   (`_parse_list_filter` in `kernel/api/registration.py`) — same shape, but for delete + with the 
   operator safelist that list filtering doesn't have yet. The operator safelist is the real work; 
   wire it into both list and bulk-delete uniformly.

2. **Bug #10 — `indemn <entity> reprocess <id> --role <role>` (backfill historical entities).** 
   When a watch is added to a role, only future events fire it. Existing entities are invisible. Cost 
   us real work in the GR Little trace (manually creating Touchpoints because the Synth's 
   "Meeting created" watch couldn't refire on already-ingested meetings). Without this, every new 
   associate we add comes with a one-time manual reprocessing chore. Fix: a new CLI/API endpoint 
   that synthesizes a `created`-equivalent event for a named role on an existing entity. 
   Tracked in `artifacts/2026-04-24-extractor-procedure-and-requirements.md` § Capability #6.

3. **Bug #9 — Associates pass dicts instead of ObjectIds → dead letters.** 
   Mostly addressed by the JSON-shape examples we shipped (the auto-generated entity skill now 
   emits real ObjectId hex placeholders). But there's a defense-in-depth piece left: the API's 
   create/update handler could coerce dict-shaped relationship fields at the boundary (e.g. accept 
   `{"company": {"name": "Acme"}}` by resolving via the new entity_resolve capability, OR reject 
   with a 400 explaining the right shape). The skill examples + the existing 
   `_coerce_objectid_fields` helper handle the happy path; this is just the failure-mode improvement.

After the top 3, continue with:

- **Finishing Bug #16 + #17 (kernel ready, skill update pending)** — the Email Classifier and 
  Touchpoint Synthesizer skills need to be updated to call `indemn <entity> entity-resolve` BEFORE 
  creating, and only auto-link on a single 1.0 candidate (else surface for review). This is 
  domain-skill work in `projects/customer-system/skills/` not kernel work — ask Craig if he wants 
  it done in this fork session or in the main session.

- **`--include-related` doesn't follow reverse relationships.** Kernel feature: kernel's 
  `--include-related` follows forward references (`is_relationship: true`) but not reverse refs. 
  For Touchpoint, this means Meeting.touchpoint→Touchpoint is invisible from Touchpoint's side. 
  Subsumed for the Touchpoint case by Option B but underlying gap remains.

- **Bug #20 + #21 — Actor CLI parity + transition API field naming.** Mechanical: Actor CLI 
  missing `transition`, `delete`, `bulk-*`. Transition API expects `to` but docs say `target_state`.

- **Bug #11 + #12 + #13 — observability/docs cleanup.** `/api/queue/stats` returns 404; 
  `mongodb-uri` secret has wrong host; Railway doesn't auto-deploy on push to main.

- **Bug #5 — `fetch-new --help` triple-dash flags + missing `--data` documentation.**

- **Bug #15 — Naive entity collection pluralization (`Company` → `companys`).**

- **Bug #2 — No singular `delete` CLI** (only `bulk-delete`, which is broken per #23).

- **Bug #3 + #4 — `bulk status` lacks counts + `bulk-delete --filter '{}'` silent no-op** (subsumed 
  by Bug #23 + #24 fix).

- **Bug #7 + #8 — Adapter noise + per-user error swallowing** (Google Workspace adapter ergonomics).

- **Bug #19 — Change records sometimes have non-Date timestamp fields** (low-severity observability bug).

==== Operational notes for this session ====

The async runtime had a deploy-failure storm at end-of-previous-session (a bare-import regression 
from the silent-stuck-state PR; fixed in commit `65dddfa`). If you see runtime-async deploy emails 
again, check that one first. The chat runtime is also failing startup with `Error 401: Invalid 
service token` — that's pre-existing, NOT from any recent fork work; it needs Craig to rotate 
the chat-runtime service token. Don't try to fix it yourself; flag it in the session and move on.

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
- Bug #30 sparse propagation audit: walk all entity defs for `unique: true` on nullable fields and add `sparse: true` (kernel reconciler audit) — OR: kernel auto-emits partialFilterExpression when `unique: true` on an Optional-typed field (defensive, prevents future Bug #30s entirely)
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
