# Vision Alignment — Resolve 10 Limitations

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bring the Indemn OS into full alignment with the vision by resolving 10 limitations found during browser testing and code review.

**Architecture:** Fixes span kernel (API, Temporal, changes), chat harness (session lifecycle, tool exposure), and UI (bulk actions, conversation persistence). Each task is independent except where noted.

**Tech Stack:** Python (FastAPI, Temporal, Motor), TypeScript (React, TanStack), deepagents framework

---

### Task 1: Fix state distribution aggregation

The observability view shows empty state distribution cards because the aggregation query hardcodes `$status` but entities like Company use `stage` as their state field.

**Files:**
- Modify: `/Users/home/Repositories/indemn-os/kernel/capability/aggregations.py:14-21`

**Step 1: Fix the aggregation query**

```python
async def state_distribution(entity_cls, org_id: ObjectId) -> dict:
    """Count per state machine value for an entity type."""
    state_field = getattr(entity_cls, "_state_field_name", None) or "status"
    pipeline = [
        {"$match": {"org_id": org_id}},
        {"$group": {"_id": f"${state_field}", "count": {"$sum": 1}}},
    ]
    result = await entity_cls.get_motor_collection().aggregate(pipeline).to_list(length=100)
    return {doc["_id"]: doc["count"] for doc in result if doc["_id"] is not None}
```

**Step 2: Deploy and verify**

Run: `railway up --service indemn-api --detach`

Verify via curl:
```bash
curl -H "Authorization: Bearer $TOKEN" "$API/api/metrics/state-distribution/Company"
# Expected: {"customer": N, "prospect": M, "expanding": K, ...}
```

**Step 3: Commit**

```bash
git add kernel/capability/aggregations.py
git commit -m "fix(kernel): state distribution resolves state field name"
```

---

### Task 2: Fix bulk-create org_id propagation

Temporal activities run without HTTP context, so `current_org_id.get()` returns None. The org_id must be passed through the BulkOperationSpec.

**Files:**
- Modify: `/Users/home/Repositories/indemn-os/kernel/temporal/workflows.py:168-179`
- Modify: `/Users/home/Repositories/indemn-os/kernel/api/registration.py:324-334`
- Modify: `/Users/home/Repositories/indemn-os/kernel/temporal/activities.py:227-229`

**Step 1: Add org_id to BulkOperationSpec**

In `workflows.py`, add field to the dataclass:
```python
@dataclass
class BulkOperationSpec:
    entity_type: str
    operation: str
    org_id: Optional[str] = None  # Added — propagated from API request context
    method_name: Optional[str] = None
    # ... rest unchanged
```

**Step 2: Inject org_id in the API bulk route**

In `registration.py` `_register_bulk_route()`, after `spec["entity_type"] = entity_name`:
```python
spec["entity_type"] = entity_name
spec["org_id"] = str(current_org_id.get())  # Propagate org context to Temporal
```

Add import at top of function: `from kernel.context import current_org_id`

**Step 3: Use spec.org_id in the activity**

In `activities.py` `process_bulk_batch()`, change the create branch:
```python
elif spec.operation == "create":
    org = ObjectId(spec.org_id) if spec.org_id else current_org_id.get()
    new_entity = entity_cls(org_id=org, **entity)
    await new_entity.save_tracked(method="bulk_create")
```

Also set org context for filter queries (for transition/method/update/delete operations):
```python
# At the top of process_bulk_batch, after spec = BulkOperationSpec(**spec_dict):
if spec.org_id:
    current_org_id.set(ObjectId(spec.org_id))
```

**Step 4: Commit**

```bash
git add kernel/temporal/workflows.py kernel/api/registration.py kernel/temporal/activities.py
git commit -m "fix(kernel): propagate org_id through bulk operation spec to Temporal"
```

---

### Task 3: Fix hash chain verification

Hash verification fails because datetime serialization differs between creation time and verification time (MongoDB strips timezone info and may round microseconds).

**Files:**
- Modify: `/Users/home/Repositories/indemn-os/kernel/changes/hash_chain.py:13-57`

**Step 1: Normalize datetime consistently**

