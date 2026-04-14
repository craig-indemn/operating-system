---
ask: "Addendum to Phase 0+1 implementation spec — covering all mechanisms from the white paper and artifacts that were missing or underspecified"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1.md"
    description: "The base spec this addendum completes"
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Cross-referenced for completeness"
  - type: artifact
    ref: "2026-04-10-realtime-architecture-design.md"
    description: "Attention and Runtime field definitions"
  - type: artifact
    ref: "2026-04-11-authentication-design.md"
    description: "Session field definitions"
  - type: artifact
    ref: "2026-04-09-data-architecture-solutions.md"
    description: "Schema migration, rule validation"
  - type: artifact
    ref: "2026-04-08-pressure-test-findings.md"
    description: "Pre-transition validation hooks"
---

# Phase 0+1 Addendum — Completing the Specification

This addendum covers mechanisms from the white paper and design artifacts that were missing or underspecified in the base Phase 0+1 spec.

---

## A.1 Attention Kernel Entity (Full Specification)

```python
# kernel_entities/attention.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from bson import ObjectId
from datetime import datetime

class Attention(BaseEntity):
    """Active working context — an actor is currently attending
    to an entity with a purpose and a lifetime."""

    actor_id: ObjectId
    target_entity: dict         # {"type": "Interaction", "id": ObjectId}
    related_entities: list[dict] = Field(default_factory=list)
    # [{"type": "Application", "id": ObjectId, "path": "interaction.application_id"}]

    purpose: Literal[
        "real_time_session",    # Associate hosting active Interaction
        "observing",            # Human watching without handling
        "review",               # Human reviewing before action
        "editing",              # Human actively editing
        "claim_in_progress",    # Generic claim-and-work
    ]

    runtime_id: Optional[ObjectId] = None    # For real-time: which Runtime
    workflow_id: Optional[str] = None        # For async: Temporal workflow ID
    session_id: Optional[str] = None         # For real-time: Runtime session handle

    opened_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime                     # TTL boundary

    metadata: dict = Field(default_factory=dict)

    status: Literal["active", "expired", "closed"] = "active"

    _state_machine = {
        "active": ["expired", "closed"],
    }

    class Settings:
        name = "attentions"
        indexes = [
            [("actor_id", 1), ("purpose", 1)],
            [("target_entity.id", 1)],
            [("related_entities.id", 1)],
            [("runtime_id", 1), ("purpose", 1)],
            [("expires_at", 1)],       # TTL expiration
            [("org_id", 1), ("status", 1)],
        ]
```

**Heartbeat bypass**: `save_tracked()` has a special path for heartbeat-only updates that skips changes collection writes and watch evaluation. Detected by checking if the only field changed is `last_heartbeat` and `expires_at`.

## A.2 Runtime Kernel Entity (Full Specification)

```python
# kernel_entities/runtime.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from datetime import datetime

class Runtime(BaseEntity):
    """Deployable host for associate execution."""

    name: str
    kind: Literal["realtime_chat", "realtime_voice", "realtime_sms", "async_worker"]
    framework: str              # "deepagents", "langchain", "custom"
    framework_version: str

    transport: Optional[str] = None     # "websocket", "livekit", "twilio_sms"
    transport_config: dict = Field(default_factory=dict)
    transport_secret_ref: Optional[str] = None

    llm_config: dict = Field(default_factory=dict)
    sandbox_config: dict = Field(default_factory=dict)

    deployment_image: str = ""
    deployment_platform: str = "railway"
    deployment_ref: Optional[str] = None

    capacity: dict = Field(default_factory=lambda: {
        "max_concurrent_sessions": None,
        "max_memory_mb": None,
    })

    status: Literal[
        "configured", "deploying", "active",
        "draining", "stopped", "error",
    ] = "configured"

    instances: list[dict] = Field(default_factory=list)
    # Each: {"instance_id": str, "started_at": datetime,
    #        "last_heartbeat": datetime, "active_sessions": int, "health": str}

    _state_machine = {
        "configured": ["deploying"],
        "deploying": ["active", "error"],
        "active": ["draining", "error"],
        "draining": ["stopped"],
        "stopped": ["deploying"],
        "error": ["configured", "stopped"],
    }

    class Settings:
        name = "runtimes"
        indexes = [
            [("org_id", 1), ("kind", 1), ("status", 1)],
        ]
```

