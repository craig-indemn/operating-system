---
ask: "How is the OS designed — entity framework, API/CLI, associate system, and key decisions?"
created: 2026-03-30
workstream: product-vision
session: 2026-03-30-a
sources:
  - type: conversation
    description: "Craig and Claude design session, 2026-03-30"
  - type: research
    description: "Open source framework landscape research, DDD patterns, Django/Rails architecture patterns"
---

# Design: Layer 1 — Entity Framework

## Architecture Decision: Modular Monolith with Rich Domain Entities

### Pattern: DDD-style modular monolith (Django/Rails pattern)
- Rich domain entities as Python classes extending a base Entity
- Service layer for deterministic cross-entity operations
- Event system for cross-domain side effects
- Associate layer for non-deterministic orchestration (reasoning required)
- One deployable unit with clear sub-domain boundaries
- Can be split into services later if needed

### Why this pattern:
- Craig is building primarily alone with AI — microservices add unnecessary operational complexity
- Modular monolith is simpler to build, deploy, and debug
- Sub-domain boundaries provide the same logical separation as microservices
- Battle-tested (Django has done this for 20 years)
- A modular monolith can be split into microservices later if scale demands it

### Patterns considered and rejected:
- **YAML generator + runtime engine**: Separates data from behavior, not OO. Adds indirection. The entity classes ARE the definitions.
- **Microservices per sub-domain**: Too much operational overhead for a solo builder. Can evolve toward this later.
- **CQRS + Event Sourcing**: Too complex for initial build. Event sourcing can be added to specific sub-domains later if needed (e.g., for audit trails on Policy).

## Technology Stack

### Core Libraries

| Library | Role | Why |
|---------|------|-----|
| **Beanie** | Async MongoDB ODM | Built on Pydantic + Motor. Pydantic models ARE MongoDB documents. Async CRUD, indexes, hooks, relationships. Designed for the FastAPI + MongoDB + Pydantic combination. Handles the persistence layer so we only build state machine, events, permissions, auto-registration on top. |
| **Pydantic** | Validation + serialization | Already in stack (FastAPI depends on it). Type validation, schema export, FastAPI request/response models. Beanie uses Pydantic models as its document class. |
| **Motor** | Async MongoDB driver | Comes with Beanie. Required for async FastAPI — synchronous pymongo would block the event loop. |
| **FastAPI** | API framework | Already used by bot-service and platform-v2. Async, Pydantic-native. |
| **Typer** | CLI framework | Built by the FastAPI creator. Uses type hints for argument parsing — same mental model as FastAPI/Pydantic. Natural fit for auto-generating CLI commands from entities. |
| **RabbitMQ** | Domain event bus | Already in infrastructure (Amazon MQ). Domain events published to RabbitMQ, subscribers consume. Durable, survives restarts, works across service instances. Ready for future service splitting. |

### Future Considerations

| Library | Role | When |
|---------|------|------|
| **Celery** | Async task execution | When event handlers need to do time-consuming work (send emails, generate documents, call external APIs) without blocking the API response. Uses RabbitMQ as broker (already available). |

## The Base Entity Class

Beanie Document (Pydantic model + MongoDB persistence) extended with state machine, events, permissions, and auto-registration.

Beanie gives us for free: async CRUD, index management, pre/post hooks, Link/BackLink relationships, aggregation pipelines. We add on top: state machine enforcement, domain events via RabbitMQ, permission checks, API/CLI/skill auto-registration.

```python
from beanie import Document, Indexed, Link, BackLink
from pydantic import Field
from datetime import datetime
from bson import ObjectId

class Entity(Document, StateMachineMixin, EventMixin, AutoRegisterMixin):
    """Base class for all OS entities. Extends Beanie Document with
    state machine, events, permissions, and auto-registration."""

    # Beanie handles _id automatically
    org_id: Indexed(ObjectId)       # Multi-tenancy — always scoped, indexed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str                  # User or associate ID

    # Subclasses define:
    # sub_domain: str               # Which sub-domain
    # state_machine: dict           # Status transitions
    # permissions: dict             # Role-based access

    class Settings:
        # Beanie document settings
        use_state_management = True  # Track document changes

    class Config:
        # Pydantic config
        arbitrary_types_allowed = True
```

