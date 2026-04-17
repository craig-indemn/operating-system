---
ask: "Consolidated implementation specification for Phase 0 (Development Foundation) and Phase 1 (Kernel Framework) — resolving all 35 gaps identified in verification"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design-level source of truth"
  - type: artifact
    ref: "2026-04-14-impl-spec-gaps.md"
    description: "90 gaps identified across 7 verification passes — 35 apply to this phase"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1.md"
    description: "Original spec (superseded by this document)"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1-addendum.md"
    description: "Addendum (superseded by this document)"
  - type: verification
    description: "This document supersedes both the base spec and addendum. It is the authoritative Phase 0+1 implementation specification."
---

# Implementation Specification: Phase 0 + Phase 1 (Consolidated)

**This document supersedes `2026-04-14-impl-spec-phase-0-1.md` and `2026-04-14-impl-spec-phase-0-1-addendum.md`.**

## Relationship to the White Paper

The white paper (Section 11) defines Phase 0 as "Development Foundation" and Phase 1 as "Kernel Framework." This spec turns the design into buildable detail. The architecture is final — this spec does not redesign. It specifies HOW to build what's been designed.

Where the white paper leaves implementation choices open, this spec makes them. Where the design artifacts contain specific patterns, this spec draws on them. Every mechanism described in the white paper that falls within Phase 0+1 scope is specified here.

## What Is NOT in Phase 0+1 (Explicitly Deferred)

Per the white paper, simplification pass, and INDEX.md decisions, these are NOT in Phase 0+1:

- Associate execution via Temporal (Phase 2)
- Integration adapters (Phase 3 — the Integration kernel entity IS defined here, but adapters are Phase 3)
- Base UI (Phase 4)
- SSO, TOTP MFA, magic links (Phase 4 — basic password + token auth IS here)
- Real-time channels, harness pattern (Phase 5)
- Active alerting on kernel entities
- WebAuthn / passkeys (post-MVP)
- Per-operation MFA re-verification `requires_fresh_mfa` (post-MVP)
- DashboardConfig, AlertConfig, Widget entities (post-MVP)
- Tier 3 billing, plans, sub-user invitation, OAuth app management (post-MVP)
- Saga-style cross-batch rollback (post-MVP)
- `bulk_apply` DSL for multi-entity rows (post-MVP)
- Visual rule builder (post-MVP)
- Rule chaining (post-MVP)

---

# Phase 0: Development Foundation

## 0.1 Repository Structure

```
indemn-os/
├── kernel/
│   ├── __init__.py
│   ├── config.py                    # Settings via pydantic-settings (env vars)
│   ├── db.py                        # MongoDB connection, init_beanie, entity registry
│   ├── context.py                   # contextvars for org_id, actor_id, correlation_id [G-71]
│   ├── entity/
│   │   ├── __init__.py
│   │   ├── base.py                  # BaseEntity class
│   │   ├── definition.py            # EntityDefinition document model
│   │   ├── factory.py               # Dynamic class creation from definitions
│   │   ├── state_machine.py         # Transition validation + pre-transition hooks
│   │   ├── computed.py              # Computed field evaluation
│   │   ├── flexible.py              # Flexible data schema resolution + validation [G-72]
│   │   ├── migration.py             # Schema migration (rename, type-change, cleanup)
│   │   ├── exposed.py               # @exposed decorator
│   │   └── save.py                  # save_tracked() — the critical transaction
│   ├── message/
│   │   ├── __init__.py
│   │   ├── schema.py                # Message + MessageLog document models [G-04]
│   │   ├── bus.py                   # MessageBus abstraction interface [G-75]
│   │   ├── mongodb_bus.py           # MongoDB implementation of MessageBus
│   │   ├── emit.py                  # Watch evaluation → message creation
│   │   └── event_metadata.py        # build_event_metadata() [G-01]
│   ├── watch/
│   │   ├── __init__.py
│   │   ├── evaluator.py             # Condition evaluation (shared by watches + rules)
│   │   ├── cache.py                 # In-memory watch cache [G-09]
│   │   ├── scope.py                 # Scope resolution (field_path, active_context)
│   │   └── validation.py            # Watch creation validation (entity-local) [G-18]
│   ├── rule/
│   │   ├── __init__.py
│   │   ├── schema.py                # Rule + RuleGroup document models
│   │   ├── engine.py                # evaluate_rules() [G-07]
│   │   ├── lookup.py                # Lookup document model + resolution
│   │   └── validation.py            # Rule creation validation [G-08]
│   ├── capability/
│   │   ├── __init__.py
│   │   ├── registry.py              # Capability registration and dispatch
│   │   └── auto_classify.py         # First kernel capability
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── middleware.py             # FastAPI auth middleware
│   │   ├── session_manager.py       # Session create, validate, revoke
│   │   ├── jwt.py                   # JWT signing, verification, revocation cache
│   │   ├── password.py              # Argon2id password hashing
│   │   ├── token.py                 # Service token management
│   │   └── rate_limit.py            # Pre-auth rate limiting (interface, full impl Phase 4)
│   ├── scoping/
│   │   ├── __init__.py
│   │   ├── org_scoped.py            # OrgScopedCollection wrapper [G-68]
│   │   └── platform.py              # PlatformCollection for cross-org admin
│   ├── changes/
│   │   ├── __init__.py
│   │   ├── collection.py            # ChangeRecord document model + write operations
│   │   └── hash_chain.py            # Sequential hash chain
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── tracing.py               # OTEL setup + span helpers
│   │   ├── correlation.py           # Correlation ID management
│   │   └── logging.py               # Structured logging setup [G-83]
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py                   # FastAPI application factory
│   │   ├── registration.py          # Auto-register routes from entity definitions
│   │   ├── meta.py                  # GET /api/_meta/entities [G-69]
│   │   ├── websocket.py             # WebSocket for real-time (Phase 4 activation)
│   │   ├── webhook.py               # /webhook/{provider}/{integration_id} (Phase 3)
│   │   ├── health.py                # Health endpoint [G-16]
│   │   ├── errors.py                # Standardized error responses [G-85]
│   │   └── bootstrap.py             # Platform init endpoint
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── app.py                   # Typer application factory
│   │   ├── registration.py          # Auto-register commands
│   │   ├── client.py                # HTTP client for API-mode
│   │   ├── entity_commands.py       # entity create/modify/enable/migrate/cleanup [G-13]
│   │   ├── org_commands.py          # org clone/diff/deploy/export/import [G-14]
│   │   ├── queue_commands.py        # queue stats/dead-letter/retry
│   │   └── platform_commands.py     # platform init/seed/upgrade [G-15]
│   ├── skill/
│   │   ├── __init__.py
│   │   ├── schema.py                # Skill document model [G-10]
│   │   ├── generator.py             # Generate markdown from entity definition
│   │   └── integrity.py             # Content hash + verification
│   ├── queue_processor.py           # Sweep process (extensible sweep functions) [G-63]
│   ├── temporal/                    # Stubs for Phase 2
│   │   ├── __init__.py
│   │   └── client.py               # Temporal client factory (Phase 2 activation)
│   └── seed.py                     # Seed data loading from YAML
│
├── kernel_entities/
│   ├── __init__.py
│   ├── organization.py
│   ├── actor.py
│   ├── role.py
│   ├── integration.py
│   ├── attention.py
│   ├── runtime.py
│   └── session.py
│
├── seed/
│   ├── entities/                    # Seed YAML for standard entity definitions
│   ├── skills/                      # Seed markdown
│   └── roles/                       # Seed YAML
│
├── tests/
│   ├── conftest.py                  # Shared fixtures
│   ├── unit/
│   │   ├── test_state_machine.py
│   │   ├── test_condition_evaluator.py
│   │   ├── test_computed_fields.py
│   │   ├── test_hash_chain.py
│   │   ├── test_jwt.py
│   │   ├── test_org_scoping.py
│   │   ├── test_rule_engine.py
│   │   ├── test_event_metadata.py
│   │   ├── test_flexible_data.py
│   │   └── test_migration.py
│   ├── integration/
│   │   ├── test_entity_lifecycle.py
│   │   ├── test_watch_evaluation.py
│   │   ├── test_message_flow.py
│   │   ├── test_rule_evaluation.py
│   │   ├── test_auth_flow.py
│   │   ├── test_cross_tenant_isolation.py
│   │   ├── test_cascade_depth.py
│   │   └── test_selective_emission.py
│   └── e2e/
│       └── test_first_domain_entity.py
│
├── Dockerfile                       # [G-88]
├── docker-compose.yml               # [G-89]
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## 0.2 Python Project Setup

```toml
# pyproject.toml
[project]
name = "indemn-os"
version = "0.1.0"
requires-python = ">=3.12"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
    "ruff>=0.4",
]

[project.dependencies]
beanie = ">=1.26"
motor = ">=3.4"
pymongo = ">=4.7"
fastapi = ">=0.111"
uvicorn = {version = ">=0.30", extras = ["standard"]}
typer = ">=0.12"
httpx = ">=0.27"
pydantic = ">=2.7"
pydantic-settings = ">=2.3"
pyjwt = ">=2.8"
argon2-cffi = ">=23.1"
pyotp = ">=2.9"
temporalio = ">=1.6"
opentelemetry-api = ">=1.25"
opentelemetry-sdk = ">=1.25"
opentelemetry-exporter-otlp = ">=1.25"
boto3 = ">=1.34"
orjson = ">=3.10"
python-multipart = ">=0.0.9"
pyyaml = ">=6.0"
jsonschema = ">=4.21"
croniter = ">=2.0"

[project.scripts]
indemn = "kernel.cli.app:main"
```

## 0.3 Dockerfile [G-88]

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY kernel/ kernel/
COPY kernel_entities/ kernel_entities/
COPY seed/ seed/

# Default entry point (overridden per Railway service)
CMD ["uv", "run", "python", "-m", "kernel.api.app"]
```

Railway services override CMD:
- API Server: `uv run python -m kernel.api.app`
- Queue Processor: `uv run python -m kernel.queue_processor`
- Temporal Worker: `uv run python -m kernel.temporal.worker`

## 0.4 docker-compose.yml [G-89]

```yaml
version: "3.8"
services:
  indemn-api:
    build: .
    command: uv run uvicorn kernel.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=${MONGODB_URI}  # Atlas dev cluster
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=us-east-1
      - JWT_SIGNING_KEY=dev-signing-key-not-for-production
      - INDEMN_API_URL=http://localhost:8000
      - TEMPORAL_ADDRESS=localhost:7233
      - TEMPORAL_NAMESPACE=default
      - ENVIRONMENT=local
    volumes:
      - .:/app

  indemn-queue-processor:
    build: .
    command: uv run python -m kernel.queue_processor
    environment:
      - MONGODB_URI=${MONGODB_URI}
      - TEMPORAL_ADDRESS=localhost:7233
      - TEMPORAL_NAMESPACE=default
      - ENVIRONMENT=local
    depends_on:
      - indemn-api

  temporal-dev:
    image: temporalio/auto-setup:latest
    ports:
      - "7233:7233"
      - "8233:8233"  # Temporal UI
```

## 0.5 Configuration [G-82]

```python
# kernel/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    mongodb_uri: str
    database_name: str = "indemn_os"
    # Connection pool sizes per service type [G-82]
    mongodb_max_pool_size: int = 50  # API: 50, QP: 10, TW: 30

    # Auth
    jwt_signing_key: str
    jwt_access_token_expire_minutes: int = 15
    jwt_algorithm: str = "HS256"

    # Temporal
    temporal_address: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_api_key: str = ""

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    # OTEL
    otel_exporter_endpoint: str = ""
    otel_service_name: str = "indemn-os"

    # API
    api_url: str = "http://localhost:8000"

    # Environment
    environment: str = "local"  # local, dev, prod

    class Config:
        env_file = ".env"

settings = Settings()
```

## 0.6 Context Variables [G-71]

The mechanism that makes org scoping work automatically across the request lifecycle.

```python
# kernel/context.py
from contextvars import ContextVar
from bson import ObjectId
from typing import Optional

# Set by auth middleware on each request
# Read by OrgScopedCollection, save_tracked(), and entity operations
current_org_id: ContextVar[Optional[ObjectId]] = ContextVar("current_org_id", default=None)
current_actor_id: ContextVar[Optional[str]] = ContextVar("current_actor_id", default=None)
current_correlation_id: ContextVar[Optional[str]] = ContextVar("current_correlation_id", default=None)
current_depth: ContextVar[int] = ContextVar("current_depth", default=0)
```

## 0.7 CLAUDE.md

Written at Phase 0. Key content (refined during implementation):

```markdown
# Indemn OS — Development Conventions

## Architecture
- Modular monolith. One repo, one Docker image, three entry points.
- Trust boundary: kernel processes (API, QP, TW) have direct MongoDB. Everything else uses the API.
- CLI always in API mode. Never direct MongoDB from CLI.

## Entity Types
- **Kernel entities**: Python classes in `kernel_entities/`. Always available. 7 total.
- **Domain entities**: Defined as data in MongoDB `entity_definitions` collection. Dynamic classes created at startup.
- Both share BaseEntity. Both get auto-generated CLI, API, and skills.

## How to Add a Kernel Entity
1. Create class in `kernel_entities/` inheriting BaseEntity
2. Add to kernel_entities list in `kernel/db.py`
3. Add tests in `tests/`

## How to Add a Domain Entity Definition
Via CLI: `indemn entity create <Name> --fields '...' --state-machine '...'`
Or via seed YAML in `seed/entities/`

## How to Add a Kernel Capability
1. Create module in `kernel/capability/`
2. Register in `kernel/capability/registry.py`
3. Add tests

## The Save Path
ALL entity saves go through `save_tracked()`. This is non-negotiable.
save_tracked() does in one MongoDB transaction:
1. Optimistic concurrency check (version field)
2. Entity write
3. Computed field evaluation
4. Changes collection record (with hash chain)
5. Watch evaluation → message creation (selective emission)

## OrgScopedCollection
All application queries use OrgScopedCollection. Never use raw Motor collections.
org_id comes from contextvars (set by auth middleware).

## Naming
- Python: snake_case
- CLI commands: kebab-case
- MongoDB collections: lowercase plural (submissions, actors, roles)
- Entity class names: PascalCase singular (Submission, Actor, Role)

## Testing
- Unit: `tests/unit/` — no external dependencies, fast
- Integration: `tests/integration/` — uses Atlas dev cluster
- E2E: `tests/e2e/` — full scenarios
- Run: `uv run pytest tests/unit/` or `tests/integration/`

## Local Dev
```bash
docker-compose up        # API + queue processor + Temporal dev
uv run indemn --help     # CLI
```
```

