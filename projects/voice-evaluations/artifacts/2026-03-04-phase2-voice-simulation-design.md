---
ask: "Design Phase 2 voice simulation evaluation — how to run multi-turn simulated evaluations against voice agents using the real production code path"
created: 2026-03-04
workstream: voice-evaluations
session: 2026-03-04-b
sources:
  - type: codebase
    description: "evaluations service — multi_turn_simulated.py, single_turn.py, transcript_evaluation.py, client.py, evaluations.py routes, models"
  - type: codebase
    description: "voice-livekit — main.py entrypoint, session.py, tool_service.py, settings.py"
  - type: codebase
    description: "copilot-dashboard-react — TestItemFormModal, TestResultCard, RunEvaluationModal, EvaluationSummaryDashboard, types.ts"
  - type: livekit-api
    description: "Python SDK tested — room creation, agent dispatch with metadata, room participation with audio tracks"
  - type: ec2
    description: "Live agent dispatch test on i-01e65d5494fd64b05 — agent picked up dispatch, connected to room, blocked at wait_for_participant()"
  - type: livekit-docs
    description: "Agent dispatch, job metadata, room participation documentation"
---

# Phase 2 Design: Voice Simulation Evaluation

## Objective

Enable simulation-based evaluation for voice agents — the same multi-turn test scenario approach used for web agents today, but running against the real voice agent code path including STT, LLM, tool execution, and TTS. The evaluation harness creates a LiveKit room, dispatches the real voice agent, joins as a simulated caller, and conducts a full audio conversation. The resulting transcript is evaluated with the same criteria and rubric evaluators used for web.

## How Web Simulation Works Today

For reference, here's the existing web multi-turn simulation flow:

1. Evaluation harness creates an LLM simulated user via OpenEvals `create_llm_simulated_user()`
2. Simulated user sends initial message text to bot-service `/chat/invoke`
3. Bot-service processes it through the web agent's LLM pipeline, returns text response
4. Simulated user decides next turn based on persona
5. Loop until max turns or handoff detected
6. Full transcript passed to evaluators (criteria + rubric)
7. Results synced to MongoDB

The voice simulation follows the same pattern — the difference is the transport. Instead of HTTP calls to bot-service, the simulator communicates via audio in a LiveKit room.

## Architecture

```
Evaluation Harness                    LiveKit Cloud                Voice Agent (voice-livekit)
───────────────────                   ─────────────                ──────────────────────────
1. create_dispatch(                   Room auto-created
   agent_name="dev-indemn",     ──→  Dispatch queued    ──→       entrypoint(ctx) triggered
   metadata={bot_id, eval_mode})                                  Reads bot_id from metadata
                                                                  Loads config, tools, system prompt
                                                                  Creates Assistant + AgentSession

2. Join room as participant      ──→  Participant joined
   (with audio track)                                        ←──  Agent detects participant
                                                                  Speaks greeting via TTS

3. Receive agent greeting audio  ←──  Audio routed           ←──
   STT → text
   Feed to simulated user LLM

4. Simulated user generates
   next message → TTS → audio   ──→  Audio routed           ──→  STT → LLM → tools → TTS

5. Receive agent response audio  ←──  Audio routed           ←──
   STT → text
   Feed to simulated user LLM

6. Loop until:
   - Max turns reached
   - Handoff detected
   - Scenario complete

7. Disconnect from room
   Collect transcript + metadata
   Delete dispatch + room

8. Pass transcript to evaluators
   (criteria + rubric — unchanged)

9. Sync results to MongoDB
   (same sync.py path)
```

## Changes by Repository

### 1. voice-livekit (~20 lines)

**File:** `main.py` — `entrypoint()` function

Add an eval mode branch early in the entrypoint. When `ctx.job.metadata` contains `eval_mode: true`:

- Read `bot_id` from metadata instead of phone number lookup
- Skip `extract_twilio_info()` / SIP attribute extraction
- Call `ctx.wait_for_participant()` to wait for the evaluation simulator to join
- Proceed with bot config loading, Assistant creation, and AgentSession start — identical to production

