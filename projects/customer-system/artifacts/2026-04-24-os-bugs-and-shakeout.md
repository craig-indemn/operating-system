---
ask: "Running list of OS bugs, CLI UX gaps, and other shakeout findings discovered while dogfooding the customer system. Add to this over time."
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
status: living-document
---

# OS Bugs & Shakeout Findings

Running list of issues found while using the Indemn OS to build the customer system. This is the first real dogfooding of the CLI-as-interface — every gap matters.

**Principle:** flag loudly, fix when we encounter them again or when they block. Don't route around bugs — that's how systems rot.

**Status legend:**
- 🔴 Open — not yet fixed
- 🟡 In progress / partial
- 🟢 Fixed and deployed
- ⚪ Won't fix / by design (with rationale)

---

## Bug #1 — Google Meet adapter rejected date-only `since` filter 🟢

**Discovered:** 2026-04-24
**Severity:** High (broke `indemn meeting fetch-new` for any user passing short date form)
**Location:** `kernel/integration/adapters/google_workspace.py`

### Symptom
`indemn meeting fetch-new --data '{"since": "2026-04-22"}'` returned `fetched: 0` even though 73 conference records existed in Google Meet for the team.

### Root cause
The adapter constructed a Meet API filter as `end_time>="2026-04-22"` with a date-only string. Meet API requires full RFC3339 datetime and returned HTTP 400 with `"Invalid filter was provided"`. The adapter caught the per-user exception in a broad `except` and continued, so every user was silently skipped.

### Fix
Added `_normalize_rfc3339()` helper that accepts `"YYYY-MM-DD"` or full RFC3339 and normalizes to RFC3339 with `Z` suffix. Applied at the top of `fetch()`.

```python
def _normalize_rfc3339(s: str) -> str:
    if not s:
        return s
    if "T" in s:
        return s if (s.endswith("Z") or "+" in s[10:]) else s + "Z"
    return s + "T00:00:00Z"
```

Commit: `8afda9d fix(google_workspace): normalize 'since' to RFC3339 before Meet API filter`

### Related gap (open)
The per-user `except Exception` in `fetch()` is too broad — swallowed a systemic filter error. Should distinguish "this user has no Meet history" from "API rejected my filter" and raise the second case. Tracked as Bug #8.

---

## Bug #2 — `indemn {entity} delete` (singular) doesn't exist 🔴

**Severity:** Medium (UX friction)
**Location:** Auto-generated CLI command registration

### Symptom
```
$ indemn meeting delete <id>
Error: No such command 'delete'. Did you mean 'bulk-delete'?
```

### Root cause
The auto-generated CLI for each entity registers: `list`, `get`, `create`, `update`, `transition`, `fetch-new` (where applicable), and bulk variants. No singular `delete`.

### Impact
To delete one entity you must use `bulk-delete --filter '{"_id": "<objectid>"}' --no-dry-run` which is async via Temporal (returns workflow_id, no confirmation of what was deleted).

### Proposed fix
Add a singular `delete` command in `kernel/cli/app.py` entity registration — synchronous, confirms deletion. Emits the same deletion event as bulk-delete.

---

## Bug #3 — `bulk status` output lacks deletion counts 🔴

**Severity:** Low (observability gap)
**Location:** `kernel/cli/` bulk command output

### Symptom
```
$ indemn bulk status bulk-xxx
{"workflow_id": "bulk-xxx", "status": "COMPLETED", "start_time": "..."}
```

No information on how many entities were processed, deleted, skipped, or errored. To verify a bulk-delete worked you have to separately `list` the entity and count.

### Proposed fix
`bulk status` should include: `records_seen`, `succeeded`, `skipped`, `errored`, `errors[]` (truncated). These fields already exist in the workflow state per the bulk-operations design — just need to be surfaced by the CLI.

---

## Bug #4 — `bulk-delete --filter '{}'` silently no-ops 🔴

**Severity:** Medium (safety issue masquerading as feature)
**Location:** `kernel/cli/` bulk command routing OR `kernel/temporal/` bulk workflow

### Symptom
```
$ indemn meeting bulk-delete --filter '{}' --no-dry-run
{"workflow_id": "bulk-xxx", "status": "started"}
# Workflow completes, 0 meetings deleted, no error
```

Yet `indemn meeting bulk-delete --filter '{"source": "google_meet"}' --no-dry-run` deleted 20 records.

### Likely cause
`{}` probably gets treated as "match nothing" instead of "match all" somewhere — OR gets rejected by validation but the CLI doesn't surface the error.

### Expected behavior
Either: `{}` matches all and confirms with a big warning, OR `{}` is explicitly rejected with "use a specific filter; `--all` is a separate flag."

### Proposed fix
Require an explicit `--all` flag to delete everything. Reject `{}` with a helpful error. Never silently do nothing when the user asked to delete.

---

## Bug #5 — `indemn meeting fetch-new --help` is unhelpful 🔴

**Severity:** Medium (discoverability)
**Location:** `kernel/cli/` fetch-new command definition

### Symptom
```
$ indemn meeting fetch-new --help
Usage: indemn meeting fetch-new [OPTIONS]
Invoke a collection-level capability (e.g., fetch-new).
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --data         TEXT                                                          │
│ ---cap         TEXT  [default: fetch_new]                                    │
│ ---slug        TEXT  [default: meeting]                                      │
│ --help               Show this message and exit.                             │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Issues
1. `--data` TEXT — no documentation of what JSON shape it accepts. User has no idea `since`, `user_emails`, `limit` are valid keys.
2. `---cap` and `---slug` have **triple dashes** — unusable and clearly wrong (Typer/argparse render bug?).
3. `---cap` and `---slug` shouldn't be exposed to users at all — they're internal routing params.

### Proposed fix
- Generate per-capability CLI docs from adapter docstring (`adapter.fetch.__doc__`)
- Hide internal params (`---cap`, `---slug`) from help
- Add examples per entity type: `indemn meeting fetch-new --data '{"since": "2026-04-22"}'`

---

## Bug #6 — Auto-generated entity skill has wrong fetch-new syntax 🔴

**Severity:** Medium (associates will follow wrong instructions)
**Location:** `kernel/skill/generator.py`

### Symptom
`indemn skill get Meeting` returns a skill doc with:
```
| `indemn meeting fetch-new <id> --auto` | fetch_new |
```

### Issues
1. `fetch-new` is a collection-level capability — no `<id>` argument
2. `--auto` is for instance-level capabilities with rule/LLM fallback — does not apply
3. Missing the `--data` shape that the command actually accepts

### Impact
AI associates reading the skill will try `indemn meeting fetch-new <random-id> --auto`, get a CLI error, retry wrong.

### Proposed fix
Update the skill generator to special-case collection-level capabilities. For `fetch-new`:
```
| `indemn meeting fetch-new --data '{"since": "ISO8601"}'` | Ingest new meetings from the integration |
```

---

## Bug #7 — Adapter noisy warnings: "Missing required parameter 'fileId'" 🔴

**Severity:** Low (log noise, but obscures real errors)
**Location:** `kernel/integration/adapters/google_workspace.py` — `_build_meeting` / Drive export

### Symptom
During `fetch_new`, dozens of lines of:
```
WARNING: Failed to export shared doc: Missing required parameter "fileId"
```
For a single call fetching ~40 meetings, we get ~50+ such warnings. Observed in direct adapter test.

### Likely cause
The adapter tries to export Drive docs for meetings even when there's no file ID (e.g., meetings without recordings or transcripts). Should short-circuit instead of calling export with empty ID.

### Proposed fix
Check `fileId` is truthy before calling the Drive export API.

---

## Bug #8 — Adapter swallows all per-user errors in fetch() 🔴

**Severity:** Medium (masks systemic failures)
**Location:** `kernel/integration/adapters/google_workspace.py:155-158`

### Code
```python
for email in real_users:
    try:
        conferences = await self._list_user_conferences(email, since)
        ...
    except Exception as e:
        logger.warning("Skipping %s: %s", email, e)
        continue
