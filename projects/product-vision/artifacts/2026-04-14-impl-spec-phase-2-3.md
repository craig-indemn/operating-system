---
ask: "Implementation specification for Phase 2 (Associate Execution) and Phase 3 (Integration Framework)"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design source of truth"
  - type: artifact
    ref: "2026-04-09-temporal-integration-architecture.md"
    description: "Temporal integration patterns"
  - type: artifact
    ref: "2026-04-09-unified-queue-temporal-execution.md"
    description: "Unified queue, associates as employees"
  - type: artifact
    ref: "2026-04-10-integration-as-primitive.md"
    description: "Integration entity, adapter pattern, credential resolution"
  - type: artifact
    ref: "2026-04-09-entity-capabilities-and-skill-model.md"
    description: "Kernel capabilities, --auto pattern, skill model"
  - type: artifact
    ref: "2026-04-10-bulk-operations-pattern.md"
    description: "Bulk operations via Temporal"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1.md"
    description: "Phase 0+1 spec (this builds on it)"
---

# Implementation Specification: Phase 2 + Phase 3

## Relationship to Phase 1

Phase 1 delivers the kernel framework: entity definitions, dynamic classes, kernel entities, watches, messages, rules, auth, CLI/API. Phase 2 adds the ability for AI actors to process work from the queue via Temporal. Phase 3 adds the ability to connect to external systems via the Integration kernel entity and adapters.

Together, Phases 1-3 produce a system where: entities are defined, changes generate messages via watches, associates claim messages and process them via durable workflows, and entity operations can reach external systems through adapters. This is the complete kernel loop.

---

# Phase 2: Associate Execution

## What It Produces

AI actors (associates) can claim messages from the queue, process them by executing CLI commands (via the `--auto` pattern or LLM reasoning), and produce entity state changes that propagate through watches.

## 2.1 Temporal Integration

### Connection

```python
# kernel/temporal/client.py
from temporalio.client import Client

async def get_temporal_client() -> Client:
    return await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
        api_key=settings.temporal_api_key,
    )
```

### The Generic Workflow

One workflow definition handles ALL associate message processing. The skill is the source of truth for orchestration — the workflow is a durability wrapper.

```python
# kernel/temporal/workflows.py
from temporalio import workflow
from datetime import timedelta

with workflow.unsafe.imports_passed_through():
    from kernel.temporal.activities import (
        claim_message, load_entity_context,
        process_with_associate, complete_message,
        fail_message,
    )

@workflow.defn
class ProcessMessageWorkflow:
    """Generic claim → process → complete workflow.
    Used by all associates regardless of role or skill."""

    @workflow.run
    async def run(self, message_id: str, associate_id: str) -> dict:
        # 1. Claim the message from the queue
        claimed = await workflow.execute_activity(
            claim_message,
            args=[message_id, associate_id],
            start_to_close_timeout=timedelta(seconds=30),
        )
        if not claimed:
            return {"status": "already_claimed"}

        # 2. Load entity context (fresh from MongoDB)
        context = await workflow.execute_activity(
            load_entity_context,
            args=[message_id],
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 3. Process (the associate does its work)
        try:
            result = await workflow.execute_activity(
                process_with_associate,
                args=[message_id, associate_id, context],
                start_to_close_timeout=timedelta(minutes=10),
                heartbeat_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5),
                    backoff_coefficient=2.0,
                    non_retryable_error_types=["PermanentError"],
                ),
            )
        except Exception as e:
            await workflow.execute_activity(
                fail_message,
                args=[message_id, str(e)],
                start_to_close_timeout=timedelta(seconds=30),
            )
            raise

        # 4. Complete the message (move from queue to log)
        await workflow.execute_activity(
            complete_message,
            args=[message_id, result],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return result
```

### Activities

