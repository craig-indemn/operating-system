---
ask: "Implementation specification for Phase 4 (Base UI) and Phase 5 (Real-Time)"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design source of truth"
  - type: artifact
    ref: "2026-04-11-base-ui-operational-surface.md"
    description: "Base UI rendering contract, assistant design"
  - type: artifact
    ref: "2026-04-10-realtime-architecture-design.md"
    description: "Attention, Runtime, harness pattern, scoped watches, handoff"
  - type: artifact
    ref: "2026-04-11-authentication-design.md"
    description: "Full auth — SSO, MFA, platform admin (Phase 4 completion)"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1.md"
    description: "Foundation spec"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-2-3.md"
    description: "Associate execution + integration spec"
---

# Implementation Specification: Phase 4 + Phase 5

## Relationship to Prior Phases

Phases 1-3 produce a working kernel: entities defined, messages flowing, associates processing, integrations connecting. Phases 4-5 add the human surfaces: Phase 4 gives operators a visual interface and completes authentication for real users. Phase 5 enables live conversations (voice, chat) through the harness pattern with real-time event delivery.

---

# Phase 4: Base UI

## What It Produces

The auto-generated operational surface. Operators can log in, see their queue, drill into entities, take actions, see the system update in real time, and interact with the assistant. Adding a new entity type makes it appear in the UI without UI code changes.

## 4.1 Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Framework | React 18+ | Standard, team familiarity, ecosystem |
| Build tool | Vite | Fast builds, HMR for development |
| HTTP client | Built-in fetch + SWR or TanStack Query | Data fetching with caching and revalidation |
| WebSocket | Native WebSocket API | Real-time entity updates |
| Styling | Tailwind CSS | Utility-first, no component library overhead |
| Tables | TanStack Table | Headless, full control over rendering |
| Forms | React Hook Form + Zod | Type-safe form generation from schemas |
| Routing | React Router | Standard |

**No component library.** The base UI auto-generates from entity schemas. A component library's opinions would fight the auto-generation. Tailwind + headless libraries give full control.

## 4.2 Application Structure

```
ui/
  src/
    main.tsx                    # Entry point
    App.tsx                     # Router, auth provider, WebSocket provider
    api/
      client.ts                 # API client (fetch wrapper with auth)
      hooks.ts                  # useEntities, useEntity, useQueue, etc.
      websocket.ts              # WebSocket connection + subscription manager
    auth/
      AuthProvider.tsx           # Auth context (JWT, refresh, logout)
      LoginPage.tsx              # Login form
      useAuth.ts                 # Auth hooks
    layout/
      Shell.tsx                  # App shell (nav, top bar, content area)
      Navigation.tsx             # Left nav (entity types, queue, admin)
      TopBar.tsx                 # Assistant input + user info
    views/
      EntityListView.tsx         # Generic entity list (table)
      EntityDetailView.tsx       # Generic entity detail (form + related)
      QueueView.tsx              # Actor's pending messages
      RoleOverview.tsx           # Aggregate counts per role
    components/
      EntityTable.tsx            # Auto-generated table from field definitions
      EntityForm.tsx             # Auto-generated form from field definitions
      StateIndicator.tsx         # Current state + transition buttons
      FieldRenderer.tsx          # Render a field value by type
      FormField.tsx              # Render a form field by type
      MessageRow.tsx             # Queue item row
      ChangeTimeline.tsx         # Recent changes for an entity
    assistant/
      AssistantInput.tsx         # Slim top-bar input
      AssistantPanel.tsx         # Slide-in conversation panel
      useAssistant.ts            # Assistant state + API calls
    types/
      entity.ts                  # TypeScript types generated from API metadata
  package.json
  vite.config.ts
  tsconfig.json
```

## 4.3 Entity Metadata Endpoint

The API serves entity metadata that the UI uses to auto-generate views.

