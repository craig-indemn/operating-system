# Session-Start Prompt — 2026-05-05 OS Hardening (pre-TD-2)

> **Objective:** Tier 1 OS hardening sprint that closes friction items before TD-2 cascade activation.
> **Drafted:** 2026-05-04 Session 17 close.
> **Usage:** copy everything between the `===PROMPT START===` and `===PROMPT END===` markers and paste into the next session.

---

```
===PROMPT START===

You are starting a session on the operating-system project — building the Indemn customer system on top of the Indemn Operating System (OS). This prompt hydrates your shared mental model with Craig so you can execute alongside him as a peer, not a junior re-deriving decisions he's already made.

## MANDATORY: read the canonical shared context, in this order

These files together ARE your shared mental model. Read all of them. No skipping. No skimming.

1. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/CLAUDE.md
2. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/vision.md
3. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/roadmap.md
4. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/os-learnings.md
5. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/CURRENT.md
6. /Users/home/Repositories/indemn-os/CLAUDE.md

Reading is non-negotiable. Without these you will propose things Craig would never propose (simplify vision, inline skills, route around bugs), re-derive decisions already made, lose the thread.

## After loading: pull on-demand depth for your work area

Once the mandatory set is loaded, follow CLAUDE.md's "When working on X, READ these" router (Section 8). For this session's OS-hardening sprint specifically, also pull:

- `os-learnings.md` end-to-end — this is the spec for the work. Every 🔴 / 🟡 row is the source of truth for what's queued, what's in flight, what's done.
- `kernel/capability/fetch_new.py` (Session 17 shipped a chunk-cap as a bridging fix; this session ships the proper bulk_save_tracked replacement)
- `kernel/entity/save.py` (where `save_tracked()` lives — bulk version goes here as a sibling)
- `indemn_os/src/indemn_os/queue_commands.py` (pattern for the new `indemn diagnose` command group)
- `kernel/api/registration.py` (auto-list endpoint — for the field-filter regression fix)
- `kernel/message/emit.py::_build_related_entities` (for `--include-related` polymorphic Option B support)

Bias toward MORE reading, not less. This session is OS kernel work — read the existing patterns before you write new ones.

## YOUR OBJECTIVE FOR THIS SESSION

**Pre-TD-2 OS hardening sprint.** TD-1 is verified done end-to-end (per Session 17 close — see SESSIONS.md). The 7-associate cascade (TD-2) lands next, but Craig has been explicit: he is in the business of building robust software, and bugs that impede effective work with the OS get fixed before the next layer goes on top. This session resolves the Tier 1 OS friction items so TD-2 lands on a foundation that doesn't fight us.

**Tier 1 — must do before TD-2 begins:**

1. **`fetch_new` bulk_save_tracked** (~half day). Add `bulk_save_tracked(entities, method=...)` in `kernel/entity/save.py` as a sibling to `save_tracked()`. Single Pydantic validation pass via `TypeAdapter(list[T]).validate_python`; `insert_many` to MongoDB; in-memory hash-chained change records inserted via second `insert_many`; batched watch evaluation + grouped `insert_many` of queue messages; partial failure preserved (`insert_many(ordered=False)` + per-row error collection); OTEL span per batch with `batch_size, succeeded, errored, duration_ms`. Wire from `kernel/capability/fetch_new.py` — replaces the per-item `for item in raw_results: await save_tracked(...)` loop. Both code paths preserve the same audit + watch contracts. Tests: 10+ unit tests covering happy path, partial-failure, hash-chain integrity across batches, watch firing per inserted entity. Done-test: a 100-record fetch_new call drops from N×200ms (~20s) to <2s end-to-end, observable via OTEL `capability.fetch_new` span. The `--data '{"limit": 100}'` chunk-cap on the 4 fetcher skills can be removed afterward (or left — bulk_save makes the cap irrelevant rather than load-bearing).

2. **`indemn diagnose` command group** (~half day). New `indemn_os/src/indemn_os/diagnose_commands.py` Typer surface alongside `queue_commands.py`. Sub-commands:
   - `indemn diagnose actor <id>` — recent N runs (claim → result), durations, outcomes, failure modes; pulls from message_log + queries OTEL by `associate.id` attribute.
   - `indemn diagnose message <id>` — full lifecycle: created_at, every claim event with claimed_by, every visibility_timeout extension, status transitions, completed_at if logged, last_error.
   - `indemn diagnose cron <actor_name>` — last 10 cron ticks for a scheduled actor with per-tick durations + outcomes + bottleneck breakdown from OTEL spans.
   New API endpoints under `/api/_diagnose/*` to back the CLI (so the auth + org-scoping is consistent). Tests: 6+ unit tests pinning command shapes + endpoint contracts. Done-test: every diagnostic Session 17 reached for during the email-fetcher debug should be `indemn diagnose <thing>` instead of mongosh + railway logs + aws CLI. Document the `INDEMN_SERVICE_TOKEN` env-var auth pattern in `indemn auth --help` while you're there (one-line docstring fix).

3. **List endpoint arbitrary field filters — regression fix** (~1-2 hours). Per os-learnings.md row "List endpoint accepts no arbitrary field filters" — the fix shipped in `df92cca` regressed or has gaps. `?data={"source_entity_type":"Email"}` is silently ignored; `?data={"totally_made_up_field":"foo"}` returns 200 with all results instead of 400. Either re-fix the original `kernel/api/_filter_safelist.py::parse_filter` integration with the list endpoint, or write a fresh route-level filter handler. Tests must include the negative case (bad field → 400) AND the positive case (good field → filtered results). CLI's `<entity> list --data` flag should also surface the filter — propagate the fix to both kernel + indemn_os surfaces.

4. **`--include-related` polymorphic Option B support** (~2 hours). Per os-learnings.md row — Touchpoint's `source_entity_id` is polymorphic (Email or Meeting depending on `source_entity_type`), `is_relationship: false` so today's `_build_related_entities` skips it. Add `is_polymorphic_relationship: true` + `target_type_field` field-spec support; resolver loads the type at runtime per-entity. The IE skill (and TD-2's MeetingClassifier later) gets clean source-content navigation without the manual two-step pattern.

5. **Employee `entity_resolve` activation** (5 min). Single CLI call: `PUT /api/entitydefinitions/Employee/enable-capability` with `{"capability": "entity_resolve", "config": {"strategies": [{"type": "field_equality", "field": "email", "normalizer": "lowercase_trim"}]}}`. TS / MC need this to resolve internal participants. Verify with `indemn employee entity-resolve --data '{"candidate": {"email": "kyle@indemn.ai"}}'` returning Kyle's Employee record at score 1.0.

**Tier 1.5 — os-learnings.md cleanup pass (~30 min, do AFTER the code work above):**

Audit the 🔴 / 🟡 rows in os-learnings.md against actual production state — several are already fixed but mismarked. Specifically check:
- Bug #44 voice-deepagents (Session 15 closed it — should be 🟢)
- Bug #25 / #26 / Meeting create (subsumed by Bug #30 — should be 🟢)
- Slack ingestion foundational + Document.source enum (both done in Session 14 — should be 🟢)
- "List endpoint accepts no arbitrary field filters" (re-fixed in Tier 1 #3 above — flip to 🟢 once that ships)
- Any other rows that show 🟢 in the body but 🔴 in the status badge

Reclassify each based on actual code/state, not stale optimism.

**Tier 2 — defer (don't do this session):** Proposal `superseded` state machine (TD-6), 12-stages-with-archetypes / origin-referrer / Playbook-hydration (TD-4 research), Document-as-artifact for emails (TD-5), Opportunity vs Problem entity (TD-4), Company hydration (TD-2's Company-Enricher associate is the design answer), Bug #45c resolver-tolerance (TD-11 hardening), Bug #19 followon test fixture pattern (process improvement, no code action).

**Done-test (acceptance criteria for "Tier 1 complete"):**
- All 5 Tier 1 items shipped: code merged to indemn-os main, deployed to indemn-api / runtime-async / queue-processor as relevant, tests green
- Full kernel unit suite passes (currently 481 tests; this session adds ~25-30 new)
- `indemn diagnose actor <email-fetcher-id>` works end-to-end against dev OS (last 10 runs, durations, outcomes — no mongosh required)
- `indemn email list --data '{"company": "<24-hex>"}'` returns filtered results; `--data '{"bogus_field": "x"}'` returns 400
- `indemn employee entity-resolve --data '{"candidate": {"email": "..."}}'` returns ranked candidates
- A fresh email_fetcher cron tick with 100+ new emails completes in <30s end-to-end (vs minutes pre-bulk_save)
- os-learnings.md status badges match actual production state (no stale 🔴s)
- CURRENT.md updated to reflect Tier 1 done; SESSIONS.md appended; commit pushed

**After Tier 1 lands: next session begins TD-2 cascade activation.** Per `roadmap.md § TD-2`: 7-associate cascade (EC v9→v10, MC NEW, SC NEW, TS v6→v7, IE verified, Proposal-Hydrator NEW, Company-Enricher NEW) + ReviewItem universal-escape-valve. Trace-as-build-method per CLAUDE.md § 2 — start with MeetingClassifier on Armadillo's Apr 28 discovery meeting (cleanest trace target: Company + 2 Contacts already exist from Session 12, structured Google Meet attendee list, transcript present).

**Multi-session context:** Pricing Framework parallel session may continue in `.claude/worktrees/gic-feature-scoping/`. Workstream A files in CURRENT.md + the pricing artifacts/tools listed there are read-only for this session. End-of-session, when updating CURRENT.md, only rewrite Workstream B + merged sections — preserve Workstream A verbatim from whatever the parallel session left.

## Operating discipline (non-negotiable)

- **The shared context contains the result of prior brainstorming. USE it.** Don't re-litigate decisions. The Tier 1 list above is the result of a triage Craig and Claude did in Session 17 close. If you find yourself proposing something that was already decided, stop and re-read the relevant section.
- **If something genuinely isn't settled, flag it to Craig BEFORE drifting into design discussion.** Don't unilaterally redesign. The bulk_save_tracked architecture has a draft shape (above) but the actual implementation will surface details — flag them as you find them, don't redesign without alignment.
- **Drive toward execution.** State intent → do the work → report. State at the start of each Tier 1 item: "starting #N — files I'll touch, expected test changes." After: "done — N tests added, deployed, verified." No long brainstorm-style preambles.
- **Use `indemn` CLI first, raw mongo/railway/aws second.** This session's whole point is making `indemn` the diagnostic surface. If you reach for mongosh during item #2's design, that's a signal the diagnose surface needs more — log it.
- **Bug #12 discipline:** the shared `mongodb-uri` AWS Secret stores `dev-indemn-pl-0` (private-link, correct). Sessions 15 + 16 wrongly overwrote it; auto-restore correctly fixed it; Session 17 fixed `mongosh-connect.sh` to do inline host swap. **DO NOT overwrite the shared secret.** If you need local mongosh, the wrapper handles it.
- **Wait for Craig's signal** before running end-of-session protocol. When signaled, run ALL of CLAUDE.md § 7 — none are optional.

## Confirmation step (do this BEFORE any work)

After loading the mandatory set, state:

1. **Top of roadmap** — TD-2 next per `roadmap.md`, but pre-TD-2 OS hardening sprint per Session 17 close (see CURRENT.md "Where we are now")
2. **What CURRENT.md says is in flight** — TD-1 verified done end-to-end; Bug #50 + fetch_new chunk-cap deployed; pre-TD-2 hardening sprint pending
3. **Previous 1-2 entries from SESSIONS.md** — Session 17 (Bug #50 + fetch_new chunk-cap + Bug #12 reframe + zombie cleanup; TD-1 verified) and Session 16 (Bug #40 + #48 + #49)
4. **Your understanding of this session's specific objective** — restated: ship the 5 Tier 1 items + os-learnings cleanup, in order, so TD-2 lands clean. NOT: start TD-2 yet.

Only after that, begin work.

===PROMPT END===
```
