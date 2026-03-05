---
ask: "Create a robust testing plan for Phase 2 voice simulation evaluation — end-to-end confidence before merge"
created: 2026-03-05
workstream: voice-evaluations
session: 2026-03-05-a
sources:
  - type: codebase
    description: "Implementation diffs across voice-livekit (feat/eval-mode), evaluations (feat/voice-simulation), indemn-platform-v2 (feat/voice-simulation-type)"
  - type: code-review
    description: "3 parallel review agents + full implementation review against design doc"
  - type: testing
    description: "Static verification: Python AST parse, module imports, 79 pytest pass, TypeScript compiles clean"
---

# Phase 2 Testing Plan: Voice Simulation Evaluation

## Testing Layers

| Layer | What | Where | Blocks |
|-------|------|-------|--------|
| 1. Static verification | Compile, import, type check | All 3 repos | Nothing |
| 2. Unit tests | Models, client mock, engine mock | evaluations | Nothing |
| 3. UI visual verification | Form, badges, filters, stats | indemn-platform-v2 | Nothing |
| 4. Deploy eval mode | Push feat/eval-mode to EC2 dev container | voice-livekit | Layer 5 |
| 5. VoiceAgentClient smoke test | Single room lifecycle + audio round-trip | evaluations → LiveKit | Layer 4 |
| 6. End-to-end evaluation | Full trigger → conversation → results | All services | Layers 4, 5 |
| 7. Dashboard verification | Results visible with correct badges/stats | Copilot Dashboard | Layer 6 |

Layers 1-3 can run immediately (no external dependencies). Layer 4 is the gate — nothing beyond it works until eval mode is deployed to the dev voice agent.

---

## Layer 1: Static Verification (DONE)

| Check | Repo | Result |
|-------|------|--------|
| Python AST parse | voice-livekit | PASS (`main.py` compiles) |
| Module imports | evaluations | PASS (`VoiceAgentClient`, `voice_simulation` engine import clean) |
| Existing tests | evaluations | PASS (79 tests, 0 failures) |
| TypeScript compile | indemn-platform-v2 | PASS (`tsc --noEmit` clean) |
| Config loads | evaluations | PASS (`settings.livekit_url`, `settings.langfuse_host` resolve) |
| Enum values | evaluations | PASS (`VOICE_SIMULATION` in both `TestCaseType` and `TestItemType`) |
| deepgram-sdk version | evaluations | PASS (3.11.0 installed, within `>=3.7.0,<4.0.0` pin) |

---

## Layer 2: Unit Tests

Write and run unit tests for the new code. No external services needed.

### 2a. Model enum serialization

```bash
cd /Users/home/Repositories/evaluations
uv run pytest tests/unit/models/ -q
```

**Verify:**
- `TestCaseType.VOICE_SIMULATION.value == "voice_simulation"`
- `TestItemType.VOICE_SIMULATION.value == "voice_simulation"`
- `TestCaseType("voice_simulation") == TestCaseType.VOICE_SIMULATION`
- `TestCaseInput(bot_id="x", initial_message="hi", simulated_user_persona="caller", max_turns=5)` validates

### 2b. VoiceAgentClient (mocked)

Test the client's internal logic without LiveKit/Deepgram/OpenAI:

- **Room name generation**: `start_session("bot123")` → room_name matches `eval-bot123-{hex}`
- **Silence detection**: Feed frames with known RMS values, verify `_agent_done` fires after 1.5s silence
- **Frame chunking math**: Verify 48kHz × 20ms = 960 samples = 1920 bytes constants
- **Dispatch metadata**: Verify `CreateAgentDispatchRequest` gets `{"bot_id": "x", "eval_mode": true}`

### 2c. Voice simulation engine (mocked)

Mock `VoiceAgentClient` to return canned responses:

- **Conversation flow**: Verify greeting → user message → agent response → next user message loop
- **Transcript format**: Verify output matches `Agent: ...\nUser: ...\nAgent: ...` format
- **Max turns respected**: Verify loop exits after `max_turns` iterations
- **Empty response stops loop**: Verify conversation ends when simulated user returns empty string

### 2d. Trigger routing

- **evaluations.py**: Verify `VOICE_SIMULATION` item type creates `TestCaseType.VOICE_SIMULATION` with correct input fields
- **runs.py**: Verify `voice_sim_cases` filter correctly separates voice simulation test cases

---

## Layer 3: UI Visual Verification

