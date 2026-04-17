# Notes: 2026-04-08-kernel-vs-domain.md

**File:** projects/product-vision/artifacts/2026-04-08-kernel-vs-domain.md
**Read:** 2026-04-16 (full file — 158 lines)
**Category:** design-source

## Key Claims

- **Kernel primitives exist before any domain system is built**; they're the fabric any system operates within. Domain entities are created per system using the entity framework.
- **Decision: "Start bare, add domain primitives later."** Kernel doesn't start with insurance assumptions. If insurance domains prove universal enough, promote later.
- **6 kernel primitives (this artifact's set)**: Organization, Entity (framework), Message, Actor, Role, **Assignment**.
- **Assignment is NOT a field on domain entities.** It's a built-in OS relationship: entity + actor + role context. Works uniformly across all entity types.
- **Multi-assignment is first-class** — multiple actors (different roles) or multiple actors (same role, collaborative).
- **Message targeting**: Messages target role by default; if entity has an assignment for the target role, message targets that specific actor.
- **Queue query semantics for an actor**: "messages where target_role in my roles AND (target_actor_id is null OR target_actor_id is me)".
- **Actor identity is OS-level**, not a domain concept. Same actor ID referenced across every system built on the OS. Cross-domain: JC could be "underwriter" in GIC Email Intelligence AND "account_manager" in a CRM built on the OS.

## Architectural Decisions

- **Kernel vs. domain line is about universality**: kernel = what's true for every system; domain = per-system data.
- **Actor roles stack in an org**: "An actor with multiple roles sees the union of all their roles' watches in their queue."
- **Assignment replaces per-entity assignment fields** (`assigned_to`, `underwriter`, `reviewer` field patterns) with one universal OS capability.
- **Actor types declared**: human, associate. (Later white paper adds the "associate is just an actor" framing stronger — the type is more about identity lifecycle than behavior.)
- **CLI-level primitives** for all kernel operations — `indemn role`, `indemn actor`, `indemn assign`, `indemn assignment`.

## Layer/Location Specified

- **Kernel primitives live in OS kernel code.** Not specified *where* in the file/module sense — just that they're kernel-level.
- **Domain entities live in each system's codebase / configuration** — but "configured", not built as kernel code.
- **The artifact is specifically about the logical layer split**, not the physical deployment topology. No trust boundary discussion.

**Relevance to Finding 0**: This artifact establishes that Actor/Role are KERNEL primitives — they must exist in the kernel. But the EXECUTION ENGINE of an actor (deterministic interpreter, reasoning interpreter) is an actor implementation detail, not a kernel primitive. The implication Craig later formalizes: the interpreter lives in the harness, not in the kernel.

## Dependencies Declared

- `indemn` CLI surface for all primitive operations
- MongoDB as storage (implicit — "entity framework")
- No Temporal, no LiveKit, no harness concept yet (pre-April 9)

## Code Locations Specified

- No code paths. Pure design.

## Cross-References

- 2026-04-08-primitives-resolved.md (same session, earlier note)
- 2026-04-08-actor-spectrum-and-primitives.md (precursor)
- White paper (later) — the 6 primitives survive with one refinement: Integration is reinstated as primitive #6 (2026-04-10).
- authentication-design.md (later) — adds Session as 7th kernel entity.

## Open Questions or Ambiguities

- **"Start bare" is a guiding principle but doesn't enumerate the tipping point.** When does something become universal enough to promote? Not specified.
- **The 6 primitives here** will become:
  - White paper-era: 6 primitives = Entity, Message, Actor, Role, Organization, Integration (Assignment becomes an Entity relationship pattern, not a top-level primitive). NOTE: Assignment is demoted or integrated differently in later artifacts.
  - 7 kernel entities (Organization, Actor, Role, Integration, Attention, Runtime, Session)
- **Supersedence note for vision map**:
  - "Actor identity is OS-level" — SURVIVES.
  - "Assignment as universal OS capability" — appears to be partially absorbed into Role + Actor references in later artifacts; need to verify in later retraces whether Assignment remains a distinct top-level primitive or becomes a relationship pattern.
  - "Multi-assignment" — survives; implemented via context + actor references.
  - "Start bare, add later" — SURVIVES as a principle.
