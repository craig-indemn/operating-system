# OS Learnings — Running Register

This is the running register of every OS-relevant finding surfaced by customer-system work. Bugs, missing capabilities, design gaps, ergonomics issues, and architectural decisions that need to flow back into the Indemn OS itself.

**The principle:** building the customer system is shipping the OS. Every gap is information the OS needs. This file is where we track that flow.

**How to use this file:**
- **Scan it** at the start of any session that might touch OS internals — see what's queued, what's blocking, what's been resolved.
- **Append to it** when customer-system work surfaces something OS-relevant. Don't bury findings in trace artifacts — surface them here.
- **Update status** when OS work moves a finding from queued → in-progress → fixed.
- **Link back** to source artifacts where the finding was first articulated, and forward to OS-side artifacts (in `../product-vision/` or in the OS repo) when the design discussion or implementation lands there.
- **Don't delete entries** when fixed — mark fixed and leave the trail. The history is valuable.

**Status legend:**
- 🔴 Open — not yet addressed
- 🟡 In-progress — actively being worked
- 🟢 Fixed — fix is in main / deployed
- ⚪ Won't fix / by design — with rationale

**Source-of-truth detail** for each finding lives in the linked artifact. This file is the index. Bugs file (`artifacts/2026-04-24-os-bugs-and-shakeout.md`) carries deeper bug detail; this file aggregates bugs + capability gaps + design questions in one place ranked by what they unblock.

---

## What's queued for the OS — by impact on customer-system

### Critical / blocking the next phase

| Item | Status | Source | OS-side artifact / commit |
|---|---|---|---|
| **Touchpoint forward source pointers (Option B)** — Add `source_entity_type: str` + `source_entity_id: objectid` fields to Touchpoint; Synthesizer populates them on create. Without this, the Intelligence Extractor has no path from Touchpoint to the source Meeting/Email content. Closes the structural information-access asymmetry surfaced by the GR Little trace Apr 24. | 🟢 Fixed | `artifacts/2026-04-24-extractor-pipeline-gap.md`, `artifacts/2026-04-24-extractor-procedure-and-requirements.md` | 2026-04-27: `indemn entity modify Touchpoint --add-field` + `indemn-api` redeploy + Synth skill v3 (`projects/customer-system/skills/touchpoint-synthesizer.md` updated, content_hash `4ddfb844ac84...`). Both new fields visible in auto-generated entity skill; new Touchpoints from the Synth will populate them. |
| **Entity-resolution kernel capability** — given a candidate (domain, name, email, similar-description), return likely existing matches with confidence scores. Associates call before creating. Root fix for Bug #16 (the 446-Company auto-create explosion). Required for reliable hydration at scale. | 🔴 Open | `artifacts/2026-04-24-trace-plan-and-design-notes.md`, memory `project_customer_system_entity_identity.md`, Bug #16 detail | TBD |
| **Bug #29 — Entity-definition replacement doesn't evict old API routes** — `register_domain_entity()` overwrites `ENTITY_REGISTRY` but `register_entity_routes()` calls `app.include_router(router)` which appends rather than replaces. Stale closures keep the old class. Workaround today: redeploy. Fix: in `kernel/api/registration.py`, evict matching prefix routes from `app.router.routes` before include. | 🟢 Fixed | `artifacts/2026-04-24-os-bugs-and-shakeout.md` Bug #29 | 2026-04-27 fork session: merged to main as `83d2494` (feature commit `0bd4e50`). New `_evict_routes_for_prefix(app, prefix)` helper removes routes whose path equals the prefix or starts with `prefix + "/"`; called inside `register_entity_routes` before `app.include_router(router)`. Trailing-slash check guards against prefix-lookalikes (e.g. `/api/companys2` is NOT evicted by `/api/companys`). 7 unit tests (incl. end-to-end TestClient roundtrip proving a re-registered handler wins over the stale one). **Pending: Craig redeploys `indemn-api` to pick up the change.** Live entity-def iteration without restart now works as advertised. |
| **Bug #23 — `bulk-delete` silently drops MongoDB operator filters** (`$in`, `$gte`, `$ne`, `$oid`, `$date`). Only simple equality filters work. Combined with Bug #24 (`bulk status` reports COMPLETED even on 0 matches), users can't tell the operation did nothing. Blocks any non-trivial cleanup at scale. | 🔴 Open | `artifacts/2026-04-24-os-bugs-and-shakeout.md` Bug #23, Bug #24 | TBD |

