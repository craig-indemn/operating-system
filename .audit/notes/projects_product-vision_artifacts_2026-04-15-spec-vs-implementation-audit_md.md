# Notes: 2026-04-15-spec-vs-implementation-audit.md

**File:** projects/product-vision/artifacts/2026-04-15-spec-vs-implementation-audit.md
**Read:** 2026-04-16 (full file — 354 lines)
**Category:** earlier-audit (Pass 1)

## Key Claims

- **Method**: read white paper (937 lines), INDEX.md (160+ decisions), all 4 consolidated specs (8,017 lines total), 90-gap document, verification report, shakeout findings, every Python file (120+), every TypeScript file (40+).
- **13 confirmed deviations**: 3 CRITICAL, 4 IMPORTANT, 5 MINOR, 1 COSMETIC. 2 retracted. 4 resolved.

### CRITICAL deviations:

- **D-01: Dual Base Class Architecture — NOT in spec.**
  - Spec: one `BaseEntity(Document)` for all entities.
  - Code: `KernelBaseEntity(Document)` (Beanie ODM, 7 kernel entities) + `DomainBaseEntity(BaseModel)` (Pydantic + raw Motor, domain entities) + `_DomainQuery` wrapper.
  - Root cause: introduced during shakeout (commit 23fcf06) to fix Findings 3 and 4 (Motor Database truth check + Beanie is_root single-collection inheritance).
  - Recommendation: document the dual base class architecture explicitly in spec.
- **D-02: save_tracked() Transaction Scope — REGRESSION.**
  - Spec (Phase 0-1 §1.9): "In one MongoDB transaction: 1. Entity write 2. Changes collection record 3. Watch evaluation → message creation."
  - Code (`kernel/entity/save.py` lines 112-155): transaction block ends at line 131 (entity write). `write_change_record` and `evaluate_watches_and_emit` at lines 134, 147 are OUTSIDE the transaction but still within the session context.
  - Root cause: shakeout fix (commit 23fcf06) wrapped block in `try/except` for version restore; indentation of change/emission shifted outside the transaction block.
  - Impact: atomicity broken — entity can commit without audit record or messages.
  - Pass 2 notes this was later FIXED (2026-04-16) per comprehensive audit.
- **D-03: Assistant Has No Tools.**
  - Spec: assistant executes operations on behalf of user (Phase 4-5 §4.7; G-59 of gap analysis).
  - Code: `kernel/api/assistant.py` streams text, `client.messages.stream()` with NO `tools` parameter.
  - Severity: CRITICAL; same as shakeout Finding 18 — NOT FIXED.
  - Recommended local fix: add tool definitions (`create_entity`, `get_entity`, `list_entities`, `transition_entity`, `invoke_capability`, `search_entities`).
  - **Pass 2 diagnosis**: this is Finding 0b — proper fix is building the chat-harness image, not patching the kernel endpoint.

### IMPORTANT deviations:

- **D-04: State field detection uses convention, not flag.**
  - Code: `_find_state_field` falls back to iterating `("status", "stage")` and returns first match. GIC's Submission uses `stage` as the state machine field but also has `status` — would break state transitions.
  - Fix: kernel entities should explicitly set `_state_field_name` as class var.
- **D-06: Flexible data cross-entity schema resolution untested.**
  - Implementation present but only partially tested. Works for Phase 1 (no flexible data); Phase 6/7 GIC submissions use product-specific form schemas.
- **D-07: Rule group status not enforced.**
  - Code: `evaluate_rules()` checks `Rule.status == "active"` but NOT the rule's group status. A rule with `status=active` in a `draft` group would still evaluate.
  - Fix: add group status check to `evaluate_rules()` in `kernel/rule/engine.py`.
- **D-08: Hash chain verification broken.** (Same as shakeout Finding 14.)
  - `indemn audit verify` fails because `compute_hash()` produces different hashes at read vs write time (ObjectId/datetime serialization inconsistency).

### MINOR deviations:

- **D-09: Bootstrap path PARTIALLY uses save_tracked()** — improved since shakeout Finding 16; admin Actor + admin Role now use save_tracked; Organization itself still uses Beanie's insert() due to self-referencing org_id.
- **D-11 (renumbered): Watch cache TTL async reload.** Now functional (per shakeout Finding 10 fix). Returns stale data during reload. Acceptable for MVP; Change Stream suggested for multi-instance.
- **D-13: Attention has 5 purposes** (code matches white paper; INDEX.md "six purposes" was a typo, corrected in white paper).
- **D-16: Seed data loading doesn't set org_id.**
  - `kernel/seed.py` creates EntityDefinition + Skill objects without `org_id`. Per-org scope requires org_id.
- **D-19: Org slug uniqueness not enforced** — index exists but not `unique=True`.

### COSMETIC:

- **D-18: `datetime.now(timezone.utc)` vs `datetime.utcnow()`** — code is better than spec. `utcnow()` is deprecated in Python 3.12+.

### Retracted findings (2):

- D-11 original: claimed `preview_bulk_operation` wasn't registered — WRONG. It is registered in `kernel/temporal/worker.py` lines 66-67.
- D-14 original: claimed `process_human_decision` wasn't registered — WRONG. It is registered at line 64.

