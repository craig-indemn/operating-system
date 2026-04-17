# Notes: 2026-04-10-session-5-checkpoint.md

**File:** projects/product-vision/artifacts/2026-04-10-session-5-checkpoint.md
**Read:** 2026-04-16 (full file — 512 lines)
**Category:** session-checkpoint

## Key Claims

Session 5 (2026-04-10) was a single very-long day. 10 phases of design work:

1. Re-read all 40+ prior artifacts
2. **Integration elevated to primitive #6** (owner field enables org/actor, adapter versioning, both outbound + inbound)
3. GIC retrace against updated kernel — kernel held up, 6 concerns surfaced
4. Base UI design + auth sketch + associate-role resolution (2 paths)
5. EventGuard retrace — biggest gap surfaced: **real-time actor mid-conversation event delivery**
6. Post-trace synthesis (10-item open list)
7. CRM retrace — `owner_actor_id` addition, domain-agnostic claim validated fully
8. **First design session — Real-time architecture (Attention + Runtime + scoped watches + handoff + harness pattern)** — 12 passes with Craig's corrections
9. CLI vs API clarification (both auto-generated surfaces; universal is entity framework, not CLI specifically)
10. This checkpoint

### Key architectural additions in session 5:

- **Integration as primitive #6** (first time formalized)
- **Attention** as bootstrap entity (unifies UI soft-locks + active working context + real-time routing)
- **Runtime** as bootstrap entity (deployable host for associate execution)
- **Harness pattern** (uses CLI, not SDK — "the whole point of deepagents is that it uses the CLI")
- **One harness serves many associates** (loads config at session start)
- **Three harness images**: voice-deepagents, chat-deepagents, async-deepagents (per realtime-architecture-design)
- **Scoped watches** (field_path / active_context resolution at emit time)
- **Watch coalescing** (by_correlation_id within time window)
- **owner_actor_id on associates** (delegated credential access)
- **Handoff mechanics** (interaction.handling_actor_id, observing purpose on Attention)
- **Voice clients for humans = Integrations** (reuse primitive #6)

### What's DECIDED (session 5 additions):

- 6 structural primitives (add Integration)
- 6 bootstrap entities (Org, Actor, Role, Integration, Attention, Runtime — Session added in session 6)
- Attention lifecycle (real_time_session, observing, review, editing, claim_in_progress)
- Runtime lifecycle (configured → deploying → active → draining → stopped)
- Harness is deployable infrastructure, NOT a kernel concept
- CLI and API are parallel auto-generated surfaces
- `indemn events stream` is the ONE new infrastructure CLI command
- Scoped watches + coalescing
- Default chat assistant in base UI (owner_actor_id bound to user, inherits roles + permissions)
- Three-layer customer-facing flexibility (Runtime defaults → Associate → Deployment)

## Architectural Decisions

Most consequential session 5 decisions:
- **Integration = primitive #6** (elevated from entity).
- **Attention + Runtime as bootstrap entities.**
- **Harness pattern formalized**: deployable images per kind+framework, using CLI via subprocess.
- **Three harness images**: voice-deepagents + chat-deepagents + async-deepagents.
- **CLI ≠ universal interface**; universal is entity framework's auto-generated surface (CLI + API both).

## Layer/Location Specified

This is THE session where the Finding 0 resolution is locked:
- **Harness = deployable image OUTSIDE kernel**, one per kind+framework combination.
- **"One harness serves many associates, loading associate config at session start"** — per-request config.
- **Harness authenticates via service token** (outside trust boundary).
- **Harness uses CLI via subprocess** for all OS interactions — not a Python SDK.
- **Async Temporal worker = IN the async-deepagents harness image** (not in the kernel).
- **Real-time workflows** run in their runtime (chat/voice harness), NOT in Temporal.
- **Kernel's Temporal Worker** handles only async associate claim → process → complete loops; but per realtime-architecture-design those loops run in the harness, not the kernel.

**Finding 0 relevance**: This is THE authoritative session where the harness pattern is locked. Every subsequent spec drift (Phase 2-3 consolidated spec §2.4, infrastructure-and-deployment missing async harness) deviates from what session 5 explicitly decided.

**Key quotes for the audit**:
- "The whole point of us using deep agents is because the deep agent uses the CLI"
- "I don't want to leave it up to an implementation detail on the voice thing" — no hand-waving on latency (meaning: don't put agents where latency is incidental)
- "The CLI commands are auto-created by the entities so I don't understand your question there"

## Dependencies Declared

- MongoDB Change Streams (replaces Redis proposal)
- Temporal Cloud (for async only)
- LiveKit (voice)
- WebSocket (chat)
- deepagents (framework, plug-and-play via harness)
- AWS Secrets Manager
- S3

## Code Locations Specified

- Harness images (deployable, not in kernel codebase at rest):
  - `indemn/runtime-voice-deepagents:1.2.0`
  - `indemn/runtime-chat-deepagents:1.2.0`
  - `indemn/runtime-async-deepagents:1.2.0` — **explicitly listed here; LATER DROPPED from infrastructure-and-deployment artifact**
- Kernel bootstrap entities: Organization, Actor, Role, Integration, Attention, Runtime
- New CLI: `indemn events stream`

## Cross-References

- Session 4 checkpoint (foundation — 5 primitives → 6 in session 5)
- 2026-04-10 artifacts (all session 5 outputs): integration-as-primitive, gic-retrace-full-kernel, base-ui-and-auth-design, eventguard-retrace, post-trace-synthesis, crm-retrace, realtime-architecture-design
- Session 6 checkpoint (gap sessions add bulk ops, base UI operational surface, authentication design, simplification pass, documentation sweep)
- Phase 2-3 consolidated spec — DEVIATES from this session's harness decision at §2.4

## Open Questions or Ambiguities

Listed as "STILL OPEN":
- Design sessions remaining: bulk operations, pipeline dashboard + queue health, authentication (all done in session 6)
- Documentation sweep (items 4, 5, 6, 11, 12 — done in session 6)
- Simplification pass (done in session 6)
- Spec writing (white paper + consolidated specs in session 6 / April 13-14)
- Stakeholder engagement (ongoing)

**Supersedence note**:
- Session 5 decisions SURVIVE as authoritative.
- **The three-harness-image architecture is Finding 0's reference design.** This session explicitly specifies it.
- Subsequent drift (infrastructure artifact missing async-deepagents, Phase 2-3 spec placing `process_with_associate` in kernel) is where the implementation diverged from this session's design.
