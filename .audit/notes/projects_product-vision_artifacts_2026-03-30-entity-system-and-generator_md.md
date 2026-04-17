# Notes: 2026-03-30-entity-system-and-generator.md

**File:** projects/product-vision/artifacts/2026-03-30-entity-system-and-generator.md
**Read:** 2026-04-16 (full file — 272 lines)
**Category:** design-source (early — entity generator concept)

## Key Claims

- **The generator pattern is the core OS capability** — define entity declaratively, auto-generate full stack (schema + API + CLI + skill + events + permissions).
- Build vs Buy: **Build from scratch**. No open source AMS exists. CRM frameworks (Twenty, ERPNext, Odoo) provide generic CRM but insurance domain is too specialized.
- Input: YAML entity definition (name, fields, state_machine, relationships, permissions, events).
- Output: Postgres schema, REST API, CLI commands, Skill markdown, webhook events, permissions.
- **Skill document is dual-purpose**: AI associate interface + developer documentation + engineer reference.
- Generator is "the OS kernel" — everything else built on top.
- Generator enables Tier 3 (developers define entities and get full stack auto-generated).
- OS with entity generator IS the CRM and AMS.

## Architectural Decisions

- **Build generator pattern from scratch** — purpose-built for insurance + CLI-first.
- **Postgres (this early doc)** — later SUPERSEDED by MongoDB decision (Beanie ODM, Pydantic-native, document-oriented fits flexible data).
- **YAML as entity definition format** — later partially changed: entity definitions stored as JSON in MongoDB per 2026-04-09-data-architecture-everything-is-data.md; YAML is used for org export/import only.
- **Auto-generate everything** — RETAINED as core principle.
- **Skills as self-documentation** — RETAINED.

## Layer/Location Specified

- **Generator as core kernel capability.** Later: kernel capabilities library includes auto-classify, fuzzy-search, pattern-extract, stale-check, etc. The entity generator itself becomes part of the kernel (factory.py, definition.py, save.py, etc.).
- No process/image/trust-boundary specifics at this stage.

## Dependencies Declared

- Postgres (later changed to MongoDB)
- Open source component candidates (Paperless-ngx, Lago, Payload CMS — deferred)
- Existing Indemn infra: middleware-socket-service, voice-service, LiveKit, Pinecone, Stripe, Indemn CLI.

## Code Locations Specified

- "Generator IS the OS kernel" — located in kernel. Later implementation: `kernel/entity/factory.py`, `kernel/entity/definition.py`, `kernel/api/registration.py`, `kernel/cli/registration.py`, `kernel/skill/generator.py`.

## Cross-References

- 2026-03-25-domain-model-v2.md (entities to generate)
- Superseded technology choice: 2026-03-30-design-layer-1-entity-framework.md (Postgres → later MongoDB)
- 2026-04-09-data-architecture-everything-is-data.md (definitions become data)

## Open Questions or Ambiguities

- Postgres vs MongoDB — later resolved to MongoDB.
- YAML format — later resolved to JSON in database (MongoDB), with YAML for org export/import.

**Early artifact. Core idea (auto-generation) retained. Specific tech (Postgres, YAML definitions) later revised. No Finding 0-class deviation.**
