---
ask: "Consolidated implementation specification for Phase 4 (Base UI) and Phase 5 (Real-Time) — resolving all 24 applicable gaps"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design-level source of truth"
  - type: artifact
    ref: "2026-04-14-impl-spec-gaps.md"
    description: "Gap identification — this resolves G-32 through G-51, G-58, G-59, G-65, G-87"
  - type: artifact
    ref: "2026-04-11-base-ui-operational-surface.md"
    description: "Rendering contract, assistant design, real-time updates"
  - type: artifact
    ref: "2026-04-11-authentication-design.md"
    description: "Full auth — Session, JWT, 5 methods, MFA, platform admin, recovery"
  - type: artifact
    ref: "2026-04-10-realtime-architecture-design.md"
    description: "Attention, Runtime, harness pattern, scoped watches, handoff"
  - type: artifact
    ref: "2026-04-13-documentation-sweep.md"
    description: "owner_actor_id, content visibility, webhook dispatch"
  - type: verification
    description: "This document supersedes 2026-04-14-impl-spec-phase-4-5.md"
---

# Implementation Specification: Phase 4 + Phase 5 (Consolidated)

**This document supersedes `2026-04-14-impl-spec-phase-4-5.md`.**

## Relationship to Prior Phases

Phases 1-3 produce a working kernel: entities defined, messages flowing, associates processing via Temporal, integrations connecting to external systems. Phase 4 adds the human visual surface and completes authentication for real users. Phase 5 enables live conversations through the harness pattern with real-time event delivery.

## What Is NOT in Phase 4+5 (Explicitly Deferred)

- Custom per-org dashboards (auto-generation covers MVP)
- DashboardConfig, AlertConfig, Widget kernel entities (post-MVP)
- Active alerting (watches on kernel entities with notification Integrations — post-MVP)
- WebAuthn / passkeys (TOTP sufficient for MVP)
- Per-operation MFA re-verification `requires_fresh_mfa` (session-level MFA sufficient)
- Billing, plans, email domain verification for Tier 3 (post-MVP)
- Assistant inline entity rendering (text responses with entity links for MVP)
- Collaborative editing / CRDTs (last-write-wins with optimistic locking)

---

# Phase 4: Base UI

## 4.1 Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Framework | React 18+ | Standard, ecosystem |
| Build | Vite | Fast builds, HMR |
| Data fetching | TanStack Query (React Query) | Caching, revalidation, optimistic updates |
| Tables | TanStack Table | Headless, full control |
| Forms | React Hook Form + Zod | Type-safe form generation from schemas |
| Routing | React Router v6 | Standard |
| Styling | Tailwind CSS | Utility-first, no component library opinions fighting auto-generation |
| WebSocket | Native WebSocket API | Real-time entity updates |
| HTTP | fetch API | Standard, no extra dependency |

**No component library.** The UI auto-generates from entity schemas. A component library's opinions would fight the auto-generation. Tailwind + headless libraries give full control.

## 4.2 Application Structure

```
ui/
├── src/
│   ├── main.tsx
│   ├── App.tsx                        # Router, providers, shell
│   ├── api/
│   │   ├── client.ts                  # fetch wrapper with auth
│   │   ├── hooks.ts                   # useEntities, useEntity, useQueue, useMeta
│   │   ├── websocket.ts              # WebSocket connection + subscription manager [G-34]
│   │   └── types.ts                   # TypeScript types from API metadata
│   ├── auth/
│   │   ├── AuthProvider.tsx           # Auth context (JWT storage, refresh, logout)
│   │   ├── LoginPage.tsx              # Login form (password + SSO provider selection)
│   │   ├── MfaChallenge.tsx           # TOTP input [G-36]
│   │   ├── useAuth.ts                 # Auth hooks
│   │   └── PasswordReset.tsx          # Password reset flow [G-38]
│   ├── layout/
│   │   ├── Shell.tsx                  # App shell (nav, top bar, content)
│   │   ├── Navigation.tsx             # Left nav (entity types, queue, admin)
│   │   ├── TopBar.tsx                 # Assistant input + user + role indicator
│   │   └── StatusBanner.tsx           # Dependency health banner [G-87]
│   ├── views/
│   │   ├── EntityListView.tsx         # Generic entity list table
│   │   ├── EntityDetailView.tsx       # Generic entity detail form
│   │   ├── QueueView.tsx              # Actor's pending messages
│   │   ├── RoleOverview.tsx           # Aggregate counts per role
│   │   ├── CascadeViewer.tsx          # Nested table by correlation_id
│   │   └── AuthEventsView.tsx         # Auth audit events [G-41]
│   ├── components/
│   │   ├── EntityTable.tsx            # Auto-generated table from metadata
│   │   ├── EntityForm.tsx             # Auto-generated form from metadata
│   │   ├── FieldRenderer.tsx          # Render field value by type [G-32]
│   │   ├── FormField.tsx              # Render form control by type [G-32]
│   │   ├── StateIndicator.tsx         # Current state badge + transition buttons
│   │   ├── MessageRow.tsx             # Queue item row
│   │   ├── CoalescedRow.tsx           # Grouped queue items by correlation_id
│   │   ├── ChangeTimeline.tsx         # Recent changes for an entity
│   │   ├── PipelineMetrics.tsx        # State distribution, throughput, dwell time
│   │   └── IntegrationHealth.tsx      # Integration status table
│   ├── assistant/
│   │   ├── AssistantInput.tsx         # Slim top-bar input
│   │   ├── AssistantPanel.tsx         # Slide-in conversation panel
│   │   └── useAssistant.ts           # Assistant state, API calls, event subscription
│   └── hooks/
│       ├── useEntityMeta.ts           # Load and cache entity metadata
│       ├── useRealtime.ts             # WebSocket subscription management
│       └── usePermissions.ts          # Permission-aware rendering
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## 4.3 Field Type → Form Control Mapping [G-32]

The rendering contract that makes auto-generation concrete.

```typescript
// components/FieldRenderer.tsx — display values
const FIELD_RENDERERS: Record<string, React.FC<{value: any}>> = {
  str:       ({ value }) => <span>{value}</span>,
  int:       ({ value }) => <span>{Number(value).toLocaleString()}</span>,
  float:     ({ value }) => <span>{Number(value).toFixed(2)}</span>,
  decimal:   ({ value }) => <span>{Number(value).toLocaleString(undefined, {minimumFractionDigits: 2})}</span>,
  bool:      ({ value }) => <span className={value ? "text-green-600" : "text-gray-400"}>{value ? "Yes" : "No"}</span>,
  date:      ({ value }) => <span>{new Date(value).toLocaleDateString()}</span>,
  datetime:  ({ value }) => <span>{new Date(value).toLocaleString()}</span>,
  objectid:  ({ value, meta }) => meta?.relationship_target
    ? <a href={`/${meta.relationship_target.toLowerCase()}s/${value}`} className="text-blue-600 underline">{value}</a>
    : <span className="font-mono text-sm">{value}</span>,
  list:      ({ value }) => <span>{Array.isArray(value) ? value.join(", ") : ""}</span>,
  dict:      ({ value }) => <pre className="text-xs bg-gray-50 p-1 rounded">{JSON.stringify(value, null, 2)}</pre>,
  enum:      ({ value }) => <span className="px-2 py-0.5 bg-gray-100 rounded text-sm">{value}</span>,
};

// components/FormField.tsx — editable controls
const FORM_CONTROLS: Record<string, React.FC<FormFieldProps>> = {
  str:       (props) => <input type="text" {...register(props.name)} className="..." />,
  int:       (props) => <input type="number" step="1" {...register(props.name)} />,
  float:     (props) => <input type="number" step="0.01" {...register(props.name)} />,
  decimal:   (props) => <input type="number" step="0.01" {...register(props.name)} />,
  bool:      (props) => <input type="checkbox" {...register(props.name)} />,
  date:      (props) => <input type="date" {...register(props.name)} />,
  datetime:  (props) => <input type="datetime-local" {...register(props.name)} />,
  objectid:  (props) => <EntityPicker entityType={props.meta.relationship_target} {...register(props.name)} />,
  list:      (props) => <MultiValueInput {...register(props.name)} />,
  dict:      (props) => <JsonEditor {...register(props.name)} />,
  enum:      (props) => (
    <select {...register(props.name)}>
      {props.meta.enum_values?.map(v => <option key={v} value={v}>{v}</option>)}
    </select>
  ),
};

