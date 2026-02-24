# MongoDB Query Patterns

Common queries, service ownership map, ID resolution chains, and aggregation patterns. All examples use `mongosh` with `--quiet --eval`.

---

## SERVICE-TO-COLLECTION MAP

| Service | Writes To | Reads From |
|---------|-----------|------------|
| **copilot-server** | organizations, projects, users, project_users, departments, faq_kbs, bot_configurations, bot_tools, bot_tools_parameters, bot_kb_mappings, llm_configurations, distributions, channel_configurations, subscriptions, billing_subscriptions, invoices, triggers | Most collections |
| **bot-service** | knowledge_bases_tracking, traces | faq_kbs, bot_configurations, bot_tools, llm_configurations, bot_kb_mappings, knowledge_bases, requests |
| **kb-service** | knowledge_bases, knowledge_bases_data_sources, knowledge_base_scrape_request_details, knowledge_bases_scrapped_faqs | knowledge_bases, bot_kb_mappings |
| **conversation-service** | messages | requests, messages |
| **middleware-socket-service** | middleware.tiledesksyncs | requests, messages, leads |
| **voice-service** | voice_configurations | voice_configurations, channel_configurations |
| **payment-service** | payment_logs, stripe_meters, invoices | billing_subscriptions, subscription_plans, stripe_prices |
| **copilot-sync-service** | subscriptionlogs | subscriptions |
| **indemn-observability** | observatory.*, observatory_conversations, traces, daily_snapshots, category_distributions, flow_*, precursor_lifts, structure_*, processing_runs, failed_conversations | requests, messages, traces |
| **evaluations** | evaluation_runs, evaluation_results, test_cases, datasets, rubrics, evaluator_configs | faq_kbs, bot_configurations |
| **indemn-platform-v2** | platform_agents, platform_templates, platform_components, platform_conversations | platform_* |

---

## DATABASE-TO-COLLECTION MAP

| Database | Key Collections |
|----------|----------------|
| **tiledesk** | organizations, projects, faq_kbs, bot_configurations, bot_tools, knowledge_bases, requests, messages, traces, leads, subscriptionlogs, observatory_conversations, all billing, all eval |
| **observatory** | conversations, traces, daily_snapshots, category_distributions, flow_links, flow_paths, flow_stage_totals, precursor_lifts, structure_*, processing_runs, failed_conversations |
| **middleware** | tiledesksyncs |
| **quotes** | quotes, quote_configs, style_configs |
| **airtable_sync** | venue_details, quote_details, multiple_quote_config, marketing_pricing_pages, *_quote_details |
| **chat21** | conversations, groups, messages (legacy chat engine) |

---

## ID RESOLUTION CHAINS

### Organization → Projects → Bots → Tools → KBs
```javascript
// 1. Find org
const org = db.getCollection("organizations").findOne({name: "Indemn"})
// 2. Get projects for org
const projects = db.getCollection("projects").find({id_organization: org._id.toString()}).toArray()
// 3. Get bots for org (via bot_kb_mappings junction)
const botIds = db.getCollection("bot_kb_mappings").distinct("id_bot", {id_organization: org._id})
// 4. Get bot configs
const configs = db.getCollection("bot_configurations").find({bot_id: {$in: botIds}}).toArray()
// 5. Get tools for those bots
const tools = db.getCollection("bot_tools").find({bot_id: {$in: botIds}}).toArray()
// 6. Get KBs for those bots
const kbIds = db.getCollection("bot_kb_mappings").distinct("id_kb", {id_organization: org._id})
const kbs = db.getCollection("knowledge_bases").find({_id: {$in: kbIds}}).toArray()
```

### Conversation → Messages → Traces
```javascript
// 1. Find a conversation
const req = db.getCollection("requests").findOne({request_id: "<request_id>"})
// 2. Get messages
const msgs = db.getCollection("messages").find({recipient: req.request_id}).sort({createdAt: 1}).toArray()
// 3. Get LLM traces
const traces = db.getCollection("traces").find({conversation_id: req.request_id}).sort({start_time: 1}).toArray()
// 4. Get enriched observatory view (if processed)
const obsConv = db.getCollection("observatory_conversations").findOne({conversation_id: req.request_id})
```

