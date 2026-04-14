---
ask: "Consolidated implementation specification for Phase 2 (Associate Execution) and Phase 3 (Integration Framework) — resolving all applicable gaps"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design-level source of truth"
  - type: artifact
    ref: "2026-04-14-impl-spec-gaps.md"
    description: "Gap identification — this spec resolves G-19 through G-31, G-60, G-61, G-64, G-73, G-76, G-77, G-78, G-80, G-81, G-90"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1-consolidated.md"
    description: "Phase 0+1 consolidated spec (this builds on it)"
  - type: artifact
    ref: "2026-04-09-temporal-integration-architecture.md"
    description: "Temporal integration patterns, GIC on Temporal"
  - type: artifact
    ref: "2026-04-09-unified-queue-temporal-execution.md"
    description: "Unified queue, associates as employees"
  - type: artifact
    ref: "2026-04-10-integration-as-primitive.md"
    description: "Integration entity, adapter pattern, credential resolution"
  - type: artifact
    ref: "2026-04-10-bulk-operations-pattern.md"
    description: "Bulk operations workflow, CLI verbs, failure handling"
  - type: artifact
    ref: "2026-04-13-documentation-sweep.md"
    description: "Inbound webhook dispatch, adapter interface"
  - type: verification
    description: "This document supersedes 2026-04-14-impl-spec-phase-2-3.md"
---

# Implementation Specification: Phase 2 + Phase 3 (Consolidated)

**This document supersedes `2026-04-14-impl-spec-phase-2-3.md`.**

## Relationship to Phase 1

Phase 1 delivers: entity definitions in MongoDB, dynamic classes, seven kernel entities, watches, messages, rules, the condition evaluator, auth, CLI/API auto-generation, skills, OTEL. Phase 2 adds durable associate execution via Temporal. Phase 3 adds external system connectivity via the Integration kernel entity and adapters.

Together, Phases 1-3 complete the kernel loop: entities defined → changes generate messages via watches → associates claim and process via durable workflows → entity operations reach external systems through adapters → changes propagate → system churns.

## What Is NOT in Phase 2+3 (Explicitly Deferred)

- Base UI (Phase 4)
- Full authentication (SSO, MFA, platform admin — Phase 4)
- Real-time channels, harness pattern, Attention activation, Runtime deployment (Phase 5)
- Saga-style cross-batch rollback (post-MVP)
- `bulk_apply` DSL for multi-entity rows (post-MVP)
- Per-adapter rate limiting infrastructure (post-MVP — adapters handle their own rate limits for now)

---

# Phase 2: Associate Execution

## 2.1 Temporal Connection and Worker Setup [G-19, G-23]

```python
# kernel/temporal/client.py
from temporalio.client import Client
from kernel.config import settings

_client: Client = None

async def get_temporal_client() -> Client:
    global _client
    if _client is None:
        connect_kwargs = {
            "target_host": settings.temporal_address,
            "namespace": settings.temporal_namespace,
        }
        if settings.temporal_api_key:
            connect_kwargs["api_key"] = settings.temporal_api_key
            connect_kwargs["tls"] = True  # Temporal Cloud requires TLS
        _client = await Client.connect(**connect_kwargs)
    return _client
```

```python
# kernel/temporal/worker.py
"""
Entry point: python -m kernel.temporal.worker
Executes associate workflows and kernel workflows.
"""
import asyncio
from temporalio.worker import Worker
from temporalio.contrib.opentelemetry import TracingInterceptor  # [G-19]
from kernel.temporal.client import get_temporal_client
from kernel.temporal.workflows import ProcessMessageWorkflow, HumanReviewWorkflow, BulkExecuteWorkflow
from kernel.temporal.activities import (
    claim_message, load_entity_context, process_with_associate,
    complete_message, fail_message, process_bulk_batch,
)
from kernel.db import init_database
from kernel.observability.tracing import init_tracing
from kernel.config import settings

async def main():
    init_tracing()
    await init_database()
    client = await get_temporal_client()

    # [G-19] OTEL TracingInterceptor on every workflow + activity
    interceptors = [TracingInterceptor()]

    worker = Worker(
        client,
        task_queue="indemn-kernel",
        workflows=[
            ProcessMessageWorkflow,
            HumanReviewWorkflow,
            BulkExecuteWorkflow,
        ],
        activities=[
            claim_message,
            load_entity_context,
            process_with_associate,
            complete_message,
            fail_message,
            process_bulk_batch,
        ],
        interceptors=interceptors,
        # [G-23] Production configuration
        max_concurrent_activities=20,      # Prevent MongoDB overload
        max_concurrent_workflow_tasks=10,
        graceful_shutdown_timeout=30,      # Seconds to finish in-flight work
    )

    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## 2.2 The Generic ProcessMessageWorkflow [G-22, G-90]

One workflow handles ALL associate message processing. The skill is the source of truth for orchestration. Temporal wraps the generic claim → process → complete cycle for durability.

```python
# kernel/temporal/workflows.py
from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta

with workflow.unsafe.imports_passed_through():
    from kernel.temporal.activities import (
        claim_message, load_entity_context, process_with_associate,
        complete_message, fail_message,
    )

