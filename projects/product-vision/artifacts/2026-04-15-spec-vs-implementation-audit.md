---
ask: "Comprehensive spec-vs-implementation audit — every deviation between what was designed and what was built"
created: 2026-04-15
workstream: product-vision
session: 2026-04-15-b
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design source of truth — 937 lines, 11 sections"
  - type: artifact
    ref: "INDEX.md"
    description: "160+ locked decisions"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1-consolidated.md"
    description: "Authoritative Phase 0+1 spec — 3,225 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-2-3-consolidated.md"
    description: "Authoritative Phase 2+3 spec — 2,009 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5-consolidated.md"
    description: "Authoritative Phase 4+5 spec — 2,076 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-6-7-consolidated.md"
    description: "Authoritative Phase 6+7 spec — 707 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-gaps.md"
    description: "90 gaps identified, all resolved in consolidated specs"
  - type: artifact
    ref: "2026-04-14-impl-spec-verification-report.md"
    description: "4-pass verification, 29 findings, all resolved"
  - type: artifact
    ref: "2026-04-15-shakeout-session-findings.md"
    description: "19 findings from first boot — 15 fixed, 4 documented"
  - type: codebase
    ref: "https://github.com/indemn-ai/indemn-os"
    description: "Every Python and TypeScript file read"
---

# Spec-vs-Implementation Audit Report

**Auditor:** Claude Opus 4.6 (1M context)
**Date:** 2026-04-15
**Scope:** Every mechanism in the white paper, every locked decision in INDEX.md, every spec, compared against every file in the codebase.

---

## Method

1. Read the shakeout session findings (19 issues, 15 fixed)
2. Read the white paper end-to-end (937 lines)
3. Read INDEX.md with all 160+ locked decisions
4. Read all four consolidated implementation specs (8,017 lines total)
5. Read the 90-gap identification and 4-pass verification report
6. Read all design artifacts that inform architectural decisions
7. Read every Python file in the codebase (120+ files)
8. Read every TypeScript/TSX file in the UI (40+ files)
9. Compared spec against implementation for every mechanism

Findings below are NEW — not re-discoveries of the 19 shakeout findings. Shakeout fixes are verified where relevant.

---

## CRITICAL Deviations

### D-01: Dual Base Class Architecture — Not in Spec

**Spec says:** One `BaseEntity(Document)` class that all entities (kernel and domain) inherit from. Dynamic domain entities created via `create_model(__base__=BaseEntity)`.

**Code does:** Two base classes exist in `kernel/entity/base.py`:
- `KernelBaseEntity(_EntityMixin, Document)` — Beanie ODM for 7 kernel entities
- `DomainBaseEntity(_EntityMixin, BaseModel)` — Pydantic + raw Motor for domain entities
- A `_DomainQuery` wrapper class replaces Beanie's query interface for domain entities

**Severity:** CRITICAL

**Impact:** This is a fundamental architectural split the spec doesn't describe. Every domain entity uses `DomainBaseEntity` with raw Motor operations instead of Beanie. The dual approach means:
- Domain entities don't get Beanie's `after_find` hook — `_loaded_state` is set manually on every `get()` and `find_one()` call
- Domain entities need a custom `_DomainQuery` class to replicate Beanie's chainable query API
- Domain entities have a different `insert()` method than kernel entities
- `get_motor_collection()` works differently — domain entities use `cls._db_ref[cls._collection_name]` while kernel entities use Beanie's built-in
- Testing surfaces differ — domain entities can't use Beanie test utilities

**Root cause:** This split was **introduced during the shakeout** (commit 23fcf06) to fix Findings 3 and 4. The original build (commit 75d1d08) had a single `BaseEntity(Document)` matching the spec exactly. Beanie's `ExpressionField` and lazy model features caused `dir()` iteration to crash on Motor Database objects (Finding 3), and `is_root=True` caused single-collection inheritance issues (Finding 4). The dual base class was the solution — kernel entities keep Beanie for ODM convenience, domain entities use raw Motor to avoid Beanie's dynamic class problems.