```python
# kernel/temporal/activities.py
from temporalio import activity

@activity.defn
async def claim_message(message_id: str, associate_id: str) -> bool:
    """Atomic claim via findOneAndUpdate.
    Returns False if already claimed by someone else."""
    result = await message_queue_collection.find_one_and_update(
        {
            "_id": ObjectId(message_id),
            "$or": [
                {"status": "pending"},
                {"status": "processing",
                 "visibility_timeout": {"$lt": datetime.utcnow()}},
            ],
        },
        {
            "$set": {
                "status": "processing",
                "claimed_by": ObjectId(associate_id),
                "claimed_at": datetime.utcnow(),
                "visibility_timeout": datetime.utcnow() + timedelta(minutes=5),
            },
            "$inc": {"attempt_count": 1},
        },
        return_document=True,
    )
    return result is not None

@activity.defn
async def load_entity_context(message_id: str) -> dict:
    """Load the entity referenced by the message. Fresh from MongoDB."""
    message = await Message.get(message_id)
    entity_cls = ENTITY_REGISTRY[message.entity_type]
    entity = await entity_cls.get(message.entity_id)
    return {
        "message": message.dict(),
        "entity": entity.dict() if entity else None,
    }

@activity.defn
async def process_with_associate(
    message_id: str, associate_id: str, context: dict
) -> dict:
    """The associate processes the message.
    For Phase 2 MVP: execute the associate's skill via CLI subprocess.
    The skill determines what CLI commands to run."""
    associate = await Actor.get(associate_id)

    # Load the associate's skills from MongoDB
    skills_content = await load_skills(associate.skills)

    # Determine execution mode
    if associate.mode == "deterministic":
        result = await execute_deterministic(skills_content, context)
    elif associate.mode == "reasoning":
        result = await execute_with_llm(associate, skills_content, context)
    else:  # hybrid
        result = await execute_hybrid(associate, skills_content, context)

    return result

@activity.defn
async def complete_message(message_id: str, result: dict) -> None:
    """Move message from queue to log. Mark complete."""
    message = await Message.get(message_id)
    # Insert into message_log
    log_entry = MessageLog(**message.dict(), result=result,
                           completed_at=datetime.utcnow())
    await log_entry.insert()
    # Delete from queue
    await message.delete()

@activity.defn
async def fail_message(message_id: str, error: str) -> None:
    """Handle message failure. Return to queue or dead-letter."""
    message = await Message.get(message_id)
    if message.attempt_count >= message.max_attempts:
        message.status = "dead_letter"
    else:
        message.status = "pending"
        message.claimed_by = None
        message.visibility_timeout = None
    message.last_error = error
    await message.save()
```

### Temporal Worker

```python
# kernel/temporal/worker.py
from temporalio.client import Client
from temporalio.worker import Worker
from kernel.temporal.workflows import ProcessMessageWorkflow, BulkExecuteWorkflow
from kernel.temporal.activities import (
    claim_message, load_entity_context,
    process_with_associate, complete_message, fail_message,
)

async def main():
    await init_database()
    client = await get_temporal_client()

    worker = Worker(
        client,
        task_queue="indemn-kernel",
        workflows=[ProcessMessageWorkflow, BulkExecuteWorkflow],
        activities=[
            claim_message, load_entity_context,
            process_with_associate, complete_message, fail_message,
        ],
    )
    await worker.run()
```

## 2.2 Skill Loading

Associates load their skills from MongoDB at invocation time.

```python
async def load_skills(skill_names: list[str]) -> str:
    """Load and concatenate skill content from MongoDB."""
    skills = []
    for name in skill_names:
        skill = await Skill.find_one({"name": name, "status": "active"})
        if skill:
            # Verify content hash (tamper detection)
            if not verify_content_hash(skill.content, skill.content_hash):
                raise SkillTamperError(f"Skill {name} failed integrity check")
            skills.append(skill.content)
    return "\n\n---\n\n".join(skills)
```

Two types of skills compose naturally:
- **Entity skills** (auto-generated) — what CLI commands exist for each entity type
- **Associate skills** (human-authored) — behavioral instructions for how to process work

An associate's skill list typically includes both: entity skills for what operations are available, plus associate skills for when and how to use them.

## 2.3 Associate Execution Modes

### Deterministic

Parse the skill as a structured sequence of CLI commands with conditions. Execute without LLM.

```python
async def execute_deterministic(skills: str, context: dict) -> dict:
    """Execute a structured skill deterministically.
    No LLM involved. Parse the skill for CLI commands and conditions."""
    # For Phase 2 MVP, deterministic execution is:
    # 1. Parse the skill for `indemn` CLI commands
    # 2. Execute each via the API (not subprocess — direct API calls)
    # 3. Evaluate simple conditions (if/then)
    # This is a simple interpreter, not a full DSL engine.
    ...
```