## A.3 Session Kernel Entity (Full Specification)

```python
# kernel_entities/session.py
from kernel.entity.base import BaseEntity
from typing import Optional, Literal
from pydantic import Field
from bson import ObjectId
from datetime import datetime

class Session(BaseEntity):
    """Authenticated presence in the system."""

    actor_id: ObjectId
    type: Literal[
        "user_interactive",     # Human with short-lived access + refresh
        "associate_service",    # AI associate with long-lived token
        "tier3_api",            # Developer machine-to-machine
        "cli_automation",       # Headless scripts
    ]

    auth_method_used: str       # "password", "password+totp", "sso:okta", "token"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    status: Literal["active", "expired", "revoked"] = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    access_token_jti: str       # Current JWT ID for revocation matching
    refresh_token_ref: Optional[str] = None  # Secrets Manager path (user_interactive only)

    mfa_verified: bool = False
    mfa_verified_at: Optional[datetime] = None

    claims_stale: bool = False  # Force claims refresh on next request

    platform_admin_context: Optional[dict] = None
    # {"target_org_id": ObjectId, "source_org_id": ObjectId,
    #  "work_type": "build", "duration_hours": 4, "expires_at": datetime}

    _state_machine = {
        "active": ["expired", "revoked"],
    }

    class Settings:
        name = "sessions"
        indexes = [
            [("actor_id", 1), ("status", 1)],
            [("access_token_jti", 1)],
            [("expires_at", 1)],
            [("org_id", 1), ("type", 1), ("status", 1)],
        ]
```

## A.4 Schema Migration

First-class capability per the white paper and Craig's explicit "schema migration is important" decision.

### CLI Commands

```bash
# Add field (no migration needed — Pydantic assigns defaults)
indemn entity modify Submission --add-field '{"priority": {"type": "str", "default": "normal"}}'

# Remove field (deprecate, then cleanup)
indemn entity modify Submission --deprecate-field old_field
indemn entity cleanup Submission --field old_field --dry-run
indemn entity cleanup Submission --field old_field

# Rename field (batched $rename with alias window)
indemn entity migrate Submission --rename-field named_insured primary_insured --dry-run
indemn entity migrate Submission --rename-field named_insured primary_insured
# During migration: definition accepts BOTH names (alias)
# After migration: alias removed

# Type change (batched transform)
indemn entity migrate Submission --convert-field premium --from str --to decimal --dry-run
indemn entity migrate Submission --convert-field premium --from str --to decimal
```

### Implementation

```python
# kernel/entity/migration.py

async def migrate_rename(entity_name: str, old_field: str, new_field: str,
                         dry_run: bool = False, batch_size: int = 500) -> dict:
    """Rename a field across all documents in batches."""
    entity_cls = ENTITY_REGISTRY[entity_name]
    collection = entity_cls.get_motor_collection()

    # Count affected documents
    count = await collection.count_documents({old_field: {"$exists": True}})
    if dry_run:
        return {"affected": count, "dry_run": True}

    # Phase 1: Update definition to accept both names (alias)
    defn = await EntityDefinition.find_one({"name": entity_name})
    defn.fields[new_field] = defn.fields.pop(old_field)
    # Add alias in field definition
    defn.fields[new_field].aliases = [old_field]
    await defn.save()

    # Phase 2: Batch rename
    processed = 0
    while processed < count:
        result = await collection.update_many(
            {old_field: {"$exists": True}},
            {"$rename": {old_field: new_field}},
            # MongoDB $rename is atomic per document
        )
        processed += result.modified_count
        # Record migration progress in changes collection
        await record_migration_progress(entity_name, "rename",
                                        old_field, new_field, processed, count)
        if result.modified_count == 0:
            break

    # Phase 3: Remove alias from definition
    del defn.fields[new_field].aliases
    await defn.save()

    return {"affected": processed, "complete": True}
```

