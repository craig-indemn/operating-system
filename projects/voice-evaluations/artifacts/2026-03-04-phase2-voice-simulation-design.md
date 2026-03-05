---
ask: "Design Phase 2 voice simulation evaluation — how to run multi-turn simulated evaluations against voice agents using the real production code path"
created: 2026-03-04
updated: 2026-03-05
workstream: voice-evaluations
session: 2026-03-04-b
review-session: 2026-03-05-a
sources:
  - type: codebase
    description: "evaluations service — multi_turn_simulated.py, single_turn.py, transcript_evaluation.py, client.py, evaluations.py routes, runs.py, models"
  - type: codebase
    description: "voice-livekit — main.py entrypoint (lines 571-719), extract_twilio_info (542-568), session.py, tool_service.py, settings.py"
  - type: codebase
    description: "copilot-dashboard-react — TestItemFormModal, TestResultCard, RunEvaluationModal, EvaluationSummaryDashboard, types.ts, TestSetDetail"
  - type: livekit-api
    description: "Python SDK tested — room creation, agent dispatch with metadata, room participation with audio tracks"
  - type: ec2
    description: "Live agent dispatch test on i-01e65d5494fd64b05 — agent picked up dispatch, connected to room, blocked at wait_for_participant()"
  - type: livekit-docs
    description: "Agent dispatch, job metadata, room participation, AudioFrame/AudioSource documentation"
  - type: code-review
    description: "5 parallel review agents validated design against actual source code in all repos"
---

# Phase 2 Design: Voice Simulation Evaluation

## Objective

Enable simulation-based evaluation for voice agents — the same multi-turn test scenario approach used for web agents today, but running against the real voice agent code path including STT, LLM, tool execution, and TTS. The evaluation harness creates a LiveKit room, dispatches the real voice agent, joins as a simulated caller, and conducts a full audio conversation. The resulting transcript is evaluated with the same criteria and rubric evaluators used for web.

## How Web Simulation Works Today

For reference, the existing web multi-turn simulation flow (from `multi_turn_simulated.py`):

1. `target()` function creates a thread_id, httpx client (300s timeout), and conversation history
2. `create_llm_simulated_user(system=persona, model="openai:gpt-4o", fixed_responses=[initial_message])` returns a callable `(trajectory, turn_counter) → next_message`
3. `app()` function sends each user message to bot-service `/llm-evaluate/invoke`, gets structured response with `bot_message`, `function_details`, `tool_result`
4. `run_multiturn_simulation(app, user, max_turns, stopping_condition)` loops turns
5. Stopping condition: max turns reached or `_is_handoff()` detects `is_human_handoff_failure` in `tool_result`
6. Transcript formatted as `User: ...\nAgent: ...\n  [Tool: name | summary]`
7. `client.evaluate(target, data=dataset_name, evaluators=evaluators)` runs through LangSmith
8. Results synced to MongoDB via `sync_results_to_mongo()`

The voice simulation follows the same pattern — the difference is the transport. Instead of HTTP calls to bot-service, the simulator communicates via audio in a LiveKit room.

## Architecture

```
Evaluation Harness                    LiveKit Cloud                Voice Agent (voice-livekit)
───────────────────                   ─────────────                ──────────────────────────
1. create_dispatch(                   Room auto-created
   agent_name="dev-indemn",     ──→  Dispatch queued    ──→       entrypoint(ctx) triggered
   metadata={bot_id, eval_mode})                                  Reads bot_id from ctx.job.metadata
                                                                  Loads config, tools, system prompt
                                                                  Creates Assistant + AgentSession

2. Join room as participant      ──→  Participant joined
   (with audio track)                                        ←──  Agent detects participant
                                                                  Speaks greeting via TTS

3. Receive agent greeting audio  ←──  Audio routed           ←──
   Buffer frames until silence
   Deepgram STT → text
   Feed to simulated user LLM

4. Simulated user generates
   next message text
   OpenAI TTS → MP3 → decode
   → resample 48kHz PCM
   → chunk into 20ms frames
   → publish via AudioSource    ──→  Audio routed           ──→  STT → LLM → tools → TTS

5. Receive agent response audio  ←──  Audio routed           ←──
   Buffer frames until silence
   Deepgram STT → text
   Feed to simulated user LLM

6. Loop until:
   - Max turns reached
   - Scenario complete (simulated user signals done)

7. Disconnect from room
   Fetch tool calls from Langfuse traces (post-conversation)
   Build transcript with inline tool traces
   Delete room

8. Pass transcript to evaluators
   (criteria + rubric — unchanged)

9. Sync results to MongoDB
   (same sync.py path)
```

## Changes by Repository

### 1. voice-livekit (~40 lines)

**File:** `main.py` — `entrypoint()` function (lines 571-719)

Add an eval mode branch after `ctx.connect()` (line 609) and before `extract_twilio_info()` (line 613). When `ctx.job.metadata` contains `eval_mode: true`:

- Read `bot_id` from metadata instead of phone number lookup
- Skip `extract_twilio_info()` / SIP attribute extraction entirely
- Call `ctx.wait_for_participant()` to wait for the evaluation simulator to join
- Build a replacement `initial_parameters` dict with eval-specific fields
- Skip `setup_recording_and_transcription()` (no audio to record)
- Proceed with bot config loading, Assistant creation, and AgentSession start — identical to production