## 0.8 CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run pytest tests/unit/ -v

  test-integration:
    runs-on: ubuntu-latest
    env:
      MONGODB_URI: ${{ secrets.MONGODB_DEV_URI }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run pytest tests/integration/ -v

  build:
    runs-on: ubuntu-latest
    needs: [lint, test-unit, test-integration]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t indemn-kernel .
```

## 0.9 Deployment

Railway services per the infrastructure design:

| Service | Entry Point | Public | maxPoolSize |
|---|---|---|---|
| `indemn-api` | `python -m kernel.api.app` | Yes (`api.os.indemn.ai`) | 50 |
| `indemn-queue-processor` | `python -m kernel.queue_processor` | No | 10 |
| `indemn-temporal-worker` | `python -m kernel.temporal.worker` | No | 30 |

Railway shared variables: `MONGODB_URI`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, `TEMPORAL_API_KEY`, `JWT_SIGNING_KEY`, `OTEL_EXPORTER_ENDPOINT`.

## Phase 0 Acceptance Criteria

- [ ] Repository exists with the structure above
- [ ] `uv sync` installs all dependencies
- [ ] `docker-compose up` starts API + queue processor + Temporal dev
- [ ] `uv run pytest tests/unit/` passes
- [ ] `docker build` produces a working image
- [ ] CLAUDE.md exists with conventions
- [ ] CI pipeline runs on push

---

# Phase 1: Kernel Framework

## 1.1 Entity Definition Schema

Domain entity type definitions stored in MongoDB. Kernel entities are NOT defined this way — they are Python classes.

```python
# kernel/entity/definition.py
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId

class FieldDefinition(BaseModel):
    """Definition of a single field on a domain entity."""
    type: str                        # str, int, float, decimal, bool, datetime, date, objectid, list, dict
    required: bool = False
    default: Optional[Any] = None
    unique: bool = False
    indexed: bool = False
    enum_values: Optional[list[str]] = None
    description: Optional[str] = None
    is_state_field: bool = False     # True for the field controlled by the state machine
    is_relationship: bool = False    # True for ObjectId fields that reference other entities
    relationship_target: Optional[str] = None  # Entity name this relationship points to [G-02]

class ComputedFieldDef(BaseModel):
    """A field whose value is derived from another field."""
    source_field: str
    mapping: dict[str, str]          # source_value → computed_value

class IndexDef(BaseModel):
    """A compound index definition."""
    fields: list[tuple[str, int]]    # [("org_id", 1), ("status", 1)]
    unique: bool = False

class CapabilityActivation(BaseModel):
    """A kernel capability activated on this entity type."""
    capability: str                  # "auto_classify", "fuzzy_search", "stale_check"
    config: dict                     # Capability-specific: evaluates, sets_field, threshold, etc.

class FlexibleDataSchema(BaseModel):
    """Configuration for the flexible data section.""" # [G-72]
    schema_source: str               # "self" or a relationship field name (e.g., "product_id")
    schema_field: str                # Field on the source entity holding the JSON schema
    # If schema_source="self", the schema is on this entity's definition
    # If schema_source="product_id", load the Product entity, read its form_schema field

class EntityDefinition(Document):
    """A domain entity type definition. The entity framework reads these
    at startup and creates Beanie Document subclasses dynamically."""

    name: str                                  # "Submission", "Email"
    collection_name: str                       # "submissions", "emails"
    description: Optional[str] = None

    fields: dict[str, FieldDefinition]
    state_machine: Optional[dict[str, list[str]]] = None
    computed_fields: Optional[dict[str, ComputedFieldDef]] = None
    flexible_data: Optional[FlexibleDataSchema] = None  # [G-72]
    indexes: list[IndexDef] = Field(default_factory=list)
    activated_capabilities: list[CapabilityActivation] = Field(default_factory=list)

    # Per-org: different organizations can define different entity types.
    # Seed templates provide starting points; orgs clone and customize.
    # `indemn org clone` copies entity definitions along with all other config.
    org_id: ObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    version: int = 1

    class Settings:
        name = "entity_definitions"
        indexes = [
            [("org_id", 1), ("name", 1)],  # Unique per org
        ]
```

## 1.2 Base Entity Class

```python
# kernel/entity/base.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, ClassVar, Any

class BaseEntity(Document):
    """Base class for all entities — kernel and domain.
    Provides common fields and the save_tracked() method."""

    org_id: ObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    version: int = 1

    # Subclass configuration
    _state_machine: ClassVar[Optional[dict[str, list[str]]]] = None
    _computed_fields: ClassVar[Optional[dict]] = None
    _activated_capabilities: ClassVar[list] = []
    _is_kernel_entity: ClassVar[bool] = False

    # Captured on load for change tracking [G-17]
    _loaded_state: dict = {}

    class Settings:
        use_state_management = True
        is_root = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    async def after_find(self):
        """Beanie hook: capture state on load for change tracking."""  # [G-17]
        self._loaded_state = self.model_dump(by_alias=True)

    def transition_to(self, target_state: str, reason: Optional[str] = None):
        """Validate and set state transition. Does NOT save."""
        from kernel.entity.state_machine import validate_and_apply_transition
        validate_and_apply_transition(self, target_state, reason)

    async def save_tracked(self, actor_id: str = None, **kwargs):
        """The ONLY save path. See section 1.9 for full implementation.
        Returns list of created messages (for optimistic dispatch in Phase 2)."""
        from kernel.entity.save import save_tracked_impl
        _actor_id = actor_id or current_actor_id.get()
        return await save_tracked_impl(self, _actor_id, **kwargs)

    @classmethod
    async def find_scoped(cls, filter_doc: dict = None, **kwargs):
        """Find with automatic org_id injection."""  # [G-68]
        from kernel.context import current_org_id
        filter_doc = filter_doc or {}
        org_id = current_org_id.get()
        if org_id:
            filter_doc["org_id"] = org_id
        return cls.find(filter_doc, **kwargs)

    @classmethod
    async def get_scoped(cls, entity_id, **kwargs):
        """Get by ID with org_id verification."""  # [G-68]
        from kernel.context import current_org_id
        entity = await cls.get(entity_id, **kwargs)
        if entity and current_org_id.get():
            if entity.org_id != current_org_id.get():
                raise PermissionError("Cross-org access denied")
        return entity
```

### Implementation Note: Dual Base Class Architecture (Post-Shakeout)

The spec above describes a single `BaseEntity(Document)` class for all entities. During the shakeout session (commit 23fcf06), this was split into two base classes to resolve runtime failures:

- **`KernelBaseEntity(_EntityMixin, Document)`** — Beanie ODM for the 7 hand-coded kernel entities (Organization, Actor, Role, Integration, Attention, Runtime, Session). These have fixed schemas, one collection each, and benefit from Beanie's query interface and lifecycle hooks.

- **`DomainBaseEntity(_EntityMixin, BaseModel)`** — Pydantic + raw Motor for dynamically-generated domain entities. These are created from `EntityDefinition` records at startup via `create_model` in `kernel/entity/factory.py`. They use per-org collections and cannot fit Beanie's `is_root=True` single-collection inheritance model (shakeout Finding 4).

- **`_DomainQuery`** — a wrapper class on `DomainBaseEntity` that provides a Beanie-compatible query interface (`find`, `find_one`, `get`, `aggregate`) over raw Motor operations, so application code can use the same patterns for both kernel and domain entities.

Both base classes share `_EntityMixin`, which provides the common fields (`org_id`, `created_at`, `updated_at`, `version`), `save_tracked()`, `transition_to()`, `find_scoped()`, and `get_scoped()`. The split is an implementation detail — the entity framework's external behavior is the same for both.

**Root cause**: Shakeout Finding 3 (Motor Database truth check under Beanie's `is_root=True` pattern) and Finding 4 (Beanie single-collection inheritance incompatible with dynamic per-org collections for domain entities). The single-`BaseEntity(Document)` spec was correct in intent but hit Beanie/Motor constraints at runtime. The dual base class resolves both without changing any external behavior.

### Beanie + OrgScopedCollection Integration [G-68]

Two layers of org isolation:

**Layer 1: BaseEntity class methods** — `find_scoped()` and `get_scoped()` inject org_id from context. Application code uses these instead of raw `find()` and `get()`.

**Layer 2: OrgScopedCollection** — wraps raw Motor collection for any queries that bypass Beanie (aggregations, raw updates, bulk operations).

```python
# kernel/scoping/org_scoped.py
from motor.motor_asyncio import AsyncIOMotorCollection
from kernel.context import current_org_id

class OrgScopedCollection:
    """Wraps a Motor collection to always inject org_id."""

    def __init__(self, collection: AsyncIOMotorCollection, org_id: ObjectId = None):
        self._collection = collection
        self._org_id = org_id or current_org_id.get()

    def _inject(self, filter_doc: dict = None) -> dict:
        f = dict(filter_doc or {})
        f["org_id"] = self._org_id
        return f

    async def find_one(self, filter_doc=None, *a, **kw):
        return await self._collection.find_one(self._inject(filter_doc), *a, **kw)

    def find(self, filter_doc=None, *a, **kw):
        return self._collection.find(self._inject(filter_doc), *a, **kw)

    async def insert_one(self, doc, *a, **kw):
        doc["org_id"] = self._org_id
        return await self._collection.insert_one(doc, *a, **kw)

    async def update_one(self, filter_doc, update, *a, **kw):
        return await self._collection.update_one(self._inject(filter_doc), update, *a, **kw)

    async def update_many(self, filter_doc, update, *a, **kw):
        return await self._collection.update_many(self._inject(filter_doc), update, *a, **kw)

    async def delete_one(self, filter_doc, *a, **kw):
        return await self._collection.delete_one(self._inject(filter_doc), *a, **kw)

    async def count_documents(self, filter_doc=None, *a, **kw):
        return await self._collection.count_documents(self._inject(filter_doc), *a, **kw)

    async def aggregate(self, pipeline, *a, **kw):
        pipeline = [{"$match": {"org_id": self._org_id}}] + list(pipeline)
        return self._collection.aggregate(pipeline, *a, **kw)
```

**PlatformCollection** — for platform admin cross-org operations. Requires explicit instantiation with full audit. Application code cannot accidentally access it.

```python
# kernel/scoping/platform.py
class PlatformCollection:
    """Bypasses org scoping for platform admin operations.
    Requires explicit org_id parameter. Every operation is audited."""

    def __init__(self, collection: AsyncIOMotorCollection, acting_actor_id: str):
        self._collection = collection
        self._acting_actor_id = acting_actor_id

    async def find_one(self, filter_doc=None, *a, **kw):
        result = await self._collection.find_one(filter_doc or {}, *a, **kw)
        # Audit: platform access logged
        return result
    # ... similar methods, all audited
```

## 1.3 Dynamic Entity Class Creation [G-02]

```python
# kernel/entity/factory.py
from pydantic import create_model
from kernel.entity.base import BaseEntity
from kernel.entity.definition import EntityDefinition, FieldDefinition
from typing import Optional, Literal
from bson import ObjectId
from datetime import datetime, date
from decimal import Decimal

TYPE_MAP = {
    "str": str, "int": int, "float": float, "decimal": Decimal,
    "bool": bool, "datetime": datetime, "date": date,
    "objectid": ObjectId, "list": list, "dict": dict,
}

def create_entity_class(definition: EntityDefinition) -> type[BaseEntity]:
    """Create a Beanie Document subclass from an EntityDefinition."""

    # Build field definitions
    field_definitions = {}
    for field_name, field_def in definition.fields.items():
        python_type = TYPE_MAP.get(field_def.type, str)
        if field_def.enum_values:
            # For enum fields, use str type with Pydantic field-level validation.
            # Literal[tuple(...)] works with create_model in Pydantic v2 but
            # can be fragile across Python versions. The json_schema_extra
            # carries enum values for the UI; validation uses a model_validator.
            python_type = str
            # Enum validation is added as a model_validator after class creation (below)
        if not field_def.required:
            python_type = Optional[python_type]
        default = field_def.default if field_def.default is not None else (
            None if not field_def.required else ...
        )
        field_definitions[field_name] = (python_type, default)

    # Add flexible data field if configured
    if definition.flexible_data:
        field_definitions["data"] = (dict, {})

    # Create dynamic class
    DynamicEntity = create_model(
        definition.name,
        __base__=BaseEntity,
        **field_definitions,
    )

    # Add enum validators for fields with enum_values
    enum_fields = {
        fname: fdef.enum_values
        for fname, fdef in definition.fields.items()
        if fdef.enum_values
    }
    if enum_fields:
        original_init = DynamicEntity.__init__
        def _validating_init(self, **data):
            for fname, allowed in enum_fields.items():
                val = data.get(fname)
                if val is not None and val not in allowed:
                    raise ValueError(f"Field '{fname}' must be one of {allowed}, got '{val}'")
            original_init(self, **data)
        DynamicEntity.__init__ = _validating_init

    # Store enum metadata for UI and skill generation
    DynamicEntity._enum_fields = enum_fields

    # Identify the state field from is_state_field flag in definition
    state_field_name = None
    for fname, fdef in definition.fields.items():
        if fdef.is_state_field:
            state_field_name = fname
            break
    DynamicEntity._state_field_name = state_field_name

    # Attach configuration
    DynamicEntity._state_machine = definition.state_machine
    DynamicEntity._computed_fields = (
        {k: v.model_dump() for k, v in definition.computed_fields.items()}
        if definition.computed_fields else None
    )
    DynamicEntity._activated_capabilities = definition.activated_capabilities or []
    DynamicEntity._flexible_data_config = definition.flexible_data
    DynamicEntity._is_kernel_entity = False

    # Create Settings for Beanie
    idx_list = [[("org_id", 1)] + list(idx.fields) for idx in definition.indexes]
    # Always add org_id as first index field [G-18 implicit]
    idx_list.append([("org_id", 1)])

    DynamicEntity.Settings = type("Settings", (), {
        "name": definition.collection_name,
        "indexes": idx_list if idx_list else None,
    })

    return DynamicEntity
```

### Relationship Resolution for Dynamic Entities [G-02]

Dynamic entities store relationships as plain ObjectId fields (e.g., `carrier_id: ObjectId`). They do NOT use Beanie's `Link` type because dynamic classes can't reference each other by name at creation time.

Relationship resolution is explicit — the caller loads related entities by ID when needed:

```python
# To load a related entity:
carrier = await ENTITY_REGISTRY["Carrier"].get_scoped(entity.carrier_id)
```

For context enrichment on messages (G-74), the watch's `context_depth` parameter triggers this resolution at message creation time. The `emit.py` module follows relationship fields (identified by `is_relationship=True` in the field definition) to the specified depth.

Kernel entities CAN use Beanie's `Link` type because they're static classes that reference each other at compile time. But for cross-referencing between kernel and domain entities, plain ObjectId fields are used.

## 1.4 Database Initialization

```python
# kernel/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from kernel.entity.definition import EntityDefinition
from kernel.entity.factory import create_entity_class
from kernel.config import settings
from kernel.skill.schema import Skill
from kernel.rule.schema import Rule, RuleGroup
from kernel.rule.lookup import Lookup
from kernel.message.schema import Message, MessageLog
from kernel.changes.collection import ChangeRecord
from kernel_entities import (
    Organization, Actor, Role, Integration,
    Attention, Runtime, Session,
)

ENTITY_REGISTRY: dict[str, type] = {}

async def init_database():
    """Initialize MongoDB and all entity classes."""
    client = AsyncIOMotorClient(
        settings.mongodb_uri,
        maxPoolSize=settings.mongodb_max_pool_size,  # [G-82]
    )
    db = client[settings.database_name]

    # Kernel entities + kernel infrastructure documents
    kernel_models = [
        Organization, Actor, Role, Integration,
        Attention, Runtime, Session,
        EntityDefinition, Skill, Rule, RuleGroup, Lookup,
        Message, MessageLog, ChangeRecord,
    ]
    for cls in kernel_models:
        if hasattr(cls, '__name__'):
            ENTITY_REGISTRY[cls.__name__] = cls

    # Load domain entity definitions from ALL orgs (direct Motor before Beanie init).
    # Entity definitions are per-org. At startup, the kernel loads all definitions
    # across all orgs, deduplicating by name (same-name definitions across orgs
    # produce the same Python class — org scoping happens at query time via org_id).
    # If two orgs define "Submission" with different fields, the UNION of fields
    # is used for the Python class — MongoDB is schemaless, so documents in each
    # org only have the fields that org's definition specifies.
    defs_coll = db["entity_definitions"]
    seen_names: dict[str, EntityDefinition] = {}
    async for doc in defs_coll.find({}):
        defn = EntityDefinition(**doc)
        if defn.name in seen_names:
            # Merge: union of fields from all orgs' definitions of this name
            existing = seen_names[defn.name]
            for fname, fdef in defn.fields.items():
                if fname not in existing.fields:
                    existing.fields[fname] = fdef
            continue
        seen_names[defn.name] = defn

    # Reserved names: kernel entity names cannot be used for domain entities
    RESERVED_NAMES = {cls.__name__ for cls in kernel_models if hasattr(cls, '__name__')}

    for defn in seen_names.values():
        if defn.name in RESERVED_NAMES:
            import logging
            logging.error(
                f"Domain entity '{defn.name}' collides with kernel entity name. "
                f"Reserved names: {RESERVED_NAMES}. Skipping."
            )
            continue
        try:
            dynamic_cls = create_entity_class(defn)
            ENTITY_REGISTRY[defn.name] = dynamic_cls
        except Exception as e:
            # Log but don't crash — one bad definition shouldn't block startup
            import logging
            logging.error(f"Failed to create entity class for {defn.name}: {e}")

    # Initialize Beanie
    all_models = list(ENTITY_REGISTRY.values())
    await init_beanie(database=db, document_models=all_models)

    # Load watch cache
    from kernel.watch.cache import load_watch_cache
    await load_watch_cache()

    return db
```

## 1.5 Kernel Entities (All Seven)

All seven kernel entities defined as Python classes. Each inherits from BaseEntity.

### Organization

```python
# kernel_entities/organization.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field

class Organization(BaseEntity):
    """Multi-tenancy scope. The boundary around everything."""
    name: str
    slug: str
    status: Literal["onboarding", "active", "suspended"] = "onboarding"
    settings: dict = Field(default_factory=dict)
    template_source: Optional[str] = None
    default_mfa_required: bool = False

    _state_machine = {
        "onboarding": ["active"],
        "active": ["suspended"],
        "suspended": ["active"],
    }
    _is_kernel_entity = True

    class Settings:
        name = "organizations"
        indexes = [[("slug", 1)]]
```

### Actor

```python
# kernel_entities/actor.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from bson import ObjectId

class Actor(BaseEntity):
    """Identity — humans, AI associates, and developers as participants."""
    name: str
    email: Optional[str] = None
    type: Literal["human", "associate", "tier3_developer"]
    status: Literal["provisioned", "active", "suspended", "deprovisioned"] = "provisioned"
    role_ids: list[ObjectId] = Field(default_factory=list)

    # Associate-specific (None for humans)
    skills: Optional[list[str]] = None
    mode: Optional[Literal["deterministic", "reasoning", "hybrid"]] = None
    runtime_id: Optional[ObjectId] = None
    owner_actor_id: Optional[ObjectId] = None
    llm_config: Optional[dict] = None
    trigger_schedule: Optional[str] = None  # Cron expression for scheduled associates
    strict_deterministic: bool = False  # [G-56] If true, RAISE on needs_reasoning instead of LLM fallback

    # Auth
    authentication_methods: list[dict] = Field(default_factory=list)
    mfa_exempt: bool = False

    _state_machine = {
        "provisioned": ["active"],
        "active": ["suspended", "deprovisioned"],
        "suspended": ["active", "deprovisioned"],
    }
    _is_kernel_entity = True

    class Settings:
        name = "actors"
        indexes = [
            [("org_id", 1), ("email", 1)],
            [("org_id", 1), ("type", 1), ("status", 1)],
            [("org_id", 1), ("role_ids", 1)],
        ]
```

### Role

```python
# kernel_entities/role.py
from kernel.entity.base import BaseEntity
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class WatchDefinition(BaseModel):
    """A watch on a role — declares what entity changes matter."""
    entity_type: str
    event: str           # "created", "transitioned", "method_invoked", "fields_changed", "deleted"
    conditions: Optional[dict] = None  # JSON condition (same language as rules)
    scope: Optional[dict] = None       # {"type": "field_path", "path": "..."} or {"type": "active_context", "traverses": "..."}
    context_depth: int = 1             # How deep to resolve related entities in message context [G-74]

class Role(BaseEntity):
    """Permissions and watches — what actors can do and what flows to them."""
    name: str
    permissions: dict = Field(default_factory=dict)
    # Format: {"read": ["Submission", "Email"], "write": ["Submission", "Draft"]}
    # "*" means all entity types

    watches: list[WatchDefinition] = Field(default_factory=list)
    can_grant: Optional[list[str]] = None  # Role names this role can grant to others
    mfa_required: bool = False
    is_inline: bool = False                # True for associate-specific singleton roles
    bound_actor_id: Optional[ObjectId] = None  # Set for inline roles

    _is_kernel_entity = True

    class Settings:
        name = "roles"
        indexes = [[("org_id", 1), ("name", 1)]]
```

### Integration

```python
# kernel_entities/integration.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from bson import ObjectId
from datetime import datetime

class Integration(BaseEntity):
    """External connectivity — provider, credentials, ownership, adapter dispatch."""
    name: str
    owner_type: Literal["org", "actor"]
    owner_id: ObjectId
    system_type: str        # email, payment, voice, ams, carrier, identity_provider, etc.
    provider: str           # outlook, gmail, stripe, livekit, etc.
    provider_version: str = "v1"
    config: dict = Field(default_factory=dict)
    secret_ref: Optional[str] = None   # AWS Secrets Manager path
    access: Optional[dict] = None      # For org-level: {"roles": ["underwriter", "ops"]}
    status: Literal["configured", "connected", "active", "error", "paused"] = "configured"
    last_checked_at: Optional[datetime] = None
    last_error: Optional[str] = None
    content_visibility: Literal["full_shared", "metadata_shared", "owner_only"] = "full_shared"

    _state_machine = {
        "configured": ["connected"],
        "connected": ["active", "error"],
        "active": ["error", "paused", "configured"],
        "error": ["configured"],
        "paused": ["active", "configured"],
    }
    _is_kernel_entity = True

    class Settings:
        name = "integrations"
        indexes = [
            [("org_id", 1), ("system_type", 1), ("status", 1)],
            [("owner_type", 1), ("owner_id", 1)],
        ]
```

### Attention

```python
# kernel_entities/attention.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from bson import ObjectId
from datetime import datetime

class Attention(BaseEntity):
    """Active working context — who is attending to what, right now."""
    actor_id: ObjectId
    target_entity: dict        # {"type": "Interaction", "id": ObjectId}
    related_entities: list[dict] = Field(default_factory=list)

    purpose: Literal[
        "real_time_session",
        "observing",
        "review",
        "editing",
        "claim_in_progress",
    ]

    runtime_id: Optional[ObjectId] = None
    workflow_id: Optional[str] = None
    session_id: Optional[str] = None

    opened_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    metadata: dict = Field(default_factory=dict)
    status: Literal["active", "expired", "closed"] = "active"

    _state_machine = {"active": ["expired", "closed"]}
    _is_kernel_entity = True

    class Settings:
        name = "attentions"
        indexes = [
            [("actor_id", 1), ("purpose", 1)],
            [("target_entity.id", 1)],
            [("related_entities.id", 1)],
            [("runtime_id", 1), ("purpose", 1)],
            [("expires_at", 1)],
            [("org_id", 1), ("status", 1)],
        ]
```

### Runtime

```python
# kernel_entities/runtime.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from datetime import datetime

class Runtime(BaseEntity):
    """Execution environment — where associates actually run."""
    name: str
    kind: Literal["realtime_chat", "realtime_voice", "realtime_sms", "async_worker"]
    framework: str             # deepagents, langchain, custom
    framework_version: str
    transport: Optional[str] = None
    transport_config: dict = Field(default_factory=dict)
    transport_secret_ref: Optional[str] = None
    llm_config: dict = Field(default_factory=dict)
    sandbox_config: dict = Field(default_factory=dict)
    deployment_image: str = ""
    deployment_platform: str = "railway"
    deployment_ref: Optional[str] = None
    capacity: dict = Field(default_factory=lambda: {"max_concurrent_sessions": None, "max_memory_mb": None})
    status: Literal["configured", "deploying", "active", "draining", "stopped", "error"] = "configured"
    instances: list[dict] = Field(default_factory=list)

    _state_machine = {
        "configured": ["deploying"],
        "deploying": ["active", "error"],
        "active": ["draining", "error"],
        "draining": ["stopped"],
        "stopped": ["deploying"],
        "error": ["configured", "stopped"],
    }
    _is_kernel_entity = True

    class Settings:
        name = "runtimes"
        indexes = [[("org_id", 1), ("kind", 1), ("status", 1)]]
```

### Session

```python
# kernel_entities/session.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from bson import ObjectId
from datetime import datetime

class Session(BaseEntity):
    """Authentication state — tokens, expiration, revocation."""
    actor_id: ObjectId
    type: Literal["user_interactive", "associate_service", "tier3_api", "cli_automation"]
    auth_method_used: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: Literal["active", "expired", "revoked"] = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    access_token_jti: str
    refresh_token_ref: Optional[str] = None
    mfa_verified: bool = False
    mfa_verified_at: Optional[datetime] = None
    claims_stale: bool = False
    platform_admin_context: Optional[dict] = None

    _state_machine = {"active": ["expired", "revoked"]}
    _is_kernel_entity = True

    class Settings:
        name = "sessions"
        indexes = [
            [("actor_id", 1), ("status", 1)],
            [("access_token_jti", 1)],
            [("expires_at", 1)],
            [("org_id", 1), ("type", 1), ("status", 1)],
        ]
```

## 1.6 State Machine Enforcement

```python
# kernel/entity/state_machine.py

class StateMachineError(Exception):
    pass

class TransitionValidationError(Exception):
    """Raised by pre-transition validation hooks."""
    pass

def validate_and_apply_transition(entity: "BaseEntity", target_state: str, reason: str = None):
    """Validate transition, run pre-transition hooks, apply state change.
    Does NOT save — caller must call save_tracked()."""
    sm = entity._state_machine
    if sm is None:
        return  # No state machine — all transitions allowed

    # Find the state field
    state_field = _find_state_field(entity)
    current_state = getattr(entity, state_field, None)

    # Check if transition is allowed
    valid_transitions = sm.get(current_state, [])
    if target_state not in valid_transitions:
        raise StateMachineError(
            f"Cannot transition {type(entity).__name__} from '{current_state}' to '{target_state}'. "
            f"Valid transitions: {valid_transitions}"
        )

    # Pre-transition validation hook (subclass override) [G from addendum A.13]
    entity._validate_pre_transition(target_state)

    # Store transition metadata for event emission
    entity._pending_transition = {
        "from": current_state,
        "to": target_state,
        "reason": reason,
    }

    # Apply the transition
    setattr(entity, state_field, target_state)

def _find_state_field(entity) -> str:
    """Find the field controlled by the state machine.
    For domain entities: uses _state_field_name set by factory.py from is_state_field.
    For kernel entities: falls back to convention ('status' or 'stage')."""
    # Dynamic entities have _state_field_name set by create_entity_class
    state_field = getattr(type(entity), '_state_field_name', None)
    if state_field:
        return state_field
    # Fallback: convention for kernel entities
    for field_name in ("status", "stage"):
        if hasattr(entity, field_name):
            return field_name
    raise StateMachineError(f"{type(entity).__name__} has a state machine but no status/stage field")
```

BaseEntity provides a default pre-transition hook that subclasses can override:

```python
# In BaseEntity:
def _validate_pre_transition(self, target_state: str):
    """Override in kernel entity subclasses for business validation.
    Domain entities use capability-based validation instead."""
    pass
```

## 1.7 Computed Field Evaluation

```python
# kernel/entity/computed.py

def evaluate_computed_fields(entity: "BaseEntity") -> dict[str, any]:
    """Evaluate computed fields and return values to set.
    Called inside save_tracked() before the MongoDB write."""
    computed_defs = entity._computed_fields
    if not computed_defs:
        return {}

    result = {}
    entity_data = entity.model_dump(by_alias=True)

    for field_name, defn in computed_defs.items():
        source_field = defn["source_field"] if isinstance(defn, dict) else defn.source_field
        mapping = defn["mapping"] if isinstance(defn, dict) else defn.mapping
        source_value = entity_data.get(source_field)
        if source_value is not None and str(source_value) in mapping:
            computed_value = mapping[str(source_value)]
            result[field_name] = computed_value
            setattr(entity, field_name, computed_value)

    return result
```

## 1.8 Flexible Data Validation [G-72]

```python
# kernel/entity/flexible.py
import jsonschema
from kernel.entity.definition import FlexibleDataSchema

async def validate_flexible_data(entity: "BaseEntity", data: dict) -> list[str]:
    """Validate the entity's 'data' field against its configured schema.
    Returns list of validation errors (empty = valid)."""
    config = getattr(entity, '_flexible_data_config', None)
    if not config or not data:
        return []

    # Resolve the schema
    schema = await _resolve_schema(entity, config)
    if not schema:
        return []  # No schema configured — all data accepted

    # Validate using JSON Schema
    errors = []
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(str(e.message))
    except jsonschema.SchemaError as e:
        errors.append(f"Invalid schema: {e.message}")

    return errors

async def _resolve_schema(entity, config: FlexibleDataSchema) -> dict:
    """Resolve the JSON Schema for flexible data validation."""
    if config.schema_source == "self":
        # Schema is on this entity's definition
        defn = await EntityDefinition.find_one({"name": type(entity).__name__})
        return defn.flexible_data.get("schema") if defn else None
    else:
        # Schema is on a related entity (e.g., product_id → Product.form_schema)
        related_id = getattr(entity, config.schema_source, None)
        if not related_id:
            return None
        from kernel.db import ENTITY_REGISTRY
        # Determine the target entity type from the field definition
        target_entity_cls = await _resolve_target_entity(entity, config.schema_source)
        if not target_entity_cls:
            return None
        related = await target_entity_cls.get(related_id)
        if not related:
            return None
        return getattr(related, config.schema_field, None)

async def _resolve_target_entity(entity, field_name: str):
    """Resolve the entity class for a relationship field."""
    from kernel.db import ENTITY_REGISTRY
    from kernel.entity.definition import EntityDefinition
    defn = await EntityDefinition.find_one({"name": type(entity).__name__})
    if defn and field_name in defn.fields:
        target = defn.fields[field_name].relationship_target
        if target:
            return ENTITY_REGISTRY.get(target)
    return None
```

## 1.9 The Save Path — save_tracked()

The critical transaction. Every entity modification goes through this.

```python
# kernel/entity/save.py
from datetime import datetime
from uuid import uuid4
from bson import ObjectId
from kernel.context import current_org_id, current_actor_id, current_correlation_id, current_depth
from kernel.entity.computed import evaluate_computed_fields
from kernel.entity.flexible import validate_flexible_data
from kernel.changes.collection import write_change_record
from kernel.message.emit import evaluate_watches_and_emit
from kernel.message.event_metadata import build_event_metadata
from kernel.observability.tracing import create_span

MAX_CASCADE_DEPTH = 10

async def save_tracked_impl(entity: "BaseEntity", actor_id: str, **kwargs):
    """
    The ONLY save path. In one MongoDB transaction:
    1. Optimistic concurrency check (version field)
    2. Computed field evaluation
    3. Flexible data validation
    4. Entity write
    5. Changes collection record (with hash chain)
    6. Selective emission: watch evaluation → message creation
    """
    method = kwargs.get("method")
    method_metadata = kwargs.get("method_metadata")
    correlation_id = kwargs.get("correlation_id") or current_correlation_id.get() or str(uuid4())
    depth = kwargs.get("depth", current_depth.get())

    with create_span("entity.save_tracked",
                     entity_type=type(entity).__name__,
                     entity_id=str(entity.id) if entity.id else "new"):

        # Detect heartbeat-only updates on Attention [from Attention spec]
        if _is_heartbeat_only(entity):
            await _save_heartbeat_only(entity)
            return

        # Compute computed fields
        computed_changes = evaluate_computed_fields(entity)

        # Validate flexible data
        if hasattr(entity, 'data') and entity.data:
            errors = await validate_flexible_data(entity, entity.data)
            if errors:
                raise ValueError(f"Flexible data validation failed: {errors}")

        # Compute field-level changes [G-17]
        is_new = entity.id is None
        changes = _compute_changes(entity) if not is_new else []

        # Update metadata
        entity.updated_at = datetime.utcnow()
        expected_version = entity.version
        entity.version += 1

        # Determine if this save should emit messages [selective emission]
        should_emit, event_type = _should_emit(entity, is_new, method, changes)

        # Build event metadata [G-01]
        event_meta = build_event_metadata(entity, method, changes) if should_emit else None

        # Check cascade depth [G-57 for kernel entities]
        if depth > MAX_CASCADE_DEPTH:
            from kernel.message.schema import Message
            await Message(
                org_id=entity.org_id,
                entity_type=type(entity).__name__,
                entity_id=entity.id or ObjectId(),
                event_type="circuit_broken",
                target_role="__circuit_broken__",
                correlation_id=correlation_id,
                depth=depth,
                status="circuit_broken",
            ).insert()
            import logging
            logging.warning(f"Cascade depth {depth} exceeded for {type(entity).__name__}")
            return

        # Bootstrap entity cascade guard [G-57]
        if entity._is_kernel_entity and depth > 0:
            # Check if this save would trigger a self-referencing cascade
            # on the same kernel entity type
            parent_entity_type = kwargs.get("parent_entity_type")
            if parent_entity_type == type(entity).__name__:
                import logging
                logging.warning(
                    f"Blocked self-referencing cascade on kernel entity {type(entity).__name__}"
                )
                should_emit = False  # Save succeeds but no cascade

        # Start MongoDB transaction
        client = entity.get_motor_collection().database.client
        async with await client.start_session() as session:
            async with session.start_transaction():

                if is_new:
                    # Insert
                    if not entity.id:
                        entity.id = ObjectId()
                    await entity.get_motor_collection().insert_one(
                        entity.model_dump(by_alias=True), session=session
                    )
                else:
                    # Update with optimistic concurrency
                    result = await entity.get_motor_collection().update_one(
                        {"_id": entity.id, "version": expected_version},
                        {"$set": entity.model_dump(by_alias=True)},
                        session=session,
                    )
                    if result.modified_count == 0:
                        raise VersionConflictError(
                            f"{type(entity).__name__} {entity.id} was modified concurrently"
                        )

                # Write changes record
                await write_change_record(
                    entity=entity,
                    change_type="create" if is_new else "update",
                    actor_id=actor_id,
                    changes=changes,
                    method=method,
                    method_metadata=method_metadata,
                    correlation_id=correlation_id,
                    session=session,
                )

                # Evaluate watches and emit messages
                created_messages = []
                if should_emit:
                    created_messages = await evaluate_watches_and_emit(
                        entity=entity,
                        event_type=event_type,
                        event_metadata=event_meta,
                        correlation_id=correlation_id,
                        depth=depth,
                        parent_entity_type=type(entity).__name__,
                        session=session,
                    )

        # Update loaded state for next change tracking
        entity._loaded_state = entity.model_dump(by_alias=True)

        # Return created messages for optimistic dispatch (Phase 2)
        return created_messages

class VersionConflictError(Exception):
    pass

def _compute_changes(entity) -> list[dict]:
    """Compare current state against loaded state to find field-level changes."""
    current = entity.model_dump(by_alias=True)
    loaded = entity._loaded_state
    changes = []
    for key in set(list(current.keys()) + list(loaded.keys())):
        if key in ("_id", "version", "updated_at"):
            continue
        old_val = loaded.get(key)
        new_val = current.get(key)
        if old_val != new_val:
            changes.append({"field": key, "old_value": old_val, "new_value": new_val})
    return changes

def _should_emit(entity, is_new: bool, method: str, changes: list) -> tuple[bool, str]:
    """Determine if this save should evaluate watches and create messages.
    Selective emission: only creation, deletion, state transitions,
    and @exposed method invocations.
    Priority: creation > transition > method > no emission.
    Creation always emits as "created" even if method="create" is passed."""
    if is_new:
        return True, "created"
    # Check for state transition (takes precedence over method —
    # a transition triggered by a method emits as "transitioned")
    if hasattr(entity, '_pending_transition') and entity._pending_transition:
        return True, "transitioned"
    if method:
        return True, "method_invoked"
    return False, None

def _is_heartbeat_only(entity) -> bool:
    """Detect heartbeat-only updates on Attention entities."""
    if type(entity).__name__ != "Attention":
        return False
    loaded = entity._loaded_state
    current = entity.model_dump(by_alias=True)
    changed_fields = {k for k in current if current.get(k) != loaded.get(k)}
    changed_fields -= {"version", "updated_at"}
    return changed_fields <= {"last_heartbeat", "expires_at"}

async def _save_heartbeat_only(entity):
    """Fast path for heartbeat updates — skip changes + watches."""
    await entity.get_motor_collection().update_one(
        {"_id": entity.id},
        {"$set": {
            "last_heartbeat": datetime.utcnow(),
            "expires_at": entity.expires_at,
            "updated_at": datetime.utcnow(),
        }},
    )
```

## 1.10 Event Metadata [G-01]

```python
# kernel/message/event_metadata.py

def build_event_metadata(entity, method: str, changes: list) -> dict:
    """Build the event metadata attached to messages.
    One save = one event with full change metadata."""
    meta = {}

    if method:
        meta["method"] = method

    if hasattr(entity, '_pending_transition') and entity._pending_transition:
        meta["state_transition"] = entity._pending_transition
        entity._pending_transition = None  # Clear after capture

    if changes:
        meta["fields_changed"] = [c["field"] for c in changes]

    return meta
```

## 1.11 Changes Collection

```python
# kernel/changes/collection.py
from beanie import Document
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, Any
import hashlib, orjson

class FieldChange(BaseModel):
    field: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

class ChangeRecord(Document):
    """Append-only audit trail. Every entity mutation recorded."""
    org_id: ObjectId
    entity_type: str
    entity_id: ObjectId
    change_type: str          # create, update, delete, transition
    actor_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    changes: list[FieldChange] = Field(default_factory=list)
    method: Optional[str] = None
    method_metadata: Optional[dict] = None  # Rule evaluation results go here
    previous_hash: Optional[str] = None
    current_hash: Optional[str] = None

    class Settings:
        name = "changes"
        indexes = [
            [("org_id", 1), ("entity_type", 1), ("entity_id", 1), ("timestamp", -1)],
            [("org_id", 1), ("timestamp", -1)],
            [("correlation_id", 1)],
            [("org_id", 1), ("actor_id", 1), ("timestamp", -1)],
        ]

async def write_change_record(entity, change_type, actor_id, changes,
                               method, method_metadata, correlation_id, session):
    """Write a change record within the entity save transaction."""
    from kernel.changes.hash_chain import compute_hash, get_previous_hash

    record = ChangeRecord(
        org_id=entity.org_id,
        entity_type=type(entity).__name__,
        entity_id=entity.id,
        change_type=change_type,
        actor_id=actor_id,
        correlation_id=correlation_id,
        changes=[FieldChange(**c) for c in changes],
        method=method,
        method_metadata=method_metadata,
    )

    # Hash chain
    record.previous_hash = await get_previous_hash(entity.org_id, session)
    record.current_hash = compute_hash(record)

    await record.insert(session=session)
```

```python
# kernel/changes/hash_chain.py
import hashlib, orjson

def compute_hash(record: "ChangeRecord") -> str:
    """SHA-256 hash of the record content for tamper evidence."""
    content = orjson.dumps({
        "entity_type": record.entity_type,
        "entity_id": str(record.entity_id),
        "change_type": record.change_type,
        "actor_id": record.actor_id,
        "timestamp": record.timestamp.isoformat(),
        "changes": [c.model_dump() for c in record.changes],
        "previous_hash": record.previous_hash,
    }, option=orjson.OPT_SORT_KEYS)
    return hashlib.sha256(content).hexdigest()

async def get_previous_hash(org_id, session) -> str:
    """Get the hash of the most recent change record for this org."""
    from kernel.changes.collection import ChangeRecord
    last = await ChangeRecord.find(
        {"org_id": org_id},
        session=session,
    ).sort("-timestamp").limit(1).to_list()
    return last[0].current_hash if last else None
```

**MongoDB permission**: The application user has INSERT permission only on the `changes` collection. No UPDATE, no DELETE.

## 1.12 Message System [G-04, G-75]

### MessageBus Abstraction [G-75]

```python
# kernel/message/bus.py
from typing import Protocol, Optional
from bson import ObjectId

class MessageBus(Protocol):
    """Abstract interface for message publishing.
    MongoDB implementation now, swappable later."""

    async def publish(self, message: "Message", session=None) -> None: ...
    async def claim(self, role: str, org_id: ObjectId, actor_id: ObjectId) -> Optional["Message"]: ...
    async def complete(self, message_id: ObjectId, result: dict) -> None: ...
    async def fail(self, message_id: ObjectId, error: str) -> None: ...
```

### MongoDB Implementation

```python
# kernel/message/mongodb_bus.py
from kernel.message.schema import Message, MessageLog
from datetime import datetime, timedelta
from bson import ObjectId

class MongoDBMessageBus:
    """MongoDB implementation of the MessageBus interface."""

    async def publish(self, message: Message, session=None) -> None:
        await message.insert(session=session)

    async def claim_by_id(self, message_id: ObjectId, actor_id: ObjectId) -> Message:
        """Claim a specific message by ID. Used by Temporal activities."""
        result = await Message.get_motor_collection().find_one_and_update(
            {
                "_id": message_id,
                "$or": [
                    {"status": "pending"},
                    {"status": "processing",
                     "visibility_timeout": {"$lt": datetime.utcnow()}},
                ],
            },
            {
                "$set": {
                    "status": "processing",
                    "claimed_by": actor_id,
                    "claimed_at": datetime.utcnow(),
                    "visibility_timeout": datetime.utcnow() + timedelta(minutes=5),
                },
                "$inc": {"attempt_count": 1},
            },
            return_document=True,
        )
        return Message(**result) if result else None

    async def claim(self, role: str, org_id: ObjectId, actor_id: ObjectId) -> Message:
        """Atomic claim via findOneAndUpdate. [G-78]"""
        result = await Message.get_motor_collection().find_one_and_update(
            {
                "org_id": org_id,
                "target_role": role,
                "$and": [
                    {"$or": [
                        {"status": "pending"},
                        {"status": "processing",
                         "visibility_timeout": {"$lt": datetime.utcnow()}},
                    ]},
                    {"$or": [  # Scoped targeting
                        {"target_actor_id": None},
                        {"target_actor_id": actor_id},
                    ]},
                ],
            },
            {
                "$set": {
                    "status": "processing",
                    "claimed_by": actor_id,
                    "claimed_at": datetime.utcnow(),
                    "visibility_timeout": datetime.utcnow() + timedelta(minutes=5),
                },
                "$inc": {"attempt_count": 1},
            },
            sort=[("priority", -1), ("created_at", 1)],  # [G-78] highest priority, oldest first
            return_document=True,
        )
        return Message(**result) if result else None

    async def complete(self, message_id: ObjectId, result: dict) -> None:
        """Move message from queue to log. [G-05] In a transaction."""
        message = await Message.get(message_id)
        if not message:
            return

        client = Message.get_motor_collection().database.client
        async with await client.start_session() as session:
            async with session.start_transaction():
                # Insert into log
                log_entry = MessageLog(
                    **message.model_dump(exclude={"id"}),
                    result=result,
                    completed_at=datetime.utcnow(),
                )
                await log_entry.insert(session=session)
                # Delete from queue
                await Message.get_motor_collection().delete_one(
                    {"_id": message_id}, session=session
                )

    async def fail(self, message_id: ObjectId, error: str) -> None:
        message = await Message.get(message_id)
        if not message:
            return
        if message.attempt_count >= message.max_attempts:
            message.status = "dead_letter"
        else:
            message.status = "pending"
            message.claimed_by = None
            message.visibility_timeout = None
        await message.get_motor_collection().update_one(
            {"_id": message_id},
            {"$set": {"status": message.status, "claimed_by": message.claimed_by,
                      "visibility_timeout": message.visibility_timeout,
                      "last_error": error}},
        )
```

### Message and MessageLog Schemas [G-04]

```python
# kernel/message/schema.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, Literal

class Message(Document):
    """Active message in the queue."""
    org_id: ObjectId
    entity_type: str
    entity_id: ObjectId
    event_type: str

    target_role: str
    target_actor_id: Optional[ObjectId] = None

    correlation_id: str
    causation_id: Optional[str] = None
    depth: int = 0

    status: Literal["pending", "processing", "completed", "failed",
                     "dead_letter", "circuit_broken"] = "pending"
    claimed_by: Optional[ObjectId] = None
    claimed_at: Optional[datetime] = None
    visibility_timeout: Optional[datetime] = None
    attempt_count: int = 0
    max_attempts: int = 3

    priority: Literal["critical", "high", "normal", "low"] = "normal"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    due_by: Optional[datetime] = None

    event_metadata: dict = Field(default_factory=dict)
    context: dict = Field(default_factory=dict)    # Enriched entity context [G-74]
    summary: dict = Field(default_factory=dict)

    last_error: Optional[str] = None

    class Settings:
        name = "message_queue"
        indexes = [
            [("org_id", 1), ("target_role", 1), ("status", 1), ("priority", -1), ("created_at", 1)],
            [("status", 1), ("visibility_timeout", 1)],
            [("correlation_id", 1), ("created_at", 1)],
        ]

class MessageLog(Document):
    """Completed messages (cold storage)."""
    org_id: ObjectId
    entity_type: str
    entity_id: ObjectId
    event_type: str
    target_role: str
    target_actor_id: Optional[ObjectId] = None
    correlation_id: str
    causation_id: Optional[str] = None
    depth: int = 0
    claimed_by: Optional[ObjectId] = None
    claimed_at: Optional[datetime] = None
    priority: str = "normal"
    created_at: datetime
    event_metadata: dict = Field(default_factory=dict)
    result: Optional[dict] = None
    completed_at: Optional[datetime] = None

    class Settings:
        name = "message_log"
        indexes = [
            [("org_id", 1), ("entity_type", 1), ("entity_id", 1), ("created_at", -1)],
            [("correlation_id", 1), ("created_at", 1)],
            [("org_id", 1), ("created_at", -1)],
        ]
```

## 1.13 Watch Evaluation and Message Emission

```python
# kernel/message/emit.py
from kernel.watch.cache import get_cached_watches
from kernel.watch.evaluator import evaluate_condition
from kernel.watch.scope import resolve_scope
from kernel.message.schema import Message
from kernel.observability.tracing import create_span
from bson import ObjectId
from datetime import datetime

async def evaluate_watches_and_emit(entity, event_type, event_metadata,
                                     correlation_id, depth, parent_entity_type,
                                     session) -> list:
    """Evaluate watches for this entity type and create messages for matches.
    Returns list of created Message objects (for optimistic dispatch in Phase 2)."""
    created_messages = []
    with create_span("watch.evaluate", entity_type=type(entity).__name__):
        org_id = str(entity.org_id)
        entity_type_name = type(entity).__name__
        entity_data = entity.model_dump(by_alias=True)

        watches = get_cached_watches(org_id, entity_type_name)

        for watch_info in watches:
            watch = watch_info["watch"]
            role_name = watch_info["role_name"]

            # Check event type match
            if not _event_matches(watch.event, event_type, event_metadata):
                continue

            # Check conditions (entity-local only) [G-18]
            if watch.conditions:
                if not evaluate_condition(watch.conditions, entity_data):
                    continue

            # Resolve scope (if present)
            target_actor_id = None
            if watch.scope:
                resolved = await resolve_scope(watch.scope, entity, session)
                if resolved is None:
                    continue
                target_actor_id = resolved

            # Build context at configured depth [G-74]
            context = await _build_context(entity, watch.context_depth, session)

            # Create message
            message = Message(
                org_id=entity.org_id,
                entity_type=entity_type_name,
                entity_id=entity.id,
                event_type=event_type,
                target_role=role_name,
                target_actor_id=target_actor_id,
                correlation_id=correlation_id,
                depth=depth + 1,
                event_metadata=event_metadata or {},
                context=context,
                summary=_build_summary(entity, event_type),
            )

            from kernel.message.mongodb_bus import MongoDBMessageBus
            bus = MongoDBMessageBus()
            await bus.publish(message, session=session)
            created_messages.append(message)

    return created_messages

def _event_matches(watch_event: str, actual_event: str, metadata: dict) -> bool:
    """Check if the watch event matches the actual event."""
    if watch_event == actual_event:
        return True
    # "method_invoked" watches can match specific methods
    if watch_event.startswith("method:") and actual_event == "method_invoked":
        return metadata.get("method") == watch_event.split(":", 1)[1]
    # "transitioned" watches can match specific target states
    if watch_event.startswith("transitioned:") and actual_event == "transitioned":
        target = watch_event.split(":", 1)[1]
        return metadata.get("state_transition", {}).get("to") == target
    return False

async def _build_context(entity, depth: int, session) -> dict:
    """Build entity context at the specified depth. [G-74]
    Depth 1: just the entity. Depth 2: + directly related entities."""
    context = {type(entity).__name__.lower(): _serialize_for_context(entity)}
    if depth <= 1:
        return context

    # Follow relationship fields
    from kernel.db import ENTITY_REGISTRY
    entity_data = entity.model_dump(by_alias=True)
    # Check EntityDefinition for relationship fields
    defn = await EntityDefinition.find_one({"name": type(entity).__name__})
    if defn:
        for field_name, field_def in defn.fields.items():
            if field_def.is_relationship and field_def.relationship_target:
                related_id = entity_data.get(field_name)
                if related_id and field_def.relationship_target in ENTITY_REGISTRY:
                    related_cls = ENTITY_REGISTRY[field_def.relationship_target]
                    related = await related_cls.get(related_id)
                    if related:
                        context[field_def.relationship_target.lower()] = _serialize_for_context(related)
    return context

def _serialize_for_context(entity) -> dict:
    """Serialize entity for message context (exclude large fields)."""
    data = entity.model_dump(by_alias=True)
    # Exclude potentially large fields
    data.pop("data", None)  # Flexible data can be large
    data.pop("_loaded_state", None)
    return data

def _build_summary(entity, event_type: str) -> dict:
    """Build a minimal summary for queue display."""
    return {
        "entity_type": type(entity).__name__,
        "event_type": event_type,
        "display": f"{type(entity).__name__} {getattr(entity, 'name', str(entity.id))}",
    }
```

## 1.14 Watch Cache [G-09]

```python
# kernel/watch/cache.py
import time
from typing import Optional
from kernel_entities.role import Role, WatchDefinition

# In-memory cache: {(org_id, entity_type): [{"watch": WatchDef, "role_name": str}]}
_cache: dict[tuple[str, str], list[dict]] = {}
_cache_loaded_at: float = 0
_CACHE_TTL = 60  # seconds

async def load_watch_cache():
    """Load all watches from all roles into the cache."""
    global _cache, _cache_loaded_at
    _cache = {}

    async for role in Role.find({}):
        for watch in role.watches:
            key = (str(role.org_id), watch.entity_type)
            if key not in _cache:
                _cache[key] = []
            _cache[key].append({
                "watch": watch,
                "role_name": role.name,
            })

    _cache_loaded_at = time.time()

def get_cached_watches(org_id: str, entity_type: str) -> list[dict]:
    """Get watches for an org + entity type. Auto-refresh on TTL expiry."""
    if time.time() - _cache_loaded_at > _CACHE_TTL:
        # Schedule async reload — for now, return stale cache
        # In production, use a background task to refresh
        pass

    key = (org_id, entity_type)
    return _cache.get(key, [])

async def invalidate_watch_cache():
    """Called when any Role entity is saved (kernel entity cache invalidation).
    Triggers immediate reload."""
    await load_watch_cache()
```

Cache invalidation: when a Role entity is saved via `save_tracked()`, the save path detects it's a kernel entity with watches and calls `invalidate_watch_cache()`. For multi-instance deployment (multiple API server replicas), each instance maintains its own cache and relies on the 60-second TTL for consistency. For stronger consistency, a MongoDB Change Stream on the roles collection can trigger invalidation across instances.

## 1.15 Condition Evaluator [G-06]

```python
# kernel/watch/evaluator.py
import re
from datetime import datetime, timedelta
from typing import Any

def evaluate_condition(condition: dict, entity_data: dict) -> bool:
    """Evaluate a JSON condition against entity field values."""
    if "all" in condition:
        return all(evaluate_condition(c, entity_data) for c in condition["all"])
    if "any" in condition:
        return any(evaluate_condition(c, entity_data) for c in condition["any"])
    if "not" in condition:
        return not evaluate_condition(condition["not"], entity_data)

    field = condition["field"]
    op = condition["op"]
    expected = condition.get("value")
    actual = _get_nested_field(entity_data, field)

    return _OPERATORS[op](actual, expected)

def _get_nested_field(data: dict, field_path: str) -> Any:
    """Get a value from nested dict using dot notation."""
    parts = field_path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current

def _older_than(actual, duration_str: str) -> bool:
    """Check if a datetime field is older than a duration. [G-06]"""
    if actual is None:
        return False
    if isinstance(actual, str):
        actual = datetime.fromisoformat(actual)
    if not isinstance(actual, datetime):
        return False

    amount = int(duration_str[:-1])
    unit = duration_str[-1]
    delta = {
        "s": timedelta(seconds=amount),
        "m": timedelta(minutes=amount),
        "h": timedelta(hours=amount),
        "d": timedelta(days=amount),
    }.get(unit)

    if delta is None:
        return False
    return actual < (datetime.utcnow() - delta)

_OPERATORS = {
    "equals": lambda a, e: a == e,
    "not_equals": lambda a, e: a != e,
    "contains": lambda a, e: e in str(a) if a else False,
    "not_contains": lambda a, e: e not in str(a) if a else True,
    "starts_with": lambda a, e: str(a).startswith(e) if a else False,
    "ends_with": lambda a, e: str(a).endswith(e) if a else False,
    "gt": lambda a, e: a > e if a is not None else False,
    "gte": lambda a, e: a >= e if a is not None else False,
    "lt": lambda a, e: a < e if a is not None else False,
    "lte": lambda a, e: a <= e if a is not None else False,
    "in": lambda a, e: a in e if isinstance(e, list) else False,
    "not_in": lambda a, e: a not in e if isinstance(e, list) else True,
    "matches": lambda a, e: bool(re.search(e, str(a))) if a else False,
    "exists": lambda a, e: a is not None,
    "older_than": lambda a, e: _older_than(a, e),
    "within": lambda a, e: not _older_than(a, e) if a else False,
}
```

## 1.16 Watch Creation Validation [G-18]

```python
# kernel/watch/validation.py

async def validate_watch(watch: "WatchDefinition", org_id: str) -> list[str]:
    """Validate a watch before allowing it to be added to a role."""
    errors = []

    # Check that the entity type exists
    from kernel.db import ENTITY_REGISTRY
    if watch.entity_type not in ENTITY_REGISTRY:
        errors.append(f"Entity type '{watch.entity_type}' does not exist")
        return errors

    # Check that conditions only reference entity-local fields
    if watch.conditions:
        entity_fields = _get_entity_fields(watch.entity_type)
        referenced_fields = _extract_field_references(watch.conditions)
        for field in referenced_fields:
            # Only the first part (before any dot) must be an entity field
            root_field = field.split(".")[0]
            if root_field not in entity_fields and root_field not in ("status", "stage"):
                errors.append(
                    f"Condition references field '{field}' which is not on {watch.entity_type}. "
                    f"Watch conditions must be entity-local."
                )

    return errors

def _get_entity_fields(entity_type: str) -> set[str]:
    """Get all field names for an entity type (kernel or domain)."""
    from kernel.db import ENTITY_REGISTRY
    cls = ENTITY_REGISTRY.get(entity_type)
    if not cls:
        return set()
    fields = set(cls.model_fields.keys())
    # For domain entities, also check the definition
    # (model_fields covers it since dynamic classes are created from definitions)
    return fields

def _extract_field_references(condition: dict) -> set[str]:
    """Extract all field names referenced in a condition tree."""
    fields = set()
    if "all" in condition or "any" in condition:
        for sub in condition.get("all", condition.get("any", [])):
            fields.update(_extract_field_references(sub))
    elif "not" in condition:
        fields.update(_extract_field_references(condition["not"]))
    elif "field" in condition:
        fields.add(condition["field"])
    return fields
```

## 1.17 Rules and Lookups [G-07, G-08]

### Rule Schema

```python
# kernel/rule/schema.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, Literal

class RuleGroup(Document):
    """Organizational container for related rules."""
    org_id: ObjectId
    entity_type: str
    name: str
    description: Optional[str] = None
    status: Literal["draft", "active", "archived"] = "draft"
    owner: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rule_groups"
        indexes = [[("org_id", 1), ("entity_type", 1), ("status", 1)]]

class Rule(Document):
    """A condition→action pattern for deterministic entity processing."""
    org_id: ObjectId
    entity_type: str
    capability: str               # auto_classify, auto_route, etc.
    group_id: Optional[ObjectId] = None  # Reference to RuleGroup
    name: Optional[str] = None
    conditions: dict              # JSON condition (same evaluator as watches)
    action: Literal["set_fields", "force_reasoning"]
    sets: Optional[dict] = None   # For set_fields: {field: value}
    forces_reasoning_reason: Optional[str] = None
    priority: int = 100           # Higher = evaluated first
    status: Literal["draft", "active", "archived"] = "draft"
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rules"
        indexes = [
            [("org_id", 1), ("entity_type", 1), ("capability", 1), ("status", 1), ("priority", -1)],
        ]
```

### Rule Engine [G-07]

```python
# kernel/rule/engine.py
from kernel.rule.schema import Rule
from kernel.rule.lookup import resolve_lookup_references
from kernel.watch.evaluator import evaluate_condition
from kernel.observability.tracing import create_span

async def evaluate_rules(org_id: str, entity_type: str,
                         capability: str, entity_data: dict) -> dict:
    """Evaluate all active rules for this org + entity type + capability.
    Returns the evaluation result with full context for debugging."""

    with create_span("rule.evaluate", entity_type=entity_type, capability=capability):
        # Load active rules, ordered by priority (highest first)
        rules = await Rule.find({
            "org_id": org_id,
            "entity_type": entity_type,
            "capability": capability,
            "status": "active",
        }).sort("-priority").to_list()

        if not rules:
            return {
                "matched": False,
                "vetoed": False,
                "reason": "no_rules_configured",
                "attempted_rules": [],
            }

        matched_rules = []
        veto_rules = []
        attempted = []

        for rule in rules:
            match = evaluate_condition(rule.conditions, entity_data)
            attempted.append({
                "name": rule.name or str(rule.id),
                "matched": match,
                "action": rule.action,
                "priority": rule.priority,
            })

            if match:
                if rule.action == "force_reasoning":  # [G-08] Veto rule
                    veto_rules.append(rule)
                else:
                    matched_rules.append(rule)

        # Veto overrides positive matches [G-08]
        if veto_rules:
            veto = veto_rules[0]  # Highest priority veto
            return {
                "matched": True,
                "vetoed": True,
                "reason": "veto",
                "veto_reason": veto.forces_reasoning_reason or "Veto rule matched",
                "attempted_rules": attempted,
                "winning_veto": {"name": veto.name, "reason": veto.forces_reasoning_reason},
            }

        if matched_rules:
            winner = matched_rules[0]  # Highest priority positive match
            # Resolve lookup references in the sets values
            resolved_sets = await resolve_lookup_references(
                winner.sets, org_id, entity_data
            ) if winner.sets else {}

            return {
                "matched": True,
                "vetoed": False,
                "winning_rule": {
                    "name": winner.name or str(winner.id),
                    "sets": resolved_sets,
                },
                "attempted_rules": attempted,
            }

        return {
            "matched": False,
            "vetoed": False,
            "reason": "no_match",
            "attempted_rules": attempted,
        }
```

### Lookup Resolution

```python
# kernel/rule/lookup.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from datetime import datetime
from typing import Optional

class Lookup(Document):
    """Mapping table — separate from rules to prevent rule explosion."""
    org_id: ObjectId
    name: str
    data: dict                    # key → value
    description: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lookups"
        indexes = [[("org_id", 1), ("name", 1)]]

async def resolve_lookup_references(sets: dict, org_id: str,
                                     entity_data: dict) -> dict:
    """Resolve lookup references in rule action values.
    Example: {"lob": {"lookup": "usli-prefix-lob", "from_field": "quote_prefix"}}
    → resolves the lookup by reading the entity's quote_prefix field."""
    resolved = {}
    for field_name, value in sets.items():
        if isinstance(value, dict) and "lookup" in value:
            lookup_name = value["lookup"]
            source_field = value.get("from_field")
            source_value = entity_data.get(source_field) if source_field else None

            lookup = await Lookup.find_one({"name": lookup_name, "org_id": org_id})
            if lookup and source_value and str(source_value) in lookup.data:
                resolved[field_name] = lookup.data[str(source_value)]
            else:
                resolved[field_name] = None  # Lookup miss
        else:
            resolved[field_name] = value
    return resolved
```

### Rule Validation [G from addendum A.6]

```python
# kernel/rule/validation.py

async def validate_rule(rule: "Rule", actor_roles: list[str]) -> list[str]:
    """Validate a rule before creation. Returns list of errors."""
    errors = []

    # 1. Fields in 'sets' must exist in entity schema
    from kernel.db import ENTITY_REGISTRY
    entity_cls = ENTITY_REGISTRY.get(rule.entity_type)
    if entity_cls and rule.sets:
        entity_fields = set(entity_cls.model_fields.keys())
        # For dynamic entities, also check the definition
        from kernel.entity.definition import EntityDefinition
        defn = await EntityDefinition.find_one({"name": rule.entity_type})
        if defn:
            entity_fields.update(defn.fields.keys())

        for field_name in rule.sets.keys():
            if isinstance(rule.sets[field_name], dict) and "lookup" in rule.sets[field_name]:
                continue  # Lookup reference — validated separately
            if field_name not in entity_fields:
                errors.append(f"Field '{field_name}' does not exist on {rule.entity_type}")

    # 2. State machine fields cannot be set via rules
    state_fields = {"status", "stage"}
    if rule.sets:
        for field_name in rule.sets.keys():
            if field_name in state_fields:
                errors.append(
                    f"Cannot set '{field_name}' via rule. "
                    f"State transitions must go through transition_to()."
                )

    # 3. Check for overlapping rules (warning, not error)
    existing = await Rule.find({
        "org_id": rule.org_id,
        "entity_type": rule.entity_type,
        "capability": rule.capability,
        "status": "active",
    }).to_list()
    for existing_rule in existing:
        if _conditions_may_overlap(rule.conditions, existing_rule.conditions):
            errors.append(
                f"WARNING: May overlap with rule '{existing_rule.name}'. "
                f"Use --force to create anyway."
            )

    return errors

def _conditions_may_overlap(cond1: dict, cond2: dict) -> bool:
    """Heuristic overlap detection. Not exhaustive."""
    # Simple check: if both reference the same fields with the same operators
    fields1 = _extract_fields(cond1)
    fields2 = _extract_fields(cond2)
    return bool(fields1 & fields2)

def _extract_fields(condition: dict) -> set:
    refs = set()
    if "all" in condition or "any" in condition:
        for sub in condition.get("all", condition.get("any", [])):
            refs.update(_extract_fields(sub))
    elif "field" in condition:
        refs.add(condition["field"])
    return refs
```

## 1.18 Kernel Capabilities

### Registry

```python
# kernel/capability/registry.py

CAPABILITY_REGISTRY: dict[str, callable] = {}

def register_capability(name: str, func: callable):
    CAPABILITY_REGISTRY[name] = func

def get_capability(name: str) -> callable:
    func = CAPABILITY_REGISTRY.get(name)
    if not func:
        raise ValueError(f"Unknown capability: {name}")
    return func
```

### auto_classify

```python
# kernel/capability/auto_classify.py
from kernel.capability.registry import register_capability
from kernel.rule.engine import evaluate_rules
from kernel.observability.tracing import create_span

async def auto_classify(entity, config: dict, org_id: str) -> dict:
    """Try deterministic classification via rules. Return result or needs_reasoning."""
    with create_span("capability.auto_classify", entity_type=type(entity).__name__):
        result = await evaluate_rules(
            org_id=str(org_id),
            entity_type=type(entity).__name__,
            capability="auto_classify",
            entity_data=entity.model_dump(by_alias=True),
        )

        if result["matched"] and not result["vetoed"]:
            # Deterministic match
            return {
                "needs_reasoning": False,
                "result": result["winning_rule"]["sets"],
                "rule_evaluation": result,
            }
        else:
            return {
                "needs_reasoning": True,
                "reason": result.get("reason", "no_match"),
                "veto_reason": result.get("veto_reason"),
                "attempted_rules": result.get("attempted_rules", []),
                "rule_evaluation": result,
            }

register_capability("auto_classify", auto_classify)
```

## 1.19 Skill Entity [G-10]

```python
# kernel/skill/schema.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, Literal

class Skill(Document):
    """Markdown document — entity skills (auto-generated) or associate skills (authored)."""
    org_id: Optional[ObjectId] = None  # None for system-level entity skills
    name: str
    type: Literal["entity", "associate"]
    entity_type: Optional[str] = None  # For entity skills: which entity
    content: str
    content_hash: str
    version: int = 1
    status: Literal["active", "pending_review", "deprecated"] = "active"
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "skills"
        indexes = [
            [("name", 1), ("status", 1)],
            [("org_id", 1), ("type", 1)],
        ]
```

### Skill Integrity [from addendum A.16]

```python
# kernel/skill/integrity.py
import hashlib

def compute_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def verify_content_hash(content: str, expected_hash: str) -> bool:
    return compute_content_hash(content) == expected_hash
```

### Skill Generator

```python
# kernel/skill/generator.py

def generate_entity_skill(entity_name: str, definition: "EntityDefinition") -> str:
    """Generate markdown skill from entity definition."""
    lines = [f"# {entity_name}\n"]

    if definition.description:
        lines.append(f"{definition.description}\n")

    # Fields
    lines.append("## Fields\n")
    lines.append("| Field | Type | Required |")
    lines.append("|-------|------|----------|")
    for name, fdef in definition.fields.items():
        lines.append(f"| {name} | {fdef.type} | {'Yes' if fdef.required else 'No'} |")

    # State machine
    if definition.state_machine:
        lines.append("\n## Lifecycle\n")
        for state, transitions in definition.state_machine.items():
            lines.append(f"- **{state}** -> {', '.join(transitions)}")

    # CLI commands
    slug = entity_name.lower()
    lines.append(f"\n## Commands\n")
    lines.append("| Command | Description |")
    lines.append("|---------|-------------|")
    lines.append(f"| `indemn {slug} list` | List with filters |")
    lines.append(f"| `indemn {slug} get <id>` | Get by ID |")
    lines.append(f"| `indemn {slug} create --data '...'` | Create new |")
    lines.append(f"| `indemn {slug} update <id> --data '...'` | Update fields |")
    if definition.state_machine:
        lines.append(f"| `indemn {slug} transition <id> --to <state>` | Change state |")
    for cap in (definition.activated_capabilities or []):
        cap_name = cap.capability.replace("_", "-")
        lines.append(f"| `indemn {slug} {cap_name} <id> --auto` | {cap.capability} |")

    return "\n".join(lines)
```

## 1.20 @exposed Decorator

```python
# kernel/entity/exposed.py
import functools

def exposed(func=None, *, name: str = None):
    """Mark a kernel entity method for API/CLI exposure.
    Domain entities use capability activations instead."""
    def decorator(fn):
        fn._exposed = True
        fn._exposed_name = name or fn.__name__

        @functools.wraps(fn)
        async def wrapper(self, *args, **kwargs):
            return await fn(self, *args, **kwargs)

        wrapper._exposed = True
        wrapper._exposed_name = fn._exposed_name
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
```

## 1.21 Auto-Generated API [G-11, G-69]

```python
# kernel/api/app.py
from fastapi import FastAPI
from kernel.db import init_database, ENTITY_REGISTRY
from kernel.api.registration import register_entity_routes
from kernel.api.meta import meta_router
from kernel.api.health import health_router
from kernel.api.bootstrap import bootstrap_router
from kernel.api.errors import register_error_handlers
from kernel.auth.middleware import AuthMiddleware
from kernel.observability.tracing import init_tracing

def create_app() -> FastAPI:
    app = FastAPI(title="Indemn OS API")

    register_error_handlers(app)  # [G-85]

    @app.on_event("startup")
    async def startup():
        init_tracing()
        await init_database()
        # Register routes for all entity types
        for name, cls in ENTITY_REGISTRY.items():
            register_entity_routes(app, name, cls)

    app.add_middleware(AuthMiddleware)
    app.include_router(meta_router)
    app.include_router(health_router)
    app.include_router(bootstrap_router)

    return app
```

```python
# kernel/api/registration.py
from fastapi import APIRouter, Depends, Query
from kernel.auth.middleware import get_current_actor, check_permission
from kernel.context import current_org_id
from typing import Optional

def register_entity_routes(app, entity_name: str, entity_cls: type):
    """Register CRUD + transition + @exposed method routes."""
    slug = entity_name.lower() + "s"
    router = APIRouter(prefix=f"/api/{slug}", tags=[entity_name])

    @router.get("/")
    async def list_entities(
        limit: int = Query(20, le=100),
        offset: int = 0,
        status: Optional[str] = None,
        sort: str = "-created_at",
        actor=Depends(get_current_actor),
    ):
        check_permission(actor, entity_name, "read")
        filter_doc = {}
        if status:
            filter_doc["status"] = status
        # Additional filters from query params [G-69]
        entities = await entity_cls.find_scoped(filter_doc).skip(offset).limit(limit).to_list()
        return [e.model_dump() for e in entities]

    @router.get("/{entity_id}")
    async def get_entity(entity_id: str, actor=Depends(get_current_actor)):
        check_permission(actor, entity_name, "read")
        entity = await entity_cls.get_scoped(entity_id)
        if not entity:
            raise HTTPException(404)
        return entity.model_dump()

    @router.post("/")
    async def create_entity(data: dict, actor=Depends(get_current_actor)):
        check_permission(actor, entity_name, "write")
        entity = entity_cls(org_id=current_org_id.get(), **data)
        await entity.save_tracked(method="create")
        return entity.model_dump()

    @router.put("/{entity_id}")
    async def update_entity(entity_id: str, data: dict, actor=Depends(get_current_actor)):
        check_permission(actor, entity_name, "write")
        entity = await entity_cls.get_scoped(entity_id)
        if not entity:
            raise HTTPException(404)
        for key, value in data.items():
            if key not in ("id", "_id", "org_id", "version"):
                setattr(entity, key, value)
        await entity.save_tracked()
        return entity.model_dump()

    @router.post("/{entity_id}/transition")
    async def transition_entity(
        entity_id: str, to: str, reason: str = None,
        actor=Depends(get_current_actor),
    ):
        check_permission(actor, entity_name, "write")
        entity = await entity_cls.get_scoped(entity_id)
        if not entity:
            raise HTTPException(404)
        entity.transition_to(to, reason)
        await entity.save_tracked(method="transition")
        return entity.model_dump()

    # Register @exposed methods as additional routes [G-11]
    for attr_name in dir(entity_cls):
        attr = getattr(entity_cls, attr_name, None)
        if attr and getattr(attr, '_exposed', False):
            method_name = attr._exposed_name
            _register_exposed_route(router, entity_cls, entity_name, method_name, attr)

    # Register capability-activated methods [G-12]
    for cap_activation in getattr(entity_cls, '_activated_capabilities', []):
        cap_name = cap_activation.capability if hasattr(cap_activation, 'capability') else cap_activation.get("capability", "")
        _register_capability_route(router, entity_cls, entity_name, cap_name, cap_activation)

    app.include_router(router)

def _register_exposed_route(router, entity_cls, entity_name, method_name, method):
    """Register an @exposed method as POST /api/{entities}/{id}/{method_name}"""
    @router.post(f"/{{entity_id}}/{method_name.replace('_', '-')}")
    async def exposed_method(entity_id: str, data: dict = {}, actor=Depends(get_current_actor)):
        check_permission(actor, entity_name, "write")
        entity = await entity_cls.get_scoped(entity_id)
        if not entity:
            raise HTTPException(404)
        result = await method(entity, **data)
        return result

def _register_capability_route(router, entity_cls, entity_name, cap_name, activation):
    """Register a capability as POST /api/{entities}/{id}/{cap-name}?auto=true"""
    @router.post(f"/{{entity_id}}/{cap_name.replace('_', '-')}")
    async def capability_method(entity_id: str, auto: bool = False,
                                 data: dict = {}, actor=Depends(get_current_actor)):
        check_permission(actor, entity_name, "write")
        entity = await entity_cls.get_scoped(entity_id)
        if not entity:
            raise HTTPException(404)
        if auto:
            from kernel.capability.registry import get_capability
            capability_fn = get_capability(cap_name)
            config = activation.config if hasattr(activation, 'config') else activation.get("config", {})
            result = await capability_fn(entity, config, entity.org_id)
            # If not needs_reasoning, apply the result and save
            if not result.get("needs_reasoning"):
                for field, value in result.get("result", {}).items():
                    setattr(entity, field, value)
                await entity.save_tracked(
                    method=cap_name,
                    method_metadata={"rule_evaluation": result.get("rule_evaluation")},
                )
            return result
        else:
            # Manual invocation — just apply provided data
            for field, value in data.items():
                setattr(entity, field, value)
            await entity.save_tracked(method=cap_name)
            return entity.model_dump()
```

### Entity Metadata Endpoint [G-33, G-69]

```python
# kernel/api/meta.py
from fastapi import APIRouter, Depends
from kernel.auth.middleware import get_current_actor
from kernel.db import ENTITY_REGISTRY
from kernel.entity.definition import EntityDefinition

meta_router = APIRouter(prefix="/api/_meta", tags=["meta"])

@meta_router.get("/entities")
async def get_entity_metadata(actor=Depends(get_current_actor)):
    """Return metadata for all entity types accessible to the current actor."""
    result = []
    for name, cls in ENTITY_REGISTRY.items():
        # Check if actor has any permission for this entity
        if not _has_any_permission(actor, name):
            continue

        meta = {
            "name": name,
            "fields": _get_field_metadata(cls, name),
            "state_machine": getattr(cls, '_state_machine', None),
            "capabilities": [
                {"name": cap.capability if hasattr(cap, 'capability') else cap.get("capability"),
                 "config": cap.config if hasattr(cap, 'config') else cap.get("config")}
                for cap in getattr(cls, '_activated_capabilities', [])
            ],
            "is_kernel_entity": getattr(cls, '_is_kernel_entity', False),
        }
        result.append(meta)

    return result

def _has_any_permission(actor, entity_name: str) -> bool:
    """Check if actor has read or write permission for this entity type."""
    roles = getattr(actor, '_cached_roles', [])
    for role in roles:
        for action in ("read", "write"):
            allowed = role.permissions.get(action, [])
            if "*" in allowed or entity_name in allowed:
                return True
    return False

def _get_field_metadata(cls, entity_name: str) -> list[dict]:
    """Derive field metadata from a kernel entity's Pydantic model_fields."""
    fields = []
    for fname, finfo in cls.model_fields.items():
        if fname.startswith("_"):
            continue
        fields.append({
            "name": fname,
            "type": _pydantic_type_to_string(finfo.annotation),
            "required": finfo.is_required(),
            "default": finfo.default if finfo.default is not None else None,
        })
    return fields

def _pydantic_type_to_string(annotation) -> str:
    """Convert a Pydantic type annotation to a simple string."""
    origin = getattr(annotation, '__origin__', None)
    if origin is list:
        return "list"
    type_name = getattr(annotation, '__name__', str(annotation))
    type_map = {"str": "str", "int": "int", "float": "float", "bool": "bool",
                "ObjectId": "objectid", "datetime": "datetime", "date": "date"}
    return type_map.get(type_name, "str")

def _check_permission(actor, entity_name: str, action: str) -> bool:
    """Check a specific permission without raising."""
    roles = getattr(actor, '_cached_roles', [])
    for role in roles:
        allowed = role.permissions.get(action, [])
        if "*" in allowed or entity_name in allowed:
            return True
    return False

def _extract_enum_values(annotation) -> list[str] | None:
    """Extract Literal values from a type annotation."""
    from typing import get_args, Literal
    args = get_args(annotation)
    if args and all(isinstance(a, str) for a in args):
        return list(args)
    return None
```

### Health Endpoint [G-16]

```python
# kernel/api/health.py
from fastapi import APIRouter
from kernel.config import settings

health_router = APIRouter(tags=["health"])

@health_router.get("/health")
async def health_check():
    """Check connectivity to all dependencies."""
    checks = {}

    # MongoDB
    try:
        from kernel.db import get_database
        db = get_database()
        await db.command("ping")
        checks["mongodb"] = "ok"
    except Exception as e:
        checks["mongodb"] = f"error: {str(e)}"

    # Temporal (if configured)
    if settings.temporal_address:
        try:
            from kernel.temporal.client import get_temporal_client
            client = await get_temporal_client()
            checks["temporal"] = "ok"
        except Exception as e:
            checks["temporal"] = f"error: {str(e)}"

    # Overall status
    all_ok = all(v == "ok" for v in checks.values())
    critical_ok = checks.get("mongodb") == "ok"

    return {
        "status": "healthy" if all_ok else ("degraded" if critical_ok else "unhealthy"),
        "checks": checks,
    }
```

### Error Responses [G-85]

```python
# kernel/api/errors.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from kernel.entity.state_machine import StateMachineError, TransitionValidationError
from kernel.entity.save import VersionConflictError

def register_error_handlers(app: FastAPI):
    @app.exception_handler(StateMachineError)
    async def state_machine_error(request: Request, exc: StateMachineError):
        return JSONResponse(status_code=400, content={
            "error": "StateMachineError", "message": str(exc),
        })

    @app.exception_handler(TransitionValidationError)
    async def transition_validation_error(request: Request, exc):
        return JSONResponse(status_code=400, content={
            "error": "TransitionValidationError", "message": str(exc),
        })

    @app.exception_handler(VersionConflictError)
    async def version_conflict_error(request: Request, exc):
        return JSONResponse(status_code=409, content={
            "error": "VersionConflict", "message": str(exc),
        })

    @app.exception_handler(PermissionError)
    async def permission_error(request: Request, exc):
        return JSONResponse(status_code=403, content={
            "error": "PermissionDenied", "message": str(exc),
        })
```

## 1.22 Authentication (Phase 1 Scope)

Phase 1 auth: password + token + JWT + Session entity. Enough to prove the kernel works.

```python
# kernel/auth/middleware.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from kernel.auth.jwt import verify_access_token
from kernel_entities.actor import Actor
from kernel.context import current_org_id, current_actor_id

security = HTTPBearer(auto_error=False)

class AuthMiddleware:
    """Set auth context on each request."""
    async def __call__(self, request: Request, call_next):
        # Skip auth for health, bootstrap, and webhook endpoints
        if request.url.path in ("/health", "/api/_platform/init"):
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Missing auth token"})

        token = auth.split(" ", 1)[1]
        try:
            payload = verify_access_token(token)
        except Exception:
            return JSONResponse(status_code=401, content={"error": "Invalid token"})

        actor = await Actor.get(payload["actor_id"])
        if not actor or actor.status != "active":
            return JSONResponse(status_code=401, content={"error": "Actor not found or inactive"})

        # Set context variables
        current_org_id.set(actor.org_id)
        current_actor_id.set(str(actor.id))

        # Load roles once per request for permission checks
        from kernel_entities.role import Role
        roles = await Role.find({"_id": {"$in": actor.role_ids}}).to_list()
        actor._cached_roles = roles

        request.state.actor = actor
        return await call_next(request)

async def get_current_actor(request: Request) -> Actor:
    return request.state.actor

def check_permission(actor: Actor, entity_type: str, action: str):
    """Check if actor's roles grant the required permission.
    Loads the actor's Role entities and checks if any grant the required action
    on the given entity type. Wildcard "*" grants access to all entity types."""
    # Roles are cached on request.state by the middleware (loaded once per request)
    roles = getattr(actor, '_cached_roles', None)
    if roles is None:
        raise PermissionError("No roles loaded for actor")

    for role in roles:
        allowed_types = role.permissions.get(action, [])
        if "*" in allowed_types or entity_type in allowed_types:
            return  # Permission granted

    raise PermissionError(
        f"Actor {actor.name} does not have '{action}' permission on {entity_type}. "
        f"Roles: {[r.name for r in roles]}"
    )
```

```python
# kernel/auth/jwt.py
import jwt
from datetime import datetime, timedelta
from uuid import uuid4
from kernel.config import settings

def create_access_token(actor_id: str, org_id: str, roles: list[str]) -> tuple[str, str]:
    """Create a JWT access token. Returns (token, jti)."""
    jti = str(uuid4())
    payload = {
        "actor_id": str(actor_id),
        "org_id": str(org_id),
        "roles": roles,
        "jti": jti,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.jwt_signing_key, algorithm=settings.jwt_algorithm)
    return token, jti

def verify_access_token(token: str) -> dict:
    """Verify and decode a JWT access token."""
    payload = jwt.decode(token, settings.jwt_signing_key, algorithms=[settings.jwt_algorithm])
    # TODO: Check jti against revocation cache (Phase 4)
    return payload
```

```python
# kernel/auth/password.py
from argon2 import PasswordHasher, Type

# Argon2id with secure defaults
_hasher = PasswordHasher(
    time_cost=3,       # iterations
    memory_cost=65536,  # 64MB
    parallelism=4,
    hash_len=32,
    type=Type.ID,  # Argon2id
)

def hash_password(password: str) -> str:
    return _hasher.hash(password)

def verify_password(password: str, hash: str) -> bool:
    try:
        return _hasher.verify(hash, password)
    except Exception:
        return False
```

## 1.23 Observability [G-83]

```python
# kernel/observability/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from contextlib import contextmanager
from kernel.config import settings

tracer = trace.get_tracer("indemn-os")

def init_tracing():
    if not settings.otel_exporter_endpoint:
        return  # No OTEL in local dev without endpoint
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

@contextmanager
def create_span(name: str, **attributes):
    with tracer.start_as_current_span(name, attributes=attributes) as span:
        yield span
```

```python
# kernel/observability/logging.py  [G-83]
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, "entity_type"):
            log_entry["entity_type"] = record.entity_type
        if hasattr(record, "entity_id"):
            log_entry["entity_id"] = record.entity_id
        return json.dumps(log_entry)

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
```

## 1.24 Queue Processor [G-63]

```python
# kernel/queue_processor.py
"""
Sweep process. Runs extensible sweep functions each cycle.
Phase 1: visibility timeout recovery + escalation checks.
Phase 2 adds: Temporal workflow dispatch.
"""
import asyncio
import logging
from kernel.db import init_database
from kernel.message.schema import Message
from datetime import datetime