```

### Issue
When EVERY user fails with the same systemic error (like Bug #1), the adapter returns 0 results silently. The caller has no way to know something is wrong.

### Proposed fix
Track whether any user succeeded. If ALL users failed with the same error class, raise it upward. Or: if more than 50% of users fail, raise with an aggregated error message.

---

## Bug #9 — Associates pass dicts instead of ObjectId strings → dead letters 🔴

**Severity:** High (breaks extraction pipeline reliably)
**Location:** Associate skills (Email Classifier, Touchpoint Synthesizer, Intelligence Extractor)

### Symptom
~10 dead-letter messages in queue, all with errors like:
```
Error 400: 1 validation error for Email
company
  Input should be an instance of ObjectId [type=is_instance_of, input_value={'name': 'Oneleet'}, input_type=dict]
```

The LLM agent is doing:
```
indemn email update <id> --data '{"company": {"name": "Oneleet"}}'
```
When it should be doing:
```
# first: resolve or create the Company → get its ID
# then: indemn email update <id> --data '{"company": "<objectid-string>"}'
```

### Impact
- Email Classifier: 3 dead letters
- Touchpoint Synthesizer: 6 dead letters
- Happens repeatedly — skill prompts don't clearly prevent it

### Proposed fix
Two layers:
1. **Skill-prompt fix** (easy): Explicit instruction in each associate's skill about passing IDs, not dicts. Include a worked example of "look up Company first, then use its `_id`."
2. **Auto-generated entity skill improvement**: When a field has `is_relationship: true`, the skill doc should make it unmissable that the value must be an `objectid` string, not the related entity. Currently the skill just says `objectid | → Company` which isn't obviously rejecting dict input.

---

## Bug #10 — Old meetings (Apr 20-21 test batch) never became Touchpoints 🟢

**Severity:** Low — specific to a one-time data state
**Location:** N/A (data / timing issue)

### Context
21 meetings ingested Apr 21 during the roadmap session. Of those, only 2 later got Touchpoints + Company links. The other 19 never had the Touchpoint Synthesizer run against them.

### Likely cause
Meeting Synthesizer role/watch was configured AFTER those meetings were created, OR the synthesizer failed silently on the initial test run (the 6 dead letters that accumulated may be related).

### Resolution
Cleared — deleted all 21 via `indemn meeting bulk-delete`. Will re-fetch fresh once Bug #1 fix deploys.

### Long-term question
When a watch is newly added to a role, should there be a "backfill" mechanism to fire it against existing entities? Today: only future events fire. For a system that evolves (associates added over time), some replay capability would be useful.

---

## Bug #11 — `/api/queue/stats` endpoint returns 404 🔴

**Severity:** Low (observability)
**Location:** `kernel/api/queue_routes.py`

### Symptom
```
curl .../api/queue/stats → {"detail": "Not Found"}
```

But `indemn queue stats` works (so the CLI uses a different path, or the endpoint is registered under a different URL).

### Proposed fix
Document the actual queue-stats endpoint. Or register `/api/queue/stats` as an alias. Make CLI and API-direct paths consistent.

---

## Bug #12 — AWS Secrets Manager `mongodb-uri` secret points to wrong host 🔴

**Severity:** Low (documented workaround exists)
**Location:** `indemn/dev/shared/mongodb-uri`

### Symptom
Secret contains `dev-indemn-pl-0.mifra5.mongodb.net` which returns DNS not-found. Actual working host is `dev-indemn.mifra5.mongodb.net`.

Noted in handoff / INDEX / ops guide. `mongosh-connect.sh` wrapper uses the broken secret and fails. Direct connection with correct URI works.

### Proposed fix
Update the secret value OR create a new secret with the correct URI and point `mongosh-connect.sh` at it.

---

## Bug #13 — Railway doesn't auto-deploy on `git push origin main` 🔴

**Discovered:** 2026-04-24
**Severity:** Medium (ops friction — "what does pushing to main even do?")
**Location:** Railway project config

### Symptom
Pushed commit `8afda9d` to `indemn-os/main`. Latest Railway deployment for `indemn-api` at the time was from the prior day (01:48 UTC). No new deployment kicked off from the push.

Per `docs/guides/development.md`:
> Push to the main branch triggers the pipeline: lint, unit tests, integration tests, build the image, deploy via rolling update.

This did not happen. Had to run `railway up --service indemn-api` manually.

### Likely causes
- GitHub Actions CI may not be configured at all (no `.github/workflows` file)
- Railway project's GitHub integration may not have "Deploy on Push" enabled for main
- The documented flow in `development.md` may describe an aspirational rather than actual setup

### Proposed fix
Decide whether we WANT auto-deploy on main:
- Yes: configure Railway's GitHub integration to deploy `main` for all services, OR set up a GitHub Action that runs `railway up` for the changed service
- No: update `docs/guides/development.md` to reflect reality (`railway up --service <name>` is the deploy path)

Either way the docs and behavior should match. Today they don't.

---

## Bug #15 — Entity collection names use naive `+s` pluralization 🔴

**Discovered:** 2026-04-24
**Severity:** Low (but confusing — silent mismatch)
**Location:** `kernel/entity/factory.py` or wherever `collection_name` is auto-derived

### Symptom
The `Company` entity uses MongoDB collection `companys` (missing "ie" plural). Anyone querying `db.companies` gets zero results; the data is in `db.companys`.

Presumably this extends: `Assessment` → `assessmentss`? `Policy` → `policys`? (Not verified.)

### Root cause
Auto-derivation of `collection_name` from `entity_name` probably uses `name.lower() + "s"`. English plurals are harder than that.

### Proposed fix
Two options:
1. Use the `inflect` library for proper pluralization
2. Require `collection_name` to be set explicitly in entity definitions, document it, fail loudly if missing

Either way, our existing `companys` collection needs to be handled — rename via migration, or just accept the name and update docs.

---

## Bug #16 — Associates auto-create Company records despite "never create" skill instruction 🟡

**Discovered:** 2026-04-24
**Severity:** High (corrupts the knowledge graph)
**Location:** Touchpoint Synthesizer skill + possibly Email Classifier skill + LLM execution

### Symptom
Company count went from ~88 (set by Craig in prior session) to **446** during today's Touchpoint Synthesizer run on 67 meetings.

Massive duplication:
- "Indemn" + "Indemn AI" + "Indemn, Inc." + "Indemn AI Inc." — four records for Indemn itself
- "Fox Quilt" (old, space) + "Foxquilt" (newly auto-created today)
- Many others

### Skill instruction (explicit)
Both the Email Classifier and Touchpoint Synthesizer skills say:
> "Companies are NEVER auto-created. Adding a Company is a business decision (is this a prospect? a vendor? a partner?). That requires human judgment. If the classifier can't match to an existing Company, it transitions to `needs_review`."

Clearly not being followed.

### Root cause (hypotheses — diagnose first)
1. Skill text isn't strong enough — LLM still creates when it can't match
2. The LLM isn't being given a list of existing Companies to match against; faced with no match, it creates
3. Company matching criteria unclear — LLM tries exact-string match, fails, creates new
4. No domain/email field on Company to support email-domain matching

### Proposed fix (after diagnosis)
- Add `domain` (or `email_domains: list`) field to Company for deterministic matching
- Move company matching OUT of the LLM skill and INTO a deterministic `auto_link` capability (email domain → Company.domain); LLM only invoked for ambiguous cases
- Enforce "no auto-create" at the ENTITY level — permission denies `create` for Company on the synthesizer role
- Alternatively: add a Company.created_by_associate boolean and report/flag any such records

### Downstream damage to clean up
- 446 Company records need to be merged back down to ~90
- Touchpoints and other entities referencing the bad companies need re-linking
- Not reversible via simple undo — will need a careful migration

---

## Bug #17 — No meeting-to-company classifier 🟡

**Discovered:** 2026-04-24
**Severity:** High (blocks the whole pipeline for customer-facing meetings)
**Location:** Pipeline wiring — missing role + watch

### Symptom
`indemn meeting fetch-new` creates Meeting entities with `company: null`. The Touchpoint Synthesizer skill says "company: from the Meeting's company" — reads null, either skips or hallucinates.

### Root cause
Emails have an Email Classifier (watches `Email created`, sets Company via sender domain). Meetings have no equivalent. The Touchpoint Synthesizer watches `Meeting created` but its job is timeline-building, not classification.

### Proposed fix
Either:
1. **Dedicated Meeting Classifier associate** — watches `Meeting created`, sets `meeting.company` by participant email domain match (deterministic), then the Touchpoint Synthesizer reads a populated `company` field.
2. **Split the Touchpoint Synthesizer** — first it classifies (sets company), then it builds the Touchpoint.
3. **Use `auto_link` capability** — turns the classification into a kernel-level operation that any entity type can activate, not a bespoke associate per entity type.

Option 3 is the most OS-native — it follows the `--auto` pattern and moves matching out of the LLM's hands.

---

## Bug #18 — Synthesizer doesn't update `Meeting.touchpoint` back-reference 🔴

**Discovered:** 2026-04-24
**Severity:** Medium (breaks graph navigation)
**Location:** Touchpoint Synthesizer skill

### Symptom
Out of 67 meetings today, only 5 have `meeting.touchpoint` field set. The other ~40 that DID get touchpoints created don't have the back-reference updated.

### Proposed fix
Add explicit step in the synth skill: "After creating the Touchpoint, `indemn meeting update <id> --data '{\"touchpoint\": \"<tp_id>\"}'`." OR change the relationship: have `Touchpoint.meeting` instead of `Meeting.touchpoint` so the FK is set on the child (synth is already creating the child).

The existing design has sources point TO Touchpoint (`Email.interaction`, `Meeting.touchpoint`), which is elegant for extensibility. But it means the child-creator (synth) has to update the parent — which the LLM sometimes forgets. Either enforce via post-create hook or flip the direction.

---

## Bug #19 — Change records occasionally have non-Date `timestamp` fields 🔴

**Discovered:** 2026-04-24
**Severity:** Low (observability nuisance)
**Location:** `kernel/changes/collection.py` writes

### Symptom
Some `changes` records have `timestamp` as something other than a BSON Date (the `toISOString()` call fails on them in mongosh aggregations).

### Likely cause
Bulk operations or certain code paths write `timestamp` as a string or other type. Should always be a datetime.

### Proposed fix
Validate on write — `timestamp` must be `datetime.now(UTC)` produced server-side. Fix any path writing strings.

---

## Bug #20 — Actor CLI inconsistent with auto-generated entity CLIs 🔴

**Discovered:** 2026-04-24
**Severity:** Medium (breaks documented workflow, blocks suspend operation)
**Location:** `kernel/cli/` (Actor is a kernel entity with custom CLI)

### Symptom
`indemn actor` has subcommands: `create`, `list`, `get`, `update`, `add-role`, `add-auth`. **Missing:** `transition`, `delete`, `bulk-*`.

But `adding-associates.md` documentation says:
```bash
indemn actor transition <actor_id> --to suspended
```

Running that: `No such command 'transition'.` Tried `indemn actor update <id> --data '{"status": "suspended"}'` instead — API rejects: `"Cannot set 'status' via update. Use POST /actors/{id}/transition instead."`

So to suspend an actor via CLI: impossible directly. Workaround: curl the API endpoint.

### Additional inconsistency
`indemn actor list --type associate` does not filter — returns all 23 actors regardless of `--type` value. Other entities use `--data '{"type": "..."}'` JSON filter format.

### Proposed fix
- Add `transition` subcommand to Actor CLI (and to all kernel entities' custom CLIs)
- Make `--type` filter actually work for `actor list`
- Unify: either kernel entities use the same auto-generated CLI pattern as domain entities, OR the custom CLI for kernel entities explicitly implements all the standard operations

---

## Bug #21 — Transition API field naming inconsistent: `to` vs `target_state` 🔴

**Discovered:** 2026-04-24
**Severity:** Low (UX friction, doc mismatch)
**Location:** `kernel/api/registration.py` transition endpoint + docs

### Symptom
Docs (`adding-entities.md`, `CLAUDE.md`) show:
```bash
curl -X POST .../transition -d '{"target_state": "active", "reason": "..."}'
```

Actual API expects:
```bash
-d '{"to": "active", "reason": "..."}'
```

Sending `target_state` returns HTTP 400: `{"detail": "'to' state is required"}`.

### Proposed fix
Pick one and sync:
- Either: rename API param to `target_state` (more explicit)
- Or: update all docs to use `to` (matches CLI's `--to` flag)

The CLI's `--to` flag works because it's mapped internally; the docs leading users to curl directly get the mismatch.

---

## Bug #22 — Cannot tell which associate acted when multiple share the service token 🟢

**Discovered:** 2026-04-24
**Severity:** High (blocks all forensics on associate misbehavior)
**Location:** Auth system — service token binding to `Platform Admin` actor

### Symptom
All 3 pipeline associates (Email Classifier, Touchpoint Synthesizer, Intelligence Extractor) plus the OS Assistant authenticate as `actor_id = 69e23d586a448759a34d3824` (Platform Admin) via the runtime service token. When ANY of them makes a CLI call that mutates an entity, the changes collection records `actor_id = Platform Admin` — indistinguishable from any other associate using the same token.

Today this blocked us from identifying which associate created the 299 duplicate Company records on Apr 23.

### Proposed fix
- Per-associate service token (each Actor gets its own opaque token via `add-auth`)
- OR: add a second field to change records — `effective_actor_id` = the actor whose work is being performed, separate from `session_actor_id` = the authenticated identity
- OR: capture `runtime_id + session_id` in change records when the action originated from a harness

Without this, the ledger cannot answer "which associate did this" — which is the question we need most often.

### Resolution (2026-04-27) — option B (effective_actor_id)
Chose the `effective_actor_id` field approach. Per-associate tokens are architecturally cleaner long-term but a much bigger lift (provisioning + AWS Secrets per associate + rotation + migration); they solve a security-isolation problem we don't have yet.

The mechanism mirrors the existing `causation_message_id` propagation chain:
1. Harness sets `INDEMN_EFFECTIVE_ACTOR_ID = <associate_id>` env var on activity start (`harnesses/async-deepagents/main.py`).
2. Harness CLI wrapper forwards the env var to subprocess (`harnesses/_base/harness_common/cli.py`).
3. CLI client adds `X-Effective-Actor-Id` header from env (`indemn_os/src/indemn_os/client.py`).
4. Auth middleware reads header, validates the asserted actor exists + is type=associate, sets contextvar (`kernel/auth/middleware.py`).
5. `save_tracked` reads contextvar, passes to `write_change_record` (`kernel/entity/save.py`).
6. `ChangeRecord` schema gains `effective_actor_id: Optional[str]` plus a compound index `(org_id, effective_actor_id, timestamp)` for cheap per-associate forensics queries.
7. Trace endpoint surfaces both `actor_id` and `effective_actor_id` so "which associate did this" is queryable through the standard CLI/UI.

**Verified live:** posted a Company create with `X-Effective-Actor-Id: <Email Classifier>` set; `/api/trace/entity/Company/<id>` returned both `actor_id=<Platform Admin>` and `effective_actor_id=<Email Classifier>`. The 446-Company explosion would now be answerable to "which associate" rather than "Platform Admin did everything." Going forward every harness-driven mutation carries the associate identity.

10 unit tests in `tests/unit/test_effective_actor_id.py` pin the contextvar lifecycle, ChangeRecord schema, CLI client header passthrough, and harness CLI wrapper subprocess env propagation. Full 226-test suite green.

### Linked OS work
- Branch: `bugfix/effective-actor-id` (feature commit `dae5bf2`, merged `e9d45e8`)
- Trace serializer: `056cba2`
- Deployed: `railway up --service indemn-api` + `railway up --service indemn-runtime-async` 2026-04-27

---

## Bug #23 — `bulk-delete` silently drops MongoDB operator filters 🔴

**Discovered:** 2026-04-24
**Severity:** **Critical** (makes bulk operations nearly unusable for anything non-trivial)
**Location:** `kernel/temporal/` bulk workflow OR `kernel/api/bulk.py` filter parsing OR `kernel/scoping/org_scoped.py`

### Symptom
Only simple `{field: value}` equality filters work with `bulk-delete`. ANY filter using MongoDB operators (`$in`, `$gte`, `$lte`, `$ne`, `$gt`, `$lt`, `$oid`, `$date`, etc.) silently matches zero records. The workflow reports `started` then `COMPLETED` with no indication it did nothing.

### Working (tested today)
- `--filter '{"name": "Y-Risk"}'` — deleted all Y-Risk records
- `--filter '{"source": "google_meet"}'` — deleted test meetings
- `--filter '{"type": "meeting"}'` — deleted all meeting-type touchpoints

### NOT working (all silently no-op'd)
- `--filter '{"created_at": {"$gte": "2026-04-23T00:00:00Z"}}'`
- `--filter '{"created_at": {"$gte": {"$date": "2026-04-23T00:00:00Z"}}}'`
- `--filter '{"_id": {"$gte": {"$oid": "69e5000000000000000000"}}}'`
- `--filter '{"_id": {"$in": [{"$oid": "..."}, {"$oid": "..."}, ...]}}'` (300+ IDs)
- `--filter '{"_id": {"$gte": ..., "$ne": ...}}'` (compound)

### Impact
- Cannot delete a specific list of entities by ID
- Cannot delete by date range
- Cannot combine filters
- Had to resort to one-at-a-time deletion by exact name match to clean up 446 Company dupes
- Got 446 → 313 (gave up at 313; half-done)

### Combines badly with Bug #3
Since `bulk status` returns no record counts, you can't even tell your delete did nothing except by manually counting before/after.

### Proposed fix (after diagnosis, hypotheses only)
- Ensure the JSON filter passes through to Motor/PyMongo without Pydantic rejecting `$`-prefixed keys
- If extended-JSON types (`$oid`, `$date`) are stripped, deserialize them explicitly
- Add a validation step that REJECTS filters matching zero documents as a config error OR returns `records_affected: 0` in status so users know

---

## Bug #24 — `bulk status` reports `COMPLETED` even when nothing was deleted 🔴

**Discovered:** 2026-04-24
**Severity:** Medium (user has no way to know their operation did nothing)
**Location:** `kernel/temporal/workflows.py::BulkExecuteWorkflow`

### Symptom
Workflow starts with no records matching filter. Workflow completes with `status: COMPLETED` immediately. No error, no indication that the filter matched nothing. Compounds Bug #23.

### Proposed fix
Return `{status: "completed_no_match"}` OR include `records_matched: 0` in the status response so the user can tell.

---

## Bug #25 — `company create --data` returns HTTP 500 Internal Server Error 🟢

**Discovered:** 2026-04-24
**Severity:** Medium (blocked re-creating Amynta company after accidental delete)
**Location:** `kernel/api/registration.py` entity create handler OR entity validation

### Symptom
```bash
$ indemn company create --data '{"name":"Amynta (Guardsman Home Warranty)","type":"Other"}'
# → HTTP 500 Internal Server Error
# No response body, no hint at cause
```

### Impact
Blocks any programmatic/scripted creation of Company records. Error opaque — user has no information to correct.

### Proposed fix
- Return validated error with specific field failure
- Log the actual exception to surface the root cause
- Almost certainly a validation or type-coercion bug given other entities create fine

### Resolution (2026-04-27)
**Same root cause as Bug #30** — Company entity has a unique index on a nullable field (e.g. `domain`). MongoDB's unique index treats explicit null as a value, so the second Company without that field collided. Resolved by the index reconciliation + sparse→partialFilterExpression work in Bug #30. After the kernel fix deployed, `indemn company create --data '{"name":"Test"}'` succeeds for any number of companies that share a null on the previously-blocking field.

---

## Bug #26 — `deal update --data` returns HTTP 500 when updating company ref 🔴

**Discovered:** 2026-04-24
**Severity:** Medium (can't re-point a Deal to a different Company)
**Location:** `kernel/api/registration.py` update handler

### Symptom
```bash
$ indemn deal update <deal_id> --data '{"company":"<new_objectid>"}'
# → HTTP 500 Internal Server Error
```

### Impact
Can't repair broken entity relationships. If cleanup requires moving a Deal's company pointer to a clean record, this is blocked.

### Proposed fix
- Same as #25 — surface the actual error
- Likely related: the company field expects ObjectId; if the string form isn't being coerced, it crashes instead of validating

---

## Bug #27 — `created_by` is null on every Company record 🔴

**Discovered:** 2026-04-24
**Severity:** Medium (audit trail gap on the Company entity itself)
**Location:** `kernel/entity/save.py` — `created_by` should capture `current_actor_id` on insert

### Symptom
All 446 Company records in the DB have `created_by: null` (verified directly). The changes collection has the actor_id (Platform Admin for 444, Kyle for 2), but the entity document itself is missing the creator.

### Impact
When looking at a Company record directly, you cannot tell who created it without joining to the changes collection. Makes forensic queries harder than they should be.

### Proposed fix
In `save_tracked()` on insert, set `entity.created_by = {"actor_id": current_actor_id, "actor_type": current_actor_type}` automatically.

---

## Bug #28 — Auto-generated `actor list` command does not filter by `--type` 🔴

**Discovered:** 2026-04-24
**Severity:** Low (ignored flag is worse than no flag)
**Location:** `kernel/cli/` actor list command

### Symptom
`indemn actor list --type associate` returns ALL 23 actors regardless of `--type` value. The flag exists in `--help` but is silently ignored.

### Proposed fix
Implement the filter OR remove the flag from help.

---

## Bug #29 — Entity definition replacement doesn't evict old API routes 🔴

**Discovered:** 2026-04-24
**Severity:** **High** (makes live entity-def replacement impossible without a restart, defeats a core self-evidence promise of the OS)
**Location:** `kernel/db.py::register_domain_entity()` + `kernel/api/registration.py::register_entity_routes()`

### Symptom
Sequence that fails:
1. `db.entity_definitions.deleteOne({name: "Playbook"})` in Mongo directly (or via `DELETE /api/entitydefinitions/Playbook`)
2. `indemn entity create Playbook --fields '{... completely different shape ...}'` (CLI hits `POST /api/entitydefinitions` which inserts the new def and calls `register_domain_entity`)
3. Response body shows the new def correctly stored and registered in `ENTITY_REGISTRY`
4. `POST /api/playbooks/` with data matching the new schema → rejected with an enum-validation error that references the OLD field's enum values (`"stage must be one of ['draft', 'active', 'archived']"`), even though the new `stage` field is a relationship with no enum_values

### Root cause
`register_domain_entity()` does:
```python
ENTITY_REGISTRY[defn.name] = dynamic_cls     # overwrites
...
register_entity_routes(app, defn.name, dynamic_cls)
```

`register_entity_routes()` ends with `app.include_router(router)`. FastAPI's `include_router` **appends** routes; it does not replace. So:
- Every `@router.post("/")` closure built from the OLD `entity_cls` is still attached to the app
- New routes from the NEW class are appended
- When a request comes in, FastAPI matches on the FIRST matching route → always the old one
- The route handler does `entity_cls(org_id=..., **data)` where `entity_cls` is closed over the stale class
- Validation uses the stale class's `__init__` validator, which enforces the stale enum

Result: the registry and Mongo are correct but every HTTP request to `/api/{entity}/...` still validates against the old schema. There's no way to unreach the stale routes short of restarting the process.

The same bug affects `PUT /api/entitydefinitions/{name}/modify` and the `migrate` endpoint — both call `register_domain_entity` and both leave stale routes in place.

### Impact
- "Live entity-def replacement without restart" is effectively broken. The kernel docs imply this works (`"Registers it immediately without restart"`) but it doesn't for any use case that changes field types, enum values, state machine, or is_state_field/is_relationship flags.
- Additive changes (adding new optional fields) happen to work because the OLD class doesn't reject the new fields (they just go into the BaseModel without validation).
- Silent correctness bug for operators — you think you've replaced an entity definition, and for most operations it looks like you did, but write operations silently use the stale schema.

### Proposed fix
Before calling `app.include_router(router)` in `register_entity_routes`, find and remove all routes whose path starts with `/api/{collection_name}/` from `app.router.routes`. Something like:

```python
prefix = f"/api/{slug}"
app.router.routes = [
    r for r in app.router.routes
    if not (hasattr(r, "path") and r.path.startswith(prefix + "/"))
]
app.include_router(router)
```

Alternative: have `register_domain_entity` take a `replace=True` mode that wipes existing routes for this entity before re-including.

### Workaround until fixed
Restart the API service (`railway up --service indemn-api`). For dev this is ~30-60s of downtime; for prod this is a full deploy. Document this limitation in `docs/guides/development.md` so no one else hits it without warning.

---

## Bug #30 — Manual entity create returns HTTP 500 due to unique index on nullable field; kernel had no index reconciliation 🟢

**Discovered:** 2026-04-27 (Alliance trace)
**Severity:** **High** (blocks any entity with a unique-but-nullable field — Meeting, Company, others)
**Location:** `kernel/db.py` (additive create_index loops), `kernel/entity/definition.py` (no sparse/partial filter support), `kernel/entity/indexes.py` (new — created during fix)

### Symptom
`POST /api/meetings/` with `{"title": "...", "date": "..."}` (no `external_ref`) returned HTTP 500. After Bug #2 (the API error transparency fix) deployed, the body surfaced the actual exception:
```
DuplicateKeyError: E11000 duplicate key error collection: indemn_os.meetings index: org_id_1_external_ref_1 dup key: { ..., external_ref: null }
```
The first manual Meeting succeeded; the second collided on `external_ref: null` because the Meeting entity had a unique index on `external_ref` but `external_ref` is nullable for manual meetings (no Google Meet / Apollo source). MongoDB's unique index treats explicit null as a value, so only ONE manual meeting per org was allowed.

### Two-layer root cause + journey

**Initial wrong hypothesis: stale index.**
First diagnosis assumed the index was a relic of a prior version of the Meeting entity definition that the kernel had never cleaned up. The kernel only ever ADDED indexes (idempotent `create_index` in startup + `register_domain_entity`); it never DROPPED indexes the operator had stopped requesting. So removing `unique: true` from a field flag would leave the unique index in place forever. This was indeed a real kernel gap — but it wasn't the actual cause for Meeting.

Verification via the API showed the Meeting definition DOES declare `external_ref: {unique: true}`. The index isn't stale — it's intentional. Same for Company's `domain` (Bug #25).

**Actual root cause: unique index on nullable field, no partial filter.**
The semantic the operator wants: `external_ref` is unique IF set, but should allow many docs without it (manual meetings have no external system source). MongoDB's plain `sparse: true` only excludes documents where the indexed field is MISSING — but Pydantic writes `external_ref: null` explicitly for unset Optional fields, so plain sparse never helps. The correct MongoDB pattern is `partialFilterExpression: {field: {$type: <bson_type>}}` — this excludes both null and missing because null isn't of any concrete type.

The kernel did not support `sparse` OR `partialFilterExpression` in entity definitions, and there was no path for an operator to express "unique-when-set" through the self-evidence surface (`indemn entity ...`).

### Fix — declarative index reconciliation + sparse-via-$type translation
Multiple PRs to main:

1. **`kernel/entity/indexes.py`** (new) — `reconcile_indexes(coll, defn)`. Diffs current MongoDB indexes vs the desired set computed from the entity definition. Drops kernel-managed indexes (those matching `org_id_1[_<field>_<dir>]*` naming) that aren't in the desired set OR whose options no longer match. Creates missing ones. Preserves `_id_` and operator-added custom-named indexes. Idempotent.

2. **`kernel/db.py`** — replaced both additive `create_index` loops (startup at `init_database()` + runtime at `register_domain_entity`) with a call to `reconcile_indexes`. Now the kernel is declarative: the entity definition is source of truth and MongoDB follows.

3. **`kernel/entity/definition.py`** — added `sparse: bool = False` to `FieldDefinition` and `IndexDef`.

4. **`kernel/entity/indexes.py`** — when a FieldDefinition has `sparse: true`, the reconciler emits `partialFilterExpression: {<field>: {$type: <bson_type>}}` instead of `sparse: true`, using a small map (str→string, objectid→objectId, datetime→date, etc.). Compound IndexDef sparse is recorded but not currently translated (no per-field type metadata in IndexDef; future work if needed).

5. **`kernel/api/admin_routes.py`** — added `modify_fields` to `PUT /api/entitydefinitions/{name}/modify`, so an operator can change an existing field's spec (e.g. add `sparse: true`) without remove+add gymnastics.

6. **`kernel/api/app.py`** — added `setup_logging()` to API startup so `kernel.*` INFO logs reach Railway/Grafana. Previously the API service inherited Python's default WARNING level and silently dropped all kernel logs, making the reconciler's behavior un-debuggable in production.

### Operator workflow after fix
The whole loop is on the self-evidence surface — no mongosh ever:
```
indemn entity get Meeting
# see external_ref: {type: str, unique: true, sparse: true}

