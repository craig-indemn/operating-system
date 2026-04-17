# Notes: 2026-04-08-actor-references-and-targeting.md

**File:** projects/product-vision/artifacts/2026-04-08-actor-references-and-targeting.md
**Read:** 2026-04-16 (full file — 109 lines)
**Category:** design-source

## Key Claims

- **Decision: Assignment is NOT a primitive.** Varies too much by domain. The kernel provides the mechanism; the domain provides the semantics.
- **Messages always target ROLES. Kernel does not do actor-specific targeting.**
- **Context enables filtering**: messages include entity context (related entities resolved and attached). Queries filter on context fields.
- Actor's queue = "Show me messages where `target_role = underwriter` AND (`context.submission.underwriter = me` OR `context.submission.underwriter is null`)".
- **Rejected `--target-from-field` proposal** (kernel resolving actor refs through entity relationships during message generation): would require cross-entity reads during watch evaluation, violating "watch evaluation is entity-local."
- **Actor references are just entity fields** — `Submission.underwriter` is a regular field that holds an actor ID. No special treatment.
- **Assignment is a domain concern**: `indemn submission update SUB-001 --underwriter jc` — just set a field. Audit trail captures it. Queue queries filter by it.
- **Scale optimization**: `target_actor_id` can be denormalized on message at scale (pre-populated from context at creation time). Not MVP; additive.

## Architectural Decisions

- **Watch evaluation must be entity-local** (no cross-entity reads during watch eval).
- **Rejected kernel-level actor-specific targeting** — keep kernel simple.
- **Domain entity fields can hold actor references** — no special kernel treatment.
- **Message schema has `target_actor_id` field** (optional, not populated initially). At scale, populated from context for pre-targeted routing.
- **Queue query semantics**: target_role match + (target_actor_id null OR target_actor_id me).

## Layer/Location Specified

- **Targeting resolution** = queue query layer (either UI or API), NOT kernel message-generation.
- **Actor reference fields** = domain entity fields.
- **`target_actor_id` denormalization** = message schema addition when scale requires.
- **Watch evaluation** = kernel, entity-local only.

**Finding 0 relevance**: Not directly relevant. This is about message targeting mechanics, not agent execution location.

## Dependencies Declared

- Watch evaluator (kernel)
- Queue query (MongoDB find)
- Audit trail (changes collection)

## Code Locations Specified

- Conceptual: `target_role`, `target_actor_id` fields on message schema.
- Later implemented in `kernel/message/schema.py` and scoped watches in `kernel/watch/scope.py`.

## Cross-References

- 2026-04-08-primitives-resolved.md (same day)
- 2026-04-08-kernel-vs-domain.md (assignment was a primitive there; this artifact rejects that; later artifacts reconcile)
- 2026-04-10-realtime-architecture-design.md (scoped watches use `field_path` + `active_context`, which IS the "target-from-field" idea — but now at watch-evaluation time, with explicit scope resolution)

## Open Questions or Ambiguities

- **Tension with kernel-vs-domain.md**: that artifact listed Assignment as a primitive; this artifact says "Assignment is not a primitive." **Resolution**: Assignment-as-relationship is a common pattern but not a kernel primitive. Kernel entities are still 6 (later 7 with Session).
- **Scope qualifier on watches** (`scope: actor_context`) introduced later (EventGuard retrace) bridges this design with the target-from-field rejection: scope resolution happens in watch eval but uses `field_path` on the watch definition, not kernel-level actor-ref inference.

**Supersedence note**:
- "Assignment is not a primitive" SURVIVES.
- "Messages target roles; context enables filtering" MOSTLY survives but CLARIFIED: **scoped watches** (2026-04-10-realtime-architecture-design.md) add emit-time scope resolution via `field_path` — a middle path between pure role targeting and kernel actor resolution. The design is: watch declares `scope: actor_context` with `field_path: owner_actor_id`; evaluator reads that field from the event entity and writes `target_actor_id` on the message.
- So the current final design is: target_actor_id IS populated from watch scope configuration, but through declarative `field_path` on the watch, not kernel magic.