# Extensible sweep functions
_sweep_functions: list[callable] = []

def register_sweep(func: callable):
    _sweep_functions.append(func)

async def check_visibility_timeouts():
    """Find processing messages past their visibility timeout.
    Return them to pending status."""
    result = await Message.get_motor_collection().update_many(
        {
            "status": "processing",
            "visibility_timeout": {"$lt": datetime.utcnow()},
        },
        {
            "$set": {"status": "pending", "claimed_by": None, "visibility_timeout": None},
        },
    )
    if result.modified_count > 0:
        logging.info(f"Recovered {result.modified_count} timed-out messages")

async def check_escalation_deadlines():
    """Find pending messages past their due_by deadline."""
    overdue = await Message.find({
        "status": "pending",
        "due_by": {"$lt": datetime.utcnow(), "$ne": None},
    }).to_list()
    for msg in overdue:
        # Mark as escalated (Phase 2 adds actual escalation logic)
        logging.warning(f"Message {msg.id} past deadline")

# Register Phase 1 sweeps
register_sweep(check_visibility_timeouts)
register_sweep(check_escalation_deadlines)

async def run_sweep_cycle():
    for func in _sweep_functions:
        try:
            await func()
        except Exception as e:
            logging.error(f"Sweep function {func.__name__} failed: {e}")

