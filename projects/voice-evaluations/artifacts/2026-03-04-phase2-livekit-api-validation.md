---
ask: "Validate LiveKit API capabilities needed for Phase 2 voice simulation evaluation — can we create rooms, dispatch agents with metadata, and join rooms as programmatic participants?"
created: 2026-03-04
workstream: voice-evaluations
session: 2026-03-04-b
sources:
  - type: livekit-api
    description: "Python SDK (livekit-api==1.1.0, livekit==1.1.2) tested against dev LiveKit Cloud"
  - type: aws
    description: "Credentials from dev/shared/livekit-credentials in AWS Secrets Manager"
  - type: github
    description: "voice-livekit codebase analysis — entrypoint, worker options, bot_id resolution"
  - type: livekit-docs
    description: "Agent dispatch docs, Python SDK docs, job metadata docs"
---

# Phase 2 Research: LiveKit API Validation for Voice Simulation Evaluation

## Objective

Before designing Phase 2 (voice simulation evaluation), validate that the LiveKit API supports the capabilities we need: programmatic room creation, agent dispatch with metadata, and room participation. Zero assumptions — every capability must be tested.

## Test Results

### 1. Room Management — VALIDATED

| Operation | Result | Notes |
|-----------|--------|-------|
| List rooms | Pass | Returns all active rooms |
| Create room | Pass | `empty_timeout` auto-cleans when no participants. Room disappears from list quickly. |
| Delete room | Pass | Immediate cleanup |
| Room metadata | Pass | Arbitrary JSON string supported |

```python
room = await lk.room.create_room(api.CreateRoomRequest(
    name="eval-test-room-001",
    empty_timeout=300,
    metadata='{"purpose": "evaluation"}'
))
# Room SID: RM_DRuJVc9EDkn2
```

### 2. Agent Dispatch with Metadata — VALIDATED

| Operation | Result | Notes |
|-----------|--------|-------|
| Create dispatch | Pass | Metadata preserved as JSON string |
| List dispatches | Pass | Returns `list` directly (not wrapper) |
| Delete dispatch | Pass | Signature: `delete_dispatch(id, room_name)` |
| Metadata content | Pass | Arbitrary JSON — `bot_id`, `eval_mode`, any fields |

```python
dispatch = await lk.agent_dispatch.create_dispatch(
    api.CreateAgentDispatchRequest(
        room="eval-dispatch-test-001",
        agent_name="Indemn Voice Assistant",
        metadata=json.dumps({
            "bot_id": "695c3df0922e070f5e057517",
            "eval_mode": True,
            "scenario_id": "test-001"
        })
    )
)
# Dispatch ID: AD_ejJo7NepsjAd
# Metadata preserved exactly as sent
```

**Key finding:** Dispatch creates the room automatically if it doesn't exist. The agent_name must match the `WorkerOptions.agent_name` used when the voice agent registers with LiveKit.

### 3. Room Participation — VALIDATED

| Operation | Result | Notes |
|-----------|--------|-------|
| Generate access token | Pass | `with_identity()`, `with_grants()` builder pattern |
| Connect to room | Pass | WebSocket connection to `wss://...livekit.cloud` |
| Publish audio track | Pass | `AudioSource` + `LocalAudioTrack` pattern |
| Event listeners | Pass | `participant_connected`, `track_subscribed`, `data_received` |
| List participants via API | Pass | Shows our participant with published tracks |

```python
token = (
    api.AccessToken(api_key=..., api_secret=...)
    .with_identity("eval-simulator")
    .with_name("Evaluation Simulator")
    .with_grants(api.VideoGrants(
        room_join=True, room="...", can_publish=True, can_subscribe=True,
    ))
)
room = rtc.Room()
await room.connect(url="wss://test-ympl759t.livekit.cloud", token=token.to_jwt())
# Connected! Identity: eval-simulator
# Audio track published: TR_AMB5aZpknfDot5
```

### 4. Full Simulation Flow — VALIDATED (minus agent)

Combined test: create room → dispatch agent → join as participant → publish audio.

| Step | Result | Notes |
|------|--------|-------|
| Room created | Pass | |
| Agent dispatched with metadata | Pass | Metadata preserved |
| Simulator joined room | Pass | Audio track publishing works |
| Agent connected | **Pass** | Agent joined room, initialized MongoDB + RabbitMQ, connected to LiveKit |
| Agent processes dispatch | **Blocked** | Agent waits at `wait_for_participant()` — no SIP caller. Exits after room deleted. |
| Dispatch queued | Pass | Dispatch stays in room waiting for agent worker |

### 5. Live Agent Dispatch Test — VALIDATED (2026-03-04-b)

**Setup:** EC2 `i-01e65d5494fd64b05` (g4dn.xlarge) runs two Docker containers on the same LiveKit Cloud project:
- `voice-livekit` (prod) → agent_name: `indemn`
- `voice-livekit-dev` (dev) → agent_name: `dev-indemn`

Both connect to `wss://test-ympl759t.livekit.cloud`. Config at `/opt/voice-livekit/.env`.

**Test:** Dispatched to `dev-indemn` with metadata `{"bot_id": "test-eval", "eval_mode": true}`.

**Result:** Agent picked up dispatch within 3 seconds, connected to room, initialized MongoDB + RabbitMQ. Then blocked at `extract_twilio_info()` → `ctx.wait_for_participant()` — waiting for a SIP caller that doesn't exist. After room was deleted (cleanup), agent exited cleanly: "disconnected from room with reason: ClientInitiated". **No errors, no crashes.**

**Docker logs confirmed:**
```
Application initialized successfully in entrypoint
connecting to wss://test-ympl759t.livekit.cloud/rtc?...
process exiting
disconnected from room with reason: ClientInitiated
```

