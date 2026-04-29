# Customer System — CURRENT

> **Fast-changing state.** What just happened, what's in flight, parallel sessions, blockers, next steps. Rewritten every session. Read this *after* CLAUDE.md to know where things actually stand right now.

**Last updated:** 2026-04-29 (end of Session 13 — comprehensive roadmap alignment; TD-1 ready to execute next)

---

## Top of roadmap

**Phase A complete (Session 6-8). Phase B1 substantially de-risked (Session 12). Roadmap now restructured as 11 Tangible Deliverables (TD-1 through TD-11) with Session 13 alignment.** TD-1 is the next attack target.

The roadmap restructure happened in Session 13: same vision, same work, different organization. Replaced foundation-phase framing (A→F) with tangible-deliverable framing because the phases were fuzzy on what's tangibly shipped to whom; the TDs make it explicit. TD-1, TD-2, TD-3 detailed at full fidelity (~170-280 lines each). TD-4 through TD-11 detailed at structural fidelity (~30-70 lines each — sufficient to start work; deeper detail filled in when each TD is approached).

Total roadmap: ~1100 lines of comprehensive design.

---

## Pipeline associate states

Unchanged from Session 12. No autonomous activation has happened yet.

| Associate | State | Skill version | Notes |
|---|---|---|---|
| Email Classifier (EC) | **suspended** (kill switch held; v9 in DB ready, content_hash `9eef4959ae701614`) | v9 | Hard Rule #1 inverted (resolve-before-create > never-auto-create); verified live on Armadillo's first-contact email. Will be augmented in TD-2 with signature parsing and ReviewItem creation for ambiguity. |
| Touchpoint Synthesizer (TS) | **suspended** (unchanged) | v6 (`8e7847c8b329f6ba`) | Will gain Deal-creation in TD-2 (atomic with Touchpoint creation when scope=external + no active Deal); will create empty Proposal too. Internal-scope multi-Deal ambiguity → assigns to latest + creates ReviewItem. |
| Intelligence Extractor (IE) | **active** (untouched) | v3 (`b65cee8d4064a30e`) | Silent-stuck-state regression fixed (Session 10). Verified on Armadillo extracting 14 entities. |

**4 NEW associates designed in Session 13's TD-2 alignment** — to be built when TD-2 executes:
- **MeetingClassifier (MC)** — classifies Meetings (resolve attendees, identify Company, scope)
- **SlackClassifier (SC)** — classifies Slack threads (channel-context-aware, relevance filter)
- **Proposal-Hydrator** — aggregates extracted entities into the Proposal entity (stages-are-fluid logic; ReviewItem when extraction doesn't fit)
- **Company-Enricher** — fills bare Companies over time (event + scheduled triggers)

**Plus the ReviewItem entity** designed in Session 13 — universal escape valve for human review (any associate creates one when uncertain; never blocks; reviewing IS training data).

---

## Material state in dev OS

**Hydrated customer constellations** (carried forward from Session 12):
- **GR Little** — Kyle validated 2026-04-24
- **Alliance Insurance** — Kyle + Cam shared 2026-04-28; v2 PDF in Cam's Drive folder
- **Armadillo Insurance** — first new-prospect trace post-Hard-Rule-#1-inversion (Apr 29, Session 12)
  - Company `69f22186…444d` + Deal `69f223cc…4470` + 2 Contacts (Matan Slagter CEO, David Wellner COO) + 2 Touchpoints + 14 extracted entities

**Cleanup pending (TD-1 pre-flight before any cascade activation):**
- 500 unrelated Emails + 6 unrelated Meetings on Kyle's mailbox from Bug #36 side-effect — **bulk-delete** (clean slate per Craig's call)
- 2 malformed Email rows from Bug #37 data side (`69ea548e…6e92` Oneleet, `69ea556f…7387` Linear Orbit) — **delete**

**Diana@CKSpecialty test entity** (carried forward from Sessions 9-12): Email `69ea56250a2b41b7696076b3`, state `received`, no Company/Contact links. Available as a TD-1/TD-2 verification target.

---

## Parallel sessions

**Session 13 ran in this worktree.** No active parallel sessions during Session 13's roadmap-alignment work.

When TD-1 execution begins next session, the parallel-session model returns:
- Main session: TD-1 work (per-TD execution per the trace-as-build method)
- Parallel sessions for OS bug fixes that surface (per the OS bug convergence continuous thread)
- Optional parallel session for TFG / John Scanlon trace if Kyle's brain dump returns

---

## Blockers

None. Worktree clean. All architectural decisions for TD-1 → TD-3 made; TD-4 → TD-11 structurally aligned. Ready to execute TD-1.

---

## What just shipped (Session 13)

**Comprehensive roadmap alignment.** Same vision, same work, fundamentally restructured for clarity + execution.