```python
# kernel/api/meta.py
@router.get("/api/_meta/entities")
async def get_entity_metadata(actor=Depends(get_current_actor)):
    """Return metadata for all entity types the current actor can access."""
    accessible_entities = []
    for entity_name, entity_cls in ENTITY_REGISTRY.items():
        if has_any_permission(actor, entity_name):
            accessible_entities.append({
                "name": entity_name,
                "collection": entity_cls.Settings.name,
                "fields": get_field_metadata(entity_cls),
                "state_machine": getattr(entity_cls, '_state_machine', None),
                "capabilities": getattr(entity_cls, '_activated_capabilities', []),
                "permissions": get_actor_permissions(actor, entity_name),
            })
    return accessible_entities
```

The UI fetches this once at startup and uses it to generate navigation, tables, forms, and action buttons.

## 4.4 Auto-Generated Views

### Entity List View

For each entity type the actor can read: an interactive table with columns derived from field types, filters from common fields, row actions from state transitions and exposed operations.

```tsx
// views/EntityListView.tsx
function EntityListView({ entityMeta }: { entityMeta: EntityMeta }) {
  const { data, isLoading } = useEntities(entityMeta.name);

  const columns = entityMeta.fields
    .filter(f => !f.hidden)
    .map(field => ({
      accessorKey: field.name,
      header: field.label || field.name,
      cell: ({ getValue }) => <FieldRenderer type={field.type} value={getValue()} />,
    }));

  // Add state badge column if state machine exists
  if (entityMeta.state_machine) {
    columns.unshift({
      accessorKey: 'status',
      header: 'Status',
      cell: ({ getValue }) => <StateIndicator state={getValue()} />,
    });
  }

  // Row actions from permissions
  const rowActions = buildRowActions(entityMeta);

  return (
    <EntityTable
      columns={columns}
      data={data}
      rowActions={rowActions}
      onRowClick={(row) => navigate(`/${entityMeta.name.toLowerCase()}/${row.id}`)}
    />
  );
}
```

### Entity Detail View

Form showing all fields with appropriate controls. Current state badge. Transition buttons. Exposed operations as action buttons. Related entities as linked sub-tables. Recent changes from changes collection.

### Queue View

The actor's home screen. Pending messages targeting their roles, sorted by priority and age. Coalesced batches (same correlation_id) render as single rows with drill-down.

```tsx
// views/QueueView.tsx
function QueueView() {
  const { data: messages } = useQueue();

  // Group by correlation_id for display coalescing
  const grouped = groupByCorrelationId(messages);

  return (
    <div>
      <h1>Your Queue</h1>
      {grouped.map(group => (
        group.count === 1
          ? <MessageRow message={group.messages[0]} />
          : <CoalescedRow group={group} />
      ))}
    </div>
  );
}
```

## 4.5 Real-Time Updates via WebSocket

The API server provides a WebSocket endpoint for real-time entity change notifications. The UI subscribes to changes filtered by the current view.

```python
# kernel/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from kernel.auth.jwt import verify_access_token

@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    # Authenticate
    token = websocket.query_params.get("token")
    payload = verify_access_token(token)
    actor_id = payload["actor_id"]
    org_id = payload["org_id"]

    # Subscribe to MongoDB Change Stream filtered by org
    collection = db["message_queue"]  # Or entity collections
    pipeline = [{"$match": {"fullDocument.org_id": org_id}}]

    async with collection.watch(pipeline, full_document="updateLookup") as stream:
        try:
            async for change in stream:
                # Send relevant changes to the client
                await websocket.send_json({
                    "type": "entity_change",
                    "data": serialize_change(change),
                })
        except WebSocketDisconnect:
            pass
```

**WebSocket keepalive**: server sends ping frames every 30 seconds (Railway proxy drops idle connections at 60 seconds).

The UI WebSocket client subscribes on connect and resubscribes on reconnect. On reconnect, the client re-fetches current state (full-state-on-reconnect pattern — simpler than event buffering).

## 4.6 The Assistant

Every human actor has a default associate pre-provisioned with the same permissions. The UI surfaces this as a primary input.

### Top-Bar Input