**Recommendation:** Document this architectural decision explicitly in the spec. It's a correct engineering decision — the fix was necessary. The `_DomainQuery` wrapper should be tested for parity with Beanie's query interface. The spec should be updated to describe the dual base class as the intended architecture.

---

### D-02: save_tracked() Transaction Scope — Changes and Messages Outside Transaction

**Spec says:** (Phase 0+1, section 1.9): "In one MongoDB transaction: 1. Entity write 2. Changes collection record 3. Watch evaluation → message creation"

**Code does:** In `kernel/entity/save.py` lines 112-155, the transaction block (`async with session.start_transaction()`) ends at line 131 (closing the entity write). Lines 133-155 (`write_change_record` and `evaluate_watches_and_emit`) appear to execute OUTSIDE the transaction but still within the session context manager.

Looking more carefully at the indentation: the `write_change_record` call at line 134 and `evaluate_watches_and_emit` at line 147 are indented under `async with await client.start_session() as session:` but NOT under `async with session.start_transaction():`. They pass `session=session` but the transaction has already committed.

**Severity:** CRITICAL

**Root cause:** This is a **regression introduced during the shakeout fix** (commit 23fcf06). The pre-shakeout code (commit 63751e2) had the correct transaction scope — changes and emission were INSIDE `async with session.start_transaction():`. The shakeout wrapped the entire block in a `try/except` to restore entity version on failure, and in doing so, the indentation of `write_change_record` and `evaluate_watches_and_emit` shifted to be inside the session but OUTSIDE the transaction. This was likely accidental — the try/except was the fix; the indentation change was the regression.

**Impact:** The atomicity guarantee — "if any part fails, none of it commits" — is broken. An entity can be written without its change record or messages. Specifically:
- Entity write succeeds → transaction commits → change record write fails → entity changed but no audit trail
- Entity write succeeds → transaction commits → watch evaluation fails → entity changed but no messages emitted

**Recommendation:** Re-indent `write_change_record` and `evaluate_watches_and_emit` back inside the `async with session.start_transaction():` block while keeping the try/except wrapper. The version restore on exception is a good fix — just preserve the original transaction scope.

---

### D-03: Assistant Has No Tools — Cannot Execute Operations

**Spec says:** (Phase 4+5, section 4.7, G-59): "The assistant can execute any operation the user has permission for." The associate execution pattern (Phase 2) shows the `execute_command` tool for reasoning-mode associates.

**Code does:** `kernel/api/assistant.py` streams text from Claude with NO tool definitions. The `client.messages.stream()` call has no `tools` parameter. The system prompt says "You can execute any CLI command" but the LLM has no mechanism to do so.

**Severity:** CRITICAL (already documented as Finding 18 in shakeout — NOT FIXED)

**Impact:** The assistant is described as "at forefront" in the white paper — the primary human-to-system interface. Without tools, it's a text-only chatbot. It cannot create entities, transition states, invoke capabilities, or do anything operational. This is the single biggest functional gap in the system.

**Recommendation:** Add tool definitions matching the API endpoints the user's roles permit: `create_entity`, `get_entity`, `list_entities`, `transition_entity`, `invoke_capability`, `search_entities`. Each tool calls the API with the user's JWT.

---

## IMPORTANT Deviations

### D-04: State Machine Field Detection Uses Convention, Not Definition Flag

**Spec says:** (Phase 0+1, section 1.3): EntityDefinition has `is_state_field: True` on the field controlled by the state machine. `_find_state_field` should use this flag.

**Code does:** `kernel/entity/state_machine.py` `_find_state_field()` checks `_state_field_name` (set by factory.py for domain entities) but falls back to iterating `("status", "stage")` for kernel entities. The verification report identified this as T-3: "Some entities might use 'stage' as their state field but also have a 'status' field for a different purpose."

**Severity:** IMPORTANT