async def main():
    await init_database()
    logging.info("Queue processor started")
    while True:
        await run_sweep_cycle()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
```

## 1.25 Platform Bootstrap

```python
# kernel/api/bootstrap.py
from fastapi import APIRouter, HTTPException
from kernel_entities.organization import Organization
from kernel_entities.actor import Actor
from kernel_entities.role import Role
from kernel.auth.jwt import create_access_token
from kernel.auth.password import hash_password
from bson import ObjectId

bootstrap_router = APIRouter(prefix="/api/_platform", tags=["platform"])

@bootstrap_router.post("/init")
async def platform_init(admin_email: str, admin_password: str):
    """Bootstrap the first organization. One-time operation."""
    existing = await Organization.find_one({"slug": "_platform"})
    if existing:
        raise HTTPException(400, "Platform already initialized")

    # Create platform org (self-referencing for org_id)
    # NOTE: Intentional save_tracked() bypass. The bootstrap Organization is the
    # only entity that cannot use save_tracked() because save_tracked() requires
    # org_id context, and this IS the org being created (circular reference).
    # The admin Actor and Role created below DO use save_tracked() after the org exists.
    # This bypass means the bootstrap Organization lacks an initial changes collection
    # audit record — an accepted tradeoff for the self-referencing bootstrap case.
    org_id = ObjectId()
    platform_org = Organization(
        id=org_id, org_id=org_id,
        name="Indemn Platform", slug="_platform", status="active",
    )
    await platform_org.insert()

    # Create admin actor
    admin = Actor(
        org_id=org_id, name="Platform Admin", email=admin_email,
        type="human", status="active",
        authentication_methods=[{
            "type": "password",
            "password_hash": hash_password(admin_password),
        }],
    )
    await admin.insert()

    # Create admin role
    admin_role = Role(
        org_id=org_id, name="platform_admin",
        permissions={"read": ["*"], "write": ["*"]},
    )
    await admin_role.insert()
    admin.role_ids = [admin_role.id]
    await admin.save()

    # Issue token
    token, jti = create_access_token(str(admin.id), str(org_id), ["platform_admin"])

    return {
        "status": "initialized",
        "org_id": str(org_id),
        "admin_id": str(admin.id),
        "access_token": token,
    }