All migrations are recorded in the changes collection. Rollback reads the migration record and applies the reverse operation.

## A.5 Rule Groups with Lifecycle

```python
# Extended Rule schema (additions to kernel/rule/schema.py)

class RuleGroup(Document):
    """Organizational container for related rules."""
    org_id: ObjectId
    entity_type: str
    name: str                   # "usli-classification", "stale-detection"
    description: Optional[str] = None
    status: Literal["draft", "active", "archived"] = "draft"
    owner: str                  # Actor ID who owns this group
    created_at: datetime = Field(default_factory=datetime.utcnow)

    _state_machine = {
        "draft": ["active"],
        "active": ["archived"],
        "archived": ["draft"],  # Can be restored
    }

    class Settings:
        name = "rule_groups"
        indexes = [
            [("org_id", 1), ("entity_type", 1), ("status", 1)],
        ]

# Rule.group field references a RuleGroup
# Only rules in "active" groups are evaluated
# Conflict detection at creation:
async def validate_rule_creation(rule: Rule) -> list[str]:
    """Check for conflicts with existing active rules."""
    warnings = []
    existing = await Rule.find({
        "org_id": rule.org_id,
        "entity_type": rule.entity_type,
        "capability": rule.capability,
        "status": "active",
    }).to_list()

    for existing_rule in existing:
        if conditions_overlap(rule.conditions, existing_rule.conditions):
            warnings.append(
                f"Conflicts with rule '{existing_rule.name}' — "
                f"overlapping conditions. Use --force to create anyway."
            )
    return warnings
```

## A.6 Rule Validation at Creation Time

```python
# kernel/rule/validation.py

async def validate_rule(rule: Rule, actor: Actor) -> None:
    """Validate a rule before allowing creation."""

    # 1. Check that all fields in 'sets' exist in the entity schema
    entity_def = await EntityDefinition.find_one({"name": rule.entity_type})
    if entity_def:
        for field_name in (rule.sets or {}).keys():
            if field_name not in entity_def.fields:
                raise RuleValidationError(
                    f"Field '{field_name}' does not exist on {rule.entity_type}"
                )

    # 2. State machine fields cannot be set via rules
    if entity_def and entity_def.state_machine:
        state_fields = {"status", "stage"}  # Common state field names
        for field_name in (rule.sets or {}).keys():
            if field_name in state_fields:
                raise RuleValidationError(
                    f"Cannot set '{field_name}' via rule action. "
                    f"State transitions must go through transition_to()."
                )

    # 3. Actor must have write permission for every field the rule touches
    actor_roles = await get_actor_roles(actor)
    for field_name in (rule.sets or {}).keys():
        if not has_write_permission(actor_roles, rule.entity_type, field_name):
            raise RuleValidationError(
                f"Actor lacks write permission for '{field_name}' on {rule.entity_type}"
            )
```

## A.7 Selective Emission

How `save_tracked()` determines whether to evaluate watches:

```python
# In the save_tracked() method:

# Determine if this save should emit messages
should_emit = False
emit_event_type = None

if is_new_entity:
    should_emit = True
    emit_event_type = "created"
elif is_deletion:
    should_emit = True
    emit_event_type = "deleted"
elif method is not None:
    # @exposed method was invoked — always emit
    should_emit = True
    emit_event_type = "method_invoked"
elif has_state_transition(changes):
    # State machine field changed — always emit
    should_emit = True
    emit_event_type = "transitioned"
else:
    # Regular field updates — do NOT emit
    # This is the selective emission rule:
    # "Not every field change generates messages"
    should_emit = False

if should_emit:
    await evaluate_watches_and_emit(
        entity=self,
        changes=changes,
        method=method,
        event_type=emit_event_type,
        actor_id=actor_id,
        correlation_id=correlation_id,
        session=mongo_session,
    )
```