Replace the `compute_hash` function to handle deserialized records:
```python
def compute_hash(record) -> str:
    """SHA-256 hash of the record content for tamper evidence."""

    def _normalize_value(val):
        """Normalize a value for consistent hashing."""
        if val is None:
            return None
        if isinstance(val, datetime):
            # Strip timezone, truncate to milliseconds for MongoDB consistency
            if val.tzinfo is not None:
                val = val.replace(tzinfo=None)
            val = val.replace(microsecond=(val.microsecond // 1000) * 1000)
            return val.strftime("%Y-%m-%dT%H:%M:%S.%f")
        if isinstance(val, ObjectId):
            return str(val)
        if isinstance(val, Decimal):
            return float(val)
        if not isinstance(val, (str, int, float, bool, list, dict)):
            return str(val)
        return val

    def _serialize_changes(changes):
        result = []
        for c in changes:
            d = c.model_dump() if hasattr(c, "model_dump") else dict(c)
            for key in ("old_value", "new_value"):
                if key in d:
                    d[key] = _normalize_value(d[key])
            result.append(d)
        return result

    ts = _normalize_value(record.timestamp)
    content = orjson.dumps(
        {
            "entity_type": record.entity_type,
            "entity_id": str(record.entity_id),
            "change_type": record.change_type,
            "actor_id": record.actor_id,
            "timestamp": ts,
            "changes": _serialize_changes(record.changes),
            "previous_hash": record.previous_hash,
        },
        option=orjson.OPT_SORT_KEYS,
        default=str,
    )
    return hashlib.sha256(content).hexdigest()
```

Add `from decimal import Decimal` and ensure `from bson import ObjectId` is imported.

**Step 2: Verify**

```bash
export INDEMN_API_URL=https://indemn-api-production.up.railway.app
indemn audit verify --limit 10
# Expected: {"chain_valid": true, "records_checked": N}
```

**Step 3: Commit**

```bash
git add kernel/changes/hash_chain.py
git commit -m "fix(kernel): normalize datetime and ObjectId in hash chain verification"
```

---

### Task 4: Verify and fix search on kernel entity endpoints

Domain entity routes have `?search=` support. Verify kernel entities (Actor, Role, Integration) also do — they should since they go through the same `register_entity_routes()`.

**Files:**
- Verify: `/Users/home/Repositories/indemn-os/kernel/api/app.py:87-94`

**Step 1: Verify which entities get auto-registered routes**

Check `_INFRASTRUCTURE` set in app.py. Actor, Role, Integration should NOT be in this set, meaning they get `register_entity_routes()` which includes search.

**Step 2: Test directly**

```bash
curl -H "Authorization: Bearer $TOKEN" "$API/api/actors/?search=Craig"
# Expected: actors with "Craig" in name
curl -H "Authorization: Bearer $TOKEN" "$API/api/roles/?search=team"
# Expected: team_member role
```

**Step 3: If search doesn't work on kernel entities**

Check if kernel entity routes are registered via a different path (admin_routes). If so, add `search` parameter to those custom routes.

**Step 4: Commit (if changes needed)**

```bash
git add kernel/api/admin_routes.py  # or app.py
git commit -m "fix(kernel): search support on kernel entity endpoints"
```

---

### Task 5: Verify changes timeline data

The changes timeline may show "No changes" for some entities. Verify that `write_change_record()` is called on every `save_tracked()` and that the trace endpoint returns the correct data.

**Files:**
- Verify: `/Users/home/Repositories/indemn-os/kernel/entity/save.py` (write_change_record call)
- Verify: `/Users/home/Repositories/indemn-os/kernel/api/trace_routes.py` (query logic)

**Step 1: Verify via API**

```bash
# Get a company ID that was transitioned
COMPANY_ID=$(indemn company list --limit 1 | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['_id'])")

# Query trace endpoint directly
curl -H "Authorization: Bearer $TOKEN" "$API/api/trace/entity/Company/$COMPANY_ID?limit=10"
# Expected: timeline with change entries (source: "changes")
```

**Step 2: If timeline is empty, check MongoDB directly**