### Reasoning (LLM)

Invoke the LLM with the skill content and entity context. The LLM decides which CLI commands to execute.

```python
async def execute_with_llm(associate: Actor, skills: str, context: dict) -> dict:
    """Execute a skill using LLM reasoning.
    The LLM reads the skill, analyzes the context, and decides
    which CLI commands to run."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic()
    messages = [
        {"role": "system", "content": f"You are an associate executing the following skill:\n\n{skills}"},
        {"role": "user", "content": f"Process this work item:\n\n{orjson.dumps(context).decode()}"},
    ]

    # LLM generates CLI commands as tool calls
    # Each tool call is executed via the API
    # Results feed back to the LLM for next steps
    # Continue until the LLM indicates completion
    ...
```

### Hybrid

Try deterministic path first. If any step returns `needs_reasoning`, fall back to LLM for that step.

```python
async def execute_hybrid(associate: Actor, skills: str, context: dict) -> dict:
    """Try deterministic first. Fall back to LLM when needed."""
    result = await execute_deterministic(skills, context)
    if result.get("needs_reasoning"):
        return await execute_with_llm(associate, skills, context)
    return result
```

## 2.4 The `--auto` Pattern End-to-End

The complete flow from message to processed entity:

```
1. Entity saves → watch matches → message in queue
2. Queue Processor dispatches Temporal workflow
3. Workflow Activity 1: claim message from queue
4. Workflow Activity 2: load entity (fresh from MongoDB)
5. Workflow Activity 3: process
   a. Load associate's skills
   b. Skill says: "indemn email classify {id} --auto"
   c. Execute via API: POST /api/emails/{id}/classify?auto=true
   d. API invokes auto_classify capability
   e. Capability evaluates rules → returns result or needs_reasoning
   f. If needs_reasoning: LLM analyzes and provides classification
   g. Classification saved on entity → triggers save_tracked()
   h. save_tracked() records changes, evaluates watches, creates new messages
6. Workflow Activity 4: complete message (move to log)
7. New messages from step 5h start new workflows → system churns
```

## 2.5 Scheduled Task Execution

Schedules create messages in the queue — same path as watch-triggered work.

```python
# In queue_processor.py — the schedule sweep
async def check_schedules():
    """Check for scheduled associates whose cron has fired."""
    associates = await Actor.find({
        "type": "associate",
        "status": "active",
        "trigger_schedule": {"$exists": True},
    }).to_list()

    for associate in associates:
        if cron_should_fire(associate.trigger_schedule):
            # Create a scheduled message in the queue
            message = Message(
                org_id=associate.org_id,
                entity_type="_scheduled",
                entity_id=associate.id,
                event_type="schedule_fired",
                target_role=associate.role_ids[0],  # Associate's role
                correlation_id=str(uuid4()),
                status="pending",
            )
            await message.insert()
```

## 2.6 Direct Invocation for Real-Time

Create queue entry for visibility AND invoke associate directly for latency.

```python
# API endpoint for direct invocation
@router.post("/api/associates/{associate_id}/invoke")
async def invoke_associate(associate_id: str, context: dict):
    """Direct invocation — used for real-time channels.
    Creates queue entry (visibility) + starts workflow immediately."""
    # Create message in queue (for visibility and audit)
    message = Message(...)
    await message.insert()

    # Start workflow immediately (don't wait for queue processor)
    client = await get_temporal_client()
    await client.start_workflow(
        ProcessMessageWorkflow.run,
        args=[str(message.id), associate_id],
        id=f"direct-{message.id}",
        task_queue="indemn-kernel",
    )
    return {"message_id": str(message.id), "status": "invoked"}
```

## 2.7 Bulk Operations via Temporal

The `bulk_execute` workflow from the bulk operations design.

```python
@workflow.defn
class BulkExecuteWorkflow:
    """Generic bulk operation workflow.
    Iterates a source, applies an operation per entity in batches."""

    @workflow.run
    async def run(self, spec: BulkOperationSpec) -> BulkResult:
        processed = 0
        errors = []

        # Process in batches
        while True:
            batch_result = await workflow.execute_activity(
                process_bulk_batch,
                args=[spec, processed],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            processed += batch_result["processed"]
            errors.extend(batch_result.get("errors", []))

            if batch_result["done"]:
                break

        status = "completed" if not errors else "completed_with_errors"
        return BulkResult(status=status, processed=processed, errors=errors)
```