@workflow.defn
class ProcessMessageWorkflow:
    """Generic claim → process → complete.
    Used by all associates regardless of role or skill.
    The skill is the source of truth — this workflow is a durability wrapper."""

    @workflow.run
    async def run(self, message_id: str, associate_id: str) -> dict:

        # Activity 1: Claim the message from the queue
        # Fast retry, low attempts — if claim fails, someone else got it
        claimed = await workflow.execute_activity(
            claim_message,
            args=[message_id, associate_id],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(  # [G-90]
                maximum_attempts=2,
                initial_interval=timedelta(seconds=1),
            ),
        )
        if not claimed:
            return {"status": "already_claimed"}

        # Activity 2: Load entity context (fresh from MongoDB)
        # Fast retry — simple DB read
        context = await workflow.execute_activity(
            load_entity_context,
            args=[message_id],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=2),
            ),
        )

        # Activity 3: Process (the associate does its work)
        # Longer timeout, more retries, heartbeat for long-running LLM calls
        # Non-retryable errors: PermanentProcessingError (bad skill, bad data)
        try:
            result = await workflow.execute_activity(
                process_with_associate,
                args=[message_id, associate_id, context],
                start_to_close_timeout=timedelta(minutes=10),
                heartbeat_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(  # [G-90]
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5),
                    backoff_coefficient=2.0,
                    maximum_interval=timedelta(seconds=60),
                    non_retryable_error_types=[
                        "PermanentProcessingError",
                        "SkillTamperError",
                        "PermissionError",
                    ],
                ),
            )
        except Exception as e:
            # Activity 4a: Fail the message (return to queue or dead-letter)
            await workflow.execute_activity(
                fail_message,
                args=[message_id, str(e)],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            raise

        # Activity 4b: Complete the message (move from queue to log)
        await workflow.execute_activity(
            complete_message,
            args=[message_id, result],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        return result
```

## 2.3 Human-in-the-Loop Workflow via Temporal Signals [G-20]

When a human needs to make a decision (approve a draft, review an assessment, reassign a submission), a separate workflow type waits for a signal.

```python
@workflow.defn
class HumanReviewWorkflow:
    """Workflow that waits for a human decision.
    Used for watches targeting human roles where the work requires
    a deliberate decision (approve/reject/escalate), not just processing."""

    def __init__(self):
        self._decision: dict = None

    @workflow.signal
    async def submit_decision(self, decision: dict):
        """Signal handler — called when human makes their decision via UI/CLI.
        Decision format: {"action": "approve"|"reject"|"escalate", "reason": "...", "data": {...}}"""
        self._decision = decision

    @workflow.run
    async def run(self, message_id: str, escalation_hours: int = 48) -> dict:

        # Claim the message
        claimed = await workflow.execute_activity(
            claim_message,
            args=[message_id, "__human_review__"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        if not claimed:
            return {"status": "already_claimed"}

        # Wait for human decision OR escalation timeout
        # The human sees this in their queue via the base UI
        # They click Approve/Reject → UI signals this workflow
        try:
            await workflow.wait_condition(
                lambda: self._decision is not None,
                timeout=timedelta(hours=escalation_hours),
            )
        except asyncio.TimeoutError:
            # Escalation — no decision within the timeout
            await workflow.execute_activity(
                fail_message,
                args=[message_id, f"No decision within {escalation_hours} hours — escalated"],
                start_to_close_timeout=timedelta(seconds=30),
            )
            return {"status": "escalated", "reason": "timeout"}

        # Human made a decision — process it
        result = await workflow.execute_activity(
            process_human_decision,
            args=[message_id, self._decision],
            start_to_close_timeout=timedelta(minutes=5),
        )

        await workflow.execute_activity(
            complete_message,
            args=[message_id, result],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return result
```

The UI signals the workflow when the human acts:

```python
# In the API layer (Phase 4 activates the UI, but the API endpoint exists from Phase 2):
@router.post("/api/messages/{message_id}/decide")
async def submit_decision(message_id: str, decision: dict, actor=Depends(get_current_actor)):
    """Human submits a decision on a pending review message.
    Signals the HumanReviewWorkflow."""
    message = await Message.get(message_id)
    if not message:
        raise HTTPException(404)

    # Find the running workflow for this message
    client = await get_temporal_client()
    handle = client.get_workflow_handle(f"human-review-{message_id}")
    await handle.signal(HumanReviewWorkflow.submit_decision, decision)

    return {"status": "decision_submitted"}
```

## 2.4 Activities [G-21, G-22, G-64]

```python
# kernel/temporal/activities.py
from temporalio import activity
from datetime import datetime, timedelta
from bson import ObjectId
from kernel.message.schema import Message, MessageLog
from kernel.message.mongodb_bus import MongoDBMessageBus
from kernel.db import ENTITY_REGISTRY
from kernel.context import current_org_id, current_actor_id, current_correlation_id, current_depth
from kernel_entities.actor import Actor
from kernel.skill.integrity import verify_content_hash
from kernel.skill.schema import Skill
from kernel.observability.tracing import create_span

class PermanentProcessingError(Exception):
    """Non-retryable processing error."""
    pass

class SkillTamperError(Exception):
    """Skill content hash mismatch."""
    pass

@activity.defn
async def claim_message(message_id: str, actor_id: str) -> bool:
    """Atomic claim via findOneAndUpdate. Returns False if already claimed."""
    bus = MongoDBMessageBus()
    msg = await bus.claim_by_id(message_id, ObjectId(actor_id))
    return msg is not None

@activity.defn
async def load_entity_context(message_id: str) -> dict:
    """Load the entity referenced by the message. Fresh from MongoDB."""
    message = await Message.get(ObjectId(message_id))
    if not message:
        return {"message": None, "entity": None}

    entity_cls = ENTITY_REGISTRY.get(message.entity_type)
    entity = None
    if entity_cls:
        entity = await entity_cls.get(message.entity_id)

    return {
        "message": message.dict(),
        "entity": entity.dict() if entity else None,
    }

@activity.defn
async def process_with_associate(message_id: str, associate_id: str, context: dict) -> dict:
    """The associate processes the message.
    This is where the skill is loaded, the execution mode determines
    the interpreter, and CLI commands are executed via the API."""  # [G-21]

    with create_span("associate.process", associate_id=associate_id):
        # Load associate configuration
        associate = await Actor.get(ObjectId(associate_id))
        if not associate or associate.status != "active":
            raise PermanentProcessingError(f"Associate {associate_id} not found or inactive")

        # Set auth context for this activity [G-64]
        current_org_id.set(associate.org_id)
        current_actor_id.set(str(associate.id))
        current_correlation_id.set(context["message"].get("correlation_id"))
        current_depth.set(context["message"].get("depth", 0))

        # Load and verify skills
        skills_content = await _load_skills(associate.skills or [])

        # Determine execution mode and run
        mode = associate.mode or "hybrid"

        if mode == "deterministic":
            result = await _execute_deterministic(associate, skills_content, context)
            # [G-56] Strict deterministic mode: raise if needs_reasoning
            if result.get("needs_reasoning") and associate.strict_deterministic:
                raise PermanentProcessingError(
                    f"Associate {associate.name} is strict_deterministic but capability "
                    f"returned needs_reasoning: {result.get('reason')}"
                )
        elif mode == "reasoning":
            result = await _execute_reasoning(associate, skills_content, context)
        else:  # hybrid
            result = await _execute_hybrid(associate, skills_content, context)

        return result

async def _load_skills(skill_names: list[str]) -> str:
    """Load and concatenate skill content with integrity verification."""
    parts = []
    for name in skill_names:
        skill = await Skill.find_one({"name": name, "status": "active"})
        if not skill:
            continue
        if not verify_content_hash(skill.content, skill.content_hash):
            raise SkillTamperError(f"Skill '{name}' failed integrity check")
        parts.append(skill.content)
    return "\n\n---\n\n".join(parts)

async def _execute_deterministic(associate: Actor, skills: str, context: dict) -> dict:
    """Execute skill deterministically — no LLM.
    Parses the skill for CLI commands and executes them via the API.

    The deterministic interpreter [G-25]:
    - Reads markdown skill content
    - Identifies lines that are CLI commands (lines starting with `indemn` or backtick-wrapped)
    - Identifies simple conditions (lines starting with "If" or "When")
    - Executes commands sequentially via HTTP API calls
    - Evaluates conditions against entity data
    - Returns the result of the last command

    This is a simple line-by-line interpreter, NOT a full DSL engine.
    Complex orchestration that can't be expressed as sequential commands
    with simple conditions should use reasoning mode instead.
    """
    import httpx
    from kernel.config import settings

    entity_data = context.get("entity", {})
    results = []

    # Parse skill into executable steps
    steps = _parse_skill_steps(skills)

    for step in steps:
        if step["type"] == "command":
            # Execute CLI command via API
            result = await _execute_command_via_api(
                step["command"], entity_data, associate
            )
            results.append(result)
            # Update entity_data with result if applicable
            if isinstance(result, dict):
                entity_data.update(result)

        elif step["type"] == "condition":
            # Evaluate condition
            from kernel.watch.evaluator import evaluate_condition
            if not evaluate_condition(step["condition"], entity_data):
                if step.get("on_false") == "skip":
                    continue
                elif step.get("on_false") == "stop":
                    break

        elif step["type"] == "auto_command":
            # Command with --auto flag — may return needs_reasoning
            result = await _execute_command_via_api(
                step["command"], entity_data, associate
            )
            if isinstance(result, dict) and result.get("needs_reasoning"):
                return result  # Bubble up to caller
            results.append(result)

    return {"status": "completed", "results": results}

def _parse_skill_steps(skill_content: str) -> list[dict]:
    """Parse markdown skill into executable steps.
    Recognizes:
    - Lines containing `indemn ...` as commands
    - Lines starting with numbers (1., 2.) containing backtick commands
    - Lines starting with 'If' or 'When' as conditions
    """
    steps = []
    for line in skill_content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue

        # Extract command from backticks
        import re
        cmd_match = re.search(r'`(indemn [^`]+)`', line)
        if cmd_match:
            cmd = cmd_match.group(1)
            if "--auto" in cmd:
                steps.append({"type": "auto_command", "command": cmd})
            else:
                steps.append({"type": "command", "command": cmd})
            continue

        # Simple condition
        if line.lower().startswith(("if ", "when ")):
            # Parse simple conditions like "If needs_reasoning is true"
            steps.append({
                "type": "condition",
                "condition": _parse_simple_condition(line),
                "on_false": "skip",
            })

    return steps

async def _execute_command_via_api(command: str, entity_data: dict, associate: Actor) -> dict:
    """Execute an indemn CLI command by translating it to an API call. [G-21]
    The command is parsed and mapped to the equivalent API endpoint."""
    import httpx
    from kernel.config import settings
    from kernel.auth.jwt import create_access_token

    # Parse command: "indemn email classify EMAIL-001 --auto"
    parts = command.strip().split()
    if parts[0] != "indemn":
        raise PermanentProcessingError(f"Invalid command: {command}")

    entity_type = parts[1]  # "email"
    operation = parts[2]    # "classify"
    args = parts[3:]        # ["EMAIL-001", "--auto"]

    # Get a service token for the associate
    token, _ = create_access_token(
        str(associate.id), str(associate.org_id),
        [r.name for r in await _get_roles(associate)],
    )

    async with httpx.AsyncClient(base_url=settings.api_url) as client:
        # Map to API endpoint
        # entity_type + "s" = collection slug
        # operation = method name
        entity_id = args[0] if args else None
        auto = "--auto" in args

        url = f"/api/{entity_type}s/{entity_id}/{operation}"
        params = {"auto": "true"} if auto else {}
        data = _extract_data_from_args(args)

        response = await client.post(
            url, json=data, params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60.0,
        )

        if response.status_code >= 400:
            raise PermanentProcessingError(
                f"API call failed: {response.status_code} {response.text}"
            )

        return response.json()

async def _execute_reasoning(associate: Actor, skills: str, context: dict) -> dict:
    """Execute skill using LLM reasoning. [G-21]
    The LLM reads the skill, analyzes the context, and decides which
    CLI commands to execute via the API."""
    # For Phase 2 MVP: use Anthropic API directly
    # Future: pluggable LLM provider per associate.llm_config
    import anthropic

    llm_config = associate.llm_config or {}
    model = llm_config.get("model", "claude-sonnet-4-6")
    temperature = llm_config.get("temperature", 0.2)

    client = anthropic.AsyncAnthropic()

    # Build the system prompt with skill content and entity context
    system_prompt = (
        f"You are an associate executing the following skill:\n\n{skills}\n\n"
        f"You have access to the Indemn OS CLI via the execute_command tool. "
        f"Every command goes through the API with your permissions. "
        f"Execute the steps in your skill against the provided context."
    )

    entity_context = context.get("entity", {})
    message_context = context.get("message", {})

    messages = [
        {"role": "user", "content": (
            f"Process this work item:\n\n"
            f"Entity: {message_context.get('entity_type')} {message_context.get('entity_id')}\n"
            f"Event: {message_context.get('event_type')}\n"
            f"Data: {_safe_serialize(entity_context)}"
        )},
    ]

    # Iterative tool-use loop
    max_iterations = 20
    results = []

    for i in range(max_iterations):
        response = await client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=temperature,
            system=system_prompt,
            messages=messages,
            tools=[{
                "name": "execute_command",
                "description": "Execute an indemn CLI command via the API",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The full indemn CLI command (e.g., 'indemn email classify EMAIL-001 --auto')",
                        },
                    },
                    "required": ["command"],
                },
            }],
        )

        # Check if the LLM wants to execute a command
        if response.stop_reason == "tool_use":
            for content_block in response.content:
                if content_block.type == "tool_use":
                    command = content_block.input["command"]
                    # Execute via API
                    try:
                        result = await _execute_command_via_api(command, entity_context, associate)
                        results.append({"command": command, "result": result})
                        # Feed result back to LLM
                        messages.append({"role": "assistant", "content": response.content})
                        messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": _safe_serialize(result),
                            }],
                        })
                    except Exception as e:
                        messages.append({"role": "assistant", "content": response.content})
                        messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": f"Error: {str(e)}",
                                "is_error": True,
                            }],
                        })

        elif response.stop_reason == "end_turn":
            # LLM is done — extract final text response
            final_text = "".join(
                b.text for b in response.content if hasattr(b, "text")
            )
            return {
                "status": "completed",
                "results": results,
                "summary": final_text,
            }

        # Heartbeat for long-running processing
        activity.heartbeat(f"iteration {i+1}")

    return {"status": "completed", "results": results, "warning": "max_iterations_reached"}