### High / significant capability or reliability gap

| Item | Status | Source | OS-side artifact / commit |
|---|---|---|---|
| **Bug #16 — Associates auto-create Companies despite skill saying never** — symptom; root is the missing entity-resolution capability above. Will be subsumed by that fix. | 🔴 Open | Bug #16 | TBD |
| **Bug #17 — No meeting-to-company classifier in pipeline** — Touchpoint Synthesizer assumes `meeting.company` is set; `fetch_new` leaves it null. Subsumed by entity-resolution + Option B. | 🔴 Open | Bug #17 | TBD |
| **Bug #22 — Service-token untraceability** — all associates authenticate as Platform Admin via shared service token. Changes collection records `actor_id = Platform Admin` for everything; can't tell which associate made a mutation. Blocks forensics. Fix: per-associate service tokens OR `effective_actor_id` field on change records. | 🔴 Open | Bug #22 | TBD |
| **Bug #9 — Associates pass dicts instead of ObjectId strings → dead letters** — LLM passes `{"company": {"name": "Oneleet"}}` when it should pass `{"company": "<objectid>"}`. Fix: skill prompt enhancement + auto-generated entity skill should teach the pattern unmissably. | 🔴 Open | Bug #9 | TBD |
| **`--include-related` doesn't follow reverse relationships** — kernel's `--include-related` follows forward references (fields where `is_relationship: true`) but not reverse refs. For Touchpoint, this means Meeting.touchpoint→Touchpoint is invisible. Either fix (general — kernel feature) or rename the flag. Subsumed by Option B for the Touchpoint case but the underlying gap remains. | 🔴 Open | `artifacts/2026-04-24-extractor-pipeline-gap.md` | TBD |
| **Cross-invocation tool-cache leak in async harness** — `/large_tool_results/` is shared across agent invocations in the same runtime container. An agent's `grep` matched content from a *different* prior agent's cached results during the GR Little trace. Fix: scope per `message_id` in `harnesses/_base/harness_common/backend.py`. | 🟢 Fixed | `artifacts/2026-04-24-extractor-pipeline-gap.md` (Secondary issues) | 2026-04-27 fork session: merged to main as `ac6d475` (feature commit `4e7e83d`). `_root_dir_for_activity()` helper + `build_backend(activity_id)` + `build_agent(activity_id)` plumb-through + cleanup in main.py finally block. 6 unit tests pass. **Pending: Craig redeploys async runtime to pick up the change.** |
| **Silent workflow stuck-state** — when an agent completes with empty output and no mutating CLI calls, the Temporal workflow doesn't mark the message complete or failed. Message sits in `processing` indefinitely with `last_error: null`. Fix: in `harnesses/async-deepagents/main.py`, inspect agent output post-`ainvoke()`; mark failed if no meaningful output and no state changes. | 🟢 Fixed | `artifacts/2026-04-24-extractor-pipeline-gap.md` (Secondary issues) | 2026-04-27 fork session: merged to main as `67f006c` (feature commit `852eeaa`). New `completion_logic.agent_did_useful_work()` helper detects mutating `indemn` calls / meaningful final content; harness now branches between `queue complete` and `queue fail --reason ...`. 20 unit tests pass. **Pending: Craig redeploys async runtime to pick up the change.** |
| **List endpoint accepts no arbitrary field filters** — `GET /api/{entity}/` only supports `status`, `search`, `limit`, `offset`, `sort`. Blocks: reverse lookups (Meeting where touchpoint=X), duplicate detection refinement, cadence queries. CLI shows it too — `--data` filter doesn't exist on list. Fix: extend list endpoint with safelisted field filters; expose as `--data` on CLI. | 🔴 Open | `artifacts/2026-04-24-extractor-procedure-and-requirements.md` § Capability #2 | TBD |
| **Bug #10 — No backfill / re-trigger mechanism for historical entities** — when a watch is added to a role, only future events fire it. Existing entities are invisible. Cost us significant work in the GR Little trace (we manually created the Touchpoint because the Synth's `Meeting created` watch couldn't refire on an already-ingested meeting). Fix: `indemn <entity> reprocess <id> --role <role_name>` or role-level backfill capability. | 🔴 Open | Bug #10, `artifacts/2026-04-24-extractor-procedure-and-requirements.md` § Capability #6 | TBD |
| **Bug #18 — Synth doesn't update `Meeting.touchpoint` back-reference** — only 5 of 67 meetings got the back-pointer set during Apr 24 backfill. Skill needs to enforce the post-create update OR the relationship needs to flip direction. Subsumed structurally by Option B. | 🔴 Open | Bug #18 | TBD |
| **API returns generic "Internal Server Error" body on 500 — no validation detail, no exception message.** Surfaced again 2026-04-27 during the Alliance trace: `POST /api/meetings/` returns 500 with body `Internal Server Error` for valid-looking input matching the entity schema (`{"title": "...", "date": "2026-02-01T18:02:00Z"}`). Same class as Bug #25 (Company), Bug #26 (Deal). **This is the root issue** making the create-500 family of bugs (#25/#26/Meeting) hard to diagnose — the API should return 400 with field-level validation errors, or at minimum include exception detail in the 500 response body. Likely fix in `kernel/api/registration.py` or `kernel/api/errors.py` (global exception handler). Without this, every associate hitting a create error has no way to self-correct. **Combined with the auto-generated entity skill not teaching JSON shape examples**, this means associates and humans both have to guess the right payload until they hit a working one. | 🟢 Fixed | 2026-04-27 Alliance trace; reinforces Bug #25, Bug #26 | 2026-04-27 fork session: merged to main as `cf5acd8` (feature commit `914fc61`). `kernel/api/errors.py` gains a Pydantic `ValidationError` → 400 handler (returns field-level `errors` array with loc/msg/type per error) + catch-all `Exception` → 500 handler (returns `{error, type, message}` JSON; logs full traceback; bounds message at 4096 chars to prevent runaway responses). Existing typed handlers still take precedence. 10 unit tests pass. **Pending: Craig redeploys `indemn-api` so the production API stops returning "Internal Server Error" plain text.** Once deployed, the next bug (Meeting create 500) becomes self-diagnosable. |
| **Meeting create returns HTTP 500** — `POST /api/meetings/` with valid-shape JSON (matching entity_definitions.Meeting field types) returns 500. Tested with both the CLI (`indemn meeting create --data ...`) and direct curl. Affects the Alliance trace (no historical Meeting entities can be created for Feb 1 / Apr 8 calls without resolving). May be the same root as Bug #25 (Company) and Bug #26 (Deal); or may be Meeting-specific. Cannot self-diagnose without the broader 500-detail fix above. | 🔴 Open | 2026-04-27 Alliance trace | TBD |
| **Auto-generated entity skill needs JSON-shape examples** — surfaced again 2026-04-27 during the Alliance trace. Reinforces `Generated entity skill teaches actual filter syntax` (existing item below) AND extends it: the skill should also emit a working example `--data` JSON payload per command. Otherwise an associate reading `indemn meeting create --data '...'` doesn't know what `'...'` should look like, must look at an existing entity (which requires `list` to return non-empty), and even then doesn't know which fields are auto-populated vs required. Combined with the 500-without-detail issue, this is what makes the create flow unworkable for autonomous associates. | 🟢 Fixed | 2026-04-27 Alliance trace; extends `Generated entity skill teaches actual filter syntax` | 2026-04-27 fork session: merged to main as `b83fa08` (feature commit `ab987c6`). `kernel/skill/generator.py` now renders a working JSON payload between `--data` quotes for both `create` (every required field with type-appropriate placeholder; ObjectId → 24-hex string, datetime → ISO 8601, enum → first allowed value; state field excluded) and `update` (representative subset of writable fields; state field excluded). 18 new unit tests pass (28 total in the file). **Pending: Craig redeploys kernel.** |