The production flow is completely unchanged. No metadata = phone lookup as before.

```python
# After ctx.connect() (line 609), before extract_twilio_info() (line 613)
settings = get_settings()
mongo_helper = get_mongo_helper()

# Check for eval mode in dispatch metadata
metadata = json.loads(ctx.job.metadata or "{}")

if metadata.get("eval_mode"):
    # ===== EVAL MODE =====
    # Bot ID comes from dispatch metadata, not phone lookup
    bot_id = metadata.get("bot_id")
    if not bot_id:
        raise ValueError("eval_mode requires bot_id in dispatch metadata")

    # Wait for eval simulator to join (replaces SIP caller)
    caller = await ctx.wait_for_participant()

    # Build replacement initial_parameters (replaces twilio_details)
    initial_parameters = {
        "id_bot": bot_id,
        "eval_mode": True,
        "caller_identity": caller.identity,
        "external_conversation_id": f"eval-{ctx.room.name}",
        "From": f"eval-simulator-{caller.identity}",
        "CallSid": f"eval-{ctx.room.name}",
    }

    # call_configurations is normally fetched from voice_configurations collection
    # by phone number (get_call_configuration). In eval mode there's no phone number.
    # Pass None — create_agent_session() handles this gracefully by falling back to
    # settings.model_settings defaults (session.py line 109-110).
    call_configurations = None

else:
    # ===== PRODUCTION MODE (existing code, unchanged) =====
    twilio_details = await extract_twilio_info(ctx)
    initial_parameters = twilio_details

    bot_id = None
    trunk_number = twilio_details.get("TrunkNumber")
    call_configurations = None

    if trunk_number:
        bot_id = await mongo_helper.get_bot_id_by_phone_flexible(trunk_number)
        call_configurations = await mongo_helper.get_call_configuration(trunk_number)

    if not bot_id:
        raise ValueError("No valid bot_id available for this call")

    initial_parameters["id_bot"] = bot_id
    initial_parameters["external_conversation_id"] = twilio_details.get("CallSid")

# ===== COMMON PATH (both modes) =====

# Initial chat context
initial_ctx = ChatContext()
if metadata.get("eval_mode"):
    initial_ctx.add_message(
        role="assistant",
        content=f"Here are the initial parameters: {initial_parameters}. This is an evaluation session.",
    )
else:
    initial_ctx.add_message(
        role="assistant",
        content=f"Here are the initial parameters: {initial_parameters}, please note that the user's number is {initial_parameters.get('From')}",
    )

# Load bot configuration (works the same for both modes)
bot_details = await load_bot_configuration(
    bot_id, initial_parameters, call_configurations, ctx
)

initial_parameters["id_organization"] = bot_details.id_organization
initial_parameters["callStartedTime"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Recording URL only for production calls
if not metadata.get("eval_mode"):
    initial_parameters["recordingUrl"] = (
        f"{os.getenv('MIDDLEWARE_SERVICE_URL')}/files/signed-url?filename=recordings/{bot_details.id_organization}/calls/{initial_parameters.get('CallSid')}.mp4&bucket=indemn-call-transcripts&returnUrl=true"
    )

# Create assistant (identical for both modes)
tool_functions = getattr(bot_details, "_tool_functions", [])
assistant = Assistant(
    chat_context=initial_ctx,
    bot_id=bot_id,
    initial_parameters=initial_parameters,
    system_prompt=bot_details.system_prompt,
    initial_tools=tool_functions,
    bot_config=bot_details.config,
)

greeting_message = bot_details.greeting_message

# call_configurations is a dict from voice_configurations collection (prod)
# or None (eval mode). create_agent_session handles modelSettings=None gracefully.
modelSettings = (call_configurations or {}).get("modelSettings") if call_configurations else None
session = create_agent_session(assistant, modelSettings=modelSettings)

# Skip recording for eval mode — no audio to save
if not metadata.get("eval_mode"):
    await setup_recording_and_transcription(
        ctx, session, initial_parameters, bot_details.id_organization
    )

# Session cleanup (both modes)
session_manager = get_session_manager()
async def cleanup_callback(_):
    await session_manager.cleanup_session(assistant)
ctx.add_shutdown_callback(cleanup_callback)

# Start session (identical for both modes — agent speaks greeting, listens for audio)
await start_agent_session(
    session=session,
    room_context=ctx,
    assistant=assistant,
    initial_message=(greeting_message if greeting_message else "Hi, How can I help you today?"),
)
```

**Key implementation details:**

- **`ctx.job.metadata`** is a string field on the Job protobuf. We validated it exists and is accessible — it contains whatever JSON was passed in `CreateAgentDispatchRequest.metadata`. Must `json.loads()` it.
- **`call_configurations`** is normally fetched from the `voice_configurations` MongoDB collection by phone number via `mongo_helper.get_call_configuration(trunk_number)`. In eval mode there's no phone number, so we pass `None`. `create_agent_session()` handles this gracefully — line 109-110 of `session.py` falls back to `self.settings.model_settings` defaults when `modelSettings` is `None`.
- **`setup_recording_and_transcription()`** (line 691) creates S3 recording egress — skipped in eval mode since there's no real call to record.
- **`setup_langfuse()`** (line 606) is called before the branch point. Eval sessions will produce Langfuse traces tagged with `eval-{room_name}` as the session ID, making them distinguishable from production traces.
- **All tools load normally** — `load_bot_configuration()` fetches tools via MongoDB regardless of how bot_id was obtained. Session-bound tools (SIP transfer) will fail gracefully if invoked during eval since there's no real SIP call, but data tools (KB search, REST APIs) work identically.