The production flow is completely unchanged. No metadata = phone lookup as before.

```python
# After ctx.connect()
metadata = json.loads(ctx.job.metadata or "{}")

if metadata.get("eval_mode"):
    # Eval mode: bot_id from dispatch metadata
    bot_id = metadata["bot_id"]
    initial_parameters = {"id_bot": bot_id, "eval_mode": True}

    # Wait for eval simulator to join (replaces SIP caller)
    caller = await ctx.wait_for_participant()
    initial_parameters["caller_identity"] = caller.identity

    # Load bot config + call config from MongoDB (same as production)
    bot_config = await mongo_helper.get_bot_configuration(bot_id)
    call_configurations = bot_config.get("call_configurations")

    # ... proceed with ChatContext, Assistant, AgentSession creation
    # Exactly the same code path from here forward
else:
    # Production mode: existing SIP flow, completely unchanged
    twilio_details = await extract_twilio_info(ctx)
    trunk_number = twilio_details.get("TrunkNumber")
    bot_id = await mongo_helper.get_bot_id_by_phone_flexible(trunk_number)
    # ... rest of existing flow
```

### 2. evaluations — New `VoiceAgentClient`

**New file:** `src/indemn_evals/agents/voice_client.py`

Analogous to `BotServiceClient` (which talks to bot-service for web agents). Manages the LiveKit room lifecycle and audio I/O.

```python
class VoiceAgentClient:
    """Client for conducting voice conversations with a LiveKit voice agent."""

    def __init__(self, livekit_url, api_key, api_secret, agent_name="dev-indemn"):
        self.lk = api.LiveKitAPI(url=livekit_url, api_key=api_key, api_secret=api_secret)
        self.agent_name = agent_name
        self.tts = OpenAITTS()     # For simulator's text → audio
        self.stt = DeepgramSTT()   # For agent's audio → text

    async def start_session(self, bot_id: str) -> str:
        """Create room, dispatch agent, join as participant. Returns room_name."""
        room_name = f"eval-{bot_id}-{uuid4().hex[:8]}"

        # Dispatch agent with eval metadata
        self.dispatch = await self.lk.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                room=room_name,
                agent_name=self.agent_name,
                metadata=json.dumps({"bot_id": bot_id, "eval_mode": True})
            )
        )

        # Generate token and join room
        token = (api.AccessToken(api_key=..., api_secret=...)
            .with_identity("eval-simulator")
            .with_grants(api.VideoGrants(room_join=True, room=room_name, ...)))

        self.room = rtc.Room()
        await self.room.connect(url=self.livekit_url, token=token.to_jwt())

        # Set up audio source for publishing
        self.audio_source = rtc.AudioSource(sample_rate=48000, num_channels=1)
        track = rtc.LocalAudioTrack.create_audio_track("eval-audio", self.audio_source)
        await self.room.local_participant.publish_track(track)

        # Wait for agent to join and publish its audio track
        await self._wait_for_agent_track()

        return room_name

    async def send_message(self, text: str) -> str:
        """TTS the text, publish audio, wait for agent response, STT back to text."""
        # Generate audio from simulator's text
        audio_frames = await self.tts.synthesize(text)

        # Publish audio frames to room
        await self.audio_source.capture_frame(audio_frames)

        # Wait for agent to respond (detect end of agent speech)
        agent_audio = await self._collect_agent_response()

        # Transcribe agent's audio response
        agent_text = await self.stt.transcribe(agent_audio)

        return agent_text

    async def get_greeting(self) -> str:
        """Wait for and transcribe the agent's initial greeting."""
        agent_audio = await self._collect_agent_response()
        return await self.stt.transcribe(agent_audio)

    async def end_session(self):
        """Disconnect, cleanup room and dispatch."""
        await self.room.disconnect()
        await self.lk.agent_dispatch.delete_dispatch(self.dispatch.id, self.room_name)
        await self.lk.room.delete_room(api.DeleteRoomRequest(room=self.room_name))
        await self.lk.aclose()
```

