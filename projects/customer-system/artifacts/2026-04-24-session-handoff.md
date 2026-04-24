---
ask: "Handoff from 2026-04-24 session — what was done, what was learned, what's next, how the next session picks up"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
---

# Session Handoff — 2026-04-24

Context is running low; next session picks up from here. Read this before doing anything else.

## Reading order for next session

1. **This handoff** (`2026-04-24-session-handoff.md`)
2. `2026-04-24-alignment-framing.md` — the lens we use to interpret Kyle's Apr 24 prep doc (it's aspirational signal, not spec)
3. `2026-04-24-kyle-craig-apr23-sync.md` — Kyle's actual verbal ask (cleaner than his prep doc)
4. `2026-04-24-kyle-prep-doc-apr24.md` — preserved but treat as signal, not spec
5. `2026-04-24-os-bugs-and-shakeout.md` — running list of 21+ OS bugs discovered today
6. `INDEX.md` — now updated with today's state
7. Prior session artifacts if needed: `2026-04-22-entity-model-brainstorm.md`, `2026-04-23-implementation-session.md`

## Where we are

### Done today
- Deployed `fix(google_workspace): normalize 'since' to RFC3339` to fix `fetch-new` returning 0 meetings — Bug #1
- Fixed CLI POST/PUT timeout: bumped 60s → 600s, configurable via `INDEMN_CLI_TIMEOUT` — Bug #14
- Cleaned slate: deleted 21 test meetings, re-fetched 67 real meetings from last 7 days via `indemn meeting fetch-new`
- **Suspended the 3 pipeline associates** (Email Classifier, Touchpoint Synthesizer, Intelligence Extractor) — they're in `suspended` status, not deleted. Re-activate in the next session when ready.
- Captured 21 OS bugs + shakeout findings in `2026-04-24-os-bugs-and-shakeout.md` (live document)
- Captured 4 context artifacts for Kyle sync framing (see reading list above)

### The key discovery from today

**The system has 446 Company records, most of them duplicates.** The ledger (changes collection) shows every single one was created:
- By `actor_id = Platform Admin` (the service-token actor)
- As a **standalone CLI call** (no upstream message cascade — not triggered by email/meeting processing)

This is NOT the Email Classifier or Touchpoint Synthesizer misbehaving during their normal message processing. Something ELSE is using the Platform Admin service token and creating Company records directly.

**We could not identify WHAT**. The ledger shows actor_id but not "which associate" — all associates share the same service token. That's Bug #22 (see below).

Craig's assertion: "I'm fairly confident it's an associate using Platform Admin." Agree — just can't tell which one from the ledger alone.

Spike pattern:
- Apr 18: 87 creations (original baseline, likely legit seed)
- Apr 21-22: 3 creations
- Apr 23: **299 creations** (the big spike — same day as team email backfill)
- Apr 24: 57 (today — our meeting ingestion)

Duplicates at scale:
- "Indemn" × 28
- "EventGuard" × 28
- "TechFix Computer Repair" × 17 (suspicious — looks like fake test/spam data)
- "Indemn.ai" × 12
- "Apollo" × 9
- Many others with 2-7 copies

### State after cleanup (when this handoff was written)

- Associates: 3 suspended, 1 active (OS Assistant — left alone for chat UI)
- Meetings: 67 fresh (last 7 days) — Foxquilt + GR Little Apr 22 among them
- Touchpoints: 43 meeting-type (linked to various companies, many to duplicates)
- Dead letters: 6 synth + 3 classifier (associate-skill bugs — passing dicts not ObjectIds)
- Companies: 446 (pre-cleanup)
- **Cleanup was planned at this point but not yet executed** — see "Next session: plan" below

## Today's key realizations

### 1. The entity model is the playbook is the proposal is the email

Craig reiterated the insight from the prior session: **the interaction timeline, the playbook, the proposal components, and the email drafting are all one thing, not separate features**. The follow-up email is a rendering of the current entity state for a customer at a given moment. The proposal is the same rendering once entities are fully populated.