### What the base Entity provides automatically:

| Capability | How |
|------------|-----|
| **CRUD** | `Entity.create()`, `Entity.get()`, `Entity.list()`, `.save()`, `.delete()` |
| **State machine** | `.transition_to(status)` — enforces valid transitions, emits events |
| **Events** | `.emit(event_name, data)` — domain event bus |
| **Permissions** | Checked before every operation based on entity's permission config |
| **Multi-tenancy** | `org_id` injected into every query automatically |
| **Validation** | Pydantic validates all fields on create/update |
| **Serialization** | To/from MongoDB documents, API responses, CLI output |
| **API routes** | Auto-registered FastAPI routes for CRUD + state transitions |
| **CLI commands** | Auto-registered CLI commands mirroring the API |
| **Skill generation** | Auto-generated markdown documenting all operations |
| **Timestamps** | `created_at`, `updated_at` managed automatically |
| **Audit trail** | `created_by` + event history |

## Entity Definition Example

```python
from beanie import Document, Indexed, Link
from pydantic import Field
from decimal import Decimal
from datetime import date
from typing import Literal, Optional, List

class Policy(Entity):
    sub_domain = "policy_lifecycle"

    # Core fields — Pydantic validates types automatically
    policy_number: Indexed(str, unique=True)
    effective_date: date
    expiration_date: date
    written_premium: Decimal = Decimal("0")
    status: Literal["issued", "active", "endorsed", "renewed",
                     "cancelled", "expired"] = "issued"

    # Relationships — Beanie Link for lazy resolution
    insured: Link["Insured"]
    carrier: Link["Carrier"]
    product: Link["Product"]

    # Flexible data — product-specific fields
    data: dict = Field(default_factory=dict)

    # State machine
    state_machine = {
        "issued": ["active"],
        "active": ["endorsed", "renewed", "cancelled", "expired"],
        "endorsed": ["active"],
    }

    # Permissions
    permissions = {
        "read": ["agent", "underwriter", "admin", "associate"],
        "write": ["underwriter", "admin", "associate"],
    }

    class Settings:
        name = "policies"  # MongoDB collection name
        indexes = [
            [("org_id", 1), ("status", 1)],
            [("org_id", 1), ("carrier.$id", 1)],
            [("org_id", 1), ("expiration_date", 1)],
        ]

    # Domain behavior — insurance-specific logic
    async def bind(self, quote: "Quote") -> "Policy":
        """Bind a policy from an accepted quote."""
        self.written_premium = quote.premium
        self.transition_to("active")
        await self.save()
        await self.emit("policy.bound", {"premium": str(self.written_premium)})
        return self

    async def endorse(self, changes: dict) -> "PolicyTransaction":
        """Apply an endorsement."""
        txn = PolicyTransaction(
            org_id=self.org_id,
            policy=self,
            type="endorsement",
            changes=changes,
            created_by=get_current_user()
        )
        await txn.insert()
        self.transition_to("endorsed")
        await self.save()
        return txn

    async def check_renewal(self) -> dict:
        """Evaluate renewal — compare new vs expiring premium."""
        await self.fetch_link(Policy.carrier)  # Resolve the carrier link
        new_premium = await self.carrier.get_renewal_rate(self)
        change_pct = (new_premium - self.written_premium) / self.written_premium
        return {
            "current_premium": self.written_premium,
            "renewal_premium": new_premium,
            "change_pct": change_pct,
            "remarket_recommended": change_pct > Decimal("0.15")
        }
```

### What Beanie gives us vs. what we build:

| Capability | Beanie (free) | We build |
|------------|---------------|----------|
| CRUD (insert, find, update, delete) | Yes | — |
| Index management | Yes | — |
| Link/BackLink relationships | Yes | — |
| Pre/post hooks (before_insert, after_save) | Yes | — |
| Aggregation pipelines | Yes | — |
| Document state tracking | Yes | — |
| Pydantic validation | Yes (inherits) | — |
| **State machine enforcement** | — | StateMachineMixin |
| **Domain events via RabbitMQ** | — | EventMixin |
| **Permission checks** | — | PermissionsMixin |
| **API route auto-registration** | — | AutoRegisterMixin |
| **CLI command auto-registration** | — | AutoRegisterMixin |
| **Skill auto-generation** | — | SkillGeneratorMixin |
| **Org-scoped queries** | — | Override find/get to inject org_id |