**TTS for simulator:** OpenAI `audio.speech.create()` — simple, one provider, already used in eval service.

**STT for simulator:** Deepgram SDK — same provider the voice agent uses, proven compatibility with the audio format.

### 3. evaluations — New `voice_simulation.py` Engine

**New file:** `src/indemn_evals/engine/voice_simulation.py`

Follows the same pattern as `multi_turn_simulated.py`:

```python
async def run_voice_simulation(test_cases, evaluators, experiment_prefix, dataset_name, concurrency):
    """Run voice simulation evaluation using LiveKit rooms."""

    async def target(inputs: dict) -> dict:
        bot_id = inputs["bot_id"]
        initial_message = inputs.get("initial_message", "Hello")
        persona = inputs.get("simulated_user_persona", "")
        max_turns = inputs.get("max_turns", 10)
        success_criteria = inputs.get("success_criteria", [])

        # Create voice agent client
        client = VoiceAgentClient(livekit_url, api_key, api_secret)

        try:
            await client.start_session(bot_id)

            # Get agent's greeting
            greeting = await client.get_greeting()
            transcript = [{"role": "agent", "content": greeting}]

            # Create LLM simulated user (same OpenEvals pattern as web)
            simulated_user = create_llm_simulated_user(
                system_prompt=f"You are a caller. Persona: {persona}. "
                              f"Start with: {initial_message}",
                model="openai:gpt-4.1-mini"
            )

            # First user message
            user_message = initial_message

            for turn in range(max_turns):
                # Send user message via audio
                agent_response = await client.send_message(user_message)

                transcript.append({"role": "user", "content": user_message})
                transcript.append({"role": "agent", "content": agent_response})

                # Check stopping conditions
                if _is_conversation_complete(agent_response):
                    break

                # Simulated user decides next turn
                user_message = simulated_user(agent_response)

            # Build transcript text (same format as web multi-turn)
            transcript_text = _build_transcript_text(transcript)

            return {"response": transcript_text}

        finally:
            await client.end_session()

    # Run through LangSmith evaluate (same as other engines)
    results = client.evaluate(
        target,
        data=test_cases,
        evaluators=evaluators,
        experiment_prefix=experiment_prefix,
    )

    return results
```

**Transcript format** is identical to web multi-turn:
```
User: Hi, I need to file a claim for water damage
Agent: I'd be happy to help you with that. Can I get your policy number?
User: Sure, it's ABC-123456
Agent: Thank you. Let me pull up your policy.
[Tool: policy_lookup | Policy found: ABC-123456, active, homeowners]
Agent: I found your policy. Can you describe the damage?
```

This means existing evaluators work without modification.

### 4. evaluations — Trigger Routing

**File:** `src/indemn_evals/api/routes/evaluations.py`

In `execute_evaluation()`, add routing for the new type:

```python
# Group test cases by type
voice_sim_cases = [tc for tc in test_cases if tc.type == "voice_simulation"]

# Run voice simulation (alongside existing engines)
if voice_sim_cases:
    voice_results = await run_voice_simulation(
        voice_sim_cases, evaluators, experiment_prefix,
        f"{dataset_name}_voice_sim", concurrency
    )
    all_results.extend(voice_results)
```

### 5. evaluations — Model Changes

**File:** `src/indemn_evals/models/test_case.py`

Add `voice_simulation` to `TestCaseType` enum:

```python
class TestCaseType(str, Enum):
    SINGLE_TURN = "single_turn"
    MULTI_TURN_SIMULATED = "multi_turn_simulated"
    MULTI_TURN_REPLAY = "multi_turn_replay"
    TRANSCRIPT = "transcript"
    VOICE_SIMULATION = "voice_simulation"  # new
```

### 6. evaluations — Dependencies

**File:** `pyproject.toml`