## A.8 Cascade Depth Propagation

```python
# In evaluate_watches_and_emit():

# Depth tracking — inherited from the parent message context
parent_depth = kwargs.get("parent_depth", 0)
parent_correlation_id = kwargs.get("correlation_id") or str(uuid4())
parent_causation_id = kwargs.get("parent_message_id")

new_depth = parent_depth + 1

# Circuit breaker
MAX_CASCADE_DEPTH = 10
if new_depth > MAX_CASCADE_DEPTH:
    # Record circuit-broken message for investigation
    circuit_msg = Message(
        org_id=entity.org_id,
        entity_type=type(entity).__name__,
        entity_id=entity.id,
        event_type=event_type,
        target_role="__circuit_broken__",
        correlation_id=parent_correlation_id,
        depth=new_depth,
        status="circuit_broken",
    )
    await circuit_msg.insert(session=session)
    logger.warning(f"Cascade depth exceeded: correlation={parent_correlation_id}")
    return

# Create messages with inherited depth
for watch in matching_watches:
    message = Message(
        ...
        correlation_id=parent_correlation_id,
        causation_id=parent_causation_id,
        depth=new_depth,
        ...
    )
```

When an associate processes a message and its actions cause entity saves, the `save_tracked()` call carries forward the correlation_id and depth from the originating message via kwargs.

## A.9 First-Org Bootstrap

```python
# kernel/api/bootstrap.py

@router.post("/api/_platform/init")
async def platform_init(admin_email: str):
    """Bootstrap the very first organization.
    Called once. Creates the _platform org, first admin actor,
    and prints a one-time token to stdout."""

    # Check if platform already initialized
    existing = await Organization.find_one({"slug": "_platform"})
    if existing:
        raise HTTPException(400, "Platform already initialized")

    # Create _platform system org
    platform_org = Organization(
        name="Indemn Platform",
        slug="_platform",
        status="active",
        org_id=ObjectId(),  # Self-referencing for the platform org
    )
    platform_org.org_id = platform_org.id
    await platform_org.insert()

    # Create first admin actor
    admin = Actor(
        org_id=platform_org.id,
        name="Platform Admin",
        email=admin_email,
        type="human",
        status="provisioned",
    )
    await admin.insert()

    # Create admin role
    admin_role = Role(
        org_id=platform_org.id,
        name="platform_admin",
        permissions={"read": ["*"], "write": ["*"]},
    )
    await admin_role.insert()
    admin.role_ids.append(admin_role.id)
    await admin.save()

    # Generate one-time setup token (magic link token)
    # Printed to stdout because no email Integration exists yet
    token = generate_magic_link_token(admin)
    return {
        "status": "initialized",
        "setup_token": token,
        "message": f"Platform initialized. First admin: {admin_email}. "
                   f"Use this token to complete setup: {token}",
    }
```

After the first admin configures an email delivery Integration, subsequent invitations use email magic links.

## A.10 Seed Data Loading

```python
# kernel/seed.py
import yaml
from pathlib import Path

async def load_seed_data(seed_dir: Path = Path("seed")):
    """Load seed YAML files into the _template org."""

    template_org = await Organization.find_one({"slug": "_template"})
    if not template_org:
        template_org = Organization(
            name="Standard Template",
            slug="_template",
            status="active",
            org_id=ObjectId(),
        )
        template_org.org_id = template_org.id
        await template_org.insert()

    # Load entity definitions
    entities_dir = seed_dir / "entities"
    if entities_dir.exists():
        for yaml_file in sorted(entities_dir.glob("*.yaml")):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            # Create or update entity definition
            existing = await EntityDefinition.find_one({
                "name": data["name"], "org_id": "_system",
            })
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                await existing.save()
            else:
                defn = EntityDefinition(org_id="_system", **data)
                await defn.insert()

    # Load skills
    skills_dir = seed_dir / "skills"
    if skills_dir.exists():
        for md_file in sorted(skills_dir.glob("*.md")):
            content = md_file.read_text()
            name = md_file.stem
            # Create or update skill
            ...

    # Load roles
    roles_dir = seed_dir / "roles"
    if roles_dir.exists():
        for yaml_file in sorted(roles_dir.glob("*.yaml")):
            ...
```

