---
ask: "Implementation specification for Phase 0 (Development Foundation) and Phase 1 (Kernel Framework) — the critical path everything depends on"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "The design-level source of truth"
  - type: artifact
    ref: "2026-04-09-consolidated-architecture.md"
    description: "Pre-white-paper consolidated architecture"
  - type: artifact
    ref: "2026-04-13-infrastructure-and-deployment.md"
    description: "Service architecture, Railway deployment"
  - type: artifact
    ref: "2026-04-13-remaining-gap-sessions.md"
    description: "Repo structure, testing strategy, CI/CD"
  - type: artifact
    ref: "2026-04-11-authentication-design.md"
    description: "Session entity, JWT, auth methods"
  - type: artifact
    ref: "2026-04-09-data-architecture-everything-is-data.md"
    description: "Entity definitions as data, dynamic class creation"
  - type: artifact
    ref: "2026-04-09-data-architecture-solutions.md"
    description: "OrgScopedCollection, security solutions"
  - type: research
    description: "Beanie dynamic Document registration, Pydantic v2 create_model, Temporal Python SDK patterns"
---

# Implementation Specification: Phase 0 + Phase 1

## Relationship to the White Paper

The white paper (Section 11) defines Phase 0 as "Development Foundation" and Phase 1 as "Kernel Framework." This spec turns the design into buildable detail. Where the white paper leaves implementation choices open, this spec makes them. Where the artifacts contain specific patterns (Beanie class structures, message schemas, condition evaluator logic), this spec draws on them.

The architecture is final. This spec does not redesign. It specifies HOW to build what's been designed.

---

# Phase 0: Development Foundation

## What It Produces

The repository, conventions, environment, and pipeline for building everything else.

## 0.1 Repository Structure

One git repository. Modular monolith.

```
indemn-os/
  kernel/
    __init__.py
    entity/
      __init__.py
      base.py                  # BaseEntity class (what kernel entities inherit from)
      definition.py            # EntityDefinition model (stored in MongoDB)
      factory.py               # Dynamic class creation from definitions
      state_machine.py         # State machine enforcement
      computed.py              # Computed field evaluation
      flexible.py              # Flexible data (schema-validated dict)
    message/
      __init__.py
      schema.py                # Message document model
      queue.py                 # Queue operations (write, claim, complete, move to log)
      emit.py                  # Entity save → watch evaluation → message creation
    watch/
      __init__.py
      evaluator.py             # Watch condition evaluation (shared with rules)
      cache.py                 # In-memory watch cache with invalidation
      scope.py                 # Scope resolution (field_path, active_context)
    rule/
      __init__.py
      schema.py                # Rule document model
      engine.py                # Rule evaluation (uses watch/evaluator.py for conditions)
      lookup.py                # Lookup document model and resolution
    capability/
      __init__.py
      registry.py              # Capability registration and dispatch
      auto_classify.py         # First kernel capability
    auth/
      __init__.py
      middleware.py             # FastAPI auth middleware
      session.py               # Session management (create, validate, revoke)
      jwt.py                   # JWT signing, verification, revocation cache
      methods.py               # Password (argon2), token, magic_link
      mfa.py                   # TOTP implementation (deferred content, interface defined)
    scoping/
      __init__.py
      org_scoped.py            # OrgScopedCollection wrapper
      platform.py              # PlatformCollection for cross-org admin
    changes/
      __init__.py
      collection.py            # Changes collection write operations
      hash_chain.py            # Sequential hash chain for tamper evidence
    observability/
      __init__.py
      tracing.py               # OTEL span creation helpers
      correlation.py           # Correlation ID management
    api/
      __init__.py
      app.py                   # FastAPI application factory
      registration.py          # Auto-register routes from entity definitions
      websocket.py             # WebSocket handler for real-time UI
      webhook.py               # Generic webhook endpoint /webhook/{provider}/{integration_id}
      health.py                # Health check endpoint
    cli/
      __init__.py
      app.py                   # Typer application factory
      registration.py          # Auto-register commands from entity definitions
      client.py                # HTTP client for API-mode operation
    skill/
      __init__.py
      generator.py             # Generate markdown skill from entity definition
      storage.py               # Skill CRUD in MongoDB
    queue_processor.py         # Sweep process (dispatch, escalation, schedules)
    temporal/
      __init__.py
      worker.py                # Temporal worker entry point
      workflows.py             # Generic claim→process→complete workflow
      activities.py            # Shared activities (claim_message, complete_message, etc.)
    config.py                  # Configuration (env vars, defaults)
    db.py                      # MongoDB connection, init_beanie, database accessor

  kernel_entities/
    __init__.py
    organization.py            # Organization kernel entity
    actor.py                   # Actor kernel entity (human + associate)
    role.py                    # Role kernel entity (permissions + watches)
    integration.py             # Integration kernel entity
    attention.py               # Attention kernel entity
    runtime.py                 # Runtime kernel entity
    session.py                 # Session kernel entity

  seed/
    entities/                  # Seed YAML for standard domain entity definitions
    skills/                    # Seed markdown for standard skills
    roles/                     # Seed YAML for reference roles

  tests/
    __init__.py
    conftest.py                # Shared fixtures (test DB, test org, test actor)
    unit/
      test_state_machine.py
      test_condition_evaluator.py
      test_computed_fields.py
      test_hash_chain.py
      test_jwt.py
      test_org_scoping.py
    integration/
      test_entity_lifecycle.py
      test_watch_evaluation.py
      test_message_flow.py
      test_rule_evaluation.py
      test_auth_flow.py
      test_cross_tenant_isolation.py
    e2e/
      test_first_domain_entity.py

  Dockerfile                   # Kernel image (multi-entry-point)
  docker-compose.yml           # Local dev: API + queue processor + temporal dev server
  pyproject.toml
  CLAUDE.md
  README.md
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
    "httpx>=0.27",          # For testing FastAPI
    "ruff>=0.4",
]

[project.dependencies]
# ODM + Database
beanie = ">=1.26"
motor = ">=3.4"
pymongo = ">=4.7"

# API + CLI
fastapi = ">=0.111"
uvicorn = ">=0.30"
typer = ">=0.12"
httpx = ">=0.27"            # CLI API client

# Validation
pydantic = ">=2.7"
pydantic-settings = ">=2.3"

# Auth
pyjwt = ">=2.8"
argon2-cffi = ">=23.1"
pyotp = ">=2.9"             # TOTP

# Workflow engine
temporalio = ">=1.6"

# Observability
opentelemetry-api = ">=1.25"
opentelemetry-sdk = ">=1.25"
opentelemetry-exporter-otlp = ">=1.25"

# AWS
boto3 = ">=1.34"            # Secrets Manager, S3

# Utilities
orjson = ">=3.10"           # Fast JSON
python-multipart = ">=0.0.9" # File uploads

[project.scripts]
indemn = "kernel.cli.app:main"
```

