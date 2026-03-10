---
ask: "Draft email to Ricky (investor) explaining our LiveKit voice agent stack, tool call latency, and evaluation approach"
created: 2026-03-10
workstream: voice-evaluations
session: 2026-03-10-a
sources:
  - type: langfuse
    description: "OTLP traces from production voice calls — tool call, LLM, TTS latency metrics"
  - type: codebase
    ref: "/Users/home/Repositories/voice-livekit"
    name: "voice-livekit agent source"
  - type: codebase
    ref: "/Users/home/Repositories/voice-service"
    name: "voice-service telephony layer"
  - type: blog
    ref: "https://blog.indemn.ai/building-evaluations-for-conversational-agents"
    name: "How We Evaluate Conversational AI Agents"
---

# Email to Ricky — Voice Stack & Tool Call Latency

**Subject:** Voice stack / tool call latency follow-up

Hey Ricky,

Good talking the other day. Here's the breakdown on how we're handling voice + tool calls with LiveKit.

**Our stack:**
- LiveKit Agents SDK (Python) — the agent is a worker process, no HTTP server
- Deepgram nova-3 for STT
- GPT-4o-mini for the LLM (configurable per bot — we also support Gemini and Groq)
- Cartesia sonic-3 for TTS
- Everything streams end-to-end: STT streams partial transcripts, LLM streams tokens to TTS, TTS streams audio chunks back to LiveKit

**How we do tool calls:**
We're not using LiveKit's built-in function calling pattern. Our `Assistant` extends `livekit.agents.Agent` and we pass tool functions directly via the `tools=` parameter. The tools themselves are Python async functions that we generate dynamically at runtime from our database config — so when a bot is configured with a "collect caller info" tool or a "check business hours" tool, we build the callable function on the fly when the call connects. LiveKit's SDK handles converting those into OpenAI function definitions for the LLM.

So the flow is: LLM decides to call a tool → LiveKit SDK invokes our Python function → function does its thing (REST call, parameter capture, whatever) → result goes back to the LLM → LLM generates the response → TTS.

**What we actually see on latency:**
I pulled real numbers from our Langfuse traces (we export OTLP spans from the LiveKit SDK). Across production calls today:

- Custom tools (parameter capture, routing logic, classification): **4-18ms**
- REST API tools (Slack notifications, scheduling lookups): **74-308ms**
- End-of-utterance detection: **~50ms median**
- LLM inference (GPT-4o-mini): **~1.5s median, 3.2s at P90**
- TTS (Cartesia): **~3.3s median**

Tool execution itself is not the bottleneck at all. The latency the caller feels is almost entirely LLM thinking time + TTS generation. Caller stops talking → ~50ms to detect they're done → ~1.5s for the LLM to start producing tokens → TTS starts streaming audio as tokens arrive. So first word back to the caller is roughly 1.5-2s after they stop speaking.

The `end_call` tool looks slow in our traces (5-21s) but that's by design — it generates a goodbye message, waits for TTS to finish playing it, then tears down the room. The caller hears a natural goodbye, not a click.

**Evaluations:**
We also talked about how we evaluate our agents. I wrote up our approach in detail here — covers rubrics, LLM judges, test modes (including voice simulation), and how we went from 30% to 91% pass rates: https://blog.indemn.ai/building-evaluations-for-conversational-agents

Happy to jump on another call if you want to dig into any of this further.

Craig
