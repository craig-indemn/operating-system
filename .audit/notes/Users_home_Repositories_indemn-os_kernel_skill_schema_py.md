# Notes: /Users/home/Repositories/indemn-os/kernel/skill/schema.py

**File:** /Users/home/Repositories/indemn-os/kernel/skill/schema.py
**Read:** 2026-04-16 (full file — 41 lines)
**Category:** code

## Key Claims

- Module docstring: "Skill document model. Two kinds: Entity skills (auto-generated from entity definitions, reference material); Associate skills (authored by humans/AI, behavioral instructions). Both stored in MongoDB, versioned, content-hashed for integrity."
- `Skill(Document)` — Beanie document model with fields:
  - `org_id` (None for system-level entity skills)
  - `name`
  - `type: Literal["entity", "associate"]`
  - `entity_type` (for entity skills)
  - `content` (markdown string)
  - `content_hash` (for tamper detection)
  - `version: int`
  - `status: Literal["active", "pending_review", "deprecated"]`
  - `created_by`, `created_at`, `updated_at`
- Collection `skills`, indexed by `(name, status)` and `(org_id, type)`.

## Architectural Decisions

- Skills stored in MongoDB per design ("everything is data").
- Content hashed for tamper detection (per white paper § Security).
- Two types (entity + associate) per design.
- Status workflow: active / pending_review / deprecated — supports skill approval workflow.
- `org_id` is optional — None means system-level (shared across orgs, for auto-generated entity skills).

## Layer/Location Specified

- Kernel code: `kernel/skill/schema.py`.
- Beanie document — registered with the kernel's `init_beanie` at startup.
- Per design: skills are data in MongoDB, loaded at runtime.

**No layer deviation for schema definition itself.**

However, skill LOADING currently happens inside the kernel Temporal worker (`kernel/temporal/activities.py::_load_skills`). Per design, this should happen inside the harness (via CLI subprocess: `indemn skill get <name>`). The schema file itself is correct; how it's consumed is the Finding 0 question.

## Dependencies Declared

- `beanie.Document`
- `bson.ObjectId`
- `pydantic.Field`
- `datetime`, `timezone`
- `typing.Literal`, `Optional`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/skill/schema.py`
- Registered for init_beanie in `kernel/db.py`
- Loaded by:
  - `kernel/temporal/activities.py::_load_skills` (Finding 0 code — should be via CLI from harness)
  - `kernel/api/assistant.py::_load_skills_for_roles` (Finding 2 code — should be via CLI from chat harness)

## Cross-References

- Design: 2026-04-09-entity-capabilities-and-skill-model.md (skills are markdown, entity + associate types)
- Design: 2026-04-13-white-paper.md § Security (content hashing + tamper-evident)
- Phase 1 spec §1.19 Skill Entity
- `kernel/skill/integrity.py` — hash verification
- `kernel/skill/generator.py` — entity skill auto-generation

## Open Questions or Ambiguities

**No Pass 2 layer deviation for schema.**

**Secondary observations:**
- The `content_hash` field supports tamper detection. The hash is verified when skills are loaded (`verify_content_hash` in `kernel/skill/integrity.py`).
- `status: pending_review` supports the skill approval workflow (new versions pending approval before activation).
- Version field is incremented on updates — multiple versions can exist in changes collection.
- No `description` field in the schema, but the `_load_skills_for_roles` in assistant.py references `skill.description` — potential minor inconsistency. May be added via `extra="allow"` or via Pydantic extra fields.

Schema is clean and appropriately placed.
