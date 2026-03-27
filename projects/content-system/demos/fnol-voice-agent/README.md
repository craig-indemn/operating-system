# FNOL Voice Agent Demo

Standalone voice agent + branded recording template for the InsurtechNY Spring conference demo video.

## What's Here

```
fnol-voice-agent/
├── fnol_agent.py          # LiveKit voice agent — Maya (Acme Insurance Claims)
├── requirements.txt       # Python deps (livekit-agents 1.3.10 + plugins)
├── .env                   # LiveKit Cloud credentials (gitignored)
├── .venv/                 # Python 3.12 venv (gitignored)
├── template/              # LiveKit Room Composite Egress template
│   ├── src/App.tsx        # React app — phone UI, transcript, captions
│   ├── src/styles.css     # Indemn-branded styles (Barlow, iris/eggplant)
│   ├── public/            # Maya avatar, Indemn logos
│   ├── package.json       # React + LiveKit components + egress SDK
│   └── vite.config.ts     # Vite build config
└── README.md              # This file
```

## Quick Start

### 1. Start the voice agent

```bash
cd demos/fnol-voice-agent
.venv/bin/python fnol_agent.py dev
```

Agent registers as `fnol-maya` on LiveKit Cloud.

### 2. Start the recording template

```bash
cd template
npm run dev -- --port 5555
```

### 3. Create a room and connect

```bash
# Create room restricted to fnol-maya agent only
cat > /tmp/fnol-agents.json << 'EOF'
{"dispatches": [{"agent_name": "fnol-maya"}]}
EOF

ROOM_NAME="fnol-$(date +%s)"
lk room create --agents-file /tmp/fnol-agents.json "$ROOM_NAME"

# Generate token
lk token create --join --room "$ROOM_NAME" --identity mike-reynolds --valid-for 1h
```

### 4. Open the template with the token

```
http://localhost:5555/?url=wss://test-ympl759t.livekit.cloud&token=<TOKEN>
```

Allow microphone access. You'll hear Maya greet you and can talk to her. The template shows:
- Phone call UI with Maya's avatar, call timer, waveform
- Live transcript panel (both speakers)
- CC caption bar at bottom

### 5. Record (for the final video)

Use LiveKit Room Composite Egress to record the template as rendered by headless Chromium:

```bash
lk egress start --type room-composite '{
  "room_name": "<ROOM_NAME>",
  "custom_base_url": "<HOSTED_TEMPLATE_URL>",
  "file_outputs": [{"file_type": "MP4", "filepath": "fnol-recording.mp4"}]
}'
```

The template must be hosted somewhere accessible to LiveKit's egress service (e.g., Vercel, ngrok, or S3 static hosting).

## Agent Details

- **Name:** Maya — Claims Associate, Acme Insurance
- **Prompt:** FNOL intake flow — greet, check safety, collect details, issue claim number CLM-2026-04281, assign adjuster Sarah Martinez
- **Voice:** Cartesia TTS (default voice)
- **STT:** Deepgram Nova-3
- **LLM:** OpenAI GPT-4.1, temperature 0.4
- **Hardcoded data:** Policyholder Mike Reynolds, policy ACM-2023-7841, 2023 Honda Accord

## Key Patterns

### Room-level agent filtering
The EC2 `voice-livekit-dev` container also connects to the same LiveKit Cloud instance. Without filtering, both agents join every room. The `--agents-file` flag restricts a room to only dispatch to the named agent:

```json
{"dispatches": [{"agent_name": "fnol-maya"}]}
```

### Template as both preview and recording source
The template enables mic input (`audio={true}`) and audio output (`<RoomAudioRenderer />`), so it works as a live preview where you can talk to the agent. For the actual egress recording, LiveKit's headless Chromium renders the same template without mic (the human joins separately via Playground or phone).

## Recreating the Environment

```bash
# Python agent
uv venv --python 3.12 .venv
VIRTUAL_ENV=.venv uv pip install -r requirements.txt

# Template
cd template && npm install

# LiveKit CLI
brew install livekit-cli
lk project add indemn-dev \
  --url wss://test-ympl759t.livekit.cloud \
  --api-key <KEY> --api-secret <SECRET> --default
```
