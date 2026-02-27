---
name: langfuse
description: Query Langfuse OTLP traces for voice agent observability — trace lookup, session data, tool call spans. Use when the user asks about voice traces, Langfuse data, or needs to debug voice agent calls.
user-invocable: false
---

# Langfuse — Voice Agent Trace Observability

Langfuse captures OTLP traces from voice-livekit agents. Each voice call produces traces with LLM calls, tool executions, and session metadata.

## Status Check

```bash
source .env && curl -s -o /dev/null -w "%{http_code}" \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
  "$LANGFUSE_HOST/api/public/traces?limit=1"
# Expect: 200
```

## Prerequisites

| Requirement | Source | Self-Service |
|-------------|--------|--------------|
| Langfuse host URL | Jonathan (Langfuse admin) | No — HIPAA instance |
| Langfuse public key | Jonathan | No |
| Langfuse secret key | Jonathan | No |

## Setup

1. Get credentials from Jonathan (HIPAA-compliant Langfuse instance at `hipaa.cloud.langfuse.com`)
2. Add to `.env`:
```bash
LANGFUSE_HOST=https://hipaa.cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

## Usage Patterns

### Get recent traces
```bash
source .env && curl -s \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
  "$LANGFUSE_HOST/api/public/traces?limit=10" | python3 -m json.tool
```

### Get trace by ID
```bash
source .env && curl -s \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
  "$LANGFUSE_HOST/api/public/traces/<trace_id>" | python3 -m json.tool
```

### Get traces for a session (room_name)
```bash
source .env && curl -s \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
  "$LANGFUSE_HOST/api/public/traces?sessionId=<room_name>&limit=20" | python3 -m json.tool
```

### Get observations (spans) for a trace
```bash
source .env && curl -s \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
  "$LANGFUSE_HOST/api/public/observations?traceId=<trace_id>" | python3 -m json.tool
```

### Search traces by metadata (call_sid, id_bot)
```bash
# Traces with metadata are enriched by voice-livekit's setup_langfuse() call
# Metadata keys: langfuse.session.id (room_name), call_sid (CallSid), id_bot
source .env && curl -s \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
  "$LANGFUSE_HOST/api/public/traces?metadata.id_bot=<bot_id>&limit=10" | python3 -m json.tool
```

## Join Key: Langfuse ↔ MongoDB

Voice-livekit writes these metadata fields to every OTLP span:
- `langfuse.session.id` → LiveKit `room_name` → links related traces for one call
- `call_sid` → Twilio CallSid → matches `requests.attributes.CallSid` in MongoDB
- `id_bot` → Bot ID → matches `faq_kbs._id` in MongoDB

**Two-hop join:** Langfuse `call_sid` → `requests.attributes.CallSid` → `request_id` → messages, traces, observatory docs

## Trace Structure

Each voice call produces traces containing:
- **LLM generations**: model, prompt, completion, tokens, latency
- **Function tool calls**: tool name, arguments, result, duration
- **Session events**: start, end, metadata
- **Audio processing**: STT/TTS spans (if instrumented)