### 2. evaluations — New `VoiceAgentClient`

**New file:** `src/indemn_evals/agents/voice_client.py`

Analogous to `BotServiceClient` (which talks to bot-service for web agents). Manages the LiveKit room lifecycle and audio I/O.

```python
import asyncio
import io
import json
from uuid import uuid4

from deepgram import DeepgramClient, PrerecordedOptions
from livekit import api, rtc
from openai import AsyncOpenAI
from pydub import AudioSegment

# LiveKit audio standard: 48kHz, 16-bit signed PCM, mono
SAMPLE_RATE = 48000
NUM_CHANNELS = 1
FRAME_DURATION_MS = 20  # 20ms per frame
SAMPLES_PER_FRAME = SAMPLE_RATE * FRAME_DURATION_MS // 1000  # 960
BYTES_PER_FRAME = SAMPLES_PER_FRAME * 2  # 1920 bytes (16-bit = 2 bytes/sample)

# Silence detection: 1.5s of silence = agent done speaking
SILENCE_THRESHOLD_SEC = 1.5
TURN_TIMEOUT_SEC = 30
SESSION_TIMEOUT_SEC = 300


class VoiceAgentClient:
    """Client for conducting voice conversations with a LiveKit voice agent.

    Handles the full lifecycle: room creation, agent dispatch, audio I/O
    (TTS for simulator output, STT for agent output), and cleanup.
    """

    def __init__(self, livekit_url: str, api_key: str, api_secret: str,
                 agent_name: str = "dev-indemn",
                 deepgram_api_key: str | None = None):
        self.livekit_url = livekit_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.agent_name = agent_name
        self.lk = api.LiveKitAPI(
            url=livekit_url.replace("wss://", "https://"),
            api_key=api_key,
            api_secret=api_secret,
        )
        self.openai = AsyncOpenAI()
        self.deepgram = DeepgramClient(deepgram_api_key)
        self.room: rtc.Room | None = None
        self.room_name: str | None = None
        self.audio_source: rtc.AudioSource | None = None
        self._agent_audio_buffer = bytearray()
        self._agent_speaking = False
        self._silence_start: float | None = None
        self._agent_done = asyncio.Event()

    async def start_session(self, bot_id: str) -> str:
        """Create room, dispatch agent, join as participant. Returns room_name."""
        self.room_name = f"eval-{bot_id}-{uuid4().hex[:8]}"

        # Dispatch agent with eval metadata (auto-creates room)
        await self.lk.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                room=self.room_name,
                agent_name=self.agent_name,
                metadata=json.dumps({"bot_id": bot_id, "eval_mode": True}),
            )
        )

        # Generate access token and join room
        token = (
            api.AccessToken(api_key=self.api_key, api_secret=self.api_secret)
            .with_identity("eval-simulator")
            .with_name("Evaluation Simulator")
            .with_grants(api.VideoGrants(
                room_join=True,
                room=self.room_name,
                can_publish=True,
                can_subscribe=True,
            ))
        )

        self.room = rtc.Room()
        await self.room.connect(url=self.livekit_url, token=token.to_jwt())

        # Set up audio source for publishing simulator speech
        self.audio_source = rtc.AudioSource(
            sample_rate=SAMPLE_RATE, num_channels=NUM_CHANNELS
        )
        track = rtc.LocalAudioTrack.create_audio_track("eval-audio", self.audio_source)
        options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
        await self.room.local_participant.publish_track(track, options)

        # Subscribe to agent's audio when it joins
        @self.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication, participant):
            if track.kind == rtc.TrackKind.KIND_AUDIO and participant.identity != "eval-simulator":
                self._setup_audio_receiver(track)

        return self.room_name

    def _setup_audio_receiver(self, track: rtc.AudioTrack):
        """Set up frame-by-frame audio reception from the agent's audio track."""
        audio_stream = rtc.AudioStream(track, sample_rate=SAMPLE_RATE, num_channels=NUM_CHANNELS)

        async def _receive_frames():
            async for event in audio_stream:
                frame = event.frame
                frame_bytes = bytes(frame.data)

                # Check if frame contains audio (simple energy-based detection)
                # 16-bit PCM: compute RMS energy
                samples = len(frame_bytes) // 2
                if samples == 0:
                    continue

                energy = sum(
                    int.from_bytes(frame_bytes[i:i+2], 'little', signed=True) ** 2
                    for i in range(0, len(frame_bytes), 2)
                ) / samples
                rms = energy ** 0.5

                if rms > 200:  # Speech threshold (tunable)
                    self._agent_speaking = True
                    self._silence_start = None
                    self._agent_audio_buffer.extend(frame_bytes)
                elif self._agent_speaking:
                    # Still buffering during silence gap
                    self._agent_audio_buffer.extend(frame_bytes)
                    if self._silence_start is None:
                        self._silence_start = asyncio.get_event_loop().time()
                    elif asyncio.get_event_loop().time() - self._silence_start > SILENCE_THRESHOLD_SEC:
                        # Silence threshold exceeded — agent done speaking
                        self._agent_speaking = False
                        self._agent_done.set()

        asyncio.ensure_future(_receive_frames())

    async def send_message(self, text: str) -> str:
        """TTS the text, publish audio, wait for agent response, STT back to text.

        Audio pipeline:
        1. OpenAI TTS generates MP3 at 24kHz
        2. pydub decodes MP3 → resample to 48kHz → 16-bit mono PCM
        3. Chunk into 20ms frames → publish via AudioSource
        4. Buffer agent's audio frames until silence detected
        5. Deepgram STT transcribes the buffered PCM
        """
        # Reset agent audio state
        self._agent_audio_buffer = bytearray()
        self._agent_speaking = False
        self._silence_start = None
        self._agent_done.clear()

        # 1. Generate simulator speech via OpenAI TTS
        tts_response = await self.openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="mp3",
        )
        mp3_bytes = tts_response.content

        # 2. Decode MP3 → resample to 48kHz → 16-bit mono PCM
        audio = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
        audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(NUM_CHANNELS).set_sample_width(2)
        pcm_data = audio.raw_data

        # 3. Chunk into 20ms frames and publish
        for offset in range(0, len(pcm_data), BYTES_PER_FRAME):
            chunk = pcm_data[offset:offset + BYTES_PER_FRAME]
            if len(chunk) < BYTES_PER_FRAME:
                chunk += b'\x00' * (BYTES_PER_FRAME - len(chunk))  # Pad last frame
            frame = rtc.AudioFrame(
                data=chunk,
                sample_rate=SAMPLE_RATE,
                num_channels=NUM_CHANNELS,
                samples_per_channel=SAMPLES_PER_FRAME,
            )
            self.audio_source.capture_frame(frame)

        # 4. Wait for agent to finish responding (silence detection)
        try:
            await asyncio.wait_for(self._agent_done.wait(), timeout=TURN_TIMEOUT_SEC)
        except asyncio.TimeoutError:
            pass  # Use whatever audio we have

        # 5. Transcribe agent's audio response
        agent_text = await self._transcribe_buffer()
        return agent_text

    async def get_greeting(self) -> str:
        """Wait for and transcribe the agent's initial greeting."""
        self._agent_audio_buffer = bytearray()
        self._agent_speaking = False
        self._silence_start = None
        self._agent_done.clear()

        try:
            await asyncio.wait_for(self._agent_done.wait(), timeout=TURN_TIMEOUT_SEC)
        except asyncio.TimeoutError:
            pass

        return await self._transcribe_buffer()

    async def _transcribe_buffer(self) -> str:
        """Transcribe the accumulated agent audio buffer using Deepgram."""
        if not self._agent_audio_buffer:
            return ""

        audio_bytes = bytes(self._agent_audio_buffer)
        response = self.deepgram.listen.rest.v("1").transcribe_file(
            {"buffer": audio_bytes, "mimetype": "audio/pcm"},
            PrerecordedOptions(
                model="nova-3",
                language="en",
                punctuate=True,
                sample_rate=SAMPLE_RATE,
                channels=NUM_CHANNELS,
                encoding="linear16",
            ),
        )
        return response.results.channels[0].alternatives[0].transcript

    async def end_session(self):
        """Disconnect, cleanup room."""
        if self.room:
            await self.room.disconnect()
        if self.room_name:
            try:
                await self.lk.room.delete_room(
                    api.DeleteRoomRequest(room=self.room_name)
                )
            except Exception:
                pass  # Room may already be cleaned up
        await self.lk.aclose()
```