Slim always-visible input in the top bar. Focused by `/` or `Cmd+K`. One line, always present, not dominant.

### Conversation Panel

On engagement, a panel slides in from the right (~400-500px). Overlay, not modal. Streaming responses. ESC closes (conversation persists).

### Context Awareness

Each turn sends implicit context from the UI:

```typescript
interface AssistantContext {
  view_type: string;            // "EntityList", "EntityDetail", "Queue"
  current_entity?: { type: string; id: string };
  current_filter?: Record<string, any>;
  role_focus?: string;
  recent_actions?: string[];
}
```

### Implementation

The assistant is an API call to the associate execution endpoint. The default associate's skills include all entity skills for the actor's roles. It executes commands through the same API the UI uses.

For Phase 4 MVP: text responses with entity links. Inline entity rendering (tables/forms in the chat) is a UX refinement for later.

## 4.7 Authentication Completion

Phase 1 established basic auth (password + token + JWT). Phase 4 completes the auth design for real users:

### SSO via Integration

```python
# Login flow for SSO
@router.get("/auth/sso/{integration_id}")
async def sso_initiate(integration_id: str):
    integration = await Integration.get(integration_id)
    adapter = get_adapter_class(integration.provider, integration.provider_version)
    redirect_url = await adapter.auth_initiate(
        redirect_uri=f"{settings.api_url}/auth/sso/{integration_id}/callback"
    )
    return RedirectResponse(redirect_url)

@router.get("/auth/sso/{integration_id}/callback")
async def sso_callback(integration_id: str, code: str, state: str):
    integration = await Integration.get(integration_id)
    adapter = get_adapter_class(integration.provider, integration.provider_version)
    user_info = await adapter.auth_callback(code, state)

    # Look up or provision actor
    actor = await Actor.find_one({
        "email": user_info["email"],
        "org_id": integration.org_id,
    })
    if not actor:
        raise HTTPException(403, "No actor found for this email")

    # Create session + issue JWT
    session = await create_session(actor, method="sso")
    tokens = issue_tokens(session)
    return tokens
```

### MFA (TOTP)

Implemented via pyotp. TOTP secret stored in Secrets Manager. Challenge flow during login.

### Platform Admin Cross-Org

Platform admin sessions: time-limited (4h default), audited in target org's changes collection, identity stays as the Indemn actor. Implemented as a special session type with `platform_admin_context` field.

### Revocation Cache

In-memory per API instance, invalidated via MongoDB Change Stream on Session status changes. Bootstrapped on startup from recently revoked sessions.

## 4.8 Kernel Entity Views

The seven kernel entities (Organization, Actor, Role, Integration, Attention, Runtime, Session) render with the same auto-generation as domain entities. Row actions: pause, drain, rotate credentials, close attention, transfer interaction, revoke session.

## Phase 4 Acceptance Criteria

```
1. OPERATOR CAN LOG IN
   - Login with password
   - Login with SSO (via Integration)
   - MFA challenge (TOTP) when required by role
   - JWT issued, stored client-side

2. QUEUE VIEW
   - Actor sees pending messages for their roles
   - Messages sorted by priority then age
   - Coalesced batches displayed as single rows
   - Claim action works (message transitions to processing)

3. ENTITY LIST VIEW
   - Tables auto-generated from entity field definitions
   - Columns, filters, row actions derived from schema + permissions
   - Sort and pagination work

4. ENTITY DETAIL VIEW
   - Forms auto-generated from field definitions
   - State machine displayed as current state + transition buttons
   - Transitions work (state changes, watches fire)
   - Related entities linked for drill-through
   - Recent changes shown from changes collection

5. REAL-TIME UPDATES
   - List and detail views update live via WebSocket
   - Entity state change in one tab appears immediately in another
   - Queue items appear without refresh

6. ASSISTANT
   - Top-bar input visible on every view
   - Conversation panel opens on engagement
   - Assistant can answer questions about current entity
   - Assistant can execute operations (via API)
   - Context from current view informs responses

7. NEW ENTITY TYPE APPEARS AUTOMATICALLY
   - Add a new entity definition
   - Restart API server
   - UI navigation shows the new entity type
   - List and detail views work for it
   - No UI code changes required

8. KERNEL ENTITY VIEWS
   - Organization, Actor, Role, Integration, Attention, Runtime, Session
   - All visible as tables with appropriate row actions
   - Operations staff can manage the system through the UI
```