// EntityPicker — search + select for relationship fields
function EntityPicker({ entityType, ...props }) {
  // Fetches from /api/{entityType}s?search=... with debounce
  // Renders a searchable dropdown
}

// MultiValueInput — for list fields
function MultiValueInput(props) {
  // Renders chips with add/remove
}

// JsonEditor — for dict fields
function JsonEditor(props) {
  // Renders a textarea with JSON validation
  // Future: CodeMirror with JSON syntax highlighting
}
```

## 4.4 Entity Metadata Endpoint — Full Contract [G-33]

Phase 1 defined the basic endpoint. Phase 4 extends it with everything the UI needs.

```python
# Addition to kernel/api/meta.py

@meta_router.get("/entities/{entity_name}")
async def get_entity_detail_metadata(entity_name: str, actor=Depends(get_current_actor)):
    """Full metadata for a specific entity type — everything the UI needs
    to auto-generate list views, detail views, and forms."""
    cls = ENTITY_REGISTRY.get(entity_name)
    if not cls:
        raise HTTPException(404)

    # Get field metadata
    fields = []
    defn = await EntityDefinition.find_one({"name": entity_name})
    if defn:
        for fname, fdef in defn.fields.items():
            fields.append({
                "name": fname,
                "type": fdef.type,
                "required": fdef.required,
                "default": fdef.default,
                "enum_values": fdef.enum_values,
                "description": fdef.description,
                "is_state_field": fdef.is_state_field,
                "is_relationship": fdef.is_relationship,
                "relationship_target": fdef.relationship_target,
                "indexed": fdef.indexed,
                "unique": fdef.unique,
            })
    else:
        # Kernel entity — derive from Pydantic model fields
        for fname, finfo in cls.model_fields.items():
            if fname.startswith("_"):
                continue
            fields.append({
                "name": fname,
                "type": _pydantic_type_to_string(finfo.annotation),
                "required": finfo.is_required(),
                "default": finfo.default if finfo.default is not None else None,
                "enum_values": _extract_enum_values(finfo.annotation),
                "description": finfo.description,
            })

    # State machine with current-state-aware transitions
    state_machine = getattr(cls, '_state_machine', None)

    # Capabilities
    capabilities = []
    for cap in getattr(cls, '_activated_capabilities', []):
        cap_dict = cap.dict() if hasattr(cap, 'dict') else cap
        capabilities.append({
            "name": cap_dict.get("capability"),
            "cli_command": f"indemn {entity_name.lower()} {cap_dict.get('capability', '').replace('_', '-')} <id> --auto",
        })

    # @exposed methods (kernel entities only)
    exposed_methods = []
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name, None)
        if attr and getattr(attr, '_exposed', False):
            exposed_methods.append({
                "name": attr._exposed_name,
                "cli_command": f"indemn {entity_name.lower()} {attr._exposed_name.replace('_', '-')} <id>",
            })

    # Permissions for the current actor
    permissions = {
        "read": _check_permission(actor, entity_name, "read"),
        "write": _check_permission(actor, entity_name, "write"),
    }

    return {
        "name": entity_name,
        "collection": cls.Settings.name if hasattr(cls, 'Settings') else entity_name.lower() + "s",
        "is_kernel_entity": getattr(cls, '_is_kernel_entity', False),
        "fields": fields,
        "state_machine": state_machine,
        "capabilities": capabilities,
        "exposed_methods": exposed_methods,
        "permissions": permissions,
    }
```

## 4.5 Auto-Generated Views

### Entity List View

```tsx
// views/EntityListView.tsx
function EntityListView({ entityName }: { entityName: string }) {
  const { data: meta } = useEntityMeta(entityName);
  const { data: entities, isLoading } = useEntities(entityName);
  const { subscribe } = useRealtime();

  // Subscribe to real-time updates for this entity type
  useEffect(() => {
    if (meta) {
      subscribe({ entity_type: entityName });
    }
    return () => unsubscribe();
  }, [entityName]);

  if (!meta) return <Loading />;

  // Build columns from field metadata
  const columns = meta.fields
    .filter(f => !f.name.startsWith("_") && f.name !== "org_id")
    .slice(0, 8) // Limit columns for readability
    .map(field => ({
      accessorKey: field.name,
      header: field.description || field.name.replace(/_/g, " "),
      cell: ({ getValue }) => (
        <FieldRenderer type={field.type} value={getValue()} meta={field} />
      ),
    }));

  // Add state badge as first column if state machine exists
  if (meta.state_machine) {
    columns.unshift({
      accessorKey: "status",
      header: "Status",
      cell: ({ getValue }) => <StateIndicator state={getValue()} />,
    });
  }

  // Row actions from permissions + state machine + capabilities
  const rowActions = [];
  if (meta.permissions.write && meta.state_machine) {
    rowActions.push({ label: "Transition...", action: "transition" });
  }
  for (const cap of meta.capabilities || []) {
    rowActions.push({ label: cap.name.replace(/_/g, " "), action: `capability:${cap.name}` });
  }
  for (const method of meta.exposed_methods || []) {
    rowActions.push({ label: method.name.replace(/_/g, " "), action: `method:${method.name}` });
  }

  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">{entityName} List</h1>
      <EntityTable
        columns={columns}
        data={entities || []}
        rowActions={rowActions}
        onRowClick={(row) => navigate(`/${entityName.toLowerCase()}s/${row._id}`)}
        // Filters, pagination, sorting handled by TanStack Table
      />
    </div>
  );
}
```

### Entity Detail View

```tsx
// views/EntityDetailView.tsx
function EntityDetailView({ entityName, entityId }: Props) {
  const { data: meta } = useEntityMeta(entityName);
  const { data: entity, refetch } = useEntity(entityName, entityId);
  const { data: changes } = useChanges(entityName, entityId);
  const { subscribe } = useRealtime();

  // Subscribe to real-time updates for this specific entity
  useEffect(() => {
    subscribe({ entity_type: entityName, entity_id: entityId });
    return () => unsubscribe();
  }, [entityId]);

  if (!meta || !entity) return <Loading />;

  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Main content: form */}
      <div className="col-span-2">
        <EntityForm
          meta={meta}
          entity={entity}
          onSave={async (data) => {
            await apiClient.put(`/api/${entityName.toLowerCase()}s/${entityId}`, data);
            refetch();
          }}
        />
      </div>

      {/* Sidebar: state + actions + changes */}
      <div className="space-y-4">
        {/* Current state + transition buttons */}
        {meta.state_machine && (
          <StateIndicator
            state={entity.status || entity.stage}
            availableTransitions={meta.state_machine[entity.status || entity.stage] || []}
            onTransition={async (to, reason) => {
              await apiClient.post(
                `/api/${entityName.toLowerCase()}s/${entityId}/transition`,
                { to, reason }
              );
              refetch();
            }}
            canTransition={meta.permissions.write}
          />
        )}

        {/* Capability and @exposed method buttons */}
        {meta.capabilities?.map(cap => (
          <button key={cap.name} onClick={() => executeCapability(cap.name, entityId)}>
            {cap.name.replace(/_/g, " ")}
          </button>
        ))}

        {/* Related entities */}
        {meta.fields
          .filter(f => f.is_relationship && entity[f.name])
          .map(f => (
            <a key={f.name} href={`/${f.relationship_target.toLowerCase()}s/${entity[f.name]}`}>
              {f.relationship_target}: {entity[f.name]}
            </a>
          ))
        }

        {/* Recent changes */}
        <ChangeTimeline changes={changes || []} />
      </div>
    </div>
  );
}
```

### Queue View

```tsx
// views/QueueView.tsx
function QueueView() {
  const { data: messages } = useQueue();
  const { subscribe } = useRealtime();

  // Subscribe to queue changes
  useEffect(() => {
    subscribe({ collection: "message_queue" });
  }, []);

  // Group by correlation_id for display coalescing (UI concern, not kernel)
  const groups = useMemo(() => {
    if (!messages) return [];
    const byCorrelation: Record<string, Message[]> = {};
    for (const msg of messages) {
      const key = msg.correlation_id;
      if (!byCorrelation[key]) byCorrelation[key] = [];
      byCorrelation[key].push(msg);
    }
    return Object.entries(byCorrelation).map(([corrId, msgs]) => ({
      correlation_id: corrId,
      messages: msgs,
      count: msgs.length,
      representative: msgs[0],
    }));
  }, [messages]);

  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Your Queue</h1>
      {groups.map(group => (
        group.count === 1 ? (
          <MessageRow
            key={group.representative._id}
            message={group.representative}
            onClaim={() => claimMessage(group.representative._id)}
          />
        ) : (
          <CoalescedRow
            key={group.correlation_id}
            group={group}
            onExpand={() => setExpandedCorrelation(group.correlation_id)}
          />
        )
      ))}
    </div>
  );
}
```

## 4.6 Real-Time Updates via WebSocket [G-34]

### WebSocket Connection Manager

```typescript
// api/websocket.ts

