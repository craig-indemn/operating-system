# Notes: /Users/home/Repositories/indemn-os/kernel/skill/generator.py

**File:** /Users/home/Repositories/indemn-os/kernel/skill/generator.py
**Read:** 2026-04-16 (full file — 53 lines)
**Category:** code

## Key Claims

- Module docstring: "Auto-generate entity skill markdown from entity definition. This is the self-evidence property for documentation: define an entity, its skill (documentation) exists immediately."
- `generate_entity_skill(entity_name, definition)` — produces markdown from EntityDefinition with:
  - Heading
  - Description
  - Fields table (name, type, required, enum values, relationships)
  - Lifecycle (state machine transitions)
  - Commands table (list/get/create/update/transition + activated capabilities)

## Architectural Decisions

- Skill generation happens at entity definition creation/modification time (called elsewhere).
- Output is markdown — human-readable and LLM-consumable.
- Entity auto-generation creates CLI commands (list/get/create/update, optionally transition, + per-capability `<cap_name> --auto`).
- No logic — pure text generation.

## Layer/Location Specified

- Kernel code: `kernel/skill/generator.py`.
- Per design (2026-04-09-entity-capabilities-and-skill-model.md): "entity skills are auto-generated from entity definitions." Implementation matches design.

**No layer deviation.**

## Dependencies Declared

- `kernel.entity.definition.EntityDefinition`

(Very light dependencies — pure text generation function.)

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/skill/generator.py`
- Called by: code that creates/updates entity definitions (e.g., CLI `indemn entity create/modify`)

## Cross-References

- Design: 2026-04-09-entity-capabilities-and-skill-model.md (auto-generated entity skills)
- Phase 1 spec §1.19 Skill Entity
- `kernel/skill/schema.py` — Skill entity schema
- `kernel/entity/definition.py` — EntityDefinition shape

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- Generates CLI commands section listing capabilities — associates reading skills can learn available commands.
- No examples section — could be added later for better LLM consumption.
- No error-handling examples or edge case documentation — minimalist.
- Output is deterministic given the same definition — good for caching/hashing.

This is a simple, correctly-placed kernel utility.