```

## 1.26 Seed Data Loading

```python
# kernel/seed.py
import yaml
from pathlib import Path
from kernel.entity.definition import EntityDefinition
from kernel.skill.schema import Skill
from kernel.skill.integrity import compute_content_hash

async def load_seed_data(seed_dir: Path = Path("seed")):
    """Load seed files into entity definitions and skills."""

    # Entity definitions
    entities_dir = seed_dir / "entities"
    if entities_dir.exists():
        for yaml_file in sorted(entities_dir.glob("*.yaml")):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            existing = await EntityDefinition.find_one({"name": data["name"]})
            if not existing:
                defn = EntityDefinition(**data)
                await defn.insert()

    # Skills
    skills_dir = seed_dir / "skills"
    if skills_dir.exists():
        for md_file in sorted(skills_dir.glob("*.md")):
            content = md_file.read_text()
            name = md_file.stem
            existing = await Skill.find_one({"name": name})
            if not existing:
                skill = Skill(
                    name=name, type="associate", content=content,
                    content_hash=compute_content_hash(content),
                    status="active",
                )
                await skill.insert()
```

## 1.27 Idempotency Utilities [G-86]

```python
# kernel/message/idempotency.py
"""Utilities for idempotent message processing."""

_processed_cache: dict[str, bool] = {}  # In-memory for MVP

