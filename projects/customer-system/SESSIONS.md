# Customer System — SESSIONS

> **Append-only log of session objectives + outcomes.** New entries at the **top**. Each session adds one entry at end of session. Loaded on-demand when a session needs to look back at history or learn the objective-statement format from prior entries.
>
> The full Journey lives in `CLAUDE.md § 5`. This file is the lighter-weight per-session log.

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
