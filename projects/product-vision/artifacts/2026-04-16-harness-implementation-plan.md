---
ask: "Document the harness hosting decision (Option 1 — three separate images) and specify what correct implementation means for each harness, with explicit input gates where Craig's approval is required before proceeding."
created: 2026-04-16
workstream: product-vision
session: 2026-04-16-b
sources:
  - type: artifact
    ref: "2026-04-10-realtime-architecture-design.md"
    description: "The design source for the harness pattern — three deployable images per kind+framework"
  - type: artifact
    ref: "2026-04-16-vision-map.md"
    description: "Authoritative vision synthesis — § 4 trust boundary, § 12 harness pattern"
  - type: artifact
    ref: "2026-04-16-alignment-audit.md"
    description: "Finding 0 + 0b — what the harness pattern is supposed to fix"
  - type: artifact
    ref: "2026-04-13-infrastructure-and-deployment.md"
    description: "Infrastructure artifact that partially dropped async-deepagents from the service table (drift source)"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5-consolidated.md"
    description: "Phase 5 §5.3 voice harness example code — the one concrete reference"
---

# Harness Implementation Plan — Option 1 Confirmed

**Decision:** Three separate Docker images, three Railway services, one per kind+framework combination. Matches the design assumption in `2026-04-10-realtime-architecture-design.md` Part 4.