async def _execute_hybrid(associate: Actor, skills: str, context: dict) -> dict:
    """Try deterministic first. If any step returns needs_reasoning,
    fall back to LLM for the remainder."""
    result = await _execute_deterministic(associate, skills, context)
    if result.get("needs_reasoning"):
        # Fall back to reasoning with the needs_reasoning context included
        return await _execute_reasoning(associate, skills, {
            **context,
            "deterministic_result": result,
        })
    return result

@activity.defn
async def process_human_decision(message_id: str, decision: dict) -> dict:
    """Process a human's decision from the HumanReviewWorkflow."""
    message = await Message.get(ObjectId(message_id))
    if not message:
        return {"status": "message_not_found"}

    entity_cls = ENTITY_REGISTRY.get(message.entity_type)
    if not entity_cls:
        return {"status": "entity_type_not_found"}

    entity = await entity_cls.get(message.entity_id)
    if not entity:
        return {"status": "entity_not_found"}

    action = decision.get("action")  # approve, reject, escalate
    reason = decision.get("reason", "")

    if action == "approve":
        # Transition entity to the approved state (if applicable)
        if hasattr(entity, '_state_machine') and entity._state_machine:
            # The specific transition depends on the entity type and current state
            # The decision data can include a target_state
            target = decision.get("target_state")
            if target:
                entity.transition_to(target, reason=reason)
                await entity.save_tracked(method="human_approve", method_metadata={"decision": decision})
    elif action == "reject":
        target = decision.get("target_state")
        if target:
            entity.transition_to(target, reason=reason)
            await entity.save_tracked(method="human_reject", method_metadata={"decision": decision})

    return {"status": action, "entity_id": str(entity.id)}

@activity.defn
async def complete_message(message_id: str, result: dict) -> None:
    """Move message from queue to log."""
    bus = MongoDBMessageBus()
    await bus.complete(ObjectId(message_id), result)

@activity.defn
async def fail_message(message_id: str, error: str) -> None:
    """Return message to queue or move to dead_letter."""
    bus = MongoDBMessageBus()
    await bus.fail(ObjectId(message_id), error)

def _safe_serialize(obj) -> str:
    """Serialize to JSON string, handling ObjectIds and datetimes."""
    import orjson
    return orjson.dumps(obj, default=str).decode()

def _parse_simple_condition(line: str) -> dict:
    """Parse a simple condition from a skill line.
    E.g., 'If needs_reasoning is true' → {"field": "needs_reasoning", "op": "equals", "value": true}"""
    # Basic parsing — extended during implementation
    import re
    match = re.search(r'(\w+)\s+(is|equals?|=)\s+(\w+)', line, re.IGNORECASE)
    if match:
        field, _, value = match.groups()
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        return {"field": field, "op": "equals", "value": value}
    return {"field": "_always", "op": "equals", "value": True}  # Fallback: always true

def _extract_data_from_args(args: list[str]) -> dict:
    """Extract --key value pairs from CLI args into a dict."""
    data = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--") and args[i] != "--auto":
            key = args[i][2:].replace("-", "_")
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                data[key] = args[i + 1]
                i += 2
            else:
                data[key] = True
                i += 1
        else:
            i += 1
    return data

async def _get_roles(actor: Actor) -> list:
    """Load role entities for an actor."""
    from kernel_entities.role import Role
    return await Role.find({"_id": {"$in": actor.role_ids}}).to_list()