## 2.8 Queue Processor Dispatch

The queue processor now dispatches Temporal workflows for associate-eligible messages.

```python
# Updated queue_processor.py sweep
async def dispatch_associate_workflows():
    """Find pending messages for roles with associates.
    Start Temporal workflows for them."""
    # Find pending messages beyond dispatch threshold
    threshold = datetime.utcnow() - timedelta(seconds=10)
    messages = await Message.find({
        "status": "pending",
        "created_at": {"$lt": threshold},
    }).to_list()

    for message in messages:
        # Check if this role has associate actors
        role = await Role.find_one({"name": message.target_role, "org_id": message.org_id})
        associates = await Actor.find({
            "type": "associate",
            "role_ids": role.id,
            "status": "active",
        }).to_list()

        if associates:
            # Pick an associate (round-robin or first available)
            associate = associates[0]
            client = await get_temporal_client()
            try:
                await client.start_workflow(
                    ProcessMessageWorkflow.run,
                    args=[str(message.id), str(associate.id)],
                    id=f"msg-{message.id}",
                    task_queue="indemn-kernel",
                )
            except WorkflowAlreadyStartedError:
                pass  # Already dispatched — optimistic dispatch got it
```

## Phase 2 Acceptance Criteria

```
1. ASSOCIATE CLAIMS AND PROCESSES MESSAGE
   - Create a role with watches
   - Create an associate with that role and a skill
   - Create an entity matching the watch
   - Message appears in queue
   - Temporal workflow starts, claims the message
   - Associate processes it (executes CLI commands per skill)
   - Entity state changes
   - Message moves to message_log
   - New messages generated from entity changes (system churns)

2. THE --auto PATTERN END-TO-END
   - Create rules for an entity type
   - Associate invokes capability with --auto
   - Rules match → deterministic result applied (no LLM)
   - Rules don't match → needs_reasoning returned
   - Associate's LLM provides fallback classification

3. SCHEDULED ASSOCIATE
   - Create an associate with schedule trigger
   - Schedule fires → message in queue
   - Temporal workflow processes it
   - Same path as watch-triggered work

4. DIRECT INVOCATION
   - Invoke an associate directly via API
   - Queue entry created for visibility
   - Workflow runs immediately (doesn't wait for queue processor)

5. FAILURE HANDLING
   - Associate crashes mid-processing
   - Visibility timeout expires
   - Message becomes claimable again
   - After max_attempts → dead_letter status

6. BULK OPERATION
   - Invoke a bulk operation via CLI
   - BulkExecuteWorkflow processes entities in batches
   - Per-entity events emitted
   - Progress queryable via workflow ID

7. GRADUAL ROLLOUT
   - Both human and associate on same role
   - Both see same queue items
   - Associate claims first (faster)
   - Human can still claim unclaimed items
   - Remove human from role → associate handles everything
```

---

# Phase 3: Integration Framework

## What It Produces

The ability to connect the OS to external systems through the Integration kernel entity and adapter pattern. At least two working adapters proving both outbound and inbound patterns.

## 3.1 Adapter Interface

Abstract base class that all provider adapters implement.

```python
# kernel/integration/adapter.py
from abc import ABC, abstractmethod
from typing import Optional
from decimal import Decimal

class Adapter(ABC):
    """Base adapter interface. Provider-specific adapters inherit this."""

    def __init__(self, config: dict, credentials: dict):
        self.config = config
        self.credentials = credentials

    # Outbound operations (override as needed)
    async def fetch(self, **params) -> list[dict]:
        raise NotImplementedError

    async def send(self, payload: dict) -> dict:
        raise NotImplementedError

    async def charge(self, amount: Decimal, currency: str, **params) -> dict:
        raise NotImplementedError

    # Inbound operations (override as needed)
    async def validate_webhook(self, headers: dict, body: bytes) -> bool:
        raise NotImplementedError

    async def parse_webhook(self, body: dict) -> dict:
        """Returns: {entity_type, lookup_by, lookup_value, operation, params}"""
        raise NotImplementedError

    # Auth operations
    async def auth_initiate(self, redirect_uri: str) -> str:
        raise NotImplementedError

    async def auth_callback(self, code: str, state: str) -> dict:
        raise NotImplementedError
```