### Resolved deviations (4):

- D-05: Generic update endpoint bypasses state machine — fixed during shakeout (Finding 15).
- D-10: No Temporal Worker implementation — FALSE; correctly implemented with TracingInterceptor and proper config.
- D-15: CLI default format JSON — correct per shakeout decision.
- 15 shakeout fixes all verified in place.

## Architectural Decisions (from this audit)

- **The single biggest user-visible gap is D-03 (assistant no tools)** — described in spec as "at forefront" primary human-to-system interface; implemented as text-only chatbot.
- **D-02 is the #1 invariant violation** — atomicity of entity write + changes + messages is the core system invariant. The shakeout fix regressed it.
- **D-01 (dual base class) is correct engineering** — the fix for Beanie+dynamic-model issues is the right approach. Spec needs to document it.

## Layer/Location Specified

- **All deviations are at the mechanism/code-correctness level**, NOT architectural layer level.
- This audit CONFIRMED Finding 0b (D-03) as a runtime-observable problem but described it as "add tools to assistant endpoint" — LOCAL fix.
- This audit DID NOT identify Finding 0 (async agent execution in kernel Temporal worker vs harness).
- **This audit IS the Pass 1 audit**; the comprehensive audit (2026-04-15) + Pass 2 audit (2026-04-16) were motivated by this audit's methodology gap (no cross-reference to source design at architectural-layer level).

**Finding 0 relevance**:
- D-03 is the runtime manifestation of Finding 0b. Fix proposed by this audit (add tools) addresses symptom.
- Pass 2 argues root cause is architectural-layer issue requiring chat-harness build.
- This audit provides CODE-LEVEL DETAIL on where Finding 0b manifests:
  - `kernel/api/assistant.py` — no `tools` parameter in `client.messages.stream()`.
  - System prompt claims "You can execute any CLI command" — disconnect from implementation.
- This audit DOES NOT touch the async-agent case (`process_with_associate` in kernel Temporal worker) — Finding 0 blind spot.

## Dependencies Declared

- Anthropic SDK (client.messages.stream usage audited)
- Beanie ODM (base class dual-mode)
- Motor (raw MongoDB for DomainBaseEntity)
- Pydantic v2 (timezone-aware datetimes)
- MongoDB transactions (session + start_transaction pattern)

## Code Locations Specified

Specific files audited with line references:
- `kernel/entity/base.py` — KernelBaseEntity + DomainBaseEntity split
- `kernel/entity/save.py` lines 112-155 — save_tracked() transaction scope (D-02)
- `kernel/entity/state_machine.py::_find_state_field` (D-04)
- `kernel/entity/flexible.py::_resolve_schema`, `_resolve_target_entity` (D-06)
- `kernel/rule/engine.py::evaluate_rules` (D-07)
- `kernel/changes/hash_chain.py::compute_hash` (D-08)
- `kernel/api/bootstrap.py::platform_init` (D-09)
- `kernel/api/registration.py` line 84-90 (D-05 resolved)
- `kernel/temporal/worker.py` lines 64, 66-67 (retractions — activities registered correctly)
- `kernel/api/assistant.py` (D-03 — no tools)
- `kernel/watch/cache.py::get_cached_watches` (D-11)
- `kernel/seed.py::load_seed_data` (D-16)

## Cross-References

- 2026-04-13-white-paper.md (design source of truth)
- INDEX.md (160+ decisions)
- All 4 consolidated specs
- 2026-04-14-impl-spec-gaps.md + verification-report.md
- 2026-04-15-shakeout-session-findings.md (19 findings)
- 2026-04-15-comprehensive-audit.md (same-day comprehensive audit; motivated Pass 2)
- 2026-04-16-pass-2-audit.md (next-day Pass 2 that closed the methodology gap)
- indemn-os repo at post-shakeout commit

## Open Questions or Ambiguities

**The methodology gap this audit demonstrates**:
- The audit compared spec vs implementation at the mechanism level thoroughly (13 deviations identified).
- The audit did NOT ask whether the spec's mechanisms were in the right architectural layer.
- Finding 0 / 0b root causes (agent execution location) were not surfaced because the audit started from the consolidated specs as authoritative, not from the source design artifacts.
- The comprehensive audit (same day) and Pass 2 audit (next day) closed this gap by cross-referencing specs back to source design artifacts.

**Priority recommendations from this audit**:
1. Fix D-02 (transaction scope) — #1 invariant violation.
2. Fix D-03 (assistant tools) — biggest functional gap. (Pass 2: better fix is the harness pattern.)
3. Document D-01 (dual base class).
4. Fix D-07 (rule group status).
5. Fix D-08 (hash chain verification).
6. Fix D-04 (explicit state field name).
7. D-11 (watch cache) — consider Change Stream for multi-instance.

**Supersedence note for vision map**:
- **D-02 is confirmed RESOLVED** per Pass 2 audit priority 3.
- **D-03 is Finding 0b** per Pass 2 — the proper resolution is the chat-harness pattern, not local tools addition.
- **D-04, D-07, D-08** remain open.
- **D-01 (dual base class)** — design decision that survives in code; spec should acknowledge.
- All other D-xx are either resolved or minor.