```

## 2.5 Context Propagation Through Associate Execution [G-22]

When an associate's CLI commands cause entity saves, the correlation_id and depth must propagate through the chain: Temporal activity → API call → save_tracked().

The API call carries context via headers:

```python
# In _execute_command_via_api():
headers = {
    "Authorization": f"Bearer {token}",
    "X-Correlation-ID": current_correlation_id.get() or "",
    "X-Cascade-Depth": str(current_depth.get()),
}
```

The API middleware reads these headers and sets context:

```python
# In kernel/auth/middleware.py (addition):
correlation_id = request.headers.get("X-Correlation-ID")
if correlation_id:
    current_correlation_id.set(correlation_id)
depth = request.headers.get("X-Cascade-Depth")
if depth:
    current_depth.set(int(depth))
```

This ensures that when an associate's API call triggers `save_tracked()`, the resulting messages inherit the correct correlation_id and depth from the original cascade.

## 2.6 Queue Processor — Temporal Dispatch [G-63, G-66, G-67]

Phase 2 adds Temporal workflow dispatch to the queue processor defined in Phase 1.

```python
# Addition to kernel/queue_processor.py

async def dispatch_associate_workflows():
    """Find pending messages for roles with associates.
    Start Temporal workflows for them.
    This is the SWEEP BACKSTOP — optimistic dispatch from the API
    is the primary path. This catches anything that was missed."""
    from kernel_entities.role import Role
    from kernel_entities.actor import Actor
    from kernel.temporal.client import get_temporal_client
    from temporalio.client import WorkflowAlreadyStartedError

    # Find pending messages older than the dispatch threshold
    threshold = datetime.utcnow() - timedelta(seconds=10)
    messages = await Message.find({
        "status": "pending",
        "created_at": {"$lt": threshold},
    }).to_list(limit=100)

    if not messages:
        return

    client = await get_temporal_client()

    for message in messages:
        # Look up role by name + org [G-66]
        role = await Role.find_one({
            "name": message.target_role,
            "org_id": message.org_id,
        })
        if not role:
            continue

        # Check if this role has active associate actors
        associates = await Actor.find({
            "type": "associate",
            "role_ids": role.id,
            "status": "active",
            "org_id": message.org_id,
        }).to_list()

        if not associates:
            continue

        # Pick an associate (first available — simple for MVP)
        associate = associates[0]

        # Determine workflow type
        # If the role is marked for human review, use HumanReviewWorkflow
        # Otherwise use ProcessMessageWorkflow
        workflow_cls = ProcessMessageWorkflow
        workflow_id = f"msg-{message.id}"

        try:
            await client.start_workflow(
                workflow_cls.run,
                args=[str(message.id), str(associate.id)],
                id=workflow_id,
                task_queue="indemn-kernel",
            )
        except WorkflowAlreadyStartedError:
            pass  # Already dispatched — optimistic dispatch got it

# Register as a Phase 2 sweep function [G-67]
register_sweep(dispatch_associate_workflows)
```

## 2.7 Optimistic Dispatch (Fire-and-Forget)

After the entity save transaction commits in the API server, optimistically start Temporal workflows for associate-eligible messages. This is the PRIMARY dispatch path — the queue processor sweep is the backstop.

```python
# kernel/message/dispatch.py

async def optimistic_dispatch(messages: list["Message"]):
    """Fire-and-forget Temporal workflow start for associate-eligible messages.
    Called AFTER the MongoDB transaction commits (not inside it).
    If this fails, the queue processor sweep catches it."""
    from kernel_entities.role import Role
    from kernel_entities.actor import Actor
    from kernel.temporal.client import get_temporal_client
    from kernel.temporal.workflows import ProcessMessageWorkflow

    try:
        client = await get_temporal_client()
    except Exception:
        return  # Temporal unavailable — sweep will handle it

    for message in messages:
        try:
            role = await Role.find_one({
                "name": message.target_role,
                "org_id": message.org_id,
            })
            if not role:
                continue

            associates = await Actor.find({
                "type": "associate",
                "role_ids": role.id,
                "status": "active",
                "org_id": message.org_id,
            }).to_list(limit=1)

            if not associates:
                continue

            await client.start_workflow(
                ProcessMessageWorkflow.run,
                args=[str(message.id), str(associates[0].id)],
                id=f"msg-{message.id}",
                task_queue="indemn-kernel",
            )
        except Exception:
            pass  # Fire and forget — sweep catches it
```

Called from the API layer after save_tracked() completes:

```python
# In the API create/transition/method endpoints, after save_tracked():
# (save_tracked returns the list of messages it created)
from kernel.message.dispatch import optimistic_dispatch
import asyncio
# Fire and forget — don't await, don't block the response
asyncio.create_task(optimistic_dispatch(created_messages))
```

## 2.8 Scheduled Task Execution [G-76]

Two approaches per the decision analysis:

**Option A (Phase 2 MVP): Application-level cron in the queue processor.**
Simple, no Temporal dependency for scheduling. The queue processor checks cron expressions and creates queue messages.

```python
# Addition to kernel/queue_processor.py
from croniter import croniter

async def check_scheduled_associates():
    """Check for associates with schedule triggers whose cron has fired."""
    associates = await Actor.find({
        "type": "associate",
        "status": "active",
        "trigger_schedule": {"$exists": True, "$ne": None},
    }).to_list()

    for associate in associates:
        cron = croniter(associate.trigger_schedule, datetime.utcnow() - timedelta(minutes=1))
        next_fire = cron.get_next(datetime)
        if next_fire <= datetime.utcnow():
            # Check if we already created a message for this firing
            existing = await Message.find_one({
                "entity_type": "_scheduled",
                "entity_id": associate.id,
                "created_at": {"$gte": datetime.utcnow() - timedelta(minutes=1)},
            })
            if existing:
                continue

            # Create message in queue — same path as watch-triggered work
            message = Message(
                org_id=associate.org_id,
                entity_type="_scheduled",
                entity_id=associate.id,
                event_type="schedule_fired",
                target_role=associate.role_ids[0] if associate.role_ids else "",
                correlation_id=str(uuid4()),
                status="pending",
                summary={"display": f"Scheduled: {associate.name}"},
            )
            await message.insert()

register_sweep(check_scheduled_associates)
```

**Future upgrade path [G-76]**: Migrate to Temporal Schedules when more sophisticated scheduling is needed (complex intervals, calendar-based, pause/resume via Temporal UI). The migration is additive — scheduled associates that use Temporal Schedules bypass the application-level cron check.

## 2.9 Direct Invocation for Real-Time

Create queue entry for visibility AND start workflow immediately (bypass the queue processor sweep).

```python
# kernel/api/direct_invoke.py
from fastapi import APIRouter, Depends
from kernel.auth.middleware import get_current_actor
from kernel.temporal.client import get_temporal_client
from kernel.temporal.workflows import ProcessMessageWorkflow
from kernel.message.schema import Message
from uuid import uuid4
from datetime import datetime

invoke_router = APIRouter(prefix="/api/associates", tags=["associates"])

@invoke_router.post("/{associate_id}/invoke")
async def invoke_associate(associate_id: str, context: dict = {},
                            actor=Depends(get_current_actor)):
    """Direct invocation — queue entry created + workflow started immediately.
    Used for real-time channels and testing."""
    associate = await Actor.get(ObjectId(associate_id))
    if not associate:
        raise HTTPException(404)

    # Create message in queue for visibility
    message = Message(
        org_id=associate.org_id,
        entity_type=context.get("entity_type", "_direct"),
        entity_id=ObjectId(context.get("entity_id", str(ObjectId()))),
        event_type="direct_invocation",
        target_role="",
        correlation_id=str(uuid4()),
        status="pending",
        context=context,
        summary={"display": f"Direct: {associate.name}"},
    )
    await message.insert()

    # Start workflow immediately
    client = await get_temporal_client()
    await client.start_workflow(
        ProcessMessageWorkflow.run,
        args=[str(message.id), associate_id],
        id=f"direct-{message.id}",
        task_queue="indemn-kernel",
    )

    return {"message_id": str(message.id), "status": "invoked"}