```bash
cd /Users/home/Repositories/indemn-platform-v2/ui
npm run dev -- --port 5174
```

Open `http://localhost:5174` and navigate to evaluation components.

### 3a. TestItemFormModal

1. Navigate to a test set → click "Add Item"
2. Verify THREE toggle buttons: **Single Turn | Scenario | Voice Sim**
3. Click "Voice Sim" → verify persona, initial message, max turns fields appear
4. Fill out and submit → verify payload has `type: "voice_simulation"` and correct inputs

### 3b. TestResultCard

Need a mock result with `item_type: "voice_simulation"` in the data. Either:
- Seed MongoDB with a fake evaluation result, OR
- Verify via code inspection that `TYPE_CONFIG` has the purple entry

### 3c. TestSetDetail

1. If there's a test set with voice_simulation items, verify:
   - `typeCounts.voice_simulation` shows correctly
   - Purple filter chip appears and filters correctly

### 3d. EvaluationSummaryDashboard

1. Verify `voiceSimResults` filter logic via code inspection
2. With mock data, verify purple "Voice Simulation Criteria" stat card renders

### 3e. TestSetsList

1. If there's a test set with voice_simulation items, verify type breakdown shows "N voice sims"

---

## Layer 4: Deploy Eval Mode to Dev Voice Agent

**This is the critical gate.** The voice agent runs on EC2 (`i-01e65d5494fd64b05`, `3.236.53.208`) in Docker. We need to deploy the `feat/eval-mode` branch to the dev container.

### Prerequisites
- SSH access to EC2 instance
- Docker permissions on the instance
- The `voice-livekit-dev` container uses agent_name `dev-indemn`

### Steps

```bash
# 1. Push the branch
cd /Users/home/Repositories/voice-livekit
git push origin feat/eval-mode

# 2. SSH to EC2
ssh -i <key> ubuntu@3.236.53.208

# 3. Inside EC2: pull the branch and rebuild dev container
cd /path/to/voice-livekit
git fetch origin feat/eval-mode
git checkout feat/eval-mode

# 4. Rebuild and restart dev container
docker compose down voice-livekit-dev
docker compose build voice-livekit-dev
docker compose up -d voice-livekit-dev

# 5. Verify agent starts
docker logs -f voice-livekit-dev --tail 50
# Should see: "Worker registered, agent_name=dev-indemn"
```

### Verification
- Agent starts without errors
- Agent registers with LiveKit Cloud as `dev-indemn`
- No changes to production container (`voice-livekit`, agent_name=`indemn`)

### Rollback
If eval mode breaks the agent:
```bash
git checkout main
docker compose build voice-livekit-dev && docker compose up -d voice-livekit-dev
```

---

## Layer 5: VoiceAgentClient Smoke Test

Run a standalone Python script that exercises the VoiceAgentClient without the full evaluation harness. This tests the audio round-trip in isolation.

### Prerequisites
- Layer 4 complete (eval mode deployed to dev agent)
- LiveKit credentials available (AWS Secrets Manager `dev/shared/livekit-credentials`)
- OpenAI API key (for TTS)
- Deepgram API key (for STT)
- `ffmpeg` installed (`brew install ffmpeg`)

### Environment setup

```bash
cd /Users/home/Repositories/evaluations
git checkout feat/voice-simulation

# Set env vars (use the livekit skill to get credentials)
export LIVEKIT_URL="wss://test-ympl759t.livekit.cloud"
export LIVEKIT_API_KEY="<from AWS Secrets Manager>"
export LIVEKIT_API_SECRET="<from AWS Secrets Manager>"
export OPENAI_API_KEY="<existing>"
export DEEPGRAM_API_KEY="<from env or AWS>"
```

### Smoke test script

