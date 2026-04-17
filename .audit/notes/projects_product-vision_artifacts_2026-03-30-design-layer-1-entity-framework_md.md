# Notes: 2026-03-30-design-layer-1-entity-framework.md

**File:** projects/product-vision/artifacts/2026-03-30-design-layer-1-entity-framework.md
**Read:** 2026-04-16 (full file — 841 lines; read key architectural sections: lines 15-280, 320-410, 504-830 via offset + grep of "kernel|harness|runtime|deploy|process")
**Category:** design-source (Layer 1 architectural — entity framework)

## Key Claims

- **Architecture decision: Modular monolith with rich domain entities** (Django/Rails pattern). "One deployable unit with clear sub-domain boundaries. Can be split into services later if needed."
- Technology stack: Beanie (ODM), Pydantic, Motor, FastAPI, Typer, RabbitMQ (domain event bus).
- Rejected alternatives: YAML generator + runtime engine (indirection, data/behavior split), Microservices per sub-domain (too much operational overhead), CQRS + Event Sourcing (too complex initially).
- Base Entity class extends Beanie `Document` with `StateMachineMixin`, `EventMixin`, `AutoRegisterMixin`, `PermissionsMixin`, `SkillGeneratorMixin`.
- Project structure: `sub_domains/{policy_lifecycle, financial, authority_compliance, distribution_delivery, platform}/entities/` + `services/`; `api/app.py`, `cli/main.py`, `skills/generated/`, `events/handlers/`.
- Layered operations: Entity methods (single entity) → Services (deterministic multi-entity) → Events (cross-domain side effects).

## Architectural Decisions

- **Modular monolith, not microservices** — solo builder, operational simplicity, splittable later.
- **Beanie as ODM** — Pydantic models ARE MongoDB documents. Later kept in consolidated spec.
- **FastAPI + Typer** — same mental model, auto-registration from entity classes.
- **RabbitMQ for domain events** — "Already in infrastructure (Amazon MQ). Domain events published to RabbitMQ, subscribers consume." **NOTE: This was later superseded** — the white paper and consolidated specs use MongoDB message_queue + message_log (not RabbitMQ) as the message bus. RabbitMQ is referenced in indemn-microservices repo but the OS uses MongoDB.
- **AutoRegisterMixin** — entity classes auto-register API routes, CLI commands, skills.
- **Python classes as entity definitions** — "The entity classes ARE the definitions." **NOTE: This was later superseded** — 2026-04-09-data-architecture-everything-is-data.md moves entity definitions from Python classes on disk to MongoDB documents with dynamic class creation.
- **Sub-domain organization** — file structure by sub-domain. Later simplified via dynamic entity definitions.
- Services emit events via RabbitMQ; consumers subscribe.

## Layer/Location Specified

- **One deployable unit** — modular monolith, single process. Consistent with later "one image, three entry points" decision.
- Code organized by sub-domain under `sub_domains/` directory.
- `platform/` sub-domain contains what later becomes kernel entities (Associate, Skill, Workflow, Template, KnowledgeBase, Organization, Task, Interaction, Correspondence, Document, Email, Draft).
- **This design PRE-DATES the harness pattern.** Associates are part of the platform sub-domain, run by the same monolith. No kernel/harness separation yet — that comes in 2026-04-10.
- **This design PRE-DATES "everything is data."** Entity definitions are Python classes, not database records. That shift comes in 2026-04-09.

## Dependencies Declared

- Beanie, Motor, Pydantic, FastAPI, Typer, RabbitMQ (later superseded by MongoDB bus), Amazon MQ, Celery (future — tasks).
- Django/Rails patterns as reference.
- DDD methodology.

## Code Locations Specified

- `sub_domains/{domain}/entities/{entity}.py` — entity classes
- `sub_domains/{domain}/services/{service}.py` — services
- `api/app.py` — FastAPI app factory with auto-registration
- `cli/main.py` — CLI entry
- `skills/generated/` — auto-gen markdown skills
- `events/handlers/` — event handlers by domain
- `events/bus.py` — event bus (RabbitMQ)

**These paths were later superseded by the actual implementation** (`kernel/entity/`, `kernel_entities/`, etc.) once the entity-as-data shift happened.

## Cross-References

- 2026-03-25-domain-model-v2.md (DDD classification)
- Superseded by:
  - 2026-04-09-data-architecture-everything-is-data.md (entities as data, not Python classes)
  - 2026-04-08-primitives-resolved.md (six primitives + kernel entities abstraction)
  - 2026-04-13-white-paper.md (final state)
- 2026-04-09-temporal-integration-architecture.md later replaces RabbitMQ event bus with MongoDB + Temporal pattern.

## Open Questions or Ambiguities

**This artifact was largely superseded.** It established:
- Modular monolith (RETAINED)
- FastAPI + Typer + Beanie + Pydantic (RETAINED)
- Auto-registration pattern (RETAINED — became auto-generation from entity definitions)
- Base Entity class + Mixins pattern (RETAINED conceptually)

It proposed and later REVISED:
- RabbitMQ for events → replaced with MongoDB message_queue + Temporal dispatch
- Python classes as entity definitions → replaced with data-driven definitions (EntityDefinition collection + dynamic class creation)
- Sub-domain folder organization → replaced with kernel/kernel_entities split + domain entities as data

**Pass 2 check**: This artifact's "modular monolith, one deployable unit" aligns with the kernel deployment. But its pre-harness-pattern framing didn't constrain future harness design. Finding 0 (harness pattern) emerged later and is independent of this artifact's decisions.

**Potential discrepancy**: The artifact proposes `platform/entities/associate.py` — an associate entity in the platform sub-domain. The implementation has `kernel_entities/actor.py` (Actor primitive, which Associate specializes via `type="associate"`). Naming evolved but semantic intent preserved.