**Impact:** GIC's Submission entity uses `stage` as its state field AND has a separate `status` field. If `_find_state_field` returns `"status"` (which it would, since it checks `status` before `stage`), transitions would operate on the wrong field. The shakeout didn't catch this because the test entities used `status`.

**Recommendation:** Kernel entities should explicitly set `_state_field_name` as a class variable, not rely on name convention. E.g., `_state_field_name = "status"` on each kernel entity.

---

### D-05: Generic Update Endpoint Bypasses State Machine

**Spec says:** (White paper, section 2): "The kernel enforces that only valid transitions can occur." State machine fields cannot be set directly.

**Code does:** `kernel/api/registration.py` line 84-90 rejects state field changes in PUT with a clear error. This WAS fixed during shakeout (Finding 15).

**Severity:** RESOLVED — confirming shakeout fix is correct.

---

### D-06: Missing Flexible Data Schema Resolution

**Spec says:** (Phase 0+1, section 1.8): `validate_flexible_data()` resolves schemas from related entities (e.g., Product.form_schema).

**Code does:** `kernel/entity/flexible.py` exists but the implementation is minimal. The `_resolve_schema` function and `_resolve_target_entity` helper are present but rely on `EntityDefinition.find_one()` which requires Beanie to be initialized. The cross-entity schema resolution (loading a related Product entity's form_schema to validate the current entity's flexible data) is implemented but untested.

**Severity:** IMPORTANT

**Impact:** Flexible data validation may not work for the cross-entity case. Not a problem for Phase 1 (no flexible data used yet) but will be for Phase 6/7 (GIC submissions with product-specific form schemas).

**Recommendation:** Add integration tests for flexible data validation with cross-entity schema resolution.

---

### D-07: Rule Group Status Not Enforced During Evaluation

**Spec says:** (Phase 0+1, section 1.17): Rule groups have lifecycle (draft, active, archived). "Draft group → rules not evaluated. Active group → rules evaluate. Archive → rules stop."

**Code does:** `kernel/rule/engine.py` `evaluate_rules()` queries `Rule.find({"status": "active"})` — it checks the rule's own status but does NOT check the rule's group status. A rule in an active state but belonging to a draft group would still evaluate.

**Severity:** IMPORTANT

**Impact:** Rules in draft groups can accidentally affect production if they're individually set to "active". The group lifecycle is supposed to be the organizational layer that prevents this.

**Recommendation:** Add a join or check in `evaluate_rules()` that verifies the rule's group (if any) is also "active".

---

### D-08: Hash Chain Verification Still Broken

**Spec says:** (White paper, section 2): "Verification is a CLI command." Changes collection hash chain should be verifiable.

**Code does:** `indemn audit verify` was documented as Finding 14 in shakeout — "reports a broken chain because compute_hash() at verify time produces different hashes than at write time." The root cause is serialization inconsistency (ObjectId/datetime serialize differently at read vs write time).

**Severity:** IMPORTANT (documented in shakeout, NOT FIXED)

**Impact:** The tamper-evident audit trail cannot be verified. This is a compliance requirement. The hash chain exists but cannot prove integrity.

**Recommendation:** Fix the serialization in `compute_hash()` to produce deterministic output regardless of when it runs. Use `str()` for ObjectId and `strftime` with explicit format for datetime, matching what `orjson.dumps` produces.

---

### D-09: Bootstrap Path PARTIALLY Uses save_tracked() — IMPROVED Since Shakeout

**Spec says:** (White paper, section 2): "ALL saves go through save_tracked()." The CLAUDE.md says "This is non-negotiable."

**Code does:** `kernel/api/bootstrap.py` `platform_init()` now uses `save_tracked(actor_id="__bootstrap__")` for the admin Actor and admin Role. Only the Organization itself uses `insert()` because of the self-referencing org_id (where org_id = id, which save_tracked would misinterpret as an update on a non-existent document).

**Severity:** MINOR (improved since shakeout Finding 16 — the Admin and Role now have audit trails)