```bash
mongosh-connect.sh dev indemn_os --eval "db.change_records.find({entity_type: 'Company'}).limit(3).pretty()"
```

**Step 3: If changes exist in DB but trace returns empty**

Check trace_routes.py query — ensure `entity_type` matches exactly (case-sensitive). The trace endpoint queries `{"entity_type": entity_type}` where entity_type comes from the URL. Verify the URL uses the entity name (e.g., "Company") not the slug (e.g., "companys").

**Step 4: Commit (if changes needed)**

```bash
git commit -m "fix(kernel): trace entity query matches entity_type correctly"
```

---

### Task 6: Conversation persistence across reloads

Store the interaction_id in localStorage and transmit it on WebSocket reconnect so the harness reuses the existing conversation thread.

**Files:**
- Modify: `/Users/home/Repositories/indemn-os/ui/src/assistant/AssistantProvider.tsx`
- Modify: `/Users/home/Repositories/indemn-os/harnesses/chat-deepagents/main.py`
- Modify: `/Users/home/Repositories/indemn-os/harnesses/chat-deepagents/session.py`

**Step 1: UI — store and transmit interaction_id**

In `AssistantProvider.tsx`, add state for interaction_id:
```typescript
const INTERACTION_KEY = "indemn_assistant_interaction_id";
const [interactionId, setInteractionId] = useState<string | null>(
  () => localStorage.getItem(INTERACTION_KEY)
);
```

In the WebSocket connect message, include it:
```typescript
ws.send(JSON.stringify({
  type: "connect",
  associate_id: associateId,
  auth_token: getToken(),
  interaction_id: interactionId,  // Resume previous conversation
}));
```

On receiving `connected` response, store the interaction_id:
```typescript
case "connected":
  connectedRef.current = true;
  if (data.interaction_id) {
    setInteractionId(String(data.interaction_id));
    localStorage.setItem(INTERACTION_KEY, String(data.interaction_id));
  }
  break;
```

On "New Conversation", clear it:
```typescript
const clearMessages = useCallback(() => {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(INTERACTION_KEY);
  setInteractionId(null);
  setMessages([]);
}, []);
```

**Step 2: Harness — accept optional interaction_id**

In `main.py`, extract interaction_id from connect message:
```python
interaction_id = connect_msg.get("interaction_id")
session = ChatSession(websocket, associate_id, auth_token, interaction_id=interaction_id)
```

In `session.py` `__init__`:
```python
def __init__(self, websocket, associate_id, auth_token, interaction_id=None):
    self.interaction_id = interaction_id  # Reuse if provided
```

In `session.py` `start()`, only create new Interaction if not provided:
```python
if self.interaction_id:
    logger.info(f"Resuming interaction: {self.interaction_id}")
else:
    self.interaction_id = indemn("interaction", "create", ...)
    logger.info(f"Created Interaction: {self.interaction_id}")
```

**Step 3: Commit**

```bash
git add ui/src/assistant/AssistantProvider.tsx harnesses/chat-deepagents/main.py harnesses/chat-deepagents/session.py
git commit -m "feat: conversation persistence — reuse interaction_id across reconnects"
```

---

### Task 7: Assistant session warmup — reduce first response latency

Move session initialization from message handler to WebSocket connect phase. Parallelize CLI calls.

**Files:**
- Modify: `/Users/home/Repositories/indemn-os/harnesses/chat-deepagents/session.py:54-116`
- Modify: `/Users/home/Repositories/indemn-os/harnesses/chat-deepagents/main.py:105-161`

**Step 1: Move session.start() to connect phase**

In `main.py`, call `session.start()` immediately after receiving the connect message, BEFORE sending the `connected` response:
```python
# After receiving connect message:
session = ChatSession(websocket, associate_id, auth_token, interaction_id=interaction_id)
await session.start()  # Initialize BEFORE confirming connection
await websocket.send_json({"type": "connected", "interaction_id": session.interaction_id})
```

**Step 2: Parallelize CLI calls in session.start()**

