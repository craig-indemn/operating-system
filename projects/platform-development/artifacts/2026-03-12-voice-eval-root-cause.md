---
ask: "Deep investigate voice eval failure — why agent never responds to eval service"
created: 2026-03-12
workstream: platform-development
session: 2026-03-12-b
sources:
  - type: github
    description: "evaluations PR #22 — fix transcription API mismatch"
    ref: "https://github.com/indemn-ai/evaluations/pull/22"
  - type: github
    description: "evaluations PR #23 — deploy fix to prod"
    ref: "https://github.com/indemn-ai/evaluations/pull/23"
  - type: aws
    description: "SSM commands to voice-livekit EC2 (i-01e65d5494fd64b05) and eval EC2 (i-00ef8e2bfa651aaa8)"
---

# Voice Eval Root Cause: LiveKit API Mismatch

## Root Cause

The eval service and voice agent used **two completely different LiveKit APIs** for transcription:

| Service | API Used | Mechanism |
|---------|----------|-----------|
| **voice-livekit** (agent) | `local_participant.publish_transcription(rtc.Transcription(...))` | Transcription API — emits `"transcription_received"` room events |
| **evaluations** (eval service) | `room.register_text_stream_handler("lk.transcription", handler)` | Text Stream API — listens for `send_text()` data streams |

These are **completely different protocols** in the LiveKit SDK. The agent published transcriptions, but the eval service was listening on a channel that never fired.

## How We Found It

1. **SSM to both EC2s** confirmed: same LiveKit Cloud project (`test-ympl759t.livekit.cloud`), same credentials, `AGENT_NAME=indemn` matches
2. **voice-livekit logs** showed eval dispatches WERE being received — rooms `eval-*` active, knowledge base queries executing, params syncing to Redis
3. **Traced livekit-agents 1.3.10 source** in the voice-livekit container: `_output.py:284-300` uses `publish_transcription()`, NOT text streams
4. **Test script** on eval EC2 confirmed: `transcription_received` events fire (7 in 3 seconds), `register_text_stream_handler` receives 0

## The Fix (PR #22, deployed via PR #23)

```python
# BEFORE (broken — text stream API, never fires)
self.room.register_text_stream_handler("lk.transcription", on_transcription)

# AFTER (working — transcription API)
@self.room.on("transcription_received")
def on_transcription(segments, participant, publication):
    for segment in segments:
        if participant.identity != "eval-simulator" and segment.text:
            self._agent_transcription = segment.text
            self._new_agent_transcription.set()
```

## Investigation Facts Discovered

- **voice-livekit EC2**: `i-01e65d5494fd64b05` at `3.236.53.208`, container `voice-livekit`
- **eval EC2 (prod)**: `i-00ef8e2bfa651aaa8` at `98.88.11.14`, container `evaluations`
- Both use `AGENT_NAME=indemn` and `wss://test-ympl759t.livekit.cloud`
- voice-livekit has `livekit-agents==1.3.10`, `livekit==1.0.23`
- eval service has `livekit==1.1.2`, `livekit-api==1.1.0`
- voice-livekit has prod AND dev containers on same GPU EC2 (`voice-livekit` + `voice-livekit-dev`)
- OTEL export failing on voice-livekit (Langfuse creds invalid) — separate issue, non-blocking
- voice-livekit eval mode code (commit `2437caa`) IS deployed and working

## What's Still Needed

1. **Verify end-to-end**: Trigger a voice eval via Jarvis and confirm full transcript + scores
2. **PR #21 (event loop cleanup)**: Still open — may help with cleanup noise but was NOT the root cause
3. **Zombie runs in MongoDB**: Runs stuck in "running" status need manual cleanup
4. **Concurrency constraint**: Voice evals should use concurrency=1 (Jarvis skills need updating)
5. **Cancel endpoint**: No way to cancel stuck runs — needs implementation