## 3.2 Adapter Registry

```python
# kernel/integration/registry.py

ADAPTER_REGISTRY: dict[str, type[Adapter]] = {}

def register_adapter(provider: str, version: str, adapter_cls: type[Adapter]):
    key = f"{provider}:{version}"
    ADAPTER_REGISTRY[key] = adapter_cls

def get_adapter_class(provider: str, version: str) -> type[Adapter]:
    key = f"{provider}:{version}"
    cls = ADAPTER_REGISTRY.get(key)
    if not cls:
        raise AdapterNotFoundError(f"No adapter for {key}")
    return cls
```

## 3.3 Credential Resolution

The priority chain from the white paper: actor-level first, org-level fallback.

```python
# kernel/integration/resolver.py

async def resolve_integration(
    actor_id: ObjectId,
    org_id: ObjectId,
    system_type: str,
    require_org_only: bool = False,
) -> Integration:
    """Resolve the Integration to use for an external operation."""

    # Step 1: Actor-level (personal integration)
    if not require_org_only:
        personal = await Integration.find_one({
            "owner_type": "actor",
            "owner_id": actor_id,
            "system_type": system_type,
            "status": "active",
            "org_id": org_id,
        })
        if personal:
            return personal

    # Step 2: Check owner's integrations (if associate has owner_actor_id)
    actor = await Actor.get(actor_id)
    if actor.owner_actor_id and not require_org_only:
        owner_personal = await Integration.find_one({
            "owner_type": "actor",
            "owner_id": actor.owner_actor_id,
            "system_type": system_type,
            "status": "active",
            "org_id": org_id,
        })
        if owner_personal:
            return owner_personal

    # Step 3: Org-level with role-based access
    actor_role_ids = actor.role_ids
    roles = await Role.find({"_id": {"$in": actor_role_ids}}).to_list()
    role_names = [r.name for r in roles]

    org_integration = await Integration.find_one({
        "owner_type": "org",
        "owner_id": org_id,
        "system_type": system_type,
        "status": "active",
        "org_id": org_id,
        "access.roles": {"$in": role_names},
    })
    if org_integration:
        return org_integration

    raise NoIntegrationFoundError(
        f"No {system_type} integration available for actor {actor_id}"
    )
```

## 3.4 Credential Fetching

```python
# kernel/integration/credentials.py
import boto3

_secrets_client = None
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 300  # 5 minutes

async def fetch_credentials(secret_ref: str) -> dict:
    """Fetch credentials from AWS Secrets Manager with caching."""
    now = time.time()
    if secret_ref in _cache:
        creds, cached_at = _cache[secret_ref]
        if now - cached_at < CACHE_TTL:
            return creds

    client = get_secrets_client()
    response = client.get_secret_value(SecretId=secret_ref)
    creds = orjson.loads(response["SecretString"])
    _cache[secret_ref] = (creds, now)
    return creds
```

## 3.5 Adapter Dispatch

When an entity operation needs external connectivity:

```python
# kernel/integration/dispatch.py

async def get_adapter(
    actor_id: ObjectId,
    org_id: ObjectId,
    system_type: str,
    **kwargs,
) -> Adapter:
    """Resolve integration, fetch credentials, instantiate adapter."""
    integration = await resolve_integration(actor_id, org_id, system_type, **kwargs)
    credentials = await fetch_credentials(integration.secret_ref)
    adapter_cls = get_adapter_class(integration.provider, integration.provider_version)
    return adapter_cls(config=integration.config, credentials=credentials)
```

## 3.6 Webhook Endpoint

Generic handler that dispatches to the Integration's adapter.