```

## 2.10 Bulk Operations [G-24, G-61, G-80, G-81]

### BulkExecuteWorkflow

```python
# Addition to kernel/temporal/workflows.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class BulkOperationSpec:
    entity_type: str
    operation: str              # "create", "transition", "method", "update", "delete"
    method_name: Optional[str]  # For "method" operation
    filter_query: Optional[dict]  # For query-based source
    source_data: Optional[list]   # For explicit data source
    batch_size: int = 50
    failure_mode: str = "skip"  # "skip" or "abort"
    dry_run: bool = False
    target_state: Optional[str] = None  # For "transition" operation
    sets: Optional[dict] = None  # For "update" operation

@dataclass
class BulkResult:
    status: str                 # completed, completed_with_errors, failed
    total: int
    processed: int
    skipped: int
    errors: list

@workflow.defn
class BulkExecuteWorkflow:
    """Generic bulk operation workflow.
    bulk_operation_id = temporal_workflow_id [G-61] — deliberate coupling."""

    @workflow.run
    async def run(self, spec_dict: dict) -> dict:
        spec = BulkOperationSpec(**spec_dict)

        if spec.dry_run:  # [G-81]
            preview = await workflow.execute_activity(
                preview_bulk_operation,
                args=[spec_dict],
                start_to_close_timeout=timedelta(minutes=2),
            )
            return {"status": "dry_run", "preview": preview}

        processed = 0
        total_errors = []
        total_count = 0

        while True:
            batch_result = await workflow.execute_activity(
                process_bulk_batch,  # [G-80]
                args=[spec_dict, processed],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5),
                    non_retryable_error_types=["BulkAbortError"],
                ),
            )

            processed += batch_result["batch_processed"]
            total_count = batch_result.get("total_count", total_count)
            total_errors.extend(batch_result.get("errors", []))

            if batch_result["done"]:
                break

            # Heartbeat with progress
            workflow.logger.info(f"Bulk progress: {processed}/{total_count}")

        status = "completed"
        if total_errors:
            status = "completed_with_errors"

        return {
            "status": status,
            "total": total_count,
            "processed": processed,
            "skipped": len(total_errors),
            "errors": total_errors,
        }
```

### Bulk Batch Activity [G-80]

```python
# Addition to kernel/temporal/activities.py

class BulkAbortError(Exception):
    """Raised in abort mode when any entity fails."""
    pass

@activity.defn
async def process_bulk_batch(spec_dict: dict, offset: int) -> dict:
    """Process one batch of a bulk operation within a MongoDB transaction."""
    spec = BulkOperationSpec(**spec_dict)
    entity_cls = ENTITY_REGISTRY.get(spec.entity_type)
    if not entity_cls:
        raise PermanentProcessingError(f"Entity type {spec.entity_type} not found")

    # Query entities
    if spec.filter_query:
        entities = await entity_cls.find_scoped(spec.filter_query).skip(offset).limit(spec.batch_size).to_list()
    elif spec.source_data:
        entities = spec.source_data[offset:offset + spec.batch_size]
    else:
        return {"done": True, "batch_processed": 0}

    if not entities:
        return {"done": True, "batch_processed": 0, "total_count": offset}

    errors = []
    batch_processed = 0

    # Process in a MongoDB transaction
    client = entity_cls.get_motor_collection().database.client
    async with await client.start_session() as session:
        async with session.start_transaction():
            for entity in entities:
                try:
                    if spec.operation == "transition":
                        entity.transition_to(spec.target_state)
                        await entity.save_tracked(
                            method=f"bulk_transition",
                            method_metadata={"bulk_operation_id": activity.info().workflow_id},
                        )
                    elif spec.operation == "method":
                        # Invoke capability
                        from kernel.capability.registry import get_capability
                        cap_fn = get_capability(spec.method_name)
                        result = await cap_fn(entity, {}, entity.org_id)
                        if not result.get("needs_reasoning"):
                            for field, value in result.get("result", {}).items():
                                setattr(entity, field, value)
                            await entity.save_tracked(
                                method=spec.method_name,
                                method_metadata={
                                    "rule_evaluation": result.get("rule_evaluation"),
                                    "bulk_operation_id": activity.info().workflow_id,
                                },
                            )
                    elif spec.operation == "update":
                        # Silent update — no events (bulk-update is silent) [from CLI verb taxonomy]
                        if spec.sets:
                            for field, value in spec.sets.items():
                                setattr(entity, field, value)
                            # Direct MongoDB update, bypassing save_tracked() to avoid event emission
                            await entity.get_motor_collection().update_one(
                                {"_id": entity.id},
                                {"$set": spec.sets, "$inc": {"version": 1}},
                                session=session,
                            )
                    elif spec.operation == "create":
                        new_entity = entity_cls(org_id=current_org_id.get(), **entity)
                        await new_entity.save_tracked(method="bulk_create")
                    elif spec.operation == "delete":
                        await entity.get_motor_collection().delete_one(
                            {"_id": entity.id}, session=session
                        )

                    batch_processed += 1

                except (StateMachineError, ValueError, PermissionError) as e:
                    # Permanent error [from bulk-operations-pattern error classification]
                    if spec.failure_mode == "abort":
                        raise BulkAbortError(str(e))
                    errors.append({
                        "entity_id": str(entity.id) if hasattr(entity, 'id') else str(entity),
                        "error_type": type(e).__name__,
                        "message": str(e),
                    })

                except VersionConflictError as e:
                    # Transient on first attempt — propagate for Temporal retry
                    raise

                activity.heartbeat(f"batch progress: {batch_processed}")

    total_count = offset + len(entities)
    done = len(entities) < spec.batch_size

    return {
        "done": done,
        "batch_processed": batch_processed,
        "total_count": total_count,
        "errors": errors,
    }

@activity.defn
async def preview_bulk_operation(spec_dict: dict) -> dict:
    """Dry-run preview — count and sample affected entities. [G-81]"""
    spec = BulkOperationSpec(**spec_dict)
    entity_cls = ENTITY_REGISTRY.get(spec.entity_type)
    if not entity_cls:
        return {"count": 0, "error": f"Entity type {spec.entity_type} not found"}

    if spec.filter_query:
        count = await entity_cls.find_scoped(spec.filter_query).count()
        sample = await entity_cls.find_scoped(spec.filter_query).limit(5).to_list()
        return {
            "count": count,
            "sample": [e.dict() for e in sample],
            "operation": spec.operation,
            "dry_run": True,
        }
    return {"count": 0}
```

### Bulk CLI Commands [from CLI verb taxonomy]

```python
# kernel/cli/bulk_commands.py
import typer
from kernel.cli.client import get_client

bulk_app = typer.Typer(name="bulk", help="Bulk operations")

# These are registered per entity type dynamically, but the pattern is:

def register_bulk_commands(entity_name: str, entity_app: typer.Typer):
    @entity_app.command("bulk-create")
    def bulk_create(from_csv: str = None, batch_size: int = 50, dry_run: bool = False):
        """Create entities in bulk. Emits creation events."""
        ...

    @entity_app.command("bulk-transition")
    def bulk_transition(filter: str, to: str, batch_size: int = 50,
                        dry_run: bool = False, failure_mode: str = "skip"):
        """Transition entities in bulk. Emits state_changed events."""
        ...

    @entity_app.command("bulk-method")
    def bulk_method(method: str, filter: str, batch_size: int = 50,
                    dry_run: bool = False, failure_mode: str = "skip"):
        """Invoke @exposed method in bulk. Emits method_invoked events."""
        ...

    @entity_app.command("bulk-update")
    def bulk_update(filter: str, set: str, batch_size: int = 50, dry_run: bool = False):
        """Raw field updates in bulk. SILENT — no events emitted.
        Use for data migrations and backfills only.
        If changes should cascade, use bulk-method instead."""
        ...

    @entity_app.command("bulk-delete")
    def bulk_delete(filter: str, batch_size: int = 50, dry_run: bool = True):
        """Delete entities in bulk. Emits deletion events.
        Dry-run is TRUE by default for safety."""
        ...