Package manager: `uv`. All commands use `uv run`.

## 0.3 CLAUDE.md for the OS Codebase

Written at Phase 0 as the first file. Defines conventions for every session:

Key content (not exhaustive — refined during implementation):
- Project structure overview
- How to add a kernel entity (add class in `kernel_entities/`, register in `kernel/db.py`)
- How to add a domain entity definition (via CLI or seed YAML)
- How to add a kernel capability (add module in `kernel/capability/`, register in `registry.py`)
- How to add a test (which directory, naming, fixtures)
- How to run locally (`docker-compose up` then `uv run indemn ...`)
- The trust boundary (kernel processes have MongoDB access; everything else uses the API)
- CLI always in API mode (never direct MongoDB access from CLI)
- Naming conventions (snake_case Python, kebab-case CLI commands, camelCase MongoDB fields only where Beanie requires)
- The entity definition → dynamic class → CLI/API/skill auto-generation pipeline
- OrgScopedCollection: always use it, never bypass it

## 0.4 Development Environment

**Local stack** (docker-compose.yml):
- `indemn-api`: uvicorn with hot reload, port 8000
- `indemn-queue-processor`: Python process, polls message_queue
- `temporal-dev-server`: `temporal server start-dev`, port 7233
- Database: remote Atlas dev cluster (no local MongoDB)
- `INDEMN_API_URL=http://localhost:8000` for CLI

**Not local**: MongoDB (Atlas dev cluster), S3 (AWS), Secrets Manager (AWS). These are remote managed services.

## 0.5 CI Pipeline

GitHub Actions on push to `main`:

```yaml
jobs:
  lint:
    - ruff check .
    - ruff format --check .
  test-unit:
    - uv run pytest tests/unit/ -v
  test-integration:
    - uv run pytest tests/integration/ -v
    # Uses Atlas dev cluster + Temporal dev server
  build:
    - docker build -t indemn-kernel .
  # Deploy handled by Railway auto-deploy from main
```

E2E tests run on-demand or weekly schedule, not on every push.

## 0.6 Deployment Configuration

Per the infrastructure design artifact, Railway services configured as:

| Service | Image | Entry Point | Public |
|---|---|---|---|
| `indemn-api` | `indemn-kernel` | `python -m kernel.api.app` | Yes (`api.os.indemn.ai`) |
| `indemn-queue-processor` | `indemn-kernel` | `python -m kernel.queue_processor` | No |
| `indemn-temporal-worker` | `indemn-kernel` | `python -m kernel.temporal.worker` | No |

Railway shared variables: `MONGODB_URI`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, `TEMPORAL_API_KEY`, `JWT_SIGNING_KEY`, `OTEL_EXPORTER_ENDPOINT`.

## Phase 0 Acceptance Criteria

- [ ] Repository exists with the directory structure above
- [ ] `uv sync` installs all dependencies
- [ ] `docker-compose up` starts API server + queue processor + Temporal dev server
- [ ] `uv run pytest tests/unit/` runs (even if no tests yet)
- [ ] `docker build` produces a working kernel image
- [ ] CLAUDE.md exists with conventions
- [ ] CI pipeline runs lint + test on push

---

# Phase 1: Kernel Framework

## What It Produces

The entity framework, the seven kernel entities, the auto-generation machinery, the message system with watches, the condition evaluator, authentication, and at least one kernel capability with the `--auto` pattern — all proven end-to-end.

## 1.1 Entity Definition Schema

An entity definition is a MongoDB document in the `entity_definitions` collection that describes a domain entity type. Kernel entities are NOT defined this way — they are Python classes in `kernel_entities/`.

```python
# kernel/entity/definition.py
from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class EntityDefinition(Document):
    """Schema for a domain entity type. Stored in MongoDB.
    The entity framework reads these at startup and creates
    Beanie Document subclasses dynamically."""

    name: str                              # "Submission", "Email", "Policy"
    collection_name: str                   # "submissions", "emails", "policies"
    org_id: str = "_system"                # "_system" for template definitions

    fields: dict[str, FieldDefinition]     # Field name → type + constraints
    state_machine: Optional[dict[str, list[str]]] = None  # state → [valid transitions]
    computed_fields: Optional[dict[str, ComputedFieldDef]] = None
    flexible_data_schema: Optional[str] = None  # Reference to a schema definition
    relationships: Optional[dict[str, RelationshipDef]] = None
    indexes: list[IndexDef] = Field(default_factory=list)
    activated_capabilities: list[CapabilityActivation] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    version: int = 1

    class Settings:
        name = "entity_definitions"
        indexes = [
            [("name", 1)],
            [("org_id", 1), ("name", 1)],
        ]
```

Supporting types:

```python
from pydantic import BaseModel
from typing import Optional, Any

class FieldDefinition(BaseModel):
    type: str                   # "str", "int", "float", "decimal", "bool",
                                # "datetime", "date", "objectid", "list", "dict"
    required: bool = False
    default: Optional[Any] = None
    unique: bool = False
    indexed: bool = False
    enum_values: Optional[list[str]] = None
    description: Optional[str] = None

class ComputedFieldDef(BaseModel):
    source_field: str           # Field to compute from (e.g., "stage")
    mapping: dict[str, str]     # Source value → computed value

class RelationshipDef(BaseModel):
    target_entity: str          # "Carrier", "Submission"
    type: str                   # "reference" (stores ObjectId), "back_reference"
    field_name: Optional[str] = None  # For back_reference: field on the other entity

class IndexDef(BaseModel):
    fields: list[tuple[str, int]]   # [("org_id", 1), ("status", 1)]
    unique: bool = False

class CapabilityActivation(BaseModel):
    capability: str             # "auto_classify", "fuzzy_search", "stale_check"
    config: dict                # Capability-specific configuration
```

## 1.2 Base Entity Class

The class that ALL entities — kernel and domain — share behavior through.

```python
# kernel/entity/base.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, ClassVar

class BaseEntity(Document):
    """Base class providing common fields and behavior for all entities.
    Kernel entities inherit directly. Domain entities are created
    dynamically via the entity factory."""

    org_id: ObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    version: int = 1

    # Subclass configuration (set by kernel entity classes or factory)
    _state_machine: ClassVar[Optional[dict]] = None
    _computed_fields: ClassVar[Optional[dict]] = None
    _activated_capabilities: ClassVar[list] = []

    async def save_tracked(self, actor_id: str, **kwargs):
        """Save with optimistic concurrency, changes tracking,
        watch evaluation, and message emission.
        This is the ONLY save path for application code."""
        # Implementation in Section 1.8 (Changes) and 1.10 (Messages)
        ...

    def transition_to(self, target_state: str, reason: Optional[str] = None):
        """Validate and execute a state machine transition.
        Does NOT save — caller must call save_tracked()."""
        # Implementation in Section 1.5
        ...

    class Settings:
        # Subclasses override
        use_state_management = True
        is_root = True
```

## 1.3 Dynamic Entity Class Creation

How entity definitions in MongoDB become Python classes at runtime.

```python
# kernel/entity/factory.py
from pydantic import create_model
from beanie import Document
from kernel.entity.base import BaseEntity
from kernel.entity.definition import EntityDefinition, FieldDefinition
from typing import Optional, Literal
from bson import ObjectId
from datetime import datetime, date
from decimal import Decimal

# Type mapping from definition strings to Python types
TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "decimal": Decimal,
    "bool": bool,
    "datetime": datetime,
    "date": date,
    "objectid": ObjectId,
    "list": list,
    "dict": dict,
}

def create_entity_class(definition: EntityDefinition) -> type[BaseEntity]:
    """Create a Beanie Document subclass from an EntityDefinition."""

    # Build field definitions for create_model
    field_definitions = {}
    for field_name, field_def in definition.fields.items():
        python_type = TYPE_MAP[field_def.type]
        if field_def.enum_values:
            python_type = Literal[tuple(field_def.enum_values)]
        if not field_def.required:
            python_type = Optional[python_type]
        default = field_def.default if field_def.default is not None else (None if not field_def.required else ...)
        field_definitions[field_name] = (python_type, default)

    # Create the dynamic Pydantic model with BaseEntity as parent
    DynamicEntity = create_model(
        definition.name,
        __base__=BaseEntity,
        **field_definitions,
    )

    # Attach entity-specific configuration
    DynamicEntity._state_machine = definition.state_machine
    DynamicEntity._computed_fields = definition.computed_fields
    DynamicEntity._activated_capabilities = definition.activated_capabilities or []

    # Create Settings inner class for Beanie
    settings_attrs = {
        "name": definition.collection_name,
    }
    if definition.indexes:
        settings_attrs["indexes"] = [
            idx.fields for idx in definition.indexes
        ]
    DynamicEntity.Settings = type("Settings", (), settings_attrs)

    return DynamicEntity
```

**Startup sequence** (in `kernel/db.py`):

```python
# kernel/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from kernel.entity.definition import EntityDefinition
from kernel.entity.factory import create_entity_class
from kernel_entities import (
    Organization, Actor, Role, Integration,
    Attention, Runtime, Session,
)
from kernel.config import settings

# Registry of all entity classes (kernel + dynamic)
ENTITY_REGISTRY: dict[str, type] = {}

async def init_database():
    """Initialize MongoDB connection and all entity classes."""
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]

    # Phase 1: Register kernel entities (always present)
    kernel_entities = [
        Organization, Actor, Role, Integration,
        Attention, Runtime, Session,
        EntityDefinition,  # The definition entity itself
    ]
    for cls in kernel_entities:
        ENTITY_REGISTRY[cls.__name__] = cls

    # Phase 2: Load domain entity definitions and create dynamic classes
    # Direct Motor query (before Beanie is initialized)
    definitions_collection = db["entity_definitions"]
    async for doc in definitions_collection.find({}):
        defn = EntityDefinition(**doc)
        dynamic_cls = create_entity_class(defn)
        ENTITY_REGISTRY[defn.name] = dynamic_cls

    # Phase 3: Initialize Beanie with all entity classes
    all_models = list(ENTITY_REGISTRY.values())
    await init_beanie(database=db, document_models=all_models)

    return db
```

## 1.4 Kernel Entities

Seven kernel entities, all Python classes in `kernel_entities/`. Each inherits from `BaseEntity` and adds kernel-specific fields and behavior.

**Organization** — the tenancy boundary:

```python
# kernel_entities/organization.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field

class Organization(BaseEntity):
    name: str
    slug: str                   # URL-safe identifier
    status: Literal["onboarding", "active", "suspended"] = "onboarding"
    settings: dict = Field(default_factory=dict)  # Org-level config
    template_source: Optional[str] = None  # Cloned from which template

    _state_machine = {
        "onboarding": ["active"],
        "active": ["suspended"],
        "suspended": ["active"],
    }

    class Settings:
        name = "organizations"
        indexes = [
            [("slug", 1)],
        ]
```

**Actor** — identity (human, associate, tier3 developer):

```python
# kernel_entities/actor.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from bson import ObjectId

class Actor(BaseEntity):
    name: str
    email: Optional[str] = None
    type: Literal["human", "associate", "tier3_developer"]
    status: Literal["provisioned", "active", "suspended", "deprovisioned"] = "provisioned"
    role_ids: list[ObjectId] = Field(default_factory=list)

    # Associate-specific fields (None for humans)
    skills: Optional[list[str]] = None
    mode: Optional[Literal["deterministic", "reasoning", "hybrid"]] = None
    runtime_id: Optional[ObjectId] = None
    owner_actor_id: Optional[ObjectId] = None
    llm_config: Optional[dict] = None

    # Auth methods (list of method references)
    authentication_methods: list[dict] = Field(default_factory=list)
    mfa_exempt: bool = False

    _state_machine = {
        "provisioned": ["active"],
        "active": ["suspended", "deprovisioned"],
        "suspended": ["active", "deprovisioned"],
    }

    class Settings:
        name = "actors"
        indexes = [
            [("org_id", 1), ("email", 1)],
            [("org_id", 1), ("type", 1), ("status", 1)],
        ]
```

**Role** — permissions + watches:

```python
# kernel_entities/role.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from bson import ObjectId

class WatchDefinition(BaseModel):
    entity_type: str
    event: str                  # "created", "transitioned", "method_invoked", "fields_changed"
    conditions: Optional[dict] = None   # JSON condition (same language as rules)
    scope: Optional[dict] = None        # {"type": "field_path", "path": "..."} or {"type": "active_context", "traverses": "..."}
    context_depth: int = 1

class Role(BaseEntity):
    name: str
    permissions: dict           # {"read": ["submission", "email"], "write": ["submission"]}
    watches: list[WatchDefinition] = Field(default_factory=list)
    can_grant: Optional[list[str]] = None  # Role names this role can grant
    mfa_required: bool = False
    is_inline: bool = False     # True for associate-specific inline roles
    bound_actor_id: Optional[ObjectId] = None  # Set for inline roles

    class Settings:
        name = "roles"
        indexes = [
            [("org_id", 1), ("name", 1)],
        ]
```

**Integration** — external system connection:

```python
# kernel_entities/integration.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from bson import ObjectId

class Integration(BaseEntity):
    name: str
    owner_type: Literal["org", "actor"]
    owner_id: ObjectId          # org_id or actor_id depending on owner_type
    system_type: str            # "email", "payment", "voice", "ams", "carrier", "identity_provider"
    provider: str               # "outlook", "gmail", "stripe", "livekit"
    provider_version: str = "v1"
    config: dict = {}           # Non-secret provider config
    secret_ref: Optional[str] = None  # AWS Secrets Manager path
    access: Optional[dict] = None     # For org-level: {"roles": ["underwriter", "ops"]}
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

    class Settings:
        name = "integrations"
        indexes = [
            [("org_id", 1), ("system_type", 1), ("status", 1)],
            [("owner_type", 1), ("owner_id", 1)],
        ]
```

**Attention**, **Runtime**, and **Session** follow the same pattern with fields as specified in the white paper and the realtime-architecture-design and authentication-design artifacts. I won't reproduce them in full here — they follow the exact field lists from those artifacts, implemented as `BaseEntity` subclasses with appropriate state machines, indexes, and settings.

## 1.5 State Machine Enforcement

```python
# kernel/entity/state_machine.py

class StateMachineError(Exception):
    pass

def validate_transition(entity: BaseEntity, target_state: str) -> None:
    """Validate that a state transition is allowed.
    Raises StateMachineError if not."""
    sm = entity._state_machine
    if sm is None:
        return  # No state machine defined — all transitions allowed

    # Find the current state (look for a field named 'status' or 'stage')
    current_state = getattr(entity, "status", None) or getattr(entity, "stage", None)
    if current_state is None:
        raise StateMachineError("Entity has a state machine but no status/stage field")

    valid_transitions = sm.get(current_state, [])
    if target_state not in valid_transitions:
        raise StateMachineError(
            f"Cannot transition from '{current_state}' to '{target_state}'. "
            f"Valid transitions: {valid_transitions}"
        )
```

The `transition_to` method on `BaseEntity` calls `validate_transition`, sets the status field, and records the transition metadata for the event. It does NOT save — the caller must call `save_tracked()`.

## 1.6 OrgScopedCollection

The defense-in-depth wrapper. All application code accesses MongoDB through this.