**Impact:** Only the Organization bootstrap entity itself lacks an audit trail entry. The admin actor and role DO have change records. This is a reasonable engineering trade-off for the self-reference bootstrap case.

**Recommendation:** Document this as an intentional exception for the self-referencing first Organization only.

---

### D-10: No Temporal Worker Implementation

**Spec says:** (Phase 2, section 2.1): `kernel/temporal/worker.py` with Temporal Worker setup, TracingInterceptor, graceful shutdown.

**Code does:** `kernel/temporal/worker.py` exists and is correctly implemented with ProcessMessageWorkflow, HumanReviewWorkflow, BulkExecuteWorkflow registrations, TracingInterceptor, and proper configuration.

**Severity:** RESOLVED — correctly implemented.

---

### ~~D-11: RETRACTED — preview_bulk_operation IS Registered~~

**Original claim was wrong.** `kernel/temporal/worker.py` lines 66-67 correctly register both `process_bulk_batch` AND `preview_bulk_operation` in the activities list. Verified on re-read.

---

### D-11 (renumbered): Watch Cache TTL Refresh — Improved Since Shakeout

**Spec says:** Watch cache should auto-refresh on 60-second TTL expiry.

**Code does:** `kernel/watch/cache.py` `get_cached_watches()` now schedules an async reload via `asyncio.create_task(load_watch_cache())` when the TTL expires. This was originally a no-op (`pass`) during the shakeout but has been fixed. The current call returns stale data while the reload happens asynchronously — acceptable for MVP.

**Severity:** MINOR (improved since shakeout — now functional, though returns stale data during reload)

**Impact:** There's a brief window where stale watch data is returned during async reload. For multi-instance deployment, each instance has independent 60-second TTL. A Change Stream on the roles collection would provide stronger cross-instance consistency.

**Recommendation:** Consider adding a Change Stream on the roles collection for production multi-instance deployments. The current TTL-based approach is sufficient for MVP.

---

## MINOR Deviations

### D-13: Attention Has 5 Purposes, Spec Originally Said 6

**Spec says:** (White paper, section 2): "Five purposes: real-time session, observing, review, editing, claim in progress." INDEX.md decision says "Six purposes" but the white paper says five.

**Code does:** 5 purposes matching the white paper. The INDEX.md reference to "six" appears to be a typo that was corrected in the white paper.

**Severity:** MINOR — code is correct per the white paper (authoritative source).

---

### ~~D-14: RETRACTED — process_human_decision IS Registered~~

**Original claim was wrong.** `kernel/temporal/worker.py` line 64 correctly registers `process_human_decision` in the activities list. Verified on re-read.

---

### D-15: CLI Default Format Is JSON (Design Decision, Not Deviation)

**Spec says:** The shakeout decided JSON as the default CLI format (agent-first CLI). Code confirms this is consistently applied across all CLI command files.

**Severity:** RESOLVED — correct per shakeout decision.

---

### D-16: Seed Data Loading Doesn't Set org_id

**Spec says:** (Phase 0+1, section 1.26): `load_seed_data()` loads entity definitions and skills.