Run on platform init: `indemn platform seed` or automatically on first boot.

## A.11 The @exposed Pattern

How entity methods are marked for API/CLI exposure.

```python
# kernel/entity/exposed.py
import functools

def exposed(func=None, *, requires_fresh_mfa: int = None):
    """Mark a method for auto-registration as API endpoint + CLI command.

    Decorated methods:
    - Appear as API routes: POST /api/{entity_type}/{id}/{method_name}
    - Appear as CLI commands: indemn {entity_type} {method-name} {id}
    - Appear in auto-generated skills
    - Trigger selective emission (the save after this method emits messages)

    For kernel entities only (domain entity capabilities are activated via CLI,
    not via @exposed on dynamic classes).
    """
    def decorator(fn):
        fn._exposed = True
        fn._requires_fresh_mfa = requires_fresh_mfa

        @functools.wraps(fn)
        async def wrapper(self, *args, **kwargs):
            result = await fn(self, *args, **kwargs)
            return result

        wrapper._exposed = True
        wrapper._exposed_name = fn.__name__
        wrapper._requires_fresh_mfa = requires_fresh_mfa
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
```

For domain entities (dynamic classes), capabilities serve the same purpose. When a capability is activated on an entity, it adds a method that behaves identically to an `@exposed` method on a kernel entity.

## A.12 Computed Field Evaluation

```python
# kernel/entity/computed.py

def evaluate_computed_fields(entity: BaseEntity) -> dict[str, any]:
    """Evaluate computed fields and return the values to set."""
    computed_defs = entity._computed_fields
    if not computed_defs:
        return {}

    result = {}
    entity_data = entity.dict()

    for field_name, defn in computed_defs.items():
        source_value = entity_data.get(defn.source_field)
        if source_value is not None and source_value in defn.mapping:
            result[field_name] = defn.mapping[source_value]

    return result
```

Called inside `save_tracked()` before the MongoDB write. Computed values are set on the entity in-memory, then saved.

## A.13 Pre-Transition Validation Hooks

```python
# In BaseEntity:

async def validate_transition(self, target_state: str) -> None:
    """Override in subclasses for business validation before transitions.
    Called by transition_to() after state machine validation succeeds.
    Raise TransitionValidationError to block the transition."""
    pass  # Default: no additional validation

def transition_to(self, target_state: str, reason: str = None):
    # 1. State machine validation (is this transition allowed?)
    validate_transition_allowed(self, target_state)

    # 2. Business validation (subclass-specific checks)
    # For kernel entities: override validate_transition()
    # For domain entities: validation rules are part of capability config
    self.validate_transition(target_state)

    # 3. Apply the transition
    self.status = target_state
    self._transition_metadata = {
        "from": old_state,
        "to": target_state,
        "reason": reason,
    }
```

## A.14 Optimistic Dispatch (Fire-and-Forget)

```python
# In the API layer, after a successful entity save transaction:

async def post_save_dispatch(messages: list[Message]):
    """After the MongoDB transaction commits, optimistically
    dispatch Temporal workflows for associate-eligible messages.
    Fire-and-forget — the queue processor sweep is the backstop."""
    from kernel.temporal.client import get_temporal_client

    client = await get_temporal_client()
    for message in messages:
        if await role_has_associates(message.target_role, message.org_id):
            try:
                associate = await pick_associate(message.target_role, message.org_id)
                await client.start_workflow(
                    "ProcessMessageWorkflow",
                    args=[str(message.id), str(associate.id)],
                    id=f"msg-{message.id}",
                    task_queue="indemn-kernel",
                )
            except Exception:
                pass  # Fire and forget — sweep will catch it
```