```python
# kernel/scoping/org_scoped.py
from motor.motor_asyncio import AsyncIOMotorCollection

class OrgScopedCollection:
    """Wraps a Motor collection to always inject org_id.
    Application code NEVER accesses the raw collection."""

    def __init__(self, collection: AsyncIOMotorCollection, org_id: str):
        self._collection = collection
        self._org_id = org_id

    def _inject_org(self, filter_doc: dict) -> dict:
        filter_doc = filter_doc or {}
        filter_doc["org_id"] = self._org_id
        return filter_doc

    async def find_one(self, filter_doc=None, *args, **kwargs):
        return await self._collection.find_one(
            self._inject_org(filter_doc), *args, **kwargs
        )

    def find(self, filter_doc=None, *args, **kwargs):
        return self._collection.find(
            self._inject_org(filter_doc), *args, **kwargs
        )

    async def insert_one(self, document, *args, **kwargs):
        document["org_id"] = self._org_id
        return await self._collection.insert_one(document, *args, **kwargs)

    async def update_one(self, filter_doc, update, *args, **kwargs):
        return await self._collection.update_one(
            self._inject_org(filter_doc), update, *args, **kwargs
        )

    async def delete_one(self, filter_doc, *args, **kwargs):
        return await self._collection.delete_one(
            self._inject_org(filter_doc), *args, **kwargs
        )

    async def aggregate(self, pipeline, *args, **kwargs):
        # Prepend $match with org_id to every pipeline
        org_match = {"$match": {"org_id": self._org_id}}
        pipeline = [org_match] + list(pipeline)
        return self._collection.aggregate(pipeline, *args, **kwargs)

    async def count_documents(self, filter_doc=None, *args, **kwargs):
        return await self._collection.count_documents(
            self._inject_org(filter_doc), *args, **kwargs
        )
```

Raw Motor access is available ONLY via `PlatformCollection` for platform admin operations, which requires a separate code path with full audit.

## 1.7 Changes Collection

Every entity mutation is recorded with field-level detail and a tamper-evident hash chain.

```python
# kernel/changes/collection.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, Any
import hashlib, orjson

class ChangeRecord(Document):
    org_id: ObjectId
    entity_type: str
    entity_id: ObjectId
    change_type: str            # "create", "update", "delete", "transition"
    actor_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None

    # Field-level changes
    changes: list[FieldChange] = Field(default_factory=list)

    # For method invocations
    method: Optional[str] = None
    method_metadata: Optional[dict] = None  # Rule evaluation results, etc.

    # Tamper evidence
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

class FieldChange(BaseModel):
    field: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
```

The MongoDB user for the application has INSERT permission only on the `changes` collection — not UPDATE or DELETE. The hash chain links each record to its predecessor.

## 1.8 The Save Path — `save_tracked()`

The critical transaction: entity save + changes record + watch evaluation + message creation, all atomic.

```python
# Conceptual implementation of BaseEntity.save_tracked()
async def save_tracked(self, actor_id: str, method: str = None,
                       method_metadata: dict = None,
                       correlation_id: str = None,
                       session=None):
    """The ONLY save path. Performs in one MongoDB transaction:
    1. Optimistic concurrency check (version field)
    2. Entity save
    3. Changes collection record
    4. Watch evaluation → message creation
    """
    from kernel.changes.collection import ChangeRecord, FieldChange
    from kernel.message.emit import evaluate_watches_and_emit
    from kernel.observability.tracing import create_span

    with create_span("entity.save", entity_type=type(self).__name__,
                     entity_id=str(self.id)):

        # Compute field-level changes (compare to previous state)
        old_values = self._previous_state  # Captured on load
        changes = compute_field_changes(old_values, self.dict())

        # Update metadata
        self.updated_at = datetime.utcnow()
        expected_version = self.version
        self.version += 1

        # Compute computed fields
        self._evaluate_computed_fields()

        # Start transaction
        async with await get_motor_client().start_session() as mongo_session:
            async with mongo_session.start_transaction():

                # 1. Optimistic concurrency save
                result = await self.get_motor_collection().update_one(
                    {"_id": self.id, "version": expected_version},
                    {"$set": self.dict(by_alias=True)},
                    session=mongo_session,
                )
                if result.modified_count == 0:
                    if await self.get_motor_collection().find_one({"_id": self.id}):
                        raise VersionConflictError(
                            f"{type(self).__name__} {self.id} was modified concurrently"
                        )
                    else:
                        # New document — insert
                        await self.get_motor_collection().insert_one(
                            self.dict(by_alias=True), session=mongo_session
                        )

                # 2. Write changes record
                change_record = ChangeRecord(
                    org_id=self.org_id,
                    entity_type=type(self).__name__,
                    entity_id=self.id,
                    change_type=determine_change_type(changes, method),
                    actor_id=actor_id,
                    correlation_id=correlation_id,
                    changes=[FieldChange(**c) for c in changes],
                    method=method,
                    method_metadata=method_metadata,
                )
                await compute_and_set_hash(change_record)
                await change_record.insert(session=mongo_session)

                # 3. Evaluate watches and create messages
                await evaluate_watches_and_emit(
                    entity=self,
                    changes=changes,
                    method=method,
                    actor_id=actor_id,
                    correlation_id=correlation_id,
                    session=mongo_session,
                )
```

## 1.9 Condition Evaluator

One evaluator, one JSON format, shared by watches and rules.

```python
# kernel/watch/evaluator.py

def evaluate_condition(condition: dict, entity_data: dict) -> bool:
    """Evaluate a JSON condition against entity field values.
    Supports: field comparisons, all/any/not composition."""

    if "all" in condition:
        return all(evaluate_condition(c, entity_data) for c in condition["all"])
    if "any" in condition:
        return any(evaluate_condition(c, entity_data) for c in condition["any"])
    if "not" in condition:
        return not evaluate_condition(condition["not"], entity_data)

    # Field comparison
    field = condition["field"]
    op = condition["op"]
    expected = condition["value"]
    actual = get_nested_field(entity_data, field)

    return OPERATORS[op](actual, expected)

OPERATORS = {
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
}
```

## 1.10 Message System

Two collections: `message_queue` (hot) and `message_log` (cold).