### 6. Agent Entrypoint Analysis — CODE REVIEWED + LIVE TESTED

**Current entrypoint flow (main.py:571-640):**
```python
1. await ctx.connect()                          # ✅ works with dispatch
2. twilio_details = await extract_twilio_info()  # ❌ BLOCKS — calls wait_for_participant()
3. trunk_number = twilio_details.get("TrunkNumber")
4. bot_id = await mongo_helper.get_bot_id_by_phone_flexible(trunk_number)
5. ... create assistant, start session
```

**What needs to change for eval mode:**
```python
# After ctx.connect(), check if this is an eval dispatch
metadata = json.loads(ctx.job.metadata or "{}")
if metadata.get("eval_mode"):
    # Eval mode: get bot_id from metadata, skip SIP extraction
    bot_id = metadata["bot_id"]
    initial_parameters = {"id_bot": bot_id, "eval_mode": True}
    # Wait for eval simulator participant instead of SIP caller
    caller = await ctx.wait_for_participant()
    # ... proceed with bot config loading, assistant creation
else:
    # Production mode: existing SIP flow unchanged
    twilio_details = await extract_twilio_info(ctx)
    trunk_number = twilio_details.get("TrunkNumber")
    bot_id = await mongo_helper.get_bot_id_by_phone_flexible(trunk_number)
```
```

**Job protobuf fields confirmed:** `['id', 'dispatch_id', 'type', 'room', 'participant', 'namespace', 'metadata', 'agent_name', 'state', 'enable_recording']`

The `metadata` field on Job is a string — same as what we pass in `CreateAgentDispatchRequest.metadata`.

### 6. Voice Agent Registration Details

| Setting | Value | Source |
|---------|-------|--------|
| Agent name (default) | `Indemn Voice Assistant` | `config/settings.py:71`, env `AGENT_NAME` |
| Agent name (prod EC2) | `indemn` | `/opt/voice-livekit/.env` AGENT_NAME=indemn |
| Agent name (dev EC2) | `dev-indemn` | Docker container `voice-livekit-dev` logs |
| EC2 instance | `i-01e65d5494fd64b05` (g4dn.xlarge) | `3.236.53.208`, SSH key: `ptrkdy_key` |
| Docker containers | `voice-livekit` (prod), `voice-livekit-dev` (dev) | Both on same EC2 |
| Worker type | `agents.WorkerOptions` | `main.py:843-852` |
| LiveKit SDK | `livekit-agents==1.3.6` | `pyproject.toml` |
| Bot ID source | Phone number only | `mongo_helper.get_bot_id_by_phone_flexible()` |
| Metadata access | `ctx.job.metadata` | LiveKit Agents SDK (documented, not yet used) |

## Credentials

| Item | Value |
|------|-------|
| AWS Secret | `dev/shared/livekit-credentials` |
| LiveKit Cloud URL | `wss://test-ympl759t.livekit.cloud` |
| API Key | `APIY4Y35ZyjQSxV` |
| Python packages | `livekit-api==1.1.0`, `livekit==1.1.2` (installed for testing) |

## Remaining Unknowns

1. ~~**Agent receives dispatch metadata**~~ VALIDATED — Agent picks up dispatch, connects to room, initializes. Metadata preserved. Agent doesn't read `ctx.job.metadata` yet (code change needed), but the field is accessible.
2. ~~**Agent joins room from dispatch**~~ VALIDATED — Agent joins within 3 seconds, initializes MongoDB + RabbitMQ, connects to LiveKit room. Blocks at `wait_for_participant()`.
3. **Audio round-trip** — Simulator publishes audio → agent STT → LLM → agent TTS → simulator receives audio. Not tested. Requires eval mode code change first.
4. **Transcript collection** — How to extract the full transcript after conversation. Options: Langfuse traces (existing), LiveKit room events, or agent-side transcript logging.
5. **Eval mode entrypoint change** — Code change to voice-livekit well-defined but not yet implemented.

## Architecture Confirmed

```
Evaluation Harness                    LiveKit Cloud                Voice Agent (voice-livekit)
───────────────────                   ─────────────                ──────────────────────────
1. create_dispatch(                   Room auto-created
   agent_name, metadata)         ──→  Dispatch queued    ──→       entrypoint(ctx) triggered
                                                                   ctx.job.metadata has bot_id

2. room.connect(token)           ──→  Participant joined

3. audio_source.capture(
   tts_audio) → publish          ──→  Audio routed       ──→       STT → LLM → tools → TTS

4. track_subscribed event        ←──  Audio routed       ←──
   receive audio → STT → text

5. Simulated user LLM next turn
   → TTS → publish               ──→  ...

6. Conversation complete

7. Collect transcript + metrics
8. Run evaluators (criteria + rubric)
```

## Changes Required per Repo

| Repo | Change | Size |
|------|--------|------|
| **voice-livekit** | Read `ctx.job.metadata` for bot_id before phone lookup | ~5 lines |
| **evaluations** | New `VoiceAgentClient` + voice simulation engine | New module |
| **evaluations** | LiveKit + TTS + STT dependencies | Package additions |

## What Comes Next

1. **Test with live agent** — Need voice-livekit running on a dev instance to validate the full dispatch → metadata → conversation → transcript flow
2. **Design the VoiceAgentClient** — How the evaluation harness manages the LiveKit room lifecycle, audio I/O, and transcript collection
3. **Design the voice simulation engine** — How to integrate with existing multi-turn simulation pattern (OpenEvals `create_llm_simulated_user` + `run_multiturn_simulation`)
4. **Design voice-aware evaluators** — What voice-specific metadata to include in evaluation (latency, interruptions, turn timing)
