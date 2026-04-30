---
ask: "TD-1 sub-piece 7 (voice harness verification + refinement). voice-deepagents harness was built this session — capture deployment + verification runbook for Craig to flip live."
created: 2026-04-30
workstream: customer-system
session: 14
sources:
  - type: indemn-os-source
    description: "harnesses/voice-deepagents/{main.py,assistant.py,tools.py,Dockerfile,pyproject.toml,tests/}"
  - type: indemn-os-source
    description: "voice-livekit/ — Indemn customer-product voice agent, the template for our LiveKit Agents pattern"
  - type: design-decision
    ref: "Session 14 — Craig: 'We already use LiveKit and have livekit self hosted on a GPU.'"
---

# voice-deepagents — Deployment + Verification Runbook

## What's built

`harnesses/voice-deepagents/` — a LiveKit Agents worker that:

- Subscribes to a LiveKit room and runs the realtime voice pipeline:
  `user audio → Silero VAD → Deepgram STT → Gemini LLM → Cartesia TTS → user audio`
- Tool surface: a single `execute(command: str)` function that subprocess-shells
  `indemn` CLI commands. Symmetric with async-deepagents and chat-deepagents.
- LLM: `google_vertexai:gemini-3-flash-preview` on `global` endpoint (matching the
  async-deepagents runtime default; Bug #42 resolution).
- Restricted tool surface: the agent can only run `indemn ...` commands. Anything
  else returns an error to the agent, never spawns. Prevents arbitrary process
  execution by a runaway model.

Files:

| File | Purpose |
|---|---|
| `main.py` | LiveKit Agents `WorkerOptions` entrypoint. Builds the AgentSession with STT/LLM/TTS/VAD/turn-detector. Greets the user. |
| `assistant.py` | `IndemnVoiceAssistant(Agent)` with the system prompt + bound tools. System prompt directs `execute('indemn skill get log-touchpoint')` on turn 1. |
| `tools.py` | The `@function_tool execute(command: str)` wrapper. Subprocess + timeout + error formatting. Restricts to `indemn` commands only. |
| `Dockerfile` | Python 3.12 base + ffmpeg/libsndfile/libportaudio2, indemn-os CLI installed, livekit-agents + plugins, VAD + turn-detector models pre-downloaded at build time. |
| `pyproject.toml` | Deps: livekit-agents>=1.0, livekit-plugins-{google,deepgram,cartesia,silero,turn-detector,noise-cancellation}, google-auth/cloud-aiplatform. |
| `tests/test_tools.py` | Unit tests for the `execute` wrapper — pin: empty rejection, non-`indemn` rejection, success returns stdout, failure returns formatted error, timeout handling, stderr appending. |

## OS state

| Item | Value |
|---|---|
| Runtime entity | `voice-deepagents-dev`, id `69f3b7fc97300b115e7236a0`, kind `realtime_voice`, framework `livekit`, llm_config `gemini-3-flash-preview/global` |
| Runtime task queue | `runtime-69f3b7fc97300b115e7236a0` |
| Runtime service actor | id `69f3b7fc97300b115e7236a2` |
| Runtime service token | Stored at AWS Secret `indemn/dev/shared/runtime-voice-service-token`. Token value visible only at create time; do not log. |
| `log-touchpoint` skill | Live in dev OS (this session). Assigned to OS Assistant. |

## What still needs to happen for live voice

This is the deployment/operational work that requires Craig's external resources.
The code is in place; flipping voice-on requires the following setup.

### 1. Required env vars on the deployed worker

The voice-deepagents Docker image expects these at runtime:

| Env var | Source | Purpose |
|---|---|---|
| `LIVEKIT_URL` | Indemn's self-hosted LiveKit server | wss://… endpoint of the LiveKit room manager |
| `LIVEKIT_API_KEY` | LiveKit dashboard | Worker auth for joining rooms |
| `LIVEKIT_API_SECRET` | LiveKit dashboard | Worker auth |
| `DEEPGRAM_API_KEY` | Deepgram dashboard (Indemn already has — used by voice-livekit) | STT |
| `CARTESIA_API_KEY` | Cartesia dashboard (Indemn already has) | TTS |
| `GCP_SERVICE_ACCOUNT_JSON` | AWS Secrets `indemn/dev/shared/google-cloud-sa` (already exists) | Vertex Gemini auth |
| `GCP_PROJECT_ID` | `prod-gemini-470505` | Vertex project for Gemini |
| `GCP_LOCATION` | `global` | Endpoint for gemini-3-flash-preview |
| `INDEMN_API_URL` | `https://api.os.indemn.ai` | OS API for the CLI subprocess |
| `INDEMN_SERVICE_TOKEN` | AWS Secret `indemn/dev/shared/runtime-voice-service-token` | CLI auth — runtime acts as `voice-deepagents-dev` service actor |

Optional tuning:
| Env var | Default | Purpose |
|---|---|---|
| `VOICE_LLM_MODEL` | `gemini-3-flash-preview` | Override LLM |
| `VOICE_LLM_LOCATION` | `global` | Override LLM endpoint |
| `VOICE_LLM_TEMPERATURE` | `0.3` | LLM temp |
| `VOICE_STT_MODEL` | `nova-3` | Deepgram model |
| `VOICE_TTS_MODEL` | `sonic-3` | Cartesia model |
| `VOICE_TTS_VOICE_ID` | `6ccbfb76-...` | Cartesia voice (matches voice-livekit default) |
| `INDEMN_CLI_TIMEOUT` | `600` | Per-command timeout in seconds |

### 2. Deploy the worker

Two patterns Indemn already runs:

**Option A (matches voice-livekit) — deploy on the same GPU instance** as voice-livekit. Build the image and run alongside. The worker connects out to the LiveKit room manager and waits for jobs.

**Option B — Railway service.** Build the image and push to Railway:

```bash
cd /Users/home/Repositories/indemn-os
railway up --service indemn-runtime-voice
# Set env vars in Railway dashboard or via:
railway variables set --service indemn-runtime-voice \
  LIVEKIT_URL=... LIVEKIT_API_KEY=... LIVEKIT_API_SECRET=... \
  DEEPGRAM_API_KEY=... CARTESIA_API_KEY=... \
  GCP_PROJECT_ID=prod-gemini-470505 GCP_LOCATION=global \
  INDEMN_API_URL=https://api.os.indemn.ai
# GCP_SERVICE_ACCOUNT_JSON + INDEMN_SERVICE_TOKEN need the AWS-Secrets injection flow
# (same pattern as indemn-runtime-async/chat).
```

Note: Option B works because LiveKit Agents workers are NOT GPU-bound — Deepgram and Cartesia handle audio externally (cloud APIs). LiveKit's local VAD + turn-detector models are CPU-fine. GPU is only required if you want local STT/TTS models, which Indemn doesn't currently use for voice agents.

### 3. Wire an Actor to use the voice runtime

Once the worker is up + connected to LiveKit, configure an actor to dispatch voice
jobs to it. For testing: update OS Assistant's runtime_id, OR create a new
`Voice OS Assistant` actor:

```bash
# Option 1: route OS Assistant to voice (loses chat path; not recommended)
# DO NOT do this — keep OS Assistant on chat-deepagents-dev.

# Option 2: clone OS Assistant onto voice runtime
indemn actor create \
  --type associate --name "Voice OS Assistant" \
  --mode hybrid \
  --runtime-id 69f3b7fc97300b115e7236a0 \
  --skills '["log-touchpoint"]'
indemn actor update <new-id> --data '{"runtime_id": "69f3b7fc97300b115e7236a0"}'
indemn actor transition <new-id> --to active
```

Then for the user-facing path: a Deployment entity that maps a UI surface (a
"call" button or push-to-talk in TD-3's per-customer page) to the Voice OS
Assistant. Per OS architecture: Deployment owns the surface + actor + runtime
+ pre-conversation params.

### 4. Verification

End-to-end smoke test:

1. Worker process is running and connected to LiveKit (look for "registered worker"
   in worker stdout).
2. Open the Indemn voice-livekit room manager / dispatch a test room.
3. Join the room as a user (LiveKit web playground or a built-in UI).
4. Speak: *"Log a touchpoint with Walker at GR Little. We discussed BT Core
   integration today and he committed to sending us the API spec by Friday."*
5. Expected behavior:
   - Agent transcribes the speech
   - Agent calls `execute('indemn skill get log-touchpoint')` to load the
     procedure
   - Agent walks through resolve → confirm → create
   - Agent confirms back: "Logged. Touchpoint <id> for GR Little. IE will pick
     this up."
6. Verify in dev OS: `indemn touchpoint list --limit 1` shows the new entry,
   `summary` matches the user's statement.
7. Verify in LangSmith (project `indemn-os-associates`): trace shows the agent
   reasoning + each `execute` call.

### 5. Out of scope for this build (future enhancements)

- Bilingual support (voice-livekit has `MultilingualModel` turn detector — not
  wired here; English only)
- Outbound calling (voice-livekit's `outbound.py` pattern — calling a customer's
  phone from the OS is a separate use case, not log-touchpoint)
- Conversation persistence (chat-deepagents has MongoDB checkpointer; voice
  conversations are ephemeral by default — recordings are LiveKit's job)
- Per-actor default_assistant pattern (Bug #44) — this voice runtime is shared
  for now; per-team-member voice assistants requires the kernel sweep that
  doesn't yet exist
- Custom LiveKit agent observability hooks (LangFuse like voice-livekit) — using
  LiveKit's built-in observability for now

## Why this design

- **LiveKit Agents framework** — same as voice-livekit (Indemn's customer voice
  product). One library, two harnesses, shared expertise.
- **Single tool (`execute`)** — symmetric with async-deepagents (commit `7281b83`
  on indemn-os main, Session 12). Skill content arrives as tool result on turn
  1, agent acts per skill instructions. No deepagents skills layer to maintain.
- **Gemini-3-flash-preview** — same model as the rest of the OS post-Bug-#42.
  Bug #42's MALFORMED_FUNCTION_CALL fix applies here too once the worker is
  live.
- **Restricted tool surface** — only `indemn` CLI commands. Prevents the agent
  from spawning arbitrary subprocesses. Safety + auditability.
- **Deepgram + Cartesia** — Indemn already pays for these and uses them in
  voice-livekit. No new vendor relationships.
- **No GPU dep** — Deepgram and Cartesia are cloud APIs; only Silero VAD +
  turn-detector run locally and are CPU-friendly. Worker is Railway-deployable.

## Why the framework choice answers your earlier question

Voice-deepagents is **option (c) LiveKit-based** from the architecture choice
earlier this session (you said: "We already use LiveKit and have livekit self
hosted on a GPU."). The harness uses LiveKit Agents for the realtime pipeline
and the same plugin set (deepgram, cartesia, silero, google) that voice-livekit
uses, so all of Indemn's existing voice infra knowledge transfers.
