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

## Bug #16 — Associates auto-create Company records despite "never create" skill instruction 🔴

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

## Bug #17 — No meeting-to-company classifier 🔴

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

## Bug #22 — Cannot tell which associate acted when multiple share the service token 🔴

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

## Bug #25 — `company create --data` returns HTTP 500 Internal Server Error 🔴

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
| 5 | `fetch-new --help` broken (triple-dash, no docs) | Med | 🔴 Open |
| 6 | Auto-generated skill has wrong fetch-new syntax | Med | 🔴 Open |
| 7 | Adapter noisy "fileId" warnings | Low | 🔴 Open |
| 8 | Adapter swallows all per-user errors | Med | 🔴 Open |
| 9 | Associates pass dicts not ObjectIds → dead letters | High | 🔴 Open |
| 10 | Old meetings unprocessed (one-time data state) | Low | 🟢 Resolved (deleted) |
| 11 | `/api/queue/stats` 404 | Low | 🔴 Open |
| 12 | Wrong MongoDB URI in AWS secret | Low | 🔴 Open |
| 13 | Railway doesn't auto-deploy on push to main | Med | 🔴 Open |
| 14 | CLI POST/PUT timeout was 60s — too short for fetch-new | Med | 🟢 Fixed (f0dfe89) |
| 15 | Naive entity collection pluralization (`companys`) | Low | 🔴 Open |
| 16 | Associates auto-create Companies despite skill saying never | **High** | 🔴 Open |
| 17 | No meeting-to-company classifier in pipeline | **High** | 🔴 Open |
| 18 | Synth doesn't update `Meeting.touchpoint` back-reference | Med | 🔴 Open |
| 19 | Change records sometimes have non-Date `timestamp` | Low | 🔴 Open |
| 20 | Actor CLI missing `transition`, `delete`, `bulk-*` | Med | 🔴 Open |
| 21 | Transition API: `to` vs docs' `target_state` | Low | 🔴 Open |
| 22 | Service token untraceability: can't tell which associate acted | **High** | 🔴 Open |
| 23 | `bulk-delete` silently drops MongoDB operator filters ($in, $gte, $oid) | **Critical** | 🔴 Open |
| 24 | `bulk status` reports COMPLETED even when 0 records matched | Med | 🔴 Open |
| 25 | `company create` returns HTTP 500 | Med | 🔴 Open |
| 26 | `deal update` with company ref returns HTTP 500 | Med | 🔴 Open |
| 27 | `created_by` null on every Company record | Med | 🔴 Open |
| 28 | `actor list --type` flag is silently ignored | Low | 🔴 Open |
