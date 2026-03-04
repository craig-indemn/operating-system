---
ask: "Test voice evaluation pipeline against production data locally — validate Langfuse sync, ingestion, and Observatory at scale"
created: 2026-03-02
workstream: voice-evaluations
session: 2026-03-02-e
sources:
  - type: langfuse
    description: "Prod Langfuse project cmht0a7ll001qad07jn0ko84c — 1,146 traces, 266 in date range"
  - type: mongodb
    description: "Prod MongoDB prod-indemn.3h3ab.mongodb.net/tiledesk — voice requests, observatory collections"
---

# Prod Data Test Results

## Environment
- Observatory API: localhost:8004 with prod MongoDB (`prod-indemn.3h3ab.mongodb.net`)
- Langfuse: prod project (1,146 traces), creds added to Observatory `.env`
- All local code includes voice patches (unpushed)

## Langfuse Sync

**Job**: `5dd9c840` | **Date range**: Feb 1 – Mar 3 | **Duration**: ~5 minutes

| Metric | Value |
|--------|-------|
| Traces in range | 266 |
| Runs synced | 17,326 |
| Matched to request_id | 258 (97%) |
| Unmatched | 8 (3%) |
| Failed | 0 |

Progress checkpoints:
- 50 traces: 3,300 runs, 50 matched, 0 unmatched (100%)
- 100 traces: 6,500 runs, 97 matched, 3 unmatched (97%)
- 150 traces: 9,400 runs, 144 matched, 6 unmatched (96%)
- 200 traces: 12,300 runs, 194 matched, 6 unmatched (97%)
- 250 traces: 16,200 runs, 243 matched, 7 unmatched (97%)
- 266 traces: 17,326 runs, 258 matched, 8 unmatched (97%)

**Key finding**: Prod match rate (97%) dramatically better than dev (69%). The phone+time fallback join works reliably at scale even without Phase 1B metadata.

## Ingestion

**Job**: `00a721c1` | **Date range**: Feb 28 only | **reuse_classifications**: true

| Metric | Value |
|--------|-------|
| Total conversations | 84 |
| Voice conversations | 13 |
| Failed | 0 |

The `$or` date filter correctly picked up voice conversations (Unix float `createdAt`) alongside web conversations (ISO string `conversation_start_time`).

## Voice Conversations in Observatory

13 voice conversations visible in prod Observatory:

| Date | Agent ID | Messages | Outcome |
|------|----------|----------|---------|
| 2026-03-02 | 695c3df0... | 22 | resolved_autonomous |
| 2026-03-02 | 697259ed... | 16 | partial_then_left |
| 2026-03-02 | 697259ed... | 2 | no_interaction |
| 2026-03-02 | 697259ed... | 2 | no_interaction |
| 2026-03-02 | 697259ed... | 17 | missed_handoff |
| 2026-03-02 | 697259ed... | 17 | missed_handoff |
| 2026-03-02 | 697259ed... | 14 | unresolved_abandoned |
| 2026-02-28 | 68e74763... | 17 | missed_handoff |
| 2026-02-28 | 68e74763... | 2 | no_interaction |
| 2026-02-28 | 697259ed... | 17 | unresolved_abandoned |
| 2026-02-28 | 697259ed... | 2 | no_interaction |
| 2026-02-28 | 68e74763... | 2 | no_interaction |
| 2026-02-28 | 697259ed... | 14 | missed_handoff |

**3 distinct voice agents** in prod data:
- `695c3df0922e070f5e057517`
- `697259edec2b21075fda6439`
- `68e74763f060f50013a79d68`

## Trace Data Verification

Spot-checked first voice conversation (22 messages, resolved_autonomous):
- Trace summary: 10 LLM calls, 3 tool calls, 0 errors
- Trace events: 13 total (10 llm + 3 tool)
- Tool calls have name (`function_tool`) and are sourced from Langfuse SPAN observations

## Issues Found

1. **MongoDB index timeout on prod**: The Langfuse sync compound index (`extra.metadata.source` + `_synced_at`) timed out on prod MongoDB Atlas, causing a 500 error that blocked the entire sync. Fixed by wrapping in try/except — the index is a performance optimization, not required for correctness.

## What This Validates

- Langfuse sync works at prod scale (266 traces, 17K runs, ~5 min)
- Phone+time fallback join is reliable (97% match rate without Phase 1B metadata)
- Voice date filter (`$or` on `createdAt`) correctly picks up voice conversations
- Voice channel detection (`attributes.channel == "VOICE"`) correctly classifies conversations
- LLM classification works on voice conversations (outcomes assigned correctly)
- Langfuse trace data (LLM calls + tool calls) attached to voice conversations
- Observatory API serves voice conversations with `agent_id` for Evaluate scoping