**Audio format details (validated against LiveKit SDK):**

- **LiveKit standard:** 48kHz, 16-bit signed PCM, mono. `AudioFrame` requires `data` (bytes), `sample_rate`, `num_channels`, `samples_per_channel`.
- **OpenAI TTS output:** MP3 at 24kHz by default. Must decode with `pydub.AudioSegment.from_mp3()`, then resample to 48kHz, convert to 16-bit mono PCM.
- **Frame chunking:** 20ms frames at 48kHz = 960 samples = 1,920 bytes per frame. Published via `audio_source.capture_frame(frame)`.
- **Agent audio reception:** Continuous stream of `AudioFrame` events via `rtc.AudioStream`. Buffer frames, detect end-of-speech via RMS energy + silence timeout (1.5s).
- **Deepgram STT:** Accepts 48kHz PCM directly as `audio/pcm` with `encoding="linear16"`. No resampling needed on receive side.

**Dependencies:** `pydub` (MP3 decoding), `ffmpeg` binary (required by pydub). Both `openai` and `deepgram-sdk` are already available or easily added.

### 3. evaluations — New `voice_simulation.py` Engine

**New file:** `src/indemn_evals/engine/voice_simulation.py`

Follows the same pattern as `multi_turn_simulated.py` — a `target()` function wrapped by `client.evaluate()`, using `create_llm_simulated_user()` from openevals.