This runs AFTER the transaction commits (not inside it). If it fails for any reason, the queue processor sweep catches the undispatched message within seconds.

## A.15 Entity Type Change → Rolling Restart

```python
# When an entity definition is created or modified via the API:

@router.post("/api/entity_definitions")
async def create_entity_definition(data: dict, actor=Depends(get_current_actor)):
    defn = EntityDefinition(**data)
    await defn.insert()

    # Signal rolling restart
    await signal_restart()
    return defn.dict()

async def signal_restart():
    """Signal all kernel processes to restart.
    For Railway: use the Railway API to trigger a rolling deploy.
    For local dev: write a sentinel file that uvicorn's reload watches."""
    if settings.environment == "local":
        Path(".restart-trigger").touch()
    else:
        # Railway API call to redeploy the service
        # Or: write a record to a _restart_signals collection
        # that each process watches via Change Stream
        await db["_restart_signals"].insert_one({
            "reason": "entity_definition_changed",
            "timestamp": datetime.utcnow(),
        })
```

For MVP (single API replica), the simplest approach: the CLI that created the definition also restarts the service. For multi-replica, a Change Stream on `_restart_signals` triggers graceful restart of each instance.

## A.16 Skill Content Hash

```python
# kernel/skill/storage.py
import hashlib

def compute_content_hash(content: str) -> str:
    """SHA-256 hash of skill content for tamper detection."""
    return hashlib.sha256(content.encode()).hexdigest()

async def save_skill(name: str, content: str, actor_id: str,
                     approval_required: bool = False) -> Skill:
    content_hash = compute_content_hash(content)

    existing = await Skill.find_one({"name": name})
    if existing:
        # Create new version
        existing.content = content
        existing.content_hash = content_hash
        existing.version += 1
        if approval_required:
            existing.status = "pending_review"
        await existing.save()
        return existing
    else:
        skill = Skill(
            name=name,
            content=content,
            content_hash=content_hash,
            version=1,
            status="active" if not approval_required else "pending_review",
            created_by=actor_id,
        )
        await skill.insert()
        return skill

async def load_skill(name: str) -> str:
    """Load skill with integrity verification."""
    skill = await Skill.find_one({"name": name, "status": "active"})
    if not skill:
        raise SkillNotFoundError(f"No active skill: {name}")

    # Verify integrity
    expected_hash = compute_content_hash(skill.content)
    if expected_hash != skill.content_hash:
        raise SkillTamperError(
            f"Skill '{name}' failed integrity check. "
            f"Content was modified outside normal update path."
        )
    return skill.content
```

## A.17 Dead Letter Surfacing

```python
# CLI commands for dead letter management
@queue_app.command("dead-letter")
def dead_letter_list(org: str = None, limit: int = 20):
    """Show messages that exceeded max_attempts."""
    client = get_client()
    params = {"status": "dead_letter", "limit": limit}
    if org:
        params["org"] = org
    response = client.get("/api/messages/queue", params=params)
    output(response.json(), "table")

@queue_app.command("retry")
def retry_message(message_id: str):
    """Retry a dead-letter or failed message."""
    client = get_client()
    response = client.post(f"/api/messages/{message_id}/retry")
    output(response.json(), "json")

@queue_app.command("stats")
def queue_stats(org: str = None):
    """Show queue statistics: pending, processing, dead_letter counts per role."""
    client = get_client()
    response = client.get("/api/messages/stats", params={"org": org})
    output(response.json(), "table")
```

## A.18 Missing: `indemn entity create` CLI Command

The CLI command that creates entity definitions:

```python
@entity_app.command("create")
def create_entity_definition(
    name: str,
    fields: str = typer.Option(..., help="JSON field definitions"),
    collection_name: str = typer.Option(None, help="MongoDB collection name"),
    state_machine: str = typer.Option(None, help="JSON state machine"),
    computed_fields: str = typer.Option(None, help="JSON computed field definitions"),
):
    """Create a new domain entity type definition."""
    client = get_client()
    data = {
        "name": name,
        "collection_name": collection_name or f"{name.lower()}s",
        "fields": orjson.loads(fields),
    }
    if state_machine:
        data["state_machine"] = orjson.loads(state_machine)
    if computed_fields:
        data["computed_fields"] = orjson.loads(computed_fields)

    response = client.post("/api/entity_definitions", json=data)
    if response.status_code == 200:
        typer.echo(f"Entity type '{name}' created. API server restart required.")
        typer.echo(f"CLI commands: indemn {name.lower()} list|get|create|update|transition")
    else:
        typer.echo(f"Error: {response.json()}", err=True)
```

## A.19 Content Visibility Enforcement

```python
# When creating entities from personal Integration data:

async def create_entity_from_personal_integration(
    entity_data: dict,
    integration: Integration,
    entity_cls: type,
    actor_id: str,
):
    """Create an entity with content visibility based on
    the source Integration's content_visibility setting."""

    visibility = integration.content_visibility

    if visibility == "full_shared":
        # All content in org-scoped storage — no special handling
        entity = entity_cls(**entity_data, org_id=integration.org_id)

    elif visibility == "metadata_shared":
        # Metadata fields in entity (shared), full content in actor-scoped S3
        full_content = entity_data.pop("body", None)
        full_content_ref = None
        if full_content:
            # Upload to actor-scoped S3 path
            s3_path = f"actor/{actor_id}/content/{entity_cls.__name__}/{uuid4()}"
            await upload_to_s3(s3_path, full_content)
            full_content_ref = s3_path

        entity = entity_cls(
            **entity_data,
            org_id=integration.org_id,
            full_content_ref=full_content_ref,
        )

    elif visibility == "owner_only":
        # Everything in actor-scoped storage
        s3_path = f"actor/{actor_id}/entities/{entity_cls.__name__}/{uuid4()}"
        await upload_to_s3(s3_path, orjson.dumps(entity_data))
        # Only store a reference in the org-scoped entity
        entity = entity_cls(
            org_id=integration.org_id,
            owner_actor_id=actor_id,
            storage_ref=s3_path,
            # Minimal metadata only
        )

    await entity.save_tracked(actor_id=actor_id)
    return entity
```

---

## A.20 Updated Acceptance Tests

Adding to the 12 tests in the base spec:

```
13. SCHEMA MIGRATION
    - Add a field → existing entities get default values
    - Rename a field → batched $rename, alias during migration
    - Dry-run shows affected count without modifying data
    - Changes collection records the migration

14. RULE GROUPS WITH LIFECYCLE
    - Create a rule group in draft status
    - Add rules to the group
    - Rules in draft groups are NOT evaluated
    - Activate the group → rules now evaluate
    - Archive the group → rules stop evaluating

15. RULE VALIDATION
    - Attempt to create a rule setting a non-existent field → rejected
    - Attempt to create a rule setting a state machine field → rejected
    - Attempt to create overlapping rules → warning returned

16. FIRST-ORG BOOTSTRAP
    - indemn platform init creates _platform org and first admin
    - One-time token printed to stdout
    - Token can be used to complete setup
    - After email Integration configured, subsequent invites use email

17. COMPUTED FIELDS
    - Define entity with computed field (stage → ball_holder mapping)
    - Create instance, set stage
    - Computed field automatically populated on save

18. SELECTIVE EMISSION
    - Regular field update (no method, no transition) → no message
    - State transition → message emitted
    - @exposed method invocation → message emitted
    - Entity creation → message emitted

19. CASCADE DEPTH
    - Create watches that would cascade (A→B→C→D...)
    - Depth tracked on each message
    - At depth > 10, circuit breaker fires → circuit_broken message
    - Alert logged
```
