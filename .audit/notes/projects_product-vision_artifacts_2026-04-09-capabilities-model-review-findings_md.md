# Notes: 2026-04-09-capabilities-model-review-findings.md

**File:** projects/product-vision/artifacts/2026-04-09-capabilities-model-review-findings.md
**Read:** 2026-04-16 (full file — 149 lines)
**Category:** design-review

## Key Claims

- Three reviewers (platform scalability, GIC trace, rule engine pitfalls) validated kernel capabilities model.
- **8 findings**:
  1. **Multi-entity atomicity is the NORMAL case** — linker creates Submission + updates Email; need batch transaction per message.
  2. **Rules need AND/OR/NOT composition from day 1** — structured JSON condition language.
  3. **Lookups ≠ Rules** — separate concepts. Mapping tables (lookups) vs. conditional logic (rules). One lookup replaces 24 rules.
  4. **Veto rules prevent incorrect matches** — override positive matches + force `needs_reasoning`.
  5. **Evaluation traces must be first-class data** — `indemn entity trace` queryable, always-on.
  6. **`needs_reasoning` response needs context** — reason, attempted_rules, hint.
  7. **Pipeline orchestration should be watches, not processing_status** — watches ARE the wiring.
  8. **Rule groups + versioning + drift prevention** — Draft → Active → Archived lifecycle, conflict detection at creation, coverage reports, soft caps.
- **27 gaps from GIC trace**; the most architecturally significant: multi-entity atomicity, watch vs. processing_status, Submission-not-Email coupling for assessor, rule condition expression language, multi-LOB multi-entity in one invocation (HIGH risk of orphaned state), draft consolidation, ball-holder as computed field.
- **Deferred items validated as correct to defer**: structured expression language, draft consolidation, visual rule builder, rule chaining, saga compensation.

## Architectural Decisions

- **JSON for conditions** with all/any/not combinators + standard operators.
- **Lookups as separate concept** from rules. Bulk-importable, maintained by non-technical users.
- **Veto rules** override positive matches + force reasoning.
- **Rule groups with lifecycle** (Draft/Active/Archived).
- **Evaluation traces in data, not logs** — queryable.

## Layer/Location Specified

- **Condition evaluator** = kernel, shared across watches + rules.
- **Rule engine** = `kernel/rule/engine.py`.
- **Lookup resolution** = `kernel/rule/lookup.py`.
- **Evaluation trace** = recorded in changes collection as `method_metadata`.
- **Rule groups** = kernel entity or rule field; lifecycle enforced in evaluation path.
- **Watches as pipeline orchestration** = kernel watch evaluation (not per-entity `processing_status` field).

**Finding 0 relevance**: Not directly. This is about rule+capability model completeness. Secondarily: the `needs_reasoning` handoff is described as "an escape valve that no traditional platform has" — this mechanism lives in the agent interpreter, which per later design should be in the harness, not in the kernel.

## Dependencies Declared

- JSON schema for conditions
- Lookup storage (per-org MongoDB collection)
- Evaluation trace records in changes collection

## Code Locations Specified

- `kernel/rule/engine.py::evaluate_rules`
- `kernel/rule/lookup.py`
- `kernel/rule/schema.py` + `kernel/rule/validation.py`
- Shared evaluator: `kernel/watch/evaluator.py`

## Cross-References

- 2026-04-09-entity-capabilities-and-skill-model.md (the design this reviews)
- 2026-04-09-data-architecture-review-findings.md (sister review — data architecture)
- 2026-04-10-gic-retrace-full-kernel.md (formal retrace uses these findings)
- Phase 0-1 consolidated spec (implements rules + lookups + veto + groups)
- Phase 2-3 consolidated spec (implements evaluate_rules + auto_classify)

## Open Questions or Ambiguities

Resolved in subsequent artifacts:
- Multi-entity atomicity → implemented via save_tracked wrapping multiple entity saves in one txn.
- Watch vs processing_status → watches are the wiring (consolidated-architecture, white paper).
- Ball-holder computed field → documented in computed field scope (documentation-sweep item 6).
- Draft consolidation → domain skill concern.

**Supersedence note**: All 8 findings SURVIVE into the final architecture. The 27 GIC gaps are tracked into the gap identification + consolidated specs.