---

# Phase 5: Real-Time

## What It Produces

Live conversations — voice, chat, SMS — running through the OS. The Attention kernel entity tracks active sessions. The Runtime kernel entity manages execution environments. Harnesses bridge agent frameworks to the kernel via CLI. Scoped watches deliver mid-conversation events. Handoff between actors works.

## 5.1 Attention Entity (Kernel Entity — Already Defined in Phase 1)

The Attention entity was defined in Phase 1 as a kernel entity. Phase 5 activates its real-time-specific behaviors:
- **Heartbeat maintenance** with TTL expiration
- **Scope resolution** for active_context watches
- **Zombie detection** for crashed sessions
- **Capacity tracking** per Runtime

The heartbeat bypass (no audit trail for heartbeats) is implemented in `save_tracked()` with a special path that skips changes collection writes for heartbeat-only updates.

## 5.2 Runtime Entity (Kernel Entity — Already Defined in Phase 1)

The Runtime entity was defined in Phase 1. Phase 5 deploys actual Runtime instances:

```bash
# Create a voice runtime
indemn runtime create \
  --name "Voice Production" \
  --kind realtime_voice \
  --framework deepagents \
  --framework-version 1.2.0 \
  --transport livekit \
  --deployment-image indemn/runtime-voice-deepagents:1.2.0 \
  --deployment-platform railway

# Deploy
indemn runtime transition RUNTIME-001 --to deploying
# Railway starts the container
# Runtime registers itself as active
indemn runtime transition RUNTIME-001 --to active
```

## 5.3 Harness Pattern

Each harness is a thin deployable (~60-100 lines of glue code) bridging a specific agent framework + transport to the OS via CLI.

### Voice Harness (deepagents + LiveKit)

```python
# harnesses/voice-deepagents/main.py
"""
Voice harness: LiveKit Agents + deepagents + Indemn OS CLI.
One harness serves any Associate of matching kind by loading config at session start.
"""
import asyncio
import subprocess
import json
from livekit.agents import Agent, AgentSession
from deepagents import create_deep_agent

# CLI wrapper for OS operations
def cli(command: str) -> dict:
    result = subprocess.run(
        ["indemn"] + command.split(),
        capture_output=True, text=True,
        env={**os.environ, "INDEMN_API_URL": os.environ["INDEMN_API_URL"]},
    )
    return json.loads(result.stdout) if result.stdout else {"error": result.stderr}

class IndemnVoiceAgent(Agent):
    async def on_session_start(self, session: AgentSession):
        # Load associate config from OS
        deployment_id = session.metadata.get("deployment_id")
        deployment = cli(f"deployment get {deployment_id}")
        associate_id = deployment["associate_id"]
        associate = cli(f"actor get {associate_id}")

        # Open Attention (real-time session)
        interaction = cli(f"interaction create --channel voice --deployment {deployment_id}")
        attention = cli(
            f"attention open --actor {associate_id} "
            f"--target-entity Interaction:{interaction['id']} "
            f"--purpose real_time_session "
            f"--runtime {os.environ['RUNTIME_ID']}"
        )
        self.interaction_id = interaction["id"]
        self.attention_id = attention["id"]
        self.associate = associate

        # Load skills
        skills = cli(f"skill get-multi {' '.join(associate['skills'])}")

        # Create deep agent with skills
        self.agent = create_deep_agent(
            skills=skills,
            model=associate.get("llm_config", {}).get("model", "claude-sonnet-4-6"),
        )

        # Start heartbeat loop
        asyncio.create_task(self._heartbeat_loop())

        # Start event listener for mid-conversation events
        asyncio.create_task(self._event_listener())

    async def on_message(self, message: str):
        # Process via deep agent
        response = await self.agent.process(message, context={
            "interaction_id": self.interaction_id,
        })

        # The agent may have executed CLI commands that changed entities
        # Those changes flow through watches → messages → potentially back here via events

        return response

    async def on_session_end(self):
        cli(f"attention close {self.attention_id}")
        cli(f"interaction transition {self.interaction_id} --to closed")

    async def _heartbeat_loop(self):
        while True:
            cli(f"attention heartbeat {self.attention_id}")
            await asyncio.sleep(30)

    async def _event_listener(self):
        """Listen for scoped events targeting this actor."""
        # Use the events stream CLI command
        process = await asyncio.create_subprocess_exec(
            "indemn", "events", "stream",
            "--actor", self.associate["id"],
            "--interaction", self.interaction_id,
            stdout=asyncio.subprocess.PIPE,
        )
        async for line in process.stdout:
            event = json.loads(line)
            # Feed event to the agent as a proactive notification
            await self.agent.handle_event(event)
```