## Project Structure

```
indemn-os/
  core/
    entity.py              # Base Entity class (Pydantic + mixins)
    persistence.py         # MongoDB operations (MongoDocument mixin)
    state_machine.py       # State machine enforcement (StateMachineMixin)
    events.py              # Domain event bus (EventMixin)
    registration.py        # Auto-discovery + API/CLI/skill registration
    permissions.py         # Permission enforcement
    relationships.py       # Relationship + HasMany descriptors
    flexible_data.py       # FlexibleData field with schema validation
    skill_generator.py     # Auto-generate skill markdown from entity class

  domains/
    core_insurance/
      entities/
        product.py
        policy_form.py
      services/
        product_service.py

    risk_parties/
      entities/
        contact.py         # Contact/Party base
        insured.py
        carrier.py
        retail_agent.py
        agency.py
        distribution_partner.py
      services/
        party_service.py

    submission_quoting/
      entities/
        submission.py
        quote.py
      services/
        intake_service.py
        quoting_service.py

    policy_lifecycle/
      entities/
        policy.py
        certificate.py
        binder.py
      services/
        binding_service.py
        renewal_service.py

    claims/
      entities/
        claim.py
        incident.py
      services/
        claims_service.py

    financial/
      entities/
        payment.py
        invoice.py
        commission_schedule.py
        commission_transaction.py
        revenue_share_agreement.py
        premium_trust_account.py
        bordereaux.py
      services/
        billing_service.py
        commission_service.py

    authority_compliance/
      entities/
        delegated_authority.py
        referral.py
        license.py
        producer_appointment.py
        surplus_lines_transaction.py
        regulatory_filing.py
      services/
        compliance_service.py

    distribution_delivery/
      entities/
        program.py
        deployment.py
        carrier_agreement.py
      services/
        deployment_service.py

    platform/
      entities/
        associate.py
        skill_entity.py    # Skill as a managed entity
        workflow.py
        template.py
        knowledge_base.py
        organization.py
        task.py
        interaction.py
        correspondence.py
        document.py
        email.py
        draft.py
      services/
        associate_service.py
        deployment_service.py

  api/
    app.py                 # FastAPI app — auto-discovers and registers entity routes
    middleware.py           # Auth, org scoping, error handling

  cli/
    main.py                # CLI entry point — auto-discovers and registers entity commands

  skills/
    generated/             # Auto-generated skill files from entity classes

  events/
    handlers/              # Event handlers organized by domain
    bus.py                 # Event bus implementation
```

## Cross-Entity Operations: The Layered Pattern

### Entity Methods — Single entity behavior
```python
# Policy knows its own behavior
policy.bind(quote)
policy.endorse(changes)
policy.check_renewal()
```

### Services — Deterministic multi-entity orchestration
```python
# BindingService orchestrates a defined sequence across entities
class BindingService:
    def bind(self, submission_id, quote_id):
        submission = Submission.get(submission_id)
        quote = Quote.get(quote_id)

        policy = Policy.create(
            insured=submission.insured,
            carrier=quote.carrier,
            product=submission.product
        )
        policy.bind(quote)
        submission.transition_to("bound")
        quote.transition_to("accepted")
        return policy
```

Services also get CLI commands:
```bash
indemn bind --submission SUB-001 --quote QUO-001
```

### Events — Cross-domain side effects (loose coupling)
```python
# Policy emits event
self.emit("policy.bound", {"policy_id": self.id, "premium": self.written_premium})

# Financial domain subscribes
@on_event("policy.bound")
def create_commission(event):
    CommissionTransaction.create(
        policy_id=event["policy_id"],
        schedule=CommissionSchedule.get_for_policy(event["policy_id"])
    )
```

Originating entity doesn't know about subscribers. Sub-domains stay decoupled.

### Associates — Non-deterministic orchestration
```
# The Intake Skill:
When a new submission email arrives:
1. indemn email classify --id {email_id}
2. Based on classification, decide next step:
   - If new submission: indemn submission create ...
   - If follow-up: indemn submission update ...
   - If unrelated: indemn task create --type manual-review
3. indemn submission validate --id {sub_id}
4. If incomplete, indemn draft create --type info-request ...
5. If complete, indemn submission route --id {sub_id}
```