- **Roadmap restructured** as Tangible Deliverables (TD-1 through TD-11) replacing the prior Phase A → F structure
- **TD-1 detailed** (~180 lines) — 4 source adapters + 4 scheduled fetcher actors + manual entry via per-actor assistant. Per-event Touchpoints (1:1 with source-events). Slack adapter NEW build (direct API, all channels, no DMs initially). Drive pull-all + lazy-classify. Pre-flight Bug #36/#37 cleanup.
- **TD-2 detailed** (~170 lines) — 7-associate cascade (EC, MC, SC, TS gains Deal-creation, IE, Proposal-Hydrator, Company-Enricher) + ReviewItem universal-escape-valve pattern. Bottom-up activation order. Done-test = systematic historical replay through cascade chronologically.
- **TD-3 detailed** (~280 lines) — React+Vite+shadcn UI matching Ganesh's repo conventions. 7 pages. Per-customer constellation page mirrors trace-showcase HTML 5-section spine (single-scrolling, inline timeline expand). Role-aware personalized dashboard with assistant prominent. Persistent assistant on every page.
- **TD-4 through TD-11 structural** (~30-70 lines each) — TD-4 conversational research (no auto-mining). TD-5 one Artifact Generator, Playbook-driven, multi-deployment. TD-6 special case for PROPOSAL. TD-7 system visibility (5 sub-pieces). TD-8 light onboarding. TD-9 evaluations three-source + LangSmith direct. TD-10 Commitment-Tracker (event + schedule + OS queue + Slack DM). TD-11 placeholder pointing at product-vision.

**Architectural decisions locked in** (full list in INDEX.md § Decisions; the load-bearing ones):
- Tangible-deliverable framing for roadmap
- 7-associate cascade architecture
- ReviewItem universal-escape-valve pattern
- Per-event Touchpoints (1:1 with source-events; threading is metadata)
- Hard Rule #1 inverted (already done in Session 12; reflected throughout)
- Slack: all channels, no DMs initially, direct Slack API, polling-then-Events-API
- Drive: pull all, lazy classification, Documents source-agnostic
- Manual entry via per-actor assistant + `log-touchpoint` skill (no special infrastructure)
- React+Vite+shadcn UI matching Ganesh's repo (audit during execution)
- Artifact Generator: one associate, Playbook-driven, both async + realtime deployments
- Drafted email = Email entity with `status: drafting`
- TD-9: LangSmith API directly for now; Path 3 kernel-adapter integration deferred to TD-11

---

## Open design questions (carried forward, none new from Session 13)

These mostly fold into TD-4's research session per the new alignment:

1. **Opportunity vs Problem entity** — surfaces from TD-4 research observing unmapped pain
2. **Document-as-artifact pattern for emails** — RESOLVED in TD-5 alignment (Email entity with `status: drafting`)
3. **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle's Apr 24 ask) — research-driven in TD-4
4. **Origin / referrer tracking** — surfaces from TD-4 research (Pat Klene → GR Little, Matan → David → Armadillo)
5. **Playbook hydration mechanism** — RESOLVED in TD-4 alignment (mostly static, conversational refinement)

---

## Recent OS commits to indemn-os main (carried forward, no new in Session 13)

Session 13 did not touch indemn-os. All OS work carried forward from Session 12:

- `8141a80`, `2ba6f63` — Bug #35 stacked fixes (skill discovery: absolute path + YAML safe_dump). **Now obsolete** — see `7281b83`.
- `7281b83` — `refactor(harness): load skills via CLI in DEFAULT_PROMPT, drop deepagents skills layer`. **Canonical skills-loading pattern: agent runs `execute('indemn skill get <name>')`; skill content arrives as tool result on turn 1.**
- `477a98f` — Bug #36 (Gmail/Calendar `fetch_new` adapters: explicit param plumbing)
- `3fc4b55` — Bug #36 propagation to Outlook adapter
- `a5aa89f` — Bug #37 (Email list endpoint: opt-in tolerance via `_DomainQuery.to_list(skip_invalid=False)`)

Plus prior cumulative work from Sessions 10-11 (LangSmith, Bug #34 CLI fix, completion check tightening).

---

## Next session — focus: TD-1 execution

**Use `PROMPT.md` as the kickoff prompt** with this objective slot:

> *Execute TD-1 — adapters running cleanly + historical hydration. Start with pre-flight cleanup (bulk-delete Bug #36's 500 emails + 6 meetings; delete Bug #37's 2 malformed Email rows). Create ReviewItem entity + Reviewer role (pre-flight infrastructure for TD-2). Then activate the four scheduled fetcher actors in bottom-up order: Email-Fetcher (5min), Meeting-Fetcher (15min, with 30-day backfill), Drive-Fetcher (hourly, with full crawl). The Slack adapter is a multi-session NEW build — start design + scaffold this session, finish in subsequent sessions. Verify each step manually before activating recurring. EC/TS/IE remain suspended — TD-1 does NOT activate the cascade. Touch all relevant docs at end of session per CLAUDE.md § 7. See `roadmap.md § TD-1` for full architecture detail.*

**Key TD-1 risks to watch:**
- Cascade-firing-before-ready: pre-flight cleanup MUST complete before any actor activation; otherwise EC/TS/IE (still suspended) stay safe but recurring fetch on dirty data is a mess
- Slack adapter is the largest NEW build — multi-session work; design first; OAuth integration; Slack API client; pagination; file attachment processing; SlackMessage entity definition
- Voice harness refinement (per Craig: not actually tested or used much) — likely needs work before push-to-talk manual-entry is reliable

**TD-1 done-test reminder** (full version in roadmap.md):
- All 4 fetcher actors active with their `trigger_schedule` running
- New entities flow in within configured cadence
- 30-day Meeting backfill complete; 90-day Slack backfill complete; full Drive crawl complete
- Bug #36/#37 cleanup verified
- Manual entry working via assistant `log-touchpoint` skill
- All entities sit at `received`/`logged` — cascade NOT activated

After TD-1 completes: TD-2 begins (cascade activation, progressive). TD-3 begins (UI build) in parallel once TD-2 has data flowing.

---

*This file is rewritten every session. Don't append — replace. The history lives in SESSIONS.md.*