```python
# kernel/message/schema.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, Literal

class Message(Document):
    org_id: ObjectId
    entity_type: str
    entity_id: ObjectId
    event_type: str             # "created", "transitioned", "method_invoked", "fields_changed"

    target_role: str
    target_actor_id: Optional[ObjectId] = None  # Set by scoped watches

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

    # Event metadata
    event_metadata: dict = Field(default_factory=dict)
    # {"method": "classify", "state_transition": {"from": "received", "to": "triaging"},
    #  "fields_changed": ["status", "classification"]}

    # Minimal summary for queue display
    summary: dict = Field(default_factory=dict)

    completed_at: Optional[datetime] = None
    result: Optional[dict] = None

    class Settings:
        name = "message_queue"
        indexes = [
            [("org_id", 1), ("target_role", 1), ("status", 1),
             ("priority", -1), ("created_at", 1)],
            [("status", 1), ("visibility_timeout", 1)],
            [("correlation_id", 1), ("created_at", 1)],
        ]
```

`MessageLog` has the same schema, collection name `message_log`, with indexes optimized for audit queries.

## 1.11 Watch Evaluation and Message Emission

Inside the entity save transaction:

```python
# kernel/message/emit.py

async def evaluate_watches_and_emit(
    entity, changes, method, actor_id, correlation_id, session
):
    """Evaluate all watches for this org+entity_type against the current
    entity state and changes. Create messages for matching watches."""
    from kernel.watch.cache import get_cached_watches
    from kernel.watch.evaluator import evaluate_condition
    from kernel.message.schema import Message

    watches = get_cached_watches(str(entity.org_id), type(entity).__name__)

    event_type = determine_event_type(changes, method)
    event_metadata = build_event_metadata(changes, method, entity)

    entity_data = entity.dict()

    for watch in watches:
        # Check event type match
        if not event_matches(watch.event, event_type, event_metadata):
            continue

        # Check conditions
        if watch.conditions and not evaluate_condition(watch.conditions, entity_data):
            continue

        # Resolve scope (if present)
        target_actor_id = None
        if watch.scope:
            target_actor_id = await resolve_scope(watch.scope, entity, session)
            if target_actor_id is None:
                continue  # Scope resolved to nothing — skip

        # Create message
        message = Message(
            org_id=entity.org_id,
            entity_type=type(entity).__name__,
            entity_id=entity.id,
            event_type=event_type,
            target_role=watch.role_name,  # From the Role this watch belongs to
            target_actor_id=target_actor_id,
            correlation_id=correlation_id or str(uuid4()),
            depth=0,  # Depth tracking handled by parent context
            event_metadata=event_metadata,
            summary=build_summary(entity, event_type),
        )
        await message.insert(session=session)
```

Watch cache: in-memory dict keyed by `(org_id, entity_type)`, loaded from Role entities at startup, invalidated on Role save (kernel entity cache invalidation per architecture ironing round 3).

## 1.12 Rules and Lookups

```python
# kernel/rule/schema.py
from beanie import Document
from pydantic import Field
from bson import ObjectId
from typing import Optional, Literal
from datetime import datetime

class Rule(Document):
    org_id: ObjectId
    entity_type: str
    capability: str             # "auto_classify", "auto_route", etc.
    group: Optional[str] = None
    name: Optional[str] = None
    conditions: dict            # JSON condition (same evaluator as watches)
    action: Literal["set_fields", "force_reasoning"]
    sets: Optional[dict] = None          # For set_fields action
    forces_reasoning_reason: Optional[str] = None  # For force_reasoning
    priority: int = 100
    status: Literal["draft", "active", "archived"] = "draft"
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rules"
        indexes = [
            [("org_id", 1), ("entity_type", 1), ("capability", 1), ("status", 1)],
        ]

class Lookup(Document):
    org_id: ObjectId
    name: str
    data: dict                  # Key → value mapping
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lookups"
        indexes = [
            [("org_id", 1), ("name", 1)],
        ]
```

## 1.13 Kernel Capabilities — auto_classify with `--auto`

```python
# kernel/capability/auto_classify.py

async def auto_classify(entity, config: dict, org_id: str) -> dict:
    """Evaluate classification rules for this entity.
    Returns either a deterministic result or needs_reasoning."""
    from kernel.rule.engine import evaluate_rules

    result = await evaluate_rules(
        org_id=org_id,
        entity_type=type(entity).__name__,
        capability="auto_classify",
        entity_data=entity.dict(),
    )

    if result["matched"] and not result["vetoed"]:
        # Deterministic match — apply the fields
        winning_rule = result["winning_rule"]
        return {
            "needs_reasoning": False,
            "result": winning_rule["sets"],
            "matched_rule": winning_rule["name"],
            "rule_evaluation": result,
        }
    else:
        return {
            "needs_reasoning": True,
            "reason": result.get("veto_reason", "no_match"),
            "attempted_rules": result.get("attempted_rules", []),
            "rule_evaluation": result,
        }
```

The `--auto` flag on CLI commands invokes this capability. If `needs_reasoning` is false, the CLI applies the result and reports success. If true, it returns the reasoning context for the associate's LLM to handle.

## 1.14 Auto-Generated CLI

Typer application that registers commands from entity definitions at startup.

```python
# kernel/cli/app.py
import typer
import httpx
from kernel.config import settings

app = typer.Typer(name="indemn", help="Indemn OS CLI")

def get_client() -> httpx.Client:
    """HTTP client for API-mode operation."""
    return httpx.Client(
        base_url=settings.api_url,
        headers={"Authorization": f"Bearer {settings.cli_token}"},
    )

# Kernel entity commands are registered statically
# Domain entity commands are registered dynamically from API metadata

def register_entity_commands(entity_name: str, entity_config: dict):
    """Register CLI commands for an entity type."""
    entity_app = typer.Typer(name=entity_name.lower(), help=f"Manage {entity_name} entities")

    @entity_app.command("list")
    def list_cmd(status: str = None, limit: int = 20, format: str = "table"):
        client = get_client()
        params = {"limit": limit}
        if status:
            params["status"] = status
        response = client.get(f"/api/{entity_name.lower()}s", params=params)
        output(response.json(), format)

    @entity_app.command("get")
    def get_cmd(id: str, format: str = "json"):
        client = get_client()
        response = client.get(f"/api/{entity_name.lower()}s/{id}")
        output(response.json(), format)

    @entity_app.command("create")
    def create_cmd(data: str = typer.Option(..., help="JSON data")):
        client = get_client()
        response = client.post(f"/api/{entity_name.lower()}s", json=orjson.loads(data))
        output(response.json(), "json")

    # ... transition, update, delete commands

    app.add_typer(entity_app)

def main():
    # On startup: fetch entity metadata from API, register commands
    # Then run the CLI
    app()
```