```python
"""Voice simulation evaluation engine.

Runs multi-turn voice conversations against real voice agents via LiveKit rooms.
Same evaluation pattern as multi_turn_simulated.py but with audio transport.
"""

import uuid
from typing import Callable

from langsmith import Client
from openevals.simulators import create_llm_simulated_user

from indemn_evals.agents.voice_client import VoiceAgentClient
from indemn_evals.config import settings
from indemn_evals.models.test_case import TestCase


def _fetch_tool_calls_from_langfuse(room_name: str) -> list[dict]:
    """Fetch tool call details from Langfuse traces for a completed voice session.

    Voice agent tool calls aren't visible in the audio stream — they happen
    inside the agent's LLM pipeline. We fetch them from Langfuse traces
    after the conversation, keyed by room_name (= Langfuse session ID).

    Same pattern as transcript_evaluation.py's Langfuse enrichment.
    """
    # Query Langfuse for traces with this session ID
    # Extract GENERATION observations (which contain tool_calls in output)
    # Extract TOOL observations (which contain results)
    # Return list of {"tool_name": ..., "summary": ...}
    # Implementation follows transcript_evaluation.py pattern
    pass


def _format_tool_traces(tool_calls: list[dict], transcript: list[dict]) -> str:
    """Build transcript text with inline tool traces.

    Output format matches multi_turn_simulated.py:
        User: message
        Agent: response
          [Tool: tool_name | summary]
        User: next message
        Agent: next response
    """
    lines = []
    for msg in transcript:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            lines.append(f"User: {content}")
        elif role == "agent":
            lines.append(f"Agent: {content}")
            # Attach any tool calls that occurred during this turn
            # (matched by turn index or timestamp)
            for tc in tool_calls:
                if tc.get("turn") == msg.get("turn"):
                    lines.append(f"  [Tool: {tc['tool_name']} | {tc['summary']}]")
    return "\n".join(lines)


async def run_voice_simulation(
    test_cases: list[TestCase],
    evaluators: list[Callable],
    experiment_prefix: str,
    dataset_name: str,
    concurrency: int = 1,
) -> dict:
    """Run voice simulation evaluation using LiveKit rooms.

    Each test case creates a LiveKit room, dispatches the real voice agent,
    and conducts a full audio conversation via TTS/STT.

    Args:
        test_cases: List of voice simulation test cases.
        evaluators: Evaluator functions passed to client.evaluate().
        experiment_prefix: Name prefix for the experiment.
        dataset_name: LangSmith dataset name.
        concurrency: Number of parallel evaluations (start with 1).

    Returns:
        Evaluation results summary.
    """
    ls_client = Client(api_key=settings.langsmith_api_key)

    # Load LiveKit credentials (from settings or AWS Secrets Manager)
    livekit_url = settings.livekit_url
    livekit_api_key = settings.livekit_api_key
    livekit_api_secret = settings.livekit_api_secret

    def target(inputs: dict) -> dict:
        """Target function that runs a voice simulation and returns transcript."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            _async_target(inputs, livekit_url, livekit_api_key, livekit_api_secret)
        )

    results = ls_client.evaluate(
        target,
        data=dataset_name,
        evaluators=evaluators,
        experiment_prefix=experiment_prefix,
        max_concurrency=concurrency if concurrency > 1 else 0,
    )

    return {
        "experiment_name": results.experiment_name,
        "results": results,
    }


async def _async_target(
    inputs: dict,
    livekit_url: str,
    livekit_api_key: str,
    livekit_api_secret: str,
) -> dict:
    """Async implementation of the voice simulation target function."""
    bot_id = inputs["bot_id"]
    initial_message = inputs.get("initial_message", "Hello")
    persona = inputs.get("simulated_user_persona", "A customer calling for help.")
    max_turns = inputs.get("max_turns", 5)

    client = VoiceAgentClient(
        livekit_url=livekit_url,
        api_key=livekit_api_key,
        api_secret=livekit_api_secret,
    )

    try:
        room_name = await client.start_session(bot_id)

        # Get agent's greeting (agent speaks first in voice calls)
        greeting = await client.get_greeting()
        transcript = [{"role": "agent", "content": greeting, "turn": 0}]

        # Build persona prompt (same pattern as multi_turn_simulated.py lines 163-177)
        system_prompt = (
            "You are simulating a real person calling an AI agent on the phone. "
            "Stay in character at all times.\n\n"
            f"YOUR PERSONA: {persona}\n\n"
            "RULES:\n"
            "- You are the CALLER, not the agent. Never respond as if you are an AI assistant.\n"
            "- Ask questions, request help, and provide information when the agent asks.\n"
            "- Stay consistent with your persona and drive toward your goal.\n"
            "- Respond naturally — short replies, follow-ups, clarifications.\n"
            "- Keep responses concise — this is a phone call, not a text chat.\n"
            "- If the agent asks you for information (email, phone, etc.), respond in character "
            "with realistic details."
        )

        # Create simulated user (same openevals function as web multi-turn)
        simulated_user = create_llm_simulated_user(
            system=system_prompt,
            model="openai:gpt-4o",
            fixed_responses=[{"role": "user", "content": initial_message}],
        )

        # Conversation loop
        # Note: we manage the loop directly instead of using run_multiturn_simulation()
        # because voice turns are async and the openevals loop is sync.
        trajectory = [{"role": "assistant", "content": greeting}]
        user_message = initial_message

        for turn in range(max_turns):
            # Send user message via audio, get agent response
            agent_response = await client.send_message(user_message)

            transcript.append({"role": "user", "content": user_message, "turn": turn + 1})
            transcript.append({"role": "agent", "content": agent_response, "turn": turn + 1})

            trajectory.append({"role": "user", "content": user_message})
            trajectory.append({"role": "assistant", "content": agent_response})

            # Simulated user decides next turn
            # create_llm_simulated_user returns callable(trajectory, turn_counter=N)
            next_msg = simulated_user(trajectory, turn_counter=turn + 1)
            if isinstance(next_msg, dict):
                user_message = next_msg.get("content", "")
            else:
                user_message = str(next_msg)

            if not user_message:
                break

        # Fetch tool calls from Langfuse (post-conversation enrichment)
        tool_calls = _fetch_tool_calls_from_langfuse(room_name)

        # Build transcript text with inline tool traces
        transcript_text = _format_tool_traces(tool_calls or [], transcript)

        return {
            "response": transcript_text,
            "transcript": transcript_text,
            "trajectory": trajectory,
        }

    finally:
        await client.end_session()
```