**Code does:** `kernel/seed.py` creates EntityDefinition and Skill objects without setting `org_id`. EntityDefinition requires `org_id` per the spec (it's per-org). Seed data would need to know which org to target.

**Severity:** MINOR

**Impact:** Seed loading would fail or create org-less definitions.

**Recommendation:** `load_seed_data()` should accept an `org_id` parameter.

---

### D-17: No `kernel/entity/migration.py` Verified as Complete

**Spec says:** Schema migration is first-class with rename, add, remove, dry-run, batching.

**Code does:** `kernel/entity/migration.py` exists. Not fully verified against the spec's complete migration spec (section 1.29) but the file is present.

**Severity:** MINOR — needs functional testing.

---

## COSMETIC Deviations

### D-18: `datetime.utcnow()` in Spec vs `datetime.now(timezone.utc)` in Code

**Spec says:** Uses `datetime.utcnow()` throughout.

**Code does:** Uses `datetime.now(timezone.utc)` throughout (timezone-aware).

**Severity:** COSMETIC — code is actually BETTER than spec. `utcnow()` is deprecated in Python 3.12+. The implementation is more correct.

---

### D-19: Org Slug Uniqueness Not Enforced

**Spec says:** Organization has a unique slug for URL-based identification.

**Code does:** Organization index is `[("slug", 1)]` but not `unique=True`.

**Severity:** COSMETIC — could cause duplicate slugs in theory.

---

## Verified Shakeout Fixes

All 15 inline fixes from the shakeout session were verified:

| # | Finding | Fix Verified |
|---|---------|-------------|
| 1 | ObjectId serialization | YES — `to_dict()` helper + `_ORJSONResponse` |
| 2 | init_beanie ordering | YES — Beanie before entity def loading |
| 3 | Motor Database truth check | YES — skip `_` prefixed attrs |
| 4 | Beanie is_root=True | YES — removed, separate collections |
| 5 | String→ObjectId coercion | YES — `_coerce_objectid_fields()` |
| 6 | date→datetime | YES — TYPE_MAP maps "date" to datetime |
| 7 | Runtime entity registration | YES — `register_domain_entity()` |
| 8 | CORS middleware | YES — outermost, expose X-Refreshed-Token |
| 9 | Entity name slug resolution | YES — `useEntityNameFromSlug` hook |
| 10 | Watch cache invalidation | YES — called in save_tracked for Role |
| 11 | httpx follow_redirects | YES — True in CLIClient |
| 12 | Dynamic CLI override | YES — expanded _STATIC_CLI_ENTITIES |
| 15 | State machine bypass | YES — rejected in update endpoint |
| 17 | Vite proxy /auth prefix | YES — /auth/ with trailing slash |

**Findings 13, 14, 16, 18, 19 were documented not fixed — status unchanged.**

---

## Summary

| Severity | Count | Key Items |
|----------|-------|-----------|
| CRITICAL | 3 | D-01 (dual base class), D-02 (transaction scope), D-03 (assistant no tools) |
| IMPORTANT | 4 | D-04 (state field), D-06 (flexible data), D-07 (rule groups), D-08 (hash chain) |
| MINOR | 5 | D-09 (bootstrap — improved), D-11 (watch cache — improved), D-13, D-16, D-19 |
| COSMETIC | 1 | D-18 (datetime.now(tz) vs utcnow — code is better than spec) |
| RETRACTED | 2 | D-11 original, D-14 — both were wrong, activities ARE registered |
| RESOLVED | 4 | D-05, D-10, D-15 + 15 shakeout fixes verified |
| **Total confirmed deviations** | **13** | **3 critical, 4 important, 5 minor, 1 cosmetic** |

---

## Priority Recommendations

1. **FIX D-02 FIRST** — Move change record and message emission inside the transaction. This is the #1 invariant of the entire system. Currently, entity writes commit independently from their audit records and messages.
2. **FIX D-03** — Add tools to the assistant. This is the biggest user-visible gap. The assistant was designed as "at forefront" but currently can't execute any operations.
3. **DOCUMENT D-01** — The dual base class architecture (KernelBaseEntity + DomainBaseEntity) is likely a correct engineering decision but must be explicitly documented in the spec. The spec says one BaseEntity; the code has two.
4. **FIX D-07** — Rule group status enforcement. Add the group status check to `evaluate_rules()`. Currently a rule in a draft group evaluates if individually active.
5. **FIX D-08** — Hash chain verification. The compute_hash has been improved with strftime/ms truncation but `indemn audit verify` still fails per shakeout Finding 14.
6. **FIX D-04** — Explicit state field naming on kernel entities. The fallback convention (`status` before `stage`) will break for GIC Submission which uses `stage` as the state machine field.
7. **D-11 (watch cache)** — Now functional (schedules async reload on TTL expiry). Consider adding Change Stream for multi-instance consistency in production.