interface Subscription {
  id: string;
  filter: {
    entity_type?: string;
    entity_id?: string;
    collection?: string;
  };
  callback: (change: any) => void;
}

class WebSocketManager {
  private ws: WebSocket | null = null;
  private subscriptions: Map<string, Subscription> = new Map();
  private reconnectAttempts = 0;
  private pingInterval: number | null = null;

  connect(token: string) {
    const url = `${API_WS_URL}/ws?token=${token}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      // Send current subscriptions to server
      this.resyncSubscriptions();
      // Start keepalive pings (Railway drops idle connections at 60s)
      this.pingInterval = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000); // 30-second pings
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "pong") return;
      // Route to matching subscriptions
      for (const sub of this.subscriptions.values()) {
        if (this.matchesFilter(data, sub.filter)) {
          sub.callback(data);
        }
      }
    };

    this.ws.onclose = () => {
      if (this.pingInterval) clearInterval(this.pingInterval);
      // Reconnect with exponential backoff
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      this.reconnectAttempts++;
      setTimeout(() => this.connect(token), delay);
    };
  }

  subscribe(filter: Subscription["filter"], callback: (change: any) => void): string {
    const id = crypto.randomUUID();
    this.subscriptions.set(id, { id, filter, callback });
    // Tell server about new subscription [G-34]
    this.sendSubscription(id, filter);
    return id;
  }

  unsubscribe(id: string) {
    this.subscriptions.delete(id);
    // Tell server to remove subscription
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "unsubscribe", subscription_id: id }));
    }
  }

  // When filters change (user changes page, applies filters) [G-34]
  updateSubscription(id: string, newFilter: Subscription["filter"]) {
    const sub = this.subscriptions.get(id);
    if (sub) {
      sub.filter = newFilter;
      this.sendSubscription(id, newFilter);
    }
  }

  private sendSubscription(id: string, filter: Subscription["filter"]) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "subscribe", subscription_id: id, filter }));
    }
  }

  private resyncSubscriptions() {
    // On reconnect: re-send all active subscriptions
    // Client then re-fetches full state (full-state-on-reconnect pattern)
    for (const sub of this.subscriptions.values()) {
      this.sendSubscription(sub.id, sub.filter);
    }
  }

  private matchesFilter(data: any, filter: Subscription["filter"]): boolean {
    if (filter.entity_type && data.entity_type !== filter.entity_type) return false;
    if (filter.entity_id && data.entity_id !== filter.entity_id) return false;
    if (filter.collection && data.collection !== filter.collection) return false;
    return true;
  }
}

export const wsManager = new WebSocketManager();
```

### Server-Side WebSocket Handler [G-34]

```python
# kernel/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from kernel.auth.jwt import verify_access_token
from kernel.db import get_database
import asyncio, orjson

# Track active subscriptions per connection
_connections: dict[str, dict] = {}  # connection_id → {ws, subscriptions, org_id}

@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    try:
        payload = verify_access_token(token)
    except Exception:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    connection_id = str(uuid4())
    org_id = payload["org_id"]

    _connections[connection_id] = {
        "ws": websocket,
        "subscriptions": {},
        "org_id": org_id,
    }

    try:
        # Start Change Stream watcher for this connection
        watcher_task = asyncio.create_task(
            _watch_changes(connection_id, org_id, websocket)
        )

        # Handle incoming messages (subscribe/unsubscribe/ping)
        async for data in websocket.iter_text():
            msg = orjson.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg.get("type") == "subscribe":
                _connections[connection_id]["subscriptions"][msg["subscription_id"]] = msg["filter"]
            elif msg.get("type") == "unsubscribe":
                _connections[connection_id]["subscriptions"].pop(msg.get("subscription_id"), None)

    except WebSocketDisconnect:
        pass
    finally:
        watcher_task.cancel()
        _connections.pop(connection_id, None)

async def _watch_changes(connection_id: str, org_id: str, websocket: WebSocket):
    """Watch MongoDB Change Streams and push matching changes to the client.
    Filter-aware: only sends changes matching active subscriptions. [G-34]"""
    db = get_database()

    # Watch the entities collections + message_queue for this org
    pipeline = [
        {"$match": {"fullDocument.org_id": org_id}},
    ]

    # Watch multiple collections by using the database-level change stream
    async with db.watch(pipeline, full_document="updateLookup") as stream:
        async for change in stream:
            doc = change.get("fullDocument", {})
            ns = change.get("ns", {})
            collection = ns.get("coll", "")

            # Check against active subscriptions for this connection
            conn = _connections.get(connection_id)
            if not conn:
                break

            for sub_id, sub_filter in conn["subscriptions"].items():
                matches = True
                if sub_filter.get("entity_type"):
                    # Map collection name back to entity type
                    if collection != sub_filter["entity_type"].lower() + "s":
                        matches = False
                if sub_filter.get("entity_id"):
                    if str(doc.get("_id")) != sub_filter["entity_id"]:
                        matches = False
                if sub_filter.get("collection"):
                    if collection != sub_filter["collection"]:
                        matches = False

                if matches:
                    try:
                        await websocket.send_json({
                            "type": "entity_change",
                            "subscription_id": sub_id,
                            "collection": collection,
                            "operation": change.get("operationType"),
                            "entity_type": _collection_to_entity_type(collection),
                            "entity_id": str(doc.get("_id")),
                            "data": _serialize_for_ws(doc),
                        })
                    except Exception:
                        break
```

## 4.7 The Assistant [G-59]

### Top-Bar Input

Always-visible slim input in the top bar of every view. Focused by `/` or `Cmd+K`.

```tsx
// assistant/AssistantInput.tsx
function AssistantInput() {
  const [input, setInput] = useState("");
  const { sendMessage, isOpen, togglePanel } = useAssistant();

  const handleSubmit = () => {
    if (input.trim()) {
      sendMessage(input.trim());
      setInput("");
      if (!isOpen) togglePanel();
    }
  };

  // Global keyboard shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "/" && !e.ctrlKey && !e.metaKey && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if ((e.key === "k" && (e.ctrlKey || e.metaKey))) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  return (
    <div className="flex-1 max-w-xl mx-auto">
      <input
        ref={inputRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        placeholder="Ask or tell me to do something — I can do anything you can"
        className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-sm"
      />
    </div>
  );
}
```

### Conversation Panel

Slides in from the right (~400-500px). Overlay, not modal. Streaming responses. ESC closes.

```tsx
// assistant/AssistantPanel.tsx
function AssistantPanel() {
  const { messages, isOpen, togglePanel, isStreaming } = useAssistant();

  if (!isOpen) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-[450px] bg-white shadow-xl border-l z-50 flex flex-col">
      <div className="flex justify-between items-center p-4 border-b">
        <h2 className="font-semibold">Assistant</h2>
        <button onClick={togglePanel}>ESC</button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={msg.role === "user" ? "text-right" : ""}>
            <div className={`inline-block p-3 rounded-lg ${
              msg.role === "user" ? "bg-blue-100" : "bg-gray-50"
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isStreaming && <StreamingIndicator />}
      </div>
    </div>
  );
}
```

### Assistant Hook [G-59]

```tsx
// assistant/useAssistant.ts
function useAssistant() {
  const { actor } = useAuth();
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  // Build context from current UI state
  const buildContext = useCallback((): AssistantContext => {
    return {
      view_type: getCurrentViewType(),
      current_entity: getCurrentEntity(),
      current_filter: getCurrentFilter(),
      role_focus: actor?.current_role,
    };
  }, []);

  const sendMessage = async (content: string) => {
    setMessages(prev => [...prev, { id: uuid(), role: "user", content }]);
    setIsStreaming(true);

    const context = buildContext();

    // Call the default assistant's API endpoint
    // The default assistant inherits the user's session JWT [G-59]
    // Audit attributed as "user X via default associate"
    const response = await fetch("/api/assistant/message", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${getToken()}`, // User's own JWT
      },
      body: JSON.stringify({ content, context }),
    });

    // Stream the response
    const reader = response.body?.getReader();
    let assistantContent = "";
    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = new TextDecoder().decode(value);
      assistantContent += chunk;
      setMessages(prev => {
        const updated = [...prev];
        const lastMsg = updated[updated.length - 1];
        if (lastMsg?.role === "assistant") {
          lastMsg.content = assistantContent;
        } else {
          updated.push({ id: uuid(), role: "assistant", content: assistantContent });
        }
        return updated;
      });
    }
    setIsStreaming(false);
  };

  return { messages, isOpen, togglePanel: () => setIsOpen(!isOpen), sendMessage, isStreaming };
}
```

### Assistant API Endpoint

```python
# kernel/api/assistant.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from kernel.auth.middleware import get_current_actor

assistant_router = APIRouter(prefix="/api/assistant", tags=["assistant"])

@assistant_router.post("/message")
async def assistant_message(data: dict, actor=Depends(get_current_actor)):
    """Process an assistant message. The default associate runs with
    the user's own session — same permissions, audit as 'user via assistant'. [G-59]"""
    content = data.get("content", "")
    context = data.get("context", {})

    # The default assistant is a pre-provisioned associate with
    # owner_actor_id = the user. It uses the user's JWT for auth.
    # Every action is audited as: "actor {user.id} via default_associate"

    async def generate():
        # Use the LLM with the user's entity skills as context
        # The assistant can execute any CLI command the user has permission for
        # via the same API (using the user's JWT)
        import anthropic
        client = anthropic.AsyncAnthropic()

        # Load entity skills for the user's roles
        skills = await load_skills_for_roles(actor.role_ids)

        async with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=f"You are the user's assistant in the Indemn OS. "
                   f"You can execute operations using the Indemn API. "
                   f"The user is viewing: {context}.\n\n"
                   f"Available operations:\n{skills}",
            messages=[{"role": "user", "content": content}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    return StreamingResponse(generate(), media_type="text/plain")
```

## 4.8 UI Graceful Degradation [G-87]

```tsx
// layout/StatusBanner.tsx
function StatusBanner() {
  const { data: health } = useQuery("health", () => fetch("/health").then(r => r.json()), {
    refetchInterval: 30000, // Check every 30 seconds
  });

  if (!health || health.status === "healthy") return null;

  const degradedServices = Object.entries(health.checks)
    .filter(([_, status]) => status !== "ok")
    .map(([name, status]) => ({ name, status }));

  return (
    <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-sm text-yellow-800">
      <strong>System degraded:</strong>{" "}
      {degradedServices.map(s => `${s.name} (${s.status})`).join(", ")}.
      {" "}Some features may be temporarily unavailable.
    </div>
  );
}
```

## 4.9 Authentication Completion

Phase 1 established basic auth (password + token + JWT). Phase 4 completes it for real users.

### SSO Login Flow [G-35]

```python
# kernel/api/auth_routes.py (additions for Phase 4)

@auth_router.get("/auth/providers")  # [G-35]
async def list_auth_providers(org_slug: str):
    """Pre-auth endpoint — no token required.
    Returns available login methods for an org."""
    org = await Organization.find_one({"slug": org_slug})
    if not org:
        raise HTTPException(404)

    providers = [{"type": "password", "name": "Password"}]

    # Find identity_provider integrations for this org
    sso_integrations = await Integration.find({
        "org_id": org.id,
        "system_type": "identity_provider",
        "status": "active",
    }).to_list()

    for integration in sso_integrations:
        providers.append({
            "type": "sso",
            "name": integration.name,  # "Okta", "Google Workspace"
            "integration_id": str(integration.id),
            "provider": integration.provider,
        })

    return {"org_id": str(org.id), "providers": providers}

@auth_router.get("/auth/sso/{integration_id}")
async def sso_initiate(integration_id: str):
    """Redirect to SSO provider."""
    integration = await Integration.get(integration_id)
    if not integration or integration.system_type != "identity_provider":
        raise HTTPException(404)

    adapter = await get_adapter_for_integration(integration)
    redirect_url = await adapter.auth_initiate(
        redirect_uri=f"{settings.api_url}/auth/sso/{integration_id}/callback"
    )
    return RedirectResponse(redirect_url)

@auth_router.get("/auth/sso/{integration_id}/callback")
async def sso_callback(integration_id: str, code: str, state: str = None):
    """SSO callback — validate token, find actor, create session."""
    integration = await Integration.get(integration_id)
    adapter = await get_adapter_for_integration(integration)
    user_info = await adapter.auth_callback(code, state)

    # Look up actor by email
    actor = await Actor.find_one({
        "email": user_info["email"],
        "org_id": integration.org_id,
        "status": "active",
    })
    if not actor:
        raise HTTPException(403, "No active actor found for this email")

    # Check MFA requirement
    mfa_required = await check_mfa_required(actor)

    # Create session
    session = await create_session(actor, auth_method="sso:" + integration.provider)

    if mfa_required and not actor.mfa_exempt:
        # Issue partial token for MFA challenge [G-36]
        partial_token = create_partial_token(actor, session)
        return {"requires_mfa": True, "mfa_type": "totp", "partial_token": partial_token}

    # Issue full tokens
    tokens = issue_full_tokens(session, actor)
    return tokens
```

### MFA Challenge Flow [G-36]

```python
@auth_router.post("/auth/mfa/verify")
async def verify_mfa(partial_token: str, totp_code: str):
    """Verify TOTP code and upgrade partial token to full session."""
    # Verify partial token
    payload = verify_partial_token(partial_token)
    actor = await Actor.get(payload["actor_id"])
    session = await Session.get(payload["session_id"])

    # Verify TOTP
    totp_method = next(
        (m for m in actor.authentication_methods if m["type"] == "totp"),
        None,
    )
    if not totp_method:
        raise HTTPException(400, "No TOTP method configured")

    # Fetch TOTP secret from Secrets Manager
    totp_secret = await fetch_credentials(totp_method["secret_ref"])
    import pyotp
    totp = pyotp.TOTP(totp_secret["secret"])
    if not totp.verify(totp_code, valid_window=1):
        # Record failed MFA attempt [G-41]
        await write_auth_event(actor, "auth.mfa_challenged", {"success": False})
        raise HTTPException(401, "Invalid TOTP code")

    # MFA verified — update session
    session.mfa_verified = True
    session.mfa_verified_at = datetime.utcnow()
    await session.save()

    # Record successful MFA [G-41]
    await write_auth_event(actor, "auth.mfa_verified", {"method": "totp"})

    # Issue full tokens
    tokens = issue_full_tokens(session, actor)
    return tokens

def create_partial_token(actor, session) -> str:
    """Create a short-lived token that can only be used for MFA verification."""
    return jwt.encode({
        "actor_id": str(actor.id),
        "session_id": str(session.id),
        "purpose": "mfa_challenge",
        "exp": datetime.utcnow() + timedelta(minutes=5),
    }, settings.jwt_signing_key, algorithm=settings.jwt_algorithm)
```

### Platform Admin Cross-Org Sessions [G-37]

```python
@auth_router.post("/api/platform/sessions")
async def create_platform_admin_session(
    target_org_id: str,
    work_type: str = "build",  # build, debug, incident, routine
    duration_hours: int = 4,
    reason: str = "",
    actor=Depends(get_current_actor),
):
    """Create a platform admin session in a target org.
    The actor must be in the _platform org with platform_admin role."""
    # Verify actor is a platform admin
    if not await is_platform_admin(actor):
        raise HTTPException(403, "Not a platform admin")

    # Enforce duration limits
    if duration_hours > 24:
        raise HTTPException(400, "Maximum session duration is 24 hours")

    target_org = await Organization.get(target_org_id)
    if not target_org:
        raise HTTPException(404, "Target org not found")

    # Create temporary session in target org
    session = Session(
        org_id=ObjectId(target_org_id),
        actor_id=actor.id,
        type="user_interactive",
        auth_method_used="platform_admin",
        status="active",
        expires_at=datetime.utcnow() + timedelta(hours=duration_hours),
        platform_admin_context={
            "source_org_id": str(actor.org_id),
            "target_org_id": target_org_id,
            "work_type": work_type,
            "reason": reason,
            "acting_actor_name": actor.name,
            "acting_actor_email": actor.email,
        },
        access_token_jti=str(uuid4()),
    )
    await session.insert()

    # Audit in target org's changes collection [G-41]
    await write_auth_event_in_org(
        ObjectId(target_org_id), actor,
        "auth.platform_admin_access",
        {
            "work_type": work_type,
            "reason": reason,
            "duration_hours": duration_hours,
            "source_org": str(actor.org_id),
        },
    )

    # Notify target org (if configured)
    # Per auth design: per-customer notification config
    await notify_platform_admin_access(target_org, actor, work_type)

    # Issue access token scoped to target org
    token, jti = create_access_token(str(actor.id), target_org_id, ["platform_admin"])
    session.access_token_jti = jti
    await session.save()

    return {"access_token": token, "expires_at": session.expires_at.isoformat()}
```

### Recovery Flows [G-38]

```python
# Password reset
@auth_router.post("/auth/reset-password/initiate")
async def initiate_password_reset(email: str, org_slug: str):
    """Send password reset magic link via email Integration."""
    org = await Organization.find_one({"slug": org_slug})
    actor = await Actor.find_one({"email": email, "org_id": org.id})
    if not actor:
        return {"status": "ok"}  # Don't reveal whether email exists

    # Generate magic link token
    token = generate_magic_link_token(actor, purpose="password_reset", expires_hours=4)
    # Send via org's email Integration
    await send_magic_link_email(org, actor, token, purpose="password_reset")
    return {"status": "ok"}

@auth_router.post("/auth/reset-password/complete")
async def complete_password_reset(token: str, new_password: str):
    """Complete password reset. Revokes all existing sessions."""
    payload = verify_magic_link_token(token, purpose="password_reset")
    actor = await Actor.get(payload["actor_id"])

    # Update password
    password_method = next(m for m in actor.authentication_methods if m["type"] == "password")
    password_method["password_hash"] = hash_password(new_password)
    await actor.save()

    # Revoke all sessions [G-38]
    await Session.get_motor_collection().update_many(
        {"actor_id": actor.id, "status": "active"},
        {"$set": {"status": "revoked"}},
    )

    await write_auth_event(actor, "auth.password_changed", {"method": "reset"})
    return {"status": "password_reset"}

# MFA recovery via backup codes
@auth_router.post("/auth/mfa/backup")
async def use_backup_code(partial_token: str, backup_code: str):
    """Use a backup code instead of TOTP. Single-use. Forces re-enrollment."""
    payload = verify_partial_token(partial_token)
    actor = await Actor.get(payload["actor_id"])

    # Fetch backup codes from Secrets Manager
    totp_method = next(m for m in actor.authentication_methods if m["type"] == "totp")
    secrets = await fetch_credentials(totp_method["secret_ref"])
    backup_codes = secrets.get("backup_codes", [])

    # Verify and consume backup code (codes stored as hashes)
    matched = False
    for i, stored_hash in enumerate(backup_codes):
        if verify_password(backup_code, stored_hash):
            matched = True
            backup_codes.pop(i)
            break

    if not matched:
        raise HTTPException(401, "Invalid backup code")

    # Update stored backup codes
    secrets["backup_codes"] = backup_codes
    await store_credentials(totp_method["secret_ref"], secrets)

    # MFA verified
    session = await Session.get(payload["session_id"])
    session.mfa_verified = True
    session.mfa_verified_at = datetime.utcnow()
    await session.save()

    await write_auth_event(actor, "auth.mfa_reset", {"method": "backup_code"})

    tokens = issue_full_tokens(session, actor)
    # Flag that re-enrollment is needed
    tokens["mfa_re_enrollment_required"] = True
    return tokens
```

### Claims Refresh [G-39]

```python
# In kernel/auth/middleware.py — addition to the request processing:

async def check_claims_freshness(actor, session, request):
    """If claims_stale=True, auto-refresh the access token."""
    if session.claims_stale:
        # Re-load actor's current roles
        current_roles = await get_current_role_names(actor)

        # Issue new access token with updated claims
        new_token, new_jti = create_access_token(str(actor.id), str(actor.org_id), current_roles)

        # Update session
        session.claims_stale = False
        session.access_token_jti = new_jti
        await session.save()

        # Return new token in response header
        request.state.refreshed_token = new_token
        request.state.actor_roles = current_roles

# In the response middleware:
async def add_refreshed_token_header(request, response):
    if hasattr(request.state, "refreshed_token"):
        response.headers["X-Refreshed-Token"] = request.state.refreshed_token
```

When a role is revoked:
```python
# When role is removed from an actor:
await Session.get_motor_collection().update_many(
    {"actor_id": actor.id, "status": "active"},
    {"$set": {"claims_stale": True}},
)
```

### Pre-Auth Rate Limiting [G-40]

```python
# kernel/auth/rate_limit.py
from datetime import datetime, timedelta
import hashlib

# Rate limit tracking collection
RATE_LIMIT_COLLECTION = "auth_rate_limits"

async def check_rate_limit(ip_address: str, email: str, org_id: str) -> bool:
    """Check if login attempts are rate-limited.
    Returns True if the attempt should be blocked."""
    db = get_database()
    collection = db[RATE_LIMIT_COLLECTION]

    # Key: hash of ip + email (don't store raw email)
    key = hashlib.sha256(f"{ip_address}:{email}".encode()).hexdigest()
    window = datetime.utcnow() - timedelta(minutes=10)

    # Count recent failures
    doc = await collection.find_one({"_id": key})
    if doc:
        recent_failures = [t for t in doc.get("failures", []) if t > window]
        if len(recent_failures) >= 5:  # Default threshold: 5 failures in 10 min
            # Check if lockout has expired (30 min)
            lockout_until = doc.get("locked_until")
            if lockout_until and lockout_until > datetime.utcnow():
                return True  # Still locked out
            elif len(recent_failures) >= 5:
                # New lockout
                await collection.update_one(
                    {"_id": key},
                    {"$set": {"locked_until": datetime.utcnow() + timedelta(minutes=30)}},
                    upsert=True,
                )
                # Audit [G-41]
                await write_auth_event_by_email(
                    email, org_id, "auth.brute_force_lockout",
                    {"ip_address": ip_address, "failures": len(recent_failures)},
                )
                return True
    return False

async def record_failed_attempt(ip_address: str, email: str):
    """Record a failed login attempt."""
    db = get_database()
    key = hashlib.sha256(f"{ip_address}:{email}".encode()).hexdigest()
    await db[RATE_LIMIT_COLLECTION].update_one(
        {"_id": key},
        {"$push": {"failures": datetime.utcnow()}, "$set": {"last_attempt": datetime.utcnow()}},
        upsert=True,
    )
```

### Auth Audit Events [G-41]

```python
# kernel/auth/audit.py

AUTH_EVENT_TYPES = [
    "auth.login_attempt",
    "auth.login_success",
    "auth.login_failure",
    "auth.session_created",
    "auth.session_refreshed",
    "auth.session_revoked",
    "auth.mfa_enrolled",
    "auth.mfa_challenged",
    "auth.mfa_verified",
    "auth.mfa_reset",
    "auth.password_changed",
    "auth.method_added",
    "auth.method_removed",
    "auth.role_granted",
    "auth.role_revoked",
    "auth.lifecycle_transitioned",
    "auth.platform_admin_access",
    "auth.brute_force_lockout",
]

async def write_auth_event(actor, event_type: str, metadata: dict = None):
    """Write an auth event to the changes collection."""
    from kernel.changes.collection import ChangeRecord, write_change_record

    record = ChangeRecord(
        org_id=actor.org_id,
        entity_type="Actor",
        entity_id=actor.id,
        change_type=event_type,
        actor_id=str(actor.id),
        method=event_type,
        method_metadata=metadata or {},
    )
    from kernel.changes.hash_chain import compute_hash, get_previous_hash
    record.previous_hash = await get_previous_hash(actor.org_id, None)
    record.current_hash = compute_hash(record)
    await record.insert()
```

### Revocation Cache with Bootstrap [G-42]

```python
# kernel/auth/jwt.py — additions for Phase 4

# In-memory revocation cache
_revocation_cache: dict[str, float] = {}  # jti → revoked_at timestamp
_CACHE_TTL = 900  # 15 minutes (matches max access token lifetime)

async def bootstrap_revocation_cache():
    """On API instance startup: load recently revoked sessions. [G-42]"""
    cutoff = datetime.utcnow() - timedelta(seconds=_CACHE_TTL)
    revoked = await Session.find({
        "status": "revoked",
        "updated_at": {"$gte": cutoff},
    }).to_list()
    for session in revoked:
        _revocation_cache[session.access_token_jti] = time.time()

async def watch_revocations():
    """Watch for Session revocations via Change Stream. [G-42]
    Run as a background task on API startup."""
    db = get_database()
    pipeline = [
        {"$match": {
            "fullDocument.status": "revoked",
            "operationType": "update",
        }},
    ]
    async with db["sessions"].watch(pipeline, full_document="updateLookup") as stream:
        async for change in stream:
            doc = change.get("fullDocument", {})
            jti = doc.get("access_token_jti")
            if jti:
                _revocation_cache[jti] = time.time()

def verify_access_token(token: str) -> dict:
    """Verify JWT with revocation check."""
    payload = jwt.decode(token, settings.jwt_signing_key, algorithms=[settings.jwt_algorithm])

    # Check revocation cache
    jti = payload.get("jti")
    if jti and jti in _revocation_cache:
        raise jwt.InvalidTokenError("Token has been revoked")

    # Evict expired cache entries
    now = time.time()
    expired = [k for k, v in _revocation_cache.items() if now - v > _CACHE_TTL]
    for k in expired:
        del _revocation_cache[k]

    return payload
```

### Tier 3 Self-Service Signup [G-58]

```python
@auth_router.post("/auth/signup")
async def tier3_signup(email: str, password: str, org_name: str):
    """Tier 3 developer self-service signup.
    MVP scope: org + first admin + password + email verification + first API key."""
    # Create org
    org_id = ObjectId()
    org = Organization(
        id=org_id, org_id=org_id,
        name=org_name, slug=_slugify(org_name),
        status="onboarding",
    )
    await org.insert()

    # Create admin actor
    admin = Actor(
        org_id=org_id, name=email.split("@")[0], email=email,
        type="tier3_developer", status="provisioned",
        authentication_methods=[{
            "type": "password",
            "password_hash": hash_password(password),
        }],
    )
    await admin.insert()

    # Create admin role
    admin_role = Role(
        org_id=org_id, name="admin",
        permissions={"read": ["*"], "write": ["*"]},
    )
    await admin_role.insert()
    admin.role_ids = [admin_role.id]
    await admin.save()

    # Generate API key (token method)
    api_key = generate_service_token()
    admin.authentication_methods.append({
        "type": "token",
        "usage": "tier3_api_key",
        "token_hash": hash_password(api_key),
    })
    await admin.save()

    # Send verification email (if email Integration exists on _platform org)
    # If not, verification is deferred
    await send_verification_email_if_possible(admin)

    return {
        "org_id": str(org_id),
        "actor_id": str(admin.id),
        "api_key": api_key,  # Shown once, never again
        "status": "created",
        "note": "Verify your email to activate the org",
    }
```

## 4.10 Pipeline Metrics

Kernel aggregation capabilities activated per entity type, callable from CLI/API/UI:

```python
# kernel/capability/aggregations.py (registered as capabilities in Phase 4)

async def state_distribution(entity_cls, org_id) -> dict:
    """Count per state machine value."""
    pipeline = [
        {"$match": {"org_id": org_id}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    result = await entity_cls.get_motor_collection().aggregate(pipeline).to_list()
    return {doc["_id"]: doc["count"] for doc in result}

async def queue_depth(org_id) -> dict:
    """Pending message count per role."""
    pipeline = [
        {"$match": {"org_id": org_id, "status": "pending"}},
        {"$group": {"_id": "$target_role", "count": {"$sum": 1}}},
    ]
    result = await Message.get_motor_collection().aggregate(pipeline).to_list()
    return {doc["_id"]: doc["count"] for doc in result}
```

## Phase 4 Acceptance Criteria

```
1. OPERATOR LOGS IN — password, SSO, MFA when required
2. QUEUE VIEW — pending messages, coalesced display, claim action
3. ENTITY LIST — auto-generated from metadata, sort/filter/paginate
4. ENTITY DETAIL — auto-generated form, state transitions, actions
5. REAL-TIME — changes appear live via WebSocket, no refresh
6. ASSISTANT — top-bar input, conversation panel, executes operations
7. NEW ENTITY APPEARS — add definition, restart, UI shows it
8. KERNEL ENTITY VIEWS — Actors, Roles, Integrations manageable via UI
9. PLATFORM ADMIN — cross-org session, audited, time-limited
10. RECOVERY — password reset, MFA backup codes, emergency access
11. RATE LIMITING — brute force blocked after 5 failures
12. AUTH AUDIT — all auth events in changes collection
13. DEGRADATION — status banner when dependencies are down
14. TIER 3 SIGNUP — self-service org creation with API key
```

---

# Phase 5: Real-Time

## 5.1 Attention Activation [G-43, G-44, G-45]

The Attention kernel entity was defined in Phase 1. Phase 5 activates its real-time behaviors.

### Heartbeat Bypass [G-43]

Already implemented in Phase 1's `save_tracked()` via `_is_heartbeat_only()` detection. Phase 5 ensures harnesses send heartbeats:

```python
# In harness code (e.g., voice harness):
async def _heartbeat_loop(self):
    """Send heartbeat every 30 seconds to keep Attention alive."""
    while True:
        try:
            cli(f"attention heartbeat {self.attention_id}")
        except Exception:
            pass  # Best-effort
        await asyncio.sleep(30)
```

### TTL Cleanup Process [G-44]

Addition to the queue processor:

```python
# kernel/queue_processor.py — Phase 5 addition

async def cleanup_expired_attentions():
    """Find and expire Attentions past their TTL. [G-44]"""
    from kernel_entities.attention import Attention
    expired = await Attention.find({
        "status": "active",
        "expires_at": {"$lt": datetime.utcnow()},
    }).to_list()

    for attention in expired:
        attention.transition_to("expired")
        await attention.save_tracked(
            actor_id="system:ttl_cleanup",
            method="ttl_expiration",
        )
        # This save triggers watches — ops can watch for
        # Attention:transitioned[to=expired] for alerting

register_sweep(cleanup_expired_attentions)
```

### Zombie Detection and Recovery [G-45]

When an Attention expires (Runtime instance crashed):

```python
async def handle_zombie_sessions():
    """Detect and recover from zombie real-time sessions. [G-45]"""
    from kernel_entities.attention import Attention

    # Find recently expired real-time sessions
    recently_expired = await Attention.find({
        "status": "expired",
        "purpose": "real_time_session",
        "expires_at": {"$gte": datetime.utcnow() - timedelta(minutes=5)},
    }).to_list()

    for attention in recently_expired:
        # Transition the linked Interaction to abandoned
        entity_type = attention.target_entity.get("type")
        entity_id = attention.target_entity.get("id")
        if entity_type and entity_id:
            from kernel.db import ENTITY_REGISTRY
            entity_cls = ENTITY_REGISTRY.get(entity_type)
            if entity_cls:
                entity = await entity_cls.get(entity_id)
                if entity and hasattr(entity, 'status') and entity.status == "active":
                    entity.transition_to("abandoned", reason="Runtime session expired")
                    await entity.save_tracked(
                        actor_id="system:zombie_recovery",
                        method="zombie_recovery",
                    )

register_sweep(handle_zombie_sessions)
```

## 5.2 Runtime Deployment [G-46]

```bash
# Create a Runtime entity
indemn runtime create --name "Voice Production" --kind realtime_voice \
  --framework deepagents --framework-version 1.2.0 \
  --transport livekit --deployment-image indemn/runtime-voice-deepagents:1.2.0 \
  --deployment-platform railway

# Deploy the harness container (manual for MVP)
# 1. Push the Docker image to registry
# 2. Create Railway service from the image
# 3. Configure environment variables (INDEMN_API_URL, RUNTIME_ID, etc.)
# 4. Start the service

# Then mark as active
indemn runtime transition RUNTIME-001 --to deploying
# ... wait for Railway to report healthy ...
indemn runtime transition RUNTIME-001 --to active
```

For MVP: deployment is a manual process (operator deploys the container, then updates the Runtime entity status). Automated deployment via Railway API is a future enhancement.

## 5.3 Harness Pattern — Full Voice Example [G-65]

```python
# harnesses/voice-deepagents/main.py
"""
Voice harness: LiveKit Agents + deepagents + Indemn OS CLI.
One harness serves any Associate of matching kind by loading config at session start.
Full access to LiveKit's features (rooms, audio processing, etc.)
"""
import asyncio
import subprocess
import json
import os
from livekit.agents import Agent, AgentSession

# CLI wrapper — all OS interactions go through this [G-65]
def cli(command: str) -> dict:
    """Execute an indemn CLI command via subprocess.
    The CLI authenticates using INDEMN_SERVICE_TOKEN."""
    env = {
        **os.environ,
        "INDEMN_API_URL": os.environ["INDEMN_API_URL"],
    }
    result = subprocess.run(
        ["indemn"] + command.split(),
        capture_output=True, text=True,
        env=env,
        timeout=60,  # 60-second timeout per command
    )
    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr}")
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return {"raw": result.stdout}

class IndemnVoiceAgent(Agent):

    async def on_session_start(self, session: AgentSession):
        """Called when a new voice session begins."""

        # Load associate config from OS via deployment metadata
        deployment_id = session.metadata.get("deployment_id")
        deployment = cli(f"deployment get {deployment_id}")
        associate_id = deployment["associate_id"]
        associate = cli(f"actor get {associate_id}")

        self.associate_id = associate_id
        self.associate = associate

        # Create Interaction entity
        interaction = cli(
            f"interaction create "
            f"--data '{{\"channel_type\": \"voice\", \"deployment_id\": \"{deployment_id}\", "
            f"\"status\": \"active\"}}'"
        )
        self.interaction_id = interaction["_id"]

        # Open Attention (real-time session tracking)
        runtime_id = os.environ.get("RUNTIME_ID", "")
        attention = cli(
            f"attention create "
            f"--data '{{\"actor_id\": \"{associate_id}\", "
            f"\"target_entity\": {{\"type\": \"Interaction\", \"id\": \"{self.interaction_id}\"}}, "
            f"\"purpose\": \"real_time_session\", "
            f"\"runtime_id\": \"{runtime_id}\", "
            f"\"expires_at\": \"{_two_minutes_from_now()}\"}}'"
        )
        self.attention_id = attention["_id"]

        # Load skills
        skill_names = associate.get("skills", [])
        skills_content = []
        for name in skill_names:
            skill = cli(f"skill get {name}")
            skills_content.append(skill.get("content", ""))
        self.skills = "\n\n---\n\n".join(skills_content)

        # Build the deep agent with skills
        # Three-layer config merge [G-50]:
        # Runtime defaults → Associate override → Deployment override
        runtime = cli(f"runtime get {runtime_id}")
        llm_config = {
            **(runtime.get("llm_config") or {}),        # Runtime defaults
            **(associate.get("llm_config") or {}),       # Associate override
            **(deployment.get("llm_override") or {}),    # Deployment override
        }

        model = llm_config.get("model", "claude-sonnet-4-6")
        # Create deepagents agent with the merged config
        from deepagents import create_deep_agent
        self.agent = create_deep_agent(
            skills=self.skills,
            model=model,
            # Full access to deepagents features
        )

        # Start background tasks
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._event_listener())

    async def on_message(self, message: str) -> str:
        """Process a voice turn."""
        # The agent may execute CLI commands that change entities
        # Those changes flow through watches → messages → potentially back here via events
        response = await self.agent.process(message, context={
            "interaction_id": self.interaction_id,
            "deployment": self.associate.get("deployment_config", {}),
        })
        return response

    async def on_session_end(self):
        """Clean up on session end."""
        try:
            cli(f"attention transition {self.attention_id} --to closed")
            cli(f"interaction update {self.interaction_id} --data '{{\"status\": \"closed\", \"ended_at\": \"{datetime.utcnow().isoformat()}\"}}'")
        except Exception:
            pass  # Best-effort cleanup

    async def _heartbeat_loop(self):
        while True:
            try:
                cli(f"attention heartbeat {self.attention_id}")
            except Exception:
                pass
            await asyncio.sleep(30)

    async def _event_listener(self):
        """Listen for scoped events targeting this actor. [G-48]
        The events stream is the notification path — scoped watches write
        messages to message_queue with target_actor_id set, and this
        stream picks them up via the Change Stream."""
        process = await asyncio.create_subprocess_exec(
            "indemn", "events", "stream",
            "--actor", self.associate_id,
            "--interaction", self.interaction_id,
            stdout=asyncio.subprocess.PIPE,
            env={**os.environ},
        )
        try:
            async for line in process.stdout:
                event = json.loads(line.decode().strip())
                # Feed event to the agent as a proactive notification
                await self.agent.handle_event(event)
        except asyncio.CancelledError:
            process.terminate()
            await process.wait()
```

### Harness CLI Authentication [G-65]

The harness CLI authenticates using a service token for the Runtime itself (not per-associate):

```bash
# Environment variables set on the harness Railway service:
INDEMN_API_URL=http://indemn-api.railway.internal:8000
INDEMN_SERVICE_TOKEN=<runtime-service-token>
RUNTIME_ID=<runtime-entity-id>
```

The service token is created when the Runtime entity is created and stored as a Session of type `associate_service`. The CLI reads `INDEMN_SERVICE_TOKEN` from the environment and uses it as a Bearer token for all API calls.

## 5.4 `indemn events stream` [G-47]

```python
# kernel/api/events.py
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from kernel.auth.middleware import get_current_actor
from kernel.db import get_database
import orjson

events_router = APIRouter(prefix="/api/_stream", tags=["events"])

@events_router.get("/events")
async def stream_events(
    actor: str = Query(None),
    interaction: str = Query(None),
    entity_type: str = Query(None),
    current_actor=Depends(get_current_actor),
):
    """Server-Sent Events backed by MongoDB Change Stream. [G-47]"""

    async def event_generator():
        db = get_database()
        org_id = current_actor.org_id

        # Build Change Stream pipeline [G-47]
        match_conditions = {"fullDocument.org_id": org_id}
        if actor:
            match_conditions["$or"] = [
                {"fullDocument.target_actor_id": ObjectId(actor)},
                {"fullDocument.target_actor_id": None},
            ]
        if entity_type:
            match_conditions["fullDocument.entity_type"] = entity_type

        pipeline = [{"$match": match_conditions}]

        async with db["message_queue"].watch(
            pipeline, full_document="updateLookup"
        ) as stream:
            async for change in stream:
                doc = change.get("fullDocument")
                if not doc:
                    continue

                # If interaction filter, check if entity is related
                if interaction:
                    # Check if this message's entity is related to the interaction
                    if not await _is_related_to_interaction(doc, interaction):
                        continue

                yield orjson.dumps({
                    "id": str(doc.get("_id")),
                    "entity_type": doc.get("entity_type"),
                    "entity_id": str(doc.get("entity_id")),
                    "event_type": doc.get("event_type"),
                    "target_role": doc.get("target_role"),
                    "correlation_id": doc.get("correlation_id"),
                    "event_metadata": doc.get("event_metadata", {}),
                }).decode() + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
    )

# CLI command
# kernel/cli/events_commands.py
@events_app.command("stream")
def stream_events(
    actor: str = typer.Option(None),
    interaction: str = typer.Option(None),
    entity_type: str = typer.Option(None),
):
    """Stream matching events as JSON lines on stdout."""
    client = get_client()
    params = {}
    if actor: params["actor"] = actor
    if interaction: params["interaction"] = interaction
    if entity_type: params["entity_type"] = entity_type

    with client.stream("GET", "/api/_stream/events", params=params) as response:
        for line in response.iter_lines():
            typer.echo(line)
```

## 5.5 Scoped Watch Resolution

Already defined in Phase 1's `kernel/watch/scope.py`. Phase 5 activates the full implementation:

```python
# kernel/watch/scope.py (complete implementation for Phase 5)

async def resolve_scope(scope: dict, entity, session) -> ObjectId | list[ObjectId] | None:
    """Resolve a watch scope to target actor(s)."""
    scope_type = scope.get("type")

    if scope_type == "field_path":
        return await _resolve_field_path(scope, entity, session)
    elif scope_type == "active_context":
        return await _resolve_active_context(scope, entity, session)
    else:
        return None

async def _resolve_field_path(scope: dict, entity, session) -> ObjectId | None:
    """Traverse entity relationships to resolve an actor_id.
    E.g., path="organization.primary_owner_id" traverses
    entity.organization_id → Organization → primary_owner_id."""
    path = scope["path"]
    parts = path.split(".")
    current_data = entity.dict(by_alias=True)

    for i, part in enumerate(parts[:-1]):
        # This part is a relationship field — load the related entity
        related_id = current_data.get(part)
        if not related_id:
            return None
        # Determine the entity type from the field definition
        entity_cls = _resolve_entity_type_for_field(type(entity).__name__, part)
        if not entity_cls:
            return None
        related = await entity_cls.get(related_id)
        if not related:
            return None
        current_data = related.dict(by_alias=True)

    # Last part is the actor_id field
    actor_id = current_data.get(parts[-1])
    return ObjectId(actor_id) if actor_id else None

async def _resolve_active_context(scope: dict, entity, session) -> ObjectId | None:
    """Find actors with Attention records covering this entity. [G-48]"""
    from kernel_entities.attention import Attention

    traverses = scope.get("traverses")
    related_id = getattr(entity, traverses, None) if traverses else entity.id
    if not related_id:
        return None

    # Query Attention for active records with matching related_entities
    attentions = await Attention.find({
        "status": "active",
        "expires_at": {"$gt": datetime.utcnow()},
        "$or": [
            {"target_entity.id": related_id},
            {"related_entities.id": related_id},
        ],
    }).to_list()

    if not attentions:
        return None

    # Return the first matching actor
    # (For multiple matches, emit one message per actor — handled in emit.py)
    return attentions[0].actor_id
```

### Scoped Watch → Runtime Notification Path [G-48]

The events stream IS the notification path. When active_context resolution finds an Attention with runtime_id:

1. The watch evaluation writes a message to `message_queue` with `target_actor_id` set to the Attention's actor_id
2. The harness is running `indemn events stream --actor {associate_id}` which watches `message_queue` via Change Stream filtered by `target_actor_id`
3. The event appears in the stream
4. The harness feeds it to the running agent

No separate notification mechanism is needed. The events stream uses the same message_queue collection that everything else uses.

## 5.6 Handoff [G-49]

```python
# kernel/api/interaction.py

@router.post("/api/interactions/{interaction_id}/transfer")
async def transfer_interaction(
    interaction_id: str,
    to_actor: str = None,
    to_role: str = None,
    actor=Depends(get_current_actor),
):
    """Transfer an Interaction between actors/roles. [G-49]"""
    interaction = await Interaction.get_scoped(interaction_id)
    if not interaction:
        raise HTTPException(404)

    old_handler = interaction.handling_actor_id

    # 1. Close old actor's Attention [G-49]
    if old_handler:
        old_attentions = await Attention.find({
            "actor_id": old_handler,
            "target_entity.id": ObjectId(interaction_id),
            "status": "active",
        }).to_list()
        for att in old_attentions:
            att.transition_to("closed")
            await att.save_tracked(actor_id=str(actor.id), method="handoff_close")

    # 2. Update Interaction handler
    if to_actor:
        interaction.handling_actor_id = ObjectId(to_actor)
        interaction.handling_role_id = None
    elif to_role:
        interaction.handling_role_id = to_role
        interaction.handling_actor_id = None  # Any actor with the role can claim

    await interaction.save_tracked(
        actor_id=str(actor.id),
        method="transfer",
        method_metadata={
            "from_actor": str(old_handler),
            "to_actor": to_actor,
            "to_role": to_role,
        },
    )

    # 3. Re-target pending messages [G-49]
    # Messages in queue for old actor targeting this interaction
    # should become available to the new handler
    if old_handler and to_actor:
        await Message.get_motor_collection().update_many(
            {
                "target_actor_id": old_handler,
                "status": "pending",
                # Only re-target messages related to this interaction
                "context.interaction_id": interaction_id,
            },
            {"$set": {"target_actor_id": ObjectId(to_actor)}},
        )

    # 4. The Runtime detects the change via Change Stream on the Interaction
    # and switches modes (associate-in-process → human-via-queue or vice versa)

    return {"status": "transferred", "to_actor": to_actor, "to_role": to_role}
```

### Observation

```python
@router.post("/api/interactions/{interaction_id}/observe")
async def observe_interaction(interaction_id: str, actor=Depends(get_current_actor)):
    """Start observing an Interaction. First-class state — see without handling."""
    attention = Attention(
        org_id=actor.org_id,
        actor_id=actor.id,
        target_entity={"type": "Interaction", "id": ObjectId(interaction_id)},
        purpose="observing",
        opened_at=datetime.utcnow(),
        last_heartbeat=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    await attention.save_tracked(actor_id=str(actor.id), method="observe")
    return {"attention_id": str(attention.id), "status": "observing"}
```

## 5.7 Human Voice Client as Integration [G-51]

```bash
# When a human wants to take over a voice call:

# 1. They have a voice_client Integration (created during onboarding)
indemn integration create --owner actor --actor cam@indemn.ai \
  --name "Cam's Voice Client" --system-type voice_client --provider livekit

# 2. The UI calls the transfer endpoint
# POST /api/interactions/INT-001/transfer?to_actor=cam

# 3. The Runtime bridges Cam's voice client into the existing call room
# The Runtime's harness has access to LiveKit's room API
# It adds Cam's audio stream to the room
# The associate can observe (Attention purpose=observing) or disconnect

# 4. Transfer back to associate
# POST /api/interactions/INT-001/transfer?to_role=quote_assistant
```

## Phase 5 Acceptance Criteria

```
1. CHAT SESSION END-TO-END
   Consumer opens chat → Interaction created → associate handles conversation →
   entity operations update state → conversation ends → Attention closed

2. MID-CONVERSATION EVENT DELIVERY
   During active conversation, scoped event occurs →
   running associate receives it via events stream →
   sends proactive message to consumer

3. SCOPED WATCH — FIELD PATH
   Event with field_path scope → only the referenced actor receives message

4. SCOPED WATCH — ACTIVE CONTEXT
   Event for entity related to active Attention →
   only the actor holding the Attention receives message

5. HANDOFF — ASSOCIATE TO HUMAN
   Human observes → transfers to self → old Attention closed →
   new handler set → pending messages re-targeted

6. HANDOFF — HUMAN TO ASSOCIATE
   Human transfers to role → associate claims → continues handling

7. HARNESS USES CLI ONLY
   All harness-to-kernel communication via CLI subprocess →
   no direct MongoDB → no Python SDK

8. RUNTIME LIFECYCLE
   Create → deploy container → transition to active →
   associates serve sessions → drain → stop

9. ATTENTION LIFECYCLE
   Open → heartbeat maintains → heartbeats stop → TTL expires → cleanup runs

10. ZOMBIE RECOVERY
    Runtime crashes → Attention expires → Interaction abandoned → ops alerted

11. THREE-LAYER CONFIG MERGE
    Runtime defaults → Associate override → Deployment override → correct merge at session start

12. EVENTS STREAM
    indemn events stream --actor X --interaction Y → filtered JSON lines on stdout
```

---

## Gaps Resolved in This Document

G-32 (field mapping), G-33 (metadata endpoint), G-34 (WebSocket subscriptions), G-35 (SSO discovery), G-36 (MFA flow), G-37 (platform admin), G-38 (recovery flows), G-39 (claims refresh), G-40 (rate limiting), G-41 (auth events), G-42 (revocation cache), G-43 (heartbeat bypass), G-44 (TTL cleanup), G-45 (zombie detection), G-46 (runtime deployment), G-47 (events stream pipeline), G-48 (scoped→runtime path), G-49 (handoff consistency), G-50 (config merge), G-51 (voice client), G-58 (Tier 3 signup), G-59 (assistant auth), G-65 (harness CLI auth), G-87 (UI degradation).
