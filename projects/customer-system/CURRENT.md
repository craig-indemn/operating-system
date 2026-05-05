# Customer System — CURRENT

> **Fast-changing state.** What just happened, what's in flight, parallel sessions, blockers, next steps. Rewritten every session. Read this *after* CLAUDE.md to know where things actually stand right now.

**Last updated:** 2026-05-05 (end of Session 18 — pre-TD-2 OS hardening sprint complete; all 5 Tier 1 items shipped + deployed + verified end-to-end; 514 unit tests pass; os-learnings.md badge audit done; indemn-os CLAUDE.md updated with bulk_save_tracked + diagnose docs).

---

## ACTIVE PARALLEL WORKSTREAMS

### Workstream A — Pricing Framework (unchanged from Session 17)

**Status:** Phase D in progress. Visual v6 generated from full staging JSON. Separate worktree at `.claude/worktrees/gic-feature-scoping/`. Not touched this session.

Resume protocol in `artifacts/2026-04-30-associate-pricing-framework.md` §0 Session Handoff.

### Workstream B — Pre-TD-2 OS hardening COMPLETE; TD-2 cascade activation NEXT

**Session 18 shipped all 5 Tier 1 items + Tier 1.5 badge audit.** Foundation is clean for TD-2.

---

## Top of roadmap

**TD-2 cascade activation begins next session.** Pre-TD-2 hardening sprint is done. All blockers resolved.

**What TD-2 delivers:** 7-associate cascade running autonomously on incoming Email/Meeting/Slack data. Every interaction flows through classification → Touchpoint → extraction → Proposal hydration.

**TD-2 execution plan (per roadmap.md § TD-2):**
1. MeetingClassifier (MC) — NEW. Trace on Armadillo's Apr 28 discovery meeting first.
2. SlackClassifier (SC) — NEW. Trace on Apr 7-8 Retention Associate Slack thread.
3. EC v9 → v10 — signature parsing + ReviewItem on ambiguity.
4. TS v6 → v7 — Deal-creation + Proposal-at-DISCOVERY atomic + multi-Deal ambiguity → ReviewItem.
5. IE verification through full cascade with TS-created Touchpoints + Option B.
6. Proposal-Hydrator (PH) — NEW. Trace on Armadillo's processed Touchpoints.
7. Company-Enricher (CE) — NEW. Trace on Armadillo's bare Company.
8. Activate bottom-up; done-test = systematic historical replay.

**Trace-as-build-method per CLAUDE.md § 2** — for each new associate: pick real scenario, trace manually via CLI, verify entity state, write skill from what worked, activate after trace produces correct state on real data.

---

## Pipeline associate states (Session 18 close — unchanged from Session 17)

| Associate | State | Notes |
|---|---|---|
| Email Classifier (EC) | **suspended** | Will activate in TD-2 (v9 → v10). |
| Touchpoint Synthesizer (TS) | **suspended** | Will gain Deal-creation in TD-2 (v6 → v7). |
| Intelligence Extractor (IE) | **active** | Inherits gemini-3-flash-preview/global. Will verify through full cascade in TD-2. |
| Email Fetcher | **active, mode=cron_runner** | Skill v5 with limit:100. Now uses bulk_save_tracked. |
| Meeting Fetcher | **active, mode=cron_runner** | Skill v4. Completing cleanly. |
| Drive Fetcher | **active, mode=cron_runner** | Skill v4. Completing cleanly. |
| Slack Fetcher | **active, mode=cron_runner** | Skill v4. Completing cleanly. |
| Voice OS Assistant | **active** | log-touchpoint skill v3. |
| Reviewer role | wired | Ready for TD-2. |

**4 NEW associates to build in TD-2:** MeetingClassifier, SlackClassifier, Proposal-Hydrator, Company-Enricher.

---

## What just shipped (Session 18)

All 5 Tier 1 OS hardening items:

1. **`bulk_save_tracked()`** — `kernel/entity/save.py`. Replaces sequential per-entity save loop in fetch_new. Single insert_many(ordered=False) + in-memory hash-chained change records + batched watch evaluation. Partial failure preserved. 12 tests.

2. **`indemn diagnose` command group** — `indemn diagnose actor <id>` (recent runs + outcomes), `indemn diagnose message <id>` (full lifecycle), `indemn diagnose cron <name>` (last N ticks). API at `/api/_diagnose/*`. Verified end-to-end. 12 tests.

3. **List endpoint `--data` filter** — CLI was missing the flag. Added `--data` to list command → passes as `?filter=` param. Bogus fields → 400 with known fields. 4 tests.

4. **Polymorphic `--include-related`** — `is_polymorphic_relationship` + `target_type_field` on FieldDefinition. `_build_related_entities` resolves target type at runtime. Touchpoint entity def activated. 5 tests.

5. **Employee `entity_resolve`** — activated with `field_equality` on email + `lowercase_trim`. Verified: Kyle@indemn.ai → score 1.0.

Plus: os-learnings.md 7 rows updated; indemn-os CLAUDE.md documented bulk_save_tracked + diagnose commands.

---

## Indemn-os commits this session

| Commit | What |
|---|---|
| `d1f695a` | feat(kernel+cli): pre-TD-2 OS hardening sprint (all 5 items + 33 tests) |
| `12ce818` | fix(diagnose): resolve role_ids → Role.name |
| `0e95ea5` | fix(diagnose): use Message.claimed_at not completed_at |
| `d746ea4` | docs: document bulk_save_tracked + diagnose commands in CLAUDE.md |

---

## Next session — TD-2 cascade activation

**Use `PROMPT-2026-05-05-td2-cascade.md` as the kickoff prompt.**

Start with MeetingClassifier on Armadillo's Apr 28 discovery meeting per trace-as-build. Multi-session work; close cleanly per session.

---

*This file is rewritten every session. Don't append — replace. The history lives in SESSIONS.md.*
