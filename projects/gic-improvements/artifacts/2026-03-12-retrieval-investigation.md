---
ask: "Why doesn't the GIC bot's KB retriever surface class codes and portal URLs that exist in the knowledge base?"
created: 2026-03-12
workstream: gic-improvements
session: 2026-03-12-g
sources:
  - type: code
    description: "bot-service FAQs retriever code path (agent_tools.py, bot_details.py, constants.py)"
  - type: mongodb
    description: "Dev tiledesk: bot_configurations, bot_kb_mappings, knowledge_bases, knowledge_bases_data_sources"
  - type: pinecone
    description: "Direct Pinecone API queries against 'indemn' index, namespace stats and vector search"
---

# KB Retrieval Investigation — Root Cause Analysis

## Executive Summary

The GIC test bot's FAQs retriever returned zero results because of **two configuration mismatches**: the Pinecone namespace pointed to a non-existent location, and the KB ID filter didn't match the vectors' metadata. Both were fixed by updating the bot configuration in MongoDB.

## Architecture: How KB Retrieval Works

### End-to-End Flow
```
User query → LLM decides to invoke faqs-retriever → Query extracted
  → OpenAI text-embedding-3-small embeds the query
  → Pinecone query with:
      - namespace (from bot_config.ai_config.kb_configuration.namespace)
      - vector (embedded query)
      - filter: {"id_kb": {"$in": [connected_kbs]}}
      - top_k (from kb_configuration.top_k_documents_count, default 10)
  → Results post-processed:
      - TYPE_BOOST scoring (text: 1.6x, url/file: 1.0x)
      - Optional Cohere reranking (disabled for GIC)
  → Documents returned to LLM for answer generation
```

### Key Code Files
| File | Lines | Purpose |
|------|-------|---------|
| `bot-service/app/services/tools/agent_tools.py` | 223-333 | Core FAQ retriever logic |
| `bot-service/app/services/bot_details.py` | 90-177 | Bot config loading with KB aggregation |
| `bot-service/app/utils/constants.py` | 72-93 | FAQ tool definition, TYPE_BOOST map |

### How connected_kbs Is Resolved
`bot_details.py:get_bot_details_with_connected_kbs()` runs a MongoDB aggregation:
1. Start from `faq_kbs` collection (lookup by bot_id)
2. Join `bot_kb_mappings` on `id_bot`
3. Project `connected_kbs` as array of `id_kb` strings from mappings

## Root Causes

### Root Cause 1: Wrong Pinecone Namespace

| | Value | Status |
|---|---|---|
| **Bot config had** | `65eb3f19e5e6de0013fda310` (prod GIC org) | **Does not exist** in Pinecone |
| **Vectors live in** | `6613cbc6658ad379b7d516c9` (dev org) | 30,971 vectors |

The prod GIC org namespace was never populated in Pinecone. All KB training happened in the dev org namespace. The bot was querying an empty namespace — guaranteed zero results.

### Root Cause 2: Wrong KB ID in Metadata Filter

| | Value | Status |
|---|---|---|
| **Bot KB mapping had** | `6787a6702ea6350012955f33` ("GIC" dev KB) | **No vectors** with this id_kb in Pinecone |
| **Vectors tagged with** | `6852bf20940d780013ef4a28` ("New knowledge base 5") | All GIC vectors use this id_kb |

The GIC Q&A data was copied/migrated across multiple KBs over time. The vector training happened from KB `6852bf20940d780013ef4a28`, but the bot's `bot_kb_mappings` still pointed to the original KB `6787a6702ea6350012955f33`.

**Evidence:** The same entry ("Where should I submit my quote to GIC?") exists in 6 different KBs:
- `66ecf179...`, `66fa6512...`, `6787a670...`, `67b5e5bd...`, `68528ab7...`, `6852bf20...`
Each trained copy created separate vectors in Pinecone.

## Fix Applied

```javascript
// Fix 1: Correct namespace
db.bot_configurations.updateOne(
  {_id: ObjectId("6787a63d2ea6350012955ee0")},
  {$set: {"ai_config.kb_configuration.namespace": "6613cbc6658ad379b7d516c9"}}
);

// Fix 2: Correct KB mapping
db.bot_kb_mappings.updateOne(
  {id_bot: ObjectId("6787a63d2ea6350012955ed9")},
  {$set: {id_kb: "6852bf20940d780013ef4a28"}}
);

// Fix 3: Increase top_k to compensate for duplication
db.bot_configurations.updateOne(
  {_id: ObjectId("6787a63d2ea6350012955ee0")},
  {$set: {"ai_config.kb_configuration.top_k_documents_count": 25}}
);
```

## Verification

Pinecone queries with corrected config return relevant results:

| Query | Score | Top Result |
|-------|-------|------------|
| "email for submitting a quote to GIC" | 0.83 | "Please submit your quote request to quotes@gicunderwriters.com" |
| "GIC policy status check" | 0.66 | "To check the status of your refund, please contact a GIC customer service representative" |
| "portal URL for new business submission" | 0.51 | "Most submissions should go through our instant quote options first" |
| "class codes for service industry" | 0.50 | "What is the class code for plumbing? → 98483" |
| "workers compensation class code 8810" | 0.51 | "What is the class code for lawn sprinkler? → 98484" |

## Additional Findings

### Vector Duplication
Each entry appears ~5 times in Pinecone (from being trained across multiple KB copies). With top_k=10, only ~2 unique results are returned. Increased top_k to 25 to get ~5 unique results. Full deduplication would require cleaning up vectors in Pinecone.

### Production Bot Has No KB Access
The production bot (`66026a302af0870013103b1e`) has NO `faqs-retriever` tool. Its tools are: POLICY CHECK, human_handoff (x2), policy_unavailable. Production users have never had KB access. Deploying this to prod requires adding a faqs-retriever tool and configuring the correct KB settings.

### KB Content Coverage
The dev GIC KB (`6787a6702ea6350012955f33`) has 269 entries:
- **69 class code entries** covering 59 unique codes (artisan/contractor focus: plumbing, HVAC, electrical, painting, etc.)
- **24 portal-related entries** (portal navigation, document access, payment processing)
- **50+ email routing entries** with verified addresses (quote@, csr@, bind@, cancellation@, endorsements@, wc@, payments@, etc.)
- **Missing:** Class code 8810 (Clerical Office Employees — most common WC code)
- **Business hours confirmed:** 8:30 AM - 5:00 PM (from KB entry)

### Retrieval Quality Notes
- No similarity threshold in the pipeline — all top-k results are returned regardless of score
- TYPE_BOOST gives 1.6x to "text" type entries (all GIC entries are text type)
- Cohere reranking is disabled (`is_reranking_enabled: false`)
- Embedding model: `text-embedding-3-small` (1536 dimensions)
- Class code queries have lower similarity scores (~0.50) than exact-match queries (~0.82)
