---
ask: "What MongoDB collections and fields are relevant to GIC chat analytics and the time-of-day feature?"
created: 2026-02-26
workstream: gic-observatory
session: 2026-02-26-a
sources:
  - type: mongodb
    description: "Explored tiledesk database collections, field structures, and query patterns"
  - type: codebase
    description: "Observatory ingestion connectors, aggregation engine, API data access layer"
---

# MongoDB Data Model for GIC Analytics

## Critical Constraint

**READ-ONLY ACCESS**: The production MongoDB database (`MONGODB_PROD_URI`) is read-only. You cannot write to it. All data processing must happen in application code. Never attempt insert/update/delete operations on production.

## Connection

```bash
# Environment variable
MONGODB_PROD_URI=mongodb+srv://devadmin:...@prod-indemn.../tiledesk

# CLI
source .env && mongosh "$MONGODB_PROD_URI" --quiet --eval '...'

# Python (Motor async driver)
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(os.environ["MONGODB_PROD_URI"])
db = client["tiledesk"]
```

## Databases on Cluster

| Database | Size | Relevance |
|----------|------|-----------|
| **tiledesk** | 11.4 GB | Primary — orgs, conversations, messages, bots |
| **observatory** | 0.9 GB | Pre-computed analytics (snapshots, distributions) |
| chat21 | 2.5 GB | Legacy chat engine |
| quotes | 0.2 GB | Insurance quote data |

## Collections Relevant to Time-of-Day Feature

### 1. `organizations` — Find GIC

```javascript
// Find GIC organization
db.organizations.findOne({name: /geico|gic/i}, {_id: 1, name: 1})
// Returns: { _id: ObjectId("..."), name: "GIC Underwriters" }
```

Key fields: `_id` (ObjectId — used as foreign key everywhere), `name`, `active`, `isEnterpriseAccount`

### 2. `requests` — Conversation Records (132,099 docs)

This is the core conversations collection. Each document = one chat session.

**Fields critical to the feature:**

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique conversation ID (e.g., `support-group-...-a80ba525...`) |
| `id_organization` | ObjectId | Links to GIC org |
| `createdAt` | datetime | Conversation start time (UTC) |
| `closed_at` | datetime | Conversation end time |
| `assigned_at` | datetime | When assigned to CSR |
| `participantsAgents` | array[string] | **CSR user IDs** who participated |
| `participantsBots` | array[string] | Bot IDs involved |
| `hasBot` | boolean | Was a bot involved |
| `status` | int | 100=pending, 200=assigned, 1000=closed |
| `depth` | int | Message count |
| `attributes` | object | Custom metadata |
| `attributes.conversation_start_time` | string (ISO) | Conversation start as ISO string |

**Sample query — GIC conversations in February 2026:**
```javascript
db.requests.find({
  id_organization: ObjectId("<GIC_ORG_ID>"),
  createdAt: {
    $gte: ISODate("2026-02-01T00:00:00Z"),
    $lt: ISODate("2026-03-01T00:00:00Z")
  },
  status: 1000  // closed conversations only
}).sort({createdAt: -1})
```

### 3. `messages` — Individual Messages (1,951,527 docs)

**This is the key collection for time-of-day CSR analysis.** Each document = one message in a conversation.

**Fields critical to the feature:**

| Field | Type | Description |
|-------|------|-------------|
| `recipient` | string | Conversation ID — joins to `requests.request_id` |
| `sender` | string | User/CSR ID who sent the message |
| `senderFullname` | string | **CSR name** (e.g., "John Smith") or `"guest#257f"` for users |
| `text` | string | Message content |
| `type` | string | Message type (text, image, etc.) |
| `createdAt` | datetime | **Message timestamp** — this is what we bucket into 20-min intervals |
| `channel_type` | string | chat21, web, etc. |