**Key differences from web multi-turn simulation:**

| Aspect | Web (`multi_turn_simulated.py`) | Voice (`voice_simulation.py`) |
|--------|------|------|
| Transport | HTTP to bot-service `/llm-evaluate/invoke` | Audio in LiveKit room |
| Agent invocation | `_invoke_bot_sync(http_client, bot_id, msg, thread_id)` | `await client.send_message(text)` |
| First turn | Simulated user sends first message | Agent speaks greeting first, then user responds |
| Tool calls | In bot-service response (`function_details`, `tool_result`) | Fetched from Langfuse traces post-conversation |
| Conversation loop | `run_multiturn_simulation()` (sync, openevals) | Manual async loop (voice turns are async) |
| Stopping condition | `_is_handoff()` checks `is_human_handoff_failure` | Max turns or empty simulated user response |
| Timeout | 300s per HTTP request | 30s per turn, 300s per session |

### 4. evaluations — Trigger Routing

**Two files need changes:**

**File 1:** `src/indemn_evals/api/routes/evaluations.py` — `_trigger_v2()` (line 818-856)

Add `VOICE_SIMULATION` to the item expansion logic:

```python
# Current code (lines 818-833):
for item in items:
    if item.type == TestItemType.SINGLE_TURN:
        tc_type = TestCaseType.SINGLE_TURN
        type_key = "single_turn"
        tc_input = TestCaseInput(bot_id=body.bot_id, message=item.inputs.message)
    else:  # SCENARIO (multi-turn simulated)
        tc_type = TestCaseType.MULTI_TURN_SIMULATED
        type_key = "multi_turn_simulated"
        tc_input = TestCaseInput(...)

# Updated code:
for item in items:
    if item.type == TestItemType.SINGLE_TURN:
        tc_type = TestCaseType.SINGLE_TURN
        type_key = "single_turn"
        tc_input = TestCaseInput(bot_id=body.bot_id, message=item.inputs.message)
    elif item.type == TestItemType.VOICE_SIMULATION:
        tc_type = TestCaseType.VOICE_SIMULATION
        type_key = "voice_simulation"
        tc_input = TestCaseInput(
            bot_id=body.bot_id,
            initial_message=item.inputs.initial_message,
            simulated_user_persona=item.inputs.persona,
            max_turns=item.inputs.max_turns,
        )
    else:  # SCENARIO (multi-turn simulated)
        tc_type = TestCaseType.MULTI_TURN_SIMULATED
        type_key = "multi_turn_simulated"
        tc_input = TestCaseInput(
            bot_id=body.bot_id,
            initial_message=item.inputs.initial_message,
            simulated_user_persona=item.inputs.persona,
            max_turns=item.inputs.max_turns,
        )
```

**File 2:** `src/indemn_evals/api/routes/runs.py` — `execute_evaluation()` (lines 113-169)

Add import at top of file:
```python
from indemn_evals.engine.voice_simulation import run_voice_simulation
```

Add voice simulation dispatch:

```python
# After transcript_cases (line 117):
voice_sim_cases = [tc for tc in test_cases if tc.type == TestCaseType.VOICE_SIMULATION]

# After transcript execution block (after line 169):
if voice_sim_cases:
    ds_name = (type_dataset_names or {}).get("voice_simulation", fallback_dataset_name)
    result = await run_voice_simulation(
        voice_sim_cases,
        evaluators,
        experiment_prefix=f"{experiment_prefix}-voice-sim",
        dataset_name=ds_name,
        concurrency=run.concurrency,
    )
    if result.get("results"):
        all_results.append(result["results"])
```

### 5. evaluations — Model Changes

**File 1:** `src/indemn_evals/models/test_case.py` — Add to `TestCaseType`:

```python
class TestCaseType(str, Enum):
    SINGLE_TURN = "single_turn"
    MULTI_TURN_SIMULATED = "multi_turn_simulated"
    MULTI_TURN_REPLAY = "multi_turn_replay"
    TRANSCRIPT = "transcript"
    VOICE_SIMULATION = "voice_simulation"  # new
```

`TestCaseInput` already has all needed fields (`bot_id`, `initial_message`, `simulated_user_persona`, `max_turns`). No changes needed.

**Enum mapping (UI → Backend):**

| Frontend `TestItemType` | Backend `TestCaseType` | Engine |
|---|---|---|
| `single_turn` | `SINGLE_TURN` | `run_single_turn_evaluation` |
| `scenario` | `MULTI_TURN_SIMULATED` | `run_multi_turn_simulated` |
| `transcript` | `TRANSCRIPT` | `run_transcript_evaluation` |
| `voice_simulation` (new) | `VOICE_SIMULATION` (new) | `run_voice_simulation` (new) |