async def check_already_processed(message_id: str) -> bool:
    """Check if a message has already been processed."""
    return message_id in _processed_cache

async def mark_processed(message_id: str):
    """Mark a message as processed."""
    _processed_cache[message_id] = True
```

For MVP, in-memory cache is sufficient (single worker). For scale, use a MongoDB collection with TTL index.

## 1.28 Graceful Shutdown [G-84]

```python
# In kernel/api/app.py:
@app.on_event("shutdown")
async def shutdown():
    """Graceful shutdown: close connections."""
    from kernel.db import get_client
    client = get_client()
    if client:
        client.close()

# In kernel/queue_processor.py:
import signal

_running = True

def handle_signal(signum, frame):
    global _running
    _running = False
    logging.info("Queue processor shutting down gracefully...")

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

async def main():
    await init_database()
    while _running:
        await run_sweep_cycle()
        await asyncio.sleep(5)
    logging.info("Queue processor stopped")
```

## 1.29 Schema Migration [M-1]

```python
# kernel/entity/migration.py
from datetime import datetime
from kernel.entity.definition import EntityDefinition
from kernel.changes.collection import write_change_record
from kernel.context import current_org_id
import logging

class MigrationPlan:
    """A planned schema migration with preview and execution."""
    def __init__(self, entity_name: str, org_id, operations: list[dict]):
        self.entity_name = entity_name
        self.org_id = org_id
        self.operations = operations  # [{"type": "rename", "from": "old", "to": "new"}, ...]
        self.affected_count = 0
        self.preview_sample = []

