---
ask: "What did three independent reviewers find when pressure-testing the kernel capabilities model against GIC and rule engine patterns?"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: review
    description: "Three independent agent reviews: platform scalability, GIC end-to-end trace, rule engine pitfalls"
  - type: artifact
    description: "2026-04-09-entity-capabilities-and-skill-model.md"
---

# Capabilities Model Review Findings

## What Was Validated

All three reviewers confirm: the kernel capabilities model is the right architecture. The primitives compose correctly. Condition→action rules with LLM fallback is novel and well-suited. CLI-configurable everything holds. The `needs_reasoning` handoff is "an escape valve that no traditional platform has."

## Finding 1: Multi-Entity Atomicity Is the Normal Case

Every GIC pipeline step changes multiple entities. The linker creates a Submission AND updates an Email. The assessor creates an Assessment AND updates a Submission. The draft writer creates a Draft AND could update the Submission.

The current transaction model wraps ONE entity + its messages. It needs to wrap MULTIPLE entities + their messages in a single MongoDB transaction. Without this, a crash between entity A's save and entity B's save leaves the system inconsistent.

**Fix:** The actor framework needs a batch transaction mode — all entity saves within one message processing are committed atomically. Opt-in per skill for high-volume scenarios where the longer lock duration matters.

## Finding 2: Rules Need AND/OR Composition From Day One

Single-condition rules cover ~50% of real cases. The first org will need compound conditions.

**Fix:** Store rules as structured JSON (array of conditions with all/any/not combinators). CLI accepts simple inline conditions as sugar. Storage format must support composition from the start.

```json
{
  "all": [
    {"field": "from_address", "op": "ends_with", "value": "@usli.com"},
    {"any": [
      {"field": "subject", "op": "contains", "value": "Quote"},
      {"field": "subject", "op": "contains", "value": "Indication"}
    ]},
    {"not": {"field": "subject", "op": "contains", "value": "Decline"}}
  ]
}
```

## Finding 3: Lookups and Rules Are Different Things

Most of what looks like 50 rules is a lookup table. The 24 USLI prefix→LOB mappings aren't conditional logic — they're a mapping table.

**Fix:** Separate concepts:
- **Rules** for conditional logic: "when X and Y, do Z"
- **Lookups** for mapping tables: "prefix MGL → General Liability"

One lookup replaces 24 rules. Lookups can be bulk-imported from CSV, exported, maintained by non-technical users. The rule engine consults lookups during evaluation.

## Finding 4: Veto Rules Prevent Incorrect Matches

`needs_reasoning` only fires when NO rule matches. Dangerous case: rule matches incorrectly (USLI email that's a decline, not a quote).

**Fix:** Negative/veto rules that override positive matches and force `needs_reasoning`:

```bash
indemn rule create --entity Email --org gic --group usli --veto \
  --when "from_address ends_with @usli.com AND subject contains 'Decline'" \
  --forces-reasoning "USLI email but subject suggests decline"
```

Simpler than confidence scoring. Covers 90% of incorrect-match cases.

## Finding 5: Evaluation Traces Must Be First-Class Data

Every entity that passes through rule evaluation gets a trace record: rules evaluated, matched, won/lost, entity state at evaluation time. Not logs. Not debug mode. Always. Queryable.

```bash
indemn entity trace email/gic/EMAIL-001
# 47 rules evaluated, 2 matched, usli-quote won (score 85),
# decline-detect eliminated (condition: subject not contains 'Decline')
```

Without this, system becomes a black box within 3 months. Every misclassification becomes a multi-hour support ticket.

## Finding 6: needs_reasoning Response Needs Context

The LLM should know WHY deterministic path failed: no match, conflict, veto, ambiguous fuzzy match.

```json
{
  "needs_reasoning": true,
  "reason": "conflict",
  "attempted_rules": [
    {"rule": "usli-quote", "matched": true, "result": {"type": "usli_quote"}},
    {"rule": "decline-detect", "matched": true, "result": {"type": "decline"}}
  ],
  "hint": "Two rules matched with different classifications."
}
```

Reduces LLM token usage and improves accuracy. Different failure modes need different reasoning strategies.

## Finding 7: Pipeline Orchestration Should Be Watches, Not processing_status

GIC's pipeline ordering is currently encoded in Email.processing_status transitions. In the OS model, watches on entity events should handle orchestration:

- Extractor watches: `Email:created WHERE has_attachments`
- Classifier watches: `Email:created WHERE no_attachments` + `Extraction:created`
- Linker watches: `Email:classification_set`
- Assessor watches: `Submission:created` (not Email:linked — more general)

processing_status becomes audit/monitoring convenience, not routing mechanism. More aligned with OS philosophy — watches ARE the wiring.

## Finding 8: Rule Groups, Versioning, and Drift Prevention

Structural defenses from day one:
- **Rule groups** with ownership (required — no orphan rules)
- **Draft → Active → Archived lifecycle** (test before deploy, roll back)
- **Conflict detection at creation time** (refuse to create overlapping rules without explicit resolution)
- **Coverage reports** (rules that never match, overlapping, conflicting)
- **Soft caps with warnings** (50 rules per entity type default)

## GIC End-to-End Trace: Key Gaps Found

The GIC trace identified 27 specific gaps. The most architecturally significant:

| Gap | Description | Severity |
|-----|------------|----------|
| Multi-entity atomicity | Every pipeline step changes multiple entities — need batch transactions | HIGH |
| Watch vs. processing_status | Fundamental tension between pipeline model and reactive model | HIGH |
| Assessor should watch Submissions, not Emails | Current coupling to email pipeline is wrong for the OS model | MEDIUM |
| Rule condition expression language | Blocks all deterministic configuration — needs specification | MEDIUM |
| Multi-LOB: three entities in one invocation | Orphaned partial multi-LOB submissions on crash | HIGH |
| Draft consolidation for multi-LOB | Two drafts to same agent from one email — awkward | MEDIUM |
| Ball holder should be auto-computed | Entity behavior (computed field), not set by actors | LOW |

## Deferred Items (Validated as Correct to Defer)

- **Structured expression language** in rule conditions — ship simple conditions + lookups + vetos. LLM fallback buys time. Build expression language when real orgs show needs.
- **Draft consolidation** — human responsibility or future capability.
- **Visual rule builder** — produces unmaintainable spaghetti. CLI/YAML forces precision.
- **Rule chaining** (rule A output triggers rule B) — fastest path to unmaintainable systems.
- **Saga-style compensation** for partial failures — batch transactions handle MVP. Sagas for complex long-running processes later.

## Scale Assessment

| Component | Comfortable | Watch Carefully | Needs Action |
|-----------|-------------|-----------------|-------------|
| Rule evaluation (200 rules/org) | <100K saves/hour | 100K-1M | >1M (but never the bottleneck — MongoDB writes are) |
| Capability library coverage | 60-70% of first 5 customers | Track needs_reasoning patterns | Build capabilities when same pattern appears 50+ times |
| LLM fallback cost (Haiku) | <$1/day/org | $1-10/day/org | >$10/day (optimize hot paths) |
| Rule count per org | <50 | 50-200 | >200 (rule explosion, needs review) |