### Bot → LLM Config → Channel Config → Distribution
```javascript
const botId = ObjectId("<bot_id>") // from faq_kbs._id
const llmConfig = db.getCollection("llm_configurations").findOne({id_bot: botId})
const channelConfig = db.getCollection("channel_configurations").findOne({id_bot: botId})
const distributions = db.getCollection("distributions").find({id_bot: botId}).toArray()
const preview = db.getCollection("bot_previews").findOne({id_bot: botId})
```

---

## COMMON QUERY PATTERNS

### PATTERN: List all organizations with bot counts
```javascript
JSON.stringify(db.getCollection("organizations").aggregate([
  {$match: {active: true}},
  {$lookup: {
    from: "bot_kb_mappings",
    localField: "_id",
    foreignField: "id_organization",
    as: "mappings"
  }},
  {$project: {
    name: 1,
    botCount: {$size: {$setUnion: "$mappings.id_bot"}},
    kbCount: {$size: {$setUnion: "$mappings.id_kb"}}
  }},
  {$sort: {botCount: -1}}
]).toArray(), null, 2)
```

### PATTERN: Get all bots for an organization with their tools and KBs
```javascript
const orgId = ObjectId("<org_id>")
const mappings = db.getCollection("bot_kb_mappings").find({id_organization: orgId}).toArray()
const botIds = [...new Set(mappings.map(m => m.id_bot.toString()))].map(id => ObjectId(id))

botIds.forEach(botId => {
  const config = db.getCollection("bot_configurations").findOne({bot_id: botId})
  const llm = db.getCollection("llm_configurations").findOne({id_bot: botId})
  const tools = db.getCollection("bot_tools").find({bot_id: botId, isDeleted: {$ne: true}}).toArray()
  const kbMappings = mappings.filter(m => m.id_bot.toString() === botId.toString())
  print(JSON.stringify({
    bot_id: botId,
    name: config?.bot_name || "unknown",
    llm: llm ? `${llm.provider}/${llm.model}` : "none",
    tools: tools.map(t => t.type),
    kbs: kbMappings.length
  }))
})
```

### PATTERN: Get conversation history with messages
```javascript
const requestId = "<request_id>"
const req = db.getCollection("requests").findOne({request_id: requestId})
const msgs = db.getCollection("messages").find(
  {recipient: requestId},
  {sender: 1, senderFullname: 1, text: 1, type: 1, createdAt: 1}
).sort({createdAt: 1}).toArray()
JSON.stringify({
  status: req.status,
  first_text: req.first_text,
  hasBot: req.hasBot,
  messages: msgs.map(m => ({
    from: m.senderFullname,
    text: m.text?.substring(0, 200),
    time: m.createdAt
  }))
}, null, 2)
```

### PATTERN: Get conversations for an organization in a date range
```javascript
JSON.stringify(db.getCollection("requests").find({
  id_organization: ObjectId("<org_id>"),
  status: 1000,
  createdAt: {
    $gte: new Date("2025-01-01"),
    $lt: new Date("2025-02-01")
  }
}, {
  request_id: 1, first_text: 1, hasBot: 1, createdAt: 1, closed_at: 1
}).sort({createdAt: -1}).limit(20).toArray(), null, 2)
```

### PATTERN: Tool type distribution across all bots
```javascript
JSON.stringify(db.getCollection("bot_tools").aggregate([
  {$match: {isDeleted: {$ne: true}}},
  {$group: {_id: "$type", count: {$sum: 1}}},
  {$sort: {count: -1}}
]).toArray(), null, 2)
```

### PATTERN: KB content stats per organization
```javascript
JSON.stringify(db.getCollection("knowledge_bases").aggregate([
  {$match: {isTrashed: {$ne: true}}},
  {$group: {_id: {org: "$id_organization", type: "$type"}, count: {$sum: 1}}},
  {$sort: {"_id.org": 1, count: -1}}
]).toArray(), null, 2)
```

