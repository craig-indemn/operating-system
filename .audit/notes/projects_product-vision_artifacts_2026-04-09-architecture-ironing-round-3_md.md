# Notes: 2026-04-09-architecture-ironing-round-3.md

**File:** projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-3.md
**Read:** 2026-04-16 (full file — 207 lines)
**Category:** design-source

## Key Claims

- **One save = one event.** When an @exposed method transitions status AND sets a field, the system generates ONE event with metadata (method invoked, state transition, fields_changed, timestamp). Watch conditions evaluate against this combined event; matching watches produce one message each, but there's only ONE event.
- **@exposed method invocations are the emission boundary.** Rules that set fields inside a method don't emit mid-method; the save at method end generates ONE event with all changes.
- **The dispatcher process is named the Queue Processor.** Reads message_queue, starts Temporal workflows for associate-eligible items. Also handles escalation deadlines, schedule dispatch, queue health monitoring. One process, multiple responsibilities.
- **message_queue has two purposes**: work queue (humans + associates) AND durable bridge to Temporal. **No separate outbox, no redundancy.**
- **Claiming is transient (about the message). Assignment is explicit (the skill chooses).** Claiming = `findOneAndUpdate`; assignment = `indemn submission assign`. They COMPOSE (some skills claim and assign; others claim and move on).
- **Bootstrap meta-circularity handled by**:
  - **Cache invalidation** on bootstrap entity save (immediately invalidate watch cache; next save reloads fresh).
  - **Cascade guard** at depth 1 for watch evaluations that would mutate the same bootstrap entity type being evaluated.
- **Schema evolution via `indemn entity modify`** — add-field, remove-field, rename-field. Rolling restart picks up changes. Changes collection records the schema change.
- **Condition language = JSON only.** No CLI shorthand. One format stored + CLI. Complex conditions in YAML files → `--from-file`.
- **Versioning insight**: Changes collection IS the version history AND the audit trail. One system, two purposes.
- **Rollback = replay changes in reverse**: `indemn rollback CHANGE-047`, `indemn rollback --to "2026-04-09 14:00"`.
- **Bulk deployment via Temporal** (saga-style compensation if any step fails).

## Architectural Decisions

- **Emission model locked**: entity saves emit events at @exposed method completion; not mid-method, not per-field. This is the selective-emission discipline.
- **Watch evaluation happens against full change metadata**, not separate sub-events.
- **Outbox eliminated (Round 1 + confirmed here).** Write to message_queue inside entity transaction. No separate outbox collection.
- **Queue Processor is THE kernel process** that bridges queue → Temporal. Named and defined.
- **Claiming ≠ assignment.** Different concepts. Kernel supports both; skill decides when to combine.
- **Bootstrap entities are "full entities with 2 safety rules"** — not specially-structured; just special on cache + cascade.
- **Schema changes are explicit CLI operations** (`indemn entity modify`), not mid-flight schema inference.
- **Condition evaluator is ONE evaluator, ONE format.** Shared between rules and watches.
- **Unified versioning + audit** — the changes collection is dual-purpose. Elegant consolidation.

## Layer/Location Specified

- **Emission point** = inside `save_tracked()` in the entity framework (kernel). Not in user code.
- **Watch evaluation** = inside `save_tracked()`, against full change metadata. Kernel.
- **Queue Processor** = separate kernel process (`indemn-queue-processor`). Reads message_queue, dispatches to Temporal.
- **Cache invalidation** = kernel watch cache layer (invalidated on bootstrap entity save).
- **Cascade guard** = kernel-level mechanism (depth tracking, type detection).
- **Schema evolution** = `indemn entity modify` CLI → writes to entity_definitions collection → triggers rolling restart.
- **Condition evaluator** = kernel; shared by watches + rules.
- **Changes collection** = MongoDB, kernel-managed, append-only.

**Finding 0 relevance**:
- Queue Processor is the right place to dispatch work. This artifact puts it in kernel — CORRECT, that's kernel-side.
- BUT: this artifact still says "start Temporal workflow for associate-eligible items" without specifying whether the Temporal worker consuming the workflow is kernel-side or harness-side. Consistent with the April 9 open question.
- `save_tracked` is placed in the entity framework, not the agent's work boundary — consistent with later design.

## Dependencies Declared

- MongoDB (entity framework + message_queue + changes collection + entity_definitions collection)
- Temporal (for workflow dispatch + saga deploys)
- CLI (`indemn rule`, `indemn rollback`, `indemn history`, `indemn deploy`, `indemn entity modify`, `indemn dry-run`)
- Rolling restart mechanism (deployment platform)

## Code Locations Specified

- Conceptual:
  - `save_tracked()` (kernel entity save)
  - Queue Processor process
  - Watch cache
  - `indemn entity modify` CLI
  - `indemn rollback`, `indemn history` CLI
- Implementation mapping (from Pass 2 + CLAUDE.md):
  - `save_tracked` exists in entity framework (noted in Pass 2 comprehensive audit as #1 architectural invariant)
  - `kernel/queue_processor.py` (Pass 2-3 spec)
  - `kernel/watch/cache.py` (Pass 2 notes confirm NO coalescing logic — simplification applied correctly)
  - `kernel/changes/` (hash chain + collection)

## Cross-References

- 2026-04-09-architecture-ironing.md (Round 1) — introduced outbox elimination, skill vs workflow, entity creation via CLI
- 2026-04-09-architecture-ironing-round-2.md — unified capabilities + entity methods, watch+rule condition language
- 2026-04-13-simplification-pass.md — later moved watch coalescing OUT of kernel (here it's still mentioned via message `batch_id`)
- Phase 2-3 consolidated spec — implements Queue Processor, save_tracked, message_queue, watch evaluation
- Phase 0-1 consolidated spec — changes collection, entity framework

## Open Questions or Ambiguities

- **Cache invalidation timing**: "immediately invalidate" — stated as immediate; implementation may be eventually-consistent if Change Streams are used (Pass 2 noted Change Stream-based invalidation is the final design).
- **Cascade guard depth threshold**: "depth 1" for self-referencing bootstrap cascades. Is depth 10 still the max globally? Yes (from Phase 2-3 spec).
- **Schema evolution for existing data**: "Pydantic handles missing fields with defaults" — relies on Pydantic behavior. Field removal leaves data in DB but ignored.
- **Entity class file on disk vs. DB**: this artifact says "Updates the Python class file" for `indemn entity modify`. That contradicts "Beanie for everything, load definitions from DB at startup" in 2026-04-09-data-architecture-solutions.md. Later artifacts resolve this as **entity definitions live ONLY in MongoDB (`entity_definitions` collection)** and classes are created via `create_model` at startup — no Python class files on disk for domain entities.

**Supersedence note**:
- "One save = one event" — SURVIVES. Core invariant.
- "@exposed methods are the emission boundary" — SURVIVES.
- "Queue Processor" name — SURVIVES. Implemented as `kernel/queue_processor.py`.
- "Entity class files on disk" — SUPERSEDED. Entity definitions live in MongoDB only.
- "message batch_id coalescing window" — SUPERSEDED by simplification-pass.md (UI-only coalescing).
- "Changes collection = version history" — SURVIVES.
- "JSON-only conditions" — SURVIVES. One evaluator shared by rules + watches.