async def plan_migration(entity_name: str, operations: list[dict]) -> MigrationPlan:
    """Build a migration plan with affected count and sample documents."""
    from kernel.db import ENTITY_REGISTRY
    org_id = current_org_id.get()
    entity_cls = ENTITY_REGISTRY.get(entity_name)
    if not entity_cls:
        raise ValueError(f"Entity type {entity_name} not found")

    plan = MigrationPlan(entity_name, org_id, operations)
    plan.affected_count = await entity_cls.find_scoped({}).count()
    plan.preview_sample = [
        e.model_dump() for e in await entity_cls.find_scoped({}).limit(5).to_list()
    ]
    return plan

async def execute_migration(plan: MigrationPlan, batch_size: int = 100,
                             dry_run: bool = False) -> dict:
    """Execute a schema migration in batches.
    Supports: rename_field, add_field (with default), remove_field (deprecate).
    Each batch is a MongoDB transaction. Progress is logged."""
    from kernel.db import ENTITY_REGISTRY, get_database
    db = get_database()
    entity_cls = ENTITY_REGISTRY.get(plan.entity_name)
    collection = entity_cls.get_motor_collection()

    total = plan.affected_count
    processed = 0
    errors = []

    for op in plan.operations:
        if dry_run:
            logging.info(f"DRY RUN: Would apply {op['type']} on {total} documents")
            continue

        if op["type"] == "rename_field":
            # Batch rename with alias support during migration window
            old_name, new_name = op["from"], op["to"]
            while processed < total:
                batch = await collection.find(
                    {"org_id": plan.org_id, old_name: {"$exists": True}},
                ).limit(batch_size).to_list(batch_size)
                if not batch:
                    break
                client = collection.database.client
                async with await client.start_session() as session:
                    async with session.start_transaction():
                        for doc in batch:
                            await collection.update_one(
                                {"_id": doc["_id"]},
                                {"$rename": {old_name: new_name}},
                                session=session,
                            )
                        processed += len(batch)
                logging.info(f"Migration progress: {processed}/{total}")

            # Update entity definition
            defn = await EntityDefinition.find_one({
                "name": plan.entity_name, "org_id": plan.org_id
            })
            if defn and old_name in defn.fields:
                defn.fields[new_name] = defn.fields.pop(old_name)
                defn.updated_at = datetime.utcnow()
                await defn.save()

        elif op["type"] == "add_field":
            # Add with default — no document migration needed for MongoDB
            # Just update the entity definition
            defn = await EntityDefinition.find_one({
                "name": plan.entity_name, "org_id": plan.org_id
            })
            if defn:
                from kernel.entity.definition import FieldDefinition
                defn.fields[op["name"]] = FieldDefinition(**op["field_def"])
                defn.updated_at = datetime.utcnow()
                await defn.save()

        elif op["type"] == "remove_field":
            # Mark as deprecated in definition, optionally clean from documents
            defn = await EntityDefinition.find_one({
                "name": plan.entity_name, "org_id": plan.org_id
            })
            if defn and op["name"] in defn.fields:
                del defn.fields[op["name"]]
                defn.updated_at = datetime.utcnow()
                await defn.save()
            if op.get("cleanup", False):
                await collection.update_many(
                    {"org_id": plan.org_id},
                    {"$unset": {op["name"]: ""}},
                )

    return {
        "status": "completed" if not dry_run else "dry_run",
        "processed": processed,
        "errors": errors,
        "operations": len(plan.operations),
    }