# (or change it via API)
PUT /api/entitydefinitions/Meeting/modify
{"modify_fields": {"external_ref": {"type": "str", "unique": true, "sparse": true}}}

# kernel re-registers the entity, reconcile_indexes sees the option mismatch,
# drops org_id_1_external_ref_1, creates it as unique with
# partialFilterExpression: {external_ref: {$type: "string"}}.

# Manual Meeting creates now succeed.
```

### Verification (2026-04-27 post-deploy)
```
POST /api/meetings/  body: {"title":"Alliance Discovery (Feb 1)", "date":"2026-02-01T..."}  → 201
POST /api/meetings/  body: {"title":"Alliance Renewal (Apr 8)",  "date":"2026-04-08T..."}  → 201
POST /api/companys/  body: {"name":"Test Company A"}  → 201
POST /api/companys/  body: {"name":"Test Company B"}  → 201
```
Both pairs succeeded; previously each pair's second create 500'd. Bug #2 (Meeting) and Bug #25 (Company) both unblocked by this single root-cause fix. Bug #26 (Deal update with company ref) likely a different shape — not yet retested.

### Lesson
**The OS principle is "the entity definition is source of truth, the database follows."** When a field flag changes, the corresponding MongoDB state must update too — by the kernel, not by the operator running mongosh. The additive-only index strategy violated that principle silently. The reconciler fix makes it real.

### Linked OS work
- Index reconciler (commits `53a7d49`, `f09a07b`, merged `869a153`)
- Sparse → partialFilterExpression translation (commit on main `<latest>`)
- modify_fields API extension (`1b2384b`)
- API logging config (`957f58d`)
- Diagnostic logging (`cfde807`) — kept for future operations debugging
- All deployed via `railway up --service indemn-api` 2026-04-27

---

## Bug #31 — Missing kernel primitive: entity-resolution (partial-identity → ranked candidates) 🟢

**Discovered:** 2026-04-24 (GR Little trace), addressed 2026-04-27.
**Severity:** **Critical** (root cause of Bug #16's 446-Company explosion; required for any associate that processes inbound entities at scale)
**Location:** `kernel/capability/entity_resolve.py` (new), `kernel/capability/__init__.py`, `kernel/skill/generator.py`

### Symptom
Associates processing inbound emails / meetings / documents had no kernel-level way to ask "which existing entity in the graph is this?" The graph held the answers (Companies with names, Contacts with emails, etc.) but there was no query path optimized for partial-identity resolution. Each associate skill improvised — `list --search` against partial signals, fuzzy-matching in the LLM head, falling back to `create` when nothing matched. Result: silent duplication. The 446-Company explosion is the visible artifact; the missing primitive is the cause.

### Root cause (architectural)
The kernel's only existing match-shaped primitive was the rule engine, which is great for deterministic per-org rules but doesn't compose strategies (exact + fuzzy + future vector) and doesn't return ranked candidates. There was no shared abstraction for "give me what we already know that resembles this." Every domain on the OS will face this question — it's connective tissue, not domain logic.

### Fix
New kernel capability `entity_resolve`, registered alongside `auto_classify` / `fetch_new` / `stale_check`. Domain-agnostic: knows about entities, fields, and a small fixed set of match-strategy types. Configured per-entity-type via `activated_capabilities` so each entity declares which fields are resolution-relevant.

**Built-in strategies (v1):**
- `field_equality` — normalize the candidate value, query by equality on the field, score 1.0 per hit. Normalizer registry: `email` (lowercase, strip; preserves plus aliases), `domain` (lowercase, strip protocol/www/path/trailing-dot), `lowercase_trim`, `none`. Sweeps recent entities to catch values that weren't normalized at write time.
- `fuzzy_string` — rapidfuzz `token_set_ratio` against the field, threshold-gated (default 0.85). Score = ratio/100 so it composes equally with field_equality. Bounded at 500 entities per call (configurable).

**Combination:** union of candidates by `_id`, max-score across strategies (so multi-strategy hits don't stack >1.0 — `matched_on` grows instead), sort descending, return top N (default 20). Each candidate carries a small summary so callers don't need a follow-up GET.

**Vector search** via MongoDB Atlas Vector Search is intentionally deferred to v2 — `field_equality` + `fuzzy_string` are already powerful and adding embedding cost+infra prematurely is wrong. Layer in only when real customer data shows it's needed.

### Contract (load-bearing)
**The capability returns ranked candidates. It never auto-picks.**
- Score 1.0 means: exact match after normalization. Caller can auto-link only when there's exactly one 1.0 candidate AND a rule says so.
- Score < 1.0 is fuzzy (probabilistic). Caller MUST hand off to a higher reasoning layer — either an LLM step that gets the candidate list as explicit context (and the LLM's tool-call decision is recorded via `save_tracked` audit), or a human review queue.
- Multiple candidates tied at score 1.0 is ambiguity, surfaced honestly. Two Companies with the same domain → two candidates at 1.0. The caller deals with it; the kernel never silently picks.

This contract is what achieves "no silent wrong picks" — the strict interpretation of "100% accurate" in the customer-system trace plan. Fuzzy auto-merge is OUT of scope by design.

### Verified live (2026-04-27)
After deploy + activation on Company with `[{type: field_equality, field: name, normalizer: lowercase_trim}, {type: fuzzy_string, field: name, threshold: 0.85}]`:

| Query | Result |
|---|---|
| `{"name": "Alliance Insurance"}` | Both canonical Alliance (1.0) AND auto-create dupe "Alliance" (1.0) — ambiguity surfaced |
| `{"name": "FoxQuilt"}` | `Foxquilt` (1.0 from lowercase-equality) + `Fox Quilt` (0.94 fuzzy) — exactly the dupe pair Bug #16 produced |
| `{"name": "This Company Does Not Exist Anywhere"}` | 0 candidates — no false positives |

### What's still pending (next session)
The kernel primitive is shipped. Bug #16 and Bug #17 don't fully resolve until the **associate skills** (Email Classifier, Touchpoint Synthesizer) are updated to:
1. Call `indemn <entity> entity-resolve --data '{"candidate": {...}}'` before any create.
2. Auto-link only when there's exactly one candidate at score 1.0.
3. Transition the parent (Email or Meeting) to `needs_review` when only fuzzy candidates exist.
4. Create new only when 0 candidates returned.

That's domain skill work — separate from the kernel piece. Marking #16 and #17 🟡 (kernel ready, skill update pending) until that lands.

### Linked OS work
- Capability module: `kernel/capability/entity_resolve.py` (new)
- Registration + collection-level routing: `kernel/capability/__init__.py`
- Skill generator: `kernel/skill/generator.py` (Resolve section emitted when activated)
- 29 unit tests: `tests/unit/test_entity_resolve.py`
- 7 new skill-generator tests: `tests/unit/test_skill_generator.py`
- Branch: `feature/entity-resolve` (commit `579c713`, merged `a5a1c97`)
- Deployed: `railway up --service indemn-api` 2026-04-27
- Activated on Company: `PUT /api/entitydefinitions/Company/enable-capability` 2026-04-27

---

## Bug #32 — `preview_bulk_operation` returns ObjectId-bearing samples that Temporal can't serialize + no retry policy → infinite retry storm 🟢

**Discovered:** 2026-04-27 (during Bug #23 verification)
**Severity:** **High** (every dry-run with non-empty sample stalls a workflow forever)
**Location:** `kernel/temporal/activities.py::preview_bulk_operation`, `kernel/temporal/workflows.py::BulkExecuteWorkflow.run` (dry_run branch)

### Symptom
After deploying Bug #23/#24 fix, verification of the operator-filter end-to-end against the live API showed: dry-run bulk-delete with an operator filter that matched any documents (e.g. `{"created_at": {"$gte": "<recent>"}}`) hung in `RUNNING` forever. Same filter via the list endpoint worked instantly. Process-bulk-batch (non-dry-run) with the same shape also worked. Only the preview path stalled.

Worker logs showed:
```
[WARN] Completing activity as failed (... 'activity_type': 'preview_bulk_operation' ...)
```
…repeated every 30-90s indefinitely. No traceback surfaced because Temporal's default activity-failure path doesn't log the exception.

### Root cause (two layers)

**Layer 1 — ObjectId serialization.** `preview_bulk_operation` returns:
```python
"sample": [e.model_dump() for e in sample]
```
Pydantic v2's `model_dump()` returns raw `ObjectId` and `datetime` values in the dict — but Temporal's default Python data converter encodes activity results via JSON (effectively `pydantic-core`'s `to_json`), which doesn't know how to encode `bson.ObjectId`. The activity raises a serialization exception when the converter tries to send the result back across the workflow boundary.

This bug was **latent** in the previous `preview_bulk_operation` because the OLD code didn't call `current_org_id.set(ObjectId(spec.org_id))` before `find_scoped(...)`. With no org_id contextvar set, `find_scoped` skipped the org-scoping clause, and queries returned 0 documents in many cases (depending on session role) — so `sample` was always empty and the serialization issue never surfaced. Fixing the org_id contextvar (correct security behavior) exposed this latent serialization bug.

**Layer 2 — no retry policy.** The workflow's `execute_activity(preview_bulk_operation, ...)` call had `start_to_close_timeout=timedelta(minutes=2)` but no `retry_policy=RetryPolicy(...)`. Temporal's default RetryPolicy is unlimited retries with exponential backoff. So when the activity failed with a serialization error, Temporal retried forever — the workflow appeared `RUNNING` indefinitely because retries kept resetting the activity, never declaring the workflow `FAILED`. The 5+ stuck workflows from earlier sessions visible in `bulk list` (some from Apr 18, hours/days old) all share this fate.

### Fix
Two changes, both in this PR:

1. `kernel/temporal/activities.py::preview_bulk_operation` — replace `e.model_dump()` with `to_dict(e)` from `kernel.api.serialize`, which recursively converts ObjectId → str, datetime → ISO string, Decimal → float for JSON-safety. Same helper every API route uses.

2. `kernel/temporal/workflows.py::BulkExecuteWorkflow.run` — add `retry_policy=RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=2), non_retryable_error_types=["PermanentProcessingError"])` to the dry-run `execute_activity` call. Validation failures (the `PermanentProcessingError` raised by `_coerce_bulk_filter` on bad input) don't retry. Other failures retry up to 3 times then mark the workflow `FAILED` so callers see a real terminal state instead of an indefinite `RUNNING`.

### Verification
After redeploy, dry-run bulk-delete with `{"created_at": {"$gte": "2026-04-27T20:00:00Z"}}` returns a normal preview result with `count: <real>` and `sample: [<JSON-safe dicts>]` within seconds.

### Linked OS work
- Same branch as Bug #23/#24: changes land alongside `bugfix/bulk-delete-operator-filters` (commit `<TBD>`)
- Same PR/merge — the verification surfaced the issue, the fix is small, and the new test stays with the bulk verification suite.
- Pre-existing zombie workflows (`bulk-e3affce85276` from Apr 18, several from earlier today) will eventually time out via Temporal's workflow execution timeout but won't auto-clear; can be cancelled manually via `indemn bulk cancel <wf>`.

---

## Future bugs (add as we encounter them)

Append new entries above this line as you find them. Format:

```
## Bug #N — <short title> <status emoji>