**How to identify CSR messages vs user messages:**
- CSR messages: `senderFullname` does NOT start with `"guest#"`
- User messages: `senderFullname` starts with `"guest#"` or is a UUID
- Bot messages: `sender` matches a bot ID from `participantsBots`

**Sample query — CSR messages for a GIC conversation:**
```javascript
// Get all messages for a conversation
db.messages.find({
  recipient: "support-group-...-a80ba525..."
}).sort({createdAt: 1})

// Filter to CSR messages only (not guest/bot)
db.messages.find({
  recipient: "support-group-...-a80ba525...",
  senderFullname: {$not: /^guest#/}
  // Note: also need to exclude bot messages by checking sender against participantsBots
})
```

### 4. `project_users` — CSR Identity Lookup

Maps user IDs to names and roles. Useful if `senderFullname` is incomplete.

| Field | Type | Description |
|-------|------|-------------|
| `id_user` | ObjectId | User ID |
| `id_project` | string | Org ID |
| `role` | string | agent, admin, owner |
| `user_available` | boolean | Online status |

### 5. `observatory_conversations` — Processed Conversations

Pre-processed by the ingestion pipeline with derived fields:
- `outcome` (classified)
- `intent` (classified)
- `resolution_path`
- `system_tags` (handoff_needed_ever, missed_handoff, out_of_hours_handoff)
- `csr_time_to_join_seconds`
- Tool call results

**Not** the source of truth for message-level timestamps — use `messages` for that.

### 6. `daily_snapshots` — Pre-computed Aggregations

Already includes `by_hour` (0-23) for conversation volume. This is aggregate conversation starts, not per-CSR message activity.

## Query Pattern for Time-of-Day Feature

### Step 1: Get GIC org ID
```javascript
const org = db.organizations.findOne({name: /gic/i})
const orgId = org._id
```

### Step 2: Get GIC conversations in date range
```javascript
const conversations = db.requests.find({
  id_organization: orgId,
  status: 1000,
  createdAt: {$gte: ISODate("2026-02-01"), $lt: ISODate("2026-03-01")}
}).toArray()
```

### Step 3: Get CSR messages for those conversations
```javascript
const requestIds = conversations.map(c => c.request_id)
const csrMessages = db.messages.find({
  recipient: {$in: requestIds},
  senderFullname: {$not: /^guest#/}
  // Further filter: exclude bot senders
}).toArray()
```

### Step 4: Bucket into 20-minute intervals
```python
for msg in csr_messages:
    ts = msg["createdAt"]
    hour = ts.hour
    bucket_index = ts.minute // 20  # 0, 1, or 2
    time_label = f"{hour:02d}:{bucket_index*20:02d}-{hour:02d}:{bucket_index*20+19:02d}"
    csr_name = msg["senderFullname"]
    # Accumulate: csr_activity[csr_name][time_label] += 1
```

### MongoDB Aggregation Pipeline (Alternative)

```javascript
db.messages.aggregate([
  // Match messages from GIC conversations
  {$match: {
    recipient: {$in: requestIds},
    senderFullname: {$not: /^guest#/}
  }},
  // Extract time components
  {$project: {
    csr_name: "$senderFullname",
    hour: {$hour: "$createdAt"},
    minute_bucket: {$floor: {$divide: [{$minute: "$createdAt"}, 20]}}
  }},
  // Group by CSR + time bucket
  {$group: {
    _id: {csr: "$csr_name", hour: "$hour", bucket: "$minute_bucket"},
    count: {$sum: 1}
  }},
  {$sort: {"_id.hour": 1, "_id.bucket": 1}}
])
```

## Important Notes

- All timestamps are **UTC**. GIC is likely in a US time zone — may need to convert for display.
- `senderFullname` is the most reliable CSR identifier available in messages. Cross-reference with `project_users` if needed.
- The `messages` collection is large (1.9M docs). Always filter by `recipient` (conversation IDs) first, then by sender type.
- Bot messages also won't have `guest#` prefix — filter them out by checking against `requests.participantsBots` for each conversation.