The CLI always operates as an HTTP client. `INDEMN_API_URL` determines where it connects.

## 1.15 Auto-Generated API

FastAPI routes registered from entity definitions at startup.

```python
# kernel/api/app.py
from fastapi import FastAPI, Depends
from kernel.db import init_database, ENTITY_REGISTRY
from kernel.api.registration import register_entity_routes
from kernel.auth.middleware import get_current_actor

app = FastAPI(title="Indemn OS API")

@app.on_event("startup")
async def startup():
    await init_database()
    for entity_name, entity_cls in ENTITY_REGISTRY.items():
        register_entity_routes(app, entity_name, entity_cls)
```

```python
# kernel/api/registration.py
from fastapi import APIRouter, Depends, HTTPException
from kernel.auth.middleware import get_current_actor, check_permission
from kernel.scoping.org_scoped import OrgScopedCollection

def register_entity_routes(app, entity_name: str, entity_cls: type):
    router = APIRouter(prefix=f"/api/{entity_name.lower()}s", tags=[entity_name])

    @router.get("/")
    async def list_entities(
        limit: int = 20, offset: int = 0,
        actor=Depends(get_current_actor),
    ):
        check_permission(actor, entity_name, "read")
        collection = OrgScopedCollection(
            entity_cls.get_motor_collection(), actor.org_id
        )
        cursor = collection.find().skip(offset).limit(limit)
        return [doc async for doc in cursor]

    @router.get("/{entity_id}")
    async def get_entity(entity_id: str, actor=Depends(get_current_actor)):
        check_permission(actor, entity_name, "read")
        # Fetch with org scoping
        ...

    @router.post("/")
    async def create_entity(data: dict, actor=Depends(get_current_actor)):
        check_permission(actor, entity_name, "write")
        entity = entity_cls(org_id=actor.org_id, **data)
        await entity.save_tracked(actor_id=str(actor.id))
        return entity.dict()

    @router.post("/{entity_id}/transition")
    async def transition_entity(
        entity_id: str, to: str, reason: str = None,
        actor=Depends(get_current_actor),
    ):
        check_permission(actor, entity_name, "write")
        entity = await entity_cls.get(entity_id)
        entity.transition_to(to, reason)
        await entity.save_tracked(actor_id=str(actor.id))
        return entity.dict()

    app.include_router(router)
```

## 1.16 Auto-Generated Skills

```python
# kernel/skill/generator.py

def generate_entity_skill(entity_name: str, definition) -> str:
    """Generate a markdown skill document from an entity definition."""
    sections = []

    sections.append(f"# {entity_name}\n")

    # Fields table
    sections.append("## Fields\n")
    sections.append("| Field | Type | Required | Description |")
    sections.append("|-------|------|----------|-------------|")
    for name, field_def in definition.fields.items():
        sections.append(f"| {name} | {field_def.type} | {'Yes' if field_def.required else 'No'} | {field_def.description or ''} |")

    # State machine
    if definition.state_machine:
        sections.append("\n## Lifecycle\n")
        for state, transitions in definition.state_machine.items():
            sections.append(f"- **{state}** -> {', '.join(transitions)}")

    # CLI commands
    sections.append(f"\n## Commands\n")
    slug = entity_name.lower()
    sections.append(f"| Command | Description |")
    sections.append(f"|---------|-------------|")
    sections.append(f"| `indemn {slug} list` | List with filters |")
    sections.append(f"| `indemn {slug} get <id>` | Get by ID |")
    sections.append(f"| `indemn {slug} create` | Create new |")
    sections.append(f"| `indemn {slug} update <id>` | Update fields |")
    if definition.state_machine:
        sections.append(f"| `indemn {slug} transition <id> --to <state>` | Change state |")

    # Activated capabilities
    for cap in (definition.activated_capabilities or []):
        sections.append(f"| `indemn {slug} {cap.capability.replace('_', '-')} <id> --auto` | {cap.capability} |")

    return "\n".join(sections)
```

Skills are stored in the `skills` MongoDB collection and regenerated when entity definitions change.

## 1.17 Authentication (Phase 1 Scope)

**Phase 1 auth scope** (MVP of the MVP):
- Session kernel entity
- Password authentication method (Argon2id)
- Token authentication method (for associates and CLI automation)
- JWT access tokens (stateless verification, 15-minute default)
- Auth middleware on every API request
- Permission enforcement (role-based entity access)

**Deferred to later phases**: SSO via Integration, TOTP MFA, magic links, platform admin cross-org, revocation cache with Change Streams, refresh tokens.

```python
# kernel/auth/middleware.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from kernel.auth.jwt import verify_access_token
from kernel_entities.actor import Actor

security = HTTPBearer()

async def get_current_actor(request: Request, credentials=Depends(security)) -> Actor:
    """Verify JWT and return the authenticated Actor."""
    payload = verify_access_token(credentials.credentials)
    actor = await Actor.get(payload["actor_id"])
    if not actor or actor.status != "active":
        raise HTTPException(status_code=401, detail="Invalid or inactive actor")
    # Attach org context for downstream scoping
    request.state.org_id = str(actor.org_id)
    request.state.actor = actor
    return actor

def check_permission(actor: Actor, entity_type: str, action: str):
    """Check if actor's roles grant the required permission."""
    # Load roles, check permissions dict
    # Raise HTTPException(403) if denied
    ...
```