```python
"""smoke_test_voice_client.py — Run from evaluations repo root."""
import asyncio
from indemn_evals.agents.voice_client import VoiceAgentClient

async def main():
    # Use a known dev voice agent bot_id
    # Dev agents: check MongoDB dev tiledesk.faq_kbs for voice bots
    # Or use one of the prod agents if testing against prod LiveKit
    BOT_ID = "<voice-agent-bot-id>"

    client = VoiceAgentClient(
        livekit_url="wss://test-ympl759t.livekit.cloud",
        api_key="<livekit-api-key>",
        api_secret="<livekit-api-secret>",
        agent_name="dev-indemn",
    )

    try:
        print("1. Starting session...")
        room_name = await client.start_session(BOT_ID)
        print(f"   Room: {room_name}")

        print("2. Waiting for agent greeting...")
        greeting = await client.get_greeting()
        print(f"   Greeting: {greeting!r}")

        print("3. Sending message: 'Hi, I need help with my insurance claim'")
        response = await client.send_message("Hi, I need help with my insurance claim")
        print(f"   Response: {response!r}")

        print("4. Sending follow-up: 'It was water damage to my kitchen'")
        response2 = await client.send_message("It was water damage to my kitchen")
        print(f"   Response: {response2!r}")

        print("\n✓ Smoke test PASSED — full audio round-trip works")

    except Exception as e:
        print(f"\n✗ Smoke test FAILED: {e}")
        raise
    finally:
        print("5. Ending session...")
        await client.end_session()

asyncio.run(main())
```

### Expected results
- Room created (`eval-{bot_id}-{hex}`)
- Agent picks up dispatch within ~5s
- Greeting received and transcribed (non-empty string)
- Two send/receive cycles complete
- Room cleaned up

### What can go wrong
| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Agent never joins | Eval mode not deployed, or agent_name mismatch | Check Layer 4, verify `dev-indemn` |
| `get_greeting()` returns empty | Silence threshold too high, or agent never spoke | Lower RMS threshold (200 → 100), check agent logs |
| `send_message()` times out | Audio not reaching agent, or response not detected | Check audio source publishing, check STT credentials |
| `_transcribe_buffer()` returns empty | Deepgram API error, wrong encoding params | Check Deepgram API key, verify PCM format |
| Room not found error | LiveKit URL wrong, or credentials invalid | Verify `wss://test-ympl759t.livekit.cloud` and API key/secret |

---

## Layer 6: End-to-End Evaluation

Run a complete voice simulation evaluation through the evaluations service API.

### Prerequisites
- Layer 5 passes (audio round-trip works)
- Evaluations service running locally on :8002
- MongoDB dev accessible (for test set and results storage)
- LangSmith API key (for experiment tracking)

### Step 1: Start evaluations service

```bash
cd /Users/home/Repositories/evaluations
git checkout feat/voice-simulation

# Set all required env vars
export LIVEKIT_URL="wss://test-ympl759t.livekit.cloud"
export LIVEKIT_API_KEY="<key>"
export LIVEKIT_API_SECRET="<secret>"
export OPENAI_API_KEY="<key>"
export DEEPGRAM_API_KEY="<key>"
# MongoDB, LangSmith should already be in .env

uv run uvicorn indemn_evals.api.main:app --port 8002 --reload
```

### Step 2: Create a voice simulation test set

Either via the UI (Layer 3) or directly in MongoDB:

```bash
mongosh-connect.sh dev tiledesk --eval '
db.test_sets.insertOne({
  name: "Voice Sim Smoke Test",
  description: "Smoke test for voice simulation evaluation",
  version: 1,
  items: [{
    name: "Basic greeting and claim inquiry",
    type: "voice_simulation",
    inputs: {
      persona: "A homeowner calling about water damage to their kitchen. You are polite but concerned about the timeline for getting help.",
      initial_message: "Hi, I need to file a claim for water damage",
      max_turns: 3
    },
    expected: {
      success_criteria: [
        "Agent greets the caller professionally",
        "Agent asks for relevant details about the claim",
        "Agent provides next steps or asks clarifying questions"
      ]
    }
  }],
  created_at: new Date(),
  updated_at: new Date()
})
'
```

Note the returned `_id` — that's the `test_set_id`.

### Step 3: Trigger the evaluation

```bash
# Replace with actual IDs
BOT_ID="<voice-agent-bot-id>"
TEST_SET_ID="<test-set-id-from-step-2>"

curl -X POST http://localhost:8002/api/v1/evaluations \
  -H "Content-Type: application/json" \
  -d "{
    \"bot_id\": \"$BOT_ID\",
    \"test_set_id\": \"$TEST_SET_ID\",
    \"concurrency\": 1
  }"
```

### Step 4: Monitor the run

```bash
RUN_ID="<run-id-from-trigger-response>"

# Poll status
curl http://localhost:8002/api/v1/runs/$RUN_ID | python3 -m json.tool

# Watch evaluations service logs for:
# - "Starting voice simulation..."
# - LiveKit room creation
# - Agent dispatch
# - Greeting received
# - Conversation turns
# - Langfuse enrichment
# - Evaluator scoring
```

### Step 5: Verify results

