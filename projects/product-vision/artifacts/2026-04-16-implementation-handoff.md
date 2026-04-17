---
ask: "Master session handoff — so the next Claude instance has complete understanding of the entire OS project and the full path to vision-realized, not just one work stream. Covers every track of work required to take the vision to completion."
created: 2026-04-16
workstream: product-vision
session: 2026-04-16-b (end of)
sources:
  - type: audit-trail
    ref: ".audit/manifest.yml (104 files, 100% checked)"
    description: "Complete structured reading of all design artifacts + specs + code + infrastructure"
  - type: artifact
    ref: "All 2026-04-16 artifacts listed below"
    description: "Synthesis outputs from Pass 2/3/4 audit + Gate 0-2 decisions"
---

# THE Implementation Handoff — Taking the OS to Vision-Realized

**Written at end of session 2026-04-16-b as the primary entry point for any subsequent session working on the OS.**

**This is the master handoff.** The harness-specific handoff (`2026-04-16-harness-session-handoff.md`) is a drill-down for when you're working Track A (Gates 2-7). Read this file first.

---

## 1. What "Done" Looks Like

The end state: **The vision described in the canonical sources — the white paper (`2026-04-13-white-paper.md`), Craig's foundational thesis (`context/craigs-vision.md`), and the 40+ design artifacts they synthesize — is implemented exactly in `/Users/home/Repositories/indemn-os/`.** The vision map (`2026-04-16-vision-map.md`) is the post-audit reconciliation of all 104 source files into 23 subsystem sections — use it when you need quick cross-referenced synthesis, but the white paper + source artifacts are the canonical vision.

Every architectural claim in the vision has corresponding correct code. All 9 discrepancies in `2026-04-16-alignment-audit.md` are resolved. Phase 6 (Indemn CRM dog-fooding) and Phase 7 (GIC first external customer) are operational. The OS is running real insurance workloads.

**Definition of done per Craig (verbatim):**
> "Identify every single discrepancy so that we can ensure what is implemented matches the vision. That is the end objective: to have the vision being implemented exactly... I want to take this to actual completion — full implementation of the OS, making sure that everything that was identified gets resolved. The vision is completely developed."

---

## 2. Reading — Budget + 4-File Mandatory Set

> **Revised 2026-04-16 (post-context-burn).** The prior version of this section prescribed an 8-tier 10-hour reading plan culminating in "read all 104 audit notes." A session attempted it, hit 700K+ tokens, and had to clear context before starting work. That plan is rescinded. Do not re-read source artifacts that the vision map already synthesized. Do not read all 104 notes. The synthesis artifacts exist so you don't have to.

**Reading budget**: The 4 mandatory files below are ~100-120K tokens. Adding per-track artifacts brings any single track to ~150-200K. That's the ceiling before you touch code.

### Mandatory — 4 files, ~100K tokens, 20-30 minutes

1. **This file** (`2026-04-16-implementation-handoff.md`) — you're reading it now
2. **`2026-04-16-vision-map.md`** — synthesized design (23 sections). Covers the thesis, the 6 primitives, 7 kernel entities, all mechanisms, trust boundary, every subsystem, known gaps. Authored after reading all 104 source files. **This replaces reading the white paper + 10 design artifacts + 3 retraces + session checkpoints.** Trust it.
3. **`2026-04-16-alignment-audit.md`** — the 9 open discrepancies + priority-ordered fix path + Pass 4 verification table. Use this instead of re-deriving Finding 0 / 0b / D-04 / D-07 / D-08 / D-01 / minor items from source.
4. **`projects/product-vision/INDEX.md`** § Decisions — every 2026-04-16 entry. Approved gates G0.1-G0.5 and G1.1-G1.5, G1.3 refinements, harness hosting decision (Option 1 = 3 images), deletion irreversibility, Daytona reclassification, etc.

That's it to get oriented. Everything else is on-demand per track.

### Per-Track On-Demand Reading

Add these to the mandatory set depending on what you're doing:

| Track | Additional files |
|---|---|
| **A (harness, Gates 2-7)** | `2026-04-16-harness-implementation-plan.md` + `2026-04-16-async-harness-draft.md` + `2026-04-16-cli-update-flow.md` + `2026-04-16-harness-session-handoff.md` |
| **B (mechanism bugs)** | Alignment audit §§ 5.1-5.3 + `.audit/notes/Users_home_Repositories_indemn-os_kernel_entity_state_machine_py.md` + `..._kernel_rule_engine_py.md` + `..._kernel_changes_hash_chain_py.md` (only the 3 files being touched) |
| **C (D-01 doc)** | Alignment audit § 5.4 + `.audit/notes/Users_home_Repositories_indemn-os_kernel_entity_base_py.md` |
| **D (spec updates)** | Open the specific consolidated-spec sections being edited (Phase 2-3 §2.4, Phase 4-5 §4.7 and §5.3, `2026-04-13-infrastructure-and-deployment.md`, `2026-04-13-remaining-gap-sessions.md` repo structure) |
| **E (Phase 6 CRM)** | `2026-04-10-crm-retrace.md` + `2026-04-14-impl-spec-phase-6-7-consolidated.md` + `.audit/notes/` for the 9 CRM entities only when touched |
| **F (Phase 7 GIC)** | `2026-04-10-gic-retrace-full-kernel.md` + `2026-04-14-impl-spec-phase-6-7-consolidated.md` |
| **Deep-dive on an unfamiliar subsystem** | That subsystem's `.audit/notes/` file(s), on-demand — not preemptively |

### Source File Re-Read Policy — Strict

**Don't re-read source artifacts that the vision map synthesized.** The vision map exists so you don't have to. Only re-read a `projects/product-vision/artifacts/*.md` source artifact when:

- The vision map is genuinely ambiguous on a specific point blocking your work
- You're writing code that needs an exact quote or line number from the source
- A synthesis contradicts what you observe in code (trust current code, then update the synthesis)

Default: trust the synthesis. If you catch yourself reading source to "be thorough" when the vision map was clear, **stop** — you're burning context on work that's already been done.

**Don't re-read all 104 audit notes.** The audit infrastructure exists AS the inheritance mechanism. The vision map + alignment audit already synthesized the notes into their conclusions. Read individual notes only when:

- You need code-level detail for a specific file you're touching (e.g., read the `kernel/temporal/activities.py` note before editing that file)
- The vision map points you to a note explicitly
- You've exhausted the synthesis and still need the next layer down

**Anti-pattern alert**: If you find yourself saying "I should read everything to be thorough" or "I need the complete picture before I act" — stop. The synthesis artifacts ARE the complete picture. Reading deeper is triple-work, not rigor.

### Quick lookup — what to read WHEN for specific work

