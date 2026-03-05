---
name: livekit
description: Manage LiveKit rooms, dispatch agents, and participate in rooms programmatically via the Python SDK. Use when working with voice agent evaluation, room management, or agent dispatch.
user-invocable: false
---

# LiveKit — Voice Agent Room & Dispatch API

LiveKit Cloud hosts Indemn's voice agent rooms. The Python SDK (`livekit-api` + `livekit`) provides room management, agent dispatch, and programmatic room participation.

## Status Check

```bash
python3 -c "
import asyncio
from livekit import api
async def check():
    creds = __import__('json').loads(
        __import__('subprocess').check_output([
            'aws', 'secretsmanager', 'get-secret-value',
            '--secret-id', 'dev/shared/livekit-credentials',
            '--region', 'us-east-1',
            '--query', 'SecretString', '--output', 'text'
        ]).decode()
    )
    lk = api.LiveKitAPI(url=creds['url'].replace('wss://', 'https://'), api_key=creds['api_key'], api_secret=creds['api_secret'])
    rooms = await lk.room.list_rooms(api.ListRoomsRequest())
    print(f'OK — {len(rooms.rooms)} rooms')
    await lk.aclose()
asyncio.run(check())
"
# Expect: OK — N rooms
```

## Prerequisites

| Requirement | Source | Self-Service |
|-------------|--------|--------------|
| AWS CLI authenticated | `aws sts get-caller-identity` | Yes |
| `livekit-api` package | `pip3 install livekit-api` | Yes |
| `livekit` package (for room participation) | `pip3 install livekit` | Yes |
| LiveKit Cloud project | Jonathan (LiveKit admin) | No |

## Credentials

Stored in **AWS Secrets Manager** at `dev/shared/livekit-credentials`:

```bash
aws secretsmanager get-secret-value \
  --secret-id dev/shared/livekit-credentials \
  --region us-east-1 \
  --query SecretString --output text | python3 -m json.tool
```

Returns: `{"api_key": "...", "api_secret": "...", "url": "wss://..."}`

**Important:** The `url` is `wss://` for WebSocket connections (room participation) and `https://` for REST API calls (room management, dispatch). Replace protocol as needed.

## Setup

```bash
pip3 install livekit-api livekit
```

## Credential Loading Pattern

```python
import json, subprocess
from livekit import api

def get_livekit_creds():
    raw = subprocess.check_output([
        "aws", "secretsmanager", "get-secret-value",
        "--secret-id", "dev/shared/livekit-credentials",
        "--region", "us-east-1",
        "--query", "SecretString", "--output", "text"
    ]).decode()
    return json.loads(raw)

creds = get_livekit_creds()
lk = api.LiveKitAPI(
    url=creds["url"].replace("wss://", "https://"),
    api_key=creds["api_key"],
    api_secret=creds["api_secret"],
)
```

## Usage Patterns

### List rooms
```python
rooms = await lk.room.list_rooms(api.ListRoomsRequest())
for r in rooms.rooms:
    print(f"{r.name} — {r.num_participants} participants")
```

### Create room
```python
room = await lk.room.create_room(api.CreateRoomRequest(
    name="eval-test-001",
    empty_timeout=300,  # seconds before auto-delete when empty
    metadata='{"purpose": "evaluation"}'
))
```

### Delete room
```python
await lk.room.delete_room(api.DeleteRoomRequest(room="eval-test-001"))
```

### Dispatch agent with metadata
```python
import json
dispatch = await lk.agent_dispatch.create_dispatch(
    api.CreateAgentDispatchRequest(
        room="eval-test-001",
        agent_name="Indemn Voice Assistant",  # must match voice-livekit WorkerOptions
        metadata=json.dumps({"bot_id": "...", "eval_mode": True})
    )
)
# dispatch.id, dispatch.metadata, dispatch.state
```

### List dispatches in room
```python
dispatches = await lk.agent_dispatch.list_dispatch("room-name")
# Returns list of AgentDispatch objects
```

### Delete dispatch
```python
await lk.agent_dispatch.delete_dispatch(dispatch_id, room_name)
```

### Join room as participant
```python
from livekit import api, rtc

# Generate access token
token = (
    api.AccessToken(api_key=creds["api_key"], api_secret=creds["api_secret"])
    .with_identity("eval-simulator")
    .with_name("Evaluation Simulator")
    .with_grants(api.VideoGrants(
        room_join=True,
        room="eval-test-001",
        can_publish=True,
        can_subscribe=True,
    ))
)

# Connect
room = rtc.Room()
await room.connect(url=creds["url"], token=token.to_jwt())

# Publish audio
audio_source = rtc.AudioSource(sample_rate=48000, num_channels=1)
track = rtc.LocalAudioTrack.create_audio_track("eval-audio", audio_source)
options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
await room.local_participant.publish_track(track, options)

# Listen for events
@room.on("participant_connected")
def on_participant(participant):
    print(f"Agent connected: {participant.identity}")

@room.on("track_subscribed")
def on_track(track, publication, participant):
    print(f"Track from {participant.identity}: {track.kind}")

# Disconnect
await room.disconnect()
```

### List participants in room
```python
result = await lk.room.list_participants(api.ListParticipantsRequest(room="eval-test-001"))
for p in result.participants:
    print(f"{p.identity} — {len(p.tracks)} tracks")
```

## Voice Agent Details

- **Agent name (prod):** `indemn` — Docker container `voice-livekit` on EC2
- **Agent name (dev):** `dev-indemn` — Docker container `voice-livekit-dev` on EC2
- **Agent name (default):** `Indemn Voice Assistant` (env: `AGENT_NAME`, default in `config/settings.py:71`)
- **EC2:** `i-01e65d5494fd64b05` (g4dn.xlarge) at `3.236.53.208`, SSH key: `ptrkdy_key`
- **Worker registration:** `agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, agent_name=...))` in `main.py:843-852`
- **Bot ID resolution:** Currently phone-only via `mongo_helper.get_bot_id_by_phone_flexible(trunk_number)`. Dispatch metadata (`ctx.job.metadata`) is available but not yet read by the entrypoint.
- **LiveKit SDK versions:** `livekit==1.0.19`, `livekit-agents==1.3.6`, `livekit-api==1.0.7`

## Validated Capabilities (2026-03-04)

| Capability | Status | Notes |
|------------|--------|-------|
| List rooms | Tested | Returns all active rooms |
| Create room | Tested | `empty_timeout` auto-cleans. Room disappears from list when empty. |
| Delete room | Tested | Immediate cleanup |
| Create dispatch with metadata | Tested | Metadata preserved as JSON string |
| List dispatches | Tested | Returns `list` (not wrapper object) |
| Delete dispatch | Tested | `delete_dispatch(id, room_name)` signature |
| Join room as participant | Tested | Identity, audio track publishing all work |
| Publish audio track | Tested | `AudioSource` + `LocalAudioTrack` pattern |
| Agent receives dispatch | Not tested | Requires voice-livekit running (not local) |

## Dev Environment

- **LiveKit Cloud URL:** `wss://test-ympl759t.livekit.cloud`
- **AWS Secret:** `dev/shared/livekit-credentials`
- **voice-livekit runs on dedicated instances** — cannot run locally (GPU required)
