# Customer System — SESSIONS

> **Append-only log of session objectives + outcomes.** New entries at the **top**. Each session adds one entry at end of session. Loaded on-demand when a session needs to look back at history or learn the objective-statement format from prior entries.
>
> The full Journey lives in `CLAUDE.md § 5`. This file is the lighter-weight per-session log.

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