**Discovered:** YYYY-MM-DD
**Severity:** Low/Med/High
**Location:** file path or subsystem

### Symptom
...

### Root cause
...

### Fix / Proposed fix
...
```

---

## Summary table

| # | Title | Severity | Status |
|---|---|---|---|
| 1 | Meet adapter rejects date-only `since` | High | 🟢 Fixed (8afda9d) |
| 2 | No singular `delete` CLI command | Med | 🔴 Open |
| 3 | `bulk status` lacks deletion counts | Low | 🔴 Open |
| 4 | `bulk-delete --filter '{}'` silent no-op | Med | 🔴 Open |
| 5 | `fetch-new --help` broken (triple-dash, no docs) | Med | 🟢 Fixed (Apr 28 burst #5, merge `896a4b0` — factory functions in both CLI surfaces) |
| 6 | Auto-generated skill has wrong fetch-new syntax | Med | 🔴 Open |
| 7 | Adapter noisy "fileId" warnings | Low | 🟢 Fixed (Apr 28 burst #5, merge `896a4b0` — truthy guard + `_export_doc` short-circuit) |
| 8 | Adapter swallows all per-user errors | Med | 🟢 Fixed (Apr 28 burst #5, merge `896a4b0` — `_PerUserErrorTracker` raises on systemic failures) |
| 9 | Associates pass dicts not ObjectIds → dead letters | High | 🟢 Fixed (Apr 27 burst #4, merge `31bb594` — boundary coercion + auto_resolve flag) |
| 10 | Old meetings unprocessed (one-time data state) | Low | 🟢 Resolved (deleted) |
| 11 | `/api/queue/stats` 404 | Low | 🟢 Fixed (Apr 28 burst #4, merge `e9d04da` — aliased to `/api/_meta/queue-stats`) |
| 12 | Wrong MongoDB URI in AWS secret | Low | 🔴 Open |
| 13 | Railway doesn't auto-deploy on push to main | Med | 🔴 Open |
| 14 | CLI POST/PUT timeout was 60s — too short for fetch-new | Med | 🟢 Fixed (f0dfe89) |
| 15 | Naive entity collection pluralization (`companys`) | Low | 🔴 Open |
| 16 | Associates auto-create Companies despite skill saying never | **High** | 🟡 Kernel ready (Bug #31); skill update pending |
| 17 | No meeting-to-company classifier in pipeline | **High** | 🟡 Kernel ready (Bug #31); skill update pending |
| 18 | Synth doesn't update `Meeting.touchpoint` back-reference | Med | 🔴 Open |
| 19 | Change records sometimes have non-Date `timestamp` | Med (audit-integrity) | 🟢 Fixed (Apr 28 burst #6, merge `cd07fb8` — `_coerce_datetime_fields` at API boundary; root was setattr-bypassing-Pydantic on PUT) |
| 20 | Actor CLI missing `transition`, `delete`, `bulk-*` | Med | 🟢 Fixed (Apr 28 burst #4, merge `e9d04da` — `transition`/`delete` shipped) |
| 21 | Transition API: `to` vs docs' `target_state` | Low | 🟢 Fixed (Apr 28 burst #4, merge `e9d04da` — picked `to` canonical, docs corrected) |
| 22 | Service token untraceability: can't tell which associate acted | **High** | 🟢 Fixed (Apr 27, deployed; effective_actor_id field) |
| 23 | `bulk-delete` silently drops MongoDB operator filters ($in, $gte, $oid) | **Critical** | 🟢 Fixed (Apr 27 burst #4, merge `0ed8c80` + alias `6b8c62e` + retry `b5e4757` — operator safelist + per-field type coercion) |
| 24 | `bulk status` reports COMPLETED even when 0 records matched | Med | 🟢 Fixed (Apr 27 burst #4, merge `0ed8c80` — `completed_no_match` status + `{matched, succeeded, errored, errors}`) |
| 25 | `company create` returns HTTP 500 | Med | 🟢 Fixed (subsumed by #30 — Apr 27) |
| 26 | `deal update` with company ref returns HTTP 500 | Med | 🟢 Fixed (Apr 28 — auto-healed by burst #4 `partialFilterExpression` propagation, verified live `PUT /api/deals/...` returns 200) |
| 27 | `created_by` null on every Company record | Med | 🔴 Open |
| 28 | `actor list --type` flag is silently ignored | Low | 🟢 Fixed (Apr 28 burst #4, merge `e9d04da` — switched to filter-safelist path, now actually filters) |
| 29 | Entity definition replacement doesn't evict old API routes (live replacement silently broken, requires restart) | **High** | 🟢 Fixed (Apr 27, merge `83d2494`) |
| 30 | Manual entity create 500 — unique index on nullable field; kernel had no index reconciliation | **High** | 🟢 Fixed (Apr 27, deployed) |
| 31 | Missing kernel primitive: entity-resolution (partial-identity → ranked candidates) | **Critical** | 🟢 Fixed (Apr 27, deployed + activated on Company) |
| 32 | `preview_bulk_operation` ObjectId serialization + missing retry policy → infinite-retry storm | **High** | 🟢 Fixed (Apr 27 burst #4, merge `b5e4757` — `to_dict()` + bounded RetryPolicy) |