**Rationale:** Design fidelity. The realtime-architecture-design artifact is the authoritative session 5 decision that specified this exact pattern. The drift toward fewer harnesses (infrastructure artifact's 5-service table missing async-deepagents) was a drafting omission, not a deliberate reversal. Restoring the design-specified pattern is the correct path.

---

## 1. The Option Space (captured for posterity)

### Options considered

| Option | Shape | Pro | Con |
|---|---|---|---|
| **Option 1 (CHOSEN)** | 3 images, 3 Railway services | Clean separation, independent scale, minimal blast radius, matches design | 3x Dockerfile maintenance, some code duplication |
| Option 2 | 1 image with 3 entry points (mirrors kernel) | Single Dockerfile, still 3 services | Shared dependencies affect all three; bigger image |
| Option 3 | 1 image, 1 service, all transports in-process | Simplest ops | Can't scale independently, single failure impacts all |
| Option 4 | Reasoning service + transport proxies | Pure concerns separation | Per-turn RPC latency kills voice; fights deepagents |

Options 1 and 2 both satisfy the vision. Option 1 picked for design fidelity.

### What this decision is NOT

- **Not "harness or adapter"** — adapters (kernel-side, stateless, single-request) solve a different problem than harnesses (outside kernel, stateful agent loop). Both exist. Both kernel and harness call adapters when they need external connectivity.
- **Not "hosted or not"** — agent execution must be hosted because all three transports require a running process (LiveKit worker, WebSocket server, Temporal worker polling its queue).
- **Not "deepagents or something else"** — Runtime entity's `framework` field supports plug-and-play, but deepagents is the MVP framework.

---

## 2. What a Harness Is, Concretely

A harness is a deployable Docker image that contains:

1. **The agent framework** (deepagents)
2. **The transport** (LiveKit Agents SDK / WebSocket server / Temporal worker)
3. **The `indemn` CLI binary** (pre-installed)
4. **Harness glue script** (~60 lines) tying transport + framework + CLI together

**What the harness does during a session:**

1. **Startup** — authenticates as a Runtime instance using a service token, registers heartbeat to kernel (`indemn runtime register-instance`), establishes transport listener.
2. **Session start** — loads associate config via `indemn associate get {id}` (skills, model, prompt, mode).
3. **Agent instantiation** — `create_deep_agent(skills=..., model=...)` with middleware configured per associate.
4. **Sandbox** — agent runs inside Daytona (or equivalent) for isolation.
5. **Event loop** — handles transport input, runs LLM iterations, executes tools via `subprocess.run(["indemn", ...])`, streams output.
6. **Events subscription** — long-running `indemn events stream --actor-id X` feeds scoped Change Stream events into the agent.
7. **Heartbeat** — periodic `indemn attention heartbeat` maintains Attention TTL.
8. **Session end** — `indemn attention close`, `indemn interaction transition` on disconnect or completion.

**What the harness NEVER does:**

- Direct MongoDB access
- Import kernel code
- Handle Temporal workflow logic beyond subscribing to its task queue (async harness only)
- Persist any kernel-authoritative state locally

---

## 3. Per-Harness Specifications

Each harness has its own specification. Correct implementation means satisfying the vision's architectural requirements PLUS the per-harness technical requirements.

### 3.1 `indemn/runtime-async-deepagents` (build first — unblocks Phase 6/7)

**Purpose:** Host scheduled + event-triggered associate work (email classifier, health monitor, overdue checker, personal syncs, etc.).

**Transport:** Temporal worker subscribing to a per-Runtime task queue (`runtime-{runtime_id}`).

**Image contents:**
- Python 3.12-slim base
- `uv` for dependency management
- deepagents + dependencies
- `indemn` CLI pre-installed
- Temporal Python SDK
- Harness glue script (async worker registration, event loop, graceful shutdown)

**What moves out of kernel:**
- `process_with_associate` activity (the agent execution loop)
- `_execute_deterministic` / `_execute_reasoning` / `_execute_hybrid` helpers
- `_execute_command_via_api` helper (replaced by CLI subprocess calls)
- `_load_skills` (replaced by `indemn skill get` calls)
- `import anthropic` from kernel

**What stays in kernel:**
- `claim_message` activity
- `load_entity_context` activity
- `complete_message` / `fail_message` activities
- `process_human_decision` activity (HITL — different concern)
- `process_bulk_batch` / `preview_bulk_operation` (bulk operations are kernel-legitimate)
- `ProcessMessageWorkflow` (generic orchestration) — but dispatches to per-Runtime queue instead of `indemn-kernel`
- `HumanReviewWorkflow`, `BulkExecuteWorkflow`

**Dispatch rewiring:**
- Queue Processor writes to `runtime-{runtime_id}` queue based on Associate.runtime_id
- Optimistic dispatch in API server writes to the same per-Runtime queue
- Kernel Temporal Worker no longer registers `process_with_associate`

**Verification criteria (how we know it's correct):**
1. `grep -r "import anthropic" kernel/` returns nothing
2. `kernel/temporal/activities.py` no longer contains the three `_execute_*` functions
3. Async harness image builds successfully with no kernel imports
4. Scheduled associate (e.g., stale-check) runs end-to-end via the async harness
5. Multiple Runtime instances can register, heartbeat, and claim work from distinct queues
6. Daytona sandbox wraps agent execution (verifiable via `indemn trace` showing sandbox span)

---

### 3.2 `indemn/runtime-chat-deepagents` (build second — resolves Finding 0b)

**Purpose:** Host the default assistant (every user gets one) + any chat-kind associates (customer-facing chat widgets).

**Transport:** WebSocket server accepting browser connections.

**Image contents:**
- Python 3.12-slim base
- deepagents + dependencies
- WebSocket server library (`websockets` or `fastapi-websocket`)
- `indemn` CLI pre-installed
- Harness glue script (connection handler, session lifecycle, JWT passthrough)

**What this replaces:**
- `kernel/api/assistant.py` — delete entirely after chat harness is serving
- UI's `fetch('/api/assistant/message')` — change to WebSocket connection to chat harness

**Auth pattern:**
- User's Session JWT is injected at session start (per authentication-design.md lines 463-482)
- Harness passes JWT through to all CLI subprocess calls via `INDEMN_AUTH_TOKEN` env var
- CLI → API middleware sees user's JWT, enforces user's permissions
- Audit attributed as "user X via default associate performed Y"

**Verification criteria:**
1. `kernel/api/assistant.py` deleted
2. `grep -r "tools\s*=" kernel/api/` returns nothing (no tools in any kernel endpoint)
3. UI assistant component connects to chat harness's WebSocket endpoint
4. User asks "create an ActionItem for me" in assistant → entity actually gets created → visible in UI
5. User's permissions enforced (user without ActionItem:write can't create via assistant)
6. deepagents middleware is fully active (todo list, subagents, filesystem, summarization, HITL)

---

### 3.3 `indemn/runtime-voice-deepagents` (build third — Phase 5 completion)

**Purpose:** Host voice associates (customer service phone agents, EventGuard voice widgets, etc.).

**Transport:** LiveKit Agents SDK worker.

**Image contents:**
- Python 3.12-slim base
- deepagents + dependencies
- LiveKit Agents SDK
- STT + TTS provider SDKs (decision — see § 5.2)
- `indemn` CLI pre-installed
- Harness glue script (matching Phase 5 §5.3 spec example)

**Starting reference:** Phase 5 §5.3 shows ~60 lines of glue code — that's the template.

**Verification criteria:**
1. Voice harness registers with LiveKit, workers respond to dispatched calls
2. Audio pipeline works end-to-end (STT → agent → TTS)
3. Pipelined streaming — first TTS audio begins before full LLM response completes
4. Mid-call events delivered via `indemn events stream` → signal handler (not polling)
5. Handoff to human works (`indemn interaction transfer --to-role X` → Runtime switches modes)
6. Call recordings (if enabled) stored per content_visibility policy

---

## 4. Input Gates — Where Craig's Approval Is Required

Before proceeding past each gate, explicit confirmation needed. **No work past a gate until approved.**

### Gate 0: Pre-work decisions (before any harness work)

**G0.1 — Deployable target.** Railway per-harness service? ECS? K8s? (Runtime.deployment_platform supports all of these.)

**G0.2 — Shared base image.** Single `indemn/harness-base` image containing Python + CLI + common deps, inherited by each harness? Or three independent Dockerfiles?
- Recommendation: shared base image. Reduces per-harness duplication without sacrificing independence.

**G0.3 — Repository structure.** Confirm: `harnesses/voice-deepagents/`, `harnesses/chat-deepagents/`, `harnesses/async-deepagents/` at repo root (as specified in `remaining-gap-sessions.md`).

**G0.4 — Image tagging convention.** `indemn/runtime-{kind}-{framework}:{version}` per design. Version scheme (semver? git SHA? date)?

**G0.5 — Deployment pipeline.** CI builds all 4 images (kernel + 3 harnesses) on push to main? Separate pipelines per harness? Manual promotion?

### Gate 1: Async harness — pre-build review

**G1.1 — Task queue naming.** Design says `runtime-{runtime_id}`. Confirm.

**G1.2 — Service token issuance.** Kernel needs to issue a service token per Runtime instance. How does the harness get it at startup? Env var? Kernel endpoint at registration? (authentication-design has precedent.)

**G1.3 — Daytona integration.** Is Daytona the sandbox provider? Alternative options? What's the API integration pattern — per-session sandbox or pooled?

**G1.4 — deepagents middleware composition.** Which middleware modules are active for async associates? Todo list? Subagents? Filesystem? Summarization at 85% context? Human-in-the-loop?

**G1.5 — Migration sequence.** Proposed: (a) build harness in parallel with kernel having both paths; (b) deploy harness; (c) route one scheduled associate through harness; (d) verify end-to-end; (e) migrate remaining associates; (f) delete kernel code. Acceptable?

### Gate 2: Async harness — implementation review

**G2.1 — Review glue code before merge.** ~60-100 lines. Craig reads + approves.

**G2.2 — Review dispatch rewiring.** Queue Processor + optimistic dispatch changes. Craig reads + approves.

**G2.3 — Approve deletion of kernel code.** `process_with_associate` + `_execute_*` + `_execute_command_via_api` deletion is irreversible. Explicit sign-off required.

### Gate 3: Chat harness — pre-build review

**G3.1 — JWT passthrough mechanism.** Proposed: user's Session JWT injected as env var at harness session start. Harness passes to CLI via `INDEMN_AUTH_TOKEN`. Acceptable security-wise?

**G3.2 — WebSocket protocol.** Message format (JSON schema), session lifecycle, reconnection semantics. Draft protocol for review.

**G3.3 — UI routing change.** UI's `sendMessage` hook currently posts to `/api/assistant/message`. Change to WebSocket connection to chat harness. Affects `ui/src/assistant/AssistantProvider.tsx` + `useAssistant.ts`. Review before change.

**G3.4 — Default assistant provisioning.** Every user gets a default associate (`owner_actor_id = user.id`). When is it created — at user creation? First chat session? Lazy?

### Gate 4: Chat harness — implementation review

**G4.1 — Review glue code before merge.**

**G4.2 — Approve deletion of `kernel/api/assistant.py`.** Irreversible. Explicit sign-off.

**G4.3 — Approve UI routing change.** Routing users to chat harness is a visible change — monitor rollout.

### Gate 5: Voice harness — pre-build review

**G5.1 — LiveKit deployment.** LiveKit Cloud or self-hosted? Affects cost, latency, availability.

**G5.2 — STT + TTS providers.** Deepgram? AssemblyAI? ElevenLabs? OpenAI? Affects cost, quality, latency.

**G5.3 — Audio pipeline specifics.** Streaming / endpoint detection / barge-in handling. Technical decisions that affect perceived latency.

**G5.4 — Reference deployment.** EventGuard voice work (existing voice-livekit) — does this harness replace it or run alongside? Migration path?

### Gate 6: Voice harness — implementation review

**G6.1 — Review glue code.**

**G6.2 — Latency testing.** Target: first-response <1.2s conversational. Voice needs objective measurement before acceptance.

### Gate 7: Post-implementation verification

**G7.1 — Re-run shakeout** after Tracks A complete. Expected outcomes per § 3 verification criteria.

**G7.2 — Pass 4 re-audit** — verify Finding 0 closed at all three levels (spec + code + infra).

**G7.3 — Phase 6 unblock confirmation** — CRM Assistant runs end-to-end, personal syncs work, Meeting Processor runs in async harness.

---

## 5. Cross-Cutting Concerns

### 5.1 Shared harness base image (G0.2)

Recommended: `indemn/harness-base:X.Y.Z` contains Python + `uv` + `indemn` CLI + common deps. Each harness image FROM-inherits:

```dockerfile
# indemn/runtime-async-deepagents/Dockerfile
FROM indemn/harness-base:1.0.0
RUN uv add temporalio deepagents
COPY main.py /app/main.py
CMD ["uv", "run", "python", "-m", "harness.async"]
```

Benefits: CLI updates propagate; framework upgrades isolated per harness; smaller per-harness build.

### 5.2 Task queue topology

Per realtime-architecture-design: `runtime-{runtime_id}` queue per Runtime instance.

Implication: Runtime creation produces a new queue (Temporal auto-creates on first dispatch). Harness subscribes using its Runtime ID at startup.

### 5.3 Service token pattern

Runtime instances authenticate with a service token (Session entity with `type=associate_service`, owner=Runtime). Issued at Runtime creation, injected as env var at harness deployment.

### 5.4 Local development story

For local dev:
- Option A: docker-compose brings up kernel + all 3 harnesses (heavy)
- Option B: docker-compose brings up kernel only; harnesses run via `python -m harness.async` in separate terminals (lightweight)
- Option C: Hybrid — async harness in docker-compose (always needed), voice/chat started on demand

Recommendation: Option B for Craig's daily dev; Option C for FDE/integration testing.

### 5.5 Secrets per harness

Each harness needs:
- MongoDB URI: NO (no direct DB access)
- AWS Secrets Manager creds: NO (service token has access scoped to what harness needs)
- Service token: YES (injected at startup)
- LLM provider API keys: resolved via `indemn associate get` → Integration lookup → Secrets Manager
- Transport-specific secrets (LiveKit API key, webhook secrets): resolved via Runtime config + Integration

### 5.6 Observability per harness

Each harness emits OTEL spans (same TracingInterceptor pattern as kernel Temporal worker). Spans join the entity trace via `correlation_id` propagation. Harness-level metrics: active sessions, token throughput, LLM latency distribution, tool-use iteration counts.

---

## 6. Build Sequence

Serial per priority, each with its own gate sequence:

```
Gate 0 → [async build] → Gate 1 → [async impl] → Gate 2 → [async merge+delete]
      → Gate 3 → [chat build] → Gate 4 → [chat merge+delete]
      → Gate 5 → [voice build] → Gate 6 → [voice merge]
      → Gate 7 → [verification]
```

Parallel work possible (Tracks B, C, D from alignment-audit § 7) during harness build.

---

## 7. What This Document Commits Us To

- **Option 1 (3 images) is the chosen approach.** Documented. Decision recorded in INDEX.md.
- **No harness work starts until Gate 0 decisions are made** by Craig.
- **Each harness has an explicit pre-build review gate + implementation review gate** with Craig's sign-off.
- **Kernel code deletion is irreversible — explicit approval required** at G2.3 and G4.2.
- **Verification criteria are objective and testable** — each harness's success is measurable before Gate 7.

This plan ensures: correctly-implemented harnesses (satisfy vision's architectural requirements), per-harness technical correctness (satisfy transport + framework requirements), and Craig's oversight at every decision point.

---

## 8. What's Not In This Plan

- **Detailed glue code for each harness** — that comes after Gate 1/3/5 approval per harness.
- **Exact provider choices (Daytona? Deepgram? LiveKit Cloud?)** — those are Gate 0/1/5 decisions requiring Craig's input.
- **Migration timeline for current customers** — per transition design, OS runs alongside current system; GIC is first migration candidate post-harness-build.
- **Cost projections** — each harness adds a Railway service. Infrastructure artifact's cost model needs updating after Gate 0.

---

## 9. Cross-References

- `2026-04-10-realtime-architecture-design.md` — the canonical harness pattern design (Part 4)
- `2026-04-16-vision-map.md` § 4 (trust boundary) + § 12 (harness pattern)
- `2026-04-16-alignment-audit.md` § 2 (Finding 0) + § 7 (fix priority order)
- `2026-04-14-impl-spec-phase-4-5-consolidated.md` § 5.3 (voice harness example code)
- `2026-04-13-infrastructure-and-deployment.md` (infrastructure — needs update to add async-deepagents)
- `2026-04-11-authentication-design.md` lines 463-482 (default assistant inherits user JWT)
- `2026-04-13-documentation-sweep.md` item 11 (`owner_actor_id` on associates)
