# Customer System — CURRENT

> **Fast-changing state.** What just happened, what's in flight, parallel sessions, blockers, next steps. Rewritten every session. Read this *after* CLAUDE.md to know where things actually stand right now.

**Last updated:** 2026-04-29 (end of Session 12 — three parallel threads: main session Armadillo trace + Hard Rule #1 inversion, parallel kernel-fix session closing Bugs #35/#36/#37, parallel hydration-redesign session producing this CLAUDE/CURRENT/SESSIONS/PROMPT structure)

---

## Top of roadmap

**Phase B1 — entity-resolution skill propagation** (in flight, substantially de-risked). Three load-bearing kernel bugs closed this session (Bugs #35/#36/#37). Hard Rule #1 inverted on EC (resolve-before-create > never-auto-create) — autonomous Company + Contact creation now allowed when resolve returns 0 candidates, since resolve-first is the dedup defense and is now reliable post-Bug-#34/#36. Armadillo Insurance traced end-to-end as designed — first new-prospect trace post-inversion. EC v9 verified on Armadillo's first-contact email.

What's left in B1: drain remaining test cases, reactivate TS + IE, watch full cascade end-to-end on next live email. Reactivate EC when next prospect's first email lands (TFG / John Scanland is the next planned trace target — brain-dump request sent to Kyle).

After Phase B1: B2 hydration (recurring email fetch, meeting backfill, Drive ingestion, hydrate Alliance + Arches + FoxQuilt + the rest). B3 stage research + Playbook completion. B4 autonomous artifact production.

---

## Pipeline associate states

| Associate | State | Skill version | Last activated | Status |
|---|---|---|---|---|
| Email Classifier (EC) | **suspended** (kill switch held; v9 in DB ready) | v9 (`9eef4959ae701614`) | 2026-04-29 (verified on Armadillo) | Hard Rule #1 inverted; resolve-before-create with autonomous create allowed on 0/0; verified live |
| Touchpoint Synthesizer (TS) | **suspended** (unchanged) | v6 (`8e7847c8b329f6ba`) | n/a | Has not been triggered autonomously since Session 9 |
| Intelligence Extractor (IE) | **active** (untouched) | v3 (`b65cee8d4064a30e`) | 2026-04-24 | Silent-stuck-state regression that previously caught it is fixed (Session 10 commit `d914d76`); ran on Armadillo extracting 14 entities |

---

## Material state in dev OS

**Armadillo Insurance constellation (queryable end-to-end):**
- Company `69f22186…444d` — Armadillo Insurance
- Deal `69f223cc…4470` — discovery stage
- 2 Contacts: Matan Slagter (CEO), David Wellner (COO)
- 2 Touchpoints + 14 extracted entities (3 Operations, 3 Opportunities, 1 Decision, 2 Commitments, 4 Signals, 2 CustomerSystem, 1 Task) all linked

**Cleanup pending (from Bug #36 side-effect):** 500 unrelated Emails + 6 unrelated Meetings on Kyle's mailbox via the broken-pre-fix adapter. Sit at status `received`. EC suspended so untouched. Cleanup or accept-fix-forward TBD.

**Cleanup pending (from Bug #37 data side):** 2 malformed Email rows pending cleanup — Emails `69ea548e…6e92` (Oneleet) and `69ea556f…7387` (Linear Orbit).

**Diana@CKSpecialty test entity** (carried forward from Sessions 9-11):
- Email `_id`: `69ea56250a2b41b7696076b3`, state `received`, no Company/Contact links

---

## Parallel sessions / threads during Session 12

Three parallel sessions ran today (2026-04-29):

1. **Main customer-system session** — Armadillo trace + Hard Rule #1 inversion + EC v9. Verified autonomous flow on Armadillo's first-contact email. 4 design gaps surfaced and logged in `os-learnings.md`. Artifacts shipped to Kyle (yesterday's roadmap doc + Armadillo trace HTML via Slack file attachment).
2. **Parallel kernel-fix session** — Closed Bugs #35 (deepagents skill discovery: stacked YAML fix + absolute-path return), #36 (Gmail/Calendar `fetch_new` adapters silently absorbing kwargs), #37 (Email list endpoint poisoned by malformed `company` field). All three load-bearing. Commits on indemn-os main: `8141a80`, `2ba6f63`, `477a98f`, `a5aa89f`.
3. **Parallel hydration-redesign session** (this one) — Solved the meta-problem of 500K-token hydration. Designed the layered hydration model. Shipped: rewritten `CLAUDE.md`, new `CURRENT.md`/`SESSIONS.md`/`PROMPT.md`, design doc at `docs/plans/2026-04-28-shared-context-hydration-design.md`.

The parallel sessions reconciled cleanly via the shared-context-update mechanism — kernel fixes logged to os-learnings, customer-system trace work logged to INDEX.md, hydration redesign done in isolation. The Session 12 close-out commit (`4a5d7f1`) deliberately left this session's CLAUDE.md/CURRENT/SESSIONS/PROMPT changes unstaged for separate commit.

---

## Blockers

None. Bug #35 was the prior blocker — now fixed and live-verified on Armadillo.

EC remains suspended only as a kill-switch caution while we drain the next test cases. Reactivation when TFG / John Scanland's first email arrives.

---

## New design questions / capability gaps logged this session

All in `os-learnings.md` under their respective severity sections:

- **Deal-lifecycle automation gap** (High, Open) — Deal-creator associate doesn't exist yet. Proposal-at-DISCOVERY auto-create not wired. Touchpoint↔Deal chicken-and-egg.
- **Employee `entity_resolve` not activated** (High, Open) — analogous to Contact entity_resolve activation in Session 9; needs the same treatment.
- **Company hydration is bare on auto-create** (Open Design Q) — newly-created Companies have minimal data; need a continuous enrichment process.
- **Contact richer-field parsing from email signatures** (Open Design Q) — title, phone, address are in signatures but fall on the floor.
- **Internal docs spanning multiple prospects** (Open Design Q) — e.g. Kyle's Apr 8 Warranty Prep covering Amynta + Fair + Armadillo. How do these attach in the entity graph?

---

## Open design questions (still open, carried from prior sessions)

Five carried forward from Sessions 9-11. None resolved this session. All belong to main session work, with Craig:

1. **Opportunity vs Problem entity** — does unmapped pain need its own entity? Source: `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` § Topic 2.
2. **Document-as-artifact pattern for emails** — drafted email lives where? Email entity with `status: drafting`? Document with `mime_type: message/rfc822`? Hybrid?
3. **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle's Apr 24 ask).
4. **Origin / referrer tracking** (Pat Klene → GR Little, Matan → David → Armadillo example).
5. **Playbook hydration mechanism** — how Playbook records refine from observed patterns over time.

---

## Recent OS commits to indemn-os main (Session 12)

- `8141a80`, `2ba6f63` — Bug #35 stacked fixes (deepagents skill discovery: absolute path + YAML safe_dump). **No longer load-bearing** after the subsequent layer-drop refactor below.
- **`7281b83` — `refactor(harness): load skills via CLI in DEFAULT_PROMPT, drop deepagents skills layer`.** The canonical skills-loading pattern is now: agent runs `execute('indemn skill get <name>')` (system-prompt directive), skill content arrives as tool result on turn 1, stays in agent message history. The deepagents `skills=[...]` parameter, SKILL.md filesystem layout, and `SkillsMiddleware` are dropped. Eliminates Bug #35 class entirely.
- `477a98f` — Bug #36 (Gmail/Calendar `fetch_new` adapters: explicit param plumbing, replaces `**params` with `**unknown_params` raising `AdapterValidationError`)
- `3fc4b55` — Bug #36 propagation to Outlook adapter
- `a5aa89f` — Bug #37 (Email list endpoint: opt-in tolerance via `_DomainQuery.to_list(skip_invalid=False)`)

Plus prior cumulative work from Sessions 10-11 (LangSmith, Bug #34 CLI fix, completion check tightening).

---

## What just shipped (this hydration-redesign thread of Session 12)

- `customer-system/CLAUDE.md` — rewritten as comprehensive shared-mind doc (what we're building / how / why / architecture / journey / foundations / best practices / index)
- `customer-system/CURRENT.md` — this file (NEW)
- `customer-system/SESSIONS.md` — append-only per-session log (NEW)
- `customer-system/PROMPT.md` — session-start prompt template (NEW)
- `docs/plans/2026-04-28-shared-context-hydration-design.md` — design doc

**Test:** the next session spun up uses `PROMPT.md` as kickoff. If shared mental model arrives intact in ~95K tokens (down from ~500K) and execution begins without re-litigation, the design works. Iterate on what goes in CLAUDE.md / CURRENT.md if something load-bearing got cut.

---

## Next session — likely focus

If TFG / John Scanland brain dump comes back from Kyle: trace TFG end-to-end as the second new-prospect trace post-Hard-Rule-#1-inversion. Different stage / different shape than Armadillo would surface more design gaps and validate the autonomous flow on a second customer.

Otherwise: pick up one of the High-priority new design gaps (Deal-lifecycle automation gap is the most directly impactful — it's why Deal creation in the Armadillo trace had to be done manually). OR pick up Bug #36 cleanup (500 emails + 6 meetings) if accept-fix-forward isn't the chosen path.

Open design questions remain available for brainstorm if Craig wants to advance one of those.

---

*This file is rewritten every session. Don't append — replace. The history lives in SESSIONS.md.*