```python
# kernel/api/webhook.py
from fastapi import APIRouter, Request, HTTPException

webhook_router = APIRouter()

@webhook_router.post("/webhook/{provider}/{integration_id}")
async def handle_webhook(provider: str, integration_id: str, request: Request):
    """Generic webhook handler. Validates via adapter, applies entity operations."""
    # Load integration
    integration = await Integration.get(integration_id)
    if not integration or integration.provider != provider:
        raise HTTPException(404)
    if integration.status != "active":
        raise HTTPException(400, "Integration is not active")

    # Get adapter
    credentials = await fetch_credentials(integration.secret_ref)
    adapter_cls = get_adapter_class(integration.provider, integration.provider_version)
    adapter = adapter_cls(config=integration.config, credentials=credentials)

    # Validate
    body = await request.body()
    headers = dict(request.headers)
    if not await adapter.validate_webhook(headers, body):
        raise HTTPException(401, "Invalid webhook signature")

    # Parse
    parsed = await adapter.parse_webhook(orjson.loads(body))

    # Apply entity operations via entity methods (state machine enforcement)
    entity_cls = ENTITY_REGISTRY[parsed["entity_type"]]
    entity = await entity_cls.find_one({
        parsed["lookup_by"]: parsed["lookup_value"],
        "org_id": integration.org_id,
    })
    if not entity:
        raise HTTPException(404, f"Entity not found: {parsed['lookup_by']}={parsed['lookup_value']}")

    if parsed["operation"] == "transition":
        entity.transition_to(parsed["params"]["to_status"])
        await entity.save_tracked(
            actor_id=f"webhook:{integration.provider}",
            method=f"webhook_{parsed['operation']}",
        )
    elif parsed["operation"] == "update":
        for field, value in parsed["params"].items():
            setattr(entity, field, value)
        await entity.save_tracked(
            actor_id=f"webhook:{integration.provider}",
            method=f"webhook_{parsed['operation']}",
        )

    return {"status": "ok"}
```

## 3.7 First Two Adapters

### Email Adapter (Outlook — outbound fetch + send)

```python
# kernel/integration/adapters/outlook.py
import httpx
from kernel.integration.adapter import Adapter

class OutlookAdapter(Adapter):
    """Microsoft Graph API adapter for Outlook email."""

    async def fetch(self, since: str = None, folder: str = "inbox", **params) -> list[dict]:
        """Fetch emails from Outlook inbox."""
        headers = {"Authorization": f"Bearer {self.credentials['access_token']}"}
        url = f"https://graph.microsoft.com/v1.0/me/mailFolders/{folder}/messages"
        params = {"$top": 50, "$orderby": "receivedDateTime desc"}
        if since:
            params["$filter"] = f"receivedDateTime ge {since}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            messages = response.json()["value"]

        # Map to OS entity format
        return [self._map_to_os(msg) for msg in messages]

    async def send(self, payload: dict) -> dict:
        """Send an email via Outlook."""
        headers = {"Authorization": f"Bearer {self.credentials['access_token']}"}
        url = "https://graph.microsoft.com/v1.0/me/sendMail"
        body = {"message": self._map_from_os(payload)}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
        return {"status": "sent"}

    def _map_to_os(self, outlook_msg: dict) -> dict:
        return {
            "external_id": outlook_msg["id"],
            "from_address": outlook_msg["from"]["emailAddress"]["address"],
            "to_addresses": [r["emailAddress"]["address"] for r in outlook_msg["toRecipients"]],
            "subject": outlook_msg["subject"],
            "body": outlook_msg["body"]["content"],
            "received_at": outlook_msg["receivedDateTime"],
            "thread_id": outlook_msg.get("conversationId"),
            "has_attachments": outlook_msg.get("hasAttachments", False),
        }

    def _map_from_os(self, email_data: dict) -> dict:
        return {
            "toRecipients": [{"emailAddress": {"address": to}} for to in email_data["to_addresses"]],
            "subject": email_data["subject"],
            "body": {"contentType": "HTML", "content": email_data["body"]},
        }

register_adapter("outlook", "v2", OutlookAdapter)
```

### Payment Adapter (Stripe — outbound charge + inbound webhook)