| When you're doing... | Beyond the baseline (Tiers 1-6), also read... |
|---|---|
| Track A (harness work) | Tier 7 items 31-34 + relevant code notes (kernel/temporal/*) |
| Track B (mechanism bugs) | Alignment audit §§ 5.1-5.3 + specific code file notes (state_machine.py, rule/engine.py, changes/hash_chain.py) |
| Track C (D-01 doc) | Alignment audit § 5.4 + shakeout findings note + kernel/entity/base.py note |
| Track D (spec updates) | Phase 2-3 + 4-5 consolidated spec notes + Track A artifacts |
| Track E (Phase 6 dog-fooding) | CRM retrace note (deep) + Phase 6-7 spec note + all 9 CRM entity references |
| Track F (Phase 7 GIC) | GIC retrace note (deep) + Phase 6-7 spec + transition section of remaining-gap-sessions note |
| Spec drift check | Pass 2 audit + any relevant design source note(s) |
| New architectural question not covered | Use systematic-audit skill with a scoped manifest + cross-reference matrix |

---

## 3. The Full Map of Work (6 Tracks)

Every track has a definition of done, an owner status, a dependency, and an artifact reference.

### Track A — Harness Pattern (Gates 2-7)

**Resolves**: Finding 0 + Finding 0b (2 structural discrepancies)

**Definition of done**: 3 harness images built (`indemn/runtime-async-deepagents`, `indemn/runtime-chat-deepagents`, `indemn/runtime-voice-deepagents`), deployed to Railway, agent execution migrated out of kernel, kernel code deleted per § 8 of `2026-04-16-async-harness-draft.md`, `grep -r "import anthropic" kernel/` returns nothing.

**Current status**: Gate 0 approved, Gate 1 approved (with G1.3 refinements), Gate 2 drafted and awaiting Craig's review.

**Pending approvals before code**: Q3 final lock (Pydantic AgentExecutionInput model), G2.1 (harness code), G2.2 (kernel dispatch rewiring). G2.3 (deletion) comes after verification.

**Reference artifacts**: `2026-04-16-harness-implementation-plan.md`, `2026-04-16-async-harness-draft.md`, `2026-04-16-harness-session-handoff.md`

**Unblocks**: Track E, Track F.

### Track B — Mechanism Bugs

**Resolves**: D-04 (state field detection fragile), D-07 (rule group status not enforced), D-08 (hash chain verification broken)

**Independence**: fully parallel with Track A. No dependency.

**Sub-tasks**:
- **B.1 — D-04 state field detection.** `kernel/entity/state_machine.py::_find_state_field` uses convention (`"status" | "stage"`) instead of `is_state_field` flag from EntityDefinition. Fix: kernel entities set `_state_field_name` class variable; primary path uses `is_state_field`. See alignment audit § 5.1.
- **B.2 — D-07 rule group status.** `kernel/rule/engine.py::evaluate_rules` checks `Rule.status == "active"` but not the rule's group status. Fix: add group lookup + status check. See alignment audit § 5.2.
- **B.3 — D-08 hash chain verification.** `kernel/changes/hash_chain.py::compute_hash` has serialization inconsistency despite improvements. Fix: focused debug session — test roundtrip with real MongoDB data. See alignment audit § 5.3.

**Scope**: all three are small focused fixes. Each ~1-2 hours of work + tests.

### Track C — Documentation

**Resolves**: D-01 (dual base class architecture undocumented in spec)

**Independence**: fully parallel with everything.

**Work**: Update `2026-04-14-impl-spec-phase-0-1-consolidated.md` to explicitly document the dual base class architecture (`KernelBaseEntity` + `DomainBaseEntity` + `_DomainQuery` wrapper) with rationale (shakeout commit 23fcf06 origin — fixes Findings 3 and 4). The code is correct; the spec just needs to catch up.

**Scope**: doc update, no code change.

### Track D — Spec + Infrastructure Artifact Updates

**Resolves**: the drift between consolidated specs and the (correct) harness pattern design.

**Independence**: should happen during Track A so specs align with new implementation.

**Sub-tasks**:
- **D.1 — Phase 2-3 consolidated spec**: update § 2.4 to place `process_with_associate` in async harness, not kernel. Remove `import anthropic` from spec code samples.
- **D.2 — Phase 4-5 consolidated spec**: update § 4.7 (assistant) to specify chat-harness pattern, not kernel endpoint. Update § 5.3 to include chat harness + async harness specs alongside voice.
- **D.3 — infrastructure-and-deployment.md**: add `indemn-runtime-async-deepagents` to the service table (it was dropped — see alignment audit § 2.3).
- **D.4 — white paper § 7 Service Architecture**: verify all 3 harness images are listed (probably correct, but verify).
- **D.5 — remaining-gap-sessions.md**: add `harnesses/async-deepagents/` to the repo structure (it was dropped alongside).

### Track E — Phase 6 (Indemn CRM Dog-Fooding)

**Resolves**: none of the 9 discrepancies — this is VISION REALIZATION.

**Dependency**: Track A complete (harnesses working). Indemn CRM requires chat-harness (CRM Assistant), async-harness (Meeting Processor, Health Monitor, Follow-up Checker, Weekly Summary Writer, personal syncs), and the `owner_actor_id` pattern working end-to-end.

**Blueprint**: `2026-04-10-crm-retrace.md` — 9 domain entities (Organization, Contact, Deal, Meeting, MeetingIntelligence, ActionItem, Interaction, HealthSignal, Note), 5 org-level integrations, 60 actor-level integrations (15 team × 4 types), 8 roles, 6 associates.

**Definition of done**: Indemn team uses OS-based CRM daily. Meeting intelligence extraction works. Personal email/Slack/Calendar syncs work. "What's the story with X?" queries work via CRM Assistant. Health scoring + action-item overdue detection runs.

**Acceptance test**: Ian runs a customer call, transcript gets processed by Meeting Intelligence Processor, action items get created with his ownership, follow-up-checker surfaces them the next morning via queue. All on the OS.

### Track F — Phase 7 (First External Customer — GIC)

**Resolves**: none of the 9 discrepancies — VISION REALIZATION.

**Dependency**: Track A complete + Track E proven (dog-fooding works). Optionally: Track B complete (bug fixes matter for customer confidence).

**Blueprint**: `2026-04-10-gic-retrace-full-kernel.md` — 7 entities (Email, Extraction, Submission, Assessment, Draft, Carrier, Agent), Outlook integration, 8 associates (Email Sync, PDF Extractor, Classifier, Linker, Assessor, Draft Writer, Stale Checker, Outbound Sender), ~5-7 roles.

**Definition of done**: GIC (Craig's customer) runs on the OS. Emails from @usli.com flow: sync → extract → classify → link → assess → draft → human review → send. Current GIC Email Intelligence bespoke system is superseded. Parallel run validated per transition design.

**Acceptance test**: real GIC email processes end-to-end on OS with result matching current bespoke system. Cutover decision made.

---

## 4. Execution Order

```
START
  ├── Track A (Gates 2-7, serial per harness)
  │    ├── Gate 2 (async harness) ──→ kernel code deletion (G2.3)
  │    ├── Gate 3+4 (chat harness) ──→ delete kernel/api/assistant.py
  │    └── Gate 5+6 (voice harness) ──→ voice ready
  │
  ├── Track B (parallel with A — small fixes)
  │    ├── B.1 D-04 state field
  │    ├── B.2 D-07 rule group status
  │    └── B.3 D-08 hash chain debug
  │
  ├── Track C (parallel with A — doc only)
  │    └── C.1 D-01 dual base class documentation
  │
  └── Track D (during A — spec updates)
       ├── D.1 Phase 2-3 spec
       ├── D.2 Phase 4-5 spec
       ├── D.3 Infrastructure artifact
       ├── D.4 White paper verification
       └── D.5 Gap sessions artifact

(After A, B, C, D complete)
  │
  ├── Gate 7 (post-implementation verification, run Pass 5 audit)
  │
  ├── Track E (Phase 6 — Indemn CRM dog-fooding)
  │    └── Per 2026-04-10-crm-retrace.md blueprint
  │
  └── Track F (Phase 7 — GIC first external customer)
       └── Per 2026-04-10-gic-retrace-full-kernel.md blueprint

END: Vision realized. OS running real insurance workloads.
```

Minor items (M-1 bootstrap org_id, M-2 seed org_id, M-3 org slug uniqueness) fit into Track B as small cleanups.

### First Action (post-reading)

After the 4 mandatory files, open **`2026-04-16-async-harness-draft.md`**. Review:
- §§ 6 (harness code: base image, cli.py, runtime.py, backend.py, agent.py, main.py)
- § 7 (kernel dispatch rewiring: ProcessMessageWorkflow, worker.py changes, queue_processor.py changes, load_actor activity)
- § 8 (kernel code deletion list — G2.3 irreversible)
- § 9 (6 verification groups)
- § 10 (open Q3 Pydantic AgentExecutionInput model + Q5 CLI extraction)

Output: brief confirmation of understanding (3-4 sentences: what you're reviewing, what gates are approved/pending, what Track A unblocks) + Gate 2 review with concerns and a proposal to approve G2.1 + G2.2. G2.3 approval comes after verification — do not propose it now.

Total expected turn: ~30K tokens of additional reading, one focused output. Tracks B, C, D can be dispatched to parallel work without blocking Craig's input.

---

## 5. Current Session State (What Happened in 2026-04-16)

For posterity — not re-litigating these, just documenting what was accomplished so the next session doesn't redo it:

### The audit (Pass 1 → 2 → 3 → 4)

- Pass 1 (2026-04-15 comprehensive audit) surfaced Finding 0 + flagged methodology gap.
- Pass 2 (2026-04-16 early) — 41 files, confirmed Finding 0 at spec + code + infra levels.
- Pass 3 (2026-04-16 mid) — extended to 104 files total. Every design artifact + every code file in scope + every infrastructure file.
- Pass 4 (2026-04-16 late) — verified every vision map claim against `/Users/home/Repositories/indemn-os/` code. Confirmed 9 open discrepancies + 8 subsystems clean.

### Artifacts produced (all in `projects/product-vision/artifacts/`)

| Artifact | Role |
|---|---|
| `2026-04-16-pass-2-audit.md` | Original Finding 0 confirmation |
| `2026-04-16-vision-map.md` | Authoritative design synthesis (23 sections) |
| `2026-04-16-alignment-audit.md` | Final discrepancy report (9 open) |
| `2026-04-16-harness-implementation-plan.md` | Track A governing plan + 7 gates |
| `2026-04-16-async-harness-draft.md` | Gate 2 implementation draft |
| `2026-04-16-cli-update-flow.md` | `indemn-os` package strategy |
| `2026-04-16-harness-session-handoff.md` | Track A drill-down |
| `2026-04-16-implementation-handoff.md` | THIS FILE — master handoff |

### Audit infrastructure

- `.audit/manifest.yml` — 104 files catalogued, 100% checked
- `.audit/notes/*.md` — 104 structured notes
- `.audit/cross-reference-matrix.md` — layer/location declarations from all notes
- `.claude/settings.local.json` has `synthesis-gate` hook (now inactive since manifest 100%)

### Gate decisions locked

- G0.1-G0.5 all approved (Railway, shared base image, repo structure, tagging, CI pipeline)
- G1.1-G1.5 all approved with G1.3 refinements (LocalShellBackend MVP / Daytona prod, both marked, switched via env var)
- Q1-Q5 answered (Q3 awaiting final lock, others confirmed)
- Package = `indemn-os` on internal PyPI, binary = `indemn`
- Not extending NPM `indemn-cli` (different tool)

All rationale in INDEX.md 2026-04-16 entries.

---

## 6. Rules for the Next Session

### DO

- **Read the reading sequence in § 2 before any work.** Tier 1-6 minimum for baseline. Tier 8 (all 104 notes) alongside Tier 3-5. This is non-negotiable — Craig's explicit requirement for every session.
- **Read the white paper in full.** It's the canonical vision statement. Don't skim.
- **Read all 104 structured notes.** Not as reference-when-needed — as the baseline for understanding the full design corpus. They exist precisely so you don't re-read source files, but reading them IS how you absorb the design.
- Respect the gate structure. Every architectural change passes through its gate with Craig's approval.
- Append decisions to INDEX.md with date + rationale. Never delete history.
- When adding new design artifacts, update `.audit/manifest.yml` + write a structured note for future sessions.
- Use the systematic-audit skill for Pass 5+ when verification is needed (post-harness, post-Phase-6, post-Phase-7).
- Keep artifacts as the system of record. Chat scatters. Artifacts encapsulate.
- Leverage the cross-reference matrix (`.audit/cross-reference-matrix.md`) when tracking layer/location questions.

### DON'T

- **Don't re-read what the synthesis artifacts already synthesized.** The vision map IS the inheritance mechanism from the source design artifacts. The 104 audit notes are the inheritance mechanism from source files. If the synthesis is clear on a point, don't go deeper. Only re-derive from source when: (a) you need an exact quote/line number for code, (b) the synthesis is ambiguous on a specific question blocking work, or (c) the synthesis contradicts what you observe in code (trust current code, update synthesis). **This is Craig's explicit preference after the 2026-04-16-b session burned 700K tokens on re-derivation before starting any real work.**
- **Don't read all 104 audit notes preemptively.** They're reference material, not required baseline. Read notes only for the specific files you're touching or when the synthesis points you to one explicitly.
- Don't re-read source artifacts the vision map covers. Tier 1-6 from the old plan is what the vision map synthesizes — don't do both.
- Don't treat the vision map as secondary. For the purposes of getting oriented, **it IS the primary reading**. The white paper + original design artifacts are canonical when there's a conflict, but you shouldn't re-read them preemptively to verify the map.
- Don't re-litigate locked Gate decisions. Rationale is in INDEX.md + artifacts.
- Don't assume deepagents API details without verifying from https://docs.langchain.com/oss/python/deepagents. (A prior session made this mistake.)
- Don't touch `/Users/home/Repositories/indemn-os/` without explicit gate approval for the specific change.
- Don't delete kernel code (G2.3, G4.2) without explicit post-verification sign-off.
- Don't conflate `indemn-os` (Python package) with `indemn-cli` (NPM, different purpose).

---

## 7. The systematic-audit Skill Going Forward

The skill at `.claude/skills/systematic-audit/` is the methodology Craig wants used for future verification passes. The current state:

- Pass 1-4 done. Manifest at 104/104.
- Current manifest is complete relative to the state-at-2026-04-16. As new artifacts are produced (e.g., during Track A implementation), they should be added to the manifest with notes.

### Planned future passes

- **Pass 5 — Post-harness verification**: after Track A Gates 2-6 complete. Verify: `harnesses/` directory exists with 3 images, kernel has no `anthropic` imports, per-Runtime task queues active, `kernel/api/assistant.py` deleted. Essentially a Pass 4 redo against post-fix code state.
- **Pass 6 — Post-Phase-6 verification**: after Track E completes. Verify Indemn CRM actually runs on OS patterns (all watches fire correctly, associates use harness, skills loaded properly, multi-source entity enrichment works per CRM retrace).
- **Pass 7 — Post-Phase-7 verification**: after Track F completes. Verify GIC pipeline runs end-to-end on OS + parallel-run outputs match bespoke system.
- **Pass 8+ — Ongoing**: as each new customer or capability is added.

Each pass uses the same skill: `init.sh` to scope a manifest, `read-next.sh` + notes, `validate-notes.sh` to mark complete, `cross-reference.sh` for the matrix. Script-enforced discipline prevents skipping files.

---

## 8. The Vision — Where This All Goes

The alignment audit resolved a ~85% architecturally-aligned system + ~95% mechanism-aligned. After all 6 tracks complete:

- Architectural alignment: ~100%
- Mechanism alignment: ~100%
- Phase 6 dog-fooding operational (Indemn team uses OS daily)
- Phase 7 GIC operational (first external customer live)
- The OS runs real insurance workloads
- Series A pitch complete: "Here's the platform. Here's it running real insurance. Here's how $10M scales this."

Per Craig's Kyle+Cam framing: the business story (Four Outcomes + Four Engines + 48 associates) maps to the OS's implementation. The moat thesis (insurance-native domain model + agent-accessible platform + compounding intelligence per deployment) materializes.

**Post-vision-realized work** — not in this handoff scope but likely next program of work:
- Additional customers onboarded (INSURICA, Union General, Branch per their retrace patterns)
- Tier 3 developer model activated (customers build on OS directly)
- Additional harness images as new frameworks become relevant (LangChain, custom)
- Post-MVP deferred items become un-deferred as scale demands

---

## 9. Quick Reference — Open Discrepancies from Alignment Audit

| # | Severity | Discrepancy | Track | Fix path |
|---|---|---|---|---|
| Finding 0 | STRUCTURAL | Agent execution in kernel | A | Gates 2-7 |
| Finding 0b | STRUCTURAL | Assistant as kernel endpoint | A | Gates 3-4 (chat harness) |
| D-04 | IMPORTANT | State field detection uses convention | B.1 | Kernel entities set `_state_field_name` |
| D-07 | IMPORTANT | Rule group status not enforced | B.2 | Group lookup in `evaluate_rules` |
| D-08 | IMPORTANT | Hash chain verification broken | B.3 | Debug `compute_hash` roundtrip |
| D-01 | DESIGN/DOC | Dual base class undocumented | C | Phase 0-1 spec update |
| M-1 | MINOR | Bootstrap org_id self-reference | B | Document intentional exception |
| M-2 | MINOR | Seed data loading missing org_id | B | `load_seed_data(org_id=...)` |
| M-3 | MINOR | Org slug uniqueness not enforced | B | `unique=True` on index |

---

## 10. Final Note

This handoff contains everything needed to resume without information loss. The audit infrastructure preserves the 104-file reading. The synthesis artifacts preserve the design. The gate structure preserves the decisions. The track structure preserves the work plan. The rules preserve the discipline.

**You are not starting from scratch. You are continuing a clearly-mapped multi-session effort to take the vision to completion.**

Read what's needed for what you're doing. Respect the gates. Use the notes. Ship the vision.
