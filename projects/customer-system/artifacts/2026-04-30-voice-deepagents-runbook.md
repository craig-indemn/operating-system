---
ask: "TD-1 sub-piece 7 (voice harness). Capture the deployment + verification runbook so Craig can flip live."
created: 2026-04-30
updated: 2026-05-01
workstream: customer-system
session: 15
sources:
  - type: indemn-os-source
    description: "harnesses/voice-deepagents/{agent,llm_adapter,session,main}.py + Dockerfile + pyproject.toml + tests/test_llm_adapter.py — v2 canonical pattern (Session 15 rebuild, indemn-os main commit 6671dea)"
  - type: indemn-os-source
    description: "harnesses/chat-deepagents/{agent,session}.py — the v2 voice harness mirrors this structure exactly; only I/O differs (LiveKit AgentSession ↔ WebSocket)"
  - type: design-decision
    ref: "Session 14 — Craig's correction 'I would read files to understand first' → reading docs/architecture/realtime.md + docs/architecture/associates.md surfaced the canonical pattern v1 violated. Session 15 — DELETE v1 + REBUILD."
  - type: indemn-os-source
    description: "voice-livekit/ — Indemn's customer-product voice agent. Same plugin stack (Deepgram, Cartesia, Silero, EnglishModel turn detector). The voice-deepagents harness is the *internal* dogfood version of the same transport layer."
---

# voice-deepagents — v2 Deployment + Verification Runbook

> **Note (2026-05-01):** v2 of this runbook supersedes v1 (commit `62f47f9`).
> v1 used `livekit.agents.Agent` + a single custom `execute` tool — wrong shape
> per `docs/architecture/realtime.md` + `associates.md`. v2 mirrors
> `harnesses/chat-deepagents/` — same agent code (deepagents +
> harness_common + Interaction/Attention lifecycle + three-layer LLM config),
> only the I/O transport differs. Indemn-os main commit `6671dea`.

## What v2 is

`harnesses/voice-deepagents/` — a LiveKit Agents worker that runs the *same
deepagents agent* as async + chat, with LiveKit handling audio I/O.

```
user audio
  → Silero VAD → Deepgram STT
                       ↓
              [DeepagentsLLM adapter]
                       ↓
                deepagents agent
            (CompiledStateGraph — internal
             reasoning loop runs CLI tools
             via LocalShellBackend)
                       ↓
        final assistant text response
                       ↓
              Cartesia TTS → audio out
```

The deepagents agent does ALL the work — loads its skill via `indemn skill get`
on turn 1, plans with `write_todos`, executes `indemn ...` CLI commands. LiveKit
sees a standard LLM that takes ChatContext and emits text deltas; it doesn't
know about the inner loop.

## v2 file inventory

