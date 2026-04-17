# Notes: 2026-04-14-impl-spec-phase-4-5.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-4-5.md
**Read:** 2026-04-16 (sampled opening + Application Structure; 702 lines total. SUPERSEDED by consolidated.)
**Category:** spec-superseded

## Key Claims

Base Phase 4+5 implementation spec. **SUPERSEDED** by 2026-04-14-impl-spec-phase-4-5-consolidated.md.

Key content:
- **Phase 4** = Base UI: React + Vite + TanStack Table + Tailwind + React Hook Form + Zod + React Router. Auto-generated entity list/detail/queue/role-overview views. WebSocket for real-time. Assistant at top-bar. Full authentication (SSO, MFA, platform admin, recovery flows).
- **Phase 5** = Real-Time: Attention lifecycle + Runtime deployment + events stream + scoped watches + handoff + harness pattern (voice example).
- **Application structure**: `ui/src/` with main/App/api/auth/layout/views/components.
- **Assistant**: `kernel/api/assistant.py` — kernel API endpoint streaming from Anthropic with skills loaded per user's roles. **NO TOOLS.** (Finding 0b source in spec.)
- **Harness pattern in Phase 5 §5.3**: complete voice harness example code at `harnesses/voice-deepagents/main.py`. "spec as example code, not deployable." NO chat harness, NO async harness in the spec.

## Architectural Decisions

- **React + Vite** for UI, hand-built pattern + auto-generation from entity metadata.
- **Full authentication end-to-end** per authentication-design.
- **Assistant as kernel endpoint** (Finding 0b entry point).
- **Voice harness as example code only** in Phase 5 §5.3.
- **Chat + async harnesses MISSING from spec.**

## Layer/Location Specified

- **`ui/src/`** — React app.
- **`kernel/api/assistant.py`** — kernel endpoint. (Finding 0b code site.)
- **`kernel/api/websocket.py`** — UI real-time.
- **`kernel/api/events.py`** — scoped events stream endpoint.
- **`kernel/api/interaction.py`** — handoff endpoint.
- **`kernel/api/auth_routes.py`** — full auth: login, SSO, MFA, platform admin.
- **`kernel/auth/*`** — middleware, session manager, JWT, etc.
- **`harnesses/voice-deepagents/`** — example code (Phase 5 §5.3) — NOT a deployable.
- **No `harnesses/chat-deepagents/` or `harnesses/async-deepagents/` in spec.**

**Finding 0 relevance**:
- **Assistant = kernel API endpoint + no tools.** "You can execute any CLI command" in system prompt, but LLM has no tool-use mechanism. This is Finding 0b directly in the spec.
- **Voice harness is example code only** — spec does not specify it as a deployable, doesn't include Dockerfile, deployment config, Railway service.
- **Chat and async harnesses missing entirely** from the spec, despite realtime-architecture-design specifying all 3.
- **This is where Finding 0b enters the spec.** Consolidated version inherits it.

## Dependencies Declared

- React 18+
- Vite, Tailwind, TanStack (Table, Query), React Hook Form, Zod, React Router
- WebSocket (native)
- `anthropic` (kernel/api/assistant.py imports it directly)
- LiveKit Agents (voice harness example)
- deepagents (voice harness example)
- Daytona (implicit; sandbox for voice harness)

## Code Locations Specified

See above. Key Finding 0 sites:
- `kernel/api/assistant.py` — no tools endpoint
- Phase 5 voice harness example at `harnesses/voice-deepagents/main.py` — not deployed
- Missing: chat + async harnesses

## Cross-References

- 2026-04-13-white-paper.md
- 2026-04-11-base-ui-operational-surface.md (source)
- 2026-04-10-realtime-architecture-design.md (source — SPECIFIES 3 harness images)
- 2026-04-11-authentication-design.md (source — full auth)
- 2026-04-14-impl-spec-phase-0-1.md (foundation)
- 2026-04-14-impl-spec-phase-2-3.md (predecessor — Phase 2-3 established the `process_with_associate` Finding 0 pattern)
- 2026-04-14-impl-spec-phase-4-5-consolidated.md (SUPERSEDES this)
- 2026-04-14-impl-spec-gaps.md (23 gaps identified)

## Open Questions or Ambiguities

Phase 4-5 ships with Finding 0b baked in + only voice harness example. The gap analysis identified 23 mechanism-level gaps but did NOT flag:
- Assistant missing tools
- Chat harness missing from spec
- Async harness missing from spec

These are layer-level issues that the gap methodology missed.

**Supersedence note**: SUPERSEDED by consolidated. Finding 0b is in both versions.