In `session.py`, use `asyncio.gather()` for independent CLI calls:
```python
async def start(self):
    loop = asyncio.get_event_loop()
    # Parallel: load associate, runtime, and skills simultaneously
    associate_future = loop.run_in_executor(None, indemn, "actor", "get", self.associate_id)
    
    associate = await associate_future
    self.associate = json.loads(associate)
    
    # Load skills in parallel
    skill_refs = self.associate.get("skills", [])
    skill_futures = [
        loop.run_in_executor(None, indemn, "skill", "get", ref)
        for ref in skill_refs
    ]
    skill_results = await asyncio.gather(*skill_futures, return_exceptions=True)
    self.skill_contents = [
        json.loads(r)["content"] for r in skill_results if not isinstance(r, Exception)
    ]
    # ... continue with Interaction + Attention creation
```

**Step 3: Commit**

```bash
git add harnesses/chat-deepagents/session.py harnesses/chat-deepagents/main.py
git commit -m "perf: parallelize session initialization, move to connect phase"
```

---

### Task 8: Assistant tool exposure — CLI as tools for create/transition/update/query

The assistant must be able to perform entity operations via the CLI. The deepagents framework needs tool definitions that map to CLI commands.

**Files:**
- Modify: `/Users/home/Repositories/indemn-os/harnesses/chat-deepagents/agent.py:14-34`
- Modify: `/Users/home/Repositories/indemn-os/harnesses/_base/harness_common/backend.py:28-50`

**Step 1: Understand current tool setup**

Read `agent.py` and `backend.py` to understand how deepagents creates the agent. The LocalShellBackend gives the agent a shell tool (execute command). The agent should already be able to run `indemn company list` etc. via the shell tool.

If the shell tool exists, the issue is the SYSTEM PROMPT — the assistant needs instructions on how to use the CLI. The entity skills document the commands but the assistant may not know to use them proactively.

**Step 2: Enhance the system prompt**

In `agent.py`, prepend operational instructions to the system prompt:
```python
ASSISTANT_SYSTEM_PROMPT = """You are the Indemn OS Assistant. You help users manage their insurance operations through the Indemn OS.

## Your Capabilities
You can perform ANY operation the user can do, using the `indemn` CLI. Key commands:
- `indemn {entity} list [--limit N] [--status STATE]` — list entities
- `indemn {entity} get ID` — get entity details
- `indemn {entity} create --data 'JSON'` — create entity
- `indemn {entity} update ID --data 'JSON'` — update fields
- `indemn {entity} transition ID --to STATE` — change state
- Entity types: Company, Contact, Deal, Conference, Task, Meeting, Signal, Decision, Commitment, AssociateDeployment, Outcome, Playbook, Stage, OutcomeType, AssociateType

## Guidelines
- When asked about the current entity, use the context provided (entity_data).
- When asked to create or modify, use the CLI via the execute tool.
- When querying across entities, use `indemn {entity} list` with appropriate filters.
- Always confirm destructive actions (transitions, deletions) before executing.
- Format CLI output readably for the user.

## Entity Skills (loaded below)
The following skills describe each entity's fields, lifecycle, and commands:
"""
```

Then concatenate skill contents after this preamble.

**Step 3: Verify the execute tool works**

The backend's execute tool should already allow running shell commands. If it does, the improved system prompt + skills should be sufficient for the assistant to use CLI commands.

If the execute tool doesn't exist, create one:
```python
from deepagents.tools import Tool

class ExecuteTool(Tool):
    name = "execute"
    description = "Execute a shell command. Use for indemn CLI operations."
    
    async def run(self, command: str) -> str:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
```

**Step 4: Commit**

```bash
git add harnesses/chat-deepagents/agent.py
git commit -m "feat: assistant system prompt with CLI operation instructions"
```

---

### Task 9: Bulk actions in UI

Add row selection checkboxes and a bulk action bar to entity list views.

**Files:**
- Modify: `/Users/home/Repositories/indemn-os/ui/src/components/EntityTable.tsx`
- Modify: `/Users/home/Repositories/indemn-os/ui/src/views/EntityListView.tsx`

**Step 1: Add row selection to EntityTable**