# Bulk monitoring commands
@bulk_app.command("status")
def bulk_status(workflow_id: str):
    """Check status of a running bulk operation."""
    client = get_client()
    response = client.get(f"/api/bulk/{workflow_id}")
    ...

@bulk_app.command("list")
def bulk_list(status: str = None):
    """List active and recent bulk operations."""
    ...

@bulk_app.command("cancel")
def bulk_cancel(workflow_id: str):
    """Cancel a running bulk operation at the next batch boundary."""
    ...
```

## 2.11 Workflow Versioning [G-77]

For deploying new associate logic without disrupting in-flight workflows:

```python
# In workflows.py, use Temporal's versioning for backward-compatible changes:

@workflow.defn
class ProcessMessageWorkflow:
    @workflow.run
    async def run(self, message_id: str, associate_id: str) -> dict:
        # Version gate for backward-compatible changes
        version = workflow.patched("v2-enhanced-error-handling")

        if version:
            # New behavior
            ...
        else:
            # Old behavior (for in-flight workflows)
            ...
```

For breaking changes: use Temporal's Build ID-based versioning. Deploy new workers with a new Build ID. Temporal routes in-flight workflows to old workers and new workflows to new workers.

## 2.12 Lookup Bulk Import [G-60]

```python
# kernel/cli/lookup_commands.py