### Medium / ergonomics + observability

| Item | Status | Source | OS-side artifact / commit |
|---|---|---|---|
| **Bug #25 — `company create --data` returns HTTP 500** — opaque error blocks programmatic / scripted Company creation. Hit when re-creating Amynta after accidental delete. | 🔴 Open | Bug #25 | TBD |
| **Bug #26 — `deal update --data` returns HTTP 500 when updating company ref** — same pattern as #25; blocks repointing a Deal at a different Company. | 🔴 Open | Bug #26 | TBD |
| **Bug #27 — `created_by` is null on every Company record** — `save_tracked()` should auto-populate `created_by` from `current_actor_id` on insert. Forensic gap on the entity itself. | 🔴 Open | Bug #27 | TBD |
| **Bug #19 — Change records occasionally have non-Date `timestamp` fields** — bulk operations or some code paths write strings. Should always be server-side `datetime.now(UTC)`. | 🔴 Open | Bug #19 | TBD |
| **Bug #20 — Actor CLI inconsistent with auto-generated entity CLIs** — `indemn actor` has `create/list/get/update/add-role/add-auth` but no `transition`, `delete`, `bulk-*`. Documented workflows reference `indemn actor transition <id> --to suspended` which doesn't work. Workaround: curl the API. Also: `indemn actor list --type` filter is silently ignored (Bug #28). | 🔴 Open | Bug #20, Bug #28 | TBD |
| **Bug #21 — Transition API field naming inconsistent: `to` vs `target_state`** — docs reference `target_state`, API expects `to`. CLI's `--to` flag works because it's mapped internally; users curl-ing the API hit the mismatch. Pick one and sync. | 🔴 Open | Bug #21 | TBD |
| **Generated entity skill teaches actual filter syntax** — `indemn skill get <Entity>` lists fields and state transitions but doesn't teach how to filter lists or navigate relationships. Agents improvise (e.g. `--filter` which doesn't exist) and fail. Fix: `kernel/skill/generator.py` should emit concrete CLI recipes once Capability #2 (arbitrary field filters) lands. | 🟢 Fixed | `artifacts/2026-04-24-extractor-procedure-and-requirements.md` § Capability #3 | 2026-04-27 fork session: merged to main as `f4fc121` (feature commit `6af2166`). Skill now teaches `--status`/`--search`/`--limit`/`--offset`/`--sort` recipes, `--depth N --include-related` for forward navigation, ObjectId-as-hex-string warning when relationship fields present, AND fixes Bug #6 (collection-level capabilities like `fetch_new` no longer emit `<id>` and `--auto`). Centralized `COLLECTION_LEVEL_CAPABILITIES` in `kernel/capability/__init__.py`. 18 unit tests pass. **Pending: Craig redeploys kernel to pick up the change.** (Full filter teaching extends when Capability #2 lands; JSON-shape example payloads still pending — see new High-section item.) |
| **Bug #5 — `fetch-new --help` is unhelpful** — triple-dash flags (`---cap`, `---slug`) leak into help output; no documentation of `--data` JSON shape. Internal routing params shouldn't be exposed. | 🔴 Open | Bug #5 | TBD |
| **Bug #6 — Auto-generated entity skill has wrong fetch-new syntax** — skill template emits `indemn meeting fetch-new <id> --auto` but `fetch-new` is collection-level (no `<id>`) and `--auto` doesn't apply. Agents follow wrong instructions. Fix: special-case collection-level capabilities in `kernel/skill/generator.py`. | 🟢 Fixed | Bug #6 | 2026-04-27 fork session: subsumed by merge `f4fc121` (feature commit `6af2166`, same kernel/skill/generator.py rewrite). Collection-level capabilities now render with `--data '{...}'` and no `<id>`/`--auto`. **Pending: Craig redeploys kernel.** |
| **Bug #11 — `/api/queue/stats` returns 404** — observability endpoint missing or registered at a different path. CLI `indemn queue stats` works (uses different path). Document the actual path or alias. | 🔴 Open | Bug #11 | TBD |
| **Bug #12 — AWS Secrets Manager `mongodb-uri` secret has wrong host** — points to `dev-indemn-pl-0.mifra5.mongodb.net` (DNS not-found). Actual host is `dev-indemn.mifra5.mongodb.net`. `mongosh-connect.sh` wrapper fails. Direct connection with corrected URI works. | 🔴 Open | Bug #12 | TBD |
| **Bug #15 — Naive entity collection pluralization** — `Company` → `companys`; `Opportunity` → `opportunitys`. Auto-derivation uses `name.lower() + "s"`. English plurals harder than that. Fix: use `inflect` library OR require explicit `collection_name` in entity defs. Existing collections need migration or doc update. | 🔴 Open | Bug #15 | TBD |
| **Bug #2 — `indemn {entity} delete` (singular) doesn't exist** — only `bulk-delete --filter '{...}'` which is async via Temporal (no synchronous confirmation). Fix: add singular `delete` to entity registration in `kernel/cli/app.py`. | 🔴 Open | Bug #2 | TBD |
| **Bug #3 — `bulk status` output lacks deletion counts** — returns workflow_id + status only; no `records_seen`, `succeeded`, `skipped`, `errored`. To verify a bulk-delete worked, must separately list and count. Fields exist in the workflow state — just need surfacing. | 🔴 Open | Bug #3 | TBD |
| **Bug #4 — `bulk-delete --filter '{}'` silently no-ops** — `{}` should match all (with confirmation) or be rejected with helpful error. Today returns started → completed with 0 deleted, no error. Pair with #23 to make bulk-delete trustworthy. | 🔴 Open | Bug #4 | TBD |
| **Bug #7 — Adapter noisy "fileId" warnings** — Google Workspace adapter logs `WARNING: Failed to export shared doc: Missing required parameter "fileId"` ~50+ times per fetch. Should short-circuit when fileId is empty. | 🔴 Open | Bug #7 | TBD |
| **Bug #8 — Adapter swallows all per-user errors in `fetch()`** — broad `except Exception` masks systemic failures (the Bug #1 root cause was hidden by this). Fix: track success rate; raise if all/most users fail with same error class. | 🔴 Open | Bug #8 | TBD |
| **Bug #13 — Railway doesn't auto-deploy on `git push origin main`** — `docs/guides/development.md` describes auto-deploy; reality is `railway up --service <name>` is required. Decide direction (configure auto-deploy or update docs) and align. | 🔴 Open | Bug #13 | TBD |

