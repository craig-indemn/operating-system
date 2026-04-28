---
ask: "Comprehensive load-bearing session-handoff artifact for the customer-system project. This is the SINGLE STARTING POINT for the next session. It hard-codes the two-track reading list (project artifacts + OS docs) so the next session does not skip Track 2 — a discipline failure that happened this session and the prior one. Captures Sessions 8 + 9 state, the Phase B1 progress, the kill-switch finding, the open work + open questions, and the canonical reading order. Read this in full before any work in the next session."
created: 2026-04-28
workstream: customer-system
session: 2026-04-28-b1-entity-resolution
sources:
  - type: local
    ref: "projects/customer-system/INDEX.md"
    description: "Status section + Decisions log + Artifacts table updated end-of-session 9"
  - type: local
    ref: "projects/customer-system/CLAUDE.md"
    description: "Session 9 entry added to journey; Where we are now updated"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-28-phase-b1-data-state-and-trace-plan.md"
    description: "Phase B1 working plan with execution decisions log"
  - type: local
    ref: "projects/customer-system/os-learnings.md"
    description: "3 new bugs logged from this session (silent-stuck regression, polymorphic Option B, list filter regression)"
---

# Session 9 Handoff — Phase B1 entity-resolution + reactivation kill-switch

> ⚠️ **READ THIS DOCUMENT IN FULL FIRST. THEN READ THE TWO-TRACK LIST IN SECTION 1 IN FULL. THEN BEGIN WORK.**
>
> The discipline failure mode this session: prior session-start prompts listed only the project files (Track 1), Claude trusted that list as exhaustive instead of cross-checking against CLAUDE.md's REQUIRED READING block which mandates BOTH tracks. The result: the OS-side bug findings in this session would have come faster + cleaner if the OS docs had been loaded up front.
>
> **Section 1 below is the non-negotiable reading list. Do not skip Track 2.**

---

## 1. MANDATORY READING — both tracks, in this order

Both tracks are required. Reading only one is a discipline violation. The customer system is a build ON the OS — you cannot do competent work in either without the other.

### Track 1 — This project (customer-system)

Read in this order. Each path is absolute.

1. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/CLAUDE.md` — orientation, vision, journey (read Sessions 6/7/8/9 entries carefully — the Session 9 entry below is the current state), foundational design principles (#20 trace-as-build is the operating method), files index, when-working-on-X router, cadence/discipline.
2. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/INDEX.md` — Status section (Session 9 entry at top), Decisions log, Open Questions, full Artifacts table.
3. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/vision.md` — slow-changing end-state. Section 4 captures the trace-as-build principle.
4. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/roadmap.md` — current "Where we are now"; Phase B preamble has the building-method note.
5. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/os-learnings.md` — fork session's queue + customer-system findings. Three new bug entries from this session.
6. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-28-session-9-handoff.md` — this file.
7. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-28-phase-b1-data-state-and-trace-plan.md` — Phase B1 working plan; the decisions log captures the execution sequence including the kill-switch finding.
8. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-27-session-handoff-alliance-trace.md` — Session 6 handoff (background context for Phase A's close).
9. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-27-alliance-trace.md` — Phase A2 trace narrative; useful for understanding the entity model in motion.
10. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-22-entity-model-design-rationale.md` — WHY the entity model is shaped this way; the Alliance test.
11. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-23-playbook-as-entity-model.md` — load-bearing insight (entities ARE the playbook).
12. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` — architectural refinements (Playbook consulted twice; Proposal-as-spine).
13. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-22-entity-model-brainstorm.md` — field-level entity specs.

### Track 2 — The OS (the platform you are building ON)

Track 2 is mandatory. The customer system is a domain modeled on the OS — these docs explain what the OS is and how it works. **Reading only Track 1 produces work that fights the OS instead of leveraging it.** Read in this order. Each path is absolute.

1. `/Users/home/Repositories/indemn-os/CLAUDE.md` — OS builder's manual. Compact reference.
2. `/Users/home/Repositories/indemn-os/README.md` — top-level OS orientation, what's running, repo structure.
3. `/Users/home/Repositories/indemn-os/docs/white-paper.md` — canonical OS vision. The full WHY.
4. `/Users/home/Repositories/indemn-os/docs/architecture/overview.md` — trust boundary, dispatch pattern, deployment topology.
5. `/Users/home/Repositories/indemn-os/docs/architecture/entity-framework.md` — `save_tracked()`, state machines, computed fields, self-evidence, schema migration.
6. `/Users/home/Repositories/indemn-os/docs/architecture/watches-and-wiring.md` — watches, conditions, scoping, message cascade, selective emission, the unified queue.
7. `/Users/home/Repositories/indemn-os/docs/architecture/associates.md` — actor model, skills, harness pattern, execution lifecycle, gradual rollout.
8. `/Users/home/Repositories/indemn-os/docs/architecture/rules-and-auto.md` — rule engine, lookups, capabilities, the `--auto` pattern.
9. `/Users/home/Repositories/indemn-os/docs/architecture/integrations.md` — adapters, credential resolution, webhooks.
10. `/Users/home/Repositories/indemn-os/docs/guides/domain-modeling.md` — the 8-step process with worked examples.

After both tracks, read activity-specific files via the **"When working on X"** router in `CLAUDE.md` — for the current Phase B1 entity-resolution work, the router points at the playbook + design-dialogue + entity-model artifacts (already in Track 1 above) plus the os-learnings critical/blocking section.

### Coverage check (do this before claiming reading is done)

Answer the following before starting work. If you can't, you haven't read enough.

- **Track 1:** Where is the trace-as-build-method articulated, and what's its content_hash equivalent across vision/CLAUDE/roadmap? (Hint: vision §4, CLAUDE #20, roadmap Phase B preamble.) What does the Phase B1 plan artifact's decisions log say happened during reactivation B1.5? (Hint: kill switch fired on Diana@CKSpecialty's email.)
- **Track 2:** What does `save_tracked()` do in a single transaction? What are the three event types that trigger selective emission? What does `--auto` mean? What is the trust boundary? Why is the kernel domain-agnostic?

If you can answer these without re-reading, the reading is loaded. Begin work.

---

## 2. State of the project at end of Session 9

### What just shipped (Session 9, 2026-04-28 afternoon)

- **Trace-as-build-method principle** captured durably — CLAUDE.md #20, vision.md §4, roadmap.md Phase B preamble. Every skill/watch/capability/dashboard goes through a trace first before activation. Discovered as Phase A's shake-out method, elevated to canonical building method for all of Phase B+.
- **Phase B1 plan artifact** built (`artifacts/2026-04-28-phase-b1-data-state-and-trace-plan.md`, 404 lines) — live OS state inventory, structural gaps, Path A cleanup pass, trace plan B1.1 → B1.7, explicit out-of-scope list, decisions log + checklist.
- **Path A cleanup executed cleanly:**
  - Activated `entity_resolve` on Contact (email + name strategies)
  - Added `domain` strategy to Company `entity_resolve` (alongside the existing name + fuzzy-name)
  - Bulk-deleted **79 orphan Companies** (Companies 314 → 235)
  - Resolved **91 high-volume Contact dupes** across 10 groups (Contacts 424 → 333)
  - Reclassified 10 Email.sender_contact references to canonicals via API before delete (clean audit trail)
- **Phase B1 trace through 3 scenarios** acting as Email Classifier on real emails:
  - S1 — known Contact + known Company (jli@levelequity.com): clean classification ✅
  - S2 — new Contact at known Company (brian.coburn@stratixadvisory.com): Contact created, classified ✅
  - S3 — truly new domain (j.kamrath@quadient.com): needs_review (no auto-create Company) ✅
  - Inline cleanup of LE × 4 + Justin Li × 3 dupes the trace surfaced (these were below the volume threshold of A3)
- **Email.interaction → Email.touchpoint rename completed as ROOT-CAUSE FIX** (not a workaround — Craig pushed back hard on workaround language in TS skill v4):
  - `indemn entity migrate Email --rename "interaction touchpoint"` migrated 1139 Email documents
  - `PUT /api/entitydefinitions/Email/modify` updated `relationship_target` from `Interaction` to `Touchpoint`
  - All 26 entity definitions audited — only Email had the leftover
  - The `interactions` MongoDB collection kept (it's the kernel chat/voice session log; different entity; IDs do not overlap with `touchpoints`)
- **Three skills updated and deployed:**
  - **Email Classifier v3** (`content_hash 4f35d9ffb5a6e273`) — resolve-before-create with explicit decision tree (single 1.0 / multi 1.0 / fuzzy / 0 outcomes), "Never auto-create Company" rule, irrelevant detection, valid `how_met` enum values
  - **Touchpoint Synthesizer v6** (`content_hash 8e7847c8b329f6ba`) — Step 1a idempotency check via `Email.touchpoint` back-reference (catches manual-trace dupes + reprocess-replay dupes), domain-gated Contact auto-create, Option B source pointers mandatory
  - **Intelligence Extractor v3** (`content_hash b65cee8d4064a30e`) — explicit two-step Option B navigation (no `--include-related` since `source_entity_id` is polymorphic), mandatory Touchpoint transition to `processed` at end (every time), investor/partner-side rule (Signals only)

### Reactivation B1.5 — kill switch fired

Reactivated Email Classifier and reprocessed Diana@CKSpecialty's email via the Apr 27 reprocess primitive. EC processed 4 messages during the brief activation:
- Email A (Justin Li, single 1.0 match for Contact + Company): clean classification ✅
- Email B (Kyle / Alliance, internal classification): classified to Alliance Company; sender_contact null (defensible — Kyle is an Employee not Contact)
- Email C (Diana@CKSpecialty.com, multi-candidate case — 2 1.0 Contacts + 1 1.0 Company by domain): **VIOLATED THE SKILL RULE**. Auto-created a NEW Company despite "Never auto-create a Company" being explicit. Did NOT mark needs_review on multi-match ambiguity. Did NOT transition the email.

**Kill switch:** Suspended EC immediately. Rolled back the auto-created Company `69f0df1bbca2d725ce90ed58`. Reset Diana's email to `received` with no Company / Contact links. Verified the v3 skill content IS in the database (correct content_hash, "Never auto-create" + "Multiple 1.0 candidates → needs_review" both present).

**Conclusion:** Skill content is correct in the DB. The agent has a **skill-compliance gap on the harder multi-candidate branch**. This is research-level — needs deeper investigation before reactivation. Possible remedies:
- **More explicit decision-tree language** in EC skill — break out multi-candidate into named outcome with example
- **Force-reasoning veto rule** that catches any Company create from EC entirely — deterministic guard rail. Per the OS rules-and-auto pattern, a `force_reasoning` rule with conditions matching "EC actor + Company creation" would block all Company creates without exception.
- **Eval-driven testing** — build a compliance test set covering multi-candidate scenarios, run evaluations against EC v3, fine-tune skill content based on failure modes.

Likely all three in combination.

### Bugs reported to os-learnings.md (queued for the bugfix fork)

1. **Silent-stuck-state regression** (🟡 Partial regression). The Apr 27 `agent_did_useful_work()` helper has a coverage gap — when an agent makes read-only `indemn` calls AND ends with "nothing to extract" final content, the message marks completed even though the entity wasn't transitioned. Surfaced when IE ran on the manual Touchpoint `69f0d8cbbca2d725ce90ed0f`: message went create → completed in 18 seconds, 0 entities created, Touchpoint stuck at `logged`. Hypothesis for proper fix: check expected entity transition in the cascade — if the watched entity's state didn't change AND no child entities were created, fail (or at minimum log a warning with `last_error`).
2. **`--include-related` does not follow polymorphic Option B `source_entity_id` refs on Touchpoint** (🟡 Workaround in skill). The field has `is_relationship: false` because the target type is polymorphic (Email | Meeting). The kernel's `--include-related` only follows fields with `is_relationship: true` and a fixed `relationship_target`. Worked around in IE skill v3 by explicit two-step navigation. Long-term kernel option: support polymorphic relationships — `is_polymorphic_relationship: true` with `target_type_field: "source_entity_type"`.
3. **List endpoint filter regression** (🟡 Regression). The Apr 27 list-endpoint `_parse_list_filter` fix appears to have regressed for non-relationship fields. `GET /api/touchpoints/?data={"source_entity_type":"Email"}` returns Touchpoints with `source_entity_type: null` — filter silently ignored. Even unknown-field filters return 200 (the "400 with known-fields list" behavior the original fix promised isn't happening). Workaround: prefer back-reference fields for idempotency checks.

### Pipeline associates current state

| Associate | Status | Skill version | Triggered autonomously this session? |
|---|---|---|---|
| Email Classifier | **suspended** (kill switch from B1.5) | v3 | Yes — 4 messages, 1 violation, suspended |
| Touchpoint Synthesizer | **suspended** (unchanged) | v6 | No |
| Intelligence Extractor | **active** (untouched) | v3 | Yes — 1 message on the manual Touchpoint, silent-stuck (no transition) |

---

## 3. What's next — start of Session 10

The natural next priority is closing the EC skill-compliance gap. Until that's resolved, broad reactivation is unsafe. Options:

### Option A — More-explicit skill language

Iterate on EC skill content. Make the multi-candidate branch impossible to misread. Examples to consider:
- Restructure decision tree into a numbered checklist instead of narrative bullets
- Add explicit "do this NOT that" pairs for the multi-candidate case
- Add a worked example specifically for multi-candidate
- End the skill with a one-line rule reminder: "When uncertain → needs_review. Never create."

Test by running `reprocess` on a single multi-candidate email after the skill update. Iterate until the agent complies.

### Option B — Force-reasoning veto rule

Per OS rules-and-auto: create a `force_reasoning` rule that vetoes any Company create attempt by EC. Deterministic guard rail — kernel-enforced, not agent-discretion.

This requires:
- Activating `auto_classify` capability on Company
- Writing a rule with conditions matching "actor is Email Classifier" → action `force_reasoning`
- Verifying the rule fires before any Company create
- Surfacing the veto reason back to EC so it knows to mark `needs_review`

This is the strongest guardrail but requires kernel-level work — needs research on whether the existing rule engine supports actor-based conditions on creation operations.

### Option C — Eval-driven testing

Build an evaluation set of 20-30 multi-candidate scenarios. Run EC v3 against the eval set, measure rule-compliance rate, iterate skill content. This is the right long-term answer but heaviest lift.

### Recommended sequence

1. **Start with Option A** — fast iteration cycle, low risk
2. If A doesn't reach 100% compliance: move to **Option B** (deterministic guard) for high-stakes operations like Company create
3. **Option C as background work** — build eval set in parallel, use to validate before reactivation

### Other carry-over work

- **Document entity sync** — set `drive_file_id: "1pM3tYg6rHzG8RW6xU_titouiq_iddhIC"` + `drive_url: <Drive URL>` on Document `69efbdea4d65e2ca69b0dd80`. Quick CLI update.
- **Watch for Cam + Kyle reactions** in MPDM `mpdm-cam--kwgeoghan--craig-1` (channel `C0A3B18LY07`) — proposal feedback informs whether v2 ships to Christopher; Kyle's reactions on the showcase inform whether/how to socialize internally.
- **Slack ingestion** (Phase B continuous) — surfaced as foundational by the Apr 27 Alliance trace; deferred from B1 but real work needed.
- **Bug #30 propagation** to Email.external_ref + audit other entities — moved to bugfix fork queue; not customer-system work.

---

## 4. The "do not skip" reminders

Things that bit us this session and the prior one — codified so they don't bite again.

1. **Do not skip Track 2 OS reads.** The discipline failure today: Craig's session-start prompt listed Track 1 only; Claude trusted that list as exhaustive. If your session-start prompt only lists Track 1, **STOP and read Track 2 anyway**. CLAUDE.md is the canonical reading authority, not the session-start prompt. (See Section 1 above for the full list with absolute paths.)
2. **Do not skip the Kyle transcript when designing things Kyle has opinions about.** The Apr 24 Kyle sync transcript at `artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt` is mandatory before any work touching dashboards, stages, sales pipeline, or visual artifacts intended for Kyle.
3. **Do not write workarounds when root cause is fixable.** This session caught me writing "Don't attempt the back-reference until the rename ships" into the TS skill — that was a workaround for an unfixed customer-system bug. Craig pushed back. The right move was to FIX the rename, then write the skill describing the system as designed. CLAUDE.md principle #12 + memory `feedback_understand_before_fix.md` cover this.
4. **Do not propose "recommendations" — propose plans.** Earlier this session I proposed "next move: entity-resolution skill propagation" as a recommendation without inventory, design, or sequencing. Craig pushed back. The right move was to inventory live data state, identify gaps, propose a structured plan, get alignment, then execute. The Phase B1 plan artifact is the result of that correction.
5. **Trace-as-build-method is not optional in Phase B+.** Every skill/watch/capability/dashboard goes through a trace first. The skill is the writeup of what worked, not the design ahead of validation. Captured durably in CLAUDE.md #20, vision §4, roadmap Phase B preamble.

---

## 5. Open design questions carried forward

Not blocking next session but worth holding in mind:

- **Skill compliance** (NEW from this session) — what's the right durable mechanism to enforce skill rules at the boundary the agent can't override? Force-reasoning rules? Pre-flight checks via capabilities? Schema-level constraints?
- **Opportunity vs Problem entity** — does unmapped pain need its own entity, or does Opportunity loosen `mapped_associate` to nullable?
- **Document-as-artifact pattern for emails** — Email entity, Document entity, or hybrid? Proposal→Document already designed; emails need resolution.
- **Stages** — 12 sub-stages with multi-select for archetypes (Kyle's Apr 24 ask). Open design.
- **Origin / referrer tracking** (Pat Klene → GR Little example) — field on Deal or new Introduction entity?

---

## 6. The shape of this handoff

This is the handoff template I should have written for Sessions 7 + 8 too. The pattern:

- Mandatory reading list — both tracks, absolute paths, in order, with a coverage check
- State-of-project — what landed this session
- Critical findings — bugs + gaps that can't be missed
- What's next — concrete options for the immediate next priority
- Do-not-skip reminders — codified discipline
- Open design questions
- Self-reference — the handoff IS the load-bearing knowledge transfer

Future sessions: write a handoff like this at the end of every substantive session. The Session 6 handoff (`artifacts/2026-04-27-session-handoff-alliance-trace.md`) is the prior canonical example; this Session 9 handoff continues the lineage.

---

End of Session 9 handoff. Next session begins with the mandatory reading list in Section 1, in full, no skipping.