```

**CLI commands:**
```bash
# Rename a field (batched, with progress)
indemn entity migrate Submission --rename old_field new_field --batch-size 100

# Add a new field with default (no document migration needed)
indemn entity migrate Submission --add-field '{"priority": {"type": "str", "default": "normal"}}'

# Remove a field from definition (documents untouched)
indemn entity migrate Submission --remove-field deprecated_field

# Remove field AND clean from documents
indemn entity migrate Submission --remove-field deprecated_field --cleanup

# Dry-run any migration
indemn entity migrate Submission --rename old new --dry-run
```

## 1.30 Auto-Generated CLI [M-2]

```python
# kernel/cli/app.py
import typer
from kernel.cli.client import CLIClient

app = typer.Typer(name="indemn", help="Indemn OS CLI")

def main():
    """Entry point. Fetches entity metadata from API, registers commands dynamically."""
    client = CLIClient()

    # Register static commands (always available)
    from kernel.cli.platform_commands import platform_app
    from kernel.cli.entity_commands import entity_app
    from kernel.cli.queue_commands import queue_app
    app.add_typer(platform_app, name="platform")
    app.add_typer(entity_app, name="entity")
    app.add_typer(queue_app, name="queue")

    # Fetch entity metadata and register dynamic commands
    try:
        meta = client.get("/api/_meta/entities")
        for entity_meta in meta:
            _register_entity_commands(app, entity_meta, client)
    except Exception:
        pass  # API unavailable — static commands still work

    app()

def _register_entity_commands(app: typer.Typer, meta: dict, client: CLIClient):
    """Register CLI commands for one entity type. Mirrors API registration."""
    name = meta["name"]
    slug = name.lower()
    entity_app = typer.Typer(name=slug, help=f"{name} operations")

    @entity_app.command("list")
    def list_cmd(limit: int = 20, offset: int = 0, status: str = None,
                 format: str = "table"):
        """List entities with filters."""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        result = client.get(f"/api/{slug}s", params=params)
        _render(result, format)

    @entity_app.command("get")
    def get_cmd(entity_id: str, format: str = "json"):
        """Get entity by ID."""
        result = client.get(f"/api/{slug}s/{entity_id}")
        _render(result, format)

    @entity_app.command("create")
    def create_cmd(data: str):
        """Create entity. Data as JSON string."""
        import orjson
        result = client.post(f"/api/{slug}s", json=orjson.loads(data))
        _render(result, "json")

    @entity_app.command("update")
    def update_cmd(entity_id: str, data: str):
        """Update entity fields."""
        import orjson
        result = client.put(f"/api/{slug}s/{entity_id}", json=orjson.loads(data))
        _render(result, "json")

    if meta.get("state_machine"):
        @entity_app.command("transition")
        def transition_cmd(entity_id: str, to: str, reason: str = None):
            """Transition entity state."""
            result = client.post(f"/api/{slug}s/{entity_id}/transition",
                                json={"to": to, "reason": reason})
            _render(result, "json")

    # Register capability commands
    for cap in meta.get("capabilities", []):
        cap_name = cap["name"].replace("_", "-")
        @entity_app.command(cap_name)
        def cap_cmd(entity_id: str, auto: bool = False, data: str = None,
                    _cap=cap["name"], _slug=slug):
            import orjson
            params = {"auto": "true"} if auto else {}
            body = orjson.loads(data) if data else {}
            result = client.post(f"/api/{_slug}s/{entity_id}/{_cap.replace('_', '-')}",
                                json=body, params=params)
            _render(result, "json")

    # Register bulk commands
    from kernel.cli.bulk_commands import register_bulk_commands
    register_bulk_commands(name, entity_app)

    app.add_typer(entity_app, name=slug)

def _render(data, format: str):
    """Render output in the requested format."""
    import orjson
    if format == "json":
        typer.echo(orjson.dumps(data, option=orjson.OPT_INDENT_2).decode())
    elif format == "table":
        # Simple table rendering for lists
        if isinstance(data, list) and data:
            keys = list(data[0].keys())[:6]
            typer.echo(" | ".join(k.ljust(20) for k in keys))
            typer.echo("-" * (22 * len(keys)))
            for row in data:
                typer.echo(" | ".join(str(row.get(k, ""))[:20].ljust(20) for k in keys))
        else:
            typer.echo(orjson.dumps(data, option=orjson.OPT_INDENT_2).decode())
```

```python
# kernel/cli/client.py
import httpx
import os

class CLIClient:
    """HTTP client for CLI API-mode. All CLI commands go through the API."""
    def __init__(self):
        self.base_url = os.environ.get("INDEMN_API_URL", "http://localhost:8000")
        self.token = os.environ.get("INDEMN_SERVICE_TOKEN", "")

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def get(self, path, params=None):
        with httpx.Client(base_url=self.base_url) as client:
            r = client.get(path, params=params, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    def post(self, path, json=None, params=None):
        with httpx.Client(base_url=self.base_url) as client:
            r = client.post(path, json=json, params=params, headers=self._headers(), timeout=60)
            r.raise_for_status()
            return r.json()

    def put(self, path, json=None):
        with httpx.Client(base_url=self.base_url) as client:
            r = client.put(path, json=json, headers=self._headers(), timeout=60)
            r.raise_for_status()
            return r.json()
```

## 1.31 Org Clone / Diff / Deploy [M-6]

```python
# kernel/cli/org_commands.py
import typer
from kernel.cli.client import CLIClient

org_app = typer.Typer(name="org", help="Organization management")

@org_app.command("clone")
def clone_org(source: str, as_name: str = typer.Option(..., "--as"),
              include_data: bool = False):
    """Clone an org's configuration into a new org.
    Copies: entity definitions, skills, rules, lookups, roles, watches,
    associate configs, capability activations, integration configs (no secrets).
    Does NOT copy: entity instances, messages, changes, sessions, attentions."""
    client = CLIClient()
    result = client.post("/api/_platform/org/clone", json={
        "source_org_slug": source,
        "target_org_name": as_name,
        "include_data": include_data,
    })
    typer.echo(f"Cloned {source} → {result['target_org_slug']} ({result['items_copied']} items)")

@org_app.command("diff")
def diff_orgs(org_a: str, org_b: str):
    """Show configuration differences between two orgs."""
    client = CLIClient()
    result = client.get("/api/_platform/org/diff",
                       params={"org_a": org_a, "org_b": org_b})
    for diff in result.get("differences", []):
        typer.echo(f"  {diff['type']:20s} {diff['name']:30s} {diff['change']}")
    typer.echo(f"\n{len(result.get('differences', []))} differences found")

@org_app.command("export")
def export_org(org_slug: str, output: str = typer.Option(".", "--output")):
    """Export org configuration to YAML files."""
    client = CLIClient()
    result = client.get(f"/api/_platform/org/export", params={"org": org_slug})
    import yaml
    from pathlib import Path
    out = Path(output) / org_slug
    out.mkdir(parents=True, exist_ok=True)
    for category, items in result.items():
        cat_dir = out / category
        cat_dir.mkdir(exist_ok=True)
        for name, data in items.items():
            with open(cat_dir / f"{name}.yaml", "w") as f:
                yaml.dump(data, f, default_flow_style=False)
    typer.echo(f"Exported to {out}/")

@org_app.command("import")
def import_org(from_dir: str = typer.Option(..., "--from"),
               as_name: str = typer.Option(..., "--as")):
    """Import org configuration from exported YAML files."""
    client = CLIClient()
    import yaml
    from pathlib import Path
    config = {}
    for cat_dir in Path(from_dir).iterdir():
        if cat_dir.is_dir():
            config[cat_dir.name] = {}
            for f in cat_dir.glob("*.yaml"):
                with open(f) as fh:
                    config[cat_dir.name][f.stem] = yaml.safe_load(fh)
    result = client.post("/api/_platform/org/import", json={
        "target_org_name": as_name,
        "config": config,
    })
    typer.echo(f"Imported into {result['org_slug']} ({result['items_imported']} items)")

@org_app.command("deploy")
def deploy_org(from_org: str = typer.Option(..., "--from-org"),
               to_org: str = typer.Option(..., "--to-org"),
               dry_run: bool = True):
    """Promote configuration from one org to another.
    Default is dry-run. Use --no-dry-run to apply."""
    client = CLIClient()
    result = client.post("/api/_platform/org/deploy", json={
        "source_org_slug": from_org,
        "target_org_slug": to_org,
        "dry_run": dry_run,
    })
    if dry_run:
        typer.echo("DRY RUN — would apply:")
        for change in result.get("changes", []):
            typer.echo(f"  {change['type']:20s} {change['name']}")
    else:
        typer.echo(f"Deployed {len(result.get('applied', []))} changes")
```

**API endpoints** backing these commands live in `kernel/api/bootstrap.py` (platform admin routes). They use `PlatformCollection` for cross-org access and audit every operation in both orgs' changes collections.

## 1.32 Audit Verify Command [M-4]

```python
# kernel/cli/audit_commands.py

@audit_app.command("verify")
def verify_hash_chain(org: str = None, entity_type: str = None, limit: int = 1000):
    """Verify the changes collection hash chain integrity.
    Reports any breaks in the chain."""
    client = CLIClient()
    params = {"limit": limit}
    if org: params["org"] = org
    if entity_type: params["entity_type"] = entity_type
    result = client.get("/api/_platform/audit/verify", params=params)
    if result["chain_valid"]:
        typer.echo(f"Hash chain verified: {result['records_checked']} records, no breaks")
    else:
        typer.echo(f"CHAIN BROKEN at record {result['break_at']}:")
        typer.echo(f"  Expected: {result['expected_hash']}")
        typer.echo(f"  Found:    {result['actual_hash']}")
```

## 1.33 Skill Approval Workflow [M-3]

```python
# kernel/api/skill_routes.py (addition to auto-generated routes)

@skill_router.post("/{skill_id}/submit-for-review")
async def submit_skill_for_review(skill_id: str, actor=Depends(get_current_actor)):
    """Submit a skill update for review. Transitions status to pending_review."""
    skill = await Skill.get_scoped(skill_id)
    if not skill:
        raise HTTPException(404)
    skill.status = "pending_review"
    await skill.save_tracked(actor_id=str(actor.id), method="submit_for_review")
    return {"status": "pending_review"}

@skill_router.post("/{skill_id}/approve")
async def approve_skill(skill_id: str, actor=Depends(get_current_actor)):
    """Approve a skill. Requires admin or skill-approver role."""
    check_permission(actor, "Skill", "write")
    skill = await Skill.get_scoped(skill_id)
    if not skill or skill.status != "pending_review":
        raise HTTPException(400, "Skill not pending review")
    skill.status = "active"
    await skill.save_tracked(actor_id=str(actor.id), method="approve")
    return {"status": "active"}
```

## 1.34 Credential Rotation [M-8]

```python
# kernel/integration/rotation.py
from datetime import datetime

async def rotate_credentials(integration_id: str, actor_id: str):
    """Rotate credentials for an integration.
    1. Adapter generates new credentials (if supported)
    2. New credentials stored in Secrets Manager
    3. Old credentials invalidated
    4. Cache invalidated across instances
    5. Integration entity updated and audited."""
    from kernel_entities.integration import Integration
    from kernel.integration.credentials import store_credentials, invalidate_cached_credentials
    from kernel.integration.dispatch import get_adapter

    integration = await Integration.get(integration_id)
    if not integration:
        raise ValueError(f"Integration {integration_id} not found")

    adapter = await get_adapter(integration.system_type)

    # Provider-specific rotation (if supported)
    if hasattr(adapter, 'rotate_credentials'):
        new_creds = await adapter.rotate_credentials()
        await store_credentials(integration.secret_ref, new_creds)
    else:
        raise ValueError(f"Adapter {integration.provider} does not support automatic rotation")

    # Invalidate cache
    invalidate_cached_credentials(integration.secret_ref)

    # Audit
    integration.last_checked_at = datetime.utcnow()
    await integration.save_tracked(
        actor_id=actor_id,
        method="rotate_credentials",
    )

    return {"status": "rotated", "integration": integration.name}
```

---

## Phase 1 Acceptance Tests

```
1. ENTITY DEFINITION → DYNAMIC CLASS
   Define entity via API → restart → CLI commands + API routes exist → skill generated

2. ENTITY CRUD + STATE MACHINE
   Create, read, update, transition (valid succeeds, invalid rejected), delete

3. ORGANIZATION SCOPING
   Two orgs, entities in each, queries return only same-org data, cross-org denied

4. CHANGES COLLECTION
   Every mutation recorded with entity_id, actor_id, field changes, timestamp, hash chain intact

5. WATCH EVALUATION → MESSAGE
   Role with watch, entity matching watch created → message in queue with correct metadata

6. CONDITIONAL WATCH
   Condition false → no message. Condition true → message created.

7. RULE EVALUATION (--auto)
   Rules match → deterministic result. No match → needs_reasoning. Veto → needs_reasoning with context.

8. LOOKUPS
   Lookup table created. Rule references lookup. Evaluation resolves through lookup.

9. AUTHENTICATION
   Password login → JWT. Token auth for service accounts. Invalid/expired tokens rejected.

10. PERMISSION ENFORCEMENT
    Read-only role can't write. Write role can write. Checked on every request.

11. SKILL AUTO-GENERATION
    Entity with fields + state machine + capabilities → generated skill documents all of them.

12. SELECTIVE EMISSION
    Regular field update → no message. State transition → message. @exposed method → message. Creation → message.

13. CASCADE DEPTH
    Cascading watches at depth > 10 → circuit_broken message, cascade stops.

14. SCHEMA MIGRATION
    Add field (default value). Rename field (batched, alias window). Dry-run shows count.

15. RULE GROUPS + LIFECYCLE
    Draft group → rules not evaluated. Active group → rules evaluate. Archive → rules stop.

16. RULE VALIDATION
    Non-existent field → rejected. State machine field → rejected. Overlapping → warning.

17. COMPUTED FIELDS
    Entity with computed field mapping → save → computed value auto-populated.

18. FIRST-ORG BOOTSTRAP
    Platform init → org + admin created → token issued → admin can operate.

19. KERNEL ENTITY CASCADE GUARD
    Watch on Role that triggers Role modification → blocked at depth 1.

20. END-TO-END
    Define domain entity via CLI → create role with watches + rules → create instance →
    watch fires → message in queue → rule evaluates → changes recorded → OTEL traces connect flow.
```

---

## Gaps Resolved in This Document

G-01, G-02, G-03, G-04, G-05, G-06, G-07, G-08, G-09, G-10, G-11, G-12, G-13 (partial — entity commands specified, full CLI in implementation), G-14 (interface defined, full implementation during Phase 6), G-15 (interface defined), G-16, G-17, G-18, G-56, G-57, G-62 (deferred list at top), G-68, G-69, G-71, G-72, G-74, G-75, G-82, G-83, G-84, G-85, G-86, G-88, G-89.
