---
ask: "Phase 1 completion handoff — what was built, what's in dev, what's needed for prod, and what comes next"
created: 2026-03-04
workstream: voice-evaluations
session: 2026-03-04-a
sources:
  - type: github
    description: "4 PRs created across indemn-ai repos with Dhruv + Dolly as reviewers"
  - type: linear
    description: "COP-359 parent issue with 7 sub-issues in Automated Testing and Evaluation project"
  - type: mongodb
    description: "Queried dev + prod for voice request status — prod healthy, dev stopped after Feb 27"
---

# Phase 1 Complete: Historical Transcript Evaluation — Handoff

## What Was Built

### 1. Voice Conversations in Observatory
Voice calls traced via Langfuse are synced into Observatory. Voice conversations appear with a voice badge, with LLM call + tool call trace data attached. The Langfuse sync task pulls traces, transforms observations to the standard run schema, and joins them to MongoDB requests via phone+time fallback matching (97% match rate on prod).

### 2. Transcript Evaluation (Web + Voice)
New evaluation mode that takes an actual conversation transcript and scores it against the success criteria defined in a test set. The agent is NOT invoked — this evaluates what already happened. Distinct from the existing replay mode (which re-invokes the current agent with historical messages). Triggered from the Observatory Evaluate dialog. Works for both web and voice conversations.

### 3. Copilot Dashboard Support
Transcript evaluation results display with a "Transcript" badge, distinct from simulation results. Type filter includes Transcript option.

### 4. Daily Pipeline Updated (dev only)
AWS Step Function runs Langfuse trace sync (voice) in parallel with LangSmith trace sync (web). Lambda step_handler.py has new `start_sync_langfuse_traces` action.

### 5. Voice Trace Metadata Enrichment
voice-livekit writes `call_sid`, `id_bot`, and `room_name` to every Langfuse OTLP span. Only applies to NEW calls after deployment.

## PRs (all in dev, ready for prod review)

| PR | Repo | Reviewers | Commits |
|----|------|-----------|---------|
| [#19](https://github.com/indemn-ai/Indemn-observatory/pull/19) | indemn-ai/Indemn-observatory | Dhruv, Dolly | 9 |
| [#7](https://github.com/indemn-ai/evaluations/pull/7) | indemn-ai/evaluations | Dhruv, Dolly | 4 |
| [#2](https://github.com/indemn-ai/copilot-dashboard-react/pull/2) | indemn-ai/copilot-dashboard-react | Dhruv, Dolly | 2 |
| [#79](https://github.com/indemn-ai/voice-livekit/pull/79) | indemn-ai/voice-livekit | Dhruv, Dolly | 2 |

## Linear Issues

**Parent: COP-359 — Voice Evaluation: Phase 1: Historical Transcript Evaluation**

| Issue | Title | Status |
|-------|-------|--------|
| COP-360 | Ingest voice conversations into Observatory via Langfuse sync | Acceptance |
| COP-361 | Evaluate historical voice conversations against test criteria | Acceptance |
| COP-362 | Transcript evaluation results in Copilot Dashboard | Acceptance |
| AI-322 | Enrich voice trace metadata for Langfuse-MongoDB joining | Acceptance |
| COP-363 | Add Langfuse sync to daily AWS pipeline | Acceptance |
| COP-364 | Deploy voice evaluation to prod | Backlog |
| COP-365 | Create voice agent evaluation criteria and verify end-to-end on prod | Backlog |

## What's Needed for Prod

1. **Merge 4 PRs** — review and merge into main on each repo
2. **Deploy services** — Observatory, evaluations, copilot-dashboard-react, voice-livekit
3. **Add Langfuse env vars** to prod Observatory environment: `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`
4. **Update AWS Lambda** with new `step_handler.py` (has `start_sync_langfuse_traces` action)
5. **Update AWS Step Function** with new `state_machine.json` (parallel Langfuse + LangSmith sync)
6. **Create voice agent test set** — evaluation criteria for one voice agent in Copilot Dashboard
7. **Verify end-to-end** — Langfuse sync → ingestion → Observatory voice badge → Evaluate → results in Dashboard

## Dev Investigation: Voice Request Gap

Dev MongoDB stopped receiving voice requests after Feb 27. Prod is healthy (19 voice requests in March). Root cause: conversation-service's RabbitMQ consumer thread likely died on dev — it has a hard restart limit of 5 attempts and the health check doesn't detect a dead consumer. This is a dev infrastructure issue, not a code bug. Does NOT affect prod deployment.

## What Comes Next: Phase 2

**Objective:** Enable simulation-based evaluation for voice agents — the same test scenario approach used for web agents today, where the harness invokes the agent directly with test scenarios. The added complexity vs web is speech-to-text transcription between the evaluation harness and the voice agent.

**How web simulation works today (for reference):**
- `SINGLE_TURN`: Send a message to bot-service `/llm-evaluate/invoke`, score the response
- `SCENARIO` (multi-turn): LLM-simulated user iterates with the bot via `/chat/invoke`, building a full conversation, then scoring against criteria

**What voice simulation needs:**
- An equivalent invocation path for voice agents (voice-livekit has no HTTP endpoint today)
- Handling the STT/TTS layer between the evaluation harness and the voice agent
- Design iteration needed before implementation

**Design document:** `projects/voice-evaluations/artifacts/2026-02-27-design-document.md` — Phase 5 covers voice simulation. Needs revisiting to align with current web evaluation architecture.

## Evaluation Modes Reference

| Mode | Agent Invoked? | What It Evaluates | How It Works |
|------|---------------|-------------------|--------------|
| **Single-turn** (web) | Yes | Current agent response | Send message → bot-service → score |
| **Scenario/simulation** (web) | Yes | Current agent in multi-turn | LLM simulated user loops with bot-service |
| **Replay** (web) | Yes | Current agent vs historical messages | Re-send historical user messages through current bot |
| **Transcript** (web + voice) | No | Actual historical conversation | Read transcript from MongoDB + Langfuse, score as-is |