```toml
[project]
dependencies = [
    # ... existing
    "livekit-api>=1.1.0",
    "livekit>=1.1.0",
    "deepgram-sdk>=3.0.0",  # STT for simulator
    # openai already a dependency (used for TTS)
]
```

### 7. copilot-dashboard-react

**Files affected:**

| File | Change |
|------|--------|
| `types.ts` | Add `'voice_simulation'` to `TestItemType` union |
| `TestItemFormModal.tsx` | Add `voice_simulation` toggle option (same fields as `scenario`) |
| `TestResultCard.tsx` | Add purple `Voice Simulation` badge |
| `TestSetDetail.tsx` | Add `voice_simulation` to type filter chips |
| `TestSetsList.tsx` | Include `voice_simulation` in type breakdown |
| `EvaluationSummaryDashboard.tsx` | Compute voice simulation stats (automatic from type) |
| `ConversationModal.tsx` | No changes — already parses User/Agent transcripts |

**Test item creation:** `voice_simulation` shows the same form fields as `scenario` — persona, initial message, max turns, success criteria. The only difference is the type value stored.

**Results display:** Voice simulation results use the existing `ConversationModal` for viewing transcripts. The card shows a purple "Voice Simulation" badge. Criteria and rubric scores display identically to scenario results.

**No voice/web agent distinction in the UI.** The test item type (`voice_simulation`) tells the backend which engine to use. A voice agent can have both `transcript` items (Phase 1) and `voice_simulation` items (Phase 2) in the same test set. The trigger flow (`RunEvaluationModal`) is unchanged — `bot_id` + `test_set_id`.

## What Does NOT Change

- **Evaluators** (criteria + rubric) — unchanged, same transcript format
- **Result sync to MongoDB** (`sync.py`) — unchanged
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
- Implement eval mode branch in `entrypoint()`
- Deploy to dev Docker container (`voice-livekit-dev`)
- Test: dispatch with metadata → agent reads bot_id → agent starts conversation → agent speaks greeting

### Milestone 2: VoiceAgentClient in evaluations
- Build `VoiceAgentClient` with LiveKit room lifecycle + TTS/STT
- Test: start session → send message → receive response → end session
- Verify full audio round-trip works

### Milestone 3: Voice simulation engine
- Build `voice_simulation.py` engine with conversation loop
- Add type routing in evaluation trigger
- Add model/enum changes
- Test: trigger voice simulation → conversation happens → transcript produced → evaluators score it → results in MongoDB

### Milestone 4: Dashboard UI
- Add `voice_simulation` type to form, badges, filters
- Test: create voice simulation test item → trigger evaluation → view results with badge

### Milestone 5: End-to-end verification
- Create a real voice agent test set with voice simulation items
- Run evaluation end-to-end
- Verify results display correctly in Copilot Dashboard
- Verify Langfuse traces captured for the simulated conversation

## Open Design Questions

1. **Agent greeting handling:** The voice agent speaks a greeting when the session starts. Should the simulated user wait for the greeting before sending the first message, or should the initial message override the greeting? Current design: wait for greeting, include it in transcript.

2. **End-of-speech detection:** How does the simulator know the agent has finished speaking? Options: silence detection (VAD), fixed timeout, or LiveKit track events. The agent's TTS publishes discrete audio segments — we can detect silence gaps.

3. **Tool call visibility:** In web simulation, tool calls are visible in the bot-service response. In voice simulation, tool calls happen inside the agent's LLM pipeline. We can capture them from Langfuse traces after the conversation, or from LiveKit room data events if the agent publishes them.

4. **Concurrency:** Can multiple voice simulations run in parallel? Each creates its own LiveKit room, so room isolation is fine. The constraint is the voice agent worker — how many concurrent jobs can it handle? The EC2 has `load_threshold: 0.85`.

5. **Timeout handling:** What if the agent never responds (crashes, hangs)? Need a per-turn timeout in `VoiceAgentClient.send_message()` and a per-session timeout for the overall conversation.