Associates reason about WHAT to do. Entities and services handle HOW.

| Pattern | When | Example | Deterministic? |
|---------|------|---------|---------------|
| Entity method | Single entity, own behavior | `policy.endorse(changes)` | Yes |
| Service | Multi-entity, defined sequence | `BindingService.bind()` | Yes |
| Event | Cross-domain side effect | `policy.bound → commission` | Yes (handler is deterministic) |
| Associate | Reasoning required | Process inbound submission | No (AI decides) |

## Flexible Fields (Product Configuration)

Entities have core typed fields + a flexible `data` field for product-specific information:

```python
class Submission(Entity):
    # Core — every submission
    insured = Relationship("Insured", required=True)
    carrier = Relationship("Carrier")
    lob: str
    status: str
    product = Relationship("Product", required=True)

    # Flexible — varies by product
    data: FlexibleData = FlexibleData(schema_from="product.form_schema")

    def validate_completeness(self):
        schema = self.product.form_schema
        missing = schema.get_missing_required(self.data)
        return {"complete": len(missing) == 0, "missing": missing}
```

Product defines the schema:
```python
class Product(Entity):
    name: str
    lob: str
    carrier = Relationship("Carrier")
    form_schema: dict    # {fields: [{name, type, required, validation}...]}
    validation_rules: dict
    workflow_rules: dict
```

MongoDB stores it naturally — core fields are typed/indexed, product-specific data is a nested document in `data`.

## Multi-Tenancy

Every entity scoped by `org_id`. Enforced at the base Entity level — impossible to bypass:

```python
class Entity:
    org_id: ObjectId  # Required, auto-injected from auth context

    @classmethod
    def list(cls, **filters):
        filters["org_id"] = get_current_org_id()  # Always injected
        return cls._find(filters)

    @classmethod
    def get(cls, id):
        doc = cls._find_one({"_id": id, "org_id": get_current_org_id()})
        if not doc:
            raise NotFound()
        return doc
```

Compound indexes: `(org_id, status)`, `(org_id, carrier_id)`, `(org_id, lob)`, etc.

## Database: MongoDB

Decision: stay on MongoDB (current stack, team expertise, Atlas infrastructure).

**Why MongoDB fits:**
- Document model handles flexible fields naturally (no migrations for new product schemas)
- Schema-per-document supports insurance's inherent field variability
- Atlas provides managed scaling, backups, monitoring
- Team already uses it for everything
- Beanie (async ODM) provides the Python interface — Pydantic models as documents, async via Motor

**Considerations:**
- Relationships are references (Beanie Link/BackLink), resolved via `fetch_link()` — not JOINs
- Complex cross-entity queries use Beanie's aggregation pipeline support
- Compound indexes defined in entity Settings class, managed by Beanie

---

# Design: Layer 2 — API, CLI, and Skills

## Core Principle: Thin Interfaces, Shared Entity Layer

Both API and CLI are thin interfaces that call into the same entity layer. Neither contains business logic — entities and services do.

```
API Request  → FastAPI route  → Entity/Service method → MongoDB
CLI Command  → Typer handler  → Entity/Service method → MongoDB
Associate    → CLI command    → Entity/Service method → MongoDB
Tier 3 dev   → API call       → Entity/Service method → MongoDB
```

One code path. Auth context is set differently per consumer, but entity permission checks work identically regardless of entry point.

CLI does NOT call the API — both call entity methods directly. This means the CLI works without the API server running (useful for development, admin tasks, associate execution, and parallel build sessions).

## API Auto-Registration (FastAPI)

At startup, the framework discovers all Entity subclasses and registers routes:

### Generated CRUD routes (every entity gets these):
```
GET    /api/{collection}                → Entity.find(filters)      # List with filtering/pagination
GET    /api/{collection}/{id}           → Entity.get(id)            # Get by ID
POST   /api/{collection}                → Entity(**data).insert()   # Create
PUT    /api/{collection}/{id}           → entity.set(data)          # Update
DELETE /api/{collection}/{id}           → entity.delete()           # Delete (if permitted)
POST   /api/{collection}/{id}/transition → entity.transition_to()   # State change
```