### Chat Harness (deepagents + WebSocket)

Similar structure but with WebSocket transport instead of LiveKit. The harness serves a WebSocket endpoint, creates Interaction entities on connection, and bridges messages between the WebSocket and the deep agent.

## 5.4 `indemn events stream` Command

The one CLI infrastructure command that's not auto-generated from entity definitions. Streams events as JSON lines on stdout via MongoDB Change Streams.

```python
# kernel/cli/events.py
@events_app.command("stream")
def stream_events(
    actor: str = typer.Option(None),
    interaction: str = typer.Option(None),
    entity_type: str = typer.Option(None),
):
    """Stream matching events as JSON lines on stdout.
    Subscribes to MongoDB Change Stream on message_queue."""
    client = get_client()
    response = client.get(
        "/api/_stream/events",
        params={"actor": actor, "interaction": interaction, "entity_type": entity_type},
        stream=True,
    )
    for line in response.iter_lines():
        typer.echo(line)
```

Server-side, this is a Server-Sent Events (SSE) endpoint backed by a Change Stream:

```python
# kernel/api/events.py
from fastapi.responses import StreamingResponse

@router.get("/api/_stream/events")
async def stream_events(
    actor: str = None,
    interaction: str = None,
    actor_context=Depends(get_current_actor),
):
    async def event_generator():
        pipeline = build_change_stream_pipeline(actor, interaction, actor_context.org_id)
        async with message_queue_collection.watch(pipeline) as stream:
            async for change in stream:
                yield json.dumps(change["fullDocument"]) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
```

## 5.5 Scoped Watch Resolution

Phase 1 defined watches with optional `scope` fields. Phase 5 implements the two resolution types.

### field_path Resolution

```python
# kernel/watch/scope.py
async def resolve_field_path(scope: dict, entity, session) -> Optional[ObjectId]:
    """Traverse entity relationships to resolve an actor_id."""
    path = scope["path"]  # e.g., "organization.primary_owner_id"
    parts = path.split(".")

    current = entity.dict()
    for i, part in enumerate(parts):
        if part in current and isinstance(current[part], ObjectId):
            # This is a reference — load the related entity
            # Determine entity type from the relationship definition
            related = await load_related_entity(current[part])
            current = related
        elif part in current:
            return current[part]  # Final value — should be an actor_id
        else:
            return None  # Path doesn't resolve

    return None
```

### active_context Resolution

```python
async def resolve_active_context(scope: dict, entity, session) -> list[ObjectId]:
    """Find actors with Attention records covering this entity."""
    traverses = scope["traverses"]  # e.g., "application_id"
    related_id = getattr(entity, traverses, None)
    if not related_id:
        return []

    # Query Attention for active records with matching related_entities
    attentions = await Attention.find({
        "related_entities.id": related_id,
        "status": "active",
        "expires_at": {"$gt": datetime.utcnow()},
    }).to_list()

    return [att.actor_id for att in attentions]
```