### PATTERN: LLM model usage across all bots
```javascript
JSON.stringify(db.getCollection("llm_configurations").aggregate([
  {$group: {_id: {provider: "$provider", model: "$model"}, count: {$sum: 1}}},
  {$sort: {count: -1}}
]).toArray(), null, 2)
```

### PATTERN: Voice numbers for an organization
```javascript
JSON.stringify(db.getCollection("voice_configurations").find(
  {id_organization: ObjectId("<org_id>"), isTrashed: false},
  {phoneNumber: 1, friendlyName: 1, voice: 1, greetingMessage: 1}
).toArray(), null, 2)
```

### PATTERN: Conversation volume by status
```javascript
JSON.stringify(db.getCollection("requests").aggregate([
  {$group: {_id: "$status", count: {$sum: 1}}},
  {$sort: {count: -1}}
]).toArray(), null, 2)
// Status: 100=pending, 200=assigned, 1000=closed
```

### PATTERN: Recent conversations with bot involvement
```javascript
JSON.stringify(db.getCollection("requests").find(
  {hasBot: true, status: 1000},
  {request_id: 1, first_text: 1, id_organization: 1, createdAt: 1, closed_at: 1, depth: 1}
).sort({createdAt: -1}).limit(10).toArray(), null, 2)
```

### PATTERN: Token usage from traces for a conversation
```javascript
JSON.stringify(db.getCollection("traces").aggregate([
  {$match: {conversation_id: "<request_id>"}},
  {$group: {
    _id: null,
    total_prompt_tokens: {$sum: "$prompt_tokens"},
    total_completion_tokens: {$sum: "$completion_tokens"},
    total_tokens: {$sum: "$total_tokens"},
    trace_count: {$sum: 1}
  }}
]).toArray(), null, 2)
```

### PATTERN: Observatory conversation analytics by outcome
```javascript
JSON.stringify(db.getCollection("observatory_conversations").aggregate([
  {$match: {"scope.customer_id": "<org_id>"}},
  {$group: {_id: "$outcome_group", count: {$sum: 1}}},
  {$sort: {count: -1}}
]).toArray(), null, 2)
```

### PATTERN: Billing subscription status for an org
```javascript
JSON.stringify(db.getCollection("billing_subscriptions").aggregate([
  {$match: {id_organization: "<org_id>"}},
  {$lookup: {
    from: "subscription_plans",
    localField: "id_plan",
    foreignField: "_id",
    as: "plan"
  }},
  {$unwind: "$plan"},
  {$project: {
    status: 1,
    seats: 1,
    currentPeriodStart: 1,
    currentPeriodEnd: 1,
    planTitle: "$plan.title",
    planTier: "$plan.tier",
    planPrice: "$plan.price",
    isCanceled: 1
  }}
]).toArray(), null, 2)
```

### PATTERN: Quote data for a conversation
```javascript
// In quotes database:
// mongosh "$MONGODB_PROD_URI/quotes" --quiet --eval '...'
JSON.stringify(db.getCollection("quotes").findOne(
  {conversation_id: "<request_id>"}
), null, 2)
```

