---
ask: "Resolve the real-time architecture design: how active working context is tracked (Attention), how scoped events are routed to specific actors (scoped watches), where associate execution lives (Runtime), how the harness pattern works, how handoff between actors/roles works, and how humans participate in real-time channels."
created: 2026-04-10
workstream: product-vision
session: 2026-04-10-a
sources:
  - type: conversation
    description: "Craig and Claude working through the real-time architecture design across multiple passes"
  - type: artifact
    description: "2026-04-10-eventguard-retrace.md (surfaced the mid-conversation event delivery gap)"
  - type: artifact
    description: "2026-04-10-crm-retrace.md (surfaced actor-context scoping for account ownership)"
  - type: artifact
    description: "2026-04-10-post-trace-synthesis.md (categorized the open design items)"
  - type: artifact
    description: "2026-04-10-base-ui-and-auth-design.md (proposed ephemeral entity locks, now unified with Attention)"
  - type: artifact
    description: "2026-04-10-integration-as-primitive.md (Integration owners, adapter pattern, reused for voice clients)"
---

# Real-Time Architecture Design

## What This Resolves

The GIC and EventGuard retraces together surfaced the biggest architectural gap in the kernel: **how do running real-time actors receive events that happen during a live interaction**, and **how do humans and associates hand off sessions to each other on the same channel**. The CRM retrace surfaced a related question: **how do scoped events (those relevant only to a specific actor) get routed correctly without broadcasting to everyone with the same role**.

This artifact resolves all of these together because they share one underlying design: the concept of an **Attention** (active working context), a **Runtime** (execution environment for associates), and **scoped watches** (the routing mechanism that reaches specific actors based on context). These three things are tightly coupled and must be designed together.

This artifact also supersedes and unifies three items from the post-trace synthesis:
- Item 1: Watch coalescing
- Item 2: Ephemeral entity locks
- Item 3: Actor-context watch scoping + mid-conversation event delivery

Plus it introduces the Runtime bootstrap entity, which wasn't on the synthesis list but surfaced as the right answer to the "where do associates actually run" question.

## The Updated Bootstrap Entity Set

Prior to this design, the bootstrap entities (entities the kernel knows about specifically because it depends on them for core behavior) were:

- **Organization** — multi-tenancy scope
- **Actor** — identity (humans and associates)
- **Role** — permissions + watches
- **Integration** — external system connection

This design adds two more:

- **Attention** — active working context of an actor on an entity
- **Runtime** — deployable host for associate execution

The six structural primitives (Entity, Message, Actor, Role, Organization, Integration) are unchanged. Attention and Runtime are bootstrap entities — managed like any entity, but the kernel depends on them for scoped routing and associate dispatch.

## Part 1: Attention

### What it is

An **Attention** is "this actor is currently attending to this entity, with this workflow or session, for this purpose, until this time."

It unifies two mechanisms that were previously separate in the design:
- **UI soft-locks** ("Cam is currently reviewing this draft") from the base-ui-and-auth artifact
- **Active routing context** ("the Quote Assistant is currently holding this Interaction") from the EventGuard retrace

Both are the same structural thing: an actor has an open working session on an entity with a lifetime, a heartbeat, auxiliary metadata, and a purpose. Unifying them gives us a single primitive for presence, soft-locking, and scoped event routing.

### Entity definition

```python
class Attention(Entity):  # bootstrap entity
    actor_id: ObjectId                      # Who is attending
    target_entity: dict                     # {"type": "Interaction", "id": "INT-091"}
    related_entities: list[dict] = []       # [{"type": "Application", "id": "APP-091", "path": "interaction.application_id"}]
                                             # Resolved at open time or updated during the session
    
    purpose: Literal[
        "real_time_session",    # Associate hosting an active Interaction
        "observing",             # Human watching an Interaction without handling
        "review",                # Human reviewing a Draft or entity before action
        "editing",               # Human actively editing an entity
        "claim_in_progress",     # Generic claim-and-work pattern
    ]
    
    runtime_id: Optional[ObjectId] = None    # For real-time sessions: which Runtime hosts this
    workflow_id: Optional[str] = None        # For async workflows: Temporal workflow ID (for signal delivery)
    session_id: Optional[str] = None         # For real-time sessions: Runtime instance's session handle
    
    opened_at: datetime
    last_heartbeat: datetime
    expires_at: datetime                     # TTL boundary, auto-expired if heartbeat stops
    
    metadata: dict = {}                      # Additional purpose-specific info
    
    org_id: ObjectId
    version: int = 1
    
    class Settings:
        name = "attentions"
        indexes = [
            [("actor_id", 1), ("purpose", 1)],
            [("target_entity.id", 1)],              # Lookup by target
            [("related_entities.id", 1)],           # Lookup by related
            [("runtime_id", 1), ("purpose", 1)],    # Runtime monitoring
            [("expires_at", 1)],                    # TTL expiration index
        ]
    
    state_machine = {
        "active": ["expired", "closed"],
    }
```

### Heartbeat semantics

Attention records require heartbeats to stay alive. The owner of an Attention (typically the Runtime instance hosting a session, or a UI process showing a user reviewing an entity) sends periodic heartbeats:

```bash
indemn attention heartbeat ATT-001
# Updates last_heartbeat and extends expires_at
```

Default heartbeat interval: 30 seconds. Default expiry: 2 minutes from last heartbeat (4x the interval, allows for missed beats).

If heartbeats stop, the Attention auto-expires via the TTL index. A background cleanup job transitions expired Attentions to `expired` status and emits an event (which other actors can watch for if they need to react to abandoned sessions).

