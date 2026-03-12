---
ask: "Teach Jarvis about voice evaluation capabilities and deploy to production"
created: 2026-03-12
workstream: platform-development
session: 2026-03-12-a
sources:
  - type: github
    description: "percy-service PR #7 — voice_simulation + transcript awareness for Jarvis"
    ref: "https://github.com/indemn-ai/percy-service/pull/7"
  - type: github
    description: "evaluations PRs #13-21 — lockfile, ffmpeg, agent name, event loop fixes"
    ref: "https://github.com/indemn-ai/evaluations/pulls"
---

# Voice Evaluation Deployment — What Shipped and What's Broken

## What Was Done

### percy-service (PR #7 — merged to main and prod)
1. **EvaluationsConnector**: Added `mode` and `conversation_ids` fields to `EvaluationsInput` + payload handling in `_invoke`
2. **test-set-creation skill (v2)**: Voice agent detection step (2b), `voice_simulation` format block, voice-specific guidelines, `voice_simulation` tag
3. **eval-orchestration skill (v2)**: Three test types table, voice detection in Workflow A, Workflow F transcript evaluation, updated evaluations tool reference
4. **seed_jarvis_templates.py (v1)**: Mirrored all v2 changes in `EVALUATION_JARVIS_PROMPT` and `TEST_SET_CREATOR_PROMPT`, updated subagent description

### evaluations (PRs #13-21 — merged to main and prod)
1. **PR #13**: Regenerated `uv.lock` to include `livekit` + `livekit-api` packages (were in pyproject.toml but missing from lockfile — caused `ModuleNotFoundError` on startup)
2. **PR #15**: Added `ffmpeg` to Dockerfile runtime stage (pydub requires ffprobe to decode MP3 audio from LiveKit)
3. **PR #17**: Made LiveKit agent name configurable via `LIVEKIT_AGENT_NAME` env var (was hardcoded to `"dev-indemn"`)
4. **PR #19**: Corrected default agent name to `"indemn"` (prod's actual name)
5. **PR #21**: Pending — graceful event loop shutdown (may not be root cause, see below)

### Prod env vars added
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` — on evaluations EC2
- `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` — on evaluations EC2

## Current State: Voice Evals Not Working

Jarvis successfully generates `voice_simulation` test items and triggers evaluation runs. The eval service accepts them and routes to the voice simulation engine. But **the actual voice conversations fail**.

### Symptoms observed (in order of fixes applied)
1. ~~`ModuleNotFoundError: No module named 'livekit'`~~ — fixed by regenerating lockfile
2. ~~`FileNotFoundError: 'ffprobe'`~~ — fixed by adding ffmpeg to Dockerfile
3. ~~Agent timeout (30s) on every turn~~ — was caused by wrong agent_name `"dev-indemn"` dispatching to non-existent agent
4. **Current**: Mix of "Timed out waiting for agent response" and "Room disconnected unexpectedly" and "Event loop is closed" errors

### What we know
- The eval service IS connecting to LiveKit (rooms are being created, dispatches sent)
- The agent name is now correct (`"indemn"`)
- `get_greeting()` times out — meaning the agent never sends a transcription back
- "Event loop is closed" errors appear — the `_run_in_thread` pattern uses `asyncio.new_event_loop()` per session, and LiveKit SDK background tasks try to use the loop after it's closed
- After some sessions, "Room disconnected unexpectedly" appears

### What we DON'T know (needs investigation)
1. **Does the voice-livekit service actually receive the dispatch?** — No logs checked on the voice-livekit side
2. **Is the voice-livekit service connected to the same LiveKit Cloud project?** — The eval service and voice-livekit might use different LiveKit instances
3. **Does the voice agent join the room at all?** — We don't know if a participant other than `eval-simulator` ever appears
4. **Does the agent produce transcriptions via `lk.transcription` text stream?** — The agent must have `sync_transcription=True` enabled in its pipeline for this to work
5. **Is the event loop issue causing rooms to fail, or is it just cleanup noise?** — PR #21 (pending) addresses this but it may be a symptom not the cause
6. **Does `agent_name="indemn"` match exactly what's registered in LiveKit?** — Could be case-sensitive, could be a namespace issue

### Architecture of voice_simulation eval (for next session)
```
voice_simulation.py::run_voice_simulation()
  → LangSmith client.evaluate() with sync target function
    → target() runs in ThreadPoolExecutor
      → _run_in_thread() creates new asyncio event loop
        → _async_target():
          1. VoiceAgentClient.start_session(bot_id)
             - Creates LiveKit room: "eval-{bot_id}-{random}"
             - Dispatches agent: agent_name="indemn", metadata={"bot_id": bot_id}
             - Joins room as "eval-simulator" participant
             - Registers lk.transcription text stream handler
             - Publishes audio track
          2. get_greeting() — waits 30s for agent's first transcription
          3. For each turn:
             - OpenAI TTS generates MP3 from simulated user text
             - pydub decodes MP3 → PCM (requires ffmpeg)
             - Publishes PCM frames to LiveKit room
             - Waits 30s for agent transcription response
          4. Fetches tool calls from Langfuse (optional enrichment)
          5. Returns transcript + metrics
```

### Key files
- `evaluations/src/indemn_evals/engine/voice_simulation.py` — orchestration
- `evaluations/src/indemn_evals/agents/voice_client.py` — LiveKit client
- `evaluations/src/indemn_evals/config.py` — settings (env vars)
- `percy-service/skills/evaluations/eval-orchestration/SKILL.md` — Jarvis skill
- `percy-service/skills/evaluations/test-set-creation/SKILL.md` — Jarvis skill

### EC2 details
- Evaluations prod: `98.88.11.14`, service name `app` in docker-compose, port 8005→8080
- Evaluations dev: `44.196.55.84`
- Percy-service on both EC2s at `/opt/percy-service`
- Evaluations on both EC2s at `/opt/evaluations`

## Zombie runs in MongoDB
Multiple runs stuck in `status: "running"` from crashed/restarted containers:
- `22c9d1bc` — stuck running, 0/5 completed
- `709379d0` — stuck running, 0/5 completed
- `98715aa5` — stuck running, 0/5 completed

No cancel endpoint exists. These are permanent zombies unless manually updated in MongoDB.

## What's NOT broken
- Jarvis generates correct `voice_simulation` test items for voice agents
- Jarvis generates correct `scenario` test items for chat agents (regression OK)
- The evaluations connector passes `mode` and `conversation_ids` correctly
- The eval service accepts `voice_simulation` as a valid test item type
- Chat evaluations (scenario, single_turn) still work fine