### Custom method routes (from @exposed decorator):
```
POST   /api/policies/{id}/bind           → policy.bind(quote_id)
GET    /api/policies/{id}/check-renewal  → policy.check_renewal()
```

### Service routes:
```
POST   /api/services/binding/bind        → BindingService.bind(submission_id, quote_id)
```

### How auto-registration works:

```python
# core/registration.py
from fastapi import APIRouter

def register_entity_routes(app: FastAPI, entity_cls: type[Entity]):
    """Auto-generate FastAPI routes from an Entity class."""
    router = APIRouter(prefix=f"/api/{entity_cls.Settings.name}", tags=[entity_cls.__name__])

    @router.get("/")
    async def list_entities(**filters):
        return await entity_cls.find(org_id=get_current_org_id(), **filters).to_list()

    @router.get("/{id}")
    async def get_entity(id: str):
        return await entity_cls.get_scoped(id)  # org-scoped get

    @router.post("/")
    async def create_entity(data: entity_cls.CreateModel):  # Pydantic model auto-derived
        entity = entity_cls(**data.dict(), org_id=get_current_org_id())
        await entity.insert()
        return entity

    @router.post("/{id}/transition")
    async def transition(id: str, to: str, reason: str = None):
        entity = await entity_cls.get_scoped(id)
        entity.transition_to(to, reason=reason)
        await entity.save()
        return entity

    # Register @exposed methods as additional routes
    for method_name, method in entity_cls.get_exposed_methods():
        register_method_route(router, entity_cls, method_name, method)

    app.include_router(router)

# At startup
def init_app():
    app = FastAPI(title="Indemn OS")
    for entity_cls in Entity.get_all_subclasses():
        register_entity_routes(app, entity_cls)
    for service_cls in Service.get_all_subclasses():
        register_service_routes(app, service_cls)
    return app
```

## CLI Auto-Registration (Typer)

Same pattern. Discover entities, generate commands:

### Generated CRUD commands (every entity):
```bash
indemn policy list [--status active] [--carrier CARR-001] [--limit 20] [--format json|table]
indemn policy get POL-001 [--include insured,coverages] [--format json|table]
indemn policy create --effective-date 2026-04-01 --insured INS-001 --carrier CARR-001
indemn policy update POL-001 --written-premium 5000
indemn policy delete POL-001
indemn policy transition POL-001 --to active [--reason "Binding complete"]
```

### Custom method commands (from @exposed):
```bash
indemn policy bind POL-001 --quote-id QUO-001
indemn policy check-renewal POL-001
```

### Service commands:
```bash
indemn binding bind --submission-id SUB-001 --quote-id QUO-001
```

### How auto-registration works:

```python
# core/cli_registration.py
import typer

def register_entity_commands(cli: typer.Typer, entity_cls: type[Entity]):
    """Auto-generate Typer commands from an Entity class."""
    entity_app = typer.Typer(name=entity_cls.cli_name(), help=entity_cls.__doc__)

    @entity_app.command("list")
    def list_cmd(status: str = None, limit: int = 20, format: str = "table"):
        results = run_async(entity_cls.find(org_id=ctx_org_id(), status=status).to_list(limit))
        output(results, format)

    @entity_app.command("get")
    def get_cmd(id: str, include: str = None, format: str = "table"):
        entity = run_async(entity_cls.get_scoped(id))
        if include:
            for link in include.split(","):
                run_async(entity.fetch_link(getattr(entity_cls, link)))
        output(entity, format)

    @entity_app.command("transition")
    def transition_cmd(id: str, to: str, reason: str = None):
        entity = run_async(entity_cls.get_scoped(id))
        entity.transition_to(to, reason=reason)
        run_async(entity.save())
        output(entity)

    # Register @exposed methods as commands
    for method_name, method in entity_cls.get_exposed_methods():
        register_method_command(entity_app, entity_cls, method_name, method)

    cli.add_typer(entity_app)

# Entry point
def init_cli():
    cli = typer.Typer(name="indemn", help="Indemn OS CLI")
    for entity_cls in Entity.get_all_subclasses():
        register_entity_commands(cli, entity_cls)
    for service_cls in Service.get_all_subclasses():
        register_service_commands(cli, service_cls)
    return cli
```