@lookup_app.command("import")
def import_lookup(name: str, from_csv: str, org: str = None):
    """Import lookup data from CSV. Bulk-importable, maintained by non-technical users."""
    import csv
    data = {}
    with open(from_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # First column is key, second is value
            cols = list(row.values())
            if len(cols) >= 2:
                data[cols[0]] = cols[1]

    client = get_client()
    response = client.post(f"/api/lookups", json={
        "name": name,
        "data": data,
    })
    typer.echo(f"Imported {len(data)} entries into lookup '{name}'")
```

---

# Phase 3: Integration Framework

## 3.1 Adapter Base Class and Error Hierarchy [G-27]

```python
# kernel/integration/adapter.py
from abc import ABC
from typing import Optional
from decimal import Decimal

class AdapterError(Exception):
    """Base adapter error."""
    pass

class AdapterAuthError(AdapterError):
    """Authentication failed — refresh credentials and retry."""
    pass

class AdapterRateLimitError(AdapterError):
    """Rate limited — backoff and retry."""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after

class AdapterTimeoutError(AdapterError):
    """Operation timed out — retry with longer timeout."""
    pass

class AdapterNotFoundError(AdapterError):
    """Resource not found — don't retry."""
    pass

class AdapterValidationError(AdapterError):
    """Invalid request — don't retry."""
    pass

class Adapter(ABC):
    """Base adapter. Provider-specific adapters inherit this."""

    def __init__(self, config: dict, credentials: dict):
        self.config = config
        self.credentials = credentials

    # Outbound
    async def fetch(self, **params) -> list[dict]:
        raise NotImplementedError

    async def send(self, payload: dict) -> dict:
        raise NotImplementedError

    async def charge(self, amount: Decimal, currency: str = "usd", **params) -> dict:
        raise NotImplementedError

    # Inbound
    async def validate_webhook(self, headers: dict, body: bytes) -> bool:
        raise NotImplementedError

    async def parse_webhook(self, body: dict) -> dict:
        """Returns: {entity_type, lookup_by, lookup_value, operation, params}"""
        raise NotImplementedError

    # Auth
    async def auth_initiate(self, redirect_uri: str) -> str:
        raise NotImplementedError

    async def auth_callback(self, code: str, state: str) -> dict:
        raise NotImplementedError

    # OAuth token refresh [G-26]
    async def refresh_token(self) -> dict:
        """Refresh OAuth tokens. Returns new credentials to store."""
        raise NotImplementedError

    def needs_token_refresh(self) -> bool:
        """Check if the token is expired or about to expire."""
        return False
```

## 3.2 Adapter Registry

```python
# kernel/integration/registry.py

ADAPTER_REGISTRY: dict[str, type["Adapter"]] = {}

def register_adapter(provider: str, version: str, adapter_cls: type):
    key = f"{provider}:{version}"
    ADAPTER_REGISTRY[key] = adapter_cls

def get_adapter_class(provider: str, version: str) -> type:
    key = f"{provider}:{version}"
    cls = ADAPTER_REGISTRY.get(key)
    if not cls:
        raise AdapterNotFoundError(f"No adapter for {key}")
    return cls
```

## 3.3 Credential Resolution [from integration-as-primitive]

```python
# kernel/integration/resolver.py
from kernel_entities.integration import Integration
from kernel_entities.actor import Actor
from kernel.context import current_org_id, current_actor_id
from bson import ObjectId

async def resolve_integration(
    system_type: str,
    actor_id: ObjectId = None,
    org_id: ObjectId = None,
    require_org_only: bool = False,
) -> Integration:
    """Resolve the Integration to use. Priority: actor → owner → org."""
    _actor_id = actor_id or ObjectId(current_actor_id.get())
    _org_id = org_id or current_org_id.get()

    # Step 1: Actor's own personal integration
    if not require_org_only:
        personal = await Integration.find_one({
            "owner_type": "actor",
            "owner_id": _actor_id,
            "system_type": system_type,
            "status": "active",
            "org_id": _org_id,
        })
        if personal:
            return personal

    # Step 2: Owner's personal integration (for owner-bound associates)
    if not require_org_only:
        actor = await Actor.get(_actor_id)
        if actor and actor.owner_actor_id:
            owner_integration = await Integration.find_one({
                "owner_type": "actor",
                "owner_id": actor.owner_actor_id,
                "system_type": system_type,
                "status": "active",
                "org_id": _org_id,
            })
            if owner_integration:
                return owner_integration

    # Step 3: Org-level with role-based access
    actor = actor if 'actor' in dir() else await Actor.get(_actor_id)
    if actor:
        from kernel_entities.role import Role
        roles = await Role.find({"_id": {"$in": actor.role_ids}}).to_list()
        role_names = [r.name for r in roles]

        org_integration = await Integration.find_one({
            "owner_type": "org",
            "org_id": _org_id,
            "system_type": system_type,
            "status": "active",
            "access.roles": {"$in": role_names},
        })
        if org_integration:
            return org_integration

    raise AdapterNotFoundError(
        f"No {system_type} integration available. "
        f"Create one with: indemn integration create --system-type {system_type} ..."
    )
```

## 3.4 Credential Management [G-28]

```python
# kernel/integration/credentials.py
import boto3
import orjson
import time
from kernel.config import settings

_secrets_client = None
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 300  # 5 minutes

def _get_secrets_client():
    global _secrets_client
    if _secrets_client is None:
        _secrets_client = boto3.client(
            "secretsmanager",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
    return _secrets_client

async def fetch_credentials(secret_ref: str) -> dict:
    """Fetch credentials from Secrets Manager with TTL caching."""
    now = time.time()
    if secret_ref in _cache:
        creds, cached_at = _cache[secret_ref]
        if now - cached_at < CACHE_TTL:
            return creds

    client = _get_secrets_client()
    response = client.get_secret_value(SecretId=secret_ref)
    creds = orjson.loads(response["SecretString"])
    _cache[secret_ref] = (creds, now)
    return creds

async def store_credentials(secret_ref: str, credentials: dict):
    """Store credentials in Secrets Manager."""
    client = _get_secrets_client()
    try:
        client.update_secret(
            SecretId=secret_ref,
            SecretString=orjson.dumps(credentials).decode(),
        )
    except client.exceptions.ResourceNotFoundException:
        client.create_secret(
            Name=secret_ref,
            SecretString=orjson.dumps(credentials).decode(),
        )
    # Invalidate cache [G-28]
    _cache.pop(secret_ref, None)

def invalidate_cached_credentials(secret_ref: str):
    """Invalidate cached credentials (e.g., after rotation)."""
    _cache.pop(secret_ref, None)
```

## 3.5 Adapter Dispatch with Auto-Refresh [G-26]

```python
# kernel/integration/dispatch.py
from kernel.integration.resolver import resolve_integration
from kernel.integration.credentials import fetch_credentials, store_credentials, invalidate_cached_credentials
from kernel.integration.registry import get_adapter_class
from kernel.integration.adapter import Adapter, AdapterAuthError

async def get_adapter(
    system_type: str,
    actor_id=None, org_id=None,
    require_org_only: bool = False,
) -> Adapter:
    """Resolve integration, fetch credentials, instantiate adapter.
    Handles OAuth token refresh transparently. [G-26]"""
    integration = await resolve_integration(system_type, actor_id, org_id, require_org_only)
    credentials = await fetch_credentials(integration.secret_ref)
    adapter_cls = get_adapter_class(integration.provider, integration.provider_version)
    adapter = adapter_cls(config=integration.config, credentials=credentials)

    # Check if token needs refresh (OAuth adapters)
    if adapter.needs_token_refresh():
        try:
            new_credentials = await adapter.refresh_token()
            await store_credentials(integration.secret_ref, new_credentials)
            # Recreate adapter with fresh credentials
            adapter = adapter_cls(config=integration.config, credentials=new_credentials)
        except Exception as e:
            # Token refresh failed — the adapter will get a 401 on use
            import logging
            logging.warning(f"Token refresh failed for {integration.name}: {e}")

    return adapter

async def execute_with_retry(adapter: Adapter, method_name: str, *args, **kwargs):
    """Execute an adapter method with automatic retry on auth errors.
    On AdapterAuthError: refresh token, recreate adapter, retry once."""
    method = getattr(adapter, method_name)
    try:
        return await method(*args, **kwargs)
    except AdapterAuthError:
        # Try to refresh and retry
        if hasattr(adapter, 'refresh_token'):
            new_creds = await adapter.refresh_token()
            await store_credentials(adapter._secret_ref, new_creds)
            adapter.credentials = new_creds
            return await method(*args, **kwargs)
        raise
```

## 3.6 Webhook Endpoint

```python
# kernel/api/webhook.py
from fastapi import APIRouter, Request, HTTPException
from kernel_entities.integration import Integration
from kernel.integration.credentials import fetch_credentials
from kernel.integration.registry import get_adapter_class
from kernel.db import ENTITY_REGISTRY
from kernel.context import current_org_id, current_actor_id
import orjson

webhook_router = APIRouter(tags=["webhooks"])

@webhook_router.post("/webhook/{provider}/{integration_id}")
async def handle_webhook(provider: str, integration_id: str, request: Request):
    """Generic webhook handler. Validates via adapter, applies entity operations.
    Entity operations go through save_tracked() for state machine enforcement and event emission."""

    # Load integration
    integration = await Integration.get(integration_id)
    if not integration or integration.provider != provider:
        raise HTTPException(404, "Integration not found")
    if integration.status != "active":
        raise HTTPException(400, "Integration is not active")

    # Get adapter
    credentials = await fetch_credentials(integration.secret_ref)
    adapter_cls = get_adapter_class(integration.provider, integration.provider_version)
    adapter = adapter_cls(config=integration.config, credentials=credentials)

    # Validate webhook signature
    body_bytes = await request.body()
    headers = dict(request.headers)

    try:
        valid = await adapter.validate_webhook(headers, body_bytes)
    except NotImplementedError:
        raise HTTPException(400, f"Adapter {provider} does not support inbound webhooks")

    if not valid:
        raise HTTPException(401, "Invalid webhook signature")

    # Parse webhook into entity operations
    body_json = orjson.loads(body_bytes)
    parsed = await adapter.parse_webhook(body_json)

    # Set org context for entity operations
    current_org_id.set(integration.org_id)
    current_actor_id.set(f"webhook:{provider}")

    # Apply entity operations via entity methods (state machine enforced)
    entity_cls = ENTITY_REGISTRY.get(parsed["entity_type"])
    if not entity_cls:
        raise HTTPException(400, f"Unknown entity type: {parsed['entity_type']}")

    entity = await entity_cls.find_one({
        parsed["lookup_by"]: parsed["lookup_value"],
        "org_id": integration.org_id,
    })
    if not entity:
        raise HTTPException(404,
            f"{parsed['entity_type']} not found: {parsed['lookup_by']}={parsed['lookup_value']}")

    if parsed["operation"] == "transition":
        entity.transition_to(parsed["params"]["to_status"])
        await entity.save_tracked(
            actor_id=f"webhook:{provider}",
            method=f"webhook_{parsed['operation']}",
            method_metadata={"webhook_event": body_json.get("type")},
        )
    elif parsed["operation"] == "update":
        for field, value in parsed["params"].items():
            setattr(entity, field, value)
        await entity.save_tracked(
            actor_id=f"webhook:{provider}",
            method=f"webhook_{parsed['operation']}",
        )
    elif parsed["operation"] == "create":
        new_entity = entity_cls(org_id=integration.org_id, **parsed["params"])
        await new_entity.save_tracked(
            actor_id=f"webhook:{provider}",
            method="webhook_create",
        )

    return {"status": "ok"}
```

## 3.7 Outlook Adapter [G-26, G-31]

```python
# kernel/integration/adapters/outlook.py
import httpx
from datetime import datetime, timedelta
from kernel.integration.adapter import (
    Adapter, AdapterAuthError, AdapterRateLimitError, AdapterTimeoutError,
    register_adapter,
)

class OutlookAdapter(Adapter):
    """Microsoft Graph API adapter for Outlook email."""

    def needs_token_refresh(self) -> bool:
        """Check if the access token is expired or about to expire."""
        expires_at = self.credentials.get("expires_at")
        if not expires_at:
            return False
        # Refresh if expires within 5 minutes
        return datetime.fromisoformat(expires_at) < datetime.utcnow() + timedelta(minutes=5)

    async def refresh_token(self) -> dict:  # [G-26]
        """Refresh OAuth tokens using the refresh token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://login.microsoftonline.com/{self.config['tenant_id']}/oauth2/v2.0/token",
                data={
                    "client_id": self.config["client_id"],
                    "client_secret": self.credentials["client_secret"],
                    "refresh_token": self.credentials["refresh_token"],
                    "grant_type": "refresh_token",
                    "scope": "https://graph.microsoft.com/.default",
                },
            )
            if response.status_code != 200:
                raise AdapterAuthError(f"Token refresh failed: {response.text}")

            token_data = response.json()
            return {
                **self.credentials,
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", self.credentials["refresh_token"]),
                "expires_at": (
                    datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                ).isoformat(),
            }

    async def fetch(self, since: str = None, folder: str = "inbox", limit: int = 50, **params) -> list[dict]:
        """Fetch emails from Outlook inbox."""  # [G-31 — async httpx]
        headers = {"Authorization": f"Bearer {self.credentials['access_token']}"}
        url = f"https://graph.microsoft.com/v1.0/me/mailFolders/{folder}/messages"
        query_params = {"$top": limit, "$orderby": "receivedDateTime desc"}
        if since:
            query_params["$filter"] = f"receivedDateTime ge {since}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=query_params, timeout=30.0)

            if response.status_code == 401:
                raise AdapterAuthError("Outlook: access token expired")
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                raise AdapterRateLimitError("Outlook rate limited", retry_after=retry_after)
            if response.status_code >= 500:
                raise AdapterTimeoutError(f"Outlook server error: {response.status_code}")

            response.raise_for_status()
            messages = response.json().get("value", [])

        return [self._map_to_os(msg) for msg in messages]

    async def send(self, payload: dict) -> dict:
        """Send an email via Outlook."""
        headers = {"Authorization": f"Bearer {self.credentials['access_token']}"}
        url = "https://graph.microsoft.com/v1.0/me/sendMail"
        body = {"message": self._map_from_os(payload)}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body, timeout=30.0)
            if response.status_code == 401:
                raise AdapterAuthError("Outlook: access token expired")
            response.raise_for_status()

        return {"status": "sent"}

    def _map_to_os(self, outlook_msg: dict) -> dict:
        return {
            "external_id": outlook_msg["id"],
            "from_address": outlook_msg.get("from", {}).get("emailAddress", {}).get("address", ""),
            "to_addresses": [
                r.get("emailAddress", {}).get("address", "")
                for r in outlook_msg.get("toRecipients", [])
            ],
            "subject": outlook_msg.get("subject", ""),
            "body": outlook_msg.get("body", {}).get("content", ""),
            "received_at": outlook_msg.get("receivedDateTime"),
            "thread_id": outlook_msg.get("conversationId"),
            "has_attachments": outlook_msg.get("hasAttachments", False),
        }

    def _map_from_os(self, email_data: dict) -> dict:
        return {
            "toRecipients": [
                {"emailAddress": {"address": to}} for to in email_data.get("to_addresses", [])
            ],
            "subject": email_data.get("subject", ""),
            "body": {"contentType": "HTML", "content": email_data.get("body", "")},
        }

register_adapter("outlook", "v2", OutlookAdapter)
```

## 3.8 Stripe Adapter [G-31]

```python
# kernel/integration/adapters/stripe_adapter.py
import stripe
from decimal import Decimal
from datetime import datetime
from kernel.integration.adapter import (
    Adapter, AdapterAuthError, AdapterValidationError,
)
from kernel.integration.registry import register_adapter

class StripeAdapter(Adapter):
    """Stripe payment adapter — outbound charges + inbound webhooks."""

    def __init__(self, config, credentials):
        super().__init__(config, credentials)
        # [G-31] Use stripe's async client or set the API key for sync calls in executor
        stripe.api_key = credentials["secret_key"]

    async def charge(self, amount: Decimal, currency: str = "usd", **params) -> dict:
        """Create a Stripe PaymentIntent."""
        import asyncio
        # [G-31] Run sync Stripe SDK in executor
        intent = await asyncio.to_thread(
            stripe.PaymentIntent.create,
            amount=int(amount * 100),
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
        event_type = body.get("type", "")
        obj = body.get("data", {}).get("object", {})

        if event_type == "payment_intent.succeeded":
            return {
                "entity_type": "Payment",
                "lookup_by": "stripe_payment_intent_id",
                "lookup_value": obj["id"],
                "operation": "transition",
                "params": {
                    "to_status": "completed",
                    "charged_at": datetime.utcnow().isoformat(),
                },
            }
        elif event_type == "payment_intent.payment_failed":
            return {
                "entity_type": "Payment",
                "lookup_by": "stripe_payment_intent_id",
                "lookup_value": obj["id"],
                "operation": "transition",
                "params": {"to_status": "failed"},
            }
        else:
            raise AdapterValidationError(f"Unhandled Stripe event: {event_type}")

register_adapter("stripe", "v1", StripeAdapter)
```

## 3.9 Integration CLI Commands

```python
# Integration CRUD is auto-generated from the kernel entity.
# Additional manual commands for credential management:

@integration_app.command("set-credentials")
def set_credentials(integration_id: str, from_file: str):
    """Store credentials in Secrets Manager."""
    ...

@integration_app.command("rotate-credentials")
def rotate_credentials(integration_id: str):
    """Rotate credentials (provider-specific)."""
    ...

@integration_app.command("test")
def test_integration(integration_id: str):
    """Test connectivity by calling a read-only adapter method."""
    ...

@integration_app.command("upgrade")  # [G-30]
def upgrade_integration(integration_id: str, to_version: str, dry_run: bool = True):
    """Upgrade adapter version (e.g., outlook v2 → v3)."""
    ...
```

---

## Phase 2+3 Acceptance Criteria

```
PHASE 2:

1. ASSOCIATE CLAIMS AND PROCESSES
   Associate with role + skill → entity matches watch → message in queue →
   Temporal workflow starts → claims message → processes via skill → entity changes →
   message moves to log → new messages generated → system churns

2. --auto PATTERN END-TO-END
   Rules configured → associate invokes capability --auto → rules match → deterministic result
   Rules don't match → needs_reasoning → LLM provides classification

3. HUMAN-IN-THE-LOOP VIA SIGNALS
   HumanReviewWorkflow starts → waits for signal → human decides via API →
   workflow resumes → entity state changes

4. SCHEDULED ASSOCIATE
   Associate with cron trigger → queue processor creates message →
   workflow dispatches → processes → same path as watch-triggered

5. DIRECT INVOCATION
   API call → queue entry created → workflow started immediately → processes

6. FAILURE HANDLING
   Associate crashes → visibility timeout → message reclaimable →
   max_attempts exceeded → dead_letter

7. BULK OPERATIONS
   bulk-transition with filter → BulkExecuteWorkflow → batched processing →
   per-entity events → progress queryable → dry-run works

8. GRADUAL ROLLOUT
   Human + associate on same role → both see queue → associate claims first →
   human handles unclaimed → remove human → associate handles all

9. OTEL TRACES
   Temporal TracingInterceptor → every workflow + activity has OTEL spans →
   spans nested under entity change trace via correlation_id

10. CONTEXT PROPAGATION
    Associate's API calls carry X-Correlation-ID and X-Cascade-Depth →
    nested entity saves inherit correlation context

PHASE 3:

11. INTEGRATION CREATED + CONNECTED
    Create integration → set credentials (Secrets Manager) → test → active

12. OUTBOUND OPERATION
    Entity method → resolve integration → fetch credentials → adapter executes →
    result returned → entity updated

13. INBOUND WEBHOOK
    External system → /webhook/{provider}/{id} → validate signature →
    parse → entity operation via save_tracked() → watches fire

14. CREDENTIAL RESOLUTION PRIORITY
    Actor-level > owner-level > org-level with role check > error with clear message

15. OAUTH TOKEN REFRESH
    Token expired → adapter detects → refreshes via provider → stores new tokens →
    retries operation — transparent to caller

16. ADAPTER ERROR HANDLING
    AuthError → refresh + retry. RateLimitError → backoff. NotFound → fail.
    ValidationError → fail. Timeout → retry.

17. TWO ADAPTERS WORKING
    Outlook: fetch emails + send emails (with token refresh)
    Stripe: create payment intent + validate/parse webhook
```

---

## Gaps Resolved in This Document

G-19 (Temporal TracingInterceptor), G-20 (HITL signals), G-21 (process_with_associate), G-22 (context propagation), G-23 (worker config), G-24 (bulk operations), G-25 (deterministic skill interpreter), G-26 (OAuth refresh), G-27 (adapter error hierarchy), G-28 (credential cache invalidation), G-29 (health monitoring — interface defined, full impl Phase 6), G-30 (adapter versioning — CLI defined), G-31 (Stripe async), G-56 (strict_deterministic flag), G-60 (lookup CSV import), G-61 (bulk_operation_id coupling), G-63 (queue processor scope), G-64 (Temporal activity auth context), G-66 (role name vs ID lookup), G-67 (extensible sweep functions), G-73 (multi-entity operations — via API calls within skill), G-76 (scheduled tasks — application cron with Temporal upgrade path), G-77 (workflow versioning), G-78 (claim sort order — in Phase 1 MessageBus), G-80 (process_bulk_batch), G-81 (dry-run), G-90 (per-activity retry policies).