| File | Purpose |
|---|---|
| `agent.py` | `build_agent(associate, skill_paths, llm_config, checkpointer)` — copy of `chat-deepagents/agent.py` with voice-specific `DEFAULT_PROMPT` (concise, ask-one-at-a-time, no JSON dumps, confirm before destructive ops). Returns a `deepagents.create_deep_agent(...)`. |
| `llm_adapter.py` | `DeepagentsLLM(LLM)` + `DeepagentsLLMStream(LLMStream)`. Translates LiveKit `ChatContext` ↔ LangChain `BaseMessage` list, invokes `agent.ainvoke(...)`, extracts the last AIMessage with non-empty text, emits as `ChatChunk`. LiveKit-side `tools` arg is intentionally ignored — deepagents owns its own tool surface. |
| `session.py` | `VoiceSession` mirroring `ChatSession`. Same OS lifecycle: load associate via CLI, three-layer LLM config merge (Runtime defaults < Associate < Deployment), write skills to filesystem (Bug #35 fix preserved — absolute path + yaml.safe_dump), create Interaction (channel_type=voice), open Attention (purpose=real_time_session), 30s heartbeat, `indemn events stream` subprocess for mid-conversation entity awareness. |
| `main.py` | LiveKit `WorkerOptions(entrypoint_fnc=...)`. Per-room job: VoiceSession.start() → AgentSession with STT/LLM/TTS/VAD/turn-detector → connect to room → greet → wait for disconnect → VoiceSession.close(). Background runtime register-instance + heartbeat (matches async/chat pattern). |
| `Dockerfile` | Same pattern as chat-deepagents: copy harness_common, install indemn CLI, install deps, `COPY harnesses/voice-deepagents/ /app/harness/`, `CMD ["opentelemetry-instrument", "python", "-m", "harness.main"]`. Pre-downloads VAD + turn-detector models at build time. |
| `pyproject.toml` | v0.2.0. Adds deepagents/langchain/langgraph alongside livekit deps. Drops `py-modules = [...]` (uses package layout). |
| `tests/test_llm_adapter.py` | 11 tests pinning ChatContext→LangChain translation + final-text extraction + DeepagentsLLM/Stream contract. Module-level `pytest.importorskip` for langchain_core + livekit so kernel test suite skips cleanly while harness venv (Docker) runs them. |

## v1 → v2 deltas (deleted from harness)

- `assistant.py` — `IndemnVoiceAssistant(livekit.agents.Agent)` subclass. Replaced by the deepagents agent (which lives in `agent.py`) wrapped in DeepagentsLLM.
- `tools.py` — single custom `execute()` function tool. Replaced by deepagents' built-in `LocalShellBackend` tool surface (execute + write_todos + read_file + glob/grep + task — same as async + chat).
- `tests/test_tools.py` — superseded by `tests/test_llm_adapter.py`.

## Pre-deployment OS state (already in place from Session 14)

- **Voice runtime entity:** id `69f3b7fc97300b115e7236a0`, kind=`realtime_voice`, framework=`livekit`/`deepagents`, llm_config=`{model: google_vertexai:gemini-3-flash-preview, location: global}`. (Inherits gemini-3-flash-preview/global from runtime defaults — Bug #42 resolution.)
- **Service token:** AWS Secrets at `indemn/dev/shared/runtime-voice-service-token`.
- **Indemn API:** `https://api.os.indemn.ai`.

## Deployment (Craig action)

The voice harness runs on the same self-hosted GPU instance as `voice-livekit` (per Craig: "we already use LiveKit and have livekit self hosted on a GPU"). Two options for runtime hosting:

### Option A — Container alongside voice-livekit on the GPU instance

```bash
# On the GPU instance:
docker build -f harnesses/voice-deepagents/Dockerfile -t indemn-runtime-voice-deepagents:dev .

docker run --rm --network host \
  -e LIVEKIT_URL="wss://livekit.indemn.<...>" \
  -e LIVEKIT_API_KEY="<...>" \
  -e LIVEKIT_API_SECRET="<...>" \
  -e DEEPGRAM_API_KEY="<...>" \
  -e CARTESIA_API_KEY="<...>" \
  -e GCP_SERVICE_ACCOUNT_JSON="$(cat /path/to/gcp-sa.json)" \
  -e GCP_PROJECT_ID="<gcp-project>" \
  -e GCP_LOCATION="us-central1" \
  -e INDEMN_API_URL="https://api.os.indemn.ai" \
  -e INDEMN_SERVICE_TOKEN="$(aws secretsmanager get-secret-value --secret-id indemn/dev/shared/runtime-voice-service-token --query SecretString --output text)" \
  -e RUNTIME_ID="69f3b7fc97300b115e7236a0" \
  -e VOICE_ASSOCIATE_ID="<actor-id-of-the-voice-assistant-actor>" \
  -e LANGSMITH_API_KEY="$(aws secretsmanager get-secret-value --secret-id indemn/dev/shared/langsmith-api-key --query SecretString --output text)" \
  -e LANGSMITH_TRACING="true" \
  -e LANGSMITH_PROJECT="indemn-os-associates" \
  -e VOICE_STT_MODEL="nova-3" \
  -e VOICE_TTS_MODEL="sonic-3" \
  indemn-runtime-voice-deepagents:dev
```

### Option B — Railway service `indemn-runtime-voice` (if/when Railway gets GPU support, or if running CPU-only is acceptable)

```bash
railway up --service indemn-runtime-voice
# Then set the same env vars in the Railway service config.
```

## Verification

### 1. Runtime registration

The harness calls `indemn runtime register-instance` on boot. Verify:

```bash
indemn runtime get 69f3b7fc97300b115e7236a0 | jq '.instances'
# Should show one instance with last_heartbeat ≤ 30s ago.
```

If the runtime is `configured` and you see `instances=[]`, the harness didn't reach the OS API — check INDEMN_API_URL + INDEMN_SERVICE_TOKEN.

### 2. Health check call

The simplest test: dispatch a LiveKit room with the harness's worker name, join it from a LiveKit playground client (or any LiveKit web SDK). Within ~2s the harness should:

1. Pick up the room job (LiveKit Agents framework)
2. `VoiceSession.start()` — log lines:
   - `Loaded associate: <name> (<id>)`
   - `Created Interaction: <id>` (channel_type=voice)
   - `Opened Attention: <id>` (purpose=real_time_session)
3. AgentSession constructs STT/LLM/TTS pipeline
4. Bot greets: "Hi, this is your Indemn OS assistant. What can I help you with?"

### 3. End-to-end skill load + execution (real voice turn)

User says: "Log a touchpoint with Walker at GR Little, today, scope external, summary: discussed renewal."

Expected:
- STT transcribes
- DeepagentsLLM invokes the deepagents agent
- Agent runs `indemn skill get log-touchpoint` on turn 1
- Agent runs `indemn contact entity-resolve --data '{"name": "Walker"}'`, `indemn company entity-resolve --data '{"name": "GR Little"}'`
- Agent confirms: "Logging a touchpoint with Walker at GR Little, scope external, dated today, summary discussed renewal. Sound right?"
- User says yes
- Agent runs `indemn touchpoint create --data '{...}'`
- Agent reports the new Touchpoint id
- TTS speaks each agent turn

### 4. LangSmith trace

Per CLAUDE.md § 8 — query the indemn-os-associates project, filter by `associate_id = <voice-actor-id>`, `entity_type = Interaction`. Use `order: "desc"` (lowercase — Bug #42 query gotcha). Trace should show:

- One root chain run per voice turn (named "<Associate Name> → Interaction <id>")
- Inside: `agent.ainvoke` → `write_todos` → `execute('indemn ...')` tool calls → final AIMessage
- Total LLM turns ≤ ~8 for a typical 1-2 minute conversation

### 5. Attention + heartbeat lifecycle

```bash
indemn attention list --filter '{"actor_id":"<voice-actor-id>","status":"active"}'
# During an active call, expect 1 active Attention with target_entity.type=Interaction
# and last_heartbeat within the past 30s.
```

After the call ends, the Attention transitions `active → closed` via `VoiceSession.close()`. If the harness crashes mid-call, the queue processor's `cleanup_expired_attentions` sweep transitions it `active → expired` 2 minutes after the last heartbeat (TTL).

### 6. Interaction record

```bash
indemn interaction list --filter '{"channel_type":"voice"}' --limit 5
# Should show recent voice Interactions with their status (active during, closed after).
```

## Known gaps + follow-ups

- **Token-by-token TTS streaming.** v1 of `DeepagentsLLM` emits one ChatChunk with the full final text. TTS will start synthesizing once it receives the chunk, but it doesn't get earlier-than-final tokens. Future enhancement: tap into `agent.astream_events(...)` and emit deltas as the final assistant message tokens generate.
- **Mid-conversation event awareness for voice.** The events stream subprocess populates `VoiceSession._event_queue` but the LLM adapter doesn't yet drain it into a system message on the next turn (chat does this in `session.py::handle_message`). Add to `DeepagentsLLMStream._run` when the use case arrives.
- **MongoDB checkpointer.** v1 voice sessions use the in-memory checkpointer (no persistence across reconnect). Wiring the LangGraph MongoDB checkpointer (same one chat uses) is straightforward when needed — set `checkpointer=...` in `VoiceSession(...)`.
- **chat-deepagents → CLI-via-prompt skill loading.** Pending separate work — chat still uses the deepagents skills layer that voice inherits. Both will migrate together when `harnesses/chat-deepagents/` adopts the async-deepagents pattern (commit `7281b83`).
- **Per-actor `default_assistant` provisioning.** Per Craig's call: shared OS Assistant covers TD-1; deferred. Kernel sweep that auto-provisions a `default_assistant` per human Actor on create is its own future work.

## Closes Bug #44

The v1 framing (assistant.py + tools.py + livekit.agents.Agent class with single custom execute tool) is fully replaced. Per-actor `default_assistant` pattern remains deferred. The voice runtime is ready for deployment by Craig once env vars + GPU instance allocation align.