## 1.18 OTEL Instrumentation

Baked in from the start. Every entity save, every watch evaluation, every rule evaluation, every CLI command gets a span.

```python
# kernel/observability/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from contextlib import contextmanager

tracer = trace.get_tracer("indemn-os")

@contextmanager
def create_span(name: str, **attributes):
    with tracer.start_as_current_span(name, attributes=attributes) as span:
        yield span

def init_tracing():
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
```

The `correlation_id` on messages IS the OTEL trace ID. One trace connects: entity save → watch evaluation → message creation → (in Phase 2) Temporal workflow → CLI commands.

## 1.19 Queue Processor

A persistent process that dispatches Temporal workflows for associate-eligible messages and handles escalation.

```python
# kernel/queue_processor.py
"""
Entry point: python -m kernel.queue_processor

Runs a polling loop that:
1. Finds pending messages targeting roles with associate actors
2. Starts Temporal workflows for them (optimistic dispatch backstop)
3. Checks escalation deadlines
4. Creates scheduled task messages from cron triggers
"""

async def run_sweep():
    # Find messages that should have workflows but don't
    # Start workflows for them
    # Check visibility timeouts (stuck messages)
    # Check escalation deadlines
    ...

async def main():
    await init_database()
    while True:
        await run_sweep()
        await asyncio.sleep(5)  # 5-second sweep interval
```

In Phase 1, this process exists and runs but Temporal integration is minimal (Phase 2). Its primary function in Phase 1 is visibility timeout recovery and escalation checks.

## 1.20 Phase 1 Acceptance Tests

These are the specific tests that prove Phase 1 is complete. They map directly to the white paper's acceptance criteria.

```
1. ENTITY DEFINITION → DYNAMIC CLASS
   - Create an entity definition via API (POST /api/entity_definitions)
   - Restart the API server (simulating rolling restart)
   - The new entity type has CLI commands and API routes
   - The skill is auto-generated and stored

2. ENTITY CRUD + STATE MACHINE
   - Create an instance of the dynamic entity
   - Read it back via API and CLI
   - Update fields
   - Transition state (valid transition succeeds)
   - Attempt invalid transition (rejected with error)
   - Delete the entity

3. ORGANIZATION SCOPING
   - Create two organizations
   - Create entities in each
   - Query from org A — only org A's entities returned
   - Query from org B — only org B's entities returned
   - Attempt cross-org access — denied

4. CHANGES COLLECTION
   - Create, update, transition an entity
   - Query changes collection — every mutation recorded
   - Each record has: entity_id, actor_id, field changes, timestamp
   - Hash chain is intact (verify with audit command)

5. WATCH EVALUATION → MESSAGE
   - Create a role with a watch (e.g., "Email:created")
   - Create an entity matching the watch
   - A message appears in message_queue targeting that role
   - Message has correct correlation_id, event metadata

6. CONDITIONAL WATCH
   - Create a role with a conditional watch (e.g., "Assessment:created WHERE needs_review=true")
   - Create an entity where condition is false — no message
   - Create an entity where condition is true — message created

7. RULE EVALUATION (--auto)
   - Create classification rules for an entity type
   - Invoke the auto_classify capability
   - Rule matches → deterministic result returned
   - No rule matches → needs_reasoning=true returned
   - Veto rule fires → needs_reasoning=true with veto context

8. LOOKUPS
   - Create a lookup table
   - Rule references the lookup
   - Evaluation resolves through the lookup correctly

9. AUTHENTICATION
   - Create an actor with password method
   - Login → receive JWT access token
   - Use token to access API — succeeds
   - Use expired/invalid token — rejected
   - Create service token for an associate actor
   - Use service token to access API — succeeds

10. PERMISSION ENFORCEMENT
    - Create two roles with different permissions
    - Actor with read-only role cannot create entities
    - Actor with write role can create entities
    - Permissions checked on every API request

11. SKILL AUTO-GENERATION
    - Define an entity with fields, state machine, capabilities
    - Generated skill documents all fields, states, CLI commands
    - Skill is stored in MongoDB and retrievable via API

12. END-TO-END FLOW
    - Define a domain entity type via CLI
    - Create a role with watches for that entity type
    - Create rules for that entity type
    - Create an instance
    - Watch fires → message in queue
    - Invoke --auto capability → rule evaluates
    - Changes collection records everything
    - OTEL traces connect the full flow
```

## 1.21 Open Questions (To Resolve During Implementation)

1. **Beanie + dynamic models integration testing.** The `create_model(__base__=BaseEntity)` → `init_beanie()` path needs a prototype spike early in Phase 1 to validate the approach works end-to-end including indexes, Settings class, and save hooks. If it doesn't work cleanly, fallback is raw Motor + Pydantic for domain entities (Beanie only for kernel entities), per data architecture review finding #9.

2. **Watch cache invalidation timing.** When a Role entity is saved (adding/removing a watch), the cache must be invalidated. The architecture specifies immediate invalidation on kernel entity save. Implementation needs to handle the multi-instance case (multiple API server replicas with separate caches). For MVP (single replica), in-process invalidation is sufficient. For scale, Change Streams on the roles collection propagate invalidation.

3. **CLI dynamic command registration.** The CLI needs to discover entity types from the API at startup. This requires the API to expose an entity metadata endpoint (`GET /api/_meta/entities`) that lists all registered entity types with their field definitions and available operations. The CLI fetches this on each invocation (CLI is ephemeral — always fresh).

4. **Flexible data validation.** When an entity has a `flexible_data_schema` reference, writes to the `data` field must validate against that schema. The schema itself is stored as a separate definition. Implementation of schema resolution and validation is Phase 1 scope but the specific JSON Schema or Pydantic-based validation approach needs prototyping.