Consequence: **don't build a "draft follow-up email" associate as a standalone feature**. Instead, build "given an entity state and a playbook for the current stage, produce the next artifact." Email for early stage, proposal for mature, task list for delivery. Same mechanism.

This reframes Phase 3 / 4 of the work.

### 2. Kyle's prep doc is signal, not spec

Kyle is the CEO, not a systems engineer. He uses Claude Code to generate very detailed documents with field-level enums and JSON schemas. **Those are NOT specs we should implement.** They're signal about what outcomes Kyle wants to see from the system.

The right way to engage Kyle:
- "Here's what the OS produces today. What would you change?"
- Never debate field names before he's seen output
- Extract intent (what outcomes does he want?) and ignore implementation detail (how we get there)

For today's planned meeting: we'd demo whatever the pipeline produced, honest about what's broken, and use the conversation to refine. We didn't get to the meeting today — this is queued for next session.

### 3. "We're cooking"

Even when the visible progress looks slow, refining architectural thinking IS the work. The company-matching diagnosis above would be lost if we'd just patched it and moved on. The diagnosis itself is the contribution.

## Next session: plan

### Phase 1 — Clean up and instrument (don't re-run yet)

**1. Clean up companies.** Delete all 359 companies created after Apr 18 (i.e., everything except the original baseline of 87) EXCEPT any referenced by a Deal. That preserves the prospect Companies (FoxQuilt, Alliance, Rankin, Tillman, O'Connor, Amynta, FoxQuilt+Ganesh) and nukes the dupes.

**2. Clean up touchpoints.** Delete all meeting-type touchpoints (43 of them) — they're linked to dupe companies. Email touchpoints stay for now, we'll figure those out later.

**3. Clean up dead-letter messages.** 6 synth + 3 classifier DLs. Purge.

**4. Fix Bug #22: service token observability.** Add a way to tell which associate acted when multiple associates share the Platform Admin service token. Either:
- Give each associate its own service token (Session per associate)
- Add `actor_id` (the associate's actor) separately from `session_actor_id` (the authenticated identity) in change records
- OR: when logging changes, capture the `user-agent` / trigger context

Without this, we cannot do forensics on which associate misbehaved.

### Phase 2 — Diagnose before re-running

Before re-activating associates and re-processing, pick ONE specific case and observe what the associate actually does:

**For Foxquilt meeting:**
- Reactivate ONLY the Touchpoint Synthesizer associate
- Manually enqueue a synth message for the Foxquilt meeting (or re-transition it to trigger a watch event)
- Watch the harness logs / OTEL traces to see the actual CLI commands the synth runs
- Understand: did it query `indemn company list`? What did it see? Why did it decide to create a new "Foxquilt" instead of linking to "Fox Quilt" (old)?

Craig's strong intuition: "An LLM should very easily be able to reliably make that connection. There has to be something wrong with the instructions or the data it's seeing." Diagnose, don't speculate.

### Phase 3 — Fix the root cause

Based on Phase 2 diagnosis, choose the minimum fix:
- Skill text change, OR
- Add Company.domain field + deterministic auto_link capability, OR
- Split Touchpoint Synthesizer into [Meeting Classifier] → [Touchpoint Synthesizer], OR
- Enforce "no auto-create" at the permission/entity level (hard fence)

Test on Foxquilt alone. Then GR Little. Then full batch.

### Phase 4 — Playbook-driven artifact generation

THIS is where the email/proposal/task-list generator lives — as part of the playbook, NOT as a standalone skill. Takes: entity state for a Company + Playbook for the current Deal stage → next artifact.

Demo for Kyle when ready: side-by-side of transcript → extracted entities → playbook applied → email draft.

## OS bugs opened today (full list in 2026-04-24-os-bugs-and-shakeout.md)

1. 🟢 Fixed: Meet adapter rejected date-only `since`
14. 🟢 Fixed: CLI POST/PUT timeout was 60s
Open:
2. No singular `delete` CLI command
3. `bulk status` lacks deletion counts
4. `bulk-delete --filter '{}'` silent no-op
5. `fetch-new --help` broken (triple-dash `---cap`)
6. Auto-generated skill has wrong `fetch-new` syntax
7. Adapter noisy "Missing fileId" warnings
8. Adapter swallows all per-user errors silently
9. Associates pass dicts not ObjectIds → dead letters
10. 🟢 Resolved: Old meetings unprocessed (deleted)
11. `/api/queue/stats` returns 404
12. Wrong MongoDB URI in AWS secret
13. Railway doesn't auto-deploy on push to main
15. Entity collection names use naive `+s` pluralization (`companys`)
16. **High:** Associates auto-create Companies despite skill saying never
17. **High:** No meeting-to-company classifier in pipeline
18. Synth doesn't update `Meeting.touchpoint` back-reference
19. Change records sometimes have non-Date `timestamp`
20. Actor CLI missing `transition`, `delete`, `bulk-*`
21. Transition API: `to` vs docs' `target_state` mismatch

### New Bug #22 to add (service token observability)

**Bug #22 — Can't tell which associate made a change when multiple share a service token.** Bigger than it sounds. All 3 (now 4 counting OS Assistant) associates authenticate as `Platform Admin` via the shared runtime service token. When they make CLI calls, the change records show `actor_id = Platform Admin`. No way to tell which associate took the action. Today this blocked us from identifying which associate created the 299 Company dupes on Apr 23. Per-associate service token OR separate `associate_id` field in change records needed.

## Commits made today (indemn-os)

```
f0dfe89 fix(cli): bump POST/PUT timeout to 600s, configurable via INDEMN_CLI_TIMEOUT
8afda9d fix(google_workspace): normalize 'since' to RFC3339 before Meet API filter
```

Also pushed to main. Railway does NOT auto-deploy on push (Bug #13). Both fixes live via `railway up --service indemn-api`.

## Known good IDs / references

- Foxquilt meeting: `69eb94a92b0a50861892382d` — Apr 22 13:59, Karim Jamal + Nick Goodfellow + Craig + Kyle + George
- GR Little meeting: `69eb94a92b0a50861892382a` — Apr 22 14:59, Walker Ross + Heather + Kyle
- Apr 17 Nick discovery (Foxquilt provenance): `69eb94a92b0a508618923843`
- "Fox Quilt" Company (original, Apr 18 baseline, linked to FOXQUILT-2026 deal): `69e41a8eb5699e1b9d7e991d`
- Platform Admin actor: `69e23d586a448759a34d3824`
- Kyle Geoghan actor: `69e7d26f23eefe641ea13e47`
- Email Classifier (suspended): `69ea1bca23eefe641ea13f44`
- Touchpoint Synthesizer (suspended): `69ea1bd123eefe641ea13f48`
- Intelligence Extractor (suspended): `69ea1bd223eefe641ea13f4c`
- OS Assistant (STILL ACTIVE): `69e50bdce35065d0498df6cc`
- Google Workspace Integration: `69e7a018bd939892d8e7a2a5`
- _platform org: `69e23d586a448759a34d3823`

## Authentication pattern (still works)

```bash
TOKEN=$(curl -s -X POST https://api.os.indemn.ai/auth/login \
  -H "Content-Type: application/json" \
  -d '{"org_slug": "_platform", "email": "craig@indemn.ai", "password": "indemn-os-dev-2026"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

INDEMN_API_URL=https://api.os.indemn.ai INDEMN_SERVICE_TOKEN="$TOKEN" INDEMN_CLI_TIMEOUT=600 \
  uv run indemn <command>
```

Direct MongoDB (secret URI is wrong — Bug #12, use this):
```bash
mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/indemn_os" --quiet --eval '...'
```

## The meeting with Kyle

Didn't happen today. It's queued for a future sync. Kyle's expectation (Apr 23 verbal): see the OS produce draft follow-up emails for the two Apr 22 meetings (Foxquilt + GR Little), compare to what he would have sent, iterate on the playbook.

When we resume and do the cleanup + diagnosis + fix + playbook work: **re-anchor on Kyle's verbal ask, not his written prep doc.** Show concrete output, don't debate schema.
