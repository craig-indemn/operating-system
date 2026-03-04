---
name: langfuse
description: Query Langfuse OTLP traces for voice agent observability — trace lookup, session data, tool call spans. Use when the user asks about voice traces, Langfuse data, or needs to debug voice agent calls.
user-invocable: false
---

# Langfuse — Voice Agent Trace Observability

Langfuse captures OTLP traces from voice-livekit agents. Each voice call produces traces with LLM calls, tool executions, and session metadata.

## Status Check

```bash
curl-langfuse.sh "/api/public/traces?limit=1" -o /dev/null -w "%{http_code}"
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
2. Store in 1Password:
```bash
op item create --vault "indemn-os" --category "API Credential" --title "Langfuse Keys" \
  host="https://hipaa.cloud.langfuse.com" public_key="pk-lf-..." secret_key="sk-lf-..."
```

## Usage Patterns

All commands use `curl-langfuse.sh` which injects auth from 1Password.

### Get recent traces
```bash
curl-langfuse.sh "/api/public/traces?limit=10" | python3 -m json.tool
```

### Get trace by ID
```bash
curl-langfuse.sh "/api/public/traces/<trace_id>" | python3 -m json.tool
```

### Get traces for a session (room_name)
```bash
curl-langfuse.sh "/api/public/traces?sessionId=<room_name>&limit=20" | python3 -m json.tool
```

### Get observations (spans) for a trace
```bash
curl-langfuse.sh "/api/public/observations?traceId=<trace_id>" | python3 -m json.tool
```

### Search traces by metadata (call_sid, id_bot)
```bash
# Traces with metadata are enriched by voice-livekit's setup_langfuse() call (main.py ~line 636)
# Metadata keys: langfuse.session.id (room_name), call_sid (CallSid), id_bot
# NOTE: Langfuse metadata filtering uses a JSON filter parameter, not dot-notation
curl-langfuse.sh "/api/public/traces?limit=10&$(python3 -c "import urllib.parse; print(urllib.parse.urlencode({'filter':'[{\"type\":\"stringObject\",\"column\":\"metadata\",\"key\":\"id_bot\",\"operator\":\"=\",\"value\":\"<bot_id>\"}]'}))")" \
  | python3 -m json.tool
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