### PATTERN: Active agents in the last N days
```javascript
// "Active" means the agent handled conversations (appeared in requests.participantsBots)
// Adjust daysAgo for different windows (7, 30, 90)
const daysAgo = 7
const since = new Date(Date.now() - daysAgo*24*60*60*1000)

const result = db.getCollection("requests").aggregate([
  {$match: {createdAt: {$gte: since}, participantsBots: {$exists: true, $ne: []}}},
  {$unwind: "$participantsBots"},
  {$group: {_id: "$participantsBots", conversations: {$sum: 1}, lastActive: {$max: "$createdAt"}}},
  {$sort: {conversations: -1}}
]).toArray()

// Resolve bot IDs to names + project names
const botIds = result.map(r => new ObjectId(r._id))
const bots = db.getCollection("faq_kbs").find({_id: {$in: botIds}}, {name: 1, id_project: 1}).toArray()
const botMap = Object.fromEntries(bots.map(b => [b._id.toString(), b]))

const projIds = [...new Set(bots.map(b => b.id_project))].filter(Boolean)
const projs = db.getCollection("projects").find({_id: {$in: projIds.map(id => new ObjectId(id))}}, {name: 1}).toArray()
const projMap = Object.fromEntries(projs.map(p => [p._id.toString(), p.name]))

print("Active agents (last " + daysAgo + " days): " + result.length + "\n")
result.forEach(r => {
  const bot = botMap[r._id] || {}
  const proj = projMap[bot.id_project] || "unknown"
  print(r.conversations + " convos | " + (bot.name || "unnamed") + " | " + proj + " | last: " + r.lastActive.toISOString().split("T")[0])
})
```

### PATTERN: Find a bot by name
```javascript
const bot = db.getCollection("faq_kbs").findOne({name: /search term/i, trashed: false})
if (bot) {
  const config = db.getCollection("bot_configurations").findOne({bot_id: bot._id})
  const llm = db.getCollection("llm_configurations").findOne({id_bot: bot._id})
  const toolCount = db.getCollection("bot_tools").countDocuments({bot_id: bot._id, isDeleted: {$ne: true}})
  print(JSON.stringify({
    id: bot._id,
    name: bot.name,
    project: bot.id_project,
    org: bot.id_organization,
    type: bot.type,
    systemPrompt: config?.ai_config?.system_prompt?.substring(0, 200),
    llm: llm ? `${llm.provider}/${llm.model}` : "none",
    tools: toolCount
  }, null, 2))
}
```

---

## AGGREGATION PATTERNS

### $lookup chain: Org → Bots → Tools
```javascript
db.getCollection("organizations").aggregate([
  {$match: {name: "Indemn"}},
  {$lookup: {
    from: "bot_kb_mappings",
    localField: "_id",
    foreignField: "id_organization",
    as: "mappings"
  }},
  {$unwind: "$mappings"},
  {$lookup: {
    from: "bot_tools",
    localField: "mappings.id_bot",
    foreignField: "bot_id",
    as: "tools"
  }},
  {$unwind: "$tools"},
  {$group: {
    _id: "$tools.type",
    count: {$sum: 1}
  }},
  {$sort: {count: -1}}
])
```

### Daily message volume
```javascript
db.getCollection("messages").aggregate([
  {$match: {createdAt: {$gte: new Date("2025-01-01")}}},
  {$group: {
    _id: {$dateToString: {format: "%Y-%m-%d", date: "$createdAt"}},
    count: {$sum: 1}
  }},
  {$sort: {_id: -1}},
  {$limit: 30}
])
```

### Conversation duration stats
```javascript
db.getCollection("requests").aggregate([
  {$match: {status: 1000, closed_at: {$ne: null}}},
  {$project: {
    duration_minutes: {
      $divide: [{$subtract: ["$closed_at", "$createdAt"]}, 60000]
    }
  }},
  {$group: {
    _id: null,
    avg: {$avg: "$duration_minutes"},
    min: {$min: "$duration_minutes"},
    max: {$max: "$duration_minutes"},
    count: {$sum: 1}
  }}
])
```

---

## CROSS-DATABASE QUERIES

To query across databases, run separate mongosh commands:

```bash
# Get conversation from tiledesk, then quotes from quotes DB
REQ_ID=$(source .env && mongosh "$MONGODB_PROD_URI/tiledesk" --quiet --eval '
  db.getCollection("requests").findOne({first_text: /insurance/i}, {request_id: 1}).request_id
')
source .env && mongosh "$MONGODB_PROD_URI/quotes" --quiet --eval "
  JSON.stringify(db.getCollection('quotes').findOne({conversation_id: '$REQ_ID'}), null, 2)
"
```

---

## BILLING-ALIGNED USAGE FILTER

When counting conversations for usage reporting that should match Stripe billing numbers, apply this filter to the `requests` collection:

```javascript
{
  status: 1000,            // closed conversations only
  isTestMode: { $ne: true }, // exclude test mode
  depth: { $gt: 2 }        // more than 2 messages (bot greeting + user msg + bot response minimum)
}
```

**Why this filter:**
- `stripe_meters` collection (29.5K docs) is the billing source of truth — one entry per billable conversation
- `stripe_meters` has two meter types: `chat_conv_count` and `voice_duration_minutes`
- This filter on `requests` matches `stripe_meters` counts within ~1-2% (small diffs are timing: meter event timestamp vs request createdAt may cross month boundaries)
- Verified empirically 2026-02-24 across GIC, Bonzah, Rankin, Distinguished, Open Enrolment

**Test/internal organizations to exclude from customer-facing usage reports:**

| Org Name | ID | Reason |
|----------|-----|--------|
| Indemn | `65e18047b26fd2526e096cd0` | Internal |
| Demos | `66c0920c358d3f001351c22c` | Demo showcase (50+ bots) |
| Voice Demos | `66d196e9cc5cd70013e46565` | Voice prototypes |
| test-dolly-prod | `66fc8ab493b5a40013596cd7` | Test account |
| InsuranceTrak | `65e60f70683d12001386515a` | Legacy test |

**EventGuard is NOT a test org** — it's a real customer (Jewelers Mutual product) despite high volume.

### PATTERN: Billable conversations by org by month
```javascript
var excludeOrgs = [
  ObjectId("65e18047b26fd2526e096cd0"), // Indemn
  ObjectId("66c0920c358d3f001351c22c"), // Demos
  ObjectId("66d196e9cc5cd70013e46565"), // Voice Demos
  ObjectId("66fc8ab493b5a40013596cd7"), // test-dolly-prod
  ObjectId("65e60f70683d12001386515a")  // InsuranceTrak
]

db.getCollection("requests").aggregate([
  { $match: {
    createdAt: { $gte: new Date("2025-09-01") },
    status: 1000,
    isTestMode: { $ne: true },
    depth: { $gt: 2 },
    id_organization: { $nin: excludeOrgs }
  }},
  { $group: {
    _id: {
      org: "$id_organization",
      month: { $dateToString: { format: "%Y-%m", date: "$createdAt" } }
    },
    conversations: { $sum: 1 }
  }},
  { $sort: { "_id.month": 1, conversations: -1 } }
]).toArray()
```

### PATTERN: Billable conversations by agent by month
```javascript
db.getCollection("requests").aggregate([
  { $match: {
    createdAt: { $gte: new Date("2025-09-01") },
    status: 1000,
    isTestMode: { $ne: true },
    depth: { $gt: 2 },
    id_organization: { $nin: excludeOrgs },
    hasBot: true,
    participantsBots: { $exists: true, $ne: [] }
  }},
  { $unwind: "$participantsBots" },
  { $group: {
    _id: {
      bot: "$participantsBots",
      org: "$id_organization",
      month: { $dateToString: { format: "%Y-%m", date: "$createdAt" } }
    },
    conversations: { $sum: 1 }
  }},
  { $sort: { "_id.month": 1, conversations: -1 } }
]).toArray()
```

---

## IMPORTANT NOTES

- **Read-only** — never insert, update, or delete without explicit authorization
- **Use `getCollection()`** — collection names like `canned-response-usage-metrics` and `metric-ai-suggestions` contain hyphens
- **ObjectId vs string** — some FK fields store ObjectId, others store string. Check the schema guide for each field's type. When comparing, use `.toString()` if needed
- **`subscriptions` vs `billing_subscriptions`** — these are completely different. `subscriptions` = webhook subscriptions, `billing_subscriptions` = Stripe billing
- **Observatory data exists in two places** — `tiledesk.observatory_conversations` (7.5K) and `observatory.conversations` (28K). The observatory database has more data
- **Soft deletes** — many collections use `isTrashed`, `isDeleted`, or `trashed` flags. Always filter these out unless specifically looking for deleted items