```typescript
import { useState } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type RowSelectionState,
} from "@tanstack/react-table";

interface Props {
  columns: ColumnDef<Record<string, unknown>>[];
  data: Record<string, unknown>[];
  onRowClick?: (row: Record<string, unknown>) => void;
  enableSelection?: boolean;
  onSelectionChange?: (selectedIds: string[]) => void;
}

export function EntityTable({ columns, data, onRowClick, enableSelection, onSelectionChange }: Props) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

  const allColumns: ColumnDef<Record<string, unknown>>[] = enableSelection
    ? [
        {
          id: "select",
          header: ({ table }) => (
            <input
              type="checkbox"
              checked={table.getIsAllPageRowsSelected()}
              onChange={table.getToggleAllPageRowsSelectedHandler()}
              className="h-4 w-4"
            />
          ),
          cell: ({ row }) => (
            <input
              type="checkbox"
              checked={row.getIsSelected()}
              onChange={row.getToggleSelectedHandler()}
              onClick={(e) => e.stopPropagation()}
              className="h-4 w-4"
            />
          ),
          size: 40,
        },
        ...columns,
      ]
    : columns;

  const table = useReactTable({
    data,
    columns: allColumns,
    state: { sorting, columnFilters, rowSelection },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onRowSelectionChange: (updater) => {
      const newSelection = typeof updater === "function" ? updater(rowSelection) : updater;
      setRowSelection(newSelection);
      if (onSelectionChange) {
        const selectedIds = Object.keys(newSelection)
          .filter((k) => newSelection[k])
          .map((k) => String(data[Number(k)]?._id || ""));
        onSelectionChange(selectedIds);
      }
    },
    enableRowSelection: enableSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });
  // ... rest of render unchanged
```

**Step 2: Add bulk action bar to EntityListView**

After the search/filter bar and before the table, add:
```typescript
const [selectedIds, setSelectedIds] = useState<string[]>([]);

// In render, between filter bar and EntityTable:
{selectedIds.length > 0 && meta.state_machine && (
  <div className="flex items-center gap-3 mb-3 p-3 bg-blue-50 rounded border border-blue-200">
    <span className="text-sm font-medium">{selectedIds.length} selected</span>
    {Object.keys(meta.state_machine).map((targetState) => (
      <button
        key={targetState}
        onClick={async () => {
          if (!window.confirm(`Transition ${selectedIds.length} items to "${targetState}"?`)) return;
          for (const id of selectedIds) {
            try {
              await apiClient(`/api/${entityType}/${id}/transition`, {
                method: "POST",
                body: JSON.stringify({ to: targetState }),
              });
            } catch { /* skip failures */ }
          }
          setSelectedIds([]);
          refetch();
        }}
        className="px-2 py-1 text-xs border rounded hover:bg-white"
      >
        → {targetState}
      </button>
    ))}
    <button onClick={() => setSelectedIds([])} className="ml-auto text-xs text-gray-500 hover:text-gray-700">
      Clear selection
    </button>
  </div>
)}

// Pass to EntityTable:
<EntityTable
  columns={columns}
  data={entities || []}
  onRowClick={(row) => navigate(`/${entityType}/${row._id}`)}
  enableSelection={!!meta.state_machine && meta.permissions.write}
  onSelectionChange={setSelectedIds}
/>
```

**Step 3: Build locally to verify**

```bash
cd ui && npm run build
```

**Step 4: Commit**

```bash
git add ui/src/components/EntityTable.tsx ui/src/views/EntityListView.tsx
git commit -m "feat(ui): bulk actions — row selection + bulk transition bar"
```

---

### Task 10: Deploy all fixes

**Step 1: Push all commits**
```bash
git push origin main
```

**Step 2: Deploy all services**
```bash
railway up --service indemn-api --detach
railway up --service indemn-ui --detach
railway up --service indemn-runtime-chat --detach
railway up --service indemn-temporal-worker --detach
```

**Step 3: Wait and verify health**
```bash
sleep 180
curl -s $API/health
```

**Step 4: Browser test each fix**
- Observability: state distribution cards should now show data
- Company list: bulk action checkboxes visible
- Assistant: should respond faster, able to create/transition entities
- Conversation: reload page, conversation should persist