**Heartbeat updates bypass audit logging.** They're noise (hundreds per session) and the interesting events are open/close/expire, which are recorded normally. The kernel has a special path: `indemn attention heartbeat` updates `last_heartbeat` and `expires_at` without generating a change record. Only open, close, and expiration generate changes.

### Core operations (auto-generated from entity definition)

```bash
# Open an Attention
indemn attention open \
  --actor ASSOC-QUOTE-ASSISTANT-001 \
  --target-entity Interaction:INT-091 \
  --related-entities '[{"type": "Application", "id": "APP-091"}]' \
  --purpose real_time_session \
  --runtime RUNTIME-VOICE-001 \
  --session-id sess_abc123 \
  --ttl 2m

# Heartbeat (no audit record)
indemn attention heartbeat ATT-001

# Close explicitly
indemn attention close ATT-001

# List attentions (observability)
indemn attention list --target-entity Interaction:INT-091     # who's attending this?
indemn attention list --actor cam@indemn.ai                   # what is Cam attending?
indemn attention list --purpose real_time_session             # all active real-time sessions
indemn attention list --purpose observing                     # who's currently watching?

# Status check
indemn attention status --target-entity Draft:DRAFT-091       # is anyone working on this?
```

### Use cases

**1. UI soft-lock (review)**
JC opens a Draft in his UI. The UI calls `indemn attention open --actor jc@indemn.ai --target-entity Draft:DRAFT-091 --purpose review --ttl 5m`. Other users opening the same Draft see "JC is reviewing this" via `indemn attention list --target-entity Draft:DRAFT-091`. JC's UI heartbeats every 30s. If JC walks away, the Attention expires and the lock lifts.

**2. Real-time session routing**
The Quote Assistant associate starts a voice call. The voice Runtime opens an Attention with purpose=real_time_session, runtime_id set, session_id set, related_entities pointing to the Interaction's Application. Scoped watches (see Part 2) use this Attention to route mid-conversation events to this specific running session.

**3. Observation**
Cam wants to watch an Interaction without taking it over. His UI opens an Attention with purpose=observing. This surfaces him in "who's watching this" queries AND subscribes his UI to real-time updates on the Interaction via a Change Stream. He can see turns as they happen. No handling state change.

**4. Presence awareness**
"Three underwriters are currently viewing this submission" — a query on Attention table by target_entity. The base UI shows avatar indicators for present users.

**5. Zombie claim detection**
Ops can query for Attentions with stale heartbeats (via the expiration sweep) to find stuck sessions. `indemn attention list --expired-after 10m --purpose real_time_session` finds zombie sessions whose runtime instances died without cleanup.

**6. Capacity management**
A runtime's health check can count active Attentions to determine its current load. Scheduling decisions (which runtime instance takes a new session) can consider Attention count.

### Why it's a bootstrap entity, not a primitive