**File 2:** `src/indemn_evals/models/test_set.py` — Add to `TestItemType`:

```python
class TestItemType(str, Enum):
    SINGLE_TURN = "single_turn"
    SCENARIO = "scenario"
    TRANSCRIPT = "transcript"
    VOICE_SIMULATION = "voice_simulation"  # new
```

`TestItemInputs` already has all needed fields (`persona`, `initial_message`, `max_turns`). No changes needed.

### 6. evaluations — Dependencies

**File:** `pyproject.toml`

```toml
[project]
dependencies = [
    # ... existing
    "livekit-api>=1.1.0",      # Room management, agent dispatch
    "livekit>=1.1.0",          # Room participation, audio I/O
    "deepgram-sdk>=3.0.0",     # STT for simulator (transcribe agent audio)
    "pydub>=0.25.1",           # MP3 decoding for TTS output → PCM conversion
    # openai already a dependency (used for TTS)
]
```

**System dependency:** `ffmpeg` binary (required by pydub for MP3 decoding). Must be available on the evaluation service's PATH. Install via `apt-get install ffmpeg` or `brew install ffmpeg`.

### 7. evaluations — Settings

**File:** `src/indemn_evals/config.py`

Add LiveKit credential settings:

```python
class Settings(BaseSettings):
    # ... existing
    livekit_url: str = ""
    livekit_api_key: str = ""
    livekit_api_secret: str = ""
```

Loaded from environment variables (`LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`) or AWS Secrets Manager at startup.

### 8. copilot-dashboard-react

**Files affected:**

| File | Change | Lines |
|------|--------|-------|
| `types.ts` | Add `'voice_simulation'` to `TestItemType` union | 1 line |
| `TestItemFormModal.tsx` | Add `voice_simulation` toggle button (same fields as `scenario`) | ~15 lines |
| `TestResultCard.tsx` | Add `voice_simulation` entry to `TYPE_CONFIG` object (line 32-37) | 1 line |
| `TestSetDetail.tsx` | Add `voice_simulation` to `typeCounts` init + filter chip | ~10 lines |
| `TestSetsList.tsx` | Include `voice_simulation` in type breakdown counts | ~3 lines |
| `EvaluationSummaryDashboard.tsx` | Add `voice_simulation` filter + stat card (lines 94-98) | ~6 lines |
| `RunEvaluationModal.tsx` | **No changes** — passes `testSetId` without examining item types |
| `ConversationModal.tsx` | **No changes** — already parses `User:`/`Agent:` transcript format |

**Specific changes:**

**`types.ts` (line 97):**
```typescript
export type TestItemType = 'single_turn' | 'scenario' | 'transcript' | 'voice_simulation';
```

**`TestItemFormModal.tsx` (lines 154-177):** Add third button to type toggle:
```tsx
<button type="button" onClick={() => setType('voice_simulation')}
  className={type === 'voice_simulation' ? activeClass : inactiveClass}>
  Voice Simulation
</button>
```
When `type === 'voice_simulation'`, show the same fields as `scenario`: persona textarea, initial_message textarea, max_turns number input (1-20).

**`TestResultCard.tsx` (lines 32-37):** Add to `TYPE_CONFIG`:
```typescript
const TYPE_CONFIG: Record<string, { style: string; label: string }> = {
  single_turn: { style: 'bg-surface-2 text-muted', label: 'Single Turn' },
  scenario: { style: 'bg-accent/10 text-accent', label: 'Scenario' },
  transcript: { style: 'bg-emerald-500/10 text-emerald-600', label: 'Transcript' },
  voice_simulation: { style: 'bg-purple-500/10 text-purple-600', label: 'Voice Simulation' },
};
```

**`TestSetDetail.tsx` (line 59):** Add to `typeCounts` initialization:
```typescript
const typeCounts = { single_turn: 0, scenario: 0, transcript: 0, voice_simulation: 0 };
```
Add conditional filter chip (after transcript chip):
```tsx
{typeCounts.voice_simulation > 0 && (
  <button onClick={() => setTypeFilter('voice_simulation')} ...>
    Voice Simulation ({typeCounts.voice_simulation})
  </button>
)}
```

**`EvaluationSummaryDashboard.tsx` (after line 98):**
```typescript
const voiceSimResults = results.filter((r) => r.item_type === 'voice_simulation');
```
Add stat card (after transcript stat card):
```tsx
{voiceSimResults.length > 0 && (
  <StatCard label="Voice Simulation Criteria" {...getCriteriaPassRate(voiceSimResults)} />
)}
```

**Test item creation:** `voice_simulation` shows the same form fields as `scenario` — persona, initial message, max turns, success criteria. The only difference is the type value stored.

**Results display:** Voice simulation results use the existing `ConversationModal` for viewing transcripts. The card shows a purple "Voice Simulation" badge. Criteria and rubric scores display identically to scenario results.

**No voice/web agent distinction in the UI.** The test item type (`voice_simulation`) tells the backend which engine to use. A voice agent can have both `transcript` items (Phase 1) and `voice_simulation` items (Phase 2) in the same test set. The trigger flow (`RunEvaluationModal`) is unchanged — `bot_id` + `test_set_id`.