### Relationship to existing Indemn CLI:
The current `indemn` CLI (agent creation, evaluation, exports) extends with entity commands. Same binary, growing command tree. `indemn agent create` still works. `indemn policy list` is new. Existing commands migrate into the entity framework over time (Agent becomes an Entity with @exposed methods).

## The @exposed Decorator

Marks entity/service methods as publicly accessible via API and CLI:

```python
def exposed(method):
    """Mark a method for auto-registration as API endpoint + CLI command.

    Inspects type hints to generate:
    - FastAPI route with request/response models
    - Typer command with typed arguments
    - Skill documentation entry
    """
    method._exposed = True
    return method
```

The framework inspects the method's:
- **Name** → route path / command name (snake_case → kebab-case for CLI)
- **Parameters with type hints** → API request body / CLI arguments
- **Return type** → API response model
- **Docstring** → API description / CLI help text / skill documentation
- **HTTP method inference** → GET if no parameters beyond self, POST if parameters

Methods WITHOUT @exposed are internal — used by other entity methods, services, or event handlers. Not accessible via API or CLI.

## Skill Auto-Generation

The skill generator inspects entity classes and produces markdown:

```python
# core/skill_generator.py

def generate_skill(entity_cls: type[Entity]) -> str:
    """Generate skill markdown from an entity class."""

    sections = []

    # Entity description from class docstring
    sections.append(f"# {entity_cls.__name__}\n\n{entity_cls.__doc__}")

    # Fields from Pydantic model
    sections.append("## Fields\n" + format_fields(entity_cls.model_fields))

    # State machine from class attribute
    if hasattr(entity_cls, 'state_machine'):
        sections.append("## Lifecycle\n" + format_state_machine(entity_cls.state_machine))

    # CRUD commands (always present)
    sections.append("## Commands\n" + format_crud_commands(entity_cls))

    # @exposed methods with docstrings and parameters
    for name, method in entity_cls.get_exposed_methods():
        sections.append(format_method_docs(entity_cls, name, method))

    # Relationships
    sections.append("## Relationships\n" + format_relationships(entity_cls))

    # Permissions
    sections.append("## Permissions\n" + format_permissions(entity_cls.permissions))

    # Events
    sections.append("## Events\n" + format_events(entity_cls))

    return "\n\n".join(sections)
```

### Self-documenting system — a key vision point

The skills are always accurate because they're generated from the code:
- Add a field → schema docs update
- Add an @exposed method → new operation appears in skill
- Change the state machine → lifecycle docs update
- Change permissions → access docs update

**No documentation maintenance.** The system describes itself.

Three audiences, one artifact:
| Audience | How they use the skill |
|----------|----------------------|
| **Associates** | Read to know what CLI commands to call and what parameters to pass |
| **Tier 3 developers** | Read as API/CLI reference documentation |
| **Indemn engineers** | Read as entity behavior reference |

The developer portal serves auto-generated skills. The associate loads skills at runtime. Engineers read them during development. All from the same source — the entity class itself.

## Auth Model

### Authentication Methods

| Consumer | Method | How |
|----------|--------|-----|
| Internal users | JWT | `indemn login` → token cached in `~/.indemn/config` |
| Associates | Service token | Per-associate token with scoped permissions, set in associate config |
| Tier 3 developers | API key | Generated on signup, scoped to organization |
| CLI (interactive) | JWT | Same as internal users — `indemn login` |
| CLI (automated) | Service token | Token in env var or config file |

### Auth Flow

```
Request arrives (API or CLI)
  → Extract auth token/key
  → Resolve: org_id, user_id, role, permissions
  → Set auth context (thread-local or async context var)
  → Entity/Service methods read from auth context:
      get_current_org_id()    → used for multi-tenancy scoping
      get_current_user()      → used for audit trail (created_by)
      get_current_permissions() → used for permission checks
```

### Permission Enforcement

Permissions are checked at the entity layer, not the API/CLI layer. This ensures they work regardless of entry point:

```python
class Entity:
    async def _check_permission(self, action: str):
        """Called before every operation."""
        role = get_current_role()
        allowed_roles = self.permissions.get(action, [])
        if role not in allowed_roles:
            raise PermissionDenied(f"{role} cannot {action} {self.__class__.__name__}")
```

## Output Formats

Both API and CLI support multiple output formats:

| Format | API | CLI |
|--------|-----|-----|
| JSON | Default response | `--format json` |
| Table | N/A | `--format table` (default for list) |
| YAML | `Accept: application/yaml` | `--format yaml` |

CLI defaults to human-readable table for `list` and structured output for `get`. JSON for piping to other commands or associate consumption.

---

## How This Gets Built (Parallel Sessions)

### Wave 1 — Core Framework (dependency for everything else)
**Session 1**: Base Entity class on Beanie — persistence, state machine, events, permissions, relationships, flexible data, @exposed decorator

### Wave 2 — Framework Interfaces (can run in parallel with each other, depends on Wave 1)
**Session 2**: API auto-registration — FastAPI app, entity route generation, service route generation, auth middleware
**Session 3**: CLI auto-registration — Typer app, entity command generation, service command generation, auth handling
**Session 4**: Skill generator — inspect entity classes, produce markdown, output to skills/generated/

### Wave 3 — Domain Entities (can ALL run in parallel, depends on Wave 1)
- **Session 5**: Core Insurance (Product, PolicyForm)
- **Session 6**: Risk & Parties (Contact, Insured, Carrier, Agent, Agency, DistributionPartner)
- **Session 7**: Submission & Quoting (Submission, Quote) + IntakeService, QuotingService
- **Session 8**: Policy Lifecycle (Policy, Certificate, Binder) + BindingService, RenewalService
- **Session 9**: Claims (Claim, Incident) + ClaimsService
- **Session 10**: Financial (Payment, Invoice, Commission entities) + BillingService, CommissionService
- **Session 11**: Authority & Compliance (DelegatedAuthority, License, etc.)
- **Session 12**: Distribution & Delivery (Program, Deployment, CarrierAgreement)
- **Session 13**: Platform (Associate, Skill, Workflow, Organization, etc.)

### Wave 4 — Integration (depends on Waves 2 + 3)
**Session 14**: Event handlers — cross-domain subscriptions via RabbitMQ
**Session 15**: Integration tests — full stack verification
**Session 16**: Skill generation run — produce all skill files from completed entities

### Timeline Estimate
- Wave 1: 1-2 days (the critical path)
- Wave 2: 1-2 days (parallel with Wave 3)
- Wave 3: 2-3 days (9 parallel sessions)
- Wave 4: 1-2 days
- **Total: ~1 week for the foundation**

## Key Architectural Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Modular monolith | Solo builder, can split later |
| Entity definition | Python classes (not YAML) | OO, data + behavior together |
| Persistence | Beanie (async ODM) | Pydantic models as MongoDB documents, async CRUD, indexes, hooks, relationships — handles persistence layer |
| Validation | Pydantic (via Beanie) | Already in stack, type validation, serialization, schema export |
| Async driver | Motor (via Beanie) | Required for async FastAPI — sync pymongo blocks event loop |
| Database | MongoDB (Atlas) | Current stack, flexible documents, managed |
| API framework | FastAPI | Already used, Pydantic-native, async |
| CLI framework | Typer | From FastAPI creator, type-hint driven, same mental model |
| Event bus | RabbitMQ | Already in infrastructure (Amazon MQ), durable, cross-service ready |
| Cross-entity (same domain) | Services | Deterministic orchestration |
| Cross-entity (cross domain) | Events via RabbitMQ | Loose coupling between sub-domains |
| Non-deterministic orchestration | Associates | AI reasoning via skills + CLI |
| Multi-tenancy | org_id on every document | Simple, enforced at base class, Beanie indexed |
| Flexible fields | dict + Product form_schema | Core fields typed via Pydantic, product-specific data in flexible dict |
| API routes | Auto-registered from entity class | FastAPI routes generated at startup |
| CLI commands | Auto-registered from entity class | Typer commands generated at startup |
| Skills | Auto-generated from entity class | Serves associates, developers, engineers |
| Async tasks (future) | Celery + RabbitMQ | When needed for long-running event handlers |