Attention uses Entity (it's an entity itself) and Actor (it references actors) and sometimes Runtime (it references runtimes). It supports the kernel's core behavior (routing, soft-locking, presence) but it doesn't add a new structural concept to the model. It's infrastructure that the kernel depends on, same category as Role and Integration.

The six primitives remain: Entity, Message, Actor, Role, Organization, Integration. Attention is a bootstrap entity managed like any other entity, with special kernel hooks for heartbeat compression and TTL cleanup.

## Part 2: Scoped Watches

### The problem

Two variants surfaced in the retraces:

- **CRM**: Cam owns INSURICA. When a Meeting is created for INSURICA, Cam should see it in his queue. Kyle (also an account_owner, but owning different accounts) should not. Scope is a **field relationship** — meeting.organization.primary_owner_id = cam.actor_id.

- **EventGuard**: The Quote Assistant is in a live voice call. A Stripe webhook fires → Payment:completed event. The running Quote Assistant needs to receive this event **during the live conversation** so it can tell the customer "Your policy is confirmed." Scope is **the actor's current working context** — the Quote Assistant's Attention covers the Interaction whose linked Application is referenced by this Payment.

Without scoping, the kernel would deliver these events to every actor in the matching role — overwhelming queues and breaking real-time delivery.

### The solution: scope expressions on watches, resolved at emit time

A watch gains an optional `scope` field. When present, the kernel resolves the scope at event emission time and writes a `target_actor_id` on the message. Only that specific actor can claim the message; everyone else with the matching role sees it filtered out.

Two resolution types:

#### Type 1: `field_path` (ownership-style scoping)

The scope references a path on the entity (possibly traversing relationships) that resolves to an actor_id.

```json
{
  "entity": "Meeting",
  "event": "created",
  "scope": {
    "type": "field_path",
    "path": "organization.primary_owner_id"
  }
}
```

When a Meeting:created event fires:
1. The kernel loads the Meeting entity
2. Resolves `meeting.organization` → Organization entity
3. Reads `organization.primary_owner_id` → returns "cam@indemn.ai"
4. Writes the message with `target_actor_id = "cam@indemn.ai"`
5. Only Cam sees this message in his queue

If the field path resolves to null (unowned entity), the scoped watch skips this event. Unscoped watches for the same event still fire normally.

#### Type 2: `active_context` (real-time routing)

The scope matches "any actor whose Attention covers this entity or a related entity."

```json
{
  "entity": "Payment",
  "event": "transitioned",
  "when": {"field": "to", "op": "equals", "value": "completed"},
  "scope": {
    "type": "active_context",
    "traverses": "application_id"
  }
}
```

When a Payment:transitioned event fires:
1. The kernel reads the Payment's `application_id`
2. Queries the Attention table for records where `related_entities` includes `{"type": "Application", "id": <payment.application_id>}` AND status is active
3. For each matching Attention, writes a message to message_queue with `target_actor_id` = the Attention's actor_id
4. If the Attention has a `runtime_id` and `session_id`, the kernel ALSO notifies the Runtime instance for in-process delivery (see Part 3 on real-time event delivery)

If no Attentions match, no scoped message is created. The event might still fire unscoped watches normally.

### Unified message claim semantics

A message with `target_actor_id` set is claimable only by that specific actor. Queue queries use:

```
{
  "org_id": current_org,
  "target_role": actor.role,
  "status": "pending",
  "$or": [
    {"target_actor_id": null},
    {"target_actor_id": actor.id}
  ]
}
```

No runtime scope expression evaluation. All resolution happens at emit time. Clean and fast.

### Watch coalescing

Separately surfaced as a concern (bulk events spamming human queues): watches can declare a **coalescing strategy**.

```json
{
  "entity": "Submission",
  "event": "fields_changed",
  "when": {"field": "is_stale", "op": "equals", "value": true},
  "scope": {"type": "field_path", "path": "primary_owner_id"},
  "coalesce": {
    "strategy": "by_correlation_id",
    "window": "5m",
    "summary_template": "{{count}} submissions became stale"
  }
}
```

When multiple matching events share the same correlation_id (they came from the same upstream operation like a scheduled bulk update) within the coalescing window, they produce a single queue item with a batch_id grouping them together. The queue view renders the batch as one row with drill-down to individual items.

Coalescing is applied AFTER scope resolution. If three scope-matched messages target the same actor and share a correlation_id, they coalesce into one row for that actor. If they target different actors, each actor sees their own batch.

### Performance

- **Field_path scoping**: one extra entity read per matching event (traversing the relationship). Sub-millisecond with indexing. Typical scoped watch: 1-2 extra reads per event.
- **Active_context scoping**: one indexed query on the Attention table per matching event. Sub-millisecond. The Attention table is small (only active sessions, typically tens to low thousands of rows).
- **Total overhead**: negligible. Emit-time scope resolution costs microseconds to low milliseconds per event. At the target scale (100K events/hour), the additional load is imperceptible.

### Condition + scope composition

Watches can have both a `when` condition and a `scope` expression:

```json
{
  "entity": "Assessment",
  "event": "created",
  "when": {"field": "needs_review", "op": "equals", "value": true},
  "scope": {"type": "field_path", "path": "submission.underwriter_id"}
}
```

The kernel evaluates `when` first (does this event match at all?). If yes, it evaluates `scope` (which actor does it target?). If the scope resolves, the message is written with the target_actor_id. If either step fails, no message is emitted.

## Part 3: Runtime

### What it is

A **Runtime** is a deployable host for associate execution. It describes the execution environment — the framework, the transport, the capacity, the deployment image — and the kernel uses it to dispatch work to associates.

### Why it's a bootstrap entity

Associates need a place to run. Without a Runtime primitive, deployment is implicit and invisible to the OS — the kernel can't answer "where does this associate live?" or "how many voice sessions can we handle right now?" or "let's move this associate to a new framework version." Elevating Runtime to a bootstrap entity makes deployment first-class, CLI-manageable, and consistent with the "everything is data" philosophy.

### Entity definition

```python
class Runtime(Entity):  # bootstrap entity
    name: str                           # "Voice Production", "Async Worker Pool"
    kind: Literal[
        "realtime_chat",
        "realtime_voice",
        "realtime_sms",
        "async_worker",
    ]
    
    framework: str                      # "deepagents", "langchain", "custom"
    framework_version: str              # pinned, e.g. "1.2.0"
    
    transport: Optional[str] = None     # For real-time: "websocket", "livekit", "twilio_sms"
    transport_config: dict = {}         # Non-secret transport config
    transport_secret_ref: Optional[str] = None  # Secrets Manager path for credentials
    
    llm_config: dict = {}               # Default LLM settings (overridable per Associate)
    sandbox_config: dict = {}           # Default sandbox settings
    
    deployment_image: str               # Docker image or deployment artifact ref
    deployment_platform: str            # "ecs", "railway", "k8s", "local"
    deployment_ref: Optional[str] = None  # Platform-specific deployment identifier
    
    capacity: dict = {                  # Capacity hints
        "max_concurrent_sessions": None,
        "max_memory_mb": None,
    }
    
    status: Literal[
        "configured",      # Entity exists but not deployed
        "deploying",       # Deploy in progress
        "active",          # Instances running and accepting work
        "draining",        # Finishing existing work, not accepting new
        "stopped",         # No instances running
        "error",           # Deployment failed or unhealthy
    ]
    
    instances: list[dict] = []          # Live instance tracking
    # Each instance entry: {"instance_id": "pod-abc123", "started_at": "...", "last_heartbeat": "...",
    #                       "active_sessions": 12, "health": "ok"}
    
    org_id: ObjectId
    version: int = 1
    
    state_machine = {
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
            [("instances.instance_id", 1)],
        ]
```

### Runtime → Associate relationship

**One Runtime hosts many Associates.** Each Associate has a `runtime_id` pointing to its Runtime. A single voice Runtime can host EventGuard's Quote Assistant, a customer service voice bot, a CRM voice assistant, and any other voice associates — all concurrently.

When a session starts on the Runtime, the Runtime instance identifies WHICH associate this session is for (from Deployment metadata, direct invocation parameters, or trigger context) and loads that Associate's configuration. The Associate carries:
- Skills (behavioral instructions)
- LLM config (model, temperature, potentially overriding Runtime defaults)
- Prompt (if any)
- Mode (deterministic, reasoning, hybrid)
- Role (permissions + watches, which may be inline or shared)

The Runtime provides the execution environment. The Associate provides the per-session config.

This means: **one harness image can serve many associates**. The harness is generic per kind+framework combination (one for voice+deepagents, one for chat+deepagents, one for async+deepagents, etc.). It doesn't know which specific associate it's hosting until a session starts and it loads the associate from the OS.

### Runtime → Associate, explicit reference

```python
class Associate(Entity):
    name: str
    role_id: Optional[ObjectId]      # Named shared role, if Path 1
    inline_role: Optional[dict]       # Inline role def, if Path 2
    runtime_id: ObjectId              # Which Runtime hosts this associate
    
    skills: list[str]
    llm_config: dict                  # Overrides Runtime defaults
    prompt: Optional[str]
    mode: Literal["deterministic", "reasoning", "hybrid"]
    
    trigger: dict                     # Message, schedule, direct invocation
    
    owner_actor_id: Optional[ObjectId]  # From CRM retrace — for delegated credential access
    
    status: Literal["configured", "active", "paused", "retired"]
```

### Runtime lifecycle

```bash
# 1. Declare the runtime
indemn runtime create \
  --name "Voice Production" \
  --kind realtime_voice \
  --framework deepagents \
  --framework-version 1.2.0 \
  --transport livekit \
  --transport-config @livekit.json \
  --llm-config @default-llm.json \
  --capacity '{"max_concurrent_sessions": 50}' \
  --deployment-image "indemn/runtime-voice-deepagents:1.2.0" \
  --deployment-platform ecs

# 2. Deploy actual instances
indemn runtime deploy RUNTIME-VOICE-001 --instances 3
# Triggers the deployment platform (ECS/Railway/K8s) to start 3 instances

# 3. Attach associates
indemn associate create --name "Quote Assistant" --runtime RUNTIME-VOICE-001 \
  --skills quote-assistant --mode reasoning --llm-config '{"model": "claude-sonnet-4-6"}'

# 4. Observability
indemn runtime health RUNTIME-VOICE-001
# Output: 3 instances active, 14/150 sessions, last heartbeat 2s ago, 0 errors, status=active

indemn runtime instances RUNTIME-VOICE-001
# Per-instance detail

# 5. Operations
indemn runtime drain RUNTIME-VOICE-001         # Stop accepting new work
indemn runtime scale RUNTIME-VOICE-001 --instances 5
indemn associate move QUOTE-ASST-001 --to-runtime RUNTIME-VOICE-002  # Migrate an associate
```

### Instance bootstrap

When a Runtime is deployed, the deployment platform starts instances of the harness image. Each instance bootstraps by:

1. Reading its Runtime ID from an environment variable or launch parameter
2. Authenticating with the OS using a service token (retrieved from Secrets Manager using the Runtime's secret_ref)
3. Calling `indemn runtime register-instance --runtime RUNTIME-001 --instance-id pod-abc123 --format json` to record its presence on the Runtime entity's instances list
4. Starting its work consumers:
   - For async runtimes: subscribing to a Temporal task queue named after the Runtime
   - For real-time chat: starting a WebSocket server on a configured port
   - For real-time voice: registering as a LiveKit Agent worker
5. Sending periodic heartbeats via `indemn runtime heartbeat --runtime RUNTIME-001 --instance-id pod-abc123`

On shutdown (SIGTERM or crash), the instance either calls `indemn runtime unregister-instance` or its heartbeat stops and the Runtime entity marks it expired.

## Part 4: The Harness Pattern

### What a harness is

A **harness** is the glue code between a specific framework (deepagents, LangChain, custom) and the OS kernel. It runs as a deployable image (usually Docker), one image per kind+framework combination:

- `indemn/runtime-voice-deepagents:1.2.0` — voice + deepagents + LiveKit Agents
- `indemn/runtime-chat-deepagents:1.2.0` — chat + deepagents + WebSocket server
- `indemn/runtime-async-deepagents:1.2.0` — async + deepagents + Temporal worker
- `indemn/runtime-voice-langchain:1.0.0` — hypothetical alternative framework

Each image contains:
- The framework itself (deepagents + its dependencies)
- The transport layer (LiveKit Agents SDK, WebSocket library, etc.)
- A small harness script that bridges between them and the OS
- The `indemn` CLI pre-installed for use inside the harness

### How the harness uses the OS

**The harness uses the CLI, not a separate Python SDK.** This is the key design decision. The CLI is already the universal interface. The harness is "just another client" of the CLI, calling it via subprocess. No dual interface, no second code path, no framework-specific adapters in the kernel.

For high-frequency or streaming operations that don't fit a subprocess-per-call model, the CLI has **streaming commands** that output events continuously. The main one this design introduces is `indemn events stream`, which subscribes to MongoDB Change Streams and emits events as JSON lines on stdout.

### Generic harness example (voice + deepagents + LiveKit)

```python
# voice_deepagents_harness.py — serves ANY voice associate attached to this runtime
import os
import json
import subprocess
from livekit.agents import Agent, JobContext
from deepagents import create_deep_agent, DaytonaSandbox

RUNTIME_ID = os.environ["RUNTIME_ID"]
INSTANCE_ID = os.environ["INSTANCE_ID"]

async def entrypoint(ctx: JobContext):
    """LiveKit calls this for each incoming call."""
    
    # Which associate is this session for?
    associate_id = ctx.room.metadata["associate_id"]
    deployment_id = ctx.room.metadata.get("deployment_id")
    
    # Load the associate's config from the OS
    result = subprocess.run(
        ["indemn", "actor", "get", associate_id, "--format", "json"],
        capture_output=True, text=True, check=True
    )
    associate = json.loads(result.stdout)
    
    # Create the Interaction entity
    result = subprocess.run([
        "indemn", "interaction", "create",
        "--channel-type", "voice",
        "--deployment-id", deployment_id or "",
        "--initial-handler", associate_id,
        "--format", "json"
    ], capture_output=True, text=True, check=True)
    interaction = json.loads(result.stdout)
    interaction_id = interaction["id"]
    
    # Open an Attention for scoped event routing
    subprocess.run([
        "indemn", "attention", "open",
        "--actor", associate_id,
        "--target-entity", f"Interaction:{interaction_id}",
        "--purpose", "real_time_session",
        "--runtime", RUNTIME_ID,
        "--session-id", ctx.room.sid,
        "--ttl", "2m"
    ], check=True)
    
    # Build the agent from the Associate's config
    agent = create_deep_agent(
        model=associate["llm_config"]["model"],
        skills=associate["skills"],
        prompt=associate.get("prompt"),
        sandbox=DaytonaSandbox(
            image=os.environ["SANDBOX_IMAGE"],
            env={
                "INDEMN_ACTOR_TOKEN": get_associate_service_token(associate_id),
                "INDEMN_INTERACTION_ID": interaction_id,
                # indemn CLI in the sandbox is pre-authenticated as this associate
            }
        )
    )
    
    # Subscribe to scoped events for mid-conversation delivery
    event_proc = subprocess.Popen([
        "indemn", "events", "stream",
        "--actor", associate_id,
        "--interaction", interaction_id,
        "--format", "json-lines"
    ], stdout=subprocess.PIPE, text=True)
    
    # Register the agent with LiveKit
    await ctx.connect()
    livekit_agent = ctx.register_agent(agent)
    
    # Main loop: drive LiveKit turns + deliver scoped events
    async def event_pump():
        """Deliver scoped events to the agent as they arrive."""
        for line in event_proc.stdout:
            event = json.loads(line)
            await livekit_agent.inject_context(event)
    
    async def heartbeat():
        while True:
            subprocess.run(["indemn", "attention", "heartbeat", attention_id])
            await asyncio.sleep(30)
    
    # Run until the call ends
    try:
        await asyncio.gather(
            livekit_agent.run(),
            event_pump(),
            heartbeat()
        )
    finally:
        # Clean up on disconnect
        event_proc.terminate()
        subprocess.run(["indemn", "attention", "close", attention_id])
        subprocess.run([
            "indemn", "interaction", "transition",
            "--id", interaction_id,
            "--to", "closed"
        ])

# LiveKit worker entry point
if __name__ == "__main__":
    from livekit.agents import cli
    cli.run_app(entrypoint)
```

This is approximately 60 lines of Python. It:
- Uses LiveKit Agents fully (all features available)
- Uses deepagents fully (sandbox, skills, subagents, tool use)
- Loads per-session config from the Associate entity
- Manages the Interaction + Attention lifecycle
- Streams scoped events into the agent via the CLI

**The same pattern applies to other framework+transport combinations.** A chat harness looks similar but uses a WebSocket server instead of LiveKit Agents. An async worker harness uses Temporal activities. A different agent framework (LangChain, custom) would have its own harness that wraps that framework with the same CLI-based OS interaction.

### Why the CLI not an SDK

1. **Consistency**: agents already use the CLI (via deepagents' execute() tool). The harness using the CLI means one interface, not two.
2. **Universality**: any language can call a CLI. Future harnesses in Go, Node, Rust don't need a language-specific SDK.
3. **Auditability**: every CLI invocation is a traceable command. SDK calls could bypass audit hooks; CLI calls go through the same audit path as everything else.
4. **Permission scoping**: the CLI honors the authenticated actor's role. The harness runs as the Runtime's service actor; when it creates an Interaction, the kernel checks the Runtime actor's permissions. Same enforcement as any CLI call.
5. **Debuggability**: you can manually run the same CLI commands the harness runs. Reproducing issues is trivial.

**The one new CLI primitive this design requires**: `indemn events stream` — a long-running subprocess that outputs events as JSON lines on stdout, backed by MongoDB Change Streams. All other CLI operations are auto-generated from the entity framework.

## Part 5: Channel Transport

### How real-time channels connect

Each real-time Runtime's harness embeds or integrates with a channel-specific transport framework:

- **Voice**: LiveKit Agents (Indemn already uses LiveKit)
- **Chat**: WebSocket server (Python/Node, your choice)
- **SMS**: HTTP handlers for Twilio webhooks
- **Embedded widget**: WebSocket or HTTP long-poll, same as chat

The transport handles:
- Accepting connections
- Managing the persistent session with the end user
- Protocol-specific concerns (STT/TTS, WebSocket ping/pong, message formatting)
- Reconnection and keep-alives

The transport is NOT a separate kernel concept. It's bundled with the Runtime's deployment. Multiple instances of the same Runtime coordinate on transport via framework-native mechanisms (LiveKit's project-level room state, WebSocket sticky sessions, etc.).

### Mid-conversation event delivery

When a scoped watch matches an Attention with a `runtime_id` and `session_id`, the kernel:

1. Writes the message to message_queue with `target_actor_id` (durable, always)
2. (Optional optimization) Pushes the event directly to the Runtime instance hosting the session

The simplest "push" mechanism is through the harness's `indemn events stream` subscription: the harness is already subscribed to Change Streams for its actor_id, so the kernel just needs the message to appear in the stream. MongoDB Change Streams deliver it within ~50-100ms to the running harness process.

**If lower latency is ever needed**, a direct Runtime-to-instance push mechanism could be added (e.g., via HTTP from the kernel to a known instance endpoint). For MVP, Change Streams are fast enough.

### Customer-facing surface flexibility

The three-layer configuration model supports flexible customer-facing surfaces:

| Configuration layer | Lives on | What it customizes |
|---|---|---|
| **Transport behavior** | Deployment entity | Widget appearance, voice greeting, venue branding, surface-specific settings |
| **Conversation style** | Associate skill | What the agent says, how it handles turns, which tools it uses, conversation flow |
| **Execution environment** | Runtime entity | LLM model, framework version, capacity, infrastructure |

Per-session overrides can happen at any layer. A specific Deployment can override its Associate's LLM (e.g., "use a faster model for this venue"). A specific Associate can override its Runtime's LLM. The merge order is Runtime defaults → Associate override → Deployment override.

This flexibility is already present in the entities — the design doesn't need new mechanism. The three-layer model is just the documentation of HOW flexibility works for customer-facing surfaces.

## Part 6: Handoff

### The model

At any moment, an Interaction has a `handling_actor_id` (and optionally a `handling_role_id`) pointing to whoever is currently driving the conversation. Handoff changes this pointer. The Runtime hosting the Interaction notices the change (via a Change Stream on the Interaction) and switches its internal mode.

Three states a human can be in relative to an Interaction:

1. **Not involved**: no Attention, no presence
2. **Observing**: Attention with purpose=observing. UI subscribes to the Interaction's turns via Change Stream. Real-time view, no handling responsibility.
3. **Handling**: Attention with purpose=real_time_session OR the human is the target of handler_actor_id on the Interaction. The human is driving the conversation; turns are routed to their UI.

Transitions:

- **Not involved → Observing**: human opens the Interaction in their UI. The UI opens an Attention (purpose=observing) so other users see "Cam is watching this." Multiple observers can coexist.
- **Observing → Handling**: human clicks "Take over" or triggers `indemn interaction transfer INT-091 --to cam@indemn.ai`. The kernel updates Interaction.handling_actor_id. The hosting Runtime notices and switches from running the associate in-process to bridging turns through Cam's UI.
- **Handling → Observing or Not involved**: human clicks "Hand back" or "Leave." Reverses.

### Transfer to a specific actor

```bash
indemn interaction transfer INT-091 --to cam@indemn.ai --reason "complex underwriting question"
```

This is an `@exposed` method on the Interaction entity (auto-generated CLI from the entity). It:

1. Updates Interaction.handling_actor_id
2. Clears Interaction.handling_role_id (if set)
3. Emits Interaction:transferred event with correlation_id for audit
4. The emitted event fires watches — including one that notifies the new handler ("You're now handling INT-091")

### Transfer to a role (any available)

```bash
indemn interaction transfer INT-091 --to-role senior_csr --reason "escalation"
```

This sets handling_role_id and clears handling_actor_id. The Runtime bridges turns to the message_queue targeting the role. Any actor with that role can see the conversation in their queue and claim it. When someone claims it, the kernel sets handling_actor_id to the claimant.

### How the Runtime switches modes

The Runtime instance hosting the Interaction subscribes (via its harness's Change Stream) to updates on the Interaction entity. When `handling_actor_id` or `handling_role_id` changes, the Runtime's session logic switches:

**Before handoff (associate handling)**:
- Customer turns from the transport → in-process deepagents agent → response back to transport
- Agent runs in the sandbox using the associate's skills and model

**During handoff**:
- The Runtime's session logic pauses the deepagents session (gracefully — waits for current turn to complete)
- Closes the old Attention record for the associate
- Opens a new Attention for the new handler (human or different associate)
- Notifies the new handler's UI (via their role's queue) that they're now handling INT-091

**After handoff (human handling)**:
- Customer turns from the transport → written to message_queue targeting the human's actor_id
- The human's UI receives turns via Change Stream subscription and renders them
- Human types responses in the UI → UI submits via an entity method (`indemn interaction respond --id INT-091 --text "..."`) → Runtime picks up the response via its own Change Stream subscription and sends on the transport

The Runtime is the persistent bridge. The handler changes; the Runtime's bridging logic swaps modes.

### Human voice handoff: open UX item

For voice handoff specifically — a human taking over a live phone call — the architectural mechanism works the same as chat handoff, but the human needs a voice-capable interface to actually hear and speak with the customer.

**Voice clients for humans are Integrations** (see Part 7). When Cam takes over a voice Interaction, his UI uses his personal voice_client Integration (e.g., a LiveKit browser client) to join the LiveKit room for the Interaction. The old associate session yields; Cam becomes the active voice participant.

The UX question — how exactly a human's browser or mobile app presents the "take over voice call" flow — is out of scope for this artifact. The architectural mechanism supports it; the UI/UX design is a follow-up.

## Part 7: Voice Clients for Humans as Integrations

### The pattern

When a human needs to participate in a voice channel (e.g., taking over a LiveKit voice call), they need a voice client. That voice client is an Integration — specifically, an Integration of `system_type: voice_client` owned by the human actor.

```bash
indemn integration create \
  --owner actor \
  --actor cam@indemn.ai \
  --name "Cam LiveKit Browser" \
  --system-type voice_client \
  --provider livekit_human_client \
  --config '{"device": "browser", "audio": {"echo_cancellation": true}}'
```

The Integration stores Cam's LiveKit identity and client preferences. When Cam takes over a voice call, his UI:

1. Reads his voice_client Integration for the target Interaction's transport type (LiveKit)
2. Requests a room token via an entity method: `indemn interaction get-voice-token --id INT-091 --as cam@indemn.ai`
3. The kernel generates a LiveKit room token scoped to Cam and returns it
4. Cam's UI establishes a LiveKit connection using the token
5. Cam is now a participant in the room; the associate's session yields

Other voice_client providers might exist:
- `provider: twilio_phone` — Cam's phone rings; he answers and is connected to the call via Twilio conferencing
- `provider: sip_client` — SIP-based calling from a desk phone
- `provider: webrtc_custom` — custom WebRTC implementation

All fit under the voice_client Integration type. Same ownership model, same credential handling, same CLI management as any other Integration.

### Why this is clean

- Voice clients for humans use the same Integration primitive as Outlook connections, Stripe connections, LiveKit voice agent integrations. No new concept.
- Per-user client preferences (which device, which audio config) are per-actor Integrations, owned by the individual human.
- Organization-level voice infrastructure (the LiveKit project, the Twilio account) is separately an org-level Integration.
- Rotation, audit, and credential management work uniformly.

## Part 8: CLI Surface

### Auto-generated (no design needed)

Every entity in this artifact (Attention, Runtime, Interaction, Associate with new fields) gets its CLI auto-generated. Every `@exposed` method on these entities becomes a CLI command. Every field becomes a filter/argument on the standard operations.

Representative entity operations (all auto-generated):

```bash
# Attention
indemn attention create/open/close/heartbeat/list/get/status

# Runtime
indemn runtime create/deploy/drain/scale/health/instances/list/get
indemn runtime register-instance/unregister-instance/heartbeat

# Interaction (new methods)
indemn interaction transfer --to/--to-role
indemn interaction respond --text  # for human handling via UI

# Associate (new fields)
indemn associate create --runtime/--llm-config/--prompt/--mode
indemn associate move --to-runtime
```

### New infrastructure CLI commands (need explicit design)

Only one new command is required beyond entity auto-generation:

**`indemn events stream`** — a streaming subscription command backed by MongoDB Change Streams.

```bash
indemn events stream \
  --actor ACTOR-ID \
  [--interaction INTERACTION-ID] \
  [--entity-type Entity]  \
  [--format json-lines|text]
```

- Subscribes to message_queue for the given actor (and optional filters)
- Outputs matching events as JSON lines on stdout as they arrive
- Long-running subprocess; terminated by caller or on signal
- Used by harnesses to receive scoped events for real-time delivery

Implementation: MongoDB Change Stream on message_queue filtered by target_actor_id. One process per harness instance (or one per session, depending on harness implementation).

## Part 9: Worked Examples

### Example 1: EventGuard mid-conversation policy confirmation

**Setup**:
- Runtime RUNTIME-VOICE-001: realtime_voice, deepagents, LiveKit
- Associate QUOTE-ASSISTANT: attached to RUNTIME-VOICE-001
- Watch on Payment:transitioned[to=completed] with active_context scope on application_id
- Watch on Policy:created with active_context scope on application_id

**Flow**:

1. Consumer calls. LiveKit room opens. Voice Runtime instance is activated for the call.
2. Harness loads Associate QUOTE-ASSISTANT, creates Interaction INT-091 (channel_type=voice, linked to Application APP-091 as it's created during the conversation), opens Attention ATT-091 (runtime=RUNTIME-VOICE-001, related_entities includes Application:APP-091).
3. Agent runs, quotes the customer, creates a Payment entity pending.
4. Agent sends Stripe payment form to the chat UI (out of scope for this trace).
5. Customer completes payment. Stripe webhook fires.
6. Webhook handler updates Payment entity, transitioning to "completed".
7. **Payment:transitioned[to=completed] event fires**. Watch matches with active_context scope.
8. **Kernel resolves the scope**: reads Payment.application_id = APP-091. Queries Attentions where related_entities contains Application:APP-091 and status=active. Finds ATT-091 owned by QUOTE-ASSISTANT in RUNTIME-VOICE-001.
9. Kernel writes a message to message_queue with target_actor_id = QUOTE-ASSISTANT's actor_id.
10. Harness's `indemn events stream` subscription picks up the message within ~50ms.
11. Harness delivers the event to the in-process deepagents agent (via `agent.inject_context(event)`).
12. Agent's next turn speaks: "Your payment came through. Let me confirm your policy is being issued right now."
13. Meanwhile, the payment_processor actor watches for Payment:completed unscoped and issues the Policy via a separate workflow.
14. **Policy:created event fires**. Watch matches with active_context scope.
15. Same resolution path. Event reaches the running agent. Agent: "All set! Your policy is confirmed. You'll receive the certificate by email shortly."
16. Customer hangs up. LiveKit room closes. Harness closes Attention, transitions Interaction to "closed".

**Total latency for "all set" confirmation** after Policy:created: ~100-200ms (Change Stream delivery + agent turn generation + TTS). Imperceptible to the user — the agent's confirmation sounds naturally timed.

### Example 2: CRM chat handoff from associate to human

**Setup**:
- Runtime RUNTIME-CHAT-001: realtime_chat, deepagents, WebSocket server
- Associate CRM-ASSISTANT: helps team members with customer briefings
- Cam has role "account_owner" with a watch scoped by organization.primary_owner_id

**Flow**:

1. Cam opens the CRM UI, asks the CRM Assistant "what's the story with INSURICA?"
2. CRM UI opens a WebSocket to RUNTIME-CHAT-001. Harness creates Interaction INT-092 with CRM-ASSISTANT as initial handler. Attention opens.
3. Agent runs, gathers the briefing, presents the story.
4. Cam reads the briefing. Something makes him want to jump in and ask a follow-up more directly. He clicks "Take over."
5. UI sends `indemn interaction transfer INT-092 --to cam@indemn.ai`.
6. Kernel updates Interaction.handling_actor_id = cam. Emits Interaction:transferred event.
7. Harness's Change Stream subscription notices the update. Harness gracefully ends the deepagents session and switches to "bridge to human" mode.
8. Cam now sees the chat interface in handling mode. He types a message.
9. UI submits `indemn interaction respond --id INT-092 --text "..."`.
10. Harness (still holding the WebSocket) picks up the response via its Change Stream and sends the message on the WebSocket.
11. Cam and (hypothetically another user watching on the other end) have a direct conversation through the CRM channel.
12. Cam clicks "Hand back" when done.
13. Kernel updates handling_actor_id back to CRM-ASSISTANT. Harness restarts the deepagents session with the conversation history as context.
14. Agent resumes: "Is there anything else I can help with about INSURICA?"

This entire flow uses existing primitives. No new mechanism beyond Attention + handoff CLI + Runtime's two-mode bridging.

## Part 10: What's Still Open

The following are deferred from this design and need their own focused design sessions or documentation updates:

1. **Bulk operations pattern** (from the synthesis list). EventGuard's 351 deployments and GIC's scheduled bulk updates need a specific pattern: transaction batching, event emission strategy, progress reporting, idempotency, rollback. Interacts with watch coalescing from this artifact.

2. **Inbound webhook dispatch documentation** (from the synthesis list). The Integration artifact needs updating to explicitly cover webhooks as inbound adapter methods.

3. **Pipeline dashboard layer** (from the synthesis list). Base UI design work; uses Attention + message_log + entity state distributions.

4. **Queue health tooling** (from the synthesis list). CLI + UI for monitoring queue depths, integration health, associate performance.

5. **Authentication** (from the synthesis list). Deserves its own session.

6. **Content visibility scoping** (from the CRM retrace). Privacy policy for entities derived from personal Integrations.

7. **Voice handoff UX specifics**. The architectural mechanism works, but the actual flow of "Cam joins a voice call on his browser with one click" needs UI design and LiveKit configuration detail.

8. **Runtime auto-deployment**. When work comes in for a Runtime with no instances, should the kernel auto-deploy, queue the work with a timeout, or fail fast? Probably A or B depending on Runtime status. Design detail.

9. **Runtime health-based dispatch**. When multiple instances of a Runtime exist, which one gets a new session? Simple round-robin for MVP; smarter load-aware dispatch later.

10. **Runtime migration across framework versions**. The CLI supports `indemn associate move --to-runtime ...`. The exact semantics of draining the old, starting the new, and handling in-flight sessions needs a focused playbook.

## Summary of Architectural Additions

| Concept | What it is | Where it lives |
|---|---|---|
| **Attention** | Active working context of an actor on an entity | Bootstrap entity (new) |
| **Runtime** | Deployable host for associate execution | Bootstrap entity (new) |
| **Scoped watches** | Watches with `scope` field for targeting specific actors | Extension to existing watch mechanism |
| **Watch coalescing** | Watches with `coalesce` strategy for batching events | Extension to existing watch mechanism |
| **Interaction.handling_actor_id** | Who is currently driving the conversation | Field on existing Interaction entity |
| **Handoff via transfer command** | `indemn interaction transfer --to/--to-role` | `@exposed` method on Interaction (auto-generated CLI) |
| **Harness pattern** | Thin CLI-based glue code, one image per kind+framework combo | Deployment artifact, not a kernel concept |
| **`indemn events stream`** | Streaming CLI subcommand backed by Change Streams | Infrastructure CLI (one new command) |
| **Voice clients as Integrations** | Human voice participation via voice_client Integrations | Reuses Integration primitive |

### Primitive count unchanged
Six structural primitives: Entity, Message, Actor, Role, Organization, Integration. Attention and Runtime are bootstrap entities, not primitives. The six-primitive story is stable.

### Bootstrap entity list updated
Org, Actor, Role, Integration, **Attention**, **Runtime**. All managed through normal entity CRUD; kernel depends on each for specific core behavior.

## How This Fits the Overall Design

- The **kernel-vs-domain** separation holds. None of this adds domain assumptions. All of it is infrastructure.
- The **CLI-first** philosophy holds. Harnesses use CLI, agents use CLI, humans use CLI. One interface.
- The **everything-is-data** principle holds. Runtimes are data. Attentions are data. Skills, rules, and watches are data. The kernel codebase is the platform; the database is the application.
- The **unified actor model** holds. Humans, associates, and tier 3 developers are all Actors. Handoff between them is a field update on Interaction, not a mechanism change.
- The **"associates are employees"** principle is fully preserved — they use the same queue, the same CLI, the same scoped watch mechanism as humans. Their execution runtime (Runtime entity) is named explicitly, but they're still just Actors from the kernel's perspective.

This design resolves the biggest architectural gaps identified from the retraces. The remaining open items from the synthesis are smaller in scope and can be tackled in parallel or sequentially without blocking further work.