## What Does NOT Change

- **Evaluators** (criteria + rubric) — unchanged, same transcript format
- **Result sync to MongoDB** (`sync.py`) — unchanged, `item_type` field is set generically
- **LangSmith experiment tracking** — unchanged
- **Existing web evaluation flows** — single_turn, multi_turn_simulated, transcript all unchanged
- **Production voice call flow** — eval mode is an additive branch, production path untouched
- **Observatory** — no changes needed for Phase 2

## LiveKit Infrastructure (Validated)

All of the following have been tested and confirmed working:

| Capability | Status | Details |
|------------|--------|---------|
| Room creation via API | Tested | `lk.room.create_room()` — auto-cleans when empty |
| Agent dispatch with metadata | Tested | Metadata preserved as JSON string |
| Room participation | Tested | Join, publish audio tracks, receive events |
| Live agent dispatch | Tested | Dev agent (`dev-indemn`) picks up dispatch in <3s |
| Agent connects to room | Tested | Initializes MongoDB + RabbitMQ, joins room |
| Agent blocks without caller | Tested | Waits at `wait_for_participant()` — eval mode change needed |

**Dev environment:**
- LiveKit Cloud: `wss://test-ympl759t.livekit.cloud`
- Credentials: AWS Secrets Manager `dev/shared/livekit-credentials`
- EC2: `i-01e65d5494fd64b05` (g4dn.xlarge) at `3.236.53.208`
- Docker: `voice-livekit` (prod, agent_name=`indemn`) + `voice-livekit-dev` (dev, agent_name=`dev-indemn`)
- Python packages: `livekit-api==1.1.0`, `livekit==1.1.2`

## Implementation Milestones

### Milestone 1: Eval mode in voice-livekit
- Implement eval mode branch in `entrypoint()` (~40 lines)
- Handle `call_configurations` lookup without phone number
- Skip `setup_recording_and_transcription()` in eval mode
- Build replacement `initial_parameters` dict
- Deploy to dev Docker container (`voice-livekit-dev`)
- Test: dispatch with metadata → agent reads bot_id → loads config → speaks greeting → listens for audio

### Milestone 2: VoiceAgentClient in evaluations
- Build `VoiceAgentClient` with LiveKit room lifecycle
- Implement audio pipeline: OpenAI TTS → MP3 decode → 48kHz PCM → frame chunking → publish
- Implement audio reception: frame buffering → silence detection → Deepgram STT
- Add `pydub` dependency, verify `ffmpeg` available
- Test: start session → send message → receive response → end session
- Verify full audio round-trip works

### Milestone 3: Voice simulation engine
- Build `voice_simulation.py` engine with conversation loop
- Implement Langfuse tool call enrichment (post-conversation)
- Add `VOICE_SIMULATION` to both `TestCaseType` and `TestItemType` enums
- Add type routing in `_trigger_v2()` and `execute_evaluation()`
- Add LiveKit settings to config
- Test: trigger voice simulation → conversation happens → transcript with tool traces → evaluators score it → results in MongoDB

### Milestone 4: Dashboard UI
- Add `voice_simulation` type to TypeScript union, form toggle, badge, filter chips, stats
- Test: create voice simulation test item → trigger evaluation → view results with purple badge

### Milestone 5: End-to-end verification
- Create a real voice agent test set with voice simulation items
- Run evaluation end-to-end
- Verify results display correctly in Copilot Dashboard
- Verify Langfuse traces captured for the simulated conversation
- Verify tool calls enriched in transcript from Langfuse

## Resolved Design Questions

1. **Agent greeting handling:** Wait for greeting, include in transcript. The agent always speaks a greeting via `session.say(greeting_message)` with `allow_interruptions=False`. The simulator waits for the greeting audio, transcribes it, and includes it as the first entry in the transcript. The simulated user's first message comes after.

2. **End-of-speech detection:** Start with **RMS energy-based silence detection** — compute energy per audio frame, once speech is detected, buffer until 1.5s of consecutive low-energy frames. This is simpler than Silero VAD and sufficient for the controlled evaluation environment. VAD upgrade path available if accuracy is insufficient. Data channels (agent publishes turn-complete events) are a future optimization.

3. **Tool call visibility:** Fetch from **Langfuse traces** after the conversation ends. The voice agent already emits OTLP traces with tool call details (GENERATION observations with `tool_calls` in output, TOOL observations with results). Room name = Langfuse session ID. This is the same pattern used by `transcript_evaluation.py` for Phase 1 Langfuse enrichment. Tool calls are formatted inline: `[Tool: tool_name | summary]`.

4. **Concurrency:** LangSmith `client.evaluate()` handles concurrent test case execution natively via `max_concurrency`. Each voice simulation creates its own LiveKit room (isolated). Start with `concurrency=1` to validate, then test scaling. The EC2 `load_threshold: 0.85` limits concurrent agent jobs — monitor via LiveKit Cloud dashboard.

5. **Timeout handling:** Per-turn timeout of 30s in `VoiceAgentClient.send_message()` via `asyncio.wait_for()`. Per-session timeout of 300s (5 minutes). If agent never responds, the turn times out and uses whatever audio was buffered (may be empty string). If session exceeds 5 minutes, `end_session()` disconnects and cleans up.