### Open design questions (need discussion before implementation)

| Item | Status | Source |
|---|---|---|
| **Opportunity vs Problem entity** — should the unmapped-pain case (a problem we noticed but no clear AssociateType fit) get its own entity, or should Opportunity loosen `mapped_associate` to nullable with state `unmapped → mapped → validated → proposed → addressed → resolved`? | 🔴 Open | `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` § Topic 2 |
| **Document-as-artifact pattern for emails** — Proposal→Document is designed. But where does a *drafted* email live? Email entity with status `drafting`? Document with `mime_type: message/rfc822`? Hybrid? | 🔴 Open | memory `project_customer_system_artifact_entity_pattern.md`; `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` § Topic 3 |
| **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle's Apr 24 ask) — Stage entity gets sub-stages, OR a separate `qualification_state` column, OR Stage records gain a `parent_stage` field for hierarchy. | 🔴 Open | `artifacts/2026-04-24-kyle-sync-recap.md`; full transcript at `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt` |
| **Origin / referrer tracking** (Pat Klene → GR Little example, Kyle's Apr 24 ask) — field on Deal (`source_referrer: Contact_id`)? New Introduction entity? Extending Conference into general "Introduction"? | 🔴 Open | `artifacts/2026-04-24-kyle-sync-recap.md`; full transcript |
| **Playbook hydrates from historical extractions** (long-term) — once the pipeline is reliable and we have many Touchpoints across stages, the Playbook records should refine from observed patterns. Mechanism for that refinement (manual? scheduled associate? human-in-the-loop?). | 🔴 Open | `artifacts/2026-04-24-playbook-entity-vision.md` |

---

## Fixed — historical record

| Item | Status | Fix | Date |
|---|---|---|---|
| **Bug #1** — Google Meet adapter rejected date-only `since` filter (Meet API requires full RFC3339; broad `except` swallowed the per-user error so `fetched: 0` for everyone). Fix: `_normalize_rfc3339()` helper in `kernel/integration/adapters/google_workspace.py`. | 🟢 Fixed | Commit `8afda9d` | 2026-04-24 |
| **Bug #14** — CLI POST/PUT timeout was 60s — too short for large `fetch-new` calls. Fix: bumped to 600s default, configurable via `INDEMN_CLI_TIMEOUT`. | 🟢 Fixed | Commit `f0dfe89` | 2026-04-24 |
| **Bug #10 (one-time)** — 21 Apr 20-21 test meetings never became Touchpoints because Synth role/watch was added after they were created (root cause = #10 — no backfill mechanism). Resolution for the data: `indemn meeting bulk-delete` cleared them. The underlying capability gap remains open above. | 🟢 Resolved (data) | Manual cleanup | 2026-04-24 |
| **Pre-Apr 24 infrastructure fixes:** Queue processor `WorkflowAlreadyStartedError` removed from temporalio SDK (replaced with `RPCError` + `RPCStatusCode.ALREADY_EXISTS`); runtime service token regenerated and propagated; "Interaction" renamed to "Touchpoint" (kernel collision); 6 entity definitions had missing `is_state_field: true` on status fields; async harness skills loaded via deepagents progressive disclosure (not concatenated into system prompt); async harness heartbeat during `ainvoke()` (Temporal was cancelling long-running activities); model upgraded to `gemini-2.5-flash` on enterprise Vertex project. | 🟢 Fixed | Multiple commits | 2026-04-22/23 |

---

## Notes on prioritization

**The top-4 to make the autonomous Extractor work** (per `extractor-procedure-and-requirements.md`):
1. Touchpoint `source_entity_*` fields + Synth populates them — **Option B**
2. Workflow detects empty-output agent as failure
3. Per-invocation tool-result isolation
4. Generated entity skill teaches filter syntax

These four together take the Extractor from "structurally broken" to "works reliably on the happy path." Everything below them is quality-of-life or scale reliability.

**Top blockers for running the pipeline at scale:**
- Entity-resolution capability (root fix for #16 / 446-Company)
- Option B (extraction unblocks)
- Bug #29 (entity-def iteration unblocks)

**Top observability gaps:**
- Bug #22 (per-associate service tokens for forensics)
- Bug #27 (`created_by` on entities)
- Bug #11 (`/api/queue/stats` endpoint)

**The acceleration mechanic is real here:** each fix above makes the next thing 2-3x faster. Option B done means the Extractor works. Extractor working means we can backfill all team meetings and emails. Backfill done means we hydrate Alliance + Arches + every prospect. Hydrated graph means the Artifact Generator has real data. Artifact Generator means dashboards have real data. Dashboards mean the team adopts. Adoption means we discover the next round of OS gaps.

---

## How findings get added here

When customer-system work surfaces something OS-relevant:

1. **Add it to `artifacts/2026-04-24-os-bugs-and-shakeout.md`** if it's a bug — that file holds the deep detail (symptom, root cause, proposed fix).
2. **Add it to `artifacts/2026-04-24-extractor-procedure-and-requirements.md`** if it's a *capability gap* — a missing OS feature, not just a bug.
3. **Add it to `INDEX.md` Open Questions** if it's a design question that needs discussion.
4. **Add a row to this file** in the appropriate severity section, with a 1-2 sentence summary and links to (1)/(2)/(3) above.
5. **When status changes** (in-progress, fixed), update this row. Don't delete it.
6. **When the OS-side write-up happens** (in `../product-vision/` or directly in `/Users/home/Repositories/indemn-os/docs/`), link it in the "OS-side artifact / commit" column.

This file is the queue. The artifacts hold the depth. The OS docs hold the resolved state.