```bash
# Get results
curl http://localhost:8002/api/v1/runs/$RUN_ID/results | python3 -m json.tool

# Check MongoDB
mongosh-connect.sh dev tiledesk --eval '
db.evaluation_results.find({run_id: "<run-id>"}).pretty()
'
```

**Verify:**
- Result has `item_type: "voice_simulation"`
- Transcript is present and non-empty
- Criteria scores are present (pass/fail for each criterion)
- Agent responses are coherent (not empty, not garbled)

---

## Layer 7: Dashboard Verification

View the evaluation results in the Copilot Dashboard.

### Prerequisites
- Layer 6 complete (results exist in MongoDB)
- Platform services running

### Start services

```bash
# Option A: Use local-dev
/opt/homebrew/bin/bash ./local-dev.sh start platform --env=dev

# Option B: Manual
# 1. copilot-server on :3000
# 2. percy-service on :8003
# 3. evaluations on :8002
# 4. Federation build:
cd /Users/home/Repositories/indemn-platform-v2/ui
git checkout feat/voice-simulation-type
npm run build:federation
npx serve dist-federation -l 5173 --cors -n
# 5. copilot-dashboard on :4500
```

### Verify in browser

1. Open `http://localhost:4500` → navigate to Evaluations
2. Find the smoke test evaluation run
3. **Verify purple "Voice Simulation" badge** on the result card
4. Click into the result → verify conversation transcript displays correctly
5. Navigate to test set detail → verify filter chip shows "Voice Simulation (1)"
6. Check evaluation summary → verify "Voice Simulation Criteria" stat card appears

### Screenshots to capture
- [ ] Test item form with Voice Sim toggle selected
- [ ] Result card with purple badge
- [ ] Conversation transcript from voice simulation
- [ ] Filter chips including Voice Simulation
- [ ] Summary dashboard with Voice Simulation stat card

---

## Test Execution Order

```
Layer 1 ──→ DONE (static verification all pass)
    │
Layer 2 ──→ Write and run unit tests (no dependencies)
    │
Layer 3 ──→ UI visual check (npm run dev, no dependencies)
    │
Layer 4 ──→ Deploy eval mode to EC2 (SSH, Docker rebuild)
    │
Layer 5 ──→ VoiceAgentClient smoke test (needs Layer 4)
    │
Layer 6 ──→ Full e2e evaluation (needs Layer 5)
    │
Layer 7 ──→ Dashboard verification (needs Layer 6)
```

**Critical path:** Layers 4 → 5 → 6 → 7 (serial, each depends on prior)
**Parallelizable:** Layers 2 and 3 can run alongside Layer 4 deployment

---

## Known Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| EC2 dev agent container won't rebuild | Blocks Layers 5-7 | Check Docker disk space, GPU driver compatibility |
| Silence detection threshold wrong | Empty or truncated transcripts | Start at 200, adjust based on smoke test. Can lower to 100 or try Silero VAD. |
| Deepgram STT returns garbage | Evaluation scores meaningless | Test raw audio quality. Try `nova-2` model. Check sample rate match. |
| OpenAI TTS audio quality in PCM | Agent can't understand simulator | Test with `tts-1-hd` model. Consider `response_format="pcm"` to skip MP3 decode. |
| Dev voice agent has no tools configured | Tool call enrichment untestable | Use a voice agent with tools (check MongoDB for agents with tool configs). |
| `concurrency > 1` blocks event loop | Concurrent evals hang | Start with `concurrency=1`. Sync HTTP calls are safe at concurrency=1. |
| Dev MongoDB has no voice requests after Feb 27 | No historical data for test set lookup | Use prod bot_ids that exist in dev MongoDB, or create the test set manually. |

---

## Success Criteria

Phase 2 is ready for PR when ALL of these pass:

- [ ] **Layer 1**: All static checks pass (compile, import, type check, existing tests)
- [ ] **Layer 2**: Unit tests pass for models, client logic, engine logic, routing
- [ ] **Layer 3**: UI form, badges, filters, stats all render correctly
- [ ] **Layer 4**: Eval mode deployed to dev, agent starts and registers
- [ ] **Layer 5**: Smoke test completes — greeting received, 2 turns, transcripts non-empty
- [ ] **Layer 6**: Full evaluation completes — results in MongoDB with criteria scores
- [ ] **Layer 7**: Dashboard shows results with purple badge, transcript viewable
- [ ] **Production path verified**: Regular voice calls still work after eval mode deploy
