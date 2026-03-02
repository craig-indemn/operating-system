# Voice Evaluations

Incorporating voice agents into the Indemn evaluation framework. Currently, only web agents are evaluated via the evaluation harness and displayed in the copilot dashboard. Voice agents use a completely different backend (voice-livekit calling OpenAI directly, NOT bot-service) and their data lives in MongoDB + LiveKit + S3 rather than LangSmith. The goal is to bridge this gap — enabling evaluation of voice agents through the existing harness, surfacing voice analytics in the Observatory, and building the OS-level skills (LiveKit, updated MongoDB) needed to interact with voice data.

## Status
**Session 2026-02-27-a** (COMPLETE): Project created. Comprehensive research across 6 repos, MongoDB prod data, Slack/email, LiveKit exports. Design document written with 5-phase roadmap.

**Session 2026-02-27-b** (COMPLETE): Design review and iteration. Ran 5-agent parallel code review that verified every claim in the design. Found and fixed 17 issues. Design document fully grounded — zero assumptions.

**Session 2026-02-27-c** (COMPLETE): Implementation plan created and executed across all 5 waves (14 tasks). All code written and committed across 5 repos: voice-livekit (trace metadata), evaluations (transcript engine + API), indemn-observability (channel fix + Langfuse connector + evaluate UI + voice metrics), indemn-platform-v2 (transcript type in UI), operating-system (Langfuse skill + MongoDB patterns).

**Session 2026-02-27-d** (COMPLETE): Testing, code review, and bug-fixing. Full line-by-line code review across all 5 repos found 3 bugs in agent-written observatory code + several documentation inaccuracies — all fixed. Static verification all pass (Python compile, TypeScript, 79 unit tests). Browser testing: Evaluate button/dialog PASS, voice channel badge and transcript badge CANNOT VERIFY (need data ingestion + running a transcript eval).

**Session 2026-02-27-e** (COMPLETE): Committed all bug fixes across 3 repos. Ran transcript evaluation on web conversations — PASS (2 items, 76/102 criteria, 12/12 rubric). Federation build browser testing in copilot-dashboard — Transcript Criteria stat card PASS, evaluation scores display correctly. **Blocked on Langfuse credentials** for voice data ingestion into Observatory and remaining verification.

**Session 2026-03-02-a** (COMPLETE): Resumed project, audited git state across all repos. All implementation commits are local only (not pushed). Commit locations verified:
- **evaluations** (`main`): `c651b79` feat + `1eddab9` fix — 2 unpushed commits
- **voice-livekit** (`main`): `9df3389` trace metadata — 1 unpushed commit
- **indemn-platform-v2** (`main`): `ffcd1e9` transcript UI — 1 unpushed commit (+ 3 other COP-325 commits)
- **indemn-observability** (`demo-gic`): `e3fa4a4` feat + `1a54bab` fix — on feature branch, not on main

**Next step**: Move commits to feature branches in evaluations, voice-livekit, and platform-v2 before pushing. Still blocked on Langfuse credentials for voice data verification.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| evaluations | GitHub repo + local | indemn-ai/evaluations, `/Users/home/Repositories/evaluations` |
| copilot-dashboard | GitHub repo + local | indemn-ai/copilot-dashboard, `/Users/home/Repositories/copilot-dashboard` |
| indemn-platform-v2 | GitHub repo + local | craig-indemn/indemn-platform-v2, `/Users/home/Repositories/indemn-platform-v2` |
| voice-service | GitHub repo + local | indemn-ai/voice-service, `/Users/home/Repositories/voice-service` |
| voice-livekit | GitHub repo + local | indemn-ai/voice-livekit, `/Users/home/Repositories/voice-livekit` |
| indemn-observability | GitHub repo + local | indemn-ai/indemn-observability, `/Users/home/Repositories/indemn-observability` |
| percy-service | GitHub repo + local | indemn-ai/percy-service, `/Users/home/Repositories/percy-service` |
| copilot-dashboard-react | GitHub repo + local | indemn-ai/copilot-dashboard-react (currently empty placeholder) |
| Platform Development project | OS project | `projects/platform-development/INDEX.md` |
| LiveKit Cloud | SIP host | `tk2bj7pt8eg.us.sip.livekit.cloud` |
| S3 recordings | AWS | `indemn-call-transcripts` bucket |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-27 | [initial-context](artifacts/2026-02-27-initial-context.md) | Comprehensive research synthesis across all repos — current state of evaluations, voice stack, observatory, data gaps, and integration challenges |
| 2026-02-27 | [voice-tracing-discovery](artifacts/2026-02-27-voice-tracing-discovery.md) | Langfuse + LiveKit Cloud tracing discovery — how voice traces work, data formats, access patterns, Slack/email evidence |
| 2026-02-27 | [design-document](artifacts/2026-02-27-design-document.md) | Comprehensive design: 5-phase roadmap, architecture, data flows, implementation details for voice evaluations + observatory |

## Decisions
- 2026-02-27: Voice trace data access pattern: OTLP → Langfuse → Langfuse API. Mirrors the web pattern (LangChain callbacks → LangSmith → LangSmith API). Langfuse is the canonical data source for voice traces, not LiveKit Cloud or direct data hooks.
- 2026-02-27: Tracing platform consolidation is out of scope. Work with what exists (Langfuse for voice, LangSmith for web).
- 2026-02-27: Two evaluation modes for voice: (1) Voice Replay Evaluation — judge real conversations from Observatory/Langfuse, build first. (2) Voice Simulation — text-mode endpoint on voice-livekit for proactive testing, build second. Replay is the MVP; simulation goes on the roadmap.
- 2026-02-27: Observatory → Evaluation bridge is a new flow: select conversations in Observatory, trigger evaluation, results appear in Copilot Dashboard. Benefits both web and voice.

## Open Questions
- ~~Where do turn-by-turn voice transcripts live?~~ ANSWERED: LiveKit chat_history.json has full turn-by-turn with metrics. Also exported to Langfuse via OTLP. MongoDB `bot_external_event_logs` has summaries only.
- ~~What tracing system is used for voice?~~ ANSWERED: **Langfuse** (HIPAA instance at `hipaa.cloud.langfuse.com`, project `cmht0a7ll001qad07jn0ko84c`). OpenTelemetry spans from LiveKit Agents SDK exported via OTLP.
- Should we consolidate on one tracing platform (Langfuse or LangSmith) or build connectors for both? Dhruv was researching this as of Feb 5 meeting.
- How should voice agents be invoked for evaluation? Transcript-based replay through existing harness seems most feasible — feed chat_history transcripts + tool logs through LLM judges.
- What Langfuse API credentials do we have? Need `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` for the HIPAA project to build the skill.
- LiveKit Cloud API doesn't expose programmatic download for observability data (Jonathan confirmed Feb 24). Is Langfuse the sole programmatic data source, or is there another path?
- Are voice-specific evaluation criteria needed beyond text content? (e.g., response latency thresholds, interruption handling, call transfer success)
- How do we join Langfuse traces with MongoDB conversation data? What's the common key? (room_id? external_conversation_id?)
- For the Observatory Langfuse connector: should it mirror the LangSmith connector pattern, or is a different approach needed given OTLP vs LangChain callback differences?