When active_context resolves to an actor with a `runtime_id` on their Attention, the kernel ALSO notifies the Runtime instance for in-process delivery (via the events stream that the harness is listening on).

## 5.6 Handoff

Transfer between actors on a live interaction.

```python
# API endpoint for interaction transfer
@router.post("/api/interactions/{interaction_id}/transfer")
async def transfer_interaction(
    interaction_id: str,
    to_actor: str = None,
    to_role: str = None,
    actor=Depends(get_current_actor),
):
    interaction = await Interaction.get(interaction_id)

    if to_actor:
        interaction.handling_actor_id = ObjectId(to_actor)
    elif to_role:
        interaction.handling_role_id = to_role
        interaction.handling_actor_id = None  # Any actor with the role can claim

    await interaction.save_tracked(
        actor_id=str(actor.id),
        method="transfer",
    )

    # The Runtime watches for changes on Interaction via Change Stream
    # It detects the handling_actor_id change and switches modes
    return {"status": "transferred"}
```

Observation is a first-class state: a human opens an Attention with `purpose=observing` on an Interaction. They see the conversation in real time without handling.

## Phase 5 Acceptance Criteria

```
1. CHAT SESSION END-TO-END
   - Consumer opens a chat session (WebSocket)
   - Interaction entity created
   - Associate handles the conversation in real time
   - Entity operations during conversation update state and trigger watches
   - Conversation ends, Attention closed, Interaction transitioned to closed

2. MID-CONVERSATION EVENT DELIVERY
   - During an active conversation, a scoped event occurs
   - (e.g., Payment completes for the Application linked to the Interaction)
   - The running associate receives the event via events stream
   - Associate sends proactive message to the consumer
   - ("Your policy is confirmed!")

3. SCOPED WATCH — FIELD PATH
   - Watch with field_path scope
   - Event fires for an entity with a related actor reference
   - Only the referenced actor receives the message

4. SCOPED WATCH — ACTIVE CONTEXT
   - Watch with active_context scope
   - Event fires for an entity related to an active Attention
   - Only the actor holding the Attention receives the message

5. HANDOFF — ASSOCIATE TO HUMAN
   - Human observes an Interaction (Attention purpose=observing)
   - Human transfers the Interaction to themselves
   - Runtime switches from associate-in-process to human-via-queue
   - Human takes over the conversation

6. HANDOFF — HUMAN TO ASSOCIATE
   - Human handling an Interaction transfers to a role
   - Associate with that role claims and continues

7. HARNESS USES CLI ONLY
   - All harness-to-kernel communication via CLI subprocess
   - No direct MongoDB access from harness
   - No Python SDK dependency

8. RUNTIME LIFECYCLE
   - Create Runtime entity
   - Deploy harness container
   - Runtime registers as active
   - Associates assigned to Runtime serve sessions
   - Drain Runtime (finish existing, no new sessions)
   - Stop Runtime

9. ATTENTION LIFECYCLE
   - Open Attention on session start
   - Heartbeat maintains TTL
   - Heartbeats stop → Attention expires automatically
   - Expired Attentions cleaned up by background process
```

## 5.7 Open Questions

1. **Voice framework choice.** The spec assumes deepagents + LiveKit Agents. The actual framework used for Indemn's voice system today is voice-livekit (Jonathan's work). The harness pattern is framework-agnostic — the specific framework choice is made when building the first voice harness.

2. **Chat WebSocket server placement.** The chat harness runs its own WebSocket server. This is a separate Railway service from the API server. Consumer-facing WebSocket connections go to the chat harness, not the API server's WebSocket endpoint (which is for the base UI's real-time updates).

3. **SMS harness.** SMS is a webhook-based channel (Twilio sends webhook on inbound message). This is closer to the Integration webhook pattern than the harness pattern. The SMS "harness" may be a Twilio adapter on the Integration entity rather than a separate deployable runtime. Design choice during implementation.