```python
# kernel/integration/adapters/stripe.py
import stripe
import hmac, hashlib
from kernel.integration.adapter import Adapter

class StripeAdapter(Adapter):
    """Stripe payment adapter."""

    def __init__(self, config, credentials):
        super().__init__(config, credentials)
        stripe.api_key = credentials["secret_key"]

    async def charge(self, amount: Decimal, currency: str = "usd", **params) -> dict:
        """Create a Stripe PaymentIntent."""
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe uses cents
            currency=currency,
            metadata=params.get("metadata", {}),
        )
        return {
            "payment_intent_id": intent.id,
            "client_secret": intent.client_secret,
            "status": intent.status,
        }

    async def validate_webhook(self, headers: dict, body: bytes) -> bool:
        """Validate Stripe webhook signature."""
        sig = headers.get("stripe-signature", "")
        try:
            stripe.Webhook.construct_event(
                body, sig, self.credentials["webhook_secret"],
            )
            return True
        except stripe.error.SignatureVerificationError:
            return False

    async def parse_webhook(self, body: dict) -> dict:
        """Parse Stripe webhook into entity operations."""
        event_type = body["type"]
        if event_type == "payment_intent.succeeded":
            pi = body["data"]["object"]
            return {
                "entity_type": "Payment",
                "lookup_by": "stripe_payment_intent_id",
                "lookup_value": pi["id"],
                "operation": "transition",
                "params": {
                    "to_status": "completed",
                    "charged_at": datetime.utcnow().isoformat(),
                },
            }
        elif event_type == "payment_intent.payment_failed":
            pi = body["data"]["object"]
            return {
                "entity_type": "Payment",
                "lookup_by": "stripe_payment_intent_id",
                "lookup_value": pi["id"],
                "operation": "transition",
                "params": {"to_status": "failed"},
            }
        raise ValueError(f"Unhandled Stripe event: {event_type}")

register_adapter("stripe", "v1", StripeAdapter)
```

## 3.8 Integration CLI Commands

Auto-generated from the Integration kernel entity, plus manual commands for credential management:

```bash
# Auto-generated CRUD
indemn integration list [--system-type email] [--status active]
indemn integration get INT-001
indemn integration create --name "..." --system-type email --provider outlook --owner org

# Manual commands for credential operations
indemn integration set-credentials INT-001 --from-file @creds.json
# → Writes to AWS Secrets Manager, stores ref on Integration

indemn integration rotate-credentials INT-001
# → Provider-specific rotation

indemn integration test INT-001
# → Calls adapter.fetch() or adapter.validate_webhook() to verify connectivity
```

## Phase 3 Acceptance Criteria

```
1. INTEGRATION CREATED AND CONNECTED
   - Create an Integration via CLI
   - Set credentials (stored in Secrets Manager, not MongoDB)
   - Test connectivity → success

2. OUTBOUND OPERATION
   - Entity method invokes an external system via adapter
   - Credential resolution follows the priority chain
   - Adapter maps between OS format and provider format
   - Operation succeeds, entity state updated

3. INBOUND WEBHOOK
   - External system sends webhook to /webhook/{provider}/{integration_id}
   - Adapter validates signature
   - Adapter parses payload into entity operations
   - Entity state updated via entity methods (state machine enforced)
   - Watch fires → downstream processing

4. CREDENTIAL RESOLUTION PRIORITY
   - Actor-level integration takes precedence over org-level
   - Owner's integration checked for owner-bound associates
   - Org-level with role-based access as fallback
   - Clear error when no integration found

5. CREDENTIAL ROTATION
   - Rotate credentials via CLI
   - Existing connections continue working
   - New connections use new credentials

6. TWO ADAPTERS WORKING
   - Outlook adapter: fetch emails, send emails
   - Stripe adapter: create payment intent, validate/parse webhook
   - Both prove the adapter interface is sufficient
```

## 3.9 Open Questions

1. **OAuth refresh token management.** Outlook and Gmail use OAuth with refresh tokens. The Secrets Manager stores the refresh token. The adapter must handle token refresh transparently (detect 401, refresh, retry). This is provider-specific logic in each OAuth-based adapter.

2. **Adapter error standardization.** Adapters should raise standardized exceptions (AdapterAuthError, AdapterRateLimitError, AdapterNotFoundError) that the kernel can handle uniformly (retry on rate limit, refresh on auth error, fail on not found).

3. **Integration health monitoring.** The Integration entity has `last_checked_at` and `last_error` fields. A background process (or the queue processor) should periodically test integrations and update these fields. Implementation details deferred to building.
